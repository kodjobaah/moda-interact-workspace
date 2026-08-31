---
id: ARCH-002-SHARED-006
architecture_id: ARCH-002
title: Add direct Grafana Loki transport to shared logger
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 27
executor: codex
claimed_at: 2026-08-30T23:15:47Z
attempt: 1
depends_on:
  - ARCH-002-SHARED-004
enables:
  - ARCH-002-SHARED-005
created: 2026-08-30
updated: 2026-08-31
---

# Add Direct Grafana Loki Transport to Shared Logger

## Objective

Add an optional direct Grafana Loki destination to the existing shared logging
library without changing the application-facing logging API.

The resulting fan-out is:

```text
createLogger(...)
    |
    +--> structured JSON stdout
    |
    +--> OpenTelemetry Logs API
    |
    +--> direct Loki transport
```

All three destinations consume the **same already-sanitized canonical
LogRecord** and are independently failure-isolated.

## Architectural Boundary

The public application API remains:

```text
@modainteract/moda-interact-shared/logging
```

Node transport/bootstrap configuration remains:

```text
@modainteract/moda-interact-shared/logging/node
```

Winston and `winston-loki` must exist **only** in the Node-only package graph.

The normal `./logging` bundle must not import:

```text
winston
winston-loki
Node networking modules
```

This preserves the Vite/browser-safe logging facade.

## Important Design Choice

Do **not** replace the accepted Moda logger API with Winston.

Winston is an internal Node transport implementation detail.

Also do **not** add a Winston Console transport.

The existing shared logger already owns canonical structured console output.
Adding another Console transport would duplicate every console log.

The desired architecture is:

```text
Moda createLogger
    |
    +--> existing console sink
    +--> existing OTel Logs API
    +--> lightweight Loki bridge
               |
               v
        ./logging/node
               |
               v
        Winston + winston-loki
               |
               v
           Grafana Loki
```

## Exact Implementation

The architect has supplied the implementation under:

```text
docs/decisions/shared/ARCH-002/SHARED-006-reference/
```

Use the exact supplied files:

```text
NEW
src/logging/loki.ts

REPLACE
src/logging/logger.ts

NEW
src/logging/node/loki.ts

REPLACE
src/logging/node.ts

NEW
src/logging/node/loki.test.ts

REPLACE
package.json

UNCHANGED/GUARD
tsup.config.ts
```

Do not redesign this solution.

Only minimal compiler/module compatibility changes are permitted if genuinely
required by the repository toolchain. Record every deviation.

## Why `globalThis` Is Used

`tsup` produces separate bundles for:

```text
./logging
./logging/node
```

Therefore a module-local:

```ts
let emitter
```

would be duplicated and would **not** connect the application logger bundle to
the Node bootstrap bundle.

The supplied `src/logging/loki.ts` intentionally stores the emitter on
`globalThis`.

Do not replace that with a module-local singleton.

## Dependencies

Add exactly:

```text
winston@3.19.0
winston-loki@6.1.7
```

Keep the existing OTel dependencies from SHARED-004.

The package version remains:

```text
0.2.0
```

during SHARED-006. Publishing remains owned by SHARED-005.

## Public Node API

`@modainteract/moda-interact-shared/logging/node` additionally exposes:

```text
initNodeLokiLogging
getNodeLokiLoggingRuntime
NodeLokiLoggingOptions
NodeLokiLoggingRuntime
```

Existing SHARED-004 exports remain unchanged.

## Loki Environment Contract

Supported deployment variables:

```text
LOKI_ENABLED

LOKI_URL

LOKI_USERNAME
LOKI_PASSWORD

LOKI_BATCHING
LOKI_BATCH_INTERVAL_SECONDS
LOKI_TIMEOUT_MS
LOKI_CLEAR_ON_ERROR
```

Rules:

```text
no LOKI_URL
    -> direct Loki disabled

LOKI_ENABLED=false
    -> direct Loki disabled

LOKI_URL present
    -> direct Loki enabled by default
```

