---
id: ARCH-010-DATABASE-011
architecture_id: ARCH-010
title: Persist merchant promotion selection and exact promotional grant-lot accounting
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 83
executor: copilot
claimed_at: 2026-09-12T06:42:57Z
attempt: 1
depends_on:
  - ARCH-010-DATABASE-009
  - ARCH-010-DATABASE-010
enables:
  - ARCH-010-ADMIN-006
  - ARCH-010-BACKGROUND-019
  - ARCH-010-SHOPIFY-009
  - ARCH-010-SHOPIFY-021
  - ARCH-010-SHOPIFY-022
created: 2026-09-12
updated: 2026-09-12
---

# ARCH-010-DATABASE-011: Persist merchant promotion selection and exact promotional grant-lot accounting

## Objective

Extend the completed DATABASE-009 promotional ledger so one merchant can claim a campaign exactly once, one promotion can be selected at a time per Shop, and Background can reserve/commit against the exact campaign grant rather than an undifferentiated lifetime aggregate.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
scripts/validate-billing-policy-schema.mjs
docs/generated/prisma-erd.puml
```

Read DATABASE-009 and DATABASE-010 in full before editing.

## 1. Extend PromotionalCreditGrant

Preserve all DATABASE-009 provenance fields. Add campaign-aware fields equivalent to:

```text
campaignId? -> PromotionCampaign
reservedQuantity   Int default 0
committedQuantity  Int default 0
firstSelectedAt?
lastSelectedAt?
selectionCount     Int default 0
firstUsedAt?
lastUsedAt?
exhaustedAt?
version            Int default 0
```

`campaignId` is nullable **only for compatibility with pre-DATABASE-010 direct grant history**.

Add a unique constraint/index equivalent to:

```text
UNIQUE(campaignId, shopId)
```

PostgreSQL NULL semantics may allow historical `campaignId=NULL` rows to coexist; do not invent campaigns for them.

Add quantity integrity checks equivalent to:

```text
quantity > 0
reservedQuantity >= 0
committedQuantity >= 0
reservedQuantity + committedQuantity <= quantity
selectionCount >= 0
```

## 2. One current merchant selection

Add `billing.MerchantPromotionSelection` with one row per Shop:

```text
shopId UNIQUE
promotionalCreditGrantId UNIQUE
selectedAt
updatedAt
version
```

Relations must make it impossible to point a Shop at another Shop's grant through normal service code; add DB-enforceable integrity where practical and require transactional identity checks where a composite FK would overcomplicate the existing schema.

The one-row-per-Shop shape is the durable invariant behind:

> one selected promotion per merchant at any one time.

The row may temporarily point to a grant whose campaign later expires/closes/becomes plan-ineligible; runtime eligibility decides spendability. Selection replacement is owned by SHOPIFY-021.

## 3. Exact reservation ownership

Extend `UsageReservation` with nullable:

```text
promotionalCreditGrantId
```

and relation/index support matching purchased-credit lot ownership.

A promotional reservation must identify the exact grant that funded it. Do not use only the aggregate `ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)` as reservation ownership.

Existing reservation rows migrate with NULL promo grant id.

## 4. Aggregate counter compatibility

Keep `PROMOTIONAL_RECOVERY_CREDITS` for aggregate accounting/reporting compatibility, but after this task it is **not sufficient authority for spendability** because campaign status/expiry/eligibility/current selection are grant-specific.

Do not delete the counter or rewrite DATABASE-009 history.

## 5. Merchant history

The campaign-linked grant must preserve enough durable fields to answer:

- which campaigns this merchant selected;
- which were actually used (`firstUsedAt != null`);
- total original allocation;
- committed usage;
- current held reservation;
- whether allocation is exhausted;
- whether the same campaign was selected again after reopen without replenishment.

No additional history table is required unless implementation proves the above cannot be answered durably without losing important selection events. Do not invent one merely for convenience.

## Required tests / validation

Prove at minimum:

1. one campaign+shop grant maximum;
2. one current selection row per Shop maximum;
3. grant counters cannot become negative/over-allocated;
4. reservation may point to exact promotional grant;
5. existing reservations/grants migrate safely;
6. historical campaign-less grant remains valid compatibility data;
7. no migration auto-selects a promotion;
8. no migration grants more capacity;
9. reopened campaign cannot create a second grant for the same shop because `(campaignId, shopId)` remains unique.

Run normal Prisma/migration/schema/ERD validations and `git diff --check`.

## Non-goals

Do not implement campaign eligibility, selection mutation, Background reserve/commit/release, Admin UI, merchant UI or expiry scheduling.

## Stop conditions

Stop if exact promo-grant reservation ownership cannot be added without conflicting with the already-accepted purchased/included UsageReservation ownership model; return the conflict to `moda_architect` rather than creating a parallel reservation table.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
