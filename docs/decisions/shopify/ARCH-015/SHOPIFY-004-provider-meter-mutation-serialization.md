---
id: ARCH-015-SHOPIFY-004
architecture_id: ARCH-015
title: Serialize recovery-credit meter mutations and harden merchant purchase/refund UI
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 85
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-015-SHARED-001
- ARCH-015-DATABASE-002
- ARCH-015-SHOPIFY-003
- ARCH-015-BACKGROUND-003
enables:
- ARCH-015-BACKGROUND-004
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-015-SHOPIFY-004

## Objective

Close the integration gaps found after all original ARCH-015 implementation tasks were accepted.

This task MUST make every merchant-originated monetary mutation of one Shopify recovery-credit meter obey one deterministic single-flight boundary:

```text
provider-meter key = (shopId, eventHandle)
```

For the same key, while any non-terminal purchase/refund mutation exists, no second purchase or refund admission may start. Different event handles remain independent.

This task also MUST:

1. prevent merchant refund reactivation once Background has linked an automatic correction `UsageEvent`;
2. make top-up availability per event handle instead of globally disabling every offer because one handle is busy;
3. stop presenting Shopify meter-unit price as "per conversation";
4. derive the displayed next meter-unit charge from the live Shopify tier model without assuming `tiers[0]` is authoritative;
5. preserve the existing asynchronous App Event publication/reconciliation architecture.

No Prisma schema change is authorized.

## Architecture invariant

After this task, the web application MUST enforce:

```text
same shop + same eventHandle:

REQUESTED purchase
OR live refund (REQUESTED | PROVIDER_ACTION_REQUIRED | NEEDS_ATTENTION)
    => meter is BUSY
    => no new purchase admission
    => no new refund admission for another purchase using that meter

same shop + different eventHandle
    => independent
```

The existing `billing.Subscription` row is the serialization primitive. Do NOT add:

- a lock table;
- a Prisma model;
- a Redis lock;
- a queue;
- a PostgreSQL advisory lock.

Purchase admission already locks this row. Refund admission MUST use the same row lock before its final busy checks/provider proof/mutation.

## Authorized implementation surface

Only the following production files are authorized unless a compile error proves one directly adjacent type/import file is required:

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/recovery-credit-purchase-management.service.ts
app/services/merchant-pricing/merchant-pricing.server.js
app/routes/app/billing/options/route.tsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/components/dashboard/RecoveryCreditPurchaseManager.jsx
app/i18n/locales/{cs,da,de,en,es,fi,fr,it,ja,ko,nb,nl,pl,pt-BR,pt-PT,sv,th,tr,zh-Hans,zh-Hant}.json

tests/unit/services/billing.service.test.ts
tests/unit/services/recovery-credit-purchase-management.service.test.ts
tests/unit/merchant-pricing-reader.test.js
tests/unit/billing-purchase-hub.test.tsx
tests/unit/recovery-credit-purchase-manager.test.tsx
tests/unit/billing-i18n.test.ts
```

Do NOT modify Background, Database, Shared or Admin in this task.

---

# Phase 1 — define one live provider-meter mutation predicate

## 1.1 Live refund statuses

In `app/services/billing/billing.service.ts`, import `RecoveryCreditRefundStatus` from `@prisma/client` and define exactly this immutable list near the other billing constants:

```ts
const LIVE_RECOVERY_CREDIT_REFUND_STATUSES = [
  RecoveryCreditRefundStatus.REQUESTED,
  RecoveryCreditRefundStatus.PROVIDER_ACTION_REQUIRED,
  RecoveryCreditRefundStatus.NEEDS_ATTENTION,
] as const;
```

`recovery-credit-purchase-management.service.ts` already has the equivalent `LIVE_REFUND_STATUSES`; retain it and use it as the refund-side source of truth.

Terminal `COMPLETED`, `REJECTED` and `CANCELLED` refunds MUST NOT block a meter.

## 1.2 Exact busy predicate

A provider meter is busy if EITHER query returns a row:

```ts
await transaction.recoveryCreditPurchase.findFirst({
  where: {
    shopId,
    status: RecoveryCreditPurchaseStatus.REQUESTED,
    shopifyEventHandleSnapshot: eventHandle,
  },
  orderBy: [{ createdAt: "asc" }, { id: "asc" }],
  select: { id: true },
});
```

or:

```ts
await transaction.recoveryCreditRefund.findFirst({
  where: {
    shopId,
    eventHandleSnapshot: eventHandle,
    status: { in: [...LIVE_RECOVERY_CREDIT_REFUND_STATUSES] },
  },
  orderBy: [{ createdAt: "asc" }, { id: "asc" }],
  select: {
    id: true,
    status: true,
    automaticCorrectionUsageEventId: true,
  },
});
```

Do NOT scope these queries by billing period, plan id, provider subscription id or purchase id. The serialization key is exactly `(shopId, eventHandle)`.

---

# Phase 2 — purchase admission must also see live refunds

File:

```text
app/services/billing/billing.service.ts
```

Function:

```text
requestRecoveryCreditPack(...)
```

The existing transaction already executes:

```sql
SELECT "id"
FROM "billing"."Subscription"
WHERE "shopId" = ...
FOR UPDATE
```

Keep that lock.

Immediately after the existing same-handle unresolved-purchase check and BEFORE creating the new `UsageEvent`, add the live-refund check for the selected `eventHandle`.

Required behavior:

```ts
const unresolvedRefund = await transaction.recoveryCreditRefund.findFirst({
  where: {
    shopId,
    eventHandleSnapshot: eventHandle,
    status: { in: [...LIVE_RECOVERY_CREDIT_REFUND_STATUSES] },
  },
  orderBy: [{ createdAt: "asc" }, { id: "asc" }],
  select: { id: true },
});

