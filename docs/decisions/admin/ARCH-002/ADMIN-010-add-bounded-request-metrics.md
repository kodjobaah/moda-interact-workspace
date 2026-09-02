---
id: ARCH-002-ADMIN-010
architecture_id: ARCH-002
title: Add bounded admin request operational metrics
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
task_kind: implementation
status: superseded
priority: 31
executor: github-copilot
claimed_at: 2026-09-02T00:00:00Z
attempt: 1
depends_on:
  - ARCH-002-ADMIN-009
enables: []
created: 2026-08-31
updated: 2026-09-02
---

# Add bounded admin request operational metrics

## Superseded — Framework-First Telemetry Reuse (2026-09-02)

This task must not be accepted or executed further.

Architect review determined that its generic admin HTTP request duration/count/
outcome telemetry duplicates the technical request telemetry already supplied by
the architecture-approved Next.js/OpenTelemetry HTTP instrumentation enabled by
`ARCH-002-ADMIN-009` through the shared observability runtime.

The architecture now requires framework-first telemetry reuse:

- standard/framework HTTP technical telemetry is exported and queried directly;
- Moda does not maintain a parallel route taxonomy merely to recreate request
  count/duration/status semantics;
- service-owned custom metrics are reserved for Moda-specific domain meaning or
  a documented operational property not supplied by standard instrumentation.

The implementation described in the historical Completion Report below was
never architect-accepted and is not part of the target architecture. If those
source changes are present in a working tree, revert the ADMIN-010-only changes
to the architect-accepted ADMIN-009 baseline before continuing dependent work.

`ARCH-002-ADMIN-009` is the final Admin telemetry-emitter prerequisite for
`ARCH-002-GATEWAY-006` and `ARCH-002-SYSTEM-TEST-002` unless a future architect
decision identifies a genuinely missing Moda-specific signal.

The remaining content is retained only as historical task evidence.

## Objective

Add admin-owned bounded request latency/outcome metrics using the global meter
provider installed by the shared runtime.

## Scope

- add request duration and request outcome instruments needed for internal
  operational visibility;
- create instruments once at module/process scope;
- use only low-cardinality route/method/outcome dimensions where safe;
- exclude admin IDs, tenant IDs, customer data, session/auth values and raw URLs
  containing arbitrary identifiers;
- isolate metric-recording failure from request correctness.

## Out of Scope

- generic Node/Prisma/HTTP instrumentation;
- custom database metrics;
- Grafana presentation;
- authentication/authorization;
- gateway/backend configuration.

## Acceptance Criteria

- [x] request latency/outcomes are available through bounded metrics;
- [x] dimensions are demonstrably low-cardinality;
- [x] sensitive/admin/tenant identifiers are absent;
- [x] metrics are created once rather than per request;
- [x] metric failure does not affect admin request correctness;
- [x] no second meter/provider runtime is installed.

## Validation

- [x] focused metric tests;
- [x] cardinality fuzz/review;
- [x] sensitive-data test/review;
- [x] failure-isolation test;
- [x] affected repository tests;
- [x] repository-defined typecheck/lint as applicable;
- [x] production build.

## Stop Condition

After bounded admin request metrics are complete and validated, set this task to
`review`, write the Completion Report, return to `moda_architect`, and STOP.

Do not begin gateway or Grafana work.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-admin/src/lib/observability/request-metrics.ts` — module-scoped
  request duration and outcome instruments with closed route/method/outcome
  dimensions and failure-isolated recording.
- `moda-interact-admin/src/app/api/health/database/route.ts` — records the real
  database health request duration and response outcome without changing its
  response behavior.
- `moda-interact-admin/tests/observability/admin-request-metrics.test.mjs` —
  bounded-cardinality, sensitive-data and metric-failure isolation tests.
- `moda-interact-admin/tests/observability/shared-runtime-ownership.test.mjs` —
  permits the explicitly approved service-owned metric module while preserving
  competing-runtime checks.
- `moda-interact-admin/package.json` and `moda-interact-admin/package-lock.json`
  — declare the OpenTelemetry API used with the shared global meter provider.
- `docs/decisions/admin/ARCH-002/ADMIN-010-add-bounded-request-metrics.md` —
  records the task claim, completed criteria, validation and review handoff.

### Work Completed

- Added `moda.admin.request.duration_ms` and
  `moda.admin.request.outcomes` using the global shared-runtime meter.
- Restricted route labels to `root`, `health_database`, `observability`, `login`,
  `auth` and `other`; methods to `GET`, `POST` and `other`; outcomes to success,
  client error and server error.
- Wrapped the database health handler so both successful and failed responses
  record actual status-derived outcomes, while thrown failures remain failures.
- Kept metric creation at module scope and isolated instrument creation and
  recording failures from request correctness.

### Validation Results

- Focused metrics tests: 3/3 pass.
- Full observability tests: 13/13 pass.
- `npm exec tsc -- --noEmit`: pass.
- `npm run lint`: pass.
- `npm run build`: pass, including Prisma generation and Next production build.
- Cardinality and sensitive-data review: closed vocabularies and no URL/query,
  tenant, admin or credential attributes recorded.
- The direct TypeScript test import emits Node's existing module-type warning;
  it does not affect test or build results.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending
