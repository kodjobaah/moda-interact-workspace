# ARCH-002 Observability Signal Routing Amendment

## Status

Architecture amendment for `ARCH-002`.

This document is authoritative for the signal-routing boundary consumed by
`ARCH-002-GATEWAY-006` and downstream deployment/system-validation tasks.

It does not change application business behaviour and does not transfer
application instrumentation ownership to `moda_gateway`.

## Decision

ARCH-002 treats traces, metrics and logs as independently configurable
observability signals.

The current initial deployment model is:

```text
                                ┌── traces ── OpenTelemetry ── OTLP ──> Grafana Cloud
Application / worker / gateway ─┼── metrics ─ OpenTelemetry ── OTLP ──> Grafana Cloud
                                │
                                └── logs ──── structured logging
                                              └── Loki-compatible transport
                                                  └──> current log backend:
                                                       Grafana Cloud / Loki
```

The destinations are independently configurable.

Changing the log destination in the future must not require changing Moda-owned
application logging calls or changing the trace/metric instrumentation model.

For example, a future architecture may keep:

```text
traces  -> OTLP -> Grafana Cloud
metrics -> OTLP -> Grafana Cloud
```

while changing only:

```text
logs -> Loki-compatible transport -> another approved log backend
```

## Signal ownership and transport ownership

### Moda-owned application repositories

Application repositories own the business/domain telemetry they explicitly emit.

They must not depend directly on Grafana-specific application APIs merely because
Grafana Cloud is the current backend.

### `moda-interact-shared`

`moda-interact-shared` owns reusable observability/runtime capabilities, including:

- the shared structured logging API;
- structured log record conventions;
- supported OpenTelemetry runtime/bootstrap behaviour;
- supported log transport capabilities;
- supported Loki transport capability;
- correlation fields and shared safe telemetry behaviour.

The existence of a supported transport does not require every deployment to
enable every transport.

### `moda_gateway`

`moda_gateway` owns deployed infrastructure/transport configuration, including:

- deployed OTLP endpoints;
- deployed Loki endpoint/configuration;
- secret-managed observability credentials;
- environment-specific routing;
- backend selection;
- transport enable/disable policy;
- retention/sampling/cost configuration where applicable.

`moda_gateway` must not rewrite application instrumentation merely to select a
different backend.

## Current ARCH-002 transport policy

### Traces

Current transport:

```text
OpenTelemetry -> OTLP -> Grafana Cloud
```

Required configuration remains vendor-neutral.

### Metrics

Current transport:

```text
OpenTelemetry -> OTLP -> Grafana Cloud
```

Required configuration remains vendor-neutral.

### Logs

Current preferred production log path:

```text
Moda structured logging -> Loki-compatible transport -> Grafana Cloud / Loki
```

The log destination must remain independently configurable from trace and metric
destinations.

OpenTelemetry Logs support may remain available in the shared runtime, but
ARCH-002 must not unintentionally persist the same application log event through
both:

```text
Loki transport
```

and:

```text
OTLP /v1/logs
```

Dual log export is permitted only when an explicit architecture decision requires
it and the duplication/cost implications are documented.

For the current ARCH-002 deployment, the default assumption is:

```text
OTLP traces:   enabled
OTLP metrics:  enabled
Loki logs:     enabled
OTLP logs:     disabled unless explicitly justified
```

This is a deployment policy, not a requirement to remove OpenTelemetry Logs
capability from `moda-interact-shared`.

## Collector policy

ARCH-002 does not introduce an OpenTelemetry Collector merely because collectors
are available.

The initial model uses direct exporter transport where supported.

A collector may be introduced later only when a concrete requirement justifies
it, for example:

- centralized routing;
- transformation;
- multi-backend export;
- centralized sampling;
- credential isolation;
- provider migration;
- operational buffering/retry requirements that cannot be satisfied safely by
  the accepted direct-export model.

## Resource identity

Every instrumented deployable unit must continue to emit:

```text
service.namespace=moda-interact
service.name=<canonical-logical-service-name>
deployment.environment.name=<environment>
```

The environment must not be encoded into `service.name`.

For ARCH-002 deployed environments:

```text
deployment.environment.name=test
deployment.environment.name=production
```

## Environment and credential isolation

Test and production observability configuration must be independently
configurable.

This includes, where applicable:

- OTLP endpoint;
- OTLP authentication;
- Loki endpoint;
- Loki authentication;
- signal enable/disable configuration;
- trace sampling;
- log routing;
- dashboard/backend selection.

No observability credential may be committed.

## Failure isolation

Observability remains non-critical to business correctness.

An unavailable trace, metric or log backend must not cause:

- Shopify webhook rejection;
- durable event acceptance failure;
- BullMQ business-job failure;
- checkout recovery failure;
- WhatsApp processing failure;
- CommerceAgent failure;
- database transaction rollback.

## Sampling, retention and cost policy

### Trace sampling

Trace sampling must remain configurable per environment.

The exact production rate is an operational assumption until measured production
traffic and observability cost are available.

Test may use a higher sampling rate where required for system validation.

Do not present an unmeasured sampling rate as a proven production optimum.

### Metrics

Prefer bounded, low-cardinality metrics.

Do not create high-cardinality dimensions merely to reproduce information already
available in traces/logs.

### Logs

Avoid storing complete high-volume webhook/customer payloads.

Prefer bounded structured operational fields.

The raw Shopify ingress target must not be interpreted as an obligation to store
one permanent log record per inbound event.

### Retention

Provider retention is governed by the selected backend/account configuration.

Until deployment configuration establishes exact retention, record it as
`UNKNOWN`/deployment-defined rather than inventing a duration.

### Cost

Observability cost remains `ESTIMATED`/`UNKNOWN` until actual ingestion volume,
sampling and retention are measured.

Trace, metric and log costs must be considered independently because their
destinations may diverge in the future.

## Consequences for GATEWAY-006

`ARCH-002-GATEWAY-006` must:

1. document the current trace, metric and log routes separately;
2. document Grafana Cloud as the current trace/metric backend;
3. document Loki-compatible transport as the current log path;
4. preserve independent signal destinations;
5. prevent or explicitly justify duplicate Loki + OTLP log persistence;
6. inspect accepted runtime contracts before declaring environment-variable
   requirements;
7. document actual sampling/retention/cost assumptions or explicitly mark them
   `UNKNOWN`/deployment-defined;
8. leave real hosted-backend connectivity validation to deployment/system testing
   when credentials are unavailable.

## Downstream validation

`SYSTEM-TEST-002` should ultimately validate, where applicable:

- traces reach the configured trace backend;
- metrics reach the configured metrics backend;
- logs reach the configured log backend;
- canonical resource identity is present;
- test and production telemetry remain distinguishable;
- no unintended duplicate log persistence exists;
- backend failure does not break business processing;
- prohibited secrets/payloads are absent.
