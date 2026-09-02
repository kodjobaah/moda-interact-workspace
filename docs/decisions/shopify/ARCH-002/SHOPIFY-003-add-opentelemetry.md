---
id: ARCH-002-SHOPIFY-003
architecture_id: ARCH-002
title: Add OpenTelemetry to Shopify ingress
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-002-GATEWAY-001
- ARCH-002-SHARED-010
enables: []
created: 2026-08-29
updated: '2026-08-31'
---
# Add OpenTelemetry to Shopify Ingress

## Superseded — Granular Replacement (2026-08-31)

This task must not be executed.

The earlier local OpenTelemetry implementation remains historical evidence. The executable migration is now split into shared-runtime adoption and BullMQ producer telemetry.

Replacement tasks:

- `ARCH-002-SHOPIFY-006`
- `ARCH-002-SHOPIFY-007`

This change applies the current architect task-granularity policy. Historical
implementation/completion material below is retained only as evidence and does
not define executable scope.

## Current Architect Instruction — Shared Runtime

This task's executable architecture is the shared-runtime amendment in this
file plus `docs/observability/shared-observability-runtime.md`. Any earlier
service-local NodeSDK/provider/exporter/bootstrap instructions or completion
notes are historical implementation evidence and are superseded where they
conflict with the shared-runtime amendment. Service/domain semantic telemetry
remains owned by this repository.

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Instrument the Shopify HTTP/webhook runtime with architecture-approved,
vendor-neutral OpenTelemetry telemetry and correlation propagation.

## Context

Accepted discovery found no OpenTelemetry implementation in `moda-interact`.

ARCH-002 requires operational visibility in both test and production without
making telemetry a correctness dependency.

## Scope

- initialize OpenTelemetry once and early enough for supported HTTP
  instrumentation;
- instrument inbound/outbound HTTP where required;
- emit bounded Shopify webhook latency/error/acceptance telemetry;
- propagate trace/correlation context into produced asynchronous work where the
  accepted queue/shared boundary supports it;
- use canonical resource identity;
- support standard OTel environment configuration;
- preserve test/production telemetry isolation;
- validate telemetry failure isolation;
- validate sensitive-data and metric-cardinality restrictions.

## Out of Scope

- OTLP backend/credential provisioning;
- Grafana dashboards;
- background consumer instrumentation;
- changing webhook business contracts unless an architect-approved
  trace-context contract is required;
- logging/storing complete Shopify webhook payloads;
- tenant-facing analytics.

## Requirements

Canonical resource identity:

```text
service.namespace=moda-interact
service.name=moda-interact
deployment.environment.name=<environment>
```

For deployed ARCH-002 environments:

```text
deployment.environment.name=test
deployment.environment.name=production
```

Do not encode the environment into `service.name`.

Test and production exporter endpoint/credentials must remain independently
configurable through infrastructure.

Local/unit-test hosted export must be disableable.

Telemetry export failure must not reject Shopify webhooks, prevent durable queue
acceptance or change business success/failure semantics.

Telemetry buffering/retries must remain bounded.

Do not emit:

- Shopify access tokens;
- authorization/cookie headers;
- OAuth authorization codes;
- complete webhook payloads;
- customer PII;
- high-cardinality business identifiers as metric labels.

If async trace propagation requires a shared contract change, return the required
change to `moda_architect` rather than modifying cross-service business contracts
inside this task.

## Work Items

- [x] initialize OTel exactly once/early;
- [x] add HTTP server/client instrumentation where required;
- [x] add bounded Shopify ingress metrics/spans;
- [x] add canonical resource attributes;
- [x] propagate context to async publication where architecture-compatible;
- [x] preserve test/production resource isolation;
- [x] add exporter-failure isolation tests;
- [x] add metric-cardinality validation;
- [x] add sensitive-data validation;
- [x] document required OTel variables for GATEWAY-006.

## Interfaces / Contracts

Emits OTel/OTLP-compatible telemetry.

Infrastructure transport/credentials are owned by:

```text
ARCH-002-GATEWAY-006
```

The logical service name remains:

```text
moda-interact
```

