---
id: ARCH-008-SHOPIFY-001
architecture_id: ARCH-008
title: Require an exact current billing cycle for recovery-credit pack purchases
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 25
executor: copilot
claimed_at: 2026-09-09T15:05:51Z
attempt: 1
depends_on:
  - ARCH-007-SHOPIFY-004
enables:
  - ARCH-008-BACKGROUND-002
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-008-SHOPIFY-001: Require an exact current billing cycle for recovery-credit pack purchases

## Architecture

Canonical:

- `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`
- `docs/architecture/ARCH-008-recovery-credit-reconciliation-preflight-2026-09-09.md`

## Objective

Ensure every newly created recovery-credit-pack UsageEvent has an exact durable
Shopify current-billing-cycle identity before it can enter asynchronous App
Events/reconciliation.

This task hardens the accepted ARCH-007-SHOPIFY-004 producer. It does not change
pricing, pack size, App Events publication or purchased-credit activation.

## Architectural invariant

A **new** recovery-credit pack must never be created with:

```text
UsageEvent.billingPeriodId = null
```

and must never be attached to a stale/local billing period whose boundaries do
not equal Shopify Partner `activeSubscription.currentBillingCycle`.

Existing-purchase idempotent replay remains independent from current provider
availability.

## Why this task exists

The accepted SHOPIFY-004 implementation permits ACTIVE or TRIALING subscriptions
and currently copies:

```text
billingPeriodId: currentSubscription.billingPeriodId
```

without requiring that value to be non-null.

The provider also exposes `currentPeriodStart/currentPeriodEnd`, but the current
pack request checks plan/meter identity only.

ARCH-008 provider reconciliation requires exact current-cycle identity; it must
not recover cycle membership later from timestamps.

## Required preflight

1. Work only in the launcher-resolved `ARCH-008-SHOPIFY-001` task worktree.
2. Confirm accepted ARCH-007-SHOPIFY-004 behavior is present, including:
   - early existing-purchase replay;
   - provider plan/meter verification outside the Prisma write transaction;
   - transactional re-read of current subscription/plan;
   - Shared canonical Shopify usage idempotency helper;
   - independent purchased-credit balance presentation.
3. Confirm `ProviderSubscription` still exposes:
   - `currentPeriodStart`;
   - `currentPeriodEnd`.
4. Confirm Subscription still links to BillingPeriod through `billingPeriodId`.
5. If those accepted capabilities are absent after normal synchronisation, STOP
   with exact evidence. Do not recreate SHOPIFY-004.

## Primary files

Expected implementation boundary:

- `app/services/billing/billing.service.ts`
- `app/routes/app.billing.tsx`
- `tests/unit/services/billing.service.test.ts`
- `tests/unit/billing-ui.test.ts`

Use actual equivalent filenames only if current accepted source has been renamed.

No database, Background, Admin or Shared repository edits are allowed.

## Required implementation

### A. Preserve existing replay ordering

Keep:

```text
validate intent + purchaseId
-> existing RecoveryCreditPurchase lookup
-> same-shop existing purchase returns immediately
```

This must remain before provider/current-cycle admission checks.

Do not make replay of an existing durable purchase depend on Shopify being
reachable.

### B. Require exact local current-cycle identity

Before provider verification for a **new** purchase require all of:

```text
subscription.status = ACTIVE or TRIALING
subscription.billingPeriodId != null
subscription.currentPeriodStart != null
subscription.currentPeriodEnd != null
subscription.billingPeriod exists
subscription.billingPeriod.id == subscription.billingPeriodId
subscription.billingPeriod.periodStart == subscription.currentPeriodStart
subscription.billingPeriod.periodEnd == subscription.currentPeriodEnd
```

If any condition fails:

```text
create no UsageEvent
create no RecoveryCreditPurchase
grant no entitlement
```

Fail closed with a bounded billing-domain error.

Do not infer a period from `new Date()`, `occurredAt`, trial end or plan cadence.

### C. Require provider/local current-cycle equality

The provider subscription used for the existing plan/meter verification must
also satisfy:

```text
provider.currentPeriodStart != null
provider.currentPeriodEnd != null
provider.currentPeriodStart == local currentPeriodStart
provider.currentPeriodEnd == local currentPeriodEnd
```

Continue to require the accepted plan-handle and meter-handle checks.

A provider subscription with no current billing cycle is not eligible for a
new pack purchase.

### D. Revalidate inside the write transaction

After provider verification and the existing transactional replay check,
re-read current Subscription + BillingPeriod + BillingPlan and require:

```text
same billingPeriodId
same periodStart
same periodEnd
same provider-verified current cycle
same plan handle
same pack meter
same creditsGranted
```

If any of those facts changed:

```text
rollback
create nothing
```

### E. Persist non-null exact cycle identity

Only after the transactional checks pass create:

```text
UsageEvent.metric = RECOVERY_CREDIT_PACK_PURCHASE
UsageEvent.quantity = +1
UsageEvent.billingPeriodId = exact current BillingPeriod.id
UsageEvent.shopifyEventHandle = exact pack meter
UsageEvent.shopifyReportState = PENDING
```

The linked RecoveryCreditPurchase snapshots remain unchanged.

Do not change Shopify App Events quantity/economics.

### F. Merchant purchase eligibility

Purchased-credit **balance** remains visible independently.

The **Buy recovery-credit pack** action must only be rendered when:

```text
existing safe plan/meter conditions
AND exact current local BillingPeriod exists
AND provider current cycle is present
AND provider/local current-cycle boundaries match
```

Do not hide existing purchased credit balance during a trial or sync gap.

If the repository already has an appropriate purchase-eligibility field, extend
it. Otherwise add one bounded server-derived boolean; do not expose provider
credentials or raw billing payloads to the browser.

## Required tests

Add/adjust focused tests proving:

1. existing same-shop purchase replay succeeds before provider/cycle checks;
2. ACTIVE subscription + matching local/provider cycle creates one pending pack
   UsageEvent with the exact non-null `billingPeriodId`;
3. local `billingPeriodId = null` creates no UsageEvent/purchase;
4. missing local current period boundary creates no UsageEvent/purchase;
5. provider current cycle missing creates no UsageEvent/purchase;
6. provider/local cycle boundary mismatch creates no UsageEvent/purchase;
7. transaction re-read observes changed billingPeriodId/boundary and rolls back;
8. plan/meter/pack-size freshness checks from SHOPIFY-004 remain intact;
9. purchased-credit balance remains visible when purchase eligibility is false;
10. Buy form is hidden when no exact current cycle is available;
11. no entitlement counter is updated by this request path.

## Out of Scope / MUST NOT

- No Prisma schema/migration.
- No Background reconciliation implementation.
- No App Events publisher change.
- No pricing or pack-size redesign.
- No manual Billing API / one-time purchase API.
- No date-window inference.
- No removal of existing purchased credits during trial.
- No cross-repository edits.

## Acceptance Criteria

- [ ] Every newly created pack UsageEvent has a non-null exact billingPeriodId.
- [ ] Provider and local current-cycle boundaries must match before creation.
- [ ] Stale cycle changes are caught inside the write transaction.
- [ ] Existing purchase replay remains provider-independent.
- [ ] Trial/no-current-cycle state cannot create a new pack purchase.
- [ ] Existing purchased balance remains visible.
- [ ] No entitlement is granted by the request path.
- [ ] No schema/cross-repository change is introduced.

## Validation

Run focused tests first:

```bash
npm test -- --run \
  tests/unit/services/billing.service.test.ts \
  tests/unit/billing-ui.test.ts
```

Then use the repository's existing validation commands:

```bash
npm run typecheck
npm run build
git diff --check
```

If repository-wide typecheck retains documented pre-existing unrelated
diagnostics, record them exactly and prove no new touched-file diagnostic was
introduced.

Do not invent a lint command if the current package does not define one.

## Stop / return rule

After implementation and validation:

1. complete Completion Report;
2. set status `review`;
3. return to `moda_architect`;
4. STOP.

Do not begin `ARCH-008-BACKGROUND-002`.

## Completion Report

### Status

In Progress

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
