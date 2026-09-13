---
id: ARCH-010-SHOPIFY-022
architecture_id: ARCH-010
title: Show merchant promotion selection and usage history
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 86
attempt: 3
depends_on:
- ARCH-010-SHOPIFY-021
- ARCH-010-DATABASE-013
enables:
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-12
updated: 2026-09-13
---

# ARCH-010-SHOPIFY-022: Show merchant promotion selection and usage history

## Objective

Expose a tenant-safe merchant history of promotions this Shop selected/used while preserving campaign and internal Admin privacy boundaries.

## Required history

Read campaign-linked `PromotionalCreditGrant` rows for the authenticated Shop and present bounded/paginated entries containing merchant-safe information equivalent to:

```text
campaign name
original promotional quantity
committed/used quantity
remaining allocation
first/last selected time
first/last used time when present
campaign current expiry
status such as selected / used / exhausted / expired / closed / no-longer-eligible
```

The history must distinguish:

```text
selected but never used
actually used (firstUsedAt != null)
exhausted
partially used then expired/closed
reopened with remaining allocation
```

Do not infer merchant campaign history from the aggregate promotional counter.

## Privacy

Never expose Admin identity, internal audit event payloads, internal target IDs, request keys or support/internal grant classifications.

DATABASE-013 contains only campaign-linked merchant promotional grants. Do not implement a campaign-less/direct-grant fallback, fabricate a campaign identity, or query removed compatibility provenance.

## Required tests

Prove tenant isolation, selected-vs-used distinction, exhausted/expired/reopened display, remaining calculation, pagination, campaign-link integrity and absence of internal provenance leakage.

## Non-goals

Do not allow selecting campaigns from history, mutate campaign/grant quantities, reopen campaigns, refund promotional credits or add export/marketing analytics.

## Completion Report

### Status
Ready for Architect Review. Attempt 3 completed.

### Files Changed
- `moda-interact/app/services/promotions/promotion.service.ts`
- `moda-interact/app/routes/app/promotions/route.tsx`
- `moda-interact/app/i18n/locales/cs.json`
- `moda-interact/app/i18n/locales/da.json`
- `moda-interact/app/i18n/locales/de.json`
- `moda-interact/app/i18n/locales/en.json`
- `moda-interact/app/i18n/locales/es.json`
- `moda-interact/app/i18n/locales/fi.json`
- `moda-interact/app/i18n/locales/fr.json`
- `moda-interact/app/i18n/locales/it.json`
- `moda-interact/app/i18n/locales/ja.json`
- `moda-interact/app/i18n/locales/ko.json`
- `moda-interact/app/i18n/locales/nb.json`
- `moda-interact/app/i18n/locales/nl.json`
- `moda-interact/app/i18n/locales/pl.json`
- `moda-interact/app/i18n/locales/pt-BR.json`
- `moda-interact/app/i18n/locales/pt-PT.json`
- `moda-interact/app/i18n/locales/sv.json`
- `moda-interact/app/i18n/locales/th.json`
- `moda-interact/app/i18n/locales/tr.json`
- `moda-interact/app/i18n/locales/zh-Hans.json`
- `moda-interact/app/i18n/locales/zh-Hant.json`
- `moda-interact/tests/unit/services/promotion.service.test.ts`
- `moda-interact/tests/unit/routes/promotion-route.test.ts`
- `moda-interact/tests/unit/merchant-i18n.test.ts`

### Work Completed
- Added a tenant-scoped `getPromotionHistory` query over exact `PromotionalCreditGrant` rows, bounded to 25 entries per page and ordered by selection history.
- Added merchant-safe campaign history projection for granted, committed, remaining, selection/use timestamps, current expiry, current-selection state and lifecycle status.
- Distinguishes selected, used, exhausted, expired, closed, no-longer-eligible and reopened history without reading aggregate promotional counters or internal provenance.
- Added history presentation and Previous/Next pagination to the existing promotions route; history exposes no mutation controls or internal admin metadata.
- Real `REOPENED` now requires the latest server-side `PromotionCampaignEvent` of kind `REOPENED` to have `createdAt > firstSelectedAt` and positive remaining allocation; selection count and current selection are not lifecycle evidence.
- Added regressions for selection-count false positives, genuine and pre-selection reopen events, selected/non-selected independence, terminal precedence and merchant-safe output privacy.
- Replaced all new history copy with `createMerchantI18n` keys and added the exact 17-key promotion-history/status family to all 20 locale catalogues. Non-English catalogues use the reviewed translated values; placeholders remain `{quantity}`, `{first}`, `{last}`, `{value}` and `{status}`.
- Attempt 3 completed the required evidence-only corrections in `moda-interact/tests/unit/services/promotion.service.test.ts`: expired and no-longer-eligible cases now include the same genuine post-selection `reopenedAt` evidence as the reopened case, proving all four terminal/ineligible precedence rules; the query-to-projection assertion proves reopen evidence classifies the row without exposing `events`, `reopenedAt`, Admin identity, target IDs or `requestKey`.

