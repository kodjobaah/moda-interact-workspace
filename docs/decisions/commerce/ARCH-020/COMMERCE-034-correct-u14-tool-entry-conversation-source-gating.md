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
status: complete
priority: 140
executor:
claimed_at:
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-017
  - ARCH-020-COMMERCE-009
enables:
  - ARCH-020-COMMERCE-019
created: 2026-09-21
updated: 2026-09-22
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

- [x] Remove selected-tool fallback from Conversation admission and payload construction.
- [x] Disable Conversation Start and render the specified guidance when no real behaviour/release source is selected.
- [x] Preserve Tool-test handoff/execution and independent source selectors.
- [x] Add focused regressions for tool-only entry, release/draft Conversation payloads and coexistence/back behavior.

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

- [x] U06 tool-only entry opens Tool test with the correct revision; a valid Run Tool request is emitted and `startConversation` remains zero calls.
- [x] Switching that tool-only entry to Conversation leaves Start disabled, shows accessible source guidance and never constructs/sends a zero-capability DRAFT.
- [x] Selecting a persisted release enables Start and sends exactly `{kind:'RELEASE',releaseId}`.
- [x] Selecting an unsaved/saved draft-behaviour source enables Start and sends its exact capability revision IDs, `toolRevisionIds: []` and response contract.
- [x] Tool selection remains usable for Tool test while Conversation selection is independent; reset/source locks/Back regressions remain green.
- [x] No fake capability/prompt, backend change or new API shape is introduced.

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

Ready for Architect Review.

### Files Changed

- `moda-interact-commerce/src/studio/preview/preview-screen.tsx`
- `moda-interact-commerce/tests/preview-screen.test.tsx`

### Work Completed

- Conversation admission now requires a selected persisted release or non-empty behaviour draft source.
- Removed selected-tool fallback from DRAFT payload construction; DRAFT payloads use the selected source members and `toolRevisionIds: []`.
- Added bounded accessible guidance for tool-only Conversation entry and regressions covering tool handoff, release/draft payloads, source coexistence, reset, locks and Back behavior.
- No backend, provider, Shared contract, route or deployment changes.

### Validation Results

- Focused U14: `./node_modules/.bin/vitest run tests/preview-screen.test.tsx --reporter=dot` -> 20 passed.
- Typecheck: `npm run typecheck` reached 179 pre-existing errors in four unrelated backend files; no diagnostics were reported in the touched U14 files.
- Lint: `npm run lint` -> 0 errors, 2 pre-existing warnings in `scripts/code-runtime-manifest.mjs` and `src/commerce/code-response/runtime/kernel.ts`.
- Production build: `npm run build` -> passed runtime packaging/smoke, Prisma generation, Next compilation, TypeScript, page data, static pages, traces and optimization.
- Diff check: `git diff --check` -> passed.

### Deviations

Repository typecheck remains red on unrelated pre-existing backend diagnostics; this task introduced no typecheck diagnostics in its changed files.

### Assumptions

COMMERCE-017/009 accepted types remain unchanged; the implementation commit is `57bd7d6` on `task/ARCH-020-COMMERCE-034`.

### Unresolved Issues

None for the bounded U14 change.

### Architectural Concerns

No contradiction found in the accepted U14/PreviewClient types.

### Git / VCS

Attempt 1 claimed by the deterministic launcher; parent claim commit `6e118484b5eace5ebf17cabc2cede1f2d2581933`.
Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-034`.
Implementation commit `57bd7d6` pushed to `task/ARCH-020-COMMERCE-034`.
Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-034`.

## Architect Review

### Review Status

Accepted.

### Review Notes

Independent review of implementation commit `57bd7d6` and report commit
`1b96d318` found no acceptance-blocking defects. Tool-only U06 handoff remains
in Tool test mode, preserves the selected tool revision, and does not call
`startConversation`. Conversation admission now requires a persisted release or
a non-empty authored draft source; selected-tool fallback, zero-capability DRAFT
payloads, synthetic capabilities and generic prompts are absent.

The release path emits exactly `{ kind: "RELEASE", releaseId }` when the
selected source is persisted. The draft path uses only the selected source's
`members.map(member => member.capabilityRevisionId)`, sends
`toolRevisionIds: []`, and forwards the selected `responseContract`. The tool
and Conversation selectors remain independent. Focused tests also cover source
locks during pending/uncertain operations, reset admission, release/draft
switching, and Back navigation to the originating release context. No backend,
PreviewClient/shared contract, route, provider, or deployment changes were
introduced.

### Reviewed Files

- `moda-interact-commerce/src/studio/preview/preview-screen.tsx`
- `moda-interact-commerce/tests/preview-screen.test.tsx`
- Implementation commit `57bd7d6`
- Completion Report in parent commit `1b96d318`

### Validation Reviewed

- Focused U14 Vitest run: 20/20 passed.
- `npm run lint`: 0 errors; two warnings are pre-existing and outside the
   touched files.
- `npm run build`: passed production packaging, compilation, generation and
   optimization checks.
- `git diff --check`: passed.
- `npm run typecheck`: 179 pre-existing errors in four unrelated backend files;
   no diagnostics were reported for the touched U14 files.
- Remote implementation ref `origin/task/ARCH-020-COMMERCE-034` resolves to
   `57bd7d6`; the commit changes only the two scoped files.

### Architecture Conformance

Conforms to ARCH-020 U14/C9/C20 and the COMMERCE-019 Attempt 2 correction
boundary. The implementation preserves the accepted PreviewClient and
`PreviewSelection` contracts, keeps source gating in the U14 UI, and satisfies
the required tool-only, release, draft, selector, reset/lock, and Back
semantics. The recorded typecheck baseline is not a regression from this task.

### Follow-up

None for implementation. Architect state reconciliation marks this task `complete` and records it as an accepted prerequisite of COMMERCE-019. COMMERCE-019 remains `ready`; no downstream task was launched by this reconciliation.
