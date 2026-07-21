#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
FONTE="${REPO_ROOT}/.agents/skills/"

if [ ! -d "${FONTE}" ]; then
  echo "Erro: fonte canônica não encontrada em .agents/skills/." >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "Erro: rsync não está instalado." >&2
  exit 1
fi

# Bundle curado publicado como plugin Codex/OpenAI (ver .codex-plugin/README.md).
# Fluxo que funciona no ChatGPT Web hospedado: organizar → diagnosticar → buscar-fontes
# (acervo via MCP) → redigir → revisar. buscar-tjpr/transcrever/diagramar seguem fora
# (dependem de scraping/whisper/typst locais).
BUNDLE_CODEX_SKILLS=(
  "1.1-organizar-caso"
  "2.1-diagnosticar"
  "2.2-buscar-fontes"
  "3.1-redigir-peca"
  "4.1-revisar-peca"
)

# Todos os espelhos são gerados a partir da fonte canônica .agents/skills/.
# Nunca editar um espelho à mão — editar a fonte e rodar este script.
sincronizar() {
  local destino="$1"
  mkdir -p "${destino}"
  rsync -a --delete --exclude='.DS_Store' "${FONTE}" "${destino}"
}

# Gera um bundle com apenas as skills da whitelist (subconjunto da fonte canônica).
sincronizar_curado() {
  local destino="$1"
  shift
  rm -rf "${destino}"
  mkdir -p "${destino}"
  local skill
  for skill in "$@"; do
    if [ ! -d "${FONTE}${skill}" ]; then
      echo "Erro: skill '${skill}' da whitelist não existe em .agents/skills/." >&2
      exit 1
    fi
    rsync -a --exclude='.DS_Store' "${FONTE}${skill}" "${destino}"
  done
}

sincronizar "${REPO_ROOT}/.claude/skills/"   # adaptador Claude Code (nível projeto)
sincronizar "${REPO_ROOT}/skills/"           # adaptador de plugin (lido via .claude-plugin/)
sincronizar_curado "${REPO_ROOT}/.codex-plugin/skills/" "${BUNDLE_CODEX_SKILLS[@]}"  # bundle curado do plugin Codex

echo "Skills sincronizadas: .agents/skills/ → .claude/skills/, → skills/ e → .codex-plugin/skills/ (curado)"
python3 "${SCRIPT_DIR}/verificar_compatibilidade.py"
