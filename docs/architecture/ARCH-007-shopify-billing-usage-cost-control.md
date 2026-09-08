---
id: ARCH-007
title: Shopify App Pricing billing, usage metering and WhatsApp cost control
status: In Progress
coordinator: moda_architect
created: 2026-09-07
updated: 2026-09-08
---

# ARCH-007: Shopify App Pricing billing, usage metering and WhatsApp cost control

## Current durable task state

> **Synchronized 2026-09-08.** This section is the current task-state snapshot.
> Earlier task-state tables or frontier prose later in this architecture document may be historical.
> For exact current status/dependencies, use the individual task YAML and
> [`WORKSPACE-CURRENT-TASK-STATE.md`](WORKSPACE-CURRENT-TASK-STATE.md).

Counts: `complete` 21, `pending` 13, `ready` 5.

Ready: `ARCH-007-ADMIN-001`, `ARCH-007-BACKGROUND-005`, `ARCH-007-BACKGROUND-009`, `ARCH-007-BACKGROUND-010`, `ARCH-007-SHOPIFY-003`.

Current accepted/published Shared release: `@modainteract/moda-interact-shared@0.8.0`.

## Status

In Progress.

ARCH-007 is a **pre-production / breaking rollout**. Moda Interact is still in development and there is no production billing state that must be preserved or kept backwards compatible. Repository agents MUST implement the target schema and runtime directly. Normal Prisma migration artifacts ARE required for database schema tasks so the repository migration history can recreate the target development schema. Those migrations may be destructive to disposable development billing data; do not add data-preserving backfills, dual reads or compatibility adapters unless `moda_architect` later changes this rollout classification.

## Problem

Moda Interact has an initial billing skeleton and a growing ARCH-007 implementation, but the durable architecture must now represent the complete agreed product rather than the original Free/Basic sketch:

- the initial commercial catalogue is **Free, Starter, Growth and Scale**, while the runtime catalog remains data-driven so future Shopify-created plans can be mapped without a code deploy;
- Free provides five lifetime recovery conversations per durable Shopify shop before signed per-shop allowance adjustments;
- Starter/Growth/Scale combine recurring Shopify subscription pricing, current-period included recovery allowances and normal overage;
- **every plan may sell repeatable prepaid recovery-credit packs**, and a merchant may buy another pack after a prior pack is exhausted;
- paid plan top-up rates may be cheaper than Free/higher-tier rates according to Shopify App Pricing configuration; Moda must not duplicate monetary pack price as a database source of truth;
- paid recovery-capacity order must be **included allowance -> purchased credits -> normal overage**; Free order is **lifetime Free allowance -> purchased credits -> block**;
- purchased credits are durable prepaid capacity and do not reset at the monthly billing boundary;
- usage must be published through Shopify App Events from the first billing implementation;
- automated WhatsApp conversations must have bounded **per-conversation** outbound-message safety limits independent of the merchant-facing recovery-conversation commercial unit;
- raw inbound WhatsApp messages must be persisted individually but nearby fragments must be coalesced into one logical CommerceAgent turn rather than causing one agent/reply per webhook;
- platform-wide and per-shop safety controls must be configurable through the Admin app;
- Free allowance testing/support exceptions must use the existing append-only shop allowance-adjustment mechanism, not environment variables or hard-coded test-shop branches;
- the existing JSON `entitlements`/`limits`, string subscription/usage states and aggregate-before-write quota check are not deterministic or concurrency-safe enough;
- current WhatsApp worker paths can call the raw provider sender directly, so not every Moda-originated message necessarily crosses one usage/safety boundary;
- current Shopify subscription projection assumptions become unsafe when a subscription has recurring and multiple usage-meter items;
- Shopify subscription state can change outside the app redirect lifecycle, so callback-only synchronization is insufficient;
- billing publication must never become a correctness dependency of recovery or customer messaging.

## Goals

1. Make Shopify App Pricing authoritative for commercial subscription state, subscription/overage prices and recovery-credit-pack monetary prices.
2. Make Moda authoritative for feature entitlements, operational included-allowance mirrors, Free lifetime usage, purchased-credit balances, safety limits, shop overrides, circuit breakers, merchant billing notifications and billing-publication state.
3. Support configurable Shopify-created plans without code deployment: Shopify configuration first, then SUPER_ADMIN maps the exact Shopify plan handle and meter handles to typed Moda policy.
4. Preserve the initial product catalogue: Free `$0 / 5 lifetime`, Starter `$35 / 200 monthly / $0.05 overage`, Growth `$75 / 500 monthly / $0.04 overage`, Scale `$149 / 1,200 monthly / $0.03 overage`. Monetary values remain configured in Shopify App Pricing.
5. Enforce five lifetime Free recovery conversations per durable Shopify shop identity with concurrency-safe admission, while allowing signed audited per-shop allowance adjustments for testing/support/operational exceptions.
6. Support repeatable prepaid recovery-credit packs for every plan. Purchased capacity may be replenished indefinitely and is consumed after included capacity but before paid overage.
7. Publish exactly one Shopify usage unit for each normal committed paid recovery conversation that is not covered by purchased credits, including units inside the plan's included allowance; Shopify determines included versus overage billing.
8. Publish exactly one Shopify pack-purchase usage event per merchant pack request and activate the purchased credits exactly once only after that billing event is reported.
9. Keep Shopify App Events asynchronous and idempotent through a durable Moda usage/outbox ledger.
10. Provide negative compensating billing events rather than mutating/deleting historical usage.
11. Route every Moda-originated WhatsApp send through one durable outbound admission/safety boundary using stable durable conversation identity.
12. Coalesce fragmented inbound WhatsApp messages into bounded conversation-scoped turns before CommerceAgent execution, while persisting each inbound message independently.
13. Enforce plan defaults, per-shop overrides and platform hard ceilings without allowing a shop override to bypass a platform hard limit.
14. Provide Admin plan catalog, safety policy, shop override, Free allowance adjustment, billing operations, audit and reconciliation views.
15. Preserve merchant-facing system notifications and upgrade/top-up CTAs through the existing merchant-support messaging layer.
16. Use Prisma-first application/database access for ARCH-007; do not introduce new billing `$queryRaw`, `$executeRaw`, `Prisma.sql` or hand-written SQL paths.

## Non-Goals

- Rebuilding Shopify App Pricing configuration inside Moda Admin. Subscription prices, overage prices, pack prices and Shopify meter definitions remain configured in Shopify.
- Charging merchants per individual inbound or outbound WhatsApp message in ARCH-007. The merchant-facing billable unit remains the recovery conversation; message counts are internal safety/cost controls.
- Treating each raw inbound WhatsApp webhook as a CommerceAgent turn. Raw messages are persisted and then coalesced by conversation.
- Adding `INBOUND_AUTOMATED_MESSAGE`, `INBOUND_CUSTOMER_MESSAGE` or `COMMERCE_AGENT_TURN` as a merchant billing metric in this architecture revision. A separate agent/token budget may be designed later if it must differ from the outbound-message cap.
- Creating an exact Meta invoice/pricing engine. ARCH-007 records provider lifecycle/category/cost metadata when available and message counts needed for later cost reconciliation; it must not invent provider cost values that Meta did not supply.
- Migrating production billing data. There is no production billing migration requirement for this initiative.
- Creating Kafka, another database, or a new general billing microservice.
- Exposing Admin operational billing data or cross-tenant telemetry directly to merchants.

## Current Architecture

Inspected workspace facts at the ARCH-007 design baseline:

- `moda-interact-database/prisma/schema.prisma` defines `BillingPlan` with JSON `entitlements` and `limits`, `Subscription` with string `provider`/`status`, `UsageEvent` with string `metric`, and `BillingPeriod` with string `status`.
- `moda-interact-background/src/services/entitlement.service.ts` reads those JSON fields, treats `null` limits as unlimited, aggregates UsageEvent rows and falls back to calendar-month boundaries when subscription dates are absent.
- `moda-interact-background/src/services/usage.service.ts` writes idempotent UsageEvent rows but has no production call sites that make the agreed recovery billing lifecycle complete.
- `moda-interact/app/services/billing/providers/shopify-billing.provider.ts` queries Partner API `activeSubscription`, but selects the first non-null `items[].handle` as the plan handle and does not read pricing types, usage, or `pendingUpdate`.
- `moda-interact-background/src/workers/whatsapp.worker.ts` contains direct `sendWhatsAppText()` paths. ARCH-007 cannot use ConversationMessage row counts as the sole outbound-message control unless those paths are unified.
- `MerchantSupportMessage` already supports SYSTEM messages, `systemCode`, `systemVersion`, unique `sourceKey`, read state and translation. Existing billing code already uses this channel for subscription-ended messaging.
- `moda-interact-background` already has independently deployable worker entrypoints (`shopify-event`, `recovery`, `messaging`, `merchant-communications`). ARCH-007 may add a billing worker entrypoint using the same runtime pattern rather than creating a new repository/service boundary.
- `moda-interact-gateway` already declares the background worker topology in `render.test.yaml` and `render.production.yaml`.

## External Shopify Contract Baseline

Verified against Shopify documentation on 2026-09-07. Repository agents must implement this contract rather than rediscovering a different billing mechanism.

### Active Subscription — Partner API 2026-07

Endpoint:

```text
https://partners.shopify.com/<SHOPIFY_PARTNER_ORG_ID>/api/2026-07/graphql.json
```

Root query:

```graphql
activeSubscription(appId: ID!, shopId: ID!)
```

ARCH-007 requires at least:

```text
billingPeriod
cancelAtEndOfCycle
trialEndsAt
currentBillingCycle { startTime endTime }
items {
  handle
  description
  price {
    __typename
    active
    currency
    ... on FlatRatePrice { amount }
    ... on TieredPrice {
      tiersMode
      tiers { upTo amountPerUnit amount }
    }
  }
  usage { quantity cost { amount currencyCode } }
}
pendingUpdate {
  billingPeriod
  items { handle price { __typename ... on FlatRatePrice { amount } } }
  legacySubscriptionId
}
legacySubscriptionId
```

`FlatRatePrice` identifies the commercial recurring-plan item. `TieredPrice` identifies usage-meter items. `activeSubscription == null` means no active Shopify App Pricing contract. A Partner API failure is not equivalent to no subscription and must fail closed without redirecting a paying merchant as though no contract existed.

### Shopify App Events — 2026-07

Token endpoint:

```text
POST https://api.shopify.com/auth/access_token
```

Body:

```json
{
  "client_id": "<client id>",
  "client_secret": "<client secret>",
  "grant_type": "client_credentials"
}
```

Use the returned `access_token` as `Authorization: Bearer <token>` and cache it according to returned `expires_in` (currently documented as 3599 seconds) with a safety refresh margin. Do not request a new token per usage event.

Event endpoint:

```text
POST https://api.shopify.com/app/2026-07/events
```

Billing request:

```json
{
  "shop_id": "gid://shopify/Shop/<id>",
  "event_handle": "<configured Shopify meter handle>",
  "timestamp": "<usage occurredAt ISO-8601>",
  "idempotency_key": "<stable <=64 chars>",
  "attributes": { "value": 1 }
}
```

The event handle must match the meter configured in Shopify App Pricing. Billing-event idempotency is permanent. Negative non-zero values are supported for compensating corrections. Billing-event timestamps must belong to an allowable Shopify billing window; do not rewrite historical `occurredAt` merely to make a rejected event current.

References:

- https://shopify.dev/docs/apps/launch/billing/shopify-app-pricing
- https://shopify.dev/docs/api/partner/latest/active-subscription
- https://shopify.dev/docs/api/app-events/2026-07/creating-events

## Proposed Architecture

```text
                           SHOPIFY APP PRICING
                 +----------------------------------+
                 | recurring plan prices            |
                 | normal recovery usage/overage    |
                 | recovery-credit-pack usage meter |
                 +----------------+-----------------+
                                  |
                          ActiveSubscription
                                  |
                                  v
                       Moda typed Subscription
                                  |
                                  v
                       EFFECTIVE BILLING POLICY
                +-----------------+-----------------+
                |                                   |
                v                                   v
             FREE                               PAID_METERED
       base lifetime allowance              current-period included
       + signed adjustments                 recovery allowance
                |                                   |
                +------------+----------------------+
                             v
                    RECOVERY CAPACITY ORDER

FREE:        free lifetime -> purchased credits -> block
PAID:        included -> purchased credits -> normal overage
                             |
                             v
                    RECOVERY ADMISSION SERVICE
                  reservation / commit / release
                             |
                             v
                DURABLE CONVERSATION IDENTITY
              recovery-linked or standalone scope
                             |
                 raw customer inbound messages
                             |
                 RAW ABUSE ADMISSION
                 sender + global
                             |
             persist individually + deduplicate
                             |
          3s quiet / 10s maximum turn coalescing
                             |
              SETTLED-TURN ABUSE ADMISSION
         sender + conversation + shop + global
                             |
                             v
               COMMON WHATSAPP SEND BOUNDARY
       platform hard limit -> plan default -> shop override
                reserve outbound slot BEFORE AI
                             |
                             v
                       CommerceAgent / META
                             |
                    provider lifecycle
                             |
                 +-----------+-----------+
                 |                       |
                 v                       v
          Moda UsageEvent        message/provider state
          durable ledger/outbox  operational accounting
                 |
          asynchronous billing worker
                 |
                 v
            Shopify App Events
                 |
                 v
        Shopify meter / merchant bill

Recovery-credit pack request:
merchant -> durable purchase + pack UsageEvent -> publisher -> Shopify
        -> REPORTED -> activate purchased credits exactly once

Admin reads/writes plan mapping, platform/shop policy, signed Free allowance
adjustments, audit and billing operations. Monetary prices stay in Shopify.
```

## Architectural Invariants

### INV-001 — Shopify owns commercial subscription state

Shopify is authoritative for plan contract, price, billing interval/cycle, included usage/tier pricing, usage cost and pending commercial updates. Moda stores a typed local projection so runtime does not query Shopify on every background event.

### INV-002 — Moda owns entitlements and safety

Moda owns feature entitlement mapping, Free lifetime allowance/usage, automated outbound-message policy, shop overrides, platform hard ceilings, circuit breakers, allowance adjustments, merchant system messages, usage/outbox delivery state and operational reconciliation.

### INV-003 — Plan catalog is data-driven

A new plan is created/configured in Shopify first. A SUPER_ADMIN then registers the exact immutable Shopify plan handle in Moda Admin and maps it to Moda plan type, features, usage meter handle when paid, and safety defaults. An active subscription whose Shopify plan handle is unknown/inactive in Moda is `UNMAPPED` and receives no guessed entitlements. Adding a correctly configured plan must not require a code deploy.

### INV-004 — Explicit plan selection

After installation, a shop without a Shopify App Pricing contract is redirected to Shopify's hosted plan-selection page. Moda does not silently invent an internal Free subscription.

### INV-005 — Free allowance is lifetime per durable Shopify shop

The initial Free plan has five lifetime recovery conversations. Usage does not reset on calendar month, billing cycle, reinstall, upgrade or downgrade. If three Free conversations were consumed before upgrade, only two remain if the shop later returns to Free. Admin allowance adjustments change effective allowance without deleting historical usage.

### INV-005A — Free allowance adjustments are the supported testing/support override

