import { createBullMQTelemetry } from "@modainteract/moda-interact-shared/observability/bullmq";

const telemetry = createBullMQTelemetry({
  serviceName: process.env.OTEL_SERVICE_NAME ?? "moda-messaging-worker",
  enableMetrics: true,
});

// Pass `telemetry` to every Queue/Worker created by this process.
// new Worker(name, processor, { connection, telemetry, concurrency });
