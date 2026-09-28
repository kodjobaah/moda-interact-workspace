---
id: ARCH-021-COMMERCE-081
architecture_id: ARCH-021
title: Show the populated Result Template as the primary External Test result
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 75
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-078
  - ARCH-021-COMMERCE-079
  - ARCH-021-COMMERCE-080
enables:
  - ARCH-021-COMMERCE-083
  - ARCH-021-SYSTEM-TEST-002
created: 2026-09-28
updated: 2026-09-28
---

# Show the populated Result Template as the primary External Test result

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Integrate the already-implemented COMMERCE-080 External HTTP live-Test backend with the canonical authoring-session validation/Test-freshness model, show the server-rendered populated Result Template as the primary Test result, and require a current successful External Test before Create/Save may persist the current External candidate.

## Context

COMMERCE-080 is Complete and supplies the canonical non-durable External live-Test backend. It accepts one complete External Tool definition, validates Result Template compatibility before provider I/O, executes the authored Request/Response pipeline, validates the canonical result and returns `renderedText` produced by the production renderer.

COMMERCE-078 owns the new-Tool authoring-session validation ledger and common Test freshness state. COMMERCE-079 applies the same session/persistence model to persisted DRAFT authoring. This task must consume those accepted capabilities; it must not create a second authoring/Test authority inside `ExternalHttpTestTab`.

The existing External Test UI already has local request/response/argument/shop staleness handling. That local mechanism is no longer sufficient once Review/Save is gated by the session-level current Test checkpoint. This task makes the common authoring session authoritative while retaining provider-specific safe diagnostics locally.

## Scope

Primary implementation areas:

```text
src/studio/external-http/editor.tsx
src/studio/external-http/test-tab.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/external-validation-server-actions.ts   # consume only unless an integration defect is proven
src/studio/tools/<C078 authoring-session module>         # consume; do not create a competing store
```

Tests:

```text
tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
tests/external-http-live-test-action.test.ts
```

## Out of Scope

- Reimplementing or changing COMMERCE-080 backend execution/rendering semantics.
- Creating a second External live-Test Server Action or result contract.
- Changing C078 section-validation semantics or creating a competing validation/Test store.
- Changing C079 persisted CAS/persistence-dirty semantics.
- Shopify Test UI; COMMERCE-083.
- Publication proof or publication-gate changes.
- Persisting Test output or provider responses.
- Changing Request, Response or Result Template authoring ownership.
- Rendering/interpolating Result Template tokens in React.

## Requirements

### R1 — consume the canonical C078 authoring Test contract; do not invent another one

Before implementation, inspect the accepted COMMERCE-078 authoring-session API.

It must provide one common Test checkpoint with these semantics:

```ts
type AuthoringTestStatus =
  | "NOT_RUN"
  | "RUNNING"
  | "PASSED"
  | "FAILED"
  | "STALE";

type AuthoringTestSnapshot = {
  toolDefinitionRevision: number;
  requestRevision: number;
  responseRevision: number;
  resultTemplateRevision: number;
};

type AuthoringTestState = {
  status: AuthoringTestStatus;
  testedSnapshot: AuthoringTestSnapshot | null;
};
```

and semantic operations equivalent to:

```text
currentAuthoringSnapshot(session)
isCurrentTestPassed(session)
mark Test RUNNING for a submitted snapshot
mark Test PASSED for that submitted snapshot
mark Test FAILED for that submitted snapshot
mark Test STALE / clear testedSnapshot
```

Use the actual accepted C078 export names. Mechanical naming differences are allowed; semantic differences are not.

If C078 is marked Complete but the implementation does not expose one authoritative session-level Test state with those semantics, **STOP and return this task Blocked** as a dependency defect. Do not add a second authoritative Test store to work around the missing contract.

Provider-specific display state in `ExternalHttpTestTab` may remain local, but it is not allowed to decide whether Review/Save considers the Tool tested.

### R2 — one exact assembled External candidate is the Test input

The Test invocation must use the same current assembled definition that Review/Create/Save would persist at that moment.

The definition passed to COMMERCE-080 must contain exactly the current values for:

```text
Tool Definition:
  name
  definitionVersion
  description

Request:
  inputSchema
  execution.connectionRevisionId
  execution.method
  execution.request

Response:
  execution.responseFormat
  execution.resultPath
  execution.responseProcessing
  execution.resultSchema

Result Template:
  responseTemplate
```

Do not independently reconstruct a second Tool definition inside `ExternalHttpTestTab` from stale props if C078/C079 already expose an assembled current candidate. The component must receive either:

```text
current complete CommerceToolDefinition
```

or a callback that returns that exact current definition immediately before Test starts.

The Server Action remains the existing:

```text
testExternalHttpCandidateAction
```

with the already-implemented COMMERCE-080 semantic input:

```ts
{
  definition: CommerceToolDefinition;
  arguments: Record<string, unknown>;
  shopId: string | null;
}
```

Do not add another Test action.

### R3 — Test is runnable only from a current validated authoring candidate

Before invoking `testExternalHttpCandidateAction`, require all four authored sections to be current and valid according to the C078/C079 validation ledger:

```text
Tool Definition  current VALID
Request          current VALID
Response         current VALID
Result Template  current VALID
```

Also require:

```text
complete assembled definition parses through the canonical Tool definition boundary
Test arguments are valid JSON
Test arguments are a JSON object
Test arguments serialized input is <= 64 KiB
```

External `shopId` remains nullable because COMMERCE-080 already permits `shopId: string | null` and connection scope determines whether a shop is required.

Do **not** automatically run missing section validations from Test. Instead show exactly one owning-step message for the first unmet authored prerequisite:

```text
Tool Definition invalid/stale -> "Return to Tool Definition and validate the current values."
Request invalid/stale         -> "Return to Request and validate the current values."
Response invalid/stale        -> "Return to Response and validate the current values."
Result Template invalid/stale -> "Return to Result Template and validate the current values."
```

Invalid Test arguments stay on Test and show the bounded local JSON error.

No message may direct the user to Agent Contract.

### R4 — exact common Test lifecycle

Immediately before the backend call:

1. Read the exact current assembled candidate.
2. Capture:

```ts
const submittedSnapshot = currentAuthoringSnapshot(session);
```

3. Capture one provider-local run identity from exactly:

```text
submittedSnapshot
Test arguments text
selected shopId or null
```

4. Mark the common session Test state `RUNNING` for `submittedSnapshot`.
5. Invoke `testExternalHttpCandidateAction` exactly once.

The Test is PASSED only when all of the following are true:

```text
Server Action result.kind === "ok"
requestConstruction.status === "passed"
connectionResolution.status === "passed"
providerRequest.status === "passed"
responseProcessing.status === "passed"
resultValidation.status === "passed"
resultRendering.status === "passed"
renderedText is a string
```

If the submitted authoring snapshot and provider-local run identity still match the current UI state, set:

```text
common Test status = PASSED
common testedSnapshot = submittedSnapshot
```

If the backend action returns an error or any required stage is not `passed`, and the submitted identity is still current, set:

```text
common Test status = FAILED
common testedSnapshot = submittedSnapshot
```

If any authored section, Test arguments, or selected shop changes while the backend request is in flight, the returned response is stale. It must not set PASSED or FAILED for the current candidate. The UI must:

```text
set common Test status = STALE
set common testedSnapshot = null
discard/ignore the returned result for current-candidate readiness
```

Preserve existing concurrent-run protection. A late response from run N must never overwrite the state/result of run N+1.

### R5 — deterministic Test staleness

C078/C079 are authoritative for staling Test when an authored section changes. Do not duplicate section-revision logic in the External component.

External Test must additionally mark the common Test state STALE and clear its provider-specific displayed result when either of these changes:

```text
Test arguments text
selected shopId
```

This applies even though neither value is persisted as part of the Tool definition.

Changing only the selected authoring tab must not stale Test.

When Test is staled use the common transition:

```text
status = STALE
testedSnapshot = null
```

Do not preserve an old PASSED checkpoint with a warning.

### R6 — server-rendered agent result is the primary success surface

