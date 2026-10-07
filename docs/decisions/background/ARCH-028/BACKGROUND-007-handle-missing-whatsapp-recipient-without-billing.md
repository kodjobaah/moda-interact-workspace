---
id: ARCH-028-BACKGROUND-007
architecture_id: ARCH-028
title: Defer recovery materialization when WhatsApp recipient is missing
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 74
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-005
enables:
  - ARCH-028-SYSTEM-TEST-001
created: 2026-10-07
updated: 2026-10-07
---

# Defer recovery materialization when WhatsApp recipient is missing

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Prevent `PendingRecoveryCandidate` materialisation into `CheckoutRecovery` when canonical Shop-scoped current-`CustomerPhone` resolution finds no usable recipient, while allowing a later `CHECKOUTS_UPDATE` to schedule a fresh candidate.

## Context

The current recovery initiator creates `CheckoutRecovery` before recipient resolution and then throws when no customer phone/test recipient exists. `PendingRecoveryCandidate` already represents a checkout that may later become recoverable, so a missing phone should stop materialisation before a durable recovery exists.

The fresh abandoned-checkout lookup may contain a phone that Customer resolution persists through `CustomerPhoneService`; otherwise an already-current Shop-scoped `CustomerPhone` may still exist. Only the absence of an active usable `CustomerPhone` after that resolution is a true missing-recipient outcome. `Customer.phone` is not authoritative.

## Scope

- At matured-candidate materialisation, use the fresh abandoned-checkout snapshot to resolve/update the Shop-scoped Customer and `CustomerPhone` history before deciding recipient availability.
- If no active usable current `CustomerPhone` exists, return a bounded `no-recipient`/deferred outcome **without creating `CheckoutRecovery`**, `RecoveryOutreachAttempt`, UsageReservation/UsageEvent, outbound message or provider call.
- Preserve the normal matured-candidate cleanup; do not keep a fake blocked recovery solely as a waiting record.
- When `CHECKOUTS_UPDATE` arrives and there is no pending candidate and no `CheckoutRecovery` for that Shop/checkout, schedule a fresh pending candidate using the update context; its maturity performs a new provider lookup and recipient check.
- If a current `CustomerPhone` exists even when `Customer.phone` is null/stale, treat the recipient as present and continue through BACKGROUND-005 reachability/admission.
- Do not add aggressive polling solely for missing phone.

## Out of Scope

- Recipient suppression TTL.
- Provider error classification.
- Synchronous failure.
- Merchant notification.

## Requirements

- [ ] Missing recipient is zero billing and zero provider work.
- [ ] It is not persisted as a permanent Customer property.
- [ ] Later usable phone can clear the block through normal processing.
- [ ] Test-only recipient behaviour remains explicitly development/test scoped and must not become production identity state.
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [ ] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [ ] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [ ] Move the missing-recipient decision to the pending-candidate materialisation boundary before `CheckoutRecovery` creation.
- [ ] Resolve/update Customer + current `CustomerPhone` from the fresh checkout snapshot and use current `CustomerPhone` as the authoritative source.
- [ ] Return a bounded deferred/no-recipient result without recovery/attempt/billing/provider state.
- [ ] Update `CHECKOUTS_UPDATE` handling so no-pending/no-recovery checkout updates schedule a fresh candidate rather than returning `recovery-not-found`.
- [ ] Ensure a null/stale `Customer.phone` does not block when an active `CustomerPhone` exists.
- [ ] Add focused tests.
- [ ] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes BACKGROUND-005 canonical current-`CustomerPhone` recipient resolution/reachability policy and the existing pending-candidate materialisation/update flow. No new database enum/state is required.

## Dependencies

- `ARCH-028-BACKGROUND-005`

## Enables

- `ARCH-028-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Missing recipient produces no `CheckoutRecovery`, outreach attempt, billing reservation, outbound UsageEvent/message or Meta call.
- [ ] Existing current `CustomerPhone` is honored even when `Customer.phone` is null/stale.
- [ ] A later `CHECKOUTS_UPDATE` with no pending candidate/recovery schedules a fresh candidate; if the subsequent fresh lookup resolves a usable phone, normal recovery materialisation/admission can proceed.
- [ ] No polling loop or durable no-recipient recovery block is introduced.
- [ ] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [ ] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [ ] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused recovery-initiation tests, full Background tests/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not conflate missing recipient with `WHATSAPP_RECIPIENT_SUPPRESSED`. Suppression is a durable policy block on a known recipient and may remain on a materialised recovery; missing recipient means there is no executable recovery yet.

Prefer a bounded candidate-materialisation recipient prerequisite and reuse existing Customer/CustomerPhone services. Keep the checkout-update rescheduling change thin; do not add another large missing-recipient branch directly to `recovery-initiation.service.ts` or the pending-candidate worker.

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
