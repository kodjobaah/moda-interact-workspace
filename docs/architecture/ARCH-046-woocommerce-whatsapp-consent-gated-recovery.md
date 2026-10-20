---
id: ARCH-046
title: WooCommerce WhatsApp opt-in, consent-blocked recovery, merchant notices and later-consent resumption
status: proposed
coordinator: moda_architect
created: 2026-10-20
updated: 2026-10-20
---

# ARCH-046 — WooCommerce WhatsApp consent-gated recovery

## Status

**Proposed; portable canonical task definitions, not materialised/claimed or implemented.** Based on `moda-interact-workspace(20261020-130224).zip` and the supplied `moda_architect` role. Access to the developer's canonical Git common-dir, worktrees and remotes was **not** supplied. No task was committed, pushed or accepted. `ARCH-046` is a newly proposed initiative, distinct from Shopify-specific `ARCH-045`.

This architecture contains a **pre-recovery opt-in phase** that can be implemented independently and a **consent-gated recovery phase that is explicitly blocked** until an architecture-approved WooCommerce recovery lifecycle and authoritative live checkout-state reader exist. **Do not** pretend that the ARCH-035 capture-only code can already send recoveries.

## Problem

WooCommerce currently offers **no single native equivalent of Shopify's 2026-07 WhatsApp marketing-consent authority and consent-change webhook**. WordPress cookie/analytics CMPs and the WP Consent API do **not** themselves demonstrate permission for WhatsApp recovery marketing. The Moda Woo plugin has no checkout WhatsApp consent field, no pre-submission consent publisher, and no hosted opt-in evidence store. The Woo Support screen is rendered but its `src/support/support-client.js` hardcodes `read/send/markRead: false` and cannot yet show hosted system notices.

Crucially, current ARCH-035 (20 October capture-only amendment) authorises Woo checkout/order **capture** only: API-008 and WOOCOMMERCE-007/008 plus dedicated checkout/order workers. It **prohibits** CheckoutRecovery materialisation, recovery sends and billing in that initiative. `woo.activity.v1` is validated/enqueued but its background processing is observational; retained BullMQ jobs are **not** an authoritative checkout-state database. Consent may be designed/collected now; actual recovery gating/resumption cannot be declared operational merely because a checkbox exists.

## Goals

1. Offer a clearly worded, optional, **unchecked-by-default** WhatsApp **abandoned-checkout recovery** opt-in on both Woo **Classic Checkout** and **Checkout Blocks**, including guests and logged-in customers, **only when a merchant has selected Moda as its consent source**. Never automatically install a second visible checkbox alongside another plugin, or require opt-in to purchase.
2. Capture a deliberate opt-in **before order placement**: record it securely when checked during checkout, even if that checkout is later abandoned; never rely solely on metadata saved after a completed order. Associate evidence with the authenticated merchant installation's `shopId`, the stable Woo `checkoutKey`, the exact then-current canonical phone and a versioned disclosure text/purpose. **Re-check/re-consent** when the phone changes. Persist revocation as well as grants, including later interactions on the **same verified Woo checkout session**.
3. Keep the durable, current consent decision, **authoritative merchant consent-source configuration**, and immutable minimal evidence in Moda PostgreSQL, not only in guest WP sessions, Redis or a merchant-controlled WordPress table. WordPress transmits evidence through its existing credential-protected hosted API; no browser sees installation credentials or Moda database secrets. Switching a merchant source invalidates prior grants for recovery admission without deleting audit evidence.
4. Where and when an **approved Woo recovery lifecycle actually exists**, block initial business-initiated WhatsApp recovery unless a **current** positive evidence record matches the same `(shopId, checkoutKey, canonicalRecipient, purpose)`; leave the recovery `DETECTED`, notify the merchant once through existing `MerchantSupportMessage`, and consume **zero** recovery credits/outbound attempts.
5. Upon a later explicit grant in the same legitimate checkout session, automatically reevaluate and, if still eligible and unexpired, resume **the same** Woo recovery generation. Never resume from a merely unchecked/unknown state, a phone-only match, a revoked consent, another shop or an expired/completed checkout. Apply the gate to proactive recovery follow-ups and merchant post-window outreach too.
6. Make Woo merchant notices actually visible through a **bounded authenticated, read-only Support notice API/proxy**, without inventing a new cross-tenant notification transport or enabling unimplemented Support sending.
7. Provide `WooCommerce > Moda Interact > Recovery settings` with a persisted source choice: **Not configured / Moda checkbox / Supported external plugin**. The third choice is selectable **only** for a specifically approved, installed and active integration with verified grant and withdrawal evidence; no such provider is asserted to exist in the supplied snapshot. Prevent double collection, source-switch stale grants and bypass through settings. Preserve 20 Woo merchant languages, WordPress-native i18n, the intentional two-stage navigation, HPOS and tenant isolation.

