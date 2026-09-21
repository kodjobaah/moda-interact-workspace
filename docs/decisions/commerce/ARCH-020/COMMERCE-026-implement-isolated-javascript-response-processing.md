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
status: ready
priority: 150
executor:
claimed_at:
attempt: 1
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

- [ ] Import029 proven kernel; preserve exact runtime/artifact version and limits. Do not reimplement worker lifecycle or change memory/time configuration.
- [ ] Implement createCodeResponseProcessor validation, JSON/TEXT response input serialization, guest-safe result extraction and strict output-schema-compatible object checks.
- [ ] Map bounded diagnostics and runtime failures exactly; no raw exception/source/body leakage or fallback. Declare runtime unavailable if accepted kernel cannot initialize.
- [ ] Cover correct text extraction, wrong output type/shape and malformed provider response through actual kernel; repeat029 smoke to establish the adapter retained limits.

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
database submodule was initialized by launcher preparation. Parent report is
ready for mirrored publication and Architect review. Review correction returned
the task to Ready with attempt 1 retained and no active executor claim.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.
