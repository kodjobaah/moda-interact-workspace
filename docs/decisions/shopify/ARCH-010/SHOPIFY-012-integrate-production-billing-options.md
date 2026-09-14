---
id: ARCH-010-SHOPIFY-012
architecture_id: ARCH-010
title: Integrate real billing options route and purchase hub
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 55
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-010-SHOPIFY-009
- ARCH-010-SHOPIFY-013
- ARCH-010-SHOPIFY-018
- ARCH-010-SHOPIFY-014
- ARCH-010-SHOPIFY-015
- ARCH-010-SHOPIFY-007
- ARCH-008-SHOPIFY-001
enables:
- ARCH-010-SHOPIFY-008
- ARCH-010-SHOPIFY-016
- ARCH-010-SHOPIFY-026
- ARCH-010-SHOPIFY-020
- ARCH-010-SYSTEM-TEST-001
created: 2026-09-11
updated: 2026-09-14
---

# ARCH-010-SHOPIFY-012: Integrate real billing options route and purchase hub

## Objective

Convert the existing `/app/billing/options` route and `BillingPurchaseHub` from the ARCH-008 mock prototype into a real merchant capacity-management surface by composing **two deliberately different read models**:

1. Shopify-authoritative commercial subscription state from SHOPIFY-013;
2. Moda-authoritative operational recovery-capacity state from SHOPIFY-009.

This task owns integration, not child-component redesign.

## Authority matrix — hard invariant

```text
Question                                         Authority
------------------------------------------------ -------------------------------
Does the Shopify contract exist?                Shopify activeSubscription
What is the current/pending Shopify plan?       Shopify activeSubscription
What price/currency/billing interval applies?   Shopify activeSubscription
What Shopify billing cycle is current?          Shopify activeSubscription
Does Moda know how to entitle that handle?      PostgreSQL BillingPlan mapping
How many Moda included credits remain?          PostgreSQL entitlement counters
How many purchased credits remain?              PostgreSQL entitlement counters
How many lifetime Free credits remain?           PostgreSQL entitlement counters (available under Free or Paid)
May another recovery start?                     SHOPIFY-009 local capacity projection
```

A local `BillingPlan` row is **not** proof that a Shopify plan exists.

## Inspect before editing

```text
app/routes/app/billing/options/route.tsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/BillingPurchaseHub.css
app/components/dashboard/billing-purchase.mock.js
app/routes/app/billing/route.tsx
app/routes/app/billing/select/route.jsx
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/routes.ts
tests/unit/billing-ui.test.ts
```

Read implemented SHOPIFY-009/014/015/013/007 first.

## Current defects to remove

The inspected route currently:

- constructs hard-coded plan and top-up arrays;
- returns one `billing` object from the loader but ignores it in the component;
- passes `mockBillingState` instead;
- uses console-only top-up and plan-change handlers.

`BillingPurchaseHub` currently:

- imports mock plans/offers/state directly;
- has mock default props;
- silently falls back to `plans[0]` when `currentPlanId` is unknown;
- wraps its content in another `<s-page>` even though the route already renders an `<s-page>`;
- assumes child component contracts that no longer match production billing.

## Loader — required algorithm

Authenticate and resolve the shop using existing policies.

Then perform exactly these conceptual reads:

```text
A. SHOPIFY-013 getMerchantShopifySubscriptionState(shop.id)
   -> live Shopify current/pending commercial subscription truth

B. SHOPIFY-009 getMerchantRecoveryCapacityState(shop.id)
   -> local recovery-capacity/credit accounting projection

C. SHOPIFY-007 local billing-cycle UI phase
   -> ACTIVE / DRAINING / RECONCILING presentation/guards
```

The loader is allowed and expected to call Shopify Partner API because this is a dedicated billing-management surface.

Do not add another direct GraphQL/fetch call in the route. Use the billing service/provider abstraction from SHOPIFY-013.

## Provider verification failure — deterministic UI behaviour

If SHOPIFY-013 cannot verify Shopify because of timeout, throttling, HTTP/API error or malformed provider response:

- do not substitute `Subscription.plan`/`BillingPlan` as live Shopify commercial truth;
- do not show a local plan as though Shopify confirmed it;
- render a localized **billing verification unavailable** state;
- keep non-mutating navigation/support available;
- disable top-up purchase and other billing mutations on this screen;
- offer retry by normal page reload/navigation;
- do not change durable subscription/entitlement state from this loader failure.

## `activeSubscription = null`

Render an explicit **no active Shopify subscription** state.

Do not present a local `BillingPlan` mapping as the merchant's active plan.

Plan-management CTA goes to:

```text
/app/billing/select
```

## Active Shopify plan mapped by Moda

When SHOPIFY-013 returns `mappingStatus = MAPPED`:

- Shopify plan handle/price/currency/billing interval/cycle/pending update are the commercial facts;
- local `BillingPlan` mapping supplies Moda name/kind/features/allowance/pack configuration;
- SHOPIFY-009 supplies current spendable recovery capacity;
- render both without conflating them.

## Active Shopify plan not mapped by Moda

When SHOPIFY-013 returns `mappingStatus = UNMAPPED`:

- render the Shopify plan handle/price/cycle faithfully;
- show localized **Moda configuration unavailable for this Shopify plan**;
- do not classify the Shopify contract as absent;
- do not fabricate included credits/features/top-up eligibility;
- disable top-up purchase;
- keep plan-management and support navigation available.

## Top-up action and lifecycle

Use SHOPIFY-014 as the server-side top-up lifecycle adapter. The route action ultimately reuses the existing:

```text
billingService.requestRecoveryCreditPack(...)
```

Business validation remains in the service. Do not duplicate provider/cycle/meter verification in JSX.

The action remains provider-authoritative for the exact purchase attempt and may make its own current Shopify verification because mutations must not trust loader-time state.

Preserve existing idempotency and SHOPIFY-007 drain/reconciliation guards.

Return the SHOPIFY-014 typed merchant-safe result so the route can show `PENDING_BILLING`, `ACTIVE` and `NEEDS_ATTENTION` correctly. Never claim credits are active immediately after App Event HTTP 202 acceptance. The options route does not call App Events directly.

## Loader purchase eligibility vs mutation verification

