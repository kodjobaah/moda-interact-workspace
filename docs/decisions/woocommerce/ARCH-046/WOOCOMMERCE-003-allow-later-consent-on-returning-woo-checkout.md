---
id: ARCH-046-WOOCOMMERCE-003
architecture_id: ARCH-046
title: Complete returning Woo consent, v2 publishing and verified checkout status
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-23T13:39:33Z
attempt: 1
depends_on:
  - ARCH-046-WOOCOMMERCE-002
enables:
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-11-01
---

# Complete returning Woo consent, v2 publishing and verified checkout status

## Developer Ownership Amendment

On 2026-10-23, `/moda_developer_create ARCH-046-WOOCOMMERCE-003` was invoked
while this task was ready and agent-owned. This is an explicit developer
takeover. `execution_mode` and `completion_mode` are now `developer`;
`assigned_agent: moda_woocommerce`, repository ownership, dependencies, scope
and acceptance criteria are unchanged. The task remains at Attempt 0 until
canonical preparation claims Attempt 1.

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** materialised and published on parent branch `task/ARCH-046-WOOCOMMERCE-003` during developer takeover from the committed portable definition. No implementation claim existed before canonical preparation.

## Objective

Complete the **existing** `ARCH-046-WOOCOMMERCE-003` implementation, rather than opening `WOOCOMMERCE-008`, by (a) retaining safe later GRANT/REVOKE capture, (b) upgrading the Woo consent publisher to the **breaking v2-only** hosted write contract, and (c) rendering **one consistent, always-visible consent checkbox** in **Classic and Blocks** checkout: **initialised checked only for currently verified effective GRANTED consent**, otherwise **initialised unchecked**; after a deliberate shopper change, the checkbox keeps that local selection regardless of request outcome. A deliberate uncheck of a verified, checked control is the sole withdrawal action; do not display a second button or confirmation popup. Moda failures must be invisible to shoppers and must never impede the merchant checkout; internal failures must still be logged safely. No guest/customer may be identified by a phone match alone.

## Context

The developer's dedicated WOO-003 worktree already edits `includes/Checkout/CheckoutConsentCheckbox.php`, `CheckoutConsentCapture.php`, `CheckoutConsentPublisher.php`, `assets/js/checkout-consent-classic.js`, `tests/CheckoutConsentReturningTest.php` and the returning-consent documentation. Its `select` field for earlier permission is an intermediate implementation, not the desired final UI. Creating an additional Woo-owned WOO-008 task would produce overlapping edits and merge conflicts. This scope amendment extends **the already claimed Attempt 1** and does not reset or supersede prior work.

API-007 changes `POST /v1/woocommerce/whatsapp-consent` to `woo.whatsapp-consent.v2` **only** (no production v1 compatibility); its approval/deployment is still an external gate. API-006, the authenticated **proof-backed shopper status read**, is **absent from both supplied 2026-10-24 workspace snapshots** and remains an independently owned API task to define, accept and deploy. Do not invent its endpoint or response payload locally. WOO-003 cannot claim the returning-status read works end to end until the API-006 contract and hosted implementation exist. No `ARCH-046-WOOCOMMERCE-008` task is required.

**Architect clarification — 2026-10-31 (final independent-checkbox decision, superseding response-driven display rules):** In both Classic and Blocks, the native checkbox responds immediately to each deliberate customer check or uncheck and remains enabled while Moda status/GRANT/REVOKE requests are pending, rejected or timed out. For a stable shopper/phone, retain the last **local UI choice** across checkout refresh and failed requests; do **not** re-check, uncheck or disable it because of any backend acknowledgement/failure. A fresh checkout/contact identity initialises from proof-backed API-006 status (otherwise unchecked) and never publishes consent automatically. The **server-side** decision remains the last confirmed GRANTED/REVOKED state unless an authenticated command actually succeeds; UI checked/unchecked is **not** consent evidence or permission to send. If transport times out after a possible server write, the actual outcome is uncertain and must be reverified, never guessed. There are no customer-facing Moda notices, confirmation popups or checkout blockers. This newer clarification overrides earlier 'restore checked after failed REVOKE' and 'check only after GRANT ACK' phrasing throughout the task.

**Architect clarification — 2026-10-31 (snapshot 10, updated single-control decision):** The developer has now explicitly selected a checked/unchecked consent checkbox instead of the earlier granted-status-only display. This clarification **supersedes** every earlier instruction in this task to hide the checkbox, replace it with an "already granted" message, or expose a customer-facing consent error/pending/status notice. The disclosure and single checkbox are the only shopper-facing Moda consent UI. Deliberate uncheck triggers protected withdrawal without an extra button or confirmation dialog; operational failures must remain invisible. Preserve the existing `in_progress` developer claim, Attempt 1, repository ownership, and API-006/API-007 acceptance gates. This is an amendment of the existing task, not a new execution claim.

