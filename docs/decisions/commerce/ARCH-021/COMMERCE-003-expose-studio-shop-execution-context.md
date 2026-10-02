---
id: ARCH-021-COMMERCE-003
architecture_id: ARCH-021
title: Expose a server-validated Studio shop execution context
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-018
enables:
  - ARCH-021-COMMERCE-004
created: 2026-09-23
updated: 2026-09-23
---

# Expose a server-validated Studio shop execution context

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Define and expose the authenticated server-side shop context that later Studio authoring and preview phases will use, including whether the selected shop has an offline Shopify session available, without exposing the offline access token.

## Context

Commerce already has real shop search/inspection through the production backend and already resolves an offline Shopify session for production Shopify operations. What is missing is a small Studio contract representing **which shop is being authored/tested against**.

Phase 1 needs this context before live tool testing or agent configuration is introduced. The selection itself is UI work owned by ARCH-021-COMMERCE-004.

## Scope

- Add a Studio shop-execution-context type distinct from the existing merchant-inspection detail model.
- Add authenticated server service/action(s) to list/search eligible Studio shops and resolve one exact selected shop by id.
- Resolve shop id/domain/label/plan from existing Commerce data.
- Determine whether an offline Shopify session exists for the resolved shop using existing session data.
- Return only bounded availability metadata; never return the Shopify offline token/session secret.
- Translate missing/unauthorised/unavailable states using existing Studio result semantics.

## Out of Scope

- Persisting a selected shop in the database.
- Adding the global shop selector UI.
- Performing Shopify API calls.
- Resolving external credentials for the selected shop.
- Modifying Shopify Session schema or token lifecycle.
- Prompt/model configuration.

## Requirements

The Phase 1 shop context must be explicit and server-validated. A conceptual shape is:

```ts
{
  shopId: string;
  domain: string;
  label: string;
  plan: string;
  shopifyOfflineSessionAvailable: boolean;
}
```

Equivalent naming is permitted, but:

- `shopId` is the durable Commerce shop id;
- domain comes from the persisted shop record;
- the browser never supplies/overrides a domain independently of the selected id;
- offline-session availability is boolean/status metadata only;
- no access token or session payload crosses the server boundary.

A shop lacking an offline session is still a valid selectable shop context; later live Shopify execution must fail/disable explicitly rather than silently changing shops.

## Work Items

- [x] Add the bounded Studio shop-execution-context contract.
- [x] Add authenticated list/search and exact-resolution service/action support, reusing current production shop inspection/search.
- [x] Add offline Shopify session availability lookup without selecting/serialising the token.
- [x] Add tests for found, missing, unavailable and no-offline-session states.
- [x] Add a data-safety regression proving no Shopify access token/session secret appears in the returned object or serialized test response.

## Interfaces / Contracts

Consumes:

- existing production Commerce shop search/inspection from ARCH-020-COMMERCE-013/018
- nested Prisma `Shop`/`Session` data already used by Commerce Shopify policy execution
- existing Studio auth/result contracts

Produces:

- one Commerce-local Studio shop-execution-context contract and server resolver.

No Database or Shared schema change is required.

## Dependencies

- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-018

Both are Complete in the Phase 1 definition snapshot.

## Enables

- ARCH-021-COMMERCE-004

## Acceptance Criteria

- [x] A real persisted shop can be searched and resolved by exact shop id.
- [x] The resolved domain cannot be replaced by caller-supplied domain text.
- [x] The result reports whether an offline Shopify session exists without returning its token.
- [x] A shop without an offline session remains selectable and is marked unavailable for future Shopify execution rather than silently substituted.
- [x] Missing/forbidden/unavailable states use existing bounded Studio failure semantics.

## Validation

- [x] focused shop-context service tests
- [x] focused server action/auth test
- [x] data-safety assertion for Session/accessToken non-disclosure
- [x] targeted lint/typecheck for changed files — changed-file ESLint passed; repository typecheck was executed and retained only the reported pre-existing Prisma/publication typing baseline, with no new shop-context diagnostic reported.
- [x] `git diff --check`

No Shopify network call is permitted in this task.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin ARCH-021-COMMERCE-004.

## Implementation Notes