### Validation Results
- Focused promotion service/route/merchant-i18n tests: passed, 46/46 across 3 files.
- Attempt 3 focused promotion service tests: passed, 28/28.
- Full test suite: passed, 316 tests; 34 files passed and 2 skipped (3 tests skipped).
- Production build: passed; Prisma client generated and React Router client/SSR bundles built.
- `git diff --check`: passed.
- Attempt 3 made no production, route, locale, schema or dependency changes; the implementation worktree contained only the authorized service test change.
- `npm run typecheck`: repository baseline failure; no diagnostics in the changed promotion service or route. Existing errors remain across unrelated JSX, billing, webhook and Redis files.
- `npm run lint`: repository baseline failure with 11 unrelated errors in onboarding, billing, merchant support, privacy and webhook files; no errors in changed promotion files. TypeScript 5.9 unsupported-version warning also remains baseline.

### Git / VCS
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-022` on `task/ARCH-010-SHOPIFY-022`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-022` on `task/ARCH-010-SHOPIFY-022`.
- Launcher preparation for Attempt 2: dependency gate passed; existing parent and implementation worktrees reused and synchronized; recursive database submodule ready at `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`; Attempt 2 claim committed and pushed by launcher as `91bd36157f7623bbe9e0a918ae175011798f1aa4`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-022` on `task/ARCH-010-SHOPIFY-022`; implementation commit `836983f` pushed to `origin/task/ARCH-010-SHOPIFY-022`.
- Attempt 3 prepared launcher evidence: canonical parent and implementation worktrees were reused and synchronized on the mirrored task branch; dependencies passed; recursive database submodule was ready at `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`; the Attempt 3 claim commit was `c4216dcff4c2054e22e961b76e284f545a1a8a52`.
- Implementation Attempt 3 commit `666409d` was pushed to `origin/task/ARCH-010-SHOPIFY-022`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-022` on the mirrored task branch; claim metadata cleared for Architect Review and this report is ready to commit and push.

### Architect Review

#### Review Status

Changes Requested

#### Review Notes

Attempt 1 is not accepted. Preserve the tenant-scoped grant query, 25-row pagination, exact grant-lot accounting, privacy-safe projection, current-selection projection and existing selection implementation. The correction is limited to the two findings below plus the tests/documentation required to prove them.

##### Finding 1 — `REOPENED` is inferred from selection history instead of campaign lifecycle truth

Current production logic classifies a row as `REOPENED` when:

```text
campaign.status == ACTIVE
AND MerchantPromotionSelection is absent
AND PromotionalCreditGrant.selectionCount > 1
```

That predicate does **not** prove the campaign was reopened. `selectionCount` records merchant selection/reselection, not `PromotionCampaignEvent(REOPENED)`. A merchant can increment `selectionCount` without any campaign close/reopen lifecycle event, and later have no current selection. Such a row is currently falsely labelled `REOPENED`.

Correct this deterministically in `moda-interact/app/services/promotions/promotion.service.ts`:

1. Keep `PromotionalCreditGrant(campaignId, shopId)` as the merchant-history/accounting authority. Do not add another history table or counter.
2. In the existing nested `campaign` read for `getPromotionHistory`, read only the lifecycle evidence required to identify an actual reopen:

```ts
events: {
  where: { kind: "REOPENED" },
  orderBy: { createdAt: "desc" },
  take: 1,
  select: { createdAt: true },
}
```

Do **not** select or return `platformAdminId`, the PlatformAdmin relation, old/new audit payloads, or the lifecycle event object in the merchant history result. The event timestamp is server-side classification evidence only.
3. Extend the internal projection input to accept the selected reopen timestamp evidence. Do not expose that evidence as a merchant history field.
4. Calculate remaining allocation exactly as today:

```text
max(0, quantity - reservedQuantity - committedQuantity)
```

5. Use this status precedence exactly:

```text
if exhaustedAt != null                         -> EXHAUSTED
else if campaign.status == CLOSED              -> CLOSED
else if campaign.expiresAt <= now              -> EXPIRED
else if current merchant is not target-eligible -> NO_LONGER_ELIGIBLE
else if latest REOPENED event exists
     AND firstSelectedAt != null
     AND reopenedAt > firstSelectedAt
     AND remaining allocation > 0              -> REOPENED
else if firstUsedAt != null                     -> USED
else                                             -> SELECTED
```

6. Remove `selectionCount > 1` and `selection === null` as reopen evidence. `currentlySelected` remains a separate field derived only from `MerchantPromotionSelection`; it must not decide whether the campaign lifecycle was reopened.
7. Preserve status precedence so a genuinely reopened campaign that is now exhausted, closed, expired or no-longer-eligible reports that current terminal/ineligible condition instead of `REOPENED`.

Required focused behavioural evidence:

- `selectionCount > 1` with **no** `REOPENED` campaign event does not report `REOPENED`;
- a real `REOPENED` event after `firstSelectedAt`, with remaining allocation, reports `REOPENED`;
- a `REOPENED` event that predates this merchant's `firstSelectedAt` does not make that merchant grant `REOPENED`;
- actual reopen classification does not depend on `currentlySelected`; prove both selected and non-selected projections where practical;
- EXHAUSTED/CLOSED/EXPIRED/NO_LONGER_ELIGIBLE continue to take precedence over reopen;
- the returned merchant row contains no event object, Admin identity, target IDs, request keys or other internal provenance.

