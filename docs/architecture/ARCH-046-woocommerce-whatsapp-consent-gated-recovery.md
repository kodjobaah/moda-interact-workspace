---
id: ARCH-046
title: WooCommerce Moda checkbox consent and customer-phone admission
status: proposed
coordinator: moda_architect
created: 2026-10-20
updated: 2026-10-22
---

# ARCH-046 — WooCommerce WhatsApp consent-gated recovery

## Status

**Proposed.** Consent capture tasks are not equivalent to live Woo recovery. ARCH-035 remains capture-only in the snapshot; Woo recovery execution (`BACKGROUND-002/004`, `SYSTEM-TEST-002`) remains **Blocked** pending an independently accepted recovery engine. Shared `ARCH-045-DATABASE-002` is developer-claimed, Attempt 1, unmerged.

## 21 October 2026 — two-way Woo merchant Support integration replaces read-only notices

The merchant has approved **full Shopify-equivalent two-way Support** in WooCommerce. The existing Woo Support UI (`ARCH-035-WOOCOMMERCE-001`, Complete) will be connected through `ARCH-035-API-020` (paginated history, idempotent send, mark-read) and `ARCH-035-WOOCOMMERCE-016` (privileged WordPress proxy and UI client). Both consume the existing shared Support tables; all consent-related SYSTEM notices remain in that one thread. The earlier read-only-only `ARCH-046-API-002` and `ARCH-046-WOOCOMMERCE-004` are **superseded**, not implemented. No duplicate notices endpoint, separate Support thread, notification queue, new database or direct Woo-to-Postgres path is allowed.

`ARCH-046-WOOCOMMERCE-007` retains the independent no-contact action and now depends on `ARCH-035-WOOCOMMERCE-016` plus `ARCH-046-API-005`. The blocked `ARCH-046-SYSTEM-TEST-002` instead depends on the full Support tasks. These Support changes **do not unblock** the separately missing Woo checkout-state reader/live recovery engine or authorise consent-triggered recovery work. ARCH-035-SYSTEM-TEST-005 independently certifies two-way Support; ARCH-046-SYSTEM-TEST-002 later certifies consent/recovery/notice interplay.

## Problem

WooCommerce lacks a uniform WhatsApp recovery permission source comparable to Shopify's native customer consent. Moda can offer its own optional checkout opt-in, but it must never treat the captured phone number or merchant selection as customer permission. Previous task drafts created multiple identity/provider/erasure tables that are unnecessary for the agreed consent-only feature.

## Goals

1. Register Moda's **one optional, unchecked WhatsApp checkout-recovery checkbox** on eligible Classic and Blocks checkouts. Merchant-facing instructions belong to the same `WOOCOMMERCE-001` task.
2. Allow customer opt-in/withdrawal to reach the hosted API **before order placement** through authenticated plugin-to-API transport and server-validated checkbox action; do not block checkout if Moda API is unavailable.
3. Resolve or create existing `Customer`/`CustomerPhone` by authenticated **merchant (`shopId`) + canonical phone**. Reuse a **single** unambiguous existing match; refuse ambiguous duplicate matches. Identity lookup is not proof of opt-in; no automatic grant from phone equality.
4. Store current consent on existing `CustomerPhone` using the shared DATABASE-002 schema; keep **one** new `commerce.WhatsAppConsentEvidence` audit table for Woo Moda-checkbox grants/withdrawals, with transactional/idempotent writes. No additional Customer/WooInstallation/reachability persisted columns.
5. Allow authorised merchant administrators to suppress/re-enable recovery for **consented** customers on CustomerPhone without creating WhatsApp consent or bypassing a customer STOP. Do not manage third-party plugin checkboxes.
6. When an approved Woo recovery engine exists, read current consent and installation status **only during normal checkout reconciliation and before proactive sends**. No consent means no recovery row, message or credit; merchant notice refers to checkout, not a nonexistent recovery. Consent change alone never scans/restarts old checkouts.

## Non-Goals

- Approved-external plugin adapters, provider/source selectors, provider epochs, third-party checkbox management or new consent authority.
- Persistent `WooCheckoutCustomerIdentity`, `CustomerPrivacyErasureFence`, principal-digest columns on Customer, installation consent config or reachability consent extensions.
- Personal-data erasure, privacy export/erase, redaction APIs/WordPress hooks. Those are separate potential privacy work and must not be implemented under ARCH-046 consent tasks.
- A new Shopify consent table, a separate Woo current-consent table, consent-driven scheduling/queue, 72-hour consent expiry, checkout-recovery creation on missing consent, or a merchant-granted opt-in.
- Live Woo recovery engine implementation within ARCH-035 capture-only integration.

