---
id: ARCH-015
title: Recovery-credit purchase, reconciliation, cross-subscription consumption and refund refactor
status: in_progress
coordinator: moda_architect
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-015: Recovery-credit purchase, reconciliation, cross-subscription consumption and refund refactor

## Purpose

Refactor recovery-credit top-up purchase, provider reconciliation, cross-plan consumption and refunds so that:

- Shopify App Pricing remains provider/subscription/monetary authority.
- ARCH-014 `MerchantPricingPlan` + `MerchantPricingUsageEvent` provide Moda's plan→meter→`creditsGrantedPerUnit` entitlement semantics.
- `RecoveryCreditPurchase` remains the durable ownership ledger.
- purchased credits survive plan and billing-cycle changes.
- only current-provider-context purchases are normally refundable.
- HTTP 202 from App Events is submission receipt only, never entitlement/refund completion.
- automated refund corrections complete only after provider reconciliation.
- Admin remains the explicit manual REFUND/CREDIT fallback.
- zero resolved top-up offers is a valid merchant state and renders "No top ups are currently available for this subscription."

## Authority boundary

```text
Shopify App Pricing
  current active subscription
  current plan handle
  live usage meter membership
  live pricing/currency
  current provider usage quantity/cost
  billing cycle
  pending subscription changes

ARCH-014 MerchantPricing*
  planHandle -> usage-event membership
  usage-event display/order semantics
  creditsGrantedPerUnit

RecoveryCreditPurchase / Refund
  immutable local purchase/refund provenance
  current owned credits
  reservation/consumption/refund state

Background
  App Event publication
  purchase provider reconciliation
  scheduled refund correction/reconciliation

Admin
  exceptional manual provider REFUND/CREDIT evidence path only
```

ARCH-014 MUST NOT replace Shopify live billing truth. Conversely, Shopify does not define how many Moda recovery credits one usage-event unit grants; that comes from ARCH-014.

## Canonical top-up offer correlation

Never resolve an offer globally by `eventHandle`.

Resolve:

```text
Shopify activeSubscription.planHandle
      ->
MerchantPricingPlan.shopifyPlanHandle

then intersect:

MerchantPricingPlan.usageEvents[].eventHandle
      WITH
Shopify activeSubscription.usageItems[].handle
```

A resolved offer receives:

```text
creditsGranted          <- ARCH-014 creditsGrantedPerUnit
cataloguePosition       <- ARCH-014 usage-event position
providerPrice           <- Shopify activeSubscription usage item
providerUsage           <- Shopify activeSubscription usage item
eventHandle             <- exact matched handle
```

For an already-contracted merchant, `MerchantPricingPlan.isActive` is NOT a contract-validity check. It is catalogue visibility. The live Shopify contract decides whether the merchant currently has the plan/meter.

## Empty-state rule

The top-up section is always rendered on the billing surface.

If there are zero valid intersections between current Shopify usage meters and ARCH-014 usage events:

```text
No top ups are currently available for this subscription.
```

This is not a provider error.

Provider/API verification failure is distinct and must render a temporary verification-unavailable state while purchases fail closed.

## Provider-context identity

Native App Pricing may have `legacySubscriptionId = null`.

Use one canonical Shared helper:

```text
legacy provider id present
  -> trimmed raw provider id

legacy provider id absent
  -> app-pricing:v1:<encoded planHandle>:<periodStart ISO>:<periodEnd ISO>
```

Store this derived identity in existing purchase provenance `providerSubscriptionIdSnapshot`. Do not overwrite the live `Subscription.providerSubscriptionId` with a fabricated Shopify id; that field continues to mirror the nullable provider value.

A purchase is "current provider context" only when all required facts agree:

```text
providerContextIdentity
shopifyPlanHandleSnapshot
billingPeriodId
```

and, for a specific refund/purchase action, the expected `shopifyEventHandleSnapshot` is present in the live subscription.

## Fractional correction schema amendment

The v1.1 design assumed no mandatory Prisma change. Current code inspection shows one exception if automated partial App Event corrections are retained:

```text
RecoveryCreditPurchase.providerUsageQuantityBeforeSnapshot Int
RecoveryCreditPurchase.providerUsageQuantityAfterSnapshot  Int?
```

