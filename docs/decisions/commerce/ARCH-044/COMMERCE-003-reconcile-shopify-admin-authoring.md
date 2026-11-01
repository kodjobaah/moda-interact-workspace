---
id: ARCH-044-COMMERCE-003
architecture_id: ARCH-044
title: Reconcile persisted Shopify Admin Tool authoring with MCP-extracted architecture
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
attempt: 1
depends_on: []
enables: []
created: '2026-10-18'
updated: 2026-11-01
---

# Reconcile persisted Shopify Admin Tool authoring with MCP-extracted architecture

## Architecture

- Parent: `ARCH-044` — `docs/architecture/ARCH-044-commerce-baseline-stabilisation.md`.
- Repository: `moda-interact-commerce` (owner: `moda_commerce`).
- Baseline evidence: unchanged baseline `baseline-vitest.log` compared with ARCH-043 task run `typescript(20261018-183033)` on 2026-10-18. These are external validation artefacts, not committed files.
- Architecture relationship: this repairs pre-existing Commerce issues; it does not change the requirements of `ARCH-043-COMMERCE-002`.

## Objective

Make persisted Shopify Admin GraphQL and Policy Operation authoring tests accurately validate supported current UI behavior, fixing real defects while retiring obsolete embedded live-Shopify-test expectations.

## Context

The unchanged baseline reports **19 failures out of 43 tests** in `tests/shopify-admin-tools-ui.test.tsx`. Many test helpers demand `screen.getByRole("button", { name: "Run Test" })`, but the actual Test tab visibly states: `Live Shopify Admin tests are deferred until standalone MCP integration is restored.` The UI still supports Tool Definition, Request, Response, Result Template, Test and Review and validates Shopify schemas, mappings and review state. Several failures involve Save/Review CAS and separate Policy Operation publishing, so they must be investigated independently rather than all dismissed as one deleted button.

## Scope

- Inspect `src/studio/tools/authoring/persisted-shopify-admin-tool-editor.tsx`, `src/studio/tools/authoring/tool-authoring-tabs.tsx`, its controller, current Shopify Admin validation actions, and architecture `ARCH-032-COMMERCE-005`/MCP extraction decisions.
- Rewrite obsolete `Run Test`, C082, offline-session and live-test status expectations to assert the supported deferred Test tab, authoritative local validation, save/publish permissions and correct navigation.
- Preserve tested behavior for draft Save, stable IDs, CAS conflict/no-overwrite, stale-request rejection, mapping validity, derived result contract, role permissions and Policy Operation publication; correct production code only for proven defects.
- Do **not** re-enable embedded MCP or a live Shopify test path merely to satisfy old tests.

## Out of Scope

- No standalone MCP live execution implementation, provider credential changes, Shared contract changes or new Shopify ingress features.
- No replacement of specific behavior tests with vacuous snapshots or skipping entire suites.

## Requirements

1. Shopify Admin live Test remains intentionally deferred at the current Commerce UI boundary until approved standalone MCP integration exists; tests must not expect `Run Test` or C082 where unavailable.
2. Authoring still validates server-side and remains safe against stale state and duplicate mutations; role-gated publication remains enforced.
3. Tests for persisted Admin and Policy Operation flows must distinguish `Validate`, `Save draft`, `Review` and `Publish`, with no bogus current-live-test requirement when deferred.
4. If a failure exposes a genuine CAS/persistence regression, fix it with a focused test; do not remove safeguards to make an assertion pass.

## Work Items

- [x] Classify each of the 19 failing named tests as stale UI expectation or real behavior defect (record mapping in Completion Report).
- [x] Replace shared `startShopifyAdminTest()`/related fixtures with current supported validation/review behavior.
- [x] Reconcile affected Admin mapping, result-schema, CAS, role and Policy Operation assertions.
- [x] Preserve green tests among the original 43 and add regression coverage for deliberate live-Test deferral.
- [x] Fix production UI only where a new test demonstrates a genuine regression.

## Interfaces / Contracts

Shopify Admin GraphQL schema artifact `admin-2026-07.json`, persisted `Tool`/`ToolRevision`, CAS tokens, studio role gates, deferred standalone MCP live-Test boundary. Existing shared tool-definition contracts remain authoritative.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [x] All 43 tests in `tests/shopify-admin-tools-ui.test.tsx` pass without an embedded `Run Test` control.
- [x] The 19 originally failing cases each have an explicit resolution in the Completion Report, including Policy Operation ones.
- [x] Deferred Test state is visibly truthful; no live network/provider execution is introduced.
- [x] CAS, role, no-replay/no-double-write and preservation of unsaved mappings are covered.
- [x] No regressions in `tests/shopify-admin-authoring-validation.test.ts` and nearby persisted-editor tests.

