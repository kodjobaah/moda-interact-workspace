---
id: ARCH-027-BACKGROUND-007
architecture_id: ARCH-027
title: Reconcile Shopify one-time-charge operations from Historical Events
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 107
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-SHOPIFY-002
enables: []
created: 2026-10-12
updated: 2026-10-12
---

# Reconcile Shopify one-time-charge operations from Historical Events

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Converge the Shopify `ONE_TIME_CHARGE` `BillingOperation` ledger onto Shopify's real provider charge identity **without replacing or weakening the existing Shopify purchase-acquisition reconciliation**.

After `ARCH-027-SHOPIFY-002`, a Shopify recovery-credit top-up may honestly begin as:

```text
BillingOperation
    kind = ONE_TIME_CHARGE
    state = INITIATING
    providerReference = NULL
    recoveryCreditPurchaseId = <exact purchase>
```

because the App Events submission returns acceptance but not a Shopify charge ID.

The current Background purchase path already establishes provider-confirmed entitlement by proving the exact Shopify meter context, quantity transition and cost transition. This task keeps that mechanism authoritative for `RecoveryCreditPurchase` activation and separately reconciles the linked operation when Shopify Historical Events later exposes the corresponding `CHARGE_USAGE` `Charge.chargeId`.

Target convergence:

```text
App Events billing event accepted
    -> UsageEvent = REPORTED
    -> existing Partner active-subscription usage reconciliation
    -> RecoveryCreditPurchase = ACTIVE
       providerPurchaseAmount/currency confirmed
       providerValuationConfirmedAt set
    -> bounded Shopify Historical Events CHARGE_USAGE lookup
    -> exactly one provider charge can be proven
    -> BillingOperation.providerReference = Charge.chargeId
    -> BillingOperation.state = CONFIRMED
```

If Historical Events is delayed, unavailable, incomplete or ambiguous, the already-proven purchase/entitlement remains valid and the operation stays unresolved for a later reconciliation cycle. The worker MUST NOT invent provider identity.

## Context

### Existing Shopify purchase-acquisition reconciliation

The current Background path is already deliberately conservative.

`RecoveryCreditPurchaseService.create()` creates:

```text
RecoveryCreditPurchase(status = REQUESTED)
    + exact provider/billing-period/plan/meter baseline snapshots
    + linked UsageEvent(
        metric = RECOVERY_CREDIT_PACK_PURCHASE,
        quantity = 1,
        shopifyReportState = PENDING,
        shopifyEventHandle = purchase meter,
        shopifyIdempotencyKey = Moda-generated App Events request identity
      )
```

`ShopifyUsageEventPublisherService` submits the UsageEvent to Shopify App Events. A successful submission marks the UsageEvent `REPORTED`; it does not produce a Shopify charge ID.

During the existing leased billing reconciliation cycle, `ProviderUsageReconciliationService` passes the current Partner active-subscription meter snapshot to `RecoveryCreditPurchaseService.reconcileProviderConfirmed()`.

That service activates a REQUESTED purchase only when the current code can prove the purchase from provider evidence, including:

```text
exact Shop
exact billing period
exact Shopify plan handle
exact purchase meter handle
same provider subscription/context identity
same currency
provider quantity = purchase baseline quantity + 1
provider cumulative cost >= purchase baseline cost
exact current provider period where supplied
no ambiguous unresolved purchase for the same purchase meter
```

On successful proof it records the post-usage quantity/cost snapshots, derives and stores the provider-confirmed purchase amount/currency, sets `providerValuationConfirmedAt`, activates the lot, increments `PURCHASED_RECOVERY_CREDITS`, and schedules capacity resume.

**This task MUST preserve that path.** Historical charge lookup is operation-ledger convergence, not a new entitlement prerequisite.

### Gap introduced by the common BillingOperation ledger

`ARCH-027-SHOPIFY-002` adds a linked provider-neutral `BillingOperation` for Shopify top-ups. The App Events `idempotency_key` is app-generated request identity, not external charge identity, so it must not be stored as `BillingOperation.providerReference`.

The Shopify App Events create endpoint accepts:

```text
shop_id
event_handle
timestamp
idempotency_key
attributes.value
```

and successful submission does not synchronously return `Charge.chargeId`.

Shopify Partner Historical Events later exposes `CHARGE_USAGE` as `Charge` evidence containing, among other fields:

```text
id                  historical event identity
chargeId            stable provider charge identity
occurredAt
eventType
shop.id
subject App id
amount.amount
amount.currencyCode
usageQuantity
planHandle
```

Provider documentation verified 2026-10-12:

- `https://shopify.dev/docs/api/app-events/latest/creating-events`
- `https://shopify.dev/docs/api/partner/latest/historical-events`

The required provider reference is `Charge.chargeId`, **not** the Historical Event `id`, not `metadata.legacyChargeId`, not the App Events idempotency key and not Moda's `BillingOperation.requestKey`.

## Scope

Modify only `moda-interact-background` implementation/tests required to:

1. add a bounded Shopify Partner Historical Events `CHARGE_USAGE` read capability;
2. identify Shopify `ONE_TIME_CHARGE` operations that are eligible for provider-reference reconciliation;
3. correlate only exact, unique Historical `Charge` evidence to the already-linked, provider-confirmed `RecoveryCreditPurchase`;
4. atomically write the exact `Charge.chargeId` and move the operation to `CONFIRMED`;
5. run this convergence from the existing leased billing reconciliation cycle after the existing purchase-usage reconciliation;
6. add structured diagnostics and focused provider/service/PostgreSQL coverage.

Expected implementation areas include:

```text
src/providers/shopify-partner-billing.provider.ts
src/services/billing-reconciliation.service.ts
src/services/billing-reconciliation/
  <bounded Shopify one-time-charge operation reconciler>

tests/unit/providers/
tests/unit/services/
tests/integration/ or existing disposable-PostgreSQL billing harness
```

Exact filenames may differ where the current Background decomposition has a clearer owner.

## Out of Scope

- Replacing `RecoveryCreditPurchaseService.reconcileProviderConfirmed()`.
- Requiring Historical Events before purchased credits become ACTIVE/usable.
- Changing App Events submission semantics.
- Changing `UsageEvent.shopifyIdempotencyKey` or treating it as provider identity.
- Changing `BillingOperation.requestKey` / `requestFingerprint` semantics.
- Creating a new queue, worker, lease or cron.
- Shopify subscription create/switch/cancel operation reconciliation.
- Shopify refund/correction reconciliation.
- WooCommerce operation or receipt reconciliation.
- Prisma schema/migration changes.
- Shared-package contract changes unless a concrete cross-repository contract gap is discovered and returned to `moda_architect`.
- Admin, Shopify UI, API, Gateway or WooCommerce application changes.
- Updating any `docs/decisions/**/_index.md`.

## Requirements

### R1 — Preserve the existing Shopify entitlement proof

The existing purchase acquisition path remains authoritative:

```text
App Events accepted
    -> UsageEvent REPORTED
    -> Partner active-subscription usage snapshot
    -> exact quantity/cost/context proof
    -> RecoveryCreditPurchase ACTIVE
    -> PURCHASED_RECOVERY_CREDITS grant
```

Historical Events MUST NOT become a prerequisite for that activation.

A missing/delayed/ambiguous Historical `CHARGE_USAGE` event MUST NOT:

- revert or block an otherwise proven `RecoveryCreditPurchase` activation;
- decrement/regrant `PURCHASED_RECOVERY_CREDITS`;
- cause duplicate capacity-resume scheduling;
- mutate the purchase's already-confirmed provider valuation evidence.

### R2 — Reconcile only the exact unresolved Shopify operation shape

The operation convergence path must be restricted to Shops whose:

```text
Shop.platform = SHOPIFY
```

and operations whose durable shape is equivalent to:

```text
kind = ONE_TIME_CHARGE
state = INITIATING
providerReference IS NULL
recoveryCreditPurchaseId IS NOT NULL
```

The linked purchase must be the exact purchase referenced by the operation and must already have sufficient provider-confirmed acquisition evidence, including:

```text
status = ACTIVE
providerValuationConfirmedAt IS NOT NULL
providerPurchaseAmount IS NOT NULL
providerPurchaseCurrency IS NOT NULL
usageEventId IS NOT NULL
```

The linked UsageEvent must remain the exact Shopify purchase-acquisition event and be `REPORTED`.

Do not correlate an arbitrary purchase by Shop, amount, plan or time when the operation already has an exact purchase link.