A safe partial correction can make Shopify's subsequent meter quantity fractional (for example 4 -> 3.75). A later purchase must be able to snapshot that exact baseline.

Therefore ARCH-015 changes only these two provider evidence quantities to `Decimal`/`Decimal?`.

`UsageEvent.quantity` is already Decimal and needs no schema change. Moda entitlement counters remain Int because recovery credits are whole units.

No new ledger, lock, refund or catalogue model is authorized by ARCH-015.

## Purchase single-flight invariant

For genuine new purchases:

```text
at most one unresolved REQUESTED RecoveryCreditPurchase
per (shopId, shopifyEventHandleSnapshot)
```

The invariant is intentionally independent of current billing period and provider subscription identity.

Purchase admission uses the existing Subscription row lock for request-time serialization. The durable REQUESTED purchase maintains single-flight across the asynchronous reconciliation window.

Same shop + different event handles may proceed independently.

## Purchase lifecycle

```text
merchant selects resolved offer
  -> app verifies fresh Shopify + ARCH-014 correlation
  -> app snapshots provider before quantity/cost
  -> app creates REQUESTED purchase + PENDING UsageEvent(+1)
  -> existing background publisher submits App Event
  -> Shopify 202 => UsageEvent submission accepted, purchase still REQUESTED
  -> background provider reconciliation proves expected meter/cost delta
  -> purchase ACTIVE + currentAmount=creditsGranted
```

No merchant credits are granted merely because the App Event endpoint returned 202.

## Consumption rule

All ACTIVE purchased lots owned by the shop remain spendable regardless of current plan/billing period.

Selection order:

```text
1. historical/non-current-provider-context ACTIVE lots, oldest first
2. current-provider-context ACTIVE lots, oldest first
```

This preserves potentially refundable current-context value.

Spending purchased credits creates local consumption evidence only and MUST NOT emit Bronze/Silver/Gold top-up App Events.

## Refund eligibility

Normal merchant refund path requires:

```text
purchase ACTIVE
purchase provider monetary amount > 0
unused/unreserved credits exist
fresh Shopify current provider context matches purchase context
purchase planHandle matches live plan
purchase billingPeriodId matches current local billing period
purchase event handle is present in live subscription
```

Historical purchases remain ACTIVE/spendable and return a non-refund outcome; they are not placed on refund hold.

## Refund invocation and completion

`SHOPIFY-003` creates the durable refund request/hold only.

There is NO direct web->Background invocation.

The existing billing worker scheduler invokes `BACKGROUND-003` during its normal cycle.

```text
RecoveryCreditRefund.status = REQUESTED
      ->
existing billing scheduler
      ->
processDueRefundCorrections()
```

Automatic path:

```text
REQUESTED
  -> create/reuse deterministic correction UsageEvent
  -> existing publisher submits negative/fractional App Event
  -> 202 is receipt only
  -> later scheduler reads Shopify provider state
  -> exact expected quantity/cost movement proven
  -> COMPLETED
```

Unsafe automatic path:

```text
REQUESTED
  -> provider correction cannot be proved safe
  -> PROVIDER_ACTION_REQUIRED
  -> Admin performs external REFUND/CREDIT
  -> Admin records exact provider evidence
  -> system verifies evidence
  -> COMPLETED
```

Ambiguous/mismatching evidence -> `NEEDS_ATTENTION`, never speculative completion.

## Task graph

```text
ARCH-014-DATABASE-001
      |
      +--> ARCH-015-DATABASE-001

ARCH-015-SHARED-001  (independent/parallel)

ARCH-014-SHOPIFY-001
      |
      +--> ARCH-015-SHOPIFY-001
                 |
ARCH-015-SHARED-001 + ARCH-015-DATABASE-001
                 |
                 +--> ARCH-015-SHOPIFY-002
                              |
                              +--> ARCH-015-BACKGROUND-001
                                      |
                                      +--> ARCH-015-BACKGROUND-002
                                      |
                                      +--> ARCH-015-SHOPIFY-003
                                                |
                                                +--> ARCH-015-BACKGROUND-003
                                                          |
                                                          +--> ARCH-015-ADMIN-001

All accepted implementation tasks
      -> ARCH-015-SYSTEM-TEST-001
```