The canonical Free base allowance is 5. Effective Free allowance is `base + SUM(signed BillingAllowanceAdjustment)` for that durable shop. Positive adjustments may raise a test/support shop above 5; negative adjustments may lower it. Historical committed/reserved usage is never rewritten to make a lower allowance fit, and remaining capacity is never negative. Do not add `FREE_RECOVERY_LIMIT` environment switches, `isTestShop` branches or domain-name special cases. Every adjustment is append-only, reasoned and audited through Admin.
### INV-006 — Conversation consumption begins at successful provider initiation

Creating a `Conversation` row alone does not consume/bill a recovery conversation. Admission first reserves capacity. A successful initial recovery-provider send commits the reservation and creates the durable recovery-conversation UsageEvent. A definitive pre-initiation failure releases the reservation. Duplicate/replayed workflow execution must resolve the same reservation/usage identity.

### INV-007 — Free admission is concurrency-safe

`committed + reserved + requested <= effective lifetime allowance` must be enforced under concurrent workers. ARCH-007 uses Prisma transactions plus a versioned/CAS counter and bounded retries; it must not add raw SQL/`FOR UPDATE` as a shortcut.

### INV-008 — Paid included usage is not a service hard stop

For a paid metered plan, recovery conversation N+1 remains eligible after N included units. Moda reports every committed paid recovery conversation to Shopify. Shopify applies included units and overage pricing.

### INV-008A — Recovery-credit packs are repeatable prepaid capacity on every plan

Every plan may enable a recovery-credit-pack Shopify usage meter. A merchant may purchase another pack after any previous pack is exhausted; there is no one-pack lifetime restriction. Pack monetary price is authoritative in Shopify App Pricing and is not duplicated in Moda billing tables. Purchased credits do not reset at the monthly billing boundary or because the merchant changes plan.

### INV-008B — Capacity consumption order is deterministic

Free uses `effective lifetime Free allowance -> purchased credits -> block`. Paid uses `current-period included recovery allowance -> purchased credits -> normal Shopify recovery overage`. A recovery committed against purchased credits creates internal usage/accounting state but MUST NOT also publish the normal paid recovery meter for the same recovery.
### INV-009 — Exactly one Shopify usage unit per committed paid recovery conversation

The positive billing event uses the plan mapping's configured Shopify usage meter handle and `value=1`. The stable event identity is derived from durable Moda usage identity and is <=64 characters. Repeated publisher attempts reuse it.

### INV-009A — Pack billing activates credits only after successful Shopify reporting

A merchant pack request creates one durable `RECOVERY_CREDIT_PACK_PURCHASE +1` UsageEvent using the current plan's snapshotted pack meter and a permanent idempotency identity. The UI request does not grant credits. Only a linked UsageEvent that reaches `REPORTED` may activate its `RecoveryCreditPurchase` and increment purchased `grantedQuantity`, exactly once under replay/concurrency.
### INV-010 — Billing publication is asynchronous

Shopify App Events is never called inside the recovery admission/provider-send transaction and is not a prerequisite for continuing the business workflow. A local committed UsageEvent/outbox record is the durable handoff.

### INV-011 — Ledger history is append-only for billing corrections

Do not edit/delete a historical +1 to produce net-zero usage. Persist a compensating -1 UsageEvent linked to the original event, with its own permanent idempotency key and audit reason.

### INV-012 — Billing cycle boundaries come from Shopify

Paid BillingPeriod boundaries are created/reconciled from `currentBillingCycle.startTime/endTime`. The ARCH-007 paid path has no calendar-month fallback.

### INV-013 — Plan-item type is explicit

Never identify a plan by the first `items[].handle`. A mapped recurring plan handle must correspond to a `FlatRatePrice` item; configured usage-meter handles correspond to `TieredPrice` items. Unknown, missing, duplicate or structurally incompatible item mappings fail closed and are surfaced operationally.

### INV-014 — Pending Shopify changes do not prematurely change current entitlements

`pendingUpdate` is stored/displayed separately. Current entitlements remain based on the current Shopify contract until the pending update becomes active.

### INV-015 — No AI conversation has an unbounded automated-outbound allowance

Every plan has a finite effective automated outbound-message hard cap. Customer inbound messages do not consume this cap.

### INV-015A — Raw inbound messages are not one-for-one agent turns

Every authenticated inbound WhatsApp message that passes the raw abuse-admission gate is deduplicated and persisted individually. Background coalesces nearby fragments for the same durable conversation using an initial 3-second quiet window and 10-second maximum settle window. One settled turn may invoke CommerceAgent at most once. One conversation may have at most one live CommerceAgent processor; different conversations remain concurrent.

A raw event denied by the later BACKGROUND-011 sender/global abuse gate is intentionally acknowledged/suppressed before tenant lookup and ConversationMessage persistence. This is the only ARCH-007 exception to the normal per-message persistence rule.

### INV-015B — Authenticated inbound traffic is still subject to abuse admission

Meta webhook authenticity does not authorise unlimited Moda application work.

Before tenant/database routing, Background applies atomic rolling-window admission by sender and global ingress. After BACKGROUND-010 coalesces a durable logical turn and claims its conversation lease, Background applies a second atomic admission by sender, durable conversation, shop and global turn rate before outbound reservation or CommerceAgent execution.

Raw abuse denial performs no tenant lookup, ConversationMessage persistence, turn enqueue, AI work or provider call. Settled-turn abuse denial preserves already-persisted raw fragments, marks the observed inbound version handled, clears processing/pending state and performs no outbound reservation, AI/tool work or provider call.

Abuse counters are operational Redis state, replay-idempotent and atomic across applicable scopes. They are not merchant billing usage. No raw phone number or message content may appear in Redis key names or metric labels.
### INV-016 — All outbound WhatsApp sends use one admission boundary

No recovery/AI/product/clarification workflow may call raw `sendWhatsAppText()` or equivalent provider send without durable message intent, an already-resolved durable `conversationId`, tenant ownership validation and effective safety admission. Recovery-linked conversations retain their recovery identity. Product/support/clarification flows use one unique active standalone scope per shop/customer/type and a 24-hour inactivity lifecycle so the per-conversation cap cannot be reset by creating a new row for every message. All existing direct-send paths must be routed through the accepted boundary.

### INV-017 — Platform hard ceilings dominate shop overrides

Effective hard cap is bounded by platform absolute hard cap. A shop override may raise/lower a plan default only within platform bounds. Expired overrides are ignored automatically.

### INV-017A — Recovery pause and automated-WhatsApp pause are independent

`pauseNewRecoveries` and `pauseAutomatedWhatsapp` are separate circuit breakers.
Effective policy resolution must expose them as separate machine-readable
dimensions, not only as one aggregate `paused` flag.

- pausing new recoveries prevents admission of new recovery conversations;
- it does not by itself terminate or suppress an already admitted conversation;
- pausing automated WhatsApp suppresses Moda automated outbound WhatsApp,
  including messages inside an already admitted conversation.

When both platform and shop sources are active, operational/audit reasons should
preserve each active source rather than hiding one behind the other.

### INV-018 — Terminal response is reserved

The hard per-conversation cap includes one deterministic non-LLM terminal response slot. Normal generated/automated responses cannot consume that reserved slot. Once normal allowance is exhausted, do not invoke the CommerceAgent to produce another answer.

The effective policy resolver must fail closed unless
`terminalMessageReservedSlots` is a positive integer strictly less than the
effective outbound hard cap. Do not silently clamp invalid terminal-slot
configuration.

### INV-018A — Outbound capacity is reserved before CommerceAgent execution

For customer-driven turns, Background persists/coalesces the inbound messages, resolves the durable conversation, then reserves a normal outbound slot before invoking CommerceAgent/LLM/tools. If normal slots are exhausted, CommerceAgent is not invoked; only the one deterministic reserved terminal response may be sent. If the terminal response was already used, further agent/provider work is suppressed for that conversation.
### INV-019 — Merchant notifications are idempotent SYSTEM messages

