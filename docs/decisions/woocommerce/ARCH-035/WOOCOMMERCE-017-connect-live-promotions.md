---
id: ARCH-035-WOOCOMMERCE-017
architecture_id: ARCH-035
title: Connect existing WooCommerce Promotions screen to hosted promotional credits
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-035-API-021
  - ARCH-035-WOOCOMMERCE-005
enables:
  - ARCH-035-SYSTEM-TEST-006
created: 2026-10-22
updated: 2026-10-23
---
# ARCH-035-WOOCOMMERCE-017: Connect existing WooCommerce Promotions screen to hosted promotional credits

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- API owner: `ARCH-035-API-021`. Existing UI `ARCH-035-WOOCOMMERCE-005` remains Complete; do **not** redo the screen.

## Objective

Make the existing WooCommerce Promotions screen load real eligible offers/selection/history and submit guarded selections through the approved hosted API.

## Context

Production `src/promotions/promotions-screen.js` currently defaults to `{status:'UNAVAILABLE'}` and has no wired data provider. Shopify-style presentation has already been implemented and tested. This task owns the missing WordPress and React integration, not the promotion business rules.

## Scope

- Add a thin `moda-interact/v1/merchant/promotions` WordPress REST GET proxy and `/merchant/promotions/selection` PUT proxy (separate handlers or a focused controller), register via existing plugin bootstrap.
- Extend `includes/Api/ModaApiClient.php` with an **allowlisted**, installation-credential-based method for API-021 routes. Use the same source-of-truth installation and site-identity checks as existing merchant proxy controllers.
- Build a small client/controller/hook for the existing `src/promotions/` presentational components. Hydrate real `offers`, `offersPagination`, `selection`, `history` from API-021 and wire `onSelect`, `onOffersPage`, `onHistoryPage`.
- Update only necessary WordPress JS/PHP tests and 20-locale strings (if new strings are introduced).

## Out of Scope

- Campaign creation, credit minting, selecting coupon discounts, Woo checkout recovery offers, database schema changes, hosted API implementation, redesign of the already accepted screen, `_index.md` files.
- Live LocalWP/hosted-provider certification belongs to `ARCH-035-SYSTEM-TEST-006` and is **not** an acceptance gate for this implementation task.

## Requirements

1. Browser → same-origin WP REST using nonce and `manage_woocommerce`; WP server → hosted API with active installation credentials; no API key or shop ID from browser. Reject disconnected/revoked/identity-changed stores before and after API call, with no data leakage.
2. GET supports bounded `offerPage`, `historyPage`, optional **WP administrator display locale** and no arbitrary URL/Shop argument. PUT forwards only `{campaignId,expectedRevision}`; server and client both validate required shape; `Content-Type: application/json`. Derive `expectedRevision` only from last authoritative GET.
3. Use API-021 exact DTO; do not fabricate promotions, balances or success. Existing UI's `offer.id`, `selection.locked`, `offersPagination`, `history.entries` and callbacks are authoritative.
4. Provide loading, no offers, no history, explicit error, 401 reconnect, 403 denied, stale 409 refresh/reload and unavailable service states. One selection in flight; disable the action when already selected, locked or ineligible; retries cannot double-select. Reconcile the existing `PromotionHistory` presentation, which currently recognises only `ACTIVE`/`EXPIRED`/`EXHAUSTED`, with the authoritative Shopify lifecycle (`SELECTED`, `USED`, `EXHAUSTED`, `EXPIRED`, `CLOSED`, `NO_LONGER_ELIGIBLE`, `REOPENED`); a valid history status must not appear as “Unavailable” merely because the UI switch is incomplete.
5. Ignore/discard stale GET/PUT responses after disconnect, credential rotation, unmount or rapid pagination. On a successful PUT, refresh the server-owned selected promotion and history; do not treat UI optimism as a persisted grant.
6. Preserve existing Billing and Purchased Credit History navigation; do not confuse promotional credits with checkout discounts or Woo billing payments. Render dates and counts using WordPress locale without changing shop/conversation language.

## Work Items

- [x] Inspect the accepted UI and current plugin `ModaApiClient`/REST proxy security patterns.
- [x] Add server-side REST GET/PUT proxies, response validation and explicit status mapping.
- [x] Wire a modular live data client/controller into existing Promotions screen with guard/stale-request fencing.
- [x] Add permission, credential, conflict, pagination, selection and state tests.
- [x] Verify the 20-locale assets/build/ZIP and preserve the separate LocalWP checklist as a handoff to system testing (its execution is not required here).

## Interfaces / Contracts

- GET WP `moda-interact/v1/merchant/promotions` → hosted `GET /v1/merchant/promotions`.
- PUT WP `moda-interact/v1/merchant/promotions/selection` → hosted `PUT /v1/merchant/promotions/selection`.
- Request/response schemas and selection authority are owned by `ARCH-035-API-021`; Woo must validate/proxy them without redefining eligibility.

