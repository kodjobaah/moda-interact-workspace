---
id: ARCH-015-BACKGROUND-001
architecture_id: ARCH-015
title: Reconcile REQUESTED recovery-credit purchases from candidate provider baselines
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 40
executor: null
claimed_at: null
attempt: 3
depends_on:
- ARCH-015-SHARED-001
- ARCH-015-DATABASE-001
- ARCH-015-SHOPIFY-002
enables:
- ARCH-015-BACKGROUND-002
- ARCH-015-SHOPIFY-003
- ARCH-015-BACKGROUND-003
created: 2026-09-15
updated: 2026-09-16
---

# ARCH-015-BACKGROUND-001

## Objective

Replace current-plan/aggregate-count purchase activation assumptions with candidate-centric reconciliation against each REQUESTED purchase's immutable provider-before evidence.

## Authorized implementation surface

## Completion Report

Status: Ready for Review

Implementation commit: `37d1a82` on `task/ARCH-015-BACKGROUND-001`, pushed to `origin`.

### Architect Review Corrections

- Finding 1 implemented: dependency is exactly `@modainteract/moda-interact-shared` `0.11.2`; installed billing entrypoint exports both `deriveShopifyProviderContextIdentity` and `isSameShopifyPurchaseProviderContext`. Fresh provider period start/end and raw nullable provider id are converted to the canonical context identity. Candidate proof compares that identity with the immutable purchase snapshot, plan handle, and local billing period. Raw `Subscription.providerSubscriptionId` persistence is unchanged.
- Finding 1 coverage implemented: legacy provider identity still activates; native App Pricing identity activates only for the exact derived plan/period context; period mismatch, plan mismatch, blank identity, and malformed context fail closed without grant.
- Finding 2 implemented: current and pending flat-rate provider items are retained by nonblank handle and `FlatRatePrice` type regardless of `price.active`; existing tiered retention and cardinality behavior remain intact.
- Finding 2 coverage implemented: current and pending `FlatRatePrice active=false` items are retained, while the existing multiple-item fail-closed behavior remains unchanged.

### Complete Audit Checklist

- Candidate discovery: implemented. Candidates are `REQUESTED`, linked to `RECOVERY_CREDIT_PACK_PURCHASE`, quantity `1`, and linked usage state `REPORTED`.
- Deterministic ordering and event-handle ambiguity: implemented. Candidates order by `createdAt`, `id`; multiple unresolved rows for one event handle return `ambiguous` and grant nothing.
- Immutable provider-before proof: implemented. No baseline rewrite or current-plan/count-derived quantity is used; exact event-handle provider readback is required.
- Exact Decimal quantities: implemented. Quantity arithmetic uses `Prisma.Decimal`, including fractional baselines.
- Inactive provider item retention: implemented for current flat-rate, pending flat-rate, and tiered items.
- Zero-cost activation: implemented and tested when exact quantity proof succeeds with unchanged cost.
- Mismatch fail-closed behavior: implemented and tested for quantity, currency, provider context, plan, cycle, missing meter, negative cost delta, blank identity, and malformed context.
- Atomic activation and aggregate idempotency: implemented with Serializable transaction, optimistic row guard, and aggregate increment in the same transaction; replay does not regrant.
- Sequential same-handle progression: tested for `0 -> 1` and `1 -> 2`.
- Fractional baseline: tested for `1.75 -> 2.75`.
- Best-effort resume scheduling: tested after commit, including enqueue failure preserving activation.
- No schema changes: confirmed; database submodule remains at supplied `d44b621cdcc3635127b91601be648b61c0eff1e2`.
- Required tests: focused provider, purchase, resume-hint, billing-reconciliation, and usage-publisher coverage passes; all listed regression cases are covered.

### Changed Files

- `package.json`
- `package-lock.json`
- `src/providers/shopify-partner-billing.provider.ts`
- `src/services/billing-reconciliation.service.ts`
- `src/services/recovery-credit-purchase.service.ts`
- `tests/unit/providers/shopify-partner-billing.provider.test.ts`
- `tests/unit/services/billing-reconciliation.service.test.ts`
- `tests/unit/services/recovery-credit-purchase.resume-hint.test.ts`
- `tests/unit/services/recovery-credit-purchase.service.test.ts`

