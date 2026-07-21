#!/usr/bin/env python3
"""Valida a portabilidade das skills entre Codex e Claude Code."""

from __future__ import annotations

import re
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]
FONTE = RAIZ / ".agents" / "skills"
# Espelhos gerados a partir da fonte canônica (ver sincronizar-skills.sh).
ESPELHOS = {
    ".claude/skills": RAIZ / ".claude" / "skills",  # adaptador Claude Code
    "skills": RAIZ / "skills",                        # adaptador de plugin
}

# Bundle curado publicado como plugin Codex/OpenAI: subconjunto da fonte canônica
# com apenas as skills autônomas (ver .codex-plugin/README.md e sincronizar-skills.sh).
BUNDLE_CODEX = RAIZ / ".codex-plugin" / "skills"
CURADO_CODEX = (
    "1.1-organizar-caso",
    "2.1-diagnosticar",
    "2.2-buscar-fontes",
    "3.1-redigir-peca",
    "4.1-revisar-peca",
)

MARCADORES_INCOMPATIVEIS = {
    "$ARGUMENTS": "substituição específica de uma interface",
    ".Codex/skills": "caminho inexistente",
    ".codex/skills": "caminho incorreto para skills de repositório",
    ".claude/skills": "dependência do espelho específico do Claude Code",
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


def filtrar_por_skills(arvore: dict[Path, Path], nomes) -> dict[Path, Path]:
    """Mantém só os arquivos cuja skill (pasta de topo) está na whitelist."""
    nomes = set(nomes)
    return {
        relativo: caminho
        for relativo, caminho in arvore.items()
        if relativo.parts and relativo.parts[0] in nomes
    }


def comparar_arvores(
    rotulo: str, esperado: dict[Path, Path], atual: dict[Path, Path]
) -> list[str]:
    """Compara duas árvores por conjunto de arquivos e por conteúdo (bytes)."""
    erros: list[str] = []
    faltando = sorted(set(esperado) - set(atual))
    sobrando = sorted(set(atual) - set(esperado))
    divergentes = sorted(
        relativo
        for relativo in set(esperado) & set(atual)
        if esperado[relativo].read_bytes() != atual[relativo].read_bytes()
    )
    for relativo in faltando:
        erros.append(f"Ausente no espelho {rotulo}/: {relativo}")
    for relativo in sobrando:
        erros.append(f"Arquivo sem fonte canônica no espelho {rotulo}/: {relativo}")
    for relativo in divergentes:
        erros.append(f"Espelho {rotulo}/ divergente da fonte canônica: {relativo}")
    return erros


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


def validar_texto_portavel(relativo: Path, texto: str) -> list[str]:
    erros: list[str] = []
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
    return erros


def validar() -> list[str]:
    erros: list[str] = []

    if not (RAIZ / "AGENTS.md").is_file():
        erros.append("AGENTS.md não encontrado na raiz.")
    claude_md = RAIZ / "CLAUDE.md"
    if not claude_md.is_file():
        erros.append("CLAUDE.md não encontrado na raiz.")
    elif "@AGENTS.md" not in claude_md.read_text(encoding="utf-8"):
        erros.append("CLAUDE.md não importa AGENTS.md.")

    fonte = arquivos_da_arvore(FONTE)
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

    for relativo_na_skill, arquivo in sorted(fonte.items()):
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relativo = arquivo.relative_to(RAIZ)
        erros.extend(validar_texto_portavel(relativo, texto))

    for rotulo, base in ESPELHOS.items():
        erros.extend(comparar_arvores(rotulo, fonte, arquivos_da_arvore(base)))

    # Bundle curado do plugin Codex: subconjunto byte-idêntico da fonte canônica.
    for nome in CURADO_CODEX:
        if not (FONTE / nome / "SKILL.md").is_file():
            erros.append(
                f"Skill '{nome}' da whitelist do bundle Codex não existe em .agents/skills/."
            )
    esperado_curado = filtrar_por_skills(fonte, CURADO_CODEX)
    erros.extend(
        comparar_arvores(
            ".codex-plugin/skills", esperado_curado, arquivos_da_arvore(BUNDLE_CODEX)
        )
    )

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
