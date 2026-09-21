---
id: ARCH-020-COMMERCE-013
architecture_id: ARCH-020
title: Integrate Commerce backend runtime and publication services
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 125
executor: copilot
claimed_at: 2026-09-21T10:50:08Z
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-005
  - ARCH-020-COMMERCE-006
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-011
  - ARCH-020-COMMERCE-014
  - ARCH-020-COMMERCE-015
  - ARCH-020-COMMERCE-016
enables:
  - ARCH-020-COMMERCE-019
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-018
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
created: 2026-09-21
updated: 2026-09-21
---

# Integrate Commerce backend runtime and publication services

## Architecture

ARCH-020. [Implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C4/C5/C7/C9/C14–C19 remain binding. The integration ownership specification is
[C20](../../../architecture/ARCH-020-implementation-contracts.md#c20-integration-task-ownership-and-parallel-execution).
Use actual accepted prerequisite source, never copied snapshots or new schemas.

## Objective

Connect production publication storage/compiler validation, MCP authorization/dispatch and Shopify/policy adapters. Deliver the stable backend facade used independently by018 and019. No Studio page or preview lifecycle wiring.

## Context

The former013 combined backend, Studio and preview integration. This definition
replaces that combined scope;018 and019 can execute concurrently after013 and
their own component prerequisites complete. No task was claimed by this amendment.

## Scope

Connect production publication storage/compiler validation, MCP authorization/dispatch and Shopify/policy adapters. Deliver the stable backend facade used independently by018 and019. No Studio page or preview lifecycle wiring.

## Out of Scope

Other integration owners' files; new business features/pages; new Shared release,
database migration or external-service implementation; deployment, paid live
provider calls or WhatsApp delivery. Do not replace real components with fixtures.

## Requirements

Follow C20 file ownership and mapping rules. Authorize each protected request using
the accepted auth library. Reuse source schemas, field bounds, hashes and replay/CAS
semantics. Preserve all active work. No production test-adapter registration.
At preparation verify each source/export against its accepted commit and record
that SHA in the mapping document; pending producer symbols must not be guessed.

## Work Items

- [ ] Deliver `src/commerce/integration/backend.ts` with server-only `getCommerceBackend()`; C20 defines its typed members and lifetime rules. Do not import Studio or preview components.
- [ ] Implement durable `PublicationStoragePort`/authorization/feature/runtime adapters under `src/commerce/integration/backend/`. The accepted003 factory currently throws UNAVAILABLE; tests/in-memory storage are not a production adapter.
- [ ] Wire011 compiler into003 validation, one executable registry into publication and014, and014 into004. Resolve durable authorization records for004 using existing grant/feature/recovery models.
- [ ] Connect005 tokenless transport and015/006/016/007 privileged adapters with current server-owned identity, policy, installation lookup and a shared per-call budget. Register exact installed versions only.
- [ ] Preserve full Studio command semantics in the backend facade. Correct the known capability enable/disable CAS mismatch as C20 specifies; do not silently drop expectedUpdatedAt or weaken strict schemas.
- [ ] Replace the unavailable MCP runtime at app/api/mcp/route.ts with this composition; preserve existing HTTP profile. No request-specific identity/grant stored in a process-global singleton.
- [ ] Provide `docs/commerce-backend-integration.md`, exact facade types, mapping table and `test:arch020-backend-integration` plus `test:arch020-backend-integration:database` commands. Freeze these contracts before018/019 begin.

## Interfaces / Contracts

Binding wiring table (paths relative to Commerce repository):

| Source/export | Destination | Required adapter/file |
|---|---|---|
| `src/commerce/publication/lifecycle.ts: CommerceLifecycle`; `ports.ts: PublicationStoragePort` | Durable publication facade | `backend/publication-storage.ts`, `backend/publication.ts` |
| `lib/discovery/compiler.ts: createCommerceCompiler` | `QueryValidationPort.validate({definition})` | `backend/query-validation.ts`: compile the exact execution/input schema, validate mapping/output/template through accepted validators; bounded INVALID_DEFINITION vs unavailable errors |
| `execution/ports.ts: createPolicyOperationRegistry`;005 `createQueryExecutionPort` |014 `createDefinitionExecutor` | `backend/executors.ts`: one immutable exact-version registry shared with publication availability |
|015 `createProductPolicyAdapters`,006 `createDiscountRuleReader`/`getDiscountOptions`,016 `createDiscountEvaluationAdapter` | Policy registry | preserve operation input/output; adapt context without resetting budget/deadline or deriving shop from arguments |
|007 accepted recommendation descriptors | Policy registry | record its actual exported symbol on accepted source before Ready; no invented handler name |
|004 `resolveAuthorizedSnapshot`, `createMcpService`, assertion verifier | `/api/mcp` | `backend/authorization.ts`, backend facade and existing MCP route only |

Typed product/rule/evidence interfaces are their accepted module exports; C19
field semantics and C18 evidence separation remain authoritative. This task owns
backend assembly only, including real PostgreSQL and HTTP transports.

## Dependencies

- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-005
- ARCH-020-COMMERCE-006
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-011
- ARCH-020-COMMERCE-014
- ARCH-020-COMMERCE-015
- ARCH-020-COMMERCE-016

All dependencies must be Complete and architect-accepted before execution.
Readiness never launches a task; use the normal dedicated mirrored worktrees.

## Enables

- ARCH-020-COMMERCE-019
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-018
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001

## Acceptance Criteria

- [ ] B01: real publication/compiler/storage create and publish a valid query and release; invalid field/mapping/version or absent executor produces zero publication/audit writes.
- [ ] B02: duplicate operation ID commits one effect/audit; mismatched reuse and stale CAS conflict. Pointer/member writes rollback together on injected failure; two real DB connections exercise races.
- [ ] B03: authenticated MCP resolve/list/call executes the published query through005; old seeded grant remains pinned after new publication; cross-shop/revoked/expired assertion dispatches zero provider calls.
- [ ] B04: every policy registration matches installed version/schema; renamed discount/recommendation tool works; unknown/missing adapter fails closed. Provider budgets are shared by reference across nested adapters.
- [ ] B05: production factory is callable with real dependencies and contains no fixture registration; missing config returns typed unavailable; backend import does not require018/019 or browser code.
- [ ] B06: known capability enable/disable timestamp CAS is preserved in strict input, payload hash and same transaction as the write; stale timestamp and changed replay payload have zero committed changes.

## Validation

Use the C20 shared isolated seed contract and this task's named scenarios. Assert
rows, operation IDs, provider calls and state, not only HTTP200 or screenshots.
Substitute external provider/model transports only; application services under
integration remain real. Run focused integration tests during work, then repository
typecheck/lint/build before submission. No redundant full-suite reruns without new
changes/failures. PostgreSQL/Redis/container checks obey the existing execution
policy: provide the command and actual evidence separately; a not-run required
check is not a pass. No paid model, live Shopify or production credentials required.
Document owned commands and exact outputs in the report; C20 maps every former
I01–I09 requirement to an owner so no acceptance coverage disappears.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Ready for Review.

### Files Changed

Implementation branch `task/ARCH-020-COMMERCE-013`: `src/commerce/integration/backend.ts`,
`src/commerce/integration/backend/{authorization,executors,publication-storage,query-validation}.ts`,
`app/api/mcp/route.ts`, publication lifecycle/ports, backend integration tests,
auth entrypoint test, package scripts, and `docs/commerce-backend-integration.md`.

### Work Completed

- Added the server-only `getCommerceBackend()` facade with publication, discovery,
  compiler, shared execution, explicit fixture execution, saved-selection and
  inspection boundaries; missing saved/inspection production adapters fail closed.
- Replaced the MCP route's unavailable composition with the backend runtime and
  retained request-scoped assertion, grant, turn and budget state.
- Added Prisma-backed serializable publication storage with advisory locking,
  durable replay reconstruction from audit metadata, atomic business/audit writes,
  canonical tool-definition JSON, and strict metadata/edit/pointer CAS.
- Wired accepted compiler, executor registry, query, policy, discount,
  recommendation, assertion and authorization exports without adding fixture
  registration to production.
- Corrected the known enable/disable timestamp CAS mismatch for both capability
  and tool commands; updated the lifecycle test to supply the current token.

### C20 Requirement Matrix

| Requirement | Evidence / disposition |
| --- | --- |
| B01 | Compiler validation and publication integration are wired; focused lifecycle and execution tests pass. Real PostgreSQL publication rows remain developer validation. |
| B02 | Serializable transaction, advisory lock, replay audit and atomic write path are implemented. Two-connection race/rollback evidence remains pending isolated PostgreSQL validation. |
| B03 | MCP route composes verified assertions, authorization snapshot and exact execution registry; request-scoped identity is preserved. Live grant/provider evidence remains pending. |
| B04 | Exact `1.0.0` policy registration and immutable registry are composed from accepted exports; renamed/adapter/provider budget scenarios are covered by prerequisite tests and require integrated provider evidence. |
| B05 | Server-only facade, no fixture registration, typed unavailable behavior, and production build are verified. |
| B06 | Capability and tool enable/disable require `expectedUpdatedAt`, hash the strict request, compare inside the transaction, and update the timestamp. Focused suite passes. |

Former I01-I09 ownership is preserved: I01/06/07 are COMMERCE-018, I09 is
COMMERCE-019, and I02/03/04/05/08 are represented by this backend boundary and
the pending real-infrastructure evidence above.

### Validation Results

Agent-executed checks, implementation worktree `task/ARCH-020-COMMERCE-013`:

- `npm run test:arch020-backend-integration`: passed, 4 files / 49 tests.
- `npm run typecheck`: passed; Next route types generated and `tsc --noEmit` passed.
- `npm run lint`: passed.
- `npm run build`: passed; Prisma Client 6.19.3 generated and Next production build completed.
- `npm run test:arch020-backend-integration:database`: static schema check passed;
  migration validator failed closed before connection with `Local isolated target required`
  because no `DATABASE_URL` was supplied.
- `git diff --check`: passed.

Developer validation required: run the migration validator twice against
developer-created localhost PostgreSQL databases `arch020_test_fresh` and
`arch020_test_upgrade`, plus the C20 real PostgreSQL two-connection race/rollback
and Redis/container transport checks. Record actual rows, operation IDs, audit
rows, provider calls, and rollback state; no pass is claimed here.

### Deviations

No scope deviation. The saved-selection and inspection adapters are explicit
injected boundaries and fail closed until their owning Studio/preview integration
provides real server adapters; no fixtures or browser code cross the backend
boundary.

### Assumptions

Accepted producer source SHAs and installed versions are recorded in
`docs/commerce-backend-integration.md`. Database submodule is consumed at
`5abfd87f57038bae515aaa09ec7c8db62adcfb98`; shared package `0.13.1`, Prisma
`6.19.3`, Next `16.3.5`, and MCP SDK `1.30.0`.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Attempt 1 uses mirrored `task/ARCH-020-COMMERCE-013` branches. Parent claim is
`97180042`; implementation branch started at `aaa776c14dde87260afdd3c9a1d2797db613df4f`.
At submission record the implementation and parent report commit hashes and push
results, the database submodule SHA above, and confirmation that no main branch
or parent service gitlink was changed.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.


## Architect readiness reconciliation — COMMERCE-007 acceptance — 2026-09-21

Promoted **Ready**, Attempt 0 retained, executor/claimed_at null. COMMERCE-003/004/005/006/007/011/014/015/016 are architect-accepted Complete, including COMMERCE-007 Attempt 7 at `e08b896`. All explicit prerequisites are satisfied. Normal preparation owns synchronization and claim and must consume actual accepted source. No automatic launch, implementation change, main integration or gitlink update.
