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
attempt: 4
depends_on:
  - ARCH-021-COMMERCE-019
  - ARCH-021-COMMERCE-020
  - ARCH-021-COMMERCE-023
  - ARCH-021-COMMERCE-005
  - ARCH-021-COMMERCE-006
enables: []
created: 2026-09-23
updated: 2026-09-26
---

# Complete External HTTP request and response authoring UI

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Allow admins to author the complete canonical EXTERNAL_HTTP draft—exact connection revision, declarative or JavaScript request construction, and DIRECT/Visual/JavaScript response processing—while previewing request construction without making a provider call.

## Context

Phase 1 connected the Tool editor to real immutable connection revisions and installed response JavaScript composition. Phase 3 adds request construction and DIRECT response handling. Real provider execution remains Phase 4.

The accepted simplification is authoritative for this UI: Tool components consume named Server Actions, receive serializable props only, use the platform-role hierarchy, preserve deterministic server errors, and use COMMERCE-020 audit reconciliation only for genuinely unconfirmed mutation responses.

## Scope

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

- [x] Add request mode UI and safe descriptor preview.
- [x] Add DIRECT response mode.
- [x] Preserve Visual/response JS modes.
- [x] Wire authoritative validation/save and LIVE_TEST_REQUIRED presentation.
- [x] Remove fixture-first human test affordance from production flow.
- [x] Add focused UI regressions.

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

- [x] Admin can author every canonical EXTERNAL_HTTP request/response mode.
- [x] Request JS sees only tool arguments and produces only a safe descriptor.
- [x] Request preview performs zero provider I/O.
- [x] Direct/Visual/JavaScript response modes persist losslessly.
- [x] Incomplete drafts can be saved without full-definition validation or a live test.
- [x] Production UI communicates that live testing is required before publication.
- [x] Explicit server failures remain visible; only lost/rejected mutation responses enter reconcilable UNCONFIRMED state.
- [x] Publish authority remains PLATFORM_SUPER_ADMIN-only through the accepted hierarchy.

## Validation

- [x] `npm run test:arch020-external-tools-ui`
- [x] focused Phase 3 external authoring UI tests
- [x] request-preview test proving zero transport calls
- [x] targeted lint/typecheck
- [x] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not implement live HTTP execution/testing.

## Implementation Notes

The model/CommerceAgent supplies runtime arguments; this UI only authors `inputSchema`, mappings/code and optional manual preview arguments.

## Completion Report

### Status
Attempt 4 implementation pushed; ready for architect review
### Files Changed
- `src/studio/external-http/editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/contracts.ts`
- `src/commerce/integration/studio/services.ts`
- `src/commerce/publication/lifecycle.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `app/preview/page.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/studio-workspace.test.tsx`
- `tests/studio-integration.test.ts`
### Work Completed
- Added Declarative and JavaScript request authoring, static safe headers, bounded tool-argument JSON, and non-network request descriptor preview.
- Added Direct response processing alongside Visual and JavaScript modes, with JSON enforcement and destructive mode-switch confirmation.
- Changed draft persistence to `CommerceToolDraftDefinitionSchema` and added a distinct authoritative Validate action.
- Removed synthetic response fixture controls from the production Tool editor.
- Corrected the COMMERCE-023 Server Action import boundary and separated local JSON parsing from action failures.
- Preserved incomplete draft definitions through the Studio read boundary while keeping publication full-definition validation strict.
- Added focused regressions for incomplete drafts, lifecycle and role separation, preview error branches, response-mode reset behavior, fixture removal, and the exact stale-CAS/dirty-navigation contract.

### Attempt 4 Validation Results
- Implementation commit: `cb1b1579624b48353abc82ab35522ad087ec6f5a`, pushed to `origin/task/ARCH-021-COMMERCE-021`.
- `npm run test:arch020-external-tools-ui`: 16 passed.
- Focused packet `npm exec vitest run tests/external-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/studio-workspace.test.tsx tests/studio-integration.test.ts`: 63 passed.
- `npm run typecheck`: exits only on unrelated baseline diagnostics in `app/api/studio/code-response/validate/route.ts`, `tests/agent-configuration-effective.test.ts`, `tests/agent-configuration-prompts-postgres.test.ts`, `tests/c20-integration-fixture.test.ts`, `tests/external-wiring.test.ts`, `tests/local-external-mcp-diagnostic.test.ts`, and `tests/selected-shop-context.test.ts`; no task-owned diagnostics.
- Targeted ESLint: 0 errors and 0 warnings.
- `git diff --check`: passed.

### Launcher Evidence
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-021`, branch `task/ARCH-021-COMMERCE-021`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-021`, branch `task/ARCH-021-COMMERCE-021`.
- Start synchronization used implementation base `4fc5034`; Attempt 4 claim commit: `74f2b46d36f30e4f2de5e37ab1600a340ea6e0de`.
- Recursive submodule status: `database` at `0a8d3b9feade69690b6c1e33aeda051ea588bd45` (`heads/main`).
- Both worktrees were clean before this report edit; final report commit, push parity, and final clean-state verification follow.
### Deviations
- Full repository typecheck remains affected by unrelated pre-existing diagnostics; no provider or live HTTP call was introduced.
### Assumptions
- The existing `SUPER_ADMIN` role value is the repository representation of `PLATFORM_SUPER_ADMIN` for the publication control.
### Unresolved Issues
- None within task scope.
### Architectural Concerns
The implementation remains bounded to `moda-interact-commerce`; no cross-repository changes were required. Live external HTTP execution/testing remains out of scope per the task stop condition.

## Architect Review

### Review Status
Changes Requested — Attempt 3

### Review Notes

#### Attempt 3 review — 2026-09-25

Reviewed implementation `4fc5034` and the submitted Attempt 3 snapshot against the
complete Attempt 2 correction contract.

Attempt 3 contains important corrections that MUST be preserved:

- JavaScript response authoring no longer has an independent mutation button; the
  main Tool draft Save path persists the current response source through the
  COMMERCE-020 `runCommand` coordinator;
- the DRAFT/full-definition type fallout in preview, in-memory Studio services and
  Studio tests is corrected; the submitted TypeScript artifact has no semantic
  diagnostic in the COMMERCE-021 causal files;
- response-mode "Discard changes and switch" now derives from the saved response
  baseline rather than leaking dirty response-owned values;
- the production Studio read boundary round-trips an incomplete DRAFT without
  forcing the full CommerceToolDefinition parser;
- malformed current input-schema JSON is classified locally before the COMMERCE-023
  preview Server Action;
- the authoring-only JavaScript response surface remains fixture-free;
- COMMERCE-023 preview/validation action routing remains correct;
- focused integration/external UI tests, targeted lint and `git diff --check` pass
  apart from the explicitly reported stale-CAS workspace regression.

Attempt 3 is not accepted because the required focused suite is knowingly red and the
failing stale-CAS regression is caused by a task-owned obsolete test boundary, not an
unrelated baseline. Two mandatory Attempt 2 lifecycle proofs are also still absent.

The following is the complete and authoritative Attempt 4 correction contract.
Runtime source should remain unchanged unless one of these tests exposes a genuine
defect. Do not implement Phase 4 live HTTP execution/testing.

##### A3-R1 — update the stale-CAS test to the COMMERCE-020 ToolMutationResult boundary

Change:

```text
tests/studio-workspace.test.tsx
```

The failing test currently uses:

```ts
const services = new InMemoryStudioServices('stale');
```

The in-memory fixture's generic Studio mutation contract returns:

```ts
{
  kind: 'conflict',
  code: 'STALE_CAS',
  message: 'This draft changed elsewhere. Refresh; your input has been retained.'
}
```

That is the LEGACY generic `StudioResult` shape.

The production Tool mutation Server Actions now return the accepted COMMERCE-020
`ToolMutationResult` envelope instead:

```ts
{
  kind: 'error',
  operationId,
  code: 'CAS_CONFLICT',
  message: 'tool draft is stale',
  retryable: false
}
```

`ToolAuthoringScreen.mutate()` intentionally recognizes `kind:'error'`; feeding the
old `kind:'conflict'` fixture into the mocked Server Action causes the test harness,
not production, to treat the result as success and display `Saved.`.

Do NOT change production `ToolAuthoringScreen` to understand the legacy generic
`StudioResult` shape. Do NOT reintroduce `STALE_CAS` into the Tool mutation contract.

Correct the test boundary in one of these bounded ways:

```text
preferred:
  for this test, mock updateToolDraft so the mocked named Server Action returns the
  exact ToolMutationResult error envelope above using the submitted operationId

