---
id: ARCH-046
title: WooCommerce customer-phone WhatsApp opt-in, merchant notices and later checkout re-evaluation
status: proposed
coordinator: moda_architect
created: 2026-10-20
updated: 2026-10-21
---

# ARCH-046 — WooCommerce WhatsApp consent-gated recovery

## Status

**Proposed; portable canonical definitions, not materialised, claimed or implemented.** Baseline: 2026-10-20 workspace snapshot; ARCH-046 Attempts 1 and 2. Woo ARCH-035 remains **capture-only**: the future recovery-admission tasks stay `blocked` pending separately approved checkout-state/recovery implementation. This amendment replaces checkout-scoped consent projection, three new model proposal and 72-hour recovery waiting state with **customer/phone consent** and **no CheckoutRecovery until eligible**.

## Problem

WooCommerce has no universal Shopify-style WhatsApp marketing-consent authority or change webhook. A customer's opt-in must survive checkout abandonment, belong to the verified **customer and exact phone**, and remain effective for the stated purpose until revoked, superseded/invalidated or otherwise no longer valid. It does not belong to a one-time `CheckoutRecovery` or automatically expire in 72 hours. Another plugin may collect consent; Moda must not render a second checkbox if an approved provider is selected, nor trust an arbitrary checkbox/cookie flag.

The supplied Woo integration currently captures checkout/order events but **does not** implement business-initiated recovery, confirmed checkout-state reads or billing. Consent capture can ship independently; actual recovery gating cannot.

## Goals

1. Give the merchant one **authoritative source setting** (`NOT_CONFIGURED`, `MODA_CHECKBOX`, `SUPPORTED_EXTERNAL`) in `WooCommerce > Moda Interact > Recovery settings`. Mode/provider/version/epoch are stored on the existing hosted `WooCommerceInstallation` record. No third-party provider is certified in the supplied snapshot: external mode remains unselectable until an approved adapter exists.
2. When `MODA_CHECKBOX` is selected, display a separate optional, initially unchecked, accessible WhatsApp checkout-recovery opt-in in Classic and Blocks, with 20-locale translations. Collect an **explicit affirmative action before order placement** on guest or logged-in checkout without interrupting purchasing if the API is offline.
3. Associate the durable current decision with existing **Moda `Customer` and its exact `CustomerPhone`**, scoped to shop + phone + `WHATSAPP_CHECKOUT_RECOVERY` purpose; record proof, source/provider, hosted configuration epoch, disclosure version, event identity/revision and grant/revoke timestamps. Do not use a checkout as the consent authority or inherit permission when the phone changes.
4. Ensure the disclosure accurately permits the intended **store-specific abandoned-checkout reminders across eligible checkouts**; sample meaning: “I agree that [store] may send WhatsApp reminders about checkouts I leave unfinished to this number. I can withdraw consent at any time.” A notice restricted to “this checkout” must **not** be used to authorise a different checkout.
5. Use **one narrowly scoped append-only Woo WhatsApp consent evidence table** for proof of each grant/withdrawal, idempotent replay and bounded later-change wakeups. The inspected 2026-10-20 schema has no suitable existing customer-consent audit/event store: `CustomerPhone` is mutable current state and `CommerceAuditEvent` is for Commerce Studio actions, not customer opt-in. This is the **only new Woo consent table**, not a second current-state projection or checkout waiting queue. If a newer canonical schema already provides equivalent guarantees, Database must report that to the architect and reuse it instead of duplicating it.
6. For a future approved Woo recovery runtime, check current consent **before creating `CheckoutRecovery`**. With no valid grant: **no recovery row, attempt, billable credit or provider send**; write at most one existing Support SYSTEM notice keyed to shop+checkout identity. A merchant mode not configured is distinct from a customer's opt-out.
7. On later explicit grant/revocation, re-evaluate only **legitimately linked, still-addressable abandoned checkouts** through the independently approved Woo checkout-state reader. If an eligible checkout remains and the exact current recipient is consented, create a recovery **for the first time**; do not resurrect an expired/paid/completed checkout. Consent has **no 72-hour timer**; checkout lifecycle controls eligibility.
8. Preserve HPOS, tenant isolation, WordPress nonce/admin capabilities, server-to-server secret handling, merchant Support read-only notices, follow-up gates, Meta recipient suppression and existing credit protection.

## Non-Goals

