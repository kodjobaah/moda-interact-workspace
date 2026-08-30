---
id: ARCH-002-SHOPIFY-001
architecture_id: ARCH-002
title: Add Shopify service health and readiness
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-GATEWAY-001
enables: []
created: 2026-08-29
updated: 2026-08-30
---

# Add Shopify Service Health and Readiness

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide deterministic, cheap liveness and dependency-aware readiness endpoints
suitable for Render private-service deployment of `moda-interact` in test and
production.

## Context

Accepted discovery found no dedicated health/readiness route in the Shopify
application.

GATEWAY-003 needs concrete health paths rather than inferred routes.

## Scope

Implement the architecture-level operational contract:

```text
GET /health
GET /ready
```

`/health` is process liveness.

`/ready` is dependency readiness for dependencies required to safely accept
normal application/webhook work.

Add tests and document status/response semantics.

## Out of Scope

- gateway/reverse-proxy configuration;
- Render Blueprint changes;
- changing Shopify webhook business behaviour;
- database schema changes;
- provider API health calls;
- returning sensitive dependency details.

## Requirements

`GET /health`:

- must remain cheap;
- must not call Shopify, Redis, PostgreSQL or other external providers merely to
  prove process liveness;
- returns a successful HTTP status when the application process is healthy;
- exposes no secrets/tenant data.

`GET /ready`:

- must use bounded checks;
- must verify Redis where queue publication is required for safe request
  handling;
- must verify PostgreSQL where application request handling requires it;
- returns success only when required dependencies are ready;
- returns a predictable non-success status when a required dependency is
  unavailable;
- must not call Shopify or other provider APIs;
- must not mutate business state.

The readiness implementation must be suitable as the Render deployment health
path.

Both endpoints must behave identically in test and production; only dependency
configuration differs.

Do not expose connection strings, host credentials, tenant identifiers or raw
exception objects.

Health routes are operational routes. GATEWAY-003 decides their Render
health-check wiring; this task does not make an otherwise private service
public.

## Work Items

- [x] implement `GET /health`;
- [x] implement `GET /ready`;
- [x] add bounded Redis readiness check;
- [x] add bounded PostgreSQL readiness check where required;
- [x] add success/failure tests;
- [x] add sensitive-response tests;
- [x] document status/response semantics;
- [x] verify liveness performs no provider/dependency work.

## Interfaces / Contracts

Produces:

```text
GET /health
GET /ready
```

for consumption by:

```text
ARCH-002-GATEWAY-003
ARCH-002-GATEWAY-004
ARCH-002-SYSTEM-TEST-001
```

Recommended Render deployment-health target:

```text
/ready
```

with `/health` retained as process-liveness diagnostics.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

None.

## Acceptance Criteria

- [x] `GET /health` returns success for a healthy process without external
      dependency calls;
- [x] `GET /ready` succeeds when required Redis/PostgreSQL dependencies are
      available;
- [x] `GET /ready` fails predictably when a required dependency is unavailable;
- [x] checks are bounded/non-mutating;
- [x] responses expose no sensitive data;
- [x] normal Shopify routes/webhook behaviour are unchanged;
- [x] test and production share the same route semantics.

## Validation

- [x] unit/integration tests;
- [x] typecheck (health/readiness code clean; pre-existing unrelated errors
      recorded in the Completion Report);
- [x] production build;
- [x] dependency-success/failure tests;
- [x] liveness no-dependency-call test;
- [x] sensitive-output review.

## Implementation Notes

Use repository-local route conventions while preserving the exact operational
paths above.

Do not add gateway behaviour here.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation:

- `moda-interact/app/routes/health.ts` — new `GET /health` liveness loader:
  returns `200` with `{ status: "ok" }` and `Cache-Control: no-store`;
  performs no dependency/provider calls.
- `moda-interact/app/routes/ready.ts` — new `GET /ready` readiness loader:
  returns `200` when `checkReadiness()` reports ready, otherwise `503`;
  body exposes only check names and booleans; `Cache-Control: no-store`.
