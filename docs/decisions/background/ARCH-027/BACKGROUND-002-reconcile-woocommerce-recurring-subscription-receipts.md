---
id: ARCH-027-BACKGROUND-002
architecture_id: ARCH-027
title: Reconcile WooCommerce recurring subscription webhook receipts
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-API-005
  - ARCH-027-BACKGROUND-001
enables:
  - ARCH-027-BACKGROUND-003
created: 2026-10-03
updated: 2026-10-03
---

# Reconcile WooCommerce recurring subscription webhook receipts

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Consume durably accepted **Woo subscription** webhook receipts from PostgreSQL and project verified recurring-provider lifecycle evidence onto the Shop's existing Moda billing state.

The bounded flow is:

```text
WooCommerceBillingWebhookReceipt
    processedAt = NULL
    normalizedPayload.subscription exists
        |
        v
claim with PostgreSQL FOR UPDATE SKIP LOCKED
        |
        v
resolve providerContractId only against trusted Moda state
        |
        v
apply exactly one idempotent recurring transition
        |
        +-- activated          -> Free -> paid
        +-- updated            -> paid -> paid switch
        +-- renewed            -> active/unfreeze evidence only
        +-- paused             -> FROZEN
        +-- canceled           -> cancelAtPeriodEnd = true
        +-- refunded           -> cancellation evidence only
        `-- prepaid_term_ended -> paid -> existing local Free
        |
        v
mark the same receipt processed in the SAME transaction
```

This task owns recurring subscription lifecycle projection only.

It MUST NOT:

- process `charge` webhook receipts;
- activate/refund `RecoveryCreditPurchase`;
- call Woo provider APIs;
- load Woo credentials;
- reset included capacity from Woo `next_payment_date`;
- implement the scheduled local Woo `EVERY_30_DAYS` entitlement rollover;
- create another Subscription;
- introduce a generic billing-provider lifecycle framework.

## Context

ARCH-027 has already fixed:

- API-003: recurring create/switch/cancel intent is persisted before provider writes;
- API-005: Woo webhooks are HMAC-verified and durably stored without business mutation;
- BACKGROUND-001: paid included recovery accounting is Woo-safe and uses `currentAllowanceQuantity ?? grantedQuantity`;
- DATABASE-001: one Subscription per Shop plus durable Woo operations/receipts and current allowance.

### Source finding — freeze the operational paid BillingPlan before Woo checkout

The existing Shopify `BillingPlanResolutionService` copies durable catalogue feature/allowance state into an operational `BillingPlan`.

`WooCommerceBillingOperation` snapshots:

```text
merchantPricingPlanId
quotedAmountMinor
quotedCurrency
quotedBillingPeriod
```

but it does not snapshot every feature/configuration/included-allowance field that becomes part of the operational plan.

If paid BillingPlan materialisation waits until the webhook arrives, an Admin edit between:

```text
merchant initiates checkout
merchant confirms checkout
```

could change the operational entitlement/feature projection after plan selection.

Therefore the companion API-003 correction included with this definition requires API-003 to reuse/generalise API-001's bounded operational-plan resolver before provider I/O:

```text
MerchantPricingPlan
    -> resolve/reuse/materialise BillingPlan
    -> persist Woo command intent
    -> commit
    -> call Woo
```

This is **not** entitlement activation. API-003 still does not change `Subscription.planId`, BillingPeriod or counters before provider confirmation.

BACKGROUND-002 therefore resolves an already-materialised paid plan; it does not materialise one.

### Woo provider lifecycle facts

Woo's Marketplace SaaS Billing documentation states:

- `activated` confirms successful subscription checkout/payment;
- `updated` confirms a subscription switch;
- `renewed` confirms a successful renewal;
- `paused` indicates renewal payment failure while Woo retries;
- `canceled` schedules cancellation while prepaid access remains until provider end;
- `prepaid_term_ended` signals that prepaid access actually ended;
- subscription refund approval also cancels the contract and emits refund/cancel lifecycle evidence;
- Woo webhook payloads contain provider contract identity, not merchant identity;
- provider `next_payment_date` may move because of proration.

Provider reference verified 3 October 2026:

`https://developer.woocommerce.com/docs/woo-marketplace/billing-api-saas`

