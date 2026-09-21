---
id: ARCH-020-COMMERCE-005
architecture_id: ARCH-020
title: Execute validated public Shopify queries
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 90
executor: copilot
claimed_at: 2026-09-21T02:31:47Z
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-001
  - ARCH-020-COMMERCE-011
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Execute validated public Shopify queries

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own tokenless execution of immutable SHOPIFY_STOREFRONT_QUERY definitions and schema-bound result projection only.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own tokenless execution of immutable SHOPIFY_STOREFRONT_QUERY definitions and schema-bound result projection only.

## Out of Scope

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
Do not implement missing dependencies or substitute production fixtures to finish.

## Requirements

Use accepted auth/Shared/database source, canonical types and C19 ports. Preserve
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.

## Work Items

- [ ] Consume011 actual pinned compiler/schema exports; execute the fixed published query and mapped variables only against the verified canonical shop host.
- [ ] Enforce C14 query/depth/list/time/response bounds and API-version checks. Reject partial GraphQL errors; no privileged fallback or installation-token lookup.
- [ ] Preserve the query fact wrapper including source/schema/version/observedAt/values; selected values can never replace it with a policy-evidence output.
- [ ] Expose QueryExecutionPort to014 with injected bounded provider transport, clock and signal. Do not implement basket/search policy helpers or MCP routes.

## Interfaces / Contracts

Own `src/commerce/query/`. C19 QueryExecutionPort receives trusted context and the canonical query definition;013 connects it to014. C14 result wrapper and Shared types remain unchanged.


## Dependencies

- ARCH-020-COMMERCE-001
- ARCH-020-COMMERCE-011
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Q01: two arbitrary authored queries execute without registering business names; mapped variables/results match the accepted compiler.
- [ ] Q02: wrong host, query/version, malformed variables/projection, partial errors and oversized response fail closed; zero credentials looked up on every path.
- [ ] Q03: timeout/throttle/cancel/count limits are honored; no redirect to unverified host or mutation is emitted.
- [ ] Q04: nested counterfeit evidence remains ordinary query values; no policy-shaped root output.

## Validation

Implement the named cases above as focused tests. Record case -> fixture -> command
-> expected/actual effects in the Completion Report. Check shared contract examples
where applicable; include malformed and denied inputs with zero side effects.
Run focused tests while developing, then typecheck/lint/build once before submission;
repeat broader checks only for new failures or changed concerns. Use actual repository
commands and record them. Local browser/component evidence is task-owned where a UI
is in scope. Follow agent-validation/live-validation policies; separate pending
required developer database/container evidence and never claim fixture tests prove
live service behavior. No minimum screenshot/test count substitutes for coverage.

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

Expected execution branch: task/ARCH-020-COMMERCE-005. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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

## Architect readiness reconciliation — 2026-09-21

COMMERCE-001, COMMERCE-011 Attempt 9 and SHARED-001 are architect-accepted Complete.
Promoted to Ready on the COMMERCE-011 acceptance branch; attempt and claim remain unchanged.
Normal task preparation owns materialisation, synchronization and the next claim.