The loader may display the current local pack configuration and provider-backed Shopify contract state, but the mutation service remains final authority for whether a purchase is accepted at submission time.

Do not duplicate mutation rules in browser code.

## BillingPurchaseHub integration

Remove every import/default dependency on `billing-purchase.mock.js`.

Require explicit production props representing:

- Shopify commercial subscription state from SHOPIFY-013;
- local Moda mapping status;
- SHOPIFY-009 capacity summary;
- current billing-cycle UI phase;
- local pack configuration;
- a fresh idempotent `purchaseId` when a purchase may be attempted;
- typed action result/pending purchase state.

Compose:

- real capacity summary;
- SHOPIFY-014 `TopUpPurchasePanel`;
- SHOPIFY-015 `SubscriptionChangePanel`.

Preserve the top-up/plan tab/switch behaviour if useful, but its data/actions must be real.

Avoid nested duplicate `<s-page>` wrappers; exactly one page-level wrapper owns the screen heading.

## Plan-change action

The plan tab/CTA MUST use the SHOPIFY-015 flow:

```text
/app/billing/select
  -> Shopify-hosted pricing
  -> callback/welcome return with plan_handle
  -> Partner activeSubscription verification
  -> current/pending classification
  -> Background reconciliation for effective transition
```

Do not submit a local target plan, do not call `appSubscriptionCreate`, and do not change included-credit counters in the HTTP route.

When Shopify returns a pending update, render current and pending plans separately with effective date; current recovery entitlement remains current until BACKGROUND-010 confirms the effective transition.

## No local Shopify plan catalogue

Do not populate plan-management UI with `BillingPlan.findMany()` and label those rows as Shopify plans.

`/app/billing/select` remains the plan discovery/selection surface hosted by Shopify.

This task only displays the merchant's **current and pending** live contract returned by `activeSubscription`.

## Mock removal

After integration:

- production code must not import `billing-purchase.mock.js`;
- hard-coded `starter`, `84`, `18`, `£5/£10/£20`, mock plan prices and console actions are removed;
- if the mock file is unused outside obsolete tests, delete it and move necessary fixtures into tests.

## Free top-up composition

For a Shopify-authoritative current Free subscription, compose the page exactly like Paid for top-up lifecycle purposes:

- current plan/price/cycle and pack usage item come from SHOPIFY-013;
- lifetime Free recovery capacity comes from SHOPIFY-009/local counters and is shop-lifetime, not Free-plan-owned;
- purchased credits are displayed/consumed ahead of lifetime Free credits;
- purchase eligibility/lifecycle comes from SHOPIFY-014;
- the Buy CTA is available only when SHOPIFY-014 says the exact Free pack meter and exact current provider/local BillingPeriod are verified and the phase is ACTIVE.

Do not hide the top-up panel merely because `modaMapping.kind = FREE`. Do not display a monthly Free recovery allowance.

## Required tests

At minimum prove:

1. loader calls SHOPIFY-013 authoritative commercial read;
2. loader calls SHOPIFY-009 local capacity read;
3. loader performs no direct Partner fetch outside the service abstraction;
4. Shopify active plan handle/price/currency/billing interval are rendered from provider state;
5. Shopify pending update is rendered from provider state;
6. a local `BillingPlan` existing without a Shopify active contract is not displayed as the current commercial plan;
7. active Shopify plan + matching Moda mapping renders combined commercial + entitlement state;
8. active Shopify plan + no Moda mapping renders `UNMAPPED` configuration state while preserving Shopify plan facts;
9. Partner verification failure does not fall back to local commercial truth and disables billing mutations;
10. `activeSubscription = null` renders no-active-subscription state;
11. route no longer uses `mockBillingState`;
12. no production mock imports remain;
13. current plan is never replaced by `plans[0]` fallback;
14. real Free capacity renders from SHOPIFY-009;
15. real Paid current-period capacity renders from SHOPIFY-009;
16. purchased balance renders separately;
17. top-up action delegates through SHOPIFY-014 to the existing billing service exactly once per submitted request;
18. PENDING_BILLING, ACTIVE and NEEDS_ATTENTION purchase states render correctly;
19. App Event 202/pending state is never rendered as activated credits;
20. DRAINING/RECONCILING prevents a new purchase through existing service contract;
21. plan management points to `/app/billing/select`;
22. returned pending plan is displayed separately while current entitlement remains current;
23. no local target-plan mutation or Billing API subscription creation exists;
24. no local monetary price is fabricated;
25. no local Shopify plan catalogue is fabricated;
26. no console-only billing actions remain;
27. screen contains only one page-level wrapper;
28. no merchant link targets Admin;
29. production build/typecheck has no task-introduced diagnostics.

## Additional required Free tests

Prove that an eligible Free subscription renders the real top-up action; an ineligible/missing-cycle/missing-meter Free subscription renders a truthful unavailable reason; and no Free screen invents a monthly Free allowance.

## Non-goals

Do not implement Background purchase confirmation, effective plan-transition logic, refunds, cancellation, promotional credits, Admin UI or an API to enumerate every Shopify plan. Those lifecycle behaviours are owned by existing Background reconciliation and BACKGROUND-010.

## Validation

Run focused billing route/component/service tests, then declared full tests, typecheck, build and `git diff --check`.

## Stop conditions

STOP if SHOPIFY-009/010/011/013 integrated contracts differ materially from the task assumptions.

STOP if the route can only present a current commercial plan by treating local `BillingPlan` as Shopify truth.

STOP if `requestRecoveryCreditPack` cannot be reused without changing its accepted billing semantics.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `app/components/dashboard/BillingPurchaseHub.jsx`
- `app/components/dashboard/SubscriptionChangePanel.jsx`
- `app/i18n/locales/cs.json` through `app/i18n/locales/zh-Hant.json` (two Attempt-2 catalogue keys in all 20 merchant locales)
- `tests/unit/billing-purchase-hub.test.tsx`
- `tests/unit/subscription-change-panel.test.tsx`