ARCH-027 intentionally keeps Woo financial dates separate from Moda's local recovery-entitlement cadence.

## Scope

Modify only `moda-interact-background` implementation/tests needed for:

1. bounded claiming of unprocessed Woo **subscription-wrapper** receipts;
2. trusted external-contract correlation;
3. recurring subscription lifecycle projection;
4. receipt processed/error bookkeeping;
5. integration into the existing leased billing worker cycle.

Expected implementation areas are conceptually:

```text
src/services/woocommerce-billing/
  subscription-receipt-reconciliation.service.ts
  subscription-operation-resolution.ts
  subscription-transition.service.ts

src/entrypoints/billing.ts
```

Exact repository-local filenames may differ where the accepted refactor provides a clearer bounded owner.

Update the nested `database/` gitlink to the newest compatible architect-accepted database main commit and regenerate Prisma before source changes.

Reuse:

- the existing billing worker deployment;
- the existing leased billing scheduler;
- Prisma transactions;
- existing Shop/Subscription lock conventions;
- existing paid-period close/release semantics;
- `recoveryCapacityResumeService`;
- Shared structured logging.

Do not add another worker deployment.

## Out of Scope

- Woo `charge` receipt processing.
- Top-up activation/refund settlement.
- Woo provider GET/POST/DELETE calls.
- Woo credentials.
- Scheduled local Woo BillingPeriod rollover after the first period.
- Using `next_payment_date` as a Moda allowance-reset boundary.
- Shopify Partner API reconciliation changes.
- Shopify same-cycle plan-change behavior.
- API webhook validation.
- API command initiation.
- Admin/Woo UI.
- Gateway changes.
- Prisma schema/migration edits other than advancing the accepted nested database gitlink.
- A Shared lifecycle-event contract.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Use the existing billing worker

Instantiate the Woo recurring receipt reconciler from:

```text
src/entrypoints/billing.ts
```

and run it from the existing leased billing reconciliation cycle.

Do not create a new Render worker, BullMQ queue or cron service.

### R2 — Exact bounded scan

Define:

```text
MAX_WOO_SUBSCRIPTION_RECEIPTS_PER_CYCLE = 50
```

Attempt at most 50 receipts per leased cycle.

Eligibility:

```text
processedAt IS NULL
normalizedPayload has top-level key "subscription"
topic IN (
  saas_billing_contract.activated,
  saas_billing_contract.updated,
  saas_billing_contract.renewed,
  saas_billing_contract.paused,
  saas_billing_contract.canceled,
  saas_billing_contract.prepaid_term_ended,
  saas_billing_contract.refunded
)
```

Order:

```text
receivedAt ASC,
id ASC
```

Never select `charge` receipts in this task.

### R3 — `FOR UPDATE SKIP LOCKED` claiming

Process each receipt in its own transaction.

Select one eligible receipt using PostgreSQL row locking equivalent to:

```sql
SELECT "id"
FROM "woocommerce"."WooCommerceBillingWebhookReceipt"
WHERE "processedAt" IS NULL
  AND "normalizedPayload" ? 'subscription'
  AND "topic" IN (...)
  AND (
       :no_cursor
       OR "receivedAt" > :cursor_received_at
       OR ("receivedAt" = :cursor_received_at AND "id" > :cursor_id)
      )
ORDER BY "receivedAt" ASC, "id" ASC
FOR UPDATE SKIP LOCKED
LIMIT 1;
```

Advance an in-memory `(receivedAt,id)` cursor after every attempted row so one process does not immediately retry the same unresolved receipt in the same cycle.

The next leased cycle starts again from the oldest unprocessed row.

Do not add a `claimedAt` database column.

### R4 — Business mutation and receipt completion are atomic

For a successful transition or a valid stale/idempotent no-op, the same transaction commits:

```text
business state
+
receipt.processedAt = reconciliation now
+
receipt.processingError = NULL
```

Never mark the receipt processed before its transition commits.

### R5 — Retryable/domain failure bookkeeping

If a recognized receipt cannot yet be reconciled safely:

```text
processedAt = NULL
processingError = one bounded code
```

Canonical codes:

```text
CONTRACT_CORRELATION_NOT_READY
CONTRACT_TENANT_CONFLICT
UNEXPECTED_CONTRACT_STATUS
SUBSCRIPTION_STATE_CONFLICT
TARGET_OPERATION_NOT_READY
TARGET_OPERATION_AMBIGUOUS
TARGET_PLAN_NOT_MATERIALIZED
TARGET_PLAN_INVALID
BILLING_PERIOD_STATE_CONFLICT
INVALID_INCLUDED_ALLOWANCE
FREE_PLAN_NOT_AVAILABLE
```

Do not store raw provider JSON/stack traces in `processingError`.

Unexpected infrastructure transaction failure may leave the row untouched and be retried on the next cycle.

### R6 — Revalidate only the provider fields this task uses

Require:

```text
normalizedPayload is an object
exactly one `subscription` object
subscription.id = receipt.providerContractId
subscription.id is non-blank
subscription.status is non-blank
```

Topic/status compatibility:

```text
activated          -> active
updated            -> active
renewed            -> active
paused             -> paused
canceled           -> canceled
prepaid_term_ended -> canceled
refunded           -> canceled
```

Mismatch:

```text
UNEXPECTED_CONTRACT_STATUS
```

and leave the receipt unprocessed.

### R7 — Resolve tenant only through trusted Moda state

Never derive a Shop from provider merchant PII, URL/domain or browser-return state.

Use only:

```text
WooCommerceBillingOperation.providerContractId
Subscription.providerSubscriptionId
```

If one external recurring contract maps to more than one distinct `shopId` across these trusted records:

```text
CONTRACT_TENANT_CONFLICT
```

and no business state changes.

### R8 — Deterministic business lock order

Initial bounded non-locking reads may discover the candidate Shop.

Once one Shop is identified, lock in this order:

```text
1. commerce.Shop
2. billing.Subscription
3. relevant WooCommerceBillingOperation rows ordered by id
4. current BillingPeriod when required
5. INCLUDED_RECOVERY_CREDITS counter when required
```

Then re-read/revalidate all correlation predicates before mutation.

This preserves compatibility with API Shop -> Subscription locking and avoids operation -> Shop deadlock inversion.

### R9 — Lifecycle audit ordering

Use local durable receipt order for the existing generic lifecycle audit fields:

```text
lastProviderLifecycleEventAt = receipt.receivedAt
lastProviderLifecycleEventId = receipt.id
```

Map states:

```text
activated            -> CREATED
updated              -> UPDATED
renewed from FROZEN  -> UNFROZEN
renewed otherwise    -> UPDATED
paused               -> FROZEN
canceled             -> CANCELLATION_SCHEDULED
refunded             -> CANCELLATION_SCHEDULED
prepaid_term_ended   -> CANCELED
```

If the persisted local lifecycle position is strictly newer by `(eventAt,eventId)`, process the incoming row as a stale no-op.

Woo does not publish a separate signed webhook event sequence/id. This local order prevents local concurrent inversion but does not claim perfect provider-causal reconstruction of arbitrarily delayed cross-topic webhooks; sandbox/system tests remain required for pause/renew sequencing.

### R10 — Target paid plan is already materialised

For `activated` / `updated`:

```text
operation.merchantPricingPlanId
    -> MerchantPricingPlan
    -> MerchantPricingPlan.shopifyPlanHandle
    -> BillingPlan.shopifyPlanHandle
```

Require:

```text
MerchantPricingPlan exists
MerchantPricingPlan.isActive = true
MerchantPricingPlan.planKind = PAID_METERED
MerchantPricingPlan.billingPeriod = EVERY_30_DAYS
includedRecoveryCredits is a non-negative safe integer

BillingPlan exists
BillingPlan.active = true
BillingPlan.kind = PAID_METERED
BillingPlan.includedRecoveryConversationAllowance
    = MerchantPricingPlan.includedRecoveryCredits
```

Missing operational plan:

```text
TARGET_PLAN_NOT_MATERIALIZED
```

BACKGROUND-002 MUST NOT create a BillingPlan or copy feature mappings.

### R11 — `activated` requires a trusted create operation

For `saas_billing_contract.activated` with a subscription wrapper, find:

```text
kind = SUBSCRIPTION_CREATE
providerContractId = receipt.providerContractId
```

A new activation requires exactly one matching operation in:

```text
AWAITING_CONFIRMATION
OUTCOME_UNKNOWN
```

Its `shopId` and `merchantPricingPlanId` are authoritative.

If none exists:

- if the current Subscription already uses this contract and the create operation is `CONFIRMED`, treat as a duplicate/stale success;
- otherwise use `CONTRACT_CORRELATION_NOT_READY`.

A delayed old activated receipt MUST NOT reactivate a historical contract after the Shop has returned to Free.

### R12 — Initial activation replaces only the existing local Free projection

Require:

```text
Shop.platform = WOOCOMMERCE
Shop.status = ACTIVE
Shop.onboardingCompleted = true

Subscription exists
Subscription.status = ACTIVE
Subscription.plan.kind = FREE
Subscription.providerSubscriptionId = NULL
Subscription.billingPeriodId = NULL
Subscription.cancelAtPeriodEnd = false
```

If another provider-backed paid contract is current:

```text
SUBSCRIPTION_STATE_CONFLICT
```

Never create a second Subscription.

### R13 — First local paid period is exactly 30 days from receipt acceptance

For verified initial paid activation:

```text
periodStart = receipt.receivedAt
periodEnd   = periodStart + 30 * 24 hours
```

Do not use Woo:

```text
next_payment_date
end_date
proration-adjusted date
browser return time
```

as the Moda recovery reset boundary.

Create one OPEN BillingPeriod:

```text
shopId
subscriptionId
planId = target BillingPlan.id

# compatibility snapshot only, not Woo provider identity
shopifyPlanHandleSnapshot = target BillingPlan.shopifyPlanHandle

planNameSnapshot = target BillingPlan.name
planKindSnapshot = PAID_METERED
includedRecoveryCreditsGranted = target allowance
periodStart
periodEnd
status = OPEN
```

There must be no pre-existing OPEN BillingPeriod for the Free -> paid activation.

### R14 — Initial paid included counter

Create:

```text
counter = INCLUDED_RECOVERY_CREDITS
grantedQuantity          = target allowance
currentAllowanceQuantity = target allowance
committedQuantity        = 0
reservedQuantity         = 0
forfeitedQuantity        = 0
```

Target allowance may be zero but must be a safe non-negative integer.

### R15 — Activate the existing Subscription row in place

In the same transaction:

```text
planId                 = target BillingPlan.id
status                 = ACTIVE
billingPeriodId        = new period.id
currentPeriodStart     = periodStart
currentPeriodEnd       = periodEnd
trialEndsAt            = NULL
cancelAtPeriodEnd      = false
providerSubscriptionId = receipt.providerContractId

observedShopifyPlanHandle = NULL
pendingShopifyPlanHandle  = NULL
pendingPlanId              = NULL
pendingEffectiveAt         = NULL
nextReconcileAt            = NULL

lastSyncedAt      = reconciliation now
lastSyncErrorCode = NULL
lastSyncErrorAt   = NULL
```

Do not reset onboarding.

Do not create/update the lifetime Free counter.

Preserve purchased/promotional/lifetime balances.

### R16 — Confirm create operation atomically

Compare-and-set the matching create operation:

```text
AWAITING_CONFIRMATION | OUTCOME_UNKNOWN
    -> CONFIRMED

lastErrorCode = NULL
```

in the same activation transaction.

Immutable operation target/quote/provider-contract evidence stays unchanged.

### R17 — `updated` requires one unresolved PLAN_SWITCH

Resolve the current Subscription by exact provider contract.

Require:

```text
status IN (ACTIVE, FROZEN)
current plan = PAID_METERED
current BillingPeriod = OPEN
```

Find PLAN_SWITCH operations for the same Shop/contract.

Exactly one in:

```text
AWAITING_CONFIRMATION
OUTCOME_UNKNOWN
```

is required to apply a switch.

More than one:

```text
TARGET_OPERATION_AMBIGUOUS
```

None:

- if a confirmed switch operation targets the already-current plan, process as duplicate;
- otherwise `TARGET_OPERATION_NOT_READY`.

Never infer the target plan from Woo JSON.

### R18 — Plan switch keeps the current BillingPeriod

A verified switch MUST NOT:

```text
create/close a BillingPeriod
change currentPeriodStart/end
reset committed/reserved/forfeited usage
```