## Explicit non-goals

ARCH-015 MUST NOT:

- create a second merchant pricing catalogue;
- make ARCH-014 pricing rows authoritative for live Shopify charges;
- use singular `BillingPlan.recoveryCreditsPerPack` or `BillingPlan.shopifyRecoveryCreditPackEventHandle` as the new top-up source;
- mutate historical purchased lots on plan change;
- emit a top-up App Event when purchased credits are consumed;
- complete a purchase/refund from HTTP 202 alone;
- auto-refund a historical provider-context purchase;
- hide the top-up section merely because no offers are currently available;
- add another background queue solely to invoke refund processing;
- allow implementation agents to invent additional Prisma models/enum states without architect review.

## Post-review update — DATABASE-001 Accepted

`ARCH-015-DATABASE-001` Attempt 1 is architect-accepted. The only ARCH-015 schema
amendment is now implemented as designed:

```text
RecoveryCreditPurchase.providerUsageQuantityBeforeSnapshot -> Decimal
RecoveryCreditPurchase.providerUsageQuantityAfterSnapshot  -> Decimal?
```

The migration preserves existing integer evidence exactly, permits fractional provider
usage baselines required by later negative/fractional App Event corrections, and does
not widen Moda credit-entitlement/refund quantities away from integers. Historical
migration SQL remains immutable and the current-schema validator/ERD are aligned.

The stale local `moda_interact` fixture recorded during validation is an environment
baseline mismatch; a fresh database built from the checked-in ARCH-010/014-compatible
migration chain applies ARCH-015 successfully. It does not block this acceptance.

`ARCH-015-DATABASE-001` is therefore **Complete**. Enabled dependants remain subject
to their other declared prerequisites; this acceptance does not bypass the task graph.
## Post-review update — SHARED-001 Attempt 1 Changes Requested

Architect review of `ARCH-015-SHARED-001` accepted the provider-context identity
format and legacy/native derivation rules, but found one fail-open defect in the
generic comparison helper.

The current implementation can treat two blank required values as matching because
it trims and compares them without requiring non-empty evidence. ARCH-015 requires a
purchase to be classified as current provider context only when provider identity,
plan handle and billing period are all positively present and equal.

Therefore ARCH-015 remains **In Progress** and the same SHARED-001 task must be
corrected so:

```text
valid non-empty identity + plan + billingPeriod, all equal
  -> current provider context = true

any missing/blank identity, plan or billingPeriod
  -> current provider context = false
```

Event-handle membership remains an operation-specific caller check and is not added to
the generic Shared comparator.

Attempt 1 published `@modainteract/moda-interact-shared@0.11.1`; that immutable release
must not be overwritten. The corrected task must publish and exact-version smoke-test
`0.11.2` before architect acceptance.

No downstream dependency is unblocked until `ARCH-015-SHARED-001` is Complete.


## Post-review update — SHARED-001 Attempt 2 External Publication Blocker

`ARCH-015-SHARED-001` Attempt 2 closes the only production defect identified in
Attempt 1. The canonical Shared comparator now fails closed when provider identity,
plan handle or billing period evidence is blank, and the corrected package is versioned
as `0.11.2`. No further Shared source correction is requested.

npm accepted publication of `@modainteract/moda-interact-shared@0.11.2`, but the
registry had not yet made that exact version resolvable for the mandatory clean
consumer smoke. The task is therefore **Blocked on external npm registry visibility**
rather than returned for another implementation attempt.

Required sequencing remains:

```text
ARCH-015-SHARED-001 Attempt 2
  functionally accepted
  + exact 0.11.2 registry artifact/consumer smoke pending
  -> Blocked

registry smoke passes
  -> same Attempt 2 returns to Architect Review
  -> architect acceptance
  -> dependent ARCH-015 tasks may be promoted
```

Do not create Attempt 3, republish `0.11.2`, or bump another Shared version solely to
work around propagation. No downstream dependency is unblocked until SHARED-001 is
Complete.