##### Finding 2 — the new merchant history UI violates the accepted promotion i18n contract

`SHOPIFY-021` established the merchant promotion route's invariant that **all new static promotion copy uses the existing merchant i18n runtime and all 20 locale catalogues**. Attempt 1 adds English-only strings including the history heading/suffix, empty state, Granted/Used/Selected labels, Currently selected, Yes/No, Status, lifecycle labels and Previous/Next.

Correct this in `moda-interact/app/routes/app/promotions/route.tsx` and the existing locale catalogues. Use the existing `createMerchantI18n` runtime; do not introduce another localisation mechanism.

Add and use this bounded key family (exact key names):

```text
promotions.history.title
promotions.history.empty
promotions.history.granted
promotions.history.usedCredits
promotions.history.selectedRange
promotions.history.usedRange
promotions.history.currentlySelected
promotions.history.status
promotions.history.yes
promotions.history.no
promotions.history.previous
promotions.history.next
promotions.status.used
promotions.status.expired
promotions.status.closed
promotions.status.noLongerEligible
promotions.status.reopened
```

Canonical English meanings:

```text
promotions.history.title               Promotion history
promotions.history.empty               No selected promotion history.
promotions.history.granted             Granted: {quantity}
promotions.history.usedCredits         Used: {quantity}
promotions.history.selectedRange       Selected: {first} – {last}
promotions.history.usedRange           Used: {first} – {last}
promotions.history.currentlySelected   Currently selected: {value}
promotions.history.status              Status: {status}
promotions.history.yes                 Yes
promotions.history.no                  No
promotions.history.previous            Previous
promotions.history.next                Next
promotions.status.used                 Used
promotions.status.expired              Expired
promotions.status.closed               Closed
promotions.status.noLongerEligible     No longer eligible
promotions.status.reopened             Reopened
```

Add locale-appropriate translations to **every** current catalogue. Do not make Luna discover or translate these strings. Use the exact translations below for the 19 non-English catalogues, and use the canonical English values above for `en.json`. Preserve the placeholders exactly (`{quantity}`, `{first}`, `{last}`, `{value}`, `{status}`).

The 20 catalogue files are:

```text
cs.json
da.json
de.json
en.json
es.json
fi.json
fr.json
it.json
ja.json
ko.json
nb.json
nl.json
pl.json
pt-BR.json
pt-PT.json
sv.json
th.json
tr.json
zh-Hans.json
zh-Hant.json
```

Exact non-English values:

##### `cs.json`

```json
"promotions.history.title": "Historie akcí",
"promotions.history.empty": "Žádná historie vybraných akcí.",
"promotions.history.granted": "Přiděleno: {quantity}",
"promotions.history.usedCredits": "Použito: {quantity}",
"promotions.history.selectedRange": "Vybráno: {first} – {last}",
"promotions.history.usedRange": "Použito: {first} – {last}",
"promotions.history.currentlySelected": "Aktuálně vybráno: {value}",
"promotions.history.status": "Stav: {status}",
"promotions.history.yes": "Ano",
"promotions.history.no": "Ne",
"promotions.history.previous": "Předchozí",
"promotions.history.next": "Další",
"promotions.status.used": "Použito",
"promotions.status.expired": "Vypršelo",
"promotions.status.closed": "Uzavřeno",
"promotions.status.noLongerEligible": "Již nesplňuje podmínky",
"promotions.status.reopened": "Znovu otevřeno"
```

##### `da.json`

```json
"promotions.history.title": "Kampagnehistorik",
"promotions.history.empty": "Ingen historik over valgte kampagner.",
"promotions.history.granted": "Tildelt: {quantity}",
"promotions.history.usedCredits": "Brugt: {quantity}",
"promotions.history.selectedRange": "Valgt: {first} – {last}",
"promotions.history.usedRange": "Brugt: {first} – {last}",
"promotions.history.currentlySelected": "Aktuelt valgt: {value}",
"promotions.history.status": "Status: {status}",
"promotions.history.yes": "Ja",
"promotions.history.no": "Nej",
"promotions.history.previous": "Forrige",
"promotions.history.next": "Næste",
"promotions.status.used": "Brugt",
"promotions.status.expired": "Udløbet",
"promotions.status.closed": "Lukket",
"promotions.status.noLongerEligible": "Ikke længere berettiget",
"promotions.status.reopened": "Genåbnet"
```

##### `de.json`

```json
"promotions.history.title": "Aktionsverlauf",
"promotions.history.empty": "Kein Verlauf ausgewählter Aktionen.",
"promotions.history.granted": "Zugewiesen: {quantity}",
"promotions.history.usedCredits": "Verwendet: {quantity}",
"promotions.history.selectedRange": "Ausgewählt: {first} – {last}",
"promotions.history.usedRange": "Verwendet: {first} – {last}",
"promotions.history.currentlySelected": "Aktuell ausgewählt: {value}",
"promotions.history.status": "Status: {status}",
"promotions.history.yes": "Ja",
"promotions.history.no": "Nein",
"promotions.history.previous": "Zurück",
"promotions.history.next": "Weiter",
"promotions.status.used": "Verwendet",
"promotions.status.expired": "Abgelaufen",
"promotions.status.closed": "Geschlossen",
"promotions.status.noLongerEligible": "Nicht mehr berechtigt",
"promotions.status.reopened": "Wieder geöffnet"
```

