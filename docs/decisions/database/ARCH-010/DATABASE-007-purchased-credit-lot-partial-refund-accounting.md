---
id: ARCH-010-DATABASE-007
architecture_id: ARCH-010
title: Add purchased-credit lot accounting and multi-partial-refund durability
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 67
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-010-ADMIN-002
  - ARCH-010-BACKGROUND-014
  - ARCH-010-SHOPIFY-017
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-DATABASE-007: Add purchased-credit lot accounting and multi-partial-refund durability

## Objective

Make each provider-confirmed `RecoveryCreditPurchase` a durable purchased-credit lot so Moda can prove exactly how many credits from that historical purchase are committed, reserved, held for refund, already refunded and still refundable.

This task changes schema/migration/validation only. It does not implement runtime reservation, Admin workflow, Shopify UI, provider refund calls or negative App Events.

## Baseline to inspect first

Inspect the actual integrated schema/migrations before editing, especially:

```text
moda-interact-database/prisma/schema.prisma
moda-interact-database/prisma/migrations/
moda-interact-database/scripts/validate-recovery-credit-pack-schema.mjs
moda-interact-database/scripts/validate-billing-lifecycle-schema.mjs
```

The supplied architecture snapshot contains:

```text
ShopEntitlementCounter.refundingQuantity
RecoveryCreditPurchase.creditsGranted
RecoveryCreditPurchase.refund  (singular)
RecoveryCreditRefund.purchaseId @unique
RecoveryCreditRefund.creditsSnapshot
UsageReservation counter-level ownership only
```

Do not assume the developer workspace is identical; re-read it.

## Required target model

### RecoveryCreditPurchase lot quantities

Add durable non-negative integer quantities equivalent to:

```text
committedQuantity Int @default(0)
reservedQuantity  Int @default(0)
refundingQuantity Int @default(0)
refundedQuantity  Int @default(0)
version           Int @default(0)
```

`creditsGranted` remains the immutable historical original grant.

Derived per-lot refundable quantity is exactly:

```text
max(
  creditsGranted
  - committedQuantity
  - reservedQuantity
  - refundingQuantity
  - refundedQuantity,
  0
)
```

Do not add a persisted `availableQuantity` column.

### UsageReservation lot identity

Add a nullable relation from `UsageReservation` to the exact `RecoveryCreditPurchase` that funded a purchased-credit reservation.

Use a clearly named relation such as:

```text
purchasedCreditPurchaseId String?
purchasedCreditPurchase   RecoveryCreditPurchase?
```

Do not overload the paid-period included-credit relation from ARCH-010-DATABASE-002.

A purchased-credit reservation must be able to identify both:

```text
aggregate ShopEntitlementCounter
exact RecoveryCreditPurchase lot
```

### Multiple refunds per purchase

Change:

```text
RecoveryCreditPurchase.refund RecoveryCreditRefund?
RecoveryCreditRefund.purchaseId @unique
```

to a one-to-many relationship.

One purchase may have multiple historical partial refund records.

### Refund credit quantities

Replace the full-pack-only meaning of `creditsSnapshot` with explicit partial-refund quantities.

Target semantics must include at least:

```text
purchaseCreditsGrantedSnapshot Int
creditsRequested               Int
creditsApproved                Int?
creditsRefunded                Int?
```

If backwards compatibility requires retaining `creditsSnapshot`, document it as legacy and do not use it as the new requested quantity.

All new quantity fields must be positive safe whole-credit quantities at application validation boundaries.

### Provider settlement evidence

Add durable provider settlement fields sufficient to audit the human Shopify action without making Moda monetary data authoritative:

```text
providerActionKind  REFUND | CREDIT
providerReference   bounded string
providerAmount      Decimal?
providerCurrency    bounded currency code?
providerConfirmedAt
providerConfirmedByPlatformAdminId
```

Use a Prisma enum for `providerActionKind` if the repository convention prefers typed enums.

`REFUND` means a Shopify Partner Dashboard partial/full refund of a paid charge.

`CREDIT` means Shopify-side credit/adjustment for a not-yet-paid charge.

Do not store a locally computed expected monetary amount as provider truth.

### Settlement mode compatibility

ARCH-010 partial refunds do not create new `CURRENT_CYCLE_APP_EVENT_CORRECTION` events.

Do not destructively remove legacy enum/data if existing migrations have created them. Preserve readable legacy rows.

New ARCH-010 request/approval code must be able to distinguish the Partner Dashboard refund/credit provider action without selecting negative App Event settlement.

