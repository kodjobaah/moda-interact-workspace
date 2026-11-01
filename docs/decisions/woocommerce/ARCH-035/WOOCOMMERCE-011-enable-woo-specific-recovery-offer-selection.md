---
id: ARCH-035-WOOCOMMERCE-011
architecture_id: ARCH-035
title: Preview WooCommerce coupons in Recovery Settings
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-035-WOOCOMMERCE-011: Preview WooCommerce coupons in Recovery Settings

## Architecture

- Architecture ID: `ARCH-035`.
- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`.
- Portable developer handoff, defined but not materialised; no task branch, commit or push created.

## Objective

Allow a Woo merchant to inspect a **read-only, paginated local coupon catalogue** inside the existing Recovery Offer section. A local preview choice must not be mistaken for a saved recovery offer.

## Context

The merchant approved a phased provider-specific coupon experience on 12 October 2026. WooCommerce native coupon records can be read by the installed plugin; this is a merchant UI discovery capability. The earlier full WOOCOMMERCE-011 design was superseded on 11 October; its provider proof, hosted selection CAS, schema and Background changes remain **outside** this Stage 1 re-scope. Stage 1 does not reactivate those old dependencies or public contracts.

## Scope

- One privileged WordPress REST GET route to list local `shop_coupon` records, using bounded queries and sanitised read-only metadata.
- Modular React `client`, `coupon-list`, `coupon-preview` components under Recovery Settings.
- Preview-only local radio selection and explicit non-persistence notice; no automatic or manual coupon save.
- Pagination (10 records per page), search, keyboard access, loading/empty/error and mobile layout.
- Tests, source catalogue updates and all 20 merchant-admin locales.

## Out of Scope

- Any hosted API additions or new read grants; WordPress can read its own coupon store through Woo native data access.
- Any coupon selection persistence, data schema, API-012, Woo discount entitlement or checkout-lineage work.
- Any outgoing coupon offer or AI-selected coupon promises, runtime verification, WhatsApp or Background changes.
- Editing or creating coupons, changing shop state, Shopify discount references or other repository source.
- All `docs/decisions/**/_index.md` files, until explicit architecture reconciliation.

## Requirements

- Preserve the two-stage WordPress navigation and approved Recovery Settings panel layout.
- WordPress REST reads require `manage_woocommerce` and valid `X-WP-Nonce`; no public coupon disclosure.
- Query rejects unexpected fields, invalid pages, non-string/overlong searches and request bodies; bounded 10-row query, server count, consistent ordering.
- Coupon preview includes code, basic type/amount and a **preliminary** status. Expired, exhausted, unsupported or obviously restricted coupons cannot be locally selected. Even an apparently unrestricted coupon is **not** guaranteed applicable at recovery send-time.
- UI never forwards selection to API-002. Existing `Save recovery behaviour` must save only delay/follow-up values and must not be coupled to this preview.
- No fake persisted selection, no hidden cross-store identifiers, no credentials in React/localStorage/logs.

## Work Items

- [ ] Implement bounded, nonce/capability-checked Woo local coupon GET.
- [ ] Add modular React preview client, list, search and pagination.
- [ ] Embed within Recovery Offer without changing policy save or store category.
- [ ] Add responsive styles, tests and complete 20-language catalogues.
- [ ] Validate LocalWP and return Completion Report to `moda_architect`.

## Interfaces / Contracts

New **local-only** WordPress REST GET: `/moda-interact/v1/merchant/recovery-coupons?q=&page=1`.

Returns `{schemaVersion:1,page,pageSize:10,total,totalPages,items:[{id,code,type,amount,currency,previewStatus}]}`. Status values: `REVIEW_REQUIRED`, `RESTRICTED`, `EXPIRED`, `EXHAUSTED`, `UNSUPPORTED`. This is a preliminary display projection, **not** a Moda cross-service runtime contract or provider eligibility proof. Only `REVIEW_REQUIRED` items are selectable in the ephemeral UI preview.

## Dependencies

None. This preview uses WooCommerce's already-installed runtime and Recovery Settings presentation. Separate future provider-capability tasks are intentionally not dependencies of Stage 1.

## Enables

None within ARCH-035. Future hosted selection/runtime capability requires separate architecture agreement.

## Acceptance Criteria

- [ ] Normal WordPress-admin navigation and current recovery-policy saving are unchanged.
- [ ] Search + first/second/last page work with 10+ coupon fixtures; bounded total is authoritative.
- [ ] Read requires admin capability and nonce; spoofed shop IDs/unknown query fields are rejected.
- [ ] Expired/exhausted/restricted coupons are not selectable in the local preview.
- [ ] Selection is never persisted nor submitted to API-002; the UI clearly says preview only.
- [ ] All 20 supported locales contain reviewed non-empty strings; no English-only new UI key.
- [ ] Responsive layout and full repository validation have evidence.

## Validation

- [ ] `npm run test:i18n`, `npm run i18n:verify:20`, `npm run test:js`, `npm run test:php`.
- [ ] `npm run lint:js`, `npm run lint:css`, `npm run build`, `npm run plugin-zip`.
- [ ] LocalWP coupon search/pagination/preview tests; PHP nonce denial; no provider write observed.
- [ ] `git apply --check --whitespace=error-all` and `git diff --check` against the exact baseline.

## Stop Condition

After completing these acceptance and validation checks, return control to `moda_architect`. Do not begin hosted selection or runtime work.

## Implementation Notes

WordPress coupons still use `shop_coupon`; bounded `WP_Query` IDs plus `WC_Coupon` getters avoid unbounded `get_posts(-1)` or direct Woo REST consumer credentials. PHP returns only a small allowlisted projection. The client validates it strictly and shows potential preview items as requiring later verification.

## ASCII Page Design

```text
Recovery Settings
+---------------------------------------------------------------+
| 1 Recovery offer                                              |
| (x) No discount | ( ) Specific discount [Unavailable for save]|
|                | ( ) AI-selected [Unavailable]                |
|---------------------------------------------------------------|
| > Browse coupons                                              |
|                                                               |
| Preview only: coupon selection is NOT saved or sent           |
| Search coupons [_______________________] [Search]             |
|                                                               |
| ( ) 10OFF        10%             Review required               |
| (x) SAVE5        GBP 5.00        Review required               |
| ( ) OLD25        25%             Expired / disabled            |
|                                                               |
| [Previous]                   Page 1 of 3               [Next] |
+---------------------------------------------------------------+
| 2 Recovery start (existing saved policy)                       |
| 3 No-response follow-up (existing saved policy)                |
|                                        [Save recovery behaviour]|
+---------------------------------------------------------------+

