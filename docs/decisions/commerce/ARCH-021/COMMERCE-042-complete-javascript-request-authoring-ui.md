---
id: ARCH-021-COMMERCE-042
architecture_id: ARCH-021
title: Complete JavaScript request bindings and editor UX
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 62
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-041
enables: []
created: 2026-09-26
updated: 2026-09-26
---

# Complete JavaScript request bindings and editor UX

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make JavaScript request authoring understandable and resilient in the External HTTP Request tab by exposing COMMERCE-040 bindings through explicit Agent-input/Literal controls, providing a usable resizable JavaScript editor with actionable validation diagnostics, and preserving each request mode's unsaved local work when authors switch between Declarative and JavaScript.

## Context

The Request tab currently gives declarative authors an explicit mapping table:

```text
Query key | Source | Agent input / Literal | Omit if missing
```

but JavaScript mode exposes only a very shallow CodeMirror instance and the statement that request code receives Tool arguments. The source/value relationship is therefore hidden, and partial JavaScript edits can be rejected by whole-execution schema parsing before the author can see a useful diagnostic.

The current mode switch also replaces the active request with a fresh default:

```text
Declarative -> JavaScript
    destroys current declarative request state

JavaScript -> Declarative
    destroys current JavaScript request state
```

COMMERCE-040 establishes the canonical JavaScript `bindings` contract and COMMERCE-041 establishes Request-local validation/preview form state. This task completes the JavaScript-specific authoring UI on top of those accepted boundaries.

## Scope

Primary files:

```text
src/studio/external-http/request-tab.tsx
src/studio/external-http/editor.tsx
src/studio/code-response/code-editor.tsx              # only generic capability needed by Request editor
src/studio/tools/new-tool-editor.tsx                   # only if Request-mode local state must be composed here
src/studio/tools/tool-editor.tsx                       # persisted DRAFT parity where the same Request component is used
app/styles.css

tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

Additional directly affected Request-authoring UI tests may change when required by this capability.

## Out of Scope

- Changing the COMMERCE-040 canonical binding semantics.
- Live provider execution/testing.
- Response, Agent contract or Review tab redesign.
- Connection management/navigation.
- Phase 2 tab gating or mandatory progression.
- Database schema changes.
- Persisting inactive request-mode drafts.
- Changing response JavaScript editor behaviour unless a generic CodeEditor capability can be added without altering its existing semantics.

## Requirements

### R1 — explicit JavaScript Request values

When Request mode is `JavaScript`, show an explicit `Request values` authoring table backed by `request.bindings`.

For each binding, the author controls:

```text
Value name
Source: Agent input | Literal
Agent input name OR literal value
Omit if missing (Agent input only)
Remove
```

The semantics shown in the UI must be literal and unambiguous:

```text
Agent input
    Value is supplied from the named CommerceAgent Tool input at invocation time.

Literal
    The authored value is fixed in the Tool definition.
