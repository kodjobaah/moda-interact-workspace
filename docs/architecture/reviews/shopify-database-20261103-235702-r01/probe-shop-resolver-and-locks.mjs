/**
 * Snapshot reproduction, not an application test suite or a SQL benchmark.
 * Executes the uploaded TypeScript unchanged apart from Node's type erasure.
 * Database, Shopify and imported helpers are explicit in-memory substitutes.
 * Usage (Node 24): node --experimental-vm-modules probe-shop-resolver-and-locks.mjs WORKSPACE_ROOT
 */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { stripTypeScriptTypes } from 'node:module';
import vm from 'node:vm';

const root = resolve(process.argv[2] || '.');
const source = (relative) => readFileSync(join(root, relative), 'utf8');

async function load(relative, dependencies) {
  const context = vm.createContext({ Date, Intl, Set, Map, Error, Promise });
  const text = stripTypeScriptTypes(source(relative), { mode: 'transform' });
  const mod = new vm.SourceTextModule(text, { context, identifier: relative });
  await mod.link(async (name) => {
    assert.ok(Object.hasOwn(dependencies, name), `Unmocked dependency: ${name}`);
    const exports = dependencies[name];
    return new vm.SyntheticModule(Object.keys(exports), function () {
      for (const [key, value] of Object.entries(exports)) this.setExport(key, value);
    }, { context, identifier: name });
  });
  await mod.evaluate();
  return mod.namespace;
}

function fixture({ refresh = false, invalidResponse = false } = {}) {
  const calls = [];
  const shop = {
    id: 'audit-shop', domain: 'review.myshopify.com',
    shopifyShopId: 'gid://shopify/Shop/1', status: 'ACTIVE',
    storeLocale: refresh ? 'fr' : 'en',
    defaultLanguageTag: refresh ? 'fr' : 'en',
    defaultCountryCode: 'GB', defaultTimeZone: 'Europe/London',
  };
  const settings = {
    id: 'audit-settings', shopId: shop.id,
    defaultLanguageTag: refresh ? 'fr' : 'en',
    defaultCountryCode: 'GB', defaultTimeZone: 'Europe/London',
  };
  const record = (name, value) => async () => { calls.push(name); return value; };
  const db = {
    shop: {
      findUnique: record('shop.findUnique', shop),
      update: async ({ data }) => { calls.push('shop.update'); return { ...shop, ...data }; },
    },
    subscription: { findUnique: record('subscription.findUnique', { id: 'audit-subscription' }) },
    shopSettings: {
      findUnique: record('shopSettings.findUnique', settings),
      update: record('shopSettings.update', settings),
    },
  };
  db.$transaction = async (fn) => { calls.push('$transaction'); return fn(db); };
  const admin = {
    graphql: async () => {
      calls.push('shopify.graphql');
      return { json: async () => invalidResponse ? {
        errors: [{ message: 'AUDIT_ORIGINAL_PROVIDER_ERROR', extensions: { code: 'AUDIT_ERROR' } }],
      } : {
        data: {
          shop: {
            shopifyShopId: shop.shopifyShopId, myshopifyDomain: shop.domain,
            ianaTimezone: 'Europe/London', shopAddress: { countryCodeV2: 'GB' },
          },
          shopLocales: [{ locale: 'en', primary: true, published: true }],
        },
      } };
    },
  };
  return { calls, shop, db, admin };
}

async function resolver(f) {
  const ns = await load('moda-interact/app/services/shop/shop.service.ts', {
    '../../db.server': { default: f.db },
    '@modainteract/moda-interact-shared/internationalization': {
      canonicaliseLanguageTag: (value) => Intl.getCanonicalLocales(value)[0],
      normalizeCountryCode: (value) => value.toUpperCase(),
      normalizeTimeZone: (value) => value,
    },
    '../discounts/shopify-discount-lifecycle.service': {
      lockShopLifecycleRow: () => { throw new Error('Unexpected lifecycle helper'); },
      markDiscountCatalogueUnavailable: () => { throw new Error('Unexpected lifecycle helper'); },
    },
  });
  return new ns.ShopService();
}

