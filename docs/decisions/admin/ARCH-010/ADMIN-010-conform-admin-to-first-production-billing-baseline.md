---
id: ARCH-010-ADMIN-010
architecture_id: ARCH-010
title: Conform Admin billing controls to the clean first-production baseline
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 8
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHARED-008
- ARCH-010-ADMIN-001
enables:
- ARCH-010-ADMIN-002
- ARCH-010-ADMIN-004
- ARCH-010-ADMIN-008
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-ADMIN-010: Conform Admin billing controls to the clean first-production baseline

## Architecture

Read first:

```text
docs/architecture/ARCH-010-first-production-baseline.md
docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md
docs/architecture/ARCH-010-promotional-campaigns.md
```

ARCH-010 is the first-production baseline. `ARCH-010-ADMIN-001` remains immutable accepted history; this task removes compatibility behaviour that ADMIN-001 intentionally retained while the schema was still incremental.

## Objective

Make `moda-interact-admin` compile and behave exclusively against the clean ARCH-010 database/shared baseline, with no runtime dependency on removed development-era billing fields, enums, cancellation state, or direct promotional grants.

## Context

ADMIN-001 correctly moved lifetime-Free configuration to `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance`, but it deliberately retained legacy audit/read compatibility for `BillingPlan.freeLifetimeConversationAllowance` because the old schema still existed at that point.

DATABASE-013 removes that legacy schema. SHARED-008 publishes the clean cross-service contract. The Admin repository must therefore stop reading, serialising, validating, presenting, or testing removed compatibility state.

## Scope

Inspect the current Admin repository before editing, especially:

```text
src/app/(protected)/billing/**
src/app/actions/billing-*.ts
src/components/admin/billing-*.tsx
src/lib/admin/billing*.ts
src/lib/admin/*promotion*.ts
src/lib/admin/*refund*.ts
src/lib/admin/types.ts
tests/security/*billing*.test.mjs
tests/security/*promotion*.test.mjs
```

Also search the repository for every removed baseline symbol named in Requirements below. Modify only files required to remove those dependencies and preserve accepted ARCH-010 Admin behaviour.

## Out of Scope

Do not:

- redesign the Admin billing UI;
- implement ADMIN-002/003 refund workflow;
- implement ADMIN-004/005/006 promotion workflow;
- implement ADMIN-007/008/009 upgrade-economics workflow;
- mutate database schema;
- reintroduce compatibility aliases;
- add merchant-facing routes;
- reopen or edit the accepted ADMIN-001 task history.

## Requirements

### 1. Lifetime-Free Admin state uses only the platform policy and shop counter

The current authority is:

```text
PlatformBillingPolicy.lifetimeFreeRecoveryAllowance
ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)
```

Remove all Admin runtime/type/test dependencies on:

```text
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment
FREE_RECOVERY_LIFETIME
FREE_ALLOWANCE_ADJUSTED
```

Do not preserve those fields in audit snapshot serializers merely because old development rows once contained them. There is no first-production compatibility requirement.

The accepted platform-policy control and its `PLATFORM_POLICY_CHANGED` audit behaviour remain.

### 2. Remove local subscription-cancellation compatibility

Search for and remove Admin code/contracts/UI/tests whose only purpose is the removed local cancellation state machine:

```text
SubscriptionCancellationRequest
SubscriptionCancellationMode
SubscriptionCancellationStatus
BILLING_CANCELLATION_REQUEST_RECEIVED
BILLING_CANCELLATION_COMPLETED
BILLING_CANCELLATION_REJECTED
```

Do not replace them with another local approval/request workflow. Provider subscription lifecycle/reconciliation remains the authority.

If no such Admin code exists, record the negative search evidence and make no speculative changes.

### 3. Promotions are campaign-linked only

Remove any Admin path that can create or present a campaign-less/direct `PromotionalCreditGrant` as a first-release action.

Admin promotion implementation after this task must assume:

```text
PromotionalCreditGrant.campaignId is required
exact grant lot is promotional capacity authority
no ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)
no direct-grant compatibility provenance
```

Do not implement the still-pending campaign-management tasks in this correction task.

### 4. Refund Admin types match the human provider-settlement baseline

Remove any compile/runtime/test dependency on:

```text
RecoveryCreditPurchaseStatus.REFUNDED
RecoveryCreditRefundSettlementMode
CURRENT_CYCLE_APP_EVENT_CORRECTION
negative App Event correction UsageEvent fields
```

The pending refund Admin tasks will build on DATABASE-013's human `REFUND | CREDIT` settlement model. Do not implement their workflow here.

### 5. Upgrade-economics schema availability

DATABASE-013 incorporates the valid schema requirements that were previously assigned to superseded DATABASE-012. This task does not implement upgrade-economics UI, but Admin Prisma/types must compile cleanly against that final baseline so ADMIN-008 can proceed later without a second compatibility layer.

### 6. No substitute compatibility layer

Do not create:

- local duplicate enums for removed Prisma values;
- optional `any`/fallback properties for removed fields;
- raw SQL using removed enum literals;
- migration-era adapters;
- fake campaign identities for old direct grants.

If accepted Admin business behaviour genuinely cannot be represented by DATABASE-013/SHARED-008, STOP and report the exact contract gap to `moda_architect`.

## Work Items

- [ ] Verify DATABASE-013 and SHARED-008 are Complete and installed/resolved by the task worktree.
- [ ] Search for every removed baseline symbol listed in this task.
- [ ] Remove lifetime-Free legacy plan/adjustment compatibility.
- [ ] Remove local cancellation compatibility if present.
- [ ] Remove direct/campaign-less promotion compatibility if present.
- [ ] Remove old refund/negative-App-Event compatibility if present.
- [ ] Preserve accepted platform-policy controls and authorization/audit boundaries.
- [ ] Add/update focused regression coverage.
- [ ] Run repository-declared validation.

## Interfaces / Contracts

Consumes:

```text
DATABASE-013 final Prisma baseline
@modainteract/moda-interact-shared version published by SHARED-008
```

Canonical lifetime-Free names:

```text
PlatformBillingPolicy.lifetimeFreeRecoveryAllowance
EntitlementCounter.LIFETIME_FREE_RECOVERY_CREDITS
```

This task creates no new cross-service contract.

## Dependencies

- `ARCH-010-DATABASE-013`
- `ARCH-010-SHARED-008`
- `ARCH-010-ADMIN-001`

## Enables

- `ARCH-010-ADMIN-002`
- `ARCH-010-ADMIN-004`
- `ARCH-010-ADMIN-008`

## Acceptance Criteria

1. Admin builds/types against DATABASE-013 with no reference to `BillingPlan.freeLifetimeConversationAllowance` or `BillingAllowanceAdjustment`.
2. No Admin source/test uses `FREE_RECOVERY_LIFETIME`; canonical lifetime state uses `LIFETIME_FREE_RECOVERY_CREDITS`.
3. No Admin source/test depends on the removed local cancellation models/contracts.
4. No Admin first-release action creates a campaign-less/direct promotional grant or depends on the aggregate promotional entitlement counter.
5. No Admin source/test depends on `RecoveryCreditPurchaseStatus.REFUNDED`, negative-App-Event refund settlement mode, or refund correction UsageEvents.
6. Accepted lifetime-Free platform-policy control, authorization and audit behaviour still pass focused tests.
7. No merchant authentication/route boundary changes are introduced.
8. Repository-wide search evidence proves removed baseline symbols are absent except where they appear in intentional historical documentation outside implementation ownership.
9. Required repository validation passes or only documented unchanged baseline failures remain.

## Validation

Use the actual scripts declared by `package.json`. At minimum:

```text
focused Admin billing/security tests covering touched behaviour
repository typecheck when declared
repository lint when declared
repository build when declared
git diff --check
```

Also run exact source/test searches for:

```text
freeLifetimeConversationAllowance
BillingAllowanceAdjustment
FREE_RECOVERY_LIFETIME
SubscriptionCancellationRequest
RecoveryCreditPurchaseStatus.REFUNDED
CURRENT_CYCLE_APP_EVENT_CORRECTION
PROMOTIONAL_RECOVERY_CREDITS
```

Any remaining implementation reference must be explained and must not recreate compatibility state.

## Implementation Notes

This task is deliberately a correction/conformance task. Do not opportunistically implement downstream Admin features merely because their final schema is now available.

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

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

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
