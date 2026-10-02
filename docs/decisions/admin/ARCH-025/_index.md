# ARCH-025 Admin tasks

Architecture: [`ARCH-025`](../../../architecture/ARCH-025-shopify-billing-service-maintainability.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

This directory contains the independent MerchantPricingPlanBuilder maintainability chain. It has no dependency on the Shopify or Background ARCH-025 chains and is sequential internally because every child-step extraction consumes the accepted typed draft/controller boundary.

```text
ADMIN-001 -> ADMIN-002 -> ADMIN-003 -> ADMIN-004
      -> ADMIN-005 -> ADMIN-006 -> ADMIN-007 -> ADMIN-008
```

Current reviewed builder baseline:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
1,553 lines
SHA-256: 7387fd18873e968220299cd976bd6705df8cba00b5c75f88a48b4d97a4ef05b0
```

The source hash is evidence only and is expected to change during extraction. The following pure/domain tests are frozen byte-for-byte for all eight tasks:

```text
tests/unit/merchant-pricing-builder-payload.test.ts
  a985f89cbc9f4d41901d2c1e400935faf8453a5bd866ac0834a58b0851feb243
tests/unit/merchant-pricing-plan-model.test.ts
  e953adaa54f7aceb31cc43af21f8088c800b32d69c2fc2561dff69fc27ce1086
tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts
  610a7b0d0860490575cdec508f52e438a4e7bee87970a101b6b39d4591d6630f
tests/unit/merchant-pricing-economics.test.ts
  eb7164c84a7c056edfc461fd5b9213ab87e3537511ccf426d32f6bc6804e05e8
tests/unit/merchant-pricing-economics-override.test.ts
  434ad7ca05dad91bfb4fb62ce3ad5cbcd1f27355cc51c879dc7bd9a9967c79f7
tests/unit/merchant-pricing-translations.test.ts
  90e0e5e37687d3037712afac1828175fe8e6623550525572fbcb9d2dc57d8c92
tests/unit/merchant-pricing-translation-workbook.test.ts
  385e79ffcd761b046fb119be18de5f313461cb8d81d6a4f0fb23d3b7837e3ce8
```

`tests/security/admin-merchant-pricing-plan.test.mjs` starts at SHA-256 `89243548c486f68cc7b741e9cac6ded5090ba477f1049e512ae6f982ccd92856` with 13 tests. ADMIN-001 may change only its builder source-loading mechanism so the same assertions follow the bounded builder module set. ADMIN-002..008 must not modify the accepted ADMIN-001 version.

Individual task YAML is authoritative.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-extract-pricing-plan-draft-controller.md) | Typed draft/controller + extraction-safe security loader | Ready | - |
| [ADMIN-002](ADMIN-002-extract-plan-step.md) | Plan/model/features/knowledge step | Pending | ADMIN-001 |
| [ADMIN-003](ADMIN-003-extract-catalogue-placement-step.md) | Catalogue placement step | Pending | ADMIN-002 |
| [ADMIN-004](ADMIN-004-extract-shopify-pricing-step.md) | Shopify pricing step | Pending | ADMIN-003 |
| [ADMIN-005](ADMIN-005-extract-usage-events-step.md) | Usage-event/tier step | Pending | ADMIN-004 |
| [ADMIN-006](ADMIN-006-extract-merchant-content-step.md) | Merchant content/highlights step | Pending | ADMIN-005 |
| [ADMIN-007](ADMIN-007-extract-portfolio-economics-step.md) | Portfolio economics/override step | Pending | ADMIN-006 |
| [ADMIN-008](ADMIN-008-extract-translations-review-and-reduce-builder.md) | Mounted translations/review + final thin shell | Pending | ADMIN-007 |

## Execution frontier

`ARCH-025-ADMIN-001` is Ready independently of `ARCH-025-BACKGROUND-001` and `ARCH-025-BACKGROUND-008`. ADMIN-002..008 remain Pending until the immediately preceding Admin task is architect-accepted Complete.
