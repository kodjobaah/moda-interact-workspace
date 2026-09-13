---
id: ARCH-010-DATABASE-014
architecture_id: ARCH-010
title: Materialise canonical recovery-credit purchase lifecycle and immutable purchase provenance
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 5
executor: copilot
claimed_at: '2026-09-13T11:26:59Z'
attempt: 2
depends_on:
- ARCH-010-DATABASE-013
enables:
- ARCH-010-SHOPIFY-014
- ARCH-010-BACKGROUND-021
- ARCH-010-BACKGROUND-022
- ARCH-010-SHOPIFY-025
- ARCH-010-ADMIN-002
- ARCH-010-ADMIN-003
- ARCH-010-SYSTEM-TEST-001
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-010-DATABASE-014: Materialise canonical recovery-credit purchase lifecycle and immutable purchase provenance

## Why this is a forward correction

`ARCH-010-DATABASE-007` and `ARCH-010-DATABASE-013` are accepted, immutable task history. Do not edit either task file.

The product definition has since been simplified before first production:

- refunds are **not arbitrary partial quantities** chosen by a merchant/Admin;
- a merchant withdraws one whole `RecoveryCreditPurchase` from future allocation and requests a refund of **all credits that ultimately remain unused** on that purchase;
- each purchase is an independent lifecycle object;
- a shop may simultaneously own many purchases in different states;
- the merchant may reactivate a withdrawn purchase until provider refund action begins;
- the purchase must retain immutable commercial provenance and purchase-time monetary value.

ARCH-010 remains pre-production. This task therefore updates the one unreleased first-production Prisma schema and clean baseline migration. Do **not** create compatibility schema merely to preserve development-only DATABASE-007 field shapes.

## Canonical `RecoveryCreditPurchase` lifecycle

The first-production purchase lifecycle has **exactly these business states**:

```text
REQUESTED
ACTIVE
COMPLETED
WITHDRAWN
REFUNDED
```

Semantics:

```text
REQUESTED
  merchant requested a recovery-credit pack;
  provider billing/valuation has not yet been durably confirmed;
  purchase is non-spendable and non-refundable.

ACTIVE
  provider purchase is confirmed and monetarily valued;
  purchase may fund new recovery reservations;
  merchant may request refund only when availableAmount > 0.

COMPLETED
  every credit from the purchase was successfully consumed;
  currentAmount = 0 and reservedAmount = 0;
  terminal and non-refundable.

WITHDRAWN
  merchant requested refund of this purchase's remaining credits;
  no new reservation may use the purchase;
  reservations created before withdrawal may still settle;
  merchant may reactivate only while the linked refund remains pre-provider-action.

REFUNDED
  provider refund/credit was confirmed for every credit that remained unused;
  currentAmount = 0 and reservedAmount = 0;
  terminal and non-spendable.
```

Operational provider uncertainty must not add extra purchase lifecycle values. Keep provider/reporting ambiguity in existing `UsageEvent.shopifyReportState`, refund workflow status/evidence, logs and operator workflows. A purchase that has not been provider-confirmed remains `REQUESTED` and non-spendable.

## Canonical per-purchase credit state

Replace the DATABASE-007 development-only partial-refund accounting shape with fields equivalent to:

```text
creditsGranted   immutable original pack quantity
currentAmount    credits from this purchase not yet successfully consumed/refunded
reservedAmount   subset of currentAmount currently reserved by in-flight conversations
version          optimistic-concurrency/CAS version
```

Retain existing immutable/history fields that still have meaning, such as purchase ID, shop, plan, event identity and activation time.

Do **not** keep first-production per-purchase:

```text
refundingQuantity
refundedQuantity
```

They are redundant under the whole-remaining-purchase refund model and create additional drift-prone sources of truth.

`committedQuantity` may be removed from the purchase lot if no accepted runtime requires it after BACKGROUND-022; successful consumption is represented by `currentAmount` decrement plus durable `UsageReservation`/`UsageEvent` history. If inspection proves a still-pending first-production consumer genuinely requires a per-lot committed aggregate, STOP and return that exact consumer to `moda_architect` rather than silently retaining two competing balance models.

