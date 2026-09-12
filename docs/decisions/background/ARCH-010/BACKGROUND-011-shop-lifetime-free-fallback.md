---
id: ARCH-010-BACKGROUND-011
architecture_id: ARCH-010
title: Make the lifetime Free recovery entitlement plan-independent and consume it after purchased credits
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 41
executor: copilot
claimed_at: '2026-09-12T16:55:26Z'
attempt: 2
depends_on:
- ARCH-010-DATABASE-013
- ARCH-007-BACKGROUND-003
- ARCH-007-BACKGROUND-009
enables:
- ARCH-010-BACKGROUND-002
- ARCH-010-BACKGROUND-009
- ARCH-010-BACKGROUND-014
- ARCH-010-BACKGROUND-019
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-BACKGROUND-011: Make the lifetime Free recovery entitlement plan-independent and consume it after purchased credits

## Objective

Change recovery admission so `LIFETIME_FREE_RECOVERY_CREDITS` is a shop-lifetime fallback available under both Free and Paid subscriptions, while purchased lifetime top-ups are intentionally consumed before that lifetime Free grant.

This task implements the **purchased → shop-lifetime Free** fallback primitive. `ARCH-010-BACKGROUND-019` later inserts promotional credits ahead of purchased capacity, so the final ARCH-010 order is:

```text
FREE
  promotional credits
  -> purchased lifetime credits
  -> shop-lifetime Free credits
  -> BLOCK NEW RECOVERY ADMISSION

PAID
  promotional credits
  -> paid period included credits
  -> purchased lifetime credits
  -> shop-lifetime Free credits
  -> BLOCK NEW RECOVERY ADMISSION
```

This task owns only the plan-independent lifetime-Free primitive and the purchased→lifetime fallback. It must not implement promotional accounting itself; `ARCH-010-BACKGROUND-019` owns the promotional layer and composes it ahead of this helper.

## Inspect before editing

```text
src/services/effective-billing-policy.service.ts
src/services/free-recovery-reservation.service.ts
src/services/purchased-recovery-reservation.service.ts
src/services/recovery-billing.service.ts
src/services/checkout-recovery.service.ts
tests/unit/services/effective-billing-policy.service.test.ts
tests/unit/services/free-recovery-reservation.service.test.ts
tests/unit/services/recovery-billing.service.test.ts
tests/integration/free-recovery-reservation.concurrency.integration.test.ts
database/prisma/schema.prisma
package.json
```

Read the implemented ARCH-007 purchased-credit reservation path before editing. Do not duplicate its CAS/transaction logic.

## 1. Lifetime Free policy must be plan-independent

The current development implementation may still derive Free allowance from plan-owned or adjustment compatibility state. DATABASE-013 removes that schema. Delete those reads rather than adapting them.

For every active mapped subscription plan (Free or Paid), load exactly:

```text
ShopEntitlementCounter(counter = LIFETIME_FREE_RECOVERY_CREDITS)
```

The effective shop-lifetime state is derived only from that durable shop counter:

```text
grant = counter.grantedQuantity
remaining = max(grant - committedQuantity - reservedQuantity, 0)
```

There is no `BillingPlan.freeLifetimeConversationAllowance`, no `BillingAllowanceAdjustment` query and no signed compatibility arithmetic in first production.

For an active/onboarded shop, a missing lifetime counter after DATABASE-013 is a configuration/data-integrity error. Fail closed; do not silently create a fresh grant during ordinary recovery admission.

## 2. Keep the existing service/file names unless a rename is mechanically required

`free-recovery-reservation.service.ts` is an accepted ARCH-007 implementation. To keep this Luna task bounded, do not perform a broad rename solely for terminology.

Change its eligibility semantics:

- remove the rule that rejects Paid plans as `not-free`;
- require an active mapped subscription and active Shop through the effective policy;
- reserve/commit/release the shop-lifetime counter regardless of current plan kind;
- preserve the existing serializable/CAS concurrency guarantees;
- lifetime-Free commit remains `ShopifyReportState.NOT_APPLICABLE` and MUST NOT create a Shopify App Event.

If the current public outcome type contains `not-free`, remove it only if all repository references/tests can be updated within this task. Do not leave Paid lifetime fallback impossible merely to preserve that outcome.

## 3. Free-plan recovery order

Change Free recovery admission from the legacy order to exactly:

```text
try purchased reservation
  -> reserved: fund from PURCHASED_RECOVERY_CREDITS
  -> exhausted: try lifetime Free reservation
       -> reserved: fund from LIFETIME_FREE_RECOVERY_CREDITS
       -> exhausted: capacity-exhausted
```

Purchased credits MUST be attempted first even when lifetime Free credits remain.

Do not reserve both buckets for one recovery.

## 4. Commit/release ownership

The admission result must retain enough source information that the provider-send path commits/releases exactly the bucket that was reserved.

Required:

```text
purchased source
  -> existing purchased reservation commit/release

lifetime-free source
  -> existing lifetime Free counter reservation commit/release
```

Do not switch funding source after the provider call has begun.

## 5. Refund consequence is intentional

Purchased credits are refundable only while unused under the later refund lifecycle. Because purchased credits are consumed before lifetime Free credits, a recovery intentionally reduces purchased refundable quantity first.

Do not reverse the order to maximise refundability.

## Required regression coverage

At minimum prove:

