---
id: ARCH-011-BACKGROUND-003
architecture_id: ARCH-011
title: Fence paid recovery admission and commit during provider-local plan mismatch
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-BACKGROUND-002
enables:
- ARCH-011-SYSTEM-TEST-001
created: 2026-09-14
updated: 2026-09-14
---
# ARCH-011-BACKGROUND-003

## Objective
Prevent creation of a normal paid-recovery Shopify UsageEvent against a stale plan meter while a provider-confirmed/ambiguous plan mismatch exists. Do not change proration/reconciliation logic.

## Authorized implementation surface
```text
src/services/paid-included-recovery-reservation.service.ts
src/services/recovery-billing.service.ts
tests/unit/services/paid-included-recovery-reservation.service.test.ts
tests/unit/services/recovery-billing.service.test.ts
tests/integration/paid-included-recovery-reservation.concurrency.integration.test.ts
```

## Exact fence
Inside the same Serializable transaction used by `PaidIncludedRecoveryReservationService.reserveInTransaction`, query whether this shop's subscription has an unresolved transition with status `PROVIDER_CONFIRMED` or `NEEDS_ATTENTION`. If yes, return new outcome `{kind:"plan-transition-in-flight"}` **before incrementing reservedQuantity or creating a reservation**.

Repeat the check inside `commitInTransaction` immediately before counter mutation/UsageEvent creation. If the reservation is still RESERVED and the fence is active, change only that reservation status to `AMBIGUOUS`; do not decrement reservedQuantity, increment committedQuantity or create UsageEvent. Return existing `ambiguous` outcome.

`REQUESTED` alone does not activate this fence.

Extend `RecoveryBillingService` blocked reason union with exact literal `plan-transition-in-flight`; map the new reserve outcome to that reason. `revalidateBeforeProvider` must also release/re-admit before provider when the fence is now active, so a newly fenced recovery does not proceed to the provider.

Do not retarget any existing UsageEvent handle.

## Tests
Prove: REQUESTED does not fence; PROVIDER_CONFIRMED and NEEDS_ATTENTION do; reserve fence writes nothing; pre-provider revalidation blocks; commit-time race marks reservation ambiguous and creates no UsageEvent; APPLIED/FAILED/SUPERSEDED clear fence; concurrent transition/reservation cannot create stale-meter event.

## Validation
```text
npm run prisma:validate
npm run prisma:generate
npx vitest run tests/unit/services/paid-included-recovery-reservation.service.test.ts tests/unit/services/recovery-billing.service.test.ts
npx vitest run tests/integration/paid-included-recovery-reservation.concurrency.integration.test.ts
npm test
npm run build
git diff --check
```

STOP if safe handling would require changing an already-created immutable UsageEvent's meter provenance.

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
