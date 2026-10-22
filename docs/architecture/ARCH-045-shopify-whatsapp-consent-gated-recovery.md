---
id: ARCH-045
title: Shopify native WhatsApp consent and normal checkout recovery admission
status: proposed
coordinator: moda_architect
created: 2026-10-20
updated: 2026-10-22
---

# ARCH-045 — Shopify WhatsApp consent-gated recovery

## Status

**Proposed; implementation in progress across repositories.** The canonical task files mark `ARCH-045-DATABASE-002`, `SHARED-001`, `SHARED-002`, `BACKGROUND-001`, and `SHOPIFY-002` Complete. Three dependencies have been reconciled for execution: `SHOPIFY-001` and `BACKGROUND-005` are Ready (as is the cross-initiative `ARCH-046-BACKGROUND-001`). Developer task branches/report evidence are recorded, but this snapshot does not prove merges into `main` or integrated production acceptance. The architecture is **not Implemented** until the remaining implementation and terminal system tests pass.

## Problem

Shopify can record native WhatsApp marketing consent. Moda must check that native permission for the correct Shopify customer and exact recipient before creating a `CheckoutRecovery` or sending business-initiated WhatsApp outreach. An unauthorised abandoned checkout is not itself a recovery. Shopify's Customer Privacy tracking preferences do not constitute WhatsApp messaging opt-in.

## Goals

1. Project current consent onto **existing `commerce.CustomerPhone`**, whose customer belongs to an existing `Customer.shopId`; Shopify is still the live source of truth.
2. On authenticated Shopify WhatsApp-consent change, use the existing queue pipeline to synchronise current CustomerPhone. No consent-change event triggers checkout recovery, scanning or rescheduling.
3. During **ordinary** checkout reconciliation, obtain live Shopify native consent for exact shop/customer/phone when necessary; **no verified opt-in → no recovery row, message, credit charge or recovery attempt**. Write one idempotent, checkout-keyed merchant Support notice for confirmed missing permission, and distinguish verification failures.
4. Treat abandoned-checkout/basket proactive WhatsApp outreach as **Marketing** (including initial reminders, scheduled follow-ups and merchant post-window recovery templates); use approved Meta **Marketing** templates. For **each distinct new checkout** call Shopify's current WhatsApp consent API once at first-recovery admission and project the native decision to CustomerPhone. Follow-up sends and first-send reentries use **stored CustomerPhone consent/no-contact**, not repeated Shopify API reads. Every proactive send uses the existing final short SQL consent/revision fence. Genuine customer-initiated in-window service replies retain their own rules.
5. Use published Shared canonical phone + Shopify numeric/GID identity helpers, preserve tenant isolation and reject stale or ambiguous decisions.
6. Reuse Database-002 for current phone state, with **one new `commerce.WhatsAppConsentEvidence` audit table for Woo-originated decisions**. Shopify does not need a separate audit table; native Shopify consent remains authoritative.

## Non-Goals

- Consent Management Platform, app block, cookie banner, pixel, or tracking/marketing consent beyond the WhatsApp recovery purpose.
- Data-export, customer erasure, privacy fences, permanent recollection bans, or changing historical customer deletion workflows. Those were previously discussed but are **outside the explicitly agreed consent architecture** and are not silently transferred to DATABASE-002.
- A Woo checkout identity table, new Customer principal columns, WooInstallation consent settings, recipient reachability schema changes, or third-party plugin adapters.
- A consent-triggered recovery queue, guaranteed later re-evaluation, fabricated 72-hour consent expiry, consent-blocked CheckoutRecovery row, or customer phone match that silently grants permission.

## Current Architecture

The inspected snapshot has a shop-scoped `Customer` with optional `shopifyCustomerId`, existing `CustomerPhone`, authenticated Shopify webhook ingress and BullMQ checkout workers. Candidate maturation currently removes its transient index after completion. `RecoveryInitiationService` persists a recovery before some existing admission checks; ARCH-045 must introduce a **pre-insert** consent gate and cover other initial-send and proactive send entry points. Merchant system notices use existing `MerchantSupportMessage` deduplication. DATABASE-002 is marked Complete, with its report describing the reduced CustomerPhone + WhatsAppConsentEvidence schema. Previous speculative identity/erasure/provider proposals were excluded from the accepted database task scope; no implementation merge to `main` is established by this snapshot.

