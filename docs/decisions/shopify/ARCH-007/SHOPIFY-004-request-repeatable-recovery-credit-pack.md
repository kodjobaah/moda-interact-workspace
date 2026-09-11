---
id: ARCH-007-SHOPIFY-004
architecture_id: ARCH-007
title: Let merchants request repeatable recovery-credit packs
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: pending
priority: 66
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-007-SHOPIFY-002
  - ARCH-007-DATABASE-005
  - ARCH-007-SHARED-006
  - ARCH-007-ADMIN-005
enables:
  - ARCH-007-SYSTEM-TEST-004
created: 2026-09-08
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-SHOPIFY-004: Let merchants request repeatable recovery-credit packs

## Shopify billing mechanism — do not substitute another API

Moda uses Shopify App Pricing.

Do NOT call:
```text
appPurchaseOneTimeCreate
appSubscriptionCreate
billing.request
```

A pack request is billed by creating a durable `UsageEvent` with:
```text
metric = RECOVERY_CREDIT_PACK_PURCHASE
quantity = 1
shopifyEventHandle = current BillingPlan.shopifyRecoveryCreditPackEventHandle
shopifyReportState = PENDING
```

The existing Background App Events publisher later sends it to Shopify.

Credits are NOT granted by this Shopify task.

## Exact files to inspect/change

Principally:
```text
app/routes/app.billing.tsx
app/services/billing/billing.service.ts
app/services/billing/providers/shopify-billing.provider.ts
app/i18n/locales/*.json
existing billing unit tests
```

Do not create a second billing page.

### ARCH-005 merchant UI internationalisation requirement

This task extends an authenticated merchant UI that is already governed by
ARCH-005. Every new or changed merchant-visible string MUST use the existing
merchant ICU/i18n implementation and application-owned `app/i18n/locales/*`
catalogues.

Deterministic requirements:

- do not hard-code new merchant-visible English copy in `app.billing.tsx` or
  server-action UI responses;
- add every new key introduced by this task to all 20 currently declared Shopify
  merchant locale catalogues;
- translate the values naturally for each declared locale rather than copying the
  English value into non-English catalogues;
- preserve ICU placeholder names/semantics exactly;
- reuse the existing ARCH-005 locale resolver/runtime and locale-aware formatting
  helpers;
- do not create a second translation/runtime mechanism.

Any English copy quoted later in this task is source-language meaning, not
permission to embed that literal directly in the component.

## Provider verification change

When the mapped current BillingPlan has `recoveryCreditPackEnabled=true`, current Shopify Active Subscription verification must require the configured `shopifyRecoveryCreditPackEventHandle` to appear as an active usage/TieredPrice item.

For FREE:
- normal recovery usage meter remains absent/null;
- top-up usage meter may be present.

For PAID_METERED:
- normal recovery usage meter and top-up meter are both required and must be distinct.

If the top-up meter cannot be verified, fail closed for TOP-UP PURCHASE only. Do not incorrectly mark the whole active subscription as Free/paid-unmapped if its normal plan mapping remains otherwise valid.

## Billing page presentation

Show:
```text
Purchased recovery credits:
  grantedQuantity - committedQuantity - reservedQuantity
```

Show pack quantity from `recoveryCreditsPerPack`.

Do NOT invent/display a monetary pack price from Moda DB. Copy must say Shopify bills the pack according to the current plan's configured Recovery Credit Pack meter.

Show Buy button only when:
- subscription current status is safe/mapped;
- plan has top-ups enabled;
- pack size > 0;
- top-up meter verified.

A merchant may buy another pack whenever desired, including after a previous pack is exhausted.

## Idempotent purchase request

Loader generates one cryptographically random `purchaseId` for the rendered purchase form.

Form submits:
```text
intent = "BUY_RECOVERY_CREDIT_PACK"
purchaseId = <loader supplied id>
```

Server validation:
- `purchaseId` must be a UUID/non-empty bounded identity according to the implementation's chosen generator;
- ignore all client-supplied pack sizes, plan IDs, meter handles or prices;
- reload current shop/subscription/plan from DB/provider state.

In one Prisma transaction:
1. if `RecoveryCreditPurchase(id=purchaseId)` already exists for this shop, return that existing purchase; create nothing;
2. require current safe mapped plan/top-up config;
3. create `UsageEvent` using the same stable `purchaseId` as the durable billing identity or another explicit stable ID derived from it;
4. set:
   - metric `RECOVERY_CREDIT_PACK_PURCHASE`;
   - quantity `1`;
   - idempotencyKey stable from shop + purchase;
   - `shopifyReportState=PENDING`;
   - `shopifyEventHandle` from current plan top-up meter;
   - `shopifyIdempotencyKey=createShopifyUsageIdempotencyKey(shopId, usageEvent.id)`;
   - current billingPeriodId when available;
5. create `RecoveryCreditPurchase` snapshotting current plan handle, meter handle and `creditsGranted=currentPlan.recoveryCreditsPerPack`;
6. link it to the UsageEvent.

Do not grant/increment credits here.

## UI state

After request creation, show a translated pending message:
```text
"Recovery credit purchase is being confirmed by Shopify."
```

ACTIVE balance appears only after Background activation.

## Required tests

1. Free mapped plan with top-up meter can request a pack.
2. Paid mapped plan can request a pack.
3. Same rendered `purchaseId` submitted twice creates exactly one purchase and one UsageEvent.
4. Different purchase IDs can create repeated pack purchases.
5. client cannot override credits/meter/plan.
6. top-up-disabled/missing-meter/unmapped state fails closed with no UsageEvent.
7. created UsageEvent is metric `RECOVERY_CREDIT_PACK_PURCHASE`, value 1, PENDING, exact mapped meter.
8. no direct Shopify billing/App Events network call is made in the request transaction.
9. credits are not granted before Background reports/activates the purchase.
10. all new merchant-visible copy is translated naturally across all 20 existing locale catalogues using the established ARCH-005 ICU/i18n path; no task-introduced merchant-visible English literal bypasses that path.
11. focused i18n coverage proves every new key exists in all 20 catalogues and resolves through the existing merchant i18n runtime with ICU placeholders preserved.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-SHOPIFY-004` branch and the mirrored parent-workspace `task/ARCH-007-SHOPIFY-004` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Pending

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
None.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status
Pending

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending

### Follow-up
None.

