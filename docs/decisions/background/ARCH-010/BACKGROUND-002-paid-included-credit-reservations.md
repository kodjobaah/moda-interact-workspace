---
id: ARCH-010-BACKGROUND-002
architecture_id: ARCH-010
title: Enforce concurrency-safe paid included-credit admission
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 42
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-BACKGROUND-011
  - ARCH-010-DATABASE-002
  - ARCH-007-BACKGROUND-003
  - ARCH-007-BACKGROUND-009
enables:
  - ARCH-010-BACKGROUND-007
  - ARCH-010-BACKGROUND-008
  - ARCH-010-BACKGROUND-009
  - ARCH-010-BACKGROUND-019
  - ARCH-010-SHOPIFY-003
created: 2026-09-11
updated: 2026-09-12
---

# ARCH-010-BACKGROUND-002: Enforce concurrency-safe paid included-credit admission

## Objective

Replace the current aggregate-count decision at the paid included-credit boundary with a concurrency-safe period-scoped reservation primitive. **This task does not own final cross-bucket priority.** BACKGROUND-019 composes the final Paid admission order after campaign selection exists:

```text
selected promotional
-> current BillingPeriod included credits
-> purchased lifetime credits
-> shop-lifetime Free credits
-> recovery blocked
```

Included-credit-funded recoveries continue to emit the normal paid Shopify recovery meter. Promotional-, purchased- and shop-lifetime-Free-funded recoveries do not. There is no automatic paid overage branch in ARCH-010.

## Inspect before editing

```text
src/services/effective-billing-policy.service.ts
src/services/recovery-billing.service.ts
src/services/free-recovery-reservation.service.ts
src/services/purchased-recovery-reservation.service.ts
src/services/shopify-usage-event-publisher.service.ts
src/services/billing-reconciliation.service.ts
database/prisma/schema.prisma
package.json
```

Focused tests:

```text
tests/unit/services/effective-billing-policy.service.test.ts
tests/unit/services/recovery-billing.service.test.ts
tests/integration/free-recovery-reservation.concurrency.integration.test.ts
```

Add a new focused paid-period concurrency test using the repository's existing integration-test conventions if PostgreSQL integration infrastructure exists.

## Current behaviour to replace

Current `RecoveryBillingService.admit()` for `PAID_METERED` calls `tryPurchasedAdmission(..., paid=true)`. That function uses:

```text
normalRecoveryUsageQuantity < includedRecoveryConversationAllowance
```

to decide whether the merchant is still inside included capacity. This is based on aggregated committed usage and is not a reservation boundary, so concurrent workers can make the same stale decision.

Do not retain this aggregate check as the correctness mechanism.

## Required paid-period reservation service

Create a focused service following the existing Free reservation concurrency pattern, e.g.:

```text
src/services/paid-included-recovery-reservation.service.ts
```

Use the canonical Prisma model from `ARCH-010-DATABASE-002`.

The service must expose bounded operations equivalent to:

```text
reserve
commit
release
markAmbiguous
```

for one recovery quantity (default 1), keyed by a durable recovery identity that is **scoped to the exact BillingPeriod**. Use a deterministic form equivalent to `paid-included:<billingPeriodId>:<canonical recovery identity>` so the same recovery can be safely re-admitted in a later period after an old-period reservation is released. Keep the key bounded and free of customer-identifying data.

### Reserve

In a Prisma `Serializable` transaction with the existing bounded retry convention:

1. derive the period-scoped included sourceKey using the exact current BillingPeriod id;
2. replay an existing UsageReservation by that sourceKey before allocating again;
3. resolve the current effective billing policy inside the transaction;
4. require mapped active `PAID_METERED` state;
5. require an exact current OPEN BillingPeriod that has not expired;
6. load that period's unique `INCLUDED_RECOVERY_CREDITS` counter;
7. verify counter.shopId/period identity match the policy;
8. calculate `available = granted - committed - reserved - forfeited`;
9. if available < requested quantity, return `allowance-exhausted` without creating a reservation;
10. CAS the counter using `version`, increment `reservedQuantity`, increment version;
11. create UsageReservation pointing only to `billingPeriodEntitlementCounterId`.

Do not lazily invent the period counter here. First paid activation/period rollover owns counter creation. Missing counter is a billing configuration/projection error, not zero allowance.

### Commit

For a RESERVED period reservation:

1. CAS decrement period `reservedQuantity` and increment `committedQuantity`;
2. create the normal `RECOVERY_CONVERSATION +1` UsageEvent in the same transaction;
3. set `billingPeriodId` to the exact reservation/current period;
4. set `shopifyReportState = PENDING`;
5. set the current paid plan's normal `shopifyUsageEventHandle`;
6. set the deterministic Shopify idempotency key using the existing Shared helper;
7. link `UsageReservation.committedUsageEventId`;
8. mark reservation COMMITTED.

Replay must return the existing committed outcome and must not create a second UsageEvent.

### Release / ambiguous

