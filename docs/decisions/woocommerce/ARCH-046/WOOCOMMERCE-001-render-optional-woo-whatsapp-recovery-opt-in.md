---
id: ARCH-046-WOOCOMMERCE-001
architecture_id: ARCH-046
title: Register Moda Woo consent checkbox and Recovery Settings guidance
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 26
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-23
---

# Register Moda Woo consent checkbox and Recovery Settings guidance

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** developer Attempt 1 was claimed on 2026-10-23. The WooCommerce implementation is committed and published as `511bab8111fba486395a62aed8d18b0f7914c499` on `task/ARCH-046-WOOCOMMERCE-001`; this submission is for architectural review and is not yet accepted or complete.

## Objective

Register and conditionally display Moda’s own optional WhatsApp checkout-recovery checkbox in Classic and Blocks, and explain the opt-in to merchants in the existing Recovery Settings. No consent-source selector or third-party adapter.

## Context

Moda alone owns its checkout checkbox; any other plugin's checkout UI is outside Moda's scope. `ARCH-046-API-003` and `ARCH-046-WOOCOMMERCE-005` are Superseded. The checkbox is a runtime registration when the Moda plugin is connected/authorised and the existing recovery feature is enabled; no merchant consent-source configuration exists.

## Scope

- Register supported Classic and Checkout Blocks checkbox integrations on eligible requests for an active connected installation with the existing Checkout Recovery feature enabled. Initial checkbox state is unchecked and optional. When the feature is disabled, installation disconnected/revoked or plugin deactivated, omit the field on subsequent page loads. Do not modify themes or interact with third-party plugins.
- Display purpose-specific, clearly worded 20-locale disclosure describing **WhatsApp reminders for checkouts the customer leaves unfinished at this store and exact phone**. Explain withdrawal and distinguish an unchecked new checkbox from any earlier recorded permission; never create a new affirmative grant from UI hydration. Authenticated current-preference display and deliberate later GRANT/REVOKE are assigned to `ARCH-046-WOOCOMMERCE-003`, following consent capture in `ARCH-046-WOOCOMMERCE-002`, rather than this UI-registration task.
- Keep the field optional, accessible and compatible with guests, logged-in customers, HPOS and both checkout types. Placement near billing phone preferred when officially supported; avoid fragile JS insertion. Registration must be idempotent across plugin upgrades/reactivation. An already-open checkout may display stale UI but cannot grant consent without server-side revalidation of current installation, recovery-feature eligibility and customer/phone identity.
- In the existing merchant Recovery Settings, explain exactly what the optional WhatsApp reminder covers, how current grants/withdrawals affect recovery, and that no consent means no recovery. Retain existing 20-locale localisation. Do **not** add a consent-source dropdown or controls for other plugins. The actual hosted consent write belongs to WOOCOMMERCE-002/API-001.

## Out of Scope

- No standalone plugin detector, API consent write, Woo recovery engine or cookie CMP. No third-party adapter automatically registered.

## Requirements

- [x] The optional Moda checkbox must expressly describe **WhatsApp abandoned-basket/checkout-recovery marketing reminders**, identify the merchant, and remain unchecked. It must not be described merely as transactional order updates or consent to provide a phone number; preserve the displayed wording/version/locale for the existing evidence contract.

- [x] One Moda checkbox at most on eligible Classic/Blocks checkout; none when the connection or recovery feature is inactive.
- [x] Wording is broad enough only for the **agreed store-specific unfinished-checkout reminder purpose**; no prechecked new grant.

- The checkbox is entirely Moda-owned. Do not detect, hide, disable or warn about other plugins’ consent checkboxes; there is no supported-external mode in v1. Consent eligibility requires an independently verified customer grant through API-001.
- Use official Classic/Blocks extension locations, with accessible text and 20 locale handling, but do not assume Woo Blocks order-only field persistence is evidence of abandonment-stage grant.

## Work Items

- [x] Register one conditional Classic and Blocks checkbox and add customer-consent guidance to existing Woo Recovery Settings without modifying the merchant theme.
- [x] Add focused PHP and JavaScript tests for initial unchecked/optional state, feature eligibility, disconnect/reconnect and revoked credentials, duplicate Classic/Blocks field registration, disclosure identity, merchant guidance and strict 20-locale coverage.

Integrated rendered-checkout behavior, guest/account identity, HPOS, upgrade/reactivation, stale open checkouts, customer-preference visibility and checkout accessibility are verified by `ARCH-046-SYSTEM-TEST-001` after the required downstream implementation tasks. They are **not developer-run acceptance checks** for this repository implementation task.

