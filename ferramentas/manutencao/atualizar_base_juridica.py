#!/usr/bin/env python3
"""Coleta, transforma, valida e compara snapshots da base jurídica.

O comando nunca altera os dados publicados durante ``executar``, ``coletar`` ou
``transformar``. A cópia para o diretório consumido pelo motor exige a ação
``promover`` e a confirmação literal ``PROMOVER``.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Iterator
from urllib.parse import quote, urljoin, urlparse


# Páginas antigas do Planalto acumulam milhares de tags inline sem fechamento
# (ex.: Decreto-Lei 1.001/1969, árvore com profundidade ~1.700); os percursos
# recursivos da árvore precisam de limite maior que o padrão do interpretador.
sys.setrecursionlimit(50000)

ROOT = Path(__file__).resolve().parents[2]
MANIFESTO_PADRAO = ROOT / "base-juridica" / "fontes.json"
AREA_PADRAO = ROOT / ".atualizacao-base-juridica"
USER_AGENT = (
    "Mozilla/5.0 (compatible; Advocacia-Aberta/1.0; "
    "+https://github.com/emidio-a11y/advocacia-aberta)"
)
ADAPTADORES = {
    "planalto_html_v1",
    "sumulas_stj_html_v1",
    "sumulas_stf_html_v1",
    "jt_stj_html_v1",
    "temas_stj_csv_v1",
}
HOSTS_OFICIAIS = {
    "www.planalto.gov.br",
    "planalto.gov.br",
    "processo.stj.jus.br",
    "scon.stj.jus.br",
    "www.stj.jus.br",
    "ww2.stj.jus.br",
    "dadosabertos.web.stj.jus.br",
    "portal.stf.jus.br",
    "jurisprudencia.stf.jus.br",
}
LIMITE_MUDANCA_PERCENTUAL_PADRAO = 25
LIMITE_MUDANCA_MINIMO_PADRAO = 20
TIPOS_CONTEUDO_ESPERADOS = {
    ".html": {"text/html", "application/xhtml+xml"},
    ".csv": {"text/csv", "application/csv", "application/octet-stream"},
    ".json": {"application/json", "text/json"},
}


def agora_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def hoje() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def carregar_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as arquivo:
        valor = json.load(arquivo)
    if not isinstance(valor, dict):
        raise ValueError(f"{path}: a raiz do JSON precisa ser um objeto")
    return valor


def salvar_json(path: Path, valor: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporario = path.with_suffix(path.suffix + ".tmp")
    temporario.write_text(
        json.dumps(valor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporario.replace(path)


def texto_normalizado(valor: str) -> str:
    return re.sub(r"\s+", " ", unescape(valor).replace("\u200b", "")).strip()


def decodificar_html(path: Path) -> str:
    bruto = path.read_bytes()
    if bruto.startswith((b"\xff\xfe", b"\xfe\xff")):
        # O Planalto publica algumas páginas em UTF-16 com BOM (ex.: Lei
        # 11.340/2006); o BOM prevalece sobre o charset declarado no HTML.
        # Um byte solto ao final (fora do fluxo de pares UTF-16) é descartado.
        return bruto[: len(bruto) - (len(bruto) % 2)].decode("utf-16")
    inicio = bruto[:4096].decode("ascii", errors="ignore")
    charset = re.search(r"charset\s*=\s*[\"']?([\w-]+)", inicio, re.IGNORECASE)
    candidatos = [charset.group(1)] if charset else []
    candidatos.extend(["utf-8-sig", "cp1252", "latin-1"])
    for encoding in candidatos:
        try:
            return bruto.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return bruto.decode("utf-8", errors="replace")


@dataclass
class Elemento:
    tag: str
    atributos: dict[str, str] = field(default_factory=dict)
    pai: Elemento | None = None
    filhos: list[Elemento | str] = field(default_factory=list)

    @property
    def classes(self) -> set[str]:
        return set(self.atributos.get("class", "").split())


class ArvoreHTML(HTMLParser):
    VAZIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    BLOCOS = {"blockquote", "body", "div", "documento", "html", "li", "ol", "p", "table", "tbody", "td", "th", "tr", "ul"}
    INLINE = {"a", "b", "del", "em", "font", "i", "s", "small", "span", "strike", "strong", "sub", "sup", "u"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.raiz = Elemento("documento")
        self.pilha = [self.raiz]

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag.lower() == "p":
            # Um novo <p> fecha implicitamente o <p> anterior não fechado,
            # como no HTML5; o Planalto publica parágrafos sem </p>.
            for indice in range(len(self.pilha) - 1, 0, -1):
                if self.pilha[indice].tag == "p":
                    del self.pilha[indice:]
                    break
                if self.pilha[indice].tag in self.BLOCOS:
                    break
        elemento = Elemento(
            tag.lower(), {chave: valor or "" for chave, valor in attrs}, self.pilha[-1]
        )
        self.pilha[-1].filhos.append(elemento)
        if tag.lower() not in self.VAZIOS:
            self.pilha.append(elemento)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VAZIOS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for indice in range(len(self.pilha) - 1, 0, -1):
            if self.pilha[indice].tag == tag:
                del self.pilha[indice:]
                return
            if tag in self.INLINE and self.pilha[indice].tag in self.BLOCOS:
                # Fechamento órfão de tag inline (comum no HTML do Planalto)
                # não pode derrubar o bloco que contém o texto.
                return

    def handle_data(self, data: str) -> None:
        if data:
            self.pilha[-1].filhos.append(data)


def analisar_html(conteudo: str) -> Elemento:
    parser = ArvoreHTML()
    parser.feed(conteudo)
    return parser.raiz


def percorrer(no: Elemento) -> Iterator[Elemento]:
    yield no
    for filho in no.filhos:
        if isinstance(filho, Elemento):
            yield from percorrer(filho)


def buscar(
    no: Elemento, *, tag: str | None = None, classe: str | None = None
) -> Iterator[Elemento]:
    for item in percorrer(no):
        if tag is not None and item.tag != tag:
            continue
        if classe is not None and classe not in item.classes:
            continue
        yield item


def primeiro(
    no: Elemento, *, tag: str | None = None, classe: str | None = None
) -> Elemento | None:
    return next(buscar(no, tag=tag, classe=classe), None)


def texto_elemento(no: Elemento, preservar_linhas: bool = False) -> str:
    partes: list[str] = []

    def visitar(item: Elemento | str) -> None:
        if isinstance(item, str):
            partes.append(item)
            return
        if item.tag in {"script", "style", "noscript"}:
            return
        if item.tag == "br":
            partes.append("\n")
            return
        for filho in item.filhos:
            visitar(filho)
        if item.tag in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4"}:
            partes.append("\n")

    visitar(no)
    texto = unescape("".join(partes)).replace("\xa0", " ").replace("\u200b", "")
    if not preservar_linhas:
        return texto_normalizado(texto)
    linhas = [texto_normalizado(linha) for linha in texto.splitlines()]
    return "\n".join(linha for linha in linhas if linha)


def tem_ancestral_riscado(no: Elemento) -> bool:
    atual: Elemento | None = no
    while atual is not None:
        estilo = atual.atributos.get("style", "").lower()
        if atual.tag in {"s", "strike", "del"} or "line-through" in estilo:
            return True
        atual = atual.pai
    return False


def ler_cabecalhos(path: Path) -> dict[str, str]:
    texto = path.read_text(encoding="latin-1", errors="replace")
    blocos = re.split(r"\r?\n\r?\n", texto.strip())
    ultimo = next((bloco for bloco in reversed(blocos) if bloco.startswith("HTTP/")), "")
    resultado: dict[str, str] = {}
    for linha in ultimo.splitlines()[1:]:
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            resultado[chave.lower().strip()] = valor.strip()
    return resultado


def validar_url_oficial(url: str) -> None:
    try:
        partes = urlparse(url)
        porta = partes.port
    except ValueError as erro:
        raise ValueError(f"URL de coleta inválida: {url}") from erro
    host = (partes.hostname or "").lower()
    if (
        partes.scheme.lower() != "https"
        or host not in HOSTS_OFICIAIS
        or porta not in (None, 443)
        or partes.username is not None
        or partes.password is not None
    ):
        raise ValueError(f"URL de coleta fora dos domínios oficiais: {url}")


def validar_tipo_conteudo(destino: Path, content_type: str | None) -> None:
    esperados = TIPOS_CONTEUDO_ESPERADOS.get(destino.suffix.lower())
    if not esperados:
        return
    recebido = (content_type or "").split(";", 1)[0].strip().lower()
    if recebido not in esperados:
        raise RuntimeError(
            f"tipo de conteúdo inesperado para {destino.name}: "
            f"{content_type or 'ausente'}"
        )


def baixar(url: str, destino: Path) -> dict[str, Any]:
    validar_url_oficial(url)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(destino.suffix + ".part")
    cabecalhos_path = destino.with_suffix(destino.suffix + ".headers")
    comando = [
        "curl",
        "--location",
        "--fail",
        "--silent",
        "--show-error",
        "--compressed",
        "--retry",
        "3",
        "--retry-all-errors",
        "--connect-timeout",
        "20",
        "--max-time",
        "180",
        "--user-agent",
        USER_AGENT,
        "--dump-header",
        str(cabecalhos_path),
        "--write-out",
        "%{url_effective}",
        "--output",
        str(temporario),
        url,
    ]
    resultado = subprocess.run(
        comando, check=True, capture_output=True, text=True
    )
    url_efetiva = resultado.stdout.strip() or url
    try:
        validar_url_oficial(url_efetiva)
    except ValueError:
        temporario.unlink(missing_ok=True)
        cabecalhos_path.unlink(missing_ok=True)
        raise
    if not temporario.exists() or temporario.stat().st_size == 0:
        raise RuntimeError(f"download vazio: {url}")
    cabecalhos = ler_cabecalhos(cabecalhos_path)
    try:
        validar_tipo_conteudo(destino, cabecalhos.get("content-type"))
    except RuntimeError:
        temporario.unlink(missing_ok=True)
        cabecalhos_path.unlink(missing_ok=True)
        raise
    temporario.replace(destino)
    return {
        "url": url,
        "url_efetiva": url_efetiva,
        "arquivo": str(destino),
        "coletado_em": agora_utc(),
        "bytes": destino.stat().st_size,
        "sha256": sha256(destino),
        "etag": cabecalhos.get("etag"),
        "last_modified": cabecalhos.get("last-modified"),
        "content_type": cabecalhos.get("content-type"),
    }


def manifesto(path: Path = MANIFESTO_PADRAO) -> dict[str, Any]:
    dados = carregar_json(path)
    if dados.get("schema_version") != 1:
        raise ValueError("versão desconhecida do manifesto de fontes")
    politica = dados.get("politica_promocao")
    if not isinstance(politica, dict):
        raise ValueError("política de promoção ausente no manifesto")
    percentual = politica.get("limite_mudanca_percentual")
    minimo = politica.get("limite_mudanca_minimo")
    if (
        not isinstance(percentual, int)
        or isinstance(percentual, bool)
        or not 1 <= percentual <= 100
        or not isinstance(minimo, int)
        or isinstance(minimo, bool)
        or minimo < 1
    ):
        raise ValueError("limites inválidos na política de promoção")
    return dados


def ids_selecionados(dados: dict[str, Any], selecao: str) -> list[str]:
    conjuntos = dados["conjuntos"]
    if selecao == "todos":
        return [chave for chave, valor in conjuntos.items() if valor.get("adaptador")]
    ids = [item.strip() for item in selecao.split(",") if item.strip()]
    invalidos = sorted(set(ids) - set(conjuntos))
    if invalidos:
        raise ValueError("conjuntos desconhecidos: " + ", ".join(invalidos))
    derivados = [item for item in ids if not conjuntos[item].get("adaptador")]
    if derivados:
        raise ValueError(
            "conjuntos sem adaptador neste pipeline: " + ", ".join(derivados)
        )
    return ids


def caminho_execucao(area: Path, execucao: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", execucao):
        raise ValueError("o identificador da execução aceita letras, números, ponto, _ e -")
    return area.resolve() / execucao


def carregar_recibo(execucao_dir: Path, versao: str) -> dict[str, Any]:
    path = execucao_dir / "execucao.json"
    if path.exists():
        return carregar_json(path)
    return {
        "pipeline_version": versao,
        "iniciada_em": agora_utc(),
        "conjuntos": {},
    }


def extrair_catalogo_stf(conteudo: str, vinculante: bool) -> list[dict[str, Any]]:
    base = "26" if vinculante else "30"
    padrao = re.compile(
        rf'<div class="sumula-item">\s*<a[^>]+href="([^"]*base={base}(?:&|&amp;)sumula=(\d+)[^"]*)"[^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    itens: list[dict[str, Any]] = []
    for href, identificador, corpo in padrao.findall(conteudo):
        rotulo = texto_normalizado(re.sub(r"<[^>]+>", " ", corpo))
        numero_match = re.search(r"(\d+)", rotulo)
        if not numero_match:
            continue
        status = "aprovada" if vinculante else "ativa"
        rotulo_status = rotulo.lower()
        for marcador, estado in (
            ("cancelada", "cancelada"),
            ("revogada", "cancelada"),
            ("superada", "superada"),
            ("alterada", "alterada"),
            ("suspensa", "suspensa"),
        ):
            if marcador in rotulo_status:
                status = estado
                break
        itens.append(
            {
                "numero": int(numero_match.group(1)),
                "identificador": identificador,
                "href": unescape(href),
                "status": status,
            }
        )
    return sorted(itens, key=lambda item: item["numero"])


def coletar_conjunto(
    conjunto_id: str,
    config: dict[str, Any],
    execucao_dir: Path,
    recibo: dict[str, Any],
) -> None:
    bruto = execucao_dir / "bruto" / conjunto_id
    downloads: list[dict[str, Any]] = []
    for fonte in config.get("fontes", []):
        destino = bruto / fonte["arquivo_bruto"]
        downloads.append(baixar(fonte["url"], destino))

    adaptador = config["adaptador"]
    if adaptador == "sumulas_stf_html_v1":
        fonte = config["fontes"][0]
        catalogo = decodificar_html(bruto / fonte["arquivo_bruto"])
        itens = extrair_catalogo_stf(catalogo, bool(config.get("vinculante")))
        if not itens:
            raise RuntimeError(f"{conjunto_id}: catálogo do STF não contém súmulas")
        for item in itens:
            url = urljoin(fonte["url"], item["href"])
            downloads.append(baixar(url, bruto / "detalhes" / f"{item['numero']}.html"))

    if adaptador == "jt_stj_html_v1":
        fonte = config["fontes"][0]
        indice = decodificar_html(bruto / fonte["arquivo_bruto"])
        numeros = [int(valor) for valor in re.findall(r"(?:numeroSumula|value)[^>]*>?(\d+)", indice)]
        numeros.extend(int(valor) for valor in re.findall(r"doc\.jsp\?livre=['%27]*(\d+)", indice))
        if not numeros:
            raise RuntimeError("não foi possível determinar a edição mais recente do STJ")
        for numero in range(1, max(numeros) + 1):
            url = f"https://processo.stj.jus.br/SCON/jt/doc.jsp?livre=%27{numero}%27.tit."
            downloads.append(baixar(url, bruto / "edicoes" / f"{numero}.html"))

    recibo["conjuntos"][conjunto_id] = {
        "coleta_concluida_em": agora_utc(),
        "downloads": downloads,
    }
    salvar_json(execucao_dir / "execucao.json", recibo)


def fonte_por_destino(config: dict[str, Any], destino: str) -> dict[str, Any]:
    for fonte in config.get("fontes", []):
        if fonte.get("destino") == destino:
            return fonte
    raise KeyError(destino)


ARTIGO = re.compile(
    # Páginas antigas do Planalto trazem defeitos tipográficos no rótulo:
    # "Art 4º" sem ponto (Lei 6.001) e "Art . 16." com espaço antes do ponto
    # (Lei 6.880). O ponto é opcional e pode vir espaçado; "Artigo"/"Arts."
    # continuam fora porque a letra seguinte interrompe o casamento. O
    # ordinal pode vir antes do sufixo ("Art. 1º-A", Lei 10.671) ou não
    # existir ("Art. 121-B", Código Penal).
    r"^Art\s*\.?\s*(\d+(?:\.\d{3})*)[ºo°]?(?:-([A-Z]))?[ºo°]?(?:\s|\.|$)",
    re.IGNORECASE,
)


def numero_artigo(match: re.Match[str]) -> str:
    numero = match.group(1).replace(".", "")
    return numero + ("-" + match.group(2).upper() if match.group(2) else "")


def chave_artigo(valor: str) -> tuple[int, str]:
    base, _, sufixo = valor.partition("-")
    return int(base), sufixo


def fragmento_texto(texto: str) -> str:
    trecho = re.sub(r"^\d+\)\s*", "", texto_normalizado(texto))
    palavras = trecho.split()
    return quote(" ".join(palavras[:22]), safe="")


def rotulo_inicial_em_link(no: Elemento) -> bool:
    """Verifica se o primeiro texto do parágrafo está dentro de um ``<a href>``.

    Quando uma lei insere dispositivos em outro diploma, a página compilada do
    Planalto apresenta o texto inserido com o rótulo "Art. N" apontando para a
    página do diploma alterado (ex.: "Art. 337-E" na Lei 14.133 liga a
    Del2848.htm, o Código Penal). O dispositivo pertence ao diploma alterado e
    não deve virar artigo da lei que o insere. Artigos próprios usam âncora
    ``<a name=...>``, sem ``href``.
    """

    def primeiro_dono_de_texto(item: Elemento) -> Elemento | None:
        if item.tag in {"script", "style", "noscript"}:
            return None
        for filho in item.filhos:
            if isinstance(filho, str):
                if texto_normalizado(filho):
                    return item
            else:
                dono = primeiro_dono_de_texto(filho)
                if dono is not None:
                    return dono
        return None

    dono = primeiro_dono_de_texto(no)
    atual: Elemento | None = dono
    while atual is not None and atual is not no.pai:
        if atual.tag == "a" and atual.atributos.get("href"):
            return True
        atual = atual.pai
    return False


def transformar_legislacao(
    config: dict[str, Any], bruto: Path, publicados: Path, candidatos: Path
) -> list[Path]:
    saidas: list[Path] = []
    for fonte in config["fontes"]:
        destino = fonte["destino"]
        atual = carregar_json(publicados / destino)
        arvore = analisar_html(decodificar_html(bruto / fonte["arquivo_bruto"]))
        paragrafos = [
            no
            for no in buscar(arvore, tag="p")
            if not any(isinstance(filho, Elemento) and filho.tag == "p" for filho in no.filhos)
        ]
        codigo = fonte["codigo"]
        marcadores_adct = [
            indice
            for indice, no in enumerate(paragrafos)
            if texto_normalizado(texto_elemento(no)).upper()
            == "ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS"
        ]
        if codigo in {"CF", "ADCT"} and marcadores_adct:
            marcador_adct = marcadores_adct[-1]
            paragrafos = (
                paragrafos[:marcador_adct]
                if codigo == "CF"
                else paragrafos[marcador_adct + 1 :]
            )
        # Descarte explícito e revisado por número: usado quando a página
        # exibe dispositivo de outra norma sem nenhum marcador estrutural
        # (ex.: o art. 59-A da Lei 9.504 reproduzido na página da Lei 13.165
        # após a derrubada do veto). A decisão fica no manifesto de fontes.
        descartar = set(fonte.get("descartar_artigos", []))
        inicio_apos = fonte.get("inicio_apos")
        if inicio_apos:
            alvo = texto_normalizado(inicio_apos).upper()
            posicoes = [
                indice
                for indice, no in enumerate(paragrafos)
                if texto_normalizado(texto_elemento(no)).upper() == alvo
            ]
            if not posicoes:
                raise ValueError(
                    f"{codigo}: marcador de início não encontrado: {inicio_apos}"
                )
            paragrafos = paragrafos[posicoes[-1] + 1 :]
        titulo = capitulo = secao = None
        titulo_nome = capitulo_nome = secao_nome = None
        ocorrencias: dict[str, tuple[bool, dict[str, Any]]] = {}

        for indice, paragrafo in enumerate(paragrafos):
            texto = texto_elemento(paragrafo, preservar_linhas=True)
            simples = texto_normalizado(texto)
            match_titulo = re.match(r"^TÍTULO\s+([IVXLCDM]+|ÚNICO)\b", simples, re.I)
            match_capitulo = re.match(r"^CAPÍTULO\s+([IVXLCDM]+|ÚNICO)\b", simples, re.I)
            match_secao = re.match(r"^SEÇÃO\s+([IVXLCDM]+|ÚNICA)\b", simples, re.I)
            if match_titulo:
                titulo = match_titulo.group(1)
                titulo_nome = simples
                capitulo = capitulo_nome = secao = secao_nome = None
                continue
            if match_capitulo:
                capitulo = match_capitulo.group(1)
                capitulo_nome = simples
                secao = secao_nome = None
                continue
            if match_secao:
                secao = match_secao.group(1)
                secao_nome = simples
                continue

            artigo_match = ARTIGO.match(simples)
            if not artigo_match:
                continue
            resto = simples[artigo_match.end() :].strip()
            if re.match(r"^\.{3,}", resto):
                # Redação pontilhada ("Art. 155. ....."): citação parcial de
                # dispositivo de outra norma alterada; não é artigo desta lei.
                continue
            if (
                not tem_ancestral_riscado(paragrafo)
                and rotulo_inicial_em_link(paragrafo)
                and not re.match(r"^\(?\s*VETADO", resto, re.IGNORECASE)
            ):
                # Dispositivo citado de outra norma (rótulo com href): não é
                # artigo desta lei. Parágrafos riscados ficam de fora da regra
                # para não perder artigos revogados retidos, e artigos vetados
                # da própria lei (rótulo ligado à mensagem de veto) são
                # preservados.
                continue
            numero = numero_artigo(artigo_match)
            if numero in descartar:
                continue
            blocos = [simples]
            for seguinte in paragrafos[indice + 1 :]:
                proximo = texto_normalizado(texto_elemento(seguinte, preservar_linhas=True))
                if ARTIGO.match(proximo):
                    break
                if re.match(r"^(TÍTULO|CAPÍTULO|SEÇÃO)\s+", proximo, re.I):
                    break
                if proximo and not proximo.lower().startswith(("voltar", "presidência da república")):
                    blocos.append(proximo)
            texto_artigo = "\n\n".join(blocos)
            antigo = atual.get("artigos", {}).get(numero, {})
            url = antigo.get("url") or (
                fonte["url"] + "#:~:text=" + fragmento_texto(simples)
            )
            registro = {
                "numero": numero,
                "texto": texto_artigo,
                "url": url,
                "keywords": antigo.get("keywords", []),
                "hierarchy": {
                    "title": titulo,
                    "title_name": titulo_nome,
                    "chapter": capitulo,
                    "chapter_name": capitulo_nome,
                    "section": secao,
                    "section_name": secao_nome,
                },
            }
            ativo = not tem_ancestral_riscado(paragrafo)
            anterior = ocorrencias.get(numero)
            if anterior is None or (ativo and not anterior[0]):
                ocorrencias[numero] = (ativo, registro)

        artigos_extraidos = {
            numero: registro
            for numero, (_, registro) in sorted(
                ocorrencias.items(), key=lambda item: chave_artigo(item[0])
            )
        }
        if not artigos_extraidos:
            raise ValueError(f"{codigo}: nenhum artigo reconhecido no HTML do Planalto")
        antigos = atual.get("artigos", {})
        retidos = sorted(set(antigos) - set(artigos_extraidos), key=chave_artigo)
        artigos = {
            numero: (
                artigos_extraidos[numero]
                if numero in artigos_extraidos
                else antigos[numero]
            )
            for numero in sorted(
                set(artigos_extraidos) | set(antigos), key=chave_artigo
            )
        }
        numeros = list(artigos)
        for indice, numero in enumerate(numeros):
            artigos[numero]["prev"] = numeros[indice - 1] if indice else None
            artigos[numero]["next"] = numeros[indice + 1] if indice + 1 < len(numeros) else None
        meta = dict(atual.get("_meta", {}))
        meta.update(
            {
                "codigo": codigo,
                "url_base": fonte["url"],
                "total_artigos": len(artigos),
                "version": "2.0",
                "gerado_em": hoje(),
                "transformacao": "planalto_html_v1",
                "registros_retidos_sem_correspondencia": retidos,
            }
        )
        objeto: dict[str, Any] = {"_meta": meta, "artigos": artigos}
        indices = atual.get("indexes")
        if indices:
            objeto["indexes"] = indices
        saida = candidatos / destino
        salvar_json(saida, objeto)
        saidas.append(saida)
    return saidas


def transformar_sumulas_stj(
    config: dict[str, Any], bruto: Path, publicados: Path, candidatos: Path
) -> list[Path]:
    arvore = analisar_html(decodificar_html(bruto / "catalogo.html"))
    sumulas: dict[str, Any] = {}
    for bloco in buscar(arvore, classe="gridSumula"):
        numero_no = primeiro(bloco, classe="numeroSumula")
        enunciado_no = primeiro(bloco, classe="clsVerbete")
        bloco_verbete = primeiro(bloco, classe="blocoVerbete")
        if numero_no is None or bloco_verbete is None:
            continue
        numero = int(texto_elemento(numero_no))
        ramo_no = primeiro(bloco, classe="ramoSumula")
        ramo = texto_elemento(ramo_no) if ramo_no else ""
        area, separador, tema = ramo.partition(" - ")
        status_no = primeiro(bloco, classe="clsINDE")
        rotulo_status = texto_elemento(status_no).upper() if status_no else ""
        status = "ativa"
        for marcador, estado in (
            ("CANCEL", "cancelada"),
            ("REVOG", "cancelada"),
            ("SUPERAD", "superada"),
            ("SUSPEN", "suspensa"),
            ("ALTERAD", "alterada"),
        ):
            if marcador in rotulo_status:
                status = estado
                break
        if status == "ativa" and (
            (enunciado_no is not None and tem_ancestral_riscado(enunciado_no))
            or tem_ancestral_riscado(bloco_verbete)
        ):
            status = "inativa"
        texto_bloco = texto_elemento(bloco_verbete)
        if ramo and texto_bloco.startswith(ramo):
            texto_bloco = texto_bloco[len(ramo) :].strip()
        comentario_no = primeiro(bloco_verbete, classe="clsCOM")
        if comentario_no:
            texto_bloco = texto_bloco.replace(texto_elemento(comentario_no), "").strip()
        citacao = re.search(
            r"\s*\((?:SÚMULA\s+\d+,\s*)?"
            r"(CORTE ESPECIAL|[A-ZÁÉÍÓÚÇ ]+SEÇÃO|[A-ZÁÉÍÓÚÇ ]+TURMA),"
            r"([^)]*)\)",
            texto_bloco,
            re.IGNORECASE,
        )
        data_citacao = (
            re.search(r"\d{1,2}/\d{1,2}/\d{4}", citacao.group(2))
            if citacao
            else None
        )
        enunciado = (
            texto_elemento(enunciado_no)
            if enunciado_no is not None
            else texto_bloco[: citacao.start()].strip() if citacao else texto_bloco
        )
        orgao_no = primeiro(bloco, classe="clsOrgaoJulgador")
        datas = [texto_elemento(no) for no in buscar(bloco, classe="clsData")]
        sumulas[str(numero)] = {
            "numero": numero,
            "enunciado": enunciado,
            "status": status,
            "area": area or "Não classificado",
            "tema": tema if separador else "",
            "orgao": (
                texto_elemento(orgao_no)
                if orgao_no
                else citacao.group(1).upper() if citacao else ""
            ),
            "data": (
                datas[0]
                if datas
                else data_citacao.group(0) if data_citacao else ""
            ),
            "url": f"https://scon.stj.jus.br/SCON/sumstj/toc.jsp?livre=%27{numero}%27.num.&O=JT",
        }
    if not sumulas:
        raise ValueError("nenhuma súmula reconhecida no catálogo do STJ")
    status = Counter(item["status"] for item in sumulas.values())
    objeto = {
        "_meta": {
            "version": "2.0",
            "tipo": "sumulas",
            "tribunal": "STJ",
            "total": len(sumulas),
            "ativas": status["ativa"],
            "canceladas": status["cancelada"],
            "gerado_em": hoje(),
            "descricao": "Súmulas STJ extraídas do catálogo oficial",
            "transformacao": "sumulas_stj_html_v1",
        },
        "sumulas": sumulas,
    }
    saida = candidatos / config["destino"]
    salvar_json(saida, objeto)
    return [saida]


def enunciado_detalhe_stf(path: Path) -> tuple[str, str, str]:
    conteudo = decodificar_html(path)
    arvore = analisar_html(conteudo)
    titulos = list(buscar(arvore, classe="titulo"))
    titulo_principal = next(
        (no for no in titulos if texto_elemento(no).lower().startswith("súmula")), None
    )
    if titulo_principal is None or titulo_principal.pai is None:
        raise ValueError(f"{path}: título da súmula não encontrado")
    irmaos = titulo_principal.pai.filhos
    posicao = irmaos.index(titulo_principal)
    enunciado = ""
    for item in irmaos[posicao + 1 :]:
        if isinstance(item, Elemento) and "parCOM" in item.classes:
            enunciado = texto_elemento(item)
            break
    pagina = texto_elemento(arvore)
    data_match = re.search(
        r"Data de (?:aprovação|publicação) do enunciado:.*?"
        r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})",
        pagina,
        re.IGNORECASE,
    )
    data = (
        f"{int(data_match.group(1)):02d}/{int(data_match.group(2)):02d}/{data_match.group(3)}"
        if data_match
        else ""
    )
    url_match = re.search(
        r"Para informações adicionais,.*?href=[\"']"
        r"(https?://jurisprudencia\.stf\.jus\.br/pages/search/seq-sumula\d+/false)",
        conteudo,
        re.IGNORECASE | re.DOTALL,
    )
    url = unescape(url_match.group(1)) if url_match else ""
    return enunciado, data, url


def transformar_sumulas_stf(
    config: dict[str, Any], bruto: Path, publicados: Path, candidatos: Path
) -> list[Path]:
    vinculante = bool(config.get("vinculante"))
    catalogo = decodificar_html(bruto / "catalogo.html")
    itens = extrair_catalogo_stf(catalogo, vinculante)
    atual = carregar_json(publicados / config["destino"])
    sumulas: dict[str, Any] = {}
    for item in itens:
        numero = item["numero"]
        enunciado, data, url = enunciado_detalhe_stf(
            bruto / "detalhes" / f"{numero}.html"
        )
        anterior = atual.get("sumulas", {}).get(str(numero), {})
        registro = {
            "numero": numero,
            "enunciado": enunciado,
            "status": item["status"],
        }
        if vinculante:
            registro["ramo"] = anterior.get("ramo", "Não classificado")
        else:
            registro["area"] = anterior.get("area", "Não classificado")
        registro["data"] = anterior.get("data", "") or data
        registro["url"] = (url or anterior.get("url", "")).replace(
            "http://jurisprudencia.stf.jus.br/",
            "https://jurisprudencia.stf.jus.br/",
        )
        sumulas[str(numero)] = registro
    if not sumulas:
        raise ValueError("nenhuma súmula reconhecida no catálogo do STF")
    contagem = Counter(item["status"] for item in sumulas.values())
    meta: dict[str, Any] = {
        "version": "2.0",
        "tipo": "Súmulas Vinculantes" if vinculante else "sumulas",
        "tribunal": "STF",
        "total": len(sumulas),
        "gerado_em": hoje(),
        "descricao": "Súmulas extraídas do catálogo oficial do STF",
        "transformacao": "sumulas_stf_html_v1",
    }
    for chave in ("ativa", "aprovada", "cancelada", "alterada", "superada", "suspensa"):
        if contagem[chave] or chave in {"ativa", "aprovada", "cancelada"}:
            meta[chave + "s"] = contagem[chave]
    saida = candidatos / config["destino"]
    salvar_json(saida, {"_meta": meta, "sumulas": sumulas})
    return [saida]


def data_iso(texto: str) -> str:
    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", texto)
    if not match:
        return ""
    return f"{match.group(3)}-{int(match.group(2)):02d}-{int(match.group(1)):02d}"


def transformar_jt(
    config: dict[str, Any], bruto: Path, publicados: Path, candidatos: Path
) -> list[Path]:
    atual = carregar_json(publicados / config["destino"])
    anteriores = atual.get("teses", {})
    teses: dict[str, Any] = {}
    for path in sorted((bruto / "edicoes").glob("*.html"), key=lambda item: int(item.stem)):
        edicao = int(path.stem)
        arvore = analisar_html(decodificar_html(path))
        materia_no = primeiro(arvore, classe="clsMateriaJT")
        titulo_no = primeiro(arvore, classe="clsTituloJT")
        cabecalho = primeiro(arvore, classe="gridEdicaoJT")
        if titulo_no is None and cabecalho is not None:
            titulo_no = primeiro(cabecalho, classe="clsVerbete")
        if titulo_no is None:
            continue
        titulo_completo = texto_elemento(titulo_no)
        titulo = titulo_completo.split(":", 1)[-1].strip()
        ramos_anteriores = [
            item.get("ramo_direito")
            for item in anteriores.values()
            if item.get("edicao") == edicao and item.get("ramo_direito")
        ]
        ramo = (
            texto_elemento(materia_no).title()
            if materia_no
            else ramos_anteriores[0] if ramos_anteriores else "Não classificado"
        )
        pagina = texto_elemento(arvore)
        publicacao_match = re.search(
            r"Edição disponibilizada em:\s*(\d{1,2}/\d{1,2}/\d{4})",
            pagina,
            re.IGNORECASE,
        )
        publicacao = data_iso(publicacao_match.group(1)) if publicacao_match else ""
        if not publicacao and cabecalho is not None:
            datas_cabecalho = [texto_elemento(no) for no in buscar(cabecalho, classe="clsData")]
            if datas_cabecalho:
                publicacao = data_iso(datas_cabecalho[-1])
        for bloco in buscar(arvore, classe="clsTemasJT"):
            if "redacaoAtual" not in bloco.classes:
                continue
            tese_no = primeiro(bloco, classe="clsSubmitPesquisaTema")
            if tese_no is None:
                continue
            bruto_tese = texto_elemento(tese_no)
            numero_match = re.match(r"(\d+)\)\s*(.*)", bruto_tese, re.DOTALL)
            if not numero_match:
                continue
            numero = int(numero_match.group(1))
            enunciado = texto_normalizado(numero_match.group(2))
            identificador = f"JT_{edicao:03d}_T{numero:02d}"
            anterior = anteriores.get(identificador, {})
            julgados_no = primeiro(bloco, classe="clsJulgadosJT")
            qtd_julgados = (
                len(list(buscar(julgados_no, tag="a")))
                if julgados_no
                else int(anterior.get("qtd_julgados", 0))
            )
            teses[identificador] = {
                "id": identificador,
                "edicao": edicao,
                "edicao_titulo": titulo,
                "tese_numero": numero,
                "ramo_direito": ramo,
                "enunciado": enunciado,
                "rito_especial": bool(anterior.get("rito_especial", False)),
                "data_publicacao": publicacao or anterior.get("data_publicacao", ""),
                "url": (
                    "https://scon.stj.jus.br/SCON/GetPDFSelecaoJT?selecao_edicao="
                    f"{edicao}#:~:text={fragmento_texto(enunciado)}"
                ),
                "qtd_julgados": qtd_julgados,
            }
    if not teses:
        raise ValueError("nenhuma tese reconhecida nas páginas do STJ")
    edicoes_extraidas = {int(item["edicao"]) for item in teses.values()}
    edicoes_retidas: set[int] = set()
    for identificador, anterior in anteriores.items():
        try:
            edicao_anterior = int(anterior.get("edicao") or 0)
        except (TypeError, ValueError):
            continue
        if edicao_anterior and edicao_anterior not in edicoes_extraidas:
            # A página oficial não devolveu a edição nesta coleta; preserva os
            # registros publicados em vez de presumir que a edição desapareceu.
            teses.setdefault(identificador, anterior)
            edicoes_retidas.add(edicao_anterior)
    ramos = Counter(item["ramo_direito"] for item in teses.values())
    objeto = {
        "_meta": {
            "version": "2.0.0",
            "tipo": "jurisprudencia_em_teses",
            "tribunal": "STJ",
            "total_edicoes": len({int(item["edicao"]) for item in teses.values()}),
            "total_teses": len(teses),
            "ramos_direito": dict(sorted(ramos.items())),
            "gerado_em": hoje(),
            "descricao": "Jurisprudência em Teses extraída das páginas oficiais do STJ",
            "transformacao": "jt_stj_html_v1",
            "edicoes_retidas_sem_correspondencia": sorted(edicoes_retidas),
        },
        "teses": teses,
    }
    saida = candidatos / config["destino"]
    salvar_json(saida, objeto)
    return [saida]


def limpar_csv(valor: str | None) -> str:
    return texto_normalizado(valor or "")


def data_br(valor: str | None) -> str:
    texto = limpar_csv(valor)
    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", texto)
    return f"{match.group(3)}/{match.group(2)}/{match.group(1)}" if match else texto


def ler_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def transformar_temas(
    config: dict[str, Any], bruto: Path, publicados: Path, candidatos: Path
) -> list[Path]:
    temas_csv = [item for item in ler_csv(bruto / "temas.csv") if item["tipoPrecedente"] == "Tema"]
    processos_por_sequencial: dict[str, list[dict[str, str]]] = defaultdict(list)
    for processo in ler_csv(bruto / "processos.csv"):
        if processo["tipoPrecedente"] == "Tema":
            processos_por_sequencial[processo["sequencialPrecedente"]].append(processo)
    atual = carregar_json(publicados / config["destino"])
    anteriores = atual.get("temas", {})
    orgaos = {
        "CE": "Corte Especial",
        "S1": "Primeira Seção",
        "S2": "Segunda Seção",
        "S3": "Terceira Seção",
    }
    temas: dict[str, Any] = {}
    for linha in temas_csv:
        numero_texto = limpar_csv(linha["numeroPrecedente"])
        if not numero_texto.isdigit():
            continue
        numero = int(numero_texto)
        chave = str(numero)
        processos = processos_por_sequencial.get(linha["sequencialPrecedente"], [])
        processo = next((item for item in processos if item.get("leadingCase") == "S"), None)
        processo = processo or (processos[0] if processos else {})
        processo_nome = limpar_csv(processo.get("Processo"))
        uf = limpar_csv(processo.get("origemUF"))
        if processo_nome and uf and not processo_nome.endswith("/" + uf):
            processo_nome += "/" + uf
        assuntos = []
        for assunto in limpar_csv(linha.get("Assuntos")).split(","):
            nome = re.sub(r"^\s*\d+\s*-\s*", "", assunto).strip()
            if nome:
                assuntos.append(nome)
        anterior = anteriores.get(chave, {})
        numero_registro = limpar_csv(processo.get("numeroRegistro"))
        numero_processo = re.sub(r"\D", "", limpar_csv(processo.get("Processo")))
        links: dict[str, str] = {
            "paginaTema": (
                "https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp"
                f"?novaConsulta=true&tipo_pesquisa=T&cod_tema_inicial={numero}&cod_tema_final={numero}"
            )
        }
        if numero_processo:
            links["scon"] = (
                "https://scon.stj.jus.br/SCON/pesquisar.jsp?b=ACOR&livre=%40num%3D%22"
                + numero_processo
                + "%22&O=JT"
            )
        if numero_registro:
            links["consultaProcessual"] = (
                "https://ww2.stj.jus.br/processo/pesquisa/"
                "?tipoPesquisa=tipoPesquisaNumeroRegistro&termo=" + numero_registro
            )
        registro: dict[str, Any] = {
            "numero": numero,
            "situacao": limpar_csv(linha.get("situacao")),
            "ramo": assuntos[0] if assuntos else "",
            "assuntos": assuntos,
            "questao": limpar_csv(linha.get("questaoSubmetidaAJulgamento")),
            "teseFirmada": limpar_csv(linha.get("teseFirmada")),
            "orgaoJulgador": orgaos.get(
                limpar_csv(linha.get("orgaoJulgador")),
                limpar_csv(linha.get("orgaoJulgador")),
            ),
            "processo": processo_nome,
            "relator": limpar_csv(processo.get("ministroRelator")),
            "dataAfetacao": data_br(linha.get("dataPrimeiraAfetacao")),
            "dataJulgamento": data_br(linha.get("dataJulgamento")),
            "links": links,
        }
        if anterior.get("keywordsLLM"):
            registro["keywordsLLM"] = anterior["keywordsLLM"]
        temas[chave] = registro
    if not temas:
        raise ValueError("nenhum Tema reconhecido nos CSVs do STJ")
    metadados_path = bruto / "metadados.json"
    metadados_sha = sha256(metadados_path) if metadados_path.exists() else None
    objeto = {
        "_meta": {
            "version": "2.0",
            "generatedAt": agora_utc(),
            "totalTemas": len(temas),
            "source": {
                "provenanceStatus": "reproducible_pipeline",
                "dataset": "Precedentes qualificados — Portal de Dados Abertos do STJ",
                "officialPublicReference": {
                    "catalog": config["fontes"][0]["url"],
                    "packageId": config["package_id"],
                    "joinKey": config["join_key"],
                    "resources": {
                        "temas": {
                            "id": config["fontes"][1]["resource_id"],
                            "url": config["fontes"][1]["url"],
                        },
                        "processos": {
                            "id": config["fontes"][2]["resource_id"],
                            "url": config["fontes"][2]["url"],
                        },
                    },
                },
                "method": (
                    "Junção determinística de Temas.csv e Processos.csv por "
                    f"{config['join_key']}; seleção preferencial do leading case."
                ),
                "metadata_sha256": metadados_sha,
                "collectedAt": agora_utc(),
            },
            "transformacao": "temas_stj_csv_v1",
        },
        "temas": temas,
    }
    for bloco in ("keywords", "terms"):
        # Índices derivados legados consumidos pelo motor; preservados como os
        # da legislação até terem geração reproduzível (BASE-019).
        if atual.get(bloco):
            objeto[bloco] = atual[bloco]
    saida = candidatos / config["destino"]
    salvar_json(saida, objeto)
    return [saida]


TRANSFORMADORES = {
    "planalto_html_v1": transformar_legislacao,
    "sumulas_stj_html_v1": transformar_sumulas_stj,
    "sumulas_stf_html_v1": transformar_sumulas_stf,
    "jt_stj_html_v1": transformar_jt,
    "temas_stj_csv_v1": transformar_temas,
}


def transformar_conjunto(
    conjunto_id: str,
    config: dict[str, Any],
    execucao_dir: Path,
    publicados: Path,
    recibo: dict[str, Any],
) -> list[Path]:
    adaptador = config["adaptador"]
    if adaptador not in TRANSFORMADORES:
        raise ValueError(f"adaptador não implementado: {adaptador}")
    bruto = execucao_dir / "bruto" / conjunto_id
    candidatos = execucao_dir / "candidatos"
    saidas = TRANSFORMADORES[adaptador](config, bruto, publicados, candidatos)
    conjunto = recibo["conjuntos"].setdefault(conjunto_id, {})
    conjunto["transformacao_concluida_em"] = agora_utc()
    conjunto["adaptador"] = adaptador
    conjunto["candidatos"] = [
        {
            "arquivo": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in saidas
    ]
    salvar_json(execucao_dir / "execucao.json", recibo)
    return saidas


def caminhos_absolutos(valor: Any, prefixo: str = "") -> list[str]:
    achados: list[str] = []
    if isinstance(valor, dict):
        for chave, item in valor.items():
            atual = f"{prefixo}.{chave}" if prefixo else chave
            achados.extend(caminhos_absolutos(item, atual))
    elif isinstance(valor, list):
        for indice, item in enumerate(valor):
            achados.extend(caminhos_absolutos(item, f"{prefixo}[{indice}]"))
    elif isinstance(valor, str) and valor.startswith("/"):
        achados.append(f"{prefixo}={valor}")
    return achados


def validar_objeto(config: dict[str, Any], objeto: dict[str, Any], nome: str) -> list[str]:
    erros: list[str] = []
    meta = objeto.get("_meta")
    chave = config.get("chave_colecao")
    registros = objeto.get(chave) if chave else None
    if not isinstance(meta, dict):
        erros.append(f"{nome}: _meta ausente ou inválido")
        meta = {}
    if not isinstance(registros, dict) or not registros:
        return erros + [f"{nome}: coleção {chave!r} ausente ou vazia"]
    if caminhos_absolutos(meta):
        erros.append(f"{nome}: metadados contêm caminho absoluto local")

    familia = config["familia"]
    obrigatorios = {
        "legislacao": ("numero", "texto", "url"),
        "sumulas": ("numero", "enunciado", "status", "url"),
        "jurisprudencia_em_teses": ("id", "edicao", "enunciado", "url"),
        "precedentes_qualificados": ("numero", "questao", "links"),
    }[familia]
    for identificador, registro in registros.items():
        if not isinstance(registro, dict):
            erros.append(f"{nome}:{identificador}: registro não é objeto")
            continue
        ausentes = [campo for campo in obrigatorios if registro.get(campo) in (None, "", {})]
        if ausentes:
            erros.append(
                f"{nome}:{identificador}: campos vazios: {', '.join(ausentes)}"
            )
        urls: list[str] = []
        if isinstance(registro.get("url"), str):
            urls.append(registro["url"])
        if isinstance(registro.get("links"), dict):
            urls.extend(str(url) for url in registro["links"].values())
        for url in urls:
            host_match = re.match(r"https://([^/]+)", url)
            if not host_match or host_match.group(1).lower() not in HOSTS_OFICIAIS:
                erros.append(f"{nome}:{identificador}: URL não oficial ou inválida: {url}")

    quantidade = len(registros)
    esperado = None
    if familia == "legislacao":
        esperado = meta.get("total_artigos")
    elif familia == "sumulas":
        esperado = meta.get("total")
    elif familia == "jurisprudencia_em_teses":
        esperado = meta.get("total_teses")
        edicoes = len({item.get("edicao") for item in registros.values()})
        if meta.get("total_edicoes") != edicoes:
            erros.append(
                f"{nome}: total_edicoes={meta.get('total_edicoes')} mas há {edicoes}"
            )
    elif familia == "precedentes_qualificados":
        esperado = meta.get("totalTemas")
    if esperado != quantidade:
        erros.append(f"{nome}: metadado informa {esperado}, coleção contém {quantidade}")
    return erros


def arquivos_do_conjunto(config: dict[str, Any]) -> list[str]:
    if config.get("destino"):
        return [config["destino"]]
    return [fonte["destino"] for fonte in config.get("fontes", []) if fonte.get("destino")]


def validar_conjuntos(
    dados: dict[str, Any], ids: Iterable[str], execucao_dir: Path
) -> dict[str, list[str]]:
    resultado: dict[str, list[str]] = {}
    candidatos = execucao_dir / "candidatos"
    for conjunto_id in ids:
        config = dados["conjuntos"][conjunto_id]
        erros: list[str] = []
        for nome in arquivos_do_conjunto(config):
            path = candidatos / nome
            if not path.exists():
                erros.append(f"{nome}: candidato não existe")
                continue
            try:
                objeto = carregar_json(path)
            except (OSError, ValueError, json.JSONDecodeError) as erro:
                erros.append(f"{nome}: JSON inválido: {erro}")
                continue
            erros.extend(validar_objeto(config, objeto, nome))
        resultado[conjunto_id] = erros
    salvar_json(execucao_dir / "relatorios" / "validacao.json", resultado)
    return resultado


def hash_registro(valor: Any) -> str:
    bruto = json.dumps(valor, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(bruto.encode()).hexdigest()


def comparar_arquivo(
    publicado: Path, candidato: Path, chave_colecao: str
) -> dict[str, Any]:
    anterior = carregar_json(publicado)
    novo = carregar_json(candidato)
    antigos = anterior.get(chave_colecao, {})
    novos = novo.get(chave_colecao, {})
    ids_antigos = set(antigos)
    ids_novos = set(novos)
    alterados = sorted(
        identificador
        for identificador in ids_antigos & ids_novos
        if hash_registro(antigos[identificador]) != hash_registro(novos[identificador])
    )
    return {
        "arquivo": candidato.name,
        "sha256_anterior": sha256(publicado),
        "sha256_candidato": sha256(candidato),
        "registros_anteriores": len(antigos),
        "registros_candidatos": len(novos),
        "adicionados": sorted(ids_novos - ids_antigos),
        "removidos": sorted(ids_antigos - ids_novos),
        "alterados": alterados,
        "metadados_alterados": hash_registro(anterior.get("_meta"))
        != hash_registro(novo.get("_meta")),
    }


def comparar_conjuntos(
    dados: dict[str, Any], ids: Iterable[str], execucao_dir: Path, publicados: Path
) -> dict[str, Any]:
    relatorio: dict[str, Any] = {"gerado_em": agora_utc(), "conjuntos": {}}
    for conjunto_id in ids:
        config = dados["conjuntos"][conjunto_id]
        itens = []
        for nome in arquivos_do_conjunto(config):
            itens.append(
                comparar_arquivo(
                    publicados / nome,
                    execucao_dir / "candidatos" / nome,
                    config["chave_colecao"],
                )
            )
        relatorio["conjuntos"][conjunto_id] = itens
    salvar_json(execucao_dir / "relatorios" / "diferencas.json", relatorio)
    linhas = ["# Diferenças da atualização", "", f"Gerado em: {relatorio['gerado_em']}", ""]
    for conjunto_id, itens in relatorio["conjuntos"].items():
        linhas.extend([f"## {conjunto_id}", ""])
        for item in itens:
            linhas.extend(
                [
                    f"- `{item['arquivo']}`: {item['registros_anteriores']} → {item['registros_candidatos']} registros",
                    f"  - adicionados: {len(item['adicionados'])}",
                    f"  - removidos: {len(item['removidos'])}",
                    f"  - alterados: {len(item['alterados'])}",
                ]
            )
        linhas.append("")
    relatorio_md = execucao_dir / "relatorios" / "diferencas.md"
    relatorio_md.parent.mkdir(parents=True, exist_ok=True)
    relatorio_md.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return relatorio


def remocoes_do_relatorio(relatorio: dict[str, Any]) -> list[str]:
    return [
        f"{conjunto_id}/{item['arquivo']}: {len(item['removidos'])}"
        for conjunto_id, itens in relatorio["conjuntos"].items()
        for item in itens
        if item["removidos"]
    ]


def mudancas_volumosas_do_relatorio(
    relatorio: dict[str, Any], percentual: int, minimo: int
) -> list[str]:
    achados: list[str] = []
    for conjunto_id, itens in relatorio["conjuntos"].items():
        for item in itens:
            anteriores = item["registros_anteriores"]
            mudancas = sum(
                len(item[chave])
                for chave in ("adicionados", "removidos", "alterados")
            )
            limite_percentual = (
                anteriores * percentual + 99
            ) // 100
            limite = max(minimo, limite_percentual)
            if mudancas > limite:
                achados.append(
                    f"{conjunto_id}/{item['arquivo']}: {mudancas} mudanças "
                    f"(limite {limite}; base {anteriores})"
                )
    return achados


def promover(
    dados: dict[str, Any],
    ids: Iterable[str],
    execucao_dir: Path,
    publicados: Path,
    confirmacao: str,
    aceitar_remocoes: bool = False,
    aceitar_mudanca_volumosa: bool = False,
) -> None:
    if confirmacao != "PROMOVER":
        raise ValueError("promoção recusada: use --confirmar PROMOVER")
    if (execucao_dir / "promocao.json").exists():
        raise ValueError("promoção recusada: esta execução já foi promovida")
    validacao = validar_conjuntos(dados, ids, execucao_dir)
    erros = [erro for conjunto in validacao.values() for erro in conjunto]
    if erros:
        raise ValueError("promoção recusada; validação falhou:\n- " + "\n- ".join(erros))
    relatorio = comparar_conjuntos(dados, ids, execucao_dir, publicados)
    remocoes = remocoes_do_relatorio(relatorio)
    if remocoes and not aceitar_remocoes:
        raise ValueError(
            "promoção recusada; há remoções no relatório:\n- "
            + "\n- ".join(remocoes)
            + "\nRevise os IDs e, somente se forem intencionais, use --aceitar-remocoes."
        )
    politica = dados.get("politica_promocao", {})
    percentual = int(
        politica.get(
            "limite_mudanca_percentual", LIMITE_MUDANCA_PERCENTUAL_PADRAO
        )
    )
    minimo = int(
        politica.get("limite_mudanca_minimo", LIMITE_MUDANCA_MINIMO_PADRAO)
    )
    volumosas = mudancas_volumosas_do_relatorio(relatorio, percentual, minimo)
    if volumosas and not aceitar_mudanca_volumosa:
        raise ValueError(
            "promoção recusada; há mudança volumosa no relatório:\n- "
            + "\n- ".join(volumosas)
            + "\nRevise as diferenças e, somente se forem intencionais, use "
            "--aceitar-mudanca-volumosa."
        )
    backup = execucao_dir / "backup"
    promovidos: list[dict[str, str]] = []
    for conjunto_id in ids:
        config = dados["conjuntos"][conjunto_id]
        for nome in arquivos_do_conjunto(config):
            origem = execucao_dir / "candidatos" / nome
            destino = publicados / nome
            backup.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destino, backup / nome)
            shutil.copy2(origem, destino)
            promovidos.append(
                {"arquivo": nome, "sha256": sha256(destino), "promovido_em": agora_utc()}
            )
    salvar_json(execucao_dir / "promocao.json", {"arquivos": promovidos})


def sondar_url(url: str, desde: str | None = None) -> dict[str, Any]:
    """GET condicional que descarta o corpo; devolve código HTTP e cabeçalhos.

    Com ``desde`` (data ISO), envia ``If-Modified-Since``: servidores que
    suportam o cabeçalho respondem 304 sem corpo quando nada mudou.
    """
    validar_url_oficial(url)
    with tempfile.TemporaryDirectory() as temp:
        corpo = Path(temp) / "corpo"
        cabecalhos_path = Path(temp) / "cabecalhos"
        comando = [
            "curl",
            "--location",
            "--fail",
            "--silent",
            "--show-error",
            "--compressed",
            "--retry",
            "2",
            "--retry-all-errors",
            "--connect-timeout",
            "20",
            "--max-time",
            "120",
            "--user-agent",
            USER_AGENT,
            "--dump-header",
            str(cabecalhos_path),
            "--write-out",
            "%{http_code}\t%{url_effective}",
            "--output",
            str(corpo),
        ]
        if desde:
            comando.extend(["--time-cond", desde])
        comando.append(url)
        resultado = subprocess.run(
            comando, check=True, capture_output=True, text=True
        )
        codigo_texto, _, url_efetiva = resultado.stdout.strip().partition("\t")
        validar_url_oficial(url_efetiva or url)
        cabecalhos = ler_cabecalhos(cabecalhos_path)
    return {
        "http": int(codigo_texto or 0),
        "url": url,
        "url_efetiva": url_efetiva or url,
        "etag": cabecalhos.get("etag"),
        "last_modified": cabecalhos.get("last-modified"),
    }


def instante_utc(valor: str) -> datetime | None:
    texto = valor.strip()
    if not texto:
        return None
    if texto.endswith("Z"):
        texto = texto[:-1] + "+00:00"
    try:
        instante = datetime.fromisoformat(texto)
    except ValueError:
        return None
    if instante.tzinfo is None:
        instante = instante.replace(tzinfo=timezone.utc)
    return instante.astimezone(timezone.utc)


def monitorar_legislacao(
    config: dict[str, Any], publicados: Path
) -> list[dict[str, Any]]:
    itens: list[dict[str, Any]] = []
    for fonte in config.get("fontes", []):
        codigo = fonte.get("codigo") or fonte.get("destino") or fonte["url"]
        caminho = publicados / fonte["destino"]
        if not caminho.exists():
            itens.append(
                {
                    "alvo": codigo,
                    "situacao": "indeterminado",
                    "detalhe": f"{fonte['destino']} não existe no diretório publicado",
                }
            )
            continue
        publicado = carregar_json(caminho)
        meta = publicado.get("_meta")
        if not isinstance(meta, dict):
            meta = publicado
        gerado_em = str(meta.get("gerado_em") or "")
        try:
            sonda = sondar_url(fonte["url"], desde=gerado_em or None)
        except (RuntimeError, ValueError, subprocess.CalledProcessError) as erro:
            itens.append({"alvo": codigo, "situacao": "erro", "detalhe": str(erro)})
            continue
        if sonda["http"] == 304:
            situacao = "sem_mudanca"
            detalhe = f"fonte não modificada desde o snapshot de {gerado_em}"
        elif sonda["http"] == 200:
            situacao = "mudou" if gerado_em else "indeterminado"
            detalhe = (
                "fonte modificada em "
                f"{sonda.get('last_modified') or 'data não informada'}; "
                f"snapshot local de {gerado_em or 'data desconhecida'}"
            )
        else:
            situacao = "indeterminado"
            detalhe = f"resposta HTTP {sonda['http']}"
        itens.append(
            {
                "alvo": codigo,
                "situacao": situacao,
                "detalhe": detalhe,
                "gerado_em": gerado_em,
                "last_modified": sonda.get("last_modified"),
            }
        )
    return itens


def contar_catalogo_sumulas_stj(caminho: Path) -> int:
    arvore = analisar_html(decodificar_html(caminho))
    total = 0
    for bloco in buscar(arvore, classe="gridSumula"):
        if primeiro(bloco, classe="numeroSumula") is None:
            continue
        if primeiro(bloco, classe="blocoVerbete") is None:
            continue
        total += 1
    return total


def monitorar_sumulas_stj(
    config: dict[str, Any], publicados: Path, temp: Path
) -> list[dict[str, Any]]:
    fonte = config["fontes"][0]
    catalogo = temp / "catalogo.html"
    baixar(fonte["url"], catalogo)
    total_fonte = contar_catalogo_sumulas_stj(catalogo)
    if not total_fonte:
        raise RuntimeError("catálogo do STJ não contém súmulas reconhecíveis")
    publicado = carregar_json(publicados / config["destino"])
    total_publicado = len(publicado.get(config.get("chave_colecao", "sumulas"), {}))
    if total_fonte != total_publicado:
        situacao = "mudou"
        detalhe = (
            f"catálogo oficial com {total_fonte} súmulas; "
            f"snapshot local com {total_publicado}"
        )
    else:
        situacao = "sem_mudanca"
        detalhe = (
            f"contagem igual ({total_fonte}); mudanças de estado sem alteração "
            "de contagem não são detectadas por este sinal"
        )
    return [{"alvo": "catalogo", "situacao": situacao, "detalhe": detalhe}]


ROTULOS_STATUS = {
    "ativa": "ativas",
    "aprovada": "aprovadas",
    "alterada": "alteradas",
    "cancelada": "canceladas",
    "superada": "superadas",
    "suspensa": "suspensas",
}


def monitorar_sumulas_stf(
    config: dict[str, Any], publicados: Path, temp: Path
) -> list[dict[str, Any]]:
    fonte = config["fontes"][0]
    catalogo = temp / "catalogo.html"
    baixar(fonte["url"], catalogo)
    itens_catalogo = extrair_catalogo_stf(
        decodificar_html(catalogo), bool(config.get("vinculante"))
    )
    if not itens_catalogo:
        raise RuntimeError("catálogo do STF não contém súmulas reconhecíveis")
    contagem_fonte = Counter(item["status"] for item in itens_catalogo)
    registros = carregar_json(publicados / config["destino"]).get(
        config.get("chave_colecao", "sumulas"), {}
    )
    contagem_publicada = Counter(
        str(item.get("status", "")) for item in registros.values()
    )
    diferencas: list[str] = []
    if len(itens_catalogo) != len(registros):
        diferencas.append(
            f"total {len(itens_catalogo)} na fonte vs {len(registros)} no snapshot"
        )
    for status in sorted(set(contagem_fonte) | set(contagem_publicada)):
        if contagem_fonte[status] != contagem_publicada[status]:
            rotulo = ROTULOS_STATUS.get(status, status)
            diferencas.append(
                f"{rotulo}: {contagem_fonte[status]} na fonte vs "
                f"{contagem_publicada[status]} no snapshot"
            )
    if diferencas:
        situacao = "mudou"
        detalhe = "; ".join(diferencas)
    else:
        situacao = "sem_mudanca"
        detalhe = (
            f"contagens por estado iguais ({len(itens_catalogo)} súmulas); "
            "alterações de enunciado não são detectadas por este sinal"
        )
    return [{"alvo": "catalogo", "situacao": situacao, "detalhe": detalhe}]


def monitorar_jt(
    config: dict[str, Any], publicados: Path, temp: Path
) -> list[dict[str, Any]]:
    fonte = config["fontes"][0]
    indice_path = temp / "indice.html"
    baixar(fonte["url"], indice_path)
    indice = decodificar_html(indice_path)
    numeros = [
        int(valor)
        for valor in re.findall(r'class="numeroSumula">\s*(\d+)\s*<', indice)
    ]
    numeros.extend(
        int(valor) for valor in re.findall(r'data-edicao="(\d+)"', indice)
    )
    if not numeros:
        raise RuntimeError("não foi possível determinar a edição mais recente do STJ")
    edicao_fonte = max(numeros)
    teses = carregar_json(publicados / config["destino"]).get(
        config.get("chave_colecao", "teses"), {}
    )
    edicao_publicada = max(
        (int(item.get("edicao") or 0) for item in teses.values()), default=0
    )
    if edicao_fonte != edicao_publicada:
        situacao = "mudou"
        detalhe = (
            f"edição mais recente {edicao_fonte} na fonte; "
            f"snapshot local vai até a {edicao_publicada}"
        )
    else:
        situacao = "sem_mudanca"
        detalhe = (
            f"edição mais recente igual ({edicao_fonte}); revisões de edições "
            "antigas não são detectadas por este sinal"
        )
    return [{"alvo": "indice", "situacao": situacao, "detalhe": detalhe}]


def monitorar_temas(
    config: dict[str, Any], publicados: Path, temp: Path
) -> list[dict[str, Any]]:
    fonte = next(
        item for item in config["fontes"] if item.get("id") == "metadados"
    )
    metadados_path = temp / "metadados.json"
    baixar(fonte["url"], metadados_path)
    recursos = (carregar_json(metadados_path).get("result") or {}).get(
        "resources"
    ) or []
    meta = carregar_json(publicados / config["destino"]).get("_meta") or {}
    base = instante_utc(str(meta.get("generatedAt") or ""))
    mais_recente: datetime | None = None
    recurso_alvo = ""
    for recurso in recursos:
        instante = instante_utc(str(recurso.get("last_modified") or ""))
        if instante and (mais_recente is None or instante > mais_recente):
            mais_recente = instante
            recurso_alvo = str(recurso.get("name") or "")
    if base is None or mais_recente is None:
        situacao = "indeterminado"
        detalhe = "datas de referência ausentes no snapshot ou nos metadados CKAN"
    elif mais_recente > base:
        situacao = "mudou"
        detalhe = (
            f"recurso {recurso_alvo} atualizado em "
            f"{mais_recente.isoformat(timespec='seconds')}; snapshot local de "
            f"{base.isoformat(timespec='seconds')}"
        )
    else:
        situacao = "sem_mudanca"
        detalhe = (
            "nenhum recurso do dataset foi atualizado depois do snapshot local; "
            "reenvio de conteúdo idêntico ainda contaria como mudança"
        )
    return [{"alvo": "ckan", "situacao": situacao, "detalhe": detalhe}]


MONITORES_POR_ADAPTADOR = {
    "sumulas_stj_html_v1": monitorar_sumulas_stj,
    "sumulas_stf_html_v1": monitorar_sumulas_stf,
    "jt_stj_html_v1": monitorar_jt,
    "temas_stj_csv_v1": monitorar_temas,
}


def monitorar_conjuntos(
    dados: dict[str, Any], ids: Iterable[str], publicados: Path
) -> dict[str, Any]:
    resultado: dict[str, Any] = {
        "verificado_em": agora_utc(),
        "conjuntos": {},
        "mudancas": 0,
        "erros": 0,
    }
    for conjunto_id in ids:
        config = dados["conjuntos"][conjunto_id]
        adaptador = config.get("adaptador")
        try:
            if adaptador == "planalto_html_v1":
                itens = monitorar_legislacao(config, publicados)
            elif adaptador in MONITORES_POR_ADAPTADOR:
                with tempfile.TemporaryDirectory() as temp:
                    itens = MONITORES_POR_ADAPTADOR[adaptador](
                        config, publicados, Path(temp)
                    )
            else:
                itens = [
                    {
                        "alvo": conjunto_id,
                        "situacao": "indeterminado",
                        "detalhe": f"adaptador sem sinal de monitoramento: {adaptador}",
                    }
                ]
        except (
            OSError,
            RuntimeError,
            ValueError,
            KeyError,
            StopIteration,
            subprocess.CalledProcessError,
        ) as erro:
            itens = [
                {"alvo": conjunto_id, "situacao": "erro", "detalhe": str(erro)}
            ]
        resultado["conjuntos"][conjunto_id] = itens
        resultado["mudancas"] += sum(
            1 for item in itens if item["situacao"] == "mudou"
        )
        resultado["erros"] += sum(
            1 for item in itens if item["situacao"] == "erro"
        )
    resultado["mudancas_detectadas"] = resultado["mudancas"] > 0
    return resultado


def imprimir_monitoramento(resultado: dict[str, Any]) -> None:
    print(f"Verificação de fontes em {resultado['verificado_em']}")
    for conjunto_id, itens in resultado["conjuntos"].items():
        for item in itens:
            print(
                f"[{item['situacao']}] {conjunto_id}/{item['alvo']}: "
                f"{item['detalhe']}"
            )
    print(
        f"Total: {resultado['mudancas']} sinal(is) de mudança, "
        f"{resultado['erros']} erro(s). O sinal indica que vale preparar um "
        "candidato; a confirmação vem do relatório de diferenças."
    )


def imprimir_validacao(resultado: dict[str, list[str]]) -> bool:
    ok = True
    for conjunto, erros in resultado.items():
        if erros:
            ok = False
            print(f"{conjunto}: FALHOU")
            for erro in erros:
                print(f"  - {erro}")
        else:
            print(f"{conjunto}: OK")
    return ok


def parser_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifesto", type=Path, default=MANIFESTO_PADRAO)
    parser.add_argument("--area", type=Path, default=AREA_PADRAO)
    sub = parser.add_subparsers(dest="acao", required=True)
    sub.add_parser("listar", help="lista conjuntos, adaptadores e destinos")
    for acao in ("coletar", "transformar", "validar", "comparar", "executar"):
        comando = sub.add_parser(acao)
        comando.add_argument("--execucao", required=True)
        comando.add_argument("--conjunto", default="todos")
    comando_monitorar = sub.add_parser(
        "monitorar",
        help="verifica sinais de mudança nas fontes sem preparar candidatos",
    )
    comando_monitorar.add_argument("--conjunto", default="todos")
    comando_monitorar.add_argument("--json", action="store_true")
    comando_promover = sub.add_parser("promover")
    comando_promover.add_argument("--execucao", required=True)
    comando_promover.add_argument("--conjunto", default="todos")
    comando_promover.add_argument("--confirmar", default="")
    comando_promover.add_argument("--aceitar-remocoes", action="store_true")
    comando_promover.add_argument(
        "--aceitar-mudanca-volumosa", action="store_true"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = parser_cli().parse_args(argv)
    dados = manifesto(args.manifesto)
    conjuntos = dados["conjuntos"]
    if args.acao == "listar":
        for conjunto_id, config in conjuntos.items():
            adaptador = config.get("adaptador") or "pendente"
            destinos = ", ".join(arquivos_do_conjunto(config)) or ", ".join(config.get("destinos", []))
            print(f"{conjunto_id}: {adaptador} -> {destinos}")
        return 0

    ids = ids_selecionados(dados, args.conjunto)
    publicados = ROOT / dados["diretorio_publicado"]

    if args.acao == "monitorar":
        resultado = monitorar_conjuntos(dados, ids, publicados)
        if args.json:
            print(json.dumps(resultado, ensure_ascii=False, indent=2))
        else:
            imprimir_monitoramento(resultado)
        return 0

    execucao_dir = caminho_execucao(args.area, args.execucao)
    execucao_dir.mkdir(parents=True, exist_ok=True)
    recibo = carregar_recibo(execucao_dir, dados["pipeline_version"])

    if args.acao in {"coletar", "executar"}:
        for conjunto_id in ids:
            print(f"Coletando {conjunto_id}...", flush=True)
            coletar_conjunto(conjunto_id, conjuntos[conjunto_id], execucao_dir, recibo)
    if args.acao in {"transformar", "executar"}:
        for conjunto_id in ids:
            print(f"Transformando {conjunto_id}...", flush=True)
            transformar_conjunto(
                conjunto_id, conjuntos[conjunto_id], execucao_dir, publicados, recibo
            )
    if args.acao in {"validar", "executar"}:
        resultado = validar_conjuntos(dados, ids, execucao_dir)
        if not imprimir_validacao(resultado):
            return 1
    if args.acao in {"comparar", "executar"}:
        relatorio = comparar_conjuntos(dados, ids, execucao_dir, publicados)
        for conjunto_id, itens in relatorio["conjuntos"].items():
            for item in itens:
                print(
                    f"{conjunto_id}/{item['arquivo']}: "
                    f"+{len(item['adicionados'])} -{len(item['removidos'])} "
                    f"~{len(item['alterados'])}"
                )
    if args.acao == "promover":
        promover(
            dados,
            ids,
            execucao_dir,
            publicados,
            args.confirmar,
            args.aceitar_remocoes,
            args.aceitar_mudanca_volumosa,
        )
        print(f"Promoção concluída; backup em {execucao_dir / 'backup'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        raise SystemExit(1)