### Amount invariants

Persist/check equivalent invariants:

```text
creditsGranted > 0
currentAmount >= 0
reservedAmount >= 0
reservedAmount <= currentAmount
version >= 0
```

Lifecycle invariants:

```text
REQUESTED  -> currentAmount = 0, reservedAmount = 0
ACTIVE     -> currentAmount > 0, reservedAmount <= currentAmount
WITHDRAWN  -> currentAmount > 0, reservedAmount <= currentAmount
COMPLETED  -> currentAmount = 0, reservedAmount = 0
REFUNDED   -> currentAmount = 0, reservedAmount = 0
```

Do not persist `availableAmount`.

For an ACTIVE purchase only:

```text
availableAmount = currentAmount - reservedAmount
```

A WITHDRAWN purchase may have the same arithmetic remainder, but it has **zero spendable capacity** because its lifecycle state blocks new reservations.

## Aggregate purchased-credit counter

Keep `ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS)` as the hot-path shop aggregate.

Its `refundingQuantity` remains useful as an **aggregate transient hold** for all unreserved credits belonging to WITHDRAWN purchase lots. It is not duplicated on each purchase.

Required aggregate parity conceptually:

```text
aggregate.refundingQuantity
  = SUM(currentAmount - reservedAmount)
    across WITHDRAWN purchases with a live pre/completing refund workflow
```

BACKGROUND-022 and SHOPIFY-025 own runtime maintenance of that invariant.

Do not add a shop-global purchase lifecycle state.

## Immutable purchase commercial provenance

Every provider-confirmed purchase must permanently identify the exact commercial context in which it was bought.

Add direct immutable fields/relations equivalent to:

```prisma
billingPeriodId String
billingPeriod   BillingPeriod @relation("RecoveryCreditPurchaseBillingPeriod", fields: [billingPeriodId], references: [id], onDelete: Restrict)

providerSubscriptionIdSnapshot String

providerUsageQuantityBeforeSnapshot Int
providerUsageCostBeforeSnapshot     Decimal
providerUsageCostCurrencyBeforeSnapshot String

providerUsageQuantityAfterSnapshot  Int?
providerUsageCostAfterSnapshot      Decimal?
providerUsageCostCurrencyAfterSnapshot String?

providerPurchaseAmount   Decimal?
providerPurchaseCurrency String?
providerValuationConfirmedAt DateTime?
providerPriceSnapshot Json?
```

Use repository/provider-safe precision and bounds. Do not silently coerce provider money into `Decimal(20,2)` if any first-production supported currency requires different precision. If the current provider contract cannot be represented exactly, STOP and return the evidence to `moda_architect`.

Add the reverse `BillingPeriod.recoveryCreditPurchases` relation.

### Provenance rules

At purchase creation, snapshot from one verified provider/local billing context:

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
```

At provider-confirmed activation, BACKGROUND-021 adds immutable after-state and final purchase amount/currency.

A purchase may become `ACTIVE` only when all required purchase-time valuation fields are present and consistent.

Current/later BillingPlan pricing, later provider subscription, later top-up meter price and later `BillingEconomicsSnapshot` are never refund authority.

## `RecoveryCreditRefund` first-production shape

A refund row represents a **request/workflow against one purchase**, not a merchant-selected quantity.

Retain one-to-many history from purchase -> refunds because a merchant may request, reactivate/cancel, then later request again. However, at most one refund may ever complete for a purchase because successful completion makes the purchase `REFUNDED`.

Replace arbitrary partial-refund request/approval quantity semantics with snapshots equivalent to:

```text
purchaseId
shopId
source = MERCHANT_UI | ADMIN as already supported
requestedByShopifyUserId when available

purchaseCreditsGrantedSnapshot
currentAmountAtRequestSnapshot
reservedAmountAtRequestSnapshot
availableAmountAtRequestSnapshot

billingPeriodIdSnapshot
providerSubscriptionIdSnapshot
planHandleSnapshot
eventHandleSnapshot
purchaseProviderAmountSnapshot
purchaseProviderCurrencySnapshot