## Current Architecture

`Customer` is shop-scoped and has associated `CustomerPhone` records. `WooCommerceInstallation` already links an authenticated installation to its shop, credential version and ACTIVE/REVOKED status. The Woo plugin and hosted API already communicate server-to-server. ARCH-035 currently captures checkout activity but is not authorised to materialise recoveries. DATABASE-002's unmerged schema contains older speculative tables and provider settings, which the same claimed Attempt 1 must remove.

## Proposed Architecture

### Checkout customer action

- **WOOCOMMERCE-001:** one opt-in field and clear Recovery Settings guidance in existing plugin UI when connected and recovery feature enabled. The field is not installed permanently into the theme and disappears on later page loads when feature/plugin becomes inactive. No support for arbitrary third-party consent plugins.
- **WOOCOMMERCE-002/003:** use supported Classic/Blocks hooks; verify that the customer actively selected/withdrew the checkbox during a current checkout (server-side field observation, normal WooCommerce nonce/session protections). A stale checkout page cannot submit a new GRANT after disconnect/feature-disable. Pre-submit acknowledgements determine when consent is valid; if checkout activity overtakes the consent ACK, that checkout may remain ineligible.
- **API-001:** authenticate WooInstallation (derive shop), verify the deliberate checkbox action, canonicalise the server-observed number, look up by `Customer.shopId` + active `CustomerPhone` canonical phone. Reuse the single match or create an ordinary Customer/CustomerPhone when none exists; ambiguous matches deny the consent write without merging customers. **Matching a number never sets GRANTED**: only a verified affirmative checkbox event does. Withdrawals/regrants use monotonic revisions and stable idempotency IDs. Atomically store current decision and evidence fact.

### Current state and evidence

- `commerce.CustomerPhone`: one current shop/phone/purpose decision, consent source `WOO_MODA_CHECKBOX`, verification/observation date and revision, local STOP/merchant no-contact. It is read for recovery admission.
- `commerce.WhatsAppConsentEvidence`: single new table of immutable Woo checkbox GRANT/REVOKE events, disclosure wording/version/locale, tenant/customer/phone references, timestamp and conflict-resistant `(shopId,eventId)` retry identity. It is audit history, **never** a polling/recovery worklist.
- `commerce.Customer`: unchanged persisted columns; `shopId` provides merchant scope. `woocommerce.WooCommerceInstallation`: unchanged persisted columns. `whatsapp.WhatsAppRecipientReachability`: unchanged, continues to describe delivery reachability, not consent.
- **API-005 + WOOCOMMERCE-007:** merchant may deselect a consented CustomerPhone to suppress recovery and later reselect it only if current consent is GRANTED. Merchant selection cannot clear customer STOP or create an opt-in. No separate selection table.

### Normal recovery only

An eventual separately approved Woo checkout recovery engine reads the active installation and current CustomerPhone during **ordinary** checkout reconciliation. Missing/UNKNOWN/REVOKED/no-contact/ambiguous identity → no CheckoutRecovery, no attempt, no credit and checkout-keyed merchant Support notice when applicable. If consent is granted later, it updates CustomerPhone only; a later ordinary checkout event may create the first recovery after fresh eligibility checks. No guaranteed revisit of old carts and no consent-specific background wakeups.

### Marketing purpose and shared STOP behaviour

- The Moda Woo checkout checkbox explicitly requests **WhatsApp abandoned-basket marketing** permission for the merchant; mere phone collection, checkout capture or a merchant recovery selection toggle is not consent. Checkout disclosure version/locale remain part of existing `commerce.WhatsAppConsentEvidence`.
- Approved live Woo recovery (still blocked pending separate engine) must use **Meta-approved Marketing templates** for initial reminders, scheduled follow-ups and merchant post-window recovery messages; never substitute a Utility/Authentication or unknown-category template. Genuine customer-initiated in-window service messages remain separate. The inspected `WhatsAppTemplateVariant` catalogue does not show a Meta category column: verify category using a trustworthy provider approval source rather than assuming purpose/status proves it.
- Inbound WhatsApp STOP is owned by `ARCH-045-BACKGROUND-005` for **both** platforms: a quoted merchant message limits suppression to that merchant phone; standalone or unresolvable-quote STOP suppresses all currently registered merchants sharing the sender's canonical phone, including Woo. Only affected Shopify shops receive the subsequent native unsubscribe API call. No new Woo consent/provider/reachability tables or separate STOP queue are added.