## Non-Goals

- Cookie consent, WP Consent API tracking categories, browser analytics or a marketing pixel. Do not treat GDPR cookie-banner approval, an email newsletter checkbox or generic terms acceptance as WhatsApp opt-in.
- A compulsory checkbox; prechecked or silently inferred consent; collecting opt-in via merchant-admin toggle; writing to Shopify Customer Privacy API; reusing Shopify `customers_whats_app_marketing_consent/update` payloads in Woo.
- Permission to send an unsolicited WhatsApp message seeking the customer's opt-in. The merchant must use a permitted website/account/checkout method or an already authorised channel.
- Building or enabling the missing Woo **recovery engine**, live Woo checkout-state query, order-completion correlation, offers, provider orchestration or billing under the guise of consent work. Those require independent approved architecture/tasks before blocked Background admission tasks become executable.
- A general-purpose cross-plugin CMP interoperability framework, new externally exposed Gateway service, third-party Woo plugins as a source of automatically trusted consent, or speculative phone-ownership OTP flows. No unverified auto-detection/field-label matching, generic `wp_has_consent('marketing')` inference, or acceptance of an arbitrary plugin-provided Boolean as a grant. Actual integration with a specific external provider requires evidence and its own bounded architect-approved adapter task; no provider is pre-certified by this proposal.
- Extending consent captured for **this checkout** to a different checkout, different phone/customer or another merchant without a separate affirmative authorisation rule. v1 is intentionally checkout-scoped.

## Current Architecture — inspected snapshot

- `moda-interact-woocommerce/includes/Runtime.php` boots only merchant Admin controllers (and no checkout consent hooks); `includes/Plugin.php` declares HPOS compatibility. No `woocommerce_register_additional_checkout_field` or consent persistence/publisher currently appears in the plugin. `src/support/support-client.js` declares all Support capabilities false; `src/support/support-thread.js` displays "Support messages are not yet available for WooCommerce".
- `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md` contains the authoritative **2026-10-20 capture-only amendment**. `ARCH-035-API-008` is marked Complete in its task YAML, while `ARCH-035-WOOCOMMERCE-007` is marked Ready in the supplied snapshot (not evidence of live deployment); the capture event publisher/source contracts remain version `woo.activity.v1`.
- `moda-interact-api/src/woocommerce/activity/{contract,producer,routes}.ts` implements only `CHECKOUT_UPDATED`, enqueueing on `woo-checkout-capture-v1` with shop identity derived from the Woo installation authenticator, not caller-supplied. The API **does not** presently receive customer opt-in evidence.
- `moda-interact-database/prisma/schema.prisma`: existing `CheckoutRecovery` has `status=DETECTED`, `detectedAt`, `admissionBlockedAt` and `admissionBlockReason`; `RecoveryAdmissionBlockReason` currently lists capacity/recipient suppression only; `MerchantSupportMessage.sourceKey` is globally unique. `WooCommerceInstallation` holds authenticated connected shop identity.
- Existing recovery processors in `moda-interact-background/src/services/checkout-recovery/` use Shopify-specific checkout reads and are **not** an authorised Woo recovery implementation. Existing merchant system notice storage is reusable but Woo's UI needs an authenticated hosted read/proxy.
- `ARCH-045-DATABASE-001` is the **only** planned owner of the generic `WHATSAPP_CONSENT_MISSING` admission-block enum. Do not introduce an identical enum value through a second competing migration. ARCH-046 Background admission declares an explicit dependency on its accepted completion.

## Proposed Architecture

### A0. Merchant selects exactly one consent collector (can start now)