acceptable:
  add a test-only Tool Server Action adapter in studio-workspace.test.tsx which
  translates the generic InMemoryStudioServices result to the current
  ToolMutationResult contract for Tool mutation action names only
```

If a shared test-only adapter is introduced, it must map at least:

```text
Studio ok                       -> Tool ok + submitted operationId
Studio forbidden               -> FORBIDDEN
Studio not-found               -> NOT_FOUND
Studio conflict STALE_CAS      -> CAS_CONFLICT
other Studio conflict          -> CONFLICT
Studio unavailable             -> DATABASE_UNAVAILABLE, retryable=true
```

and a legacy `kind:'unknown'` must simulate transport uncertainty by REJECTING the
mocked named Server Action rather than returning `kind:'unknown'`.

Required stale-CAS regression:

```text
edit Description
Save draft
mocked Tool Server Action returns:
  kind='error'
  code='CAS_CONFLICT'
  operationId=<submitted id>

-> status contains CAS_CONFLICT
-> exact server message remains visible
-> Description still equals "Retained draft text"
-> editor remains dirty
-> navigating Back opens the unsaved-changes dialog
-> NO "Saved." status
-> NO Tool UNCONFIRMED state
```

This regression must test the current Tool Server Action contract, not the removed
generic Studio mutation result.

##### A3-R2 — complete the incomplete-DRAFT production-read -> editor round-trip proof

Keep the existing production service regression:

```text
tests/studio-integration.test.ts
  "round-trips an incomplete DRAFT through the production Studio read boundary"
```

Add the missing UI half in:

```text
tests/external-tools-ui.test.tsx
```

Use an incomplete EXTERNAL_HTTP DRAFT that satisfies:

```text
CommerceToolDraftDefinitionSchema.safeParse(...) -> success
CommerceToolDefinitionSchema.safeParse(...)      -> failure
```

The test MUST prove:

```text
1. ToolEditor renders that DRAFT without throwing
2. the exact incomplete Input JSON Schema buffer is visible in
   "Input JSON Schema"
3. the exact incomplete Response template buffer is visible in
   "Response template"
4. Save draft can be clicked again
5. updateToolDraft receives the same incomplete draft payload; it is not silently
   replaced by a full-valid default
6. Validate invokes COMMERCE-023 and renders structural issues
7. PLATFORM_SUPER_ADMIN publish control remains disabled while the definition is
   invalid / validation is not current
```

The test may use the production-service result as `initialDetail` or construct an
equivalent ToolSummary from the exact production-reread DTO. It must not satisfy this
item with `InMemoryStudioServices` persistence alone.

Do not cast the incomplete DRAFT through `CommerceToolDefinitionSchema`.

##### A3-R3 — prove exact Save / Validate / Publish lifecycle and role separation

Add focused executable tests in:

```text
tests/external-tools-ui.test.tsx
```

Use the existing COMMERCE-023 action mock and the named Tool mutation Server Action
mock separately.

Required ADMIN case:

```text
role=ADMIN
Save draft visible
Validate visible
Publish validated revision ABSENT
Save draft calls updateToolDraft
Save draft does NOT call validateExternalToolDefinitionAction
Save draft creates no UNCONFIRMED when the mutation returns an explicit error
```

Required Validate case:

```text
validateExternalToolDefinitionAction returns:
  { kind:'ok', value:{ valid:true, issues:[] } }

