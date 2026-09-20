---
id: ARCH-018-SHOPIFY-001
architecture_id: ARCH-018
title: Enforce promotion selection until expiry and make the merchant UI explicit
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SHOPIFY-021
- ARCH-010-SHOPIFY-022
enables:
- ARCH-018-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# ARCH-018-SHOPIFY-001

## Objective

Change merchant promotion selection so a selected promotion occupies the Shop's single selection slot until the selected `PromotionCampaign.expiresAt`, regardless of credit exhaustion, campaign closure, or target ineligibility.

Make that rule explicit on `/app/promotions` and prevent rapid/double UI submission without weakening server-side SERIALIZABLE authority.

Do not wait for Background cleanup before allowing a new selection after expiry.

## Dependency/baseline gate

The accepted ARCH-010 promotion catalogue/selection/history implementation is the baseline:

```text
ARCH-010-SHOPIFY-021
ARCH-010-SHOPIFY-022
```

Do not redesign campaign Admin management, grant allocation, reservation priority, billing lifecycle, translation architecture, or database schema.

## Read before editing

Read completely:

```text
app/services/promotions/promotion.service.ts
app/routes/app/promotions/route.tsx
app/routes/app/promotions/PromotionsRoute.css
app/i18n/catalogues.js
app/i18n/locales/*.json
app/utils/merchant-i18n.js
tests/unit/services/promotion.service.test.ts
tests/unit/routes/promotion-route.test.ts
tests/unit/merchant-i18n.test.ts
database/prisma/schema.prisma
docs/architecture/ARCH-018-promotion-selection-lock-and-expiry-reconciliation.md
```

## Authorized implementation surface

Production:

```text
app/services/promotions/promotion.service.ts
app/routes/app/promotions/route.tsx
app/routes/app/promotions/PromotionsRoute.css
app/i18n/locales/*.json
```

Tests:

```text
tests/unit/services/promotion.service.test.ts
tests/unit/routes/promotion-route.test.ts
tests/unit/merchant-i18n.test.ts
```

Do not modify the Prisma schema/migrations, Background repository, Admin repository, package manifest, billing services, campaign Admin flows or recovery reservation services.

If the required behaviour cannot be implemented inside the authorized surface, STOP and return the concrete dependency to `moda_architect`.

---

# Part A — selection lock server contract

## A1. Keep the existing error code

Do not rename:

```ts
ACTIVE_PROMOTION_ALREADY_SELECTED
```

Its meaning changes from "different still-usable promotion exists" to:

```text
a current MerchantPromotionSelection points to a campaign whose expiresAt > now
```

This minimizes API/i18n churn.

## A2. Replace the current blocking predicate exactly

File:

```text
app/services/promotions/promotion.service.ts
```

Inside `selectPromotionOffer()`, keep the requested campaign eligibility check unchanged:

```text
campaign exists
campaign.status === ACTIVE
campaign.startsAt <= now
campaign.expiresAt > now
requested campaign target is eligible
merchant subscription is executable
```

After loading `current`, replace the current blocker that checks:

```text
current campaign differs from requested campaign
isUsableGrant(currentGrant)
current campaign ACTIVE
current campaign started
current campaign unexpired
current campaign target eligible
```

with this exact rule:

```ts
const currentGrant = current?.promotionalCreditGrant ?? null;

if (
  current &&
  currentGrant &&
  currentGrant.campaign.expiresAt > now
) {
  throw new PromotionSelectionError("ACTIVE_PROMOTION_ALREADY_SELECTED");
}
```

Do not include any of these in the lock predicate:

```text
currentGrant.campaignId !== campaignId
isUsableGrant(currentGrant)
currentGrant.exhaustedAt
currentGrant quantity/reservedQuantity/committedQuantity
currentGrant.campaign.status
currentGrant.campaign.startsAt
isTargetEligible(current campaign)
current shop plan
```

Consequences that MUST hold:

```text
same campaign clicked again before expiry -> blocked
another campaign clicked before expiry -> blocked
selected grant exhausted before expiry -> blocked
selected campaign CLOSED before expiry -> blocked
selected campaign no longer target-eligible before expiry -> blocked
selected campaign expiresAt <= now -> does not block
```

The requested new campaign still has to pass its own normal eligibility checks.

## A3. Preserve exact grant reuse semantics

Do not change the existing grant upsert:

```ts
await transaction.promotionalCreditGrant.upsert({
  where: { campaignId_shopId: { campaignId, shopId } },
  update: {},
  create: { campaignId, shopId, quantity: campaign.quantity },
});
```

