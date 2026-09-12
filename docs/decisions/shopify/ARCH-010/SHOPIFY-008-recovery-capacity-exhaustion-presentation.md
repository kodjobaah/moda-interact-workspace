---
id: ARCH-010-SHOPIFY-008
architecture_id: ARCH-010
title: Present recovery-capacity exhaustion on merchant dashboard and history
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 58
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHOPIFY-009
  - ARCH-010-SHOPIFY-012
  - ARCH-010-BACKGROUND-009
  - ARCH-010-SHARED-004
enables: []
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SHOPIFY-008: Present recovery-capacity exhaustion on merchant dashboard and history

## Objective

Keep an exhausted merchant in the normal merchant application and make the capacity restriction visible without changing subscription state or hiding usage/history.

This task is **presentation only**. It must not productionise `/app/billing/options`; that work is decomposed into SHOPIFY-009/010/011/012.

## Inspect before editing

```text
app/routes/app/home/route.jsx
app/routes/app/usage/route.jsx
app/routes/app/pending-recoveries/route.jsx
app/components/dashboard/UsageOverview.jsx
app/components/dashboard/Dashboard.jsx
app/components/dashboard/PendingRecoveries.jsx
app/services/merchant-support/system-message-actions.ts
app/i18n/catalogues.js
app/i18n/locales/*.json
```

Read the implemented SHOPIFY-009 capacity read model and SHOPIFY-012 billing-options route first. Do not duplicate their derivation or billing actions in UI code.

## Required behaviour

When the local read model reports `capacitySource = EXHAUSTED`:

- `/app` remains the normal landing page;
- `/app/usage`, event/history/detail and merchant support remain available;
- existing admitted conversations remain available subject to their existing controls;
- render a prominent localized warning explaining that only **new abandoned-checkout recovery initiation** is paused;
- CTA target is exactly `/app/billing/options`;
- do not redirect to billing, onboarding, support or Admin.

Free wording must distinguish lifetime Free exhaustion from cancellation. Paid wording must distinguish monthly included-credit exhaustion from cancellation/contract expiry.

Do **not** show the full exhaustion warning while any capacity source remains. For Paid this includes selected usable promotional capacity first, then current-period included, purchased, then lifetime Free. For Free this includes selected usable promotion, purchased, then lifetime Free.

## Blocked recovery presentation

For a durable recovery with:

```text
status = DETECTED
admissionBlockReason = RECOVERY_CAPACITY_EXHAUSTED
```

render localized semantics equivalent to `Waiting for recovery capacity` anywhere the existing merchant recovery/pending surface exposes that recovery.

Do not present it as sent, failed, cancelled or completed.

## Merchant-support action

Map `BILLING_RECOVERY_CAPACITY_EXHAUSTED` to `/app/billing/options` with localized action text equivalent to `Manage recovery capacity`.

Keep historical `BILLING_FREE_ALLOWANCE_EXHAUSTED` renderable and point it to the same merchant capacity route where safe.

No merchant action may link to `moda-interact-admin`.

## Performance / source of truth

Dashboard exhaustion rendering must use SHOPIFY-009's PostgreSQL-only read model. A normal dashboard request must not call Shopify/Partner merely to decide whether capacity is exhausted.

## Required tests

At minimum prove:

1. Free purchased exhausted + lifetime Free exhausted shows the warning;
2. Paid selected promotional + included + purchased + lifetime Free all exhausted shows the warning;
3. purchased available suppresses the full warning even when lifetime Free remains;
3a. Paid selected promotional unavailable + included/purchased exhausted + lifetime Free available suppresses the full warning;
4. dashboard/history/usage remain accessible while exhausted;
5. warning CTA is `/app/billing/options`;
6. blocked DETECTED recovery shows waiting-for-capacity semantics;
7. generic exhaustion SYSTEM message action points to `/app/billing/options`;
8. historical Free exhaustion message remains renderable;
9. no merchant link points to Admin;
10. dashboard capacity rendering does not invoke Shopify/Partner;
11. new strings are present with locale placeholder parity.

## Non-goals

Do not change:

- recovery admission/background processing;
- billing-options loader/action/components;
- top-up purchase semantics;
- plan-change semantics;
- subscription state;
- refund/cancellation behaviour.

## Validation

Inspect `package.json`, then run the repository-declared focused tests plus, when present:

```bash
npm test
npm run typecheck
npm run build
git diff --check
```

## Stop conditions

STOP and return to `moda_architect` if SHOPIFY-009 cannot provide the capacity state without a Shopify/Partner call, or SHOPIFY-012 has not produced a real `/app/billing/options` destination.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Validation Results
Populate during implementation.


## Final promotional capacity presentation

The exhaustion UI must treat promotional credits as a distinct source ahead of purchased/lifetime Free:

```text
Free: promotional -> purchased -> lifetime Free
Paid: selected promotional -> included -> purchased -> lifetime Free
```

When promotional credits remain, do not show full exhaustion. When promotional credits are the active fallback, presentation may say Moda-provided promotional credits are funding new recoveries. Do not expose internal campaign reference/reason/admin identity.
