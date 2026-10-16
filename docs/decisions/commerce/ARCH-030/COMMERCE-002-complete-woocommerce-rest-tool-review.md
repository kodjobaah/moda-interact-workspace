---
id: ARCH-030-COMMERCE-002
architecture_id: ARCH-030
title: Complete WooCommerce REST tool Review and Save
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-030-COMMERCE-001
enables: []
created: 2026-10-14
updated: 2026-10-16
---

# Complete WooCommerce REST tool Review and Save

## Architecture

`ARCH-030` — `docs/architecture/ARCH-030-woocommerce-commerce-tool-authoring.md`. Coordinator: `moda_architect`.

## Objective

Replace the WooCommerce Review placeholder with an accurate final review and a working Save-draft action for the tested WooCommerce tool.

## Context

`src/studio/tools/authoring/review/woocommerce-rest-review-summary.tsx` is a placeholder. The Woo authoring state currently has no persistable provider definition, and `src/commerce/tool-definition/contracts.ts` does not accept Woo as an execution kind. A summary-only screen would leave the wizard incomplete, so this task must connect authoring fields to the existing Commerce draft-saving contract within Commerce ownership.

## Scope

Only `moda-interact-commerce`: provider-specific Review summary, Woo draft-definition assembly/validation and Commerce-owned draft Save integration, plus focused tests. Build on the tested draft and navigation produced by COMMERCE-001.

## Out of Scope

New store GET transport, changing the Test execution behaviour, Woo write operations, API/Shared/Gateway/Database/WordPress plugin work, merchant Studio access, publishing/activation, and production Background/MCP execution. Do not broaden the Commerce persisted schema into a new cross-service published runtime promise.

## Requirements

1. Show the selected authorized WooCommerce store; Tool name/display name/description/version; chosen read resource/method; configured path, fixed and agent-input parameters; input schema; Response projection and output schema; Result Template; and current last-test status. Bound displayed content and do not expose credential material or raw sensitive test payloads.
2. Verify the current Woo request, response and template, validate input/result schema consistency and construct a deterministic WooCommerce tool *draft* using only the existing Commerce-owned fields. Reuse existing authoring validators; reject unsupported fields rather than coercing silently.
3. Integrate WooCommerce draft Save with the existing `createToolWithInitialDraft`-style Commerce workflow, including provider-specific Commerce-local draft schema support where needed. The Save action must actually persist an editable Woo draft and return its identity; never present an in-memory-only success message.
4. Save must remain disabled when the current store-specific Test is missing, failed or stale, when fields are invalid, or while a Save is pending. Server-side enforcement must re-check identity, authorization, draft validation and server-verifiable, current-store/canonical-draft test proof from COMMERCE-001 rather than relying only on browser navigation state.
5. Display server validation, conflict and save errors inline, prevent double-click/duplicate record creation, allow returning to edit, and keep the unsaved draft intact on failure.
6. A saved Woo draft is not automatically published or executable by production agent runtimes; keep publish/activation disabled or explicitly unavailable until separately implemented and approved. No new cross-repository tasks are part of this scope.

## Work Items

- [x] Implement the WooCommerce Review cards using canonical authoring state and selected Shop.
- [x] Build and validate persistable WooCommerce Commerce-local draft structure without duplicating the Request/Response editors.
- [x] Wire the existing Commerce draft Save workflow, server-side authorization/validation and duplicate-submit protection.
- [x] Add UI and persistence tests for success, stale Test, validation failure, retries, duplicate click and navigation back to edits.

## Interfaces / Contracts

Consumes COMMERCE-001 current-store Test state, server-verifiable expiring test proof, and WooCommerce Request/Response/template drafts. Produces a Commerce tool draft via existing Commerce persistence; no Shared package, external API contract or production runtime publication is created.

## Dependencies

- `ARCH-030-COMMERCE-001` must be architect-accepted and Complete before execution.

## Enables

None within ARCH-030; production runtime and merchant Studio work are separate initiatives.

## Acceptance Criteria

