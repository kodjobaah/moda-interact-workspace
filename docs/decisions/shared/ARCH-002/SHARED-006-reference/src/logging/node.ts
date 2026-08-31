import { logs } from "@opentelemetry/api-logs";
import { OTLPLogExporter } from "@opentelemetry/exporter-logs-otlp-http";
import { resourceFromAttributes } from "@opentelemetry/resources";
import {
  BatchLogRecordProcessor,
  LoggerProvider,
} from "@opentelemetry/sdk-logs";

export {
  getNodeLokiLoggingRuntime,
  initNodeLokiLogging,
} from "./node/loki.js";
export type {
  NodeLokiLoggingOptions,
  NodeLokiLoggingRuntime,
} from "./node/loki.js";

const DEFAULT_SERVICE_NAMESPACE = "moda-interact";

export type NodeOpenTelemetryLoggingOptions = {
  serviceName: string;
  environment: string;
  serviceNamespace?: string;

  /**
   * Explicit endpoint override. Intended mainly for tests.
   *
   * Production normally uses:
   *   OTEL_EXPORTER_OTLP_LOGS_ENDPOINT
   * or:
   *   OTEL_EXPORTER_OTLP_ENDPOINT
   */
  endpoint?: string;

  /** Optional explicit OTLP headers override. */
  headers?: Record<string, string>;

  /** Test-only switch. Production should rely on environment configuration. */
  forceEnable?: boolean;
};

export type NodeOpenTelemetryLoggingRuntime = {
  enabled: boolean;
  endpoint: string | null;
  forceFlush: () => Promise<void>;
  shutdown: () => Promise<void>;
};

let runtime: NodeOpenTelemetryLoggingRuntime | null = null;

function requireNonEmpty(value: string, field: string): string {
  const normalized = value.trim();
  if (!normalized) {
    throw new Error(`${field} must be a non-empty string`);
  }
  return normalized;
}

/**
 * Installs the Node OpenTelemetry LoggerProvider exactly once for this process.
 *
 * IMPORTANT:
 * This module is Node-only. Import and initialize it from the process bootstrap
 * before framework/application modules are loaded. Do not import this module
 * through Vite/React/browser bundles.
 *
 * Application modules should import only:
 *
 *   @modainteract/moda-interact-shared/logging
 *
 * Once this provider is installed, createLogger(...) automatically fans safe
 * canonical log records out to stdout and the OpenTelemetry Logs API.
 *
 * Direct Loki delivery, when desired, is independently enabled with:
 *
 *   initNodeLokiLogging(...)
 *
 * from this same Node-only package entry.
 */
export function initNodeOpenTelemetryLogging(
  options: NodeOpenTelemetryLoggingOptions,
): NodeOpenTelemetryLoggingRuntime {
  if (runtime) {
    return runtime;
  }

  const serviceName = requireNonEmpty(options.serviceName, "serviceName");
  const environment = requireNonEmpty(options.environment, "environment");
  const serviceNamespace = requireNonEmpty(
    options.serviceNamespace ?? DEFAULT_SERVICE_NAMESPACE,
    "serviceNamespace",
  );

  const config = resolveLogsConfig(options);

  if (!config.enabled || !config.endpoint) {
    runtime = {
      enabled: false,
      endpoint: null,
      forceFlush: async () => {},
      shutdown: async () => {},
    };
    return runtime;
  }

  const exporter = new OTLPLogExporter({
    url: config.endpoint,
    headers: config.headers,
    concurrencyLimit: envInt("OTEL_LOG_EXPORT_CONCURRENCY_LIMIT", 2),
  });

  const processor = new BatchLogRecordProcessor({
    exporter,
    maxQueueSize: envInt("OTEL_BLRP_MAX_QUEUE_SIZE", 2048),
    maxExportBatchSize: envInt("OTEL_BLRP_MAX_EXPORT_BATCH_SIZE", 512),
    scheduledDelayMillis: envInt("OTEL_BLRP_SCHEDULE_DELAY", 1_000),
    exportTimeoutMillis: envInt("OTEL_BLRP_EXPORT_TIMEOUT", 30_000),
  });

  const provider = new LoggerProvider({
    resource: resourceFromAttributes({
      "service.namespace": serviceNamespace,
      "service.name": serviceName,
      "deployment.environment.name": environment,
    }),
    processors: [processor],
    logRecordLimits: {
      attributeCountLimit: 64,
      attributeValueLengthLimit: 4096,
    },
  });

  logs.setGlobalLoggerProvider(provider);

  runtime = {
    enabled: true,
    endpoint: config.endpoint,
    forceFlush: async () => {
      try {
        await provider.forceFlush();
      } catch {
        // Telemetry delivery is best-effort.
      }
    },
    shutdown: async () => {
      try {
        await provider.shutdown();
      } catch {
        // Telemetry shutdown is best-effort.
      }
    },
  };

  return runtime;
}

