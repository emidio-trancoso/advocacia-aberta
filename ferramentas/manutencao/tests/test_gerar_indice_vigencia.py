from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
MODULO_PATH = ROOT / "ferramentas" / "manutencao" / "gerar_indice_vigencia.py"
SPEC = importlib.util.spec_from_file_location("gerar_indice_vigencia", MODULO_PATH)
assert SPEC and SPEC.loader
gerador = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gerador
SPEC.loader.exec_module(gerador)


class ExtracaoDaAnotacaoTest(unittest.TestCase):
    """O que o gerador lê de uma anotação isolada."""

    def test_le_especie_numero_e_ano(self) -> None:
        diploma = gerador.extrair_diploma("(Redação dada pela Lei nº 14.181, de 2021)")
        self.assertEqual(
            diploma, {"especie": "Lei", "numero": "14.181", "ano": 2021}
        )

    def test_distingue_lei_complementar_de_lei(self) -> None:
        # "Complementar" não termina em "es": o padrão ingênuo `Complementares?`
        # casava "Complementare" e classificava a LC como lei ordinária.
        diploma = gerador.extrair_diploma("(Incluído pela Lei Complementar nº 150, de 2015)")
        self.assertEqual(diploma["especie"], "Lei Complementar")
        self.assertEqual(diploma["numero"], "150")

    def test_reconhece_emenda_constitucional(self) -> None:
        # Mesmo defeito de "Constitucionais?", que não casa "Constitucional".
        diploma = gerador.extrair_diploma("(Redação dada pela Emenda Constitucional nº 110, de 2021)")
        self.assertEqual(diploma["especie"], "Emenda Constitucional")
        self.assertEqual(diploma["ano"], 2021)

    def test_preserva_a_reedicao_da_medida_provisoria(self) -> None:
        # A MP 2.177-44 é norma distinta da MP 2.177-43; truncar no hífen
        # perdia a reedição e ainda derrubava o ano junto.
        diploma = gerador.extrair_diploma(
            "(Incluído pela Medida Provisória nº 2.177-44, de 2001)"
        )
        self.assertEqual(diploma["especie"], "Medida Provisória")
        self.assertEqual(diploma["numero"], "2.177-44")
        self.assertEqual(diploma["ano"], 2001)

    def test_le_o_ano_dentro_da_data_completa(self) -> None:
        diploma = gerador.extrair_diploma("(Redação dada pela Lcp nº 114, de 16.12.2002)")
        self.assertEqual(diploma["especie"], "Lei Complementar")
        self.assertEqual(diploma["ano"], 2002)

    def test_ano_de_dois_digitos_fica_nulo_em_vez_de_inventar_o_seculo(self) -> None:
        # Completar "97" para 1997 seria inferência nossa, não leitura da fonte.
        # O ano fica nulo e a anotação inteira permanece em `literal`.
        diploma = gerador.extrair_diploma("(Redação dada pela Lei nº 9.527, de 10.12.97)")
        self.assertEqual(diploma["numero"], "9.527")
        self.assertIsNone(diploma["ano"])

    def test_marcador_seco_de_situacao_nao_tem_diploma(self) -> None:
        self.assertIsNone(gerador.extrair_diploma("(Revogado)"))
        self.assertIsNone(gerador.extrair_diploma("(Vigência encerrada)"))


class AncoraTest(unittest.TestCase):
    """A anotação se prende à unidade alterada, não ao artigo."""

    TEXTO = (
        "Art. 6º São direitos básicos do consumidor:\n\n"
        "I - a proteção da vida;\n\n"
        "III - a informação adequada sobre preço; (Redação dada pela Lei nº 12.741, de 2012)\n\n"
        "XI - a repactuação de dívidas; (Incluído pela Lei nº 14.181, de 2021)\n\n"
        "§ 1º O disposto neste artigo é acessível. (Incluído pela Lei nº 13.146, de 2015)\n"
    )

    def test_prende_cada_anotacao_a_sua_unidade(self) -> None:
        eventos = gerador.eventos_do_artigo(self.TEXTO)
        self.assertEqual(
            [(evento["tipo"], evento["unidade"]) for evento in eventos],
            [
                ("redacao", "inciso III"),
                ("inclusao", "inciso XI"),
                ("inclusao", "§ 1º"),
            ],
        )

    def test_alteracao_de_inciso_nao_vira_situacao_do_artigo(self) -> None:
        # O caso que motiva a âncora: a Lei 14.181/2021 incluiu incisos no art.
        # 6º do CDC; dizer "art. 6º alterado pela Lei 14.181" seria afirmação
        # que a fonte não faz e que o caput desmente.
        eventos = gerador.eventos_do_artigo(self.TEXTO)
        self.assertIsNone(gerador.situacao_do_artigo(eventos))

    def test_revogacao_no_caput_revoga_o_artigo(self) -> None:
        eventos = gerador.eventos_do_artigo(
            "Art. 30. (Revogado pela Lei nº 13.105, de 2015)"
        )
        self.assertEqual(eventos[0]["unidade"], "caput")
        self.assertEqual(gerador.situacao_do_artigo(eventos), "revogado")

    def test_revogacao_de_inciso_nao_revoga_o_artigo(self) -> None:
        eventos = gerador.eventos_do_artigo(
            "Art. 40. São deveres:\n\nII - o dever antigo; (Revogado pela Lei nº 9.999, de 1999)\n"
        )
        self.assertEqual(eventos[0]["unidade"], "inciso II")
        self.assertIsNone(gerador.situacao_do_artigo(eventos))

    def test_nunca_afirma_vigencia(self) -> None:
        # A fonte não diz "vigente"; o índice também não pode dizer.
        eventos = gerador.eventos_do_artigo(
            "Art. 1º Texto. (Redação dada pela Lei nº 1.000, de 2000)"
        )
        self.assertIsNone(gerador.situacao_do_artigo(eventos))


