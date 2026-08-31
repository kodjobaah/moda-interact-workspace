---
id: ARCH-002-SHARED-004
architecture_id: ARCH-002
title: Add OpenTelemetry log emission to shared structured logger
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 27
executor: codex
claimed_at: 2026-08-30T22:16:13Z
attempt: 1
depends_on:
  - ARCH-002-SHARED-003
enables:
  - ARCH-002-SHARED-005
created: 2026-08-30
updated: 2026-08-30
---

# Add OpenTelemetry Log Emission to Shared Structured Logger

## Objective

Complete the intended Moda Interact logging architecture.

Every call to the public shared logger:

```ts
logger.debug(...)
logger.info(...)
logger.warn(...)
logger.error(...)
```

must continue to produce safe structured stdout JSON and must also emit the
same already-sanitized record through the OpenTelemetry Logs API.

The heavy Node SDK/exporter must remain isolated in:

```text
@modainteract/moda-interact-shared/logging/node
```

and must be initialized from the Node process bootstrap, never through
Vite/browser/application bundles.

## Target Architecture

```text
application module
    |
    v
@modainteract/moda-interact-shared/logging
    |
    +--> canonical JSON stdout
    |
    +--> @opentelemetry/api-logs
             |
             | global LoggerProvider
             v
process bootstrap only
@modainteract/moda-interact-shared/logging/node
    |
    +--> LoggerProvider
    +--> BatchLogRecordProcessor
    +--> OTLPLogExporter
             |
             v
          /v1/logs
```

If no LoggerProvider is installed, the OpenTelemetry API is a no-op and stdout
continues normally.

If an active trace/span context exists, the OpenTelemetry Logs SDK associates
the emitted log record with that active context. The shared logger must not
create or own service-specific traces.

## Critical Bundling Boundary

This task is specifically designed to avoid the runtime problem observed when
Node OpenTelemetry SDK packages were evaluated through the Shopify Vite SSR
module graph.

Application code may import:

```text
@modainteract/moda-interact-shared/logging
```

Process bootstrap code may import:

```text
@modainteract/moda-interact-shared/logging/node
```

Application/Vite/browser modules must **not** import `./logging/node`.

## Exact Implementation

The architect has supplied the complete implementation at:

```text
docs/decisions/shared/ARCH-002/SHARED-004-reference/
```

Copy/adapt these exact files:

```text
src/logging/types.ts
src/logging/redaction.ts
src/logging/otel.ts
src/logging/logger.ts
src/logging/index.ts
src/logging/node.ts
src/logging/logger.test.ts
src/logging/node.test.ts
package.json
tsup.config.ts
```

into `moda-interact-shared`.

The supplied source is the architecture-approved implementation.

Do not redesign the API.

Only minimal compiler/module adaptations are permitted if the accepted package
toolchain requires them. Record any deviation in the Completion Report.

## Public API

Existing:

```text
@modainteract/moda-interact-shared/logging
```

continues to expose:

```text
createLogger
StructuredLogger
LogFields
LogRecord
...
```

New Node-only export:

```text
@modainteract/moda-interact-shared/logging/node
```

exposes:

```text
initNodeOpenTelemetryLogging
getNodeOpenTelemetryLoggingRuntime
resolveLogsEndpoint
parseOtlpHeaders
NodeOpenTelemetryLoggingOptions
NodeOpenTelemetryLoggingRuntime
```

## OpenTelemetry Package Versions

For this implementation use the supplied `package.json` reference.

The architecture-approved log-signal dependencies are:

```text
@opentelemetry/api                    ^1.9.0
@opentelemetry/api-logs               0.221.0
@opentelemetry/exporter-logs-otlp-http 0.221.0
@opentelemetry/resources              ^2.10.0
@opentelemetry/sdk-logs               0.221.0
```

Do not add:

```text
sdk-trace-node
sdk-metrics
instrumentation-http
instrumentation-undici
context-async-hooks
```

to this shared task.

Those remain service-specific tracing/metrics concerns.

## Environment Contract

The Node logging bootstrap supports:

```text
OTEL_SDK_DISABLED

OTEL_LOGS_EXPORTER

OTEL_EXPORTER_OTLP_LOGS_ENDPOINT
OTEL_EXPORTER_OTLP_ENDPOINT

OTEL_EXPORTER_OTLP_LOGS_HEADERS
OTEL_EXPORTER_OTLP_HEADERS

OTEL_BLRP_MAX_QUEUE_SIZE
OTEL_BLRP_MAX_EXPORT_BATCH_SIZE
OTEL_BLRP_SCHEDULE_DELAY
OTEL_BLRP_EXPORT_TIMEOUT

OTEL_LOG_EXPORT_CONCURRENCY_LIMIT
```

