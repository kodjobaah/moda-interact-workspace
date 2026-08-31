import { logs, SeverityNumber } from "@opentelemetry/api-logs";
import type { LogLevel, LogRecord } from "./types.js";

const OTEL_LOGGER_SCOPE_NAME = "@modainteract/moda-interact-shared/logging";

const SEVERITY_BY_LEVEL: Readonly<Record<LogLevel, SeverityNumber>> = Object.freeze({
  debug: SeverityNumber.DEBUG,
  info: SeverityNumber.INFO,
  warn: SeverityNumber.WARN,
  error: SeverityNumber.ERROR,
});

/**
 * Emits the already-sanitized canonical Moda log record through the global
 * OpenTelemetry Logs API.
 *
 * If no LoggerProvider has been installed, the OpenTelemetry Logs API is a
 * no-op. This is intentional: stdout logging remains available in local/test
 * environments without an OTLP backend.
 *
 * The OpenTelemetry SDK automatically associates emitted records with the
 * active Context when a tracing context manager/provider is present. This is
 * how logs become trace/span-correlated without the shared logger depending on
 * a service-specific tracing SDK.
 */
export function emitOpenTelemetryLog(record: LogRecord): void {
  try {
    const logger = logs.getLogger(OTEL_LOGGER_SCOPE_NAME);

    logger.emit({
      eventName: record.event,
      timestamp: new Date(record.timestamp),
      severityNumber: SEVERITY_BY_LEVEL[record.level],
      severityText: record.level.toUpperCase(),
      // Keep the OTLP body identical to the structured stdout record.
      body: JSON.stringify(record),
      attributes: {
        "event.name": record.event,
        "log.level": record.level,
        "service.namespace": record["service.namespace"],
        "service.name": record["service.name"],
        "deployment.environment.name":
          record["deployment.environment.name"],
      },
    });
  } catch {
    // OpenTelemetry is best-effort. It must never change business correctness.
  }
}
