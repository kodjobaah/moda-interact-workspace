---
id: ARCH-032-ADMIN-001
architecture_id: ARCH-032
title: Admin controls for required MCP execution policy
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-032-DATABASE-001
enables:
- ARCH-032-GATEWAY-002
- ARCH-032-SYSTEM-TEST-002
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-ADMIN-001 — Admin controls for required MCP execution policy

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Allow authorised platform administrators to create, update and clear each environment’s MCP execution policy within the existing Platform Policy page.

## Context

The MCP JSONB entry must be provisioned intentionally through Admin or an approved deployment operation. MCP must never create or silently replace it. Reuse the singleton `PlatformBillingPolicy` and its current audited admin controls.

## Scope

Extend the **existing System Controls > Platform Policy** page (`src/app/(protected)/system-controls/platform-policy/page.tsx`) with a bounded MCP Execution Policy section. Edit the selected canonical Commerce environment's entry inside `PlatformBillingPolicy.mcpExecutionPolicy`; no new policy page or table. Show field descriptions and units; distinguish missing environment entry from missing singleton, permit intentional create/update/clear, validate complete positive bounded integers and provider timeout <= total deadline. Perform whole-row optimistic concurrency using existing `PlatformBillingPolicy.version`, incrementing on every successful mutation (including clear). Preserve billing fields and all other environment entries, and use existing audited mutation patterns. Prevent double submit; show inline validation and stale-version conflicts.

## Out of Scope

No merchant-facing controls, no MCP execution runtime code, no policy defaults, no separate policy store, no _index.md changes.

## Requirements

Reuse platform-admin authorisation and audited `PlatformBillingPolicy` mutation infrastructure. Make environment and shared row version visible; ensure that concurrent billing and MCP writes, edits of separate environments, and create-clear-replay cannot silently overwrite each other. Treat JSON null/absent entry as unprovisioned. Changes become effective in MCP through its bounded refresh/re-read, without redeploying services.

## Work Items

- [x] Inspect existing system-controls Admin pages and audit conventions.
- [x] Implement server action, validation and scoped UI.
- [x] Add focused authorisation/validation/concurrency regression tests.

## Interfaces / Contracts

Consumes the existing Prisma `PlatformBillingPolicy` row and `mcpExecutionPolicy` JSONB from ARCH-032-DATABASE-001; no local schema duplicate or second model. Audit environment, operation, previous/next version and actor without exposing private credentials.

## Dependencies

- ARCH-032-DATABASE-001

## Enables

- ARCH-032-GATEWAY-002
- ARCH-032-SYSTEM-TEST-002

## Acceptance Criteria

- [x] Only authorised platform administrators may create/update/clear an MCP environment entry; other callers are denied.
- [x] MCP controls appear on the existing Platform Policy page, with missing environment entries clearly visible and intentionally provisionable.
- [ ] Bounded validation, version-conflict feedback and double-submit protection work, including create-clear-replay and concurrent billing-policy updates. A JSON `null` entry for an individual environment currently throws instead of being treated as unprovisioned.
- [x] Existing billing fields, other environments, System Controls and merchant-facing UI remain unaffected.

## Validation

- [ ] Admin-focused server security tests
- [ ] npm run prisma:generate; npm run lint; npm run build
- [ ] Disposable PostgreSQL policy create/update race tests when feasible

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This is a **portable task definition**, `defined but not materialised`: no branches, commits, pushes, claims or worktrees have been created by this artifact. Run `/moda_developer_create ARCH-032-ADMIN-001` after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

## Completion Report

### Status

Changes Requested — Attempt 1 developer self-review found an unhandled JSON `null` environment entry and a non-reproducible database schema dependency. Claim released without incrementing the attempt.

### Files Changed
- `src/app/(protected)/system-controls/platform-policy/page.tsx`
- `src/app/actions/billing-controls.ts`
- `src/app/actions/mcp-execution-policy.ts`
- `src/components/admin/billing-controls.tsx`
- `src/components/admin/mcp-execution-policy/mcp-execution-policy-controls.tsx`
- `src/components/admin/mcp-execution-policy/mcp-execution-policy-fields.tsx`
- `src/lib/admin/billing-control-validation.ts`
- `src/lib/admin/mcp-execution-policy.ts`
- `tests/security/admin-billing-controls.test.mjs`
- `tests/unit/commerce-model-platform-policy-page.test.mjs`
- `tests/unit/mcp-execution-platform-policy.test.mjs`

### Work Completed
- Added an environment-scoped MCP execution policy section to the existing Platform Policy page, visible only to SUPER_ADMIN users.
- Added bounded policy parsing, audited save/clear actions, shared `PlatformBillingPolicy.version` compare-and-swap, and optimistic-conflict handling.
- Added focused tests for authorization, bounds, audit behavior, clear/replay, CAS loss, and preservation of the other environment and billing JSONB.