### Work Completed
- Preserved the accepted Attempt-1 production mechanics and implemented every Attempt-2 correction: Paid-included and lifetime-Free balances now render as separate ICU-formatted items, with promotional and purchased balances remaining separate.
- Mapped provider verification failure to its dedicated merchant copy and unavailable current-plan value, while preserving mapping-specific copy for verified `UNMAPPED` contracts.
- Added the exact provider-verification and configured-but-ineligible top-up messages to all 20 merchant catalogues; the Free top-up explanation is shown only for the required ACTIVE/missing-cycle conditions and remains suppressed for pending, FROZEN, DRAINING and RECONCILING states.
- Capacity `null` now renders one bounded unavailable summary without fabricated zero balances. Added the required direct-render regression coverage; no route, service, provider, shared, database or lifecycle contract files were changed.

### Validation Results
- Focused billing tests: `npm test -- --run tests/unit/billing-purchase-hub.test.tsx tests/unit/subscription-change-panel.test.tsx tests/unit/billing-ui.test.ts` -> 3 files passed, 25 tests passed.
- Full tests: `npm test` -> 40 files passed, 2 skipped; 494 tests passed, 3 skipped.
- Typecheck: `npm run typecheck` retains the documented unrelated JSX baseline diagnostics in dashboard/home/merchant-support/pending-recoveries/usage files; no diagnostics referenced Attempt-2 touched files.
- Production build: `npm run build` passed; only existing bundler/chunk-size warnings were emitted.
- Whitespace: `git diff --check` passed.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-012`
- Implementation branch: `task/ARCH-010-SHOPIFY-012`
- Implementation commits: `ee310ac` (`feat(shopify): integrate production billing options`) and `012b88e` (`fix(shopify): correct billing capacity presentation`), both pushed to `origin/task/ARCH-010-SHOPIFY-012`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-012`
- Launcher VCS evidence: prepared Attempt 2 reused the canonical parent/implementation worktrees, passed all seven dependencies, initialized submodules, and durably claimed executor `copilot` before implementation.
- Parent branch/report commit and push: this Attempt-2 report update is committed and published on `task/ARCH-010-SHOPIFY-012`.

### Architect Review
Pending.


## Final lifecycle composition

Compose SHOPIFY-018 lifecycle state with SHOPIFY-013 commercial state. A provider FROZEN result is neither `NO_ACTIVE_SUBSCRIPTION` nor ordinary verification failure. Render frozen billing-management state and keep mutations disabled until durable Background reconciliation restores an executable subscription.


## Final promotional balance composition

When SHOPIFY-009 exposes promotional capacity, compose it into the production billing-options read model as a separate Moda-owned balance. Do not treat it as Shopify commercial truth, price it, make it purchasable/refundable, or expose internal grant provenance. SHOPIFY-020 owns the detailed merchant-facing wording/components.


## Architect Review — Attempt 1

### Decision

**Changes Requested.**

This review is intentionally focused on **functional correctness and architectural authority**, not on obtaining 100% test coverage. The production composition is substantially correct and the accepted SHOPIFY-009/013/014/015 service semantics MUST be preserved. Attempt 2 is a narrow presentation/integration correction only.

### Accepted in Attempt 1 — do not rework

Preserve all of the following exactly unless one of the bounded corrections below cannot compile without a direct adjustment:

- `/app/billing/options` authenticates/resolves the merchant shop and calls only `billingService` abstractions; it performs no direct Partner GraphQL/fetch;
- SHOPIFY-013 remains the Shopify-authoritative current/pending commercial contract read;
- SHOPIFY-009 remains the Moda-authoritative capacity projection;
- SHOPIFY-014 remains the sole top-up mutation adapter used by the route action;
- SHOPIFY-015 remains the hosted plan-management component/flow and `/app/billing/select` remains the only plan-management destination;
- no production `billing-purchase.mock.js` import/default/fallback remains;
- no local Shopify plan catalogue, local target-plan mutation, `appSubscriptionCreate`, direct App Event publication or console-only billing mutation is reintroduced;
- exactly one page-level `<s-page>` remains;
- current/pending provider facts remain distinct and no local `BillingPlan` row becomes proof of a Shopify contract;
- the accepted SHOPIFY-014 REQUESTED/idempotency/provider-evidence semantics are not changed.

### Finding 1 — Paid summary hides lifetime-Free capacity and misuses ICU copy

`BillingPurchaseHub.jsx` currently collapses:

```text
paidIncluded ?? freeLifetime ?? 0
```

into one summary slot. On Paid, when both balances exist, the Paid included balance wins and the lifetime-Free balance disappears. That violates the authority matrix and the task Completion Report, both of which require Paid-included, lifetime-Free, promotional and purchased capacity to remain separate Moda-owned balances.

The same summary also calls:

```text
i18n.t("billing.paidIncludedAllowance")
i18n.t("billing.lifetimeFreeAllowance")
```

without the required ICU variables. Those catalogue messages require `{remaining}` and `{allowance}`.

#### Required correction

In `app/components/dashboard/BillingPurchaseHub.jsx`:

1. Treat `capacity == null` separately; do not derive numeric balances from it.
2. When `capacity.paidIncluded != null`, render a dedicated Paid-included summary item using:

```text
i18n.t("billing.paidIncludedAllowance", {
  remaining: capacity.paidIncluded.remaining,
  allowance: capacity.paidIncluded.granted,
})
```

3. When `capacity.freeLifetime != null`, render a **separate** lifetime-Free item even when Paid-included is also present, using:

```text
i18n.t("billing.lifetimeFreeAllowance", {
  remaining: capacity.freeLifetime.remaining,
  allowance: capacity.freeLifetime.granted,
})
```

4. Continue rendering promotional and purchased balances separately.
5. On Free, do not invent/display a monthly included allowance. `paidIncluded == null`; lifetime-Free remains the Free entitlement balance.
6. Do not merge lifetime-Free into Paid-included and do not hide it merely because `reconciledPlanMapping.kind = PAID_METERED`.

The existing two-column CSS grid already supports four capacity cards. Do not redesign the page styling for this correction.

### Finding 2 — provider verification failure is presented as mapping/configuration failure

SHOPIFY-012 explicitly requires Partner/API verification failure to be a distinct merchant state. It MUST NOT be described as though a local Moda plan mapping failed.

The current integration does both of the following:

- the page hero falls back to the ordinary billing-page description when `verificationState === "VERIFICATION_UNAVAILABLE"`;
- `SubscriptionChangePanel` renders `billing.configurationUnavailableDescription`, whose meaning is a mapping/configuration failure (`Your subscription could not be safely mapped...`).

That conflates two different authorities:

