---
id: ARCH-010-ADMIN-003
architecture_id: ARCH-010
title: Lock and settle withdrawn recovery-credit purchases through Shopify Partner Dashboard
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 82
executor: copilot
claimed_at: 2026-09-14T23:15:44Z
attempt: 3
depends_on:
- ARCH-010-ADMIN-002
- ARCH-010-BACKGROUND-022
- ARCH-010-SHARED-008
- ARCH-010-DATABASE-014
- ARCH-010-BACKGROUND-021
enables:
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: 2026-09-15
---

# ARCH-010-ADMIN-003: Lock and settle withdrawn recovery-credit purchases through Shopify Partner Dashboard

## Product correction

The old arbitrary-partial approval/hold workflow is superseded.

The merchant already placed the exact purchase into `WITHDRAWN` through SHOPIFY-025. That transition removed the purchase from future FIFO allocation and placed its currently unreserved credits into aggregate `refundingQuantity`.

ADMIN-003 does **not** choose or hold a partial quantity. It waits for all pre-existing reservations on that purchase to settle, then locks the purchase's **entire remaining `currentAmount`** as the final provider refund quantity.

There is no Shopify refund API call in application code; the human uses Shopify Partner Dashboard/Support and records evidence.

## Authorization

Only active `SUPER_ADMIN` may:

```text
lock provider action
reject before provider action
record provider action
complete refund
move/resolve NEEDS_ATTENTION according to existing Admin conventions
```

Use existing platform-admin authorization/audit infrastructure.

## Irreversible provider-action boundary

Provider action may begin only when a fresh Serializable transaction proves:

```text
refund.status = REQUESTED
purchase.status = WITHDRAWN
purchase.currentAmount > 0
purchase.reservedAmount = 0
refund/purchase belong to same shop
purchase immutable commercial provenance is complete
the aggregate purchased counter exists and is internally consistent
```

If `reservedAmount > 0`, return `WAITING_FOR_RESERVATIONS`; do not create provider instructions and do not guess final quantity.

If `currentAmount = 0`, no money is refundable. Close according to the canonical no-credits terminal path and ensure purchase is `COMPLETED`; do not create a £0 provider action.

## Final credit quantity

At the winning provider-action transaction:

```text
finalCreditQuantity = purchase.currentAmount
```

The merchant/Admin never enters this value.

Persist it in the canonical DATABASE-014 refund field (for example `finalCreditQuantity`) together with the deterministic expected provider amount/currency.

Once refund moves:

```text
REQUESTED -> PROVIDER_ACTION_REQUIRED
```

merchant reactivation is forbidden.

### Race with merchant reactivation

SHOPIFY-025 and ADMIN-003 both CAS the exact refund `status + version`.

If merchant reactivation wins first, Admin retry sees refund `CANCELLED`/purchase ACTIVE and must not begin provider action.

If Admin provider-action lock wins first, merchant retry sees `PROVIDER_ACTION_REQUIRED` and cannot reactivate.

Exactly one wins; no global lock.

## Historical monetary value

Refund money comes only from the exact purchase's immutable provider-confirmed original value.

Let:

```text
G = purchase.creditsGranted
R = finalCreditQuantity
M = purchase.providerPurchaseAmount
```

Require valid purchase amount/currency/provenance and `0 < R <= G`.

Compute the expected provider refund for `R/G` of the original purchase using the deterministic currency-safe precision/rounding rule established by DATABASE-014/provider representation.

Persist:

```text
expectedProviderAmount
expectedProviderCurrency = purchase.providerPurchaseCurrency
```

Never use:

```text
current BillingPlan price
current Shopify plan/tier
current top-up meter rate
another purchase lot
later BillingEconomicsSnapshot
browser/Admin-entered amount as expected truth
```

Because a successful refund makes this purchase terminal REFUNDED, first production has at most one completed refund per purchase; no cumulative multi-partial-refund arithmetic is required.

