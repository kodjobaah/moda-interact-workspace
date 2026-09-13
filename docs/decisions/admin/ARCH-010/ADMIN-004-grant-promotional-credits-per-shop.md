---
id: ARCH-010-ADMIN-004
architecture_id: ARCH-010
title: Create and activate GLOBAL, PLAN and SHOP promotion campaigns
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 84
executor: copilot
claimed_at: '2026-09-13T12:35:36Z'
attempt: 1
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-ADMIN-010
enables:
- ARCH-010-ADMIN-005
- ARCH-010-SHOPIFY-021
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-ADMIN-004: Create and activate GLOBAL, PLAN and SHOP promotion campaigns

## Objective

Replace the old direct one-shop credit-grant concept with a SUPER_ADMIN-only campaign-authoring workflow. Admin creates an optional merchant offer with exactly one targeting scope (`GLOBAL`, `PLAN`, `SHOP`), a fixed recovery-credit quantity and a bounded running window. Creating/activating a campaign does **not** grant credits to merchants.

Merchants never access `moda-interact-admin`.

## Inspect before editing

```text
src/app/(protected)/**
src/components/admin/**
src/app/actions/**
src/lib/admin/**
src/lib/auth/platform-admin.ts
database/prisma/schema.prisma
```

Use the integrated Admin navigation/component conventions rather than assuming the prototype files still exist under the same names.

## Required behaviour

Provide SUPER_ADMIN campaign create/edit-before-activation support for:

```text
name
merchantDescription?       # merchant-facing campaign copy
scope = GLOBAL | PLAN | SHOP
quantity > 0
startsAt
expiresAt
```

Target controls:

```text
GLOBAL -> no target field
PLAN   -> exact BillingPlan.id selected from durable plan mapping
SHOP   -> exact Shop.id selected from tenant directory/search
```

Server validation must reject mixed/missing target shapes even if the client is bypassed.

## Activation

Activation must:

1. re-read campaign state in the transaction/action;
2. require DRAFT;
3. require valid target/quantity/window;
4. set `status=ACTIVE` and the activation/start state according to the DATABASE-010 contract;
5. append the required `PromotionCampaignEvent` audit evidence;
6. never create `PromotionalCreditGrant`, `MerchantPromotionSelection`, Shopify App Event, BillingAllowanceAdjustment or entitlement counter mutation.

After first activation, scope/target/quantity are immutable. The Admin UI must not imply that those can be changed later; a materially different offer is a new campaign.

## Security

- SUPER_ADMIN only;
- use existing platform-admin session/authorization conventions;
- no merchant Shopify session path;
- no raw Prisma error/stack leakage;
- exact Shop/BillingPlan IDs are resolved server-side.

## Required tests

At minimum prove:

1. non-SUPER_ADMIN cannot create/activate;
2. GLOBAL validates with no target;
3. PLAN requires exact BillingPlan;
4. SHOP requires exact Shop;
5. mixed target shape is rejected;
6. quantity/window validation is server-side;
7. activation writes audit event;
8. activation creates zero merchant grants/selections/counter changes;
9. post-activation target/quantity edits are rejected;
10. no Shopify/App Event call exists.

Run focused security/action/UI tests plus repository typecheck/lint/build/full tests as normally required and `git diff --check`.

## Non-goals

Do not implement merchant selection, consumption, campaign reopen/close/history, usage reporting, email/WhatsApp marketing delivery, campaign codes or automatic enrolment.

## Stop conditions

Stop if DATABASE-010 has not landed or if current Admin authorization/tenant-plan lookup cannot resolve exact durable IDs without inventing a second identity system.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `src/app/(protected)/promotions/page.tsx`
- `src/app/actions/promotions.ts`
- `src/components/admin/admin-shell.tsx`
- `src/components/admin/promotion-campaign-form.tsx`
- `src/components/admin/sidebar.tsx`
- `src/lib/admin/promotion-validation.ts`
- `src/lib/admin/promotions.ts`
- `tests/security/admin-promotions.test.mjs`
- `tests/unit/promotion-validation.test.ts`

### Work Completed
- Added a protected Admin campaign history/editor route with exact active BillingPlan and Shop selectors.
- Added SUPER_ADMIN-only server actions for draft creation, draft editing, and transactional activation.
- Added server-side validation for GLOBAL/PLAN/SHOP target exclusivity, exact durable target lookup, positive bounded quantity, and ordered campaign windows.
- Activation re-reads the campaign, requires DRAFT, preserves immutable commercial terms, sets ACTIVE, and appends `PromotionCampaignEvent.ACTIVATED` evidence.
- Creation appends `PromotionCampaignEvent.CREATED` evidence.
- No merchant grant, selection, entitlement counter, Shopify App Event, or compatibility-model mutation is present.

### Validation Results
- `node --experimental-strip-types --test tests/unit/promotion-validation.test.ts`: 3 passed.
- `node --test tests/security/admin-promotions.test.mjs tests/unit/promotion-validation.test.ts`: 8 passed.
- `npm test`: passed; existing observability tests that require a prior build were skipped as designed.
- `npm run lint`: passed with two unchanged warnings in `src/components/admin/queue-monitor.tsx`.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed; existing BullMQ optional-dependency/critical-dependency warnings remain.
- `git diff --check`: passed.
- Exact clean-baseline search: no implementation references to removed compatibility symbols; historical assertions remain in the existing regression test.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-004`
- Implementation branch: `task/ARCH-010-ADMIN-004`
- Implementation commit/push: `6df7899` pushed to `origin/task/ARCH-010-ADMIN-004` in `moda-interact-admin`.
- Parent claim commit/push: `54288b7` pushed to `origin/task/ARCH-010-ADMIN-004` in `moda-interact-workspace`.
- Database submodule gitlink remained unchanged at accepted commit `5443afd`.

### Architect Review
Pending.
