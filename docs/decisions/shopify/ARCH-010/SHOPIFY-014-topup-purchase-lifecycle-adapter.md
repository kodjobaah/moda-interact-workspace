---
id: ARCH-010-SHOPIFY-014
architecture_id: ARCH-010
title: Implement merchant recovery top-up lifecycle adapter and production panel
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 54
executor: copilot
claimed_at: 2026-09-14T05:44:18Z
attempt: 2
depends_on:
- ARCH-010-SHOPIFY-013
- ARCH-010-SHOPIFY-007
- ARCH-007-SHOPIFY-004
- ARCH-010-SHOPIFY-018
- ARCH-010-DATABASE-014
enables:
- ARCH-010-SHOPIFY-012
- ARCH-010-BACKGROUND-021
created: 2026-09-11
updated: 2026-09-14
---

# ARCH-010-SHOPIFY-014: Implement merchant recovery top-up lifecycle adapter and production panel

## Consolidation

This task absorbs superseded `ARCH-010-SHOPIFY-010`. Do not implement SHOPIFY-010 separately.

## Objective

Implement the merchant-safe top-up read/action adapter and production `TopUpPurchasePanel` while creating every new `RecoveryCreditPurchase` in the final first-production `REQUESTED` lifecycle with immutable purchase-time commercial context.

Moda uses Shopify App Pricing/App Events. Do not introduce Shopify Billing API one-time purchases.

## Inspect before editing

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/providers/shopify-billing.provider.ts
app/routes/app/billing/route.tsx
app/routes/app/billing/options/route.tsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/billing-purchase.mock.js
tests/unit/services/billing.service.test.ts
tests/unit/services/shopify-billing.provider.test.ts
tests/unit/billing-ui.test.ts
package.json
```

Read implemented/current contracts:

```text
ARCH-010-DATABASE-014
ARCH-010-SHOPIFY-007
ARCH-010-SHOPIFY-013
ARCH-010-SHOPIFY-018
```

## Canonical purchase lifecycle

Use exactly:

```text
REQUESTED
ACTIVE
COMPLETED
WITHDRAWN
REFUNDED
```

This task creates only `REQUESTED` purchases. BACKGROUND-021 is the sole owner of provider-confirmed `REQUESTED -> ACTIVE` activation.

Hard lifecycle:

```text
merchant requests one pack
  -> resolve one exact verified local/provider billing context
  -> snapshot exact provider subscription/cycle/meter and BEFORE usage/cost evidence
  -> create/reuse RecoveryCreditPurchase(REQUESTED, currentAmount=0, reservedAmount=0)
  -> create/reuse UsageEvent(RECOVERY_CREDIT_PACK_PURCHASE, quantity=1, PENDING)
  -> HTTP request returns without direct provider publication
  -> Background publishes/reconciles App Event
  -> BACKGROUND-021 proves exact provider AFTER quantity/cost/currency
  -> immutable purchase monetary basis frozen
  -> currentAmount = creditsGranted
  -> REQUESTED -> ACTIVE exactly once