Billing warning/exhaustion/plan-change notifications use existing MerchantSupportMessage SYSTEM semantics and a unique deterministic `sourceKey`. Action destinations are rendered by merchant UI from `systemCode`; URLs are not embedded inside translated message text.

### INV-020 — Shopify synchronization is bounded-staleness, not hot-path remote lookup

Plan-selection return performs immediate verification. A separate billing worker performs scheduled reconciliation. Billing publisher errors may trigger/mark a reconciliation need. Normal recovery/WhatsApp hot paths rely on the typed local projection and fail closed when it is stale/unmapped beyond architecture-approved bounds.

### INV-021 — Uninstall stops new usage but drains pre-uninstall billable events

When Shopify uninstall is received, shop lifecycle becomes UNINSTALLED and no new billable recovery may be admitted. Pending App Events for usage that occurred before uninstall remain eligible for prioritized publication inside Shopify's documented post-uninstall reporting window. Do not fabricate post-uninstall usage timestamps.

### INV-022 — Prisma-first billing implementation

ARCH-007 normal application/database code uses generated Prisma delegates, typed enums, relations, unique constraints, atomic numeric updates, `updateMany` CAS and Prisma transactions. Do not add billing `$queryRaw`, `$executeRaw`, `Prisma.sql`, raw SQL enum casts or direct database-driver SQL. Database tasks MUST create the normal Prisma migration generated for their accepted schema change and regenerate the repository's normal database artifacts. Because this is pre-production, migrations may assume disposable development billing data and development databases may be reset/recreated; do not add compatibility/backfill machinery solely to preserve old development billing rows.

## Request / Event Flows

### Install / first plan selection

```text
Shopify install/auth complete
  -> resolve durable Shop + shopifyShopId
  -> query activeSubscription
     -> Partner API failure: surface recoverable billing error; DO NOT assume no subscription
     -> null: redirect top-level to Shopify hosted pricing_plans
     -> contract: map exact FlatRatePrice plan handle to active BillingPlan
        -> unknown/inactive mapping: Subscription=UNMAPPED, fail closed, Admin operational issue
        -> mapped: persist typed Subscription + current cycle/pending update
  -> merchant app continues only with mapped eligible plan
```

### Free recovery admission

```text
eligible recovery candidate
  -> effective plan/policy = FREE
  -> effective lifetime allowance = base 5 + signed shop adjustments
  -> deterministic reservation sourceKey
  -> try FREE_RECOVERY_LIFETIME
       available -> reserve/commit Free
       exhausted -> try PURCHASED_RECOVERY_CREDITS
         available -> reserve/commit purchased credit
         exhausted -> deny new recovery + idempotent exhaustion SYSTEM message
```

A signed Admin adjustment changes effective Free capacity without changing historical committed/reserved usage. This is the supported way to raise/lower a test shop's Free limit.

The fifth admitted base-Free conversation remains interactive subject to message safety policy. Only the next new recovery is denied when both Free and purchased capacity are exhausted.

### Paid recovery: included -> purchased -> overage

```text
eligible recovery candidate
  -> effective plan = PAID_METERED
  -> determine normal RECOVERY_CONVERSATION quantity in current Shopify billing period
  -> if normal quantity < includedRecoveryConversationAllowance:
       use normal paid path
       successful initial send -> normal RECOVERY_CONVERSATION +1 PENDING Shopify report
  -> else if PURCHASED_RECOVERY_CREDITS available:
       reserve purchased credit
       successful initial send -> commit purchased credit
       create internal RECOVERY_CONVERSATION +1 NOT_APPLICABLE
       DO NOT publish the normal recovery meter for this recovery
  -> else:
       use normal paid path
       successful initial send -> normal RECOVERY_CONVERSATION +1 PENDING
       Shopify treats it as overage according to App Pricing
```

Paid merchants are not hard-stopped merely because included units or a purchased pack are exhausted. Separate safety/circuit-breaker policy may still stop work.

### Repeatable recovery-credit-pack purchase

```text
merchant selects Buy Recovery Pack
  -> reload current shop/subscription/plan; ignore client-supplied quantity/meter/price
  -> require safe mapped plan + enabled verified top-up meter
  -> one durable purchaseId
  -> transaction creates:
       RecoveryCreditPurchase PENDING_BILLING
       UsageEvent RECOVERY_CREDIT_PACK_PURCHASE +1 PENDING
       snapshotted current plan handle, meter handle, creditsGranted
  -> no credits granted yet
  -> generic App Events publisher reports persisted UsageEvent
  -> REPORTED:
       activate purchase exactly once
       PURCHASED_RECOVERY_CREDITS.grantedQuantity += creditsGranted
  -> NEEDS_ATTENTION:
       grant zero credits
  -> merchant may repeat the process after any earlier pack is exhausted
```

Shopify App Pricing is authoritative for the pack's monetary price. Higher paid plans may map to cheaper pack rates. Moda stores pack quantity/meter mapping, not duplicate money price.

### App Event publisher

```text
select bounded due PENDING/RETRYABLE reportable rows
  -> DO NOT hard-code a RECOVERY_CONVERSATION-only metric filter
  -> atomic/CAS claim to IN_FLIGHT
  -> get cached App Events bearer token; refresh before expiry
  -> POST one event to /app/2026-07/events using persisted shop/event handle/timestamp/key/quantity
  -> success => REPORTED
  -> transient/ambiguous => RETRYABLE + bounded backoff, same key
  -> permanent/current-period/meter/subscription configuration error => NEEDS_ATTENTION
```

The same generic publisher supports normal recovery usage, negative corrections and recovery-credit-pack purchase UsageEvents once their schemas/contracts are adopted.

### Negative correction

```text
SUPER_ADMIN determines committed paid usage must be reversed
  -> require original UsageEvent + reason
  -> append compensating UsageEvent quantity=-original net quantity
  -> link correction to original
  -> new permanent idempotency key
  -> generic publisher sends negative event
  -> audit actor/reason/original/correction
```

### Durable conversation + fragmented inbound turn

```text
raw WhatsApp inbound message
  -> verify/normalise upstream
  -> Background resolves stable conversation
       recovery-linked OR
       standalone:<shopId>:<customerId>:PRODUCT_DISCOVERY|PRODUCT_SUPPORT
  -> standalone active scope reused while IN_PROGRESS and <24h idle
  -> persist each new inbound message idempotently by providerMessageId
  -> increment inboundVersion
  -> first unprocessed fragment sets pendingTurnStartedAt
  -> delayed internal process-conversation-turn job
       quiet window = 3 seconds
       maximum settle = 10 seconds
  -> one live conversation processing lease
  -> join currently pending fragment contents in persisted order for logical turn
  -> reserve normal outbound slot BEFORE CommerceAgent
       available -> invoke agent once
       no normal capacity -> no agent; terminal slot behavior only
  -> if a newer inbound arrives while agent runs:
       do not send stale response
       release/fail prepared reservation according to accepted semantics
       newest settled version is processed next
```

Different conversations may process concurrently. Raw inbound messages are never discarded merely because they are coalesced.

### Common outbound-message safety

```text
workflow wants to send Moda-originated WhatsApp message
  -> require durable conversationId + tenant ownership
  -> count OUTBOUND_AUTOMATED_MESSAGE only for that conversation
  -> load effective policy:
       global/shop automated-WhatsApp pause
       platform absolute hard cap
       plan soft/hard defaults
       active bounded shop override
  -> atomically admit normal outbound slot
  -> normal slot -> desired template/text send + usage
  -> normal exhausted and terminal unused -> no LLM; deterministic terminal response once
  -> terminal already used or pause -> no provider/agent work
```