## Post-review update — SHOPIFY-001 Attempt 1 Changes Requested

Architect review accepts the core live Shopify × ARCH-014 top-up offer resolver from `374f16f`, including plan-scoped usage-event intersection, live provider price/usage authority, inactive returned provider-price eligibility, bounded unknown-meter diagnostics, and separate verified-empty versus verification-unavailable merchant states.

Two Attempt-2 conditions remain before `ARCH-015-SHOPIFY-001` can become Complete:

```text
1. resolved multi-offer cards are display-only until SHOPIFY-002 supplies
   intent + purchaseId + selected eventHandle and revalidates server-side;
2. the ARCH-015 provider reader/resolver is merged onto the latest accepted
   ARCH-014 merchant-pricing reader without regressing highlights, exact-locale
   presentation integrity, usage-event semantics, or catalogue behavior.
```

ARCH-014 highlight rows are merchant presentation only and do not participate in top-up economic/provider resolution. `MerchantPricingUsageEvent` remains the ARCH-014 entitlement source; Shopify remains live monetary/provider authority.

Do not reintroduce `BillingPlan.recoveryCreditsPerPack` or `BillingPlan.shopifyRecoveryCreditPackEventHandle` as operative offer authority. Do not implement SHOPIFY-002 purchase admission early.

The same `ARCH-015-SHOPIFY-001` task returns to Ready for Attempt 2. `ARCH-015-SHOPIFY-002` remains Pending until SHOPIFY-001 is architect-accepted.

## Post-review update — SHOPIFY-001 Attempt 2 Accepted

`ARCH-015-SHOPIFY-001` Attempt 2 is architect-accepted.

The live Shopify × ARCH-014 offer resolver remains the canonical read model, and the
interim multi-offer UI is now safely display-only until `ARCH-015-SHOPIFY-002`
implements selected-offer purchase admission.

The accepted state is:

```text
Shopify active subscription planHandle
  -> exact MerchantPricingPlan.shopifyPlanHandle

MerchantPricingUsageEvent.eventHandle
  intersect
Shopify activeSubscription.usageItems[].handle

matched offer
  -> creditsGranted from ARCH-014 creditsGrantedPerUnit
  -> price/currency/usage from live Shopify
  -> display-only in SHOPIFY-001
```

The extended ARCH-014 catalogue reader introduced by accepted
`ARCH-014-SHOPIFY-002` remains intact. Pricing-card highlights and their exact-locale
translations are presentation data only and are not top-up economic/provider
authority.

No enabled Buy action, callback, fetcher submission, or selected-event purchase path
is exposed by SHOPIFY-001. The pre-existing legacy mutation surface is intentionally
left for `ARCH-015-SHOPIFY-002` to replace with strict:

```text
intent
purchaseId
eventHandle
```

admission and fresh provider/ARCH-014 revalidation.

The ARCH-015 frontier is now:

```text
ARCH-015-SHARED-001   Complete
ARCH-015-DATABASE-001 Complete
ARCH-015-SHOPIFY-001  Complete
        |
        +--> ARCH-015-SHOPIFY-002 Ready
```

Downstream Background/refund tasks remain Pending until their declared prerequisites
are complete.

## Post-review update — SHOPIFY-002 Attempt 2 Changes Requested

Architect review accepts the substantive purchase-admission rework in `fdb72fc`: selected `eventHandle` admission, exact ARCH-014 credits mapping, live Shopify meter proof, second pre-write provider snapshot, fail-closed provider-evidence comparison, Shared native-App-Pricing fallback identity, fractional provider-before evidence, exact same-handle unresolved scope, different-handle independence, and atomic PENDING UsageEvent + REQUESTED purchase creation.

One concurrency-contract requirement remains unresolved. The current purchase write opens Prisma `$transaction(async (...) => ...)` without explicitly selecting Serializable isolation. ARCH-015 requires both:

```text
PostgreSQL SERIALIZABLE transaction
+
Subscription row SELECT ... FOR UPDATE
```

The row lock is present and must remain. Attempt 3 must add Prisma Serializable isolation to this purchase transaction only and regression-test the transaction option while retaining the row-lock behavior. No schema/index/lock-table change is authorized.

