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
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 1
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
- [ ] Add UI and persistence tests for success, stale Test, validation failure, retries, duplicate click and navigation back to edits.

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

- [ ] Focused WooCommerce Review, draft validation and persistence integration tests, including blocked/stale/duplicate cases. The focused Review/draft/server tests pass; direct Woo UI duplicate-click and back-to-edit coverage remains outstanding.
- [x] Typecheck, relevant lint/build checks actually supported by Commerce and required for this task.
- [x] `git diff --check`; task worktree isolation and synchronization evidence in Completion Report.

## Stop Condition

Set task to `review`, record Completion Report and STOP when all requirements are met. Report any unavoidable cross-repository publication/runtime contract gap instead of silently extending scope.

## Implementation Notes

Reuse existing ReviewTab controls and persistence actions. Keep Woo-specific detail in provider modules, not an enlarged wizard orchestrator. Save is a Commerce draft operation, not a tool publication or store credential change.

## Completion Report

### Status

Changes Requested — Attempt 1 implementation is pushed. Work Items 1–3 and Acceptance Criteria 1–5 are implemented; the UI/persistence test work item remains open because Woo-specific duplicate-click and navigation-back coverage is missing. The task is `ready`, `executor: null`, `claimed_at: null`, `attempt: 1`.

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
- `update-submodule.sh` (included in the implementation commit; unrelated to this task and flagged for architect review)

### Work Completed

- Added canonical Review cards for selected store, tool identity, GET operation and parameters, input/output schemas, selected response fields, result template and current test status; credential/test payload material is excluded or redacted.
- Added a strict Commerce-local Woo draft parser/builder and persisted editable `DRAFT_ONLY` definition. Runtime `CommerceToolDefinitionSchema` rejects the Woo draft.
- Added an authorized server-side Save action that validates the draft, verifies expiring signed proof for the same principal/store/draft/examples, rejects generic-action bypasses, and persists through the existing initial-draft workflow. Persisted Woo draft edits remain shop-scoped and draft-only.
- Added Review UI, draft-schema, save-boundary and persistence retry tests. The shared mutation handler suppresses an in-flight duplicate; existing lifecycle tests verify exact operation retries do not duplicate tool/revision/audit records.

### Validation Results

- Focused command `./node_modules/.bin/vitest run tests/woocommerce-rest-draft-definition.test.ts tests/woocommerce-rest-review-save.test.ts tests/woocommerce-rest-review-ui.test.tsx`: **passed, 10/10**.
- `./node_modules/.bin/vitest run tests/tool-authoring-screen.test.tsx tests/commerce-lifecycle.test.ts`: Commerce lifecycle tests **passed, 60/60**; the broader authoring-screen file had **7 failures** where existing Admin test flows could not find the `Run Test` button. These failures are not represented as passing Woo Review tests; baseline comparison was not performed.
- `npm run typecheck`: **passed**.
- Changed-production-file ESLint: **0 errors, 1 warning** (`selectedShop` unused in `new-tool-editor.tsx`).
- `npm run build`: **passed**; webpack emitted the existing Nunjucks dynamic-dependency warnings.
- `git diff --check origin/main...HEAD`: **passed**. Implementation commit `2139a7677b39f25065fba57fe91b503fe66913e2` is pushed to `origin/task/ARCH-030-COMMERCE-002`; implementation worktree is clean.
- Canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-030-COMMERCE-002` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-030-COMMERCE-002` are isolated on their matching `task/ARCH-030-COMMERCE-002` branches. The parent claim branch is synchronized; implementation `HEAD` equals its remote task branch. The implementation repository's database submodule was already initialized at its recorded gitlink.

### Deviations

- `update-submodule.sh` is included in the implementation commit but is unrelated to COMMERCE-002; it checks out a database submodule revision and searches for an enum. It was not executed and is flagged for architect disposition.
- The broader authoring-screen suite has the failures recorded above. No baseline run was made, so whether those failures predate this task is unverified.
- No production authorized Woo store was used for an end-to-end UI save demonstration; Save-boundary tests use signed proof fixtures.

### Assumptions

The task's UI test-work-item gap can be resolved with focused Woo-specific screen coverage; the reported broad Admin failures are not attributed to this implementation without a baseline comparison.

### Unresolved Issues

- Add direct Woo authoring-screen tests for duplicate Save clicks and returning to edit without losing the current draft; verify stale/invalid/pending Save remains blocked in the integrated screen.
- Investigate or baseline the seven `tool-authoring-screen.test.tsx` failures before treating that broader suite as green.
- Architect to decide whether the unrelated `update-submodule.sh` belongs on the task branch.

### Architectural Concerns

No new non-Commerce implementation or production runtime support was introduced. The draft format is explicitly `DRAFT_ONLY`; the unrelated database helper requires architect review.

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

## Developer Claim — Attempt 1

- Claimed by developer at `2026-10-16T13:00:35+0100`; `status: in_progress`, `executor: developer`, `attempt: 1`. `execution_mode: developer`, `completion_mode: developer`, `assigned_agent: moda_commerce`, and `coordinator: moda_architect` are unchanged.
- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-030-COMMERCE-002`; branch `task/ARCH-030-COMMERCE-002`, created from parent `origin/main` at `84ba39e14e4ac8e9f020d67271e031d123de108a`. The dependency task record in this synchronized parent worktree has `status: complete`.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-030-COMMERCE-002`; repository `moda-interact-commerce`; branch `task/ARCH-030-COMMERCE-002`, created from Commerce `origin/main` at `e1ead6058b92339ff2d9c018d5a8f0586c4fc2b3`.
- Both task worktrees were clean after creation and fetch; current `origin/main` is an ancestor of each task branch. There was no pre-existing local or remote task branch for COMMERCE-002.
- No implementation files were changed and no implementation tests/builds were run during claim preparation.
