---
id: ARCH-021-COMMERCE-057
architecture_id: ARCH-021
title: Preserve actionable provider response diagnostics for live authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 72
executor: copilot
claimed_at: 2026-09-27T11:46:25Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-051
enables:
  - ARCH-021-COMMERCE-058
created: 2026-09-27
updated: 2026-09-27
---

# Preserve actionable provider response diagnostics for live authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Preserve bounded, credential-safe provider response diagnostics when the existing
COMMERCE-051 live External HTTP authoring observation receives a provider response but
cannot decode it under the authored response format.

The authoring caller must be able to distinguish why decoding failed and, when safe,
show the provider status, received media type and a bounded textual body preview.
Production Tool acceptance rules, transport security, provider success semantics and
durable state remain unchanged.

## Context

Manual Automatic-generation testing exposed an information-loss defect.

For this authored Request:

```text
GET https://api.mydummyapi.com/categor/products
```

the provider returns:

```text
HTTP 404
Content-Type: text/html

Cannot GET /categor/products
```

The current transport has enough information to explain the failure, but
`observeExternalHttpDescriptor(...)` collapses decode failures to:

```text
{ kind: "failure", code: "INVALID_RESPONSE", retryable: false }
```

and `createExternalHttpAuthoringObservation(...)` preserves only that generic code.
Studio therefore reports only that the response could not be decoded as JSON and loses
the actionable provider status/media-type/body evidence.

This task corrects that authoring-observation boundary. It does not change whether a
response is valid for Tool execution.

COMMERCE-055 and COMMERCE-056 may already be executing independently. This task MUST
NOT edit, re-gate, reopen or otherwise change either task.

## Scope

Primary implementation is expected in:

```text
moda-interact-commerce/src/commerce/external-http/index.ts
moda-interact-commerce/src/commerce/tool-authoring/external-observation.ts
moda-interact-commerce/src/studio/tools/external-validation-server-actions.ts

moda-interact-commerce/tests/external-http-authoring-observation.test.ts
moda-interact-commerce/tests/external-http-authoring-action.test.ts
moda-interact-commerce/tests/external-http-executor.test.ts
moda-interact-commerce/tests/external-http-live-test.test.ts
```

Additional Commerce-local files may be changed only where required to propagate the
bounded diagnostic contract.

## Out of Scope

- Response-tab Automatic presentation changes; COMMERCE-058 owns those.
- Any change to the accepted `DIRECT | VISUAL | JAVASCRIPT` processing union.
- Any change to `SCALAR`, `OBJECT`, `LIST` or `SCALAR_LIST` semantics.
- Making HTML, malformed JSON or another invalid body acceptable as a Tool response.
- Relaxing HTTPS, DNS/global-address, TLS-hostname, redirect, deadline or body limits.
- Returning provider response headers generally.
- Returning credentials, authorization headers, cookies or resolved credential values.
- Persisting provider observations, test receipts, Tools or Tool revisions.
- Changing production non-2xx handling.
- Reworking the COMMERCE-055 Test UI while that task is already executing.
- Editing or re-gating COMMERCE-056.

## Requirements

### 1. Keep the accepted live-observation boundary

The existing COMMERCE-051 flow remains authoritative:

```text
current Request candidate
    -> preview exact safe request descriptor
    -> authorize ADMIN / shop scope
    -> resolve immutable Connection + credentials server-side
    -> existing secure External HTTP transport
    -> bounded provider observation
```

Do not create a second HTTP client or a second request-construction path.

### 2. Preserve a typed provider-response diagnostic

When a provider response exists but cannot become the authored `TransformResponse`, the
authoring observation must preserve one bounded diagnostic equivalent to:

```ts
type ProviderResponseDiagnosticReason =
  | "MISSING_CONTENT_TYPE"
  | "UNEXPECTED_MEDIA_TYPE"
  | "UNSUPPORTED_CHARSET"
  | "INVALID_UTF8"
  | "NUL_CONTENT"
  | "MALFORMED_JSON"
  | "UNSAFE_JSON_VALUE"
  | "UNSUPPORTED_CONTENT_ENCODING"
  | "BODY_TOO_LARGE"
  | "BODY_READ_FAILED";

type ProviderResponseDiagnostic = {
  reason: ProviderResponseDiagnosticReason;
  status: number;
  expectedMediaTypes: readonly string[];
  receivedMediaType: string | null;
  bodyPreview: string | null;
  bodyPreviewTruncated: boolean;
};
```

Equivalent repository-local naming is acceptable, but the information and reason
distinctions above are mandatory.

The diagnostic is attached only to an authoring/live-observation
`providerRequest / INVALID_RESPONSE` failure. Other failure categories retain their
existing contracts.

### 3. Diagnostic collection must be explicitly authoring-only

The secure transport helper may be refactored to retain the diagnostic information, but
rich provider diagnostics MUST be produced/propagated only for the explicit
authoring/live-observation path that currently opts into non-success observations.

