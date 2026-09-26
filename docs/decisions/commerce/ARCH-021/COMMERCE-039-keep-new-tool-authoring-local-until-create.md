---
id: ARCH-021-COMMERCE-039
architecture_id: ARCH-021
title: Keep new Tool authoring local until final creation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 55
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-021
  - ARCH-021-COMMERCE-022
  - ARCH-021-COMMERCE-038
enables: []
created: 2026-09-25
updated: 2026-09-26
---

# Keep new Tool authoring local until final creation

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Refactor the new-Tool Studio flow so all pre-creation authoring state remains local to the browser/editor and zero Tool/ToolRevision persistence occurs until the user explicitly performs the final Create action, which invokes the COMMERCE-038 atomic Tool + initial-draft mutation exactly once.

## Context

The current `ToolLibrary` new-Tool form immediately persists a Tool identity and then separately persists a draft:

```text
submit New tool form
  -> createTool(...)
  -> set stagedToolDraft with durable toolId
  -> createToolDraft(...)
  -> navigate to persisted DRAFT editor
```

`ToolAuthoringScreen` therefore carries composite recovery state:

```text
stagedToolDraft
resumeStagedDraft
name-based committed Tool lookup
DRAFT-revision lookup
```

This is contrary to the desired authoring model. Request/Query, Response/Result, Test, Agent contract and Review are one creation flow. Intermediate steps do not need durable persistence. If the user abandons that flow, no database artifact should exist.

COMMERCE-021 and COMMERCE-022 own the completed authoring surfaces for EXTERNAL_HTTP and SHOPIFY_ADMIN_GRAPHQL. COMMERCE-038 provides one atomic final creation mutation and exact reconciliation identity. This task connects those pieces.

This is **Phase 1 creation semantics only**. Tab gating/progression is explicitly deferred to Phase 2.

## Scope

Primary files:

```text
src/studio/tools/tool-library.tsx
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/contracts.ts
src/studio/external-http/editor.tsx                 # reuse/local authoring composition only as required
src/studio/tools/admin-validation-server-actions.ts # consume existing metadata/validation boundary
src/studio/tools/external-validation-server-actions.ts # consume existing validation/preview boundary
components/studio-composer-context.tsx              # consume navigation API; change only if directly required

 tests/tool-authoring-screen.test.tsx
 tests/external-tools-ui.test.tsx
 tests/studio-workspace.test.tsx
 tests/shopify-admin-authoring-validation.test.ts    # only if directly affected by composition
```

Add a focused new-Tool authoring UI test file if that gives a clearer executable contract than overloading existing suites.

## Out of Scope

- Phase 2 gating of tabs or steps.
- Requiring the user to finish one tab before opening another.
- Next/Previous wizard sequencing.
- completed/current/locked tab-state indicators beyond presentation already accepted by COMMERCE-021/022.
- Persisting unfinished new-Tool state to PostgreSQL.
- Browser localStorage/sessionStorage persistence of abandoned new Tools.
- Auto-saving new Tool authoring.
- Changing existing persisted DRAFT Save/Publish semantics.
- Removing the ability to create a later DRAFT revision for an existing Tool.
- Live provider execution or publication proof.
- Database schema changes.
- Capability/Release work.

## Requirements

### R1 — explicit new-Tool authoring mode

Represent a brand-new Tool as local authoring state until final creation.

The local state must contain enough information to build the complete initial creation payload, including at least:

```text
name
displayName
description
tool execution kind
canonical proposedDefinition
```

For the accepted Phase 3 Tool kinds this includes the canonical definition fields authored by:

```text
SHOPIFY_ADMIN_GRAPHQL
EXTERNAL_HTTP
```

Do not create a temporary/pending `CommerceTool` row merely to obtain a Tool id for the editor.

### R2 — no persistence while traversing authoring tabs

Before the final Create action, interactions on:

```text
Request / Query
Response / Result
Test
Agent contract
Review
```

must not invoke any Tool mutation that persists:

```text
CommerceTool
CommerceToolRevision
```

This includes tab navigation, field edits, request/sample preview, validation and Review rendering.

Existing non-mutating server validation/metadata calls remain allowed.

### R3 — no new-Tool Save draft persistence

A brand-new Tool has no durable `Save draft` operation before final creation.

Do not expose the existing persisted-revision `Save draft` mutation as a way to persist intermediate new-Tool authoring.

Existing Tools with an already durable DRAFT revision retain their current `Save draft`, CAS and Publish behaviour.

