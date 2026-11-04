---
id: ARCH-057-SHOPIFY-003
architecture_id: ARCH-057
title: Simplify recovery credit purchases and refunds
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-11-04T10:41:30Z
attempt: 2
depends_on:
- ARCH-057-SHOPIFY-002
enables:
- ARCH-057-SHOPIFY-004
- ARCH-057-SHOPIFY-011
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-003: Simplify recovery credit purchases and refunds

## Architecture

Architecture ID: `ARCH-057`.

Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`.

Coordinator: `moda_architect`.

Mandatory execution, diagnostic, provenance and validation contract: `docs/architecture/ARCH-057/task-contract.md`. This task is materialised in the canonical parent and implementation worktrees recorded below. SHOPIFY-002 is complete and architect-accepted. Attempt 1 was reviewed with Changes Requested; the claim is cleared and this task is ready for correction, not accepted.

## Objective

Give recovery-credit history one bounded verification context and make purchase/refund admission use a single owning mutation boundary, with external evidence obtained before short, authoritative database transactions.

## Context

Review F03 finds provider HTTP and independent Prisma reads inside refund admission's Serializable transaction. F09 finds repeated Shop/subscription/credential/provider work per eligible history row and unbounded nested refunds. F08 finds route-level purchase prevalidation before the mutation service's otherwise efficient receipt replay. These touchpoints share purchase identity, refund eligibility and provider-cycle evidence; they form one reviewable change.

The new-purchase service intentionally obtains two provider lifecycle observations and reads the catalogue twice before its write transaction. Those freshness checks are retained. This task removes duplicate route/history work and relocates refund provider work; it does not relax admission, accounting or provider verification.

## Scope

All paths below are relative to `moda-interact`. Consume the accepted request context from SHOPIFY-001 and provider diagnostics/parser from SHOPIFY-002 without changing either contract.

### Existing files to modify

| Path | Exact responsibility |
|---|---|
| `app/services/billing/recovery-credit-purchase-management.service.ts` | One history context, bounded refund summaries, provider-before-transaction refund flow, current transaction-client reads, and owned failure/retry diagnostics |
| `app/services/billing/recovery-credit-purchase-request.service.ts` | Preserve service-owned replay/new-admission sequencing and add original operational diagnostics at handled/propagated failure boundaries; retain two provider observations and two catalogue reads |
| `app/routes/app/billing/recovery-credit-purchases/route.tsx` | Consume trusted merchant context, retain access/field/batch checks, and log original Admin GraphQL development-store verification failures |
| `app/routes/app/billing/options/route.tsx` | Action only: consume request context and delegate new-purchase admission/replay to the existing mutation service; remove redundant capacity/live-commercial prevalidation |
| `tests/unit/services/recovery-credit-purchase-management.service.test.ts` | Preserve existing provider/tenant/accounting outcomes and add the short-transaction, shared-history-context and replay cases |
| `tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts` | Preserve two observations/catalogue reads, receipt replay, unresolved-offer and cycle-change regressions; add diagnostics |
| `tests/unit/recovery-credit-purchase-manager.test.tsx` | Confirm the unchanged public history/refund/reactivation DTO remains renderable; no visual redesign |
| `tests/unit/billing-purchase-hub.test.tsx` | Confirm purchase replay/new-request result rendering remains unchanged |

### New files

| Path | Purpose |
|---|---|
| `app/services/billing/recovery-credit-provider-context.server.ts` | Typed provider observation and pure local/purchase matching; no cache, transaction owner or generic repository |
| `tests/unit/recovery-credit-history-budget.test.ts` | Actual service invocation counts and bounded latest/completed refund summary fixtures for 1/5/20 rows |
| `tests/unit/routes/recovery-credit-purchases.test.ts` | Actual route action/loader authorization, batch limits and original Admin GraphQL error output |
| `tests/unit/routes/billing-options-action.test.ts` | Actual action delegates receipt replay without provider prevalidation and preserves authorization/new-admission behavior |
| `tests/integration/recovery-credit-refunds.postgres.integration.test.ts` | Real migrated refund/reactivation/reservation races and rollback with controlled provider observations |
| `tests/integration/recovery-credit-purchases.postgres.integration.test.ts` | Real migrated same-ID/different-ID purchase races, cycle revalidation and three-entity atomic persistence |
| `tests/fixtures/recovery-credit-refunds.ts` | Small fixture builders and deterministic barriers for refund tests |
| `tests/fixtures/recovery-credit-purchases.ts` | Small plan/catalogue/provider/purchase fixtures for purchase tests |

Reuse `tests/helpers/billing-postgres.ts` from SHOPIFY-002. Its contract is sufficient; this task does not expand it into a generic runner. New test/helper files each stay below 300 lines. No package script/dependency is needed; Validation uses existing `npm test` with exact paths.

## Out of Scope

No real charge/refund execution, Background refund processor change, cash-value policy change, partial refund feature, arbitrary balance consolidation, schema/index/migration, process-wide cache, queue/outbox or identity migration. This purchase/refund task leaves identity generation unchanged within its own scope. SHOPIFY-012 subsequently replaces the three namespace literals under the user-confirmed development-only baseline; old digest compatibility is not an architecture requirement. Do not change pricing formulas, development-store zero-price rules, source/tenant guards or the public purchase/refund DTOs.

The options loader/read composition belongs to SHOPIFY-004. Privacy/retention and subscription-ended notice durability remain explicitly deferred; this task does not infer either policy from the presence of refund history. Do not alter another task or any `_index.md`.

## Requirements

### R1. Purchase service owns replay and fresh admission

Both route handlers use `getMerchantRequestContext({ request, context })`, retain active-Shop authorization and the existing per-surface access policy. Preserve the active-only subscription projection where the purchase-history guard previously used `getSubscription`. Request fields remain untrusted; preserve supported intent, bounded UUID/handle checks, same-Shop/provider validation and the maximum 20 unique refund selections.

In the options action remove the extra `getMerchantRecoveryCapacityState` and `getMerchantShopifySubscriptionState` calls. Keep the route's authenticated Shop and surface checks, then call the existing `requestRecoveryCreditPack` service. The service's first receipt lookup decides an authorized same-Shop/SHOPIFY receipt replay before provider/catalogue work. A replay that passes current route authorization must succeed during a provider outage without a new charge, observation or catalogue read.

For a new purchase retain exactly two `getSubscriptionLifecycleSnapshot` calls and two catalogue observations before the Serializable transaction. Preserve provider-before usage evidence, exact current billing cycle, plan/meter/quantity/price matching, transition-window rejection, unresolved-offer admission, final transaction-bound Subscription validation and atomic UsageEvent + RecoveryCreditPurchase + BillingOperation persistence. Do not reuse a presentation/history observation for this admission. No provider or Redis call occurs inside the write transaction.

### R2. History verifies shared facts once

Read the requested purchase page and count with the existing tenant/provider/status filters, deterministic purchase ordering, route page sizes 5/10/20, service cap 50 and out-of-range clamp. Validate purchase evidence before rendering as today.

When at least one visible ACTIVE purchase has monetary/development-store evidence requiring provider verification, read current Shop and Subscription context once and make one `getActiveSubscription` call for that history invocation. Project every eligible row against those same immutable request facts using the pure matcher below. If no row needs verification, make no provider or credential read. No cross-request memoization is permitted. Provider failure still fails the read at its existing boundary; do not silently present failure as confirmed refund eligibility or ineligibility.

The provider context contains only the provider observation and trusted Shopify Shop identity. Local context carries the queried local Shop identity/platform/status and Subscription/current BillingPeriod facts. The matcher compares the same provider identity derivation, handle, event membership, billing period ID and exact start/end predicates as today. History output is presentation; no later mutation can treat it as authority.

### R3. Bound both refund summaries without hiding older completion

Choose two bounded relation reads rather than a new raw-SQL subsystem:

1. The purchase-page query includes only the latest SHOPIFY refund per purchase using `take: 1` and `createdAt desc, id desc`.
2. One additional `recoveryCreditPurchase.findMany` is limited to the resulting page's IDs, the same `shopId` and `provider: SHOPIFY`; select purchase ID and one latest COMPLETED SHOPIFY refund per purchase with the same ordering and `take: 1`.

Skip the second query for an empty page. Merge the two summaries by purchase ID into the unchanged `latestRefund`/`completedRefund` output. Do not retain arbitrary refund history, select the first two refunds, or query per purchase. The second summary may legitimately refer to an older completed refund hidden behind many newer cancelled attempts.

For an unclamped nonempty page with at least one eligible row, the resulting service budget is **six repository Prisma invocations and one Partner call**, independent of 1/5/20 visible rows: count + page + completed-summary page + Shop + Subscription + credential. With no eligible rows it is three and zero; an empty page uses two and zero. A clamp adds one page query. These are explicit method counts, not a claim about relation expansion or SQL latency. The additional bounded summary read deliberately trades one method for bounded retained history.

### R4. Refund provider preflight precedes each write attempt

Keep the existing three-attempt P2034 bound and same request key. On each attempt:

1. Read the tenant/provider-scoped purchase with its bounded current live refund. Apply the existing pure early-out checks. An existing refund, terminal purchase, no available credits, invalid evidence or nonrefundable zero-value purchase returns the same existing outcome without provider work or a new hold.
2. Only for an apparently eligible new hold, obtain one fresh provider observation **before** opening the write transaction. A failure creates no refund, withdrawal or aggregate hold. Do not share this observation with a later attempt or another independently admitted purchase in a batch.
3. Start the existing Serializable transaction. Reread the purchase/live refund, local Shop, current Subscription/BillingPeriod and aggregate through the transaction client. Reapply early-out and money/quantity checks against current rows. Compare the captured provider identity/cycle/event against those transaction-local facts. Current Shop platform/status/Shopify identity must still authorize this operation; otherwise return the existing `REFUND_NOT_CURRENT_PROVIDER_CONTEXT` outcome.
4. Keep the existing refund creation, purchase CAS and purchased-counter CAS atomic. Preserve exact request identity, provider/tenant predicates, versions, current/reserved/refunding quantities and zero-available rejection. A failed CAS rolls everything back and enters the bounded retry with fresh preflight.

The preflight purchase read and transaction reread are intentional: the former avoids network work for known no-ops; the latter authorizes the hold. Remove root-client Shop/subscription/credential calls from inside the transaction. Test proxies may observe the boundary, but the PostgreSQL evidence must execute real reads, locks and CAS writes.

### R5. Preserve idempotent recovery and reactivation

Keep current unique-conflict receipt recovery, including same-Shop/provider validation and returned current purchase outcome. A replay may not create a second refund or balance hold. Preserve reactivation's transaction, provider-action fence, defensive zero-credit completion branch and three-entity CAS; the zero-credit validation amendment below governs evidence for that unreachable persisted state; no provider read is required for reactivation. Batches remain sequential, bounded and individually transactional rather than holding one transaction across provider calls.

Return all normal business denials in the existing typed outcomes. Unexpected persistence/transport errors retain their original cause. Do not hide retry exhaustion behind a new generic message without the originating error evidence.

### R6. Diagnostic ownership

Use direct Shared logging at the owning boundary, consuming SHOPIFY-002's typed provider error/recorded-source classification. Do not emit the same provider body again in route/service catches. Record safe context and local failure evidence at the boundary that actually converts or propagates it. Inject the real Shared sink in tests; checking a mocked `logger.error` call is insufficient.

| Failure / owner | Required emitted evidence | Preserved outcome |
|---|---|---|
| Partner read fails during history or mutation preflight, SHOPIFY-002 adapter | Original safe message/code/details/status/request ID/cause and truthful origin | History fails as before; new hold has no writes; no duplicate provider body downstream |
| Admin GraphQL development-store read fails, purchase-history route adapter | Actual SDK/HTTP/GraphQL error, safe request ID/cause; malformed data is internal evidence | Fail closed; never treat unknown as development-store true |
| History page/summary/local-context DB read fails, management service | Original Prisma message/code/cause, Shop and read stage | No fabricated history/eligibility result |
| Purchase transaction fails, request service | Original database/invariant message/code/cause and safe purchase ID | Full rollback or validated existing receipt; no second provider charge |
| Refund/reactivation P2034 retry, management service | Actual retry error/code/cause and bounded attempt at warn | Rollback and fresh retry; no network inside transaction |
| Refund/reactivation retry exhausted or aggregate invariant missing | Original final error/code/cause at error; truthful local origin | No partial withdrawal/refund/counter commit |
| Unique conflict with valid receipt recovery | Preserve ownership/result checks; ordinary replay is not a fabricated provider error | Existing outcome, no duplicate durable effect |
| Invalid input, cross-Shop/provider ID or normal no-credit/locked outcome | Preserve validation; no fabricated operational/provider exception | Existing safe response/outcome, no information leak |
| Shared sink throws | Real Shared isolation assertion | Identical HTTP outcome, rollback, retries and committed quantities |

Known cause chains are supplied explicitly as bounded Shared fields under the common contract; preserve the actual thrown cause as well. No raw form, provider payload, online user object, credential or payment detail enters logs or merchant responses.

## Architect Validation Amendment (2026-11-04)

The accepted baseline migration `20260912000000_arch010_first_production_baseline/migration.sql:1479–1484` defines `RecoveryCreditPurchase_lifecycle_amounts`: WITHDRAWN requires `currentAmount > 0`, while COMPLETED/REFUNDED require zero current and reserved amounts. No later pinned migration replaces this constraint. `reactivateRefund` requires WITHDRAWN before its defensive `COMPLETED_NO_CREDITS` branch, so successful execution of that branch against the canonical migrated database is not a reachable state.

For this bounded task, replace the impossible successful PostgreSQL zero-credit reactivation requirement with (1) real migrated PostgreSQL rejection of WITHDRAWN/currentAmount=0 by that exact constraint, asserting unchanged purchase/counter balances and versions, and (2) retention of the existing isolated unit regression for the unchanged defensive branch, labelled as such rather than production database proof. The submitted integration and unit assertions satisfy this amended zero-credit evidence requirement and were independently rerun during review.

This is a validation correction, not a financial or lifecycle policy change. It authorizes no schema change, constraint bypass, new legal state, provider refund, or removal/rewrite of the defensive branch. All other real transaction, race, rollback and diagnostic gates remain mandatory. The implementer's blocker record below is preserved as historical evidence; this amendment resolves that specific blocker only. The separate Admin-response logging finding prevents acceptance.

## Work Items

- [x] Consume request context in the declared route handlers while retaining independent access checks.
- [x] Remove duplicate purchase-route capacity/provider prevalidation and preserve service replay/admission.
- [x] Implement the small provider-observation/pure-matching module and one-context history projection.
- [x] Replace unbounded nested refunds with the two bounded summary reads.
- [x] Move each new-refund provider preflight before its write transaction and use only transaction-local current state for admission.
- [x] Retain replay, CAS, batch and reactivation behaviour; leave namespace replacement to SHOPIFY-012.
- [ ] Complete actual Shared-output assertions, deterministic call budgets and both migrated PostgreSQL suites. The budgets and 14 database cases pass, including the amended zero-credit constraint proof; Admin malformed-response privacy needs the correction in Architect Review.

## Interfaces / Contracts

Consumes the accepted SHOPIFY-001 `MerchantRequestContext` and SHOPIFY-002 provider parser/failure ownership and disposable PostgreSQL helper. Mutation admission does not consume cached Subscription as authoritative state.

The new source module exports these narrow internal operations using actual Prisma/domain types:

```ts
type RecoveryCreditProviderObservation = Readonly<{
  shopifyShopId: string;
  subscription: ProviderSubscription | null;
}>;

