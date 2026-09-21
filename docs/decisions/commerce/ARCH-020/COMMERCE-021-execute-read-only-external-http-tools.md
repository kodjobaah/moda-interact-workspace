---
id: ARCH-020-COMMERCE-021
architecture_id: ARCH-020
title: Execute read-only external HTTP tools
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-014
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-GATEWAY-003
  - ARCH-020-COMMERCE-030
created: 2026-09-21
updated: 2026-09-22
---

# Execute read-only external HTTP tools

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/external-http/** plus explicit014 dispatcher/renderer extension points. Implement C21 transport with injected028 resolver and025/026 processing ports. No connection persistence, UI or production factory wiring.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/external-http/** plus explicit014 dispatcher/renderer extension points. Implement C21 transport with injected028 resolver and025/026 processing ports. No connection persistence, UI or production factory wiring.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [x] Implement createExternalHttpExecutionPort and explicit EXTERNAL_HTTP branch, runtime wrapper/schema validation, rendering and result/error mapping. Existing query/policy dispatch remains exhaustive.
- [x] Implement fixed-origin DNS/socket pinning, TLS hostname verification, target classification, no redirects/proxies/cookies, encoded bounded query and abort/deadline/decompression limits.
- [x] Decode declared JSON/TEXT without assuming structured content; apply injected visual/code dispatcher before final schema validation/rendering; on failure return bounded error, never raw upstream data. Exclude provider responses from logs.
- [x] Consume shared per-call budgets with no hidden retries; current connection authorization every call. Document transport fixture evidence and exact public factory in docs/external-http-executor.md.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-014

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-GATEWAY-003
- ARCH-020-COMMERCE-030

## Acceptance Criteria

- [x] HT01: supported GET is proven through the production DNS-aware HTTPS transport path into a controlled HTTPS server, with injected auth, exact encoded query and filtered valid response reaching the renderer.
- [x] HT02: the recorded socket address matches approved DNS resolution; private, mapped, mixed-resolution and redirect attempts fail before unsafe dispatch; the transport performs no second hostname lookup.
- [x] HT03: UTF-8 JSON and TEXT decoding, one-request budget, streamed/decompressed byte bound, absolute DNS/connect/body deadlines, caller abort, MIME/schema/status mapping and raw JSON safety validation are covered by focused fixtures with no raw body fallback.
- [x] HT04: synthetic 404/429/5xx and malformed/unsafe data produce the required bounded errors; existing Shopify/policy dispatch remains passing; denial cases have adjacent permitted cases through the same entry point.

## Validation

Provide `test:arch020-external-http` with HT01–HT04. HT01 must be implemented first and retained as the positive baseline. Tests instantiate createExternalHttpExecutionPort and the actual production DNS/transport implementation. A controlled HTTPS endpoint and injected DNS mapping may replace external internet, never bypass certificate/hostname verification or target validation in production code. Use recording socket/TLS adapters at OS boundary only where CI cannot bind a public address; demonstrate production connector uses the approved address.

Publish a fixtures table naming request, expected status/data, connected address and provider-call count. Every review correction becomes a committed regression plus adjacent allowed case. Typecheck/build plus old suites cannot substitute for these scenarios. Live public provider calls are unnecessary.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Ready for Review (Attempt 2).

### Files Changed

- `src/commerce/external-http/index.ts`
- `src/commerce/execution/executor.ts`
- `src/commerce/execution/index.ts`
- `tests/external-http-executor.test.ts`
- `docs/external-http-executor.md`
- `package.json`
- `package-lock.json`

### Attempt-2 Work Completed

- A1-R1: added exact production dependency `ip-address@10.7.2`; replaced local CIDR tables with `Address4.isGlobal()` / `Address6.isGlobal()`; added and exported `createNodeDnsResolver`, using Node DNS lookup with `all: true` and `verbatim: true`, preserving deduplicated first-seen addresses; retained resolver output as the sole source of the pinned socket address.
- A1-R2: added independent five-second-bounded DNS, connect/headers and body/decompression abort scopes; added active request and response/decompression cleanup on abort, limit and error; reserved the provider budget exactly once immediately before dispatch and mapped reservation failure to non-retryable `DEADLINE`.
- A1-R3: added pre-processor JSON traversal validation with depth 20, finite-number, ordinary-object and unsafe-key checks; unsafe/deep input is rejected before `resultPath` or either processor, while TEXT remains unparsed.
- A1-R4: made `EXTERNAL_HTTP` an explicit dispatcher branch with compile-time exhaustive fallback; Shopify and policy branches remain unchanged.
- Updated the transport fixture table with production DNS/classifier, connected address, provider calls, JSON/TEXT, private/mapped/mixed DNS, redirects, compression, decompressed limits, stage deadlines, in-flight abort and 404/429/5xx evidence.

### Attempt-2 Validation Results

- `npm run test:arch020-external-http`: passed, 1 file and 12/12 tests (HT01--HT04 focused scenarios, including correction regressions).
- `npm exec vitest run tests/definition-execution.test.ts tests/external-http-executor.test.ts`: passed, 2 files and 24/24 tests.
- `npm run lint`: passed with 0 errors and 2 existing warnings outside task-owned files: `scripts/code-runtime-manifest.mjs:7` and `src/commerce/code-response/runtime/kernel.ts:91`.
- `npm run typecheck`: blocked by the unchanged unrelated errors at `src/commerce/integration/backend/executors.ts:17` (`operation` and `operationVersion` are not present on the `EXTERNAL_HTTP` union member).
- `npm run build`: compilation succeeded, then the same unchanged type-check errors at `src/commerce/integration/backend/executors.ts:17` blocked completion.
- `git diff --check`: passed.

### Attempt-2 Deviations and Unresolved Issues

- The accepted Shared 0.14.2 result union does not include `CANCELLED`; processor or external-operation cancellation remains mapped to non-retryable `DEADLINE`, while runner-level cancellation remains `CANCELLED`. Shared was not widened or published.
- Repository-wide typecheck/build remain blocked only by the unrelated integration backend discriminated-union errors recorded above. No unrelated files were changed.

### Attempt-2 Git / VCS

- Mirrored branch: `task/ARCH-020-COMMERCE-021`.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-021`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-021`.
- Attempt-1 history below is preserved verbatim; this Attempt-2 report supersedes its stale validation claims.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.

### Attempt 1 — Review Status

Changes Requested.

### Attempt 1 — Review Notes

Reviewed implementation `b19f9d7` and parent report `5abdd61a` against the exact
submitted snapshot, C21 sections 2, 5 and 9.3, and the accepted
`@modainteract/moda-interact-shared@0.14.2` contract. This review is about the
runtime behaviour required by HT01–HT04, not exhaustive coverage.

Preserve the following Attempt-1 work unless a correction below explicitly requires a
small change to it:

```text
- exact Shared 0.14.2 dependency;
- fixed administrator-selected HTTPS origin/path and encoded lexically sorted query;
- injected current connection resolver and no credential/configuration persistence;
- one provider-budget reservation and no transport retry/pagination loop;
- socket connection to the validated address while retaining original Host/TLS SNI;
- TLS certificate hostname verification;
- no redirect following, proxy environment fallback or cookie jar;
- bounded JSON/TEXT decode and injected visual/code processing ports;
- final resultSchema validation and EXTERNAL_HTTP result wrapper;
- 401/403/404/redirect -> nonretryable UNAVAILABLE, 429 -> retryable THROTTLED,
  5xx/connection failure -> retryable UNAVAILABLE;
- existing Shopify/policy execution paths and rendering behaviour.
```

#### Architect resolution — cancellation at the CommerceToolResult boundary

**Architecture/documentation reconciliation; do not widen Shared in this task.**

Attempt 1 correctly identified a genuine contract contradiction. The accepted
Shared 0.14.2 `CommerceToolResultSchema` does not contain `CANCELLED`, while the
processor ports and runner-level result do. For this architecture revision the
boundary is resolved as follows:

```text
Visual/Code processor CANCELLED
or an aborted external HTTP operation
        -> CommerceToolResult { code: 'DEADLINE', retryable: false }

RunCommerceTurnResult cancellation
        -> remains runner-level CANCELLED
```

`ARCH-020-COMMERCE-021` MUST NOT invent a `CANCELLED` CommerceToolResult, locally
widen the Shared union or publish a Shared package. The parent C21 architecture is
reconciled by this architect patch. The correction items below therefore retain the
nonretryable `DEADLINE` mapping at this tool-result boundary.

#### A1-R1 — provide the production DNS resolver and replace the hand-maintained IP policy

**Source/dependency/test/documentation change required.**

Files permitted/expected:

```text
moda-interact-commerce/package.json
moda-interact-commerce/package-lock.json
moda-interact-commerce/src/commerce/external-http/**
moda-interact-commerce/src/commerce/execution/index.ts
moda-interact-commerce/tests/external-http-executor.test.ts
moda-interact-commerce/docs/external-http-executor.md
```

Current defects:

1. There is no production DNS resolver implementation/export. The public port accepts
   an injected `DnsResolver`, but the only resolver in the submitted repository is a
   test fixture. C21 assigns the actual DNS/TLS transport producer to COMMERCE-021;
   COMMERCE-024 must not invent the missing DNS implementation later.
2. `isGlobalAddress()` maintains a local list of IPv4/IPv6 CIDR exceptions. C21
   explicitly requires a maintained address classifier backed by official
   special-address behaviour rather than a hand-maintained prefix table.

Required dependency:

```json
"ip-address": "10.7.2"
```

Add it as an exact direct production dependency and reconcile `package-lock.json`.
Do not rely on the currently transitive copy. No version range.

Required address policy:

```text
IPv4 -> Address4.isGlobal()
IPv6 -> Address6.isGlobal()
invalid input -> false
```

Use the package's globally-reachable predicate as the trust decision. Do not retain
`IPV4_NON_GLOBAL_RANGES`, `IPV6_NON_GLOBAL_RANGES` or another locally maintained
special-purpose CIDR table. IPv4-mapped/NAT64 IPv6 must be classified according to
the classifier's embedded-address/global semantics, not accepted merely because the
outer value is IPv6.

Required production resolver export:

```ts
createNodeDnsResolver(...): DnsResolver
```

The default implementation MUST use Node DNS lookup with:

```text
all: true
verbatim: true
```

and return every resolved address for the hostname (deduplicated without changing the
first-seen order). It must never choose/return an address that was not produced by the
DNS lookup. A narrowly injected lookup function is allowed for tests; the production
default is the Node implementation. `createExternalHttpExecutionPort` continues to
accept the resolver as an injected dependency so COMMERCE-024 only composes producers.

Export the production DNS factory from the existing external-HTTP/execution public
surface alongside `createNodeHttpsTransport`.

Required focused proof through the real external HTTP entry point:

```text
DENY with zero transport calls:
  0.0.0.0
  10.0.0.1
  100.64.0.1
  127.0.0.1
  169.254.169.254
  192.0.2.1
  198.18.0.1
  203.0.113.1
  ::1
  fc00::1
  fe80::1
  2001:db8::1
  ::ffff:127.0.0.1
  64:ff9b::7f00:1
  fec0::1
  4000::1
  [93.184.216.34, 10.0.0.1]  // mixed resolution: reject the hostname entirely

ALLOW through the same entry point:
  192.0.0.9
  192.0.0.10
  8.8.8.8
  2001:4860:4860::8888
```

Also prove the production DNS factory requests all/verbatim addresses and that the
address passed to the production TLS transport is exactly an address returned by that
resolver. No second hostname lookup is allowed in the transport.

#### A1-R2 — enforce an absolute bounded DNS/connect/body stage deadline and prompt abort cleanup

**Source/test change required.**

Files:

```text
moda-interact-commerce/src/commerce/external-http/**
moda-interact-commerce/tests/external-http-executor.test.ts
```

Attempt 1 passes `timeoutMs` to `https.request`, but Node's request/socket timeout is
not an absolute DNS/connect/body wall-clock bound. A peer can keep a body alive by
sending data before each inactivity timeout. The injected DNS resolver is likewise
currently awaited without the C21 five-second stage bound.

For each of these stages independently:

```text
DNS resolution
connect + response headers
response body + decompression
```

calculate at stage start:

```ts
stageMs = Math.min(5_000, context.deadlineAt - now())
```

If `stageMs <= 0`, return nonretryable `DEADLINE` without entering the stage.

Each stage MUST use a derived abort scope which:

```text
- aborts when the parent context.signal aborts;
- aborts when stageMs elapses;
- clears its timer and parent listener in finally;
- cannot leave a later stage using an already-expired timer;
- never creates a second provider request.
```

The Node transport must destroy the request/socket when its supplied signal aborts.
The body/decompression reader must also be actively interruptible while waiting for
the *next* chunk; checking `signal.aborted` only after a chunk arrives is insufficient.
On abort/limit/error, stop/destroy the response/decompression stream so a late provider
body cannot continue consuming process resources.

Provider-budget reservation rules:

```text
- reserveProviderRequest() exactly once, immediately before transport dispatch;
- if reservation throws, make zero transport calls and return
  {code:'DEADLINE', retryable:false};
- no hidden retry in COMMERCE-021.
```

Keep the transport's own socket timeout as defence in depth, but it does not substitute
for the absolute stage timer.

Required focused proof using the actual production external HTTP path:

```text
1. resolver never settles -> stage expiry -> DEADLINE false; transport calls = 0
2. transport/connect never settles -> stage expiry -> DEADLINE false; request signal observed aborted
3. body emits one chunk then stalls -> stage expiry/abort terminates the body wait -> DEADLINE false
4. caller aborts an in-flight body -> prompt DEADLINE false and body cleanup
5. valid gzip body under 256 KiB decoded -> succeeds
6. compressed body whose decoded bytes exceed 256 KiB -> UNAVAILABLE false and stream is stopped
7. budget reservation throws -> DEADLINE false, transport calls = 0
```

Use fake timers or another deterministic clock/timer seam for the five-second cases;
do not make the focused suite sleep for real five-second intervals.

#### A1-R3 — reject unsafe/deep parsed JSON before resultPath or processor execution

**Source/test change required.**

Files:

```text
moda-interact-commerce/src/commerce/external-http/**
moda-interact-commerce/tests/external-http-executor.test.ts
```

C21 requires JSON-mode input to reject unsafe keys and nesting beyond depth 20.
`TransformResponseSchema`/`z.json()` alone does not establish that raw-provider input
policy. Attempt 1 currently calls `JSON.parse()` and sends the resulting value to
`resultPath`/the response processor without the required traversal.

Immediately after JSON parsing and before `selected(...)`, `responseProcessor` or
`codeProcessor`, validate the entire parsed JSON tree with these rules:

```text
root depth = 1
if depth > 20 -> reject
allowed values: null, string, finite number, boolean, arrays, ordinary JSON objects
for every object key, reject exactly:
  __proto__
  prototype
  constructor
visit every array element and every object value
no getters/method calls/coercion/stringification during validation
```

A rejection returns nonretryable `UNAVAILABLE`; neither processor may be called.
TEXT mode remains `json: null` and is not parsed as JSON.

Required focused proof:

```text
- ordinary nested JSON at/below depth 20 -> permitted
- depth 21 -> UNAVAILABLE, processor calls = 0
- __proto__ at root -> UNAVAILABLE, processor calls = 0
- constructor nested inside an array/object -> UNAVAILABLE, processor calls = 0
- adjacent safe key such as constructorName -> permitted
```

Do not solve this by serializing/reparsing the provider value or by relying on the
processed-output 48 KiB validator; this is raw input validation before processing.

#### A1-R4 — make EXTERNAL_HTTP an explicit exhaustive dispatcher branch

**Source change required; existing focused dispatcher suite is sufficient proof when it
continues to pass.**

File:

```text
moda-interact-commerce/src/commerce/execution/executor.ts
```

Attempt 1 currently dispatches:

```text
SHOPIFY_STOREFRONT_QUERY
else if POLICY_OPERATION
else -> external HTTP
```

The final `else` is not the explicit extension required by C21 and would silently route
a future execution kind to the external HTTP port.

Required dispatch shape:

```text
if SHOPIFY_STOREFRONT_QUERY -> query path
else if POLICY_OPERATION -> policy path
else if EXTERNAL_HTTP -> external HTTP path
else -> compile-time exhaustive never/unreachable handling
```

Do not use a generic final branch to mean EXTERNAL_HTTP. Preserve current result
validation/rendering and do not modify Shopify or policy semantics.

Required proof:

```text
npm exec vitest run tests/definition-execution.test.ts tests/external-http-executor.test.ts
```

The existing Shopify/policy cases and the positive EXTERNAL_HTTP case must all remain
passing.

### Attempt 2 validation contract

The purpose is to prove the corrected runtime behaviour, not to broaden the suite.
Run exactly the task-focused checks plus normal task-owned static validation:

```text
npm run test:arch020-external-http
npm exec vitest run tests/definition-execution.test.ts tests/external-http-executor.test.ts
npm run lint
npm run typecheck
npm run build
git diff --check
```

If repository-wide `typecheck` still fails only on the already-recorded unrelated
Prisma integration diagnostics, record the exact unchanged diagnostics and show that
all Attempt-2 touched files have no TypeScript diagnostics. Do not edit unrelated
`src/commerce/integration/backend*` files to clean the baseline.

Update `docs/external-http-executor.md` so the fixture/evidence table records at least:

```text
- production DNS factory/classifier path;
- connected address;
- provider-call count;
- JSON positive request;
- TEXT positive request;
- private/mapped/mixed DNS denial;
- redirect denial;
- valid compressed response;
- decompressed-byte rejection;
- DNS/connect/body deadline;
- in-flight abort;
- 404/429/5xx mappings.
```

### Attempt 2 preservation / forbidden scope

MUST NOT:

```text
- implement COMMERCE-028 credentials;
- implement COMMERCE-025/026 processors;
- implement COMMERCE-024 production factory wiring;
- change database schema;
- widen/publish Shared contracts;
- add POST/PUT/PATCH/DELETE, bodies, OAuth, cookies, redirects or provider pagination;
- add automatic external-result caching;
- expose URL query values, credentials or provider body data in errors/logs;
- begin COMMERCE-030, COMMERCE-024, GATEWAY-003, COMMERCE-012 or system tests.
```

### Attempt 2 stop condition

After A1-R1 through A1-R4 are implemented and the focused validation above is run:

```text
1. update Work Items / Acceptance Criteria / Validation truthfully;
2. replace the current Completion Report with Attempt-2 current evidence while
   preserving Attempt-1 history as historical review text;
3. set status: review;
4. set executor: null;
5. set claimed_at: null;
6. commit and push the Commerce implementation branch;
7. commit and push the parent task-report branch;
8. STOP and return to moda_architect.
```

Do not claim or start an enabled/downstream task.
