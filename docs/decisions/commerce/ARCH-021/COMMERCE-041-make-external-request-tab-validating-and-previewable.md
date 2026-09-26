---
id: ARCH-021-COMMERCE-041
architecture_id: ARCH-021
title: Make the External HTTP Request tab validate and preview the authored request
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 61
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-040
enables:
  - ARCH-021-COMMERCE-042
created: 2026-09-26
updated: 2026-09-26
---

# Make the External HTTP Request tab validate and preview the authored request

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make the External HTTP Request tab the complete non-network authoring checkpoint for request construction: retain/edit invalid intermediate input visibly, validate the current request configuration with bounded server-authoritative diagnostics, and show the exact safe HTTP request descriptor produced from sample Tool arguments before the author moves to another freely navigable tab.

## Context

Developer manual review after COMMERCE-039 identified three Request-tab defects:

1. Request controls are edited through `ExternalHttpExecutionSchema.safeParse(...)`; when an intermediate edit is invalid the update is silently discarded, so the author receives no useful error and may see the field snap back or appear not to accept input.
2. The safe `Preview request` capability from COMMERCE-023 is presented under the Test tab even though it answers the Request-tab question: *what HTTP request will this definition construct?*
3. The Request tab contains a disabled `Manage connections` button during local-only new-Tool authoring. Connection management is a separate Studio domain and navigating there would abandon the local creation session. The product decision is to remove this button from the Tool Request surface rather than preserve/navigation-couple a local creation session.

The target Request tab is still zero-provider-I/O. It validates and previews request construction only. Real provider execution belongs to the later Test-tab review and is not part of this task.

COMMERCE-040 supplies the final canonical JavaScript binding semantics this task must validate and preview.

## Scope

Primary files:

```text
src/studio/external-http/request-tab.tsx
src/studio/external-http/test-tab.tsx
src/studio/external-http/editor.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/external-validation-server-actions.ts
src/commerce/tool-authoring/external-validation.ts
app/styles.css                                      # bounded Request-tab presentation only

tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
tests/external-tool-authoring-server-actions.test.ts
tests/external-tool-authoring-validation.test.ts
```

Additional directly affected Request-tab tests may change when required by the same bounded capability.

## Out of Scope

- Live DNS, HTTP/provider calls or credential reads.
- Redesigning the Test tab beyond removing Request-construction preview from it and leaving a truthful placeholder/state for later review.
- JavaScript binding-table controls and JavaScript editor sizing/mode preservation; COMMERCE-042 owns those UI changes.
- Response, Agent contract or Review tab redesign.
- Phase 2 tab gating, locked tabs, mandatory Next/Back or completion-state progression.
- Persisting intermediate new-Tool state.
- Connection creation/editing/navigation from this Request tab.
- Database schema changes.

## Requirements

### R1 — remove Manage connections from Tool Request authoring

Remove the `Manage connections` button/affordance from the External HTTP Request tab for both new-Tool and persisted-draft authoring.

The Request tab keeps:

```text
Connection revision selector
safe connection metadata summary
```

but does not navigate into the Connections domain.

Remove now-unused Request-tab callback props/tests rather than leaving a disabled or dead control.

### R2 — Request-specific authoring validation

Add/reuse a named non-mutating, hierarchy-authorized Request validation boundary that can validate the current request without requiring the Response, Agent contract or Review portions of the Tool to be complete.

The bounded validation input must include only what request validation needs, such as:

```text
connectionRevisionId
inputSchema
request construction
```

It must validate, as applicable:

- selected connection revision metadata exists and is authoring-eligible;
- declarative relative path;
- declarative query mapping names/source references/literal bounds;
- safe static headers and reserved-header restrictions;
- COMMERCE-040 JavaScript bindings;
- JavaScript request-source compilation/runtime-version compatibility.

It must perform zero provider I/O, zero DNS lookup and zero credential read/decryption.

Use the existing bounded `ToolAuthoringValidation` issue model/path conventions rather than inventing generic strings where structured issues are available.

### R3 — do not silently discard invalid intermediate edits

The Request-tab form must be able to represent a temporarily invalid authoring value long enough to show the author what is wrong.

At minimum, an invalid intermediate edit to declarative fields such as:

```text
HTTP path
query key / mapping source value
safe-header name/value
```

must not simply disappear because the complete `ExternalHttpExecutionSchema` rejected it.

Use Request-local raw/form state where necessary. Synchronize the canonical execution value only when the relevant authored request is parseable/valid enough to do so.

Visible validation diagnostics must identify the affected field/row where practical.

Do not persist invalid intermediate new-Tool state.

### R4 — move Request construction preview into Request

Move the COMMERCE-023 request-construction preview experience from the Test tab to the Request tab.

The Request tab must provide bounded sample Tool arguments for preview and, on `Preview request`, show the safe descriptor as an HTTP-shaped summary containing at least:

```text
GET <selected connection origin><relative path>?<serialized query>
Auth: not configured OR configured/redacted
Safe headers: authored descriptor headers only
```

