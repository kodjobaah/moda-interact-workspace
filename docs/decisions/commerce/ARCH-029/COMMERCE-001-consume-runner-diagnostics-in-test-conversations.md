---
id: ARCH-029-COMMERCE-001
architecture_id: ARCH-029
title: Adopt Shared runner diagnostics in staff Test Conversations
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-029-SHARED-002
enables:
  - ARCH-029-SYSTEM-TEST-001
created: 2026-10-10
updated: 2026-10-10
---

# Adopt Shared runner diagnostics in staff Test Conversations

## Architecture

Architecture ID: `ARCH-029`.

Architecture document: `docs/architecture/ARCH-029-commerce-runner-failure-diagnostics.md`.

Coordinator: `moda_architect`.

## Objective

Consume the published Shared diagnostic-capable runner in Commerce Test Conversations and preserve safe failure reasons in staff-only operational logs without exposing implementation/provider information to customers.

## Context

Commerce 1.3.5 already logs OpenRouter diagnostic callbacks from `src/commerce/integration/preview/model-runtime.ts` and records `output.error.code` from `runCommerceTurn` in `src/commerce/preview/service.ts`. The new Shared package adds runner-stage diagnostics beyond model-provider failures. Current Test Conversation failure traces do not retain those reasons.

## Scope

Only `moda-interact-commerce`: adopt exact published Shared version from SHARED-002, integrate bounded `stage/reasonCode` into staff-operational preview run logs/trace under existing access controls, and add focused tests. Keep existing PreviewResult transport and access boundaries unless explicitly required by the task's staff-only diagnostic representation.

## Out of Scope

- Shared runtime implementation, model provider policy, MCP tool execution and Background.
- Customer-facing UI, customer response messages or merchant exposure to staff diagnostic data.
- Arbitrary error messages/stacks, model output, prompts, credentials or provider payloads.
- New telemetry backend, request metrics or general UI redesign.

## Requirements

1. Use the exact published Shared package release from SHARED-002; do not import local source or copy diagnostic schema.
2. Retain current OpenRouter `onDiagnostic` callback behaviour and augment failed Test Conversation operational logs with the canonical safe runner `diagnostic` stage/reason when present.
3. Keep `failureCode`/`PreviewResult` success and customer-message behaviour unchanged unless a narrowly required additive staff-only trace field is approved.
4. Missing diagnostics from an older/mocked runner remain safe and do not break rendering or persistence.
5. Logging failures do not alter Test Conversation results; no secret or model content leaks.

## Work Items

- [ ] Update Shared dependency to the exact SHARED-002 publication and verify installed version.
- [ ] Record safe runner diagnostics in existing staff preview operational context.
- [ ] Add focused compatibility and privacy tests for invalid final/provider error/cancel.

## Interfaces / Contracts

Consumes `@modainteract/moda-interact-shared/commerce/runner`, `commerce/model/node`, and Shared logger. No new cross-service schema owned by Commerce.

## Dependencies

- `ARCH-029-SHARED-002`.

## Enables

- `ARCH-029-SYSTEM-TEST-001`.

## Acceptance Criteria

- [ ] Test Conversation errors can be distinguished by safe stage/reason in internal logs.
- [ ] Existing PreviewResult public failure code/outcome semantics remain stable.
- [ ] No raw OpenRouter/provider, customer, prompt or tool content is emitted.
- [ ] Published dependency is actually installed and tests exercise it.

## Validation

- [ ] Focused Commerce Test Conversation/Preview tests using declared scripts.
- [ ] Typecheck and appropriate repository build/validation for changed code.
- [ ] Inspect privacy/authorization and output compatibility.

## Stop Condition

Set `status: review`, complete task report, return to `moda_architect` and STOP.

## Implementation Notes

The existing Test Conversation OpenRouter diagnostic callback should be reused. Do not build a second provider logger or store raw provider details in Redis. Avoid broad UI changes; internal structured logs are the minimum delivery.

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
