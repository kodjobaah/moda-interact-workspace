---
id: ARCH-045
title: Shopify WhatsApp customer-phone consent synchronisation and reconciliation gating
status: proposed
coordinator: moda_architect
created: 2026-10-20
updated: 2026-10-21
---

# ARCH-045 — Shopify WhatsApp consent and normal checkout reconciliation

## Status

**Proposed; documentation-only portable definitions.** Based on `moda-interact-workspace(20261020-130224).zip`, ARCH-045 Attempt 1 and subsequent agreed ARCH-045/046 consent-model corrections. The developer's live branches/worktrees are not inspected, created or pushed here. The current amendment removes consent-triggered checkout recovery wakeups, not the Shopify-to-Moda *consent-state synchronisation* required for `commerce.CustomerPhone`.

## Problem

An abandoned Shopify checkout must not create a `CheckoutRecovery` or initiate WhatsApp outreach before valid consent for the **actual customer and recipient phone** is established. Creating a blocked `CheckoutRecovery` conflates an abandoned checkout with an authorised recovery. Conversely, re-evaluating old checkouts whenever a customer changes consent would add a separate scheduling and retention mechanism without an established requirement.

Shopify is authoritative for its native WhatsApp marketing preference. Moda requires an up-to-date shop/customer/phone-scoped **local current-state projection** on existing `commerce.CustomerPhone`, because ordinary checkout reconciliation should read the customer's latest consent when it runs. Shopify's Customer Privacy API for analytics/tracking is not proof of WhatsApp marketing opt-in.

## Goals

1. Add a cross-platform WhatsApp recovery consent decision to the existing `CustomerPhone` model through one owner, `ARCH-045-DATABASE-002`. No default grant and no consent table for Shopify.
2. On an authenticated Shopify WhatsApp consent-change webhook, reliably enqueue a **minimal sync signal**; Background fetches Shopify's **current** state, validates shop/customer/exact phone and updates the local phone record. The webhook never starts, reschedules or creates a checkout recovery.
3. During **ordinary** checkout creation/update/candidate maturation and reconciliation, resolve the correct customer/phone, evaluate the latest phone consent (refreshing from Shopify when absent or uncertain), and create `CheckoutRecovery` only when otherwise eligible and authorised.
4. If there is no verified consent, create **no recovery, attempt, credit reservation/charge or WhatsApp message**; write at most one idempotent, checkout-keyed merchant Support notice, distinguishing no consent from temporary verification failure.
5. Revalidate Shopify authority before proactive outbound sends, including existing-recovery follow-ups, to prevent stale local state or delayed/reordered webhooks authorising a send after withdrawal.
6. Preserve normal checkout eligibility/retention and outbound idempotency. There is no 72-hour consent expiration, consent-wait recovery, new checkout index, consent-triggered checkout scan or separate recovery wake-up queue.

## Non-Goals

- New CMP, tracking banner, theme app block or pixel for this WhatsApp-only initiative.
- Reading generic marketing, tracking or email/SMS flags as permission for WhatsApp recovery.
- Re-evaluating **all** abandoned checkouts immediately when consent changes, or guaranteeing recovery without a subsequent ordinary checkout reconciliation event.
- New `WHATSAPP_CONSENT_MISSING` `RecoveryAdmissionBlockReason`, `DETECTED` consent-wait recovery, expiry job, dedicated consent-to-recovery queue or consent-specific outbox table.
- Trusting a Shopify webhook's stale status as authority or merging customers by phone number.

## Current Architecture — inspected snapshot

