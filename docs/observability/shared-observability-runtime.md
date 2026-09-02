# Shared Observability Runtime Convention

## Purpose

Moda Interact uses one reusable Node observability runtime from
`@modainteract/moda-interact-shared`.

The architectural invariant is:

```text
shared owns HOW telemetry is bootstrapped/exported
service owns WHAT its business activity means
```

This document is the durable integration contract for service agents.

## ARCH-002 published release

The current architect-approved release for ARCH-002 consumers is:

`@modainteract/moda-interact-shared@0.4.0`

Use the exact version. Do not consume a floating range during ARCH-002 rollout.

## Canonical package surfaces

After the architecture-approved shared observability release is published, use:

```text
@modainteract/moda-interact-shared/observability
@modainteract/moda-interact-shared/observability/node
@modainteract/moda-interact-shared/observability/bullmq
@modainteract/moda-interact-shared/observability/genai
```

`./observability/node`, `./observability/bullmq`, and `./observability/genai` are
Node/runtime surfaces. Do not pull them through browser/Vite client graphs.

## Ownership boundary

`moda-interact-shared` owns reusable mechanics including:

- NodeSDK bootstrap and process lifecycle;
- canonical resource identity;
- trace and metric providers;
- OTLP exporters;
- sampling configuration;
- bounded batching/flush/shutdown;
- HTTP/HTTPS and Undici/fetch instrumentation;
- optional Prisma instrumentation added by the shared Prisma adapter task;
- BullMQ telemetry adapter;
- generic GenAI/agent/tool observation helpers;
- integration with the accepted shared logging runtime.

A service repository owns:

- its canonical `service.name` profile;
- which approved shared instrumentations are enabled;
- its process preload file and start-command wiring;
- business/domain semantic spans and metrics;
- bounded domain attributes;
- queue/worker use of the shared BullMQ telemetry object;
- service-specific tests proving the integration works.

## Prohibited local duplication

Once the required shared package version is available, a service task must not
create or retain a competing service-local implementation of:

```text
NodeSDK
TracerProvider / MeterProvider
OTLP trace or metric exporter
sampler/bootstrap policy
BatchSpanProcessor/metric-reader lifecycle
HTTP/Undici generic runtime instrumentation
Prisma generic runtime instrumentation
BullMQOtel construction helpers
```

Service-specific semantic instrumentation is still allowed. It must use the
global providers installed by the shared runtime and must not install another
provider/exporter stack.

## Framework-first telemetry reuse

Service-specific does not mean service-duplicated. Before adding a custom
metric/span, inspect the telemetry already emitted by the enabled framework and
approved OpenTelemetry/shared instrumentation.

If standard instrumentation already provides an operationally equivalent
technical signal, use that signal directly. Do not create a Moda metric/span
solely to rename, re-bucket, relabel or maintain a second route taxonomy for the
same lifecycle.

Typical generic signals that should be reused when actually available from the
installed/configured instrumentation include:

```text
HTTP server request count/duration/status/method/route
HTTP client request spans/metrics
framework request spans
Prisma/database client spans
BullMQ producer/consumer spans or metrics supplied by the approved adapter
```

Availability must be established from the installed version/configuration and
export path; documentation or package presence alone is not enough.

A custom service metric/span is justified when it adds Moda-specific semantic
meaning that generic instrumentation cannot know, for example a webhook being
accepted/rejected after provider verification, a recovery transition, a
privileged admin action, a billing event or a CommerceAgent business outcome. A
custom signal may also be justified when the required unsampled/aggregated
operational property is not supplied by the existing signal. Record that gap in
the task or Completion Report.

Do not maintain a custom route allowlist merely to recreate ordinary framework
HTTP request telemetry. New application routes should become observable through
the approved framework/runtime instrumentation without changes to a parallel
Moda metric schema.

If an implementation task is discovered to duplicate existing approved
telemetry, return it to `moda_architect` for narrowing or supersession rather
than implementing the duplicate.

If the published shared version lacks a required generic capability, return the
gap to `moda_architect`. Do not silently recreate the missing runtime locally.

## Required process ordering

Instrumentation must be registered before the framework/worker modules that it
needs to patch are imported:

```text
node process
  -> repository preload
      -> initNodeObservability(...)
  -> framework/worker entrypoint
  -> application modules
```

Do not initialize the heavy Node OTel runtime from React Router `entry.server`,
Next.js route modules, worker processors, or other modules loaded after the
framework/runtime dependencies.

## Consumer integration procedure

Every service agent adopting the shared runtime must perform this sequence:

1. Confirm `ARCH-002-SHARED-010` (or its superseding shared release task) is
   architect-accepted Complete.
2. Consume the exact architecture-approved published shared package version.
3. Inspect the repository's real production start command/entrypoint. Do not
   invent one.
4. Add a small repository-owned preload such as `observability.mjs` that imports
   `initNodeObservability` from `.../observability/node` and supplies only the
   service profile.
