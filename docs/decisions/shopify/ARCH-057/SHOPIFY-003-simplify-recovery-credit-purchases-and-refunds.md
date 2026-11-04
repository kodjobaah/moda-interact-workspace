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
claimed_at: 2026-11-04T08:23:14Z
attempt: 1
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

Mandatory execution, diagnostic, provenance and validation contract: `docs/architecture/ARCH-057/task-contract.md`. This is a **portable definition, defined but not materialised**. No implementation claim, worktree, branch, commit or acceptance is asserted. SHOPIFY-002 is not Complete, so this task is Pending.

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

Keep current unique-conflict receipt recovery, including same-Shop/provider validation and returned current purchase outcome. A replay may not create a second refund or balance hold. Preserve reactivation's transaction, provider-action fence, zero-credit completion case and three-entity CAS; no provider read is required for reactivation. Batches remain sequential, bounded and individually transactional rather than holding one transaction across provider calls.

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

## Work Items

- [ ] Consume request context in the declared route handlers while retaining independent access checks.
- [ ] Remove duplicate purchase-route capacity/provider prevalidation and preserve service replay/admission.
- [ ] Implement the small provider-observation/pure-matching module and one-context history projection.
- [ ] Replace unbounded nested refunds with the two bounded summary reads.
- [ ] Move each new-refund provider preflight before its write transaction and use only transaction-local current state for admission.
- [ ] Retain replay, CAS, batch and reactivation behaviour; leave namespace replacement to SHOPIFY-012.
- [ ] Complete actual Shared-output assertions, deterministic call budgets and both migrated PostgreSQL suites.

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

- [ ] Authorized existing purchase replay makes no provider/catalogue/capacity calls and retains its existing receipt; cross-Shop/provider replay is denied.
- [ ] A new purchase still makes two fresh provider lifecycle observations and two catalogue observations outside its write transaction, with final local revalidation inside it.
- [ ] Eligible 1/5/20-row history pages use six repository methods and one provider call; noneligible/empty/clamped branches meet the specified budgets.
- [ ] Latest and completed refund summaries are independently correct and bounded, including an older completion behind many newer cancellations and equal-timestamp ordering.
- [ ] Refund HTTP/credential/root-client context reads never execute while a write transaction is open.
- [ ] Refund/refund, refund/reservation and reactivation interleavings preserve one durable hold, nonnegative balances, versions and provider-action fences on real PostgreSQL.
- [ ] Purchase same-ID and same-offer races preserve one admissible durable request and atomic UsageEvent/Purchase/BillingOperation persistence.
- [ ] Every named operational failure retains original safe Shared output and cause; provider text is not duplicated and secret/PII sentinels do not appear.
- [ ] No schema, dependency, public DTO, locale, pricing policy, hash preimage, identity or Background change occurred.

## Validation

Run from the prepared `moda-interact` implementation worktree under the mandatory execution contract.

- [ ] `npm run prisma:generate`
- [ ] `npm test -- tests/unit/services/recovery-credit-purchase-management.service.test.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts tests/unit/recovery-credit-history-budget.test.ts tests/unit/routes/recovery-credit-purchases.test.ts tests/unit/routes/billing-options-action.test.ts tests/unit/recovery-credit-purchase-manager.test.tsx tests/unit/billing-purchase-hub.test.tsx`
- [ ] `MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/recovery-credit-refunds.postgres.integration.test.ts tests/integration/recovery-credit-purchases.postgres.integration.test.ts`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `npx --no-install eslint app/services/billing/recovery-credit-purchase-management.service.ts app/services/billing/recovery-credit-purchase-request.service.ts app/services/billing/recovery-credit-provider-context.server.ts app/routes/app/billing/recovery-credit-purchases/route.tsx app/routes/app/billing/options/route.tsx tests/unit/recovery-credit-history-budget.test.ts tests/unit/routes/recovery-credit-purchases.test.ts tests/unit/routes/billing-options-action.test.ts tests/integration/recovery-credit-refunds.postgres.integration.test.ts tests/integration/recovery-credit-purchases.postgres.integration.test.ts tests/fixtures/recovery-credit-refunds.ts tests/fixtures/recovery-credit-purchases.ts` and focused lint of changed existing tests.
- [ ] `git diff --check`

Both PostgreSQL files must run against task-owned `pgvector/pgvector:pg17` containers with all accepted forward migrations, using the prerequisite helper. Separate real Prisma connections and explicit barriers control races; provider ports are synthetic. Do not use a mocked transaction, fabricated SQL result or timing sleep as database proof.

Required database cases: two same-ID new purchases; different IDs competing for the same unresolved offer; billing-cycle change after provider observations but before final admission; rollback after one of the three purchase writes; two refund requests; reservation/version change before refund CAS; refund-versus-reactivation; reactivation after provider action has begun; zero-credit completion; failure after refund creation before counter CAS. Assert durable row counts, request identities, versions, reserved/refunding/current quantities and no partial writes.

Record same-fixture before/after method/provider counts and actual emitted SQL separately. The expected new refund preflight adds a deliberate read; the acceptance goal is a correct short transaction, not fewer reads at any cost. Include actual Shared JSON evidence, unavailable validation, warnings and owned-resource cleanup in the Completion Report.

## Stop Condition

When the defined work, acceptance criteria and required validation pass, set this task to review, return its Completion Report to `moda_architect` and stop. Do not mark it Complete or start SHOPIFY-004.

Stop for an architect amendment if dependency interfaces differ, an existing policy would have to change, a schema/Shared/Background edit is required, safe diagnostics cannot preserve source evidence, identity bytes would change, or real PostgreSQL validation cannot execute. Do not substitute mocks or a skipped suite for required database evidence.

## Implementation Notes

The history optimization is request-local reuse; refund admission deliberately reads again. The history summary design uses one bounded extra ORM call rather than specialized raw SQL. It yields six constant calls instead of the review's unbounded-history five-call hypothetical; record that distinction honestly.

Use pure matching to keep history and mutation predicates coherent without making a presentation cache authoritative. Keep existing per-purchase transactions and replay recovery. Do not batch independent mutations into a transaction spanning external work. The newer task names exist only in task/test metadata, not runtime names or events.

## Completion Report

### Status

Not Started. Defined but not materialised.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record actual commands/results, source/build/dependency provenance, method/SQL/provider counts, race/accounting cases, emitted Shared-log assertions and owned-resource cleanup.

### Deviations

None.

### Assumptions

The launcher verifies SHOPIFY-002 and its prerequisite are integrated and accepted before claim. Controlled provider fixtures never execute live financial operations.

### Unresolved Issues

Implementation and validation remain outstanding. Privacy/retention and notice durability are not decided by this task.

### Architectural Concerns

Return changes to financial policy, database/schema ownership, retry identity, provider contract or cross-repository mutation semantics to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only; no implementation accepted.

### Reviewed Files

Definition and the named latest-snapshot touchpoints.

### Validation Reviewed

Definition checks only. Implementation evidence is outstanding.

### Architecture Conformance

To be assessed from actual source, unchanged identities, transaction/race results and original-error output.

### Follow-up

Return for review; do not begin enabled work automatically.

## Architect Dependency Reconciliation (2026-11-04)

ARCH-057-SHOPIFY-002 Attempt 3 is architect-accepted and complete at implementation `8561a870a8a5a407dca8b9da7f6239c69a140c90`. This task's only declared prerequisite is satisfied; status is `ready` for normal launcher preparation. Attempt remains 0 and executor/claimed_at remain empty. No implementation was claimed or started by this promotion. The launcher must retain the normal accepted-source integration and worktree gates.
