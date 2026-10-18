---
id: ARCH-035-WOOCOMMERCE-006
architecture_id: ARCH-035
title: Add Shopify-parity Woo Usage History UI
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-035-WOOCOMMERCE-012
enables:
  - ARCH-035-WOOCOMMERCE-010
  - ARCH-035-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-035-WOOCOMMERCE-006: Add Shopify-parity Woo Usage History UI

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: `moda-interact-workspace(20261011-192347).zip`; portable definition, not a materialised parent/implementation task branch.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-006` for this ready task. Execution and completion ownership are taken over from the assigned agent and set to `developer`/`developer`; logical ownership remains `assigned_agent: moda_woocommerce`. Scope, dependencies, acceptance criteria and validation requirements are unchanged. The canonical launcher will claim Attempt 1 after worktree synchronization and dependency verification.

## Objective

Build the Usage History merchant screen with period selection, event filters and paginated history presentation.

## Context

Shopify app/components/dashboard/UsageEvents.tsx uses Current/Past tabs, billing-period selection, filter controls, event table and cursor paging. Woo Billing and Purchase History exist, but no equivalent merchant Usage History surface.

Source references:
- Shopify: app/components/dashboard/UsageEvents.tsx; app/routes/app/usage/route.jsx.
- Woo: src/billing/purchase-history-screen.js; src/billing/connected-billing-screen.js.

## Scope

- Provide Usage History link from the existing appropriate merchant navigation without disturbing Billing Purchase History.
- Implement Current/Past views, period chooser, kind filtering, event table, cursor paging and loading/empty/invalid-cursor/error states.
- Use existing billing/usage read responses where available; missing history endpoint yields unavailable state, not synthetic usage activity.
- Apply locale-aware date/number/currency formatting and provider-correct cadence labels, with no fabricated monetary values.

## Out of Scope

- New Moda-hosted API routes, data migrations, shared contracts, Background workflow, Woo checkout/order event publishing and provider coupon integration.
- Artificial production records, local mock-success modes, or storage of authoritative merchant data in browser state.
- Shopify UI code copy/paste that imports Shopify authentication or Polaris-only server routes.
- Any `docs/decisions/**/_index.md` changes before explicit final reconciliation.

## Requirements

- Use WordPress Admin as the shell, React via @wordpress/element for content, native gettext/i18n, and existing Woo installation, nonce, capability and disconnect protections.
- Source alignment, accessibility, section placement and state meanings must follow the Shopify reference files named here; only platform chrome/provider-specific actions may differ.
- UI composition and state/transport must be modular; do not enlarge src/page.js or create new catch-all files (target <=200 lines, maximum 300 new production lines per file).
- The assigned task is **UI-only**: no DB schema/migrations, Shared contracts, hosted API implementation, background jobs, event ingestion, order reconciliation, coupon-provenance, payment-provider commands or business-rule changes.
- Do not invent new endpoints or use Shopify authentication from WordPress. The browser may use only an already-approved privileged WordPress API proxy; server-side Woo integration must remain within existing accepted contracts.
- A missing external dependency must not be silently faked. Fixture data are for tests/storyboards only; production shows honest unavailable/disabled states while preserving the page design.
- State requests are single-flight or otherwise protected against duplicate clicks, and stale callbacks after disconnect/credential rotation cannot modify current UI.

## Work Items

- [x] Inspect and map source UI: Shopify: app/components/dashboard/UsageEvents.tsx; app/routes/app/usage/route.jsx.
- [x] Implement the bounded UI using separate presentation, controller/state, and supported transport modules.
- [x] Add fixture-driven component tests for primary, empty, loading, unavailable, denied and error states.
- [x] Provide 20-locales native gettext translation assets.
- [x] Record the LocalWP keyboard/responsive validation disposition: the user reports the plugin is installed and satisfactory; explicit developer completion accepts this report without claiming an independent walkthrough or reinstall.
- [x] Document any unsupported hosted API operation as a gap; never implement or fake a new backend service.

## Interfaces / Contracts

- Consume **only** existing approved Woo plugin/browser privileged REST interfaces and existing hosted API responses where implemented. Confirm the exact reachable contract from inspected source before wiring it.
- Do not create cross-repository DTOs or silently invent an `ARCH-035-API-*` prerequisite. If required data/action is unavailable, record an external dependency and keep production state truthful.
- UI fixture interfaces are local tests only; no fixtures enter the production bundle as merchant data.

## Dependencies

- `ARCH-035-WOOCOMMERCE-012` (architect-accepted Complete)

## Enables

- `ARCH-035-WOOCOMMERCE-010`
- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Billing plan/purchase history remains unchanged and Usage History is distinguishable from purchase transactions.
- [x] Period/filters/pagination preserve input and avoid duplicate requests; absent data is identified as unavailable rather than zero usage.
- [x] Back links and native page accessibility work.
- [x] New strings are translated in all 20 supported Admin locales (admin UI locale, site fallback; store/conversation language unchanged).
- [x] Existing Billing/connection/category experience and WordPress capability/nonce safeguards remain intact.
- [x] No backend service or database code is changed.

## Validation

- [x] Existing repository-declared focused JS component/controller tests for relevant UI states: 18 focused controller/screen tests passed; the screen suite passed 11/11 after adding the empty-state fixture.
- [x] Relevant PHP admin navigation/capability/nonce tests if PHP files are touched: `npm run test:php` passed (105 tests, 645 assertions).
- [x] `npm run test:i18n` and `npm run i18n:verify:20`: 28 i18n tests passed; 407 source messages, 19/19 translation packs, and 38 generated assets verified.
- [x] `npm run test:js`: 47 files and 292 tests passed; 37 integration/i18n checks passed.
- [x] `npm run build` and `npm run plugin-zip`: build succeeded with webpack entrypoint-size advisories; production archive verified (113 entries, 20/20 locales, 38 compiled assets).
- [x] Manual LocalWP validation disposition: user reports the existing install is satisfactory and explicitly supplied “Architect Review Accepted.” No independent login-protected walkthrough or reinstall was performed. No approved usage-history API exists; production shows unavailable rather than synthetic records.
- [x] `git diff --check` and canonical task launch/worktree evidence: clean diff; Attempt 1 task worktrees and dependency were verified by the canonical launcher; implementation commit `76babb3` and test follow-up `ad6311b` are published on the task branch.

## Stop Condition

When Work Items, UI-only Acceptance Criteria and required validation are complete, finish the Completion Report, set task to `review` and STOP for moda_architect. Do not implement deferred cross-repository capabilities. Report unavailable validation accurately.

## Implementation Notes

Match the canonical Shopify page composition rather than the illustrative labels/numbers in the wireframe. Layout is not permission to add unsupported functionality. Keep controlled state, transport and presentational components isolated. Use semantic native WordPress markup and CSS, not a cloned Shopify-only runtime.

## ASCII Page Design

The following is the **required UI layout/interaction guide**, not invented runtime data, API schema, or pixel-perfect CSS. Bracketed items are placeholders, not sample production records. Show unsupported actions disabled with explanation.

```text
+-------------------------------------------------------------------------------+
| Moda Interact > Usage History                                    [Refresh]    |
| Usage history for your subscription and entitlements.                          |
+-------------------------------------------------------------------------------+
| [Current period] [Past periods]                                                |
| Billing/entitlement period [Select period v]                                   |
| Event type [All v]                                            [Apply filters] |
+-------------------------------------------------------------------------------+
| Date / time       Event type           Quantity         Additional details     |
| [date]            [real event]         [quantity]       [real description]    |
| [date]            [real event]         [quantity]       [real description]    |
| [Previous]                                                    [Next]           |
+-------------------------------------------------------------------------------+
| [No events / Invalid cursor / Read unavailable / Load error]                    |
+-------------------------------------------------------------------------------+
```

## Completion Report

### Status

Complete — Attempt 1 was claimed by the developer at 2026-10-16T17:20:07Z and explicitly completed after “Architect Review Accepted.” The user-reported LocalWP satisfaction is accepted as the manual-validation disposition; no independent admin walkthrough was performed.

### Files Changed

45 implementation files changed across the Usage History UI, native navigation, locale catalogs, and focused tests. The implementation commits are `76babb3` and `ad6311b` on `task/ARCH-035-WOOCOMMERCE-006`.

### Work Completed

Added a distinct native Usage History screen with Current/Past views, period selection and cursor navigation, event filtering, page sizing, event pagination, recovery links, accessible state messaging, and locale-aware formatting. Presentation, controller/lifecycle, and transport remain modular; Billing Purchase History is unchanged. Added fixture coverage for ready/empty/loading/unavailable/denied/error/cursor states and request invalidation.

### Validation Results

Focused Usage History tests passed (controller/screen suite; final screen suite 11/11). `npm run test:i18n` passed 28 tests; `npm run i18n:verify:20` verified 407 source messages, 19/19 packs and 38 assets. `npm run test:js` passed 47 files/292 tests plus 37 integration/i18n checks. `npm run test:php` passed 105 tests/645 assertions. `composer lint` reported no PHP syntax errors. `npm run build` succeeded with webpack bundle-size advisories. `npm run plugin-zip` verified the 113-entry production archive and all 20 locales. `git diff --check` passed. `npm run lint` is not defined by this package; the package-defined `composer lint` was run instead.

### Deviations

The user reports that the plugin is installed in LocalWP and is satisfactory. The explicit developer completion accepts that report; it is not represented as an independently observed keyboard, responsive, error, or unavailable-state walkthrough. The Woo plugin has no approved usage-history endpoint; the production client therefore remains explicitly unavailable and never issues a guessed request or displays fabricated activity.

### Assumptions

Attempt 1 is claimed in the canonical developer worktrees. Fixture history is test-only; the missing hosted usage-history API remains external to this UI task and may require separate architecture.

### Unresolved Issues

No backend capability is asserted by this UI-only task. The production usage-history API is absent and documented above; no API, database, shared contract, or background changes were made.

### Architectural Concerns

The unavailable hosted usage-history API is an external dependency and must remain out of scope. Manual LocalWP validation remains unverified.

## Architect Review

### Review Status

Accepted by the developer-as-architect on 2026-10-16 after automated reconciliation. LocalWP satisfaction is user-reported, not independently observed.

### Review Notes

Implementation was source-compared with the named Shopify UsageEvents component/route and the Woo billing boundary. Billing remains distinct; missing hosted usage data is shown as unavailable. No backend or database files changed.


**Architect reconciliation (2026-10-16):** Native navigation prerequisite WOOCOMMERCE-012 is now Complete. Usage History remains absent. Status promoted from Pending to Ready after dependency reconciliation. No source code was changed by this promotion.

### Reviewed Files

Usage History screen/controller/client/formatting modules, native navigation and page-surface integration, locale catalogs, and focused JS/PHP tests. Automated validation results are recorded in the Completion Report. User-reported LocalWP satisfaction is not treated as independently observed evidence.

### Validation Reviewed

Automated JS, i18n, PHP, build, package and diff checks passed as listed in the Completion Report. No live LocalWP walkthrough was performed.

### Architecture Conformance

Conforms to the UI-only boundary. The page is functional as a UI surface but honestly unavailable for real history until an approved usage-history API exists. No new endpoint or data source was invented.

### Follow-up

No further task-scoped work. The developer explicitly accepted the recorded LocalWP validation disposition; downstream eligibility is reconciled below.

## Developer Self-Review

### Review Status

Accepted — Attempt 1 meets the UI-only scope and acceptance criteria. Focused and repository-wide JS checks, PHP tests/lint, i18n, build, packaging and diff checks passed. The user-reported LocalWP satisfaction is explicitly accepted as validation evidence, without claiming an independent walkthrough.

### Reviewed Files

The implementation diff on `task/ARCH-035-WOOCOMMERCE-006` (45 files), including the Usage History screen/controller/client/formatting modules, native navigation and page integration, locale catalogs, and JS/PHP tests. The follow-up empty-state test is included in commit `ad6311b`.

### Validation Reviewed

Focused Usage History controller/screen tests; `npm run test:i18n`; `npm run i18n:verify:20`; `npm run test:js` (47 files/292 tests plus 37 integration/i18n checks); `npm run test:php` (105 tests/645 assertions); `composer lint`; `npm run build`; `npm run plugin-zip`; and `git diff --check`. Results and webpack bundle-size advisories are recorded above.

### Architecture Conformance

Conforms to the UI-only boundary. No backend, database, shared-contract, or background changes were made. The unavailable hosted usage-history API is not fabricated; production presents an unavailable state.

## Developer Completion Decision

On 2026-10-16, the developer explicitly invoked `/moda_developer_update ARCH-035-WOOCOMMERCE-006 complete` and supplied “Architect Review Accepted.” Attempt 1 remains the accepted attempt; status is `complete`, with `executor: null` and `claimed_at: null`. The user-reported LocalWP satisfaction is accepted as the validation disposition; no independent admin walkthrough or plugin installation was performed. Neither task branch was merged into `main`.

### Dependency Frontier

- `ARCH-035-WOOCOMMERCE-010` remains `pending` on the canonical parent baseline until this completed task record is integrated. Its other dependency, `ARCH-035-WOOCOMMERCE-013`, is complete. No WOO-010 worktree was claimed or task file changed.
- `ARCH-035-SYSTEM-TEST-001` remains `pending`: its dependency set still includes WOO-010 and other incomplete tasks, and the system-test manual gate remains in force. No system-test worktree was claimed or task file changed.
- No architecture `_index.md`, submodule pointer, or `main` branch was changed.
