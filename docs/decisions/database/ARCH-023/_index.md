# ARCH-023 database tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_database`. Repository: `moda-interact-database`. Coordinator: `moda_architect`.

The initial Merchant Knowledge persistence design was consolidated into DATABASE-001 before implementation. DATABASE-002 and DATABASE-003 remain historical superseded definitions. DATABASE-004 is a later, narrowly bounded forward-migration correction discovered by the required COMMERCE-002 successor-release PostgreSQL proof; it does not reopen the Merchant Knowledge schema. DATABASE-005 is the narrow database-owned prerequisite discovered by BACKGROUND-004 Attempt 1: it adds only the two Merchant Knowledge runtime lease enum values required by the already-approved Background scheduler design.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-merchant-knowledge-schema.md) | Persist the complete Merchant Knowledge, Store Profile and generic plan-feature schema | Complete — Accepted Attempt 2 | - |
| [DATABASE-002](DATABASE-002-persist-localised-store-category-prompt-configuration.md) | Historical split Store Category/prompt persistence | Superseded by DATABASE-001 | - |
| [DATABASE-003](DATABASE-003-persist-merchant-knowledge-pgvector.md) | Historical split Merchant Knowledge/pgvector persistence | Superseded by DATABASE-001 | - |
| [DATABASE-004](DATABASE-004-allow-historical-release-feature-snapshots.md) | Permit exact same-Feature historical immutable release snapshots while retaining current/invalid snapshot guards | Complete — Accepted Attempt 1 | ARCH-021-DATABASE-003, DATABASE-001 |
| [DATABASE-005](DATABASE-005-add-merchant-knowledge-runtime-lease-names.md) | Add the two exact Merchant Knowledge distributed-scheduler lease enum identities | Ready | DATABASE-001, DATABASE-004 |

## Execution frontier

```text
ARCH-023-DATABASE-001   Complete — Accepted Attempt 2
ARCH-023-DATABASE-004   Complete — Accepted Attempt 1
ARCH-023-DATABASE-005   Ready
```

DATABASE-005 is now the executable database frontier required to unblock the Merchant Knowledge worker entrypoint. When accepted it enables BACKGROUND-007; it does not itself resume BACKGROUND-004.

DATABASE-004 was consumed by the now-accepted `ARCH-023-COMMERCE-002` successor-release implementation. DATABASE-005 is independent of that Commerce correction and exists only to unblock the Merchant Knowledge Background scheduler lease contract.
