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
executor: null
claimed_at: null
attempt: 1
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

This task assumes `ARCH-015-SHOPIFY-004` has already made new merchant purchase/refund admissions single-flight on the same provider meter. Background still MUST defend against pre-existing/inconsistent rows and scheduler concurrency; it may not merely trust the web invariant.

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

The accepted SHOPIFY-004 invariant is:

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

Implementation commit: `1f7cd30` on `task/ARCH-015-BACKGROUND-004`, pushed to `origin`.

Changed files:

- `src/services/recovery-credit-refund-correction.service.ts`
- `tests/unit/services/recovery-credit-refund-correction.service.test.ts`

Implemented the per-invocation collision-safe provider-meter visitation rule, deterministic oldest-live refund and unresolved-purchase gate, `createdAt` selection, and exact frozen BEFORE/EXPECTED AFTER/provider-conflict classification. Existing PREPARE transaction/CAS, idempotency keys, immutable evidence, linked-refund reconciliation, and generic publisher behavior remain unchanged. No schema or cross-repository files were modified.

Focused validation: `npm test -- --run tests/unit/services/recovery-credit-refund-correction.service.test.ts` passed, 19 tests.

Schema validation: `npm run prisma:validate` passed.

Build: `npm run build` passed.

Diff hygiene: `git diff --check` passed.

Full suite: `npm test` ran 78 files, with 67 passed, 10 skipped, and 1 failed file containing 4 failed tests. The unchanged unrelated failures are the four tests in `tests/integration/translation-enum-bindings.integration.test.ts`; each fails because `Background runtime configuration has not started` before its database assertion in the translation services. No refund-correction tests failed.

Limitations: no blockers identified for this task. The full-suite translation runtime baseline remains unresolved and is outside this task's authorized implementation surface.
