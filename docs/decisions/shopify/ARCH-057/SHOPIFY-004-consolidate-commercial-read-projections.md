---
id: ARCH-057-SHOPIFY-004
architecture_id: ARCH-057
title: Consolidate commercial read projections
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-057-SHOPIFY-001
- ARCH-057-SHOPIFY-002
- ARCH-057-SHOPIFY-003
enables:
- ARCH-057-SHOPIFY-011
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-004: Consolidate commercial read projections

## Architecture

Architecture ID: `ARCH-057`.

Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`.

Coordinator: `moda_architect`.

Mandatory execution, diagnostic, provenance and validation contract: `docs/architecture/ARCH-057/task-contract.md`. This is a **portable definition, defined but not materialised**. No execution claim, branches, worktrees, commits or implementation acceptance are asserted. Its named dependencies are not Complete, so the task is Pending.

## Objective

Make billing, promotion and usage pages derive their presentation from one trusted request context and one set of required read inputs, removing repeated queries and unused work while preserving current access, lifecycle, accounting and merchant output.

## Context

Review F08 traces 17 repository methods in a healthy billing-options GET after Shop resolution. F14 finds repeated promotion context reads, unbounded eligible-offer loading and separate usage count/sum queries for the same predicate. F16 records silent capacity/provider/usage fallbacks. SHOPIFY-001 supplies scalar request facts; SHOPIFY-002 makes provider evidence trustworthy; SHOPIFY-003 owns mutation and history behavior. This task consumes those boundaries and changes read composition.

Read facts may be gathered in parallel but are not an atomic database snapshot. A page never grants credits or authorizes a later mutation from its cached presentation. The mutation services retain fresh transaction-bound admission.

## Scope

All paths are relative to `moda-interact`. The exact route filenames are significant: billing select and usage are `.jsx`.

### Existing files to modify

| Path | Exact responsibility |
|---|---|
| `app/routes/app/billing/options/route.tsx` | Loader uses one commercial presentation composition; preserve SHOPIFY-003 action ownership and all current fields/denied redirects |
| `app/routes/app/billing/select/route.jsx` | Consume context and determine FROZEN from scalar status without loading balances, promotions or catalogue |
| `app/routes/app/home/route.jsx` | Reuse scalar Subscription and already-loaded pricing facts for capacity; preserve onboarding/legacy redirect/recovery overview branches |
| `app/services/billing/billing.service.ts` | Expose the two chosen presentation methods and remove superseded page-only read facade methods after migrating their named callers |
| `app/services/billing/merchant-billing-read.service.ts` | Extract pure top-up/balance projection from supplied facts, remove unused lifetime `usageEvent.aggregate`/`usageQuantity`, preserve output predicates |
| `app/services/billing/merchant-recovery-capacity-read.service.ts` | Extract pure capacity projection from supplied facts; no hidden Subscription/counter rereads in the page path |
| `app/services/billing/subscription-read.service.ts` | Extract pure provider-to-merchant mapping supplied with already-loaded operational plans; preserve existing standalone read APIs used outside page composition |
| `app/services/billing/billing-plan-resolution.service.ts` | Add a bounded presentation-only catalogue batch reader; do not change mutation materialization or the two new-purchase catalogue observations |
| `app/services/billing/billing.types.ts` | Type the narrow presentation inputs/result and pure projections; preserve merchant DTOs except the unconsumed internal `usageQuantity` |
| `app/services/merchant-pricing/merchant-pricing.server.js` | Export/reuse the existing pure top-up configuration derivation from known pricing usage events; preserve catalogue validation/localization |
| `app/routes/app/promotions/route.tsx` | Consume context and the bounded single-context page reader; preserve selection action authorization and existing form/results |
| `app/services/promotions/promotion.service.ts` | Single read context input, database-paged eligible offers, shared predicates, unchanged mutation admission with explicit failure ownership |
| `app/routes/app/usage/route.jsx` | Consume context and log true read failures before existing fallback; cursor validation remains normal control flow |
| `app/services/usage/history.server.ts` | Combine identical-filter count and quantity sum into one aggregate; preserve bounded source query and cursor/tenant rules |
| `tests/unit/services/billing/merchant-billing-read.service.test.ts` | Pure projection parity and failure regression |
| `tests/unit/services/billing/merchant-recovery-capacity-read.service.test.ts` | Capacity invariants across all existing lifecycle/balance branches |
| `tests/unit/services/billing/subscription-read.service.test.ts` | Pure mapping and unchanged standalone read API behavior |
| `tests/unit/services/billing/billing-plan-resolution.service.test.ts` | Bounded presentation batch read; unchanged mutation materialization |
| `tests/unit/services/billing.service.test.ts` | Updated facade composition without constructor side effects |
| `tests/unit/home-route.test.ts` | Existing onboarding/setup/legacy-link branches and shared scalar/capacity use |
| `tests/unit/billing-ui.test.ts` | Unchanged select/options status behavior |
| `tests/unit/merchant-pricing-usage-overview.test.jsx` | Unchanged localized catalogue/usage rendering |
| `tests/unit/services/promotion.service.test.ts` | Shared page predicates, pagination and unchanged selection rules |
| `tests/unit/routes/promotion-route.test.ts` | Bounded offers/history DTO and selection action regression |
| `tests/unit/usage-route.test.ts` | Combined aggregate, safe cursor/tenant behavior and real read-error diagnostics |
| `tests/integration/promotion-selection.concurrency.integration.test.ts` | Use pgvector PG17 with forward migrations; reconcile same-campaign expectation with existing policy and exercise bounded translated-offer pages |

### New files

| Path | Purpose |
|---|---|
| `app/services/billing/merchant-billing-presentation.server.ts` | One local composition owner for commercial/capacity/top-up read inputs and partial-failure boundaries |
| `tests/unit/services/billing/merchant-billing-presentation.test.ts` | Real orchestration with controlled ports, projection parity and original Shared output |
| `tests/unit/commercial-read-budget.test.ts` | Deterministic repository/provider counts for options, select, home capacity, promotions and usage |
| `tests/unit/routes/billing-options-loader.test.ts` | Actual loader access, output, outage and no-write behavior |
| `tests/fixtures/commercial-read-context.ts` | Small scalar context/plan/period/catalogue fixtures reused by the new suites |

New test/helper files each stay below 300 lines. Use existing `npm test` with exact paths, without a new package script/dependency. This task may not modify prerequisite request-context/provider-diagnostics implementations to make its own tests pass.

## Out of Scope

No subscription sync/materialization during a GET, process cache, new middleware framework, generic repository layer, schema/index/migration, arbitrary truncation of business results, purchase/refund policy, cash movement, queue/outbox, privacy/retention or notice-durability change. No architecture ID in new runtime names. This read-composition task does not change billing identity generation. SHOPIFY-012 owns the later canonical development namespace replacement; no historical-identity compatibility is required.

Do not redesign the merchant catalogue or invent a new balance. Lifetime Free, purchased, promotional and current paid-period capacity retain their distinct rules. Do not change the callback/milestone/category lifecycle or the accepted post-contract behavior. Do not edit another task or `_index.md`.

## Requirements

### R1. Consume the existing scalar context

Every named route consumes `getMerchantRequestContext({ request, context })` and retains its current independent Shop/surface authorization. Preserve active-only filtering where the previous guard used `getSubscription`; use the full scalar projection where it used `getSubscriptionProjection`. In select, check the unfiltered scalar FROZEN status to retain its current forbidden behavior before redirecting to pricing.

SHOPIFY-001's `readSubscription()` returns a full scalar `Subscription | null`, not plan/period relations. Do not issue another `subscription.findUnique` merely to attach those relations. Fetch required operational plans, current period/counters and other rows explicitly by the trusted scalar IDs. Related rows must match Shop/subscription/plan identity exactly before projection; mismatched/missing related data remains unavailable. The scalar context is request-local, not a transaction snapshot or mutation authorization.

### R2. One billing presentation composition

Add `MerchantBillingPresentationReadService` in the new source module, constructed with existing provider/database dependencies and no constructor I/O. Its `readOptions(input)` returns the existing commercial, capacity and top-up results. Its `readHome(input)` performs only local reads and returns the existing Home subscription summary and capacity DTO. BillingService delegates through the named methods in Interfaces / Contracts.

For options, collect the following each at most once:

1. One provider active-subscription observation, including its one current credential read; reuse it for commercial mapping and top-up eligibility.
2. One `billingPlan.findMany` for distinct referenced current/pending local IDs and observed current/pending provider handles. Attach local plans by their scalar foreign keys; provider mapping does not replace local authority.
3. One current `billingPeriod` read with its included-credit counter, when a period ID exists, scoped/validated against the trusted Shop and Subscription.
4. One `shopEntitlementCounter.findMany` restricted to the two required lifetime-Free/purchased counter kinds.
5. One selected-promotion read with grant/campaign facts.
6. One `merchantPricingPlan.findMany` for the distinct current local/live handles, including their ordered usage events/tiers. At most two plan handles are needed. Keep separate rows when local/live handles differ.
7. The existing latest-purchase read and existing unresolved-purchases read with their tenant/provider/evidence predicates.

Build pure projections from those returned inputs. The plan/counter/promotion/pricing readers may run in parallel where dependencies permit; no second service secretly reloads Shop, Subscription, counters or catalogue. Keep the existing unresolved-purchase semantics; do not impose an arbitrary limit that can hide an unresolved event and re-enable purchase. This task does not redesign that history surface.

Remove the unconsumed lifetime `usageEvent.aggregate` and its `usageQuantity` field from internal merchant billing state. No current production consumer may require it. Preserve all rendered commercial/capacity/top-up DTO fields, paid-cycle validation, mapping status, unsupported/transition cases, development-price display, cancellation/post-contract behavior and separate balance sources.

The healthy active Paid/current-cycle options branch has **eight repository data calls after a supplied Shop/scalar Subscription context**, including the provider credential: operational-plan batch, period/counter, two-counter batch, promotion selection, pricing batch, latest purchase, unresolved purchases, credential. It makes one Partner request and no writes. Counts exclude context acquisition, parent support reads, Prisma relation expansion and SDK work. A pending provider plan remains inside the same bounded plan batch, not another query.

### R3. Local capacity and frozen checks stay narrow

`readHome` accepts the same trusted Shop/scalar Subscription and a fixed `now`, obtains the required local related rows once, and never calls the provider. Its one operational-plan batch includes both current and pending plan IDs. Return the existing Home subscription summary (`status`, `planHandle`, `planName`, `cancelAtEndOfCycle`, `currentPeriodEnd`, `pendingPlan.name/effectiveAt`) from those plan rows and scalar fields; do not drop pending-plan names or reread Subscription to obtain them. Preserve the existing observed-handle fallback when a current plan is absent.

Home also passes its already-loaded active pricing catalogue's minimal `{shopifyPlanHandle, usageEvents[].creditsGrantedPerUnit}` facts. If the local handle is present, derive top-up enabled/credits-per-pack from that entry without another catalogue read. If it is absent, retain an exact local-handle lookup; do not infer that an inactive/unlisted catalogue plan has no configuration. Missing/NO_CONTRACT projections keep their existing no-top-up rules. A failed capacity-specific read logs its original error and returns `capacity: null`, preserving the successfully obtained subscription summary and the existing Home fallback.

For a healthy Paid Home fixture with a catalogue match, local presentation adds at most four reads: current/pending operational-plan batch, current period/counter, the two-counter batch, selected promotion. A valid Free fixture without a current period skips the period read. Invoke this composition only after existing Home onboarding/setup/legacy-link early returns; those branches require only scalar subscription evidence, not new capacity work. Preserve recovery overview and pending-recovery behavior.

Billing-select performs no capacity, counter, promotion, catalogue or provider work after obtaining context; full scalar status answers its FROZEN check. Ordinary projection/getters remain read-only.

### R4. Page promotions at the database using one trusted context

Introduce `getMerchantPromotionPage(input, database?)` in the existing promotion service. It receives trusted `{shopId, shopStatus, subscriptionStatus, planId}` plus locale, pages and a single `now`; the route derives those facts from its scalar context. The page reader does not reread Shop or Subscription. Its existing pure eligibility/history functions remain the projection authority.

Use one exact eligible-offer predicate for both `promotionCampaign.count` and the bounded `findMany`: ACTIVE, started, not expired, GLOBAL/eligible PLAN/this SHOP scope, and a translation for the requested catalogue locale. The canonical campaign/locale uniqueness makes that equivalent to the existing one-translation filter. Do not count untranslated offers and then filter them out after pagination.

Count first, normalize/clamp the offer page, then query `skip`/`take: 6` using `expiresAt asc, createdAt desc, id asc`. Preserve the existing returned pagination fields and selected-offer visibility behavior. Retain the current selection read and history count/page (six history entries and one latest reopen event). This gives **five page-data repository calls after supplied context**, independent of catalogue size: offer count/page, current selection, history count/page. No full-offer scan or per-row source/context call is permitted.

The selection action continues to call `selectPromotionOffer`, whose fresh Serializable transaction context/campaign/current-selection reads and bounded P2034 retries remain authoritative. Keep the current rule: an unexpired selection blocks a new selection, including another selection of the same campaign. Correct the existing integration expectation that both same-campaign calls succeed; require one accepted selection, one normal `ACTIVE_PROMOTION_ALREADY_SELECTED` outcome and `selectionCount=1`. Do not weaken the service to satisfy the stale test. Retain same-Shop grant reuse, quantity accounting, expiry/reopen and targeting behavior.

### R5. Consolidate usage totals and retain bounded source resolution

Replace the separate identical-predicate `usageEvent.count` and sum with one `usageEvent.aggregate({ where, _count: { _all: true }, _sum: { quantity: true } })`. Derive the same total and quantity fields, with the same zero/null normalization. Do not add a second aggregate in the route.

Preserve the selected-period tenant predicate, current/past filters, validated signed-integer offset, maximum 100 usage rows, 26-row keyset period fetch showing 25, stable cursor boundaries and the single bounded raw source query. Do not replace its three-branch source join with per-row service lookups. With a selected period the reader uses four Prisma methods plus the existing raw query when source IDs are nonempty; with no selected period it uses two reads and no source query.

### R6. Preserve degraded presentation and original diagnostics

Provider failure must still allow an authorized page to present its durable shell and any successfully read local capacity. The provider adapter from SHOPIFY-002 owns the original upstream diagnostic; the presentation boundary does not repeat the body. A failed local capacity/top-up/usage/promotion read is logged through Shared before the existing unavailable/failure outcome. Do not turn a provider outage into NO_CONTRACT or a failed DB read into zero available credits.

Replace message-only truncation or empty catches with original safe `error`, actual Prisma code and available cause fields under the common contract. The orchestration keeps one owner for a shared failing read, even when two derived projections become unavailable. Normal invalid cursors, denied surfaces and locked/ineligible promotions remain normal control flow.

| Injection / owner | Required actual Shared output | Required result |
|---|---|---|
| Provider error, SHOPIFY-002 adapter | Original safe upstream source/code/message/cause/status/request ID; no second provider body | Durable shell/local successes preserved; live verification unavailable |
| Plan/period/counter/promotion/pricing DB read failure, presentation owner | Actual database error/code/cause, Shop and failed stage | Affected projection unavailable, no fabricated balance or entitlement |
| Top-up pure validation/invariant failure, presentation owner | Actual internal error/cause and classification, no invented provider details | Existing unavailable presentation, no writes |
| Home capacity rejects, Home/presentation owning boundary | Original error/code/cause before existing nullable fallback | Existing overview and page behavior preserved |
| Promotion page count/page/history failure, page reader | Actual database error/code/cause and failed read | Existing route failure, no silently empty catalogue |
| Promotion P2034 retry/exhaustion, selection service | Actual retry error at warn; original final error/code/cause at error | Same bounded retry; preserve typed `PROMOTION_SELECTION_UNAVAILABLE` with original cause |
| Usage data/source query fails, usage route/service owner | Actual database/driver error/code/cause before fallback | Existing `error: read` UI result |
| Invalid usage cursor, normal promotion denial or denied access | No fabricated operational/provider error | Existing safe cursor/message/redirect outcome |
| Shared sink throws | Real Shared isolation assertion | Identical rendering/fallback, selection rollback/retry and authorization |

Keep server diagnostics out of merchant JSON and locale text. No new visible keys are planned; if implementation requires one, stop for an explicit scope/copy amendment instead of changing only English.

## Work Items

- [ ] Consume the accepted request context in the declared page entrypoints.
- [ ] Implement one typed billing presentation collector and pure commercial/capacity/top-up projections.
- [ ] Batch required counters/plans/catalogue and remove unused lifetime usage aggregation.
- [ ] Reuse Home pricing facts and replace select's full-capacity read with scalar status.
- [ ] Implement exact database-paged translated promotion offers and shared read context.
- [ ] Preserve promotion mutation admission and repair its stale concurrency expectation.
- [ ] Combine usage count/sum without changing bounds or source resolution.
- [ ] Complete branch budgets, actual Shared failure assertions and the required promotion PostgreSQL evidence.

## Interfaces / Contracts

Consumes SHOPIFY-001's `MerchantRequestContext`. Related data stays in this domain owner. Consumes SHOPIFY-002's provider parser/error ownership and SHOPIFY-003's service-owned purchase action; it never restores removed prevalidation or reuses a GET observation for mutation.

Add these server-only facade methods using actual Prisma/domain types:

```ts
type MerchantBillingReadInput = Readonly<{
  shop: Shop;
  subscription: Subscription | null;
  now: Date;
}>;