if (unresolvedRefund) {
  throw new Error(
    "Another billing change for this recovery-credit meter is already being processed.",
  );
}
```

Required ordering inside the locked transaction:

```text
Subscription FOR UPDATE
-> replay purchaseId check
-> same-handle REQUESTED purchase check
-> same-handle live-refund check
-> re-read local subscription/cycle invariants
-> create UsageEvent + RecoveryCreditPurchase
```

Do NOT weaken the existing second Shopify/ARCH-014 verification done before the transaction.

---

# Phase 3 — refund admission must use the same Subscription row lock

File:

```text
app/services/billing/recovery-credit-purchase-management.service.ts
```

Function:

```text
requestRefundWithRetry(...)
```

## 3.1 New application outcome

Add exactly:

```ts
| "METER_BUSY"
```

to `RefundOutcomeCode`.

Do not add a Prisma enum/status for this. It is an HTTP/application outcome only.

## 3.2 Lock location

After:

- exact purchase exists;
- purchase belongs to the authenticated shop;
- idempotent existing live refund for THIS purchase has been returned;
- purchase is still `ACTIVE`;
- `shopifyShopId` is nonblank;
- there is a positive unreserved balance;
- provider purchase value is strictly positive;

but BEFORE `isCurrentProviderContext(...)`, obtain the same per-shop `Subscription` row lock used by purchase admission:

```ts
if ("$queryRaw" in transaction && typeof transaction.$queryRaw === "function") {
  await transaction.$queryRaw(Prisma.sql`
    SELECT "id"
    FROM "billing"."Subscription"
    WHERE "shopId" = ${input.shopId}
    FOR UPDATE
  `);
}
```

Do not create a second lock mechanism.

## 3.3 Re-check meter busy state while lock is held

Use the target purchase's immutable meter:

```ts
const eventHandle = purchase.shopifyEventHandleSnapshot;
```

Then execute BOTH checks under the lock:

```ts
const pendingPurchase = await transaction.recoveryCreditPurchase.findFirst({
  where: {
    shopId: input.shopId,
    status: RecoveryCreditPurchaseStatus.REQUESTED,
    shopifyEventHandleSnapshot: eventHandle,
  },
  orderBy: [{ createdAt: "asc" }, { id: "asc" }],
  select: { id: true },
});

