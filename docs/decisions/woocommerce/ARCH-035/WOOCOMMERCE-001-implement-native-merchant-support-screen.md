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
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-16T12:24:22Z
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
- Task state: `in_progress`, `execution_mode: developer`, `completion_mode: developer`; Attempt 1 was claimed after the launcher re-gated the live dependency.

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

- [ ] Inspect and map source UI: Shopify: app/routes/app/merchant-support/route.jsx.
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

- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Thread ordering, pagination, message kinds, translated/original switching and 500-grapheme validation match the Shopify interaction model.
- [ ] Duplicate clicks cannot create duplicate UI submits; stale responses after reconnect/disconnect are not applied.
- [ ] No Shopify-only refund action, invented send acknowledgement or message persisted in browser storage.
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

In Progress — Attempt 1 claimed by developer at 2026-10-16T12:24:22Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The task is materialised and its developer takeover is recorded. Any missing hosted API capability is external to ARCH-035 and may require a separate architecture.

### Unresolved Issues

No backend capability is asserted by this UI-only task. Document discovered API gaps in the completion report.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.


**Architect reconciliation (2026-10-16):** Native navigation prerequisite WOOCOMMERCE-012 is now Complete. Support remains a placeholder. Status promoted from Pending to Ready after dependency reconciliation. No source code was changed by this promotion.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Return to architect for UI review and source comparison.
