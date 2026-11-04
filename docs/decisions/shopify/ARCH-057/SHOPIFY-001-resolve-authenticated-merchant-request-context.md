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
status: review
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
| `tests/unit/home-route.test.ts` | Adapt the declared home consumer's fixture to merchant request context; preserve its billing/onboarding assertions |
| `tests/unit/pending-recoveries-route.test.ts` | Adapt the declared resource consumer's fixture to local context and scalar subscription; preserve admission/queue-reader assertions |
| `tests/unit/routes/app-layout-access.test.ts` | Adapt the declared parent consumer's context fixture; preserve lifecycle/surface assertions |
| `tests/unit/routes/billing-status.test.ts` | Adapt the declared billing-status consumer's context fixture; preserve DTO/admission assertions |
| `tests/unit/routes/reinstalling-route.test.ts` | Adapt the declared reinstall loader/action context fixture; preserve reconciliation and redirect assertions |
| `tests/unit/recovery-list-route.test.ts` | Adapt fixture wiring through the changed recovery access helper; preserve independent tenant/lifecycle/reader assertions |
| `tests/unit/recovery-detail-route.test.ts` | Adapt fixture wiring through the changed recovery access helper; preserve independent tenant/lifecycle/reader assertions |
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

Architect scope clarification (4 November 2026, Attempt 1): the seven existing consumer suites listed above are authorised test-only adaptations necessitated by this task's changed authentication/read composition boundary. Retain their behavioural assertions and use the new context fixture or real access helper with its new ports. This amendment does not authorise production changes to additional routes, downstream route migration, weakened access assertions, new dependencies or schema changes. Run the seven adapted suites as focused regression validation in addition to the exact package entrypoints below. Any further existing test path requiring edits must be returned for another bounded scope decision.

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

- [x] Implement and type the single request-context module and explicit refresh middleware.
- [x] Refactor existing resolver reads without duplicate existence probes.
- [x] Wire the declared first consumers and both access helpers.
- [x] Preserve tenant, bootstrap, profile refresh, lifecycle and post-action freshness.
- [x] Add the required router/PostgreSQL/failure evidence.

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

- [x] Parallel matched page loaders migrated by this task authenticate/refresh once and reuse the same scalar reads; independent HTTP requests and tenants never share context.
- [x] Established standalone status/poll access has zero profile GraphQL requests and no bootstrap writes; required lifecycle/subscription checks remain.
- [x] Missing rows, first install, profile change, unchanged replay and concurrent bootstrap preserve current outcomes and unique identities.
- [x] Non-GET and post-action loaders cannot observe stale cached mutation state.
- [x] Context secrets/admin/session objects never appear in loader JSON or logs.
- [x] Actual upstream diagnostic markers survive safe emission; malformed data never becomes trusted identity.
- [x] Installed router/typecheck and migrated database evidence validate the chosen mechanism.

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

- [x] `npm run test:merchant-request:unit`
- [x] `npm run test:merchant-request:router` — actual installed router; an SDK port fixture is explicitly recorded as simulated
- [x] `npm run test:merchant-request:postgres` — required cases execute, not skip
- [x] `npm run typecheck` and `npm run build` — server-only import boundaries
- [x] Focused ESLint of modified/new implementation/test files and `git diff --check`
- [x] Same-fixture before/after repository calls, emitted SQL, provider calls, writes and outcomes; record relation expansion separately

## Stop Condition

After the defined work and required evidence pass, set this task to review, complete its report and return to moda_architect. Stop on unsupported pinned-router behaviour, changed auth contract, missing declared test path or required schema/API change. Do not install a new router version, weaken auth or implement downstream tasks.

## Implementation Notes

Current `v8_middleware` is already enabled. Verify through actual types/runtime; current online documentation is explanatory, not a substitute for 7.18.2 tests. Shared request facts are an internal composition improvement. No global session cache, middleware framework or freshness scheduler is needed.