On a successful live Test, render this section before stage/request/provider/processed-result diagnostics:

```tsx
<section aria-label="Result shown to agent">
  <h4>Result shown to agent</h4>
  <pre>{renderedText}</pre>
</section>
```

The displayed text must be exactly the `renderedText` returned by COMMERCE-080. React must not interpolate or render the Result Template independently.

After the primary result, preserve safe diagnostics for:

```text
Live Test stages
Request sent
Provider response
Processed Tool result
```

Existing diagnostic bounds/redaction must not be widened.

### R7 — External Create/Save requires a current PASSED Test

After this task, External persistence readiness must include the common current-Test predicate.

For a new External Tool:

```ts
canCreateExternal =
  existingC078NewToolSaveEligibility &&
  isCurrentTestPassed(session);
```

For a persisted External DRAFT:

```ts
canSaveExternalDraft =
  existingC079PersistedSaveEligibility &&
  isCurrentTestPassed(session);
```

`existingC078NewToolSaveEligibility` means the current section-validation/schema-validity/lock/pending rules already accepted in C078.

`existingC079PersistedSaveEligibility` means the current section-validation, persistence-dirty, CAS/lock/pending rules already accepted in C079.

Do not replace either existing predicate. Add the current Test requirement to it.

The exact consequences are:

```text
NOT_RUN -> Create/Save disabled
RUNNING -> Create/Save disabled
FAILED  -> Create/Save disabled
STALE   -> Create/Save disabled
PASSED for an older snapshot -> Create/Save disabled
PASSED for current snapshot -> Test requirement satisfied
```

Review remains navigable while Test is not current/passed. Do not turn the authoring UI into forced sequential Next/Previous navigation.

This task must change only the External provider gate. Do not make Shopify Create/Save depend on Test here; COMMERCE-083 owns that provider gate.

### R8 — Test output is non-durable and does not create persistence dirtiness

Running Test, receiving Test output, changing Test arguments, changing selected shop, or staling Test must perform zero:

```text
createToolWithInitialDraft
updateToolDraft
publication-proof write
Tool/ToolRevision write
audit write
operation-receipt write
```

Provider-specific Test result/diagnostic state is transient and must not become part of the persisted Tool definition.

For persisted DRAFTs, changing only Test arguments/shop/Test result must not make the draft persistence-dirty.

### R9 — preserve COMMERCE-080 as the only External live-Test backend

Do not modify or duplicate:

```text
src/commerce/tool-authoring/external-live-test.ts
```

unless a concrete integration defect in the accepted C080 API is proven. If such a defect is found, stop and return the issue to `moda_architect`; do not silently redesign C080 inside this UI task.

Do not create another renderer, another Test result shape or another provider observation path.


### R6 — drive the C078 common Test checkpoint

For the new-Tool session, C081 MUST consume the C078 common Test freshness model rather than maintain a second canonical candidate-pass checkpoint.

On Test start:

```text
submittedSnapshot = currentAuthoringSnapshot(session)
session = startAuthoringTest(session).session
```

The exact submitted snapshot must be retained with the in-flight request.

On C080 success, call the C078 completion operation with `PASSED`. On C080 failure, call it with `FAILED`.

If any Tool Definition, Request, Response or Result Template revision changed while the request was in flight, the completion must resolve to:

```text
status = STALE
testedSnapshot = null
```

and the returned provider result must not mark the current candidate passed.

Provider-specific safe result/diagnostic state may remain local to the External Test UI. Do not copy provider result payloads into the C078 common `test` state.

Use `isCurrentTestPassed(session)` wherever new-Tool UI logic needs to decide whether the current candidate has a current successful Test checkpoint.

## Work Items

