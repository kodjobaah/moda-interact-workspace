import { createBullMQTelemetry } from "@modainteract/moda-interact-shared/observability/bullmq";

export const bullmqTelemetry = createBullMQTelemetry({
  serviceName: "moda-interact-messaging",
  enableMetrics: true,
});
// Pass this into the inbound Queue options so the HTTP trace propagates to the worker.
