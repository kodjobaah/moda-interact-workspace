---
id: ARCH-007-BACKGROUND-009
architecture_id: ARCH-007
title: Activate billed recovery packs and consume purchased credits before overage
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 67
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-007-DATABASE-005
  - ARCH-007-SHARED-006
  - ARCH-007-BACKGROUND-007
enables:
  - ARCH-007-BACKGROUND-008
  - ARCH-007-SYSTEM-TEST-004
created: 2026-09-08
updated: 2026-09-08T20:02:00+01:00
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

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
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-BACKGROUND-009` branch and the mirrored parent-workspace `task/ARCH-007-BACKGROUND-009` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Ready for Review (Attempt 3)

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
- Attempt 3 selects `REPORTED` purchases before stable `NEEDS_ATTENTION` purchases, then fills the remaining bounded reconciliation capacity with attention and non-terminal states.
- Attempt 3 adds a deterministic reservation barrier proving both contenders read the same counter version, one loses the conditional CAS, retries in a new transaction, and observes exhausted capacity.

### Validation Results
- `npm run prisma:validate` passed.
- `npm run prisma:generate` passed.
- `npm run build` passed.
- Focused B009 suites passed: 37 tests across recovery billing, purchase activation, purchased reservation, and Shopify usage publisher services.
- Full unit suite: 368 passed, 7 skipped, 2 unrelated existing failures in pending recovery candidate behavior.
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

### Attempt 3 Implementation
- Implementation commit: `125f1a9`
- REPORTED-first bounded reconciliation: `src/services/recovery-credit-purchase.service.ts`, `tests/unit/services/recovery-credit-purchase.service.test.ts`.
- CAS-loss/retry concurrency proof: `tests/unit/services/purchased-recovery-reservation.service.test.ts`.

### Git / VCS

Task branch: `task/ARCH-007-BACKGROUND-009`

Implementation repository:
  repository: `moda-interact-background`
  commit: `125f1a9`
  remote branch: `origin/task/ARCH-007-BACKGROUND-009`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/background/ARCH-007/BACKGROUND-009-activate-consume-recovery-credit-packs.md`
  commit: `6644b41`
  remote branch: `origin/task/ARCH-007-BACKGROUND-009`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

#### Attempt 3 — Accepted

Attempt 3 is architect-accepted Complete.

The two remaining Attempt 2 corrections are implemented correctly:

1. Recovery-credit reconciliation now selects `REPORTED` purchases first
   within the bounded reconciliation limit, then spends only remaining capacity
   on `NEEDS_ATTENTION` and non-terminal billing states. Stable historical
   `NEEDS_ATTENTION` rows can therefore no longer starve a newer successfully
   billed purchase awaiting activation.

2. Purchased-credit reservation concurrency coverage now deterministically
   exercises the intended CAS-loss/retry path. Both contenders read the same
   pre-update counter state, exactly one conditional CAS loses, the loser
   retries in a new transaction, and the retry observes exhausted capacity.

The previously accepted B009 behaviour remains intact, including:

- Shopify-reported pack activation grants credits exactly once;
- activation failure after successful Shopify reporting cannot move the
  UsageEvent back into provider retry/attention handling;
- PENDING/RETRYABLE/NEEDS_ATTENTION billing states grant no credits;
- Free capacity is consumed before purchased capacity;
- purchased capacity is consumed before paid overage;
- definitive failures release purchased reservations;
- ambiguous provider outcomes retain reserved capacity;
- purchased credits remain durable across billing periods and plan changes.

Implementation reviewed at `125f1a9`.

No further implementation changes are required for ARCH-007-BACKGROUND-009.

### Review Status

Accepted

### Review Notes

#### Attempt 2 — Changes Requested

Attempt 2 correctly fixes both production defects identified in Attempt 1:

- post-REPORTED purchase activation failures are isolated from the Shopify
  provider retry/attention state machine; and
- reconciliation now prioritizes terminal UsageEvent states over older
  non-terminal PENDING / IN_FLIGHT / RETRYABLE rows.

Those corrections must be preserved. Two narrow issues remain before this task
can be architect-accepted.

##### Correction 1 — REPORTED activation must outrank stable NEEDS_ATTENTION

