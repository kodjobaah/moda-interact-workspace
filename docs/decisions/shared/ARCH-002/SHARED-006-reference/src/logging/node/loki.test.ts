import assert from "node:assert/strict";
import http from "node:http";
import test from "node:test";
import { createLogger } from "../logger.js";
import { initNodeLokiLogging } from "./loki.js";

test("direct Loki transport receives sanitized structured JSON with bounded labels", async () => {
  let received:
    | {
        url: string;
        contentType: string;
        body: string;
      }
    | undefined;

  let resolveRequest!: () => void;
  const requestReceived = new Promise<void>((resolve) => {
    resolveRequest = resolve;
  });

  const server = http.createServer((request, response) => {
    const chunks: Buffer[] = [];

    request.on("data", (chunk: Buffer) => {
      chunks.push(chunk);
    });

    request.on("end", () => {
      received = {
        url: request.url ?? "",
        contentType: request.headers["content-type"] ?? "",
        body: Buffer.concat(chunks).toString("utf8"),
      };

      response.statusCode = 204;
      response.end();
      resolveRequest();
    });
  });

  await new Promise<void>((resolve) => {
    server.listen(0, "127.0.0.1", resolve);
  });

  const address = server.address();
  assert.ok(address && typeof address === "object");

  const host = `http://127.0.0.1:${address.port}`;

  const loki = initNodeLokiLogging({
    serviceName: "moda-interact",
    environment: "test",
    host,
    batching: false,
    timeoutMs: 1_000,
    forceEnable: true,
  });

  const stdout: unknown[] = [];

  const logger = createLogger({
    serviceName: "moda-interact",
    environment: "test",
    sink: (record) => stdout.push(record),
  });

  logger.info("shopify.webhook.outcome", {
    topic: "checkouts/create",
    outcome: "ENQUEUED",
    authorization: "Bearer must-not-leak",
    recoveryId: "safe-high-cardinality-body-value",
  });

  await Promise.race([
    requestReceived,
    new Promise<never>((_, reject) => {
      setTimeout(
        () => reject(new Error("Timed out waiting for Loki push request")),
        2_000,
      );
    }),
  ]);

  assert.equal(stdout.length, 1);
  assert.ok(received);
  assert.equal(received.url, "/loki/api/v1/push");
  assert.match(received.contentType, /application\/json/i);

  // Canonical static labels are present.
  assert.match(received.body, /service_namespace/);
  assert.match(received.body, /moda-interact/);
  assert.match(received.body, /service_name/);
  assert.match(received.body, /environment/);
  assert.match(received.body, /test/);

  // The structured log content is present.
  assert.match(received.body, /shopify\.webhook\.outcome/);
  assert.match(received.body, /ENQUEUED/);

  // Sensitive data was removed before it reached the transport.
  assert.doesNotMatch(received.body, /must-not-leak/);
  assert.match(received.body, /\[REDACTED\]/);

  // High-cardinality operational identifiers may remain in the safe JSON body
  // but must not be promoted to architecture labels.
  assert.match(received.body, /safe-high-cardinality-body-value/);
  assert.doesNotMatch(received.body, /"recoveryId"\s*:\s*"safe-high-cardinality-body-value"\s*,?\s*"[^"]*"\s*:/);

  await loki.shutdown();

  await new Promise<void>((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
});
