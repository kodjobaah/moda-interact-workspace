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
status: review
priority: 55
executor: null
claimed_at: null
attempt: 2
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

## Work Items

- [x] Introduce/derive a local new-Tool authoring model from Tool metadata + canonical proposed definition.
- [x] Reuse the accepted EXTERNAL_HTTP and SHOPIFY_ADMIN_GRAPHQL authoring surfaces in new mode without a persisted Tool id.
- [x] Remove the initial `createTool -> createToolDraft` browser sequence.
- [x] Remove new-Tool dependence on `stagedToolDraft` / resume composite recovery.
- [x] Ensure Request/Response/Test/Agent contract/Review changes are local/non-mutating.
- [x] Remove/avoid persisted `Save draft` for a not-yet-created Tool.
- [x] Wire final Review `Create tool` to the COMMERCE-038 atomic mutation.
- [x] Navigate using the returned exact `toolId` + `toolRevisionId`.
- [x] Wire transport-only UNCONFIRMED reconciliation to exact committed identity.
- [x] Preserve existing persisted Tool DRAFT editing unchanged.
- [x] Add focused regressions for no intermediate persistence and abandonment.

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

- [x] A new Tool can be authored across the accepted tabs/sections without creating a Tool or ToolRevision row.
- [x] No new-Tool persistence occurs when entering/changing Request/Query, Response/Result, Test, Agent contract or Review.
- [x] A brand-new Tool does not expose durable `Save draft` before creation.
- [x] Final `Create tool` performs exactly one atomic initial-create mutation.
- [x] Confirmed creation navigates using the exact returned `toolId` + `toolRevisionId`.
- [x] Abandoning the flow before Create leaves no Tool/ToolRevision artifact created by that flow.
- [x] Lost final-create response is reconciled through the one operation identity without mutation replay or name/DRAFT scans.
- [x] Both EXTERNAL_HTTP and SHOPIFY_ADMIN_GRAPHQL obey the same no-intermediate-persistence rule.
- [x] Existing persisted Tool DRAFT Save/Publish/CAS behaviour remains unchanged.
- [x] All tabs remain freely navigable; no Phase 2 gating is introduced.
- [x] Browser state is not treated as a trust boundary; final server validation remains authoritative.

## Validation

- [x] `npm run test:arch020-external-tools-ui` (16 passed)
- [x] `npm run test:arch021-tool-authoring-common` (85 passed)
- [x] focused `tests/tool-authoring-screen.test.tsx` (6 passed)
- [x] focused Shopify Admin Tool-authoring UI regression packet affected by this composition (15 passed)
- [x] regression: changing fields/tabs/preview/validation before final Create invokes zero Tool persistence Server Actions
- [x] regression: abandoning/discarding new Tool flow invokes zero Tool persistence Server Actions
- [x] regression: final Create invokes the atomic action once and never calls legacy create-then-draft sequence
- [x] regression: committed UNCONFIRMED reconciliation navigates by returned audit identity
- [x] regression: existing persisted Tool DRAFT still saves/publishes through existing actions
- [x] targeted lint/typecheck with zero new task-owned diagnostics
- [x] `git diff --check`

## Stop Condition

After local-only new-Tool authoring, final atomic creation and required regressions are complete, set this task to `review`, complete the Completion Report and STOP. Do not implement Phase 2 tab gating/progression and do not begin system-test work.

## Implementation Notes

Prefer reusing canonical authoring state/components rather than maintaining a second independently shaped Tool-definition model. However, do not force persisted `ToolSummary`/revision identifiers into new-mode state merely to reuse a component; new authoring genuinely has no durable IDs before final Create.

The visible label/button flow may distinguish an initial local setup action such as `Continue` from the final `Create tool`, provided no intermediate action persists. The exact presentation can follow the accepted COMMERCE-021/022 UI structure.

## Completion Report

### Status
Ready for architect review

### Files Changed
`moda-interact-commerce/src/studio/external-http/editor.tsx`
`moda-interact-commerce/src/studio/server-services.ts`
`moda-interact-commerce/src/studio/tools/new-tool-editor.tsx`
`moda-interact-commerce/src/studio/tools/tool-authoring-screen.tsx`
`moda-interact-commerce/src/studio/tools/tool-library.tsx`
`moda-interact-commerce/tests/external-tools-ui.test.tsx`
`moda-interact-commerce/tests/shopify-admin-tools-ui.test.tsx`
`moda-interact-commerce/tests/studio-workspace.test.tsx`
`moda-interact-commerce/tests/tool-authoring-screen.test.tsx`

### Work Completed
Implemented a local new-Tool authoring session with the accepted five-tab Request, Response, Test, Agent contract and Review presentation. Setup now only loads local metadata and enters authoring; edits, tab changes, preview and validation do not call Tool persistence mutations. Final Review Create submits the canonical metadata and proposed definition through the COMMERCE-038 atomic action exactly once, navigates with the returned Tool and ToolRevision IDs, and retains exact-identity reconciliation without mutation replay. Existing persisted Tool DRAFT editing remains on its durable Save/Validate/CAS/Publish path.

### Validation Results
`npm run test:arch020-external-tools-ui`: 16 passed.
`npm run test:arch021-tool-authoring-common`: 85 passed.
Focused local and adjacent UI packet: 58 passed across 4 files.
Focused Admin/local packet: 21 passed across 2 files.
Focused ESLint: clean.
Task-owned typecheck diagnostics: clean; the full project typecheck still reports unrelated pre-existing diagnostics outside this task.
`git diff --check`: clean.

### Deviations
No Phase 2 tab gating or system-test work was added. Existing compatibility props for staged draft state remain in the library/editor boundaries where adjacent callers still provide them, but the new local flow no longer uses them for persistence or recovery.

### Assumptions
The existing COMMERCE-038 action and exact-operation reconciliation contract are authoritative for final creation. Server-side definition validation remains the trust boundary; browser validation only informs the local authoring experience.

### Unresolved Issues
The full repository typecheck has unrelated baseline diagnostics in generated/Prisma and other test surfaces; no diagnostics remain in the task-owned implementation or affected tests.

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
