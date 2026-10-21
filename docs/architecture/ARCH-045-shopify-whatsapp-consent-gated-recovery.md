---
id: ARCH-045
title: Shopify WhatsApp consent-gated recovery, merchant notice and later-consent re-evaluation
status: proposed
coordinator: moda_architect
created: 2026-10-20
updated: 2026-10-20
---

# ARCH-045 — Shopify WhatsApp consent-gated recovery

## Status

**Proposed; portable definitions, not implemented or materialised.** Baseline: `moda-interact-workspace(20261020-130224).zip` plus ARCH-045 Attempt 1. This amendment **supersedes** the proposed consent-specific `CheckoutRecovery` admission reason and arbitrary 72-hour wait. No claim is made that the user's live task branches have been inspected or reconciled. Scope remains business-initiated Shopify WhatsApp checkout recovery, merchant notice and possible later opt-in.

## Problem

The existing checkout recovery materialisation path resolves the recipient then initiates a recovery without first checking Shopify's *current WhatsApp marketing consent*. Creating a `CheckoutRecovery(status=DETECTED)` merely to record that no consent exists confuses an abandoned checkout with an authorised recovery workflow. It also creates artificial cleanup/expiry work and requires an unnecessary enum migration.

Shopify's Customer Privacy API governs storefront tracking, **not** the channel-specific permission needed for WhatsApp outreach. Shopify Admin GraphQL `Customer.defaultPhoneNumber.whatsAppMarketingConsent`, checked against the exact recipient, is the proposed read-only consent authority. The webhook `customers_whats_app_marketing_consent/update` (Shopify API 2026-07) is a re-evaluation trigger, not consent proof.

## Goals

1. Gate **recovery creation** for initial proactive WhatsApp outreach: check live Shopify `SUBSCRIBED` state for the actual shop, verified Shopify customer and exact canonical recipient **before calling the service that persists `CheckoutRecovery`**. Missing, revoked, mismatched or unverifiable consent creates **no CheckoutRecovery, no outreach attempt, no credit reservation/consumption, no provider send**.
2. Notify the merchant once per identifiable unconsented checkout via the **existing Support inbox**, with an idempotent checkout-based `MerchantSupportMessage.sourceKey`. Distinguish *not verified/not granted* from *verification temporarily unavailable*; no false accusation that the shopper refused.
3. On a later Shopify consent-change event, attempt **fresh checkout re-evaluation** using an existing, still-addressable checkout candidate or authoritative checkout lookup, confirmed customer/checkout identity, current consent and normal abandoned-checkout eligibility. **Create a recovery for the first time** only if every gate passes. A customer consent event by itself never creates a recovery.
4. Keep customer consent and checkout lifetime separate: **no 72-hour consent period, consent-wait deadline, consent-specific terminal status or consent-driven expiry job**. Current Shopify consent remains authoritative until changed or otherwise invalid. Checkout re-evaluation is bounded by the platform's *existing* checkout availability, abandonment/eligibility rules and normal processing retention, not an invented consent TTL.
5. Re-check current consent before each later proactive sequence-two or merchant post-window WhatsApp recovery template; preserve existing recipient suppression, capacity/credits, outreach idempotency, Meta 24-hour customer-service rules and human control.
6. Protect tenant/customer/recipient isolation, webhook duplicates, race conditions, API failures and merchant data privacy, using the shared structured logger.

## Non-Goals

- Treating Customer Privacy API tracking/cookie consent, email or SMS opt-in as WhatsApp recovery permission; adding app blocks, CMP banners or custom pixels.
- Storing a second authoritative Shopify consent Boolean in Moda's database, or fabricating a grant from a phone number.
- Sending an unsolicited opt-in request to the customer or allowing merchant manual bypass.
- Introducing a `WHATSAPP_CONSENT_MISSING` recovery admission reason, a `DETECTED` recovery waiting for consent, an artificial consent-expiry clock, or a new generic recovery engine.
- Promising resumption of an abandoned checkout that cannot be safely rediscovered. A consent record alone is **not** a checkout index.

