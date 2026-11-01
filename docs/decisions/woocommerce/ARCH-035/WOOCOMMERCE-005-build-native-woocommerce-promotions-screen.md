---
id: ARCH-035-WOOCOMMERCE-005
architecture_id: ARCH-035
title: Build native Woo Promotions credit-selection UI
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
  - ARCH-035-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-035-WOOCOMMERCE-005: Build native Woo Promotions credit-selection UI

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Definition state: materialised on parent branch `task/ARCH-035-WOOCOMMERCE-005` in the canonical parent task worktree. The implementation task worktree will be prepared by the launcher when execution is claimed.
- Task state: `complete`, `execution_mode: developer`, `completion_mode: developer`; Attempt 1 was accepted and explicitly completed by the developer. The launcher verified the live WOOCOMMERCE-012 dependency as `complete`.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-005`, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Execution/completion modes are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_woocommerce`, and the task scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 1 was claimed after canonical worktree preparation and dependency verification.

## Objective

Implement the Shopify-style Promotions cards, current selection and history in the native Woo admin surface.

## Context

Shopify app/routes/app/promotions/route.tsx offers promotional recovery-credit selection (not coupon or discount issuance), with selected/locked state, available offers, pagination and history. Woo promotions submenu is a placeholder.

Source references:
- Shopify: app/routes/app/promotions/route.tsx.
- Woo: includes/Admin/NativeNavigation.php.

## Scope

- Implement Promotions heading/intro, current promotion card, eligible offer grid, claim selection controls, paginated offer list and history disclosure.
- Use the current Shop promotion data if an approved existing read exists; otherwise show honest unavailable/empty states; do not fabricate eligibility.
- A real selection write, if present, must use an approved existing API via privileged WordPress route; otherwise selection controls are disabled with explanation.
- Prevent double-selection and represent selected/locked/exhausted/expired outcomes without claiming a new backend transition.

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

- [x] Inspect and map source UI: Shopify: app/routes/app/promotions/route.tsx.
- [x] Implement the bounded UI using separate presentation, controller/state, and supported transport modules.
- [x] Add fixture-driven component tests for primary, empty, loading, unavailable, denied and error states.
- [x] Provide 20-locales native gettext translation assets and WordPress keyboard/responsive checks.
- [x] Document any unsupported hosted API operation as a gap; never implement or fake a new backend service.

## Interfaces / Contracts

- Consume **only** existing approved Woo plugin/browser privileged REST interfaces and existing hosted API responses where implemented. Confirm the exact reachable contract from inspected source before wiring it.
- Do not create cross-repository DTOs or silently invent an `ARCH-035-API-*` prerequisite. If required data/action is unavailable, record an external dependency and keep production state truthful.
- UI fixture interfaces are local tests only; no fixtures enter the production bundle as merchant data.

## Dependencies

- `ARCH-035-WOOCOMMERCE-012` (architect-accepted Complete)

## Enables

- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Promotions refer to recovery credits, never Woo or Shopify coupon creation.
- [x] Selected/locked state removes or disables unavailable choices and protects double click.
- [x] History, pagination, no-offers and failure states align with Shopify.
- [x] New strings are translated in all 20 supported Admin locales (admin UI locale, site fallback; store/conversation language unchanged).
- [x] Existing Billing/connection/category experience and WordPress capability/nonce safeguards remain intact.
- [x] No backend service or database code is changed.

## Validation

- [x] Existing repository-declared focused JS component/controller tests for relevant UI states.
- [x] Relevant PHP admin navigation/capability/nonce tests if PHP files are touched.
- [x] npm run test:i18n and npm run i18n:verify:20 (20 locales, POT/PO/compiled assets).
- [x] npm run test:js; npm run test:php when PHP is touched; npm run build; npm run plugin-zip.
- [x] Manual LocalWP admin navigation/keyboard/responsive/error/unavailable-state demonstration; record whether APIs are real or absent.
- [x] git diff --check and canonical task launch/worktree evidence from actual developer environment.

## Stop Condition

When Work Items, UI-only Acceptance Criteria and required validation are complete, finish the Completion Report, set task to `review` and STOP for moda_architect. Do not implement deferred cross-repository capabilities. Report unavailable validation accurately.

## Implementation Notes

Match the canonical Shopify page composition rather than the illustrative labels/numbers in the wireframe. Layout is not permission to add unsupported functionality. Keep controlled state, transport and presentational components isolated. Use semantic native WordPress markup and CSS, not a cloned Shopify-only runtime.

## ASCII Page Design

