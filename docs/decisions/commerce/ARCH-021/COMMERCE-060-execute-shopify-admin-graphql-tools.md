---
id: ARCH-021-COMMERCE-060
architecture_id: ARCH-021
title: Execute Shopify Admin GraphQL Tool definitions
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 72
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-018
enables:
  - ARCH-021-COMMERCE-070
  - ARCH-021-COMMERCE-069
created: 2026-09-27
updated: 2026-09-27
---

# Execute Shopify Admin GraphQL Tool definitions

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add the production Commerce execution path for the already-authored `SHOPIFY_ADMIN_GRAPHQL` Tool kind so an immutable Tool revision can execute its validated Shopify Admin `2026-07` read query against the selected merchant using the server-side offline Shopify installation token, return a bounded normalized Commerce Tool result, and preserve the existing response-template/rendering boundary.

## Context

The current baseline can author and validate `SHOPIFY_ADMIN_GRAPHQL` definitions through the pinned Admin compiler, but `DefinitionExecutor` executes only Storefront queries, policy operations and supported External HTTP definitions. Admin definitions therefore validate but are not executable.

Production Commerce already demonstrates the approved Shopify Admin credential boundary in policy adapters: the server resolves the merchant's offline session token and sends it only in the `X-Shopify-Access-Token` header to the pinned Admin endpoint. This task makes the Tool execution path use that same ownership/security model.

This task intentionally adds Admin execution **without** removing Storefront. Storefront removal is a later independent cleanup once Admin execution and Admin Explore authoring are both in place.

## Scope

Expected implementation areas include:

```text
src/commerce/execution/
src/commerce/query/
src/commerce/integration/backend/
src/commerce/integration/backend.ts
lib/discovery/admin-compiler.ts                # reuse only; no authoring redesign

tests/query-execution.test.ts
tests/arch021-commerce-tool-contract.test.ts
tests/commerce-lifecycle.test.ts               # only where executor availability is asserted
```

Exact filenames may follow repository conventions.

## Out of Scope

- Removing `SHOPIFY_STOREFRONT_QUERY`.
- Rebuilding Explore Shopify.
- Changing Tool creation tabs or navigation.
- Deriving `resultSchema` automatically from GraphQL; COMMERCE-062 owns that later refinement.
- Persisting credentials in Tool definitions, browser state, logs or telemetry.
- Shopify Admin mutations.
- Live-Test tab UI.
- Database schema/migration changes.
- Shared-package contract changes.

## Requirements

### R1 — execute only the accepted Admin query contract

The execution path accepts only canonical `SHOPIFY_ADMIN_GRAPHQL` definitions using the pinned Admin `2026-07` schema identity and existing compiler restrictions.

Before provider execution, reuse the accepted Admin compiler/definition validation so runtime does not create a second interpretation of:

```text
apiVersion
schemaHash
document
operationName
variables
resultPath
resultSchema
```

Fragments/directives/mutations or another schema version remain rejected according to the existing compiler contract.

### R2 — resolve merchant credentials server-side

Resolve the selected merchant's offline Shopify session token on the server using the existing Commerce/Shopify persistence boundary.

The Tool definition and mapped Tool arguments MUST NOT contain or receive:

```text
access token
authorization header
shop domain supplied by the model
provider URL supplied by the model
```

Use the authorized execution context's merchant/shop domain.

### R3 — use the pinned Admin endpoint safely

Issue a bounded POST to:

```text
https://<authorized-shop>/admin/api/2026-07/graphql.json
```

with the canonical operation name, document and mapped variables.

Preserve existing execution protections applicable to Shopify provider calls, including deadline/abort handling, redirect rejection, bounded response consumption, provider throttling mapping and safe failure translation.

### R4 — normalize the successful result

After a successful GraphQL envelope:

1. reject provider GraphQL errors;
2. select the configured `resultPath`;
3. reject a missing/null selected root using the existing Tool failure semantics;
4. validate the selected value against the persisted `resultSchema` for this task's baseline behavior;
5. produce bounded data equivalent to:

```text
{
  source: "SHOPIFY_ADMIN",
  apiVersion: "2026-07",
  schemaHash: <pinned hash>,
  observedAt: <ISO timestamp>,
  values: <validated selected result>
}
```

Do not render provider data into instructions. `renderDefinitionResult` remains the response-template boundary after execution.

### R5 — preserve failure semantics

Map failures into existing Commerce Tool errors without exposing provider secrets or raw internal exceptions.

At minimum cover:

```text
INVALID_INPUT
NOT_FOUND
UNAVAILABLE
THROTTLED
DEADLINE
INCOMPATIBLE_VERSION
```

The precise existing code mapping remains authoritative.

### R6 — availability reflects real Admin executability

