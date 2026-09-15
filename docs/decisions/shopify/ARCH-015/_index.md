# ARCH-015 Shopify tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-SHOPIFY-001](SHOPIFY-001-live-top-up-offers.md) | complete | Resolve live top-up offers by Shopify current plan/meter intersected with ARCH-014 entitlement rows and render valid empty states. |
| [ARCH-015-SHOPIFY-002](SHOPIFY-002-purchase-admission.md) | ready | Create selected top-up purchase with fresh provider/ARCH-014 proof and same-handle single-flight. |
| [ARCH-015-SHOPIFY-003](SHOPIFY-003-refund-eligibility-hold.md) | pending | Permit normal refund hold only for current-provider-context positive-value purchases. |

## Current architect review state

`ARCH-015-SHOPIFY-002` Attempt 2 is **Changes Requested**.

The selected-offer request contract, fresh Shopify/ARCH-014 proof, second provider snapshot, persisted revalidated provider evidence, exact same-handle single-flight scope, fractional quantity support, null legacy-id fallback, and independent event-handle behavior are accepted.

One correction remains: the purchase write uses Prisma `$transaction(...)` without explicitly requesting Serializable isolation even though the canonical task requires a Serializable transaction in addition to the existing `Subscription ... FOR UPDATE` lock. The same task remains **Ready** for Attempt 3; no downstream task is promoted.

`ARCH-015-SHOPIFY-003` remains Pending until its declared prerequisites are complete.