Credentials are Node-bootstrap configuration only.

Never log:

```text
LOKI_URL credentials
LOKI_USERNAME
LOKI_PASSWORD
Basic Auth values
connection headers
```

## Labels / Cardinality

The only default Loki labels are:

```text
service_namespace
service_name
environment
```

Do not add dynamic identifiers to Loki labels.

In particular, do **not** label by:

```text
traceId
spanId
requestId
jobId
deliveryId
eventId
recoveryId
checkoutToken
cartToken
shop
shopDomain
customerId
phone
email
```

The implementation must explicitly retain:

```text
useWinstonMetaAsLabels: false
```

High-cardinality safe operational identifiers may remain in the sanitized JSON
log body where justified. They must not become indexed stream labels.

## Reliability / Failure Isolation

Direct Loki is observability only.

The supplied implementation uses:

```text
batching=true by default
bounded timeout
clearOnError=true by default
replaceTimestamp=true
gracefulShutdown=false
```

Moda owns explicit flush/shutdown from the process bootstrap.

If Loki is unavailable:

```text
logging may be dropped
application processing must continue
```

Do not retry indefinitely or create an unbounded in-memory correctness
dependency.

Do not recursively write Loki connection errors through the shared logger.

## OpenTelemetry Coexistence

Direct Loki and OpenTelemetry Logs remain independently configurable.

The shared logger may therefore support:

```text
console only

console + Loki

console + OTel Logs

console + Loki + OTel Logs
```

Deployment configuration must avoid routing the OTel Logs destination back into
the same Loki instance when direct Loki is also enabled, otherwise each log
would be stored twice.

The library itself does not guess the backend topology.

## Integration Test

The supplied Loki test starts a bounded local HTTP server and configures
`winston-loki` against it.

It must prove:

```text
logger.info(...)
    ->
POST /loki/api/v1/push
```

and assert:

```text
canonical service labels exist
event exists
safe structured data exists
secret value does not exist
[REDACTED] does exist
high-cardinality body data is not promoted to architecture labels
```

## Security Validation

`winston-loki` uses `protobufjs` in its dependency graph even when JSON
transport is selected.

After updating `package-lock.json`:

1. inspect the actually resolved `protobufjs` version;
2. require `>= 7.6.5` for the winston-loki dependency path;
3. run `npm audit`;
4. do not accept a newly introduced high/critical vulnerability;
5. report any audit finding rather than silently overriding dependencies.

## README

Update the public README to document:

```text
console
OpenTelemetry Logs
direct Loki
```

and show process-bootstrap configuration:

```ts
import {
  initNodeLokiLogging,
  initNodeOpenTelemetryLogging,
} from "@modainteract/moda-interact-shared/logging/node";

initNodeLokiLogging({
  serviceName: "moda-interact",
  environment: "production",
});

initNodeOpenTelemetryLogging({
  serviceName: "moda-interact",
  environment: "production",
});
```

Also document the duplicate-delivery warning:

```text
direct Loki ON
+
OTel Logs ultimately routed to same Loki
=
duplicate log storage
```

## Work Items

- [x] copy the exact reference implementation;
- [x] add `winston@3.19.0`;
- [x] add `winston-loki@6.1.7`;
- [x] update package-lock;
- [x] keep version at `0.2.0`;
- [x] add Loki public Node exports;
- [x] preserve existing OTel Node exports;
- [x] preserve existing application logging API;
- [x] preserve stdout behavior;
- [x] add direct Loki fan-out;
- [x] keep Winston/Loki out of normal `./logging` dependency graph;
- [x] add/update README;
- [x] run all tests;
- [x] run typecheck;
- [x] run build;
- [x] run `npm pack --dry-run`;
- [x] inspect built `dist/logging/index.js` imports;
- [x] inspect built `dist/logging/node.js` imports;
- [x] run `npm audit`;
- [x] verify resolved winston-loki protobufjs path;
- [x] return `status: review`.

## Acceptance Criteria

