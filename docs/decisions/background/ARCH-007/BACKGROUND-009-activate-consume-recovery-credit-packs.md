---
id: ARCH-007-BACKGROUND-009
architecture_id: ARCH-007
title: Activate billed recovery packs and consume purchased credits before overage
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: review
priority: 67
executor: copilot
claimed_at: 2026-09-08T15:49:11Z
attempt: 2
depends_on:
  - ARCH-007-DATABASE-005
  - ARCH-007-SHARED-006
  - ARCH-007-BACKGROUND-007
enables:
  - ARCH-007-SYSTEM-TEST-004
created: 2026-09-08
updated: 2026-09-08T16:53:30Z
---
# ARCH-007-BACKGROUND-009: Activate billed recovery packs and consume purchased credits before overage

## Exact capacity order

Implement exactly:

```text
FREE recovery:
  try FREE_RECOVERY_LIFETIME
  if available -> reserve/commit Free
  else try PURCHASED_RECOVERY_CREDITS
  if available -> reserve/commit purchased
  else -> deny new recovery

PAID_METERED recovery:
  determine normal recovery usage in current billing period
  if normal-meter usage < plan.includedRecoveryConversationAllowance:
      use existing paid metered path (Shopify sees the unit as included)
  else:
      try PURCHASED_RECOVERY_CREDITS
      if available:
          consume purchased credit
          do NOT report this recovery on normal recovery/overage meter
      else:
          use existing paid metered path (Shopify overage remains allowed)
```

Do not hard-stop paid merchants merely because included units are exhausted.

## Purchase activation

Add a bounded service/reconciliation path for `RecoveryCreditPurchase`.

State mapping:
```text
linked UsageEvent REPORTED
  -> activate purchase exactly once
  -> purchase ACTIVE
  -> activatedAt set
  -> PURCHASED_RECOVERY_CREDITS counter.grantedQuantity += creditsGranted

linked UsageEvent NEEDS_ATTENTION
  -> purchase NEEDS_ATTENTION
  -> grant 0 credits

linked UsageEvent PENDING/IN_FLIGHT/RETRYABLE
  -> purchase remains PENDING_BILLING
  -> grant 0 credits
```

If a NEEDS_ATTENTION UsageEvent is later retried and becomes REPORTED, activation may transition the purchase to ACTIVE exactly once.

Activation transaction must be idempotent. Reprocessing an ACTIVE purchase must not increment `grantedQuantity` again.

## Purchased-credit reservation service

Use existing Prisma transaction/CAS conventions from `FreeRecoveryReservationService`; do not copy raw SQL.

Counter:
```text
EntitlementCounter.PURCHASED_RECOVERY_CREDITS
```

Available:
```text
grantedQuantity - committedQuantity - reservedQuantity
```

Reservation lifecycle:
- reserve before provider send;
- definitive provider failure -> RELEASED and reservedQuantity decremented;
- ambiguous provider outcome -> AMBIGUOUS, still consumes safety capacity until reconciliation;
- provider accepted / recovery initiated -> COMMITTED; committedQuantity incremented, reserved decremented.

Commit creates one internal `RECOVERY_CONVERSATION +1` UsageEvent with:
```text
shopifyReportState = NOT_APPLICABLE
```
because the merchant already paid via the recovery-credit-pack billing event. Never also emit the normal paid recovery meter for that same top-up-covered recovery.

## Paid included-usage calculation

For top-up-enabled PAID_METERED plans only, calculate normal current-period recovery quantity from durable `UsageEvent` rows that:
- belong to current `billingPeriodId`;
- metric = `RECOVERY_CONVERSATION`;
- use the plan's normal `shopifyUsageEventHandle`;
- include positive/negative correction quantities so corrected billing identity is respected.

If included allowance/meter configuration is invalid, do not guess. Preserve the existing normal paid-metered path and do not consume purchased credits until configuration is safe.

## Credit persistence rules

Purchased credits:
- do not reset at billing period boundary;
- do not reset on plan upgrade/downgrade;
- do not reset on uninstall/reinstall of the same durable Shop;
- are consumed before paid overage once included units are exhausted;
- may have been bought on a different prior plan; they remain usable.