```

Forbidden:

```text
appPurchaseOneTimeCreate
appSubscriptionCreate
billing.request
appUsageRecordCreate
client-supplied monetary authority
direct App Events network publication from merchant HTTP action
HTTP-side ACTIVE transition
```

## Server read model

Expose one merchant-safe top-up state using current repository types. At minimum include:

```ts
{
  configured: boolean;
  purchaseEligible: boolean;
  unavailableReason: string | null;
  creditsPerPack: number | null;
  purchasedCreditsAvailable: number;
  shopifyPackMeter: {
    handle: string;
    description: string | null;
    currency: string | null;
    price: /* exact SHOPIFY-013 provider price shape */;
    currentQuantity: number | null;
    currentCostAmount: string | null;
    currentCostCurrency: string | null;
  } | null;
  latestPurchase: {
    id: string;
    status: "REQUESTED" | "ACTIVE" | "COMPLETED" | "WITHDRAWN" | "REFUNDED";
    creditsGranted: number;
    currentAmount: number;
    reservedAmount: number;
    createdAt: string;
    activatedAt: string | null;
    usageReportState: string;
  } | null;
}
```

Provider `NEEDS_ATTENTION`/retry state is exposed through `usageReportState` or a bounded derived unavailable/attention field; do not invent a sixth purchase lifecycle state.

## Authority

Shopify provider state is authority for:

- current provider subscription identity/current handle;
- exact current provider billing cycle;
- exact configured recovery-pack usage item;
- provider price/tier shape;
- current provider usage quantity/cost/currency.

Moda/PostgreSQL is authority for:

- `recoveryCreditsPerPack`;
- durable purchase lifecycle/balances;
- local BillingPeriod/plan mapping;
- UsageEvent report state;
- local cycle phase.

Current local BillingPlan monetary values are never provider purchase/refund truth.

## Purchase eligibility

At mutation time both Free and Paid merchants require:

```text
Shop ACTIVE
executable current subscription policy
provider current plan == mapped current BillingPlan handle
recovery-credit pack enabled and creditsPerPack > 0
exact current local BillingPeriod
provider current cycle == exact local BillingPeriod
configured pack event handle exists on exact provider usage item
cycle phase ACTIVE, not DRAINING/RECONCILING
provider usage item returns unambiguous quantity/cost/currency BEFORE evidence
no unresolved REQUESTED top-up purchase that would make before/after valuation ambiguous
```

The last guard is server-side, concurrency-safe and not merely a disabled button. Two simultaneous purchase clicks must not create two unresolved purchases whose provider cost deltas cannot be attributed uniquely.

Free plan rules remain: no Paid recovery meter requirement and no Free included-period grant/reset.

## One verified billing-context read

Before creating the purchase, resolve one coherent provider/local context and use it for all snapshots. Do not query one plan, then later independently pick another period/meter.

Capture from that same verified context:

```text
billingPeriodId
providerSubscriptionIdSnapshot
planId
shopifyPlanHandleSnapshot
shopifyEventHandleSnapshot
providerUsageQuantityBeforeSnapshot
providerUsageCostBeforeSnapshot
providerUsageCostCurrencyBeforeSnapshot
providerPriceSnapshot
creditsGranted = local configured recoveryCreditsPerPack
```

The provider-before quantity/cost/currency are required. Missing provider cost must not be silently treated as zero.

## Purchase action transaction

The action accepts only minimal idempotency/client operation identity already used by the repository. Reject/ignore client:

```text
price
currency
plan
meter handle
creditsPerPack
provider quantity/cost
refund fields
```

Create/reuse in one transaction equivalent state:

```text
RecoveryCreditPurchase:
  status = REQUESTED
  currentAmount = 0
  reservedAmount = 0
  immutable commercial-before snapshots

UsageEvent:
  metric = RECOVERY_CREDIT_PACK_PURCHASE
  quantity = 1
  exact billingPeriodId/meter
  shopifyReportState = PENDING