- Canonical source mode is `NOT_CONFIGURED` (default), `MODA_CHECKBOX` or `SUPPORTED_EXTERNAL`; external mode also identifies one **explicitly certified provider adapter**. Store the active mode, provider identity and monotonically increasing **configuration epoch** under the merchant's Woo `shopId` in hosted PostgreSQL. WordPress may cache the last acknowledged configuration for display, but is **not** the Background authority. `NOT_CONFIGURED` and an unregistered/unavailable external provider never permit proactive recovery sending.
- Introduce a narrowly scoped authenticated, server-to-server consent-configuration read/write API, separate from consent-event ingestion. The WordPress Recovery Settings control requires existing merchant admin capability and REST nonce, writes through the connected installation, and reports a successful switch only after hosted durability. An API outage must not create a false configured/safe state; do not fall back to local-only acceptance.
- **One visible checkbox:** Moda registers/renders its own field only for acknowledged `MODA_CHECKBOX` mode; hide it for `NOT_CONFIGURED` and `SUPPORTED_EXTERNAL`. Do not decide from another plugin's label, DOM or installed-plugin flag. Recognised plugin detection can offer **advisory guidance** only. If a different plugin already renders an overlapping checkbox, the merchant chooses its collection strategy and disables duplicate collection; Moda must not silently trust it.
- On every source switch, including disable, increment the hosted epoch. Consent evidence is stamped with the accepted epoch and source/provider. Background checks the **current** mode, provider and epoch as well as the exact checkout/recipient/purpose. Old grants from a former source or epoch are instantly ineligible for new sends without needing mass revocation or scanning all checkouts. In-flight attempts are rechecked at the final possible provider-admission boundary. Historical evidence remains for retention/privacy handling.
- `SUPPORTED_EXTERNAL` is **not** a generic checkbox connector: it remains visibly unavailable until an approved provider-specific adapter supports authenticated checkout identity, explicit positive action, disclosure/purpose, exact current phone, pre-abandonment persistence, withdrawals and source-event idempotency. No named adapter is approved in this snapshot, so the merchant cannot select a fabricated provider. When one is approved, it must publish through the same hosted consent-write path with the correct source/epoch, not directly set a global marketing flag. WP Consent API cookie/tracking categories are not WhatsApp outreach consent.

### A. Explicit checkout opt-in with pre-abandonment persistence (can start now)

- When the merchant has chosen and durably acknowledged `MODA_CHECKBOX`, register an optional, **initially unchecked**, purpose-specific consent input for Classic and Blocks using supported Woo checkout extension points. For Checkout Blocks evaluate `woocommerce_register_additional_checkout_field` and appropriate Store API pre-submit update hooks; for Classic evaluate native checkout fields/hooks and an explicit change submission. **Verify with real LocalWP tests** that a checked box is durably transmitted to hosted Moda *before order placement*, as Woo's field/order persistence semantics differ across modes and versions. Never infer that registration alone proves an abandoned guest's consent was received.
- Suggested disclosure meaning, to be finalised by merchant/legal review and localised: "I agree that [store] may send WhatsApp reminders about this unfinished checkout to the mobile number entered here. I can withdraw my consent at any time." The actual versioned text approved/shown must be tied to the stored consent evidence. An opt-in is optional, separate from the purchase, and never preselected.
- The WP plugin accepts Moda-checkbox consent changes **only when Moda is the acknowledged active source** and **only from the current Woo checkout session** using applicable Store API nonce/cart token/WordPress anti-CSRF/session controls and the `checkoutKey` produced by ARCH-035-WOOCOMMERCE-007; it binds the **current checkout phone at the time of the affirmative action**. No arbitrary browser-supplied `shopId`, checkoutKey or phone may be trusted without server/session validation. A changed phone invalidates the previous grant for the changed checkout; grant for the new phone requires a new explicit affirmative action. Initial unchecked/default state is **not** a revocation event.
- WordPress uses its existing connected-installation credentials server-to-server for a bounded API-owned versioned route (`POST /v1/woocommerce/whatsapp-consent`, illustrative exact route owned by API-001). Transport retries use existing Woo Action Scheduler; the **same eventId and sourceRevision** survive retry. Shopify and Woo paths never share consent-source authentication. Shopper checkout must continue when the API is unavailable, but **hosted consent remains unknown and no message is authorised** until durable API acceptance. Do not claim successful hosted capture merely because a client checkbox was clicked.
- For the v1 later-consent case, a customer may return to the **same** legitimately bound checkout/session, enter a valid phone and newly opt in. The plugin emits the new explicit grant and the same checkout identity; no unsolicited contact is required. Checkout session expiry/identity mismatch means this path cannot be assumed to work, and the old recovery must remain blocked or expire. A general unrelated guest "type a phone and grant" endpoint is specifically prohibited.

### B. Authoritative hosted consent/evidence state (can start now)

