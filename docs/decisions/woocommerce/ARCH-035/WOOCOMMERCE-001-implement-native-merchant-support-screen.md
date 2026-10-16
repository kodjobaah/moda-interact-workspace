---
id: ARCH-035-WOOCOMMERCE-001
architecture_id: ARCH-035
title: Build native Woo merchant Support screen UI
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
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

# ARCH-035-WOOCOMMERCE-001: Build native Woo merchant Support screen UI

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Definition state: materialised on parent branch `task/ARCH-035-WOOCOMMERCE-001` in the canonical parent task worktree. The canonical launcher prepared the implementation task worktree for Attempt 1.
- Task state: `review`, `execution_mode: developer`, `completion_mode: developer`; Attempt 1 is submitted for architect review. The execution claim is cleared; the attempt number is unchanged.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-001`, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Execution/completion modes are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_woocommerce`, and task scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 1 was claimed after canonical worktree preparation and dependency verification.

## Objective

Replace the Woo Support placeholder with a Shopify-parity merchant support thread and composer UI using only already-approved integration capabilities.

## Context

Shopify app/routes/app/merchant-support/route.jsx renders paginated Administrative/System/Merchant messages, read states, translated/original toggle and a 500-grapheme composer; Woo NativeNavigation currently shows a placeholder.

Source references:
- Shopify: app/routes/app/merchant-support/route.jsx.
- Woo: includes/Admin/NativeNavigation.php; src/page/connected-workspace.js.

## Scope

- Implement Support content as small message-list, message-card, thread-pager, composer, controller and client modules.
- Use the existing WordPress nonce/capability, installation and session-safety model for any currently supported plugin/API read/write calls; do not add hosted API endpoints.
- Display translated/original messages, read/unread state, 500-grapheme count, submitted/error/empty/loading states, and provider-safe system links.
- For missing API operations render explicit unavailable state, disable unsupported mutation actions and document the backend gap; fixtures are tests only.

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

- [x] Inspect and map source UI: Shopify: app/routes/app/merchant-support/route.jsx.
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

- [x] Thread ordering, pagination, message kinds, translated/original switching and 500-grapheme validation match the Shopify interaction model.
- [x] Duplicate clicks cannot create duplicate UI submits; stale responses after reconnect/disconnect are not applied.
- [x] No Shopify-only refund action, invented send acknowledgement or message persisted in browser storage.
- [x] New strings are translated in all 20 supported Admin locales (admin UI locale, site fallback; store/conversation language unchanged).
- [x] Existing Billing/connection/category experience and WordPress capability/nonce safeguards remain intact.
- [x] No backend service or database code is changed.

## Validation

- [x] Existing repository-declared focused JS component/controller tests for relevant UI states.
- [x] Relevant PHP admin navigation/capability/nonce tests if PHP files are touched.
- [x] npm run test:i18n and npm run i18n:verify:20 (20 locales, POT/PO/compiled assets).
- [x] npm run test:js; npm run test:php when PHP is touched; npm run build; npm run plugin-zip.
- [x] Manual LocalWP admin navigation/keyboard/responsive/error/unavailable-state demonstration; developer confirms manual checks; API operations are absent and production remains unavailable.
- [x] git diff --check and canonical task launch/worktree evidence from actual developer environment.

## Stop Condition

When Work Items, UI-only Acceptance Criteria and required validation are complete, finish the Completion Report, set task to `review` and STOP for moda_architect. Do not implement deferred cross-repository capabilities. Report unavailable validation accurately.

## Implementation Notes

Match the canonical Shopify page composition rather than the illustrative labels/numbers in the wireframe. Layout is not permission to add unsupported functionality. Keep controlled state, transport and presentational components isolated. Use semantic native WordPress markup and CSS, not a cloned Shopify-only runtime.

## ASCII Page Design

The following is the **required UI layout/interaction guide**, not invented runtime data, API schema, or pixel-perfect CSS. Bracketed items are placeholders, not sample production records. Show unsupported actions disabled with explanation.

```text
+-------------------------------------------------------------------------------+
| Moda Interact > Support                                          [Refresh]    |
| Contact Moda support and review your messages.                                |
+-------------------------------------------------------------------------------+
| Support thread                                                                |
| +---------------------------------------------------------------------------+ |
| | Moda Support   [time]      [unread]                                        | |
| | Message body, translated where present.           [View original]         | |
| +---------------------------------------------------------------------------+ |
| | You            [time]      Message sent to Moda                            | |
| +---------------------------------------------------------------------------+ |
| | System         [time]      [Provider-safe related action, when allowed]    | |
| +---------------------------------------------------------------------------+ |
| [Previous]                                              Page n/N     [Next] |
+-------------------------------------------------------------------------------+
| Contact support                                                               |
| Message: [                                                                  ] |
|          [                                                                  ] |
| 0/500                     [Send / Sending... / Unavailable when no API]        |
+-------------------------------------------------------------------------------+
| Empty: No messages yet.   Error: Unable to load; [Retry].                     |
+-------------------------------------------------------------------------------+
```

## Completion Report

### Status

Developer Self-Review Accepted — Attempt 1. Status is `review`; `executor` and `claimed_at` are cleared. Because `completion_mode: developer`, this is not a completion decision.

### Files Changed

- Native Admin Support navigation and surface routing: `includes/Admin/NativeNavigation.php`, `src/native-admin/page-surface.js`, `src/page.js`, `src/page/connected-workspace.js`.
- Modular Support UI, state/controller, transport boundary, validation and styles: `src/support/**`, `src/index.scss`.
- Navigation/PHP/component/controller tests and gettext assets: `tests/PluginTest.php`, `tests/js/**`, `tests/i18n/**`, `languages/moda-interact.pot`, and 19 translated locale packs.
- Responsive shell correction and regression assertion: `src/support/styles/_support.scss`, `tests/js/support-screen.test.js` (implementation commit `fab5e9f`).

