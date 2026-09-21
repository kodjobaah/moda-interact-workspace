---
id: ARCH-020-COMMERCE-018
architecture_id: ARCH-020
title: Integrate Studio pages with production services
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 140
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-002
  - ARCH-020-COMMERCE-011
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
created: 2026-09-21
updated: 2026-09-21
---

# Integrate Studio pages with production services

## Architecture

ARCH-020. [Implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C4/C5/C7/C9/C14–C19 remain binding. The integration ownership specification is
[C20](../../../architecture/ARCH-020-implementation-contracts.md#c20-integration-task-ownership-and-parallel-execution).
Use actual accepted prerequisite source, never copied snapshots or new schemas.

## Objective

Connect accepted U01–U13 Studio components to the013 backend facade and existing discovery services. Own protected UI service/action adapters and integrated authoring navigation; no MCP runtime or preview backend changes.

## Context

The former013 combined backend, Studio and preview integration. This definition
replaces that combined scope;018 and019 can execute concurrently after013 and
their own component prerequisites complete. No task was claimed by this amendment.

## Scope

Connect accepted U01–U13 Studio components to the013 backend facade and existing discovery services. Own protected UI service/action adapters and integrated authoring navigation; no MCP runtime or preview backend changes.

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

- [ ] Own `src/commerce/integration/studio/` and minimal wiring in `src/studio/server-services.ts` plus Studio command Server Actions/client service transport. Do not change backend.ts, MCP route or preview runtime.
- [ ] Implement every008 StudioServices method against real013 publication/read services and011 discovery; recheck auth per request/action, Origin on mutations and role before replay.
- [ ] Apply the C20 field/error translation table, including source revision names, exact release members and pointer CAS. Rehydrate actual returned IDs into Studio view models; never synthesize IDs by splitting strings.
- [ ] Keep existing008 components, routes and draft state. Wire functional commands, preserve unknown-operation identity and role-aware controls; no page redesign or backend business-rule reimplementation.
- [ ] Create server-authorized merchant inspection/read models using013 current feature/grant-candidate resolver; never create a production conversation grant for U13.
- [ ] Provide `docs/commerce-studio-integration.md` and `test:arch020-studio-integration`. Demonstrate the complete populated authoring flow before collecting secondary layout evidence.

## Interfaces / Contracts

Source: `src/studio/contracts.ts: StudioServices` and the accepted
`docs/studio-service-contract.md`. Producer:013 `getCommerceBackend()` facade,
`CommerceLifecycle` commands/read snapshot and011 `createDiscoveryService`/compiler.
Factory destination: existing `src/studio/server-services.ts:getStudioServices`.
Use `lib/auth` helpers including requireStudioAdmin/requireStudioSuperAdmin and
assertStudioMutationOrigin. C20 lists actual payload mappings; no backend module
may be imported into browser bundles. New protected action files belong only to018.
If the accepted facade cannot express a required field, report the producer gap;
do not silently omit it or implement a second publication service.

## Dependencies

- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-002
- ARCH-020-COMMERCE-011

All dependencies must be Complete and architect-accepted before execution.
Readiness never launches a task; use the normal dedicated mirrored worktrees.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001

## Acceptance Criteria

- [ ] S01: actual U03 -> U04 -> U09 -> U06 -> U07 -> U06 -> U09 -> U10 -> U11 flow authors, validates, publishes and activates through real services; exact definitions/member positions/responseContract survive.
- [ ] S02: N01–N09/N12 and composer portion of N13 pass with real reads/actions; missing IDs/foreign revisions produce correct states and exact published revisions remain read-only.
- [ ] S03: ADMIN cannot publish; revoked admin denied on next request; duplicate clicks/CAS/changed replay and unknown-outcome recovery preserve exactly one write/audit and the original operationId.
- [ ] S04: discovery outage preserves local/saved draft; schema unavailable blocks publication; empty/not-found/denied/unavailable are distinct. No JSON-dump or fixture-success substitute for UI.
- [ ] S05: U13 presents authoritative eligibility/tool descriptors without token/definition leakage or grant writes; shop IDs cannot be inferred from fixture naming.
- [ ] S06: production/narrow/keyboard populated views use accepted008 components and return paths. U14 remains a link with contract handoff; actual preview behavior is019-owned.

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

Expected execution branch: task/ARCH-020-COMMERCE-018. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
