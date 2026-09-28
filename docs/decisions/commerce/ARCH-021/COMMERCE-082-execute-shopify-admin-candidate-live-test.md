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
<<<<<<< HEAD
status: ready
priority: 73
executor: null
claimed_at: null
attempt: 0
=======
status: complete
priority: 73
executor: null
claimed_at: null
attempt: 1
>>>>>>> e44d01d530cf6d9f4eb803a7cd17b4cd15291938
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

<<<<<<< HEAD
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
=======
- [x] Add complete-candidate Shopify Admin live-Test domain service.
- [x] Add authenticated Server Action.
- [x] Resolve `shopId` to server-authoritative shop context/domain/session; never trust browser domain/token.
- [x] Narrow `AdminQueryExecutionPort` to the exact provider-execution context shared by production and authoring.
- [x] Expose the existing Admin execution port through `CommerceBackend` without exposing credentials.
- [x] Reuse Admin compiler/mapping/result normalization semantics.
- [x] Reuse existing Admin execution port/transport rather than duplicate GraphQL networking.
- [x] Validate Result Template against compiler output before I/O.
- [x] Reuse `renderDefinitionResult`.
- [x] Return the five bounded stage outcomes, canonical processed values and renderedText.
- [x] Preserve one-provider-request/deadline/throttle rules.
- [x] Prove zero durable/publication-proof writes.
- [x] Add credential-leak and no-provider-on-invalid-candidate tests.
>>>>>>> e44d01d530cf6d9f4eb803a7cd17b4cd15291938

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

<<<<<<< HEAD
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
=======
- [x] ADMIN-authorized Test accepts a complete current Shopify Admin definition + arguments + shopId.
- [x] Browser cannot supply shop domain/access token.
- [x] Invalid definition/mapping/result-contract/template fails before provider I/O.
- [x] Provider execution reuses the existing Admin execution transport/normalization semantics through the narrow context; no fake grant/release/conversation identity is constructed.
- [x] Canonical renderer produces the returned `renderedText`.
- [x] Result stages are exactly candidateValidation, shopResolution, providerRequest, resultValidation, resultRendering.
- [x] At most one provider request is reserved per Test call.
- [x] Credentials/auth headers/raw secrets are absent from result and logs.
- [x] Test performs zero durable/publication-proof write and does not change publish eligibility.

## Validation

- [x] `npx vitest run tests/shopify-admin-live-test.test.ts tests/shopify-admin-live-test-action.test.ts`
- [x] focused invalid-candidate/no-provider-call tests
- [x] focused selected-shop/domain/token trust-boundary tests
- [x] focused renderer/output-envelope tests
- [x] focused zero-write/publication-gate test
- [x] targeted ESLint for changed files
- [x] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [x] `git diff --check`
>>>>>>> e44d01d530cf6d9f4eb803a7cd17b4cd15291938

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Prefer dependency injection around the existing Admin execution port so tests remain deterministic and network-free. Do not call the public/private MCP route from Studio Test merely to reuse execution; that would incorrectly import grant/conversation authorization into authoring.

## Completion Report

### Status

<<<<<<< HEAD
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
=======
Ready for Review

### Files Changed

```text
moda-interact-commerce/src/commerce/execution/index.ts
moda-interact-commerce/src/commerce/execution/ports.ts
moda-interact-commerce/src/commerce/integration/backend.ts
moda-interact-commerce/src/commerce/tool-authoring/shopify-admin-live-test.ts
moda-interact-commerce/src/studio/tools/shopify-admin-live-test-server-actions.ts
moda-interact-commerce/tests/definition-execution.test.ts
moda-interact-commerce/tests/shopify-admin-live-test-action.test.ts
moda-interact-commerce/tests/shopify-admin-live-test.test.ts
```

### Work Completed

Implemented the complete-candidate Admin live-Test service and ADMIN-authorized Server Action. Candidate schema, Admin compilation, exact compiler-derived result schema, mapped arguments, and Result Template compatibility are checked before shop resolution or provider I/O. The action resolves `shopId` through the existing server-authoritative Studio service; the provider port resolves the offline access token server-side.

Narrowed `AdminQueryExecutionPort` to shop domain, deadline, abort signal, request budget, trace ID, and span ID, and exposed the existing port on `CommerceBackend`. The live Test reuses that port, canonical result normalization, and `renderDefinitionResult`; it returns only the five bounded stages, normalized result values, and rendered text. No durable Tool/revision/audit/receipt/proof writes or UI changes were added.

### Validation Results

Agent-executed validation:

- `npx vitest run tests/shopify-admin-live-test.test.ts tests/shopify-admin-live-test-action.test.ts tests/definition-execution.test.ts tests/admin-query-execution.test.ts tests/admin-graphql-compiler.test.ts tests/result-template-authoring.test.ts tests/commerce-lifecycle.test.ts tests/tool-authoring-validation.test.ts` — passed, 8 files and 96 tests.
- `npx eslint src/commerce/execution/ports.ts src/commerce/execution/index.ts src/commerce/integration/backend.ts src/commerce/tool-authoring/shopify-admin-live-test.ts src/studio/tools/shopify-admin-live-test-server-actions.ts tests/shopify-admin-live-test.test.ts tests/shopify-admin-live-test-action.test.ts tests/definition-execution.test.ts` — passed with no output.
- `npx tsc --noEmit --pretty false` — repository-wide check reports 30 existing errors across 17 files; no diagnostics are reported in the new service/action, narrowed execution port/barrel, or directly updated tests. The remaining errors are in unrelated existing editor, discovery, result-template, fixture, and test files.
- `git diff --check` — passed.
- Prisma client generated from `database/prisma/schema.prisma` in this isolated worktree for TypeScript validation; no database migration or shared database change was made.