- `moda-interact-database` creates shop-scoped current source configuration and a compact consent current-state model plus append-only minimal evidence/change-outbox model under a Woo-owned schema or existing approved commerce schema. Canonical key is `(shopId, checkoutKey, recipientCanonical, purpose=WHATSAPP_CHECKOUT_RECOVERY)`. Current decision `GRANTED`/`REVOKED` is separate from no record (= unknown/not authorised). Record `evidenceEventId`, monotonic checkout source revision, text-version, **source mode, approved provider ID where applicable and hosted configuration epoch**, server receipt timestamp, and optional bounded client occurrence time. No full browsing activity or arbitrary HTML, cookies or customer payloads are stored.
- Enforce uniqueness for event ID and `(shopId,checkoutKey,sourceRevision)` so retries are idempotent, conflicting replays reject, and a **late retry of an old grant cannot overwrite a later revocation**. Across phone changes, revoke prior granted recipient before allowing new opt-in; the plugin cannot silently transfer permission. Persist current projection and durable pending change evidence in **one PostgreSQL transaction**. This commit is the HTTP **durable acceptance point**; do not synchronously require both PostgreSQL commit and Redis publication.
- A Background consumer may inspect a bounded `PENDING` change-outbox and, when an approved Woo recovery runtime exists, wake the exact checkout's blocked recovery. No new Shared queue schema or package publication is required for this database-backed cross-repository handoff; Prisma schema/migration and an API-owned versioned HTTP OpenAPI contract are the canonical boundaries. This avoids a competing local runtime schema copied between services. Add a Shared contract **only** if a real future queued wire boundary is approved by the architect.
- A Background-local injected `WooCheckoutRecoveryConsentReader` reads current hosted **source configuration and consent** by exact `shopId`/`checkoutKey`/recipient, not by a customer's asserted phone alone. Explicit `GRANTED` **for the active acknowledged source/provider and current configuration epoch** is necessary; no configuration, no match, revoked, stale revision, provider mismatch, data unavailability or source ambiguity fail closed. Re-check immediately before irreversible provider dispatch. An unacknowledged WP checkbox, pending HTTP retry, stale UI or generic WP tracking consent never authorises delivery.

### C. Recovery blocked → merchant notified → later grant (blocked until approved Woo recovery runtime)

1. Existing authorised Woo recovery engine detects a genuinely abandoned checkout and has a recoverable, stable checkout identity plus an authoritative way to confirm that checkout remains unpaid/uncompleted. **This capability is currently missing**; ARCH-035 capture-only jobs must not be repurposed as an authoritative reader.
2. At initial action admission, resolve the **actual outbound** canonical WhatsApp recipient and check exact Woo consent evidence. If no verified current grant, keep `CheckoutRecovery.status=DETECTED`, set `admissionBlockReason=WHATSAPP_CONSENT_MISSING`, and create one `MerchantSupportMessage` SYSTEM notice with deterministic `sourceKey=arch046:consent-missing:<recoveryId>`. No sequence-one attempt, reservation, charge or provider send. Missing phone is the distinct ARCH-028 no-recipient case, **not** missing consent.
3. Merchant Support notice explains consent was not verified, no message/credit used, and a **customer-initiated** return to the same checkout **may** allow re-evaluation before expiry. Do not promise that merely checking a box elsewhere will resume this recovery; never ask merchant to bypass consent.
4. Choose the same **provisional** 72-hour consent wait as ARCH-045, measured from immutable `CheckoutRecovery.detectedAt` (not extended by retries). **Additionally**, an earlier verified Woo checkout/session expiry or terminal order state wins. Exact active-cart expiry rules and checkout-state reader are an external Woo recovery-lifecycle prerequisite, not made up by this consent initiative.
5. Later pre-submit grant commits in the hosted API and creates a durable change receipt. When the blocked Woo recovery runtime is approved, Background consumes bounded receipts, matches `(shopId, checkoutKey, exact current recipient)`, re-reads **latest** consent, verifies original checkout still exists and is abandoned and open, original generation/eligibility, recipient suppression, entitlement, expiry and any order completion; then resumes **the original** sequence-one admission exactly once. A revoke, duplicate, older grant, stale phone, out-of-window event or completed order never sends.
6. A deadline job/periodic bounded repair expires outstanding blocked recoveries without a consent update; do not poll all active recovery candidates every minute or leave orphan blocks because one job was lost. Consumer failures are retryable; no duplicate merchant notices, attempted sends or credit usage.
7. Scheduled sequence-two and merchant post-window recovery templates use the same injected reader, with one final near-provider consent gate and correct unused-attempt/credit correction. Ordinary customer-initiated WhatsApp service-window replies retain their separate permission rules and existing suppression/moderation checks.