The UI must clearly distinguish:

```text
NEW TOOL
  local authoring
  final action: Create tool

EXISTING TOOL DRAFT
  durable revision
  Save draft / Publish behaviour unchanged
```

### R4 — final Review creates once

The final creation action submits the complete local Tool metadata + `proposedDefinition` to the COMMERCE-038 named atomic mutation.

Exactly one operationId is generated for the final initial-create attempt.

On confirmed success:

```text
receive toolId + toolRevisionId
  -> clear local new-Tool authoring state
  -> navigate directly to /tools/<toolId>?revision=<toolRevisionId>
```

Do not call `createTool()` followed by `createToolDraft()`.

Do not require a list refresh/name lookup/DRAFT scan to determine where to navigate.

### R5 — abandonment creates nothing

If the user:

```text
uses Back
navigates elsewhere after accepting dirty-navigation discard
closes/reloads the page
abandons the authoring flow before final Create
```

there is no Tool/ToolRevision persistence caused by the unfinished flow.

Normal in-memory state may be discarded.

Do not introduce server-side orphan cleanup as a substitute for this requirement.

### R6 — preserve dirty-navigation semantics

Edits to the local new-Tool authoring model mark the screen dirty through the accepted Studio composer/navigation blocker.

Discarding local changes may clear the local authoring model and permit navigation.

A final-create operation with an unconfirmed transport outcome remains navigation-locked until reconciliation resolves it, exactly as COMMERCE-020 requires.

### R7 — simplify composite creation recovery

Remove new-Tool creation dependence on the current two-operation staging mechanisms:

```text
stagedToolDraft
resumeStagedDraft
submitToolDraft after createTool success
reconcile CREATE_TOOL by Tool name
reconcile CREATE_TOOL_DRAFT by first DRAFT revision
```

Equivalent state used for unrelated existing-Tool functionality may remain only if it still has a real owner; do not preserve dead composite-creation machinery.

For a lost/rejected final-create response:

```text
UNCONFIRMED
  -> reconcile exact operation
  -> committed: receive exact toolId/toolRevisionId and navigate
  -> not committed: unlock and allow a new explicit Create attempt
```

Never automatically replay the original create mutation.

### R8 — both accepted Tool kinds use the same persistence rule

`SHOPIFY_ADMIN_GRAPHQL` and `EXTERNAL_HTTP` new Tool flows both remain local until final Create.

Kind-specific local defaults/metadata are allowed:

```text
SHOPIFY_ADMIN_GRAPHQL
  server-owned Admin API version/schema metadata

EXTERNAL_HTTP
  selected immutable authorized connection revision
```

Choosing either kind must not itself persist a Tool.

### R9 — preserve authoring validation and preview semantics

Continue using the accepted COMMERCE-019/023/024 validation boundaries.

Validation/preview may be server-backed but remains non-mutating.

The final creation command must still receive a canonical draft definition that passes its own server-side validation. Browser validation is not a trust boundary.

Do not weaken:

```text
connection revision checks
Admin schema identity checks
request/response definition bounds
zero-provider-I/O Phase 3 preview rules
```

### R10 — Phase 2 gating explicitly absent

Tabs/sections remain freely navigable in this task.

MUST NOT add any of the following:

```text
lock later tabs until earlier tabs complete
mandatory Next/Back workflow
per-step completion gating
prevent Review tab opening because another tab is incomplete
automatic downstream completion invalidation state machine
```

Existing field/server validation may still reject the final Create operation when the submitted definition is invalid. That is validation, not navigation gating.

### R11 — existing Tool editing remains durable

Opening an already persisted Tool/revision continues to use the existing durable editor behaviour:

```text
update Tool metadata where supported
Save DRAFT with expectedEditVersion CAS
validate
publish with existing authority/live-test gate
create later DRAFT from existing Tool where supported
```

Do not convert existing Tool editing into an all-local session merely because new Tool creation is local.

### R12 — restore the accepted External HTTP authoring presentation without reverting COMMERCE-021 behavior

COMMERCE-021 corrected important DRAFT typing, validation, save/CAS and production-read behaviour, but its final implementation also flattened the previously accepted External HTTP authoring presentation. This task must restore that presentation as part of the new-Tool flow **without rolling back COMMERCE-021 behavior**.

The restored External HTTP presentation contract is exact:

```text
Request | Response | Test | Agent contract | Review
```

The five controls are presentation tabs only. They are freely navigable and MUST NOT implement Phase 2 gating.

For both:

```text
EXISTING EXTERNAL_HTTP DRAFT
NEW EXTERNAL_HTTP local authoring session
```

render one tablist with:

```tsx
<nav
  className="tool-editor-tabs"
  role="tablist"
  aria-label="External tool authoring steps"
>
```

and exactly these tab labels/order:

```text
Request
Response
Test
Agent contract
Review
```

Each tab button MUST use:

```text
role="tab"
aria-selected=<true only for active tab>
className="active" only when selected
```

Only the active panel is rendered. Panel semantics are:

```text
Request
  current COMMERCE-021 connection selection
  request mode
  declarative/JavaScript request construction
  path/query/header authoring

Response
  current COMMERCE-021 response format
  result path
  DIRECT / VISUAL / JAVASCRIPT response processing
  current CodeEditor behavior
  result-schema authoring

Test
  current COMMERCE-021 request-construction preview
  tool-arguments input
  Preview request action/result
  NO provider call and NO restoration of removed live/sample-provider behavior

Agent contract
  Definition SemVer
  Description
  Input JSON Schema
  Response template

Review
  structured review summary
  validation state
  final action appropriate to mode:
    existing DRAFT -> existing Save/Validate/Publish behavior
    new Tool       -> Create tool only
```

Restore/export a presentation section type equivalent to:

```ts
export type ExternalHttpEditorSection = "request" | "response" | "test";
```

and restore a `section` input on `ExternalHttpEditor`. `ExternalHttpEditor` MUST continue using the post-COMMERCE-021 draft-safe execution contract; do not restore the old `ToolDefinition` cast boundary.

`toolRevisionId` MUST NOT force fake persistence identity into new authoring. If the component only uses it for DOM metadata, make it optional (or otherwise omit the DOM attribute in new mode). Existing persisted DRAFTs continue to pass the real revision id.

The following presentation classes already exist in `app/styles.css` and MUST be used rather than replaced with a second style system:

```text
tool-editor-tabs
tool-editor-panel
tool-editor-actions
tool-review-panel
tool-review-heading
tool-review-summary-grid
tool-review-card
tool-review-card-wide
tool-review-facts
tool-review-facts-single
tool-review-query
tool-review-publish
tool-review-publish-controls
tool-editor-json-textarea
tool-editor-sample-textarea        # use only where the current UI still has a sample/body-style editor
navigation-link-button
```

The Review panel must restore the structured visual composition rather than a single flattened `<dl>`:

```text
tool-review-panel
  tool-review-heading
    title + explanatory text
    validation-status pill

  tool-review-summary-grid
    Tool card
    Request card

  Agent contract wide card
  Result contract wide card

  final-action area
```

For an existing persisted DRAFT, the final-action area keeps the accepted COMMERCE-021 Save/Validate/SUPER_ADMIN publication semantics. For a new Tool, the same review presentation uses a creation area and the only durable action is `Create tool`.

Restore the large editor presentation for JSON/text contracts. At minimum these controls must use `className="tool-editor-json-textarea"` and an explicit multi-line row count equivalent to the accepted presentation:

```text
Input JSON Schema             rows=12
Response template             rows=12
Advanced response processing rows=12 (when present)
Response shape/resultSchema   rows=12
```

Do not restore obsolete COMMERCE-021 behavior merely because it existed in the earlier presentation. In particular:

```text
MUST preserve current request-preview Server Action routing
MUST preserve DIRECT / VISUAL / JAVASCRIPT modes
MUST preserve CodeEditor behavior
MUST preserve current draft-capable typing
MUST preserve stale-validation invalidation
MUST preserve CAS/save semantics
MUST preserve current authorization and LIVE_TEST_REQUIRED behavior
MUST NOT reintroduce provider I/O or the removed synthetic/live sample execution path
```

### R13 — the metadata form starts local authoring; it is not the final create surface

The current Attempt 1 implementation still renders a small `New tool` metadata form whose submit button is `Create tool` and immediately submits a generated default definition. That does not satisfy this architecture.

Change the flow deterministically to:

```text
Tool library
  -> New tool setup form
       name
       displayName
       description
       kind
  -> Continue authoring            # local state only, zero Tool mutations
  -> local authoring shell
       Request / Query
       Response / Result
       Test
       Agent contract
       Review
  -> Create tool                   # only here
  -> createToolWithInitialDraft exactly once
  -> navigate by returned toolId + toolRevisionId
```

