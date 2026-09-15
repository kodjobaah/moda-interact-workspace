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
status: in_progress
priority: 82
executor: copilot
claimed_at: 2026-09-15T00:31:18Z
attempt: 4
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
Ready for Review. Attempt 4 completed all three mandatory Architect Review corrections on the existing implementation branch. The stale Attempt 2 shared-package blocker remains superseded by the observed `@modainteract/moda-interact-shared` refund message exports.

### Files Changed
- Implementation repository:
	- `src/app/actions/recovery-credit-refunds.ts`
	- `src/lib/admin/recovery-credit-refund-settlement.ts`
	- `src/components/admin/recovery-credit-refunds.tsx`
	- `tests/security/admin-recovery-credit-refund-settlement.test.mjs`
	- `tests/security/admin-recovery-credit-refunds.test.mjs`
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
- Independent audit found one gap in the published commit: the server actions were not reachable from the admin refund drawer, and the drawer did not display frozen expected settlement evidence. Added SUPER_ADMIN-gated lock/reject/provider-evidence forms and the final quantity, expected amount/currency, and recorded provider evidence fields. Updated the stale read-only UI test to assert this workflow.

### Independent Audit Gap Table
| Requirement | Exact evidence inspected | Result | Risk |
| --- | --- | --- | --- |
| Admin can lock/reject/record provider settlement through the admin surface | `src/components/admin/recovery-credit-refunds.tsx:56-104` invokes all three server actions; server authorization remains in `src/lib/admin/recovery-credit-refund-settlement.ts:54-113` | PASS after fix | Previously unreachable controls could leave provider settlement operationally incomplete. |
| Durable provider evidence is displayed before/manual settlement | `src/components/admin/recovery-credit-refunds.tsx` frozen evidence block and provider form; `src/lib/admin/recovery-credit-refunds.ts:12-59` selects persisted fields | PASS after fix | Previously operators could not see or record the frozen provider boundary from the drawer. |
| Transactional authorization, provenance, hold parity, CAS/idempotency, and no provider API | `src/lib/admin/recovery-credit-refund-settlement.ts:45-142`; Prisma fields in `database/prisma/schema.prisma:714-805` and `1250-1290`; focused security tests | PASS | Remaining risk is limited to the repository's static-test coverage of runtime transaction behavior. |
| Full-suite validation | `npm test` result: 176 total, 174 passed, 2 baseline failures in internationalization/merchant-support shared-version assertions | PASS with documented baseline | Baseline failures are unrelated to settlement; they remain a release validation caveat. |

### Validation Results
- `node --test tests/security/admin-recovery-credit-refund-settlement.test.mjs tests/security/admin-recovery-credit-refunds.test.mjs tests/security/admin-security-boundary.test.mjs tests/security/admin-billing-controls.test.mjs`: 23 passed, 0 failed.
- `npm run prisma:validate`: passed.
- `npx tsc --noEmit`: passed.
- `npm run lint`: passed with two pre-existing warnings in `src/components/admin/queue-monitor.tsx` for missing `refresh` hook dependencies; no errors.
- `npm run build`: passed. Existing BullMQ warnings remain for an expression dependency and optional `@valkey/valkey-glide` resolution.
- `npm test`: 176 total, 174 passed, 2 unrelated baseline failures. Both failures are existing shared-package version assertions in `tests/security/admin-internationalization.test.mjs` and `tests/security/admin-merchant-support.test.mjs` expecting `^0.7.3` while the repository declares `^0.11.0`; neither touches the settlement implementation.
- `git diff --check`: passed after implementation and report changes.

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
19. Focused tests, concurrency transaction coverage, build, static checks, full suite, and diff check: satisfied except the two documented unrelated baseline failures; focused validation now includes the repaired admin UI surface.

### Git / VCS
Launcher claim commit: `1d0d2246b6703c56b14ee802b2d1a5569d0f2bf5`.
Authoritative implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-003`, branch `task/ARCH-010-ADMIN-003`.
Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-003`, branch `task/ARCH-010-ADMIN-003`.
Implementation commit: `341d710` (`feat(admin): settle withdrawn recovery credit refunds`), followed by the audit correction commit recorded in the final task response and pushed to `origin/task/ARCH-010-ADMIN-003`.
The parent report correction is being published on the mirrored parent branch after this update; its exact publication commit is recorded in the final task response and parent branch history.