finalCreditQuantity             nullable until provider-action boundary; system-derived from purchase.currentAmount
expectedProviderAmount          nullable until provider settlement boundary
expectedProviderCurrency        nullable until provider settlement boundary

status
requestKey
reason
version
provider action/evidence fields
createdAt/completedAt
```

Remove/deprecate first-production fields whose only meaning was arbitrary merchant/Admin quantity selection, including development-only `creditsRequested` / `creditsApproved` semantics. Do not preserve them as authorities merely because DATABASE-007 once introduced them.

### Request-time snapshots are not the final refund quantity

At request time:

```text
availableAmountAtRequestSnapshot = currentAmount - reservedAmount
```

This proves what was refundable at the exact winning CAS state.

It is **not** the final provider refund quantity because reservations that existed before withdrawal may later fail/release and return credits to the withdrawn purchase.

Final provider refund quantity is fixed only when:

```text
purchase.status = WITHDRAWN
purchase.reservedAmount = 0
purchase.currentAmount > 0
refund.status = REQUESTED
```

At that irreversible provider-action boundary:

```text
finalCreditQuantity = purchase.currentAmount
```

ADMIN-003 owns the transition and provider settlement.

## Refund workflow status

Retain the existing refund workflow values unless schema inspection proves a naming conflict:

```text
REQUESTED
PROVIDER_ACTION_REQUIRED
COMPLETED
REJECTED
CANCELLED
NEEDS_ATTENTION
```

Here `RecoveryCreditRefund.CANCELLED` means the refund request is terminal/cancelled (for example merchant reactivated the purchase or no credits remained). It is distinct from `RecoveryCreditPurchase.WITHDRAWN`, which means the purchase is withdrawn from new credit allocation pending refund.

Use bounded `reason` to distinguish terminal closure causes such as merchant reactivation, Admin rejection and no credits remaining.

## Database uniqueness

Add migration-level constraints/indexes proving at least:

1. at most one non-terminal refund per purchase in:

```text
REQUESTED
PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
```

2. at most one `COMPLETED` refund per purchase;
3. request keys remain globally unique;
4. useful indexes exist for merchant list views by `shopId,status,createdAt/activatedAt` and Admin refund queues.

Use PostgreSQL partial unique indexes where Prisma cannot express the invariant directly and add validators that prove the SQL exists.

## Purchase monetary refund basis

The final refund amount is always based on the immutable original purchase monetary value, never current pricing.

When Admin locks provider action and `reservedAmount == 0`:

```text
G = purchase.creditsGranted
R = purchase.currentAmount
M = purchase.providerPurchaseAmount
```

The expected provider refund is the exact proportional historical-purchase value for `R/G`, using a deterministic currency-safe rounding rule approved by the repository/provider representation.

There is no sequence of completed partial refunds for one purchase in first production. A successful refund makes the purchase terminal `REFUNDED`.

If provider money precision/rounding cannot be represented deterministically from current provider evidence, STOP rather than inventing a current-price or floating-point approximation.

## Clean baseline migration

ARCH-010 has not reached production. Update the existing first-production baseline migration so a clean empty database is created directly in this final shape.

Do not add:

```text
legacy compatibility columns
runtime dual-read/dual-write
second production migration solely to preserve development schema
```

Update ERD/schema docs and validation scripts.

## Required validation

At minimum prove:

1. enum contains exactly the five purchase lifecycle states;
2. REQUESTED defaults non-spendable with `currentAmount=0,reservedAmount=0`;
3. ACTIVE/WITHDRAWN require positive current amount and valid reservation bound;
4. COMPLETED/REFUNDED require zero current/reserved;
5. `availableAmount` is not persisted;
6. per-purchase `refundingQuantity/refundedQuantity` are absent from the final baseline;
7. direct BillingPeriod/provider-subscription provenance exists;
8. purchase valuation fields can prove immutable original amount/currency;
9. refund request-time current/reserved/available snapshots exist;
10. arbitrary merchant/Admin refund quantity fields are not first-production authorities;
11. one non-terminal refund per purchase is DB-enforced;
12. one completed refund per purchase is DB-enforced;
13. aggregate `ShopEntitlementCounter.refundingQuantity` remains available;
14. clean baseline migration + Prisma validation succeed;
15. ERD/schema validators reflect the final model;
16. `git diff --check` passes.

## Non-goals

Do not implement provider reconciliation, reservation runtime, merchant UI/actions, Admin settlement or system tests in this task.

## Stop conditions

STOP and return evidence to `moda_architect` if:

- an accepted first-production consumer outside the planned correction tasks requires the old arbitrary-partial-refund fields;
- exact provider monetary precision cannot be represented safely;
- a completed task file would need to be edited;
- a production database already exists and would require compatibility migration semantics.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql`
- `moda-interact-database/scripts/validate-first-production-baseline.mjs`
- `moda-interact-database/docs/generated/prisma-erd.puml`

