---
id: ARCH-016-SHOPIFY-001
architecture_id: ARCH-016
title: Add Shopify discount scope, webhook ingress and installation lifecycle sync triggers
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
- ARCH-016-DATABASE-001
- ARCH-016-SHARED-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-016-SHOPIFY-001

## Objective

Wire Shopify discount discovery into the existing app install/subscription/webhook lifecycle without doing catalogue reconciliation inside the HTTP lifecycle.

## Published Shared dependency

Before editing, read ARCH-016-SHARED-001 Completion Report and install/pin the exact published package version in:

```text
package.json
package-lock.json
```

Do not copy the queue payload locally.

## Authorized implementation surface

```text
shopify.app.moda-interact.toml
app/routes/webhooks/root/route.jsx
app/routes/webhooks/app/scopes-update/route.jsx
app/routes/webhooks/app/uninstalled/route.jsx
app/services/webhooks/shopify-webhook-ingress.service.ts
app/services/webhooks/shopify-webhook-metadata.ts
app/services/webhooks/shopify-webhook-queue.server.ts
app/services/shop/shop.service.ts
app/services/billing/billing.service.ts
app/routes/app/billing/callback/route.tsx
new app/services/discounts/* queue/lifecycle helpers as required
focused tests for those files
package.json
package-lock.json
```

Do not implement Shopify Admin `discountNodes` reconciliation here. That belongs to BACKGROUND-001.

## Shopify app configuration

Modify only canonical:

```text
shopify.app.moda-interact.toml
```

Add `read_discounts` to required scopes. Preserve all existing scopes.

Add the five app-specific topics to the existing `/webhooks` subscription:

```text
discounts/create
discounts/update
discounts/delete
discounts/redeemcode_added
discounts/redeemcode_removed
```

Do not add a second shop-specific webhook registration mechanism.

## Webhook ingress rule

Existing checkout/order ingress remains unchanged.

For the five discount topics:

1. authenticate using existing root `authenticate.webhook` path;
2. resolve durable shop identity using existing ingress conventions;
3. create canonical Shared discount-sync payload with reason `DISCOUNT_WEBHOOK`;
4. publish to `shopify-discount-sync` queue using Shared contract/helper;
5. use Shopify delivery ID for duplicate-safe job identity;
6. acknowledge only after durable BullMQ acceptance, matching existing webhook reliability behavior;
7. do not parse/store the discount payload as catalogue truth;
8. do not call Shopify Admin API synchronously.

Unknown/non-supported topics retain existing behavior.

## Initial subscription bootstrap

Do NOT sync discounts on bare app installation / `NO_CONTRACT`.

After an initial Free/Paid activation has been durably verified as:

```text
Shop.status = ACTIVE
ShopSettings.onboardingCompleted = true
Subscription.status = ACTIVE | TRIALING
```

publish one best-effort `SUBSCRIPTION_ACTIVATED` discount-sync job.

App-side hook points in current snapshot:

```text
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts::completeFreeActivation
paid activation/sync path already used by billing callback
```

Do not publish before the activation transaction commits.

A queue publication failure MUST NOT roll back a valid subscription activation. Log the failure and leave the durable catalogue `SYNC_REQUIRED` so Background reconciliation/next lifecycle trigger can repair it.

When publishing the job, atomically/boundedly ensure `ShopifyDiscountCatalogue` exists and is `SYNC_REQUIRED` unless shop is unavailable. This state write must happen after subscription success; do not make a Shopify API call.

## Scope-update bootstrap

Current file:

```text
app/routes/webhooks/app/scopes-update/route.jsx
```

continues to persist the Session scope string.

After persistence, when the updated durable session includes `read_discounts` AND the shop currently satisfies eligible subscription/install state, request a FULL sync with reason `SCOPES_UPDATED`.

If the scope is absent, mark catalogue `UNAVAILABLE` and do not publish a sync.

Repeated scope-update webhooks are idempotent; duplicate FULL sync requests are safe.

## Uninstall

Current uninstall ordering is:

```text
authenticate
shopService.markUninstalled
session delete
```

Preserve that ordering.

Extend the same durable uninstall transaction/service boundary so BEFORE session deletion:

```text
Shop.status = UNINSTALLED                 existing behavior
ShopifyDiscountCatalogue.status = UNAVAILABLE
activeSyncToken = null
unavailableAt = uninstall event time
all ShopifyDiscount rows for shop:
  isAvailable = false
  unavailableAt = uninstall event time when not already set
```

Do NOT delete ShopifyDiscount rows. Do NOT delete RecoveryOutreachAttempt/Conversation history.

Do not enqueue a sync from uninstall.

## Reinstall boundary

Do not add app-side logic that marks the catalogue CURRENT on reinstall. Existing background billing reconciliation is provider authority for restored Free/Paid subscription state; BACKGROUND-001 owns the `REINSTALL_RECONCILED` sync trigger.

## Catalogue eligibility helper

Create one repository-local helper used by activation/scope paths. It must require:

```text
Shop ACTIVE
onboardingCompleted true
Subscription ACTIVE | TRIALING
current durable Session scope includes read_discounts
```

Do not duplicate slightly different eligibility predicates in each route.

## Required tests

- canonical TOML retains existing scopes + `read_discounts`;
- canonical TOML includes exactly the five required discount topics at `/webhooks`;
- authenticated `discounts/create` enqueues canonical FULL sync trigger;
- all five topics route identically except topic field;
- duplicate delivery ID dedupes;
- discount webhook never calls Admin API synchronously;
- initial NO_CONTRACT install does not enqueue;
- verified Free activation enqueues after commit;
- verified Paid activation enqueues after commit;
- failed activation does not enqueue;
- missing `read_discounts` scope does not enqueue;
- scope-added event for eligible shop enqueues;
- scope removal marks catalogue unavailable;
- uninstall marks catalogue/discount rows unavailable before sessions are removed;
- uninstall retains discount/history rows;
- queue publication failure does not invalidate a successfully committed subscription activation.

## Validation

Inspect `package.json` and run declared equivalents of:

```text
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

Also parse/inspect `shopify.app.moda-interact.toml` using existing config validation if present.

## Stop conditions

STOP if:

- implementation requires `write_discounts` (ARCH-016 is read-only discovery);
- implementation starts using webhook payload as the persistent discount definition;
- implementation needs to call Shopify during uninstall after session/token cleanup;
- a second webhook subscription mechanism would be introduced instead of canonical TOML app-specific subscriptions;
- implementation attempts to define AI/CommerceAgent discount selection.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
