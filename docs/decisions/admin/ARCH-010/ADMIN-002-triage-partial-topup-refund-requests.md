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
executor: copilot
claimed_at: 2026-09-14T20:03:33Z
attempt: 2
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

### Validation Results
- `node --test tests/security/admin-recovery-credit-refunds.test.mjs`: passed, 2 tests.
- `node --test tests/security/admin-billing-progressive-disclosure.test.mjs tests/security/admin-internationalization.test.mjs tests/security/admin-recovery-credit-refunds.test.mjs`: passed, 18 tests.
- `npm exec tsc -- --noEmit`: passed after `npm run prisma:generate`; the first post-edit run caught and the focused rerun confirmed the optional support-context identifier fix.
- `npm run test:unit`: passed, 42 tests.
- `npm test`: passed, 173 tests; 0 failures.
- `npm run lint`: passed with 2 existing warnings in `src/components/admin/queue-monitor.tsx` for missing `refresh` hook dependencies; no errors.
- `npm run build`: passed. Existing non-blocking BullMQ webpack warnings remain for an expression dependency and optional `@valkey/valkey-glide` resolution.
- `git diff --check`: passed.

### Two-Pass Audit
- First pass omitted/partially met: exact request detail did not visibly render the already-loaded BillingPeriod dates/plan provenance, provider usage valuation before/after evidence, support-context message identity, or sufficient historical refund-attempt evidence for amount/currency/time/reason. No queue, authorization, state-derivation, pagination, read-only, quantity-control, provider-action, Shopify, support-message-prerequisite, or cross-shop boundary omission was found.
- Corrections: extended the existing bounded read projection/type and drawer rendering; added focused regression assertions. No database, workflow, provider, or cross-repository changes were required.
- Second independent pass: all objective requirements now pass. Queue/detail authorization uses the existing platform-admin read guard; queue filters use database `count` plus bounded `skip`/`take` with default 20 and max 50; derived waiting/ready states use the exact withdrawn purchase conditions; snapshots and live values are distinct; invalid ACTIVE/COMPLETED/REFUNDED non-terminal cases surface attention without repair; terminal cancellation history remains visible; no arbitrary quantity or settlement control exists.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-002`.
- Implementation branch: `task/ARCH-010-ADMIN-002`.
- Implementation commits: `cd0eda5` (`feat(admin): triage recovery credit refund requests`), `9e571cd` (`fix(admin): complete refund triage detail evidence`).
- Implementation branch pushed to `origin/task/ARCH-010-ADMIN-002`.
- Parent report is being published from `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-002` on the mirrored `task/ARCH-010-ADMIN-002` branch.

### Architect Review
Pending architect review. No unresolved task-scope blocker identified.
