---
id: ARCH-021-COMMERCE-054
architecture_id: ARCH-021
title: Execute the non-durable External HTTP candidate live
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 69
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-051
enables:
  - ARCH-021-COMMERCE-055
created: 2026-09-27
updated: 2026-09-27
---

# Execute the non-durable External HTTP candidate live

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add one backend-only Commerce Studio live-Test capability that executes the exact current **non-durable** External HTTP Request + Response candidate against the selected real provider, applies the canonical authored response processing and result contract, and returns bounded stage-by-stage diagnostics without creating or modifying any durable Tool state.

## Context

The authoring flow before durable creation is:

```text
Request
  author + validate request locally/server-authoritatively

Response
  author + validate response processing locally/server-authoritatively

Test
  execute those exact current definitions together against the real provider

later final Create
  first durable Tool + revision write
```

At Test time there is deliberately no saved Tool revision to bind to.

COMMERCE-040..050 already established and accepted the Request/Response contracts. They are baseline capabilities, not dependencies for this task. COMMERCE-051 owns the reusable secure provider-observation boundary: ADMIN/PER_SHOP authorization, immutable Connection resolution, server-only credentials, DNS/public-address enforcement, TLS verification, GET-only transport, redirects/deadlines/body bounds and response-format decoding.

This task composes those accepted contracts into a live Test backend only. COMMERCE-055 owns the React Test UI.

## Scope

Primary implementation files are expected to include:

```text
moda-interact-commerce/src/commerce/integration/external/index.ts
moda-interact-commerce/src/commerce/tool-authoring/external-live-test.ts
moda-interact-commerce/src/commerce/tool-authoring/contracts.ts
moda-interact-commerce/src/studio/tools/external-validation-server-actions.ts

moda-interact-commerce/tests/external-tool-authoring-server-actions.test.ts
moda-interact-commerce/tests/external-http-executor.test.ts
moda-interact-commerce/tests/response-processing.test.ts
moda-interact-commerce/tests/code-response-processor.test.ts
```

Equivalent repository-local locations are acceptable when they preserve ownership.

## Out of Scope

- Test-tab React presentation; COMMERCE-055 owns it.
- Synthetic/sample-provider response fixtures as a product Test mode.
- Response authoring or Automatic generation.
- Request/Response contract redesign.
- Persisting `CommerceTool`, `CommerceToolRevision`, authoring state or Test state.
- Audit writes.
- Publication/live-test receipts or satisfying `LIVE_TEST_REQUIRED`.
- Saved-revision lookup or requiring `toolId`/`toolRevisionId`.
- Publish behaviour.
- Phase 2 tab gating.
- Database/Prisma/Shared/Gateway changes.
- Enabling production JavaScript Request execution beyond the accepted authoring observation path.

## Requirements

### R1 — accept the exact current local candidate

Expose one authorized live-Test operation equivalent to:

```ts
type ExternalHttpLiveTestInput = {
  connectionRevisionId: string;
  inputSchema: unknown;
  request: unknown;
  responseFormat: unknown;
  acceptedMediaTypes: unknown;
  resultPath: unknown;
  responseProcessing: unknown;
  resultSchema: unknown;
  arguments: unknown;
  shopId: string | null;
};
```

Equivalent use of an existing canonical `ExternalHttpExecution` candidate is preferred when it avoids duplicating the contract.

The operation MUST NOT require or accept as authority:

```text
toolId
toolRevisionId
saved revision number
published release identity
```

The browser supplies the current candidate; the server reparses/revalidates it through existing canonical Commerce contracts before execution.

### R2 — preserve Studio authorization and Connection scope

Require the existing platform staff authoring role and selected-shop authorization.

For `PER_SHOP` Connections, revalidate the supplied shop through the accepted Studio shop-execution/inspection boundary before credential resolution.

For `PLATFORM` Connections, preserve the existing platform credential scope.

Never trust browser-supplied origin, credential material, resolved IP or absolute destination URL.

