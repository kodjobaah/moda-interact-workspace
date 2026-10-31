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
updated: 2026-10-31
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

Complete the **existing** `ARCH-046-WOOCOMMERCE-003` implementation, rather than opening `WOOCOMMERCE-008`, by (a) retaining safe later GRANT/REVOKE capture, (b) upgrading the Woo consent publisher to the **breaking v2-only** hosted write contract, and (c) rendering **one consistent, always-visible consent checkbox** in **Classic and Blocks** checkout: **checked only for currently verified effective GRANTED consent**, otherwise **unchecked**. Retain a distinct, confirmed withdrawal action. Moda failures must be invisible to shoppers and must never impede the merchant checkout; internal failures must still be logged safely. No guest/customer may be identified by a phone match alone.

## Context

The developer's dedicated WOO-003 worktree already edits `includes/Checkout/CheckoutConsentCheckbox.php`, `CheckoutConsentCapture.php`, `CheckoutConsentPublisher.php`, `assets/js/checkout-consent-classic.js`, `tests/CheckoutConsentReturningTest.php` and the returning-consent documentation. Its `select` field for earlier permission is an intermediate implementation, not the desired final UI. Creating an additional Woo-owned WOO-008 task would produce overlapping edits and merge conflicts. This scope amendment extends **the already claimed Attempt 1** and does not reset or supersede prior work.

API-007 changes `POST /v1/woocommerce/whatsapp-consent` to `woo.whatsapp-consent.v2` **only** (no production v1 compatibility); its approval/deployment is still an external gate. API-006, the authenticated **proof-backed shopper status read**, is **absent from both supplied 2026-10-24 workspace snapshots** and remains an independently owned API task to define, accept and deploy. Do not invent its endpoint or response payload locally. WOO-003 cannot claim the returning-status read works end to end until the API-006 contract and hosted implementation exist. No `ARCH-046-WOOCOMMERCE-008` task is required.

**Architect clarification — 2026-10-31 (snapshot 10):** The developer has now explicitly selected a checked/unchecked consent checkbox instead of the earlier granted-status-only display. This clarification **supersedes** every earlier instruction in this task to hide the checkbox, replace it with an "already granted" message, or expose a customer-facing consent error/pending/status notice. The consent disclosure, the optional withdrawal control and its deliberate confirmation are permitted UI; operational failures are not. Preserve the existing `in_progress` developer claim, Attempt 1, repository ownership, and API-006/API-007 acceptance gates. This is an amendment of the existing task, not a new execution claim.

## Scope