## Validation

- [x] `npx vitest run tests/shopify-admin-tools-ui.test.tsx` — PASS, exit 0; 1 file, 45 tests passed (Node 24.19.0).
- [x] `npx vitest run tests/shopify-admin-tools-ui.test.tsx tests/shopify-admin-authoring-validation.test.ts tests/persisted-shopify-admin-tool-editor.test.tsx tests/admin-graphql-compiler.test.ts tests/policy-operation-live-test-action.test.ts` — PASS, exit 0; 5 files, 74 tests passed (Node 24.19.0).
- [ ] `npm run typecheck` — Next schema sync and route type generation completed, then the TypeScript process produced no output for several minutes. It was interrupted (exit 130). A direct `npx tsc --noEmit --pretty false --diagnostics` retry behaved the same and was interrupted (exit 130); typecheck is unverified.
- [x] `npx eslint tests/shopify-admin-tools-ui.test.tsx` — PASS, exit 0.
- [x] `git diff --check` — PASS, exit 0.
- [x] Prisma setup required by Vitest: `npx prisma generate --schema database/prisma/schema.prisma` — PASS, generated Prisma Client v6.19.3.

The first Vitest startup attempt could not load the ungenerated Prisma client; after generation, both required test commands passed. The test worktree was otherwise clean and the schema sync produced no tracked change.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

The current Test panel is deliberately deferred (evidence from baseline Testing Library DOM). Do not equate a green historical test with an approved ability to execute live Shopify GraphQL from embedded Commerce. If standalone MCP is separately restored, that belongs to its existing architecture and dependent task, not this stabilisation patch.

### Exact unchanged-baseline failures (19)

- `offers Admin GraphQL and saves the exact validated definition`
- `requires a current Shopify Test for Save and shows the exact server-rendered result without writes`
- `stales a successful Shopify Test when arguments change without persisting the transient edit`
- `does not call C082 when no Studio shop is selected`
- `disables Shopify Test when the selected shop has no offline session`
- `marks a failed C082 stage FAILED and never exposes a passed rendered result`
- `prevents an old run from resurfacing after shop and arguments both cycle A-to-B-to-A`
- `saves once with the current CAS token and refreshes from the canonical revision`
- `keeps a Shopify CAS conflict visible without refreshing or overwriting local edits`
- `persists editable JSON string and numeric literal mappings`
- `recomputes aggregate validity when a literal mapping switches to an input mapping`
- `keeps another invalid literal mapping invalid while fixing one literal`
- `ignores invalid literal state for variables removed from the current document`
- `derives and displays a read-only result shape without saving a persisted draft`
- `does not accept an old Shopify Review validation after candidate A-to-B-to-A`
- `saves the compiler-produced schema while preserving the persisted response template`
- `keeps Admin publication disabled for ADMIN and surfaces the typed live-test gate for SUPER_ADMIN`
- `saves, publishes through the canonical action, and reopens the exact Policy binding read-only`
- `preserves Policy local edits on CAS conflict and unknown mutation outcome without retrying`

## Completion Report

### Status

Ready for architect review. The requested UI and related regression suites pass. TypeScript validation remains unverified because both attempts remained silent after route type generation and were stopped; this limitation is recorded above.

### Files Changed

No implementation files needed changes in this attempt. The task's reconciled behavior and regression cases were already present at implementation start commit `15d505ef0f84e8cab57af43dee0d78a83d969f93`; the required suites confirm the current snapshot. This attempt changes only this task report.

### Work Completed

Inspected the persisted Shopify Admin editor, authoring tabs/controller, validation actions, and Policy Operation authoring and publication tests. Confirmed the Admin Test surface is intentionally deferred, local authoritative validation and mapping/result-contract checks remain available, and save/review/publish and Policy Operation behavior remain covered.