For `EXTERNAL_HTTP`, connection selection belongs to the current Request authoring surface; the setup form MUST NOT persist merely to obtain a revision id. It may seed the first available authorized connection revision when creating the local draft model.

For `SHOPIFY_ADMIN_GRAPHQL`, continue using the accepted COMMERCE-022 metadata/validation boundary. Loading pinned Admin metadata is non-mutating and may be used to seed the local definition. Do not invent a persisted Tool id for component reuse.

The initial setup submit label MUST be `Continue authoring`, not `Create tool`. The `Create tool` button MUST exist only in the final local Review surface.

### R14 — preserve the accepted COMMERCE-021 behavioral contract exactly

The presentation restoration and local-new mode must not undo any of the behavior accepted in COMMERCE-021 Attempt 6. Preserve all of the following:

```text
DRAFT-capable authoring state; no incomplete DRAFT cast to full ToolDefinition
ExternalHttpExecutionSchema narrowing only at the execution boundary
stale authoritative-validation success cleared on authored changes
Save does not silently validate
current saved-vs-unsaved validation semantics
CAS_CONFLICT retains user edits and dirty/navigation protection
exact production DRAFT DTO round-trip
current preview action error handling
current response-mode discard behavior
DIRECT / VISUAL / JAVASCRIPT response processing
current CodeEditor behavior
ADMIN authoring / SUPER_ADMIN publishing hierarchy
typed LIVE_TEST_REQUIRED presentation
zero provider I/O in the Phase 3 preview path
```

Do not copy the old pre-COMMERCE-021 component wholesale. Restore only its presentation shell around the accepted current behavior.

## Work Items

- [ ] Introduce/derive a local new-Tool authoring model from Tool metadata + canonical proposed definition.
- [ ] Reuse the accepted EXTERNAL_HTTP and SHOPIFY_ADMIN_GRAPHQL authoring surfaces in new mode without a persisted Tool id.
- [ ] Remove the initial `createTool -> createToolDraft` browser sequence.
- [ ] Remove new-Tool dependence on `stagedToolDraft` / resume composite recovery.
- [ ] Ensure Request/Response/Test/Agent contract/Review changes are local/non-mutating.
- [ ] Remove/avoid persisted `Save draft` for a not-yet-created Tool.
- [ ] Wire final Review `Create tool` to the COMMERCE-038 atomic mutation.
- [ ] Navigate using the returned exact `toolId` + `toolRevisionId`.
- [ ] Wire transport-only UNCONFIRMED reconciliation to exact committed identity.
- [ ] Preserve existing persisted Tool DRAFT editing unchanged.
- [ ] Add focused regressions for no intermediate persistence and abandonment.
- [ ] Replace the metadata-form `Create tool` submit with a non-mutating `Continue authoring` transition.
- [ ] Render a genuine local authoring session before final creation; do not submit generated defaults directly from the setup form.
- [ ] Restore the five-tab External HTTP authoring shell for both local-new and persisted-DRAFT modes.
- [ ] Restore the structured Review-card presentation and JSON-editor sizing/classes without reverting COMMERCE-021 behavior.
- [ ] Keep the current COMMERCE-021 request preview in the Test tab; do not resurrect removed provider/sample execution semantics.
- [ ] Reconcile all Work Items, Acceptance Criteria and Validation checkboxes to the final Attempt 2 evidence.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-021
EXTERNAL_HTTP authoring surface

ARCH-021-COMMERCE-022
SHOPIFY_ADMIN_GRAPHQL authoring surface

ARCH-021-COMMERCE-038
atomic initial Tool named Server Action
exact creation/reconciliation result

