---
id: ARCH-057-SHOPIFY-001
architecture_id: ARCH-057
title: Resolve authenticated merchant context once within each request
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-04T03:39:50Z
attempt: 1
depends_on: []
enables:
- ARCH-057-SHOPIFY-002
- ARCH-057-SHOPIFY-004
- ARCH-057-SHOPIFY-005
- ARCH-057-SHOPIFY-006
- ARCH-057-SHOPIFY-007
- ARCH-057-SHOPIFY-008
- ARCH-057-SHOPIFY-009
- ARCH-057-SHOPIFY-011
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-001: Resolve authenticated merchant context once within each request

## Architecture

Architecture ID: `ARCH-057`. Document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Coordinator: `moda_architect`.

Mandatory execution/logging contract: `docs/architecture/ARCH-057/task-contract.md`. **Defined but not materialised.**

## Objective

Give authenticated merchant routes one request-owned local identity/read context while making remote profile refresh an explicit page/authentication responsibility.

## Context

Review F06 records three database reads plus one Admin GraphQL call per unchanged-Shop resolution. Parent and child repeat it; polling/actions do the same. The existing React Router configuration already enables `v8_middleware`. This task owns the context mechanism and first consumers. Domain tasks consume the frozen API in their routes/services.

## Scope

All paths below are relative to `moda-interact`.

### Existing files to modify

| Path | Exact responsibility |
|---|---|
| `app/services/shop/shop.service.ts` | Refactor existing resolution to return useful local rows once; preserve bootstrap/profile/lifecycle behaviour |
| `app/routes/app/route.jsx` | Export page middleware and consume cached merchant context; use scalar subscription for existing navigation projection |
| `app/routes/app/home/route.jsx` | Replace own auth/resolution with context; retain its existing rich billing projection/current and pending plan names until SHOPIFY-004 owns that composition |
| `app/routes/app/pending-recoveries/route.jsx` | Local authenticated context and cached scalar subscription; retain queue reader |
| `app/routes/app/billing/status/route.ts` | Local authenticated context; retain status DTO and admission |
| `app/routes/app/reinstalling/route.jsx` | Fresh context for loader/action; retain existing reconciliation and redirects |
| `app/routes/auth/catchall/route.jsx` | Keep explicit authenticated profile/provisioning refresh and reinstall entry |
| `app/services/feature-preferences/access.server.ts` | Accept optional framework context; preserve result/policy and expose server-only merchant context |
| `app/routes/app/recoveries/access.server.ts` | Same context threading, preserving independent access checks and returned public fields |
| `tests/unit/services/shop.service.test.ts` | Update resolution/bootstrap/profile expectations and diagnostic assertions |
| `tests/unit/routes/auth-catchall.test.ts` | Preserve reinstall/authentication behaviour |
| `tests/unit/merchant-route-access-policy.test.ts` | Preserve existing lifecycle/surface matrix |
| `react-router.config.ts` | Read-only unless typing requires a precise existing middleware declaration; do not change flags/origin policy |
| `package.json` | Add exactly the test entrypoints below; no dependency change |

### New files

| Path | Purpose |
|---|---|
| `app/services/shop/merchant-request-context.server.ts` | Server-only typed context, request-local promises, page middleware |
| `tests/unit/merchant-request-context.test.ts` | Authentication/tenant/lazy read/cache boundary and failure fixtures |
| `tests/integration/merchant-request-context-router.test.ts` | Actual pinned router parent/child, direct resource and POST→loader lifecycle |
| `tests/integration/merchant-shop-bootstrap.postgres.test.ts` | Canonical migrated bootstrap/profile/no-op/missing-row recovery |
| `tests/helpers/merchant-request-fixtures.ts` | Small synthetic authenticated-context fixtures used by the new suites |

No other existing route/service refactor is selected here. Other task owners migrate their routes against this API.

## Out of Scope

No process cache, Redis cache, schema, new profile timestamp/TTL, new webhook topic, subscription reconciliation on reads, broad billing/settings reader rewrite or auth bypass. No client-side context carrying session/admin objects. Do not modify independent webhook authentication.

## Requirements

