---
id: ARCH-035-WOOCOMMERCE-017
architecture_id: ARCH-035
title: Connect existing WooCommerce Promotions screen to hosted promotional credits
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-021
  - ARCH-035-WOOCOMMERCE-005
enables:
  - ARCH-035-SYSTEM-TEST-006
created: 2026-10-22
updated: 2026-10-22
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

- [ ] Inspect the accepted UI and current plugin `ModaApiClient`/REST proxy security patterns.
- [ ] Add server-side REST GET/PUT proxies, response validation and explicit status mapping.
- [ ] Wire a modular live data client/controller into existing Promotions screen with guard/stale-request fencing.
- [ ] Add permission, credential, conflict, pagination, selection and state tests.
- [ ] Verify the 20-locale assets/build/ZIP and produce a reproducible manual LocalWP checklist.

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

Not Started — portable definition, not claimed or materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

No Git worktree, branch, implementation commit, provider credentials, deployment or acceptance is created by this task definition.

### Unresolved Issues

None recorded at definition time; report concrete schema/contract gaps to the architect rather than broadening scope.

### Architectural Concerns

None recorded at definition time.

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
