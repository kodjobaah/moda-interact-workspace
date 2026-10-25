---
id: ARCH-046
title: WooCommerce Moda checkbox consent and customer-phone admission
status: proposed
coordinator: moda_architect
created: 2026-10-20
updated: 2026-10-25
---

# ARCH-046 — WooCommerce WhatsApp consent-gated recovery

## Status

**Proposed; consent integration in progress (25 October 2026 13:36 snapshot).** `ARCH-046-BACKGROUND-005` is recorded Complete and its shared notifier is present in merged Background source, including Shopify consumer integration. `ARCH-048-BACKGROUND-003/004` are Complete with row-only admission and initial-outreach services; `ARCH-046-BACKGROUND-002` has all prerequisites Complete and is now Ready for the Woo notice adapter. `ARCH-046-BACKGROUND-004` is Pending on BG002 and is narrowed to the Woo **initial-send** final consent/STOP permit; the Woo follow-up runtime remains disabled and out of scope. `ARCH-048-BACKGROUND-005` orchestrator and terminal system tests are still Pending/Blocked. This is not end-to-end Woo outbound certification or authorisation to enable live sends.

## 21 October 2026 — two-way Woo merchant Support integration replaces read-only notices

The merchant has approved **full Shopify-equivalent two-way Support** in WooCommerce. The existing Woo Support UI (`ARCH-035-WOOCOMMERCE-001`, Complete) will be connected through `ARCH-035-API-020` (paginated history, idempotent send, mark-read) and `ARCH-035-WOOCOMMERCE-016` (privileged WordPress proxy and UI client). Both consume the existing shared Support tables; all consent-related SYSTEM notices remain in that one thread. The earlier read-only-only `ARCH-046-API-002` and `ARCH-046-WOOCOMMERCE-004` are **superseded**, not implemented. No duplicate notices endpoint, separate Support thread, notification queue, new database or direct Woo-to-Postgres path is allowed.

`ARCH-046-WOOCOMMERCE-007` retains the independent no-contact action and now depends on `ARCH-035-WOOCOMMERCE-016` plus `ARCH-046-API-005`. The blocked `ARCH-046-SYSTEM-TEST-002` instead depends on the full Support tasks. These Support changes **do not authorise** consent-triggered recovery work or a WordPress live-checkout reader: ARCH-048 instead uses only accepted Woo events and existing Moda state. ARCH-035-SYSTEM-TEST-005 independently certifies two-way Support; ARCH-046-SYSTEM-TEST-002 later certifies consent/recovery/notice interplay.

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

`Customer` is shop-scoped and has associated `CustomerPhone` records. `WooCommerceInstallation` already links an authenticated installation to its shop, credential version and ACTIVE/REVOKED status. The Woo plugin and hosted API already communicate server-to-server. ARCH-035 currently captures checkout activity but is not authorised to materialise recoveries. DATABASE-002 is marked Complete after its unmerged task-branch implementation was narrowed to the shared CustomerPhone and WhatsAppConsentEvidence contract. Merge-to-main status is not established by this snapshot.

## Proposed Architecture

### Checkout customer action

- **WOOCOMMERCE-001:** one opt-in field and clear Recovery Settings guidance in existing plugin UI when connected and recovery feature enabled. The field is not installed permanently into the theme and disappears on later page loads when feature/plugin becomes inactive. No support for arbitrary third-party consent plugins.
- **WOOCOMMERCE-002/003:** use supported Classic/Blocks hooks; verify that the customer actively selected/withdrew the checkbox during a current checkout (server-side field observation, normal WooCommerce nonce/session protections). A stale checkout page cannot submit a new GRANT after disconnect/feature-disable. Pre-submit acknowledgements determine when consent is valid; if checkout activity overtakes the consent ACK, that checkout may remain ineligible.
- **API-001 baseline, corrected by API-007:** authenticate WooInstallation (derive shop); Woo verifies the deliberate checkbox action and canonicalises the submitted recipient; the hosted API enforces the canonical recipient, and looks up `Customer.shopId` + active `CustomerPhone` canonical phone. Reuse the single match or create an ordinary Customer/CustomerPhone when none exists; ambiguous matches deny the consent write without merging customers. **Matching a number never sets GRANTED**: only a verified affirmative checkbox event does. Withdrawals/regrants use monotonic revisions and stable idempotency IDs. Atomically store current decision and evidence fact.