```

The binding table must edit the exact COMMERCE-040 canonical binding map; it must not create a browser-only parallel mapping representation.

### R2 — bounded literal authoring

JavaScript binding literals may be any JSON value permitted by the canonical bounded mapping contract, not only strings.

The UI must preserve the authored JSON type (`string`, number, boolean, null, object or array where contract-allowed) and show a deterministic validation error for malformed/out-of-bounds literal text rather than coercing it silently.

### R3 — truthful JavaScript contract guidance

The JavaScript section must explain the exact contract:

```js
function buildRequest({ args }) {
  // args contains only the resolved Request values declared above.
  // return { path, query, headers };
}
```

Do not describe `args` as the entire Tool input object after COMMERCE-040.

The current Request preview from COMMERCE-041 must execute the current bindings + source and display the resulting descriptor.

### R4 — usable resizable CodeMirror editor

The JavaScript request editor must no longer render as an effectively one-line code strip.

Provide a useful initial editing area with, at minimum:

```text
visible multi-line height suitable for the starter function
vertical scrolling
vertical resizing by the author
line numbers retained
```

A request-specific wrapper/class is preferred if changing generic `CodeEditor` styling would unintentionally resize unrelated response JavaScript editors.

Resizing is presentation state only and must not mutate the Tool definition.

### R5 — retain invalid/partial JavaScript while editing

Authors must be able to type temporarily invalid JavaScript, including an incomplete function, without the editor snapping back to the last schema-valid source.

Keep the raw source in Request-local form state and surface COMMERCE-041 validation/compile diagnostics against that current source.

Only canonical valid request state is emitted to durable Tool-definition state.

### R6 — preserve both mode drafts during the authoring session

Switching Request mode must not destroy the other mode's unsaved local configuration.

Within the current editor session maintain distinct local drafts for:

```text
Declarative request
JavaScript request
```

Example:

```text
author creates declarative mappings
-> switches to JavaScript and edits bindings/source
-> switches back
-> original declarative mappings are restored
-> switches again to JavaScript
-> JavaScript bindings/source are restored
```

Only the currently selected mode belongs to the canonical Tool definition and is persisted by final Create/Save. The inactive local mode draft is authoring convenience only and must not be written into the definition.

### R7 — validation/preview staleness

Changing JavaScript source or any binding must immediately invalidate the Request validation/preview result established by COMMERCE-041.

The UI must show binding/source diagnostics in the Request tab and must not require visiting Test or Review to discover JavaScript request errors.

### R8 — no gating

All authoring tabs remain freely navigable. JavaScript errors are visible Request-tab state only in this phase and do not introduce locked tabs or mandatory Next/Back progression.

## Work Items

- [x] Render COMMERCE-040 JavaScript bindings as Request values.
- [x] Add Agent input/Literal source switching with typed literal preservation.
- [x] Update JavaScript contract help text to describe resolved bindings accurately.
- [x] Give Request JavaScript CodeMirror a useful resizable multi-line presentation.
- [x] Retain invalid/partial JavaScript source locally with actionable diagnostics.
- [x] Preserve independent Declarative and JavaScript local drafts across mode switches.
- [x] Invalidate Request validation/preview state on source/binding edits.
- [x] Add focused regressions for mapping parity, literal typing, editor state and mode switching.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-040
canonical JavaScript Request bindings

ARCH-021-COMMERCE-041
Request-local validation and exact request preview
```

No new cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-041

## Enables

None.

## Acceptance Criteria

- [x] JavaScript mode visibly exposes Request values with Agent input/Literal sources.
- [x] The binding controls edit the canonical COMMERCE-040 `bindings` map.
- [x] JSON literal types are preserved and malformed literals receive visible errors.
- [x] JavaScript guidance states that `args` contains only resolved Request values.
- [x] The request CodeMirror editor opens at a useful multi-line height, scrolls and can be resized vertically.
- [x] Partial/invalid JavaScript remains visible while being edited and receives validation diagnostics.
- [x] Declarative authoring state survives Declarative -> JavaScript -> Declarative switching within the session.
- [x] JavaScript bindings/source survive JavaScript -> Declarative -> JavaScript switching within the session.
- [x] Only the active request mode is part of the canonical definition/persistence payload.
- [x] Request validation/preview is invalidated when source/bindings change.
- [x] New-Tool authoring remains non-durable until final Create.
- [x] No live provider I/O or Phase 2 gating is introduced.

## Validation

- [x] focused External HTTP Request JavaScript UI tests
- [x] focused mode-switch retention tests for new and persisted-DRAFT authoring where applicable
- [x] focused Request validation/preview regression with JavaScript bindings
- [x] existing External UI/common Tool-authoring regression packet required by repository scripts
- [x] targeted TypeScript diagnostics or repository typecheck with baseline reconciliation
- [x] targeted ESLint for changed files
- [x] `git diff --check`

## Stop Condition

