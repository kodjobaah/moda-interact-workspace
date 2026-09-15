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
status: ready
priority: 52
executor:
claimed_at:
attempt: 2
depends_on:
- ARCH-014-DATABASE-003
enables:
- ARCH-014-SYSTEM-TEST-002
created: 2026-09-15
updated: 2026-09-16
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

Status: Ready for Review.

Implementation completed in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-SHOPIFY-003` and pushed to `task/ARCH-014-SHOPIFY-003` at commit `596ac5d`. The integrated DATABASE-003 submodule is `d44b621cdcc3635127b91601be648b61c0eff1e2` and contains the `PromotionCampaignTranslation` model, relation, migration, and generated-client schema required by this task.

Implemented:

- Resolved `promotionLocale` from `merchantUiContext(settings, session)` through `createMerchantI18n(merchantUi).catalogueLocale` and passed it explicitly to both promotion readers.
- Updated eligible offers to select exact-locale `merchantTitle` and `merchantDescription`, omit campaigns without exactly one requested translation, and stop exposing internal campaign names or legacy scalar descriptions.
- Updated history to project exact-locale `campaignTitle: string | null`; the route uses `promotions.history.titleUnavailable` when the exact row is missing.
- Added localized `promotions.history.titleUnavailable` to all 20 merchant catalogues, including distinct `pt-BR`/`pt-PT` and `zh-Hans`/`zh-Hant` entries.
- Preserved promotion eligibility, billing-plan targeting, route access, selection transaction/concurrency, grant and reservation accounting, lifecycle status projection, and read-route no-write behavior.
- Added focused exact-locale, leakage, fail-closed offer, nullable history, and route-locale tests while retaining the existing selection and accounting coverage.

Changed files: `app/services/promotions/promotion.service.ts`, `app/routes/app/promotions/route.tsx`, `tests/unit/services/promotion.service.test.ts`, `tests/unit/routes/promotion-route.test.ts`, and the 20 files under `app/i18n/locales/`.

Validation:

- Focused promotion tests: passed, 41 tests.
- Full `npm test`: passed, 593 tests passed and 3 skipped across 49 files.
- `npm run build`: passed.
- `git diff --check`: passed.
- Required leakage scan: passed for production code; only negative assertions in the route test mention forbidden legacy field strings.
- Required `titleUnavailable` scan: passed; all 20 catalogues contain the key.
- `npm run typecheck`: repository command reports existing baseline diagnostics across unrelated JSX/routes and billing tests; after the local fix, no diagnostics reference changed promotion files.
- `npm run lint`: repository command reports existing baseline errors in unrelated dashboard, billing, privacy, webhook, and telemetry files; no changed promotion file is reported.

No architectural concerns or unresolved implementation dependencies remain. Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-SHOPIFY-003`. Implementation HEAD: `596ac5d`.
