---
id: ARCH-046
title: WooCommerce customer-phone WhatsApp consent capture and normal reconciliation gating
status: proposed
coordinator: moda_architect
created: 2026-10-20
updated: 2026-10-21
---

# ARCH-046 — WooCommerce WhatsApp consent and normal checkout reconciliation

## Status

**Proposed; portable task definitions, not materialised or implemented.** Baseline: supplied 2026-10-20 workspace snapshot, ARCH-046 Attempts 1/2/3, and ARCH-045/046 customer-consent correction. This revision removes the proposed Woo evidence-driven checkout wakeup/worklist while retaining immutable audit facts and merchant notification. The separately approved WooCommerce recovery engine remains a hard execution boundary.

## 21 October 2026 — two-way Woo merchant Support integration replaces read-only notices

The merchant has approved **full Shopify-equivalent two-way Support** in WooCommerce. The existing Woo Support UI (`ARCH-035-WOOCOMMERCE-001`, Complete) will be connected through `ARCH-035-API-020` (paginated history, idempotent send, mark-read) and `ARCH-035-WOOCOMMERCE-016` (privileged WordPress proxy and UI client). Both consume the existing shared Support tables; all consent-related SYSTEM notices remain in that one thread. The earlier read-only-only `ARCH-046-API-002` and `ARCH-046-WOOCOMMERCE-004` are **superseded**, not implemented. No duplicate notices endpoint, separate Support thread, notification queue, new database or direct Woo-to-Postgres path is allowed.

`ARCH-046-WOOCOMMERCE-007` retains the independent no-contact action and now depends on `ARCH-035-WOOCOMMERCE-016` plus `ARCH-046-API-005`. The blocked `ARCH-046-SYSTEM-TEST-002` instead depends on the full Support tasks. These Support changes **do not unblock** the separately missing Woo checkout-state reader/live recovery engine or authorise consent-triggered recovery work. ARCH-035-SYSTEM-TEST-005 independently certifies two-way Support; ARCH-046-SYSTEM-TEST-002 later certifies consent/recovery/notice interplay.

## Problem

WooCommerce does not expose a universal Shopify-style WhatsApp marketing consent record that Moda can use for every merchant. Merchants may already have a consent plugin, so automatically adding a second checkbox can confuse customers. Permission must be captured **before checkout completion** to support legitimate abandoned checkout recovery. The previous proposal coupled each consent event to an evidence-backed background wakeup of old checkouts, adding unnecessary processing complexity.

Instead, current permission belongs to the verified `commerce.CustomerPhone`. A consent change updates that same record, and **only a later ordinary Woo checkout/recovery reconciliation** reconsiders a still-eligible checkout. A consent event alone never creates a recovery, schedules an abandoned checkout, or charges a credit.

## Goals

1. Reuse `commerce.Customer` and the **same cross-platform current phone-consent fields** owned by `ARCH-045-DATABASE-002`; create no second current-state table.
2. Store merchant consent collection selection, provider ID and epoch on existing `woocommerce.WooCommerceInstallation`, default `NOT_CONFIGURED`.
3. Display one optional, initially unchecked WhatsApp unfinished-checkout checkbox for Moda mode in **Classic and Blocks**; hide it when not configured or a certified external integration is selected. Unsupported external plugins are not accepted just because a similar checkbox exists.
4. Accept verified customer/guest exact-phone GRANT/REVOKE decisions through the hosted Woo API before order placement; atomically update `CustomerPhone` and append one immutable Woo consent-evidence fact for history, retry detection and privacy review. **No wakeup claim/status, retry scheduling, outbox or second consent table**.
5. During a future approved Woo normal checkout reconciliation, read the latest CustomerPhone decision and installation source/epoch; if consent is not valid, create **no CheckoutRecovery**, attempt, message or credit charge. Notify merchant with an idempotent checkout-keyed existing Support SYSTEM notice.
6. A later grant changes only current customer-phone consent. If another ordinary reconciliation event subsequently occurs for the same legitimate, still-eligible checkout, the existing first-creation path can create a recovery then. No consent-driven checkout polling, direct materialisation or 72-hour consent wait.
7. Stop proactive recovery follow-ups when current consent is withdrawn or source/phone changes, without bypassing provider rules or charging incorrectly.

