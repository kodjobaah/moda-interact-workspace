---
id: ARCH-020-COMMERCE-029
architecture_id: ARCH-020
title: Prove and package bounded code runtime
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-001
enables:
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-012
  - ARCH-020-GATEWAY-003
created: 2026-09-21
updated: 2026-09-21
---

# Prove and package bounded code runtime

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/code-response/runtime/**, runtime artifact/build manifest and minimal direct runtime tests. Deliver a reusable bounded QuickJS worker kernel, not a paper evaluation or throwaway prototype. No Shared schemas, business validation, UI or production factory wiring.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/code-response/runtime/**, runtime artifact/build manifest and minimal direct runtime tests. Deliver a reusable bounded QuickJS worker kernel, not a paper evaluation or throwaway prototype. No Shared schemas, business validation, UI or production factory wiring.

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

- [x] Build/pin the synchronous QuickJS WASM variant with enforceable finite memory maximum and worker entry; record dependency/artifact hashes and supported runtime profile quickjs-sync.v1.
- [x] Implement the section9 SandboxKernel compile/run entry points and bounded JSON-text result. Prove C21 memory/time/abort/concurrency constraints with real execution.
- [x] Run positive text transform, infinite-loop, built-in long operation, allocation/serialization attack, forbidden capability and post-failure recovery scenarios before architecture acceptance.
- [x] Publish docs/code-runtime-proof.md with actual limits/results and artifact loading in the repository production build; if a required limit is not enforceable report that concrete gap and do not mark Complete or weaken it.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-COMMERCE-001

## Enables

- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-012
- ARCH-020-GATEWAY-003

## Acceptance Criteria

- [x] SB01: actual pinned worker/WASM executes synthetic transform and produces exact output; production build can load bundled artifact without network download.
- [x] SB02: heap/stack/WASM maximum and supervisor termination are demonstrated, including infinite loop and memory pressure; process remains usable afterward.
- [x] SB03: no guest network/filesystem/environment/module loader; distinct concurrent inputs remain isolated; fifth run throttles; slots/handles reclaimed on every terminal path.

## Validation

Ready for Review.

Use focused checks while implementing, then existing typecheck/build/lint where defined. Record unrun developer-owned PostgreSQL/container checks accurately; executable scenarios must still exist. No repeated unrelated full suites or screenshot quotas. No live credentials/WhatsApp delivery.

`moda-interact-commerce/src/commerce/code-response/runtime/types.ts`
`moda-interact-commerce/src/commerce/code-response/runtime/kernel.ts`
`moda-interact-commerce/src/commerce/code-response/runtime/worker.mjs`
`moda-interact-commerce/tests/code-runtime-proof.test.ts`
`moda-interact-commerce/scripts/code-runtime-manifest.mjs`
`moda-interact-commerce/docs/code-runtime-proof.md`
`moda-interact-commerce/package.json` and `package-lock.json`

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
Added `quickjs-emscripten@0.31.0` with the synchronous release WASM profile `quickjs-sync.v1`.
Added fresh-worker `SandboxKernel` compile/run entry points with 16 MiB QuickJS heap, 512 KiB stack, 64 MiB WASM linear-memory maximum, 500 ms guest interrupt, 2,000 ms supervisor/turn deadline, 64/16 MiB worker V8 limits, four active workers with no queue, cancellation, and `finally` capacity cleanup.
Disabled guest module loading, network/filesystem/environment/timer/credential host surfaces and deterministic clock/random access; validated object-only JSON output with depth, array, prototype/accessor, cycle-compatible serialization, and 48 KiB bounds.
Added deterministic fixtures for valid text transformation, syntax failure, infinite loop and recovery, allocation/output pressure, forbidden capability, deadline, cancellation, concurrent tenant-input isolation, and fifth-run throttling.
Added artifact manifest/hash command and proof documentation with actual runtime limits and requirement-to-fixture matrix.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

Agent-executed:

- `npm run test:arch020-code-runtime-proof` -> PASS, 1 file and 6 tests.
- `npm run lint` -> PASS.
- `npm run build` -> PASS; Prisma client generation and Next.js webpack production build completed successfully.
- `npm run code-runtime:manifest` -> PASS; `quickjs-emscripten@0.31.0`, `@jitl/quickjs-wasmfile-release-sync@0.31.0`, SHA-256 `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`, configured WASM maximum `67108864` bytes.
- `git diff --check` -> PASS.
- `npm run typecheck` -> FAIL only in pre-existing unrelated Prisma client typing surfaces: `lib/auth/development-platform-admin.ts` (four `Prisma.Sql`/`Prisma.sql` errors) and `lib/server/connections.ts` (implicit `tx` any). No runtime-owned file was reported.

Requirement-to-fixture matrix is committed in `docs/code-runtime-proof.md`; the focused command observes actual QuickJS execution, not safe-rejection-only mocks. No PostgreSQL, container, live provider, credential, DNS, or deployment validation was required or claimed for this bounded runtime task.

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
The repository-wide typecheck remains blocked by the unrelated Prisma generated-client baseline listed above; the production build's TypeScript phase passed.
Runtime code is not wired into the future typed adapter or production factory; those are explicitly owned by COMMERCE-026/024.

## Completion Report

Implementation completed in the dedicated implementation worktree
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-029`
on implementation branch `task/ARCH-020-COMMERCE-029`, committed and pushed as
`39e636f` (`feat(commerce): add bounded QuickJS code runtime`). The parent task
report is being submitted on the mirrored parent branch
`task/ARCH-020-COMMERCE-029`. No service gitlink, main branch, database schema,
architecture/index file or Architect Review text was modified.

### Work Completed

- Built and pinned the synchronous QuickJS WASM profile `quickjs-sync.v1` with
  `quickjs-emscripten@0.31.0` and
  `@jitl/quickjs-wasmfile-release-sync@0.31.0`.
- Implemented `SandboxKernel` compile/run entry points and a fresh-worker
  QuickJS execution path with bounded JSON-text results.
- Enforced a 16 MiB QuickJS heap, 512 KiB stack, 64 MiB WASM linear-memory
  maximum, 500 ms guest interrupt, 2,000 ms supervisor/turn deadline, 64/16
  MiB worker V8 limits, four active workers with no queue, cancellation and
  `finally` capacity cleanup.
- Disabled guest module loading, network, filesystem, environment, timers and
  credential host surfaces, with deterministic clock/random access.
- Added bounded object-only JSON serialization with depth, array,
  prototype/accessor, cycle-compatible and 48 KiB output protections.
- Added deterministic fixtures for positive text transformation, syntax failure,
  infinite loop and recovery, built-in long operation, allocation/serialization
  pressure, forbidden capability, deadline, cancellation, concurrent
  tenant-input isolation and fifth-run throttling.
- Published `docs/code-runtime-proof.md`, including actual runtime limits,
  artifact evidence and the requirement-to-fixture matrix. The runtime artifact
  manifest is loaded by the production build without a network download.

Implementation files are:

- `src/commerce/code-response/runtime/types.ts`
- `src/commerce/code-response/runtime/kernel.ts`
- `src/commerce/code-response/runtime/worker.mjs`
- `tests/code-runtime-proof.test.ts`
- `scripts/code-runtime-manifest.mjs`
- `docs/code-runtime-proof.md`
- `package.json` and `package-lock.json`

### Validation Results

- `npm run test:arch020-code-runtime-proof` -> PASS, 1 file and exact focused
  `6/6` tests. The scenarios observe actual QuickJS execution, not
  safe-rejection-only mocks.
- `npm run lint` -> PASS.
- `npm run build` -> PASS; Prisma client generation and the Next.js webpack
  production build completed successfully, including the production artifact
  load.
- `npm run code-runtime:manifest` -> PASS; the manifest records
  `quickjs-emscripten@0.31.0`,
  `@jitl/quickjs-wasmfile-release-sync@0.31.0`, SHA-256
  `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`, and
  configured WASM maximum `67108864` bytes.
- `git diff --check` -> PASS.
- `npm run typecheck` -> BLOCKED only by five known unrelated Prisma client
  typing diagnostics: four `Prisma.Sql`/`Prisma.sql` errors in
  `lib/auth/development-platform-admin.ts` and one implicit `tx` any in
  `lib/server/connections.ts`. No runtime-owned file was reported; the
  production build TypeScript phase passed.

### Requirement-to-Fixture Matrix

The complete matrix is committed in `docs/code-runtime-proof.md`: SB01 is
covered by the synthetic transform and artifact-load scenarios; SB02 by heap,
stack/WASM limits, infinite-loop supervisor termination, allocation pressure
and post-failure recovery; SB03 by forbidden-capability, tenant-isolation,
fifth-run throttling and terminal-path capacity-reclamation scenarios.

### Deviations

The repository-wide typecheck remains blocked by the five unrelated Prisma
generated-client baseline diagnostics described above. Shared package
publication is required only for SHARED-002 and is outside this task. Runtime
code is not wired into the future typed adapter or production factory; those
surfaces are owned by COMMERCE-026/024.

### Assumptions

C21 read-only scope applies; visual rules and generic JavaScript execute only
inside the specified bounded sandbox. C21 live HTTP, credentials, preview
receipts, schema validation and production assembly remain downstream task
responsibilities.

### Unresolved Issues

No implementation issue remains within this bounded runtime scope. PostgreSQL,
container, live provider, credential, DNS and deployment validation were not
required or claimed for this task. SYSTEM-TEST-002 requires explicit developer
invocation even when Ready.

### Architectural Concerns

None. The implementation preserves the C21 limits and ownership boundary;
future external tool definitions require publication rather than another
Background handler.

### Git / VCS

Dependency and worktree evidence: the dedicated physical implementation
worktree and mirrored task branch were used; the implementation commit is
`39e636f` and was pushed. The parent report branch is
`task/ARCH-020-COMMERCE-029`; this report change is the only parent-workspace
file change. Recursive database submodule state was not changed.

### Remaining Validation

Architecture review remains pending. No live credentials, WhatsApp delivery,
PostgreSQL/container run, deployment or assembled cross-service flow is claimed;
those are downstream/developer-owned checks. The task is ready for
`moda_architect` review.

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