## Dependencies

- `ARCH-035-API-021` (must be architect-accepted Complete, including contract).
- `ARCH-035-WOOCOMMERCE-005` (existing completed presentation).

## Enables

- `ARCH-035-SYSTEM-TEST-006`.

## Acceptance Criteria

- [x] The existing Promotions screen consumes API-021 offer/selection/history DTOs and submits guarded revision-bound selections through the authenticated WordPress proxy, as verified by automated JS/PHP tests.
- [x] Automated code-level tests verify the installed proxy and client/controller safety contracts, including no fabricated selection success or exposure of another merchant's data. Live-merchant proof is deferred to `ARCH-035-SYSTEM-TEST-006`.
- [x] Existing Promotions presentation is reused; Shopify and Woo accounting semantics remain aligned.
- [x] All 20 admin locales remain valid; accessible selection states, native navigation and existing Billing remain intact in source and automated validation.

## Validation

- [x] Focused WP REST/PHP tests and JS controller/presentation tests, including stale/disconnect and selection double-click.
- [x] Repository-defined JS/PHP/i18n suites (`npm run test:js`, `npm run test:i18n`, `npm run i18n:verify:20`, `npm run test:php`) and build/plugin ZIP commands when provided by `package.json`.
- [x] `git diff --check`, canonical worktree isolation and Completion Report evidence.

Live LocalWP/hosted API end-to-end validation is owned by `ARCH-035-SYSTEM-TEST-006`; it is **not required** for this task to reach architect review or developer completion. Do not infer live behavior from mocked or unit-test results.

## Stop Condition

Submit `status: review` with evidence to `moda_architect` and STOP. Do not execute dependent certification.

## Implementation Notes

Separate PHP request forwarding from UI state; reuse established WP native authentication flow. Do not introduce service-local general logger or browser-held provider secret.

## Completion Report

### Status

Developer Self-Review Accepted — Attempt 2 passed the remaining focused and full PHPUnit gates on 2026-10-23. The implementation branch is published and clean at `efa842e2ebd7229070f9f4900c3216b45d33d860`; the parent report update is recorded on the parent task branch. All task acceptance criteria and required implementation validation are complete. Authenticated LocalWP certification remains assigned to `ARCH-035-SYSTEM-TEST-006` and is not claimed here. Because `completion_mode: developer`, explicit developer completion is pending.

### Files Changed

Implementation branch `task/ARCH-035-WOOCOMMERCE-017` contains 59 changed paths (3,256 insertions, 179 deletions) through `efa842e2ebd7229070f9f4900c3216b45d33d860`, published at the matching origin branch. Principal changes include `includes/Rest/PromotionsController.php`, `includes/Api/ModaApiClient.php`, `includes/Api/PromotionsResponseValidator.php`, the `src/promotions/` live client/controller/screen binding, focused PHP/JS tests, all 20 locale catalogues and `tests/manual/ARCH-035-WOOCOMMERCE-017-localwp.md`. At review, the canonical implementation worktree was clean and matched its remote task branch; the parent worktree contained only this task-record update before commit.

### Work Completed

- Added authenticated, same-origin WordPress GET/PUT routes with `manage_woocommerce` and REST nonce checks, strict request allowlists, active installation/site-identity checks before and after hosted calls, no-store responses and explicit upstream error mapping.
- Added strict API-021 response validation and installation-credential-based hosted requests. Browser requests contain no hosted credential, shop ID or upstream URL.
- Connected the existing Promotions presentation to paginated live DTO state, authoritative GET revision selection, single-flight selection, stale-request fencing, and post-selection server refresh. History rendering covers all seven API-021 lifecycle statuses.
- Added focused REST/DTO and JavaScript controller/presentation tests, updated translation catalogues, and provided an execution checklist for the authenticated LocalWP workflow. The checklist is not evidence that the workflow has run.

### Validation Results

- `npx wp-scripts test-unit-js tests/js/promotions-live.test.js tests/js/promotions-screen.test.js`: passed, 2 files / 31 tests.
- `npm run test:js`: passed, 56 test files / 436 unit tests, plus 52 Node integration/i18n tests.
- `npm run test:i18n`: passed, 28 tests.
- `npm run i18n:verify:20`: passed; 482 source messages and all 19 translation packs compiled in strict mode; production release manifest verified 20/20 locales and 38 assets.
- `npm run build`: passed. Webpack emitted bundle-size/performance warnings for the 267 KiB JS bundle and 407 KiB entrypoint.
- `npm run plugin-zip`: passed; production archive verified with 126 entries and SHA-256 `040a122974b04cfacb8fb48aeb9743476881a5ce1b4c62b519afd622443e0cd`.
- `php -l` passed for `includes/Api/ModaApiClient.php`, `includes/Api/PromotionsResponseValidator.php`, `includes/Rest/PromotionsController.php` and `tests/PromotionsControllerTest.php`.
- `npm run install:php`: passed from the canonical Woo implementation worktree; Composer installed from `composer.lock`, with no dependency changes required.
- `composer test -- --filter PromotionsControllerTest`: passed, 6 tests / 59 assertions.
- `npm run test:php`: passed, 154 tests / 1,177 assertions.
- `git diff --check origin/main...HEAD`: passed. Parent and implementation task branches are published; both canonical worktrees are clean. The implementation worktree is at the matching remote branch tip `efa842e2ebd7229070f9f4900c3216b45d33d860`.
- Authenticated LocalWP workflow: not run. This is now reserved for independent `ARCH-035-SYSTEM-TEST-006` certification, not this task's acceptance. No provider, connected-store or live installation evidence is claimed.

