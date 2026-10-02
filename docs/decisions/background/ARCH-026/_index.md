# ARCH-026 Background tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-adopt-shared-onboarding-milestone.md) | Make shared `Shop.onboardingCompleted` authoritative for reconciliation/discount eligibility while mirroring completion to the retained legacy field | Pending | DATABASE-001 |
| [BACKGROUND-002](BACKGROUND-002-adopt-shared-international-context.md) | Read merchant language/time-zone/country from shared Shop state instead of Shopify settings | Pending | DATABASE-002, SHOPIFY-002, BACKGROUND-001 |

## Execution frontier

BACKGROUND-001 remains Pending until DATABASE-001 is architect-accepted Complete. BACKGROUND-002 remains Pending until DATABASE-002, SHOPIFY-002 and BACKGROUND-001 are architect-accepted Complete.
