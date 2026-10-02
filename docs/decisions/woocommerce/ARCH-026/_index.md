# ARCH-026 WooCommerce tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_woocommerce`.

Repository: `moda-interact-woocommerce`.

Coordinator: `moda_architect`.

ARCH-026 is being defined iteratively. The extension foundation, local runtime/lifecycle hardening and the PHP-side Moda API connection boundary are materialised at this stage.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [WOOCOMMERCE-001](WOOCOMMERCE-001-establish-woocommerce-extension-foundation.md) | Establish a reproducible installable PHP + React WooCommerce extension foundation and minimal Woo Admin page | Blocked | - |
| [WOOCOMMERCE-002](WOOCOMMERCE-002-establish-plugin-runtime-lifecycle-boundary.md) | Establish WordPress/WooCommerce/PHP compatibility, dependency gating and safe plugin activation/deactivation runtime | Pending | WOO-001 |
| [WOOCOMMERCE-003](WOOCOMMERCE-003-connect-plugin-to-hosted-moda-api.md) | Implement PHP-side site-control challenge, server-side installation credential storage, authenticated Moda API client and local connection REST facade | Pending | WOO-002, API-002 |

## Execution frontier

```text
No WooCommerce task is Ready.
```

The repository-provisioning gate has been satisfied. WOO-001 is currently Blocked by
a host WooCommerce-toolchain prerequisite recorded in its Completion Report; no plugin
implementation work has completed yet. WOO-002 remains Pending and cannot become Ready
until WOO-001 is architect-accepted Complete. WOO-003 additionally depends on accepted API-002 and remains Pending until both WOO-002 and API-002 are Complete.

Do not execute WOO-002 or WOO-003 early to work around an upstream blocker.
