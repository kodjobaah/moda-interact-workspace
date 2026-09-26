---
id: ARCH-021-COMMERCE-045
architecture_id: ARCH-021
title: Complete External HTTP Response-tab authoring UX
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
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-043
  - ARCH-021-COMMERCE-044
  - ARCH-021-COMMERCE-006
  - ARCH-021-COMMERCE-039
enables: []
created: 2026-09-26
updated: 2026-09-26
---

# Complete External HTTP Response-tab authoring UX

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make the External HTTP Response tab a coherent authoring/validation surface for Direct, Visual and JavaScript processing by wiring the existing JavaScript panel into local new-Tool authoring, replacing duplicate path/schema controls with mode-specific concepts, preserving raw local edits and per-mode drafts, and presenting COMMERCE-043/044 derived contracts and diagnostics in the tab where they belong.

## Context

Manual review identified several independent presentation/behaviour problems in the completed Phase 3 Response tab:

- new-Tool JavaScript mode displays the stale message `JavaScript code editor is unavailable until COMMERCE-027 provides its panel`, even though COMMERCE-006/021 already provide the production response-code editor for persisted drafts;
- `Result path` and `Direct result path` edit the same `execution.resultPath` property, creating a false impression that they are different concepts;
- Visual mode exposes both visual projection controls and always-visible editable `Advanced response processing JSON`, making one processing definition look like two separate authoring obligations;
- Visual mode separately exposes editable `Response shape JSON` even though COMMERCE-043 makes that result contract derivable from the projection authoring;
- invalid media types, paths, filters or JavaScript can be discarded/reverted instead of remaining visible with actionable errors;
- destructive mode switching can reset the previous mode configuration;
- the tab does not expose a Response-only authoritative validation action/status.

This task composes the accepted response authoring capabilities into one understandable UI. It remains zero-provider-I/O and does not add Phase 2 navigation gating.

## Scope

Primary files:

```text
src/studio/external-http/response-tab.tsx
src/studio/external-http/editor.tsx
src/studio/code-response/code-editor.tsx          # only generic/request-specific sizing capability where safe
src/studio/tools/new-tool-editor.tsx               # new-Tool JavaScript panel/local mode composition
src/studio/tools/tool-editor.tsx                   # persisted-DRAFT parity where shared Response editor is composed
src/studio/tools/external-validation-server-actions.ts
src/studio/external-http/ports.ts
app/styles.css

tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

Additional directly affected Response-authoring UI tests may change when required.

## Out of Scope

- Request-tab follow-up COMMERCE-040..042.
- Live provider execution, DNS or credential access.
- Running response JavaScript against a real/sample provider response.
- Automatic Direct/JavaScript result-schema inference from observed output; defer until Test-tab review establishes the sample/live-test contract.
- Agent-contract/response-template redesign.
- Review-tab redesign.
- Phase 2 tab locking, mandatory Next/Previous or progression gating.
- Database schema changes.
- Persisting inactive mode drafts or temporarily invalid local form state.

## Requirements

### R1 — one clear Response-tab purpose

The Response tab must present the authoring pipeline truthfully:

```text
provider response
    -> optional Source path (Direct/Visual JSON modes)
    -> selected processing mode
    -> processed Tool result
    -> result contract