1. Free + purchased available + lifetime Free available reserves purchased;
2. Free + purchased exhausted + lifetime Free available reserves lifetime Free;
3. Free + both exhausted returns capacity-exhausted;
4. Paid plan can reserve lifetime Free through the plan-independent lifetime service;
5. lifetime Free reservation remains concurrency-safe;
6. lifetime Free commit creates no Shopify-reportable App Event;
7. purchased commit remains unchanged;
8. replay does not reserve a second bucket;
9. failure/release returns quantity to the same reserved bucket;
10. no plan-owned lifetime allowance field is read;
11. platform-policy changes after grant do not alter an existing shop's counter grant;
12. no signed lifetime-Free adjustment query or compatibility arithmetic exists;
13. missing lifetime counter on active onboarded shop fails closed;
14. inactive/uninstalled shop remains blocked by existing shop-availability rules.

Run focused tests plus repository-declared build/typecheck/test validation required by the task. Preserve unrelated documented baseline failures.

## Non-goals

Do not:

- implement paid period included-credit reservation (BACKGROUND-002);
- implement top-up purchase billing;
- implement refunds;
- implement the promotional-credit bucket in this task (`ARCH-010-BACKGROUND-019` owns that layer);
- change Shopify plans;
- reset/regrant lifetime Free credits;
- modify another repository.

## Stop conditions

Stop and return to `moda_architect` if:

- DATABASE-013 schema/client is unavailable;
- purchased reservation semantics differ materially from the inspected ARCH-007 design;
- the required routing would need cross-repository contract changes;
- preserving the existing reservation idempotency/source-key rules is not possible.

## Completion Report

### Status
Ready for Review

### Files Changed
- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/checkout-recovery.service.ts`
- `src/services/effective-billing-policy.service.ts`
- `src/services/free-recovery-reservation.service.ts`
- `src/services/recovery-billing.service.ts`
- `tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
- `tests/unit/services/effective-billing-policy.service.test.ts`
- `tests/unit/services/free-recovery-reservation.service.test.ts`
- `tests/unit/services/recovery-billing.service.test.ts`

### Work Completed
Implemented the DATABASE-013-backed, plan-independent lifetime Free fallback.
The effective policy now reads only the durable
`LIFETIME_FREE_RECOVERY_CREDITS` counter and fails closed when that counter is
missing. Legacy plan-owned lifetime allowance reads, signed adjustment queries,
and `FREE_RECOVERY_LIFETIME` compatibility identifiers were removed from the
touched path.

Free admission now attempts purchased credits before lifetime Free credits, and
Paid admission uses lifetime Free after included and purchased capacity are
exhausted. Admission source identity is preserved so commit, release, and
ambiguous provider outcomes operate on the exact reserved bucket. Lifetime Free
commit remains `NOT_APPLICABLE` and does not create a Shopify-reportable App
Event. Reconciliation now provisions the renamed lifetime counter for new Free
subscriptions without changing an existing grant.

Required regressions cover purchased-first ordering, lifetime fallback and
exhaustion, Paid fallback, concurrency, replay, same-bucket release/commit,
missing-counter fail-closed behavior, plan-independent grants, and inactive or
uninstalled shop blocking.

### Validation Results
Focused tests:
`npm test -- --run tests/unit/services/effective-billing-policy.service.test.ts tests/unit/services/free-recovery-reservation.service.test.ts tests/unit/services/recovery-billing.service.test.ts tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
passed: 3 files, 42 tests; the integration file was skipped because its
database guard requires explicit disposable-test flags.

Guarded PostgreSQL concurrency test:
`TEST_DATABASE_URL='postgresql://postgres:postgres@localhost:5432/moda_interact' MODA_DISPOSABLE_INTEGRATION=1 npm test -- --run tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
passed: 1 file, 1 test.

Prisma generation succeeded through `npm run build` with the hydrated
DATABASE-013 schema/client. The repository build remains non-zero under the
documented `TYPECHECK-001` baseline: no current-task files produce errors, but
the pre-existing purchased-reservation nullability errors and recovery-credit
purchase/refund schema-consumer errors remain.

Repository unit validation via `npm run test:unit` remains non-zero: 44 files
passed and 3 files failed, with 488 tests passed and 41 failed. The failures
are in the unrelated recovery-credit purchase/refund consumers and observability
startup baseline, not in the focused ARCH-010-BACKGROUND-011 tests.

`git diff --check` passed. The database submodule remains an unstaged gitlink at
`014408e0402221f08a3961880b34e828a8bdc736` and was not modified or committed.

### Deviations
Repository-wide build and unit validation retain documented/unrelated baseline
failures described above. The focused task validation is green.

### Assumptions
The hydrated DATABASE-013 database submodule and generated Prisma client are
the accepted prerequisite baseline supplied for this attempt.

### Unresolved Issues
Repository-wide recovery-credit purchase/refund consumers still require the
DATABASE-013 follow-up work owned outside this task. Those errors do not affect
the changed lifetime Free path.

### Architectural Concerns
None. No cross-repository contract, schema, transaction, or idempotency
boundary was changed.

### Git / VCS
Task branch: `task/ARCH-010-BACKGROUND-011`

Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-011
  parent branch: task/ARCH-010-BACKGROUND-011
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-011
  implementation branch: task/ARCH-010-BACKGROUND-011
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Implementation repository:
  repository: moda-interact-background
  implementation commit: a6b7dd3 (feat: add plan-independent lifetime free fallback)
  remote branch: origin/task/ARCH-010-BACKGROUND-011
  pushed: yes

Parent workspace:
  task file: docs/decisions/background/ARCH-010/BACKGROUND-011-shop-lifetime-free-fallback.md
  claim commit: 0ae28f0
  report commit: pending final parent task-branch commit
  remote branch: origin/task/ARCH-010-BACKGROUND-011
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architect Review
Pending.