```text
Shopify could not be verified       !=      Shopify was verified but Moda mapping is unavailable
```

#### Required correction

Add this canonical key to all 20 merchant catalogues:

```text
billing.verificationUnavailableDescription
```

Then:

1. `BillingPurchaseHub.jsx` MUST use this description when `verificationState === "VERIFICATION_UNAVAILABLE"`.
2. For the summary's current-plan value in that state, use `i18n.t("common.unavailable")`; do not use `billing.configurationUnavailable` as though an unmapped Shopify plan were proven.
3. `SubscriptionChangePanel.jsx` MUST use `billing.verificationUnavailableDescription` for `VERIFICATION_UNAVAILABLE` only.
4. Preserve the existing mapping-specific `billing.configurationUnavailable` / `billing.configurationUnavailableDescription` behavior for genuinely verified-but-`UNMAPPED` state.
5. Billing mutations remain unavailable when commercial verification is unavailable. Normal page reload/navigation remains the retry mechanism.

### Finding 3 — configured but unverifiable Free top-up silently loses the Buy CTA

The task requires an eligible Free subscription to show the real top-up action and an ineligible/missing-cycle/missing-meter Free subscription to show a truthful unavailable reason.

Today, when the pack is configured but `purchaseEligible=false`, the production top-up view can simply omit the Buy button with no explanation. This is especially misleading for the required Free cases where the current cycle or exact pack meter cannot be verified.

#### Required correction

Add this canonical key to all 20 merchant catalogues:

```text
billingCommerce.topup.verificationUnavailable
```

In `BillingPurchaseHub.jsx`, show that message adjacent to the top-up panel only when all of the following are true:

```text
topUpState.configured === true
AND topUpState.purchaseEligible === false
AND topUpState.latestPurchase?.status !== "REQUESTED"
AND verificationState === "ACTIVE_SUBSCRIPTION"
AND lifecycleState === "ACTIVE"
AND billingPeriodPhase !== "DRAINING"
AND billingPeriodPhase !== "RECONCILING"
```

This condition intentionally includes `billingPeriodPhase == null`, because a missing/unverified local cycle is one of the required fail-closed cases.

Do NOT show this generic top-up verification message when:

- commercial verification itself is unavailable — the page-level verification message owns that state;
- lifecycle is FROZEN — SHOPIFY-016 owns the detailed FROZEN restriction presentation;
- phase is DRAINING/RECONCILING — the existing phase copy owns that state;
- a REQUESTED purchase exists — SHOPIFY-014's pending/retry/attention copy owns that state;
- the pack is not configured — `TopUpPurchasePanel`'s existing no-offer/configured behavior remains authoritative.

Do not expose the English `billingService.getMerchantBillingState().unavailableReason` string directly to merchants. Merchant copy must remain catalogue-backed.

### Finding 4 — unavailable SHOPIFY-009 capacity is fabricated as zero

The loader deliberately uses `Promise.allSettled`. Therefore `capacity` can legitimately be `null` while the commercial read succeeds.

`BillingPurchaseHub.jsx` currently converts unknown capacity to:

```text
Paid/Free = 0
Promotional = 0
Purchased = 0
```

through optional chaining plus `?? 0`. Those are fabricated values, not SHOPIFY-009 authority.

#### Required correction

When `capacity == null`:

- do not render any numeric recovery-capacity balance as `0`;
- render one bounded summary-unavailable state using the existing localized `common.unavailable` copy;
- keep verified Shopify commercial current/pending facts visible;
- do not manufacture Paid, lifetime-Free, promotional or purchased quantities;
- do not change durable state.

When `capacity != null`, render the actual four independent Moda balances as described in Finding 1.

### Exact catalogue strings

Use these strings exactly. Do not ask the implementation model to invent translations.