##### `es.json`

```json
"promotions.history.title": "Historial de promociones",
"promotions.history.empty": "No hay historial de promociones seleccionadas.",
"promotions.history.granted": "Concedidos: {quantity}",
"promotions.history.usedCredits": "Usados: {quantity}",
"promotions.history.selectedRange": "Seleccionada: {first} – {last}",
"promotions.history.usedRange": "Usada: {first} – {last}",
"promotions.history.currentlySelected": "Seleccionada actualmente: {value}",
"promotions.history.status": "Estado: {status}",
"promotions.history.yes": "Sí",
"promotions.history.no": "No",
"promotions.history.previous": "Anterior",
"promotions.history.next": "Siguiente",
"promotions.status.used": "Usada",
"promotions.status.expired": "Caducada",
"promotions.status.closed": "Cerrada",
"promotions.status.noLongerEligible": "Ya no cumple los requisitos",
"promotions.status.reopened": "Reabierta"
```

##### `fi.json`

```json
"promotions.history.title": "Kampanjahistoria",
"promotions.history.empty": "Ei valittujen kampanjoiden historiaa.",
"promotions.history.granted": "Myönnetty: {quantity}",
"promotions.history.usedCredits": "Käytetty: {quantity}",
"promotions.history.selectedRange": "Valittu: {first} – {last}",
"promotions.history.usedRange": "Käytetty: {first} – {last}",
"promotions.history.currentlySelected": "Tällä hetkellä valittu: {value}",
"promotions.history.status": "Tila: {status}",
"promotions.history.yes": "Kyllä",
"promotions.history.no": "Ei",
"promotions.history.previous": "Edellinen",
"promotions.history.next": "Seuraava",
"promotions.status.used": "Käytetty",
"promotions.status.expired": "Vanhentunut",
"promotions.status.closed": "Suljettu",
"promotions.status.noLongerEligible": "Ei enää kelvollinen",
"promotions.status.reopened": "Avattu uudelleen"
```

##### `fr.json`

```json
"promotions.history.title": "Historique des promotions",
"promotions.history.empty": "Aucun historique de promotions sélectionnées.",
"promotions.history.granted": "Accordés : {quantity}",
"promotions.history.usedCredits": "Utilisés : {quantity}",
"promotions.history.selectedRange": "Sélectionnée : {first} – {last}",
"promotions.history.usedRange": "Utilisée : {first} – {last}",
"promotions.history.currentlySelected": "Actuellement sélectionnée : {value}",
"promotions.history.status": "Statut : {status}",
"promotions.history.yes": "Oui",
"promotions.history.no": "Non",
"promotions.history.previous": "Précédent",
"promotions.history.next": "Suivant",
"promotions.status.used": "Utilisée",
"promotions.status.expired": "Expirée",
"promotions.status.closed": "Fermée",
"promotions.status.noLongerEligible": "Plus éligible",
"promotions.status.reopened": "Rouverte"
```

##### `it.json`

```json
"promotions.history.title": "Cronologia promozioni",
"promotions.history.empty": "Nessuna cronologia delle promozioni selezionate.",
"promotions.history.granted": "Assegnati: {quantity}",
"promotions.history.usedCredits": "Utilizzati: {quantity}",
"promotions.history.selectedRange": "Selezionata: {first} – {last}",
"promotions.history.usedRange": "Utilizzata: {first} – {last}",
"promotions.history.currentlySelected": "Attualmente selezionata: {value}",
"promotions.history.status": "Stato: {status}",
"promotions.history.yes": "Sì",
"promotions.history.no": "No",
"promotions.history.previous": "Precedente",
"promotions.history.next": "Successivo",
"promotions.status.used": "Utilizzata",
"promotions.status.expired": "Scaduta",
"promotions.status.closed": "Chiusa",
"promotions.status.noLongerEligible": "Non più idonea",
"promotions.status.reopened": "Riaperta"
```

##### `ja.json`

```json
"promotions.history.title": "プロモーション履歴",
"promotions.history.empty": "選択済みプロモーションの履歴はありません。",
"promotions.history.granted": "付与: {quantity}",
"promotions.history.usedCredits": "使用済み: {quantity}",
"promotions.history.selectedRange": "選択: {first} – {last}",
"promotions.history.usedRange": "使用: {first} – {last}",
"promotions.history.currentlySelected": "現在選択中: {value}",
"promotions.history.status": "ステータス: {status}",
"promotions.history.yes": "はい",
"promotions.history.no": "いいえ",
"promotions.history.previous": "前へ",
"promotions.history.next": "次へ",
"promotions.status.used": "使用済み",
"promotions.status.expired": "期限切れ",
"promotions.status.closed": "終了",
"promotions.status.noLongerEligible": "対象外",
"promotions.status.reopened": "再開済み"
```

##### `ko.json`

