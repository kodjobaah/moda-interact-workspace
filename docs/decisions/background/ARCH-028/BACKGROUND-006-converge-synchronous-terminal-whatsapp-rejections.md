---
id: ARCH-028-BACKGROUND-006
architecture_id: ARCH-028
title: Converge synchronous terminal WhatsApp rejections
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 72
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-005
enables:
  - ARCH-028-BACKGROUND-008
created: 2026-10-07
updated: 2026-10-07
---

# Converge synchronous terminal WhatsApp rejections

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Preserve bounded Meta provider codes from synchronous HTTP rejection and make exact code `131026` follow the same compensation, hard-limit and Shop-scoped suppression policy as asynchronous terminal failure.

## Context

`WhatsAppService` currently discards the provider error body/code and throws only `provider-rejected`. Recovery billing failure handling cannot therefore distinguish terminal recipient rejection from other synchronous provider failures.

## Scope

- Extend `WhatsAppServiceError` with optional bounded `providerCode` extracted from Meta error response without retaining raw detail/body.
- For synchronous exact `131026`, persist message `FAILED` + failure evidence and use the same local terminal-recipient classifier.
- Invoke the same idempotent compensation/release/hard-limit owner used by asynchronous processing.
- After successful correction invoke the same reachability suppression owner.
- Preserve existing ambiguous/non-terminal provider-failure handling for other codes/network uncertainty.
- Keep duplicate/idempotent admission semantics.

## Out of Scope

- New provider-code classification beyond `131026`.
- Merchant notification (BACKGROUND-008).
- Purchased COMMITTED compensation (BACKGROUND-009).

## Requirements

- [ ] Sync 131026 and async FAILED/131026 converge to the same policy outcome.
- [ ] Raw Meta error text/body is not persisted/logged.
- [ ] Other synchronous rejections are not silently classified as recipient-undeliverable.
- [ ] RESERVED recovery source is released idempotently.
- [ ] Outbound hard-limit UsageEvent is removed consistently with async terminal failure.
- [ ] Reachability suppression occurs only after correction succeeds.

## Work Items

- [ ] Add bounded providerCode extraction/error type tests for text/template sends.
- [ ] Wire synchronous terminal classifier to message evidence.
- [ ] Reuse compensation/hard-limit/reachability owners.
- [ ] Add duplicate, non-terminal and ambiguous failure tests.

## Interfaces / Contracts

Repository-local `WhatsAppServiceError.providerCode?: string` only; no new cross-service contract.

## Dependencies

- `ARCH-028-BACKGROUND-005`

## Enables

- `ARCH-028-BACKGROUND-008`

## Acceptance Criteria

- [ ] Sync `131026` results match async terminal policy except there is no later provider message-status requirement.
- [ ] Non-131026/network/configuration failures preserve existing safe semantics.
- [ ] No double release/hard-limit correction/suppression occurs on retries.

## Validation

Focused WhatsApp service, outbound admission and recovery send tests; full Background tests/build; `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Keep provider error parsing bounded to the numeric/string code needed by policy. Do not make WhatsAppService own billing/recovery policy.

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
