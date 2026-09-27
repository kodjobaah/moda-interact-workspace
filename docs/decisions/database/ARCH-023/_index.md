# ARCH-023 database tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md).

Assigned agent: `moda_database`. Repository: `moda-interact-database`. Coordinator: `moda_architect`.

These are portable task definitions from the 2026-09-27 review patch; individual task YAML is authoritative. No task branch/worktree is materialised by this patch.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-plan-feature-configuration.md) | Persist generic plan-feature configuration | Ready | - |
| [DATABASE-002](DATABASE-002-persist-localised-store-category-prompt-configuration.md) | Persist localised Store Category/prompt configuration | Ready | - |
| [DATABASE-003](DATABASE-003-persist-merchant-knowledge-pgvector.md) | Persist Merchant Knowledge + pgvector | Ready | - |

## Execution frontier

Ready: `ARCH-023-DATABASE-001`, `ARCH-023-DATABASE-002`, `ARCH-023-DATABASE-003`
