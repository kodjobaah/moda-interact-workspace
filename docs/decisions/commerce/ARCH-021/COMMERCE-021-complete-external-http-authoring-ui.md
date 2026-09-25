---
id: ARCH-021-COMMERCE-021
architecture_id: ARCH-021
title: Complete External HTTP request and response authoring UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 50
executor: null
claimed_at: null
attempt: 5
depends_on:
  - ARCH-021-COMMERCE-019
  - ARCH-021-COMMERCE-020
  - ARCH-021-COMMERCE-023
  - ARCH-021-COMMERCE-005
  - ARCH-021-COMMERCE-006
enables: []
created: 2026-09-23
updated: 2026-09-25
---

# Complete External HTTP request and response authoring UI

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Allow admins to author the complete canonical EXTERNAL_HTTP draft—exact connection revision, declarative or JavaScript request construction, and DIRECT/Visual/JavaScript response processing—while previewing request construction without making a provider call.

Primary files:

```text
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/tool-editor.tsx
src/studio/external-http/editor.tsx
src/studio/code-response/code-editor.tsx       # reuse only; behavior changes only if required for generic label/props
src/studio/tools/external-validation-server-actions.ts
src/studio/tools/reconciliation-server-actions.ts
tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

## Out of Scope

- Live external HTTP calls.
- Credential display/decryption.
- POST/write methods.
- Shopify Admin UI (COMMERCE-022).
- Feature association/publishing after live test.

## Requirements

### R1 — execution choice

The Tool editor's external execution kind persists exactly:

```text
kind: EXTERNAL_HTTP
method: GET
connectionRevisionId: exact immutable selected revision
```

The user selects a real persisted connection revision; origin/auth are displayed only as safe metadata already exposed by the accepted port. Secrets never enter browser state.

### R2 — request authoring

Provide exactly two request modes:

```text
Declarative
JavaScript
```

Declarative fields:

```text
path
query mappings
static safe headers
```

JavaScript uses the existing CodeMirror JavaScript editor with starter source:

```js
function buildRequest({ args }) {
  return {
    path: '/',
    query: {},
    headers: { accept: 'application/json' }
  };
}
```

Do not show method/origin/credential/body controls inside JavaScript.

### R3 — request preview

Provide a bounded manual "Tool arguments" JSON editor/input for authoring preview only. On `Preview request`:

1. parse JSON;
2. server-validate against the current tool `inputSchema`;
3. execute declarative mapping or COMMERCE-017 request processor;
4. show only the resulting safe descriptor:

```text
GET <connection origin redacted-safe display + relative path/query>
authored safe headers
credential header: configured/redacted, never value
```

No DNS/network/provider call occurs. The UI must visibly label this as request construction preview, not a live Tool test.

### R4 — response authoring

Provide exactly three response modes:

```text
Direct
Visual
JavaScript
```

Direct:

```text
responseFormat must be JSON
resultPath
resultSchema
no projection/filter/code fields
```

Visual preserves existing OBJECT/LIST/filter/sort/limit editor.

JavaScript preserves existing raw-response/code editor and `transform(response)` contract.

Switching modes must not silently copy stale incompatible configuration into the newly selected mode. A dirty-editor confirmation is required before destructive mode resets.

### R5 — draft save, validation and publication handoff

`Save draft` and `Validate` are intentionally different lifecycle operations:

```text
Save draft
  -> parse/bound through COMMERCE-016 CommerceToolDraftDefinitionSchema
  -> preserve storage/security bounds
  -> incomplete authoring state may persist
  -> no live test required

Validate
  -> COMMERCE-023 authoritative full-definition validation
  -> request JavaScript/response processing/connection checks as applicable
  -> still no provider I/O

Publish
  -> definition must first pass COMMERCE-023 full validation
  -> common COMMERCE-019 publication gate applies
  -> Phase 3 returns LIVE_TEST_REQUIRED
