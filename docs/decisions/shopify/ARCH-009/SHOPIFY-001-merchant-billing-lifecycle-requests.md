---
id: ARCH-009-SHOPIFY-001
architecture_id: ARCH-009
title: Add merchant plan-change, cancellation-request and pack-refund-request UX
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-09-10T12:35:00Z
attempt: 2
depends_on:
  - ARCH-009-DATABASE-001
  - ARCH-009-SHARED-001
  - ARCH-008-SHOPIFY-001
  - ARCH-007-SHOPIFY-002
enables:
  - ARCH-009-ADMIN-001
created: 2026-09-09
updated: 2026-09-10
---

# ARCH-009-SHOPIFY-001

## Objective

Merchant-safe:

```text
Change plan
Switch to Free
Request cancellation
Request full-pack refund
```

## Adopt

Exact Shared 0.9.0 and accepted ARCH-009 DB revision.

Registry availability was confirmed on 2026-09-10 for `@modainteract/moda-interact-shared@0.9.0`.
The executor must still resolve and verify exactly `0.9.0` during task preflight. If unavailable, STOP.

## Change plan / Switch to Free

Use existing Shopify-hosted pricing route.

Do not introduce:

```text
appSubscriptionCreate
billing.request
appPurchaseOneTimeCreate
```

Merchant chooses/approves plan in Shopify.

## Cancellation request

Merchant exposes only:

```text
Request cancellation at end of billing cycle
```

Form:

```text
intent = REQUEST_SUBSCRIPTION_CANCELLATION
requestId = server/loader UUID
```

Browser cannot submit mode/provider ID/plan.

Server reloads Shop+Subscription and requires:

```text
ACTIVE or TRIALING
providerSubscriptionId non-null
observedShopifyPlanHandle non-null
```

Create/replay key:

```text
subscription-cancel:<shopId>:<providerSubscriptionId>
```

Persist:

```text
source MERCHANT_UI
providerSubscriptionIdSnapshot
planHandleSnapshot
currentPeriodEndSnapshot
mode END_OF_CYCLE
status REQUESTED
```

Create exactly one:

```text
BILLING_CANCELLATION_REQUEST_RECEIVED
```

SYSTEM message.

No Partner call.

## Refund request

Bounded same-shop purchase list.

Refund action only for ACTIVE purchase.

Form:

```text
intent = REQUEST_RECOVERY_CREDIT_REFUND
refundRequestId = server/loader UUID
purchaseId
```

Ignore client:

```text
credits
price
plan
meter
billingPeriod
settlementMode
```

Reload purchase+UsageEvent.

Create/replay:

```text
recovery-credit-refund:<purchaseId>
```

Snapshots:

```text
originalUsageEventIdSnapshot
billingPeriodIdSnapshot
planHandleSnapshot
eventHandleSnapshot
creditsSnapshot
status REQUESTED
```

Create one:

```text
BILLING_REFUND_REQUEST_RECEIVED
```

No hold/decrement/correction/provider call.

## Purchased-credit display

Use Shared availability including refundingQuantity.

Display:

```text
Granted
Committed
Reserved
Pending refund
Available
```

## Support CTA

```text
BILLING_PLAN_CHANGE_ACTION_REQUIRED
-> /app/billing
-> Change plan
```

Unknown system code no action.

## i18n

All 20 merchant locales.

Required meanings:

```text
Change plan
Switch to Free
Request cancellation
Cancellation requested
Request refund
Refund requested
Pending refund
Full-pack refund only
Refund availability warning
```

Placeholder parity.

## Tests

1. paid plan does not mutate Free counter;
2. hosted Change plan;
3. hosted Switch to Free;
4. no forbidden create APIs;
5. cancellation always END_OF_CYCLE;
6. immediate mode cannot be supplied;
7. cancellation replay one row;
8. no provider call;
9. refund ignores client price/credits/meter;
10. cross-shop purchase rejected;
11. refund replay one row;
12. no hold/decrement on request;
13. availability subtracts refunding;
14. plan-change SYSTEM CTA exact;
15. all 20 locales resolve.

## Validation

```bash
npm test
npm run typecheck
npm run build
npm run prisma:validate
git diff --check
```

## Stop

Return review and STOP.

## Completion Report

### Status
In Progress — Attempt 2

### Files Changed

Implementation branch `task/ARCH-009-SHOPIFY-001` changes:

- `app/routes/app/billing/route.tsx`
- `app/services/billing/billing.service.ts`
- `app/i18n/locales/*.json` (20 merchant locales)
- `tests/unit/billing-i18n.test.ts`
- `package.json`
- `package-lock.json`

### Work Completed

- Pinned `@modainteract/moda-interact-shared` to exact `0.9.0`.
- Added Shopify-hosted billing navigation.
- Added durable merchant cancellation-request persistence.
- Added durable same-shop recovery-credit refund-request persistence.
- Added refund-aware purchased-credit availability calculation.
- Added merchant billing copy across the locale catalogues.
- Added translation-row creation for new lifecycle SYSTEM messages.

### Validation Results

Agent-reported:

- `npm test`: 207 passed, 1 skipped.
- focused billing tests: 43 passed.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- `npm run typecheck`: nonzero on reported pre-existing dashboard/test diagnostics; no touched billing-route/service diagnostics were reported.

### Git / VCS

Implementation repository:

- repository: `moda-interact`
- branch: `task/ARCH-009-SHOPIFY-001`
- commit: `5a22f51d8af6890f9c1f7a992715b774c55496d0`
- pushed: yes
- branch base: `c6790f099c4c115bcdb26eeda20d33a2872060ab`
- ahead of `main`: 1
- behind `main`: 0

Parent workspace:

- branch: `task/ARCH-009-SHOPIFY-001`
- claim commit: `feed089f94433be03e89a82af0a0083d5fe648cb`
- review handoff commit: `69f861b5907145e8a70f13c6f113b25d67da95b7`
- pushed: yes

Mandatory physical parent/implementation worktree paths and start-of-attempt synchronization evidence were not preserved in the Attempt 1 Completion Report. Attempt 2 must restore that evidence.

### Deviations

- Full TypeScript validation remains nonzero on reported unrelated baseline diagnostics.
- The Attempt 1 parent handoff accidentally overwrote the canonical `## Tests` section with Completion Report content and left the actual Completion Report stale.

### Assumptions

- `/app/billing/select` remains the accepted internal bridge to Shopify-hosted App Pricing.
- Shared `0.9.0` is available from npm.

### Unresolved Issues

See Architect Review.

### Architectural Concerns

See Architect Review.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 establishes much of the merchant lifecycle request plumbing, but it does not yet satisfy the authoritative SHOPIFY-001 contract.

#### 1. Refund purchase list is not bounded

The task explicitly requires a bounded same-shop purchase list.

Current code uses:

```ts
recoveryCreditPurchase.findMany({
  where: { shopId, status: "ACTIVE" },
  orderBy: { createdAt: "desc" },
  include: { usageEvent: true, refund: true },
})
```

with no `take`.

Attempt 2 must:

- introduce a fixed merchant refund-list bound of **20**;
- query only `shopId + ACTIVE`;
- use deterministic ordering:
  `createdAt DESC, id DESC`;
- keep the `usageEvent` and `refund` includes;
- add a focused regression proving the DB query is same-shop, ACTIVE-only, `take: 20`, and deterministically ordered.

Do not add client-side filtering as a substitute for the DB bound.

#### 2. Required merchant meanings are missing from the UI/i18n contract

The task requires all of these merchant-visible meanings:

```text
Change plan
Switch to Free
Request cancellation
Cancellation requested
Request refund
Refund requested
Pending refund
Full-pack refund only
Refund availability warning
```

Attempt 1 adds some new billing copy, but three required meanings are absent entirely:

```text
Switch to Free
Pending refund
Refund availability warning
```

The purchased-credit state already contains `refundingQuantity`, but the route does not display it.

Attempt 2 must:

- add a localized **Switch to Free** CTA for a paid merchant;
- route it to the same existing `/app/billing/select` Shopify-hosted pricing bridge;
- keep **Change plan** as a separate hosted-pricing action;
- visibly display the five purchased-credit values required by the task:
  Granted, Committed, Reserved, Pending refund, Available;
- ensure the displayed Available value remains the Shared `availablePurchasedRecoveryCredits(...)` result;
- add a localized refund-availability warning explaining that approval requires enough available purchased credits for the complete pack;
- correct the current `billing.fullPackRefundOnly` wording so it does **not** claim that a particular pack is "unused". ARCH-009 uses pooled purchased-credit capacity and deliberately does not invent per-pack credit provenance. Use semantics equivalent to:
  `Only complete recovery-credit packs can be refunded.`