- Bind account and guest checkout identity securely across Woo plugin, capture-only checkout activity, hosted API and `CustomerPhone`; phone number, email and `checkoutKey` alone never establish customer identity.
- Require safe Classic/Blocks pre-submit consent acknowledgement and monotonic grant/revoke/source epoch ordering; support Woo privacy exports and erasure, inbound STOP and merchant-authorised off-channel opt-out.
- When the future Woo recovery engine exists, gate *every* first recovery insert, initial retry, scheduled template and merchant post-window proactive send on exact current phone, installation configuration, local no-contact, privacy fence and short SQL revision check.

## Non-Goals

- Shopify Customer Privacy API implementation or Meta advertising consent; each platform retains its own consent collection authority.
- Automatically trusting CMP cookies, generic marketing flags or an unreviewed third-party plugin; automatic DOM scraping of consent checkboxes.
- A new `CheckoutRecovery` for unconsented checkout; recovery admission enum; a 72-hour consent deadline; a database evidence worklist or consent-triggered recovery scheduler.
- Enabling Woo outbound recovery from ARCH-035's **capture-only** state before an independently approved Woo recovery engine and authoritative checkout/order recheck exist.
- A generic Woo-versus-Shopify Shared Redis consent queue schema.

## Current Architecture — inspected snapshot

- `commerce.Customer` is shop-scoped; `commerce.CustomerPhone` stores the customer's phone and active interval with no consent fields. `ARCH-045-DATABASE-002` is the single owning task for shared current WhatsApp recovery consent fields.
- `woocommerce.WooCommerceInstallation` is installation- and shop-scoped; it currently lacks consent source settings. Woo API can authenticate the installation and derive shop; plugin cannot access Moda PostgreSQL/Redis/private secrets.
- There is no durable general-purpose WhatsApp opt-in/withdrawal history model in the inspected schema. One Woo evidence model is justified solely for auditability, idempotency and ordering, not as a separate current projection or a queue.
- ARCH-035's Woo checkout/order integration is capture-only; no approved Woo `CheckoutRecovery` materialisation and provider send path yet. Woo Support UI currently has no live API-backed read/send/mark-read; ARCH-035-API-020 and WOOCOMMERCE-016 will supply the full two-way path.

- Deep review 2026-10-21: `moda-interact-api/src/woocommerce/activity/contract.ts` has checkoutKey and optional contact, not a server-verified Woo guest/account-to-Customer association. Consent and checkout activity arrive separately and can overtake each other.
- ARCH-035-WOOCOMMERCE-007 is capture-only, not a live recovery engine; no Woo recovery materialisation or scheduled follow-up is authorised by ARCH-046 consent capture tasks.

## Proposed Architecture

### A. Merchant consent collection source

Use installation-owned `consentSourceMode=NOT_CONFIGURED|MODA_CHECKBOX|SUPPORTED_EXTERNAL`, optional approved provider ID and monotonic source epoch. Default NOT_CONFIGURED permits no recovery; source switches fence prior-source grants for eligibility without erasing immutable evidence. `SUPPORTED_EXTERNAL` is selectable **only** after a specific verified adapter exists; none is approved in the supplied snapshot. The selected mode controls whether Moda renders its checkbox in Classic/Blocks.

### B. Current consent belongs to the exact customer-phone

The **single** source for Woo current permission is the customer's active `commerce.CustomerPhone` record, with purpose `WHATSAPP_CHECKOUT_RECOVERY`, exact canonical phone, decision, source/provider, epoch, disclosure evidence reference and decision order. Existing `commerce.Customer` owns shop/customer identity; logged-in accounts are verified and guests require secure checkout/session-bound identity, never phone-only joining. A changed phone or stale source epoch does not inherit a grant.

The shared phone-consent schema is owned by `ARCH-045-DATABASE-002` and used by both architectures. `ARCH-045-DATABASE-002` also adds Woo installation configuration and **one append-only `WooWhatsAppConsentEvidence`-equivalent record**; it does **not** redefine shared CustomerPhone fields or add a separate current-consent table. Immutable evidence facts have a stable `(shopId,eventId)` deduplication key, decision, customer/phone identity, source/epoch, disclosure/version and timestamps. They are not marked `READY`, polled, leased, acked or retried to trigger checkout recovery; normal privacy export/erasure rules still apply.

### C. Capture and update before abandonment

Moda checkbox is unchecked by default and uses supported Woo Classic and Blocks extension points. The plugin verifies current Woo session/checkout identity and exact phone, then sends an authenticated server-to-server event through hosted API. `ARCH-046-API-001` transactionally checks current installation mode/epoch and customer/phone identity, updates CustomerPhone and writes immutable evidence. The same event retry is idempotent; stale changes cannot reverse a later withdrawal. Host outage does not block checkout and cannot fabricate permission. Later grant or withdrawal updates **the same CustomerPhone**; API ingestion does not enqueue recovery or scan past carts.