A later valid re-selection of an old campaign reuses the original grant.

Never reset/increase:

```text
quantity
reservedQuantity
committedQuantity
exhaustedAt
```

Do not increment `selectionCount` on a blocked duplicate request.

## A4. Keep SERIALIZABLE bounded retry

Preserve:

```ts
{ isolationLevel: Prisma.TransactionIsolationLevel.Serializable }
```

and the existing maximum three attempts for Prisma `P2034`.

Do not weaken the server contract because the UI will also prevent double clicks.

---

# Part B — current promotion selection read model

## B1. Add the projection function

In `promotion.service.ts`, add:

```ts
export type CurrentPromotionSelectionState = {
  campaignId: string;
  merchantTitle: string | null;
  expiresAt: Date;
  remainingQuantity: number;
  exhausted: boolean;
  campaignStatus: string;
  targetEligible: boolean;
  spendable: boolean;
  locked: boolean;
};
```

Add:

```ts
export async function getCurrentPromotionSelectionState(
  shopId: string,
  locale: string,
  now = new Date(),
  database: PromotionDatabase = prisma,
): Promise<CurrentPromotionSelectionState | null>
```

Implementation contract:

1. call existing `readContext(database, shopId)`;
2. if there is no shop context, return `null`;
3. query `merchantPromotionSelection.findUnique({ where: { shopId } })`;
4. select only:

```text
promotionalCreditGrant.quantity
promotionalCreditGrant.reservedQuantity
promotionalCreditGrant.committedQuantity
promotionalCreditGrant.exhaustedAt
campaign.id
campaign.status
campaign.startsAt
campaign.expiresAt
campaign.scope
campaign.targetPlanId
campaign.targetShopId
campaign translation merchantTitle for the exact locale
```

5. if there is no selection, return `null`;
6. compute:

```ts
const remainingQuantity = Math.max(
  0,
  grant.quantity - grant.reservedQuantity - grant.committedQuantity,
);

const targetEligible = isTargetEligible(
  campaign,
  shopId,
  context.subscription?.planId ?? null,
);

const locked = campaign.expiresAt > now;

const spendable =
  campaign.status === "ACTIVE" &&
  campaign.startsAt <= now &&
  campaign.expiresAt > now &&
  targetEligible &&
  isUsableGrant(grant);
```

7. return exactly merchant-safe state; do not expose grant ID, selection ID, target IDs, Admin IDs or audit metadata.

`locked` MUST use only `campaign.expiresAt > now`.

## B2. Make history "currently selected" expiry-aware

In `projectPromotionHistoryRow()`, replace:

```ts
currentlySelected: grant.selection !== null,
```

with:

```ts
currentlySelected:
  grant.selection !== null && grant.campaign.expiresAt > now,
```

This prevents a stale expired pointer from showing `Currently selected: Yes` while waiting for Background cleanup.

Do not change `promotionHistoryStatus()` precedence in this task.

---

# Part C — loader and merchant UI

## C1. Load current selection independently

File:

```text
app/routes/app/promotions/route.tsx
```

Import:

```ts
getCurrentPromotionSelectionState
```

The loader must read all three promotion projections:

```ts
const [allOffers, promotionSelection, history] = await Promise.all([
  getEligiblePromotionOffers(shop.id, promotionLocale),
  getCurrentPromotionSelectionState(shop.id, promotionLocale),
  getPromotionHistory(shop.id, promotionLocale, historyPageValue),
]);
```

Use `allOffers` for pagination exactly as today and return:

```ts
promotionSelection,
history,
```

Do not infer the lock by searching the paginated offer list.

## C2. Render the lock notice

When:

```ts
promotionSelection?.locked === true
```

render a notice before the promotion-offers panel with:

```text
className="moda-promotions-lock-notice"
role="status"
```

It must display:

```text
existing localized promotions.status.selected
merchantTitle when non-null
existing localized promotions.error.activeSelected
existing localized promotions.expires + formatted promotionSelection.expiresAt
existing localized promotions.remaining + promotionSelection.remainingQuantity
```

If `promotionSelection.exhausted === true`, the existing exhausted status may also be shown, but exhaustion must not alter the lock.

The notice is required even when the selected campaign is CLOSED or target-ineligible and therefore absent from `offers`.

## C3. Button enablement rule

Define:

```ts
const selectionLocked = promotionSelection?.locked === true;
```

Every promotion `<button>` must be disabled when:

```text
selectionLocked
OR a selection submission is currently in flight
OR offer.currentlySelected
```

