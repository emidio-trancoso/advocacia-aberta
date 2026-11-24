#!/usr/bin/env python3
"""Relatório de uso do site e do servidor MCP a partir dos logs do Caddy.

Lê os arquivos JSON de acesso gravados por deploy/Caddyfile e resume volume,
clientes e páginas em linguagem direta. Os IPs já chegam mascarados do Caddy
(faixa /24), então este relatório conta faixas de rede, não pessoas.

Uso, direto na VM:

    sudo python3 relatorio_acesso.py /var/log/caddy/site.log
    sudo python3 relatorio_acesso.py /var/log/caddy/mcp.log --desde hoje

Uso, a partir da máquina local (sem copiar o log para cá):

    gcloud compute ssh <instancia> --zone <zona> --command \\
      'sudo python3 -' < ferramentas/manutencao/relatorio_acesso.py

O filtro --desde aceita "hoje", "ontem" ou um número de horas ("24h").
"""

from __future__ import annotations

import argparse
import json
import mmap
import struct
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Índice local de geolocalização, gerado por construir_indice_geo.py. Se não existir,
# o relatório apenas omite a seção de origem — nada é consultado fora da máquina.
INDICE_GEO_PADRAO = Path("/var/lib/dbip")
REGISTRO_GEO = struct.Struct("<IIH")

# Requisições que inflam a contagem sem indicar leitura humana de conteúdo.
EXTENSOES_ESTATICAS = (
    ".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp",
    ".ico", ".woff", ".woff2", ".ttf", ".map", ".xml", ".txt",
)

# User-Agents de robôs, scanners e monitoramento, separados do tráfego de interesse.
# "l9scan"/"leakix" e afins são varredores de vulnerabilidade: batem em /.git/config,
# /wp-admin e similares. Contá-los como visita infla o número de usuários.
MARCAS_DE_ROBO = (
    "bot", "crawler", "spider", "slurp", "curl", "wget",
    "python-requests", "headless", "monitor", "uptime", "probe",
    "scan", "leakix", "go-http-client", "httpx", "aiohttp", "okhttp", "libwww",
)


class IndiceGeo:
    """Consulta país/estado de um IPv4 usando o índice local.

    O arquivo é mapeado em memória e percorrido por busca binária: 2 milhões de
    faixas cabem em 20 MiB e a consulta não carrega o índice inteiro na RAM, o que
    importa numa máquina pequena.
    """

    def __init__(self, diretorio: Path):
        self.locais: list[tuple[str, str]] = []
        with (diretorio / "locais.tsv").open(encoding="utf-8") as arquivo:
            for linha in arquivo:
                pais, _, estado = linha.rstrip("\n").partition("\t")
                self.locais.append((pais, estado))
        self._arquivo = (diretorio / "ranges.bin").open("rb")
        self._mapa = mmap.mmap(self._arquivo.fileno(), 0, access=mmap.ACCESS_READ)
        self.total = len(self._mapa) // REGISTRO_GEO.size

    @staticmethod
    def _para_inteiro(ip: str) -> int | None:
        partes = ip.split(".")
        if len(partes) != 4:
            return None
        valor = 0
        for parte in partes:
            if not parte.isdigit() or not 0 <= int(parte) <= 255:
                return None
            valor = (valor << 8) | int(parte)
        return valor

    def localizar(self, ip: str) -> tuple[str, str] | None:
        """Devolve (país, estado) ou None quando o IP não está em nenhuma faixa."""
        numero = self._para_inteiro(ip)
        if numero is None:
            return None
        baixo, alto = 0, self.total
        while baixo < alto:
            meio = (baixo + alto) // 2
            inicio, fim, indice = REGISTRO_GEO.unpack_from(self._mapa, meio * REGISTRO_GEO.size)
            if numero < inicio:
                alto = meio
            elif numero > fim:
                baixo = meio + 1
            else:
                return self.locais[indice]
        return None


def abrir_indice_geo(caminho: Path) -> IndiceGeo | None:
    """Carrega o índice se ele existir; caso contrário segue sem geolocalização."""
    if not (caminho / "ranges.bin").exists() or not (caminho / "locais.tsv").exists():
        return None
    try:
        return IndiceGeo(caminho)
    except OSError:
        return None


