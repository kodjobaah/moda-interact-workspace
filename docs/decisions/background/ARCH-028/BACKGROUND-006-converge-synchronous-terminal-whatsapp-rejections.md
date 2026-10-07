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
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [ ] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [ ] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [ ] Add bounded providerCode extraction/error type tests for text/template sends.
- [ ] Wire synchronous terminal classifier to message evidence.
- [ ] Reuse compensation/hard-limit/reachability owners.
- [ ] Add duplicate, non-terminal and ambiguous failure tests.
- [ ] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

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
- [ ] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [ ] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [ ] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused WhatsApp service, outbound admission and recovery send tests; full Background tests/build; `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Keep provider error parsing bounded to the numeric/string code needed by policy. Do not make WhatsAppService own billing/recovery policy.

Keep the synchronous provider-rejection adapter thin and reuse the asynchronous terminal-failure policy owners. Do not duplicate compensation, hard-limit or reachability policy in the WhatsApp provider client/service.

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