const competingRefund = await transaction.recoveryCreditRefund.findFirst({
  where: {
    shopId: input.shopId,
    eventHandleSnapshot: eventHandle,
    status: { in: [...LIVE_REFUND_STATUSES] },
  },
  orderBy: [{ createdAt: "asc" }, { id: "asc" }],
  select: { id: true, purchaseId: true },
});
```

The current purchase's own idempotent live refund has already returned before this point. Therefore any `competingRefund` here is a competing meter mutation.

If either row exists, return exactly:

```ts
{
  purchaseId: input.purchaseId,
  code: "METER_BUSY",
  currentAmount: purchase.currentAmount,
  reservedAmount: purchase.reservedAmount,
  availableAmount,
}
```

with NO mutation.

Then continue with fresh current-provider-context proof while still holding the transaction/row lock, followed by aggregate/refund/purchase updates.

### Required concurrency result

If purchase admission and refund admission race for the same `(shopId,eventHandle)`:

- whichever acquires `Subscription FOR UPDATE` first may create its mutation;
- the waiter MUST re-check the busy predicate after acquiring the lock;
- the waiter MUST fail/return busy without creating its mutation.

Different event handles MUST NOT block one another.

---

# Phase 4 — batch refunds must serialize same-handle selections

Do not add special client grouping logic.

`requestRefundBatch()` already processes purchase ids sequentially. Keep that behavior.

Required result for two ACTIVE purchases using the same event handle in one batch:

```text
first eligible purchase  -> REQUESTED
second same-handle       -> METER_BUSY
```

Two purchases with different event handles may both become `REQUESTED`.

---

# Phase 5 — automatic correction permanently closes merchant reactivation

## 5.1 Read model

Extend the local refund shapes in `recovery-credit-purchase-management.service.ts`:

```ts
automaticCorrectionUsageEventId: string | null;
```

Add it to the Prisma refund select in `listPurchaseHistory()` and return it from `refundSummary()`.

`RefundSummary` MUST therefore contain:

```ts
automaticCorrectionUsageEventId: string | null;
```

## 5.2 Server precondition

In `reactivateRefund(...)`, the initial eligibility check MUST include:

```ts
refund.automaticCorrectionUsageEventId !== null
```

as a blocking condition.

Equivalent required predicate:

```ts
if (
  purchase.status !== RecoveryCreditPurchaseStatus.WITHDRAWN ||
  !refund ||
  refund.status !== RecoveryCreditRefundStatus.REQUESTED ||
  refund.automaticCorrectionUsageEventId !== null ||
  refund.providerReference ||
  refund.providerActionKind ||
  refund.providerConfirmedAt
) {
  return { purchaseId: input.purchaseId, code: "REACTIVATION_NOT_AVAILABLE" };
}
```

## 5.3 CAS protection — mandatory

Both `recoveryCreditRefund.updateMany(...)` CAS predicates in `reactivateRefund()` MUST include:

```ts
automaticCorrectionUsageEventId: null,
```

This applies to:

1. the zero-credit `COMPLETED_NO_CREDITS` branch;
2. the normal `MERCHANT_REACTIVATED` branch.

This is mandatory even though the initial read checks the field. It closes this race:

```text
merchant reads REQUESTED / no correction
Background links correction
merchant CAS executes
```

The CAS MUST lose, the transaction MUST retry, the retry MUST observe the correction link and return `REACTIVATION_NOT_AVAILABLE`.

## 5.4 Merchant UI

In `RecoveryCreditPurchaseManager.jsx`, change:

```js
const canReactivate =
  purchase.status === "WITHDRAWN" && refund?.status === "REQUESTED";
```

to exactly:

```js
const canReactivate =
  purchase.status === "WITHDRAWN" &&
  refund?.status === "REQUESTED" &&
  refund.automaticCorrectionUsageEventId == null;
```

`providerActionStarted` MUST also treat a non-null automatic correction id as settlement having started:

```js
const providerActionStarted =
  purchase.status === "WITHDRAWN" &&
  refund &&
  (refund.status !== "REQUESTED" ||
    refund.automaticCorrectionUsageEventId != null);
```

Reuse the existing `billingPurchases.reactivationBlocked` copy. Do not add a new reactivation string.

---

# Phase 6 — make top-up availability per meter, not global

Current defect:

```text
latest purchase REQUESTED on handle A
=> global recoveryCreditPackPurchaseEligible = false
=> handles B/C are incorrectly disabled
```

Remove the existing global line:

```ts
if (latestPurchase?.status === "REQUESTED") {
  recoveryCreditPackPurchaseEligible = false;
}
```

## 6.1 Offer shape

Extend `RecoveryCreditOffer` in `billing.types.ts` with:

```ts
providerNextUnitCost: {
  amount: string;
  currency: string;
} | null;

