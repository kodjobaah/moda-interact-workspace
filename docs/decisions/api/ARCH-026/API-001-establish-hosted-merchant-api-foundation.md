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
claimed_at: 2026-10-02T19:31:29Z
attempt: 2
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

- [x] Bootstrap the `moda-interact-api` Node/TypeScript repository foundation on the canonical workspace Node version.
- [x] Add the canonical `moda-interact-database` repository as nested `database/` submodule.
- [x] Configure Prisma generation from `database/prisma/schema.prisma` without schema duplication.
- [x] Add bounded runtime configuration for `DATABASE_URL` and `PORT`.
- [x] Implement the HTTP server entry point and deterministic startup lifecycle.
- [x] Implement `GET /health/live` without database dependency.
- [x] Implement `GET /health/ready` with a bounded PostgreSQL probe and 503 failure behavior.
- [x] Implement bounded 404 handling for all other routes.
- [x] Implement graceful SIGTERM/SIGINT shutdown including Prisma disconnect.
- [x] Integrate the canonical Shared structured logger without secret/payload logging.
- [x] Add focused tests for health/readiness, unknown routes, config safety and shutdown behavior.
- [x] Add repository-local install/dev/build/start/typecheck/lint/test/Prisma commands.
- [x] Document clean-checkout local execution and environment requirements in README.
- [x] Verify no merchant business API, Redis/BullMQ or Woo/provider behavior has been introduced.

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

- [x] `moda-interact-api` is a backend-only Node/TypeScript service with no React/Next/browser runtime.
- [x] `package.json` pins the repository to the canonical Node 24.19.0 runtime contract.
- [x] The repository contains the canonical `database/` submodule pointing to `moda-interact-database`.
- [x] Prisma generation uses `database/prisma/schema.prisma` and no duplicate local schema exists.
- [x] Prisma versions are compatible with the canonical database repository and were not independently upgraded.
- [x] `DATABASE_URL` is never logged or returned to clients.
- [x] Supplied `PORT` is honored and the server binds to `0.0.0.0`.
- [x] `GET /health/live` returns 200 while PostgreSQL is intentionally unavailable.
- [x] `GET /health/ready` returns 200 against a disposable/reachable PostgreSQL database.
- [x] `GET /health/ready` returns 503 when PostgreSQL is unavailable.
- [x] Readiness performs no DDL/migration/business-state mutation.
- [x] Unknown routes return bounded 404 responses.
- [x] SIGTERM/SIGINT stop the listener and disconnect Prisma cleanly.
- [x] Generic structured logging uses the Shared logger.
- [x] No Woo installation authentication, Shop business route, billing, recovery, Redis/BullMQ or provider workflow is implemented.
- [x] Clean install/typecheck/test/build passes from the task worktree with recursively initialized submodules.

## Validation

Run the commands actually declared by the repository and record exact commands/results.

Required validation categories:

- [x] canonical Node bootstrap from the launcher/workspace;
- [x] clean npm install from lockfile;
- [x] recursive submodule initialization/proof;
- [x] Prisma generation from `database/prisma/schema.prisma`;
- [x] typecheck;
- [x] lint;
- [x] focused unit/integration tests;
- [x] production build;
- [x] bounded local start smoke;
- [x] `GET /health/live` 200 smoke;
- [x] live endpoint remains 200 with PostgreSQL unavailable;
- [x] disposable PostgreSQL readiness 200 proof;
- [x] unavailable PostgreSQL readiness 503 proof;
- [x] unknown route 404 proof;
- [x] secret-redaction/log negative check;
- [x] graceful SIGTERM/SIGINT shutdown smoke;
- [x] static audit proving no Redis/BullMQ, Woo billing/provider or merchant business route was introduced;
- [x] `git diff --check`;
- [x] repository clean-state check after commit/push.
Canonical bootstrap selected Node `24.19.0` and npm `11.17.0`. API implementation commit `6635491` was pushed to `origin/task/ARCH-026-API-001`; the API worktree is clean and tracks that task branch.

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

Review

### Files Changed

API repository: `.gitmodules`, `database/` gitlink, `.gitignore`, `eslint.config.js`, `package.json`, `package-lock.json`, TypeScript configs, `src/`, and `README.md`.

### Work Completed

Added the server-only TypeScript runtime, bounded runtime configuration, native `node:http` health server, Prisma readiness probe, Shared structured logging, focused tests, local commands, and clean-checkout documentation. The canonical database submodule is pinned at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