```json
"promotions.history.title": "프로모션 기록",
"promotions.history.empty": "선택한 프로모션 기록이 없습니다.",
"promotions.history.granted": "지급: {quantity}",
"promotions.history.usedCredits": "사용: {quantity}",
"promotions.history.selectedRange": "선택: {first} – {last}",
"promotions.history.usedRange": "사용: {first} – {last}",
"promotions.history.currentlySelected": "현재 선택됨: {value}",
"promotions.history.status": "상태: {status}",
"promotions.history.yes": "예",
"promotions.history.no": "아니요",
"promotions.history.previous": "이전",
"promotions.history.next": "다음",
"promotions.status.used": "사용됨",
"promotions.status.expired": "만료됨",
"promotions.status.closed": "종료됨",
"promotions.status.noLongerEligible": "더 이상 대상 아님",
"promotions.status.reopened": "다시 열림"
```

##### `nb.json`

```json
"promotions.history.title": "Kampanjehistorikk",
"promotions.history.empty": "Ingen historikk for valgte kampanjer.",
"promotions.history.granted": "Tildelt: {quantity}",
"promotions.history.usedCredits": "Brukt: {quantity}",
"promotions.history.selectedRange": "Valgt: {first} – {last}",
"promotions.history.usedRange": "Brukt: {first} – {last}",
"promotions.history.currentlySelected": "Valgt nå: {value}",
"promotions.history.status": "Status: {status}",
"promotions.history.yes": "Ja",
"promotions.history.no": "Nei",
"promotions.history.previous": "Forrige",
"promotions.history.next": "Neste",
"promotions.status.used": "Brukt",
"promotions.status.expired": "Utløpt",
"promotions.status.closed": "Lukket",
"promotions.status.noLongerEligible": "Ikke lenger kvalifisert",
"promotions.status.reopened": "Gjenåpnet"
```

##### `nl.json`

```json
"promotions.history.title": "Promotiegeschiedenis",
"promotions.history.empty": "Geen geschiedenis van geselecteerde promoties.",
"promotions.history.granted": "Toegekend: {quantity}",
"promotions.history.usedCredits": "Gebruikt: {quantity}",
"promotions.history.selectedRange": "Geselecteerd: {first} – {last}",
"promotions.history.usedRange": "Gebruikt: {first} – {last}",
"promotions.history.currentlySelected": "Momenteel geselecteerd: {value}",
"promotions.history.status": "Status: {status}",
"promotions.history.yes": "Ja",
"promotions.history.no": "Nee",
"promotions.history.previous": "Vorige",
"promotions.history.next": "Volgende",
"promotions.status.used": "Gebruikt",
"promotions.status.expired": "Verlopen",
"promotions.status.closed": "Gesloten",
"promotions.status.noLongerEligible": "Niet langer in aanmerking",
"promotions.status.reopened": "Heropend"
```

##### `pl.json`

```json
"promotions.history.title": "Historia promocji",
"promotions.history.empty": "Brak historii wybranych promocji.",
"promotions.history.granted": "Przyznano: {quantity}",
"promotions.history.usedCredits": "Wykorzystano: {quantity}",
"promotions.history.selectedRange": "Wybrano: {first} – {last}",
"promotions.history.usedRange": "Użyto: {first} – {last}",
"promotions.history.currentlySelected": "Obecnie wybrana: {value}",
"promotions.history.status": "Status: {status}",
"promotions.history.yes": "Tak",
"promotions.history.no": "Nie",
"promotions.history.previous": "Poprzednia",
"promotions.history.next": "Następna",
"promotions.status.used": "Wykorzystana",
"promotions.status.expired": "Wygasła",
"promotions.status.closed": "Zamknięta",
"promotions.status.noLongerEligible": "Już nie kwalifikuje się",
"promotions.status.reopened": "Ponownie otwarta"
```

##### `pt-BR.json`

```json
"promotions.history.title": "Histórico de promoções",
"promotions.history.empty": "Nenhum histórico de promoções selecionadas.",
"promotions.history.granted": "Concedidos: {quantity}",
"promotions.history.usedCredits": "Usados: {quantity}",
"promotions.history.selectedRange": "Selecionada: {first} – {last}",
"promotions.history.usedRange": "Usada: {first} – {last}",
"promotions.history.currentlySelected": "Selecionada atualmente: {value}",
"promotions.history.status": "Status: {status}",
"promotions.history.yes": "Sim",
"promotions.history.no": "Não",
"promotions.history.previous": "Anterior",
"promotions.history.next": "Próxima",
"promotions.status.used": "Usada",
"promotions.status.expired": "Expirada",
"promotions.status.closed": "Encerrada",
"promotions.status.noLongerEligible": "Não é mais elegível",
"promotions.status.reopened": "Reaberta"
```

##### `pt-PT.json`

```json
"promotions.history.title": "Histórico de promoções",
"promotions.history.empty": "Sem histórico de promoções selecionadas.",
"promotions.history.granted": "Atribuídos: {quantity}",
"promotions.history.usedCredits": "Utilizados: {quantity}",
"promotions.history.selectedRange": "Selecionada: {first} – {last}",
"promotions.history.usedRange": "Utilizada: {first} – {last}",
"promotions.history.currentlySelected": "Atualmente selecionada: {value}",
"promotions.history.status": "Estado: {status}",
"promotions.history.yes": "Sim",
"promotions.history.no": "Não",
"promotions.history.previous": "Anterior",
"promotions.history.next": "Seguinte",
"promotions.status.used": "Utilizada",
"promotions.status.expired": "Expirada",
"promotions.status.closed": "Encerrada",
"promotions.status.noLongerEligible": "Já não elegível",
"promotions.status.reopened": "Reaberta"
```

