---
id: ARCH-010-SHARED-007
architecture_id: ARCH-010
title: Remove superseded pre-production billing compatibility contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 6
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-010-SHARED-006
- ARCH-010-BACKGROUND-020
- ARCH-010-SHOPIFY-024
enables:
- ARCH-010-SHARED-008
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-SHARED-007: Remove superseded pre-production billing compatibility contracts

## Architecture

Read `docs/architecture/ARCH-010-first-production-baseline.md` and the ARCH-010 supersession map.

ARCH-010 is pre-production. Shared must publish only contracts that belong to the first-release architecture; it must not preserve ARCH-009 cancellation execution contracts merely because they were previously published.

## Objective

Remove Shared exports/system-message values whose only first-party purpose is superseded pre-production billing behaviour, including the local cancellation request/approval/`appSubscriptionCancel` workflow and the historical Free-only exhaustion code, while retaining the canonical ARCH-010 reconciliation, generic capacity-exhaustion and top-up-refund contracts.

## Context

ARCH-009 introduced a local cancellation execution contract including:

```text
SUBSCRIPTION_CANCELLATION_MODES
SubscriptionCancellationModeSchema
SubscriptionCancellationMode
ShopifySubscriptionCancellationArgs
SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS
BILLING_CANCELLATION_REQUEST_RECEIVED
BILLING_CANCELLATION_COMPLETED
BILLING_CANCELLATION_REJECTED
BILLING_FREE_ALLOWANCE_EXHAUSTED
```

ARCH-010 cancellation is Shopify-authoritative observation/reconciliation, and full-capacity exhaustion uses the generic `BILLING_RECOVERY_CAPACITY_EXHAUSTED` code for both Free and Paid. None of the listed compatibility contracts belongs to first production.

`BILLING_PLAN_CHANGE_ACTION_REQUIRED` was also introduced for the superseded local plan-change request workflow. Current ARCH-010 plan changes use Shopify-hosted App Pricing and do not use that message contract. Remove it unless inspection proves an active ARCH-010 consumer exists; if such a consumer exists, STOP and report the exact consumer rather than silently retaining ambiguous compatibility.

## Scope

Inspect the current package source, public billing entrypoint, schemas, exports and tests.

Remove the obsolete contracts above from their canonical registry/export locations and remove tests that require their presence.

Retain, unchanged in semantics:

```text
ARCH-010 subscription reconciliation queue contract
App Pricing drain constant
recovery-capacity-exhausted message contract
BILLING_REFUND_REQUEST_RECEIVED
BILLING_REFUND_COMPLETED
BILLING_REFUND_REJECTED
createMerchantBillingSystemSourceKey
PurchasedRecoveryCreditCounterSnapshot / availablePurchasedRecoveryCredits if still used
all unrelated messaging/observability contracts
```

## Out of Scope

Do not:

- publish the package;
- edit consumer repositories;
- rename retained ARCH-010 contracts;
- add compatibility aliases or deprecated re-exports;
- remove refund message codes used by ADMIN-002/003;
- change queue payload versions unrelated to cancellation cleanup.

## Requirements

1. obsolete cancellation mode/mapping exports are absent from source, declarations and built public entrypoint;
2. obsolete cancellation message values and `BILLING_FREE_ALLOWANCE_EXHAUSTED` are absent from the billing system-code schema;
3. `BILLING_PLAN_CHANGE_ACTION_REQUIRED` is absent unless an active ARCH-010 consumer is proven; if proven, STOP for architect review;
4. refund message codes remain exact and parseable;
5. subscription reconciliation and generic `BILLING_RECOVERY_CAPACITY_EXHAUSTED` contracts remain exact;
6. no deprecated alias/re-export preserves the removed names;
7. package version is **not** changed in this task; publication/versioning belongs to SHARED-008.

## Work Items