### 24 October 2026 — thin Woo consent-write API (`ARCH-046-API-007`)

`ARCH-046-API-007` is a new, API-owned correction task; the completed `API-001` is not reopened. Replace v1 with `woo.whatsapp-consent.v2` on the existing authenticated `POST /v1/woocommerce/whatsapp-consent` route with exactly six top-level fields: `schemaVersion`, `eventId`, `decision`, `canonicalPhone`, `occurredAt` and `disclosure`. For GRANT the disclosure contains `{version,locale,text}`; for REVOKE it is `null`. The authenticated WooCommerce plugin is responsible for nonce/session/cart-token checks, the deliberate customer grant/withdrawal action, phone canonicalisation and accurate translated disclosure. The API derives merchant and fixed consent purpose from installation authentication; it does not require Classic/Blocks mode, checkout key, checkbox IDs/states, attestation booleans, duplicate recipient, or merchant URL in v2. It still enforces authentication/tenant isolation, bounded contract/recipient validation and atomic, ordered and idempotent consent/evidence persistence.

To shorten the hot write path, remove the Subscription/BillingPlan/Feature entitlement lookup from the v2-only consent write: a stored GRANT is passive permission evidence, never permission to create recovery work or send a message. Background remains the authoritative recovery-feature, consent and STOP gate. Replace separate transaction-time Shop and WooCommerceInstallation verification queries with one semantically equivalent indexed, row-locked join, preserving credential-rotation/revocation races. Keep initial installation authentication, immutable event facts, unambiguous shop/phone lookup, consent revision and decision ordering, event replay-digest integrity, existing per-event/recipient locks, STOP non-override and commit-before-ACK. Do not loosen five-minute freshness or timestamp-ordering semantics in this task without separately approved correctness work. Introduce no new database table, queue or infrastructure. Measure before/after SQL operations and transaction time rather than asserting an untested throughput gain.

**Rollout:** pre-production breaking change approved by the developer on 2026-10-24: Moda has no existing users, so accept **v2 only** and reject v1 rather than carry legacy parsers and retry adapters. The existing Woo v1 publisher will not work until an independent WooCommerce-owned v2 adoption task is implemented; coordinate API and Woo adoption before integrated validation. Do not infer permission to delete development databases or other durable resources. The previously drafted proof-backed returning-checkout `ARCH-046-API-006`/`ARCH-046-WOOCOMMERCE-008` handoff is **not present in this supplied workspace snapshot**; it remains a separate materialisation step. When API-006 is materialised, make it depend on architect-accepted, `complete` API-007. Do not create or edit nonexistent API-006/WOOCOMMERCE-008 task files within API-007, or change any `docs/decisions/**/_index.md` before the architect session is explicitly completed.

**API-007 review handoff (24 October 2026):** developer execution Attempt 1 is prepared for the `/moda_developer_update` reconciliation/self-review; the task remains `in_progress` until the authorised workflow changes state. Implementation `moda-interact-api` commit `220fa2b` was pushed on `task/ARCH-046-API-007`; post-correction lint and typecheck passed, and the disposable PostgreSQL suite passed 10/10. The v2 test measured 14 SQL statements/76.37 ms for a fresh grant and 9/23.06 ms for a duplicate retry, but no comparable pre-change SQL baseline or transaction-only duration has been provided. The Woo v1 producer remains incompatible until a separately owned v2 migration. This evidence handoff is **not** a passing self-review, acceptance or completion.

### Current state and evidence

