---
id: ARCH-021-COMMERCE-054
architecture_id: ARCH-021
title: Implement External HTTP live Test tab
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 69
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-051
  - ARCH-021-COMMERCE-053
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Implement External HTTP live Test tab

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the External HTTP Test-tab placeholder with one live execution/observation surface that runs the **current unsaved Tool authoring candidate** using the shared Sample Tool arguments, shows the safe Request, bounded provider response, processed Tool result and result-contract outcome, and contains **no response-authoring controls**.

## Context

The current Test tab says live provider testing is not implemented.

The agreed ownership model is now:

```text
Request
  authors + validates + previews request construction

Response
  authors + validates response processing
  Automatic may generate Visual rules, then hands editing to Visual

Test
  executes and observes the already-authored current candidate
```

Therefore Test must not become a duplicate Response editor.

COMMERCE-051 owns live provider observation/security.

COMMERCE-053 owns the one shared Sample Tool arguments state and Automatic/Visual handoff.

COMMERCE-048/049 own recursive Visual processing; the existing `createResponseProcessor(...)` is the production Visual/Direct processing authority.

The existing JavaScript response processor remains the JavaScript execution authority.

## Scope

Primary files are expected to include:

```text
moda-interact-commerce/src/commerce/integration/external/index.ts
moda-interact-commerce/src/commerce/tool-authoring/external-live-test.ts         # optional dedicated composition module
moda-interact-commerce/src/studio/tools/external-validation-server-actions.ts
moda-interact-commerce/src/studio/external-http/editor.tsx
moda-interact-commerce/src/studio/external-http/test-tab.tsx
moda-interact-commerce/src/studio/tools/new-tool-editor.tsx
moda-interact-commerce/src/studio/tools/tool-editor.tsx
moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/external-tool-authoring-server-actions.test.ts
```

Reuse existing processors/security rather than copying implementation into Test.

## Out of Scope

- Editing Response structure in Test.
- Source-path controls in Test.
- Visual field/tree controls in Test.
- Result/item type controls in Test.
- Visual filters/sort/limit controls in Test.
- Result-schema editor in Test.
- JavaScript response editor in Test.
- Automatic generation controls in Test.
- Synthetic fixture/sample-response testing UI.
- Model/prompt/agent conversational preview.
- Persisting a live-test receipt or satisfying `LIVE_TEST_REQUIRED`.
- Database/Shared changes.
- Production JavaScript Request enablement.

## Requirements

### R1 — one shared Sample Tool arguments value

Use the exact shared Sample Tool arguments text/state established by COMMERCE-053.

Test must not maintain its own independent arguments copy.

Test may edit the shared value. Changing it invalidates the previous Test result but does not dirty/persist the Tool definition.

### R2 — exact current authoring candidate

`Run tool` uses the current authoring state:

```text
connectionRevisionId
current active Request
current responseFormat
current resultPath
current responseProcessing
current resultSchema
current inputSchema
shared sample Tool arguments
selected shop context
```

It works for:

```text
new unsaved Tool authoring
existing persisted DRAFT authoring with unsaved edits
```

Do not reload the last saved ToolRevision and ignore visible unsaved changes.

The current candidate must be canonical enough to run. If Request/Response local state is currently invalid and has not been promoted to canonical execution, Test must report that the visible configuration needs correction rather than silently testing an older candidate.

### R3 — compose, do not duplicate, live observation

Server-side Test execution must call the COMMERCE-051 provider-observation capability.

Do not add a second DNS/TLS/credential/HTTP implementation for Test.

Equivalent composition:

```text
current request + args + connection/shop + response format
        |
        v
COMMERCE-051 live observation
        |
        +-- failure -> bounded Test failure
        |
        v
bounded TransformResponse
```

### R4 — process the observed response with canonical processors

For a successfully observed provider response, Test uses the current authored Response exactly.

For:

```text
DIRECT
VISUAL
```

select `execution.resultPath` from `observation.response.json` using the same safe result-path semantics as production, then call the existing:

```text
createResponseProcessor(...)
```

For:

```text
JAVASCRIPT
```

pass the **complete bounded `TransformResponse`** to the existing JavaScript response processor:

```text
createCodeResponseProcessor(...)
```

Do not add a Test-specific response transformer.

### R5 — result-contract validation

After response processing succeeds, validate the processed values with the same Commerce result-schema compiler used by production:

```text
compileCommerceResultSchema(execution.resultSchema)
```

Test must distinguish:

```text
provider observation succeeded
response processing succeeded/failed
result contract succeeded/failed
```

Do not turn a result-schema mismatch into a provider/network failure.

### R6 — non-2xx response behavior