### Validation Results

Canonical bootstrap selected Node `24.19.0` and npm `11.17.0`. `npm ci`, `npm run prisma:generate`, `npm run typecheck`, `npm run lint`, `npm test` (8 passed), and `npm run build` passed from the API task worktree. Prisma CLI and `@prisma/client` are both `6.19.3`.

### Attempt 2 Launcher and Provisioning Evidence

The deterministic launcher prepared and claimed Attempt 2 for executor `copilot`. The claim advanced the task from `ready`/Attempt 1 to `in_progress`/Attempt 2 and was committed and pushed as `8ccefb61a1ab39d242be179619b1c74670f52f51`.

Physical worktree isolation:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace` (launcher confirmed it was not derived from a previous task worktree).
- Parent task worktree and branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-API-001`, `task/ARCH-026-API-001`.
- Implementation worktree and branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-API-001`, `task/ARCH-026-API-001`.
- Shared workspace checkout switched or mutated for task work: no. Shared implementation checkout switched or mutated for task work: no. Another task's worktree reused: no; launcher reused only the two canonical worktrees above.

Start-of-attempt synchronization, from the prepared packet:

- Parent task remote branch fast-forwarded: `not-needed`; parent `origin/main` incorporated: `already-current` (parent head `2acf128c1be1d0dd7db51fd03f65cbe3dff74ece`).
- Implementation task remote branch fast-forwarded: `not-needed`; implementation `origin/main` incorporated: `already-current` (implementation head `6635491eb6a99b628b2fbc9a129ba0599afa1f69`).

Repository-provisioning gate and recursive submodules:

- The canonical workspace repository/submodule `moda-interact-api` resolved at `/Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-api`.
- Launcher route: domain/folder `API` / `api`; logical owner: `moda_api`; assigned repository: `moda-interact-api`.
- `git submodule sync --recursive` and `git submodule update --init --recursive`: both passed. Recursive submodule status: `ready`; `database/` was initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`, matching the implementation repository's gitlink.

Durable publication history:

- Implementation commit `6635491eb6a99b628b2fbc9a129ba0599afa1f69` is pushed to `origin/task/ARCH-026-API-001`.
- Parent report publication sequence supplied with the Attempt 1 review: `72a5959c`, then `4d108c8c`.
- Architect synchronization commit `2acf128c1be1d0dd7db51fd03f65cbe3dff74ece` incorporated current `origin/main`; Attempt 2 claim commit `8ccefb61a1ab39d242be179619b1c74670f52f51` is pushed on the parent task branch. This Attempt 2 Completion Report update will be committed and pushed on that same branch.
- Architect synchronization commit `2acf128c1be1d0dd7db51fd03f65cbe3dff74ece` incorporated current `origin/main`; Attempt 2 claim commit `8ccefb61a1ab39d242be179619b1c74670f52f51` and the Attempt 2 Completion Report commit `4ba522b2` are pushed on the parent `origin/task/ARCH-026-API-001` branch. Both the parent and implementation task worktrees are clean and remote-aligned; final `git diff --check` passed in both.

Live smoke used port `43127` and disposable PostgreSQL 16: liveness 200, readiness 200 while PostgreSQL was reachable, readiness 503 after PostgreSQL stopped, liveness remained 200 during that outage, and an unknown route returned 404. SIGTERM emitted bounded shutdown-started/completed logs. Startup/readiness logs and HTTP bodies contained no database URL or credentials. `git diff --check` passed.

Static source and direct dependency checks found no migration, merchant/business route, Woo/provider, billing, recovery, Redis or BullMQ implementation. The lockfile does contain BullMQ transitively via `@modainteract/moda-interact-shared@1.1.0` -> `bullmq-otel@2.0.1`; the API does not import or use it. `npm ci` reported 3 high audit findings in the Prisma CLI dependency chain (`deepmerge-ts`); no forced dependency changes were made because Prisma is pinned to the canonical database version. npm install-script approval warnings did not prevent Prisma generation or validation.

### Deviations

None.

### Assumptions

- The repository-provisioning readiness gate was satisfied before implementation: the canonical `moda-interact-api` workspace submodule/repository, `API` launcher route and `moda_api` owner were resolved by the launcher; recursive implementation submodules materialised successfully.
- The current canonical workspace Node runtime is 24.19.0.
- The current database repository continues to own schema/migrations and Prisma version alignment.
- API-002 will define Woo installation authentication after this foundation is accepted.