## Completion Report

### Status

Ready for Review — Attempt 1, codex, 2026-11-04. Implementation committed and pushed as `f69948137a20d8b994691194b5e081593e39e77c` on `task/ARCH-057-SHOPIFY-001`. No merge to main, downstream promotion or architect acceptance is asserted.

### Files Changed

Implementation commit contains only the following task-owned paths, including the architect-authorised seven-suite fixture amendment recorded above:

```text
app/routes/app/billing/status/route.ts
app/routes/app/home/route.jsx
app/routes/app/pending-recoveries/route.jsx
app/routes/app/recoveries/access.server.ts
app/routes/app/reinstalling/route.jsx
app/routes/app/route.jsx
app/routes/auth/catchall/route.jsx
app/services/feature-preferences/access.server.ts
app/services/shop/merchant-request-context.server.ts
app/services/shop/shop.service.ts
package.json
tests/helpers/merchant-request-fixtures.ts
tests/integration/merchant-request-context-router.test.ts
tests/integration/merchant-shop-bootstrap.postgres.test.ts
tests/unit/home-route.test.ts
tests/unit/merchant-request-context.test.ts
tests/unit/pending-recoveries-route.test.ts
tests/unit/recovery-detail-route.test.ts
tests/unit/recovery-list-route.test.ts
tests/unit/routes/app-layout-access.test.ts
tests/unit/routes/auth-catchall.test.ts
tests/unit/routes/billing-status.test.ts
tests/unit/routes/reinstalling-route.test.ts
tests/unit/services/shop.service.test.ts
```

### Work Completed

- Added a private typed router context promise and a separate authentication promise. GET/HEAD readers share in-flight success/failure; subscription/settings are lazy and memoized. Missing prerequisites share one authenticated repair and seed both scalar rows.
- Added the explicit page GET/HEAD refresh middleware and retained the auth entry's explicit refresh. Established direct resources and actions resolve local Shop identity without routine provider calls or writes.
- Changed resolver existence reads into useful full scalar reads and return `{shop, subscription, settings}`. Compatibility `resolveShopifyShop` returns its Shop. Profile updates, NO_CONTRACT provisioning, locale normalization and reinstall behaviour remain; malformed/provider-conflicting identity is rejected before writes.
- Migrated the declared layout/home/pending/status/reinstall consumers and both access helpers. Layout/pending use cached scalar subscription status; home/status retain their distinct rich commercial projection. Helpers preserve active-only subscription filtering and independent lifecycle checks, and expose merchant context only to server composition.
- Non-GET calls obtain fresh Shop/row closures without reading or storing the GET context. The real pinned router document POST creates a GET loader request within the same HTTP context; SPA revalidation creates a fresh navigation context. Both see changed persisted fixture state.
- Source diagnostics use Shared 3.1.0 and deployment-environment resolution. Actual safe messages, bounded Error causes, Prisma codes, provider errors/status/request IDs and available trusted Shop correlation survive. Redirect Responses retain identity/headers. Credential/PII/URL spans are removed before Shared emission; log-sink failure preserves the business result.

### Validation Results

| Command / gate | Result |
|---|---|
| `npm run test:merchant-request:unit` | 92 passed |
| `npm run test:merchant-request:router` | 7 passed |
| `npm run test:merchant-request:postgres` on pushed implementation | 7 passed; zero skipped |
| Seven architect-authorised existing consumer suites | 117 passed |
| `npm run typecheck` | passed |
| `npm run build` | passed; server-only imports accepted |
| Focused ESLint across all changed implementation/test paths | passed |
| `git diff --check` | passed before implementation commit |

The additional regression command was:

```sh
npx vitest run tests/unit/home-route.test.ts tests/unit/pending-recoveries-route.test.ts tests/unit/routes/app-layout-access.test.ts tests/unit/routes/billing-status.test.ts tests/unit/routes/reinstalling-route.test.ts tests/unit/recovery-list-route.test.ts tests/unit/recovery-detail-route.test.ts
```

