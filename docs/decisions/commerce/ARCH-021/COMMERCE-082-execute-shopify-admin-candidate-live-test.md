---
id: ARCH-021-COMMERCE-082
architecture_id: ARCH-021
title: Execute and render a non-durable Shopify Admin candidate live
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 73
executor: copilot
claimed_at: 2026-09-28T06:22:15Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-060
  - ARCH-021-COMMERCE-062
  - ARCH-021-COMMERCE-063
  - ARCH-021-COMMERCE-070
enables:
  - ARCH-021-COMMERCE-083
created: 2026-09-28
updated: 2026-09-28
---

# Execute and render a non-durable Shopify Admin candidate live

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add the missing staff-authorized Shopify Admin live-Test backend for an unsaved/current Tool candidate, reusing the production Admin execution/result-normalization and canonical Result Template renderer while creating no durable Tool/publication proof.

## Context

`NewToolEditor` currently renders only `Admin query validation is non-mutating.` on Test. Production Shopify Admin execution already exists through `createAdminQueryExecutionPort`, compiler-derived result contracts, normalization and `renderDefinitionResult`. Studio already has a server-authoritative selected-shop execution context with domain/offline-session availability.

This is a distinct backend task from External live testing because it resolves Shopify shop/session credentials and uses GraphQL transport rather than External Connection credentials.

## Scope

Primary implementation areas:

```text
src/commerce/tool-authoring/shopify-admin-live-test.ts        # new
src/studio/tools/shopify-admin-live-test-server-actions.ts    # new, or exact bounded Server Action equivalent
src/commerce/execution/ports.ts                              # narrow Admin execution context for production + authoring reuse
src/commerce/query/admin.ts                                   # consume existing execution port
src/commerce/integration/backend.ts                           # expose existing AdminQueryExecutionPort internally
src/commerce/execution/renderer.ts                            # consume
src/studio/server-actions.ts / Studio services                # consume selected-shop execution context
```

Focused tests should be added as:

```text
tests/shopify-admin-live-test.test.ts
tests/shopify-admin-live-test-action.test.ts
```

Use existing test fixtures/adapters rather than real Shopify network access in automated tests.

## Out of Scope

- React Test-tab presentation; COMMERCE-083.
- Changing Admin GraphQL compiler semantics.
- Changing production MCP/grant authorization.
- Creating a persisted live-Test/publication receipt.
- Publication-gate removal/change; the existing `LIVE_TEST_REQUIRED` publication behaviour remains until a separately agreed exact-saved-revision proof design exists.
- New database tables or Shared contracts.

## Requirements

### R1 — complete-candidate Test contract

Accept one bounded semantic input:

```ts
type ShopifyAdminLiveTestInput = {
  definition: CommerceToolDefinition; // execution.kind MUST be SHOPIFY_ADMIN_GRAPHQL
  arguments: Record<string, unknown>;
  shopId: string;
};
```

Server Action requires current Studio platform `ADMIN` authorization and resolves `shopId` through the existing server-authoritative shop execution-context/service. Do not accept shop domain or access token from the browser.

### R2 — validate definition/result/template before provider I/O

Before Shopify transport:

1. parse `CommerceToolDefinitionSchema`;
2. require `SHOPIFY_ADMIN_GRAPHQL`;
3. compile with the existing Admin compiler;
4. require compiled result contract to match the definition's current compiler-derived result schema according to COMMERCE-070 semantics;
5. require valid mapped arguments;
6. validate Result Template against the compiler `outputSchema` through COMMERCE-063.

Any failure here returns `INVALID_CANDIDATE`/bounded issues and performs zero provider request.

### R3 — use server-authoritative selected shop/session

Resolve selected `shopId` to its authoritative shop domain. Require an available Shopify offline session according to the existing Studio context/production Admin execution dependency. Access tokens remain server-only and must never appear in input/output/logs.

### R4 — reuse production Admin execution semantics through a narrow context

Do not implement a second GraphQL transport, response selector, nullable normalizer or template renderer.

The current `AdminQueryExecutionPort` accepts an entire `AuthorizedToolCall` even though `query/admin.ts` only requires provider-execution context. Narrow that Commerce-local port contract to exactly:

```ts
type AdminQueryExecutionContext = Pick<
  AuthorizedToolCall,
  "shopDomain" | "deadlineAt" | "signal" | "budget" | "traceId" | "spanId"
>;
```

and make `AdminQueryExecutionPort.execute(...).context` use that type. Production `DefinitionExecutor` may continue passing the full `AuthorizedToolCall` structurally. The authoring Test must pass only the narrow context; it must **not** fabricate grantId/releaseId/conversation/turn/tool revision identifiers.