Reuse the existing shop/session schema. Do not create a new durable `selectedShop` field; Phase 1 selection is request/navigation context, not business state.

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/studio/contracts.ts`
- `src/commerce/integration/studio/services.ts`
- `src/studio/server-actions.ts`
- `src/studio/server-services.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/shop-execution-context.test.ts`
- `tests/shop-execution-context-action.test.ts`

### Work Completed

- Added the distinct `ShopExecutionContext` contract with bounded shop identity, plan, and `shopifyOfflineSessionAvailable` metadata.
- Added authenticated `listShopExecutionContexts` and exact-id `getShopExecutionContext` service methods and server-action exports.
- Reused existing Commerce inspection authorization and development-bypass principal flow. The selected shop domain and plan are read from the persisted shop row; caller input contains only the shop id.
- Resolved offline-session availability with an existence-only Prisma projection for `{ shop, isOnline: false }` selecting `{ id: true }`; no access token or session payload is returned or serialized.
- Added in-memory service support and focused tests for found, missing, unavailable, forbidden, development bypass, no offline session, exact persisted domain, and access-token non-disclosure behavior.

Acceptance mapping:
- persisted search and exact resolution: `src/commerce/integration/studio/services.ts`, `tests/shop-execution-context.test.ts`
- caller domain cannot override persisted domain: `tests/shop-execution-context.test.ts`
- boolean offline availability and no-session selectability: `src/commerce/integration/studio/services.ts`, `tests/shop-execution-context.test.ts`
- bounded missing/forbidden/unavailable semantics: `src/commerce/integration/studio/services.ts`, `tests/shop-execution-context.test.ts`
- server-only action boundary: `src/studio/server-actions.ts`, `tests/shop-execution-context-action.test.ts`

### Validation Results

Agent-executed validation:
- `npm ci` — completed; installed the locked dependencies. npm reported the repository's existing Node engine mismatch (`required 24.19.0`, current `24.21.0`) and audit warnings.
- `npm test -- --run tests/shop-execution-context.test.ts tests/shop-execution-context-action.test.ts` — passed, 2 files / 6 tests.
- `npm test -- --run tests/studio-integration.test.ts tests/studio-services.test.ts` — passed, 2 files / 15 tests.
- `npx eslint src/studio/contracts.ts src/studio/server-services.ts src/studio/server-actions.ts src/studio/testing/in-memory-studio-services.ts src/commerce/integration/studio/services.ts tests/shop-execution-context.test.ts tests/shop-execution-context-action.test.ts` — passed with no errors or warnings.
- `git diff --check` — passed.
- `npm run typecheck` — failed on the existing generated-Prisma typing baseline, including pre-existing errors in `src/commerce/integration/backend.ts`, `src/commerce/integration/backend/publication-storage.ts`, existing feature/list code in `src/commerce/integration/studio/services.ts`, and `tests/c20-integration-fixture.test.ts`; no new context-specific errors remained after the implementation fixes.
- No Shopify or other third-party network call was made.

### Deviations

- Full repository typecheck remains blocked by the documented existing Prisma-client/type-generation baseline. Focused runtime tests and changed-file lint pass.

### Assumptions

- An offline Shopify session is available when an existing non-online `Session` row matches the persisted shop domain, consistent with existing Commerce provider resolution.

### Unresolved Issues

Full repository typecheck requires the existing generated Prisma typing/publication baseline to be repaired outside this task scope.

### Architectural Concerns

None.

### Architect Reconciliation

- The architect reconciled the task checkboxes from the submitted implementation snapshot and validation evidence rather than requiring a documentation-only implementation attempt.
- Submitted implementation commit: `ce8c8bc`; submitted parent report commit: `344f7fd`.
- The supplied review archive is rooted at the dedicated parent task surface `moda-interact-workspace-task-ARCH-021-COMMERCE-003/` and contains the task Commerce implementation tree plus its recursively materialised nested `database/` contents.
- The executor did not copy the launcher's exact parent/implementation path, synchronization SHA and recursive-submodule packet fields into the Completion Report. The architect has not invented those missing packet values. This is recorded as a procedural evidence omission; no implementation rework is required because the submitted review archive provides the isolated task surfaces needed for this review.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 was reviewed against the ARCH-021 Phase 1 contract, the submitted Commerce implementation `ce8c8bc`, the parent report `344f7fd`, and the supplied combined review snapshot.

The implementation establishes a distinct server-validated shop execution context without introducing durable selected-shop state. Exact resolution accepts only the Commerce shop id, reuses the existing staff inspection authorization boundary, and re-reads domain/plan from persisted shop data. Offline Shopify availability is determined with an existence-only Session projection (`select: { id: true }`); no access token or Session payload crosses the Studio service/action boundary. A missing offline session remains a valid context with `shopifyOfflineSessionAvailable: false`.

The list/search path reuses the bounded production shop inspection search. The exact path preserves existing not-found, forbidden, unavailable and development-bypass semantics. No Shopify/provider network call was introduced.

No task-owned architecture or security defect was found. The missing launcher-packet details in the executor Completion Report are a documentation/evidence omission only and were reconciled above rather than creating a code-free Attempt 2. Future submissions should preserve those launcher fields in the Completion Report.

### Reviewed Files

- `src/studio/contracts.ts`
- `src/commerce/integration/studio/services.ts`
- `src/studio/server-actions.ts`
- `src/studio/server-services.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/shop-execution-context.test.ts`
- `tests/shop-execution-context-action.test.ts`

### Validation Reviewed

- focused shop execution-context/action tests: 6 passed
- existing Studio regression tests: 15 passed
- changed-file ESLint: passed
- `git diff --check`: passed
- repository typecheck: non-zero only on the executor-reported pre-existing Prisma/publication typing baseline; no new shop-context diagnostic reported
- static architect comparison against the supplied ARCH-021 Phase 1 baseline: task-owned source/test changes are bounded to the declared scope

### Architecture Conformance

Conformant. COMMERCE-003 provides only the server-validated selected-shop execution context required by Phase 1. It does not persist selection, call Shopify, resolve external credentials, alter Session schema/token lifecycle, or introduce model/prompt configuration.

### Follow-up

`ARCH-021-COMMERCE-004` is now Ready. No implementation correction is required for COMMERCE-003.
