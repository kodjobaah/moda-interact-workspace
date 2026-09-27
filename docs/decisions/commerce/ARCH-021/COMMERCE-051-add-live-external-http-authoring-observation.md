---
id: ARCH-021-COMMERCE-051
architecture_id: ARCH-021
title: Add bounded live External HTTP authoring observation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 66
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-041
  - ARCH-021-COMMERCE-047
enables:
  - ARCH-021-COMMERCE-053
  - ARCH-021-COMMERCE-054
created: 2026-09-27
updated: 2026-09-27
---

# Add bounded live External HTTP authoring observation

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add one Commerce-owned, ADMIN-authorized server-side capability that executes the **current External HTTP Request authoring candidate** against its selected immutable Connection revision and returns a bounded, credential-redacted provider observation for later Response Automatic generation and Test-tab composition.

This task owns only provider observation. It does **not** infer Visual response rules, process the response into the Tool result, validate `resultSchema`, persist a live-test receipt, or redesign the Response/Test UI.

## Context

The accepted Request work now has two zero-provider-I/O capabilities:

```text
validate request
preview request descriptor
```

`previewExternalRequest(...)` already resolves the current Declarative or JavaScript Request against sample Tool arguments and returns the exact bounded `ExternalRequestDescriptor`:

```text
path
query
safe authored headers
```

The production External HTTP executor already owns the important transport/security mechanics:

```text
immutable Connection revision resolution
server-side credential resolution
HTTPS-only origin
no literal-IP origin
DNS resolution
public/global-address enforcement
address pinning + TLS hostname verification
GET-only transport
no redirects
bounded deadline
bounded decompressed body
strict UTF-8 / response-format decoding
```

However, the production executor deliberately still rejects JavaScript Request execution through its existing compatibility gate. This authoring task must **not** remove that production gate. Live Studio authoring may execute a JavaScript Request only by first using the already-accepted Request preview/processor to produce the safe descriptor, then passing that descriptor through the new authoring observation boundary.

## Scope

Primary implementation files are expected to include:

```text
moda-interact-commerce/src/commerce/external-http/index.ts
moda-interact-commerce/src/commerce/integration/external/index.ts
moda-interact-commerce/src/commerce/tool-authoring/external-validation.ts
moda-interact-commerce/src/commerce/tool-authoring/contracts.ts          # only if a reusable observation type belongs here
moda-interact-commerce/src/studio/tools/external-validation-server-actions.ts

moda-interact-commerce/tests/external-http-executor.test.ts
moda-interact-commerce/tests/external-tool-authoring-server-actions.test.ts
moda-interact-commerce/tests/external-tool-authoring-validation.test.ts
moda-interact-commerce/tests/external-wiring.test.ts                      # only if integration wiring changes
```

A small dedicated Commerce-local observation module is permitted when it keeps `external-http/index.ts` coherent. Do not create a second generic HTTP stack.

## Out of Scope

- Visual inference or generation.
- Response-tab `Automatic` UI.
- Test-tab UI.
- Response processing (`DIRECT`, `VISUAL`, `JAVASCRIPT`).
- `resultSchema` validation.
- Prompt/model/agent execution.
- Persisting or satisfying `LIVE_TEST_REQUIRED`.
- Tool/ToolRevision writes.
- Connection or credential writes.
- Database schema/Prisma migrations.
- Shared package changes/publication.
- Gateway/Render changes.
- Enabling production JavaScript External HTTP execution.
- Following redirects.
- POST/PUT/PATCH/DELETE support.

## Requirements

### R1 — exact authoring observation input

Expose one server-side authoring operation equivalent to:

```ts
type ExternalHttpAuthoringObservationInput = {
  connectionRevisionId: string;
  request: unknown;
  responseFormat: unknown;
  inputSchema: unknown;
  arguments: unknown;
  shopId: string | null;
};
```

The browser MUST NOT supply:

```text
origin
resolved IP address
credential material
authentication header
absolute destination URL
arbitrary HTTP method
```

