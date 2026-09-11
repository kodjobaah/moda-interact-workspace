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
status: pending
priority: 51
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHARED-001
enables:
  - ARCH-010-SHARED-004
created: 2026-09-11
updated: 2026-09-11
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
