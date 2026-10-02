#!/usr/bin/env sh

# Moda Interact WooCommerce task toolchain bootstrap.
# Recommended: source scripts/bootstrap-woocommerce.sh
#
# This script deliberately does not install PHP, Composer, Docker, or Node.
# It reuses the canonical workspace Node bootstrap and verifies the remaining
# host prerequisites required by WordPress/WooCommerce development tasks.

_moda_woo_fail() {
  echo "ERROR: $*" >&2
}

_moda_woo_find_workspace() {
  _dir="$PWD"
  while [ "$_dir" != "/" ]; do
    if [ -f "$_dir/.nvmrc" ] && \
       [ -f "$_dir/scripts/bootstrap-node.sh" ] && \
       [ -d "$_dir/.codex/agents" ]; then
      printf '%s\n' "$_dir"
      return 0
    fi
    _dir="$(dirname "$_dir")"
  done
  return 1
}

if [ -n "${MODA_WORKSPACE_ROOT:-}" ]; then
  if [ ! -f "$MODA_WORKSPACE_ROOT/.nvmrc" ] || \
     [ ! -f "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh" ] || \
     [ ! -d "$MODA_WORKSPACE_ROOT/.codex/agents" ]; then
    _moda_woo_fail "MODA_WORKSPACE_ROOT does not identify a valid Moda Interact workspace: $MODA_WORKSPACE_ROOT"
    return 1 2>/dev/null || exit 1
  fi
else
  MODA_WORKSPACE_ROOT="$(_moda_woo_find_workspace)" || {
    _moda_woo_fail "Moda Interact workspace root not found."
    return 1 2>/dev/null || exit 1
  }
  export MODA_WORKSPACE_ROOT
fi

# Always run the canonical Node bootstrap so Woo tasks use the workspace .nvmrc
# rather than whichever Node happens to be first on PATH.
# shellcheck source=/dev/null
. "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh" || {
  _moda_woo_fail "WooCommerce bootstrap could not establish the workspace Node environment."
  return 1 2>/dev/null || exit 1
}

if ! command -v php >/dev/null 2>&1; then
  _moda_woo_fail "PHP is required for WooCommerce tasks but is not available on PATH. Install/configure PHP deliberately, then rerun the bootstrap."
  return 1 2>/dev/null || exit 1
fi

if ! command -v composer >/dev/null 2>&1; then
  _moda_woo_fail "Composer is required for WooCommerce tasks but is not available on PATH. Install/configure Composer deliberately, then rerun the bootstrap."
  return 1 2>/dev/null || exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  _moda_woo_fail "Docker is required for the wp-env WooCommerce development environment but is not available on PATH. Install/configure Docker deliberately, then rerun the bootstrap."
  return 1 2>/dev/null || exit 1
fi

if ! docker info >/dev/null 2>&1; then
  _moda_woo_fail "Docker is installed but the Docker daemon is not available. Start the configured Docker runtime, then rerun the bootstrap."
  return 1 2>/dev/null || exit 1
fi

MODA_PHP_VERSION="$(php -r 'echo PHP_VERSION;' 2>/dev/null)" || {
  _moda_woo_fail "PHP is present but its version could not be read."
  return 1 2>/dev/null || exit 1
}
export MODA_PHP_VERSION

MODA_COMPOSER_VERSION="$(composer --version --no-ansi 2>/dev/null | sed -n '1p')" || {
  _moda_woo_fail "Composer is present but its version could not be read."
  return 1 2>/dev/null || exit 1
}
export MODA_COMPOSER_VERSION

MODA_DOCKER_VERSION="$(docker version --format '{{.Client.Version}}' 2>/dev/null)" || {
  _moda_woo_fail "Docker is present but its client version could not be read."
  return 1 2>/dev/null || exit 1
}
export MODA_DOCKER_VERSION

echo "Moda Interact WooCommerce environment ready:"
echo "  workspace: $MODA_WORKSPACE_ROOT"
echo "  node:      $(command -v node) ($(node --version))"
echo "  npm:       $(command -v npm) ($(npm --version))"
echo "  php:       $(command -v php) ($MODA_PHP_VERSION)"
echo "  composer:  $(command -v composer) ($MODA_COMPOSER_VERSION)"
echo "  docker:    $(command -v docker) ($MODA_DOCKER_VERSION; daemon available)"

unset _dir
unset -f _moda_woo_find_workspace _moda_woo_fail 2>/dev/null || true
