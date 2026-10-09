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
status: pending
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

- [ ] Add safe stage/reason metadata to MCP/host error boundaries.
- [ ] Correlate host error handling with runner output, while retaining stable host failure semantics.
- [ ] Test HTTP 401/403/429/5xx, invalid MCP result, stale/denied turn, unexpected host throw and sensitive-data omission.

## Interfaces / Contracts

Consumes the published Shared `RunCommerceTurnResult` diagnostic and canonical Shared logger. Does not change MCP wire schemas, response bodies, queue contracts or worker-facing failure code meaning.

## Dependencies

- `ARCH-029-SHARED-002`.

## Enables

- `ARCH-029-SYSTEM-TEST-001`.

## Acceptance Criteria

- [ ] Host/transport failure logs report actual known source stage/reason without raw payloads.
- [ ] Public codes/retryability and durable side effects remain unchanged.
- [ ] Existing tenant/authorization guards are intact; no unauthorized data exposure.
- [ ] A caller can correlate MCP and runner failures using existing turn/host identifiers.

## Validation

- [ ] Run focused Commerce host/MCP tests and relevant integration tests per repository scripts.
- [ ] Run repository typecheck and inspect emitted diagnostic records for privacy/size.
- [ ] Diff review for policy, retry and wire-contract changes.

## Stop Condition

Set `status: review`, finish Completion Report, return to `moda_architect` and STOP.

## Implementation Notes

Keep endpoint/provider specifics at the owning Background boundary. Safe error metadata can be conveyed internally while the public `CommerceHostError` contract remains stable. Do not turn a normal structured `DENIED` tool result into a provider exception.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
