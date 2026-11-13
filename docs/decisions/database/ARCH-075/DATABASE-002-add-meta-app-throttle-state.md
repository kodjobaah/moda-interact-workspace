---
id: ARCH-075-DATABASE-002
architecture_id: ARCH-075
title: Add durable Meta app sample throttle state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 5
executor: codex
claimed_at: 2026-11-13T11:03:20Z
attempt: 1
depends_on:
  - ARCH-075-DATABASE-001
enables:
  - ARCH-075-BACKGROUND-007
created: 2026-11-13
updated: 2026-11-13
---

# Add durable Meta app sample throttle state

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Add durable Meta app sample throttle state.

## Context

Actual Meta sample_session HTTP403/code4 app request limit was classified as permanent blocked. One upload perlocale plus60second local polling and replica overlap can amplify calls; changing classification alone does not give durable cooldown. Existing scheduler leases/config/audit rows are not proper app-scoped lifecycle state. Generic historical rejection events do not carry code4 evidence.

## Scope

Additive Prisma model/migration/constraints and focused ERD/documentation for one app-scoped sample-operation cooldown/lease row. No application behavior, provider calls or existing state rewrite.

## Out of Scope

Other repositories except explicit accepted submodule adoption, provider credentials/grants, live sends/repair/deployment, Shared publication, blind create retry, unsupported caching, generic refactors or implementation-source merges.

## Requirements

Dedicated whatsapp.MetaTemplateAppOperationState keyed by existing CommerceEnvironment plus appId (numeric1..32), not tenant/WABA: app quota spans those scopes. Fields: cooldownUntil nullable timestamp, consecutiveThrottleCount nonnegative bounded saturating integer, lastThrottleAt nullable, lease owner token/generation/acquiredAt/leaseUntil with coherent nullable tuple, updatedAt. Use owner/generation fencing and monotonic generation; no secret/token payload. Exact field names may follow repository conventions but publish the final shape before consumer execution. One lease covers ONE bounded sample operation,120seconds; app backoff first15minutes, doubles to6hour cap. Database supplies invariant storage; Background owns timing/policy. A cooldown cannot be removed/shortened by stale owner completion; expired ownership can be reclaimed only with new generation. PK supports point lookup; add only indexes needed by actual queries, not speculative scans. Preserve existing tables/records and reversible compatible rollout. No reuse of scheduler enum/config/audit JSON.

## Work Items

- [ ] Implement only the owning bounded outcome and final contract.
- [ ] Prove meaningful failure/concurrency/compatibility behavior.
- [ ] Complete mirrored report/checks, return review and stop.

## Interfaces / Contracts

Database002 owns durable Prisma/SQL state. Background007 consumes exact accepted schema and owns provider policy/leases/recovery; no new Shared contract. SystemTest002 is terminal validation. Root owns migration/deployment/operational evidence; no network inside transaction.

## Dependencies

ARCH-075-DATABASE-001

## Enables

ARCH-075-BACKGROUND-007

## Acceptance Criteria

- [ ] Assigned bounded capability/invariants and explicit negative behavior satisfied.
- [ ] Existing provider-intent, tenant/environment, immutable source and legacy lifecycle guards remain intact.
- [ ] Canonical matching physical isolation/sync and exact validation evidence reported; no live mutation.

## Validation

- [ ] Real PostgreSQL fresh+populated-upgrade migration, duplicate app identity, environment separation, lease tuple/nonnegative/generation and stale-owner invariants; generated Prisma/types/static checks and focused ERD. No unrelated baseline diagram/history repair.
- [ ] Diff/privacy hygiene; no secrets/private production identifiers or unsupported capability claim.

## Stop Condition

When scope/checks complete, submit Completion Report/status review and STOP. No enabled task, source merge, hosted migration or live recovery/provider action.

## Implementation Notes

You are not alone; preserve other work. Canonical launcher packet owns start/claim. Root owns all final merges, test/prod migration, worker rollout/drain and protected live evidence. New domain logs reuse published Shared logging; do not duplicate generic telemetry. Return genuine contract gaps before widening scope.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

No provider reset guarantee; timing bounds are explicit internal policy.

### Unresolved Issues

None currently.

### Architectural Concerns

Return actual cross-owner gaps before workaround.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
