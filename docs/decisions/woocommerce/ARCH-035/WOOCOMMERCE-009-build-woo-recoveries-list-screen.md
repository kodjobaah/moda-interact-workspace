---
id: ARCH-035-WOOCOMMERCE-009
architecture_id: ARCH-035
title: Build native Woo Recoveries list UI
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-WOOCOMMERCE-012
enables:
  - ARCH-035-WOOCOMMERCE-013
  - ARCH-035-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-035-WOOCOMMERCE-009: Build native Woo Recoveries list UI

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: `moda-interact-workspace(20261011-192347).zip`; portable definition, not a materialised parent/implementation task branch.

## Objective

Replace the native Woo Recoveries placeholder with the Shopify-parity filterable recovery list (detail in task 013).

## Context

Shopify RecoveryList.tsx renders date presets, from/to range, search, status filter, tenant time zone, paginated recovery rows and explicit never-used/empty/error states. Woo has no real Recoveries screen.

Source references:
- Shopify: app/routes/app/recoveries/RecoveryList.tsx; app/routes/app/recoveries/recovery-list-state.ts.
- Woo: includes/Admin/NativeNavigation.php.

## Scope

- Implement Recoveries list shell with Today/Week/Month/Custom, date range, search, status, Apply, Clear and Refresh.
- Render customer, status, detected timestamp, recovery value where authoritative and row navigation to Recovery Detail.
- Use an existing approved recovery read only when available, else explicitly show unavailable and no fabricated customer/order/revenue data.
- Preserve filter context and cursor/page behaviour across refresh and detail/back navigation.

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

- [ ] Inspect and map source UI: Shopify: app/routes/app/recoveries/RecoveryList.tsx; app/routes/app/recoveries/recovery-list-state.ts.
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

- `ARCH-035-WOOCOMMERCE-013`
- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Search/date/status filters, date bounds, timezone and pagination match Shopify layout semantics.
- [ ] Never-used, filtered empty, loading, invalid-filter, denial and error states are distinct.
- [ ] Recovery list does not implement checkout detection, order ingest or background processing.
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
| Moda Interact > Recoveries                                         [Refresh]  |
| Browse recovery activity for your store.                                       |
+-------------------------------------------------------------------------------+
| [Today] [7 days] [30 days] [Custom]                                            |
| From [date]  To [date]  Search [customer/email]  Status [All v]  [Apply]        |
| Timezone: [store timezone]                                  [Clear filters]    |
+-------------------------------------------------------------------------------+
| Customer               Status          Detected           Recovered value     |
| [real customer]        [status]        [date/time]        [amount or --]      |
| [real customer]        [status]        [date/time]        [amount or --]      |
| [Previous]                                           Page n/N        [Next]    |
+-------------------------------------------------------------------------------+
| [Never used / No results / Loading / Invalid filters / Unavailable / Error]    |
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

Accepted — retrospective code-based review, 16 October 2026.

### Review Notes

Real recoveries list with form filters, bounded server pagination, privileged WP read proxy and empty/error states.

This is a **retrospective, source-code-based architectural reconciliation** against the developer-provided 2026-10-16 10:58:55 workspace ZIP. The source snapshot is not the historical paired task worktrees or Git branches; an original launcher packet, accepted task commit, Completion Report validation and LocalWP run cannot be reconstructed from it. Retain `attempt: 0` and the original developer/agent Completion Report; no historical execution claim or test pass is manufactured.

### Reviewed Files

- `moda-interact-woocommerce/src/recoveries/{recoveries-screen.js,recoveries-controller.js}`
- `moda-interact-woocommerce/src/recoveries/{api,filters,list,states}/`
- `moda-interact-woocommerce/includes/Rest/RecoveryListController.php`
- `moda-interact-woocommerce/tests/js/{recoveries-shell.test.js,recoveries-controller.test.js,recoveries-client.test.js}`

### Validation Reviewed

This session directly passed `npm run test:i18n` (28 tests) and `npm run i18n:verify:20` (332 current PHP/React gettext strings, 19 translation packs / 20 canonical locales). Related Woo PHP controller and native navigation files passed `php -l`. JS component/integration tests and API TypeScript test cases were inspected as source, but `node_modules` are absent from the ZIP and their execution, PHP integration, LocalWP browser evidence, production build, package ZIP, disposable PostgreSQL proof and launcher worktree verification were **not** run in this session.

### Architecture Conformance

The inspected implementation provides the task's bounded capability and uses the approved architecture/repository boundary. The source-based reconciliation is not a claim of unobserved runtime validation, task worktree isolation or release certification.

### Follow-up

Continue normal work only for other, incomplete ARCH-035 tasks. The terminal SYSTEM-TEST-001 remains blocked until every required UI implementation is Complete.
