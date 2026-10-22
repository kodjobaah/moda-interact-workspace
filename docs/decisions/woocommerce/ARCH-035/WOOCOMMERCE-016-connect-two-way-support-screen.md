---
id: ARCH-035-WOOCOMMERCE-016
architecture_id: ARCH-035
title: Connect native Woo Support screen to hosted two-way Support
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 32
executor: developer
claimed_at: 2026-10-22T08:47:30Z
attempt: 2
depends_on:
  - ARCH-035-API-020
enables:
  - ARCH-035-SYSTEM-TEST-005
  - ARCH-046-WOOCOMMERCE-007
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-21
updated: 2026-10-22
---

# ARCH-035-WOOCOMMERCE-016: Connect native Woo Support screen to hosted two-way Support

## Architecture

Architecture ID: `ARCH-035`. Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`. Coordinator: `moda_architect`.

**Lifecycle:** Architect definition was materialised on the canonical parent task branch after dependency `ARCH-035-API-020` became Complete. The developer explicitly requested takeover from the default agent execution mode; the canonical launcher will prepare/synchronize both worktrees and claim the first developer attempt.

## Objective

Enable the already-implemented WooCommerce merchant Support thread and composer against the approved two-way hosted Support API, using a privileged WordPress REST proxy.

## Context

`ARCH-035-WOOCOMMERCE-001` is Complete as a UI task, but `src/support/support-client.js` still reports all three capabilities unavailable. `ARCH-035-API-020` provides the missing authoritative read, compose and mark-read operations. ARCH-046 SYSTEM notices must appear in that same conversation, not a separate view.

## Scope

- Extend the existing Woo PHP ModaApiClient and privileged WP REST controller with three operations corresponding to API-020.
- Replace the unavailable-only Support client with real list/send/markRead methods and connect it to the existing controller/UI.
- Preserve existing native WordPress Support navigation, translations, thread/component separation and Shopify-parity styling.
- Add focused PHP proxy/authentication and JS async controller/network tests, plus 20-locale build verification.

## Out of Scope

- No new WordPress Support data store, new top-level menu, hosted API changes, schemas or background translation processing.
- Do not implement customer WhatsApp messaging, Shopify refunds, platform-admin responses or ARCH-046 merchant no-contact action (owned by WOOCOMMERCE-007).

## Requirements

- Every WordPress browser request requires capability `manage_woocommerce` or the current narrower approved merchant-admin capability plus a verified REST nonce. PHP obtains current authenticated installation credentials server-side and calls hosted API over HTTPS; never expose credentials in JS, browser HTML or logs.
- Render paginated `MERCHANT`, `ADMINISTRATIVE` and `SYSTEM` records, original/translated switch, accurate read/unread badges, and actionable only validated provider-safe system links.
- Use stable UUID actionId per attempted send and reuse on safe retries; persist the actionId only for pending client retry, not as authoritative message storage. Double-click prevention and only confirm send upon authenticated hosted ACK.
- Disable send/read/markRead on disconnected, revoked, stale or denied installation; abort or ignore in-flight operations after disconnect/reconnect, credential rotation and unmount. Provide clear permission/error/unavailable states.
- Keep 20 administrator UI locales with WordPress admin preference and site fallback; language of customer conversations and Shop default remain unchanged.
- No locally fabricated data or success, and no direct call to Shopify app routes.

## Work Items

- [x] Inspect existing `src/support` controller and WP REST/API client code; map API-020 response/error contracts.
- [x] Wire privileged PHP proxy and strict plugin-side transport validation.
- [x] Enable real read, send and markRead in separate `support-client`/controller modules; retain fixture-only test seams.
- [x] Test disconnected, stale response, nonce denial, invalid body, duplicate send, translated reply and SYSTEM notice read path.
- [x] Run WordPress PHP/JS and 20-language tooling, build and ZIP.

## Interfaces / Contracts

- Consumes API-owned three-route Support v1 contract of `ARCH-035-API-020`; hosted API derives tenant from Woo installation.
- Browser → nonce/capability-checked WordPress REST → authenticated PHP ModaApiClient → hosted API → existing PostgreSQL Support thread.

## Dependencies

- `ARCH-035-API-020` (must be architect-accepted Complete)

## Enables

- `ARCH-035-SYSTEM-TEST-005`
- `ARCH-046-WOOCOMMERCE-007`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] Connected merchant can read paginated Support history, send a message and see subsequent Moda admin reply in the same thread.
- [x] System/ARCH-046 consent notices appear among ordinary Support messages; existing translated/original and read/unread flows operate.
- [x] Non-admin, bad nonce, another tenant, stale installation and malformed API responses fail closed without presenting fake success.
- [x] No duplicate sends on double-click/network retry; all 20 locale assets pass strict verification.
- [x] Existing Woo onboarding, Billing, Recoveries and Shopify Support unaffected.
- [x] Developer-approved Woo Support visual experience: merchant chat bubbles align right, Moda Support replies align left, and the conversation/composer presentation follows the accepted Shopify reference. Verified on LocalWP on 2026-10-22.

## Validation

- [x] Run focused JS Support client/controller/UI and PHPUnit REST nonce/capability/credential tests, plus negative disconnect/reconnect tests.
- [x] Run project-declared `npm run test:js`, `npm run test:i18n`, `npm run i18n:verify:20`, `npm run test:php`, `npm run build`, `npm run plugin-zip` and `git diff --check` as available.
- [x] Record developer-performed LocalWP deployment, connected two-way Support verification and visual approval separately from automated test results (2026-10-22); see the manual acceptance record in Implementation Notes.

## Stop Condition

After all required Work Items, Acceptance Criteria and task-specific Validation are satisfied, update the task Completion Report and `status: review`, return to `moda_architect` and STOP. Do not perform dependent tasks, create new task implementation worktrees, merge or push main, or change `docs/decisions/**/_index.md`.

## Implementation Notes

Retain current Support component boundaries; do not enlarge a catch-all page module. ARCH-046-WOOCOMMERCE-007 may add an independent merchant no-contact action later; it must not be bundled into the Support messaging implementation.

### Developer LocalWP verification and visual acceptance — 2026-10-22

The developer reports that the updated WooCommerce plugin was packaged with `npm run plugin-zip` and deployed to a LocalWP installation. In that environment, the developer verified the connected two-way Support experience: a merchant message ("can i get some help") and the Moda Support response ("sure you can") were displayed in the same thread. The developer compared the final WooCommerce screen with the Shopify Support reference, including right-aligned merchant bubbles, left-aligned administrative replies and the composer, and **explicitly approved the look and feel**. The developer supplied screenshots during the 2026-10-22 acceptance conversation; this task records the outcome rather than claiming those screenshots are committed to the repository.

**Reviewer instruction:** The LocalWP deployment, manual connected-thread demonstration and visual acceptance have already been performed by the developer. **Do not require the reviewer to install, package, deploy or run the plugin in LocalWP, or repeat a visual UI walkthrough**, to approve the already accepted appearance. Review the source diff, task boundaries, security/authentication/tenant handling, automated test results and remaining acceptance criteria using the available implementation and validation evidence. This manual sign-off does **not** establish coverage for unshown scenarios such as paginated multi-page history, SYSTEM/ARCH-046 notices, translation switching or negative permission cases; assess those from their required tests/evidence. Do not mark the entire task Complete solely because its UI is approved.

Start with `scripts/start-agent-task.py --prepare` through the normal `/moda-task` path. The prepared packet proves canonical parent/implementation worktree identity, synchronization and submodule state; record that packet in the Completion Report. Re-read the latest task and architect review before claiming. Use actual repository scripts. The architect in this externally supplied ZIP session has not created any Git branches or worktrees.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-22T08:47:30Z. Attempt 1 review history is preserved below.

### Files Changed

Implementation commit `8b537dc79697ef9b301c5b94b7c26fb3c08a08b2` changes these 19 WooCommerce plugin files:

- `composer.json`
- `includes/Api/ModaApiClient.php`
- `includes/Api/SupportResponseValidator.php`
- `includes/Rest/SupportController.php`
- `includes/Runtime.php`
- `src/support/styles/_support.scss`
- `src/support/support-action-id.js`
- `src/support/support-client.js`
- `src/support/support-composer.js`
- `src/support/support-contract.js`
- `src/support/support-controller.js`
- `src/support/support-message-card.js`
- `src/support/support-screen.js`
- `src/support/support-thread.js`
- `src/support/support-validation.js`
- `tests/SupportControllerTest.php`
- `tests/js/support-client.test.js`
- `tests/js/support-controller.test.js`
- `tests/js/support-screen.test.js`

No parent workspace, API, Shared, Database or other implementation repository files were changed by this attempt.

### Work Completed

Implemented the authenticated WordPress REST proxy for Support history, compose and mark-read; strict hosted-response and browser-request validation; server-side installation credential use with post-request site/credential revalidation; connected the production Support client/controller and UI; added paginated thread, translation/original display, SYSTEM notice, unread/read, retry/idempotency and disconnected/stale-response handling. The developer separately verified the connected two-way conversation on LocalWP and explicitly approved the visual presentation; this remains manual evidence and is not being substituted for automated validation.

### Validation Results

- Focused Support JavaScript tests: **PASS**, 3 files / 22 tests (`wp-scripts test-unit-js tests/js/support-client.test.js tests/js/support-controller.test.js tests/js/support-screen.test.js`).
- Full `npm run test:js`: **PASS**, 54 files / 372 unit tests and 52 Node integration/i18n tests.
- Focused `composer test -- tests/SupportControllerTest.php`: **PASS**, 7 tests / 61 assertions.
- Full `composer test`: **PASS**, 137 tests / 985 assertions.
- `composer lint`: **PASS**, no PHP syntax errors, including Support controller, response validator and tests.
- `npm run test:i18n`: **PASS**, 28 tests. `npm run i18n:verify:20`: **PASS**, 463 source messages, 19/19 translation packs and 38 strict generated locale assets (English plus 19 translations).
- `npm run build`: **PASS**; webpack emitted the existing asset/entrypoint size recommendations (251 KiB JS bundle; 391 KiB entrypoint).
- `npm run plugin-zip`: **PASS**; production build and strict locale validation passed, and `unzip -t moda-interact.zip` reported no compressed-data errors.
- `git diff --check origin/main...HEAD`: **PASS**, no whitespace errors.
- Composer development dependencies were restored from the lockfile to run PHPUnit. The production packaging script subsequently removed those dev-only packages as designed; no tracked dependency manifest/lockfile changes resulted.
- Canonical parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-016` is on `task/ARCH-035-WOOCOMMERCE-016`, clean and synchronized with `origin/task/ARCH-035-WOOCOMMERCE-016` at parent commit `74a91094c` before this review update. Canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-016` is clean; implementation commit `8b537dc79697ef9b301c5b94b7c26fb3c08a08b2` is published and local/remote task refs match (`0 0`).
- Dependency check: canonical resolver reports `ARCH-035-API-020` Complete, but its task file still says `## Architect Review / Review Status: Pending — no implementation reviewed.` This does not satisfy this task's explicit dependency contract, “must be architect-accepted Complete.”

