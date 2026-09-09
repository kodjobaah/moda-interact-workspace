---
id: ARCH-007-SHOPIFY-004
architecture_id: ARCH-007
title: Let merchants request repeatable recovery-credit packs
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: ready
priority: 66
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-007-SHOPIFY-002
  - ARCH-007-DATABASE-005
  - ARCH-007-SHARED-006
  - ARCH-007-ADMIN-005
enables:
  - ARCH-007-SYSTEM-TEST-004
created: 2026-09-08
updated: 2026-09-09
---

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
Ready for Review

### Files Changed
Implementation branch changes:
- `app/routes/app.billing.tsx`
- `app/services/billing/billing.service.ts`
- `tests/unit/services/billing.service.test.ts`
- `app/i18n/locales/da.json`
- `app/i18n/locales/de.json`
- `app/i18n/locales/en.json`
- `app/i18n/locales/es.json`
- `app/i18n/locales/fr.json`
- `app/i18n/locales/it.json`
- `app/i18n/locales/nl.json`
- `app/i18n/locales/pt-BR.json`
- `app/i18n/locales/pt-PT.json`

### Work Completed
Implemented repeatable recovery-credit pack requests using durable `RecoveryCreditPurchase` and pending `UsageEvent` records. Requests validate the server-generated UUID, reload current subscription/plan state, verify the configured Shopify pack meter, snapshot the current plan configuration, and do not grant credits or call Shopify billing/App Events directly. Duplicate purchase IDs return the existing purchase and different IDs support repeat purchases. The billing page displays the purchased-credit balance and only renders the Buy form when the mapped subscription, pack configuration, and Shopify meter verification are safe.

Added focused coverage for Free and paid mapped plans, idempotency, repeated purchases, client identity validation, and fail-closed meter verification. Completed translations were preserved in the nine locale catalogues already changed on the interrupted attempt.

### Validation Results
- `npm test -- --run tests/unit/services/billing.service.test.ts tests/unit/services/shopify-billing.provider.test.ts tests/unit/billing-ui.test.ts`: 30 passed.
- `npm test -- --run tests/unit/services/billing.service.test.ts tests/unit/services/shopify-billing.provider.test.ts tests/unit/billing-i18n.test.ts tests/unit/billing-ui.test.ts`: 30 passed; the existing catalogue-completeness test fails because eleven declared catalogues still lack the five new billing keys.
- `npm run typecheck`: repository baseline failures remain; the task-introduced nullable `recoveryCreditsPerPack` error was fixed. Remaining failures include pre-existing implicit-any and legacy route/test typing errors.
- `git diff --check`: passed.

### Deviations
Per developer instruction, translation work is paused. Do not delete the nine completed locale updates. The remaining eleven locale catalogues and the failing catalogue-completeness check require architect coordination before translation work continues.

### Assumptions
Shopify meter verification remains a read-only provider check outside the Prisma write transaction; no direct Shopify billing/App Events network call is made by the purchase transaction.

### Unresolved Issues
The following locales still need the five new billing keys: `cs`, `fi`, `ja`, `ko`, `nb`, `pl`, `sv`, `th`, `tr`, `zh-Hans`, and `zh-Hant`. The architect should assign or authorize completion of those translations and rerun the focused i18n test.

### Architectural Concerns
Translation completion is intentionally deferred and is the only task acceptance gap identified in this interrupted continuation.

### Git / VCS

Task branch: `task/ARCH-007-SHOPIFY-004`

Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-007-SHOPIFY-004
  parent branch: task/ARCH-007-SHOPIFY-004
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-007-SHOPIFY-004
  implementation branch: task/ARCH-007-SHOPIFY-004
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Implementation repository:
  repository: moda-interact
  commit: 06a963e
  remote branch: origin/task/ARCH-007-SHOPIFY-004
  pushed: yes

Parent workspace:
  task file: docs/decisions/shopify/ARCH-007/SHOPIFY-004-request-repeatable-recovery-credit-pack.md
  remote branch: origin/task/ARCH-007-SHOPIFY-004
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes

Attempt 1 establishes the correct overall Shopify App Pricing mechanism, but it
is not yet architect-acceptable. The interrupted translation work is no longer
an open design question: `moda_architect` has supplied completed translations
for the eleven remaining locale catalogues. Attempt 2 must integrate those
files unchanged unless a repository validation rule exposes a concrete ICU
problem.

Three implementation corrections are also required.

#### Correction 1 — use Shared's canonical Shopify usage idempotency key helper

Attempt 1 defines a local helper:

```ts
export function createShopifyUsageIdempotencyKey(
  shopId: string,
  usageEventId: string,
): string {
  return `shopify:${shopId}:${usageEventId}`.slice(0, 64);
}
```

This duplicates and weakens the architect-accepted Shared contract. Shared
already exports `createShopifyUsageIdempotencyKey` from
`@modainteract/moda-interact-shared/billing`; its bounded-key implementation
hashes overlength identities rather than truncating their distinguishing tail.

Attempt 2 must:

- delete the local helper;
- import `createShopifyUsageIdempotencyKey` from the accepted Shared billing
  contract;
- keep the task-required stable identity derived from the newly created
  UsageEvent id;
- add a regression proving the persisted `shopifyIdempotencyKey` equals the
  Shared helper result and is stable on replay.

Do not introduce a second idempotency-key algorithm.

#### Correction 2 — preserve replay idempotency and revalidate current plan state inside the write transaction

Attempt 1 loads the current subscription/plan, performs Shopify meter
verification, and only then enters the Prisma transaction. Inside the
transaction it checks for an existing purchase but creates the UsageEvent from
the earlier plan snapshot without re-reading current durable plan state.

That violates the deterministic purchase sequence in this task:

```text
transaction
  1. existing purchase -> return existing
  2. require current safe mapped plan/top-up config
  3. create UsageEvent
  4. create RecoveryCreditPurchase snapshot
```

Attempt 2 must keep provider network verification outside the transaction but
close both races:

1. perform an early durable lookup for `RecoveryCreditPurchase(id=purchaseId)`;
   if it exists for this shop, return it without requiring Shopify/provider
   availability again;
2. perform the current provider verification for a new purchase;
3. enter one Prisma transaction and repeat the existing-purchase check for
   concurrency safety;
4. re-read the current subscription + plan inside that transaction;
5. require ACTIVE/TRIALING, active plan, top-ups enabled, positive pack size,
   correct meter rules, and confirm that the in-transaction plan identity /
   handles / pack quantity still match the provider-verified facts;
6. if durable configuration changed between verification and write, fail closed
   and create neither UsageEvent nor purchase;
7. otherwise create the UsageEvent and RecoveryCreditPurchase atomically.

Do not make a Shopify network call while holding the Prisma transaction open.

Required regressions:

- replay of an already-created purchase succeeds even if the provider is now
  unavailable or current top-up configuration has subsequently changed;
- a plan/meter/pack-size change between provider verification and transaction
  re-read fails closed with zero new UsageEvents;
- concurrent/same-id replay still results in one purchase and one UsageEvent.

#### Correction 3 — purchased credit balance is durable entitlement state, not purchase-button state

The task separately requires:

```text
Show purchased recovery credits:
  grantedQuantity - committedQuantity - reservedQuantity

Show Buy button only when:
  safe mapped subscription
  + top-ups enabled
  + positive pack size
  + verified top-up meter
```

Attempt 1 renders the purchased-credit balance inside the same condition that
controls top-up purchase availability. This hides already-purchased durable
credits whenever a merchant changes to a plan with top-ups disabled or Shopify
meter verification is temporarily unavailable. Purchased credits persist
across cycles/plan changes and must remain visible independently of whether a
new pack can currently be purchased.

Attempt 2 must:

- render `billing.purchasedRecoveryCredits` for a safe mapped billing page
  independently of `recoveryCreditPackEnabled` / meter verification;
- keep pack-size description, Shopify meter explanation and Buy form behind the
  purchase-eligibility checks;
- keep the Buy form fail-closed exactly as today.

