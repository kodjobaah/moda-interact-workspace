import { BullMQOtel } from "bullmq-otel";

export type BullMQTelemetryOptions = {
  serviceName: string;
  version?: string;
  enableMetrics?: boolean;
};

export function createBullMQTelemetry(options: BullMQTelemetryOptions) {
  return new BullMQOtel({
    tracerName: options.serviceName,
    meterName: options.serviceName,
    version: options.version ?? "unknown",
    enableMetrics: options.enableMetrics ?? true,
  });
}
