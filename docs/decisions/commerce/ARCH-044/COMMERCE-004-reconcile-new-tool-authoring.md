---
id: ARCH-044-COMMERCE-004
architecture_id: ARCH-044
title: Reconcile New Tool authoring and WooCommerce provider-local boundaries
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: []
created: '2026-10-18'
updated: 2026-11-01
---

# Reconcile New Tool authoring and WooCommerce provider-local boundaries

## Architecture

- Parent: `ARCH-044` — `docs/architecture/ARCH-044-commerce-baseline-stabilisation.md`.
- Repository: `moda-interact-commerce` (owner: `moda_commerce`).
- Baseline evidence: unchanged baseline `baseline-vitest.log` compared with ARCH-043 task run `typescript(20261018-183033)` on 2026-10-18. These are external validation artefacts, not committed files.
- Architecture relationship: this repairs pre-existing Commerce issues; it does not change the requirements of `ARCH-043-COMMERCE-002`.

## Objective

Correct seven stale New Tool authoring flow tests and the related WooCommerce Response component-boundary assertion while preserving local draft, validation, navigation, CAS and no-duplicate-write invariants.

## Context

The baseline has **7/35 failures** in `tests/tool-authoring-screen.test.tsx`; most try to click an unavailable `Run Test` for a new Shopify Admin candidate before entering Review or creating a Tool. A separate failing boundary test (`tests/tool-authoring-request-component-boundaries.test.ts`) string-searches `src/studio/tools/new-tool-editor.tsx` for `<WooCommerceRestTest />`, even though the current feature may render the component through a provider-local child. Determine the actual component tree before changing either implementation or assertion.

## Scope

- Inspect `src/studio/tools/new-tool-editor.tsx`, `src/studio/tools/tool-authoring-screen.tsx`, `src/studio/tools/new-tool-authoring-state.ts` and provider-owned Request/Response/Test components, including WooCommerce.
- Rework Test/Review advancement for Shopify Admin new-tool candidates around the current deferred live-Test contract rather than a nonexistent `Run Test` button.
- Preserve local-only edits and navigation, dirty state, stale result protection, confirmation, one exact final create, returned IDs and lost-response reconciliation.
- Reconcile the WooCommerce Response boundary using actual imports/components instead of brittle string matching; only refactor rendering when source proves a boundary violation.

## Out of Scope

- No new provider live-testing capability, plugin/API changes, new cross-service contracts or broad UI design rewrite.
- Do not make Review or final create bypass required validation/auth/tenant controls.

## Requirements

1. New Tool authoring does not persist during setup, tab edits or local tests; only the approved final Create action mutates durable data.
2. A failed/stale/missing required validation cannot unlock a protected Review or final mutation; where live Shopify Test is deferred, requirements must reflect what the current architecture actually supports.
3. Final mutation must be idempotent and reconcile an uncertain result without issuing a second command; navigation must use returned canonical identities.
4. WooCommerce REST Response UI remains owned by its provider component; shared Result Template is reused without provider-specific behavior leaking into the main orchestrator.

## Work Items

- [x] Classify all seven named New Tool failures and identify the obsolete `Run Test` expectation; current tests use the approved deferred Shopify live-Test contract.
- [x] Verify tests reflect deferred live testing and authoritative Request/Response/Result Template validation behavior.
- [x] Verify stale/failed test gates, local draft persistence, Create idempotency and navigation.
- [x] Inspect WooCommerce provider-local component tree; its existing AST boundary assertion matches the actual component hierarchy, so no refactor was warranted.
- [x] Retain and run previously passing New Tool and WooCommerce authoring tests.

## Interfaces / Contracts

Existing `CommerceToolDraftDefinition`/`CommerceToolDefinition`, Tool mutation result and idempotency/operation-ID contracts; current WooCommerce REST Test/Response components; result-template shared stage; no new shared package contract.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [x] All 35 New Tool screen tests pass, including the seven originally failing cases.
- [x] WooCommerce Response component-boundary test passes with assertions reflecting the real component hierarchy.
- [x] Deferred Shopify live Test remains truthful and no obsolete embedded control is recreated.
- [x] No early persistence, no duplicate Create, no loss of dirty draft or incorrect returned identities.
- [x] Neighboring WooCommerce authoring and new-tool state tests remain green.