class FalsoPositivoTest(unittest.TestCase):
    def test_prosa_entre_parenteses_nao_vira_evento(self) -> None:
        # A TIPI escreve "(incluídos os fios absorvíveis...)" como texto comum
        # da norma. Começa com o mesmo verbo de "(Incluído pela Lei...)" e não
        # registra alteração nenhuma.
        eventos = gerador.eventos_do_artigo(
            "Art. 1º Materiais (incluídos os fios absorvíveis esterilizados "
            "para cirurgia ou odontologia) ficam isentos."
        )
        self.assertEqual(eventos, [])

    def test_marcador_seco_continua_sendo_evento(self) -> None:
        eventos = gerador.eventos_do_artigo("Art. 2º (Revogado)")
        self.assertEqual(len(eventos), 1)
        self.assertEqual(eventos[0]["tipo"], "revogacao")

    def test_remissao_vide_fica_de_fora(self) -> None:
        # "Vide" aponta outro texto; não registra mudança sofrida.
        eventos = gerador.eventos_do_artigo("Art. 3º Texto. (Vide Lei nº 8.000, de 1990)")
        self.assertEqual(eventos, [])


class IndicePublicadoTest(unittest.TestCase):
    def test_manifesto_declara_processo_local_sem_modelo(self) -> None:
        config = gerador.carregar_manifesto()["vigencia"]["gerador"]
        self.assertEqual(config["algoritmo"], gerador.ALGORITMO)
        self.assertIsNone(config["modelo"])
        self.assertIsNone(config["prompt"])

    def test_saidas_publicadas_sao_exatamente_reproduziveis(self) -> None:
        for destino, esperado in gerador.gerar_todos():
            atual = json.loads(destino.read_text(encoding="utf-8"))
            self.assertEqual(atual, esperado, destino.name)

    def test_todo_diploma_tem_indice_e_todo_indice_aponta_sua_fonte(self) -> None:
        manifesto = gerador.carregar_manifesto()
        diretorio = ROOT / manifesto["diretorio_dados"]
        fontes = sorted(diretorio.glob(manifesto["vigencia"]["padrao_fonte"]))
        self.assertEqual(len(fontes), 277)
        for fonte_path in fontes:
            destino = (
                fonte_path.parent
                / manifesto["vigencia"]["subdiretorio_destino"]
                / (fonte_path.stem + manifesto["vigencia"]["sufixo_destino"])
            )
            self.assertTrue(destino.exists(), destino.name)
            indice = json.loads(destino.read_text(encoding="utf-8"))
            self.assertEqual(indice["_meta"]["fonte"]["arquivo"], fonte_path.name)
            self.assertEqual(
                indice["_meta"]["fonte"]["sha256"], gerador.sha256(fonte_path)
            )

    def test_nenhum_artigo_sem_anotacao_recebe_entrada(self) -> None:
        manifesto = gerador.carregar_manifesto()
        diretorio = ROOT / manifesto["diretorio_dados"]
        for fonte_path in sorted(diretorio.glob("lei_c*.json")):
            fonte = json.loads(fonte_path.read_text(encoding="utf-8"))
            destino = fonte_path.parent / "indices" / (fonte_path.stem + "_vigencia.json")
            indice = json.loads(destino.read_text(encoding="utf-8"))["vigencia"]
            for numero, artigo in fonte["artigos"].items():
                tem_evento = bool(gerador.eventos_do_artigo(str(artigo["texto"])))
                self.assertEqual(numero in indice, tem_evento, f"{fonte_path.name}:{numero}")

    def test_todo_evento_e_rastreavel_a_uma_string_da_fonte(self) -> None:
        manifesto = gerador.carregar_manifesto()
        diretorio = ROOT / manifesto["diretorio_dados"]
        for fonte_path in sorted(diretorio.glob("lei_cdc.json")):
            fonte = json.loads(fonte_path.read_text(encoding="utf-8"))
            destino = fonte_path.parent / "indices" / (fonte_path.stem + "_vigencia.json")
            indice = json.loads(destino.read_text(encoding="utf-8"))["vigencia"]
            for numero, registro in indice.items():
                texto = " ".join(str(fonte["artigos"][numero]["texto"]).split())
                for evento in registro["eventos"]:
                    self.assertIn(evento["literal"], texto)

    def test_cobertura_medida_do_acervo(self) -> None:
        """Fixa o resultado medido, para que regressão apareça como queda."""
        manifesto = gerador.carregar_manifesto()
        diretorio = ROOT / manifesto["diretorio_dados"]
        artigos = eventos = sem_diploma = 0
        situacoes: dict[str | None, int] = {}
        for destino in sorted(diretorio.glob("indices/*_vigencia.json")):
            indice = json.loads(destino.read_text(encoding="utf-8"))["vigencia"]
            artigos += len(indice)
            for registro in indice.values():
                situacoes[registro["situacao"]] = situacoes.get(registro["situacao"], 0) + 1
                for evento in registro["eventos"]:
                    eventos += 1
                    if evento["diploma"] is None:
                        sem_diploma += 1
        self.assertEqual(artigos, 7321)
        self.assertEqual(eventos, 32146)
        self.assertEqual(situacoes.get("revogado"), 872)
        self.assertEqual(situacoes.get("vetado"), 395)
        self.assertEqual(situacoes.get("vigencia_encerrada"), 33)
        # Sem diploma nomeado é o marcador seco da fonte — "(Revogado)",
        # "(VETADO)", "(Vigência)" —, não falha de extração.
        self.assertEqual(sem_diploma, 5001)


if __name__ == "__main__":
    unittest.main()
