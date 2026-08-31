export const REDACTED = "[REDACTED]";
export const CIRCULAR = "[Circular]";
export const MAX_DEPTH_REACHED = "[MaxDepth]";
export const TRUNCATED = "[Truncated]";

export const LOG_VALUE_LIMITS = Object.freeze({
  maxDepth: 6,
  maxArrayItems: 50,
  maxObjectKeys: 100,
  maxStringLength: 4096,
});

const SENSITIVE_EXACT_KEYS = new Set([
  "authorization",
  "cookie",
  "setcookie",
  "password",
  "passwd",
  "apikey",
  "privatekey",
  "cvv",
  "cvc",
  "cardnumber",
  "creditcard",
  "firstname",
  "lastname",
]);

function normalizeKey(key: string): string {
  return key.toLowerCase().replace(/[^a-z0-9]/g, "");
}

export function isSensitiveLogKey(key: string): boolean {
  const normalized = normalizeKey(key);

  return (
    SENSITIVE_EXACT_KEYS.has(normalized) ||
    normalized.includes("secret") ||
    normalized.endsWith("token") ||
    normalized.includes("email") ||
    normalized.includes("phone") ||
    normalized.endsWith("address")
  );
}

function sanitizeString(value: string): string {
  const scrubbed = value
    .replace(/\bBearer\s+[^\s,;]+/gi, `Bearer ${REDACTED}`)
    .replace(
      /([?&](?:access_token|refresh_token|verify_token|client_secret|api_key|token|password)=)[^&#\s]*/gi,
      `$1${REDACTED}`,
    );

  if (scrubbed.length <= LOG_VALUE_LIMITS.maxStringLength) {
    return scrubbed;
  }

  return `${scrubbed.slice(0, LOG_VALUE_LIMITS.maxStringLength)}…${TRUNCATED}`;
}

function sanitizeError(error: Error): Record<string, unknown> {
  return {
    name: sanitizeString(error.name),
    message: sanitizeString(error.message),
  };
}

function sanitizeValue(
  value: unknown,
  depth: number,
  activeObjects: WeakSet<object>,
): unknown {
  if (value === null || value === undefined) {
    return value ?? null;
  }

  if (typeof value === "string") {
    return sanitizeString(value);
  }

  if (typeof value === "number") {
    return Number.isFinite(value) ? value : String(value);
  }

  if (typeof value === "boolean") {
    return value;
  }

  if (typeof value === "bigint") {
    return value.toString();
  }

  if (typeof value === "symbol" || typeof value === "function") {
    return `[${typeof value}]`;
  }

  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? "Invalid Date" : value.toISOString();
  }

  if (value instanceof Error) {
    return sanitizeError(value);
  }

  if (depth >= LOG_VALUE_LIMITS.maxDepth) {
    return MAX_DEPTH_REACHED;
  }

  if (typeof value !== "object") {
    return String(value);
  }

  if (activeObjects.has(value)) {
    return CIRCULAR;
  }

  activeObjects.add(value);

  try {
    if (Array.isArray(value)) {
      const result = value
        .slice(0, LOG_VALUE_LIMITS.maxArrayItems)
        .map((item) => sanitizeValue(item, depth + 1, activeObjects));

      if (value.length > LOG_VALUE_LIMITS.maxArrayItems) {
        result.push(TRUNCATED);
      }

      return result;
    }

    const result: Record<string, unknown> = {};
    const entries = Object.entries(value).slice(0, LOG_VALUE_LIMITS.maxObjectKeys);

    for (const [key, item] of entries) {
      result[key] = isSensitiveLogKey(key)
        ? REDACTED
        : sanitizeValue(item, depth + 1, activeObjects);
    }

    if (Object.keys(value).length > LOG_VALUE_LIMITS.maxObjectKeys) {
      result.__truncated__ = true;
    }

    return result;
  } finally {
    activeObjects.delete(value);
  }
}

export function sanitizeLogFields(
  fields: Readonly<Record<string, unknown>>,
): Record<string, unknown> {
  return sanitizeValue(fields, 0, new WeakSet<object>()) as Record<string, unknown>;
}
