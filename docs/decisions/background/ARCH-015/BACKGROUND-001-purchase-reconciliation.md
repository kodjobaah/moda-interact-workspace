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
executor:
claimed_at:
attempt: 2
depends_on:
- ARCH-015-SHARED-001
- ARCH-015-DATABASE-001
- ARCH-015-SHOPIFY-002
enables:
- ARCH-015-BACKGROUND-002
- ARCH-015-SHOPIFY-003
- ARCH-015-BACKGROUND-003
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-015-BACKGROUND-001

## Objective

Replace current-plan/aggregate-count purchase activation assumptions with candidate-centric reconciliation against each REQUESTED purchase's immutable provider-before evidence.

## Authorized implementation surface

```text
src/providers/shopify-partner-billing.provider.ts
src/services/recovery-credit-purchase.service.ts
src/services/billing-reconciliation.service.ts
src/services/shopify-usage-event-publisher.service.ts      # only if Decimal handling needs alignment
tests/unit/services/recovery-credit-purchase*.test.ts
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/services/shopify-usage-event-publisher.service.test.ts
# directly affected integration tests
```

No schema changes.

## Provider parser rule

Do not discard live subscription items solely because `price.active === false`.

Provider usage quantity must be represented without integer coercion. Use `Prisma.Decimal` or exact decimal-string conversion at database boundaries.

## Reconciliation candidate discovery

For each scanned shop, discover unresolved purchase candidates from durable data, not solely from the current BillingPlan singular pack meter.

Candidate:

```text
RecoveryCreditPurchase.status = REQUESTED
linked UsageEvent metric = RECOVERY_CREDIT_PACK_PURCHASE
linked UsageEvent submission state is REPORTED (provider accepted submission)
```

Process by deterministic creation/id order and event handle.

The architecture invariant permits at most one unresolved purchase per shop+eventHandle. If multiple are observed, do not guess; emit `ambiguous` discrepancy and leave all unactivated.

## Candidate proof

For candidate P:

```text
expectedQuantityAfter = P.providerUsageQuantityBeforeSnapshot + 1
```

Read current Shopify provider state for P's exact `shopifyEventHandleSnapshot`.

Require:

- current provider context identity matches P snapshot;
- current provider plan handle matches P plan snapshot;
- current local/provider cycle remains provably the candidate's context;
- provider meter exists;
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
