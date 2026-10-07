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

## Work Items

- [ ] Add deterministic source-key helper/policy message builder.
- [ ] Add generic async/sync notification integration after correction/suppression success.
- [ ] Add disposition-sensitive wording/tests.
- [ ] Add retry/dedup/translation-failure tests.

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

## Validation

Focused merchant-support integration/unit tests, full Background tests/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Keep merchant wording platform-owned and bounded. Provider code may drive internal classification but should not be surfaced as raw provider diagnostics to the merchant.

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
