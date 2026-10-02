# ARCH-026 Admin tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-read-shared-onboarding-milestone.md) | Source tenant onboarding completion from shared `Shop` state rather than requiring Shopify settings | Pending | SHOPIFY-001, BACKGROUND-001 |
| [ADMIN-002](ADMIN-002-read-shared-international-context.md) | Read merchant international context from shared Shop state rather than requiring Shopify settings | Pending | DATABASE-002, SHOPIFY-002, ADMIN-001 |

## Execution frontier

ADMIN-001 remains Pending until both current production onboarding-completion writers have migrated to the shared field. ADMIN-002 remains Pending until DATABASE-002, SHOPIFY-002 and ADMIN-001 are architect-accepted Complete.
