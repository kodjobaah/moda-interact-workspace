---
id: ARCH-010-SHARED-003
architecture_id: ARCH-010
title: Add generic recovery-capacity-exhausted billing system code
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 51
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-010-SHARED-001
enables:
  - ARCH-010-SHARED-004
created: 2026-09-11
updated: 2026-09-11T16:57:52Z
---

# ARCH-010-SHARED-003: Add generic recovery-capacity-exhausted billing system code

## Objective

Extend the existing Shared merchant-billing system-message contract with one plan-neutral code used when **all currently supported recovery capacity is exhausted**:

```text
BILLING_RECOVERY_CAPACITY_EXHAUSTED
```

The code is consumed by Background when writing SYSTEM support messages and by the merchant app when choosing the safe merchant action.

## Inspect before editing

```text
src/billing.ts
src/billing.test.ts
src/index.ts
package.json
tsup.config.ts
```

Use the existing `BILLING_SYSTEM_MESSAGE_CODES` and `BillingSystemMessageCodeSchema` pattern. Do not create a second system-message registry.

## Required contract change

Add:

```ts
RECOVERY_CAPACITY_EXHAUSTED: "BILLING_RECOVERY_CAPACITY_EXHAUSTED"
```

to the canonical billing system-message code object/schema/export.

Keep all existing values, including:

```text
BILLING_FREE_ALLOWANCE_EXHAUSTED
```

for backward compatibility with already-persisted messages. Do not rename or remove historical values.

## Required tests

Prove at least:

1. the new code exists in `BILLING_SYSTEM_MESSAGE_CODES`;
2. `BillingSystemMessageCodeSchema` accepts it;
3. existing codes still parse unchanged;
4. unknown codes remain rejected;
5. the public billing entrypoint exports the updated contract;
6. no queue payload version is changed by this task.

## Validation

Run the repository's declared focused Shared tests/build/typecheck plus:

```bash
git diff --check
```

## Non-goals

Do not publish in this task. Do not edit Background/App consumers, database schema, message copy, queue contracts, promotional credits or refund contracts.

## Stop conditions

STOP if ARCH-010-SHARED-001 has not been reconciled into the task worktree or another accepted Shared change has already introduced an equivalent generic code under a different canonical name.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `src/billing.ts`
- `src/billing.test.ts`
- `scripts/validate-billing-entrypoint.mjs`

### Work Completed
- Added `RECOVERY_CAPACITY_EXHAUSTED` to the canonical `BILLING_SYSTEM_MESSAGE_CODES` registry and strict `BillingSystemMessageCodeSchema`.
- Preserved the historical `BILLING_FREE_ALLOWANCE_EXHAUSTED` code and all existing system-message values.
- Added focused coverage for the new code, legacy-code compatibility, unknown-code rejection, and unchanged v1 queue payload semantics.
- Extended the existing public `./billing` entrypoint validation to verify the updated registry and exact new code value.

### Validation Results
- `npm test -- src/billing.test.ts` passed; Redis integration remains skipped because `TEST_REDIS_URL` is not configured.
- `npm run typecheck` passed.
- `npm run build` passed.
- `npm run validate:billing-entrypoint` passed, including built runtime and declaration/package-target validation.
- `git diff --check` passed.
- `npm ci` completed in the isolated implementation worktree; npm reported one low-severity audit finding and pending install-script approvals, with no task-source impact.

### Git / VCS
- Task branch: `task/ARCH-010-SHARED-003`
- Physical worktree isolation:
  - canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  - parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHARED-003`
  - parent branch: `task/ARCH-010-SHARED-003`
  - implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHARED-003`
  - implementation branch: `task/ARCH-010-SHARED-003`
  - shared workspace checkout switched/mutated for task work: no
  - shared implementation checkout switched/mutated for task work: no
  - another task worktree reused: no
- Start-of-attempt synchronization:
  - parent remote task branch fast-forwarded: not-needed; branch created from current `origin/main`
  - parent `origin/main` incorporated: already-current at worktree creation
  - implementation remote task branch fast-forwarded: not-needed; branch created from current `origin/main`
  - implementation `origin/main` incorporated: already-current at worktree creation
- Implementation repository: `moda-interact-shared`, commit `a81215e`, remote `origin/task/ARCH-010-SHARED-003`, pushed: yes.
- Parent workspace task file: this file, review report commit `d92e70b`, remote `origin/task/ARCH-010-SHARED-003`, pushed: yes.
- Submodule gitlink staged: no.
- Merged to implementation main: no.
- Merged to workspace main: no.

### Architect Review
Pending.
