---
id: ARCH-075-BACKGROUND-007
architecture_id: ARCH-075
title: Honor app-wide sample throttle before template intent
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-DATABASE-002
  - ARCH-075-BACKGROUND-006
enables:
  - ARCH-075-SYSTEM-TEST-002
created: 2026-11-13
updated: 2026-11-13
---

# Honor app-wide sample throttle before template intent

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Honor app-wide sample throttle before template intent.

## Context

Actual Meta sample_session HTTP403/code4 app request limit was classified as permanent blocked. One upload perlocale plus60second local polling and replica overlap can amplify calls; changing classification alone does not give durable cooldown. Existing scheduler leases/config/audit rows are not proper app-scoped lifecycle state. Generic historical rejection events do not carry code4 evidence.

## Scope

Existing sample error classifier, Meta preclaim submit/due path, dedicated app throttle repository/lease policy, bounded exact operator recovery for evidenced historical code4 blocks, related tests/docs and accepted Database gitlink adoption. No Shared release/cache.

## Out of Scope

Other repositories except explicit accepted submodule adoption, provider credentials/grants, live sends/repair/deployment, Shared publication, blind create retry, unsupported caching, generic refactors or implementation-source merges.

## Requirements

Recognize only evidenced numeric Meta code4 from structured provider403 sample_session/sample_upload response as app throttle (no English message substring). Other403 auth/permission rejections remain blocked. Preserve other existing provider error semantics unless directly necessary for safe preclaim deferral. Resolve trusted app/environment and acquire dedicated durable fenced lease BEFORE each sample operation;120seconds covers source fetch and both bounded HTTP phases. No network inside SQL transaction. Verify lease/app identity before sample HTTP, renew only under matching generation if needed; release/finish cannot clear newer ownership/cooldown. After code4, persist specific bounded evidence/reason and cooldown15min doubling to6h cap with saturated count, stop remaining same-app work across loops/replicas, and durably defer only still-unclaimed READY rows until permitted. Check future nextRetryAt and shared app gate before upload; newly created rows also respect cooldown. Genuine successful bounded sample operation may reset consecutive throttle count only under valid ownership, never override a later cooldown. Missing state/database failure is fail-closed for protected upload; no in-memory/Redis-only correctness gate. No singleflight/sample-handle reuse/cache without independently verified provider lifetime/scope (not authorized here). CREATE_INTENT/POST_INTENT/uncertain creates retain existing reconciliation/no-repost safety; never change submitted rows or approved snapshots. Historical generic REJECTED events lack durable code4 metadata: NEVER blanket-reset them. Root-only dry-run/apply operator capability may recover at most20 exact IDs per manifest only with explicit protected external403/code4 evidence digest/reference and truthful operator attestation, exact app/WABA/source/reviewer/updatedAt/transport fingerprint and zero prior claim/post/provider/unknown evidence, reusing existing preclaim guards compatibly. Preserve missing-app recovery behavior. Atomically audit recovery and seed/retain app cooldown (never shorten it or increment perlocale), make rows due no earlier than cooldown; no provider call/reset of history/attempts/unknown state. Live repair belongs to root after deployment/drain; task agent performs no live mutation. Internal policy bounds are conservative safety settings, not a provider guaranteed reset interval.

## Work Items

- [ ] Implement only the owning bounded outcome and final contract.
- [ ] Prove meaningful failure/concurrency/compatibility behavior.
- [ ] Complete mirrored report/checks, return review and stop.

## Interfaces / Contracts

Database002 owns durable Prisma/SQL state. Background007 consumes exact accepted schema and owns provider policy/leases/recovery; no new Shared contract. SystemTest002 is terminal validation. Root owns migration/deployment/operational evidence; no network inside transaction.

## Dependencies

ARCH-075-DATABASE-002, ARCH-075-BACKGROUND-006

## Enables

ARCH-075-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Assigned bounded capability/invariants and explicit negative behavior satisfied.
- [ ] Existing provider-intent, tenant/environment, immutable source and legacy lifecycle guards remain intact.
- [ ] Canonical matching physical isolation/sync and exact validation evidence reported; no live mutation.

## Validation

- [ ] Meaningful red/green classifier403/code4 vs auth403; units plus actual PostgreSQL concurrent replica lease, stale generation/reclaim, persistent cooldown/backoff saturation/expiry and future/new row gates, source-fetch/request deadline, duplicate completion and DB failure. Provider simulator proves no remaining same-app calls after throttle across cycles/replicas; intent/unknown POST never replayed. Exact historical recovery evidence/CAS/batch/replay/audit rollback negatives, no generic REJECTED reset. Relevant types/lint/build/exact-head full CI; no live provider calls.
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