- [x] application-facing API remains unchanged;
- [x] stdout remains canonical;
- [x] OTel Logs fan-out remains intact;
- [x] direct Loki fan-out works;
- [x] Loki failure cannot affect business correctness;
- [x] only canonical low-cardinality Loki labels are configured;
- [x] `useWinstonMetaAsLabels=false`;
- [x] secrets are sanitized before Loki;
- [x] no Winston Console transport duplicates stdout;
- [x] Winston/Loki are isolated to `./logging/node`;
- [x] `./logging` has no Winston/Loki/Node network imports;
- [x] package remains `0.2.0`;
- [x] tests/typecheck/build/pack pass;
- [x] security validation is recorded;
- [x] task returns `status: review`.

## Completion Report

### Status

Complete

### Files Changed

All files in `moda-interact-shared`, using the supplied reference exactly:

- `src/logging/loki.ts` (NEW) — globalThis-based Loki emitter bridge
  (`setLokiLogEmitter` / `emitLokiLog`). Contains no Winston, winston-loki or
  Node networking imports, so it is safe inside the normal `./logging` entry.
- `src/logging/logger.ts` (REPLACE) — every canonical record is fanned out to
  the configured sink, `emitOpenTelemetryLog`, and `emitLokiLog`; each
  destination is independently failure-isolated.
- `src/logging/node/loki.ts` (NEW) — Node-only direct Loki bootstrap
  (`initNodeLokiLogging` / `getNodeLokiLoggingRuntime`,
  `NodeLokiLoggingOptions`, `NodeLokiLoggingRuntime`). Winston logger with the
  LokiTransport: json, batching, bounded timeout, clearOnError,
  replaceTimestamp, gracefulShutdown=false, static low-cardinality labels,
  `useWinstonMetaAsLabels: false`, connection errors swallowed.
- `src/logging/node.ts` (REPLACE) — added the Loki public exports and preserved
  all existing SHARED-004 OpenTelemetry exports unchanged.
- `src/logging/node/loki.test.ts` (NEW) — bounded local HTTP server integration
  test proving `logger.info(...)` -> `POST /loki/api/v1/push` with canonical
  service labels, event/data present, secret absent, `[REDACTED]` present, and
  high-cardinality body values not promoted to architecture labels.
- `package.json` (REPLACE per reference) — added `winston@3.19.0` and
  `winston-loki@6.1.7`; version remains `0.2.0`.
- `package-lock.json` — updated (44 packages added) without bumping version.
- `README.md` — documents console + OpenTelemetry Logs + direct Loki, the
  combined `initNodeLokiLogging`/`initNodeOpenTelemetryLogging` bootstrap, the
  Loki environment contract, label/cardinality rules, and the
  duplicate-delivery warning.
- `tsup.config.ts` — UNCHANGED/GUARDED (byte-identical to the reference and to
  the pre-existing SHARED-004 working-tree state).

### Validation Results

All run from `moda-interact-shared` (Node via `scripts/bootstrap-node.sh`):

- `npm test` — 49/49 pass, 0 fail, run through `/bin/sh` exactly as CI runs it.
  Includes the 6 preserved logger tests, 4 OTel node tests, 1 new direct-Loki
  integration test, the 7 `shopify/node` tests, and the 31 pre-existing nested
  `shopify/v1` + `shopify/v2` tests that the old test glob silently excluded.
- `npm run typecheck` — pass (`tsc --noEmit`).
- `npm run build` — pass; emits `dist/logging/index.js` (6.92 kB),
  `dist/logging/node.js` (9.94 kB) and the shared `dist/chunk-XU4XX7SD.js`
  (518 B, the `loki.ts` globalThis bridge), plus matching `.d.ts` files.
- `npm pack --dry-run` — 21 files, 32.1 kB; both `dist/logging/index.*` and
  `dist/logging/node.*` present in the publish artifact.
- Bundling boundary — `dist/logging/index.js` imports only
  `../chunk-XU4XX7SD.js` and `@opentelemetry/api-logs`; zero occurrences of
  `winston`, `loki`, or Node networking modules. `dist/logging/node.js` imports
  the OTel packages plus `winston` and `winston-loki`.