def instante_de_corte(desde: str | None) -> datetime | None:
    """Converte o filtro textual em um instante UTC, ou None se não houver filtro."""
    if not desde:
        return None
    agora = datetime.now(timezone.utc)
    termo = desde.strip().lower()
    if termo == "hoje":
        return agora.replace(hour=0, minute=0, second=0, microsecond=0)
    if termo == "ontem":
        return agora.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    if termo.endswith("h"):
        return agora - timedelta(hours=float(termo[:-1]))
    raise ValueError(f'Filtro --desde não reconhecido: "{desde}" (use hoje, ontem ou 24h)')


def eh_robo(user_agent: str) -> bool:
    ua = user_agent.lower()
    return any(marca in ua for marca in MARCAS_DE_ROBO)


def eh_estatico(uri: str) -> bool:
    caminho = uri.split("?", 1)[0].lower()
    return caminho.endswith(EXTENSOES_ESTATICAS)


def normalizar_pagina(uri: str) -> str:
    """Junta /metodo e /metodo/ na mesma contagem — são a mesma página."""
    caminho = uri.split("?", 1)[0]
    return caminho.rstrip("/") or "/"


def rotulo_de_cliente(user_agent: str) -> str:
    """Agrupa o User-Agent em uma família legível, para não pulverizar a contagem."""
    ua = user_agent.lower()
    if "openai-mcp" in ua:
        return "Codex (OpenAI)" if "codex" in ua else "ChatGPT (OpenAI)"
    if "claude-code" in ua:
        return "Claude Code"
    # O connector remoto do claude.ai se identifica assim ao chamar o MCP.
    if "claude-user" in ua:
        return "Claude (claude.ai)"
    if ua.startswith("claude") or "anthropic" in ua:
        return "Claude (outro)"
    if eh_robo(user_agent):
        return "robô / monitoramento"
    for nome, marca in (("Edge", "edg/"), ("Chrome", "chrome"), ("Firefox", "firefox"), ("Safari", "safari")):
        if marca in ua:
            return nome
    return "outro"


def abrir(caminho: Path):
    """Abre o arquivo, ou a entrada padrão quando o caminho é '-'."""
    if str(caminho) == "-":
        return sys.stdin
    return caminho.open(encoding="utf-8", errors="replace")


def extrair_json(linha: str) -> dict | None:
    """Isola o JSON da linha.

    O journald prefixa cada linha com data, host e processo; o log do Caddy vem
    limpo. Cortar a partir da primeira chave atende aos dois casos.
    """
    inicio = linha.find("{")
    if inicio < 0:
        return None
    try:
        return json.loads(linha[inicio:])
    except json.JSONDecodeError:
        return None


def momento_do_registro(registro: dict) -> datetime | None:
    """Lê o instante do evento: epoch no log do Caddy, ISO 8601 na telemetria."""
    ts = registro.get("ts")
    # A soma diária do MCP não tem hora (de propósito): vale o começo do dia em Brasília.
    if ts is None and isinstance(registro.get("dia"), str):
        try:
            inicio = datetime.fromisoformat(registro["dia"]).replace(tzinfo=timezone(timedelta(hours=-3)))
            return inicio.astimezone(timezone.utc)
        except ValueError:
            return None
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def carregar(caminho: Path, corte: datetime | None) -> tuple[list[dict], list[dict]]:
    """Lê o log e separa os dois tipos de evento que sabemos interpretar.

    Devolve (acessos, usos): requisições HTTP registradas pelo Caddy e chamadas de
    ferramenta registradas pelo servidor MCP. Um arquivo costuma ter só um dos dois.
    """
    acessos, usos = [], []
    arquivo = abrir(caminho)
    try:
        for linha in arquivo:
            registro = extrair_json(linha)
            if registro is None:
                continue
            eh_acesso = registro.get("msg") == "handled request"
            eh_uso = registro.get("evento") in ("uso_ferramenta", "uso_diario")
            if not (eh_acesso or eh_uso):
                continue
            momento = momento_do_registro(registro)
            if momento is None:
                continue
            if corte and momento < corte:
                continue
            registro["_momento"] = momento
            (acessos if eh_acesso else usos).append(registro)
    finally:
        if arquivo is not sys.stdin:
            arquivo.close()
    return acessos, usos


