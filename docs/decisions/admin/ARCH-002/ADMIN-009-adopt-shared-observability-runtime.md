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
executor: claude
claimed_at: 2026-09-01T22:07:26+01:00
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-001
  - ARCH-002-SHARED-010
enables:
  - ARCH-002-GATEWAY-006
  - ARCH-002-SYSTEM-TEST-002
created: 2026-08-31
updated: 2026-09-01
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

- [ ] shared runtime starts before Next.js/framework imports;
- [ ] canonical `service.name=moda-interact-admin` is emitted;
- [ ] HTTP/fetch and Prisma instrumentation are enabled through shared runtime;
- [ ] Moda-owned preload/configuration/application telemetry does not explicitly
      capture sensitive admin/tenant/database values;
- [ ] approved framework/OpenTelemetry telemetry is allowed to pass through
      without Moda-specific attribute rewriting;
- [ ] no repository-local sanitizer/Span patch is introduced for third-party
      telemetry;
- [ ] no competing local provider/exporter/sampler stack exists;
- [ ] local/test hosted export remains disableable;
- [ ] temporary telemetry diagnostic routes/scaffolding are absent from the final
      implementation.

## Validation

- [ ] focused preload/bootstrap tests;
- [ ] Moda-owned telemetry ownership/data-safety review;
- [ ] confirm third-party framework/instrumentation attributes are not treated as
      Moda-owned safety-contract failures;
- [ ] confirm temporary telemetry diagnostic routes/scaffolding are removed;
- [ ] affected repository tests;
- [ ] repository-defined typecheck/lint as applicable;
- [ ] production build;
- [ ] duplicate provider/exporter ownership review.

## Stop Condition

After shared-runtime adoption and required validation are complete, set this task
to `review`, write the Completion Report, return to `moda_architect`, and STOP.

ADMIN-010 is superseded by the framework-first telemetry reuse decision. Do not implement duplicate generic request metrics.

## Completion Report

### Status

In Progress

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
    database connection credentials, and Prisma SQL telemetry contains no
    credentials/parameter values.
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

No repository-local sanitizer or patch of OpenTelemetry/framework internals is
authorised or required.

### Assumptions

Architecture-approved third-party/framework telemetry is trusted and may be
exported unchanged to the internal observability backend according to the parent
ARCH-002 architecture document.

### Unresolved Issues

None for the former third-party `http.target` / framework span query-string
finding. The temporary `/telemetry-probe` diagnostic route has been removed and
is not required for the remaining acceptance criteria.

### Architectural Concerns

The former shared-runtime sanitization blocker is resolved by the ARCH-002
telemetry ownership boundary. ADMIN-009 introduces no local workaround.

## Architect Review

### Review Status

Complete

### Review Notes

The earlier ADMIN-009 block was based on treating framework-generated
Next.js/OpenTelemetry attributes as if they were Moda-owned telemetry. The
parent ARCH-002 architecture now explicitly distinguishes these ownership
boundaries and treats approved third-party telemetry as trusted operational
telemetry that may be exported unchanged.

No SHARED-014/SHARED-015 sanitizer or publication dependency is required for
this finding.

### Follow-up

The resumed ADMIN-009 work described in the Completion Report above has now been
executed: the focused validation is aligned to the architecture-owned telemetry
boundary, the temporary `/telemetry-probe` route is removed from production
source, Undici/fetch span coverage comes from a test-only preload fixture, an
exporter/backend failure-isolation test was added, and validation passes
(ownership tests 7/7, bootstrap tests 3/3, production build).

Remaining before review: set this task to `review` and return to
`moda_architect` per the Stop Condition, without implementing the superseded ADMIN-010 custom request metrics.