Moda intentionally does **not** export to the OpenTelemetry default localhost
endpoint unless an endpoint is explicitly configured.

Therefore:

```text
no endpoint
    -> stdout JSON still works
    -> OTel log export disabled
```

## Endpoint Rules

```text
OTEL_EXPORTER_OTLP_LOGS_ENDPOINT
    exact signal endpoint; do not append /v1/logs

OTEL_EXPORTER_OTLP_ENDPOINT
    generic endpoint; append /v1/logs
```

## Data Safety

The OTel log is emitted **after** the same shared redaction/sanitization used
for stdout.

The OTel body is:

```text
JSON.stringify(canonical sanitized LogRecord)
```

and queryable attributes include only:

```text
event.name
log.level
service.namespace
service.name
deployment.environment.name
```

Do not independently add arbitrary user/customer/job values as OTel attributes
inside the generic logger.

This preserves the same privacy boundary for stdout and OTLP.

## Trace Correlation

Do not manually manufacture trace IDs in the shared logger.

The OpenTelemetry Logs SDK uses active context when emitting records.

Therefore:

```text
service-specific tracing bootstrap active
        |
        v
active span/context
        |
        v
shared logger call
        |
        v
OTel log associated with active context
```

If no active span exists, the log still exports without trace correlation.

## Failure Isolation

All paths remain best-effort.

Failure of:

```text
stdout sink
OpenTelemetry API
OTLP endpoint
batch export
forceFlush
shutdown
```

must not change application/business correctness.

## Tests

The supplied `node.test.ts` creates a bounded local HTTP OTLP test receiver and
proves:

```text
createLogger(...)
    ->
stdout record
    +
OTLP HTTP /v1/logs request
```

It also proves that a sensitive authorization value is redacted before the
OTLP request.

Preserve all existing logger tests.

## Work Items

- [x] copy/adapt the supplied reference source;
- [x] add `./logging/node` package export;
- [x] add `logging/node` tsup entry;
- [x] add exact OTel logs dependencies;
- [x] update package-lock without bumping package version;
- [x] keep package version at `0.2.0` during SHARED-004;
- [x] update shared README to explain stdout + OTel log fan-out;
- [x] run all tests;
- [x] run typecheck;
- [x] run build;
- [x] run `npm pack --dry-run`;
- [x] verify both logging subpaths are present;
- [x] verify Node-only SDK/exporter code is absent from the normal
      `./logging` entry's direct imports;
- [x] verify no trace/metric instrumentation packages were added;
- [x] return `status: review`.

## Acceptance Criteria

- [x] `createLogger` still emits canonical structured stdout;
- [x] the same sanitized record is emitted through OTel Logs API;
- [x] stdout failure does not suppress OTel emission;
- [x] OTel failure does not suppress stdout;
- [x] no provider/endpoint means safe stdout-only operation;
- [x] `./logging/node` configures LoggerProvider + batching + OTLP HTTP exporter;
- [x] Node SDK/exporter imports are isolated from normal `./logging`;
- [x] canonical service/environment Resource attributes are configured;
- [x] generic OTLP endpoint appends `/v1/logs`;
- [x] signal-specific endpoint remains exact;
- [x] secrets are redacted before OTLP emission;
- [x] no service-specific tracing/metrics packages are introduced;
- [x] tests/typecheck/build/pack pass;
- [x] package remains `0.2.0`;
- [x] task returns `status: review`.

## Completion Report

### Status

Ready for Review

### Files Changed

All files in `moda-interact-shared`:

- `src/logging/otel.ts` (new) — emits the sanitized canonical record through
  the OpenTelemetry Logs API via `@opentelemetry/api-logs`.
- `src/logging/node.ts` (new) — Node-only bootstrap: `LoggerProvider` +
  `BatchLogRecordProcessor` + `OTLPLogExporter`, env contract, endpoint
  resolution, header parsing, runtime accessors.
- `src/logging/node.test.ts` (new) — bounded local HTTP OTLP receiver test
  proving stdout + `/v1/logs` fan-out and redaction before OTLP; endpoint and
  header-parser unit tests.