1. **V2-only producer within WOO-003.** Change the existing server-side event builder, publisher, HTTP client/validator as needed, API contract fixtures, retry assertions, and associated tests to send exactly the six documented v2 top-level fields; remove the old v1 outgoing payload and v1-only tests/examples. No feature-compatibility adapter is required because there are no production users or queued legacy consent events to preserve. Keep the live checkout session/nonce/Cart Token/customer-action validation *inside Woo* instead of serialising checkbox attestation flags to Moda.
2. **Current-consent display within WOO-003.** A read-only, installation-authenticated, server-to-server lookup to the API-006 proof-status operation, *only once an eligible shopper/phone is established and a valid server-held proof is available*. Never permit an anonymous lookup by phone alone, never expose installation bearer credentials or protected proof to checkout JavaScript, and never use a local cached consent value as the definitive current provider state.
3. **Single, truthfully checked checkout consent checkbox.** Remove the Classic and Blocks withdrawal **select/dropdown**, but **never replace/hide the checkbox merely because the customer has consented**. Once proof-backed API-006 confirms effective `GRANTED` without STOP/no-contact for this installation, shopper and canonical phone, render the checkbox **checked** and **non-editable**; keep the separate **Withdraw WhatsApp permission** action for deliberate revocation. For `UNVERIFIED`, revoked, unknown, missing/invalid proof, mismatched shopper, unavailable API or other unverifiable status, render the same checkbox **unchecked** (optionally actionable only when the ordinary feature/checkout eligibility rules permit a new explicit GRANT). Never infer GRANTED from a local flag, phone match, account sign-in, stale HTTP response or unverified write. A verifiable STOP/no-contact state must not be portrayed as active consent or overridden by Woo UI.
4. **Explicit withdrawal.** A withdrawal must require a separate, deliberate customer action, server-validated against the current account or guest checkout session and canonical phone, with confirmation and a new `REVOKE` v2 event. The **checked checkbox must not be freely toggleable**: allowing uncheck without a REVOKE would lie about durable consent, while translating uncheck into automatic REVOKE would violate the existing deliberate-action contract. Unchecking, hydration, field refresh and a mere phone change must never emit REVOKE. Do not show a success notice; change a confirmed checked view to unchecked only after a hosted ACK or fresh authoritative status. A failed/ambiguous withdrawal must never persist a fictitious REVOKE or assert success; if current state cannot be proven, fall back to neutral unchecked while checkout continues. Preserve bounded same-event retry and permit a later explicit new GRANT subject to STOP.
5. **Proof binding.** After a successful *acknowledged* grant, retain only the minimum necessary server-side event association (immutable grant `eventId`, applicable installation/shop identity, associated canonical-phone binding or keyed digest, revision and current Woo shopper/session binding) needed by API-006. For a signed-in shopper, bind to the authenticated WordPress account using existing supported storage, without inventing a new Moda identity table; for a guest, bind to their verified Woo session/cart identity and do not persist a cross-session guest identity. A grant from a guest must not silently become another account's proof on login/account creation. Never treat an arbitrary `eventId` pasted into a request as sufficient identity proof; API-006 owns the definitive immutable-evidence/current-STOP proof verification. For REVOKE or change of account/phone/installation, invalidate the affected association and pending lookup immediately.
6. **Minimal read load and checkout availability.** Request status only for a stable, verified shop + shopper/session + canonical-phone + proof tuple. Reuse an already validated result within that unchanged checkout context, with bounded short caching only where explicitly safe. Do not call the hosted API on every character typed, every Woo `update_checkout`, every Blocks draft refresh, or when the shopper lacks a trusted proof. Suppress stale responses after identity/phone/session changes. Moda feature eligibility, proof status and consent-write operations are **optional to checkout**: avoid synchronous hosted network requests on the checkout page's critical rendering path; use bounded, non-blocking presentation checks and fail closed if prerequisites cannot be established. A failed or slow Moda request must not delay, break or alter WooCommerce cart, checkout, payment, order submission, or unrelated merchant interactions.
7. **No recovery side effects.** Preserve the existing rule that consent write or status read does not create/revisit old CheckoutRecovery rows, publish a recovery wakeup, send WhatsApp messages, consume credits, or clear authoritative WhatsApp STOP. Background owns recovery eligibility and final-send guards.
8. **Twenty locales and accessibility.** Use the configured WooCommerce site/store language for the approved consent disclosure, checkbox label, separate withdrawal action and customer-initiated confirmation. Maintain all 20 supported catalogues, label association, native checked semantics, keyboard/screen-reader handling and accessible focus behaviour. **Do not render Moda operational status, loading, error or success messages** on the merchant storefront, including screen-reader-only alerts/live regions for failures.

9. **Silent to shoppers, observable to operators.** No Moda status-read, feature-read, GRANT, REVOKE, retry, timeout or unexpected exception may inject checkout notices, banners, toast notifications, inline errors, blocking browser alerts, technical reason strings or checkout-validation errors. Do not emit `consent_status_remote_unavailable` or similar codes into visible merchant checkout UI. Keep necessary diagnostics **server-side** via the repository-approved Woo/WordPress structured logger (the Node shared logger is not a PHP runtime import); log bounded non-sensitive event type, code, correlation and HTTP status. Do not log checkout HTML, phone, proof, raw provider payload, nonce, cookie or credentials. Do not swallow exceptions without an appropriate internal diagnostic; failure of the logging sink must itself be isolated from checkout. The customer-initiated **withdrawal confirmation** is not an error notice and remains allowed.

