# ARCH-023 database tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_database`. Repository: `moda-interact-database`. Coordinator: `moda_architect`.

The initial ARCH-023 Merchant Knowledge database design was intentionally consolidated into DATABASE-001. The earlier 2026-09-27 DATABASE-002/DATABASE-003 split was superseded before implementation.

DATABASE-004 is a later, narrowly bounded forward-migration correction discovered by the required COMMERCE-002 Attempt 3 PostgreSQL successor-release proof. It does not reopen the Merchant Knowledge schema and does not supersede DATABASE-001.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-merchant-knowledge-schema.md) | Persist the complete Merchant Knowledge, Store Profile and generic plan-feature schema | Complete — Accepted Attempt 2 | - |
| [DATABASE-002](DATABASE-002-persist-localised-store-category-prompt-configuration.md) | Historical split Store Category/prompt persistence | Superseded by DATABASE-001 | - |
| [DATABASE-003](DATABASE-003-persist-merchant-knowledge-pgvector.md) | Historical split Merchant Knowledge/pgvector persistence | Superseded by DATABASE-001 | - |
| DATABASE-004 | Permit exact same-Feature historical immutable release snapshots while retaining current/invalid snapshot guards | Defined — portable task ready for materialization | ARCH-021-DATABASE-003, DATABASE-001 |

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


## COMMERCE-002 database blocker

The architect-defined `ARCH-023-DATABASE-004` corrects only `commerce.arch021_release_feature_guard()` so a new release may insert either the current Feature Behaviour prompt or an exact immutable historical prompt already persisted for that same Feature. Arbitrary never-published stale text, cross-Feature historical text and mutation/deletion of release Feature snapshots remain rejected.

The portable canonical task definition is supplied separately as:

```text
ARCH-023-DATABASE-004-allow-historical-release-feature-snapshots.md
```

Until it is materialized and architect-accepted Complete:

```text
ARCH-023-DATABASE-004  Ready once materialized
ARCH-023-COMMERCE-002  Blocked — Attempt 3 retained
```
