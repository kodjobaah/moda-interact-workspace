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
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-11-01T16:45:17Z
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

- [ ] Classify all seven named New Tool failures and identify the common legacy `Run Test` helper.
- [ ] Amend tests to current, explicitly approved deferred-test and authoritative validation behavior.
- [ ] Verify stale/failed test gates, local draft persistence, Create idempotency and navigation.
- [ ] Inspect WooCommerce provider-local component tree and correct the single boundary assertion or true implementation drift.
- [ ] Retain all previously passing New Tool and WooCommerce authoring tests.

## Interfaces / Contracts

Existing `CommerceToolDraftDefinition`/`CommerceToolDefinition`, Tool mutation result and idempotency/operation-ID contracts; current WooCommerce REST Test/Response components; result-template shared stage; no new shared package contract.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [ ] All 35 New Tool screen tests pass, including the seven originally failing cases.
- [ ] WooCommerce Response component-boundary test passes with assertions reflecting the real component hierarchy.
- [ ] Deferred Shopify live Test remains truthful and no obsolete embedded control is recreated.
- [ ] No early persistence, no duplicate Create, no loss of dirty draft or incorrect returned identities.
- [ ] Neighboring WooCommerce authoring and new-tool state tests remain green.

## Validation

- [ ] `npx vitest run tests/tool-authoring-screen.test.tsx tests/tool-authoring-request-component-boundaries.test.ts`.
- [ ] `npx vitest run tests/new-tool-authoring-state.test.ts tests/woocommerce-rest-response-authoring.test.tsx tests/woocommerce-rest-review-workflow.test.tsx tests/tool-authoring-session.test.ts`.
- [ ] `npm run typecheck`, changed-file ESLint, `git diff --check`.

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