##### `sv.json`

```json
"promotions.history.title": "Kampanjhistorik",
"promotions.history.empty": "Ingen historik för valda kampanjer.",
"promotions.history.granted": "Tilldelade: {quantity}",
"promotions.history.usedCredits": "Använda: {quantity}",
"promotions.history.selectedRange": "Vald: {first} – {last}",
"promotions.history.usedRange": "Använd: {first} – {last}",
"promotions.history.currentlySelected": "Vald just nu: {value}",
"promotions.history.status": "Status: {status}",
"promotions.history.yes": "Ja",
"promotions.history.no": "Nej",
"promotions.history.previous": "Föregående",
"promotions.history.next": "Nästa",
"promotions.status.used": "Använd",
"promotions.status.expired": "Utgången",
"promotions.status.closed": "Stängd",
"promotions.status.noLongerEligible": "Inte längre behörig",
"promotions.status.reopened": "Återöppnad"
```

##### `th.json`

```json
"promotions.history.title": "ประวัติโปรโมชัน",
"promotions.history.empty": "ไม่มีประวัติโปรโมชันที่เลือก",
"promotions.history.granted": "ได้รับ: {quantity}",
"promotions.history.usedCredits": "ใช้แล้ว: {quantity}",
"promotions.history.selectedRange": "เลือก: {first} – {last}",
"promotions.history.usedRange": "ใช้: {first} – {last}",
"promotions.history.currentlySelected": "เลือกอยู่ในขณะนี้: {value}",
"promotions.history.status": "สถานะ: {status}",
"promotions.history.yes": "ใช่",
"promotions.history.no": "ไม่",
"promotions.history.previous": "ก่อนหน้า",
"promotions.history.next": "ถัดไป",
"promotions.status.used": "ใช้แล้ว",
"promotions.status.expired": "หมดอายุแล้ว",
"promotions.status.closed": "ปิดแล้ว",
"promotions.status.noLongerEligible": "ไม่มีสิทธิ์แล้ว",
"promotions.status.reopened": "เปิดอีกครั้งแล้ว"
```

##### `tr.json`

```json
"promotions.history.title": "Promosyon geçmişi",
"promotions.history.empty": "Seçilen promosyon geçmişi yok.",
"promotions.history.granted": "Verilen: {quantity}",
"promotions.history.usedCredits": "Kullanılan: {quantity}",
"promotions.history.selectedRange": "Seçildi: {first} – {last}",
"promotions.history.usedRange": "Kullanıldı: {first} – {last}",
"promotions.history.currentlySelected": "Şu anda seçili: {value}",
"promotions.history.status": "Durum: {status}",
"promotions.history.yes": "Evet",
"promotions.history.no": "Hayır",
"promotions.history.previous": "Önceki",
"promotions.history.next": "Sonraki",
"promotions.status.used": "Kullanıldı",
"promotions.status.expired": "Süresi doldu",
"promotions.status.closed": "Kapatıldı",
"promotions.status.noLongerEligible": "Artık uygun değil",
"promotions.status.reopened": "Yeniden açıldı"
```

##### `zh-Hans.json`

```json
"promotions.history.title": "促销历史",
"promotions.history.empty": "没有已选择的促销历史。",
"promotions.history.granted": "已授予：{quantity}",
"promotions.history.usedCredits": "已使用：{quantity}",
"promotions.history.selectedRange": "已选择：{first} – {last}",
"promotions.history.usedRange": "使用：{first} – {last}",
"promotions.history.currentlySelected": "当前已选择：{value}",
"promotions.history.status": "状态：{status}",
"promotions.history.yes": "是",
"promotions.history.no": "否",
"promotions.history.previous": "上一页",
"promotions.history.next": "下一页",
"promotions.status.used": "已使用",
"promotions.status.expired": "已过期",
"promotions.status.closed": "已关闭",
"promotions.status.noLongerEligible": "不再符合资格",
"promotions.status.reopened": "已重新开放"
```

##### `zh-Hant.json`

```json
"promotions.history.title": "促銷歷史",
"promotions.history.empty": "沒有已選擇的促銷歷史。",
"promotions.history.granted": "已授予：{quantity}",
"promotions.history.usedCredits": "已使用：{quantity}",
"promotions.history.selectedRange": "已選擇：{first} – {last}",
"promotions.history.usedRange": "使用：{first} – {last}",
"promotions.history.currentlySelected": "目前已選擇：{value}",
"promotions.history.status": "狀態：{status}",
"promotions.history.yes": "是",
"promotions.history.no": "否",
"promotions.history.previous": "上一頁",
"promotions.history.next": "下一頁",
"promotions.status.used": "已使用",
"promotions.status.expired": "已過期",
"promotions.status.closed": "已關閉",
"promotions.status.noLongerEligible": "不再符合資格",
"promotions.status.reopened": "已重新開放"
```

Admin-authored campaign names remain displayed as authored; do not translate campaign content. Date/time values must continue through the existing merchant formatter.