- [x] Consume C078/C079 common authoring Test state; do not create a competing authoritative Test store.
- [x] Pass the exact assembled current External definition to `testExternalHttpCandidateAction`.
- [x] Gate Test execution on current VALID Tool Definition, Request, Response and Result Template sections.
- [x] Capture the current authoring snapshot and provider-local run identity before every backend invocation.
- [x] Drive common RUNNING/PASSED/FAILED/STALE transitions exactly as defined above.
- [x] Stale common Test state on Test-argument or selected-shop changes.
- [x] Preserve stale-response/concurrent-run protection.
- [x] Render `Result shown to agent` first from server `renderedText`.
- [x] Keep safe stage/request/provider/processed-result diagnostics secondary.
- [x] Add current Test PASSED to new External Create eligibility.
- [x] Add current Test PASSED to persisted External Save eligibility without changing C079 persistence-dirty/CAS semantics.
- [x] Prove Test state/arguments/output remain non-durable and do not make a persisted draft dirty.
- [x] Remove every External Test instruction that points to Agent Contract.
- [x] Add all required regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-078
  canonical authored-section validation ledger
  common AuthoringTestState / snapshot semantics
  current new-Tool assembled candidate
  current new-Tool Save eligibility

ARCH-021-COMMERCE-079
  persisted authoring-session parity
  persisted assembled candidate
  persistence-dirty/CAS Save eligibility

ARCH-021-COMMERCE-080
  testExternalHttpCandidateAction
  ExternalHttpLiveTestInput
  ExternalHttpLiveTestResult
  server-produced renderedText