def imprimir_secao(titulo: str, contagem: Counter, limite: int = 10, total: int | None = None) -> None:
    if not contagem:
        return
    print(f"\n{titulo}")
    print("-" * len(titulo))
    for chave, valor in contagem.most_common(limite):
        if total:
            print(f"  {valor:6}  ({valor / total:5.1%})  {chave}")
        else:
            print(f"  {valor:6}  {chave}")
    restantes = len(contagem) - limite
    if restantes > 0:
        print(f"  ... e mais {restantes} não listados")


def formatar_bytes(total: float) -> str:
    for unidade in ("B", "KiB", "MiB", "GiB"):
        if abs(total) < 1024 or unidade == "GiB":
            return f"{total:.0f} {unidade}" if unidade == "B" else f"{total:.1f} {unidade}"
        total /= 1024
    return f"{total:.1f} GiB"


def chamadas_do_registro(uso: dict) -> int:
    """Quantas chamadas uma linha representa: 1 no formato antigo, a soma no diário."""
    if uso.get("evento") == "uso_diario":
        return int(uso.get("chamadas", 0) or 0)
    return 1


def relatorio_de_consumo(usos: list[dict]) -> None:
    """Quem consumiu quanto — a visão de administração do serviço.

    Separa consumo atribuível a uma pessoa do consumo de origem compartilhada. Um IP do
    claude.ai agrega usuários sem relação entre si: somar aquilo como se fosse um usuário
    produziria um "heavy user" que não existe.
    """
    atores: dict[str, dict] = {}
    for uso in usos:
        chave = uso.get("ator")
        if not chave:
            continue
        registro = atores.setdefault(
            chave,
            {"chamadas": 0, "bytes": 0, "ms": 0.0, "cliente": uso.get("cliente", "?"),
             "pessoa": bool(uso.get("pessoa")), "tools": Counter()},
        )
        n = chamadas_do_registro(uso)
        registro["chamadas"] += n
        registro["bytes"] += uso.get("bytes", 0) or 0
        registro["ms"] += uso.get("ms", 0) or 0
        registro["tools"][uso.get("tool", "?")] += n

    if not atores:
        print("\n(Sem identificação de ator nos registros — telemetria anterior à v2.)")
        return

    print("\nCONSUMO POR ATOR")
    print("-" * 16)
    print("  {:<34} {:>8} {:>10} {:>9}".format("ator", "chamadas", "resposta", "tempo"))

    ordenados = sorted(atores.items(), key=lambda item: -item[1]["chamadas"])
    total_chamadas = sum(r["chamadas"] for _, r in ordenados)

    for chave, registro in ordenados[:15]:
        # O identificador da OpenAI é longo; o começo já basta para distinguir e agir.
        rotulo = chave if len(chave) <= 32 else f"{chave[:29]}…"
        marca = "" if registro["pessoa"] else "  (origem compartilhada)"
        print(
            f"  {rotulo:<34} {registro['chamadas']:>8} "
            f"{formatar_bytes(registro['bytes']):>10} "
            f"{registro['ms'] / 1000:>8.1f}s{marca}"
        )

    if len(ordenados) > 15:
        print(f"  ... e mais {len(ordenados) - 15} atores")

    # Heavy user: quem sozinho responde por fatia desproporcional do total.
    pessoas = [(k, r) for k, r in ordenados if r["pessoa"]]
    if pessoas and total_chamadas:
        maior_chave, maior = pessoas[0]
        fatia = maior["chamadas"] / total_chamadas
        print(f"\n  Atores distintos      : {len(atores)}  "
              f"({len(pessoas)} identificam pessoa)")
        print(f"  Maior consumidor      : {maior['chamadas']} chamadas "
              f"({fatia:.0%} do total), {formatar_bytes(maior['bytes'])}")
        print(f"                          {maior_chave[:56]}")
        print(f"                          preferidas: "
              f"{', '.join(t for t, _ in maior['tools'].most_common(3))}")
        if fatia > 0.5:
            print("  ⚠ Um único ator responde por mais da metade das chamadas.")

    compartilhado = sum(r["chamadas"] for _, r in ordenados if not r["pessoa"])
    if compartilhado:
        print(f"\n  {compartilhado} chamada(s) vieram de origem compartilhada (claude.ai):")
        print("  o protocolo não expõe o usuário final, então esse consumo é atribuível")
        print("  à origem, não a uma pessoa.")


