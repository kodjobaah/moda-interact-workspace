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
status: pending
priority: 84
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-010
enables:
  - ARCH-010-ADMIN-005
  - ARCH-010-SHOPIFY-021
created: 2026-09-11
updated: 2026-09-12
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
