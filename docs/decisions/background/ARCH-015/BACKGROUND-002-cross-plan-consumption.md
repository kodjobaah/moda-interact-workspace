---
id: ARCH-015-BACKGROUND-002
architecture_id: ARCH-015
title: Consume historical purchased-credit lots before current refundable lots
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-015-SHARED-001
- ARCH-015-BACKGROUND-001
enables:
- ARCH-015-SYSTEM-TEST-001
created: 2026-09-15
updated: 2026-09-16
---

# ARCH-015-BACKGROUND-002

## Objective

Preserve all active purchased credits across plan/cycle changes while changing reservation selection to consume historical/non-current-provider-context lots before current-context lots.

## Authorized implementation surface

```text
src/services/purchased-recovery-reservation.service.ts
src/services/recovery-billing.service.ts                 # only if orchestration needs classification input
tests/unit/services/purchased-recovery-reservation.service.test.ts
tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts
```

No Shopify network call in the reservation path.

## Current-context classification

Use current local Subscription projection only as a consumption-order hint.

Derive current provider context through Shared from:

```text
Subscription.providerSubscriptionId
Subscription.observedShopifyPlanHandle
Subscription.currentPeriodStart
Subscription.currentPeriodEnd
Subscription.billingPeriodId
```

A lot is "current-context" only when:

```text
status == ACTIVE
purchase.providerSubscriptionIdSnapshot == current derived context
purchase.shopifyPlanHandleSnapshot == current observed plan handle
purchase.billingPeriodId == current billingPeriodId
```

If subscription projection is missing/ambiguous/unmapped/frozen, classify all lots as historical for ordering. This does not make them unspendable.

## Selection order

For spendable ACTIVE lots:

```text
1. historical/non-current lots
   order activatedAt ASC NULLS LAST, createdAt ASC, id ASC

2. current-context lots
   same oldest-first order
```

Retain all existing atomic reservation/CAS/refund-hold rules.

Do not filter by current `planId`, current billingPeriodId, or current meter to determine spendability.

## Replay behavior

If an existing released reservation can reuse its original lot and that lot is still ACTIVE/spendable, preserve replay affinity even if classification changed. If original lot cannot be reused, apply the new ordered selector.

## Shopify billing rule

Commit of purchased credits continues to create local `RECOVERY_CONVERSATION` usage evidence with `ShopifyReportState.NOT_APPLICABLE`.

Never emit the purchase meter's event handle when consuming credits.

## Tests

- old Starter lot remains spendable after Growth transition;
- historical Starter lots selected before current Growth lot even when Growth lot is older by id;
- within historical group oldest first;
- within current group oldest first;
- ambiguous local subscription => all lots still spendable, oldest ordering;
- no current plan/billingPeriod filter removes historical credits;
- replay original lot semantics preserved;
- refund-held WITHDRAWN lots remain non-selectable;
- purchased-credit commit remains NOT_APPLICABLE to Shopify;
- concurrency/CAS tests remain green.

## Stop conditions

STOP if implementing order requires Shopify network I/O in recovery admission/reservation.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

Status: Ready for Review

Implementation commit: `56f95e3` (`Validate purchased credit provider context projection`), pushed to `task/ARCH-015-BACKGROUND-002`.

### Implementation Summary

- Updated `src/services/purchased-recovery-reservation.service.ts` to select `currentPeriodStart` and `currentPeriodEnd`, require a valid ordered period projection, and derive provider context through Shared `deriveShopifyProviderContextIdentity` using the provider subscription ID, observed plan handle, period bounds, and billing period ID.
- Current-context classification now requires `status == ACTIVE`; `TRIALING`, missing projections, and invalid period projections classify every lot as historical for ordering without making any ACTIVE lot unspendable.
- Existing historical-before-current ordering, within-group FIFO, cross-plan/cycle preservation, replay affinity, WITHDRAWN refund holds, atomic CAS behavior, local `RECOVERY_CONVERSATION` / `NOT_APPLICABLE` evidence, and no-Shopify-I/O behavior remain intact.

### Rework Correction Mapping

- Shared provider-context derivation with period identity: implemented in `src/services/purchased-recovery-reservation.service.ts`; focused tests retain current-group ordering with valid period data and cover invalid period projection as historical.
- ACTIVE-only current-context classification: implemented by removing `TRIALING` from the current-context gate; focused regression verifies a TRIALING lot follows historical FIFO rather than current-group ordering.
- Existing required behavior: preserved by the unchanged reservation/CAS/replay/refund/commit paths and the focused suite passing 19/19.

### Tests and Validation

- `npm run test -- tests/unit/services/purchased-recovery-reservation.service.test.ts`: passed, 19/19.
- `npm run test -- tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts`: skipped, 7 tests, because `TEST_DATABASE_URL` and `MODA_DISPOSABLE_INTEGRATION=1` were not enabled in the environment.
- `npm run build`: passed, including Prisma client generation and TypeScript compilation.
- `npm run test:unit`: 927/929 passed; 2 existing unrelated observability-startup baseline failures remain for worker close-resource source text and Shared version `0.9.0` versus package version `0.11.2`.
- `git diff --check`: passed.

### Worktree and Dependency Evidence

- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-BACKGROUND-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-BACKGROUND-002`.
- Database submodule observed at: `d44b621cdcc3635127b91601be648b61c0eff1e2`.
- Implementation branch is clean after push; parent report has only this Completion Report/frontmatter update pending publication.

### Limitations

- Disposable PostgreSQL concurrency tests were not executable without the required integration environment gate; no source or schema workaround was applied.
- Broader unit-test failures were not modified because they are outside this task's authorized implementation surface.


## Architect Review — Attempt 2

### Status

**Changes Requested — one fail-closed projection correction only**

Attempt 2 closes the two principal defects from Attempt 1:

```text
- current provider context is derived through Shared from provider id + observed plan
  + current period bounds;
- null legacy provider id is no longer rejected before Shared derivation;
- TRIALING is no longer classified as current-context for BACKGROUND-002 ordering;
- reversed/non-forward current periods classify all ACTIVE lots as historical;
- historical-first / within-group FIFO / replay / refund-hold / CAS / NOT_APPLICABLE
  behavior remains intact.
```

Implementation evidence reviewed:

```text
56f95e3800f4d0a4be9a6d8a8df53461273b541c
```

Parent Completion Report evidence:

```text
8573d8c1502b203639c229bad8d52cce5d53fccd
```

One production fail-closed gap remains.

### Finding — malformed native App Pricing ordering hints can still throw

The selector currently gates the Shared derivation with JavaScript truthiness:

```ts
subscription.plan?.active
&& subscription.observedShopifyPlanHandle
&& subscription.billingPeriodId
&& isValidCurrentPeriod(...)
```

and then calls:

```ts
deriveShopifyProviderContextIdentity(...)
```

directly.

That is not sufficient for the task's ambiguous/malformed-projection rule. In
particular, a whitespace-only `observedShopifyPlanHandle` is truthy. When the raw
`providerSubscriptionId` is null (native App Pricing), Shared rejects the blank plan
handle with `SHOPIFY_PROVIDER_CONTEXT_INVALID:`. The exception can therefore escape the
reservation path.

BACKGROUND-002 requires the local Subscription projection to be an ordering hint only.
Missing, malformed, ambiguous, unmapped or otherwise unusable context evidence must
classify every ACTIVE purchased lot as historical; it must never make purchased credits
unspendable by throwing from reservation selection.

### Required Attempt-3 correction

Modify only the bounded current-context classification in:

```text
src/services/purchased-recovery-reservation.service.ts
```

and its focused tests.

Implement a fail-closed helper or equivalent deterministic logic with these exact rules:

```text
1. subscription must exist;
2. subscription.status must equal ACTIVE exactly;
3. mapped plan must be active;
4. observedShopifyPlanHandle must be a nonblank string after trim;
5. billingPeriodId must be a nonblank string after trim;
6. currentPeriodStart/currentPeriodEnd must both be valid finite dates and start < end;
7. call deriveShopifyProviderContextIdentity(...) with the raw nullable
   providerSubscriptionId and validated plan/period evidence;
8. if Shared derivation throws SHOPIFY_PROVIDER_CONTEXT_INVALID (or any malformed local
   projection prevents safe derivation), return currentContext = null;
9. never propagate that ordering-hint derivation failure from reserve().
```

Do not require `providerSubscriptionId` itself to be non-null. Valid native App Pricing
must still derive:

```text
app-pricing:v1:<encodedPlanHandle>:<periodStartIso>:<periodEndIso>
```

The Shared comparator remains the authority for identity + plan + billingPeriod equality.
Do not add Shopify I/O.

### Required focused regressions

Add/retain tests proving:

```text
A. legacy provider id + valid ACTIVE context
   -> matching lot is current-context
   -> historical lot is selected first

B. native App Pricing (providerSubscriptionId = null) + valid ACTIVE plan/period
   -> derive canonical app-pricing:v1 identity
   -> matching native lot is current-context
   -> a later historical lot is still selected first

C. native period changes
   -> old derived purchase identity is historical

D. whitespace-only observedShopifyPlanHandle with null legacy provider id
   -> no exception escapes
   -> all ACTIVE lots remain spendable under historical FIFO

E. blank billingPeriodId / invalid or non-forward period
   -> no exception
   -> all ACTIVE lots historical

F. TRIALING
   -> all ACTIVE lots historical under this task's ordering rule
```

Preserve existing tests for replay affinity, refund-held WITHDRAWN exclusion,
`NOT_APPLICABLE` usage evidence, FIFO grouping and CAS behavior.

### Integration validation

The disposable PostgreSQL concurrency suite was unavailable in Attempts 1 and 2. This
remains an environmental limitation, not the production defect above.

Attempt 3 must:

```bash
npm run test -- tests/unit/services/purchased-recovery-reservation.service.test.ts
npm run build
npm run test:unit
git diff --check
```

Run the disposable PostgreSQL concurrency suite only when both required environment gates
are available. If unavailable, record the skip exactly; do not introduce a workaround.

### Scope / stop conditions

Do not redesign:

```text
reservation transaction isolation / CAS
replay affinity
refund hold semantics
lot spendability rules
ShopifyReportState.NOT_APPLICABLE evidence
Shared package source/version
schema or database submodule
Shopify provider/network integration
```

If this fail-closed ordering-hint correction requires any of those changes, STOP and
return the limitation to `moda_architect`.

Return this same task to `review` after the correction. Preserve `attempt: 2` before the
next claim so `/moda-task` increments **Attempt 2 -> Attempt 3 exactly once**. Clear
`executor` and `claimed_at` on return.
