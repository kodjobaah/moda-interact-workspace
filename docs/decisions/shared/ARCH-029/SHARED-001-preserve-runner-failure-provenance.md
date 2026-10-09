---
id: ARCH-029-SHARED-001
architecture_id: ARCH-029
title: Preserve Commerce turn failure provenance and safe diagnostics
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-029-SHARED-002
created: 2026-10-10
updated: 2026-10-10
---

# Preserve Commerce turn failure provenance and safe diagnostics

## Architecture

Architecture ID: `ARCH-029`.

Architecture document: `docs/architecture/ARCH-029-commerce-runner-failure-diagnostics.md`.

Coordinator: `moda_architect`.

## Objective

Make every canonical Shared Commerce-turn failure diagnosable by emitting stable, bounded stage/reason metadata and preserving its source without changing public error classification, retries, authorization, budget accounting or result success behaviour.

## Context

In Shared 1.3.5, `RunnerFailure` holds only a broad code; `runtime.bounded()` discards dependency causes; failure events do not contain stage/reason; preflight errors can occur before logger creation; invalid model/final responses have ambiguous `INVALID_FINAL` descriptions. OpenRouter already emits a safe diagnostic callback but the runner must preserve provenance at its boundary.

## Scope

Only `moda-interact-shared` source/tests. Inspect and make bounded changes as needed to `src/commerce/runner/{failure,index,runtime,preflight,model-step,tool-execution,tool-policy,evidence,final-response,observability}.ts`, graph nodes, `src/commerce/model/openrouter-model-client.internal.ts` and focused runner/model tests. No new generic logger, telemetry backend, consumer changes or dependencies.

## Out of Scope

- Modifying Background, Commerce, Admin, the database, Gateway, or task documentation outside this task's Completion Report.
- Package publication/version bump; belongs to SHARED-002.
- Changing the semantic meaning of `RunnerErrorCode`, `retryable`, tool retries, budgets or referral behaviour.
- Raw exception/provider/Zod/model data in logs, public failure detail or the LLM context.
- Service-specific provider credential or MCP host classification; belongs to Background tasks.

## Requirements

### R1 — Stable failure classification plus actionable reason

Preserve `RunCommerceTurnResult.error.code` and `.retryable` values and success shape. Add an optional bounded, exported internal `diagnostic` object to the failure variant, with a finite `stage`/`reasonCode` vocabulary and strictly allowlisted optional fields. The same diagnostic must appear in the terminal `commerce.turn.failed` structured event. Avoid stringly typed arbitrary messages as reason codes. Existing callers that only inspect `code` and `retryable` continue to work.

### R2 — Record source at each failure boundary

Identify important preflight, runtime, model, tool authorization/execution, evidence and final-response failures separately. Distinguish the subset of `INVALID_FINAL` failures due to model-step shape, route, final-schema validation, mandatory referral and rejected/expired evidence. Distinguish the source of `INVALID_INPUT` at preflight and tool input validation. Distinguish `DEADLINE` caused by whole-turn expiry versus bounded operation timeout. Preserve nested exceptions internally via standard `cause` when available; never log raw cause objects.

### R3 — Provider classification survives model invocation

Retain the already supported OpenRouter diagnostic stages/reasons and bounded provider numeric codes/status. Ensure a model invocation failure can carry that safe diagnostic through the runner even if an invoker reports its cause through a typed error rather than the optional callback. Preserve current safe message contract (`Commerce model unavailable`), avoid raw provider bodies, and keep model invokers independent of LangChain types.

### R4 — Log all failure paths, including preflight

Create a safe root logging path before preflight so invalid turn/manifest/grant validation produces a terminal diagnostic event. Use validated child identity only after preflight succeeds. Preserve `commerce.turn.failed` and its existing `errorCode`, `retryable`, `modelSteps`, `remoteCalls`, `durationMs` fields. Emit a single terminal failure event, maintain best-effort sink isolation and do not suppress other telemetry. Keep structured tool outcome errors distinct from terminal runner failures.

### R5 — Sensitive-data and bounds contract

No exception/raw model/provider payload, prompt, history, args, full Zod issue object, Error.stack, secrets, customer fields, or arbitrary dynamic schema keys. Schema diagnostics may include issue count, issue code and bounded allowlisted path metadata, without values. Tool names/status codes/numeric provider codes and counters must be bounded and safe. Unknown exceptions receive an explicit `UNEXPECTED_EXCEPTION` reason and origin stage, with the prior public code/retryable semantics unchanged.

### R6 — Existing runtime safety invariants

No additional remote calls, retries, model steps, timers, network logging or durable state changes. Cancellation, deadlines, limits, evidence validation and authorization are unchanged. Error/diagnostic logging failure must never change the result.

## Work Items

- [ ] Define typed safe diagnostics and preserve internal source/cause at failure construction points.
- [ ] Capture source-specific schema/authorization/budget/model/tool/evidence/final failures and bounded metadata.
- [ ] Emit terminal diagnostics for preflight and post-preflight paths through the existing Shared logger.
- [ ] Preserve provider-safe classifications across the OpenRouter invoker boundary.
- [ ] Add tests for non-disclosure, correlation, failure stability and logger failures.

## Interfaces / Contracts

Owner: `moda_shared`.

Published entrypoints: `@modainteract/moda-interact-shared/commerce/runner`, `@modainteract/moda-interact-shared/commerce/model/node`.

Consumers: `moda-interact-background`, `moda-interact-commerce`.

Keep `RunCommerceTurnResult.error.code/retryable` stable; add only the bounded optional diagnostic for internal hosts. No changes to `CommerceModelInvoker` request/response, queue schemas or customer response contract. Follow `docs/observability/shared-logging.md`.

## Dependencies

None. Task can execute once the developer accepts the proposed ARCH-029 design.

## Enables

- `ARCH-029-SHARED-002`.

## Acceptance Criteria

- [ ] Same representative 401, 429, provider-response-invalid, tool-throw, auth-throw, malformed-final and preflight failures retain their existing public `code/retryable`, but have distinct `stage/reasonCode`.
- [ ] `commerce.turn.failed` includes structured cause metadata for every failure path including preflight (with no unvalidated tenant payload logged).
- [ ] Provider/request/model result text, credentials, raw Zod data, tool args and other sensitive values never appear in diagnostic return/log records.
- [ ] Failure sink exceptions change neither results nor retries, budgets or model/tool counts.
- [ ] Normal structured tool `ERROR`/`DENIED` outcomes remain business semantics and are not incorrectly classified as terminal failures.
- [ ] No duplicated generic logger or custom request/LLM metrics.

## Validation

- [ ] `npm run typecheck`.
- [ ] `npm run test` (including focused runner and OpenRouter diagnostics regressions).
- [ ] `npm run build`.
- [ ] `npm run validate:commerce-entrypoints` (after build, using the declared script).
- [ ] Inspect diff for secrets, semantic changes and external API compatibility.

## Stop Condition

When bounded implementation and validation complete, record Completion Report evidence, set `status: review`, return to `moda_architect` and STOP; do not publish or start consumer tasks.

## Implementation Notes

Prefer stable codes at specific `throw` sites over a broad catch that infers cause after it has been lost. Do not return a full raw `error.message = JSON.stringify(zodError.format())`. Preserve `Error.cause` for internal chains while logging only explicitly constructed safe fields. Do not globally retry exceptions or silently remap unexpected errors to new public codes. Keep modules cohesive; do not grow a monolithic runner file.

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

Pending implementation review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
