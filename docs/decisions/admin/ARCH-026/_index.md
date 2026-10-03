# ARCH-026 Admin tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-read-shared-onboarding-milestone.md) | Source tenant onboarding completion from shared `Shop` state rather than requiring Shopify settings | Complete (Accepted, Attempt 1) | SHOPIFY-001, BACKGROUND-001 |
| [ADMIN-002](ADMIN-002-read-shared-international-context.md) | Read merchant international context from shared Shop state rather than requiring Shopify settings | Ready | DATABASE-002, SHOPIFY-002, ADMIN-001 |

## Execution frontier

ADMIN-001 is Complete / Accepted at Attempt 1. DATABASE-002, SHOPIFY-002 and ADMIN-001
are all architect-accepted Complete, so ADMIN-002 is Ready as the remaining materialised
ARCH-026 Admin migration frontier.

## ADMIN-001 Attempt 1 architect acceptance — 2026-10-03

**Accepted / Complete, Attempt 1.** Implementation `2fdbf181...` moves tenant-detail
onboarding authority to shared `commerce.Shop.onboardingCompleted`, preserves Shopify
settings only for existing recovery controls, and makes Woo tenant detail independent of
ShopSettings. The Admin-owned dashboard fixture mirrors Shopify onboarding values to the
shared Shop field and does not create Shopify settings for Woo Shops.

Focused onboarding tests pass 3/3, tenant information-architecture tests pass 4/4, Python
syntax/CLI checks pass, and submitted Prisma/typecheck/lint/build/diff checks pass.
Repository-wide residuals are inherited Admin baseline categories. ADMIN-002 is promoted
Ready.