The server resolves those values from the selected immutable Connection revision and current authoring definition.

### R2 — resolve the exact current Request descriptor

Before any network call, use the accepted COMMERCE-041/047 Request construction boundary rather than reimplementing Request mapping.

Equivalent flow:

```text
inputSchema + sample Tool arguments + current request
        |
        v
previewExternalRequest(..., canonical requestProcessor)
        |
        v
ExternalRequestDescriptor
```

This must support both:

```text
DECLARATIVE
JAVASCRIPT
```

For JavaScript, QuickJS receives only the COMMERCE-040 declared/resolved Request bindings. Do not send the complete Tool input object to Request code.

Invalid arguments, mappings, JavaScript, descriptor paths, query values or headers fail before credential resolution/network I/O.

### R3 — preserve the production JavaScript execution gate

The new authoring observation capability may execute a safe descriptor produced from JavaScript authoring.

It MUST NOT change the existing production executor rule that production JavaScript External HTTP execution remains disabled.

A compliant design may extract/reuse a lower-level **descriptor-based provider observation** primitive from the existing executor, provided:

```text
production executor
  still reaches that primitive only after its existing production-compatible Request gate

authoring observation
  reaches the primitive after previewExternalRequest(...) has produced a safe descriptor
```

Do not refactor production execution in a way that silently enables JavaScript Requests in production.

### R4 — selected-shop and Connection scope

The action is platform-staff authoring and requires:

```text
requireStudioPlatformRole("ADMIN")
```

Connection scope must be enforced server-side:

```text
PLATFORM revision
  -> credential scope is null

PER_SHOP revision
  -> a non-null selected shop is required
  -> the supplied shop identifier must be revalidated through the existing Studio shop-execution/inspection authorization boundary before credential resolution
```

Do not trust a browser-supplied shop ID merely because it came from the Studio URL.

If no valid shop is available for a PER_SHOP Connection, no provider request occurs.

### R5 — one shared secure provider-observation primitive

Reuse/refactor the accepted External HTTP security implementation. Do not create parallel DNS/TLS/body-limit rules for Studio.

The descriptor-based provider call must preserve at least:

```text
HTTPS only
origin has no explicit port
origin hostname is not a literal IP address
relative Request path cannot change origin
scalar bounded query values only
forbidden/reserved request metadata remains forbidden
DNS must resolve to at least one address
all resolved addresses must be global/public
connect to the validated resolved address
TLS SNI/servername remains the original hostname
certificate verification remains enabled
GET only
redirects are not followed
maximum provider stage deadline <= 5 seconds
maximum decompressed response body = existing 256 KiB bound
supported content encodings remain bounded to the existing implementation
strict UTF-8 decoding
NUL-containing bodies are rejected
response body must satisfy the current authored `responseFormat`
```

If implementation extraction changes constants/helpers, there must remain **one source of truth** for these rules.

### R6 — credential secrecy

Credentials are resolved only on the server using the existing credential service.

Credential material MUST NOT be:

```text
returned to the browser
included in the safe Request descriptor
stored in React state
written to task/audit metadata
logged
included in errors
included in test snapshots
```

The observation may report only safe authentication metadata equivalent to:

```text
NONE
CONFIGURED
```

Never return the resolved authorization/API-key header name+value pair from this boundary.

### R7 — exact observation output

Return a bounded authoring result equivalent to:

```ts
type ExternalHttpAuthoringObservation =
  | {
      kind: "response";
      request: ExternalRequestDescriptor;
      origin: string;
      authentication: "NONE" | "CONFIGURED";
      response: TransformResponse;
    }
  | {
      kind: "failure";
      code:
        | "CONNECTION_UNAVAILABLE"
        | "SHOP_REQUIRED"
        | "PROVIDER_UNAVAILABLE"
        | "DEADLINE"
        | "INVALID_RESPONSE";
      retryable: boolean;
    };
```

