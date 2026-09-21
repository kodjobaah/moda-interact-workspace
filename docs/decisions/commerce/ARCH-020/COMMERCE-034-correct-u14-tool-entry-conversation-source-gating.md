---
id: ARCH-020-COMMERCE-034
architecture_id: ARCH-020
title: Correct U14 tool-entry conversation source gating
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 140
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-017
  - ARCH-020-COMMERCE-009
enables:
  - ARCH-020-COMMERCE-019
created: 2026-09-21
updated: 2026-09-21
---

# Correct U14 tool-entry conversation source gating

## Architecture

ARCH-020 U14/C9/C20 and the COMMERCE-019 Attempt 2 Architect Review. This is the
bounded correction for an interface defect discovered after COMMERCE-017 acceptance;
it does not reopen or redesign PreviewService.

## Objective

Make U14 distinguish a saved tool-test source from the authored behaviour/release
source required to start a Conversation preview.

## Context

The accepted U14 component lets a U06 tool handoff switch to Conversation and start a
DRAFT with zero capability revisions plus the selected tool revision. The real saved
loader correctly returns no authored capabilities/prompts for that selection, while a
valid Shared Commerce manifest requires authored capability content. The architecture
now resolves the ambiguity: tools are valid Tool-test inputs; Conversation requires a
real release/behaviour source. No synthetic capability or generic prompt is allowed.

## Scope

`src/studio/preview/preview-screen.tsx` and focused U14 tests in
`tests/preview-screen.test.tsx` (or the existing accepted equivalent test file). Update
only directly related U14 copy if needed.

## Out of Scope

Preview backend/routes, COMMERCE-013 saved facade, Redis, model providers, Shared
schemas, synthetic capabilities/prompts, release persistence, Studio U01–U13 services,
new navigation routes or deployment.

## Requirements

Apply these exact UI/payload rules:

1. A U06/saved-tool handoff continues to preselect that exact tool and opens U14 in
   **Tool test** mode. Existing schema-driven `Run tool test` behavior is unchanged.
2. Tool source and Conversation source are independent selectors. A selected tool is
   never sufficient evidence for Conversation Start.
3. In Conversation mode, `Start conversation` is disabled unless a real release or
   draft-behaviour source (`selectedRelease`) is selected and fixtures are ready.
4. With only a tool selected, render bounded accessible guidance:
   `Select a saved release or behaviour draft to start a conversation.`
   Equivalent punctuation is allowed; do not expose internals.
5. `conversationPayload()` must never derive Conversation `toolRevisionIds` from
   `selectedTool`.
6. Saved release selection uses exactly `{kind:'RELEASE', releaseId}` when the selected
   item has a persisted release ID and `selectionKey === 'release'`.
7. DRAFT Conversation selection uses only the selected behaviour/draft source's
   actual `members.map(member => member.capabilityRevisionId)` and its validated
   `responseContract`; set `toolRevisionIds: []`.
8. Empty capability revision arrays are not dispatched by Conversation Start. Do not
   invent `conversation_core`, generic prompts or another tool-to-capability mapping.
9. Switching tabs does not silently replace either selector. A tool may remain
   preselected for Tool test while a separate release/draft is selected for
   Conversation.
10. Existing source locks/reconciliation/reset/Back semantics remain unchanged. Back
    still returns to the originating source context.

## Work Items

- [ ] Remove selected-tool fallback from Conversation admission and payload construction.
- [ ] Disable Conversation Start and render the specified guidance when no real behaviour/release source is selected.
- [ ] Preserve Tool-test handoff/execution and independent source selectors.
- [ ] Add focused regressions for tool-only entry, release/draft Conversation payloads and coexistence/back behavior.

## Interfaces / Contracts

Consumes the already accepted COMMERCE-017 `PreviewClient` and C9.1
`PreviewSelection` union. No contract changes. COMMERCE-019 consumes this corrected UI
component after architect acceptance.

## Dependencies

- ARCH-020-COMMERCE-017
- ARCH-020-COMMERCE-009

## Enables

- ARCH-020-COMMERCE-019

## Acceptance Criteria

- [ ] U06 tool-only entry opens Tool test with the correct revision; a valid Run Tool request is emitted and `startConversation` remains zero calls.
- [ ] Switching that tool-only entry to Conversation leaves Start disabled, shows accessible source guidance and never constructs/sends a zero-capability DRAFT.
- [ ] Selecting a persisted release enables Start and sends exactly `{kind:'RELEASE',releaseId}`.
- [ ] Selecting an unsaved/saved draft-behaviour source enables Start and sends its exact capability revision IDs, `toolRevisionIds: []` and response contract.
- [ ] Tool selection remains usable for Tool test while Conversation selection is independent; reset/source locks/Back regressions remain green.
- [ ] No fake capability/prompt, backend change or new API shape is introduced.

## Validation

Run the focused U14 component tests, repository typecheck, lint, production build and
`git diff --check`. Do not add browser/E2E volume merely to increase test counts; the
required evidence is the functional source/payload behavior above.

## Stop Condition

After work/acceptance/validation is complete, update this task to review, clear claim
fields, return the Completion Report to moda_architect and STOP. Do not execute019 or
change backend/provider code.

## Implementation Notes

Use `/moda-task ARCH-020-COMMERCE-034` and the dedicated mirrored worktrees. The
architectural choice is final for this task: **tool-only means Tool test; Conversation
requires authored behaviour/release content.** Do not spend execution time exploring a
synthetic-capability alternative.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

COMMERCE-017/009 accepted types remain unchanged.

### Unresolved Issues

None at definition time.

### Architectural Concerns

Return any contradiction in the accepted U14/PreviewClient types to moda_architect.

### Git / VCS

Defined but not claimed. Expected mirrored branch `task/ARCH-020-COMMERCE-034`.
Record normal launcher preparation/isolation/commit/push evidence on execution.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation of the exact source-gating correction above.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Accept independently, then leave019 blocked until COMMERCE-033 is also Complete.
