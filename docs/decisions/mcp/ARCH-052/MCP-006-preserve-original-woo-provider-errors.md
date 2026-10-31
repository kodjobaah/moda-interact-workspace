---
id: ARCH-052-MCP-006
architecture_id: ARCH-052
title: Preserve actual WooCommerce REST and transport errors in direct MCP product reader
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 45
executor: copilot
claimed_at: 2026-10-31T05:12:35Z
attempt: 1
depends_on:
  - ARCH-052-MCP-005
enables:
  - ARCH-052-SYSTEM-TEST-002
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-052-MCP-006: Preserve original WooCommerce provider errors

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. **Defined but not materialised**; this is an
implementation task specification, not an execution claim.

## Objective

Restore actual WooCommerce REST/provider and SDK/transport failure diagnostics
at the accepted MCP-005 direct product-reader boundary, without changing its
security policy, returned MCP tool contract or read semantics.

## Context

Inspected `moda-interact-mcp/src/connections/woocommerce/direct-product-reader.ts`
in the 31 October snapshot: failed Woo HTTP statuses are reduced to
`MCP_WOOCOMMERCE_PROVIDER_FAILED`/`AUTH_REJECTED`; request errors are caught
without logging their original `Error.message`; JSON error bodies from Woo are
available as bounded `HttpResult.body` but are discarded. MCP-005 has already
been accepted; do not rewrite its Completion Report or implementation history.
MCP-003 implements product search/exact reads and Shopify projection separately;
there is no reason to block it on this diagnostic-only correction.

## Scope

- Modify only `src/connections/woocommerce/direct-product-reader.ts`, its
  direct-reader tests and narrowly necessary error-log fixtures **in MCP**.
- On a Woo HTTP failure (including 400/401/403/404/429/5xx), extract the
  **original** source `code` and `message` from Woo JSON when supplied; log
  actual status and a trusted request ID if supplied. When no JSON `error`
  object exists, preserve the actual source error response body safely if
  readable; do not replace it with a guessed explanation.
- For DNS/TLS/timeout/request exceptions without an upstream HTTP response,
  record actual originating `Error.name`, `Error.message` and available cause,
  labelled `origin:sdk_exception`; do not fabricate a Woo provider message.
- Log via the existing `@modainteract/moda-interact-shared/logging` logger.
  Preserve existing `McpRequestError` code/status/retryability externally; its
  safe public MCP error response remains unchanged.

## Out of Scope

- No new Woo endpoint, grant flow, DNS/SSRF/rebinding logic, request budget,
  provider mutation, credential/keyring mechanism, database/Shared contract,
  public error payload or new logger. No change to MCP-005 accepted task state.
- No product search implementation, GraphQL/Shopify adapter changes, additional
  remote requests or edits to another repository.

## Requirements

1. At the existing bounded `HttpResult` decision point, classify HTTP failures
   using the current stable `McpRequestError` mechanism **after** capturing
   diagnostic source data. Woo REST errors may be `{"code":"...","message":"...","data":{"status":400}}`
   rather than a nested `{"error":...}`; accept actual structured provider
   error shapes only, not invented labels. Source `code`, `message` and safe
   bounded `data` remain verbatim except marked secret/PII redaction/truncation.
2. Preserve original error for 401/403/404 as well as generic 4xx/5xx, while
   preserving existing security-denial/not-found behaviour. Never turn a
   provider-denied result into success or a retry against another tenant.
3. For caught `database.shop.findUnique`, DNS, TLS, HTTP request, JSON parsing,
   credential/keyring or eligibility exceptions, log the actual original
   exception `name`/`message`/cause and separate Moda reason at the owning
   failure boundary. **Credential exception messages may contain secrets**:
   redact unsafe spans before logging; do not print decrypted material. An
   internally generated configuration failure has `origin:internal`, not a
   fabricated Woo provider response.
4. Use a bounded, redacted, read-only snapshot of the **error response only**;
   do not log complete REST success responses, authorization headers,
   credentials, customer information, product records, source URLs or cookies.
   Apply the provider-origin policy in `docs/observability/shared-logging.md`.
   When a safe source message cannot be extracted, emit safe source status/code
   with `redactionApplied:true` and `[REDACTED]` for unsafe text; never
   replace it with a guessed message. Request ID comes from a known header only,
   never all response headers. Logging sink failure must not fail a provider read.