### Attempt 4 Correction Checklist and Requirement Audit

1. **Zero-current completion is lot-independent: PASS.** Removed the shop-wide `aggregate.refundingQuantity === 0` precondition and removed the aggregate dependency from `completeZeroCurrent(...)`. Both lock and reject zero-current callers now close only the exact purchase/refund; they do not mutate aggregate quantities. Focused regression assertions prove a separate purchase hold cannot block this path and no aggregate update is present.
2. **Currency precision is provider-currency derived: PASS.** Added ISO currency validation through `Intl.supportedValuesOf("currency")` and `Intl.NumberFormat(...).resolvedOptions().maximumFractionDigits`, preserving Prisma Decimal arithmetic and `ROUND_HALF_UP`. The fixed `toDecimalPlaces(2, ...)` path is absent; provider lock passes the immutable purchase currency. Focused assertions cover USD/JPY/KWD precision metadata paths and fail-closed validation.
3. **Settlement controls are SUPER_ADMIN-only in the UI: PASS.** Billing now retains the page principal and passes `canSettle={principal.role === "SUPER_ADMIN"}`. The drawer renders `SettlementActions` only when `canSettle` is true while retaining evidence/read visibility for all authorized admins. Server mutation checks remain unchanged and independently enforce `SUPER_ADMIN`.

Accepted behavior audit: exact live `currentAmount` remains the final quantity; historical purchase amount/currency remain the sole expected-money authority; provider-action CAS, reservation blocking, aggregate parity, evidence mismatch attention state, atomic completion, pre-provider rejection, idempotent messages/audit, no provider API, no negative App Event, and independent purchase-lot scope remain unchanged. No schema, shared package, background, Shopify app, or reactivation changes were made.

### Attempt 4 Validation

- Focused settlement/UI suites: 7 passed, 0 failed.
- Required focused security suites (`admin-recovery-credit-refund-settlement`, `admin-recovery-credit-refunds`, `admin-security-boundary`, `admin-billing-controls`): 25 passed, 0 failed.
- `npm run prisma:validate`: passed.
- `npx tsc --noEmit`: passed after narrowing `Intl` precision and the persisted nullable currency field.
- `npm run lint`: passed with two pre-existing `queue-monitor.tsx` `react-hooks/exhaustive-deps` warnings; no errors.
- `npm run build`: passed. Existing BullMQ expression-dependency and optional `@valkey/valkey-glide` warnings remain.
- `npm test`: 178 total, 176 passed, 2 unchanged baseline failures: `admin-internationalization.test.mjs` and `admin-merchant-support.test.mjs` still expect `@modainteract/moda-interact-shared` `^0.7.3` while the repository declares `^0.11.0`.
- `git diff --check`: passed.

### Attempt 4 Git / VCS Evidence

- Launcher claim commit: `19eccd5`.
- Authoritative implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-003`, branch `task/ARCH-010-ADMIN-003`; prepared previous head `c2c7ccb`; implementation commit `4b8bd8d` pushed to `origin/task/ARCH-010-ADMIN-003`.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-003`, branch `task/ARCH-010-ADMIN-003`; launcher physical worktree isolation was preserved.
- Launcher reported recursive submodules synchronized and at recorded commits; no submodule gitlink was staged or changed by this task.
- Parent report publication commit is the final commit recorded in this task branch and in the final response.

No unresolved implementation limitation remains within the bounded Admin scope. The two shared-package version assertions, lint warnings, build warnings, and Node module-type warnings are unrelated baseline conditions.

### Architect Review
Ready for Architect Review. The independently identified reachability/evidence gap is fixed and validated. No unresolved implementation limitation remains within the bounded Admin scope. The two full-suite baseline failures and existing lint/build warnings are recorded above and are unrelated to this task.
## Architect Review — Attempt 3

### Decision

**Changes Requested — narrow functional correction.**

The UI re-audit correction is accepted:

```text
- lock/reject/provider-evidence actions are now reachable from the Admin refund drawer;
- frozen final quantity and expected provider amount/currency are displayed;
- recorded provider action/reference/amount are displayed;
- provider evidence remains manual Shopify Partner Dashboard/Support evidence;
- the server mutation functions remain SUPER_ADMIN-authorized.
```

Implementation correction commit reviewed:

```text
c2c7ccbada3f1099a9d48fe6616e0efa6acddbb3
```

Parent report commit reviewed:

```text
b368fc67e965b9a556d3bd81fcaf38be1f760ce8
```

The task is **not** being returned for exhaustive test coverage. Two production
functional defects remain in the settlement implementation, plus one bounded UI
authorization/presentation correction.

---

# Attempt 4 — exact implementation contract

## Correction 1 — zero-current completion MUST NOT impose a shop-wide refund lock

### Problem

Current `completeZeroCurrent(...)` contains:

```ts
if (
  purchase.reservedAmount !== 0
  || aggregate.refundingQuantity !== 0
) {
  throw new Error("Aggregate hold parity is inconsistent.");
}
```

`aggregate.refundingQuantity` is the **shop-wide purchased-credit aggregate**.
It may legitimately contain refund holds belonging to other withdrawn purchases.

Therefore this condition makes independent purchase lots interfere with each
other.

Example that MUST succeed:

```text
Purchase A
  status = WITHDRAWN
  currentAmount = 0
  reservedAmount = 0
  refund = REQUESTED

Purchase B
  status = WITHDRAWN
  currentAmount = 7
  reservedAmount = 0
  contributes 7 to shop aggregate.refundingQuantity

shop aggregate.refundingQuantity = 7
```

Closing Purchase A must not require Purchase B's hold to disappear.

### Required code change

Modify exactly:

```text
src/lib/admin/recovery-credit-refund-settlement.ts
```

Change `completeZeroCurrent(...)` so it does **not** require:

```text
aggregate.refundingQuantity === 0
```

and does **not** mutate any aggregate quantity.

The zero-current path owns zero refundable credits for that purchase, so the
correct invariant is only:

```text
purchase.status = WITHDRAWN
purchase.currentAmount = 0
purchase.reservedAmount = 0
refund.status = REQUESTED
```

`loadSettlementState(...)` has already proved the shop aggregate exists.

Implement the helper with no aggregate dependency. Preferred exact shape:

```ts
async function completeZeroCurrent(
  transaction: Transaction,
  adminId: string,
  refund: Awaited<ReturnType<typeof loadSettlementState>>["refund"],
  purchase: Awaited<ReturnType<typeof loadSettlementState>>["purchase"],
  reason: string,
) {
  if (purchase.reservedAmount !== 0) {
    throw new Error("Purchase reservation parity is inconsistent.");
  }

  const purchaseUpdate =
    await transaction.recoveryCreditPurchase.updateMany({
      where: {
        id: purchase.id,
        status: RecoveryCreditPurchaseStatus.WITHDRAWN,
        version: purchase.version,
        currentAmount: 0,
        reservedAmount: 0,
      },
      data: {
        status: RecoveryCreditPurchaseStatus.COMPLETED,
        version: { increment: 1 },
      },
    });

  const refundUpdate =
    await transaction.recoveryCreditRefund.updateMany({
      where: {
        id: refund.id,
        status: RecoveryCreditRefundStatus.REQUESTED,
        version: refund.version,
      },
      data: {
        status: RecoveryCreditRefundStatus.COMPLETED,
        completedAt: new Date(),
        reason,
        version: { increment: 1 },
      },
    });

  if (purchaseUpdate.count !== 1 || refundUpdate.count !== 1) {
    throw new Error("Refund changed while closing zero-current purchase.");
  }

  // preserve the existing audit and one refund-completed system message
}
```

Update both callers:

```ts
lockRecoveryCreditRefund(...)
rejectRecoveryCreditRefund(...)
```

from:

```ts
completeZeroCurrent(
  transaction,
  principal.id,
  refund,
  purchase,
  aggregate,
  boundedReason,
)
```

to:

```ts
completeZeroCurrent(
  transaction,
  principal.id,
  refund,
  purchase,
  boundedReason,
)
```

Do **not** decrement:

```text
aggregate.refundingQuantity
aggregate.grantedQuantity
aggregate.committedQuantity
aggregate.reservedQuantity
```

in this zero-current path.

Do not add any shop-wide lock.

### Required functional regression

Prove:

```text
Purchase A current=0/reserved=0/REQUESTED
Purchase B owns a non-zero shop refund hold
aggregate.refundingQuantity > 0
```

then closing Purchase A:

```text
succeeds
A purchase -> COMPLETED
A refund -> COMPLETED
aggregate quantities are unchanged
Purchase B is untouched
exactly one audit/message is produced
```

