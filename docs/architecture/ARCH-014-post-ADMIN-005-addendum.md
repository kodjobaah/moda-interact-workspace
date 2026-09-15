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
      ├────────► ADMIN-006 READY              └────────► DATABASE-003 READY
      │                │                                      │
      └────────► ADMIN-007 COMPLETE           ┌───────────────┴──────────────┐
                                               │                              │
                                ADMIN-006 + DATABASE-003               DATABASE-003
                                               │                              │
                                               ▼                              ▼
                                      ADMIN-008 PENDING             SHOPIFY-003 PENDING
                                               │                              │
                                               └───────────────┬──────────────┘
                                                               ▼
                                                    SYSTEM-TEST-002 PENDING

ADMIN-006 + existing MerchantPricing prerequisites
      └────────► SYSTEM-TEST-001 PENDING (developer-gated)
```

`ADMIN-007` is architect-accepted Complete. `ADMIN-006` and `DATABASE-003` remain independent of this cleanup and may continue in parallel from the accepted baseline.

After `DATABASE-003` completes, `SHOPIFY-003` may start immediately. `ADMIN-008` starts only when both `DATABASE-003` and `ADMIN-006` are complete so it reuses the established XLSX implementation.

## Promotion localization invariant

`PromotionCampaign.name` is internal Admin identity. Merchant-visible promotion title/description are exact-locale `PromotionCampaignTranslation` content. DRAFT may be incomplete; ACTIVE requires exact 20/20 at the server activation boundary.

## Admin cleanup invariant

The manual `BillingUpgradeEconomicsEdge` / `BillingEconomicsSnapshot` Admin forms are superseded by ARCH-014 MerchantPricing catalogue position/full-portfolio economics and are removed from Admin code only. Existing operational database objects remain untouched. Tenant search is a tenant-directory tool, not global Admin chrome.