- `commerce.CustomerPhone`: one current shop/phone/purpose decision, consent source `WOO_MODA_CHECKBOX`, verification/observation date and revision, local STOP/merchant no-contact. It is read for recovery admission.
- `commerce.WhatsAppConsentEvidence`: single new table of immutable Woo checkbox GRANT/REVOKE events, disclosure wording/version/locale, tenant/customer/phone references, timestamp and conflict-resistant `(shopId,eventId)` retry identity. It is audit history, **never** a polling/recovery worklist.
- `commerce.Customer`: unchanged persisted columns; `shopId` provides merchant scope. `woocommerce.WooCommerceInstallation`: unchanged persisted columns. `whatsapp.WhatsAppRecipientReachability`: unchanged, continues to describe delivery reachability, not consent.
- **API-005 + WOOCOMMERCE-007:** merchant may deselect a consented CustomerPhone to suppress recovery and later reselect it only if current consent is GRANTED. Merchant selection cannot clear customer STOP or create an opt-in. No separate selection table.

### Normal recovery only

The accepted ARCH-048 Woo admission service reads the active installation and current CustomerPhone during **ordinary** event-driven checkout reconciliation; ARCH-048-BG005 still needs to wire that service into the workers. Missing/UNKNOWN/REVOKED/no-contact/ambiguous identity → no CheckoutRecovery, no attempt, no credit and checkout-keyed merchant Support notice when applicable. If consent is granted later, it updates CustomerPhone only; a later ordinary checkout event may create the first recovery after fresh eligibility checks. No guaranteed revisit of old carts and no consent-specific background wakeups.

### Marketing purpose and shared STOP behaviour

- The Moda Woo checkout checkbox explicitly requests **WhatsApp abandoned-basket marketing** permission for the merchant; mere phone collection, checkout capture or a merchant recovery selection toggle is not consent. Checkout disclosure version/locale remain part of existing `commerce.WhatsAppConsentEvidence`.
- The approved initial Woo recovery capability must use a **Meta-approved Marketing template**; never substitute a Utility/Authentication or unknown-category template. Scheduled Woo follow-ups and merchant post-window recovery messages are disabled and require separately approved future implementation tasks. Genuine customer-initiated in-window service messages remain separate. The inspected `WhatsAppTemplateVariant` catalogue does not show a Meta category column: verify category using a trustworthy provider approval source rather than assuming purpose/status proves it.
- Inbound WhatsApp STOP is owned by `ARCH-045-BACKGROUND-005` for **both** platforms: a quoted merchant message limits suppression to that merchant phone; standalone or unresolvable-quote STOP suppresses all currently registered merchants sharing the sender's canonical phone, including Woo. No Shopify unsubscribe API call is made. The Moda-owned STOP remains effective across all affected Shopify and WooCommerce `CustomerPhone` records, is never cleared by native Shopify permission refresh, a Woo consent grant or merchant re-enable, and causes an idempotent Support notification to each affected merchant. It blocks **all further outbound WhatsApp messages** to the affected shop/phone, including in-window customer-service replies. No new Woo consent/provider/reachability tables or separate STOP queue are added.

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
- **Hosted API:** versioned, thin authenticated consent write with atomic current consent/evidence and safe ordering; merchant suppression, merchant Support reads and safe idempotency. After API-007 the consent write performs no billing feature-eligibility SQL. No provider-source configuration API.
- **Background:** accepted current-consent reader (BG001), accepted ARCH-048 first-row admission/outreach services, Woo merchant-notice adapter (BG002 Ready), final initial-send guard (BG004 Pending) and independent ARCH-048 worker composition.
- **System test:** LocalWP Classic/Blocks capture and eventual live recovery, with separate terminal gates.

### Shared recovery-consent merchant notifications (2026-10-24)

`ARCH-046-BACKGROUND-005` is Complete and the merged Background source contains the single `RecoveryConsentMerchantNoticeService` implementing `RecoveryConsentMerchantNotifier`. Shopify imports it now; the Ready `ARCH-046-BACKGROUND-002` task supplies only Woo-specific denial mapping, verified available shop-scoped checkout context and an awaited adapter. The common notifier owns bounded plain-text formatting, deterministic deduplication, a single transactional `MerchantSupportMessage(kind=SYSTEM)` writer, and safe structured logging. Neither the shared notifier nor the Woo adapter recreates Shopify-native or Woo current-consent policy; STOP notifications retain their existing separate owner.