The selected card's disabled button text uses:

```ts
i18n.t("promotions.status.selected")
```

Non-selected cards retain the existing select/reselect labels.

Do not hide other offers while locked. The merchant must be able to see what will become available after expiry.

## C4. Implement synchronous double-click protection

Add React imports:

```ts
import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
```

Add React Router `useNavigation`.

Inside `PromotionsRoute()` create exactly one page-wide submission lock:

```ts
const navigation = useNavigation();
const submitLockRef = useRef(false);
const [submittingCampaignId, setSubmittingCampaignId] = useState<string | null>(null);

useEffect(() => {
  if (navigation.state === "idle") {
    submitLockRef.current = false;
    setSubmittingCampaignId(null);
  }
}, [navigation.state]);

const submissionInFlight =
  navigation.state !== "idle" || submittingCampaignId !== null;

const guardPromotionSubmit =
  (campaignId: string) =>
  (event: FormEvent<HTMLFormElement>) => {
    if (selectionLocked || submitLockRef.current) {
      event.preventDefault();
      return;
    }

    submitLockRef.current = true;
    setSubmittingCampaignId(campaignId);
  };
```

Attach:

```tsx
onSubmit={guardPromotionSubmit(offer.id)}
```

to every promotion form.

Every promotion button must use:

```tsx
disabled={selectionLocked || submissionInFlight || offer.currentlySelected}
aria-busy={submittingCampaignId === offer.id}
```

Do not create one ref per card.

The `useRef` is required because React state/navigation may not update before a second synchronous click event.

## C5. CSS

In `PromotionsRoute.css` add styles for:

```text
.moda-promotions-lock-notice
.moda-promotions-lock-notice h3
.moda-promotions-lock-notice p
.moda-promotion-button:disabled
```

Requirements:

```text
lock notice visually consistent with existing forest-green promotion design
button disabled state visibly distinct
button disabled cursor is not-allowed
button disabled hover must not lift/add hover shadow
no layout regression below 560px/820px breakpoints
```

Do not introduce a new styling framework.

---

# Part D — localized lock copy

Do not add a new catalogue key.

Change the semantic meaning of existing:

```text
promotions.error.activeSelected
```

from "use/exhaust the promotion first" to "the selection remains locked until expiry".

Use these exact values:

```text
cs: Aktuální promo akce zůstává vybraná až do vypršení platnosti. Jinou promo akci můžete vybrat až poté.
da: Din nuværende kampagne forbliver valgt, indtil den udløber. Du kan først vælge en anden kampagne, når den er udløbet.
de: Ihre aktuelle Aktion bleibt bis zu ihrem Ablauf ausgewählt. Erst danach können Sie eine andere Aktion auswählen.
en: Your current promotion remains selected until it expires. You can choose another promotion only after it expires.
es: Tu promoción actual seguirá seleccionada hasta que caduque. Solo podrás elegir otra promoción después de que caduque.
fi: Nykyinen kampanjasi pysyy valittuna sen voimassaolon päättymiseen asti. Voit valita toisen kampanjan vasta sen jälkeen.
fr: Votre promotion actuelle reste sélectionnée jusqu’à son expiration. Vous ne pourrez choisir une autre promotion qu’après son expiration.
it: La promozione attuale rimane selezionata fino alla scadenza. Potrai scegliere un’altra promozione solo dopo la scadenza.
ja: 現在のプロモーションは有効期限が切れるまで選択されたままです。別のプロモーションを選択できるのは、有効期限が切れた後だけです。
ko: 현재 프로모션은 만료될 때까지 선택된 상태로 유지됩니다. 다른 프로모션은 만료된 후에만 선택할 수 있습니다.
nb: Den gjeldende kampanjen forblir valgt til den utløper. Du kan først velge en annen kampanje etter at den har utløpt.
nl: Je huidige promotie blijft geselecteerd totdat deze verloopt. Je kunt pas daarna een andere promotie kiezen.
pl: Obecna promocja pozostaje wybrana do momentu jej wygaśnięcia. Inną promocję można wybrać dopiero po jej wygaśnięciu.
pt-BR: A promoção atual permanece selecionada até expirar. Você só poderá escolher outra promoção depois que ela expirar.
pt-PT: A promoção atual permanece selecionada até expirar. Só poderá escolher outra promoção depois de esta expirar.
sv: Din nuvarande kampanj förblir vald tills den löper ut. Du kan välja en annan kampanj först efter att den har löpt ut.
th: โปรโมชันปัจจุบันจะยังคงถูกเลือกไว้จนกว่าจะหมดอายุ คุณจะเลือกโปรโมชันอื่นได้หลังจากโปรโมชันนี้หมดอายุแล้วเท่านั้น
tr: Mevcut promosyonunuz süresi dolana kadar seçili kalır. Başka bir promosyonu ancak süresi dolduktan sonra seçebilirsiniz.
zh-Hans: 当前促销将在到期前一直保持选中。只有在它到期后，您才能选择其他促销。
zh-Hant: 目前的促銷在到期前會一直保持已選取狀態。只有在它到期後，您才能選擇其他促銷。
```