Therefore `ARCH-015-SHOPIFY-002` remains **Ready** on the same task after Attempt-2 review. `ARCH-015-BACKGROUND-001` and `ARCH-015-SHOPIFY-003` remain Pending until SHOPIFY-002 is architect-accepted Complete.


## Post-review update — SHOPIFY-002 Attempt 3 Accepted

`ARCH-015-SHOPIFY-002` Attempt 3 is architect-accepted and **Complete**.

The final purchase-admission path now satisfies the full ARCH-015 request-time concurrency contract:

```text
fresh selected Shopify/ARCH-014 evidence
  -> second provider snapshot immediately before write
  -> Prisma SERIALIZABLE transaction
  -> Subscription row SELECT ... FOR UPDATE
  -> replay + exact same-handle single-flight checks
  -> re-read/revalidate local subscription/period/plan state
  -> create PENDING UsageEvent
  -> create REQUESTED RecoveryCreditPurchase
```

The accepted implementation preserves immutable provider-before quantity/cost/currency/price from the revalidated provider snapshot, including fractional quantities and native App Pricing contexts with no legacy subscription id. Different event handles remain independently purchasable; the unresolved invariant remains per `(shopId, shopifyEventHandleSnapshot)` rather than per billing period/provider identity.

No direct Shopify App Events HTTP submission is added to the web path, and no retired singular BillingPlan top-up field is purchase authority.

Attempt 3 adds Serializable isolation only to this purchase transaction and retains the existing `Subscription ... FOR UPDATE` lock. Regression coverage proves the runtime transaction option and ordering.

The ARCH-015 frontier is now:

```text
ARCH-015-SHARED-001      Complete
ARCH-015-DATABASE-001    Complete
ARCH-015-SHOPIFY-002     Complete
           |
           +--> ARCH-015-BACKGROUND-001 Ready
                    |
                    +--> later BACKGROUND-002 / SHOPIFY-003 / BACKGROUND-003
```

`ARCH-015-SHOPIFY-003` remains Pending because `ARCH-015-BACKGROUND-001` is still an unsatisfied declared prerequisite.


## Post-review update — BACKGROUND-001 Attempt 2 Changes Requested

Architect review accepts the candidate-centric purchase reconciliation core and the
Attempt-2 fixes for inactive tiered meters, Decimal provider quantities and sequential
same-handle baselines.

Two integration defects remain before `ARCH-015-BACKGROUND-001` can become Complete:

```text
1. Background still compares the raw nullable Shopify legacySubscriptionId against
   RecoveryCreditPurchase.providerSubscriptionIdSnapshot. Native App Pricing purchases
   store the canonical Shared app-pricing:v1 provider-context identity, so a null legacy
   id can never match. Attempt 3 must consume Shared 0.11.2, derive the current context
   identity, and use the canonical three-field context comparator.

2. The Background Shopify Partner parser still filters current/pending FlatRatePrice
   items on price.active. ARCH-015 requires returned subscription membership, not the
   price.active flag, to decide plan/meter membership. Tiered handling is already fixed;
   current and pending flat-rate handling must be aligned.
```

No schema, status, queue or reconciliation redesign is requested. Existing Decimal
candidate proof, zero-cost activation, same-handle ambiguity, different-handle
independence, Serializable activation, atomic entitlement increment and post-commit
resume behavior remain accepted and must not be churned.

The same `ARCH-015-BACKGROUND-001` task returns to **Ready** at Attempt 2. The next valid
claim is Attempt 3. Its downstream tasks remain Pending until BACKGROUND-001 is accepted
Complete.

## Post-review update — BACKGROUND-001 Attempt 3 Changes Requested

Architect review accepts the Attempt-3 corrections for canonical Shared provider-context
identity and complete inactive-price parser alignment.

The production reconciliation now correctly consumes exact Shared `0.11.2`, supports
native App Pricing contexts with no legacy subscription id, compares identity + plan +
billing period through the canonical Shared comparator, keeps event-handle proof
operation-specific, and retains current/pending flat-rate plus tiered subscription items
without filtering solely on `price.active`.

