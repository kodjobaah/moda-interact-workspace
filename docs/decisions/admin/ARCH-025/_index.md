# ARCH-025 Admin tasks

Architecture: [`ARCH-025`](../../../architecture/ARCH-025-shopify-billing-service-maintainability.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

This directory contains two independent Admin maintainability chains. Neither depends on the Shopify or Background ARCH-025 chains. The MerchantPricingPlanBuilder chain is sequential internally because every child-step extraction consumes the accepted typed draft/controller boundary. The QueueMonitor chain is sequential internally because each hook/presentation extraction consumes the previously accepted client/control boundary.

```text
ADMIN-001 -> ADMIN-002 -> ADMIN-003 -> ADMIN-004
      -> ADMIN-005 -> ADMIN-006 -> ADMIN-007 -> ADMIN-008

ADMIN-009 -> ADMIN-010 -> ADMIN-011 -> ADMIN-012
      -> ADMIN-013 -> ADMIN-014 -> ADMIN-015
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

QueueMonitor reviewed baseline:

```text
src/components/admin/queue-monitor.tsx
1,058 lines
SHA-256: 851f8e5e25875a4bb6657ecd5d01bd2c4f3cf1bafa7928e342e332ce3012a4f7

src/components/admin/queue-monitor-refresh.ts
SHA-256: 14463cd5480aa82cd05ef569968ee579c14d94f610baab1d5ebdf1d31584a0cc
```

ADMIN-009 is the only QueueMonitor task permitted to modify `admin-queue-monitor.test.mjs`, `admin-queue-details-drawer.test.mjs`, `admin-failed-job-detail-panel.test.mjs` or `admin-internationalization.test.mjs`, and only to make their QueueMonitor source loading follow the bounded extracted module set without weakening assertions. ADMIN-010..015 must not modify the accepted ADMIN-009 versions. The server reader/routes and their dedicated tests remain frozen throughout ADMIN-009..015.

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
| [ADMIN-009](ADMIN-009-extract-queue-monitor-browser-client.md) | Browser contracts/client + extraction-safe QueueMonitor assertions | Ready | - |
| [ADMIN-010](ADMIN-010-extract-queue-monitor-summary-hook.md) | Queue-summary polling/single-flight hook | Pending | ADMIN-009 |
| [ADMIN-011](ADMIN-011-extract-queue-jobs-hook.md) | Queue jobs filters/page/recent-full hook | Pending | ADMIN-010 |
| [ADMIN-012](ADMIN-012-extract-queue-job-detail-hook.md) | Selected-job detail hook | Pending | ADMIN-011 |
| [ADMIN-013](ADMIN-013-extract-resizable-queue-drawer-hook.md) | Resizable drawer viewport/pointer/keyboard hook | Pending | ADMIN-012 |
| [ADMIN-014](ADMIN-014-extract-queue-summary-table.md) | Queue summary table presentation | Pending | ADMIN-013 |
| [ADMIN-015](ADMIN-015-extract-queue-details-and-reduce-monitor.md) | Queue details presentation + final thin QueueMonitor shell | Pending | ADMIN-014 |

## Execution frontier

`ARCH-025-ADMIN-001` and `ARCH-025-ADMIN-009` are independently Ready, and both are independent of `ARCH-025-BACKGROUND-001` / `ARCH-025-BACKGROUND-008`. ADMIN-002..008 and ADMIN-010..015 remain Pending until the immediately preceding task in their own Admin chain is architect-accepted Complete.
## Deep coherence review — 2026-10-02

A source/task closure review against the 1,553-line post-ARCH-024 builder kept the ADMIN-001..008 graph unchanged and tightened the execution contract before ADMIN-001 starts. ADMIN-001 must establish the complete consume-only controller/action/selector interface for every later step, keep its pure reducer directly Node-testable, preserve hook-edge event/highlight identity generation and effect-driven economics-override invalidation, make the security harness scan the full bounded builder module set (including the ARCH-014 forbidden-dependency check), and preserve the exact hidden translation JSON fallback. ADMIN-002..008 may consume but not extend that accepted controller; a missing interface returns to `moda_architect`. Usage-event stale-field/tier quirks, the current empty secondary economics rows, and the workbook/final-step mount/conditional DOM semantics are explicitly preserved as move-only behaviour.
