from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
MODULO_PATH = ROOT / "ferramentas" / "manutencao" / "gerar_indices_derivados.py"
SPEC = importlib.util.spec_from_file_location("gerar_indices_derivados", MODULO_PATH)
assert SPEC and SPEC.loader
gerador = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gerador
SPEC.loader.exec_module(gerador)


class IndicesDerivadosTest(unittest.TestCase):
    def test_manifesto_declara_processo_local_sem_modelo(self) -> None:
        manifesto = gerador.carregar_manifesto()
        config = manifesto["gerador"]
        self.assertEqual(config["versao"], "1.0.0")
        self.assertEqual(config["algoritmo"], "tokens-significativos-v1")
        self.assertIsNone(config["modelo"])
        self.assertIsNone(config["prompt"])
        self.assertEqual(config["parametros"]["stopwords"], "pt-juridico-v1")

    def test_saidas_publicadas_sao_exatamente_reproduziveis(self) -> None:
        for destino, esperado in gerador.gerar_todos():
            atual = json.loads(destino.read_text(encoding="utf-8"))
            self.assertEqual(atual, esperado, destino.name)

    def test_indices_cobrem_as_fontes_em_relacao_um_para_um(self) -> None:
        manifesto = gerador.carregar_manifesto()
        diretorio = ROOT / manifesto["diretorio_dados"]
        for config in manifesto["conjuntos"].values():
            fonte_path = diretorio / config["fonte"]
            fonte = json.loads(fonte_path.read_text(encoding="utf-8"))
            registros = fonte[config["colecao"]]
            indice = json.loads((diretorio / config["destino"]).read_text(encoding="utf-8"))
            itens = indice["keywords"]
            self.assertEqual(len(itens), len(registros))
            self.assertEqual(
                {item["numero"] for item in itens.values()},
                {item["numero"] for item in registros.values()},
            )
            self.assertTrue(all(item["keywords"] for item in itens.values()))
            self.assertEqual(indice["_meta"]["fonte"]["sha256"], hashlib.sha256(fonte_path.read_bytes()).hexdigest())

    def test_manifesto_da_legislacao_declara_processo_local_sem_modelo(self) -> None:
        manifesto = gerador.carregar_manifesto()
        config = manifesto["legislacao"]["gerador"]
        self.assertEqual(config["algoritmo"], "tokens-texto-integral-v1")
        self.assertIsNone(config["modelo"])
        self.assertIsNone(config["prompt"])
        self.assertEqual(config["parametros"]["tamanho_minimo_token"], 3)
        # As stopwords são preservadas de propósito: o índice reproduz a busca
        # em texto integral do motor, e removê-las mudaria ranking e piso.
        self.assertIn("nenhuma", config["parametros"]["stopwords"])

    def test_indices_da_legislacao_cobrem_todos_os_dispositivos(self) -> None:
        manifesto = gerador.carregar_manifesto()
        diretorio = ROOT / manifesto["diretorio_dados"]
        config = manifesto["legislacao"]
        fontes = sorted(diretorio.glob(config["padrao_fonte"]))
        self.assertGreaterEqual(len(fontes), 270)
        for fonte_path in fontes:
            fonte = json.loads(fonte_path.read_text(encoding="utf-8"))
            indice_path = (
                diretorio
                / config["subdiretorio_destino"]
                / (fonte_path.stem + config["sufixo_destino"])
            )
            self.assertTrue(indice_path.exists(), indice_path.name)
            indice = json.loads(indice_path.read_text(encoding="utf-8"))
            curados = gerador.numeros_no_indice_curado(fonte)
            gerados = set(indice["tokens"])
            artigos = set(fonte["artigos"])
            # Cobertura 1:1: cada dispositivo publicado aparece exatamente uma
            # vez, no índice curado preservado ou no derivado — nenhum artigo
            # novo pode ficar invisível à busca textual.
            self.assertEqual(curados | gerados, artigos, fonte_path.name)
            self.assertEqual(curados & gerados, set(), fonte_path.name)
            self.assertTrue(all(indice["tokens"].values()), fonte_path.name)
            self.assertEqual(
                indice["_meta"]["fonte"]["sha256"],
                hashlib.sha256(fonte_path.read_bytes()).hexdigest(),
                fonte_path.name,
            )


if __name__ == "__main__":
    unittest.main()