The preview must use the current Request-tab authoring state, current `inputSchema` and COMMERCE-040 JavaScript binding semantics.

It must never display a credential value.

### R5 — distinguish validation from preview

Request validation and request preview answer different questions and must be presented distinctly:

```text
Validate request
    Is the current request definition structurally/authoritatively valid?

Preview request
    With these sample Tool arguments, what safe request descriptor is produced?
```

Changing any request field, connection revision, JavaScript source/binding, input schema or preview arguments must invalidate the relevant displayed validation/preview state rather than leaving stale success/output visible.

### R6 — Test tab no longer owns Request preview

After this task, `ExternalHttpTestTab` must not present `Request construction preview`, Tool-argument preview input or `Preview request`.

Do not invent the later live Test-tab workflow in this task. Leave a concise truthful state indicating that request construction is handled in Request and that live provider testing is not implemented by this task, or preserve the minimum existing shell needed for the next independent Test-tab review.

### R7 — no gating

Invalid Request-tab state must be obvious, but this task MUST NOT disable the Response/Test/Agent contract/Review tabs solely because Request is invalid.

Phase 2 progression/gating remains explicitly deferred.

## Work Items

- [x] Remove the Manage connections control and obsolete callback plumbing/tests.
- [x] Add/reuse bounded server-authoritative Request-only validation.
- [x] Preserve invalid intermediate declarative form values and surface useful diagnostics.
- [x] Move Tool-arguments request preview from Test to Request.
- [x] Render the exact safe GET descriptor with serialized query, redacted auth state and safe headers.
- [x] Invalidate stale validation/preview results on relevant edits.
- [x] Remove Request-preview controls from Test without implementing live Test behavior.
- [x] Add focused zero-provider-I/O, UI and stale-state regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-023
safe request preview / bounded authoring validation conventions

ARCH-021-COMMERCE-040
canonical JavaScript request binding semantics

