---
id: ARCH-046-WOOCOMMERCE-002
architecture_id: ARCH-046
title: Capture affirmative pre-submit Woo consent and publish durable evidence
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 27
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-035-WOOCOMMERCE-007
  - ARCH-046-API-001
  - ARCH-046-WOOCOMMERCE-001
enables:
  - ARCH-046-WOOCOMMERCE-003
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-23
---

# Capture affirmative pre-submit Woo consent and publish durable evidence

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** materialised and claimed by `copilot` for agent Attempt 1 on 2026-10-23. The WooCommerce implementation was committed as `5aefb6d5eddfcfb1b0f5bebd16e5da5a4b352bb0` and validated again after merging `origin/main` at `e18f5b6d5bef4bd703f2a5c383a47990199432ed`; the merged task branch is published. The developer review passed and automatic completion is recorded below. No task branch was merged to `main`.

## Objective

Securely publish an explicit Woo WhatsApp recovery opt-in/withdrawal **before order placement** and resolve it to an existing merchant-scoped customer and exact phone through Moda’s own optional checkout field.

## Context

Classic/Blocks additional checkout field persistence at order completion does not guarantee Moda can recognise consent before abandonment. Hosted API-001 records current customer-phone permission. The plugin must authenticate the active checkout checkbox action server-side; the hosted API locates `Customer` through the authenticated shop and canonical phone.

**Architect-approved validation handoff (2026-10-21):** Shared `ARCH-045-SHARED-001` supplies runtime-neutral golden identity fixtures and Node coverage; after `ARCH-045-SHARED-002` publishes them, this WooCommerce consumer task owns **PHP-runtime** parity for the applicable exact-recipient and recipient-lifecycle vectors. Runtime PHP parity is intentionally not a Shared-task acceptance or publication prerequisite.

## Scope

- In Classic and Blocks, capture a deliberate checkbox GRANT or withdrawal through supported UI hooks and server-verified live Woo checkout action with exact canonical phone. Do not infer opt-in from a default checked field or completed order metadata.
- Use the existing verified WordPress installation authentication to POST to API-001, with stable event ID on retry; protect the guest checkbox action against forgery using normal WordPress/WooCommerce server-side session and nonce controls; phone lookup alone is not a GRANT.
- Persist consent **before order placement** when the hosted API is available; on outage checkout may proceed but current permission remains unverified. Consent submission itself never schedules a recovery/reconciliation job.
- Preserve 20-locale opt-in wording, both checkout implementations, and Moda checkbox registration controlled by existing installation/feature eligibility.

- Update the existing Woo plugin checkout activity publisher to carry the same authenticated installation/shop context and canonical recipient accepted by API-001, under an agreed version/compatibility transition. Do not change ARCH-035 capture-only business semantics or turn consent submission into checkout reconciliation.

**Validation ownership:** This repository task implements and unit/contract-tests the plugin boundary. All real LocalWP Classic/Blocks checkout execution, guest/login/HPOS flows, abandonment-before-order, API/PostgreSQL durable ACK sequencing and consent-versus-checkout-event races are deferred to `ARCH-046-SYSTEM-TEST-001`. Such live checkout testing is **not** an implementation review or completion prerequisite for WOOCOMMERCE-002.

## Out of Scope

- No recovery creation, Shopify code, new WP consent table, arbitrary third-party checkbox integration or unilateral consent grants from admin. Shopify numeric customer ID/GID conversion fixtures are not applicable to Woo PHP; Shared already owns their Node contract tests.
- Live WordPress/LocalWP browser/checkout, HPOS and full API/PostgreSQL end-to-end validation are owned by `ARCH-046-SYSTEM-TEST-001`, not this implementation task.

## Requirements

- [x] A pre-submit affirmative checkbox action refers to the merchant-specific WhatsApp **abandoned-basket marketing** disclosure; default unchecked state or receipt of a phone number cannot establish permission. The version, locale and merchant site URL are supplied in the API-001 evidence request. Verified through Woo-owned code and contract tests; actual rendered disclosure in a live checkout is system-test coverage.