## Validation

- [x] `npx vitest run tests/tool-authoring-screen.test.tsx tests/tool-authoring-request-component-boundaries.test.ts`.
- [x] `npx vitest run tests/new-tool-authoring-state.test.ts tests/woocommerce-rest-response-authoring.test.tsx tests/woocommerce-rest-review-workflow.test.tsx tests/tool-authoring-session.test.ts`.
- [x] `npm run prisma:generate && npm run typecheck`, changed-file ESLint and `git diff --check` (results recorded below, including unrelated diagnostics).

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

In the baseline the failed boundary assertion expected literal `<WooCommerceRestTest />` inside `new-tool-editor.tsx`. A literal source-string test is not proof of runtime ownership; a focused component import/render test may better enforce the architectural boundary.

### Exact unchanged-baseline failures (7)

- `does not unlock the first Review step after a failed Test`
- `does not unlock the first Review step after a stale Test`
- `preserves edited local definition values through tab switches`
- `validates and creates the exact current Admin candidate without intermediate persistence`
- `uses exact returned identities after confirmed creation`
- `reconciles a lost final create without replaying the mutation`
- `cancels from Review without writing and returns to Tools`

## Completion Report

### Status

Complete — Attempt 1. Architect acceptance is recorded. Focused authoring and
provider-boundary suites pass; the typecheck's unrelated TS2345 error and the
existing focused-lint warning are documented and do not block this task.

### Files Changed

No implementation source or test files changed in this attempt. The current task branch already contains the deferred-test assertions, the seven named authoring flow cases, and the AST-based WooCommerce provider-local boundary check. This task file is the only intended change for this attempt.

### Work Completed

Confirmed the seven named New Tool failures are covered by current tests: failed/stale Request validation cannot unlock Review; local definition edits survive tab changes; exact current Admin candidate is created only after validation; canonical returned IDs drive navigation; lost Create responses reconcile without replay; and cancellation returns to Tools without writes. The Test step explicitly states Shopify Admin live tests are deferred and contains no `Run Test` control.

Inspected the actual WooCommerce component tree. `NewToolEditor` imports and renders `WooCommerceRestResponse`, `WooCommerceRestTest`, and `WooCommerceRestReviewCards`; `ToolAuthoringScreen` does not import/render the provider components. The existing TypeScript AST boundary test checks these imports/render sites and shared Result Template reuse, so no brittle source-string correction or implementation refactor was needed.

### Validation Results

Environment: Darwin/x64; `.nvmrc` selected Node `v24.19.0`, npm `11.17.0`; npm package manager. `npm ci` passed and installed 905 packages (npm reported 44 audit findings: 27 moderate, 16 high, 1 critical; no dependency changes were made).

| Command | Result |
|---|---|
| `npx vitest run tests/tool-authoring-screen.test.tsx tests/tool-authoring-request-component-boundaries.test.ts` | PASS, 2 files, 42 tests. |
| `npx vitest run tests/new-tool-authoring-state.test.ts tests/woocommerce-rest-response-authoring.test.tsx tests/woocommerce-rest-review-workflow.test.tsx tests/tool-authoring-session.test.ts` | PASS, 4 files, 40 tests. |
| `npm run prisma:generate && npm run typecheck` | Prisma generation PASS; typecheck FAIL with one unrelated TS2345 at `tests/system-commerce-tool-sync.test.ts:305`: `{}` omits required `NODE_ENV` from Next.js `ProcessEnv`. |
| Focused `npx eslint` over New Tool editor/screen/state, WooCommerce Request/Response/Test components and the six focused tests | 0 errors; 1 warning in `src/studio/tools/new-tool-editor.tsx:248` (`selectedShop` defined but never used). |
| `git diff --check` | PASS; implementation worktree has no source changes. |

