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
status: in_progress
priority: 53
executor: copilot
claimed_at: '2026-09-13T14:30:00Z'
attempt: 2
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

A lifetime-Free adjustment, promotional grant, merchant reactivation of a WITHDRAWN purchased-credit lot, or other capacity restoration does not need to enqueue directly. The repair scan below is the durable recovery mechanism. Do not couple the Shopify merchant app to this Background-internal queue solely for refund reactivation.

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
In Progress.

### Files Changed
- `moda-interact-background/src/domain/recovery-capacity-resume.ts`
- `moda-interact-background/src/services/recovery-capacity-resume.service.ts`
- `moda-interact-background/src/services/recovery-billing.service.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/src/services/recovery-credit-purchase.service.ts`
- `moda-interact-background/src/workers/recovery-capacity-resume.worker.ts`
- `moda-interact-background/src/entrypoints/recovery.ts`
- `moda-interact-background/tests/unit/services/recovery-billing.service.test.ts`

### Work Completed
- Changed full-capacity admission to the canonical `capacity-exhausted` result and retained the existing promotion/purchased/lifetime/included routing without paid overage.
- Persisted `RECOVERY_CAPACITY_EXHAUSTED` and the first block timestamp on DETECTED recoveries; successful MESSAGE_SENT transitions clear both fields.
- Added deterministic generic Free/Paid exhaustion epochs using durable subscription, billing-period, entitlement-counter, and pack facts.
- Added a Background-owned tenant-scoped BullMQ resume queue, deterministic IDs, bounded startup/periodic PostgreSQL repair, FIFO batches of 25, checkout locks, current Shopify revalidation, retryable provider errors, and terminal handling for unrecoverable checkouts.
- Added post-commit best-effort resume scheduling after confirmed purchased-credit activation; queue failures do not roll back activation.

### Validation Results
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- Focused billing suite: `npx vitest run tests/unit/services/recovery-billing.service.test.ts`, 45/45 passed.
- `npm run test:integration`: passed, 3/3 tests.
- `npm run test:unit`: 10 existing failures remain in purchased-credit reconciliation and runtime observability baseline tests; the purchased-credit failures are caused by the accepted database gitlink/client lacking fields and enum members already used by the pre-existing source (`PENDING_BILLING`, `NEEDS_ATTENTION`, refund counters), and the observability failures retain the pre-existing shared-runtime version assertion.
- `npm run build`: blocked by the same pre-existing accepted-gitlink Prisma/client drift; `git diff --check`: passed.

### Git / VCS
Implementation repository: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-009` on `task/ARCH-010-BACKGROUND-009`, pushed at commit `50bcda3`.
Parent repository: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-009` on `task/ARCH-010-BACKGROUND-009`, claim commit `9d0cbba` pushed.
Both canonical worktrees were created from current `origin/main`; no remote task branch existed before creation.

### Architect Review
Requested. Self-acceptance is not performed.


## Final promotional capacity and restoration

Final exhaustion order is:

```text
Free: promotional -> purchased -> lifetime Free -> exhausted
Paid: selected promotional -> included -> purchased -> lifetime Free -> exhausted
```

The exhaustion epoch key must include promotional `grantedQuantity`, `committedQuantity` and `reservedQuantity` so a later promotional grant creates a genuinely new capacity epoch.

Merchant exhaustion copy must mention promotional credits when applicable without exposing internal campaign metadata.

A promotional grant can restore blocked recoveries. No direct Admin->Background queue is required: the existing PostgreSQL repair scan/re-admission path is correctness authority and must see the newly available promotional counter on its next pass.

## Architect Review

### Review Status

Changes Requested

### Attempt 1 — Changes Requested

Attempt 1 is **not accepted**. Keep this same task and return it to `ready` for Attempt 2. Do not create a replacement task and do not begin `ARCH-010-BACKGROUND-007`, `ARCH-010-BACKGROUND-012`, `ARCH-010-SHOPIFY-008` or `ARCH-010-SYSTEM-TEST-001` from this task.