There are 223 passing focused candidate tests in total (92 + 7 + 7 + 117). Router tests execute React Router 7.18.2's real middleware/static-handler and memory-router lifecycles. Shopify SDK/provider and Prisma ports are explicitly synthetic in that suite. One case connects the actual migrated layout/home exports to the real request context and real profile resolver; it verifies one authentication/profile/scalar read set, the separately retained rich commercial projection, and absence of private authentication data in loader JSON.

The PostgreSQL suite uses `pgvector/pgvector:pg17`, Testcontainers 12.1.0 and all 71 canonical forward migrations. It uses real Prisma SQL and owned disposable containers. Concurrent bootstrap uses two one-connection clients, verifies distinct backend PIDs, and waits at a barrier after both absent-Shop reads. It leaves exactly one Shop, subscription and settings row. The real P2003 bootstrap failure rolls back Shop creation; zero partial Shop rows remain. Missing-row repair makes one provider observation. All task-created clients and containers are closed/stopped through teardown/finally paths; no shared Docker resources were pruned.

Container commands used the existing active Colima context:

```sh
export DOCKER_HOST="$(docker context inspect --format '{{.Endpoints.docker.Host}}')"
export TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock
npm run test:merchant-request:postgres
```

Provider observations in PostgreSQL tests are controlled `admin.graphql` Response fixtures, not live Shopify calls.

#### Same-fixture before/after measurements

The original resolver was executed from `3d581bb87b8ed93358ed6a16216bebd1e39d3bec`, temporarily restored for the compatible baseline branches and restored to candidate source in a Python `finally` block. Baseline: three compatible cases passed; four new-context cases are deliberately inapplicable to original code. The required candidate suite executes all seven without skips.

Both runs use a fresh migrated container with the same authenticated domain/profile, locale/country/timezone and no-contract scalar fixture. These numbers describe the selected scalar composition, not all home-page commercial/support/overview work.

| Fixture | Repository calls | Emitted SQL reads | Write statements | Transaction control | Provider calls | Related-row expansion |
|---|---:|---:|---:|---:|---:|---:|
| Original two-reader scalar composition | 8 | 4 | 0 | 0 | 2 | 0 |
| Candidate two-reader scalar composition | 3 | 3 | 0 | 0 | 1 | 0 |
| Candidate direct local context + subscription | 2 | 2 | 0 | 0 | 0 | 0 |

Prisma batches duplicate `findUnique` calls in the baseline: eight repository calls are four actual SQL reads, not eight. First install remains three write statements with one durable row in each of the three tables; profile change uses two successful single-row updates and no subscription write; unchanged replay has no write or transaction. The home rich plan/pending-plan/period composition remains separate and is covered by existing consumer regressions. No throughput or latency claim is made.

Actual captured query text and call order for the measured fixtures follow; SQL parameters are intentionally not logged:

<details>
<summary>Captured SQL and repository/provider counters</summary>

