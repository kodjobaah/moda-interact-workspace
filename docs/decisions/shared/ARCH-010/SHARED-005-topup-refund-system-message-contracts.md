---
id: ARCH-010-SHARED-005
architecture_id: ARCH-010
title: Add merchant top-up refund billing message contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 22
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-010-SHARED-006
created: 2026-09-11
updated: 2026-09-11T16:12:00Z
---

# ARCH-010-SHARED-005: Add merchant top-up refund billing message contracts

## Objective

Add the canonical merchant billing system-message codes required by ARCH-010 partial purchased-top-up refunds.

## Required codes

Extend the existing billing system-message contract with exactly:

```text
BILLING_REFUND_REQUEST_RECEIVED
BILLING_REFUND_COMPLETED
BILLING_REFUND_REJECTED
```

Use the existing `BILLING_SYSTEM_MESSAGE_CODES`, `BillingSystemMessageCodeSchema` and `createMerchantBillingSystemSourceKey` conventions.

Do not introduce a second message-code registry.

## Idempotency identity

Refund messages use the durable `RecoveryCreditRefund.id` as `eventIdentity`.

Examples:

```text
billing-system:<shopId>:BILLING_REFUND_REQUEST_RECEIVED:<refundId>:1
billing-system:<shopId>:BILLING_REFUND_COMPLETED:<refundId>:1
billing-system:<shopId>:BILLING_REFUND_REJECTED:<refundId>:1
```

Do not put purchase amount, merchant PII or support-message text into source keys.

## Compatibility

The frozen ARCH-009 Shared branch may already contain equivalent codes. At task preflight:

- if exact names/values already exist in the integrated source, do not duplicate them; add/retain the ARCH-010 acceptance tests and report reuse;
- if values differ, STOP and return the conflict to `moda_architect`.

Do not import frozen ARCH-009 task metadata as a dependency.

## Required tests

Prove:

1. all three exact values are included in `BillingSystemMessageCodeSchema`;
2. deterministic refund source keys are stable;
3. long shop/refund IDs remain bounded through existing helper semantics;
4. unrelated billing/WhatsApp contracts are unchanged.

Run repository unit/type/build validation declared by `package.json` and `git diff --check`.

## Non-goals

Do not publish the package, edit consumer repositories, add refund quantities/status enums or create queue contracts.

## Stop conditions

STOP if equivalent refund message codes already exist with different values/semantics or if adding the codes would require changing a consumer repository. Report the exact conflict to `moda_architect`.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `src/billing.test.ts`
- `docs/decisions/shared/ARCH-010/SHARED-005-topup-refund-system-message-contracts.md`

### Work Completed
- Reused the existing `BILLING_SYSTEM_MESSAGE_CODES` entries and `BillingSystemMessageCodeSchema` values for all three required refund codes; no duplicate registry or source constants were introduced.
- Added focused acceptance coverage for the exact refund values, schema parsing, deterministic `RecoveryCreditRefund.id`-style source keys, and bounded long shop/refund identifiers.
- Existing cancellation, WhatsApp, and other billing contract coverage remains unchanged.

### Validation Results
- `npm test -- --test-name-pattern='top-up refund'` passed: 107 passed, 0 failed, 1 skipped because `TEST_REDIS_URL` is not configured; the refund acceptance test passed.
- `npm run typecheck` passed.
- `npm run build` passed, including the public billing entrypoint declarations.
- `git diff --check` passed.
- `npm ci` installed the repository lockfile dependencies in the new worktree; npm reported one low-severity audit finding and pending install-script approvals, with no task-source impact.

### Git / VCS
- Task branch: `task/ARCH-010-SHARED-005`.
- Physical worktree isolation:
  - canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`;
  - parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHARED-005`;
  - parent branch: `task/ARCH-010-SHARED-005`;
  - implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHARED-005`;
  - implementation branch: `task/ARCH-010-SHARED-005`;
  - shared workspace checkout switched/mutated for task work: no;
  - shared implementation checkout switched/mutated for task work: no;
  - another task worktree reused: no.
- Start-of-attempt synchronization:
  - parent remote task branch fast-forwarded: not-needed; branch created from current `origin/main`;
  - parent `origin/main` incorporated: already-current;
  - implementation remote task branch fast-forwarded: not-needed; branch created from current `origin/main`;
  - implementation `origin/main` incorporated: already-current.
- Implementation repository: `moda-interact-shared`, commit `cdb29ca`, remote `origin/task/ARCH-010-SHARED-005`, pushed: yes.
- Parent workspace task file: this file, claim commit `5337f57`, review commit pending, pushed: yes.
- Submodule gitlink staged: no.
- Merged to implementation main: no.
- Merged to workspace main: no.

### Architect Review
Pending.