- [x] Inspect current billing public exports and exact consumers represented by repository tests.
- [x] Remove superseded cancellation mode/provider mapping exports.
- [x] Remove obsolete cancellation system-message values.
- [x] Remove `BILLING_FREE_ALLOWANCE_EXHAUSTED` and preserve the generic capacity-exhaustion code.
- [x] Remove superseded plan-change action-required code if no ARCH-010 consumer exists.
- [x] Update focused tests to assert retained ARCH-010 contracts and absence of removed exports.
- [x] Build declarations/public entrypoint and verify removed names are absent.

## Interfaces / Contracts

Retained first-release Shared billing contracts are the only public compatibility surface after SHARED-008 publication.

Removed names intentionally have no compatibility alias because this is a pre-production breaking cleanup.

## Dependencies

`ARCH-010-SHARED-006` is Complete and represents the published 0.10.0 baseline containing all accepted ARCH-010 refund contracts.

## Enables

`ARCH-010-SHARED-008` publishes the cleaned package.

## Acceptance Criteria

1. all five cancellation mode/provider mapping symbols listed in Context are absent;
2. all three cancellation system-message values and `BILLING_FREE_ALLOWANCE_EXHAUSTED` are absent;
3. no deprecated alias or alternate export recreates them;
4. `BILLING_PLAN_CHANGE_ACTION_REQUIRED` is removed unless an active ARCH-010 consumer forced a stop;
5. all three ARCH-010 refund codes remain exact;
6. reconciliation and generic capacity-exhausted contracts remain unchanged;
7. unit tests, typecheck, build and diff check pass;
8. built declarations/public billing entrypoint contain none of the removed symbols.

## Validation

Run repository-declared equivalents of:

```text
npm test
npm run typecheck
npm run build
git diff --check
```

Also inspect the built package/public declaration surface and prove the removed symbol names are absent.

## Implementation Notes

This is deliberately breaking cleanup before first production. Do not add deprecation wrappers.

## Completion Report

### Status

Attempt 2 complete; returned to architect review.

### Implementation

Changed implementation files:

```text
moda-interact-shared/src/billing.ts
moda-interact-shared/src/billing.test.ts
```

Implemented the original breaking pre-production cleanup after the architect-confirmed
consumer prerequisites became Complete.

Removed from the public Shared billing contract:

```text
SUBSCRIPTION_CANCELLATION_MODES
SubscriptionCancellationModeSchema
SubscriptionCancellationMode
ShopifySubscriptionCancellationArgs
SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS

BILLING_CANCELLATION_REQUEST_RECEIVED
BILLING_CANCELLATION_COMPLETED
BILLING_CANCELLATION_REJECTED
BILLING_FREE_ALLOWANCE_EXHAUSTED
BILLING_PLAN_CHANGE_ACTION_REQUIRED
```

No deprecated alias, compatibility export or alternate spelling was added.

Retained unchanged:

```text
BILLING_SUBSCRIPTION_RECONCILE_SCHEMA_VERSION
BILLING_SUBSCRIPTION_RECONCILE_QUEUE_NAME
BILLING_SUBSCRIPTION_RECONCILE_JOB_NAME
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
BILLING_RECOVERY_CAPACITY_EXHAUSTED
BILLING_REFUND_REQUEST_RECEIVED
BILLING_REFUND_COMPLETED
BILLING_REFUND_REJECTED
createMerchantBillingSystemSourceKey
PurchasedRecoveryCreditCounterSnapshot
availablePurchasedRecoveryCredits
unrelated messaging/observability contracts
```

Package version remains:

```text
0.10.0
```

Versioning/publication is owned by `ARCH-010-SHARED-008`.

### Consumer prerequisites

The breaking cleanup was executed only after architect acceptance of:

```text
ARCH-010-BACKGROUND-020   Complete
ARCH-010-SHOPIFY-024      Complete
```

Those accepted tasks established that first-party consumers of the retired contracts
were removed before Shared deleted the public names.

### Validation Results

Canonical implementation-worktree evidence:

```text
focused billing test:
  11 passed

full npm test:
  109 passed
  1 Redis-dependent test skipped because TEST_REDIS_URL was unset

npm run typecheck:
  passed

npm run build:
  passed

npm run validate:billing-entrypoint:
  passed

built runtime/declaration removed-symbol scan:
  clear

git diff --check:
  passed
```