```

The tab validates the configuration. It does not claim to have executed a real provider response; that belongs to Test.

### R2 — rename and de-duplicate resultPath as Source path

Present `execution.resultPath` as one user-facing concept:

```text
Source path
```

Help text:

```text
Select the part of the JSON response to process. Leave empty to use the response root.
```

Show Source path only for:

```text
Direct
Visual rules
```

Do not show Source path for JavaScript because `transform(response)` receives the complete bounded response object and chooses what to consume.

Remove the duplicate `Direct result path` control. There must be only one control bound to `execution.resultPath` in a given mode.

### R3 — wire the real JavaScript response panel in new-Tool authoring

New local-only Tool authoring must use the already-accepted JavaScript response editor/composition rather than the stale COMMERCE-027 placeholder.

Remove the message:

```text
JavaScript code editor is unavailable until COMMERCE-027 provides its panel.
```

JavaScript mode must provide a useful multi-line code editor for the canonical:

```js
function transform(response) {
  ...
}
```

contract, with line numbers, scrolling and a usable/resizable editing area consistent with the accepted CodeMirror integration.

The source remains browser-local for a new Tool until final Create.

### R4 — preserve invalid raw Response edits locally

Response authoring must distinguish:

```text
raw local form state
canonical local Tool draft
durable Tool state
```

Temporarily invalid values, including malformed media-type text, Source paths, filter lists, advanced text where retained, JavaScript source or explicit Direct/JavaScript result-schema JSON, MUST remain visible long enough to show an actionable error.

Do not silently keep only the last valid value without telling the author what is wrong.

Only schema-valid values are promoted into the canonical local Tool draft. For a new Tool, neither raw form state nor canonical local draft state is durably persisted before final Create from Review.

### R5 — Response-local validation action and diagnostics

Expose COMMERCE-044 Response validation in the Response tab with a clear action/status such as:

```text
Validate response
```

Display mode-specific issues next to the affected control/row where practical and provide a concise Response-level summary for non-field-specific issues.

A previous validation success becomes stale immediately when any relevant Response field changes.

Do not require navigation to Test or Review to discover a Response configuration error.

Validation failures do not disable other tabs in this phase.

### R6 — Visual mode is the primary authoring surface; advanced processing JSON is not a second required editor

For Visual mode, projection/filter/sort/limit controls are the primary processing authoring surface.

Replace the always-visible editable:

```text
Advanced response processing JSON
```

with an explicitly secondary/collapsible representation such as:

```text
View processing JSON
```

The representation should be read-only unless there is an architecture-approved reason to support a separate advanced editing mode with deterministic round-trip semantics. This task must not require the administrator to maintain the visual controls and raw processing JSON independently.

### R7 — Visual result contract is derived, not separately authored

Consume COMMERCE-043 so each Visual projected field exposes at least:

```text
Output name
Path
Type
Omit if missing
```

Changing those controls updates both the canonical `responseProcessing` and deterministic Visual `resultSchema` coherently.

Do not show an independently editable `Response shape JSON` textarea in Visual mode.

Instead present a concise derived-contract summary and an optional read-only disclosure such as:

```text
Derived result contract
[ View JSON ]
```

For LIST mode, the preview must truthfully show the canonical `{ items: [...] }` result envelope.

### R8 — Direct result contract remains explicit for now

Direct mode cannot derive value types from Source path alone.

Until Test-tab review establishes sample-based schema generation, keep one clearly labelled explicit contract editor:

```text
Processed result schema
```

Do not label it `Response shape JSON`, which can be confused with the provider's raw response shape.

The editor must retain invalid local JSON with an in-tab error rather than reverting silently.

### R9 — JavaScript result contract remains explicit for now

JavaScript output cannot be reliably inferred from source code alone.

Keep a clearly labelled explicit:

```text
Processed result schema
```

for JavaScript mode until Test-tab work defines inference/generation from an observed transformed sample.

Compilation and schema validation occur in Response; executing the transform against a response belongs to Test.

### R10 — preserve independent per-mode local drafts

Switching between:

```text
Direct
Visual
JavaScript
```

must not destroy the other modes' unsaved local authoring state during the current editor session.

Maintain local mode drafts so an administrator can compare modes and return without losing work.

Only the currently selected mode is promoted into the canonical local Tool definition and eventually persisted by final Create/Save. Inactive mode drafts are UI convenience only and must never be durably persisted.

A destructive switch confirmation may remain where needed for persisted-draft semantics, but it must not be the only mechanism protecting new local authoring work.

### R11 — mode-specific explanatory text

Present concise mode descriptions:

```text
Direct
Returns the JSON selected by Source path unchanged.

Visual rules
Projects, filters, sorts and limits JSON using the authored rules.

