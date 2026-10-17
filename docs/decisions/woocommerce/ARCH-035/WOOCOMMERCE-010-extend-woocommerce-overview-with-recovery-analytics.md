---
id: ARCH-035-WOOCOMMERCE-010
architecture_id: ARCH-035
title: Bring native Woo Overview presentation to Shopify dashboard parity
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-WOOCOMMERCE-006
  - ARCH-035-WOOCOMMERCE-013
enables:
  - ARCH-035-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-WOOCOMMERCE-010: Bring native Woo Overview presentation to Shopify dashboard parity

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: `moda-interact-workspace(20261011-192347).zip`; portable definition, not a materialised parent/implementation task branch.

## Objective

Extend the existing Woo Overview layout with the Shopify recovery-performance, capacity, recent and pending presentation only where authoritative data is available.

## Context

Shopify RecoveryOverview.tsx displays date-filtered Started/Recovered/Rate/Value metrics, incomplete/ongoing counts, recent recoveries, capacity balances and pending recoveries. Woo Overview currently focuses on connection/state, store context and a basic summary.

Source references:
- Shopify: app/components/dashboard/RecoveryOverview.tsx; app/components/dashboard/PendingRecoveries.jsx.
- Woo: src/overview-screen.js; src/page/connected-workspace.js.

## Scope

- Preserve Woo connection/Free plan/category status while introducing Shopify-like date-presets and metric cards, recent recoveries, capacity and pending section.
- Link recent/pending rows to Recoveries list/detail, and usage capacity to Usage History/Billing, with clear navigation boundaries.
- Never calculate recovered revenue, conversion rates or pending counts from fabricated or unrelated billing data.
- When aggregate/read APIs are absent, show an explicit unavailable card or partial-data message, not misleading zeroes.

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

- [ ] Inspect and map source UI: Shopify: app/components/dashboard/RecoveryOverview.tsx; app/components/dashboard/PendingRecoveries.jsx.
- [ ] Implement the bounded UI using separate presentation, controller/state, and supported transport modules.
- [ ] Add fixture-driven component tests for primary, empty, loading, unavailable, denied and error states.
- [ ] Provide 20-locales native gettext translation assets and WordPress keyboard/responsive checks.
- [ ] Document any unsupported hosted API operation as a gap; never implement or fake a new backend service.

## Interfaces / Contracts

- Consume **only** existing approved Woo plugin/browser privileged REST interfaces and existing hosted API responses where implemented. Confirm the exact reachable contract from inspected source before wiring it.
- Do not create cross-repository DTOs or silently invent an `ARCH-035-API-*` prerequisite. If required data/action is unavailable, record an external dependency and keep production state truthful.
- UI fixture interfaces are local tests only; no fixtures enter the production bundle as merchant data.

## Dependencies

- `ARCH-035-WOOCOMMERCE-006` (architect-accepted Complete)
- `ARCH-035-WOOCOMMERCE-013` (architect-accepted Complete)

## Enables

- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Overview layout/capacity/recent/pending sections correspond to real Shopify reference, not invented metric titles.
- [ ] Date filters, refresh, loading/empty/error states work; metrics use locale-aware precision/currency.
- [ ] Existing onboarding, category and Billing connection/status flows remain functional.
- [ ] New strings are translated in all 20 supported Admin locales (admin UI locale, site fallback; store/conversation language unchanged).
- [ ] Existing Billing/connection/category experience and WordPress capability/nonce safeguards remain intact.
- [ ] No backend service or database code is changed.

## Validation

- [ ] Existing repository-declared focused JS component/controller tests for relevant UI states.
- [ ] Relevant PHP admin navigation/capability/nonce tests if PHP files are touched.
- [ ] npm run test:i18n and npm run i18n:verify:20 (20 locales, POT/PO/compiled assets).
- [ ] npm run test:js; npm run test:php when PHP is touched; npm run build; npm run plugin-zip.
- [ ] Automated component/DOM-responsive, keyboard and unavailable/error-state checks using repository-supported fixtures (no LocalWP invocation).
- [ ] git diff --check and canonical task launch/worktree evidence from actual developer environment.

## Stop Condition

When Work Items, UI-only Acceptance Criteria and required validation are complete, finish the Completion Report, set task to `review` and STOP for moda_architect. Do not implement deferred cross-repository capabilities. Report unavailable validation accurately.

## Implementation Notes

Match the canonical Shopify page composition rather than the illustrative labels/numbers in the wireframe. Layout is not permission to add unsupported functionality. Keep controlled state, transport and presentational components isolated. Use semantic native WordPress markup and CSS, not a cloned Shopify-only runtime.

Developer-only manual checkpoint (outside repository-agent execution/acceptance): the developer launches LocalWP and checks connected/admin navigation, keyboard/responsive layout and truthful unavailable/error states, recording screenshots/results if desired. The implementing agent must not launch or manually operate LocalWP or claim those checks passed. Automated repository validation remains required.

## ASCII Page Design

The following is the **required UI layout/interaction guide**, not invented runtime data, API schema, or pixel-perfect CSS. Bracketed items are placeholders, not sample production records. Show unsupported actions disabled with explanation.

```text
+-------------------------------------------------------------------------------+
| Moda Interact > Overview                                          [Refresh]   |
| [Connection status]  [Plan and store context]                                  |
+-------------------------------------------------------------------------------+
| Recovery performance  [Today] [Week] [Month] [Custom dates]                   |
| +-------------+ +--------------+ +----------------+ +-----------------------+ |
| | Started     | | Recovered    | | Recovery rate  | | Recovered value       | |
| | [real n]    | | [real n]     | | [real %]       | | [real currency value] | |
| +-------------+ +--------------+ +----------------+ +-----------------------+ |
| Incomplete [n]   Ongoing [n]        [Unavailable where data is missing]       |
+-------------------------------------+-----------------------------------------+
| Recent recoveries                   | Recovery capacity                       |
| [real recent rows]                  | [available / reserved]                   |
| [View all recoveries]               | Promotional / purchased credits          |
+-------------------------------------+-----------------------------------------+
| Pending recoveries                                                           |
| [Customer / status / date]  [View all / Refresh]                              |
+-------------------------------------------------------------------------------+
| [No data / Loading / Partial information / Unavailable / Error]                |
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

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Return to architect for UI review and source comparison.