- add the required keys/copy to all 20 merchant locale catalogues and preserve ICU placeholder parity.

Suggested stable keys:

```text
billing.switchToFree
billing.pendingRefund
billing.refundAvailabilityWarning
```

Existing locale fallback policy may be used where a maintained translation is unavailable, but every locale catalogue must contain the keys.

#### 3. Required plan-change SYSTEM CTA is absent

The authoritative contract requires:

```text
BILLING_PLAN_CHANGE_ACTION_REQUIRED
-> /app/billing
-> Change plan
```

The current `system-message-actions.ts` has no case for this ARCH-009 code, and its `labelKey` union cannot currently return `billing.changePlan`.

Attempt 2 must:

- add `billing.changePlan` to the allowed `MerchantSystemMessageAction.labelKey` union;
- map `BILLING_PLAN_CHANGE_ACTION_REQUIRED` exactly to:
  `{ href: "/app/billing", labelKey: "billing.changePlan" }`;
- preserve existing mappings;
- preserve unknown-code => `null`;
- add a focused exact regression.

#### 4. Translation dispatch occurs before transaction commit

`createBillingSystemMessage(...)` currently creates a durable translation row and immediately calls `dispatchTranslation(...)` while still inside the cancellation/refund database transaction.

That violates the existing merchant-support invariant: the queue hint is best-effort and the durable translation state must be committed before enqueue.

Attempt 2 must restructure the lifecycle request flow so:

1. request row + SYSTEM message + optional translation row are created atomically in the DB transaction;
2. the transaction returns the persisted request plus an optional `translationId`;
3. only **after `$transaction(...)` resolves successfully** may `dispatchTranslation(translationId)` run;
4. replay of an existing request does not create or dispatch a second SYSTEM message/translation;
5. queue failure remains best-effort and does not roll back a committed lifecycle request.

Add a focused ordering/idempotency regression.

#### 5. Cancellation/refund replay is not race-safe

Both new methods perform:

```text
find existing
then create
```

inside a transaction, but unlike the existing recovery-credit-pack path they do not recover from a `P2002` uniqueness race.

Two concurrent merchant submissions can therefore produce one durable row but one user-visible failure.

Attempt 2 must:

- preserve the existing unique `requestKey` identities;
- recover a `P2002` race by re-reading the winner outside the aborted transaction;
- for refunds, retain the same-shop check on replay;
- return the already-persisted request rather than surfacing a duplicate-request error;
- guarantee only the winning transaction creates the lifecycle SYSTEM message;
- add replay regressions that cover both ordinary replay and the uniqueness-race path.

Do not introduce a second request identity or additional persistence field.

#### 6. The required behavioural test matrix was not implemented

The authoritative task explicitly lists 15 required tests. The published implementation commit changes only `tests/unit/billing-i18n.test.ts`; it does not add tracked cancellation/refund/service/CTA behaviour tests.

Attempt 2 must add focused tracked regressions covering **all 15 authoritative test items**:

1. paid plan does not mutate Free counter;
2. hosted Change plan;
3. hosted Switch to Free;
4. no forbidden `appSubscriptionCreate`, `billing.request`, or `appPurchaseOneTimeCreate` plan-change implementation;
5. cancellation persists `END_OF_CYCLE`;
6. browser-supplied immediate mode cannot alter the persisted cancellation mode;
7. cancellation replay yields one row;
8. merchant cancellation makes no Partner/provider cancellation call;
9. refund ignores forged client price/credits/meter/billing-period/settlement values and snapshots DB truth;
10. cross-shop purchase is rejected;
11. refund replay yields one row;
12. refund request performs no counter hold/decrement and no correction/provider call;
13. merchant purchased-credit availability subtracts `refundingQuantity`;
14. `BILLING_PLAN_CHANGE_ACTION_REQUIRED` CTA is exact;
15. all 20 locale catalogues resolve the task-visible keys with placeholder parity.

Also add explicit coverage for the bounded refund list and committed-before-enqueue translation ordering from this Architect Review.

Tests must exercise the actual service/route/action contracts, not merely search for source strings where runtime behaviour can be tested.

#### 7. Parent task document / Completion Report was corrupted

The published parent handoff inserted report material into the canonical `## Tests` section and left the actual `## Completion Report` at `In Progress / None`.

This overlay restores the canonical test list and reconstructs the Attempt 1 report, but Attempt 2 must finish the workflow properly.

