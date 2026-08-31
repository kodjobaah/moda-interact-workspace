import { emitLokiLog } from "./loki.js";
import { emitOpenTelemetryLog } from "./otel.js";
import { sanitizeLogFields } from "./redaction.js";
import type {
  LogFields,
  LogLevel,
  LogRecord,
  LogSink,
  LoggerOptions,
  StructuredLogger,
} from "./types.js";

const DEFAULT_SERVICE_NAMESPACE = "moda-interact";

function requireNonEmpty(value: string, field: string): string {
  const normalized = value.trim();
  if (!normalized) {
    throw new Error(`${field} must be a non-empty string`);
  }
  return normalized;
}

function defaultSink(record: LogRecord): void {
  const line = JSON.stringify(record);

  switch (record.level) {
    case "debug":
      console.debug(line);
      break;
    case "warn":
      console.warn(line);
      break;
    case "error":
      console.error(line);
      break;
    case "info":
    default:
      console.info(line);
      break;
  }
}

function safeTimestamp(now: () => Date): string {
  try {
    const value = now();
    if (value instanceof Date && !Number.isNaN(value.getTime())) {
      return value.toISOString();
    }
  } catch {
    // Logging must not become a correctness dependency.
  }

  return new Date().toISOString();
}

export function createLogger(options: LoggerOptions): StructuredLogger {
  const serviceName = requireNonEmpty(options.serviceName, "serviceName");
  const environment = requireNonEmpty(options.environment, "environment");
  const serviceNamespace = requireNonEmpty(
    options.serviceNamespace ?? DEFAULT_SERVICE_NAMESPACE,
    "serviceNamespace",
  );
  const sink: LogSink = options.sink ?? defaultSink;
  const now = options.now ?? (() => new Date());
  const initialBaseFields = { ...(options.baseFields ?? {}) };

  function buildLogger(baseFields: Record<string, unknown>): StructuredLogger {
    function emit(level: LogLevel, event: string, fields: LogFields = {}): void {
      let record: LogRecord;

      try {
        const eventName = event.trim() || "unknown";
        const sanitizedData = sanitizeLogFields({ ...baseFields, ...fields });

        record = Object.freeze({
          timestamp: safeTimestamp(now),
          level,
          event: eventName,
          "service.namespace": serviceNamespace,
          "service.name": serviceName,
          "deployment.environment.name": environment,
          ...(Object.keys(sanitizedData).length > 0
            ? { data: sanitizedData }
            : {}),
        });
      } catch {
        // Sanitization/record construction must never affect business logic.
        return;
      }

      // Each destination is deliberately isolated. Failure of one destination
      // must not suppress another destination and must never escape to business
      // code.
      try {
        sink(record);
      } catch {
        // best-effort stdout/custom sink
      }

      emitOpenTelemetryLog(record);
      emitLokiLog(record);
    }

    return Object.freeze({
      debug: (event: string, fields?: LogFields) => emit("debug", event, fields),
      info: (event: string, fields?: LogFields) => emit("info", event, fields),
      warn: (event: string, fields?: LogFields) => emit("warn", event, fields),
      error: (event: string, fields?: LogFields) => emit("error", event, fields),
      child: (fields: LogFields) => buildLogger({ ...baseFields, ...fields }),
    });
  }

  return buildLogger(initialBaseFields);
}