export function getNodeOpenTelemetryLoggingRuntime():
  | NodeOpenTelemetryLoggingRuntime
  | null {
  return runtime;
}

export function resolveLogsEndpoint(
  explicitEndpoint?: string,
): string | undefined {
  const explicit = nonEmpty(explicitEndpoint);
  if (explicit) {
    return explicit;
  }

  const signalEndpoint = envString("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT");
  if (signalEndpoint) {
    return signalEndpoint;
  }

  const genericEndpoint = envString("OTEL_EXPORTER_OTLP_ENDPOINT");
  if (!genericEndpoint) {
    return undefined;
  }

  const normalized = genericEndpoint.replace(/\/+$/, "");
  if (normalized.endsWith("/v1/logs")) {
    return normalized;
  }
  return `${normalized}/v1/logs`;
}

export function parseOtlpHeaders(value: string | undefined):
  | Record<string, string>
  | undefined {
  const raw = nonEmpty(value);
  if (!raw) {
    return undefined;
  }

  const headers: Record<string, string> = {};

  for (const part of raw.split(",")) {
    const separator = part.indexOf("=");
    if (separator <= 0) {
      continue;
    }

    const rawKey = part.slice(0, separator).trim();
    const rawValue = part.slice(separator + 1).trim();

    if (!rawKey) {
      continue;
    }

    headers[safeDecodeURIComponent(rawKey)] =
      safeDecodeURIComponent(rawValue);
  }

  return Object.keys(headers).length > 0 ? headers : undefined;
}

function resolveLogsConfig(options: NodeOpenTelemetryLoggingOptions) {
  if (!options.forceEnable && envBool("OTEL_SDK_DISABLED") === true) {
    return {
      enabled: false,
      endpoint: undefined,
      headers: undefined,
    };
  }

  const exporterName = envString("OTEL_LOGS_EXPORTER") ?? "otlp";

  if (!options.forceEnable && exporterName !== "otlp") {
    return {
      enabled: false,
      endpoint: undefined,
      headers: undefined,
    };
  }

  const endpoint = resolveLogsEndpoint(options.endpoint);

  if (!endpoint) {
    return {
      enabled: false,
      endpoint: undefined,
      headers: undefined,
    };
  }

  const headers =
    options.headers ??
    parseOtlpHeaders(
      envString("OTEL_EXPORTER_OTLP_LOGS_HEADERS") ??
        envString("OTEL_EXPORTER_OTLP_HEADERS"),
    );

  return {
    enabled: true,
    endpoint,
    headers,
  };
}

function envString(name: string): string | undefined {
  return nonEmpty(process.env[name]);
}

function nonEmpty(value: string | undefined): string | undefined {
  if (value === undefined) {
    return undefined;
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

function envBool(name: string): boolean | undefined {
  const value = envString(name);
  if (value === undefined) {
    return undefined;
  }
  return ["1", "true", "yes", "on"].includes(value.toLowerCase());
}

function envInt(name: string, fallback: number): number {
  const value = envString(name);
  if (value === undefined) {
    return fallback;
  }

  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0
    ? Math.floor(parsed)
    : fallback;
}

function safeDecodeURIComponent(value: string): string {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}