The following Attempt 1 implementation choices are directionally correct and should be preserved unless one of the required regression tests below proves a concrete defect:

- canonical `{ kind: "blocked", reason: "capacity-exhausted" }` for full capacity exhaustion;
- persistence of `RECOVERY_CAPACITY_EXHAUSTED` only on `DETECTED` recoveries and preservation of the first `admissionBlockedAt` through the `admissionBlockReason: null` CAS predicate;
- clearing block fields on successful `MESSAGE_SENT` transition;
- Background-owned `recovery-capacity-resume` BullMQ queue using the existing Redis/telemetry conventions;
- startup plus five-minute repair cadence and the 100-shop / 25-recovery bounds;
- FIFO recovery query order `detectedAt ASC, id ASC`;
- checkout-scoped locking and fresh `abandonedCheckoutLookupService` lookup before resumed initiation;
- post-transaction purchased-credit activation hint with queue failure isolated from the committed credit activation;
- no automatic paid-overage branch and no `BILLING_FREE_ALLOWANCE_EXHAUSTED` producer.

The corrections below are bounded to this task's original architecture. Do not redesign the billing model, add a cross-repository queue contract, or move resume ownership out of Background.

#### Correction 1 — the exhaustion epoch must include the selected promotional grant state

Files:

```text
moda-interact-background/src/services/recovery-billing.service.ts
moda-interact-background/tests/unit/services/recovery-billing.service.test.ts
```

`createCapacityExhaustedMessage()` currently builds its lifecycle key from plan/subscription, BillingPeriod, lifetime-Free, included and purchased state, plus the configured recovery-pack handle. It does **not** include the currently selected `PromotionalCreditGrant` identity/accounting state. This contradicts the task's explicit final promotional-capacity requirement and means a later promotion selection/restoration can return capacity and then exhaust again while deduplicating against the old SYSTEM-message epoch.

Extend the database view used by `RecoveryBillingService` so the exhaustion snapshot can read the shop's current `MerchantPromotionSelection` and selected `PromotionalCreditGrant`.

The deterministic lifecycle input must contain, when a selection/grant exists, at minimum:

```text
promotionalCreditGrant.id
promotionalCreditGrant.version
promotionalCreditGrant.quantity            # canonical granted quantity in this schema
promotionalCreditGrant.committedQuantity
promotionalCreditGrant.reservedQuantity
```

Use a deterministic sentinel such as `no-selected-promotion` when there is no selected grant. Do not use campaign copy, checkout/customer identity, phone numbers or any other customer data in the source key. `recoveryCreditPack.shopifyEventHandle` is configuration metadata and is **not** a substitute for promotional grant state.

Required regression coverage:

1. two blocked recoveries with the identical selected promotional grant snapshot deduplicate to one SYSTEM-message source key;
2. a different selected grant id creates a new exhaustion epoch;
3. a version/accounting change to the selected grant changes the exhaustion epoch;
4. the existing purchased/lifetime/included epoch assertions remain green.

#### Correction 2 — continuation after a full 25-row batch must not enqueue the currently-active BullMQ job id

Files:

```text
moda-interact-background/src/domain/recovery-capacity-resume.ts
moda-interact-background/src/services/recovery-capacity-resume.service.ts
moda-interact-background/src/workers/recovery-capacity-resume.worker.ts
```

The current worker does:

```ts
if (recoveries.length === MAX_RECOVERIES_PER_JOB) {
  await recoveryCapacityResumeService.schedule(job.data);
}
```

`job.data` produces the same deterministic job id as the job that is still executing. BullMQ can therefore deduplicate the attempted continuation against the active job; once the active job completes/removes, no successor remains. The worker also reaches this branch when the query returned 25 rows even if processing stopped on the first `capacity-exhausted` result.

Required behaviour:

- track how many selected rows were actually attempted and whether `capacity-exhausted` was returned;
- when any attempt returns `capacity-exhausted`, stop immediately **and do not enqueue a continuation**;
- when fewer than 25 rows were selected, do not enqueue a continuation;
- when all 25 selected rows were consumed without capacity exhaustion, enqueue one successor job with a **different but deterministic** bounded trigger/job id;
- the successor identity may use a bounded internal continuation marker derived from the last processed recovery id (for example `continuation-<lastRecoveryId>`), or an equivalent deterministic non-customer-data identity; it must not contain `:`;
- duplicate workers reaching the same continuation boundary must resolve to the same successor job id so BullMQ deduplication remains useful;
- do not loop over more than 25 recoveries in one job.

Do not solve this by disabling job-id deduplication or by globally serialising all shops.

Required worker tests:

1. 25 successful/terminal/ignored attempts with capacity still available enqueue one distinct successor;
2. a capacity-exhausted result on any row stops immediately and schedules no successor;
3. fewer than 25 selected rows schedule no successor;
4. duplicate continuation attempts produce the same deterministic successor id.

#### Correction 3 — ambiguous/bounded Shopify lookup outcomes are not terminal checkout evidence

File:

```text
moda-interact-background/src/services/checkout-recovery.service.ts
```

`resumeCapacityBlockedRecovery()` currently terminalizes every lookup outcome other than `found` or `provider-error`. That includes:

```text
ambiguous
bounded-limit-exceeded
```

Those outcomes do not prove that the abandoned checkout is no longer recoverable. They must not transition the durable recovery to `CANCELLED`.

Required classification:

```text
provider-error             -> throw; BullMQ retry policy applies
ambiguous                  -> throw/retry or otherwise return a retryable non-terminal failure
bounded-limit-exceeded     -> throw/retry or otherwise return a retryable non-terminal failure
found + completedAt != null -> terminalize without sending
not-found                  -> may terminalize using the existing lifecycle convention
found + still abandoned    -> continue through ordinary initiation
```

For every non-terminal lookup failure, preserve `DETECTED + RECOVERY_CAPACITY_EXHAUSTED`; never send from the stale stored checkout snapshot.

Add focused tests proving ambiguous/bounded/provider failure never writes a terminal status and never invokes the provider-send path.

#### Correction 4 — every task-owned terminal transition must clear stale capacity-block fields

File:

```text
moda-interact-background/src/services/checkout-recovery.service.ts
```

The new resume-specific `CANCELLED` transition clears `admissionBlockedAt` and `admissionBlockReason`, but the existing order-completion transition can move a capacity-blocked `DETECTED` recovery to `COMPLETED` while leaving both block fields populated.

When the order-completion transaction wins its status transition, clear:

```text
admissionBlockedAt = null
admissionBlockReason = null
```

in the same durable update. Inspect other terminal writes in this service that can consume a blocked `DETECTED` recovery and apply the same invariant where applicable. Do not change recovered-revenue semantics or invent a new status.

Required regression test: a `DETECTED + RECOVERY_CAPACITY_EXHAUSTED` recovery completed by the order path ends `COMPLETED` with both block fields null.

#### Correction 5 — add focused tests for the actual resume capability, not only the billing reason rename

Attempt 1 changes seven production files implementing a new durable queue/repair/resume mechanism, but the only changed test file is `tests/unit/services/recovery-billing.service.test.ts`. The passing 3-test integration suite is pre-existing purchased-reservation coverage and does not prove the new worker/repair/resume lifecycle.

Add focused tests using existing Vitest/module-mocking conventions. Prefer these files (names may vary only to match repository conventions):

```text
moda-interact-background/tests/unit/services/recovery-billing.service.test.ts
moda-interact-background/tests/unit/services/recovery-capacity-resume.service.test.ts
moda-interact-background/tests/unit/workers/recovery-capacity-resume.worker.test.ts
moda-interact-background/tests/unit/services/checkout-recovery.capacity-resume.test.ts
moda-interact-background/tests/unit/services/recovery-credit-purchase.service.test.ts
```

