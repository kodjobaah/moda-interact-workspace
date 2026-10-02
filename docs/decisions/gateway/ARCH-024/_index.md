# ARCH-024 Gateway tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_gateway`.

Repository: `moda-interact-gateway`.

Coordinator: `moda_architect`.

ARCH-024 requires one infrastructure/deployment task after the application runtimes have adopted the database-backed OpenRouter credential contract.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [GATEWAY-001](GATEWAY-001-wire-database-backed-openrouter-runtime.md) | Share the accepted credential keyring with authorized runtimes and remove obsolete static Preview provider/model/API-key configuration | Ready | ARCH-020-GATEWAY-003, ADMIN-003, COMMERCE-007, BACKGROUND-001 |

## Dependency rationale

These cross-application dependencies are intentional **deployment-cutover** gates, not source-code dependencies:

- ADMIN-003 proves the credential writer uses the accepted keyring/AAD contract;
- COMMERCE-007 proves Commerce consumes the database-backed OpenRouter credential and no longer reads obsolete Preview provider/model/API-key variables;
- BACKGROUND-001 proves the production worker consumes the same database-backed credential/runtime contract.

BACKGROUND-002 is not required for deployment/keyring cutover; deleting the unused local one-node LangGraph wrapper is independent cleanup.

## Deployment boundary

Gateway changes configuration only; it adds no new service/worker/route/database/Redis resource.

Normal OpenRouter credential replacement is a database operation and does not require a Render configuration change or runtime restart. Gateway owns the rarer encryption-keyring distribution/rotation boundary.

## System validation

No ARCH-024 system-test task is materialised in this architecture session. After GATEWAY-001 and all implementation tasks are architect-accepted Complete, a later architect session must define the terminal integrated validation for the final overlapping architecture set.

## Current gate

ARCH-024 application-side cutover prerequisites are now satisfied: `ARCH-024-ADMIN-003`, `ARCH-024-COMMERCE-007`, and `ARCH-024-BACKGROUND-001` are Complete / architect-accepted.

`ARCH-020-GATEWAY-003` is now Complete / Accepted at Attempt 3. With ADMIN-003, COMMERCE-007 and BACKGROUND-001 already Complete, `ARCH-024-GATEWAY-001` is promoted **Pending -> Ready, Attempt 0, claim clear**. Readiness does not launch or claim the task.
