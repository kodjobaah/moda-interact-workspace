# ARCH-052 — Background task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_background`. Repository: `moda-interact-background`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-snapshot-authorised-discount-policy-at-attempt.md) | Freeze effective selected-discount policy at initial attempt creation | Pending | `ARCH-052-DATABASE-001`, `ARCH-052-SHARED-003`, `ARCH-052-SHOPIFY-001`, `ARCH-052-API-001` |
| [BACKGROUND-002](BACKGROUND-002-discover-bounded-offer-candidates.md) | Discover all relevant catalogue candidates with bounded pagination | Pending | `ARCH-052-BACKGROUND-001` |
| [BACKGROUND-003](BACKGROUND-003-connect-shopify-woo-live-eligibility-providers.md) | Wire independent Shopify and Woo checkout-specific eligibility adapters | Pending | `ARCH-052-BACKGROUND-002`, `ARCH-052-COMMERCE-001`, `ARCH-052-WOOCOMMERCE-001` |
| [BACKGROUND-004](BACKGROUND-004-wire-bounded-ai-offer-selector.md) | Connect approved AI recommendation to verified offer shortlist | Pending | `ARCH-052-BACKGROUND-003` |
| [BACKGROUND-005](BACKGROUND-005-bind-basket-summary-and-merchant-context.md) | Build deterministic checkout-item summary and merchant display bindings | Pending | `ARCH-052-SHARED-003` |
| [BACKGROUND-006](BACKGROUND-006-resolve-fresh-woo-resume-checkout-links.md) | Resolve fresh authenticated Woo restore links at initial send preparation | Pending | `ARCH-052-WOOCOMMERCE-002` |
| [BACKGROUND-007](BACKGROUND-007-prepare-shop-scoped-recovery-product-image.md) | Normalize and cache optional checkout-product IMAGE header | Pending | `ARCH-052-DATABASE-002`, `ARCH-052-SHARED-003`, `ARCH-052-COMMERCE-002`, `ARCH-049-BACKGROUND-001`, `ARCH-049-BACKGROUND-002`, `ARCH-049-BACKGROUND-004` |
| [BACKGROUND-008](BACKGROUND-008-integrate-three-modes-into-initial-whatsapp-send.md) | Integrate all three offer modes and fallback templates at final initial send | Pending | `ARCH-052-BACKGROUND-003`, `ARCH-052-BACKGROUND-004`, `ARCH-052-BACKGROUND-005`, `ARCH-052-BACKGROUND-006`, `ARCH-052-BACKGROUND-007`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002` |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