Update `tests/unit/merchant-i18n.test.ts` and `tests/unit/routes/promotion-route.test.ts` so the new keys are part of catalogue parity/route evidence and the route no longer contains the new raw English UI strings. Preserve the existing SHOPIFY-021 semantic-translation checks; extend them for representative new promotion-history keys rather than weakening/removing them.

#### Reviewed Files

```text
moda-interact/app/services/promotions/promotion.service.ts
moda-interact/app/routes/app/promotions/route.tsx
moda-interact/tests/unit/services/promotion.service.test.ts
moda-interact/tests/unit/routes/promotion-route.test.ts
moda-interact/database/prisma/schema.prisma
docs/architecture/ARCH-010-promotional-campaigns.md
docs/decisions/database/ARCH-010/DATABASE-013-first-production-schema-baseline.md
docs/decisions/shopify/ARCH-010/SHOPIFY-021-promotion-offer-catalogue-and-selection.md
docs/decisions/shopify/ARCH-010/SHOPIFY-022-merchant-promotion-history.md
```

#### Validation Reviewed

Attempt-1 reported evidence was inspected:

```text
focused promotion tests: 33/33 passed
full tests: 316 passed, 3 skipped
build: passed
git diff --check: passed
typecheck/lint: documented unrelated repository baseline diagnostics only
```

Those green checks do not cover the two semantic gaps above. Attempt 2 must run:

```bash
npm test -- \
  tests/unit/services/promotion.service.test.ts \
  tests/unit/routes/promotion-route.test.ts \
  tests/unit/merchant-i18n.test.ts

npm test
npm run build
npm run typecheck
npm run lint
git diff --check
```

For `typecheck`/`lint`, baseline failures may be reported only when they remain unrelated to the files changed by Attempt 2. Any diagnostic in the changed promotion service, route, locale/i18n path or changed tests is an Attempt-2 failure and must be fixed before returning to review.

#### Architecture Conformance

Conforms and must be preserved:

- history query is scoped by authenticated `shopId` for both count and row retrieval;
- one campaign-linked `PromotionalCreditGrant` is the history/accounting authority;
- remaining allocation subtracts both reserved and committed quantities;
- page size is bounded to 25;
- current selection is distinct from historical grant ownership;
- no history mutation path was introduced;
- Admin identity, target IDs and other internal provenance are omitted from the merchant result.

Does not yet conform:

- `REOPENED` is not based on durable campaign lifecycle evidence;
- new merchant-visible static promotion-history copy bypasses the accepted i18n contract.

#### Scope / Non-Goals for Attempt 2

Allowed implementation files:

```text
moda-interact/app/services/promotions/promotion.service.ts
moda-interact/app/routes/app/promotions/route.tsx
moda-interact/app/i18n/locales/*.json
moda-interact/tests/unit/services/promotion.service.test.ts
moda-interact/tests/unit/routes/promotion-route.test.ts
moda-interact/tests/unit/merchant-i18n.test.ts
```

Do not change Prisma schema/migrations, Admin, Background, Shared, campaign selection rules, grant quantities, pagination page size, campaign lifecycle mutation, or any unrelated billing/runtime code. Do not expose campaign lifecycle audit rows to the browser merely to classify `REOPENED`.

#### Attempt-2 Completion Evidence

Before returning this same task to review, the Completion Report must state:

1. the exact production rule now used to establish a real campaign reopen;
2. the false-positive regression test proving `selectionCount` alone is insufficient;
3. the genuine reopen test and terminal-status precedence tests;
4. the exact locale files changed and confirmation that no new history key uses an English placeholder in non-English catalogues;
5. focused test count including `merchant-i18n.test.ts`;
6. full test/build/typecheck/lint/diff-check results with any baseline failures identified by existing baseline context;
7. launcher/worktree/recursive-submodule evidence for Attempt 2.

#### Follow-up / Stop Condition

Return the **same** `ARCH-010-SHOPIFY-022` task through `/moda-task`. The next authorized claim must increment `attempt: 1` to **Attempt 2 exactly once**. After implementing only the corrections above, update the Completion Report, set the task to `review`, clear the claim, push both mirrored task branches and STOP. Do not start `ARCH-010-SYSTEM-TEST-003` or any adjacent task.

## Architect Review — Attempt 2

### Review Status

**Changes Requested**

Attempt 2 corrects both production defects identified in Attempt 1. The production
implementation is accepted in substance:

- `REOPENED` now derives from the latest server-side
  `PromotionCampaignEvent(kind = REOPENED).createdAt`;
- `selectionCount` and current-selection presence are no longer reopen evidence;
- the exact required status precedence is implemented in production;
- the merchant projection does not return lifecycle-event data;
- all 20 locale catalogues contain the exact architect-specified history/status
  translations and placeholders;
- the route uses the existing merchant i18n runtime rather than raw English copy;
- tenant scoping, 25-row pagination, exact grant-lot accounting and privacy
  boundaries remain unchanged.

No production source or locale correction is requested by this review.

### Finding — required Attempt-2 regression evidence is incomplete

The Attempt-1 Architect Review required this exact behavioural proof:

```text
EXHAUSTED / CLOSED / EXPIRED / NO_LONGER_ELIGIBLE
continue to take precedence over an otherwise genuine REOPENED classification.
```

