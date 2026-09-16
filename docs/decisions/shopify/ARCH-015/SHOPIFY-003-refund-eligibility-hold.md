---
id: ARCH-015-SHOPIFY-003
architecture_id: ARCH-015
title: Enforce current-provider-context refund eligibility and durable refund holds
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 60
attempt: 2
depends_on:
- ARCH-015-SHARED-001
- ARCH-015-SHOPIFY-002
- ARCH-015-BACKGROUND-001
enables:
- ARCH-015-BACKGROUND-003
created: 2026-09-15
updated: 2026-09-16
---

# ARCH-015-SHOPIFY-003

## Objective

Prevent historical purchases from entering the normal monetary refund path while keeping their credits spendable. For eligible current-context purchases, create a durable refund request/entitlement hold only; Background owns provider correction.

## Authorized implementation surface

```text
app/services/billing/recovery-credit-purchase-management.service.ts
app/services/billing/providers/shopify-billing.provider.ts    # read only if required by current service composition
app/routes/app/billing/recovery-credit-purchases/route.tsx
app/components/dashboard/*purchase*manager*.*
tests/unit/services/recovery-credit-purchase-management.service.test.ts
tests/unit/recovery-credit-purchase-manager.test.tsx
# directly affected route tests
```

No App Events submission from this task.

## Fresh provider eligibility

Before changing purchase/refund state:

1. authenticate exact shop;
2. load exact purchase;
3. reject cross-shop/missing;
4. require purchase `ACTIVE`;
5. require provider purchase amount is non-null and strictly > 0 for monetary refund eligibility;
6. require unused current balance > 0;
7. obtain fresh Shopify active subscription;
8. derive current provider context through Shared;
9. require purchase context matches current context;
10. require purchase plan handle equals live provider plan handle;
11. require purchase billingPeriodId equals current local subscription billingPeriodId;
12. require purchase event handle is present in live provider subscription.

Historical/context-mismatched purchase outcome:

```text
REFUND_NOT_CURRENT_PROVIDER_CONTEXT
```

It must remain ACTIVE and no aggregate hold/refund row is created.

Zero-cost purchase outcome:

```text
REFUND_NOT_AVAILABLE
```

Credits remain spendable.

## Hold semantics

For eligible purchase, preserve existing safe reservation behavior:

```text
availableAmount = max(currentAmount - reservedAmount, 0)
```

If availableAmount < 1 => REFUND_NOT_AVAILABLE.

Create one idempotent RecoveryCreditRefund with immutable snapshots.

Transition purchase:

```text
ACTIVE -> WITHDRAWN
```

Increase aggregate `refundingQuantity` by currently available amount only. Existing reserved usage may complete/release under current reservation service rules.

Do not mark refund provider-complete.

Do not set provider evidence fields as if a provider action occurred.

## Durable invocation boundary

Successful request ends after transaction commits.

Do NOT call Background/Redis directly.

The existing billing scheduler discovers:

```text
RecoveryCreditRefund.status = REQUESTED
```

and `ARCH-015-BACKGROUND-003` processes it asynchronously.

## UI

History remains visible.

Historical ACTIVE purchase:
- show remaining credits as usable;
- hide/disable normal refund action with generic explanation that it is no longer refundable under the current subscription;
- do not imply credits expired.

REQUESTED/WITHDRAWN:
- show refund requested/processing state.

## Required tests

- current-context active positive-value purchase -> REQUESTED refund + WITHDRAWN hold;
- historical prior-plan purchase -> REFUND_NOT_CURRENT_PROVIDER_CONTEXT, stays ACTIVE;
- prior billing-cycle purchase -> not current provider context;
- event handle absent from current provider subscription -> not current context;
- null legacy id current native App Pricing context works through Shared identity;
- zero-cost purchase not monetary-refundable;
- reserved credits excluded from initial hold;
- duplicate request is idempotent;
- no Background queue/network App Event invocation;
- merchant UI keeps historical credits visible/spendable.

## Stop conditions

STOP if:

- safe eligibility requires mutating historical purchase provenance;
- task needs a new refund status/field;
- refund request must synchronously wait for Background/provider completion.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