### D. Merchant Support visibility and setup

- Recovery Settings is now the **source-selection** authority in the merchant-facing UI. The WordPress server submits configuration to the dedicated hosted API; its acknowledged mode and epoch determine whether Moda renders its own checkbox. `NOT_CONFIGURED` is the safe initial state. An existing checkbox from another plugin does not turn on external mode or imply any permission.
- External selection must list only integrations that have passed an explicit checkout + withdrawal + exact-recipient certification. When none exists, show “No supported consent provider integration available” and explain that the merchant may use Moda's own checkbox or remain disabled; do **not** offer a generic “trust other plugin” switch.
- Record which collection source applies and warn the merchant about duplicate checkout opt-ins and **duplicate abandoned-cart messaging workflows**. Moda cannot deduplicate sends performed by another independent plugin; the merchant must configure one recovery sender.

- The authoritative system notification remains existing `MerchantSupportThread`/`MerchantSupportMessage`, tenant scoped; no merchant WhatsApp alert to a new number and no extra email/SMS channel.
- `moda_api` exposes a **read-only** installation-authenticated, strictly paginated projection of the shop's system/support notices. `moda_woocommerce` provides a WordPress permission-checked REST proxy and connects the existing **Support** screen for read-only message view. Do **not** enable unsupported send/mark-read actions or copy Shopify session cookies.
- Under `WooCommerce > Moda Interact` → existing top-level Moda Interact → `Recovery settings`, show native opt-in status/setup guidance, 20-language translations and a clear explanation of the difference between site tracking consent and WhatsApp recovery consent. Do not move or duplicate the intended two-stage WordPress menu.
- Notification delivery failure is observable and retryable with deterministic `sourceKey`; it never opens a send/credit bypass.

## Flows

```text
Woo Classic / Blocks checkout (guest or account)
  -> user affirmatively checks optional WhatsApp recovery opt-in
  -> same checkout session + checkoutKey + exact current phone verified by WP plugin
  -> WP server authenticated POST -> hosted Moda API (Shop from installation)
  -> PostgreSQL transaction: consent projection + append-only event/outbox
  -> 2xx (durable receipt); guest can still abandon without placing order

Approved Woo recovery engine [NOT PRESENT in current snapshot]
  -> abandoned checkout + authoritative Woo status recheck
  -> current checkout-scoped consent for exact phone
        | GRANTED -> existing provider/billing admission once
        | unknown/revoked -> DETECTED + consent-blocked + one Support SYSTEM notice
                              no charge, no customer WhatsApp

Customer later returns to same valid checkout and grants permission
  -> same durable consent API/outbox -> bounded Background wakeup
  -> fresh consent + checkout/order/recipient/expiry checks
  -> still eligible? resume once / otherwise remain blocked or expire
```

## Repository Responsibilities

| Owner | Repository | Approved outcome |
|---|---|---|
| `moda_database` | `moda-interact-database` | Minimal durable current consent + immutable change/outbox projection with idempotency, indexes and migration |
| `moda_api` | `moda-interact-api` | Installation-authenticated consent-write route; separate shop-authenticated read-only merchant Support notice projection |
| `moda_woocommerce` | `moda-interact-woocommerce` | Classic/Blocks opt-in UI, pre-order event capture + retry, later checkout return/revocation, Support proxy/UI and Recovery Settings guidance |
| `moda_background` | `moda-interact-background` | Exact consent reader (can start); initial admission notice, later-grant re-entry and proactive follow-up gate **blocked by absent approved Woo recovery engine** |
| `moda_system_test` | `moda-interact-system-test` | Staged real LocalWP consent capture certification; terminal end-to-end recovery/notice/billing/resume certification after engine approval |
| `moda_architect` | Workspace docs | Coordinate with ARCH-035 capture-only and ARCH-045 generic enum; approve any future Woo recovery lifecycle separately |

No new `moda_gateway` task is justified from the current snapshot: existing HTTPS hosted API and Redis/PostgreSQL services suffice, and no new Render process/service is required. Reassess if actual deployment requires a new ingress/worker topology.

## Data Model / Contracts

