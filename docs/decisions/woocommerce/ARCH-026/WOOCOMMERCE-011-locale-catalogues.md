---
id: ARCH-026-WOOCOMMERCE-011
architecture_id: ARCH-026
title: Translate Northern European merchant UI
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-WOOCOMMERCE-009
enables:
  - ARCH-026-WOOCOMMERCE-014
created: 2026-10-09
updated: 2026-10-16
---

# Translate Northern European merchant UI

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Publish reviewed WooCommerce Admin gettext/JavaScript translation assets for `nl`, `da`, `fi`, `nb`, `sv` using WOO-009 tooling.

## Context

This is one of four independent translation batches for Shopify-parity language support. All five require translated values. The source messages include Woo-specific connection, billing and native WordPress menu strings not present in Shopify translations.

## Scope

- Create/review message translations for current Woo screens in `nl`, `da`, `fi`, `nb`, `sv`.
- Use verified Shopify translations for matching concepts where message meaning and placeholders are identical, with Woo-specific translations for other strings.
- Generate locale-specific WordPress gettext and JS assets through WOO-009 pipeline, with source files retained for future updates.
- Add scope-limited locale coverage and placeholder/pluralization tests for this batch.

## Out of Scope

- Changing PHP/JS runtime feature logic or WordPress locale selection semantics.
- Updating translations or files owned by the other locale batches.
- Changing shop language, API payloads, billing/subscription state or category activation.

## Requirements

- Every current merchant-facing string for these locales resolves to a reviewed value; non-brand strings must not silently remain in English.
- Preserve named/ordered printf placeholders, plural rules, HTML escaping and accessibility labels; use locale-correct punctuation where appropriate.
- Only WordPress plugin translation assets are changed; Shopify source catalogues are never edited or vendored into the WordPress runtime.

## Work Items

- [ ] Review and catalogue current Woo merchant PHP/React source messages.
- [ ] Translate and build the locale batch.
- [ ] Validate exact message-key coverage, placeholders/plurals and representative user-facing screens.

## Interfaces / Contracts

- Consumes translation template and compilation tool from ARCH-026-WOOCOMMERCE-009.
- Consumes existing Shopify curated translations as a reference for genuinely identical messages.
- Produces language assets under `moda-interact-woocommerce/languages/`.

## Dependencies

- `ARCH-026-WOOCOMMERCE-009`

## Enables

- `ARCH-026-WOOCOMMERCE-014`

## Acceptance Criteria

- [ ] The requested locale batch has complete compiled PHP and JavaScript translation assets.
- [ ] Source keys, substitution safety and plural rules pass strict validation.
- [ ] A missing translation fails this task’s coverage checks rather than being silently treated as ready.
- [ ] Current WooCommerce runtime and provider-neutral Shop locale semantics are unchanged.

## Validation

- [ ] Translation completeness and placeholder/plural tests for the locale batch.
- [ ] Automated JS/PHP locale rendering checks for selected screens in the batch.
- [ ] `npm run lint:js`, existing tests, and applicable build/packaging checks without requiring other batches to be present.

## Stop Condition

After Work Items, Acceptance Criteria and the scoped Validation pass, set the task to `review`, submit the Completion Report to `moda_architect`, and STOP. Do not begin enabled tasks.

## Implementation Notes

Reuse approved translated terminology and maintain a glossary for `Shop`, `Free`, `Recovery settings`, `CommerceAgent`, `Billing`, and platform-specific terminology. Do not introduce an additional translation-library runtime. For `pt-BR` vs `pt-PT` and `zh-Hans` vs `zh-Hant`, verify explicit regional/script differentiation rather than defaulting both to one locale.

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

Dutch, Danish, Finnish, Norwegian Bokmål and Swedish native gettext/JS catalogues are present, with locale-batch coverage and administrator/store locale-separation tests.

This is an explicit architecture-level retrospective closure based on the 2026-10-16 supplied code snapshot, **not** a reconstruction of an original task execution or CI run. The attached archive has no Git worktrees/commits or historical launcher packet, so mirrored-branch isolation, claim provenance, original attempts, historical test results and actual WordPress/HTTPS/provider execution cannot be independently certified here. Original `attempt: 0` and executor-owned Completion Report are preserved without manufacturing evidence. These provenance limitations do not establish process compliance. Terminal integrated Woo provider certification remains `ARCH-026-SYSTEM-TEST-001`.

### Reviewed Files

- `moda-interact-woocommerce/languages/moda-interact-nl_NL.po`
- `moda-interact-woocommerce/languages/moda-interact-da_DK.po`
- `moda-interact-woocommerce/languages/moda-interact-fi.po`
- `moda-interact-woocommerce/languages/moda-interact-nb_NO.po`
- `moda-interact-woocommerce/languages/moda-interact-sv_SE.po`

### Validation Reviewed

- `moda-interact-woocommerce/tests/i18n/locale-batch-011.test.mjs` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-woocommerce/tests/integration/locale-batch-011.mjs` (test present and inspected; not independently executed in this read-only archive)
- `node scripts/i18n/verify-source.mjs`: PASS, 332 PHP/React source messages match POT.
- `node --test tests/i18n/*.test.mjs`: PASS, 28/28 tests.
- Static cross-file wiring and source inspection: completed for this task's bounded implementation.
- No new API TypeScript, PHP unit, WordPress integration, PostgreSQL or live provider tests were executed as part of this reconciliation unless explicitly listed as PASS above.

### Architecture Conformance

Accepted for bounded code-level implementation reconciliation. Live/integrated runtime acceptance is reserved for terminal system-test evidence. No source-code change is authorised by this review.

### Follow-up

`ARCH-026-SYSTEM-TEST-001` — certify the integrated HTTPS callback, real Woo consent/read and credential/tenant/billing isolation. Recover missing Git/provenance records separately if full historical workflow certification is required; do not invent them.
