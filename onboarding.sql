UPDATE shopify."ShopSettings"
SET "onboardingCompleted" = false,
    "updatedAt" = NOW()
WHERE "shopId" = 'cmtrsenye0000po6glmgjescp';

SELECT
    "shopId",
    "onboardingCompleted",
    "plan"
FROM shopify."ShopSettings"
WHERE "shopId" = 'cmtrsenye0000po6glmgjescp';