**Architect decision — 2026-11-01 (passive consent, superseding feature-entitlement capture gates):** API-007 already removes plan/feature lookups from the v2 authenticated consent **write**. For WOO-003, a customer's deliberate consent is evidence of their choice, not a recovery entitlement. The plugin must therefore remove its `GET /v1/merchant/feature-preferences` call from the GRANT path; no `checkout_recovery.effective` or `planEligible` requirement applies to consent GRANT/REVOKE. This supersedes older references below to fresh feature eligibility on writes, feature-dependent checkbox activation and `capture_observe_feature_ineligible` for otherwise valid consent. Keep locally validated installation/site identity, authenticated API write, nonce/Cart Token, session, canonical contact, idempotency, protected proof and STOP non-override. Independently enforce feature/plan/consent/STOP at **recovery admission and final send**. Preserve the in-progress developer claim (Attempt 1); no API, Background or database implementation is authorised by this amendment.

## Scope

1. **V2-only producer within WOO-003.** Change the existing server-side event builder, publisher, HTTP client/validator as needed, API contract fixtures, retry assertions, and associated tests to send exactly the six documented v2 top-level fields; remove the old v1 outgoing payload and v1-only tests/examples. No feature-compatibility adapter is required because there are no production users or queued legacy consent events to preserve. Keep the live checkout session/nonce/Cart Token/customer-action validation *inside Woo* instead of serialising checkbox attestation flags to Moda.
2. **Current-consent display within WOO-003.** A read-only, installation-authenticated, server-to-server lookup to the API-006 proof-status operation, *only once an eligible shopper/phone is established and a valid server-held proof is available*. Never permit an anonymous lookup by phone alone, never expose installation bearer credentials or protected proof to checkout JavaScript, and never use a local cached consent value as the definitive current provider state.
3. **Single, truthfully checked checkout consent checkbox.** Remove the Classic and Blocks withdrawal **select/dropdown**, but **never replace/hide the checkbox merely because the customer has consented**. Once proof-backed API-006 confirms effective `GRANTED` without STOP/no-contact for this installation, shopper and canonical phone, render the checkbox **checked and editable**, with the deliberate **checked-to-unchecked user change** invoking the already authenticated/proof-backed REVOKE operation. Do not add a withdrawal button, dropdown or dialog. For `UNVERIFIED`, revoked, unknown, missing/invalid proof, mismatched shopper, unavailable API or other unverifiable status, render the same checkbox **unchecked** (actionable for a new explicit GRANT when the installation, active checkout, shopper/session and recipient validation succeed, regardless of `checkout_recovery` entitlement). Never infer GRANTED from a local flag, phone match, account sign-in, stale HTTP response or unverified write. A verifiable STOP/no-contact state must not be portrayed as active consent or overridden by Woo UI.
4. **Explicit checkbox withdrawal.** When and only when current API-006 proof has verified `GRANTED` for the same shopper, installation, session and canonical phone, a deliberate **user-generated uncheck event** invokes the existing server-side protected `withdraw` command with an explicit-action flag. No separate button, modal or confirmation prompt. The server must independently validate the current proof/nonce or Cart Token, checkout identity and phone, then publish a fresh `REVOKE` v2 event. The checkbox becomes unchecked **immediately on the deliberate user action**, without waiting for hosted acknowledgement, and stays unchecked if the write is rejected or times out; no failure rolls back the UI. The persisted consent remains GRANTED unless a protected REVOKE actually succeeds. A lost/ambiguous ACK requires safe bounded retry or later proof-backed status verification; do not claim that a timeout proves either successful or unsuccessful persistence. Initial unchecked state, hydration, server-controlled `checked` updates, field refresh, stale responses, phone/account/session changes and unknown status must never emit `REVOKE`. A later re-grant requires a distinct deliberate user check and remains subject to STOP.
5. **Proof binding.** After a successful *acknowledged* grant, retain only the minimum necessary server-side event association (immutable grant `eventId`, applicable installation/shop identity, associated canonical-phone binding or keyed digest, revision and current Woo shopper/session binding) needed by API-006. For a signed-in shopper, bind to the authenticated WordPress account using existing supported storage, without inventing a new Moda identity table; for a guest, bind to their verified Woo session/cart identity and do not persist a cross-session guest identity. A grant from a guest must not silently become another account's proof on login/account creation. Never treat an arbitrary `eventId` pasted into a request as sufficient identity proof; API-006 owns the definitive immutable-evidence/current-STOP proof verification. For REVOKE or change of account/phone/installation, invalidate the affected association and pending lookup immediately.
6. **Minimal read load and checkout availability.** Request status only for a stable, verified shop + shopper/session + canonical-phone + proof tuple. Reuse an already validated result within that unchanged checkout context, with bounded short caching only where explicitly safe. Do not call the hosted API on every character typed, every Woo `update_checkout`, every Blocks draft refresh, or when the shopper lacks a trusted proof. Suppress stale responses after identity/phone/session changes. Moda proof-status and consent-write operations are **optional to checkout**; no merchant feature-preferences query belongs to this capture path: avoid synchronous hosted network requests on the checkout page's critical rendering path; use bounded, non-blocking presentation checks and fail closed if prerequisites cannot be established. A failed or slow Moda request must not delay, break or alter WooCommerce cart, checkout, payment, order submission, or unrelated merchant interactions.
7. **No recovery side effects.** Preserve the existing rule that consent write or status read does not create/revisit old CheckoutRecovery rows, publish a recovery wakeup, send WhatsApp messages, consume credits, or clear authoritative WhatsApp STOP. Background owns recovery eligibility and final-send guards.
8. **Twenty locales and accessibility.** Use the configured WooCommerce site/store language for the approved consent disclosure and single checkbox label; no separate withdrawal action wording or modal is displayed. Maintain all 20 supported catalogues, label association, native checked semantics, keyboard/screen-reader handling and accessible focus behaviour. **Do not render Moda operational status, loading, error or success messages** on the merchant storefront, including screen-reader-only alerts/live regions for failures.