Add focused UI/source behavior coverage proving a non-zero purchased balance is
still presented when top-up purchasing is disabled or meter verification is
false.

#### Correction 4 — complete the required regression matrix

In addition to the corrections above, the task-required focused tests must
explicitly prove:

- top-up disabled -> no UsageEvent;
- configured pack meter missing/blank -> no UsageEvent;
- unmapped/unsafe subscription -> no UsageEvent;
- client-supplied pack size / plan id / meter / price fields are ignored because
  the action accepts only server-resolved shop identity plus intent/purchaseId;
- Shopify/provider verification occurs outside the Prisma write transaction;
- the request path does not mutate `PURCHASED_RECOVERY_CREDITS` or otherwise
  grant credits before Background activation;
- the created event remains quantity `1`, metric
  `RECOVERY_CREDIT_PACK_PURCHASE`, state `PENDING`, exact current mapped pack
  meter and current billingPeriodId when available.

Existing Free/paid creation and repeated-purchase tests may remain.

#### Correction 5 — integrate the architect-supplied eleven locale catalogues and strengthen i18n proof

The remaining locales are:

```text
cs
fi
ja
ko
nb
pl
sv
th
tr
zh-Hans
zh-Hant
```

The architect handoff supplies all five new keys in each catalogue:

```text
billing.purchasedRecoveryCredits
billing.recoveryCreditPackDescription
billing.recoveryCreditPackShopifyMeter
billing.buyRecoveryCreditPack
billing.recoveryCreditPurchasePending
```

The supplied translations preserve the exact ICU placeholder sets required by
the English source. Attempt 2 must apply the handoff and keep the nine existing
completed translations.

Extend `billing-i18n.test.ts` so it proves more than key presence:

- all five task keys exist in all 20 declared catalogues;
- each catalogue preserves the same placeholder set as English for each key;
- each new key resolves through the existing merchant ICU runtime with sample
  values without throwing;
- no task-introduced merchant-visible English literal bypasses the i18n path in
  `app.billing.tsx`.

Do not broaden this task into retranslating pre-existing unrelated billing keys.

### Reviewed Files

Implementation commit reviewed:

```text
06a963eb58b0c3104cbcc0f390974f3956c678e0
```

Primary implementation files:

- `app/routes/app.billing.tsx`
- `app/services/billing/billing.service.ts`
- `tests/unit/services/billing.service.test.ts`
- `tests/unit/billing-ui.test.ts`
- `tests/unit/billing-i18n.test.ts`
- nine completed locale catalogues from Attempt 1

Parent task report reviewed at:

```text
606c47a8ecdc4c2fe8c587bb0492008580ea9bf0
```

Cross-repository contracts checked:

- Shared canonical `createShopifyUsageIdempotencyKey`;
- DATABASE-005 `UsageEvent` / `RecoveryCreditPurchase` uniqueness and durable
  fields;
- accepted Background recovery-credit activation/publisher contracts.

### Validation Reviewed

Attempt 1 records 30 focused tests passing without the i18n completeness test.
The i18n-inclusive focused run fails only because the eleven catalogues were
missing the five new keys. `git diff --check` passed. The reported remaining
typecheck failures are repository baseline failures after the task-introduced
nullable pack-size error was corrected.

The architect independently validated the supplied eleven-locale handoff for:

- JSON syntax;
- presence of all five new keys across 20/20 locale catalogues when overlaid;
- exact ICU placeholder parity with English.

### Architecture Conformance

Changes required within this SAME task. The core App Pricing mechanism is
correct, but canonical idempotency-key use, transactional freshness/replay,
durable balance presentation, full regression evidence and all-locale i18n
completion must be corrected before acceptance.

### Follow-up

Return `ARCH-007-SHOPIFY-004` to `ready`.

Durable state:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next claim is **Attempt 2** on the same mirrored
`task/ARCH-007-SHOPIFY-004` branches/worktree.

Do not create an attempt-specific branch.

`ARCH-007-SYSTEM-TEST-004` remains Pending / manual-terminal-gated. Do not
auto-start it.
