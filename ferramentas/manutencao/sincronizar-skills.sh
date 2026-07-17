#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
FONTE="${REPO_ROOT}/.agents/skills/"
ESPELHO="${REPO_ROOT}/.claude/skills/"

if [ ! -d "${FONTE}" ]; then
  echo "Erro: fonte canônica não encontrada em .agents/skills/." >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "Erro: rsync não está instalado." >&2
  exit 1
fi

mkdir -p "${ESPELHO}"
rsync -a --delete --exclude='.DS_Store' "${FONTE}" "${ESPELHO}"

echo "Skills sincronizadas: .agents/skills/ → .claude/skills/"
python3 "${SCRIPT_DIR}/verificar_compatibilidade.py"
