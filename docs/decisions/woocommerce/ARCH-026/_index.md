# ARCH-026 WooCommerce tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_woocommerce`.

Repository: `moda-interact-woocommerce`.

Coordinator: `moda_architect`.

ARCH-026 is being defined iteratively. The extension foundation, local runtime/lifecycle hardening, PHP-side Moda API connection boundary and first production-shaped Woo Admin shell/connection experience, authenticated merchant Overview and production packaging hardening are materialised at this stage.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [WOOCOMMERCE-001](WOOCOMMERCE-001-establish-woocommerce-extension-foundation.md) | Establish a reproducible installable PHP + React WooCommerce extension foundation and minimal Woo Admin page | Complete | - |
| [WOOCOMMERCE-002](WOOCOMMERCE-002-establish-plugin-runtime-lifecycle-boundary.md) | Establish WordPress/WooCommerce/PHP compatibility, dependency gating and safe plugin activation/deactivation runtime | Complete | WOO-001 |
| [WOOCOMMERCE-003](WOOCOMMERCE-003-connect-plugin-to-hosted-moda-api.md) | Implement PHP-side site-control challenge, server-side installation credential storage, authenticated Moda API client and local connection REST facade | Complete | WOO-002, API-002 |
| [WOOCOMMERCE-004](WOOCOMMERCE-004-establish-admin-shell-connection-experience.md) | Replace the placeholder page with the real Woo Admin React shell and connection/setup experience over WOO-003 local REST | Complete (Accepted, Attempt 1) | WOO-003 |
| [WOOCOMMERCE-005](WOOCOMMERCE-005-render-authenticated-merchant-overview.md) | Render the first real authenticated merchant Overview from API-003 shared onboarding, Store Category and international-context data | Ready | WOO-004, API-003 |
| [WOOCOMMERCE-006](WOOCOMMERCE-006-harden-production-packaging-upgrade-lifecycle.md) | Harden the distributable plugin ZIP, production API default and install/upgrade/deactivate lifecycle | Pending | WOO-005, GATEWAY-001 |

## Execution frontier

```text
ARCH-026-WOOCOMMERCE-001  Complete (Attempt 4 Accepted)
ARCH-026-WOOCOMMERCE-002  Complete (Attempt 1 Accepted)
ARCH-026-WOOCOMMERCE-003  Complete (Attempt 1 Accepted)
ARCH-026-WOOCOMMERCE-004  Complete (Attempt 1 Accepted)
ARCH-026-WOOCOMMERCE-005  Ready
```

WOO-004 Attempt 1 establishes the accepted production-shaped Woo Admin connection shell
over WOO-003's local browser-safe REST facade. Browser code never receives the long-lived
installation credential or remote API configuration; all accepted connection states are
explicit and Connect/Reconnect/Retry behavior is bounded, single-flight and race-safe.

API-003 is architect-accepted Complete at Attempt 2, so WOO-005 now has both dependencies
satisfied and is Ready. WOO-006 remains Pending until WOO-005 is architect-accepted
Complete and its Gateway dependency is also satisfied. Preserve branch-local independent
chain state and do not execute WOO-006 early.
