---
id: ARCH-050-WOOCOMMERCE-001
architecture_id: ARCH-050
title: Add the WooCommerce recovery-outreach notification opt-in
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-050-API-001
enables:
  - ARCH-050-SYSTEM-TEST-002
created: 2026-10-26
updated: 2026-10-27
---

# Add the WooCommerce recovery-outreach notification opt-in

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Render and persist the merchant opt-in inside the existing WooCommerce Recovery Settings form using the accepted v2 hosted policy contract.

## Context

`src/recovery-policy-client.js`, `src/recovery-policy-controller.js`, `src/recovery-settings/recovery-behaviour-panel.js`, validation helpers and WordPress REST PHP proxy own the existing settings flow.

## Scope

**Modify in `moda-interact-woocommerce/`:**

- `includes/Api/RecoveryPolicyResponseValidator.php` — exact v2 GET/PUT validator including new required top-level preference; `merchant` and `effective` values stay original four fields.
- `includes/Rest/RecoveryPolicyController.php` — retain capability/nonce, endpoint and PHP proxy; accepts new validated request via existing validator.
- `includes/Api/ModaApiClient.php` — retain hosted endpoint, authentication, HTTP error conversion and no-store behaviour; ensure strict response validator accepts v2.
- `src/recovery-policy-client.js` — v2 `parseMerchantRecoveryPolicy()`, required fifth-field `makeRecoveryPolicyUpdate()` and confirmation of saved preference.
- `src/recovery-settings/recovery-behaviour-validation.js` — draft initialization and dirty detection include the new Boolean; existing minute validations untouched.
- `src/recovery-settings/recovery-behaviour-fields.js` — new accessible, translated checkbox section `Notify me when initial recovery outreach starts`, not affected by follow-up toggle.
- `src/recovery-settings/recovery-behaviour-panel.js` — initialize/submit/refresh preference alongside recovery policy with no autosave.
- Update `tests/js/recovery-policy-integration.test.js`, `tests/js/recovery-behaviour-preview.test.js`, `tests/js/recovery-settings-screen.test.js`, `tests/RecoveryPolicyControllerTest.php` and PHP validator tests/fixtures if separate.

No new WordPress REST endpoint, public WordPress callback or schema. Do not change Support inbox here (WOOCOMMERCE-002).

## Out of Scope

- Creating a new Settings REST endpoint, modifying Background, changing billing/discount rules, Support notification action or enabling live Woo outbound.

## Requirements

- Mirror **API-001 v2** exactly: successful `GET|PUT /v1/merchant/recovery-policy` returns top-level `notifyOnInitialRecoveryOutreach: boolean`, `schemaVersion:2` and unmodified four-field `merchant/effective`. Strict PUT from WordPress to API has fifth required Boolean alongside old four fields.
- Update `RecoveryPolicyResponseValidator::isValid()` and `::isUpdate()` to validate v2 and **reject** missing/extra fields, string flags, malformed policy. `ModaApiClient::merchantRecoveryPolicy` must still pass only validated data and use installation credentials.
- In browser, update `parseMerchantRecoveryPolicy()` exact field set, `makeRecoveryPolicyUpdate(current,draft)`, and read-after-save field equality check. A successful save must confirm the Boolean equals the requested value.
- `recoveryBehaviourPreview()` includes `notifyOnInitialRecoveryOutreach: Boolean(effective?.notifyOnInitialRecoveryOutreach)`, but use **top-level policy response** to initialise it, NOT `merchant`/`effective` (which intentionally lack the field). Adjust call signatures appropriately and make `recoveryBehaviourChanged()` compare the toggle even if nothing else changed.
- Add new accessible checkbox in `RecoveryBehaviourFields`; leave `followUpEnabled` and follow-up minute enable/disable independent. Save only on explicit `Save recovery behaviour`; conflicts preserve unsaved local edits, refresh replaces them.
- Preserve `manage_woocommerce` permission, `X-WP-Nonce`, current-installation check and WordPress-to-hosted signature; never expose hosted credentials or use unauthenticated browser direct API calls.
- Use WordPress native `__()` translation and existing plugin i18n extraction/20-language verification. Do not hardcode English-only strings or bypass localisation.
- **Logger boundary:** WordPress PHP cannot consume a JavaScript logger; the WooCommerce browser bundle must not add `@modainteract/moda-interact-shared/logging` as a new dependency for this feature. Keep hosted `moda-interact-api` logging at its StructuredLogger boundary (API-001). In PHP, if this task adds/changes an operational `catch (\Throwable $error)` in `RecoveryPolicyController.php` or `ModaApiClient.php`, report the failure using the existing Woo/WordPress logging convention (`wc_get_logger()` with source `moda-interact`, stable operation/error class/code and no credential/request body) and preserve the existing `WP_Error`/HTTP response mapping. Do not create a new logging subsystem.
- The Woo browser client/controller must reject and surface network, malformed-v2, stale-revision and save failures in the existing visible error state; do not `catch {}` and return the existing snapshot, silently reset the checkbox or show a success banner on failure. Validation failures are expected UX outcomes, not server crash logs. Never include merchant installation secrets, raw HTTP bodies or customer data in logs.