### R3 — reuse COMMERCE-051 for the real provider request

Provider execution MUST compose the accepted COMMERCE-051 observation boundary rather than creating a second DNS/TLS/credential/HTTP stack.

Equivalent flow:

```text
current inputSchema + request + test arguments
        |
        v
accepted Request construction
        |
        v
COMMERCE-051 secure provider observation
        |
        v
bounded provider response
```

Declarative and JavaScript Request candidates use their already-accepted semantics.

### R4 — process the actual observed response with the canonical Response contract

For a 2xx provider response, execute the exact current authored Response candidate.

For:

```text
DIRECT
VISUAL
```

use the existing result-path semantics and canonical response processor.

For:

```text
JAVASCRIPT
```

pass the complete bounded `TransformResponse` to the existing JavaScript response processor.

Do not implement Test-specific projection, filtering, sorting, schema or JavaScript transformation logic.

### R5 — validate the actual processed result contract

After successful response processing, compile and validate through the same Commerce result-schema authority used by runtime/publication:

```text
compileCommerceResultSchema(...)
```

Keep these outcomes distinct:

```text
provider request succeeded/failed
response processing succeeded/failed/not-run
result validation succeeded/failed/not-run
```

A result-contract mismatch is not a network/provider failure.

### R6 — return explicit execution stages

Return deterministic stages covering:

```text
Request construction
Connection resolution
Provider request
Response processing
Result validation
```

Each stage must be represented as one of:

```text
passed
failed
not-run
```

with a stable bounded code/message when failed.

If an earlier stage fails, later stages are `not-run`; do not invent cascading failures.

### R7 — non-2xx provider responses stop normal processing

A decodable 4xx/429/5xx observation remains visible as the provider outcome, but normal Tool response processing and result validation do not run.

Equivalent:

```text
Provider request: failed (HTTP 401/404/429/503 ...)
Response processing: not-run
Result validation: not-run
```

Preserve the bounded observed response body/content type supplied by COMMERCE-051 where safe.

### R8 — bounded live-Test result contract

Return a safe contract equivalent to:

```ts
type ExternalHttpLiveTestResult = {
  stages: {
    requestConstruction: LiveTestStageResult;
    connectionResolution: LiveTestStageResult;
    providerRequest: LiveTestStageResult;
    responseProcessing: LiveTestStageResult;
    resultValidation: LiveTestStageResult;
  };
  request?: {
    method: "GET";
    url: string;
    authentication: "NONE" | "CONFIGURED";
    headers: Record<string, string>;
  };
  provider?: {
    status: number;
    contentType: string;
    bodyText: string;
    json: unknown | null;
  };
  processedResult?: unknown;
  contractIssues?: Array<{ path: string; message: string }>;
};
```

Equivalent naming is acceptable.

Never return:

```text
resolved credential values
provider response headers
server stack traces
raw internal/QuickJS exception text
unbounded provider bodies
```

### R9 — zero durable writes is a hard invariant

Successful and failed live Test execution MUST NOT create or modify:

```text
CommerceTool
CommerceToolRevision
audit events
publication/live-test receipts
publication proof
Connection/Credential state
```

Do not call Save, Create, Publish or receipt-recording paths.

No database write is justified merely because Test succeeded.

### R10 — no saved-revision reconciliation

Do not compare the candidate with a saved revision, bind success to a revision/content hash, or attempt to satisfy publication proof.

At this stage the tested definition is intentionally non-durable. Publication-proof semantics belong to a later post-creation workflow if required.

### R11 — no synthetic Test mode

This backend represents one product operation:

```text
execute the current local Tool candidate against the real selected provider
```

Do not expose or create a synthetic provider-response branch for Studio Test.

### R12 — no tab gating

Backend Test failures are diagnostic only in this phase. Do not add progression/gating semantics to the Test result contract.

## Work Items