const outcomes = [];
{
  const f = fixture();
  const service = await resolver(f);
  const result = await service.resolveShopifyShop({ admin: f.admin, domain: f.shop.domain });
  assert.equal(result.id, f.shop.id);
  assert.deepEqual(f.calls, ['shopify.graphql', 'shop.findUnique', 'subscription.findUnique', 'shopSettings.findUnique']);
  outcomes.push({ case: 'existing_unchanged_shop', observed: f.calls, prisma_operations: 3, provider_requests: 1, writes: 0 });
}
{
  const f = fixture();
  const service = await resolver(f);
  await Promise.all([1, 2].map(() => service.resolveShopifyShop({ admin: f.admin, domain: f.shop.domain })));
  const count = (key) => f.calls.filter((name) => name === key).length;
  for (const key of ['shopify.graphql', 'shop.findUnique', 'subscription.findUnique', 'shopSettings.findUnique']) assert.equal(count(key), 2);
  outcomes.push({ case: 'two_concurrent_resolutions_same_shop', observed: f.calls, prisma_operations: 6, provider_requests: 2, writes: 0 });
}
{
  const f = fixture({ refresh: true });
  const service = await resolver(f);
  await service.resolveShopifyShop({ admin: f.admin, domain: f.shop.domain });
  assert.deepEqual(f.calls, ['shopify.graphql', 'shop.findUnique', 'subscription.findUnique', 'shopSettings.findUnique', '$transaction', 'shop.update', 'shopSettings.update']);
  outcomes.push({ case: 'profile_refresh_during_resolution', observed: f.calls, prisma_operations: 5, transaction_wrappers: 1, provider_requests: 1, writes: 2 });
}
{
  const f = fixture({ invalidResponse: true });
  const service = await resolver(f);
  let error;
  try { await service.resolveShopifyShop({ admin: f.admin, domain: f.shop.domain }); }
  catch (caught) { error = caught; }
  assert.ok(error);
  assert.equal(error.message.includes('AUDIT_ORIGINAL_PROVIDER_ERROR'), false);
  assert.equal(error.cause, undefined);
  assert.deepEqual(f.calls, ['shopify.graphql']);
  outcomes.push({ case: 'graphql_error_body_without_shop', resulting_error: error.message, original_provider_error_preserved: false, limitation: 'The SDK itself is mocked; this verifies handling if an errors-only body reaches ShopService.' });
}
{
  const statements = [];
  const ns = await load('moda-interact/app/services/billing/subscription-locks.ts', {
    '@prisma/client': { Prisma: { sql: (parts, ...values) => parts.reduce((s, part, i) => s + part + (i < values.length ? `$${i + 1}` : ''), '') } },
  });
  const tx = { $queryRaw: async (sql) => { statements.push(sql.replace(/\s+/g, ' ').trim()); return []; } };
  await ns.lockShopForInitialPaidActivation(tx, 'audit-shop');
  assert.equal(statements.length, 1);
  assert.ok(statements[0].includes('FROM "shopify"."Shop"'));
  const schema = source('moda-interact/database/prisma/schema.prisma');
  const model = schema.match(/model Shop \{([\s\S]*?)^\}/m)?.[1];
  assert.ok(model?.includes('@@schema("commerce")'));
  outcomes.push({ case: 'initial_paid_activation_lock', emitted_sql: statements[0], canonical_relation: 'commerce.Shop', relation_mismatch: true, sql_executed: false });
  statements.length = 0;
  await ns.lockInitialFreeActivationState(tx, 'audit-shop');
  assert.equal(statements.length, 2);
  outcomes.push({ case: 'existing_settings_subscription_locks', emitted_sql: statements, sql_executed: false });
}

process.stdout.write(JSON.stringify({
  validation_kind: 'original-source execution with in-memory substitutes',
  runtime: process.version,
  postgres_executed: false,
  shopify_sdk_executed: false,
  assertions: 'passed',
  outcomes,
}, null, 2) + '\n');
