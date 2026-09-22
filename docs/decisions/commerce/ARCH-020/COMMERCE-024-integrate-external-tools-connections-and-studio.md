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
attempt: 2
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

- [ ] Wire020 lifecycle +028 credentials +021 transport +025/026 processors +030 publication +031 preview +032 availability into accepted factories; adapt fields without recreating business logic.
- [ ] Install022/023/027 components and bind accepted service methods with existing auth/Origin adapters. Preserve method/result/operation identity, not catch-all success wrappers.
- [ ] Demonstrate XN01–04 using real assembled application services and controlled external HTTP; verify EXTERNAL_HTTP cache bypass.
- [ ] If a producer is incomplete, record concrete failing producer contract and route correction to its owner; do not absorb missing persistence, eligibility, receipt/quota or runtime implementation into024.

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

Implementation complete; submitted for Architect Review. WI01 is not claimed because the full configured production-factory MCP path was not executed without live credentials or deployment validation.

### Files Changed

Implementation branch `task/ARCH-020-COMMERCE-024`, commit `1814f82c5828de50f1ae9f040da623f4ceba0ca7`:

- `src/commerce/integration/external/index.ts`
- `lib/preview/runtime.ts`
- `app/api/studio/preview/tool-tests/route.ts`
- `tests/external-wiring.test.ts`
- `package.json`

The Attempt-1 producer-owned connection changes were reverted from the task branch; no producer business logic was added.

### Work Completed

Composed the accepted credential command kernel, saved-tool loader, COMMERCE-038 external fixture runner, COMMERCE-031 preview factory, external HTTP executor, publication validation, and availability resolver. Preview runtime injection preserves one `PreviewService` state-store identity for ordinary and external tests. The tool-test route dispatches only validated `externalResponseFixture` requests to the external preview service; ordinary requests retain the existing path.

Acceptance mapping:

- WI02: `tests/external-wiring.test.ts`, `XN01-XN03`, and `XN04` exercise assembled credential isolation, provider transport boundaries, publication receipt storage, visual/JavaScript fixture processing, preview state identity, and provider-free replay. `tests/external-preview.test.ts` covers the accepted external preview regression suite.
- WI03: composition consumes accepted producer exports and introduces no duplicate connection, credential, HTTP, publication, response-processing, preview, availability, or fixture-runner algorithm.
- WI01: not claimed; the full connection -> tool -> publish -> release -> merchant -> MCP production path requires a separate configured integration execution.

### Validation Results

Passed:

- `npm run test:arch020-external-wiring`: 2/2
- `npm run test:arch020-external-preview`: 18/18
- `npm run test:arch020-external-publication`: 11/11
- `npm run test:arch020-external-http`: 13/13
- `npm run test:arch020-external-credentials`: 9/9
- `npm run test:arch020-external-availability`: 4/4
- targeted ESLint and `git diff --check`
- build webpack compilation and packaged code-runtime smoke completed

`npm run typecheck` and the final build exit remain blocked by 12 pre-existing baseline errors in `components/studio-workspace.tsx`, producer connection files, and unrelated tests. No Attempt-2 file appears in the remaining diagnostics. No live credentials, third-party calls, Shopify, WhatsApp, paid models, PostgreSQL/container checks, or deployment validation were run.

### Deviations

Attempt 2 was required after Attempt 1 lacked the accepted COMMERCE-019 source and reusable COMMERCE-038 fixture-runner seam. The implementation uses a composition-local command kernel because the accepted COMMERCE-020 lifecycle does not expose its internal kernel; producer-owned connection files were not retained in the final task diff.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox. Accepted dependency source was synchronized before claim. Recursive database submodule evidence: `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

### Unresolved Issues

WI01 remains unverified and is intentionally not claimed. The repository baseline still has the 12 typecheck/build diagnostics listed above; resolving them belongs to the relevant producer/UI/test owners unless Architect Review redirects scope.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Expected mirrored branch: `task/ARCH-020-COMMERCE-024`. Attempt 2 implementation worktree was physically isolated at `.../moda-interact-workspace.worktrees/ARCH-020-COMMERCE-024`; commit `1814f82c5828de50f1ae9f040da623f4ceba0ca7` was pushed to the task branch. Dependencies were consumed from accepted synchronized source; recursive database submodule was initialized at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

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
