#!/usr/bin/env python3
"""Valida a portabilidade das skills entre Codex e Claude Code."""

from __future__ import annotations

import re
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]
FONTE = RAIZ / ".agents" / "skills"
ESPELHO = RAIZ / ".claude" / "skills"

MARCADORES_INCOMPATIVEIS = {
    "$ARGUMENTS": "substituição específica de uma interface",
    ".Codex/skills": "caminho inexistente",
    ".codex/skills": "caminho incorreto para skills de repositório",
    "WebFetch": "nome de ferramenta específico do Claude Code",
    "`Read`": "nome de ferramenta específico do Claude Code",
    "você (Codex)": "instrução vinculada a um fornecedor",
    "abriu o Codex": "instrução vinculada a um fornecedor",
}


def arquivos_da_arvore(base: Path) -> dict[Path, Path]:
    if not base.is_dir():
        return {}
    return {
        arquivo.relative_to(base): arquivo
        for arquivo in base.rglob("*")
        if arquivo.is_file() and arquivo.name != ".DS_Store"
    }


def ler_frontmatter(caminho: Path) -> dict[str, str]:
    texto = caminho.read_text(encoding="utf-8")
    if not texto.startswith("---\n"):
        return {}
    fim = texto.find("\n---\n", 4)
    if fim == -1:
        return {}

    dados: dict[str, str] = {}
    for linha in texto[4:fim].splitlines():
        if ":" not in linha:
            continue
        chave, valor = linha.split(":", 1)
        dados[chave.strip()] = valor.strip().strip('"\'')
    return dados


def validar() -> list[str]:
    erros: list[str] = []

    if not (RAIZ / "AGENTS.md").is_file():
        erros.append("AGENTS.md não encontrado na raiz.")
    if "@AGENTS.md" not in (RAIZ / "CLAUDE.md").read_text(encoding="utf-8"):
        erros.append("CLAUDE.md não importa AGENTS.md.")

    fonte = arquivos_da_arvore(FONTE)
    espelho = arquivos_da_arvore(ESPELHO)
    skills = sorted(FONTE.glob("*/SKILL.md")) if FONTE.is_dir() else []

    if not skills:
        erros.append("Nenhuma skill encontrada em .agents/skills/.")

    for skill in skills:
        relativo = skill.relative_to(RAIZ)
        texto = skill.read_text(encoding="utf-8")
        dados = ler_frontmatter(skill)
        nome_da_pasta = re.sub(r"^\d+\.\d+-", "", skill.parent.name)

        if not dados.get("name"):
            erros.append(f"{relativo}: frontmatter sem 'name'.")
        elif dados["name"] != nome_da_pasta:
            erros.append(
                f"{relativo}: name '{dados['name']}' não corresponde à pasta "
                f"'{skill.parent.name}'."
            )
        if not dados.get("description"):
            erros.append(f"{relativo}: frontmatter sem 'description'.")

        for marcador, motivo in MARCADORES_INCOMPATIVEIS.items():
            if marcador in texto:
                erros.append(f"{relativo}: contém '{marcador}' ({motivo}).")

        for referencia in re.findall(r"/\.agents/skills/([^\s\"')]+)", texto):
            destino = FONTE / referencia
            if not destino.is_file():
                erros.append(
                    f"{relativo}: arquivo auxiliar não encontrado: "
                    f".agents/skills/{referencia}"
                )

    faltando = sorted(set(fonte) - set(espelho))
    sobrando = sorted(set(espelho) - set(fonte))
    divergentes = sorted(
        relativo
        for relativo in set(fonte) & set(espelho)
        if fonte[relativo].read_bytes() != espelho[relativo].read_bytes()
    )

    for relativo in faltando:
        erros.append(f"Ausente no espelho .claude/skills/: {relativo}")
    for relativo in sobrando:
        erros.append(f"Arquivo sem fonte canônica no espelho: {relativo}")
    for relativo in divergentes:
        erros.append(f"Espelho divergente da fonte canônica: {relativo}")

    return erros


def main() -> int:
    erros = validar()
    if erros:
        print("Falha na compatibilidade das skills:\n")
        for erro in erros:
            print(f"- {erro}")
        print("\nRode: bash ferramentas/manutencao/sincronizar-skills.sh")
        return 1

    total = len(list(FONTE.glob("*/SKILL.md")))
    print(f"Compatibilidade validada: {total} skills portáveis e sincronizadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
