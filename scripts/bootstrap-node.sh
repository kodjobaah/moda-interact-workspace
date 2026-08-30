#!/usr/bin/env sh

# Moda Interact Node/NVM bootstrap.
# Recommended: source scripts/bootstrap-node.sh
# `.nvmrc` is the only Node version source of truth.

_moda_fail() {
  echo "ERROR: $*" >&2
  return 1
}

_moda_find_workspace() {
  _dir="$PWD"
  while [ "$_dir" != "/" ]; do
    if [ -f "$_dir/.nvmrc" ] && [ -d "$_dir/.codex/agents" ]; then
      printf '%s\n' "$_dir"
      return 0
    fi
    _dir="$(dirname "$_dir")"
  done
  return 1
}

MODA_WORKSPACE_ROOT="$(_moda_find_workspace)" || {
  _moda_fail "Moda Interact workspace root not found."
  return 1 2>/dev/null || exit 1
}
export MODA_WORKSPACE_ROOT

_selector="$(tr -d '[:space:]' < "$MODA_WORKSPACE_ROOT/.nvmrc")"
if [ -z "$_selector" ]; then
  _moda_fail "$MODA_WORKSPACE_ROOT/.nvmrc is empty."
  return 1 2>/dev/null || exit 1
fi

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"

if ! command -v nvm >/dev/null 2>&1 && [ -s "$NVM_DIR/nvm.sh" ]; then
  . "$NVM_DIR/nvm.sh"
fi

if command -v nvm >/dev/null 2>&1; then
  if ! nvm use --silent "$_selector"; then
    echo "ERROR: Node '$_selector' from .nvmrc is not installed." >&2
    echo "Install it with: nvm install $_selector" >&2
    return 1 2>/dev/null || exit 1
  fi
else
  # Fallback only for an exact version already installed under NVM.
  _exact="${_selector#v}"
  case "$_exact" in
    *[!0-9.]*|'')
      _moda_fail "NVM is unavailable and .nvmrc is not an exact version: $_selector"
      return 1 2>/dev/null || exit 1
      ;;
  esac

  _node_bin="$NVM_DIR/versions/node/v$_exact/bin"
  if [ -x "$_node_bin/node" ]; then
    PATH="$_node_bin:$PATH"
    export PATH
  else
    _moda_fail "Node $_selector is unavailable through NVM and $_node_bin."
    return 1 2>/dev/null || exit 1
  fi
fi

if ! command -v node >/dev/null 2>&1; then
  _moda_fail "node did not resolve after bootstrap."
  return 1 2>/dev/null || exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  _moda_fail "npm did not resolve after bootstrap."
  return 1 2>/dev/null || exit 1
fi

_exact="${_selector#v}"
case "$_exact" in
  *[!0-9.]*|'') ;;
  *)
    if [ "$(node --version)" != "v$_exact" ]; then
      _moda_fail "Expected Node v$_exact from .nvmrc; got $(node --version)."
      return 1 2>/dev/null || exit 1
    fi
    ;;
esac

export MODA_NODE_VERSION="$(node --version)"

echo "Moda Interact Node environment ready:"
echo "  workspace: $MODA_WORKSPACE_ROOT"
echo "  selector:  $_selector"
echo "  node:      $(command -v node) ($(node --version))"
echo "  npm:       $(command -v npm) ($(npm --version))"
for _tool in npx corepack shopify; do
  if command -v "$_tool" >/dev/null 2>&1; then
    echo "  $_tool: $(command -v "$_tool")"
  fi
done

unset _dir _selector _exact _node_bin _tool
unset -f _moda_find_workspace _moda_fail 2>/dev/null || true
