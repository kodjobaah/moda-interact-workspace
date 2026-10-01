# ARCH-024 Gateway tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_gateway`.

Repository: `moda-interact-gateway`.

Coordinator: `moda_architect`.

ARCH-024 requires one infrastructure/deployment task after the application runtimes have adopted the database-backed OpenRouter credential contract.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [GATEWAY-001](GATEWAY-001-wire-database-backed-openrouter-runtime.md) | Share the accepted credential keyring with authorized runtimes and remove obsolete static Preview provider/model/API-key configuration | Pending | ARCH-020-GATEWAY-003, ADMIN-003, COMMERCE-007, BACKGROUND-001 |

## Deployment boundary

Gateway changes configuration only; it adds no new service/worker/route/database/Redis resource.

Normal OpenRouter credential replacement is a database operation and does not require a Render configuration change or runtime restart. Gateway owns the rarer encryption-keyring distribution/rotation boundary.

## System validation

No ARCH-024 system-test task is materialised in this architecture session. After GATEWAY-001 and all implementation tasks are architect-accepted Complete, a later architect session must define the terminal integrated validation for the final overlapping architecture set.