### R3 — Add a bounded Historical `CHARGE_USAGE` provider query

Extend the existing Shopify Partner provider rather than introducing a second generic HTTP client.

The provider request must use the configured Partner app identity and the exact Shopify Shop identity, with Historical Events filters equivalent to:

```text
subjectId = configured Shopify App ID
shopId = exact Shopify Shop ID
eventTypes = [CHARGE_USAGE]
occurredAtMin = bounded candidate-window start
occurredAtMax = bounded candidate-window end
```

Use the current Partner API version already owned by the provider unless the repository has deliberately advanced it.

#### Required Partner GraphQL request

Implement this as an extension of the existing Partner GraphQL client. For the current repository configuration the HTTP request shape is:

```text
POST https://partners.shopify.com/<orgId>/api/2026-07/graphql.json
Content-Type: application/json
X-Shopify-Access-Token: <existing Partner access token>
```

No new Shopify credential or HTTP client is authorised by this task. Reuse the provider's existing `orgId`, `appId`, access token, HTTP error mapping and GraphQL-error handling.

The GraphQL operation must be equivalent to:

```graphql
query ShopifyUsageChargeHistory($filter: EventFilterInput!, $cursor: String) {
  events(
    filter: $filter
    orderBy: OCCURRED_AT_ASC
    first: 100
    after: $cursor
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      cursor
      node {
        __typename
        id
        occurredAt
        eventType
        shop { id }
        subject {
          __typename
          ... on AppReference { id }
        }
        ... on Charge {
          chargeId
          chargeType
          amount { amount currencyCode }
          usageQuantity
          planHandle
          metadata { legacyChargeId }
        }
      }
    }
  }
}
```

For one unresolved purchase operation, the variables must be derived from durable local evidence and be equivalent to:

```json
{
  "filter": {
    "subjectType": "APP",
    "subjectId": "<configured Shopify App GID>",
    "shopId": "<exact commerce.Shop.shopifyShopId>",
    "eventTypes": ["CHARGE_USAGE"],
    "occurredAtMin": "<UsageEvent.occurredAt ISO-8601>",
    "occurredAtMax": "<RecoveryCreditPurchase.providerValuationConfirmedAt ISO-8601>"
  },
  "cursor": null
}
```

Shopify's Historical Events filter is inclusive at both time boundaries. Supplying `shopId` requires `subjectId`; always send both rather than relying on broad Partner-account history. `subjectType: APP` is included explicitly even though the Partner API currently defaults Historical Events to App subjects.

Pagination contract:

```text
page 1: cursor = NULL
next page: cursor = previous pageInfo.endCursor
stop: pageInfo.hasNextPage = false
```

Use `first: 100` and cap one reconciliation lookup at **5 pages / 500 returned edges**. Shopify permits page sizes up to 250, but this task intentionally uses the smaller fixed page size so provider responses and parsing remain bounded. If page 5 still reports `hasNextPage = true`, return an incomplete/ambiguous provider result and leave the operation unresolved. Do not treat the first 500 events as exhaustive. `hasNextPage = true` with a missing `endCursor` is invalid provider evidence and must also leave the operation unresolved.

Before issuing the query, validate that both local timestamps exist and:

```text
UsageEvent.occurredAt <= RecoveryCreditPurchase.providerValuationConfirmedAt
```

If the local window is inverted, do not widen or reorder it; report invalid durable evidence and leave the operation unresolved.

The provider parser must discard/reject any returned node that is not structurally a usage charge. A candidate supplied to the reconciler must have all of the following:

```text
__typename = Charge
eventType = CHARGE_USAGE
chargeType = USAGE
chargeId = non-empty Shopify charge GID
shop.id = requested Shopify Shop GID
subject.__typename = AppReference
subject.id = configured Shopify App GID
occurredAt = valid timestamp inside the requested inclusive window
amount.amount = valid decimal string
amount.currencyCode = non-empty currency code
usageQuantity = valid decimal value
planHandle = non-empty string
```

`node.id` is retained only as Historical Event diagnostic identity. `metadata.legacyChargeId` may be retained as bounded diagnostic/backfill evidence, but neither value may be promoted to `BillingOperation.providerReference`.

The result parser must validate provider evidence and expose only bounded fields required by reconciliation, including:

```text
historical event id
chargeId
occurredAt
eventType
shop id
subject app id
amount + currency
usageQuantity
planHandle
```

