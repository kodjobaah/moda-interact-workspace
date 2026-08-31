export const LOG_LEVELS = ["debug", "info", "warn", "error"] as const;

export type LogLevel = (typeof LOG_LEVELS)[number];

export type LogFields = Readonly<Record<string, unknown>>;

export type LogRecord = Readonly<{
  timestamp: string;
  level: LogLevel;
  event: string;
  "service.namespace": string;
  "service.name": string;
  "deployment.environment.name": string;
  data?: Readonly<Record<string, unknown>>;
}>;

export type LogSink = (record: LogRecord) => void;

export type LoggerOptions = {
  serviceName: string;
  environment: string;
  serviceNamespace?: string;
  baseFields?: LogFields;
  sink?: LogSink;
  now?: () => Date;
};

export interface StructuredLogger {
  debug(event: string, fields?: LogFields): void;
  info(event: string, fields?: LogFields): void;
  warn(event: string, fields?: LogFields): void;
  error(event: string, fields?: LogFields): void;
  child(fields: LogFields): StructuredLogger;
}
