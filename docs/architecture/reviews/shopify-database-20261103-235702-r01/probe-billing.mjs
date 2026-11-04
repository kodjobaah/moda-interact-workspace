import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { stripTypeScriptTypes } from "node:module";
import path from "node:path";
import vm from "node:vm";

// Scratch source-execution probe. All persistence/provider ports are mocks.
assert.ok(process.argv[2], "Usage from workspace root: node --experimental-vm-modules docs/architecture/reviews/shopify-database-20261103-235702-r01/probe-billing.mjs .");
const root = path.resolve(process.argv[2], "moda-interact") + path.sep;
const sources = {
  provider: "app/services/billing/providers/shopify-billing.provider.ts",
  management: "app/services/billing/recovery-credit-purchase-management.service.ts",
};
let operations = [];
let transactionOpen = false;
let providerBody;
const context = vm.createContext({
  Date, Error, Math, Number, Object, Promise, Set, String, JSON,
  fetch: async () => {
    operations.push({ name: "provider.fetch", transactionOpen });
    return { ok: true, status: 200, json: async () => providerBody };
  },
});
const enumOf = (...values) => Object.fromEntries(values.map(value => [value, value]));
class KnownRequestError extends Error { constructor(message, options) { super(message); this.code = options.code; } }
function synthetic(id, exports) {
  return new vm.SyntheticModule(Object.keys(exports), function () {
    for (const [key, value] of Object.entries(exports)) this.setExport(key, value);
  }, { context, identifier: id });
}
const credentials = {
  requireShopifyPartnerCredentials: async () => {
    operations.push({ name: "credentials.read", transactionOpen });
    return { organizationId: "fixture-org", appId: "fixture-app", accessToken: "fixture-token" };
  },
};
const dependency = new Map([
  ["@prisma/client", synthetic("prisma", {
    EntitlementCounter: enumOf("PURCHASED_RECOVERY_CREDITS"),
    Prisma: { TransactionIsolationLevel: { Serializable: "Serializable" }, PrismaClientKnownRequestError: KnownRequestError },
    RecoveryCreditPurchaseStatus: enumOf("ACTIVE", "WITHDRAWN", "COMPLETED", "REFUNDED"),
    RecoveryCreditRefundStatus: enumOf("REQUESTED", "PROVIDER_ACTION_REQUIRED", "NEEDS_ATTENTION", "COMPLETED", "CANCELLED"),
  })],
  ["@modainteract/moda-interact-shared/billing", synthetic("shared", {
    deriveShopifyProviderContextIdentity: ({ providerSubscriptionId }) => `fixture-context:${providerSubscriptionId}`,
  })],
  ["../../db.server", synthetic("db", { default: {} })],
  ["../../platform-configuration/composition.server", synthetic("configuration", {
    createDefaultShopifyPlatformConfigurationService: () => credentials,
  })],
]);
const fingerprints = {};
async function readSource(key) {
  const source = await readFile(root + sources[key], "utf8");
  fingerprints[sources[key]] = createHash("sha256").update(source).digest("hex");
  return new vm.SourceTextModule(stripTypeScriptTypes(source, { mode: "transform" }), {
    context, identifier: root + sources[key],
  });
}
async function link(module) {
  await module.link(specifier => {
    const found = dependency.get(specifier);
    if (!found) throw new Error(`Unmocked dependency: ${specifier}`);
    return found;
  });
  await module.evaluate();
}
const providerModule = await readSource("provider");
await link(providerModule);
dependency.set("./providers/shopify-billing.provider", providerModule);
const managementModule = await readSource("management");
await link(managementModule);
const Provider = providerModule.namespace.ShopifyBillingProvider;
const Management = managementModule.namespace.RecoveryCreditPurchaseManagementService;
const start = new Date("2026-11-01T00:00:00.000Z");
const end = new Date("2026-12-01T00:00:00.000Z");
const providerSnapshot = {
  data: { activeSubscription: {
    billingPeriod: "EVERY_30_DAYS", cancelAtEndOfCycle: false, trialEndsAt: null,
    currentBillingCycle: { startTime: start.toISOString(), endTime: end.toISOString() },
    items: [
      { handle: "growth", description: "Growth", price: { __typename: "FlatRatePrice", active: true, currency: "USD", amount: "25.00" }, usage: null },
      { handle: "bronze", description: "Bronze", price: { __typename: "TieredPrice", active: true, currency: "USD", tiersMode: "GRADUATED", tiers: [{ upTo: null, amountPerUnit: "5.00", amount: "0.00" }] }, usage: { quantity: 1, cost: { amount: "5.00", currencyCode: "USD" } } },
    ], pendingUpdate: null, legacySubscriptionId: "provider-1",
  } },
};
const purchase = id => ({
  id, shopId: "shop-1", provider: "SHOPIFY", status: "ACTIVE", createdAt: start,
  activatedAt: start, creditsGranted: 5, currentAmount: 5, reservedAmount: 0, version: 0,
  billingPeriodId: "period-1", shopifyPlanHandleSnapshot: "growth", shopifyEventHandleSnapshot: "bronze",
  providerSubscriptionIdSnapshot: "fixture-context:provider-1", providerPurchaseAmount: "5.00",
  providerPurchaseCurrency: "USD", refunds: [], plan: { name: "Growth", shopifyPlanHandle: "growth" },
});
const record = (name, result) => async () => { operations.push({ name, transactionOpen }); return result; };
function databaseFor(rows) {
  return {
    recoveryCreditPurchase: { count: record("db.purchase.count", rows.length), findMany: record("db.purchase.findMany", rows) },
    shop: { findUnique: record("outside-db.shop.findUnique", { shopifyShopId: "external-shop-1" }) },
    subscription: { findUnique: record("outside-db.subscription.findUnique", { billingPeriodId: "period-1", billingPeriod: { periodStart: start, periodEnd: end } }) },
    $transaction: async callback => {
      transactionOpen = true;
      try {
        return await callback({
          recoveryCreditPurchase: { findFirst: record("tx.purchase.findFirst", rows[0]), updateMany: record("tx.purchase.updateMany", { count: 1 }) },
          shopEntitlementCounter: { findUnique: record("tx.counter.findUnique", { id: "counter-1", version: 0, refundingQuantity: 0, reservedQuantity: 0 }), updateMany: record("tx.counter.updateMany", { count: 1 }) },
          recoveryCreditRefund: { create: record("tx.refund.create", { id: "refund-1" }) },
        });
      } finally { transactionOpen = false; }
    },
  };
}
const results = {
  nodeVersion: process.version,
  methodology: "Executed unchanged TypeScript source after Node type stripping with mocked Prisma and HTTP ports. No PostgreSQL, installed SDK, real Shopify call, SQL statement count, latency, or throughput was measured.",
  sources: fingerprints,
};
providerBody = providerSnapshot;
for (const n of [1, 5, 20]) {
  operations = [];
  const service = new Management(databaseFor(Array.from({ length: n }, (_, i) => purchase(`purchase-${i}`))), new Provider(credentials));
  const result = await service.listPurchaseHistory({ shopId: "shop-1", shopifyShopId: "external-shop-1", page: 1, pageSize: n });
  assert.equal(result.purchases.length, n);
  assert.ok(result.purchases.every(item => item.refundEligible === true));
  for (const [name, expected] of Object.entries({
    "db.purchase.count": 1, "db.purchase.findMany": 1,
    "outside-db.shop.findUnique": n, "outside-db.subscription.findUnique": n,
    "credentials.read": n, "provider.fetch": n,
  })) assert.equal(operations.filter(item => item.name === name).length, expected, name);
  assert.ok(operations.every(item => item.transactionOpen === false));
  results[`history_${n}`] = {
    resultCount: result.purchases.length,
    counts: Object.fromEntries([...new Set(operations.map(item => item.name))].map(name => [name, operations.filter(item => item.name === name).length])),
  };
}
operations = [];
const refundService = new Management(databaseFor([purchase("purchase-1")]), new Provider(credentials));
results.refund = {
  outcome: await refundService.requestRefund({ shopId: "shop-1", shopifyShopId: "external-shop-1", purchaseId: "purchase-1", requestId: "request-1" }),
  operations,
};
assert.equal(results.refund.outcome.code, "REQUESTED");
assert.deepEqual(operations.map(item => item.name), [
  "tx.purchase.findFirst", "outside-db.shop.findUnique", "outside-db.subscription.findUnique",
  "credentials.read", "provider.fetch", "tx.counter.findUnique", "tx.refund.create",
  "tx.purchase.updateMany", "tx.counter.updateMany",
]);
assert.ok(operations.every(item => item.transactionOpen === true));
operations = [];
providerBody = {};
results.malformedProviderResponse = {
  body: {},
  result: await new Provider(credentials).getActiveSubscription({ shopifyShopId: "external-shop-1" }),
};
assert.equal(results.malformedProviderResponse.result, null);
results.assertions = "Passed: current-source N+1 counts, eligible fixture projections, outside-client/network work inside refund transaction, malformed response mapped to null.";
process.stdout.write(JSON.stringify(results, null, 2) + "\n");