5. Source `providerError` data stays **server-side** in Shared structured logs.
   Never place its body or message in published `CommerceToolResult`, MCP
   `isError` content, model tool results or public HTTP error details. Retain
   existing deadlines, grant revocation checks, SSRF/DNS pinning and timeouts.

## Work Items

- [ ] At Woo HTTP non-success handling, capture actual Woo error shape,
  permitted request ID and redacted/bounded source body before existing typed
  `McpRequestError` conversion, with no extra HTTP request.
- [ ] Record original non-response exception `name`/`message`/cause at each
  existing catch that currently discards it, while not logging credentials.
- [ ] Add focused tests covering HTTP 400/401/403/404/429/503 original error
  shapes, non-JSON error body, missing body, TLS/timeout/DB failures,
  redaction/truncation, existing MCP response and unchanged grant/security.
- [ ] Run owning repository's declared focused tests, typecheck/build and
  `git diff --check`; record execution results and worktree evidence.

## Interfaces / Contracts

Consumed existing MCP-local `ApprovedWooProductReader.read`, `HttpResult`,
`McpRequestError`, `McpServicePorts.logger` and published Shared logger. No
wire-contract field, schema version, package publication or HTTP error response
change. Source log fields: `origin`, `provider=woocommerce`, `operation`,
`httpStatus`, `providerRequestId`, actual `providerError.code/message/details`
or bounded `providerErrorBody`, `redactionApplied`, `truncated`, plus **separate**
`reasonCode` and shop/request correlation. For transport-only failures emit
`origin:sdk_exception` and actual exception name/message, not a fake provider
error. No new generic log serializer or secret redaction framework.

## Dependencies

- `ARCH-052-MCP-005` — accepted direct WooCommerce REST reader.

## Enables

- `ARCH-052-SYSTEM-TEST-002` — final Woo provider-origin logging validation.

## Acceptance Criteria

- [ ] Provider supplies `{"code":"woocommerce_rest_invalid_product_id","message":"Invalid product ID."}`:
  logged provider code/message match those literal source values after safe
  redaction; the outward MCP failure still uses the existing typed code.
- [ ] Distinct 401/403/404/429/503 provider messages and approved request IDs
  are preserved without leaking provider response bodies to MCP clients or AI.
- [ ] Network/SDK/Prisma-only error logs actual original exception and no
  invented upstream error text. Secret-bearing/PII-bearing error details are
  redacted with visible flags; allowed source message text is not paraphrased.
- [ ] Existing grant, tenant, redirect, DNS pinning, cert, response size,
  cancellation, timeout, typed failure, retry and product read tests still pass.
- [ ] No new provider call, Shared schema, persistent error row, logger utility
  or modification to previously accepted MCP-005 task documentation.

## Validation

- [ ] Focused direct Woo REST reader tests with injected `HttpResult` and
  `Error`/logger sink; assert literal source message and absence of synthetic
  provider explanation; verify redaction of tokens, email and signed query.
- [ ] Existing MCP reader security tests including cross-tenant and redirect
  tests; repository declared typecheck/build and `git diff --check`.
- [ ] Launcher-resolved dedicated parent/implementation worktrees,
  synchronization and submodule evidence recorded in Completion Report.

## Stop Condition

After Work Items, Acceptance Criteria and Validation are complete, set the task
to `review`, return the implementation/report to `moda_architect`, and STOP.
Do not start MCP-003, modify indexes or other task files, merge/push main or
self-accept.

## Implementation Notes

Do not add a second reusable logging/redaction implementation. Existing Shared
logger owns generic sanitisation/sink isolation; this task owns only Woo REST
error extraction, original-cause handling and safe provider semantics. Review
`docs/observability/shared-logging.md`, `docs/agent-vcs-ownership-policy.md`
and `docs/agent-worktree-isolation-policy.md`. No rework of accepted MCP-005
behaviour beyond the bounded diagnostic correction is authorized.

## Completion Report

### Status

Not Started — task defined, not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Source status/errors are available via the existing `HttpResult`.

### Unresolved Issues

None established before implementation.

### Architectural Concerns

Escalate any provider-adapter error shape or Shared logger limitation that
prevents secure provenance preservation rather than silently inventing data.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation reviewed; architectural task only.

### Reviewed Files

31 October 2026 workspace source, existing MCP-005 reader, MCP-003 task and
Shared logging policy.

### Validation Reviewed

None for implementation.

### Architecture Conformance

Awaiting implementation review.

### Follow-up

Terminal system test validates the MCP-006 Woo error preservation path.