### Unresolved Issues

Implementation and executable validation are complete. Both task worktrees are clean and synchronized with their corresponding `origin/task/ARCH-026-API-001` branches. The transitive Shared-package BullMQ dependency and Prisma CLI audit findings are disclosed above for review.

### Architectural Concerns

The required Shared logger package brings BullMQ transitively into the install tree although no queue behavior is used by this service. `npm audit` reports 3 high findings in Prisma CLI's transitive dependency chain; resolving them must preserve canonical Prisma `6.19.3` alignment.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implementation is architecture-conformant. The server-only Node/TypeScript runtime, canonical nested database/Prisma consumption, dependency-independent liveness, PostgreSQL-backed readiness, bounded unknown-route behavior, Shared structured logging, graceful shutdown and explicit exclusion of merchant/Woo/queue business behavior match the task contract.

The remaining deficiency is durable execution evidence, not application code. The Completion Report says both task worktrees are clean and synchronized and records the implementation head, but it does not record the launcher-resolved physical-isolation/start-of-attempt synchronization packet required by the architect protocol. It also leaves repository provisioning as an assumption rather than recording that the API repository/submodule/launcher readiness gate was actually satisfied before execution, and it does not durably identify the final parent report publication heads supplied with the review submission. Chat-only evidence is insufficient for cross-environment handoff.

The disclosed `npm audit` findings in the Prisma CLI dependency chain and BullMQ's transitive presence through the required Shared package do not block this task. No queue behavior is imported or implemented, and Prisma remains aligned to the canonical database version.

### Reviewed Files

- `moda-interact-api/package.json`
- `moda-interact-api/package-lock.json`
- `moda-interact-api/.gitmodules`
- `moda-interact-api/src/index.ts`
- `moda-interact-api/src/runtime-config.ts`
- `moda-interact-api/src/database.ts`
- `moda-interact-api/src/server.ts`
- `moda-interact-api/src/runtime-config.test.ts`
- `moda-interact-api/src/server.test.ts`
- `moda-interact-api/README.md`
- this task's Completion Report
- parent `ARCH-026` architecture and API task index

### Validation Reviewed

Reviewed the recorded clean `npm ci`, Prisma generation, typecheck, lint, 8-test suite, production build, disposable-PostgreSQL liveness/readiness 200/503 proofs, unknown-route 404 proof, secret/log negative checks, SIGTERM shutdown smoke, static scope audit and `git diff --check`. The submitted review archive contains no dependency install or Git metadata suitable for an independent Node-24/Git rerun, so this review does not replace the recorded task-worktree validation.

### Architecture Conformance

The implementation conforms to the ARCH-026 API-001 runtime, repository-ownership, database, security and scope boundaries. Acceptance is withheld only until the required launcher/worktree/VCS evidence is made durable in the Completion Report. No implementation source change is requested.

### Follow-up

Attempt 2 is an evidence-only correction contract:

- **A1-R1 — Record the prepared launcher/worktree packet.** In the Completion Report, record the launcher-resolved canonical workspace root, dedicated parent task worktree and branch, dedicated `moda-interact-api` implementation task worktree and branch, and the explicit evidence that execution did not occur from a shared/default checkout or another task's worktree. Record start-of-attempt synchronization for both repositories, including task-branch remote alignment and the required `origin/main` incorporation state.
- **A1-R2 — Record repository-provisioning and recursive-submodule evidence as facts.** Replace the stale provisioning assumption with the verified readiness-gate result: canonical `moda-interact-api` workspace submodule/repository, `API` launcher route/logical owner, recursively materialised nested submodules, and the `database/` gitlink SHA used by the attempt. Do not change database schema or dependency versions.
- **A1-R3 — Record final durable Git publication state.** Record implementation commit `6635491` as pushed to `origin/task/ARCH-026-API-001`; record the parent report publication sequence supplied with the review (`72a5959c`, then final report head `4d108c8c`) and prove the final parent and implementation task worktrees are clean and remote-aligned. Rerun `git diff --check` as the bounded final evidence check.

No API source/test/dependency changes are required. Do not rerun the implementation validation suites merely for this correction unless source, dependency, database gitlink or runtime configuration changes. Reclaim the same task through the normal launcher; preserve Attempt 1 history and let the next authorized claim increment to Attempt 2. API-002 remains Pending until API-001 and DATABASE-001 are both architect-accepted Complete.
