# ARCH-052 — Shopify task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_app`. Repository: `moda-interact`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [SHOPIFY-001](SHOPIFY-001-select-multiple-authorised-recovery-discounts.md) | Save and display Shopify merchant-selected discount sets | Pending | `ARCH-052-DATABASE-001`, `ARCH-052-SHARED-003` |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