## Interfaces / Contracts

Consumes existing plugin/installation state and recovery feature eligibility. Produces Moda checkout UI and merchant Recovery Settings guidance only; consent capture remains WOOCOMMERCE-002 and persistence remains API-001. No API-003 or WOOCOMMERCE-005.

## Dependencies

None

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Supported Classic and Blocks hooks register an optional, initially unchecked checkbox only for an authorised connected installation with effective, plan-eligible Checkout Recovery. The registered field is not required for checkout; actual customer-facing rendering is reserved for `ARCH-046-SYSTEM-TEST-001`.
- [x] Duplicate Classic filter and Blocks registration are prevented; disabled, invalidated, revoked or disconnected installation/feature checks fail closed. This presentation-only task never creates a grant; server-side consent identity, hosted acknowledgment and stale-session defenses belong to `ARCH-046-WOOCOMMERCE-002/003` and integrated system testing.

- [x] Merchant Recovery Settings contains consent guidance using the existing 20-locale source/catalogue pipeline, without a consent-source selector or changes to third-party checkout plugins.

## Validation

- [x] `npm run test:php` — 160/160 PHPUnit tests passed (1,209 assertions), including `CheckoutConsentCheckboxTest.php`.
- [x] `npm run test:js` — 437/437 JavaScript tests and 52/52 Node integration/i18n tests passed.
- [x] `npm run test:i18n` — 28/28 i18n tests passed; these overlap with the combined `test:js` command and are not counted as distinct new tests.
- [x] `npm run i18n:verify:20` — 486 source messages verified, 19/19 translated packs, 38 generated assets.
- [x] `npm run build` — WordPress scripts production build passed, with three bundle-performance warnings.
- [x] `npm run lint:php` — PHP syntax validation passed.
- [x] `npm run lint:js` — zero errors, six warnings in unchanged `tests/js/billing-screen.test.js`.
- [x] `git diff --check` — no whitespace errors reported.

**System-test ownership:** Real Classic/Blocks checkout, HPOS, guest/account behavior, deactivation/reconnection, stale pages, customer-preference display, disclosure visibility, end-to-end consent acknowledgement and related merchant-environment checks are assigned to `ARCH-046-SYSTEM-TEST-001`, following completion of its declared implementation dependencies. No developer-managed checkout smoke test is required for acceptance of this repository task.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

The field is not a licence to send any WhatsApp message; actual grant requires subsequent hosted DB acknowledgement and exact phone binding.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

Ready for Review — **developer Attempt 1**. Claimed `2026-10-23T10:46:50Z`; implementation committed and pushed to `origin/task/ARCH-046-WOOCOMMERCE-001` at `511bab8111fba486395a62aed8d18b0f7914c499`. Architecture acceptance and the developer's explicit completion decision remain outstanding.

### Files Changed

The implementation commit changed **35 WooCommerce files** (777 insertions, 15 deletions), including:

- `composer.json` and `includes/Runtime.php` — register the consent presentation classes.
- `includes/Checkout/CheckoutConsentCheckbox.php` and `includes/Checkout/CheckoutConsentEligibility.php` — conditional Classic/Blocks field presentation and authenticated feature eligibility.
- `src/recovery-settings/recovery-settings-screen.js` and `src/recovery-settings/whatsapp-consent-guidance.js` — merchant consent guidance.
- `tests/CheckoutConsentCheckboxTest.php`, `tests/js/recovery-settings-screen.test.js` and `tests/js/whatsapp-consent-guidance.test.js` — focused PHP/JS coverage.
- `languages/moda-interact.pot`, 19 `languages/moda-interact-*.po` catalogues, and existing `tests/i18n/` batch/release checks — 20-locale parity.

No database schema, hosted API source, architecture document, domain `_index.md` or other repository implementation was modified by this task.

### Work Completed