- Converting WP Consent API cookie/tracking choices, email marketing flags, or a generic plugin checkbox into WhatsApp opt-in; silently registering grants for other plugins.
- Automatically enabling Woo outbound recoveries as part of ARCH-035 capture-only work; a future recovery engine and authoritative live checkout/order reader must be separately approved before BACKGROUND-002/003/004 and SYSTEM-TEST-002 can run.
- Creating a current consent table for each checkout, separate merchant source-config table, `WHATSAPP_CONSENT_MISSING` enum, or consent-wait `CheckoutRecovery`.
- Treating consent as eternally usable regardless of revocation, changing purpose/phone, provider/source switching, privacy deletion or merchant policy. **No fixed 72-hour consent expiry is imposed.**
- Creating a generic third-party adapter framework or relying on unverified customer identity from a phone number alone. No unsolicited WhatsApp consent requests.

## Current Architecture — inspected snapshot

- `moda-interact-database/prisma/schema.prisma` has `Customer(shopId, shopifyCustomerId?)` and `CustomerPhone(customerId,phone,startedAt,endedAt)` with phone-history support. `WooCommerceInstallation` is already uniquely linked to `shopId`. There is **no Woo current-consent field or customer-consent audit/event record** in the supplied schema; existing Commerce Studio and administrative audit models are domain-specific and cannot prove a guest/customer checkout opt-in. The database owner must add **only necessary fields/indexes** for verified Woo account or bound guest identity and current phone consent, without fabricating a Shopify ID or matching customers by phone alone.
- `ARCH-035` Woo checkout/order work is capture-only. `woo.activity.v1` is not a live abandoned-checkout recovery state authority.
- Woo plugin's checkout opt-in UI is absent; merchant Support UI presently advertises no read capability. Existing `MerchantSupportMessage.sourceKey` can deduplicate notices without a recovery ID.
- Shopify consent remains sourced from Shopify for ARCH-045; **do not clone it** into the Woo DB fields. There is no required dependency on `ARCH-045-DATABASE-001`, which is superseded.

## Proposed Architecture

### A. One merchant consent collection source

- Extend existing hosted `WooCommerceInstallation` with `consentSourceMode`, certified external provider ID when applicable and `consentSourceEpoch` (monotonic; no-op changes do not increment). Unknown/default = `NOT_CONFIGURED`, fails closed. `ARCH-046-API-003` exclusively owns authenticated read/write and optimistic concurrency, not a new settings table.
- The merchant selects the active collector under `WooCommerce > Moda Interact > Recovery settings`; privileged WP REST proxy calls authenticated Moda API; UI shows successful configuration **only after hosted confirmation**.
- Moda renders one checkout checkbox **only** for `MODA_CHECKBOX`. A known third-party plugin may show advisory integration guidance but cannot be silently trusted. External option is unavailable until a concrete approved provider adapter verifies explicit positive action, phone, customer/session identity, disclosure and withdrawal and is integrated through the same authenticated consent API. A source switch makes old-source/epoch grants **ineligible for sends**, preserving historical proof rather than deleting it.

### B. Current consent on CustomerPhone, not the checkout

- The Woo plugin validates a logged-in Woo customer identifier or a server-bound anonymous checkout/session identity; Moda API resolves/creates a shop-owned `Customer` identity and current `CustomerPhone` row. Guest identity must remain tied to a proven checkout/session; do not merge unrelated guests by phone/email or accept an arbitrary browser-provided customer ID. Implement necessary small model fields/indexes only in `DATABASE-001`; no separate checkout customer identity table without a reviewed need.
- `CustomerPhone` holds current `GRANTED | REVOKED` (absence/unknown is not granted) for fixed purpose `WHATSAPP_CHECKOUT_RECOVERY`, with exact canonical number, source/provider/epoch, disclosureVersion, source revision, immutable event ID reference and effective timestamps. Phone changes use the new exact phone's state, **never** transfer a previous number's permission.
- One append-only Woo consent evidence/change record is **required by this inspected baseline** to preserve the original positive action/withdrawal, the exact disclosed wording or immutable version reference, timestamp, verified shop/customer/phone, collection source/epoch and replay identity. `CustomerPhone` remains the **only current-consent authority**; evidence history is not queried as a second current-state projection. In a single PostgreSQL transaction, the accepted transition updates `CustomerPhone` and inserts the unique evidence event. Identity/source checks and ordering must make retries idempotent and prevent a delayed old grant from replacing a newer revoke. An existing equivalent evidence mechanism discovered in a later canonical schema must be referred to the architect before creating a duplicate.
- Consent is a **customer-phone-purpose** decision, not a checkout-period countdown. The checkoutKey/nonce is evidence of the collection context and an identity/re-evaluation link, **not** the scope of the permission. Another checkout may use an already valid opt-in only when the same authenticated shop/customer and exact phone are safely linked and the disclosure genuinely authorises this use.