click Validate
-> action called exactly once
-> exact status:
   "Definition passed authoritative validation. Live test is required before publication."
-> updateToolDraft/publishToolRevision not called
-> no Operation outcome unknown UI
```

Required SUPER_ADMIN case:

```text
role=SUPER_ADMIN
Publish validated revision visible

while dirty:
  publish disabled

after successful Save:
  still disabled until authoritative Validate succeeds

after current Validate succeeds + nonblank publication reason:
  publish enabled

publishToolRevision returns:
  {
    kind:'error',
    operationId,
    code:'LIVE_TEST_REQUIRED',
    message:'Run a successful live tool test for the current saved revision before publishing.',
    retryable:false
  }

-> status contains exact LIVE_TEST_REQUIRED code/message
-> no generic INTERNAL_ERROR
-> no Operation outcome unknown UI
-> definition remains editable
```

Also retain the module-boundary proof:

```text
Preview request -> COMMERCE-023 previewExternalRequestAction
Validate        -> COMMERCE-023 validateExternalToolDefinitionAction
```

##### A3-R4 — prove malformed argument JSON vs malformed schema vs action rejection

Keep the current local parsing separation and add/retain focused regressions for all
four observable branches:

```text
malformed Tool arguments JSON
-> "Tool arguments must be valid JSON."
-> previewExternalRequestAction call count = 0

malformed current Input JSON Schema buffer
-> "INVALID_INPUT: Input JSON Schema must be valid JSON."
-> previewExternalRequestAction call count = 0

previewExternalRequestAction returns explicit error
-> exact code/message visible
-> no UNCONFIRMED

previewExternalRequestAction Promise rejects
-> "INTERNAL_ERROR: Request preview could not be completed."
-> no UNCONFIRMED
```

Do not report a Server Action transport failure as invalid JSON.

##### A3-R5 — preserve response-mode and fixture-removal regressions

Do not regress the existing Attempt 3 tests for:

```text
persisted DIRECT selector value
DIRECT/Visual/JavaScript switching
Keep editing preserving dirty response state
Discard changes and switch dropping dirty response-owned values
authoring-only JavaScript response CodeEditor
Raw response sample absent
Run sample absent
Check run status absent
Cancel run absent
synthetic fixture selection/result absent
```

No Phase 4 live test button may be introduced.

##### A3-R6 — run the entire required focused packet successfully

Run exactly:

```bash
npm run test:arch020-external-tools-ui

npm exec vitest run \
  tests/external-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx \
  tests/studio-workspace.test.tsx \
  tests/studio-integration.test.ts

npm run typecheck

npm exec eslint \
  src/studio/external-http/editor.tsx \
  src/studio/tools/tool-editor.tsx \
  src/studio/contracts.ts \
  src/commerce/integration/studio/services.ts \
  src/commerce/publication/lifecycle.ts \
  src/studio/testing/in-memory-studio-services.ts \
  app/preview/page.tsx \
  tests/external-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx \
  tests/studio-workspace.test.tsx \
  tests/studio-integration.test.ts

git diff --check
```

All focused tests MUST pass with zero skips.

The stale-CAS test failure is task-owned and MUST be gone.

There must be zero TypeScript diagnostics in:

```text
src/studio/external-http/editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/contracts.ts
src/commerce/integration/studio/services.ts
src/commerce/publication/lifecycle.ts
src/studio/testing/in-memory-studio-services.ts
app/preview/page.tsx
tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
tests/studio-workspace.test.tsx
tests/studio-integration.test.ts
```

Other diagnostics may remain documented only when their exact file/error is unrelated
to COMMERCE-021.

##### A3-R7 — fresh Attempt 4 execution/report evidence

The submitted Attempt 3 task is still:

```yaml
status: in_progress
executor: copilot
claimed_at: 2026-09-25T18:07:29Z
attempt: 3
```

and its Completion Report explicitly states that focused validation is still blocked.
It is therefore not a valid review-ready handoff.

Attempt 4 must record the exact fresh launcher-prepared:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-021
implementation branch = task/ARCH-021-COMMERCE-021
start-of-attempt parent synchronization
start-of-attempt implementation synchronization
Attempt 4 claim evidence / commit
recursive submodule materialization
database submodule commit
implementation commit
final parent report commit
push parity
clean parent worktree
clean implementation worktree
```

Do not reuse or infer Attempt 3 claim/synchronization values.

Reconcile all Work Items, Acceptance Criteria, Validation and the Completion Report to
the final Attempt 4 results.

Before handoff set exactly:

```yaml
status: review
attempt: 4
executor: null
claimed_at: null
```

##### Attempt 4 stop condition

Return to architect review only when:

```text
stale CAS uses the ToolMutationResult boundary and the editor stays dirty
AND incomplete DRAFT production-read -> editor -> save/validate proof passes
AND ADMIN Save/Validate separation passes
AND SUPER_ADMIN clean+validated publish gating passes
AND LIVE_TEST_REQUIRED remains explicit and never becomes UNCONFIRMED
AND preview parse/action error branches are all proved
AND response-mode/fixture-removal regressions remain green
AND the complete four-file focused packet passes with zero skips
AND zero COMMERCE-021 task-owned type/lint/diff diagnostics remain
AND fresh Attempt 4 launcher/report evidence is complete
```

Then push implementation and parent task branches, return control to
`moda_architect`, and STOP.

Do not implement Phase 4 live HTTP execution/testing.

#### Historical Attempt 2 review

#### Attempt 2 review — 2026-09-25

Reviewed implementation `2662d939` and the submitted Attempt 2 Completion Report
against the complete Attempt 1 correction contract.

Attempt 2 contains important corrections that MUST be preserved:

- `ToolEditor` now imports the accepted COMMERCE-023
  `previewExternalRequestAction` / `validateExternalToolDefinitionAction` boundary;