This may be one focused transaction test. No combinatorial matrix is required.

---

## Correction 2 — remove the fixed two-decimal refund calculation

### Problem

Current code calculates:

```ts
amount
  .mul(quantity)
  .div(granted)
  .toDecimalPlaces(2, Prisma.Decimal.ROUND_HALF_UP)
```

The accepted DATABASE-014 contract explicitly forbids assuming every provider
currency has two fractional digits.

### Required code change

Modify exactly:

```text
src/lib/admin/recovery-credit-refund-settlement.ts
```

Add one deterministic ISO-currency precision helper.

Use this exact implementation contract:

```ts
const SUPPORTED_CURRENCIES =
  new Set(Intl.supportedValuesOf("currency"));

function currencyFractionDigits(currency: string): number {
  if (
    !CURRENCY.test(currency)
    || !SUPPORTED_CURRENCIES.has(currency)
  ) {
    throw new Error("Provider currency is unsupported.");
  }

  const fractionDigits =
    new Intl.NumberFormat("en", {
      style: "currency",
      currency,
    }).resolvedOptions().maximumFractionDigits;

  if (
    !Number.isInteger(fractionDigits)
    || fractionDigits < 0
    || fractionDigits > 4
  ) {
    throw new Error("Provider currency precision is unsupported.");
  }

  return fractionDigits;
}
```

Change:

```ts
function expectedAmount(
  amount: Prisma.Decimal,
  quantity: number,
  granted: number,
): Prisma.Decimal
```

to:

```ts
function expectedAmount(
  amount: Prisma.Decimal,
  quantity: number,
  granted: number,
  currency: string,
): Prisma.Decimal {
  const fractionDigits = currencyFractionDigits(currency);

  return amount
    .mul(quantity)
    .div(granted)
    .toDecimalPlaces(
      fractionDigits,
      Prisma.Decimal.ROUND_HALF_UP,
    );
}
```

Change the provider-lock call from:

```ts
expectedAmount(
  purchase.providerPurchaseAmount!,
  finalCreditQuantity,
  purchase.creditsGranted,
)
```

to:

```ts
expectedAmount(
  purchase.providerPurchaseAmount!,
  finalCreditQuantity,
  purchase.creditsGranted,
  purchase.providerPurchaseCurrency,
)
```

Do not:

```text
use JavaScript Number for monetary arithmetic
use floating-point Math.round
use current plan/top-up pricing
change expected amount to operator-entered provider evidence
default an unknown currency to two decimal places
```

If the provider currency is not a supported ISO currency, fail closed before
`PROVIDER_ACTION_REQUIRED`.

### Required functional proof

Prove at minimum:

```text
USD -> 2 fraction digits
JPY -> 0 fraction digits
KWD -> 3 fraction digits
```

and proportional rounding remains `ROUND_HALF_UP`.

Representative examples:

```text
USD: M=10.00, R=1, G=3 -> 3.33
JPY: M=1000,  R=1, G=3 -> 333
KWD: M=1.000, R=1, G=3 -> 0.333
```

Also assert the production source no longer contains:

```text
toDecimalPlaces(2
```

No broad currency test matrix is required.

---

## Correction 3 — make the Admin controls genuinely SUPER_ADMIN-only in the UI

The server-side authorization is already correct and MUST remain the primary
security boundary:

```ts
const principal = await requirePlatformAdminMutation();

if (principal.role !== "SUPER_ADMIN") {
  throw new Error("SUPER_ADMIN access is required.");
}
```

Do not weaken or remove those checks.

The current billing page, however, uses:

```ts
await requirePlatformAdminPage();
```

and discards the returned principal, so ordinary active platform admins can see
settlement controls that they are not allowed to use.

Use the existing Admin UI convention and hide mutation controls from non-SUPER_ADMIN
users.

### Billing page

Modify:

```text
src/app/(protected)/billing/page.tsx
```

Change:

```ts
await requirePlatformAdminPage();
```

to:

```ts
const principal = await requirePlatformAdminPage();
```

When rendering the refund drawer, pass:

```tsx
<RecoveryCreditRefundDrawer
  refund={selectedRefund}
  params={params}
  canSettle={principal.role === "SUPER_ADMIN"}
/>
```

### Refund drawer

Modify:

```text
src/components/admin/recovery-credit-refunds.tsx
```

Change the drawer props to:

```ts
{
  refund: RecoveryCreditRefundDetail;
  params: Record<string, string>;
  canSettle: boolean;
}
```

and render:

```tsx
{canSettle ? <SettlementActions refund={refund} /> : null}
```

instead of unconditionally rendering `SettlementActions`.

All active platform admins may continue to read:

```text
refund status
purchase provenance
frozen final quantity
expected provider amount/currency
recorded provider evidence
history
```

Only `SUPER_ADMIN` sees the mutation forms.

Server role enforcement remains mandatory even though the UI is hidden.

### Required functional proof

Prove:

```text
SUPER_ADMIN -> settlement controls rendered
non-SUPER_ADMIN active admin -> evidence rendered, settlement controls absent
server settlement methods still independently reject non-SUPER_ADMIN mutation
```

---

# Accepted behavior that MUST remain unchanged

Do not modify the following accepted ADMIN-003 behavior:

```text
REQUESTED + reservedAmount>0 -> WAITING_FOR_RESERVATIONS
finalCreditQuantity = exact live purchase.currentAmount
historical provider purchase value is refund authority
REQUESTED -> PROVIDER_ACTION_REQUIRED freezes quantity and expected money
merchant/Admin never enters finalCreditQuantity
provider action kind = REFUND | CREDIT only
provider reference bounded to existing limit
explicit provider confirmation required
provider amount/currency mismatch -> NEEDS_ATTENTION
mismatch preserves purchase WITHDRAWN and aggregate hold
successful completion atomically:
  purchase -> REFUNDED/currentAmount=0
  aggregate refundingQuantity -= finalCreditQuantity
  aggregate grantedQuantity -= finalCreditQuantity
  refund -> COMPLETED
pre-provider reject only while refund = REQUESTED
pre-provider reject releases exact current unreserved hold
provider action boundary prevents merchant reactivation
exact refund/purchase versioned CAS
one refund-scoped merchant system message
transition-gated audit/idempotency
no Shopify refund API
no negative/fractional App Event correction
other purchase lots remain independent
```

The new `c2c7ccb` drawer controls and frozen evidence display are accepted and
must remain.

---

# Allowed files for Attempt 4

Production files:

```text
src/lib/admin/recovery-credit-refund-settlement.ts
src/app/(protected)/billing/page.tsx
src/components/admin/recovery-credit-refunds.tsx
```

Focused test files:

```text
tests/security/admin-recovery-credit-refund-settlement.test.mjs
tests/security/admin-recovery-credit-refunds.test.mjs
```

A new narrowly scoped settlement utility test is allowed if runtime testing the
currency helper cleanly requires it.

Do not modify:

```text
database schema/migrations
shared package
background service
Shopify app
RecoveryCreditPurchase/Refund enums
refund request creation
merchant reactivation semantics
provider APIs
unrelated Admin pages/components
```

---

# Required validation

Run the existing focused security suites covering:

```text
admin recovery-credit refund settlement
admin recovery-credit refund UI
admin security boundary
admin billing controls
```

and the two new functional regressions above.

Then run:

```bash
npm run prisma:validate
npx tsc --noEmit
npm run lint
npm run build
npm test
git diff --check
```

The two already-documented repository-wide shared-version baseline test failures
remain non-blocking if unchanged.

Any new error in an Attempt-4 touched production file is blocking.

---

# Metadata / stop conditions

Return this task to:

```text
status: ready
attempt: 3
executor: null
claimed_at: null
```

The next `/moda-task ARCH-010-ADMIN-003` claim MUST become:

```text
attempt: 4
```

exactly once.

STOP and return to `moda_architect` rather than inventing a new design if:

```text
currency precision cannot be represented deterministically without floating point
the zero-current correction would require changing aggregate ownership semantics
a schema/migration change appears necessary
refund/CAS/provider settlement semantics would need redesign
```

Attempt 4 may return to Architect Review only when:

```text
zero-current closure is independent of other purchase holds
shop aggregate remains untouched in zero-current closure
currency-aware proportional refund precision replaces fixed 2 decimals
USD/JPY/KWD precision proof passes
non-SUPER_ADMIN users cannot see settlement mutation controls
server SUPER_ADMIN enforcement remains intact
accepted c2c7ccb drawer reachability/evidence behavior remains intact
focused validation passes
status = review
executor = null
claimed_at = null
both worktrees are clean and pushed
```

`ARCH-010-SYSTEM-TEST-003` remains gated.