| Locale | `billing.verificationUnavailableDescription` | `billingCommerce.topup.verificationUnavailable` |
| --- | --- | --- |
| `cs` | Nepodařilo se ověřit aktuální fakturační údaje Shopify. Změny fakturace jsou na této obrazovce vypnuté. Obnovte stránku a zkuste to znovu. | Nákup doplňkových kreditů není dostupný, dokud nebude ověřen aktuální fakturační cyklus a měřič kreditů pro obnovu. |
| `da` | Vi kunne ikke bekræfte dine aktuelle Shopify-faktureringsoplysninger. Faktureringsændringer er deaktiveret på denne side. Genindlæs siden for at prøve igen. | Køb af ekstra kreditter er ikke tilgængeligt, før den aktuelle faktureringscyklus og måleren for genoprettelseskreditter er bekræftet. |
| `de` | Wir konnten deine aktuellen Shopify-Abrechnungsdaten nicht bestätigen. Abrechnungsänderungen sind auf dieser Seite deaktiviert. Lade die Seite neu, um es erneut zu versuchen. | Der Kauf zusätzlicher Guthaben ist nicht verfügbar, bis der aktuelle Abrechnungszyklus und der Zähler für Wiederherstellungsguthaben bestätigt wurden. |
| `en` | We couldn't verify your current Shopify billing details. Billing changes are disabled on this screen. Reload the page to try again. | Top-up purchase is unavailable until the current billing cycle and recovery-credit meter are verified. |
| `es` | No pudimos verificar los datos de facturación actuales de Shopify. Los cambios de facturación están deshabilitados en esta pantalla. Recarga la página para volver a intentarlo. | La compra de créditos adicionales no está disponible hasta que se verifiquen el ciclo de facturación actual y el medidor de créditos de recuperación. |
| `fi` | Emme voineet vahvistaa nykyisiä Shopify-laskutustietojasi. Laskutusmuutokset on poistettu käytöstä tällä näytöllä. Lataa sivu uudelleen ja yritä uudelleen. | Lisäkrediittien ostaminen ei ole käytettävissä, ennen kuin nykyinen laskutusjakso ja palautuskrediittien mittari on vahvistettu. |
| `fr` | Nous n’avons pas pu vérifier vos informations de facturation Shopify actuelles. Les modifications de facturation sont désactivées sur cet écran. Rechargez la page pour réessayer. | L’achat de crédits supplémentaires n’est pas disponible tant que le cycle de facturation actuel et le compteur de crédits de récupération ne sont pas vérifiés. |
| `it` | Non è stato possibile verificare i dati di fatturazione Shopify correnti. Le modifiche alla fatturazione sono disabilitate in questa schermata. Ricarica la pagina per riprovare. | L’acquisto di crediti aggiuntivi non è disponibile finché non vengono verificati il ciclo di fatturazione corrente e il contatore dei crediti di recupero. |
| `ja` | 現在の Shopify 請求情報を確認できませんでした。この画面では請求に関する変更が無効になっています。ページを再読み込みして、もう一度お試しください。 | 現在の請求サイクルとリカバリークレジットメーターが確認されるまで、追加クレジットを購入できません。 |
| `ko` | 현재 Shopify 결제 정보를 확인할 수 없습니다. 이 화면에서는 결제 변경이 비활성화되어 있습니다. 페이지를 새로고침한 후 다시 시도하세요. | 현재 결제 주기와 복구 크레딧 미터가 확인될 때까지 추가 크레딧을 구매할 수 없습니다. |
| `nb` | Vi kunne ikke bekrefte de gjeldende Shopify-faktureringsopplysningene dine. Faktureringsendringer er deaktivert på denne siden. Last inn siden på nytt for å prøve igjen. | Kjøp av ekstra kreditter er ikke tilgjengelig før gjeldende faktureringssyklus og måleren for gjenopprettingskreditter er bekreftet. |
| `nl` | We konden je huidige Shopify-factureringsgegevens niet verifiëren. Factureringswijzigingen zijn op dit scherm uitgeschakeld. Laad de pagina opnieuw om het opnieuw te proberen. | Extra credits kopen is niet beschikbaar totdat de huidige factureringscyclus en de meter voor herstelcredits zijn geverifieerd. |
| `pl` | Nie udało się zweryfikować bieżących danych rozliczeniowych Shopify. Zmiany rozliczeń są wyłączone na tym ekranie. Odśwież stronę, aby spróbować ponownie. | Zakup dodatkowych kredytów jest niedostępny, dopóki bieżący cykl rozliczeniowy i licznik kredytów odzyskiwania nie zostaną zweryfikowane. |
| `pt-BR` | Não foi possível verificar seus dados atuais de cobrança da Shopify. As alterações de cobrança estão desativadas nesta tela. Recarregue a página para tentar novamente. | A compra de créditos adicionais não está disponível até que o ciclo de cobrança atual e o medidor de créditos de recuperação sejam verificados. |
| `pt-PT` | Não foi possível verificar os seus dados atuais de faturação da Shopify. As alterações de faturação estão desativadas neste ecrã. Recarregue a página para tentar novamente. | A compra de créditos adicionais não está disponível até que o ciclo de faturação atual e o medidor de créditos de recuperação sejam verificados. |
| `sv` | Vi kunde inte verifiera dina aktuella Shopify-faktureringsuppgifter. Faktureringsändringar är inaktiverade på den här sidan. Ladda om sidan och försök igen. | Köp av extra krediter är inte tillgängligt förrän den aktuella faktureringscykeln och mätaren för återställningskrediter har verifierats. |
| `th` | เราไม่สามารถยืนยันข้อมูลการเรียกเก็บเงิน Shopify ปัจจุบันของคุณได้ การเปลี่ยนแปลงการเรียกเก็บเงินถูกปิดใช้งานบนหน้าจอนี้ โปรดโหลดหน้าใหม่แล้วลองอีกครั้ง | ยังไม่สามารถซื้อเครดิตเพิ่มเติมได้จนกว่าจะยืนยันรอบการเรียกเก็บเงินปัจจุบันและมิเตอร์เครดิตการกู้คืนแล้ว |
| `tr` | Mevcut Shopify faturalandırma bilgilerinizi doğrulayamadık. Bu ekranda faturalandırma değişiklikleri devre dışı bırakıldı. Yeniden denemek için sayfayı yenileyin. | Mevcut faturalandırma dönemi ve kurtarma kredisi sayacı doğrulanana kadar ek kredi satın alınamaz. |
| `zh-Hans` | 我们无法验证您当前的 Shopify 账单信息。此页面已禁用账单更改。请重新加载页面后重试。 | 在当前账单周期和恢复额度计量项验证完成之前，无法购买额外额度。 |
| `zh-Hant` | 我們無法驗證您目前的 Shopify 帳單資訊。此頁面已停用帳單變更。請重新載入頁面後再試一次。 | 在目前的帳單週期和恢復額度計量項驗證完成之前，無法購買額外額度。 |

### Attempt 2 allowed files

Production changes are limited to:

```text
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/SubscriptionChangePanel.jsx
app/i18n/locales/cs.json
app/i18n/locales/da.json
app/i18n/locales/de.json
app/i18n/locales/en.json
app/i18n/locales/es.json
app/i18n/locales/fi.json
app/i18n/locales/fr.json
app/i18n/locales/it.json
app/i18n/locales/ja.json
app/i18n/locales/ko.json
app/i18n/locales/nb.json
app/i18n/locales/nl.json
app/i18n/locales/pl.json
app/i18n/locales/pt-BR.json
app/i18n/locales/pt-PT.json
app/i18n/locales/sv.json
app/i18n/locales/th.json
app/i18n/locales/tr.json
app/i18n/locales/zh-Hans.json
app/i18n/locales/zh-Hant.json
```

Test changes are limited to:

```text
tests/unit/billing-purchase-hub.test.tsx   # create this direct render test
tests/unit/subscription-change-panel.test.tsx
tests/unit/billing-ui.test.ts              # only if a source-contract assertion needs updating
```

### Forbidden scope in Attempt 2

Do NOT change:

```text
app/routes/app/billing/options/route.tsx
app/routes/app/billing/route.tsx
app/routes/app/billing/select/route.jsx
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/providers/**
app/components/dashboard/TopUpPurchasePanel.jsx
database/**
shared/**
background/**
admin/**
```

Do not implement SHOPIFY-016's complete FROZEN/cancellation direct-action guard matrix or SHOPIFY-020's selected-promotion detail UI in this correction. Those tasks remain separate downstream owners.

### Mandatory focused functional regressions

Create `tests/unit/billing-purchase-hub.test.tsx` using the existing `renderToStaticMarkup` pattern from `subscription-change-panel.test.tsx` and prove these exact behaviors:

1. `renders Paid included and lifetime Free as separate balances`
   - Paid included fixture: `granted=30`, `remaining=21`;
   - lifetime Free fixture: `granted=10`, `remaining=7`;
   - markup contains the fully formatted localized Paid message `Included recoveries this period: 21 of 30 remaining`;
   - markup separately contains `Lifetime Free recoveries: 7 of 10 remaining`.

2. `renders Shopify verification failure distinctly from an unmapped plan`
   - `verificationState="VERIFICATION_UNAVAILABLE"`, `current=null`;
   - markup contains the new verification-unavailable description;
   - markup does NOT contain `Your subscription could not be safely mapped`.

3. `explains a configured but unverifiable Free top-up`
   - `topUpState.configured=true`, `purchaseEligible=false`, no REQUESTED purchase;
   - `verificationState="ACTIVE_SUBSCRIPTION"`, `lifecycleState="ACTIVE"`, `billingPeriodPhase=null`;
   - markup contains `Top-up purchase is unavailable until the current billing cycle and recovery-credit meter are verified.`;
   - markup contains no enabled Buy button.

4. `does not fabricate zero balances when capacity is unavailable`
   - `capacity=null`;
   - markup contains localized `Unavailable` for the capacity summary;
   - markup does not render Paid/lifetime/promotional/purchased balance labels with numeric zero values.

Update `tests/unit/subscription-change-panel.test.tsx` so the `VERIFICATION_UNAVAILABLE` assertion expects the new provider-verification copy rather than the mapping-failure copy.

Do not add broad combinatorial coverage merely to increase test count.

### Attempt 2 validation

Run:

```text
npm test -- --run \
  tests/unit/billing-purchase-hub.test.tsx \
  tests/unit/subscription-change-panel.test.tsx \
  tests/unit/billing-ui.test.ts

npm run typecheck
npm run build
git diff --check
```

`npm run typecheck` may retain only the previously documented unrelated JSX baseline diagnostics. There must be no new diagnostic in an Attempt 2 touched file.

### Stop conditions

STOP and return to `moda_architect` without widening scope if any correction requires:

- changing SHOPIFY-009 capacity semantics;
- changing SHOPIFY-013 provider/commercial contracts;
- changing SHOPIFY-014 purchase lifecycle/idempotency/provider-evidence semantics;
- changing SHOPIFY-015 hosted plan-change persistence/callback semantics;
- adding a direct Partner API call to the route/component;
- changing Prisma/shared/background contracts;
- implementing SHOPIFY-016 or SHOPIFY-020 instead of this bounded integration correction.

### Workflow state after this review

Authoritative task state after applying this architect review:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next `/moda-task ARCH-010-SHOPIFY-012` claim MUST increment to Attempt 2 exactly once.

Do not start `ARCH-010-SHOPIFY-008`, `ARCH-010-SHOPIFY-016`, `ARCH-010-SHOPIFY-026`, `ARCH-010-SHOPIFY-020` or `ARCH-010-SYSTEM-TEST-001` from this review.



## Architect Review — Attempt 2 (Revised after flow clarification)

### Decision

**Changes Requested — narrow integration correction.** This revised review supersedes the earlier provisional Attempt-2 review that treated `UNMAPPED` as though it were the normal post-Shopify-return waiting state. **Do not apply the earlier `ARCH-010-SHOPIFY-012-attempt2-changes-requested.patch` (SHA-256 `2ca6716d1aea775169405fc3cd89b7ae46fa67cca63280160e603b562f31df35`).**

This decision remains focused on functionality, not exhaustive test coverage.

### Correct state model — do not conflate these states

The production flow has three distinct concepts:

```text
A. Confirmed current Shopify commercial plan
   Authority: Partner activeSubscription.current plan

B. Provider-confirmed pending Shopify update
   Authority: Partner activeSubscription.pendingUpdate

C. Merchant-selected target returned by Shopify pricing,
   but Partner activeSubscription does not yet report that handle
   as current or pending
   Authority: callback plan_handle as SELECTION CONTEXT ONLY
```

`UNMAPPED` is **not C**.

The canonical SHOPIFY-013 meaning of:

```text
mappingStatus = UNMAPPED
```

is:

```text
Partner activeSubscription has confirmed a current Shopify plan handle,
but PostgreSQL has no active BillingPlan mapping for that confirmed handle.
```

Preserve that meaning. Do not rename it and do not use `UNMAPPED` as an "awaiting Shopify confirmation" state.

### Functionality that already exists — preserve, do not duplicate

The following functionality is already present and MUST remain unchanged:

1. `getMerchantShopifySubscriptionState()` returns provider current commercial truth and provider `pendingUpdate` separately.
2. `SubscriptionChangePanel` already renders `current` and provider-confirmed `pending` separately.
3. Provider-confirmed pending commercial state does not replace current recovery entitlement before Background reconciliation.
4. `recordHostedPlanChangeReturn()` treats callback `plan_handle` as selection context only and does not grant entitlement from the URL.
5. `CURRENT`, provider-confirmed `PENDING`, `NO_ACTIVE`, `UNVERIFIED` and `MISMATCH` remain distinct callback outcomes.
6. Attempt-2 presentation corrections remain accepted: four independent capacity balances, provider-verification copy, configured-but-ineligible top-up explanation, and no fabricated zeroes for unavailable capacity.
7. SHOPIFY-009 remains sole local recovery-capacity projection authority. SHOPIFY-012 MUST NOT override or recalculate `canStartRecovery`/`capacitySource` from commercial mapping state.

### Remaining functional gap — returned selection context is discarded before Partner catches up

The current callback has this safe classification rule:

```text
requested plan_handle != provider current handle
AND requested plan_handle != provider pending handle
  -> MISMATCH
```

That rule must remain safe for entitlement. However, the callback currently redirects with only:

```text
/app/billing/options?plan_change=mismatch
```

so the merchant-selected target handle is discarded.

This creates a poor but common eventual-consistency experience:

```text
Current confirmed Shopify plan: Growth
Merchant selects Scale in Shopify managed pricing
Shopify redirects back with plan_handle=scale
Partner activeSubscription still reports Growth and no pendingUpdate yet

Current implementation:
  -> MISMATCH
  -> selected Scale context is lost
  -> billing page shows only Growth

Required presentation:
  -> Growth remains current and authoritative
  -> Scale is shown separately as a NON-AUTHORITATIVE selected target
  -> Scale is visually greyed out
  -> exact copy says "Waiting for confirmation from Shopify."
  -> no Scale price/cycle/features/credits are invented
  -> no entitlement changes occur
```