- [ ] Define the bounded non-durable live-Test input/result contracts.
- [ ] Reparse/revalidate the current candidate server-side without saved-revision lookup.
- [ ] Compose the real provider call through COMMERCE-051.
- [ ] Apply canonical DIRECT/VISUAL/JavaScript response processing.
- [ ] Validate the processed result through the canonical result-schema compiler.
- [ ] Return the five explicit execution stages with deterministic failure/not-run semantics.
- [ ] Preserve bounded safe Request/provider/result data without credentials/headers/internal errors.
- [ ] Prove successful and failed Test runs perform zero durable writes.
- [ ] Add focused non-2xx, processing, contract and security regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-051
secure credential-redacted live provider observation

accepted canonical External HTTP Request contract
accepted canonical External HTTP Response contract
existing response processors
existing result-schema compiler
```

Produces one Commerce-local Studio live-Test backend contract consumed by COMMERCE-055.

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-051

## Enables

- ARCH-021-COMMERCE-055

## Acceptance Criteria

- [ ] Live Test accepts the exact current non-durable candidate and ephemeral test arguments.
- [ ] No `toolId` or `toolRevisionId` is required.
- [ ] Server-side candidate validation occurs before unsafe execution.
- [ ] Real provider I/O is performed only through COMMERCE-051.
- [ ] DIRECT/VISUAL use canonical response processing.
- [ ] JAVASCRIPT uses the canonical bounded code response processor.
- [ ] Actual processed output is checked by the canonical result contract.
- [ ] Five deterministic stages report passed/failed/not-run correctly.
- [ ] Non-2xx provider outcomes remain visible and downstream processing is not run.
- [ ] Credential values/provider response headers/raw internal errors never enter the result.
- [ ] No synthetic Test mode is introduced.
- [ ] Successful and failed Test runs perform zero durable writes.
- [ ] No saved-revision lookup, receipt, publication proof or `LIVE_TEST_REQUIRED` satisfaction is introduced.
- [ ] No Request/Response redesign or tab gating is introduced.

## Mandatory Regression Scenarios

Prove at minimum:

```text
1. malformed test arguments fail Request construction before provider I/O.
2. invalid current Request fails before credential/provider I/O.
3. PER_SHOP Connection without an authorized selected shop performs no provider call.
4. Declarative Request + 200 + DIRECT + valid contract -> all stages passed.
5. JavaScript Request reaches provider through C051 without enabling production JS execution.
6. 200 + nested VISUAL result -> canonical processed result + valid contract.
7. 200 + JAVASCRIPT Response -> canonical code processor + valid contract.
8. response-processing failure -> provider visible, processing failed, validation not-run.
9. result-schema mismatch -> processed value visible, result validation failed.
10. 401/404/429/503 -> provider failed, processing/validation not-run.
11. provider deadline/network/security rejection -> bounded provider-stage failure.
12. no resolved credential or provider response headers returned.
13. successful run causes zero Tool/Revision/audit/receipt writes.
14. failed run causes zero Tool/Revision/audit/receipt writes.
15. no saved-revision identifier is required or consulted.
```

## Validation

Run at minimum the focused suites declared by the repository for:

- [ ] External HTTP authoring Server Actions/live observation
- [ ] External HTTP executor/security where shared composition changes
- [ ] canonical response processing
- [ ] JavaScript response processing
- [ ] result-schema validation
- [ ] focused new non-durable live-Test backend tests
- [ ] targeted ESLint on changed files
- [ ] changed-file TypeScript diagnostics contain no task-owned error
- [ ] `git diff --check`

Inspect the repository `package.json` before choosing exact script names; do not invent scripts.

## Stop Condition

After the backend can execute the exact non-durable candidate end-to-end, return bounded stage diagnostics, prove zero durable writes and pass required validation, set this task to `review`, complete the Completion Report and STOP. Do not implement COMMERCE-055 UI.

## Implementation Notes

The architectural invariant is:

```text
Request  = define + validate request
Response = define + validate response
Test     = execute those definitions together against reality
Create   = first durable write, later
```

If implementation requires persistence merely to run Test, stop and return the conflict to `moda_architect`.

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