**Current consent key:** `(shopId, checkoutKey, recipientCanonical, purpose)`, required unique index; `purpose=WHATSAPP_CHECKOUT_RECOVERY` fixed for v1. Store `decision=GRANTED|REVOKED`, latest sourceRevision, latest eventId and timestamps; absent = not authorised. **Append-only evidence/change receipt:** one row per authenticated eventId with `(shopId,checkoutKey,recipientCanonical,kind,sourceRevision,disclosureVersion,source,receivedAt)`, unique event identity, bounded consumer/lease state, retries and an explicit terminal/no-op receipt retirement policy. Sensitive fields have defined privacy access/retention; no full checkout payload, location/cookies or gratuitous marketing profile. Contract/migration owner: DATABASE-001.

**Versioned HTTP:** API-owned `woo.whatsapp-consent.v1`, `POST /v1/woocommerce/whatsapp-consent` (illustrative), authenticated with the **existing Woo installation principal**. Request includes `schemaVersion`, `eventId`, `sourceRevision`, `checkoutKey`, `recipientPhone`, `decision=GRANT|REVOKE`, `disclosureVersion`, `occurredAt`; **no shopId**. API resolves shop identity, validates strict bounds, canonicalises recipient and rejects invalid/conflicting stale evidence. WordPress PHP calls server-to-server with its existing `ModaApiClient` installation headers; no browser access to credentials. Producer: Woo plugin; contract owner/validator: `moda_api`; state owner: `moda_database`; consumer for current decision: `moda_background` using Prisma. No TypeScript Shared publication is needed merely to transfer a PHP-owned HTTPS payload.

**Merchant notice read API:** API-owned bounded `GET /v1/merchant/support-notices` (illustrative exact path decided by API-002); Woo installation auth resolves the shop and returns only messages belonging to that shop. WordPress REST facade checks merchant capability/nonce; existing React Support screen renders **read only** (send/mark-read remain unavailable).

**Cross-architecture enum dependency:** `ARCH-045-DATABASE-001` owns `RecoveryAdmissionBlockReason.WHATSAPP_CONSENT_MISSING`. ARCH-046's admission tasks consume it only after completion; ARCH-046-DATABASE-001 must **not** duplicate that migration. The two platforms do **not** share actual consent source/readers: Shopify queries Shopify Admin GraphQL, Woo reads its own hosted consent records.

**Live Woo recovery capability:** NOT defined by ARCH-035 capture-only or these consent tasks. Before unblocking BACKGROUND-002/003/004, the architect must accept a separate contract covering (a) durable Woo recovery materialisation, (b) current authoritative checkout/cart/order state and checkoutKey mapping, (c) cancellation on payment/order, (d) recipient selection, (e) provider send and credit admission. Do not fabricate a task ID for work that has not been approved/defined.

## Consistency / Ordering / Failure Handling

- The **PostgreSQL commit** of current state plus change receipt is the consent-write durable acceptance point. Do not require Redis enqueue inside the HTTP transaction. Background may use a bounded lease/claim over durable pending consent-change receipts; no exactly-once delivery assumptions. Old or inapplicable change receipts must transition to an explicitly terminal, bounded retained/archived state rather than remaining PENDING forever; this is distinct from the minimal retained audit evidence.
- `eventId` idempotency and strictly monotonic **checkout-scoped** sourceRevision, plus a separate **shop configuration epoch**, prevent a retry of an old grant or former provider source from defeating a newer withdrawal or configuration switch. An equal revision with different payload fails closed and is not accepted as a new grant. Revocation wins when events race; unsynchronised event sources cannot overwrite a more recent revocation. Use server-received timestamps for audit, not client time for ordering.
- Checkout identity and recipient are attached by plugin server-side from the live Woo session, not accepted from arbitrary browser JSON. A source phone change invalidates the previous recipient grant; no cross-checkout phone-only grants. Guest account/session expiry or missing current checkout identity fails closed; a consent event cannot resurrect an expired checkout.
- Retry outbox on transient API/DB failure; WordPress checkout must not be blocked by remote unavailability. A checkbox change without hosted acknowledgement is **not accepted permission** for recovery. API stale/conflict/invalid requests are not retried indefinitely. Provider send never proceeds on an unverifiable record, API outage, stale grant or unconsented phone.
- Merchant notice insertion is idempotent using `sourceKey=arch046:consent-missing:<recoveryId>`. Failed notice writes must be retryable independently of recovery sending. Terminalisation and consent re-entry must respect existing checkout-scoped locks, generation uniqueness and provider/credit correction semantics.
- The practical race boundary is the final near-provider check versus provider handoff; withdrawal **after** an irreversible provider handoff cannot unsend a message. Never claim atomicity across WordPress, PostgreSQL and Meta.

