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
        initial subscription activation
        callback happy path only

 SHOPIFY-001
      |
      v
 SHOPIFY-004
 WEB_PAGE Merchant Knowledge
 source lifecycle + Recovery Settings
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
| [SHOPIFY-001](SHOPIFY-001-materialise-merchant-knowledge-feature-configuration.md) | Extend existing BillingPlan materialiser to copy generic Feature configuration | Ready | DATABASE-001, SHARED-002 |
| [SHOPIFY-002](SHOPIFY-002-select-store-category-pending-profile.md) | One initial/later Store Category selection lifecycle and pending Shop DRAFT/profile | Ready | DATABASE-001, SHARED-002 |
| [SHOPIFY-003](SHOPIFY-003-activate-initial-store-category.md) | Billing callback activation of initial pending Store Category and Shop prompt | Pending | SHOPIFY-001, SHOPIFY-002 |
| [SHOPIFY-004](SHOPIFY-004-manage-merchant-knowledge-web-pages.md) | Current-plan WEB_PAGE source management and Recovery Settings UI | Pending | SHOPIFY-001, SHARED-002 |
| [SHOPIFY-005](SHOPIFY-005-upload-merchant-knowledge-files.md) | Private R2 CSV/XLSX upload/finalize/replace/reprocess | Pending | SHOPIFY-004 |

## Execution frontier

DATABASE-001 and SHARED-002 are Complete/accepted, so:

```text
SHOPIFY-001 -> Ready
SHOPIFY-002 -> Ready
```

Both tasks must consume exactly `@modainteract/moda-interact-shared@1.0.1`.

After SHOPIFY-001 + SHOPIFY-002:

```text
SHOPIFY-003 -> Ready
```

After SHOPIFY-001:

```text
SHOPIFY-004 -> Ready
```

After SHOPIFY-004:

```text
SHOPIFY-005 -> Ready
```

## Cross-domain follow-up required

ARCH-023 also requires the **existing Background subscription reconciler** to perform the same initial pending Store Category activation when the Shopify billing callback is missed.

SHOPIFY-003 intentionally implements only the callback happy path. A bounded Background reconciliation hook must be defined before final ARCH-023 system acceptance; it must not be hidden inside the new Merchant Knowledge worker.