At minimum produce durable evidence for all of the following BG9-owned behaviours:

1. Free full exhaustion returns `capacity-exhausted`, creates no normal recovery UsageEvent/provider call and persists the generic block through the checkout service;
2. Paid full exhaustion has the same generic block with no overage UsageEvent;
3. purchased capacity is consumed before blocking;
4. block replay preserves the first `admissionBlockedAt`;
5. one Free epoch and one Paid epoch each deduplicate across multiple blocked recoveries;
6. purchased counter restoration and a new BillingPeriod produce new epoch identities;
7. selected promotional grant restoration produces a new epoch identity (Correction 1);
8. successful resumed initiation clears both block fields;
9. normal order completion clears both block fields (Correction 4);
10. purchased-credit activation schedules a resume hint **after** the reconciliation transaction returns successfully;
11. queue-add failure after purchase activation does not reject/roll back the already-successful reconciliation result;
12. repair selects only active shops with blocked DETECTED recoveries and never schedules more than 100 shops per pass;
13. a schedule failure for one repaired shop is non-fatal and does not prevent later shops from being attempted;
14. inactive-shop resume is a successful terminal no-op;
15. worker query is FIFO and bounded to 25;
16. fresh checkout lookup occurs before resumed initiation;
17. provider/ambiguous/bounded lookup failures are retryable/non-terminal (Correction 3);
18. still-exhausted resume stops the batch immediately and produces no continuation;
19. a full successful 25-row batch schedules exactly one distinct deterministic continuation (Correction 2);
20. duplicate resume delivery cannot produce duplicate initial send: prove the checkout lock/status guard and existing `recovery-message:<recoveryId>` idempotency path remain in force;
21. the startup repair and five-minute periodic repair are both wired to the recovery worker entrypoint;
22. no new generic logger or duplicate BullMQ telemetry mechanism is introduced;
23. no `BILLING_FREE_ALLOWANCE_EXHAUSTED` producer or paid-overage recovery branch is reintroduced.

Existing tests that already prove one of these points may be cited in the Completion Report instead of duplicated, but the report must name the exact test/file. Do not claim the pre-existing three integration tests validate the resume worker unless they actually exercise it.

#### Correction 6 — BACKGROUND-008 is Complete and merged to Background `main`; integrate it before any BG9 editing

`ARCH-010-BACKGROUND-008` is no longer a hypothetical overlap. It has been architect-accepted **Complete at Attempt 3** and its accepted implementation is now part of `moda-interact-background/main`.

Recorded accepted/mainline evidence:

```text
BACKGROUND-008 accepted implementation:
  b4ef7c885e03009f6622894230ab54a87bf4364a

moda-interact-background main merge containing BACKGROUND-008:
  a585139bb5f4c42d30ce0cc303f738f0c93c70b2
```

`BACKGROUND-009` Attempt 1 was created before this BG8 mainline merge. Therefore Attempt 2 MUST first bring current `origin/main` into the canonical BG9 implementation worktree and MUST implement BG9 **on top of** the accepted BG8 boundary-safety behavior.

Before changing any BG9 source file in the implementation worktree:

```bash
cd /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-009

git fetch origin
git status --short

# Synchronize the task branch with its own remote task branch first.
# If local/remote task history has diverged rather than being fast-forwardable, STOP.
git merge --ff-only origin/task/ARCH-010-BACKGROUND-009

# Then incorporate current Background main.
# A merge commit is allowed/expected because BG9 Attempt 1 and BG8 mainline diverged.
git merge --no-edit origin/main
```

Do not start implementation until that merge is complete.

After the merge, prove that accepted BG8 is in the implementation ancestry:

```bash
git merge-base --is-ancestor b4ef7c885e03009f6622894230ab54a87bf4364a HEAD
echo "BG8 accepted commit ancestor: $?"

git merge-base --is-ancestor a585139bb5f4c42d30ce0cc303f738f0c93c70b2 HEAD
echo "BG8 main merge ancestor: $?"
```

