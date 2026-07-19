from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
MODULO_PATH = ROOT / "ferramentas" / "manutencao" / "atualizar_base_juridica.py"
SPEC = importlib.util.spec_from_file_location("atualizar_base_juridica", MODULO_PATH)
assert SPEC and SPEC.loader
pipeline = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pipeline
SPEC.loader.exec_module(pipeline)


class PipelineBaseJuridicaTest(unittest.TestCase):
    def preparar_promocao(
        self,
        raiz: Path,
        artigos_publicados: dict[str, dict[str, object]],
        artigos_candidatos: dict[str, dict[str, object]],
        meta_candidato: dict[str, object] | None = None,
    ) -> tuple[dict[str, object], Path, Path]:
        publicados = raiz / "publicados"
        execucao = raiz / "execucao"
        candidatos = execucao / "candidatos"
        publicados.mkdir()
        candidatos.mkdir(parents=True)
        dados: dict[str, object] = {
            "conjuntos": {
                "legislacao_teste": {
                    "familia": "legislacao",
                    "chave_colecao": "artigos",
                    "destino": "lei_teste.json",
                }
            }
        }
        publicado = {
            "_meta": {"total_artigos": len(artigos_publicados)},
            "artigos": artigos_publicados,
        }
        candidato = {
            "_meta": meta_candidato or {"total_artigos": len(artigos_candidatos)},
            "artigos": artigos_candidatos,
        }
        (publicados / "lei_teste.json").write_text(
            json.dumps(publicado), encoding="utf-8"
        )
        (candidatos / "lei_teste.json").write_text(
            json.dumps(candidato), encoding="utf-8"
        )
        return dados, execucao, publicados

    def test_manifesto_cobre_destinos_publicados(self) -> None:
        dados = pipeline.manifesto()
        publicados = ROOT / dados["diretorio_publicado"]
        ativos = {
            chave: config
            for chave, config in dados["conjuntos"].items()
            if config.get("adaptador")
        }
        nucleo = {
            "legislacao",
            "sumulas_stj",
            "sumulas_stf",
            "sumulas_vinculantes",
            "jurisprudencia_teses_stj",
            "temas_repetitivos_stj",
        }
        self.assertLessEqual(nucleo, set(ativos))
        extras = set(ativos) - nucleo
        # Além do núcleo, só são esperados conjuntos da expansão legislativa.
        self.assertEqual(
            extras, {chave for chave in extras if chave.startswith("legislacao_")}
        )
        for config in ativos.values():
            self.assertIn(config["adaptador"], pipeline.ADAPTADORES)
            for nome in pipeline.arquivos_do_conjunto(config):
                self.assertTrue((publicados / nome).exists(), nome)
            for fonte in config["fontes"]:
                self.assertTrue(fonte["url"].startswith("https://"))

    def test_manifesto_rejeita_limite_de_promocao_invalido(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fontes.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "politica_promocao": {
                            "limite_mudanca_percentual": 0,
                            "limite_mudanca_minimo": 20,
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "limites inválidos"):
                pipeline.manifesto(path)

    def test_temas_publicados_nao_expoem_caminho_pessoal(self) -> None:
        path = (
            ROOT
            / "ferramentas"
            / "pesquisa"
            / "vade-mecum"
            / "data"
            / "flash_temas_stj.json"
        )
        objeto = json.loads(path.read_text(encoding="utf-8"))
        source = objeto["_meta"]["source"]
        referencia = source["officialPublicReference"]
        serializado = json.dumps(source, ensure_ascii=False)
        self.assertNotIn("/Users/", serializado)
        self.assertNotIn("Downloads", serializado)
        self.assertEqual(source["provenanceStatus"], "reproducible_pipeline")
        self.assertEqual(
            referencia["packageId"], "4238da2f-c07b-4c1a-b345-4402accacdcf"
        )
        self.assertEqual(referencia["joinKey"], "sequencialPrecedente")
        self.assertEqual(
            referencia["resources"]["temas"]["id"],
            "df29da13-7d6b-41ba-ad96-cd1a5bbd191c",
        )
        self.assertEqual(
            referencia["resources"]["processos"]["id"],
            "7ed21202-0049-4fcb-aa7c-48d810d3c499",
        )

    def test_catalogo_stf_preserva_numero_identificador_e_status(self) -> None:
        html = """
        <div class="sumula-item"><a href="sumariosumulas.asp?base=30&amp;sumula=1451">
        Súmula 1</a></div>
        <div class="sumula-item"><a href="sumariosumulas.asp?base=30&amp;sumula=1306">
        Súmula 3 <em>(superada)</em></a></div>
        <div class="sumula-item"><a href="sumariosumulas.asp?base=30&amp;sumula=1308">
        Súmula 4 <em>(cance&#8203;lada)</em></a></div>
        """
        itens = pipeline.extrair_catalogo_stf(html, False)
        self.assertEqual([item["numero"] for item in itens], [1, 3, 4])
        self.assertEqual(itens[0]["identificador"], "1451")
        self.assertEqual(itens[1]["status"], "superada")
        self.assertEqual(itens[2]["status"], "cancelada")

    def test_transforma_sumula_stj_sem_span_de_enunciado(self) -> None:
        html = """
        <div class="gridSumula">
          <span class="numeroSumula">152</span><span class="clsINDE">CANCELADA</span>
          <div class="blocoVerbete"><span class="ramoSumula">DIREITO TRIBUTÁRIO - ICMS</span>
          Na venda pelo segurador, de bens salvados de sinistros, incide o ICMS.
          (SÚMULA 152, PRIMEIRA SEÇÃO, DJ 14/03/1996, p. 7115)
          <span class="clsCOM">Cancelada em sessão posterior.</span></div>
        </div>
        """
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto"
            candidatos = raiz / "candidatos"
            bruto.mkdir()
            (bruto / "catalogo.html").write_text(html, encoding="utf-8")
            config = {"destino": "sumulas_stj.json"}
            [saida] = pipeline.transformar_sumulas_stj(
                config, bruto, raiz / "publicados", candidatos
            )
            registro = json.loads(saida.read_text())["sumulas"]["152"]
        self.assertEqual(registro["status"], "cancelada")
        self.assertEqual(
            registro["enunciado"],
            "Na venda pelo segurador, de bens salvados de sinistros, incide o ICMS.",
        )
        self.assertEqual(registro["orgao"], "PRIMEIRA SEÇÃO")
        self.assertEqual(registro["data"], "14/03/1996")

    def test_transforma_estados_nao_ativos_de_sumula_stj(self) -> None:
        html = """
        <div class="gridSumula"><span class="numeroSumula">1</span>
          <span class="clsINDE">SUPERADA</span><div class="blocoVerbete">
          <span class="clsVerbete">Texto 1.</span></div></div>
        <div class="gridSumula"><span class="numeroSumula">2</span>
          <span class="clsINDE">SUSPENSA</span><div class="blocoVerbete">
          <span class="clsVerbete">Texto 2.</span></div></div>
        <div class="gridSumula"><span class="numeroSumula">3</span>
          <div class="blocoVerbete"><del><span class="clsVerbete">
          Texto 3.</span></del></div></div>
        """
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto"
            bruto.mkdir()
            (bruto / "catalogo.html").write_text(html, encoding="utf-8")
            [saida] = pipeline.transformar_sumulas_stj(
                {"destino": "sumulas_stj.json"},
                bruto,
                raiz / "publicados",
                raiz / "candidatos",
            )
            sumulas = json.loads(saida.read_text())["sumulas"]
        self.assertEqual(sumulas["1"]["status"], "superada")
        self.assertEqual(sumulas["2"]["status"], "suspensa")
        self.assertEqual(sumulas["3"]["status"], "inativa")

    def test_download_rejeita_url_e_redirecionamento_externos(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            destino = Path(temp) / "fonte.html"
            with patch.object(pipeline.subprocess, "run") as executar:
                with self.assertRaisesRegex(ValueError, "domínios oficiais"):
                    pipeline.baixar("https://example.com/fonte", destino)
                executar.assert_not_called()

            def simular_redirect(comando: list[str], **_: object) -> object:
                temporario = Path(comando[comando.index("--output") + 1])
                cabecalhos = Path(comando[comando.index("--dump-header") + 1])
                temporario.write_text("<html></html>", encoding="utf-8")
                cabecalhos.write_text(
                    "HTTP/2 200\ncontent-type: text/html\n\n", encoding="latin-1"
                )
                return pipeline.subprocess.CompletedProcess(
                    comando, 0, stdout="https://example.com/redirecionado", stderr=""
                )

            with patch.object(
                pipeline.subprocess, "run", side_effect=simular_redirect
            ):
                with self.assertRaisesRegex(ValueError, "domínios oficiais"):
                    pipeline.baixar(
                        "https://www.planalto.gov.br/fonte", destino
                    )
            self.assertFalse(destino.exists())
            self.assertFalse(destino.with_suffix(".html.part").exists())

    def test_download_rejeita_tipo_de_conteudo_incompativel(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            destino = Path(temp) / "fonte.html"

            def simular_pdf(comando: list[str], **_: object) -> object:
                temporario = Path(comando[comando.index("--output") + 1])
                cabecalhos = Path(comando[comando.index("--dump-header") + 1])
                temporario.write_bytes(b"%PDF-1.7")
                cabecalhos.write_text(
                    "HTTP/2 200\ncontent-type: application/pdf\n\n",
                    encoding="latin-1",
                )
                return pipeline.subprocess.CompletedProcess(
                    comando,
                    0,
                    stdout="https://www.planalto.gov.br/fonte",
                    stderr="",
                )

            with patch.object(pipeline.subprocess, "run", side_effect=simular_pdf):
                with self.assertRaisesRegex(RuntimeError, "tipo de conteúdo"):
                    pipeline.baixar(
                        "https://www.planalto.gov.br/fonte", destino
                    )
            self.assertFalse(destino.exists())

    def test_decodifica_html_utf16_com_bom(self) -> None:
        html = "<html><body><p>Art. 1º A proteção começa aqui.</p></body></html>"
        with tempfile.TemporaryDirectory() as temp:
            for encoding in ("utf-16-le", "utf-16-be"):
                path = Path(temp) / f"{encoding}.html"
                bom = b"\xff\xfe" if encoding == "utf-16-le" else b"\xfe\xff"
                path.write_bytes(bom + html.encode(encoding))
                self.assertEqual(pipeline.decodificar_html(path), html)
            # Byte solto ao final, observado na página da Lei 11.340/2006.
            impar = Path(temp) / "impar.html"
            impar.write_bytes(b"\xff\xfe" + html.encode("utf-16-le") + b" ")
            self.assertEqual(pipeline.decodificar_html(impar), html)

    def test_pagina_com_milhares_de_tags_sem_fechamento_nao_estoura_recursao(self) -> None:
        # O Decreto-Lei 1.001/1969 (CPM) tem árvore com profundidade ~1.700
        # por tags inline nunca fechadas; o parser e os percursos precisam
        # funcionar bem acima disso.
        html = "<html><body>" + "<font>" * 3000 + "<p>Art. 1º Texto profundo.</p>"
        arvore = pipeline.analisar_html(html)
        texto = pipeline.texto_elemento(arvore)
        self.assertIn("Art. 1º Texto profundo.", texto)

    def test_rotulo_de_artigo_tolera_defeitos_tipograficos_do_planalto(self) -> None:
        # "Art 4º" sem ponto ocorre na Lei 6.001; "Art . 16." com espaço antes
        # do ponto ocorre na Lei 6.880. "Artigo 1º" (texto de tratados) e
        # "Arts. 5º e 6º" não são rótulos de artigo próprios.
        self.assertEqual(pipeline.ARTIGO.match("Art 4º Os índios...").group(1), "4")
        self.assertEqual(pipeline.ARTIGO.match("Art . 16. Os círculos...").group(1), "16")
        self.assertEqual(pipeline.ARTIGO.match("Art. 1.001. Texto.").group(1), "1.001")
        self.assertIsNone(pipeline.ARTIGO.match("Artigo 1º do tratado."))
        self.assertIsNone(pipeline.ARTIGO.match("Arts. 5º e 6º aplicam-se."))

    def test_transformacao_ignora_artigo_citado_de_outra_norma(self) -> None:
        # Padrão da Lei 14.133: o art. 178 insere dispositivos no Código
        # Penal e a página cita o texto inserido com o rótulo apontando
        # (href) para Del2848.htm. O dispositivo citado não pertence à lei.
        # A Lei 6.515 cita redações pontilhadas sem link ("Art. 155. ....."),
        # e a Lei 11.804 tem artigos vetados próprios com o rótulo ligado à
        # mensagem de veto — o vetado é preservado; a citação, não.
        html = """
        <html><body>
        <p><a name="art1"></a>Art. 1º Artigo próprio da lei.</p>
        <p>Art. 2º O Código passa a vigorar acrescido do seguinte artigo:</p>
        <p><a href="Del2848.htm#art337e">Art. 337-E</a>. Texto inserido no
        outro diploma.</p>
        <p>Art. 155. ..................................................
        II - trecho citado de norma alterada.</p>
        <p><a href="Msg/VEP-100.htm">Art. 2º-A</a>. (VETADO)</p>
        <p><a name="art3"></a>Art. 3º Esta Lei entra em vigor.</p>
        <p>Art. 59-A. Texto de outra norma reproduzido sem marcador algum,
        descartado por decisão explícita no manifesto.</p>
        </body></html>
        """
        config = {
            "fontes": [
                {
                    "codigo": "XX",
                    "url": "https://www.planalto.gov.br/teste",
                    "arquivo_bruto": "xx.html",
                    "destino": "lei_xx.json",
                    "descartar_artigos": ["59-A"],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto"
            publicados = raiz / "publicados"
            bruto.mkdir()
            publicados.mkdir()
            (bruto / "xx.html").write_text(html, encoding="utf-8")
            (publicados / "lei_xx.json").write_text(
                json.dumps({"_meta": {}, "artigos": {}}), encoding="utf-8"
            )
            [saida] = pipeline.transformar_legislacao(
                config, bruto, publicados, raiz / "candidatos"
            )
            objeto = json.loads(saida.read_text())
        self.assertEqual(set(objeto["artigos"]), {"1", "2", "2-A", "3"})
        self.assertIn("VETADO", objeto["artigos"]["2-A"]["texto"])

    def test_transforma_legislacao_sem_remover_registro_nao_reencontrado(self) -> None:
        html = """
        <html><body><p>TÍTULO I</p><p>Art. 1º Texto atualizado.</p>
        <p>Art. 1.001. Artigo novo.</p></body></html>
        """
        atual = {
            "_meta": {
                "codigo": "XX",
                "nome": "Código de teste",
                "lei": "Lei de teste",
                "url_base": "https://www.planalto.gov.br/teste",
                "total_artigos": 2,
            },
            "artigos": {
                "1": {"numero": "1", "texto": "Texto antigo.", "url": "https://www.planalto.gov.br/teste#1"},
                "2": {"numero": "2", "texto": "Retido.", "url": "https://www.planalto.gov.br/teste#2"},
            },
        }
        config = {
            "fontes": [
                {
                    "codigo": "XX",
                    "url": "https://www.planalto.gov.br/teste",
                    "arquivo_bruto": "xx.html",
                    "destino": "lei_xx.json",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto"
            publicados = raiz / "publicados"
            candidatos = raiz / "candidatos"
            bruto.mkdir()
            publicados.mkdir()
            (bruto / "xx.html").write_text(html, encoding="utf-8")
            (publicados / "lei_xx.json").write_text(json.dumps(atual), encoding="utf-8")
            [saida] = pipeline.transformar_legislacao(
                config, bruto, publicados, candidatos
            )
            objeto = json.loads(saida.read_text())
        self.assertEqual(set(objeto["artigos"]), {"1", "2", "1001"})
        self.assertEqual(objeto["_meta"]["registros_retidos_sem_correspondencia"], ["2"])

    def test_transforma_edicao_jurisprudencia_em_teses(self) -> None:
        html = """
        <div class="gridEdicaoJT"><span class="numeroSumula">1</span>
          <span class="clsVerbete">PROCESSO ADMINISTRATIVO DISCIPLINAR - I</span>
          <b class="clsData">20/09/2013</b><b class="clsData">13/11/2013</b>
        </div>
        <div class="clsTemasJT redacaoAtual"><div class="clsSubmitPesquisaTema">
          <a>1) A falta de defesa técnica não ofende a Constituição.</a>
        </div><div class="clsJulgadosJT"><a>julgado 1</a></div></div>
        """
        atual = {
            "_meta": {},
            "teses": {
                "JT_001_T01": {
                    "edicao": 1,
                    "ramo_direito": "Direito Administrativo",
                    "qtd_julgados": 3,
                }
            },
        }
        config = {"destino": "jt_stj.json"}
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            edicoes = raiz / "bruto" / "edicoes"
            publicados = raiz / "publicados"
            edicoes.mkdir(parents=True)
            publicados.mkdir()
            (edicoes / "1.html").write_text(html, encoding="utf-8")
            (publicados / "jt_stj.json").write_text(json.dumps(atual), encoding="utf-8")
            [saida] = pipeline.transformar_jt(
                config, raiz / "bruto", publicados, raiz / "candidatos"
            )
            objeto = json.loads(saida.read_text())
        tese = objeto["teses"]["JT_001_T01"]
        self.assertEqual(tese["data_publicacao"], "2013-11-13")
        self.assertEqual(tese["ramo_direito"], "Direito Administrativo")
        self.assertEqual(tese["qtd_julgados"], 1)

    def test_edicao_179_publicada_contem_somente_as_dez_teses_oficiais(self) -> None:
        path = (
            ROOT
            / "ferramentas"
            / "pesquisa"
            / "vade-mecum"
            / "data"
            / "jt_stj.json"
        )
        objeto = json.loads(path.read_text(encoding="utf-8"))
        ids = {
            identificador
            for identificador, tese in objeto["teses"].items()
            if tese["edicao"] == 179
        }
        self.assertEqual(ids, {f"JT_179_T{numero:02d}" for numero in range(1, 11)})
        self.assertNotIn("JT_179_T19", objeto["teses"])

    def test_ctb_publicado_inclui_artigo_326_c_e_contagem_coerente(self) -> None:
        path = (
            ROOT
            / "ferramentas"
            / "pesquisa"
            / "vade-mecum"
            / "data"
            / "lei_ctb.json"
        )
        objeto = json.loads(path.read_text(encoding="utf-8"))
        artigos = objeto["artigos"]
        self.assertEqual(objeto["_meta"]["total_artigos"], len(artigos))
        self.assertIn(
            "Dia Mundial em Memória das Vítimas do Trânsito",
            artigos["326-C"]["texto"],
        )
        self.assertEqual(artigos["326-B"]["next"], "326-C")
        self.assertEqual(artigos["326-C"]["prev"], "326-B")
        self.assertEqual(artigos["326-C"]["next"], "327")
        self.assertEqual(artigos["327"]["prev"], "326-C")

    def test_transforma_csv_oficial_de_temas(self) -> None:
        campos_temas = [
            "sequencialPrecedente", "tipoPrecedente", "numeroPrecedente",
            "dataPrimeiraAfetacao", "dataJulgamento", "situacao",
            "questaoSubmetidaAJulgamento", "teseFirmada", "orgaoJulgador", "Assuntos",
        ]
        campos_processos = [
            "sequencialPrecedente", "tipoPrecedente", "numeroPrecedente", "Processo",
            "numeroRegistro", "ministroRelator", "leadingCase", "origemUF",
        ]
        config = {
            "destino": "flash_temas_stj.json",
            "package_id": "4238da2f-c07b-4c1a-b345-4402accacdcf",
            "join_key": "sequencialPrecedente",
            "fontes": [
                {"url": "https://dadosabertos.web.stj.jus.br/api/3/action/package_show?id=precedentes-qualificados"},
                {
                    "resource_id": "df29da13-7d6b-41ba-ad96-cd1a5bbd191c",
                    "url": "https://dadosabertos.web.stj.jus.br/temas.csv",
                },
                {
                    "resource_id": "7ed21202-0049-4fcb-aa7c-48d810d3c499",
                    "url": "https://dadosabertos.web.stj.jus.br/processos.csv",
                },
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto"
            publicados = raiz / "publicados"
            bruto.mkdir()
            publicados.mkdir()
            with (bruto / "temas.csv").open("w", encoding="utf-8", newline="") as arquivo:
                writer = csv.DictWriter(arquivo, fieldnames=campos_temas)
                writer.writeheader()
                writer.writerow({
                    "sequencialPrecedente": "263", "tipoPrecedente": "Tema",
                    "numeroPrecedente": "1", "dataPrimeiraAfetacao": "2008-10-10",
                    "dataJulgamento": "2012-05-02", "situacao": "Trânsito em Julgado",
                    "questaoSubmetidaAJulgamento": "Questão de teste.",
                    "teseFirmada": "Tese de teste.", "orgaoJulgador": "CE",
                    "Assuntos": "8826- DIREITO PROCESSUAL CIVIL, 8867- Substituição Processual",
                })
            with (bruto / "processos.csv").open("w", encoding="utf-8", newline="") as arquivo:
                writer = csv.DictWriter(arquivo, fieldnames=campos_processos)
                writer.writeheader()
                writer.writerow({
                    "sequencialPrecedente": "263", "tipoPrecedente": "Tema",
                    "numeroPrecedente": "1", "Processo": "REsp 1091443",
                    "numeroRegistro": "200802176867", "ministroRelator": "RELATOR",
                    "leadingCase": "S", "origemUF": "SP",
                })
            (bruto / "metadados.json").write_text("{}", encoding="utf-8")
            (publicados / "flash_temas_stj.json").write_text(
                json.dumps({"_meta": {}, "temas": {}}), encoding="utf-8"
            )
            [saida] = pipeline.transformar_temas(
                config, bruto, publicados, raiz / "candidatos"
            )
            objeto = json.loads(saida.read_text())
        tema = objeto["temas"]["1"]
        self.assertEqual(tema["processo"], "REsp 1091443/SP")
        self.assertEqual(tema["orgaoJulgador"], "Corte Especial")
        self.assertEqual(objeto["_meta"]["totalTemas"], 1)
        source = objeto["_meta"]["source"]
        referencia = source["officialPublicReference"]
        self.assertEqual(referencia["joinKey"], "sequencialPrecedente")
        self.assertEqual(
            referencia["resources"]["temas"]["id"],
            "df29da13-7d6b-41ba-ad96-cd1a5bbd191c",
        )

    def test_relatorio_sinaliza_remocoes_antes_da_promocao(self) -> None:
        relatorio = {
            "conjuntos": {
                "teses": [
                    {"arquivo": "jt_stj.json", "removidos": ["JT_001_T01"]}
                ],
                "sumulas": [
                    {"arquivo": "sumulas_stj.json", "removidos": []}
                ],
            }
        }
        self.assertEqual(
            pipeline.remocoes_do_relatorio(relatorio),
            ["teses/jt_stj.json: 1"],
        )

    def test_promocao_exige_confirmacao_literal(self) -> None:
        artigo = {
            "1": {
                "numero": "1",
                "texto": "Texto.",
                "url": "https://www.planalto.gov.br/teste",
            }
        }
        with tempfile.TemporaryDirectory() as temp:
            dados, execucao, publicados = self.preparar_promocao(
                Path(temp), artigo, artigo
            )
            with self.assertRaisesRegex(ValueError, "use --confirmar PROMOVER"):
                pipeline.promover(
                    dados, ["legislacao_teste"], execucao, publicados, "sim"
                )
            self.assertFalse((execucao / "backup").exists())

    def test_validacao_bloqueia_promocao_com_caminho_local(self) -> None:
        artigo = {
            "1": {
                "numero": "1",
                "texto": "Texto.",
                "url": "https://www.planalto.gov.br/teste",
            }
        }
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            dados, execucao, publicados = self.preparar_promocao(
                raiz,
                artigo,
                artigo,
                {"total_artigos": 1, "origem": "/Users/pessoa/Downloads/fonte.html"},
            )
            publicado_antes = (publicados / "lei_teste.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "caminho absoluto local"):
                pipeline.promover(
                    dados, ["legislacao_teste"], execucao, publicados, "PROMOVER"
                )
            self.assertEqual(
                (publicados / "lei_teste.json").read_bytes(), publicado_antes
            )
            self.assertFalse((execucao / "backup").exists())

    def test_remocao_exige_aceite_e_backup_preserva_publicado(self) -> None:
        artigo_1 = {
            "numero": "1",
            "texto": "Texto.",
            "url": "https://www.planalto.gov.br/teste",
        }
        artigo_2 = {
            "numero": "2",
            "texto": "Será removido.",
            "url": "https://www.planalto.gov.br/teste",
        }
        with tempfile.TemporaryDirectory() as temp:
            dados, execucao, publicados = self.preparar_promocao(
                Path(temp), {"1": artigo_1, "2": artigo_2}, {"1": artigo_1}
            )
            publicado_antes = (publicados / "lei_teste.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "use --aceitar-remocoes"):
                pipeline.promover(
                    dados, ["legislacao_teste"], execucao, publicados, "PROMOVER"
                )
            self.assertEqual(
                (publicados / "lei_teste.json").read_bytes(), publicado_antes
            )
            self.assertFalse((execucao / "backup").exists())

            pipeline.promover(
                dados,
                ["legislacao_teste"],
                execucao,
                publicados,
                "PROMOVER",
                aceitar_remocoes=True,
            )
            backup = json.loads(
                (execucao / "backup" / "lei_teste.json").read_text()
            )
            promovido = json.loads((publicados / "lei_teste.json").read_text())
            self.assertEqual(set(backup["artigos"]), {"1", "2"})
            self.assertEqual(set(promovido["artigos"]), {"1"})
            self.assertTrue((execucao / "promocao.json").exists())
            backup_antes = (execucao / "backup" / "lei_teste.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "já foi promovida"):
                pipeline.promover(
                    dados,
                    ["legislacao_teste"],
                    execucao,
                    publicados,
                    "PROMOVER",
                    aceitar_remocoes=True,
                )
            self.assertEqual(
                (execucao / "backup" / "lei_teste.json").read_bytes(),
                backup_antes,
            )

    def test_mudanca_volumosa_exige_aceite_adicional(self) -> None:
        publicados_artigos = {
            str(numero): {
                "numero": str(numero),
                "texto": f"Texto anterior {numero}.",
                "url": "https://www.planalto.gov.br/teste",
            }
            for numero in range(1, 101)
        }
        candidatos_artigos = {
            numero: {**artigo, "texto": artigo["texto"].replace("anterior", "novo")}
            for numero, artigo in publicados_artigos.items()
        }
        with tempfile.TemporaryDirectory() as temp:
            dados, execucao, publicados = self.preparar_promocao(
                Path(temp), publicados_artigos, candidatos_artigos
            )
            with self.assertRaisesRegex(
                ValueError, "use --aceitar-mudanca-volumosa"
            ):
                pipeline.promover(
                    dados, ["legislacao_teste"], execucao, publicados, "PROMOVER"
                )
            pipeline.promover(
                dados,
                ["legislacao_teste"],
                execucao,
                publicados,
                "PROMOVER",
                aceitar_mudanca_volumosa=True,
            )
            promovido = json.loads((publicados / "lei_teste.json").read_text())
            self.assertEqual(promovido["artigos"]["1"]["texto"], "Texto novo 1.")


if __name__ == "__main__":
    unittest.main()