COMMERCE-051 may return an observed provider 4xx/429/5xx response.

Test must show that provider status/body observation and must **not** run normal Tool response processing for non-2xx status in this task.

Render a bounded state equivalent to:

```text
Provider responded with HTTP <status>.
Processed Tool result: not run.
```

This keeps live Test truthful while preserving the production executor's existing non-2xx semantics.

### R7 — exact Test result contract

Use one bounded Server Action result equivalent to:

```ts
type ExternalHttpLiveTestResult = {
  request: {
    method: "GET";
    url: string;
    authentication: "NONE" | "CONFIGURED";
    headers: Record<string, string>; // authored safe headers only; no resolved credential
  };
  provider: {
    status: number;
    contentType: string;
    bodyText: string;
    json: unknown | null;
  };
  processed:
    | { kind: "ok"; values: unknown }
    | { kind: "not-run"; reason: string }
    | { kind: "error"; code: string };
  contract:
    | { kind: "valid" }
    | { kind: "invalid"; issues: Array<{ path: string; message: string }> }
    | { kind: "not-run" };
};
```

Equivalent naming is acceptable.

Do not include:

```text
resolved credential values
provider response headers
server stack traces
raw QuickJS/internal runtime exception text
```

### R8 — Test UI content

Render one Test panel containing at minimum:

```text
Sample Tool arguments
[ Run tool ]

Request
  method + safe URL
  authentication: not configured | configured/redacted
  authored safe headers

Provider response
  HTTP status
  content type
  bounded body/JSON presentation

Processed Tool result
  bounded JSON presentation or processing failure/not-run

Result contract
  Valid | Invalid | Not run
  actionable issues when invalid
```

Long JSON/body output must be presented in a bounded/scrollable `<pre>`-style surface; do not create editable textareas for response/result display.

### R9 — absolutely no Response authoring duplication

Test MUST NOT render controls for:

```text
Source path
Response processing mode
Visual output name
Visual source path
Visual node type
Result type
Item type
Filters
Sort
Limit
Omit if missing
Processed result schema
JavaScript response source
Automatic generation/candidate selection
```

If the author wants to change any of those, the UI directs them to **Response**.

### R10 — no synthetic Test mode

Do not expose the historical `ExternalFixture` / synthetic sample fixture machinery in the Test tab.

The existing internal fixture helpers may remain for repository tests/other accepted uses, but this Test-tab product flow has exactly one meaning:

```text
Run the current Tool candidate against the real selected External provider.
```

### R11 — staleness

Invalidate the displayed Test result whenever any Test-affecting authoring state changes, including:

```text
sample arguments
Connection revision
Request
responseFormat
resultPath
responseProcessing
resultSchema
selected shop
```

Do not leave a previous successful Test displayed as if it represented newer unsaved edits.

### R12 — pending/concurrency behavior

While `Run tool` is pending:

```text
disable another Run tool submission
keep authoring tabs navigable
show bounded progress status
```

If the author edits the candidate before an earlier Test promise resolves, the stale result must not replace the result for the newer current candidate. Use a deterministic request/key/revision identity in UI state rather than assuming completion order.

### R13 — actionable failures follow C050 principles

Present failures by category with safe corrective guidance.

At minimum distinguish:

```text
invalid sample arguments
current Request invalid
current Response invalid
shop required
Connection unavailable
provider unavailable
provider deadline
non-2xx provider response
response processing invalid
result contract invalid
validation/Test service unavailable
forbidden
```

Stable technical codes may be secondary. Raw server/provider/QuickJS messages are not primary user text.

### R14 — no persistence / no publication receipt

`Run tool` is non-mutating with respect to authored Tool state.

It does not:

```text
Save Draft
Create Tool
Publish
write ToolRevision
write live-test publication receipt
satisfy LIVE_TEST_REQUIRED
```

A later architecture/task must explicitly bind a successful live test to an exact saved revision/content hash before the publication gate can be satisfied.

## Work Items

- [ ] Add one server-side current-draft External HTTP Test composition over COMMERCE-051.
- [ ] Process DIRECT/VISUAL through existing `createResponseProcessor(...)`.
- [ ] Process JAVASCRIPT through existing code response processor.
- [ ] Validate processed output through `compileCommerceResultSchema(...)`.
- [ ] Add bounded Test action result contract with no secrets/response headers.
- [ ] Replace Test placeholder with execution/observation UI.
- [ ] Reuse COMMERCE-053 shared Sample Tool arguments.
- [ ] Add Test-result staleness and stale-promise suppression.
- [ ] Keep Test free of all Response-authoring controls and synthetic fixture modes.
- [ ] Add new/existing Tool regressions and no-write/security evidence.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-051
  secure live provider observation

