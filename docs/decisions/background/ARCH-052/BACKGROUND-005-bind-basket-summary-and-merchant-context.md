---
id: ARCH-052-BACKGROUND-005
architecture_id: ARCH-052
title: Bind deterministic basket summary and merchant category for initial outreach
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-008
created: '2026-10-29'
updated: 2026-10-30
---

# ARCH-052-BACKGROUND-005: Bind deterministic basket summary and merchant category for initial outreach

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`.

This task was claimed and materialised for Attempt 1. At claim, the parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-005` was synchronized at `951cef829ace9b9705bcda15ca68bdfd67129d70`, and the implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-005` was synchronized at `6c284114afd7686ed4628def56fa248c3a79fce7`. The launcher confirmed `origin/main` was current at startup, recursively synchronized submodules, and verified `database` at `af77c594ecbfc78c26d01c0021a090830884bbff`. The task-claim commit is `ef530cd804ee538583693b53d2a7ca5b680f1d7f`. Before completion, the implementation branch incorporated the two commits subsequently added to `origin/main` (`4430635`, `0570565`) without conflicts. Implementation commit `c463c15d6e3dd0ff0b2eaad4d4bf9e1fc3741c72` is pushed to `origin/task/ARCH-052-BACKGROUND-005`; this parent task report will be committed and pushed separately.

## Objective

Render safe customer-facing `checkout.itemsSummary`, verified shop display name and existing `shop.categoryName` from saved recovery facts.

## Context

CheckoutRecovery.lineItems contains titles and quantities for both providers. `automated-recovery-template.service.ts` currently passes `shop.domain` as shopName, and ARCH-047 resolver has no checkout-item summary semantic key.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Add a bounded, locale-aware but deterministic item-summary formatter for saved `CheckoutRecovery.lineItems` (titles, variant, quantity, a small number of items and “and N more” suffix). No AI needed.
- Extend the existing `recovery-template-preparation/` variable resolver to bind the Shared `checkout.itemsSummary` key with safe length, Unicode/control, Meta placeholder and output-sanitisation checks.
- Resolve shop.name from verified brand/display configuration where available, not blindly from domain; preserve safe branded-domain fallback.
- Reuse existing `shop.categoryName` scoped/translated category binding; on missing category/translation require a separate approved no-category template or typed fallback, never invent category text.
- Produce fixture evidence for Shopify/Woo line-item formats, absent/invalid product titles, multiple quantities, locale, truncation and tenant isolation.

## Out of Scope

- No new category taxonomy reader/translation task, product photo fetch, AI wording, Meta AST compilation or discount evaluation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Basket description and shop category come from persisted trusted state, not AI-generated marketing prose. Category uses existing `shop.categoryName`; actual product category facts for AI come from MCP `commerce_search_products` and `commerce_get_product` when available.
- Follow task launcher and dedicated worktrees, Shared logger, no PII/credentials in logs and no provider cart mutations.

## Work Items

- [x] Create summary formatter with bounded fixtures.
- [x] Connect new semantic key and approved merchant brand fallback in Background preparer.
- [x] Unit and DB-backed cross-tenant tests.

## Interfaces / Contracts

- Shared `/recovery-template-bindings` `checkout.itemsSummary`; `RecoveryTemplatePreparationInput` extends with shop-scoped trusted checkout summary.

## Dependencies

- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-BACKGROUND-008`

## Acceptance Criteria

- [x] A checkout with shoes and a water bottle renders a readable deterministic item summary.
- [x] Missing or malformed items/category cannot make an unapproved placeholder/value; the existing typed `BINDING_VALUE_UNAVAILABLE` fallback prevents unresolved placeholders or invented category text.

## Validation