def relatorio_de_ferramentas(usos: list[dict]) -> None:
    """Mostra quais ferramentas do acervo foram chamadas e quantas acharam algo."""
    chamadas = Counter()
    vazias = Counter()
    falhas = Counter()
    facetas = Counter()
    duracoes: list[float] = []

    for uso in usos:
        ferramenta = uso.get("tool", "(desconhecida)")
        n = chamadas_do_registro(uso)
        if not n:
            continue  # linha só de bloqueios por limite de taxa
        chamadas[ferramenta] += n
        if uso.get("evento") == "uso_diario":
            falhas[ferramenta] += uso.get("falhas", 0)
            vazias[ferramenta] += uso.get("sem_resultado", 0)
            # A soma diária só tem o tempo total: entra a média, uma vez por chamada.
            duracoes.extend([uso.get("ms", 0) / n] * n)
        else:
            if uso.get("falhou"):
                falhas[ferramenta] += 1
            elif uso.get("achou") is False:
                vazias[ferramenta] += 1
            if isinstance(uso.get("ms"), (int, float)):
                duracoes.append(float(uso["ms"]))
        for campo in ("tribunal", "codigo"):
            if uso.get(campo):
                facetas[f"{campo}={uso[campo]}"] += n

    total = sum(chamadas.values())
    sem_resultado = sum(vazias.values())

    print("\nFERRAMENTAS DO ACERVO")
    print("-" * 21)
    print(f"  Chamadas       : {total}")
    print(f"  Sem resultado  : {sem_resultado} ({sem_resultado / total:.1%})" if total else "")
    if sum(falhas.values()):
        print(f"  Chamadas inválidas: {sum(falhas.values())}")
    if duracoes:
        ordenadas = sorted(duracoes)
        mediana = ordenadas[len(ordenadas) // 2]
        print(f"  Tempo (mediana): {mediana:.1f} ms   (pior: {ordenadas[-1]:.1f} ms)")

    print("\n  {:<22} {:>8} {:>14}".format("ferramenta", "chamadas", "sem resultado"))
    for ferramenta, quantidade in chamadas.most_common():
        vazio = vazias[ferramenta]
        marca = "  ← revisar" if quantidade >= 5 and vazio / quantidade > 0.5 else ""
        print(f"  {ferramenta:<22} {quantidade:>8} {vazio:>8} ({vazio / quantidade:4.0%}){marca}")

    imprimir_secao("FILTROS USADOS", facetas)
    print("\nO termo pesquisado não é registrado — só a ferramenta e se houve resultado.")


def main() -> int:
    analisador = argparse.ArgumentParser(
        description="Resume os logs de acesso do Caddy (site e MCP).",
    )
    analisador.add_argument("log", type=Path, help="caminho do arquivo .log")
    analisador.add_argument("--desde", help="hoje, ontem ou um número de horas (ex.: 24h)")
    analisador.add_argument(
        "--com-estaticos",
        action="store_true",
        help="inclui CSS, imagens e fontes na contagem de páginas",
    )
    analisador.add_argument(
        "--geo",
        default=str(INDICE_GEO_PADRAO),
        help=f"diretório do índice de geolocalização (default: {INDICE_GEO_PADRAO})",
    )
    argumentos = analisador.parse_args()

    if str(argumentos.log) != "-" and not argumentos.log.exists():
        print(f"Arquivo não encontrado: {argumentos.log}", file=sys.stderr)
        print("Na VM os logs ficam em /var/log/caddy/ e exigem sudo.", file=sys.stderr)
        return 1

    try:
        corte = instante_de_corte(argumentos.desde)
    except ValueError as erro:
        print(erro, file=sys.stderr)
        return 1

    eventos, usos = carregar(argumentos.log, corte)
    if not eventos and not usos:
        janela = f" desde {argumentos.desde}" if argumentos.desde else ""
        origem = "entrada padrão" if str(argumentos.log) == "-" else argumentos.log.name
        print(f"Nenhum evento reconhecido em {origem}{janela}.")
        return 0

    # Telemetria do servidor MCP: relatório próprio, não tem requisição HTTP para resumir.
    if usos and not eventos:
        primeiro = min(u["_momento"] for u in usos)
        ultimo = max(u["_momento"] for u in usos)
        print("=" * 60)
        print("RELATÓRIO DE USO DAS FERRAMENTAS")
        print("=" * 60)
        print(f"Janela      : {primeiro:%d/%m/%Y %H:%M} a {ultimo:%d/%m/%Y %H:%M} (UTC)")
        relatorio_de_ferramentas(usos)
        relatorio_de_consumo(usos)
        return 0

    clientes = Counter()
    faixas = Counter()
    paginas = Counter()
    horas = Counter()
    status = Counter()
    sessoes_mcp = set()
    requisicoes_humanas = 0

    for evento in eventos:
        requisicao = evento["request"]
        cabecalhos = requisicao.get("headers", {})
        user_agent = (cabecalhos.get("User-Agent") or ["(sem identificação)"])[0]
        uri = requisicao.get("uri", "/")

        status[evento.get("status", 0)] += 1
        clientes[rotulo_de_cliente(user_agent)] += 1

        sessao = cabecalhos.get("Mcp-Session-Id")
        if sessao:
            sessoes_mcp.add(sessao[0])

        if eh_robo(user_agent):
            continue
        if not argumentos.com_estaticos and eh_estatico(uri):
            continue

        requisicoes_humanas += 1
        faixas[requisicao.get("client_ip", "?")] += 1
        paginas[normalizar_pagina(uri)] += 1
        horas[evento["_momento"].strftime("%d/%m %Hh")] += 1

    primeiro = min(e["_momento"] for e in eventos)
    ultimo = max(e["_momento"] for e in eventos)

    print("=" * 60)
    print(f"RELATÓRIO DE ACESSO — {argumentos.log.name}")
    print("=" * 60)
    print(f"Janela      : {primeiro:%d/%m/%Y %H:%M} a {ultimo:%d/%m/%Y %H:%M} (UTC)")
    print(f"Requisições : {len(eventos)} no total")
    print(f"              {requisicoes_humanas} após excluir robôs e arquivos estáticos")
    print(f"Faixas de IP: {len(faixas)} distintas (rede /24, não pessoas)")
    if sessoes_mcp:
        print(f"Sessões MCP : {len(sessoes_mcp)} distintas")

    erros = sum(quantidade for codigo, quantidade in status.items() if codigo >= 400)
    if erros:
        print(f"Erros (4xx/5xx): {erros} ({erros / len(eventos):.1%} das requisições)")

    total = requisicoes_humanas or None
    imprimir_secao("CLIENTES", clientes, total=len(eventos))
    imprimir_secao("PÁGINAS MAIS PEDIDAS", paginas, total=total)

    # Origem geográfica: conta faixas de rede, não requisições — uma faixa que pediu
    # 40 páginas continua sendo um ponto de origem, e contar acessos distorceria o mapa.
    geo = abrir_indice_geo(Path(argumentos.geo))
    if geo and faixas:
        paises, estados = Counter(), Counter()
        nao_localizadas = 0
        for faixa in faixas:
            local = geo.localizar(faixa)
            if local is None:
                nao_localizadas += 1
                continue
            pais, estado = local
            paises[pais] += 1
            estados[f"{pais} · {estado or '(estado não informado)'}"] += 1

        if paises:
            imprimir_secao("PAÍS (por faixa de rede)", paises, total=sum(paises.values()))
            imprimir_secao("ESTADO / REGIÃO", estados, total=sum(estados.values()))
            if nao_localizadas:
                print(f"\n  {nao_localizadas} faixa(s) sem correspondência no índice.")
    elif not geo:
        print(f"\n(Sem geolocalização: índice ausente em {argumentos.geo} —"
              " ver construir_indice_geo.py.)")

    imprimir_secao("FAIXAS DE REDE MAIS ATIVAS", faixas, total=total)

    if horas:
        print("\nPOR HORA (UTC)")
        print("-" * 14)
        for chave in sorted(horas):
            print(f"  {horas[chave]:6}  {chave}  {'█' * min(horas[chave], 40)}")

    print("\nO IP chega mascarado do Caddy: conta-se a faixa de rede, não a máquina.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