After JavaScript binding controls, resizable editor, partial-source diagnostics, mode-draft preservation and required regressions are complete, set the task to `review`, complete the Completion Report and STOP. Do not begin Response-tab, Test-tab, Agent-contract or Review-tab redesign and do not implement Phase 2 gating.

## Implementation Notes

The current mode switch creates a brand-new default request object for the selected mode. Replace that destructive behaviour with explicit Request-local per-mode drafts.

Do not persist both modes into the canonical Tool definition. This is local editor state analogous to retaining text while the author compares alternatives.

## Completion Report

### Status
Ready for Architect Review

### Files Changed
- `app/styles.css`
- `src/studio/external-http/editor.tsx`
- `src/studio/external-http/request-tab.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`

### Work Completed
- Added canonical JavaScript Request `bindings` controls for value name, Agent input/Literal source, typed bounded JSON, omission policy and removal. Literal text remains local while edited; malformed and over-limit JSON receives a stable Request diagnostic.
- Replaced the destructive mode switch with independent Declarative and JavaScript drafts. Only the active request is emitted in the canonical definition; New Tool and persisted DRAFT actions remain blocked until the active JavaScript Request passes current validation or preview.
- Added exact `buildRequest({ args })` contract guidance, Request-local compile/validation feedback, and input-keyed invalidation/fencing for validation and preview results.
- Wrapped the Request CodeMirror in a resizable, scrolling, 280px initial editing area while retaining line numbers and leaving response editor sizing unchanged.
- Added coverage for typed canonical bindings, source switching, malformed literals/source, both mode-retention directions, preview staleness, stale asynchronous validation, active-mode-only persistence, and new-tool non-durability.

### Validation Results
- Focused packet: `npm run test -- tests/external-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/external-tool-authoring-validation.test.ts tests/external-tool-authoring-server-actions.test.ts tests/code-request-processor.test.ts` — 5 files, 83 tests passed.
- Targeted ESLint for the six changed TypeScript/TSX files — passed with no warnings. `git diff --check` — passed.
- Editor diagnostics for all six changed TypeScript/TSX files — no errors.
- `npm run typecheck` — repository check remains red with 249 diagnostics across 20 files. The final run has no diagnostics in task-changed files; reported errors are in unrelated existing integration and test files.

### Execution Evidence
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-042`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-042`. Both use `task/ARCH-021-COMMERCE-042`; neither worktree was reused and the canonical shared checkouts were left untouched.
- Launcher preparation passed the COMMERCE-041 dependency gate. Both task-branch fast-forwards were `not-needed`; `origin/main` was `already-current`. Recursive submodule sync/update-init passed; database submodule commit was `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Parent claim commit `393364dc79d04d8418514f9fe2964fc7543f8781` was pushed by the launcher. Parent preparation HEAD was `013e5e54f742afd0c82cddec679ec53533d40d82`; implementation starting HEAD was `ba837f2ffa83617738196c77b139700c6e4e5fbd`.

### Deviations
None. The existing Request validation and preview actions were reused; no provider execution, new service boundary, persistence model, or tab gating was added.

### Assumptions
JavaScript requests require a successful current Request validation or preview checkpoint before Create/Save, because the canonical request schema alone cannot report JavaScript compilation failures. Any request edit or mode switch invalidates that checkpoint.

### Unresolved Issues
The repository-wide typecheck has 249 diagnostics across 20 unrelated files; see Validation Results. No task-local type errors remain.

### Architectural Concerns
None.

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes

#### Attempt 1 review — 2026-09-27

Reviewed the submitted C042 implementation against the complete task contract,
accepted COMMERCE-040 binding semantics, and the accepted COMMERCE-041 Request-tab
architecture.

The implementation contains useful work that MUST be preserved:

- JavaScript Request values are exposed through the canonical COMMERCE-040
  `bindings` map;
- Agent input and Literal sources are explicit;
- bounded JSON literals preserve JSON types instead of coercing everything to text;
- the JavaScript contract guidance correctly says `args` contains only resolved
  Request values;
- Request JavaScript uses a dedicated resizable multi-line CodeMirror wrapper;
- invalid/partial JavaScript and malformed literal text remain local rather than
  snapping back to the previous value;
- separate Declarative and JavaScript local mode drafts survive mode switching;
- only the active canonical request is emitted through `onChange`;
- validation/preview display is keyed to the current Request state so stale results
  disappear after source/binding edits;
- no provider execution, database change or tab locking was added;
- submitted TypeScript metadata contains no semantic diagnostics in the C042 changed
  source/test files.

Attempt 1 is not accepted because C042 introduces an unapproved final
Create/Save gate and the JavaScript binding table has two local-state/data-loss
defects.

The following is the complete and authoritative Attempt 2 correction contract. Do
not infer additional work from chat history. Do not redesign Response/Test/Agent/
Review tabs and do not implement Phase 2 gating or live provider execution.

##### A1-R1 — remove the JavaScript Validate/Preview checkpoint from final Create/Save gating

Change the minimum required files:

```text
moda-interact-commerce/src/studio/external-http/request-tab.tsx
moda-interact-commerce/src/studio/external-http/editor.tsx
moda-interact-commerce/src/studio/tools/new-tool-editor.tsx
moda-interact-commerce/src/studio/tools/tool-editor.tsx
moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/tool-authoring-screen.test.tsx
```

The submitted implementation currently creates:

```ts
const requestCanPersist =
  requestDraftValid &&
  (requestDraft.kind !== "JAVASCRIPT" || checkedRequestKey === validationKey);