## Current Architecture — inspected snapshot

- `moda-interact-background/src/services/checkout-recovery/recovery-materialization.service.ts` evaluates a matured `PendingRecoveryCandidate`, checks order status, resolves fresh checkout and recipient, then calls `initiate(seed,generation,recipient)`. Consent must be checked **between recipient resolution and that call**, with a final pre-provider check after materialisation only for authorised recoveries.
- `recovery-initiation.service.ts` persists/updates `CheckoutRecovery` and handles suppression, sequence-one admission and billing. It is **too late** to first decide whether a recovery should exist if admission is checked only after its upsert.
- `PendingRecoveryCandidate` and Redis/BullMQ indexes are transient; `candidate-lifecycle.service.ts` can cancel/remove an indexed candidate. The snapshot does **not** prove that an evaluated, unconsented checkout remains discoverable indefinitely. BACKGROUND-002/003 must verify viable bounded checkout reference retention/re-discovery and state limitations rather than invent a 72-hour hold or claim guaranteed later resumption.
- `Customer` and `CustomerPhone` already model shop customer and phone identity. Shopify's consent record stays **at Shopify**; Moda customer linkage is used for safe checkout correlation only.
- `CheckoutRecovery` has `admissionBlockReason` for *existing recoveries* blocked by capacity/suppression, not for never-authorised recovery candidates. `MerchantSupportThread` and `MerchantSupportMessage.sourceKey` already support merchant notices without adding another table.
- Shopify app webhook ingestion uses authenticated routes and Shared contracts; `customers_whats_app_marketing_consent/update` is not currently subscribed. Scheduled and human post-window recovery follow-ups are independent proactive send paths.

## Proposed Architecture

### A. Current Shopify consent, customer and phone

- Inject `WhatsAppRecoveryConsentReader` returning `allowed | not-authorised | verification-unavailable` from Shopify Admin GraphQL, requiring the shop-linked Shopify customer ID and exact canonical phone. Only current `SUBSCRIBED` for the same `Customer.defaultPhoneNumber` passes. `PENDING`, `NEVER_SUBSCRIBED`, `UNSUBSCRIBED`, `REDACTED`, unknown, missing or mismatched identities fail closed; API/session failures are unavailable, not grants.
- Do not add consent fields/tables for Shopify on `Customer`/`CustomerPhone`; do not use those models to override Shopify's current response. Use them only for safe `(shopId,shopifyCustomerId)` and recipient matching.

### B. No initial recovery without consent

1. Normal candidate maturation, shop eligibility, current abandoned-checkout/order recheck and phone resolution run under existing checkout-scoped coordination.
2. Before `RecoveryInitiationService.upsertRecovery`, read live WhatsApp consent. An unavailable read must defer/retry boundedly without manufacturing a customer opt-out; an explicit negative/unknown result must **not** create a `CheckoutRecovery` or outreach attempt.
3. Persist one Support SYSTEM notice keyed to the **shop + checkout identity** (using a deterministic bounded hashed source key, not `<recoveryId>`). Notice insertion is independently idempotent and repairable. Do not store customer PII in the notice or log.
4. Retain/re-discover only the minimal checkout identity required by existing checkout candidate or authoritative checkout lookup **while it remains legitimately actionable**. Do not create a consent-wait recovery, perpetual Redis job, unrelated new table or custom 72-hour timer. Explicitly test behaviour when the normal candidate is consumed and cannot be found later; if reliable correlation needs a new durable retention capability, return that architectural gap for approval instead of silently making a permanent wakeup store.
5. On a successful later re-evaluation, create **one new recovery generation by the existing ordinary creation path** and then apply normal attempt/credit/provider idempotency. A consent event must never resurrect a terminal recovery for an already processed checkout.

### C. Later consent-change event and existing recoveries