- [x] Review accurately represents all WooCommerce authoring selections for the selected store and latest Test, without secrets.
- [x] Valid, current successful Woo tests can be reviewed and saved as a durable editable draft through the established Commerce workflow.
- [x] Failed/stale tests and invalid definitions cannot be saved; user receives actionable errors without losing work.
- [x] Duplicate Save cannot create duplicate records; no Woo tool is silently published or used in production.
- [x] Commerce-focused UI/schema/persistence tests pass without new non-Commerce repository changes.

## Validation

- [x] Focused WooCommerce Review, draft validation and persistence integration tests, including blocked/stale/duplicate cases. The four focused files pass 15/15, including integrated blocked/stale/invalid/pending/duplicate/retry/back-to-edit/success flows.
- [x] Typecheck, relevant lint/build checks actually supported by Commerce and required for this task.
- [x] `git diff --check`; task worktree isolation and synchronization evidence in Completion Report.

## Stop Condition

Set task to `review`, record Completion Report and STOP when all requirements are met. Report any unavoidable cross-repository publication/runtime contract gap instead of silently extending scope.

## Implementation Notes

Reuse existing ReviewTab controls and persistence actions. Keep Woo-specific detail in provider modules, not an enlarged wizard orchestrator. Save is a Commerce draft operation, not a tool publication or store credential change.

## Completion Report

### Status

Complete — Attempt 2 passed developer self-review and the developer explicitly completed the task at 2026-10-16T13:49:23Z. Attempt 1 Changes Requested history is preserved below. Attempt 2 adds the missing invalid-description Save guard and corrects the integrated workflow assertions.

### Files Changed

- `src/commerce/woocommerce/authoring-draft-definition.ts`
- `src/studio/server-actions.ts`
- `src/studio/tools/authoring/persisted-woocommerce-tool-editor.tsx`
- `src/studio/tools/authoring/review/woocommerce-rest-review-summary.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/admin-explorer.test.tsx`
- `tests/fixtures/arch030-woocommerce-draft.ts`
- `tests/woocommerce-rest-draft-definition.test.ts`
- `tests/woocommerce-rest-review-save.test.ts`
- `tests/woocommerce-rest-review-ui.test.tsx`
- `tests/woocommerce-rest-review-workflow.test.tsx`

### Work Completed

- Added canonical Review cards for selected store, tool identity, GET operation and parameters, input/output schemas, selected response fields, result template and current test status; credential/test payload material is excluded or redacted.
- Added a strict Commerce-local Woo draft parser/builder and persisted editable `DRAFT_ONLY` definition. Runtime `CommerceToolDefinitionSchema` rejects the Woo draft.
- Added an authorized server-side Save action that validates the draft, verifies expiring signed proof for the same principal/store/draft/examples, rejects generic-action bypasses, and persists through the existing initial-draft workflow. Persisted Woo draft edits remain shop-scoped and draft-only.
- Added Review UI, draft-schema, save-boundary and persistence retry tests. The shared mutation handler suppresses an in-flight duplicate; existing lifecycle tests verify exact operation retries do not duplicate tool/revision/audit records.
- Added integrated Woo authoring workflow tests for current-test gating, returning to edits, expired proofs, pending/duplicate Save clicks, retry behavior and successful persisted navigation.
- Attempt 2 fixed a real validation gap: the Review Save control now remains disabled when the required tool description is blank, matching draft-builder validation. Workflow assertions now verify stale proof blocks advancing/entering Review and match the actual URL-only navigation contract.

### Validation Results