- [x] Formatter positive/negative and bounded-output tests, frozen-binding compatibility, and disposable PostgreSQL Background integration.
- [x] Background build and `git diff --check`; repository-wide lint ran with one pre-existing error in untouched `src/services/translation-reconciliation.service.ts:218` (`preserve-caught-error`). Lint reports no findings in changed files.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-template-preparation/recovery-template-brand.ts`
- `moda-interact-background/src/services/recovery-template-preparation/recovery-template.types.ts`
- `moda-interact-background/src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `moda-interact-background/tests/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Implementation complete; submitted for architect review at Attempt 1.

### Files Changed

 - `src/services/recovery-template-preparation/recovery-template-items-summary.ts` — new bounded, deterministic locale-aware formatter for saved Shopify/WooCommerce line items. It rejects malformed titles, controls, Unicode format characters and Meta placeholders, formats quantities and variants, limits visible rows, and caps output at 400 characters.
 - `src/services/recovery-template-preparation/recovery-template-brand.ts` and `recovery-template.types.ts` — bind Shared `checkout.itemsSummary` only for matching shop-scoped line items; resolve `shop.name` from the shop's configured `ShopBrand.brandName` first and retain the verified shop domain as safe fallback. Existing translated `shop.categoryName` continues to fail closed when unavailable.
 - `src/services/recovery-template-integration/automated-recovery-template.service.ts` — read persisted `lineItems` and pass them through the scoped preparation input. Unexpected exceptions remain logged with the Shared logger's bounded Error serialization; raw exception messages are not copied into log fields.
 - Unit and PostgreSQL integration tests cover Shopify and WooCommerce item shapes, quantities/variants, locale, invalid/missing titles, bounded truncation, tenant mismatch, configured-name preference and domain fallback, frozen binding digest compatibility, and persisted tenant-scoped preparation.

### Work Completed

 - The Shared semantic key was already present in Background's installed `@modainteract/moda-interact-shared` version `2.7.2`; Background now accepts and resolves it without duplicating a Shared contract.
 - Category values continue to come from the existing tenant-scoped, language-translated category reader. Missing category or translation produces the existing typed unavailable result, never invented text.
 - No provider calls, cart mutations, database schema changes, or dependent-task implementation were added.

### Validation Results

 - Focused unit run: **3 files passed, 30 tests passed** (`recovery-template-items-summary`, `recovery-template-preparer`, and `automated-recovery-template.service`). This includes the existing frozen-binding fingerprint compatibility coverage.
 - Disposable PostgreSQL integration: **1 file passed, 1 test passed** using `node scripts/test-integration.mjs tests/integration/arch047-recovery-template-preparation.integration.test.ts`. It exercised persisted basket binding and rejection of cross-tenant checkout facts.
 - `npm run build`: passed, including Prisma Client generation and TypeScript compilation.
 - `git diff --check`: passed.
 - `npm run lint`: reports one error at untouched `src/services/translation-reconciliation.service.ts:218` (`preserve-caught-error`); no findings were reported in changed files. The task implementation does not modify that baseline file.

### Deviations

Repository-wide lint is not fully clean because of the unrelated existing error described above. No out-of-scope lint fix was made.

### Assumptions

`ShopBrand.brandName` is the verified display configuration available to this service; the authenticated Shop domain remains the existing fallback when no safe brand name is configured. Persisted normalized line-item fields are the shared Shopify/WooCommerce recovery facts; provider-specific extra fields are ignored.

### Unresolved Issues

None within the assigned implementation scope. The existing repository-wide lint error remains for its owner to address.

### Architectural Concerns

None discovered.


## Architect Review

### Attempt 1 Architect Review

#### Review Status

Changes Requested.

#### Review Notes

The implementation otherwise follows the task scope: it formats persisted, tenant-scoped Shopify and WooCommerce line items, binds the existing Shared `checkout.itemsSummary` key, uses configured shop display name with a safe domain fallback, preserves the existing translated category binding, and fails closed for missing or malformed basket facts.

One customer-visible issue remains in `src/services/recovery-template-preparation/recovery-template-items-summary.ts`: the remainder suffix is hard-coded as `more` while the number formatting and list conjunction use the selected locale. The French fixture currently expects `et 1 more`, demonstrating mixed-language output. Localize the remainder label or use a language-neutral marker, and add an assertion that verifies the localized or neutral result.

#### Reviewed Files

- Attempt 1 Completion Report, task YAML, Work Items, Acceptance Criteria and Validation.
- Background implementation branch `task/ARCH-052-BACKGROUND-005` at `c463c15d6e3dd0ff0b2eaad4d4bf9e1fc3741c72`, clean and pushed.
- `src/services/recovery-template-preparation/recovery-template-items-summary.ts`.
- `src/services/recovery-template-preparation/recovery-template-brand.ts`.
- `src/services/recovery-template-preparation/recovery-template-preparer.service.ts` and `recovery-template.types.ts`.
- `src/services/recovery-template-integration/automated-recovery-template.service.ts`.
- Related unit and PostgreSQL integration tests.

#### Validation Reviewed

Reviewed the recorded focused unit tests (30), disposable PostgreSQL integration (1), build, changed-file lint and `git diff --check`. No tests were rerun for this review.

#### Architecture Conformance

The implementation respects the task's saved-facts, tenant-isolation, approved-template and fail-closed boundaries. Acceptance is withheld only for the locale inconsistency in the “and N more” suffix.

#### Follow-up

The same task is returned to `status: ready`; retain `attempt: 1` and clear `executor` and `claimed_at`. The canonical launcher may claim Attempt 2. Correct the remainder suffix and locale coverage, then resubmit for review. Keep `ARCH-052-BACKGROUND-008` blocked until this prerequisite is accepted.
