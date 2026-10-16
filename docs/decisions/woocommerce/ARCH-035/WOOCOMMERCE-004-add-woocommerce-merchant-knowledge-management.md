---
id: ARCH-035-WOOCOMMERCE-004
architecture_id: ARCH-035
title: Add Shopify-parity Merchant Knowledge section within Recovery Settings
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
attempt: 0
depends_on:
  - ARCH-035-WOOCOMMERCE-003
enables:
  - ARCH-035-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-035-WOOCOMMERCE-004: Add Shopify-parity Merchant Knowledge section within Recovery Settings

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: portable architect definition materialised on the canonical parent task branch `task/ARCH-035-WOOCOMMERCE-004`; implementation task branch/worktree is being prepared for Attempt 1.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-004` for this ready task. Execution and completion ownership are taken over from the assigned agent: `execution_mode` and `completion_mode` are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_woocommerce`. Scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 0 remains unclaimed until canonical preparation and dependency verification succeed.

## Objective

Build the Woo Recovery Settings Merchant Knowledge management UI following Shopify source list, add-source and status presentation.

## Context

Shopify MerchantKnowledgeSection.tsx is embedded inside Recovery Settings and supports URL/file source disclosure, plan capacity, status, refresh, reorder, edit, replace and delete. Woo currently has no such section.

Source references:
- Shopify: app/components/settings/MerchantKnowledgeSection.tsx; app/routes/app/recovery-settings/RecoverySettingsView.tsx.
- Woo: src/recovery-settings/recovery-settings-screen.js.

## Scope

- Implement a bounded section with source-count/capacity summary, add URL and upload disclosures, source cards, processing/failure badges and source actions.
- Match approved input concepts (name, purpose/type, language, URL or file) only where supported by the existing service read/write contracts.
- Separate source list, URL form, upload form, individual card, controller and API adapter; preserve URL safety and file validation at browser boundary.
- Do not create hosted upload intent or R2 CORS changes; when absent show explicit unavailable status and disable unsupported actions (including uploads).

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

- [ ] Inspect and map source UI: Shopify: app/components/settings/MerchantKnowledgeSection.tsx; app/routes/app/recovery-settings/RecoverySettingsView.tsx.
- [ ] Implement the bounded UI using separate presentation, controller/state, and supported transport modules.
- [ ] Add fixture-driven component tests for primary, empty, loading, unavailable, denied and error states.
- [ ] Provide 20-locales native gettext translation assets and WordPress keyboard/responsive checks.
- [ ] Document any unsupported hosted API operation as a gap; never implement or fake a new backend service.

## Interfaces / Contracts

- Consume **only** existing approved Woo plugin/browser privileged REST interfaces and existing hosted API responses where implemented. Confirm the exact reachable contract from inspected source before wiring it.
- Do not create cross-repository DTOs or silently invent an `ARCH-035-API-*` prerequisite. If required data/action is unavailable, record an external dependency and keep production state truthful.
- UI fixture interfaces are local tests only; no fixtures enter the production bundle as merchant data.

## Dependencies

- `ARCH-035-WOOCOMMERCE-003` (architect-accepted Complete)

## Enables

- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Section is placed within Recovery Settings alongside store/assistant context, not an unapproved top-level page.
- [ ] Plan limits, processing/failure, reorder, refresh and edit controls have truthful disabled/loading/error states.
- [ ] Drag/drop or file selection cannot send data to arbitrary cloud endpoints or claim success without server acknowledgement.
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
| Recovery settings > Store and assistant context                               |
+-------------------------------------------------------------------------------+
| Merchant Knowledge                         Sources: [used] / [plan limit]       |
| [Add website / URL v]                       [Upload CSV / XLSX v]                |
| URL source:  Name [                 ]   Purpose [                v]             |
|              URL  [https://...                                  ] [Add / off]  |
+-------------------------------------------------------------------------------+
| Sources                                                                       |
| +-------------------------------------------------------------------------+   |
| | [URL] [Source name]     READY       Language: en-GB                  |   |
| | [Move up/down] [Refresh] [Edit] [Delete]                              |   |
| +-------------------------------------------------------------------------+   |
| | [FILE] [Source name]     PROCESSING   [Replace when available]        |   |
| +-------------------------------------------------------------------------+   |
| | [URL] [Source name]     FAILED       [Retry when available]         |   |
| +-------------------------------------------------------------------------+   |
| [Empty / Processing / Error / No entitlement / Integration unavailable]         |
+-------------------------------------------------------------------------------+
```

## Completion Report

### Status

Developer takeover recorded — Attempt 0 remains unclaimed until canonical worktree preparation and dependency verification succeed.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The portable definition is materialised on the canonical parent task branch. Attempt 0 is not claimed; any missing hosted API capability remains external to ARCH-035 and may require a separate architecture.

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