purchaseEligible: boolean;
blockReason: "PURCHASE_PENDING" | "REFUND_PENDING" | null;
pendingPurchase: {
  id: string;
  usageReportState: string;
} | null;
```

In `resolveCurrentRecoveryCreditOffers(...)`, use neutral defaults because that resolver has no database mutation-state context:

```js
purchaseEligible: true,
blockReason: null,
pendingPurchase: null,
```

The billing service MUST overwrite these values using database state before returning merchant billing data.

## 6.2 Read all busy handles

After the offers are resolved and after the global subscription/cycle eligibility has been calculated, freeze that non-meter-specific result before applying per-handle busy state:

```ts
const globalPurchaseEligibility = recoveryCreditPackPurchaseEligible;
const offerHandles = recoveryCreditOffers.map((offer) => offer.eventHandle);
```

`globalPurchaseEligibility` means only that the shop/subscription/current cycle/provider verification permit top-ups in principle. It MUST NOT include any single pending purchase/refund.

Read:

```ts
const pendingPurchases = offerHandles.length
  ? await this.database.recoveryCreditPurchase.findMany({
      where: {
        shopId,
        status: RecoveryCreditPurchaseStatus.REQUESTED,
        shopifyEventHandleSnapshot: { in: offerHandles },
      },
      orderBy: [{ createdAt: "asc" }, { id: "asc" }],
      include: { usageEvent: true },
    })
  : [];
```

and:

```ts
const liveRefunds = offerHandles.length
  ? await this.database.recoveryCreditRefund.findMany({
      where: {
        shopId,
        eventHandleSnapshot: { in: offerHandles },
        status: { in: [...LIVE_RECOVERY_CREDIT_REFUND_STATUSES] },
      },
      orderBy: [{ createdAt: "asc" }, { id: "asc" }],
      select: {
        id: true,
        eventHandleSnapshot: true,
        status: true,
      },
    })
  : [];
```

Build first-row-per-handle maps. Do not use the global latest purchase to decide per-handle eligibility.

For each offer:

```ts
const pendingPurchase = pendingPurchaseByHandle.get(offer.eventHandle) ?? null;
const liveRefund = liveRefundByHandle.get(offer.eventHandle) ?? null;

return {
  ...offer,
  purchaseEligible:
    globalPurchaseEligibility && !pendingPurchase && !liveRefund,
  blockReason: pendingPurchase
    ? "PURCHASE_PENDING"
    : liveRefund
      ? "REFUND_PENDING"
      : null,
  pendingPurchase: pendingPurchase
    ? {
        id: pendingPurchase.id,
        usageReportState:
          pendingPurchase.usageEvent?.shopifyReportState ?? "UNKNOWN",
      }
    : null,
};
```

After annotation, set the existing top-level value to:

```ts
recoveryCreditPackPurchaseEligible = recoveryCreditOffers.some(
  (offer) => offer.purchaseEligible,
);
```

The top-level value now means "at least one offer can currently be purchased".

## 6.3 Route/UI

Keep the route's existing global commercial/lifecycle gating.

In `TopUpPurchasePanel.jsx`, each Buy button MUST use both levels:

```jsx
disabled={!topUpState.purchaseEligible || !offer.purchaseEligible}
```

Per-card purchase reporting messages MUST use `offer.pendingPurchase`, not `topUpState.latestPurchase`.

For `offer.blockReason === "REFUND_PENDING"`, render:

```js
i18n.t("billingCommerce.topup.meterBusy")
```

The existing bottom-of-panel latest-purchase summary may remain; it is informational only and MUST NOT control all offer buttons.

---

# Phase 7 — correct Shopify price presentation

Current code is forbidden after this task:

```js
const tier = offer.providerPrice?.tiers?.[0];
const providerAmount = tier?.amountPerUnit ?? tier?.amount;
...
i18n.t("billingCommerce.perConversation")
```

Reasons:

- a Shopify App Event meter unit is one top-up purchase unit, not one recovery conversation;
- `creditsGrantedPerUnit` may grant many conversations;
- first-tier pricing is not necessarily the next unit's actual charge under VOLUME/GRADUATED pricing.

## 7.1 Deterministic next-unit cost helper

In `merchant-pricing.server.js`, add:

```js
import { Prisma } from "@prisma/client";
```

and implement the following behavior exactly (names may vary only if required by existing lint conventions):

```js
function parseProviderDecimal(value) {
  if (value === null || value === undefined) return null;
  try {
    const decimal = new Prisma.Decimal(value);
    return decimal.isFinite() ? decimal : null;
  } catch {
    return null;
  }
}