The executable-registry/availability boundary must recognize a valid `SHOPIFY_ADMIN_GRAPHQL` definition when the Admin executor is installed.

Do not mark Storefront unavailable in this task.

### R7 — no credential leakage

Tests must prove access tokens do not appear in:

```text
CommerceToolResult
renderedText
telemetry attributes
ordinary failure messages
Tool definition snapshots
```

## Work Items

- [x] Add a dedicated Admin GraphQL execution port without changing the tokenless Storefront port.
- [x] Implement the pinned Admin provider request with server-side offline-session token resolution.
- [x] Reuse the accepted Admin compiler and mapped-argument validation before session/provider work.
- [x] Select `resultPath` and validate selected values against persisted `resultSchema`.
- [x] Normalize successful data as bounded `SHOPIFY_ADMIN` facts.
- [x] Wire `DefinitionExecutor`, production backend composition and executable-registry availability.
- [x] Add success, throttle, GraphQL-error, deadline, invalid-result and credential-safety tests.

## Interfaces / Contracts

Consumes:

```text
SHOPIFY_ADMIN_GRAPHQL execution contract from COMMERCE-018
CommerceToolResult / DefinitionExecutor contracts
server-owned offline Shopify session token
```

Produces no new cross-repository contract.

The normalized result's `data.values` becomes the source later consumed by COMMERCE-062/063 and response-template rendering.

## Dependencies

- `ARCH-021-COMMERCE-018`

## Enables

- `ARCH-021-COMMERCE-070`
- `ARCH-021-COMMERCE-069`

## Acceptance Criteria

- [x] A valid Admin query definition executes against the authorized merchant context when the Admin executor is installed.
- [x] Runtime uses Shopify Admin `2026-07`, not Storefront.
- [x] Runtime uses the server-side offline token and never accepts one from Tool arguments.
- [x] Admin compiler rejection prevents session lookup and provider execution.
- [x] Mapped variables are the only model-supplied query inputs.
- [x] `resultPath` is selected deterministically.
- [x] The selected result must satisfy the persisted `resultSchema`.
- [x] Successful data uses source `SHOPIFY_ADMIN` and contains `values`.
- [x] Provider 429 maps to `THROTTLED`.
- [x] Aborted/deadline execution settles as `DEADLINE` and aborts the provider signal.
- [x] Credentials are absent from returned results, rendered text, telemetry attributes and definition snapshots.
- [x] Existing External HTTP and policy execution tests remain green.
- [x] Storefront support is unchanged by this task.

## Validation

- [x] Focused Admin query execution tests: `npx vitest run tests/admin-query-execution.test.ts` passed (10 tests).
- [x] DefinitionExecutor tests: included in the final focused compatibility run.
- [x] Executable-registry availability tests: included in the final focused compatibility run.
- [x] Targeted lint: ESLint passed for all changed source and test files.
- [x] Changed-file TypeScript diagnostics: no Pylance errors in changed files.
- [x] `git diff --check` passed before commit and after mainline synchronization.
- [x] Shopify Admin validator accepted the bounded Products query fixture against API `2026-07` (`read_products` scope).
- [x] Compatibility suite: `npx vitest run tests/admin-query-execution.test.ts tests/query-execution.test.ts tests/definition-execution.test.ts tests/backend-integration.test.ts tests/external-http-executor.test.ts --reporter=verbose` passed (60 tests).
- [x] Implementation commit `0902590` was merged with fetched `origin/main` and pushed to `origin/task/ARCH-021-COMMERCE-060`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-062 or COMMERCE-069.

## Implementation Notes

Prefer reusing the existing server-side Admin request pattern in `src/commerce/integration/backend.ts` rather than introducing a second credential-resolution mechanism.

Do not redesign Admin `resultSchema` semantics here. The current persisted schema remains authoritative until COMMERCE-062 introduces derived result-contract semantics.

## Completion Report

### Status

Attempt 2 correction complete; submitted for architect review.

### Files Changed

`moda-interact-commerce/src/commerce/query/admin.ts`; `moda-interact-commerce/src/commerce/execution/executor.ts`; `moda-interact-commerce/src/commerce/execution/index.ts`; `moda-interact-commerce/src/commerce/execution/ports.ts`; `moda-interact-commerce/src/commerce/execution/renderer.ts`; `moda-interact-commerce/src/commerce/integration/backend.ts`; `moda-interact-commerce/src/commerce/integration/backend/executors.ts`; `moda-interact-commerce/tests/admin-query-execution.test.ts`; `moda-interact-commerce/tests/backend-integration.test.ts`; `moda-interact-commerce/tests/definition-execution.test.ts`.

### Work Completed

