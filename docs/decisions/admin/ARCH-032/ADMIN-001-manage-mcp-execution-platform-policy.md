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
status: complete
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
- [x] Bounded validation, version-conflict feedback and double-submit protection work, including create-clear-replay and concurrent billing-policy updates. A JSON `null` entry for an individual environment is treated as unprovisioned and can be provisioned without changing other environments.
- [x] Existing billing fields, other environments, System Controls and merchant-facing UI remain unaffected.

## Validation
- [x] Admin-focused server security tests
- [x] `npm run prisma:generate`, `npm run lint`, and `npm run build`
- [ ] Disposable PostgreSQL policy create/update race tests when feasible; not run because no database was verified as disposable.

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This task is materialised on `task/ARCH-032-ADMIN-001`; canonical parent and implementation worktrees are recorded in the Completion Report. It completed at Attempt 1 after explicit developer-as-architect acceptance; no new attempt was claimed. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

## Completion Report

### Status

Complete — Attempt 1 was accepted by the developer-as-architect on 2026-10-15 following the explicit direction `Architect Review Accepted`. The null-entry and reproducibility corrections are present in the published implementation branch. No attempt increment, merge to `main`, or implementation-branch change was made for this completion record.

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
- `database` (submodule gitlink aligned to DATABASE-001 commit `139765042baad3901682cfe9c54a3d6bba73e75c`)

### Work Completed
- Added an environment-scoped MCP execution policy section to the existing Platform Policy page, visible only to SUPER_ADMIN users.
- Added bounded policy parsing, audited save/clear actions, shared `PlatformBillingPolicy.version` compare-and-swap, and optimistic-conflict handling.
- Added focused tests for authorization, bounds, audit behavior, clear/replay, CAS loss, and preservation of the other environment and billing JSONB.
- Normalize an individual environment's JSON `null` value to an unprovisioned entry; focused tests verify null/absent rendering and saving that environment while preserving other entries.
- Align the Admin task branch's `database` gitlink to completed DATABASE-001 commit `139765042baad3901682cfe9c54a3d6bba73e75c`, which contains `PlatformBillingPolicy.mcpExecutionPolicy`.

### Validation Results
- Passed: focused MCP policy and Platform Policy page tests after correction (12 tests).
- Passed: focused Admin billing/security tests (11 tests).
- Passed: `npm run lint` with 0 errors and 1 warning in `database/eslint.config.mjs`.
- Passed: `npm run prisma:generate`, `npm run prisma:validate`, and `npm run build` from the committed database gitlink at `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Earlier Attempt 1 review, before the correction commit: `npm run test:unit` reported 444/447; two Commerce Model page tests failed source expectations and `tests/unit/shopify-taxonomy.test.ts` failed resolving the `@/lib` alias under Node's test runner.
- Earlier Attempt 1 review, before the correction commit: `npm test` failed in Store Category translation staging and Tenant Directory KPI source expectations, outside the files changed for this task.
- Not run: disposable PostgreSQL race tests. No database was verified as disposable, so no database writes were attempted. Accepted as a non-blocking validation limitation in the explicit review.
- Correction verification: current full unit suite is 446/449; the same three unrelated failures remain (two Commerce Model page source expectations and `@/lib` resolution in Shopify taxonomy). The broad `npm test` failures remain in unrelated Store Category translation staging and Tenant Directory KPI source expectations.
- Resolved reproducibility gap: implementation HEAD `7c50c1bf99a539877a618078a2f2cb52f678066b` records database gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`; Prisma generation, validation and production build pass using this committed revision.

### Deviations
The follow-up implementation commit is pushed on the canonical implementation task branch. The database submodule revision is now an intentional committed gitlink change, not an uncommitted worktree modification. No implementation changes were made during this reconciliation.

### Assumptions
No assumption was made that the configured `DATABASE_URL` is disposable.

### Unresolved Issues
- Accepted non-blocking residuals: full unit and broad security/observability commands still report failures in unrelated Commerce Model, Shopify taxonomy alias resolution, Store Category translation staging, and Tenant Directory KPI expectations; these were not changed by this task.
- Accepted validation limitation: disposable PostgreSQL race coverage was not run because no database target was verified as disposable.

### Architectural Concerns
The database dependency pointer is resolved to DATABASE-001 commit `139765042baad3901682cfe9c54a3d6bba73e75c`; Prisma generation, validation and the production build passed from that committed schema.

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

## 2026-10-15 — Follow-up correction evidence (before explicit completion)

