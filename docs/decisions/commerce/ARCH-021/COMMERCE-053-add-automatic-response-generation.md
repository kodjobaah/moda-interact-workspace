---
id: ARCH-021-COMMERCE-053
architecture_id: ARCH-021
title: Add Automatic Visual response generation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 68
executor: copilot
claimed_at: 2026-09-27T10:35:40Z
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-042
  - ARCH-021-COMMERCE-050
  - ARCH-021-COMMERCE-051
  - ARCH-021-COMMERCE-052
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Add Automatic Visual response generation

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add one **authoring-only `Automatic` choice** to the External HTTP Response tab that calls the current live provider using shared sample Tool arguments, infers one of the accepted COMMERCE-048/049 Visual authoring trees, and then installs that proposal into the existing **Visual rules** editor for normal manual editing/validation.

`Automatic` is a transient Studio workflow, not a fourth persisted/runtime response-processing kind.

## Context

The accepted persisted response-processing union remains exactly:

```text
DIRECT
VISUAL
JAVASCRIPT
```

COMMERCE-048/049 own the Visual grammar:

```text
SCALAR       -> Scalar
OBJECT       -> Object
LIST         -> List of objects
SCALAR_LIST  -> List of values
```

COMMERCE-050 owns actionable Response validation presentation.

COMMERCE-051 supplies a bounded credential-redacted live provider observation.

COMMERCE-052 supplies deterministic observed-JSON -> `VisualAuthoringRoot` candidates.

The product decision for this task is:

```text
Automatic helps create Visual rules.
Visual remains the editor.
Test remains execution/observation only.
```

There must not be a second editable response-mapping surface inside Automatic or Test.

## Scope

Primary files are expected to include:

```text
moda-interact-commerce/src/studio/external-http/editor.tsx
moda-interact-commerce/src/studio/external-http/request-tab.tsx
moda-interact-commerce/src/studio/external-http/response-tab.tsx
moda-interact-commerce/src/studio/external-http/ports.ts                  # only UI callback/types required
moda-interact-commerce/src/studio/tools/new-tool-editor.tsx
moda-interact-commerce/src/studio/tools/tool-editor.tsx
moda-interact-commerce/src/studio/tools/tool-authoring-screen.tsx         # selected-shop plumbing for New Tool if required
moda-interact-commerce/src/studio/tools/external-validation-server-actions.ts
moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/tool-authoring-screen.test.tsx
```

The exact server action may remain the COMMERCE-051 observation action; do not create another network implementation for Automatic.

## Out of Scope

- Adding persisted/runtime `kind:"AUTOMATIC"`.
- Editing response mappings inside Test.
- A second Automatic-specific field/tree editor.
- Changing Visual node terminology/semantics.
- Synthetic fixture/sample testing UI.
- Satisfying `LIVE_TEST_REQUIRED`.
- Persisting provider responses or inference samples.
- Database/Shared changes.
- Automatic generation of Direct/JavaScript result schemas in this task.
- Prompt/model/agent execution.
- Tab gating.

## Requirements

### R1 — authoring mode presentation only

The Response mode selector may present:

```text
Visual rules
Direct
JavaScript
Automatic
```

but the canonical definition remains:

```text
DIRECT | VISUAL | JAVASCRIPT
```

This is prohibited everywhere outside browser-local Response UI state:

```ts
{ kind: "AUTOMATIC" }
```

Do not add `AUTOMATIC` to:

```text
LocalResponseProcessingSchema
ResponseProcessing
ExternalHttpExecutionSchema
publication validation
runtime processors
Prisma/database
Shared contracts
```

### R2 — selecting Automatic does not mutate the Tool definition

When an author selects `Automatic`:

```text
current canonical execution stays unchanged
Response validation success becomes stale only when a real canonical Response change is later installed
Tool dirty state does not change merely because Automatic was selected
```

Automatic owns transient state only:

```text
idle
generating
failure
candidate-selection
```