Customer inbound messages do not themselves increment `OUTBOUND_AUTOMATED_MESSAGE`.

### Upgrade / downgrade / unknown plan / uninstall

Upgrade and downgrade continue to use Shopify-hosted plan selection and `pendingUpdate`; current entitlements never change before Shopify makes the new plan active. The lifetime Free counter and purchased-credit balance survive plan changes. An unknown Shopify FlatRate plan handle remains `UNMAPPED` until SUPER_ADMIN registers it; no Free/paid entitlements are guessed.

On `APP_UNINSTALLED`, persist a stable uninstall cutoff, stop new admission, retain historical counters/purchases/usage and let the billing worker drain only pre-uninstall reportable events within Shopify's accepted window. Do not rewrite event timestamps to force acceptance.

## Repository Responsibilities

### moda-interact-database / moda_database

Owns final typed Prisma billing/conversation schema, migrations, relations, enums, indexes, reservation/counter support, standalone conversation scope, turn-settling state, policy/override/adjustment/audit persistence and recovery-credit purchase persistence.

### moda-interact-shared / moda_shared

Owns cross-repository billing semantics that must not drift: billing usage metrics including `RECOVERY_CREDIT_PACK_PURCHASE`, plan kinds, merchant billing system codes, provider-status v2, deterministic idempotency/source-key helpers and schema-version constants. Publication is a separate task.

### moda-interact / moda_app

Owns Shopify Partner Active Subscription verification, local subscription projection during merchant requests, hosted pricing redirects, current/pending billing UI, merchant SYSTEM-message CTAs, repeatable pack request creation, top-up-meter verification and uninstall lifecycle ingress. It never grants purchased credits merely because the merchant clicked Buy.

### moda-interact-background / moda_background

Owns effective entitlement/safety resolution, Free/purchased recovery reservations, capacity-order admission, usage recording, stable standalone conversation lifecycle, fragmented inbound turn coalescing, common outbound WhatsApp admission, provider lifecycle application, durable tenant resolution, Shopify App Events adapter/generic publisher, recovery-credit activation, corrections, scheduled reconciliation and independent billing worker runtime.

### moda-interact-messaging / moda_messaging

Owns Meta webhook verification/normalisation and canonical provider-status publication. It publishes provider identities from verified Meta payloads and does not fabricate Moda tenant identity or decide billing entitlement.

### moda-interact-admin / moda_admin

Owns plan/meter mapping, operational included-allowance mirrors, top-up pack quantity/meter mapping (not monetary price), platform/shop safety policy, signed Free allowance adjustments, billing overview/tenant detail, failed-event/reconciliation operations and privileged audit UI/actions.

### moda-interact-gateway / moda_gateway

Owns Render test/production billing-worker deployment declarations, environment wiring and readiness/scaling configuration after the background entrypoint exists.

### moda-interact-system-test / moda_system_test

Owns terminal/manual-gated integrated validation only. No implementation/publication/infrastructure task depends on a system-test task.

## Data Model

The task files own exact Prisma syntax. The canonical target semantics are:

```text
BillingPlan
  id
  shopifyPlanHandle UNIQUE, immutable after creation
  name
  kind: FREE | PAID_METERED
  active
  shopifyUsageEventHandle?                // normal recovery meter; required PAID_METERED
  freeLifetimeConversationAllowance?      // required FREE; base is initially 5
  includedRecoveryConversationAllowance?  // operational mirror for paid included->topup->overage routing
  recoveryCreditPackEnabled
  recoveryCreditsPerPack?
  shopifyRecoveryCreditPackEventHandle?   // distinct top-up meter; monetary price lives in Shopify
  defaultOutboundSoftLimit
  defaultOutboundHardLimit
  terminalMessageReservedSlots

ShopEntitlementCounter
  shopId
  counter: FREE_RECOVERY_LIFETIME | PURCHASED_RECOVERY_CREDITS
  grantedQuantity                         // used by purchased credits; Free uses base+adjustments
  committedQuantity
  reservedQuantity
  version
  UNIQUE(shopId, counter)

UsageReservation
  shopId/counter/sourceKey UNIQUE/quantity
  status: RESERVED | COMMITTED | RELEASED | AMBIGUOUS
  committedUsageEventId? UNIQUE

UsageEvent
  shopId / billingPeriodId?
  metric: RECOVERY_CONVERSATION |
          OUTBOUND_AUTOMATED_MESSAGE |
          DELIVERED_WHATSAPP_MESSAGE |
          RECOVERY_CREDIT_PACK_PURCHASE
  quantity non-zero Decimal; negative corrections allowed
  idempotencyKey UNIQUE
  sourceType/sourceId/occurredAt
  correctionOfUsageEventId?
  shopifyReportState: NOT_APPLICABLE | PENDING | IN_FLIGHT | RETRYABLE | REPORTED | NEEDS_ATTENTION
  shopifyEventHandle?
  shopifyIdempotencyKey? UNIQUE
  attempt/due/result fields

RecoveryCreditPurchase
  id                               // merchant request identity
  shopId / planId?
  shopifyPlanHandleSnapshot
  shopifyEventHandleSnapshot
  creditsGranted
  status: PENDING_BILLING | ACTIVE | NEEDS_ATTENTION | CANCELLED
  usageEventId UNIQUE
  activatedAt?

Conversation
  existing recovery link remains unchanged
  shopId? / customerId?            // standalone ownership
  standaloneScopeKey? UNIQUE       // active standalone product/support scope only
  inboundVersion / lastProcessedVersion
  lastInboundAt / lastMessageAt
  pendingTurnStartedAt?
  processingInboundVersion?
  processingStartedAt?

PlatformBillingPolicy / ShopBillingPolicyOverride
  global/shop pause dimensions
  finite outbound hard/soft safety bounds
  platform absolute hard ceiling dominates tenant overrides

BillingAllowanceAdjustment
  shopId
  counter: FREE_RECOVERY_LIFETIME
  signed non-zero quantity
  reason/admin/timestamp
  append-only; reversal is another signed row

BillingAuditEvent
  typed action + actor/reason + bounded before/after snapshots
```

The effective Free allowance is `BillingPlan.freeLifetimeConversationAllowance + SUM(BillingAllowanceAdjustment.quantity)`. Historical committed/reserved quantities remain truthful if the effective allowance is later lowered.

Audit JSON does not reintroduce JSON-driven entitlement logic. Runtime entitlement/limit fields remain typed columns/relations.

## Contracts

Cross-repository contracts owned by `@modainteract/moda-interact-shared` include at minimum:

- typed billing plan kinds and usage metrics used by more than one repository, including the post-0.7.4 `RECOVERY_CREDIT_PACK_PURCHASE` addition published by SHARED-006;
- merchant billing SYSTEM message codes;
- normalized Meta provider message-status event schema/version used by Messaging producer and Background consumer;

Provider-status v2 canonical runtime shape (introduced by SHARED-003/004 after MESSAGING-001 review exposed the invalid v1 tenant-routing assumption):

```text
schemaVersion: 2
providerAccountId       // Meta entry.id / WABA identity
providerPhoneNumberId   // Meta metadata.phone_number_id
providerMessageId       // Meta outbound message/status id
status                  // SENT | DELIVERED | READ | FAILED
occurredAt              // provider timestamp normalized to ISO datetime
pricing?                // bounded billable/category/model metadata only
```

`shopId` is deliberately absent. Messaging cannot derive a trustworthy Moda tenant from the signed raw webhook without database state. Background resolves the local outbound message by `providerMessageId` and derives the owning shop from durable local state. Provider identities must never be used to guess a different tenant.
- deterministic bounded source/idempotency-key helpers where identities cross repositories;
- any shared billing-operation DTO actually transferred across runtime boundaries.