```

No new database, Shared, queue or cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-078
- ARCH-021-COMMERCE-079
- ARCH-021-COMMERCE-080

## Enables

- ARCH-021-COMMERCE-083
- ARCH-021-SYSTEM-TEST-002

## Acceptance Criteria

- [x] No second authoritative External Test/dirty/validated state is created outside the C078/C079 authoring session.
- [x] Test cannot invoke the backend while any of Tool Definition, Request, Response or Result Template is not current VALID.
- [x] External Test sends the exact current assembled Tool definition, arguments and nullable shopId to `testExternalHttpCandidateAction`.
- [x] Test start captures the current section-revision snapshot and marks the common Test RUNNING.
- [x] Only a backend result with every C080 stage passed and server `renderedText` present may mark the current Test PASSED.
- [x] Backend/action failure marks the current matching Test FAILED.
- [x] An edit/argument/shop change during an in-flight Test prevents the late response from changing current Test readiness.
- [x] Tool Definition/Request/Response/Result Template changes stale Test through the common session model.
- [x] Test-argument and selected-shop changes also stale Test and clear the displayed prior result.
- [x] Successful Test displays server `renderedText` first under `Result shown to agent`.
- [x] Existing safe Request/provider/processed-result/stage diagnostics remain available after the primary result.
- [x] New External Create is disabled unless the common Test is PASSED for the exact current snapshot.
- [x] Persisted External Save is disabled unless C079 Save eligibility is satisfied and the common Test is PASSED for the exact current snapshot.
- [x] Review remains navigable while Test is NOT_RUN/RUNNING/FAILED/STALE.
- [x] Test actions/results do not create/save Tool state, publication proof, audit/receipt state or persisted-draft dirtiness.
- [x] Shopify Create/Save gating is unchanged by this task.

## Validation

- [x] `npx vitest run tests/external-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/external-http-live-test-action.test.ts`
- [x] New Tool: all four sections current VALID + Test NOT_RUN -> Create disabled.
- [x] New Tool: current successful External Test -> Create enabled when all other C078 gates pass.
- [x] New Tool: edit Result Template after PASS -> common Test STALE -> Create disabled.
- [x] New Tool: edit Tool Definition after PASS -> common Test STALE -> Create disabled.
- [x] Persisted DRAFT: C079 persistence-dirty/current-valid + Test NOT_RUN -> Save disabled.
- [x] Persisted DRAFT: same state + current PASS -> Save enabled.
- [x] Persisted DRAFT: changing only Test arguments/shop does not set persistence-dirty but does stale Test/disable Save.
- [x] Start run at snapshot N, edit Request before completion, resolve old successful response -> Test remains STALE and Create/Save remains disabled.
- [x] Start run N, then run N+1; late N response cannot overwrite N+1 result/checkpoint.
- [x] Backend `kind: ok` with any failed C080 stage -> common Test FAILED, never PASSED.
- [x] Successful result renders `Result shown to agent` before diagnostics and displays server `renderedText` exactly.
- [x] Invalid/stale prerequisite messages point only to Tool Definition, Request, Response or Result Template as defined.
- [x] Focused zero-write assertion proves Test invokes no create/save/publication mutation.
- [x] Targeted ESLint for changed files.
- [x] Changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation.
- [x] `git diff --check`.

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin COMMERCE-083 or any adjacent task.

## Implementation Notes

The common authoring session is the authority for Test freshness and Save eligibility. `ExternalHttpTestTab` may retain local safe diagnostic/result presentation state, but a local `submission`, identity key or `testPassed` boolean must never become a second persistence-readiness authority.

The uploaded 2026-09-28 snapshot already contains the accepted COMMERCE-080 backend implementation in `src/commerce/tool-authoring/external-live-test.ts`; consume it rather than replacing it.

## Completion Report

### Status

Ready for architect review (Attempt 2; status: `review`).

### Files Changed

In `moda-interact-commerce`:

- `src/studio/external-http/editor.tsx`
- `src/studio/external-http/request-tab.tsx`
- `src/studio/external-http/test-tab.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`

Attempt 2 changed only `src/studio/external-http/test-tab.tsx` and `tests/external-tools-ui.test.tsx`.

### Work Completed

Consumed the accepted C078/C079 common authoring Test snapshot and lifecycle for new and persisted External authoring. Test now uses the exact assembled candidate, requires current authored validations, enforces bounded object arguments, and accepts PASS only when every C080 stage passed and server `renderedText` is present. The server-rendered text is shown first; safe diagnostics remain secondary.

Attempt 2 addresses the architect-requested transient identity race. Test arguments and selected-shop changes now advance a monotonic provider-local generation, synchronously clear the displayed submission and stale the common checkpoint. The generation is captured in each run identity and checked before completion can update provider display state, so changing arguments/shop away and back cannot revive a pending or completed result. The common persisted authoring revision ledger remains unchanged; transient values stay non-durable.

Added argument A-to-B-to-A tests for pending and already-displayed results, a selected-shop A-to-B-to-A pending-result test, and persisted-DRAFT assertions proving transient changes cause no Tool/publication writes and a fresh Test restores Save eligibility. Existing run-N/run-N+1 protection remains intact. No C080 backend, database, Shopify gate, or unrelated task file was changed.

### Validation Results

- `npx vitest run tests/external-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/external-http-live-test-action.test.ts`: 3 files passed, 124 tests passed.
- Targeted ESLint on the two Attempt 2 files: passed with no output or warnings.
- Changed-file diagnostics across all eight C081 implementation/test files: no errors found.
- `git diff --check`: passed.
- Attempt 1's repository TypeScript check reported two Result Template prop-union diagnostics in `src/studio/tools/tool-editor.tsx`; that file was unchanged in Attempt 2. The Attempt 2 changed-file diagnostics are clean. A full repository typecheck was not rerun for Attempt 2.
- Launcher verified recursive submodule synchronization/update passed and database is initialized at `0a8d3b9feade69690b6c1e33aeda051ea588bd45` (`database`, `heads/main`).

### Deviations

Attempt 2 implements the required correction from the Architect Review without changing the task's scope or API.

### Assumptions

No new assumptions. The Attempt 1 broad typecheck findings are retained as context; Attempt 2's changed-file diagnostics are clean.

### Unresolved Issues

The last full repository typecheck (Attempt 1) reported two Result Template prop-union diagnostics in `tool-editor.tsx`; Attempt 2 did not change that file or rerun the full typecheck. No errors were reported for any C081 changed file in the Attempt 2 diagnostics pass.

### Architectural Concerns

C081 consumes the canonical C078/C079 checkpoint and C080 action/rendered output; no competing authoritative Test state or backend was introduced.

### Git / Worktree Evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-081`, branch `task/ARCH-021-COMMERCE-081`.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-081`, branch `task/ARCH-021-COMMERCE-081`; Attempt 2 launcher claim commit `6e8ca5e33dceea41deab74dd98b1d880d9616d1a` (pushed).
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-081`, branch `task/ARCH-021-COMMERCE-081`.
- Parent synchronization: remote task branch fast-forwarded `not-needed`; `origin/main` incorporated `already-current`.
- Implementation synchronization: remote task branch fast-forwarded `not-needed`; `origin/main` incorporated `already-current`.
- Both physical worktrees were dedicated to C081; the canonical shared workspace and shared implementation source checkout were not switched or mutated; no other task worktree was reused.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; database commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45` (initialized).
- Attempt 1 implementation commit `52e09a27a0d81189757870fd584144f4a2f8d51c` and Attempt 2 correction commit `64a7709` are pushed to `task/ARCH-021-COMMERCE-081` in `moda-interact-commerce`.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is accepted.

The sole Attempt 1 correction is satisfied. External Test now uses a monotonic provider-local transient generation in addition to the common C078/C079 authored-section snapshot.

The implementation guarantees:

- every Test-arguments mutation invalidates the current provider-local generation;
- every selected-shop change invalidates the current provider-local generation;
- the exact generation is captured at Test start;
- provider-local displayed submission/result state is cleared immediately on transient mutation;
- a completion is accepted for display only when the submitted generation is still current;
- argument A -> B -> A cannot resurrect an in-flight or already-displayed A result;
- shop A -> B -> A cannot resurrect an in-flight A result;
- stale completions cannot repopulate stage, request, provider or processed-result diagnostics;
- the common C078/C079 checkpoint remains authoritative for persistence readiness;
- transient Test arguments/shop/result state remains non-durable and does not make a persisted DRAFT persistence-dirty;
- a fresh successful Test after staleness restores External Save/Create eligibility when all other existing gates are satisfied; and
- existing run-N/run-N+1 protection remains intact.

The correction does not add Test arguments or shop identity to the persisted four-revision authoring ledger. The monotonic generation is provider-local/transient only, as required.

The rest of the C081 architecture remains conformant: C080 is still the only External live-Test backend; the exact assembled candidate is submitted; Tool Definition/Request/Response/Result Template validation gates Test; server `renderedText` is the primary success surface; diagnostics remain secondary and bounded; and new External Create plus persisted External Save require `isCurrentTestPassed(...)`.

The submitted task snapshot still contains `executor: copilot` and a non-null `claimed_at` despite the handoff reporting a cleared claim. This acceptance overlay normalizes both fields to `null`; it is not an implementation defect.

### Reviewed Files

- `src/studio/external-http/test-tab.tsx`
- `src/studio/external-http/editor.tsx`
- `src/studio/external-http/request-tab.tsx`
- `src/studio/tools/new-tool-authoring-state.ts`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/external-http-live-test-action.test.ts`
- C081 Completion Report — Attempt 2

