# ARCH-052 — Woocommerce task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_woocommerce`. Repository: `moda-interact-woocommerce`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [WOOCOMMERCE-001](WOOCOMMERCE-001-expose-read-only-native-coupon-verification.md) | Expose read-only native Woo coupon eligibility proof | Ready | — |
| [WOOCOMMERCE-002](WOOCOMMERCE-002-create-secure-customer-initiated-checkout-resume.md) | Provide secure customer-initiated Woo checkout restoration link | Ready | — |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
