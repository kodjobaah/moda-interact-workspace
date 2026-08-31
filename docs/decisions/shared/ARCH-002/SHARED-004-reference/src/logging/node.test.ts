import assert from "node:assert/strict";
import http from "node:http";
import test from "node:test";
import { createLogger } from "./logger.js";
import {
  initNodeOpenTelemetryLogging,
  parseOtlpHeaders,
  resolveLogsEndpoint,
} from "./node.js";

test("OTLP log export receives the same safe structured record", async () => {
  const requests: Array<{
    url: string;
    contentType: string;
    body: string;
  }> = [];

  const server = http.createServer((request, response) => {
    const chunks: Buffer[] = [];

    request.on("data", (chunk: Buffer) => {
      chunks.push(chunk);
    });

    request.on("end", () => {
      requests.push({
        url: request.url ?? "",
        contentType: request.headers["content-type"] ?? "",
        body: Buffer.concat(chunks).toString("utf8"),
      });

      response.statusCode = 200;
      response.end();
    });
  });

  await new Promise<void>((resolve) => {
    server.listen(0, "127.0.0.1", resolve);
  });

  const address = server.address();
  assert.ok(address && typeof address === "object");

  const endpoint = `http://127.0.0.1:${address.port}/v1/logs`;

  const runtime = initNodeOpenTelemetryLogging({
    serviceName: "moda-interact",
    environment: "test",
    endpoint,
    forceEnable: true,
  });

  const stdoutRecords: unknown[] = [];

  const logger = createLogger({
    serviceName: "moda-interact",
    environment: "test",
    sink: (record) => stdoutRecords.push(record),
  });

  logger.info("shopify.webhook.outcome", {
    topic: "checkouts/create",
    authorization: "Bearer must-not-leak",
    outcome: "ENQUEUED",
  });

  await runtime.forceFlush();

  assert.equal(stdoutRecords.length, 1);
  assert.equal(requests.length, 1);
  assert.equal(requests[0]?.url, "/v1/logs");
  assert.match(requests[0]?.contentType ?? "", /application\/json/i);
  assert.match(requests[0]?.body ?? "", /shopify\.webhook\.outcome/);
  assert.match(requests[0]?.body ?? "", /ENQUEUED/);
  assert.doesNotMatch(requests[0]?.body ?? "", /must-not-leak/);
  assert.match(requests[0]?.body ?? "", /\[REDACTED\]/);

  await runtime.shutdown();

  await new Promise<void>((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
});

test("generic endpoint appends /v1/logs", () => {
  const previousGeneric = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
  const previousSignal = process.env.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT;

  process.env.OTEL_EXPORTER_OTLP_ENDPOINT = "https://otel.example.test/";
  delete process.env.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT;

  try {
    assert.equal(
      resolveLogsEndpoint(),
      "https://otel.example.test/v1/logs",
    );
  } finally {
    if (previousGeneric === undefined) {
      delete process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
    } else {
      process.env.OTEL_EXPORTER_OTLP_ENDPOINT = previousGeneric;
    }

    if (previousSignal === undefined) {
      delete process.env.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT;
    } else {
      process.env.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT = previousSignal;
    }
  }
});

test("signal-specific endpoint is used exactly", () => {
  const previousGeneric = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
  const previousSignal = process.env.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT;

  process.env.OTEL_EXPORTER_OTLP_ENDPOINT = "https://generic.example.test";
  process.env.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT =
    "https://logs.example.test/custom/v1/logs";

  try {
    assert.equal(
      resolveLogsEndpoint(),
      "https://logs.example.test/custom/v1/logs",
    );
  } finally {
    if (previousGeneric === undefined) {
      delete process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
    } else {
      process.env.OTEL_EXPORTER_OTLP_ENDPOINT = previousGeneric;
    }

    if (previousSignal === undefined) {
      delete process.env.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT;
    } else {
      process.env.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT = previousSignal;
    }
  }
});

test("OTLP header parser supports standard comma separated key=value pairs", () => {
  assert.deepEqual(
    parseOtlpHeaders("Authorization=Bearer%20abc,x-tenant=test"),
    {
      Authorization: "Bearer abc",
      "x-tenant": "test",
    },
  );
});
