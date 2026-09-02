<!-- ARCH-002-SHARED-OTEL-LOGGING:START -->
## Architect Coordination Amendment — Shared OpenTelemetry Logging

The clarified logging architecture introduces a new required shared dependency:

```text
ARCH-002-SHARED-004
ARCH-002-SHARED-005
```

SHOPIFY-003 must not implement its own OpenTelemetry Logs exporter/provider.

It remains responsible for:

```text
Shopify traces
Shopify metrics
HTTP/undici instrumentation
process-level trace/metric bootstrap
trace context propagation
```

The shared package owns:

```text
structured stdout logs
OpenTelemetry LogRecord emission
Node LoggerProvider / OTLP log exporter
```

When SHOPIFY-003 resumes after SHARED-005:

1. consume exact architect-accepted shared version (expected `0.3.0`);
2. application code imports only `@modainteract/moda-interact-shared/logging`;
3. the process-level bootstrap imports
   `@modainteract/moda-interact-shared/logging/node`;
4. initialize shared OTel logging before Vite/React Router application modules;
5. initialize/fix Shopify trace + metric instrumentation at that same true
   process bootstrap boundary;
6. do not duplicate the shared log exporter;
7. preserve the previously requested production-start inbound/outbound tracing
   validation;
8. prove a log emitted under active tracing context is trace-correlated in the
   integration test where practical.

<!-- ARCH-002-SHARED-OTEL-LOGGING:END -->