- The published implementation branch advanced to `7c50c1bf99a539877a618078a2f2cb52f678066b`. The commit normalizes JSON `null` environment entries, adds regression tests for null/absent rendering and provisioning, and records database gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Focused MCP policy and Platform Policy page tests pass 12/12; focused Admin billing/security tests pass 11/11.
- `npm run prisma:generate`, `npm run prisma:validate`, `npm run lint` (0 errors, 1 warning), and `npm run build` pass against the committed schema revision.
- Full unit suite passes 446/449 with the previously identified unrelated failures. Broad `npm test` still fails in unrelated Store Category translation staging and Tenant Directory KPI expectations. Disposable PostgreSQL tests remain unrun because no target was verified as disposable.
- At the time this evidence was recorded, no Attempt 2 claim or completion decision had been made; the lifecycle was Ready at Attempt 1. The subsequent acceptance and completion are recorded below.

## Developer Self-Review — Accepted

### Reviewed Attempt

Attempt 1, developer execution. Review date: 2026-10-15. Explicit acceptance direction: `Architect Review Accepted`.

### Acceptance

The implementation satisfies the four Acceptance Criteria. The JSON `null` environment correction is covered by tests for null/absent rendering and provisioning; the committed database gitlink resolves the Prisma schema required for clean generation. The focused policy/page and security tests, Prisma validation/generation, lint and production build passed. The unrelated broad-suite failures and unrun disposable PostgreSQL tests are accepted non-blocking residuals as documented in the Completion Report.

### Evidence

- Implementation branch `task/ARCH-032-ADMIN-001` is published at `7c50c1bf99a539877a618078a2f2cb52f678066b` and clean; database gitlink is `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Parent task branch `task/ARCH-032-ADMIN-001` was clean/published at `d0d6d851fd70dd21b87b5ba2a28efc96e24f609a` before this completion update.
- Focused policy/page tests passed 12/12; focused Admin billing/security tests passed 11/11. `npm run prisma:generate`, `npm run prisma:validate`, `npm run lint` (0 errors, 1 warning), and `npm run build` passed.
- Broad unit/security suite failures are limited to unrelated Commerce Model, Shopify taxonomy alias, Store Category translation and Tenant Directory KPI tests. No disposable database target was verified, so PostgreSQL race tests were not run.

## Developer Completion Decision

On 2026-10-15, the developer explicitly invoked completion with the direction `Architect Review Accepted`. The accepted review and developer completion authority are recorded for Attempt 1. No implementation merge or push to `main` was made.

### State Transition

`status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`.

### Dependency Frontier

- `ARCH-032-GATEWAY-002` remains `blocked`; its explicit operational hold and remaining dependencies are unchanged.
- `ARCH-032-SYSTEM-TEST-002` remains `pending` because its other implementation dependencies are incomplete.
- No downstream status was promoted or otherwise changed.

## Architect Review

### Review Status
Accepted — 2026-10-15, per the developer's explicit direction `Architect Review Accepted`.

### Review Notes
The corrected implementation satisfies the task acceptance criteria. The two validation residuals listed in the Completion Report are accepted as non-blocking: broad-suite failures are outside this task's changed surfaces, and a disposable PostgreSQL target was not verified.

### Reviewed Files
Implementation files listed in the Completion Report, including the MCP policy parser/action/UI/tests and the committed database gitlink.

### Validation Reviewed
Focused policy/page tests 12/12; focused Admin billing/security tests 11/11; Prisma generation and validation, lint (zero errors, one warning), production build, and implementation diff check passed. Full unit suite remains 446/449 with three unrelated failures; disposable PostgreSQL tests were not run because no safe target was verified.

### Architecture Conformance
Conforms to the accepted scope: reuses the existing `PlatformBillingPolicy` singleton and shared version CAS, with no new policy model/table or merchant-facing changes.

### Follow-up
No further ADMIN-001 implementation is required. Gateway-002 remains `blocked` under its operational cutover hold and other dependencies; SYSTEM-TEST-002 remains `pending` on its remaining implementation dependencies. Neither downstream status was changed.

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting. Earlier `depends_on`: `ARCH-032-DATABASE-001`. Earlier `enables`: `ARCH-032-MCP-015`.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-DATABASE-001`. Active `enables`: `ARCH-032-GATEWAY-002`, `ARCH-032-SYSTEM-TEST-002`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Active JSONB platform-policy storage correction

The user directs reuse of the existing `billing.PlatformBillingPolicy` singleton with an optional environment-keyed MCP JSONB field. This active storage/scope decision supersedes earlier references to a new MCP policy model/table or per-environment rows, while preserving the historical task record, review evidence and existing task dependencies. No task is marked Complete by this definition update.

## 2026-10-15 — Dependency Frontier Reconciliation (before explicit completion)

At the time of this reconciliation, `ARCH-032-DATABASE-001` had completed Attempt 1 with explicit developer completion and accepted review in parent commit `2d3dbcf9`. This task's sole declared dependency was satisfied, so its then-current `pending` state was promoted to `ready`, preserving `attempt: 0`, `executor: null`, and `claimed_at: null`. This historical eligibility update preceded the Attempt 1 implementation and the explicit completion decision recorded above; the current authoritative lifecycle is Complete.
