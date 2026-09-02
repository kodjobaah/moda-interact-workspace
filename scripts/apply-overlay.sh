#!/usr/bin/env bash

set -euo pipefail

OVERLAY_ZIP="${1:-}"

if [[ -z "$OVERLAY_ZIP" ]]; then
  echo "Usage: $0 <overlay.zip>"
  exit 1
fi

if [[ ! -f "$OVERLAY_ZIP" ]]; then
  echo "Overlay not found: $OVERLAY_ZIP"
  exit 1
fi

WORKSPACE_ROOT="$(pwd)"

if [[ ! -d "$WORKSPACE_ROOT/docs" ]]; then
  echo "Error: run this script from the moda-interact-workspace root."
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Extracting overlay: $OVERLAY_ZIP"

unzip -q "$OVERLAY_ZIP" -d "$TMP_DIR"

# Some overlays contain a single top-level directory.
ENTRIES=("$TMP_DIR"/*)

if [[ ${#ENTRIES[@]} -eq 1 && -d "${ENTRIES[0]}" ]]; then
  OVERLAY_ROOT="${ENTRIES[0]}"
else
  OVERLAY_ROOT="$TMP_DIR"
fi

echo "Applying overlay from:"
echo "  $OVERLAY_ROOT"
echo
echo "Into workspace:"
echo "  $WORKSPACE_ROOT"
echo

rsync -av \
  --exclude='README.md' \
  "$OVERLAY_ROOT"/ \
  "$WORKSPACE_ROOT"/

echo
echo "Overlay applied."
echo
echo "Review changes with:"
echo "  git status"
echo "  git diff"