9. **Silent to shoppers, observable to operators.** No Moda status-read, feature-read, GRANT, REVOKE, retry, timeout or unexpected exception may inject checkout notices, banners, toast notifications, inline errors, blocking browser alerts, technical reason strings or checkout-validation errors. Do not emit `consent_status_remote_unavailable` or similar codes into visible merchant checkout UI. Keep necessary diagnostics **server-side** via the repository-approved Woo/WordPress structured logger (the Node shared logger is not a PHP runtime import); log bounded non-sensitive event type, code, correlation and HTTP status. Do not log checkout HTML, phone, proof, raw provider payload, nonce, cookie or credentials. Do not swallow exceptions without an appropriate internal diagnostic; failure of the logging sink must itself be isolated from checkout. Do not display any withdrawal confirmation popup or browser `alert` in this flow.

## Out of Scope

- Do **not** create `ARCH-046-WOOCOMMERCE-008`, a separate Woo implementation branch, new checkout customer tables, an unauthenticated phone-number preference API, a My Account consent page, a persistent guest cross-session identity, or Shopify consent changes.
- Do not implement or alter hosted API-006/API-007 code, database schema, Meta STOP processing, Background recovery workers, recovery scheduling or merchant suppression. WOO-003 consumes those separately owned contracts; missing cross-boundary capabilities go back to `moda_architect`.
- No compatibility shim, legacy v1 sender, migration/backfill of old v1 events, new Woo-to-PostgreSQL/Redis connection, or unapproved direct browser-to-Moda call.
- Do not rewrite the checkout UI or use brittle DOM scraping to simulate a separate withdrawal button. Use the existing WooCommerce-native Classic checkbox and the registered Blocks Checkout Fields component.
- Do not add a new merchant/site-facing error UI, checkout-wide failure handler, global `wc_add_notice`, or a success/pending banner to compensate for unreliable consent requests. Silent storefront failure is not permission to skip internal logging, suppress diagnostics from operators, or manufacture consent.

## Requirements

**A. Exact v2 outgoing consent event.** The authenticated Woo server sends only:

```json
{
  "schemaVersion": "woo.whatsapp-consent.v2",
  "eventId": "stable-event-id-for-retries",
  "decision": "GRANT",
  "canonicalPhone": "447400123456",
  "occurredAt": "2026-10-24T10:00:00.000Z",
  "disclosure": {
    "version": "moda.woo.whatsapp-recovery-marketing.v3",
    "locale": "en-GB",
    "text": "Send me WhatsApp shopping updates, reminders and offers."
  }
}
```

- Top-level properties are exactly `schemaVersion`, `eventId`, `decision`, `canonicalPhone`, `occurredAt`, `disclosure`. A withdrawal is `decision: "REVOKE"` with `disclosure: null`; its other top-level fields are identical in shape. Preserve a stable, unique `eventId` and identical payload for retries; a new real action gets a new ID/time. `canonicalPhone` is digits-only E.164 derived from **server-observed** billing contact and country. Time is a canonical UTC millisecond timestamp, with the existing API expiry/ordering limitations explicitly tested. Send displayed translated disclosure text/version/locale, not a guessed English translation or merchant URL embedded in prose.
- Do **not** send `purpose`, `checkoutAction`, `checkoutKey`, `checkoutMode`, `selection`, `source`, `fieldId`, `nonceVerified`, `sessionVerified`, `userInitiated`, `serverObservedPhone`, `verifiedCountryCode`, `shopId`, `customerId` or `merchantSiteUrl` in v2. Preserve the *actual* Woo nonce/Cart Token, active checkout, installation/site identity and deliberate choice-change checks as local PHP behaviour; **feature/plan eligibility is not a consent-write prerequisite**.
- The API ACK is `{schemaVersion:"woo.whatsapp-consent.v2", status:"recorded"|"duplicate", decision, consentRevision, decisionSequence}` with decimal-string revision/sequence. Validate its shape/version and matching decision; an HTTP 200 with an invalid/mismatched body must **not** be treated as durable consent. Stop retry on terminal 4xx conflicts; do not replay stale GRANT after a later REVOKE, STOP, logout, phone change or installation credential rotation. PHP backoff remains bounded and does not extend the server's grant freshness contract.

**B. Verified consent checkbox — authoritative current-state decision table.**