in both test and production.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-GATEWAY-006`

## Acceptance Criteria

- [x] expected canonical service identity is emitted;
- [x] test and production differ through deployment environment attributes rather
      than service name;
- [x] webhook processing succeeds when telemetry backend is unavailable;
- [x] HTTP/webhook telemetry is emitted with bounded cardinality;
- [x] correlation/trace context is preserved where architecture-compatible;
- [x] any required cross-service contract change is returned to the architect;
- [x] no prohibited secrets/payloads appear in telemetry;
- [x] telemetry buffering/retry behaviour is bounded;
- [x] local/test hosted export can be disabled.

## Validation

- [x] unit/integration tests;
- [x] typecheck;
- [x] production build;
- [x] telemetry failure test;
- [x] test/production resource identity test;
- [x] sensitive-data review;
- [x] metric-cardinality review.

## Implementation Notes

Prefer standard OpenTelemetry environment variables and backend-neutral APIs.

## Required OTel Variables for GATEWAY-006

The moda-interact Shopify service consumes only standard OpenTelemetry
environment variables plus one deployment-environment override. GATEWAY-006
must wire the following for test and production:

| Variable | Purpose | Required |
| --- | --- | --- |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Base OTLP/HTTP collector URL (the SDK appends `/v1/traces` and `/v1/metrics` unless the per-signal variables below are set). | Yes, when telemetry is enabled |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` | Per-signal traces endpoint override. | No |
| `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` | Per-signal metrics endpoint override. | No |
| `OTEL_TRACES_EXPORTER` | Defaults to `otlp`; any other value (e.g. `console`) disables OTLP traces. | No |
| `OTEL_METRICS_EXPORTER` | Defaults to `otlp`; any other value disables OTLP metrics. | No |
| `OTEL_SDK_DISABLED` | `true` forces the SDK off even when an endpoint is configured. | No |
| `OTEL_BSP_SCHEDULE_DELAY` | Trace batch span schedule delay (ms). Default `5000`. | No |
| `OTEL_BSP_MAX_QUEUE_SIZE` | Trace batch span queue size. Default `2048`. | No |
| `OTEL_BSP_MAX_EXPORT_BATCH_SIZE` | Trace batch size. Default `512`. | No |
| `OTEL_BSP_EXPORT_TIMEOUT` | Trace export timeout (ms). Default `30000`. | No |
| `OTEL_METRIC_EXPORT_INTERVAL` | Metric export interval (ms). Default `60000`. | No |
| `OTEL_METRIC_EXPORT_TIMEOUT` | Metric export timeout (ms). Default `30000`. | No |
| `DEPLOYMENT_ENVIRONMENT_NAME` | Canonical `deployment.environment.name` (`test`, `production`, or a named environment). Falls back to `NODE_ENV`. | Yes, for canonical identity |

Behaviour notes for GATEWAY-006:

- The OTLP endpoint is intentionally NOT defaulted to `localhost:4318`.
  Without an explicit endpoint the SDK is a no-op, so local/dev/test/ephemeral
  hosts never export telemetry unless an endpoint is configured.
- Every signal carries `service.namespace=moda-interact`,
  `service.name=moda-interact` and `deployment.environment.name`; environment
  is never encoded into `service.name`.
- Exporter credentials/headers are transport-owned (e.g.
  `OTEL_EXPORTER_OTLP_HEADERS`); the app treats export as best-effort and
  failure-isolated.
- Metric cardinality is bounded server-side by an attribute allowlist and a
  cardinality cap of `64`; no per-tenant or high-cardinality business
  identifiers are emitted as metric labels.

## Completion Report

### Status

Ready for Review

### Files Changed

Within `moda-interact/`:

- `app/entry.server.jsx` — call `initOpenTelemetry()` once at server boot
  (no-op without an OTLP endpoint).
- `app/services/otel/otel.constants.ts` — new: telemetry identity constants,
  bounded webhook attribute allowlist, metric cardinality cap.
- `app/services/otel/otel.server.ts` — new: one-time OpenTelemetry SDK
  bootstrap, canonical resource identity, bounded batch/metric configuration,
  `getActiveTraceId`, deployment-environment resolution.
- `app/services/otel/shopify-webhook-telemetry.server.ts` — new: Shopify
  webhook span/counter/histogram emission; consumes the
  `ShopifyWebhookObservation` type.
- `app/services/webhooks/shopify-webhook-observation.ts` — new: type-only
  PII-safe Shopify webhook observation contract.
- `app/services/webhooks/shopify-webhook-observability.server.ts` — new: thin
  Shopify semantic adapter — shared `createLogger` record plus Shopify OTel.
- `app/services/webhooks/shopify-webhook-ingress.service.ts` — record outcomes
  through `recordShopifyWebhookOutcome`; carry the active trace id on the
  queued event envelope.
- `app/services/webhooks/shopify-webhook-logger.ts` — deleted (local generic
  logger removed; generic logging is owned by the shared package).
- `tests/unit/otel/otel-init.test.js` — new: SDK bootstrap, telemetry-failure
  and resource-identity tests.
- `tests/unit/otel/shopify-webhook-telemetry.test.js` — new: span/metric
  attribute-boundary tests.
- `tests/unit/otel/shopify-webhook-ingress-traceid.test.js` — new: trace-id
  propagation tests.
- `tests/unit/webhooks/shopify-webhook-ingress.service.test.js` — shared
  logging boundary test (PII-safe envelope through the shared sink).