function nonNegativeDecimal(value) {
  return value.lt(0) ? new Prisma.Decimal(0) : value;
}

function calculateProviderUsageCost(price, quantity) {
  if (
    !price ||
    price.kind !== "TIERED" ||
    !quantity?.isFinite?.() ||
    quantity.lt(0) ||
    !Array.isArray(price.tiers) ||
    price.tiers.length === 0
  ) return null;

  const tiers = price.tiers.map((tier) => ({
    upTo: tier.upTo === null ? null : new Prisma.Decimal(tier.upTo),
    unit: parseProviderDecimal(tier.amountPerUnit),
    flat: parseProviderDecimal(tier.amount),
  }));

  if (tiers.some((tier) => !tier.unit || !tier.flat || tier.unit.lt(0) || tier.flat.lt(0))) {
    return null;
  }

  const mode = String(price.tiersMode ?? "").toUpperCase();

  if (mode === "VOLUME") {
    const tier = tiers.find(
      (candidate) => candidate.upTo === null || quantity.lte(candidate.upTo),
    );
    return tier ? tier.flat.plus(quantity.mul(tier.unit)) : null;
  }

  if (mode !== "GRADUATED") return null;

  let total = new Prisma.Decimal(0);
  let lower = new Prisma.Decimal(0);
  for (const tier of tiers) {
    const upper = tier.upTo ?? quantity;
    const segment = nonNegativeDecimal(
      quantity.lt(upper) ? quantity.minus(lower) : upper.minus(lower),
    );
    total = total.plus(segment.mul(tier.unit).plus(tier.flat));
    if (quantity.lte(upper)) return total;
    lower = upper;
  }
  return null;
}

function resolveNextProviderUnitCost(providerItem) {
  const currency = providerItem?.price?.currency;
  const quantity = parseProviderDecimal(providerItem?.usage?.quantity);
  if (!currency || !quantity || quantity.lt(0)) return null;

  const before = calculateProviderUsageCost(providerItem.price, quantity);
  const after = calculateProviderUsageCost(
    providerItem.price,
    quantity.plus(1),
  );
  if (!before || !after) return null;

  const delta = after.minus(before);
  if (!delta.isFinite() || delta.lt(0)) return null;

  return {
    amount: delta.toString(),
    currency,
  };
}
```

This is presentation evidence only. Do NOT use it as purchase/refund settlement authority. Existing provider quantity/cost reconciliation remains authoritative.

## 7.2 Resolver output

Each matched offer returned from `resolveCurrentRecoveryCreditOffers(...)` MUST include:

```js
providerNextUnitCost: resolveNextProviderUnitCost(providerItem),
purchaseEligible: true,
blockReason: null,
pendingPurchase: null,
```

## 7.3 UI

Replace first-tier/per-conversation rendering with:

```jsx
const providerPrice = offer.providerNextUnitCost
  ? i18n.formatMoney(
      offer.providerNextUnitCost.amount,
      offer.providerNextUnitCost.currency,
    )
  : null;