Reworked and pushed on `task/ARCH-015-SHOPIFY-003` at commit `8c5a953`.

### Changes

- Added fresh Shopify active-subscription eligibility checks before refund mutation.
- Made the exact nonblank `shopifyShopId` mandatory at the refund service boundary and rejected missing/blank identities without mutation.
- Enforced strictly positive provider purchase value for every refund admission path, including direct service callers.
- Allowed both live Shopify subscription statuses, `ACTIVE` and `TRIALING`, when the provider context matches.
- Matched Shared provider context, plan handle, local billing-period identity and dates, and live event handle.
- Returned `REFUND_NOT_CURRENT_PROVIDER_CONTEXT` for historical purchases without changing purchase or aggregate state.
- Returned `REFUND_NOT_AVAILABLE` for zero-cost or fully reserved purchases.
- Preserved idempotent `REQUESTED` refund creation, available-balance-only aggregate holds, and `ACTIVE -> WITHDRAWN` transition.
- Passed the exact Shopify shop identity from the authenticated route.
- Kept historical credits visible and spendable in the merchant UI while hiding the normal refund action with generic copy.
- Added regression coverage for current context, `ACTIVE`/`TRIALING` parity, mismatched trial context, prior plan, prior billing cycle, missing event, native App Pricing identity, zero/non-positive purchases, missing/blank identity, and UI visibility.

### Validation

- Focused Vitest: `31/31` passed across the refund service and purchase manager suites.
- Focused ESLint: passed for touched TypeScript/test files.
- Prisma schema validation: passed.
- Application build: passed.
- `git diff --check`: passed.
- Repository lint: existing unrelated errors remain outside this task; direct lint of touched files passed.

### Preparation evidence

Physical worktree isolation:
	canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
	parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-SHOPIFY-003`
	parent branch: `task/ARCH-015-SHOPIFY-003`
	implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-SHOPIFY-003`
	implementation branch: `task/ARCH-015-SHOPIFY-003`
	shared workspace checkout switched/mutated for task work: no
	another task worktree reused: no

Start-of-attempt synchronization:
	parent remote task branch fast-forwarded: not-needed
	parent origin/main incorporated: already-current
	implementation remote task branch fast-forwarded: not-needed
	implementation origin/main incorporated: already-current

Recursive implementation submodules:
	`git submodule sync --recursive`: passed
	`git submodule update --init --recursive`: passed
	recorded submodule commit: `database` at `d44b621cdcc3635127b91601be648b61c0eff1e2`

Returned to `moda_architect` for review after attempt-2 rework.

## Architect Review — Attempt 1

### Status

**Changes Requested — mandatory provider proof at the service boundary and TRIALING current-context parity**

The durable hold mechanics and historical-purchase behavior are otherwise accepted.
Preserve the existing behavior for:

```text
authenticated route resolves the exact shop
cross-shop/missing purchase fails closed
purchase must be ACTIVE
availableAmount = max(currentAmount - reservedAmount, 0)
provider monetary amount must be strictly positive
historical/context mismatch remains ACTIVE and returns REFUND_NOT_CURRENT_PROVIDER_CONTEXT
zero-cost purchase returns REFUND_NOT_AVAILABLE
one idempotent REQUESTED RecoveryCreditRefund
ACTIVE -> WITHDRAWN
aggregate refundingQuantity increments by availableAmount only
reserved credits are not included in the hold
no provider-complete evidence is fabricated
no direct Background/Redis/App Events invocation
historical credits remain visible/spendable
```

Attempt 2 is limited to the two corrections below. Do not redesign refund
correction, Background scheduling, refund statuses, database schema, purchase
provenance, reservation semantics or the merchant-history surface.

### Finding 1 — refund mutation can bypass all fresh-provider eligibility

`shopifyShopId` is optional on the service refund methods and the current implementation
guards provider-value/context checks with:

```ts
if (input.shopifyShopId && ...)
```

Therefore a direct service call that omits `shopifyShopId` can still create a
`REQUESTED` refund, transition the purchase to `WITHDRAWN`, and increment
`refundingQuantity` without any fresh Shopify proof. The retained success/idempotency
unit tests currently exercise this bypass.

