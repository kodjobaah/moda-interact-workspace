---
id: ARCH-002-ADMIN-009
architecture_id: ARCH-002
title: Adopt shared observability runtime in admin process
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 30
executor: copilot
claimed_at: 2026-09-03T07:42:18Z
attempt: 2
depends_on:
  - ARCH-002-GATEWAY-001
  - ARCH-002-SHARED-010
enables:
  - ARCH-002-GATEWAY-006
  - ARCH-002-SYSTEM-TEST-002
created: 2026-08-31
updated: 2026-09-03
---

# Adopt shared observability runtime in admin process

## Objective

Install and preload the published shared Node observability runtime for the
internal Next.js admin service.

## Telemetry Ownership Boundary

The parent ARCH-002 architecture document defines the authoritative telemetry
ownership boundary.

- Telemetry explicitly created or enriched by Moda-owned application code is
  subject to Moda sensitive-data, cardinality and failure-isolation rules.
- Telemetry emitted by architecture-approved third-party frameworks and standard
  OpenTelemetry instrumentation is treated as trusted operational telemetry and
  may be exported unchanged to the internal observability backend/Grafana.
- ADMIN-009 must not rewrite, sanitize, monkey-patch or reject third-party
  telemetry merely because a framework-owned attribute contains a URL, query
  string or other framework-defined value.

This task validates the Admin-owned preload/configuration boundary rather than
asserting Moda ownership over arbitrary Next.js/OpenTelemetry-generated span
attributes.

## Scope

- use exact shared dependency `@modainteract/moda-interact-shared@0.4.0`;
- add a small repository-owned preload;
- initialize `.../observability/node` with:
  `serviceName=moda-interact-admin` and
  `instrument={http:true, fetch:true, prisma:true}`;
- preload before the real Next.js production CLI entrypoint;
- ensure canonical resource/environment identity;
- validate that Moda-owned preload/configuration or application telemetry does
  not explicitly add sensitive admin, tenant, credential or SQL parameter values;
- allow architecture-approved third-party/framework instrumentation telemetry to
  be exported as emitted, without repository-local rewriting;
- ensure no competing local generic provider/exporter/sampler runtime exists;
- remove temporary diagnostic application routes/scaffolding before review.

## Out of Scope

- custom admin request metrics;
- Grafana UI/embedding;
- platform-admin authentication/authorization;
- gateway/backend OTLP wiring;
- sanitizing, rewriting or patching Next.js/OpenTelemetry/other approved
  third-party telemetry attributes;
- unrelated admin refactoring.

## Acceptance Criteria

- [x] shared runtime starts before Next.js/framework imports;
- [x] canonical `service.name=moda-interact-admin` is emitted;
- [x] HTTP/fetch and Prisma instrumentation are enabled through shared runtime;
- [x] Moda-owned preload/configuration/application telemetry does not explicitly
      capture sensitive admin/tenant/database values;
- [x] approved framework/OpenTelemetry telemetry is allowed to pass through
      without Moda-specific attribute rewriting;
- [x] no repository-local sanitizer/Span patch is introduced for third-party
      telemetry;
- [x] no competing local provider/exporter/sampler stack exists;
- [x] local/test hosted export remains disableable;
- [x] temporary telemetry diagnostic routes/scaffolding are absent from the final
      implementation.

## Validation

- [x] focused preload/bootstrap tests;
- [x] Moda-owned telemetry ownership/data-safety review;
- [x] confirm third-party framework/instrumentation attributes are not treated as
      Moda-owned safety-contract failures;
- [x] confirm temporary telemetry diagnostic routes/scaffolding are removed;
- [x] affected repository tests;
- [x] repository-defined lint as applicable (no `typecheck` script is defined;
  the production build completed its TypeScript check);
- [x] production build;
- [x] duplicate provider/exporter ownership review.

## Stop Condition

After shared-runtime adoption and required validation are complete, set this task
to `review`, write the Completion Report, return to `moda_architect`, and STOP.

ADMIN-010 is superseded by the framework-first telemetry reuse decision. Do not implement duplicate generic request metrics.

## Architect Correction Request — 2026-09-03

`ARCH-002-SYSTEM-TEST-002` exposed a validation-contract defect in the accepted
ADMIN-009 focused bootstrap test. The current test requires a literal
`SELECT 1` value to appear in `db.statement` or `db.query.text`, but neither the
ARCH-002 parent architecture nor ADMIN-009/SHARED-008 requires Prisma
instrumentation to export SQL text. The accepted contract requires Prisma spans
to be emitted when instrumentation is enabled.

This is a correction within the original ADMIN-009 scope. Do not create a new
Admin task and do not redesign the runtime.

Required correction:

- keep the production preload and shared-runtime configuration unchanged unless
  investigation proves a genuine runtime instrumentation defect;
- make the focused bootstrap test prove Prisma instrumentation from exported
  Prisma spans rather than requiring the literal SQL text `SELECT 1`;
- if `db.statement` or `db.query.text` is present, continue validating that it
  contains no prohibited credential/parameter values;
- absence of SQL-text attributes must not fail the observability contract;
- keep exporter/backend failure isolation and canonical resource-identity
  coverage intact;
- prefer the canonical `/ready` operational boundary when practical, but do not
  broaden this correction into unrelated health-route refactoring;
- rerun the focused ADMIN-009 validation, repository tests, lint/typecheck as
  declared by the repository, and production build on the workspace Node
  runtime;
- reconcile the ADMIN-009 Acceptance Criteria, Validation checklist and
  Completion Report before returning the task to `review`.

Repository-local ADMIN-009 validation remains independent of the system-test
fixture. Do not make `moda-interact-admin` depend on
`moda-interact-system-test`. If a developer-local PostgreSQL instance is absent,
the focused owning-repository bootstrap test may still observe the bounded
unavailable readiness path, provided it validates the actual Prisma span
contract without demanding SQL-text attributes.

`ARCH-002-SYSTEM-TEST-002` will separately use the new
`ARCH-002-SYSTEM-TEST-005` ephemeral PostgreSQL fixture to prove the healthy
production-representative database path with a reachable `DATABASE_URL`.

