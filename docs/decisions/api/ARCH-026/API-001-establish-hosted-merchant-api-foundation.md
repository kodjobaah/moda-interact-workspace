---
id: ARCH-026-API-001
architecture_id: ARCH-026
title: Establish the hosted Moda merchant API foundation
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 12
executor: copilot
claimed_at: 2026-10-02T15:42:32Z
attempt: 1
depends_on: []
enables:
  - ARCH-026-API-002
created: 2026-10-02
updated: 2026-10-02
---

# Establish the hosted Moda merchant API foundation

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Establish `moda-interact-api` as the backend-only, Moda-hosted HTTP service that later ARCH-026 tasks can use as the trusted server-side boundary between merchant-controlled WooCommerce installations and Moda durable state.

The bounded runtime established by this task is:

```text
HTTP request
    |
    v
moda-interact-api
    |
    +-- liveness
    |
    `-- readiness -> PostgreSQL connectivity
```

This task proves only that the new service can build, start, expose deterministic health/readiness endpoints and reach Moda PostgreSQL through the canonical Prisma schema.

It MUST NOT implement Woo installation registration/authentication, merchant business queries/commands, event ingestion, Redis/BullMQ publication, billing, recovery, CommerceAgent or plugin-facing application endpoints.

## Context

ARCH-026 requires a hosted request/response backend because the WooCommerce extension executes inside merchant-controlled WordPress infrastructure and must never connect directly to Moda PostgreSQL, Redis/BullMQ or private service credentials.

The intended later path is:

```text
Woo Admin React
    -> local WordPress REST
    -> Moda PHP plugin
    -> authenticated HTTPS
    -> moda-interact-gateway
    -> moda-interact-api
    -> Moda application/domain services
    -> PostgreSQL
```

`moda-interact-api` is not another merchant-facing UI. It is a server-only TypeScript service.

It is also not a second Background service. Synchronous merchant queries/commands and authenticated external application ingress belong here; long-running/asynchronous business workflows continue to belong to `moda-interact-background`.

### Repository-provisioning readiness gate

This task is defined before the new implementation repository exists in the supplied workspace.

Before this task may transition from `pending` to `ready`, the architecture coordination layer MUST verify:

```text
workspace repository path:
    moda-interact-api/

Git repository:
    provisioned and reachable

default branch:
    main

workspace submodule:
    moda-interact-api
    registered at the canonical workspace path

logical owner:
    moda_api

launcher route:
    API
        folder: api
        repository: moda-interact-api
        agent: moda_api

agent definitions:
    .codex/agents/moda_api.toml
    .claude/agents/moda_api.agent.md
```

Use the workspace's canonical repository-provisioning workflow where available. Repository provisioning is a coordination prerequisite, not implementation work for this task.

The repository agent MUST NOT create a replacement repository, execute from a shared/default checkout, or bypass the launcher readiness gate.

## Scope

Create the initial server-only application foundation in:

```text
moda-interact-api/
```

Expected top-level areas include:

```text
package.json
package-lock.json
tsconfig.json
src/
  index.ts
  server.ts
  runtime-config.ts
  database.ts
  health/
    ...
tests/
database/                 # canonical moda-interact-database submodule
README.md
```

The exact internal file layout may vary if the repository agent can produce a clearer bounded structure, but responsibility boundaries below are mandatory.

### Runtime

Use the canonical workspace Node runtime:

```text
Node 24.19.0
```

The service MUST be TypeScript/Node and server-only.

Do not introduce React, Next.js, browser assets or a second merchant-facing UI.

Do not introduce a heavyweight application framework merely to expose two health endpoints. A bounded, production-suitable HTTP stack is sufficient. Record the selected HTTP stack in the Completion Report.

### Canonical database dependency

Consume the existing database repository as a nested submodule:

```text
database/ -> moda-interact-database
```

The API repository MUST generate/use Prisma from:

```text
database/prisma/schema.prisma
```

Align Prisma client/tooling versions with the canonical database repository. Do not independently upgrade Prisma in this task.

This task MUST NOT create or modify database schema/migrations.

### Runtime configuration

At minimum support:

```text
DATABASE_URL
PORT
```

`DATABASE_URL` is required for readiness/database operation.

`PORT` may use a bounded local-development default, but deployment must honor a supplied `PORT` value and bind to `0.0.0.0`.

Configuration validation must fail clearly without logging secrets.

Do not introduce Woo installation credentials, Redis URLs, billing credentials or provider secrets in this task.

### Liveness endpoint

Expose exactly one canonical liveness route:

```text
GET /health/live
```

Liveness proves the process can accept HTTP requests.

It MUST NOT require PostgreSQL, Redis or an external provider.

Expected behavior:

```text
HTTP 200
bounded JSON body
no secrets
no environment dump
```

### Readiness endpoint

Expose exactly one canonical readiness route:

```text
GET /health/ready
```

Readiness MUST perform a bounded PostgreSQL connectivity probe through the canonical Prisma client.

Expected behavior:

```text
PostgreSQL reachable:
    HTTP 200

PostgreSQL unavailable / Prisma cannot connect:
    HTTP 503
