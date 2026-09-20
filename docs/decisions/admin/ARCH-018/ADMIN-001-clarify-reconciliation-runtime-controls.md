---
id: ARCH-018-ADMIN-001
architecture_id: ARCH-018
title: Clarify that reconciliation controls include expired promotion cleanup
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-ADMIN-009
enables:
- ARCH-018-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# ARCH-018-ADMIN-001

## Objective

Clarify the existing Admin Background Runtime Controls so operators understand that the existing billing reconciliation interval/batch also governs expired promotion-selection cleanup.

This task changes **copy/tests only**. Do not add or rename any runtime-config field, database column, lease, action payload or UI section.

## Read before editing

```text
src/lib/admin/background-runtime-control-validation.ts
src/components/admin/background-runtime-controls.tsx
src/app/actions/background-runtime-controls.ts
tests/unit/background-runtime-control-validation.test.ts
tests/security/admin-background-runtime-controls.test.mjs
docs/architecture/ARCH-018-promotion-selection-lock-and-expiry-reconciliation.md
```

## Authorized implementation surface

```text
src/lib/admin/background-runtime-control-validation.ts
tests/unit/background-runtime-control-validation.test.ts
tests/security/admin-background-runtime-controls.test.mjs
```

Do not edit the component/action unless the exact copy cannot be surfaced from `RUNTIME_FIELDS`. If that occurs, STOP and return to architect rather than broadening scope.

## Exact production change

In `RUNTIME_FIELDS.OPERATIONAL`, keep the same key, label, units, min/max/default:

```text
key: billingReconciliationIntervalSeconds
label: Reconciliation interval
unit: seconds
min: 10
max: 3600
default: 60
```

Replace only its description with this exact approved copy:

```text
How often Moda performs periodic billing and entitlement reconciliation, including Shopify billing checks and expired promotion cleanup.
```

Keep:

```text
billingReconciliationShopBatchSize
label: Shops per reconciliation cycle
```

Replace only its description with:

```text
Maximum merchants processed during one periodic billing and entitlement reconciliation pass, including expired promotion cleanup. Increase this as the merchant base grows, while watching provider and database load.
```

Do not change the key names or persistence semantics.

## Explicit non-changes

There must be no new:

```text
promotionReconciliationIntervalSeconds
promotionReconciliationBatchSize
BackgroundRuntimeLeaseName
Prisma migration
Admin mutation field
environment variable
```

The Background task uses the existing values.

## Tests

In `tests/unit/background-runtime-control-validation.test.ts`, add one test that locates both fields from `ALL_RUNTIME_FIELDS` and asserts the exact label/description strings above plus unchanged defaults/ranges.

In `tests/security/admin-background-runtime-controls.test.mjs`, add source assertions that:

```text
Reconciliation interval
expired promotion cleanup
```

are present in validation metadata and that no `promotionReconciliationIntervalSeconds`/`promotionReconciliationBatchSize` string appears in action/validation/component source.

Do not weaken any existing SUPER_ADMIN/version/audit assertions.

## Validation

Run:

```bash
npm run prisma:generate
npm run prisma:validate
npm run test:unit
npm test
npm run build
npm run lint -- \
  src/lib/admin/background-runtime-control-validation.ts \
  tests/unit/background-runtime-control-validation.test.ts \
  tests/security/admin-background-runtime-controls.test.mjs
npm run format:check -- \
  src/lib/admin/background-runtime-control-validation.ts \
  tests/unit/background-runtime-control-validation.test.ts \
  tests/security/admin-background-runtime-controls.test.mjs
git diff --check
```

If repository-wide baseline failures remain outside the three authorized files, report them without repairing unrelated code.

## Stop conditions

STOP if copy cannot be changed without schema/action/API changes. No such change is authorized by ARCH-018.

## Completion protocol

Set task to `review`, clear claim fields, report exact validation results/implementation commit, push both task branches and STOP.

## Acceptance invariant

The Admin UI describes the existing interval as periodic billing **and entitlement** reconciliation including expired promotion cleanup, while the underlying runtime-control contract remains byte-for-byte compatible in key/type/range/default semantics.
