# ARCH-052 — Database task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_database`. Repository: `moda-interact-database`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-merchant-selected-discount-sets.md) | Persist canonical tenant-scoped selected discount sets | Ready | — |
| [DATABASE-002](DATABASE-002-persist-checkout-product-media-provenance.md) | Persist one bounded checkout-product media selection | Ready | — |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