The Attempt 2 terminal query groups `REPORTED` and `NEEDS_ATTENTION` together
and orders them only by purchase `createdAt` / `id`. A bounded page of old
already-stable NEEDS_ATTENTION purchases can therefore continue to occupy the
entire reconciliation limit and indefinitely hide a newer REPORTED purchase.

Example with `limit = 50`:

```text
50 old purchases:
  purchase.status = NEEDS_ATTENTION
  usageEvent.shopifyReportState = NEEDS_ATTENTION

1 newer purchase:
  purchase.status = PENDING_BILLING
  usageEvent.shopifyReportState = REPORTED
```

The 50 old rows remain eligible on every pass, while the REPORTED purchase is
the state that actually requires durable credit activation.

Required Attempt 3 behavior:

1. Select REPORTED purchases first, within the same bounded reconciliation
   limit.
2. REPORTED must not be starved by older stable NEEDS_ATTENTION rows.
3. Preserve REPORTED -> ACTIVE exactly once + grant.
4. Preserve NEEDS_ATTENTION -> NEEDS_ATTENTION + zero grant.
5. Keep the total reconciliation work bounded.
6. Do not replace the bounded scan with an unbounded read.

A clean implementation may use separate bounded priority buckets, for example:

```text
1. REPORTED
2. actionable NEEDS_ATTENTION / normalization work
3. non-terminal normalization using remaining capacity
```

but the exact query shape is left to the Background agent provided the stated
invariant is met.

Required regression:

```text
more than <limit> old stable NEEDS_ATTENTION purchases
+ one later REPORTED purchase
-> the REPORTED purchase is selected/activated in that reconciliation pass
-> total selected work remains <= limit
```

##### Correction 2 — purchased-credit concurrency test must exercise CAS loss + retry

The Attempt 2 `Promise.all()` reservation unit test produces the correct final
count, but its shared mutable mock allows the second request to observe the
first request's updated counter before attempting its own version-CAS. It can
therefore return `credits-exhausted` without ever executing the intended losing
CAS path:

```text
updateMany(version = staleVersion) -> count 0
-> ReservationConcurrencyConflict
-> withRetry()
-> reread current counter
-> credits-exhausted
```

That means the production CAS design remains sound, but the explicit Attempt 1
review requirement has not yet been proven by the regression.

Required Attempt 3 test behavior:

- either use the repository's existing disposable PostgreSQL integration
  harness for the concurrency assertion; or
- use a deterministic unit barrier so two logical reservations both read the
  same original counter version/capacity before either CAS update proceeds.

The test must prove that one request loses the version-CAS, enters the retry
path, and then observes exhausted capacity. Assert the retry/conflict path
directly rather than inferring it only from the final balance.

The concurrent activation unit test may remain as replay/idempotency coverage,
but do not describe that shared-mock test as strong database concurrency proof
unless it similarly forces the competing conditional-update path.

##### Attempt 3 scope

Attempt 3 is limited to:

1. REPORTED-before-stable-NEEDS_ATTENTION reconciliation priority;
2. its bounded starvation regression;
3. a purchased-reservation concurrency regression that genuinely exercises
   CAS loss + retry; and
4. completion-report wording that accurately describes the concurrency proof.

Do not redesign purchased credits. Do not broaden into BACKGROUND-008,
BACKGROUND-010, BACKGROUND-011, Admin, Shopify UI, or database schema changes.
Preserve the accepted Attempt 2 publisher isolation and all previously sound
B009 behavior.

Current durable state after this review:

```text
status: ready
attempt: 2
executor: null
claimed_at: null
```

The next claim becomes **Attempt 3**.

#### Attempt 1 — Changes Requested (preserved)

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

Accepted. Attempt 3 resolves all requested B009 corrections and no further
implementation changes are required for this task.

### Follow-up

`ARCH-007-BACKGROUND-009` is Complete.

Dependency propagation:

- `ARCH-007-BACKGROUND-008` is now Ready because BACKGROUND-005,
  BACKGROUND-007, BACKGROUND-009 and SHOPIFY-001 are all
  architect-accepted Complete.
- `ARCH-007-SYSTEM-TEST-004` remains Pending / manual-gated because
  SHOPIFY-004, BACKGROUND-008 and ADMIN-005 are still incomplete.
- No system-test task is started automatically.

The implementation reviewed at `125f1a9` has already been merged into
`moda-interact-background` `main` through the developer-owned merge flow.