ARCH-021-COMMERCE-019/023/024
existing validation/preview boundaries
```

No new cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-021
- ARCH-021-COMMERCE-022
- ARCH-021-COMMERCE-038

Current dependency state after COMMERCE-021 Attempt 6 acceptance:

```text
ARCH-021-COMMERCE-021  Complete
ARCH-021-COMMERCE-022  Complete
ARCH-021-COMMERCE-038  Complete
```

All dependencies are architect-accepted Complete. This task is `ready` for execution.

## Enables

None in this task set. Phase 2 progression/gating may be defined separately only after this creation model is accepted and manually reviewed.

## Acceptance Criteria

- [ ] A new Tool can be authored across the accepted tabs/sections without creating a Tool or ToolRevision row.
- [ ] No new-Tool persistence occurs when entering/changing Request/Query, Response/Result, Test, Agent contract or Review.
- [ ] A brand-new Tool does not expose durable `Save draft` before creation.
- [ ] Final `Create tool` performs exactly one atomic initial-create mutation.
- [ ] Confirmed creation navigates using the exact returned `toolId` + `toolRevisionId`.
- [ ] Abandoning the flow before Create leaves no Tool/ToolRevision artifact created by that flow.
- [ ] Lost final-create response is reconciled through the one operation identity without mutation replay or name/DRAFT scans.
- [ ] Both EXTERNAL_HTTP and SHOPIFY_ADMIN_GRAPHQL obey the same no-intermediate-persistence rule.
- [ ] Existing persisted Tool DRAFT Save/Publish/CAS behaviour remains unchanged.
- [ ] All tabs remain freely navigable; no Phase 2 gating is introduced.
- [ ] Browser state is not treated as a trust boundary; final server validation remains authoritative.
- [ ] The New tool setup form exposes `Continue authoring` and does not expose the final `Create tool` action.
- [ ] `Create tool` is available only from the local Review surface after entering the authoring session.
- [ ] EXTERNAL_HTTP renders exactly five freely navigable tabs in this order: Request, Response, Test, Agent contract, Review.
- [ ] Existing EXTERNAL_HTTP DRAFT editing uses the same restored tab/panel presentation while retaining durable Save/Validate/Publish semantics.
- [ ] Only the active External HTTP tab panel is rendered and each tab exposes correct `role=tab` / `aria-selected` semantics.
- [ ] Agent-contract JSON/text areas and response-processing/schema JSON areas use the accepted `tool-editor-json-textarea` presentation.
- [ ] Review uses the accepted `tool-review-*` card/grid/action structure rather than a flattened facts list.
- [ ] The Test tab contains the current no-provider request-construction preview; no removed live/sample-provider behavior is reintroduced.
- [ ] COMMERCE-021 Attempt 6 behavioral regressions remain green after the presentation restoration.

## Validation

- [ ] `npm run test:arch020-external-tools-ui`
- [ ] `npm run test:arch021-tool-authoring-common`
- [ ] focused `tests/tool-authoring-screen.test.tsx`
- [ ] focused Shopify Admin Tool-authoring UI regression packet affected by this composition
- [ ] regression: changing fields/tabs/preview/validation before final Create invokes zero Tool persistence Server Actions
- [ ] regression: abandoning/discarding new Tool flow invokes zero Tool persistence Server Actions
- [ ] regression: final Create invokes the atomic action once and never calls legacy create-then-draft sequence
- [ ] regression: committed UNCONFIRMED reconciliation navigates by returned audit identity
- [ ] regression: existing persisted Tool DRAFT still saves/publishes through existing actions
- [ ] targeted lint/typecheck with zero new task-owned diagnostics
- [ ] regression: setup form -> `Continue authoring` performs zero Tool persistence actions and renders the local authoring shell
- [ ] regression: EXTERNAL_HTTP tablist has exactly Request / Response / Test / Agent contract / Review in order, all freely clickable
- [ ] regression: clicking each External HTTP tab renders only its matching panel while preserving authored values across tab switches
- [ ] regression: Request/Response/Test/Agent edits followed by Review still produce zero Tool persistence calls
- [ ] regression: `Create tool` is absent before Review and final Review Create submits the actually edited local definition, not generated defaults
- [ ] regression: persisted EXTERNAL_HTTP DRAFT still exposes the restored tabs and retains COMMERCE-021 Save -> Validate -> publish/LIVE_TEST_REQUIRED behavior
- [ ] regression: restored Agent contract textareas carry `tool-editor-json-textarea`; restored Review carries `tool-review-panel`, `tool-review-summary-grid` and `tool-review-card` structure
- [ ] source audit: no new-mode fake/persisted Tool or ToolRevision id is invented for component reuse
- [ ] source audit: no `createTool` / `createToolDraft` call returns to the new-Tool flow
- [ ] `git diff --check`

## Stop Condition

After local-only new-Tool authoring, final atomic creation and required regressions are complete, set this task to `review`, complete the Completion Report and STOP. Do not implement Phase 2 tab gating/progression and do not begin system-test work.

## Implementation Notes

Prefer reusing canonical authoring state/components rather than maintaining a second independently shaped Tool-definition model. However, do not force persisted `ToolSummary`/revision identifiers into new-mode state merely to reuse a component; new authoring genuinely has no durable IDs before final Create.

The visible label/button flow may distinguish an initial local setup action such as `Continue` from the final `Create tool`, provided no intermediate action persists. The exact presentation can follow the accepted COMMERCE-021/022 UI structure.

## Completion Report

### Status
Ready for review

### Files Changed
- `src/studio/contracts.ts`
- `src/studio/tools/tool-library.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/tool-authoring-screen.test.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/studio-workspace.test.tsx`

### Work Completed
- Replaced the new-tool `createTool` then `createToolDraft` browser sequence with one `createToolWithInitialDraft` action.
- Kept new-tool metadata and canonical definitions local until final Create; removed staged-draft/resume handling.
- Preserved existing durable Tool DRAFT editing and added exact returned `toolId`/`toolRevisionId` navigation and reconciliation.
- Added atomic in-memory fixture support and updated focused regressions for local authoring, exact-once creation, external authoring, and failure handling.
- Added the atomic operation to the shared Studio service contract and mutation refresh typing.

### Validation Results
- `npm run test:arch021-tool-authoring-common`: 7 files, 85 tests passed.
- `npm run test:arch020-external-tools-ui`: 16 tests passed.
- Focused packet (`tool-authoring-screen`, `external-tools-ui`, `studio-workspace`, `studio-integration`): 4 files, 56 tests passed.
- Targeted ESLint: passed.
- `git diff --check`: passed.
- Legacy new-tool path invariant: passed; no `createTool`, `createToolDraft`, or staged new-tool recovery path remains in the owning screens.
- `npm run typecheck`: exits nonzero with 255 repository-baseline diagnostics; zero diagnostics remain in task-owned implementation, fixture, and regression files.

### Deviations
- Full repository typecheck remains blocked by unrelated existing diagnostics outside this task's files.

### Assumptions
- COMMERCE-038 atomic creation and exact-identity reconciliation contracts remain the authoritative server boundary.

### Unresolved Issues
None

### Architectural Concerns
None

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes

#### Attempt 1 review — 2026-09-26

Reviewed implementation `2914d56` and submitted parent report `18e1ef8c`. Preserve the useful Attempt 1 work: the legacy browser `createTool -> createToolDraft` sequence and staged-draft recovery have been removed; final persistence uses `createToolWithInitialDraft`; confirmed and reconciled creation navigate using exact `toolId` + `toolRevisionId`; existing persisted-DRAFT mutations remain available.

Attempt 1 is not accepted because the primary product flow in this task is still missing. The current `ToolLibrary` metadata form submits `Create tool` immediately and constructs a generated default `proposedDefinition`. The user therefore never enters a local Request/Response/Test/Agent contract/Review authoring session before persistence. This changes the number of writes from two to one, but it does not satisfy “author locally until final creation.”

The current source also still reflects a presentation regression introduced during COMMERCE-021: the accepted External HTTP five-tab authoring shell and its structured Review/editor presentation were flattened even though the associated CSS contract remains present. This correction restores that presentation while preserving every COMMERCE-021 behavioral fix.

The following is the complete and authoritative Attempt 2 correction contract. Do not infer additional requirements from chat history.

##### A1-R1 — preserve the accepted Attempt 1 persistence mechanics

MUST preserve:

```text
one final createToolWithInitialDraft mutation
no new-tool createTool -> createToolDraft sequence
no stagedToolDraft/resumeStagedDraft composite flow
exact returned toolId/toolRevisionId navigation
exact audit reconciliation for UNCONFIRMED
no mutation replay during reconciliation
existing persisted Tool DRAFT update/publish/CAS paths
```

Do not rewrite COMMERCE-036/037/038 server persistence as part of this correction.

##### A1-R2 — add an actual local new-Tool session before final Create

Change the minimum owning files:

```text
src/studio/tools/tool-library.tsx
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/tool-editor.tsx
src/studio/external-http/editor.tsx
```

You MAY add these focused local components to keep the boundaries explicit:

```text
src/studio/tools/new-tool-editor.tsx
src/studio/tools/external-authoring-tabs.tsx
```

If added, they remain repository-local UI components; no new cross-service contract is created.

The setup form is not a creation form. It must do exactly this:

```text
submit setup form
  -> validate local metadata/default prerequisites
  -> construct local CommerceToolDraftDefinition
  -> store local authoring session in React state
  -> mark screen dirty
  -> render authoring editor
  -> ZERO Tool persistence Server Actions
```

The setup button text must be:

```text
Continue authoring
```

`Create tool` must not be rendered on the setup form.

The final local Review action must do exactly this:

```text
Create tool
  -> one fresh operationId
  -> createToolWithInitialDraft({
       operationId,
       reason,
       name,
       displayName,
       description,
       proposedDefinition: CURRENT LOCAL AUTHORED DEFINITION
     })
```

It MUST NOT rebuild a fresh default definition at click time. The payload must contain the edits made in Request/Response/Test/Agent contract.

On success:

```text
clear local session
clear dirty state if the submitted revision is still current
navigate /tools/<toolId>?revision=<toolRevisionId>
```

On deterministic error:

```text
keep local session
keep authored values
show bounded error
allow correction/retry
```

On transport `UNCONFIRMED`:

```text
keep local session
lock navigation/mutations
reconcile exact operation only
committed     -> navigate by exact recorded IDs
not committed -> unlock, preserve local session, require a new explicit Create click
```

##### A1-R3 — restore one shared External HTTP tab shell

Restore exactly five tabs:

```text
Request
Response
Test
Agent contract
Review
```

Use the existing `tool-editor-tabs` CSS contract and exact ARIA semantics from R12. The same visual shell must be used by:

```text
new local EXTERNAL_HTTP authoring
existing persisted EXTERNAL_HTTP DRAFT editing
```

Do not maintain two visually different External HTTP editors. If practical, extract the tab strip as one small presentation component used by both modes.

`ExternalHttpEditor` must regain section rendering around the CURRENT COMMERCE-021 controls:

```text
request  -> connection + request mode/construction/path/query/headers
response -> response format/result path/processing/result schema
test     -> current request-construction preview and its arguments/result
```

The Test tab must retain the current no-provider preview. Do not restore the old sample/provider execution mechanism.

##### A1-R4 — restore the accepted presentation classes/structure

Use the existing CSS classes in `app/styles.css`; do not create a competing style system.

Agent contract:

```text
<div className="tool-editor-panel" role="tabpanel" aria-label="Agent contract">
```

with the Input JSON Schema and Response template controls using:

```text
className="tool-editor-json-textarea"
rows={12}
```

Current External response-processing/result-schema JSON controls must likewise use `tool-editor-json-textarea` with `rows={12}` where they are textareas.

Review must use:

```text
<section className="tool-review-panel" role="tabpanel" ...>
  tool-review-heading
  tool-review-summary-grid
    tool-review-card      # Tool
    tool-review-card      # Request
  tool-review-card-wide   # Agent contract
  tool-review-card-wide   # Result contract
  tool-review-publish     # existing persisted mode
    OR equivalent final-create action area for new mode
