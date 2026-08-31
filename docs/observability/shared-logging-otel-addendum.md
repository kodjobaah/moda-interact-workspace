# Shared Logging — OpenTelemetry Logs Addendum

The canonical Moda logger is intended to fan one safe log call to two outputs:

```text
logger.info(...)
    |
    +--> structured JSON stdout
    |
    +--> OpenTelemetry Logs API
```

The Node export pipeline is installed once per process:

```ts
import {
  initNodeOpenTelemetryLogging,
} from "@modainteract/moda-interact-shared/logging/node";

initNodeOpenTelemetryLogging({
  serviceName: "moda-interact",
  environment: "test",
});
```

Application modules continue to use:

```ts
import {
  createLogger,
} from "@modainteract/moda-interact-shared/logging";
```

Do **not** import `/logging/node` from Vite/browser/application modules.

If no OTLP logs endpoint is configured, stdout continues and the OTel log
signal is a no-op.

If an active trace/span exists, the OpenTelemetry Logs SDK associates the log
record with the active context. The shared logger does not create traces.

Service-specific tracing and metrics remain in the owning service repository.