Equivalent naming is allowed, but consumers must be able to distinguish:

```text
a real provider response
vs
no provider response because observation failed
```

`TransformResponse` remains the bounded canonical response shape already used by Commerce:

```text
status
contentType
bodyText
json
```

Do not add response headers to the browser contract. Provider response headers may contain cookies/tokens and are not needed by Automatic/Test in this architecture.

### R8 — non-2xx responses are observations, not transport exceptions

If the provider successfully returns an HTTP response and the bounded body can be decoded under the authored `responseFormat`, return:

```text
kind: response
```

for HTTP 2xx, 4xx, 429 and 5xx alike.

The HTTP status is part of the observation. Automatic generation may later require 2xx JSON, while Test must be able to show the actual provider status.

Network/TLS/DNS/deadline/decode failures remain `kind: failure`.

This authoring behavior MUST NOT change the production executor's existing 429/non-2xx Tool-result semantics.

### R9 — no durable mutation and no live-test receipt

The operation is read/execute-only.

It MUST NOT write:

```text
CommerceTool
CommerceToolRevision
CommerceAuditEvent
publication receipts
LIVE_TEST_REQUIRED evidence
Connection revisions
credentials
```

A successful authoring observation does **not** satisfy the publication `LIVE_TEST_REQUIRED` gate because it is based on a mutable unsaved authoring candidate rather than the architecture's future exact-saved-revision live-test receipt.

### R10 — action/error presentation contract

Wrap the capability in the existing Tool-authoring Server Action result convention.

Use action-level errors only for:

```text
FORBIDDEN
INVALID_INPUT
NOT_FOUND
DATABASE_UNAVAILABLE
INTERNAL_ERROR
```

Expected provider/connection/deadline outcomes belong in the bounded observation `value` described in R7, not fabricated field-validation issues.

Do not expose raw thrown/server/provider messages.

### R11 — sensitive-data logging

If operational logging is added, use the shared logger and log only bounded metadata such as:

```text
connectionRevisionId
scope class
outcome code
HTTP status class
elapsed duration
```

Do not log:

```text
Tool arguments
request query values
request header values
provider body/json
credential material
shop customer data
```

## Work Items

- [ ] Define one bounded Commerce-local External HTTP authoring observation contract.
- [ ] Extract/reuse one descriptor-based secure provider-observation primitive from the existing External HTTP executor without changing production JavaScript gating.
- [ ] Reuse `previewExternalRequest(...)` with the canonical Request processor for Declarative and JavaScript authoring.
- [ ] Enforce ADMIN and server-revalidated selected-shop scope.
- [ ] Resolve Connection revision and credentials server-side only.
- [ ] Preserve existing DNS/global-IP/TLS/deadline/body/decode protections.
- [ ] Return credential-redacted Request metadata plus bounded `TransformResponse`.
- [ ] Return non-2xx HTTP responses as observations while leaving production Tool semantics unchanged.
- [ ] Add the non-mutating Server Action/integration wiring.
- [ ] Add focused security/request/transport/authorization/no-write regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-041
  exact Request validation/preview boundary

ARCH-021-COMMERCE-047
  bounded JavaScript Request compiler diagnostics/runtime path

