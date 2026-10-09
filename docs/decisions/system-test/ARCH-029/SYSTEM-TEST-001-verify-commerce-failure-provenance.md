---
id: ARCH-029-SYSTEM-TEST-001
architecture_id: ARCH-029
title: Verify Commerce failure provenance across hosts
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-029-BACKGROUND-001
  - ARCH-029-BACKGROUND-002
  - ARCH-029-COMMERCE-001
enables: []
created: 2026-10-10
updated: 2026-10-10
---

# Verify Commerce failure provenance across hosts

## Architecture

Architecture ID: `ARCH-029`.

Architecture document: `docs/architecture/ARCH-029-commerce-runner-failure-diagnostics.md`.

Coordinator: `moda_architect`.

## Objective

Verify that distinct CommerceAgent failure origins remain identifiable and safe across accepted Shared, Background and Commerce boundaries without altering turn outcomes.

## Context

Individual repository tests cover schema and adapter failure paths. This terminal architecture test verifies that published package/host composition preserves those diagnostics and correlation at real service boundaries. The developer may manually validate first; execution becomes eligible only after all implementation dependencies are Complete.

## Scope

Only `moda-interact-system-test` test scenarios, fixtures, orchestration and evidence for ARCH-029, using existing disposable/offline test harnesses. Use injected/provider stubs and deterministic errors; do not depend on causing live 401/429 with paid credentials.

## Out of Scope

Implementing Shared, Background or Commerce fixes; changing provider policies; sending real customer messages; new metrics/OTLP infrastructure; unrelated system domains.

## Requirements

- Exercise a rate-limited provider path (429), provider authorization failure (401/403), malformed model output, preflight invalid manifest, malformed tool result, tool authorization exception and expired/invalid evidence when supported by the existing harness.
- Assert the known public code/retryability is preserved and relevant structured log contains distinct `stage/reasonCode` and correlation identifiers.
- Verify logging or diagnostic sink failure cannot alter the business outcome.
- Inject hostile tokens, raw provider body and model/tool text into exceptions; assert none appear in emitted diagnostic fields/customer messages.
- Do not make system test a prerequisite for implementation or publication.

## Work Items

- [ ] Add bounded deterministic cross-host failure scenarios using current system-test orchestration.
- [ ] Assert stable public outcomes, correct diagnostic reason and correlation.
- [ ] Assert redaction/non-disclosure and failure-isolated logging.
- [ ] Capture the system-test evidence report.

## Interfaces / Contracts

Published Shared `commerce/runner` failure diagnostics and the current Background/Commerce host boundaries. No new runtime contract.

## Dependencies

- `ARCH-029-BACKGROUND-001`.
- `ARCH-029-BACKGROUND-002`.
- `ARCH-029-COMMERCE-001`.

## Enables

None.

## Acceptance Criteria

- [ ] Required representative failure classes are distinguishable by safe structured diagnostics.
- [ ] Retry/budget/authorization/customer outcomes match pre-change behaviour.
- [ ] No secrets/customer/provider payloads appear in logs/results.
- [ ] System-test run is reproducible and evidence captures actual executed results.

## Validation

- [ ] Run targeted system-test evidence in disposable local mode using actual repository scripts.
- [ ] Validate generated evidence report and cleanup/isolation.

## Stop Condition

Return `status: review`, evidence and Completion Report to `moda_architect` and STOP.

## Implementation Notes

Keep fixtures, assertions and executor/orchestration modules focused rather than building one large multi-purpose scenario file. Prefer deterministic injected provider failures to flaky real-provider requests.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

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

Pending.

### Review Notes

Pending.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
