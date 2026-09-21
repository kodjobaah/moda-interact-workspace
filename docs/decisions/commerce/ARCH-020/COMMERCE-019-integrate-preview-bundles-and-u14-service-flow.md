---
id: ARCH-020-COMMERCE-019
architecture_id: ARCH-020
title: Integrate preview bundles and the U14 service flow
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 145
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-009
  - ARCH-020-COMMERCE-017
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-002
  - ARCH-020-COMMERCE-033
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-024
  - ARCH-020-COMMERCE-031
created: 2026-09-21
updated: 2026-09-21
---

# Integrate preview bundles and the U14 service flow

## Architecture

ARCH-020. [Implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C4/C5/C7/C9/C14–C19 remain binding. The integration ownership specification is
[C20](../../../architecture/ARCH-020-implementation-contracts.md#c20-integration-task-ownership-and-parallel-execution).
Use actual accepted prerequisite source, never copied snapshots or new schemas.

## Objective

Connect saved definitions and prompts to the009 preview lifecycle and017 U14 client, using real Redis and isolated provider/model fixtures. Own preview assembly only; no U01–U13 service wiring.

## Context

The former013 combined backend, Studio and preview integration. This definition
replaces that combined scope;018 and019 can execute concurrently after013 and
their own component prerequisites complete. No task was claimed by this amendment.

## Scope

Connect saved definitions and prompts to the009 preview lifecycle and017 U14 client, using real Redis and isolated provider/model fixtures. Own preview assembly only; no U01–U13 service wiring.

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

- [ ] Own `src/commerce/integration/preview/` and minimal composition in `lib/preview/runtime.ts` plus U14 client injection. Do not edit018 Studio services/actions or013 backend factory.
- [ ] Implement PreviewBundleLoader, PreviewPromptLoader and PreviewToolExecutionPort from accepted009 types using013 read facade and authorized saved revisions. Do not replace authored prompts with generic strings.
- [ ] Freeze exact revision content, response definition and synthetic grant at start. After a saved draft changes, an existing conversation still executes its frozen definition; no reloading latest tool content during later turns.
- [ ] Instantiate009 PreviewService/RedisPreviewStateStore and typed ports. Use014 actual interpreter with isolated fixture operation adapters; explicit MODEL mode uses separate model config, never production credentials.
- [ ] Connect017 PreviewClient to exact C9.1 routes. Retain008 layout handoff and Back restoration using component fixture mounting where needed; no dependency on018 service adapters.
- [ ] Provide `docs/commerce-preview-integration.md` and `test:arch020-preview-integration` plus `test:arch020-preview-integration:redis`; preserve existing quotas/replay/cancel logic instead of duplicating it.

## Interfaces / Contracts

Source: `src/commerce/preview/types.ts: PreviewBundleLoader, PreviewPromptLoader,
PreviewToolExecutionPort` and `service.ts: PreviewServiceDependencies`.
`lib/preview/types.ts`/`service.ts` re-export these; do not create a second service.
Destination: `lib/preview/runtime.ts:getPreviewService`, replacing unavailableLoader
with real preview adapters.017's accepted PreviewClient supplies frontend route
calls; record actual file/export once017 is accepted, not a guessed symbol.
013 provides read-only saved-definition access and interpreter factory;019 supplies
fixture transports explicitly. Never reuse the live policy/provider registry.
PreviewResult and body/error shapes remain009/C9.1, not UI-specific alternatives.

## Dependencies

- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-009
- ARCH-020-COMMERCE-017
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-002

All dependencies must be Complete and architect-accepted before execution.
Readiness never launches a task; use the normal dedicated mirrored worktrees.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-024
- ARCH-020-COMMERCE-031

## Acceptance Criteria

- [ ] P01: real017 UI ->009 route -> real saved loader -> Shared runner/interpreter -> Redis -> reply/details flow; no fake preview service or constant EVAL response.
- [ ] P02: N10/N11/N13 preview portion covers release/draft/tool entry, sidebar, Back and refresh loss. Test the real008 composer handoff with injected source data;018 is not required.
- [ ] P03: repeated/concurrent Send, same-ID changed payload, cancel/complete race, expired/unknown state and quota boundaries preserve one reservation/model start per logical run across two service instances.
- [ ] P04: edit/publish saved content between turns; frozen prompts/tool definitions and language/history persist. New conversation sees new selection; no production grant/reset/write.
- [ ] P05: denied staff or foreign/missing revision fails before loading sensitive content; fixture/model credentials remain isolated and no WhatsApp/live-Shopify transport is constructed.
- [ ] P06: fail unavailable if loader/Redis/model config is absent; same-code default FIXTURE run works without paid credentials. Real Redis tests verify counters/locks/results/TTL, not merely Lua source text.

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

Expected execution branch: task/ARCH-020-COMMERCE-019. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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


### Readiness reconciliation after COMMERCE-013 Attempt 9 acceptance — 2026-09-21

Ready, Attempt 0 retained; executor/claimed_at null. COMMERCE-013 implementation
`4d52977` is architect accepted and all other explicit prerequisites are Complete.
No claim or automatic launch. Consume the actual backend via normal preparation.
Preserve native-basic monetary discount profiles as UNSUPPORTED while provider
rounding semantics are unproven; do not estimate savings or implement missing
provider semantics in this composition task. PostgreSQL adapter timeout diagnosis
and live infrastructure evidence remain separately developer-owned.


### Dependency correction — C20 fixture producer gap — 2026-09-21

**Blocked; Attempt 0 retained; executor/claimed_at null.** COMMERCE-018 Attempt 3
proved that the shared C20 persistent seed/reset helper assigned to the backend
producer is absent from accepted COMMERCE-013. C20 requires the same helper for
COMMERCE-019's real Redis/PostgreSQL preview integration evidence.

ARCH-020-COMMERCE-033 is now the explicit producer-correction task and is added as a
dependency. Do not claim COMMERCE-019 until 033 is architect-accepted Complete and
`moda_architect` returns this task to Ready. No 019 implementation or attempt is
started by this reconciliation.
