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
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-16T13:53:43Z
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

- [ ] Inspect and map source UI: Shopify: app/components/settings/FeaturePreferences.tsx; app/routes/app/recovery-settings/RecoverySettingsView.tsx.
- [ ] Implement the bounded UI using separate presentation, controller/state, and supported transport modules.
- [ ] Add fixture-driven component tests for primary, empty, loading, unavailable, denied and error states.
- [ ] Provide 20-locales native gettext translation assets and WordPress keyboard/responsive checks.
- [ ] Document any unsupported hosted API operation as a gap; never implement or fake a new backend service.

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

- [ ] Required/optional layout and effective on/off language match Shopify.
- [ ] Toggles are guarded against duplicate saves and stale responses; denial/empty/error states are distinct.
- [ ] No new feature entitlement logic, persisted Shop state or cross-service contracts.
- [ ] New strings are translated in all 20 supported Admin locales (admin UI locale, site fallback; store/conversation language unchanged).
- [ ] Existing Billing/connection/category experience and WordPress capability/nonce safeguards remain intact.
- [ ] No backend service or database code is changed.

## Validation

- [ ] Existing repository-declared focused JS component/controller tests for relevant UI states.
- [ ] Relevant PHP admin navigation/capability/nonce tests if PHP files are touched.
- [ ] npm run test:i18n and npm run i18n:verify:20 (20 locales, POT/PO/compiled assets).
- [ ] npm run test:js; npm run test:php when PHP is touched; npm run build; npm run plugin-zip.
- [ ] Manual LocalWP admin navigation/keyboard/responsive/error/unavailable-state demonstration; record whether APIs are real or absent.
- [ ] git diff --check and canonical task launch/worktree evidence from actual developer environment.

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

In Progress — Attempt 1 claimed by developer at 2026-10-16T13:53:43Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

This definition is portable and has not been claimed. Any missing hosted API capability is external to ARCH-035 and may require a separate architecture.

### Unresolved Issues

No backend capability is asserted by this UI-only task. Document discovered API gaps in the completion report.

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