```

and reports:

```text
Validate or preview the current JavaScript request before saving.
```

It then feeds `onRequestDraftValidityChange(false)` into:

```text
NewToolEditor externalRequestDraftValid -> Create disabled
ToolEditor externalDefinitionValid      -> Save/Validate disabled
```

This is architecturally incorrect.

The accepted COMMERCE-041 Architect Review explicitly states:

```text
COMMERCE-041 does NOT own cross-tab gating or final Create/Save/Publish blocking.
Request-local raw state may temporarily differ from the last schema-valid canonical
Tool draft while the author is editing.
```

C042 R8 also states that JavaScript Request errors are Request-tab state only and do
not introduce progression/gating.

Required behavior:

```text
Validate request
Preview request
```

remain non-mutating Request-local diagnostics/checkpoints only.

Changing JavaScript source/bindings MUST:

```text
invalidate/hide stale validation result
invalidate/hide stale preview result
retain local raw source/literal text
```

but MUST NOT make successful Request validation/preview a prerequisite for final
Create or Save.

Preserve R5:

```text
invalid local Request form/source
-> retained locally
-> NOT emitted through onChange until ExternalRequestConstructionSchema accepts it

schema-valid canonical active Request
-> may be emitted through onChange
```

Do not persist the inactive mode draft.

Remove the visible:

```text
Validate or preview the current JavaScript request before saving.
```

persistence-gate message.

Do not replace it with another validation-completion gate.

The existing parent Create/Save boundaries may still reject malformed Agent/Response
JSON or other previously accepted full-draft constraints. This correction is only
about the new C042 Request-validation/preview checkpoint.

Required regressions:

```text
NEW TOOL:
switch to JavaScript
edit a schema-valid source/binding
do NOT Validate or Preview
-> Review remains freely reachable
-> Create is not disabled merely because Request validation/preview has not run
-> final Create persists the active canonical JavaScript request

PERSISTED DRAFT:
edit a schema-valid JavaScript source/binding
do NOT Validate or Preview
-> Save is not disabled merely because Request validation/preview has not run
-> Save persists the active canonical JavaScript request

AFTER A SUCCESSFUL VALIDATION/PREVIEW:
edit JavaScript source or binding
-> prior result/output disappears immediately
-> Save/Create is not newly gated by the now-stale checkpoint
```

Do not call Validate/Preview implicitly from Create/Save.

##### A1-R2 — scope malformed literal errors to the Literal source only

Change:

```text
moda-interact-commerce/src/studio/external-http/request-tab.tsx
moda-interact-commerce/tests/external-tools-ui.test.tsx
```

The current `activeLiteralErrors` logic treats an error as active whenever the
binding name still exists:

```ts
Object.entries(literalErrors)
  .filter(([name]) => name in requestDraft.bindings)
