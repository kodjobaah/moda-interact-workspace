// Snapshot audit evidence only. These probes execute source with mocked external
// boundaries and assert the observed baseline defects. They are not acceptance
// tests for a future fix, a Shopify SDK integration test, or SQL measurements.
// Usage from workspace root (Node 24): node docs/architecture/reviews/shopify-database-20261103-235702-r01/probe-webhooks.mjs .
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createHash } from "node:crypto";
import { stripTypeScriptTypes } from "node:module";
import assert from "node:assert/strict";

if (!process.argv[2]) throw new Error("Pass the extracted Moda workspace root.");
const workspace = resolve(process.argv[2]);
const sourceSha256 = {};

function readSource(relativePath) {
  const raw = readFileSync(resolve(workspace, relativePath), "utf8");
  sourceSha256[relativePath] = createHash("sha256").update(raw).digest("hex");
  return raw;
}

function executableSource(relativePath, typed = true) {
  const raw = readSource(relativePath);
  const js = typed ? stripTypeScriptTypes(raw) : raw;
  return js
    .replace(/^import\s[\s\S]*?;\s*$/gm, "")
    .replace(/^export\s+(?=(?:class|const|function|async function)\b)/gm, "");
}

async function duplicateUninstallDuringPendingReinstall() {
  const shop = {
    id: "shop-review",
    domain: "review.myshopify.com",
    status: "UNINSTALLED",
    uninstalledAt: new Date("2026-11-03T10:00:00Z"),
    reinstallPendingAt: new Date("2026-11-03T10:10:00Z"),
  };
  const replacementSession = {
    id: "offline_review.myshopify.com",
    shop: shop.domain,
    isOnline: false,
    accessToken: "synthetic-test-token",
  };
  const sessions = [replacementSession];
  const calls = [];
  const database = {
    $transaction: async (fn) => fn(database),
    $queryRaw: async () => {
      calls.push("lifecycle-lock");
      return [{ id: shop.id }];
    },
    shop: {
      findUnique: async () => {
        calls.push("shop.findUnique");
        return { ...shop };
      },
      updateMany: async ({ where, data }) => {
        calls.push("shop.updateMany");
        if (where.uninstalledAt === null && shop.uninstalledAt !== null) {
          return { count: 0 };
        }
        Object.assign(shop, data);
        return { count: 1 };
      },
    },
    shopifyDiscountCatalogue: {
      upsert: async () => { calls.push("catalogue.upsert"); return {}; },
    },
    shopifyDiscount: {
      updateMany: async () => { calls.push("discount.updateMany"); return { count: 0 }; },
    },
    session: {
      deleteMany: async () => {
        calls.push("session.deleteMany");
        const count = sessions.length;
        sessions.length = 0;
        return { count };
      },
      findFirst: async () => sessions.find((session) => !session.isOnline) ?? null,
    },
  };
  const helpers = new Function(
    "Prisma",
    executableSource("moda-interact/app/services/discounts/shopify-discount-lifecycle.service.ts")
      + "\nreturn {lockShopLifecycleRow,markDiscountCatalogueUnavailable};",
  )({ sql: (strings, ...values) => ({ strings, values }) });
  const ShopService = new Function(
    "prisma", "lockShopLifecycleRow", "markDiscountCatalogueUnavailable",
    executableSource("moda-interact/app/services/shop/shop.service.ts") + "\nreturn ShopService;",
  )(database, helpers.lockShopLifecycleRow, helpers.markDiscountCatalogueUnavailable);
  const authenticate = {
    webhook: async () => ({
      shop: shop.domain,
      session: replacementSession,
      topic: "APP_UNINSTALLED",
      eventId: "old-uninstall-event",
      triggeredAt: shop.uninstalledAt.toISOString(),
    }),
  };
  const logs = [];
  const record = (value) => logs.push(value);
  const action = new Function(
    "authenticate", "db", "shopService", "recordShopifyWebhookAuthenticationFailure",
    "recordShopifyWebhookReceived", "recordShopifyWebhookRouteFailure", "recordShopifyWebhookRouteOutcome",
    executableSource("moda-interact/app/routes/webhooks/app/uninstalled/route.jsx", false)
      + "\nreturn action;",
  )(authenticate, database, new ShopService(), record, record, record, record);
  const response = await action({
    request: new Request("https://review.example/webhooks/app/uninstalled", { method: "POST" }),
  });
  assert.equal(response.status, 200);
  assert.equal(shop.reinstallPendingAt.toISOString(), "2026-11-03T10:10:00.000Z");
  assert.equal(sessions.length, 0);
  assert.deepEqual(calls, [
    "shop.findUnique", "lifecycle-lock", "shop.findUnique", "shop.updateMany",
    "catalogue.upsert", "discount.updateMany", "discount.updateMany", "session.deleteMany",
  ]);
  const getToken = new Function(
    "prisma",
    executableSource("moda-interact-background/src/services/shopify-session.service.ts")
      + "\nreturn getShopifyAccessToken;",
  )(database);
  let downstreamError;
  try { await getToken(shop.domain); } catch (error) { downstreamError = error.message; }
  assert.equal(downstreamError, "No offline Shopify session found for review.myshopify.com");
  return {
    probe: "duplicate-uninstall-during-pending-reinstall",
    assertions: "passed: observed baseline defect reproduced",
    responseStatus: response.status,
    reinstallMarkerPreserved: true,
    replacementOfflineSessionDeleted: true,
    explicitRepositoryDatabaseCalls: calls,
    downstreamTokenReadError: downstreamError,
  };
}