## Out of Scope

- Do **not** create `ARCH-046-WOOCOMMERCE-008`, a separate Woo implementation branch, new checkout customer tables, an unauthenticated phone-number preference API, a My Account consent page, a persistent guest cross-session identity, or Shopify consent changes.
- Do not implement or alter hosted API-006/API-007 code, database schema, Meta STOP processing, Background recovery workers, recovery scheduling or merchant suppression. WOO-003 consumes those separately owned contracts; missing cross-boundary capabilities go back to `moda_architect`.
- No compatibility shim, legacy v1 sender, migration/backfill of old v1 events, new Woo-to-PostgreSQL/Redis connection, or unapproved direct browser-to-Moda call.
- Do not rewrite all checkout UI or introduce unsupported WooCommerce DOM scraping just to display a button. Prefer documented checkout extension points; if the required Blocks extension capability is absent in the supported runtime, return the specific gap to the architect.
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
- Do **not** send `purpose`, `checkoutAction`, `checkoutKey`, `checkoutMode`, `selection`, `source`, `fieldId`, `nonceVerified`, `sessionVerified`, `userInitiated`, `serverObservedPhone`, `verifiedCountryCode`, `shopId`, `customerId` or `merchantSiteUrl` in v2. Preserve the *actual* Woo nonce/Cart Token, active checkout, installation/site identity, eligibility and choice-change checks as local PHP behaviour.
- The API ACK is `{schemaVersion:"woo.whatsapp-consent.v2", status:"recorded"|"duplicate", decision, consentRevision, decisionSequence}` with decimal-string revision/sequence. Validate its shape/version and matching decision; an HTTP 200 with an invalid/mismatched body must **not** be treated as durable consent. Stop retry on terminal 4xx conflicts; do not replay stale GRANT after a later REVOKE, STOP, logout, phone change or installation credential rotation. PHP backoff remains bounded and does not extend the server's grant freshness contract.

**B. Verified consent checkbox — authoritative current-state decision table.**

| API-006 / checkout fact for the current authenticated installation + shopper/session + canonical phone | Checkbox presentation | Allowed operation / fallback |
|---|---|---|
| `CONFIRMED_GRANTED` with verified current consent and no authoritative STOP/no-contact | **Checked**, visible, non-editable (read-only semantics/disabled control); separate explicit withdrawal action | Read never writes; only a separately confirmed withdrawal may publish `REVOKE`. Never submit another `GRANT` because the checked control is included in a checkout form. |
| `UNVERIFIED`, `REVOKED`, `UNKNOWN`, no prior proof or no existing consent | **Unchecked**, visible when consent feature is eligible | A new **deliberate** checked choice may publish `GRANT`. Page load and form refresh cannot grant/revoke. |
| Verified STOP/no-contact that can be independently established | **Unchecked**; no active-permission claim, and no actionable control capable of clearing STOP | STOP remains authoritative. Where API-006 intentionally returns opaque `UNVERIFIED`, do not infer the reason; all hosted write admission and final-send guards still enforce STOP. |
| Missing/invalid proof, account/session/phone/installation mismatch, malformed/stale response, failed or timed-out API-006 read | **Unchecked** neutral fallback; no error text, spinner that persists, or visible status/notice | No new `GRANT`, `REVOKE`, persistent status change or checkout inhibition is generated by the read/failure. Existing durable consent is unchanged. |
| A new GRANT request is unacknowledged, rejected or transport fails | **Unchecked** as the safe final display; no failure message | Do not treat a browser click or unresolved hosted write as verified consent. Bounded retries retain original identity, but checkout proceeds. |
| A new GRANT was ACKed, but effective current permission has not been verified | **Unchecked** until current API-006 confirmation (or equivalent authoritative confirmation accepted by this architecture) | An ACK records an event, not an unconditional assertion that current STOP-free outreach permission exists. No automatic replay of checkbox intent. |
| A separately confirmed REVOKE was ACKed | **Unchecked**, without a success notice | Clear the appropriate proof association; a later GRANT requires a new explicit action, subject to STOP. |
| Feature/installation eligibility itself cannot be established | Omit or deactivate the optional Moda consent control rather than present broken merchant checkout UI | Fail closed for new GRANT; never prevent or delay ordinary checkout. |

