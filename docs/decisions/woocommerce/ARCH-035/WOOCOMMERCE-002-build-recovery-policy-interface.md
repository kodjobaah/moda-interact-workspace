---
id: ARCH-035-WOOCOMMERCE-002
architecture_id: ARCH-035
title: Match Shopify recovery-policy settings layout and controls
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-003
  - ARCH-035-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-WOOCOMMERCE-002: Match Shopify recovery-policy settings layout and controls

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: `moda-interact-workspace(20261011-192347).zip`; portable definition, not a materialised parent/implementation task branch.

## Objective

Bring the existing Woo Recovery Settings policy section to Shopify visual and interaction parity without implementing policy storage or a new backend command.

## Context

Shopify RecoverySettingsView.tsx displays an effective-policy summary, admin-override notice and offer/delay/follow-up sections; current Woo recovery-settings-screen.js provides store category and read-only effective summary.

Source references:
- Shopify: app/routes/app/recovery-settings/RecoverySettingsView.tsx.
- Woo: src/recovery-settings/recovery-settings-screen.js; src/recovery-settings/recovery-effective-summary.js.

## Scope

- Preserve existing Store Category selector and effective-summary reads, then compose Shopify-style effective delay/offer/follow-up cards and policy form.
- Show current values and inline validation for delay/follow-up; distinguish saved state from unsaved local edits.
- Show offer modes only as supported/unsupported provider capabilities: never offer selectable ShopifyDiscount references or unverified Woo coupon workflows.
- Submit through an existing approved Woo merchant settings endpoint only if present; otherwise disable Save with an explicit integration-unavailable explanation; document missing write contract.

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

- [ ] Inspect and map source UI: Shopify: app/routes/app/recovery-settings/RecoverySettingsView.tsx.
- [ ] Implement the bounded UI using separate presentation, controller/state, and supported transport modules.
- [ ] Add fixture-driven component tests for primary, empty, loading, unavailable, denied and error states.
- [ ] Provide 20-locales native gettext translation assets and WordPress keyboard/responsive checks.
- [ ] Document any unsupported hosted API operation as a gap; never implement or fake a new backend service.

## Interfaces / Contracts

- Consume **only** existing approved Woo plugin/browser privileged REST interfaces and existing hosted API responses where implemented. Confirm the exact reachable contract from inspected source before wiring it.
- Do not create cross-repository DTOs or silently invent an `ARCH-035-API-*` prerequisite. If required data/action is unavailable, record an external dependency and keep production state truthful.
- UI fixture interfaces are local tests only; no fixtures enter the production bundle as merchant data.

## Dependencies

None. Task is Ready as a **UI-only** implementation; it does not certify underlying API functionality.

## Enables

- `ARCH-035-WOOCOMMERCE-003`
- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Effective values, override notice, section order and validation presentation follow the Shopify reference.
- [ ] Disabled save/modes clearly explain unsupported capability, not a fake success.
- [ ] Store category selection remains functional and regression tested.
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
| Moda Interact > Recovery settings                              [Refresh]     |
+-------------------------------------------------------------------------------+
| Effective policy                                                              |
| +---------------------+ +---------------------+ +-------------------------+ |
| | First outreach      | | Recovery offer      | | Follow-up               | |
| | [effective delay]   | | [effective mode]    | | [effective delay/state] | |
| +---------------------+ +---------------------+ +-------------------------+ |
| [Administrative override notice when applicable]                              |
+-------------------------------------------------------------------------------+
| Recovery behaviour                                                             |
| 1. Offer mode   (o) None  ( ) Fixed*  ( ) AI*   *Disabled if unsupported       |
| 2. First outreach delay       [ value ] [unit]                                 |
| 3. Follow-up       [toggle]  Delay [ value ] [unit]                            |
| [Inline error / revision conflict]                     [Save policy / locked] |
+-------------------------------------------------------------------------------+
| Store and assistant context                                                    |
| Store category: [selected category]          [Change / Save category]          |
| [Existing category mappings]                                                   |
| [Conversation features section - separate task 003]                            |
| [Merchant Knowledge section  - separate task 004]                              |
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
