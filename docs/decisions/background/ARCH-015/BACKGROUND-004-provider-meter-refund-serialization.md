---
id: ARCH-015-BACKGROUND-004
architecture_id: ARCH-015
title: Serialize automatic refund corrections per provider meter and classify provider conflicts
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 86
attempt: 2
depends_on:
- ARCH-015-BACKGROUND-003
enables:
- ARCH-015-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-015-BACKGROUND-004

## Objective

Defensively enforce the same `(shopId,eventHandle)` monetary-mutation invariant inside Background and distinguish three provider reconciliation states after an automatic correction has been reported:

```text
provider == frozen BEFORE state
    => Shopify has not caught up yet; remain REQUESTED

provider == frozen EXPECTED AFTER state
    => automatic correction proven; complete refund

provider == neither BEFORE nor EXPECTED AFTER
    => conflicting provider evidence; NEEDS_ATTENTION
```

This task is coordinated with `ARCH-015-SHOPIFY-004`, but the two implementation tasks may execute concurrently. SHOPIFY-004 hardens merchant admission while BACKGROUND-004 independently defends against pre-existing/inconsistent rows and scheduler concurrency. Neither task is an execution prerequisite of the other; terminal integrated acceptance requires both to be architect-accepted Complete.

No Prisma schema change is authorized.

## Authorized implementation surface

```text
src/services/recovery-credit-refund-correction.service.ts
tests/unit/services/recovery-credit-refund-correction.service.test.ts
# only directly affected billing entrypoint/result typing if the compiler proves necessary
```

Do NOT modify the Shopify app, Database, Shared, Admin, or generic App Event publisher unless the task hits a STOP condition and returns to Architect.

---

# Phase 1 — process at most one REQUESTED refund per meter per scheduler pass

`processDue()` already reads REQUESTED refunds ordered by:

```ts
[{ createdAt: "asc" }, { id: "asc" }]
```

Preserve that ordering.

Add a per-invocation set:

```ts
const visitedMeters = new Set<string>();
```

Use this exact collision-safe key function:

```ts
function refundMeterKey(refund: Pick<RefundRow, "shopId" | "eventHandleSnapshot">): string {
  return JSON.stringify([refund.shopId, refund.eventHandleSnapshot]);
}
```

At the beginning of the loop:

```ts
const meterKey = refundMeterKey(refund);
if (visitedMeters.has(meterKey)) continue;
visitedMeters.add(meterKey);
```

Result: one scheduler pass may process at most one REQUESTED refund for a given meter, but may process different handles for the same shop.

Do not mark skipped same-handle rows failed/attention merely because another same-handle row was selected first.

---

# Phase 2 — defensive oldest-live-refund gate before PREPARE

Add `createdAt: true` to `refundSelect` because deterministic older-row comparison is required.

Define the same live statuses locally:

```ts
const LIVE_RECOVERY_CREDIT_REFUND_STATUSES = [
  RecoveryCreditRefundStatus.REQUESTED,
  RecoveryCreditRefundStatus.PROVIDER_ACTION_REQUIRED,
  RecoveryCreditRefundStatus.NEEDS_ATTENTION,
] as const;
```

Before `readProof(refund)` inside `prepare()`, call a new helper:

```ts
private async hasEarlierLiveMeterMutation(refund: RefundRow): Promise<boolean>
```

It MUST check BOTH:

### A. Earlier live refund on same meter

```ts
const earlierRefund = await this.database.recoveryCreditRefund.findFirst({
  where: {
    shopId: refund.shopId,
    eventHandleSnapshot: refund.eventHandleSnapshot,
    status: { in: [...LIVE_RECOVERY_CREDIT_REFUND_STATUSES] },
    id: { not: refund.id },
    OR: [
      { createdAt: { lt: refund.createdAt } },
      {
        createdAt: refund.createdAt,
        id: { lt: refund.id },
      },
    ],
  },
  orderBy: [{ createdAt: "asc" }, { id: "asc" }],
  select: { id: true },
});
```

### B. unresolved purchase on same meter

```ts
const unresolvedPurchase = await this.database.recoveryCreditPurchase.findFirst({
  where: {
    shopId: refund.shopId,
    status: RecoveryCreditPurchaseStatus.REQUESTED,
    shopifyEventHandleSnapshot: refund.eventHandleSnapshot,
  },
  orderBy: [{ createdAt: "asc" }, { id: "asc" }],
  select: { id: true },
});
```

