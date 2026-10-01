---
id: ARCH-024-SHARED-003
architecture_id: ARCH-024
title: Add structured Commerce turn runtime logging
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 22
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-024-SHARED-002
enables:
  - ARCH-024-SHARED-004
created: 2026-10-01
updated: 2026-10-01
---

# Add structured Commerce turn runtime logging

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Instrument the modular Shared Commerce turn runtime with a small stable semantic event taxonomy using the existing canonical `StructuredLogger`, so production Background turns and Commerce Test Conversations can be traced through the same runner without logging prompts, customer content, Merchant Knowledge content, Tool arguments/results, credentials or raw provider payloads.

## Context

The canonical generic logging API already exists at:

```text
@modainteract/moda-interact-shared/logging
```

and `docs/observability/shared-logging.md` explicitly prohibits service-local competing loggers. Shared runner instrumentation therefore receives a host-created `StructuredLogger`; the runner MUST NOT call `createLogger()` with a fabricated `moda-interact-shared` service identity.

The host service remains authoritative for:

```text
service.namespace
service.name
deployment.environment.name
```

The runner adds only safe Commerce-turn/component context and semantic events.

## Scope

Authorised implementation surface:

```text
src/commerce/runner/types.ts
src/commerce/runner/index.ts
src/commerce/runner/observability.ts              CREATE
src/commerce/runner/observability.test.ts         CREATE
src/commerce/runner/runner.test.ts                 only where required for logging/failure-isolation coverage
```

Focused updates to already-created SHARED-002 modules are allowed only to emit the events specified below. Do not move policy responsibility between modules while adding logging.

## Out of Scope

- Creating a new generic logger.
- Creating a logger inside Shared with a new service identity.
- Metrics or spans that duplicate existing framework/OpenTelemetry signals.
- New OpenTelemetry SDK initialization.
- Grafana-specific application semantics.
- Logging full prompts/messages/context/Tool payloads/provider payloads.
- Logging Merchant Knowledge chunks or uploaded spreadsheet/document content.
- Logging customer name/email/phone/address or other unnecessary customer content.
- Logging credentials, ciphertext, nonce, authTag, headers or key material.
- Changing runner outcomes, retries, budgets, ordering or trust semantics.
- Background/Commerce host wiring; their existing ARCH-024 consumer tasks supply the logger after SHARED-004 is published.

## Requirements

### R1 — extend the runner dependency contract only with an optional StructuredLogger

Import the existing type from the same package logging module and extend `RunCommerceTurnInput.dependencies` additively:

```ts
import type { StructuredLogger } from "../../logging";

export type RunCommerceTurnInput = {
  // existing fields unchanged
  dependencies: {
    model: CommerceModelInvoker;
    tools: RunnerTool[];
    now: () => number;
    digest: Digest;
    logger?: StructuredLogger;
  };
  // existing budgets unchanged
};
```

The field is optional for backward compatibility. ARCH-024 Commerce/Background consumer tasks are nevertheless required to pass their existing host logger.

Do not expose logger configuration/environment parsing through the runner API.

### R2 — add one semantic logging adapter, not a second logger

Create:

```text
src/commerce/runner/observability.ts
```

It may import only the canonical `StructuredLogger`/`LogFields` types from Shared logging and expose bounded semantic helpers. It MUST NOT implement JSON serialization, redaction, sinks, levels or OpenTelemetry transport.

Every logger call MUST be failure-isolated even if a caller supplies a noncanonical logger object whose method throws. Use an internal helper equivalent to:

```ts
function safeLog(
  logger: StructuredLogger | undefined,
  level: "debug" | "info" | "warn" | "error",
  event: string,
  fields: LogFields,
): void {
  try {
    logger?.[level](event, fields);
  } catch {
    // Logging can never affect Commerce-turn correctness.
  }
}
```

### R3 — create one runner child logger with safe stable context

After preflight has validated the turn/grant/manifest and before graph execution, derive:

```ts
const turnLogger = input.dependencies.logger?.child({
  component: "commerce-turn-runner",
  runnerVersion,
  shopId: prepared.turn.shopId,
  checkoutRecoveryId: prepared.turn.checkoutRecoveryId,
  conversationId: prepared.turn.conversationId,
  inboundVersion: prepared.turn.inboundVersion,
  grantId: prepared.grant.id,
  releaseId: prepared.grant.releaseId,
});
```

