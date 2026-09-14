---
id: ARCH-010-ADMIN-002
architecture_id: ARCH-010
title: Review merchant recovery-credit purchase refund requests
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 81
executor: null
claimed_at: null
attempt: 3
depends_on:
- ARCH-010-DATABASE-014
- ARCH-010-BACKGROUND-022
- ARCH-010-SHOPIFY-025
- ARCH-010-SHARED-008
- ARCH-010-ADMIN-010
enables:
- ARCH-010-ADMIN-003
created: 2026-09-11
updated: 2026-09-14
---

# ARCH-010-ADMIN-002: Review merchant recovery-credit purchase refund requests

## Product correction

The old definition expected Admin to convert a merchant support message into an arbitrary partial-credit refund quantity. That design is superseded before implementation.

The merchant now creates the durable request directly through SHOPIFY-025 by withdrawing one exact ACTIVE `RecoveryCreditPurchase`. There is no Admin-entered refund quantity.

This task owns the internal review/queue/read experience only. ADMIN-003 owns the irreversible provider-action boundary and settlement.

## Objective

Give authorized internal Admin users a deterministic queue/detail view of merchant-created `RecoveryCreditRefund` requests and their exact purchase-lot state.

Admin must be able to understand:

```text
which shop requested it
which exact RecoveryCreditPurchase was withdrawn
original purchase/subscription/BillingPeriod/plan/meter provenance
original purchase amount/currency
request-time current/reserved/available snapshots
current purchase currentAmount/reservedAmount
whether existing reservations are still draining
whether provider action may begin
refund workflow/history
```

Admin does not choose how many credits to refund.

## Authorization

Use existing internal Admin authorization.

ADMIN and SUPER_ADMIN may view/review if that matches existing support/billing conventions.

Only SUPER_ADMIN may perform ADMIN-003 provider settlement actions.

Merchants never access Admin routes.

## Queue

Add/reuse a bounded paginated queue for refund workflows. Default page 20, max 50 unless repository convention is stricter.

Useful filters:

```text
REQUESTED
READY_FOR_PROVIDER_ACTION (derived: refund REQUESTED + purchase WITHDRAWN + reservedAmount=0 + currentAmount>0)
WAITING_FOR_RESERVATIONS (derived: refund REQUESTED + purchase WITHDRAWN + reservedAmount>0)
PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
COMPLETED
REJECTED
CANCELLED
```

`READY_FOR_PROVIDER_ACTION` and `WAITING_FOR_RESERVATIONS` are Admin read-model labels, not new database refund statuses.

Every query must be database-scoped/paginated; do not load all shops then filter.

## Exact request detail

For one request display at minimum:

```text
refund ID/status/createdAt/source
merchant/shop identity allowed by Admin conventions
requestedByShopifyUserId when present

purchase ID/status
purchase created/activated date
creditsGranted
currentAmount
reservedAmount
current unreserved amount = currentAmount - reservedAmount

currentAmountAtRequestSnapshot
reservedAmountAtRequestSnapshot
availableAmountAtRequestSnapshot

billingPeriod/provider-subscription/plan/event snapshots
original providerPurchaseAmount/providerPurchaseCurrency
provider before/after valuation evidence in a bounded operator-safe form

existing exact UsageReservations if current Admin patterns permit bounded drill-down
historical refund attempts for this purchase
```

Do not display current BillingPlan price as refund authority.

## State interpretation

### Purchase WITHDRAWN + reservedAmount > 0

Display clearly:

```text
Waiting for in-flight conversations to settle.
Provider refund action MUST NOT start yet.
```

Existing reservations may commit or release. A release can increase the final refund quantity; a commit can reduce it.

### Purchase WITHDRAWN + reservedAmount = 0 + currentAmount > 0

Display:

```text
Ready for provider action.
Final credit quantity will be locked by ADMIN-003 from currentAmount.
```

Do not let ADMIN-002 persist a quantity.

### Purchase COMPLETED

There is nothing left to refund. The live request should already be terminally closed by BACKGROUND-022/SHOPIFY-025 race handling. If an inconsistent non-terminal refund remains, surface `DATA_INTEGRITY_ATTENTION`; do not repair it in this read task.

