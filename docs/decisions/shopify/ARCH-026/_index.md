# ARCH-026 Shopify tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_app`.

Repository: `moda-interact`.

Coordinator: `moda_architect`.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [SHOPIFY-001](SHOPIFY-001-adopt-shared-onboarding-milestone.md) | Make shared `Shop.onboardingCompleted` authoritative for Shopify merchant lifecycle reads while mirroring completion to the retained legacy field | Complete | DATABASE-001 |
| [SHOPIFY-002](SHOPIFY-002-adopt-shared-international-context.md) | Make shared Shop international context authoritative for Shopify business reads while mirroring legacy ShopSettings values | Ready | DATABASE-002, SHOPIFY-001 |

## Execution frontier

SHOPIFY-001 is architect-accepted Complete at Attempt 1. SHOPIFY-002 is Ready because both DATABASE-002 and SHOPIFY-001 are architect-accepted Complete.
