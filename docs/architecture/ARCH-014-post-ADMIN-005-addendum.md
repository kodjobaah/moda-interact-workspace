# ARCH-014 post-ADMIN-005 architecture addendum

This addendum records the architect decisions made after accepted `ARCH-014-ADMIN-005`.

## One spreadsheet technology

All `moda-interact-admin` human translation workbooks use exactly:

```text
exceljs@4.4.0
```

`ARCH-014-ADMIN-006` establishes `src/lib/admin/translation-workbook-common.ts`; later workbook tasks reuse it. No second spreadsheet package is permitted without a new architect decision.

## Remaining dependency graph

```text
ADMIN-005 COMPLETE                    DATABASE-002 COMPLETE
      │                                      │
      ├────────► ADMIN-006 COMPLETE           └────────► DATABASE-003 COMPLETE
      │                │                                      │
      └────────► ADMIN-007 COMPLETE           ┌───────────────┴──────────────┐
                                               │                              │
                                ADMIN-006 + DATABASE-003               DATABASE-003
                                               │                              │
                                               ▼                              ▼
                                      ADMIN-008 COMPLETE                SHOPIFY-003 COMPLETE
                                               │                              │
                                               └───────────────┬──────────────┘
                                                               ▼
                                                    SYSTEM-TEST-002 PENDING

ADMIN-006 + existing MerchantPricing prerequisites
      └────────► SYSTEM-TEST-001 READY (developer-gated)
```

`DATABASE-003`, `ADMIN-006`, `ADMIN-007`, `ADMIN-008`, and `SHOPIFY-003` are architect-accepted Complete. `SYSTEM-TEST-001` is Ready and developer-gated. `SYSTEM-TEST-002` now remains Pending only on the corrective `ARCH-014-ADMIN-010` hardening task before terminal execution.

`ADMIN-008` is Complete and reuses the XLSX implementation established by accepted `ADMIN-006`. `SHOPIFY-003` is Complete. The task metadata defect where ADMIN-008 had a blank front-matter `id` is corrected by the current overlay.

## Promotion localization invariant

`PromotionCampaign.name` is internal Admin identity. Merchant-visible promotion title/description are exact-locale `PromotionCampaignTranslation` content. DRAFT may be incomplete; ACTIVE requires exact 20/20 at the server activation boundary.

## Admin cleanup invariant

The manual `BillingUpgradeEconomicsEdge` / `BillingEconomicsSnapshot` Admin forms are superseded by ARCH-014 MerchantPricing catalogue position/full-portfolio economics and are removed from Admin code only. Existing operational database objects remain untouched. Tenant search is a tenant-directory tool, not global Admin chrome.

## Corrective post-implementation audit

The 16 Sep snapshot audit added `ARCH-014-ADMIN-010`; `SYSTEM-TEST-002` must wait for that hardening before developer execution. Runtime-control cadence corrections are documented separately in `ARCH-014-runtime-controls-corrective-addendum.md`.