```

Replay of the same client operation returns the same purchase/event. Concurrency must enforce at most one unresolved valuation candidate for the same shop/provider subscription/BillingPeriod/pack meter according to DATABASE-014/runtime invariant.

Return REQUESTED as pending. Never claim credits are usable before durable ACTIVE state exists.

## `TopUpPurchasePanel` production contract

Refactor the component to consume explicit server props. It must:

- render real pack credit quantity and current aggregate purchased available balance;
- explain top-ups are lifetime-until-used;
- render provider-derived pricing only from exact adapter data;
- otherwise say Shopify bills through the current App Pricing meter without fabricating price/unit cost/currency;
- expose one purchase CTA only when `purchaseEligible=true` and no unresolved REQUESTED purchase blocks valuation;
- render REQUESTED as awaiting Shopify confirmation and show zero newly activated credits;
- render ACTIVE only from durable ACTIVE state;
- render COMPLETED/WITHDRAWN/REFUNDED as historical latest-purchase states without treating them as newly purchased capacity;
- use bounded provider report/attention copy without introducing an extra purchase lifecycle state;
- call only supplied callbacks; no network/Prisma/provider calls from component;
- remove mock/default pricing imports;
- localize every new string.

Add/link to the future dedicated purchase-management page only in SHOPIFY-026, not here.

## Required tests

At minimum prove:

1. exact configured pack meter required;
2. provider subscription/cycle/meter are coherent and current;
3. missing provider BEFORE quantity/cost/currency is ineligible;
4. BillingPlan local money is never authority;
5. REQUESTED purchase snapshots exact BillingPeriod/provider subscription/plan/meter/before usage evidence;
6. REQUESTED initializes `currentAmount=0,reservedAmount=0`;
7. HTTP action never sets ACTIVE;
8. same operation replays one purchase/event;
9. concurrent unresolved purchase creation is prevented server-side;
10. direct App Event network publication does not occur in HTTP transaction;
11. client money/quantity/context cannot override server snapshots;
12. mapped Free exact cycle+meter remains eligible without Paid meter;
13. DRAINING/RECONCILING/missing cycle/missing meter fail closed;
14. panel renders provider price only from explicit provider state;
15. no local/fabricated price or mock remains;
16. REQUESTED prevents misleading success/duplicate action;
17. all five canonical statuses can be rendered safely when latest historical purchase has them;
18. focused tests, repository validation/build and `git diff --check` pass.

## Non-goals

Do not implement Background provider activation/valuation, refund lifecycle/actions/UI, plan change, cancellation, promotions, Admin or full billing-options composition.

## Stop conditions

STOP if Shopify App Pricing/App Events is no longer the actual mechanism, exact provider before-cost evidence is unavailable from the accepted provider read model, or implementing this task requires guessing a purchase price.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `app/components/dashboard/TopUpPurchasePanel.jsx`
- `app/i18n/locales/en.json`
- `app/routes/app/billing/options/route.tsx`
- `app/routes/app/billing/route.tsx`
- `app/services/billing/billing.service.ts`
- `tests/unit/services/billing.service.test.ts`

### Work Completed
- Implemented the merchant-safe top-up read model and action using the canonical `REQUESTED` lifecycle.
- Added coherent provider subscription/cycle/meter verification, required provider BEFORE usage/cost/currency evidence, immutable purchase snapshots, zero initial balances, and unresolved-purchase concurrency protection.
- Preserved idempotent replay and prevented HTTP-side activation or direct App Event publication.
- Replaced mock pricing/purchase UI with the explicit server-state `TopUpPurchasePanel`, canonical status rendering, pending-state duplicate prevention, provider-derived pricing, and localized copy.
- Added focused service coverage for evidence gates, REQUESTED initialization, and unresolved-purchase prevention.

### Validation Results
- `npm test -- --run tests/unit/services/billing.service.test.ts tests/unit/billing-ui.test.ts`: passed, 2 files and 196 tests.
- `git diff --check`: passed.

### Git / VCS
- Launcher-provided isolated implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-014`.
- Launcher-provided isolated parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-014`.
- Mirrored task branch: `task/ARCH-010-SHOPIFY-014` in both repositories.
- Implementation commit `bfc7af3` (`feat(shopify): finalize recovery credit top-up lifecycle`) pushed to `origin/task/ARCH-010-SHOPIFY-014`.
- Parent report commit `77944d9` (`task: return SHOPIFY-014 for review`) is pushed to `origin/task/ARCH-010-SHOPIFY-014`.

### Architect Review
Pending moda_architect review.

## Architect Review — Attempt 1

### Decision

**Changes Requested — return the same task to Ready for Attempt 2.**

Implementation reviewed:

```text
bfc7af3f7a0c87813dba521a81b853b755c6a34e
```

Parent/report evidence reviewed:

```text
77944d9  task: return SHOPIFY-014 for review
571f8a7654ba22fc9f2b90c2f6b3bce43fe8b5d4  docs: finalize SHOPIFY-014 VCS evidence
```

Attempt 1 gets the core durable purchase write largely right and that work MUST be preserved:

- new purchases are created only as `REQUESTED`;
- `currentAmount=0` and `reservedAmount=0` at creation;
- one verified provider/local cycle is used for the commercial BEFORE snapshots;
- `billingPeriodId`, provider subscription identity, plan/meter, BEFORE quantity/cost/currency and provider price snapshot are persisted;
- one `RECOVERY_CREDIT_PACK_PURCHASE` UsageEvent is created as `PENDING`;
- same purchase ID replays the existing purchase/event;
- the Subscription row is locked before unresolved-purchase arbitration, serialising same-shop concurrent requests;
- HTTP code neither publishes the App Event nor transitions the purchase to `ACTIVE`;
- Free does not require the Paid recovery meter;
- client-supplied price/plan/meter/credit data is not authoritative.

Do not rewrite those accepted mechanics unless one of the exact Attempt-2 regressions below proves a defect.

### Finding 1 — mutation/read eligibility does not enforce the full executable contract

The task requires, at mutation time:

```text
Shop ACTIVE
executable current subscription policy
provider lifecycle not FROZEN/CANCELED/UNRESOLVED
exact current provider subscription identity/plan/cycle/meter
ACTIVE local/provider cycle phase
exact provider BEFORE quantity/cost/currency
```

The current `requestRecoveryCreditPack(...)` loads `Shop` but only checks that `shopifyShopId` exists. It does **not** require:

```text
shop.status == ACTIVE
```

The current provider verification also uses `provider.getActiveSubscription(...)` directly and therefore ignores the accepted SHOPIFY-018 rule:

```text
latest effective FROZEN lifecycle evidence wins even when activeSubscription is temporarily non-null
```

That can permit a purchase in the interval where Shopify has frozen the contract but the local Subscription projection has not yet caught up.

The merchant read model has the same truthfulness problem. `recoveryCreditPackPurchaseEligible`/`purchaseEligible` can currently be true for states that the mutation will reject because the read predicate does not require all of:

```text
Shop.status == ACTIVE
Subscription.status in {ACTIVE, TRIALING}
plan.active == true
plan.recoveryCreditPackEnabled == true
recoveryCreditsPerPack is a safe integer > 0
provider lifecycle is executable (not FROZEN/CANCELED/UNRESOLVED)
providerSubscriptionId is present
Paid primary recovery meter is configured, differs from the pack meter and exists on the provider subscription
```

This is a functional UI/API defect, not merely missing coverage: the production panel can expose a Buy CTA from a state that the authoritative mutation rejects.

#### Required Attempt-2 correction

In:

```text
app/services/billing/billing.service.ts
```

use the already accepted SHOPIFY-018 provider lifecycle snapshot for the top-up provider verification. Do **not** perform both a lifecycle snapshot and a separate `getActiveSubscription()` call for the same top-up read/action.

Use one provider request equivalent to:

```ts
const lifecycleSnapshot = await this.provider.getSubscriptionLifecycleSnapshot!(...);
const providerSubscription = lifecycleSnapshot.activeSubscription;
```

and classify it with the exact existing SHOPIFY-018 semantics:

```text
latest lifecycle state FROZEN
  -> not executable even if activeSubscription is non-null

