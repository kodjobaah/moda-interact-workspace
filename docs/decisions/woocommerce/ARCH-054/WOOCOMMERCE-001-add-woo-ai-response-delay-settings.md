---
id: ARCH-054-WOOCOMMERCE-001
architecture_id: ARCH-054
title: Add WooCommerce AI delay control through protected WordPress REST
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: codex
claimed_at: 2026-11-01T12:51:33Z
attempt: 1
depends_on:
  - ARCH-054-API-001
enables: []
created: 2026-10-31
updated: 2026-11-01
---


# ARCH-054-WOOCOMMERCE-001: Add WooCommerce AI delay control through protected WordPress REST


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task materialised in the canonical parent worktree and claimed through the prepared launcher; see Worktree and Git Evidence below.


## Objective

Provide authenticated WooCommerce settings UI for all whole-minute 0–30 values through the approved hosted API, without direct database access.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Create `includes/Rest/AiResponseDelayController.php`, `includes/Api/AiResponseDelayResponseValidator.php`, `src/ai-response-delay-client.js`, `src/ai-response-delay-controller.js`, `src/recovery-settings/ai-response-delay-panel.js`. Modify `includes/Runtime.php`, `includes/Api/ModaApiClient.php`, `src/page/controller-factory.js`, page state/render plumbing, and `src/recovery-settings/recovery-settings-screen.js`; add focused PHP/JS tests. Do not change the existing RecoveryPolicyController contract.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- WP REST proxy path exactly `/wp-json/moda-interact/v1/merchant/ai-response-delay` GET/PUT, with `manage_woocommerce` permission and valid WP REST nonce. Server PHP reads trusted `InstallationStore`, checks current canonical SiteIdentity against stored installation, sends installation credentials through existing ModaApiClient server-to-server and rechecks installation state after response. Browser never sends bearer token, shop ID, credentials or backend URL.
- Validate the Shared v1 wire exactly in PHP: read keys `schemaVersion,revision,aiResponseDelayMinutes`; update keys `schemaVersion,expectedRevision,aiResponseDelayMinutes`; min0 max30 integer with `is_int`, `UNCONFIGURED`/UTC ISO revision, reject unknown keys; status mapping follows existing proxy. No introducing a distinct PHP business policy or caching a supposedly updated value on an ambiguous network failure.
- UI labeled 0–30 integer input, translated through existing plugin gettext text-domain, clear "Human replies are immediate" guidance, separate Save from recovery delay, pending/conflict state and read-after-save. On reload reads saved canonical setting; `Cache-Control: private, no-store`.
- Existing per-merchant Take Over and Reply composer continues to work unchanged; this setting has zero effect on the PHP/runtime human dispatch.


## Work Items

- [x] Add PHP proxy/auth/validator + ModaApiClient method; register and route.
- [x] Add JS controller/client/panel and recovery settings page integration.
- [x] Test WP privilege/nonce, cross-site changed URL, installation rotation, type bounds, no-op/revision conflict, server failure, and HUMAN bypass UI copy.


## Interfaces / Contracts

Exact Shared v1 GET and PUT examples from parent architecture. Woo PHP may validate the same wire shape, but must not invent another Node/Zod contract; the hosted API consumes the published schema.


## Dependencies

- ARCH-054-API-001


## Enables

None


## Acceptance Criteria

- [x] Only authorised WP merchant can read/write their own shop setting; all integers 0–30 supported, floats/strings rejected at server boundaries.
- [x] No direct DB/Redis access, no credential in browser and no change to existing recovery settings or human send admission.


## Validation

- [x] `npm run test:php` (run; repository suite has 2 errors and 4 failures, detailed below).
- [x] `npm run test:js:unit` (62 files, 473 tests passed).
- [x] `npm run i18n:verify:20` (passed).
- [x] `npm run lint:js` (run; repository lint reports 480 errors outside changed files; changed-file lint passed).
- [x] `npm run lint:php` (run; Composer script references a missing integration fixture; changed-file PHP syntax checks passed).
- [x] `npm run build` (passed with bundle-size/performance warnings).
- [x] `git diff --check` (passed).


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Ready for Review