## Request / Event Flow

```text
Woo Classic/Blocks checkbox changed
  -> server-verified checkout action + authenticated installation
  -> hosted Woo API (derive shop; canonicalise phone)
  -> lookup existing Customer(shopId) + active CustomerPhone(number)
      |- one match: reuse existing records (no automatic grant)
      |- zero: create existing Customer and CustomerPhone
      `- multiple: reject ambiguous write
  -> deliberate GRANT/REVOKE validated
  -> atomic CustomerPhone + WhatsAppConsentEvidence write
  -> STOP (no checkout scan, recovery or charge)

Later normal Woo checkout reconciliation (once live recovery engine approved)
  -> latest CustomerPhone + installation status + checkout eligibility
    |- no valid consent: no recovery + checkout-keyed notice
    `- valid consent: recovery may be created and outbound guarded
```

## Repository Responsibilities

- **Database:** shared `ARCH-045-DATABASE-002` only; CustomerPhone extension plus one new `commerce.WhatsAppConsentEvidence` table.
- **Woo plugin:** checkbox + merchant guidance, validated pre-submit choice/withdrawal, merchant recovery suppression UI and optional Support notice reader.
- **Hosted API:** authenticated consent write/merchant suppression on existing customer/phone, merchant Support reads, safe idempotency. No provider-source configuration API.
- **Background:** future current-consent reader, pre-creation and send gates only when approved Woo engine exists.
- **System test:** LocalWP Classic/Blocks capture and eventual live recovery, with separate terminal gates.

## Data Model / Contracts

Tenant identity is `Customer.shopId` and authenticated `WooCommerceInstallation.shopId`; canonical phone is joined through CustomerPhone. The only new relation object is `commerce.WhatsAppConsentEvidence`. `API-001` defines its Woo HTTP consent v1 contract; the PHP producer uses matching fixtures. `ARCH-045-SHARED-001/002` provide Node phone canonicalisation and Shopify sync contract. No Shared Woo queue event or Woo customer-session linking table is defined.

## Consistency / Transactions / Failure Handling

- The API accepts positive permission **only** from a deliberate validated checkout opt-in, not an arbitrary browser-provided `customerId`, phone match, checkbox appearance, merchant toggle or provider flag.
- CustomerPhone and the event evidence fact commit atomically; `(shopId,eventId)` supports idempotent replay and rejects same-ID/different-body conflicts; stale grants cannot override newer withdrawals or customer STOP. Plugin checkout continues during hosted outages but no unacknowledged grant is considered verified.
- Identical phone in another merchant's shop is never matched. Ambiguous duplicate active records within a shop must fail closed rather than silently merge identities. Phone changes do not carry a grant automatically.
- Merchant suppression is distinct from customer permission: re-enable clears only merchant-owned suppression if the phone is already GRANTED, never clears customer STOP and never grants opt-in.
- No network calls inside SQL transactions, no consent-driven recovery scheduling, no duplicate charge on retries.

## Security / Observability

Use existing WordPress admin capabilities and REST nonces, trusted installation authentication for hosted API, server-side checkout action validation, tenant-scoped phone lookup, Shared canonical phone tests and minimal/redacted structured logs. Reuse framework telemetry. No Gateway infrastructure task required for the consent-only design.

## Rollout / Migration