Do not duplicate a shared schema as a local `type`/Zod schema after the shared release is available.

## Consistency and Transactions

- Free and purchased-credit reservations use Prisma transactions plus version/CAS counter semantics with bounded retry on conflict.
- Reservation commit/release is idempotent by deterministic source identity and terminal status.
- Positive normal paid recovery UsageEvent is created at most once by deterministic recovery identity.
- A recovery covered by purchased credits creates internal recovery usage with `NOT_APPLICABLE` Shopify state and never duplicates the normal paid meter.
- One recovery-credit purchase request creates one pack UsageEvent and one purchase row; activation increments granted purchased capacity exactly once.
- App Event publication occurs after business transactions and cannot roll them back.
- Publisher claims are conditional so horizontally scaled workers cannot concurrently treat one pending row as independently owned.
- The publisher is report-state/event-handle driven, not hard-coded to one metric, so normal recovery, corrections and pack-purchase events can share it.
- Conversation turn processing uses a conversation-scoped lease; it never globally serializes unrelated conversations.
- Ambiguous external-provider outcomes retain state that prevents unsafe duplicate side effects until reconciled.
- Corrections are append-only compensating events.

## Ordering

- Do not globally serialize billing or WhatsApp processing.
- Free/purchased counter conflicts are scoped to the hot shop/counter only.
- WhatsApp response ordering and CommerceAgent processing are conversation-scoped.
- Raw inbound fragments for one conversation settle for 3 seconds, with a 10-second maximum window, then one claimed turn processes the current version.
- A newer inbound arriving during agent execution invalidates the stale response; it is persisted and processed in the next turn.
- Different conversations remain independently concurrent.
- App Event ordering is not a correctness substitute for idempotency; each event is independently durable and keyed.
- Subscription reconciliation is shop-scoped and idempotent.

## Failure Handling

- Partner API transport/GraphQL failure != no subscription.
- Unknown plan mapping => `UNMAPPED`/fail closed; never guess Free/Starter/Growth/Scale.
- First event-endpoint 401 may perform one controlled generation-aware token refresh/retry. Token endpoint 401/403, event 403, or a second event 401 are definitive configuration/needs-attention outcomes.
- App Event timeout/5xx => retry same permanent idempotency key with bounded backoff.
- Definitive configuration/current-period/meter failures => `NEEDS_ATTENTION`, not infinite retry.
- Recovery-credit purchase billing failure grants zero credits; a later successful retry may activate exactly once.
- Meta definitive failure before successful initial recovery => release Free/purchased reservation; no committed recovery usage.
- Meta ambiguous outcome => preserve durable ambiguous state; do not blindly release/re-send.
- Provider-status webhook tenant identity is resolved in Background from durable local outbound state; Messaging never fabricates `shopId`.
- Redis/queue failure after durable DB state leaves enough DB state for reconciliation workers/scans to recover work.
- Global/shop pause is safe and reversible; it must not corrupt counters or historical usage.
- A lowered Free effective allowance below historical committed/reserved usage yields zero remaining capacity; historical usage is not rewritten.
- If a new inbound arrives while CommerceAgent is running, suppress the stale response and process the new settled version rather than racing two replies.

## Scalability

ARCH-007 does not change the reference Shopify ingress scale (~20,000 events/minute). Billing work belongs on the **action path**, not the raw Shopify ingress hot path. Only events that become recoveries/messages incur billing-policy work.

Key scaling rules:

- no Partner/App Events call for every raw Shopify webhook;
- local subscription/policy lookups must be indexed and bounded;
- Free CAS conflicts are scoped to a hot shop, not global;
- billing publisher processes bounded batches/pages with worker concurrency/backoff;
- usage/reconciliation queries require shop/state/due-time indexes;
- one hot tenant must not globally block other shops;
- provider rate limits/backpressure must grow queue lag rather than corrupt billing state.

## Security

- Shopify Partner and App Events credentials remain server-side only.
- App Events `attributes` must contain no customer-identifying data; billing events require only bounded operational scalars such as `value`.
- Admin plan/policy/billing mutations require server-side PlatformAdmin authorization; platform-hard-limit/plan-catalog/correction operations are SUPER_ADMIN-only unless a task explicitly defines a narrower safe ADMIN permission.
- Every financially sensitive Admin mutation writes a durable BillingAuditEvent.
- Tenant merchant UI only reads its own subscription/usage and cannot see Admin operational/reconciliation data.

## Observability

Reuse approved shared structured logging and existing OpenTelemetry/framework signals. Add custom billing telemetry only for Moda-specific outcomes not derivable from generic HTTP/BullMQ instrumentation, for example:

- recovery billing admission allowed/denied reason and capacity source (Free / purchased / normal paid);
- Free reservation conflict/exhaustion;
- billing App Event report success/retry/needs-attention;
- recovery-credit purchase requested/reported/activated/needs-attention;
- conversation-turn coalescing fragments/settle latency/stale-response suppression;
- inbound abuse admission allow/deny counts by bounded stage/reason, without phone/message-content metric labels;
- subscription unmapped/sync error;
- reconciliation discrepancy;
- outbound safety cap reached/terminal response used;
- billing worker due backlog/oldest due event where not already obtainable from approved queue instrumentation.

Do not emit secrets, authorization headers or customer payloads. Observability backend failure must never break billing correctness or business processing.

## Rollout / Development Reset

Classification: **PRE-PRODUCTION / BREAKING ROLLOUT**.

- `moda-interact-database` edits the canonical Prisma schema directly.
- Every ARCH-007 database schema task creates a normal Prisma migration through the repository's Prisma migration workflow and regenerates normal database artifacts (Prisma client plus ERD artifacts).
- Migration SQL may be destructive to disposable development billing data; do not add production-style data backfills, dual-read compatibility or legacy adapters.
- Development databases may be reset/recreated as needed while generating/applying the migration.
- Any repository seed/fixture made invalid by the schema change must be updated in the same database task so a normal development reset remains usable.
- Consumer repositories adopt the developer-published accepted database revision/submodule and regenerate Prisma client; do not use raw SQL because a consumer is on an old generated client.
- Shared contract implementation is published before consumer tasks that import it.
- No theoretical backwards-compatibility adapters are required.