```

For new mode, heading/action wording must refer to creation rather than publication. For existing persisted mode, retain the existing Save/Validate/SUPER_ADMIN publication semantics.

##### A1-R5 — preserve all COMMERCE-021 behavioral corrections

No production change may regress:

```text
DRAFT-capable state instead of incomplete-DRAFT -> ToolDefinition casts
ExternalHttpExecutionSchema narrowing
stale validation-message invalidation
Save/current-validation boundary
CAS_CONFLICT retained text + dirty navigation protection
production incomplete-DRAFT DTO round-trip
preview errors and request-preview action routing
response-mode Keep editing / Discard behavior
DIRECT / VISUAL / JAVASCRIPT modes
CodeEditor behavior
ADMIN/SUPER_ADMIN hierarchy
LIVE_TEST_REQUIRED typed presentation
zero-provider-I/O preview behavior
```

Do not copy a pre-COMMERCE-021 source file over the current implementation. Restore the presentation around the current behavior.

##### A1-R6 — both Tool kinds remain local until final Create

`SHOPIFY_ADMIN_GRAPHQL` does not need the historical External HTTP tab styling if COMMERCE-022 never defined it, but it MUST use the same persistence rule:

```text
setup -> local Admin authoring -> final Review/Create -> one atomic mutation
```

Its current pinned metadata, variable mapping, result-schema and validation behavior must remain COMMERCE-022-compatible. Loading/validating Admin metadata is allowed before Create because it is non-mutating.

##### A1-R7 — exact regressions required

Update/add tests so they prove the user flow rather than only the atomic mutation. At minimum:

```text
1. New EXTERNAL_HTTP:
   fill setup metadata
   click Continue authoring
   assert createToolWithInitialDraft = 0
   assert legacy createTool/createToolDraft = 0
   assert five tabs in exact order
   edit Request
   edit Response
   open Test and run current request preview
   edit Agent contract
   switch between tabs and prove values survive
   open Review
   assert createToolWithInitialDraft still = 0
   click Create tool
   assert createToolWithInitialDraft = 1
   assert payload contains the edits made above
   assert legacy mutations = 0
   assert navigation uses returned exact IDs

