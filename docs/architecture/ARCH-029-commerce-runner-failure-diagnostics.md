---
id: ARCH-029
title: CommerceAgent runner failure provenance and operational diagnostics
status: proposed
coordinator: moda_architect
created: 2026-10-10
updated: 2026-10-10
---

# ARCH-029: CommerceAgent runner failure provenance and operational diagnostics

## Status

Proposed, for the developer's review. This is a bounded diagnostic-correctness initiative, not a redesign of the CommerceAgent runner, MCP or provider retry policy.

## Problem

As inspected in the 2026-10-09 workspace snapshot (`@modainteract/moda-interact-shared` 1.3.5), several errors with different causes collapse to the same public code without retaining diagnostic provenance:

- Shared `src/commerce/model/openrouter-model-client.internal.ts` classifies provider HTTP 401/403/429 and malformed provider responses through optional `onDiagnostic`, then throws a generic `Commerce model unavailable` error. The Background production model does not register that callback.
- Background `src/commerce/production-model.ts` catches credential/client/provider errors and replaces all of them with `Commerce model invocation failed`.
- Shared `src/commerce/runner/runtime.ts` catches dependency exceptions and replaces them with `RunnerFailure("UNAVAILABLE")` without origin metadata.
- Shared `src/commerce/runner/failure.ts` maps unexpected uncategorised errors to `INVALID_INPUT`.
- Shared `src/commerce/runner/final-response.ts`, `preflight.ts`, `model-step.ts`, `tool-execution.ts`, and `evidence.ts` use broad failure codes for distinct schema/policy conditions.
- Shared `src/commerce/runner/index.ts` creates the child logger only after preflight; preflight failures may emit no `commerce.turn.failed` event. Terminal failure events currently contain a public code, retryability, counters and duration, not the actual failure stage/reason.
- Background `src/commerce/host.ts` maps the returned runner failure to a `CommerceHostError` with only code/retryability and also loses information on unexpected host failures. The MCP transport in `src/commerce/mcp-client.ts` maps diverse non-2xx responses to `UNAVAILABLE` without status diagnostics.

The public codes are useful for stable orchestration, but are insufficient to debug failures. Simply placing raw `Error.message`, provider bodies or Zod `.format()` in the returned error is unsafe and is not the target design.

## Goals

1. For every runner failure, preserve **stage**, a stable **reasonCode**, and the already-established public `code`/`retryable` classification.
2. Record safe, bounded contextual metadata when available: `modelStep`, `remoteCallNumber`, `attempt`, `toolName`, upstream HTTP status, numeric provider code, count of validation issues and a bounded allowlisted schema-path summary.
3. Preserve the original exception internally using `cause` where appropriate; do not silently overwrite cause chains at service boundaries.
4. Emit a correlated terminal structured failure event for preflight failures and graph/runtime failures as well as failures after runner startup.
5. Make production model/credential/MCP origin diagnostics visible in Background, as Commerce Test Conversations already partially do through OpenRouter's optional `onDiagnostic` callback.
6. Retain existing business outcome, authorization, budgets, retry policy, tool-call count and customer-visible reply behaviour.
7. Use the canonical Shared logger; diagnostic logging failure must not change execution outcomes.

## Non-Goals

- Replacing LangGraph, the MCP SDK, OpenRouter, or the canonical Shared logger.
- Returning raw provider response text, credentials, model outputs, tool arguments, customer data, Zod received values or raw exception stacks to customers/staff UI.
- Adding duplicate HTTP/LLM/BullMQ metrics already emitted by approved instrumentation.
- Changing the meaning of existing `RunnerErrorCode` values or retryability in this diagnostic-only initiative. Any future retry-policy correction must be separately reviewed.
- Altering response content, referral decisions, evidence rules, authorization or budgets.
- Adding database migrations, new queues, a new service or Gateway infrastructure.

## Current Architecture

The canonical Shared runner orchestrates `resolveAvailableTools -> invokeModel -> executeToolCalls -> validateFinalResponse`, with loops back to tool resolution. `runCommerceTurn` returns either a final result and usage or `{ ok: false, error: { code, retryable } }`. A `RunnerFailure` carries only the broad code. The terminal event `commerce.turn.failed` does not contain the underlying exception, stage or reason. The Background production model erases provider causes, while the Commerce Preview model records provider diagnostics through a separate callback.

## Proposed Architecture

### A. Two levels of error identity

Keep the **public behaviour code** (`UNAVAILABLE`, `INVALID_FINAL`, `INVALID_INPUT`, etc.) and its existing retryability. Add a **safe structured diagnostic**:

```ts
{
  stage: "model.invoke",             // finite runner/host stage vocabulary
  reasonCode: "PROVIDER_RATE_LIMITED", // finite, stable reason vocabulary
  statusCode: 429,                    // optional, bounded numeric HTTP status
  modelStep: 1                       // optional, bounded counter
}
```

The example is illustrative, not a request to emit unfiltered provider errors. Define an exported, typed diagnostic contract suitable for internal hosts. Attach it optionally to the failed `RunCommerceTurnResult.error` without changing `code`, `retryable` or successful response shape. For old asserted results, update tests to explicitly validate the new safe diagnostic contract. No diagnostic becomes model input or a customer-visible reply. An internal consumer must not render this diagnostic verbatim to customers.

Use stable reasons at their source. Required distinctions include at least:

- preflight: invalid turn/grant/manifest, response-contract mismatch, unsafe/oversized input and invalid budget;
- runtime: caller cancellation, turn deadline and bounded operation timeout;
- model: provider auth, rate limit, HTTP failure, request failure and malformed response; malformed model-step shape and invalid call routing;
- tool: current authorization failure, invalid input schema, execution exception, oversized/invalid result and a structured tool error;
- evidence/final: invalid evidence, expired evidence, invalid final-response schema, mandatory referral mismatch, and evidence-reservation budget exhaustion;
- unexpected graph/runtime exception, even when its existing public code is retained for compatibility.

