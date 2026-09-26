---
id: ARCH-021-COMMERCE-047
architecture_id: ARCH-021
title: Surface bounded JavaScript compiler diagnostics in Request validation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-046
enables: []
created: 2026-09-26
updated: 2026-09-26
---

# Surface bounded JavaScript compiler diagnostics in Request validation

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Preserve the bounded QuickJS-NG compiler cause for JavaScript Request authoring failures from the sandbox worker through the existing Request validation result so the Request tab shows the actual syntax/entrypoint cause instead of the generic `Request processor did not compile` message.

## Context

Manual validation of the submitted COMMERCE-046 QuickJS-NG/WASI implementation now reaches the sandbox correctly and returns a normal Request authoring validation failure for malformed JavaScript. The current visible result is still generic:

```text
/request/source: Request processor did not compile
```

The useful guest diagnostic is currently discarded at three boundaries:

```text
worker.mjs
  failure(code)
    -> KernelResult contains code + null line/column only

code-request/processor.ts
  mapFailure(...)
    -> diagnostic: { code }

external-validation.ts
  processorDiagnostic(...)
    -> message = "Request processor did not compile"
```

This task preserves one safe, bounded **guest compiler diagnostic** through those existing boundaries. It does not change Request validation semantics, tab state, Create/Save/Publish behavior, the QuickJS engine adapter, or operational error classification.

Expected authored syntax/entrypoint failures remain normal validation results. They are not operational runtime failures and MUST NOT be emitted as shared `error` logs merely because guest JavaScript is invalid.

## Scope

Primary files:

```text
src/commerce/code-runtime/types.ts
src/commerce/code-runtime/worker.mjs
src/commerce/code-request/processor.ts
src/commerce/tool-authoring/external-validation.ts

tests/code-runtime-proof.test.ts
tests/code-request-processor.test.ts
tests/external-tool-authoring-validation.test.ts
tests/external-tool-authoring-server-actions.test.ts
tests/external-tools-ui.test.tsx
```

Change additional directly affected Request-validation test fixtures only when required by the same bounded diagnostic propagation.

## Out of Scope

- Changing `quickjs-wasi`, `quickjs-sync.v1`, worker supervision, resource limits or packaged runtime loading.
- Changing Response-tab diagnostic presentation; COMMERCE-044/045 own Response authoring.
- Changing Request validation/preview semantics established by COMMERCE-041.
- Changing JavaScript bindings or Request editor UX established by COMMERCE-040/042.
- Adding workflow gating or making Request validation a prerequisite for Create/Save/full-definition Validate/Publish.
- Logging expected guest syntax/entrypoint mistakes as operational errors.
- Logging guest source, Tool arguments, request/response bodies, headers, credentials, customer data, stacks or absolute filesystem paths.
- Database, Shared-contract, gateway or deployment changes.
- Live provider execution.

## Requirements

### R1 — preserve one bounded guest compiler message at the sandbox boundary

Extend the failure side of `KernelResult` with an optional bounded guest diagnostic message without changing the existing result codes:

```ts
{
  ok: false;
  code: RuntimeDiagnosticCode | 'DEADLINE' | 'CANCELLED' | 'THROTTLED';
  message?: string | null;
  line: number | null;
  column: number | null;
}
```

For **guest compile/entrypoint failures only**:

```text
SYNTAX_ERROR
```

`worker.mjs` must preserve the guest exception `message` when one exists.

The message MUST be bounded to at most **512 UTF-8 bytes before it leaves the worker**.

Do not include:

```text
stack
source text
input values
host paths
worker/WASM paths
```

If QuickJS-NG exposes explicit finite numeric source `line` / `column` properties, preserve them. Otherwise leave the existing `null` values. Do not parse host stack strings or invent locations.

Operational failures such as:

```text
RUNTIME_UNAVAILABLE
DEADLINE
CANCELLED
THROTTLED
```

must not expose internal runtime exception messages to the browser through this field.

### R2 — preserve the diagnostic through the Request processor

Extend the Request processor diagnostic shape from:

```ts
{ code: string }
```

to the bounded equivalent:

```ts
{
  code: string;
  message?: string;
  line?: number | null;
  column?: number | null;
}
```

`mapFailure(...)` must preserve `message`, `line` and `column` for guest `INVALID_REQUEST` failures such as `SYNTAX_ERROR`.

Keep the existing operational mapping unchanged:

```text
DEADLINE            -> DEADLINE
CANCELLED           -> CANCELLED
THROTTLED           -> THROTTLED
RUNTIME_UNAVAILABLE -> RUNTIME_UNAVAILABLE
```

Those operational results must not be converted into browser-input diagnostics.

### R3 — Request authoring validation uses the precise cause when available

Extend the local `processorDiagnostic(...)` input shape in `external-validation.ts` so it can consume:

```text
code
message
line
column
```

For a normal guest authoring failure, construct the existing `ToolAuthoringValidationIssue` using:

```text
path    = existing canonical Request path
code    = existing diagnostic code
message = diagnostic.message when present
          otherwise existing generic fallback
line    = propagated line when present
column  = propagated column when present
```

For the Request-only validation route, malformed JavaScript must therefore return a normal successful Server Action envelope containing:

```text
kind: ok
value.valid: false
issue.path: /request/source
issue.code: SYNTAX_ERROR
issue.message: bounded QuickJS-NG compiler cause
```

It MUST NOT become `INTERNAL_ERROR` merely because the guest source is invalid.

The existing generic fallback:

```text
Request processor did not compile
```

remains valid only when no safe guest diagnostic message is available.

### R4 — Request UI displays the returned issue; do not add a second parser

`ExternalHttpRequestTab` already renders `ToolAuthoringValidationIssue.message`.

Do not introduce a browser-side JavaScript parser/compiler or duplicate QuickJS syntax analysis.

Add a focused regression proving that when Request validation returns a bounded issue such as:

```text
/request/source
SYNTAX_ERROR
Unexpected end of input
```

the Request validation issue list visibly contains the diagnostic cause and does **not** replace it with `Request processor did not compile`.

The UI may continue to render line/column using the existing validation-issue presentation when those values are available. Do not redesign the Request tab in this task.

### R5 — operational logging remains separate from guest authoring diagnostics

Read and obey:

```text
docs/observability/shared-logging.md
```

Preserve COMMERCE-046 operational logging through:

```ts
@modainteract/moda-interact-shared/logging
```

Expected guest `SYNTAX_ERROR` / entrypoint authoring failures are bounded business/authoring results and MUST NOT produce new `error`-level runtime log events merely because compilation failed.

Operational failures continue to use the COMMERCE-046 shared structured runtime events.

Do not add:

```text
console.log
console.error
new service-local generic logger
```

and do not place guest source or compiler stacks into shared logs.

### R6 — diagnostic text is data-safe and deterministic

The browser-visible compiler message must be derived only from the QuickJS-NG guest exception message or the existing bounded generic fallback.

Required bounds/invariants:

```text
maximum message bytes: 512 UTF-8
maximum validation issues: existing ToolAuthoringValidation bound
no stack trace
no host filesystem paths
no guest source echo
no request arguments/body/header values
no credential/provider data
```

Do not expose arbitrary `cause`, serialized exception objects or worker diagnostic payloads through the Server Action.

## Work Items

- [ ] Extend `KernelResult` with an optional bounded diagnostic message.
- [ ] Preserve bounded QuickJS-NG `SYNTAX_ERROR` / entrypoint message in `worker.mjs`.
- [ ] Preserve Request processor diagnostic message/line/column through `mapFailure(...)`.
- [ ] Use the propagated Request compiler cause in `processorDiagnostic(...)` with the existing generic fallback.
- [ ] Add runtime/processor/validation/Server Action regressions for diagnostic propagation.
- [ ] Add one Request UI regression proving the exact returned authoring cause is visible.
- [ ] Prove operational runtime failures remain separately classified and do not leak internal messages.
- [ ] Preserve shared structured logging and prove no direct `console.*` runtime diagnostics are introduced.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-046
  QuickJS-NG/WASI SandboxKernel implementation

ARCH-021-COMMERCE-041
  Request-only authoritative validation and Request validation issue presentation

