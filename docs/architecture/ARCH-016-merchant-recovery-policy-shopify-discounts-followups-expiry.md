---
id: ARCH-016
title: Merchant recovery policy, Shopify discount catalogue, follow-up outreach and recovery expiry
status: in_progress
coordinator: moda_architect
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-016: Merchant recovery policy, Shopify discount catalogue, follow-up outreach and recovery expiry

## Purpose

Introduce one coherent merchant recovery-policy architecture that:

- exposes the existing recovery-start delay to merchants;
- lets Free and Paid merchants choose no recovery offer, one fixed Shopify discount, or `AI_BEST_APPLICABLE` as configuration state;
- synchronises the merchant's Shopify discount catalogue only after an eligible Free/Paid subscription is verified;
- maintains that catalogue from Shopify discount webhooks while the app is installed;
- makes uninstall/reinstall/scope-change lifecycle explicit;
- allows one configurable no-response follow-up;
- consumes one recovery credit for each proactive outbound recovery outreach attempt, not for ordinary customer/agent continuation messages;
- preserves one `Conversation` for the lifetime of one `CheckoutRecovery` generation;
- expires stale `CheckoutRecovery` generations after an admin-controlled inactivity lifetime;
- permits a later checkout update after `EXPIRED` to pass through the normal pending-abandonment delay and create a new recovery generation;
- gives platform admins visibility into merchant recovery policy and an explicit override mechanism.

## Current implementation facts

The uploaded 2026-09-16 snapshot establishes these starting invariants:

```text
ShopSettings.recoveryDelayMinutes Int @default(30)

CheckoutRecovery
  @@unique([shopId, checkoutToken])

Conversation
  checkoutRecoveryId String?
  @@unique([checkoutRecoveryId])
```

`moda-interact-background/src/services/checkout-recovery.service.ts` currently:

- creates/materialises one recovery for a shop + checkout token;
- refuses to reopen `COMPLETED`, `EXPIRED` or `CANCELLED` recovery rows;
- refreshes active recovery basket state on checkout updates;
- bills the initial recovery by `recoveryId`;
- obtains/creates exactly one recovery `Conversation`;
- sends the proactive recovery template through `OutboundWhatsAppAdmissionService`.

`Conversation` is therefore already the durable WhatsApp thread and ordering/history boundary. ARCH-016 MUST preserve that responsibility.

## Terminology boundary

ARCH-010 promotion entities are Moda recovery-credit promotion campaigns. They are NOT Shopify merchant discounts.

ARCH-016 MUST NOT reuse or reinterpret:

```text
PromotionCampaign
PromotionalCreditGrant
MerchantPromotionSelection
/app/promotions
```

for Shopify discounts.

Use the terms:

```text
ShopifyDiscount               provider discount projection
RecoveryOfferMode             merchant recovery-offer configuration
RecoveryOutreachAttempt       one proactive chargeable recovery outreach
```

## Merchant recovery policy

The merchant-owned settings are stored on the existing `ShopSettings` row.

Canonical settings:

```text
recoveryDelayMinutes
recoveryOfferMode
fixedShopifyDiscountId        nullable; required only for FIXED
followUpEnabled
followUpDelayMinutes          nullable; required only when enabled
```

Canonical offer modes:

```text
NONE
FIXED
AI_BEST_APPLICABLE
```

Rules:

```text
NONE
  fixedShopifyDiscountId = null

FIXED
  fixedShopifyDiscountId != null
  referenced discount belongs to the same shop
  catalogue is CURRENT
  discount is currently selectable

AI_BEST_APPLICABLE
  fixedShopifyDiscountId = null
```

The settings apply to Free and Paid subscribed merchants. They are not a paid-only entitlement.

## CommerceAgent / AI boundary

`AI_BEST_APPLICABLE` is configuration state only in ARCH-016.

ARCH-016 MUST NOT implement:

- LLM calls for discount selection;
- ranking discounts;
- deciding which discount is "best";
- basket-to-discount AI eligibility reasoning;
- CommerceAgent tools or prompts for discount selection;
- AI fallback ranking;
- AI-generated codes or discounts.

A later CommerceAgent architecture owns those semantics.

ARCH-016 persists/exposes the merchant's choice so that future CommerceAgent work has an authoritative configuration contract.