Leaving Automatic before applying a proposal discards only that transient workflow state.

### R3 — one shared Sample Tool arguments state

Move the current Request-tab-local:

```text
Sample Tool arguments
```

text state to `ExternalHttpEditor` (or the closest single parent shared by Request/Response Automatic).

There must be **one string value** shared by:

```text
Request preview
Response Automatic generation
```

Request must continue to render/edit that value.

Automatic may render/edit the same shared textarea, clearly labelled as the same Sample Tool arguments used by Request. It must not create a second independent arguments state.

Changing sample arguments:

```text
does not dirty/persist the Tool definition
invalidates prior Request preview
invalidates prior Automatic observation/candidate state
```

### R4 — selected-shop plumbing

Pass the current Studio selected-shop identity through the existing Tool-authoring composition so COMMERCE-051 can enforce PER_SHOP Connection scope.

This must work for:

```text
new unsaved Tool authoring
existing persisted DRAFT authoring
```

The server still revalidates shop authorization; client plumbing is not authority.

PLATFORM Connections do not require a shop credential scope.

### R5 — exact Generate action input

`Generate from live response` uses the current authoring state:

```text
current connectionRevisionId
current canonical active Request
current JSON responseFormat
current inputSchema
shared Sample Tool arguments
selected shop context
```

It does not require an already-valid Visual/Direct/JavaScript result definition because generation exists to create one.

If the current Request cannot be represented canonically because Request-local authoring is invalid, generation is unavailable and the user is directed back to Request diagnostics. Do not silently use an older Request while invalid newer Request text is visible.

### R6 — Automatic requires observed 2xx JSON

Generation can infer Visual rules only when COMMERCE-051 returns:

```text
kind: response
HTTP status 200..299
response.json !== null
```

For non-2xx, transport failure, invalid/decode failure or non-JSON response:

```text
stay in Automatic
preserve sample arguments/current Tool definition
show bounded actionable guidance
apply no Visual change
```

Do not run inference against provider error JSON from a non-2xx response.

### R7 — run COMMERCE-052 inference exactly

For an eligible provider response:

```text
observation.response.json
      |
      v
inferVisualResponseTrees(...)
```

Do not duplicate candidate inference in React.

Use COMMERCE-049 terminology in all labels:

```text
Object
List of objects
List of values
Scalar
```

### R8 — zero usable candidates

When inference returns zero candidates:

```text
stay in Automatic
show: no usable Visual response structure could be inferred
show bounded reason/warning summary when available
leave canonical Response unchanged
```

Do not switch to Visual with an empty invalid tree.

### R9 — exactly one usable candidate

When inference returns exactly one candidate:

```text
re-run deriveVisualTreeContract(candidate.authoring)
require ok === true
install candidate.authoring into the existing Visual draft state
set execution.resultPath = candidate.resultPath
set responseProcessing = derived.processing
set resultSchema = derived.schema
keep the current valid JSON responseFormat/mediaTypes
switch active Response mode to VISUAL
mark Tool dirty
invalidate previous Response validation success
```

The user must immediately see the normal existing **Visual rules** editor.

There is no separate Automatic projection table.

### R10 — multiple candidates

When inference returns more than one candidate, Automatic shows only a bounded candidate picker plus generation status/warnings.

Each candidate row shows at minimum:

```text
Source path: "Response root" for "" or exact dot path
Root shape: Object | List of objects
field count
unresolved-field count
```

Candidate order is exactly COMMERCE-052 output order.

The author selects one candidate and clicks a single action equivalent to:

```text
Use selected structure
```

Applying it follows R9.

Do not render editable Visual fields under the candidate picker.

### R11 — unresolved-field warning

If the applied candidate contains COMMERCE-052 unresolved issues, switch to Visual as normal but retain one bounded non-blocking notice equivalent to:

```text
Visual rules were generated from the live response. Some response fields could not be inferred; review the generated rules.
```

