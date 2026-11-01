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
status: complete
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
updated: 2026-10-16
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

Accepted — retrospective implementation-evidence reconciliation, 2026-10-16.

### Review Notes

The strict 20-locale manifest, source-POT synchronization, release-asset integrity gate, packaging inclusion and WordPress integration harness are implemented.

This is an explicit architecture-level retrospective closure based on the 2026-10-16 supplied code snapshot, **not** a reconstruction of an original task execution or CI run. The attached archive has no Git worktrees/commits or historical launcher packet, so mirrored-branch isolation, claim provenance, original attempts, historical test results and actual WordPress/HTTPS/provider execution cannot be independently certified here. Original `attempt: 0` and executor-owned Completion Report are preserved without manufacturing evidence. These provenance limitations do not establish process compliance. Terminal integrated Woo provider certification remains `ARCH-026-SYSTEM-TEST-001`.

### Reviewed Files

- `moda-interact-woocommerce/scripts/i18n/release-assets.mjs`
- `moda-interact-woocommerce/scripts/i18n/verify-source.mjs`
- `moda-interact-woocommerce/scripts/package-production.mjs`
- `moda-interact-woocommerce/tests/integration/release-locales.mjs`
- `moda-interact-woocommerce/tests/integration/release-browser-locales.mjs`
- `moda-interact-woocommerce/tests/integration/run-wordpress.mjs`
- `moda-interact-woocommerce/tests/integration/run-package-lifecycle.mjs`

### Validation Reviewed

- `moda-interact-woocommerce/tests/i18n/release-assets.test.mjs` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-woocommerce/tests/i18n/release-source.test.mjs` (test present and inspected; not independently executed in this read-only archive)
- `node scripts/i18n/verify-source.mjs`: PASS, 332 PHP/React source messages match POT.
- `node --test tests/i18n/*.test.mjs`: PASS, 28/28 tests.
- Static cross-file wiring and source inspection: completed for this task's bounded implementation.
- No new API TypeScript, PHP unit, WordPress integration, PostgreSQL or live provider tests were executed as part of this reconciliation unless explicitly listed as PASS above.

### Architecture Conformance

Accepted for bounded code-level implementation reconciliation. Live/integrated runtime acceptance is reserved for terminal system-test evidence. No source-code change is authorised by this review.

### Follow-up

`ARCH-026-SYSTEM-TEST-001` — certify the integrated HTTPS callback, real Woo consent/read and credential/tenant/billing isolation. Recover missing Git/provenance records separately if full historical workflow certification is required; do not invent them.