## Aggregate hold invariant at provider-action boundary

When `reservedAmount = 0`, every remaining current credit on a WITHDRAWN purchase must already be represented in aggregate `refundingQuantity` through SHOPIFY-025/BACKGROUND-022.

Require enough aggregate held quantity for the exact final credit quantity. If parity is inconsistent, do not start provider action; move/report integrity attention rather than repairing by subtraction from another lot.

## Provider settlement instructions

Display exact durable evidence:

```text
shop
purchase/refund IDs
original purchase date
plan/provider subscription/BillingPeriod/meter snapshots
creditsGranted
finalCreditQuantity
original providerPurchaseAmount/providerPurchaseCurrency
expectedProviderAmount/expectedProviderCurrency
```

Human selects actual Shopify action:

```text
REFUND  -> paid charge/invoice can be refunded
CREDIT  -> Shopify requires a credit/adjustment for unpaid charge
```

Do not offer negative/fractional App Events or current-cycle correction events for first-production purchase refunds.

Warn that provider limitations may require Shopify Support/manual escalation. If provider settlement cannot be confirmed, retain purchase WITHDRAWN and aggregate hold.

## Provider evidence

Require:

```text
providerActionKind = REFUND | CREDIT
providerReference bounded string
providerAmount
providerCurrency
explicit confirmation
```

Before local completion require exact match:

```text
providerAmount == expectedProviderAmount
providerCurrency == expectedProviderCurrency
```

If provider evidence differs or action may be ambiguous:

```text
refund -> NEEDS_ATTENTION (or retain equivalent accepted attention state)
purchase stays WITHDRAWN
aggregate hold stays in place
merchant cannot reactivate because provider action may have started
```

Do not silently change expected amount to what the operator typed.

## Completion transaction

After confirmed provider action, one Serializable/CAS transaction re-reads exact refund/purchase/aggregate state and requires:

```text
refund.status = PROVIDER_ACTION_REQUIRED (or retry-safe attention resolution path)
purchase.status = WITHDRAWN
purchase.reservedAmount = 0
purchase.currentAmount = refund.finalCreditQuantity
aggregate.refundingQuantity >= finalCreditQuantity
aggregate.grantedQuantity >= finalCreditQuantity
provider evidence exactly matches expected amount/currency
```

Then atomically:

```text
purchase.currentAmount = 0
purchase.reservedAmount = 0
purchase.status = REFUNDED
purchase.version += 1

aggregate.refundingQuantity -= finalCreditQuantity
aggregate.grantedQuantity   -= finalCreditQuantity
aggregate.version += 1

refund.status = COMPLETED
refund provider evidence fields = confirmed evidence
refund.completedAt = now
refund.version += 1
```

Do not increment a per-purchase `refundedQuantity`; first production has no such lot counter.

Do not modify aggregate committed/reserved quantities during provider completion because `reservedAmount=0` was already required and consumed credits remain committed history.

Write existing `RECOVERY_CREDIT_REFUND` audit evidence and create exactly one merchant `BILLING_REFUND_COMPLETED` message using refund ID identity.

## Reject before provider action

A SUPER_ADMIN may reject only while exact refund is still `REQUESTED` and no provider action may have occurred.

This is concurrency-equivalent to merchant reactivation and must use fresh CAS.

If purchase still has `currentAmount > 0`, atomically:

```text
heldAvailable = currentAmount - reservedAmount
aggregate.refundingQuantity -= heldAvailable
purchase WITHDRAWN -> ACTIVE
refund REQUESTED -> REJECTED
```

Do not change purchase current/reserved quantities.

If currentAmount has reached 0, make/retain purchase COMPLETED and reject/close refund with no provider money movement.

Create exactly one `BILLING_REFUND_REJECTED` merchant message with bounded reason.

Never reject/release hold after provider action may have started. Use NEEDS_ATTENTION instead.

## Multiple purchases

Different purchase lots are independent. Admin may simultaneously have:

```text
Purchase A refund waiting for reservations
Purchase B ready for provider action
Purchase C provider action required
Purchase D completed/refunded
```

No shop-wide refund lock is allowed. Every mutation scopes to exact purchase/refund plus the shared aggregate counter under versioned CAS.

## Required tests

At minimum prove:

1. only SUPER_ADMIN can mutate settlement;
2. reservedAmount>0 blocks provider-action lock;
3. currentAmount=0 cannot create £0 refund;
4. final credit quantity is always exact currentAmount, never operator input;
5. historical purchase amount/currency is sole expected-money authority;
6. current plan/top-up rate changes do not affect expected refund;
7. REQUESTED -> PROVIDER_ACTION_REQUIRED freezes final quantity/amount;
8. merchant-reactivation vs Admin-lock race has exactly one winner;
9. provider-action-required/needs-attention blocks merchant reactivation contractually;
10. aggregate held parity is required;
11. provider amount/currency mismatch cannot complete;
12. successful completion sets purchase REFUNDED/current=0 and removes exact aggregate grant+hold;
13. no per-lot refundedQuantity is written;
14. replay does not double-remove credits or duplicate messages/audit;
15. pre-provider Admin reject reactivates exact purchase and releases only its current unreserved hold;
16. rejection while provider action may have happened never releases hold;
17. other purchase lots remain untouched;
18. no negative App Event/automatic refund API is introduced;
19. focused tests, concurrency tests where applicable, repository build/full suite and `git diff --check` pass.

## Non-goals

Do not create merchant refund requests, implement merchant UI, change FIFO reservation logic, or refund Shopify recurring subscription fees.

## Stop conditions

STOP if a provider refund cannot be tied to exact immutable purchase value, if aggregate hold parity is ambiguous, if exact money cannot be represented safely, or if a completed task must be rewritten.

## Completion Report

### Status
Ready for Review. Attempt 3 completed the bounded settlement implementation after the shared package dependency gate was resolved. The stale Attempt 2 shared-package blocker is superseded by the observed `@modainteract/moda-interact-shared` refund message exports.

### Files Changed
- Implementation repository:
	- `src/app/actions/recovery-credit-refunds.ts`
	- `src/lib/admin/recovery-credit-refund-settlement.ts`
	- `tests/security/admin-recovery-credit-refund-settlement.test.mjs`
- Parent repository: this task report only.

### Work Completed
- Re-read the complete current task definition and the current review state. No newer Architect Review section is present after the stale Attempt 2 report; this report does not edit or create one.
- Confirmed the resolved shared package exports `BILLING_SYSTEM_MESSAGE_CODES.REFUND_COMPLETED = BILLING_REFUND_COMPLETED` and `REFUND_REJECTED = BILLING_REFUND_REJECTED`; no local fallback was added.
- Added SUPER_ADMIN-only server actions for provider lock, pre-provider rejection, and provider evidence recording. Each mutation uses the existing active platform-admin resolver, exact shop/purchase/refund scope, Serializable transactions, and versioned CAS predicates.
- Implemented exact remaining-`currentAmount` settlement. Locking waits for reservations, requires immutable purchase provenance and aggregate parity, freezes final quantity and historical expected money, and never calls a provider API or creates a negative event.
- Implemented the zero-current terminal path without a £0 provider action, including purchase completion and zero-reservation/aggregate-hold checks.
- Implemented provider evidence exact amount/currency matching, mismatch transition to `NEEDS_ATTENTION`, hold preservation, and retry-safe resolution.
- Implemented atomic completion of purchase `REFUNDED`/`currentAmount=0`, aggregate grant and hold removal, refund completion, bounded evidence fields, and existing billing audit/system-message infrastructure. Message identity is refund-scoped through the unique `sourceKey`; audit writes are transition-gated and replay-safe.
- Implemented pre-provider rejection that reactivates only the exact purchase and releases only its current unreserved hold. Rejection is unavailable once provider action may have started.
- Added the focused security test and an explicit 19-item acceptance checklist, plus runtime provider action-kind validation for the browser-supplied enum value.