One original BACKGROUND-001 invariant remains unresolved: the Background orchestration
still requires `projection.packMeterHandle`, which is sourced from the retired singular
`BillingPlan.shopifyRecoveryCreditPackEventHandle`, before it will invoke durable purchase
reconciliation.

ARCH-015 requires durable REQUESTED+REPORTED purchases to be discovered and proved from
their own immutable `shopifyEventHandleSnapshot` against the complete live Shopify
`providerUsageSnapshot`. A missing/disabled singular BillingPlan pack configuration must
not prevent that reconciliation.

Therefore the same `ARCH-015-BACKGROUND-001` task returns to **Ready** for Attempt 4.
Attempt 4 is limited to removing the singular pack-meter prerequisite/scope from the
normal Background purchase-reconciliation path while preserving all accepted provider-
identity, Decimal, transaction, idempotency and parser behavior.

Downstream tasks remain Pending until BACKGROUND-001 is architect-accepted Complete.

## Post-review update — BACKGROUND-001 Attempt 4 Accepted

`ARCH-015-BACKGROUND-001` Attempt 4 is architect-accepted and **Complete**.

The final purchase-reconciliation flow is candidate-centric end to end:

```text
valid current local/provider billing context
  -> derive canonical providerContextIdentity
  -> pass complete live providerUsageSnapshot
  -> discover durable REQUESTED + REPORTED purchases
  -> group by each stored shopifyEventHandleSnapshot
  -> prove each candidate against its own exact live meter
  -> Decimal before + 1 quantity proof + cost/currency/context/cycle proof
  -> Serializable ACTIVE transition + atomic purchased-credit grant
```

The retired singular `BillingPlan.shopifyRecoveryCreditPackEventHandle` and
`recoveryCreditPackEnabled` no longer gate or select the normal Background purchase
reconciliation path. Remaining references inside existing subscription plan-change /
rollover compatibility logic are not purchase-reconciliation authority and were outside
Attempt 4's bounded correction.

The previously accepted Shared 0.11.2 provider-context identity, native App Pricing
fallback identity, inactive-price provider membership, Decimal evidence, same-handle
ambiguity, different-handle independence, idempotency and post-commit resume behavior
remain intact.

The execution frontier is now:

```text
ARCH-015-BACKGROUND-001  Complete
        |
        +--> ARCH-015-BACKGROUND-002  Ready
        |
        +--> ARCH-015-SHOPIFY-003     Ready
                    |
                    +--> ARCH-015-BACKGROUND-003 Pending
```

BACKGROUND-003 remains Pending because SHOPIFY-003 is not yet Complete.


## Post-review update — SHOPIFY-003 Attempt 2 Accepted

`ARCH-015-SHOPIFY-003` Attempt 2 is architect-accepted and **Complete**.

The merchant refund-admission boundary now enforces the full current-provider-context
contract before any new monetary refund hold is created:

```text
authenticated exact shop + nonblank shopifyShopId
  -> ACTIVE purchase
  -> providerPurchaseAmount > 0
  -> availableAmount >= 1
  -> fresh Shopify ACTIVE/TRIALING subscription
  -> canonical providerContextIdentity
  -> exact plan + local billingPeriod + provider/local cycle match
  -> purchase eventHandle present live
  -> Serializable durable REQUESTED refund hold
  -> ACTIVE purchase becomes WITHDRAWN
  -> refundingQuantity += availableAmount only
```

Historical/non-current purchases remain ACTIVE and spendable and do not enter the normal
monetary refund path. Zero/non-positive-value purchases likewise remain spendable and
return `REFUND_NOT_AVAILABLE`. No direct web-to-Background invocation or provider
completion evidence is introduced; `ARCH-015-BACKGROUND-003` remains responsible for
asynchronous correction and provider reconciliation.

The frontier is now:

```text
ARCH-015-SHOPIFY-003     Complete
ARCH-015-BACKGROUND-001  Complete
ARCH-015-SHARED-001      Complete
ARCH-015-DATABASE-001    Complete
        |
        +--> ARCH-015-BACKGROUND-003 Ready
```

`ARCH-015-BACKGROUND-002` continues independently through its own review lifecycle.
