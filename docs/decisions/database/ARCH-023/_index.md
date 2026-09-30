# ARCH-023 database tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_database`. Repository: `moda-interact-database`. Coordinator: `moda_architect`.

The current ARCH-023 database design is intentionally one coherent task. The earlier
2026-09-27 three-task split was superseded when the schema was consolidated before
implementation.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-merchant-knowledge-schema.md) | Persist the complete Merchant Knowledge, Store Profile and generic plan-feature schema | Complete — Accepted Attempt 2 | - |
| [DATABASE-002](DATABASE-002-persist-localised-store-category-prompt-configuration.md) | Historical split Store Category/prompt persistence | Superseded by DATABASE-001 | - |
| [DATABASE-003](DATABASE-003-persist-merchant-knowledge-pgvector.md) | Historical split Merchant Knowledge/pgvector persistence | Superseded by DATABASE-001 | - |

## Execution frontier

`ARCH-023-DATABASE-001` is **Complete / Accepted at Attempt 2**.

The database prerequisite remains satisfied. The two direct dependants now stand at:

```text
ARCH-023-SHARED-001  Ready
ARCH-023-ADMIN-002   Complete — Accepted Attempt 2
```

ADMIN-003 is now Ready because ADMIN-002 additionally completed; that promotion is tracked
in the Admin index and parent architecture and is not a new direct consequence of
DATABASE-001 acceptance alone.
