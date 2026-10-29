# ARCH-052 — Api task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_api`. Repository: `moda-interact-api`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [API-001](API-001-migrate-woo-selected-discounts-to-canonical-set.md) | Move Woo offer Save/GET to canonical selected-discount storage | Pending | `ARCH-052-DATABASE-001`, `ARCH-052-SHARED-003` |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