| API-006 / checkout fact for the current authenticated installation + shopper/session + canonical phone | Checkbox presentation | Allowed operation / fallback |
|---|---|---|
| `CONFIRMED_GRANTED` with verified current consent and no authoritative STOP/no-contact | **Checked**, visible and editable unless a request is pending | Read never writes; a deliberate user uncheck invokes a separate server-verified REVOKE command (no modal). Prechecked form submission does not generate GRANT. |
| `UNVERIFIED`, `REVOKED`, `UNKNOWN`, no prior proof or no existing consent | **Unchecked**, visible for a locally valid installation and checkout | A new **deliberate** checked choice may publish `GRANT` for a locally valid installation and checkout even if recovery is disabled or plan-ineligible. Page load and form refresh cannot grant/revoke. |
| Verified STOP/no-contact that can be independently established | **Unchecked**; no active-permission claim, and no actionable control capable of clearing STOP | STOP remains authoritative. Where API-006 intentionally returns opaque `UNVERIFIED`, do not infer the reason; all hosted write admission and final-send guards still enforce STOP. |
| Missing/invalid proof, account/session/phone/installation mismatch, malformed/stale response, failed or timed-out API-006 read | **Unchecked** neutral fallback; no error text, spinner that persists, or visible status/notice | No new `GRANT`, `REVOKE`, persistent status change or checkout inhibition is generated by the read/failure. Existing durable consent is unchanged. |
| A new GRANT request is unacknowledged, rejected or transport fails | **Unchecked** as the safe final display; no failure message | Do not treat a browser click or unresolved hosted write as verified consent. Bounded retries retain original identity, but checkout proceeds. |
| A new GRANT was ACKed, but effective current permission has not been verified | **Unchecked** until current API-006 confirmation (or equivalent authoritative confirmation accepted by this architecture) | An ACK records an event, not an unconditional assertion that current STOP-free outreach permission exists. No automatic replay of checkbox intent. |
| A deliberate checkbox-uncheck REVOKE was ACKed | **Unchecked**, without a success notice | Clear the appropriate proof association; a later GRANT requires a new explicit action, subject to STOP. |
| Active installation/site/session cannot be established | Omit or deactivate the optional Moda consent control rather than present broken merchant checkout UI | Fail closed for an untrusted checkout or installation; never prevent or delay ordinary checkout. Recovery feature/plan state is not part of this capture decision. |

- These are **checkout presentation states**, not a replacement API-006 wire schema. Use the accepted published API-006 contract and verify the current `CustomerPhone` and independent STOP decision. A matching phone number, a logged-in Woo account, or a cached Woo `checked` state is **never** evidence of a current consent grant.
- The checkbox **always stays in the consent field location when the installation/site is locally eligible**, including the proven-granted case. Do not substitute the old 'Already granted' paragraph/status-only view or hide the checkbox. There is no separate withdrawal control or confirmation popup. Do not interpret an unchecked UI fallback as a durable REVOKE.
- The initial control is **unchecked while a read is pending**. Status validation may update it to checked only while the exact shopper/shop/session/phone/proof tuple remains unchanged; stale responses are discarded. Consent-status requests and field re-renders are read-only. An acknowledged GRANT is not a reason to treat prior STOP as cleared.
- Reconcile deliberate action with checked-state truth: only the actual DOM/React user change from **verified checked** to **unchecked** may call the protected `withdraw` command; status reads, hydration and programmatic property updates are inert. Keep the native checkbox enabled and keep the customer's immediately changed selection during and after pending, failed or successful requests; the backend decision only changes after an authenticated acknowledged command. A failed/ambiguous write never fabricates a durable consent transition or displays a message. After a verified status-read failure, fall back unchecked without treating that as a user action.

**C. Classic and Blocks presentation.**

- **Classic:** retain Woo's `woocommerce_checkout_fields` integration and supported checkout hooks/nonce-bound AJAX. The one checkbox remains in its native form position. A verified returning grant makes it **checked and user-toggleable**, never a hidden field or a status-only replacement. Only a deliberate new checked action adds the `moda_interact_whatsapp_recovery_checked_action` marker; a prechecked existing-consent field, form serialisation and repeated `update_checkout` calls must not add a GRANT. The user-generated uncheck calls existing nonce-bound `wc-ajax` withdrawal; programmatic checkbox updates and ordinary form refreshes cannot invoke it.
- **Blocks:** retain the one supported native Additional Checkout Fields API checkbox and Store API cart/extensions flow, with **one WooCommerce Additional Checkout Field checkbox** registered during Woo initialization. The initial checked state is proof-backed; after customer interaction, the native input follows the local selection without blocking while the authenticated operation proceeds. Do not create another React root, duplicate field or replace it with a granted-status card. Store API status reads and hydration never submit decisions; a deliberate checked-to-unchecked event invokes the existing authenticated Store API withdrawal operation with a stable request identity.
- Both paths must survive account creation/login/logout, two tabs, billing phone/country changes, cancellation/abandonment before order, malformed/replayed actions, hosted outages, stale asynchronous replies and on-page refreshes. They must not show Moda errors or change non-consent merchant checkout behaviour.

**D. Fail silently on the merchant storefront; log safely for operators.**