- `moda-interact/app/services/health/health-check.server.ts` — Redis and
  PostgreSQL readiness checks:
  - Redis PING bounded via `connectTimeout`/`withTimeout`, `retryStrategy`
    disabled; short-lived client disconnected in `finally`;
  - purpose-built short-lived `pg.Client` probe with
    `connectionTimeoutMillis`, `query_timeout` and `statement_timeout`;
  - `checkPostgresReadiness()` always invokes probe `end()` in `finally`;
  - no `Promise.race` wrapper around the PostgreSQL probe.
- `moda-interact/app/routes.js` — routes registered via `flatRoutes()`; the
  `health`/`ready` file routes are picked up automatically.

Tests:

- `moda-interact/tests/unit/health/health-route.test.ts` — liveness status,
  no-dependency-call, `no-store`.
- `moda-interact/tests/unit/health/ready-route.test.ts` — 200/503 mapping,
  check body, sensitive-output restriction.
- `moda-interact/tests/unit/health/health-check.server.test.ts` — Redis and
  PostgreSQL readiness behaviour, bounding, probe options, and the
  `PostgresProbeFactory` `end()` lifecycle contract (success, connect failure,
  query failure, driver query timeout, teardown-error swallowing).
- `moda-interact/tests/unit/health/postgres-probe.integration.test.ts` — real
  `pg` driver against a local black-hole TCP server; validates the probe
  settles via the driver-level connection bound.

Documentation:

- `moda-interact/README.md` — added operational `/health` and `/ready`
  documentation and the `/ready` Render deployment health path.
- `docs/decisions/shopify/ARCH-002/SHOPIFY-001-add-health-readiness.md` —
  reconciled Work Items, Acceptance Criteria, Validation checkboxes and the
  Completion Report (this file).

### Work Completed

- `GET /health` process liveness (200, `no-store`, dependency-free).
- `GET /ready` dependency readiness (200 only when Redis and PostgreSQL are
  ready; 503 otherwise; bounded, non-mutating checks; sensitive-free body).
- Bounded Redis PING readiness using a short-lived ioredis client.
- Bounded PostgreSQL `SELECT 1` readiness using a short-lived `pg.Client` with
  `connectionTimeoutMillis`, `query_timeout` and `statement_timeout`; `end()`
  always invoked in `finally`.
- Route tests, readiness unit tests, sensitive-response tests, and the
  real-driver black-hole integration test.
- Repository operational documentation for `/health` and `/ready`.
- PostgreSQL probe comments corrected to state precisely that connection
  acquisition and query execution are driver-bounded and that `end()` is
  invoked in `finally`; implementation unchanged.

### Validation Results

Executed 2026-08-30 in `moda-interact` (Node v24.19.0, npm 11.17.0).

- Focused health/readiness tests (`npx vitest run tests/unit/health`):
  **4 test files passed, 28 tests passed** (Duration 1.98s). Includes the
  PostgreSQL probe unit tests and the real-driver black-hole integration test.
- Full test suite (`npm run test`): **9 test files passed, 59 tests passed**
  (Duration 2.19s).
- Typecheck (`npm run typecheck`): **exit code 2 with 48 pre-existing errors**,
  all in files unrelated to this task (`app/db.server.js`,
  `app/routes/_index/route.jsx`, `app/routes/app._index.jsx`,
  `app/routes/app.jsx`, `app/routes/app.usage.jsx`, `app/routes/auth.$.jsx`,
  `app/routes/auth.login/error.server.jsx`,
  `app/routes/auth.login/route.jsx`). Zero type errors in `app/routes/health.ts`,
  `app/routes/ready.ts`, `app/services/health/*` or `tests/unit/health/*`.
- Production build (`npm run build`): **exit code 0 — success**. Prisma client
  generation succeeded; React Router SSR production build produced
  `build/server/index.js` (49 modules transformed; built in 1.05s).
- ESLint on all health/readiness implementation and test files: **exit code 0**.

### Deviations

None to the accepted health/readiness architecture. The implementation matches
the architecture-level operational contract and the accepted runtime design
(bounded Redis PING; purpose-built `pg.Client` probe; `end()` in `finally`;
real-driver connection-bound integration test).