```json
[
  {
    "label": "before-page",
    "calls": [
      "Shop.findUnique",
      "Shop.findUnique",
      "Subscription.findUnique",
      "ShopSettings.findUnique",
      "Subscription.findUnique",
      "ShopSettings.findUnique",
      "Subscription.findUnique",
      "Subscription.findUnique"
    ],
    "sql": [
      "SELECT \"commerce\".\"Shop\".\"id\", \"commerce\".\"Shop\".\"domain\", \"commerce\".\"Shop\".\"shopifyShopId\", \"commerce\".\"Shop\".\"platform\"::text, \"commerce\".\"Shop\".\"onboardingCompleted\", \"commerce\".\"Shop\".\"storeLocale\", \"commerce\".\"Shop\".\"defaultLanguageTag\", \"commerce\".\"Shop\".\"defaultTimeZone\", \"commerce\".\"Shop\".\"defaultCountryCode\", \"commerce\".\"Shop\".\"status\"::text, \"commerce\".\"Shop\".\"installedAt\", \"commerce\".\"Shop\".\"uninstalledAt\", \"commerce\".\"Shop\".\"reinstallPendingAt\", \"commerce\".\"Shop\".\"createdAt\", \"commerce\".\"Shop\".\"updatedAt\" FROM \"commerce\".\"Shop\" WHERE \"commerce\".\"Shop\".\"domain\" IN ($1,$2) OFFSET $3",
      "SELECT \"billing\".\"Subscription\".\"id\", \"billing\".\"Subscription\".\"shopId\" FROM \"billing\".\"Subscription\" WHERE \"billing\".\"Subscription\".\"shopId\" IN ($1,$2) OFFSET $3",
      "SELECT \"shopify\".\"ShopSettings\".\"id\", \"shopify\".\"ShopSettings\".\"defaultLanguageTag\", \"shopify\".\"ShopSettings\".\"defaultTimeZone\", \"shopify\".\"ShopSettings\".\"defaultCountryCode\", \"shopify\".\"ShopSettings\".\"shopId\" FROM \"shopify\".\"ShopSettings\" WHERE \"shopify\".\"ShopSettings\".\"shopId\" IN ($1,$2) OFFSET $3",
      "SELECT \"billing\".\"Subscription\".\"id\", \"billing\".\"Subscription\".\"shopId\", \"billing\".\"Subscription\".\"planId\", \"billing\".\"Subscription\".\"observedShopifyPlanHandle\", \"billing\".\"Subscription\".\"status\"::text, \"billing\".\"Subscription\".\"billingPeriodId\", \"billing\".\"Subscription\".\"currentPeriodStart\", \"billing\".\"Subscription\".\"currentPeriodEnd\", \"billing\".\"Subscription\".\"trialEndsAt\", \"billing\".\"Subscription\".\"cancelAtPeriodEnd\", \"billing\".\"Subscription\".\"providerSubscriptionId\", \"billing\".\"Subscription\".\"providerCoverageEndAt\", \"billing\".\"Subscription\".\"lastSyncedAt\", \"billing\".\"Subscription\".\"lastSyncErrorCode\", \"billing\".\"Subscription\".\"lastSyncErrorAt\", \"billing\".\"Subscription\".\"pendingShopifyPlanHandle\", \"billing\".\"Subscription\".\"pendingPlanId\", \"billing\".\"Subscription\".\"pendingEffectiveAt\", \"billing\".\"Subscription\".\"nextReconcileAt\", \"billing\".\"Subscription\".\"lastProviderLifecycleState\"::text, \"billing\".\"Subscription\".\"lastProviderLifecycleEventId\", \"billing\".\"Subscription\".\"lastProviderLifecycleEventAt\", \"billing\".\"Subscription\".\"createdAt\", \"billing\".\"Subscription\".\"updatedAt\" FROM \"billing\".\"Subscription\" WHERE \"billing\".\"Subscription\".\"shopId\" IN ($1,$2) OFFSET $3"
    ],
    "reads": 4,
    "writes": 0,
    "transactionControl": 0,
    "providerCalls": 2,
    "relationExpansion": 0
  },
  {
    "label": "after-page",
    "calls": [
      "Shop.findUnique",
      "Subscription.findUnique",
      "ShopSettings.findUnique"
    ],
    "sql": [
      "SELECT \"commerce\".\"Shop\".\"id\", \"commerce\".\"Shop\".\"domain\", \"commerce\".\"Shop\".\"shopifyShopId\", \"commerce\".\"Shop\".\"platform\"::text, \"commerce\".\"Shop\".\"onboardingCompleted\", \"commerce\".\"Shop\".\"storeLocale\", \"commerce\".\"Shop\".\"defaultLanguageTag\", \"commerce\".\"Shop\".\"defaultTimeZone\", \"commerce\".\"Shop\".\"defaultCountryCode\", \"commerce\".\"Shop\".\"status\"::text, \"commerce\".\"Shop\".\"installedAt\", \"commerce\".\"Shop\".\"uninstalledAt\", \"commerce\".\"Shop\".\"reinstallPendingAt\", \"commerce\".\"Shop\".\"createdAt\", \"commerce\".\"Shop\".\"updatedAt\" FROM \"commerce\".\"Shop\" WHERE (\"commerce\".\"Shop\".\"domain\" = $1 AND 1=1) LIMIT $2 OFFSET $3",
      "SELECT \"shopify\".\"ShopSettings\".\"id\", \"shopify\".\"ShopSettings\".\"shopId\", \"shopify\".\"ShopSettings\".\"onboardingCompleted\", \"shopify\".\"ShopSettings\".\"plan\", \"shopify\".\"ShopSettings\".\"recoveryDelayMinutes\", \"shopify\".\"ShopSettings\".\"aiResponseDelayMinutes\", \"shopify\".\"ShopSettings\".\"recoveryOfferMode\"::text, \"shopify\".\"ShopSettings\".\"fixedShopifyDiscountId\", \"shopify\".\"ShopSettings\".\"followUpEnabled\", \"shopify\".\"ShopSettings\".\"followUpDelayMinutes\", \"shopify\".\"ShopSettings\".\"notifyOnInitialRecoveryOutreach\", \"shopify\".\"ShopSettings\".\"defaultLanguageTag\", \"shopify\".\"ShopSettings\".\"defaultTimeZone\", \"shopify\".\"ShopSettings\".\"defaultCountryCode\", \"shopify\".\"ShopSettings\".\"createdAt\", \"shopify\".\"ShopSettings\".\"updatedAt\" FROM \"shopify\".\"ShopSettings\" WHERE (\"shopify\".\"ShopSettings\".\"shopId\" = $1 AND 1=1) LIMIT $2 OFFSET $3",
      "SELECT \"billing\".\"Subscription\".\"id\", \"billing\".\"Subscription\".\"shopId\", \"billing\".\"Subscription\".\"planId\", \"billing\".\"Subscription\".\"observedShopifyPlanHandle\", \"billing\".\"Subscription\".\"status\"::text, \"billing\".\"Subscription\".\"billingPeriodId\", \"billing\".\"Subscription\".\"currentPeriodStart\", \"billing\".\"Subscription\".\"currentPeriodEnd\", \"billing\".\"Subscription\".\"trialEndsAt\", \"billing\".\"Subscription\".\"cancelAtPeriodEnd\", \"billing\".\"Subscription\".\"providerSubscriptionId\", \"billing\".\"Subscription\".\"providerCoverageEndAt\", \"billing\".\"Subscription\".\"lastSyncedAt\", \"billing\".\"Subscription\".\"lastSyncErrorCode\", \"billing\".\"Subscription\".\"lastSyncErrorAt\", \"billing\".\"Subscription\".\"pendingShopifyPlanHandle\", \"billing\".\"Subscription\".\"pendingPlanId\", \"billing\".\"Subscription\".\"pendingEffectiveAt\", \"billing\".\"Subscription\".\"nextReconcileAt\", \"billing\".\"Subscription\".\"lastProviderLifecycleState\"::text, \"billing\".\"Subscription\".\"lastProviderLifecycleEventId\", \"billing\".\"Subscription\".\"lastProviderLifecycleEventAt\", \"billing\".\"Subscription\".\"createdAt\", \"billing\".\"Subscription\".\"updatedAt\" FROM \"billing\".\"Subscription\" WHERE (\"billing\".\"Subscription\".\"shopId\" = $1 AND 1=1) LIMIT $2 OFFSET $3"
    ],
    "reads": 3,
    "writes": 0,
    "transactionControl": 0,
    "providerCalls": 1,
    "relationExpansion": 0
  },
  {
    "label": "after-direct-status",
    "calls": [
      "Shop.findUnique",
      "Subscription.findUnique"
    ],
    "sql": [
      "SELECT \"commerce\".\"Shop\".\"id\", \"commerce\".\"Shop\".\"domain\", \"commerce\".\"Shop\".\"shopifyShopId\", \"commerce\".\"Shop\".\"platform\"::text, \"commerce\".\"Shop\".\"onboardingCompleted\", \"commerce\".\"Shop\".\"storeLocale\", \"commerce\".\"Shop\".\"defaultLanguageTag\", \"commerce\".\"Shop\".\"defaultTimeZone\", \"commerce\".\"Shop\".\"defaultCountryCode\", \"commerce\".\"Shop\".\"status\"::text, \"commerce\".\"Shop\".\"installedAt\", \"commerce\".\"Shop\".\"uninstalledAt\", \"commerce\".\"Shop\".\"reinstallPendingAt\", \"commerce\".\"Shop\".\"createdAt\", \"commerce\".\"Shop\".\"updatedAt\" FROM \"commerce\".\"Shop\" WHERE (\"commerce\".\"Shop\".\"domain\" = $1 AND 1=1) LIMIT $2 OFFSET $3",
      "SELECT \"billing\".\"Subscription\".\"id\", \"billing\".\"Subscription\".\"shopId\", \"billing\".\"Subscription\".\"planId\", \"billing\".\"Subscription\".\"observedShopifyPlanHandle\", \"billing\".\"Subscription\".\"status\"::text, \"billing\".\"Subscription\".\"billingPeriodId\", \"billing\".\"Subscription\".\"currentPeriodStart\", \"billing\".\"Subscription\".\"currentPeriodEnd\", \"billing\".\"Subscription\".\"trialEndsAt\", \"billing\".\"Subscription\".\"cancelAtPeriodEnd\", \"billing\".\"Subscription\".\"providerSubscriptionId\", \"billing\".\"Subscription\".\"providerCoverageEndAt\", \"billing\".\"Subscription\".\"lastSyncedAt\", \"billing\".\"Subscription\".\"lastSyncErrorCode\", \"billing\".\"Subscription\".\"lastSyncErrorAt\", \"billing\".\"Subscription\".\"pendingShopifyPlanHandle\", \"billing\".\"Subscription\".\"pendingPlanId\", \"billing\".\"Subscription\".\"pendingEffectiveAt\", \"billing\".\"Subscription\".\"nextReconcileAt\", \"billing\".\"Subscription\".\"lastProviderLifecycleState\"::text, \"billing\".\"Subscription\".\"lastProviderLifecycleEventId\", \"billing\".\"Subscription\".\"lastProviderLifecycleEventAt\", \"billing\".\"Subscription\".\"createdAt\", \"billing\".\"Subscription\".\"updatedAt\" FROM \"billing\".\"Subscription\" WHERE (\"billing\".\"Subscription\".\"shopId\" = $1 AND 1=1) LIMIT $2 OFFSET $3"
    ],
    "reads": 2,
    "writes": 0,
    "transactionControl": 0,
    "providerCalls": 0,
    "relationExpansion": 0
  }
]
```

