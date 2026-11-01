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
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-18'
updated: '2026-10-18'
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

- [ ] Classify each of the 19 failing named tests as stale UI expectation or real behavior defect (record mapping in Completion Report).
- [ ] Replace shared `startShopifyAdminTest()`/related fixtures with current supported validation/review behavior.
- [ ] Reconcile affected Admin mapping, result-schema, CAS, role and Policy Operation assertions.
- [ ] Preserve green tests among the original 43 and add regression coverage for deliberate live-Test deferral.
- [ ] Fix production UI only where a new test demonstrates a genuine regression.

## Interfaces / Contracts

Shopify Admin GraphQL schema artifact `admin-2026-07.json`, persisted `Tool`/`ToolRevision`, CAS tokens, studio role gates, deferred standalone MCP live-Test boundary. Existing shared tool-definition contracts remain authoritative.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [ ] All 43 tests in `tests/shopify-admin-tools-ui.test.tsx` pass without an embedded `Run Test` control.
- [ ] The 19 originally failing cases each have an explicit resolution in the Completion Report, including Policy Operation ones.
- [ ] Deferred Test state is visibly truthful; no live network/provider execution is introduced.
- [ ] CAS, role, no-replay/no-double-write and preservation of unsaved mappings are covered.
- [ ] No regressions in `tests/shopify-admin-authoring-validation.test.ts` and nearby persisted-editor tests.

## Validation

- [ ] `npx vitest run tests/shopify-admin-tools-ui.test.tsx`.
- [ ] `npx vitest run tests/shopify-admin-authoring-validation.test.ts tests/persisted-shopify-admin-tool-editor.test.tsx tests/admin-graphql-compiler.test.ts tests/policy-operation-live-test-action.test.ts`.
- [ ] `npm run typecheck`, changed-file ESLint, `git diff --check`.
- [ ] Record the 19 original failing test names versus corrected behavior.

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

Not Started

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run. Record each exact command, environment, exit code, test totals and any known-baseline differences. Baseline failures may not be silently treated as task successes.

### Worktree / Synchronisation Evidence

Not yet materialised. Record launcher-resolved canonical workspace root, dedicated parent and implementation worktrees, initial branch/commit identities and recursive submodule state when execution begins.

### Deviations

None yet.

### Assumptions

Task definition based on the 2026-10-18 source snapshot and supplied baseline/task logs; re-inspect current implementation when executing.

### Unresolved Issues

None beyond the explicitly described diagnostics to investigate.

### Architectural Concerns

Report new cross-service contracts, database schema/owner changes, secret handling issues, or deployment requirements to `moda_architect` without expanding scope.

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