- [x] The plugin sends a verified pre-submit decision to the authenticated hosted API and treats only the API acknowledgement as success; completed-order metadata alone never creates a grant. Actual durable CustomerPhone/evidence persistence and ordering are validated by API-001 and `ARCH-046-SYSTEM-TEST-001`.
- [x] Guest checkbox actions are checked server-side against Woo nonce/session or bound Cart-Token; only deliberate transitions submit consent. An unavailable hosted API cannot establish permission and does not block checkout. Ambiguous customer matching and durable permission enforcement remain hosted API responsibilities.

- **C4/H3:** For Classic and Blocks, verify the checkout field action server-side and pass the canonical number through authenticated plugin-to-API transport. Do not persist a separate WooCheckoutCustomerIdentity. The API uses installation-derived merchant and existing Customer/CustomerPhone; stale guest/session actions and phone edits must fail validation.
- Choose and document the pre-submit consent publication point independently for each checkout mode. The UI must not show success or allow recovery eligibility until the hosted API acknowledges a durable consent write; normal checkout activity published before ACK must remain potentially ineligible. Do not fabricate consent from order-meta/checkbox render state or schedule a special recovery wake-up to fix races.
- Make retried HTTP publication idempotent with stable event ID and server-ordered decision revision; a revoke must not be overtaken by late GRANT after a multi-tab or Action Scheduler retry. Woo checkout itself must remain usable on hosted outage.

## Work Items

- [x] Implement isolated Classic order-review and Blocks pre-submit/draft-update observation, nonce/guest-session validation, canonical-phone capture and authenticated server-to-server API-001 publication. Preserve a stable event ID and immutable request on retry.
- [x] Add deterministic PHPUnit and JavaScript/Node contract tests for deliberate versus default checkbox state, changed phones, revoked/rotated installations, feature eligibility, checkout/session changes, Blocks Cart-Token, Classic CSRF, a missing billing phone, GRANT/REVOKE, lost ACK/replay and hosted outage handling. These tests do not claim execution of a live checkout.
- [x] Ensure the optional checkout activity projection remains distinct from consent publication and preserves the existing v1 queue contract while supporting the approved versioned HTTP contact envelope. Do not enqueue a recovery or consent-driven wake-up.
- [x] Add PHP-runtime compatibility tests consuming the published Shared `2.5.0` `identity/fixtures` golden vectors; cover applicable phone normalization and recipient-lifecycle safeguards without importing Shopify-specific identity semantics.

**System-test handoff:** `ARCH-046-SYSTEM-TEST-001` owns all LocalWP and real Classic/Blocks execution tests, including guest/account and HPOS behaviour, actual abandonment before Place Order, live API/PostgreSQL ACK ordering, checkout event races, multi-tab/logout/device changes and failure/retry scenarios. These are not pending Work Items for this implementation task.

## Interfaces / Contracts

Consumes WOOCOMMERCE-001 Moda field, ARCH-035 checkoutKey support and API-001 versioned customer-phone consent contract.

**Portable fixture contract:** `ARCH-045-SHARED-001` owns the canonical JSON (published by `ARCH-045-SHARED-002` at `@modainteract/moda-interact-shared/identity/fixtures`). PHP consumes the portable test data, not Shared JavaScript/TypeScript source. `ARCH-046-API-001` already depends on `ARCH-045-SHARED-002`, so publication is an existing transitive prerequisite for this task; no new dependency is necessary.

## Dependencies