### C. Capture before abandonment, later withdrawal

- Woo Classic and Blocks checkbox use supported Woo extension points. Verify LocalWP customer/guest and pre-order persistence, not just metadata on a completed order. The plugin sends an authenticated, bounded server-to-server consent change to `ARCH-046-API-001` using current active merchant mode/epoch and server-resolved phone and customer/checkout identity. Failed send does not prevent checkout completion but **cannot count as accepted consent**.
- Initial unchecked is **no grant**, not an artificial revoke. Already verified consent for the same customer/phone may be shown as an existing subscribed preference and must offer withdrawal; never invent a new grant from pre-filled UI state. Later explicit opt-in or revocation can occur through a valid returning checkout or another verified checkout for an authenticated customer, and uses the same `CustomerPhone` identity; no new My Account preference page is required. Actual WP session expiry must be respected.

### D. Future recovery: no consent, no CheckoutRecovery

1. A **separately approved** Woo checkout recovery engine establishes an abandoned/unpaid actionable checkout, real shop/customer association, phone, maturity and eligibility. ARCH-035 capture-only events do not provide this authority.
2. Inject `WooCheckoutRecoveryConsentReader` on `(shopId, verifiedCustomerId, exactRecipient, purpose)` plus current Woo merchant source/epoch. Check **before creating** a `CheckoutRecovery` and again before each irreversible proactive provider send. Unknown, revoked, changed phone/source, API/DB outage or unsupported external provider fail closed.
3. When no grant is verified, create **no CheckoutRecovery, attempt or charge**. Add a Support notice via `MerchantSupportMessage.sourceKey` derived from `shopId + checkoutKey + reason`, not `recoveryId`. A transient verification outage is distinguishable from absent/unconfigured customer consent. No separate waiting recovery or 72-hour expiry job.
4. On a grant-change receipt, Background checks an authoritative still-addressable checkout linked to **that exact customer** (and current phone); it does not search by phone alone. Only if the normal checkout recovery eligibility window is still open, create a first recovery through the approved path, once. If checkout is gone, completed, expired or unidentifiable, no-op. Record that limitation rather than manufacture a recoverable checkout solely from a consent event.
5. For existing legitimately created recoveries, revocation/source changes prevent further proactive follow-ups; preserve historic recovery and billing/provider states. The approved engine owns normal expiry and completion rules, separate from consent validity.

## Request / Event Flow

```text
Woo checkout plugin -> verified customer + exact phone -> checked, explicit opt-in
  -> hosted Woo API auth/source check -> CustomerPhone current grant + evidence receipt
  -> no CheckoutRecovery at consent collection time

Later approved Woo abandoned-checkout evaluator -> current customer/phone consent?
  -> verified grant -> create CheckoutRecovery (normal eligibility + billing)
  -> missing/revoked/unavailable -> no recovery or charge; Support notice when appropriate

Later grant event -> bounded evidence consumer -> verified live checkout lookup
  -> eligible and current consent -> create CheckoutRecovery once
  -> no linked/eligible checkout -> no-op (consent remains until withdrawn/invalid)
```

## Repository Responsibilities

| Owner | Bounded responsibility |
|---|---|
| `moda_database` | Extend `Customer`, `CustomerPhone` and `WooCommerceInstallation`; one minimal immutable evidence/change table; migration/index/replay proofs |
| `moda_api` | authenticated customer/phone consent changes, source-mode/epoch settings and read-only Support notice API |
| `moda_woocommerce` | source selection, conditional checkbox, pre-order consent capture, later grant/revoke, Support read-only UI |
| `moda_background` | current customer-phone consent reader; later **pre-recovery** gate, notice, bounded grant-triggered checkout re-evaluation and proactive send check |
| `moda_system_test` | LocalWP consent-only certification and, after independently approved Woo recovery, full end-to-end test |

## Data Model / Contracts

