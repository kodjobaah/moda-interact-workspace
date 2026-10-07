---
id: ARCH-027-SHOPIFY-002
architecture_id: ARCH-027
title: Record Shopify billing command history in the common BillingOperation ledger
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 106
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-SHOPIFY-001
enables: []
created: 2026-10-07
updated: 2026-10-07
---

# Record Shopify billing command history in the common BillingOperation ledger

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Adopt the Shop-owned provider-neutral `billing.BillingOperation` ledger for existing Shopify billing commands without changing Shopify billing product behaviour or replacing Shopify's current pending-state/reconciliation mechanics.

## Context

`ARCH-027-DATABASE-001` introduces one provider-neutral billing command-intent/history ledger:

```text
Shop
    -> BillingOperation[]
```

`BillingOperation` has required `shopId`, no `subscriptionId`, and no provider discriminator. Shopify/Woo ownership is derived from `Shop.platform`.

The existing Shopify implementation already has durable current/pending projection fields on `Subscription` and dedicated purchase/usage rows. ARCH-027 does not remove those mechanisms. This task adds historical command provenance so equivalent Shopify and Woo merchant billing actions share one business-operation ledger.

## Scope

Modify only `moda-interact` Shopify billing command/reconciliation code and focused tests.

Record `BillingOperation` for the existing Shopify command paths corresponding to:

```text
SUBSCRIPTION_CREATE
PLAN_SWITCH
CANCEL
ONE_TIME_CHARGE
```

Use the existing authenticated Shop as `BillingOperation.shopId`.

Preserve existing Shopify provider APIs, pending fields and reconciliation behaviour.

## Out of Scope

- Removing or deriving `Subscription.pendingPlanId`, `pendingShopifyPlanHandle` or `pendingEffectiveAt`.
- Replacing Shopify provider lifecycle/reconciliation types.
- Changing Shopify plan-change, cancellation or top-up product behaviour.
- Creating a Shopify-specific operation table.
- Adding a provider discriminator to `BillingOperation`.
- Woo command/webhook/reconciliation implementation.
- Database migrations.
- Gateway/system-test implementation.

## Requirements

### R1 — Shop ownership and provider boundary

Every Shopify operation MUST use the authenticated Shopify `Shop.id` as `BillingOperation.shopId`.

The task MUST validate `Shop.platform = SHOPIFY` at the existing trusted command boundary and MUST NOT store a duplicate provider discriminator on the operation.

### R2 — Preserve existing pending projection

The common operation ledger is durable history/intent. Existing Shopify `Subscription.pending*` fields remain the live pending projection in ARCH-027 and continue to drive current provider reconciliation.

Creating or confirming a `BillingOperation` MUST NOT change when existing Shopify pending/current Subscription fields are written or cleared.

### R3 — Command identity

For each existing Shopify merchant billing command, create/reuse exactly one `BillingOperation` under the task-defined deterministic `requestKey`/`requestFingerprint` rules appropriate to that current command path.

Retries MUST NOT create duplicate operations for the same `(shopId, requestKey)`.

### R4 — Generic provider reference

Where the existing Shopify provider workflow exposes a stable billing reference, store it in `BillingOperation.providerReference` with the database write-once semantics. Do not fabricate a reference where none exists.

### R5 — Top-up provenance

For a Shopify predefined recovery-credit purchase, the operation MUST be linked to the exact `RecoveryCreditPurchase` row. Existing `RecoveryCreditPurchase.usageEventId` / `UsageEvent` accounting provenance remains authoritative and unchanged.

### R6 — Resolution state

When existing trusted Shopify reconciliation establishes that the command's requested business outcome is current, transition the matching operation to `CONFIRMED` using a focused helper/service rather than duplicating reconciliation rules.

Ambiguous provider outcomes must not be represented as confirmed merely to complete the ledger.

## Work Items

- [ ] Update the nested database dependency to the accepted ARCH-027 database revision and regenerate Prisma.
- [ ] Add a focused Shopify billing-operation helper/service for operation create/reuse/state transitions.
- [ ] Record `SUBSCRIPTION_CREATE` intent in the existing initial paid-subscription path.
- [ ] Record `PLAN_SWITCH` intent in the existing hosted plan-change path.
- [ ] Record `CANCEL` intent in the existing cancellation path.
- [ ] Record `ONE_TIME_CHARGE` intent and link it to the exact `RecoveryCreditPurchase`.
- [ ] Integrate confirmation updates with existing trusted Shopify reconciliation without changing projection behaviour.
- [ ] Add focused idempotency, provider-reference and provider-isolation tests.

## Interfaces / Contracts

Database contract owner:

`ARCH-027-DATABASE-001`

Consumed model:

```text
billing.BillingOperation
    shopId
    kind
    state
    requestKey
    requestFingerprint
    merchantPricingPlanId?
    merchantPricingUsageEventId?
    recoveryCreditPurchaseId?
    providerReference?
```

Provider selection:

```text
BillingOperation.shopId -> Shop.platform = SHOPIFY
```

No cross-service runtime contract is introduced.

## Dependencies

- `ARCH-027-SHOPIFY-001`

## Enables

None directly. This task is a terminal implementation dependency of `ARCH-027-SYSTEM-TEST-001`.

## Acceptance Criteria

- [ ] Equivalent Shopify create/switch/cancel/top-up commands create/reuse Shop-owned `BillingOperation` history.
- [ ] `BillingOperation` stores neither `subscriptionId` nor provider discriminator.
- [ ] Existing Shopify `Subscription.pending*` semantics and merchant-visible billing behaviour remain unchanged.
- [ ] `(shopId, requestKey)` retries do not create duplicate operations.
- [ ] Shopify top-up operation links to the exact `RecoveryCreditPurchase`, whose existing `UsageEvent` provenance remains intact.
- [ ] Woo Shops cannot be processed by the Shopify operation integration.
- [ ] Operation confirmation is driven only by existing trusted Shopify outcome/reconciliation evidence.

## Validation

- [ ] focused Shopify billing-operation unit tests
- [ ] existing hosted plan-change/cancellation tests
- [ ] existing top-up purchase/refund tests
- [ ] TypeScript typecheck
- [ ] lint for changed files
- [ ] production build where required by the repository task contract

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to review, return the Completion Report to `moda_architect` and STOP. Do not begin system-test work.

## Implementation Notes

Prefer a small focused billing-operation collaborator called from existing Shopify command/reconciliation services. Do not turn this task into a rewrite of those services or remove current pending projection fields.

## Completion Report

### Status

Not Started

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
