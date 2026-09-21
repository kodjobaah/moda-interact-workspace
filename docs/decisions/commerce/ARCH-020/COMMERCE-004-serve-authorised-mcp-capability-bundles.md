---
id: ARCH-020-COMMERCE-004
architecture_id: ARCH-020
title: Authenticate MCP requests and resolve immutable grants
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-003
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-010
  - ARCH-020-COMMERCE-014
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Authenticate MCP requests and resolve immutable grants

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own /api/mcp transport, assertion verification, durable ownership/grant reads and manifest/prompt/tool discovery. Inject definition execution through the C19 port.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own /api/mcp transport, assertion verification, durable ownership/grant reads and manifest/prompt/tool discovery. Inject definition execution through the C19 port.

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

- [ ] Implement the accepted001 Streamable HTTP profile, method/purpose matrix, request bounds and Origin rejection; no alternate endpoint.
- [ ] Validate C5 JWT algorithm/key/issuer/audience/subject/expiry/environment and durable Conversation -> Recovery -> Shop ownership, turn/lease and current original-provenance permission.
- [ ] Resolve candidate manifest, read/verify existing immutable grant, prompts and tool list. Background alone inserts grants; simulate its winner-write in transport fixtures.
- [ ] Produce server-only AuthorizedToolCall context with pinned definition and effective C8 limits; dispatch to injected DefinitionExecutionPort. Never execute operation mappings or templates here.
- [ ] Propagate typed C4/C5 failures and AbortSignal/deadline; return the C16 response contract/hash. Missing execution adapter is UNAVAILABLE, never a fake success.

## Interfaces / Contracts

Own `src/commerce/mcp/` and the existing /api/mcp entry. C19 AuthorizedToolCall/DefinitionExecutionPort separates004 transport from014 execution.013 installs the production014 adapter;004 acceptance uses a contract-faithful executor double.


## Dependencies

- ARCH-020-COMMERCE-003
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-010
- ARCH-020-COMMERCE-014
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] M01: resolve vs execute matrix, malformed JWT/Origin/body and mismatched tenant/turn deny before executor calls.
- [ ] M02: grant race fixture reads one winner; changed release/features never expand existing discovery; exact names/versions and zero-tools result are preserved.
- [ ] M03: revocation across replicas and conflicting original-association bounds enforce C8 minima; newly added association cannot grant authority.
- [ ] M04: pinned authorized call reaches the injected executor once with trusted context; ungranted/wrong revision reaches it zero times; execute failure is encoded by the accepted profile.

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

Expected execution branch: task/ARCH-020-COMMERCE-004. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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

COMMERCE-003 Attempt 4 and SHARED-001 are architect-accepted Complete.
Promoted to Ready on the COMMERCE-003 acceptance branch; attempt and claim remain unchanged.
Normal task preparation owns materialisation, synchronization and the next claim.
