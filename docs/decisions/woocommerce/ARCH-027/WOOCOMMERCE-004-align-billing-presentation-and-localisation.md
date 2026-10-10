---
id: ARCH-027-WOOCOMMERCE-004
architecture_id: ARCH-027
title: Align Woo Billing presentation, module boundaries and locale formatting with Shopify
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 78
executor: copilot
claimed_at: 2026-10-10T11:38:02Z
attempt: 1
depends_on:
  - ARCH-027-WOOCOMMERCE-001
enables:
  - ARCH-027-WOOCOMMERCE-002
created: 2026-10-10
updated: 2026-10-10
---

# Align Woo Billing presentation, module boundaries and locale formatting with Shopify

## Architecture

Architecture ID: `ARCH-027`

Architecture document: `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator: `moda_architect`

## Objective

Make the **existing accepted Woo Billing hub** present the same Moda merchant visual experience as the Shopify Billing hub, using **focused, reusable components** and the WordPress administrator's UI locale, without changing subscription/entitlement logic or adding top-up/history functionality.

This is the presentation foundation for WOOCOMMERCE-002 and WOOCOMMERCE-003, not a reopening of accepted WOOCOMMERCE-001 billing business behaviour.

## Context

WOOCOMMERCE-001 is Complete. It provides the native Woo Billing page and the accepted PHP -> hosted API read/command boundary, plan/capacity read, recurring create/switch/cancel, Woo confirmation navigation, return refresh and connection/stale-response safety.

The 10 October source now uses:

```text
includes/Admin/NativeNavigation.php            WordPress Billing submenu
src/page/connected-workspace.js                  connected screen composition
src/page/use-moda-page-state.js                  page/controller orchestration
src/billing-screen.js                            current combined billing presentation
src/billing-controller.js                        accepted command/read orchestration
src/billing-client.js                            browser -> local WP REST client
src/styles/_tokens.scss                          scoped Moda design variables
src/styles/_billing.scss                         existing basic billing styling
```

`_billing.scss` explicitly records that **full billing visual parity is a separate pass**. `billing-screen.js` contains substantial combined hero, card, plan and dialog presentation. Do not add top-ups/history into that large component before establishing modular presentation boundaries.

Shopify's actual billing reference is:

```text
moda-interact/app/components/dashboard/BillingPurchaseHub.jsx
moda-interact/app/components/dashboard/BillingPurchaseHub.css
moda-interact/app/components/dashboard/TopUpPurchasePanel.jsx
moda-interact/app/routes/app/billing/recovery-credit-purchases/route.tsx
```

Use these for Moda *visual/product* consistency. Do not copy Shopify's React Router, hosted pricing, checkout or local refund actions into Woo.

ARCH-026's WordPress native i18n pipeline is implemented in the supplied plugin: `@wordpress/i18n`, `moda-interact` gettext domain, English POT, 19 non-English PO files, strict `.mo`/JavaScript JSON compilation and production ZIP checks. The ARCH-026 localisation task documents still appear Pending in this snapshot; this task does **not** change or purport to accept their statuses.

## Scope

One bounded Woo plugin presentation-foundation change:

1. Align the **current** Billing heading/hero, plan summary, free/paid/purchased-capacity cards, plan catalogue cards, pending/cancellation/error notices, action hierarchy and layout with the Shopify Billing design language and existing Moda tokens.
2. Extract focused presentational modules under `src/billing/` (or accepted equivalent) for page/hero, summary/capacity, plan cards, notices/dialog and shared presentation formatters. Keep `src/billing-screen.js` as a thin stable facade if existing callers/tests use it.
3. Establish an explicit WordPress administrator UI locale source/fallback for billing quantity, money and date formatting; keep formatting independent of saved shop/store language and CommerceAgent conversation language. Preserve the current intended time-zone semantics unless an existing contract requires otherwise.
4. Add focused presentation/formatting tests, full gettext compilation/regression validation, and packaged-plugin checks for any new user-visible copy.

This task may modify only `moda-interact-woocommerce` implementation/tests needed for this foundation, plus its own Completion Report. No unrelated applications/services or schema.

## Out of Scope

- Modifying WOOCOMMERCE-001's accepted provider/entitlement/subscription state machine, PHP REST authorization, retry semantics or checkout return behaviour.
- Implementing any top-up purchase command, bundle Buy action or history/refund view (WOOCOMMERCE-002/003).
- New WordPress menu, page, router, package-level design system, global wp-admin styling or browser-persisted billing state.
- Copying Shopify's hosted plan-change APIs, Shopify pricing unit semantics, refund POST/batch/merchant reactivation controls.
- Altering saved store language, customer conversation/AI language detection or translation policy outside merchant UI presentation.
- Database/Shared/API/Gateway changes or a broad unrelated Recovery/Overview refactor.
- Editing any `docs/decisions/**/_index.md` or `docs/architecture/_index.md` before architect/user session finalisation.

## Requirements

### R1 — Preserve current runtime and native navigation

Billing remains the existing `moda-interact-billing` native WordPress submenu and `BILLING` screen in `ConnectedWorkspace`. The current `src/page/use-moda-page-state.js`, `billing-controller.js`, `billing-client.js`, `includes/Rest/BillingController.php` and `ModaApiClient.php` retain their accepted request/command boundaries. No browser-to-hosted-API call, second React app, new routing system or duplicate state manager.

The accepted Billing summary/plan selection/cancellation flow must remain functional. Existing callbacks and billing-controller exports should remain stable where feasible; adjust focused tests for legitimate presentation-only extraction rather than changing workflow semantics.

### R2 — Shopify-aligned Moda visual foundation

For corresponding features in the accepted Woo Billing read model, match the Shopify `BillingPurchaseHub` visual hierarchy:

- clear heading/hero with plan status and primary/secondary plan actions;
- distinguishable current-plan summary and free/paid/purchased capacity blocks;
- consistent plan cards/featured/current state, pricing/allowance typography, badges and explanatory copy;
- pending plan, scheduled cancellation, FROZEN and attention notices that are clear without colour alone;
- accessible loading, unavailable, empty, error and action-in-progress states;
- mobile single-column stacking, long-label wrapping, clear CTA hit areas and WordPress-admin responsive constraints.

Use the scoped variables from `src/styles/_tokens.scss` and `.moda-interact-page` style boundary. Do not transplant Shopify CSS globally or attempt pixel-identical WordPress chrome. The same product concepts should feel consistent; Woo provider/payment-specific copy and behaviour remain Woo-owned.

### R3 — Focused presentation modules, not monolithic growth

Extract current UI-only responsibilities out of `src/billing-screen.js` into small cohesive components and formatting utilities under `src/billing/` (or equivalent). Separate UI rendering, state orchestration, API transport and formatting. Retain existing `billing-controller.js` responsibilities without broad rewriting; do not duplicate controller logic inside components.

Create reusable presentation primitives that WOOCOMMERCE-002 top-up cards and WOOCOMMERCE-003 purchase-history cards can consume without retrofitting the accepted Billing page again. Avoid another 300+ line catch-all component.

### R4 — Administrator UI locale determines presentation

Use the WordPress administrator's selected interface locale as the primary locale for `Intl` number/currency/date formatting (normalize e.g. `de_DE` to `de-DE`), with established site locale then safe English fallback. Do not use `Intl.NumberFormat(undefined)` / `Intl.DateTimeFormat(undefined)` when WordPress provides a valid UI locale, or equate persisted Shop/store locale with admin display locale. Preserve API-provided minor currency amounts, currency codes and date/time semantics; formatting is display-only.

WordPress text strings remain selected by its normal `@wordpress/i18n` loaded catalogue. If server-to-browser locale metadata is required, use the existing authenticated/admin bootstrap (no secrets; do not create a new endpoint merely for locale).

### R5 — Complete 20-language gettext and release assets

Use static, extractable `@wordpress/i18n` calls with text domain `moda-interact`. For **every** added/modified merchant-visible text or accessibility string, regenerate/verify `languages/moda-interact.pot`, provide reviewed entries in all **19 non-English** PO catalogues (including distinct Portuguese variants), preserve `sprintf` placeholders and contexts, and update hardcoded source-count assertions. A `.pot` alone is not translated support.

`npm run i18n:verify:20` must compile the expected PHP `.mo` and JavaScript translation JSON assets. `npm run plugin-zip` must include them. Do not commit unrelated generated build artifacts unless required by the repository's approved packaging contract.

### R6 — Accessibility and presentation safety

Provide semantic sections/headings, readable focus indication, text-backed statuses, keyboard-operable plan actions and accessible cancellation dialog with focus restoration/Escape behaviour preserved. Confirm no primary CTA loses its disabled/single-flight state, no React secret/id/provider internal data appears, and long translated strings are usable at narrower viewport widths.

## Work Items

- [x] Compare actual Shopify Billing Hub source and Woo Billing display states; record relevant visual parity behaviours without copying provider-specific actions.
- [x] Split `billing-screen.js` presentation into cohesive Billing hero/summary/capacity/plan/notice/dialog/formatter modules; preserve existing facade/controller contracts.
- [x] Apply scoped Moda design tokens and responsive layout to accepted Billing states.
- [x] Pass explicit normalized administrator UI locale to quantity/currency/date display helpers; verify browser/store mismatch scenarios.
- [x] Preserve recurring create/switch/cancel, pending/frozen, confirmation and return-refresh behaviour.
- [x] Extract/update all added gettext copy and translate it in each of the 19 PO catalogues.
- [x] Add focused UI/accessibility/locale/long-text tests and plugin packaging verification.

## Interfaces / Contracts

Consumes the already accepted WOOCOMMERCE-001 state/actions (`src/billing-controller.js`, `src/page/connected-workspace.js`) and the API-002 billing/plans projections through existing local WordPress REST. This task does not introduce any new remote request, billing payload, API schema, Woo vendor credential or shared contract.

Presentation locale: WordPress administrator UI locale, site locale fallback, normalized for standard `Intl` display. This is **UI-only** and must never overwrite durable Shop international context.

Design reference: Shopify `BillingPurchaseHub` and its design styles; implementation owner: `moda_woocommerce`.

## Dependencies

- `ARCH-027-WOOCOMMERCE-001` — architect-accepted Complete.

This task is Ready by the snapshot task state. It is **defined but not materialised** in the developer's canonical parent task branch until the supplied portable definition is materialised through `/moda-task` or the equivalent approved launcher.

## Enables

- `ARCH-027-WOOCOMMERCE-002` — becomes eligible only after this task has been accepted Complete and API-004/WOOCOMMERCE-001 remain Complete.

WOOCOMMERCE-003 remains downstream of WOOCOMMERCE-002 and API-006.

## Acceptance Criteria

- [x] Existing Billing current-plan/capacity, recurring create/switch/cancel, and Woo return refresh remain behaviourally equivalent to accepted WOOCOMMERCE-001.
- [x] Billing uses native WordPress menu/connected screen; no new menu/page/router/hosted-browser API call introduced.
- [ ] Shopify-equivalent hero/summary/capacity/plan cards and status/action treatments are visibly consistent using scoped tokens on desktop/mobile, with screenshots or reproducible review evidence. Developer browser/DOM smoke remains pending.
- [x] Presentation modules are focused and independently testable; no new monolithic controller/screen or duplicated state machine.
- [x] Admin selected `de_DE` with browser `en-US` (and saved store language differing) yields German-formatted amount/quantity/date presentation; missing/invalid admin locale follows documented site/safe fallback.
- [x] Time-zone semantics, API-supplied minor amounts and billing authority are unchanged by formatting refactor.
- [ ] Long translations fit cards and controls at narrow widths; keyboard focus, disabled buttons, live statuses and cancellation dialog are accessible. Developer browser/DOM smoke remains pending.
- [x] Every new merchant-visible string is extractable/translated in 19 PO files; POT/placeholder checks, 38 compiled translation assets and plugin ZIP verification pass.
- [x] No Woo vendor secrets, raw provider IDs, Shopify handles or browser-persisted billing data added.
- [x] No `_index.md` files or unrelated repo/API/database source modified.

## Validation

Check the current Woo repository scripts (`package.json` and Composer) before execution; run focused tests and the required packaging pipeline, including:

- [x] Focused Billing screen/controller/connected-workspace JS regression tests; Billing screen suite: 18 passed.
- [x] Administrator locale vs browser/store locale currency, quantity and date formatting tests.
- [ ] Desktop/mobile and long-translation visual/DOM smoke plus accessibility/keyboard/cancellation focus regressions; run the developer-owned package lifecycle command below.
- [x] `npm run test:i18n` (28 passed).
- [x] `npm run i18n:makepot` and `npm run i18n:verify:20` (169 source messages; 19/19 translation packs; 38 assets).
- [x] `npm run test:js` (23 files / 135 tests, plus 37 Node checks).
- [ ] `npm run test:php`: 69/70 passed; the unrelated `RecoverySummaryControllerTest::test_no_browser_shop_id_and_missing_installation` expects 401 but receives 200. `vendor/bin/phpunit --filter PluginTest` passed (13 tests, 65 assertions).
- [x] `npm run lint:js` (passes; existing legacy ESLint configuration warning), `npm run lint:css`, and `npm run lint:php`.
- [x] `npm run plugin-zip`: verified 101-entry archive, 20 locales, 38 assets; SHA-256 `e197e5ec9db4e72a2b7fb252216a719e89e35765e03cbe00f64f11f2126385`.
- [ ] Developer validation required: `npm run test:integration:package-lifecycle`. Expected result: fresh install and in-place upgrade pass at WordPress 7.1.2 / WooCommerce 11.1.2 / PHP 8.1, including packaged admin DOM/assets and locale browser smoke. No complete agent-side result is claimed.
- [x] `git diff --check`, narrow diff and no `_index.md` changes.
- [x] Dedicated parent and implementation task worktrees used; launcher-managed synchronization/submodule initialization completed before implementation; no shared workspace or implementation checkout was switched.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, update Completion Report, change status to `review`, return to `moda_architect`, and **STOP**. Do not start WOOCOMMERCE-002 or WOOCOMMERCE-003.

## Implementation Notes

Keep the component tree small and composable, with explicit dependencies and contracts. Change the rendering/layout and formatting boundaries only; avoid unnecessary refactor of accepted PHP/REST or billing state transitions. Shopify is the product design reference; WordPress is the runtime, localisation and navigation authority.

## Completion Report

### Status

Review

### Files Changed

- `includes/Admin/Setup.php`: bootstrap WordPress administrator/site locale metadata before the plugin script.
- `src/billing-screen.js`, `src/billing/`, and `src/styles/_billing.scss`: modular Billing presentation, formatting and responsive scoped styles.
- `tests/PluginTest.php`, `tests/bootstrap.php`, and `tests/js/billing-screen.test.js`: locale bootstrap and presentation regression coverage.
- `languages/moda-interact.pot`: regenerated source references; existing 19 translation packs compile without adding untranslated strings.

### Work Completed

- Compared the Shopify Billing hub presentation with accepted Woo states while retaining Woo navigation, REST/controller boundaries and billing commands.
- Extracted the Billing hero, summary/capacity, catalogue, notices, cancellation dialog and locale-aware formatters; kept `BillingScreen` as the facade.
- Added administrator locale primary selection with site-locale then English fallback, locale normalization, API minor-unit/currency preservation and UTC date semantics.
- Applied responsive, scoped Billing styles and retained notices in both Summary and Plans views. Added locale, plan, cancellation, capacity, hero and notice regression coverage.
- Regenerated the POT and verified all 19 non-English catalogues and 38 compiled assets. The production ZIP includes all 20 locales.
- Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-WOOCOMMERCE-004` on `task/ARCH-027-WOOCOMMERCE-004`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-WOOCOMMERCE-004` on `task/ARCH-027-WOOCOMMERCE-004`. No other task worktree or shared checkout was used for implementation.

### Validation Results

- Passed: `npm run test:js` (23 files / 135 tests and 37 Node checks); focused Billing screen suite (18 tests); `npm run test:i18n` (28 tests); `npm run i18n:makepot`; `npm run i18n:verify:20` (169 messages, 19 packs, 38 assets); JS/CSS/PHP linters; `vendor/bin/phpunit --filter PluginTest` (13 tests / 65 assertions); `npm run plugin-zip` (101 entries; SHA-256 above); `git diff --check`.
- Previously passed in this attempt: WordPress integration checks for WOO-014 locale, WOO-008 category, WOO-007 store context and WOO-003 REST/HTTPS. These were not rerun after the final presentation-only edits.
- Full PHP suite: 69/70 passed. The remaining unrelated Recovery Summary test expects 401 but receives 200; no baseline identifier was available in the task packet.
- Developer-owned validation pending: `npm run test:integration:package-lifecycle`. It includes packaged-browser DOM, asset and locale checks. An agent-side attempt was stopped under the validation policy; only task-owned fixture containers/directories were removed, and unrelated wp-env projects were left running.
- Launcher evidence: the prepared task launcher claimed Attempt 1 as `copilot`, synchronized the dedicated parent/implementation task worktrees and initialized implementation submodules before handoff. The implementation branch remains uncommitted; no implementation or parent report commit has been made yet.

### Deviations

- Long multi-container package-lifecycle validation is developer-owned by `docs/agent-validation-execution-policy.md`; it is reported as pending rather than passed. The full PHP suite also retains the unrelated Recovery Summary failure described above.

### Assumptions

- WOOCOMMERCE-001 is accepted Complete and its UI/controller contracts are working.
- The current 20-language pipeline and strict packaging checks in the uploaded Woo snapshot are the implementation baseline, without assuming ARCH-026 localisation task statuses have been accepted.

### Unresolved Issues

- Developer package-lifecycle/browser smoke is still required before final acceptance.
- Unrelated PHP failure: `RecoverySummaryControllerTest::test_no_browser_shop_id_and_missing_installation` expected 401, got 200.

### Architectural Concerns

None identified at definition time.

## Architect Review

### Review Status

Pending

### Review Notes

- **Attempt 1 architect inspection (2026-10-10): implementation provisionally conforms; acceptance withheld solely pending mandatory developer-owned package-lifecycle/real-browser evidence.** Keep task at `status: review`, preserve `attempt: 1`, and do not promote `ARCH-027-WOOCOMMERCE-002`. The validation policy explicitly permits returning long-running developer-validated tasks to `review` before those commands run; no new agent attempt is required merely to supply that evidence.
- Source inspection confirms focused `src/billing/` hero, summary/capacity, plan catalogue, notices, cancel-dialog and formatting modules, with `src/billing-screen.js` retained as the facade. The existing billing controller, browser-to-local-REST client, PHP billing routes and hosted API contracts are untouched. No new top-up or purchase-history commands were implemented.
- Presentation locale uses administrator `get_user_locale()` with site `get_locale()` fallback and safe English fallback, normalized for `Intl` display. UTC date semantics and API-provided minor currency amounts are preserved. `@wordpress/i18n` remains authoritative for translated UI strings; the reported 20-locale compile pipeline and inspected release assets agree in structure.
- The submitted package `moda-interact.zip` is a 101-entry archive rooted under `moda-interact/` with SHA-256 `e197e5ec9db4e72a2b7fb252216a719e89e35765e03cbe00f64f11f2126385`; it contains 19 `.mo` and 19 JavaScript JSON translation assets and no development-source tree. This independently matches the submitted SHA-256.
- The reported full PHP failure is `RecoverySummaryControllerTest::test_no_browser_shop_id_and_missing_installation` (expected 401, got 200). Its test and controller were not modified by this task; the test seeds a valid installation in its earlier `controller()` call and does not clear it before asserting the supposedly disconnected case. Treat this as a separately recorded test-fixture/baseline concern, not a Woo Billing presentation regression. Do not silently claim that the full PHP suite passed.
- Implementation commit `03e49ebff5cf96f636c6e4cb81226fd56767088f` and parent report commit `c8a46217b6c4d525b0882b21c5412b024579cfb2` were verified on their respective task branches. The Completion Report's historical sentence stating that these commits had not yet been made is stale; Git commit evidence takes precedence. Correct that narrative at the next authorised report update without manufacturing an implementation change.

### Reviewed Files

- `src/billing-screen.js`, `src/billing/{hero,summary,capacity-summary,plan-catalogue,notices,cancel-dialog,presentation-formatters}.js`, `src/styles/_billing.scss`.
- `includes/Admin/Setup.php`, `tests/PluginTest.php`, `tests/bootstrap.php`, `tests/js/billing-screen.test.js`, `languages/moda-interact.pot`, packaged translation assets, and `moda-interact.zip`.
- `docs/decisions/woocommerce/ARCH-027/WOOCOMMERCE-004-align-billing-presentation-and-localisation.md` and parent ARCH-027 architecture.
- Unchanged `tests/RecoverySummaryControllerTest.php` and `includes/Rest/RecoverySummaryController.php` for the unrelated failing test.

### Validation Reviewed

- Submitted: 135 JavaScript tests plus 37 Node checks, strict 20-language asset verification, 19 non-English catalogues and 38 compiled locale assets, CSS/JS/PHP lint, focused PHP PluginTest (13 tests), package ZIP audit and `git diff --check` passing. These are developer/agent reported results, not an independently rerun suite.
- Independently inspected the 101-entry production ZIP; its SHA-256 matches the task report, and its 19 `.mo` plus 19 JavaScript JSON assets are present. PHP source/tests and component/module boundaries were inspected. The review environment lacks the PHP extensions required to run PHPUnit, so PHP test results were not independently rerun.
- The full PHP suite remains non-green at 69/70; no passing or known-baseline test result is fabricated.
- **Outstanding before acceptance:** `npm run test:integration:package-lifecycle`, including packaged WordPress admin DOM/asset/browser/locale smoke, desktop/mobile layout, long translated strings, keyboard/dialog focus and fresh install/upgrade evidence. The task's visual/accessibility Acceptance Criteria and developer-owned Validation checkboxes correctly remain unchecked.

### Architecture Conformance

- Provisionally conforms to ARCH-027 Woo Billing presentation foundation and the WOOCOMMERCE-001 accepted business boundary. Presentation components are modular, tenant identity and credentials remain outside browser presentation, and no Shopify/API/database/Shared source changes were made.
- Cannot conclude visual, keyboard or package-lifecycle acceptance from static inspection and unit tests alone; developer browser/integration evidence is mandatory.

### Follow-up

- Developer: run `npm run test:integration:package-lifecycle` on the submitted Woo implementation revision; supply the actual command, exit code, fresh-install/upgrade result, and packaged-browser DOM/locale evidence, including narrow widths and a long translation. Include cancellation Escape/focus restoration and disabling/single-flight behaviour where the test harness can prove them.
- If validation passes without implementation changes, return its evidence to `moda_architect` for acceptance of **the same Attempt 1**; do not restart the agent solely for test orchestration. If it fails, record the failing assertion and request a bounded correction within the same task.
- Do not promote WOOCOMMERCE-002 or modify any `docs/decisions/**/_index.md` until the explicit acceptance/finalisation gates are satisfied.
