from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
MODULO_PATH = ROOT / "ferramentas" / "manutencao" / "construir_indice_geo.py"
SPEC = importlib.util.spec_from_file_location("construir_indice_geo", MODULO_PATH)
assert SPEC and SPEC.loader
construtor = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = construtor
SPEC.loader.exec_module(construtor)


class ParaInteiroTest(unittest.TestCase):
    """Conversão de IPv4 em inteiro usada para montar as faixas do índice."""

    def test_converte_ipv4_valido(self) -> None:
        self.assertEqual(construtor.para_inteiro("1.2.3.4"), (1 << 24) | (2 << 16) | (3 << 8) | 4)

    def test_endereco_zero(self) -> None:
        self.assertEqual(construtor.para_inteiro("0.0.0.0"), 0)

    def test_endereco_maximo(self) -> None:
        self.assertEqual(construtor.para_inteiro("255.255.255.255"), 0xFFFFFFFF)

    def test_ipv6_devolve_none(self) -> None:
        self.assertIsNone(construtor.para_inteiro("2001:db8::1"))

    def test_string_vazia_devolve_none(self) -> None:
        self.assertIsNone(construtor.para_inteiro(""))

    def test_octeto_fora_da_faixa_devolve_none(self) -> None:
        self.assertIsNone(construtor.para_inteiro("1.2.3.256"))

    def test_octeto_nao_numerico_devolve_none(self) -> None:
        self.assertIsNone(construtor.para_inteiro("1.2.3.abc"))

    def test_numero_insuficiente_de_octetos_devolve_none(self) -> None:
        self.assertIsNone(construtor.para_inteiro("1.2.3"))


if __name__ == "__main__":
    unittest.main()