Pagination must be bounded. Never silently treat an incomplete page as an exhaustive candidate set. If the configured bound is reached while `hasNextPage` remains true, leave the operation unresolved and report bounded diagnostic evidence rather than guessing.

### R4 — Correlate from the already-confirmed purchase, never from a fabricated identifier

A Historical Charge candidate may be considered only when all available authoritative evidence agrees with the linked purchase/UsageEvent.

At minimum, require exact agreement for:

```text
Shop
App subject
CHARGE_USAGE event type
plan handle
currency
provider-confirmed purchase amount
usage quantity versus the linked purchase UsageEvent quantity
bounded occurrence window
```

The occurrence window must be derived from durable local evidence. For the existing purchase flow, the normal bound is:

```text
UsageEvent.occurredAt
    <= Charge.occurredAt
    <= RecoveryCreditPurchase.providerValuationConfirmedAt
```

because the App Event must exist before the provider usage delta can be observed and confirmed locally.

If actual provider semantics discovered during implementation make that bound invalid, STOP and return the concrete provider evidence to `moda_architect`; do not silently widen it until multiple charges can be guessed apart.

The Historical `Charge` contract does not expose the local purchase meter handle or Moda idempotency key. Therefore:

- do not infer a meter match that Shopify did not provide;
- do not match on amount alone;
- do not match on timestamp alone;
- do not map the first/nearest event merely because it is convenient;
- do not use `UsageEvent.shopifyIdempotencyKey`, `BillingOperation.requestKey`, Historical Event `id` or `metadata.legacyChargeId` as the `providerReference`.

Exactly one candidate must survive the proof. Zero candidates means "not available yet" unless other evidence proves a permanent contradiction. More than one candidate is ambiguous and must remain unresolved.

### R5 — `Charge.chargeId` is the only provider reference written by this task

On exact unique proof, write:

```text
BillingOperation.providerReference = Historical Charge.chargeId
BillingOperation.state = CONFIRMED
BillingOperation.lastErrorCode = NULL
```

The write must be transactional and race-safe. Re-read/lock the exact operation/purchase evidence before mutation using the repository's accepted PostgreSQL transaction pattern.

Provider-reference semantics are write-once:

```text
NULL -> exact chargeId       allowed
same chargeId -> replay/no-op
other non-null chargeId -> never overwrite; fail closed/report conflict
```

Do not copy the charge reference to `Subscription.providerSubscriptionId`.

### R6 — Existing purchase activation and operation confirmation are independently retryable

The normal same-cycle ordering is:

```text
existing subscription reconciliation
    -> existing provider-usage / purchase reconciliation
    -> Shopify ONE_TIME_CHARGE provider-reference reconciliation
```

This permits a purchase activated earlier in the same cycle to converge immediately if Historical Events already contains the exact charge.

It must also support later convergence:

```text
cycle N:
    purchase becomes ACTIVE
    Historical charge not visible yet
    operation remains INITIATING

cycle N+1:
    Historical charge becomes visible
    exact proof succeeds
    operation becomes CONFIRMED
```

A process restart between those cycles must not lose the work because the unresolved operation/purchase evidence is durable in PostgreSQL.

### R7 — Do not misclassify charge-history convergence as subscription synchronization

Historical one-time-charge correlation is operation-ledger reconciliation, not subscription lifecycle truth.

A Partner Historical Events timeout/error, malformed charge response, zero candidate or ambiguity MUST NOT be persisted as a false Shopify subscription `SYNC_ERROR` / `PARTNER_API_ERROR` merely because this work executes inside the leased billing cycle.

Keep this failure boundary separate from existing subscription reconciliation. Preserve existing subscription and purchase results, leave the operation unresolved, and retry on a later cycle where appropriate.

### R8 — Use the shared structured logger

Use:

```text
@modainteract/moda-interact-shared/logging
```

through the existing Background logger. Do not create a local generic logger and do not use ad-hoc `console.*` for the new reconciliation path.

Emit bounded semantic events sufficient to distinguish at least:

```text
confirmed
not-yet-observed
ambiguous
provider-query-failed
provider-evidence-invalid
provider-reference-conflict
```

Include bounded identifiers such as `shopId`, `billingOperationId`, `recoveryCreditPurchaseId`, candidate count and provider error code where appropriate. Do not log provider credentials or full provider payloads.