## Required tests

FREE:
1. free 5/5 + 0 purchased -> blocked.
2. free 5/5 + 1 purchased -> admitted and purchased balance becomes 0 after commit.
3. free allowance remaining -> Free is consumed before purchased credits.
4. purchased pack exhausted -> later newly activated pack restores capacity.

PAID:
5. included allowance 200, normal count 199, purchased >0 -> 200th uses normal meter, not purchased.
6. normal count 200, purchased >0 -> next recovery consumes purchased credit and no normal recovery meter event is reportable.
7. normal count 200, purchased 0 -> next recovery follows existing paid overage path.
8. after purchased credits exhaust, paid overage resumes.
9. after another pack activates, subsequent recovery can consume purchased credits again.

ACTIVATION/IDEMPOTENCY:
10. REPORTED purchase increments grantedQuantity exactly once under replay/concurrency.
11. PENDING/RETRYABLE does not grant.
12. NEEDS_ATTENTION does not grant.
13. later REPORTED after retry grants once.
14. duplicate recovery execution does not consume two purchased credits.
15. definitive vs ambiguous provider outcomes preserve reservation semantics.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Do not run `git commit` or `git push`.

## Completion Report

### Status
Review (Attempt 2)

### Files Changed
- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/src/services/effective-billing-policy.service.ts`
- `moda-interact-background/src/services/purchased-recovery-reservation.service.ts`
- `moda-interact-background/src/services/recovery-credit-purchase.service.ts`
- `moda-interact-background/src/services/recovery-billing.service.ts`
- `moda-interact-background/src/services/shopify-usage-event-publisher.service.ts`
- `moda-interact-background/tests/unit/services/purchased-recovery-reservation.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-credit-purchase.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-billing.service.test.ts`
- `moda-interact-background/tests/unit/runtime/observability-startup.test.ts`

### Work Completed
- Added durable purchased-credit reservation lifecycle with serializable transactions, CAS/version checks, idempotent replay, release, and ambiguous outcomes.
- Added billed recovery-pack activation and bounded reconciliation from linked UsageEvent state.
- Added Free and paid admission ordering so purchased credits are consumed before paid overage, while preserving the normal paid path for invalid configuration and exhausted purchased balance.
- Added publisher activation after successful `RECOVERY_CREDIT_PACK_PURCHASE` reporting.
- Updated the Shared runtime dependency to the accepted `0.8.0` contract.
- Corrected reconciliation to prioritize bounded terminal `REPORTED` and `NEEDS_ATTENTION` purchases ahead of older non-terminal billing events.
- Isolated post-report purchase activation failures from the Shopify provider retry/attention state machine; successfully reported UsageEvents remain `REPORTED`.
- Added Attempt 2 regressions for capacity restoration after pack activation, `RETRYABLE` zero-grant behavior, replay/concurrent activation idempotency, ambiguous reservation capacity, concurrent reservation CAS bounds, reconciliation starvation, and all publisher activation outcomes.

### Validation Results
- `npm run prisma:validate` passed.
- `npm run prisma:generate` passed.
- `npm run build` passed.
- Focused B009 suites passed: 37 tests across recovery billing, purchase activation, purchased reservation, and Shopify usage publisher services.
- Full unit suite: 366 passed, 7 skipped, 2 unrelated existing failures in pending recovery candidate behavior.
- `git diff --check` passed.

### Deviations
- Full suite retains two pre-existing failures in `pending-recovery-candidate.service.test.ts`; they are outside this task's scope.

### Assumptions
- The accepted `ARCH-007-SHARED-006` contract is consumed at version `0.8.0`.

### Unresolved Issues
- The two unrelated pending recovery candidate tests remain failing.

### Architectural Concerns
None.

### Attempt 2 Implementation
- Implementation commit: `68a16f0093beebc8469107403ebc46a8b3eb6076`
- Correction 1 files/tests: `src/services/recovery-credit-purchase.service.ts`, `tests/unit/services/recovery-credit-purchase.service.test.ts`.
- Correction 2 files/tests: `src/services/shopify-usage-event-publisher.service.ts`, `tests/unit/services/shopify-usage-event-publisher.service.test.ts`.
- Required reservation and admission regressions: `tests/unit/services/purchased-recovery-reservation.service.test.ts`, `tests/unit/services/recovery-billing.service.test.ts`.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implements the core recovery-credit model correctly, but two bounded
reliability defects and several explicit regression gaps remain.

The following Attempt 1 behavior is architecturally sound and must be preserved:

- exact Shared `0.8.0` dependency is installed;
- purchased credits use a durable `UsageReservation` lifecycle;
- reservation capacity is `grantedQuantity - committedQuantity - reservedQuantity`;
- reserve/commit/release use serializable transactions and counter-version CAS;
- purchased-credit commit creates exactly one internal
  `RECOVERY_CONVERSATION +1` with `shopifyReportState = NOT_APPLICABLE`;
- a purchased-covered recovery does not also create the normal paid Shopify
  recovery-meter event;
- Free attempts its lifetime allowance before purchased capacity;
- paid normal usage below the included allowance uses the normal paid path;
- once the included quantity is exhausted, purchased capacity is attempted
  before normal paid overage;
- exhausted purchased capacity falls back to normal paid overage rather than
  hard-stopping the merchant;
- REPORTED pack purchases transition to ACTIVE and grant credits transactionally;
- ACTIVE replay does not grant the same purchase again;
- NEEDS_ATTENTION grants zero;
- a later REPORTED state can activate a previously attention-state purchase;
- the accepted generic B007 Shopify UsageEvent publisher remains the reporting
  mechanism.

Two corrections are required in this SAME task.

---

### Correction 1 — terminal purchase reconciliation must not starve

Current `RecoveryCreditPurchaseService.reconcilePending()` selects the oldest
`PENDING_BILLING` / `NEEDS_ATTENTION` purchases regardless of the linked
UsageEvent state:

```text
old PENDING purchase 1
old PENDING purchase 2
...
old PENDING purchase 50
newer REPORTED purchase 51
```

With `limit = 50`, every recurring scan can select purchases 1..50 again,
observe that they are still non-terminal, and never reach purchase 51.

That violates the durable recovery requirement that an already-REPORTED pack
purchase cannot remain indefinitely unactivated after a process crash.

Required behavior:

1. Terminal linked UsageEvents MUST have reconciliation priority.
2. A bounded scan must discover non-ACTIVE purchases whose linked UsageEvent is:
   - `REPORTED`; or
   - `NEEDS_ATTENTION`.
3. A backlog of older `PENDING`, `IN_FLIGHT`, or `RETRYABLE` billing events must
   not prevent a later terminal purchase from being processed.
4. Preserve bounded scans; do not replace the limit with an unbounded read.
5. Preserve the state contract:
   - REPORTED -> ACTIVE exactly once + grant;
   - NEEDS_ATTENTION -> NEEDS_ATTENTION + zero grant.
6. If the implementation also normalises a purchase from NEEDS_ATTENTION back to
   PENDING_BILLING when its linked UsageEvent is explicitly retried, do that in
   a separate bounded path or otherwise ensure it cannot starve terminal
   activation work.

Required regression:

```text
more than <limit> older non-terminal purchases
+ one later REPORTED purchase
-> the REPORTED purchase is selected/activated in that reconciliation pass
```

Also prove that the reconciliation limit remains bounded.

---

### Correction 2 — post-report credit activation is not a provider failure

Current publisher flow effectively does:

```text
provider.createBillingEvent()
mark UsageEvent REPORTED
activate recovery-credit purchase

