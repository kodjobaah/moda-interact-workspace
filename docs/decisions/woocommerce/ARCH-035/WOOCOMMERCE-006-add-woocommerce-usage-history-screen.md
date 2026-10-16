---
id: ARCH-035-WOOCOMMERCE-006
architecture_id: ARCH-035
title: Add Shopify-parity Woo Usage History UI
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
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

- [ ] Inspect and map source UI: Shopify: app/components/dashboard/UsageEvents.tsx; app/routes/app/usage/route.jsx.
- [ ] Implement the bounded UI using separate presentation, controller/state, and supported transport modules.
- [ ] Add fixture-driven component tests for primary, empty, loading, unavailable, denied and error states.
- [ ] Provide 20-locales native gettext translation assets and WordPress keyboard/responsive checks.
- [ ] Document any unsupported hosted API operation as a gap; never implement or fake a new backend service.

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

- [ ] Billing plan/purchase history remains unchanged and Usage History is distinguishable from purchase transactions.
- [ ] Period/filters/pagination preserve input and avoid duplicate requests; absent data is identified as unavailable rather than zero usage.
- [ ] Back links and native page accessibility work.
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

Not Started.

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


**Architect reconciliation (2026-10-16):** Native navigation prerequisite WOOCOMMERCE-012 is now Complete. Usage History remains absent. Status promoted from Pending to Ready after dependency reconciliation. No source code was changed by this promotion.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Return to architect for UI review and source comparison.
