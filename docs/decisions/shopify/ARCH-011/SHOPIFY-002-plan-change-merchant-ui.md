---
id: ARCH-011-SHOPIFY-002
architecture_id: ARCH-011
title: Present deterministic upgrade and deferred-downgrade state to merchants
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-SHOPIFY-001
- ARCH-011-BACKGROUND-002
enables:
- ARCH-011-SYSTEM-TEST-001
created: 2026-09-14
updated: 2026-09-14
---
# ARCH-011-SHOPIFY-002

## Authorized implementation surface
```text
app/routes/app/billing/route.tsx
app/routes/app/billing/options/route.tsx
app/components/dashboard/SubscriptionChangePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/i18n/locales/*.json
tests/unit/billing-ui.test.ts
```
Do not change server transition/application logic.

## Exact presentation rules
Billing route/options loader must expose from durable rows: effective current plan, active provider cycle, unresolved transition status, requested target, provider-confirmed target, current BillingPlanSegments ordered effectiveFrom, pending lower plan/effectiveAt, purchased balance, top-up eligibility.

UI labels:
- REQUESTED: `Upgrade requested — waiting for Shopify confirmation`.
- PROVIDER_CONFIRMED: `Shopify confirmed <plan> — applying upgrade`.
- NEEDS_ATTENTION: `Plan change needs reconciliation`; no claim credits are active.
- requested!=confirmed: show both `Requested in Moda: X` and `Confirmed by Shopify: Y`.
- pending lower: `Scheduled for next billing cycle`; current plan remains visually current.
- lower option action copy must say it takes effect next billing cycle; never show prorated refund/credit.
- direct Free->Scale shows no Starter/Growth fabricated segments.
- top-up button disabled with transition-in-progress explanation when server eligibility false; purchased lifetime balance remains visible.

Remove `rank` as billing-direction authority from `SubscriptionChangePanel`; consume server-provided `direction` literal only. Remove hard-coded mock plans from production `/app/billing/options` route.

## Validation
```text
npx vitest run tests/unit/billing-ui.test.ts
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