## Proposed Architecture

### Shopify consent synchronisation

- `SHOPIFY-001` authenticates `customers_whats_app_marketing_consent/update`, converts customer ID with Shared's strict Shopify identity helper and publishes minimal, versioned **consent-sync** event through the existing queue.
- `BACKGROUND-003` consumes the event and refreshes native consent from Shopify's current GraphQL data before updating current CustomerPhone. Duplicate, reordered and stale updates cannot regrant after later withdrawal/STOP.
- No checkout candidate, recovery, merchant notice or billing action is initiated merely because consent changes.

### Normal reconciliation and sending

1. Ordinary checkout activity/candidate maturation resolves the correct shop and Shopify customer identity; Shopify-specific resolution must not attach a foreign Shopify customer solely because phones match.
2. Use the current exact canonical phone and Shopify's WhatsApp consent API (authoritatively refreshed where required). If not verified GRANTED, **do not create CheckoutRecovery**; if confirmed absent, notify the merchant with existing Support mechanism.
3. On valid consent, ordinary checkout eligibility (unpaid/abandoned/mature, entitlement, idempotency, customer phone and local no-contact) still applies before first creation.
4. The new checkout's native Shopify consent verification updates CustomerPhone (`SUBSCRIBED`→`GRANTED`; absent/revoked→non-granted), with distinct fail-closed handling for unavailable provider responses. After recovery creation, read **only stored** consent and no-contact state before proactive sends and recheck durable revisions in the short SQL fence. A missed webhook can leave Shopify consent stale locally until sync or a new checkout; do not claim per-send Shopify verification. No network calls are made inside SQL transactions.
5. A later consent grant alone only updates CustomerPhone. Re-evaluation occurs **only if another normal checkout event/reconciliation runs**; there is no guaranteed rediscovery of previously discarded candidates.

### Cross-platform data rule

`CustomerPhone` is the only stored current permission projection. `Customer` already carries `shopId`; `Shop.platform` identifies Shopify/WooCommerce. For Woo checkout capture, one unambiguous `(shopId, canonicalPhone)` match may locate an existing Customer/CustomerPhone; no match can create an ordinary customer/phone and ambiguous duplicates must be denied. **Finding a matching phone does not mean consent was granted.** Only validated Shopify-native permission or a deliberate authenticated Woo checkbox action writes GRANTED. No separate Woo session-identity table is required.

### Abandoned-basket Marketing and inbound STOP

- Abandoned-cart/basket recovery reminders are **direct marketing** (not ordinary order confirmations). Initial, scheduled and post-window merchant recovery templates must be **Meta-approved Marketing-category** templates. Existing `WhatsAppTemplateVariant` in the inspected code records recovery purpose and approval status but **not** Meta category; a verified provider category source is a release requirement. Unknown/non-Marketing categories fail closed; this consent initiative does not add fields to DATABASE-002 merely to invent category evidence.
- **Quoted STOP** referring to a reliably identifiable merchant outbound message: set no-contact on all active matching canonical-number CustomerPhones **within that merchant**. **Standalone STOP**, or a STOP with an unresolvable quoted message: set no-contact on **every currently registered merchant** having that canonical phone. Do not infer a single merchant from recent conversation activity or create an unbounded global suppression table. No record means no invented future-merchant block.
- Apply local STOP first, before background routing ignores the inbound. The local `CustomerPhone.whatsappNoContact` restriction is authoritative for **every outbound WhatsApp send** to each affected shop/phone, including automated, merchant/human and in-window service replies; it is never cleared by Shopify API reads, Shopify consent webhooks, merchant re-enable actions or ordinary Woo checkout consent updates. Shopify is **not written to** when STOP arrives, so `write_customers`, a Shopify unsubscribe mutation and remote STOP retries are outside ARCH-045. Notify **each affected merchant** through an idempotent Moda Support SYSTEM notice; do not send a WhatsApp acknowledgement to the stopped number.
- Merchant recovery suppression is separate from customer consent and STOP. **Every outbound WhatsApp send** for an affected shop/phone is denied while local STOP is active, including legitimate customer-initiated in-window service replies. Such replies retain their existing non-Marketing classification, but STOP still blocks delivery.