## Scalability / Security / Observability

- Do **not** check consent on every Woo cart update; capture consent changes only. In recovery, check at actionable admission and proactive follow-up only. Outbox jobs are bounded by `(shopId,checkoutKey)`; no global scan of all Woo checkout events. Distinguish measured versus assumed workload; no throughput capacity claim is made from the snapshot.
- Authenticate every hosted call with current Woo installation secrets server-side; derive `shopId` from authenticated installation, require Woo platform, enforce token rotation/revocation. Protect storefront submit against CSRF and anonymous session spoofing, validate server-side checkout/phone, reject fabricated shop/order identifiers. PHP should never contact PostgreSQL/Redis directly. Respect Woo HPOS and WP minimum version.
- Use `@modainteract/moda-interact-shared/logging` for Node API/Background semantic logs; use WordPress-native bounded/redacted diagnostics in PHP, **not** an invented PHP import of Node Shared. Never log full phone, email, consent checkout fields, auth headers or secrets. Reuse standard HTTP/BullMQ instrumentation before adding metrics; no new generic logger/OTel duplicate. Logs distinguish grant/revoke/unknown/unavailable, merchant notice, resume, expiration and duplicate.
- Retention, consent disclosure version and customer privacy export/erasure must be reviewed before a live launch. Implement the smallest supported deletion/erasure integration as part of owning tasks when the actual Woo/Moda privacy interfaces can be verified; **do not** claim this proposal alone establishes legal compliance. Existing Meta recipient suppression, STOP/opt-out signals and local consent revocation are all additional fail-closed gates.

## Rollout / Migration

**Provisional pre-production design; deployment classification requires actual live status from developer.** Snapshot/task YAML is not proof of production rollouts. Safe order: database consent/source-config migration → authenticated API configuration endpoint → merchant Recovery Settings source selection and conditional Classic/Blocks checkbox → consent writer/API and pre-submit capture (requires ARCH-035-WOOCOMMERCE-007) → later-return/revoke path and merchant notice read/support UI → consent-only LocalWP integration tests. Until a source is configured/acknowledged, the checkout checkbox is hidden and hosted recovery consent fails closed. **No WhatsApp recovery may be enabled at this stage.** After a separately approved Woo recovery architecture and `ARCH-045-DATABASE-001` become Complete, implement Background admission/notice/resumption/follow-up gates, deploy those **before** enabling any Woo business-initiated recovery send, manually validate on LocalWP, then run the full terminal black-box system test.

If production Woo stores already exist, ensure additive migration and source revision compatibility. Do not rewrite or infer consent from old customer/order/checkout data. Historic unconsented checkouts remain non-sendable. Do not destroy live queue data. Before enabling consent publishing for live merchants, ensure either the accepted wakeup consumer or a bounded no-op/expiration receipt-drain is deployed: pre-recovery testing may run on LocalWP, but production must not accumulate an indefinite PENDING outbox backlog while BG003 remains Blocked. WordPress plugin upgrade and 20-locale release tests are required for storefront/UI work.

## Decisions / Tasks

States below represent **portable definition eligibility** only, not claimed worktrees/commits. `blocked` means a proven external Woo recovery-lifecycle prerequisite does not yet exist.

| Task | Owner | Status | Depends on (fully qualified; only defined tasks) |
|---|---|---|---|
| ARCH-046-DATABASE-001 | moda_database | ready | — |
| ARCH-046-API-003 | moda_api | pending | ARCH-046-DATABASE-001 |
| ARCH-046-API-001 | moda_api | pending | ARCH-046-DATABASE-001; ARCH-046-API-003 |
| ARCH-046-API-002 | moda_api | ready | — |
| ARCH-046-WOOCOMMERCE-001 | moda_woocommerce | ready | — |
| ARCH-046-WOOCOMMERCE-002 | moda_woocommerce | pending | ARCH-035-WOOCOMMERCE-007; ARCH-046-API-001; ARCH-046-WOOCOMMERCE-001; ARCH-046-WOOCOMMERCE-005 |
| ARCH-046-WOOCOMMERCE-003 | moda_woocommerce | pending | ARCH-046-WOOCOMMERCE-002 |
| ARCH-046-WOOCOMMERCE-004 | moda_woocommerce | pending | ARCH-046-API-002 |
| ARCH-046-WOOCOMMERCE-005 | moda_woocommerce | pending | ARCH-046-API-003 |
| ARCH-046-BACKGROUND-001 | moda_background | pending | ARCH-046-DATABASE-001 |
| ARCH-046-BACKGROUND-002 | moda_background | **blocked** | ARCH-045-DATABASE-001; ARCH-046-BACKGROUND-001; **external Woo recovery engine approval absent** |
| ARCH-046-BACKGROUND-003 | moda_background | **blocked** | ARCH-046-BACKGROUND-002; ARCH-046-API-001; ARCH-046-WOOCOMMERCE-002; **external Woo recovery engine approval absent** |
| ARCH-046-BACKGROUND-004 | moda_background | **blocked** | ARCH-046-BACKGROUND-001; ARCH-046-BACKGROUND-002; **external Woo recovery follow-up approval absent** |
| ARCH-046-SYSTEM-TEST-001 | moda_system_test | pending | ARCH-046-DATABASE-001; ARCH-046-API-001/003; ARCH-046-WOOCOMMERCE-001/002/003/005 (full IDs in task YAML) |
| ARCH-046-SYSTEM-TEST-002 | moda_system_test | **blocked** | all required implementation above, ARCH-045-DATABASE-001; **external Woo recovery engine approval absent** |

