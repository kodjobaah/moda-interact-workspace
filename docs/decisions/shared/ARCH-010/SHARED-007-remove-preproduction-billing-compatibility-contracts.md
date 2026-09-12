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
status: ready
priority: 6
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SHARED-006
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

- [ ] Inspect current billing public exports and exact consumers represented by repository tests.
- [ ] Remove superseded cancellation mode/provider mapping exports.
- [ ] Remove obsolete cancellation system-message values.
- [ ] Remove `BILLING_FREE_ALLOWANCE_EXHAUSTED` and preserve the generic capacity-exhaustion code.
- [ ] Remove superseded plan-change action-required code if no ARCH-010 consumer exists.
- [ ] Update focused tests to assert retained ARCH-010 contracts and absence of removed exports.
- [ ] Build declarations/public entrypoint and verify removed names are absent.

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
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Deviations
None.

### Assumptions
No production consumer requires ARCH-009 local cancellation contracts.

### Unresolved Issues
None at task definition time.

### Architectural Concerns
Stop if an active ARCH-010 consumer of `BILLING_PLAN_CHANGE_ACTION_REQUIRED` or the cancellation exports is found.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

## Architect Review

### Review Status
Pending

### Review Notes
Pending implementation.

### Reviewed Files
None yet.

### Validation Reviewed
None yet.

### Architecture Conformance
Pending.

### Follow-up
None yet.