This violates the task invariant that fresh provider eligibility is required **before
changing purchase/refund state**.

#### Required correction

Make the exact Shopify shop identity mandatory for refund admission.

Use the existing route-resolved Shopify shop id; do not rediscover merchant identity
from browser input.

Required service contract:

```text
requestRefund / requestRefundBatch
  -> require a nonblank exact shopifyShopId for any refund mutation path
  -> load exact purchase and reject missing/cross-shop
  -> require ACTIVE
  -> require providerPurchaseAmount is non-null and strictly > 0
  -> require availableAmount >= 1
  -> obtain fresh Shopify active subscription
  -> prove current provider context / plan / billing period / event handle
  -> only then create hold/refund state
```

`providerPurchaseAmount > 0` must be enforced unconditionally for refund eligibility;
it must not depend on whether a Shopify shop id happened to be supplied.

A missing/blank Shopify shop id must fail closed with **no** refund row, purchase
transition or aggregate hold. Prefer making `shopifyShopId` required in the internal
refund request types so new callers cannot accidentally omit it, while retaining a
runtime nonblank guard.

Non-mutating terminal cases that are already knowable from local durable state
(missing/cross-shop, non-ACTIVE, no available credits, zero/non-positive provider
amount) may return their existing bounded outcomes without making a Shopify request.
No potentially successful monetary-refund path may skip fresh provider proof.

Required regressions:

```text
direct service request with missing/blank shopifyShopId -> no mutation
current positive-value request with exact shopifyShopId -> REQUESTED
zero/non-positive provider amount -> REFUND_NOT_AVAILABLE even before provider proof
batch/idempotent success tests use the exact shopifyShopId and provider fixture
replay remains one durable refund row
```

Do not weaken the route authentication/access checks.

### Finding 2 — valid TRIALING current contracts are misclassified as historical

`ProviderSubscription.status` supports both:

```text
TRIALING
ACTIVE
```

and ARCH-015-SHOPIFY-002 explicitly permits purchase admission under an
`ACTIVE/TRIALING` executable contract.

`isCurrentProviderContext(...)` currently requires:

```ts
providerSubscription.status === "ACTIVE"
```

so a valid positive-value purchase made under a current `TRIALING` Shopify contract
returns `REFUND_NOT_CURRENT_PROVIDER_CONTEXT` even when provider identity, plan,
billing period and event handle all match.

SHOPIFY-003 defines current-provider-context refundability; it does not introduce a
new policy that trial contracts are historically ineligible.

#### Required correction

Treat both executable live statuses as current-context candidates:

```text
providerSubscription.status in { ACTIVE, TRIALING }
```

All other existing context checks remain mandatory:

```text
exact Shopify shop identity
canonical providerContextIdentity
plan handle
local billingPeriodId
provider/local period start/end
purchase event handle present live
```

Required regressions:

```text
matching TRIALING provider context -> refund may become REQUESTED
TRIALING provider with plan/period/event mismatch -> REFUND_NOT_CURRENT_PROVIDER_CONTEXT
ACTIVE behavior remains unchanged
```

### Validation

Run at minimum:

```bash
npm test -- \
  tests/unit/services/recovery-credit-purchase-management.service.test.ts \
  tests/unit/recovery-credit-purchase-manager.test.tsx

npm run lint -- \
  app/services/billing/recovery-credit-purchase-management.service.ts \
  app/routes/app/billing/recovery-credit-purchases/route.tsx \
  tests/unit/services/recovery-credit-purchase-management.service.test.ts \
  tests/unit/recovery-credit-purchase-manager.test.tsx

npm run prisma:validate
npm run build
git diff --check
```

If repository-wide typecheck remains blocked only by the already documented unrelated
JSX/Polaris baseline, record that evidence; do not broaden this task to fix it.

### Stop condition

When both findings are corrected and focused tests prove that every potentially
successful refund mutation has fresh provider proof while ACTIVE and TRIALING current
contexts behave consistently, update the Completion Report, set `status: review`,
clear the claim and return to `moda_architect`.

Do not mark `ARCH-015-BACKGROUND-003` Ready. Dependency promotion belongs to architect
acceptance of SHOPIFY-003.
