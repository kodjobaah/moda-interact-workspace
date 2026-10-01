# ARCH-023 database tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_database`. Repository: `moda-interact-database`. Coordinator: `moda_architect`.

The initial Merchant Knowledge persistence design was consolidated into DATABASE-001 before implementation. DATABASE-002 and DATABASE-003 remain historical superseded definitions. DATABASE-004 is a later, narrowly bounded forward-migration correction discovered by the required COMMERCE-002 successor-release PostgreSQL proof; it does not reopen the Merchant Knowledge schema. DATABASE-005 is the narrow enum-only prerequisite for the Merchant Knowledge Background runtime lease identities discovered by BACKGROUND-004.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-merchant-knowledge-schema.md) | Persist the complete Merchant Knowledge, Store Profile and generic plan-feature schema | Complete — Accepted Attempt 2 | - |
| [DATABASE-002](DATABASE-002-persist-localised-store-category-prompt-configuration.md) | Historical split Store Category/prompt persistence | Superseded by DATABASE-001 | - |
| [DATABASE-003](DATABASE-003-persist-merchant-knowledge-pgvector.md) | Historical split Merchant Knowledge/pgvector persistence | Superseded by DATABASE-001 | - |
| [DATABASE-004](DATABASE-004-allow-historical-release-feature-snapshots.md) | Permit exact same-Feature historical immutable release snapshots while retaining current/invalid snapshot guards | Complete — Accepted Attempt 1 | ARCH-021-DATABASE-003, DATABASE-001 |
| [DATABASE-005](DATABASE-005-add-merchant-knowledge-runtime-lease-names.md) | Add the two Merchant Knowledge Background runtime lease enum identities only | Ready — Attempt 2 evidence correction | DATABASE-001, DATABASE-004 |

## Execution frontier

```text
ARCH-023-DATABASE-001   Complete — Accepted Attempt 2
ARCH-023-DATABASE-004   Complete — Accepted Attempt 1
ARCH-023-DATABASE-005   Ready — Attempt 2 evidence correction
```

DATABASE-005's implementation is source-conformant but awaits the required durable launcher/worktree/synchronization/submodule evidence before architect acceptance. `ARCH-023-BACKGROUND-007` remains Pending on DATABASE-005, and `ARCH-023-BACKGROUND-004` remains Blocked behind BACKGROUND-007. No Background implementation is started by this review.
