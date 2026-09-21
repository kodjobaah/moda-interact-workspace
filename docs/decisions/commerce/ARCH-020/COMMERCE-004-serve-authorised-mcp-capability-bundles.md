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
status: review
priority: 80
executor: copilot
claimed_at: 2026-09-21T01:25:13Z
attempt: 1
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

- [x] Implement the accepted001 Streamable HTTP profile, method/purpose matrix, request bounds and Origin rejection; no alternate endpoint.
- [x] Validate C5 JWT algorithm/key/issuer/audience/subject/expiry/environment and durable Conversation -> Recovery -> Shop ownership, turn/lease and current original-provenance permission.
- [x] Resolve candidate manifest, read/verify existing immutable grant, prompts and tool list. Background alone inserts grants; simulate its winner-write in transport fixtures.
- [x] Produce server-only AuthorizedToolCall context with pinned definition and effective C8 limits; dispatch to injected DefinitionExecutionPort. Never execute operation mappings or templates here.
- [x] Propagate typed C4/C5 failures and AbortSignal/deadline; return the C16 response contract/hash. Missing execution adapter is UNAVAILABLE, never a fake success.

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

- [x] M01: resolve vs execute matrix, malformed JWT/Origin/body and mismatched tenant/turn deny before executor calls.
- [x] M02: grant race fixture reads one winner; changed release/features never expand existing discovery; exact names/versions and zero-tools result are preserved.
- [x] M03: revocation across replicas and conflicting original-association bounds enforce C8 minima; newly added association cannot grant authority.
- [x] M04: pinned authorized call reaches the injected executor once with trusted context; ungranted/wrong revision reaches it zero times; execute failure is encoded by the accepted profile.

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

Implementation branch `task/ARCH-020-COMMERCE-004`, commit `c97a85be3a1561adca06eb03577dd84ad30ed306`:

- `package.json`, `package-lock.json`
- `app/api/mcp/route.ts`
- `src/commerce/mcp/authentication.ts`
- `src/commerce/mcp/ports.ts`
- `src/commerce/mcp/service.ts`
- `tests/mcp-service.test.ts`
- `tests/auth-entrypoints.test.ts`

### Work Completed

Implemented the private `/api/mcp` POST transport with Origin/content/body bounds,
JSON-RPC validation, resolve/execute method-purpose authorization, RS256 JWT
verification, tenant/turn/grant/release/expiry checks, immutable manifest and
response-contract hash checks, bounded discovery, prompt retrieval, and
server-only `AuthorizedToolCall` dispatch through the injected
`DefinitionExecutionPort`. Missing runtime adapters fail closed as
`UNAVAILABLE`; execution results are schema-validated and encoded in the MCP
response contract. Deterministic fixtures cover deny-before-executor,
revocation, expiry, stale tenant/turn, exact pinned revision, malformed input,
origin rejection, and JWT verification. The stale entry-point test now asserts
that the required MCP route is private rather than absent.

Requirement-to-fixture matrix:

| Requirement | Fixture/test | Expected and observed effect |
| --- | --- | --- |
| M01 | `tests/mcp-service.test.ts`: resolve/execute matrix; origin, batch, params and argument bounds; JWT verifier | Resolve discovery succeeds, resolve execution and malformed/Origin inputs deny, executor calls remain zero, and RS256 issuer/audience/subject/kid/purpose/lifetime checks pass. |
| M02 | `tests/mcp-service.test.ts`: exact pinned revision, manifest contract hash, zero-tool fixture | Only the granted tool whose name/version/revision match the immutable definition is listed/callable; bad contract denies before discovery and zero-tool discovery remains empty. |
| M03 | `tests/mcp-service.test.ts`: tenant/turn mismatch, release mismatch, expiry and revocation mutations | Stale turn, wrong release, expired grant and revoked tool deny; no executor call occurs. Authorization is re-read for each request through the injected port. |
| M04 | `tests/mcp-service.test.ts`: pinned `tools/call` executor double and denied-call assertions | One authorized call reaches the executor with pinned grant/release context; denied or revoked calls reach it zero times; typed execution failures map to unavailable/error responses. |

### Validation Results

Agent-owned checks:

- `npm test -- --run tests/auth-entrypoints.test.ts tests/mcp-service.test.ts tests/mcp-compatibility.test.ts` -> passed, 3 files / 13 tests.
- `npm run lint` -> passed.
- `npm run typecheck` -> passed after the build regenerated Prisma Client.
- `npm run build` -> passed; Prisma Client generated from `database/prisma/schema.prisma`, Next.js compiled, and `/api/mcp` was included as a dynamic route.
- `npm test` -> 20 files passed, 150 tests passed; one Redis-backed test failed by timeout: `tests/discovery-limits.test.ts` requires `REDIS_URL` and timed out after 30 seconds. No MCP test failed.
- `git diff --check` -> passed.
- `git submodule status --recursive` -> database submodule at recorded SHA `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.

Developer-owned live/integration validation remains pending: run
`REDIS_URL=<developer Redis> npm test -- --run tests/discovery-limits.test.ts`
and the live Background-signed assertion plus production execution-adapter/system
integration checks in the developer environment. Fixture tests do not prove live
issuer keys, network admission, Redis, database, provider, or deployment behavior.

### Deviations

The existing `tests/auth-entrypoints.test.ts` expected no `/api/mcp` route from a pre-task baseline; it was updated to assert the required private route. Full validation retains one unrelated Redis timeout as pending developer evidence.

### Assumptions

The accepted Shared commerce contracts and the recorded database submodule SHA are authoritative. The injected authorization/execution ports represent the C19 composition boundary; production adapter wiring remains with its owning task.

### Unresolved Issues

Live Redis-backed discovery validation is unavailable in this agent worktree and
must be run by the developer with configured infrastructure. No implementation
blocker remains for the bounded Commerce-004 scope.

### Architectural Concerns

None newly reported.

### Git / VCS

Status: Ready for Review. Attempt: 1. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-004`, branch `task/ARCH-020-COMMERCE-004`, pushed commit `c97a85be3a1561adca06eb03577dd84ad30ed306`. Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-004`, branch `task/ARCH-020-COMMERCE-004`, based on pushed claim `1b1258f664eeb3f6c834d24f6fc68aeec17fb499`; this report update is the next parent task commit. The recursive database submodule remained at recorded SHA `5abfd87f57038bae515aaa09ec7c8db62adcfb98`. No parent service gitlink or main branch integration was performed.

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