```

Do not run migrations, mutate application tables or perform broad schema inspection in the readiness request.

### Unknown/application routes

No merchant application endpoint is created by this task.

Requests outside the defined health/readiness surface MUST return a bounded 404 response.

Do not expose placeholder endpoints that imply installation authentication, Shop access or merchant functionality already exists.

### Process lifecycle

The service MUST:

- initialize the HTTP listener once;
- initialize the Prisma runtime once;
- handle `SIGTERM` and `SIGINT` without abandoning the listening socket/Prisma connection;
- stop accepting new requests during shutdown;
- disconnect Prisma before process exit where practical;
- avoid unhandled promise rejection during normal startup/shutdown paths.

### Logging

Use the canonical Shared structured logger:

```text
@modainteract/moda-interact-shared/logging
```

Do not create a competing generic JSON logger.

Startup, shutdown and readiness-failure logging must be bounded and must not include `DATABASE_URL`, authorization headers, credentials or complete request bodies.

Do not add custom HTTP request metrics/spans merely to duplicate standard framework/runtime telemetry.

### Repository commands

Provide clear repository-local commands for at least:

```text
npm run dev
npm run build
npm run start
npm run typecheck
npm run lint
npm test
npm run prisma:generate
```

The exact lint/test implementation is repository-local, but all commands must be deterministic from the lockfile and clean checkout.

## Out of Scope

- Woo installation connection/handshake.
- Installation credential generation, rotation or verification.
- HTTP authentication/authorization for Woo installations.
- Shop creation or lookup application logic.
- Provider-neutral onboarding lifecycle migration.
- Merchant Overview/Setup APIs.
- React/WordPress REST implementation.
- Woo plugin changes.
- Redis/BullMQ.
- Background workflows.
- Commerce-event ingress.
- Recovery processing.
- Product/coupon integration.
- Merchant Knowledge.
- CommerceAgent.
- WhatsApp/Meta.
- Billing or Woo Marketplace SaaS Billing API.
- Recovery-credit purchases.
- Database schema or migration changes.
- Gateway routing/Render Blueprint changes.
- Hosted deployment itself.
- Custom application metrics/dashboards.
- Public CORS policy for browser clients.
- API versioning/business-resource route design beyond the health surface.

## Requirements

### R1 — Backend-only service

`moda-interact-api` is a server-only Node/TypeScript deployable. It must not contain a merchant-facing frontend runtime.

### R2 — Canonical database consumption

The service consumes `moda-interact-database` through its nested `database/` submodule and generates Prisma from the canonical schema. It does not duplicate or fork the Prisma schema.

### R3 — No migration ownership

Startup/readiness MUST NOT run `prisma migrate`, DDL or seed operations. Database migration remains owned by `moda_database`/deployment sequencing.

### R4 — Liveness independent of dependencies

`GET /health/live` remains healthy when PostgreSQL is unavailable as long as the API process itself is serving requests.

### R5 — Readiness reflects PostgreSQL reachability

`GET /health/ready` returns 200 only when the bounded database probe succeeds and returns 503 when it cannot establish the required PostgreSQL connection.

### R6 — No fake business API

Unknown/non-health routes return 404. This task must not create placeholder merchant endpoints or fake installation state.

### R7 — Secret-safe configuration and logs

Missing/invalid runtime configuration produces bounded errors. `DATABASE_URL` and other secret values are never returned to clients or emitted in logs.

### R8 — Graceful process lifecycle

Normal SIGTERM/SIGINT shutdown closes the server and Prisma cleanly without creating a correctness dependency on telemetry/log transport.

### R9 — Shared logging only

Generic application logging uses `@modainteract/moda-interact-shared/logging`; no competing logger abstraction is introduced.

### R10 — Clean reproducible repository

A clean checkout with recursively initialized submodules and locked npm dependencies can install, generate Prisma, typecheck, test and build without borrowing dependencies from another checkout.

## Work Items

- [ ] Bootstrap the `moda-interact-api` Node/TypeScript repository foundation on the canonical workspace Node version.
- [ ] Add the canonical `moda-interact-database` repository as nested `database/` submodule.
- [ ] Configure Prisma generation from `database/prisma/schema.prisma` without schema duplication.
- [ ] Add bounded runtime configuration for `DATABASE_URL` and `PORT`.
- [ ] Implement the HTTP server entry point and deterministic startup lifecycle.
- [ ] Implement `GET /health/live` without database dependency.
- [ ] Implement `GET /health/ready` with a bounded PostgreSQL probe and 503 failure behavior.
- [ ] Implement bounded 404 handling for all other routes.
- [ ] Implement graceful SIGTERM/SIGINT shutdown including Prisma disconnect.
- [ ] Integrate the canonical Shared structured logger without secret/payload logging.
- [ ] Add focused tests for health/readiness, unknown routes, config safety and shutdown behavior.
- [ ] Add repository-local install/dev/build/start/typecheck/lint/test/Prisma commands.
- [ ] Document clean-checkout local execution and environment requirements in README.
- [ ] Verify no merchant business API, Redis/BullMQ or Woo/provider behavior has been introduced.

## Interfaces / Contracts

This task creates no merchant business contract and no cross-service event contract.

### HTTP liveness contract

```text
GET /health/live