The current `tests/shopify-admin-tools-ui.test.tsx` contains 45 tests (the task's original count was 43); all pass. The 19 exact unchanged-baseline failures map to the current coverage as follows:

1. `offers Admin GraphQL and saves the exact validated definition` → current test of the same name; it validates and derives the local candidate, asserts deferred Test, and saves the exact definition.
2. `requires a current Shopify Test for Save and shows the exact server-rendered result without writes` → `requires a current result contract for Save and never invokes the deferred live Test`; Save remains gated by the current result contract, and the live provider action is not called.
3. `stales a successful Shopify Test when arguments change without persisting the transient edit` → `invalidates the current result contract when the Request changes without writes or a live Test`; Request edits stale the result contract and do not write or invoke a provider.
4. `does not call C082 when no Studio shop is selected` → `defers live Shopify Test even when no Studio shop is selected`.
5. `disables Shopify Test when the selected shop has no offline session` → `does not expose embedded Shopify Test even with a shop lacking an offline session`.
6. `marks a failed C082 stage FAILED and never exposes a passed rendered result` → `never invokes the removed C082 provider action or displays a provider result`.
7. `prevents an old run from resurfacing after shop and arguments both cycle A-to-B-to-A` → `keeps deferred Shopify Test inert across shop and Request A-to-B-to-A changes`.
8. `saves once with the current CAS token and refreshes from the canonical revision` → current test of the same name; it asserts the current edit version, single save per action, and canonical returned revision.
9. `keeps a Shopify CAS conflict visible without refreshing or overwriting local edits` → current test of the same name; conflict remains visible and local edits remain intact.
10. `persists editable JSON string and numeric literal mappings` → current test of the same name; both literal forms are saved.
11. `recomputes aggregate validity when a literal mapping switches to an input mapping` → current test of the same name; mapping validity follows the selected input mapping.
12. `keeps another invalid literal mapping invalid while fixing one literal` → current test of the same name; one correction does not mask another invalid mapping.
13. `ignores invalid literal state for variables removed from the current document` → current test of the same name; removed variables no longer affect current mapping validity.
14. `derives and displays a read-only result shape without saving a persisted draft` → current test of the same name; derivation displays the shape without draft writes.
15. `does not accept an old Shopify Review validation after candidate A-to-B-to-A` → current test of the same name; stale validation cannot authorize the current candidate.
16. `saves the compiler-produced schema while preserving the persisted response template` → current test of the same name.
17. `keeps Admin publication disabled for ADMIN and surfaces the typed live-test gate for SUPER_ADMIN` → `enforces ADMIN publication permissions and reports the standalone MCP live-test gate to SUPER_ADMIN`.
18. `saves, publishes through the canonical action, and reopens the exact Policy binding read-only` → current test of the same name.
19. `preserves Policy local edits on CAS conflict and unknown mutation outcome without retrying` → current test of the same name; local edits survive, and the mutation is not retried.

Policy Operation's supported local simulated Test remains distinct from the deferred embedded Shopify Admin provider test. No live Shopify provider path was introduced.

### Validation Results

- `npx vitest run tests/shopify-admin-tools-ui.test.tsx`: PASS, 45 tests.
- Required combined regression command: PASS, 74 tests across five files.
- `npx eslint tests/shopify-admin-tools-ui.test.tsx`: PASS.
- `git diff --check`: PASS.
- `npm run typecheck`: interrupted after Next route type generation stalled without further output; no PASS claimed. Direct TypeScript retry was also interrupted after no output.

### Worktree / Synchronisation Evidence

Launcher preparation packet:
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-044-COMMERCE-003`, branch `task/ARCH-044-COMMERCE-003`, prepared HEAD `d70081a49fdd91a85336d303fcac75502e42eea7`.
- Parent claim commit `e6b328e1a30000df724c49d59e079cede524174d` was committed and pushed by the launcher.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-044-COMMERCE-003`, branch `task/ARCH-044-COMMERCE-003`, HEAD `15d505ef0f84e8cab57af43dee0d78a83d969f93`; clean at completion.
- Parent and implementation origin/main were already current; no remote task branch existed at preparation. The shared canonical checkout and shared implementation source checkout were not switched or edited; no other task worktree was reused.
- Recursive `git submodule sync --recursive` and `git submodule update --init --recursive` passed. The initialized `database` submodule was at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- Isolated implementation dependency install used `npm ci --ignore-scripts`; Prisma client generation used the initialized schema submodule.

### Deviations

No source edits were made because the requested reconciled UI and test coverage were already present in the prepared implementation snapshot. Typecheck could not be verified; both attempts were stopped after extended silence, and are not reported as passing.

### Assumptions

The prepared implementation snapshot is the authoritative current source; the task's 2026-10-18 baseline is historical evidence and does not override current behavior.

### Unresolved Issues

TypeScript validation remains unverified because the command stalled without output after Next route type generation.

### Architectural Concerns

None. No cross-service contracts, provider credential behavior, or live Shopify execution paths changed.

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation evidence.

### Reviewed Files

None yet.

### Validation Reviewed

None yet.

### Architecture Conformance

Not assessed.

### Follow-up

None yet.
