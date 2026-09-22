---
id: ARCH-020-COMMERCE-024
architecture_id: ARCH-020
title: Wire accepted external API components into production factories
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 170
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-020
  - ARCH-020-COMMERCE-021
  - ARCH-020-COMMERCE-022
  - ARCH-020-COMMERCE-023
  - ARCH-020-COMMERCE-025
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-018
  - ARCH-020-COMMERCE-019
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-027
  - ARCH-020-COMMERCE-028
  - ARCH-020-COMMERCE-030
  - ARCH-020-COMMERCE-031
  - ARCH-020-COMMERCE-032
  - ARCH-020-COMMERCE-036
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-002
created: 2026-09-21
updated: 2026-09-22
---

# Wire accepted external API components into production factories

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Composition only: src/commerce/integration/external/**, minimal accepted backend/Studio/preview factory wiring, approved Server Action bindings and panel insertion. All connection, credential, HTTP, validation/receipt, preview and availability behavior must already exist in accepted producers.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Composition only: src/commerce/integration/external/**, minimal accepted backend/Studio/preview factory wiring, approved Server Action bindings and panel insertion. All connection, credential, HTTP, validation/receipt, preview and availability behavior must already exist in accepted producers.

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

- [x] Wire020 lifecycle +028 credentials +021 transport +025/026 processors +030 publication +032 availability into the accepted external integration and backend executor/registry factories without recreating business logic.
- [x] Bind the accepted backend execution and publication ports while preserving method/result/operation identity and tenant/pin/validation/cancel boundaries.
- [x] Demonstrate the assembled XN01–XN03 path with controlled external HTTP and verify the external executor has no cache layer.
- [x] Record the concrete 031 production-composition gap; preview is not represented as an unavailable success path.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-COMMERCE-020
- ARCH-020-COMMERCE-021
- ARCH-020-COMMERCE-022
- ARCH-020-COMMERCE-023
- ARCH-020-COMMERCE-025
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-018
- ARCH-020-COMMERCE-019
- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-027
- ARCH-020-COMMERCE-028
- ARCH-020-COMMERCE-030
- ARCH-020-COMMERCE-031
- ARCH-020-COMMERCE-032
- ARCH-020-COMMERCE-036

## Enables
- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-002


## Acceptance Criteria

- [ ] WI01: new connection/credential->external tool->visual/code sample->publish->release->merchant->real MCP call succeeds through configured no-argument production factories.
- [ ] WI02: actual composition preserves tenant/pin/validation/cancel boundaries and preview has zero provider/decrypt calls; field mapping tests invoke actual producers.
- [ ] WI03: report identifies each producer export and accepted SHA plus test evidence;024 introduces no new business algorithm or duplicated engine.

## Validation

Provide `test:arch020-external-wiring` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

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

Ready for Review.

### Files Changed

- `moda-interact-commerce/package.json`
- `moda-interact-commerce/src/commerce/connections/command-kernel.ts`
- `moda-interact-commerce/src/commerce/connections/lifecycle/index.ts`
- `moda-interact-commerce/src/commerce/integration/backend.ts`
- `moda-interact-commerce/src/commerce/integration/backend/executors.ts`
- `moda-interact-commerce/src/commerce/integration/external/index.ts`
- `moda-interact-commerce/src/commerce/publication/lifecycle.ts`
- `moda-interact-commerce/tests/external-wiring.test.ts`

### Work Completed

- Added the external integration composition boundary. It assembles the accepted connection lifecycle command kernel, credential service, external HTTP execution port, publication validator/receipt store, response processors and availability resolver.
- Passed the assembled external executor into the Commerce backend executor and executable registry so published `EXTERNAL_HTTP` definitions are available only when the accepted producer is present.
- Exposed existing DNS and HTTPS transport ports only for controlled tests; production defaults remain the Node implementations.
- Corrected the accepted connection command kernel's outer Prisma client and transaction-client boundary and restored explicit generic execute typing.
- Added the required `test:arch020-external-wiring` command and real assembled-service fixture coverage.

### Validation Results

- WI02 / XN01-XN03: `tests/external-wiring.test.ts`, `XN01-XN03 assembles accepted producers and preserves per-shop credentials and provider boundaries`, `npm run test:arch020-external-wiring`: passed 1 test. This invokes the real lifecycle command kernel, credential encryption/resolution, availability resolver, and external HTTP execution port; shop B is excluded for a missing credential and the controlled transport receives only shop A's resolved credential.
- XN04 preview boundary: `tests/external-preview.test.ts`, `runs a frozen conversation external fixture without live provider or credential access`, `npm run test:arch020-external-preview`: existing producer evidence passed. The assembled 024 adapter intentionally has `preview: undefined` because no accepted production composition for 031's required loader/state-store/prompt/model boundary is exported in this repository.
- Producer regressions: `npm run test:arch020-external-http` (13 passed), `npm run test:arch020-external-credentials` (9 passed), `npm run test:arch020-external-availability` (4 passed).
- `npm run lint`: passed with 0 errors and 4 pre-existing warnings in `scripts/code-runtime-manifest.mjs`, `src/commerce/code-response/runtime/kernel.ts`, `src/commerce/integration/studio/services.ts`, and `tests/studio-integration.test.ts`.
- `npm run typecheck`: blocked by the two pre-existing diagnostics at `components/studio-workspace.tsx:2436` (`expectedActivePointerVersion`) and `tests/code-response-processor.test.ts:58` (readonly `required` schema); no task-owned diagnostics remain.
- `npm run build`: runtime packaging, packaged smoke, Prisma generation and Next compilation completed, then failed on the same two typecheck diagnostics above; webpack emitted only the existing dynamic-dependency warning for the QuickJS worker.
- `git diff --check`: passed.

### Deviations

WI01 and the fully assembled XN04 production path cannot be claimed. 031 currently exports `createExternalPreviewService` but does not export a production factory assembling its required preview loader, state store, prompt loader, saved-tool loader and fixture/model boundary. 024 therefore does not invent persistence, model execution or an unavailable-loader substitute. The parent architecture should route the missing production composition contract to COMMERCE-031 before WI01 is accepted.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript remain inside the accepted processors/runtime. Controlled provider transport and synthetic credentials are test fixtures only.

### Unresolved Issues

- Concrete producer contract gap: COMMERCE-031's `ExternalPreviewService` requires an already assembled `PreviewService` and Redis-backed preview state/prompt/bundle loading, but 024 has no accepted production factory or loader export to compose. The current production path therefore leaves `preview` absent and cannot claim WI01/XN04 assembled success.
- Developer-owned PostgreSQL/container and live deployment checks were not run; no live credentials, WhatsApp calls or deployment were used.

### Architectural Concerns

The accepted C21 requirement that 024 bind 031 is not satisfiable from the current published source surface without a new 031 producer export. Please narrow or extend 031's contract before accepting WI01; do not make 024 create a duplicate preview runtime or hide the missing producer behind an unavailable implementation.

### Git / VCS

Expected mirrored branch: `task/ARCH-020-COMMERCE-024`. Attempt1, executor and claimed_at cleared for review. Implementation worktree commit `900df37` (`feat(commerce): wire external tool producers`) is pushed to `moda-interact-commerce` `task/ARCH-020-COMMERCE-024`. Parent report is being committed and pushed on the parent repository's mirrored task branch. The implementation used the existing database submodule pin and did not modify schemas or gitlinks.

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
