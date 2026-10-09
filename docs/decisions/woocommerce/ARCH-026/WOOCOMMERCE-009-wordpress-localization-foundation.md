---
id: ARCH-026-WOOCOMMERCE-009
architecture_id: ARCH-026
title: Establish WordPress-native twenty-language localization pipeline
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 38
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-WOOCOMMERCE-008
enables:
  - ARCH-026-WOOCOMMERCE-010
  - ARCH-026-WOOCOMMERCE-011
  - ARCH-026-WOOCOMMERCE-012
  - ARCH-026-WOOCOMMERCE-013
created: 2026-10-09
updated: 2026-10-09
---

# Establish WordPress-native twenty-language localization pipeline

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Establish deterministic, reviewable WordPress PHP/React translation generation and locale selection, without claiming translation coverage before the locale packs exist.

## Context

Shopify has 20 complete ICU message catalogues. WooCommerce already marks PHP and JavaScript strings with the `moda-interact` text domain, uses `load_plugin_textdomain` and `wp_set_script_translations`, and ships only an English `.pot` template. The canonical WordPress administrator locale and separate store locale must stay distinct.

## Scope

- Audit all current native sidebar, connected screens, connection, billing, category and error strings for translation extraction.
- Implement source-only `.pot` extraction and reproducible `.po` to `.mo` and WordPress JavaScript JSON compilation with predictable asset names.
- Define a tested translation-coverage manifest for `en` and the nineteen other Shared/Shopify-supported catalogue languages, including WordPress locale aliases.
- Add build-time validation of native locale resolution and JS script translation registration, without rejecting unsupported WordPress provider locales.
- Add focused unit tests and a small disposable WordPress fixture exercising separate administrator and store locale.

## Out of Scope

- Authoring all translations; that belongs to WOO-010 through WOO-013.
- New custom user language settings, direct Shopify runtime imports in PHP, or a second JavaScript i18n framework.
- Changing hosted API, persisted Shop locale, CommerceAgent or WhatsApp language, billing, category selection or subscription logic.

## Requirements

- WordPress user interface language takes precedence; site locale is fallback, without rewriting store context.
- Supported translation coverage is exactly the canonical set of twenty, not a rejection/normalization allowlist for input locales.
- English source strings use gettext-compatible contexts, pluralization and printf placeholders.
- Script and PHP translations can be loaded from shipped assets; no network dependency on Shopify in the plugin at runtime.
- A source translation-key change fails coverage validation after the full locale-pack gate becomes active, with a bounded bootstrap stage during this task.

## Work Items

- [ ] Audit existing translatable strings and native menu; fix non-translatable literals within current scope.
- [ ] Implement and test localized asset generation from WordPress source messages.
- [ ] Implement locale alias/selection tests for `fr_FR`, `pt_BR`, `pt_PT`, `nb_NO`, `zh_CN`, `zh_TW` plus unsupported fallback.
- [ ] Document the contract required by WOO-010 to WOO-013 translation batches.

## Interfaces / Contracts

- WordPress PHP `moda-interact` text domain, `load_plugin_textdomain`, PHP `__` / `_n` / `_x`.
- WordPress JavaScript `@wordpress/i18n` and `wp_set_script_translations`.
- Canonical language coverage metadata from existing Shared/Shopify supported locale set; no new cross-service runtime contract.

## Dependencies

- `ARCH-026-WOOCOMMERCE-008`

## Enables

- `ARCH-026-WOOCOMMERCE-010`
- `ARCH-026-WOOCOMMERCE-011`
- `ARCH-026-WOOCOMMERCE-012`
- `ARCH-026-WOOCOMMERCE-013`

## Acceptance Criteria

- [ ] Reproducible source-only POT/PO/MO/JS pipeline, with no generated `build/` code polluting message extraction.
- [ ] Locale selection is user-UI-scoped, preserves store language, and safely falls back to English for unsupported locales.
- [ ] WordPress can load a generated PHP and JS sample translation using the plugin text domain.
- [ ] No new browser secrets, remote translation service, or changes to merchant business state.

## Validation

- [ ] `npm run lint:js` and existing focused JavaScript tests.
- [ ] Focused PHP and WordPress admin/user-locale tests.
- [ ] Source i18n extraction/asset generation tests and `npm run build`.

## Stop Condition

After Work Items, Acceptance Criteria and the scoped Validation pass, set the task to `review`, submit the Completion Report to `moda_architect`, and STOP. Do not begin enabled tasks.

## Implementation Notes

Use WordPress gettext/native translation loading for the browser and PHP. Existing Shopify ICU JSON messages are a translation-memory input only: never copy `{var}` ICU syntax blindly into gettext `%s` fields. Defer *full* twenty-pack enforcement to WOO-014 so this infrastructure task remains independently executable.

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