The seven named screen cases passed as part of the 35-test `tool-authoring-screen.test.tsx` suite; the combined primary command also ran the seven component-boundary tests. No full repository suite was run for this bounded task.

### Worktree / Synchronisation Evidence

Launcher-prepared canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-044-COMMERCE-004`, branch `task/ARCH-044-COMMERCE-004`, initial synchronized head `62bd8f77ba2896a1d94009af4a963f16a1f91b25`, claim commit `b49f1c920e17f58f14a9d0de8c8c6093771f750c`. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-044-COMMERCE-004`, branch `task/ARCH-044-COMMERCE-004`, head `15d505ef0f84e8cab57af43dee0d78a83d969f93`; recursive submodule sync/update passed and `database` was initialized at `af77c594ecbfc78c26d01c0021a090830884bbff`. Dependency gate passed; no task dependencies.

### Deviations

No source or test edit was necessary because the task's required behavior and regression assertions are already present on the prepared mainline snapshot and all focused suites pass. Standalone typecheck remains blocked by the documented unrelated `ProcessEnv` test typing diagnostic; targeted ESLint reports one existing unused-variable warning.

### Assumptions

The unchanged-baseline test identities describe issues already reconciled in the current prepared Commerce snapshot; this attempt revalidated that state rather than recreating the historical failures.

### Unresolved Issues

The repository-wide typecheck remains non-green due to `tests/system-commerce-tool-sync.test.ts:305`, outside this task. Focused ESLint retains one unused `selectedShop` warning in the existing New Tool editor; no new warning was introduced by this attempt.

### Architectural Concerns

Report new cross-service contracts, database schema/owner changes, secret handling issues, or deployment requirements to `moda_architect` without expanding scope.

## Architect Review

### Review Status

Accepted — Attempt 1. With `completion_mode: automatic`, the task transitions
to `status: complete`; executor and claim are clear, and Attempt 1 is preserved.

### Review Notes

The focused authoring and boundary requirements are satisfied: the seven
baseline failures are covered under the deferred Shopify live-Test contract,
Create remains gated on current validation and preserves idempotency/returned
identities, and the WooCommerce provider boundary test reflects the actual AST
component tree. The reported typecheck failure is the unchanged, unrelated
`ProcessEnv` diagnostic in `tests/system-commerce-tool-sync.test.ts:305`; no
implementation source changed in this task. The single ESLint warning is an
existing unused `selectedShop` in `new-tool-editor.tsx`.

### Reviewed Files

- `tests/tool-authoring-screen.test.tsx`
- `tests/tool-authoring-request-component-boundaries.test.ts`
- `tests/new-tool-authoring-state.test.ts`
- `tests/woocommerce-rest-response-authoring.test.tsx`
- `tests/woocommerce-rest-review-workflow.test.tsx`
- `tests/tool-authoring-session.test.ts`
- Relevant New Tool and WooCommerce provider-owned source component hierarchy.
- The Completion Report and validation evidence.

### Validation Reviewed

- Primary UI and component-boundary run: 42 tests passed across two files.
- State, WooCommerce authoring and session regression run: 40 tests passed
  across four files.
- Prisma generation and changed-file ESLint passed; ESLint reports one
  existing unused-variable warning. Typecheck completed with the documented
  unrelated TS2345 diagnostic.
- Implementation worktree is clean at `15d505e`; the task branch ref is
  published. Parent task branch is clean and synchronized at `7781eda5` before
  this review overlay. `git diff --check` passed.

### Architecture Conformance

Conforms to ARCH-044: deferred Shopify live testing remains explicit; local
validation gates and exact final Create semantics remain intact; WooCommerce
REST Response/Test components remain provider-owned. No production source or
cross-service contract changed.

### Follow-up

Accepted and Complete at Attempt 1. The documented typecheck diagnostic and
existing lint warning are outside this task and do not undermine the focused
acceptance evidence. No task depends on or is enabled by this task, so no
dependency status changed.