ARCH-021-COMMERCE-053
  shared Sample Tool arguments + current authoring composition

existing createResponseProcessor(...)
existing JavaScript response processor
existing compileCommerceResultSchema(...)
```

Produces:

```text
one Commerce Studio live External HTTP Test result contract/UI
```

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-051
- ARCH-021-COMMERCE-053

## Enables

None.

## Acceptance Criteria

- [ ] Test runs the exact current unsaved External HTTP authoring candidate.
- [ ] New unsaved and existing DRAFT Tool flows both work.
- [ ] Test shares Sample Tool arguments with Request/Automatic and has no independent copy.
- [ ] Test reuses COMMERCE-051; no second live HTTP/security stack exists.
- [ ] DIRECT/VISUAL use the canonical response processor.
- [ ] JAVASCRIPT uses the canonical code response processor with full bounded TransformResponse.
- [ ] Processed values are validated through `compileCommerceResultSchema(...)`.
- [ ] Provider non-2xx status is shown and response processing is not run.
- [ ] Request display never contains resolved credential values.
- [ ] Provider response headers are not returned/displayed.
- [ ] Provider body/result display is bounded/read-only.
- [ ] Test has no Source-path/Visual/schema/JavaScript/Automatic authoring controls.
- [ ] No synthetic fixture selector/mode is exposed.
- [ ] Test result becomes stale after every relevant Request/Response/args/shop edit.
- [ ] Stale in-flight completion cannot replace a newer Test state.
- [ ] Actionable failures contain no raw server/provider/internal messages.
- [ ] Run tool performs no Tool/Revision/publish/receipt mutation.
- [ ] Successful Test does not satisfy `LIVE_TEST_REQUIRED`.
- [ ] All tabs remain freely navigable.

## Mandatory Regression Scenarios

Add focused tests proving at least:

```text
1. Test initially renders shared Sample Tool arguments and Run tool.
2. Test does not render any prohibited Response-authoring control.
3. Request-edited sample args appear unchanged in Test.
4. Test-edited sample args appear unchanged in Request/Automatic.
5. malformed sample JSON performs no provider call.
6. current Declarative Request is observed and exact safe URL shown.
7. current JavaScript Request is observed through C051 without enabling production JS execution.
8. PLATFORM auth is shown configured/redacted with no credential value.
9. PER_SHOP missing shop produces actionable no-call result.
10. 200 + DIRECT + valid contract -> processed ok + contract valid.
11. 200 + VISUAL nested LIST/SCALAR_LIST -> canonical processed result + contract valid.
12. 200 + JAVASCRIPT -> full TransformResponse processor path + contract valid.
13. processing failure -> provider response remains visible, processed error, contract not-run.
14. schema mismatch -> processed values remain visible, contract invalid with bounded issues.
15. 404 -> provider visible, processed not-run, contract not-run.
16. 429 -> provider visible, processed not-run.
17. 503 -> provider visible, processed not-run.
18. provider deadline/network failure shows bounded actionable state without raw message.
19. editing Request after success removes/marks Test result stale.
20. editing Response after success removes/marks Test result stale.
21. editing sample args after success removes/marks Test result stale.
22. changing selected shop after success removes/marks Test result stale.
23. run A, edit, run B, A resolves after B -> A cannot replace B/current state.
24. double Run while pending is prevented.
25. new Tool live Test performs no Create/Save.
26. existing DRAFT live Test performs no Save/Publish.
27. no live-test receipt is written.
28. historical synthetic fixture controls do not render in Test.
```

## Validation

Run at minimum:

- [ ] `npm run test:arch020-external-tools-ui`
- [ ] `npm run test:arch021-external-tool-authoring-validation`
- [ ] `npm run test:arch020-response-processing`
- [ ] `npm run test:arch020-code-processor`
- [ ] `npm run test:arch020-external-http` when Test composition touches observation integration
- [ ] focused new live-Test tests
- [ ] targeted ESLint on changed files
- [ ] `git diff --check`
- [ ] changed-file TypeScript diagnostics contain no task-owned error

## Stop Condition

After Test executes/observes the current candidate with canonical processing/result validation, the UI contains no authoring duplication, mandatory regressions pass and the Completion Report is complete, set the task to `review`, clear the execution claim according to the normal workflow, return control to `moda_architect` and STOP. Do not begin system-test work automatically.

## Implementation Notes

The architectural boundary is deliberately strict:

```text
Request  = construct
Response = define result
Test     = execute + observe
```

If implementation pressure suggests adding an editable mapping/schema field to Test, return that issue to `moda_architect` rather than creating a second Response editor.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