### Deviations

None.

### Assumptions

Inspect current canonical developer workspace when materialising; this source ZIP may lag task branches.

### Unresolved Issues

Dependency review gate unresolved: obtain an authorized architect acceptance for API-020, or an explicit architecture amendment to WOOCOMMERCE-016's dependency contract. Do not treat developer completion alone as architect acceptance. No source-level issue was identified in the reviewed Woo Support implementation.

### Architectural Concerns

No implementation-scope concern identified. The implementation confines hosted credentials to PHP and enforces WordPress capability/nonce checks, strict DTOs, tenant identity via the installation record, credential/site revalidation, bounded requests, no-store responses, safe error mapping, stable action IDs and stale async response suppression.

## Developer Self-Review - Changes Requested (Attempt 1)

The Woo Support implementation and required automated checks pass, and the developer's LocalWP connected-thread/visual acceptance is recorded above. Do not accept or proceed to a new attempt until the explicit dependency condition is resolved: `ARCH-035-WOOCOMMERCE-016` requires `ARCH-035-API-020` to be **architect-accepted Complete**, but the canonical API-020 task still has Architect Review status Pending. Request `moda_architect` review/acceptance of API-020, or obtain an explicit architecture amendment changing this dependency. Once resolved, re-evaluate eligibility and continue without discarding the published Attempt 1 implementation. No changes are requested to the API or Woo implementation based on this review. Attempt remains 1; executor and claimed_at are null; status is `ready` per the developer Changes Requested transition.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

Definition approved for handoff; no implementation has been accepted.

## Developer Takeover Amendment — 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-016` for this ready agent-owned task. Execution and completion ownership are transferred to the developer (`execution_mode: developer`, `completion_mode: developer`); logical ownership remains `assigned_agent: moda_woocommerce`, and task scope, dependency, acceptance criteria, and validation requirements are unchanged. The canonical launcher will record the developer claim after worktree preparation and dependency verification.
