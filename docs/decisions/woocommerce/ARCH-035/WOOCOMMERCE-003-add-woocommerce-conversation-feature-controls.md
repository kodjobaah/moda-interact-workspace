---
id: ARCH-035-WOOCOMMERCE-003
architecture_id: ARCH-035
title: Add Shopify-parity conversation feature controls within Recovery Settings
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
  - ARCH-035-WOOCOMMERCE-002
enables:
  - ARCH-035-WOOCOMMERCE-004
  - ARCH-035-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-035-WOOCOMMERCE-003: Add Shopify-parity conversation feature controls within Recovery Settings

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: `moda-interact-workspace(20261011-192347).zip`; portable definition, not a materialised parent/implementation task branch.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-003` for this ready task. Execution ownership is taken over from the assigned agent: `execution_mode` and `completion_mode` are set to `developer`/`developer`; logical ownership remains `assigned_agent: moda_woocommerce`. Scope, dependencies, acceptance criteria and validation requirements are unchanged. The launcher will claim Attempt 1 after canonical worktree preparation and dependency verification.

## Objective

Render the existing plan-gated merchant feature preference cards and interactions inside Woo Recovery Settings.

## Context

Shopify app/components/settings/FeaturePreferences.tsx renders required non-editable features and optional automatically submitted toggles; it is embedded in RecoverySettingsView, not a separate top-level AI settings page.

Source references:
- Shopify: app/components/settings/FeaturePreferences.tsx; app/routes/app/recovery-settings/RecoverySettingsView.tsx.
- Woo: src/recovery-settings/recovery-settings-screen.js.

## Scope

- Build a self-contained feature-preferences section within Recovery Settings, with separate view, controller/client adapter and persisted-value presentation.
- Render required/core features as non-editable; render optional features as switches only when editable and entitled.
- Use feature keys and names returned by an existing approved read source; do not invent Human Handoff/Test Conversations features or hard-code entitlements.
- For missing feature read/write contract, use a clear unavailable panel and disabled controls rather than writing to local-only fake state.

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

- [x] Inspect and map source UI: Shopify: app/components/settings/FeaturePreferences.tsx; app/routes/app/recovery-settings/RecoverySettingsView.tsx.
- [x] Implement the bounded UI using separate presentation, controller/state, and supported transport modules; production remains explicitly unavailable because no approved preference API exists.
- [x] Add fixture-driven component/controller tests for primary, empty, loading, saving, unavailable, denied, conflict and error states.
- [ ] Provide 20-locales native gettext translation assets and WordPress keyboard/responsive checks. Locale verification passed; feature-specific keyboard/responsive LocalWP evidence remains outstanding.
- [x] Document the unsupported hosted API operation as a gap; do not implement or fake a new backend service.

## Interfaces / Contracts

- Consume **only** existing approved Woo plugin/browser privileged REST interfaces and existing hosted API responses where implemented. Confirm the exact reachable contract from inspected source before wiring it.
- Do not create cross-repository DTOs or silently invent an `ARCH-035-API-*` prerequisite. If required data/action is unavailable, record an external dependency and keep production state truthful.
- UI fixture interfaces are local tests only; no fixtures enter the production bundle as merchant data.

## Dependencies

- `ARCH-035-WOOCOMMERCE-002` (architect-accepted Complete)

## Enables

- `ARCH-035-WOOCOMMERCE-004`
- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Required/optional layout and effective on/off language match Shopify; unsupported production data/actions are not fabricated.
- [x] Controller guards duplicate saves and stale responses; denial/empty/error states are distinct.
- [x] No new feature entitlement logic, persisted Shop state or cross-service contracts.
- [x] Existing strings/assets pass the 20-locale verification; administrator/site locale behavior and store/conversation language are unchanged.
- [x] Existing Billing/connection/category experience and WordPress capability/nonce safeguards remain intact under the JS regression suite; no PHP files were touched.
- [x] No backend service or database code is changed.

## Validation

- [x] Focused controller/panel tests: `npx vitest run tests/js/feature-preferences-controller.test.js tests/js/feature-preferences-panel.test.js` (2 files, 13 tests passed).
- [x] PHP tests were not applicable; no PHP files were touched.
- [x] `npm run test:i18n` (28 passed) and `npm run i18n:verify:20` (367 messages, 19 translation packs, 38 generated assets; strict verification passed).
- [x] `npm run test:js` (44 Vitest files/262 tests and 37 Node integration/i18n tests passed); `npm run build` passed; `npm run plugin-zip` passed (113 entries, SHA-256 `b0fd66fb8ef78a15feaa01451128404faa86d0823f75ba330e7de0025f6927d9`). PHP tests were not applicable.
- [ ] Manual LocalWP feature navigation/keyboard/responsive/error/unavailable-state demonstration. Developer reports LocalWP is installed and is satisfactory; this session did not independently verify those feature-specific interactions. Source inspection confirms the preference API is absent/superseded, and production therefore renders the unavailable state. Browser access during this session failed with SSL/ngrok errors.
- [x] `git diff --check`, focused JS lint and new stylesheet lint passed. Launcher route resolved the canonical worktrees; implementation branch `task/ARCH-035-WOOCOMMERCE-003` is pushed at `1fa459bd4972ab320c6d248838e47d0900b4ca6c`. Parent task branch is the canonical task worktree; detailed start-of-attempt submodule synchronization evidence was not retained in this report.

## Stop Condition

When Work Items, UI-only Acceptance Criteria and required validation are complete, finish the Completion Report, set task to `review` and STOP for moda_architect. Do not implement deferred cross-repository capabilities. Report unavailable validation accurately.

## Implementation Notes

Match the canonical Shopify page composition rather than the illustrative labels/numbers in the wireframe. Layout is not permission to add unsupported functionality. Keep controlled state, transport and presentational components isolated. Use semantic native WordPress markup and CSS, not a cloned Shopify-only runtime.

## ASCII Page Design

The following is the **required UI layout/interaction guide**, not invented runtime data, API schema, or pixel-perfect CSS. Bracketed items are placeholders, not sample production records. Show unsupported actions disabled with explanation.

```text
+-------------------------------------------------------------------------------+
| Recovery settings > Conversation features                                     |
+-------------------------------------------------------------------------------+
| Merchant features                                                             |
| Control optional features available under your plan.                           |
| +------------------------------------+ +------------------------------------+ |
| | [check] Checkout recovery          | | [switch ON/OFF] AI Conversations   | |
| | Required / always on               | | Optional / effective status        | |
| +------------------------------------+ +------------------------------------+ |
| | [switch] Other entitled feature    | | [required] Other core feature      | |
| +------------------------------------+ +------------------------------------+ |
| [Saving...] [Conflict / Reload] [No configurable features / Unavailable]        |
+-------------------------------------------------------------------------------+
| Feature list and switch availability come from real entitlements.              |
+-------------------------------------------------------------------------------+
```

## Completion Report

### Status

Developer self-review requests changes — Attempt 1. The task is returned to Ready without incrementing the attempt; the feature-specific LocalWP keyboard/responsive interaction evidence remains outstanding.

### Files Changed

Implementation is in `moda-interact-woocommerce`, primarily the feature-preferences client/controller/panel and stylesheet, Recovery Settings/page integration, and focused JS tests. No PHP, API, Shared, database or background files were changed. Implementation commits: `40788629118db7e2be259025f47c1896cafa98d3` and lint follow-up `1fa459bd4972ab320c6d248838e47d0900b4ca6c` (pushed on the task branch).

### Work Completed

Added the Shopify-aligned conversation-features section, isolated client/controller/panel modules, lifecycle/revision/stale-response guards, accessible loading/saving/unavailable/denied/conflict/error/empty states, and fixture-driven coverage. The production adapter returns `FEATURES_UNAVAILABLE`; it does not invent a route or persist browser-only feature state. Source and API inspection found `ARCH-035-API-003` superseded and no approved feature-preference route. The UI-only behavior remains within scope.

### Validation Results

Passed: focused feature tests (13); full JS suite (44 files/262 Vitest tests plus 37 Node tests); i18n suite (28); strict 20-locale verification; focused JS and feature stylesheet lint; build; production ZIP verification (113 entries, 20/20 locale assets); `git diff --check`. The build retains the repository's 291 KiB entrypoint warning against a 244 KiB recommendation. No PHP files changed, so PHP tests were not required.

Not independently verified: the feature-specific LocalWP keyboard, responsive, and unavailable/error-state walkthrough. The developer reports LocalWP is installed and satisfactory and requested no installation; browser access from this session failed with SSL/ngrok errors. This report does not treat that statement as evidence for the unobserved interaction matrix.

### Deviations

No new API/backend was added because the only identified preference API task is superseded and there is no approved route. Production controls remain disabled/unavailable as required by the UI-only contract. The required manual LocalWP evidence is deferred rather than claimed.

### Assumptions

The feature-preference API gap is external to this UI-only task and requires a separately approved architecture/task before real preference reads or writes can be enabled.

### Unresolved Issues

Feature-specific LocalWP navigation, keyboard and responsive validation still needs a reproducible checklist or evidence. Real preference data and writes remain unavailable because no approved API contract exists.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.


**Architect reconciliation (2026-10-16):** Recovery policy prerequisite WOOCOMMERCE-002 is now Complete. The feature-preferences section is absent. Status promoted from Pending to Ready after dependency reconciliation. No source code was changed by this promotion.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Return to architect for UI review and source comparison.

## Developer Self-Review - Changes Requested

### Outcome

Changes Requested. Attempt 1's implementation and automated validation are substantially complete, but the task's required manual LocalWP interaction validation is not evidenced. The user reports that LocalWP is installed and satisfactory; no feature-specific keyboard/responsive/error/unavailable-state walkthrough was observed in this session. Preserve Attempt 1 and return the task to Ready.

### Required Corrections

- Provide a feature-specific LocalWP walkthrough or reproducible evidence covering Recovery Settings navigation, keyboard operation, responsive layout, and unavailable/error states. Confirm that no preference read/write endpoint is present and that controls remain disabled without one.
- Update this report with the exact evidence/steps and validation result; then rerun any focused check affected by corrections.

### Review Evidence

- Implementation task branch: `task/ARCH-035-WOOCOMMERCE-003`, pushed tip `1fa459bd4972ab320c6d248838e47d0900b4ca6c`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-003`, branch `task/ARCH-035-WOOCOMMERCE-003`; claim commit `3af98e0ccabd971eee05403de1308f1b6ea1fc1c` is present on its remote-tracking branch.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-003`; no shared/default implementation checkout was switched or edited for this work. No submodule gitlink was staged.
- Attempt remains 1. This self-review does not mark the task complete or begin a new attempt.
