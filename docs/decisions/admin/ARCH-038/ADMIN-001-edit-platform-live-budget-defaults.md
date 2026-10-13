---
id: ARCH-038-ADMIN-001
architecture_id: ARCH-038
title: Manage Platform LIVE CommerceAgent budgets
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: developer
claimed_at: null
attempt: 1
depends_on:
  - ARCH-038-DATABASE-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-13
---
# Manage Platform LIVE CommerceAgent budgets

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_admin`
- Repository: `moda-interact-admin`

## Objective

Expose centrally audited LIVE CommerceAgent Platform deadline/output-token defaults in System Controls → Platform Policy.

## Context

The existing Platform Policy page edits billing/recovery safeguards. CommerceAgent execution controls belong in a clearly separated section backed by `CommerceModelPolicy` filtered to `context=LIVE` and `scope=PLATFORM`.

## Scope

- Add a distinct **CommerceAgent Execution Policy** section within System Controls → Platform Policy (not mixed with billing controls); show selected environment, required LIVE defaults, edit/schema versions and visible provenance.
- Build a reusable **schema-driven Admin budget-policy editor** for ADMIN-001/002/003 using an allowlisted `budgetSchemaVersion=1` descriptor for `deadlineMs` and `outputTokens`, with labels, units, descriptions, parsing, inline errors and optional scope-dependent Override/Inherit controls. Do not render arbitrary JSON keys as inputs.
- Display deadline in milliseconds alongside a readable seconds equivalent, and explain that `outputTokens` is per model invocation.
- Implement SUPER_ADMIN-only server reads and version-checked writes using DATABASE-001 schema.
- Record mandatory audit reason, actor and changed values in same durable mutation; expose a scope/environment-filtered **Policy History** view of existing `CommerceAuditEvent` records (timestamp, actor, reason and before/after values) with pagination/empty state.
- Handle missing defaults, stale edits, field-level validation errors and double-submit safely; present explicit conflict/reload recovery and disable the save action in flight.

## Out of Scope

- Do not add LIVE budgets to PlatformBillingPolicy or change its validation rules.
- Do not expose these controls to merchants or edit Preview budgets.

## Requirements

- Deadline means total turn milliseconds, tokens means per model call; both required positive safe integers.
- Server validates operational feasibility against documented Background execution envelope; unresolved envelope limitations must be raised rather than silently clipped.
- Required default persists as complete JSONB `budget` and is shown with provenance, budget schema version and edit version. Unknown schema versions/keys fail closed; neither required Platform field can be set to Inherit. Future JSON keys are editable only after the versioned descriptor and runtime support are updated.

## Work Items

- [x] Add Admin read/mutation path using accepted database schema.
- [x] Implement shared Admin field descriptors and reusable form/editor; integrate required Platform inputs, descriptions, effective source and in-flight protection in the existing Platform Policy page.
- [x] Add paginated, scoped Commerce policy audit-history read/presentation using existing `CommerceAuditEvent`.
- [ ] Add authentication, scoped history, schema allowlist, audit, CAS/conflict reload, double-submit and field-validation regression tests.

## Interfaces / Contracts

Consumes ARCH-038-DATABASE-001 `CommerceModelPolicy` (`context=LIVE`, `scope=PLATFORM`, `budgetSchemaVersion=1`) Platform row and existing CommerceAuditEvent. Exposes repository-local reusable Admin editor/field descriptors for ARCH-038-ADMIN-002 and ADMIN-003; does not introduce a new cross-service contract or modify Shared/merchant-facing applications.

## Dependencies

- `ARCH-038-DATABASE-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Only authorised SUPER_ADMIN can save; audit is transactional.
- [x] Invalid/stale inputs render actionable errors without partial writes.
- [x] Changing Platform default does not mutate Plan, Merchant or Preview overrides.
- [x] Required numeric fields, descriptions, units and effective source display clearly; no raw JSON editing or unsupported keys.
- [x] Scoped Policy History shows actor, time, reason and old/new changed budget fields without exposing other merchants; concurrent save shows a recoverable conflict.
- [x] Reusable editor is available to downstream Admin Plan and Merchant tasks without duplicate field schemas.

## Validation

- [ ] Focused admin action and component tests
- [x] Relevant typecheck/lint/build scripts
- [x] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-ADMIN-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Developer Self-Review — Changes Requested, Attempt 1. The implementation is present and its current focused unit tests, typecheck, lint, and production build were run during reconciliation. Review identified an authorization-boundary mismatch and missing action/component regression coverage; the task is returned to `ready` without incrementing the attempt.

### Files Changed

Implementation commit `c843e7a` changes:

- `src/app/(protected)/system-controls/platform-policy/page.tsx`
- `src/app/actions/commerce-model-platform-policy.ts`
- `src/components/admin/commerce-model-policy/budget-policy-fields.tsx`
- `src/components/admin/commerce-model-policy/live-platform-policy.tsx`
- `src/lib/admin/commerce-model-platform-policy.ts`
- `src/lib/admin/commerce-model-policy-fields.ts`
- `tests/unit/commerce-model-platform-policy.test.ts`
- `tests/unit/commerce-model-policy-fields.test.ts`

Implementation commit `640d8fc` updates the `database` submodule gitlink to `12c3bee13cabeb3c8b9cb0ac602d836700702413`.