Revise unmerged DATABASE-002 migration and test in place (check developer's actual migration history before applying). Then implement authenticated API consent transaction, WordPress checkbox and pre-submit handling; release them only when targeted LocalWP system test passes. Consent collection can ship without authorising outbound Woo recovery. Live Woo BACKGROUND-002/004 and SYSTEM-TEST-002 remain **Blocked** until the independently approved recovery engine exists. Do not update `docs/decisions/**/_index.md` until this architecture session is explicitly completed.

## Decisions / Tasks

| Task | Owner | Status | Depends on |
|---|---|---|---|
| `ARCH-046-DATABASE-001` | `moda_database` | superseded | — |
| `ARCH-046-API-001` | `moda_api` | pending | `ARCH-045-DATABASE-002`, `ARCH-045-SHARED-002` |
| `ARCH-046-API-002` | `moda_api` | ready | — |
| `ARCH-046-API-003` | `moda_api` | superseded | — |
| `ARCH-046-API-004` | `moda_api` | superseded | — |
| `ARCH-046-API-005` | `moda_api` | pending | `ARCH-045-DATABASE-002` |
| `ARCH-046-WOOCOMMERCE-001` | `moda_woocommerce` | ready | — |
| `ARCH-046-WOOCOMMERCE-002` | `moda_woocommerce` | pending | `ARCH-035-WOOCOMMERCE-007`, `ARCH-046-API-001`, `ARCH-046-WOOCOMMERCE-001` |
| `ARCH-046-WOOCOMMERCE-003` | `moda_woocommerce` | pending | `ARCH-046-WOOCOMMERCE-002` |
| `ARCH-046-WOOCOMMERCE-004` | `moda_woocommerce` | pending | `ARCH-046-API-002` |
| `ARCH-046-WOOCOMMERCE-005` | `moda_woocommerce` | superseded | — |
| `ARCH-046-WOOCOMMERCE-006` | `moda_woocommerce` | superseded | — |
| `ARCH-046-WOOCOMMERCE-007` | `moda_woocommerce` | pending | `ARCH-046-API-005`, `ARCH-046-WOOCOMMERCE-004` |
| `ARCH-046-BACKGROUND-001` | `moda_background` | pending | `ARCH-045-DATABASE-002`, `ARCH-045-SHARED-002` |
| `ARCH-046-BACKGROUND-002` | `moda_background` | blocked | `ARCH-046-BACKGROUND-001`, `ARCH-045-BACKGROUND-005` |
| `ARCH-046-BACKGROUND-003` | `moda_background` | superseded | — |
| `ARCH-046-BACKGROUND-004` | `moda_background` | blocked | `ARCH-046-BACKGROUND-001`, `ARCH-046-BACKGROUND-002`, `ARCH-045-BACKGROUND-005` |
| `ARCH-046-SYSTEM-TEST-001` | `moda_system_test` | pending | `ARCH-045-DATABASE-002`, `ARCH-046-API-001`, `ARCH-046-WOOCOMMERCE-001`, `ARCH-046-WOOCOMMERCE-002`, `ARCH-046-WOOCOMMERCE-003`, `ARCH-045-SHARED-002`, `ARCH-045-BACKGROUND-005`, `ARCH-046-API-005`, `ARCH-046-WOOCOMMERCE-007` |
| `ARCH-046-SYSTEM-TEST-002` | `moda_system_test` | blocked | `ARCH-045-DATABASE-002`, `ARCH-046-API-001`, `ARCH-046-API-002`, `ARCH-046-WOOCOMMERCE-002`, `ARCH-046-WOOCOMMERCE-003`, `ARCH-046-WOOCOMMERCE-004`, `ARCH-046-BACKGROUND-001`, `ARCH-046-BACKGROUND-002`, `ARCH-046-BACKGROUND-004`, `ARCH-045-SHARED-002`, `ARCH-045-BACKGROUND-005`, `ARCH-046-API-005`, `ARCH-046-WOOCOMMERCE-007` |

## Open Questions

- Confirm real Classic/Blocks pre-submit ordering with LocalWP: no assumption that checkout capture arrives after consent acknowledgement.
- Resolve duplicate active shop/phone rows as a data-quality problem; never accept an ambiguous match as customer opt-in.
- Separate live Woo recovery engine task IDs are deliberately not fabricated. Consent integration does not make them Ready.

## Change History

- 2026-10-20: Initial Woo consent capture and recovery gate proposal.
- 2026-10-21: Removed 72-hour consent expiry, consent-wakeup/poller and consent-blocked CheckoutRecovery rows.
- 2026-10-21: Consolidated Database/Shared ownership, removed third-party consent provider selection, and merged merchant guidance into the checkout UI task.
- 2026-10-21: **Consolidated minimal consent model:** same existing Customer and CustomerPhone; shop-scoped canonical phone lookup allowed with no automatic grant; one `commerce.WhatsAppConsentEvidence` table; no added WooInstallation, reachability, customer-principal, guest-link or erasure structures. Privacy tasks are outside consent and remain superseded for traceability.
