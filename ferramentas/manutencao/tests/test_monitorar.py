from __future__ import annotations

import contextlib
import importlib.util
import io
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
    def preparar(
        self, raiz: Path, gerado_em: str = "2026-01-20"
    ) -> tuple[dict[str, object], Path]:
        publicados = raiz / "publicados"
        publicados.mkdir()
        (publicados / "lei_teste.json").write_text(
            json.dumps({"_meta": {"gerado_em": gerado_em}, "artigos": {}}),
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

    def test_200_com_fonte_anterior_ao_snapshot_e_sem_mudanca(self) -> None:
        # O Planalto ignora o If-Modified-Since e responde 200 com o
        # Last-Modified da republicação em massa de 23/04, anterior ao snapshot
        # de 19/07: o candidato já incorporou esse conteúdo, não é mudança.
        with tempfile.TemporaryDirectory() as temp:
            config, publicados = self.preparar(Path(temp), gerado_em="2026-07-19")
            with patch.object(
                pipeline,
                "sondar_url",
                return_value={
                    "http": 200,
                    "last_modified": "Thu, 23 Apr 2026 23:00:31 GMT",
                },
            ):
                itens = pipeline.monitorar_legislacao(config, publicados)
        self.assertEqual(itens[0]["situacao"], "sem_mudanca")
        self.assertIn("anterior ao snapshot", itens[0]["detalhe"])

    def test_200_sem_last_modified_permanece_conservador(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            config, publicados = self.preparar(Path(temp), gerado_em="2026-07-19")
            with patch.object(
                pipeline,
                "sondar_url",
                return_value={"http": 200, "last_modified": None},
            ):
                itens = pipeline.monitorar_legislacao(config, publicados)
        self.assertEqual(itens[0]["situacao"], "mudou")

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

    def test_cli_aceita_excluir(self) -> None:
        args = pipeline.parser_cli().parse_args(
            ["monitorar", "--excluir", "sumulas_stj,jurisprudencia_teses_stj"]
        )
        self.assertEqual(args.excluir, "sumulas_stj,jurisprudencia_teses_stj")

    def test_relatorio_declara_fontes_excluidas(self) -> None:
        # Fonte pulada nunca some em silêncio: o relatório diz qual e por quê.
        resultado = {
            "verificado_em": "2026-07-22T00:00:00+00:00",
            "mudancas": 0,
            "erros": 0,
            "conjuntos": {
                "legislacao": [
                    {"alvo": "CF", "situacao": "sem_mudanca", "detalhe": "d"}
                ]
            },
            "excluidos": ["jurisprudencia_teses_stj", "sumulas_stj"],
        }
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            pipeline.imprimir_monitoramento(resultado)
        saida = buffer.getvalue()
        self.assertIn("[excluido]", saida)
        self.assertIn("sumulas_stj", saida)
        self.assertIn("jurisprudencia_teses_stj", saida)
        # sem_mudanca continua resumido, não linha a linha
        self.assertNotIn("legislacao/CF", saida)


class RegistroDeVerificacaoTest(unittest.TestCase):
    """O registro responde 'quando isto foi conferido?', não 'quando mudou?'."""

    def resultado(
        self,
        conjuntos: dict[str, list[dict[str, str]]],
        verificado_em: str = "2026-07-29T12:00:00+00:00",
    ) -> dict[str, object]:
        return {"verificado_em": verificado_em, "conjuntos": conjuntos}

    def test_grava_conferido_em_por_conjunto(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            alvo = Path(temp) / "verificacoes.json"
            saida = pipeline.registrar_verificacao(
                self.resultado(
                    {
                        "legislacao": [
                            {"alvo": "CF", "situacao": "sem_mudanca", "detalhe": "d"},
                            {"alvo": "CC", "situacao": "sem_mudanca", "detalhe": "d"},
                        ]
                    }
                ),
                alvo,
            )
        registro = saida["conjuntos"]["legislacao"]
        self.assertEqual(registro["conferido_em"], "2026-07-29T12:00:00+00:00")
        self.assertEqual(registro["situacao"], "sem_mudanca")
        self.assertEqual(registro["fontes"], 2)

    def test_execucao_de_outra_rede_nao_apaga_a_anterior(self) -> None:
        # O monitor da nuvem pula as famílias que exigem rede aceita; elas são
        # conferidas de outro ponto. Substituir o arquivo perderia uma das duas.
        with tempfile.TemporaryDirectory() as temp:
            alvo = Path(temp) / "verificacoes.json"
            pipeline.registrar_verificacao(
                self.resultado(
                    {"legislacao": [{"alvo": "CF", "situacao": "sem_mudanca", "detalhe": "d"}]},
                    "2026-07-27T09:00:00+00:00",
                ),
                alvo,
            )
            saida = pipeline.registrar_verificacao(
                self.resultado(
                    {"sumulas_stf": [{"alvo": "catalogo", "situacao": "sem_mudanca", "detalhe": "d"}]},
                    "2026-07-29T12:00:00+00:00",
                ),
                alvo,
            )
        self.assertEqual(
            saida["conjuntos"]["legislacao"]["conferido_em"], "2026-07-27T09:00:00+00:00"
        )
        self.assertEqual(
            saida["conjuntos"]["sumulas_stf"]["conferido_em"], "2026-07-29T12:00:00+00:00"
        )

    def test_erro_nao_conta_como_conferencia(self) -> None:
        # 403 por IP de datacenter não é conferência: a data antiga permanece, senão
        # o site afirmaria frescor que ninguém verificou.
        with tempfile.TemporaryDirectory() as temp:
            alvo = Path(temp) / "verificacoes.json"
            pipeline.registrar_verificacao(
                self.resultado(
                    {"sumulas_stf": [{"alvo": "catalogo", "situacao": "sem_mudanca", "detalhe": "d"}]},
                    "2026-07-20T09:00:00+00:00",
                ),
                alvo,
            )
            saida = pipeline.registrar_verificacao(
                self.resultado(
                    {"sumulas_stf": [{"alvo": "catalogo", "situacao": "erro", "detalhe": "403"}]},
                    "2026-07-29T12:00:00+00:00",
                ),
                alvo,
            )
        registro = saida["conjuntos"]["sumulas_stf"]
        self.assertEqual(registro["conferido_em"], "2026-07-20T09:00:00+00:00")
        self.assertEqual(registro["situacao"], "erro")
        self.assertEqual(registro["ultimo_erro_em"], "2026-07-29T12:00:00+00:00")

    def test_erro_em_uma_fonte_domina_o_conjunto(self) -> None:
        itens = [
            {"alvo": "CF", "situacao": "sem_mudanca", "detalhe": "d"},
            {"alvo": "CC", "situacao": "erro", "detalhe": "timeout"},
        ]
        self.assertEqual(pipeline.situacao_do_conjunto(itens), "erro")

    def test_mudanca_prevalece_sobre_sem_mudanca(self) -> None:
        itens = [
            {"alvo": "CF", "situacao": "sem_mudanca", "detalhe": "d"},
            {"alvo": "CC", "situacao": "mudou", "detalhe": "d"},
        ]
        self.assertEqual(pipeline.situacao_do_conjunto(itens), "mudou")

    def test_cli_aceita_registrar(self) -> None:
        args = pipeline.parser_cli().parse_args(["monitorar", "--registrar"])
        self.assertTrue(args.registrar)

    def test_cli_aceita_registrar_na_comparacao(self) -> None:
        args = pipeline.parser_cli().parse_args(
            ["comparar", "--execucao", "x", "--registrar"]
        )
        self.assertTrue(args.registrar)

    def test_sinal_nao_apaga_a_recoleta_anterior(self) -> None:
        # Um sinal barato de hoje não pode apagar o registro de que a conferência
        # forte foi feita ontem: elas não valem o mesmo.
        with tempfile.TemporaryDirectory() as temp:
            alvo = Path(temp) / "verificacoes.json"
            pipeline.registrar_verificacao(
                self.resultado(
                    {"sumulas_stf": [{"alvo": "s.json", "situacao": "sem_mudanca", "detalhe": "d"}]},
                    "2026-07-29T20:00:00+00:00",
                ),
                alvo,
                metodo="recoleta",
            )
            saida = pipeline.registrar_verificacao(
                self.resultado(
                    {"sumulas_stf": [{"alvo": "catalogo", "situacao": "sem_mudanca", "detalhe": "d"}]},
                    "2026-08-03T09:00:00+00:00",
                ),
                alvo,
                metodo="sinal",
            )
        registro = saida["conjuntos"]["sumulas_stf"]
        self.assertEqual(registro["conferido_em"], "2026-08-03T09:00:00+00:00")
        self.assertEqual(registro["metodo"], "sinal")
        self.assertEqual(registro["recoletado_em"], "2026-07-29T20:00:00+00:00")

    def test_comparacao_sem_diferenca_e_sem_mudanca(self) -> None:
        relatorio = {
            "gerado_em": "2026-07-29T20:00:00+00:00",
            "conjuntos": {
                "sumulas_stf": [
                    {"arquivo": "sumulas_stf.json", "adicionados": [], "removidos": [], "alterados": []}
                ],
                "jurisprudencia_teses_stj": [
                    {"arquivo": "jt_stj.json", "adicionados": [], "removidos": [], "alterados": ["JT_087_T09"]}
                ],
            },
        }
        resultado = pipeline.resultado_da_comparacao(relatorio)
        self.assertEqual(
            resultado["conjuntos"]["sumulas_stf"][0]["situacao"], "sem_mudanca"
        )
        self.assertEqual(
            resultado["conjuntos"]["jurisprudencia_teses_stj"][0]["situacao"], "mudou"
        )
        self.assertEqual(resultado["verificado_em"], "2026-07-29T20:00:00+00:00")


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


class ExecutarCurlTest(unittest.TestCase):
    def test_preserva_o_motivo_do_curl_na_falha(self) -> None:
        import subprocess

        erro = subprocess.CalledProcessError(
            60,
            ["curl"],
            stderr="curl: (60) SSL certificate problem: unable to get local issuer certificate\n",
        )
        with patch.object(pipeline.subprocess, "run", side_effect=erro):
            with self.assertRaises(RuntimeError) as capturado:
                pipeline.executar_curl(["curl", "https://exemplo"])
        mensagem = str(capturado.exception)
        self.assertIn("60", mensagem)
        self.assertIn("SSL certificate problem", mensagem)


class DataCondicionalTest(unittest.TestCase):
    def test_data_iso_nua_vira_data_http(self) -> None:
        http = pipeline.data_http("2026-07-19")
        assert http is not None
        self.assertTrue(http.endswith("GMT"))
        self.assertNotEqual(http, "2026-07-19")
        self.assertEqual(
            pipeline.para_instante(http), pipeline.para_instante("2026-07-19")
        )

    def test_data_http_e_preservada_no_instante(self) -> None:
        original = "Wed, 08 Jul 2026 02:05:19 GMT"
        self.assertEqual(
            pipeline.para_instante(pipeline.data_http(original)),
            pipeline.para_instante(original),
        )

    def test_vazio_e_none(self) -> None:
        self.assertIsNone(pipeline.data_http(None))
        self.assertIsNone(pipeline.data_http(""))

    def test_para_instante_le_iso_e_http(self) -> None:
        self.assertIsNotNone(pipeline.para_instante("2026-07-19"))
        self.assertIsNotNone(
            pipeline.para_instante("Wed, 08 Jul 2026 02:05:19 GMT")
        )
        self.assertIsNone(pipeline.para_instante("não é data"))

    def test_fonte_nao_e_mais_nova(self) -> None:
        self.assertTrue(
            pipeline.fonte_nao_e_mais_nova(
                "Thu, 23 Apr 2026 23:00:31 GMT", "2026-07-19"
            )
        )
        self.assertFalse(
            pipeline.fonte_nao_e_mais_nova(
                "Thu, 02 Jul 2026 10:22:29 GMT", "2026-01-20"
            )
        )
        self.assertFalse(pipeline.fonte_nao_e_mais_nova(None, "2026-07-19"))
        self.assertFalse(
            pipeline.fonte_nao_e_mais_nova(
                "Thu, 23 Apr 2026 23:00:31 GMT", "não é data"
            )
        )


class MonitorarTemasRGTest(unittest.TestCase):
    URL = "https://portal.stf.jus.br/jurisprudenciaRepercussao/exportarDados.asp"

    def tabela(self, situacoes: dict[int, str]) -> str:
        ths = "".join(f"<th>{c}</th>" for c in pipeline.COLUNAS_TEMAS_RG)
        linhas = ""
        for numero, situacao in situacoes.items():
            tds = [""] * len(pipeline.COLUNAS_TEMAS_RG)
            tds[0] = str(numero)
            tds[3] = "" if numero in (self.sem_titulo or ()) else f"Tema {numero}"
            tds[11] = situacao
            linhas += "<tr>" + "".join(f"<td>{v}</td>" for v in tds) + "</tr>"
        return (
            f"<html><body><table><thead><tr>{ths}</tr></thead>"
            f"<tbody>{linhas}</tbody></table></body></html>"
        )

    sem_titulo: tuple[int, ...] = ()

    def monitorar(
        self,
        fonte: dict[int, str],
        snapshot: dict[str, str],
        omitidos: dict[str, str] | None = None,
        sem_titulo: tuple[int, ...] = (),
    ):
        self.sem_titulo = sem_titulo
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
                        "_meta": {
                            "excluidosPorLacunaDaFonte": [
                                {"numero": int(chave), "situacao": situacao}
                                for chave, situacao in (omitidos or {}).items()
                            ]
                        },
                        "temas": {
                            chave: {"situacao": situacao}
                            for chave, situacao in snapshot.items()
                        },
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

    def test_tema_omitido_por_lacuna_da_fonte_conta_no_total(self) -> None:
        # BASE-048: o tema sem título continua na fonte, mas fora da coleção.
        # Sem descontá-lo, o monitor acusaria "mudou" toda semana só por ele.
        itens = self.monitorar(
            {1: "Trânsito em Julgado", 2: "Em julgamento"},
            {"1": "Trânsito em Julgado"},
            omitidos={"2": "Em julgamento"},
            sem_titulo=(2,),
        )
        self.assertEqual(itens[0]["situacao"], "sem_mudanca")

    def test_tema_omitido_que_ganhou_titulo_na_fonte_indica_mudanca(self) -> None:
        # Quando o STF preenche o título, é hora de recoletar e promover.
        itens = self.monitorar(
            {1: "Trânsito em Julgado", 2: "Em julgamento"},
            {"1": "Trânsito em Julgado"},
            omitidos={"2": "Em julgamento"},
            sem_titulo=(),
        )
        self.assertEqual(itens[0]["situacao"], "mudou")
        self.assertIn("ganharam título na fonte: 2", itens[0]["detalhe"])


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

    def test_200_com_planilha_anterior_permanece_sem_mudanca(self) -> None:
        itens = self.monitorar(
            {"http": 200, "last_modified": "Wed, 01 Jul 2026 00:00:00 GMT"}
        )
        self.assertEqual(itens[0]["situacao"], "sem_mudanca")


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


class RedacaoCompiladaTest(unittest.TestCase):
    """Lei compilada: redação anterior e vigente, ambas sem tachado."""

    def transformar(self, corpo: str) -> dict:
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            bruto, publicados, candidatos = raiz / "bruto", raiz / "pub", raiz / "cand"
            for pasta in (bruto, publicados, candidatos):
                pasta.mkdir()
            (bruto / "teste.html").write_text(
                f"<html><body>{corpo}</body></html>", encoding="utf-8"
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
                    }
                ]
            }
            saidas = pipeline.transformar_legislacao(
                config, bruto, publicados, candidatos
            )
            return json.loads(saidas[0].read_text(encoding="utf-8"))["artigos"]

    def test_vale_a_ultima_redacao_ativa_com_seus_paragrafos(self) -> None:
        # Padrão do art. 24 do Estatuto da OAB: a redação anterior não vem
        # riscada, e os parágrafos pertencem à redação vigente (a segunda).
        artigos = self.transformar(
            "<p>Art. 24. A decisão judicial que fixar honorários.</p>"
            "<p>Art. 24. O ato judicial que fixar honorários. "
            "(Redação dada pela Lei nº 14.365, de 2022)</p>"
            "<p>&#167; 1º A execução dos honorários pode ser promovida nos autos.</p>"
            "<p>&#167; 2º Os sucessores recebem os honorários proporcionais.</p>"
            "<p>Art. 25. Prescreve em cinco anos.</p>"
        )
        texto = artigos["24"]["texto"]
        self.assertIn("O ato judicial", texto)
        self.assertNotIn("A decisão judicial", texto)
        self.assertIn("§ 1º A execução", texto)
        self.assertIn("§ 2º Os sucessores", texto)

    def test_riscada_nao_substitui_a_vigente_ja_registrada(self) -> None:
        artigos = self.transformar(
            "<p>Art. 5º Texto vigente.</p>"
            "<p>&#167; 1º Parágrafo do vigente.</p>"
            '<p style="text-decoration: line-through">Art. 5º Texto revogado.</p>'
            "<p>Art. 6º Outro artigo.</p>"
        )
        self.assertIn("Texto vigente", artigos["5"]["texto"])
        self.assertNotIn("revogado", artigos["5"]["texto"])
        self.assertIn("§ 1º Parágrafo do vigente", artigos["5"]["texto"])

    def test_paragrafo_riscado_dentro_do_p_fica_fora_do_artigo(self) -> None:
        # Padrão do art. 26 da Lei 9.514 (issue #26, BASE-050): o <strike> abre
        # dentro do <p>, depois da âncora, e a redação anterior entrava no
        # artigo como texto comum, antes da vigente.
        artigos = self.transformar(
            '<p><font><a name="art26"></a><strike>Art. 26. Vencida e não paga, '
            "no todo ou em parte, a dívida.</strike></font></p>"
            '<p><span><a name="art26.0"></a><font>Art. 26. Vencida e não paga a '
            "dívida, no todo ou em parte, e constituídos em mora o devedor.</font> "
            '<a href="L14711.htm#art2">(Redação dada pela Lei nº 14.711, de 2023)'
            "</a></span></p>"
            '<p><font><a name="art26§2"></a><strike>§ 2º O contrato definirá o '
            "prazo de carência após o qual será expedida a intimação.</strike>"
            "</font></p>"
            '<p><font><a name="art26§2.0"></a>§ 2º O contrato poderá estabelecer '
            "o prazo de carência, após o qual será expedida a intimação. "
            "(Redação dada pela Lei nº 14.711, de 2023)</font></p>"
            "<p>Art. 27. Seguinte.</p>"
        )
        texto = artigos["26"]["texto"]
        self.assertIn("constituídos em mora o devedor", texto)
        self.assertNotIn("no todo ou em parte, a dívida.", texto)
        self.assertIn("poderá estabelecer", texto)
        self.assertNotIn("definirá", texto)
        self.assertEqual(texto.count("§ 2º"), 1)
        self.assertNotIn("27", artigos["26"]["texto"])

    def test_inciso_riscado_sob_caput_vigente_fica_fora(self) -> None:
        # Lei 8.009, art. 3º, III: o caput não mudou; só o inciso traz a
        # redação anterior riscada e, logo abaixo, a vigente.
        artigos = self.transformar(
            "<p>Art. 3º A impenhorabilidade é oponível em qualquer processo:</p>"
            "<p>I - em razão dos créditos de trabalhadores.</p>"
            '<p><font><a name="art3iii"></a><strike>III -- pelo credor de pensão '
            "alimentícia;</strike></font></p>"
            "<p>III - pelo credor da pensão alimentícia, resguardados os direitos. "
            "(Redação dada pela Lei nº 13.144 de 2015)</p>"
            "<p>Art. 4º Seguinte.</p>"
        )
        texto = artigos["3"]["texto"]
        self.assertIn("I - em razão", texto)
        self.assertIn("resguardados os direitos", texto)
        self.assertNotIn("III -- pelo credor", texto)

    def test_artigo_inteiro_riscado_sem_substituto_mantem_os_paragrafos(self) -> None:
        # Art. 7º da Lei 9.514 (revogado): tudo riscado e nenhuma redação nova.
        # O artigo fica retido com os seus parágrafos, como já era.
        artigos = self.transformar(
            "<p><strike>Art. 7º O CRI terá as seguintes características:</strike></p>"
            "<p><strike>I - nome da companhia emitente;</strike> "
            "(Revogado pela Lei nº 14.430, de 2022)</p>"
            "<p><strike>II - número de ordem.</strike></p>"
            "<p>Art. 8º Seguinte.</p>"
        )
        texto = artigos["7"]["texto"]
        self.assertIn("I - nome da companhia", texto)
        self.assertIn("II - número de ordem", texto)

    def test_riscado_com_anotacao_fora_da_marca_e_preservado(self) -> None:
        # Estatuto da OAB, art. 7º, I: texto riscado por decisão em ADI, com a
        # anotação "(Vide ADIN ...)" fora da marca. A anotação é informação da
        # fonte sobre o dispositivo; o parágrafo fica, com ela.
        artigos = self.transformar(
            "<p>Art. 7º Ao advogado é assegurado:</p>"
            "<p><strike>I - a postulação a qualquer órgão do Poder Judiciário;"
            "</strike> (Vide ADIN 1.127-8)</p>"
            "<p>II - a inviolabilidade de seu escritório.</p>"
            "<p>Art. 8º Seguinte.</p>"
        )
        texto = artigos["7"]["texto"]
        self.assertIn("I - a postulação", texto)
        self.assertIn("(Vide ADIN 1.127-8)", texto)
        self.assertIn("II - a inviolabilidade", texto)


    def test_rotulo_repetido_sem_marca_nao_apaga_o_artigo(self) -> None:
        # Defeito tipográfico da LGPD: "Art. 5 7." é o art. 57, mas casa como 5º.
        # Sem o rótulo de nova redação, não pode substituir o artigo real.
        artigos = self.transformar(
            "<p>Art. 5º Para os fins desta Lei, considera-se:</p>"
            "<p>I - dado pessoal: informação relacionada a pessoa identificada;</p>"
            "<p>Art. 6º Outro artigo.</p>"
            "<p>Art. 5 7. (VETADO).</p>"
        )
        self.assertIn("Para os fins desta Lei", artigos["5"]["texto"])
        self.assertNotIn("VETADO", artigos["5"]["texto"])
        self.assertIn("I - dado pessoal", artigos["5"]["texto"])

    def test_nova_redacao_menor_nao_engole_o_artigo(self) -> None:
        # Estatuto da Terra art. 37 / Lei do Petróleo art. 68-C: a reedição do
        # caput vem marcada, mas é curta; aceitá-la descartaria o corpo do artigo.
        artigos = self.transformar(
            "<p>Art. 37. São órgãos específicos para a execução da Reforma "
            "Agrária: I - o Instituto; II - a Superintendência; III - o Conselho; "
            "IV - a Comissão; V - o Grupo Executivo.</p>"
            "<p>Art. 37. São órgãos específicos. "
            "(Redação dada pela Lei nº 6.431, de 1977)</p>"
            "<p>Art. 38. Seguinte.</p>"
        )
        self.assertIn("o Instituto", artigos["37"]["texto"])
        self.assertIn("V - o Grupo Executivo", artigos["37"]["texto"])


if __name__ == "__main__":
    unittest.main()