- **No visible operational messages:** Do not render `config.changeFailed`, `config.waitForPhone`, a granted-status paragraph, an inline `role="alert"`, a consent-error toast/banner, Woo notice, checkout validation error, technical diagnostic code, success announcement or a persistent spinner for Moda operations. Only the approved opt-in disclosure and its native checkbox are permitted; no withdrawal popup or extra button is rendered. Diagnostics must not appear in shopper-accessible DOM/ARIA live regions.
- **No checkout dependency:** Checkout rendering, cart updates, address edits, shipping/tax calculation, payment and order placement must work if the Moda feature API, API-006, API-007, JavaScript or logging infrastructure is absent, slow, malformed or returns errors. Keep network work off the critical checkout render/submit path where feasible; enforce bounded timeouts and asynchronous optional requests. Never throw an uncaught consent exception into Woo's request lifecycle or keep a checkout control disabled forever because a consent request did not resolve.
- **Failure-to-state rules:** A failed status read leaves unchecked neutral UI but **does not write REVOKE**. A failed GRANT leaves the customer-selected checkbox checked but cannot create an authoritative permission claim. A failed/ambiguous withdrawal leaves the customer-selected checkbox unchecked but cannot fabricate a durable REVOKE, automatic re-GRANT or successful hosted response. The durable Moda record and independent STOP guard remain authoritative; do not turn failure into permissive outreach.
- **Internal diagnostics:** Use the repository's approved sanitized Woo/WordPress logging adapter in PHP in all environments when a meaningful failure happens (not only under `WP_DEBUG`). Record a bounded stable reason, operation, source and safe HTTP status/correlation; never raw exceptions containing secrets, customer PII, full checkout data, phone, consent proof, nonce, cookies or access tokens. Log at the owning boundary instead of duplicating events at each layer. Sink failure must not affect checkout. Optional browser diagnostics remain explicitly opt-in and contain fixed, non-sensitive codes only, never shopper-facing notices.

## Work Items

- [ ] Convert the current `CheckoutConsentCapture` event builder, `CheckoutConsentPublisher` validation/retry and `ModaApiClient::publishWooConsent` validation/fixtures from **v1 to v2 only**. Preserve accepted original observations and idempotency; remove obsolete v1 wire assertions and retry identities.
- [ ] Remove `CLASSIC_WITHDRAW_FIELD` / `BLOCK_WITHDRAW_FIELD` **select** UI registrations and the JS select-change handler. Reuse the existing proof-backed withdrawal command, but call it **only for a deliberate user uncheck of a verified checked checkbox**; a default/unknown unchecked checkbox, hydration or draft refresh cannot REVOKE.
- [ ] Implement a small, testable proof-association component for ACK → server-held protected session/account identity, invalidation on phone/login/logout/site/credential changes, and API-006 proof-bound lookup. Follow the API-006 owned contract; no arbitrary browser-supplied event reference can select a different customer.
- [ ] Update **both** Classic and Blocks to keep the checkbox visible, **checked and toggleable only for proof-backed current `CONFIRMED_GRANTED`**, otherwise unchecked. Remove the separate withdrawal control/dialog; remove old granted-status-only UI and disable implicit new GRANT from a prechecked field. Track in-flight responses by current shopper, phone and installation; ignore stale results.
- [ ] Update `assets/js/checkout-consent-classic.js`, `assets/js/checkout-consent-blocks-status.js`, `CheckoutConsentCheckbox.php` and `CheckoutConsentPresentation.php` so status-check, action and timeout failures have **no shopper-visible messages, alerts/live regions, or order-validation side effects**. Keep the checkbox accessible and optional. Update only narrowly needed extension registration, asset build manifest/packaging and installation lifecycle.
- [ ] Remove the `GET /v1/merchant/feature-preferences` entitlement query and `checkout_recovery.effective` / `planEligible` admission decision from `includes/Checkout/CheckoutConsentEligibility.php::eligible()` and its call in `CheckoutConsentCapture.php` on a new explicit GRANT. Retain bounded local installation/site checks and the existing authenticated API-007 v2 write's authoritative installation, recipient and evidence validation. No hosted feature-preferences request on render, hydration, GRANT, REVOKE or retry, and no direct database/Redis call from Woo.
- [ ] Preserve local connection validation in `CheckoutConsentEligibility::eligibleForPresentation()`, `CheckoutConsentCheckbox` and `CheckoutConsentPresentation`, while ensuring disabled recovery plans do not silently prevent the trusted opt-in from being displayed or recorded. Preserve server-side nonce/Cart Token, active checkout, canonical recipient, shopper identity, protected REVOKE and consent disclosure; do not make a rejected GRANT appear acknowledged.
- [ ] Test a connected installation with `checkout_recovery` enabled, disabled, plan-ineligible and feature-preferences API completely unavailable: deliberate GRANT/REVOKE still reaches authenticated API-007 without fetching feature preferences; disabled/ineligible recovery does **not** produce a recovery, outbound message or credit. Installation revoked, mismatched shop/site, missing validated contact, stale session, STOP and ambiguous recipient still fail appropriately. Assert no `capture_observe_feature_ineligible` for a valid consent write and do not weaken error logging or retries.
- [ ] Replace WP_DEBUG-only and unlogged consent/eligibility/publisher exception branches with **sanitized, internally observable** failure handling through the approved PHP/Woo logging adapter; logging must remain non-blocking and never reveal PII/credentials.
- [ ] Replace v1 tests/fixtures and extend `CheckoutConsentReturningTest.php`, `CheckoutConsentCaptureTest.php`, `CheckoutConsentCheckboxTest.php`, `CheckoutConsentPresentationTest.php`, API client tests, and Classic/Blocks JS tests with v2 snapshots and **the entire checked/unchecked and silent-failure decision table**. Cover guest/account, first/no phone, pre-submit ACK, proven returning GRANTED, current STOP, missing proof, mismatched identity, unavailable/slow API, retries, failed GRANT/REVOKE, duplicate action, phone/session change, no checkout interruption and no shopper-visible errors.
- [ ] Update Woo documentation, disclosure translations (`.po`/POT and generated catalogues as required), 20-locale verification and the Completion Report, preserving original Attempt 1 work and worktree evidence.

