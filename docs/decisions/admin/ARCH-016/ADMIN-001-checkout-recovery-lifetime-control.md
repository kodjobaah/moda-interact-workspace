---
id: ARCH-016-ADMIN-001
architecture_id: ARCH-016
title: Add platform checkout-recovery lifetime control
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-016-DATABASE-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16T17:28:00Z
---

# ARCH-016-ADMIN-001

## Objective

Expose `BackgroundRuntimeConfig.checkoutRecoveryLifetimeDays` through the existing audited platform runtime controls. Do not build a parallel settings system.

## Authorized implementation surface

```text
src/lib/admin/background-runtime-control-validation.ts
src/app/actions/background-runtime-controls.ts
src/components/admin/background-runtime-controls.tsx
src/app/(protected)/billing/controls/page.tsx only if presentation wiring requires it
focused tests
```

No tenant recovery-policy override work; that is ADMIN-002.

## Required field

Add to OPERATIONAL section:

```text
key: checkoutRecoveryLifetimeDays
label: Checkout recovery lifetime
guidance: Expire an active checkout recovery after this many days without checkout/customer activity. Expired history is retained; later checkout activity can start a new recovery generation.
unit: days
min: 1
max: 90
default: 21
```

Use whole integer days only.

## Existing audit/version semantics

The update MUST use existing:

```text
expectedVersion optimistic concurrency
required admin reason
BackgroundRuntimeConfigAuditEvent
beforeValue / afterValue
```

Do not create another audit table.

Classify the audit event under existing `OPERATIONAL` section.

## Presentation

The admin page should make clear:

- `21 days` default;
- expiry does not delete recovery/conversation/message history;
- changing the value affects the next expiry scans using the new current cutoff;
- it is platform-wide, not merchant-specific.

Do not expose expiry scheduler cadence as another control.

## Required tests

- default displays 21 days;
- accepts 1 and 90;
- rejects 0, 91, fraction/non-integer;
- optimistic conflict behavior unchanged;
- reason remains mandatory;
- audit event contains before/after value;
- changing this field does not rewrite checkout recovery rows from Admin.

## Validation

```text
npm run test:unit
npm test
npm run lint
npm run build
git diff --check
```

Run only scripts actually declared by repository package.json.

## Stop conditions

STOP if implementation would:

- add an unaudited direct database edit;
- make the lifetime merchant-configurable;
- delete expired recovery data;
- introduce a second runtime-config store.

## Completion protocol

## Completion Report

### Status

Ready for Review

### Work Completed

Exposed `BackgroundRuntimeConfig.checkoutRecoveryLifetimeDays` through the existing audited platform runtime controls as an OPERATIONAL field:

- default: 21 days;
- accepted range: whole integer days from 1 through 90;
- platform-wide, not merchant-specific;
- expiry guidance explains that recovery, conversation, and message history is retained and later checkout activity can start a new generation;
- expiry-scan cutoff guidance explains that changes apply to subsequent scans.

The existing `expectedVersion`, required reason, `BackgroundRuntimeConfigAuditEvent`, `beforeValue`, and `afterValue` behavior remains in use. No checkout recovery rows are mutated by the Admin action, no scheduler cadence control was added, and no second runtime-config store was introduced.

### Files Changed

- `src/lib/admin/background-runtime-control-validation.ts`
- `src/app/actions/background-runtime-controls.ts`
- `src/components/admin/background-runtime-controls.tsx`
- `tests/unit/background-runtime-control-validation.test.ts`
- `tests/security/admin-background-runtime-controls.test.mjs`

### Validation

- focused unit validation: 6 passed;
- focused security validation: 5 passed;
- `npm run test:unit`: 125 passed, 0 failed;
- `npm run lint`: passed;
- `npm run build`: passed;
- `git diff --check`: passed;
- `npm test`: repository baseline remains non-clean: 97 passed, 2 failed, 11 cancelled, 3 skipped. The failures are unrelated existing async security/observability harness cancellations plus two pre-existing internationalization expectation mismatches (`@modainteract/moda-interact-shared` version/catalogue expectations). The changed runtime-controls security test passes independently.

### Physical Worktree Isolation

- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`;
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-016-ADMIN-001`;
- parent branch: `task/ARCH-016-ADMIN-001`;
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-016-ADMIN-001`;
- implementation branch: `task/ARCH-016-ADMIN-001`;
- shared workspace checkout switched or mutated for task work: no;
- shared implementation checkout switched or mutated for task work: no;
- another task worktree reused: no;
- implementation submodule `database`: `c59f2eb6953642f1c850d38b09ed03096d672547`;
- recursive submodule sync: passed;
- recursive submodule update/init: passed.

### Synchronization Evidence

- parent remote task branch fast-forwarded: not-needed;
- parent origin/main incorporated: already-current;
- implementation remote task branch fast-forwarded: not-needed;
- implementation origin/main incorporated: already-current.

### Git / Handoff

- implementation commit: `44dd7a5` (`feat(admin): expose checkout recovery lifetime control`);
- implementation branch pushed: `origin/task/ARCH-016-ADMIN-001`;
- task status set to `review`;
- executor and claimed timestamp cleared;
- returned to `moda_architect` for review; no merge to `main` performed.

## Completion protocol

The implementation and report are complete. The task is returned to `moda_architect` at `status: review`; stop here pending architect acceptance.
