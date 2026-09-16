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
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-09-16T16:18:30Z
attempt: 1
depends_on:
- ARCH-016-DATABASE-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16
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

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