Update:

```text
Subscription.planId = target BillingPlan.id
Subscription.status = ACTIVE
```

Keep:

```text
providerSubscriptionId
billingPeriodId
currentPeriodStart/end
```

unchanged.

Do not rewrite current BillingPeriod plan/name/handle snapshots; they remain opening-period audit context.

### R19 — Plan switch allowance transition

Let:

```text
targetAllowance = target BillingPlan.includedRecoveryConversationAllowance

oldEffective =
    currentAllowanceQuantity
    ?? grantedQuantity
```

Apply atomically:

```text
if targetAllowance > grantedQuantity:
    grantedQuantity = targetAllowance

currentAllowanceQuantity = targetAllowance
version += 1
```

Preserve:

```text
committedQuantity
reservedQuantity
forfeitedQuantity
```

Update the BillingPeriod high-water snapshot only upward:

```text
includedRecoveryCreditsGranted =
    max(existing includedRecoveryCreditsGranted, targetAllowance)
```

Never lower the historical grant snapshot on downgrade.

### R20 — Confirm switch operation atomically

In the same switch transaction:

```text
AWAITING_CONFIRMATION | OUTCOME_UNKNOWN
    -> CONFIRMED

lastErrorCode = NULL
```

A later duplicate where operation/current plan already match is a processed no-op.

### R21 — Resume blocked recoveries only when a switch creates capacity

Compute `availableBefore` / `availableAfter` using BACKGROUND-001 semantics.

If:

```text
availableAfter > availableBefore
```

after commit schedule:

```text
recoveryCapacityResumeService.schedule({
  shopId,
  trigger: "woo-plan-change"
})
```

Enqueue failure does not roll back committed billing state; log a bounded warning.

### R22 — `renewed` never resets the local period

For `renewed` / active:

- require exactly one current Subscription using the provider contract;
- do not create/close/rotate a BillingPeriod;
- do not modify current allowance;
- do not use `next_payment_date` as a Moda reset date.

If current status is `FROZEN`, set:

```text
ACTIVE
```

and after commit schedule:

```text
trigger = "woo-renewed"
```

If already ACTIVE, the receipt updates lifecycle audit only.

A separate follow-on task owns local `EVERY_30_DAYS` period rollover.

### R23 — `paused` freezes without deleting entitlement state

For `paused` / paused:

```text
Subscription.status = FROZEN
```

Preserve:

```text
planId
billingPeriodId
currentPeriodStart/end
providerSubscriptionId
cancelAtPeriodEnd
all counters/reservations
all purchased/lifetime/promotional balances
```

Do not close the period.

### R24 — `canceled` schedules termination, not Free fallback

For `canceled` / canceled:

```text
cancelAtPeriodEnd = true
```

Preserve plan/status/period/provider contract.

If a matching CANCEL operation for the same Shop/contract is:

```text
INITIATING
OUTCOME_UNKNOWN
```

compare-and-set it to:

```text
CONFIRMED
lastErrorCode = NULL
```

Already-CONFIRMED remains unchanged.

Do not use Woo `end_date` as the Moda recovery reset/close boundary.

### R25 — Subscription `refunded` is cancellation evidence only

For `refunded` / canceled:

```text
cancelAtPeriodEnd = true
```

Do not:

- switch to Free immediately;
- close the current period;
- create `RecoveryCreditRefund` (that model owns purchased credit lots);
- infer provider monetary settlement into Moda capacity.

Woo also emits cancellation lifecycle evidence; prepaid-term end remains the actual access-end transition.

### R26 — `prepaid_term_ended` returns the same Subscription to existing local Free

Resolve exactly one active Free `MerchantPricingPlan` and the already-materialised active Free `BillingPlan`.

Do not materialise Free in Background.

If not resolvable:

```text
FREE_PLAN_NOT_AVAILABLE
```

### R27 — Close the current paid period at prepaid-term end

When the current paid period is OPEN:

1. lock the included counter;
2. require aggregate RESERVED/AMBIGUOUS reservation quantity equals `counter.reservedQuantity`;
3. release those reservations with `PERIOD_CLOSED`;
4. set:
   ```text
   reservedQuantity -> 0

   forfeitedQuantity +=
       grantedQuantity
       - committedQuantity
       - forfeitedQuantity

   version += 1
   ```