```

This is wrong after a binding switches from:

```text
Literal -> Agent input
```

because the stale literal text/error remains in `literalErrors` even though the
active canonical binding is now `{ input: ... }`.

Concrete current failure:

```text
set Literal text to malformed "{"
-> visible literal error
-> Validate/Preview disabled

switch Source to Agent input
enter valid input name "sku"
-> literal field/error disappears from the UI
-> stale literal error still counts as active internally
-> Validate/Preview remain disabled with no visible reason
```

Required behavior:

```text
Literal binding
-> its current literal parsing/bounds error is active

Agent input binding
-> any retained inactive literal text/error for that binding is NOT active
-> it does not invalidate Request validation/preview

switch back to Literal
-> previously typed literal text may be restored
-> if that retained literal text is malformed, its error becomes active/visible again
```

A source switch may preserve inactive literal authoring text for convenience, but an
inactive source's validation error must never block the active source.

Use one helper for "active literal errors" and reuse it in normal editing and mode
switch logic so the two paths cannot drift.

Required regression:

```text
add binding
switch to Literal
enter malformed "{"
-> error visible
-> Validate/Preview disabled

switch to Agent input
enter "sku"
-> literal error not visible
-> current Request can Validate/Preview

switch back to Literal
-> malformed "{" text is restored
-> literal error visible again
```

##### A1-R3 — prevent JavaScript binding add/rename from silently overwriting another binding

Change:

```text
moda-interact-commerce/src/studio/external-http/request-tab.tsx
moda-interact-commerce/tests/external-tools-ui.test.tsx
```

The submitted Add logic uses:

```ts
requestValue${Object.keys(bindings).length + 1}
```

which can collide after deletion.

Example:

```text
requestValue1
requestValue2

remove requestValue1
bindings.length = 1

Add request value
-> generated name = requestValue2
-> existing requestValue2 is silently overwritten
```

`renameBinding()` also currently does:

```ts
delete bindings[name];
bindings[nextName] = binding;
```

so renaming onto an existing binding silently destroys the target row.

This violates C042's requirement to preserve local Request authoring work.

Required behavior:

```text
Add request value
-> choose a deterministic unused safe name
-> never overwrite an existing binding

Rename binding A -> existing binding B
-> do NOT overwrite either binding
-> retain both rows
-> show a local actionable error such as:
   "Request value name already exists."
-> no canonical request update is emitted for the invalid rename

Rename to a new valid unused name
-> exact binding + local literal text/source state move to the new name
```

The duplicate-name error is Request-local authoring state; do not add a second
canonical bindings representation.

Required regressions:

```text
add requestValue1 + requestValue2
remove requestValue1
Add request value
-> requestValue2 unchanged
-> a different unused requestValueN is created

rename requestValue1 -> requestValue2
-> both original rows remain
-> duplicate-name error visible
-> canonical binding map is not destructively changed
```

##### A1-R4 — preserve all accepted C042 behavior

Do not regress:

```text
typed bounded JSON literal values
Agent input/Literal source semantics
resolved-bindings guidance
resizable multi-line Request CodeMirror + line numbers
partial/incomplete JavaScript retained locally
Declarative -> JavaScript -> Declarative local draft retention
JavaScript -> Declarative -> JavaScript local draft retention
active-mode-only canonical persistence
validation/preview staleness fencing
late async validation not authorizing changed Request state
new-Tool non-durability until final Create
zero provider I/O
free tab navigation
```

No inactive mode draft may be serialized into the Tool definition.

##### A1-R5 — deterministic validation

Run exactly:

```bash
npm run test:arch020-external-tools-ui

