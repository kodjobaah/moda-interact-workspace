---
id: ARCH-002-SHARED-012
architecture_id: ARCH-002
title: Decouple GenAI span activation and add safe exception mapping
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 26
executor: codex
claimed_at: 2026-08-31 18:04:29+00:00
attempt: 1
depends_on:
- ARCH-002-SHARED-010
enables:
- ARCH-002-SHARED-013
created: 2026-08-31
updated: '2026-08-31'
---

# Decouple GenAI span activation and add safe exception mapping

## Objective

Make the published shared GenAI observation helpers composable so a consumer can
activate the accepted SHARED-009 active spans without necessarily activating the
SHARED-011 metrics, and can provide a safe exception representation without
changing the original application error that is rethrown.

## Context

`@modainteract/moda-interact-shared@0.4.0` currently combines the SHARED-009 span
helpers and SHARED-011 metrics in the same three public operations:

- `observeConversationTurn`;
- `observeAgentInvocation`;
- `observeAgentTool`.

Each call records metrics unconditionally.

The accepted generic `withObservedSpan` implementation also records the original
application `Error`. That is safe only where callers already know the Error
message is telemetry-safe. The current background CommerceAgent/tool path can
surface provider response details in Error messages.

This gap was discovered by `ARCH-002-BACKGROUND-008`, which correctly returned
Blocked rather than duplicating shared mechanics locally or starting
BACKGROUND-009 early.

## Scope

Extend the existing shared APIs in a backwards-compatible way so consumers can:

1. suppress GenAI metric recording for one observed operation while retaining
   the accepted active-span behaviour; and
2. supply an optional exception transformation/mapping function that produces a
   bounded telemetry-safe exception representation for span recording while the
   original thrown value is rethrown unchanged.

The implementation may add the smallest backwards-compatible optional controls
to:

- the public GenAI helpers; and
- `withObservedSpan` only where necessary to support safe exception mapping.

Existing calls that provide no new option must retain the current `0.4.0`
behaviour.

## Required Behaviour

### Metric control

Provide an explicit opt-out such as:

```text
recordMetrics: false
```

or an equivalent clear API.

Requirements:

- default/omitted behaviour continues to record the SHARED-011 metrics;
- spans remain active when metrics are suppressed;
- suppressing metrics creates no replacement service-local instruments;
- the existing bounded metric names and dimensions are unchanged when metrics
  are enabled.

### Safe exception mapping

Provide an optional mapping/transform boundary with equivalent semantics to:

```text
application error
    |
    +--> caller-supplied safe telemetry representation
    |        -> span exception event/status
    |
    +--> original error/value
             -> rethrown unchanged
```

Requirements:

- the mapper receives the application error/value only because the consumer
  explicitly supplies it;
- only the mapped/sanitized representation reaches `span.recordException`;
- the original application error/value is rethrown unchanged;
- mapper failure must never replace the original application error;
- if mapping fails, record only a bounded generic failure or omit the exception
  event while still setting the span status to ERROR;
- never fall back to recording the original potentially sensitive Error after a
  mapper has been supplied;
- no prompt, completion, message, tool payload, provider response body,
  credential, token, customer identifier or business payload is captured by the
  shared helper.

## Backwards Compatibility

This is an additive API correction.

Do not break existing `0.4.0` call signatures or default runtime behaviour.

Existing consumers that do not pass the new controls must continue to receive:

- the existing active spans;
- the existing SHARED-011 metrics;
- the existing exception behaviour unless they opt into the new safe mapper.

## Out of Scope

Do NOT:

- change service repositories;
- add CommerceAgent-specific names or business semantics to shared;
- change the six accepted GenAI metric instrument names;
- add new metric dimensions;
- create a new SDK/provider/exporter;
- redesign BullMQ/Prisma/HTTP instrumentation;
- publish the package;
- change BACKGROUND-008 or BACKGROUND-009 implementation;
- introduce a default sanitizer that silently rewrites all existing consumer
  errors.

## Acceptance Criteria

- [x] a consumer can obtain turn/agent/tool active spans with GenAI metrics
      explicitly suppressed;
- [x] default helper calls still emit the accepted SHARED-011 metrics;
- [x] metric suppression does not change active-context nesting or span status;
- [x] a supplied exception mapper controls what reaches the span exception event;
- [x] the original thrown value/error is rethrown unchanged by identity/value;
- [x] mapper failure cannot replace the application error and cannot cause the
      original sensitive Error to be recorded as fallback;
- [x] existing metric names/dimensions/cardinality remain unchanged when enabled;
- [x] no service-specific semantics or sensitive payload capture is introduced;
- [x] existing public call forms remain source/runtime compatible.