### Validation

- `npm install`: passed; installed shared package is exactly `0.11.2` and both required billing helpers are functions.
- Focused required command: passed, 5 files / 104 tests.
- `npm run build`: passed; Prisma client generation and TypeScript compilation completed successfully.
- `npm run test:unit`: 58 files, 921 passed / 2 failed / 923 total. The only failures are the documented pre-existing observability baseline mismatches in `tests/unit/runtime/observability-startup.test.ts`: stale worker close-resource source-text expectation and stale exact shared runtime expectation of `0.9.0` (the task-required dependency is now `0.11.2`). No task-owned test failed.
- `git diff --check`: passed.

### Worktree and Publication Evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-BACKGROUND-001`.
- Implementation branch: `task/ARCH-015-BACKGROUND-001`, pushed at `37d1a82`.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-BACKGROUND-001`.
- Attempt 3 claim commit: `04f5937d67999dddf2905990e4e8846a79a73ec6`.
- Dependencies passed: `ARCH-015-SHARED-001`, `ARCH-015-DATABASE-001`, `ARCH-015-SHOPIFY-002`.
- No submodule gitlink, schema, Architect Review section, or other task file was modified.

### Limitations

The full unit suite retains only the two documented observability startup baseline failures above. Focused task validation, build, dependency export proof, and all task-owned tests are green.
- provider quantity equals expected quantity-after exactly;
- provider currency equals before currency;
- provider cost-after is non-negative;
- provider cost-after >= provider cost-before.

`providerPurchaseAmount = costAfter - costBefore`.

Zero monetary delta is valid for a genuinely zero-cost Shopify top-up meter. Do not require `providerPurchaseAmount > 0` to activate. Negative delta is invalid for purchase activation.

On proof, atomically:

```text
providerUsageQuantityAfterSnapshot = exact Decimal provider quantity
providerUsageCostAfterSnapshot
providerUsageCostCurrencyAfterSnapshot
providerPurchaseAmount
providerPurchaseCurrency
providerValuationConfirmedAt
currentAmount = creditsGranted
status = ACTIVE
activatedAt
version++
increment PURCHASED_RECOVERY_CREDITS.grantedQuantity by creditsGranted
```

Then schedule existing capacity-resume hint best-effort.

## Provider context changed before proof

If App Event was reported but the current provider context no longer exposes/proves the candidate's original context:

- do not grant credits;
- do not rewrite candidate baseline;
- do not attribute new-cycle quantity;
- mark/report bounded attention using existing durable report/discrepancy mechanisms;
- leave purchase REQUESTED so same-handle single-flight remains blocked pending investigation.

Do not add a new purchase status without architect approval.

## Sequential same-handle test

Prove:

```text
P1 before=0 -> provider=1 -> P1 ACTIVE
P2 before=1 -> provider=2 -> P2 ACTIVE
```

Also prove fractional baseline after a prior correction:

```text
P3 before=1.75 -> provider=2.75 -> P3 ACTIVE
```

## Required tests

- price.active false provider item retained;
- REQUESTED candidate requires reported usage event;
- exact Decimal quantity arithmetic;
- zero-cost purchase activates when quantity proof is exact and cost unchanged;
- quantity mismatch does not activate;
- currency mismatch does not activate;
- provider context mismatch does not activate;
- plan/cycle change does not reinterpret current meter;
- multiple unresolved same-handle rows => ambiguous/no grant;
- sequential two-purchase same-handle baseline progression;
- fractional pre-baseline purchase;
- aggregate granted counter increments once;
- repeated reconciliation is idempotent;
- resume scheduling remains best-effort after activation.

## Stop conditions

STOP if:

- reconciliation cannot prove candidate from its stored before evidence without adding new schema beyond DATABASE-001;
- current task would need to grant on HTTP 202 without provider readback;
- a code path still derives expected provider quantity from count of active purchases rather than candidate before snapshot.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

Status: Ready for Review

Implementation commit: `337b1a7` on `task/ARCH-015-BACKGROUND-001`, pushed to `origin`. This commit follows the packet baseline `6c3e92779b537ccfd073ed2a7c32ff674c2921c9`.

### Audit Checklist

- Objective: implemented. Activation is candidate-centric and uses each REQUESTED purchase's immutable provider-before evidence.
- Authorized implementation surface: only the provider parser and authorized unit tests changed; no schema or other repository changes.
- Provider parser rule: implemented. Tiered live items are retained regardless of `price.active`; provider quantities accept number or exact decimal-string representations and are normalized to strings.
- Durable candidate discovery: implemented. Candidates require `RecoveryCreditPurchase.status = REQUESTED`, linked `RECOVERY_CREDIT_PACK_PURCHASE` usage, quantity `1`, and `shopifyReportState = REPORTED`.
- Deterministic ordering and event-handle ambiguity: implemented. Candidates order by `createdAt`, `id`; multiple REQUESTED rows for one event handle produce `ambiguous` with no activation. Distinct handles activate independently.
- Candidate proof: implemented. Proof checks immutable subscription, plan, event handle, billing cycle, exact expected quantity, currency, non-negative cost, and non-negative cost delta. Missing exact meters fail closed.
- Context changes: implemented. Candidates remain REQUESTED and are not re-baselined or attributed to a new cycle when proof fails.
- Sequential same-handle behavior: implemented and now explicitly tested for `0 -> 1`, `1 -> 2`; fractional `1.75 -> 2.75` coverage remains green.
- Zero-cost activation: implemented and covered; unchanged cost with exact quantity proof activates.
- Negative, currency, quantity, and context mismatch: implemented fail-closed behavior and covered by focused tests.
- Atomic activation and aggregate increment idempotency: implemented with Serializable transaction, optimistic row guard, and aggregate update in the same transaction; replay remains idempotent.
- Best-effort resume scheduling: implemented and covered; scheduling occurs after commit and failures are logged without changing the activation result.
- Stop conditions: no provider grant on HTTP 202, no count-derived expected quantity, no schema change, and no new status introduced.

### Findings and Fixes

One real implementation gap was found: `parseActiveSubscription` filtered inactive tiered items when they had no usage object, which discarded a live provider item solely because `price.active` was false. The parser now retains all tiered subscription items. The audit also added explicit regression coverage for string-decimal provider quantities and sequential same-handle baselines. No other implementation gaps were found.

### Changed Files

- `src/providers/shopify-partner-billing.provider.ts`
- `tests/unit/providers/shopify-partner-billing.provider.test.ts`
- `tests/unit/services/recovery-credit-purchase.service.test.ts`

### Validation

- `npm test -- tests/unit/providers/shopify-partner-billing.provider.test.ts tests/unit/services/recovery-credit-purchase.service.test.ts tests/unit/services/recovery-credit-purchase.resume-hint.test.ts`: passed, 3 files / 49 tests.
- `npm test -- tests/unit/services/recovery-credit-purchase.service.test.ts tests/unit/services/recovery-credit-purchase.resume-hint.test.ts tests/unit/services/billing-reconciliation.service.test.ts tests/unit/providers/shopify-partner-billing.provider.test.ts tests/unit/services/shopify-usage-event-publisher.service.test.ts`: passed, 5 files / 102 tests.
- `npm run build`: passed; Prisma client generation and TypeScript compilation completed successfully.
- `npm run test:unit`: 57 files, 919 passed / 2 failed / 921 total. Both failures are pre-existing observability baseline mismatches in `tests/unit/runtime/observability-startup.test.ts`: worker close-resource source text and expected shared runtime `0.9.0` versus declared `0.11.0`. No task-owned test failed.
- `git diff --check`: passed.

### Worktree and Submodule Evidence

- Prepared implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-BACKGROUND-001`.
- Implementation branch: `task/ARCH-015-BACKGROUND-001`; pushed at `337b1a7`; database submodule was `d44b621cdcc3635127b91601be648b61c0eff1e2` as supplied by the packet.
- Prepared parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-BACKGROUND-001`.
- Packet claim commit: `d729cb9ad2e871c92ddebdcaf840aba29992c039`; dependencies passed: `ARCH-015-SHARED-001`, `ARCH-015-DATABASE-001`, `ARCH-015-SHOPIFY-002`.
- No submodule gitlink, schema, Architect Review section, or other task file was modified.

### Limitations

The full unit suite remains blocked only by the two pre-existing observability startup expectation mismatches listed above. Focused task validation, build, and all task-owned tests are green.


## Architect Review — Attempt 2

### Status

**Changes Requested — canonical provider-context identity + complete inactive-price parser alignment**

The candidate-centric reconciliation implementation is otherwise accepted. Preserve the
existing behavior for:

```text
REQUESTED + REPORTED durable candidate discovery
exact event-handle provider readback
Decimal before + 1 quantity proof
zero-cost purchase activation
non-negative provider cost delta
currency equality
cycle proof
same-handle ambiguity fail-closed behavior
different-handle independence
Serializable activation transaction
optimistic purchase row guard
atomic PURCHASED_RECOVERY_CREDITS increment
idempotent replay
best-effort capacity resume after commit
no grant from HTTP 202 alone
```

Attempt 3 is limited to the two corrections below. Do not redesign the reconciliation
flow, schema, queues, purchase statuses, or refund behavior.

### Finding 1 — native App Pricing purchases cannot reconcile

`ARCH-015-SHOPIFY-002` stores the canonical provider-context identity in
`RecoveryCreditPurchase.providerSubscriptionIdSnapshot`.

For a legacy Shopify subscription id this identity is the trimmed provider id. For
native App Pricing, where `legacySubscriptionId == null`, the accepted Shared contract
derives:

```text
app-pricing:v1:<encodedPlanHandle>:<periodStartIso>:<periodEndIso>
```

The Background provider currently exposes the raw nullable
`PartnerSubscription.providerSubscriptionId`, and `BillingReconciliationService` passes
that raw value into `reconcileProviderConfirmed(...)`. The purchase service then requires:

```text
input.providerSubscriptionId !== null
candidate.providerSubscriptionIdSnapshot === input.providerSubscriptionId
```

Therefore a valid native App Pricing purchase has:

```text
purchase snapshot = app-pricing:v1:...
current raw legacy id = null
```

and can never activate even when plan, billing period, meter, quantity, currency and cost
all prove the purchase.

#### Required correction

Consume the architect-accepted Shared provider-context API from:

```text
@modainteract/moda-interact-shared/billing
```

The Background repository in this snapshot is pinned to `0.11.0`; the accepted ARCH-015
Shared correction is `0.11.2`. Update exactly:

```text
package.json
package-lock.json

