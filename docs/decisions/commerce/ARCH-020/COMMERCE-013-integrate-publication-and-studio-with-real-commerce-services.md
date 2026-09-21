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
status: pending
priority: 125
executor: null
claimed_at: null
attempt: 0
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

Not Started.

### Files Changed

None; implementation has not started.

### Work Completed

None; task definition only.

### Validation Results

Not run. At execution, distinguish agent checks from exact developer validation required.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-COMMERCE-013. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
