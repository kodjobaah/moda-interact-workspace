# ARCH-036-COMMERCE-001 Attempt 1 selection-bound review

Local implementation based on `d0ade086b60b42a4145cc7e50836c2b2c8258de5`; Node 24.19.0. The temporary test reused the submitted local-operation fixture and honored query limits/cursors for 51 selected rows. This is a deterministic operation-boundary reproduction, not a live database test. The temporary test was removed after the run.

## Reproduction

```typescript
import { afterEach, describe, expect, it, vi } from 'vitest';
import { createLocalPolicyRegistrations } from '../src/commerce/preview/local-policy-providers';
import type { AuthorizedToolCall } from '../src/commerce/preview/local-execution-ports';

const couponId = 'woo:coupon:27';
const couponRow = {
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

function makePrisma(mode: 'NONE' | 'FIXED' | 'AI_BEST_APPLICABLE', override = false, catalogueStatus = 'CURRENT', lastSuccessfulSyncAt: Date | null = new Date()) {
  const session = { findFirst: vi.fn() };
  const shop = {
    findFirst: vi.fn(async () => ({ id: 'woo-shop', platform: 'WOOCOMMERCE' })),
    findUnique: vi.fn(async () => ({ id: 'woo-shop', domain: 'woo.example', platform: 'WOOCOMMERCE', status: 'ACTIVE' })),
  };
  const shopifyDiscount = {
    findFirst: vi.fn(async () => ({ shopifyDiscountNodeId: couponId, startsAt: null, endsAt: null })),
    findMany: vi.fn(async () => [couponRow]),
  };
  const prisma = {
    session,
    shop,
    shopSettings: { findUnique: vi.fn(async () => ({ recoveryOfferMode: mode, fixedShopifyDiscountId: null })) },
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

afterEach(() => vi.unstubAllEnvs());


function manySelected() {
 vi.stubEnv('COMMERCE_CURSOR_SECRET', 'x'.repeat(40));
 const t=makePrisma('FIXED');
 const rows=Array.from({length:51},(_,n)=>({...couponRow,isAvailable:true,shopifyDiscountNodeId:`woo:coupon:${101+n}`,providerSnapshot:{...couponRow.providerSnapshot,couponId:101+n}}));
 t.shopifyDiscount.findMany.mockImplementation(async (args:any)=>{
   let found=rows.filter(r=>!args.where.shopifyDiscountNodeId?.in || args.where.shopifyDiscountNodeId.in.includes(r.shopifyDiscountNodeId));
   if(args.cursor) found=found.slice(found.findIndex(r=>r.shopifyDiscountNodeId===args.cursor.shopId_shopifyDiscountNodeId.shopifyDiscountNodeId)+(args.skip??0));
   return found.slice(0,args.take??found.length);
 });
 return createLocalPolicyRegistrations(t.prisma as never);
}
it('review: reports the selected-set limit instead of claiming completeness', async()=>{
 const result=await operation(manySelected(),'discounts.getOptions')({context:context(),input:{}});
 expect(result).toMatchObject({status:'OK',data:{truncated:true}});
});
it('review: does not deny an exact read of the 51st selected coupon', async()=>{
 const result=await operation(manySelected(),'discounts.evaluate')({context:context(),input:{offerId:'woo:coupon:151',proposal:null}});
 expect(result).not.toMatchObject({status:'ERROR',code:'DENIED'});
});

```

## Result

```text

 RUN  v5.0.1 /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-COMMERCE-001

 ❯ tests/arch036-commerce-review-pagination.test.ts (2 tests | 2 failed) 823ms
   × review: reports the selected-set limit instead of claiming completeness 265ms
   × review: does not deny an exact read of the 51st selected coupon 554ms

⎯⎯⎯⎯⎯⎯⎯ Failed Tests 2 ⎯⎯⎯⎯⎯⎯⎯

 FAIL  tests/arch036-commerce-review-pagination.test.ts > review: reports the selected-set limit instead of claiming completeness
AssertionError: expected { Object (contractVersion, status, ...) } to match object { status: 'OK', …(1) }
(4 matching properties omitted from actual)

- Expected
+ Received

  {
    "data": {
-     "truncated": true,
+     "truncated": false,
    },
    "status": "OK",
  }

 ❯ tests/arch036-commerce-review-pagination.test.ts:87:17
     85| it('review: reports the selected-set limit instead of claiming complet…
     86|  const result=await operation(manySelected(),'discounts.getOptions')({…
     87|  expect(result).toMatchObject({status:'OK',data:{truncated:true}});
       |                 ^
     88| });
     89| it('review: does not deny an exact read of the 51st selected coupon', …

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/2]⎯

 FAIL  tests/arch036-commerce-review-pagination.test.ts > review: does not deny an exact read of the 51st selected coupon
AssertionError: expected { Object (contractVersion, status, ...) } to not match object { status: 'ERROR', code: 'DENIED' }

Compared values have no visual difference.

 ❯ tests/arch036-commerce-review-pagination.test.ts:91:21
     89| it('review: does not deny an exact read of the 51st selected coupon', …
     90|  const result=await operation(manySelected(),'discounts.evaluate')({co…
     91|  expect(result).not.toMatchObject({status:'ERROR',code:'DENIED'});
       |                     ^
     92| });
     93|

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[2/2]⎯


 Test Files  1 failed | 2 passed (3)
      Tests  2 failed | 6 passed (8)
   Start at  15:50:10
   Duration  13.18s (import 52%, transform 30%, tests 16%, worker 2%)

  Transform  transforming modules took 6.53s · 30% of tracked time, re-done on every run
             persist transforms across runs with fsModuleCache: true
             learn more: https://vitest.dev/guide/improving-performance#caching-between-reruns


```