Both exit codes MUST be `0`. Record the actual current Background `origin/main` SHA in the Completion Report because `main` may advance beyond `a585139`.

The merged implementation must retain all accepted BG8 semantics, including at minimum:

```text
revalidateBeforeProvider(...) remains mandatory before irreversible WhatsApp provider work

fresh newRecoveriesPaused state wins at pre-provider revalidation

Paid BillingPeriod phases/reasons remain:
  ACTIVE
  DRAINING
  EXPIRED_RECONCILING
  billing-period-closing
  billing-period-reconciliation

DRAINING does not consume paid included capacity and retains:
  promotional -> purchased -> lifetime-Free fallback ordering

EXPIRED_RECONCILING releases pre-provider reservations and blocks provider work

period-specific paid-included source identity remains:
  paid-included:<billingPeriodId>:<recovery identity>

a still-reserved paid-included reservation can be released after its owning period closes

WhatsApp text/template sends retain the accepted 30-second bounded timeout

timeout/provider uncertainty remains ambiguous rather than definitive

blocked pre-provider revalidation performs no WhatsApp send and no successful billing commit
```

When applying BG9 changes to overlapping files, use these deterministic ownership rules.

**`src/services/recovery-billing.service.ts`**

- preserve the BG8/main version of `revalidateBeforeProvider()` and its pause/DRAINING/EXPIRED semantics;
- layer BG9's generic `capacity-exhausted` result, durable exhaustion epoch, and promotional-state epoch correction around the accepted BG8 admission/revalidation behavior;
- do not replace BG8's revalidation function with the older Attempt 1 BG9/pre-BG8 form;
- do not collapse `billing-period-closing` or `billing-period-reconciliation` into `capacity-exhausted`.

**`src/services/checkout-recovery.service.ts`**

- preserve BG8's unconditional billing revalidation immediately before provider send;
- if revalidation blocks, preserve the BG8 no-send/no-commit boundary;
- layer BG9's durable `RECOVERY_CAPACITY_EXHAUSTED` marking and resume lifecycle onto that flow;
- a BG9 capacity block must not create a bypass around BG8 revalidation.

**`src/services/paid-included-recovery-reservation.service.ts`**

- preserve the accepted BG8 `requireOpenReservationCounter()` behavior;
- preserve release of a still-reserved included reservation after its period closes;
- do not reintroduce a rule that prevents definitive release merely because the BillingPeriod is now closed.

**BG8 regression tests**

- retain the accepted BG8 tests;
- do not delete, weaken, rename away from execution, `.skip`, or rewrite them merely to satisfy BG9;
- BG9 tests may extend the same files, but all accepted BG8 boundary proofs must continue to pass.

If `git merge --no-edit origin/main` produces conflicts, resolve them only when the result can satisfy the ownership rules above without architectural guesswork. Do **not** use whole-file `--ours` or `--theirs` on the overlapping billing/checkout files.

If a conflict cannot be resolved while preserving the listed BG8 invariants and the bounded BG9 corrections, STOP and return the exact conflicted files/hunks to `moda_architect`. Do not implement an alternative billing boundary design inside BG9.
#### Correction 7 — record the mandatory Attempt 2 worktree/synchronisation evidence exactly

Attempt 1 used the correct-looking dedicated paths, but the Completion Report does not contain the complete mandatory physical-isolation/start-of-attempt evidence structure. Do not invent historical Attempt 1 evidence.

For Attempt 2, record actual observed results in this exact form:

```text
Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-009
  parent branch: task/ARCH-010-BACKGROUND-009
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-009
  implementation branch: task/ARCH-010-BACKGROUND-009
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Also record the actual initialized `database` submodule gitlink/HEAD and whether it changed.

Because BG8 is now merged to Background main, also record:

```text
BG8/main integration:
  Background origin/main SHA incorporated: <actual SHA>
  BG8 accepted commit b4ef7c885e03009f6622894230ab54a87bf4364a is ancestor of implementation HEAD: yes
  BG8 merge commit a585139bb5f4c42d30ce0cc303f738f0c93c70b2 is ancestor of implementation HEAD: yes
  BG8 preservation gate passed: yes