- These are **checkout presentation states**, not a replacement API-006 wire schema. Use the accepted published API-006 contract and verify the current `CustomerPhone` and independent STOP decision. A matching phone number, a logged-in Woo account, or a cached Woo `checked` state is **never** evidence of a current consent grant.
- The checkbox **always stays in the consent field location when the feature is eligible**, including the proven-granted case. Do not substitute the old 'Already granted' paragraph/status-only view or hide the checkbox. The separate withdrawal control may appear alongside the checked non-editable field. Do not interpret an unchecked UI fallback as a durable REVOKE.
- The initial control is **unchecked while a read is pending**. Status validation may update it to checked only while the exact shopper/shop/session/phone/proof tuple remains unchanged; stale responses are discarded. Consent-status requests and field re-renders are read-only. An acknowledged GRANT is not a reason to treat prior STOP as cleared.
- Reconcile deliberate action with checked-state truth: a verified-granted checkbox is non-editable and a **separate** withdrawal action is required. Once withdrawn with ACK, show unchecked. A failed/ambiguous withdrawal never claims success, never clears durable consent locally, and leaves either the last still-verified state or neutral unchecked pending fresh verification.

**C. Classic and Blocks presentation.**

- **Classic:** retain Woo's `woocommerce_checkout_fields` integration and supported checkout hooks/nonce-bound AJAX. The one checkbox remains in its native form position. A verified returning grant makes it **checked** and **non-editable**, never a hidden field or a status-only replacement. Only a deliberate new checked action adds the `moda_interact_whatsapp_recovery_checked_action` marker; a prechecked existing-consent field, form serialisation and repeated `update_checkout` calls must not add a GRANT. The separate withdrawal button and explicit confirmation remain distinct.
- **Blocks:** retain the one supported Woo Checkout Fields inner block and Store API cart/extensions flow, with **one native-looking controlled checkbox** checked only after authoritative verification and non-editable while verified GRANTED. Do not create a second React root, duplicate Additional Checkout Field, or replace the checkbox with a granted-status card. Store API status reads and hydration never submit decisions; a confirmed separate withdrawal triggers a distinct authenticated operation.
- Both paths must survive account creation/login/logout, two tabs, billing phone/country changes, cancellation/abandonment before order, malformed/replayed actions, hosted outages, stale asynchronous replies and on-page refreshes. They must not show Moda errors or change non-consent merchant checkout behaviour.

**D. Fail silently on the merchant storefront; log safely for operators.**

