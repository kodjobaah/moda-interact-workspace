---
id: ARCH-018-SYSTEM-TEST-001
architecture_id: ARCH-018
title: Validate promotion selection lock, expiry cleanup and shared reconciliation cadence
task_kind: system_test
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: manual
status: pending
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-018-SHOPIFY-001
- ARCH-018-BACKGROUND-001
- ARCH-018-ADMIN-001
enables: []
created: 2026-09-20
updated: 2026-09-20
---

# ARCH-018-SYSTEM-TEST-001

## Terminal/manual gate

Do **not** auto-start.

The developer starts this task only after ARCH-018 implementation tasks are architect-accepted, integrated, deployed/testable as required, and manually smoke-tested.

No non-system-test task depends on this task.

## Objective

Prove the integrated ARCH-018 merchant promotion-selection lifecycle across Merchant UI/server selection, Background expiry cleanup and Admin reconciliation controls.

## Required scenarios

### 1. Selection lock before expiry

Create/select campaign A with future `expiresAt`.

Prove:

```text
A selected
campaign B visible if otherwise eligible
B action disabled in UI
server attempt to select B is rejected
same-campaign replay is rejected
```

### 2. Exhaustion does not unlock

Consume all A promotional credits before expiry.

Prove:

```text
remaining = 0 / exhausted
A remains selection-locked
B remains blocked
UI explains selection remains until expiry
```

### 3. Manual close does not unlock

Close A before `expiresAt`.

Prove:

```text
A may disappear from eligible-offer catalogue
current-selection notice still identifies/represents the locked selection
B remains blocked
```

### 4. Target loss does not unlock

Use a PLAN-targeted A, select it, then move the merchant to a different plan while A is unexpired.

Prove A is no longer spendable/target-eligible but the merchant cannot select B until A expires.

### 5. Expiry unlocks immediately before cleanup

Set A `expiresAt <= now` while its `MerchantPromotionSelection` pointer still exists.

Without first running Background cleanup, select eligible B.

Prove:

```text
selection succeeds immediately
pointer now references B
A PromotionalCreditGrant/history remains
```

### 6. Background cleanup preserves history

Create an expired selection pointer and run one billing reconciliation cycle/promotion cleanup stage.

Prove:

```text
MerchantPromotionSelection deleted
PromotionalCreditGrant retained
quantity/reserved/committed/selection timestamps/count unchanged
history remains queryable
```

### 7. Cleanup cannot delete newer B

Prove the compare/delete race contract using real PostgreSQL/concurrent operations or the repository's approved deterministic integration harness:

```text
cleanup candidate observes expired A
merchant changes pointer to unexpired B
stale cleanup final delete affects zero rows
B remains selected
```

### 8. Admin expiry extension defeats stale cleanup

Candidate observes expired A, then Admin extends A expiry beyond the cleanup cutoff before final delete.

Prove final delete affects zero rows and the pointer remains.

### 9. Shared reconciliation timer

Using the existing Admin Runtime Controls, change **Reconciliation interval** in the approved test environment.

Prove the Background billing worker continues to use:

```text
lease = BILLING_RECONCILIATION
same runtime config version for billing and promotion cleanup
billingReconciliationIntervalSeconds controls cycle cadence
```

Do not introduce or configure a separate promotion timer.

### 10. Batch bound

Create more expired selections than `billingReconciliationShopBatchSize`.

Prove one cycle releases no more than the configured batch and later cycles drain the remainder.

### 11. Double-submit

On `/app/promotions`, trigger rapid repeated submission for A and rapid A/B selection attempts.

Prove:

```text
UI blocks duplicate in-flight interaction
server persists one winning selection mutation
selectionCount/timestamps are not double-incremented by the blocked replay
```

### 12. Reopened/reselected historical grant

After A expiry and pointer release, later make A eligible/running again according to existing campaign lifecycle support.

Select A again and prove:

```text
same PromotionalCreditGrant reused
no quantity replenishment
consumed credits remain consumed
exhausted historical grant remains exhausted
```

## Admin presentation

Verify Admin displays exactly:

```text
Reconciliation interval
How often Moda performs periodic billing and entitlement reconciliation, including Shopify billing checks and expired promotion cleanup.
```

and does not expose a separate promotion reconciliation control.

## Out of scope

- changing campaign targeting/quantity semantics;
- live external Shopify billing calls beyond what existing test environment already requires;
- new database schema;
- performance/load benchmarking.

## Validation

Use the repository-declared integrated/system-test commands and environment conventions. Record exact application/background/admin revisions and test environment.

Run:

```text
git diff --check
```

Do not substitute mock-only evidence for the required stale-cleanup race if the system-test harness provides real PostgreSQL concurrency.

## Stop conditions

STOP if any implementation dependency is not accepted/integrated, if the environment cannot exercise the required DB race safely, or if the Admin runtime control cannot be changed in the selected test environment without affecting unrelated production resources.

## Completion protocol

Return the task to `review` with exact scenario evidence; STOP. Architect acceptance is required to mark ARCH-018 Implemented.

## Completion Report

### Status

Not started — terminal/manual-gated.
