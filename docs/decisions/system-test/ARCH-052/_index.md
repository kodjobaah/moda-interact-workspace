# ARCH-052 — System-Test task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_system_test`. Repository: `moda-interact-system-test`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [SYSTEM-TEST-001](SYSTEM-TEST-001-certify-shopify-initial-outreach-modes.md) | Certify Shopify initial outreach personalization and all offer modes | Pending | `ARCH-052-BACKGROUND-008`, `ARCH-052-SHOPIFY-001`, `ARCH-052-COMMERCE-001`, `ARCH-052-COMMERCE-002`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002`, `ARCH-052-DATABASE-001`, `ARCH-052-DATABASE-002` |
| [SYSTEM-TEST-002](SYSTEM-TEST-002-certify-woocommerce-initial-outreach-modes.md) | Certify Woo initial outreach, native coupon proof and secure cart return | Pending | `ARCH-052-BACKGROUND-008`, `ARCH-052-API-001`, `ARCH-052-WOOCOMMERCE-001`, `ARCH-052-WOOCOMMERCE-002`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002`, `ARCH-052-DATABASE-001`, `ARCH-052-DATABASE-002` |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
