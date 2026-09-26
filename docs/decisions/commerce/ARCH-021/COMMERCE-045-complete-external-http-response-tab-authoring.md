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
attempt: 1
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

- [x] Replace duplicate Result/Direct-result controls with one contextual Source path.
- [x] Wire the existing JavaScript response editor into new local-only Tool authoring and remove stale COMMERCE-027 copy.
- [x] Give JavaScript response editing a useful multi-line/resizable presentation.
- [x] Preserve invalid Response form values locally with field/row diagnostics.
- [x] Add `Validate response` using COMMERCE-044 and stale-success invalidation.
- [x] Make Visual controls the single primary processing editor and move processing JSON behind a read-only/secondary disclosure.
- [x] Add Visual projected-field Type authoring and COMMERCE-043 derived result-contract presentation.
- [x] Rename explicit Direct/JavaScript result-schema authoring to `Processed result schema`.
- [x] Preserve independent Direct/Visual/JavaScript local mode drafts across switches.
- [x] Add focused regressions for new/persisted draft parity, local-vs-durable state and no tab gating.

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

- [x] Response tab uses one `Source path` control for Direct/Visual and none for JavaScript.
- [x] The duplicate `Direct result path` control no longer exists.
- [x] New-Tool JavaScript response authoring uses the real CodeMirror response editor; no COMMERCE-027 placeholder remains.
- [x] JavaScript editor has a usable multi-line, scrollable/resizable presentation.
- [x] Temporarily invalid Response values remain visible locally with actionable Response-tab errors.
- [x] `Validate response` validates only Response configuration and displayed success becomes stale on relevant edits.
- [x] Visual processing JSON is no longer an always-visible second required editor.
- [x] Visual fields expose Output name, Path, Type and Omit-if-missing semantics.
- [x] Visual `resultSchema` is generated from COMMERCE-043 and shown only as derived/read-only contract information.
- [x] Direct and JavaScript modes use the clearer `Processed result schema` label and retain explicit schema authoring until Test-tab sample inference is designed.
- [x] Direct/Visual/JavaScript local authoring survives mode switches within the session.
- [x] Only the active mode enters the canonical local definition; inactive mode drafts and invalid raw form state are not durably persisted.
- [x] Errors are shown in Response; other tabs remain freely navigable.
- [x] No live provider I/O, database migration or Phase 2 gating is introduced.

## Validation

- [x] focused External HTTP Response-tab UI tests for Direct/Visual/JavaScript
- [x] focused new-Tool local-only JavaScript panel regression
- [x] focused Visual derived-contract UI/round-trip tests
- [x] focused invalid raw-state retention and Response validation diagnostics
- [x] focused mode-switch retention tests for new and persisted-DRAFT authoring where applicable
- [x] explicit proof that Response validation performs zero provider/credential I/O
- [x] existing External UI/common Tool-authoring regression packet required by repository scripts
- [x] targeted TypeScript diagnostics or repository typecheck with baseline reconciliation
- [x] targeted ESLint for changed files
- [x] `git diff --check`

## Stop Condition

After the Response tab presents coherent Direct/Visual/JavaScript authoring, local diagnostics, derived Visual result contract, JavaScript editor wiring and per-mode draft preservation with all required validation complete, set the task to `review`, complete the Completion Report and STOP. Do not begin Test-tab, Agent-contract, Review-tab or Phase 2 gating work.

## Implementation Notes

The current code exposes `execution.resultPath` twice and disables the first control for Direct while exposing the second. Treat this as one Source-path concept, not two stored properties.

For Visual mode, do not modify Shared merely to persist the UI's selected scalar type inside response-processing fields. The generated canonical `resultSchema` is the durable result type contract and is sufficient to reconstruct compatible Visual field types on edit.

Direct/JavaScript sample-based result-schema generation is intentionally deferred because it depends on the later Test-tab contract for observed processed output. Do not guess schema types from Source path or JavaScript source text.

## Completion Report

### Status
Implementation complete; submitted for Architect Review.

### Files Changed
`moda-interact-commerce/app/styles.css`
`moda-interact-commerce/src/studio/external-http/editor.tsx`
`moda-interact-commerce/src/studio/external-http/response-tab.tsx`
`moda-interact-commerce/src/studio/tools/new-tool-editor.tsx`
`moda-interact-commerce/src/studio/tools/tool-editor.tsx`
`moda-interact-commerce/tests/external-tools-ui.test.tsx`
`moda-interact-commerce/tests/tool-authoring-screen.test.tsx`

### Work Completed
- Consolidated Source path behavior for Direct/Visual and removed it from JavaScript mode; replaced duplicate schema/path language with mode-specific controls.
- Connected stable, resizable CodeMirror response panels to new local Tool authoring and persisted Draft authoring. Kept new Tool persistence behind final Create and preserved independent mode drafts.
- Made Visual processing controls primary, added projected result types, derived the deterministic result contract, and kept invalid Visual authoring state local until schema derivation succeeds.
- Added Response-only validation, field diagnostics, stale-result invalidation, and raw invalid-value retention; added regression coverage for incomplete Visual types and malformed filter values.
- Preserved free tab navigation and the no-provider-I/O boundary.

### Validation Results
- `npm run test:arch020-external-tools-ui`: passed, 26 tests.
- `npx vitest run tests/tool-authoring-screen.test.tsx`: passed, 12 tests.
- `npm run test:arch021-external-tool-authoring-validation`: passed, 47 tests. Packaged the repository QuickJS runtime first with `npm run code-runtime:package`.
- `npm run test:arch021-tool-authoring-common`: passed, 85 tests.
- `npm run test:arch020-code-editor`: passed, 14 tests.
- Targeted ESLint across all changed TS/TSX files: passed.
- Targeted editor diagnostics: no errors in changed TS/TSX/CSS files.
- `npx tsc --noEmit --pretty false`: repository-wide check remains blocked by pre-existing errors in unrelated API imports, generated Prisma client/types and tests; final output had no diagnostics in C045-modified files.
- `git diff --check`: passed.

### Deviations
No scope deviations. Response validation remains configuration-only; provider execution, schema inference from samples, database changes and Phase 2 gating were not added.

### Assumptions
The existing `productionCodePanel` feature flag remains the enablement boundary for persisted Draft editor composition. The new Tool flow composes its stable CodeMirror panel directly.

### Unresolved Issues
The repository-wide TypeScript check has unrelated existing baseline failures; targeted diagnostics and changed-file lint are clean.

### Architectural Concerns
None identified. Architect Review remains pending and was not edited.

## Architect Review

### Review Status
Changes Requested — Attempt 1 (2026-09-26)

### Review Notes
Reviewer: `moda_architect`. Reviewed implementation `9bfd342` and completion-report handoff `ce216523`.

Attempt 1 closes most of the intended Response-tab composition: Source path is de-duplicated, the new-Tool and persisted-DRAFT JavaScript editors use CodeMirror, Visual result types and derived contracts are exposed, invalid Direct/JavaScript schema JSON and malformed Visual `IN` values remain local, and COMMERCE-044 Response validation is wired without provider execution. Preserve those changes. Four bounded state/validation defects remain.

#### A1-R1 — Validate the exact active Response mode after a mode switch

File: `moda-interact-commerce/src/studio/external-http/response-tab.tsx` plus focused UI regression coverage.

`advancedTexts` is initialised for all three modes from the initially active `advancedText`. `resetMode()` then restores `advancedTexts[mode]`, while `validateResponse()` sends `advancedText` as `responseProcessing` for Direct and JavaScript. Consequently, a persisted Visual draft switched to Direct can submit the old Visual processing JSON to `validateExternalResponseAction`; switching Visual -> JavaScript and validating before editing the source can do the same. The UI and canonical `execution.responseProcessing` say one mode while the authoritative Response validator receives another.

Correction contract:

1. Build the Response-validation DTO from the exact currently active Response candidate. Direct validation must submit `{ kind: "DIRECT" }`; JavaScript validation must submit the current `{ kind: "JAVASCRIPT", runtimeVersion, source }`; Visual must submit the current Visual processing candidate.
2. Do not rely on an `advancedText` value seeded from another mode. If per-mode raw processing text remains, initialise/reconcile it from that mode's own draft deterministically.
3. Preserve raw invalid Direct/JavaScript `resultSchema`, media-type and Source-path text for validation exactly as required by R4/R5.
4. Add regressions that start from the persisted Visual fixture, switch to Direct and validate without another edit, then switch to JavaScript and validate without another source edit. Assert the Server Action receives the selected mode, not the previous Visual JSON.

#### A1-R2 — Every relevant Response edit must invalidate a previous success, including locally invalid Visual edits

File: `moda-interact-commerce/src/studio/external-http/response-tab.tsx` plus focused UI regression coverage.

The normal `update()` path invalidates Response validation, but locally invalid Visual edits can return before reaching `update()`. In particular, clearing a projected field Type causes `setVisual()` to report `Choose a result type...` and return without calling `invalidateResponseValidation()`. A previously successful `Response configuration is valid` status therefore remains visible while the current local Response state is invalid. Duplicate output-name rejection has the same shape. This violates R5's requirement that successful validation becomes stale immediately on every relevant Response edit.

Correction contract:

1. Invalidate Response validation at the beginning of every relevant authoring edit, before parsing/derivation can fail.
2. At minimum cover projected field Type/name/path, add/remove projected field, Visual shape/filter/sort/limit, Response format/media types, Source path, JavaScript source and explicit Direct/JavaScript result schema.
3. Do not erase the invalid raw value merely to obtain staleness.
4. Add a regression: obtain a successful Visual Response validation, clear one projected field Type, assert the local Type remains blank with its actionable error and the validation status immediately returns to `Not validated` (or equivalent stale state) without another Server Action call.

#### A1-R3 — Visual read-only disclosures must describe the current local Visual authoring state

File: `moda-interact-commerce/src/studio/external-http/response-tab.tsx` plus focused UI regression coverage.

`setVisual()` updates `visualDraft` / canonical execution but does not reconcile `advancedTexts` / `onAdvancedTextChange`, while `View Visual processing JSON` renders the `advancedText` prop. After editing projection/filter/sort/limit controls, that disclosure can therefore continue to show the initial processing JSON. Likewise, when a Visual Type is deliberately incomplete and the canonical `resultSchema` is correctly left unchanged, the tab still renders `execution.resultSchema` under `Derived result contract` as though it represented the current incomplete controls.

Correction contract:

1. Make `View Visual processing JSON` a read-only representation of the current Visual local draft, not an older canonical/text buffer.
2. When all Visual types are valid, the displayed derived result-contract JSON must correspond to the current controls and the canonical derived schema.
3. When the current Visual authoring state cannot derive a result contract (for example a blank Type), do not present the previous schema as the current derived contract; show the existing local error and mark/suppress the derived contract until derivation succeeds.
4. Add regressions proving a projection/filter change updates the read-only processing JSON and an incomplete Type cannot display a stale prior schema as the current derived contract.

#### A1-R4 — OBJECT and LIST Visual shapes must not destructively reuse one shape draft

File: `moda-interact-commerce/src/studio/external-http/response-tab.tsx` plus focused UI regression coverage.

Manual validation after the Attempt 1 handoff exposed a fourth state defect. The Shape selector currently converts the active Visual draft with:

```ts
setVisual(event.target.value === "LIST"
  ? { kind: "LIST", fields, filters: [], sort: null, limit: 20 }
  : { kind: "OBJECT", fields })
```

so switching OBJECT -> LIST reuses the OBJECT projection fields as the LIST row projection, and switching back reuses the mutated LIST fields as the OBJECT projection. These are different result shapes and the user has not asked to reinterpret one shape's authoring as the other. The switch is therefore destructive/ambiguous in the same way C045 already avoids for Direct/Visual/JavaScript mode drafts.

Correction contract:

1. Maintain independent browser-local Visual shape drafts for `OBJECT` and `LIST` during the editor session, including their projected fields and result-type authoring. LIST-only filters/sort/limit belong only to the LIST draft.
2. Switching OBJECT -> LIST must restore the previous LIST draft when one exists; otherwise initialise a deterministic bounded LIST default rather than copying the OBJECT projection implicitly.
3. Switching LIST -> OBJECT must restore the previous OBJECT draft when one exists; LIST-only state must not leak into OBJECT.
4. Only the currently selected Visual shape enters the canonical local `execution.responseProcessing` / derived `resultSchema`. The inactive shape draft remains browser-local convenience state and must not be persisted.
5. Any shape switch is a relevant Response edit and must invalidate prior Response-validation success immediately.
6. Add regressions proving: author OBJECT fields/types -> switch to LIST -> LIST starts/restores its own draft; edit LIST -> switch back -> original OBJECT fields/types are restored; switch again -> LIST edits are restored; validation and read-only derived/disclosure output always describe the selected shape only.

Do not expand this attempt into Test-tab execution, sample schema inference, Request-tab corrections, Agent/Review redesign, database work or Phase 2 gating.

### Reviewed Files
- `moda-interact-commerce/src/studio/external-http/response-tab.tsx`
- `moda-interact-commerce/src/studio/external-http/editor.tsx`
- `moda-interact-commerce/src/studio/tools/new-tool-editor.tsx`
- `moda-interact-commerce/src/studio/tools/tool-editor.tsx`
- `moda-interact-commerce/app/styles.css`
- `moda-interact-commerce/tests/external-tools-ui.test.tsx`
- `moda-interact-commerce/tests/tool-authoring-screen.test.tsx`
- COMMERCE-043/044 accepted contracts and this task's R1-R12 / Acceptance Criteria

### Validation Reviewed
Submitted evidence is retained as supporting evidence:

```text
External HTTP UI:                    26/26 passed
New Tool authoring:                  12/12 passed
External validation / Server Action: 47/47 passed
Common Tool authoring:               85/85 passed
CodeMirror:                          14/14 passed
Targeted ESLint:                     passed
Changed-file diagnostics:            clean
git diff --check:                    passed
```

The supplied review archive does not contain installed dependencies, so dependency-backed commands were not falsely rerun in the architect container. Source inspection plus developer manual validation found the four functional gaps above, which the submitted tests do not currently cover.

### Architecture Conformance
Changes Requested. The overall composition remains aligned with ARCH-021, but R5 is not yet satisfied for exact active-mode validation/stale-success invalidation, R6/R7 are not yet satisfied by the stale Visual read-only disclosures, and Visual OBJECT/LIST switching still destructively reinterprets one local shape draft as the other.

### Follow-up
Return to `ready` with Attempt 1 retained and claim cleared. The next executor claim becomes Attempt 2. Preserve the completed C045 work and correct only A1-R1 through A1-R4 before resubmitting for Architect Review.