## Interfaces / Contracts

- **Write:** API-007 owns `woo.whatsapp-consent.v2` on `POST /v1/woocommerce/whatsapp-consent`; WOO-003 is its **only Woo producer-adoption task**. The write remains installation-authenticated. No Shared queue/event change. API-007 is currently awaiting final review in the supplied primary snapshot; WOO-003 cannot claim integrated success until API-007 is accepted and available to its tests.
- **Read:** API-006 owns the **proof-backed shopper status endpoint**, exact validated request/response contract, tenant/installation authentication, complete evidence tuple check `(shopId,eventId,canonicalPhone,customerPhoneId,phoneConsentRevision)` and current CustomerPhone/STOP read. WOO-003 owns only Woo's server-side proof binding and response consumption. API-006 is absent/unmaterialised in both supplied snapshots, so this is a **completion/review gate**, not a claim of an implemented endpoint. Never invent URL/method/wire fields in WOO-003; reconcile the final accepted API-006 contract when materialised.
- **Existing capture:** WOO-002 owns nonce, session, billing and deliberate action observation; WOO-003 refines that same mechanism rather than introducing parallel capture handlers or a second checkout consent store. `CheckoutConsentEligibility::eligible()` must no longer consume `/v1/merchant/feature-preferences` on GRANT; this endpoint remains available for normal merchant settings. `eligibleForPresentation()` remains a local installation/site presentation check, not a billing entitlement check.
- **Data:** Existing CustomerPhone and immutable WhatsAppConsentEvidence remain the durable source; Woo holds only revocable identity-bound proof pointers after an ACK. Guest proof never creates a global identity. STOP is independent and takes precedence.
- **Recovery boundary:** `checkout_recovery` feature enablement, `planEligible`, consent, recipient suppression and STOP are checked independently by the approved Background admission and final-send gates; they are not queried by Woo's consent publisher. API-007 v2 deliberately stores valid consent even when recovery is disabled.
- **Status:** The authenticated API-006 lookup must be bounded and fail closed without preventing checkout. Do not reimplement current-consent decisions from cached Woo state or assume the state from `CustomerPhone` solely because a canonical number matches.

## Dependencies

- `ARCH-046-WOOCOMMERCE-002` — original satisfied execution prerequisite for the **already claimed** WOO-003 Attempt 1.
- **Integration/review gates introduced by this amendment:** `ARCH-046-API-007` must be architect-accepted as v2-only; `ARCH-046-API-006` must be explicitly defined/materialised, implemented, tested and accepted before final proof-backed status acceptance. API-006 is not present in this snapshot; do not add a dangling YAML dependency or reset an active WOO-003 developer claim. The architect must reconcile formal dependency metadata as those external tasks become materialised, before WOO-003 is accepted Complete.
- The current WOO-003 metadata (`status: in_progress`, `attempt: 1`, `executor: developer`, `claimed_at`) is preserved; this is a scoped mid-attempt developer/architect amendment, **not** a new task, re-claim or automatic downstream promotion.

## Enables

- `ARCH-046-SYSTEM-TEST-001` — terminal integrated Classic/Blocks, guest/account, API proof and consent-write certification after both hosted dependencies are accepted.
- `ARCH-046-SYSTEM-TEST-002` — existing blocked live recovery certification; this scope does not unblock its independent Background recovery engine prerequisites.

## Acceptance Criteria

- [ ] A deliberate authenticated GRANT for a valid checkout/installation is accepted by API-007 without invoking `/v1/merchant/feature-preferences` even when `checkout_recovery.effective=false`, `planEligible=false`, the feature catalogue is unavailable or the merchant has no recovery entitlement. This records passive evidence only, not recovery eligibility. A revoked/disconnected installation and unverified customer action still fail closed.
- [ ] No consent-specific request triggers recovery, outbound WhatsApp, credit consumption, feature-entitlement SQL or any consent-driven queue work. Existing authoritative Background admission, final-send and STOP guards are unchanged and tested independently.

