# ARCH-026 Admin tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-read-shared-onboarding-milestone.md) | Source tenant onboarding completion from shared `Shop` state rather than requiring Shopify settings | Complete (Accepted, Attempt 1) | SHOPIFY-001, BACKGROUND-001 |
| [ADMIN-002](ADMIN-002-read-shared-international-context.md) | Read merchant international context from shared Shop state rather than requiring Shopify settings | Complete (Accepted, Attempt 1) | DATABASE-002, SHOPIFY-002, ADMIN-001 |

## Execution frontier

ADMIN-001 and ADMIN-002 are Complete / Accepted at Attempt 1. The materialised ARCH-026
Admin migration stream is complete; there is no further Admin task to promote from ADMIN-002.

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

## ADMIN-002 Attempt 1 architect acceptance — 2026-10-03

**Accepted / Complete, Attempt 1.** Implementation `84a8329d16844f289a4cfce43724b3b2de3819e0`
moves merchant-support target-language authority from `shopify.ShopSettings.defaultLanguageTag`
to shared `commerce.Shop.defaultLanguageTag`, preserves the support-thread `FOR UPDATE OF t`
lock, existing normalization / `en-GB` fallback, translation-state writes and post-commit queue
ordering, and proves Woo-like operation without a ShopSettings row. Focused support behavior /
security coverage passes 13/13 and UI security coverage passes 7/7; Prisma generation, typecheck,
targeted lint, build, static audit and diff checks pass. The two repository-wide residual assertions
are inherited from the exact pre-task base and are outside this bounded source migration.
