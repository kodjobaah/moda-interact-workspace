# ARCH-014 admin tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-014-ADMIN-001](ADMIN-001-multimeter-portfolio-economics.md) | complete | Add pure deterministic multi-meter/full-portfolio economics evaluation over caller-supplied MerchantPricing catalogue order without changing operational billing runtime. |
| [ARCH-014-ADMIN-002](ADMIN-002-plan-builder-translation-publish.md) | complete | Refactor the billing Plans view into a self-contained MerchantPricing catalogue builder with explicit catalogue placement, translation template/import and atomic save/activation. |
| [ARCH-014-ADMIN-003](ADMIN-003-remove-superseded-admin-plan-management.md) | complete | Remove the legacy Admin BillingPlan catalogue/editor/mutation/read-model surface made unreachable by ADMIN-002 while preserving durable BillingPlan state and live operational economics controls. |
| [ARCH-014-ADMIN-004](ADMIN-004-complete-builder-content-and-translation-gating.md) | complete | Complete the builder with human-readable placement, ordered merchant plan-card highlights, translation JSON v2/retention, portfolio-step gating and server-authoritative final review. |
| [ARCH-014-ADMIN-005](ADMIN-005-clarify-usage-pricing-and-translation-import.md) | complete | Clarify usage-event pricing and harden schema-v2 translation import UX while preserving server-authoritative economics and translation validation. |
| [ARCH-014-ADMIN-006](ADMIN-006-prefilled-xlsx-translation-workbook.md) | complete | Establish the single `exceljs@4.4.0` Admin spreadsheet standard and replace human-facing MerchantPricing JSON with a pre-populated XLSX workbook. |
| [ARCH-014-ADMIN-007](ADMIN-007-remove-legacy-economics-and-scope-tenant-search.md) | ready | Remove superseded manual BillingPlan economics controls and render tenant search only on the tenant directory. |
| [ARCH-014-ADMIN-008](ADMIN-008-multilingual-promotion-xlsx.md) | ready | Reuse the ADMIN-006 XLSX standard to author exact 20-locale promotion merchant title/description and gate activation on 20/20. |