- **No visible operational messages:** Do not render `config.changeFailed`, `config.waitForPhone`, a granted-status paragraph, an inline `role="alert"`, a consent-error toast/banner, Woo notice, checkout validation error, technical diagnostic code, success announcement or a persistent spinner for Moda operations. The approved opt-in disclosure/checkbox label, explicit withdrawal control and customer-initiated confirmation are permitted. Diagnostics must not appear in shopper-accessible DOM/ARIA live regions.
- **No checkout dependency:** Checkout rendering, cart updates, address edits, shipping/tax calculation, payment and order placement must work if the Moda feature API, API-006, API-007, JavaScript or logging infrastructure is absent, slow, malformed or returns errors. Keep network work off the critical checkout render/submit path where feasible; enforce bounded timeouts and asynchronous optional requests. Never throw an uncaught consent exception into Woo's request lifecycle or keep a checkout control disabled forever because a consent request did not resolve.
- **Failure-to-state rules:** A failed status read leaves unchecked neutral UI but **does not write REVOKE**. A failed GRANT cannot produce an affirmative checked permission claim. A failed/ambiguous withdrawal cannot produce a local REVOKE, automatic re-GRANT, or a fabricated success. The durable Moda record and independent STOP guard remain authoritative; do not turn failure into permissive outreach.
- **Internal diagnostics:** Use the repository's approved sanitized Woo/WordPress logging adapter in PHP in all environments when a meaningful failure happens (not only under `WP_DEBUG`). Record a bounded stable reason, operation, source and safe HTTP status/correlation; never raw exceptions containing secrets, customer PII, full checkout data, phone, consent proof, nonce, cookies or access tokens. Log at the owning boundary instead of duplicating events at each layer. Sink failure must not affect checkout. Optional browser diagnostics remain explicitly opt-in and contain fixed, non-sensitive codes only, never shopper-facing notices.

## Work Items

- [ ] Convert the current `CheckoutConsentCapture` event builder, `CheckoutConsentPublisher` validation/retry and `ModaApiClient::publishWooConsent` validation/fixtures from **v1 to v2 only**. Preserve accepted original observations and idempotency; remove obsolete v1 wire assertions and retry identities.
- [ ] Remove `CLASSIC_WITHDRAW_FIELD` / `BLOCK_WITHDRAW_FIELD` **select** UI registrations and the JS select-change handler. Implement an explicit authenticated withdrawal command reusing the existing server-side publish pipeline; never emit REVOKE from an unchecked checkbox or draft hydration.
- [ ] Implement a small, testable proof-association component for ACK → server-held protected session/account identity, invalidation on phone/login/logout/site/credential changes, and API-006 proof-bound lookup. Follow the API-006 owned contract; no arbitrary browser-supplied event reference can select a different customer.
- [ ] Update **both** Classic and Blocks to keep the checkbox visible, **checked and non-editable only for proof-backed current `CONFIRMED_GRANTED`**, otherwise unchecked. Preserve the separate confirmed withdrawal control; remove old granted-status-only UI and disable implicit new GRANT from a prechecked field. Track in-flight responses by current shopper, phone and installation; ignore stale results.
- [ ] Update `assets/js/checkout-consent-classic.js`, `assets/js/checkout-consent-blocks-status.js`, `CheckoutConsentCheckbox.php` and `CheckoutConsentPresentation.php` so status-check, action and timeout failures have **no shopper-visible messages, alerts/live regions, or order-validation side effects**. Keep the checkbox accessible and optional. Update only narrowly needed extension registration, asset build manifest/packaging and installation lifecycle.
- [ ] Remove slow synchronous hosted feature-status calls from the **critical** checkout page render path (or otherwise prove strict non-disruption under provider timeout), while retaining fresh server-side eligibility verification on actual GRANT/REVOKE and fail-closed behaviour when the optional feature cannot be established.
- [ ] Replace WP_DEBUG-only and unlogged consent/eligibility/publisher exception branches with **sanitized, internally observable** failure handling through the approved PHP/Woo logging adapter; logging must remain non-blocking and never reveal PII/credentials.
- [ ] Replace v1 tests/fixtures and extend `CheckoutConsentReturningTest.php`, `CheckoutConsentCaptureTest.php`, `CheckoutConsentCheckboxTest.php`, `CheckoutConsentPresentationTest.php`, API client tests, and Classic/Blocks JS tests with v2 snapshots and **the entire checked/unchecked and silent-failure decision table**. Cover guest/account, first/no phone, pre-submit ACK, proven returning GRANTED, current STOP, missing proof, mismatched identity, unavailable/slow API, retries, failed GRANT/REVOKE, duplicate action, phone/session change, no checkout interruption and no shopper-visible errors.
- [ ] Update Woo documentation, disclosure translations (`.po`/POT and generated catalogues as required), 20-locale verification and the Completion Report, preserving original Attempt 1 work and worktree evidence.