activeSubscription present and no effective FROZEN
  -> eligible to continue verification

no activeSubscription + CANCELED
  -> not executable

no activeSubscription + other lifecycle evidence
  -> unresolved / not executable

no activeSubscription + no evidence
  -> no contract / not executable
```

Because SHOPIFY-014 depends on SHOPIFY-018, `getSubscriptionLifecycleSnapshot` is an accepted dependency. If a supplied test provider does not implement it, the top-up path must fail closed rather than silently falling back to a weaker commercial read.

For both the merchant top-up read state and `requestRecoveryCreditPack(...)`, require the same local executable prerequisites before returning/accepting eligibility:

```text
Shop.status == ACTIVE
Subscription.status == ACTIVE or TRIALING
BillingPlan.active == true
recoveryCreditPackEnabled == true
recoveryCreditsPerPack is safe integer > 0
exact OPEN pointed BillingPeriod
pack meter handle is non-empty
Paid only:
  primary recovery meter is non-empty
  primary recovery meter != pack meter
```

Then require from the single provider lifecycle snapshot:

```text
provider lifecycle executable
providerSubscriptionId non-empty
provider plan handle == local mapped plan handle
provider/local cycle exact match
exact pack usage item exists
pack handle exists in usageEventHandles
provider BEFORE quantity/cost/currency is complete
Paid only: provider exposes the exact primary recovery meter
billing phase == ACTIVE
```

The merchant read state may continue to expose the latest REQUESTED purchase separately. The panel must still suppress the CTA while that unresolved purchase exists; the server transaction remains final concurrency authority.

Do not move provider/network I/O inside the Prisma write transaction.

### Finding 2 — `/app/billing/options` integration belongs to SHOPIFY-012

Attempt 1 replaced the entire mock `BillingPurchaseHub` route with a top-up-only route. That removes the plan-management half of the route and crosses the explicit ownership boundary of:

```text
ARCH-010-SHOPIFY-012
Integrate real billing options route and purchase hub
```

SHOPIFY-012 explicitly owns composition of:

```text
SHOPIFY-009 capacity
SHOPIFY-013 commercial state
SHOPIFY-014 TopUpPurchasePanel
SHOPIFY-015 SubscriptionChangePanel
```

SHOPIFY-014 owns the adapter and the child component, not the final `/app/billing/options` composition.

#### Required Attempt-2 correction

Restore exactly:

```text
app/routes/app/billing/options/route.tsx
```

to the pre-task parent commit:

```text
64b535798ed03ca08045fbfa96ff364f7be26f77
```

Do not partially preserve the Attempt-1 route wiring. SHOPIFY-012 will remove the mock route and compose both production child panels after SHOPIFY-014 is accepted.

Preserve the correct `PENDING_BILLING -> REQUESTED` correction in:

```text
app/routes/app/billing/route.tsx
```

Do not restore that one-line lifecycle correction.

### Finding 3 — the production panel does not expose provider report attention/retry state

`getMerchantBillingState(...)` correctly returns:

```text
latestPurchase.usageReportState
```

but `TopUpPurchasePanel` discards it.

The task contract explicitly requires bounded provider reporting/attention presentation without inventing another purchase lifecycle state.

#### Required Attempt-2 correction

In:

```text
app/components/dashboard/TopUpPurchasePanel.jsx
```

extend the explicit `latestPurchase` prop contract to include:

```text
usageReportState
```

For a `REQUESTED` purchase:

```text
PENDING / IN_FLIGHT / REPORTED
  -> continue showing the existing awaiting-Shopify-confirmation copy;
     do not show active credits.