### R9 — No new infrastructure

Reuse the existing `BILLING_RECONCILIATION` leased cycle and existing Shopify Partner credentials/provider boundary.

Do not add:

```text
new BullMQ queue
new worker process
new cron
new Redis keyspace
new Render service
new environment secret
```

unless implementation proves the existing Partner credential lacks required Historical Events permission; if so, STOP and return that concrete infrastructure/permission gap to `moda_architect` rather than silently adding configuration outside Background ownership.

## Work Items

- [ ] Adopt the integrated `ARCH-027-SHOPIFY-002` database/application contract and regenerate Background Prisma from the current accepted database submodule.
- [ ] Add the concrete `ShopifyUsageChargeHistory` `events(filter:, after:)` GraphQL query, variables, bounded cursor pagination and typed `Charge` parser described in R3 to the existing Partner provider.
- [ ] Add a focused Shopify one-time-charge operation reconciler over linked ACTIVE purchases.
- [ ] Reuse the existing provider-confirmed purchase amount/currency and linked UsageEvent evidence for exact charge proof.
- [ ] Confirm only one uniquely proven operation with `providerReference = Charge.chargeId`.
- [ ] Preserve unresolved operations on zero/ambiguous/delayed provider evidence.
- [ ] Integrate the reconciler after existing provider-usage purchase reconciliation in the leased billing cycle.
- [ ] Keep charge-history failures isolated from Subscription sync-error state.
- [ ] Add shared-logger semantic events for confirmation/unresolved/error outcomes.
- [ ] Add provider parser/query unit coverage.
- [ ] Add reconciliation unit coverage for exact, missing, ambiguous, conflicting and replay cases.
- [ ] Add disposable PostgreSQL proof of the real BillingOperation constraint/state transition and no duplicate purchase grant.
- [ ] Re-run the existing Shopify purchase/refund/billing regression suites required by the task.

## Interfaces / Contracts

### Existing database contract

Owner:

`ARCH-027-DATABASE-001`

Consumed models:

```text
billing.BillingOperation
billing.RecoveryCreditPurchase
billing.UsageEvent
billing.ShopEntitlementCounter
commerce.Shop
billing.Subscription
billing.BillingPeriod
```

No schema change is authorised by this task.

### Shopify operation producer

Owner:

`ARCH-027-SHOPIFY-002`

Required input shape for a newly submitted Shopify top-up:

```text
BillingOperation
    shopId = authenticated Shopify Shop
    kind = ONE_TIME_CHARGE
    state = INITIATING
    providerReference = NULL
    recoveryCreditPurchaseId = exact purchase
```

### Shopify provider evidence

Current provider boundary:

`src/providers/shopify-partner-billing.provider.ts`

Existing provider usage evidence remains authoritative for purchase activation. This task extends that provider with Historical `CHARGE_USAGE` evidence for operation-ledger convergence.

Provider references:

- Shopify App Events create API: `https://shopify.dev/docs/api/app-events/latest/creating-events`
- Shopify Partner Historical Events: `https://shopify.dev/docs/api/partner/latest/historical-events`

## Dependencies

- `ARCH-027-SHOPIFY-002`

`ARCH-027-BACKGROUND-001`, `ARCH-027-DATABASE-001` and `ARCH-027-SHOPIFY-001` are already accepted prerequisites in the existing ARCH-027 implementation chain; this task does not reopen them.

## Enables

None directly in this portable definition.

During final architecture reconciliation, `moda_architect` must add this task to any terminal ARCH-027 system-test dependency set that claims end-to-end Shopify BillingOperation convergence.

## Acceptance Criteria

