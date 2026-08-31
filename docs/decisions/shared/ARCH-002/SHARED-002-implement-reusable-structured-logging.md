---
id: ARCH-002-SHARED-002
architecture_id: ARCH-002
title: Implement reusable structured logging library
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 25
executor: codex
claimed_at: 2026-08-30T16:34:13Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-001
enables:
  - ARCH-002-SHARED-003
created: 2026-08-30
updated: 2026-08-30
---

# Implement Reusable Structured Logging Library

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Architecture amendment:

`docs/architecture/ARCH-002-shared-logging-amendment.md`

Coordinator:

`moda_architect`

## Objective

Implement the canonical reusable structured application logger in:

```text
moda-interact-shared
```

and expose it as:

```text
@modainteract/moda-interact-shared/logging
```

The logger is intended for application/runtime services that need structured
operational logging without independently inventing service-local generic
logging implementations.

The first blocked consumer is:

```text
ARCH-002-SHOPIFY-003
```

Future consumers may include:

```text
moda-interact-background
moda-interact-messaging
moda-interact-admin
other Moda Interact runtime services
```

## Why This Belongs in Shared

The concern is generic and cross-service:

- canonical JSON log envelope;
- log levels;
- service/environment identity;
- safe field sanitisation/redaction;
- safe `Error` serialisation;
- bounded log values;
- child/base context;
- best-effort logging semantics;
- stdout/stderr transport boundary.

It is not Shopify-specific business logic.

Provider/domain-specific semantic fields and OpenTelemetry metrics/traces remain
owned by the corresponding application repository.

## Public API

Consumers must import:

```ts
import {
  createLogger,
  type StructuredLogger,
  type LogFields,
} from "@modainteract/moda-interact-shared/logging";
```

Required public API:

```ts
createLogger(options)

logger.debug(event, fields?)
logger.info(event, fields?)
logger.warn(event, fields?)
logger.error(event, fields?)
logger.child(fields)
```

The logger must emit the canonical envelope:

```json
{
  "timestamp": "2026-08-30T12:00:00.000Z",
  "level": "info",
  "event": "shopify.webhook.outcome",
  "service.namespace": "moda-interact",
  "service.name": "moda-interact",
  "deployment.environment.name": "test",
  "data": {
    "topic": "checkouts/create",
    "outcome": "ENQUEUED",
    "ackMs": 12
  }
}
```

## Required Implementation

The architect has supplied the complete reference implementation under:

```text
docs/decisions/shared/ARCH-002/SHARED-002-reference/src/logging/
```

Files:

```text
types.ts
redaction.ts
logger.ts
index.ts
logger.test.ts
```

Implement those files in:

```text
moda-interact-shared/src/logging/
```

The supplied code is the architecture-approved starting implementation.

Do not redesign the API merely because another logging style is preferred.

A minimal technical adaptation is permitted only when required by the current
shared package compiler/module conventions. Any semantic deviation from the
reference implementation must be recorded in the Completion Report.

## Exact Reference Source

The full implementation is supplied as durable files rather than abbreviated
snippets in this task:

```text
SHARED-002-reference/src/logging/types.ts
SHARED-002-reference/src/logging/redaction.ts
SHARED-002-reference/src/logging/logger.ts
SHARED-002-reference/src/logging/index.ts
SHARED-002-reference/src/logging/logger.test.ts
```

Copy/adapt these into `moda-interact-shared/src/logging/`.

## Package Export

Add a package subpath export equivalent to:

```json
"./logging": {
  "types": "./dist/logging/index.d.ts",
  "import": "./dist/logging/index.js"
}
```

Do not remove or alter the existing root/Shopify exports.

The existing package name remains:

```text
@modainteract/moda-interact-shared
```

## Build Entry

Update the current `tsup` configuration so:

```text
src/logging/index.ts
```

is a build entry alongside the existing entrypoints.

The build must produce:

```text
dist/logging/index.js
dist/logging/index.d.ts
```

and any normal source-map/chunk artifacts produced by the existing build.

Do not create a second build system.

## Runtime Dependencies

Do not add a logging framework or backend dependency.

The shared logger must remain:

```text
vendor-neutral
backend-neutral
OpenTelemetry-independent
framework-independent
```

The default transport boundary is one JSON record per console line.

Centralised collection/storage remains an infrastructure/gateway concern.

## Security and Data Safety

The supplied sanitiser is mandatory baseline behaviour.

It must:

- recursively redact known sensitive field names;
- redact keys ending in `token`;
- redact keys containing `secret`;
- redact authorization/cookie/password/API-key/private-key fields;
- redact common email/phone/address fields;
- scrub Bearer credentials embedded in strings;
- scrub common token/secret query parameters embedded in strings;
- serialise `Error` as bounded `name` + `message`, without stack by default;
- handle circular values;
- bound string length;
- bound array size;
- bound object-key count;
- bound recursive depth.

