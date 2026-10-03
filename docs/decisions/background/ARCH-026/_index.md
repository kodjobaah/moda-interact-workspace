# ARCH-026 Background tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-adopt-shared-onboarding-milestone.md) | Make shared `Shop.onboardingCompleted` authoritative for reconciliation/discount eligibility while mirroring completion to the retained legacy field | Ready | DATABASE-001 |
| [BACKGROUND-002](BACKGROUND-002-adopt-shared-international-context.md) | Read merchant language/time-zone/country from shared Shop state instead of Shopify settings | Pending | DATABASE-002, SHOPIFY-002, BACKGROUND-001 |

## Execution frontier

BACKGROUND-001 is Ready because DATABASE-001 is architect-accepted Complete. DATABASE-002 and SHOPIFY-002 are now architect-accepted Complete, so BACKGROUND-002 has those two dependencies satisfied but remains Pending until BACKGROUND-001 is architect-accepted Complete.