catch(any error)
  -> provider retry/needs-attention handling
```

If Shopify reporting succeeds and `activateForUsageEvent()` then throws, the
UsageEvent is already durably `REPORTED`.

That activation error MUST NOT enter the Shopify provider reporting failure
state machine.

Required behavior:

```text
Shopify report succeeds
-> UsageEvent REPORTED
-> direct purchase activation attempted

if direct activation fails:
   UsageEvent remains REPORTED
   do not mark RETRYABLE
   do not mark NEEDS_ATTENTION as a provider failure
   do not schedule another provider submission
   durable B009/B008 purchase reconciliation remains the recovery mechanism
```

The publisher may continue the scan or surface/log the activation problem, but
it must never reinterpret a successful Shopify billing event as an unreported
provider event.

Required regressions:

1. `RECOVERY_CREDIT_PACK_PURCHASE` REPORTED successfully -> activator called
   once with that UsageEvent id.
2. ordinary recovery metric -> purchase activator not called.
3. activator throws after `markReported` -> UsageEvent remains REPORTED and
   provider retry/attention mutation is not invoked.

---

### Required-test completion

Attempt 1 covers much of the 15-case contract but does not yet prove all of the
explicit cases.

Add focused deterministic coverage for at least the missing cases below:

1. exhausted purchased capacity followed by activation of another pack restores
   Free recovery capacity;
2. exhausted purchased capacity followed by another pack activation restores
   paid purchased-before-overage behavior;
3. `RETRYABLE` pack UsageEvent grants zero credits;
4. ambiguous purchased-provider outcome leaves the reservation consuming
   capacity and does not release it;
5. activation under concurrent/replayed execution grants one purchase exactly
   once;
6. concurrent purchased reservation cannot reserve beyond the granted balance;
7. the terminal-reconciliation starvation case above;
8. the three publisher/activation cases above.

Use the repository's existing disposable PostgreSQL integration harness for a
real concurrency assertion where it is already practical. If a unit CAS race
test is used for one layer, it must exercise the losing/retry path rather than
only sequential replay.

Do not broaden this correction into BACKGROUND-008, BACKGROUND-010, Admin,
Shopify UI, or database-schema redesign.

### Full-suite baseline

The reported full run retained the same two unrelated pending-recovery-candidate
failures already present outside this task slice. They are not a reason to
broaden B009.

Attempt 2 should continue to record them factually if they remain unchanged.

### Reviewed Files

- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/src/services/effective-billing-policy.service.ts`
- `moda-interact-background/src/services/purchased-recovery-reservation.service.ts`
- `moda-interact-background/src/services/recovery-credit-purchase.service.ts`
- `moda-interact-background/src/services/recovery-billing.service.ts`
- `moda-interact-background/src/services/shopify-usage-event-publisher.service.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/tests/unit/services/purchased-recovery-reservation.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-credit-purchase.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-billing.service.test.ts`
- `moda-interact-background/tests/unit/services/shopify-usage-event-publisher.service.test.ts`
- `docs/decisions/background/ARCH-007/BACKGROUND-009-activate-consume-recovery-credit-packs.md`