- Studio DTOs distinguish DRAFT `ToolDraftDefinition` from PUBLISHED full
  `CommerceToolDefinition`;
- production Studio reads parse DRAFT rows with
  `CommerceToolDraftDefinitionSchema` and PUBLISHED rows with
  `CommerceToolDefinitionSchema`;
- publication lifecycle DRAFT create/update signatures use the draft definition;
- DIRECT is a controlled response-processing mode;
- response-mode dirty detection includes processing, format, resultPath and
  resultSchema;
- request-arguments JSON parsing is separated from a rejected preview Server Action;
- the production JavaScript response path no longer composes the fixture-led
  `ProductionCodeResponsePanel`;
- focused Vitest now executes and the submitted UI packet reports 24 passing tests.

Attempt 2 is not accepted because the JavaScript response Save path bypasses the
accepted COMMERCE-020 mutation boundary, the draft DTO widening leaves task-owned
typecheck failures in dependent Studio/preview surfaces, the destructive-switch
"Discard changes" path does not actually discard all response-mode-owned edits, and
the mandatory incomplete-draft + Save/Validate/Publish lifecycle regressions remain
absent.

The following is the complete and authoritative Attempt 3 correction contract. Do
not infer additional work from chat history. Do not implement Phase 4 live HTTP
testing.

##### A2-R1 — use one COMMERCE-020 mutation path for JavaScript response draft saves

Change:

```text
src/studio/tools/tool-editor.tsx
tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

The submitted authoring-only JavaScript response panel currently renders its own:

```tsx
<button onClick={() => void saveCodeDraft(...)}>Save draft</button>
```

and `saveCodeDraft()` calls `updateToolDraft()` directly.

That bypasses the accepted COMMERCE-020 `runCommand` mutation coordinator. Therefore:

```text
transport rejection
-> no Tool UNCONFIRMED state

later edit while save is in flight
-> direct helper may set dirty=false after the newer edit

explicit Tool mutation error
-> thrown Error from the panel instead of the normal Tool result presentation
```

This violates R5.

Required result: there MUST be only one production draft-save mutation path for the
external Tool editor, and it MUST go through the existing `runCommand` boundary.

Preferred smallest correction:

```text
JavaScript authoring panel
-> CodeEditor + transform(response) help only
-> NO independent mutation button

main ToolEditor "Save draft"
-> persists request + response JavaScript + inputSchema + responseTemplate together
-> uses runCommand/updateToolDraft
-> COMMERCE-020 transport-only UNCONFIRMED and monotonic dirty handling
```

If a second JavaScript-local Save button is retained for UX reasons, it MUST invoke
the exact same `runCommand` coordinator and preserve the content-revision dirty
invariant; it may not call `updateToolDraft()` directly.

Remove `saveCodeDraft()` if it is no longer needed.

Required executable regressions:

```text
edit response JavaScript
-> main Save draft sends the edited source through updateToolDraft exactly once

updateToolDraft returns explicit error
-> exact code/message visible
-> no UNCONFIRMED

updateToolDraft Promise rejects
-> UNCONFIRMED visible
-> exact original operationId retained
-> Reconcile path available

edit response JavaScript after save submission but before success
-> earlier success does NOT clear the newer dirty edit
```

Do not reintroduce fixture/sample execution.

##### A2-R2 — finish the task-owned type fallout from DRAFT/full-definition separation

Change the minimum required affected consumers:

```text
app/preview/page.tsx
src/studio/testing/in-memory-studio-services.ts
tests/studio-workspace.test.tsx
```

The submitted `tsconfig.tsbuildinfo` contains task-owned diagnostics caused by
COMMERCE-021 widening `ToolRevision.definition` for DRAFT rows:

```text
app/preview/page.tsx
  DRAFT ToolDraftDefinition is not assignable to PreviewTool full definition

src/studio/testing/in-memory-studio-services.ts
  draft-capable revision.definition.inputSchema is unknown when building
  AgentDescriptor

tests/studio-workspace.test.tsx
  definition.execution is unknown after reading a draft-capable union
```

These are NOT unrelated baseline diagnostics. They are direct consequences of A1-R2
and must be corrected in this task.

Required semantics:

1. `app/preview/page.tsx`
   - Preview may receive only a full `CommerceToolDefinition`.
   - PUBLISHED revisions are already full definitions.
   - A DRAFT may be offered to synthetic preview only when
     `CommerceToolDefinitionSchema.safeParse(revision.definition)` succeeds.
   - An incomplete authorable DRAFT must remain persisted/editable but MUST NOT be
     cast into `PreviewTool` or silently upgraded.
   - Filter/omit a draft from preview until it is structurally full-valid.

2. `src/studio/testing/in-memory-studio-services.ts`
   - Build `AgentDescriptor` only from a revision narrowed to `status:'PUBLISHED'`
     (or an explicitly full-schema-parsed definition).
   - Do not cast draft `inputSchema: unknown` to the published descriptor contract.

3. `tests/studio-workspace.test.tsx`
   - Where a test intentionally manipulates a full Storefront Tool definition,
     narrow/parse it through `CommerceToolDefinitionSchema` (or narrow a PUBLISHED
     revision) before reading `definition.execution`.
   - Do not use unsafe `as ToolDefinition` casts merely to silence TypeScript.

After correction `npm run typecheck` MUST contain zero diagnostics in all three files.

##### A2-R3 — make "Discard changes and switch" actually discard response-mode-owned edits

Change:

```text
src/studio/external-http/editor.tsx
tests/external-tools-ui.test.tsx
```

Attempt 2 correctly expands `processingDirty` to:

```text
responseProcessing
responseFormat
resultPath
resultSchema
```

but `confirmMode(true)` still switches from the CURRENT dirty execution. Therefore
dirty fields such as `resultSchema` can survive the button labelled:

```text
Discard changes and switch
```

Required behavior:

```text
Keep editing
-> current mode and every edited response-owned value remain unchanged