RETRYABLE
  -> show localized retry copy;
     do not enable another purchase;
     do not show active credits.

NEEDS_ATTENTION
  -> show localized needs-attention copy;
     do not enable another purchase;
     do not show active credits.
```

The purchase lifecycle remains exactly:

```text
REQUESTED | ACTIVE | COMPLETED | WITHDRAWN | REFUNDED
```

Do not create `RETRYABLE` or `NEEDS_ATTENTION` purchase statuses.

Use these exact English source strings:

```text
billingCommerce.topup.reportingRetry
  Shopify confirmation is being retried. No new credits are active yet.

billingCommerce.topup.reportingNeedsAttention
  Shopify confirmation needs attention. No new credits are active yet.
```

### Finding 4 — new merchant strings exist only in English

Attempt 1 added these canonical English keys:

```text
billingCommerce.purchaseStatus.ACTIVE
billingCommerce.purchaseStatus.COMPLETED
billingCommerce.purchaseStatus.WITHDRAWN
billingCommerce.purchaseStatus.REFUNDED
```

but none of the other 19 supported merchant catalogues contain them.

This is a runtime-functional defect. `CATALOGUE_KEYS` comes from `en.json` and `createMerchantI18n(...)` validates the selected catalogue against that canonical key set. A supported non-English merchant can therefore fail catalogue validation when this code is present.

Attempt 2 must add the four status keys plus the two provider-report keys above to **every** supported catalogue:

```text
cs da de en es fi fr it ja ko nb nl pl pt-BR pt-PT sv th tr zh-Hans zh-Hant
```

Use these exact status labels:

| Locale | ACTIVE | COMPLETED | WITHDRAWN | REFUNDED |
| --- | --- | --- | --- | --- |
| cs | Aktivní | Dokončeno | Staženo | Vráceno |
| da | Aktiv | Fuldført | Trukket tilbage | Refunderet |
| de | Aktiv | Abgeschlossen | Zurückgezogen | Erstattet |
| en | Active | Completed | Withdrawn | Refunded |
| es | Activo | Completado | Retirado | Reembolsado |
| fi | Aktiivinen | Valmis | Peruttu | Hyvitetty |
| fr | Actif | Terminé | Retiré | Remboursé |
| it | Attivo | Completato | Ritirato | Rimborsato |
| ja | 有効 | 完了 | 取り下げ | 返金済み |
| ko | 활성 | 완료 | 철회됨 | 환불됨 |
| nb | Aktiv | Fullført | Trukket tilbake | Refundert |
| nl | Actief | Voltooid | Ingetrokken | Terugbetaald |
| pl | Aktywny | Zakończony | Wycofany | Zwrócony |
| pt-BR | Ativo | Concluído | Retirado | Reembolsado |
| pt-PT | Ativo | Concluído | Retirado | Reembolsado |
| sv | Aktiv | Slutförd | Återtagen | Återbetald |
| th | ใช้งานอยู่ | เสร็จสมบูรณ์ | ถอนแล้ว | คืนเงินแล้ว |
| tr | Etkin | Tamamlandı | Geri çekildi | İade edildi |
| zh-Hans | 已激活 | 已完成 | 已撤回 | 已退款 |
| zh-Hant | 已啟用 | 已完成 | 已撤回 | 已退款 |

For `billingCommerce.topup.reportingRetry` and `billingCommerce.topup.reportingNeedsAttention`, preserve the exact English semantics above and provide a native-language translation in every supported non-English catalogue. Do not leave the English source text copied into non-English catalogues.

### Provider price presentation

Do not invent a flat amount from the tiered Shopify usage price. The accepted provider pack price is the SHOPIFY-013 tiered usage-item shape. It is safe for the panel to show the localized Shopify-meter billing note when that exact shape cannot be represented as one unambiguous amount.

Update the component JSDoc/PropTypes so it no longer claims the tiered pack price has a flat `{ amount, currency }` shape. Do not add client-side pricing calculations.

### Attempt-2 permanent functional tests

The focus is functionality, not exhaustive coverage. Add only the regressions required to prove the corrected behaviour:

1. `rejects top-up when Shop is not ACTIVE before provider verification`
   - Shop status is not ACTIVE;
   - provider lifecycle API is not called;
   - no UsageEvent or purchase is created.

2. `fails closed when Shopify lifecycle is FROZEN even if activeSubscription is present`
   - lifecycle snapshot contains a valid active subscription plus latest `FROZEN` event;
   - read state returns `purchaseEligible=false`;
   - mutation creates no UsageEvent/purchase.

3. `uses one lifecycle snapshot as the provider authority for a successful top-up`
   - exactly one lifecycle-snapshot provider call;
   - no independent `getActiveSubscription()` call for the same mutation;
   - exact REQUESTED snapshots remain unchanged.

4. `does not advertise purchase eligibility for an unsafe local subscription projection`
   cover at least one non-executable status such as `FROZEN` or `SYNC_ERROR` and assert `purchaseEligible=false`.

5. `does not advertise purchase eligibility when provider subscription identity is missing`
   - otherwise-valid provider context;
   - `providerSubscriptionId=null`;
   - `purchaseEligible=false` and mutation rejects.

6. `does not advertise purchase eligibility when local pack configuration is disabled`
   - `recoveryCreditPackEnabled=false` or invalid `recoveryCreditsPerPack`;
   - `purchaseEligible=false`.

7. `renders REQUESTED provider retry and attention states without enabling another purchase`
   - RETRYABLE and NEEDS_ATTENTION;
   - no Buy CTA;
   - no active-credit claim.

8. merchant catalogue validation proves all six task-visible keys exist in all 20 supported locale catalogues.

Keep the existing REQUESTED creation/replay/concurrency/snapshot tests. Do not chase unrelated repository coverage.

### Validation

Run and record:

```text
npm test -- --run \
  tests/unit/services/billing.service.test.ts \
  tests/unit/billing-ui.test.ts \
  tests/unit/merchant-i18n.test.ts \
  tests/unit/billing-i18n.test.ts