The **merged accepted runtime** takes `(shopId, platform, checkoutToken, reason, blockedOperation, optional merchant display context)` and returns `created | duplicate`. Its current canonical `sourceKey` is `"recovery-consent:v1:" + sha256(JSON.stringify(["recovery-consent", 1, platform, shopId, checkoutToken, reason]))` (lowercase hex), **without** `blockedOperation`. Thus creation-stage and initial-send reentry notices with the same checkout/reason deduplicate to the first committed message; `blockedOperation` controls truthful body copy only. This reconciles older **operation-sensitive** task prose with the completed implementation: BG002 MUST consume the existing accepted contract rather than change the shared formatter/key. The common service owns fixed reason/outcome copy, optional bounded context, verified duplicate detection, tenant isolation and one atomic Support transaction. It never uses the checkout hash as its merchant-facing description. Shopify forwards already accepted checkout/customer context where available; Woo enriches shop-scoped data in BG-002. Neither caller duplicates the writer.

**Pre-production decision:** previously sent development Support messages and legacy Shopify `sourceKey` values need no backward-compatibility handling, adapter, migration or backfill. Use the new canonical contract for both platforms' future notices, without deleting existing development Support data. No new database table, Shared package, API endpoint or merchant UI is required. Shopify and WooCommerce denial/admission decisions remain platform-specific.

## Data Model / Contracts

Tenant identity is `Customer.shopId` and authenticated `WooCommerceInstallation.shopId`; canonical phone is joined through CustomerPhone. The only new relation object is `commerce.WhatsAppConsentEvidence`. `API-001` defined the previous v1 contract; `API-007` **replaces** it with v2 as the only supported request on the existing authenticated route. v2 producer adoption is a separate WooCommerce-owned task. `ARCH-045-SHARED-001/002` provide Node phone canonicalisation and Shopify sync contract. No Shared Woo queue event or Woo customer-session linking table is defined.

## Consistency / Transactions / Failure Handling

- The Woo server validates deliberate checkout opt-in/withdrawal and its checkout authentication before publishing; the API accepts the resulting event **only from the authenticated installation**, not arbitrary browser-provided `customerId`, a phone match, checkbox appearance, merchant toggle or provider flag. The API does not independently re-verify Woo checkout-only assertions in v2.
- CustomerPhone and the event evidence fact commit atomically; `(shopId,eventId)` supports idempotent replay and rejects same-ID/different-body conflicts; stale grants cannot override newer withdrawals or customer STOP; even a new Woo checkbox grant cannot automatically clear a WhatsApp STOP. Plugin checkout continues during hosted outages but no unacknowledged grant is considered verified.
- Identical phone in another merchant's shop is never matched. Ambiguous duplicate active records within a shop must fail closed rather than silently merge identities. Phone changes do not carry a grant automatically.
- Merchant suppression is distinct from customer permission: re-enable clears only merchant-owned suppression if the phone is already GRANTED, never clears customer STOP and never grants opt-in.
- No network calls inside SQL transactions, no consent-driven recovery scheduling, no duplicate charge on retries.

## Security / Observability

Use existing WordPress admin capabilities and REST nonces, trusted installation authentication for hosted API, server-side checkout action validation, tenant-scoped phone lookup, Shared canonical phone tests and minimal/redacted structured logs. Reuse framework telemetry. No Gateway infrastructure task required for the consent-only design.

## Rollout / Migration

DATABASE-002, Woo API-001 and BACKGROUND-001 are marked Complete with accepted task-branch evidence; their dependency versions and integration must be reconciled during deployment. Implement API-007 as an independently reviewed correction before materialising the previously drafted API-006 reader. Coordinate v2-only API deployment with a separately defined Woo v2 producer adoption (the current v1 producer becomes incompatible). No v1 migration or adapter is required because there are no production users. Next implement/validate WordPress checkbox and pre-submit handling; release them only when targeted LocalWP system test passes. Consent collection can ship without authorising outbound Woo recovery. Woo BG002 is **Ready** now that the admission seam and shared notifier have been accepted. Woo BG004 remains **Pending** until BG002 completes; it is limited to the initial-send/final-provider fence. ARCH-048 BG005 still awaits both accepted guards, and SYSTEM-TEST-002 remains Blocked by outstanding implementation and platform prerequisites. Do not update `docs/decisions/**/_index.md` until this architecture session is explicitly completed.

