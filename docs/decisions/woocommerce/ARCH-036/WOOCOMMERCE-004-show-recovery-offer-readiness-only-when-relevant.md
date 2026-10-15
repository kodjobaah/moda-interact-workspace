---
id: ARCH-036-WOOCOMMERCE-004
architecture_id: ARCH-036
title: Scope coupon loading and display provider-identifiable Woo coupons
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-API-004"]
enables: []
created: 2026-10-15
updated: 2026-10-15
---

# ARCH-036-WOOCOMMERCE-004 — Mode-scoped UX with merchant-controlled coupon selection

## Architecture

- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Bounded follow-up to `ARCH-036-WOOCOMMERCE-003`, using the corrected settings-read contract from `ARCH-036-API-004`.
- Owner: `moda_woocommerce`, repository `moda-interact-woocommerce`; coordinator: `moda_architect`.
- Portable definition only; not materialised or claimed. Do not claim until the API-004 dependency is accepted.

## Observed defect

The Woo Recovery Settings screenshot shows **Do not offer a discount** selected, followed by `WooCommerce coupon selection is not yet available.` and an unexplained **Refresh** button with a large empty coupon pane and disabled actions. This is misleading when the merchant has deliberately selected `NONE`. API-002 previously refused the independent offer-settings GET when the catalogue was ERROR; API-004 removes that coupling. The presentation must also respect the selected mode.

## Objective

Render one clear Recovery Offer configuration UI that shows only the controls and error/loading states relevant to the **draft mode**. NONE and AI modes must not imply that the merchant needs a coupon catalogue refresh. FIXED must show real multi-select controls for **all identifiable, code-usable Woo coupons returned by API-004**, without treating expiry, usage, amount or unknown discount type as Moda-made selection restrictions. WooCommerce decides redemption validity.

## Required behaviour

1. **NONE**: show the selected mode card and a concise no-discount explanation; do not render coupon list, coupon loading state, coupon error, or coupon **Refresh** button. If persisted NONE matches the draft, Save/Discard stay disabled because there is nothing to save; if the merchant changed from another saved mode, Save becomes enabled even if coupon GET is unavailable.
2. **AI_BEST_APPLICABLE**: show mode configuration and a concise explanation that this only saves preferences (no CommerceAgent/offer-execution claim). No coupon checkbox list or catalogue Refresh required for this mode; provide Save/Discard when dirty.
3. **FIXED**: render bounded search, accessible multi-checkbox list, pagination and count from the API coupon catalogue via the existing privileged WordPress proxy; show a clear `Waiting for coupon synchronisation` or `Coupon catalogue unavailable` state and a **Retry coupons** control only when list loading fails or readiness is missing. An authentically empty catalogue is distinct from a failing catalogue. Do not hide or disable an otherwise deliverable coupon merely because its Woo type is unknown, amount zero, expired, exhausted or restricted.
4. **State isolation**: load saved offer preferences using API-004 independently of the coupon-list query. A coupon-list `503` must not replace the saved NONE/AI mode with an unavailable state or disable changing mode. Do not show a generic `WooCommerce coupon selection is not yet available` banner under NONE.
5. **Manual Save**: preserve staged mode/checkbox edits and full selected-ID set across filters/pages; Save only on explicit action with duplicate-click prevention. FIXED with zero checked coupon rows has inline validation. Do not preselect a coupon without merchant action. After a failed Save preserve draft and report the error; Cancel restores persisted settings. A non-current list should block choosing NEW FIXED items, not reintroduce business eligibility validation in API PUT. Do not lose saved selected IDs just because coupon metadata or catalogue status changes.
6. **Preserve UX**: keep the existing two-stage WordPress navigation `WooCommerce > Moda Interact` entry and active `Moda Interact > Recovery settings` submenu; keep Recovery start, No-response follow-up, Store Category and existing recovery-policy controls unchanged. Do not create a second Recovery Offer section.
7. **Transparent status, no merchant veto**: optionally display Woo expiry/usage/type metadata as **information**, never as a disabled checkbox or an invented claim that the provider coupon is invalid. Clearly explain that WooCommerce validates coupon redemption. Treat a coupon missing a safely deliverable code as a technical sending problem, not an unsupported discount type; never truncate a provider code to fit UI.
8. **Localise** all added/changed copy through WordPress native i18n in all 20 supported locales. Update POT/PO/compiled release assets and strict message-count tests to actual extracted source, without bypassing the 20-locale gate.