ARCH-021-COMMERCE-039
local-only new-Tool authoring
```

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-040

## Enables

- ARCH-021-COMMERCE-042

## Acceptance Criteria

- [x] The External HTTP Request tab contains no Manage connections button/control.
- [x] Connection selection and safe metadata remain available.
- [x] Request validation runs without requiring Response/Test/Agent-contract completion.
- [x] Request validation performs zero DNS/provider/credential operations.
- [x] Invalid intermediate declarative edits remain visible and receive actionable diagnostics instead of being silently discarded.
- [x] Request preview is presented only in the Request tab, not the Test tab.
- [x] Preview displays the exact safe GET origin/path/query shape, safe headers and configured/redacted authentication state.
- [x] Preview uses schema-validated sample Tool arguments and canonical request construction.
- [x] Validation/preview success becomes stale immediately after relevant authoring changes.
- [x] No Tool/ToolRevision persistence occurs merely from Request validation/preview.
- [x] All authoring tabs remain freely navigable regardless of Request validity.
- [x] No live provider call is introduced.

## Validation

- [x] focused External HTTP Request-tab UI tests
- [x] focused External HTTP authoring validation/Server Action tests
- [x] explicit zero DNS/transport/credential-read proof for Request validation and preview
- [x] existing External UI/common Tool-authoring regression packet required by repository scripts
- [x] targeted TypeScript diagnostics or repository typecheck with baseline reconciliation
- [x] targeted ESLint for changed files
- [x] `git diff --check`

## Stop Condition

After Request-specific validation, exact safe preview relocation, invalid-form diagnostics, Manage-connections removal and required regressions are complete, set the task to `review`, complete the Completion Report and STOP. Do not add live provider testing, redesign later tabs or begin COMMERCE-042.

## Implementation Notes

The current `ExternalHttpRequestTab.update()` validates the entire patched execution and discards the edit when parsing fails. That pattern is specifically insufficient for an authoring form because it prevents the UI from showing the invalid text that needs correction.

Do not weaken canonical server validation to accommodate intermediate form state. Keep invalid text local to the form and only emit canonical `ExternalHttpExecution` through `onChange` when appropriate.

The Request preview remains a descriptor preview, not evidence of a successful provider call and not evidence that can satisfy `LIVE_TEST_REQUIRED`.

## Completion Report

### Status
Ready for Review

### Files Changed
`app/styles.css`; `src/commerce/integration/external/index.ts`; `src/commerce/tool-authoring/external-validation.ts`; `src/commerce/tool-definition/contracts.ts`; `src/studio/external-http/editor.tsx`; `src/studio/external-http/request-tab.tsx`; `src/studio/external-http/test-tab.tsx`; `src/studio/tools/external-validation-server-actions.ts`; `src/studio/tools/new-tool-editor.tsx`; `src/studio/tools/tool-editor.tsx`; `tests/external-tool-authoring-server-actions.test.ts`; `tests/external-tool-authoring-validation.test.ts`; `tests/external-tools-ui.test.tsx`; `tests/tool-authoring-screen.test.tsx`.

### Work Completed
Added strict Request-only authoritative validation through the existing metadata-only connection port, with declarative mapping checks and bounded JavaScript request compilation. Added an ADMIN-authorized Server Action and wired both new-tool and persisted-draft editors.

Moved safe request preview and sample arguments to Request, rendered the GET origin/path/query with redacted auth state and descriptor headers, and left Test as a truthful no-live-testing placeholder. Request-local form state keeps invalid intermediate values visible across every tab; validation and preview results are keyed to their relevant inputs and stale outputs remain hidden. Removed Manage connections navigation without adding persistence or provider calls.

Implementation commit: `a37dcfc` (`feat(commerce): validate and preview external requests`), pushed to `task/ARCH-021-COMMERCE-041` in `moda-interact-commerce`.

### Validation Results
Passed: `npm run test:arch021-tool-authoring-common` (85 tests); `npm run test:arch020-external-tools-ui` (17 tests); `npm run test:arch021-external-tool-authoring-validation` (45 tests); focused `tests/tool-authoring-screen.test.tsx` (10 tests). UI coverage also verifies new-tool persistence remains untouched by validation/preview, safe descriptor output, invalid text retention, free tab navigation, and stale in-flight preview suppression.

Passed: targeted ESLint for all changed TypeScript/TSX files; editor diagnostics report no errors in changed TypeScript/TSX files; `git diff --check`.

Repository `npm run typecheck` remains red with 249 diagnostics across 20 files outside this task's changed files. No diagnostics were reported for changed files.

### Task Execution Evidence
Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-041`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-041`; both task branches are `task/ARCH-021-COMMERCE-041`. Both worktrees were newly created; shared workspace and implementation checkouts were not switched or mutated, and no other task worktree was reused.

Start synchronization per launcher: parent and implementation remote task fast-forward were `not-needed`; `origin/main` was `already-current` in both. Recursive implementation submodule sync and initialization passed; `database` is at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

Parent claim was committed and pushed as `3afc6c08350a0bc1132539e36f48eb3675487f1e`. Implementation commit `a37dcfc` is pushed. Architect Review remains unchanged.

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
Accepted — Attempt 1

### Review Notes

#### Attempt 1 review — 2026-09-26

Reviewed implementation `a37dcfc` and parent report handoff `a8f18256` against the bounded COMMERCE-041 Request-tab contract.

Accepted. The implementation keeps COMMERCE-041 correctly scoped to Request authoring. It removes `Manage connections`, preserves connection selection and safe metadata, retains invalid intermediate Request form values locally instead of silently discarding them, adds ADMIN-authorized Request-only server validation with bounded structured issues, moves safe request-descriptor preview into Request, leaves Test as a truthful no-live-provider placeholder, and keeps all authoring tabs freely navigable.

The architect explicitly confirms that COMMERCE-041 does **not** own cross-tab gating or final Create/Save/Publish blocking. Request-local raw state may temporarily differ from the last schema-valid canonical Tool draft while the author is editing; this task's requirement is to retain that raw Request state and diagnose it within Request. Phase-2 progression/gating and other-tab behavior remain out of scope. The accepted COMMERCE-036/037 atomic create boundary remains unchanged.

Request validation/preview are non-mutating and zero-provider-I/O. Validation uses only the bounded Request inputs and safe connection metadata; preview produces the safe descriptor and never reads credentials or performs transport/DNS work. COMMERCE-040 bounded JavaScript binding semantics remain in force.

### Reviewed Files
- `src/studio/external-http/request-tab.tsx`
- `src/studio/external-http/test-tab.tsx`
- `src/studio/external-http/editor.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/external-validation-server-actions.ts`
- `src/commerce/tool-authoring/external-validation.ts`
- `src/commerce/integration/external/index.ts`
- `tests/external-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/external-tool-authoring-server-actions.test.ts`
- `tests/external-tool-authoring-validation.test.ts`

### Validation Reviewed
Accepted submitted evidence:

```text
Common Tool-authoring packet:                  85 passed
External UI packet:                            17 passed
Request validation / Server Action packet:     45 passed
Focused new-tool authoring packet:              10 passed
Targeted ESLint:                                passed
Changed-file diagnostics:                      clean
git diff --check:                              passed
Repository typecheck:                           249 unrelated diagnostics outside task-owned files
```

Source/test inspection additionally confirms:

```text
Request contains Validate request + Preview request
Test contains no Request preview controls
Manage connections is absent from Request
invalid Request edits remain visible
all five authoring tabs remain navigable
Request validation/preview do not persist Tool state
zero DNS/transport/credential-read behavior is covered
```

### Architecture Conformance
Conforms. COMMERCE-041 remains a bounded Request-tab follow-up. It does not redesign Response, Agent contract or Review, introduce progression gating, add provider execution, change database schema, or alter the accepted atomic creation lifecycle.

### Follow-up
`ARCH-021-COMMERCE-042` is promoted to `ready` to complete the JavaScript-specific Request binding/editor UX. Manual review should remain on the Request tab until COMMERCE-042 is accepted.