## Validation

- [x] focused spans-only test proving zero GenAI metric records when suppressed;
- [x] default-behaviour regression test proving current metrics still record;
- [x] turn -> agent -> tool nesting regression test;
- [x] safe-exception mapping test proving only mapped fields reach the span;
- [x] original-error identity/value rethrow test;
- [x] mapper-failure isolation test;
- [x] existing SHARED-011 cardinality test/regression;
- [x] repository tests;
- [x] typecheck;
- [x] production build;
- [x] package dry-run / consumer-style import for changed public types/exports.

## Stop Condition

After the capability and required implementation validation are complete:

1. record the Completion Report;
2. set this task to `review`;
3. return control to `moda_architect`;
4. STOP.

Do not publish a package and do not start SHARED-013.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/src/observability/index.ts`
- `moda-interact-shared/src/observability/genai.ts`
- `moda-interact-shared/src/observability/genai.test.ts`
- `moda-interact-shared/src/observability/genai.controls.test.ts`
- `moda-interact-shared/src/observability/test-fixtures/genai-spans-only-app.ts`
- `moda-interact-shared/README.md`
- `docs/decisions/shared/ARCH-002/SHARED-012-decouple-genai-span-controls.md`

### Work Completed

- Added optional `ObservedSpanOptions.mapException` and exported the
  `SpanExceptionMapper` contract.
- Added trailing optional `GenAIObservationOptions` to turn, agent and tool
  helpers with default-on metrics and explicit `recordMetrics: false` support.
- Bounded caller-mapped exception fields to 1,024 characters, omitted unusable
  or failed mappings, and preserved original thrown values unchanged.
- Added spans-only, nested-context, mapped-exception, mapper-failure,
  sensitive-data and compatibility coverage.
- Documented suppression and safe mapping semantics for consumers.

### Validation Results

- Focused GenAI tests: 4 passed.
- Repository tests: 63 passed, 1 skipped because `TEST_REDIS_URL` is not
  configured, 0 failed.
- `npm run typecheck`: passed.
- `npm run build`: passed with ESM and declaration outputs.
- `npm pack --dry-run`: passed for version `0.4.0`, 37 expected `dist` files.
- Consumer compile against both public package subpaths: passed.
- Built runtime package imports for all changed functions: passed.
- VS Code diagnostics for changed TypeScript files: no errors.

### Deviations

None.

### Assumptions

- Exception mapping is per observed span. Consumers sanitize each nested helper
  that can observe a rethrown failure, matching the per-helper metric control.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation resolves the BACKGROUND-008 shared-package capability gap
without collapsing the granular span and metric tasks:

- `GenAIObservationOptions.recordMetrics` is an additive trailing option on the
  existing turn, agent and tool helpers;
- omitted/default options preserve the accepted 0.4.0 behavior, including the
  SHARED-011 metrics;
- `recordMetrics: false` bypasses only the metric wrapper and still executes the
  same `withObservedSpan` path, preserving active-context nesting and span
  success/error status;
- no replacement instruments, alternate providers or service-specific metric
  semantics were introduced;
- `ObservedSpanOptions.mapException` provides an explicit caller-owned
  sanitization boundary before `span.recordException`;
- mapped exception string fields are bounded to 1,024 characters;
- if the supplied mapper fails, the helper does not fall back to the original
  potentially sensitive Error/value;
- span status still becomes ERROR on application failure even when mapped
  exception recording is omitted;
- the original thrown Error/value is rethrown unchanged by identity/value;
- when no mapper is supplied, existing exception behavior remains unchanged for
  backward compatibility;
- no CommerceAgent/background business semantics, prompts, messages, tool
  payloads, provider response bodies, credentials or customer identifiers were
  added to the shared runtime.

Direct source/test inspection confirms the new tests cover spans-only nesting,
zero GenAI metrics under suppression, safe mapped exceptions, mapper-failure
isolation, original-value rethrow and sensitive-value exclusion.

The Completion Report records:

- focused GenAI tests: 4 passed;
- repository tests: 63 passed, 1 Redis-dependent test skipped, 0 failed;
- typecheck passed;
- production build passed;
- package dry-run passed at existing version 0.4.0;
- consumer-style public-subpath compile/import checks passed.

The compressed review workspace contains no `node_modules`, so architect review
did not rerun the implementation suite. This is not a defect; validation
evidence is corroborated by direct source and test review.

Package/version state also confirms the Stop Condition was respected:
`package.json` and `package-lock.json` remain at 0.4.0 and SHARED-013 was not
started.

`ARCH-002-SHARED-012` is architecturally Complete.

`ARCH-002-SHARED-013` may now move to `ready` as a publication-only task.
