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


class InstanteUtcTest(unittest.TestCase):
    def test_normaliza_sufixo_z_e_ingenuo(self) -> None:
        com_z = pipeline.instante_utc("2026-01-07T14:45:51.152Z")
        ingenuo = pipeline.instante_utc("2026-07-18T17:13:30")
        self.assertIsNotNone(com_z)
        self.assertIsNotNone(ingenuo)
        assert com_z and ingenuo
        self.assertLess(com_z, ingenuo)
        self.assertIsNone(pipeline.instante_utc("não é data"))


if __name__ == "__main__":
    unittest.main()
