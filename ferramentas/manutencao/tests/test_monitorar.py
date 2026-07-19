from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
MODULO_PATH = ROOT / "ferramentas" / "manutencao" / "atualizar_base_juridica.py"
SPEC = importlib.util.spec_from_file_location("atualizar_base_juridica_monitor", MODULO_PATH)
assert SPEC and SPEC.loader
pipeline = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pipeline
SPEC.loader.exec_module(pipeline)


def fabricar_baixar(conteudos: dict[str, str]):
    def falso_baixar(url: str, destino: Path) -> dict[str, object]:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(conteudos[url], encoding="utf-8")
        return {"url": url, "arquivo": str(destino)}

    return falso_baixar


class MonitorarLegislacaoTest(unittest.TestCase):
    def preparar(self, raiz: Path) -> tuple[dict[str, object], Path]:
        publicados = raiz / "publicados"
        publicados.mkdir()
        (publicados / "lei_teste.json").write_text(
            json.dumps({"_meta": {"gerado_em": "2026-01-20"}, "artigos": {}}),
            encoding="utf-8",
        )
        config = {
            "fontes": [
                {
                    "id": "teste",
                    "codigo": "TESTE",
                    "url": "https://www.planalto.gov.br/ccivil_03/teste.htm",
                    "destino": "lei_teste.json",
                }
            ]
        }
        return config, publicados

    def test_304_significa_sem_mudanca(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            config, publicados = self.preparar(Path(temp))
            with patch.object(
                pipeline,
                "sondar_url",
                return_value={"http": 304, "last_modified": None},
            ) as sonda:
                itens = pipeline.monitorar_legislacao(config, publicados)
        sonda.assert_called_once_with(
            "https://www.planalto.gov.br/ccivil_03/teste.htm", desde="2026-01-20"
        )
        self.assertEqual(itens[0]["situacao"], "sem_mudanca")

    def test_200_significa_mudanca(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            config, publicados = self.preparar(Path(temp))
            with patch.object(
                pipeline,
                "sondar_url",
                return_value={
                    "http": 200,
                    "last_modified": "Thu, 02 Jul 2026 10:22:29 GMT",
                },
            ):
                itens = pipeline.monitorar_legislacao(config, publicados)
        self.assertEqual(itens[0]["situacao"], "mudou")
        self.assertIn("2026-01-20", itens[0]["detalhe"])

    def test_arquivo_publicado_ausente_e_indeterminado(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            config, publicados = self.preparar(Path(temp))
            (publicados / "lei_teste.json").unlink()
            itens = pipeline.monitorar_legislacao(config, publicados)
        self.assertEqual(itens[0]["situacao"], "indeterminado")


class MonitorarSumulasTest(unittest.TestCase):
    def test_contagem_do_catalogo_stj(self) -> None:
        html = (
            '<div class="gridSumula"><span class="numeroSumula">1</span>'
            '<div class="blocoVerbete">a</div></div>'
            '<div class="gridSumula"><span class="numeroSumula">2</span>'
            '<div class="blocoVerbete">b</div></div>'
            '<div class="gridSumula"><span class="numeroSumula">3</span></div>'
        )
        with tempfile.TemporaryDirectory() as temp:
            caminho = Path(temp) / "catalogo.html"
            caminho.write_text(html, encoding="utf-8")
            self.assertEqual(pipeline.contar_catalogo_sumulas_stj(caminho), 2)

    def test_stf_detecta_mudanca_de_estado(self) -> None:
        url = "https://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp?base=30"
        catalogo = (
            '<div class="sumula-item">'
            '<a href="sumariosumulas.asp?base=30&sumula=101">Súmula 1</a></div>'
            '<div class="sumula-item">'
            '<a href="sumariosumulas.asp?base=30&sumula=102">Súmula 2 cancelada</a>'
            "</div>"
        )
        config = {
            "adaptador": "sumulas_stf_html_v1",
            "chave_colecao": "sumulas",
            "destino": "sumulas_stf.json",
            "fontes": [{"id": "catalogo", "url": url, "arquivo_bruto": "catalogo.html"}],
        }
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            publicados = raiz / "publicados"
            publicados.mkdir()
            (publicados / "sumulas_stf.json").write_text(
                json.dumps(
                    {"sumulas": {"1": {"status": "ativa"}, "2": {"status": "ativa"}}}
                ),
                encoding="utf-8",
            )
            with patch.object(
                pipeline, "baixar", side_effect=fabricar_baixar({url: catalogo})
            ):
                itens = pipeline.monitorar_sumulas_stf(
                    config, publicados, raiz / "temp"
                )
        self.assertEqual(itens[0]["situacao"], "mudou")
        self.assertIn("canceladas", itens[0]["detalhe"])

    def test_catalogo_stf_mapeia_revogada_para_cancelada(self) -> None:
        catalogo = (
            '<div class="sumula-item">'
            '<a href="sumariosumulas.asp?base=30&sumula=2442">'
            "Súmula 152 <em>(revogada)</em></a></div>"
        )
        itens = pipeline.extrair_catalogo_stf(catalogo, False)
        self.assertEqual(itens[0]["numero"], 152)
        self.assertEqual(itens[0]["status"], "cancelada")

    def test_jt_compara_edicao_mais_recente(self) -> None:
        url = "https://processo.stj.jus.br/SCON/jt/jt.jsp"
        indice = (
            '<span class="numeroSumula">271</span>'
            '<a data-edicao="271">Baixar PDF</a>'
        )
        config = {
            "adaptador": "jt_stj_html_v1",
            "chave_colecao": "teses",
            "destino": "jt_stj.json",
            "fontes": [{"id": "indice", "url": url, "arquivo_bruto": "indice.html"}],
        }
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            publicados = raiz / "publicados"
            publicados.mkdir()
            (publicados / "jt_stj.json").write_text(
                json.dumps({"teses": {"JT_269_T1": {"edicao": 269}}}),
                encoding="utf-8",
            )
            with patch.object(
                pipeline, "baixar", side_effect=fabricar_baixar({url: indice})
            ):
                itens = pipeline.monitorar_jt(config, publicados, raiz / "temp")
        self.assertEqual(itens[0]["situacao"], "mudou")
        self.assertIn("271", itens[0]["detalhe"])


class MonitorarTemasTest(unittest.TestCase):
    def test_ckan_mais_novo_que_snapshot_e_mudanca(self) -> None:
        url = "https://dadosabertos.web.stj.jus.br/api/3/action/package_show?id=x"
        metadados = json.dumps(
            {
                "result": {
                    "resources": [
                        {"name": "Temas.csv", "last_modified": "2026-07-18T17:13:30"},
                        {"name": "dicionario.csv", "last_modified": "2022-07-11T22:40:56"},
                    ]
                }
            }
        )
        config = {
            "adaptador": "temas_stj_csv_v1",
            "chave_colecao": "temas",
            "destino": "flash_temas_stj.json",
            "fontes": [
                {"id": "metadados", "url": url, "arquivo_bruto": "metadados.json"}
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            publicados = raiz / "publicados"
            publicados.mkdir()
            (publicados / "flash_temas_stj.json").write_text(
                json.dumps(
                    {
                        "_meta": {"generatedAt": "2026-01-07T14:45:51.152Z"},
                        "temas": {},
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(
                pipeline, "baixar", side_effect=fabricar_baixar({url: metadados})
            ):
                itens = pipeline.monitorar_temas(config, publicados, raiz / "temp")
        self.assertEqual(itens[0]["situacao"], "mudou")
        self.assertIn("Temas.csv", itens[0]["detalhe"])


class MonitorarConjuntosTest(unittest.TestCase):
    def test_erro_de_coleta_nao_interrompe_o_monitor(self) -> None:
        dados = {
            "conjuntos": {
                "sumulas_stj": {
                    "adaptador": "sumulas_stj_html_v1",
                    "chave_colecao": "sumulas",
                    "destino": "sumulas_stj.json",
                    "fontes": [
                        {
                            "id": "catalogo",
                            "url": "https://processo.stj.jus.br/SCON/x",
                            "arquivo_bruto": "catalogo.html",
                        }
                    ],
                }
            }
        }
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(
                pipeline, "baixar", side_effect=RuntimeError("fonte indisponível")
            ):
                resultado = pipeline.monitorar_conjuntos(
                    dados, ["sumulas_stj"], Path(temp)
                )
        self.assertEqual(resultado["erros"], 1)
        self.assertFalse(resultado["mudancas_detectadas"])
        self.assertEqual(
            resultado["conjuntos"]["sumulas_stj"][0]["situacao"], "erro"
        )

    def test_cli_aceita_monitorar_sem_execucao(self) -> None:
        args = pipeline.parser_cli().parse_args(["monitorar", "--json"])
        self.assertEqual(args.acao, "monitorar")
        self.assertTrue(args.json)
        self.assertFalse(hasattr(args, "execucao"))


class ArvoreHTMLTest(unittest.TestCase):
    def test_fechamento_orfao_de_inline_nao_derruba_o_paragrafo(self) -> None:
        html = (
            "<font><p>Art. 1º Início do artigo. </font>"
            "<font>Continuação após tag órfã.</font></p></font>"
        )
        arvore = pipeline.analisar_html(html)
        paragrafos = list(pipeline.buscar(arvore, tag="p"))
        self.assertEqual(len(paragrafos), 1)
        texto = pipeline.texto_elemento(paragrafos[0])
        self.assertIn("Continuação após tag órfã", texto)

    def test_paragrafo_sem_fechamento_nao_engole_o_seguinte(self) -> None:
        html = "<p>§ 3º Texto do parágrafo.<p>Art. 2º Seguinte.</p>"
        arvore = pipeline.analisar_html(html)
        textos = [
            pipeline.texto_elemento(no) for no in pipeline.buscar(arvore, tag="p")
        ]
        self.assertEqual(textos, ["§ 3º Texto do parágrafo.", "Art. 2º Seguinte."])

    def test_fechamento_de_bloco_continua_funcionando(self) -> None:
        html = "<div><p>um</p><p>dois</p></div><p>três</p>"
        arvore = pipeline.analisar_html(html)
        textos = [
            pipeline.texto_elemento(no) for no in pipeline.buscar(arvore, tag="p")
        ]
        self.assertEqual(textos, ["um", "dois", "três"])


class TransformarLegislacaoIndicesTest(unittest.TestCase):
    def test_preserva_o_indice_invertido_publicado(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto"
            publicados = raiz / "publicados"
            candidatos = raiz / "candidatos"
            for pasta in (bruto, publicados, candidatos):
                pasta.mkdir()
            (bruto / "teste.html").write_text(
                "<html><body><p>Art. 1º Texto do artigo.</p></body></html>",
                encoding="utf-8",
            )
            indice = {"keywords": {"texto": ["1"]}}
            (publicados / "lei_teste.json").write_text(
                json.dumps(
                    {
                        "_meta": {},
                        "artigos": {
                            "1": {
                                "numero": "1",
                                "texto": "Texto antigo",
                                "url": "https://www.planalto.gov.br/x.htm",
                                "keywords": ["texto"],
                            }
                        },
                        "indexes": indice,
                    }
                ),
                encoding="utf-8",
            )
            config = {
                "fontes": [
                    {
                        "codigo": "TESTE",
                        "url": "https://www.planalto.gov.br/x.htm",
                        "arquivo_bruto": "teste.html",
                        "destino": "lei_teste.json",
                    }
                ]
            }
            saidas = pipeline.transformar_legislacao(
                config, bruto, publicados, candidatos
            )
            objeto = json.loads(saidas[0].read_text(encoding="utf-8"))
        self.assertEqual(objeto.get("indexes"), indice)
        self.assertEqual(objeto["artigos"]["1"]["keywords"], ["texto"])


class TransformarLegislacaoInicioAposTest(unittest.TestCase):
    def test_corpo_anexado_prevalece_sobre_o_decreto_de_promulgacao(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto"
            publicados = raiz / "publicados"
            candidatos = raiz / "candidatos"
            for pasta in (bruto, publicados, candidatos):
                pasta.mkdir()
            (bruto / "teste.html").write_text(
                "<html><body>"
                "<p>Art. 1º Fica aprovada a Consolidação anexa.</p>"
                "<p>Art. 2º Este decreto-lei entrará em vigor.</p>"
                "<p>CONSOLIDAÇÃO DAS LEIS DO TRABALHO</p>"
                "<p>Art. 1º Esta Consolidação estatui as normas.</p>"
                "<p>Art. 2º Considera-se empregador a empresa.</p>"
                "</body></html>",
                encoding="utf-8",
            )
            (publicados / "lei_teste.json").write_text(
                json.dumps({"_meta": {}, "artigos": {}}), encoding="utf-8"
            )
            config = {
                "fontes": [
                    {
                        "codigo": "TESTE",
                        "url": "https://www.planalto.gov.br/x.htm",
                        "arquivo_bruto": "teste.html",
                        "destino": "lei_teste.json",
                        "inicio_apos": "CONSOLIDAÇÃO DAS LEIS DO TRABALHO",
                    }
                ]
            }
            saidas = pipeline.transformar_legislacao(
                config, bruto, publicados, candidatos
            )
            artigos = json.loads(saidas[0].read_text(encoding="utf-8"))["artigos"]
        self.assertIn("Esta Consolidação estatui", artigos["1"]["texto"])
        self.assertIn("Considera-se empregador", artigos["2"]["texto"])

    def test_marcador_ausente_encerra_a_transformacao(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto"
            publicados = raiz / "publicados"
            candidatos = raiz / "candidatos"
            for pasta in (bruto, publicados, candidatos):
                pasta.mkdir()
            (bruto / "teste.html").write_text(
                "<html><body><p>Art. 1º Texto.</p></body></html>", encoding="utf-8"
            )
            (publicados / "lei_teste.json").write_text(
                json.dumps({"_meta": {}, "artigos": {}}), encoding="utf-8"
            )
            config = {
                "fontes": [
                    {
                        "codigo": "TESTE",
                        "url": "https://www.planalto.gov.br/x.htm",
                        "arquivo_bruto": "teste.html",
                        "destino": "lei_teste.json",
                        "inicio_apos": "MARCADOR INEXISTENTE",
                    }
                ]
            }
            with self.assertRaises(ValueError):
                pipeline.transformar_legislacao(
                    config, bruto, publicados, candidatos
                )


class TransformarTemasIndicesTest(unittest.TestCase):
    def test_preserva_keywords_e_terms_publicados(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto = raiz / "bruto"
            publicados = raiz / "publicados"
            candidatos = raiz / "candidatos"
            for pasta in (bruto, publicados, candidatos):
                pasta.mkdir()
            (bruto / "temas.csv").write_text(
                "tipoPrecedente,numeroPrecedente,sequencialPrecedente,situacao,"
                "assunto,questaoSubmetidaAJulgamento,teseFirmada,orgaoJulgador,"
                "dataPrimeiraAfetacao,dataJulgamento\n"
                "Tema,1,10,Afetado,Direito Civil,Questão de teste,,S2,,\n",
                encoding="utf-8",
            )
            (bruto / "processos.csv").write_text(
                "tipoPrecedente,sequencialPrecedente,leadingCase,ministroRelator\n"
                "Tema,10,S,MINISTRO TESTE\n",
                encoding="utf-8",
            )
            indice = {"teste": [1]}
            (publicados / "flash_teste.json").write_text(
                json.dumps(
                    {"_meta": {}, "temas": {}, "keywords": indice, "terms": indice}
                ),
                encoding="utf-8",
            )
            config = {
                "destino": "flash_teste.json",
                "package_id": "x",
                "join_key": "sequencialPrecedente",
                "fontes": [
                    {"id": "metadados", "url": "https://dadosabertos.web.stj.jus.br/x"},
                    {"id": "temas", "url": "https://dadosabertos.web.stj.jus.br/t", "resource_id": "a"},
                    {"id": "processos", "url": "https://dadosabertos.web.stj.jus.br/p", "resource_id": "b"},
                ],
            }
            saidas = pipeline.transformar_temas(
                config, bruto, publicados, candidatos
            )
            objeto = json.loads(saidas[0].read_text(encoding="utf-8"))
        self.assertEqual(objeto["keywords"], indice)
        self.assertEqual(objeto["terms"], indice)
        self.assertIn("1", objeto["temas"])


class TransformarJtRetencaoTest(unittest.TestCase):
    def test_edicao_sem_correspondencia_na_coleta_e_retida(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            edicoes = raiz / "bruto" / "edicoes"
            publicados = raiz / "publicados"
            candidatos = raiz / "candidatos"
            edicoes.mkdir(parents=True)
            publicados.mkdir()
            candidatos.mkdir()
            (edicoes / "1.html").write_text(
                '<div class="gridEdicaoJT">'
                '<span class="clsVerbete">EDIÇÃO N. 1: TESTE</span>'
                '<span class="clsData">01/01/2020</span></div>'
                '<div class="clsTemasJT redacaoAtual">'
                '<a class="clsSubmitPesquisaTema">1) Enunciado extraído.</a>'
                "</div>",
                encoding="utf-8",
            )
            tese_retida = {
                "id": "JT_002_T01",
                "edicao": "2",
                "edicao_titulo": "Edição antiga",
                "tese_numero": "1",
                "ramo_direito": "Direito Penal",
                "enunciado": "Enunciado preservado.",
                "rito_especial": "False",
                "data_publicacao": "2014-01-01",
                "url": "https://scon.stj.jus.br/SCON/x",
                "qtd_julgados": "3",
            }
            (publicados / "jt_teste.json").write_text(
                json.dumps({"_meta": {}, "teses": {"JT_002_T01": tese_retida}}),
                encoding="utf-8",
            )
            config = {"destino": "jt_teste.json"}
            saidas = pipeline.transformar_jt(
                config, raiz / "bruto", publicados, candidatos
            )
            objeto = json.loads(saidas[0].read_text(encoding="utf-8"))
        self.assertIn("JT_001_T01", objeto["teses"])
        self.assertEqual(objeto["teses"]["JT_002_T01"], tese_retida)
        self.assertEqual(
            objeto["_meta"]["edicoes_retidas_sem_correspondencia"], [2]
        )
        self.assertEqual(objeto["_meta"]["total_edicoes"], 2)


class InstanteUtcTest(unittest.TestCase):
    def test_normaliza_sufixo_z_e_ingenuo(self) -> None:
        com_z = pipeline.instante_utc("2026-01-07T14:45:51.152Z")
        ingenuo = pipeline.instante_utc("2026-07-18T17:13:30")
        self.assertIsNotNone(com_z)
        self.assertIsNotNone(ingenuo)
        assert com_z and ingenuo
        self.assertLess(com_z, ingenuo)
        self.assertIsNone(pipeline.instante_utc("não é data"))


class MonitorarTemasRGTest(unittest.TestCase):
    URL = "https://portal.stf.jus.br/jurisprudenciaRepercussao/exportarDados.asp"

    def tabela(self, situacoes: dict[int, str]) -> str:
        ths = "".join(f"<th>{c}</th>" for c in pipeline.COLUNAS_TEMAS_RG)
        linhas = ""
        for numero, situacao in situacoes.items():
            tds = [""] * len(pipeline.COLUNAS_TEMAS_RG)
            tds[0] = str(numero)
            tds[11] = situacao
            linhas += "<tr>" + "".join(f"<td>{v}</td>" for v in tds) + "</tr>"
        return (
            f"<html><body><table><thead><tr>{ths}</tr></thead>"
            f"<tbody>{linhas}</tbody></table></body></html>"
        )

    def monitorar(self, fonte: dict[int, str], snapshot: dict[str, str]):
        config = {
            "adaptador": "temas_rg_stf_html_v1",
            "chave_colecao": "temas",
            "destino": "temas_rg_stf.json",
            "fontes": [{"id": "exportar", "url": self.URL, "arquivo_bruto": "x.xls"}],
        }
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            publicados = raiz / "publicados"
            publicados.mkdir()
            (publicados / "temas_rg_stf.json").write_text(
                json.dumps(
                    {
                        "temas": {
                            chave: {"situacao": situacao}
                            for chave, situacao in snapshot.items()
                        }
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(
                pipeline,
                "baixar",
                side_effect=fabricar_baixar({self.URL: self.tabela(fonte)}),
            ):
                return pipeline.monitorar_temas_rg(config, publicados, raiz / "temp")

    def test_situacao_divergente_indica_mudanca(self) -> None:
        itens = self.monitorar(
            {1: "Trânsito em Julgado", 2: "Cancelado"},
            {"1": "Trânsito em Julgado", "2": "Trânsito em Julgado"},
        )
        self.assertEqual(itens[0]["situacao"], "mudou")
        self.assertIn("Cancelado", itens[0]["detalhe"])

    def test_contagem_e_situacoes_iguais_sem_mudanca(self) -> None:
        itens = self.monitorar(
            {1: "Trânsito em Julgado", 2: "Trânsito em Julgado"},
            {"1": "Trânsito em Julgado", "2": "Trânsito em Julgado"},
        )
        self.assertEqual(itens[0]["situacao"], "sem_mudanca")


class MonitorarInformativoTest(unittest.TestCase):
    URL = "https://www.stf.jus.br/arquivo/cms/informativoSTF/anexo/Informativo_Dados/Dados_InformativosSTF.xlsx"

    def monitorar(self, resposta: dict[str, object]):
        config = {
            "adaptador": "informativo_stf_xlsx_v1",
            "chave_colecao": "informativos",
            "destino": "informativo_stf.json",
            "fontes": [{"id": "planilha", "url": self.URL, "arquivo_bruto": "x.xlsx"}],
        }
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            publicados = raiz / "publicados"
            publicados.mkdir()
            (publicados / "informativo_stf.json").write_text(
                json.dumps(
                    {
                        "_meta": {
                            "source": {"lastModified": "Wed, 08 Jul 2026 02:05:19 GMT"}
                        },
                        "informativos": {},
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(pipeline, "sondar_url", return_value=resposta):
                return pipeline.monitorar_informativo(config, publicados, raiz / "t")

    def test_304_sem_mudanca(self) -> None:
        itens = self.monitorar({"http": 304, "last_modified": None})
        self.assertEqual(itens[0]["situacao"], "sem_mudanca")

    def test_200_indica_mudanca(self) -> None:
        itens = self.monitorar(
            {"http": 200, "last_modified": "Fri, 18 Jul 2026 00:00:00 GMT"}
        )
        self.assertEqual(itens[0]["situacao"], "mudou")
        self.assertIn("18 Jul 2026", itens[0]["detalhe"])


class MonitorarEspelhosTest(unittest.TestCase):
    URL = "https://dadosabertos.web.stj.jus.br/api/3/action/package_show?id=espelhos-de-acordaos-corte-especial"

    def monitorar(self, modificado_ckan: str, modificado_snapshot: str):
        config = {
            "adaptador": "espelhos_stj_ckan_v1",
            "chave_colecao": "espelhos",
            "destino": "espelhos_stj.json",
            "fontes": [
                {"id": "corte-especial", "url": self.URL, "arquivo_bruto": "x.json"}
            ],
        }
        pacote = json.dumps({"result": {"metadata_modified": modificado_ckan}})
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            publicados = raiz / "publicados"
            publicados.mkdir()
            (publicados / "espelhos_stj.json").write_text(
                json.dumps(
                    {
                        "_meta": {
                            "source": {
                                "officialPublicReference": {
                                    "packages": {
                                        "corte-especial": {
                                            "metadata_modified": modificado_snapshot
                                        }
                                    }
                                }
                            }
                        },
                        "espelhos": {},
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(
                pipeline, "baixar", side_effect=fabricar_baixar({self.URL: pacote})
            ):
                return pipeline.monitorar_espelhos(config, publicados, raiz / "t")

    def test_ckan_mais_novo_indica_mudanca(self) -> None:
        itens = self.monitorar("2026-07-10T00:00:00", "2026-06-09T00:00:00")
        self.assertEqual(itens[0]["situacao"], "mudou")

    def test_ckan_igual_sem_mudanca(self) -> None:
        itens = self.monitorar("2026-06-09T00:00:00", "2026-06-09T00:00:00")
        self.assertEqual(itens[0]["situacao"], "sem_mudanca")


if __name__ == "__main__":
    unittest.main()
