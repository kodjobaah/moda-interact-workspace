---
id: ARCH-028-BACKGROUND-011
architecture_id: ARCH-028
title: Converge WhatsApp recipient reachability after correction and success
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-004
  - ARCH-028-BACKGROUND-010
enables:
  - ARCH-028-BACKGROUND-006
created: 2026-10-08
updated: 2026-10-08
---
# Converge WhatsApp recipient reachability after correction and success

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Upsert finite recipient suppression only after successful terminal delivery-failure release/compensation and clear it only on authoritative positive Shop-scoped evidence, preserving idempotency and chronological convergence.

## Context

BACKGROUND-004 reports durable generic correction (or a bounded deferred committed-purchased result). BACKGROUND-010 owns reads/admission. DATABASE-001 owns reachability state. BACKGROUND-005 captures the actual recipient at each attempt. This task owns reachability writes and positive clearing, not billing or pre-admission policy.

## Scope

- For terminal `131026` evidence associated to an exact message/attempt/recovery/Shop, upsert `(shopId, attempt.recipient)` failure metadata only once release/compensation has durably succeeded.
- Use `PlatformBillingPolicy.whatsappRecipientSuppressionDays` (default seven) and the provider failure time; preserve bounded code and CAS/version/concurrent monotonicity, avoiding stale failures overriding newer positive evidence.
- On a `DELIVERED` or `READ` message, clear suppression only for the exact Shop and attempt recipient; retain historical evidence for audit.
- On an inbound WhatsApp event, clear suppression only after existing routing establishes one concrete Shop/customer/conversation owner; never clear two Shops from a contextless phone number.
- Return stable bounded writer/clearing outcomes for BACKGROUND-006 and BACKGROUND-008; idempotent retries after corrected status are safe.

## Out of Scope

- Admission gating/resume (BACKGROUND-010).
- Provider status classification and generic compensation accounting (BACKGROUND-002/004).
- Committed purchased compensation strategy (BACKGROUND-009).
- Synchronous HTTP rejection integration (BACKGROUND-006).
- Merchant notification (BACKGROUND-008).

## Requirements

- [ ] The writer never suppresses on a deferred/failed COMMITTED purchased result before BACKGROUND-009 correction.
- [ ] The Shop is resolved from durable message/attempt/recovery lineage, not phone matching.
- [ ] Positive evidence cannot be reversed by an older failure replay; stronger positive evidence clears an earlier suppression.
- [ ] Default suppression length is seven days; policy changes affect new failure evidence without retroactive inference.
- [ ] Logs contain identifiers/outcomes, not raw provider bodies or full phone numbers.
- [ ] New production source files target <=200 lines and never exceed 300; do not build a catch-all service.

## Work Items

- [ ] Add focused idempotent reachability writer after accepted release/compensation result.
- [ ] Read configured duration and calculate finite suppression from failureAt.
- [ ] Clear suppression on exact delivered/read message and safely Shop-routed inbound evidence.
- [ ] Test concurrency, version races, replay, late positive status and two-Shop same-phone isolation.
- [ ] Expose bounded outcomes to synchronous parity/notification owners.

## Interfaces / Contracts

Consumes DATABASE-001 reachability/policy, immutable attempt recipient from BACKGROUND-005 and bounded correction outcomes from BACKGROUND-004/009. Provides finite suppression and positive-clear operations for the existing provider-status and inbound-message workflows; no new cross-service payload is introduced.

## Dependencies

- `ARCH-028-BACKGROUND-004`
- `ARCH-028-BACKGROUND-010`

## Enables

- `ARCH-028-BACKGROUND-006`

## Acceptance Criteria

- [ ] Corrected terminal recipient failure creates finite Shop/recipient suppression exactly once.
- [ ] Deferred/uncompensated purchased source creates no false suppression or notification-ready outcome.
- [ ] Duplicate or stale provider failure cannot override later positive evidence.
- [ ] Delivered/read or unambiguous inbound clears only the owning Shop/recipient.
- [ ] All touched modules respect focused responsibility/300-line production ceiling.

## Validation

Focused unit/PostgreSQL race/idempotency tests, provider-status replay, positive/inbound routing multi-Shop tests; repository-declared Background tests/build and `git diff --check`.

## Stop Condition

Complete defined work/acceptance/validation, fill the Completion Report, set status `review`, return to `moda_architect`, and STOP. Do not begin a dependent task.

## Implementation Notes

Keep separate modules for durable suppression writes and positive evidence clearing, with a thin integration point. Preserve the existing message/status transaction; do not call a provider or Redis inside the compensation transaction. Existing purchased correction is wired later by BACKGROUND-009.

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