- [ ] Only the v2 six-field body is sent by Woo, with successful GRANT/REVOKE and idempotent retries against architect-accepted API-007; no v1 fallback exists.
- [ ] Woo verifies the *real* checkout action, nonce/cart token, current canonical phone, session/account and installation in both flows before publishing. No status read, page load, phone-only lookup or initially/programmatically unchecked checkbox emits consent; only deliberate checkbox changes are valid requests.
- [ ] In **Classic and Blocks**, the **same visible checkbox initialises checked** for a shopper with **current, proof-backed API-006 `CONFIRMED_GRANTED`** (no STOP), then follows the latest deliberate customer selection without waiting for the backend; no second button, modal or confirmation control exists. No granted-status-only replacement, hidden checkbox or implicit duplicate GRANT is allowed.
- [ ] In **Classic and Blocks**, initial no proof, no consent, `UNVERIFIED`/revoked/unknown consent, invalid or changed identity, STOP/no-contact or API outage produces an **unchecked initial** fallback before a deliberate user action (non-actionable where STOP/eligibility requires); no status read, page refresh or fallback emits GRANT/REVOKE or changes existing durable consent.
- [ ] Current STOP is independent of `GRANTED`, never cleared, and is not presented as messaging permission; a valid user withdrawal/regrant cannot create recovery work or messages.
- [ ] Phone, login/logout, session/cart token, installation/credential change and in-flight reply races invalidate proof and pending actions across Classic and Blocks; guest proof never crosses account/session boundaries.
- [ ] A deliberate shopper-generated uncheck invokes the protected, proof-checked `REVOKE` operation without a popup; no programmatic or default uncheck does so. Checkbox becomes unchecked immediately and stays unchecked even if the write fails. A failed REVOKE leaves prior server consent unchanged (unless the transport outcome was ambiguous, in which case verify before asserting status); retries remain idempotent. No customer-facing error/success message is rendered.
- [ ] No Moda status, warning, toast, alert, notice, technical diagnostic, error, success or indefinite loading text is visible or screen-reader-announced on merchant storefront failure paths; only the approved disclosure and checkbox remain. All 20 locales and accessible checked/disabled/keyboard semantics are verified.
- [ ] Simulated hosted feature-preferences, API-006, API-007, JavaScript and diagnostic-sink failures/timeouts do not delay or block checkout page rendering, address/cart changes, shipping, payment, order submission or order creation; no consent failure becomes a Woo checkout-validation error.
- [ ] Consent status/read and publisher failures produce bounded, non-sensitive **internal** error logs under normal production logging settings, not only `WP_DEBUG`, without leaking phone, token, proof, cookie, nonce or checkout HTML; logger failure does not affect checkout. No unlogged swallowed exception remains in the WOO-003-owned paths.
- [ ] Focused tests prove no consent-triggered checkout recovery, wakeup, credits, Meta send or cross-shop lookup; dedicated LocalWP/system-test validation remains a terminal independent gate.
- [ ] The Completion Report records exactly what code was changed, the prepared worktrees, validation results and any blocked external API-006 capability; do not mark WOO-003 Ready for Review or Complete while its proof-status integration remains unverified.

## Validation

- [ ] Focused PHP tests for `CheckoutConsentEligibility`/`CheckoutConsentCapture` and Classic/Blocks integration tests prove zero `GET /v1/merchant/feature-preferences` calls for initial render, explicit GRANT/REVOKE, status hydration or retry; use failing remote-feature fixtures as well as disabled and plan-ineligible feature responses. Keep invalid/revoked installation, untrusted session and stale proof regression coverage. Test against the accepted v2 writer, not a mocked feature gate.

- [ ] `composer lint` and focused PHPUnit tests: `vendor/bin/phpunit tests/CheckoutConsentCaptureTest.php tests/CheckoutConsentReturningTest.php tests/CheckoutConsentCheckboxTest.php` (or equivalent declared test runner when the PHPUnit CLI does not accept multiple positional paths).
- [ ] `npm run i18n:verify:20`, `npm run test:i18n`, `npm run lint:js`, `npm run build` and focused Blocks/Classic JS tests actually declared in this Woo repository.
- [ ] Verify golden outgoing payloads/ACK for GRANT, REVOKE, duplicate, terminal conflict, retry and phone/session/installation changes using the *actual* API-007 v2 contract. Run a proof-status integration test against the real architect-accepted API-006 contract before marking the task complete; isolated mocks alone cannot certify the absent hosted endpoint.
- [ ] PHPUnit and JavaScript tests assert that initial checked state requires proof-backed `CONFIRMED_GRANTED`; deliberate GRANT keeps the UI checked even when write fails while durable permission remains unchanged, and deliberate REVOKE keeps the UI unchecked even when write fails while the stored grant remains. The input stays enabled during remote requests, rapid toggles are ordered without lost choices, and no checkout-related GRANT occurs from a prechecked verified field. An explicit verified user uncheck emits a single protected `REVOKE` and does not require a second confirmation dialog. Assert no error/status/notice DOM or ARIA alert is produced when any request rejects, times out or has malformed response; checkout remains submit-safe.
- [ ] Real disposable WordPress Classic/Blocks HTTP integration: live status/GRANT/REVOKE via the actual checkout transport and controlled hosted fixture; verify consumer-visible HTML remains safe when the hosted fixture is unavailable or slow, without consent-caused checkout activity. Keep a separate opt-in Chromium hydration test for checked/unchecked state, no visible errors, and successful normal checkout; fixture-based success must not be represented as real API-006 integration.
- [ ] LocalWP Classic and Blocks smoke checks for rendering/phone-before-or-after-opt-in/guest/registered/proven returning/withdrawal/STOP/outage; system-test ownership remains separate for full certification.
- [ ] `git diff --check`, strict task-scope diff review; no edits to `docs/decisions/**/_index.md` or to another owning repository.