- **Current state:** existing `commerce.CustomerPhone`, via verified shop-scoped `commerce.Customer`, stores the latest purpose-specific decision for the exact active recipient and source/provider/epoch. A new/different phone has no inherited grant. These Woo-specific fields must not be used as a substitute for Shopify's native consent authority. **Merchant mode:** existing `woocommerce.WooCommerceInstallation` stores source/provider/epoch; no configuration table. **Historical evidence:** one `woocommerce.WooWhatsAppConsentEvidence`-equivalent append-only table is required because the inspected schema lacks a reusable consumer-consent audit store. No checkout-specific current-consent table or separate wakeup/outbox table.
- **Immutable fact columns:** unique `(shopId,eventId)`, shop/customer/CustomerPhone foreign keys, decision `GRANT|REVOKE`, fixed `WHATSAPP_CHECKOUT_RECOVERY` purpose, canonical exact phone binding, disclosure wording/version/hash with locale and retained resolvable wording, source/provider/epoch, monotonic customer-phone revision, server-recorded time, and optional **verified** collection checkout context (not the consent owner). Personal data must be minimised and export/erasure supported. Evidence must not be overwritten on duplicate retry, source switch or later revoke.
- **Mutable delivery metadata on that same table:** a bounded, indexed wakeup state (for example `NOT_ACTIONABLE`, `READY`, leased/claimed, terminal handled), attempt count and next-attempt/claim timestamps may be updated without changing evidence facts. **Before Woo recovery is enabled, API-001 commits new evidence as `NOT_ACTIONABLE`**, retaining the audit fact but not a PENDING wakeup. Once the separately approved engine is enabled, only *new* eligible grant receipts can become `READY`; a bounded Background-003 poll/claim/ack of those records is a local database worklist, **not a new Shared Redis/BullMQ queue schema**. Terminalise retries, expire processing claims and do not delete immutable audit proof merely to clear delivery state. Evidence retention/deletion follows approved privacy policy; it does not define consent lifetime.
- API contract: authenticated versioned `woo.whatsapp-consent.v1`, shop derived from installation, verified customer or guest session binding, exact phone, source and epoch, disclosure evidence, positive/withdrawal event. Active source and identity checked atomically with update. No browser access to installation credentials.
- `MerchantSupportMessage` uses deterministic checkout-based source keys, and its read-only Woo proxy is independent from the consent DB. No `RecoveryAdmissionBlockReason.WHATSAPP_CONSENT_MISSING` dependency or Shopify Shared webhook payload in Woo.

## Consistency / Ordering / Failure Handling

- Transactional `CustomerPhone` update + one append-only evidence receipt; no synchronous Redis publication required for the consent API acknowledgement. Same `(shopId,eventId)` with identical facts is an idempotent success; the same ID with conflicting facts is rejected. Stale revision or source epoch cannot overwrite newer consent; epoch switches use installation-level optimistic concurrency/locking. Delivery metadata transitions must not mutate consent evidence.
- Without a verified current grant: zero recovery creation/send/credit. If a provider check fails before dispatch after authorised materialisation, compensate existing reservation. No attempt to undo a Meta message already sent.
- Checkout re-evaluation uses narrow checkout keys and existing business eligibility; no new 72-hour timer, checkout-wide consent projection, unsafe phone-only matching or indefinite polling. A consent grant is not proof the checkout is abandoned.
- External adapter outage and WordPress API errors never silently grant permission. WP storefront purchase can continue while hosted decision remains unknown. Merchant notice insertion is idempotent and repairable without recovery materialisation.

## Scalability / Security / Observability

- Update customer consent only on verified customer decisions, and fence source changes using installation epoch. Do not poll each Woo cart event, scan all customers by phone or scan immutable evidence for **current** permission. The eventual consumer reads a bounded indexed worklist of actionable evidence receipts, re-reads the live `CustomerPhone` and installation source, and correlates only through approved checkout identity. Consent-source read belongs close to the send boundary.
- Protect hosted API with current installation authentication and tenant identity; use WP admin capabilities and REST nonces for settings. No full phone, webhook body, access token or consent evidence in structured logs. Reuse Node Shared logging, existing HTTP metrics and WordPress safe diagnostics.
- Privacy export/erasure, approved evidence retention and the actual legal disclosure must be verified before production launch; audit retention, processing-claim expiration, consent validity and checkout eligibility are **four distinct lifecycles**. Evidence fields do not by themselves establish legal compliance.

## Rollout / Migration