### Purchase ACTIVE

A non-terminal refund with ACTIVE purchase is inconsistent unless it is in the middle of an atomic action that cannot be observed after commit. Surface integrity attention; do not invent a hold.

### Purchase REFUNDED

Show terminal historical settlement; no new action.

## No support-message prerequisite

A `MerchantSupportMessage` is no longer required to create the refund request.

If the merchant separately contacted support, Admin may display/link that thread through existing support tooling, but it is contextual only and must not become refund identity/quantity authority.

Do not create a `RecoveryCreditRefund` from NLP, keywords or support triage in this task.

## No quantity controls

The Admin UI must contain **no** control equivalent to:

```text
creditsRequested input
creditsApproved input
partial amount selector
percentage selector
```

The product rule is always: refund every credit that remains unused on the exact withdrawn purchase once its existing reservations have drained.

## Merchant cancellation/reactivation visibility

If the merchant reactivated the purchase before provider action, the refund becomes terminal `CANCELLED` with a bounded reason. Show that history; do not reopen it automatically.

A later refund request against the reactivated ACTIVE purchase creates a new refund row through SHOPIFY-025.

## Required tests

At minimum prove:

1. Admin authorization protects queue/detail;
2. queue pagination/filtering is bounded;
3. merchant-created requests appear without support message;
4. request-time snapshots and current purchase amounts are both shown distinctly;
5. WITHDRAWN + reserved>0 is labelled waiting and cannot start provider action here;
6. WITHDRAWN + reserved=0 + current>0 is labelled ready;
7. no quantity/percentage/money-entry control exists in ADMIN-002;
8. current plan/top-up price is not presented as refund authority;
9. merchant-reactivated terminal refund history is visible;
10. completed/refunded purchases cannot be triaged into another refund here;
11. inconsistent ACTIVE/non-terminal refund fails visibly rather than being auto-repaired;
12. cross-shop data isolation/Admin authorization tests pass;
13. focused tests, repository validation/build and `git diff --check` pass.

## Non-goals

Do not create merchant refund requests, mutate purchase holds, choose provider action, calculate final provider refund amount, confirm provider settlement, or call Shopify.

## Stop conditions