Mirror the existing Free reservation semantics during an OPEN period:

- definitive pre-initiation/provider failure -> release capacity;
- ambiguous provider outcome -> reservation status AMBIGUOUS and leave the reserved quantity protected while the period remains open;
- committed reservations cannot be released.

`ARCH-010-BACKGROUND-007` owns the special **period-close** terminalization: remaining RESERVED/AMBIGUOUS period reservations are released with `releaseReason = PERIOD_CLOSED`, the held quantity is removed from `reservedQuantity`, and that unused capacity is forfeited. BACKGROUND-002 must not create a commit path that can commit against a CLOSED/expired BillingPeriod.

Do not decrement committed capacity after a successful provider initiation merely because Shopify usage publication later fails; publication is asynchronous/outbox behaviour.

## Effective policy changes

For `PAID_METERED`, policy resolution must fail closed when any required current-period fact is missing/inconsistent:

```text
Subscription.current/billingPeriod pointer missing
BillingPeriod.status != OPEN
BillingPeriod periodStart/end != Subscription currentPeriodStart/end
BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS) missing
counter quantities invalid
paid normal usage meter missing
```

Expose enough typed policy data for reservation code without performing a second non-transactional aggregate to determine included remaining capacity.

Remove `normalRecoveryUsageQuantity` as the correctness input for paid included->purchased routing. It may remain only if another read-only/reporting concern genuinely needs it; do not use it for admission.

## RecoveryBillingService integration boundary

Expose/use the paid-period reservation primitive so BACKGROUND-019 can compose it after promotional priority. Do **not** make this task permanently route Paid admission before promotional capacity.

When BACKGROUND-002 lands before BACKGROUND-019, preserve compatibility without introducing automatic overage; BACKGROUND-019 is the final top-level router and will call this primitive only after no selected usable promotion funded the recovery.

Commit semantics remain:

- paid-included: commit period reservation + normal paid meter UsageEvent;
- purchased/lifetime-free: owned by their respective downstream primitives and create no normal paid meter event;
- blocked capacity: no provider send and no UsageEvent.

Never create a new paid recovery UsageEvent with `billingPeriodId = null`.

## Idempotency and race cases

Required tests must prove at least:

1. first N concurrent paid recoveries cannot commit more than `grantedQuantity` to included capacity;
2. the period-included primitive returns exhausted without inventing overage;
3. BACKGROUND-019 can call this primitive after promotional capacity is unavailable;
4. final blocking is owned by the integrated BACKGROUND-019 routing and occurs only when promotional, included, purchased and lifetime Free capacity are all unavailable;
5. blocked exhaustion performs no provider send and creates no recovery UsageEvent;
6. included commit creates exactly one normal paid Shopify-meter UsageEvent;
7. purchased commit creates no normal paid recovery meter event;
8. duplicate reserve returns replay outcome without double reservation;
9. duplicate commit does not double increment or create a second UsageEvent;
10. definitive failure releases included reservation;
11. ambiguous failure preserves protected included capacity;
12. missing period counter fails closed rather than falling through to purchased or any overage path;
13. CLOSED or time-expired period fails closed;
14. mismatched Subscription/BillingPeriod boundaries fail closed;
15. paid recovery never creates `billingPeriodId = null`;
16. existing Free reservation tests remain unchanged/passing;
17. existing purchased-credit tests remain unchanged/passing;
18. same recovery identity in two different BillingPeriods derives two different included-reservation sourceKeys;
19. a reservation belonging to an expired/closed period cannot commit.

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test:unit
npm run build
git diff --check
```

Also run the new focused PostgreSQL concurrency test through the existing `npm run test:integration` harness if that harness supports the test without unrelated environment requirements. If not, document the exact repository baseline limitation; do not invent a replacement command.

## Non-goals

Do not implement first-plan callback UI, billing-period rollover, drain-window/pre-provider revalidation, plan upgrades/downgrades, promotional-credit reservation logic, top-up lot/refund changes, Shopify plan configuration or Admin UI. BACKGROUND-019 owns promotional insertion, BACKGROUND-008 owns drain-window/pre-provider behaviour and BACKGROUND-007 owns rollover.

## Stop conditions

STOP if:

- Prisma client does not contain the ARCH-010-DATABASE-002 period counter relation;
- implementing paid reservations would require raw `FOR UPDATE` rather than the accepted Serializable + CAS convention;
- current recovery workflow cannot distinguish successful provider initiation from pre-initiation failure using existing hooks;
- another integrated task has already changed the paid capacity ordering.

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


## Final promotional-capacity integration contract

BACKGROUND-002 still owns the first Paid current-period included reservation. After `ARCH-010-BACKGROUND-019` lands, the canonical downstream fallback is:

```text
promotional -> included -> purchased FIFO -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION
```

BACKGROUND-019 owns top-level routing and must preserve the **promotion-first** rule. The final integrated order is `promotional -> included -> purchased FIFO -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION`.
