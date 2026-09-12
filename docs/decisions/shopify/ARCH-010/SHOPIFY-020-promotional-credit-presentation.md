---
id: ARCH-010-SHOPIFY-020
architecture_id: ARCH-010
title: Present selected promotion and promo-first recovery capacity
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 85
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SHOPIFY-009
- ARCH-010-SHOPIFY-012
- ARCH-010-SHOPIFY-021
enables:
- ARCH-010-SYSTEM-TEST-001
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SHOPIFY-020: Present selected promotion and promo-first recovery capacity

## Objective

Present the merchant's currently selected promotional campaign/allocation as a separate non-refundable capacity source and explain the final promo-first ordering without exposing internal Admin provenance.

Canonical order:

```text
PAID
  selected promotional -> monthly included -> purchased -> lifetime Free

FREE
  selected promotional -> purchased -> lifetime Free
```

## Required presentation

Consume SHOPIFY-009's local capacity projection and SHOPIFY-021's selected-promotion read model. Show, where relevant:

```text
selected campaign name
promotional credits remaining
campaign expiry
whether promo is currently usable
next fallback capacity source
```

If no promotion is selected, do not present unrelated running offers as owned capacity; SHOPIFY-021 owns the offer catalogue.

If the selected promo is expired/closed/plan-ineligible/exhausted, clearly show that it is not funding new recoveries and route the merchant back to the available-promotion catalogue where appropriate.

## Capacity copy

Merchant-facing copy must reflect:

```text
Selected promotion is used first.
Then Paid monthly allowance (when on Paid).
Then purchased lifetime credits.
Then lifetime Free credits.
```

Promotional credits are non-refundable and create no Shopify charge.

## Lifecycle

FROZEN/NO_CONTRACT/inactive/reinstall-pending merchants may see preserved selected/history information but must not be told the promo is currently spendable. SHOPIFY-009 lifecycle availability remains authoritative.

## Privacy / refunds

Do not expose `platformAdminId`, internal reason, audit events, target IDs or request keys. Never include promo quantity in purchased-credit refund totals/limits/provider refund guidance.

## Translation

Localize all static labels. Do not attempt to machine-translate Admin-authored campaign name/description in this task.

## Required tests

At minimum prove:

1. selected promo renders separately;
2. promo-first Paid ordering copy;
3. promo-first Free ordering copy;
4. no-selected-promo state is clean;
5. expired/closed/ineligible selected promo is not represented as spendable;
6. refund calculations ignore promo;
7. internal metadata does not leak;
8. lifecycle blocks preserve but disable spendability;
9. i18n/static copy checks pass.

## Non-goals

Do not implement offer selection, history, Admin campaign management or Background reservation logic.

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