The billing public-entrypoint validator checks the built billing runtime/declaration
targets and packed export targets. The removed-symbol scan reported none of the retired
names in the built public artifact.

Architect inspection of the portable review archive independently confirms:

```text
all retired exports are absent from src/billing.ts
all retired registry values are absent from BILLING_SYSTEM_MESSAGE_CODES
all retired schema values are rejected by billing.test.ts
retained reconciliation/capacity/refund/purchased-credit contracts remain present
package version is still 0.10.0
```

The portable archive does not include installed dependencies or `dist/`, so the
canonical-worktree build/entrypoint/symbol-scan evidence is used for those generated
artifact checks.

### Git / VCS

Canonical worktrees recorded by the submitted task:

```text
parent:
  /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHARED-007
  branch: task/ARCH-010-SHARED-007

implementation:
  /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHARED-007
  branch: task/ARCH-010-SHARED-007
```

The missing parent worktree from the blocked attempt was restored before final review.
The implementation worktree was preserved.

Recorded synchronization/publication evidence:

```text
parent synchronization merge:
  4612ee8

implementation commit:
  f26ebad

latest submitted parent task/report commit:
  914c385
```

Both task branches are reported pushed and clean.

Main branches:

```text
modified: no
```

Database/submodule gitlink:

```text
changed: no
staged: no
```

### Deviations

One Redis-dependent test was skipped because `TEST_REDIS_URL` was unset. This does not
exercise the billing contract removed by this task and is not a blocker.

### Unresolved Issues

None within SHARED-007.

## Architect Review

### Attempt 1 — Blocked

Attempt 1 correctly stopped because first-party Background and Shopify consumers still
depended on contracts SHARED-007 was required to remove.

The architect resolved the rollout cycle by introducing:

```text
ARCH-010-BACKGROUND-020
ARCH-010-SHOPIFY-024
```

and requiring both to complete against published Shared `0.10.0` before SHARED-007
could retry.

No Shared implementation from the blocked probe was accepted.

### Attempt 2 — Accepted

Architect review confirms the consumer sequencing prerequisites are Complete and the
Attempt-2 implementation now satisfies the original SHARED-007 contract.

Architect comparison against the blocked Attempt-1 package snapshot shows that the only
Shared source changes are:

```text
src/billing.ts
  remove the five cancellation mode/provider exports
  remove Free-only exhaustion, local plan-change action-required and three local
  cancellation message values from the canonical registry/schema

src/billing.test.ts
  remove obsolete positive cancellation-contract assertions
  assert the retired registry/schema values are absent/rejected
```

No unrelated Shared source file changed in the portable snapshot comparison.

Acceptance invariants:

```text
1. cancellation mode/provider exports absent
2. cancellation message values absent
3. BILLING_FREE_ALLOWANCE_EXHAUSTED absent
4. BILLING_PLAN_CHANGE_ACTION_REQUIRED absent
5. no deprecated alias/re-export
6. reconciliation queue contract retained
7. APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS retained
8. BILLING_RECOVERY_CAPACITY_EXHAUSTED retained
9. all three refund message contracts retained and parseable
10. purchased-credit helpers retained
11. package version remains 0.10.0
12. built public runtime/declarations reported clean
```

The restored dedicated parent worktree resolves the workflow issue encountered during
the retry. The submitted final task heads are:

```text
parent:
  914c385

implementation:
  f26ebad
```

**Architect decision: Accepted — Attempt 2.**

Because `completion_mode: automatic`, `ARCH-010-SHARED-007` is now `complete`.
`attempt: 2` is preserved and the active executor/claim is cleared.

### Dependency Reconciliation

`ARCH-010-SHARED-008` depends only on SHARED-007.

SHARED-007 is now architect-accepted Complete, so SHARED-008 transitions:

```text
pending -> ready
```

SHARED-008 remains a **publication-only** task. It must publish the already-accepted
clean contract as `0.11.0`; it must not redesign or revalidate SHARED-007 implementation
semantics.
