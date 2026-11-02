# ARCH-036-COMMERCE-001 local selection correction verification

Review-only diagnostic run against the uncommitted Attempt 1 worktree on 2 November 2026, Node 24.19.0. Cursor-aware fixture verifies the distinct options returned, rather than only their count. No live provider/database validation is claimed. Temporary test removed after execution.

## Diagnostic

```typescript
import { afterEach, describe, expect, it, vi } from 'vitest';
import { createLocalPolicyRegistrations } from '../src/commerce/preview/local-policy-providers';
import type { AuthorizedToolCall } from '../src/commerce/preview/local-execution-ports';

const couponId = 'woo:coupon:27';
type CouponRow = {
  id: string;
  shopId: string;
  shopifyDiscountNodeId: string;
  providerType: string;
  method: string;
  providerStatus: string;
  title: string;
  startsAt: Date | null;
  endsAt: Date | null;
  fixedSelectable: boolean;
  providerSnapshot: Record<string, unknown>;
  singleRedeemCode: string | null;
  isAvailable: boolean;
  lastSeenSyncGeneration: number;
  lastSyncedAt: Date;
  unavailableAt: Date | null;
};
const couponRow: CouponRow = {
  id: 'discount-row-27', shopId: 'woo-shop', shopifyDiscountNodeId: couponId,
  providerType: 'WooCoupon:code', method: 'CODE', providerStatus: 'ACTIVE',
  title: 'Ten percent', startsAt: null, endsAt: null, fixedSelectable: true,
  providerSnapshot: {
    provider: 'WOOCOMMERCE', couponId: 27, discountType: 'percent', amount: '10',
    freeShipping: false, usageLimit: 0, usageCount: 0, usageLimitPerUser: 0,
    maximumUsageItems: 0, minimumAmount: '0', maximumAmount: '0', productIds: [],
    excludedProductIds: [], productCategories: [], excludedProductCategories: [],
    individualUse: true, excludeSaleItems: false, emailRestrictionsPresent: false,
    uninspectedMetadataPresent: false, dateExpiresGmt: null, expiryUnverified: false,
    codeDeliverable: true, code: 'TENOFF',
  },
  singleRedeemCode: 'TENOFF', isAvailable: false,
  lastSeenSyncGeneration: 4, lastSyncedAt: new Date('2026-11-02T12:00:00Z'), unavailableAt: null,
};

function makePrisma(
  mode: 'NONE' | 'FIXED' | 'AI_BEST_APPLICABLE',
  override = false,
  catalogueStatus = 'CURRENT',
  lastSuccessfulSyncAt: Date | null = new Date(),
  options: { coupons?: CouponRow[]; platform?: 'SHOPIFY' | 'WOOCOMMERCE'; sessionScope?: string; fixedId?: string | null } = {},
) {
  const coupons = options.coupons ?? [couponRow];
  const platform = options.platform ?? 'WOOCOMMERCE';
  const session = { findFirst: vi.fn(async () => platform === 'SHOPIFY' ? { accessToken: 'test-token', scope: options.sessionScope ?? 'read_discounts' } : null) };
  const shop = {
    findFirst: vi.fn(async () => ({ id: 'woo-shop', platform })),
    findUnique: vi.fn(async () => ({ id: 'woo-shop', domain: 'woo.example', platform, status: 'ACTIVE' })),
  };
  const shopifyDiscount = {
    findFirst: vi.fn(async ({ where = {} }: { where?: Record<string, unknown> } = {}) => coupons.find((row) => {
      if (typeof where.shopId === 'string' && row.shopId !== where.shopId) return false;
      if (typeof where.id === 'string' && row.id !== where.id) return false;
      if (typeof where.shopifyDiscountNodeId === 'string' && row.shopifyDiscountNodeId !== where.shopifyDiscountNodeId) return false;
      if (where.isAvailable === true && !row.isAvailable) return false;
      if (Array.isArray(where.AND)) {
        const now = Date.now();
        if (row.startsAt && row.startsAt.getTime() > now) return false;
        if (row.endsAt && row.endsAt.getTime() <= now) return false;
      }
      return true;
    }) ?? null),
    findMany: vi.fn(async ({ where = {}, take }: { where?: Record<string, unknown>; take?: number } = {}) => {
      const matches = coupons.filter((row) => {
        if (where.shopId === 'woo-shop' && row.shopId !== 'woo-shop') return false;
        if (typeof where.isAvailable === 'boolean' && row.isAvailable !== where.isAvailable) return false;
        if (typeof where.providerType === 'string' && row.providerType !== where.providerType) return false;
        if (typeof where.providerStatus === 'string' && row.providerStatus !== where.providerStatus) return false;
        if (typeof where.fixedSelectable === 'boolean' && row.fixedSelectable !== where.fixedSelectable) return false;
        if (where.shopifyDiscountNodeId && typeof where.shopifyDiscountNodeId === 'object') {
          const ids = (where.shopifyDiscountNodeId as { in?: unknown }).in;
          if (Array.isArray(ids) && !ids.includes(row.shopifyDiscountNodeId)) return false;
        }
        if (Array.isArray(where.AND)) {
          const now = Date.now();
          if (row.startsAt && row.startsAt.getTime() > now) return false;
          if (row.endsAt && row.endsAt.getTime() <= now) return false;
        }
        return true;
      }).sort((left, right) => left.shopifyDiscountNodeId.localeCompare(right.shopifyDiscountNodeId));
      return matches.slice(0, take ?? matches.length);
    }),
  };
  const prisma = {
    session,
    shop,
    shopSettings: { findUnique: vi.fn(async () => ({ recoveryOfferMode: mode, fixedShopifyDiscountId: options.fixedId ?? null })) },
    shopifyDiscountCatalogue: { findUnique: vi.fn(async () => ({ status: catalogueStatus, syncGeneration: 4, activeSyncToken: null, lastSuccessfulSyncAt, unavailableAt: null })) },
    shopRecoveryPolicyOverride: { findUnique: vi.fn(async () => override ? ({
      recoveryOfferMode: 'FIXED', fixedShopifyDiscountId: 'discount-row-27', expiresAt: null,
    }) : null) },
    shopifyDiscount,
    checkoutRecovery: { findFirst: vi.fn(async () => ({
      lineItems: [{ productId: 'woo-product-3', variantId: 'woo-variation-4', quantity: 1, unitPrice: '20.00' }],
      currency: 'USD',
    })) },
  };
  return { prisma, session, shop, shopifyDiscount };
}

function context(): AuthorizedToolCall {
  return {
    turn: {
      contractVersion: 'commerce.v1', shopId: 'woo-shop', checkoutRecoveryId: 'recovery-1',
      conversationId: 'conversation-1', inboundVersion: 1,
    },
    grantId: 'grant-1', releaseId: 'release-1', toolId: 'tool-1', toolRevisionId: 'revision-1',
    name: 'discounts.evaluate', definition: {} as never, arguments: {},
    shopDomain: 'woo.example', environment: 'test', deadlineAt: Date.now() + 10_000,
    limits: { maxPolicyOutputItems: 10, maxCollectionItems: 10 },
    signal: new AbortController().signal, budget: { reserveProviderRequest: vi.fn() },
    purpose: 'preview', requestId: 'request-1',
  } as unknown as AuthorizedToolCall;
}

function operation(registrations: ReturnType<typeof createLocalPolicyRegistrations>, name: 'discounts.getOptions' | 'discounts.evaluate') {
  const registration = registrations.find((item) => item.operation === name);
  if (!registration) throw new Error(`Missing ${name} registration`);
  return registration.adapter.execute;
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});


it('review: returns 50 distinct current coupons and authorizes the selected coupon outside that page', async()=>{
 vi.stubEnv('COMMERCE_CURSOR_SECRET','z'.repeat(40));
 const selected=Array.from({length:51},(_,n)=>({...couponRow,id:`row-${101+n}`,isAvailable:true,shopifyDiscountNodeId:`woo:coupon:${101+n}`,providerSnapshot:{...couponRow.providerSnapshot,couponId:101+n}}));
 const expired={...selected[0],id:'expired',shopifyDiscountNodeId:'woo:coupon:1',endsAt:new Date(Date.now()-1000)};
 const t=makePrisma('FIXED',false,'CURRENT',new Date(),{coupons:[expired,...selected]});
 t.shopifyDiscount.findMany.mockImplementation(async (args:any)=>{
   let found=[expired,...selected].filter(r=>(!args.where.shopId || r.shopId===args.where.shopId) && (!args.where.isAvailable || r.isAvailable) &&
     (!args.where.AND || ((!r.startsAt || r.startsAt.getTime()<=Date.now()) && (!r.endsAt || r.endsAt.getTime()>Date.now()))) &&
     (!args.where.shopifyDiscountNodeId?.in || args.where.shopifyDiscountNodeId.in.includes(r.shopifyDiscountNodeId)))
     .sort((a,b)=>a.shopifyDiscountNodeId.localeCompare(b.shopifyDiscountNodeId));
   if(args.cursor) found=found.slice(found.findIndex(r=>r.shopifyDiscountNodeId===args.cursor.shopId_shopifyDiscountNodeId.shopifyDiscountNodeId)+(args.skip??0));
   return found.slice(0,args.take??found.length);
 });
 const registrations=createLocalPolicyRegistrations(t.prisma as never);
 const result:any=await operation(registrations,'discounts.getOptions')({context:context(),input:{}});
 expect(result).toMatchObject({status:'OK',data:{truncated:true}});
 expect(result.data.offers.map((o:any)=>o.offerId)).toEqual(selected.slice(0,50).map(r=>r.shopifyDiscountNodeId));
 expect(new Set(result.data.offers.map((o:any)=>o.offerId)).size).toBe(50);
 expect(await operation(registrations,'discounts.evaluate')({context:context(),input:{offerId:'woo:coupon:151',proposal:null}})).toMatchObject({status:'ERROR',code:'UNAVAILABLE'});
 expect(await operation(registrations,'discounts.evaluate')({context:context(),input:{offerId:'woo:coupon:999',proposal:null}})).toMatchObject({status:'ERROR',code:'DENIED'});
});

```

## Result

```text

 RUN  v5.0.1 /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-COMMERCE-001


 Test Files  3 passed (3)
      Tests  9 passed (9)
   Start at  18:24:08
   Duration  858ms (import 50%, transform 35%, tests 14%, worker 1%)


```