</details>

#### Diagnostic and failure ownership

| Injection / owner | Emitted Shared evidence and outcome |
|---|---|
| Errors-only GraphQL / profile resolver | Original `profile-original-marker`, actual provider code/request ID, provider_response origin; no bootstrap writes |
| Installed SDK GraphqlQueryError / profile resolver | Original SDK and provider messages/code/request ID retained; data body excluded |
| Installed SDK HttpResponseError / profile resolver | Original SDK/upstream markers, actual 503/request ID, explicit redaction flag |
| SDK transport exception / profile resolver | Actual HttpRequestError marker and cause; transport origin; same source exception propagated |
| Invalid JSON / profile resolver | Original parse failure and cause; internal origin; no fabricated providerError |
| Malformed or mismatched identity / profile resolver | Distinct internal rejection; no tenant creation, update or switch |
| Local Shop lookup / Shop service | Original multiline Prisma reason, P2021 and cause survive real Shared JSON; following safe failure reason remains visible after URL redaction |
| Both lazy scalar reads / request context | Original DB marker/P2021/cause and trusted Shop ID in real Shared JSON; no provider field fabrication or refresh |
| Bootstrap constraint failure / resolver + real transaction | Original P2003 propagated and rollback verified |
| Throwing real Shared console sink / resolver | Original failure identity and successful bootstrap result unchanged |
| SDK redirect Response / request context | Same Response object, Location and Shopify security header retained; no local reads |

