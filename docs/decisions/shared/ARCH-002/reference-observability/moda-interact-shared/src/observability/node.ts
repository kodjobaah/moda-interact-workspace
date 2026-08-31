import { NodeSDK } from "@opentelemetry/sdk-node";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { OTLPMetricExporter } from "@opentelemetry/exporter-metrics-otlp-http";
import { PeriodicExportingMetricReader } from "@opentelemetry/sdk-metrics";
import {
  AlwaysOffSampler,
  AlwaysOnSampler,
  BatchSpanProcessor,
  ParentBasedSampler,
  TraceIdRatioBasedSampler,
  type Sampler,
} from "@opentelemetry/sdk-trace-base";
import { HttpInstrumentation } from "@opentelemetry/instrumentation-http";
import { UndiciInstrumentation } from "@opentelemetry/instrumentation-undici";
import {
  initNodeLokiLogging,
  initNodeOpenTelemetryLogging,
} from "../../logging/node.js";

const DEFAULT_NAMESPACE = "moda-interact";

type InstrumentProfile = {
  http?: boolean;
  fetch?: boolean;
};

export type NodeObservabilityOptions = {
  serviceName: string;
  environment?: string;
  serviceNamespace?: string;
  instrument?: InstrumentProfile;
  traceSampleRatio?: number;
  forceEnable?: boolean;
};

export type NodeObservabilityRuntime = {
  enabled: boolean;
  serviceName: string;
  environment: string;
  error?: string;
  forceFlush(): Promise<void>;
  shutdown(): Promise<void>;
};

let runtime: NodeObservabilityRuntime | undefined;

export function resolveDeploymentEnvironmentName(): string {
  return nonEmpty(process.env.DEPLOYMENT_ENVIRONMENT_NAME)
    ?? nonEmpty(process.env.OTEL_DEPLOYMENT_ENVIRONMENT)
    ?? nonEmpty(process.env.NODE_ENV)
    ?? "development";
}

export function initNodeObservability(
  options: NodeObservabilityOptions,
): NodeObservabilityRuntime {
  if (runtime) return runtime;

  const serviceName = requireValue(options.serviceName, "serviceName");
  const environment = options.environment ?? resolveDeploymentEnvironmentName();
  const serviceNamespace = options.serviceNamespace ?? DEFAULT_NAMESPACE;

  // Logging destinations are independently best-effort. Existing shared logger
  // continues to write stdout even when both transports are disabled.
  const otelLogs = safeInit(() => initNodeOpenTelemetryLogging({
    serviceName,
    environment,
    serviceNamespace,
  }));
  const loki = safeInit(() => initNodeLokiLogging({
    serviceName,
    environment,
    serviceNamespace,
  }));

  if (!options.forceEnable && envBool("OTEL_SDK_DISABLED") === true) {
    runtime = disabledRuntime(serviceName, environment, otelLogs, loki);
    return runtime;
  }

  const traceEndpoint = signalEndpoint("TRACES", "traces");
  const metricEndpoint = signalEndpoint("METRICS", "metrics");
  if (!options.forceEnable && !traceEndpoint && !metricEndpoint) {
    runtime = disabledRuntime(serviceName, environment, otelLogs, loki);
    return runtime;
  }

  try {
    const resource = resourceFromAttributes({
      "service.namespace": serviceNamespace,
      "service.name": serviceName,
      "deployment.environment.name": environment,
    });

    const interval = positiveInt("OTEL_METRIC_EXPORT_INTERVAL", 60_000);
    const configuredTimeout = positiveInt("OTEL_METRIC_EXPORT_TIMEOUT", 30_000);
    const timeout = Math.min(configuredTimeout, interval);

    const instrumentations = [];
    const profile = options.instrument ?? {};
    if (profile.http) instrumentations.push(new HttpInstrumentation());
    if (profile.fetch) instrumentations.push(new UndiciInstrumentation());

    const traceProcessor = traceEndpoint
      ? new BatchSpanProcessor(new OTLPTraceExporter({ url: traceEndpoint }))
      : undefined;

    const metricReader = metricEndpoint
      ? new PeriodicExportingMetricReader({
          exporter: new OTLPMetricExporter({ url: metricEndpoint }),
          exportIntervalMillis: interval,
          exportTimeoutMillis: timeout,
        })
      : undefined;

    const sdk = new NodeSDK({
      resource,
      sampler: resolveSampler(options.traceSampleRatio, environment),
      // Passing an explicit empty list prevents SDK auto-configuration from
      // creating a default localhost trace exporter when Moda has no endpoint.
      spanProcessors: traceProcessor ? [traceProcessor] : [],
      ...(metricReader ? { metricReader } : {}),
      instrumentations,
    });

    // start() must run before framework modules are imported.
    sdk.start();

    runtime = {
      enabled: true,
      serviceName,
      environment,
      forceFlush: async () => {
        await Promise.allSettled([
          traceProcessor?.forceFlush(),
          metricReader?.forceFlush(),
          otelLogs?.forceFlush?.(),
          loki?.forceFlush?.(),
        ]);
      },
      shutdown: async () => {
        await Promise.allSettled([
          Promise.resolve(sdk.shutdown()),
          otelLogs?.shutdown?.(),
          loki?.shutdown?.(),
        ]);
      },
    };
    return runtime;
  } catch (error) {
    // Observability is never a correctness dependency. Do not throw from app
    // startup solely because SDK/exporter configuration is invalid.
    runtime = {
      ...disabledRuntime(serviceName, environment, otelLogs, loki),
      error: error instanceof Error
        ? error.message.slice(0, 300)
        : "observability-init-failed",
    };
    return runtime;
  }
}