- Registered an optional Classic checkout field near billing phone and a WooCommerce Additional Checkout Fields checkbox for Blocks in the supported `order` location. Classic starts unchecked; Blocks uses order-scoped field registration rather than hydrating an earlier customer-profile preference. Neither is a verified consent grant.
- Made registration conditional on a valid site-bound installation and authenticated, effective, plan-eligible Checkout Recovery feature. Re-read installation identity after the hosted response so disconnect/reconnect or credential rotation fails closed on subsequent requests.
- Added a merchant-specific, versioned, locale-aware WhatsApp unfinished-checkout marketing disclosure; preserved the disclosure version and locale in field metadata for the later consent-capture task.
- Added informational Recovery Settings guidance explaining purpose, optional opt-in, no recovery without verified permission, withdrawal, and why an unchecked later checkout does not itself revoke an earlier grant.
- Kept consent mutation, authenticated customer preference display and later GRANT/REVOKE outside this checkbox-registration implementation; these belong to `ARCH-046-WOOCOMMERCE-002/003` and the hosted `ARCH-046-API-001` contract.
- Updated the English source catalogue, 19 translated packs, and strict i18n release fixtures. Corrected one apostrophe-related JavaScript parse error in the guidance during local validation before the successful rerun.

### Validation Results

Recorded from local terminal validation `typescript(20261023-111408)`:

- [x] `npm run i18n:verify:20` — 486 PHP/React source messages; 19/19 translated packs; 38 compiled language assets.
- [x] `npm run build` — passed. Webpack reported three non-blocking performance warnings.
- [x] `npm run test:php` — PHPUnit **160/160 passed**, **1,209 assertions** (after building the required admin assets).
- [x] `npm run test:js` — **437/437 JS tests** across 57 files; **52/52 Node integration/i18n tests**.
- [x] `npm run test:i18n` — **28/28 passed**. These tests also appear in the combined `test:js` run; do not double-count them.
- [x] `npm run lint:php` — passed.
- [x] `npm run lint:js` — passed with **zero errors**, six warnings in unchanged `tests/js/billing-screen.test.js` (`@wordpress/no-global-active-element`).
- [x] `git diff --check` — no whitespace errors reported.
- [x] `git commit` and `git push -u origin task/ARCH-046-WOOCOMMERCE-001` — implementation published at **`511bab8111fba486395a62aed8d18b0f7914c499`**, 35 files changed.

**Integrated runtime validation is deferred:** Real customer-facing Classic/Blocks flows, guest/account/HPOS behavior, disconnect/upgrade/reconnect, stale checkout pages, current-preference display and server-side consent-write ordering are in `ARCH-046-SYSTEM-TEST-001` and are not prerequisite checks in this repository task.

### Deviations

- The officially supported WooCommerce Blocks additional-field API registers at `order` rather than an unsupported billing-phone-adjacent position. This also avoids treating customer-profile hydration as a fresh opt-in.
- A one-line JavaScript quoting fix was required during initial implementation validation; the successful full test rerun includes that correction.
- Build-generated assets must exist before running the whole PHP suite because admin asset enqueue tests check for them. Validation reran in that order and passed.

### Assumptions

- The checkbox and merchant guidance are presentation only. `ARCH-046-WOOCOMMERCE-002` owns server-side capture and publishing to the hosted consent API; `ARCH-046-WOOCOMMERCE-003` owns returning-customer preference changes. Consent does not trigger recovery work by itself.
- The `ARCH-046-SYSTEM-TEST-001` system test owns live checkout and platform-integration verification once its downstream dependencies are complete. No additional developer-operated checkout environment is required for this implementation task.

### Unresolved Issues

No failing automated validation checks remain in the supplied successful run. Six existing JavaScript lint warnings and three Webpack performance warnings are recorded as non-blocking.

The developer's terminal output confirms the implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-WOOCOMMERCE-001` and published task branch, but no complete launcher-resolved **parent worktree and start-of-attempt synchronization packet** was included in the provided evidence. The reviewer should verify or request that evidence before acceptance; it is not claimed as completed here.

### Architectural Concerns

- The task does not interpret an order-scoped Blocks field as pre-submission WhatsApp consent evidence. The subsequent server-side capture must validate exact checkout/customer/phone identity and obtain hosted acknowledgement before recognizing a grant.
- The original portable scope mentioned displaying a returning customer's current preference; authenticated current-preference display belongs to `ARCH-046-WOOCOMMERCE-003`. The architect should confirm this ownership boundary while reviewing this registration-only task.
- Full real-checkout rendering, HPOS, accessibility and consent-persistence behavior remain explicit terminal system-test acceptance criteria; this Completion Report does **not** claim those flows have passed.

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

## Developer Takeover

On 2026-10-23, `/moda_developer_create ARCH-046-WOOCOMMERCE-001` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_woocommerce`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The canonical launcher claimed developer Attempt 1 at `2026-10-23T10:46:50Z`; the implementation was subsequently committed and published as `511bab8111fba486395a62aed8d18b0f7914c499`.