- Shopify webhook ingress authenticates, validates and durably enqueues the published Shared customer-ID-scoped wakeup, without GraphQL lookup or sending in HTTP. Background resolves **only safely linked** checkout references for `(shopId,shopifyCustomerId)`, re-reads live Shopify consent, independently verifies current checkout unpaid/abandoned status, recipient, maturity, shop entitlement and suppressions, then re-enters normal **pre-materialisation** checks.
- If a checkout is no longer identifiable, accessible, eligible, or was completed/cancelled, do nothing; do not search all shops or match by phone alone. Ordinary subsequent Shopify checkout updates may provide another legitimate opportunity. No promise of unconditional automatic resumption is made for an unavailable checkout.
- For recoveries that **already exist because consent was verified previously**, withdrawal prevents subsequent proactive templates; preserve existing recovery history and provider/billing reconciliation.

## Request / Event Flow

```text
authenticated Shopify checkout event -> PendingRecoveryCandidate -> mature checkout + phone
  -> current Shopify WhatsApp consent?
       allowed       -> ordinary first CheckoutRecovery creation -> credit/provider admission
       not authorised -> no CheckoutRecovery -> idempotent Support notice
       unavailable   -> no CheckoutRecovery -> bounded retry, operational error

Shopify customer WhatsApp consent update -> authenticated Shared wakeup
  -> find verifiably linked, still-addressable checkout -> fresh eligibility + consent
  -> if allowed and still abandoned: create CheckoutRecovery once, otherwise no-op
```

## Repository Responsibilities

| Repository | Ownership |
|---|---|
| `moda-interact-database` | **No new Shopify consent migration**; ARCH-045-DATABASE-001 superseded |
| `moda-interact-shared` | v1 WhatsApp consent-change wakeup contract and separate publication gate |
| `moda-interact` | authenticated Shopify consent webhook subscription/producer and merchant setup guidance |
| `moda-interact-background` | Shopify consent reader, **pre-materialisation** gate, merchant Support notice, safe candidate wakeup, proactive follow-up gates |
| `moda-interact-system-test` | terminal integrated merchant/customer/credit evidence |

## Data Model / Contracts

- **Consent authority:** Shopify; not stored in a parallel Moda consent table.
- **Customer linkage:** existing `Customer(shopId,shopifyCustomerId)` and exact phone; no phone-only guest permission. **Checkout evidence:** existing checkout identity/candidate or fresh verified provider lookup, not `CheckoutRecovery` when no consent.
- **Merchant notice:** existing `MerchantSupportMessage`, unique `sourceKey` derived from shop+checkout+reason (bounded/hash as needed). Avoid recovering from a notice row alone: it is an informational artefact, not a source of checkout state.
- **Wakeup event:** Shared `ShopifyWhatsAppConsentChangedJobV1Schema` v1: `{schemaVersion,shopId,shopifyCustomerId,deliveryId,triggeredAt}`; producer Shopify app; consumer Background. Event contains no consent state or phone and never authorises a send.
- **No new enum:** `ARCH-045-DATABASE-001` is `superseded`, with dependencies removed from active tasks. Existing admission reasons remain unchanged.

## Consistency, Ordering and Failure Handling

- Checkout-scoped coordination, order-completion fences, recipient snapshots, existing unique recovery generation/attempt identities and pre-provider consent recheck prevent ordinary duplicates. Shopify consent webhook order is not trusted; always re-read current state.
- If Shopify API fails at first admission: **no recovery creation or billing**, bounded retry/recheck. Do not confuse unavailable provider data with a deliberate customer refusal when notifying merchants.
- Merchant Support notices are idempotent by checkout key. Notification write failure cannot enable a send and must be reparable without creating a recovery.
- A completed/expired/unretrievable checkout cannot be revived just because consent changed. Consent **does not expire after 72 hours**; the independently existing checkout/recovery lifecycle governs eligibility. No extra consent-expiry repair job is introduced.
- Pre-provider opt-out races may require existing credit release/compensation if a provisional reservation was made after initial consent verification. A withdrawal after irreversible Meta dispatch cannot unsend the message.

