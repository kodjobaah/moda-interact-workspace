# ARCH-052 — Gateway task index

Architecture: [`ARCH-052`](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Assigned agent: `moda_gateway`. Repository: `moda-interact-gateway`. Coordinator: `moda_architect`.

Task definitions are **portable / not materialised** in the developer Git environment. Individual task YAML is authoritative for status.

| Task | Objective | Status | Depends on |
|---|---|---|---|
| [GATEWAY-001](GATEWAY-001-configure-private-recovery-product-read-transport.md) | Route private product-image reads and declare independent HMAC secrets | Pending | `ARCH-052-COMMERCE-003`, `ARCH-052-API-002`, `ARCH-052-API-003`, `ARCH-052-API-004`, `ARCH-052-SHARED-003` |

Do not manually promote a dependent task until every dependency is marked `complete` in its individual task file and has an accepted review; external ARCH-049 dependencies use the same rule.
