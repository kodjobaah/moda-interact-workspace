# ARCH-015 background tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-BACKGROUND-001](BACKGROUND-001-purchase-reconciliation.md) | complete | Candidate-centric provider reconciliation is complete; durable purchase event handles drive exact provider proof without singular BillingPlan pack-meter authority. |
| [ARCH-015-BACKGROUND-002](BACKGROUND-002-cross-plan-consumption.md) | complete | Historical/non-current ACTIVE lots are consumed before current-context lots with fail-closed local context classification. |
| [ARCH-015-BACKGROUND-003](BACKGROUND-003-refund-correction-reconciliation.md) | ready | Existing billing scheduler processes durable refunds, submits safe negative/fractional corrections and reconciles completion. |

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

## Post SHOPIFY-003 Attempt 2 acceptance

`ARCH-015-SHOPIFY-003` is now Complete. Together with already-complete
`ARCH-015-SHARED-001`, `ARCH-015-DATABASE-001` and `ARCH-015-BACKGROUND-001`, this
satisfies every declared prerequisite of `ARCH-015-BACKGROUND-003`.

`ARCH-015-BACKGROUND-003` is therefore **Ready**.

`ARCH-015-BACKGROUND-002` remains independently Ready / in its own review workflow and
does not gate BACKGROUND-003.

## BACKGROUND-002 Attempt 3 acceptance

`ARCH-015-BACKGROUND-002` Attempt 3 is **Accepted — Complete**. The local Subscription
projection is now a fail-closed ordering hint only: valid ACTIVE contexts derive canonical
Shared provider identity (including native App Pricing with a null legacy provider id),
while malformed, ambiguous, TRIALING or otherwise unusable projections classify every
spendable ACTIVE lot as historical rather than throwing.

Historical-first FIFO, replay affinity, refund-held exclusion, Serializable/CAS behavior
and local `NOT_APPLICABLE` consumption evidence remain intact.

`ARCH-015-SYSTEM-TEST-001` remains Pending because `ARCH-015-BACKGROUND-003` and the
downstream `ARCH-015-ADMIN-001` are not yet Complete. `ARCH-015-BACKGROUND-003` remains
Ready and is the current Background implementation frontier.
