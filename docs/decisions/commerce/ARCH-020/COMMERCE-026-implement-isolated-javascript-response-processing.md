---
id: ARCH-020-COMMERCE-026
architecture_id: ARCH-020
title: Implement validated code-processing adapter over proven runtime
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 150
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-029
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-GATEWAY-003
  - ARCH-020-COMMERCE-030
  - ARCH-020-COMMERCE-031
created: 2026-09-21
updated: 2026-09-21
---

# Implement validated code-processing adapter over proven runtime

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/code-response/processor.ts and validation adapter tests only;029 exclusively owns runtime/** and artifacts. Adapt accepted SandboxKernel to C21 Shared input/result types and output validation. No new sandbox engine, UI, HTTP or factory wiring.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/code-response/processor.ts and validation adapter tests only;029 exclusively owns runtime/** and artifacts. Adapt accepted SandboxKernel to C21 Shared input/result types and output validation. No new sandbox engine, UI, HTTP or factory wiring.

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

- [x] Import029 proven kernel; preserve exact runtime/artifact version and limits. Do not reimplement worker lifecycle or change memory/time configuration.
- [x] Implement createCodeResponseProcessor validation, JSON/TEXT response input serialization, guest-safe result extraction and strict output-schema-compatible object checks.
- [x] Map bounded diagnostics and runtime failures exactly; no raw exception/source/body leakage or fallback. Declare runtime unavailable if accepted kernel cannot initialize.
- [x] Cover correct text extraction, wrong output type/shape and malformed provider response through actual kernel; repeat029 smoke to establish the adapter retained limits.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-029

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-GATEWAY-003
- ARCH-020-COMMERCE-030
- ARCH-020-COMMERCE-031

## Acceptance Criteria

- [ ] CA01: same accepted runtime produces exact synthetic text/JSON output through exported processor; unsupported version and invalid source rejected.
- [ ] CA02: invalid/cyclic/nonfinite/oversized/nonobject results rejected, runtime failure maps correctly and successful sample does not bypass future checks.
- [ ] CA03: actual kernel timeout/abort/isolation smoke still passes with adapter; no duplicated engine or relaxed limits.

## Validation

Provide `test:arch020-code-processor` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

Use focused checks while implementing, then existing typecheck/build/lint where defined. Record unrun developer-owned PostgreSQL/container checks accurately; executable scenarios must still exist. No repeated unrelated full suites or screenshot quotas. No live credentials/WhatsApp delivery.

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

Implementation complete; submitted for moda_architect review.

### Files Changed

`src/commerce/code-response/processor.ts`, `tests/code-response-processor.test.ts`,
`package.json`, and `package-lock.json`.

### Work Completed

Implemented `createCodeResponseProcessor` over the accepted COMMERCE-029
`createSandboxKernel` without duplicating runtime lifecycle or changing runtime
limits. The adapter validates Shared `TransformResponse` and JavaScript
processing contracts, serializes only the approved response fields, maps bounded
kernel failures, and rejects non-object, unsafe, cyclic/nonfinite, oversized,
deep, and over-cardinality outputs. Added the accepted Shared `0.14.2` consumer
pin and focused adapter command.

### Validation Results

* CA01: `tests/code-response-processor.test.ts` / `transforms JSON through the accepted kernel`,
  `transforms TEXT without attempting JSON parsing` / `npm run test:arch020-code-processor`
  -> 6/6 tests passed after the review regression was added.
* CA02: `rejects malformed responses and non-object output roots`,
  `maps syntax, deadline, cancellation, and output-limit failures` / the same
  focused command -> passed; actual kernel diagnostics and bounded output checks observed.
* C21 sections 2.3/9.4 schema boundary: `leaves result-schema enforcement at the Shared validation boundary`
  uses `compileSubset(resultSchema, "details")` after a successful adapter result;
  wrong-typed `title: 42` is rejected while `resultSchema` remains absent from
  `CodeResponseProcessorInput`. `npm run test:arch020-code-processor` -> passed.
* CA03: `keeps simultaneous inputs isolated` plus accepted runtime proof
  `tests/code-runtime-proof.test.ts` / `npm run test:arch020-code-processor` and
  `npm run test:arch020-code-runtime-proof` -> 5/5 and 10/10 passed.
* Packaged runtime: `npm run code-runtime:package && npm run code-runtime:smoke`
  -> passed with `quickjs-sync.v1`, `quickjs-emscripten@0.31.0`, artifact SHA256
  `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`, 64 MiB
  WASM ceiling, and max 4 workers.
* `npm run lint` -> passed with two existing warnings in COMMERCE-029 runtime
  files. `npm run typecheck` -> blocked by unrelated existing integration/Prisma
  diagnostics; no new processor/test diagnostics were reported.
* Review correction rerun: the first post-correction focused invocation once
  returned `EXECUTION_ERROR` before subsequent clean reruns; no deterministic
  reproduction occurred. The final focused run passed 6/6, and the accepted
  runtime proof remained 10/10.

### Deviations

The accepted Shared producer revision is consumed as published package `0.14.2`.
No runtime files or artifacts owned by COMMERCE-029 were modified.

### Assumptions

C21 read-only scope; visual rules remain owned by COMMERCE-025 and generic
JavaScript is executed only through the accepted COMMERCE-029 sandbox.

### Unresolved Issues

Repository-wide typecheck remains blocked by pre-existing integration/Prisma
diagnostics outside this task. Full schema/render validation is owned by the
later COMMERCE-030 publication validator and COMMERCE-024 assembly path. This
task consumes the Shared processor input contract and performs the bounded
guest-output validation available at this port; it does not duplicate or invent
the downstream `resultSchema` port.

### Architectural Concerns

COMMERCE-030's production validator is still pending, so this task cannot prove
the eventual assembled publication/sample service. The focused regression now
proves the accepted Shared schema validator rejects a wrong-typed adapter result
and explicitly preserves the boundary: COMMERCE-026 does not accept or validate
`resultSchema`; COMMERCE-030/024 must perform that check before rendering/model
flow.

### Git / VCS

Implementation branch `task/ARCH-020-COMMERCE-026` published at commit
`4b8e5bc` (includes prior implementation `ae47b61`). Physical isolated worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-026`.
Accepted runtime dependency: `quickjs-emscripten@0.31.0`, Shared `0.14.2`;
database submodule was initialized by launcher preparation. Correction was
reclaimed through the launcher as Attempt 2 with executor `copilot`, claimed at
`2026-09-21T22:47:39Z`; parent claim commit
`5c9859e861cf19a3423a3423dfd37c5291299b77`. Parent report is resubmitted for
Architect review.

## Architect Review

### Review Status

Accepted.

### Review Notes

Attempt 2 accepted. Reviewed the exact submitted snapshot representing implementation
`4b8e5bc` and parent report `170074b3`.

The adapter remains inside the COMMERCE-026 ownership boundary: `processor.ts` consumes
the accepted COMMERCE-029 sandbox kernel and Shared `0.14.2` contracts without
modifying `runtime/**`, introducing another sandbox engine, or adding HTTP/UI/factory
behavior.

Functional inspection confirms:

- `createCodeResponseProcessor` is server-only;
- JSON and TEXT responses are serialized only through the approved
  `status/contentType/bodyText/json` surface;
- Shared `TransformResponseSchema` and `ResponseProcessingSchema` are applied before
  execution and only the JAVASCRIPT processing variant is admitted;
- expired deadlines and already-aborted calls fail before guest execution;
- the adapter delegates execution/compile to the accepted kernel and maps
  `DEADLINE`, `CANCELLED` and `THROTTLED` without exposing raw exceptions;
- syntax/runtime/resource failures map to bounded `INVALID_RESPONSE` diagnostics;
- successful guest output must be a plain object with finite JSON values, no
  prototype-pollution keys, maximum depth 20, nested arrays bounded by both 20 and
  `limits.maxSearchResults`, and maximum serialized output 48 KiB;
- unsupported runtime versions fail closed;
- simultaneous inputs remain isolated through the accepted fresh-worker kernel.

C21 section 2.3 final `resultSchema` validation is not duplicated into the
`CodeResponseProcessorInput` contract. The accepted architecture assigns the
assembled sample/publication schema check to COMMERCE-030
`validateSampleAndRecord(...)`, which invokes the processor and then validates the
returned object before recording the receipt. The committed regression correctly
proves the Shared subset validator rejects a wrong-typed successful processor result
without widening this adapter's port.

The accepted COMMERCE-029 runtime manifest is not redefined by this task. Attempt 2
reran the accepted packaged-runtime proof and recorded `quickjs-sync.v1`,
`quickjs-emscripten@0.31.0`, artifact SHA-256
`0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`, the 64 MiB
WASM ceiling and four-worker process cap. No runtime-owned file or artifact was
changed.

One focused run was reported to have returned a non-reproducing `EXECUTION_ERROR`
before subsequent clean reruns. Because the final focused adapter suite passed 6/6,
the independent accepted runtime proof passed 10/10, and no deterministic recurrence
was found, this is recorded as non-blocking review evidence rather than hidden.

### Reviewed Files

- `src/commerce/code-response/processor.ts`
- `tests/code-response-processor.test.ts`
- `src/commerce/code-response/runtime/types.ts` (dependency contract inspection only)
- `src/commerce/code-response/runtime/kernel.ts` (dependency contract inspection only)
- `package.json`
- `package-lock.json`
- this task Completion Report
- C21 sections 2.2, 2.3, 9.4 and 9.5

### Validation Reviewed

Submitted evidence:

- `npm run test:arch020-code-processor` -> PASS, 6/6.
- `npm run test:arch020-code-runtime-proof` -> PASS, 10/10.
- `npm run code-runtime:package && npm run code-runtime:smoke` -> PASS.
- packaged runtime -> `quickjs-sync.v1`, artifact SHA-256
  `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`,
  64 MiB WASM ceiling, maximum four workers.
- `npm run lint` -> PASS with two pre-existing COMMERCE-029 runtime warnings.
- `npm run typecheck` -> blocked by unrelated existing integration/Prisma
  diagnostics; no COMMERCE-026 processor/test diagnostic was reported.
- `git diff --check` -> PASS.

The submitted archive does not carry installed dependencies or Git remote metadata,
so dependency-backed commands and remote branch heads were not falsely claimed as
independently rerun/verified in the review container.

### Architecture Conformance

Accepted. CA01-CA03 are satisfied for this bounded adapter. COMMERCE-026 reuses the
accepted runtime, preserves its isolation/resource contract, consumes the accepted
Shared contract, and does not take ownership of COMMERCE-030 publication validation,
COMMERCE-031 preview authorization/quotas, COMMERCE-024 assembly, HTTP transport,
credentials, or UI behavior.

### Follow-up

None for COMMERCE-026. Set task Complete at Attempt 2 and clear the execution claim.

No dependent task becomes Ready from COMMERCE-026 alone in this snapshot:
COMMERCE-030 still requires COMMERCE-025 in addition to its other prerequisites;
COMMERCE-031 remains gated by COMMERCE-019, COMMERCE-025 and COMMERCE-030;
COMMERCE-024, GATEWAY-003 and COMMERCE-012 retain additional declared dependencies.
Do not automatically launch any downstream task.
