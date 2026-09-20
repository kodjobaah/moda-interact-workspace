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
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-09-20T07:20:32Z
attempt: 2
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

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-admin/src/lib/admin/background-runtime-control-validation.ts`
- `moda-interact-admin/tests/unit/background-runtime-control-validation.test.ts`
- `moda-interact-admin/tests/security/admin-background-runtime-controls.test.mjs`

### Work Completed

- Updated the existing reconciliation interval guidance to describe periodic billing and entitlement reconciliation, including Shopify billing checks and expired promotion cleanup.
- Updated the existing reconciliation batch guidance to describe expired promotion cleanup without adding a new control.
- Added exact metadata contract coverage for both fields and source-level security assertions for the approved copy and prohibited promotion-specific control names.
- Preserved all existing keys, labels, units, ranges, defaults, authorization, version fencing, audit, and persistence semantics.

### Validation Results

- Focused unit/security tests: passed, 13 tests, 0 failures.
- `git diff --check`: passed.
- `npm run test:unit`: blocked by missing installed dependencies; changed tests passed, while unrelated tests failed on missing `exceljs` and `@modainteract/moda-interact-shared`.
- `npm test`: blocked by missing installed dependencies including `bullmq` and other repository packages.
- `npm run prisma:generate`: blocked because `prisma` is not installed.
- `npm run prisma:validate`: blocked because `prisma` is not installed.
- `npm run build`: blocked because `prisma` is not installed.
- Focused lint: blocked because `eslint` is not installed.
- Focused format check: blocked because `prettier` is not installed.

### Deviations

Repository-wide validation could not complete in the dependency-free prepared worktree. No unrelated failures were repaired.

### Assumptions

The existing `field.guidance` metadata path is the approved UI copy surface, as confirmed by the component read before editing.

### Unresolved Issues

Install the repository dependencies in the implementation worktree before rerunning the blocked required validation commands.

### Architectural Concerns

None.

### Git / VCS

Implementation commit: `1407869`.

Parent report commit: `3d622105`.


## Architect Review — Attempt 1

### Review Status

Changes Requested — acceptance evidence correction only. No production-code correction is required.

### Functional assessment

The implementation is functionally conformant with ARCH-018-ADMIN-001. `RUNTIME_FIELDS.OPERATIONAL` retains the existing `billingReconciliationIntervalSeconds` and `billingReconciliationShopBatchSize` keys, labels, units, ranges and defaults while changing only their `guidance` strings to the exact architect-approved copy. The existing Admin component renders `field.guidance`, so the revised text reaches the Background Runtime UI without a component/action/schema change.

The focused unit contract asserts both complete field objects, including unchanged key/label/unit/min/max/default semantics. The focused security contract asserts the approved copy and verifies that `promotionReconciliationIntervalSeconds` and `promotionReconciliationBatchSize` are absent from validation/action/component source. Source review found no new promotion-specific runtime control, lease, environment variable, action field or persistence contract.

The unavailable repository dependencies do not expose a functional defect in this copy-only task. No implementation change is requested for Prisma, build, lint, formatting or unrelated dependency failures.

### Blocking acceptance-evidence gap

Architect acceptance cannot be recorded from this submission because the required task-execution evidence is internally inconsistent/incomplete:

1. The Completion Report records parent report commit `3d622105`, while the architect submission identifies parent report commit `b8927548`. One exact canonical parent report commit must be reported.
2. The Completion Report does not record the launcher-resolved dedicated parent worktree, implementation worktree, prepared execution/claim evidence, or start-of-attempt synchronization evidence required by `docs/agent-worktree-isolation-policy.md` and the architect contract.
3. The submitted archive contains no Git metadata from which the architect can independently reconstruct that missing evidence. Do not infer or manufacture developer-specific paths or commit IDs.

### Required Attempt 2 correction — deterministic and report-only

Do **not** modify production code or tests solely for this review. The accepted functional implementation remains implementation commit `1407869` unless the steps below reveal that the submitted branch does not actually contain that implementation.

1. Start `ARCH-018-ADMIN-001` through the normal deterministic `/moda-task` preparation path so `scripts/start-agent-task.py --prepare` resolves the canonical primary workspace and the dedicated mirrored worktrees.
2. Use the launcher-returned values exactly. Do not derive paths from the previous task worktree and do not invent absolute paths.
3. Verify the implementation worktree is on `task/ARCH-018-ADMIN-001` and contains implementation commit `1407869` (or a descendant containing exactly the same functional change with no unrelated code churn).
4. Verify the parent worktree is on the matching `task/ARCH-018-ADMIN-001` branch.
5. Record in the Completion Report, verbatim from the prepared execution packet / Git inspection:
   - canonical `workspace_root`;
   - dedicated parent worktree path;
   - dedicated implementation worktree path;
   - mirrored parent and implementation branch names;
   - preparation/claim commit or packet identifier supplied by the launcher;
   - start-of-attempt synchronization result for parent and implementation repositories;
   - recursive implementation-submodule materialisation result where supplied by the launcher;
   - exact implementation commit reviewed;
   - the one exact parent report commit that actually contains the corrected Completion Report.
6. Resolve the current `3d622105` versus `b8927548` discrepancy. The corrected report must contain only the actual parent report commit. Do not copy either value unless Git confirms it.
7. Rerun the focused ARCH-018-ADMIN-001 tests in the canonical implementation worktree and report their exact result. The expected focused scope remains:
   - `tests/unit/background-runtime-control-validation.test.ts`;
   - `tests/security/admin-background-runtime-controls.test.mjs`.
8. Rerun `git diff --check`.
9. Run the task's other required validation commands if their declared dependencies are available in the canonical prepared worktree. If a command is blocked because the dependency is genuinely unavailable, record the exact command and exact blocker; do not modify unrelated code or broaden task scope merely to make repository-wide validation green.
10. Confirm the implementation diff is still restricted to the three authorized implementation/test files:
    - `src/lib/admin/background-runtime-control-validation.ts`;
    - `tests/unit/background-runtime-control-validation.test.ts`;
    - `tests/security/admin-background-runtime-controls.test.mjs`.
11. Set the task back to `review`, clear `executor` and `claimed_at`, commit/push the corrected parent Completion Report, and resubmit.

### Stop conditions

STOP and return to `moda_architect` without changing implementation code if any of the following is true:

- the normal launcher resolves execution in a shared/default checkout or another task's worktree;
- implementation commit `1407869` is not present on the canonical task branch and the discrepancy cannot be explained by a no-churn descendant commit;
- the parent and implementation branches are not both the mirrored `task/ARCH-018-ADMIN-001` branch;
- the prepared packet reports unsatisfied dependency or synchronization gates;
- correcting the evidence would require altering runtime-control schema, action/API behavior, component structure or any file outside the three authorized implementation/test files.

No new Admin functionality, tests beyond the focused evidence above, schema work, or runtime-control design change is requested. Attempt 2 exists only to provide deterministic acceptance evidence for the already functionally conformant implementation.