Expose the already-created `dependencies.adminQuery` port on `CommerceBackend` as a Commerce-internal execution dependency (for example `adminQuery?: AdminQueryExecutionPort`). This exposes executable behaviour only; it must not expose access tokens/session rows.

Use that existing port to execute:

```text
mapped arguments
-> Admin GraphQL request
-> selected resultPath
-> compiler-owned result normalization/validation
-> canonical CommerceToolResult data.values envelope
```

Then call `renderDefinitionResult` for the exact candidate.

### R5 — deterministic stage result

Return these exact logical stages:

```text
candidateValidation
shopResolution
providerRequest
resultValidation
resultRendering
```

Each is `passed | failed | not-run` with bounded stable code/message. Return on success:

```text
renderedText
processedResult   # canonical normalized values only; bounded for display
```

Do not return access token, request Authorization header, unbounded GraphQL response, customer headers or credential material. If a safe GraphQL diagnostic summary is included, restrict it to operation name + bounded failure code; do not echo the authored document as provider diagnostic output.

### R6 — deadlines/provider budget

Reuse production Admin timeout/deadline/provider-budget behaviour. One Test invocation may reserve at most one provider request. Abort/deadline/throttle outcomes must map to bounded retryable codes without retry loops inside the authoring action.

### R7 — non-durable boundary

The Test performs no Tool/ToolRevision/audit/operation receipt/publication-proof write and does not satisfy the current publication `LIVE_TEST_REQUIRED` gate.

## Work Items

- [ ] Add complete-candidate Shopify Admin live-Test domain service.
- [ ] Add authenticated Server Action.
- [ ] Resolve `shopId` to server-authoritative shop context/domain/session; never trust browser domain/token.
- [ ] Narrow `AdminQueryExecutionPort` to the exact provider-execution context shared by production and authoring.
- [ ] Expose the existing Admin execution port through `CommerceBackend` without exposing credentials.
- [ ] Reuse Admin compiler/mapping/result normalization semantics.
- [ ] Reuse existing Admin execution port/transport rather than duplicate GraphQL networking.
- [ ] Validate Result Template against compiler output before I/O.
- [ ] Reuse `renderDefinitionResult`.
- [ ] Return the five bounded stage outcomes, canonical processed values and renderedText.
- [ ] Preserve one-provider-request/deadline/throttle rules.
- [ ] Prove zero durable/publication-proof writes.
- [ ] Add credential-leak and no-provider-on-invalid-candidate tests.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-060  production Shopify Admin Tool execution
ARCH-021-COMMERCE-062  compiler-derived Admin result schema
ARCH-021-COMMERCE-063  Result Template compatibility
ARCH-021-COMMERCE-070  runtime result-contract enforcement
createAdminQueryExecutionPort / AdminQueryExecutionPort
renderDefinitionResult
Studio getShopExecutionContext
```

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-060
- ARCH-021-COMMERCE-062
- ARCH-021-COMMERCE-063
- ARCH-021-COMMERCE-070

## Enables

- ARCH-021-COMMERCE-083

## Acceptance Criteria

- [ ] ADMIN-authorized Test accepts a complete current Shopify Admin definition + arguments + shopId.
- [ ] Browser cannot supply shop domain/access token.
- [ ] Invalid definition/mapping/result-contract/template fails before provider I/O.
- [ ] Provider execution reuses the existing Admin execution transport/normalization semantics through the narrow context; no fake grant/release/conversation identity is constructed.
- [ ] Canonical renderer produces the returned `renderedText`.
- [ ] Result stages are exactly candidateValidation, shopResolution, providerRequest, resultValidation, resultRendering.
- [ ] At most one provider request is reserved per Test call.
- [ ] Credentials/auth headers/raw secrets are absent from result and logs.
- [ ] Test performs zero durable/publication-proof write and does not change publish eligibility.

## Validation

- [ ] `npx vitest run tests/shopify-admin-live-test.test.ts tests/shopify-admin-live-test-action.test.ts`
- [ ] focused invalid-candidate/no-provider-call tests
- [ ] focused selected-shop/domain/token trust-boundary tests
- [ ] focused renderer/output-envelope tests
- [ ] focused zero-write/publication-gate test
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Prefer dependency injection around the existing Admin execution port so tests remain deterministic and network-free. Do not call the public/private MCP route from Studio Test merely to reuse execution; that would incorrectly import grant/conversation authorization into authoring.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

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

Pending

### Follow-up

None