Attempt 2 Completion Report must record:

- exact files changed;
- work completed;
- all validation results;
- exact TypeScript baseline diagnostics if `npm run typecheck` remains nonzero, with evidence that no touched ARCH-009 billing file introduces a new diagnostic;
- physical canonical parent task worktree path;
- physical canonical implementation task worktree path;
- both branch names;
- start-of-attempt synchronization evidence;
- implementation commit;
- parent review-handoff commit;
- deviations/unresolved issues.

Do not overwrite task-definition sections when updating the Completion Report, and preserve this Architect Review unchanged until the next architect decision.

### Positive Findings To Preserve

The following implementation decisions are correct and should not regress:

- exact Shared dependency is pinned to `0.9.0`;
- hosted App Pricing remains the plan-change mechanism;
- no `appSubscriptionCreate`, `billing.request`, or `appPurchaseOneTimeCreate` plan creation path was introduced;
- cancellation form sends only intent + server-generated request UUID;
- server derives cancellation provider/plan identity from durable Subscription state;
- cancellation persists `MERCHANT_UI`, snapshot identity, `END_OF_CYCLE`, and `REQUESTED`;
- cancellation performs no Partner cancellation call;
- refund form sends only intent + server-generated refund UUID + purchase ID;
- refund server reloads purchase + UsageEvent and enforces same-shop + ACTIVE;
- refund snapshots durable UsageEvent/plan/meter/credits state;
- refund request performs no hold, decrement, negative UsageEvent, settlement selection, or provider call;
- Shared refund-aware availability is already used in `getMerchantBillingState`;
- lifecycle SYSTEM messages are persisted through the merchant support domain;
- all 20 locale files remain structurally present;
- build and Prisma validation were reported successful;
- implementation branch is one commit ahead of main and zero behind;
- no downstream ADMIN task was started.

### Validation Reviewed

Agent-reported Attempt 1:

```text
npm test:               207 passed, 1 skipped
focused billing tests:  43 passed
npm run build:          passed
npm run prisma:validate passed
git diff --check:       passed
npm run typecheck:      nonzero on reported unrelated baseline diagnostics
```

The supplied archive does not contain `node_modules`, so npm validation was not independently rerun in the architect container.

Architect source review confirmed:

- 20 merchant locale files exist;
- `billing.switchToFree` is absent from all 20;
- `billing.pendingRefund` is absent from all 20;
- `billing.refundAvailabilityWarning` is absent from all 20;
- no tracked behavioural test file other than `billing-i18n.test.ts` changed in the implementation commit;
- `system-message-actions.ts` does not implement the required ARCH-009 plan-change action;
- recovery-credit purchase lookup has no server-side bound;
- translation dispatch is currently invoked from inside the lifecycle transaction.

### Published Git Verification

- implementation branch tip:
  `5a22f51d8af6890f9c1f7a992715b774c55496d0`;
- implementation branch base:
  `c6790f099c4c115bcdb26eeda20d33a2872060ab`;
- implementation branch: one commit ahead of `main`, zero behind;
- parent claim commit:
  `feed089f94433be03e89a82af0a0083d5fe648cb`;
- parent review-handoff / branch-tip commit:
  `69f861b5907145e8a70f13c6f113b25d67da95b7`.

### Architecture Conformance

Changes required.

### Follow-up

Attempt 2 must remain on the SAME `ARCH-009-SHOPIFY-001` task and mirrored `task/ARCH-009-SHOPIFY-001` branches.

After corrections:

1. synchronize both canonical task worktrees;
2. implement only the corrections above;
3. run the authoritative 15-test matrix plus the new bounded-list, replay-race and post-commit-translation regressions;
4. rerun:
   - `npm test`;
   - focused billing tests;
   - `npm run typecheck`;
   - `npm run build`;
   - `npm run prisma:validate`;
   - `git diff --check`;
5. if typecheck remains nonzero only because of unchanged baseline files, record exact diagnostics and baseline evidence rather than changing unrelated code;
6. update the actual Completion Report without modifying task-specification sections;
7. set this same task to `review`;
8. STOP.

`ARCH-009-ADMIN-001` remains Pending until SHOPIFY-001 is architect-accepted Complete.

`ARCH-009-BACKGROUND-001` and `ARCH-009-BACKGROUND-002` are independent of this rework and may continue under their own Ready task gates.