async function publicationPreReadHasNoDeadline() {
  let getJobCalls = 0;
  let addCalls = 0;
  let armedTimers = 0;
  class Queue {
    constructor(name) { this.name = name; }
    getJob() { getJobCalls += 1; return new Promise(() => {}); }
    add() { addCalls += 1; return Promise.resolve({ id: "added" }); }
  }
  const contracts = { CHECKOUT_EVENTS: { queueName: "checkout-events", jobName: "checkout-created" } };
  const publish = new Function(
    "Queue", "createBullMQTelemetry", "SHOPIFY_WEBHOOK_QUEUE_CONTRACTS",
    "createShopifyWebhookJobId", "process", "setTimeout",
    executableSource("moda-interact/app/services/webhooks/shopify-webhook-queue.server.ts")
      + "\nreturn publishShopifyCheckoutCreatedEvent;",
  )(
    Queue, () => ({}), contracts, () => "synthetic-legacy-job-id",
    { env: { REDIS_URL: "redis://synthetic-boundary" } },
    () => { armedTimers += 1; return 1; },
  );
  let settled = false;
  // getJob never resolves. No real Redis socket or timer is created by this probe.
  void publish({ event: { tenant: { shopId: "shop-review" }, deliveryId: "delivery-review" } })
    .then(() => { settled = true; }, () => { settled = true; });
  await Promise.resolve();
  await Promise.resolve();
  assert.equal(getJobCalls, 1);
  assert.equal(addCalls, 0);
  assert.equal(armedTimers, 0);
  assert.equal(settled, false);
  return {
    probe: "checkout-publication-pre-read-not-covered-by-timeout",
    assertions: "passed: observed baseline defect reproduced",
    getJobCalls, addCalls, armedTimers, publicationSettled: settled,
  };
}

function namedSubscriptionDeclarationMismatch() {
  const raw = readSource("moda-interact/shopify.app.moda-interact.toml");
  const expected = [
    "app/uninstalled", "customers_whats_app_marketing_consent/update",
    "discounts/create", "discounts/update", "discounts/delete",
    "discounts/redeemcode_added", "discounts/redeemcode_removed",
  ];
  const missing = expected.filter((topic) => !raw.includes(`"${topic}"`));
  const consentDeclarationPass = /uri\s*=\s*"\/webhooks"\s*topics\s*=\s*\[[^\]]*"customers_whats_app_marketing_consent\/update"/s.test(raw);
  assert.equal(consentDeclarationPass, false);
  assert.deepEqual(missing, expected);
  return {
    probe: "named-subscription-declaration-vs-implemented-handlers",
    assertions: "passed: observed baseline mismatch reproduced",
    existingConsentTestEquivalentPassed: consentDeclarationPass,
    missingTopics: missing,
    deployedSubscriptionState: "not inspected; no claim made",
  };
}

const probes = [
  await duplicateUninstallDuringPendingReinstall(),
  await publicationPreReadHasNoDeadline(),
  namedSubscriptionDeclarationMismatch(),
];
console.log(JSON.stringify({
  evidenceType: "source execution with mocked database/auth/queue boundaries plus static declarations",
  limitations: "No PostgreSQL, Redis, Shopify SDK, provider, network, latency, or throughput validation.",
  nodeVersion: process.version,
  probes,
  sourceSha256,
}, null, 2));