@modainteract/moda-interact-shared: 0.11.0 -> 0.11.2
```

Do not use `0.11.1`. Do not choose another version. If exact `0.11.2` cannot be installed
or does not export both required helpers, STOP and return the blocker to `moda_architect`.

Use:

```ts
deriveShopifyProviderContextIdentity(...)
isSameShopifyPurchaseProviderContext(...)
```

The deterministic flow must be:

```text
BillingReconciliationService has fresh Partner subscription
  -> require exact current period start/end as today
  -> derive current providerContextIdentity from:
       providerSubscriptionId
       planHandle
       currentPeriodStart
       currentPeriodEnd
  -> pass the derived identity into purchase reconciliation

RecoveryCreditPurchaseService candidate proof
  -> compare candidate.providerSubscriptionIdSnapshot
     + candidate.shopifyPlanHandleSnapshot
     + candidate.billingPeriodId
     against current providerContextIdentity
     + current provider plan handle
     + current local billingPeriodId
     using isSameShopifyPurchaseProviderContext(...)
  -> separately prove exact candidate eventHandle/meter evidence
```

Do not overwrite or reinterpret `Subscription.providerSubscriptionId`; it remains the raw
nullable provider value. Do not derive identity from wall-clock time.

Rename the reconciliation input field from raw-provider semantics where practical, for
example:

```text
providerSubscriptionId -> providerContextIdentity
```

so callers cannot accidentally pass the raw nullable legacy id in the future.

Required regression coverage:

```text
legacy provider id -> valid matching candidate still activates
legacy provider id mismatch -> remains REQUESTED
native legacy id null -> derived app-pricing:v1 identity matches purchase and activates
native period/plan mismatch -> remains REQUESTED
blank/malformed required context -> fail closed; no credit grant
```

### Finding 2 — flat-rate live items are still filtered by `price.active`

The Attempt-2 correction fixed tiered usage items, but
`src/providers/shopify-partner-billing.provider.ts` still selects current and pending
flat-rate items with:

```text
item.price.__typename === "FlatRatePrice" && item.price.active
```

ARCH-015's provider parser rule is broader: membership comes from the returned Shopify
subscription items. A returned item must not be discarded solely because
`price.active === false`.

This is already the accepted behavior in the Shopify app-side provider parser and must be
consistent in Background.

Required parser behavior:

```text
current flat-rate plan candidates:
  handle is nonblank
  price.__typename == FlatRatePrice
  DO NOT filter on price.active