- `commerce.Customer` is shop-scoped, with `shopifyCustomerId`, and `commerce.CustomerPhone` contains customer/phone identity but **no WhatsApp consent fields**. `ARCH-045-DATABASE-002` adds them; `ARCH-045-DATABASE-001` remains Superseded as the obsolete admission enum proposal.
- `moda-interact` authenticated webhook ingress publishes typed `@modainteract/moda-interact-shared/shopify` jobs to existing BullMQ queues. Only checkout/cart/order/discount topics are currently normalised; there is no current WhatsApp consent-sync event handling. Therefore a minimal shared sync-event type is required for the existing pipeline, **not** a new queue/service or a checkout recovery wakeup.
- `checkout-event-orchestrator.service.ts` can schedule a new candidate after a subsequent checkout update if no recovery exists. `pending-recovery-candidate.worker.ts` cleans up its candidate index when maturation completes. No periodic rediscovery of consent-ineligible checkouts has been demonstrated.
- `recovery-materialization.service.ts` resolves current checkout and recipient before `RecoveryInitiationService` persists/initiates recovery; that is the pre-creation gate. Existing sequence-two and merchant post-window recovery follow-ups require a fresh send-side gate.
- Existing `MerchantSupportMessage.sourceKey` supports checkout-keyed idempotent merchant notices without creating a recovery or notice table.

## Proposed Architecture

### A. One customer-phone projection, Shopify remains authoritative

`CustomerPhone` stores the current WhatsApp checkout-recovery consent state (default unknown/not granted), authority/source, source timestamp and local verification time for the **exact shop-owned customer and active normalised phone**. The database schema is shared with ARCH-046. A Shopify-native grant is never inferred from a phone, cookie preference, SMS flag, checkout event or Woo consent record. When phone/customer ownership changes, an old grant does not transfer.

`ARCH-045-BACKGROUND-001` provides an injectable policy reader/synchroniser. For Shopify it resolves `(shopId,shopifyCustomerId,recipient)` against Shopify Admin GraphQL's current `whatsAppMarketingConsent` and exact `defaultPhoneNumber`; writes the current validated decision to the corresponding CustomerPhone, with monotonic source version/timestamp handling. Local `GRANTED` is an eligibility input for normal reconciliation, not permission to override a later `UNSUBSCRIBED` result. Unknown/ambiguous state and unavailable authority always fail closed.

### B. Consent change updates the phone — nothing more

1. Shopify authenticates `customers_whats_app_marketing_consent/update` and publishes a minimal, deduplicated **sync** signal via existing webhook queues and the published Shared event schema. No consent Boolean, phone number or checkout ID is trusted in that signal.
2. Background consumes the sync signal, obtains Shopify's **current** phone and consent for the authenticated customer/shop and safely updates an existing active CustomerPhone, or creates an appropriately linked active phone for an already verified shop-owned Customer. Duplicates/out-of-order signals are harmless; older observations cannot overwrite a newer decision.
3. If Moda has no safely linked Customer yet, the event does not invent a customer by phone number, create a checkout reference or queue a recovery. For an existing verified Customer, a newly observed Shopify default phone may be added as its own active CustomerPhone with unknown/default-deny semantics before updating the verified consent. An ordinary future checkout reconciliation can resolve and refresh that customer from Shopify.
4. **Stop.** No checkout lookup, pending-candidate creation, merchant Support notice or recovery job is produced by the consent-change handler.

### C. Ordinary checkout reconciliation remains the only new-recovery trigger

1. An existing checkout/cart/update event schedules or refreshes its normal pending candidate. The matured candidate retrieves current provider checkout/order state and verified customer/recipient.
2. Before `RecoveryInitiationService` creates a recovery, evaluate current active CustomerPhone consent. On unknown/uninitialised state, refresh with Shopify before an initial grant can be accepted. A valid exact-phone `SUBSCRIBED` result is needed; denial or unverifiable state creates **no** recovery.
3. A verified negative state produces one existing merchant Support `SYSTEM` message keyed by shop+checkout+reason (not recovery ID). A provider outage is reported differently and remains fail-closed/retryable under existing bounded error handling.
4. A subsequent **ordinary** reconciliation of the same still-eligible checkout reads the **then-current** CustomerPhone state, revalidates provider checkout and consent, and can create a first recovery. If no subsequent event/reconciliation occurs, consent change **alone will not** revive the earlier checkout; this is an accepted boundary, not a missing consent wakeup.
5. Existing recoveries' proactive follow-ups use the same consent policy, with a fresh Shopify authority check as close to provider dispatch as practical; preserve no-double-charge and compensation behaviour.

## Request / Event Flow

