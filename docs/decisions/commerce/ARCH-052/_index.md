# ARCH-052 — Commerce task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_commerce`. Repository: `moda-interact-commerce`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [COMMERCE-001](COMMERCE-001-verify-shopify-discount-against-current-checkout.md) | Prove Shopify discount eligibility for a recovery checkout | Ready | — |
| [COMMERCE-002](COMMERCE-002-read-authoritative-shopify-checkout-product-image.md) | Read first checkout-product image from Shopify product facts | Ready | — |
| [COMMERCE-003](COMMERCE-003-serve-authenticated-private-shopify-recovery-reads.md) | Expose authenticated private Shopify discount-proof and product-image reads | Pending | `ARCH-052-COMMERCE-001`, `ARCH-052-COMMERCE-002`, `ARCH-052-SHARED-003` |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