- Earlier focused command `./node_modules/.bin/vitest run tests/woocommerce-rest-draft-definition.test.ts tests/woocommerce-rest-review-save.test.ts tests/woocommerce-rest-review-ui.test.tsx`: **passed, 10/10**.
- Latest focused command `./node_modules/.bin/vitest run tests/woocommerce-rest-draft-definition.test.ts tests/woocommerce-rest-review-save.test.ts tests/woocommerce-rest-review-ui.test.tsx tests/woocommerce-rest-review-workflow.test.tsx`: **4 files passed, 15/15 tests passed**.
- `./node_modules/.bin/vitest run tests/tool-authoring-screen.test.tsx`: **28 passed, 7 failed** on the task branch. The same test file on a temporary detached `origin/main` worktree also reported **28 passed, 7 failed**; failures are pre-existing Admin flows unable to find the `Run Test` button. The temporary baseline worktree was removed.
- `npm run typecheck`: **passed** after Attempt 2 changes.
- ESLint on `src/studio/tools/new-tool-editor.tsx` and `tests/woocommerce-rest-review-workflow.test.tsx`: **0 errors, 1 warning** (`selectedShop` unused in `new-tool-editor.tsx`).
- `npm run build`: **passed**; webpack emitted the existing Nunjucks dynamic-dependency warnings.
- `git diff --check origin/main...HEAD`: **passed** after Attempt 2 changes. Implementation fix commit `8a8c150f9415d73c2709ceaa352067808be88697` is pushed to `origin/task/ARCH-030-COMMERCE-002`; implementation worktree is clean. The `database` submodule remains initialized at its recorded gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-030-COMMERCE-002` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-030-COMMERCE-002` are isolated on their matching `task/ARCH-030-COMMERCE-002` branches. The parent claim branch is synchronized; implementation `HEAD` equals its remote task branch. The implementation repository's database submodule was already initialized at its recorded gitlink.

### Deviations

- The latest implementation commit adds Woo workflow tests and removes the unrelated `update-submodule.sh` helper from the task branch.
- The broader authoring-screen suite has seven Admin failures, reproduced identically on `origin/main`; these are baseline failures and are not attributed to this task.
- No production authorized Woo store was used for an end-to-end UI save demonstration; Save-boundary tests use signed proof fixtures.

### Assumptions

The task's UI test-work-item gap can be resolved with focused Woo-specific screen coverage; the reported broad Admin failures are not attributed to this implementation without a baseline comparison.

### Unresolved Issues

- No real authorized-store UI save was demonstrated; Save authorization and persistence are covered with signed proof fixtures and mocked services. This remains unavailable live-store evidence, not a test claim.

### Architectural Concerns

No new non-Commerce implementation or production runtime support was introduced. The draft format is explicitly `DRAFT_ONLY`.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.

## Developer Self-Review — Changes Requested

### Corrections Required

- Add and run Woo-specific authoring-screen tests proving a duplicate Save click results in one mutation and returning to edit preserves the unsaved draft.
- Exercise integrated missing, failed/stale, invalid and pending Save states in the Woo Review flow; retain server-side signed-proof checks.
- Investigate the seven failing Admin authoring-screen tests or compare against the task branch baseline, then record the exact result. Do not describe them as passing.
- Remove `update-submodule.sh` from the task branch if it is not required by this scope, or document its task-specific justification for architect review.

### Validation Reviewed

Focused Woo Review/draft/save tests: 10 passed. Commerce lifecycle tests: 60 passed. Typecheck and production build passed. Changed-file ESLint had one unused-parameter warning and no errors. The combined authoring-screen/lifecycle run had seven authoring-screen failures and 60 lifecycle passes. No baseline comparison or live-store UI save was performed.

### Decision

Return this task to `ready`, clear `executor` and `claimed_at`, and preserve `attempt: 1`. The implementation commit is published on the existing implementation task branch. Do not create Attempt 2 in this review; the next authorized developer claim increments the attempt exactly once.

## Developer Self-Review — Changes Requested (Follow-up)

### Corrections Required

- Fix the two failing assertions in `tests/woocommerce-rest-review-workflow.test.tsx` without weakening coverage: verify stale proof prevents Review navigation and Save, and verify success navigates to the persisted tool using the actual navigation contract.
- Rerun all four focused Woo Review/draft/server/workflow test files and require a fully passing result.
- Resolve or baseline the seven failures in `tests/tool-authoring-screen.test.tsx`; preserve the result accurately and do not claim the shared screen suite passes while it fails.
- Keep the Commerce-focused UI/schema/persistence acceptance checkbox open until the focused Woo workflow tests pass.

### Validation Reviewed

Latest focused Woo suite: 13 passed, 2 failed. Latest existing authoring-screen suite: 28 passed, 7 failed. New workflow test ESLint passed. Earlier production typecheck/build passed; no production source changed in the latest test-only follow-up commit. Implementation branch is clean and pushed at `578733e4175b69b4c6df8aa88135ba47919d6c03`.

### Decision

