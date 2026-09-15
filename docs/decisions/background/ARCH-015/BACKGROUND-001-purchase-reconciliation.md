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
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 1
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

Implementation commit: `6c3e92779b537ccfd073ed2a7c32ff674c2921c9` on `task/ARCH-015-BACKGROUND-001`, pushed to `origin`.

### Implementation Summary

- Shopify Partner parsing retains tiered usage items when `price.active` is false and preserves provider quantities as exact decimal-compatible values.
- Billing reconciliation forwards the complete provider usage snapshot and current cycle evidence.
- Recovery-credit activation discovers reported `REQUESTED` candidates from durable purchase/event data, proves each candidate against its immutable provider plan, event handle, subscription, cycle, quantity, currency, and cost baseline, and activates only proven candidates in one Serializable transaction.
- Distinct event handles are processed independently; duplicate unresolved candidates for one handle remain ambiguous. Missing exact meters, mismatched context, quantity, currency, cycle, or cost leave candidates `REQUESTED`. Aggregate grants and capacity-resume scheduling remain transactional/best-effort respectively.

### Acceptance Mapping

- Provider parser rule: implemented and covered by inactive tiered-item test.
- Durable candidate discovery and reported UsageEvent filtering: preserved and covered by focused purchase-service tests.
- Exact candidate proof and Decimal quantity arithmetic: implemented, including fractional baseline and missing-handle fail-closed tests.
- Zero-cost activation, quantity/currency/context mismatch handling, duplicate same-handle ambiguity, distinct-handle activation, aggregate idempotency, and resume scheduling: implemented and covered by focused tests.
- No schema changes, synchronous provider correction, or new purchase status introduced.

### Validation

- `npm test -- tests/unit/services/recovery-credit-purchase.service.test.ts tests/unit/services/recovery-credit-purchase.resume-hint.test.ts tests/unit/services/billing-reconciliation.service.test.ts tests/unit/providers/shopify-partner-billing.provider.test.ts tests/unit/services/shopify-usage-event-publisher.service.test.ts`: passed, 5 files / 101 tests.
- `npm run build`: passed; Prisma client generation and TypeScript compilation completed successfully.
- `npm run test:unit`: 57 files, 918 passed / 2 failed / 920 total. The two failures are pre-existing observability baseline mismatches in `tests/unit/runtime/observability-startup.test.ts`: expected worker close-resource source text differs from current implementation, and the test expects shared runtime `0.9.0` while the repository declares `0.11.0`. No task-owned test failed.
- `git diff --check`: passed. Editor diagnostics for all seven changed files: no errors.

### Worktree and Submodule Evidence

- Prepared implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-BACKGROUND-001`.
- Implementation branch: `task/ARCH-015-BACKGROUND-001`; clean after commit and pushed at `6c3e92779b537ccfd073ed2a7c32ff674c2921c9`.
- Prepared parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-BACKGROUND-001`.
- Prepared execution verified recursive submodules were initialized and matched their recorded commits; no submodule gitlink was staged or changed by this task.

### Limitations

The repository-wide unit suite remains blocked only by the two documented/pre-existing observability startup expectation mismatches listed above. Focused task validation and production build are green.
