#!/usr/bin/env python3
"""Audita estrutura, cobertura e metadados da base jurídica local.

O script não confirma vigência nem compara o conteúdo com fontes externas. Ele mede
o que existe no repositório e aponta inconsistências reproduzíveis.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MOTOR = ROOT / "ferramentas" / "pesquisa" / "busca_delfus"
DATA = MOTOR / "data"


def carregar(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def caminhos_absolutos(valor: Any, prefixo: str = "") -> list[str]:
    encontrados: list[str] = []
    if isinstance(valor, dict):
        for chave, item in valor.items():
            caminho = f"{prefixo}.{chave}" if prefixo else chave
            encontrados.extend(caminhos_absolutos(item, caminho))
    elif isinstance(valor, list):
        for indice, item in enumerate(valor):
            encontrados.extend(caminhos_absolutos(item, f"{prefixo}[{indice}]"))
    elif isinstance(valor, str) and valor.startswith("/"):
        encontrados.append(f"{prefixo}={valor}")
    return encontrados


def auditar() -> dict[str, Any]:
    achados: list[dict[str, str]] = []

    def registrar(prioridade: str, codigo: str, mensagem: str) -> None:
        achados.append(
            {"prioridade": prioridade, "codigo": codigo, "mensagem": mensagem}
        )

    legislacao: list[dict[str, Any]] = []
    for path in sorted(DATA.glob("lei_*.json")):
        dados = carregar(path)
        meta = dados.get("_meta", {})
        artigos = dados.get("artigos", {})
        quantidade = len(artigos)
        quantidade_meta = meta.get("total_artigos")
        com_url = sum(bool(item.get("url")) for item in artigos.values())
        com_keywords = sum(bool(item.get("keywords")) for item in artigos.values())
        codigo = str(meta.get("codigo", path.stem.removeprefix("lei_").upper()))

        if quantidade_meta != quantidade:
            registrar(
                "P1",
                "CONTAGEM_LEGISLACAO",
                f"{codigo}: metadado informa {quantidade_meta}, arquivo contém {quantidade}.",
            )
        if com_url != quantidade:
            registrar(
                "P0",
                "URL_LEGISLACAO",
                f"{codigo}: {quantidade - com_url} registros não têm URL de origem.",
            )

        legislacao.append(
            {
                "arquivo": path.name,
                "codigo": codigo,
                "nome": meta.get("nome"),
                "diploma": meta.get("lei"),
                "gerado_em": meta.get("gerado_em"),
                "versao": meta.get("version"),
                "registros": quantidade,
                "registros_meta": quantidade_meta,
                "registros_com_url": com_url,
                "registros_com_keywords": com_keywords,
                "indice_precomputado": bool(dados.get("indexes")),
                "url_base": meta.get("url_base"),
            }
        )

    sumulas: list[dict[str, Any]] = []
    especificacoes = (
        ("sumulas_stj.json", "STJ"),
        ("sumulas_stf.json", "STF"),
        ("sumulas_vinculantes.json", "STF vinculantes"),
    )
    for nome_arquivo, nome_conjunto in especificacoes:
        path = DATA / nome_arquivo
        dados = carregar(path)
        meta = dados.get("_meta", {})
        registros = dados.get("sumulas", {})
        quantidade = len(registros)
        com_url = sum(bool(item.get("url")) for item in registros.values())
        status = Counter(item.get("status", "sem_status") for item in registros.values())

        if meta.get("total") != quantidade:
            registrar(
                "P1",
                "CONTAGEM_SUMULAS",
                f"{nome_conjunto}: metadado informa {meta.get('total')}, arquivo contém {quantidade}.",
            )
        if com_url != quantidade:
            registrar(
                "P0",
                "URL_SUMULAS",
                f"{nome_conjunto}: {quantidade - com_url} registros não têm URL oficial.",
            )

        sumulas.append(
            {
                "arquivo": nome_arquivo,
                "conjunto": nome_conjunto,
                "gerado_em": meta.get("gerado_em"),
                "registros": quantidade,
                "registros_com_url": com_url,
                "status": dict(sorted(status.items())),
            }
        )

    jt = carregar(DATA / "jt_stj.json")
    teses = jt.get("teses", {})
    edicoes = {item.get("edicao") for item in teses.values()}
    teses_sem_enunciado = [
        chave for chave, item in teses.items() if not item.get("enunciado")
    ]
    teses_sem_url = [chave for chave, item in teses.items() if not item.get("url")]
    if len(teses) != jt.get("_meta", {}).get("total_teses"):
        registrar(
            "P1",
            "CONTAGEM_TESES",
            "A quantidade de teses diverge do metadado.",
        )
    if len(edicoes) != jt.get("_meta", {}).get("total_edicoes"):
        registrar(
            "P1",
            "CONTAGEM_EDICOES",
            "A quantidade de edições diverge do metadado.",
        )
    if teses_sem_enunciado:
        registrar(
            "P1",
            "TESE_VAZIA",
            f"Teses sem enunciado: {', '.join(teses_sem_enunciado)}.",
        )
    if teses_sem_url:
        registrar(
            "P0",
            "URL_TESES",
            f"{len(teses_sem_url)} teses não têm URL oficial.",
        )

    temas_raw = carregar(DATA / "flash_temas_stj.json")
    temas = temas_raw.get("temas", {})
    temas_sem_pagina = [
        chave
        for chave, item in temas.items()
        if not item.get("links", {}).get("paginaTema")
    ]
    if len(temas) != temas_raw.get("_meta", {}).get("totalTemas"):
        registrar(
            "P1",
            "CONTAGEM_TEMAS",
            "A quantidade de temas diverge do metadado.",
        )
    if temas_sem_pagina:
        registrar(
            "P0",
            "URL_TEMAS",
            f"{len(temas_sem_pagina)} temas não têm página oficial.",
        )

    absolutos = caminhos_absolutos(temas_raw.get("_meta", {}))
    if absolutos:
        registrar(
            "P1",
            "CAMINHO_LOCAL",
            "Metadados de temas contêm caminhos absolutos do computador de origem.",
        )

    legislacao_ts = (MOTOR / "src" / "search" / "legislacao.ts").read_text(
        encoding="utf-8"
    )
    declarados = dict(
        re.findall(
            r'^\s{2}([A-Z]+):\s*\{\s*arquivo:\s*"\.\./\.\./data/(lei_[^"]+\.json)"',
            legislacao_ts,
            re.MULTILINE,
        )
    )
    if not declarados:
        # Compatibilidade com o registro simples usado antes da centralização.
        declarados = dict(
            re.findall(
                r'^\s{2}([A-Z]+):\s+"\.\./\.\./data/(lei_[^"]+\.json)"',
                legislacao_ts,
                re.MULTILINE,
            )
        )
    ausentes = [
        codigo for codigo, arquivo in declarados.items() if not (DATA / arquivo).exists()
    ]
    for codigo in ausentes:
        registrar(
            "P0",
            "ARQUIVO_DECLARADO_AUSENTE",
            f"{codigo} está declarado no motor, mas seu arquivo JSON não existe.",
        )

    usa_registro_central = bool(
        re.search(
            r'codigo === "todos"\s*\?\s*CODIGOS_DISPONIVEIS',
            legislacao_ts,
        )
    )
    match_todos = re.search(
        r'codigo === "todos"\s*\?\s*\[([^]]+)\]', legislacao_ts, re.DOTALL
    )
    if usa_registro_central:
        codigos_todos = [
            codigo
            for codigo, arquivo in declarados.items()
            if (DATA / arquivo).exists()
        ]
    else:
        codigos_todos = (
            re.findall(r'"([A-Z]+)"', match_todos.group(1)) if match_todos else []
        )
    disponiveis = [item["codigo"] for item in legislacao]
    fora_de_todos = sorted(set(disponiveis) - set(codigos_todos))
    if fora_de_todos:
        registrar(
            "P0",
            "COBERTURA_TODOS",
            "Busca legislativa 'todos' exclui: " + ", ".join(fora_de_todos) + ".",
        )

    index_ts = (MOTOR / "src" / "index.ts").read_text(encoding="utf-8")
    descricao_edicoes = re.search(
        r"([\d.]+) teses de ([\d.]+) edições", index_ts
    )
    edicoes_descritas = (
        int(descricao_edicoes.group(2).replace(".", ""))
        if descricao_edicoes
        else None
    )
    if edicoes_descritas is not None and edicoes_descritas != len(edicoes):
        registrar(
            "P1",
            "DESCRICAO_MCP",
            f"Descrição MCP informa {edicoes_descritas} edições; a base contém {len(edicoes)}.",
        )

    formatadores = (
        (
            "SÚMULAS",
            MOTOR / "src" / "search" / "sumulas.ts",
            "export function formatSumula",
            ("s.url", "sumula.url"),
        ),
        (
            "TESES",
            MOTOR / "src" / "search" / "jt.ts",
            "export function formatTese",
            ("tese.url",),
        ),
        (
            "TEMAS",
            MOTOR / "src" / "search" / "temas.ts",
            "export function formatTema",
            ("tema.links",),
        ),
    )
    for conjunto, path, marcador, referencias in formatadores:
        fonte = path.read_text(encoding="utf-8")
        corpo = fonte.split(marcador, 1)[1] if marcador in fonte else ""
        if not any(referencia in corpo for referencia in referencias):
            registrar(
                "P0",
                "URL_OMITIDA_NA_SAIDA",
                f"Formatador de {conjunto.lower()} não inclui a URL oficial disponível no JSON.",
            )

    superficies_taxonomia = tuple(
        MOTOR / caminho
        for caminho in (
            "package.json",
            "src/index.ts",
            "src/search/legislacao.ts",
            "src/search/sumulas.ts",
            "src/search/jt.ts",
            "src/search/temas.ts",
        )
    )
    rotulos_ambiguos = (
        "FONTE PRIMÁRIA",
        "**Força:**",
        "| PERSUASIVA",
        "| ORIENTATIVA",
    )
    for path in superficies_taxonomia:
        fonte = path.read_text(encoding="utf-8")
        encontrados = [rotulo for rotulo in rotulos_ambiguos if rotulo in fonte]
        if encontrados:
            registrar(
                "P1",
                "TAXONOMIA_JURIDICA",
                f"{path.relative_to(ROOT)} ainda usa rótulos ambíguos: "
                + ", ".join(encontrados)
                + ".",
            )

    return {
        "auditado_em": date.today().isoformat(),
        "escopo": "estrutura local; sem confirmação externa de vigência ou conteúdo",
        "inventario": {
            "arquivos_json": len(list(DATA.glob("*.json"))),
            "tamanho_bytes": sum(path.stat().st_size for path in DATA.glob("*.json")),
            "legislacao": legislacao,
            "total_registros_legislacao": sum(
                item["registros"] for item in legislacao
            ),
            "sumulas": sumulas,
            "total_sumulas": sum(item["registros"] for item in sumulas),
            "jurisprudencia_em_teses": {
                "arquivo": "jt_stj.json",
                "gerado_em": jt.get("_meta", {}).get("gerado_em"),
                "edicoes": len(edicoes),
                "teses": len(teses),
                "teses_com_url": len(teses) - len(teses_sem_url),
                "teses_sem_enunciado": teses_sem_enunciado,
            },
            "temas_repetitivos": {
                "arquivo": "flash_temas_stj.json",
                "gerado_em": temas_raw.get("_meta", {}).get("generatedAt"),
                "temas": len(temas),
                "temas_com_pagina_oficial": len(temas) - len(temas_sem_pagina),
                "status": dict(
                    sorted(
                        Counter(
                            item.get("situacao", "sem_status")
                            for item in temas.values()
                        ).items()
                    )
                ),
                "caminhos_absolutos_no_meta": absolutos,
            },
            "motor_legislacao": {
                "codigos_declarados": sorted(declarados),
                "codigos_com_arquivo": sorted(disponiveis),
                "codigos_na_busca_todos": codigos_todos,
                "codigos_fora_da_busca_todos": fora_de_todos,
                "codigos_sem_arquivo": ausentes,
            },
        },
        "achados": achados,
    }


def imprimir_relatorio(relatorio: dict[str, Any]) -> None:
    inventario = relatorio["inventario"]
    print("Auditoria estrutural da base jurídica")
    print(f"Data: {relatorio['auditado_em']}")
    print(f"Escopo: {relatorio['escopo']}")
    print(
        "Inventário: "
        f"{inventario['arquivos_json']} JSON; "
        f"{inventario['total_registros_legislacao']} registros legislativos; "
        f"{inventario['total_sumulas']} súmulas; "
        f"{inventario['jurisprudencia_em_teses']['teses']} teses; "
        f"{inventario['temas_repetitivos']['temas']} temas."
    )
    print()
    if not relatorio["achados"]:
        print("Nenhuma inconsistência estrutural encontrada.")
        return
    print("Achados:")
    for achado in relatorio["achados"]:
        print(
            f"- [{achado['prioridade']}] {achado['codigo']}: "
            f"{achado['mensagem']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="imprime o relatório em JSON"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="retorna código 1 quando houver qualquer achado",
    )
    args = parser.parse_args()

    relatorio = auditar()
    if args.json:
        print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    else:
        imprimir_relatorio(relatorio)

    return 1 if args.strict and relatorio["achados"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