### D. Future recovery reads current consent during its ordinary reconciliation

Once an independently approved Woo recovery engine exists, its **normal** checkout/candidate reconciliation reads current CustomerPhone and installation mode/epoch before first recovery creation, in addition to the current unpaid/abandoned, phone, suppression, entitlement and maturity checks. When absent/invalid, create no recovery, credit reservation or Meta send; generate at most one checkout-keyed existing merchant Support notice, differentiating missing customer consent from merchant collection not configured or verification outage.

A later opt-in may be seen when the **next ordinary checkout event** causes reconciliation of the same eligible checkout. If no such event occurs, no automatic reprocessing is promised. The superseded `ARCH-046-BACKGROUND-003` evidence-polling wakeup is unnecessary and must not be implemented. Existing authorised proactive follow-ups also re-check current Woo consent before admission/provider send.

- **Verified Woo identity:** add only the minimum necessary durable Woo account/guest-session/customer/checkout link under the consolidated `ARCH-045-DATABASE-002`, protected by installation-verified server transport, session lifetime/rotation and reuse checks. It is not another current-consent table and no phone-only join is allowed.
- **Pre-submit ordering:** grant becomes eligible only after API-001 atomically commits CustomerPhone+evidence and Woo receives an ACK. If ordinary checkout capture/maturation overtakes that ACK, no recovery occurs unless a subsequent *normal* checkout event occurs. No consent-specific queue/scheduler is authorised.
- **Concurrency:** installation source epochs, immutable evidence payload hashes, monotonic per-principal decision order, and CustomerPhone local no-contact revisions are transactionally checked. Multi-tab stale grant, lost ACK, source ABA, phone swap and retry after privacy deletion cannot revive permission.
- **Data rights and opt-out:** API-004 plus WOOCOMMERCE-006 provide authenticated WP privacy requests for hosted current consent/evidence, while API-005 plus WOOCOMMERCE-007 record verified merchant off-channel STOP using existing merchant auth; inbound STOP is owned by ARCH-045-BACKGROUND-005.
- **Recovery runtime remains blocked:** approved Woo checkout/order-state reader and live recovery engine are external release gates. A future engine reuses Background consent and final send fences for first and proactive follow-up sends, not consent evidence wakeups.

## Request / Event Flow

```text
Woo merchant selects consent source -> existing WooCommerceInstallation fields
Woo customer explicitly opts in/out in checkout -> verified WordPress server
  -> authenticated hosted API -> atomic CustomerPhone update + one immutable audit event -> STOP

Later normal Woo checkout reconciliation (once approved recovery engine exists)
  -> obtain current checkout/order state + verified customer/phone
  -> current CustomerPhone grant and Woo installation source/epoch
      |- missing / withdrawn / invalid: no CheckoutRecovery, checkout-keyed merchant Support notice
      `- valid and checkout eligible: existing first recovery materialisation, provider/billing rules