Mobile: one-column search and list; amounts/reasons wrap under code;
Previous / page / Next remain reachable without horizontal overflow.
Unavailable/error states explain that no coupon selection has been saved.
```

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run by developer yet.

### Deviations

None.

### Assumptions

Developer will apply portable patch to the WooCommerce implementation checkout.

### Unresolved Issues

Hosted coupon selection and runtime proof are intentionally not covered by this task.

### Architectural Concerns

No persisted provider coupon identity exists under this UI-only task.

## Architect Review

### Review Status

Accepted — retrospective code-based review, 16 October 2026.

### Review Notes

Read-only, paginated local Woo coupon preview; no persisted preview selection.

This is a **retrospective, source-code-based architectural reconciliation** against the developer-provided 2026-10-16 10:58:55 workspace ZIP. The source snapshot is not the historical paired task worktrees or Git branches; an original launcher packet, accepted task commit, Completion Report validation and LocalWP run cannot be reconstructed from it. Retain `attempt: 0` and the original developer/agent Completion Report; no historical execution claim or test pass is manufactured.

### Reviewed Files

- `moda-interact-woocommerce/includes/Rest/RecoveryCouponCatalogueController.php`
- `moda-interact-woocommerce/src/recovery-settings/woo-coupons/{coupon-preview.js,coupon-list.js,coupon-client.js}`
- `moda-interact-woocommerce/tests/js/recovery-coupon-preview.test.js`

### Validation Reviewed

This session directly passed `npm run test:i18n` (28 tests) and `npm run i18n:verify:20` (332 current PHP/React gettext strings, 19 translation packs / 20 canonical locales). Related Woo PHP controller and native navigation files passed `php -l`. JS component/integration tests and API TypeScript test cases were inspected as source, but `node_modules` are absent from the ZIP and their execution, PHP integration, LocalWP browser evidence, production build, package ZIP, disposable PostgreSQL proof and launcher worktree verification were **not** run in this session.

### Architecture Conformance

The inspected implementation provides the task's bounded capability and uses the approved architecture/repository boundary. The source-based reconciliation is not a claim of unobserved runtime validation, task worktree isolation or release certification.

### Follow-up

Continue normal work only for other, incomplete ARCH-035 tasks. The terminal SYSTEM-TEST-001 remains blocked until every required UI implementation is Complete.