current tiered usage candidates:
  handle is nonblank
  price.__typename == TieredPrice
  DO NOT filter on price.active

pending flat-rate plan candidates:
  handle is nonblank
  price.__typename == FlatRatePrice
  DO NOT filter on price.active
```

Retain the existing cardinality checks: exactly one current flat-rate plan item and at
most one pending flat-rate plan item. Updating error text from "active flat-rate" to
"flat-rate" is allowed if needed for accuracy.

Required regression coverage:

```text
current FlatRatePrice active=false returned in activeSubscription.items -> planHandle retained
current TieredPrice active=false -> usage handle retained (existing coverage preserved)
pending FlatRatePrice active=false -> pendingPlanHandle retained
multiple current flat-rate items -> still fail closed
multiple pending flat-rate items -> still fail closed
```

### Attempt-3 authorized corrective surface

In addition to the original task surface, this review explicitly authorizes only these
extra dependency files because the task already depends on `ARCH-015-SHARED-001`:

```text
package.json
package-lock.json
```

Expected production/test surface is limited to:

```text
src/providers/shopify-partner-billing.provider.ts
src/services/billing-reconciliation.service.ts
src/services/recovery-credit-purchase.service.ts
package.json
package-lock.json
tests/unit/providers/shopify-partner-billing.provider.test.ts
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/services/recovery-credit-purchase.service.test.ts
# directly affected existing focused tests only
```

No database/schema migration, Shared source change, new status, new queue, or Shopify web
purchase change is authorized.

### Validation

Run at minimum:

```bash
npm install
npm test -- \
  tests/unit/providers/shopify-partner-billing.provider.test.ts \
  tests/unit/services/recovery-credit-purchase.service.test.ts \
  tests/unit/services/recovery-credit-purchase.resume-hint.test.ts \
  tests/unit/services/billing-reconciliation.service.test.ts \
  tests/unit/services/shopify-usage-event-publisher.service.test.ts
npm run build
npm run test:unit
git diff --check
```

The two already-documented unrelated observability startup failures may remain baseline
failures if unchanged. No task-owned failure is acceptable.

Also prove the installed package is exactly `0.11.2` and the billing entrypoint exports:

```text
deriveShopifyProviderContextIdentity
isSameShopifyPurchaseProviderContext
```

### Stop conditions

STOP and return to `moda_architect` if:

```text
exact Shared 0.11.2 cannot be consumed;
provider-context proof would require changing the canonical Shared identity format;
a schema change is required;
provider proof would need to activate from HTTP 202 without readback;
fixing inactive-price membership would require guessing among multiple flat-rate items.
```

### Workflow

Keep this same task:

```text
status: ready
attempt: 2
executor: null
claimed_at: null
```

Reclaim with `/moda-task ARCH-015-BACKGROUND-001`; the next valid claim increments to
Attempt 3 exactly once. `ARCH-015-BACKGROUND-002`, `ARCH-015-SHOPIFY-003`, and
`ARCH-015-BACKGROUND-003` remain Pending until this task is architect-accepted Complete.