5. Change the production process command so the preload runs before the real
   framework/worker entrypoint.
6. Enable only the shared instrumentation the service actually uses.
7. Where BullMQ Queue/Worker objects are created, construct telemetry through
   `.../observability/bullmq` and pass it through BullMQ's supported `telemetry`
   option. Do not monkey-patch BullMQ.
8. Preserve or add service-owned semantic spans/metrics, but use the global
   provider installed by the shared runtime. Create instruments once at module
   or process scope, never per request/job.
9. Remove obsolete service-local provider/exporter/bootstrap code only after
   equivalent shared behaviour has been proven by tests.
10. Validate early bootstrap, canonical identity, trace continuity where
    applicable, telemetry failure isolation, sensitive-data safety, and metric
    cardinality.

## Service profiles

### moda-interact / `moda_app`

Canonical service identity:

```text
service.name=moda-interact
```

Final shared profile after SHARED-008:

```js
initNodeObservability({
  serviceName: "moda-interact",
  instrument: { http: true, fetch: true, prisma: true },
});
```

The Shopify service is also a BullMQ producer where it publishes queued work.
Use `createBullMQTelemetry(...)` on those Queue instances when required by the
accepted queue implementation.

For the current React Router production shape, the preload must precede
`react-router-serve`, for example:

```text
node --import ./observability.mjs ./node_modules/@react-router/serve/bin.js ./build/server/index.js
```

Shopify webhook acceptance/latency/error semantics remain owned by `moda_app`.

### moda-interact-messaging / `moda_messaging`

Canonical service identity:

```text
service.name=moda-interact-messaging
```

Profile:

```js
initNodeObservability({
  serviceName: "moda-interact-messaging",
  instrument: { http: true, fetch: true, prisma: false },
});
```

The messaging ingress is a BullMQ producer. Pass shared BullMQ telemetry through
its inbound Queue options so accepted trace context can continue into the
background consumer.

For the current React Router production shape, preload before
`react-router-serve`.

### moda-interact-admin / `moda_admin`

Canonical service identity:

```text
service.name=moda-interact-admin
```

Final shared profile after SHARED-008:

```js
initNodeObservability({
  serviceName: "moda-interact-admin",
  instrument: { http: true, fetch: true, prisma: true },
});
```

For the current Next.js production shape, preload before the Next CLI, for
example:

```text
node --import ./observability.mjs ./node_modules/next/dist/bin/next start
```

Admin request/database semantics remain owned by `moda_admin`. Grafana UI or
embedding is a separate admin presentation concern.

### moda-interact-background / `moda_background`

ARCH-002 defines independently deployable worker identities:

```text
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

Each production worker process gets its own preload/profile with the matching
`service.name`. After `BACKGROUND-001` has established the actual worker
commands, prefix each real worker command with its matching preload. Do not
invent worker entrypoints before that task is complete.

Final generic instrumentation after SHARED-008:

```text
HTTP/Undici=true where external calls occur
Prisma=true where used
BullMQ producer/consumer=true
```

`moda-messaging-worker` additionally uses the generic GenAI/agent/tool helpers.
One inbound WhatsApp turn is one trace. Do not model a whole multi-message
customer conversation as one trace.

## Sampling

The shared runtime owns sampling policy and must honour the architecture-approved
OpenTelemetry configuration. Services must not implement their own sampler.

At minimum the shared runtime supports the standard local sampler modes used by
Moda:

```text
always_on
always_off
traceidratio
parentbased_always_on
parentbased_always_off
parentbased_traceidratio
```

For ratio samplers, `OTEL_TRACES_SAMPLER_ARG` is interpreted only when the
selected sampler accepts a ratio. A service may not reinterpret these variables.

## Flush and shutdown

`NodeObservabilityRuntime.forceFlush()` means flush every initialized shared
signal pipeline:

```text
traces
metrics
OpenTelemetry Logs
Loki
```

A service must not add a second shutdown/flush implementation for shared
providers. Service shutdown may call the shared runtime lifecycle together with
its own business-resource shutdown.

## Cardinality and data safety

Metric attributes must come from small architecture-controlled vocabularies.
Truncating an arbitrary identifier does not make it low-cardinality.

Do not use customer, conversation, checkout, order, message, job, trace or other
high-cardinality Moda identifiers as metric attributes or Loki labels.

Agent/tool names may be recorded as bounded span attributes where useful, but
shared GenAI duration metrics must not use arbitrary agent/tool names as metric
labels.

Do not capture prompts, completions, message bodies, access tokens, credentials,
authorization headers, full webhook payloads or sensitive database values by
default.

## Failure isolation

Observability is never a business correctness dependency. Exporter/backend
failure must not reject otherwise valid HTTP requests, fail BullMQ business
jobs, roll back database work, or fail CommerceAgent processing.
