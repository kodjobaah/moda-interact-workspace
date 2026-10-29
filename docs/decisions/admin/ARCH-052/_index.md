# ARCH-052 — Admin task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_admin`. Repository: `moda-interact-admin`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-author-six-initial-outreach-template-variants.md) | Author and publish the six existing recovery purposes with basket copy | Pending | `ARCH-052-SHARED-003` |
| [ADMIN-002](ADMIN-002-author-optional-checkout-product-image-headers.md) | Author optional checkout-product IMAGE headers and approved text fallbacks | Pending | `ARCH-052-SHARED-003`, `ARCH-049-ADMIN-002` |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
