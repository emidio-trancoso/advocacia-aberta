#!/usr/bin/env python3
"""Versiona os snapshots publicados e o resumo das diferenças (BASE-013).

O manifesto `base-juridica/snapshots.json` registra, por arquivo publicado da
base jurídica: a versão (contador que avança a cada mudança de conteúdo), o
SHA-256, a data de geração declarada pelo próprio arquivo, a contagem de
registros e o resumo das mudanças em relação à versão anterior (IDs
adicionados, removidos e alterados, contados a partir do estado versionado no
Git antes da promoção).

- `--escrever` atualiza o manifesto após uma promoção (o estado anterior vem
  de `git show HEAD:<arquivo>`);
- `--verificar` confere que o manifesto reflete exatamente os arquivos
  publicados (SHA-256, contagens e cobertura), sem consultar a rede.

Os índices derivados não entram aqui: eles têm manifesto e verificação
próprios (`indices-derivados.json`, BASE-010/BASE-019).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
DATA = RAIZ / "ferramentas" / "pesquisa" / "vade-mecum" / "data"
MANIFESTO = RAIZ / "base-juridica" / "snapshots.json"

# Famílias publicadas rastreadas: coleção e campo de data de geração.
FAMILIAS_FIXAS = {
    "sumulas_stj.json": ("sumulas", "gerado_em"),
    "sumulas_stf.json": ("sumulas", "gerado_em"),
    "sumulas_vinculantes.json": ("sumulas", "gerado_em"),
    "jt_stj.json": ("teses", "gerado_em"),
    "flash_temas_stj.json": ("temas", "generatedAt"),
    "temas_rg_stf.json": ("temas", "generatedAt"),
    "informativo_stf.json": ("informativos", "generatedAt"),
    "espelhos_stj.json": ("espelhos", "generatedAt"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def arquivos_rastreados() -> list[tuple[str, str, str]]:
    """Devolve (nome do arquivo, coleção, campo de data) em ordem estável."""
    rastreados = [
        (path.name, "artigos", "gerado_em")
        for path in sorted(DATA.glob("lei_*.json"))
    ]
    rastreados.extend(
        (nome, colecao, campo)
        for nome, (colecao, campo) in sorted(FAMILIAS_FIXAS.items())
    )
    return rastreados


def carregar_json(texto: str) -> dict[str, Any]:
    return json.loads(texto)


def hash_registro(valor: Any) -> str:
    return hashlib.sha256(
        json.dumps(valor, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def resumo_mudancas(
    anterior: dict[str, Any] | None, atual: dict[str, Any], colecao: str
) -> dict[str, Any] | None:
    """Resumo de IDs adicionados, removidos e alterados entre dois snapshots."""
    if anterior is None:
        return None
    registros_antes = anterior.get(colecao, {})
    registros_agora = atual.get(colecao, {})
    adicionados = sorted(set(registros_agora) - set(registros_antes))
    removidos = sorted(set(registros_antes) - set(registros_agora))
    alterados = sorted(
        chave
        for chave in set(registros_antes) & set(registros_agora)
        if hash_registro(registros_antes[chave]) != hash_registro(registros_agora[chave])
    )
    return {
        "adicionados": len(adicionados),
        "removidos": len(removidos),
        "alterados": len(alterados),
        "amostra_adicionados": adicionados[:10],
        "amostra_removidos": removidos[:10],
        "amostra_alterados": alterados[:10],
    }


def conteudo_versionado(nome: str) -> dict[str, Any] | None:
    caminho_git = f"ferramentas/pesquisa/vade-mecum/data/{nome}"
    resultado = subprocess.run(
        ["git", "show", f"HEAD:{caminho_git}"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        return None
    return carregar_json(resultado.stdout)


def carregar_manifesto() -> dict[str, Any]:
    if not MANIFESTO.exists():
        return {
            "$schema": "./snapshots.schema.json",
            "schema_version": 1,
            "descricao": (
                "Manifesto de versões dos snapshots publicados: versão, "
                "SHA-256, data de geração, contagem e resumo das mudanças "
                "promovidas (BASE-013)."
            ),
            "arquivos": {},
        }
    dados = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    if dados.get("schema_version") != 1:
        raise ValueError("versão desconhecida do manifesto de snapshots")
    return dados


def serializar(objeto: dict[str, Any]) -> str:
    return json.dumps(objeto, ensure_ascii=False, indent=2) + "\n"


def escrever() -> int:
    manifesto = carregar_manifesto()
    entradas = manifesto["arquivos"]
    mudancas = 0
    for nome, colecao, campo_data in arquivos_rastreados():
        path = DATA / nome
        atual = carregar_json(path.read_text(encoding="utf-8"))
        resumo_atual = {
            "sha256": sha256(path),
            "gerado_em": atual.get("_meta", {}).get(campo_data),
            "registros": len(atual.get(colecao, {})),
        }
        entrada = entradas.get(nome)
        if entrada and entrada["sha256"] == resumo_atual["sha256"]:
            continue
        # A primeira entrada é a linha de base (mudancas nula); nas seguintes,
        # o estado anterior vem do Git — por isso o manifesto deve ser
        # atualizado depois da promoção e antes do commit correspondente.
        anterior = conteudo_versionado(nome) if entrada else None
        entradas[nome] = {
            "versao": (entrada["versao"] + 1) if entrada else 1,
            **resumo_atual,
            "colecao": colecao,
            "mudancas": resumo_mudancas(anterior, atual, colecao),
        }
        mudancas += 1
        print(f"Versionado: {nome} (v{entradas[nome]['versao']})")
    # Arquivos que deixaram de existir saem do manifesto (a remoção do dado em
    # si já passou pelos gates de promoção).
    conhecidos = {nome for nome, _, _ in arquivos_rastreados()}
    for orfao in sorted(set(entradas) - conhecidos):
        del entradas[orfao]
        mudancas += 1
        print(f"Removido do manifesto: {orfao}")
    manifesto["arquivos"] = dict(sorted(entradas.items()))
    MANIFESTO.write_text(serializar(manifesto), encoding="utf-8")
    print(f"Manifesto atualizado: {mudancas} entrada(s) alterada(s).")
    return 0


def verificar() -> int:
    problemas: list[str] = []
    if not MANIFESTO.exists():
        print("snapshots.json ainda não existe; rode --escrever.", file=sys.stderr)
        return 1
    manifesto = carregar_manifesto()
    entradas = manifesto.get("arquivos", {})
    esperados = arquivos_rastreados()
    nomes_esperados = {nome for nome, _, _ in esperados}
    for nome, colecao, _ in esperados:
        entrada = entradas.get(nome)
        if entrada is None:
            problemas.append(f"{nome}: publicado sem entrada no manifesto")
            continue
        path = DATA / nome
        if entrada.get("sha256") != sha256(path):
            problemas.append(f"{nome}: SHA-256 divergente do publicado")
            continue
        atual = carregar_json(path.read_text(encoding="utf-8"))
        if entrada.get("registros") != len(atual.get(colecao, {})):
            problemas.append(f"{nome}: contagem divergente do publicado")
    for orfao in sorted(set(entradas) - nomes_esperados):
        problemas.append(f"{orfao}: entrada no manifesto sem arquivo publicado")
    if problemas:
        for problema in problemas:
            print(f"Divergente: {problema}", file=sys.stderr)
        print(
            "Após promover, atualize o manifesto com gerar_snapshots.py --escrever.",
            file=sys.stderr,
        )
        return 1
    print(f"Snapshots coerentes: {len(entradas)} arquivos versionados.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--escrever", action="store_true")
    grupo.add_argument("--verificar", action="store_true")
    args = parser.parse_args()
    return escrever() if args.escrever else verificar()


if __name__ == "__main__":
    raise SystemExit(main())