JavaScript
Runs bounded transform(response) against the complete response object.
```

Do not expose implementation/task-history language such as COMMERCE task numbers in production UI.

### R12 — no Phase 2 gating

All authoring tabs remain freely navigable regardless of Response validity.

This task must not add locked tabs, mandatory Next/Previous progression or completion state machines.

## Work Items

- [ ] Replace duplicate Result/Direct-result controls with one contextual Source path.
- [ ] Wire the existing JavaScript response editor into new local-only Tool authoring and remove stale COMMERCE-027 copy.
- [ ] Give JavaScript response editing a useful multi-line/resizable presentation.
- [ ] Preserve invalid Response form values locally with field/row diagnostics.
- [ ] Add `Validate response` using COMMERCE-044 and stale-success invalidation.
- [ ] Make Visual controls the single primary processing editor and move processing JSON behind a read-only/secondary disclosure.
- [ ] Add Visual projected-field Type authoring and COMMERCE-043 derived result-contract presentation.
- [ ] Rename explicit Direct/JavaScript result-schema authoring to `Processed result schema`.
- [ ] Preserve independent Direct/Visual/JavaScript local mode drafts across switches.
- [ ] Add focused regressions for new/persisted draft parity, local-vs-durable state and no tab gating.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-006
accepted production JavaScript response-panel composition

ARCH-021-COMMERCE-039
new-Tool local-only authoring and final-create persistence invariant

ARCH-021-COMMERCE-043
Visual derived result contract

ARCH-021-COMMERCE-044
Response-only authoritative validation
```

No new cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-043
- ARCH-021-COMMERCE-044
- ARCH-021-COMMERCE-006
- ARCH-021-COMMERCE-039

## Enables

None.

## Acceptance Criteria

- [ ] Response tab uses one `Source path` control for Direct/Visual and none for JavaScript.
- [ ] The duplicate `Direct result path` control no longer exists.
- [ ] New-Tool JavaScript response authoring uses the real CodeMirror response editor; no COMMERCE-027 placeholder remains.
- [ ] JavaScript editor has a usable multi-line, scrollable/resizable presentation.
- [ ] Temporarily invalid Response values remain visible locally with actionable Response-tab errors.
- [ ] `Validate response` validates only Response configuration and displayed success becomes stale on relevant edits.
- [ ] Visual processing JSON is no longer an always-visible second required editor.
- [ ] Visual fields expose Output name, Path, Type and Omit-if-missing semantics.
- [ ] Visual `resultSchema` is generated from COMMERCE-043 and shown only as derived/read-only contract information.
- [ ] Direct and JavaScript modes use the clearer `Processed result schema` label and retain explicit schema authoring until Test-tab sample inference is designed.
- [ ] Direct/Visual/JavaScript local authoring survives mode switches within the session.
- [ ] Only the active mode enters the canonical local definition; inactive mode drafts and invalid raw form state are not durably persisted.
- [ ] Errors are shown in Response; other tabs remain freely navigable.
- [ ] No live provider I/O, database migration or Phase 2 gating is introduced.

## Validation

- [ ] focused External HTTP Response-tab UI tests for Direct/Visual/JavaScript
- [ ] focused new-Tool local-only JavaScript panel regression
- [ ] focused Visual derived-contract UI/round-trip tests
- [ ] focused invalid raw-state retention and Response validation diagnostics
- [ ] focused mode-switch retention tests for new and persisted-DRAFT authoring where applicable
- [ ] explicit proof that Response validation performs zero provider/credential I/O
- [ ] existing External UI/common Tool-authoring regression packet required by repository scripts
- [ ] targeted TypeScript diagnostics or repository typecheck with baseline reconciliation
- [ ] targeted ESLint for changed files
- [ ] `git diff --check`

## Stop Condition

After the Response tab presents coherent Direct/Visual/JavaScript authoring, local diagnostics, derived Visual result contract, JavaScript editor wiring and per-mode draft preservation with all required validation complete, set the task to `review`, complete the Completion Report and STOP. Do not begin Test-tab, Agent-contract, Review-tab or Phase 2 gating work.

## Implementation Notes

The current code exposes `execution.resultPath` twice and disables the first control for Direct while exposing the second. Treat this as one Source-path concept, not two stored properties.

For Visual mode, do not modify Shared merely to persist the UI's selected scalar type inside response-processing fields. The generated canonical `resultSchema` is the durable result type contract and is sufficient to reconstruct compatible Visual field types on edit.

Direct/JavaScript sample-based result-schema generation is intentionally deferred because it depends on the later Test-tab contract for observed processed output. Do not guess schema types from Source path or JavaScript source text.

## Completion Report

### Status
Not Started

### Files Changed
None

### Work Completed
None

### Validation Results
None

### Deviations
None

### Assumptions
None

### Unresolved Issues
None

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
