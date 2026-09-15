# ARCH-015 Shopify tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-SHOPIFY-001](SHOPIFY-001-live-top-up-offers.md) | complete | Resolve live top-up offers by Shopify current plan/meter intersected with ARCH-014 entitlement rows and render valid empty states. |
| [ARCH-015-SHOPIFY-002](SHOPIFY-002-purchase-admission.md) | ready | Create selected top-up purchase with fresh provider/ARCH-014 proof and same-handle single-flight. |
| [ARCH-015-SHOPIFY-003](SHOPIFY-003-refund-eligibility-hold.md) | pending | Permit normal refund hold only for current-provider-context positive-value purchases. |

## Current architect review state

`ARCH-015-SHOPIFY-001` Attempt 2 is **Accepted — Complete**.

Implementation `6706491` closes the interim multi-offer purchase-action defect without
pulling `ARCH-015-SHOPIFY-002` purchase admission forward. Resolved offers remain
visible and ordered, but are display-only; the extended ARCH-014 merchant-pricing
reader from accepted/integrated `ARCH-014-SHOPIFY-002` remains intact.

Because `ARCH-015-SHARED-001`, `ARCH-015-DATABASE-001`, and
`ARCH-015-SHOPIFY-001` are now Complete, `ARCH-015-SHOPIFY-002` is **Ready**.

`ARCH-015-SHOPIFY-003` remains Pending until its declared prerequisites are complete.
