# ARCH-002 Shared Logger OpenTelemetry Logs Amendment

## Decision

The shared logger owns the platform's **logging signal**, including:

```text
safe structured stdout
OpenTelemetry LogRecord emission
Node OTLP log-provider/exporter bootstrap
```

Service repositories continue to own service-specific:

```text
traces
metrics
HTTP/BullMQ/provider instrumentation
```

## Package split

```text
@modainteract/moda-interact-shared/logging
    safe application-facing API
    stdout + OpenTelemetry Logs API emission
    no Node SDK/exporter imports

@modainteract/moda-interact-shared/logging/node
    Node-only LoggerProvider
    BatchLogRecordProcessor
    OTLPLogExporter
    Resource identity
```

## Why

This gives every Moda runtime one logging abstraction while avoiding duplicated
OTel log setup in Shopify, messaging, admin and background.

It also prevents the Node OTel SDK/exporter from being evaluated through Vite
or browser application bundles.

## Context correlation

The shared logger does not create spans.

When a service-specific tracing provider/context manager has established an
active span, the OpenTelemetry Logs SDK associates the log with the active
context.

## Sequencing

```text
SHARED-003 Complete / 0.2.0
        |
        v
SHARED-004 implement OTel logs
        |
        v
architect review
        |
        v
SHARED-005 publish 0.3.0
        |
        v
architect review
        |
        v
SHOPIFY-003 resume
```

SHOPIFY-003 still owns its trace/metric bootstrap correction. It must not build
a separate OpenTelemetry log exporter once the shared `0.3.0` logger is
available.