The focused tests cover invalid definition/mapping/result contract/template before I/O, selected-shop/offline-session trust, narrow provider context, one reserved request, bounded throttle diagnostics, normalized output and canonical rendering, credential exclusion, ADMIN authorization, no publication writes, and unchanged `LIVE_TEST_REQUIRED` publication gating.

### Deviations

No scope deviations. Repository-wide TypeScript validation remains non-green because of the 30 unrelated diagnostics noted above; task-owned source and direct test files are clean under the isolated TypeScript scan.

### Assumptions

Node and npm were available in the task environment. `npm ci` emitted the repository's engine warning because the available Node is 24.21.0 while `package.json` declares 24.19.0; focused tests, lint, Prisma generation, and task-file type diagnostics ran successfully.

### Unresolved Issues

Repository-wide `npx tsc --noEmit` still reports 30 errors in 17 files, including existing editor/template/discovery/test typing issues. These are outside the task changes and are not required to implement the Admin live-Test path.

### Architectural Concerns

None identified. The live Test is non-durable and does not provide saved-revision publication proof; the existing `LIVE_TEST_REQUIRED` gate remains in force.

### Launcher Evidence

Physical worktree isolation:

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-082
parent branch: task/ARCH-021-COMMERCE-082
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-082
implementation branch: task/ARCH-021-COMMERCE-082
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
```

Start-of-attempt synchronization from launcher packet:

```text
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: already-current
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current
```

Recursive implementation submodules from launcher packet:

```text
git submodule sync --recursive: passed
git submodule update --init --recursive: passed
recorded submodule commit: database @ 0a8d3b9feade69690b6c1e33aeda051ea588bd45
```

Task execution:

```text
task: ARCH-021-COMMERCE-082
executor: copilot
attempt: 1
implementation claim commit: f66b697d434e3088c4f8989ea224b6db523c5887
parent task-definition materialization commit: 2e6d469143d02edbedfc7ed5bfcb5d280cef136c
dependency gate: passed (COMMERCE-060, 062, 063, 070 complete)
```
>>>>>>> e44d01d530cf6d9f4eb803a7cd17b4cd15291938

## Architect Review

### Review Status

<<<<<<< HEAD
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
=======
Accepted

### Review Notes

Attempt 1 conforms to the C082 contract. The live-Test boundary validates the complete current Shopify Admin candidate and mapped arguments before shop/provider work, resolves only the server-authoritative selected shop, reuses the existing `AdminQueryExecutionPort` and canonical renderer, and returns only bounded stage/result data. No browser-supplied domain/token, fabricated production grant/release/conversation identity, duplicate GraphQL transport, durable Tool/publication write or publication-proof receipt was introduced.

The submitted task file omitted the standard Architect Review section; this acceptance overlay restores that architect-owned section rather than returning otherwise-valid implementation work for report-only churn.

### Reviewed Files

- `moda-interact-commerce/src/commerce/execution/ports.ts`
- `moda-interact-commerce/src/commerce/execution/index.ts`
- `moda-interact-commerce/src/commerce/integration/backend.ts`
- `moda-interact-commerce/src/commerce/tool-authoring/shopify-admin-live-test.ts`
- `moda-interact-commerce/src/studio/tools/shopify-admin-live-test-server-actions.ts`
- `moda-interact-commerce/tests/shopify-admin-live-test.test.ts`
- `moda-interact-commerce/tests/shopify-admin-live-test-action.test.ts`
- `moda-interact-commerce/tests/definition-execution.test.ts`

### Validation Reviewed

- Submitted focused compatibility packet: 8 files / 96 tests passed.
- Submitted targeted ESLint: passed.
- Submitted `git diff --check`: passed.
- Submitted repository-wide TypeScript check remains non-green with 30 diagnostics in 17 unrelated files; no C082 changed implementation/test file is reported with diagnostics.
- Automated tests correctly use fixtures/adapters rather than requiring live Shopify I/O; no live Shopify call or migration is required by C082 acceptance.

### Architecture Conformance

Conforms to ARCH-021 and the accepted C060/C062/C063/C070 boundaries. `AdminQueryExecutionPort` is narrowed only to provider-execution context and remains structurally usable by production. Authoring reuses the production Admin transport/session lookup/result normalization and `renderDefinitionResult`, enforces one provider-request budget, keeps access tokens server-only, exposes only bounded canonical values/rendered text, and performs no durable/publication-proof write. The current publication `LIVE_TEST_REQUIRED` gate remains unchanged.

### Follow-up

`ARCH-021-COMMERCE-083` is referenced by C082 `enables`, but no C083 task file is present in the submitted snapshot. C082 acceptance therefore cannot promote a non-materialised dependent task in this overlay. Materialise/reconcile C083 separately before execution.
>>>>>>> e44d01d530cf6d9f4eb803a7cd17b4cd15291938