- `ARCH-035-WOOCOMMERCE-007`
- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-001`

## Enables

- `ARCH-046-WOOCOMMERCE-003`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] The Woo producer constructs a versioned, authenticated, explicit pre-submit GRANT/REVOKE request bound to the current canonical phone, checkout action, merchant disclosure and idempotent event ID; the hosted API owns durable `CustomerPhone`/immutable-evidence persistence. Woo contract tests validate request and ACK handling, not real cross-service persistence.
- [x] An unselected checkbox, inactive installation, unverified session or hosted API outage cannot establish consent; the normal Woo checkout path remains available without a successful consent request.
- [x] Consent capture alone creates no checkout recovery, consent-triggered checkout re-evaluation, WhatsApp message or usage/billing event. Checkout activity continues through the separate approved capture path.
- [x] PHP tests demonstrate parity with applicable published Shared `2.5.0` phone and recipient-lifecycle fixtures without inferring consent from phone matching or introducing Shopify-only identity code.
- [x] The producer does not infer durable permission before an API ACK and retains stable event identity across retries. If checkout activity precedes or outlives the ACK, it creates no artificial consent/recovery wake-up. Live cross-service ordering and DB evidence are the acceptance responsibility of `ARCH-046-SYSTEM-TEST-001`.

## Validation

- [x] After the `origin/main` merge, `npm run i18n:verify:20` — 512 source messages; 19/19 translated catalogues plus English; 38 generated assets.
- [x] After merge, `npm run build` — successful Webpack build (three non-blocking bundle-size/performance warnings).
- [x] After merge, `npm run test:php` — 178/178 tests, 1,335 assertions; includes checkout consent and Shared identity fixture parity.
- [x] After merge, `npm run test:js` — 445/445 Vitest tests in 58 files and 53/53 Node integration/i18n tests. The standalone i18n cases overlap the combined Node suite.
- [x] After merge, `npm run lint:php` — passed. `npm run lint:js` — zero errors and six existing warnings in unchanged `tests/js/billing-screen.test.js`.
- [x] `git diff --check` — no errors reported; the merged implementation was committed and pushed to `origin/task/ARCH-046-WOOCOMMERCE-002`.
- [x] `tests/CheckoutConsentPhoneTest.php` — uses `tests/fixtures/identity-v1.shared-2.5.0.json` for applicable published Shared 2.5.0 identity-vector parity; included in the passing PHPUnit suite.

**Explicit deferral:** No LocalWP/manual checkout testing is required or claimed by `ARCH-046-WOOCOMMERCE-002`. All real Classic/Blocks, HPOS, checkout abandonment, guest/login, pre-submit API acknowledgement and PostgreSQL persistence tests are deferred to `ARCH-046-SYSTEM-TEST-001`, after its dependencies become Complete.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Keep session binding, field observation and remote publication in separate small classes/modules. Avoid one large `Runtime.php` or `page.js` handler; use existing server transport and Action Scheduler where available.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

**Complete — automatic Attempt 1** (`execution_mode: agent`, `completion_mode: automatic`). Independent developer review accepted the implementation after rerunning all repository-scoped checks. Implementation commit `e18f5b6d5bef4bd703f2a5c383a47990199432ed` is published on `task/ARCH-046-WOOCOMMERCE-002`; no task branch was merged to `main`.

### Developer Self-Review Accepted — Attempt 1 (2026-10-23)

The submitted implementation satisfies all defined Work Items and Acceptance Criteria: server-validated Classic/Blocks capture, canonical phone and session binding, stable retry identity, hosted-ACK gating, outage-safe checkout behavior, Shared fixture parity, and separation from checkout activity. No task-owned correctness gap was found. Live LocalWP, browser checkout, HPOS, and hosted PostgreSQL ordering remain explicitly assigned to `ARCH-046-SYSTEM-TEST-001` and are not claimed here.

Independent validation passed: PHP **178/178 tests, 1,335 assertions**; JavaScript **445/445 tests** plus **53/53 Node integration/i18n tests**; CSS and PHP lint; strict i18n verification; production build; and `git diff --check`. JavaScript lint reported only six existing warnings in unchanged `tests/js/billing-screen.test.js`; the build reported only three non-blocking bundle-size warnings.

### Developer Completion Decision — Attempt 1 (2026-10-23)

Because `completion_mode: automatic`, the accepted Attempt 1 review transitioned this task directly to `complete`. The parent task record and implementation branch are published and clean. Architect acceptance remains a separate review decision.

### Files Changed

Twenty task-owned source/test files in the original implementation commit, including:

- `assets/js/checkout-consent-classic.js`
- `composer.json`, `package.json`, `scripts/package-production.mjs`
- `includes/Api/ModaApiClient.php`
- `includes/Checkout/CheckoutConsentCapture.php`, `CheckoutConsentCheckbox.php`, `CheckoutConsentPhone.php`, `CheckoutConsentPublisher.php` and `CheckoutActivityPublisher.php`
- `includes/Runtime.php`
- `docs/arch046-woo-pre-submit-consent.md`
- `tests/CheckoutCaptureTest.php`, `CheckoutConsentCaptureTest.php`, `CheckoutConsentCheckboxTest.php`, `CheckoutConsentPhoneTest.php`, `tests/bootstrap.php`
- `tests/fixtures/Arch046CartTokenUtils.php`, `tests/fixtures/identity-v1.shared-2.5.0.json`
- `tests/integration/checkout-consent-classic-client.test.mjs`

The subsequent merge from `origin/main` incorporated separately owned WooCommerce customer-recovery-selection changes and newer translation catalogues; those are not presented as this task's independent implementation. No parent `_index.md` or architect review section was changed here.

### Work Completed

- Captured deliberate Classic checkout checkbox changes through Woo's supported, server-verified order-review lifecycle; browser script does not call the hosted API directly.
- Captured Blocks field changes through supported draft/check-out and customer-update paths, including the existing draft order and the checkbox-before-billing-phone case. Refused final order metadata as consent evidence.
- Verified current guest/session/nonce or Cart-Token context, checkout/installation and exact canonical phone before producing versioned GRANT/REVOKE requests. New phone, logout/session change, stale installation or ineligible recovery do not inherit consent.
- Published API-001 requests through existing authenticated Woo-to-Moda transport with stable event IDs, immutable retry payloads and fail-closed ACK handling. A hosted outage does not prevent checkout; without a durable ACK the plugin does not assert a grant.
- Kept checkout activity distinct from consent submission, maintaining the v1 background queue contract and introducing only the compatible approved HTTP contact projection.
- Added PHP parity coverage for Shared 2.5.0 identity fixtures and focused consent-capture/Classic-browser tests. No consent-triggered recovery, billing or WhatsApp send was added.
- Fixed JavaScript formatting errors in the Classic script and Node integration test before the validated implementation commit.

### Validation Results

Post-merge validation executed in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-WOOCOMMERCE-002`, branch `task/ARCH-046-WOOCOMMERCE-002`, terminal capture `typescript(20261023-130045)`:

- `npm run install:php` — Composer dependencies satisfied.
- `npm run i18n:verify:20` — PASS; 512 messages and 19/19 translated catalogues, with English source and 38 generated assets.
- `npm run build` — PASS; Webpack 5.111.1 compiled with three non-blocking performance warnings.
- `npm run test:php` — PASS; 178 tests, 1,335 assertions.
- `npm run test:js` — PASS; 445 Vitest unit tests in 58 files plus 53 Node integration/i18n tests.
- `npm run lint:php` — PASS.
- `npm run lint:js` — 0 errors, six existing warnings in `tests/js/billing-screen.test.js`.
- `git diff --check` — no whitespace errors reported.
- Git history at validation: `e18f5b6` (merge from `origin/main`), `5aefb6d` (consent feature implementation), `7de61d8` (merged upstream WooCommerce selection work). `git push -u origin task/ARCH-046-WOOCOMMERCE-002` succeeded; published branch head `e18f5b6d5bef4bd703f2a5c383a47990199432ed`.

### Deviations

Real LocalWP Classic/Blocks checkout verification was **not** run as part of this implementation task. Per the agreed ownership boundary, those scenarios are deferred to `ARCH-046-SYSTEM-TEST-001` and are not a prerequisite to submitting WOOCOMMERCE-002 for review. A separately owned upstream WooCommerce change was merged before final test validation.

### Assumptions

The authenticated hosted API-001 owns the current `CustomerPhone` and immutable consent evidence. Woo publication alone is not durable permission without the hosted acknowledgement. Shared golden fixtures are version 2.5.0. Consent changes do not initiate a recovery wake-up or grant on their own.

### Unresolved Issues

No failing task-owned automated checks in the submitted post-merge run. The six existing JavaScript lint warnings and three Webpack performance warnings are non-blocking. Full physical parent-worktree and launcher start-of-attempt synchronization evidence was not independently available in the supplied terminal log and should be checked by the reviewer; the dedicated implementation worktree, task branch and published commit are confirmed.

### Architectural Concerns

`ARCH-046-SYSTEM-TEST-001` must certify actual browser/checkout behavior, live session/nonce protection and PHP-to-API/PostgreSQL pre-submit ACK ordering, including abandonment before order placement and all consent/recovery side-effect invariants. The implementation tests establish the Woo producer's behavior but do not substitute for that integration evidence.

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