Return true if either exists.

At the very start of `prepare()`:

```ts
if (await this.hasEarlierLiveMeterMutation(refund)) {
  return "reconciled";
}
```

Here `"reconciled"` retains the service's existing meaning of "no terminal change this pass". Do not create a new Prisma status merely to label deferral.

### Why only EARLIER refunds block

If invalid historical data already contains two REQUESTED same-handle refunds, querying "any other refund" would deadlock both. The deterministic rule is oldest `(createdAt,id)` first. Later rows wait until every earlier live refund on that meter becomes terminal.

An unresolved REQUESTED purchase blocks regardless of creation time because its `+1` provider mutation has not yet been reconciled.

---

# Phase 3 — preserve immutable PREPARE evidence

Do not alter the accepted BACKGROUND-003 PREPARE transaction semantics:

```text
read safe provider proof
-> calculate negative/fractional correction
-> create/upsert exact correction UsageEvent
-> atomically freeze typed RecoveryCreditRefund before/expected-after evidence
-> link automaticCorrectionUsageEventId
```

Do not recompute frozen correction evidence after the link exists.

Do not change the deterministic idempotency keys:

```text
recovery-credit-refund:${refund.id}
Shopify idempotency derived from that source id
```

Do not move correction submission into this service; the existing generic App Event publisher remains submission owner.

---

# Phase 4 — classify REPORTED provider state exactly

Current code incorrectly does:

```ts
if (actual !== expectedAfter) return "reconciled";
```

Replace this with explicit before/after/conflict classification.

After:

```ts
if (event.shopifyReportState !== ShopifyReportState.REPORTED) return "reconciled";
```

and after a safe `readProviderState(refund)`, use EXACTLY the frozen fields already on `RecoveryCreditRefund`.

Required code shape:

```ts
const sameCurrency = proof.currency === refund.expectedProviderCurrency;

const matchesBefore =
  sameCurrency &&
  proof.quantity.equals(refund.providerUsageQuantityBeforeCorrection!) &&
  proof.cost.equals(refund.providerUsageCostBeforeCorrection!);

const matchesExpectedAfter =
  sameCurrency &&
  proof.quantity.equals(refund.expectedProviderUsageQuantityAfterCorrection!) &&
  proof.cost.equals(refund.expectedProviderUsageCostAfterCorrection!);

if (matchesExpectedAfter) {
  const completed = await this.complete(refund, proof.cost, proof.currency);
  return completed ? "completed" : "reconciled";
}

if (matchesBefore) {
  return "reconciled";
}

await this.markNeedsAttention(
  refund,
  "automatic-correction-provider-state-conflict",
);
return "needs-attention";
```

Do not use tolerances. Prisma Decimal comparisons are exact.

Do not treat a currency mismatch as "provider has not caught up". A safe provider response with the wrong currency is conflicting evidence and MUST become `NEEDS_ATTENTION`.

`readProviderState()` failures that are already classified unsafe retain the accepted BACKGROUND-003 behavior; this task does not redesign provider outage policy.

---

# Phase 5 — cancellation/reactivation race expectations

Do not modify Shopify code here.

The cross-task SHOPIFY-004 invariant, to be verified again during integrated/manual testing, is:

```text
automaticCorrectionUsageEventId != null
=> merchant reactivation unavailable
```

Background MUST preserve its existing PREPARE atomicity:

- correction `UsageEvent` creation and refund link occur in one DB transaction;
- if the refund-link CAS loses because merchant cancellation committed first, `PrepareRaceError` rolls the transaction back, so there is no orphan PENDING correction event;
- if Background linked first, Shopify reactivation's `automaticCorrectionUsageEventId: null` CAS loses.

Add tests proving this cross-task contract from the Background side. Do not weaken `PrepareRaceError` behavior.

---

# Phase 6 — no generic publisher rewrite

Do NOT change `shopify-usage-event-publisher.service.ts` merely to filter CANCELLED refunds.

After SHOPIFY-004 + existing PREPARE atomicity, a valid automatic correction event can only exist after the refund has been durably linked and merchant reactivation is permanently blocked.

If a test proves the generic publisher can still submit an automatic correction whose linked refund was legitimately transitioned to `CANCELLED` through an accepted code path, STOP and return that evidence to `moda_architect`; do not invent a publisher/refund join in this task.

---

# Required tests — exact scenarios

File:

```text
tests/unit/services/recovery-credit-refund-correction.service.test.ts
```

Add/adjust tests for all of the following.

## Meter serialization

1. two REQUESTED refunds same `(shopId,eventHandle)`, same scheduler page:
   - only oldest `(createdAt,id)` attempts PREPARE;
   - second is skipped for this pass;
   - only one correction `UsageEvent` is created;
2. same shop, different handles:
   - both may PREPARE in one pass;
3. earlier `PROVIDER_ACTION_REQUIRED` refund same handle:
   - newer REQUESTED refund remains REQUESTED and creates no correction;
4. earlier `NEEDS_ATTENTION` refund same handle:
   - newer REQUESTED refund remains REQUESTED and creates no correction;
5. unresolved REQUESTED purchase same handle:
   - refund remains REQUESTED, no correction;
6. unresolved REQUESTED purchase different handle:
   - refund may PREPARE;
7. once older same-handle refund becomes terminal, next scheduler invocation can prepare the next refund using a fresh provider baseline.

## Reconciliation classifier

For a linked correction event in `REPORTED`:

8. provider exactly equals frozen BEFORE quantity/cost/currency:
   - refund stays REQUESTED;
   - no entitlement decrement;
   - outcome `reconciled`;
9. provider exactly equals EXPECTED AFTER quantity/cost/currency:
   - existing atomic completion runs;
   - refund COMPLETED;
   - purchase REFUNDED;
10. provider quantity is a third value:
    - NEEDS_ATTENTION with reason `automatic-correction-provider-state-conflict`;
11. provider cost is a third value:
    - NEEDS_ATTENTION;
12. safe provider response currency differs:
    - NEEDS_ATTENTION;
13. fractional example:

```text
before quantity       4.00
correction           -0.25
expected after        3.75
actual                3.50
```

must become NEEDS_ATTENTION, never remain silently REQUESTED.

## PREPARE/cancellation race

14. PREPARE creates event then refund-link CAS returns 0:
    - transaction throws `PrepareRaceError`;
    - correction event is rolled back/not persisted;
15. refund already has correction link:
    - `prepare()` is not called by `processDue()`; reconciliation path is used.

## Regression

16. all accepted BACKGROUND-003 cases remain green:
    - safe full -1;
    - safe fractional negative event;
    - 202/reporting state alone does not complete;
    - provider-action fallback occurs only before automatic event creation;
    - automatic completion writes existing REFUND_COMPLETED system message;
    - typed evidence remains immutable on retries.

---

# Required validation commands

From `moda-interact-background`:

```bash
npm test -- --run tests/unit/services/recovery-credit-refund-correction.service.test.ts
npm run prisma:validate
npm run build
git diff --check
```

Then:

```bash
npm test
```

If the full suite has pre-existing unrelated failures, record exact unchanged baseline failures and ensure the focused refund-correction suite is completely green.

---

# Forbidden implementations

Do NOT:

- add a schema field/model/status;
- add a second worker/queue;
- serialize different event handles;
- recompute frozen correction evidence on retries;
- let a newer same-handle refund overtake an older live refund;
- classify a third provider state as ordinary propagation delay;
- use floating-point epsilon comparisons;
- change the generic publisher without hitting the explicit STOP condition;
- modify merchant/Admin UI in this task.

# Stop conditions

STOP and return to `moda_architect` if:

- safe serialization requires a new persistent lock model;
- an accepted code path can CANCEL a refund after a linked automatic correction despite SHOPIFY-004;
- provider reconciliation needs evidence not already stored by DATABASE-002;
- generic publisher changes become necessary;
- the provider returns a pricing/state shape that cannot be classified using exact frozen Decimal evidence.

# Completion protocol

1. Update Completion Report with exact commits/files/tests.
2. Set `status: review`.
3. Clear claim metadata.
4. Return to `moda_architect`.
5. STOP. Do not start SYSTEM-TEST-001.

## Completion Report

Status: Ready for Review

Implementation commit: `d270d92` on `task/ARCH-015-BACKGROUND-004`, pushed to `origin`.

Prior accepted implementation retained: `1f7cd30`.

Changed files in attempt 2:

- `tests/unit/services/recovery-credit-refund-correction.service.test.ts`