5. require:
   ```text
   committedQuantity + forfeitedQuantity = grantedQuantity
   reservedQuantity = 0
   ```
6. move any Shopify `PENDING`/`RETRYABLE` usage for that period to the existing `NEEDS_ATTENTION` close behavior; Woo `NOT_APPLICABLE` usage remains untouched;
7. close:
   ```text
   status = CLOSED
   closedAt = receipt.receivedAt
   closeReason = CONTRACT_ENDED
   ```

Close against `grantedQuantity`, not the lower mutable current allowance.

### R28 — Free fallback preserves one-time merchant state

In the same terminal transaction:

```text
Subscription.planId = Free BillingPlan.id
Subscription.status = ACTIVE

billingPeriodId = NULL
currentPeriodStart = NULL
currentPeriodEnd = NULL

providerSubscriptionId = NULL
cancelAtPeriodEnd = false
trialEndsAt = NULL

observedShopifyPlanHandle = NULL
pendingShopifyPlanHandle = NULL
pendingPlanId = NULL
pendingEffectiveAt = NULL
nextReconcileAt = NULL

lastSyncedAt = reconciliation now
lastSyncErrorCode = NULL
lastSyncErrorAt = NULL
```

Do not set onboarding false.

Do not recreate/reset lifetime Free credits.

Preserve all purchased/promotional/history state.

After commit schedule:

```text
recoveryCapacityResumeService.schedule({
  shopId,
  trigger: "woo-prepaid-term-ended"
})
```

### R29 — Lifecycle audit fields

Every successful recurring transition/no-op updates lifecycle audit when the Subscription still represents that contract:

```text
lastProviderLifecycleState
lastProviderLifecycleEventId
lastProviderLifecycleEventAt
lastSyncedAt
```

using R9.

For terminal prepaid end, write terminal lifecycle audit in the same transaction that clears the provider contract.

### R30 — Stale/replayed receipts cannot regress terminal state

Examples that must become no-op:

```text
old activated
    after prepaid_term_ended returned the Shop to Free

old updated
    after its switch operation is confirmed and a newer switch is current

duplicate paused/canceled/refunded
    after same/newer local lifecycle evidence
```

For non-activation topics, if current `Subscription.providerSubscriptionId` no longer equals the receipt contract, do not mutate the Subscription.

### R31 — No Woo network dependency

This task makes no Woo network calls and loads no Woo billing credentials.

Trusted evidence is:

```text
signed durable receipt
+
Moda operations/subscription state
```

only.

### R32 — Periodic Woo local rollover is a separate task

Initial activation creates the first local 30-day period.

Plan switch leaves it unchanged.

Renewal leaves it unchanged.

This task does not advance an ACTIVE Woo paid merchant when:

```text
now >= Subscription.currentPeriodEnd
```

because that scheduled local cadence has different trigger/race semantics and is a separate Background task.

### R33 — Logging

Use the Shared structured logger.

Allowed bounded fields:

```text
receiptId
topic
providerContractId
shopId after trusted correlation
subscriptionId
operationId
transition outcome
processingError code
```

Never log the full provider payload, transaction URLs, credentials or payment/customer details.

## Work Items

- [ ] Update nested database gitlink to the accepted ARCH-027 database commit and regenerate Prisma.
- [ ] Add Woo subscription receipt reconciliation to the existing billing worker.
- [ ] Add exact 50-per-cycle selection ordered by `(receivedAt,id)`.
- [ ] Claim one receipt per transaction with `FOR UPDATE SKIP LOCKED`.
- [ ] Add in-cycle cursoring so one unresolved row is attempted at most once per cycle.
- [ ] Revalidate subscription wrapper/status by topic.
- [ ] Add contract-to-Shop correlation from operations/current Subscription only.
- [ ] Add cross-Shop contract conflict detection.
- [ ] Add deterministic Shop -> Subscription -> operation -> period -> counter lock ordering.
- [ ] Add bounded processingError handling while leaving failed rows unprocessed.
- [ ] Add lifecycle audit ordering from receipt receivedAt/id.
- [ ] Reconcile activated Free -> paid and confirm SUBSCRIPTION_CREATE.
- [ ] Require already-materialised paid BillingPlan; do not materialise in Background.
- [ ] Open initial local 30-day BillingPeriod and current-allowance counter.
- [ ] Reconcile updated plan switch in the same period and confirm PLAN_SWITCH.
- [ ] Preserve usage on switch and update high-water/current allowance correctly.
- [ ] Resume blocked recoveries only on capacity increase.
- [ ] Reconcile renewed without period reset; unfreeze when required.
- [ ] Reconcile paused to FROZEN.
- [ ] Reconcile canceled/refunded to scheduled cancellation without Free fallback.
- [ ] Reconcile prepaid_term_ended to existing Free, close paid period and preserve lifetime/purchased/history state.
- [ ] Confirm ambiguous CANCEL operations when canceled evidence proves the provider action.
- [ ] Mark receipt processed atomically with every successful transition/no-op.
- [ ] Add focused concurrency/idempotency/lifecycle/negative tests.