Discard changes and switch
-> discard the current unsaved response-owned values
-> derive the target mode from the SAVED response baseline plus the canonical
   target-mode defaults
-> no dirty responseFormat/resultPath/resultSchema value silently crosses the
   destructive switch
```

Do not reset unrelated request authoring or Tool metadata.

Required regression:

```text
start from saved DIRECT (or Visual)
edit resultPath
edit Response shape JSON
choose another response mode
dialog appears

Keep editing
-> old mode remains
-> edited resultPath/schema remain

repeat -> Discard changes and switch
-> target mode selected
-> edited resultPath/schema are NOT retained as unsaved values
```

The controlled selector must continue to display DIRECT for a persisted DIRECT
definition.

##### A2-R4 — complete the incomplete-DRAFT round-trip proof through the real Studio read boundary

Add/extend a focused integration test, preferably:

```text
tests/studio-integration.test.ts
```

plus UI coverage in:

```text
tests/external-tools-ui.test.tsx
```

The test MUST prove the exact A1-R2 sequence, not only TypeScript shape compatibility:

```text
1. begin with an EXTERNAL_HTTP DRAFT whose execution is authorable
2. persist inputSchema and/or responseTemplate that:
     - CommerceToolDraftDefinitionSchema ACCEPTS
     - CommerceToolDefinitionSchema REJECTS
3. updateToolDraft succeeds
4. re-read through createCommerceStudioServices(...).getTool(...)
5. DRAFT is returned without full-definition parse failure
6. render ToolEditor from that returned DRAFT
7. exact incomplete JSON text remains in its textarea
8. Save draft can run again
9. Validate returns structural issues rather than crashing/replacing the buffer
10. Publish remains disabled/unavailable until authoritative full validation passes
```

Do not satisfy this with `InMemoryStudioServices` only; the regression must cover the
production `models()` DRAFT-vs-PUBLISHED parser boundary.

Also prove PUBLISHED state still rejects the same incomplete definition.

##### A2-R5 — prove the exact Save / Validate / Publish role and lifecycle separation

Add executable UI regressions using the accepted named Server Action boundaries.

Mock the real module:

```text
src/studio/tools/external-validation-server-actions.ts
```

and the Tool mutation Server Actions separately.

Required cases:

```text
ADMIN:
  Save draft visible
  Validate visible
  publish control absent
  Save draft does NOT call validateExternalToolDefinitionAction

Validate:
  calls validateExternalToolDefinitionAction exactly once
  valid result shows exact:
  "Definition passed authoritative validation. Live test is required before publication."
  no mutation/UNCONFIRMED is created

SUPER_ADMIN:
  publish control visible
  disabled while dirty
  disabled until current authoritative validation passes
  after validation + clean save + reason -> enabled

publishToolRevision returns:
  { kind:'error', code:'LIVE_TEST_REQUIRED', ... }
-> exact LIVE_TEST_REQUIRED code/message remains visible
-> no generic INTERNAL_ERROR
-> no UNCONFIRMED
```

Also add the module-boundary assertion required by A1-R1:

```text
Preview request -> COMMERCE-023 previewExternalRequestAction
Validate        -> COMMERCE-023 validateExternalToolDefinitionAction
```

The current end-to-end test that stops after Save does not satisfy this item.

##### A2-R6 — classify malformed current input-schema JSON locally during Preview

Change:

```text
src/studio/tools/tool-editor.tsx
tests/external-tools-ui.test.tsx
```

Attempt 2 correctly separates malformed Tool-arguments JSON from a rejected preview
Server Action, but the ToolEditor callback still does:

```ts
JSON.parse(inputSchemaText)
```

inside the async callback passed to `ExternalHttpEditor`.

If the current input-schema buffer is malformed, this throws and the child reports:

```text
INTERNAL_ERROR: Request preview could not be completed.
```

That is not an internal/runtime failure; it is the current authoring buffer.

Before invoking `previewExternalRequestAction`, parse the current input-schema buffer
in a local bounded error branch.

Required observable behavior:

```text
malformed Tool arguments JSON
-> "Tool arguments must be valid JSON."
-> Server Action not called

malformed Input JSON Schema buffer
-> explicit INVALID_INPUT-style local authoring message
-> Server Action not called

Server Action explicit error
-> exact code/message displayed
-> no UNCONFIRMED

Server Action Promise rejection
-> bounded INTERNAL_ERROR preview message
-> no UNCONFIRMED
```

Remove the duplicate `JSON.parse(requestArguments)` call currently present in
`ExternalHttpEditor.previewRequest()`.

##### A2-R7 — preserve production removal of synthetic response testing

Keep the authoring-only JavaScript response UI.

Production JavaScript response mode MUST continue to have:

```text
Code editor visible
transform(response) help visible
no Raw response sample
no Run sample
no Check run status
no Cancel run
no synthetic fixture selector/result workflow
```

The legacy fixture-capable ARCH-020 panel may remain for explicit developer/automated
paths, but `ToolEditor` must not compose it for the normal production authoring
surface.

##### A2-R8 — deterministic validation and task-owned typecheck classification

Run exactly:

```bash
npm run test:arch020-external-tools-ui

npm exec vitest run \
  tests/external-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx \
  tests/studio-workspace.test.tsx \
  tests/studio-integration.test.ts

npm run typecheck

npm exec eslint \
  src/studio/external-http/editor.tsx \
  src/studio/tools/tool-editor.tsx \
  src/studio/contracts.ts \
  src/commerce/integration/studio/services.ts \
  src/commerce/publication/lifecycle.ts \
  src/studio/testing/in-memory-studio-services.ts \
  app/preview/page.tsx \
  tests/external-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx \
  tests/studio-workspace.test.tsx \
  tests/studio-integration.test.ts