### Files Changed

- `includes/Api/AiResponseDelayResponseValidator.php`, `includes/Rest/AiResponseDelayController.php`, `includes/Api/ModaApiClient.php`, `includes/Runtime.php`, and `composer.json`.
- `src/ai-response-delay-client.js`, `src/ai-response-delay-controller.js`, `src/recovery-settings/ai-response-delay-panel.js`, recovery settings/page controller state and rendering integration.
- Focused PHP/JS tests and PHP test bootstrap changes.
- Gettext POT plus all 19 locale PO files.

### Work Completed

Implemented the protected WordPress REST proxy and strict Shared v1 response/request validation, including capability and nonce checks, current installation/SiteIdentity checks before and after server-to-server requests, no-store responses, bounded status/error mapping, revision conflict handling, and safe install rotation behavior. Added the separate WooCommerce Admin delay setting with integer 0–30 input, translated strings, immediate-human-reply guidance, pending/conflict handling, and canonical read-after-save. Existing recovery settings and human dispatch/admission paths remain unchanged. Added focused PHP/JS coverage for authorization, identity/installation changes, validation bounds/types, revision conflict/no-op, provider failure, and the human bypass copy.

### Validation Results

Passed: focused PHP controller tests (5 tests, 43 assertions); full JS unit suite (62 files, 473 tests); `npm run i18n:verify:20` (568 source messages, 19/19 locales, 38 generated assets); `npm run build` (three bundle-size/performance warnings); changed-file JS lint; PHP syntax checks for every changed PHP file; and `git diff --check`.

`npm run test:php` ran 304 tests / 2,338 assertions but ended with 2 errors and 4 failures in checkout-consent/Plugin tests: `CheckoutConsentCheckboxTest::test_classic_uses_only_native_checkbox_without_a_withdrawal_button` (null result to `assertCount`), `CheckoutConsentCheckboxTest::test_blocks_registers_native_field_at_woocommerce_init_on_checkout` (null not callable), `CheckoutConsentCaptureTest::test_native_checkout_field_changes_cannot_create_consent_hooks` (unexpected `woocommerce_store_api_checkout_update_draft` hook), `CheckoutConsentPresentationTest::test_request_scoped_local_decision_is_shared_without_blocking_checkout` (expected true, got false), `PluginTest::test_native_navigation_checks_merchant_capability_and_only_loads_app_assets` (expected 7, got 0), and `PluginTest::test_assets_load_only_on_the_woocommerce_admin_screen` (expected script enqueue). Re-running the suite after restoring test globals did not change these failures. They are outside this task; no pre-task comparison was available, so this report does not claim a verified baseline.

Full `npm run lint:js` reported 480 errors in untouched files; none of the changed task JS files appeared in the full-lint diagnostics, and targeted changed-file lint passed. `npm run lint:php` could not complete because the Composer script references missing `tests/integration/checkout-consent-saved-block-variant.php`; direct `php -l` passed for the changed PHP files. The WooCommerce bootstrap currently reports that Docker is installed but its daemon is unavailable in this shell. No PostgreSQL/container integration is specified by this task.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

Repository-wide PHP test and lint failures described above remain unresolved and outside this task's scope. The full PHP suite's failure pattern appeared unrelated to these changes, but without a recorded pre-task comparison it is not asserted as pre-existing. No task-owned behavior remains unimplemented.

### Worktree and Git Evidence

Prepared launcher evidence for Attempt 1: canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-WOOCOMMERCE-001`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-WOOCOMMERCE-001`, mirrored branch `task/ARCH-054-WOOCOMMERCE-001`. Parent start SHA `d260d8323a85ae46df3b3bf19b7d01e541698167`; implementation start SHA `83b5c1390598ddc132d2b5119665679e883e454c`. Launcher synchronized both task branches (no fast-forward was needed), confirmed current `origin/main` was incorporated, and initialized recursive submodules at their recorded pins; submodule status was ready with none requiring updates. Durable parent claim commit: `30a8acafd9e22d24f062ba814a98edb0ec493569`. Implementation commit `0b57453` is pushed to the implementation task branch.


## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