## Decisions / Tasks

| Task | Owner | Status | Depends on |
|---|---|---|---|
| `ARCH-046-DATABASE-001` | `moda_database` | superseded | — |
| `ARCH-046-API-001` | `moda_api` | complete | `ARCH-045-DATABASE-002`, `ARCH-045-SHARED-002` |
| `ARCH-046-API-007` | `moda_api` | in_progress | `ARCH-046-API-001`, `ARCH-045-DATABASE-002`, `ARCH-045-SHARED-002` |
| `ARCH-046-API-002` | `moda_api` | superseded | — |
| `ARCH-046-API-003` | `moda_api` | superseded | — |
| `ARCH-046-API-004` | `moda_api` | superseded | — |
| `ARCH-046-API-005` | `moda_api` | ready | `ARCH-045-DATABASE-002` |
| `ARCH-046-WOOCOMMERCE-001` | `moda_woocommerce` | ready | — |
| `ARCH-046-WOOCOMMERCE-002` | `moda_woocommerce` | pending | `ARCH-035-WOOCOMMERCE-007`, `ARCH-046-API-001`, `ARCH-046-WOOCOMMERCE-001` |
| `ARCH-046-WOOCOMMERCE-003` | `moda_woocommerce` | pending | `ARCH-046-WOOCOMMERCE-002` |
| `ARCH-046-WOOCOMMERCE-004` | `moda_woocommerce` | superseded | `ARCH-046-API-002` |
| `ARCH-046-WOOCOMMERCE-005` | `moda_woocommerce` | superseded | — |
| `ARCH-046-WOOCOMMERCE-006` | `moda_woocommerce` | superseded | — |
| `ARCH-046-WOOCOMMERCE-007` | `moda_woocommerce` | pending | `ARCH-046-API-005`, `ARCH-035-WOOCOMMERCE-016` |
| `ARCH-046-BACKGROUND-001` | `moda_background` | complete | `ARCH-045-DATABASE-002`, `ARCH-045-SHARED-002` |
| `ARCH-046-BACKGROUND-002` | `moda_background` | ready | `ARCH-046-BACKGROUND-001`, `ARCH-045-BACKGROUND-005`, `ARCH-048-BACKGROUND-003`, `ARCH-046-BACKGROUND-005` |
| `ARCH-046-BACKGROUND-003` | `moda_background` | superseded | — |
| `ARCH-046-BACKGROUND-004` | `moda_background` | pending | `ARCH-046-BACKGROUND-001`, `ARCH-046-BACKGROUND-002`, `ARCH-045-BACKGROUND-005`, `ARCH-048-BACKGROUND-004`; initial-send final permit only |
| `ARCH-046-BACKGROUND-005` | `moda_background` | complete | `ARCH-045-BACKGROUND-002` |
| `ARCH-046-SYSTEM-TEST-001` | `moda_system_test` | pending | `ARCH-045-DATABASE-002`, `ARCH-046-API-001`, `ARCH-046-WOOCOMMERCE-001`, `ARCH-046-WOOCOMMERCE-002`, `ARCH-046-WOOCOMMERCE-003`, `ARCH-045-SHARED-002`, `ARCH-045-BACKGROUND-005`, `ARCH-046-API-005`, `ARCH-046-WOOCOMMERCE-007` |
| `ARCH-046-SYSTEM-TEST-002` | `moda_system_test` | blocked | `ARCH-045-DATABASE-002`, `ARCH-046-API-001`, `ARCH-035-API-020`, `ARCH-046-WOOCOMMERCE-002`, `ARCH-046-WOOCOMMERCE-003`, `ARCH-035-WOOCOMMERCE-016`, `ARCH-046-BACKGROUND-001`, `ARCH-046-BACKGROUND-002`, `ARCH-046-BACKGROUND-004`, `ARCH-045-SHARED-002`, `ARCH-045-BACKGROUND-005`, `ARCH-046-API-005`, `ARCH-046-WOOCOMMERCE-007` |