### RecoveryCreditPurchase.status

Do not require new ARCH-010 partial-refund completion to set `RecoveryCreditPurchase.status=REFUNDED`.

Keep original provider-confirmation state independent from refundable/spendable quantity.

Retain legacy enum values for existing data unless an architect-approved migration explicitly removes them.

## Deterministic migration/backfill

This task MUST backfill lot accounting for existing provider-confirmed purchased credits without resetting aggregate balances.

### Purchase order

Canonical lot order:

```text
activatedAt ASC NULLS LAST
createdAt   ASC
id          ASC
```

For a provider-confirmed purchase with null `activatedAt`, use `createdAt` as the deterministic historical ordering fallback. Do not invent current timestamps.

### Existing purchased reservations

Existing purchased-credit `UsageReservation` rows must be associated to purchase lots deterministically.

Current recovery reservations are expected to use positive whole quantities. If the integrated data contains a purchased reservation that cannot be allocated exactly without splitting across lots, STOP migration rather than guess.

Assign reservation quantities FIFO across provider-confirmed purchase lots while preserving reservation chronological order:

```text
reservation.createdAt ASC
reservation.id ASC
```

After assignment:

```text
COMMITTED -> purchase.committedQuantity
RESERVED  -> purchase.reservedQuantity
AMBIGUOUS -> purchase.reservedQuantity
RELEASED  -> no current lot consumption/hold
```

Preserve historical lot relation for RELEASED reservations if assigned; it must not increase active quantities.

### Existing refund rows

If integrated data contains ARCH-009 refund rows:

- completed full-pack legacy refund: backfill `refundedQuantity` from durable legacy evidence;
- active hold: backfill `refundingQuantity` from durable legacy evidence;
- do not reinterpret rejected/withdrawn requests as active holds;
- if the durable evidence is ambiguous, STOP and report the affected IDs.

### Aggregate reconciliation invariant

After backfill, for each shop:

```text
aggregate committedQuantity == sum(purchase.committedQuantity)
aggregate reservedQuantity  == sum(purchase.reservedQuantity)
aggregate refundingQuantity == sum(purchase.refundingQuantity)
```

and:

```text
aggregate grantedQuantity
== sum(purchase.creditsGranted - purchase.refundedQuantity)
```

for provider-confirmed purchased-credit lots included in the aggregate.

If existing data cannot satisfy the equality without guessing, migration must stop/fail loudly.

## Required indexes/constraints

At minimum add indexes supporting:

```text
purchase FIFO selection by shop/status/activatedAt/createdAt/id
refund lookup by purchaseId/status/createdAt
purchased reservation lookup by purchasedCreditPurchaseId/status
```

Add database check constraints where the repository migration pattern supports them so lot quantities cannot be negative and:

```text
committed + reserved + refunding + refunded <= creditsGranted
```

If Prisma cannot express a required CHECK, use migration SQL and document it.

## Explicit non-goals

Do not:

- implement FIFO runtime reservation;
- implement Admin refund screens/actions;
- implement merchant refund CTA;
- emit negative/fractional Shopify App Events;
- change Free lifetime entitlement;
- change plan/cancellation lifecycle;
- make Admin accessible to merchants.

## Required tests/validation

Add/extend schema validation proving at minimum:

1. purchase lot quantity fields exist with zero defaults;
2. multiple refunds per purchase are allowed;
3. refund quantity fields are distinct from original pack-size snapshot;
4. provider action/evidence fields exist;
5. purchased reservation can reference exact purchase lot;
6. FIFO/backfill fixture with two purchases and committed/reserved reservations preserves aggregate balance exactly;
7. ambiguous/impossible backfill fails rather than guessing;
8. existing completed/held legacy refund fixture maps to refunded/refunding quantities correctly;
9. no migration resets `creditsGranted`, aggregate committed/reserved/refunding, Free lifetime credits or BillingPeriods;
10. `prisma validate` and repository schema validators pass.

Run the actual database repository validation scripts declared by `package.json` and task conventions, plus:

```text
git diff --check
```

## Stop conditions

STOP and return to `moda_architect` if:

- existing purchased reservations cannot be deterministically mapped to lots;
- existing aggregate balances disagree with reconstructable purchase/reservation history;
- a required schema change would destroy legacy refund evidence;
- another migration already implements incompatible lot/refund semantics.

Do not invent a balancing adjustment.

## Completion Report

Populate all standard completion evidence, including exact migration/backfill fixtures and any legacy rows encountered.