200 when the API process is serving requests.
```

Response must be bounded JSON and must not expose runtime secrets or environment details.

### HTTP readiness contract

```text
GET /health/ready

200 when PostgreSQL connectivity probe succeeds.
503 when required PostgreSQL connectivity cannot be established.
```

### Database contract

Contract owner:

`moda-interact-database`

Consumed through:

```text
database/prisma/schema.prisma
@prisma/client generated from that schema
```

No schema ownership transfers to `moda_api`.

## Dependencies

None.

There are no architecture-task dependencies.

Execution nevertheless has the mandatory repository-provisioning readiness gate described under Context.

Until that gate is complete:

```text
status: pending
```

After repository/submodule provisioning and route/agent verification, `moda_architect` may promote this task to `ready` without changing implementation scope.

## Enables

- `ARCH-026-API-002`

API-002 is expected to own the secure Woo installation connection/authentication boundary after this foundation is accepted. Its exact contract remains subject to later architecture definition.

## Acceptance Criteria

- [ ] `moda-interact-api` is a backend-only Node/TypeScript service with no React/Next/browser runtime.
- [ ] `package.json` pins the repository to the canonical Node 24.19.0 runtime contract.
- [ ] The repository contains the canonical `database/` submodule pointing to `moda-interact-database`.
- [ ] Prisma generation uses `database/prisma/schema.prisma` and no duplicate local schema exists.
- [ ] Prisma versions are compatible with the canonical database repository and were not independently upgraded.
- [ ] `DATABASE_URL` is never logged or returned to clients.
- [ ] Supplied `PORT` is honored and the server binds to `0.0.0.0`.
- [ ] `GET /health/live` returns 200 while PostgreSQL is intentionally unavailable.
- [ ] `GET /health/ready` returns 200 against a disposable/reachable PostgreSQL database.
- [ ] `GET /health/ready` returns 503 when PostgreSQL is unavailable.
- [ ] Readiness performs no DDL/migration/business-state mutation.
- [ ] Unknown routes return bounded 404 responses.
- [ ] SIGTERM/SIGINT stop the listener and disconnect Prisma cleanly.
- [ ] Generic structured logging uses the Shared logger.
- [ ] No Woo installation authentication, Shop business route, billing, recovery, Redis/BullMQ or provider workflow is implemented.
- [ ] Clean install/typecheck/test/build passes from the task worktree with recursively initialized submodules.

## Validation

Run the commands actually declared by the repository and record exact commands/results.

Required validation categories:

- [ ] canonical Node bootstrap from the launcher/workspace;
- [ ] clean npm install from lockfile;
- [ ] recursive submodule initialization/proof;
- [ ] Prisma generation from `database/prisma/schema.prisma`;
- [ ] typecheck;
- [ ] lint;
- [ ] focused unit/integration tests;
- [ ] production build;
- [ ] bounded local start smoke;
- [ ] `GET /health/live` 200 smoke;
- [ ] live endpoint remains 200 with PostgreSQL unavailable;
- [ ] disposable PostgreSQL readiness 200 proof;
- [ ] unavailable PostgreSQL readiness 503 proof;
- [ ] unknown route 404 proof;
- [ ] secret-redaction/log negative check;
- [ ] graceful SIGTERM/SIGINT shutdown smoke;
- [ ] static audit proving no Redis/BullMQ, Woo billing/provider or merchant business route was introduced;
- [ ] `git diff --check`;
- [ ] repository clean-state check after commit/push.

The Completion Report MUST record:

```text
Node version
npm version
Prisma CLI version
@prisma/client version
database submodule SHA
selected HTTP stack
local test port
```

If a disposable PostgreSQL runtime is unavailable, leave the readiness integration criterion unchecked and report the task blocked rather than replacing it with a mock-only proof.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
        ->
set status: review
        ->
return to moda_architect
        ->
STOP
```

Do not begin API-002.

Do not implement Woo installation authentication, merchant queries/commands, event ingress, Gateway deployment or any other follow-on capability.

## Implementation Notes

Prefer the smallest coherent server-only HTTP runtime that satisfies this task. Do not introduce a frontend framework or a generic internal platform/framework merely because later API endpoints are expected.

Use dependency injection at the server/database boundary sufficiently to make liveness/readiness behavior testable without duplicating Prisma or logging abstractions.

Read `docs/observability/shared-logging.md` before adding generic runtime logging.

The API service will eventually sit behind `moda-interact-gateway`; do not independently expose/deploy it or edit the Render Blueprint in this task.

Normal execution must use the canonical `/moda-task` preparation flow after the `moda-interact-api` repository provisioning gate is satisfied.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- The repository will be provisioned as `moda-interact-api` before task execution.
- The current canonical workspace Node runtime is 24.19.0.
- The current database repository continues to own schema/migrations and Prisma version alignment.
- API-002 will define Woo installation authentication after this foundation is accepted.

### Unresolved Issues

None within this task's bounded foundation scope.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