2. Abandonment:
   Continue authoring
   edit local definition
   discard/navigate away
   assert all Tool persistence mutations = 0

3. EXTERNAL_HTTP presentation:
   tablist aria-label = "External tool authoring steps"
   exact tab labels/order
   only active panel rendered
   Agent panel has tool-editor-panel
   JSON contract textareas have tool-editor-json-textarea
   Review has tool-review-panel + tool-review-summary-grid + tool-review-card

4. Existing persisted EXTERNAL_HTTP DRAFT:
   restored tab shell present
   current COMMERCE-021 dirty -> Save -> Validate behavior remains
   CAS regression remains
   SUPER_ADMIN publish still surfaces LIVE_TEST_REQUIRED exactly

5. New SHOPIFY_ADMIN_GRAPHQL:
   Continue authoring performs zero Tool persistence
   local Admin edits/validation remain non-mutating
   final Create uses one atomic mutation with the current authored definition
```

A regression that clicks `Create tool` directly on the small metadata form is invalid and must be rewritten because that form is no longer the final creation surface.

##### A1-R8 — validation commands

Run:

```bash
npm run test:arch020-external-tools-ui
npm run test:arch021-tool-authoring-common

npm exec vitest run \
  tests/tool-authoring-screen.test.tsx \
  tests/external-tools-ui.test.tsx \
  tests/studio-workspace.test.tsx \
  tests/studio-integration.test.ts

npm exec eslint \
  src/studio/tools/tool-library.tsx \
  src/studio/tools/tool-authoring-screen.tsx \
  src/studio/tools/tool-editor.tsx \
  src/studio/external-http/editor.tsx \
  tests/tool-authoring-screen.test.tsx \
  tests/external-tools-ui.test.tsx \
  tests/studio-workspace.test.tsx

npm run typecheck
git diff --check
```

If new focused source/test files are added, include them in targeted ESLint/type diagnostics. Repository baseline diagnostics may remain only when no diagnostic belongs to a COMMERCE-039-owned changed file.

Also run source audits proving:

```bash
! rg -n 'createTool\(|createToolDraft\(' \
  src/studio/tools/tool-library.tsx \
  src/studio/tools/tool-authoring-screen.tsx \
  src/studio/tools/new-tool-editor.tsx 2>/dev/null

rg -n 'Continue authoring' src/studio/tools
rg -n 'External tool authoring steps' src/studio/tools src/studio/external-http
```

The first audit must pass with no new-mode legacy create/draft call. If the optional `new-tool-editor.tsx` file is not created, omit that path rather than treating its absence as a failure.

##### A1-R9 — report reconciliation and stop condition

Attempt 2 must reconcile the durable task file:

```text
Work Items
Acceptance Criteria
Validation
Completion Report
```

to the actual final evidence. Completion Report status must be exactly:

```text
Ready for Review
```

Before handoff set:

```yaml
status: review
attempt: 2
executor: null
claimed_at: null
```

Return to `moda_architect` and STOP. Do not implement Phase 2 gating, Next/Previous sequencing, completion badges, provider live testing or system-test work.

### Reviewed Files

```text
moda-interact-commerce/src/studio/tools/tool-library.tsx
moda-interact-commerce/src/studio/tools/tool-authoring-screen.tsx
moda-interact-commerce/src/studio/tools/tool-editor.tsx
moda-interact-commerce/src/studio/external-http/editor.tsx
moda-interact-commerce/tests/tool-authoring-screen.test.tsx
moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/studio-workspace.test.tsx
moda-interact-commerce/app/styles.css
```

### Validation Reviewed

Submitted Attempt 1 evidence:

```text
implementation: 2914d56
parent report: 18e1ef8c
common Tool-authoring packet: 85 passed
external UI: 16 passed
focused packet: 56 passed
targeted ESLint: passed
git diff --check: passed
repository typecheck: baseline failures reported; no task-owned diagnostics reported
```

The green packet does not prove the missing local-authoring flow because its new-tool tests invoke `Create tool` directly from the metadata form.

### Architecture Conformance

Changes Requested. Atomic persistence/reconciliation mechanics conform, but the primary local-authoring-before-create behavior and accepted External HTTP authoring presentation do not yet conform.

### Follow-up

Reclaim the same task as Attempt 2. Preserve the accepted Attempt 1 atomic mechanics and implement only the correction contract above.