### Work Completed

- Replaced the Support placeholder with a native WordPress Admin screen composed from separate thread, message-card, pager, composer, controller, hook and client modules.
- Added fixture-driven coverage for primary/paginated, empty, loading, unavailable, denied, read/send error, grapheme count, duplicate submission, stale response and provider-safe system-link behavior.
- Added translated/original message rendering, unread labels, 500-grapheme composer validation, single-submit protection, confirmation-gated send success and connection-identity remount protection.
- Fixed the Support shell's narrow viewport overflow with scoped `border-box` sizing; the focused regression test and production CSS build pass.
- No backend/API, database, shared-contract or background code was added or changed. No fixture data enters production; read/send/mark-read remain disabled because no approved Woo privileged proxy/API operations exist.

### Validation Results

- `npx vitest run tests/js/support-screen.test.js`: 5 passed.
- `npm run test:js`: 42 Vitest files / 248 tests passed; 37 Node integration/i18n tests passed.
- `npm run test:i18n`: 28 passed. `npm run i18n:verify:20`: 355 source messages, 19/19 translation packs and 38 generated assets passed strict verification; release manifest reports 20/20 languages.
- `npm run test:php`: 105 tests / 644 assertions passed after installing the lockfile's Composer dev dependencies. `npm run lint:php`: no syntax errors.
- `npm run build`: passed. Webpack emitted a non-blocking performance recommendation because the 278 KiB entrypoint exceeds the 244 KiB advisory limit.
- `npm run plugin-zip`: production archive verified, version 0.1.0, 113 entries, 20/20 languages and 38 compiled assets; SHA-256 `d251347223985ea2971bb45d3ba5d383ca5e6fb51285140d13fbf44c1bdf80f`.
- `git diff --check`: passed for implementation and parent task changes. Canonical route/worktrees were verified; implementation commit `fab5e9f` is pushed.
- Manual checks: developer confirms LocalWP navigation, keyboard, responsive, error and unavailable-state checks. Shared sandbox inspection showed the explicit production unavailable state with unsupported controls disabled and no synthetic messages. That sandbox still served pre-fix CSS after rebuild, so the sizing correction is evidenced by the focused test and rebuilt production CSS rather than that cached asset.

### Deviations

- The Woo privileged REST/API surface has no approved support read, compose/send or mark-read operations. Per scope, production reports messages/sending unavailable and disables those actions; no endpoint was invented. Disabled production capabilities are covered by tests.

### Assumptions

- `ARCH-035-WOOCOMMERCE-012` remains complete and the task's developer takeover/materialisation evidence is authoritative.
- The missing support proxy/API operations remain external to this UI-only task and require a separately owned architecture/task before production functionality can be enabled.

### Unresolved Issues

- Production support read/send/mark-read are unavailable until an approved authenticated Woo privileged proxy and corresponding hosted support contract exist. This task intentionally leaves all three capabilities false.

### Architectural Concerns

No scope or architecture deviation identified. Production behavior is truthful in the absence of support API operations; no fake success or persisted message state is introduced.

## Architect Review

### Review Status

Pending moda_architect review. Developer self-review accepted Attempt 1 and transitioned the task to `review`; this does not complete the task.

### Review Notes

Reviewed the implementation diff, Shopify reference route, Woo navigation/surface wiring, support UI/controller/client/validation, focused tests, locale assets, PHP navigation tests and task/worktree state. The UI-only boundary, unsupported-operation behavior, state lifecycle and validation evidence conform to the task. Developer reports the requested LocalWP manual checks complete. The runtime limitation is the documented external API gap.


**Architect reconciliation (2026-10-16):** Native navigation prerequisite WOOCOMMERCE-012 is now Complete. Support remains a placeholder. Status promoted from Pending to Ready after dependency reconciliation. No source code was changed by this promotion.

### Reviewed Files

- `includes/Admin/NativeNavigation.php`
- `src/native-admin/page-surface.js`, `src/page.js`, `src/page/connected-workspace.js`
- `src/support/**`, `src/support/styles/_support.scss`
- `tests/PluginTest.php`, `tests/js/**`, `tests/i18n/**`
- `languages/moda-interact.pot` and supported locale catalogues

### Validation Reviewed

See Completion Report. All required automated test, lint, translation, build, package and diff checks passed. Manual validation is recorded from developer confirmation; the shared browser was not treated as evidence for the post-build CSS correction because it continued serving a cached/pre-fix asset.

### Architecture Conformance

Conforms to UI-only scope. No backend service, database or shared-contract changes; no invented endpoints, fixture production data, browser persistence or Shopify-only code. Unsupported production operations remain disabled and explicitly explained.

### Follow-up

Return to moda_architect for review. Do not start `ARCH-035-SYSTEM-TEST-001` or mark this task complete from this self-review. A future API-owned task must establish the approved support proxy/contract before enabling read, send or mark-read.

### Developer Self-Review - Accepted

- Attempt: 1 (unchanged).
- Implementation commit: `fab5e9f` on `task/ARCH-035-WOOCOMMERCE-001`, pushed to its mirrored remote branch.
- Parent task/report branch: `task/ARCH-035-WOOCOMMERCE-001`; report update is committed and pushed separately.
- Decision: accepted for architect review; task remains `review` because `completion_mode: developer`. No merge to `main` and no downstream task promotion performed.