For `FIXED`, ARCH-016 snapshots the chosen Shopify discount on the outreach attempt. Do not invent a new WhatsApp template-variable convention in this architecture. The current `WhatsAppTemplateVariant` model contains no parameter contract. Customer-facing template composition beyond the existing approved-template path is not authorised unless the existing template path already has an explicit compatible contract. The implementation MUST NOT guess Meta template variable positions.

## Shopify discount catalogue lifecycle

Shopify is provider authority for the discount catalogue.

The canonical lifecycle is:

```text
APP INSTALLED
    -> Shop ACTIVE / Subscription NO_CONTRACT
    -> do not bootstrap discounts

verified Free or Paid subscription
Subscription ACTIVE or TRIALING
ShopSettings.onboardingCompleted = true
    -> request FULL discount sync

while installed + eligible
    discounts/create
    discounts/update
    discounts/delete
    discounts/redeemcode_added
    discounts/redeemcode_removed
      -> request FULL reconciliation

APP UNINSTALLED
    -> existing Shop UNINSTALLED lifecycle
    -> catalogue UNAVAILABLE
    -> all provider discounts unavailable for new recovery selection
    -> retain rows/history
    -> no Shopify discount API call after access is gone

APP REINSTALLED
    -> existing reinstall billing reconciliation
    -> if NO_CONTRACT: catalogue remains UNAVAILABLE
    -> if eligible ACTIVE/TRIALING subscription restored:
         request FULL authoritative reconciliation
    -> old pre-uninstall catalogue is never trusted as current
```

The canonical Shopify app config is:

```text
moda-interact/shopify.app.moda-interact.toml
```

Add required scope:

```text
read_discounts
```

Add app-specific subscriptions to `/webhooks`:

```text
discounts/create
discounts/update
discounts/delete
discounts/redeemcode_added
discounts/redeemcode_removed
```

Shopify 2026-07 `discountNodes` is the provider read path. Pagination is mandatory.

Webhook payloads are synchronization triggers, not the durable catalogue definition. Duplicate/out-of-order deliveries MUST remain harmless.

## Catalogue state and concurrency

Each shop has exactly one durable catalogue state record.

Canonical status set:

```text
UNAVAILABLE
SYNC_REQUIRED
SYNCING
CURRENT
ERROR
```

A full sync uses a monotonic `syncGeneration` plus an opaque `activeSyncToken` fence.

```text
request sync
  -> catalogue status SYNC_REQUIRED

worker claims
  -> increment syncGeneration
  -> set activeSyncToken
  -> status SYNCING

fetch every discountNodes page outside a long DB transaction

final commit only if activeSyncToken still matches
  -> upsert every observed ShopifyDiscount
  -> mark rows not seen in this generation unavailable
  -> status CURRENT
  -> clear token/error
```

A superseded/older worker MUST NOT overwrite a newer generation.

Uninstall invalidation takes precedence over in-flight sync finalization: a final sync commit MUST recheck shop install/subscription eligibility and token authority before making the catalogue CURRENT.

## ShopifyDiscount projection

Store all provider discounts returned by `discountNodes`, including supported native and app/function-backed types. Preserve enough normalized display/provider state for merchant selection and future architecture, plus the bounded provider snapshot required for future interpretation.

At minimum persist:

```text
shopifyDiscountNodeId
discountType               GraphQL __typename
method                     AUTOMATIC | CODE
providerStatus
title
summary
startsAt
endsAt
codeCount                  nullable
singleRedeemCode           nullable; set only when exactly one code is provable
providerSnapshot           JSON
isAvailable
lastSeenSyncGeneration
lastSyncedAt
unavailableAt
```

The merchant page may display every currently running discount. `FIXED` selection is allowed only when the record is current, belongs to the shop and is structurally usable without guessing. In v1:

```text
AUTOMATIC provider discount
  -> fixedSelectable = true

CODE provider discount with exactly one provable redeem code
  -> fixedSelectable = true

CODE provider discount with zero/multiple/unknown codes
APP/Function-backed discount whose customer-facing redemption cannot be represented deterministically
  -> display in catalogue
  -> fixedSelectable = false
```

Do not infer a redeem code from a discount title.

"Currently running" requires:

```text
catalogue CURRENT
isAvailable = true
providerStatus = ACTIVE
startsAt <= now when startsAt is present
endsAt > now when endsAt is present
```

## Effective policy and admin override

Merchant settings remain merchant-owned. Platform admin override is a separate durable row.

Use one complete override snapshot, not field-by-field nullable precedence.

