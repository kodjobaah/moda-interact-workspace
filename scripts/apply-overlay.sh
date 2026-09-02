#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./scripts/apply-overlay.sh <overlay.zip>
  ./scripts/apply-overlay.sh <overlay.zip> --strip-wrapper

Default behavior:
  Treat archive paths as workspace-root-relative exactly as packaged.

Examples:
  docs/architecture/file.md
    -> <workspace>/docs/architecture/file.md

  scripts/tool.sh
    -> <workspace>/scripts/tool.sh

The script does NOT automatically strip a single top-level directory.

Use --strip-wrapper only for a deliberately wrapped archive such as:

  my-overlay/
    docs/
    scripts/

Overlay metadata files are ignored:
  MANIFEST.txt
  README-OVERLAY.md

README.md is NOT ignored because it may be a real workspace file.
EOF
}

OVERLAY_ZIP="${1:-}"
MODE="${2:-}"

if [[ -z "$OVERLAY_ZIP" ]]; then
  usage
  exit 2
fi

if [[ ! -f "$OVERLAY_ZIP" ]]; then
  echo "ERROR: overlay zip not found: $OVERLAY_ZIP" >&2
  exit 2
fi

if [[ -n "$MODE" && "$MODE" != "--strip-wrapper" ]]; then
  echo "ERROR: unknown option: $MODE" >&2
  usage
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "Extracting overlay: $OVERLAY_ZIP"

# Reject unsafe archive paths before extraction.
while IFS= read -r entry; do
  [[ -z "$entry" ]] && continue

  if [[ "$entry" == /* ]]; then
    echo "ERROR: overlay contains absolute path: $entry" >&2
    exit 1
  fi

  IFS='/' read -r -a parts <<< "$entry"
  for part in "${parts[@]}"; do
    if [[ "$part" == ".." ]]; then
      echo "ERROR: overlay contains parent-directory traversal: $entry" >&2
      exit 1
    fi
  done
done < <(unzip -Z1 "$OVERLAY_ZIP")

unzip -q "$OVERLAY_ZIP" -d "$TMP_DIR"

OVERLAY_ROOT="$TMP_DIR"

if [[ "$MODE" == "--strip-wrapper" ]]; then
  # Consider only non-metadata top-level entries when resolving an explicit
  # wrapper. Hidden workspace directories such as .codex and .claude count.
  mapfile -t TOP_LEVEL < <(
    find "$TMP_DIR" -mindepth 1 -maxdepth 1 \
      ! -name 'MANIFEST.txt' \
      ! -name 'README-OVERLAY.md' \
      ! -name '.DS_Store' \
      ! -name '__MACOSX' \
      -print
  )

  if [[ ${#TOP_LEVEL[@]} -ne 1 || ! -d "${TOP_LEVEL[0]}" ]]; then
    echo "ERROR: --strip-wrapper requires exactly one non-metadata top-level directory." >&2
    printf 'Found:\n' >&2
    printf '  %s\n' "${TOP_LEVEL[@]}" >&2
    exit 1
  fi

  OVERLAY_ROOT="${TOP_LEVEL[0]}"
fi

echo "Applying overlay from:"
echo "  $OVERLAY_ROOT"
echo
echo "Into workspace:"
echo "  $WORKSPACE_ROOT"
echo

rsync -av \
  --exclude='MANIFEST.txt' \
  --exclude='README-OVERLAY.md' \
  --exclude='.DS_Store' \
  --exclude='__MACOSX/' \
  --exclude='.git/' \
  "$OVERLAY_ROOT"/ "$WORKSPACE_ROOT"/

echo
echo "Overlay applied."
echo
echo "Review changes with:"
echo "  git status"
echo "  git diff"
