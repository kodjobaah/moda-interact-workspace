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
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [ ] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [ ] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [ ] Replace missing-phone exception with bounded block outcome.
- [ ] Ensure no attempt requiring recipient/billing/provider send is created first.
- [ ] Add later-phone re-evaluation/clear path.
- [ ] Add focused tests.
- [ ] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

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
- [ ] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [ ] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [ ] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused recovery-initiation tests, full Background tests/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not conflate `NO_WHATSAPP_RECIPIENT` with `WHATSAPP_RECIPIENT_SUPPRESSED`; they have different recovery triggers.

Prefer a bounded recipient-resolution/admission outcome reused by recovery initiation. Do not add another large missing-recipient branch directly to `recovery-initiation.service.ts`.

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
