# ARCH-007 SHOPIFY-002 Attempt 2 review note

Attempt 2 received **Changes Requested** for one remaining canonical billing SYSTEM-code mismatch.

The accepted Shared 0.7.4 contract uses:

```text
BILLING_SUBSCRIPTION_ENDED
```

but `billing.service.ts` currently persists:

```text
SUBSCRIPTION_ENDED
```

The latter is rejected by the canonical Shared schema, so subscription-ended merchant messages render without the required billing CTA.

The authoritative Attempt 3 correction contract is the latest `## Architect Review` in:

```text
docs/decisions/shopify/ARCH-007/SHOPIFY-002-merchant-billing-ui-system-actions.md
```

Do not broaden this correction into ARCH-005 full UI translation work.
