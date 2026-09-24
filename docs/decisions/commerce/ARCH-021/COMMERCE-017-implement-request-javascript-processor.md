---
id: ARCH-021-COMMERCE-017
architecture_id: ARCH-021
title: Implement bounded external request JavaScript processor
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 35
executor: copilot
claimed_at: 2026-09-24T08:04:15Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-020-COMMERCE-029
  - ARCH-020-COMMERCE-026
enables:
  - ARCH-021-COMMERCE-023
created: 2026-09-23
updated: 2026-09-24
---

# Implement bounded external request JavaScript processor

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Extend the proven QuickJS runtime with a second bounded entrypoint, `buildRequest({ args })`, that converts already input-schema-validated CommerceAgent arguments into the canonical Commerce-owned `ExternalRequestDescriptor` without performing network or credential operations.

## Context

ARCH-020 proved and packaged the QuickJS response transformer `transform(response)`. Phase 3 must reuse that exact isolation/runtime rather than introducing another JS engine or allowing `fetch()` from authored code.

## Scope

Refactor the accepted runtime into one generic sandbox kernel while preserving the response processor. Use these target locations:

```text
src/commerce/code-runtime/types.ts
src/commerce/code-runtime/kernel.ts
src/commerce/code-runtime/worker.mjs
src/commerce/code-response/processor.ts
src/commerce/code-request/processor.ts
scripts/code-runtime-manifest.mjs
scripts/code-runtime-packaged-smoke.mjs
tests/code-response-processor.test.ts
tests/code-request-processor.test.ts
package.json
```

The previous `src/commerce/code-response/runtime/*` implementation is moved/replaced by `src/commerce/code-runtime/*`; do not leave two independent sandbox implementations.

## Out of Scope

- HTTP/network execution.
- Connection/credential lookup.
- Shopify GraphQL.
- Studio editor UI.
- Publication policy.

## Requirements

### R1 — exact source entrypoint

Request source is a normal script defining:

```js
function buildRequest({ args }) {
  return {
    path: '/catalogue/search',
    query: { q: args.query },
    headers: { accept: 'application/json' }
  };
}
```

`export default`, ESM imports and async functions are not part of the contract.

Response source remains exactly the existing:

```js
function transform(response) { ... }
```

### R2 — generic worker modes

The single worker MUST support:

```text
compile-response
run-response
compile-request
run-request
memory-probe
```

or an equivalent enum carrying exactly the same distinction. There must be one runtime-limit manifest and one worker implementation.

### R3 — request input

Before invoking QuickJS, `createCodeRequestProcessor().process(...)` MUST:

1. reject aborted/deadline inputs;
2. validate `processing` through the COMMERCE-016 canonical Commerce contract;
3. validate `args` by JSON serialization as a plain bounded object (no functions, prototypes, accessors, symbols, BigInt, non-finite numbers or prototype-pollution keys);
4. bound serialized input to 128 KiB;
5. pass only `{ args }` into the guest.

No environment, shop/session, connection, secret, URL/origin, history or model state enters the guest.

### R4 — request output

The guest return value MUST be parsed with the COMMERCE-016 `ExternalRequestDescriptorSchema`. Any extra/unsafe field therefore fails.

Return exactly `CodeRequestProcessorResult`.

### R5 — sandbox invariants

Preserve the accepted runtime limits and disable at minimum:

```text
eval
Function
Date
fetch
XMLHttpRequest
require
process
importScripts
WebAssembly
Math.random
```

Keep current heap/stack/WASM/guest/supervisor/concurrency limits. No increase is authorized.

### R6 — compiler

`compile({ source, runtimeVersion, ... })` for request JavaScript MUST prove both syntax and existence of a callable `buildRequest` entrypoint. A script containing valid syntax but no `buildRequest` is `SYNTAX_ERROR`/invalid for authoring purposes.

### R7 — packaged runtime proof

Update the existing package/smoke scripts so the packaged worker proves both:

```text
transform(response)
buildRequest({ args })
```

using the same packaged WASM artifact/hash and memory ceiling.

### R8 — focused test cases

`test:arch021-code-request` MUST prove:

- deterministic successful descriptor;
- unknown extra output field rejected;
- absolute URL/origin/method/body rejected by the canonical Commerce descriptor;
- reserved header rejected;
- network/global access unavailable;
- non-finite/prototype/accessor output rejected;
- oversized input/output rejected;
- deadline/cancellation/throttling mapped correctly;
- no `buildRequest` fails compile;
- existing response processor regressions still pass.

## Work Items

- [ ] Extract one generic QuickJS runtime.
- [ ] Add request compile/run mode and processor.
- [ ] Validate request output through the canonical Commerce schema.
- [ ] Update packaged runtime proof.
- [ ] Add focused request regressions.

## Interfaces / Contracts

Consumes COMMERCE-016 `ExternalRequestConstruction`, `ExternalRequestDescriptor` and local Tool-definition contracts.

Produces a server-only processor consumed by COMMERCE-023. The External HTTP UI reaches request preview through the COMMERCE-023 server validation/preview boundary.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-020-COMMERCE-029
- ARCH-020-COMMERCE-026

## Enables

- ARCH-021-COMMERCE-023

## Acceptance Criteria

- [ ] One QuickJS sandbox implementation serves response and request code.
- [ ] Request code cannot perform I/O or receive secrets/context.
- [ ] Only canonical Commerce-valid request descriptors escape the sandbox.
- [ ] Existing response code behavior/package proof remains intact.

## Validation

- [ ] `npm run test:arch021-code-request`
- [ ] `npm run test:arch020-code-processor`
- [ ] `npm run test:arch020-code-runtime-proof`
- [ ] `npm run code-runtime:package`
- [ ] `npm run code-runtime:smoke`
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set task to `review`, return Completion Report and STOP. Do not wire this processor to live external HTTP.

## Implementation Notes

No second worker implementation is permitted. Preserve the current packaged-runtime contract and safety ceilings.

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
