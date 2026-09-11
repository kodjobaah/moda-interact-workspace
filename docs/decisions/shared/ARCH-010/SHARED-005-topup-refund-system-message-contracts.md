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
status: complete
priority: 22
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-010-SHARED-006
created: 2026-09-11
updated: 2026-09-11T17:44:41Z
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
- Parent workspace task file: this file, claim commit `5337f57`, review commit `d648ecb`, pushed: yes.
- Submodule gitlink staged: no.
- Merged to implementation main: no.
- Merged to workspace main: no.

### Architect Review

#### Review Status

Accepted

#### Attempt 1 — Accepted

Architect review verified:

- the integrated Shared billing contract already contains the exact required refund codes:
  - `BILLING_REFUND_REQUEST_RECEIVED`;
  - `BILLING_REFUND_COMPLETED`;
  - `BILLING_REFUND_REJECTED`;
- the values are present in the existing `BILLING_SYSTEM_MESSAGE_CODES` registry and
  `BillingSystemMessageCodeSchema`; no second registry or duplicate constants were introduced;
- the task correctly followed the compatibility rule by reusing the existing codes and adding
  ARCH-010 acceptance tests only;
- `createMerchantBillingSystemSourceKey` is used with the durable refund identity as
  `eventIdentity`, producing the required versioned keys;
- the tests prove exact readable refund source keys, deterministic replay identity, and bounded
  deterministic fallback for long shop/refund identifiers;
- no amount, merchant PII, support-message text, refund status enum, queue contract or consumer
  implementation was added to the source-key/message contract;
- the implementation repository change is focused on `src/billing.test.ts`; the billing source
  contract itself did not require modification for this task;
- repository tests, typecheck, build and `git diff --check` passed;
- the single Redis integration skip is unrelated to this contract and is expected when
  `TEST_REDIS_URL` is unset;
- the Completion Report contains the canonical parent and implementation worktrees, negative
  shared/reused-worktree assertions, and all four start-of-attempt synchronization outcomes;
- implementation commit `cdb29ca` is the reviewed implementation head.

**Architect decision: Accepted.**

Because `completion_mode: automatic`, this task is complete. `executor` and `claimed_at`
remain cleared while `attempt: 1` is preserved.

The submitted handoff identifies parent review-report commit `343bca5`. The task file also
contains earlier parent claim/review commit evidence; this is not an acceptance blocker because
the final parent commit cannot durably embed its own final hash.

`ARCH-010-SHARED-006` depends only on this task and is therefore promoted to `ready`.

