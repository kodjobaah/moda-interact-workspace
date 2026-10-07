---
id: ARCH-028-BACKGROUND-007
architecture_id: ARCH-028
title: Handle missing WhatsApp recipient without billing
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

# Handle missing WhatsApp recipient without billing

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Turn a missing/unusable recovery phone into an explicit zero-billing, zero-provider-call temporary block that can become eligible when later customer/recovery evidence supplies a usable number.

## Context

The current recovery initiator throws when no customer phone/test recipient exists. A person without a usable number today may have one later. Missing recipient is not the same as provider-confirmed recipient suppression.

## Scope

- Resolve recipient before creating an outreach attempt that requires a recipient and before recovery billing admission.
- If no usable customer recipient exists, set `CheckoutRecovery.admissionBlockReason = NO_WHATSAPP_RECIPIENT`, record `admissionBlockedAt`, and return a bounded non-error outcome.
- Do not create a UsageReservation/outbound message/provider call for that attempt.
- On later normal checkout/customer/recovery processing, if a usable recipient exists, clear the no-recipient block and proceed through the normal reachability gate/admission path.
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

## Work Items

- [ ] Replace missing-phone exception with bounded block outcome.
- [ ] Ensure no attempt requiring recipient/billing/provider send is created first.
- [ ] Add later-phone re-evaluation/clear path.
- [ ] Add focused tests.

## Interfaces / Contracts

Consumes DATABASE-001 `NO_WHATSAPP_RECIPIENT` and BACKGROUND-005 recipient preprocessing.

## Dependencies

- `ARCH-028-BACKGROUND-005`

## Enables

- `ARCH-028-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Missing recipient produces no billing reservation, outbound UsageEvent or Meta call.
- [ ] Recovery remains potentially actionable rather than permanently failed.
- [ ] Later usable recipient can continue normal admission.

## Validation

Focused recovery-initiation tests, full Background tests/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not conflate `NO_WHATSAPP_RECIPIENT` with `WHATSAPP_RECIPIENT_SUPPRESSED`; they have different recovery triggers.

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
