---
id: ARCH-002-SHARED-007
architecture_id: ARCH-002
title: Add reusable Node observability runtime
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 15
executor: codex
claimed_at: 2026-08-31T12:17:32Z
attempt: 1
depends_on:
  - ARCH-002-SHARED-005
enables:
  - ARCH-002-SHARED-008
  - ARCH-002-SHARED-009
created: 2026-08-31
updated: 2026-08-31
---

# Add reusable Node observability runtime

## Objective

Implement the reusable **base Node OpenTelemetry runtime** and early process
bootstrap in `@modainteract/moda-interact-shared` so service repositories
configure a profile rather than rebuild tracer/meter/exporter plumbing.

## Architectural Boundary

This task owns the base runtime only.

It MUST NOT implement:

```text
Prisma instrumentation
BullMQ telemetry
GenAI/agent/tool helpers
```

Those capabilities belong to SHARED-008 and SHARED-009.

SHARED-008 may extend the Node profile after this task is architect-accepted.

## Scope

- add browser-safe `./observability` and Node-only `./observability/node` exports;
- initialize Node tracing/metrics before framework/application imports;
- canonical resource identity;
- HTTP/HTTPS server and client instrumentation;
- Undici/fetch instrumentation;
- configurable OpenTelemetry sampler selection;
- bounded OTLP trace and metric exporters;
- explicit trace processor and metric-reader lifecycle handles;
- reuse the accepted shared OTel Logs and direct Loki bootstrap;
- runtime-wide safe forceFlush/shutdown;
- configuration validation that cannot crash business startup;
- create instruments/providers once per process.

## Requirements

The implementation must use this ordering:

```text
process preload -> initNodeObservability() -> framework/worker -> app
```

Do not require Vite or application modules to import Node SDK packages.

SHARED-007 must not import `@prisma/instrumentation` or `bullmq-otel`.

Metric export timeout must never exceed export interval after normalization.
`enabled=true` must not be reported until initialization succeeds.

No endpoint/configuration must remain a safe no-op for traces/metrics while
stdout logging remains available.

### Sampling

Do not read `OTEL_TRACES_SAMPLER_ARG` while ignoring `OTEL_TRACES_SAMPLER`.

Support at least these architecture-approved standard values:

```text
always_on
always_off
traceidratio
parentbased_always_on
parentbased_always_off
parentbased_traceidratio
```

For `traceidratio` and `parentbased_traceidratio`, interpret
`OTEL_TRACES_SAMPLER_ARG` as the ratio. Invalid/unsupported configuration must
not crash application startup; use the documented Moda fallback and emit only a
bounded configuration warning.

### Runtime-wide forceFlush

`forceFlush()` must flush every initialized pipeline:

```text
trace BatchSpanProcessor
metric reader/provider
OpenTelemetry Logs
Loki
```

Do not expose a method named runtime `forceFlush()` that flushes logging only.

## Reference Implementation

Use the supplied code under:

`docs/decisions/shared/ARCH-002/reference-observability/moda-interact-shared/`

as the implementation starting point. The reference has been corrected so the
base `node.ts` contains no Prisma implementation and retains explicit trace and
metric flush handles.

Do not redesign the bootstrap unless the reference is incompatible with the
repository/toolchain and the incompatibility is documented with evidence.

## Acceptance Criteria

- [x] true Node preload initializes before HTTP/framework modules;
- [x] SHARED-007 contains no Prisma or BullMQ implementation;
- [x] inbound HTTP and outbound fetch spans are created in a production-start smoke test;
- [x] trace/log correlation works when a span is active;
- [x] `OTEL_TRACES_SAMPLER` selects the sampler and ratio ARG is only used where valid;
- [x] runtime `forceFlush()` flushes trace, metric, OTel Log and Loki pipelines when initialized;
- [x] metric exporter configuration cannot abort trace initialization;
- [x] invalid/unavailable exporter degrades telemetry only;
- [x] no service credentials/payloads are added to telemetry;
- [x] package build/typecheck/tests pass;
- [x] browser-safe entry does not pull Node SDK dependencies.

## Validation

- [x] unit tests;
- [x] sampler matrix tests;
- [x] typecheck/build;
- [x] package/exports smoke test;
- [x] spawned process preload test with local OTLP receiver;
- [x] trace + metric + logs/Loki forceFlush test;
- [x] exporter failure-isolation test;
- [x] sensitive/cardinality review.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- `moda-interact-shared/tsup.config.ts`
- `moda-interact-shared/README.md`
- `moda-interact-shared/src/observability/index.ts`
- `moda-interact-shared/src/observability/node.ts`
- `moda-interact-shared/src/observability/node.test.ts`
- `moda-interact-shared/src/observability/preload.test.ts`
- `moda-interact-shared/src/observability/test-fixtures/preload.ts`
- `moda-interact-shared/src/observability/test-fixtures/app.ts`
- `moda-interact-shared/src/observability/test-fixtures/failure-app.ts`
- `docs/decisions/shared/ARCH-002/SHARED-007-add-node-observability-runtime.md`

### Work Completed

- Corrected `moda-interact-shared/README.md` after architect review so the
  shared package explicitly owns generic Node OpenTelemetry runtime mechanics,
  while services own domain semantics, business attributes, application
  metrics, and deployment/backend wiring.
