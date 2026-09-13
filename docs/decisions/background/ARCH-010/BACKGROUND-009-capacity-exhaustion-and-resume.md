---
id: ARCH-010-BACKGROUND-009
architecture_id: ARCH-010
title: Persist recovery exhaustion and resume blocked recoveries when capacity returns
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 53
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHARED-008
- ARCH-010-BACKGROUND-002
- ARCH-010-BACKGROUND-011
- ARCH-007-BACKGROUND-003
- ARCH-007-BACKGROUND-009
- ARCH-010-BACKGROUND-019
enables:
- ARCH-010-BACKGROUND-007
- ARCH-010-BACKGROUND-012
- ARCH-010-SHOPIFY-008
- ARCH-010-SYSTEM-TEST-001
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-BACKGROUND-009: Persist recovery exhaustion and resume blocked recoveries when capacity returns

## Objective

Make full recovery-capacity exhaustion a durable, explainable and recoverable execution state.

When all currently supported checkout-recovery capacity is exhausted:

```text
Free: promotional credits -> purchased credits -> shop-lifetime Free credits -> exhausted
Paid: selected promotional credits -> current-period included credits -> purchased credits -> shop-lifetime Free credits -> exhausted
```

Background must block only **new recovery initiation**, preserve the subscription and existing conversations, persist why a DETECTED recovery did not start, notify the merchant once per capacity epoch, and automatically retry still-recoverable blocked checkouts when capacity later returns.

There is no automatic paid overage.

## Inspect before editing

```text
src/services/recovery-billing.service.ts
src/services/checkout-recovery.service.ts
src/services/free-recovery-reservation.service.ts
src/services/purchased-recovery-reservation.service.ts
src/services/recovery-credit-purchase.service.ts
src/services/effective-billing-policy.service.ts
src/services/abandoned-checkout-lookup.service.ts
src/services/pending-recovery-candidate.service.ts
src/workers/pending-recovery-candidate.worker.ts
src/entrypoints/recovery.ts
src/lib/redis.ts
src/domain/**
src/observability/**
database/prisma/schema.prisma
package.json
```

Read the implemented form of `ARCH-010-BACKGROUND-002` before editing. Do not restore the removed paid-overage branch.

Consume the published Shared system-message code only from:

```text
@modainteract/moda-interact-shared/billing
```

## 1. Canonical blocked admission result

Use a plan-neutral blocked result for **all capacity sources exhausted**, e.g.:

```text
{ kind: "blocked", reason: "capacity-exhausted" }
```

Do not use `paused`, `reservation-in-flight` or a provider error to represent zero capacity.

Required routing remains:

```text
FREE
  -> promotional reservation
  -> purchased reservation
  -> shop-lifetime Free reservation
  -> capacity-exhausted

PAID
  -> selected promotional reservation
  -> current-period included reservation
  -> purchased reservation
  -> shop-lifetime Free reservation
  -> capacity-exhausted
```

When capacity-exhausted:

- no Meta/WhatsApp provider call;
- no normal recovery UsageEvent;
- no hidden overage event;
- no retry exception merely because capacity is zero.

## 2. Persist the recovery block

`CheckoutRecoveryService.handleCheckoutCreated()` currently has a durable DETECTED recovery before billing admission. When admission returns `capacity-exhausted`, atomically/idempotently mark that recovery using DATABASE-005:

```text
admissionBlockReason = RECOVERY_CAPACITY_EXHAUSTED
admissionBlockedAt   = first time this recovery entered the block
status               = DETECTED
```

Replays while still exhausted must preserve the original `admissionBlockedAt`; do not continually rewrite it.

Do not create a new CheckoutRecovery status.

When the same recovery later successfully initiates and transitions to `MESSAGE_SENT`, clear both block fields in the same durable lifecycle transition or in an immediately adjacent transactionally-safe operation. Terminal recovery transitions must not leave a row falsely presented as waiting for capacity.

## 3. Generic merchant SYSTEM message

Use only `BILLING_RECOVERY_CAPACITY_EXHAUSTED` for full capacity exhaustion. Remove any Background producer/branch that writes `BILLING_FREE_ALLOWANCE_EXHAUSTED`; first production has no historical-row compatibility requirement for that development-only code.

Write new exhaustion notifications with:

```text
BILLING_RECOVERY_CAPACITY_EXHAUSTED
```

Use the existing merchant-support thread/message and translation pipeline. Do not invent a second notification store.

### Message body semantics

For Free, convey:

```text
Every applicable Free-plan recovery-capacity source is exhausted: promotional credits, purchased credits and shop-lifetime Free. New abandoned-checkout recoveries are paused. Existing conversations continue. The merchant can manage recovery capacity or change plan.
```

For Paid, convey:

```text
Every applicable recovery-capacity source is exhausted: Paid monthly included where applicable, promotional credits, purchased credits and shop-lifetime Free. New abandoned-checkout recoveries are paused. Existing conversations continue. Capacity returns when any canonical source becomes available again.
```

Persist platform-language source text using the existing translation pipeline; do not bypass localization infrastructure.

### Idempotent exhaustion epoch

Do not create one message per blocked checkout.

Construct a deterministic exhaustion lifecycle/source key from durable capacity facts.

For Free include at least:

```text
subscriptionId
selected PromotionalCreditGrant id/version/quantity/committedQuantity/reservedQuantity when usable
purchased grantedQuantity/committedQuantity/reservedQuantity/refundingQuantity
lifetime Free grantedQuantity/committedQuantity/reservedQuantity
```

For Paid include at least:

```text
current BillingPeriod id
selected PromotionalCreditGrant id/version/quantity/committedQuantity/reservedQuantity when usable
included BillingPeriod id/grantedQuantity/committedQuantity/reservedQuantity/forfeitedQuantity
purchased grantedQuantity/committedQuantity/reservedQuantity/refundingQuantity
lifetime Free grantedQuantity/committedQuantity/reservedQuantity
```

A later campaign selection/grant restoration, purchased top-up, verified Paid period or other canonical capacity restoration creates a new durable capacity epoch. No legacy signed lifetime-Free adjustment state exists in the first-production model.

Do not include customer identifiers, checkout token, phone number or message content in the lifecycle key.

## 4. Existing conversations are not blocked

Do not add capacity checks to already-admitted recovery-conversation customer replies/CommerceAgent continuation merely because the shop now has zero capacity for **new** recoveries.

Continue to enforce existing:

```text
Shop.status
BillingPlanFeature mappings
outbound safety limits
abuse admission
provider configuration
```

Capacity exhaustion is not an uninstall/suspension switch.

## 5. Capacity-resume queue — Background internal contract

Create one Background-owned BullMQ queue, for example:

```text
queue: recovery-capacity-resume
job:   resume-capacity-blocked-recoveries
```

This queue is produced and consumed only by `moda-interact-background`; do not add it to `moda-interact-shared`.

Define one strict local payload in a focused domain module. Keep it bounded and tenant-scoped, e.g.:

```ts
{
  shopId: string;
  trigger: string; // bounded non-sensitive deterministic trigger identity
}
```

Provide a deterministic BullMQ job-ID helper containing no customer data and no `:` if current BullMQ custom-ID conventions prohibit it.

Use the existing Redis connection/telemetry conventions. Do not open one Redis connection per recovery.

## 6. Direct restoration hints

After capacity is durably restored, enqueue a best-effort shop resume hint **after** the committing database transaction.

### Purchased-credit activation

Extend `RecoveryCreditPurchaseService.reconcileProviderConfirmed(...)` so when one or more purchases become ACTIVE and `PURCHASED_RECOVERY_CREDITS.grantedQuantity` is incremented, it exposes enough deterministic result data to schedule one resume hint for that shop.

Do not publish before the transaction commits. Queue failure must not roll back credit activation.

### Paid BillingPeriod rollover

`ARCH-010-BACKGROUND-007` is amended to invoke the same resume scheduler after a successor Paid BillingPeriod + included counter are committed. Do not duplicate resume logic in BACKGROUND-007.

### Other restoration paths

A lifetime-Free adjustment, promotional grant or other capacity restoration does not need to enqueue directly. The repair scan below is the durable recovery mechanism.

## 7. Startup and periodic repair after Redis loss

The durable source is PostgreSQL, not BullMQ.

At recovery-worker startup and periodically thereafter, perform a bounded scan for distinct shops with:

```text
CheckoutRecovery.status = DETECTED
CheckoutRecovery.admissionBlockReason = RECOVERY_CAPACITY_EXHAUSTED
Shop.status = ACTIVE
```

Recommended implementation constraints for Luna:

- process at most 100 distinct shops per repair pass;
- use indexed/cursor or bounded distinct-query patterns supported by Prisma/PostgreSQL;
- do not load every blocked recovery into memory;
- enqueue at most one deterministic resume job per shop for that repair epoch;
- a queue-add failure is logged and left for the next repair pass;
- do not query Shopify merely to decide whether to enqueue repair work.

The resume job itself re-runs current local entitlement admission and stops immediately if capacity is still exhausted.

Use a modest repair interval such as 5 minutes unless an existing runtime scheduler abstraction already provides an equivalent bounded cadence. Do not create sub-minute polling.

## 8. Resume execution algorithm

The resume worker processes one shop at a time and uses the **oldest blocked recoveries first**.

For each job:

1. verify current `Shop.status = ACTIVE`; inactive -> successful terminal no-op;
2. select at most 25 `DETECTED + RECOVERY_CAPACITY_EXHAUSTED` recoveries ordered by `detectedAt ASC, id ASC`;
3. for each recovery, acquire/reuse the existing checkout-scoped lock before initiation;
4. re-fetch/revalidate the current abandoned checkout using the existing `abandonedCheckoutLookupService` and durable checkout/shop identifiers;
5. never send from only the stale stored checkout snapshot;
6. if the provider lookup is transient/provider-error, throw so BullMQ retry policy applies;
7. if the checkout is definitively no longer recoverable, use existing lifecycle/status-history conventions to make it terminal without sending; do not invent recovered revenue;
8. if still recoverable, retry the normal recovery initiation path so the ordinary billing reservation/provider-send/idempotency rules execute;
9. after one attempt returns `capacity-exhausted`, stop processing the remaining shop batch immediately;
10. after a successful send, the normal lifecycle clears the admission block and the worker proceeds to the next oldest blocked recovery;
11. if 25 rows were consumed and capacity is still available, enqueue/continue another bounded shop job rather than looping without bound in one BullMQ job.

If existing service structure prevents reuse without duplicating template selection/provider send, refactor `CheckoutRecoveryService` into one private/public reusable **attempt DETECTED recovery initiation** path. Do not create a second implementation of the send workflow.

## 9. Concurrency/idempotency

Prove that simultaneous direct restoration hints, periodic repair and duplicate BullMQ delivery cannot produce duplicate initial WhatsApp sends.

Use:

- existing checkout lock;
- existing `recovery-message:<recoveryId>` outbound idempotency identity;
- current recovery status guard;
- reservation replay semantics.

Do not globally serialize all shops.

## Required tests

At minimum prove:

1. Free full exhaustion persists DETECTED block and sends no provider call;
2. Paid full exhaustion persists the same generic block and sends no provider call;
3. purchased capacity available is consumed instead of marking exhausted;
4. block replay preserves first `admissionBlockedAt`;
5. one Free capacity epoch creates one SYSTEM message across multiple blocked checkouts;
6. one Paid capacity epoch creates one SYSTEM message across multiple blocked checkouts;
7. a new top-up grant creates a new epoch for future exhaustion;
8. a new paid BillingPeriod creates a new epoch for future exhaustion;
9. already admitted MESSAGE_SENT/ENGAGED conversation processing is not denied solely because new-recovery capacity is zero;
10. successful resumed initiation clears block fields;
11. direct top-up activation schedules a best-effort resume hint only after commit;
12. queue-add failure does not roll back activated credits;
13. startup repair finds durable blocked shops and recreates jobs after Redis loss;
14. periodic repair can recreate a lost hint without process restart;
15. inactive shop resume job is terminal no-op;
16. current checkout is revalidated before resumed send;
17. transient lookup failure retries rather than sending stale data;
18. still-exhausted resume stops after the first capacity denial;
19. oldest blocked recoveries are attempted first;
20. duplicate resume jobs do not duplicate provider send;
21. processing is bounded to the configured per-job batch;
22. no automatic paid-overage UsageEvent is created;
23. no new generic application logger or duplicate BullMQ telemetry mechanism is introduced.

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test:unit
npm run test:integration
npm run build
git diff --check
```

If integration tests require unavailable external infrastructure, follow the repository's integration harness/baseline policy and report the exact limitation rather than inventing a replacement validation command.

## Non-goals

Do not implement merchant React UI, Free-plan App Events cycle redesign, promotional grant/reservation primitives, refunds, upgrades/downgrades or Shopify subscription cancellation. Consume the promotional capacity primitive supplied by BACKGROUND-019.

## Stop conditions

STOP and return to `moda_architect` if:

- DATABASE-005 fields are unavailable;
- the integrated BACKGROUND-002 still contains a paid-overage path;
- current checkout revalidation cannot be reused without violating ARCH-001 lookup bounds;
- a proposed resume mechanism requires global serialization or unbounded scans;
- implementing resume would change the meaning of COMPLETED/recovered revenue for a checkout that received no recovery message.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.


## Final promotional capacity and restoration

Final exhaustion order is:

```text
Free: promotional -> purchased -> lifetime Free -> exhausted
Paid: selected promotional -> included -> purchased -> lifetime Free -> exhausted
```

The exhaustion epoch key must include promotional `grantedQuantity`, `committedQuantity` and `reservedQuantity` so a later promotional grant creates a genuinely new capacity epoch.

Merchant exhaustion copy must mention promotional credits when applicable without exposing internal campaign metadata.

A promotional grant can restore blocked recoveries. No direct Admin->Background queue is required: the existing PostgreSQL repair scan/re-admission path is correctness authority and must see the newly available promotional counter on its next pass.