## Interfaces / Contracts

### Durable input

Owner:

`ARCH-027-DATABASE-001`

Producer:

`ARCH-027-API-005`

Table:

```text
woocommerce.WooCommerceBillingWebhookReceipt
```

This task consumes only rows where:

```text
processedAt = NULL
normalizedPayload.subscription exists
```

### Trusted contract correlation

```text
providerContractId
    -> WooCommerceBillingOperation
    and/or current Subscription
    -> one Shop
```

### Target operational plan

```text
operation.merchantPricingPlanId
    -> MerchantPricingPlan.shopifyPlanHandle
    -> already-materialised BillingPlan.shopifyPlanHandle
```

The Shopify handle is only a current-schema internal bridge.

### Local paid entitlement period

Initial activation:

```text
start = activated receipt.receivedAt
end   = start + exactly 30 days
```

Switch:

```text
same period
current allowance changes
usage unchanged
```

Provider renewal:

```text
no local period reset
```

Scheduled local rollover:

separate follow-on task.

## Dependencies

- `ARCH-027-API-005`
- `ARCH-027-BACKGROUND-001`

Both must be architect-accepted Complete before this task becomes Ready.

API-005 supplies authenticated durable receipts.

BACKGROUND-001 guarantees that activated Woo paid merchants already have safe local included-usage accounting and cannot enter the Shopify App Event publisher.

Through API-005's dependency chain, API-003 recurring operations exist for target-plan correlation.

## Enables

- `ARCH-027-BACKGROUND-003`

BACKGROUND-003 owns the independent local Woo `EVERY_30_DAYS` entitlement-period rollover after provider lifecycle projection is safe and accepted.

Woo one-time-charge receipt reconciliation remains a separate later task.

## Acceptance Criteria

- [ ] Existing billing worker executes this reconciler; no new deployable worker exists.
- [ ] At most 50 eligible subscription receipts are attempted per leased billing cycle.
- [ ] Selection is ordered by `(receivedAt,id)` and uses `FOR UPDATE SKIP LOCKED`.
- [ ] One process attempts the same unresolved row at most once per cycle.
- [ ] `charge` receipts are untouched.
- [ ] Transition + receipt processed state commit atomically.
- [ ] Domain failure leaves processedAt null with one bounded error code.
- [ ] Cross-Shop provider-contract ambiguity fails closed.
- [ ] Lock order matches the task contract.
- [ ] Provider status is revalidated per topic.
- [ ] Initial activation requires exactly one trusted unresolved create operation.
- [ ] Initial activation updates the existing Free Subscription row; no second Subscription is created.
- [ ] Paid target BillingPlan must already exist from API-003 materialisation.
- [ ] First paid local period starts at receipt receivedAt and ends exactly 30 days later.
- [ ] First included counter has granted/current allowance equal to target and zero usage.
- [ ] Create operation is confirmed atomically with activation.
- [ ] Switch requires exactly one unresolved matching PLAN_SWITCH.
- [ ] Switch keeps period ID/start/end unchanged.
- [ ] Switch preserves committed/reserved/forfeited usage.
- [ ] Switch raises high-water only when needed and always sets current allowance to target.
- [ ] Capacity resume is scheduled only when immediately available capacity increases.
- [ ] Renewed never resets/rotates the local period.
- [ ] Renewed unfreezes FROZEN current contract.
- [ ] Paused sets FROZEN and preserves plan/period/credits.
- [ ] Canceled sets cancelAtPeriodEnd and preserves paid access.
- [ ] Subscription refunded marks cancellation without immediate Free fallback.
- [ ] Prepaid-term-ended closes the paid period with CONTRACT_ENDED and returns the same Subscription to existing Free.
- [ ] Prepaid-term-ended does not re-grant/reset lifetime Free credits or onboarding.
- [ ] Historical old-contract receipts cannot reactivate after Free fallback.
- [ ] No Woo provider network/credential access occurs.
- [ ] No periodic local Woo period rollover is implemented.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the accepted `moda-interact-background/package.json` and prerequisite implementations before choosing commands.