### Assumptions

- `REDIS_URL` and `DATABASE_URL` are the environment-specific dependency
  configurations; the route contract is identical in test and production.
- Pre-existing typecheck errors in unrelated `.jsx`/`.js` files are outside
  this task's scope and are recorded for accuracy rather than fixed here.

### Unresolved Issues

- Typecheck currently fails on pre-existing errors in unrelated files listed
  under Validation Results. No health/readiness-related type issue remains.

### Architectural Concerns

None. The runtime design is unchanged from the accepted architecture.

## Architect Review

### Review Status

Accepted

### Review Notes

`ARCH-002-SHOPIFY-001` is accepted Complete.

The returned implementation was reviewed from the actual source, tests,
documentation and durable task state rather than from the Completion Report
alone.

Accepted implementation:

- `GET /health` is deterministic process liveness and performs no Redis,
  PostgreSQL, Shopify or provider calls;
- `GET /ready` returns 200 only when required Redis and PostgreSQL dependencies
  are ready and returns 503 otherwise;
- readiness responses expose bounded operational booleans only and do not
  expose connection strings, credentials or raw dependency errors;
- Redis readiness uses a short-lived ioredis client with bounded connection
  behaviour and disconnects it in `finally`;
- PostgreSQL readiness uses a purpose-built short-lived `pg.Client`;
- PostgreSQL connection acquisition is bounded with
  `connectionTimeoutMillis`;
- PostgreSQL query execution is bounded with `query_timeout` and
  `statement_timeout`;
- `checkPostgresReadiness()` invokes the probe `end()` contract in `finally`
  after success or failure;
- the implementation no longer relies on an outer `Promise.race` to claim
  PostgreSQL operation cancellation;
- deterministic unit tests validate the PostgreSQL probe lifecycle contract;
- the real-driver black-hole integration test validates driver-level connection
  timeout without relying on timing-sensitive remote socket-close semantics;
- route tests validate health/readiness status, body, no-store behaviour and
  sensitive-response restrictions;
- repository operational documentation now defines `/health`, `/ready`, and
  `/ready` as the intended Render deployment health path;
- test and production use the same route contract with environment-specific
  dependency configuration only.

### Validation Reviewed

The implementing agent recorded the following final validation in its actual
execution environment (Node v24.19.0, npm 11.17.0):

```text
Focused health/readiness tests:
4 files passed
28 tests passed

Full test suite:
9 files passed
59 tests passed

Production build:
passed

Health/readiness ESLint:
passed
```

Repository-wide `npm run typecheck` still exits non-zero because of 48 errors
recorded in pre-existing files outside this task's implementation scope.

The Completion Report identifies the affected unrelated files and reports zero
type errors in the new health/readiness implementation and tests.

This existing repository typecheck debt is therefore recorded but is not
attributed to `ARCH-002-SHOPIFY-001` and does not block acceptance of this
bounded task.

Architect-side source review additionally confirmed:

- the Round 2 Architect Review was preserved unchanged by `moda_app`;
- the final task handoff is `Ready for Review` / `status: review`;
- the required README operational documentation is present;
- the PostgreSQL teardown comments were corrected to match the actual
  implementation guarantee;
- no accidental `Users/`, `home/`, `mnt/` or `tmp/` host-path directories are
  present at the workspace root in the returned archive.

### Architecture Conformance

Accepted.

The implementation conforms to the ARCH-002 Shopify service health/readiness
contract and is suitable for consumption by the later Render topology and
system-validation work.

### Dependency Evaluation

`ARCH-002-SHOPIFY-001` is now Complete.

This satisfies the SHOPIFY-001 prerequisite of `ARCH-002-GATEWAY-003`, but does
not by itself make GATEWAY-003 Ready because that task has additional
prerequisites which must also become Complete.

No downstream task is unblocked solely by this acceptance.

### Acceptance

```text
ARCH-002-SHOPIFY-001
Architect Review: Accepted
Task status: complete
Accepted: 2026-08-30
```
