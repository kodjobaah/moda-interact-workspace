# ARCH-024 Gateway tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_gateway`.

Repository: `moda-interact-gateway`.

Coordinator: `moda_architect`.

ARCH-024 requires one infrastructure/deployment task after the application runtimes have adopted the database-backed OpenRouter credential contract.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [GATEWAY-001](GATEWAY-001-wire-database-backed-openrouter-runtime.md) | Share the accepted credential keyring with authorized runtimes and remove obsolete static Preview provider/model/API-key configuration | Complete (Accepted, Attempt 1) | ARCH-020-GATEWAY-003, ADMIN-003, COMMERCE-007, BACKGROUND-001 |

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

`ARCH-024-GATEWAY-001` is Complete / Accepted at Attempt 1. The shared keyring/writer ownership, Commerce-only HMAC, Preview kill switch, transcription boundary and removal of static Preview model credentials are accepted. All materialised ARCH-024 implementation tasks are now Complete.

The broader Docker/HAProxy harness was unavailable to the implementation executor, but no HAProxy/Docker/route file changed and the complete Blueprint positive/negative validation passed. Terminal integrated validation remains deliberately deferred to the later overlapping-architecture session already described above.
