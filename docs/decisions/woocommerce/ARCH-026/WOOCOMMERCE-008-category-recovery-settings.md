---
id: ARCH-026-WOOCOMMERCE-008
architecture_id: ARCH-026
title: Expose Shopify-parity Store Category controls in Woo Recovery Settings
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 37
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-WOOCOMMERCE-007
  - ARCH-026-API-005
  - ARCH-026-API-006
enables: []
created: 2026-10-09
updated: 2026-10-09
---

# Expose Shopify-parity Store Category controls in Woo Recovery Settings

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Give connected WooCommerce merchants a real `Recovery Settings -> Store & assistant context -> Store category` selection experience matching Shopify's category controls, without a Woo plan-selection step.

## Context

The LocalWP merchant already has connected installation, automatically active Free subscription, five lifetime credits and working store-context synchronization (API-004/WOO-007). The Woo merchant Overview currently presents Store Profile read-only, while Shopify's Recovery Settings provides an editable Store Category section and optional taxonomy mapping choices. Add this UI behind existing Woo installation credentials, consuming the API-005 read and API-006 mutation contracts; don't implement a Woo-specific taxonomy or reinterpret `onboardingCompleted`.

## Scope

`moda-interact-woocommerce` only:

- Add `Recovery Settings` navigation/section to the connected Moda Interact Woo Admin screen, aligned with Shopify's information architecture. Under `Store & assistant context`, provide a `Store category` disclosure or panel showing active/pending category, localized description, mapping choices, provenance/pending status and explicit Save/update action.
- Add PHP Moda API client support for authenticated GET category/profile and POST mutation requests, and privileged WordPress REST proxy endpoints with bounded/strict input validation and existing site URL/credential continuity checks.
- Add small, focused JS selection/read controllers and a translatable accessible view: separate read loading, saving, empty, conflict, success and retryable unavailable states; refresh category read and existing bootstrap Overview on success.
- Add focused PHP/JS/WordPress integration tests and validate updated installable ZIP in LocalWP.

## Out of Scope

- Replacing the working Connect/Free activation or Woo store-context sync; selecting a paid plan.
- Editing recovery timing, WhatsApp automations, feature preferences or Merchant Knowledge in this category-only task; no inert settings toggles.
- Category creation, deletion, automatic detection from Woo product taxonomy or direct database access from WordPress.
- Shipping Shopify React Router components inside WordPress, or exposing installation tokens to JavaScript.
- Database schema changes, new Backend workers or billing/entitlement updates.

## Requirements

- Present a clearly named Recovery Settings section available to connected Woo admins; match Shopify's conceptual hierarchy and active/pending/profile terminology while using native WordPress UI conventions and the `moda-interact` text domain.
- Distinguish initial category `Not selected` from a failed/no-category service; account onboarding and active Free plan do not need to be reset or changed.
- Display enabled selectable localized category names/descriptions and optional mappings from API-005, preserve selected IDs and `pendingSelectionGeneration`, and send an explicit administrator-initiated Save via API-006.
- Only privileged WordPress REST calls with `manage_woocommerce` and normal cookie/nonce protection can read/mutate category state. PHP derives the installation principal/credential; no `shopId`, token or API endpoint controlled by browser input. Enforce server-side site URL continuity.
- Use current administrator UI language for displaying translated category options, independent of Woo site language; fallback according to Shopify category localization semantics. Existing store locale synchronization is unaffected.
- API conflict (409) prompts refresh/reselect rather than automatic overwrite; unavailable category/template or network error shows bounded feedback, leaves previous active state intact, and supports explicit retry.
- A successful initial Save on a Free Shop must show **Active category** immediately (not pending until another billing event), and re-read the existing Overview. Later changes must display the new active category, persisted mappings and pending/provenance correctly.
- GET/page load and reconnect must not auto-select, auto-publish or charge credits; do not regress HPOS compatibility, plugin navigation, established connection or store-context sync.

## Work Items

- [ ] Add bounded server-side PHP client/proxy for API-005 and API-006 with capability, nonce and credential checks.
- [ ] Add connected Recovery Settings view and Shopify-parity Store Category summary, selector and optional mapping controls.
- [ ] Wire strict generation CAS mutation and reconciliation/readback with clear async state and errors.
- [ ] Add focused PHP/JS/WordPress integration tests and verify production ZIP replacement in LocalWP.

## Interfaces / Contracts

- API-005: `GET /v1/merchant/store-categories` hosted authenticated category/profile catalogue.
- API-006: `POST /v1/merchant/store-category` hosted authenticated generation-checked category selection and activation.
- Local privileged PHP facade: `GET /wp-json/moda-interact/v1/merchant/store-categories` and `POST /wp-json/moda-interact/v1/merchant/store-category`, consuming the above exact OpenAPI contracts. Browser never talks directly to hosted API.
- Existing API-003 bootstrap GET remains the Overview readback. Existing API-004/WOO-007 context-sync routes remain unchanged.

## Dependencies

- `ARCH-026-WOOCOMMERCE-007` — must be architect-accepted Complete so this builds on current Woo Admin and store-context layout.
- `ARCH-026-API-005` — category/profile read contract Complete.
- `ARCH-026-API-006` — category selection/activation contract Complete.

## Enables

None. Integrated system validation follows accepted implementation dependencies; it must not gate implementation.

## Acceptance Criteria

- [ ] Connected Woo admin sees Recovery Settings -> Store & assistant context -> Store category, same conceptual controls as Shopify; no plan-selection step or Shopify-specific branding.
- [ ] Category dropdown/optional mappings and localized descriptions reflect the canonical selectable category catalogue, not Woo product categories.
- [ ] Initial explicit Save on the LocalWP Free merchant sets active category and published prompt; Overview refresh reflects it while Free credit remaining stays five.
- [ ] Changing active category/mappings works once, with correct CAS generation, provenance/readback; stale second browser returns conflict and can refresh.
- [ ] A non-privileged WP user, missing/invalid REST nonce or changed installation site URL cannot access a mutable category endpoint.
- [ ] Connection/credential, subscription, lifetime credits, HPOS/nav and context sync remain unchanged when category selection succeeds, fails or API is offline.
- [ ] No category mutation occurs on GET, Connect or ordinary page load, and UI displays errors without exposing secret values.

## Validation

- [ ] `composer lint` and `composer test`.
- [ ] `npm run lint:js`, `npm run test:js` and `npm run build`.
- [ ] `npm run test:integration:wordpress` against disposable WP/Woo test environment when available.
- [ ] `npm run plugin-zip` and controlled LocalWP in-place upgrade with real API-005/006 calls, including unauthorised/CAS/outage cases.
- [ ] `git diff --check`, ZIP safety audit and canonical task worktree/synchronization evidence in Completion Report.

## Stop Condition

After satisfying bounded work, acceptance and validation, set task to review, submit Completion Report to `moda_architect` and STOP. Do not add unrelated Recovery Settings features.

## Implementation Notes

Keep PHP REST/action, remote API transport, JS controller and UI components small and separate; do not accumulate a catch-all `page.js` or test fixture. Use existing Woo Admin CSS/scoping and WordPress `@wordpress/i18n`; preserve current `Overview` and `Sync store settings` controls. Merchant must remain eligible for category setup even after onboardingCompleted is already true.

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

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