Added bounded Admin GraphQL execution using only the authorized shop domain and a server-resolved offline session token. The runtime reuses the pinned Admin compiler, validates mapped GraphQL variables before provider work, posts only to the Admin `2026-07` endpoint, bounds and validates the provider response, applies `resultPath` and persisted `resultSchema`, and emits normalized `SHOPIFY_ADMIN` facts. Wired production transport/session lookup, executor dispatch and compiler-backed executable-registry availability. Admin result arrays now use the existing bounded search-results rendering cap. Storefront, policy and External HTTP paths remain supported.

### Validation Results

Passed focused Admin execution tests (10), DefinitionExecutor/backend/registry tests, Storefront query tests and External HTTP executor regressions (60 total). Shopify Admin schema validation accepted the bounded query fixture against `2026-07`. Targeted ESLint and changed-file Pylance diagnostics passed; `git diff --check` passed. Package-wide `npx tsc --noEmit` remains non-green due to unrelated existing diagnostics in generated-Prisma-dependent backend/publication code, Studio services and existing tests; no changed-file Pylance diagnostics were reported.

### Deviations

No scope deviation. Admin array rendering uses the already-existing Storefront `maxSearchResults` limit so Admin result-template rendering remains bounded.

### Assumptions

The existing Prisma `session` row keyed by the authorized shop domain with `isOnline: false` is the authoritative offline-token source, matching the existing production Admin policy integration.

### Unresolved Issues

The package-wide TypeScript command reports unrelated diagnostics as noted under Validation Results; changed files have no editor TypeScript diagnostics.

### Architectural Concerns

None.

### Attempt 2 Correction

Addressed the Changes Requested finding: Shopify Admin GraphQL HTTP 200 envelopes now map any bounded error entry with `extensions.code === "THROTTLED"` to the minimal Commerce `THROTTLED` error with `retryable: true`. Other GraphQL errors retain the existing safe `UNAVAILABLE` mapping. Added a regression containing a token, provider message, and request identifier in the provider error; the returned result contains none of those details.

### Attempt 2 Files Changed

`moda-interact-commerce/src/commerce/query/admin.ts`; `moda-interact-commerce/tests/admin-query-execution.test.ts`.

### Attempt 2 Validation

- Focused Admin execution suite passed (11 tests).
- Admin, Storefront query, DefinitionExecutor, backend integration, and External HTTP compatibility suite passed (61 tests across 5 files).
- Targeted ESLint passed for both changed files.
- Changed-file Pylance diagnostics reported no errors.
- `git diff --check` passed.

### Attempt 2 Status

Ready for architect review on the existing mirrored task branches. No additional scope changes were made.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 satisfies the Attempt 1 correction contract. The Admin execution port now recognizes Shopify Admin GraphQL throttling delivered in an HTTP 200 GraphQL envelope when any bounded error entry has `extensions.code === "THROTTLED"`, returning only the minimal Commerce `THROTTLED` result with `retryable: true`. Other GraphQL errors continue to use the existing safe `UNAVAILABLE` mapping.

The regression includes provider message text, a request identifier and access-token-like material and proves none are exposed in the returned Commerce result. The defensive HTTP 429 mapping remains intact. No unrelated execution behavior changed.

The broader C060 architecture remains conformant: the pinned Admin compiler runs before session/provider work; the authorized shop domain comes only from execution context; the offline Shopify token is resolved server-side; the provider endpoint is pinned to Admin `2026-07`; provider response consumption is bounded; selected results are checked against `resultPath` and persisted `resultSchema`; the response-template boundary remains unchanged; and Storefront, policy and External HTTP execution remain supported.

The submitted snapshot still carried an active executor/claim despite the review handoff. Acceptance normalizes `executor` and `claimed_at` to `null`.

### Reviewed Files

- `moda-interact-commerce/src/commerce/query/admin.ts`
- `moda-interact-commerce/tests/admin-query-execution.test.ts`
- C060 Completion Report and prior Architect Review
- Commerce ARCH-021 task index and parent architecture execution tables

### Validation Reviewed

- Attempt 2 focused Admin execution suite: 11 tests passed.
- Five-file Admin/Storefront/DefinitionExecutor/backend/External HTTP compatibility suite: 61 tests passed.
- Targeted ESLint: passed.
- Changed-file diagnostics: clean.
- `git diff --check`: passed.
- Attempt 1 Shopify Admin `2026-07` schema validation remained recorded as passed; no schema/query-shape change was introduced by Attempt 2.

### Architecture Conformance

Conforms. Provider throttling semantics now match the required Commerce error contract while preserving credential secrecy, tenant/shop authority, endpoint pinning, compiler reuse, bounded provider I/O, response validation, rendering and compatibility with existing execution paths.

### Follow-up

None for C060. Mark the task Complete. COMMERCE-069 and COMMERCE-070 remain Pending because each still has another dependency in addition to C060; acceptance of C060 alone does not make either task executable.
