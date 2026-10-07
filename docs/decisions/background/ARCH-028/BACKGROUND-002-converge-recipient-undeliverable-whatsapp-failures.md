---
id: ARCH-028-BACKGROUND-002
architecture_id: ARCH-028
title: Converge recipient-undeliverable WhatsApp delivery failures
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-001
  - ARCH-028-MESSAGING-001
enables:
  - ARCH-028-BACKGROUND-004
created: 2026-10-03
updated: 2026-10-07
---

# Converge recipient-undeliverable WhatsApp delivery failures

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Classify exact bounded Meta code `131026` as the ARCH-028 terminal recipient-delivery condition, converge linked recovery/follow-up state safely, and make later compensation eligibility independent of `RecoveryOutreachAttempt.status`.

## Context

A delayed provider failure can arrive after the follow-up processor has already moved the initial attempt to `NO_RESPONSE`. Provider delivery authority therefore belongs to `ConversationMessage`, not the attempt response-lifecycle enum.

## Scope

- Add one pure classifier: `131026 -> RECIPIENT_UNDELIVERABLE`, other/absent -> unclassified.
- Resolve the exact linked `RecoveryOutreachAttempt` through `outboundMessageId`; never correlate by phone/customer/timestamp.
- If the exact attempt is still `WAITING_FOR_RESPONSE`, guardedly move it to `FAILED` with `WHATSAPP_RECIPIENT_UNDELIVERABLE` inside the existing provider-status transaction.
- If attempt is already `NO_RESPONSE`, `ENGAGED`, `CANCELLED`, `CAPACITY_BLOCKED` or `FAILED`, do not overwrite its response lifecycle merely to make compensation possible.
- Make due follow-up processing consult authoritative failed-message evidence before `markNoResponseIfWaiting`, billing or provider work.

## Out of Scope

- Usage release/compensation.
- Recipient suppression.
- Hard-limit correction.
- Synchronous HTTP rejection.
- Missing phone.
- Merchant notification.

## Requirements

- [ ] Exact `131026` is the only terminal-recipient code in ARCH-028 v1.
- [ ] A provider FAILED message linked to a recovery can be financially compensatable regardless of attempt status.
- [ ] `WAITING_FOR_RESPONSE -> FAILED` remains a useful convergence transition but is not a financial eligibility precondition.
- [ ] `NO_RESPONSE` race cannot permanently block later compensation.
- [ ] DELIVERED/READ wins before compensation and prevents terminal classification from acting.
- [ ] A due follow-up whose initial message is durably FAILED/131026 performs no policy/billing/provider send.
- [ ] No permanent `hasWhatsApp` assertion is created.

## Work Items

- [ ] Add pure provider-code classifier/tests.
- [ ] Resolve linked attempt/recovery from message relation.
- [ ] Guard WAITING -> FAILED convergence in the provider-status transaction.
- [ ] Preserve other attempt lifecycle states without using them as compensation gates.
- [ ] Add failed-message follow-up suppression before no-response/billing/provider work.
- [ ] Add NO_RESPONSE race and duplicate/out-of-order tests.

## Interfaces / Contracts

Consumes v3 `failure.providerCode`; introduces repository-local classification `RECIPIENT_UNDELIVERABLE` and stable attempt failure code `WHATSAPP_RECIPIENT_UNDELIVERABLE` when WAITING can be converged.

## Dependencies

- `ARCH-028-BACKGROUND-001`
- `ARCH-028-MESSAGING-001`

## Enables

- `ARCH-028-BACKGROUND-004`

## Acceptance Criteria

- [ ] `131026` classifies terminal-recipient; other/absent codes do not.
- [ ] Linked WAITING attempt can become FAILED idempotently.
- [ ] Existing NO_RESPONSE/ENGAGED/etc. state is not overwritten solely for compensation.
- [ ] Later compensation can use FAILED/131026 message + exact reservation lineage even when attempt is not FAILED.
- [ ] Due follow-up no-ops before billing/provider work when authoritative initial delivery failed.
- [ ] Positive delivery/read and unrelated failures retain existing behaviour.

## Validation

Run focused classifier/provider-status/follow-up tests, repository unit/full test/build gates and `git diff --check` as declared by the current repository.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not redesign `RecoveryOutreachStatus` to carry two independent dimensions. Message delivery and attempt response lifecycle stay separate; later compensation reads both durable associations without requiring an artificial state rewrite.

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
