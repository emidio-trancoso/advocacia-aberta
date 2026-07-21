from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
MODULO_PATH = ROOT / "ferramentas" / "manutencao" / "verificar_compatibilidade.py"
SPEC = importlib.util.spec_from_file_location("verificar_compatibilidade", MODULO_PATH)
assert SPEC and SPEC.loader
compatibilidade = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = compatibilidade
SPEC.loader.exec_module(compatibilidade)


class VerificadorCompatibilidadeTest(unittest.TestCase):
    def test_detecta_caminho_do_espelho_em_arquivo_auxiliar(self) -> None:
        erros = compatibilidade.validar_texto_portavel(
            Path(".agents/skills/exemplo/template.typ"),
            '#import "/.claude/skills/exemplo/template.typ": *',
        )
        self.assertEqual(len(erros), 1)
        self.assertIn("dependência do espelho", erros[0])

    def test_aceita_referencia_para_arquivo_canonico_existente(self) -> None:
        erros = compatibilidade.validar_texto_portavel(
            Path(".agents/skills/3.2-diagramar-peca/SKILL.md"),
            'Use "/.agents/skills/3.2-diagramar-peca/template.typ".',
        )
        self.assertEqual(erros, [])

    def test_filtrar_por_skills_seleciona_apenas_whitelist(self) -> None:
        arvore = {
            Path("1.1-organizar-caso/SKILL.md"): Path("/x/a"),
            Path("2.1-diagnosticar/SKILL.md"): Path("/x/b"),
            Path("3.1-redigir-peca/SKILL.md"): Path("/x/c"),
        }
        filtrado = compatibilidade.filtrar_por_skills(
            arvore, ("1.1-organizar-caso", "2.1-diagnosticar")
        )
        self.assertEqual(
            set(filtrado),
            {Path("1.1-organizar-caso/SKILL.md"), Path("2.1-diagnosticar/SKILL.md")},
        )

    def test_comparar_arvores_detecta_faltando_sobrando_e_divergente(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "igual_fonte.txt").write_bytes(b"abc")
            (base / "igual_espelho.txt").write_bytes(b"abc")
            (base / "div_fonte.txt").write_bytes(b"fonte")
            (base / "div_espelho.txt").write_bytes(b"espelho")
            (base / "so_fonte.txt").write_bytes(b"x")
            (base / "so_espelho.txt").write_bytes(b"y")

            esperado = {
                Path("igual.txt"): base / "igual_fonte.txt",
                Path("div.txt"): base / "div_fonte.txt",
                Path("faltando.txt"): base / "so_fonte.txt",
            }
            atual = {
                Path("igual.txt"): base / "igual_espelho.txt",
                Path("div.txt"): base / "div_espelho.txt",
                Path("sobrando.txt"): base / "so_espelho.txt",
            }
            erros = compatibilidade.comparar_arvores("teste", esperado, atual)

        texto = "\n".join(erros)
        self.assertIn("Ausente no espelho teste/: faltando.txt", texto)
        self.assertIn("Arquivo sem fonte canônica no espelho teste/: sobrando.txt", texto)
        self.assertIn("Espelho teste/ divergente da fonte canônica: div.txt", texto)
        self.assertNotIn("igual.txt", texto)


if __name__ == "__main__":
    unittest.main()