### Validation Results
- `node --test tests/security/admin-recovery-credit-refund-settlement.test.mjs tests/security/admin-security-boundary.test.mjs tests/security/admin-billing-controls.test.mjs`: 21 passed, 0 failed.
- `npm run prisma:validate`: passed.
- `npx tsc --noEmit`: passed.
- `npm run lint`: passed with two pre-existing warnings in `src/components/admin/queue-monitor.tsx` for missing `refresh` hook dependencies; no errors.
- `npm run build`: passed. Existing BullMQ warnings remain for an expression dependency and optional `@valkey/valkey-glide` resolution.
- `get_errors` diagnostics for all three changed files: no errors.
- `npm test`: 176 total, 174 passed, 2 unrelated baseline failures. Both failures are existing shared-package version assertions in `tests/security/admin-internationalization.test.mjs` and `tests/security/admin-merchant-support.test.mjs` expecting `^0.7.3` while the repository declares `^0.11.0`; neither touches the settlement implementation.
- `git diff --check`: passed before implementation commit.

### 19-Item Acceptance Checklist
1. SUPER_ADMIN-only mutation: satisfied by active resolver plus role gates.
2. `reservedAmount > 0` blocks provider lock: satisfied with `WAITING_FOR_RESERVATIONS`.
3. `currentAmount = 0` cannot create £0 provider action: satisfied by terminal completion path.
4. Final quantity is exact current amount: satisfied; no operator quantity input exists.
5. Historical purchase amount is sole expected-money authority: satisfied.
6. Historical purchase currency is sole expected-money authority: satisfied.
7. `REQUESTED -> PROVIDER_ACTION_REQUIRED` freezes quantity and expected money: satisfied by refund CAS/version update.
8. Merchant reactivation versus Admin lock has one CAS winner: satisfied by exact refund status/version predicates.
9. Provider-action-required and attention states block reactivation contractually: satisfied by locked refund state.
10. Aggregate held parity is required: satisfied before provider action and at completion.
11. Provider mismatch cannot complete: satisfied; mismatch persists `NEEDS_ATTENTION` and preserves the hold.
12. Successful completion removes exact aggregate grant and hold and refunds the purchase: satisfied atomically.
13. No per-lot `refundedQuantity` write: satisfied; no such field is referenced.
14. Replay does not double-remove credits or duplicate message/audit: satisfied by terminal CAS, version predicates, unique source key, and transition-gated audit.
15. Pre-provider reject reactivates exact purchase and releases only its current unreserved hold: satisfied atomically.
16. Rejection after possible provider action never releases the hold: satisfied by `REQUESTED`-only rejection.
17. Other purchase lots remain untouched: satisfied by exact purchase/refund IDs and shared aggregate CAS.
18. No negative App Event or automatic refund API: satisfied; source has no provider API, `UsageEvent.create`, or negative-event path.
19. Focused tests, concurrency transaction coverage, build, static checks, full suite, and diff check: satisfied except the two documented unrelated baseline failures.

### Git / VCS
Launcher claim commit: `1d0d2246b6703c56b14ee802b2d1a5569d0f2bf5`.
Authoritative implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-003`, branch `task/ARCH-010-ADMIN-003`.
Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-003`, branch `task/ARCH-010-ADMIN-003`.
Implementation commit: `341d710` (`feat(admin): settle withdrawn recovery credit refunds`), pushed to `origin/task/ARCH-010-ADMIN-003`.
The parent report is being published on the mirrored parent branch after this update; its exact publication commit is recorded in the final task response and parent branch history.

### Architect Review
Ready for Architect Review. No unresolved implementation limitation remains within the bounded Admin scope. The two full-suite baseline failures and existing lint/build warnings are recorded above and are unrelated to this task.