## Scalability / Security / Observability

- Consent checks occur for actionable checkout creation and proactive outbound sends, not all ~20,000/minute *total* Shopify ingress events. Customer-event wakeups use bounded customer-linked candidate lookup and normal Shopify rate limits; no unbounded tenant scan or new service.
- HMAC/session validation and customer/shop identity linkage precede processing. `read_customers` for read-only Shopify API access; no `write_customers` needed. No raw phone, emails, access tokens or complete event bodies in shared logs.
- Emit bounded semantic `recovery.consent.checked`, `recovery.consent.skipped_before_creation`, `recovery.consent.notice`, `recovery.consent.wakeup_recheck` outcomes via `@modainteract/moda-interact-shared/logging`. Reuse approved standard HTTP/BullMQ telemetry; provider/logging failures do not change consent policy.

## Rollout / Migration

- Verify actual deployed state before classifying rollout. No ARCH-045 schema migration is required under the revised model. Safe order: Shared contract implementation and publication; Background reader and pre-materialisation/merchant notice protection; Background wakeup/follow-up consumers; Shopify webhook registration/producer and merchant guidance; independent system test. Coordinate provider consumer-first availability for rolling deployments.
- If ARCH-045-DATABASE-001 was **already materialised or executed** outside the supplied portable baseline, reconcile the real task/branch and migration with the architect before reverting or marking it superseded; this patch does **not** remove any runtime migration.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-045-DATABASE-001 | moda_database | **superseded** | — |
| ARCH-045-SHARED-001 | moda_shared | ready | — |
| ARCH-045-SHARED-002 | moda_shared | pending | SHARED-001 |
| ARCH-045-SHOPIFY-001 | moda_app | pending | SHARED-002 |
| ARCH-045-BACKGROUND-001 | moda_background | ready | — |
| ARCH-045-BACKGROUND-002 | moda_background | pending | BACKGROUND-001 |
| ARCH-045-BACKGROUND-003 | moda_background | pending | SHARED-002, SHOPIFY-001, BACKGROUND-002 |
| ARCH-045-BACKGROUND-004 | moda_background | pending | BACKGROUND-001, BACKGROUND-002 |
| ARCH-045-SHOPIFY-002 | moda_app | pending | BACKGROUND-002 |
| ARCH-045-SYSTEM-TEST-001 | moda_system_test | pending | SHARED-002, SHOPIFY-001/002, BACKGROUND-001/002/003/004 |

System tests are terminal only; there is no implementation task depending on SYSTEM-TEST-001. Statuses represent **portable definition eligibility**, not claims of developer task execution or architect acceptance.

## Open Questions / Explicit Boundaries

1. **No 72-hour consent window.** Provider consent validity and checkout eligibility/retention are separate. The snapshot proves candidate indexes are transient; BACKGROUND-002/003 must document actual eligible candidate retention or safe provider rediscovery before promising reliable later-consent re-evaluation.
2. Guest/phone-only Shopify records cannot be joined to another customer's consent webhook by phone. No guessed customer ID, fake checkout persistence or unbounded waiting.
3. The active deployed Shopify app TOML must be verified because the snapshot includes differing app configs. Current Admin GraphQL schema/scope must be verified by implementation owner.

## External Provider References (baseline verification 2026-10-20)

- Shopify Admin GraphQL 2026-07 [`CustomerPhoneNumber`](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/CustomerPhoneNumber) — WhatsApp marketing consent state read.
- Shopify [WhatsApp marketing consent availability](https://shopify.dev/changelog/posts/whatsapp-marketing-consent-now-available) and [2026-07 webhooks](https://shopify.dev/docs/api/webhooks/2026-07).

## Change History

- 2026-10-20: Consent-model correction — initial recovery exists **only after verified consent**; merchant notice references checkout; Shopify remains source of truth; removed invented 72h window and ARCH-045-DATABASE-001 enum migration.
- 2026-10-20: Initial proposed consent-blocked recovery with 72h delay (superseded by above correction).
