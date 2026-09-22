---
id: ARCH-020-COMMERCE-023
architecture_id: ARCH-020
title: Build external tool authoring and response-filter editor
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 155
executor: copilot
claimed_at: 2026-09-22T02:21:41Z
attempt: 2
depends_on:
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-017
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-22
---

# Build external tool authoring and response-filter editor

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Frontend only: src/studio/external-http/**, U06 external execution/response-processing steps and U14 synthetic fixture controls. Own mode selector and typed code-panel slot, not027 code editor. No U15/U16/sidebar, provider HTTP, credential or shared-factory edits.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Frontend only: src/studio/external-http/**, U06 external execution/response-processing steps and U14 synthetic fixture controls. Own mode selector and typed code-panel slot, not027 code editor. No U15/U16/sidebar, provider HTTP, credential or shared-factory edits.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [ ] Implement exact U06 connection/revision/GET/query/schema controls and Process response visual editor + Advanced configuration for the same section2.1 schema.
- [ ] Display supplied connection documentation in Studio; source/processed sample side by side, counts and field errors. Use injected processor port fixtures; never execute source in browser;027 supplies code panel. Do not infer a trusted schema from a sample.
- [ ] Implement U06->U16 return-context contract, saved revision U14 test/return, stale validation invalidation and source hash checks. No secret fields; no live call/decryption in Fixture or Model preview.
- [ ] Preserve existing publication/release flow and exact tool binding/version selection. Demonstrate owned XN02 sections through injected connection/processor/service ports.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-017

## Enables
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024


## Acceptance Criteria

- [ ] X06: full authoring of C21 sample and list-filter example, including field rename/filter/sort/limit, produces exact stored execution JSON.
- [ ] No lost edits on save/discard/return, duplicate Test/Publish guarded, modified response invalidates old validation; keyboard/narrow controls usable.
- [ ] U14 external tests show processed fixtures and existing reply template with zero network calls; no U15 backend dependency for component acceptance.

## Validation

Provide `test:arch020-external-tools-ui` in the owning repository and document its exact scope.
Run focused changed-boundary tests, then existing repository typecheck/build
and lint where defined. Inspect package scripts first; do not invent a claim that
an absent script passed. Use C21 controlled transports and isolated stores.
Follow current developer-owned live/container validation policy; clearly separate
actual agent results from required unrun developer checks. No arbitrary screenshot
quota or repeated full-suite runs without new changes/failures.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Not Started.

### Files Changed

None; task definition only.

### Work Completed

None.

### Validation Results

No implementation validation performed.

### Deviations

Definition authored on main under the user's existing instruction.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.

### Unresolved Issues

No implementation reported. Explicit dependencies gate execution.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Expected mirrored branch: task/ARCH-020-COMMERCE-023. Attempt0; no implementation worktree or
commit claimed. At submission record physical isolation, dependency versions,
recursive database submodule evidence where applicable, commits and pushes.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

Reviewed by `moda_architect` against the exact submitted source snapshot associated by
the developer with implementation commit `f4c7b8b`.

The submitted implementation establishes a useful first U06 visual editor: the Shared
C21 `EXTERNAL_HTTP` definition is rendered, visual LIST processing can be edited,
synthetic processing is injected with zero network calls, and the focused X06 suite
reports 4/4 while the existing StudioWorkspace regressions report 18/18.

Attempt 1 is **not accepted** because the implementation does not yet provide the
complete C21 COMMERCE-023 authoring flow or X06/XN02 evidence. The corrections below
are the complete Attempt 1 rework contract. Do not broaden the task beyond them.

#### A1-R1 — make External API an actual U06 authoring choice and keep fixtures out of production composition

**Source and focused-test changes required.**

The current host can render `ExternalHttpEditor` only when a draft already contains
`execution.kind === "EXTERNAL_HTTP"`. A newly created tool can only create the
Shopify `emptyDefinition()`, so the required flow:

```text
U09/Create tool -> U06 -> External API (read-only)
```

cannot be performed through the UI.

Also, `ExternalHttpEditor` currently defaults to:

```ts
port = createExternalHttpFixturePort()
```

and its default execution contains the synthetic ID
`connection_revision_fixture`. Component fixtures must never become the implicit
application authoring source.

Correct exactly:

1. Add a U06 **Retrieve information** choice before creating the first editable
   revision:

```text
Shopify Storefront
External API (read-only)
```

2. For a tool with no editable revision, **Create draft** must create the selected
   execution kind. Existing Shopify behavior remains unchanged.
3. External draft creation is enabled only when the injected external UI port exposes
   at least one authorized connection revision. The proposed definition must use the
   exact selected real/injected revision ID; never write
   `connection_revision_fixture` unless the test explicitly injected that fixture.
4. If no external connection is available, do not create an invalid/synthetic draft.
   Show **No external connections are available** plus the Manage connections action
   from A1-R2.
5. Remove the fixture-port default from `ExternalHttpEditor`. The component must
   receive an `ExternalHttpUiPort` explicitly. Extend `StudioWorkspace`/`ToolEditor`
   with an optional external-HTTP composition port; when absent, external authoring
   renders an unavailable state rather than constructing fixtures.
6. `createExternalHttpFixturePort()` remains test/component-fixture code and must be
   passed explicitly by focused tests. No fixture is installed by an authenticated
   route or production factory in this task.

Focused proof:

```text
new tool -> choose External API -> Create draft
  -> createToolDraft receives EXTERNAL_HTTP
  -> connectionRevisionId equals exact injected revision ID

no injected external port
  -> zero synthetic revision IDs
  -> external authoring unavailable

fixture port is used only when test explicitly supplies it
```

#### A1-R2 — implement exact connection/revision presentation and U06 -> U16 -> U06 return context

**Source and focused-test changes required.**

C21 requires selection by connection and exact immutable revision, plus scope/auth/
documentation visibility and a guarded Manage connections route.

The current editor exposes a flat revision selector showing only:

```text
<revision id> · <origin>
```

and has no Manage connections action or return context.

Use the Shared `ConnectionView` / `ConnectionRevisionView` DTOs rather than inventing
another connection shape. The U06 component port may stay read-only and fixture-backed
for this task, but it must expose enough data to select a connection then one exact
revision.

Required visible state for the selected revision:

```text
Connection display name/key
Revision number
Origin
Scope: PLATFORM | PER_SHOP
Auth mode: NONE | BEARER | API_KEY
API-key header name only when applicable
Inline documentation
```

Never render credential values or credential status.

Add a **Manage connections** action. The host owns the return destination:

```text
returnTo = /tools/<toolId>?revision=<exact toolRevisionId>
```

and the selected connection destination is U16:

```text
/connections/<connectionId>?returnTo=<URL-encoded returnTo>
```

If there is no selected connection, use U15 `/connections` with the same encoded
`returnTo`.

Navigation must go through the existing Studio navigation blocker. If the tool draft is
dirty, the user gets Stay / Discard; do not silently navigate. Returning to U06 must
address the same tool revision. COMMERCE-023 does not edit U15/U16 internals.

Focused proof:

```text
select connection A revision 2
  -> displays A / revision 2 / scope / auth / docs
  -> stored execution uses revision 2 ID

Manage connections
  -> exact encoded returnTo points to same tool revision
  -> dirty draft invokes navigation guard

return to tool revision
  -> external definition is still the saved exact revision
```

#### A1-R3 — complete C21 query + visual-processing authoring; no silent data loss

**Source and focused-test changes required.**

The current controls cannot author the complete Shared schema:

- query keys cannot be edited;
- literal query mappings cannot be created;
- editing an existing input mapping drops `omitIfMissing`;
- filter operator `IN` is not offered;
- filter values are always written back as strings, so number/boolean/null filters
  cannot be authored;
- output field names cannot be renamed;
- `omitIfMissing` cannot be authored for projected fields;
- switching Visual/JavaScript immediately replaces the previous processing;
- the Advanced JSON textarea becomes stale after visual edits and can overwrite them;
- visual controls remain editable while `pending || locked`;
- invalid path/query text is rejected by Shared parsing by snapping back to the old
  value instead of retaining the user's text and highlighting the affected row.

Implement the exact v1 authoring surface:

**Query row**

```text
Query key
Source: Agent input | Literal

Agent input:
  input name
  omit if missing checkbox

Literal:
  scalar type: string | number | boolean
  typed literal value

Remove
```

Preserve all untouched mapping fields. Never turn a literal into an input mapping or
drop `omitIfMissing` because another field changed.

**Visual projected-field row**

```text
Output name
Source path
Omit if missing
Remove
```

**LIST filter row**

```text
Source path
Operator:
  EQ NE GT GTE LT LTE CONTAINS STARTS_WITH IN
Scalar type:
  string number boolean null
Value
```

For `IN`, accept 1..20 same-type scalar values. Enforce the Shared maxima in the UI:
32 projections, 8 filters, LIST limit 1..20. Show **All filters are ANDed**.

Sort remains optional `{path,direction}`. Do not coerce numeric/boolean/null filter
values to strings.

All visual mutation controls must honor `pending || locked`.

**Mode switching**

TEXT response mode requires JAVASCRIPT. Visual rules are JSON-only. Show that rule
next to Response format / Process response.

Switching Visual <-> JavaScript when the current processing mode has unsaved edits
must open:

```text
Keep editing
Discard changes and switch
```

There is no silent conversion between visual rules and JavaScript. The persisted
definition contains only the selected Shared `ResponseProcessing` member.

**Advanced configuration**

The Advanced JSON textarea is another view of the same selected visual schema:

- every successful visual edit immediately updates the Advanced JSON text;
- valid Advanced JSON immediately updates the visual controls;
- invalid Advanced JSON remains visible with a bounded error and does not mutate the
  saved execution until corrected;
- changing shape/mode never resurrects stale Advanced JSON.

Do not create a second visual-processing syntax.

**Code-panel slot**

Replace the plain `"Code editor slot owned by COMMERCE-027"` text with an actual typed
slot, for example:

```ts
type ExternalCodePanelSlotProps = {
  processing: Extract<ResponseProcessing, {kind: 'JAVASCRIPT'}>;
  responseFormat: ExternalResponseFormat;
  resultSchema: ExternalHttpExecution['resultSchema'];
  disabled: boolean;
  onChange(processing: Extract<ResponseProcessing, {kind: 'JAVASCRIPT'}>): void;
};

renderCodePanel?: (props: ExternalCodePanelSlotProps) => React.ReactNode;
```

Equivalent typing is acceptable, but COMMERCE-024 must be able to install
COMMERCE-027 without COMMERCE-023 importing its implementation directly.

Focused proof must build the execution from UI controls rather than starting from a
pre-authored object and assert exact JSON for:

```text
query input + omitIfMissing
query string literal
query numeric literal
query boolean literal
renamed projection
omitIfMissing projection
boolean EQ filter
numeric GT filter
IN filter
DESC sort
limit
```

#### A1-R4 — implement Response shape validation, stale-result guards, field chips and review/publish flow

**Source and focused-test changes required.**

Attempt 1 only parses `resultSchema` as configuration. `Apply to sample` processes the
fixture but never validates the resulting object against `resultSchema`. There is no
separate **Validate sample**, schema keyword reference, stale async-result guard,
schema-derived Response chips, or external-definition review panel.

The current async sample path also has a race:

```text
Apply sample A
  -> processing promise pending
edit processing/schema/sample
  -> UI says stale
old promise resolves
  -> UI overwrites state with "Applied to sample"
```

Implement one generation/hash boundary for U06 sample validation.

Use Shared `canonicalJson` and browser Web Crypto SHA-256. Define the current
validation hash exactly as lowercase-hex SHA-256 of:

```ts
canonicalJson({
  execution,
  sampleId,
  sample,
})
```

`execution` already includes query, connection revision, response format,
responseProcessing and resultSchema.

Every change to:

```text
connection revision
path
query
response format/media types
resultPath
responseProcessing
resultSchema
selected sample
editable sample body/status/content type
```

increments the generation and clears current process/validation success.

The injected component port must separate processing from validation. Keep
`processSample(...)`; add an injected schema-validation operation such as:

```ts
validateSample(input: {
  values: Record<string, unknown>;
  resultSchema: ExternalHttpExecution['resultSchema'];
  contentHash: string;
}): Promise<
  | {kind:'ok'; contentHash:string}
  | {kind:'invalid'; contentHash:string; issues: readonly {path:string; message:string}[]}
  | {kind:'unavailable'; message:string}
>;
```

Equivalent naming is acceptable. COMMERCE-023 must **not** implement another
production result-schema engine; focused fixtures inject this port and COMMERCE-024
later adapts the accepted validator.

Apply async results only when both generation and returned/requested `contentHash`
still match.

**Response shape UI**

Keep editable raw JSON, and add the bounded inline keyword reference:

```text
object
properties
required
additionalProperties: false
string / maxLength
number
boolean
array / items / maxItems
```

Show that `resultPath=""` means the response root and that response templates read the
wrapper under `values`.

After processing, **Validate sample** validates the processed object. Schema/path
errors retain all input and show the exact issue path. Do not infer a trusted schema
from a sample.

**Schema-derived chips**

In the existing Response section render read-only schema-derived paths, for example:

```text
values.title
values.price
values.items[].name
```

depending on the authored `resultSchema`. They are guidance only and never mutate the
schema/template automatically.

**Review panel**

Before Publish show:

```text
agent descriptor: name + description + input schema (unchanged)
connection name + exact revision number
GET path
query mapping names only
literal values redacted as [literal]
result schema
selected processing kind
current sample-validation state
```

Never display credential values.

The external draft branch must retain the existing Save CAS workflow and add the same
role-aware Publish action as other tool drafts:

```text
ADMIN:
  Save/Test, no Publish

SUPER_ADMIN:
  Save/Test/Publish
```

Publish calls the existing `publishToolRevision` with the exact draft revision,
current `editVersion`, reason and the normal unknown-operation reconciliation path.
Do not bypass later COMMERCE-030 receipt enforcement; a backend rejection remains a
bounded failure and never displays success.

Focused proof:

```text
start sample validation for hash A
edit schema/sample before result
late A result => discarded

invalid schema result
  -> exact issue path visible
  -> source/sample/schema retained

successful validation
  -> current hash recorded
edit query
  -> validation becomes stale immediately

ADMIN
  -> no Publish

SUPER_ADMIN
  -> Publish exact revision/editVersion
  -> duplicate publish admitted once
```

#### A1-R5 — provide actual U14 external fixture controls with four bounded scenarios and zero live calls

**Source and focused-test changes required.**

Attempt 1 labels the U06 sample fieldset `U14 synthetic sample`, but it is still inside
the U06 editor. No U14-consumable external fixture control is exported and the fixture
catalogue has only one success sample.

Add:

```text
src/studio/external-http/fixture-controls.tsx
```

and export it from the external-http UI boundary.

The component is a typed U14 slot for later COMMERCE-024 composition. It must not edit
COMMERCE-017's preview implementation directly.

Required fixture catalogue:

```text
success
empty
missing-field
provider-failure
```

For JSON visual fixtures, use only synthetic `TransformSample` values. Provider
failure is represented by the injected fixture/test port result, not by making a
network call.

Required component inputs include the exact frozen `toolRevisionId`, exact saved
external definition, fixture catalogue/selection and an injected test/process port.
Required output shows:

```text
selected fixture
processed values or bounded failure
existing rendered reply/template result supplied by the injected port
```

No credential/decryption field exists in this component.

When the enclosing preview conversation is frozen:

```text
fixture selector disabled
sample editor disabled
message: Reset the conversation to change this fixture.
```

A reset signal from the host unlocks selection; COMMERCE-023 does not implement Redis
or the preview backend.

Focused proof:

```text
all four fixtures selectable
success -> processed values + rendered reply
empty -> valid empty processed result
missing-field -> bounded path failure
provider-failure -> bounded unavailable/provider-failure state

global fetch spy -> zero calls
no credential value rendered
frozen=true -> fixture cannot change
reset/unfrozen -> selection may change
```

#### A1-R6 — prove the owned XN02 segments and reconcile the durable task record

**Focused validation and task-record changes required.**

The current four tests start from an already-authored external definition, so they do
not prove X06's complete authoring flow. Add one focused integration-style component
test using only injected/in-memory ports:

```text
Create tool
-> choose External API
-> Create draft
-> select connection/revision
-> Manage connections destination contains exact return tool/revision
-> return to same U06 revision
-> author query + visual list filter/sort/limit
-> edit resultSchema
-> apply synthetic sample
-> validate sample
-> Save draft
-> hand saved exact revision to U14 fixture controls
-> return to same tool revision
-> SUPER_ADMIN Publish
```

Assertions:

```text
stored execution === exact expected C21 execution JSON
agent descriptor fields unchanged
sample-validation hash current before save/publish
zero fetch/network calls
zero credential values
duplicate Apply/Save/Publish admitted once each
```

Retain the existing StudioWorkspace regression suite.

After corrections run exactly:

```bash
npm run test:arch020-external-tools-ui
npx vitest run tests/studio-workspace.test.tsx
npx eslint \
  src/studio/external-http \
  components/studio-workspace.tsx \
  tests/external-tools-ui.test.tsx
npm run lint
npm run typecheck
npm run build
git diff --check
```

If repository-wide lint/typecheck/build remain blocked solely by an unchanged baseline
outside the task-owned files, record the exact diagnostics and prove there are no new
diagnostics in:

```text
src/studio/external-http/**
components/studio-workspace.tsx
tests/external-tools-ui.test.tsx
package.json
package-lock.json
```

Do not repair unrelated Connections, Prisma, execution or preview code inside
COMMERCE-023.

The submitted parent task record is also stale: this snapshot still says
`status: in_progress`, `executor: copilot` and Completion Report `Not Started`
despite the developer reporting implementation `f4c7b8b`. Attempt 2 must accurately
update Work Items, Acceptance Criteria, Validation and the Completion Report before
returning to review. Do not fabricate Git evidence that is not visible from the
actual worktrees.

### Reviewed Files

- `components/studio-workspace.tsx`
- `components/studio-composer-context.tsx`
- `src/studio/external-http/editor.tsx`
- `src/studio/external-http/ports.ts`
- `src/studio/external-http/processor.ts`
- `tests/external-tools-ui.test.tsx`
- `package.json`
- C21 sections 2, 2.1, 6 and 8
- this task file and current domain index

### Validation Reviewed

Submitted developer evidence:

```text
npm run test:arch020-external-tools-ui
  PASS — 4/4

StudioWorkspace regressions
  PASS — 18/18

changed-file diagnostics
  PASS

git diff --check
  PASS

npm run lint
  NON-ZERO — reported pre-existing Connections failure
```

The uploaded snapshot contains no `node_modules` or Git metadata, so dependency-backed
commands and remote branch heads were not falsely claimed as independently rerun from
the review container. The reported lint baseline is not the reason for this outcome;
the functional C21/X06 gaps above independently require correction.

### Architecture Conformance

Not yet conformant with C21 X06/XN02.

The visual-editor starting point and zero-network fixture principle are sound, but the
current UI cannot create an external draft through the normal tool flow, cannot perform
the U06/U16 return path, cannot fully author the Shared query/filter schema, silently
replaces dirty processing modes, lacks a real typed code-panel slot, does not validate
processed samples against `resultSchema`, lacks stale async-result protection and
schema/review guidance, does not expose the required U14 fixture component, and omits
the external draft Publish path.

No changes to connection backend/credentials, external HTTP execution, sandbox
runtime, publication receipt implementation, preview Redis/backend, MCP, database or
gateway are authorized by this correction.

### Follow-up

Return the same task to the normal execution path:

```yaml
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next:

```text
/moda-task ARCH-020-COMMERCE-023
```

must claim **Attempt 2 exactly once**.

The implementing agent must read this complete Architect Review before source
inspection, implement only A1-R1 through A1-R6, run the bounded validation above,
reconcile the Completion Report/checklists, set the task to review, clear the claim on
handoff, push both mirrored task branches and STOP.

Do not start COMMERCE-024 or COMMERCE-012. They remain dependency-gated.