- `package.json`, `package-lock.json` — `@opentelemetry/*` dependencies;
  `@modainteract/moda-interact-shared@0.2.0` (exact, per coordination
  amendment).
- `vite.config.js` — SSR bundling of `@opentelemetry` packages.
- `vitest.config.ts` — vitest configuration for the added unit tests.

### Work Completed

- Initialised the OpenTelemetry SDK exactly once at server boot; without an
  OTLP endpoint the SDK runs as a no-op so local/dev/test hosts never export.
- Added HTTP server/client instrumentation (HTTP + undici/fetch).
- Added bounded Shopify webhook telemetry: `shopify.webhook.process` span plus
  `shopify.webhook.ingress` counter and `shopify.webhook.duration` histogram.
- Added canonical resource identity (`service.namespace`, `service.name`,
  `deployment.environment.name`), with environment resolved from
  `DEPLOYMENT_ENVIRONMENT_NAME` and falling back to `NODE_ENV`.
- Propagated the active trace id into the queued event envelope (`traceId`)
  via `getActiveTraceId`, falling back to the generated request id.
- Removed the local generic logger and replaced it with a thin Shopify
  semantic adapter on `@modainteract/moda-interact-shared/logging`;
  Shopify-specific OTel remains local and separate.
- Enforced sensitive-data and metric-cardinality restrictions: span/metric
  attributes are an allowlisted 5-key set, metric Views cap cardinality at
  `64`, and log records carry only PII-safe observation fields.
- Isolated telemetry failure: SDK no-op path and try/catch emission mean
  logging/telemetry can never affect webhook correctness.

### Validation Results

- unit/integration tests — `npm test`: 13 files / 82 tests passed.
- typecheck — `npm run typecheck`: 48 pre-existing errors matching documented
  baseline TYPECHECK-001; 0 new errors in task-changed files.
- production build — `npm run build`: succeeded (SSR bundle built).
- telemetry failure test — `otel-init.test.js`: no-op runtime when no OTLP
  endpoint is configured; `forceFlush` resolves; telemetry inactive.
- test/production resource identity test — `otel-init.test.js`: canonical
  resource attributes asserted; environment resolution from
  `DEPLOYMENT_ENVIRONMENT_NAME` and `NODE_ENV` fallback.
- sensitive-data review — span/metric attributes are the 5 allowlisted keys;
  log records carry only PII-safe observation fields; boundary test asserts
  customer email/phone and checkout token never reach output.
- metric-cardinality review — metric Views enforce the attribute allowlist and
  cap cardinality at 64; no per-tenant/high-cardinality metric labels.

### Deviations

None. Trace propagation reuses the existing `traceId` field on the queued
recovery event envelope; no cross-service contract change was required.

### Assumptions

- `@modainteract/moda-interact-shared@0.2.0` is the exact
  architect-approved shared logging package version.
- `DEPLOYMENT_ENVIRONMENT_NAME` is the canonical deployment-environment
  override; it falls back to `NODE_ENV`.

### Unresolved Issues

None.

### Architectural Concerns

None. Logging and telemetry remain correctness-isolated and best-effort.

## Architect Review

### Review Status

Pending architect review — implementation complete, ready for review.

### Review Notes

All coordination amendments satisfied: shared `@modainteract/moda-interact-shared@0.2.0`
`./logging` consumed, local generic logger removed, Shopify-specific OTel kept
local, canonical identity in place, telemetry/logging failure-isolated.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.

<!-- ARCH-002-SHARED-LOGGING-COORDINATION:START -->
## Architect Coordination Amendment — Shared Structured Logging

### Coordination Status

Blocked pending:

```text
ARCH-002-SHARED-002
```

### Architectural Decision

Generic structured logging is now owned by:

```text
moda-interact-shared
@modainteract/moda-interact-shared/logging
```

The local Shopify implementation currently centred on:

```text
app/services/webhooks/shopify-webhook-logger.ts
```

must not become the platform's generic logging implementation.

This task remains the owner of Shopify-specific observability semantics and
Shopify-specific OpenTelemetry instrumentation.

### Required Work When This Task Resumes

Only resume after `ARCH-002-SHARED-002` is `complete`.

Then:

1. consume:

   ```ts
   import { createLogger } from
     "@modainteract/moda-interact-shared/logging";
   ```

2. remove the local generic logger implementation, including the direct
   `console.info("shopify_webhook", JSON.stringify(...))` logging mechanism;

3. do not recreate local generic:

   ```text
   JSON serialisation
   log-level infrastructure
   redaction
   error serialisation
   size/depth bounds
   sink abstraction
   ```

4. preserve Shopify-specific OpenTelemetry in `moda-interact`;

5. move/retain the Shopify observation type in a Shopify-specific module rather
   than making the shared logger package depend on Shopify semantics;

