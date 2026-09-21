---
id: ARCH-020-COMMERCE-014
architecture_id: ARCH-020
title: Execute and render pinned tool definitions
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 85
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-004
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-21
updated: 2026-09-21
---

# Execute and render pinned tool definitions

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own C14 input validation, mappings, operation dispatch and safe response templates behind the authenticated MCP port.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own C14 input validation, mappings, operation dispatch and safe response templates behind the authenticated MCP port.

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

- [x] Implement DefinitionExecutionPort from C19 against the exact pinned C14 execution union; never select latest, infer business handlers from tool names or mutate a process-global tenant registry.
- [x] Validate authored input schema and mappings/literals before provider work; dispatch QueryExecutionPort or versioned policy registry with trusted context injected server-side.
- [x] Implement bounded text/items renderer, allowed tokens and null/empty/unavailable/error behavior; no expressions, eval, recursive interpolation or hidden I/O.
- [x] Preserve structured policy Evidence and public-query wrapper separation under C18; rendering cannot promote UNKNOWN or counterfeit facts.
- [x] Use injected query/policy adapters for component acceptance.013 owns production registration;014 does not implement provider retrieval, pricing or discount logic.

## Interfaces / Contracts

Own `src/commerce/execution/`. Import004 context types; do not edit its authorizer. Implement query/policy ports with fixtures here;013 installs real005/015/006/016/007 providers.


## Dependencies

- ARCH-020-COMMERCE-004
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [x] E01: renamed/narrowed/literal tools dispatch the exact version and arguments once; bad mapping/schema/absent operation dispatches zero times.
- [x] E02: two shops/concurrent calls share no mutable context; deadline/cancellation propagate; missing adapter is typed UNAVAILABLE.
- [x] E03: template null/empty/overflow/error/injection cases obey C14, keep structured data unchanged and never evaluate provider text as a template.
- [x] E04: C18 EC07/EC08 output provenance/authorization cases hold through the full definition executor.

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

Ready for Review. Attempt 1 implementation and agent-owned validation are complete.

### Files Changed

- `src/commerce/execution/executor.ts`
- `src/commerce/execution/index.ts`
- `src/commerce/execution/ports.ts`
- `src/commerce/execution/renderer.ts`
- `tests/definition-execution.test.ts`
- `tests/definition-execution-mcp.test.ts`

### Work Completed

- Implemented the C19 `DefinitionExecutionPort`, injected `QueryExecutionPort`, and immutable exact-version `PolicyOperationRegistry`.
- Validated authored input schemas and Shared argument mappings before dispatch, including renamed, narrowed, and literal mappings.
- Added exact policy operation/version dispatch and fail-closed `UNAVAILABLE` behavior for missing adapters.
- Added bounded scalar and item rendering with strict token grammar, safe own-property traversal, fixed null/empty/error output, and no recursive interpolation.
- Preserved structured policy evidence and kept public query facts inside the C18 provenance wrapper.
- Propagated trusted context, cancellation, and deadlines without process-global tenant state.

### Validation Results

Agent-owned checks:

- E01 — renamed query fixture, exact policy-version fixture, malformed schema/mapping and absent-operation fixtures — `npx vitest run tests/definition-execution.test.ts tests/definition-execution-mcp.test.ts --reporter=verbose` — 11/11 tests passed; valid calls dispatched once with exact mapped arguments, invalid calls dispatched zero times.
- E02 — concurrent two-shop fixture, cancellation/deadline fixtures and missing-adapter fixtures — same focused command — passed; contexts remained distinct, pre-cancelled/expired calls dispatched zero times, post-dispatch expiry failed closed, and missing adapters returned typed `UNAVAILABLE`.
- E03 — null, empty-item, item-limit, oversized structured result, provider error and injected-template fixtures — same focused command — passed; output stayed bounded, item limiting affected rendered text only, structured data was unchanged, and provider text was not recursively evaluated.
- E04 — valid/malformed evidence, counterfeit public-query evidence, stale authority and revoked authority fixtures through `createMcpService` — same focused command — passed; valid evidence was preserved, malformed policy evidence was rejected, public data remained wrapped, and denied authority reached the provider zero times.
- `npm run lint` — passed.
- `npm run typecheck` — passed after repository-standard Prisma generation.
- `npm run build` — passed; the production Next build includes the dynamic `/api/mcp` route.
- Full `npm test` — 31/33 files and 270/273 tests passed. The task-owned suites passed. `tests/discovery-limits.test.ts` timed out waiting for its configured Redis-backed environment. Two `tests/readiness-docker.test.ts` process-tree setup barriers failed under the 33-worker full-suite load.
- `npx vitest run tests/readiness-docker.test.ts` — 9/10 passed; the abort case missed its setup barrier in the grouped run.
- The readiness abort case run alone — 1/1 passed.
- Full non-infrastructure suite excluding `discovery-limits.test.ts` and `readiness-docker.test.ts` — 31 files and 262 tests passed.
- `git diff --check` — passed.

No live provider, database, or container validation is required by this definition-execution component task. The Redis-backed discovery test remains environment-dependent evidence rather than a task-owned product failure.

### Deviations

No implementation-scope deviation. Production provider registration remains with COMMERCE-013 as required. Full-suite infrastructure-sensitive failures are recorded above without weakening task-owned acceptance.

### Assumptions

The accepted COMMERCE-004 and SHARED-001 contracts are authoritative. Query providers return the C14 storefront-facts wrapper and policy adapters return their exact Shared output schema. COMMERCE-013 will install production adapters without changing this execution boundary.

### Unresolved Issues

The configured Redis-backed discovery suite needs its expected local service to produce live infrastructure evidence. The process-tree readiness abort case is sensitive to full-suite concurrency but passed alone. Neither condition changes the scoped C14/C18 acceptance result.

### Architectural Concerns

None. The implementation preserves the C19 ownership boundary and leaves production adapter composition to COMMERCE-013.

### Git / VCS

Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.

Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-014` on `task/ARCH-020-COMMERCE-014`.

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-014` on `task/ARCH-020-COMMERCE-014`, prepared from accepted source `0aa3a7be8472d9d1325ade395ce20d63fc128d4f`.

Launcher preparation synchronized the registered repository and recursively initialized the accepted database submodule at `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.

Implementation commit `232cbdd` (`feat(commerce): execute pinned tool definitions`) is pushed to `origin/task/ARCH-020-COMMERCE-014`. The parent report commit and push are recorded by the submission commit containing this report. No parent service gitlink update or main integration was performed.

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

Ready, Attempt 0, executor/claimed_at null. COMMERCE-004 is architect-accepted
Complete at Attempt 3 (`0411babc`); SHARED-001 is already accepted Complete.
All explicit prerequisites are satisfied. Normal preparation owns the next claim
and approved accepted-source consumption. Retain C19's definition-execution port
boundary;013 owns production composition. No task is launched by this promotion.
