---
id: ARCH-028-BACKGROUND-005
architecture_id: ARCH-028
title: Snapshot the exact WhatsApp recipient for every outreach attempt
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 47
executor: copilot
claimed_at: 2026-10-09T11:00:51Z
attempt: 1
depends_on:
  - ARCH-028-DATABASE-003
  - ARCH-028-BACKGROUND-007
enables:
  - ARCH-028-BACKGROUND-010
created: 2026-10-07
updated: 2026-10-09
---

# Snapshot the exact WhatsApp recipient for every outreach attempt

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Adopt DATABASE-003 required `RecoveryOutreachAttempt.recipient` in every initial and follow-up send path, persisting the canonical, actual destination before billing/Meta admission. Do not implement suppression policy or reachability writes in this task.

## Context

The exact Shop/recovery for provider failure is already known through durable message/attempt/recovery relations. The attempt's required `recipient` snapshot identifies the failed destination. BACKGROUND-007 resolves the initial recipient before recovery creation; this task adopts the strict DATABASE-003 field on all attempt-creation paths, including follow-ups and sends to a changed current phone.

The current refactored `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts` still checks `!recovery.customer?.phone` as part of its early due guard and uses `to: recovery.customer.phone` for the provider send. Both are stale for ARCH-028 when `CustomerPhone` is authoritative: `Customer.phone` may be null or out of date while a usable current Shop-scoped `CustomerPhone` exists.

## Scope

- Reuse BACKGROUND-007's canonical current-`CustomerPhone` prerequisite for initial sends; resolve the current Shop-scoped phone again when creating each follow-up, not from a stale `Customer.phone` field. Replace the follow-up processor's `!recovery.customer?.phone` early guard and `to: recovery.customer.phone` destination with the current canonical resolution result; do not turn an absent/stale legacy `Customer.phone` into a false suppression outcome.
- Centralise bounded digits-only recipient canonicalization in a small Background-owned helper (not a duplicate phone-identity model).
- Populate required `RecoveryOutreachAttempt.recipient` before initial and follow-up outbound admission/Meta send; pass the same number to the provider. Treat the stored recipient as immutable after provider-directed work begins.
- Ensure all attempt writers, test fixtures and relevant Prisma consumers adopt the breaking DATABASE-003 revision together. Record the exact database gitlink/version adopted.
- If current recipient is absent when initiating a follow-up, do not admit/send/bill; return a bounded safe outcome rather than inventing a recipient.
- Preserve Shop isolation and existing attempt idempotency. No recipient is inferred from a provider status webhook.

## Out of Scope

- Candidate no-recipient prerequisite (BACKGROUND-007), except its typed initial-recipient handoff.
- Reachability policy, suppression lookups/resume (BACKGROUND-010).
- Post-compensation failure reachability and positive-evidence clearing (BACKGROUND-011).
- Synchronous provider rejection (BACKGROUND-006) and merchant notification (BACKGROUND-008).
- Global phone blacklist or Customer.hasWhatsApp.

## Requirements

- [ ] Every initial and follow-up attempt has a required canonical digits-only recipient matching the actual Meta destination.
- [ ] Recipient selection uses current Shop-scoped `CustomerPhone`, never stale `Customer.phone`; BACKGROUND-007 remains the initial materialisation guard. A null/stale `Customer.phone` does not block an otherwise eligible follow-up with a current usable `CustomerPhone`.
- [ ] Attempt recipient is immutable after provider-directed work; a new current phone requires a separate attempt snapshot.
- [ ] Provider delivery status never resolves tenant ownership through phone lookup.
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [ ] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [ ] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [ ] Reuse BACKGROUND-007 recipient-prerequisite output for initial attempt creation and send.
- [ ] Add canonical current-`CustomerPhone` selection and per-attempt recipient snapshots for follow-ups.
- [ ] Adopt DATABASE-003 across all attempt creation paths and fixtures.
- [ ] Verify persisted recipient equals the actual provider destination even when current phone changes.
- [ ] Add initial/follow-up and multi-Shop same-number tests, including null and stale `Customer.phone` with a valid current `CustomerPhone` and actual Meta destination parity.
- [ ] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes DATABASE-003 required outreach recipient and BACKGROUND-007 canonical initial recipient. Exposes the immutable per-attempt recipient to BACKGROUND-010 and BACKGROUND-011; does not consume compensation outcomes.

## Dependencies

- `ARCH-028-DATABASE-003`
- `ARCH-028-BACKGROUND-007`

## Enables

- `ARCH-028-BACKGROUND-010`

## Acceptance Criteria

- [ ] All attempt-creation paths satisfy mandatory DATABASE-003 recipient without a nullable/default escape hatch.
- [ ] Initial and follow-up sends target their own immutable per-attempt stored digits-only recipient.
- [ ] A changed phone never mutates an earlier attempt recipient.
- [ ] Missing follow-up recipient creates no new admission or provider call.
- [ ] A due follow-up with null or stale `Customer.phone` but a valid current Shop-scoped `CustomerPhone` is not falsely suppressed and sends to the stored per-attempt current recipient.
- [ ] Two Shops sharing the same phone remain isolated.
- [ ] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [ ] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [ ] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused initial/follow-up recipient-selection and attempt-write tests including missing/changed current phone, null/stale `Customer.phone` positive follow-up admission, required-field PostgreSQL integration, Meta destination/snapshot parity, full Background test/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Reuse existing recipient resolution and do not log full recipient values. Avoid making `recovery-initiation.service.ts` own phone-history selection and all future reachability policy. The stricter database revision and attempt writers must be integrated together; do not independently deploy the mandatory-field migration to running incompatible Background code.

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