STOP if SHOPIFY-025 does not create durable merchant refund requests, if DATABASE-014 fields are unavailable, or if implementing the queue would require recreating the old arbitrary-partial-refund model.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-admin/src/lib/admin/recovery-credit-refunds.ts`
- `moda-interact-admin/src/lib/admin/types.ts`
- `moda-interact-admin/src/components/admin/recovery-credit-refunds.tsx`
- `moda-interact-admin/src/components/admin/billing-tabs.tsx`
- `moda-interact-admin/src/app/(protected)/billing/page.tsx`
- `moda-interact-admin/src/i18n/locales/en.json`
- `moda-interact-admin/src/i18n/required-keys.ts`
- `moda-interact-admin/tests/security/admin-recovery-credit-refunds.test.mjs`
- `moda-interact-admin/tests/security/admin-billing-progressive-disclosure.test.mjs`

### Work Completed
- Added an authorized, read-only, database-paginated recovery-credit refund queue with default page size 20 and maximum page size 50.
- Added derived `READY_FOR_PROVIDER_ACTION` and `WAITING_FOR_RESERVATIONS` labels from the exact withdrawn purchase state; invalid active/non-terminal combinations surface integrity attention.
- Added bounded refund detail data for request-time snapshots, current purchase amounts, billing-period/provider/plan provenance, provider valuation evidence, support context identity, reservation history and refund history.
- Attempt 2 audit found a partial requirement gap: the first implementation loaded billing-period dates/plan provenance, provider usage before/after valuation evidence, support-context identity and refund-history fields but did not render all of them in the detail drawer. The drawer now displays those fields, including bounded refund-history reason, amount/currency and created time.
- Added the billing Refund requests tab and detail drawer. The UI has no quantity, percentage, money-entry, approval or provider-settlement control and explicitly treats plan/top-up price as non-authoritative evidence.
- Preserved merchant-created request identity; no support-message prerequisite, NLP creation path, Shopify call, purchase mutation or provider action was added.
- Updated the directly affected billing-view and i18n contract tests and added focused refund triage security coverage.
- Attempt 3 corrected the derived `NEEDS_ATTENTION` filter so persisted attention rows and `REQUESTED` rows with invalid purchase states or zero-credit withdrawn balances are database-filtered into the same operator view as `queueStatus()`. Valid waiting and ready withdrawn states remain excluded from this filter.

### Validation Results
- `node --test tests/security/admin-recovery-credit-refunds.test.mjs`: passed, 2 tests.
- `node --test tests/security/admin-billing-progressive-disclosure.test.mjs tests/security/admin-internationalization.test.mjs tests/security/admin-recovery-credit-refunds.test.mjs`: passed, 18 tests.
- `npm exec tsc -- --noEmit`: passed after `npm run prisma:generate`; the first post-edit run caught and the focused rerun confirmed the optional support-context identifier fix.
- `npm run test:unit`: passed, 42 tests.
- `npm test`: passed, 173 tests; 0 failures.
- `npm run lint`: passed with 2 existing warnings in `src/components/admin/queue-monitor.tsx` for missing `refresh` hook dependencies; no errors.
- `npm run build`: passed. Existing non-blocking BullMQ webpack warnings remain for an expression dependency and optional `@valkey/valkey-glide` resolution.
- `git diff --check`: passed.
- Attempt 3 focused predicate assertions: passed; the test covers persisted `NEEDS_ATTENTION`, `REQUESTED` + invalid `REQUESTED`/`ACTIVE`/`COMPLETED`/`REFUNDED`, and zero-credit `WITHDRAWN` attention branches while retaining the valid waiting/ready predicates.

### Two-Pass Audit
- First pass: all queue/detail authorization and merchant-route boundaries, shop isolation, database pagination/sorting, lifecycle derivation, snapshots versus live values, provenance, support context, reservation/refund history, read-only behavior, UI controls, non-goals, and existing validation coverage were present. One production omission was found: derived invalid `REQUESTED` rows were shown as `NEEDS_ATTENTION` in the queue but excluded by the `NEEDS_ATTENTION` database filter.
- Correction: added the explicit database `OR` predicate in `src/lib/admin/recovery-credit-refunds.ts` and focused assertions in `tests/security/admin-recovery-credit-refunds.test.mjs`. No schema, database, Shopify, Background, Shared, provider, or ADMIN-003 changes were required.
- Second independent pass: the filter now includes persisted `NEEDS_ATTENTION`, `REQUESTED` + invalid `REQUESTED`/`ACTIVE`/`COMPLETED`/`REFUNDED`, and invalid zero-credit `WITHDRAWN` rows; valid waiting and ready withdrawn states remain excluded. Queue queries remain database-scoped and bounded, and no mutation, provider action, quantity control, or settlement behavior was added. All task requirements pass. Residual validation limitation: focused security tests inspect the generated Prisma predicate rather than using a database fixture, consistent with the Architect Review allowance; full existing tests remain green.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-002`.
- Implementation branch: `task/ARCH-010-ADMIN-002`.
- Implementation commits: `cd0eda5` (`feat(admin): triage recovery credit refund requests`), `9e571cd5076b3783f6a8845ba860c3ab7d2e9fd7` (`fix(admin): complete refund triage detail evidence`), `bb7ccc10ec3aadfe19693143f47d6a7c2ad922a7` (`fix(admin): include derived refund attention states`).
- Implementation branch pushed to `origin/task/ARCH-010-ADMIN-002`.
- Parent report is being published from `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-002` on the mirrored `task/ARCH-010-ADMIN-002` branch.

### Architect Review
Ready for architect review. No unresolved task-scope blocker identified.

## Architect Review — Attempt 2

### Status

**Changes Requested — one functional queue-filter correction only**

This review intentionally prioritises operator/runtime functionality over exhaustive
test coverage.

The Attempt-2 implementation is broadly accepted.

Accepted behavior includes:

```text
ADMIN / SUPER_ADMIN authenticated read access through existing platform-admin auth
merchant users cannot access Admin routes
database-bounded queue pagination (default 20, maximum 50)
merchant-created refund requests require no support message
request-time snapshots remain distinct from current purchase balances
WITHDRAWN + reservedAmount > 0 -> WAITING_FOR_RESERVATIONS
WITHDRAWN + reservedAmount = 0 + currentAmount > 0 -> READY_FOR_PROVIDER_ACTION
ACTIVE / COMPLETED / REFUNDED invalid non-terminal combinations are surfaced as
integrity attention rather than repaired
terminal CANCELLED / COMPLETED / REJECTED / NEEDS_ATTENTION history remains visible
detail drawer exposes purchase/BillingPeriod/provider/plan/event provenance
provider before/after valuation evidence is bounded for operator display
support context remains contextual only
bounded reservation/refund history is read-only
no refund quantity / percentage / money-entry control exists
current plan/top-up price is explicitly non-authoritative
no Shopify call, provider action, purchase mutation, refund creation, or settlement
is introduced
```

The Attempt-2 correction that completed the detail drawer is accepted and MUST NOT be
redesigned.

One operator-facing read-model defect remains.

---

### Finding — the `NEEDS_ATTENTION` filter omits rows that the queue itself derives as attention

The queue derives:

```ts
if (refund.status === REQUESTED) {
  if (purchase is valid WITHDRAWN waiting/ready) {
    ...
  }

  return "NEEDS_ATTENTION";
}
```

Therefore examples such as:

```text
refund REQUESTED + purchase ACTIVE
refund REQUESTED + purchase COMPLETED
refund REQUESTED + purchase REFUNDED
refund REQUESTED + purchase REQUESTED
refund REQUESTED + purchase WITHDRAWN with currentAmount <= 0 and no reservations
```

are rendered as:

```text
queueStatus = NEEDS_ATTENTION
```

and the detail drawer correctly says:

```text
Data integrity attention: this request is not in a valid withdrawn-purchase state.
```

However the database filter currently handles:

```text
status = NEEDS_ATTENTION
```

by returning only:

```ts
{ status: RecoveryCreditRefundStatus.NEEDS_ATTENTION }
```

That excludes the derived integrity-attention rows above because their persisted
refund status is still `REQUESTED`.

Functionally this means:

```text
operator sees an anomaly in All/Requested
-> operator selects Needs attention
-> the anomaly disappears
```

This contradicts the task's triage objective and the explicit requirement to surface
invalid ACTIVE/COMPLETED/REFUNDED non-terminal states for operator attention.

This is a production read-model defect, not a request for broader test coverage.

---

### Required correction

Modify only:

```text
moda-interact-admin/src/lib/admin/recovery-credit-refunds.ts
```

Make the database `NEEDS_ATTENTION` filter match the same semantic set that
`queueStatus(...)` labels as `NEEDS_ATTENTION`.

The query must include:

```text
A. persisted refund.status = NEEDS_ATTENTION

OR

B. refund.status = REQUESTED
   AND the purchase is not one of the two valid withdrawn states:
     1. WITHDRAWN + reservedAmount > 0
     2. WITHDRAWN + reservedAmount = 0 + currentAmount > 0
```

Prefer an explicit Prisma predicate rather than loading rows and filtering in memory.

A deterministic equivalent is:

```ts
if (status === "NEEDS_ATTENTION") {
  return {
    OR: [
      {
        status: RecoveryCreditRefundStatus.NEEDS_ATTENTION,
      },
      {
        status: RecoveryCreditRefundStatus.REQUESTED,
        purchase: {
          status: {
            in: [
              RecoveryCreditPurchaseStatus.REQUESTED,
              RecoveryCreditPurchaseStatus.ACTIVE,
              RecoveryCreditPurchaseStatus.COMPLETED,
              RecoveryCreditPurchaseStatus.REFUNDED,
            ],
          },
        },
      },
      {
        status: RecoveryCreditRefundStatus.REQUESTED,
        purchase: {
          status: RecoveryCreditPurchaseStatus.WITHDRAWN,
          reservedAmount: 0,
          currentAmount: { lte: 0 },
        },
      },
    ],
  };
}
```