Recommended implementation order is encoded by task dependencies. Developer/user owns git commit/push publication after architect acceptance.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-007-DATABASE-001 | moda_database | Complete | - |
| ARCH-007-DATABASE-002 | moda_database | Complete | DATABASE-001 |
| ARCH-007-DATABASE-003 | moda_database | Complete | DATABASE-002 |
| ARCH-007-DATABASE-004 | moda_database | Complete | DATABASE-003 |
| ARCH-007-DATABASE-005 | moda_database | **Ready — Changes Requested; next claim Attempt 2** | DATABASE-004 |
| ARCH-007-DATABASE-006 | moda_database | Pending | DATABASE-005 |
| ARCH-007-SHARED-001 | moda_shared | Complete | DATABASE-003 |
| ARCH-007-SHARED-002 | moda_shared | Complete | SHARED-001 |
| ARCH-007-SHARED-003 | moda_shared | Complete | SHARED-002 |
| ARCH-007-SHARED-004 | moda_shared | Complete | SHARED-003 |
| ARCH-007-SHARED-005 | moda_shared | Pending | DATABASE-005 |
| ARCH-007-SHARED-006 | moda_shared | Pending | SHARED-005 |
| ARCH-007-SHOPIFY-001 | moda_app | Complete | SHARED-002, DATABASE-003 |
| ARCH-007-SHOPIFY-002 | moda_app | **Ready — Changes Requested, next claim Attempt 2** | SHOPIFY-001 |
| ARCH-007-SHOPIFY-003 | moda_app | **Ready** | SHOPIFY-001 |
| ARCH-007-SHOPIFY-004 | moda_app | Pending | SHOPIFY-002, DATABASE-005, SHARED-006, ADMIN-005 |
| ARCH-007-MESSAGING-001 | moda_messaging | **Complete (Attempt 3)** | SHARED-002, SHARED-004 |
| ARCH-007-BACKGROUND-001 | moda_background | Complete | SHARED-002, DATABASE-003 |
| ARCH-007-BACKGROUND-002 | moda_background | Complete | BACKGROUND-001 |
| ARCH-007-BACKGROUND-003 | moda_background | Complete | BACKGROUND-002, SHOPIFY-001 |
| ARCH-007-BACKGROUND-004 | moda_background | Complete | BACKGROUND-003, DATABASE-004 |
| ARCH-007-BACKGROUND-005 | moda_background | **Ready** | BACKGROUND-004, MESSAGING-001, SHARED-004 |
| ARCH-007-BACKGROUND-006 | moda_background | Complete | SHARED-002, DATABASE-002 |
| ARCH-007-BACKGROUND-007 | moda_background | Complete | BACKGROUND-003, BACKGROUND-006 |
| ARCH-007-BACKGROUND-008 | moda_background | Pending | BACKGROUND-005, BACKGROUND-007, BACKGROUND-009, SHOPIFY-001 |
| ARCH-007-BACKGROUND-009 | moda_background | Pending | DATABASE-005, SHARED-006, BACKGROUND-007 |
| ARCH-007-BACKGROUND-010 | moda_background | Pending | DATABASE-006, BACKGROUND-004 |
| ARCH-007-BACKGROUND-011 | moda_background | Pending | BACKGROUND-010 |
| ARCH-007-ADMIN-001 | moda_admin | **Ready** | SHARED-002, DATABASE-003 |
| ARCH-007-ADMIN-002 | moda_admin | Pending | ADMIN-001 |
| ARCH-007-ADMIN-003 | moda_admin | Pending | ADMIN-002, BACKGROUND-007, SHOPIFY-001 |
| ARCH-007-ADMIN-004 | moda_admin | Pending | ADMIN-003, BACKGROUND-008 |
| ARCH-007-ADMIN-005 | moda_admin | Pending | ADMIN-001, DATABASE-005, SHARED-006 |
| ARCH-007-GATEWAY-001 | moda_gateway | Pending | BACKGROUND-008 |
| ARCH-007-SYSTEM-TEST-001 | moda_system_test | Pending / manual-gated | SHOPIFY-002, BACKGROUND-003, ADMIN-002 |
| ARCH-007-SYSTEM-TEST-002 | moda_system_test | Pending / manual-gated | SHOPIFY-002, BACKGROUND-008, ADMIN-004, GATEWAY-001 |
| ARCH-007-SYSTEM-TEST-003 | moda_system_test | Pending / manual-gated | SHOPIFY-003, MESSAGING-001, BACKGROUND-005, BACKGROUND-008, ADMIN-004, GATEWAY-001 |
| ARCH-007-SYSTEM-TEST-004 | moda_system_test | Pending / manual-gated | SHOPIFY-004, BACKGROUND-009, BACKGROUND-008, ADMIN-005 |
| ARCH-007-SYSTEM-TEST-005 | moda_system_test | Pending / manual-gated | BACKGROUND-010, BACKGROUND-004, BACKGROUND-011 |

Individual task YAML is authoritative for execution state. System tests are terminal/manual-gated and must never block implementation/publication/infrastructure work.

The current architect-accepted and published Shared release is `@modainteract/moda-interact-shared@0.8.0`. It contains the accepted `RECOVERY_CREDIT_PACK_PURCHASE` metric from SHARED-005/006.

## Current execution frontier

Snapshot synchronized 2026-09-08 after SHOPIFY-003 Attempt 1 architect review:

```text
READY
  SHOPIFY-003
    SAME Changes Requested task; next claim Attempt 2
    restore accepted Shared 0.7.4 dependency baseline only

  ADMIN-001 Attempt 1
  BACKGROUND-005 Attempt 1
  BACKGROUND-009 Attempt 1
  BACKGROUND-010 Attempt 1

CROSS-ARCHITECTURE READY
  ARCH-005-SHOPIFY-004 Attempt 1

ACCEPTED COMPLETE
  DATABASE-001/002/003/004/005/006
  SHARED-001/002/003/004/005/006
  SHOPIFY-001/002
  MESSAGING-001 Attempt 3
  BACKGROUND-001/002/003/004/006/007

DEPENDENCY GATED
  ADMIN-001 -> ADMIN-002
  ADMIN-001 + DATABASE-005 + SHARED-006 -> ADMIN-005
  ADMIN-002 + BACKGROUND-007 + SHOPIFY-001 -> ADMIN-003
  ADMIN-003 + BACKGROUND-008 -> ADMIN-004

  BACKGROUND-005 + BACKGROUND-007 + BACKGROUND-009 + SHOPIFY-001
    -> BACKGROUND-008
    -> GATEWAY-001

  BACKGROUND-010
    -> BACKGROUND-011 inbound abuse admission
    -> SYSTEM-TEST-005 (terminal/manual-gated)

  ADMIN-005 + SHOPIFY-002 + DATABASE-005 + SHARED-006
    -> SHOPIFY-004

SYSTEM TESTS
  SYSTEM-TEST-001..005 remain Pending / manual-gated.
```

Current architect-accepted/published Shared release is `@modainteract/moda-interact-shared@0.8.0`.
The SHOPIFY-003 correction deliberately restores its previously accepted consumer baseline to 0.7.4 rather than opportunistically consuming the pack-contract release.

## Open Questions

The following are configuration/product-tuning values, **not architecture blockers**:

- exact recovery-credit pack quantity or quantities offered to merchants;
- exact pack monetary price/rate on Free, Starter, Growth and Scale in Shopify App Pricing (higher paid tiers are intended to receive preferential rates);
- initial per-plan automated outbound soft/hard caps;
- platform absolute outbound hard cap and warning percentage;
- optional daily shop/global safety ceilings;
- whether a future independent `COMMERCE_AGENT_TURN`/token budget is needed in addition to outbound reservation. It is not required by the current architecture.

The current subscription/overage targets are agreed product values, not open questions:

```text
Free    $0       5 lifetime recoveries   no automatic overage
Starter $35/mo   200/month               $0.05/recovery overage
Growth  $75/mo   500/month               $0.04/recovery overage
Scale   $149/mo  1,200/month             $0.03/recovery overage
```

The base Free lifetime allowance is 5. A specific test/support shop may have a different **effective** allowance only through signed audited `BillingAllowanceAdjustment` rows; this does not change the canonical Free plan for other shops.

## Change History

- 2026-09-08 — full workspace state synchronization: restored previously accepted BACKGROUND-001, BACKGROUND-006, MESSAGING-001, SHOPIFY-001 and SHARED-002 task records that had drifted; recorded DATABASE-005/006, SHARED-005/006, SHOPIFY-002, BACKGROUND-004/007 acceptances; current Shared is 0.8.0; BACKGROUND-009 and BACKGROUND-010 are Ready; SHOPIFY-003 is actively claimed Attempt 1; ARCH-005-SHOPIFY-004 is Ready; BACKGROUND-011 remains Pending behind BACKGROUND-010.

- 2026-09-08 — BACKGROUND-011 created: add two-stage inbound WhatsApp abuse admission for the single public Moda number. Raw sender/global rolling limits run before tenant/DB routing; settled-turn sender/conversation/shop/global limits run after BACKGROUND-010 coalescing and before outbound reservation/CommerceAgent. Abuse state is operational Redis state, not merchant billing. SYSTEM-TEST-005 is extended to validate coalescing plus abuse admission.