### Work Completed

- Added a LIVE/PLATFORM policy dashboard and SUPER_ADMIN-guarded save action with complete budget validation, version-checked mutation, and a transactional `CommerceAuditEvent` write.
- Added reusable allowlisted budget descriptors and field controls, Platform Policy page integration, and a paginated Policy History view scoped to the current LIVE Platform policy and environment.
- The required SUPER_ADMIN-only read boundary is not complete: the dashboard read currently uses the general platform-admin read guard. Required action/component-level regression coverage is also incomplete; see Developer Self-Review below.

### Validation Results

- Focused policy service/validation tests: **PASS**, 2 files / 8 tests, using `node --experimental-strip-types --test tests/unit/commerce-model-platform-policy.test.ts tests/unit/commerce-model-policy-fields.test.ts`.
- `./node_modules/.bin/tsc --noEmit`: **PASS** (the repository has no dedicated typecheck script).
- ESLint on the eight changed files: **PASS**, zero errors. ESLint reported the two `tests/unit` files as ignored by its configured patterns, so those test files were not linted.
- `npm run build`: **PASS**, including Prisma Client generation and Next.js TypeScript/build stages. Build warnings were emitted for existing BullMQ optional/runtime imports (`@valkey/valkey-glide` and dynamic dependency expression); compilation and page generation completed.
- `git diff --check origin/main...HEAD`: **PASS** for the implementation task branch. Parent task report `git diff --check`: **PASS** after this update.
- The focused tests exercise policy projection/update/history query and pure schema/form validation. No server-action or React component tests exist for this feature yet; the task's required focused action/component validation is therefore incomplete.

### Deviations

- No implementation files were changed during this reconciliation. The implementation branch already contains and publishes commits `c843e7a` and `640d8fc`.
- The shared primary workspace and shared `moda-interact-admin` checkout contain unrelated user changes. They were not used for task implementation and were left untouched.

### Assumptions

None

### Unresolved Issues

- `getLivePlatformPolicyDashboard()` authorizes with `requirePlatformAdminRead()`, which permits non-SUPER_ADMIN platform roles to read the new LIVE policy and its audit history. Task scope requires SUPER_ADMIN-only server reads.
- The changed tests do not invoke the server action or render/test the React controls. Authentication enforcement, conflict/reload behavior, in-flight single-submit behavior, field-error rendering, history empty/pagination presentation, and the transaction boundary need focused action/component regressions.

### Architectural Concerns

- The hard-coded `LIVE_BACKGROUND_DEADLINE_ENVELOPE_MS = 90_000` matches the current Background `AbortSignal.timeout(90_000)` implementation. The Admin form rejects larger values rather than clipping them.
- Policy mutation filters on the exact LIVE/PLATFORM policy row; Preview and scoped override rows are not targeted by this write.

### Physical Worktree and Synchronization Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-ADMIN-001`, branch `task/ARCH-038-ADMIN-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-ADMIN-001`, branch `task/ARCH-038-ADMIN-001`.
- At review start, the parent task branch was at claim commit `39b84b59` and matched `origin/task/ARCH-038-ADMIN-001`; implementation was at `640d8fc` and matched `origin/task/ARCH-038-ADMIN-001`. `origin/main` was already an ancestor of the implementation branch.
- The parent task worktree was clean before reconciliation. After fetching both repositories, current `origin/main` was merged into the parent task branch; the merge completed without conflict. This report update will be pushed on the same parent task branch.
- The primary workspace and shared Admin checkout had unrelated modified/untracked content; neither was used for task changes. No other task worktree was used.

## Developer Self-Review - Changes Requested

### Review Result

Changes Requested — Attempt 1. Preserve the current attempt number. The task returns to `ready` with `executor: null` and `claimed_at: null`; the next `/moda_developer_create` claim increments to Attempt 2.

### Required Corrections

1. Enforce the required SUPER_ADMIN-only authorization on the server-side LIVE Platform policy read/dashboard path, including audit history. UI visibility is not an authorization boundary. Add a regression proving a non-SUPER_ADMIN platform role cannot read the policy or history.
2. Add focused tests that invoke the actual save server action and exercise the React controls. Cover unauthorized roles, validation field errors, stale/CAS conflict response and reload recovery, audit transaction rollback, and double-submit/in-flight disabling. Add component assertions for the field errors and Policy History empty/paginated states. Keep the existing service and parser tests.
3. Rerun the focused action/component suite plus `tsc --noEmit`, changed-file ESLint, `npm run build`, and `git diff --check`; update the Validation checkboxes and Completion Report only from those results.

### Evidence Reviewed

- `src/lib/admin/commerce-model-platform-policy.ts` loads the dashboard via `requirePlatformAdminRead()` and queries policy/audit records by exact LIVE Platform row/environment.
- `src/app/actions/commerce-model-platform-policy.ts` checks SUPER_ADMIN before mutation and wraps policy update plus audit insertion in a serializable transaction.
- Existing changed tests cover low-level CAS/audit/history query and field parsing, but do not invoke the action or exercise the component.
- Validation during self-review: focused tests **PASS** (2 files / 8 tests), `tsc --noEmit` **PASS**, changed-file ESLint **PASS** with test files ignored, and `npm run build` **PASS** with the warnings recorded above.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation

### Follow-up

None
