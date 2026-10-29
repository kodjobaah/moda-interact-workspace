# ARCH-052 — Api task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_api`. Repository: `moda-interact-api`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [API-001](API-001-align-existing-woo-selection-with-shared-contract.md) | Align existing Woo multi-select API with canonical Shared validator | Pending | `ARCH-052-SHARED-003` |
| [API-002](API-002-expose-private-woo-checkout-product-image-read.md) | Expose bounded authenticated Woo product/variation image read for Background | Pending | `ARCH-052-SHARED-003` |
| [API-003](API-003-proxy-woo-native-coupon-proof-through-private-api.md) | Expose authenticated private Woo discount-proof proxy with existing Woo provider grant | Pending | `ARCH-052-SHARED-003`, `ARCH-052-WOOCOMMERCE-001` |
| [API-004](API-004-proxy-woo-restore-link-through-private-api.md) | Issue Woo checkout-restoration links through private hosted API read grant | Pending | `ARCH-052-SHARED-003`, `ARCH-052-WOOCOMMERCE-002` |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