Any equivalent database-scoped predicate is acceptable if it exactly mirrors the
current derived queue semantics.

Do not change:

```text
READY_FOR_PROVIDER_ACTION
WAITING_FOR_RESERVATIONS
REQUESTED raw-status filter
persisted refund status
database schema
refund/purchase lifecycle
```

Do not create a new database enum such as `DATA_INTEGRITY_ATTENTION`.

`DATA_INTEGRITY_ATTENTION` remains a read-model/operator interpretation, not persisted
workflow state.

---

### Functional regression evidence required

No broad test expansion is required.

Update only the focused refund triage test(s), preferably:

```text
moda-interact-admin/tests/security/admin-recovery-credit-refunds.test.mjs
```

or an existing service-level test if one already exercises Prisma arguments.

Prove the resulting `NEEDS_ATTENTION` query includes:

```text
persisted NEEDS_ATTENTION
REQUESTED + ACTIVE
REQUESTED + COMPLETED
REQUESTED + REFUNDED
REQUESTED + invalid zero-credit WITHDRAWN
```

and excludes the two valid REQUESTED withdrawn queue states:

```text
WITHDRAWN + reservedAmount > 0
WITHDRAWN + reservedAmount = 0 + currentAmount > 0
```

The test may validate the generated Prisma predicate or the actual bounded query
behavior. Do not build a large new integration fixture solely for this correction.

Existing authorization/detail/read-only tests must continue to pass.

---

### Accepted Attempt-2 work — do not churn

Do not redesign:

```text
moda-interact-admin/src/components/admin/recovery-credit-refunds.tsx
moda-interact-admin/src/lib/admin/types.ts
moda-interact-admin/src/components/admin/billing-tabs.tsx
moda-interact-admin/src/app/(protected)/billing/page.tsx
moda-interact-admin/src/i18n/*
```

unless a mechanical import/type adjustment is required by the narrow filter change.

Preserve:

```text
bounded pagination
existing queue status names
exact detail drawer evidence
support-context read-only display
reservation/refund-history bounds
Admin authentication
no quantity/provider controls
no mutation/provider behavior
```

---

### Attempt-3 allowed scope

Production:

```text
moda-interact-admin/src/lib/admin/recovery-credit-refunds.ts
```

Tests:

```text
moda-interact-admin/tests/security/admin-recovery-credit-refunds.test.mjs
```

plus this task/Completion Report.

If the correction requires schema, Shopify, Background, Shared, provider, or ADMIN-003
changes, STOP and return the exact limitation to `moda_architect`.

---

### Attempt-3 validation

Prioritise the functional slice:

```bash
cd moda-interact-admin

node --test tests/security/admin-recovery-credit-refunds.test.mjs
npm exec tsc -- --noEmit
npm run build
git diff --check
```

Run the existing broader tests only for regression awareness.

The two pre-existing queue-monitor lint warnings and existing BullMQ build warnings
remain non-blocking if unchanged.

Do not spend Attempt 3 fixing unrelated warnings.

---

### Workflow / Completion Report

Preserve immutable Attempt-2 publication history:

```text
Attempt-2 implementation:
9e571cd5

Attempt-2 parent report:
d438b2d7
```

Also preserve the earlier implementation commit:

```text
cd0eda5
```

Record full SHAs from repository history where available.

Return this SAME task through `/moda-task`.

Preserve:

```text
attempt: 2
```

The next authorised claim must increment to **Attempt 3 exactly once**.

Attempt 3 may return to review when:

```text
1. the Needs attention filter returns both persisted NEEDS_ATTENTION rows and derived
   integrity-attention REQUESTED rows;
2. valid READY_FOR_PROVIDER_ACTION / WAITING_FOR_RESERVATIONS rows remain excluded
   from Needs attention;
3. pagination remains database-scoped and bounded;
4. no mutation/provider/quantity behavior is introduced;
5. focused validation passes;
6. status = review, executor = null, claimed_at = null;
7. both worktrees are clean and pushed.
```

Then STOP and return to `moda_architect`.

`ARCH-010-ADMIN-003` remains gated until `ADMIN-002` is architect-accepted Complete.
