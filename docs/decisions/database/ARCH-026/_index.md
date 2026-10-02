# ARCH-026 Database tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_database`.

Repository: `moda-interact-database`.

Coordinator: `moda_architect`.

The database stream establishes only the minimum durable Woo installation identity needed by the later hosted Moda API. It does not generalise billing, customers or recovery persistence.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-woocommerce-installation-identity.md) | Add explicit Shop platform identity and one secure WooCommerce installation/credential record per Woo tenant | Ready | - |

## Execution frontier

```text
ARCH-026-DATABASE-001 is Ready and may execute independently of the blocked/pending Woo plugin tasks.
```

A later hosted-API installation/authentication task will depend on this database capability once that API boundary is materialised. Do not begin such API work from DATABASE-001.
