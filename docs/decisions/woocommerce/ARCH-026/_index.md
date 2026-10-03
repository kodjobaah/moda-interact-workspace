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
| [WOOCOMMERCE-004](WOOCOMMERCE-004-establish-admin-shell-connection-experience.md) | Replace the placeholder page with the real Woo Admin React shell and connection/setup experience over WOO-003 local REST | Ready | WOO-003 |
| [WOOCOMMERCE-005](WOOCOMMERCE-005-render-authenticated-merchant-overview.md) | Render the first real authenticated merchant Overview from API-003 shared onboarding, Store Category and international-context data | Pending | WOO-004, API-003 |
| [WOOCOMMERCE-006](WOOCOMMERCE-006-harden-production-packaging-upgrade-lifecycle.md) | Harden the distributable plugin ZIP, production API default and install/upgrade/deactivate lifecycle | Pending | WOO-005, GATEWAY-001 |

## Execution frontier

```text
ARCH-026-WOOCOMMERCE-001  Complete (Attempt 4 Accepted)
ARCH-026-WOOCOMMERCE-002  Complete (Attempt 1 Accepted)
ARCH-026-WOOCOMMERCE-003  Complete (Attempt 1 Accepted)
ARCH-026-WOOCOMMERCE-004  Ready
```

WOO-003 Attempt 1 implements the accepted API-002 PHP consumer boundary: explicit
public/local-development site identity policy, one-attempt HMAC challenge proof,
server-side non-autoloaded installation credential storage, strict authenticated remote
probe and browser-safe local REST state. Focused PHP validation, production packaging and
the live `wp-env` HTTPS-fixture route flow passed.

WOO-004 is Ready because WOO-003 was its only dependency. API-003 is independently
architect-accepted Complete at Attempt 2, but WOO-005 remains Pending until WOO-004 is
also architect-accepted Complete. WOO-006 remains Pending until accepted WOO-005 plus
GATEWAY-001. Do not execute WOO-005 or WOO-006 early.
WOO-002 Attempt 1 established the native WordPress/WooCommerce/PHP requirements,
bounded runtime guard, delayed single-run Woo initialisation and safe local
activation/deactivation lifecycle. Both frozen compatibility matrices passed, and
the WOO-001 Admin foundation remained functional.

WOO-003's WOO-002 and API-002 dependencies are now both architect-accepted Complete,
so WOO-003 is Ready. API-002's accepted OpenAPI v1 contract is the authoritative remote
connection/authentication boundary that WOO-003 must consume; WOO-003 must not redefine
the remote status/error semantics or expose credentials to React. API-003 is now architect-accepted
Complete at Attempt 2. WOO-004 remains Pending until WOO-003 is architect-accepted Complete,
and WOO-005 remains Pending because it still requires accepted WOO-004 even though its API-003
dependency is satisfied. WOO-006 waits for accepted WOO-005 plus GATEWAY-001. Do not execute
WOO-004 through WOO-006 early.