git diff --check
```

All focused tests must execute with zero skips.

No TypeScript diagnostic in any of these causal COMMERCE-021 surfaces may be
classified as baseline:

```text
src/studio/external-http/editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/contracts.ts
src/commerce/integration/studio/services.ts
src/commerce/publication/lifecycle.ts
src/studio/testing/in-memory-studio-services.ts
app/preview/page.tsx
tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
tests/studio-workspace.test.tsx
tests/studio-integration.test.ts
```

The submitted Attempt 2 `tsconfig.tsbuildinfo` specifically contains COMMERCE-021
causal diagnostics in:

```text
src/studio/testing/in-memory-studio-services.ts
app/preview/page.tsx
tests/studio-workspace.test.tsx
```

Those three categories MUST be gone before Attempt 3 review.

Other typecheck diagnostics may remain baseline only when their exact file/error is
unrelated to the DRAFT/full-definition contract and the files above.

##### A2-R9 — fresh Attempt 3 launcher/report evidence

The user handoff identifies final parent report commit `b4202c2f`, while the embedded
Completion Report does not record that exact final hash and states only that the
final pushed tip will be recorded after the metadata amend.

Attempt 3 must record the exact fresh launcher-prepared:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-021
implementation branch = task/ARCH-021-COMMERCE-021
start-of-attempt parent synchronization
start-of-attempt implementation synchronization
Attempt 3 claim evidence / commit
recursive submodule materialization
database submodule commit
implementation commit
final parent report commit
push parity
clean parent worktree
clean implementation worktree
```

Do not reuse/infer Attempt 2 claim/synchronization values.

Reconcile Work Items, Acceptance Criteria, Validation and Completion Report to the
actual Attempt 3 evidence.

Before handoff set exactly:

```yaml
status: review
attempt: 3
executor: null
claimed_at: null
```

##### Attempt 3 stop condition

Return to architect review only when:

```text
JavaScript response Save uses COMMERCE-020 mutation semantics
AND all draft/full-definition causal type errors are removed
AND destructive response-mode discard actually discards response-owned edits
AND incomplete DRAFT persists -> production reread -> editor round-trip works
AND Save/Validate/SUPER_ADMIN/LIVE_TEST_REQUIRED lifecycle is executable
AND malformed arguments/input-schema/action failures are distinguished
AND fixture-led production response testing remains absent
AND focused Vitest + typecheck + lint + diff validation passes
AND zero task-owned diagnostic remains
AND fresh Attempt 3 launcher/report evidence is complete
```

Then push implementation and parent task branches, return control to
`moda_architect`, and STOP.

Do not implement Phase 4 live HTTP execution/testing.

#### Historical Attempt 1 review

#### Attempt 1 review — 2026-09-25

Reviewed implementation `e51f3b2` and parent report `ea3e0493` against the complete
COMMERCE-021 task contract and the accepted COMMERCE-020/023 boundaries.

The task was eligible to execute: COMMERCE-019, COMMERCE-020, COMMERCE-023,
COMMERCE-005 and COMMERCE-006 are Complete in the submitted parent snapshot.

The implementation contains useful work that MUST be preserved:

- Declarative and JavaScript request modes exist;
- the request UI exposes path, query mappings and bounded safe static headers;
- request-construction preview is labelled as non-live;
- DIRECT response processing exists alongside Visual and JavaScript;
- Save and Validate are visibly separate lifecycle operations;
- Save uses the Commerce-owned draft schema at the immediate UI boundary;
- fixture controls were removed from the main External HTTP visual editor;
- PLATFORM_SUPER_ADMIN remains the only role shown a publish control;
- selected-shop/Connections handoff behavior is retained.

Attempt 1 is not accepted because several task-owned runtime contracts are incomplete
and the required executable UI validation did not run.

The following is the complete and authoritative Attempt 2 correction contract. Do
not infer additional work from chat history and do not implement Phase 4 live HTTP
testing.

##### A1-R1 — import the accepted External HTTP validation/preview Server Actions

Change:

```text
src/studio/tools/tool-editor.tsx
```

The submitted implementation currently imports:

```ts
import {
  previewExternalRequestAction,
  validateExternalToolDefinitionAction
} from "../../commerce/tool-authoring/server-actions";
```

That module exports the COMMERCE-019 common actions:

```text
validateToolDefinitionAction
validateToolArgumentsAction
```

and does NOT export the COMMERCE-023 External HTTP actions.

Use the accepted named Server Action module:

```text
src/studio/tools/external-validation-server-actions.ts
```

from the Tool UI.

The production Tool editor MUST call exactly:

```text
previewExternalRequestAction
validateExternalToolDefinitionAction
```

from that accepted COMMERCE-023 boundary.

Add a focused module-boundary regression that mocks the real External HTTP Server
Action module and proves:

```text
Preview request -> previewExternalRequestAction
Validate        -> validateExternalToolDefinitionAction
```

The common COMMERCE-019 validation Server Actions must not be substituted for the
External HTTP domain validator.

This correction must compile under `npm run typecheck`; editor-only diagnostics are
not sufficient proof.

##### A1-R2 — make incomplete DRAFT persistence round-trip through the Studio boundary

R5 requires:

```text
Save draft
-> CommerceToolDraftDefinitionSchema
-> incomplete authoring state may persist
-> reload/edit must still work
```

The submitted UI parses with `CommerceToolDraftDefinitionSchema`, but the surrounding
Studio DTO/read boundary still assumes every DRAFT is a full
`CommerceToolDefinition`:

```text
src/studio/contracts.ts
  ToolRevision status DRAFT -> definition: ToolDefinition
  createToolDraft.proposedDefinition -> ToolDefinition
  updateToolDraft.definition         -> ToolDefinition

src/commerce/integration/studio/services.ts
  every stored Tool revision -> CommerceToolDefinitionSchema.parse(...)
```

The publication lifecycle already validates create/update DRAFT writes through
`CommerceToolDraftDefinitionSchema`, so the current read/type boundary is inconsistent
with the persisted contract. A syntactically valid but incomplete DRAFT can be stored
and then fail when it is re-read.

Correct the same-repository Studio boundary so:

```ts
type ToolRevision =
  | {
      status: 'DRAFT';
      definition: ToolDraftDefinition;
      ...
    }
  | {
      status: 'PUBLISHED';
      definition: PublishedToolDefinition; // full CommerceToolDefinition
      ...
    };
```

and:

```text
createToolDraft.proposedDefinition -> ToolDraftDefinition
updateToolDraft.definition         -> ToolDraftDefinition
```

Align the explicit TypeScript input annotations on the publication lifecycle
create/update DRAFT methods with the draft schema they already parse.

When projecting publication state into Studio DTOs:

```text
DRAFT     -> CommerceToolDraftDefinitionSchema.parse(...)
PUBLISHED -> CommerceToolDefinitionSchema.parse(...)
```

Do NOT weaken the PUBLISHED contract and do NOT make publication accept an incomplete
definition.

The Tool editor must safely hydrate an incomplete DRAFT. It must not unconditionally
cast/parse a DRAFT as a full `ToolDefinition`.

Required executable round-trip regression:

```text
1. start from an EXTERNAL_HTTP DRAFT whose execution object is authorable
2. set a syntactically valid but intentionally incomplete draft-only inputSchema
   and/or responseTemplate object that CommerceToolDraftDefinitionSchema accepts but
   CommerceToolDefinitionSchema rejects
3. Save draft succeeds
4. re-read the Tool through the same Studio get/list boundary
5. no full-definition parse exception occurs
6. re-render the editor for that DRAFT
7. the exact incomplete JSON buffer is still present
8. Save draft may run again
9. Validate reports structural issues
10. Publish remains unavailable/blocked until the full definition is valid
```

Do not add a compatibility conversion or silently replace the incomplete persisted
object with a valid default.

##### A1-R3 — make DIRECT response mode a real controlled mode and protect destructive switches

Change:

```text
src/studio/external-http/editor.tsx
tests/external-tools-ui.test.tsx
```

The submitted response-mode `<select>` currently computes:

```ts
value={
  execution.responseProcessing.kind === "JAVASCRIPT"
    ? "JAVASCRIPT"
    : "VISUAL"
}
```

so a persisted `DIRECT` definition renders the selector as `VISUAL`.

Its change handler also types only:

```ts
"VISUAL" | "JAVASCRIPT"
```

even though `switchMode()` accepts `DIRECT`.

Required controlled value:

```text
JAVASCRIPT -> JAVASCRIPT
DIRECT     -> DIRECT
OBJECT     -> VISUAL
LIST       -> VISUAL
```

and the change handler must admit all three UI values:

```text
DIRECT
VISUAL
JAVASCRIPT
```

The destructive response-mode guard is also too narrow. `processingDirty` currently
compares only `responseProcessing`, while switching mode may reset/drop response
state affected by:

```text
responseProcessing
responseFormat
resultPath
resultSchema
```

Use a deterministic response-mode dirty comparison containing all response-mode-owned
fields above, or an equivalent correctly scoped guard. The currently passed
`draftDirty` prop must not remain an unused misleading contract.

Required regressions:

```text
persisted DIRECT -> select visibly has value DIRECT

DIRECT -> VISUAL can be selected directly

edit Direct resultPath (or another response-mode-owned field)
then select JAVASCRIPT
-> destructive-switch confirmation appears
-> Keep editing preserves DIRECT + edited value
-> Discard changes and switch moves to JAVASCRIPT

same protection applies to a dirty Visual/JavaScript response configuration
```

Do not prompt merely because unrelated Tool metadata changed if a precise response
configuration dirty comparison is available.

##### A1-R4 — distinguish invalid preview JSON from a rejected non-mutating Server Action

Change:

```text
src/studio/external-http/editor.tsx
tests/external-tools-ui.test.tsx
```

The submitted `previewRequest()` wraps both JSON parsing and the awaited Server Action
inside one `try/catch`. Therefore a rejected/lost non-mutating preview call is shown
as:

```text
Tool arguments must be valid JSON.
```

That is incorrect.

Required behavior:

```text
JSON.parse(requestArguments) fails
-> exact local JSON/input message
-> Server Action not called

Server Action returns explicit error
-> display its explicit code/message
-> no UNCONFIRMED

Server Action Promise rejects / transport fails
-> display bounded INTERNAL_ERROR-style preview failure
-> no UNCONFIRMED
-> do not claim the JSON is invalid
```

Use separate parse and await error boundaries.

Add focused tests for all three cases.

##### A1-R5 — remove fixture-led response-JavaScript testing from the production Tool editor

R6 applies to the entire production Tool editor, not only the Visual editor.

The submitted `ToolEditor` still composes:

```text
ProductionCodeResponsePanel
fixtureId = externalHttpPort.listSamples()[0].id
externalResponseFixture = externalHttpPort.listSamples()[0].sample
```

The accepted `ProductionCodeResponsePanel` renders a fixture-led human workflow,
including:

```text
Raw response sample
Run sample
Check run status
fixture-backed preview execution
```

That remains a synthetic "test this Tool" path in the production Tool editor and
violates R6.

For the Phase 3 production EXTERNAL_HTTP JavaScript response mode, expose authoring
only:

```text
CodeMirror/CodeEditor source editing
transform(response) contract/help
draft persistence
authoritative structural Validate
```

Do NOT expose in the normal production Tool editor:

```text
fixture selector/sample body
Run sample
Check run status
Cancel run
fixture-backed preview execution
synthetic sample completion as publication evidence
```

You may reuse the existing `CodeEditor` directly or introduce a small authoring-only
panel inside the existing code-response domain. Do not delete the fixture-capable
ARCH-020 panel if automated/developer-only tests still require it.

Update the old regression:

```text
composes the production JavaScript response panel in the tool detail path
```

so it proves the new production authoring-only boundary instead.

Required production UI regression in JavaScript response mode:

```text
Code editor visible
Save/authoring capability visible
Raw response sample absent
Run sample absent
Check run status absent
Cancel run absent
synthetic fixture values absent
```