- Added browser-safe `./observability` helpers and the Node-only
  `./observability/node` package export.
- Added canonical tracing/metrics resources, bounded OTLP exporters, sampler
  selection, HTTP/HTTPS and Undici instrumentation, and process-wide lifecycle.
- Reused the accepted OTel Logs and Loki runtimes; runtime `forceFlush()` covers
  traces, metrics, OTel Logs, and Loki with idempotent best-effort shutdown.
- Isolated trace and metric exporter construction so one invalid signal cannot
  disable the other, and kept runtime activation false until SDK startup passes.
- Removed URL query strings/fragments from automatic HTTP and Undici span
  attributes so credentials and request parameters are not exported.
- Added sampler, configuration, production preload, correlation, all-signal
  flush, metric-isolation, and unavailable-exporter tests.

### Validation Results

- Correction-only validation: contradictory README ownership phrases are
  absent and the required shared/runtime and service/semantic ownership
  language is present.
- Correction-only `npm pack --dry-run` — pass, 29-file package artifact with
  `./observability` and `./observability/node` entries retained.
- `npm test` — pass, 57/57 tests.
- `npm run typecheck` — pass.
- `npm run build` — pass; both observability JS and declaration entries emitted.
- `npm pack --dry-run` — pass, 29-file package artifact.
- Clean temporary tarball install and imports of `./observability` and
  `./observability/node` — pass.
- Spawned production preload with local OTLP/Loki receiver — pass; inbound HTTP,
  native outbound HTTP, outbound fetch, metric, trace-correlated log, and all
  four force-flush paths observed.
- Invalid metric endpoint with valid trace receiver — pass; trace remained active.
- Unavailable trace/metric receivers — pass; flush and shutdown did not escape.
- Browser bundle scan — pass; no Node SDK, exporter, instrumentation, Winston,
  Loki, or `node:` imports in `dist/observability/index.js`.
- Deferred-scope and safety scan — pass; no Prisma/BullMQ/GenAI implementation,
  and secret URL/log values were absent from captured telemetry.
- `scripts/workspace-doctor.sh --quick` — 6 checks pass; existing warning for
  `moda-interact/.npmrc` `shamefully-hoist` configuration.
- npm reported one low-severity advisory and install-script approval notices;
  neither affected validation and no unrelated dependency remediation was made.

### Deviations

None. The reference implementation was retained with requirement-driven failure
isolation, canonical resource precedence, and URL-data safety hardening.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested

### Review Notes

The runtime implementation is architecturally conformant and does not require
redesign. The following documentation correction is required before acceptance:

1. In `moda-interact-shared/README.md`, the `What this package does not own`
   section currently states both:

   ```text
   OpenTelemetry spans or application-specific metrics
   OpenTelemetry tracing/metrics SDK bootstraps
   ```

   These statements now conflict with SHARED-007. The shared package owns the
   generic/base Node tracing and metrics SDK bootstrap and exposes generic span
   helpers. Service repositories own the semantic meaning of their telemetry.

2. Replace the conflicting ownership wording with language equivalent to:

   ```text
   service/domain-specific span names, business attributes and application metrics
   deployment OTLP endpoint/credential wiring and observability backends
   ```

   Keep the README explicit that `@modainteract/moda-interact-shared` owns the
   reusable base Node OpenTelemetry runtime.

3. Re-run the documentation/package smoke validation needed to confirm the README
   and exported package boundary remain coherent. No runtime code change is
   requested unless that validation reveals a regression.

### Re-review Gate

Return this same task to `status: review` after the README ownership language has
been corrected. SHARED-008 and SHARED-009 remain blocked until architect
acceptance of SHARED-007.

### Correction Response

Status: **Ready for Re-review**.

The README ownership contradiction has been corrected. No runtime source,
dependency, exporter, sampler, instrumentation, logging, or preload behavior was
changed during this correction-only pass.

## Architect Re-review — Accepted (2026-08-31)

Review status: **Accepted / Complete**.

The correction-only return is accepted. Compared with the previously reviewed
SHARED-007 submission, the correction changed only:

```text
moda-interact-shared/README.md
docs/decisions/shared/ARCH-002/SHARED-007-add-node-observability-runtime.md
docs/decisions/shared/ARCH-002/_index.md
```

No SHARED-007 runtime source, tests, package metadata, exporter, sampler,
instrumentation, logging, or preload implementation changed during the
correction pass.

The README now consistently states the approved ownership boundary:

```text
moda-interact-shared
    owns generic Node OpenTelemetry runtime mechanics

service repositories
    own service/domain span semantics, business attributes,
    application-specific metrics, and deployment/backend wiring
```

The contradictory statements that generic OpenTelemetry spans and tracing/metric
SDK bootstrap are outside shared ownership have been removed. The consumer
repository guidance now consistently directs services to use the shared runtime
while retaining ownership of their semantic telemetry.

Architecture conformance: **Accepted**.

Dependency decision:

```text
ARCH-002-SHARED-007 -> Complete
ARCH-002-SHARED-008 -> Ready
ARCH-002-SHARED-009 -> Ready
ARCH-002-SHARED-010 -> Pending
```

SHARED-008 and SHARED-009 may proceed independently. SHARED-010 remains blocked
until both are architect-accepted Complete.

