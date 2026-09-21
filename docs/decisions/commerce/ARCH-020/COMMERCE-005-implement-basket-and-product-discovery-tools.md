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
status: review
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

Ready for Review.

### Files Changed

- `moda-interact-commerce/src/commerce/query/index.ts`
- `moda-interact-commerce/tests/query-execution.test.ts`

### Work Completed

- Added the Commerce-owned `QueryExecutionPort` and injected bounded tokenless Storefront transport.
- Consumes the accepted `SHOPIFY_STOREFRONT_QUERY` definition/compiler, fixed `2026-07` API version, verified `*.myshopify.com` host, validated mapped variables, and schema-proved result path.
- Sends one request with a 10-second bound, shared request-budget reservation and cancellation signal; no retry, redirect, credential lookup or privileged fallback.
- Returns the unchanged C14 fact wrapper `{source, apiVersion, schemaHash, observedAt, values}` inside the Shared structured result union. Partial GraphQL errors, null projections, oversized responses and provider failures fail closed.
- Added deterministic injected fixtures for success, invalid host/variables/path, partial errors, null facts, oversized output, throttling, cancellation, expired deadline and exhausted request budget.

### Validation Results

Agent validation:

| Case | Fixture | Command | Result |
|---|---|---|---|
| Q01 valid authored query and fact wrapper | C14 wrapper success fixture | `npm test -- --run tests/query-execution.test.ts` | PASS, 4/4 |
| Q02 wrong host, malformed variables/path, partial errors, oversized response | invalid-input and partial/oversized fixtures | focused command above | PASS; invalid cases made zero provider calls |
| Q03 deadline, cancellation, request budget and provider errors | cancellation/budget/throttled fixtures | focused command above | PASS; no retry or late result |
| Q04 ordinary query facts, not policy evidence | structured wrapper assertion | focused command above | PASS; source/schema/version/observation preserved |
| lint | query module and tests | `npm run lint` | PASS |
| typecheck | repository after Prisma generation | `npm run typecheck` | PASS |
| build | production build and Prisma generation | `npm run build` | PASS |
| diff hygiene | scoped files | `git diff --check` | PASS |

Full `npm test`: 187 tests, 182 passed and 5 failed outside this task: two Prisma development-identity failures (`Prisma.sql is not a function`), two readiness child-process timing failures, and the Redis-backed discovery admission timeout. No failure involved the Commerce-005 files; focused tests remained 4/4 passing.

Developer validation required: execute against an approved development Shopify shop to confirm real tokenless `2026-07` provider behavior, redirect rejection, cancellation/timeout and GraphQL error handling. Fixture tests do not prove live provider behavior. Run environment/database/container readiness checks when developer-owned dependencies are available; this task performs no migrations.

### Deviations

The user request mentioned basket/product discovery broadly, but the authoritative narrowed task and C19 assign basket/search policy adapters to Commerce-015. This implementation therefore owns only generic query execution and does not add basket/search policy helpers or MCP routes. The five unrelated full-suite failures remain unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: `task/ARCH-020-COMMERCE-005`. Attempt: 1. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-005`; parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-005`. Recursive database submodule remained at recorded SHA `5abfd87f57038bae515aaa09ec7c8db62adcfb98`. Implementation and parent commits/pushes are recorded at submission. No main branch, parent service gitlink, architecture/index file or Architect Review text was modified; no enabled task was started.

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
