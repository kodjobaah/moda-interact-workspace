import assert from "node:assert/strict";
import test from "node:test";
import { createLogger } from "./logger.js";
import { REDACTED } from "./redaction.js";
import type { LogRecord } from "./types.js";

test("emits canonical structured record", () => {
  const records: LogRecord[] = [];
  const logger = createLogger({
    serviceName: "moda-interact",
    environment: "test",
    now: () => new Date("2026-08-30T12:00:00.000Z"),
    sink: (record) => records.push(record),
  });

  logger.info("shopify.webhook.accepted", {
    topic: "checkouts/create",
    ackMs: 12,
  });

  assert.deepEqual(records, [
    {
      timestamp: "2026-08-30T12:00:00.000Z",
      level: "info",
      event: "shopify.webhook.accepted",
      "service.namespace": "moda-interact",
      "service.name": "moda-interact",
      "deployment.environment.name": "test",
      data: { topic: "checkouts/create", ackMs: 12 },
    },
  ]);
});

test("recursively redacts sensitive keys and bearer/query tokens", () => {
  const records: LogRecord[] = [];
  const logger = createLogger({
    serviceName: "moda-interact-messaging",
    environment: "production",
    sink: (record) => records.push(record),
  });

  logger.info("meta.webhook", {
    authorization: "Bearer top-secret",
    nested: {
      accessToken: "abc",
      email: "person@example.com",
      url: "https://example.test/cb?verify_token=xyz&safe=yes",
    },
  });

  assert.equal(records[0]?.data?.authorization, REDACTED);
  assert.deepEqual(records[0]?.data?.nested, {
    accessToken: REDACTED,
    email: REDACTED,
    url: `https://example.test/cb?verify_token=${REDACTED}&safe=yes`,
  });
});

test("serializes Error safely without stack", () => {
  const records: LogRecord[] = [];
  const logger = createLogger({
    serviceName: "moda-recovery-worker",
    environment: "test",
    sink: (record) => records.push(record),
  });

  logger.error("recovery.failed", {
    error: new Error("Bearer secret-value failed"),
  });

  assert.deepEqual(records[0]?.data?.error, {
    name: "Error",
    message: `Bearer ${REDACTED} failed`,
  });
});

test("child logger merges stable base context", () => {
  const records: LogRecord[] = [];
  const logger = createLogger({
    serviceName: "moda-shopify-event-worker",
    environment: "test",
    baseFields: { queue: "shopify" },
    sink: (record) => records.push(record),
  }).child({ worker: "checkout" });

  logger.info("job.completed", { jobId: "job-1" });

  assert.deepEqual(records[0]?.data, {
    queue: "shopify",
    worker: "checkout",
    jobId: "job-1",
  });
});

test("sink failure never escapes to caller", () => {
  const logger = createLogger({
    serviceName: "moda-interact",
    environment: "test",
    sink: () => {
      throw new Error("sink unavailable");
    },
  });

  assert.doesNotThrow(() =>
    logger.error("log.sink.failure", { safe: true }),
  );
});

test("handles circular structures without throwing", () => {
  const records: LogRecord[] = [];
  const circular: Record<string, unknown> = { name: "root" };
  circular.self = circular;

  const logger = createLogger({
    serviceName: "moda-interact",
    environment: "test",
    sink: (record) => records.push(record),
  });

  logger.info("circular.test", { circular });

  assert.deepEqual(records[0]?.data?.circular, {
    name: "root",
    self: "[Circular]",
  });
});