```

and:

```jsx
{providerPrice ? <p>{providerPrice}</p> : null}
```

Do NOT append `billingCommerce.perConversation` or any other per-conversation wording.

If exact next-unit cost cannot be deterministically derived, show no numeric top-up price in the card. Do not fall back to `tiers[0]`.

---

# Phase 8 — exact localization values

Add the two architect-supplied keys from:

```text
docs/decisions/shopify/ARCH-015/SHOPIFY-localization-matrix-004.json
```

to all 20 existing merchant locale files.

Keys:

```text
billingCommerce.topup.meterBusy
billingPurchases.outcome.METER_BUSY
```

Rules:

- copy values verbatim;
- do not translate/paraphrase;
- do not add/remove locales;
- do not alter unrelated translations;
- `billing-i18n.test.ts` must continue proving catalogue parity.

---

# Required tests — exact scenarios

## `tests/unit/services/billing.service.test.ts`

Add deterministic cases proving:

1. existing REQUESTED purchase on handle A blocks new purchase handle A;
2. live `REQUESTED` refund on handle A blocks new purchase handle A;
3. live `PROVIDER_ACTION_REQUIRED` refund on handle A blocks new purchase handle A;
4. live `NEEDS_ATTENTION` refund on handle A blocks new purchase handle A;
5. terminal refund on handle A does not block;
6. live refund on handle A does not block purchase handle B;
7. per-offer read model: pending purchase A => A false/B true;
8. per-offer read model: live refund A => A false/B true;
9. top-level `purchaseEligible` is true when at least one offer remains eligible and false when none do.

The concurrency-style unit setup MUST prove the busy check occurs after the `Subscription FOR UPDATE` call in the transaction mock.

## `tests/unit/services/recovery-credit-purchase-management.service.test.ts`

Add:

1. refund admission calls the Subscription `FOR UPDATE` lock;
2. REQUESTED purchase same handle => `METER_BUSY`, no refund/purchase/counter mutation;
3. live refund on another purchase same handle => `METER_BUSY`, no mutation;
4. different handle mutation does not block;
5. batch [A1, A2] same handle => first REQUESTED, second METER_BUSY;
6. batch [A, B] different handles => both REQUESTED;
7. reactivation with `automaticCorrectionUsageEventId != null` => `REACTIVATION_NOT_AVAILABLE`;
8. simulated race: initial refund read has null correction id, CAS update count=0 because Background linked correction, retry sees non-null id and returns `REACTIVATION_NOT_AVAILABLE`;
9. both reactivation CAS predicates contain `automaticCorrectionUsageEventId: null`.

## `tests/unit/merchant-pricing-reader.test.js`

Add exact next-unit cost cases:

1. VOLUME single tier: quantity 3, unit 10, flat 0 => next unit cost 10;
2. GRADUATED single tier: quantity 3, unit 10, flat 0 => next unit cost 10;
3. graduated threshold crossing uses full cost delta, not first-tier price;
4. missing quantity => `providerNextUnitCost === null`;
5. malformed/unsupported pricing => null, no throw;
6. negative derived delta => null, never display a fabricated negative price.

## UI tests

`billing-purchase-hub.test.tsx` / directly relevant TopUp test:

- one busy handle disables only its button;
- refund-busy handle renders `billingCommerce.topup.meterBusy`;
- pending-purchase retry/attention copy is attached only to that offer;
- displayed price is `providerNextUnitCost`;
- rendered markup contains no `per conversation` price suffix.

`recovery-credit-purchase-manager.test.tsx`:

- non-null `automaticCorrectionUsageEventId` hides Reactivate and shows existing blocked copy;
- `METER_BUSY` result resolves through the localized outcome key.

`billing-i18n.test.ts`:

- all 20 catalogues contain both new keys;
- no fallback/missing-key failure.

---

# Required validation commands

From `moda-interact`:

```bash
npm test -- --run \
  tests/unit/services/billing.service.test.ts \
  tests/unit/services/recovery-credit-purchase-management.service.test.ts \
  tests/unit/merchant-pricing-reader.test.js \
  tests/unit/billing-purchase-hub.test.tsx \
  tests/unit/recovery-credit-purchase-manager.test.tsx \
  tests/unit/billing-i18n.test.ts

npm run prisma:validate
npm run typecheck
npm run build
git diff --check
```

Also run the full application test suite:

```bash
npm test
```

If repository-wide lint has unrelated baseline failures, run ESLint directly on every touched JS/TS/TSX/JSX file and record both the focused result and unchanged baseline evidence.

---

# Forbidden implementations

Do NOT:

- add a database model/column/index for this correction;
- add Redis locking;
- add advisory locking;
- serialize different event handles;
- block by plan/billing period instead of event handle;
- remove merchant batch refund support;
- let reactivation cancel a refund with a linked automatic correction;
- use `tiers[0]` as the displayed provider price;
- label a meter-unit/top-up price "per conversation";
- trust client-provided price, credits, provider quantity or meter state;
- call Shopify App Events directly from web routes.

# Stop conditions

STOP and return to `moda_architect` without inventing architecture if:

- the existing `Subscription` row cannot be used as the common purchase/refund admission lock;
- a schema change appears necessary;
- a third monetary mutation path exists that bypasses both corrected admission services;
- Shopify price data cannot be interpreted using the already-accepted VOLUME/GRADUATED semantics used by Background;
- tests require weakening the `(shopId,eventHandle)` single-flight invariant.

# Completion protocol

1. Update this task's Completion Report with exact files/commits/test counts.
2. Set `status: review`.
3. Increment `attempt` according to launcher protocol.
4. Clear `executor`/`claimed_at`.
5. Return to `moda_architect`.
6. STOP. Do not start BACKGROUND-004.