The following is the **required UI layout/interaction guide**, not invented runtime data, API schema, or pixel-perfect CSS. Bracketed items are placeholders, not sample production records. Show unsupported actions disabled with explanation.

```text
+-------------------------------------------------------------------------------+
| Moda Interact > Promotions                                        [Refresh]   |
| Choose promotional recovery-credit offers available to your store.            |
+-------------------------------------------------------------------------------+
| Active promotion [only when selected]                                           |
| [Campaign title]     [Selected / Exhausted]  Remaining [count]  Expires [date] |
+-------------------------------------------------------------------------------+
| Available promotions                                                          |
| +----------------------+ +----------------------+ +-------------------------+ |
| | [Offer title]        | | [Offer title]        | | [Offer title]           | |
| | [credit quantity]    | | [credit quantity]    | | [credit quantity]       | |
| | [expiry]  [Select]   | | [expiry]  [Select]   | | [expiry] [Select]       | |
| +----------------------+ +----------------------+ +-------------------------+ |
| [Previous]                                                     [Next]          |
+-------------------------------------------------------------------------------+
| > Promotion history                                                           |
|    Campaign / quantity / selection & expiry dates / status                    |
+-------------------------------------------------------------------------------+
| [No offers / Already selected / Unavailable / Unable to load]                 |
+-------------------------------------------------------------------------------+
```

## Completion Report

### Status

Complete — Attempt 1; Architect Review Accepted and explicit developer completion recorded on 2026-10-16. The developer reports installing the plugin in LocalWP and being satisfied. The assistant did not reinstall it or independently repeat that walkthrough, per the developer's instruction.

### Files Changed

Promotions UI and presentation modules: `src/promotions/promotions-screen.js`, `src/promotions/presentation.js`, `src/promotions/history.js`, `src/promotions/_promotions.scss`.

Native page wiring and admin navigation: `src/page.js`, `src/page/connected-workspace.js`, `src/native-admin/page-surface.js`, `includes/Admin/NativeNavigation.php`.

Coverage: `tests/js/promotions-screen.test.js`, `tests/js/native-merchant-navigation.test.js`, `tests/js/page-connected-workspace.test.js`, `tests/PluginTest.php`.

Localization: `languages/moda-interact.pot` and all 19 supported PO catalogues. The task branch also incorporates current `origin/main` Support-screen work; shared navigation and page wiring retain both Support and Promotions.

### Work Completed

- Inspected the Shopify Promotions route and Woo native admin surface. Added modular Woo presentation for active/available promotional recovery credits, offer pagination, selected/locked states and expandable history; coupon issuance is not represented.
- Production Promotions remains explicitly unavailable because no approved Woo privileged read/write contract exists for eligible offers, current selection, history or selection. Selection is disabled; test fixtures are not shipped as merchant data and no successful backend transition is claimed.
- Added fixture-driven coverage for unavailable, loading, error/denied, empty, selected/locked, pagination/history and selection guards. Connected native routing and capability-screen coverage include Promotions alongside the current-main Support surface.
- Added/merged translation entries across all supported catalogues and preserved existing admin locale behavior. Native buttons/details provide keyboard-operable controls; the responsive Promotions layout is implemented in its feature stylesheet.
- No backend service, database, Shared contract, API, Background, checkout or coupon implementation was changed.

### Validation Results

- `npm run test:js`: passed; 43 JS files, 257 unit tests, plus 37 integration/i18n tests.
- `npm run test:i18n`: passed; 28 tests.
- `npm run i18n:verify:20`: passed; 371 source messages, 19/19 translated language packs, 38 generated assets for 20 canonical locales.
- `npm run test:php`: passed; 105 tests, 642 assertions.
- `npm run lint:js`: passed; only the existing legacy ESLint configuration warning remains.
- `npm run lint:php`: passed; all configured PHP syntax checks passed.
- `npm run build`: passed. Webpack emitted two bundle-size recommendations; the 295 KiB entrypoint exceeds the 244 KiB recommendation.
- `npm run plugin-zip`: passed; production archive verified as `moda-interact.zip` with 113 entries. This packaged the plugin but did not install it.
- `git diff --check`, staged diff check and conflict-marker/unmerged-path checks passed after synchronization.
- LocalWP: developer reports the plugin is installed and satisfactory. No assistant reinstall or independent per-scenario keyboard/responsive/error/unavailable walkthrough was performed. Fixture tests cover unavailable and failure states; the API remains absent as noted above.
- Implementation worktree: `moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-005`, branch `task/ARCH-035-WOOCOMMERCE-005`. Implementation commit `70c182c` and synchronization/resolution commit `dfd3b5e` are published to `origin/task/ARCH-035-WOOCOMMERCE-005`. The latter merges current main into the task branch; no task branch was merged into main.

