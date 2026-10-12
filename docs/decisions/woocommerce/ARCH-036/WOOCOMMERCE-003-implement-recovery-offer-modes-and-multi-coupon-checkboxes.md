---
id: ARCH-036-WOOCOMMERCE-003
architecture_id: ARCH-036
title: Implement three offer modes and multi-coupon checkbox UI
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-API-002", "ARCH-036-WOOCOMMERCE-002"]
enables: ["ARCH-036-BACKGROUND-003", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-WOOCOMMERCE-003 — Implement three offer modes and multi-coupon checkbox UI

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Replace the preview-only controls with a real three-mode Recovery Offer editor, where FIXED permits multiple Woo coupons via checkboxes.

## Context

ARCH-035-WOOCOMMERCE-011 contains a read-only coupon preview. The user corrected the intended interaction: NONE offers no coupon, FIXED allows merchant-selected checkboxes, AI considers applicable current coupons. Only one coupon is ever offered per recovery.

## Scope

Modular React Recovery Offer radio cards, accessible multi-checkbox catalogue, filter/pagination with retained selections, preview of chosen set, Save/Cancel and conflict feedback. Add a privileged WordPress REST proxy to API-002; reuse the existing Woo coupon list styling, category/settings flow and native WordPress menus. Update all 20 merchant locales.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Top-level mode cards mutually exclusive. When FIXED, show only selectable coupons as checkboxes, preserve selected IDs across pages/search/reload until explicit Save, warn on unavailable selections. NONE/AI show no selected-set checkboxes; AI description promises only verifiably applicable offers. No second independent radio group; no direct React-to-hosted API calls, no storing of secrets or selection in browser storage. Save uses `expectedRevision` and leaves drafts on 400/409/503. Prevent double clicks. Respect mobile responsive layout.

## Work Items

- [ ] Implement mode state and paginated checkbox selection in modular components.
- [ ] Wire WordPress REST proxy, controller, CAS save and safe failure feedback.
- [ ] Preserve selected IDs during filtering/pagination and clear correctly when switching modes.
- [ ] Add 20-language translations and responsive/keyboard tests.

## Interfaces / Contracts

Privileged WordPress REST GET/PUT proxy to API-002; provider-neutral Shared v1 DTO via validated browser projection; current ARCH-035 `recovery-behaviour` controls remain as-is.

## Dependencies

- `ARCH-036-API-002`
- `ARCH-036-WOOCOMMERCE-002`

## Enables

- `ARCH-036-BACKGROUND-003`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] NONE disables coupon selection/use; FIXED shows checked set; AI shows applicable-catalogue explanation.
- [ ] Changing mode without saving leaves stored configuration unchanged.
- [ ] Saved choices remain after page reload, with explicit unavailable-state warnings.
- [ ] Accessible mobile controls, active WordPress submenu, independent delay/follow-up saving unaffected.
- [ ] No customer-facing coupon promise until runtime proof gate is complete.

## Validation

- [ ] Woo React controller/component tests, PHP proxy and nonce tests, end-to-end LocalWP review
- [ ] 20-language i18n + eslint/stylelint/build/plugin-zip and `git diff --check`

## Implementation Notes

Do not put API calls in presentation components. Keep the existing `WOOCOMMERCE-011` preview work as historical UI foundation.

For developer execution, use the canonical `/moda_developer_create ARCH-036-WOOCOMMERCE-003` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-WOOCOMMERCE-003`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

## ASCII Page Design

```text
Recovery Settings — Recovery Offer
+------------------------------------------------------------------+
| (o) No discount   ( ) Specific discount   ( ) AI-selected         |
|                                                                  |
| When Specific discount is active:                                |
| Search coupons [______________________] [Search]                 |
| [x] SAVE20       GBP 20.00       Supported                       |
| [x] WELCOME10    10%             Supported                       |
| [ ] OLD25        25%             Expired (disabled)             |
| [Previous]             Page 1 of 3                  [Next]        |
| 2 coupons permitted; ONE applicable coupon chosen per recovery    |
|                                                  [Save selection] |
+------------------------------------------------------------------+
| Recovery start and follow-up stay in their existing panels.      |
+------------------------------------------------------------------+
Mobile: radio cards stack; checkboxes remain labels in single-column rows;
selection persists while paging and search results change.
```

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

The implementation executor will verify local checkout, dependencies and available toolchain at claim time.

### Unresolved Issues

None recorded by an implementation executor.

### Architectural Concerns

Report schema, cross-service or provider-proof deviations to `moda_architect` instead of silently expanding scope.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only, not implementation acceptance.

### Reviewed Files

Current 12 October 2026 source snapshot used to define ownership; implementation not yet reviewed.

### Validation Reviewed

None from this task.

### Architecture Conformance

To be determined after implementation inspection.

### Follow-up

Await canonical materialisation, execution and review.