Production Tool execution continues to consume the accepted production result contract
and MUST NOT expose provider body diagnostics to the CommerceAgent.

### 4. Preserve HTTP status even when decoding fails

Once an HTTP response has been received, decode failure must not discard its status.

For the reproduced defect the observation must retain:

```text
status: 404
receivedMediaType: text/html
expectedMediaTypes: [application/json]
reason: UNEXPECTED_MEDIA_TYPE
```

### 5. Preserve a safe bounded textual preview

Where the received body has already been bounded by the existing response-body limit
and can safely be represented as text:

- decode with the same strict UTF-8 safety used by the External HTTP boundary;
- do not execute or render markup as HTML;
- retain at most **4096 UTF-8 bytes** in `bodyPreview`;
- truncate only at a valid UTF-8 boundary;
- set `bodyPreviewTruncated: true` when truncation occurs;
- never include response headers, credentials or request authorization values in the
  preview.

A body that is not safely representable as text may use `bodyPreview: null`.

### 6. Preserve exact decode reasons

At minimum, the transport/decoder must distinguish the mandatory reasons listed in
Requirement 2 instead of converting all of them directly to one unqualified null
decode result.

Examples:

```text
no Content-Type                     -> MISSING_CONTENT_TYPE
text/html when JSON is expected     -> UNEXPECTED_MEDIA_TYPE
unsupported declared charset        -> UNSUPPORTED_CHARSET
invalid UTF-8                       -> INVALID_UTF8
NUL-containing text                 -> NUL_CONTENT
application/json with invalid JSON  -> MALFORMED_JSON
JSON outside accepted value bounds  -> UNSAFE_JSON_VALUE
unsupported Content-Encoding        -> UNSUPPORTED_CONTENT_ENCODING
decompressed body exceeds bound     -> BODY_TOO_LARGE
other bounded body/decode failure   -> BODY_READ_FAILED
```

`DEADLINE`, connection resolution and provider transport failures remain their existing
non-`INVALID_RESPONSE` failure categories.

### 7. Keep successful observations source-compatible

A valid successful JSON observation must retain the accepted COMMERCE-051 response
shape and behaviour.

Existing callers that do not inspect the new diagnostic must remain source/behaviour
compatible.

### 8. Keep COMMERCE-054 compatible

COMMERCE-054 is already Complete and composes the COMMERCE-051 observation boundary for
live Test execution. The additive diagnostic work must not regress its stage model,
response processing or result validation.

This task does not require Test UI changes. If COMMERCE-055 does not present the richer
diagnostics when returned for review, that is a separate architect decision after its
current attempt finishes.

## Work Items

- [x] Refactor bounded body/decode outcomes so invalid provider responses retain the
      mandatory diagnostic reason.
- [x] Add the bounded provider-response diagnostic contract to the live authoring
      observation path.
- [x] Preserve status, expected media types and received media type for decode failures.
- [x] Add a credential-safe UTF-8 body-preview helper bounded to 4096 UTF-8 bytes.
- [x] Propagate the diagnostic through `createExternalHttpAuthoringObservation(...)`
      and the existing Server Action without creating another HTTP path.
- [x] Keep successful COMMERCE-051 observations unchanged.
- [x] Keep production External HTTP execution semantics unchanged.
- [x] Add the exact 404 `text/html` regression.
- [x] Add malformed-JSON and remaining mandatory reason regressions.
- [x] Re-run the affected COMMERCE-054 live-Test backend regressions.

## Interfaces / Contracts

Consumed:

```text
COMMERCE-051 live External HTTP authoring observation
ExternalRequestDescriptor
ExternalResponseFormat
TransformResponse
existing secure External HTTP transport
```

Produced:

```text
additive bounded ProviderResponseDiagnostic
only for providerRequest / INVALID_RESPONSE live-authoring failures
```

No cross-repository contract is introduced.

## Dependencies

- `ARCH-021-COMMERCE-051`

## Enables

- `ARCH-021-COMMERCE-058`

## Acceptance Criteria

- [x] `404 text/html` for a JSON response format produces
      `stage: providerRequest`, `code: INVALID_RESPONSE`, `retryable: false`.
- [x] That failure also carries `reason: UNEXPECTED_MEDIA_TYPE`, `status: 404`,
      `receivedMediaType: text/html` and expected media type `application/json`.
- [x] For the body `<pre>Cannot GET /categor/products</pre>` (or the equivalent
      provider HTML page), the safe textual preview contains
      `Cannot GET /categor/products`.
- [x] A `200 application/json` body containing malformed JSON reports
      `MALFORMED_JSON`, not `UNEXPECTED_MEDIA_TYPE`.
- [x] Missing Content-Type, unsupported charset, invalid UTF-8, NUL content, unsafe
      JSON value, unsupported content encoding, oversized body and body-read failure
      have deterministic distinct reasons.