## Interfaces / Contracts

- **Write:** API-007 owns `woo.whatsapp-consent.v2` on `POST /v1/woocommerce/whatsapp-consent`; WOO-003 is its **only Woo producer-adoption task**. The write remains installation-authenticated. No Shared queue/event change. API-007 is currently awaiting final review in the supplied primary snapshot; WOO-003 cannot claim integrated success until API-007 is accepted and available to its tests.
- **Read:** API-006 owns the **proof-backed shopper status endpoint**, exact validated request/response contract, tenant/installation authentication, complete evidence tuple check `(shopId,eventId,canonicalPhone,customerPhoneId,phoneConsentRevision)` and current CustomerPhone/STOP read. WOO-003 owns only Woo's server-side proof binding and response consumption. API-006 is absent/unmaterialised in both supplied snapshots, so this is a **completion/review gate**, not a claim of an implemented endpoint. Never invent URL/method/wire fields in WOO-003; reconcile the final accepted API-006 contract when materialised.
- **Existing capture:** WOO-002 owns nonce, session, billing and deliberate action observation; WOO-003 refines that same mechanism rather than introducing parallel capture handlers or a second checkout consent store.
- **Data:** Existing CustomerPhone and immutable WhatsAppConsentEvidence remain the durable source; Woo holds only revocable identity-bound proof pointers after an ACK. Guest proof never creates a global identity. STOP is independent and takes precedence.
- **Status:** The authenticated API-006 lookup must be bounded and fail closed without preventing checkout. Do not reimplement current-consent decisions from cached Woo state or assume the state from `CustomerPhone` solely because a canonical number matches.

## Dependencies

- `ARCH-046-WOOCOMMERCE-002` — original satisfied execution prerequisite for the **already claimed** WOO-003 Attempt 1.
- **Integration/review gates introduced by this amendment:** `ARCH-046-API-007` must be architect-accepted as v2-only; `ARCH-046-API-006` must be explicitly defined/materialised, implemented, tested and accepted before final proof-backed status acceptance. API-006 is not present in this snapshot; do not add a dangling YAML dependency or reset an active WOO-003 developer claim. The architect must reconcile formal dependency metadata as those external tasks become materialised, before WOO-003 is accepted Complete.
- The current WOO-003 metadata (`status: in_progress`, `attempt: 1`, `executor: developer`, `claimed_at`) is preserved; this is a scoped mid-attempt developer/architect amendment, **not** a new task, re-claim or automatic downstream promotion.

## Enables

- `ARCH-046-SYSTEM-TEST-001` — terminal integrated Classic/Blocks, guest/account, API proof and consent-write certification after both hosted dependencies are accepted.
- `ARCH-046-SYSTEM-TEST-002` — existing blocked live recovery certification; this scope does not unblock its independent Background recovery engine prerequisites.

## Acceptance Criteria

