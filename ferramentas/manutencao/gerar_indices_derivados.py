#!/usr/bin/env python3
"""Gera índices locais de palavras-chave a partir dos textos publicados.

Duas famílias de saída, ambas determinísticas e sem modelo de linguagem:

- súmulas (`tokens-significativos-v1`): tokens dos enunciados, sem stopwords,
  um arquivo derivado por conjunto;
- legislação (`tokens-texto-integral-v1`): tokens dos dispositivos que o índice
  curado (`indexes.keywords`) não cobre, preservando as stopwords para manter
  fidelidade à busca em texto integral do motor; um arquivo derivado por
  diploma em `data/indices/`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFESTO_PADRAO = ROOT / "base-juridica" / "indices-derivados.json"
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = frozenset(
    {
        "a", "o", "e", "de", "da", "do", "das", "dos", "em", "no", "na",
        "nos", "nas", "por", "para", "com", "sem", "que", "se", "ou", "um",
        "uma", "uns", "umas", "ao", "aos", "pelo", "pela", "pelos", "pelas",
        "este", "esta", "esse", "essa", "seu", "sua", "seus", "suas", "como",
        "mais", "qual", "quais", "sobre", "sob", "entre", "ser", "ter", "haver",
        "fazer", "poder", "dever", "apos",
    }
)


def carregar_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def carregar_manifesto(path: Path = MANIFESTO_PADRAO) -> dict[str, Any]:
    dados = carregar_json(path)
    if dados.get("schema_version") != 2:
        raise ValueError("versão desconhecida do manifesto de índices")
    gerador = dados.get("gerador", {})
    if gerador.get("algoritmo") != "tokens-significativos-v1":
        raise ValueError("algoritmo de índices não suportado")
    if gerador.get("modelo") is not None or gerador.get("prompt") is not None:
        raise ValueError("o gerador local não aceita modelo ou prompt externos")
    legislacao = dados.get("legislacao", {})
    if legislacao.get("gerador", {}).get("algoritmo") != "tokens-texto-integral-v1":
        raise ValueError("algoritmo de índices de legislação não suportado")
    gerador_leg = legislacao["gerador"]
    if gerador_leg.get("modelo") is not None or gerador_leg.get("prompt") is not None:
        raise ValueError("o gerador local não aceita modelo ou prompt externos")
    return dados


def normalizar(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto.casefold())
    return "".join(
        caractere
        for caractere in decomposto
        if unicodedata.category(caractere) != "Mn"
    )


def tokens_significativos(textos: list[str], tamanho_minimo: int) -> list[str]:
    vistos: set[str] = set()
    tokens: list[str] = []
    for texto in textos:
        for token in TOKEN_RE.findall(normalizar(texto)):
            if len(token) < tamanho_minimo or token in STOPWORDS or token in vistos:
                continue
            vistos.add(token)
            tokens.append(token)
    return tokens


def tokens_texto_integral(texto: str, tamanho_minimo: int) -> list[str]:
    """Tokens do texto sem remover stopwords, na ordem da primeira ocorrência.

    As stopwords são preservadas porque o motor casa as palavras da consulta
    contra estes tokens exatamente como a busca em texto integral casaria
    contra o texto publicado; removê-las mudaria ranking e piso de corte.
    Tokens abaixo do tamanho mínimo nunca casariam com uma palavra de consulta
    (o motor descarta palavras com menos de três caracteres) e ficam de fora.
    """
    vistos: set[str] = set()
    tokens: list[str] = []
    for token in TOKEN_RE.findall(normalizar(texto)):
        if len(token) < tamanho_minimo or token in vistos:
            continue
        vistos.add(token)
        tokens.append(token)
    return tokens


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def gerar_conjunto(
    manifesto: dict[str, Any],
    nome: str,
    config: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    diretorio = ROOT / manifesto["diretorio_dados"]
    fonte_path = diretorio / config["fonte"]
    destino_path = diretorio / config["destino"]
    fonte = carregar_json(fonte_path)
    registros = fonte[config["colecao"]]
    parametros = manifesto["gerador"]["parametros"]
    tamanho_minimo = int(parametros["tamanho_minimo_token"])

    indice: dict[str, dict[str, Any]] = {}
    for chave, registro in sorted(
        registros.items(), key=lambda item: int(item[1]["numero"])
    ):
        numero = int(registro["numero"])
        identificador = f'{config["prefixo_id"]}_{numero:03d}'
        item = {campo: registro[campo] for campo in config["campos_copiados"]}
        textos = [str(registro.get(campo, "")) for campo in config["campos_texto"]]
        item["keywords"] = tokens_significativos(textos, tamanho_minimo)
        if not item["keywords"]:
            raise ValueError(f"{nome}:{chave} não produziu palavra-chave")
        indice[identificador] = item

    meta_fonte = fonte.get("_meta", {})
    saida = {
        "_meta": {
            "schema_version": 2,
            "tipo": "indice_derivado",
            "total_sumulas": len(indice),
            "gerado_em": manifesto["gerado_em"],
            "gerador": manifesto["gerador"],
            "fonte": {
                "arquivo": config["fonte"],
                "colecao": config["colecao"],
                "sha256": sha256(fonte_path),
                "total_registros": len(registros),
                "gerado_em": meta_fonte.get("gerado_em"),
            },
            "relacao": {
                "chave": "numero",
                "cobertura": "1:1",
            },
        },
        "keywords": indice,
    }
    return destino_path, saida


def numeros_no_indice_curado(dados: dict[str, Any]) -> set[str]:
    curado = (dados.get("indexes") or {}).get("keywords") or {}
    numeros: set[str] = set()
    for lista in curado.values():
        numeros.update(str(numero) for numero in lista)
    return numeros


def gerar_diploma(
    manifesto: dict[str, Any],
    fonte_path: Path,
) -> tuple[Path, dict[str, Any]]:
    config = manifesto["legislacao"]
    fonte = carregar_json(fonte_path)
    artigos = fonte["artigos"]
    curados = numeros_no_indice_curado(fonte)
    fantasmas = curados - set(artigos)
    if fantasmas:
        raise ValueError(
            f"{fonte_path.name}: índice curado aponta dispositivos inexistentes: "
            + ", ".join(sorted(fantasmas))
        )

    tamanho_minimo = int(config["gerador"]["parametros"]["tamanho_minimo_token"])
    tokens: dict[str, str] = {}
    for numero, artigo in artigos.items():
        if numero in curados:
            continue
        encontrados = tokens_texto_integral(str(artigo["texto"]), tamanho_minimo)
        if not encontrados:
            raise ValueError(f"{fonte_path.name}:{numero} não produziu token")
        tokens[numero] = " ".join(encontrados)

    meta_fonte = fonte.get("_meta", {})
    destino = fonte_path.parent / config["subdiretorio_destino"] / (
        fonte_path.stem + config["sufixo_destino"]
    )
    saida = {
        "_meta": {
            "schema_version": 2,
            "tipo": "indice_derivado",
            "codigo": meta_fonte.get("codigo"),
            "gerado_em": config["gerado_em"],
            "gerador": config["gerador"],
            "fonte": {
                "arquivo": fonte_path.name,
                "colecao": "artigos",
                "sha256": sha256(fonte_path),
                "total_registros": len(artigos),
                "gerado_em": meta_fonte.get("gerado_em"),
            },
            "relacao": {
                "chave": "numero",
                "cobertura": (
                    "complementar ao índice curado indexes.keywords; "
                    "a união cobre todos os dispositivos publicados (1:1)"
                ),
                "dispositivos_indexados": len(tokens),
                "dispositivos_no_indice_curado": len(curados),
            },
        },
        "tokens": tokens,
    }
    return destino, saida


def gerar_legislacao(
    manifesto: dict[str, Any],
) -> list[tuple[Path, dict[str, Any]]]:
    config = manifesto["legislacao"]
    diretorio = ROOT / manifesto["diretorio_dados"]
    fontes = sorted(diretorio.glob(config["padrao_fonte"]))
    if not fontes:
        raise ValueError("nenhum diploma encontrado para indexar")
    return [gerar_diploma(manifesto, fonte_path) for fonte_path in fontes]


def gerar_todos(
    manifesto_path: Path = MANIFESTO_PADRAO,
) -> list[tuple[Path, dict[str, Any]]]:
    manifesto = carregar_manifesto(manifesto_path)
    saidas = [
        gerar_conjunto(manifesto, nome, config)
        for nome, config in manifesto["conjuntos"].items()
    ]
    saidas.extend(gerar_legislacao(manifesto))
    return saidas


def serializar(objeto: dict[str, Any]) -> str:
    return json.dumps(objeto, ensure_ascii=False, indent=2) + "\n"


def escrever(manifesto_path: Path) -> int:
    for destino, objeto in gerar_todos(manifesto_path):
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(serializar(objeto), encoding="utf-8")
        print(f"Gerado: {destino.relative_to(ROOT)}")
    return 0


def verificar(manifesto_path: Path) -> int:
    divergentes: list[Path] = []
    for destino, objeto in gerar_todos(manifesto_path):
        esperado = serializar(objeto)
        atual = destino.read_text(encoding="utf-8") if destino.exists() else ""
        if atual != esperado:
            divergentes.append(destino)
        else:
            print(f"Reproduzível: {destino.relative_to(ROOT)}")
    if divergentes:
        for path in divergentes:
            print(f"Divergente: {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--escrever", action="store_true")
    grupo.add_argument("--verificar", action="store_true")
    parser.add_argument("--manifesto", type=Path, default=MANIFESTO_PADRAO)
    args = parser.parse_args()
    return escrever(args.manifesto) if args.escrever else verificar(args.manifesto)


if __name__ == "__main__":
    raise SystemExit(main())
