---
id: ARCH-010-SHOPIFY-020
architecture_id: ARCH-010
title: Present promotional recovery credits separately in merchant capacity surfaces
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
  - ARCH-010-DATABASE-009
  - ARCH-010-SHOPIFY-009
  - ARCH-010-SHOPIFY-012
enables:
  - ARCH-010-SYSTEM-TEST-001
  - ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SHOPIFY-020: Present promotional recovery credits separately in merchant capacity surfaces

## Objective

Expose the merchant's promotional recovery-credit balance as a separate, non-refundable capacity source and explain the final capacity priority without exposing internal Admin campaign metadata.

Canonical merchant order:

```text
FREE
  promotional -> purchased -> lifetime Free

PAID
  monthly included -> promotional -> purchased -> lifetime Free
```

## Inspect before editing

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/routes/app/billing/route.tsx
app/routes/app/billing/options/route.tsx
app/routes/app/home/route.jsx
app/routes/app/usage/route.jsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/i18n/locales/*.json
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
tests/unit/billing-i18n.test.ts
package.json
```

Use actual integrated filenames if prerequisite ARCH-010 capacity/billing-options tasks refactor these surfaces.

## 1. Capacity projection consumption

Consume SHOPIFY-009's amended local projection containing:

```text
promotional:
  granted
  committed
  reserved
  remaining
```

and `capacitySource = PROMOTIONAL` when it is the next usable source.

Do not query `PromotionalCreditGrant` history to decide runtime capacity; the aggregate entitlement counter is the operational source.

## 2. Billing/dashboard presentation

On relevant merchant surfaces show promotional credits separately from:

- monthly included credits;
- purchased credits;
- lifetime Free credits.

Use customer-facing wording equivalent to:

```text
Promotional recovery credits
Provided by Moda. These credits are used before purchased credits and do not expire under the current product terms.
```

Do not describe them as purchased, refundable, monthly or Shopify-billed.

When promotional credits are currently funding new recoveries, the dashboard/capacity state should make that source understandable without alarming the merchant.

## 3. Privacy boundary

Merchant UI MUST NOT expose internal Admin provenance fields such as:

```text
platformAdminId
internal reason
campaignReference
requestKey
internal grant type when it contains operational/support classification
```

Only aggregate balance/use semantics are merchant-facing in ARCH-010.

## 4. Refund presentation

Promotional credits are non-refundable.

The purchased-credit refund flow remains based only on refundable unused `RecoveryCreditPurchase` lots.

Do not include promotional quantity in:

- refundable purchased-credit totals;
- refund request quantity limits;
- Shopify refund/credit guidance.

SHOPIFY-017 may link/explain that promotional and lifetime Free credits are not refundable, but the existing purchased refund CTA remains available for eligible purchased lots.

## 5. Lifecycle presentation

When subscription execution is disabled by:

```text
FROZEN
NO_CONTRACT
inactive/uninstalled/reinstall-pending
```

promotional balances may still be displayed as owned/preserved, but they MUST NOT be represented as currently spendable capacity.

SHOPIFY-009's availability state remains authoritative for whether another recovery can start.

## 6. Translation

Add all new merchant-facing keys using the repository's existing locale discipline.

Do not hard-code English in React/routes.

If the repository's normal workflow requires every supported locale file to contain the key, update every locale using the accepted translation/fallback convention rather than leaving missing-key runtime behaviour.

## Required tests

At minimum prove:

1. promotional balance renders separately from purchased/lifetime Free;
2. `capacitySource=PROMOTIONAL` has correct merchant presentation;
3. Free ordering copy is promotional -> purchased -> lifetime Free;
4. Paid ordering copy is included -> promotional -> purchased -> lifetime Free;
5. promotional credits are described as non-refundable/non-purchased;
6. refund totals/CTA eligibility ignore promotional balance;
7. internal campaign reference/reason/admin identity never appears in merchant serialization/rendering;
8. FROZEN/NO_CONTRACT may display preserved balance but not as spendable;
9. zero/missing promotional counter renders cleanly without configuration error;
10. all required i18n keys pass repository locale tests;
11. no Shopify provider call is added merely to read promotional balance.

Run focused billing/UI/i18n tests, repository-declared typecheck/build/full tests and `git diff --check`.

## Non-goals

Do not:

- let merchants request promotional grants;
- expose campaign history/details;
- make promotional credits refundable;
- add expiry;
- add Shopify/App Event mutations;
- change Admin behaviour;
- change subscription lifecycle state.

## Stop conditions

Stop and return to `moda_architect` if:

- SHOPIFY-009 has not exposed the promotional aggregate;
- merchant UI would require reading internal Admin grant provenance to compute capacity;
- integrated billing/options surfaces no longer match the expected component ownership.

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