Do not create one reason for each source line. Prefer a compact typed taxonomy that identifies the failed invariant or external boundary.

### B. Preserve cause, log an allowlisted diagnostic

`RunnerFailure` may retain `cause` for internal propagation. At the terminal boundary, log `errorCode`, `retryable`, `stage`, `reasonCode` and the allowlisted safe metadata through `@modainteract/moda-interact-shared/logging`. The logger's redaction is defence-in-depth; do not send arbitrary provider/exception objects, raw model messages or full Zod error objects. Unknown thrown values receive a stable `UNEXPECTED_EXCEPTION` reason plus a bounded safe origin/type, not a potentially sensitive raw message.

Make the root logger available before preflight; emit failure logs even when no validated turn identity exists. Never log raw unvalidated identifiers or payloads merely to recover context. Once preflight succeeds, retain the existing child logger's shop, conversation, inbound version and grant correlation fields.

Structured tool outcome errors (`DENIED`, `THROTTLED`, etc.) continue to be logged as tool outcomes, not automatically promoted to terminal runner errors. Diagnostic enrichment must not introduce new retries or remote calls.

### C. Host integration

Background `production-model.ts` supplies OpenRouter's already-supported `onDiagnostic` callback and logs a safe model-selection/stage/reason/status event. Separate credential-resolution failures (missing row, key unavailable, decryption failed, database read failed, cancellation) by safe reason rather than recording ciphertext or secrets. Preserve/relay safe diagnostic provenance through generic host adapters where possible.

Background MCP/host logs distinguish connection, manifest, tool listing, authorization, tool call and response parsing, including bounded HTTP status. Preserve existing host error codes and handling. Commerce Test Conversations consume the published Shared diagnostic-capable runner and retain their existing staff-only model diagnostic path without displaying provider internals to customers.

### D. Failure observability and correlation

Retain `commerce.turn.failed` as the terminal event. Extend its data rather than replacing its event name. Emit at most one terminal event per failed runner execution; other stage-specific events may exist but must serve a distinct investigative purpose. Ensure every event can be correlated through the existing shop/conversation/inbound version or an existing preview run ID when available. Do not add high-cardinality metric labels.

## Runtime/Contract Boundaries

| Boundary | Owner | Behaviour |
|---|---|---|
| `RunCommerceTurnResult.error` / diagnostic | `moda_shared` | Bounded typed internal failure contract; public code and retryable unchanged |
| OpenRouter diagnostic and runner failure provenance | `moda_shared` | Safe origin metadata and terminal shared logger event |
| Background credential/model diagnostics | `moda_background` | Register existing adapter diagnostic callback; preserve provider/credential stages |
| Background MCP/host diagnostics | `moda_background` | Correlate transport/host stages and preserve service classification |
| Test Conversation consumer | `moda_commerce` | Upgrade published dependency and validate staff-only internal diagnostics |
| End-to-end verification | `moda_system_test` | Verify diagnostic origin and non-disclosure under real host boundaries |

## Security

The public/customer-facing error code remains bounded. Never log `credential`, Authorization headers, full provider errors or bodies, prompt/history, model output, tool arguments or whole Zod objects. `statusCode` and provider numeric `providerCode` are bounded. Validation diagnostics include only issue code and allowlisted field path, never `received`, content or arbitrary dynamic keys. Original exceptions may be retained as `cause` in memory; raw causes must not automatically be serialised. Diagnostic sinks remain best-effort and failure-isolated.

## Consistency, Retries, Scaling and Failure Handling

No durable-state change. No new remote calls, synchronous telemetry network activity, retries, blocking logging, provider calls or queue operations. Preserve exact existing cancellation/deadline semantics and per-turn budgets. Safe event cardinality is proportional to actual failed turns, not raw Shopify ingress. Existing OpenTelemetry/runtime instrumentation is reused without custom metric duplication.

## Rollout / Migration

The project snapshot is a development snapshot; verify deployment state before publication. This is an additive shared-contract change preserving existing `code`/`retryable` and result success semantics. Publish the accepted Shared implementation as a separate release gate. Upgrade Background and Commerce consumers only after the package is available. No database migration or Gateway task is required. Never claim the published version or consumer upgrade occurred solely because this proposal was written.

## Decisions / Tasks

| Task | Owner | Planned status | Depends on |
|---|---|---|---|
| ARCH-029-SHARED-001 | moda_shared | Ready after developer agrees to proposal | — |
| ARCH-029-SHARED-002 | moda_shared | Pending | SHARED-001 |
| ARCH-029-BACKGROUND-001 | moda_background | Pending | SHARED-002 |
| ARCH-029-BACKGROUND-002 | moda_background | Pending | SHARED-002 |
| ARCH-029-COMMERCE-001 | moda_commerce | Pending | SHARED-002 |
| ARCH-029-SYSTEM-TEST-001 | moda_system_test | Pending | BACKGROUND-001, BACKGROUND-002, COMMERCE-001 |

System testing is terminal: no implementation or publication task depends on a system-test task. The developer may manually validate consumers before invoking system tests.

## Open Questions

- Whether the internal Preview UI should display the safe stage/reasonCode in its staff-only trace; this proposal only requires it in internal logs/trace data, never customer output.
- Whether future operational policy should revise unexpected-exception `INVALID_INPUT` classification; diagnostics are corrected here without silently changing retries.

## Change History

- 2026-10-10 — Proposed after inspecting the 2026-10-09 package, Background and Commerce snapshot. No implementation, release or repository branches created.