- [ ] Only the v2 six-field body is sent by Woo, with successful GRANT/REVOKE and idempotent retries against architect-accepted API-007; no v1 fallback exists.
- [ ] Woo verifies the *real* checkout action, nonce/cart token, current canonical phone, session/account and installation in both flows before publishing. No status read, page load, phone-only lookup or unchecked checkbox emits consent.
- [ ] In **Classic and Blocks**, the **same visible checkbox is checked** and non-editable for a shopper with **current, proof-backed API-006 `CONFIRMED_GRANTED`** (no STOP); the distinct withdrawal action remains available. No granted-status-only replacement, hidden checkbox or implicit duplicate GRANT is allowed.
- [ ] In **Classic and Blocks**, no proof, no consent, `UNVERIFIED`/revoked/unknown consent, invalid or changed identity, STOP/no-contact, stale status reply or API outage produces an **unchecked** fallback (non-actionable where STOP/eligibility requires); no status read, page refresh or fallback emits GRANT/REVOKE or changes existing durable consent.
- [ ] Current STOP is independent of `GRANTED`, never cleared, and is not presented as messaging permission; a valid user withdrawal/regrant cannot create recovery work or messages.
- [ ] Phone, login/logout, session/cart token, installation/credential change and in-flight reply races invalidate proof and pending actions across Classic and Blocks; guest proof never crosses account/session boundaries.
- [ ] Explicit withdrawal (not unchecking the displayed checkbox) publishes one new `REVOKE` only after confirmation; duplicate clicks/retries preserve one event identity. After a valid ACK the checkbox becomes unchecked; failed/ambiguous writes never assert success or fabricate a REVOKE. No customer-facing failure/success message is rendered.
- [ ] No Moda status, warning, toast, alert, notice, technical diagnostic, error, success or indefinite loading text is visible or screen-reader-announced on merchant storefront failure paths; only the approved disclosure, checkbox, withdrawal control and explicit customer confirmation remain. All 20 locales and accessible checked/disabled/keyboard semantics are verified.
- [ ] Simulated hosted feature-preferences, API-006, API-007, JavaScript and diagnostic-sink failures/timeouts do not delay or block checkout page rendering, address/cart changes, shipping, payment, order submission or order creation; no consent failure becomes a Woo checkout-validation error.
- [ ] Consent status/read and publisher failures produce bounded, non-sensitive **internal** error logs under normal production logging settings, not only `WP_DEBUG`, without leaking phone, token, proof, cookie, nonce or checkout HTML; logger failure does not affect checkout. No unlogged swallowed exception remains in the WOO-003-owned paths.
- [ ] Focused tests prove no consent-triggered checkout recovery, wakeup, credits, Meta send or cross-shop lookup; dedicated LocalWP/system-test validation remains a terminal independent gate.
- [ ] The Completion Report records exactly what code was changed, the prepared worktrees, validation results and any blocked external API-006 capability; do not mark WOO-003 Ready for Review or Complete while its proof-status integration remains unverified.

## Validation

- [ ] `composer lint` and focused PHPUnit tests: `vendor/bin/phpunit tests/CheckoutConsentCaptureTest.php tests/CheckoutConsentReturningTest.php tests/CheckoutConsentCheckboxTest.php` (or equivalent declared test runner when the PHPUnit CLI does not accept multiple positional paths).
- [ ] `npm run i18n:verify:20`, `npm run test:i18n`, `npm run lint:js`, `npm run build` and focused Blocks/Classic JS tests actually declared in this Woo repository.
- [ ] Verify golden outgoing payloads/ACK for GRANT, REVOKE, duplicate, terminal conflict, retry and phone/session/installation changes using the *actual* API-007 v2 contract. Run a proof-status integration test against the real architect-accepted API-006 contract before marking the task complete; isolated mocks alone cannot certify the absent hosted endpoint.
- [ ] PHPUnit and JavaScript tests assert `checked=true` only for `CONFIRMED_GRANTED` with valid proof, `checked=false` for every unverified/failure case, `checked=false` after acknowledged REVOKE, and no checkout-related GRANT from a prechecked verified field. Assert no error/status/notice DOM or ARIA alert is produced when any request rejects, times out or has malformed response; checkout remains submit-safe.
- [ ] Real disposable WordPress Classic/Blocks HTTP integration: live status/GRANT/REVOKE via the actual checkout transport and controlled hosted fixture; verify consumer-visible HTML remains safe when the hosted fixture is unavailable or slow, without consent-caused checkout activity. Keep a separate opt-in Chromium hydration test for checked/unchecked state, no visible errors, and successful normal checkout; fixture-based success must not be represented as real API-006 integration.
- [ ] LocalWP Classic and Blocks smoke checks for rendering/phone-before-or-after-opt-in/guest/registered/proven returning/withdrawal/STOP/outage; system-test ownership remains separate for full certification.
- [ ] `git diff --check`, strict task-scope diff review; no edits to `docs/decisions/**/_index.md` or to another owning repository.

