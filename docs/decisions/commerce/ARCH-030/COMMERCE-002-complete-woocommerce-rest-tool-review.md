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
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-16T13:00:35+0100
attempt: 1
depends_on:
  - ARCH-030-COMMERCE-001
enables: []
created: 2026-10-14
updated: 2026-10-14
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

- [ ] Implement the WooCommerce Review cards using canonical authoring state and selected Shop.
- [ ] Build and validate persistable WooCommerce Commerce-local draft structure without duplicating the Request/Response editors.
- [ ] Wire the existing Commerce draft Save workflow, server-side authorization/validation and duplicate-submit protection.
- [ ] Add UI and persistence tests for success, stale Test, validation failure, retries, duplicate click and navigation back to edits.

## Interfaces / Contracts

Consumes COMMERCE-001 current-store Test state, server-verifiable expiring test proof, and WooCommerce Request/Response/template drafts. Produces a Commerce tool draft via existing Commerce persistence; no Shared package, external API contract or production runtime publication is created.

## Dependencies

- `ARCH-030-COMMERCE-001` must be architect-accepted and Complete before execution.

## Enables

None within ARCH-030; production runtime and merchant Studio work are separate initiatives.

## Acceptance Criteria

- [ ] Review accurately represents all WooCommerce authoring selections for the selected store and latest Test, without secrets.
- [ ] Valid, current successful Woo tests can be reviewed and saved as a durable editable draft through the established Commerce workflow.
- [ ] Failed/stale tests and invalid definitions cannot be saved; user receives actionable errors without losing work.
- [ ] Duplicate Save cannot create duplicate records; no Woo tool is silently published or used in production.
- [ ] Commerce-focused UI/schema/persistence tests pass without new non-Commerce repository changes.

## Validation

- [ ] Focused WooCommerce Review, draft validation and persistence integration tests, including blocked/stale/duplicate cases.
- [ ] Typecheck, relevant lint/build checks actually supported by Commerce and required for this task.
- [ ] `git diff --check`; task worktree isolation and synchronization evidence in Completion Report.

## Stop Condition

Set task to `review`, record Completion Report and STOP when all requirements are met. Report any unavoidable cross-repository publication/runtime contract gap instead of silently extending scope.

## Implementation Notes

Reuse existing ReviewTab controls and persistence actions. Keep Woo-specific detail in provider modules, not an enlarged wizard orchestrator. Save is a Commerce draft operation, not a tool publication or store credential change.

## Completion Report

### Status

In Progress — developer Attempt 1 is claimed. The sole explicit dependency, `ARCH-030-COMMERCE-001`, is `complete` in the synchronized parent task worktree. No implementation changes have been made during claim preparation.

### Files Changed

None during claim preparation. Implementation files will be recorded by the developer.

### Work Completed

None.

### Validation Results

No implementation validation was run during claim preparation.

### Deviations

No claim-time blocker. The primary workspace and Commerce source/reference checkout contain unrelated local changes; they were preserved and are not part of this task claim.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

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

## Developer Claim — Attempt 1

- Claimed by developer at `2026-10-16T13:00:35+0100`; `status: in_progress`, `executor: developer`, `attempt: 1`. `execution_mode: developer`, `completion_mode: developer`, `assigned_agent: moda_commerce`, and `coordinator: moda_architect` are unchanged.
- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-030-COMMERCE-002`; branch `task/ARCH-030-COMMERCE-002`, created from parent `origin/main` at `84ba39e14e4ac8e9f020d67271e031d123de108a`. The dependency task record in this synchronized parent worktree has `status: complete`.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-030-COMMERCE-002`; repository `moda-interact-commerce`; branch `task/ARCH-030-COMMERCE-002`, created from Commerce `origin/main` at `e1ead6058b92339ff2d9c018d5a8f0586c4fc2b3`.
- Both task worktrees were clean after creation and fetch; current `origin/main` is an ancestor of each task branch. There was no pre-existing local or remote task branch for COMMERCE-002.
- No implementation files were changed and no implementation tests/builds were run during claim preparation.