Do not change unrelated promotion translations.

---

# Part E — required focused tests

Modify `tests/unit/services/promotion.service.test.ts` so the old ARCH-010 switch rules are replaced by the ARCH-018 rules.

Required cases:

1. first valid selection creates one exact grant and one selection;
2. second same-campaign request before expiry throws `ACTIVE_PROMOTION_ALREADY_SELECTED` and does not update grant timestamps/count;
3. another campaign before expiry is blocked;
4. exhausted selected grant before expiry is blocked;
5. CLOSED selected campaign before expiry is blocked;
6. target-ineligible selected campaign before expiry is blocked;
7. selected campaign with `expiresAt <= now` permits replacement without waiting for pointer cleanup;
8. existing grant with **no current selection pointer** is reused without replenishing quantity;
9. exhausted historical grant with no current pointer remains exhausted when later selected/reopened; no new quantity is granted;
10. `getCurrentPromotionSelectionState()` returns `locked=true` for exhausted/CLOSED/target-ineligible selections while unexpired;
11. projection returns `locked=false` after expiry;
12. projection `spendable` retains ACTIVE/running/target/isUsableGrant semantics independently of `locked`;
13. history `currentlySelected=false` when the pointer is stale but the campaign is expired;
14. existing SERIALIZABLE retry tests remain passing.

Update/remove tests whose names assert that exhaustion, closure or target loss permits replacement.

Modify `promotion-route.test.ts` to prove source includes:

```text
getCurrentPromotionSelectionState
promotionSelection
useNavigation
useRef
submitLockRef
guardPromotionSubmit
disabled={selectionLocked || submissionInFlight || offer.currentlySelected}
moda-promotions-lock-notice
```

and no merchant/internal IDs are exposed.

Update `merchant-i18n.test.ts` only as needed to keep catalogue completeness/semantic locale assertions valid. Do not weaken `validateIcuCatalogue` coverage.

---

# Validation

Inspect `package.json` first, then run exactly the declared commands/capabilities:

```bash
npm run prisma:generate
npm run prisma:validate

npx vitest run \
  tests/unit/services/promotion.service.test.ts \
  tests/unit/routes/promotion-route.test.ts \
  tests/unit/merchant-i18n.test.ts

npm run typecheck
npm run build

npx eslint \
  app/services/promotions/promotion.service.ts \
  app/routes/app/promotions/route.tsx \
  tests/unit/services/promotion.service.test.ts \
  tests/unit/routes/promotion-route.test.ts \
  tests/unit/merchant-i18n.test.ts

npm test

git diff --check
```

If full-suite/typecheck/build has a documented unrelated baseline failure, record the exact baseline evidence. Any failure caused by an authorized changed file is blocking.

## Required source invariant search

Run:

```bash
rg -n "isUsableGrant\(currentGrant\)|campaignId !== campaignId|isTargetEligible\(currentGrant\.campaign" \
  app/services/promotions/promotion.service.ts
```

There must be no hit inside the current-selection lock predicate.

## Stop conditions

STOP and return to `moda_architect` if:

- the selection lock requires a Prisma schema/migration change;
- implementing the projection requires exposing internal grant/selection IDs;
- a safe post-expiry selection cannot be achieved without waiting for Background cleanup;
- the change would require modifying promotional recovery reservation priority/spendability;
- exact locale catalogue validation cannot be preserved within the authorized locale files.

Do not invent a new architecture.

## Completion protocol

Update the Completion Report with exact changed files, focused test counts, source-invariant result, build/typecheck/lint/full-suite result and implementation commit. Set task `status: review`, clear `executor`/`claimed_at`, push both task branches and STOP.

## Acceptance invariant

Holding all other state constant:

```text
selected campaign expiresAt > now  -> no promotion selection mutation is permitted
selected campaign expiresAt <= now -> stale pointer does not block a new eligible selection
```

Changing only exhaustion/status/target eligibility of the **selected** campaign before expiry must not release the selection lock.
