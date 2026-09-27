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
status: in_progress
priority: 72
executor: copilot
claimed_at: 2026-09-27T14:56:22Z
attempt: 1
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

- [ ] Add or generalize the Shopify query execution port for Admin GraphQL without weakening authorization.
- [ ] Implement the pinned Admin provider request with offline-token resolution.
- [ ] Reuse the accepted Admin compiler before execution.
- [ ] Select `resultPath` and validate current persisted `resultSchema`.
- [ ] Normalize successful data as `SHOPIFY_ADMIN` facts.
- [ ] Wire `DefinitionExecutor` and executable-registry availability.
- [ ] Add success, throttle, GraphQL-error, deadline, invalid-result and credential-safety tests.

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

- [ ] A valid published/draft-executable Admin query can execute against an authorized merchant.
- [ ] Runtime uses Shopify Admin `2026-07`, not Storefront.
- [ ] Runtime uses the server-side offline token and never accepts one from Tool arguments.
- [ ] Admin compiler rejection prevents provider execution.
- [ ] Mapped variables are the only model-supplied query inputs.
- [ ] `resultPath` is selected deterministically.
- [ ] The selected result must satisfy the persisted `resultSchema`.
- [ ] Successful data uses source `SHOPIFY_ADMIN` and contains `values`.
- [ ] Provider 429 maps to the accepted throttling failure.
- [ ] Aborted/deadline execution cannot later replace the deadline result.
- [ ] Credentials are absent from results/log-safe assertions.
- [ ] Existing External HTTP and policy execution tests remain green.
- [ ] Storefront support is unchanged by this task.

## Validation

- [ ] focused Admin query execution tests
- [ ] DefinitionExecutor tests
- [ ] executable-registry availability tests
- [ ] targeted lint
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-062 or COMMERCE-069.

## Implementation Notes

Prefer reusing the existing server-side Admin request pattern in `src/commerce/integration/backend.ts` rather than introducing a second credential-resolution mechanism.

Do not redesign Admin `resultSchema` semantics here. The current persisted schema remains authoritative until COMMERCE-062 introduces derived result-contract semantics.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

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

Pending review.

### Follow-up

None.