```

If either ancestry check is not `yes`, or canonical worktree restoration/synchronization cannot be performed cleanly, STOP under `docs/agent-worktree-isolation-policy.md`.

#### Correction 8 — Attempt 2 validation and baseline classification

From the canonical BG9 implementation worktree, initialize the recorded database submodule without changing its gitlink.

First run the **BG8 preservation gate** against the post-merge implementation. These tests are mandatory because BG8 is accepted mainline behavior and BG9 overlaps its billing/checkout surfaces:

```bash
npm run prisma:validate
npm run prisma:generate

npx vitest run \
  tests/unit/services/effective-billing-policy.service.test.ts \
  tests/unit/services/paid-included-recovery-reservation.service.test.ts \
  tests/unit/services/recovery-billing.service.test.ts \
  tests/unit/services/whatsapp.service.test.ts

npx vitest run \
  tests/unit/services/matured-candidate.materialization.test.ts \
  -t 'does not send or commit when billing revalidation blocks the admission'

npx vitest run \
  tests/unit/services/outbound-whatsapp-admission.service.test.ts \
  -t 'removes definitive failures but preserves ambiguous pending intent'
```

Every BG8 preservation-gate test above MUST pass. A failure in a BG8-owned boundary test is a BG9 regression and is not an acceptable repository baseline failure.

Then run the BG9 focused validation:

```bash
npx vitest run \
  tests/unit/services/recovery-billing.service.test.ts \
  tests/unit/services/recovery-capacity-resume.service.test.ts \
  tests/unit/workers/recovery-capacity-resume.worker.test.ts \
  tests/unit/services/checkout-recovery.capacity-resume.test.ts \
  tests/unit/services/recovery-credit-purchase.service.test.ts

npm run test:unit
npm run test:integration
npm run build
git diff --check
```
If one of the suggested new test filenames differs because the repository already has a better matching harness, use that harness and record the exact command. All BG9-owned focused tests must pass.

The known full-suite/build Prisma/client drift may remain non-green only if the Attempt 2 report demonstrates that the failing diagnostics are pre-existing/unrelated to BG9 and none originates from a BG9-touched source/test file. Do not modify unrelated purchased-refund or observability code merely to make this task green.

#### Attempt 2 allowed scope

Production changes are limited to the existing BG9 capability surfaces plus focused tests:

```text
src/domain/recovery-capacity-resume.ts
src/services/recovery-capacity-resume.service.ts
src/services/recovery-billing.service.ts
src/services/checkout-recovery.service.ts
src/services/recovery-credit-purchase.service.ts
src/workers/recovery-capacity-resume.worker.ts
src/entrypoints/recovery.ts
tests/unit/**               # BG9-focused tests only
this BACKGROUND-009 task file for execution metadata / Completion Report
```

Do not change Prisma schema/migrations, Shared contracts, Shopify/Admin/Messaging repositories, subscription/refund architecture, paid-overage policy, or another task file.

#### Attempt 2 stop conditions

STOP and return this same task to `moda_architect` without inventing a new design if:

1. the selected promotional grant snapshot required for the exhaustion epoch is not available at the recorded database gitlink;
2. a correct bounded continuation requires disabling BullMQ idempotency/deduplication globally;
3. preserving ambiguous/bounded checkout outcomes requires changing the cross-repository Shopify lookup contract;
4. current `origin/main` cannot be integrated while preserving the accepted BG8 invariants listed in Correction 6;
5. fixing BG9 requires schema/migration changes or another repository.

When the corrections, focused tests and required evidence are complete, set this same task to `review`, publish the implementation and parent report commits, then STOP for `moda_architect` review.

