---
id: ARCH-020-COMMERCE-009
architecture_id: ARCH-020
title: Implement isolated preview lifecycle and execution service
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 130
executor: copilot
claimed_at: 2026-09-21T00:50:51Z
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-002
  - ARCH-020-SHARED-001
  - ARCH-020-COMMERCE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-010
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Implement isolated preview lifecycle and execution service

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own C9.1 preview routes, synthetic runner/tool execution, Redis state/replay/budgets and cancellation. No U14 visual components.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own C9.1 preview routes, synthetic runner/tool execution, Redis state/replay/budgets and cancellation. No U14 visual components.

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

- [ ] Implement every C9.1 route and strict body/status/ownership shape using accepted auth guards. Fixture mode requires no live provider/model; explicit model mode has separate credentials.
- [ ] Implement atomic environment/admin/run identity, creation replay, payload conflicts, conversation busy lock, 24h retention,20-turn/32k history, quotas and cancellation/UNKNOWN handling.
- [ ] Reuse the accepted Shared runner, C16 synthetic frozen response definition and C6.2 language/status fixtures. No production transcript/shop credential or WhatsApp admission.
- [ ] Use C19 PreviewBundleLoader against injected authorized synthetic bundle fixtures until013 supplies the real saved-bundle adapter. Unavailable production composition fails closed.
- [ ] Expose the exact service contract and controlled runner fixtures to017. Do not implement UI forms/navigation/screens or production publication/compiler services.

## Interfaces / Contracts

Own `src/commerce/preview/` and exact C9.1 route handlers under the accepted App Router root.017 owns U14;013 owns real saved-bundle composition. This backend task can be accepted with strict loader fixtures;013 must verify real service wiring.


## Dependencies

- ARCH-020-COMMERCE-002
- ARCH-020-SHARED-001
- ARCH-020-COMMERCE-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-010
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] P01: all C9.1 methods validate auth/owner/body and return exact statuses; other admin IDs leak no data.
- [ ] P02: cross-replica same-ID replay reserves one budget/model call; changed payload conflicts; distinct run IDs on one conversation reject before any start.
- [ ] P03: quotas, history/turn boundaries, cancellation/completion race, unknown/crash state, slot TTL and retained dedupe have explicit fake-clock assertions.
- [ ] P04: C6.2 language and C16 response cases use frozen synthetic state and the same runner version; later publication never expands the preview grant.
- [ ] P05: fixture output cannot send WhatsApp, access production providers or spend model quota; model mode never falls back to production keys.

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

Expected execution branch: task/ARCH-020-COMMERCE-009. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