## Stop Condition

When all Work Items, Acceptance Criteria and required Validation can be honestly checked, preserve the developer-owned Attempt 1 claim, record physical dedicated worktree and start-of-attempt synchronization evidence and current integration prerequisites in the Completion Report; return the task through its authorised developer self-review path and STOP. Do not begin API-006, a nonexistent WOO-008, or enabled system-test tasks. If API-006 is not yet available, complete independently testable parts but **report the external dependency instead of claiming the full feature works**.

## Implementation Notes

**Inspected snapshot (10), 2026-10-31 (source-review findings, not acceptance):** `assets/js/checkout-consent-classic.js::setView()` unconditionally unchecks and hides the checkbox on `granted`, then substitutes the status paragraph/button; it also renders `config.changeFailed` after failed withdrawal. `assets/js/checkout-consent-blocks-status.js::ConsentControl()` renders a granted-status paragraph/button *instead of* the checkbox; its controlled checkbox is checked only for `waitingPhone`, not existing GRANTED, and it renders `config.changeFailed` and `config.waitForPhone`. `includes/Checkout/CheckoutConsentCheckbox.php::classicFields()` defaults to unchecked and supplies a hidden error region in the withdrawal container. `CheckoutConsentStatusReader.php::logFailure()` only logs with `WP_DEBUG`; `CheckoutConsentEligibility.php` and `CheckoutConsentPublisher.php` contain caught exceptions without safe operational diagnostics. `CheckoutConsentEligibility::eligible()` makes a synchronous merchant-feature read during page-render eligibility and `ModaApiClient` uses a five-second default timeout; this needs explicit non-disruption validation. Existing nonce/session/proof checks and deliberate withdrawal boundaries should be **preserved**, not replaced by automatic uncheck-to-REVOKE. Modify these existing components and tests rather than creating another consent flow.

**Task-definition review boundary:** The snapshot includes a Woo client for `POST /v1/woocommerce/whatsapp-consent/status` with `woo.whatsapp-consent-status.v1`, but its existence in the Woo repository does **not** verify the deployed hosted API-006 contract. Reconcile against the architect-accepted API and prove authenticated end-to-end behaviour before completing this task.

Do not blindly implement an API-006 lookup from an invented endpoint/response schema. The API must also decide how the stored evidence reference and *current* CustomerPhone/STOP authority are authenticated, before Woo attaches its UI. Prefer existing WordPress account metadata and Woo session facilities over new identity tables. Store no installation bearer in a browser, output, session payload or log. Consider idempotent local proof invalidation after server ACKs and privacy-export/erasure implications of WordPress account metadata within the existing approved platform privacy scope.

**Blocks support:** WooCommerce's documented Additional Checkout Fields API does not implement an action button (only `select`, `text`, `checkbox`, `date`). A custom, version-supported checkout extension/SlotFill or documented inner block may be used; test the concrete installed Woo version rather than assuming a particular experimental slot is stable. If a supported integration is not available, record the limitation and seek an architect decision—do not retain a misleading dropdown solely to force a successful task. For Classic, prefer native Woo checkout rendering and event handling, not a hardcoded storefront template.

**Ownership/rollout:** No existing production users. The agreed breaking rollout allows dropping v1; coordinate API-007 deployment/availability and new Woo v2 producer, then API-006 proof read. Do not reintroduce deprecated version adapters or an untested read cache. `moda_architect` owns architecture-wide reconciliation and dependency promotion, and domain `_index.md` remains untouched until the architect session is explicitly closed. No implementation code, branch claim, commit or push is performed by this task-amendment patch itself.

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