- [ ] The Partner request uses the exact App + Shop + `CHARGE_USAGE` + durable occurrence-window filters described in R3; it does not query unbounded Partner history.
- [ ] Cursor pagination follows `pageInfo.endCursor`, stops when `hasNextPage` is false, and treats a still-open result after 5 pages / 500 edges as incomplete rather than exhaustive.
- [ ] Existing aggregate Shopify meter proof still activates a valid `RecoveryCreditPurchase` and grants purchased credits even when Historical Events has no matching charge yet.
- [ ] A Shopify `ONE_TIME_CHARGE` operation starts/continues unresolved with `state = INITIATING` and `providerReference = NULL` until exact Historical Charge evidence exists.
- [ ] Exactly one matching `CHARGE_USAGE` event writes its `Charge.chargeId` to `providerReference` and moves the exact linked operation to `CONFIRMED`.
- [ ] Historical Event `id`, `metadata.legacyChargeId`, `UsageEvent.shopifyIdempotencyKey` and `BillingOperation.requestKey` are never substituted for `Charge.chargeId`.
- [ ] A zero-candidate result leaves the operation unchanged for later retry.
- [ ] Multiple viable candidates leave the operation unchanged and produce bounded ambiguity telemetry.
- [ ] Plan, amount, currency, quantity, Shop/App identity or occurrence-window mismatch cannot confirm an operation.
- [ ] An existing different non-null `providerReference` is never overwritten.
- [ ] Reprocessing an already-confirmed same-reference operation is idempotent.
- [ ] Provider history failure does not roll back an already-proven purchase activation and does not set a false Subscription sync error.
- [ ] The operation confirmation path does not increment purchased credits, reactivate the purchase, or reschedule capacity as a side effect.
- [ ] WooCommerce billing reconciliation is unchanged.
- [ ] No new queue/worker/cron/infrastructure or database migration is introduced.
- [ ] New runtime logs use the shared structured logger and contain no credentials/full provider payloads.

## Validation

- [ ] `npm run prisma:generate` (or the repository-declared equivalent after inspecting `package.json`)
- [ ] focused Shopify Partner provider tests asserting the exact `events` GraphQL variables (`subjectType`, `subjectId`, `shopId`, `CHARGE_USAGE`, `occurredAtMin`, `occurredAtMax`), `Charge` selection, cursor propagation and 5-page/500-edge cap
- [ ] focused one-time-charge operation reconciliation tests
- [ ] existing `RecoveryCreditPurchaseService` reconciliation tests
- [ ] existing Shopify usage-event publisher tests
- [ ] existing billing-reconciliation tests
- [ ] Shopify billing regression suite(s) declared by the repository/task baseline
- [ ] disposable PostgreSQL integration proof covering `INITIATING + NULL -> CONFIRMED + chargeId`, replay, ambiguity/no-match and no duplicate entitlement grant
- [ ] repository typecheck
- [ ] changed-file lint
- [ ] production build
- [ ] `git diff --check`

Record exact commands/results in the Completion Report. Do not claim checks that were not run.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled/follow-on work.

If Shopify's observed Historical Events semantics cannot deterministically correlate the exact charge under the requirements above, return this task `blocked` with the concrete provider evidence. Do not invent a provider reference or weaken ambiguity handling merely to complete the task.

## Implementation Notes

- Prefer a small dedicated reconciliation collaborator instead of enlarging `billing-reconciliation.service.ts` with provider-specific matching logic.
- Query Historical Events only when at least one eligible unresolved Shopify one-time-charge operation exists for the Shop.
- Preserve the current hot path for Shops with no unresolved operation; do not add a Historical Events request to every Shopify reconciliation unconditionally.
- Provider I/O must occur outside database transactions.
- Perform final operation mutation only after re-reading/locking durable evidence in a short transaction.
- Use decimal-safe comparisons for provider amounts and quantities. Do not compare monetary decimals through JavaScript floating-point arithmetic.
- Keep the Historical Events result type provider-local; this is not a new Shared cross-service runtime contract.
- Do not couple this task to Shopify refund correlation. Refunds remain on the existing meter-correction path.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

- Shopify Partner Historical Events `CHARGE_USAGE` remains available to the existing Partner API client and exposes `Charge.chargeId`, amount/currency, `usageQuantity`, `planHandle`, `occurredAt`, Shop and App subject evidence as documented for Partner API 2026-07 on 2026-10-12.
- The existing Background provider-usage reconciliation remains the entitlement/purchase-activation authority.

### Unresolved Issues

None at definition time.

### Architectural Concerns

The Historical `Charge` contract does not expose Moda's App Events idempotency key or purchase meter handle. Exact unique correlation therefore depends on the already-linked purchase plus provider-confirmed amount/currency/quantity/plan/time evidence. Any real provider behavior that makes those fields insufficient is an architectural gap and must be returned to `moda_architect` rather than guessed around.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation.

### Follow-up

None
