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
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 1
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
- [x] Verify the 20-locale assets/build/ZIP and produce a reproducible manual LocalWP checklist.

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

- [ ] A real connected Woo merchant can page live offers/history, inspect a real locked selection and select exactly one eligible campaign without duplicate credits.
- [ ] WordPress nonce/capability denial, disconnected/rotated installation, stale revision and hosted errors never show fabricated success or cross-shop records.
- [ ] Existing Promotions presentation is reused; Shopify and Woo accounting semantics remain aligned.
- [ ] All 20 admin locales remain valid; responsive and accessible UI, native navigation and existing Billing remain intact.

## Validation

- [ ] Focused WP REST/PHP tests and JS controller/presentation tests, including stale/disconnect and selection double-click.
- [ ] Repository-defined JS/PHP/i18n suites (`npm run test:js`, `npm run test:i18n`, `npm run i18n:verify:20`, `npm run test:php`) and build/plugin ZIP commands when provided by `package.json`.
- [ ] User/developer LocalWP live authenticated workflow evidence; no invented provider validation.
- [ ] `git diff --check`, canonical worktree isolation and Completion Report evidence.

## Stop Condition

Submit `status: review` with evidence to `moda_architect` and STOP. Do not execute dependent certification.

## Implementation Notes

Separate PHP request forwarding from UI state; reuse established WP native authentication flow. Do not introduce service-local general logger or browser-held provider secret.

## Completion Report

### Status

Changes Requested — Attempt 1 reviewed on 2026-10-23 and returned to `ready`. The implementation is published, and JS/i18n/build/package/PHP syntax checks passed, but PHP test execution and authenticated LocalWP evidence remain outstanding. Attempt remains 1; the next `/moda_developer_create` claim increments it.

### Files Changed

Implementation branch `task/ARCH-035-WOOCOMMERCE-017` contains 59 changed paths (3,256 insertions, 179 deletions) through `efa842e2ebd7229070f9f4900c3216b45d33d860`, published at the matching origin branch. Principal changes include `includes/Rest/PromotionsController.php`, `includes/Api/ModaApiClient.php`, `includes/Api/PromotionsResponseValidator.php`, the `src/promotions/` live client/controller/screen binding, focused PHP/JS tests, all 20 locale catalogues and `tests/manual/ARCH-035-WOOCOMMERCE-017-localwp.md`. Parent task worktree contains only this task record change. The implementation worktree retains the pre-existing untracked `typescript` artifact; it was not staged, changed or removed.

### Work Completed

- Added authenticated, same-origin WordPress GET/PUT routes with `manage_woocommerce` and REST nonce checks, strict request allowlists, active installation/site-identity checks before and after hosted calls, no-store responses and explicit upstream error mapping.
- Added strict API-021 response validation and installation-credential-based hosted requests. Browser requests contain no hosted credential, shop ID or upstream URL.
- Connected the existing Promotions presentation to paginated live DTO state, authoritative GET revision selection, single-flight selection, stale-request fencing, and post-selection server refresh. History rendering covers all seven API-021 lifecycle statuses.
- Added focused REST/DTO and JavaScript controller/presentation tests, updated translation catalogues, and provided an execution checklist for the authenticated LocalWP workflow. The checklist is not evidence that the workflow has run.

### Validation Results

- `npx wp-scripts test-unit-js tests/js/promotions-live.test.js tests/js/promotions-screen.test.js`: passed, 2 files / 31 tests.
- `npm run test:js`: passed, 56 test files / 436 unit tests, plus 52 Node integration/i18n tests.
- `npm run i18n:verify:20`: passed; 482 source messages and all 19 translation packs compiled in strict mode; production release manifest verified 20/20 locales and 38 assets.
- `npm run build`: passed. Webpack emitted bundle-size/performance warnings for the 267 KiB JS bundle and 407 KiB entrypoint.
- `npm run plugin-zip`: passed; production archive verified with 126 entries and SHA-256 `040a122974b04cfacb8fb48aeb9743476881a5ce1b4c62b519afd622443e0cd`.
- `php -l` passed for `includes/Api/ModaApiClient.php`, `includes/Api/PromotionsResponseValidator.php`, `includes/Rest/PromotionsController.php` and `tests/PromotionsControllerTest.php`.
- `git diff --check origin/main...HEAD`: passed. Parent and implementation task branches matched their published origins; implementation worktree had only the noted untracked `typescript` artifact.
- `composer test -- --filter PromotionsControllerTest`: blocked because `vendor/bin/phpunit` was absent. The declared PHP test suite was therefore not executed.
- Authenticated LocalWP workflow: not run. No provider, connected-store or live installation evidence is claimed.

### Deviations

None.

### Assumptions

Canonical parent and implementation worktrees exist on `task/ARCH-035-WOOCOMMERCE-017`; the implementation branch is published through `efa842e2ebd7229070f9f4900c3216b45d33d860`. No provider credentials, deployment, authenticated merchant execution or live API acceptance is claimed.

### Unresolved Issues

- Install the locked Composer development dependencies in the canonical implementation worktree (`npm run install:php` / `composer install --no-interaction`), then run the focused `PromotionsControllerTest` and the complete `npm run test:php` suite. Preserve and report any failures.
- Execute the authenticated LocalWP workflow in `tests/manual/ARCH-035-WOOCOMMERCE-017-localwp.md` against the deployed API-021 and an approved connected merchant. Record WordPress/WooCommerce/PHP versions, API revision, locale, redacted request/response statuses, one-PUT proof, navigation/accessibility checks and reconnect/permission/security outcomes. Do not include credentials or customer data.
- Update the remaining Acceptance Criteria and Validation checkboxes only from that executable evidence; then append a new Attempt 2 self-review with the resulting status.

### Architectural Concerns

None recorded at definition time.

## Architect Review
## Developer Self-Review - Changes Requested (Attempt 1, 2026-10-23)

The submitted implementation is materially present and published. Source review and the JavaScript, locale, build, package and PHP syntax checks passed. Review is not accepted because two task-required evidence gates remain unverified: PHPUnit could not run without `vendor/bin/phpunit`, and the required authenticated LocalWP workflow has not been executed. No live merchant/API behavior is inferred from fixtures or the checklist. Corrections are listed under **Unresolved Issues**. Attempt remains 1, with no dependent certification performed.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed. This is a new task definition, not an accepted implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed from implementation and test evidence.

### Follow-up

Architect acceptance required before enabling dependants.

## Developer Takeover Amendment - 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-017` for this agent-owned task. The task is transferred to developer execution with developer-controlled completion while preserving the assigned agent `moda_woocommerce`, repository ownership, scope, dependencies, acceptance criteria and validation requirements. Attempt claim and implementation-worktree preparation remain delegated to the canonical launcher.
