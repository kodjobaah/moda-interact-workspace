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
| [WOOCOMMERCE-003](WOOCOMMERCE-003-connect-plugin-to-hosted-moda-api.md) | Implement PHP-side site-control challenge, server-side installation credential storage, authenticated Moda API client and local connection REST facade | Pending | WOO-002, API-002 |
| [WOOCOMMERCE-004](WOOCOMMERCE-004-establish-admin-shell-connection-experience.md) | Replace the placeholder page with the real Woo Admin React shell and connection/setup experience over WOO-003 local REST | Pending | WOO-003 |
| [WOOCOMMERCE-005](WOOCOMMERCE-005-render-authenticated-merchant-overview.md) | Render the first real authenticated merchant Overview from API-003 shared onboarding, Store Category and international-context data | Pending | WOO-004, API-003 |
| [WOOCOMMERCE-006](WOOCOMMERCE-006-harden-production-packaging-upgrade-lifecycle.md) | Harden the distributable plugin ZIP, production API default and install/upgrade/deactivate lifecycle | Pending | WOO-005, GATEWAY-001 |

## Execution frontier

```text
ARCH-026-WOOCOMMERCE-001  Complete (Attempt 4 Accepted)
ARCH-026-WOOCOMMERCE-002  Complete (Attempt 1 Accepted)
ARCH-026-WOOCOMMERCE-003  Pending (waiting for ARCH-026-API-002)
```

WOO-002 Attempt 1 established the native WordPress/WooCommerce/PHP requirements,
bounded runtime guard, delayed single-run Woo initialisation and safe local
activation/deactivation lifecycle. Both frozen compatibility matrices passed, and
the WOO-001 Admin foundation remained functional.

WOO-003's WOO-002 dependency is now satisfied, but WOO-003 also depends on accepted
API-002. API-002 remains Pending in this snapshot, so WOO-003 remains Pending. WOO-004
remains Pending until WOO-003 is architect-accepted Complete. WOO-005 then requires both
accepted WOO-004 and API-003 before it can render the first real merchant Overview. WOO-006
waits for accepted WOO-005 plus GATEWAY-001, then hardens the final ARCH-026 distribution
artifact and local upgrade lifecycle. Do not execute WOO-003 through WOO-006 early.