### Work Completed
- Replaced the development purchase status enum with the canonical `REQUESTED`, `ACTIVE`, `COMPLETED`, `WITHDRAWN`, and `REFUNDED` lifecycle.
- Replaced per-purchase legacy quantity counters with `currentAmount` and `reservedAmount`, retaining aggregate `ShopEntitlementCounter.refundingQuantity`.
- Added restrictive billing-period linkage and immutable provider subscription, usage, valuation, amount, currency, and price provenance fields.
- Replaced arbitrary refund quantity fields with request-time amount snapshots and provider settlement fields.
- Added lifecycle/amount checks, partial unique refund indexes, migration foreign keys, validator coverage, and regenerated the ERD.
- Attempt 2 added the exact cross-merchant refund queue index, the purchase-grant balance upper bound, confirmed valuation checks for every post-REQUESTED state, required refund provenance snapshots, and provider settlement precision without a fixed two-decimal annotation.

### Validation Results
- `npm run prisma:validate` passed.
- `npm run prisma:generate` passed.
- `npm run test:first-production-baseline` passed.
- `npm run erd:puml` passed.
- `git diff --check` passed.
- The baseline migration remains clean: no `UPDATE`, `INSERT INTO`, or `DELETE FROM` statements.
- `npm ci` installed the lockfile-pinned dependencies in the isolated worktree; the install reported existing npm audit warnings that did not affect validation.

### Git / VCS
Task branch: `task/ARCH-010-DATABASE-014`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-010`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-010-task-ARCH-010-DATABASE-014`
  parent branch: `task/ARCH-010-DATABASE-014`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-010.worktrees/ARCH-010-DATABASE-014`
  implementation branch: `task/ARCH-010-DATABASE-014`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-database`
  commit: `abee18e`
  remote branch: `origin/task/ARCH-010-DATABASE-014`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/database/ARCH-010/DATABASE-014-recovery-credit-purchase-lifecycle-and-provenance.md`
  commit: `c6b6db0`
  remote branch: `origin/task/ARCH-010-DATABASE-014`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

Changes Requested

### Attempt 1 — Changes Requested

Attempt 1 is **not accepted**. The canonical five-state lifecycle and overall schema direction are correct, but the database invariants are not yet strong enough for downstream purchase/refund tasks.

This is an **Attempt 2 correction on the same task**. Do not create a replacement task. Do not modify any dependent repository. Do not redesign the lifecycle.

#### Attempt 2 implementation scope — exact files

Implementation changes are limited to:

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql`
- `moda-interact-database/scripts/validate-first-production-baseline.mjs`
- `moda-interact-database/docs/generated/prisma-erd.puml` — generated output only
- this task file — execution metadata and Completion Report only

Do **not** create a second migration. ARCH-010 is still pre-production and this task owns correction of the existing clean first-production baseline.

Do **not** modify `DATABASE-007`, `DATABASE-013`, BACKGROUND, SHOPIFY, ADMIN, SHARED, GATEWAY, SYSTEM-TEST, architecture documents, or another task file.

Do **not** add another `RecoveryCreditPurchaseStatus`. The purchase enum must remain exactly:

```text
REQUESTED
ACTIVE
COMPLETED
WITHDRAWN
REFUNDED
```

#### Correction 1 — add the exact Admin refund-queue index

In `prisma/schema.prisma`, inside `model RecoveryCreditRefund`, add exactly:

```prisma
@@index([status, createdAt, id])
```

Keep the existing shop-scoped and purchase-scoped indexes.

In the clean baseline migration, create the matching PostgreSQL index:

```sql
CREATE INDEX "RecoveryCreditRefund_status_createdAt_id_idx"
ON "billing"."RecoveryCreditRefund"("status", "createdAt", "id");
```

Do not substitute a shop-leading index. This index exists specifically for the cross-merchant Admin queue in `ARCH-010-ADMIN-002`.

Update `scripts/validate-first-production-baseline.mjs` so validation fails if either the Prisma index or this migration index is absent.

#### Correction 2 — purchase balances must never exceed the immutable grant

Keep `RecoveryCreditPurchase_creditsGranted_positive`.

Strengthen the existing `RecoveryCreditPurchase_amounts_non_negative` migration constraint so it enforces all of the following:

```text
currentAmount >= 0
currentAmount <= creditsGranted
reservedAmount >= 0
reservedAmount <= currentAmount
version >= 0
```

The resulting SQL condition must include:

```sql
"currentAmount" <= "creditsGranted"
```

Do not add another mutable balance field. Do not reintroduce `committedQuantity`, per-purchase `refundingQuantity`, or per-purchase `refundedQuantity`.

Update the baseline validator to fail if `currentAmount <= creditsGranted` is not DB-enforced.

#### Correction 3 — confirmed purchase valuation must survive every post-REQUESTED lifecycle state

The current migration constraint named:

```text
RecoveryCreditPurchase_active_valuation_complete
```

is insufficient because it protects only `ACTIVE` rows.

Replace it with a constraint named exactly:

```text
RecoveryCreditPurchase_confirmed_valuation_complete
```

The constraint must allow `REQUESTED` rows without provider-confirmed after/final valuation. For **every non-REQUESTED state** (`ACTIVE`, `COMPLETED`, `WITHDRAWN`, `REFUNDED`), it must require all of the following:

```text
providerUsageQuantityAfterSnapshot IS NOT NULL
providerUsageCostAfterSnapshot IS NOT NULL
providerUsageCostCurrencyAfterSnapshot IS NOT NULL
providerPurchaseAmount IS NOT NULL
providerPurchaseAmount > 0
providerPurchaseCurrency IS NOT NULL
providerValuationConfirmedAt IS NOT NULL
providerPriceSnapshot IS NOT NULL
providerUsageCostCurrencyBeforeSnapshot = providerUsageCostCurrencyAfterSnapshot
providerUsageCostCurrencyAfterSnapshot = providerPurchaseCurrency
providerUsageCostAfterSnapshot > providerUsageCostBeforeSnapshot
providerPurchaseAmount = providerUsageCostAfterSnapshot - providerUsageCostBeforeSnapshot
```

Use a `CHECK` whose outer shape is equivalent to:

```sql
CHECK (
  "status" = 'REQUESTED'
  OR (
    ...all confirmed-valuation requirements above...
  )
)
```

Do **not** make the nullable after/final valuation fields globally `NOT NULL` in Prisma, because `REQUESTED` purchases must still be representable before provider confirmation.

Do **not** calculate the purchase amount from current `BillingPlan` pricing or any later price. This constraint only verifies the already-snapshotted provider before/after values.

Update the baseline validator to assert the new constraint name and every required condition above, and to reject the old ACTIVE-only constraint as the final baseline authority.

#### Correction 4 — refund request provenance must be complete and immutable at row creation

In `model RecoveryCreditRefund` in `prisma/schema.prisma`, change:

```prisma
purchaseProviderAmountSnapshot   Decimal?
purchaseProviderCurrencySnapshot String? @db.VarChar(3)
```

to exactly:

```prisma
purchaseProviderAmountSnapshot   Decimal
purchaseProviderCurrencySnapshot String @db.VarChar(3)
```

