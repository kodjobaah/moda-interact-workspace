---
id: ARCH-026-WOOCOMMERCE-014
architecture_id: ARCH-026
title: Validate all twenty languages and release-ready WooCommerce translation assets
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 43
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-WOOCOMMERCE-010
  - ARCH-026-WOOCOMMERCE-011
  - ARCH-026-WOOCOMMERCE-012
  - ARCH-026-WOOCOMMERCE-013
enables: []
created: 2026-10-09
updated: 2026-10-09
---

# Validate all twenty languages and release-ready WooCommerce translation assets

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Make full 20-locale WordPress merchant-UI translation coverage an automated production packaging and integration requirement.

## Context

WOO-009 defines the pipeline, and WOO-010 through WOO-013 author its complete locale corpus. This task is the release gate: partial translations must never be presented as equivalent to Shopify’s 20-language support.

## Scope

- Validate 20 supported catalogue locales and English source fallback, covering native sidebar, Overview, Billing, Recovery Settings, connection, category and recoverable errors.
- Exercise PHP `.mo` and WordPress JavaScript translation loading in disposable WordPress with different admin and store languages.
- Verify region/script aliases including `pt_BR` vs `pt_PT` and `zh_CN` vs `zh_TW`, placeholder/plural safety and unsupported-locale English fallback.
- Update production ZIP packaging verification so every required translation asset is present, version-compatible and loaded with the actual bundled JS asset.
- Prove language switching does not mutate Shop international context, category, subscription or lifetime credits.

## Out of Scope

- Adding a bespoke language picker or changing native WordPress user language controls.
- Translating customer WhatsApp responses, LLM prompts or changing CommerceAgent language authority.
- Changing API/database, billing/categorization business logic or Shopify’s existing messages.

## Requirements

- The installed plugin—not merely the source tree—renders translated labels, notices, errors and commands for all twenty supported catalogue languages.
- All translations are shipped inside `moda-interact.zip`, with no runtime dependency on Shopify catalogue files or a translation API.
- Unsupported locale and missing string behavior is safe and bounded, without altering the underlying store locale.
- Locale-change tests establish separate admin and store language semantics and confirm no business-state writes.

## Work Items

- [ ] Enable strict whole-corpus translation coverage gate for all current PHP/React source keys.
- [ ] Verify bundled PHP `.mo` and JavaScript JSON hash/catalogue lookup in installed WordPress environment.
- [ ] Validate installed plugin and historical upgrade retaining connection/category/billing state.
- [ ] Add a focused release-evidence report with per-language coverage and actual WordPress smoke tests.

## Interfaces / Contracts

- Consumes complete assets from WOO-010, WOO-011, WOO-012, WOO-013.
- WordPress installed-plugin locale APIs and existing `moda-interact` gettext/script domain.

## Dependencies

- `ARCH-026-WOOCOMMERCE-010`
- `ARCH-026-WOOCOMMERCE-011`
- `ARCH-026-WOOCOMMERCE-012`
- `ARCH-026-WOOCOMMERCE-013`

## Enables

None

## Acceptance Criteria

- [ ] The locale coverage manifest reports 20/20 with no missing user-facing keys or unsafe substitutions.
- [ ] A disposable WordPress admin verifies independent user/store language behavior with 20 supported coverage and region variants.
- [ ] Complete plugin ZIP contains required language assets and passes packaging integrity, install and upgrade checks.
- [ ] Translation does not change Shop state, category selection, Free credits or authorization.

## Validation

- [ ] Full JS/PHP tests, lint and build relevant to localization.
- [ ] WordPress integration tests with a multi-locale admin/store matrix.
- [ ] `npm run plugin-zip` with translation-pack and asset-path validation; clean-install and upgrade evidence.

## Stop Condition

After Work Items, Acceptance Criteria and the scoped Validation pass, set the task to `review`, submit the Completion Report to `moda_architect`, and STOP. Do not begin enabled tasks.

## Implementation Notes

This is validation/production-packaging implementation work, not an npm package publication or Woo Marketplace submission. Do not weaken coverage thresholds or add a fallback that claims untranslated strings are covered. System-test tasks, if later required for cross-service language behavior, must remain terminal and depend on this implementation task.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