### Deviations

- The existing approved Woo API surface does not expose Promotions reads or selection writes. Per scope, the implementation delivers the truthful unavailable/disabled production state instead of inventing an endpoint or fake data.
- The task branch was synchronized with current main after WOO-001 added Support. The merge was resolved to preserve both application screens, translations and tests. Support files received scoped formatting/lint corrections so the synchronized repository-wide JavaScript lint passes.

### Assumptions

The user-reported LocalWP satisfaction is treated as the developer's manual confirmation; it is not claimed as an independently observed test result. Promotions API work remains outside this UI-only task and requires separately approved scope.

### Unresolved Issues

No approved Woo contract currently provides eligible promotions, selected promotional credits, promotion history or a selection operation. Production remains unavailable/disabled until a separately scoped API and privileged Woo proxy are approved and delivered.

### Architectural Concerns

No scope expansion or backend implementation was made. The missing Promotions API is an explicit external dependency, not a code defect within this UI-only task.

### Developer Self-Review

**Passed / Accepted.** The UI-only scope, truthful unavailable behavior, fixture coverage, translation gate, PHP navigation/capability checks and production package validation pass. The user's LocalWP confirmation is recorded with its verification limitation above. Attempt 1 is accepted; the developer's explicit completion decision is recorded below.

## Architect Review

### Review Status

Accepted — the developer supplied “Architect Review Accepted” with the explicit completion request on 2026-10-16.

### Review Notes

Accepted for this UI-only task. The source-aligned recovery-credit UI is implemented; missing production read/write capabilities are explicitly unavailable and were not fabricated. The combined native navigation and translations preserve WOO-001 Support and Promotions. The developer confirmed acceptance and explicitly completed Attempt 1.


**Architect reconciliation (2026-10-16, historical):** Native navigation prerequisite WOOCOMMERCE-012 is now Complete. Promotions was then a planned/unavailable destination. Status was promoted from Pending to Ready after dependency reconciliation. No source code was changed by that promotion. The task was subsequently implemented, reviewed and completed in Attempt 1 as recorded above.

### Reviewed Files

`src/promotions/promotions-screen.js`, `src/promotions/presentation.js`, `src/promotions/history.js`, `src/promotions/_promotions.scss`, `src/page.js`, `src/page/connected-workspace.js`, `src/native-admin/page-surface.js`, `includes/Admin/NativeNavigation.php`, `tests/js/promotions-screen.test.js`, `tests/js/native-merchant-navigation.test.js`, `tests/js/page-connected-workspace.test.js`, `tests/PluginTest.php`, `languages/moda-interact.pot`, and all 19 locale PO catalogues. Current-main Support coexistence changes were inspected as part of the synchronization merge.

### Validation Reviewed

Accepted based on the recorded results: 257 JS unit tests, 37 integration/i18n tests, 28 standalone i18n tests, 105 PHP tests / 642 assertions, JS and PHP lint, strict 20-locale verification, build, ZIP packaging and clean diff checks. The reported Webpack size warning and user-reported (not independently repeated) LocalWP validation limitation remain documented.

### Architecture Conformance

Accepted. The implementation remains UI-only, uses truthful unavailable production state, preserves capability/navigation protections, and does not introduce hosted API, database, Shared, Background or coupon behavior.

### Follow-up

The developer explicitly invoked `/moda_developer_update ARCH-035-WOOCOMMERCE-005 complete` after supplying Architect Review Accepted. The task is `complete`, claim fields are cleared, and Attempt 1 is unchanged. If real Woo Promotions data/selection is later required, define and approve a separate API/proxy task before enabling production controls. `ARCH-035-SYSTEM-TEST-001` remains `pending`: other required Woo UI dependencies, including WOOCOMMERCE-003, -004, -006 and -010, are not complete; no downstream readiness transition was made.

## Developer Completion Decision

On 2026-10-16, the developer explicitly invoked `/moda_developer_update ARCH-035-WOOCOMMERCE-005 complete` with “Architect Review Accepted.” The passing review is durable above, the task-owned implementation commit is published, all defined Work Items and Acceptance Criteria are checked, and required validation is recorded. Status is `complete`; `executor` and `claimed_at` are null; Attempt 1 is preserved. The Promotions API gap remains an accepted external dependency under the UI-only contract, not unimplemented in-scope work.