```text
active unexpired ShopRecoveryPolicyOverride exists
      -> effective policy = override snapshot
otherwise
      -> effective policy = ShopSettings
```

Admin override contains:

```text
recoveryDelayMinutes
recoveryOfferMode
fixedShopifyDiscountId
followUpEnabled
followUpDelayMinutes
reason
expiresAt
updatedByPlatformAdminId
```

Every create/update/clear is also written to a dedicated durable recovery-policy override audit event containing shop, actor, action, reason and before/after JSON. Clearing an override MUST NOT erase its audit history.

Merchant UI MUST show when an admin override controls the effective policy. Merchant may still edit underlying merchant values; those values become effective only after override removal/expiry.

## RecoveryOutreachAttempt

One `CheckoutRecovery` generation owns zero or more `RecoveryOutreachAttempt` rows.

One attempt represents exactly one proactive outbound recovery outreach and one recovery-credit admission.

Canonical triggers:

```text
INITIAL
NO_RESPONSE_FOLLOW_UP
```

Canonical statuses:

```text
PENDING
WAITING_FOR_RESPONSE
ENGAGED
NO_RESPONSE
CAPACITY_BLOCKED
CANCELLED
FAILED
```

Required invariant:

```text
@@unique([checkoutRecoveryId, sequence])
```

Sequence starts at 1.

Attempt #1 is the initial proactive recovery message. The configured no-response follow-up, if it actually sends, is attempt #2.

ARCH-016 v1 permits at most one configured no-response follow-up. The schema remains sequence-capable so a later architecture does not require replacing the identity model.

## Credit rule

Canonical commercial rule:

```text
proactive outbound RecoveryOutreachAttempt successfully admitted/sent
  -> one recovery credit

customer replies
  -> ordinary continuation messages in the same Conversation
  -> no new recovery credit

customer does not reply
configured follow-up becomes due
Moda sends another proactive recovery outreach
  -> create/admit attempt #2
  -> one additional recovery credit
```

Therefore:

```text
follow-up < 24h with no customer response   => new credit
follow-up >= 24h with no customer response  => new credit
customer has responded before due time      => suppress follow-up; no new credit
```

The 24-hour Meta customer-service window is provider-policy state and MUST NOT be used as Moda's recovery-credit boundary.

## Follow-up timing

The merchant configures one delay. It is measured from the latest successfully sent proactive recovery attempt:

```text
followUpDueAt = latestAttempt.sentAt + followUpDelayMinutes
```

A delayed job is only a wake-up hint. When it wakes, durable state is revalidated once.

Before sending attempt #2 require:

```text
CheckoutRecovery still active
shop execution still eligible
attempt #1 successfully sent
no customer inbound after attempt #1 sentAt
order/recovery not completed/cancelled/expired
follow-up still enabled in the policy snapshot governing the pending follow-up
follow-up due time reached
capacity admission succeeds
```

If capacity is unavailable, do not send. Mark the attempt `CAPACITY_BLOCKED`. Do not silently borrow another entitlement or send first and bill later.

## Conversation invariant

ARCH-016 MUST NOT create a new `Conversation` merely because a new outreach attempt exists.

```text
CheckoutRecovery generation N
  -> exactly one recovery Conversation
  -> N RecoveryOutreachAttempts
```

`Conversation` remains the long-lived communication thread for that recovery generation.

An attempt links to the proactive outbound `ConversationMessage` created by the existing outbound admission path. This gives explicit provenance without duplicating `conversationId` on the attempt:

```text
RecoveryOutreachAttempt
  -> CheckoutRecovery
  -> Conversation

RecoveryOutreachAttempt.outboundMessageId
  -> proactive ConversationMessage
```

Inbound engagement resolves the recovery from `Conversation.checkoutRecoveryId` and marks the latest `WAITING_FOR_RESPONSE` attempt engaged. If Meta `context.id` points to an older proactive attempt, preserve the message reply-context provenance but suppress the current no-response follow-up because the customer has engaged with the recovery conversation.

## CheckoutRecovery generations and expiry

`EXPIRED` is historical, not deleted.

Add:

```text
generation Int
lastExternalActivityAt DateTime
```

Replace global uniqueness:

```text
@@unique([shopId, checkoutToken])
```

with:

```text
@@unique([shopId, checkoutToken, generation])
```

Add a PostgreSQL partial unique index guaranteeing at most one active generation for `(shopId, checkoutToken)` where status is one of:

```text
DETECTED
MESSAGE_SENT
ENGAGED
```

Only `EXPIRED` may restart from later checkout activity. `COMPLETED` and `CANCELLED` remain permanently terminal for that checkout token unless another future architecture changes the rule.

## Recovery external activity clock

`lastExternalActivityAt` is monotonic.

Qualifying activity:

```text
checkout update activityAt
inbound customer WhatsApp message for the recovery Conversation
initial detectedAt at generation creation
```

Do NOT reset expiry from:

```text
Moda initial outbound recovery
Moda follow-up outbound
CommerceAgent outbound
billing/capacity updates
admin reads/edits
background reconciliation
updatedAt noise
```

Always write:

```text
lastExternalActivityAt = max(current, incomingActivityAt)
```

so late/out-of-order events never move the activity clock backwards.

## Admin-controlled lifetime

Extend the existing singleton `BackgroundRuntimeConfig`:

```text
checkoutRecoveryLifetimeDays Int @default(21)
```

Allowed range:

```text
1..90 days
```

This is an `OPERATIONAL` runtime control and uses the existing optimistic version + audit reason mechanism.

Expiry calculation uses the current runtime value:

```text
cutoff = now - checkoutRecoveryLifetimeDays
active recovery with lastExternalActivityAt <= cutoff
  -> EXPIRED
```

Do not persist a derived `expiresAt`; this makes an admin lifetime change effective without rewriting every recovery row.

## Expiry scheduler

Reuse `moda-recovery-worker`; no new Render service and no Gateway task.

Add one leased scheduler to the existing recovery worker process. Add lease enum:

```text
CHECKOUT_RECOVERY_EXPIRY
```

Use a fixed one-hour scheduler cadence. The lifetime remains admin-configurable; the sweep cadence is operational implementation detail for v1 and is not another merchant/admin setting.

Each sweep processes bounded pages and performs conditional terminal transitions only when the row is still active and still older than the current cutoff.

Expiry also cancels/suppresses any pending no-response follow-up attempt/job for the recovery.

## Post-expiry checkout update

Current code discards checkout updates when no recovery exists and ignores terminal recoveries. ARCH-016 changes only the `EXPIRED` case.

When a checkout update arrives for a checkout whose latest recovery generation is `EXPIRED`:

```text
checkout update
  -> create/refresh PendingRecoveryCandidate using existing inactivity scheduling
  -> do not create CheckoutRecovery immediately
  -> further activity resets pending timer
  -> candidate maturity re-fetches current Shopify checkout
  -> if still recoverable, create generation = previous generation + 1
  -> create new Conversation only when the new recovery actually initiates
  -> create RecoveryOutreachAttempt sequence 1
```

If latest generation is `COMPLETED` or `CANCELLED`, keep existing terminal behavior.

Generation selection/materialisation MUST occur under the existing checkout-scoped lock and survive duplicate/concurrent Shopify deliveries.

## Installation/scope/subscription eligibility

A discount catalogue is usable only when:

```text
Shop.status = ACTIVE
ShopSettings.onboardingCompleted = true
Subscription.status IN (ACTIVE, TRIALING)
read_discounts scope is present in the durable offline session
```

If any prerequisite is absent, fail closed as `UNAVAILABLE`/`SYNC_REQUIRED`; do not display stale data as current.

## Infrastructure assessment

No new deployable service is required.

Existing boundaries are sufficient:

```text
moda-interact          Shopify UI + webhook ingress + install lifecycle
moda-interact-background
                       discount sync + expiry + recovery orchestration
moda-interact-admin    platform controls + tenant override
PostgreSQL             durable state
Redis/BullMQ           async wake-up/sync work
```

No ARCH-016 Gateway task is authorised.

## Observability assessment

Reuse existing shared structured logging and BullMQ/OpenTelemetry instrumentation. Add bounded semantic log events for:

```text
discount sync requested/started/completed/failed/superseded
recovery expired
new recovery generation materialised
outreach attempt admitted/sent/engaged/suppressed/capacity-blocked
```

Do not create duplicate generic HTTP/queue metrics.

## Task graph