```text
Shopify consent-change webhook
  -> Shopify authenticated ingress
  -> existing BullMQ pipeline, published minimal sync job
  -> Background Shopify current-consent query
  -> validated commerce.CustomerPhone update
  -> STOP (no recovery/checkout wakeup)

Later normal checkout reconciliation event
  -> normal candidate scheduling / checkout maturity and paid-state checks
  -> verified customer + exact CustomerPhone consent
  -> live Shopify verification where necessary and pre-send fence
      |- not granted / unknown / unavailable: no CheckoutRecovery; checkout-keyed Support notice as appropriate
      `- granted, still eligible: existing first-recovery materialisation path
```

## Repository Responsibilities

| Repository / owner | Bounded responsibility |
|---|---|
| `moda-interact-database` / `moda_database` | `ARCH-045-DATABASE-002` defines reusable current phone consent fields/constraints; no new Shopify consent table |
| `moda-interact-shared` / `moda_shared` | `ARCH-045-SHARED-001/002` define and publish **consent-sync** signal on an **existing** Shopify queue, not a recovery wakeup/second queue |
| `moda-interact` / `moda_app` | Authenticate, normalise, enqueue consent-update sync; merchant guidance uses Shopify-native consent facilities |
| `moda-interact-background` / `moda_background` | Shopify consent refresh to CustomerPhone, pre-materialisation checks, checkout-keyed notices and proactive send gates; no consent-driven checkout rediscovery |
| `moda-interact-system-test` / `moda_system_test` | Terminal black-box tests for sync, subsequent normal reconciliation, suppression, merchant notice and billing |

## Data Model / Contracts

- Reuse `commerce.Customer` and existing `commerce.CustomerPhone`; the cross-platform schema is owned by **`ARCH-045-DATABASE-002`**. New current consent fields default to unknown/unverified; record source/provider timestamp and verification metadata, and Woo's source epoch where applicable. No new Shopify consent table or initial-consent `CheckoutRecovery` enum.
- No second consent authority: Shopify Admin GraphQL is authoritative for Shopify; CustomerPhone is its validated local current-state projection and must be refreshed where staleness would authorise a send.
- Existing `MerchantSupportThread` and `MerchantSupportMessage` persist checkout-keyed idempotent notices with bounded safe text.
- A minimal versioned event (contract `ARCH-045-SHARED-001`; publication `SHARED-002`) carries only `{schemaVersion,shopId,shopifyCustomerId,deliveryId,triggeredAt}`. Its *sole* business effect is current CustomerPhone sync. It uses an existing Shopify BullMQ ingress/consumer infrastructure and distinct job type; the checkout event parser must not misinterpret it as a checkout. This is a cross-repository sync contract, **not a consent-triggered recovery queue**.
- Producer: `moda-interact`; consumer: `moda-interact-background`; validation: published `@modainteract/moda-interact-shared/shopify` runtime schema. No new checkout candidate or deferred recovery schema.

## Consistency, Ordering and Failure Handling

- Webhook duplicates are idempotent; older Shopify observations never supersede newer consent states. Re-read current provider state instead of trusting webhook order, with bounded GraphQL timeout/retry.
- A failed Shopify sync may leave local state stale; a fresh authoritative Shopify check is required before **outbound** business-initiated WhatsApp dispatch and can refresh CustomerPhone. Unavailable verification means no send and no charge.
- Current phone status cannot be joined across shops/customers by phone alone; old number grants are not inherited on change. An unmatched webhook is no recovery trigger.
- Normal checkout candidate/index cleanup is unchanged. No consent-only retries aimed at checkout rediscovery or new pending-reference retention. The next ordinary checkout event is the only new-recovery opportunity under this architecture.
- Any failure while inserting the merchant notice must be independently repairable/idempotent without fabricating a recovery; avoid exposing customer PII in notice source keys or logs.

## Scalability / Security / Observability

- High-volume Shopify event ingress remains short: authenticate -> validate -> durably accept sync event -> acknowledge. Shopify GraphQL and CustomerPhone updates occur in Background. No shop-wide scans, customer-phone scans, extra recovery scheduler, separate queue or unbounded backlogs.
- Emit bounded structured outcome fields (`consent_sync`, `consent_not_verified`, `recovery_not_created`, `notice_written`, `outbound_consent_rejected`) using `@modainteract/moda-interact-shared/logging`. Never log full phone numbers, Shopify tokens, customer payloads, consent text or secrets.
- Tenant isolation, safe current-shop sessions, exact customer and recipient verification, no other tenant access, provider failure isolation and existing BullMQ observability are mandatory. Reuse standard telemetry rather than duplicating framework signals.

## Rollout / Migration

- The real deployment status is not established from the supplied snapshot; use an additive backward-compatible migration unless developer evidence confirms an isolated pre-production cutover.
- Implement `ARCH-045-DATABASE-002`; independently implement and accept `SHARED-001`, then publish `SHARED-002`. Background consent reader/sync uses the migrated CustomerPhone model; Shopify ingress uses published Shared package. Consent synchronisation may start without recovering old checkouts.
- Complete Background pre-materialisation gate and follow-up gate; permit manual validation before terminal system test. Old queue messages are unaffected; no second queue and no consent-wait recovery migration.
- Do **not** implement superseded `ARCH-045-DATABASE-001`. If it was independently implemented/deployed in the real worktree, architect must reconcile that fact; this portable snapshot does not undo a migration.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-045-DATABASE-001 | moda_database | **superseded** | — |
| ARCH-045-DATABASE-002 | moda_database | **ready** | — |
| ARCH-045-SHARED-001 | moda_shared | ready | — |
| ARCH-045-SHARED-002 | moda_shared | pending | SHARED-001 |
| ARCH-045-SHOPIFY-001 | moda_app | pending | SHARED-002 |
| ARCH-045-SHOPIFY-002 | moda_app | ready | — |
| ARCH-045-BACKGROUND-001 | moda_background | pending | DATABASE-002 |
| ARCH-045-BACKGROUND-002 | moda_background | pending | BACKGROUND-001 |
| ARCH-045-BACKGROUND-003 | moda_background | pending | DATABASE-002, BACKGROUND-001, SHARED-002, SHOPIFY-001 |
| ARCH-045-BACKGROUND-004 | moda_background | pending | BACKGROUND-001, BACKGROUND-002 |
| ARCH-045-SYSTEM-TEST-001 | moda_system_test | pending | all applicable implementation + SHARED-002 publication |

## Open Questions / Explicit Boundaries

1. **Accepted product behaviour:** a consent update does not itself locate/retry an earlier checkout. Without a later ordinary reconciliation event, no new recovery is guaranteed. Do not add a polling scheduler or durable checkout reference to claim otherwise.
2. No 72-hour customer consent lifetime. Customer consent validity and normal checkout recovery eligibility are different concerns.
3. Existing provider/API versions and active app configuration/scope must be rechecked at implementation claim. Verify the exact Shopify customer/phone/consent field path on the selected API version.
4. A webhook for a customer not yet linked to a Moda `CustomerPhone` cannot safely create a relationship by phone number; later normal reconciliation may initialise the projection from Shopify.
5. Customer-phone evidence and source epoch for WooCommerce are defined by ARCH-046; the single current-state schema lives in ARCH-045-DATABASE-002.

## External Provider References (baseline verification 2026-10-20)

- Shopify CustomerPhoneNumber and WhatsApp marketing consent API (Admin GraphQL 2026-07 or verified later version).
- Shopify `customers_whats_app_marketing_consent/update` webhook and mandatory webhook authentication.
- Meta WhatsApp business-initiated opt-in/opt-out requirements, independently from Shopify tracking consent.

## Change History

- 2026-10-20: Initial proposal with blocked recovery and 72-hour consent wait; withdrawn.
- 2026-10-20: No `CheckoutRecovery` without consent, no 72-hour consent limit, checkout-keyed merchant notice.
- 2026-10-21: Customer-owned `CustomerPhone` current consent, updated on Shopify native consent changes. **Next normal checkout reconciliation** reads current state; consent sync never initiates a recovery. Add database schema task ARCH-045-DATABASE-002; retain only minimal Shared cross-repository sync contract on an existing queue, no recovery wakeup.