npm run prisma:generate
npm run build
git diff --check
```

If repository-wide typecheck remains non-zero only for the documented `TYPECHECK-001` baseline, record the exact count and prove no new diagnostic belongs to Attempt-2 changed lines.

### Scope / non-goals for Attempt 2

Allowed production files:

```text
app/services/billing/billing.service.ts
app/components/dashboard/TopUpPurchasePanel.jsx
app/i18n/locales/*.json
app/routes/app/billing/options/route.tsx   # restore-only to 64b5357
```

Preserve the already-correct lifecycle change in:

```text
app/routes/app/billing/route.tsx
```

Tests may change only as required for the functional regressions above.

Do not modify:

```text
Prisma schema/migrations
Background services
Shared package
Admin
refund lifecycle
purchase activation/valuation
plan-change implementation
BillingPurchaseHub composition
Shopify provider GraphQL contract
```

### Stop condition

Return to `moda_architect` only when:

```text
- the service mutation and merchant read state apply the same executable top-up authority;
- FROZEN provider lifecycle cannot purchase even with a temporarily non-null activeSubscription;
- Shop ACTIVE is enforced by the service, not only the route;
- `/app/billing/options` is restored for SHOPIFY-012 ownership;
- REQUESTED report retry/attention state is visible without a sixth lifecycle state;
- all six task-visible keys are present in all 20 merchant locale catalogues;
- existing REQUESTED purchase provenance/idempotency/concurrency behaviour remains intact;
- focused functional tests and diff check pass.
```

Do not start `ARCH-010-SHOPIFY-012` or `ARCH-010-BACKGROUND-021` from this task.