- [x] `bodyPreview` is never more than 4096 UTF-8 bytes and truncation is reported.
- [x] Markup is returned only as text data; no diagnostic path introduces HTML
      execution/rendering.
- [x] Credentials, authorization headers, cookies and general provider response
      headers are absent from the browser-visible diagnostic contract.
- [x] Valid JSON successful observations retain the accepted COMMERCE-051 shape.
- [x] Production Tool execution still rejects/handles invalid/non-success provider
      responses exactly as before this task.
- [x] COMMERCE-054 live-Test backend regressions remain passing.
- [x] No Tool, ToolRevision, audit, receipt or publication-proof write is introduced.
- [x] COMMERCE-055 and COMMERCE-056 task state/scope are unchanged by this task.

## Validation

Before running commands, inspect `moda-interact-commerce/package.json` and use the
repository scripts that actually exist.

Required focused validation:

- [x] External HTTP executor/security tests covering body/decode bounds.
- [x] COMMERCE-051 authoring-observation tests.
- [x] Authoring Server Action tests.
- [x] COMMERCE-054 live-Test backend tests.
- [x] Exact `404 text/html` + `Cannot GET /categor/products` regression.
- [x] Malformed JSON and mandatory diagnostic-reason regressions.
- [x] Targeted lint for changed files.
- [x] Changed-file TypeScript diagnostics.
- [x] `git diff --check`.

Do not turn unrelated documented repository baseline failures into task-owned work.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete,
set the task to `review`, return the Completion Report to `moda_architect` and STOP.
Do not begin COMMERCE-058 or modify the currently executing COMMERCE-055/056 tasks.

## Implementation Notes

Prefer an additive typed diagnostic over parsing error-message strings in React.

The authoritative distinction is:

```text
provider returned a response
        |
        +-- accepted under authored response format -> normal observation
        |
        +-- not accepted -> INVALID_RESPONSE + bounded diagnostic reason/evidence
```

Do not weaken the accepted response format merely to obtain a preview.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

- `src/commerce/external-http/index.ts`
- `src/commerce/tool-authoring/external-observation.ts`
- `tests/external-http-authoring-action.test.ts`
- `tests/external-http-authoring-observation.test.ts`

### Work Completed

- Added a typed `ProviderResponseDiagnostic` contract with deterministic reasons, response status, expected media types, sanitized received media type, and an optional bounded textual preview.
- Refactored body reading and response decoding to preserve distinct reasons for unsupported encoding, oversized/read-failed body, missing or unexpected media type, unsupported charset, invalid UTF-8, NUL, malformed JSON and unsafe JSON values.
- Added a strict UTF-8 preview helper that excludes invalid/NUL text, redacts resolved/request credential values, truncates at a valid UTF-8 boundary to at most 4096 bytes, and reports truncation.
- Emits and propagates diagnostics only when the existing `includeNonSuccessResponses` live-authoring observation path is explicitly enabled. Production execution still maps invalid responses to `UNAVAILABLE` and does not receive preview details.
- Preserved the existing Server Action result shape additively and added coverage proving the diagnostic passes through without exposing response headers or adding mutations.
- Added the exact 404 HTML regression, malformed JSON and all mandatory reason cases, oversized/read-failed body coverage, UTF-8 truncation/redaction coverage, and retained successful-observation/production executor behavior.

### Validation Results

- Launcher preparation passed for Attempt 1: dependency `ARCH-021-COMMERCE-051` is complete; task claim was committed/pushed. Dedicated mirrored worktrees are parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-057` and implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-057`; recursive submodule initialization passed with `database` at pinned commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Passed: `./node_modules/.bin/vitest run tests/external-http-authoring-observation.test.ts tests/external-http-authoring-action.test.ts tests/external-http-executor.test.ts tests/external-http-live-test.test.ts` (4 files, 64 tests), covering COMMERCE-051 authoring, action propagation, production transport/executor and COMMERCE-054 live Test.
- Passed: targeted ESLint for all four changed files; `git diff --check`.
- `./node_modules/.bin/tsc --noEmit --pretty false` reports existing repository-wide errors, including missing generated Prisma Client exports and unrelated preview imports/types. Filtering the output for all four changed files found no TypeScript diagnostics in task-owned changes. Prisma generation was not required for the focused tests and no schema/submodule change was made.
- The first `pnpm exec vitest` invocation attempted pnpm auto-install and stopped because pnpm blocked dependency build scripts. Retried using the installed local Vitest binary; focused tests passed. The two generated untracked pnpm metadata files were removed and are not part of the task diff.

### Deviations

None. No production acceptance, transport security, status mapping, persistence, COMMERCE-055 or COMMERCE-056 behavior was changed.

### Assumptions

- Redaction removes exact resolved authentication values and values of request headers with credential-bearing names before exposing any valid textual body preview. General response headers are never included.

### Unresolved Issues

The repository-wide TypeScript check remains blocked by missing generated Prisma Client types and unrelated existing diagnostics; no changed-file diagnostics were reported.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
