#!/usr/bin/env sh

# Moda Interact Node/NVM bootstrap.
#
# Usage (recommended):
#
#   source scripts/bootstrap-node.sh
#
# It is deliberately version-independent. The workspace `.nvmrc` is the
# single source of truth.
#
# The script avoids `set -e`, `set -u` and `set -o pipefail` because it is
# intended to be sourced and must not unexpectedly alter the caller's shell.

_moda_node_fail() {
  echo "ERROR: $*" >&2
  return 1
}

# Locate the workspace root by walking upward. This works when the caller is in
# the workspace root or inside one of its submodule directories.
_moda_dir="$PWD"
MODA_WORKSPACE_ROOT=""

while [ "$_moda_dir" != "/" ]; do
  if [ -f "$_moda_dir/.nvmrc" ] && [ -d "$_moda_dir/.codex/agents" ]; then
    MODA_WORKSPACE_ROOT="$_moda_dir"
    break
  fi
  _moda_dir="$(dirname "$_moda_dir")"
done

if [ -z "$MODA_WORKSPACE_ROOT" ]; then
  _moda_node_fail "Moda Interact workspace root not found. Expected .nvmrc and .codex/agents in a parent directory."
  return 1 2>/dev/null || exit 1
fi

export MODA_WORKSPACE_ROOT

_moda_nvmrc="$MODA_WORKSPACE_ROOT/.nvmrc"
_moda_selector="$(tr -d '[:space:]' < "$_moda_nvmrc")"

if [ -z "$_moda_selector" ]; then
  _moda_node_fail "$_moda_nvmrc is empty."
  return 1 2>/dev/null || exit 1
fi

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"

# Load NVM when the current shell has not already done so.
if ! command -v nvm >/dev/null 2>&1; then
  if [ -s "$NVM_DIR/nvm.sh" ]; then
    # shellcheck disable=SC1090
    . "$NVM_DIR/nvm.sh"
  fi
fi

if command -v nvm >/dev/null 2>&1; then
  # Passing the selector explicitly means the script works regardless of the
  # caller's current directory.
  if ! nvm use --silent "$_moda_selector"; then
    echo "ERROR: Node version '$_moda_selector' selected by .nvmrc is not installed." >&2
    echo "Install it with:" >&2
    echo "  nvm install $_moda_selector" >&2
    return 1 2>/dev/null || exit 1
  fi
else
  # Last-resort fallback for non-interactive shells where nvm.sh cannot be
  # loaded but an exact semver NVM installation already exists.
  _moda_exact="${_moda_selector#v}"

  case "$_moda_exact" in
    *[!0-9.]*|'')
      _moda_node_fail "NVM is unavailable and .nvmrc uses non-exact selector '$_moda_selector'."
      return 1 2>/dev/null || exit 1
      ;;
  esac

  _moda_node_bin="$NVM_DIR/versions/node/v$_moda_exact/bin"

  if [ -x "$_moda_node_bin/node" ]; then
    PATH="$_moda_node_bin:$PATH"
    export PATH
  else
    _moda_node_fail "Node '$_moda_selector' is not available through NVM or $_moda_node_bin."
    return 1 2>/dev/null || exit 1
  fi
fi

if ! command -v node >/dev/null 2>&1; then
  _moda_node_fail "Node did not resolve after workspace bootstrap."
  return 1 2>/dev/null || exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  _moda_node_fail "npm did not resolve after workspace bootstrap."
  return 1 2>/dev/null || exit 1
fi

# For exact semver selectors, verify that the active version is precisely the
# workspace-selected version. NVM aliases such as lts/* are left to NVM.
_moda_exact="${_moda_selector#v}"
case "$_moda_exact" in
  *[!0-9.]*|'')
    ;;
  *)
    if [ "$(node --version)" != "v$_moda_exact" ]; then
      _moda_node_fail "Expected Node v$_moda_exact from .nvmrc, got $(node --version)."
      return 1 2>/dev/null || exit 1
    fi
    ;;
esac

export MODA_NODE_VERSION="$(node --version)"

echo "Moda Interact Node environment ready:"
echo "  workspace: $MODA_WORKSPACE_ROOT"
echo "  selector:  $_moda_selector"
echo "  node:      $(command -v node) ($(node --version))"
echo "  npm:       $(command -v npm) ($(npm --version))"

for _moda_tool in npx corepack shopify; do
  if command -v "$_moda_tool" >/dev/null 2>&1; then
    echo "  $_moda_tool: $(command -v "$_moda_tool")"
  fi
done

unset _moda_dir _moda_nvmrc _moda_selector _moda_exact _moda_node_bin _moda_tool
unset -f _moda_node_fail 2>/dev/null || true
