import {
  createLogger as createWinstonLogger,
  format,
  type Logger as WinstonLogger,
} from "winston";
import LokiTransport from "winston-loki";
import { setLokiLogEmitter } from "../loki.js";
import type { LogRecord } from "../types.js";

const DEFAULT_SERVICE_NAMESPACE = "moda-interact";

export type NodeLokiLoggingOptions = {
  serviceName: string;
  environment: string;
  serviceNamespace?: string;

  /**
   * Explicit Loki base URL.
   *
   * Production normally supplies LOKI_URL.
   */
  host?: string;

  /**
   * Optional Basic Auth override in `username:password` format.
   *
   * Prefer separate LOKI_USERNAME/LOKI_PASSWORD environment variables in
   * deployed services so the composed value never needs to be committed.
   */
  basicAuth?: string;

  /**
   * Optional additional static headers.
   *
   * Never include these in log payloads or error messages.
   */
  headers?: Record<string, string>;

  batching?: boolean;
  intervalSeconds?: number;
  timeoutMs?: number;
  clearOnError?: boolean;

  /**
   * Test-only override. In normal service bootstrap, the presence of a Loki
   * host is sufficient to enable the transport.
   */
  forceEnable?: boolean;
};

export type NodeLokiLoggingRuntime = {
  enabled: boolean;
  host: string | null;
  labels: Readonly<Record<string, string>>;
  forceFlush: () => Promise<void>;
  shutdown: () => Promise<void>;
};

let runtime: NodeLokiLoggingRuntime | null = null;

function requireNonEmpty(value: string, field: string): string {
  const normalized = value.trim();
  if (!normalized) {
    throw new Error(`${field} must be a non-empty string`);
  }
  return normalized;
}

/**
 * Installs the direct Grafana Loki destination exactly once per Node process.
 *
 * IMPORTANT:
 * - This module is Node-only.
 * - It is reached through @modainteract/moda-interact-shared/logging/node.
 * - Do not import it from Vite/browser/application module graphs.
 * - The normal ./logging entry contains no Winston/winston-loki imports.
 */
export function initNodeLokiLogging(
  options: NodeLokiLoggingOptions,
): NodeLokiLoggingRuntime {
  if (runtime) {
    return runtime;
  }

  const serviceName = requireNonEmpty(options.serviceName, "serviceName");
  const environment = requireNonEmpty(options.environment, "environment");
  const serviceNamespace = requireNonEmpty(
    options.serviceNamespace ?? DEFAULT_SERVICE_NAMESPACE,
    "serviceNamespace",
  );

  const host = nonEmpty(options.host) ?? envString("LOKI_URL");
  const enabled =
    options.forceEnable === true ||
    (envBool("LOKI_ENABLED") !== false && host !== undefined);

  const labels = Object.freeze({
    service_namespace: serviceNamespace,
    service_name: serviceName,
    environment,
  });

  if (!enabled || !host) {
    setLokiLogEmitter(null);

    runtime = {
      enabled: false,
      host: null,
      labels,
      forceFlush: async () => {},
      shutdown: async () => {},
    };

    return runtime;
  }

  const basicAuth =
    nonEmpty(options.basicAuth) ??
    buildBasicAuth(
      envString("LOKI_USERNAME"),
      envString("LOKI_PASSWORD"),
    );

  const transport = new LokiTransport({
    host,
    json: true,
    batching: options.batching ?? envBool("LOKI_BATCHING") ?? true,
    interval:
      options.intervalSeconds ??
      envInt("LOKI_BATCH_INTERVAL_SECONDS", 5),
    timeout:
      options.timeoutMs ??
      envInt("LOKI_TIMEOUT_MS", 10_000),

    // Prefer bounded loss to unbounded memory growth when the logging backend
    // is unavailable. Loki must never become an application dependency.
    clearOnError:
      options.clearOnError ??
      envBool("LOKI_CLEAR_ON_ERROR") ??
      true,

    // Current winston-loki guidance recommends keeping timestamp replacement
    // enabled unless there is a specific reason not to.
    replaceTimestamp: true,

    // Moda owns flush/shutdown explicitly from the process bootstrap.
    gracefulShutdown: false,

    // Critical cardinality rule: only these architecture-approved static
    // labels may be indexed. Never promote Winston meta/data to labels.
    labels,
    useWinstonMetaAsLabels: false,

    ...(basicAuth ? { basicAuth } : {}),
    ...(options.headers ? { headers: options.headers } : {}),

    // Do not recursively log Loki connection errors through the shared logger.
    // Doing so could create a failure loop while Loki is unavailable.
    onConnectionError: () => {},
  });

  const lokiLogger = createWinstonLogger({
    level: "debug",
    format: format.json(),
    transports: [transport],
    exitOnError: false,
  });

  setLokiLogEmitter((record) => {
    writeCanonicalRecord(lokiLogger, record);
  });

  runtime = {
    enabled: true,
    host,
    labels,
    forceFlush: async () => {
      await safeFlush(transport);
    },
    shutdown: async () => {
      setLokiLogEmitter(null);
      await safeFlush(transport);
      await safeCloseTransport(transport);

      try {
        lokiLogger.close();
      } catch {
        // best-effort
      }
    },
  };

  return runtime;
}

export function getNodeLokiLoggingRuntime():
  | NodeLokiLoggingRuntime
  | null {
  return runtime;
}

function writeCanonicalRecord(
  logger: WinstonLogger,
  record: LogRecord,
): void {
  try {
    // Winston requires a `message`; use the canonical event name.
    //
    // Every other value comes from the already-sanitized immutable Moda
    // LogRecord. Because useWinstonMetaAsLabels=false, these values remain in
    // the JSON log line rather than becoming Loki stream labels.
    logger.log({
      ...record,
      level: record.level,
      message: record.event,
    });
  } catch {
    // Direct Loki emission must never escape to business code.
  }
}

async function safeFlush(transport: LokiTransport): Promise<void> {
  try {
    await transport.flush();
  } catch {
    // Logs may be dropped. Business processing must continue.
  }
}

async function safeCloseTransport(
  transport: LokiTransport,
): Promise<void> {
  try {
    const closeable = transport as LokiTransport & {
      close?: () => unknown | Promise<unknown>;
    };

    if (typeof closeable.close === "function") {
      await Promise.resolve(closeable.close());
    }
  } catch {
    // best-effort shutdown
  }
}

function buildBasicAuth(
  username: string | undefined,
  password: string | undefined,
): string | undefined {
  if (!username || !password) {
    return undefined;
  }

  return `${username}:${password}`;
}

function envString(name: string): string | undefined {
  return nonEmpty(process.env[name]);
}

function nonEmpty(value: string | undefined): string | undefined {
  if (value === undefined) {
    return undefined;
  }

  const normalized = value.trim();
  return normalized.length > 0 ? normalized : undefined;
}

function envBool(name: string): boolean | undefined {
  const value = envString(name);

  if (value === undefined) {
    return undefined;
  }

  const normalized = value.toLowerCase();

  if (["1", "true", "yes", "on"].includes(normalized)) {
    return true;
  }

  if (["0", "false", "no", "off"].includes(normalized)) {
    return false;
  }

  return undefined;
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