Do not render raw provider data or internal stack/error text in that notice.

The unresolved issue count may be shown. Technical issue codes may be secondary, but they are not the primary user message.

### R12 — existing Visual editor/diagnostics are authoritative after generation

After applying a candidate:

```text
Automatic workflow ends
current mode = VISUAL
VisualTreeEditor owns all further edits
deriveVisualTreeContract owns processing/schema derivation
COMMERCE-050 owns actionable validation presentation
```

Do not keep a hidden Automatic copy that later overwrites manual Visual edits.

To generate again, the author deliberately selects Automatic again and performs another live generation.

### R13 — preserve per-mode drafts

Existing Direct/Visual/JavaScript draft retention remains intact.

Automatic is not a persisted mode draft. Successful generation replaces the **current Visual draft** with the selected generated proposal, because that is the explicit Generate action.

It must not overwrite inactive Direct/JavaScript local drafts.

### R14 — no persistence from observation/generation itself

The live response, inferred candidates and sample arguments are browser/session authoring state only.

Generation performs no Tool/Revision save.

For a new Tool, generated Visual state is persisted only by the existing final Create from Review.

For an existing DRAFT, generated Visual state is persisted only by the existing Save Draft action.

A successful generation does not satisfy `LIVE_TEST_REQUIRED`.

### R15 — bounded actionable failures

Use the COMMERCE-050 presentation principle:

```text
what failed
what the author can do next
```

Do not show raw server/thrown/provider error messages.

At minimum distinguish:

```text
invalid sample arguments
Request is not currently executable
shop required for selected Connection
Connection unavailable
provider unavailable
provider deadline
provider returned non-2xx
provider response cannot be decoded as current JSON response format
no inferable structure
```

## Work Items

- [x] Lift Sample Tool arguments to one `ExternalHttpEditor`-owned shared state.
- [x] Keep Request preview wired to that shared state.
- [x] Plumb selected shop for both new and existing Tool authoring without trusting it server-side.
- [x] Add transient `Automatic` Response selection without changing canonical response schemas.
- [x] Call COMMERCE-051 observation using the exact current Request/arguments/response format.
- [x] Run COMMERCE-052 inference on eligible 2xx JSON only.
- [x] Add zero/one/multiple candidate deterministic UI flows.
- [x] Install selected candidate into existing Visual draft + canonical execution through `deriveVisualTreeContract(...)`.
- [x] Switch successful generation to Visual rules.
- [x] Preserve Direct/JavaScript drafts and existing Visual/Response validation behavior.
- [x] Add new/existing Tool UI regressions and no-persistence evidence.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-042
  final JavaScript Request UI/local-draft behavior

ARCH-021-COMMERCE-050
  actionable Response validation presentation

ARCH-021-COMMERCE-051
  live bounded provider observation

ARCH-021-COMMERCE-052
  VisualResponseInference candidates

ARCH-021-COMMERCE-048/049 transitively
  exact Visual authoring model and terminology