Attempt 2 added deterministic regression coverage for unresolved purchases on a different handle, terminal older-refund unblocking with a fresh provider baseline, explicit 4.00 / -0.25 / 3.75 versus 3.50 fractional conflict classification, staged correction rollback when the refund-link CAS loses, linked reconciliation without PREPARE or UsageEvent recreation, and immutable fractional PREPARE evidence across retries. No production source, schema, queue/status/lock model, generic publisher, or cross-repository files were modified.

Validation:

- `npm run test -- tests/unit/services/recovery-credit-refund-correction.service.test.ts`: passed, 24 tests.
- `npm run test -- tests/unit/services/shopify-usage-event-publisher.service.test.ts`: passed, 15 tests.
- `npm run test -- tests/unit/providers/shopify-app-events.provider.test.ts`: passed, 20 tests.
- `npm run prisma:validate`: passed.
- `npm run build`: passed.
- `npm run test:unit`: passed, 66 files and 1,019 tests.
- `git diff --check`: passed.
- `npm test`: 67 files passed, 10 skipped, and 1 failed file with 4 failures. The unchanged unrelated failures are the four tests in `tests/integration/translation-enum-bindings.integration.test.ts`, each failing with `Background runtime configuration has not started` before its translation database assertion. No refund-correction tests failed.

Limitations: no task blocker identified. The full-suite translation runtime baseline remains unresolved and is outside this task's authorized implementation surface. SYSTEM-TEST-001 was not started. Parent report publication commit: `a3c22986b2d6e95c6441b128f9b98ba96905c320`.

## Architect Review — Attempt 1 — Changes Requested

Verdict: **Changes Requested — test-only correction; production implementation accepted in substance.**

The implementation commit `1f7cd30` correctly adds the bounded Background protections required by this task: per-invocation collision-safe `(shopId,eventHandle)` visitation, deterministic earlier-live-refund and unresolved-purchase gating, exact frozen BEFORE / EXPECTED AFTER / conflict classification, and no schema / queue / publisher redesign. Do not redesign `recovery-credit-refund-correction.service.ts` unless one of the required regressions below proves a production defect.

`ARCH-015-SHOPIFY-004` and `ARCH-015-BACKGROUND-004` are **parallel correction tasks**. BACKGROUND-004 does not wait for SHOPIFY-004 to execute. The Background tests can prove PREPARE rollback/link behavior from the Background side independently; the cross-repository interaction is verified later by manual/integrated testing once both tasks are Complete.

Attempt 2 is limited to `tests/unit/services/recovery-credit-refund-correction.service.test.ts` unless a new test demonstrates a real production defect. Add deterministic coverage for the required scenarios that Attempt 1 did not yet prove:

```text
1. unresolved REQUESTED purchase on a different event handle does not block PREPARE;
2. after an older same-handle refund becomes terminal, the next scheduler invocation prepares the next refund using a fresh provider baseline;
3. explicit fractional conflict: BEFORE 4.00, correction -0.25, EXPECTED AFTER 3.75, actual 3.50 => NEEDS_ATTENTION with automatic-correction-provider-state-conflict;
4. PREPARE refund-link CAS loss proves transactional rollback of the staged correction event (no committed/publishable orphan);
5. an already-linked correction routes through reconciliation and does not call PREPARE / UsageEvent upsert again;
6. safe fractional PREPARE freezes exact Decimal evidence and a subsequent linked retry does not recreate the event or rewrite frozen evidence.
```

Preserve the already-green scenarios for same-meter oldest-first processing, different-handle independence, earlier `PROVIDER_ACTION_REQUIRED` / `NEEDS_ATTENTION` deferral, same-handle unresolved-purchase deferral, exact BEFORE propagation, exact EXPECTED AFTER completion, third quantity/cost/currency conflicts, full -1 correction, 202-not-complete semantics, provider-action fallback-before-event, REFUND_COMPLETED system message, immutable evidence, and PREPARE race behavior.

Re-run exactly:

```bash
npm test -- --run tests/unit/services/recovery-credit-refund-correction.service.test.ts
npm run prisma:validate
npm run build
git diff --check
npm test
```

The four existing translation-runtime failures may remain documented as unrelated baseline failures if unchanged. Do not modify translation runtime, schema, generic publisher, Shopify/Admin UI, or another repository to make this task green.

Lifecycle after this review:

```text
ARCH-015-SHOPIFY-004      Ready / may execute independently
ARCH-015-BACKGROUND-004   Ready at Attempt 1 -> next claim becomes Attempt 2
ARCH-015-SYSTEM-TEST-001  Pending until both correction tasks are Complete and manual-test authorization is given
```