Keep task `ready`, clear `executor` and `claimed_at`, and preserve `attempt: 1`. Attempt 1 remains Changes Requested; do not create Attempt 2 in this review. The next authorized developer claim increments the attempt exactly once.

## Developer Claim — Attempt 1

- Claimed by developer at `2026-10-16T13:00:35+0100`; `status: in_progress`, `executor: developer`, `attempt: 1`. `execution_mode: developer`, `completion_mode: developer`, `assigned_agent: moda_commerce`, and `coordinator: moda_architect` are unchanged.
- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-030-COMMERCE-002`; branch `task/ARCH-030-COMMERCE-002`, created from parent `origin/main` at `84ba39e14e4ac8e9f020d67271e031d123de108a`. The dependency task record in this synchronized parent worktree has `status: complete`.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-030-COMMERCE-002`; repository `moda-interact-commerce`; branch `task/ARCH-030-COMMERCE-002`, created from Commerce `origin/main` at `e1ead6058b92339ff2d9c018d5a8f0586c4fc2b3`.
- Both task worktrees were clean after creation and fetch; current `origin/main` is an ancestor of each task branch. There was no pre-existing local or remote task branch for COMMERCE-002.
- No implementation files were changed and no implementation tests/builds were run during claim preparation.

## Developer Claim — Attempt 2

- Claimed by developer at `2026-10-16T13:34:55Z`; `status: in_progress`, `executor: developer`, `attempt: 2`. `execution_mode: developer`, `completion_mode: developer`, `assigned_agent: moda_commerce`, and `coordinator: moda_architect` remain unchanged.
- The dependency `ARCH-030-COMMERCE-001` is `complete` in the canonical parent task worktree.
- Canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-030-COMMERCE-002`, branch `task/ARCH-030-COMMERCE-002`, was clean and synchronized with `origin/task/ARCH-030-COMMERCE-002` at `f405e7cf0f46d87c6e648abbc9733150ff466972` before the claim update.
- Canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-030-COMMERCE-002`, repository `moda-interact-commerce`, branch `task/ARCH-030-COMMERCE-002`, was clean and synchronized with its remote at `578733e4175b69b4c6df8aa88135ba47919d6c03`. Current Commerce `origin/main` at `e1ead6058b92339ff2d9c018d5a8f0586c4fc2b3` is an ancestor. The `database` submodule is initialized and matches its recorded gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`.
- No implementation files or tests were changed/run during claim preparation. Attempt 2 must address the two focused workflow assertion failures and resolve or baseline the seven existing authoring-screen failures as specified in the preceding Changes Requested review.

## Developer Self-Review — Attempt 2 Accepted

### Review Status

Accepted. Attempt 2 satisfies the task's required Work Items, Acceptance Criteria and focused validation. The seven broader Admin authoring-screen failures reproduce unchanged on `origin/main` and are recorded as baseline failures.

### Reconciliation Evidence

- Implementation commit `8a8c150f9415d73c2709ceaa352067808be88697` is published on `origin/task/ARCH-030-COMMERCE-002`; implementation worktree is clean. Changes are limited to the Woo Review Save validity guard and its integrated workflow tests.
- Focused Woo suite passes 15/15 across four files. Typecheck and production build pass. Changed-file ESLint reports no errors and one existing unused-parameter warning. `git diff --check origin/main...HEAD` passes.
- The broader `tests/tool-authoring-screen.test.tsx` suite reports 28 passed / 7 failed both on this task branch and on detached `origin/main`; the Admin flows fail to find `Run Test`. Baseline worktree was removed after the comparison.
- No authorized live Woo store was used; signed-proof server-action fixtures provide the Save boundary evidence, not live-store evidence.

### Decision

Attempt 2 is accepted. All task Work Items and Acceptance Criteria are complete. Explicit developer completion is recorded below; preserve `attempt: 2` and clear `executor` and `claimed_at`.

## Developer Completion Decision

The developer explicitly completed `ARCH-030-COMMERCE-002` on 2026-10-16T13:49:23Z after the Attempt 2 Accepted review. Set `status: complete`, `executor: null`, `claimed_at: null`, and preserve `attempt: 2`. No merge to `main` was performed or is required. No active downstream task depends on this task in the current canonical task set; superseded proposal references remain historical and inactive.
