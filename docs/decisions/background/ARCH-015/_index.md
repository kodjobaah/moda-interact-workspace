# ARCH-015 background tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-BACKGROUND-001](BACKGROUND-001-purchase-reconciliation.md) | complete | Candidate-centric provider reconciliation is complete; durable purchase event handles drive exact provider proof without singular BillingPlan pack-meter authority. |
| [ARCH-015-BACKGROUND-002](BACKGROUND-002-cross-plan-consumption.md) | ready | Spend historical purchased lots before current refundable lots. |
| [ARCH-015-BACKGROUND-003](BACKGROUND-003-refund-correction-reconciliation.md) | pending | Existing billing scheduler processes durable refunds, submits safe negative/fractional corrections and reconciles completion. |

## Current architect review state

`ARCH-015-BACKGROUND-001` Attempt 4 is **Accepted — Complete**.

The normal Background purchase-reconciliation path is now independent of the retired
singular BillingPlan pack-meter configuration. Durable REQUESTED+REPORTED purchases use
their own stored event handles against the complete live Shopify provider snapshot.

`ARCH-015-BACKGROUND-002` is now Ready. `ARCH-015-BACKGROUND-003` remains Pending until
`ARCH-015-SHOPIFY-003` is Complete.


## BACKGROUND-002 Attempt 2 review

`ARCH-015-BACKGROUND-002` remains **Ready** for Attempt 3. Attempt 2 correctly added
period-aware Shared provider-context derivation and ACTIVE-only current classification,
but malformed native-App-Pricing local projection evidence can still throw from the
ordering hint instead of failing closed to historical FIFO. Attempt 3 is limited to that
fail-closed classification correction and focused regressions.