The correction must not introduce custom SQL telemetry or a competing Prisma
instrumentation mechanism merely to make `SELECT 1` visible.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-admin/observability.mjs` — production preload adopting the
  shared Node observability runtime
  (`@modainteract/moda-interact-shared/observability/node` with
  `serviceName=moda-interact-admin` and
  `instrument={http:true, fetch:true, prisma:true}`), loaded before the Next.js
  production CLI entrypoint. It only calls `initNodeObservability`; no local
  sanitizer/span patch.
- `moda-interact-admin/src/app/telemetry-probe/route.ts` — REMOVED. The
  temporary diagnostic application route no longer exists in production source.
- `moda-interact-admin/tests/observability/fixtures/probe-preload.mjs` — NEW
  test-only preload fixture that imports the real production preload and fires a
  short, bounded burst of outbound fetches to the in-process receiver, so
  Undici/fetch client spans are validated end to end without shipping a
  production probe endpoint.
- `moda-interact-admin/tests/observability/otlp-receiver.mjs` — in-process
  OTLP/HTTP receiver used by the focused preload/bootstrap tests.
- `moda-interact-admin/tests/observability/admin-telemetry-bootstrap.test.mjs` —
  focused production-runtime tests aligned to the ARCH-002 telemetry ownership
  boundary (shared-runtime bootstrap, Moda-owned telemetry safety, third-party
  pass-through, exporter failure isolation).
- `moda-interact-admin/tests/observability/shared-runtime-ownership.test.mjs` —
  ownership, disable-ability and environment-identity tests.
- `docs/decisions/admin/ARCH-002/ADMIN-009-adopt-shared-observability-runtime.md` —
  this document (architect-reconciled Ready status).

### Work Completed

- Adopted the shared Node observability runtime through the repository-owned
  `moda-interact-admin/observability.mjs` preload, preloaded before the Next.js
  production CLI entrypoint.
- Removed the temporary `/telemetry-probe` application route. Production `npm
  start` now runs the exact repository command (`node --import
  ./observability.mjs ./node_modules/next/dist/bin/next start`) with no
  diagnostic scaffolding.
- Introduced the test-only preload fixture
  (`tests/observability/fixtures/probe-preload.mjs`) for Undici/fetch client-span
  coverage. The fixture imports the real production preload and fires a bounded
  burst of outbound fetches, so the runtime test still exercises the canonical
  production bootstrap while fetch spans remain observable.
- Realigned the focused validation to the architecture-owned telemetry boundary:
  - Moda-owned telemetry safety is asserted directly: canonical resource
    attributes carry no sensitive values, no exported span attribute contains
    database connection credentials, and any optional Prisma SQL attributes
    contain no credentials/parameter values.
  - Approved framework/OpenTelemetry telemetry (legacy `http.target` with the
    raw query string and related framework span metadata) is asserted to pass
    through unchanged — no repository-local sanitizer, rewrite, monkey-patch or
    rejection.
  - Structural ownership tests verify `src/` has no Moda-owned span/metric
    creation (no `@opentelemetry/api`, tracer/meter calls, span-attribute
    writes, sanitizers) and that the preload performs no local telemetry
    rewriting or span patching.
  - Environment identity from `DEPLOYMENT_ENVIRONMENT_NAME` is validated to
    distinguish `test` from `production`.
- Added an exporter/backend failure-isolation test: with the OTLP trace exporter
  pointed at a closed port, batch export failures must not crash the server or
  reject valid admin requests.
- Confirmed no competing local provider/exporter/sampler stack remains in
  application code and hosted export stays disableable.

### Validation Results

- `tests/observability/shared-runtime-ownership.test.mjs` — 7/7 pass: canonical
  preload identity; hosted export disableable without an endpoint and with
  `OTEL_SDK_DISABLED=true`; runtime enables with an OTLP endpoint; no competing
  generic provider/exporter/sampler stack in `src/`; no Moda-owned span/metric
  creation in application code; preload performs no local telemetry rewriting;
  environment identity distinguishes test and production.
- `tests/observability/admin-telemetry-bootstrap.test.mjs` — 3/3 pass against the
  real production Next server spawned with the shared preload: shared runtime
  starts before framework imports (HTTP and Undici/fetch client spans captured);
  canonical resource identity emitted; HTTP/Undici/Prisma instrumentation
  enabled; Moda-owned telemetry carries no sensitive values and no span attribute
  contains database connection credentials; approved framework/OpenTelemetry
  telemetry passes through unchanged; exporter/backend failure does not break
  valid admin requests; observability does not change application correctness.
- `npm test` — 28/28 pass.
- `npm run lint` — pass.
- `npm run build` — pass; the build completed its TypeScript check and the route
  listing contains no `/telemetry-probe` route.
- The health route returns 200 when the local database is reachable and 503
  otherwise; the tests accept either status while still validating span capture,
  ownership and failure isolation. Local Postgres via `DATABASE_URL` (or
  `ADMIN_TEST_DATABASE_URL`) is required for a full green 200-path run.
- Production build passes and the build route listing confirms no
  `/telemetry-probe` route remains.
- Note: this environment cannot discover test files by directory path (`node
  --test tests/observability/` fails with MODULE_NOT_FOUND — pre-existing,
  reproduced with a scratch directory), so the suite is run with explicit test
  files or a glob, e.g. `node --test tests/observability/*.test.mjs`.

### Deviations

The focused test no longer requires `db.statement` or `db.query.text` to contain
literal `SELECT 1`; those attributes are optional under the accepted Prisma span
contract. When present, they remain covered by the sensitive-value checks. No
repository-local sanitizer or patch of OpenTelemetry/framework internals was
introduced.

### Assumptions

Architecture-approved third-party/framework telemetry is trusted and may be
exported unchanged to the internal observability backend according to the parent
ARCH-002 architecture document.

### Unresolved Issues

None for the former third-party `http.target` / framework span query-string
finding. The temporary `/telemetry-probe` diagnostic route has been removed and
is not required for the remaining acceptance criteria.

### Architectural Concerns

None. The former shared-runtime sanitization blocker remains resolved by the
ARCH-002 telemetry ownership boundary, and ADMIN-009 introduces no local
workaround.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted on 2026-09-03 after attempt 2. The bounded correction is exactly within
the Architect Correction Request:

- the production `observability.mjs` preload/shared-runtime configuration is
  unchanged;
- the bootstrap test still requires exported `prisma:*` spans;
- `db.statement` / `db.query.text` are treated as optional third-party
  attributes rather than required Prisma contract fields;
- when SQL-text attributes are present, the existing sensitive-value checks
  remain in force;
- the literal `SELECT 1` assertion has been removed;
- no custom SQL telemetry, Prisma patch, sanitizer or competing instrumentation
  mechanism was introduced;
- canonical resource identity and exporter/backend failure-isolation coverage
  remain intact.

The agent records focused bootstrap 3/3, ownership 7/7, repository test 28/28,
lint pass and production build pass. The correction therefore closes the
ADMIN-009 validation-contract drift discovered by SYSTEM-TEST-002 attempt 1.

`ARCH-002-SYSTEM-TEST-002` is not yet promoted because its new direct
`ARCH-002-SYSTEM-TEST-005` ephemeral-PostgreSQL prerequisite remains Ready and
must be architect-accepted Complete first. `ARCH-002-GATEWAY-006` remains
Complete and unchanged.
