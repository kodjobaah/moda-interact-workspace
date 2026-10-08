---
id: ARCH-028-BACKGROUND-008
architecture_id: ARCH-028
title: Notify merchant after terminal delivery compensation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-006
enables:
  - ARCH-028-BACKGROUND-009
created: 2026-10-07
updated: 2026-10-07
---

# Notify merchant after terminal delivery compensation

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Create one deduplicated merchant SYSTEM support message for a terminally undelivered recovery only after the required release/compensation and reachability update have durably succeeded.

## Context

Merchant notification must never claim a credit was restored before accounting correction is true. Existing `MerchantSupportThread` / `MerchantSupportMessage.sourceKey` provides the notification mechanism and deduplication identity.

## Scope

- Define deterministic source key from the recovery/usage/message identity.
- Create/reuse merchant support thread and SYSTEM message after successful correction + suppression.
- Use platform-owned bounded wording.
- Wording must reflect actual result: spendable restoration, held/historical correction, or RESERVED release; never say spendable credit was restored for `HISTORICAL_ONLY`/`HELD_FOR_REFUND`.
- Notification retries are idempotent.
- Translation/rendering failure must not roll back completed compensation/suppression.

## Out of Scope

- New notification table/subsystem.
- Provider monetary refunds.
- Purchased compensation itself (BACKGROUND-009 integrates with this capability after its correction succeeds).

## Requirements

- [ ] Notification is last in terminal convergence ordering.
- [ ] Deterministic sourceKey prevents duplicates on provider-status/job retry.
- [ ] Merchant text does not expose provider payload/error details or phone number.
- [ ] No notification is created for deferred/failed compensation.
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [ ] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [ ] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [ ] Add deterministic source-key helper/policy message builder.
- [ ] Add generic async/sync notification integration after correction/suppression success.
- [ ] Add disposition-sensitive wording/tests.
- [ ] Add retry/dedup/translation-failure tests.
- [ ] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes existing Merchant Support persistence plus BACKGROUND compensation/reachability bounded outcomes.

## Dependencies

- `ARCH-028-BACKGROUND-006`

## Enables

- `ARCH-028-BACKGROUND-009`

## Acceptance Criteria

- [ ] Merchant never receives a false "credit restored" claim.
- [ ] Duplicate provider/job retries create at most one SYSTEM message.
- [ ] Completed financial correction is never rolled back because notification failed.
- [ ] Sync and async terminal paths use the same notification owner.
- [ ] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [ ] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [ ] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused merchant-support integration/unit tests, full Background tests/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Keep merchant wording platform-owned and bounded. Provider code may drive internal classification but should not be surfaced as raw provider diagnostics to the merchant.

Keep merchant-notification composition/deduplication separate from compensation and reachability policy. The notification owner should consume an already-resolved terminal outcome rather than recalculate financial state.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

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

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
