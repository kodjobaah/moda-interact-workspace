---
id: ARCH-029-BACKGROUND-001
architecture_id: ARCH-029
title: Preserve production Commerce model and credential diagnostics
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
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

# Preserve production Commerce model and credential diagnostics

## Architecture

Architecture ID: `ARCH-029`.

Architecture document: `docs/architecture/ARCH-029-commerce-runner-failure-diagnostics.md`.

Coordinator: `moda_architect`.

## Objective

Ensure the production CommerceAgent model invocation records why credential resolution, model setup or the OpenRouter provider failed, while retaining the existing worker/public failure classification.

## Context

`src/commerce/production-model.ts` does not supply the OpenRouter adapter's existing `onDiagnostic` callback and replaces all failures with `Commerce model invocation failed`; `src/commerce/openrouter-credential.ts` likewise erases credential-resolution causes. Therefore a provider 429 and missing credential can look identical in production even though Test Conversations already log provider diagnostics.

## Scope

Only `moda-interact-background` production model/credential diagnostics and related focused tests; expected files: `src/commerce/production-model.ts`, `src/commerce/openrouter-credential.ts` plus tests. Upgrade the Shared dependency to the exact version accepted by SHARED-002 if not already installed. Use `@modainteract/moda-interact-shared/logging`, not a local generic logger.

## Out of Scope

- Shared runner/model implementation changes or package publication.
- MCP transport/host-level errors; owned by BACKGROUND-002.
- Retrying provider 429, adding backoff or changing model selection, tenant resolution or credential storage/encryption.
- Logging any credential, ciphertext, key material, raw provider error/message/body or model input/output.

## Requirements

1. Pass the established Shared OpenRouter `onDiagnostic` callback for production invocation and emit bounded structured `stage`, `reason`, optional `statusCode` and bounded `providerCode` under the selected model's existing safe identity. Keep diagnostic callback exceptions isolated.
2. Distinguish credential lookup/database failure, missing credential, missing key, failed decryption/invalid envelope, client construction, provider request/response failure and caller cancellation by stable safe reason where ascertainable, without logging secrets or revealing them to end users.
3. Do not overwrite a safe Shared typed diagnostic/cause with a generic `Error` when it would erase provenance. Preserve the existing stable public failure code/retryability and cancellation/deadline semantics.
4. Maintain correlation with model selection source, shop/conversation context available to the caller, and turn invocation as appropriate; never embed customer payloads in log entries.
5. Do not add metrics duplicating standard OpenTelemetry provider/client instrumentation or synchronously send logs over the network.

## Work Items

- [x] Wire the published Shared `onDiagnostic` into production model creation.
- [x] Distinguish safe credential/client/provider failure reasons and preserve appropriate typed cause.
- [x] Add focused tests covering provider 401/429, invalid response, missing credential, decryption failure, cancel and hostile provider message non-disclosure.

## Interfaces / Contracts

Consumes published `@modainteract/moda-interact-shared/commerce/model/node`, `commerce/runner` and `logging`. Do not change the model request/response contract or `CommerceAgentResult`.

## Dependencies

- `ARCH-029-SHARED-002`.

## Enables

- `ARCH-029-SYSTEM-TEST-001`.

## Acceptance Criteria

- [x] Production logs distinguish a 429 from auth failure, invalid provider response and credential failure without raw secrets or content.
- [x] The Shared runner sees safe failure provenance when the model dependency fails.
- [x] No change to production agent success, retry, cancellation or timeout behaviour.
- [x] Diagnostics/log sink failures cannot change model/worker outcomes.

## Validation

- [x] Run focused production Commerce model/credential tests under declared repository scripts.
- [x] Run repository typecheck and applicable unit tests per `package.json`/task scope.
- [ ] Inspect package lock/dependency version and structured log payload safety.

## Stop Condition

On completion, set `status: review`, submit Completion Report, and STOP.

## Implementation Notes

Do not catch and log the raw OpenRouter error object; use Shared's existing bounded diagnostic callback. A safe `cause` chain is internal and must not be automatically serialized. When a credential resolver must distinguish database and decryption failure, introduce an internal finite reason vocabulary instead of exposing plaintext or SQL details.

## Completion Report

### Status

Ready for Review — retrospective record of the manually applied patch workflow.

### Files Changed

- package.json
- src/agents/commerce.agent.ts
- src/commerce/openrouter-credential-failure.ts (new)
- src/commerce/openrouter-credential.ts
- src/commerce/production-model.ts
- tests/unit/commerce/openrouter-credential.test.ts
- tests/unit/commerce/production-model.test.ts
- tests/unit/runtime/observability-startup.test.ts

### Work Completed

- Updated the Background declared Shared dependency to 1.4.0 and wired Shared OpenRouter `onDiagnostic` to production model invocation.
- Distinguished lookup, missing credential, key, malformed envelope and decryption errors while retaining typed provider diagnostics; used bounded, safe structured logging.
- Applied a two-test-file validation assertion correction after local unit tests identified old expected strings and a 1.3.0 version expectation.

### Validation Results

- The developer reported a successful Background build (Prisma generation and TypeScript compilation).
- The developer pasted full local unit results: 176/176 test files and 1,904/1,904 tests passed.
- The implementation and correction patches passed fresh-snapshot Git apply/whitespace checks in prior work; full dedicated-worktree validation evidence was not supplied.

### Deviations

- This work was delivered as an external `.patch` plus ZIP for developer application; local application/validation is evidenced only where separately recorded below. It did not follow the repository agent launcher/dual dedicated task-worktree submission process.
- The uploaded snapshot contains no launcher execution packet, two-worktree isolation/synchronisation evidence, pushed task branches, implementation commit IDs or parent-task review commits. These have **not** been invented or certified. This is a developer-directed administrative closeout exception, not a conforming claim under `docs/agent-worktree-isolation-policy.md`.

### Assumptions

- The user’s local 1,904-test result reflects the final BACKGROUND-001 code and assertion correction.

### Unresolved Issues

- Task-worktree branches/commits and start-of-attempt synchronisation evidence were not supplied.

### Architectural Concerns

- The original background exception path previously erased provider provenance; the correction retains Shared diagnostic cause instead of recreating a service-local generic logger.

## Architect Review

### Review Status

Accepted — developer-directed closeout with the evidence limitations explicitly recorded below.

### Review Notes

- The observed test failures were outdated expectations, corrected within the same task. The user subsequently reported the full suite green.

### Reviewed Files

- package.json
- src/agents/commerce.agent.ts
- src/commerce/openrouter-credential-failure.ts (new)
- src/commerce/openrouter-credential.ts
- src/commerce/production-model.ts
- tests/unit/commerce/openrouter-credential.test.ts
- tests/unit/commerce/production-model.test.ts
- tests/unit/runtime/observability-startup.test.ts

### Validation Reviewed

- The developer reported a successful Background build (Prisma generation and TypeScript compilation).
- The developer pasted full local unit results: 176/176 test files and 1,904/1,904 tests passed.
- The implementation and correction patches passed fresh-snapshot Git apply/whitespace checks in prior work; full dedicated-worktree validation evidence was not supplied.

### Architecture Conformance

- The changes preserve existing worker model, credential storage, failure classification and retry semantics while adding cause visibility.
- Worktree policy evidence missing; explicit developer-directed closeout exception recorded.

### Follow-up

- No new Background runtime changes required by reported tests.