- Public API — `dist/logging/node.d.ts` exposes `initNodeLokiLogging`,
  `getNodeLokiLoggingRuntime`, `NodeLokiLoggingOptions`, `NodeLokiLoggingRuntime`
  alongside the preserved `initNodeOpenTelemetryLogging` and
  `getNodeOpenTelemetryLoggingRuntime`. `dist/logging/index.d.ts` has no
  Loki/Winston references.

### Security Validation

- Resolved `winston@3.19.0` and `winston-loki@6.1.7` (exact, per architecture).
- `protobufjs@7.6.6` resolved on the winston-loki dependency path
  (`protobufjs ^7.2.4`) — satisfies the required `>= 7.6.5`.
- `npm audit` — 1 low severity finding: `esbuild` 0.27.3–0.28.0
  (GHSA-g7r4-m6w7-qqqr, arbitrary file read when running the dev server on
  Windows). It is a `devDependency` (tsup's bundler), was present before
  SHARED-006, and was not introduced by the Loki additions. No high/critical
  findings. Reported rather than silently overridden; `npm audit fix` was not
  run to avoid deviating from the supplied dependency set.

### Reference-Code Deviations

- `package.json` `test` script changed from `tsx --test src/**/*.test.ts` to
  `tsx --test "src/**/*.test.ts"` (quoted glob). Required by the repository
  toolchain: npm runs scripts via `/bin/sh`, where `**` degrades to a
  single-level `*`, which silently excluded the architecture-approved nested
  integration test `src/logging/node/loki.test.ts` (and the pre-existing
  nested `shopify/v1`/`shopify/v2` tests) from `npm test`. Quoting passes the
  pattern literally to the Node test runner, whose glob expands `**`
  recursively, so all 49 tests now run. This is the only change beyond
  byte-exact reference copies.
- `tsup.config.ts` unchanged/guarded; byte-identical to reference.

### Architectural Concerns

- The globalThis bridge is intentional and required: tsup emits `./logging` and
  `./logging/node` as independent bundles, so a module-local variable would not
  connect them. `dist/chunk-XU4XX7SD.js` contains only the `loki.ts` bridge and
  leaks no Winston/Node networking into the normal entry.
- Winston's Console transport is not used; only the LokiTransport is configured,
  so canonical console output is not duplicated.
- Pre-existing latent issue surfaced by this task: the unquoted `**` test glob
  in the architect-supplied `package.json` silently excluded all nested test
  files under `/bin/sh`. Fixed minimally; recorded above.

## Architect Review

### Review Status

Accepted

### Review Notes

The direct Grafana Loki transport is accepted.

The actual implementation was inspected against the supplied reference.

All supplied source/configuration targets are byte-identical except for the
accepted npm test-script correction:

```json
"test": "tsx --test \"src/**/*.test.ts\""
```

The quoted glob ensures the Node test runner, rather than `/bin/sh`, performs
recursive test discovery. The returned validation therefore executes the full
49-test suite.

Accepted implementation properties:

```text
canonical stdout preserved
OpenTelemetry Logs fan-out preserved
direct Loki fan-out added
Winston/Loki isolated behind ./logging/node
no Winston Console duplication
globalThis bridge preserved
static low-cardinality labels only
useWinstonMetaAsLabels=false
secrets sanitized before Loki
Loki failures correctness-isolated
package remains 0.2.0
```

Validation reported:

```text
npm test: 49/49 pass
npm run typecheck: pass
npm run build: pass
npm pack --dry-run: pass
```

Security validation reported:

```text
winston 3.19.0
winston-loki 6.1.7
protobufjs 7.6.6
no new high/critical audit finding
```

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-002-SHARED-005` is Ready.

Publish one package containing both SHARED-004 and SHARED-006.

If the current package remains `0.2.0`, the architect-approved target remains:

```text
0.3.0
```

Do not resume SHOPIFY-003 until SHARED-005 is architect-accepted Complete.