## Work Items

- [x] Upgrade PHP `RecoveryPolicyResponseValidator` exact v2 request/response and confirm existing controller/client still proxy safely.
- [x] Upgrade browser `recovery-policy-client.js` v2 parsing/building/saved-value reconciliation.
- [x] Add preview/dirty/controlled checkbox UI, explicit save and conflict behaviour.
- [x] Extend PHP/JS tests for default OFF, ON/OFF save, stale revisions, malformed v2, nonce/capability and 20-language i18n checks.
- [x] Verify existing PHP/hosted failure logging and add bounded Woo logging at any newly introduced operational catch; add assertions for logged unexpected failures and visible failed-save state.

## Interfaces / Contracts

- **Consume API-001**: `MerchantRecoveryPolicyResponseV2.notifyOnInitialRecoveryOutreach: boolean` at top level and `RecoveryPolicyUpdateV2.notifyOnInitialRecoveryOutreach: boolean` in required PUT body.
- WordPress browser REST path unchanged: `/moda-interact/v1/merchant/recovery-policy` GET/PUT; PHP-to-hosted path unchanged: `/v1/merchant/recovery-policy` GET/PUT.
- Draft preview: `{ recoveryDelayMinutes:string, followUpEnabled:boolean, followUpDelayMinutes:string, notifyOnInitialRecoveryOutreach:boolean }`; `makeRecoveryPolicyUpdate` sends this Boolean with revision and other fields.
- No new `ShopRecoveryPolicyOverride` semantics and no separate config row in WordPress options.
- Logging/exception boundary: canonical Shared Node logger lives **only in hosted API** (API-001); PHP uses its existing Woo/WP logger if it catches operational faults, browser uses existing error state and rejects failed promises. No new external log endpoint.

## Dependencies