## ASCII page states

```text
WordPress Admin > WooCommerce > Moda Interact
  > Moda Interact > Recovery settings
+----------------------------------------------------------------------+
| 1  Recovery offer                                                    |
|                                                                      |
| (o) No discount    ( ) Specific discount    ( ) AI-selected          |
|                                                                      |
| No discount will be offered.                                         |
|                                    No changes to save                |
+----------------------------------------------------------------------+

When FIXED is selected and current:
+----------------------------------------------------------------------+
| ( ) No discount    (o) Specific discount    ( ) AI-selected          |
| Search coupons [____________________] [Search]                       |
| [x] SAVE10          10%                 (merchant selected)          |
| [ ] SAVE20          custom Woo type     (not selected)             |
| [Previous]              Page 1 of N           [Next]                 |
| 1 selected                        [Discard] [Save recovery offer]     |
+----------------------------------------------------------------------+

When FIXED is selected but catalogue unavailable:
+----------------------------------------------------------------------+
| ( ) No discount    (o) Specific discount    ( ) AI-selected          |
| Coupons are not ready. Synchronisation is pending or unavailable.    |
| [Retry coupons]                                                       |
| You can still select No discount or AI-selected mode.                |
+----------------------------------------------------------------------+
```

## Scope and exclusions

- Only WooCommerce plugin React controller/component/presentation, privileged WordPress proxy if required for error differentiation, styling, native translation assets and focused tests.
- No changes to Background, API, Prisma, Shopify, CommerceAgent, billing, coupon redemption or outbound recovery; no `_index.md` changes.
- Do not add duplicate menu entries or move the canonical two-stage navigation.

## Acceptance criteria

- [ ] When **NONE** is saved, there is no coupon Refresh button, coupon-unavailable warning, empty placeholder box, or demand for catalogue readiness.
- [ ] Changing NONE -> AI and back enables/disables Save based only on real edits even when coupon catalogue GET fails.
- [ ] FIXED with CURRENT catalogue presents all provider-identified, code-usable Woo rows including unchecked ones, regardless of type/amount/expiry/usage, with persistent selection across page/search and manual Save/Cancel.
- [ ] FIXED with non-current catalogue shows one actionable inline readiness message and a scoped Retry control, never an unexplained global Refresh button.
- [ ] Good/empty catalogue, network error, permission error, 409, 503, reset, double clicks and changed-in-background scenarios have deterministic user-visible outcomes; unknown type, zero amount, expired/exhausted and >255-character code have focused rendering/checkbox tests.
- [ ] No regression in 20 locale support, mobile layout, current WordPress navigation, or unrelated recovery-policy controls.

## Required validation

- [ ] React controller/component state tests covering NONE/AI/FIXED with current and unavailable catalogue responses, page changes, checkbox and discard; assert no API writes until Save. Include expired/exhausted/zero/unknown-type Woo coupons that remain selectable, and full-length long-code safe rendering.
- [ ] PHP WordPress proxy tests for authenticated calls and distinct error statuses; no browser-to-hosted secrets.
- [ ] `npm run i18n:verify:20`, `npm run test:js`, `npm run test:php`, JS/CSS/PHP lint, production build, plugin ZIP audit, `git diff --check`.
- [ ] Manual LocalWP screenshot/interaction evidence for desktop and narrow viewport, with catalog CURRENT and ERROR, including both WordPress menu stages.

## Stop condition

After bounded validated work, submit the developer Completion Report and mark this task `review`; return to `moda_architect`. No dependent-task execution, incidental refactors or `_index.md` edits.

## Completion Report

### Status

Not started; portable definition only.

### Files Changed

None in application source.

### Work Completed

None.

### Validation Results

Not run by implementation executor.

### Deviations

None recorded.

### Unresolved Issues

None yet.

## Architect Review

### Review Status

Pending implementation evidence.