Do not invent a new random correlation ID. Existing safe turn identity (`conversationId` + `inboundVersion`) is sufficient and can correlate host/runner events.

If `checkoutRecoveryId` is optional in the accepted turn contract, include it only when present.

### R4 — exact stable event taxonomy

Emit only these new runner event names in ARCH-024:

```text
commerce.turn.started
commerce.turn.model.started
commerce.turn.model.completed
commerce.turn.model.invalid
commerce.turn.tool.denied
commerce.turn.tool.started
commerce.turn.tool.retry
commerce.turn.tool.completed
commerce.turn.evidence.accepted
commerce.turn.completed
commerce.turn.failed
```

Do not create alternate spellings for the same lifecycle event.

### R5 — exact event levels and safe fields

Use:

```text
commerce.turn.started            info
commerce.turn.model.started      debug
commerce.turn.model.completed    debug
commerce.turn.model.invalid      warn
commerce.turn.tool.denied        warn
commerce.turn.tool.started       debug
commerce.turn.tool.retry         warn
commerce.turn.tool.completed     debug
commerce.turn.evidence.accepted  debug
commerce.turn.completed          info
commerce.turn.failed             warn or error according to R6
```

Allowed event-specific fields:

```text
commerce.turn.started
  modelStepBudget
  remoteCallBudget
  deadlineMs
  outputTokenBudget

commerce.turn.model.started
  modelStep
  availableToolCount

commerce.turn.model.completed
  modelStep
  requestedToolCount
  finalResponseRequested
  outputTokens
  durationMs

commerce.turn.model.invalid
  modelStep
  reasonCode

commerce.turn.tool.denied
  modelStep
  toolName
  reasonCode   # INSUFFICIENT_TOOLS | TOOL_UNAVAILABLE | TOOL_REVOKED

commerce.turn.tool.started
  modelStep
  toolName
  attempt      # 1 or 2
  remoteCallNumber

commerce.turn.tool.retry
  modelStep
  toolName
  attempt      # completed attempt that triggered retry
  errorCode    # UNAVAILABLE | THROTTLED only

commerce.turn.tool.completed
  modelStep
  toolName
  attempt
  status       # OK | ERROR
  errorCode    # bounded CommerceToolResult code when status=ERROR
  retryable    # only when status=ERROR
  durationMs
  remoteCallNumber

commerce.turn.evidence.accepted
  modelStep
  toolName
  evidenceCount

commerce.turn.completed
  answerKind
  modelSteps
  remoteCalls
  evidenceCount
  durationMs

commerce.turn.failed
  errorCode
  retryable
  modelSteps
  remoteCalls
  durationMs
```

The child logger already carries stable turn/grant/release fields; do not duplicate them on every event.

### R6 — deterministic final failure level

Use `warn` for bounded business/control outcomes:

```text
CANCELLED
DENIED
STALE_TURN
BUDGET_EXHAUSTED
```

Use `error` for final runtime/contract failures:

```text
INVALID_INPUT
INVALID_FINAL
DEADLINE
UNAVAILABLE
INCOMPATIBLE_VERSION
```

No raw exception/provider text is logged by `commerce.turn.failed`.

### R7 — prohibited log content is a hard acceptance rule

The runner MUST NOT intentionally place any of the following in log fields:

```text
PLATFORM_INSTRUCTIONS
hostInstructions
response-contract instruction text
Feature Behaviour prompt text
ModelRequest.instructions
ModelRequest.context
ModelRequest.history
ModelRequest.messages
customer-authored message text
assistant replyText
model/provider raw output
OpenRouter raw response/error body
Tool arguments
CommerceToolResult.data
CommerceToolResult.renderedText
Merchant Knowledge matches/chunks/source content
External HTTP bodies
Shopify response bodies
CommerceEvidence payloads
credentials/tokens/ciphertext/nonce/authTag/key material
Authorization or X-Moda-Commerce-Context header values
customer name/email/phone/address
```

`toolName`, non-secret catalogue/release/grant/turn identifiers, bounded error codes, counts and durations are allowed.