```

Produces:

```text
browser-local Automatic generation workflow
-> existing VisualAuthoringRoot
-> existing canonical VISUAL processing/result schema
```

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-042
- ARCH-021-COMMERCE-050
- ARCH-021-COMMERCE-051
- ARCH-021-COMMERCE-052

## Enables

None.

## Acceptance Criteria

- [x] Response visibly offers `Automatic` alongside Visual rules/Direct/JavaScript.
- [x] `AUTOMATIC` is not added to any persisted/runtime processing schema.
- [x] Selecting Automatic alone does not mutate/dirty the canonical Tool definition.
- [x] Request/Automatic/Test share one Sample Tool arguments string/state.
- [x] Sample arguments remain authoring-only and are never persisted.
- [x] New and existing Tool flows provide selected-shop context for PER_SHOP live calls.
- [x] Automatic uses the exact current canonical Request candidate, not a stale older Request.
- [x] Automatic performs one COMMERCE-051 live observation per explicit Generate action.
- [x] Only 2xx JSON responses are passed to inference.
- [x] Zero candidate result leaves Response unchanged with actionable guidance.
- [x] One candidate is applied directly then the UI switches to Visual rules.
- [x] Multiple candidates show a picker only; no duplicate Visual editor is rendered.
- [x] Candidate labels use `Object` / `List of objects`; nested field terminology remains C049 exact.
- [x] Applying a candidate sets exact `resultPath`, Visual authoring tree, derived processing and derived result schema.
- [x] `deriveVisualTreeContract(...)` remains the only processing/schema derivation authority.
- [x] Automatically inferred fields remain optional (`omitIfMissing`) as provided by C052.
- [x] Generated Visual state can be edited normally after generation.
- [x] COMMERCE-050 validation diagnostics continue to work on generated Visual state.
- [x] Direct/JavaScript inactive drafts survive generation.
- [x] Observation/generation performs no Tool/Revision save and does not satisfy `LIVE_TEST_REQUIRED`.
- [x] All authoring tabs remain freely navigable.

## Mandatory Regression Scenarios

Add focused UI/composition tests proving at least:

```text
1. selector shows Visual rules / Direct / JavaScript / Automatic.
2. selecting Automatic does not call onChange and does not dirty Tool.
3. shared sample arguments edited in Request are visible unchanged in Automatic.
4. shared sample arguments edited in Automatic are visible unchanged in Request.
5. malformed sample JSON blocks Generate locally and performs no observation call.
6. invalid current Request blocks Generate instead of using stale canonical-looking UI state.
7. PER_SHOP Connection without selected shop shows actionable shop-required result.
8. provider transport/deadline failure leaves Response unchanged.
9. provider 404/429/503 leaves Response unchanged and does not infer.
10. 2xx non-JSON/null-json response leaves Response unchanged.
11. 2xx JSON + zero candidates stays Automatic with guidance.
12. one OBJECT candidate installs Visual, resultPath and derived schema, then shows normal Visual editor.
13. one LIST candidate installs root List of objects and exact Source path.
14. generated nested SCALAR_LIST is shown by existing UI as List of values.
15. multiple candidates show picker in C052 order and no editable Visual tree.
16. selecting second candidate applies exactly that candidate and switches to Visual.
17. unresolved issues apply usable candidate but show bounded review notice.
18. after generation, manual Visual edit is retained and not overwritten by hidden Automatic state.
19. Direct draft survives Automatic -> Visual generation -> Direct switch.
20. JavaScript draft survives Automatic -> Visual generation -> JavaScript switch.
21. generated invalid/local edit uses C050 actionable diagnostic path.
22. New Tool generation does not create/persist Tool until existing Review Create.
23. existing DRAFT generation does not save until existing Save Draft.
24. no AUTOMATIC value appears in submitted definition/persistence payload.
25. successful generation does not create a live-test publication receipt.
```

## Validation

Run at minimum:

- [x] `npm run test:arch020-external-tools-ui`
- [x] focused `tests/tool-authoring-screen.test.tsx`
- [x] `npm run test:arch021-tool-authoring-common` when shared New/Existing Tool composition changes
- [x] targeted ESLint on changed files
- [x] `git diff --check`
- [x] changed-file TypeScript diagnostics contain no task-owned error

Do not rerun provider/security suites owned by COMMERCE-051 unless this task changes that implementation.

## Stop Condition

After Automatic generation works through the existing Visual editor for both new and existing Tool authoring, all mandatory UI regressions pass and the Completion Report is complete, set the task to `review`, clear the execution claim under the normal workflow, return control to `moda_architect` and STOP. Do not begin independent live-Test tasks.

## Implementation Notes

The critical UI invariant is:

```text
Automatic = generator
Visual rules = editor
Test = observer
```

Do not collapse these responsibilities merely because they share the same External HTTP editor.

## Completion Report

### Status

Complete; submitted for Architect Review.

### Files Changed

- `src/studio/external-http/editor.tsx`
- `src/studio/external-http/request-tab.tsx`
- `src/studio/external-http/response-tab.tsx`
- `src/studio/external-http/test-tab.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`

### Work Completed

- Lifted one Sample Tool arguments string into `ExternalHttpEditor`, shared by Request preview, Automatic generation, and Test; argument edits invalidate stale Request previews and Automatic state without dirtying or persisting the Tool.
- Added transient Automatic Response mode using the COMMERCE-051 observation action with the current canonical Request, JSON response format, input schema, shared arguments, and selected shop. Only successful 2xx JSON observations reach COMMERCE-052 inference.
- Added zero/one/multiple candidate flows, candidate ordering and selection, bounded failure guidance, unresolved-field notice, and candidate application through `deriveVisualTreeContract(...)` into the existing Visual editor.
- Preserved Direct, Visual, and JavaScript drafts; guarded against late observations after leaving Automatic or changing generation context; kept Visual editing and COMMERCE-050 validation authoritative after application.
- Wired selected-shop context through New Tool and existing DRAFT composition. Added regression evidence for shop scope, shared arguments across all three tabs, no intermediate persistence, and canonical-only Create/Save payloads.

### Validation Results

- `npm run test:arch020-external-tools-ui`: passed, 66 tests.
- `npx vitest run tests/tool-authoring-screen.test.tsx`: passed, 13 tests.
- `npm run test:arch021-tool-authoring-common`: 85/86 tests passed; one existing `commerce-lifecycle.test.ts` case still receives `INVALID_DEFINITION` where its assertion expects `LIVE_TEST_REQUIRED`.
- Targeted ESLint on all nine changed files: passed.
- `git diff --check`: passed.
- `npm run typecheck`: non-zero with 250 diagnostics in 21 files. Pylance and filtered TypeScript output report no diagnostics in task-changed files. This is recorded against `TYPECHECK-001`; the observed count differs from its historical 171-error revision-specific observation, so the baseline count is not claimed as an exact match.

### Deviations

No functional scope deviations. The shared authoring packet was run as required and retains one pre-existing lifecycle expectation mismatch outside the changed files.

### Assumptions

The selected shop ID is context only; COMMERCE-051 remains responsible for revalidating authorization and PER_SHOP scope. Generation is transient and does not replace the later Create or Save Draft lifecycle.

### Unresolved Issues

- `npm run test:arch021-tool-authoring-common` retains the unrelated lifecycle failure described above.
- Repository-wide typecheck remains non-zero under `TYPECHECK-001` (250 current diagnostics across 21 files); no task-changed file has a diagnostic. The documented historical count is revision-specific and differs from this run.

### Architectural Concerns

No additional architectural concerns identified. Architect Review remains pending.

### Git / VCS

Implementation branch: `task/ARCH-021-COMMERCE-053`

Implementation commit: `534dbb5` (`feat(commerce): add Automatic Visual response generation`), pushed to `origin/task/ARCH-021-COMMERCE-053`.

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-053`

Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-053`

Parent task branch: `task/ARCH-021-COMMERCE-053`.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is architecturally aligned in its main Automatic-generation flow: the implementation keeps `AUTOMATIC` browser-local, shares one Sample Tool arguments state, passes selected-shop context to the accepted COMMERCE-051 observation boundary, sends only eligible 2xx JSON to COMMERCE-052 inference, installs candidates through `deriveVisualTreeContract(...)`, returns successful generation to the existing Visual editor, and does not persist during observation/generation.

The attempt nevertheless requires correction before acceptance.

1. **R2 is violated when Automatic is exited back to the unchanged canonical Response mode.** `response-tab.tsx` routes every non-Automatic selection through `resetMode(...)`. Therefore `VISUAL -> AUTOMATIC -> VISUAL` (and the corresponding unchanged DIRECT/JAVASCRIPT case) calls `invalidateResponseValidation()`, `onChange(...)` and `onDirty()` even though no generated proposal or other canonical Response change was applied. R2 requires Automatic selection/abandonment to remain transient: Tool dirty state and a previously successful Response validation may become stale only after a real canonical Response change.
2. **Mandatory regression scenario 13 is not proved.** The submitted tests prove a nested LIST candidate selected from the multiple-candidate picker, but not the required exactly-one LIST candidate path that automatically installs a root `List of objects` candidate and its exact source path.
3. **Mandatory regression scenario 25 is not proved explicitly.** Add focused evidence that successful Automatic generation does not create/satisfy the live-test publication receipt and `LIVE_TEST_REQUIRED` remains unsatisfied until the separately owned live-test receipt boundary exists.
4. **The Completion Report misattributes the Commerce repository-wide typecheck result to `TYPECHECK-001`.** `docs/development-baseline.md` scopes `TYPECHECK-001` to `moda-interact/`, not `moda-interact-commerce/`. The report may record the observed Commerce typecheck as non-zero/unrelated with zero diagnostics in changed files, but must not claim `TYPECHECK-001` as the applicable baseline identifier.

Correction contract for Attempt 2:

- Preserve the current canonical persisted mode when Automatic is abandoned without applying a proposal. Returning from Automatic to that same mode must not call `onChange`, must not mark the Tool dirty, and must not invalidate a successful Response validation.
- Preserve existing behavior when the author intentionally chooses a *different* persisted mode from Automatic; that remains a real canonical change and may dirty/invalidate normally.
- Add an explicit regression for `persisted mode -> Automatic -> same persisted mode` proving no canonical mutation/dirty/validation invalidation.
- Add the missing mandatory exactly-one root LIST candidate regression and exact `resultPath` assertion.
- Add explicit no-live-test-receipt / `LIVE_TEST_REQUIRED` evidence for successful generation.
- Correct the Completion Report typecheck attribution. Do not modify `docs/development-baseline.md` merely to make this task pass.
- Keep COMMERCE-051 transport/security behavior and COMMERCE-052 inference semantics unchanged; this is a Response composition/state correction only.

### Reviewed Files

- `src/studio/external-http/editor.tsx`
- `src/studio/external-http/request-tab.tsx`
- `src/studio/external-http/response-tab.tsx`
- `src/studio/external-http/test-tab.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `docs/development-baseline.md`
- `docs/decisions/commerce/ARCH-021/COMMERCE-053-add-automatic-response-generation.md`
- `docs/decisions/commerce/ARCH-021/_index.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

Recorded submission evidence reviewed:

- `npm run test:arch020-external-tools-ui`: 66/66 passed.
- focused `tests/tool-authoring-screen.test.tsx`: 13/13 passed.
- `npm run test:arch021-tool-authoring-common`: 85/86; recorded failure is outside the C053 changed files and concerns an existing lifecycle expectation (`LIVE_TEST_REQUIRED` versus `INVALID_DEFINITION`).
- targeted ESLint: passed.
- `git diff --check`: passed.
- repository-wide Commerce typecheck: non-zero with 250 diagnostics across 21 files; submitted changed-file diagnostics are clean. `TYPECHECK-001` is not accepted as the baseline identifier because that baseline is scoped to `moda-interact/`.

The submitted archive is a source snapshot rather than the live Git worktrees, so clean/synchronized branch state and pushed commit identity are recorded from the Completion Report rather than independently re-queried from Git metadata.

### Architecture Conformance

Main Automatic generation architecture: **conformant**.

Transient-mode abandonment semantics under R2 and mandatory regression completeness: **not yet conformant**.

Repository ownership, persistence boundary, C051 observation reuse, C052 inference reuse, Visual-editor authority and selected-shop server-revalidation boundary are otherwise preserved.

### Follow-up

Return the same task to `ready` for Attempt 2. COMMERCE-054 remains dependency-gated until COMMERCE-053 is architect-accepted Complete.