This is defense in depth.

Consumers remain responsible for not intentionally passing full webhook/request
payloads, credentials, customer records, or other prohibited data into logs.

## Correctness Isolation

Logging must never become a correctness dependency.

After a logger has been created:

```text
logger.debug(...)
logger.info(...)
logger.warn(...)
logger.error(...)
```

must not throw because:

- sanitisation encounters an unusual value;
- timestamp generation fails;
- the configured sink throws;
- console output fails.

Invalid logger construction configuration such as an empty service name may
fail at `createLogger(...)` because that is configuration/programming error,
not request-path logging failure.

## Logging vs OpenTelemetry

Do NOT add OpenTelemetry packages to the shared logger.

The logger does not automatically:

- create spans;
- increment counters;
- record histograms;
- export OTLP;
- discover the active OTel resource;
- turn arbitrary log fields into metric attributes.

Domain/service instrumentation remains separately owned.

For example:

```text
moda-interact
    shared logger -> structured diagnostic log
    app OTel code -> Shopify span/metrics

moda-interact-background
    shared logger -> worker diagnostic log
    background OTel code -> BullMQ spans/metrics
```

This separation prevents high-cardinality log identifiers from accidentally
becoming metric labels.

## Documentation

Update:

```text
moda-interact-shared/README.md
```

with a concise "Structured logging" section that:

- documents the `./logging` import;
- links/conforms to
  `docs/observability/shared-logging.md`;
- shows creation + `info` + `error` + `child` examples;
- explains required `serviceName` and `environment`;
- states that full provider payloads/secrets/customer PII are prohibited;
- states that service-specific OTel remains separate.

The architecture-owned durable consumer guide already exists at:

```text
docs/observability/shared-logging.md
```

Do not duplicate a different logging contract in the repository README.

## Work Items

- [x] copy/adapt all five supplied reference implementation files into
      `moda-interact-shared/src/logging/`;
- [x] add the `./logging` package export;
- [x] add `src/logging/index.ts` to the existing tsup entrypoints;
- [x] preserve all existing shared package exports;
- [x] add/update the shared README logging section;
- [x] run logger tests;
- [x] run the full shared package test suite;
- [x] run shared typecheck;
- [x] run shared build;
- [x] verify `dist/logging/index.js` exists;
- [x] verify `dist/logging/index.d.ts` exists;
- [x] run `npm pack --dry-run`;
- [x] verify the dry-run package contains the `dist/logging` public artifacts;
- [x] verify no new runtime dependency was added;
- [x] verify logging failures cannot escape;
- [x] verify sensitive values are redacted;
- [x] return the task with `status: review`.

## Package Release Boundary

This task implements and validates the additive public API.

Do **not** run `npm publish` merely because the implementation is ready.

If an architecture-approved shared-package release task/process requires a
version bump/publication, report the required release state in the Completion
Report so `moda_architect` can sequence it.

Local workspace consumers may use the current shared workspace dependency while
the separate production-package task resolves the exact published artifact.

## Interfaces / Contracts

Owner:

```text
ARCH-002-SHARED-002
```

Package:

```text
@modainteract/moda-interact-shared
```

Subpath:

```text
@modainteract/moda-interact-shared/logging
```

Public functions/types:

```text
createLogger
LOG_LEVELS
StructuredLogger
LoggerOptions
LogRecord
LogFields
LogLevel
LogSink
sanitizeLogFields
isSensitiveLogKey
LOG_VALUE_LIMITS
REDACTED
CIRCULAR
MAX_DEPTH_REACHED
TRUNCATED
```

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-SHOPIFY-003`

## Acceptance Criteria

- [x] `@modainteract/moda-interact-shared/logging` is a valid built package
      subpath;
- [x] `createLogger` exposes debug/info/warn/error/child;
- [x] one structured JSON record is emitted per default-sink call;
- [x] canonical service namespace/name/environment fields are present;
- [x] arbitrary consumer data cannot overwrite canonical envelope fields;
- [x] nested known-sensitive values are redacted;
- [x] Bearer/query-token strings are scrubbed;
- [x] Error values are safely serialised without stack by default;
- [x] circular/unusually large values are bounded safely;
- [x] sink failure cannot escape into business code;
- [x] the logger has no OpenTelemetry/backend/runtime-framework dependency;
- [x] existing shared Shopify exports remain intact;
- [x] `npm test` passes;
- [x] `npm run typecheck` passes;
- [x] `npm run build` passes;
- [x] `npm pack --dry-run` includes the logging JS and type declarations;
- [x] shared README documents the API;
- [x] no package publication occurs unless separately authorised.

## Validation

Run the validation commands actually defined by `moda-interact-shared`.

Expected commands include:

```bash
npm test
npm run typecheck
npm run build
npm pack --dry-run
```

Also inspect:

```text
dist/logging/index.js
dist/logging/index.d.ts
package.json exports
tsup entrypoints
```

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/src/logging/types.ts` (new)
- `moda-interact-shared/src/logging/redaction.ts` (new)
- `moda-interact-shared/src/logging/logger.ts` (new)
- `moda-interact-shared/src/logging/index.ts` (new)
- `moda-interact-shared/src/logging/logger.test.ts` (new)
- `moda-interact-shared/package.json` (added `./logging` export)
- `moda-interact-shared/tsup.config.ts` (added `logging/index` build entry)
- `moda-interact-shared/README.md` (added "Structured logging" section)