The `ARCH-035` capture-only implementation remains independently valid and must **not** be modified to add recovery effects. No non-system-test task depends on a system-test task. Developer manually validates after implementations are accepted, before executing Ready terminal system tests.

## Open Questions / Explicit policies

1. **72-hour v1 consent wait** is copied as a **provisional Moda product choice** from ARCH-045, **not** a WooCommerce law/API requirement. A known earlier Woo cart/session expiry, checkout expiration or paid order overrides it. Do not use 72 hours to invent a usable cart session beyond actual Woo validity.
2. v1 consent is **shop + checkout + recipient + purpose scoped**. A new phone, different checkout/guest, disconnected session, old marketing plugin flag or WP cookie banner cannot resume the old recovery; returning to the verified same checkout and explicitly consenting can. A general My Account/global subscription preference could be a future architecture, **not silently assumed here**.
3. Retention and privacy export/erasure handling need merchant legal/privacy review and a concrete owner-approved implementation before live rollout. No blanket legal-compliance certification is made.
4. The exact Woo checkout-state reader and complete Woo recovery engine are **outside the current source snapshot and ARCH-035**, and must be separately designed/approved before BG002/BG003/BG004 and SYSTEM-TEST-002 move from Blocked.
5. The API-owned example route names are design decisions to be pinned by API-001/API-002/API-003; they are **not** claims that deployed endpoints already exist.
6. **No third-party Woo consent plugin is approved by name in this snapshot.** The external-provider option must remain unavailable until a concrete provider adapter passes a separate bounded approval/implementation/review. Do not auto-enable based on detecting installed plugins or a cookie-consent category; source selection is not a grant.

## External sources verified 2026-10-20

- WooCommerce [Additional checkout fields](https://developer.woocommerce.com/docs/block-development/extensible-blocks/cart-and-checkout-blocks/additional-checkout-fields/) — unchecked, optional custom fields for Checkout Blocks, plus contact/account/order persistence semantics.
- WooCommerce [Updating cart on demand](https://developer.woocommerce.com/docs/apis/store-api/extending-store-api/extend-store-api-update-cart/) — `woocommerce_store_api_register_update_callback`/`extensionCartUpdate` server-side client changes.
- WooCommerce [Store API updates 9.8](https://developer.woocommerce.com/2025/04/02/store-api-updates-coming-in-woocommerce-9-8/) — draft checkout update mechanism and pre-order field persistence; **requires actual Classic/Blocks validation**, not an assumption.
- WooCommerce [Customising checkout fields](https://developer.woocommerce.com/docs/code-snippets/customising-checkout-fields) — Classic shortcode checkout differs from Checkout Blocks.
- WooCommerce [Consent mode and WP Consent API](https://woocommerce.com/document/google-analytics-integration/) — visitor tracking consent is distinct from messaging permission.

## Change History

- 2026-10-20: Attempt 2 consent-source clarification: introduce hosted merchant mode/epoch, default OFF, conditional Moda checkbox, and external-provider certification gate; update affected tasks and add API-003 configuration owner.
- 2026-10-20: Initial Woo-specific consent architecture/task proposal, source-reconciled against supplied 20 October snapshot and Shopify ARCH-045. Explicitly prevented activating Woo recovery in capture-only ARCH-035, avoided duplicate generic admission enum, and reserved customer-initiated return-to-checkout consent resumption for approved future Woo recovery execution.