Do not pass whole input/error/result objects to the logger and rely on redaction.

### R8 — logging placement follows module ownership

Required emission points:

```text
runCommerceTurn / graph shell
  commerce.turn.started
  commerce.turn.completed
  commerce.turn.failed

invoke-model node/model-step validator
  commerce.turn.model.started
  commerce.turn.model.completed
  commerce.turn.model.invalid

tool-execution module
  commerce.turn.tool.denied
  commerce.turn.tool.started
  commerce.turn.tool.retry
  commerce.turn.tool.completed

evidence module
  commerce.turn.evidence.accepted
```

Do not log every LangGraph node transition. Semantic lifecycle events are the debugging surface.

### R9 — timings use the injected runner clock

Compute `durationMs` using the same injected `dependencies.now()` clock used by runner deadlines/tests. Do not mix `Date.now()` with the injected clock inside Shared runner instrumentation.

Durations must be nonnegative bounded numbers. Tests with fake clocks must be deterministic.

### R10 — logging failure cannot change any runner result

Add tests proving identical `RunCommerceTurnResult` when:

1. no logger is supplied;
2. a canonical logger with an in-memory sink is supplied;
3. logger methods/child throw deliberately;
4. sink/serialization failure occurs inside the canonical logger.

No logging failure may alter Tool execution count, retry count, model count, final response or error code.

### R11 — verify useful traces without sensitive payloads

Using the canonical logger with an in-memory sink, add deterministic tests for at least:

1. successful final-only turn -> started, model started/completed, completed;
2. one successful Tool round -> Tool started/completed and final completion with correct counts;
3. retryable Tool error -> retry event and exactly two Tool attempts;
4. ungranted/hallucinated Tool -> denied event with bounded reason and no Tool payload;
5. invalid model step -> model.invalid + turn.failed;
6. Merchant-Knowledge-like result containing hostile instructions -> no hostile text appears in any serialized `LogRecord`;
7. provider/error object containing secret-looking payload -> only bounded runner error code appears.

## Work Items

- [ ] Add optional `StructuredLogger` to `RunCommerceTurnInput.dependencies` without breaking existing callers.
- [ ] Create `runner/observability.ts` semantic adapter over the canonical logger.
- [ ] Add safe turn child context after validated preflight.
- [ ] Instrument the exact event points/taxonomy/fields from R4-R8.
- [ ] Add failure-isolation and sensitive-content regressions.
- [ ] Verify no generic logger/metrics/spans were duplicated.
- [ ] Run required validation and complete the report.

## Interfaces / Contracts

Consumes:

```text
@modainteract/moda-interact-shared/logging
StructuredLogger
LogFields
```

Extends additively:

```text
RunCommerceTurnInput.dependencies.logger?: StructuredLogger
```

No new package entrypoint is created.

## Dependencies

- ARCH-024-SHARED-002

## Enables

- ARCH-024-SHARED-004

## Acceptance Criteria

- [ ] Runner uses only the canonical Shared `StructuredLogger` contract.
- [ ] Shared runner never creates its own service logger identity.
- [ ] Host service/environment identity survives unchanged.
- [ ] Exact `commerce.turn.*` taxonomy/levels/fields are implemented.
- [ ] Safe turn/grant/release context is present for correlation.
- [ ] No prompt/customer/Tool/Merchant-Knowledge/provider/credential payload is logged.
- [ ] Logging failure cannot change Commerce-turn behaviour.
- [ ] Existing runner tests and SHARED-002 graph tests remain passing.
- [ ] No duplicate metrics/spans/generic logging mechanism is introduced.

## Validation

From the prepared `moda-interact-shared` task worktree:

```bash
npm run typecheck
npm test
npm run build
npm run validate:commerce-entrypoints
git diff --check
```

Static inspection must also prove runner code imports logging only through Shared's existing logging modules and contains no direct `console.*` logging.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin SHARED-004 publication.

## Implementation Notes

Logging is a diagnostic side effect, never a correctness dependency. The host constructs the service logger; Shared adds a child component context only.

Do not log graph-state objects wholesale. They contain runtime messages/evidence and therefore potentially untrusted/sensitive content.

## Completion Report

### Status

Not Started

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

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