```text
ARCH-016-DATABASE-001 ------------------------------+
       |                                               |
       +--> ADMIN-001                                  |
       +--> BACKGROUND-002                             |
       |                                               |
       +------------------+----------------------------+
                          |
ARCH-016-SHARED-001 ------+
       |                  |
       +--> SHOPIFY-001   |   requires DATABASE + SHARED
       +--> BACKGROUND-001|   requires DATABASE + SHARED
       +--> SHOPIFY-002   |   requires DATABASE + SHARED
       +--> ADMIN-002     |   requires DATABASE + SHARED
       +--> BACKGROUND-003|   requires DATABASE + SHARED

No implementation sibling depends on another sibling merely because it supplies
runtime data. Catalogue/UI/outreach tests seed the durable state they consume.

All implementation tasks
       -> SYSTEM-TEST-001
```

Parallelism is allowed where dependencies permit. Do not serialize tasks merely by task number. Dependencies in ARCH-016 represent hard schema, published-contract or validation prerequisites; they do not encode merchant/runtime sequence. A task that merely reads data another sibling will populate in production MUST seed that durable state in its focused tests rather than depend on the sibling implementation.

## Tasks

| Task | Repository | Summary |
|---|---|---|
| ARCH-016-DATABASE-001 | moda-interact-database | Persist recovery policy, admin override, discount catalogue, outreach attempts, generations and lifetime config. |
| ARCH-016-SHARED-001 | moda-interact-shared | Implement, version and publish canonical ARCH-016 queue/policy contracts in one task. |
| ARCH-016-SHOPIFY-001 | moda-interact | Add scope/webhooks/install lifecycle and app-side sync triggers/invalidation. |
| ARCH-016-BACKGROUND-001 | moda-interact-background | Reconcile the authoritative Shopify discount catalogue and trigger sync after background subscription/reinstall activation. |
| ARCH-016-SHOPIFY-002 | moda-interact | Add merchant Recovery Settings route/UI/actions. |
| ARCH-016-ADMIN-001 | moda-interact-admin | Add checkout-recovery lifetime to platform runtime controls. |
| ARCH-016-ADMIN-002 | moda-interact-admin | Add tenant recovery-policy visibility and explicit override. |
| ARCH-016-BACKGROUND-002 | moda-interact-background | Expire stale recovery generations and restart after later checkout activity. |
| ARCH-016-BACKGROUND-003 | moda-interact-background | Implement chargeable recovery outreach attempts and one no-response follow-up. |
| ARCH-016-SYSTEM-TEST-001 | moda-interact-system-test | Integrated validation after implementation and developer manual testing. |

## Post-review update — SHARED-001 Attempt 1 Accepted

`ARCH-016-SHARED-001` is architect-accepted **Complete** at implementation commit `202082e`.

The published Shared release is:

```text
@modainteract/moda-interact-shared@0.12.1
```

It supplies the architecture-owned runtime boundary for:

```text
merchant effective recovery policy
Shopify discount-sync queue payload
Shopify discount-sync queue/job names
bounded deterministic discount-sync job identity
```

The accepted Shared implementation remains intentionally free of Prisma/database types, provider GraphQL response models and CommerceAgent/LLM discount-selection semantics.

Current ARCH-016 frontier after this acceptance:

```text
SHARED-001       Complete
DATABASE-001     Ready

SHOPIFY-001      Pending; requires DATABASE-001 + SHARED-001
BACKGROUND-001   Pending; requires DATABASE-001 + SHARED-001
SHOPIFY-002      Pending; requires DATABASE-001 + SHARED-001
ADMIN-002        Pending; requires DATABASE-001 + SHARED-001
BACKGROUND-003   Pending; requires DATABASE-001 + SHARED-001

ADMIN-001        Pending on DATABASE-001
BACKGROUND-002   Pending on DATABASE-001
SYSTEM-TEST-001  Pending; terminal integrated phase after all implementation tasks and developer manual testing
```

No implementation consumer is promoted merely because Shared is now Complete; `DATABASE-001` remains the unsatisfied common hard prerequisite.

## Development migration/rollout

Moda is still in development and has no live merchants. No business-data transformation for live merchants is required beyond deterministic schema backfill of existing development rows.

Database migration order:

```text
1. ARCH-016-DATABASE-001
2. ARCH-016-SHARED-001 package publication can occur independently
3. consumers pin the published Shared version
4. application/background/admin tasks deploy
```

The database migration MUST backfill existing `CheckoutRecovery` rows:

```text
generation = 1
lastExternalActivityAt = max(detectedAt, engagedAt when present)
```

Do not delete/recreate durable PostgreSQL state merely because the environment is development.