6. a thin Shopify-specific semantic adapter may remain if useful, for example:

   ```text
   recordShopifyWebhookOutcome
       -> shared logger
       -> Shopify-specific OTel
   ```

   but that adapter must contain no generic logger implementation;

7. use the canonical logger identity:

   ```text
   service.namespace=moda-interact
   service.name=moda-interact
   deployment.environment.name=<resolved environment>
   ```

8. preserve the existing rule that logging/telemetry failure cannot affect
   webhook correctness;

9. preserve the current OTel metric-cardinality allowlist;

10. ensure no complete webhook payload, customer PII, access token, OAuth code,
    authorization/cookie header or other prohibited data is logged;

11. update tests so they validate the shared logging boundary rather than the
    deleted local logger implementation;

12. rerun this task's full required validation and return `status: review`.

### Recommended Shopify Structure

The generic logger should disappear from the Shopify repository.

A service-specific structure such as this is acceptable:

```text
app/services/webhooks/
    shopify-webhook-observation.ts
    shopify-webhook-observability.server.ts

app/services/otel/
    shopify-webhook-telemetry.server.ts
```

Where:

```text
shopify-webhook-observation.ts
    ShopifyWebhookObservation type only

shopify-webhook-observability.server.ts
    createLogger(...) from shared
    recordShopifyWebhookOutcome(...)
        -> logger.info(...)
        -> recordShopifyWebhookTelemetry(...)

shopify-webhook-telemetry.server.ts
    Shopify-specific OTel spans/metrics only
```

The exact filenames may differ if the current implementation has a clearer
equivalent, but the ownership boundary must not differ.

### Consumer Documentation

Read:

```text
docs/observability/shared-logging.md
```

before implementing the correction.

### Acceptance Addition

SHOPIFY-003 cannot be accepted until:

- `ARCH-002-SHARED-002` is Complete;
- no service-local generic Shopify logger remains;
- Shopify structured logs use the shared `./logging` export;
- Shopify-specific OTel remains local and independent;
- logging and OTel failures remain correctness-isolated;
- tests/build/typecheck required by SHOPIFY-003 pass.

<!-- ARCH-002-SHARED-LOGGING-COORDINATION:END -->

<!-- ARCH-002-SHARED-LOGGING-RELEASE:START -->
## Architect Coordination Amendment — Published Shared Logging Release

SHOPIFY-003 remains **Blocked** after SHARED-002 implementation.

It may resume only after:

```text
ARCH-002-SHARED-003 = Complete
```

SHARED-003 publishes and independently verifies the npm artifact containing:

```text
@modainteract/moda-interact-shared/logging
```

When SHOPIFY-003 resumes it must consume the exact published package version
accepted by SHARED-003.

Do not resume against an unpublished workspace-only logging export.

<!-- ARCH-002-SHARED-LOGGING-RELEASE:END -->

<!-- ARCH-002-SHARED-LOGGING-PUBLISHED-VERSION -->
## Architect-Approved Shared Logging Package Version

The shared implementation and public release dependencies are Complete.

SHOPIFY-003 must consume the exact accepted package version:

```text
@modainteract/moda-interact-shared@0.2.0
```

Required logging subpath:

```text
@modainteract/moda-interact-shared/logging
```

Do not use a floating package range for this architecture handoff.

## Architect Amendment — Shared Observability Runtime (2026-08-31)

**This amendment supersedes any conflicting service-local NodeSDK/provider/
exporter/bootstrap instructions earlier in this task.** Shopify still owns its
business-semantic webhook spans/metrics; it no longer owns generic runtime
plumbing.

Do not resume implementation until `ARCH-002-SHARED-010` is architect-accepted
Complete and its exact published package version is recorded.

Then:

1. install/use that exact shared package version;
2. read `docs/observability/shared-observability-runtime.md`;
3. add a repository-owned preload importing
   `@modainteract/moda-interact-shared/observability/node`;
4. use the final profile:

```js
initNodeObservability({
  serviceName: "moda-interact",
  instrument: { http: true, fetch: true, prisma: true },
});
```

5. preload it before the existing React Router production entrypoint:

```text
node --import ./observability.mjs ./node_modules/@react-router/serve/bin.js ./build/server/index.js
```

6. where Shopify publishes BullMQ jobs, use
   `@modainteract/moda-interact-shared/observability/bullmq` and pass the shared
   telemetry object through the Queue's supported `telemetry` option;
7. preserve Shopify-specific acceptance/latency/error semantics using the global
   providers installed by shared runtime;
8. remove obsolete local heavy OTel provider/exporter/bootstrap modules only
   after equivalent shared behaviour is proven;
9. do not add Prisma/BullMQ/HTTP exporters or sampler logic locally.

Reference code:
`docs/decisions/shared/ARCH-002/reference-observability/services/moda-interact/`.
