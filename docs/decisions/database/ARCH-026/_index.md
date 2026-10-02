# ARCH-026 Database tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_database`.

Repository: `moda-interact-database`.

Coordinator: `moda_architect`.

The database stream establishes only the minimum durable Woo installation identity needed by the later hosted Moda API. Shared tenant/platform state remains in `commerce`; Woo-specific installation/authentication state is persisted in the dedicated `woocommerce` PostgreSQL schema. It does not generalise billing, customers or recovery persistence.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-woocommerce-installation-identity.md) | Add `commerce.Shop` platform identity plus one secure `woocommerce.WooCommerceInstallation` record per Woo tenant | Ready | - |

## Execution frontier

```text
ARCH-026-DATABASE-001 is Ready and may execute independently of the blocked/pending Woo plugin tasks.
```

`ARCH-026-API-002` depends on this database capability and will consume the architect-accepted database commit through the API repository's nested `database/` gitlink. Do not begin API-002 from DATABASE-001; the API task remains separately owned by `moda_api`.
