# ARCH-015 Shopify tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-SHOPIFY-001](SHOPIFY-001-live-top-up-offers.md) | ready | Resolve live top-up offers by Shopify current plan/meter intersected with ARCH-014 entitlement rows and render valid empty states. |
| [ARCH-015-SHOPIFY-002](SHOPIFY-002-purchase-admission.md) | pending | Create selected top-up purchase with fresh provider/ARCH-014 proof and same-handle single-flight. |
| [ARCH-015-SHOPIFY-003](SHOPIFY-003-refund-eligibility-hold.md) | pending | Permit normal refund hold only for current-provider-context positive-value purchases. |

## Current architect review state

`ARCH-015-SHOPIFY-001` Attempt 1 received **Changes Requested** after review against the latest ARCH-014 extension. The live offer resolver itself is accepted, but Attempt 2 must preserve the extended ARCH-014 merchant-pricing reader and keep resolved top-up cards display-only until `ARCH-015-SHOPIFY-002` implements selected-`eventHandle` purchase admission.

Preserve `attempt: 1`, `executor: null`, and `claimed_at: null` before reclaim. The next `/moda-task ARCH-015-SHOPIFY-001` claim must create Attempt 2 exactly once. `ARCH-015-SHOPIFY-002` remains Pending until architect acceptance of SHOPIFY-001.
