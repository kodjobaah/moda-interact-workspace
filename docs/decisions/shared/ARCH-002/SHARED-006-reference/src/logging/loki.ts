import type { LogRecord } from "./types.js";

export type LokiLogEmitter = (record: LogRecord) => void;

type ModaLoggingGlobal = typeof globalThis & {
  __modaInteractLokiLogEmitterV1?: LokiLogEmitter;
};

function globalState(): ModaLoggingGlobal {
  return globalThis as ModaLoggingGlobal;
}

/**
 * Installs/removes the Node-owned direct Loki emitter.
 *
 * This bridge deliberately contains no Winston, Loki or Node networking
 * imports so it remains safe inside the normal ./logging entry.
 *
 * globalThis is required because tsup emits ./logging and ./logging/node as
 * independent bundles. A module-local variable would not be shared between
 * those package entry points.
 */
export function setLokiLogEmitter(emitter: LokiLogEmitter | null): void {
  try {
    const state = globalState();

    if (emitter) {
      state.__modaInteractLokiLogEmitterV1 = emitter;
    } else {
      delete state.__modaInteractLokiLogEmitterV1;
    }
  } catch {
    // Logging configuration must never become a correctness dependency.
  }
}

/**
 * Sends an already-sanitized canonical Moda log record to the optional Loki
 * emitter installed by ./logging/node.
 */
export function emitLokiLog(record: LogRecord): void {
  try {
    globalState().__modaInteractLokiLogEmitterV1?.(record);
  } catch {
    // Direct Loki delivery is always best-effort.
  }
}