This is a presentation handoff state only. Call it `requestedSelection` / `AWAITING_SHOPIFY_CONFIRMATION` in route/component code if a name is needed. **Do not add a new Prisma enum, provider enum or durable subscription status.**

### Attempt 3 required implementation

#### 1. Preserve callback selection context without making it entitlement authority

In:

```text
app/routes/app/billing/callback/route.tsx
```

Do not change `recordHostedPlanChangeReturn()` classification or persistence semantics.

For `result.result === "mismatch"`, preserve the requested handle only in the redirect query string:

```text
/app/billing/options?plan_change=mismatch&requested_plan_handle=<URL-encoded requestedPlanHandle>
```

For Partner verification failure, also preserve the same non-authoritative selection context:

```text
/app/billing/options?plan_change=unverified&requested_plan_handle=<URL-encoded requestedPlanHandle>
```

Do not write `requestedPlanHandle` into:

```text
Subscription.planId
Subscription.observedShopifyPlanHandle
Subscription.pendingPlanId
Subscription.pendingShopifyPlanHandle
Subscription.pendingEffectiveAt
BillingPeriod
any entitlement counter
```

Do not enqueue a new transition solely because the URL contains the requested handle. Existing reconciliation ownership remains unchanged.

#### 2. Derive a transient requested selection in the billing-options loader

In:

```text
app/routes/app/billing/options/route.tsx
```

Read:

```text
plan_change
requested_plan_handle
```

from `request.url`.

The query value is display-only selection context. React escaping must remain the only rendering mechanism; never inject it as HTML or a URL destination.

Construct `requestedSelection` only when all of the following are true:

```text
requested_plan_handle is non-empty after trim
requested_plan_handle length <= 128
plan_change is "mismatch" or "unverified"
```

Then suppress the transient requested selection if the fresh SHOPIFY-013 read on the options page has already caught up and proves the same handle as either:

```text
commercial.subscription.planHandle
OR
commercial.subscription.pendingUpdate.planHandle
```

This suppression is mandatory. Once Partner has confirmed the target as current or pending, the existing provider-authoritative `current` / `pending` rendering owns presentation and no duplicate grey card may remain.

Return only:

```ts
requestedSelection: {
  shopifyPlanHandle: string;
} | null
```

Do not attach price, currency, billing interval, effective date, plan allowance, pack size or entitlement to this transient object because Shopify `activeSubscription` has not yet supplied those facts for this target.

#### 3. Show the selected target as greyed-out and explicitly unconfirmed

In:

```text
app/components/dashboard/SubscriptionChangePanel.jsx
```

add an optional display-only prop equivalent to:

```ts
requestedSelection: {
  shopifyPlanHandle: string;
} | null
```

The component MUST render in this order:

```text
confirmed current provider plan        # normal/current presentation
provider-confirmed pending update       # existing pending presentation, if any
requestedSelection                     # only when provider has not confirmed it
```

For `requestedSelection`:

- render the raw Shopify-returned handle as selection context;
- render `billingCommerce.plans.awaitingShopifyConfirmation`;
- use a dedicated class such as `moda-provider-plan-awaiting-confirmation`;
- do not render a price, currency, interval, effective date, included allowance, pack size or credits for it;
- do not call it current;
- do not call it an upgrade/downgrade;
- do not expose any mutation button on the grey card.

When `requestedSelection` exists, the billing-options page SHOULD open the plan view initially so the merchant immediately sees the selected target and waiting state. It is acceptable to pass:

```text
initialView="plans"
```

for this case only. Otherwise preserve the existing default view.

#### 4. Make the grey state visually real

In:

```text
app/components/dashboard/BillingPurchaseHub.css
```

add deterministic styling for:

```text
.moda-provider-plan-awaiting-confirmation
```

Use the existing design tokens. Required visual semantics:

```text
opacity: approximately 0.55 to 0.65
muted/soft background
non-interactive appearance
clearly secondary to the confirmed current plan
```

Do not use a disabled form control to represent the plan; this is informational presentation.

The existing `moda-provider-plan-pending` class is already emitted for Partner-confirmed pending plans. You may give it a subdued style too, but do not make the two semantic states identical in copy:

```text
provider pendingUpdate = Shopify-confirmed pending commercial update
requestedSelection = merchant selection awaiting Partner confirmation
```

#### 5. Keep genuine `UNMAPPED` semantics narrow and truthful

Pass SHOPIFY-013 `mappingStatus` explicitly into `BillingPurchaseHub` if needed for presentation. Do not infer mapping from `mappedModaPlanName` alone.

For a genuine:

```text
verificationState == ACTIVE_SUBSCRIPTION
AND mappingStatus == UNMAPPED
```

preserve:

- exact Shopify current handle/price/currency/interval/cycle;
- all durable local balances exactly as supplied by SHOPIFY-009;
- SHOPIFY-009 availability/capacity semantics without UI recalculation.

Show the existing mapping-specific warning:

```text
billing.configurationUnavailableDescription
```

and keep plan-specific top-up mutation disabled because Moda cannot safely resolve the current Shopify handle to pack configuration.

Do **not** suppress or zero purchased, lifetime-Free, promotional or other SHOPIFY-009 balances merely because the commercial handle is unmapped.

Do not present `billingCommerce.topup.verificationUnavailable` for genuine `UNMAPPED`. That copy is only for an already-MAPPED contract whose exact cycle/meter cannot currently be verified. Its predicate must therefore require:

```text
mappingStatus == MAPPED
```

This is the only part of the earlier provisional `UNMAPPED` review that remains applicable.

### Exact new catalogue key

Add this key to all 20 merchant catalogues exactly as follows:

| Locale | `billingCommerce.plans.awaitingShopifyConfirmation` |
| --- | --- |
| `cs` | Čekáme na potvrzení od Shopify. |
| `da` | Venter på bekræftelse fra Shopify. |
| `de` | Warten auf Bestätigung von Shopify. |
| `en` | Waiting for confirmation from Shopify. |
| `es` | Esperando la confirmación de Shopify. |
| `fi` | Odotetaan vahvistusta Shopifylta. |
| `fr` | En attente de confirmation de Shopify. |
| `it` | In attesa della conferma di Shopify. |
| `ja` | Shopify からの確認を待っています。 |
| `ko` | Shopify 확인을 기다리는 중입니다. |
| `nb` | Venter på bekreftelse fra Shopify. |
| `nl` | Wachten op bevestiging van Shopify. |
| `pl` | Oczekiwanie na potwierdzenie od Shopify. |
| `pt-BR` | Aguardando confirmação da Shopify. |
| `pt-PT` | A aguardar confirmação da Shopify. |
| `sv` | Väntar på bekräftelse från Shopify. |
| `th` | กำลังรอการยืนยันจาก Shopify |
| `tr` | Shopify onayı bekleniyor. |
| `zh-Hans` | 正在等待 Shopify 确认。 |
| `zh-Hant` | 正在等待 Shopify 確認。 |

Do not ask the implementation model to invent translations.

### Attempt 3 allowed production files

```text
app/routes/app/billing/callback/route.tsx
app/routes/app/billing/options/route.tsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/SubscriptionChangePanel.jsx
app/components/dashboard/BillingPurchaseHub.css
app/i18n/locales/cs.json
app/i18n/locales/da.json
app/i18n/locales/de.json
app/i18n/locales/en.json
app/i18n/locales/es.json
app/i18n/locales/fi.json
app/i18n/locales/fr.json
app/i18n/locales/it.json
app/i18n/locales/ja.json
app/i18n/locales/ko.json
app/i18n/locales/nb.json
app/i18n/locales/nl.json
app/i18n/locales/pl.json
app/i18n/locales/pt-BR.json
app/i18n/locales/pt-PT.json
app/i18n/locales/sv.json
app/i18n/locales/th.json
app/i18n/locales/tr.json
app/i18n/locales/zh-Hans.json
app/i18n/locales/zh-Hant.json
```

Tests may change only the directly relevant files:

```text
tests/unit/routes/billing-callback.test.ts
tests/unit/billing-ui.test.ts
tests/unit/billing-purchase-hub.test.tsx
tests/unit/subscription-change-panel.test.tsx
```

### Forbidden scope

Do NOT change:

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/providers/**
database/**
shared/**
background/**
admin/**
```

Do not change SHOPIFY-015's durable callback classification/persistence rules. In particular, callback URL `plan_handle` remains selection context only and MUST NOT become entitlement evidence.

Do not change SHOPIFY-009 capacity semantics or derive recovery admission from the requested selection.

### Mandatory focused functional regressions

Add focused evidence for these exact behaviors:

1. `preserves an unconfirmed managed-pricing selection in the mismatch redirect`
   - callback receives `plan_handle=scale`;
   - Partner still reports another current plan and no matching pending update;
   - `recordHostedPlanChangeReturn()` remains `mismatch`;
   - callback performs no new durable pending-plan write;
   - redirect includes URL-encoded `requested_plan_handle=scale`.

2. `preserves selection context when Partner verification is unavailable`
   - provider verification throws;
   - existing verification-failure scheduling behavior remains unchanged;
   - redirect contains `plan_change=unverified` and the URL-encoded requested handle;
   - no entitlement state is created from the URL.

3. `renders current confirmed plan and unconfirmed selection separately`
   - current provider plan is `growth`;
   - requested selection is `scale`;
   - current `growth` remains normal/current;
   - `scale` renders in the awaiting-confirmation class;
   - markup contains `Waiting for confirmation from Shopify.`;
   - the requested card contains no fabricated price, interval, allowance or credits.

4. `does not duplicate requested selection after Partner confirms it as pending`
   - fresh commercial state contains `pendingUpdate.planHandle=scale`;
   - query still carries `requested_plan_handle=scale`;
   - transient `requestedSelection` is suppressed;
   - existing provider-confirmed pending rendering owns `scale` exactly once.

5. `does not duplicate requested selection after Partner confirms it as current`
   - fresh commercial current handle is `scale`;
   - query still carries `requested_plan_handle=scale`;
   - transient requested card is absent.

6. `keeps genuine unmapped current contract distinct from awaiting confirmation`
   - provider confirms a current Shopify handle;
   - `mappingStatus=UNMAPPED`;
   - current Shopify handle remains visible;
   - mapping-unavailable copy renders;
   - awaiting-confirmation copy does not render unless explicit requested-selection query context exists;
   - generic cycle/meter top-up verification copy does not own the unmapped state;
   - SHOPIFY-009 balances are not zeroed or suppressed by mapping state.

Do not add broad combinatorial tests merely to increase test count.

### Attempt 3 validation

Run:

```text
npm test -- --run \
  tests/unit/routes/billing-callback.test.ts \
  tests/unit/billing-purchase-hub.test.tsx \
  tests/unit/subscription-change-panel.test.tsx \
  tests/unit/billing-ui.test.ts

npm test
npm run typecheck
npm run build
git diff --check
```

`npm run typecheck` may retain only the already documented unrelated JSX baseline diagnostics. There must be no new diagnostic in an Attempt-3 touched file.

### Stop conditions

STOP and return to `moda_architect` without widening scope if the correction appears to require:

- persisting callback `plan_handle` as a durable current/pending subscription fact before Partner confirms it;
- changing `recordHostedPlanChangeReturn()` classification semantics;
- changing SHOPIFY-013 provider/commercial types;
- changing SHOPIFY-009 capacity semantics;
- changing SHOPIFY-014 purchase lifecycle/idempotency/provider-evidence semantics;
- granting/forfeiting/opening/closing any entitlement from the callback;
- changing Prisma/shared/background contracts;
- implementing SHOPIFY-016 or SHOPIFY-020.

### Workflow state after this revised review

Authoritative state after applying this review:

```text
status: ready
attempt: 2
executor: null
claimed_at: null
```

The next `/moda-task ARCH-010-SHOPIFY-012` claim MUST increment to Attempt 3 exactly once.

Do not start `ARCH-010-SHOPIFY-008`, `ARCH-010-SHOPIFY-016`, `ARCH-010-SHOPIFY-026`, `ARCH-010-SHOPIFY-020` or `ARCH-010-SYSTEM-TEST-001` from this review.