- Verify real deployment state first; snapshot does not prove production. Consent-only sequence: Database migration -> API-003 source settings -> Woo source UI + conditional checkbox -> API-001 consent writer -> Woo pre-submit/returning session capture -> Support read/proxy -> LocalWP system test. No Woo recovery is enabled in this phase.
- Background-001 consent reader can be implemented independently after DB migration. BACKGROUND-002/003/004 and SYSTEM-TEST-002 remain **blocked** until a separately approved live Woo checkout-state reader and recovery engine have architect-accepted implementation. Remove their former `ARCH-045-DATABASE-001` dependency; do not mark them Ready just because consent capture works.
- If in production, use additive migrations and explicit source-switch behaviour. Never backfill grants from phone/contact marketing flags or rewrite live Shopify consent. API-001 must record consent evidence as non-actionable for wakeup while recovery is disabled; Background-003 later processes only new eligible receipts when the approved recovery engine is enabled. Never accumulate an indefinite pending backlog while recovery tasks are blocked.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-046-DATABASE-001 | moda_database | ready | — |
| ARCH-046-API-003 | moda_api | pending | DATABASE-001 |
| ARCH-046-API-001 | moda_api | pending | DATABASE-001, API-003 |
| ARCH-046-API-002 | moda_api | ready | — |
| ARCH-046-WOOCOMMERCE-001 | moda_woocommerce | ready | — |
| ARCH-046-WOOCOMMERCE-002 | moda_woocommerce | pending | ARCH-035-WOOCOMMERCE-007, API-001, WOOCOMMERCE-001/005 |
| ARCH-046-WOOCOMMERCE-003 | moda_woocommerce | pending | WOOCOMMERCE-002 |
| ARCH-046-WOOCOMMERCE-004 | moda_woocommerce | pending | API-002 |
| ARCH-046-WOOCOMMERCE-005 | moda_woocommerce | pending | API-003 |
| ARCH-046-BACKGROUND-001 | moda_background | pending | DATABASE-001 |
| ARCH-046-BACKGROUND-002 | moda_background | **blocked** | BACKGROUND-001 + externally approved Woo recovery engine |
| ARCH-046-BACKGROUND-003 | moda_background | **blocked** | BACKGROUND-002, API-001, WOOCOMMERCE-002 + externally approved checkout state |
| ARCH-046-BACKGROUND-004 | moda_background | **blocked** | BACKGROUND-001/002 + externally approved Woo follow-up |
| ARCH-046-SYSTEM-TEST-001 | moda_system_test | pending | DATABASE-001, API-001/003, WOOCOMMERCE-001/002/003/005 |
| ARCH-046-SYSTEM-TEST-002 | moda_system_test | **blocked** | all applicable accepted implementation + approved Woo recovery engine |

No **non-system-test** task depends on a system-test task. Task statuses reflect portable definitions, not materialisation or acceptance.

## Open Questions / Explicit Policies

1. No fixed 72-hour consent expiry. Consent remains a customer-phone-purpose decision until withdrawn, source/purpose/phone invalidation or applicable retention/legal rules. A checkout may independently become ineligible sooner; do not invent Woo cart/session lifetime.
2. A guest's phone is not a reusable verified identity. Guest association must be proven through server-bound checkout/session context. An existing grant can cover a later checkout only if the same customer identity and disclosure scope are verifiably established. If not, require a new affirmative grant or no send.
3. No external consent plugin is certified yet. No auto-detection from DOM, WP Consent API cookies or generic plugin marketing toggle.
4. The Woo recovery engine and current checkout reader are outside ARCH-035; confirm their future contracts before materialising Blocked tasks.

## External Sources (recorded with initial proposal 2026-10-20)

- WooCommerce [Additional checkout fields](https://developer.woocommerce.com/docs/block-development/extensible-blocks/cart-and-checkout-blocks/additional-checkout-fields/).
- WooCommerce [Updating cart on demand](https://developer.woocommerce.com/docs/apis/store-api/extending-store-api/extend-store-api-update-cart/).
- WooCommerce [Classic checkout field customisation](https://developer.woocommerce.com/docs/code-snippets/customising-checkout-fields).

## Change History

- 2026-10-20: Customer-phone consent correction: reuse Customer/CustomerPhone/WooCommerceInstallation; one minimal event evidence record; never create recovery without verified consent; eliminate invented 72h wait; later grant re-evaluates checkout instead of resuming a blocked recovery.
- 2026-10-21: Verified that the supplied schema has no usable customer WhatsApp consent audit history. Specify one immutable Woo evidence/change record with separate bounded mutable processing state; no second current consent/configuration table or Shared queue schema. Clarify sender, consumer, deduplication, privacy and source-epoch acceptance.
- 2026-10-20: Attempt 2 external-source selection/epoch proposal (refined by above correction).
- 2026-10-20: Initial checkout-scoped consent/block architecture (superseded by above correction).
