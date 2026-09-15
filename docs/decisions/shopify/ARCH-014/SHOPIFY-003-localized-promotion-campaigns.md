---
id: ARCH-014-SHOPIFY-003
architecture_id: ARCH-014
title: Render promotion offers and history from exact localized campaign translations
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 52
executor:
claimed_at:
attempt: 1
depends_on:
- ARCH-014-DATABASE-003
enables:
- ARCH-014-SYSTEM-TEST-002
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-SHOPIFY-003

## Objective

Stop exposing the internal promotion campaign name/single legacy description to merchants. Promotion offers and promotion history must use the exact `PromotionCampaignTranslation` for the merchant application's resolved supported locale.

## Binding GPT-5.6 Luna rule

Implement only localization of promotion merchant copy. Do not change campaign eligibility, selection, grant/reservation accounting, concurrency, lifecycle, billing-plan targeting or route-access policy.

## Current defect

Current merchant code returns/renders:

```text
campaign.name
campaign.merchantDescription
```

Those are not a multilingual merchant content contract. After this task:

```text
PromotionCampaign.name = internal Admin-only
PromotionCampaignTranslation.merchantTitle = merchant-facing
PromotionCampaignTranslation.merchantDescription = merchant-facing
```

## Exact locale resolution

In `app/routes/app/promotions/route.tsx` keep the existing `merchantUiContext(settings, session)` calculation.

Derive the canonical promotion locale exactly with:

```ts
const promotionLocale = createMerchantI18n(merchantUi).catalogueLocale;
```

This gives one of the existing exact supported catalogue locales (`cs`, `pt-BR`, `zh-Hant`, etc.). Do not infer locale from country, currency, browser APIs or campaign scope.

Pass this exact locale into both promotion service readers.

Change service signatures/call sites/tests consistently to require the locale explicitly. Do not hide a default English fallback in the service API.

## Eligible offers query

Update `getEligiblePromotionOffers(...)` so each ACTIVE campaign query selects only the exact requested translation, e.g. equivalent to:

```text
translations where locale == requested locale
select merchantTitle + merchantDescription
```

The projected merchant offer must expose:

```text
merchantTitle
merchantDescription
```

and MUST NOT expose/use `campaign.name` as the merchant title.

Because ADMIN-008 activation requires 20/20, an ACTIVE campaign missing the exact requested translation is an integrity defect. Fail closed for the affected offer: do not substitute English, internal campaign name, legacy scalar description or a neighboring locale. Omit that campaign from the eligible offer list and make the condition observable in deterministic test evidence (existing logger convention if one exists; do not add a logging framework solely for this task).

## Promotion history query

Update history projection to select the exact requested campaign translation and expose:

```text
campaignTitle
```

instead of `campaignName` derived from internal `PromotionCampaign.name`.

For a historical grant whose exact translation is unexpectedly missing, return `campaignTitle: null`; the route must display an existing/new generic localized static key such as `promotions.history.titleUnavailable` rather than leaking internal campaign name or falling back to English.

Add that static key to **all 20 existing merchant catalogue files** with appropriate translations following repository conventions. The fallback is only for integrity/legacy history display; active offer publication still requires 20/20.

## Route rendering

Available offer card:

```tsx
<h3>{offer.merchantTitle}</h3>
<p>{offer.merchantDescription}</p>
```

Do not conditionally hide description because activated translations require non-empty descriptions.

History card:

```text
entry.campaignTitle ?? i18n.t("promotions.history.titleUnavailable")
```

All other credits, dates, status and selection actions remain unchanged.

## Selection action

`selectPromotionOffer(...)` does not need localized strings to mutate selection. Do not add translation requirements to the selection transaction beyond existing ACTIVE/eligibility checks; the activation gate is the publication invariant.

Do not make translation rows billing/accounting authority.

## Exact-locale rule

For supported locales, do not implement:

```text
pt-BR -> pt-PT fallback
zh-Hant -> zh-Hans fallback
fr -> en fallback
```

Exact resolved `catalogueLocale` only.

## Mandatory tests

Update/add tests proving:

1. route resolves locale from `merchantUiContext` through `createMerchantI18n(...).catalogueLocale`;
2. `fr` offer reads French row;
3. `ja` offer reads Japanese row;
4. `pt-BR` and `pt-PT` remain distinct;
5. `zh-Hans` and `zh-Hant` remain distinct;
6. offer uses merchantTitle, never internal campaign name;
7. offer uses localized description, never legacy scalar merchantDescription;
8. missing exact translation causes ACTIVE offer omission, not English fallback;
9. history uses exact localized campaignTitle;
10. missing history translation uses localized generic unavailable-title key, not internal name;
11. all 20 catalogues contain the new generic key and catalogue validation passes;
12. promotion eligibility/selection concurrency tests remain unchanged/pass;
13. grant quantity, remaining calculation and lifecycle statuses are unchanged;
14. no database writes are added to read routes;
15. no BillingPlan targeting semantics are changed by this task.

## Required validation

Run repository-declared:

```bash
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

Also scan:

```bash
rg -n 'offer\.name|campaignName|merchantDescription: campaign\.merchantDescription|campaign\.name' app/routes/app/promotions app/services/promotions tests
rg -n 'titleUnavailable' app/i18n app/routes/app/promotions tests
```

Expected production merchant-presentation path contains no internal-name/legacy-description fallback.

## Stop conditions

STOP if exact locale cannot be derived from the existing merchant i18n runtime, if DATABASE-003 is not integrated, or if implementation appears to require changing promotion eligibility/accounting semantics. Return to `moda_architect`.

## Completion Report

Status: Blocked.

The prepared implementation worktree is at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-SHOPIFY-003` with database submodule commit `f202931c58dba7f9fcc53c74333736e978e8b6de`. That submodule checkout contains no `PromotionCampaignTranslation` model, relation, migration, or generated Prisma client model. The required DATABASE-003 integration is therefore absent despite the dependency gate, and the task stop condition prohibits implementing a local schema or changing another repository.

No implementation source or test files were changed. The implementation branch remains at `597b6f238fe7741ab4e6b3377119400b52569b76`; no implementation commit was created or pushed. Required application validation was not run because the task is blocked before a safe source edit. The environment also lacks `rg`; the required scans could not be executed with that command.

Required follow-up: integrate the DATABASE-003 schema/client into the implementation worktree, then retry this same task branch and attempt without creating a competing local contract. Architect review is required to resolve the dependency mismatch.