The current service test proves:

```text
REOPENED evidence + exhaustedAt -> EXHAUSTED
REOPENED evidence + campaign CLOSED -> CLOSED
```

but its `EXPIRED` and `NO_LONGER_ELIGIBLE` assertions do **not** include a valid
post-selection `reopenedAt`. Those two assertions therefore prove the ordinary
terminal/ineligible statuses, not their precedence over `REOPENED`.

The same review also required the returned merchant history row to prove that the
server-side reopen evidence and internal provenance do not escape into the result.
The query correctly selects only `events[].createdAt` and the projection is clean,
but the current integration-style history assertion checks only
`platformAdminId` and `targetPlanId`.

### Required Attempt-3 correction

Modify **only**:

```text
moda-interact/tests/unit/services/promotion.service.test.ts
```

plus this task's Completion Report through the normal coordination-document
exception.

Do not modify production code, route code, locale catalogues, Prisma schema,
dependencies or any other repository.

#### 1. Complete the reopen-precedence regression

In the existing test:

```text
projects selected, used, exhausted, expired, closed, and reopened history safely
```

preserve the existing assertions and add/replace assertions so these two cases
contain the same genuine post-selection reopen evidence already used by the
`REOPENED` assertion:

```ts
const reopenedAt = new Date("2026-09-13T12:01:00.000Z");
```

Add an expired case equivalent to:

```ts
expect(projectPromotionHistoryRow({
  ...baseGrant,
  reopenedAt,
  campaign: {
    ...baseGrant.campaign,
    expiresAt: new Date("2026-09-01T00:00:00.000Z"),
  },
}, "shop-1", "plan-1", now).status).toBe("EXPIRED");
```

Add a no-longer-eligible case equivalent to:

```ts
expect(projectPromotionHistoryRow({
  ...baseGrant,
  reopenedAt,
  campaign: {
    ...baseGrant.campaign,
    scope: "PLAN",
    targetPlanId: "plan-other",
  },
}, "shop-1", "plan-1", now).status).toBe("NO_LONGER_ELIGIBLE");
```

The test must therefore prove all four precedence cases with valid reopen evidence:

```text
REOPENED + exhausted                -> EXHAUSTED
REOPENED + CLOSED                   -> CLOSED
REOPENED + expired                  -> EXPIRED
REOPENED + no longer target-eligible -> NO_LONGER_ELIGIBLE
```

Do not change the production precedence merely to satisfy the test; it is already
ordered correctly.

#### 2. Complete the query-to-projection privacy evidence

In:

```text
reads only the authenticated shop's campaign-linked grants with bounded pagination
```

the mocked grant already contains:

```ts
events: [{ createdAt: new Date("2026-09-13T12:01:00.000Z") }]
```

After calling `getPromotionHistory(...)`, add assertions proving the query evidence
was consumed for classification but was not returned to the merchant:

```ts
expect(history.entries[0]).toMatchObject({
  campaignId: "campaign-1",
  status: "REOPENED",
});

expect(history.entries[0]).not.toHaveProperty("events");
expect(history.entries[0]).not.toHaveProperty("reopenedAt");
expect(history.entries[0]).not.toHaveProperty("platformAdminId");
expect(history.entries[0]).not.toHaveProperty("targetPlanId");
expect(history.entries[0]).not.toHaveProperty("targetShopId");
expect(history.entries[0]).not.toHaveProperty("requestKey");
```

Keep the existing assertion that the Prisma campaign event selection is exactly:

```ts
events: {
  where: { kind: "REOPENED" },
  orderBy: { createdAt: "desc" },
  take: 1,
  select: { createdAt: true },
}
```

Do not expose the event object or timestamp merely to make the test pass.

### Required validation

From `moda-interact` run:

```bash
npm test -- tests/unit/services/promotion.service.test.ts

npm test -- \
  tests/unit/services/promotion.service.test.ts \
  tests/unit/routes/promotion-route.test.ts \
  tests/unit/merchant-i18n.test.ts

npm test
npm run build
git diff --check
```

Because Attempt 3 is test/evidence-only, `npm run typecheck` and `npm run lint` do
not need to be re-investigated unless the changed test produces a new diagnostic or
the observed baseline differs from Attempt 2. If they are rerun, report the result
honestly and do not modify unrelated baseline files.

Record exact pass/fail/skip counts in the Completion Report.

### Scope boundary

Attempt 3 must make **no production changes**. In particular, do not modify:

```text
app/services/promotions/promotion.service.ts
app/routes/app/promotions/route.tsx
app/i18n/locales/*.json
database/prisma/**
package.json
package-lock.json
```

Do not create a new history model, lifecycle rule, translation mechanism or privacy
projection. The existing Attempt-2 implementation is the baseline to preserve.

### Reclaim and stop condition

Return this **same** task through `/moda-task`.

The current attempt remains:

```text
attempt: 2
```

The next authorized claim must increment it to **Attempt 3 exactly once**.

After adding only the required regression/privacy assertions, running the validation,
updating the Completion Report, setting the task back to `status: review`, clearing
the claim, committing/pushing both mirrored task branches, STOP and return to
`moda_architect`.

Do not start `ARCH-010-SYSTEM-TEST-003` or any adjacent task.