export function getNodeObservabilityRuntime(): NodeObservabilityRuntime | undefined {
  return runtime;
}

function resolveSampler(explicitRatio: number | undefined, environment: string): Sampler {
  if (explicitRatio !== undefined) {
    return new ParentBasedSampler({
      root: new TraceIdRatioBasedSampler(clampRatio(explicitRatio)),
    });
  }

  const requested = nonEmpty(process.env.OTEL_TRACES_SAMPLER)?.toLowerCase();
  if (!requested) {
    return new ParentBasedSampler({
      root: new TraceIdRatioBasedSampler(environment === "test" ? 1 : 0.1),
    });
  }

  switch (requested) {
    case "always_on":
      return new AlwaysOnSampler();
    case "always_off":
      return new AlwaysOffSampler();
    case "traceidratio":
      return new TraceIdRatioBasedSampler(samplerRatioArg(1));
    case "parentbased_always_on":
      return new ParentBasedSampler({ root: new AlwaysOnSampler() });
    case "parentbased_always_off":
      return new ParentBasedSampler({ root: new AlwaysOffSampler() });
    case "parentbased_traceidratio":
      return new ParentBasedSampler({
        root: new TraceIdRatioBasedSampler(samplerRatioArg(1)),
      });
    default:
      // Reference fallback only. Production implementation should emit one
      // bounded configuration warning without throwing from business startup.
      return new ParentBasedSampler({
        root: new TraceIdRatioBasedSampler(environment === "test" ? 1 : 0.1),
      });
  }
}

function samplerRatioArg(fallback: number): number {
  const raw = nonEmpty(process.env.OTEL_TRACES_SAMPLER_ARG);
  if (!raw) return fallback;
  const value = Number(raw);
  return Number.isFinite(value) ? clampRatio(value) : fallback;
}

function disabledRuntime(
  serviceName: string,
  environment: string,
  otelLogs: any,
  loki: any,
): NodeObservabilityRuntime {
  return {
    enabled: false,
    serviceName,
    environment,
    forceFlush: async () => {
      await Promise.allSettled([
        otelLogs?.forceFlush?.(),
        loki?.forceFlush?.(),
      ]);
    },
    shutdown: async () => {
      await Promise.allSettled([
        otelLogs?.shutdown?.(),
        loki?.shutdown?.(),
      ]);
    },
  };
}

function safeInit<T>(fn: () => T): T | undefined {
  try {
    return fn();
  } catch {
    return undefined;
  }
}

function requireValue(value: string, name: string): string {
  const v = value.trim();
  if (!v) throw new Error(`${name} must be non-empty`);
  return v;
}

function nonEmpty(value: string | undefined): string | undefined {
  const v = value?.trim();
  return v ? v : undefined;
}

function envBool(name: string): boolean | undefined {
  const v = nonEmpty(process.env[name])?.toLowerCase();
  if (v === "true" || v === "1") return true;
  if (v === "false" || v === "0") return false;
  return undefined;
}

function envNumber(name: string): number | undefined {
  const raw = nonEmpty(process.env[name]);
  if (!raw) return undefined;
  const value = Number(raw);
  return Number.isFinite(value) ? value : undefined;
}

function positiveInt(name: string, fallback: number): number {
  const value = envNumber(name);
  return value && value > 0 ? Math.floor(value) : fallback;
}

function clampRatio(value: number): number {
  return Math.max(0, Math.min(1, value));
}

function signalEndpoint(signal: "TRACES" | "METRICS", suffix: string): string | undefined {
  const exact = nonEmpty(process.env[`OTEL_EXPORTER_OTLP_${signal}_ENDPOINT`]);
  if (exact) return exact;
  const base = nonEmpty(process.env.OTEL_EXPORTER_OTLP_ENDPOINT)?.replace(/\/+$/, "");
  return base ? `${base}/v1/${suffix}` : undefined;
}