In the clean baseline migration, these columns must therefore be:

```sql
"purchaseProviderAmountSnapshot" DECIMAL(65,30) NOT NULL,
"purchaseProviderCurrencySnapshot" VARCHAR(3) NOT NULL,
```

Do not add defaults. The refund creator must copy these values from the already provider-confirmed purchase.

Strengthen `RecoveryCreditRefund_snapshot_amounts` so it enforces all of the following:

```text
purchaseCreditsGrantedSnapshot > 0
purchaseProviderAmountSnapshot > 0
currentAmountAtRequestSnapshot >= 0
currentAmountAtRequestSnapshot <= purchaseCreditsGrantedSnapshot
reservedAmountAtRequestSnapshot >= 0
reservedAmountAtRequestSnapshot <= currentAmountAtRequestSnapshot
availableAmountAtRequestSnapshot = currentAmountAtRequestSnapshot - reservedAmountAtRequestSnapshot
availableAmountAtRequestSnapshot > 0
finalCreditQuantity IS NULL OR finalCreditQuantity > 0
finalCreditQuantity IS NULL OR finalCreditQuantity <= currentAmountAtRequestSnapshot
expectedProviderAmount IS NULL OR expectedProviderAmount >= 0
```

The upper bound for `finalCreditQuantity` must be `currentAmountAtRequestSnapshot`, **not** `availableAmountAtRequestSnapshot`. Existing reservations may release after withdrawal, so the final refundable quantity may legitimately be greater than the request-time available amount, but it cannot exceed the request-time current amount.

Do not reintroduce `creditsRequested`, `creditsApproved`, a merchant-selected quantity, a percentage, or any arbitrary partial-refund authority.

Update the baseline validator to prove the required/non-null snapshot fields and every amount invariant above.

#### Correction 5 — remove the remaining fixed two-decimal provider settlement column

In `model RecoveryCreditRefund`, replace:

```prisma
providerAmount Decimal? @db.Decimal(20, 2)
```

with exactly:

```prisma
providerAmount Decimal?
```

Do not add another native precision annotation.

In the clean baseline migration, change:

```sql
"providerAmount" DECIMAL(20,2),
```

to:

```sql
"providerAmount" DECIMAL(65,30),
```

This intentionally aligns actual provider settlement precision with `providerPurchaseAmount`, `purchaseProviderAmountSnapshot`, and `expectedProviderAmount` in the current first-production Prisma representation.

Do not round or truncate to two decimal places in DATABASE-014. Do not introduce floating-point storage.

Update the baseline validator to fail if `providerAmount` is still `DECIMAL(20,2)` / `@db.Decimal(20, 2)`.

#### Correction 6 — regenerate the ERD, do not hand-edit it

After the Prisma schema and baseline migration corrections are complete, regenerate:

```text
moda-interact-database/docs/generated/prisma-erd.puml
```

using the repository's existing `npm run erd:puml` command.

Do not manually edit generated ERD output to make validation pass.

#### Correction 7 — Attempt 2 worktree/VCS evidence must be recorded prospectively

Do **not** invent or retrospectively reconstruct missing Attempt 1 synchronization evidence.

When Attempt 2 is claimed, reuse the canonical dedicated task worktrees and perform the mandatory start-of-attempt synchronization before implementation changes.

The Attempt 2 Completion Report must contain this exact evidence structure with the actual launcher-resolved paths and actual outcomes:

```text
Physical worktree isolation:
  canonical workspace root: <actual path>
  parent worktree: <actual canonical parent task worktree>
  parent branch: task/ARCH-010-DATABASE-014
  implementation worktree: <actual canonical implementation task worktree>
  implementation branch: task/ARCH-010-DATABASE-014
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Record only outcomes actually observed during Attempt 2.

If either canonical worktree is mapped to the wrong repository/branch, another task worktree is being reused, the worktree is unexpectedly dirty, a task branch diverges from its remote, or merging `origin/main` conflicts, STOP using the error/stop behaviour in `docs/agent-worktree-isolation-policy.md`. Do not repair this by switching a shared checkout, rebasing published history, force-pushing, resetting another task, or deleting another worktree.

#### Correction 8 — required Attempt 2 validation

Extend `scripts/validate-first-production-baseline.mjs` for Corrections 1–5. Do not satisfy this review only by changing source text; the validator must protect the final baseline invariants.

From the canonical implementation worktree run, in this order:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test:first-production-baseline
npm run erd:puml
git diff --check
```

