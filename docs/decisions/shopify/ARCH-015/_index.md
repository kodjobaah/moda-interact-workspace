# ARCH-015 Shopify tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-SHOPIFY-001](SHOPIFY-001-live-top-up-offers.md) | complete | Resolve live top-up offers by Shopify current plan/meter intersected with ARCH-014 entitlement rows and render valid empty states. |
| [ARCH-015-SHOPIFY-002](SHOPIFY-002-purchase-admission.md) | complete | Create selected top-up purchase with fresh provider/ARCH-014 proof and same-handle single-flight. |
| [ARCH-015-SHOPIFY-003](SHOPIFY-003-refund-eligibility-hold.md) | complete | Permit normal refund hold only for current-provider-context positive-value purchases. |
| [ARCH-015-SHOPIFY-004](SHOPIFY-004-provider-meter-mutation-serialization.md) | complete | Serialize purchase/refund admission per `(shopId,eventHandle)`, close automatic-correction reactivation races, make offer eligibility per meter and correct provider price presentation. |

## Current architect review state

`ARCH-015-SHOPIFY-002` Attempt 3 is **Accepted — Complete**.

The purchase-admission contract is now complete: selected-event admission, fresh Shopify/ARCH-014 proof, second provider snapshot, persisted revalidated provider evidence, exact same-handle single-flight scope, fractional quantity support, null legacy-id fallback, independent event-handle behavior, Serializable isolation and the existing `Subscription ... FOR UPDATE` lock are all in place.

`ARCH-015-BACKGROUND-001` is now Ready because all of its declared prerequisites are Complete.

`ARCH-015-SHOPIFY-003` remains Pending because it additionally depends on `ARCH-015-BACKGROUND-001`.


## Post BACKGROUND-001 Attempt 4 acceptance

`ARCH-015-BACKGROUND-001` is now **Complete**, so every declared prerequisite of
`ARCH-015-SHOPIFY-003` is Complete. `ARCH-015-SHOPIFY-003` is therefore **Ready**.

`ARCH-015-BACKGROUND-003` remains Pending until SHOPIFY-003 is architect-accepted
Complete.


## Post SHOPIFY-003 Attempt 2 acceptance

`ARCH-015-SHOPIFY-003` Attempt 2 is **Accepted — Complete**.

Refund admission now requires a nonblank authenticated Shopify shop identity, strictly
positive provider purchase value and fresh current-provider-context proof before any new
refund hold can be created. Matching `ACTIVE` and `TRIALING` provider contracts are both
valid current-context candidates; all identity, plan, local billing-period, exact cycle
and live event-handle checks remain mandatory.

Historical/context-mismatched purchases remain ACTIVE and spendable, while eligible
current-context requests create only the durable REQUESTED refund/hold. Background owns
provider correction and completion.

`ARCH-015-BACKGROUND-003` is now Ready because every declared prerequisite is Complete.


## Post-implementation integration audit — 2026-09-16

A meticulous cross-repository ARCH-015 audit found that individually accepted tasks did not yet provide one common provider-meter mutation boundary. `ARCH-015-SHOPIFY-004` was therefore introduced as a bounded correction task and is now **Accepted — Complete**. It is a bounded correction task: no schema change, no new queue and no new lock model. It reuses the existing per-shop `Subscription ... FOR UPDATE` lock so purchase and refund admission share the same `(shopId,eventHandle)` busy predicate.

`ARCH-015-BACKGROUND-004` is an independent parallel correction task; it is not a blocking implementation dependency of SHOPIFY-004. This SHOPIFY-004 branch snapshot predates its later architect acceptance, so Background task metadata is not rewritten here. Terminal system testing remains intentionally deferred until after manual testing and must not be launched from this task.

## Post-review update — SHOPIFY-004 Attempt 1 Accepted

`ARCH-015-SHOPIFY-004` Attempt 1 is **Accepted — Complete**. The common provider-meter admission boundary, automatic-correction reactivation CAS, per-handle offer eligibility and deterministic next-unit provider price are accepted. The small Dutch matrix wording difference and missing one-for-one unit scenarios are recorded as non-blocking follow-up validation observations. No further SHOPIFY-004 implementation attempt is required.
