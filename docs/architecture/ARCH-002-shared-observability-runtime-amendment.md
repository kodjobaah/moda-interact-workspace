# ARCH-002 Amendment — Shared Observability Runtime

## Decision

OpenTelemetry SDK/bootstrap/instrumentation plumbing is a cross-service platform
capability and is owned by `moda-interact-shared`, not independently by each
service repository.

The invariant is:

```text
shared owns HOW telemetry is installed and exported
service owns WHAT business activity means
```

`moda-interact-shared` therefore owns the reusable Node observability runtime,
resource identity, context management, OTLP trace/metric exporters, sampling,
batching, HTTP/Undici instrumentation, the Prisma adapter introduced by
SHARED-008, the BullMQ telemetry adapter, and generic GenAI/agent span helpers.

Service repositories retain only their service profile, process-preload wiring,
and bounded business semantics.

The durable consumer contract is:

`docs/observability/shared-observability-runtime.md`

## Task boundary correction

The implementation boundary is intentionally staged:

```text
SHARED-007
  base Node runtime only
  - NodeSDK lifecycle
  - resources
  - traces/metrics
  - OTLP
  - sampling
  - HTTP/HTTPS
  - Undici/fetch
  - logging integration

SHARED-008
  runtime adapters
  - Prisma instrumentation/profile extension
  - BullMQ telemetry adapter/context continuity

SHARED-009
  GenAI active-span helpers
  - conversation-turn spans
  - agent invocation spans
  - tool invocation spans

SHARED-011
  GenAI operational metrics
  - bounded duration histograms
  - bounded success/error counters
  - closed metric dimensions
```

SHARED-007 must not pre-implement Prisma or BullMQ. SHARED-008 may extend the
shared Node runtime/profile after SHARED-007 is accepted.

## Published ARCH-002 release

The architect-accepted shared observability runtime release is:

`@modainteract/moda-interact-shared@0.4.0`

ARCH-002 consumer tasks must use this exact version unless a later
architect-approved publication task supersedes it.

## Required process ordering

Node auto-instrumentation must start before framework/application dependencies:

```text
node process
    -> observability preload
        -> shared Node OTel runtime
        -> instrumentation registered
    -> framework/worker entrypoint
    -> application modules
```

For React Router services the reference launch shape is:

```bash
node --import ./observability.mjs ./node_modules/@react-router/serve/bin.js ./build/server/index.js
```

For the current Next.js admin production shape the equivalent reference is:

```bash
node --import ./observability.mjs ./node_modules/next/dist/bin/next start
```

Do not initialize the heavy OTel Node SDK from `entry.server`, route modules,
Vite application graphs, worker processors, or after Express/HTTP/Prisma/BullMQ
have already been loaded.

## Service profiles

```text
moda-interact
  HTTP server/client + Undici/fetch + Prisma + BullMQ producer

moda-interact-admin
  HTTP server/client + Undici/fetch + Prisma

moda-interact-messaging
  HTTP server/client + Undici/fetch + BullMQ producer

moda-interact-background
  BullMQ producer/consumer + Prisma + HTTP/Undici + GenAI/agent/tool spans
```

Prisma is introduced into the final profile by SHARED-008, not SHARED-007.

## Sampling correction

The shared runtime must honour `OTEL_TRACES_SAMPLER` together with
`OTEL_TRACES_SAMPLER_ARG` rather than reading the argument while ignoring the
selected sampler.

The architecture-approved implementation must support at least:

```text
always_on
always_off
traceidratio
parentbased_always_on
parentbased_always_off
parentbased_traceidratio
```

A programmatic task-specific sample ratio may override environment configuration
when explicitly supplied. Invalid/unsupported sampler configuration must not
crash business startup; it must fall back to the documented Moda policy with a
bounded configuration warning.

## Flush semantics correction

`NodeObservabilityRuntime.forceFlush()` means all initialized shared pipelines:

```text
trace BatchSpanProcessor
metric reader/provider
OpenTelemetry Logs
Loki
```

It must not flush only logging while presenting itself as a runtime-wide flush.
Shutdown remains failure-isolated and idempotent at the process level.

## WhatsApp / CommerceAgent trace boundary

A whole customer conversation must NOT be represented by one long trace.
One inbound conversation turn is one trace:

```text
inbound WhatsApp turn
    -> queue wait / BullMQ processing
    -> conversation lookup
    -> CommerceAgent invocation
        -> LLM invocation
        -> tool invocation(s)
        -> outbound provider HTTP
```

Conversation/customer/shop identifiers are not metric labels. High-cardinality
identifiers must not be promoted to Loki labels or metric attributes.

## GenAI metric-cardinality correction

String truncation is not a cardinality control.

Agent/tool names may be useful on spans, but shared GenAI duration metrics must
not attach arbitrary `agent.name` or `tool.name` values. Shared metric dimensions
must be absent or come from a small architecture-controlled vocabulary.

## Performance safety

- metrics are collected for all operations where practical;
- production tracing is sampled and configurable;
- test tracing may use 100% sampling;
- exporters use bounded batching/queues/timeouts;
- telemetry backend failure must not affect business correctness;
- invalid telemetry configuration must degrade telemetry, not crash the service;
- providers are marked active only after successful initialization;
- instruments are created once, not on every hot-path request/job.

## Implementation ownership

The implementation sequence is:

```text
SHARED-005 accepted Complete
            |
       SHARED-007 base Node runtime
            |\
            | +----> SHARED-008 Prisma + BullMQ adapters
            +------> SHARED-009 GenAI active spans
                          |
                     SHARED-011 GenAI metrics
                          |
                 SHARED-010 publish 0.4.0
                          |
      +-------------------+----------------------+------------------+
      |                   |                      |                  |
 SHOPIFY-006         BACKGROUND-003*        MESSAGING-003       ADMIN-009
      |                                          |                  |
 SHOPIFY-007                            +---------+---------+    ADMIN-010
                                       |                   |
                                MESSAGING-004        MESSAGING-005

* BACKGROUND-003 remains a decomposition gate until BACKGROUND-001 establishes
  the actual worker entrypoints.
```

The service tasks must not recreate local Node tracer/meter providers or
service-local OTLP exporters once `SHARED-010` is available.