##### A1-R6 — prove Save / Validate / Publish lifecycle separation

Add focused UI coverage for the exact R5 lifecycle:

```text
Save draft
-> can persist a draft-valid/full-invalid definition
-> does not call authoritative Validate
-> does not require live-test evidence

Validate
-> invokes COMMERCE-023 validateExternalToolDefinitionAction
-> valid result shows:
   "Definition passed authoritative validation. Live test is required before publication."
-> performs no mutation/UNCONFIRMED

PLATFORM_ADMIN
-> can Save + Validate
-> no publish control

PLATFORM_SUPER_ADMIN
-> publish control visible
-> requires clean saved + current authoritative validation
-> publication result LIVE_TEST_REQUIRED remains visibly identifiable
-> LIVE_TEST_REQUIRED does not become generic INTERNAL_ERROR or UNCONFIRMED
```

Do not treat the existing end-to-end test named "...and publish" as satisfying this
requirement: the current test stops after Save and does not execute Validate or the
Phase 3 publication gate.

##### A1-R7 — execute the required tests; unavailable Vitest is not acceptance evidence

Attempt 1 did not execute Vitest:

```text
sh: vitest: command not found
```

and did not run repository TypeScript validation. The task therefore has no
executable proof for its focused UI changes.

Use the canonical prepared Attempt 2 worktree and the repository's normal dependency
setup. Do not modify `package.json`/lockfiles merely to bypass a missing local
installation.

If the declared dependencies cannot be made available through the normal repository
workflow, return the task `blocked` with the exact environment/dependency condition
instead of returning it to `review`.

Once dependencies are available, run exactly:

```bash
npm run test:arch020-external-tools-ui

npm exec vitest run \
  tests/external-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx

npm run typecheck

npm exec eslint \
  src/studio/external-http/editor.tsx \
  src/studio/tools/tool-editor.tsx \
  src/studio/contracts.ts \
  src/commerce/integration/studio/services.ts \
  src/commerce/publication/lifecycle.ts \
  tests/external-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx

git diff --check
```

If A1-R2 requires another directly affected focused test file, add it to both the
Vitest and ESLint commands.

All focused tests must execute with zero skips.

There must be zero task-owned TypeScript diagnostics in:

```text
src/studio/external-http/editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/contracts.ts
src/commerce/integration/studio/services.ts
src/commerce/publication/lifecycle.ts
tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

In particular, the wrong Server Action import and draft/full-definition type mismatch
must be absent.

##### A1-R8 — reconcile task metadata, acceptance boxes and fresh Attempt 2 launcher evidence

The submitted task currently has:

```yaml
status: review
executor: copilot
claimed_at: 2026-09-25T17:15:29Z
attempt: 1
```

A review handoff must not retain an active claim.

Attempt 2 must record the exact fresh launcher-prepared:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-021
implementation branch = task/ARCH-021-COMMERCE-021
start-of-attempt parent synchronization
start-of-attempt implementation synchronization
Attempt 2 claim evidence / commit
recursive submodule materialization
database submodule commit
implementation commit
final parent report commit
push parity
clean parent worktree
clean implementation worktree
```

Do not reuse or infer Attempt 1 values.

After the executable validation passes, reconcile every satisfied
`## Acceptance Criteria` and `## Validation` checkbox to `[x]`.

Before handoff set exactly:

```yaml
status: review
attempt: 2
executor: null
claimed_at: null
```

##### Attempt 2 stop condition

Return to architect review only when:

```text
correct COMMERCE-023 Server Actions are wired
AND incomplete DRAFT save -> Studio reread -> editor round-trip works
AND PUBLISHED remains full-definition-only
AND DIRECT selector/control + destructive mode guard are correct
AND preview JSON vs Server Action rejection is distinguished
AND no synthetic fixture-led response-JS test workflow appears in production
AND Save/Validate/LIVE_TEST_REQUIRED role/lifecycle UI is executable
AND focused Vitest + typecheck + lint + diff validation passes
AND no task-owned diagnostic remains
AND the fresh Attempt 2 launcher/report packet is complete
```

Then push implementation and parent branches, return control to
`moda_architect`, and STOP.

Do not implement Phase 4 live HTTP execution/testing.

### Reviewed Files

- `src/studio/external-http/editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/external-validation-server-actions.ts`
- `src/commerce/tool-authoring/server-actions.ts`
- `src/studio/contracts.ts`
- `src/commerce/integration/studio/services.ts`
- `src/commerce/publication/lifecycle.ts`
- `src/commerce/tool-definition/contracts.ts`
- `src/studio/code-response/code-response-panel.tsx`
- `src/studio/code-response/production-panel.tsx`
- `tests/external-tools-ui.test.tsx`
- Completion Report

### Validation Reviewed

Submitted Attempt 1 evidence:

```text
editor diagnostics/get_errors: no reported diagnostics
git diff --check: PASS
npm run test:arch020-external-tools-ui: NOT EXECUTED
  -> sh: vitest: command not found
repository typecheck: NOT RUN
```

Static inspection identifies a task-owned compile boundary issue: `tool-editor.tsx`
imports the COMMERCE-023 External HTTP actions from the COMMERCE-019 common action
module, which does not export those symbols.

Static inspection also identifies that the draft write schema and Studio read/DTO
boundary disagree, DIRECT response mode does not control its `<select>` value, and
the production response-JavaScript path still composes fixture-led sample execution.

### Architecture Conformance

Changes Requested. The request/response authoring direction is correct, but R5/R6 and
the accepted COMMERCE-023/COMMERCE-016 boundaries are not yet implemented end-to-end.
No database, Shared or cross-repository redesign is required.

### Follow-up

Return this same task through `/moda-task ARCH-021-COMMERCE-021` for Attempt 2.

`ARCH-021-COMMERCE-022` remains independently Ready and is not gated by this rework.
Do not start Phase 4 live-test work.
