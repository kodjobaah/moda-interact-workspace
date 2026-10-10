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
status: complete
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
- [x] Record safe runner diagnostics in existing staff preview operational context.
- [x] Add focused compatibility and privacy tests for invalid final/provider error/cancel.

## Interfaces / Contracts

Consumes `@modainteract/moda-interact-shared/commerce/runner`, `commerce/model/node`, and Shared logger. No new cross-service schema owned by Commerce.

## Dependencies

- `ARCH-029-SHARED-002`.

## Enables

- `ARCH-029-SYSTEM-TEST-001`.

## Acceptance Criteria

- [x] Test Conversation errors can be distinguished by safe stage/reason in internal logs.
- [x] Existing PreviewResult public failure code/outcome semantics remain stable.
- [x] No raw OpenRouter/provider, customer, prompt or tool content is emitted.
- [ ] Published dependency is actually installed and tests exercise it.

## Validation

- [ ] Focused Commerce Test Conversation/Preview tests using declared scripts.
- [ ] Typecheck and appropriate repository build/validation for changed code.
- [x] Inspect privacy/authorization and output compatibility.

## Stop Condition

Set `status: review`, complete task report, return to `moda_architect` and STOP.

## Implementation Notes

The existing Test Conversation OpenRouter diagnostic callback should be reused. Do not build a second provider logger or store raw provider details in Redis. Avoid broad UI changes; internal structured logs are the minimum delivery.

## Completion Report

### Status

Ready for Review — retrospective record of the manually applied patch workflow.

### Files Changed

- package.json
- src/commerce/preview/runner-diagnostic-log-fields.ts (new)
- src/commerce/preview/service.ts
- tests/preview-runner-diagnostic-log-fields.test.ts (new)
- tests/preview-service.test.ts

### Work Completed

- Prepared the Commerce staff Test Conversation integration using the published Shared 1.4.0 runner failure diagnostic type.
- Added safe runner `stage/reasonCode` correlation to the internal preview log, without adding raw provider data to persisted/customer-visible PreviewResult.
- Added focused tests for malformed model output, missing diagnostics and logging failure isolation.

### Validation Results

- The Commerce patch passed `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all` and `git diff --check` against a fresh Commerce snapshot.
- TypeScript syntax/transpilation and isolated diagnostic checks passed, 6/6.
- **No local Commerce npm install, full Vitest, build, or typecheck output has been supplied after this patch**. The patch’s application in the developer checkout is also not independently confirmed. Do not represent this task as test-certified.

### Deviations

- This work was delivered as an external `.patch` plus ZIP for developer application; local application/validation is evidenced only where separately recorded below. It did not follow the repository agent launcher/dual dedicated task-worktree submission process.
- The uploaded snapshot contains no launcher execution packet, two-worktree isolation/synchronisation evidence, pushed task branches, implementation commit IDs or parent-task review commits. These have **not** been invented or certified. This is a developer-directed administrative closeout exception, not a conforming claim under `docs/agent-worktree-isolation-policy.md`.
- The developer requested closure of all implementation tasks while independently continuing system tests. For Commerce, source application and repository-level validation have not been evidenced in the conversation; accepted administratively at the developer’s direction with this explicit outstanding verification gap.

### Assumptions

- The user wishes to close the prepared Commerce implementation patch as part of this developer-directed ARCH-029 closeout; source application/installed version are not independently verified.

### Unresolved Issues

- Commerce full test/build/typecheck, lockfile regeneration and confirmed installation of Shared 1.4.0 remain unverified.
- Worktree source/branch/commit/attempt evidence remains unavailable.

### Architectural Concerns

- Keep staff-only diagnostic correlation separate from customer and persisted preview outputs.

## Architect Review

### Review Status

Accepted — developer-directed closeout with the evidence limitations explicitly recorded below.

### Review Notes

- Developer requested closeout of implementation work and continuation of end-to-end coverage independently in the system-test project.
- **Acceptance scope is administrative only for this external patch workflow. The conversation does not contain the local repository-level validation required by the task, so no passing local checks are claimed.**

### Reviewed Files

- package.json
- src/commerce/preview/runner-diagnostic-log-fields.ts (new)
- src/commerce/preview/service.ts
- tests/preview-runner-diagnostic-log-fields.test.ts (new)
- tests/preview-service.test.ts

### Validation Reviewed

- The Commerce patch passed `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all` and `git diff --check` against a fresh Commerce snapshot.
- TypeScript syntax/transpilation and isolated diagnostic checks passed, 6/6.
- **No local Commerce npm install, full Vitest, build, or typecheck output has been supplied after this patch**. The patch’s application in the developer checkout is also not independently confirmed. Do not represent this task as test-certified.

### Architecture Conformance

- The code patch conforms in scope: retain public PreviewResult semantics and log only bounded internal runner stage/reason.
- Formal worktree isolation and full local implementation validation are not established; this is a consciously recorded developer-directed closure exception.

### Follow-up

- Run the published Commerce test/build commands and confirm Shared 1.4.0 lockfile/install before treating the feature as locally test-certified.
- System-test validation is independently owned by the existing moda-interact-system-test project.
