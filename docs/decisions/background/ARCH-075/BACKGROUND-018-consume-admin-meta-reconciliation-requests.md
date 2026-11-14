---
id: ARCH-075-BACKGROUND-018
architecture_id: ARCH-075
title: Consume durable Admin Meta reconciliation requests
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T16:02:08Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Consume durable Admin Meta reconciliation requests

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Make the existing Admin reconciliation command durably consumable by the bounded Background timer.

## Context

Normal UI requests remain unprocessed until six-hour scheduling because listDue ignores Admin requests. Root identified actual pending receipts during current rollout. Necessary fix separate from frozen NBSP task.

## Scope

Background owning repository discovery/service/status receipt handling and focused unit/disposable database tests.

## Out of Scope

Admin UI changes, provider submission/registration/activation, Shared/schema/newqueue, manual DB flags, main/live operations.

## Requirements

Existing Admin requestMetaReconciliation writes source ADMIN/eventType RECONCILE_REQUESTED/processedAt null with registration/sender/provider identity and submitted requestDigest. Current bounded timer discovery ignores these and status repository consumes only webhook receipts. Add bounded discovery/handling of eligible pending Admin receipts through EXISTING reconcileRegistration and registration lease/CAS/provider status validation. No provider submission/resend path for an Admin reconcile request. Validate selected receipt registration/WABA/provider name/language/id and frozen submitted hash; stale/malformed identity cannot authorize refresh or be called success. Mark EXACT handled receipt IDs processed atomically with successful authoritative reconciliation where possible; do not consume a newer concurrent request never covered by that observation. Preserve retry/backoff on provider unavailable/busy/stale lease, pending receipt durability and no double-click flood. Concurrent workers must not issue duplicate Graph work beyond existing lease semantics; tests prove one winner/idempotent replay. Keep bounded limit/order fairness and no network inside SQL transaction. Reuse existing worker timer/no new queue/event/table/config/Shared release. Root accepted separate BG017 equivalence fix; this task does not change it or block its deployment. If BG017 main merges meanwhile sync accepted main before final checks, preserve both status event changes. Root service-only canary may occur independently, but old Admin requests remain durable until this consumer handles them.

## Work Items

- [ ] Add bounded eligible Admin request discovery and existing-service execution.
- [ ] Preserve exact receipt identity/CAS/lease/retry lifecycle.
- [ ] Add concurrency/idempotency/stale/failure/newer-request regressions.
- [ ] Record exact isolated source/check/report.

## Interfaces / Contracts

Existing database WhatsAppTemplateMetaEvent ADMIN RECONCILE_REQUESTED receipt and existing provider reconciliation service; no wire/schema change.

## Dependencies

None; existing service and Admin producer already integrated. Accepted BG017 main must be preserved if it merges before final validation.

## Enables

Normal root UI reconciliation without operator service fallback.

## Acceptance Criteria

- [ ] Pending valid UI request refreshes through normal timer without waiting six-hour due schedule or submitting template.
- [ ] Exact covered receipt processed; newer/stale/malformed requests not falsely consumed.
- [ ] Lease/concurrent/replay/provider failure/backoff failclosed and retry durable.
- [ ] Required checks/report complete; no liveops.

## Validation

- [ ] Focused actual timer/repository/service tests.
- [ ] Disposable PG actual Admin-shaped receipt→normal consumer→authoritative status+processed receipt, concurrency/newer receipt/providerfailure cases.
- [ ] Types/build/scopedlint/exact remote CI and diff/privacy; no unrelated broad local repeat.

## Stop Condition

After checks publish source and matching parent report, set review and STOP. Root owns merge/live.

## Implementation Notes

Normal moda-task canonical sibling worktrees/claim. You are not alone; BG017 owner edits same status repository/service on another branch. Coordinate narrowly, preserve changes, sync accepted main before final. No hidden direct field patching or provider network in SQL.

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

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual code

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Root normal UI verification
