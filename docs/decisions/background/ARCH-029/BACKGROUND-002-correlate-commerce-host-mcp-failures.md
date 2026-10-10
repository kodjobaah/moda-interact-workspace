---
id: ARCH-029-BACKGROUND-002
architecture_id: ARCH-029
title: Correlate Commerce host and MCP failure origins
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-029-SHARED-002
enables:
  - ARCH-029-SYSTEM-TEST-001
created: 2026-10-10
updated: 2026-10-10
---

# Correlate Commerce host and MCP failure origins

## Architecture

Architecture ID: `ARCH-029`.

Architecture document: `docs/architecture/ARCH-029-commerce-runner-failure-diagnostics.md`.

Coordinator: `moda_architect`.

## Objective

Make Background Commerce host failures identifiable as MCP transport, manifest/tool contract, authorization, stale-turn or host failures without changing public host failure/retry semantics.

## Context

`src/commerce/mcp-client.ts` uses generic `CommerceHostError` for multiple stages and collapses non-2xx HTTP into `UNAVAILABLE`; `src/commerce/host.ts` converts runner and unexpected failures into a code-only `CommerceHostError`. Existing useful cause/context is discarded, making failures difficult to correlate to `commerce.turn.failed` records.

## Scope

Only `moda-interact-background` host/MCP diagnostic code and focused tests; expected files `src/commerce/mcp-client.ts`, `src/commerce/host.ts`, and tests. Use the published Shared diagnostic/structured logging interface. Do not change Shared or Commerce source.

## Out of Scope

- Model/provider/credential factory changes (BACKGROUND-001).
- MCP protocol/SDK or authentication redesign.
- Altering HTTP retries, timeouts, grant matching, evidence refresh or tenant authorization.
- Passing raw exception messages, MCP content or request/response bodies to logs or the customer.

## Requirements

1. Distinguish bounded stages: configuration, MCP connection, manifest resource, tool listing, authorization, tool invocation, tool response validation, host lifecycle and final result conversion.
2. Preserve `CommerceHostError.code` and `.retryable` behaviour and attach safe finite stage/reason metadata where needed. For HTTP failures record safe numeric status and operation kind, not endpoint credentials or response bodies.
3. Avoid losing Shared runner diagnostic fields when converting `RunCommerceTurnResult` to a host error. Emit a correlated host diagnostic while preserving existing worker error handling and no customer diagnostic exposure.
4. Preserve `STALE_TURN`, `DENIED`, deadline and cancellation identity; if a host-supplied exception occurs during runner-bound work, ensure the Shared runner terminal event identifies the host stage rather than only `UNAVAILABLE`.
5. Logging failures are isolated, no new remote calls/retries/metrics.

## Work Items

- [x] Add safe stage/reason metadata to MCP/host error boundaries.
- [x] Correlate host error handling with runner output, while retaining stable host failure semantics.
- [x] Test HTTP 401/403/429/5xx, invalid MCP result, stale/denied turn, unexpected host throw and sensitive-data omission.

## Interfaces / Contracts

Consumes the published Shared `RunCommerceTurnResult` diagnostic and canonical Shared logger. Does not change MCP wire schemas, response bodies, queue contracts or worker-facing failure code meaning.

## Dependencies

- `ARCH-029-SHARED-002`.

## Enables

- `ARCH-029-SYSTEM-TEST-001`.

## Acceptance Criteria

- [x] Host/transport failure logs report actual known source stage/reason without raw payloads.
- [x] Public codes/retryability and durable side effects remain unchanged.
- [x] Existing tenant/authorization guards are intact; no unauthorized data exposure.
- [x] A caller can correlate MCP and runner failures using existing turn/host identifiers.

## Validation

- [x] Run focused Commerce host/MCP tests and relevant integration tests per repository scripts.
- [x] Run repository typecheck and inspect emitted diagnostic records for privacy/size.
- [x] Diff review for policy, retry and wire-contract changes.

## Stop Condition

Set `status: review`, finish Completion Report, return to `moda_architect` and STOP.

## Implementation Notes

Keep endpoint/provider specifics at the owning Background boundary. Safe error metadata can be conveyed internally while the public `CommerceHostError` contract remains stable. Do not turn a normal structured `DENIED` tool result into a provider exception.

## Completion Report

### Status

Ready for Review — retrospective record of the manually applied patch workflow.

### Files Changed

- src/commerce/host-diagnostics.ts (new)
- src/commerce/host.ts
- src/commerce/mcp-client.ts
- tests/unit/commerce/host-diagnostics.test.ts (new)
- tests/integration/commerce/host.test.ts

### Work Completed

- Added bounded, human-readable MCP transport/HTTP/status and Commerce host diagnostic classifications without changing public code/retry contracts.
- Propagated the Shared runner failure stage/reason through the host and correlated terminal logs with existing turn identifiers.
- Added focused tests covering HTTP 401/403/429/5xx, malformed MCP results, stale/denied turns and failure-isolated logging.

### Validation Results

- The developer confirmed “all green” after being provided focused Vitest, Background build and unit suite commands; no detailed terminal output was supplied for this task.
- The implementation patch passed fresh-snapshot `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all` and `git diff --check` and isolated diagnostic checks in the earlier patch preparation.
- Local detailed test counts and two-worktree validation provenance were not independently available.

### Deviations

- This work was delivered as an external `.patch` plus ZIP for developer application; local application/validation is evidenced only where separately recorded below. It did not follow the repository agent launcher/dual dedicated task-worktree submission process.
- The uploaded snapshot contains no launcher execution packet, two-worktree isolation/synchronisation evidence, pushed task branches, implementation commit IDs or parent-task review commits. These have **not** been invented or certified. This is a developer-directed administrative closeout exception, not a conforming claim under `docs/agent-worktree-isolation-policy.md`.

### Assumptions

- The user’s “all green” refers to BACKGROUND-002 focused tests, build and complete unit test commands issued immediately before that confirmation.

### Unresolved Issues

- Detailed local validation output and physical worktree/synchronisation evidence remain unavailable.

### Architectural Concerns

- No new HTTP retries or MCP payload/wire-schema changes were intended.

## Architect Review

### Review Status

Accepted — developer-directed closeout with the evidence limitations explicitly recorded below.

### Review Notes

- Developer confirmation indicates all requested local checks passed. Maintained the explicit distinction between the observed confirmation and independently replayed tests.

### Reviewed Files

- src/commerce/host-diagnostics.ts (new)
- src/commerce/host.ts
- src/commerce/mcp-client.ts
- tests/unit/commerce/host-diagnostics.test.ts (new)
- tests/integration/commerce/host.test.ts

### Validation Reviewed

- The developer confirmed “all green” after being provided focused Vitest, Background build and unit suite commands; no detailed terminal output was supplied for this task.
- The implementation patch passed fresh-snapshot `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all` and `git diff --check` and isolated diagnostic checks in the earlier patch preparation.
- Local detailed test counts and two-worktree validation provenance were not independently available.

### Architecture Conformance

- MCP host log diagnostics now have bounded stage/reason and preserve stable public codes, without adding wire-contract changes.
- Formal worktree-isolation compliance not established by the archive.

### Follow-up

- Independent system-test verification proceeds in the existing system-test project, not in this task closeout.