Required categories:

- [ ] Prisma generate/validate;
- [ ] repository production build/typecheck;
- [ ] targeted lint/changed-file diagnostics;
- [ ] scan batch-limit/order/cursor tests;
- [ ] two-worker `SKIP LOCKED` concurrency test;
- [ ] unresolved receipt retry-next-cycle test;
- [ ] charge-receipt exclusion test;
- [ ] cross-Shop contract collision negative test;
- [ ] activated correlation-not-ready then retry-after-operation-update test;
- [ ] activated Free -> paid integration test;
- [ ] duplicate/byte-distinct activated idempotency tests;
- [ ] delayed activated after prepaid-end no-reactivation test;
- [ ] exact initial 30-day period anchor test;
- [ ] initial granted/current allowance counter test;
- [ ] missing materialised paid BillingPlan negative test;
- [ ] updated switch integration test;
- [ ] downgrade below committed usage test;
- [ ] upgrade high-water/current-allowance test;
- [ ] switch keeps period identity/dates test;
- [ ] PLAN_SWITCH operation confirmation CAS test;
- [ ] renewed ACTIVE no-reset test;
- [ ] paused -> renewed FROZEN/ACTIVE restoration test;
- [ ] local stale/duplicate lifecycle ordering tests;
- [ ] canceled prepaid-access preservation test;
- [ ] OUTCOME_UNKNOWN CANCEL confirmation test;
- [ ] refunded no-immediate-Free test;
- [ ] prepaid-term-ended paid -> Free integration test;
- [ ] prepaid-term-ended reservation release/high-water close test;
- [ ] lifetime Free counter exact-preservation test;
- [ ] purchased/promotional state preservation test;
- [ ] no Woo provider HTTP/secret access assertion;
- [ ] no `charge` mutation assertion;
- [ ] transition/receipt atomic rollback test;
- [ ] bounded processingError/no-payload-leak test;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization, nested database gitlink and pushed task-branch evidence.

Real Woo sandbox event ordering remains a later system-test gate.

## Stop Condition

After all Work Items, Acceptance Criteria and Validation are complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin local Woo period rollover or charge receipt reconciliation.

## Implementation Notes

Prefer one bounded Woo-specific collaborator around the refactored billing worker rather than adding Woo branches throughout Shopify Partner reconciliation.

Do not reuse Shopify `PartnerSubscription` as a Woo contract type.

The convergence point is:

```text
Subscription
BillingPeriod
BillingPeriodEntitlementCounter
```

not a generic provider framework.

`BillingPeriod.shopifyPlanHandleSnapshot` may contain the existing operational BillingPlan handle for Woo only as current-schema compatibility/audit data. It is not Woo provider identity.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- API-003 is corrected/implemented to resolve/reuse/materialise the selected paid operational BillingPlan before provider I/O while leaving Subscription/BillingPeriod untouched.
- Woo paid local recovery entitlement uses an independent 30-day cadence.
- Woo refund approval also causes provider cancellation as documented.
- API-005 already authenticated the webhook raw body; Background consumes durable receipts only.

### Unresolved Issues

- Woo does not expose a separate signed webhook sequence/event ID. ARCH-027 uses durable receipt arrival ordering plus transition guards; arbitrary provider-causal reordering remains a sandbox/system-test concern.
- Periodic local 30-day rollover is deliberately separate.
- One-time charge receipt reconciliation is deliberately separate.

### Architectural Concerns

None beyond the recorded provider event-ordering limitation.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