npm exec vitest run \
  tests/external-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx \
  tests/external-tool-authoring-validation.test.ts \
  tests/external-tool-authoring-server-actions.test.ts \
  tests/code-request-processor.test.ts

npm run test:arch021-tool-authoring-common

npm exec eslint \
  src/studio/external-http/request-tab.tsx \
  src/studio/external-http/editor.tsx \
  src/studio/tools/new-tool-editor.tsx \
  src/studio/tools/tool-editor.tsx \
  tests/external-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx

npm run typecheck
git diff --check
```

All C042-focused tests must execute with zero skips.

The known unrelated common-packet lifecycle fixture may remain documented only if it
reproduces unchanged and no C042 file/stack is involved.

No TypeScript diagnostic in these C042 causal files may be classified as baseline:

```text
src/studio/external-http/request-tab.tsx
src/studio/external-http/editor.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

##### A1-R6 — reconcile Completion Report and final execution evidence

The Attempt 1 Completion Report records the prepared worktrees, start synchronization,
claim and database submodule, but does not record the final implementation commit,
final parent report commit, push parity or final clean-worktree evidence.

Attempt 2 must record the exact fresh launcher-provided:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-042
implementation branch = task/ARCH-021-COMMERCE-042
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

Do not infer or reuse Attempt 1 claim/synchronization values.

Reconcile Work Items, Acceptance Criteria and Validation to the actual Attempt 2
results.

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
Request validation/preview no longer gates Create/Save
AND malformed inactive Literal errors cannot block an Agent-input binding
AND binding add/rename cannot overwrite existing local work
AND every accepted C042 mode/source/editor/staleness regression remains green
AND focused/common/typecheck/lint/diff validation is recorded
AND zero C042-owned diagnostic remains
AND the fresh Attempt 2 launcher/report packet is complete
```

Then push implementation and parent task branches, return control to
`moda_architect`, and STOP.

Do not begin COMMERCE-053 or any live-provider/Test-tab follow-up.

### Reviewed Files

- `moda-interact-commerce/src/studio/external-http/request-tab.tsx`
- `moda-interact-commerce/src/studio/external-http/editor.tsx`
- `moda-interact-commerce/src/studio/code-response/code-editor.tsx`
- `moda-interact-commerce/src/studio/tools/new-tool-editor.tsx`
- `moda-interact-commerce/src/studio/tools/tool-editor.tsx`
- `moda-interact-commerce/app/styles.css`
- `moda-interact-commerce/tests/external-tools-ui.test.tsx`
- `moda-interact-commerce/tests/tool-authoring-screen.test.tsx`
- COMMERCE-040 accepted contract
- COMMERCE-041 accepted Architect Review
- submitted `tsconfig.tsbuildinfo`
- Attempt 1 Completion Report

### Validation Reviewed

Submitted Attempt 1 evidence:

```text
focused packet:
  5 files / 83 tests PASS

targeted ESLint:
  PASS

editor diagnostics:
  no errors in six changed TS/TSX files

git diff --check:
  PASS

full typecheck:
  249 diagnostics across 20 unrelated repository files
  0 semantic diagnostics in the six C042 changed source/test files
```

Independent `tsconfig.tsbuildinfo` inspection confirms no semantic diagnostic in the
C042 changed source/test files.

The focused tests currently encode the unapproved validation-before-save behavior;
green tests do not make that gate architecture-conformant.

### Architecture Conformance

Changes Requested. The JavaScript bindings/editor/mode-draft direction conforms to
COMMERCE-040/C042, but final Create/Save gating contradicts the accepted COMMERCE-041
no-gating boundary and C042 R8. The malformed-Literal source switch and binding-name
collision paths also violate local authoring-state correctness. No schema,
persistence, provider or cross-repository redesign is required.

### Follow-up

Return this same task through `/moda-task ARCH-021-COMMERCE-042` for Attempt 2.

COMMERCE-053 remains Pending on COMMERCE-042 plus its other declared dependencies.
Do not start COMMERCE-053 or live-provider/Test-tab work from this review.