readMerchantBillingPresentation(input: MerchantBillingReadInput): Promise<{
  commercial: MerchantShopifySubscriptionState | null;
  capacity: MerchantRecoveryCapacityState | null;
  topUp: MerchantBillingState | null;
}>;

readMerchantHomeBillingPresentation(
  input: MerchantBillingReadInput & {
    pricingCatalogue?: readonly {
      shopifyPlanHandle: string;
      usageEvents: readonly { creditsGrantedPerUnit: number }[];
    }[];
  },
): Promise<{
  subscription: MerchantHomeSubscriptionSummary | null;
  capacity: MerchantRecoveryCapacityState | null;
}>;
```

`MerchantBillingState` is the existing rendered merchant billing result minus its unconsumed internal `usageQuantity`; define an explicit source-owned type rather than `any`. `MerchantHomeSubscriptionSummary` is the exact existing Home summary enumerated in R3, including nullable pending plan and dates serialized as before. The result's `commercial: null` denotes failed verification; valid explicit provider absence remains the existing `NO_ACTIVE_SUBSCRIPTION` result. Capacity/top-up null denotes the existing failed/unavailable read boundary, never a new durable state.

Migrate current page callers and remove the superseded page-only `getMerchantBillingState` / `getMerchantRecoveryCapacityState` facade paths rather than retain parallel I/O implementations. Keep the existing general subscription getters and provider-verification APIs used by activation/mutations. Pure selectors remain in their existing domain files and accept prepared facts; they do not own caches or network calls.

The promotion page input is `{shopId, shopStatus, subscriptionStatus, planId, locale, offerPage, historyPage, now}`. Its output is the current route's `{offers, offersPagination, promotionSelection, history}` shape. New page-read context is never accepted by `selectPromotionOffer` as mutation authority.

## Dependencies

- ARCH-057-SHOPIFY-001 — accepted request-context and first-consumer baseline.
- ARCH-057-SHOPIFY-002 — accepted provider parsing/diagnostic and activation baseline.
- ARCH-057-SHOPIFY-003 — accepted purchase action/history/refund baseline before the shared options route is edited again.

All must be Complete and architect-accepted before claim. The explicit list records overlap ownership even where dependencies are transitive.

## Enables

- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [ ] Options uses eight repository data calls and one Partner request in the supplied-context healthy Paid fixture, with no repeated Shop/Subscription/counter/catalogue reads and no writes.
- [ ] Local/live plan differences, pending selection, Free/Paid/TRIALING/FROZEN/NO_CONTRACT/post-contract/unmapped/transition/error states retain current DTO and entitlement behavior.
- [ ] Select uses scalar FROZEN status with no capacity/catalogue/provider work; Home retains current and pending plan names from one plan batch, reuses matching pricing facts and keeps all early-return/legacy-link branches.
- [ ] Promotion pages use five page-data calls, return at most six correctly translated offers, and have count/page predicates and stable ordering in agreement.
- [ ] Promotion mutation policy and grant/accounting remain unchanged; real same-campaign concurrency yields one selection rather than artificially incrementing twice.
- [ ] Usage uses one count/sum aggregate and retains its tenant, cursor, offset, page and source-query bounds.
- [ ] Every named failure preserves actual safe Shared message/code/cause output; fallback and sink-failure behavior remain correct with no provider-body duplication or secret/PII leakage.
- [ ] No schema, package, mutation freshness, locale/copy, hash identity, notification/privacy policy or cross-repository behavior changed.

## Validation

Run from the prepared `moda-interact` implementation worktree under the mandatory contract.

- [ ] `npm run prisma:generate`
- [ ] `npm test -- tests/unit/services/billing/merchant-billing-presentation.test.ts tests/unit/commercial-read-budget.test.ts tests/unit/routes/billing-options-loader.test.ts tests/unit/services/billing/merchant-billing-read.service.test.ts tests/unit/services/billing/merchant-recovery-capacity-read.service.test.ts tests/unit/services/billing/subscription-read.service.test.ts tests/unit/services/billing/billing-plan-resolution.service.test.ts tests/unit/services/billing.service.test.ts tests/unit/home-route.test.ts tests/unit/billing-ui.test.ts tests/unit/merchant-pricing-usage-overview.test.jsx tests/unit/services/promotion.service.test.ts tests/unit/routes/promotion-route.test.ts tests/unit/usage-route.test.ts`
- [ ] `npm test -- tests/unit/routes/billing-options-action.test.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts` — prerequisite mutation freshness and action ownership remain intact.
- [ ] `MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/promotion-selection.concurrency.integration.test.ts`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `npx --no-install eslint app/services/billing app/services/promotions/promotion.service.ts app/services/merchant-pricing/merchant-pricing.server.js app/services/usage/history.server.ts app/routes/app/billing/options/route.tsx app/routes/app/billing/select/route.jsx app/routes/app/home/route.jsx app/routes/app/promotions/route.tsx app/routes/app/usage/route.jsx tests/unit/services/billing/merchant-billing-presentation.test.ts tests/unit/commercial-read-budget.test.ts tests/unit/routes/billing-options-loader.test.ts tests/fixtures/commercial-read-context.ts tests/integration/promotion-selection.concurrency.integration.test.ts` and focused lint of changed existing tests.
- [ ] `git diff --check`

Budget tests execute the actual route/service composition with controlled Prisma/provider ports; they do not inspect source text alone. Fix fixture time and use identical before/after fixture branches. Record context acquisition separately, including whether the parent already seeded scalar rows. Count physical SQL only where collected, separately from method budgets and relation expansion; do not claim latency/capacity from these tests.

Required projection fixtures include current/local handle mismatch, a pending live handle, a missing/null cycle, inactive or missing plan, malformed related-row identity, Free/Paid/trial/frozen/post-contract capacity, missing counters and provider outage with a usable local shell. Home fixtures include distinct current/pending plan names and effective date, observed-handle fallback, and retained summary when a capacity-only read fails. Promotion fixtures include more than two pages, untranslated rows interspersed with eligible rows, tied timestamps, plan/Shop targets, unexpired same-campaign selection and expired/reopened selection. Usage fixtures include empty selection, 100 rows, invalid/cross-Shop cursor, large bounded offset and all supported source types.

The promotion integration suite must execute on task-owned `pgvector/pgvector:pg17` using forward migrations, real separate connections and explicit race barriers. Extend it to prove translated count/page agreement using actual SQL. Default skips and a database image missing vector support do not pass. Record actual Shared output, database cases, warnings and owned-resource cleanup.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation pass, set this task to review, return its Completion Report to `moda_architect` and stop. Do not mark it Complete or begin follow-on work.

Stop for an architect amendment if a prerequisite context/DTO differs, removing `usageQuantity` reveals a real production consumer, bounded promotion translation semantics cannot be preserved with the existing uniqueness contract, an identity/schema/policy change is required, a new visible locale key is needed, or required PostgreSQL validation cannot execute. Do not add a cache, index or new framework to reach a method-count target.

## Implementation Notes

One request-local collector plus existing pure domain calculations is the chosen implementation. Do not assemble three differently timed Subscription snapshots and call them coherent. Do not claim the replacement inputs are transactionally atomic either: identity/cycle predicates and unavailable states still matter, and mutation services continue to reread current state.

The method budgets are branch-specific upper bounds and preserve legitimate checks. The unchanged purchase-read queries remain separate because latest receipt and all unresolved event summaries serve different UI purposes. The selected promotion mutation test must reflect accepted service policy, not invent a new policy to simplify concurrency assertions.

## Completion Report

### Status

Not Started. Defined but not materialised.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact commands, branch fixtures/results, source/build/dependency provenance, context/domain/provider/SQL counts, actual Shared-log evidence and owned-container cleanup.

### Deviations

None.

### Assumptions

All three dependencies are integrated and architect-accepted before claim. No source-probe or unit timing is treated as a production performance measurement.

### Unresolved Issues

Implementation and required validation remain outstanding. Notice durability, privacy/retention and Background category activation remain outside this outcome.

### Architectural Concerns

Return changed context, presentation, lifecycle, financial, schema, identity or ownership contracts to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only; no implementation accepted.

### Reviewed Files

Definition and named latest-snapshot touchpoints.

### Validation Reviewed

Definition checks only. Implementation evidence is outstanding.

### Architecture Conformance

To be assessed from actual projections, call budgets, database policy evidence and original-error output.

### Follow-up

Return for review; terminal validation follows the parent dependency map rather than starting automatically.
