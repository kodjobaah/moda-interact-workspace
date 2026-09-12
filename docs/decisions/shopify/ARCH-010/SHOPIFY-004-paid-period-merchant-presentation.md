---
id: ARCH-010-SHOPIFY-004
architecture_id: ARCH-010
title: Present current paid-period entitlement to merchants
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SHOPIFY-003
- ARCH-010-DATABASE-013
enables:
- ARCH-010-SHOPIFY-007
- ARCH-010-SHOPIFY-009
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SHOPIFY-004: Present current paid-period entitlement to merchants

## Objective

Align merchant-facing paid billing screens with the new period-scoped included-credit state. A merchant who has successfully completed first paid activation must see the exact current Shopify period and Moda's current-period included capacity, while lifetime balances remain separate.

This is merchant UI only. Never expose or route merchants to `moda-interact-admin`.

## Inspect before editing

```text
app/routes/app/billing/route.tsx
app/routes/app/usage/route.jsx
app/routes/app/home/route.jsx
app/components/dashboard/UsageOverview.*
app/components/dashboard/UsageEvents.*
app/i18n/locales/*.json
app/services/billing/billing.service.ts
tests/unit/billing-ui.test.ts
package.json
```

Reuse existing merchant i18n conventions. Do not hard-code English-only merchant strings.

## Billing service read model

For a safe mapped paid subscription, expose from durable current-period state:

```text
current BillingPeriod id/start/end/status
included grantedQuantity
included committedQuantity
included reservedQuantity
included forfeitedQuantity
included remaining = max(granted - committed - reserved - forfeited, 0)
purchased lifetime granted/committed/reserved/refunding/available
shop-lifetime Free granted/committed/reserved/remaining
```

Do not use shop-wide paid UsageEvent aggregate as the authoritative "included remaining" calculation.

If the paid subscription is ACTIVE but period/counter state is missing/inconsistent, surface the existing safe `configuration unavailable` merchant state rather than displaying invented zero/full allowance.

## Merchant `/app/billing`

For paid plan, show at minimum:

```text
Current plan: <mapped plan name>
Status: ACTIVE
Current period: <Shopify start> - <Shopify end>
Included recoveries: <remaining> of <granted> remaining
Purchased recovery credits: <available> ...
Lifetime Free recoveries: <remaining> of <granted> remaining
```

It is acceptable to show committed/reserved details separately if the existing UI style supports them, but do not confuse reserved with already-consumed usage.

Keep the Shopify-hosted plan-change link.

Keep top-up purchase CTA only when the existing ARCH-008 eligibility checks pass:

```text
current plan active
exact local/provider billing cycle matches
pack meter verified
plan pack configuration enabled
```

Do not make the purchase button appear merely because a paid period counter exists.

## `/app` and `/app/usage`

After successful paid onboarding, normal merchant dashboard/detail/usage routes remain available.

Usage period selection must continue to use durable BillingPeriod ids/boundaries. Where current-period summary displays included capacity, use the period counter. Historical usage events remain event history; do not rewrite them into the new counter.

Do not expose current/past data from another tenant.

## Feature availability

UI navigation/actions may be hidden/disabled according to existing `BillingPlanFeature` mappings, but do not add plan-name conditionals such as `if plan === Growth`.

`moda-interact-admin` remains internal only and must not appear in merchant navigation, buttons, redirects or support links.

## Required tests

Prove at least:

1. paid billing screen reads current period counter;
2. remaining calculation accounts for committed + reserved + forfeited;
3. paid screen does not use shop-wide usage aggregate as included remaining;
4. current period dates render from durable Shopify-derived period;
5. purchased credits render separately;
5a. remaining lifetime Free credits render separately while Paid and are not hidden/reset;
6. missing paid period shows safe configuration-unavailable state;
7. missing paid period counter shows safe configuration-unavailable state;
8. top-up CTA still requires exact ARCH-008 purchase eligibility;
9. plan-change link still points to Shopify-hosted selection flow;
10. merchant routes contain no Admin links/redirects;
11. Free billing UI remains correct;
12. merchant-facing new strings use i18n keys across the repository's supported locale contract.

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test -- tests/unit/billing-ui.test.ts
npm run typecheck
npm run build
git diff --check
```

Run the full declared `npm test` if focused validation passes and repository baseline permits it; report known unrelated baseline failures by baseline ID rather than rediscovering them.

## Non-goals

Do not change Background admission, create periods, implement plan changes, cancellation, refund behaviour, Admin UI, or pricing amounts.

## Stop conditions

STOP if the integrated paid period counter/read model differs materially from ARCH-010-DATABASE-002 or if merchant UI would need to query Shopify directly on every screen render.

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
