# ARCH-026 Admin tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-read-shared-onboarding-milestone.md) | Source tenant onboarding completion from shared `Shop` state rather than requiring Shopify settings | Ready | SHOPIFY-001, BACKGROUND-001 |
| [ADMIN-002](ADMIN-002-read-shared-international-context.md) | Read merchant international context from shared Shop state rather than requiring Shopify settings | Pending | DATABASE-002, SHOPIFY-002, ADMIN-001 |

## Execution frontier

ADMIN-001 is Ready because SHOPIFY-001 and BACKGROUND-001 are architect-accepted
Complete. DATABASE-002 and SHOPIFY-002 are also Complete, but ADMIN-002 remains Pending
until ADMIN-001 is architect-accepted Complete.