- 2026-09-08 — BACKGROUND-004 Attempt 2 actively claimed after DATABASE-004 acceptance; current durable task state is `in_progress` under `copilot`. Domain index/handoff reconciled without resetting the claim.
- 2026-09-08 — DATABASE-004 Attempt 1 architect-accepted Complete: nullable standalone shop/customer ownership, unique active standalone scope identity, bounded indexes and the named scope CHECK invariant are verified. BACKGROUND-004 returns to Ready for Attempt 2 and DATABASE-005 becomes Ready.

- 2026-09-07 — ARCH-007 initiated for Free/Basic Shopify billing.
- 2026-09-07 — Agreed conversation as merchant-facing usage unit and automated outbound message as internal safety/cost unit.
- 2026-09-07 — Shopify App Events usage billing moved into first implementation.
- 2026-09-07 — Added Admin plan mapping, platform/shop safety controls, allowance adjustments, billing operations and reconciliation.
- 2026-09-07 — Classified rollout as pre-production/breaking; Prisma-first/no-new-runtime-raw-SQL invariant added.
- 2026-09-07 — Clarified database workflow during DATABASE-001 review: normal Prisma migration artifacts and regenerated DB artifacts are required even in development; migrations need not preserve disposable development billing data, and stale seed/fixtures must be corrected in the schema task.
- 2026-09-07 — Task decomposition made deliberately fine-grained and deterministic for GPT-5.6 Luna repository agents.
- 2026-09-07 — DATABASE-002 Attempt 2 architect-accepted after correcting seed usage/reporting semantics, rerunnable counter/reservation cleanup, and bounded stale-report/correction-link indexes; DATABASE-003 unblocked Ready.
- 2026-09-07 — DATABASE-003 architect-accepted after review of typed platform/shop billing policy, allowance-adjustment and audit persistence, normal Prisma migration, bounded indexes and deletion-safety semantics; ARCH-007 database foundation completed and SHARED-001 unblocked Ready.
- 2026-09-07 — SHARED-001 Attempt 6 architect-accepted after implementing exact six-code compile-time typing, lifecycle-scoped merchant SYSTEM source keys, independent message-contract version semantics, and focused regression coverage; SHARED-002 publication gate unblocked Ready.
- 2026-09-07 — SHARED-002 architect-accepted after successful publication of `@modainteract/moda-interact-shared@0.7.3` and developer correction of repository lock metadata to the same version; Shopify, Messaging, Background policy/App-Events, and Admin plan-catalog frontiers unblocked Ready.

- 2026-09-07 — SHOPIFY-001 Attempt 1 changes requested: Partner classification was implemented against a stale pre-ARCH-007 database consumer schema, so Attempt 2 must adopt DATABASE-003 and persist the canonical typed projection before acceptance.

- 2026-09-07 — MESSAGING-001 Attempt 1 architect-blocked after direct review and Meta payload verification showed Shared provider-status v1 incorrectly required `shopId`. Added SHARED-003/004 for strict provider-status v2 (`providerAccountId`, `providerPhoneNumberId`, `providerMessageId`, no `shopId`) and moved tenant resolution to Background durable state.

- 2026-09-07 — BACKGROUND-001 Attempt 1 changes requested: effective policy must expose new-recovery and automated-WhatsApp pause controls independently, terminal reserved slots must be positive and below the effective hard cap, typed BillingPeriod status must be preserved, and the task-specified fail-closed/override/pause regression coverage must be completed.

- 2026-09-07 — SHOPIFY-001 Attempt 2 changes requested: DATABASE-003 adoption and typed projection are now correct; Attempt 3 is limited to replacing four stale `PAID` BillingPeriod consumer checks with `CLOSED`, fail-closing billing callback success to verified mapped current/pending plan state, and adding the missing paid-success/callback/period regressions.

- 2026-09-07 — SHARED-003 architect-accepted Complete: provider-status schema v2 uses WABA/phone-number/message provider identities and deliberately carries no `shopId`. SHARED-004 is Ready to publish exact Shared `0.7.4`; MESSAGING-001 remains Blocked until publication acceptance.

- 2026-09-07 — BACKGROUND-001 Attempt 2 architect-accepted Complete: typed independent pause dimensions, bounded pause reasons, terminal reserved-slot safety, typed BillingPeriod status and the requested fail-closed/override/pause regressions are complete. BACKGROUND-002 is Ready.
- 2026-09-08 — BACKGROUND-002 Attempt 2 architect-accepted Complete: concurrent duplicate-source P2002 replay, bounded retry exhaustion, explicit Free `NOT_APPLICABLE` usage state, and allowance-reduction counter safety are verified. BACKGROUND-003 is Ready because SHOPIFY-001 is already Complete.

- 2026-09-08 — SHARED-004 architect-accepted Complete after exact `@modainteract/moda-interact-shared@0.7.4` publication and clean-consumer verification; provider-status v2 is now consumable. MESSAGING-001 is no longer contract-blocked and is currently in architect review on Attempt 2.
- 2026-09-08 — SHOPIFY-002 remains Changes Requested / Ready for Attempt 2; a separate ARCH-005 Shopify i18n-completion task is dependency-gated behind SHOPIFY-002 because both edit merchant-support UI and locale catalogues.

- 2026-09-07 — SHOPIFY-001 Attempt 3 architect-accepted Complete: the typed Shopify current/pending commercial projection is stable, historical BillingPeriod consumers use `CLOSED`, and billing callback success is fail-closed to verified mapped current/pending Partner state. SHOPIFY-002 is Ready.

- 2026-09-08 — MESSAGING-001 Attempt 3 architect-accepted Complete after adding realistic Meta webhook extraction regression; provider-status v2 tenant routing is now complete and BACKGROUND-005 waits only on BACKGROUND-004.
- 2026-09-08 — BACKGROUND-003 Attempt 2 architect-accepted Complete after correcting definitive-vs-ambiguous provider handling, stable Free-exhaustion lifecycle identity and integrated Free/paid admission regressions.
- 2026-09-08 — BACKGROUND-006 Attempt 2 architect-accepted Complete after generation-aware concurrent 401 recovery and definitive token/event authentication classification; BACKGROUND-007 is Ready.
- 2026-09-08 — BACKGROUND-004 Attempt 1 architect-blocked: its automated-message counter was shop-wide instead of per conversation, and non-recovery paths lacked stable durable conversation identity. DATABASE-004 added as prerequisite; BACKGROUND-004 stays the same task and returns for Attempt 2 after DATABASE-004 acceptance.
- 2026-09-08 — Product policy expanded from the original Free/Basic sketch to the initial data-driven Free/Starter/Growth/Scale pricing catalogue plus repeatable recovery-credit packs for every plan. Paid capacity order is included -> purchased -> overage; Free is lifetime -> purchased -> block. Pack monetary prices remain Shopify-authoritative.
- 2026-09-08 — Added fragmented inbound-message turn coalescing: persist every raw message, 3-second quiet/10-second maximum settling, one CommerceAgent processor per conversation, outbound reservation before AI, stale response suppression when a correction arrives during processing.
- 2026-09-08 — Confirmed per-shop Free testing/support overrides use the already-accepted signed `BillingAllowanceAdjustment` ledger and Admin controls; no test-shop environment bypass is introduced.
- 2026-09-08 — Added DATABASE-005/006, SHARED-005/006, ADMIN-005, SHOPIFY-004, BACKGROUND-009/010 and SYSTEM-TEST-004/005; BACKGROUND-008 now waits for BACKGROUND-009 so the independent billing worker integrates pack activation/reconciliation into the target architecture.
- 2026-09-08 — Reconciled canonical ARCH-007, domain indices, pricing documentation and ARCH-005 Shopify i18n coordination into durable repository state; temporary overlay/amendment files are historical transport artifacts only.