### Validation Reviewed

Repository-agent Completion Report records:

```text
Prisma validate/generate: passed
build: passed
focused tests: 52/52 passed
full suite: 326 passed, 2 unrelated existing failures
git diff --check: passed
```

Architect static review additionally verified:

- package manifest and lock resolve exact Shared `0.8.0`;
- purchased commit uses `NOT_APPLICABLE`;
- no normal paid UsageEvent is created by the purchased admission commit path;
- purchased reservation capacity is guarded by counter version CAS;
- activation transition and counter grant occur in one serializable transaction;
- B008 is explicitly designed to invoke the bounded B009 reconciliation path.

### Architecture Conformance

Changes required within this SAME task.

### Follow-up

Return this SAME task to `moda_background`.

Durable state:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next claim becomes **Attempt 2**.

Preserve the Attempt 1 implementation and correct only the reconciliation,
publisher activation error boundary, and missing focused regressions described
above.

Do not begin or modify BACKGROUND-010 as part of this correction.

Because BACKGROUND-010 has already been started separately in the developer's
live workspace, this review overlay intentionally does not update the Background
domain `_index.md` or parent architecture frontier from the older B009 review
snapshot. The current task YAML remains authoritative and the shared indexes
should be regenerated from live task state after the active B010 claim is
available.
