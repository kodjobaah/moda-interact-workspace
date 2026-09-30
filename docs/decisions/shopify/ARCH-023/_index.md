# ARCH-023 Shopify tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_app`.

Repository: `moda-interact`.

Coordinator: `moda_architect`.

The Shopify decomposition follows lifecycle/security boundaries:

```text
DATABASE-001 + SHARED-002
        |
        +------------------------------+
        |                              |
        v                              v
 SHOPIFY-001                     SHOPIFY-002
 BillingPlan feature             Store Category selection
 configuration materialisation   + pending Shop DRAFT/profile
        |                              |
        +--------------+---------------+
                       |
                       v
                 SHOPIFY-003
        initial Store Category activation
        after durable subscription activation

 SHOPIFY-001 + ADMIN-004
          |
          v
     SHOPIFY-004
 Merchant opt-in control plane +
 WEB_PAGE source lifecycle
      |
      v
 SHOPIFY-005
 private R2 CSV/XLSX upload lifecycle
      |
      v
 planned GATEWAY-001
```

SHOPIFY-001 and SHOPIFY-002 are independent once Database/Shared dependencies are complete.

Individual task YAML is authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [SHOPIFY-001](SHOPIFY-001-materialise-merchant-knowledge-feature-configuration.md) | Extend existing BillingPlan materialiser to copy generic Feature configuration | Complete | DATABASE-001, SHARED-002 |
| [SHOPIFY-002](SHOPIFY-002-select-store-category-pending-profile.md) | One initial/later Store Category selection lifecycle and pending Shop DRAFT/profile | Complete | DATABASE-001, SHARED-002 |
| [SHOPIFY-003](SHOPIFY-003-activate-initial-store-category.md) | Initial Store Category/Shop prompt activation only after durable ACTIVE/TRIALING subscription state | Ready — Attempt 1 corrections | SHOPIFY-001, SHOPIFY-002 |
| [SHOPIFY-004](SHOPIFY-004-manage-merchant-knowledge-web-pages.md) | Merchant opt-in control plane plus current-plan WEB_PAGE source management | Pending | SHOPIFY-001, SHARED-002, ADMIN-004 |
| [SHOPIFY-005](SHOPIFY-005-upload-merchant-knowledge-files.md) | Private R2 CSV/XLSX upload/finalize/replace/reprocess | Pending | SHOPIFY-004 |

## Execution frontier

DATABASE-001 and SHARED-002 are Complete/accepted. SHOPIFY-001 is now Complete / Accepted at Attempt 2 and SHOPIFY-002 is Complete / Accepted at Attempt 2. The current Shopify frontier is:

```text
SHOPIFY-001 -> Complete — Accepted Attempt 2
SHOPIFY-002 -> Complete — Accepted Attempt 2
SHOPIFY-003 -> Ready — Attempt 1 PostgreSQL proof
SHOPIFY-004 -> Pending (new dependency: ADMIN-004)
SHOPIFY-005 -> Pending (still gated on SHOPIFY-004)
```

SHOPIFY-001 and SHOPIFY-002 both consume exactly `@modainteract/moda-interact-shared@1.0.1`. SHOPIFY-003 remains independently executable. SHOPIFY-004 is deliberately re-gated on ADMIN-004 so the fixed `merchant_knowledge` Feature is reconciled to `MERCHANT_OPT_IN` before the merchant-facing control plane is implemented.

SHOPIFY-003 Attempt 1 is substantively conformant but remains Ready for one bounded correction: execute its authored disposable PostgreSQL activation suite against the accepted migrations. No production redesign, database change, Background hook or Commerce audit actor is part of that correction.

After SHOPIFY-004:

```text
SHOPIFY-005 -> Ready
```

## Cross-domain follow-up required

ARCH-023 also requires the **existing Background subscription reconciler** to perform the same initial pending Store Category activation when the Shopify billing callback is missed.

SHOPIFY-003 implements the Shopify-repository activation path only after authoritative durable ACTIVE/TRIALING subscription state. A bounded Background reconciliation hook must be defined before final ARCH-023 system acceptance; it must not be hidden inside the new Merchant Knowledge worker.

## Merchant opt-in reconciliation

The current plan grants Merchant Knowledge configuration access; it does not activate the feature. `SHOPIFY-004` reuses the existing Recovery Settings `FeaturePreferences` / `ShopFeaturePreference` control as the single ON/OFF state. Sources may be configured while OFF, but Shopify does not start ingestion until ON. `SHOPIFY-005` remains a separate file/R2 extension.