```

## Repository Responsibilities

| Repository / owner | Responsibility |
|---|---|
| `moda-interact-database` / `moda_database` | **Single** `ARCH-045-DATABASE-002` owns cross-platform CustomerPhone state, WooInstallation mode/epoch, one Woo immutable evidence record, verified Woo identity linkage and the privacy erasure fence; **no worklist** |
| `moda-interact-api` / `moda_api` | API-003 merchant source configuration; API-001 verified transactional CustomerPhone+evidence writer; the separate ARCH-035-API-020 two-way merchant Support read/send/mark-read API |
| `moda-interact-woocommerce` / `moda_woocommerce` | Classic/Blocks UI, customer decision transfer, later consent/withdrawal and merchant Settings/Support |
| `moda-interact-background` / `moda_background` | When Woo recovery is separately approved, read current consent in normal checkout reconciliation and gate initial/proactive sends; **no evidence polling** |
| `moda-interact-system-test` / `moda_system_test` | Terminal LocalWP consent capture and subsequent actual normal-reconciliation recovery validation |

- Additional ownership: `moda_api` API-004 Woo privacy export/erase and API-005 merchant no-contact, `moda_woocommerce` WOOCOMMERCE-006 WP privacy hooks and WOOCOMMERCE-007 admin no-contact action. These are separate from the blocked Woo recovery engine and do not create a consent wakeup.

## Data Model / Contracts

- Reuse `commerce.Customer` + `commerce.CustomerPhone`, with current phone consent fields owned by `ARCH-045-DATABASE-002` (common to Shopify and Woo). No consent-specific `CheckoutRecovery` state.
- Reuse `woocommerce.WooCommerceInstallation` for `NOT_CONFIGURED`, `MODA_CHECKBOX` or certified `SUPPORTED_EXTERNAL`, provider ID and source epoch; no settings table.
- New single Woo `WooWhatsAppConsentEvidence`-equivalent append-only **fact** table for verified grant/withdrawal, deduplication, source-epoch ordering and audit. No `NOT_ACTIONABLE`, `READY`, lease, claim, retry or ack status, polling index or queue contract. Historical evidence is **not** current authorisation and cannot itself cause recovery.
- Versioned API-owned `woo.whatsapp-consent.v1` request with shop derived from installation credentials, server-verified customer/session and exact phone, decision and disclosure, event ID/revision, source/epoch and optional checkout reference as **collection context**. Replayed/stale/forged writes fail closed; the consent change endpoint never schedules checkout reconciliation.
- Existing Support message records hold merchant notice (checkout-based sourceKey). No Woo Shared queue schema or Shopify webhook-to-Woo dependency.

- Canonical phone and Shopify principal helpers: combined `ARCH-045-SHARED-001` published by `ARCH-045-SHARED-002` for Node; PHP Woo uses matching golden vectors. CustomerPhone local STOP/current revision and privacy erasure fence are all owned by `ARCH-045-DATABASE-002`.
- Woo identity link (if a separate non-consent entity is strictly required) is owned by `ARCH-045-DATABASE-002`; only **one** Woo immutable consent evidence table and the existing WooInstallation configuration. Evidence cannot queue recovery; verified privacy erasure is an explicit exception to ordinary immutable audit state.
- Woo consent HTTP v1 and normal checkout activity v1 must share an authenticated account/guest/checkout association. If the current capture-only activity envelope cannot carry enough verified identity, revise the existing owning Woo plugin/API activity contract only under their assigned tasks, never create phone-only joining in Background.

- All proactive Woo sends check existing shop/recipient permanent no-contact safety fence as well as CustomerPhone; a STOP that arrived before a guest Customer was verified cannot be overridden by an unrelated customer record. No new Woo consent-grant table is needed.

## Consistency / Ordering / Failure Handling

- Commit effective CustomerPhone decision and immutable Woo evidence together in a database transaction. Retries of identical `(shopId,eventId)` do not duplicate evidence or silently flip state; same ID/different decision is rejected. Stale source epochs and old decision revisions cannot resurrect grants after withdrawal.
- A source switch makes older source grants ineligible via an epoch check, without editing historical evidence. The current state can stay as historical fact but must not be treated as current permission after invalidation; a new opt-in via active source is required as specified by disclosure/policy.
- Verified shop/customer/exact phone and supported collection source are mandatory; guest mobile number alone is not reusable identity. Hosted API outages mean unknown consent and no proactive send; checkout itself continues.
- No dedicated recovery wakeup is created on a grant. Ordinary Woo checkout reconciliation may later encounter the now-granted phone and create a recovery only if a separately approved checkout state reader proves eligibility. No custom consent age limit; checkout expiry is independent.
- Consent-evidence retention/export/erasure requires privacy policy; never equate indefinite audit retention with perpetual consent authority.

- ACK ordering is defined per Classic/Blocks mode; checkout observation before verified grant is allowed to miss recovery by design. Action Scheduler does not independently trigger a consent wakeup, and a later grant does not poll old checkouts.
- Use DB lock/conditional write for source epochs and CustomerPhone decision revisions; explicit revoke/STOP/privacy erase win over old grants. No consumer may reinterpret immutable evidence as current permission.
- Privacy request must cover hosted current state/evidence with WordPress exporter/eraser hooks; erased identity blocks later plugin retries. If opt-out arrives on WhatsApp, Background owns precedence before conversation routing.

## Scalability / Security / Observability

- No extra Redis queue, evidence polling, full-history scan or merchant-wide checkout scan. Normal Woo checkout volume drives normal reconciliation; consent writes remain narrow exact-customer/phone transactions.
- Use existing Woo installation authentication for hosted API, WordPress admin capabilities and REST nonces for Settings; no browser disclosure of credentials or direct access to Moda DB. Distinguish expected grant/revoke vs source/not-configured/verification failure without exposing full phone numbers in logs or Support messages.
- Reuse Shared structured logger in Node; framework/infrastructure telemetry where already available. Any provider failure must not turn into an outbound message or charge.

## Rollout / Migration

- Verify real deployment status before running migrations. Sequence for consent capture: **the complete ARCH-045-DATABASE-002 schema** -> API-003 -> Woo Settings/conditional checkout UI -> API-001 -> Woo pre-submit and later opt-in/withdrawal -> LocalWP consent tests. ARCH-035-API-020/WOOCOMMERCE-016 full Support implementation may proceed independently.
- BACKGROUND-001 is a consent-read boundary, but BACKGROUND-002/004 and terminal SYSTEM-TEST-002 remain **blocked** on a separately approved live Woo checkout recovery engine. `ARCH-046-BACKGROUND-003` is **superseded**, not a dependency.
- No historic audit events are backfilled into processing queues. No Woo recovery is enabled by the consent-only rollout; system tests do not claim a live Woo recovery engine exists in the supplied snapshot.

- Complete the consolidated DATABASE-002 schema (including current phone consent, Woo source/evidence/identity and privacy erasure fence) and publish the combined SHARED-001 via SHARED-002 before Woo API consent/privacy writers.
- Capture-only and merchant settings may be certified in SYSTEM-TEST-001. Keep live Woo BACKGROUND-002/004 and SYSTEM-TEST-002 Blocked until an **explicit** external approved live recovery engine exists; do not allow consent capture to be called live recovery.
- Woo privacy export/erase and merchant no-contact capabilities are release dependencies, not unowned operational manual steps.

## Decisions / Tasks

**Deep-review dependency correction (2026-10-21):** task YAML frontmatter is authoritative. Woo consent/evidence/privacy schema is consolidated into ARCH-045-DATABASE-002; Woo API-001/BACKGROUND-001 use the published Shared identity helper; SYSTEM-TEST-001/002 now include Woo privacy and no-contact owners. BLOCKED tasks remain blocked pending the externally approved live Woo recovery engine.


| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-045-DATABASE-002 | moda_database | ready | — |
| ARCH-046-DATABASE-001 | moda_database | **superseded** | — |
| ARCH-046-API-001 | moda_api | pending | ARCH-045-DATABASE-002, ARCH-046-API-003, ARCH-045-SHARED-002 |
| ARCH-046-API-002 | moda_api | **superseded** | Replaced by ARCH-035-API-020 |
| ARCH-046-API-003 | moda_api | pending | ARCH-045-DATABASE-002 |
| ARCH-046-API-004 | moda_api | pending | ARCH-045-DATABASE-002 |
| ARCH-046-API-005 | moda_api | pending | ARCH-045-DATABASE-002 |
| ARCH-046-WOOCOMMERCE-001 | moda_woocommerce | ready | — |
| ARCH-046-WOOCOMMERCE-002 | moda_woocommerce | pending | ARCH-035-WOOCOMMERCE-007, ARCH-046-API-001, ARCH-046-WOOCOMMERCE-001, ARCH-046-WOOCOMMERCE-005 |
| ARCH-046-WOOCOMMERCE-003 | moda_woocommerce | pending | ARCH-046-WOOCOMMERCE-002 |
| ARCH-046-WOOCOMMERCE-004 | moda_woocommerce | **superseded** | Replaced by ARCH-035-WOOCOMMERCE-016 |
| ARCH-046-WOOCOMMERCE-005 | moda_woocommerce | pending | ARCH-046-API-003 |
| ARCH-046-WOOCOMMERCE-006 | moda_woocommerce | pending | ARCH-046-API-004 |
| ARCH-046-WOOCOMMERCE-007 | moda_woocommerce | pending | ARCH-046-API-005, ARCH-035-WOOCOMMERCE-016 |
| ARCH-046-BACKGROUND-001 | moda_background | pending | ARCH-045-DATABASE-002, ARCH-045-SHARED-002 |
| ARCH-046-BACKGROUND-002 | moda_background | **blocked** | ARCH-046-BACKGROUND-001, ARCH-045-BACKGROUND-005 |
| ARCH-046-BACKGROUND-003 | moda_background | **superseded** | — |
| ARCH-046-BACKGROUND-004 | moda_background | **blocked** | ARCH-046-BACKGROUND-001, ARCH-046-BACKGROUND-002, ARCH-045-BACKGROUND-005 |
| ARCH-046-SYSTEM-TEST-001 | moda_system_test | pending | ARCH-045-DATABASE-002, ARCH-046-API-001, ARCH-046-API-003, ARCH-046-WOOCOMMERCE-001, ARCH-046-WOOCOMMERCE-002, ARCH-046-WOOCOMMERCE-003, ARCH-046-WOOCOMMERCE-005, ARCH-045-SHARED-002, ARCH-045-BACKGROUND-005, ARCH-046-API-004, ARCH-046-API-005, ARCH-046-WOOCOMMERCE-006, ARCH-046-WOOCOMMERCE-007 |
| ARCH-046-SYSTEM-TEST-002 | moda_system_test | **blocked** | ARCH-045-DATABASE-002, ARCH-046-API-001, ARCH-035-API-020, ARCH-046-API-003, ARCH-046-WOOCOMMERCE-002, ARCH-046-WOOCOMMERCE-003, ARCH-035-WOOCOMMERCE-016, ARCH-046-WOOCOMMERCE-005, ARCH-046-BACKGROUND-001, ARCH-046-BACKGROUND-002, ARCH-046-BACKGROUND-004, ARCH-045-SHARED-002, ARCH-045-BACKGROUND-005, ARCH-046-API-004, ARCH-046-API-005, ARCH-046-WOOCOMMERCE-006, ARCH-046-WOOCOMMERCE-007 |


## Open Questions / Explicit Policies

1. A consent change does **not** schedule a new checkout reconciliation. The next normal event might cause re-evaluation; without such an event there is **no guarantee** of later recovery. This is intentional.
2. There is no 72-hour consent expiry or fabricated checkout retention. Consent remains a customer/phone/purpose preference until withdrawn or invalidated; checkout eligibility follows the separately approved recovery rules.
3. No external provider adapter is certified by this snapshot. Unsupported plugin cookies/checkbox values are insufficient.
4. The future Woo recovery engine is outside ARCH-035 capture-only work; actual checkout-state authorisation and idempotent materialisation must be agreed before releasing blocked tasks.

- Pin exactly how Woo guest session IDs are verifiably derived/bound and invalidated by logout, Woo session expiry, login and checkout-key rotation before any guest recovery admission.
- Pin consent write ACK and checkout event ordering in Classic vs Blocks through real LocalWP smoke tests. A queue order cannot be assumed when events use distinct pipelines.
- Identify the separately approved Woo recovery engine task IDs only after they exist; until then BACKGROUND-002/004 and SYSTEM-TEST-002 remain blocked without fabricating missing dependency IDs.

## External Sources (recorded with initial proposal 2026-10-20)

- WooCommerce [Additional checkout fields](https://developer.woocommerce.com/docs/block-development/extensible-blocks/cart-and-checkout-blocks/additional-checkout-fields/).
- WooCommerce [Updating cart on demand](https://developer.woocommerce.com/docs/apis/store-api/extending-store-api/extend-store-api-update-cart/).
- WooCommerce [Classic checkout field customisation](https://developer.woocommerce.com/docs/code-snippets/customising-checkout-fields).

## Change History

- 2026-10-20: Initial consent capture and consent-blocked recovery proposal, later corrected to prohibit a recovery without verified permission.
- 2026-10-20: Conditional first-party/approved-external checkbox selection and source-epoch fencing.
- 2026-10-20: Customer/CustomerPhone/WooInstallation reuse, one Woo immutable evidence model and no fixed 72-hour consent period.
- 2026-10-21: Verified evidence history requirement in schema; initially proposed bounded evidence processing state.
- 2026-10-21: **Supersede evidence-driven recovery wakeups.** CustomerPhone latest consent is updated on consent change and read during the **next normal reconciliation**; immutable Woo evidence has no claim/ack/worklist fields. Share CustomerPhone schema via ARCH-045-DATABASE-002; no consent-triggered checkout scan or recovery job.

- 2026-10-21: Deep-review corrections C1–C6/H1–H6: verified Woo identity linkage, pre-submit ordering and session takeover tests, monotonic source/consent writes, WP privacy export/erase and merchant no-contact, future send-path hard gate.

- 2026-10-21: Merge Woo DATABASE-001 and ARCH-045-DATABASE-003 into cross-platform `ARCH-045-DATABASE-002`; supersede Woo DATABASE-001. Merge Shared identity task SHARED-003 into SHARED-001, with separate SHARED-002 publication. Woo API/Background depend on the single accepted Database task.