- `ARCH-050-API-001` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-SYSTEM-TEST-002` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [x] Woo merchant can switch ON/OFF independently, save, reload and see persisted value.
- [x] Preference-only change counts as dirty and is persisted; stale updates fail with policy conflict.
- [x] Browser JS, WordPress PHP and hosted v2 validators agree on field set; extra/missing or invalid values fail closed.
- [x] WordPress capability/nonce/installation and no-store security stay enforced; no production outbound sends are triggered merely by enabling setting.
- [x] Transport/validator/persistence failure is not silently ignored or displayed as a successful save; caught PHP server errors have bounded non-sensitive operational logging.
- [x] 20-language source/compile checks pass.

## Validation

- [x] `npm run test:js:unit` passed: 61 test files, 460 tests. `npm run test:php` passed: 198 tests, 1,509 assertions.
- [x] Negative-path coverage passed for failed hosted response reconciliation, preserved failed-save state, bounded exception logging, and a throwing Woo logger preserving the sanitized 503.
- [x] `npm run i18n:verify:20` passed (557 source messages, 19/19 packs); `npm run lint:php` and `git diff --check` passed.
- [x] `npm run build` passed with webpack's existing bundle-size performance warnings. `npm run lint:js` passed repository-wide after resolving reported formatting/style errors.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

The hosted API v2 and Woo plugin v2 are a coordinated rollout in development. Do not upgrade just the hosted DTO and leave PHP/browser strict parsers at v1. This task touches recovery settings and its PHP REST proxy **only**, not Support messaging or recovery-detail navigation. Keep plugin-only data at WordPress boundary and hosted DB access at API.

## Completion Report

### Status

Ready for Architect Review after addressing the Attempt 1 Changes Requested items.

### Files Changed

`includes/Api/RecoveryPolicyResponseValidator.php`; `includes/Rest/RecoveryPolicyController.php`; `src/recovery-policy-client.js`; `src/recovery-settings/recovery-behaviour-validation.js`; `src/recovery-settings/recovery-behaviour-fields.js`; `src/recovery-settings/recovery-behaviour-panel.js`; `tests/RecoveryPolicyControllerTest.php`; `tests/js/recovery-policy-integration.test.js`; `tests/js/recovery-behaviour-preview.test.js`; `tests/js/recovery-human-conversation.test.js`; `tests/i18n/locale-batch-010.test.mjs`; `tests/i18n/locale-batch-011.test.mjs`; `tests/i18n/locale-batch-012.test.mjs`; `tests/i18n/locale-batch-013.test.mjs`; `tests/i18n/release-source.test.mjs`; `tests/i18n/release-assets.test.mjs`; `tests/integration/action-scheduler-sql.test.mjs`; `tests/integration/run-wordpress.mjs`; `tests/integration/scenarios/checkout-clear-refill-wordpress.mjs`; `tests/integration/scenarios/checkout-clear-refill-wordpress.test.mjs`; `tests/integration/scenarios/checkout-wordpress.mjs`; `tests/integration/scenarios/order-wordpress.mjs`; `vitest.config.mjs`; `languages/moda-interact.pot`; all 19 supported `.po` catalogues.

### Work Completed

Implemented strict v2 response/request validation with the top-level Boolean preference, persisted it through the existing privileged proxy, added an accessible localized independent checkbox and dirty-state handling, and verified the returned Boolean on save. Added malformed v2, both preference values, notification-only dirty, mismatched save response, failed-save state and bounded PHP logging coverage. No new route or browser dependency was added.

**Attempt 1 review correction 1 — implemented:** Isolated `wc_get_logger()` and `logger->error()` failures in the unexpected-error path. If the Woo logger throws, a bounded PHP `error_log()` fallback records only operation and exception class/code, then the controller still returns the sanitized `REMOTE_UNAVAILABLE` 503. `RecoveryPolicyControllerTest` verifies the throwing logger path.

**Attempt 1 review correction 2 — implemented:** Installed the exact `package-lock.json` and `composer.lock` dependencies in the implementation worktree; all requested JS/PHP tests, JS lint and build were executed. Added a Vitest include config for the repository's actual JS unit suite, refreshed message-count expectations after adding four gettext strings, and corrected repository lint findings so the full JS lint passes.

### Validation Results

`npm run test:js:unit` passed (61 test files, 460 tests). `npm run test:php` passed (198 tests, 1,509 assertions), including the logger-sink failure case. `npm run lint:js` passed repository-wide; `npm run lint:php` passed. `npm run build` passed with webpack bundle-size performance warnings. `npm run i18n:verify:20` passed (557 source messages; all 19 translation packs compiled strictly). Targeted PHP/JS syntax checks and `git diff --check` passed.

### Deviations

The installed locked dependencies and build/test outputs are ignored worktree artifacts and are not committed. Four source strings increased catalogue expectations from 553 to 557. Repository JS lint required formatting and a small unused assertion-result cleanup in existing integration tests. The production build emits bundle-size recommendations but exits successfully. No product behavior deviation.

### Assumptions

`ARCH-050-API-001` is complete. Its v2 contract was verified in the API implementation; this WooCommerce branch consumes that exact response and request shape.

### Unresolved Issues

None.

### Architectural Concerns

Return newly discovered cross-repository/schema/security/contract issues to `moda_architect`.

### Task Branch / Worktree Evidence

Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-WOOCOMMERCE-001`, branch `task/ARCH-050-WOOCOMMERCE-001`. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-WOOCOMMERCE-001`, branch `task/ARCH-050-WOOCOMMERCE-001`, latest implementation commit `0cb22af` (`fix(woocommerce): preserve recovery policy 503 on logger failure`), pushed to `origin/task/ARCH-050-WOOCOMMERCE-001`. Per the Architect Review follow-up, the resubmitted task metadata retains `attempt: 1` and clears executor/claimed_at; the deterministic launcher recorded the correction claim as Attempt 2 (`64646302`).

## Architect Review — Attempt 1 — Changes Requested — 27 October 2026

### Review Status

Changes Requested.

### Review Notes

The v2 PHP/JS contract, explicit Boolean form value, preference-only dirty/persistence path, admin-override separation, and translated checkbox are consistent with the task. The implementation branch is clean and published. Acceptance is blocked by the following corrections:

1. In `includes/Rest/RecoveryPolicyController.php`, isolate failures from `wc_get_logger()` / `logger->error()` inside the unexpected-exception catch. As written, if the logging sink throws, the handler exits before returning the existing `REMOTE_UNAVAILABLE` 503 response. Preserve that response mapping when the logger fails, and add a test with a throwing Woo logger that proves the controller still returns the sanitized 503.
2. Run the required existing `npm run test:js:unit`, `npm run test:php`, `npm run lint:js`, and `npm run build` in an environment with the repository dependencies installed. Update the validation report with actual outcomes; fix any failures before resubmitting. The current report explicitly marks all four unverified because `node_modules` and `vendor` are absent. Static syntax checks and i18n/PHP lint do not cover these required behavioral and bundle checks.

### Reviewed Files

- `moda-interact-woocommerce/includes/Api/RecoveryPolicyResponseValidator.php`
- `moda-interact-woocommerce/includes/Rest/RecoveryPolicyController.php`
- `moda-interact-woocommerce/src/recovery-policy-client.js`
- `moda-interact-woocommerce/src/recovery-settings/recovery-behaviour-validation.js`
- `moda-interact-woocommerce/src/recovery-settings/recovery-behaviour-fields.js`
- `moda-interact-woocommerce/src/recovery-settings/recovery-behaviour-panel.js`
- PHP/JS contract and route tests, locale catalogs, and Attempt 1 Completion Report.

### Validation Reviewed

- `npm run i18n:verify:20` passed (557 source messages; 19/19 packs), `npm run lint:php` passed, targeted PHP/JS syntax checks passed, and `git diff --check` passed, per the task report.
- `npm run test:js:unit`, `npm run test:php`, `npm run lint:js`, and `npm run build` were not run because dependencies are absent from the implementation worktree. These checks remain required before acceptance.
- Implementation branch `task/ARCH-050-WOOCOMMERCE-001` is clean and published at `f2921409f5dad286be2fde6f5a30e99e287e78f7`. No task branch was merged to `main`.

### Architecture Conformance

The field contract and UI/data-flow changes follow the intended API/Woo boundary. The uncaught logger-sink failure violates the explicit requirement to preserve existing HTTP error mapping and must be corrected before acceptance.

### Follow-up

Keep `attempt: 1`; clear executor and claimed_at, make the logger failure path safe, complete the outstanding validation, update the report, and resubmit for architect review. Do not start dependent system testing from this review.

## Architect Dependency Frontier Reconciliation — 27 October 2026

`ARCH-050-API-001` was accepted and completed at Attempt 1. This task's sole declared dependency is therefore satisfied, so its status advances from `pending` to `ready`. It remains unclaimed at Attempt 0 (`executor: null`, `claimed_at: null`); no implementation worktree or attempt was started.