### Deviations

None.

### Assumptions

Canonical parent and implementation worktrees exist on `task/ARCH-035-WOOCOMMERCE-017`; the implementation branch is published through `efa842e2ebd7229070f9f4900c3216b45d33d860`. No provider credentials, deployment, authenticated merchant execution or live API acceptance is claimed.

### Unresolved Issues

None for this implementation task. Authenticated LocalWP/hosted-provider certification is intentionally deferred to `ARCH-035-SYSTEM-TEST-006`; no live behavior is claimed here.

### Architectural Concerns

None recorded at definition time.

### Developer Self-Review — Changes Requested (Attempt 1, 2026-10-23)

Historical review (preserved): The submitted implementation is materially present and published. Source review and the JavaScript, locale, build, package and PHP syntax checks passed. Review was not accepted because two task-required evidence gates remained unverified: PHPUnit could not run without `vendor/bin/phpunit`, and the required authenticated LocalWP workflow had not been executed. No live merchant/API behavior was inferred from fixtures or the checklist. Attempt remains 1, with no dependent certification performed.

### Scope Amendment — 2026-10-23

The developer is satisfied with the implemented Promotions behavior and explicitly removed authenticated LocalWP scenarios as a prerequisite for accepting `ARCH-035-WOOCOMMERCE-017`. Those end-to-end cases will be performed separately under `ARCH-035-SYSTEM-TEST-006`, which already depends on this task. The historical self-review above is retained for provenance, but its LocalWP evidence request is superseded. Focused and complete PHPUnit evidence remains required. No implementation source changes or attempt-number increment are authorised by this amendment.

### Developer Self-Review Accepted — Attempt 2 (2026-10-23)

The Attempt 1 PHPUnit gap is resolved. Composer development dependencies installed from the lock file, the focused Promotions controller tests passed (6 tests / 59 assertions), and the full PHP suite passed (154 tests / 1,177 assertions). Previously recorded JavaScript, i18n, production build, plugin ZIP and PHP syntax validations remain passing. All acceptance criteria are supported by the recorded automated and source-level evidence; live LocalWP certification remains out of scope and assigned to `ARCH-035-SYSTEM-TEST-006`. The implementation worktree is clean and the task branch is published. No material assigned-agent assistance or implementation source changes were made during Attempt 2; the attempt resolved validation and report evidence only. Explicit developer completion is pending.

## Architect Review

### Review Status

Developer Self-Review Accepted — Attempt 2; explicit developer completion is pending.

### Review Notes

Attempt 1 developer self-review and the subsequent scope amendment are preserved in the Completion Report. Attempt 2 developer self-review passed focused and full PHPUnit validation; explicit developer completion is pending. Live LocalWP certification is reserved for `ARCH-035-SYSTEM-TEST-006`.

### Reviewed Files

No implementation source files changed during Attempt 2. The implementation branch remains published at `efa842e2ebd7229070f9f4900c3216b45d33d860`.

### Validation Reviewed

`composer test -- --filter PromotionsControllerTest` (6 tests / 59 assertions); `npm run test:php` (154 tests / 1,177 assertions); `npm run test:i18n` (28 tests). The previously recorded JS suite, 20-locale verification, production build, plugin ZIP and PHP syntax checks also remain passing.

### Architecture Conformance

The existing implementation remains unchanged in Attempt 2. Recorded source review and automated validation support the task requirements; no live LocalWP or hosted-provider behavior is claimed.

### Follow-up

The developer may now invoke `/moda_developer_update ARCH-035-WOOCOMMERCE-017 complete`. Do not require the `ARCH-035-SYSTEM-TEST-006` end-to-end tests as a prerequisite of this task.

## Developer Takeover Amendment - 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-017` for this agent-owned task. The task is transferred to developer execution with developer-controlled completion while preserving the assigned agent `moda_woocommerce`, repository ownership, scope, dependencies, acceptance criteria and validation requirements. Attempt claim and implementation-worktree preparation remain delegated to the canonical launcher.
