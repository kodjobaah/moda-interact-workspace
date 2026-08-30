#!/usr/bin/env bash
set -euo pipefail

MODE="${1:---quick}"
case "$MODE" in
  --quick|--full|--production) ;;
  *)
    echo "Usage: scripts/workspace-doctor.sh [--quick|--full|--production]" >&2
    exit 2
    ;;
esac

find_workspace() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/.nvmrc" && -d "$dir/.codex/agents" ]]; then
      printf '%s\n' "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  return 1
}

WORKSPACE="$(find_workspace)" || {
  echo "FAIL workspace root not found" >&2
  exit 2
}

cd "$WORKSPACE"
source scripts/bootstrap-node.sh >/dev/null
exec python3 scripts/workspace-doctor.py "$MODE"