```

Browser-only validation remains advisory. Save MUST NOT require the draft to satisfy the complete `CommerceToolDefinitionSchema`; otherwise partially authored JavaScript/request/response work could not be saved.

Save persists the exact Commerce-owned draft representation. No compatibility conversion is allowed. `LIVE_TEST_REQUIRED` must be shown clearly rather than treated as a generic failure.

Mutation/error handling follows COMMERCE-020 exactly:

- Save/create/update/publish use named Server Actions;
- explicit `FORBIDDEN`, `INVALID_INPUT`, `NOT_FOUND`, `CONFLICT`, `CAS_CONFLICT`, `LIVE_TEST_REQUIRED`, `DATABASE_UNAVAILABLE` and `INTERNAL_ERROR` remain visible;
- only a rejected/lost mutation response may enter `UNCONFIRMED`;
- `Reconcile` uses COMMERCE-020 audit lookup and never replays the original mutation;
- validation/request-preview failures never create `UNCONFIRMED` because they are non-mutating.

Publishing remains visible/enabled only for `PLATFORM_SUPER_ADMIN`; PLATFORM_ADMIN may author/save/validate drafts but does not gain publication authority.

### R6 — no fixture-led human test

The production Tool editor must no longer present synthetic external response fixtures as the *normal* "test this tool" workflow. Fixture UI may remain in explicit developer/test-only paths used by automated suites. Real live Tool Test arrives in Phase 4.

## Work Items

- [ ] Add request mode UI and safe descriptor preview.
- [ ] Add DIRECT response mode.
- [ ] Preserve Visual/response JS modes.
- [ ] Wire authoritative validation/save and LIVE_TEST_REQUIRED presentation.
- [ ] Remove fixture-first human test affordance from production flow.
- [ ] Add focused UI regressions.

## Interfaces / Contracts

Consumes the COMMERCE-016 Commerce-owned Tool contract, COMMERCE-023 External HTTP validation/preview boundary and COMMERCE-019 common publication gate.

## Dependencies

- ARCH-021-COMMERCE-019
- ARCH-021-COMMERCE-020
- ARCH-021-COMMERCE-023
- ARCH-021-COMMERCE-005
- ARCH-021-COMMERCE-006

## Enables

None in Phase 3. Phase 4 live-test tasks will depend on this completed authoring surface.

## Acceptance Criteria

- [ ] Admin can author every canonical EXTERNAL_HTTP request/response mode.
- [ ] Request JS sees only tool arguments and produces only a safe descriptor.
- [ ] Request preview performs zero provider I/O.
- [ ] Direct/Visual/JavaScript response modes persist losslessly.
- [ ] Incomplete drafts can be saved without full-definition validation or a live test.
- [ ] Production UI communicates that live testing is required before publication.
- [ ] Explicit server failures remain visible; only lost/rejected mutation responses enter reconcilable UNCONFIRMED state.
- [ ] Publish authority remains PLATFORM_SUPER_ADMIN-only through the accepted hierarchy.

## Validation

- [ ] `npm run test:arch020-external-tools-ui`
- [ ] focused Phase 3 external authoring UI tests
- [ ] request-preview test proving zero transport calls
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not implement live HTTP execution/testing.

## Implementation Notes

The model/CommerceAgent supplies runtime arguments; this UI only authors `inputSchema`, mappings/code and optional manual preview arguments.

## Completion Report

### Status
Attempt 5 implementation complete; returned to architect review.
### Files Changed
- `src/studio/tools/tool-editor.tsx`
- `src/studio/external-http/editor.tsx`
- `src/studio/tools/shopify-admin-editor.tsx`
- `tests/external-tools-ui.test.tsx`
### Work Completed
- Replaced incomplete-DRAFT/full-definition casts with a draft-capable editor state and schema-based readback.
- Narrowed child editor contracts to execution-owned data.
- Invalidated external validation success and messages on authoring edits.
- Preserved validation state only when the saved definition exactly matches the submitted candidate.
- Added production-reread incomplete-DRAFT DTO UI coverage.
- Added explicit dirty -> Save -> Validate -> SUPER_ADMIN publish gating coverage, including `LIVE_TEST_REQUIRED`.
### Validation Results
- `npm run test:arch020-external-tools-ui`: 16/16 passed.
- Focused four-file Vitest packet (`external-tools-ui`, `tool-authoring-screen`, `studio-workspace`, `studio-integration`): 67/67 passed.
- Targeted ESLint: passed with zero warnings.
- `git diff --check`: passed.
- Static `as ToolDefinition` invariant for the DRAFT editor path: passed.
- `npm run typecheck`: repository baseline exited 2; no diagnostics referenced any COMMERCE-021 task-owned file.
- No Phase 4 live HTTP execution/testing was run.
### Deviations
- The implementation branch had an existing upstream tracking mismatch; it was pushed explicitly with `git push origin HEAD`.
### Assumptions
- Attempt 5 launcher claim commit `cd4ae5512540510e6820554d88beba6225c70a63` is synchronized in both the parent worktree and implementation worktree.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-021`, branch `task/ARCH-021-COMMERCE-021`, claim commit `cd4ae5512540510e6820554d88beba6225c70a63`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-021`, branch `task/ARCH-021-COMMERCE-021`, implementation commit `7a033f32c0ed76431b2a5f7db1e347ee278cbb81`, matching `origin/task/ARCH-021-COMMERCE-021`.
- Recursive database submodule evidence: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
### Unresolved Issues
Repository-wide typecheck still reports pre-existing diagnostics outside the task-owned files; these were not changed.
### Architectural Concerns
None

## Architect Review

### Review Status
Pending
### Review Notes
None
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending
### Follow-up
None