## Open Questions

- Confirm real Classic/Blocks pre-submit ordering with LocalWP: no assumption that checkout capture arrives after consent acknowledgement.
- Resolve duplicate active shop/phone rows as a data-quality problem; never accept an ambiguous match as customer opt-in.
- ARCH-048 row-only admission and initial outreach services are Complete, but worker orchestration/activation remain outstanding; no Woo follow-up engine is currently approved.
- Before production Woo outreach, explicitly decide how to accept or mitigate the acknowledged risk of completely undelivered Woo payment/checkout updates.

## Change History

- 2026-10-24: Defined API-007 as a thin versioned consent-write API (v2 envelope with v1 compatibility), removed billing feature lookup from consent write, consolidated transaction-time installation checks, kept STOP/ordering/idempotency, and required before/after SQL measurements. Prior API-006/WooCommerce-008 draft remains a separate, not-yet-materialised handoff in the supplied snapshot. No runtime code or domain `_index.md` changed.
- 2026-10-24: Defined `ARCH-046-BACKGROUND-005` shared recovery-consent merchant notice extraction and added it as a prerequisite to Woo BG-002. New canonical cross-platform deduplication and richer merchant-facing context are permitted without compatibility for older development notices; no domain `_index.md` reconciliation.
- 2026-10-24: Tightened the `ARCH-046-BACKGROUND-005` implementation contract: exact Shopify/Woo decision tables, truth-preserving reason/operation templates, field validation/bounds, operation-sensitive `sourceKey` vectors, duplicate verification and atomic thread/message persistence. No compatibility for older development notices or domain `_index.md` update.
- 2026-10-24: Prepared developer Attempt 1 review handoff for API-007 at API commit `220fa2b` (10/10 PostgreSQL tests, lint/typecheck passed); preserved pending reviewer decision and recorded missing before/after SQL baseline and launcher isolation evidence. No `_index.md` changed.
- 2026-10-24: Defined API-007 as a thin v2-only breaking consent-write API (no legacy v1 compatibility required by pre-production decision), removed billing feature lookup from consent write, consolidated transaction-time installation checks, kept STOP/ordering/idempotency, and required before/after SQL measurements. Prior API-006/WooCommerce-008 draft remains a separate, not-yet-materialised handoff in the supplied snapshot. No runtime code or domain `_index.md` changed.

- 2026-10-20: Initial Woo consent capture and recovery gate proposal.
- 2026-10-21: Removed 72-hour consent expiry, consent-wakeup/poller and consent-blocked CheckoutRecovery rows.
- 2026-10-21: Consolidated Database/Shared ownership, removed third-party consent provider selection, and merged merchant guidance into the checkout UI task.
- 2026-10-21: **Consolidated minimal consent model:** same existing Customer and CustomerPhone; shop-scoped canonical phone lookup allowed with no automatic grant; one `commerce.WhatsAppConsentEvidence` table; no added WooInstallation, reachability, customer-principal, guest-link or erasure structures. Privacy tasks are outside consent and remain superseded for traceability.
- 2026-10-22: Architect coordination reconciled completed task reports, readiness frontier, and ARCH-046 terminal system-test Support dependencies without changing runtime source or architecture completion state.
- 2026-10-22: Developer explicitly completed BACKGROUND-001 after passing self-review. Recalculated direct dependents: BACKGROUND-002, BACKGROUND-004 and SYSTEM-TEST-002 remain blocked by their separate recovery-engine, dependency and manual validation gates; no downstream task was promoted and `_index.md` files were left unchanged.

- 2026-10-25: Verified ARCH-046-BG005 merged notifier in Background source. Promoted BG002 to Ready, narrowed BG004 to the initial-send final consent/STOP permit (pending BG002), aligned canonical sourceKey with accepted runtime and made ARCH-048 BG005 depend on both consent implementations. No follow-up activation or `_index.md` update.