ToolAuthoringValidationIssue
  existing bounded path/code/message/line/column authoring issue contract

@modainteract/moda-interact-shared/logging
  existing operational runtime logging boundary
```

No new cross-repository contract is introduced.

The logical runtime identifier remains:

```text
quickjs-sync.v1
```

## Dependencies

- ARCH-021-COMMERCE-046

## Enables

None.

## Acceptance Criteria

- [ ] A malformed Request JavaScript source returns `SYNTAX_ERROR` with a non-empty bounded guest compiler message through the real SandboxKernel.
- [ ] A missing/invalid `buildRequest` entrypoint returns `SYNTAX_ERROR` with a bounded useful cause.
- [ ] Request processor `mapFailure(...)` preserves code/message/line/column for guest invalid-request diagnostics.
- [ ] `validateExternalHttpRequest(...)` returns `/request/source` with the propagated compiler cause instead of the generic fallback when a safe message exists.
- [ ] The Request Server Action returns the syntax issue as `kind: ok` / `valid: false`, not `INTERNAL_ERROR`.
- [ ] The Request UI visibly displays the propagated compiler cause.
- [ ] `Request processor did not compile` remains only the fallback when no bounded guest message exists.
- [ ] `RUNTIME_UNAVAILABLE`, `DEADLINE`, `CANCELLED` and `THROTTLED` retain their existing operational classification and do not expose internal runtime messages to the browser.
- [ ] Guest syntax/entrypoint failures do not create new error-level operational logs.
- [ ] No guest source, stack, Tool arguments, request/response body/header data, credentials or absolute host paths are logged or returned as diagnostics.
- [ ] COMMERCE-046 QuickJS-NG runtime packaging/worker/supervision behavior remains unchanged.
- [ ] No Request workflow gating, Response UI change, database migration or provider execution is introduced.

## Validation

Run from `moda-interact-commerce`:

```bash
npm run code-runtime:package
npm run code-runtime:smoke
npm run test:arch020-code-runtime-proof
npm run test:arch021-code-request
npm run test:arch021-external-tool-authoring-validation
npm run test:arch020-external-tools-ui
```

Add/extend focused regressions proving:

```text
real malformed Request compile -> SYNTAX_ERROR + bounded non-empty message
invalid/missing Request entrypoint -> bounded useful message
Request processor preserves message + optional location
Request validation preserves message at /request/source
Server Action serializes the bounded validation issue
Request UI renders the cause and not the generic fallback
runtime-unavailable/deadline/throttled/cancelled remain operational failures
```

Then run:

```bash
npm run typecheck

npm exec eslint \
  src/commerce/code-runtime/types.ts \
  src/commerce/code-runtime/kernel.ts \
  src/commerce/code-request/processor.ts \
  src/commerce/tool-authoring/external-validation.ts \
  src/studio/external-http/request-tab.tsx \
  tests/code-runtime-proof.test.ts \
  tests/code-request-processor.test.ts \
  tests/external-tool-authoring-validation.test.ts \
  tests/external-tool-authoring-server-actions.test.ts \
  tests/external-tools-ui.test.tsx

git diff --check
```

Source audits:

```bash
! rg -n \
  'console\\.(log|info|warn|error|debug)' \
  src/commerce/code-runtime

rg -n \
  '@modainteract/moda-interact-shared/logging' \
  src/commerce/code-runtime/kernel.ts
```

If repository-wide typecheck remains non-zero only for an established unrelated baseline, record the exact diagnostics and prove there are no diagnostics in task-owned files.

## Stop Condition

After the bounded guest compiler cause is preserved from QuickJS-NG through Request validation/UI, all Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not begin Response diagnostic work, Request gating, Test-tab work or another runtime refactor.

## Implementation Notes

Keep this task deliberately small. The accepted QuickJS-NG/WASI migration already executes the compiler successfully; this task only preserves safe diagnostic fidelity across existing result boundaries.

Prefer extending existing result types and mappings over introducing a second validation result contract.

Do not parse JavaScript in React and do not reconstruct compiler messages from codes when QuickJS-NG already supplied a safe message.

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