Tests capture actual Shared JSON output, rather than only mocked logger calls, and assert that injected credential, email, signed-URL and provider-data sentinels are absent from emitted records. Error causes are bounded to four Error entries; no global diagnostic registry, telemetry or replacement generic logger was added.

#### Source, build and launcher provenance

- Node 24.19.0 through the workspace bootstrap; React Router 7.18.2; Shopify React Router SDK 1.2.1; Prisma Client 6.19.3; Shared 3.1.0; Testcontainers PostgreSQL 12.1.0.
- Implementation start: `3d581bb87b8ed93358ed6a16216bebd1e39d3bec`; implementation end/pushed: `f69948137a20d8b994691194b5e081593e39e77c`.
- Built server `build/server/index.js` SHA-256: `547d7229bdb72438cc3f1ce9b2eba4cbfc7ecbefff5118c85735eb9909742627`; generated build is ignored, not committed.
- Parent synchronized pre-claim head: `3254c9cc8c7d95ccd1f53418eb79cc5c8da7236f`; durable claim: `8d966214380ce2bae683ab9916a7bb4efaef44dc`, pushed, 2026-11-04T03:39:50Z.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent physical worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-001`; branch `task/ARCH-057-SHOPIFY-001`.
- Implementation physical worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-001`; same task branch.
- Parent and implementation remote task branch fast-forward: not needed; origin/main incorporated: already current, as proved by the launcher. Dependency gate passed; no dependencies.
- Recursive submodule sync/update passed in preparation. Recorded and final working Database pin both `8e74634ff92be9900f693c0c449ffce888e7d617`.
- Shared workspace/source checkout switched or mutated for implementation: no. Another task worktree reused: no. Parent implementation gitlink changed/staged: no.
- Complete local command output is in `/tmp/shopify001-{unit,router,regressions,before-postgres,after-postgres,typecheck,build,lint}.log`; durable counts and measured SQL are recorded above.

### Deviations

The architect added a narrow test-only scope amendment for seven existing consumer suites; no additional production route migration was added. The actual router exposes readonly context types, so the helper accepts `Readonly<RouterContextProvider>` while retaining its actual get/set methods. Existing direct JS route-test callers receive an isolated provider by default; actual framework handlers receive the framework provider.

Initial container autodetection failed because the host uses Colima rather than the default Docker socket; selecting the existing context resolved it without host changes. An initial baseline assertion incorrectly equated eight repository calls with eight SQL statements; observed Prisma batching corrected the SQL expectation to four. Final baseline and candidate runs pass.

### Assumptions

Request contexts belong to framework requests/navigations, as verified against the installed router. Cached scalar rows are a request read composition, not a cross-table atomic snapshot or a mutation admission decision. Explicit authentication-entry/profile refresh remains the SDK/provider boundary.

### Unresolved Issues

None in this bounded submission. Architect review is pending. Downstream task states are unchanged.

### Architectural Concerns

No schema, dependency version, router flag/origin-policy, queue, billing identity or external contract change was needed. The public merchant-context helper is available for the separately owned downstream migrations.

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