## Stop Condition

When all Work Items, Acceptance Criteria and required Validation can be honestly checked, preserve the developer-owned Attempt 1 claim, record physical dedicated worktree and start-of-attempt synchronization evidence and current integration prerequisites in the Completion Report; return the task through its authorised developer self-review path and STOP. Do not begin API-006, a nonexistent WOO-008, or enabled system-test tasks. If API-006 is not yet available, complete independently testable parts but **report the external dependency instead of claiming the full feature works**.

## Implementation Notes

**2026-11-01 execution map (source-observed, not implementation):** Current `includes/Checkout/CheckoutConsentEligibility.php::eligible()` performs `ModaApiClient::merchantKnowledgeExchange($record, '/v1/merchant/feature-preferences', 'GET', null, 2)` and checks `checkout_recovery.effective` / `planEligible`; `CheckoutConsentCapture.php` uses that result to reject GRANT as `capture_observe_feature_ineligible`. Remove only this redundant capture-side feature gate. Keep local `eligibleForPresentation()` and caller authentication/session validation. Update the existing eligibility/capture tests and `docs/arch046-woo-consent-integration.md` to reflect passive evidence and explain that Background—not the consent UI—owns recovery entitlement. Do not add a second API endpoint, caching, a local eligibility feature catalogue, a new task, or phone-change consent-transfer shortcuts.

**Inspected snapshot (10), 2026-10-31 (source-review findings, not acceptance):** `assets/js/checkout-consent-classic.js::setView()` unconditionally unchecks and hides the checkbox on `granted`, then substitutes the status paragraph/button; it also renders `config.changeFailed` after failed withdrawal. `assets/js/checkout-consent-blocks-status.js::ConsentControl()` renders a granted-status paragraph/button *instead of* the checkbox; its controlled checkbox is checked only for `waitingPhone`, not existing GRANTED, and it renders `config.changeFailed` and `config.waitForPhone`. `includes/Checkout/CheckoutConsentCheckbox.php::classicFields()` defaults to unchecked and supplies a hidden error region in the withdrawal container. `CheckoutConsentStatusReader.php::logFailure()` only logs with `WP_DEBUG`; `CheckoutConsentEligibility.php` and `CheckoutConsentPublisher.php` contain caught exceptions without safe operational diagnostics. `CheckoutConsentEligibility::eligible()` makes a synchronous merchant-feature read during page-render eligibility and `ModaApiClient` uses a five-second default timeout; this needs explicit non-disruption validation. Existing nonce/session/proof checks must be **preserved**; replace the old separate withdrawal button with an explicitly user-generated, proof-guarded uncheck that invokes that same secure operation. Never convert programmatic unchecked/default states to REVOKE. Modify these existing components and tests rather than creating another consent flow.

**Task-definition review boundary:** The snapshot includes a Woo client for `POST /v1/woocommerce/whatsapp-consent/status` with `woo.whatsapp-consent-status.v1`, but its existence in the Woo repository does **not** verify the deployed hosted API-006 contract. Reconcile against the architect-accepted API and prove authenticated end-to-end behaviour before completing this task.

Do not blindly implement an API-006 lookup from an invented endpoint/response schema. The API must also decide how the stored evidence reference and *current* CustomerPhone/STOP authority are authenticated, before Woo attaches its UI. Prefer existing WordPress account metadata and Woo session facilities over new identity tables. Store no installation bearer in a browser, output, session payload or log. Consider idempotent local proof invalidation after server ACKs and privacy-export/erasure implications of WordPress account metadata within the existing approved platform privacy scope.

**Blocks support:** The existing registered Checkout Fields inner block owns exactly one checkbox, using Woo's cart/extensions API for authenticated status, GRANT and deliberate user-uncheck REVOKE. Do not duplicate with a second custom renderer or React root. Classic uses the native checkout field and session-bound `wc-ajax` for status and explicit uncheck REVOKE. Test browser hydration and shopper event handling with the installed Woo version.

**Ownership/rollout:** No existing production users. The agreed breaking rollout allows dropping v1; coordinate API-007 deployment/availability and new Woo v2 producer, then API-006 proof read. Do not reintroduce deprecated version adapters or an untested read cache. `moda_architect` owns architecture-wide reconciliation and dependency promotion, and domain `_index.md` remains untouched until the architect session is explicitly closed. This task amendment documents the decided behaviour; accompanying Woo implementation changes are delivered separately and require developer-side application, testing, review and commit.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-23T13:39:33Z. Attempt 0 review history is preserved below.

### Files Changed

None — no runtime implementation in this documentation patch.

### Work Completed

None.

### Validation Results

Not run by a repository agent; no developer worktree/remote access is available from this snapshot.

### Deviations

None.

### Assumptions

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Consent has no Moda-imposed waiting/expiry period. Recheck the current customer-phone permission and independently applicable checkout validity; do not invent a retention deadline.

### Unresolved Issues

None recorded at definition time; raise actual missing cross-repository contract/rollout dependencies to moda_architect before scope drift.

### Architectural Concerns

None recorded beyond explicit context and gates.

## Architect Review

### Review Status

Pending — no implementation reviewed or accepted.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