1. Create a private React Router `createContext` key holding the in-flight merchant-context promise, using the actual installed `RouterContextProvider`. Store the promise before awaiting so parallel parent/child readers share success or failure. Authentication has its own request-scoped promise. Never key a process-global map by domain/token/URL.
2. `getMerchantRequestContext({request, context})` authenticates with the existing Shopify SDK, derives the domain from that authenticated session and resolves current local Shop. Preserve SDK redirects/Responses and security headers. A submitted Shop ID/domain does not authorize anything.
3. Established standalone resources use a local Shop lookup and lazy row reads; they make no routine profile GraphQL call and perform no writes. Missing Shop or a required missing settings/subscription row follows the current bootstrap/repair behaviour once, using the authenticated provider identity. Concurrent callers share that repair promise. Never trust a malformed/mismatched provider identity to create or switch tenants.
4. The parent `merchantPageContextMiddleware` explicitly refreshes the Shopify profile on GET/HEAD before its matched parallel loaders. Reuse the current remote query/normalization, conditional updates and provisioning contract. The auth catchall remains another explicit refresh boundary. This preserves page-view profile/locale freshness without a new global TTL or shop-update handler. Direct status/poll/mutation routes use local state.
5. Refactor the resolver into `resolveShopifyMerchantSnapshot` returning `{shop, subscription, settings}` with full **scalar** Subscription/ShopSettings rows. Upgrade its existing existence reads to useful scalar reads rather than adding new ones. Preserve `resolveShopifyShop` as a small Shop-returning compatibility entry used by explicit auth/bootstrap callers. It is not a read-policy gate.
6. Context exposes lazy memoized `readSubscription()` and `readSettings()`, seeded when the page resolver already loaded those rows. Do not eagerly fetch either on a standalone resource that needs neither. Related billing plans/periods/counters remain owned by commercial read composition. Cached rows do not imply a cross-table atomic snapshot.
7. Shared merchant row caching applies only to GET/HEAD. Non-GET actions obtain fresh local Shop and per-call read closures; they do not reuse/store the GET read context. Post-action loaders must see new persisted state, whether the router uses the same HTTP request or a subsequent GET. Test the exact pinned router behaviour; no Request mutation or guessed object-identity cache.
8. Each loader/resource retains its own capability/lifecycle check. Preserve current active-only filtering where a guard previously used `getSubscription`; the parent uses full scalar status as before. Do not widen FROZEN/SUPPORT_ONLY/REINSTALLING access. Mutation services retain fresh locked rereads.
9. `settingsAccess(request, context?)` and `requireRecoveryHistory(request, context?)` retain existing returned fields and add a server-only `merchant` property. Optional context supports existing direct test/helper callers through a new isolated provider, never a global fallback. Domain owners must pass actual framework context in production handlers. No raw context/authentication/session/credential object is returned to the browser.
10. Parse errors-only GraphQL and malformed JSON/identity responses distinctly. Retain actual provider errors/messages/cause through Shared server diagnostics; domain mismatch is internal identity rejection. No credentials, GraphQL data or complete provider payload is logged.

## Work Items

- [ ] Implement and type the single request-context module and explicit refresh middleware.
- [ ] Refactor existing resolver reads without duplicate existence probes.
- [ ] Wire the declared first consumers and both access helpers.
- [ ] Preserve tenant, bootstrap, profile refresh, lifecycle and post-action freshness.
- [ ] Add the required router/PostgreSQL/failure evidence.

## Interfaces / Contracts

```ts
type MerchantRequestContext = {
  authentication: Awaited<ReturnType<typeof authenticate.admin>>;
  shop: Shop;
  readSubscription(): Promise<Subscription | null>;
  readSettings(): Promise<ShopSettings | null>;
};

getMerchantRequestContext(input: {
  request: Request;
  context: RouterContextProvider;
}): Promise<MerchantRequestContext>;

merchantPageContextMiddleware: MiddlewareFunction;
```

Use actual imported SDK/Prisma/router types, not `any`. Authentication retains all SDK members callers need, including its redirect helper. The context is server-only; exported names contain no task ID. The public helper is the contract consumed by SHOPIFY-002–010. A direct caller without framework context uses the access helper's isolated fallback; it receives no request-sharing claim.

Add these exact package script values:

```json
{
  "test:merchant-request:unit": "vitest run tests/unit/merchant-request-context.test.ts tests/unit/services/shop.service.test.ts tests/unit/routes/auth-catchall.test.ts tests/unit/merchant-route-access-policy.test.ts",
  "test:merchant-request:router": "vitest run tests/integration/merchant-request-context-router.test.ts",
  "test:merchant-request:postgres": "MODA_MERCHANT_REQUEST_POSTGRES=1 vitest run tests/integration/merchant-shop-bootstrap.postgres.test.ts"
}
```

The PostgreSQL suite uses existing Testcontainers dependency, pg17+pgvector and canonical migrations; owns and cleans its container. Do not add a second general database-test runner.

## Dependencies

None. Real launcher still verifies latest integrated source and no ARCH-057 allocation collision.

## Enables

- ARCH-057-SHOPIFY-002
- ARCH-057-SHOPIFY-004
- ARCH-057-SHOPIFY-005
- ARCH-057-SHOPIFY-006
- ARCH-057-SHOPIFY-007
- ARCH-057-SHOPIFY-008
- ARCH-057-SHOPIFY-009
- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [ ] Parallel matched page loaders migrated by this task authenticate/refresh once and reuse the same scalar reads; independent HTTP requests and tenants never share context.
- [ ] Established standalone status/poll access has zero profile GraphQL requests and no bootstrap writes; required lifecycle/subscription checks remain.
- [ ] Missing rows, first install, profile change, unchanged replay and concurrent bootstrap preserve current outcomes and unique identities.
- [ ] Non-GET and post-action loaders cannot observe stale cached mutation state.
- [ ] Context secrets/admin/session objects never appear in loader JSON or logs.
- [ ] Actual upstream diagnostic markers survive safe emission; malformed data never becomes trusted identity.
- [ ] Installed router/typecheck and migrated database evidence validate the chosen mechanism.

### Required cases and log owners

| Case | Required result |
|---|---|
| Parent + child started concurrently, same context | One SDK authentication and profile observation; no repeated subscription/settings existence reads |
| Two contexts, same Shop; two Shops | Independent observations; no cross-request/cache reuse |
| Direct command/status route | Authenticated local Shop + required admission, no parent dependence or GraphQL |
| Action updates lifecycle/settings followed by document and SPA revalidation | Loader observes committed result, never action/pre-action cache |
| Provider GraphQL errors, network failure, invalid JSON, domain mismatch | Source marker/cause logged at resolver; correct provider/internal origin; no writes |
| DB lookup/bootstrap failure | Original Prisma message/code/cause; no partial bootstrap state |
| Log sink throws | Auth outcome/rollback/redirect behaviour unchanged |

## Validation

- [ ] `npm run test:merchant-request:unit`
- [ ] `npm run test:merchant-request:router` — actual installed router; an SDK port fixture is explicitly recorded as simulated
- [ ] `npm run test:merchant-request:postgres` — required cases execute, not skip
- [ ] `npm run typecheck` and `npm run build` — server-only import boundaries
- [ ] Focused ESLint of modified/new implementation/test files and `git diff --check`
- [ ] Same-fixture before/after repository calls, emitted SQL, provider calls, writes and outcomes; record relation expansion separately

## Stop Condition

After the defined work and required evidence pass, set this task to review, complete its report and return to moda_architect. Stop on unsupported pinned-router behaviour, changed auth contract, missing declared test path or required schema/API change. Do not install a new router version, weaken auth or implement downstream tasks.

## Implementation Notes

Current `v8_middleware` is already enabled. Verify through actual types/runtime; current online documentation is explanatory, not a substitute for 7.18.2 tests. Shared request facts are an internal composition improvement. No global session cache, middleware framework or freshness scheduler is needed.

## Completion Report

### Status

Not Started. Defined but not materialised; no execution claim or worktree is asserted.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact commands, fixture/case results, source/build/installed-package provenance, original diagnostic assertions, SQL/provider counts where required, and task-owned resource cleanup.

### Deviations

None.

### Assumptions

The launcher will verify actual dependency status and the accepted integrated source before claiming this task.

### Unresolved Issues

Implementation and required validation are outstanding.

### Architectural Concerns

Return changed ownership, persisted identity, schema, queue, transaction or external contract requirements to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only; no implementation accepted.

### Reviewed Files

Definition and current snapshot touchpoints only.

### Validation Reviewed

Definition checks only. Implementation evidence is outstanding.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

Return the completed task for architect review; do not start enabled tasks.