readRecoveryCreditProviderObservation(
  provider: BillingProvider,
  shopifyShopId: string,
): Promise<RecoveryCreditProviderObservation>;

matchesRecoveryCreditProviderContext(
  purchase: ShopifyPurchaseEvidence,
  local: RecoveryCreditLocalContext,
  observed: RecoveryCreditProviderObservation,
): boolean;
```

`ShopifyPurchaseEvidence` is the current validated purchase's provider/period/plan/event identity subset. `RecoveryCreditLocalContext` contains local Shop `{id, platform, status, shopifyShopId}` and current Subscription/BillingPeriod identity/start/end; its `shop.id` must equal the purchase's `shopId`. Define and export those exact structural subsets in the new module instead of exposing `PrismaClient` or accepting a request-supplied context.

The read function makes one provider operation and no domain DB reads; the matcher performs no I/O. History builds local context once. Refund supplies transaction-derived local context. The module does not own retries, authentication, a cache or a transaction.

Preserve `PurchaseHistoryPage`, `PurchaseHistoryItem`, `RefundOutcome`, `ReactivationOutcome`, request keys, queue/report states and existing BillingOperation fingerprints. New work does not create another persisted workflow state or cash-refund API.

## Dependencies

- ARCH-057-SHOPIFY-002 — Complete and architect-accepted, including its SHOPIFY-001 prerequisite, provider diagnostics/parser and PostgreSQL test helper.

## Enables

- ARCH-057-SHOPIFY-004
- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [x] Authorized existing purchase replay makes no provider/catalogue/capacity calls and retains its existing receipt; cross-Shop/provider replay is denied.
- [x] A new purchase still makes two fresh provider lifecycle observations and two catalogue observations outside its write transaction, with final local revalidation inside it.
- [x] Eligible 1/5/20-row history pages use six repository methods and one provider call; noneligible/empty/clamped branches meet the specified budgets.
- [x] Latest and completed refund summaries are independently correct and bounded, including an older completion behind many newer cancellations and equal-timestamp ordering.
- [x] Refund HTTP/credential/root-client context reads never execute while a write transaction is open.
- [x] Refund/refund, refund/reservation and reactivation interleavings preserve one durable hold, nonnegative balances, versions and provider-action fences on real PostgreSQL.
- [x] Purchase same-ID and same-offer races preserve one admissible durable request and atomic UsageEvent/Purchase/BillingOperation persistence.
- [ ] Every named operational failure retains original safe Shared output and cause; provider text is not duplicated and secret/PII sentinels do not appear.
- [x] No schema, dependency, public DTO, locale, pricing policy, hash preimage, identity or Background change occurred.

## Validation

Run from the prepared `moda-interact` implementation worktree under the mandatory execution contract.

- [x] `npm run prisma:generate`
- [x] `npm test -- tests/unit/services/recovery-credit-purchase-management.service.test.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts tests/unit/recovery-credit-history-budget.test.ts tests/unit/routes/recovery-credit-purchases.test.ts tests/unit/routes/billing-options-action.test.ts tests/unit/recovery-credit-purchase-manager.test.tsx tests/unit/billing-purchase-hub.test.tsx`
- [x] `MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/recovery-credit-refunds.postgres.integration.test.ts tests/integration/recovery-credit-purchases.postgres.integration.test.ts`
- [x] `npm run typecheck`
- [x] `npm run build`
- [x] `npx --no-install eslint app/services/billing/recovery-credit-purchase-management.service.ts app/services/billing/recovery-credit-purchase-request.service.ts app/services/billing/recovery-credit-provider-context.server.ts app/routes/app/billing/recovery-credit-purchases/route.tsx app/routes/app/billing/options/route.tsx tests/unit/recovery-credit-history-budget.test.ts tests/unit/routes/recovery-credit-purchases.test.ts tests/unit/routes/billing-options-action.test.ts tests/integration/recovery-credit-refunds.postgres.integration.test.ts tests/integration/recovery-credit-purchases.postgres.integration.test.ts tests/fixtures/recovery-credit-refunds.ts tests/fixtures/recovery-credit-purchases.ts` and focused lint of changed existing tests.
- [x] `git diff --check`

**Amended zero-credit evidence:** the real migrated-constraint rejection and unchanged balances/versions, together with the existing defensive-branch unit regression, satisfy the Architect Validation Amendment above. Do not describe this as successful PostgreSQL execution of `COMPLETED_NO_CREDITS`.

Both PostgreSQL files must run against task-owned `pgvector/pgvector:pg17` containers with all accepted forward migrations, using the prerequisite helper. Separate real Prisma connections and explicit barriers control races; provider ports are synthetic. Do not use a mocked transaction, fabricated SQL result or timing sleep as database proof.

Required database cases: two same-ID new purchases; different IDs competing for the same unresolved offer; billing-cycle change after provider observations but before final admission; rollback after one of the three purchase writes; two refund requests; reservation/version change before refund CAS; refund-versus-reactivation; reactivation after provider action has begun; the amended zero-credit constraint-rejection proof; failure after refund creation before counter CAS. Assert durable row counts, request identities, versions, reserved/refunding/current quantities and no partial writes.

Record same-fixture before/after method/provider counts and actual emitted SQL separately. The expected new refund preflight adds a deliberate read; the acceptance goal is a correct short transaction, not fewer reads at any cost. Include actual Shared JSON evidence, unavailable validation, warnings and owned-resource cleanup in the Completion Report.

## Stop Condition

When the defined work, acceptance criteria and required validation pass, set this task to review, return its Completion Report to `moda_architect` and stop. Do not mark it Complete or start SHOPIFY-004.

Stop for an architect amendment if dependency interfaces differ, an existing policy would have to change, a schema/Shared/Background edit is required, safe diagnostics cannot preserve source evidence, identity bytes would change, or real PostgreSQL validation cannot execute. Do not substitute mocks or a skipped suite for required database evidence.

## Implementation Notes

The history optimization is request-local reuse; refund admission deliberately reads again. The history summary design uses one bounded extra ORM call rather than specialized raw SQL. It yields six constant calls instead of the review's unbounded-history five-call hypothetical; record that distinction honestly.

Use pure matching to keep history and mutation predicates coherent without making a presentation cache authoritative. Keep existing per-purchase transactions and replay recovery. Do not batch independent mutations into a transaction spanning external work. The newer task names exist only in task/test metadata, not runtime names or events.

## Completion Report

### Status

Blocked — implementation published; architect amendment required before review submission. No acceptance decision has been made. The existing `RecoveryCreditPurchase_lifecycle_amounts` constraint rejects `WITHDRAWN/currentAmount=0`, while the required PostgreSQL zero-credit reactivation case needs precisely that state. The existing `COMPLETED_NO_CREDITS` service branch remains unchanged and is covered by its existing unit regression; successful real-database execution is unavailable under the accepted schema.

### Files Changed

Implementation commit `fffbf30641544574b7de72c7829b85a9ea4fc0d4`, pushed to `origin/task/ARCH-057-SHOPIFY-003` in `moda-interact`. All 15 changed files are on the task allowlist:

- Services: `recovery-credit-purchase-management.service.ts`, `recovery-credit-purchase-request.service.ts`, new `recovery-credit-provider-context.server.ts` in `app/services/billing/`.
- Routes: `app/routes/app/billing/recovery-credit-purchases/route.tsx`; action/import only in `app/routes/app/billing/options/route.tsx` (loader unchanged).
- Existing tests: the two declared service unit files and `tests/unit/recovery-credit-purchase-manager.test.tsx`.
- New tests: `tests/unit/recovery-credit-history-budget.test.ts`, `tests/unit/routes/recovery-credit-purchases.test.ts`, `tests/unit/routes/billing-options-action.test.ts`, both declared PostgreSQL integration files and both declared fixture files.
- The purchase-hub test needed no edits; its unchanged rendering checks pass. Every new file is below 300 lines (largest 170).

### Work Completed

Trusted request context is consumed independently by each handler, retaining active-Shop/surface authorization and the history active-only Subscription projection. The options action delegates receipt replay and admission directly, removing duplicate capacity/commercial reads. Actual-route tests replay a same-tenant receipt during provider/catalogue outage and deny foreign-Shop/provider receipts. New admission retains two provider lifecycle and two catalogue observations outside the Serializable transaction, final transaction-local Subscription validation and atomic UsageEvent/Purchase/BillingOperation persistence.

History uses one request-local typed observation and pure matcher, bounded latest and separately bounded completed refund summaries, deterministic timestamp/ID ordering and ID-based merge. The older-completion-behind-50-cancellations and equal-timestamp cases pass. Refunds obtain fresh evidence before each attempt, then reread purchase, live refund, Shop, Subscription/period and aggregate using only the transaction client. Current platform/status/Shopify identity changes deny admission. Three-attempt CAS retries, unique receipt recovery, sequential batches, provider-action fences and identities remain intact.

Operational failures use Shared 3.1.0 and the accepted provider/domain diagnostic adapter. Original Prisma codes/messages/causes, read stages, safe IDs and bounded retry attempt survive actual JSON output. Provider source evidence is not re-extracted downstream. Admin SDK, HTTP, HTTP-200 GraphQL and malformed success/error-envelope cases fail closed. Real Shared throwing sinks preserve exceptions and authorization; a genuine PostgreSQL serialization retry succeeds with the throwing sink and retains exact committed quantities.

### Validation Results

All listed executable commands passed on the published implementation; the task's separate required zero-credit success scenario remains unavailable and prevents review readiness.

- `npm run prisma:generate`: passed against pinned Database schema (also rerun by build).
- Exact seven-file focused unit/route/render command from Validation: **7 files, 106 tests passed**.
- Exact two-file `MODA_DISPOSABLE_INTEGRATION=1 npm test -- ...` command: **2 files, 14 tests passed**, none skipped, task-owned `pgvector/pgvector:pg17`, all forward migrations applied by unchanged prerequisite helper.
- `npm run typecheck`: passed.
- `npm run build`: passed; existing client chunk-size warning remains (merchant-i18n bundle ~1.22 MB). No build/dependency source changed.
- Exact declared scoped ESLint command plus all three changed existing test files: passed.
- `git diff --check`: passed.
- Existing Admin `ModaInteractRefundShopPlan` query validated successfully against configured **2026-07** schema with Shopify AI Toolkit; Partner documentation targeted configured **2026-10**. No live Shopify operations or financial execution.

Real PostgreSQL cases: identical-ID and different-ID/same-offer purchase races each leave one durable request, one usage event and one billing operation; cycle change after both observations denies all writes; injected failures after each real usage/purchase/operation write roll back all three. Two refund requests leave one hold; a separate connection reserves three credits between transaction reads and CAS, causes a real serialization retry with fresh observation and commits only seven refunding credits (purchase/counter version 2). Pending refund versus committed refund/reactivation reauthorizes current state and preserves one live hold (version 3). Provider-action-started reactivation remains fenced. Failure after real refund creation and purchase withdrawal but before counter CAS rolls everything back. The zero-credit fixture mutation is rejected by **`RecoveryCreditPurchase_lifecycle_amounts`** and leaves purchase/counter unchanged; this is blocking evidence, not successful completion coverage.

Same-fixture measurements (no latency/capacity claim):

| Eligible rows | Before repository method calls | Before Partner requests | After repository method calls | After Partner requests |
|---|---:|---:|---:|---:|
| 1 | 5 | 1 | 6 | 1 |
| 5 | 17 | 5 | 6 | 1 |
| 20 | 62 | 20 | 6 | 1 |

Measured by running the same new unit fixture against archived start commit `b40775fd2f0b68ed39efc4b937c9ecec2cd607f7` and current source, using real provider parsing, actual sealed-credential/configuration reader and synthetic fetch. Baseline intentionally fails the new assertions; it is comparison evidence, not an acceptance run. After noneligible/empty/clamped branches are respectively **3/0**, **2/0**, **7/1** repository/provider calls.

Actual PostgreSQL SQL is recorded separately: the same real history fixture emits **7 SELECTs before and 9 SELECTs after** for each 1/5/20-row case, zero transaction-control statements, same returned row counts. Provider reads are synthetic here, so credential SQL is excluded. Prisma batches identical concurrent `findUnique` reads in the original implementation: method counts do not imply one emitted SQL statement per invocation. The bounded completed summary deliberately adds SQL. Final complete suites emitted 338 purchase-suite and 389 refund-suite statements including fixture setup/assertion reads/transaction control; these totals are not per-operation budgets.

Representative actual Shared JSON fields captured after serialization (not logger-call mocks):

```json
{"level":"warn","event":"shopify.billing.recovery_credit_retry","data":{"operation":"request_refund","stage":"refund_transaction","origin":"database","shopId":"shop-1","identities":{"purchaseId":"one","attempt":"1"},"error":{"name":"PrismaClientKnownRequestError","message":"actual serialization marker 0"},"causeChain":[{"name":"Error","message":"original conflict cause"}],"databaseCode":"P2034","redactionApplied":false,"truncated":false}}
{"level":"error","event":"shopify.billing.provider_failed","data":{"operation":"verify_refund_development_store","origin":"provider_response","failureKind":"GRAPHQL","provider":"shopify","error":{"name":"ShopifyBillingProviderError","message":"original ADMIN_DENIED [REDACTED] [REDACTED]"},"causeChain":[],"httpStatus":200,"providerRequestId":"request-safe","providerErrors":[{"code":"ACCESS_DENIED","message":"original ADMIN_DENIED [REDACTED] [REDACTED]"}],"redactionApplied":true,"truncated":false}}
```

Records also assert original Partner code/details/request ID/causes, two warn attempts then final error for each mutation, local/invariant origins, no repeated provider body and absence of injected email/token/password sentinels. The test command emits safe JSON evidence. Local detailed logs: `/tmp/arch057-shopify003-{focused,postgres,typecheck,build,eslint,before-budget,before-sql,admin-validate}.log`.

Provenance: locked `npm ci`; Node **24.19.0**, npm **11.17.0**, installed Shared **3.1.0**; source start `b40775fd2f0b68ed39efc4b937c9ecec2cd607f7`; accepted SHOPIFY-002 commit `8561a870a8a5a407dca8b9da7f6239c69a140c90`; Database recursive gitlink **`8e74634ff92be9900f693c0c449ffce888e7d617`** unchanged. No schema/migration/dependency/public DTO/locale/pricing/identity/hash preimage/Background change.

Physical worktree isolation (launcher evidence): canonical root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-003`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-003`; both branches `task/ARCH-057-SHOPIFY-003`. Newly created, no shared/default checkout switched/mutated, no other task worktree reused. Parent and implementation remote-task fast-forward `not-needed`, origin/main `already-current`; recursive sync/update passed. Attempt 1 claim `8af5e5f18f2cac010614f09737ff1e968e955a10` pushed by launcher at `2026-11-04T08:23:14Z`.

Environment recovery: selected existing Colima Docker endpoint via `docker context inspect`, with `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock`; no host reconfiguration or shared resource pruning. Earlier discovery/mount failures are superseded by the real passing runs. Each helper cleaned up only its own clients/containers, including archived-baseline measurement. Final Docker inventory retains only the pre-existing developer containers. No skipped acceptance suite is presented as passed.

### Deviations

The required successful real-PostgreSQL zero-credit completion cannot be produced legally. A dedicated real constraint-rejection assertion records that conflict without disabling constraints, editing schema or fabricating transaction results. Task remains blocked, not ready for review; the final Work Item is intentionally unchecked.

### Assumptions

Synthetic provider ports model read-only lifecycle observations; no live charge/refund is authorized or executed. Existing identity generation and development-store pricing semantics remain unchanged. Actual SQL comparison explicitly excludes the provider credential query, whereas repository-method comparison includes its real configuration-reader invocation.

### Unresolved Issues

`moda_architect` must amend the zero-credit validation requirement to an attainable legal state/outcome, or coordinate a separately owned Database lifecycle-constraint change before successful execution of that branch can be required. This implementation does not choose either financial/lifecycle policy. No downstream task started.

### Architectural Concerns

Evidence: accepted Database migration `20260912000000_arch010_first_production_baseline/migration.sql` defines `RecoveryCreditPurchase_lifecycle_amounts`, requiring `currentAmount > 0` for WITHDRAWN (lines 1479–1484). Subsequent accepted migrations retain it. Management `reactivateRefund` checks WITHDRAWN before its zero-current branch, so no persisted row can reach `COMPLETED_NO_CREDITS` under these migrations. The real PostgreSQL rejection test names that exact constraint and verifies unchanged balances. Task Stop Condition requires an architect amendment when a schema/policy change is needed; no such change has been made here.

## Architect Review

### Review Status

**Changes Requested — Attempt 1, 2026-11-04.** The zero-credit validation blocker is resolved by the scoped amendment above. A reproduced privacy defect remains, so the task is not accepted or complete. Status is `ready`, executor/claimed_at are cleared and Attempt remains 1.

### Finding

**[P2] Exclude malformed Admin response text from both diagnostic messages.** In `app/routes/app/billing/recovery-credit-purchases/route.tsx:55–63`, the `response.json()` catch copies the native parser's message into the typed error and retains that same error as its logged cause. Node includes response text in SyntaxError messages. A synthetic body `SECRETXYZ` at both HTTP 200 and HTTP 503 appeared verbatim in actual Shared output in `error.message` and `causeChain[0].message`, with `redactionApplied: false`. This violates the task's raw-provider-data exclusion even though refund execution correctly fails closed.

Use a safe internal parse reason for the emitted top-level error and the accepted SHOPIFY-002 `diagnosticCause` facility for a sanitized parse diagnostic, retaining the original SyntaxError object as the propagated cause. Preserve safe HTTP status/request ID and truthful classification. Add actual-route/real-Shared tests for short full-body and long partial-body sentinels on both successful and non-2xx malformed responses; assert no mutation, original propagated cause, safe correlation and absence of body fragments. Keep source-error handling for other SDK/transport failures intact. No edit to the prerequisite diagnostics contract is needed.

### Reviewed Files and Architecture Conformance

- Implementation `fffbf30641544574b7de72c7829b85a9ea4fc0d4`, its 15-file delta from `b40775fd2f0b68ed39efc4b937c9ecec2cd607f7`, and parent submission `4821936db`.
- Both declared routes, request/management services, provider-context matcher, focused route/service/history fixtures, migrated purchase/refund suites and the canonical lifecycle constraint.
- The history context and separately bounded latest/completed summaries preserve the intended request-local design. Refund provider preflight precedes each transaction and the local authorization reads use the transaction client. Existing purchase replay, two provider/catalogue observations, current cycle validation, CAS and atomic persistence remain in place.
- Verified the official configured Admin 2026-07 `ShopPlan.partnerDevelopment` Boolean contract with the Shopify AI Toolkit: https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ShopPlan. No live provider operation was performed.
- No additional blocking implementation finding was identified in the reviewed scope. This is not acceptance while the privacy failure remains.

### Validation Reviewed

- Independent exact seven-file unit/route/render command: **106/106 passed**, no skips. Log: `/tmp/arch057-shopify003-review-units.log`.
- Independent exact two-file migrated PG17 integration command: **14/14 passed**, no skips. Real barriers/connections cover purchase/refund races, serialization retry, cycle change, rollback, provider-action fence and the zero-credit constraint rejection. Fixture cleanup completed. Log: `/tmp/arch057-shopify003-review-postgres.log`.
- History SQL measurements reproduced **9 SELECTs** and one synthetic provider call for each 1/5/20-row fixture; method budgets remain separately asserted by the unit suite. No SQL reduction or latency claim is inferred from fewer method calls.
- Two temporary actual-route malformed-response probes **both failed**, at HTTP 200 and 503. They used native Response parsing and the installed Shared logger; synthetic body text appeared twice in emitted records. Log: `/tmp/arch057-shopify003-review-probes.log`. The probe additions were removed and the original test file restored byte-for-byte.
- Node 24.19.0 and the existing locked toolchain were used. Reviewed the reported Prisma generation, typecheck, build and lint results; these were not independently rerun because the reproduced blocker already prevents acceptance. Implementation and parent whitespace checks passed.
- No implementation, schema, dependency, public DTO, pricing, identity or gitlink change was retained by the review.

### Follow-up and Dependencies

Fix the Admin-response diagnostic boundary and add the regression evidence within the existing allowlist. Reconcile the next Completion Report with the validation amendment and rerun affected suites and applicable gates. The defensive zero-credit unit case must remain clearly distinguished from the real migrated constraint proof; do not restore an impossible database success requirement or alter financial policy.

SHOPIFY-004 and SHOPIFY-011 were checked and remain `pending` because SHOPIFY-003 is not complete. No downstream task was claimed or executed. The developer explicitly authorized committing and pushing the review, validation amendment and architecture handoff on the parent task branch on 2026-11-04.

## Architect Dependency Reconciliation (2026-11-04)

ARCH-057-SHOPIFY-002 Attempt 3 is architect-accepted and complete at implementation `8561a870a8a5a407dca8b9da7f6239c69a140c90`. This task's only declared prerequisite is satisfied; status is `ready` for normal launcher preparation. Attempt remains 0 and executor/claimed_at remain empty. No implementation was claimed or started by this promotion. The launcher must retain the normal accepted-source integration and worktree gates.