## System-test timing

`ARCH-016-SYSTEM-TEST-001` is defined now but remains Pending until every implementation dependency is Complete.

The developer may manually validate the integrated feature before invoking the Ready system-test task. No implementation task depends on the system-test task.

## Post-review update — DATABASE-001 Attempt 2 Accepted

`ARCH-016-DATABASE-001` Attempt 2 is architect-accepted and **Complete**. The durable
schema boundary now provides the complete recovery policy/override state, authoritative
Shopify discount catalogue projection, generation-aware recovery identity, proactive
outreach-attempt identity and the admin-controlled inactivity lifetime/expiry lease.

Attempt 2 corrected the three PostgreSQL integrity defects found during Attempt-1
review: the historical recovery uniqueness object is dropped as an index, enabled
follow-up policies cannot carry a NULL delay, and deterministic single-code claims
cannot carry an unknown NULL `codeCount`. No Conversation identity, ARCH-010
promotion data or unrelated billing schema was changed.

The current ARCH-016 implementation frontier is:

```text
ARCH-016-DATABASE-001    Complete
ARCH-016-SHARED-001      Ready

DATABASE-only frontier:
  ARCH-016-ADMIN-001       Ready
  ARCH-016-BACKGROUND-002  Ready

DATABASE + SHARED frontier (still waiting for SHARED-001):
  ARCH-016-SHOPIFY-001     Pending
  ARCH-016-BACKGROUND-001  Pending
  ARCH-016-SHOPIFY-002     Pending
  ARCH-016-ADMIN-002       Pending
  ARCH-016-BACKGROUND-003  Pending

ARCH-016-SYSTEM-TEST-001 Pending
```

The selected validation database still has the pre-existing ARCH-015 Prisma P3009,
so ARCH-016 migration deployment was not executed there. That history condition must
be resolved before deployment; it does not reopen DATABASE-001.

The terminal system-test task remains gated on all implementation prerequisites and
continues to sit after the developer manual-testing checkpoint.


## Post-review update — ADMIN-001 Attempt 1 Accepted

`ARCH-016-ADMIN-001` Attempt 1 is architect-accepted **Complete** at implementation commit `44dd7a5`. The existing audited platform runtime-controls path now exposes `checkoutRecoveryLifetimeDays` as an `OPERATIONAL` whole-day control with default `21` and range `1..90`; no tenant-specific lifetime state, direct recovery-row rewrite or scheduler-cadence control was introduced.

This review also reconciles the ARCH-016 frontier after the independently accepted DATABASE-001 and SHARED-001 branches. Both prerequisites are now Complete, so every untouched task whose declared dependencies are exactly those accepted prerequisites is promoted without being claimed:

```text
ARCH-016-DATABASE-001    Complete
ARCH-016-SHARED-001      Complete
ARCH-016-ADMIN-001       Complete

Ready:
  ARCH-016-SHOPIFY-001
  ARCH-016-SHOPIFY-002
  ARCH-016-BACKGROUND-001
  ARCH-016-BACKGROUND-002
  ARCH-016-BACKGROUND-003
  ARCH-016-ADMIN-002

ARCH-016-SYSTEM-TEST-001 Pending
```

The Ready promotions are dependency-state reconciliation only: each promoted task remains `attempt: 0`, `executor: null` and `claimed_at: null` until launched through the normal task workflow. `ARCH-016-SYSTEM-TEST-001` is not started automatically and remains behind completion of all implementation tasks plus the developer manual-testing checkpoint.

## Post-review update — ADMIN-002 Attempt 2 Accepted

`ARCH-016-ADMIN-002` Attempt 2 is architect-accepted **Complete** at implementation
commit `215cb7f`.

The accepted Admin boundary now provides tenant-scoped merchant/override/effective
recovery-policy visibility, CURRENT/ACTIVE/running Shopify discount eligibility,
complete durable override UPSERT/CLEAR semantics, transactional active-SUPER_ADMIN
rechecks and dedicated before/after audit history including override expiry. Merchant
`ShopSettings` remains merchant-owned, Shared remains pinned to `0.12.1`, and no AI
discount-selection or provider-secret presentation was introduced.

This acceptance does not independently make the terminal system-test task eligible.
`ARCH-016-SYSTEM-TEST-001` remains Pending until every implementation dependency is
Complete and the developer has completed the existing manual-testing checkpoint.
