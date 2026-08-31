# Shared Logging — Direct Loki Addendum

Direct Loki is an optional Node transport of the shared logger.

Application code continues to call only:

```ts
logger.info(...)
logger.warn(...)
logger.error(...)
```

The process bootstrap may enable direct Loki:

```ts
import {
  initNodeLokiLogging,
} from "@modainteract/moda-interact-shared/logging/node";

initNodeLokiLogging({
  serviceName: "moda-interact",
  environment: "production",
});
```

Deployment variables:

```text
LOKI_URL
LOKI_USERNAME
LOKI_PASSWORD
```

No URL means direct Loki is disabled.

Only these static labels are indexed by default:

```text
service_namespace
service_name
environment
```

Never promote request/job/customer/trace identifiers to default Loki labels.

If OpenTelemetry Logs are also enabled, ensure their backend path does not
forward the same records into the same Loki instance unless duplicate storage
is deliberately desired.