### Work Completed

- Copied all five supplied reference files verbatim into
  `moda-interact-shared/src/logging/`.
- Added the `./logging` package subpath export to `package.json` without
  altering the existing root/Shopify exports.
- Added `src/logging/index.ts` to the existing tsup entrypoints (no second
  build system).
- Added the shared README "Structured logging" section conforming to
  `docs/observability/shared-logging.md`.

### Validation Results

- `npm test`: 13/13 pass (6 new logger tests + 7 existing Shopify tests).
- `npm run typecheck`: pass (exit 0).
- `npm run build`: success; produced `dist/logging/index.js`,
  `dist/logging/index.d.ts`, `dist/logging/index.js.map` alongside all
  existing artifacts.
- `npm pack --dry-run`: tarball includes `dist/logging/index.js` (5.9 kB),
  `dist/logging/index.d.ts` (1.7 kB), `dist/logging/index.js.map` (12.0 kB)
  plus all existing artifacts.
- Built-package subpath smoke test:
  `import("@modainteract/moda-interact-shared/logging")` resolves; canonical
  envelope fields, sensitive-key/query-token redaction, child context merge,
  and bounded `Error` serialisation verified against the built artifact.
- No new runtime dependency added (`dependencies` still only `zod`).

### Reference-Code Deviations

None. All five reference files were copied verbatim and are byte-identical to
`docs/decisions/shared/ARCH-002/SHARED-002-reference/src/logging/`.

### Package / Release State

Package version remains `0.1.0`. No publication performed (task boundary).
The `./logging` subpath is present in the package exports map and build output,
and `npm pack --dry-run` confirms the published tarball will contain the
logging public artifacts. A separate architecture-approved shared-package
release task may version-bump/publish a release containing `./logging`.

### Deviations

None.

### Assumptions

- The authoritative applied task file is
  `docs/decisions/shared/ARCH-002/SHARED-002-implement-reusable-structured-logging.md`
  (identical to the coordination overlay copy).
- The README cites the workspace-relative
  `docs/observability/shared-logging.md` as the architecture-owned consumer
  guide without duplicating its contract.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

The implementation is accepted.

Actual returned source/configuration was inspected. The five files under
`moda-interact-shared/src/logging/` are byte-identical to the
architect-supplied SHARED-002 reference implementation.

The package exposes:

```text
@modainteract/moda-interact-shared/logging
```

and preserves the existing root/Shopify exports.

`tsup` includes `src/logging/index.ts` as a build entry.

No logging framework, OpenTelemetry package or other new runtime dependency was
introduced.

The Completion Report records 13/13 tests passing, clean typecheck/build,
successful `npm pack --dry-run`, and built-package import smoke testing.

### Reviewed Files

- `moda-interact-shared/src/logging/types.ts`
- `moda-interact-shared/src/logging/redaction.ts`
- `moda-interact-shared/src/logging/logger.ts`
- `moda-interact-shared/src/logging/index.ts`
- `moda-interact-shared/src/logging/logger.test.ts`
- `moda-interact-shared/package.json`
- `moda-interact-shared/tsup.config.ts`
- `moda-interact-shared/README.md`

### Validation Reviewed

Agent-reported validation:

```text
npm test: 13/13 pass
npm run typecheck: pass
npm run build: pass
npm pack --dry-run: logging runtime/types included
built-package ./logging smoke test: pass
```

The compressed review archive does not include the installed dependency tree or
generated `dist` output, so those commands were not independently rerun from
the submitted archive.

### Architecture Conformance

Accepted.

The logger is generic/shared, backend-neutral and OpenTelemetry-independent.
Service-specific semantic logging and OTel remain owned by each runtime
repository.

The dependency chain has been corrected to:

```text
SHARED-002 -> SHARED-003 -> SHOPIFY-003
```

### Follow-up

`ARCH-002-SHARED-003` is now Ready.

Do not resume SHOPIFY-003 until SHARED-003 is architect-accepted Complete.