existing Commerce Connection revision + credential service
existing ExternalRequestDescriptor
existing TransformResponse
existing External HTTP DNS/TLS/transport security implementation
```

Produces:

```text
one Commerce-local live authoring observation boundary
```

No cross-repository runtime contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-041
- ARCH-021-COMMERCE-047

## Enables

- ARCH-021-COMMERCE-053
- ARCH-021-COMMERCE-054

## Acceptance Criteria

- [ ] Declarative Request authoring can obtain a real bounded provider observation.
- [ ] JavaScript Request authoring can obtain a real bounded provider observation through `previewExternalRequest(...)` without enabling production JavaScript execution.
- [ ] Tool arguments are validated against the current input schema before provider I/O.
- [ ] Invalid Request construction performs zero credential/DNS/transport work.
- [ ] PLATFORM and PER_SHOP credential scopes are enforced server-side.
- [ ] PER_SHOP live observation requires a revalidated selected shop.
- [ ] Provider credentials never leave the server and are never logged.
- [ ] HTTPS/global-IP/address-pinning/TLS-hostname/no-redirect protections match the production security boundary.
- [ ] Provider body is bounded by the existing 256 KiB decompressed limit.
- [ ] Provider execution is bounded by the existing <=5 second stage/deadline behavior.
- [ ] 4xx/429/5xx provider responses can be returned as bounded observations when decode succeeds.
- [ ] Network/DNS/TLS/deadline/decode failure is represented without raw internal/provider error text.
- [ ] The browser receives no provider response headers.
- [ ] The operation performs no Tool/Revision/Connection/Credential/receipt writes.
- [ ] A successful observation does not satisfy `LIVE_TEST_REQUIRED`.
- [ ] Existing production External HTTP executor behavior remains unchanged, including its JavaScript Request gate and non-2xx Tool-result mapping.

## Mandatory Regression Scenarios

Add focused named tests proving at least:

```text
1. Declarative + valid arguments -> exact preview descriptor -> one provider GET.
2. JavaScript + declared bindings -> exact preview descriptor -> one provider GET.
3. invalid input-schema arguments -> INVALID_INPUT and zero credential/DNS/transport calls.
4. JavaScript syntax/entrypoint failure -> no provider call and bounded authoring failure.
5. PLATFORM revision resolves credential with null shop scope.
6. PER_SHOP revision without shop -> SHOP_REQUIRED and no provider call.
7. PER_SHOP revision with unauthorized/missing shop -> no provider call.
8. credential material is applied to transport but absent from returned observation.
9. HTTPS literal-IP origin is rejected.
10. HTTP origin is rejected.
11. DNS resolving private/loopback/link-local/non-global address is rejected.
12. mixed global + non-global DNS answers are rejected.
13. validated address is pinned while TLS servername remains original hostname.
14. redirects are not followed.
15. oversized decompressed body fails closed.
16. unsupported content encoding fails closed.
17. invalid UTF-8/NUL body fails closed.
18. authored response media type mismatch fails closed.
19. provider 404 with valid bounded JSON returns kind=response with status 404.
20. provider 429 with valid bounded JSON returns kind=response with status 429.
21. provider 503 with valid bounded JSON returns kind=response with status 503.
22. deadline/abort terminates transport/body consumption and returns bounded failure.
23. response headers including Set-Cookie are not present in the browser contract.
24. no Tool/Revision/receipt mutation occurs on success or failure.
25. production JavaScript External HTTP execution remains rejected exactly as before.
```

## Validation

Run the repository-declared commands that cover this task, at minimum:

- [ ] `npm run test:arch020-external-http`
- [ ] `npm run test:arch021-code-request`
- [ ] `npm run test:arch021-external-tool-authoring-validation`
- [ ] `npm run test:arch020-external-wiring` when integration wiring changes
- [ ] focused new observation tests
- [ ] targeted ESLint on changed files
- [ ] `git diff --check`
- [ ] changed-file TypeScript diagnostics contain no task-owned error

Do not treat unrelated repository baseline diagnostics as task failures when they match the documented development baseline; record the baseline ID/evidence in the Completion Report.

## Stop Condition

After the live authoring observation boundary, security regressions, required validation and Completion Report are complete, set the task to `review`, clear the execution claim according to the normal workflow, return control to `moda_architect` and STOP. Do not begin COMMERCE-053 or COMMERCE-054.

## Implementation Notes

Prefer extracting one descriptor-based provider-observation primitive that can be reused by Studio without changing the production executor's current Request compatibility gate. Do not duplicate the security-sensitive DNS/TLS/body-reading code merely to move quickly.

The exact internal file/function name is repository-local. The architectural invariants in Requirements R1-R11 are not optional.

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

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
