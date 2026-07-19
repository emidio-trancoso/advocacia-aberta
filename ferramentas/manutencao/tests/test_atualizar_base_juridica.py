from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


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
            "temas_rg_stf",
            "informativo_stf",
            "espelhos_stj",
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

    def test_nome_real_de_titulos_e_capitulos_e_extraido(self) -> None:
        # BASE-018: a página costuma separar o rótulo ("TÍTULO I") do nome
        # real ("Dos Princípios Fundamentais") em parágrafos distintos, às
        # vezes com uma remissão "(Vide ...)" entre eles; outras vezes escreve
        # tudo na mesma linha. Sem nome identificável, mantém a linha do
        # marcador, como antes.
        html = """
        <html><body>
        <p>TÍTULO I</p>
        <p>(Vide Lei nº 1.234, de 2020)</p>
        <p>DOS PRINCÍPIOS FUNDAMENTAIS</p>
        <p>CAPÍTULO II - DA COBRANÇA</p>
        <p>SEÇÃO I</p>
        <p>Das Disposições Gerais</p>
        <p>Art. 1º Primeiro artigo.</p>
        <p>TÍTULO II</p>
        <p>Art. 2º Segundo artigo, em título sem nome na página.</p>
        </body></html>
        """
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
        hierarquia = objeto["artigos"]["1"]["hierarchy"]
        self.assertEqual(hierarquia["title_name"], "DOS PRINCÍPIOS FUNDAMENTAIS")
        self.assertEqual(hierarquia["chapter_name"], "DA COBRANÇA")
        self.assertEqual(hierarquia["section_name"], "Das Disposições Gerais")
        self.assertEqual(objeto["artigos"]["2"]["hierarchy"]["title_name"], "TÍTULO II")

    def test_nome_de_divisao_com_sufixo_de_letra_usa_paragrafo_seguinte(self) -> None:
        # "CAPÍTULO VI-A"/"SEÇÃO II-A" (dispositivos incluídos por lei posterior):
        # o traço do sufixo é consumido pelo rótulo e sobra uma letra isolada
        # ("A"), que não é nome. O nome real fica no parágrafo seguinte, após a
        # remissão "(Incluído ...)", como no caso sem nome na mesma linha.
        html = """
        <html><body>
        <p>CAPÍTULO VI-A</p>
        <p>(Incluído pela Lei nº 14.112, de 2020)</p>
        <p>DA INSOLVÊNCIA TRANSNACIONAL</p>
        <p>SEÇÃO II-A</p>
        <p>(Incluído pela Lei nº 14.112, de 2020)</p>
        <p>Das Conciliações e das Mediações</p>
        <p>Art. 1º Primeiro artigo.</p>
        </body></html>
        """
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
        hierarquia = objeto["artigos"]["1"]["hierarchy"]
        self.assertEqual(hierarquia["chapter"], "VI")
        self.assertEqual(hierarquia["chapter_name"], "DA INSOLVÊNCIA TRANSNACIONAL")
        self.assertEqual(hierarquia["section"], "II")
        self.assertEqual(hierarquia["section_name"], "Das Conciliações e das Mediações")

    def test_nome_de_divisao_descarta_remissao_entre_parenteses(self) -> None:
        # A remissão da lei que incluiu ou revogou a divisão gruda no nome
        # ("DA LAJE (Incluído pela Lei ...)"), fica sozinha na linha do marcador
        # revogado ("(Revogado ...)") ou no parágrafo seguinte — nenhuma é nome.
        html = """
        <html><body>
        <p>TÍTULO XI DA LAJE (Incluído pela Lei nº 13.465, de 2017)</p>
        <p>Art. 1º Primeiro artigo.</p>
        <p>CAPÍTULO II (Revogado pela Lei nº 14.368, de 2022)</p>
        <p>Art. 2º Segundo artigo.</p>
        <p>CAPÍTULO X</p>
        <p>DO FUNDO DE INVESTIMENTO (Incluído pela Lei nº 13.874, de 2019)</p>
        <p>Art. 3º Terceiro artigo.</p>
        <p>Seção VIII (Incluída pela Lei nº 12.010, de 2009) Vigência Da Habilitação de Pretendentes</p>
        <p>Art. 4º Quarto artigo.</p>
        <p>SEÇÃO IX DA CONCESSÃO DAS FÉRIAS (Redação dada pelo Decreto-lei nº 1.535, de 13.4.1977</p>
        <p>Art. 5º Quinto artigo.</p>
        <p>CAPÍTULO XI Vigência da Legislação Tributária</p>
        <p>Art. 6º Sexto artigo.</p>
        </body></html>
        """
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
        arts = objeto["artigos"]
        # nome na mesma linha, com remissão colada
        self.assertEqual(arts["1"]["hierarchy"]["title_name"], "DA LAJE")
        # divisão revogada, sem nome real: rótulo limpo, sem a remissão
        self.assertEqual(arts["2"]["hierarchy"]["chapter_name"], "CAPÍTULO II")
        # nome no parágrafo seguinte, com remissão colada
        self.assertEqual(
            arts["3"]["hierarchy"]["chapter_name"], "DO FUNDO DE INVESTIMENTO"
        )
        # anotação "Vigência" logo após a remissão é descartada com ela
        self.assertEqual(
            arts["4"]["hierarchy"]["section_name"], "Da Habilitação de Pretendentes"
        )
        # remissão sem parêntese de fechamento (o Planalto perde o ")")
        self.assertEqual(
            arts["5"]["hierarchy"]["section_name"], "DA CONCESSÃO DAS FÉRIAS"
        )
        # nome real que contém "Vigência" (não segue remissão) é preservado
        self.assertEqual(
            arts["6"]["hierarchy"]["chapter_name"], "Vigência da Legislação Tributária"
        )

    def test_hierarquia_tolera_ortografia_antiga_sem_acento(self) -> None:
        # Padrão do Decreto 2.044/1908: a página usa "TITULO I", "CAPITULO
        # XII" e "SECÇÃO I" na ortografia da época. Sem tolerância, essas
        # linhas colariam no texto do artigo anterior em vez de marcar a
        # hierarquia.
        html = """
        <html><body>
        <p>TITULO I</p>
        <p>Da letra de cambio</p>
        <p>CAPITULO I</p>
        <p>Art. 1º A letra de cambio é uma ordem de pagamento.</p>
        <p>SECÇÃO I</p>
        <p>Art. 2º Segundo artigo.</p>
        </body></html>
        """
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
        self.assertEqual(set(objeto["artigos"]), {"1", "2"})
        self.assertNotIn("SECÇÃO", objeto["artigos"]["1"]["texto"])
        hierarquia = objeto["artigos"]["1"]["hierarchy"]
        self.assertEqual(hierarquia["title"], "I")
        self.assertEqual(hierarquia["chapter"], "I")
        self.assertEqual(objeto["artigos"]["2"]["hierarchy"]["section"], "I")

    def test_fim_antes_encerra_extracao_antes_do_marcador(self) -> None:
        # Padrão do Código Comercial de 1850: depois do art. 913 do corpo, a
        # página traz o "TÍTULO ÚNICO" da administração da justiça comercial
        # com arts. 1º a 30 PRÓPRIOS — capturá-los colidiria com a numeração
        # do corpo. O fim_antes corta a página antes do marcador.
        html = """
        <html><body>
        <p>Art. 912 - Penúltimo artigo do corpo.</p>
        <p>Art. 913 - Último artigo do corpo.</p>
        <p>TÍTULO ÚNICO</p>
        <p>DA ADMINISTRAÇÃO DA JUSTIÇA NOS NEGÓCIOS E CAUSAS COMERCIAIS</p>
        <p>Art. 1º - Haverá Tribunais do Comércio na Capital do Império.</p>
        <p>Art. 2º - Composição do Tribunal.</p>
        </body></html>
        """
        config = {
            "fontes": [
                {
                    "codigo": "XX",
                    "url": "https://www.planalto.gov.br/teste",
                    "arquivo_bruto": "xx.html",
                    "destino": "lei_xx.json",
                    "fim_antes": "TÍTULO ÚNICO",
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
        self.assertEqual(set(objeto["artigos"]), {"912", "913"})
        self.assertNotIn("Tribunais do Comércio", objeto["artigos"]["913"]["texto"])

    def test_fim_antes_ausente_na_pagina_interrompe_a_transformacao(self) -> None:
        html = "<html><body><p>Art. 1º Texto.</p></body></html>"
        config = {
            "fontes": [
                {
                    "codigo": "XX",
                    "url": "https://www.planalto.gov.br/teste",
                    "arquivo_bruto": "xx.html",
                    "destino": "lei_xx.json",
                    "fim_antes": "TÍTULO ÚNICO",
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
            with self.assertRaises(ValueError):
                pipeline.transformar_legislacao(
                    config, bruto, publicados, raiz / "candidatos"
                )

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


def _tabela_rg(linhas: str, cabecalho: list[str] | None = None) -> str:
    colunas = cabecalho or list(pipeline.COLUNAS_TEMAS_RG)
    ths = "".join(f"<th>{c}</th>" for c in colunas)
    return (
        "<html><head><title>Título</title></head><body>"
        f"<table><thead><tr>{ths}</tr></thead><tbody>{linhas}</tbody></table>"
        "</body></html>"
    )


# Fixture com duas linhas: o tema 1 tem mojibake em "Há Repercussão" ("HÃ¡"),
# links em Manifestação/Acórdão/Plenário Virtual e um espaço não encodado na
# URL do acórdão; o tema 2 é cancelado, sem tese e com células-link "-".
_LINHAS_RG = (
    "<tr>"
    "<td>0001</td><td>RE 559937</td><td>MIN. ELLEN GRACIE</td>"
    "<td>Base do PIS e da COFINS</td><td>Descrição um.</td><td>Descrição um.</td>"
    '<td><a href="https://portal.stf.jus.br/x/verPronunciamento.asp?pronunciamento=1">'
    "<div>Manifestação</div></a></td>"
    '<td><a href="https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=RE 559937">'
    "<div>Acórdão</div></a></td>"
    '<td><a href="https://portal.stf.jus.br/x/detalharProcesso.asp?numeroTema=1">'
    "<div>Acórdão</div></a></td>"
    "<td>HÃ¡</td><td>21/03/2013</td><td>Trânsito em Julgado</td>"
    "<td>Tese do tema um.</td><td>21/03/2013</td><td></td>"
    "</tr>"
    "<tr>"
    "<td>0002</td><td>RE 000002</td><td>MIN. FULANO</td>"
    "<td>Tema dois</td><td>Descrição dois.</td><td>Descrição dois.</td>"
    "<td>-</td><td>-</td><td>-</td>"
    "<td>NÃ£o hÃ¡</td><td></td><td>Cancelado</td>"
    "<td></td><td></td><td>Obs dois.</td>"
    "</tr>"
)


class CorrigirMojibakeTest(unittest.TestCase):
    def test_recupera_mojibake_e_preserva_utf8_correto(self) -> None:
        self.assertEqual(pipeline.corrigir_mojibake("HÃ¡"), "Há")
        self.assertEqual(pipeline.corrigir_mojibake("NÃ£o hÃ¡"), "Não há")
        # UTF-8 genuíno (acento isolado) e ASCII passam intactos.
        self.assertEqual(
            pipeline.corrigir_mojibake("Trânsito em Julgado"), "Trânsito em Julgado"
        )
        self.assertEqual(
            pipeline.corrigir_mojibake("Âmbito de incidência"),
            "Âmbito de incidência",
        )
        self.assertEqual(pipeline.corrigir_mojibake("Data da Tese"), "Data da Tese")


class TransformarTemasRGTest(unittest.TestCase):
    def transformar(self, html: str) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto" / "temas_rg_stf"
            bruto.mkdir(parents=True)
            (bruto / "repercussao_geral.xls").write_text(html, encoding="utf-8")
            candidatos = raiz / "candidatos"
            config = {
                "destino": "temas_rg_stf.json",
                "fontes": [
                    {
                        "id": "exportar",
                        "url": "https://portal.stf.jus.br/jurisprudenciaRepercussao/exportarDados.asp",
                        "arquivo_bruto": "repercussao_geral.xls",
                    }
                ],
            }
            pipeline.transformar_temas_rg(config, bruto, raiz / "pub", candidatos)
            return json.loads(
                (candidatos / "temas_rg_stf.json").read_text(encoding="utf-8")
            )

    def test_extrai_campos_corrige_mojibake_e_links(self) -> None:
        objeto = self.transformar(_tabela_rg(_LINHAS_RG))
        temas = objeto["temas"]
        self.assertEqual(objeto["_meta"]["totalTemas"], 2)
        self.assertEqual(objeto["_meta"]["temasComTese"], 1)
        self.assertEqual(objeto["_meta"]["situacoes"]["Cancelado"], 1)

        um = temas["1"]
        self.assertEqual(um["numero"], 1)
        self.assertEqual(um["repercussao"], "Há")  # mojibake corrigido
        self.assertEqual(um["situacao"], "Trânsito em Julgado")
        self.assertEqual(um["tese"], "Tese do tema um.")
        self.assertEqual(
            um["links"]["paginaTema"],
            "https://portal.stf.jus.br/jurisprudenciaRepercussao/verTeseTema.asp?numTema=1",
        )
        self.assertIn("verPronunciamento.asp", um["links"]["manifestacao"])
        self.assertIn("detalharProcesso.asp?numeroTema=1", um["links"]["detalhamento"])
        # Espaço da URL do acórdão foi encodado.
        self.assertIn("classeNumeroIncidente=RE%20559937", um["links"]["acordao"])
        self.assertNotIn("plenarioVirtual", um)

        dois = temas["2"]
        self.assertEqual(dois["repercussao"], "Não há")  # mojibake corrigido
        self.assertEqual(dois["situacao"], "Cancelado")
        self.assertEqual(dois["tese"], "")
        self.assertEqual(dois["observacao"], "Obs dois.")
        # Células "-" não geram links; sobra só a página do tema.
        self.assertEqual(list(dois["links"]), ["paginaTema"])

    def test_cabecalho_divergente_falha(self) -> None:
        cabecalho = list(pipeline.COLUNAS_TEMAS_RG)
        cabecalho[3] = "Coluna Trocada"
        with self.assertRaisesRegex(ValueError, "cabeçalho"):
            self.transformar(_tabela_rg(_LINHAS_RG, cabecalho))


def _xlsx_bytes(cabecalho: list[str], linhas: list[dict[int, str]]) -> bytes:
    """Monta um XLSX mínimo (zip+XML) com strings inline e células numéricas."""
    import io

    def coluna(indice: int) -> str:
        return chr(ord("A") + indice)

    def celula(indice: int, linha_num: int, valor: str) -> str:
        ref = f"{coluna(indice)}{linha_num}"
        # Colunas Informativo (0) e Data Julgamento (6) são numéricas na fonte.
        if indice in (0, 6):
            return f'<c r="{ref}" t="n"><v>{valor}</v></c>'
        seguro = valor.replace("&", "&amp;").replace("<", "&lt;")
        return f'<c r="{ref}" t="inlineStr"><is><t>{seguro}</t></is></c>'

    partes = ['<row r="1">']
    partes += [celula(i, 1, nome) for i, nome in enumerate(cabecalho)]
    partes.append("</row>")
    for numero, linha in enumerate(linhas, start=2):
        partes.append(f'<row r="{numero}">')
        partes += [
            celula(indice, numero, valor)
            for indice, valor in sorted(linha.items())
            if valor != ""
        ]
        partes.append("</row>")
    sheet = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<sheetData>" + "".join(partes) + "</sheetData></worksheet>"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_arquivo:
        zip_arquivo.writestr("xl/worksheets/sheet1.xml", sheet.encode("utf-8"))
    return buffer.getvalue()


class InformativoXlsxTest(unittest.TestCase):
    def test_serial_excel_para_data(self) -> None:
        # Valor real do snapshot (INF_1222_001, edição 1222).
        self.assertEqual(pipeline.serial_excel_para_data("46190.125"), "17/06/2026")
        self.assertEqual(pipeline.serial_excel_para_data("texto"), "texto")

    def transformar(self, cabecalho: list[str], linhas: list[dict[int, str]]) -> dict:
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto" / "informativo_stf"
            bruto.mkdir(parents=True)
            (bruto / "Dados_InformativosSTF.xlsx").write_bytes(
                _xlsx_bytes(cabecalho, linhas)
            )
            candidatos = raiz / "candidatos"
            config = {
                "destino": "informativo_stf.json",
                "fontes": [
                    {
                        "id": "planilha",
                        "url": "https://www.stf.jus.br/arquivo/cms/informativoSTF/anexo/Informativo_Dados/Dados_InformativosSTF.xlsx",
                        "arquivo_bruto": "Dados_InformativosSTF.xlsx",
                    }
                ],
            }
            pipeline.transformar_informativo(config, bruto, raiz / "pub", candidatos)
            return json.loads(
                (candidatos / "informativo_stf.json").read_text(encoding="utf-8")
            )

    def test_extrai_julgados_datas_e_links(self) -> None:
        linhas = [
            {0: "1222", 1: "ADI", 2: "5069", 6: "46190", 7: "MIN. FULANO",
             9: "Plenário", 11: "Concluído", 12: "Título um", 14: "Resumo um",
             16: "Direito Constitucional", 17: "Federalismo", 18: "Não", 20: "CF/1988"},
            {0: "1222", 1: "RE", 2: "999", 6: "46188", 12: "Título dois",
             13: "Tese dois", 16: "Direito Penal", 17: "Insignificância",
             18: "Sim", 19: "1234"},
        ]
        objeto = self.transformar(list(pipeline.COLUNAS_INFORMATIVO), linhas)
        registros = objeto["informativos"]
        self.assertEqual(objeto["_meta"]["totalRegistros"], 2)
        self.assertEqual(objeto["_meta"]["totalEdicoes"], 1)
        self.assertEqual(objeto["_meta"]["julgadosComTese"], 1)
        self.assertIn("license", objeto["_meta"]["source"])

        um = registros["INF_1222_001"]
        self.assertEqual(um["edicao"], 1222)
        self.assertEqual(um["sequencial"], 1)
        self.assertEqual(um["dataJulgamento"], "17/06/2026")  # serial convertido
        self.assertEqual(um["materia"], "Federalismo")
        self.assertEqual(
            um["links"]["edicao"],
            "https://www.stf.jus.br/arquivo/informativo/documento/informativo1222.htm",
        )
        dois = registros["INF_1222_002"]
        self.assertEqual(dois["sequencial"], 2)
        self.assertEqual(dois["teseJulgado"], "Tese dois")
        self.assertEqual(dois["temaRG"], "1234")

    def test_cabecalho_divergente_falha(self) -> None:
        cabecalho = list(pipeline.COLUNAS_INFORMATIVO)
        cabecalho[13] = "Coluna Trocada"
        with self.assertRaisesRegex(ValueError, "cabeçalho"):
            self.transformar(cabecalho, [{0: "1", 17: "x"}])


class EspelhosStjTest(unittest.TestCase):
    def test_data_publicacao_espelho(self) -> None:
        self.assertEqual(
            pipeline.data_publicacao_espelho("DJE        DATA:31/05/2022"),
            "31/05/2022",
        )
        self.assertEqual(pipeline.data_publicacao_espelho(""), "")
        self.assertEqual(pipeline.data_publicacao_espelho(None), "")

    def transformar(self, meses: dict[str, str]) -> dict:
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto" / "espelhos_stj"
            orgao_dir = bruto / "corte-especial"
            orgao_dir.mkdir(parents=True)
            (orgao_dir / "package.json").write_text(
                json.dumps(
                    {"result": {"id": "pkg-ce", "metadata_modified": "2026-06-09T00:00:00"}}
                ),
                encoding="utf-8",
            )
            for nome, conteudo in meses.items():
                (orgao_dir / nome).write_text(conteudo, encoding="utf-8")
            candidatos = raiz / "candidatos"
            config = {
                "destino": "espelhos_stj.json",
                "fontes": [
                    {
                        "id": "corte-especial",
                        "url": "https://dadosabertos.web.stj.jus.br/api/3/action/package_show?id=espelhos-de-acordaos-corte-especial",
                        "arquivo_bruto": "corte-especial/package.json",
                    }
                ],
            }
            pipeline.transformar_espelhos(config, bruto, raiz / "pub", candidatos)
            return json.loads(
                (candidatos / "espelhos_stj.json").read_text(encoding="utf-8")
            )

    def test_curadoria_links_e_mes_malformado(self) -> None:
        valido = json.dumps(
            [
                {
                    "id": "000815561",
                    "numeroProcesso": "3329",
                    "numeroRegistro": "201900000001",
                    "siglaClasse": "REsp",
                    "descricaoClasse": "RECURSO ESPECIAL",
                    "nomeOrgaoJulgador": "CORTE ESPECIAL",
                    "ministroRelator": "FULANO",
                    "dataPublicacao": "DJE        DATA:26/05/2022",
                    "ementa": "PROCESSUAL CIVIL. Ementa do acórdão.",
                    "teseJuridica": "Tese do acórdão.",
                    "tema": "Tema Repetitivo 1",
                    "jurisprudenciaCitada": "REsp 1",
                    "referenciasLegislativas": ["LEG:FED LEI:013105 ANO:2015"],
                },
                {"id": "", "nomeOrgaoJulgador": "CORTE ESPECIAL"},
            ]
        )
        # Mês sem lançamentos, com o "}" a mais que o STJ publica.
        malformado = '[ {"id":"", "nomeOrgaoJulgador":"CORTE ESPECIAL"} } ]'
        objeto = self.transformar(
            {"20220531.json": valido, "20220228.json": malformado}
        )
        espelhos = objeto["espelhos"]
        self.assertEqual(objeto["_meta"]["totalEspelhos"], 1)  # o id vazio é ignorado
        self.assertIn(
            "corte-especial/20220228.json",
            objeto["_meta"]["source"]["arquivosMensaisIgnorados"],
        )
        registro = espelhos["000815561"]
        self.assertEqual(registro["dataPublicacao"], "26/05/2022")
        self.assertEqual(registro["teseJuridica"], "Tese do acórdão.")
        self.assertEqual(registro["referenciasLegislativas"], ["LEG:FED LEI:013105 ANO:2015"])
        self.assertEqual(registro["ementa"], "PROCESSUAL CIVIL. Ementa do acórdão.")
        self.assertIn("201900000001", registro["links"]["consultaProcessual"])
        self.assertIn("000815561", registro["links"]["jurisprudencia"])


if __name__ == "__main__":
    unittest.main()