- `src/logging/logger.ts` (modified) — every emitted record is fanned out to
  the configured sink and `emitOpenTelemetryLog`; sink and OTel paths are
  isolated/best-effort.
- `src/logging/types.ts`, `src/logging/redaction.ts`, `src/logging/index.ts`,
  `src/logging/logger.test.ts` — reference-identical (no-op re-copy; all
  existing logger tests preserved).
- `package.json` — added `./logging/node` export and the exact
  architecture-approved log-signal dependencies; version stays `0.2.0`.
- `tsup.config.ts` — added `logging/node` entry.
- `package-lock.json` — updated for the OTel dependencies; package version
  stays `0.2.0`.
- `README.md` — replaced the old “Logging and OpenTelemetry are separate”
  section with a full stdout + OTel Logs fan-out explanation, Node bootstrap
  usage, env contract, endpoint rules, data-safety/correlation notes, and the
  `./logging/node` package export in the exports list.

### Validation Results

All run from `moda-interact-shared` (Node sourced via
`scripts/bootstrap-node.sh`):

- `npm test` — 17/17 pass, 0 fail. Includes the 6 preserved logger tests, the
  new OTLP export test (stdout record + OTLP HTTP `/v1/logs` request + redacted
  authorization), endpoint/header tests, and the 7 existing Shopify tests.
- `npm run typecheck` — pass (`tsc --noEmit`).
- `npm run build` — pass; emits `dist/logging/index.js`, `dist/logging/node.js`
  and matching `.d.ts` files.
- `npm pack --dry-run` — 19 files, package 26.1 kB; both `dist/logging/index.*`
  and `dist/logging/node.*` present in the publish artifact.
- Bundling boundary — `dist/logging/index.js` imports only
  `@opentelemetry/api-logs` (lightweight no-op API facade); the Node
  `sdk-logs`, `exporter-logs-otlp-http` and `resources` imports exist only in
  `dist/logging/node.js`. Source `index.ts` does not reference `./node`.
- Package-scope audit — direct dependencies are exactly `@opentelemetry/api`
  `^1.9.0`, `@opentelemetry/api-logs` `0.221.0`, `@opentelemetry/exporter-logs-otlp-http`
  `0.221.0`, `@opentelemetry/resources` `^2.10.0`, `@opentelemetry/sdk-logs`
  `0.221.0`, `zod` `^4.0.0`. `sdk-trace-node`, `instrumentation-http`,
  `instrumentation-undici`, and `context-async-hooks` are entirely absent from
  the lockfile.
- Package version — `0.2.0`, unchanged.

### Reference-Code Deviations

None. The supplied reference source, `package.json` and `tsup.config.ts` were
copied byte-exact into `moda-interact-shared`. The README is package-local
documentation (not part of the reference) and was updated per the work item to
explain the stdout + OTel log fan-out.

### Architectural Concerns

- `@opentelemetry/sdk-metrics@2.10.0` and `@opentelemetry/sdk-trace@2.10.0`
  appear in `package-lock.json` only as transitive dependencies of
  `@opentelemetry/otlp-transformer@0.221.0`, which ships inside the
  architecture-approved `@opentelemetry/exporter-logs-otlp-http@0.221.0`. They
  are not direct dependencies and are not reachable from the emitted
  `./logging` module graph. `sdk-trace-node` (the service-specific Node trace
  SDK) was not introduced. Flagging for architect awareness; no action taken to
  avoid deviating from the supplied `package.json`.
- `./logging/node` is a module-level singleton (init once per process) and
  registers the global `LoggerProvider`. This matches the reference and is
  safe because `node.test.ts` runs in its own test-runner child process.

## Architect Review

### Review Status

Accepted

### Review Notes

The actual returned SHARED-004 implementation was inspected.

The implementation source, package.json and tsup.config.ts are byte-identical
to the architect-supplied SHARED-004 reference implementation.

The Completion Report records:

```text
npm test: 17/17 pass
npm run typecheck: pass
npm run build: pass
npm pack --dry-run: pass
```

The `./logging` bundle keeps the heavy Node OTel SDK/exporter out of its module
graph, while `./logging/node` owns LoggerProvider/exporter setup.

The task is accepted Complete.

### Follow-up

Do not publish yet.

`ARCH-002-SHARED-006` adds the newly agreed direct Loki transport before the
single SHARED-005 public release.

