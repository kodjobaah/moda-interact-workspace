---
id: ARCH-036-WOOCOMMERCE-003
architecture_id: ARCH-036
title: Implement three offer modes and multi-coupon checkbox UI
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-036-API-002"]
enables: ["ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-15
---

# ARCH-036-WOOCOMMERCE-003 — Implement three offer modes and multi-coupon checkbox UI

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Enable the agreed three Recovery Offer modes using the existing Woo coupon catalogue, real multi-select checkboxes, and a manual Save action backed by API-002's existing discount selection flags.

## Context


ARCH-035-WOOCOMMERCE-011 already offers a preview-only native coupon picker. API-002 is the sole new hosted read/write endpoint for the merchant selection and offers; Background synchronises Woo coupon pages directly using the approved encrypted grant; no outbound coupon verification is part of ARCH-036. No new API coupon proxy/proof endpoint or Shared response schema is required; coupon eligibility, redemption, CommerceAgent and outbound recovery are explicitly out of scope.

## Scope

Modular React recovery offer cards, accessible checkbox list with bounded search/pagination, selected-state persistence across result pages, Save/Cancel/conflict feedback and privileged WordPress REST proxy to API-002. Preserve existing Store Category/Recovery Behaviour save and two-stage WordPress menus. Use all 20 locales.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

- Top-level NONE/FIXED/AI mutually exclusive **configuration** modes. FIXED exposes multiple **checkboxes** for ACTIVE/current/supported coupons; NONE and AI persist their chosen mode, without implying any CommerceAgent or recovery execution change.
- The checkbox checked state comes from `isAvailable` and is not a separate preview radio control. Search/filter/page changes preserve the draft set. Disabled/removed/expired coupons never appear as selectable; show a count/notice if previously selected choices became unavailable.
- Save only on click; changes remain unsaved until success. FIXED with zero checked rows is blocked with inline explanation. Submit the complete internal discount row ID set through API-002; follow API-002's accepted contract of a Shop-locked, atomic, revision-free last-writer-wins Save (the read revision is informational, not a PUT precondition). No fake Shopify GraphQL IDs or direct browser-to-hosted access.
- Retain state on 400/409/503, disable repeat submissions, and keep settings/configuration distinct from send-time proof. Preloading not ready => controls nonpersistent/unavailable, not a false saved offer.

## Work Items

- [x] Replace the preview-only choice with one interactive NONE/FIXED/AI mode selector and multiple coupon checkboxes within FIXED.
- [x] Read selected flags and the active catalogue through API-002 with server-side pagination; preserve the active search when moving between pages.
- [x] Persist the mode and complete checkbox set only on explicit Save through the privileged WordPress proxy; prevent duplicate submissions and preserve edits after tested failed Saves. Follow API-002's accepted revision-free transactional last-writer-wins contract; a read revision is not a CAS token.
- [x] Add client/controller tests for multi-page selection persistence, no automatic writes, duplicate-submit prevention, 409 draft retention and the pre-sync unavailable state.
- [x] Verify strict 20-locale source/catalogue/compiled-asset coverage.
- [ ] Add successful persistence coverage for NONE and AI, component/render coverage for the mode states, and 400/503 failed-Save draft-retention cases.
- [ ] Correct and test unavailable previously selected coupon counts when the catalogue spans multiple pages; verify stale/removed-row treatment against the API-002 contract.
- [ ] Verify both WordPress navigation stages and responsive behavior with manual LocalWP desktop/narrow-viewport interaction and screenshots.

## Interfaces / Contracts


Privileged WordPress REST proxy to API-002's API-owned GET/PUT merchant discount catalogue/offer endpoints; existing `ShopifyDiscount` IDs/selected `isAvailable` flags and `ShopSettings` mode. No new Shared npm schema or coupon-upload event.

## Dependencies

- `ARCH-036-API-002`

## Enables

- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Selected Woo coupon checkboxes reflect the saved selection projection (`isAvailable`) and survive reload/pagination.
- [ ] NONE/FIXED/AI settings persist exactly as requested; FIXED requires nonempty selected coupons, while unchecked ACTIVE coupons remain visible. No send-time or CommerceAgent promise is made.
- [x] Save is explicit, does not write automatically, blocks duplicate submissions, and retains the draft after a tested 409 response.
- [x] Existing native menu implementation was not changed, and strict verification/package audit cover all 20 supported locales.
- [ ] Complete LocalWP interaction evidence for the existing two-stage navigation and responsive UI.

## Validation

- [x] PHP WordPress proxy/unit validation: `npm run test:php` passed (104 tests, 637 assertions).
- [x] Focused client/controller tests: included in the passing JavaScript unit-test run (39 files, 226 tests).
- [ ] Component/render tests for mode-specific UI, zero selection and 400/409/503 error states.
- [ ] LocalWP manual UX evidence at desktop and narrow viewports, including both menu stages and catalogue CURRENT/ERROR states.
- [ ] Disposable WordPress integration: `npm run test:integration:wordpress` was started but returned no test verdict; its temporary containers were cleaned up.
- [ ] Mobile/desktop visual checks and screenshots.
- [x] Strict 20-locale translation verification: `npm run i18n:verify:20` passed (327 messages, 19/19 translation packs, 38 generated assets).
- [ ] JavaScript lint and complete JavaScript suite: `npm run lint:js` reported three lint errors; `npm run test:js` had 7 failing legacy locale-count assertions (324 expected, 327 extracted), although all 226 JS unit tests passed.
- [x] CSS lint and PHP lint: `npm run lint:css` and `npm run lint:php` passed.
- [x] Production build and plugin ZIP audit: `npm run build` passed with two bundle-size warnings; `npm run plugin-zip` passed with 113 entries, 20/20 languages and 38 compiled assets.
- [x] `git diff --check origin/main...HEAD` passed.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Do not put API calls in presentation components. Preserve the existing two-stage WordPress menus (the WooCommerce entry opens the Moda Interact top-level menu with its Recovery settings submenu); do not move the entry or create competing permanent menu positions. Keep the existing `WOOCOMMERCE-011` preview work as historical UI foundation.

For developer execution, use the canonical `/moda_developer_create ARCH-036-WOOCOMMERCE-003` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-WOOCOMMERCE-003`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

## ASCII Page Design

```text
WordPress Admin > WooCommerce > Moda Interact (entry)
  > Moda Interact > Recovery settings (active menu)
+-----------------------------------------------------------------------+
| RECOVERY OFFER                                                        |
|                                                                       |
| ( ) No discount   (x) Specific discount   ( ) AI-selected discount     |
|                                                                       |
| Specific discount — select one or more coupons                        |
| Search coupons [_______________________] [Search]                      |
|                                                                       |
| [x] SAVE10      10% off                ACTIVE                          |
| [ ] SAVE20      GBP 20 fixed cart      ACTIVE                          |
| [x] WELCOME5    GBP 5 fixed cart       ACTIVE                          |
|                                                                       |
| [Previous]             Page 1 of N                   [Next]             |
|                                                                       |
| 2 coupons selected                        [Save recovery behaviour]   |
+-----------------------------------------------------------------------+
| Only ACTIVE, supported, in-date coupons appear.                       |
| An expired/removed coupon is not selectable.                          |
+-----------------------------------------------------------------------+

At tablet width the offers wrap; on mobile the three mode cards,
search and each coupon checkbox row stack with full-width Save action.
Selecting the UI never changes a coupon until Save succeeds.
```

## Completion Report

### Status

Attempt 1 is partially implemented and reconciled below. Developer review returned Changes Requested; the task remains Ready at Attempt 1. No new attempt was claimed.

### Files Changed

- `src/recovery-settings/recovery-behaviour-fields.js`
- `src/recovery-settings/woo-coupons/merchant-offers-panel.js`
- `src/recovery-settings/woo-coupons/offer-client.js`
- `src/recovery-settings/woo-coupons/offer-controller.js`
- `tests/js/merchant-discount-offers.test.js`

### Work Completed

- Added the privileged WordPress offer/catalogue client and a controller for mode drafts, checkbox selection, search/pagination, manual Save/Discard, duplicate-submit prevention and failed-save draft retention for tested failures.
- Replaced the old read-only offer-choice preview with the interactive NONE/FIXED/AI mode selector and FIXED checkbox list. No source edits were made during this review.
- Reviewed implementation commit `a8daa4499158706cfdb8122f60ed83e753799fe0`, published on `origin/task/ARCH-036-WOOCOMMERCE-003`; implementation worktree was clean at review.

### Validation Results

- `npm run i18n:verify:20`: passed; 327 extracted messages, 19/19 translation packs and 38 generated assets.
- `npm run test:js`: failed overall. The 39 JavaScript unit-test files passed (226 tests). The integration/i18n phase had 30 passed and 7 failed because legacy locale tests still assert 324 messages while the current source/catalogues contain 327.
- `npm run test:php`: passed after installing locked Composer dependencies; 104 tests and 637 assertions.
- `npm run lint:js`: failed with three errors: missing JSDoc parameter types for `MerchantOffersPanel` and a nested ternary in `tests/js/merchant-discount-offers.test.js`.
- `npm run lint:css` and `npm run lint:php`: passed.
- `npm run build`: passed; webpack emitted two entrypoint-size/performance warnings.
- `npm run plugin-zip`: passed; production package audit reports 113 entries, 20/20 languages and 38 compiled assets (SHA-256 `f270b00a630b75d5abd02861b8220427deafbb0c5aaea415f797e6314aec2115`).
- `git diff --check origin/main...HEAD`: passed.
- Manual LocalWP desktop/narrow-viewport interaction and screenshot evidence was not produced. `npm run test:integration:wordpress` did not return a test verdict; its temporary containers were stopped and removed. Integration validation is incomplete and is not claimed as passed.

### Deviations

None.

### Assumptions

The canonical parent worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-036-WOOCOMMERCE-003`, branch `task/ARCH-036-WOOCOMMERCE-003`. The canonical implementation worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-WOOCOMMERCE-003`, same task branch. The parent branch was clean at `7cdb20b`; implementation HEAD was clean and published at `a8daa4499158706cfdb8122f60ed83e753799fe0`. Attempt 1 is preserved.

### Unresolved Issues

- JavaScript lint and the complete JavaScript suite do not pass; the stale locale assertions must be updated to follow the extracted source catalogue count.
- The explicit LocalWP manual UX evidence, including both menu stages, desktop/narrow viewports, and current/error catalogue states, is missing.
- The new panel's component-level state/rendering coverage and unavailable-selected-coupon count across a multi-page catalogue need focused verification; current changed tests primarily exercise the client/controller path.

### Architectural Concerns

Report schema, cross-service or provider-proof deviations to `moda_architect` instead of silently expanding scope.

## Architect Review

### Review Status

Not submitted to the architect. Developer self-review is Changes Requested; correction work is pending.

### Review Notes

Attempt 1 was reviewed against the published implementation and returned to Ready. This is not an architect acceptance or developer completion decision.

### Reviewed Files

Canonical implementation branch at `a8daa4499158706cfdb8122f60ed83e753799fe0`; changed files are listed in the Completion Report.

### Validation Reviewed

Developer review evidence is recorded in the Completion Report and Developer Self-Review. The review did not accept the attempt.

### Architecture Conformance

No scope expansion was identified. Save semantics follow API-002's accepted revision-free, Shop-locked, atomic last-writer-wins contract.

### Follow-up

Attempt 1 remains Ready for the corrections listed in the Developer Self-Review below. No merge to `main`, attempt increment, or downstream task update was made.

## Developer Self-Review - Changes Requested

### Reviewed Attempt

Attempt 1, developer execution. Review date: 2026-10-15. The implementation is not accepted for architect review yet.

### Required Corrections

1. Fix the three `lint:js` errors: provide typed JSDoc parameters for `MerchantOffersPanel` and remove the nested ternary in the changed offer tests. Rerun `npm run lint:js`.
2. Update legacy i18n tests that hard-code 324 messages so they validate the current extracted catalogue (327 messages) without weakening translation/placeholder checks. Rerun `npm run test:js` and keep `npm run i18n:verify:20` green.
3. Add focused component/render and controller coverage for successful NONE/FIXED/AI Saves, zero-selection validation, checkbox state, Discard and retained drafts for 400/409/503 responses. Ensure unavailable selected coupons are counted/noticed correctly across multi-page catalogues, and confirm stale-row behavior follows API-002's accepted contract.
4. Provide manual LocalWP evidence at desktop and narrow widths for both WordPress menu stages and catalogue CURRENT and ERROR states, including mode/checkbox/Save interactions. Record screenshots and outcomes in the task report.
5. Run `npm run test:integration:wordpress` to a definitive pass/fail result; investigate and resolve why the prior run returned no verdict, then record the result.
6. Rerun the required validation matrix after corrections, including PHP proxy tests, CSS/PHP lint, production build, plugin ZIP audit and `git diff --check`; record actual outcomes.

### State Transition

`status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. No Attempt 2 was created by this review.