**Reference policy:** Meta's WhatsApp abandoned-cart recovery guidance (https://whatsappbusiness.com/blog/shopping-cart-recovery-seasonal-sales/) and WhatsApp Business Messaging Policy (https://whatsappbusiness.com/policy/) treat this outreach as marketing and require opt-in/opt-out handling. UK ICO direct-marketing guidance: https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-direct-marketing-using-electronic-mail/.

## Request / Event Flow

```text
Shopify native consent change -> authenticated Shopify ingress
  -> existing BullMQ sync event -> Background refresh from Shopify
  -> CustomerPhone current state update -> STOP (no recovery)

Ordinary checkout reconciliation -> exact Shopify customer + phone
  -> native WhatsApp consent verification
    |- not granted: no CheckoutRecovery; checkout-keyed merchant notice
    |- unavailable: no CheckoutRecovery; technical failure, not denial
    `- granted: checkout eligibility -> first recovery; pre-send checks
```

## Repository Responsibilities

- **Database:** `ARCH-045-DATABASE-002` supplies `CustomerPhone` consent columns and **one** new `commerce.WhatsAppConsentEvidence` audit table (for Woo data). No changes to Customer, WooInstallation, reachability or privacy erasure schema.
- **Shared:** combined `ARCH-045-SHARED-001` owns minimal sync message and canonical IDs/phone utilities; separate `SHARED-002` publishes them.
- **Shopify app:** authenticated read-only consent-change webhook and concrete merchant Recovery Settings guidance; native consent changes remain in Shopify Admin. No duplicate Moda merchant opt-out control.
- **Background:** current Shopify consent reader/synchroniser, pre-creation admission, first/follow-up send gates and inbound STOP handling.
- **System test:** terminal verification after implementation and separate acceptance/manual validation.

## Data Model / Contracts

- `Customer.shopId` supplies merchant identity; `CustomerPhone` supplies canonical active recipient, current UNKNOWN/GRANTED/REVOKED, provenance, verification time/revision and local STOP/merchant suppression.
- `commerce.WhatsAppConsentEvidence` holds **Woo Moda-checkbox history only in v1**, is not consulted for Shopify permission or used as a recovery worklist.
- Sync signal: `{schemaVersion,shopId,shopifyCustomerId,deliveryId,triggeredAt}`; owner `ARCH-045-SHARED-001`; produced by Shopify app and consumed by Background through published `@modainteract/moda-interact-shared` runtime validator.
- The existing `MerchantSupportThread`/`MerchantSupportMessage` handles checkout-keyed merchant notices. `WhatsAppRecipientReachability` remains unchanged and delivery-focused.

## Consistency, Ordering and Failure Handling

- Shop scope is mandatory. Multiple active CustomerPhones resolving to the same shop/phone must not be arbitrarily merged or authorise outreach.
- Shopify's current observed state updates the **native consent decision** when a new checkout is checked or a consent-sync webhook arrives. A direct WhatsApp STOP is immediately recorded as a separate authoritative local no-contact restriction that no Shopify consent response or webhook can clear. A Shopify `SUBSCRIBED` response (even one recorded after STOP) updates **only** the native consent decision; effective sending remains prohibited. A merchant may clear only merchant-owned suppression, not customer STOP or grant customer opt-in. Any future STOP removal requires a separate, explicitly authorised and verified customer request to Moda; no automatic release mechanism belongs to these initiatives.
- No Redis or Shopify/Meta API within SQL transactions; no optimistic claim of exactly-once webhook processing.
- Reconciliation may not run after later opt-in; the system makes no guaranteed automatic recovery promise.

## Security and Observability

Authenticate Shopify webhook and admin API, validate Shopify customer numeric/GID conversion, enforce shop scope, exact international recipient and customer-local STOP. Use the approved Shared logger, bounded non-PII event outcomes and existing queue metrics. No new gateway/topology or custom generic telemetry is required merely for this initiative.

## Rollout / Migration

DATABASE-002 is marked Complete following acceptance of its task-branch schema/migration and validation; do not assume that completion merged its gitlink to `main`. The accepted/published Shared package is version `2.5.0` per task report; each consumer must adopt the required published version and deploy in a compatible order before Shopify/Background readers and writers are released. Preserve production-compatible sequencing if this functionality has already shipped. Only when all required consent tests pass may consent-gated sending be considered release-ready. No `docs/decisions/**/_index.md` amendments until architect/developer explicitly ends the session.

## Decisions / Tasks

| Task | Owner | Status | Depends on |
|---|---|---|---|
| `ARCH-045-DATABASE-001` | `moda_database` | superseded | — |
| `ARCH-045-DATABASE-002` | `moda_database` | complete | — |
| `ARCH-045-DATABASE-003` | `moda_database` | superseded | — |
| `ARCH-045-SHARED-001` | `moda_shared` | complete | — |
| `ARCH-045-SHARED-002` | `moda_shared` | complete | `ARCH-045-SHARED-001` |
| `ARCH-045-SHARED-003` | `moda_shared` | superseded | — |
| `ARCH-045-SHOPIFY-001` | `moda_app` | ready | `ARCH-045-SHARED-002` |
| `ARCH-045-SHOPIFY-002` | `moda_app` | complete | — |
| `ARCH-045-SHOPIFY-003` | `moda_app` | superseded | — |
| `ARCH-045-SHOPIFY-004` | `moda_app` | superseded | — |
| `ARCH-045-SHOPIFY-005` | `moda_app` | superseded | `ARCH-045-DATABASE-002` |
| `ARCH-045-BACKGROUND-001` | `moda_background` | complete | `ARCH-045-DATABASE-002`, `ARCH-045-SHARED-002` |
| `ARCH-045-BACKGROUND-002` | `moda_background` | pending | `ARCH-045-BACKGROUND-001`, `ARCH-045-BACKGROUND-005` |
| `ARCH-045-BACKGROUND-003` | `moda_background` | pending | `ARCH-045-DATABASE-002`, `ARCH-045-BACKGROUND-001`, `ARCH-045-SHARED-002`, `ARCH-045-SHOPIFY-001` |
| `ARCH-045-BACKGROUND-004` | `moda_background` | pending | `ARCH-045-BACKGROUND-001`, `ARCH-045-BACKGROUND-002`, `ARCH-045-BACKGROUND-005` |
| `ARCH-045-BACKGROUND-005` | `moda_background` | ready | `ARCH-045-DATABASE-002` |
| `ARCH-045-SYSTEM-TEST-001` | `moda_system_test` | pending | `ARCH-045-DATABASE-002`, `ARCH-045-SHARED-002`, `ARCH-045-SHOPIFY-001`, `ARCH-045-SHOPIFY-002`, `ARCH-045-BACKGROUND-001`, `ARCH-045-BACKGROUND-002`, `ARCH-045-BACKGROUND-003`, `ARCH-045-BACKGROUND-004`, `ARCH-045-SHARED-001`, `ARCH-045-BACKGROUND-005` |

## Open Questions

- Verify deployed Shopify protected-customer-data access and exact native WhatsApp consent API behavior before relying on the provider at send admission.
- No consent-driven replay is authorised; if guaranteed later recovery becomes a separate product requirement, it needs a new architectural decision.

## Change History

- 2026-10-20: Initial Shopify consent-gated checkout recovery and native collection proposal.
- 2026-10-21: Rejected consent-blocked CheckoutRecovery and a 72-hour wait; moved to normal reconciliation with customer-phone state.
- 2026-10-21: Consolidated Database and Shared tasks; removed third-party Woo consent-source selection.
- 2026-10-21: **Consent-only scope correction.** Database-002 is one new WhatsAppConsentEvidence table plus CustomerPhone consent fields; Shopify remains provider-authoritative. General privacy export/erasure work is excluded from these initiatives. Woo may resolve Customer by a unique merchant-scoped canonical phone without auto-granting consent.
- 2026-10-22: Architect coordination reconciled completed task reports, readiness frontier, and ARCH-046 terminal system-test Support dependencies without changing runtime source or architecture completion state.