All five commands must pass for Attempt 2 to return to `review`.

Also verify that the clean baseline migration still contains no data-migration DML:

```text
no UPDATE
no INSERT INTO
no DELETE FROM
```

Record each command and result in the Completion Report.

Commit and push the implementation task branch, then update the parent Completion Report/status, commit and push the parent task branch according to the normal task protocol. Record the new implementation commit and new parent Completion Report commit.

#### Explicit non-goals for Attempt 2

Do not implement:

- purchase creation or provider reconciliation runtime;
- BACKGROUND-021 activation logic;
- BACKGROUND-022 reservation/refund concurrency;
- merchant purchase/refund actions or UI;
- Admin provider settlement;
- system tests;
- new observability;
- compatibility schema for the development-only DATABASE-007 model.

Do not start or modify any task listed under `enables`.

#### Attempt 2 stop conditions

STOP and return the same DATABASE-014 task to `moda_architect` without implementing an alternative design if any of the following is true:

1. an accepted first-production consumer requires one of the removed legacy purchase/refund fields;
2. the provider monetary values cannot be represented exactly by the repository's current Decimal representation;
3. satisfying these corrections requires a second production migration instead of correcting the clean baseline;
4. satisfying these corrections requires changing a completed task or another repository;
5. the canonical task worktree isolation/synchronization rules cannot be satisfied;
6. any required validation command fails because of a change made by Attempt 2.

After successful implementation and validation, set this same task to `status: review`, update the Completion Report, push both task branches, and STOP for `moda_architect` review. Do not execute downstream work.

### Reviewed Files

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql`
- `moda-interact-database/scripts/validate-first-production-baseline.mjs`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `docs/decisions/database/ARCH-010/DATABASE-014-recovery-credit-purchase-lifecycle-and-provenance.md`
- `docs/decisions/admin/ARCH-010/ADMIN-002-triage-partial-topup-refund-requests.md`
- `docs/decisions/admin/ARCH-010/ADMIN-003-approve-settle-partial-topup-refunds.md`
- `docs/decisions/background/ARCH-010/BACKGROUND-021-confirm-purchase-commercial-value.md`
- `docs/decisions/shopify/ARCH-010/SHOPIFY-014-topup-purchase-lifecycle-adapter.md`

### Validation Reviewed

- Independent `node scripts/validate-first-production-baseline.mjs`: passed against Attempt 1 in the supplied review snapshot.
- The Attempt 1 Completion Report records `npm run prisma:validate`, `npm run prisma:generate`, `npm run test:first-production-baseline`, `npm run erd:puml`, and `git diff --check` as passed.
- Clean-baseline migration DML scan found no `UPDATE`, `INSERT INTO`, or `DELETE FROM` statements.
- Cross-repository source inspection found no current non-document first-production consumer requiring the removed `PENDING_BILLING`, purchase-level `NEEDS_ATTENTION/CANCELLED`, `creditsRequested/creditsApproved`, or per-purchase legacy quantity fields.

### Architecture Conformance

The exact five-state purchase lifecycle, removal of arbitrary merchant-selected refund quantities, direct BillingPeriod/provider provenance, request-time refund snapshots, aggregate-only `ShopEntitlementCounter.refundingQuantity`, and partial unique refund indexes conform to the agreed ARCH-010 architecture.

Acceptance is blocked only by the database integrity, queue-index, precision and durable execution-evidence corrections defined above.

### Follow-up

Reclaim **this same task** as Attempt 2. Leave `attempt: 1` in this overlay; the authorized Attempt 2 claim must increment it exactly once. All tasks depending on `ARCH-010-DATABASE-014` remain gated until this task is architect-accepted and `status: complete`.
