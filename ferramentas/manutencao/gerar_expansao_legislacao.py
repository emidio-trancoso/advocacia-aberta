#!/usr/bin/env python3
"""Materializa grupos da expansão legislativa a partir do manifesto versionado.

O manifesto é ``base-juridica/expansao/normas.json``. Cada norma tem sigla,
nome, espécie normativa, URL oficial validada e grupo. Materializar um grupo
significa:

1. acrescentar o conjunto ``legislacao_<grupo>`` em ``fontes.json``;
2. criar stubs vazios em ``data/`` para destinos ainda inexistentes (o
   pipeline de atualização preenche e o diff mostra somente adições);
3. regenerar o bloco de entradas do ``REGISTRO_CODIGOS`` entre os marcadores
   de ``legislacao.ts``, cobrindo todos os grupos já materializados.

Nada aqui coleta ou publica conteúdo jurídico: a captura continua no
``atualizar_base_juridica.py`` e a promoção continua exigindo revisão.

``--verificar`` confere a sincronia (manifesto ↔ fontes.json ↔ legislacao.ts
↔ arquivos em data/) sem escrever nada, e falha com código 1 em divergência.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
NORMAS_PATH = ROOT / "base-juridica" / "expansao" / "normas.json"
FONTES_PATH = ROOT / "base-juridica" / "fontes.json"
LEGISLACAO_TS = (
    ROOT / "ferramentas" / "pesquisa" / "vade-mecum" / "src" / "search" / "legislacao.ts"
)
DATA = ROOT / "ferramentas" / "pesquisa" / "vade-mecum" / "data"
MARCA_INICIO = (
    "  // [expansao:inicio] entradas geradas por gerar_expansao_legislacao.py"
    " — não edite à mão"
)
MARCA_FIM = "  // [expansao:fim]"
PREFIXO_CONJUNTO = "legislacao_"


def carregar_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_json(path: Path, valor: Any) -> None:
    with path.open("w", encoding="utf-8") as arquivo:
        json.dump(valor, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")


def id_da_sigla(sigla: str) -> str:
    return sigla.lower()


def carregar_normas() -> list[dict[str, Any]]:
    manifesto = carregar_json(NORMAS_PATH)
    if manifesto.get("schema_version") != 1:
        raise ValueError("versão desconhecida do manifesto de expansão")
    normas = manifesto["normas"]
    erros: list[str] = []
    siglas = [norma["sigla"] for norma in normas]
    for sigla in sorted({s for s in siglas if siglas.count(s) > 1}):
        erros.append(f"sigla duplicada no manifesto: {sigla}")
    nucleo = siglas_do_nucleo()
    for sigla in sorted(set(siglas) & nucleo):
        erros.append(f"sigla colide com o núcleo do motor: {sigla}")
    for norma in normas:
        if not re.fullmatch(r"[A-Z][A-Z0-9]*", norma["sigla"]):
            erros.append(f"sigla inválida: {norma['sigla']!r}")
        url = norma["url"]
        if not url.startswith("https://www.planalto.gov.br/ccivil_03/"):
            erros.append(f"{norma['sigla']}: URL fora do Planalto: {url}")
        caminho = url.removeprefix("https://www.planalto.gov.br")
        if caminho != caminho.lower():
            erros.append(f"{norma['sigla']}: URL fora do caminho minúsculo canônico: {url}")
        for campo in ("nome", "lei", "grupo"):
            if not str(norma.get(campo, "")).strip():
                erros.append(f"{norma['sigla']}: campo vazio: {campo}")
        if '"' in norma["nome"] + norma["lei"]:
            erros.append(f"{norma['sigla']}: aspas duplas em nome/lei quebram o TS gerado")
    if erros:
        raise ValueError("manifesto de expansão inválido:\n- " + "\n- ".join(erros))
    return normas


def siglas_do_nucleo() -> set[str]:
    """Siglas declaradas à mão em legislacao.ts, antes do marcador gerado."""
    fonte = LEGISLACAO_TS.read_text(encoding="utf-8")
    corpo = fonte.split(MARCA_INICIO)[0] if MARCA_INICIO in fonte else fonte
    return set(re.findall(r"^\s{2}([A-Z][A-Z0-9]*):\s*\{", corpo, re.MULTILINE))


def grupos_do_manifesto(normas: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grupos: dict[str, list[dict[str, Any]]] = {}
    for norma in normas:
        grupos.setdefault(norma["grupo"], []).append(norma)
    return grupos


def conjunto_esperado(normas_grupo: list[dict[str, Any]]) -> dict[str, Any]:
    fontes = []
    for norma in sorted(normas_grupo, key=lambda item: id_da_sigla(item["sigla"])):
        identificador = id_da_sigla(norma["sigla"])
        fonte = {
            "id": identificador,
            "codigo": norma["sigla"],
            "url": norma["url"],
            "arquivo_bruto": f"{identificador}.html",
            "destino": f"lei_{identificador}.json",
        }
        if norma.get("descartar_artigos"):
            fonte["descartar_artigos"] = list(norma["descartar_artigos"])
        fontes.append(fonte)
    return {
        "familia": "legislacao",
        "adaptador": "planalto_html_v1",
        "chave_colecao": "artigos",
        "fontes": fontes,
    }


def grupos_materializados(fontes_json: dict[str, Any]) -> list[str]:
    return sorted(
        chave.removeprefix(PREFIXO_CONJUNTO)
        for chave in fontes_json["conjuntos"]
        if chave.startswith(PREFIXO_CONJUNTO)
    )


def bloco_ts(normas_materializadas: list[dict[str, Any]]) -> str:
    linhas = [MARCA_INICIO]
    for norma in sorted(normas_materializadas, key=lambda item: item["sigla"]):
        identificador = id_da_sigla(norma["sigla"])
        linhas.extend(
            [
                f"  {norma['sigla']}: {{",
                f'    arquivo: "../../data/lei_{identificador}.json",',
                f'    rotulo: "{norma["nome"]} ({norma["lei"]})",',
                "  },",
            ]
        )
    linhas.append(MARCA_FIM)
    return "\n".join(linhas)


def bloco_ts_atual() -> str | None:
    fonte = LEGISLACAO_TS.read_text(encoding="utf-8")
    match = re.search(
        re.escape(MARCA_INICIO) + r"\n.*?" + re.escape(MARCA_FIM), fonte, re.DOTALL
    )
    return match.group(0) if match else None


def stub_da_norma(norma: dict[str, Any]) -> dict[str, Any]:
    return {
        "_meta": {
            "codigo": norma["sigla"],
            "nome": norma["nome"],
            "lei": norma["lei"],
            "url_base": norma["url"],
            "total_artigos": 0,
        },
        "artigos": {},
    }


def normas_dos_grupos(
    normas: list[dict[str, Any]], grupos: list[str]
) -> list[dict[str, Any]]:
    por_grupo = grupos_do_manifesto(normas)
    resultado: list[dict[str, Any]] = []
    desconhecidos = sorted(set(grupos) - set(por_grupo))
    if desconhecidos:
        raise ValueError("grupos ausentes do manifesto: " + ", ".join(desconhecidos))
    for grupo in grupos:
        resultado.extend(por_grupo[grupo])
    return resultado


def materializar(grupos: list[str]) -> None:
    normas = carregar_normas()
    fontes_json = carregar_json(FONTES_PATH)
    for grupo in grupos:
        chave = PREFIXO_CONJUNTO + grupo
        fontes_json["conjuntos"][chave] = conjunto_esperado(
            normas_dos_grupos(normas, [grupo])
        )
    # Reordena somente os conjuntos da expansão, em ordem alfabética, após os
    # conjuntos originais do manifesto.
    originais = {
        chave: valor
        for chave, valor in fontes_json["conjuntos"].items()
        if not chave.startswith(PREFIXO_CONJUNTO)
    }
    expansao = {
        chave: fontes_json["conjuntos"][chave]
        for chave in sorted(fontes_json["conjuntos"])
        if chave.startswith(PREFIXO_CONJUNTO)
    }
    fontes_json["conjuntos"] = {**originais, **expansao}
    salvar_json(FONTES_PATH, fontes_json)

    todos_materializados = normas_dos_grupos(
        normas, grupos_materializados(fontes_json)
    )
    criados = 0
    for norma in todos_materializados:
        destino = DATA / f"lei_{id_da_sigla(norma['sigla'])}.json"
        if not destino.exists():
            salvar_json(destino, stub_da_norma(norma))
            criados += 1

    fonte = LEGISLACAO_TS.read_text(encoding="utf-8")
    novo_bloco = bloco_ts(todos_materializados)
    atual = bloco_ts_atual()
    if atual is None:
        raise ValueError(
            "marcadores da expansão não encontrados em legislacao.ts; "
            "acrescente as linhas de [expansao:inicio] e [expansao:fim] dentro "
            "de REGISTRO_CODIGOS"
        )
    LEGISLACAO_TS.write_text(fonte.replace(atual, novo_bloco), encoding="utf-8")
    print(
        f"materializados: {', '.join(grupos)} | stubs novos: {criados} | "
        f"grupos no total: {len(grupos_materializados(fontes_json))}"
    )


def verificar() -> list[str]:
    problemas: list[str] = []
    normas = carregar_normas()
    fontes_json = carregar_json(FONTES_PATH)
    materializados = grupos_materializados(fontes_json)
    por_grupo = grupos_do_manifesto(normas)
    for grupo in materializados:
        if grupo not in por_grupo:
            problemas.append(f"conjunto {PREFIXO_CONJUNTO}{grupo} não existe no manifesto")
            continue
        esperado = conjunto_esperado(por_grupo[grupo])
        real = fontes_json["conjuntos"][PREFIXO_CONJUNTO + grupo]
        if real != esperado:
            problemas.append(
                f"{PREFIXO_CONJUNTO}{grupo}: conjunto em fontes.json diverge do manifesto"
            )
    normas_materializadas = (
        normas_dos_grupos(normas, [g for g in materializados if g in por_grupo])
        if materializados
        else []
    )
    for norma in normas_materializadas:
        destino = DATA / f"lei_{id_da_sigla(norma['sigla'])}.json"
        if not destino.exists():
            problemas.append(f"{norma['sigla']}: {destino.name} não existe em data/")
    esperado_ts = bloco_ts(normas_materializadas)
    atual_ts = bloco_ts_atual()
    if atual_ts is None:
        problemas.append("marcadores da expansão ausentes em legislacao.ts")
    elif atual_ts != esperado_ts:
        problemas.append("bloco gerado em legislacao.ts diverge do manifesto")
    return problemas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    grupo_acao = parser.add_mutually_exclusive_group(required=True)
    grupo_acao.add_argument(
        "--materializar",
        help="grupos do manifesto a materializar, separados por vírgula",
    )
    grupo_acao.add_argument(
        "--verificar",
        action="store_true",
        help="confere a sincronia dos grupos materializados sem escrever nada",
    )
    grupo_acao.add_argument(
        "--listar", action="store_true", help="lista grupos do manifesto e estado"
    )
    args = parser.parse_args()

    if args.listar:
        normas = carregar_normas()
        materializados = set(grupos_materializados(carregar_json(FONTES_PATH)))
        for grupo, itens in sorted(grupos_do_manifesto(normas).items()):
            estado = "materializado" if grupo in materializados else "pendente"
            print(f"{grupo}: {len(itens)} normas [{estado}]")
        return 0
    if args.verificar:
        problemas = verificar()
        if problemas:
            print("divergências encontradas:")
            for problema in problemas:
                print(f"- {problema}")
            return 1
        print("expansão sincronizada: manifesto, fontes.json, legislacao.ts e data/.")
        return 0
    materializar([g.strip() for g in args.materializar.split(",") if g.strip()])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        raise SystemExit(1)
