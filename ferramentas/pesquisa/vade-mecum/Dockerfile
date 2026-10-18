# Imagem do MCP jurídico (Vade Mecum) para execução hospedada em container.
#
# O contexto de build é este diretório, que é auto-contido: o motor (src/) e o
# acervo (data/, ~95 MB em 290 arquivos JSON) vivem lado a lado.
#
#   docker build -t advocacia-aberta-mcp:<tag> ferramentas/pesquisa/vade-mecum
#
# Isto NÃO substitui a execução por systemd na VM (deploy/vade-mecum-mcp.service),
# que continua sendo a produção de mcp.advocaciaaberta.org. É um segundo modo de
# execução, para o mesmo código, em cluster.
#
# Memória: o acervo é carregado inteiro em memória no import (src/search/*.ts usa
# require), então o consumo é alto e constante desde o boot — medido em 30/07/2026:
# 574 MiB em repouso, 640 MiB após buscas. Quem for definir limites de container
# precisa reservar acima disso; 512 MiB mata o processo antes da primeira resposta.
#
# Prontidão: como o carregamento é síncrono no import, "está ouvindo" já implica
# "acervo carregado". O /health de src/http.ts serve como sonda de liveness e de
# readiness, sem janela de warm-up depois do listen.
#
# PORT e MCP_PATH repetem os defaults de src/http.ts; ficam explícitos para
# documentar o contrato com quem faz proxy (o endpoint MCP é /mcp na raiz).

# ─── Estágio 1: dependências (cacheado por package.json + bun.lock) ───────────
FROM oven/bun:1.3-slim AS deps
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile --production

# ─── Estágio 2: runtime ───────────────────────────────────────────────────────
FROM oven/bun:1.3-slim
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY package.json bun.lock tsconfig.json ./
COPY src ./src
COPY data ./data

ENV PORT=8080
ENV MCP_PATH=/mcp

# Usuário não-root: a imagem base oven/bun já traz o usuário `bun` (uid 1000).
# Nada é escrito em disco no runtime — o acervo é somente leitura.
USER bun

EXPOSE 8080

CMD ["bun", "run", "src/http.ts"]
