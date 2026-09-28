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
status: ready
priority: 75
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-078
  - ARCH-021-COMMERCE-080
enables:
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

Wire the complete new-Tool candidate into External Test and make the populated Result Template (`renderedText`) the primary success output, with Request/provider/processed-result details retained as secondary diagnostics.

## Context

COMMERCE-080 adds backend rendering. The current `ExternalHttpTestTab` identifies staleness from Request/Response/inputSchema/arguments/shop only and presents stage/request/provider/processed result, but not what the agent receives. It also still tells users to return to Agent Contract for invalid input schema.

The agreed flow places Result Template before Test, so Test must invalidate when the template changes and answer the user's primary question: **what will the agent receive?**

## Scope

Primary implementation:

```text
src/studio/external-http/editor.tsx
src/studio/external-http/test-tab.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/tools/external-validation-server-actions.ts   # consume changed action contract
```

Tests:

```text
tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
tests/external-http-live-test-action.test.ts
```


## Out of Scope

- Backend execution/rendering semantics (C080).
- Shopify Test UI (C083).
- Publication proof.
- Persisting Test output.
- Changing Request/Response/Result Template authoring.

## Requirements

### R1 — Test receives the exact current complete candidate

The Test call must be built from the same assembled definition that Review/Save would use at that moment, including:

```text
Tool Definition identity/version/description
Request-owned inputSchema
current External execution/request
current Response/resultSchema
current responseTemplate
```

Do not reconstruct a second partial definition in `ExternalHttpTestTab`.

### R2 — local preflight points to owning tabs

Before calling the Server Action:

- invalid Request -> tell user to return to Request;
- invalid Response/result contract -> return to Response;
- invalid Result Template -> return to Result Template;
- invalid input schema wording -> return to Request, never Agent Contract;
- invalid test arguments -> remain on Test with the bounded JSON error.

### R3 — rendered agent result is the primary success surface

On a successful live Test, render first:

```text
<section aria-label="Result shown to agent">
  <h4>Result shown to agent</h4>
  <pre>...renderedText...</pre>
</section>
```

The text must be exactly `renderedText` returned by C080; the browser must not render/interpolate the template itself.

After that surface, preserve stage status and safe diagnostics for:

```text
Request sent
Provider response
Processed Tool result
```

These may remain visible or be placed under `<details>`, but they must be visually/DOM-secondary to the agent result.

### R4 — stale identity includes the whole renderable candidate

A prior Test result must be marked stale/cleared when any of these changes:

```text
Tool Definition fields used by definition
inputSchema
External Request/execution
Response/resultSchema
responseTemplate
Test arguments
selected shop
```

Changing only tab selection must not make a Test stale.

### R5 — no persistence side effect

Running Test, viewing output or changing Test arguments performs zero Tool/draft/publication write.


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

- [ ] Pass one assembled complete candidate to the External live-Test action.
- [ ] Add Result Template validity to local preflight.
- [ ] Remove every Test instruction that points to Agent Contract for input-schema fixes.
- [ ] Render `Result shown to agent` first on success from server `renderedText`.
- [ ] Keep existing safe stage/request/provider/processed-result diagnostics after the primary output.
- [ ] Include Tool Definition/input schema/template in stale-test identity.
- [ ] Preserve concurrent-run/stale-response protection.
- [ ] Drive C078 `startAuthoringTest` / `completeAuthoringTest` and use `isCurrentTestPassed` as the common new-Tool Test checkpoint.
- [ ] Add UI regressions for output order, template staleness and zero writes.

## Interfaces / Contracts

Consumes the C078 assembled authoring candidate, C078 common Test checkpoint/freshness operations and C080 live-Test result/action contract. No new persistent or cross-repository contract.

## Dependencies

- ARCH-021-COMMERCE-078
- ARCH-021-COMMERCE-080

## Enables

- ARCH-021-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] External Test sends the exact current complete candidate.
- [ ] Invalid input schema directs the user to Request, not Agent Contract.
- [ ] Invalid template directs the user to Result Template without provider I/O.
- [ ] Successful Test displays `Result shown to agent` before diagnostics.
- [ ] Displayed agent text equals server-returned canonical `renderedText` exactly.
- [ ] Template/definition/request/response/argument/shop changes stale prior results deterministically.
- [ ] Existing safe Request/provider/processed-result diagnostics remain available.
- [ ] Test remains non-durable.
- [ ] New-Tool Test state transitions through the C078 common checkpoint; stale in-flight completions cannot mark the current candidate passed.

## Validation

- [ ] `npx vitest run tests/external-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/external-http-live-test-action.test.ts`
- [ ] focused rendered-result DOM-order assertion
- [ ] focused stale-on-template-change assertion
- [ ] focused zero-write assertion
- [ ] focused C078 RUNNING/PASSED/FAILED/STALE checkpoint integration assertions
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Do not render template tokens in React. The browser displays the canonical server-produced renderer output so Test and production cannot drift.

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