### Validation Results
- Passed: focused MCP policy and Platform Policy page tests (10 tests).
- Passed: focused Admin billing/security tests (11 tests).
- Passed: `npm run lint` with 0 errors and 1 warning in `database/eslint.config.mjs`.
- Passed: `npm run prisma:generate` and `npm run build`; both used the currently checked-out database submodule at `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Failed: `npm run test:unit` (444/447); two Commerce Model page tests failed existing source expectations and `tests/unit/shopify-taxonomy.test.ts` failed resolving the `@/lib` alias under Node's test runner.
- Failed: `npm test`; failures were in Store Category translation staging and Tenant Directory KPI source expectations, outside the files changed for this task.
- Not run: disposable PostgreSQL race tests. `DATABASE_URL` is configured but was not verified as disposable, so no database writes were attempted.
- Reproducibility gap: the Admin task commit records database gitlink `12c3bee13cabeb3c8b9cb0ac602d836700702413`, whose Prisma schema lacks `PlatformBillingPolicy.mcpExecutionPolicy`. The generated client/build passed only with the uncommitted newer submodule checkout. The pointer was not staged or modified.

### Deviations
The implementation branch has no uncommitted source changes and its implementation commit is pushed. The canonical implementation worktree has a modified `database` submodule checkout at `1397650`; this change is preserved and was not included in the Admin task commit. The parent task branch was clean before this self-review update.

### Assumptions
No assumption was made that the configured `DATABASE_URL` is disposable.

### Unresolved Issues
- `readMcpExecutionPolicy({ schemaVersion: 1, environments: { DEVELOPMENT: null } })` throws `MCP execution policy contains an invalid environment entry.` Treat a null environment entry as unprovisioned and add regression coverage.
- The Admin task branch's recorded database gitlink does not expose the Prisma field required by this implementation. The authorized integration owner must reconcile the submodule revision; the task agent did not stage the gitlink.
- The complete unit/security suites have the failures listed above; determine whether they are pre-existing before attributing them to this task.

### Architectural Concerns
The Admin repository's dependency pointer must resolve to a database revision containing the `mcpExecutionPolicy` field for fresh worktree setup and reproducible Prisma generation/build. Resolve ownership before changing the submodule pointer.

## Developer Self-Review — Changes Requested

### Outcome
Changes Requested for Attempt 1. The scoped UI, server action, shared-row CAS, audit path, and focused tests are present and pushed, but the null-entry acceptance criterion is not met and a clean checkout at the committed database gitlink cannot generate the required Prisma client.

### Required Corrections
- Normalize an individual environment value of JSON `null` to an unprovisioned/absent entry in `readMcpExecutionPolicy`; add tests showing the null and absent forms render as unconfigured and can be provisioned without changing other environments.
- Resolve the database schema revision through the authorized developer/architect integration path. Then initialize the canonical Admin worktree at its recorded gitlink and rerun `npm run prisma:generate`, focused tests, lint, and build; record the exact database commit used. Do not stage or alter the database gitlink without that ownership decision.
- Re-run the full suites after correction and record whether the currently observed failures are baseline or task regressions; do not expand this task to unrelated failures without evidence.

### Review Evidence
- Focused MCP policy/page tests: 10 passed; focused billing/security tests: 11 passed.
- Full unit suite: 444 passed, 3 failed. Full `npm test` reported failures in Store Category translation staging and Tenant Directory KPIs.
- Lint, Prisma generation, and production build passed only with the newer uncommitted database checkout noted above.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-032-ADMIN-001`, branch `task/ARCH-032-ADMIN-001`, implementation commit `25e13e7335b8e2d766e50fdf7abdef11f0d015c2`; parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-032-ADMIN-001`.

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed

### Reviewed Files
None

### Validation Reviewed
None

### Architecture Conformance
Pending

### Follow-up
None

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting. Earlier `depends_on`: `ARCH-032-DATABASE-001`. Earlier `enables`: `ARCH-032-MCP-015`.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-DATABASE-001`. Active `enables`: `ARCH-032-GATEWAY-002`, `ARCH-032-SYSTEM-TEST-002`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Active JSONB platform-policy storage correction

The user directs reuse of the existing `billing.PlatformBillingPolicy` singleton with an optional environment-keyed MCP JSONB field. This active storage/scope decision supersedes earlier references to a new MCP policy model/table or per-environment rows, while preserving the historical task record, review evidence and existing task dependencies. No task is marked Complete by this definition update.

## 2026-10-15 — Dependency Frontier Reconciliation

`ARCH-032-DATABASE-001` completed Attempt 1 with explicit developer completion and accepted review in parent commit `2d3dbcf9`. This task's sole declared dependency is now satisfied. Promote `pending` to `ready`; preserve `attempt: 0`, `executor: null`, and `claimed_at: null`. This is an eligibility update only, not an implementation claim or completion decision.
