#!/usr/bin/env bash
# =============================================================================
# setup.sh — prepara o ambiente da Advocacia Aberta.
#
# A MAIORIA das skills NÃO precisa de nada disto — elas rodam diretamente no agente.
# Este script instala as ferramentas de 4 skills:
#   • buscar-fontes  → bun         (busca de súmulas/leis/temas, offline)
#   • buscar-tjpr    → uv + python (busca de jurisprudência no TJPR)
#   • transcrever    → whisper + ffmpeg + modelo de voz (~539 MB)
#   • diagramar-peca → typst       (gera o PDF diagramado)
#
# Você não é obrigado a usar este script: a skill preparar-ambiente faz o mesmo
# com o agente guiando o processo. Use este aqui se preferir "clicar e instalar".
#
# Uso:   bash setup.sh
# (No macOS dá pra dar dois cliques em setup.command, que chama este arquivo.)
# =============================================================================
set -uo pipefail
cd "$(dirname "$0")"  # garante que rodamos na raiz do projeto

azul()  { printf "\033[1;34m%s\033[0m\n" "$1"; }
ok()    { printf "\033[1;32m✓ %s\033[0m\n" "$1"; }
aviso() { printf "\033[1;33m! %s\033[0m\n" "$1"; }

SO="$(uname -s)"
azul "== Advocacia Aberta — preparação do ambiente (${SO}) =="
echo "A maioria das skills já funciona sem nada disto. Vamos instalar só o extra."
echo

# --- bun (para buscar-fontes) -------------------------------------------------
azul "[1/4] bun — busca de fontes (Delfus)"
if command -v bun >/dev/null 2>&1; then ok "bun já instalado";
else
  echo "Instalando bun..."
  curl -fsSL https://bun.sh/install | bash || aviso "Falha ao instalar bun (precisa de internet; no Windows use o WSL)."
  export PATH="$HOME/.bun/bin:$PATH"
fi
if command -v bun >/dev/null 2>&1; then
  ( cd ferramentas/pesquisa/busca_delfus && bun install ) && ok "busca_delfus pronto" || aviso "bun install falhou em busca_delfus"
fi
echo

# --- uv (para buscar-tjpr) ----------------------------------------------------
azul "[2/4] uv — busca de jurisprudência (TJPR)"
if command -v uv >/dev/null 2>&1; then ok "uv já instalado";
else
  echo "Instalando uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh || aviso "Falha ao instalar uv (precisa de internet; no Windows use o WSL)."
  export PATH="$HOME/.local/bin:$PATH"
fi
if command -v uv >/dev/null 2>&1; then
  uv sync --project ferramentas/pesquisa/busca-tjpr && ok "busca-tjpr pronto (a 1ª busca baixa ~400 MB de navegador)" || aviso "uv sync falhou"
fi
echo

# --- typst (para diagramar-peca) ----------------------------------------------
azul "[3/4] typst — diagramação em PDF"
if command -v typst >/dev/null 2>&1; then ok "typst já instalado";
elif [ "$SO" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
  brew install typst && ok "typst instalado" || aviso "brew install typst falhou"
else
  aviso "Instale o typst manualmente: https://github.com/typst/typst (há instaladores prontos)."
fi
echo

# --- whisper (para transcrever) — opcional, download grande -------------------
azul "[4/4] whisper — transcrição de áudio/vídeo (opcional, ~539 MB)"
if [ "$SO" != "Darwin" ]; then
  aviso "Transcrição com whisper.cpp é mais simples no macOS. Em Windows/Linux, instale whisper.cpp e ffmpeg manualmente."
else
  read -r -p "Instalar whisper + ffmpeg e baixar o modelo de voz (~539 MB)? [s/N] " resp
  if [[ "${resp:-N}" =~ ^[sS]$ ]]; then
    if command -v brew >/dev/null 2>&1; then
      brew install whisper-cpp ffmpeg || aviso "brew install falhou"
      mkdir -p "$HOME/.whisper-models"
      if [ ! -f "$HOME/.whisper-models/ggml-medium-q5_0.bin" ]; then
        echo "Baixando o modelo (pode levar alguns minutos)..."
        curl -L -o "$HOME/.whisper-models/ggml-medium-q5_0.bin" \
          https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium-q5_0.bin \
          && ok "modelo de voz pronto" || aviso "download do modelo falhou"
      else ok "modelo de voz já existe"; fi
    else
      aviso "Homebrew não encontrado. Instale em https://brew.sh e rode de novo."
    fi
  else
    echo "Pulado. Você pode instalar depois com a skill preparar-ambiente ou rodando este script de novo."
  fi
fi
echo
azul "== Pronto =="
echo "Abra a pasta no Claude Code ou no Codex."
echo "Claude Code: use /nome. Codex: mencione \$nome ou escolha em /skills."
echo "Se algo falhou, peça ao agente para executar a skill preparar-ambiente."