### Validation Reviewed

- Submitted focused packet: 3 files, 124 tests passed.
- Submitted targeted ESLint for Attempt 2 files: passed.
- Submitted changed-file diagnostics across all eight C081 implementation/test files: clean.
- Submitted `git diff --check`: passed.
- Full repository typecheck was not rerun in Attempt 2. Attempt 1 recorded only the two known Result Template prop-union diagnostics in `tool-editor.tsx`; Attempt 2 did not modify that file and its changed-file diagnostics are clean.
- Review source inspection confirms the monotonic transient generation is provider-local only and no C080 backend, database, Shopify gate or persistence contract was changed.
- Focused regressions cover in-flight argument A -> B -> A, already-displayed argument A -> B -> A, selected-shop A -> B -> A, persisted zero-write behavior and fresh-Test Save restoration.

### Architecture Conformance

Conforms.

C081 now cleanly composes the C078/C079 common Test checkpoint with the C080 External provider backend and adds only provider-local non-durable result identity/presentation state. Persistence readiness remains owned by the common checkpoint, and transient Test context cannot resurrect stale provider results.

### Follow-up

C081 is Complete / Accepted — Attempt 2.

COMMERCE-083 becomes Ready because C078, C079, C081 and C082 are Complete.

ARCH-021-SYSTEM-TEST-002 remains Pending until COMMERCE-083 is Complete.
