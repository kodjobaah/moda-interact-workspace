# ARCH-010 SHARED-007 consumer sequencing correction

Date: 2026-09-12  
Coordinator: `moda_architect`

## Decision

`ARCH-010-SHARED-007` is correctly Blocked after Attempt 1.

The block is caused by first-party runtime consumers of contracts that SHARED-007 is
supposed to delete. Because ARCH-010 is pre-production, the resolution is **not** to
retain aliases. The consumers must be removed first.

## Confirmed blocking consumers

```text
Background:
  src/services/subscription-cancellation.service.ts
  src/providers/shopify-partner-billing.provider.ts
  tests/unit/services/recovery-billing.service.test.ts

Shopify:
  app/services/merchant-support/system-message-actions.ts
```

The blocked run found no active consumer of:

```text
BILLING_PLAN_CHANGE_ACTION_REQUIRED
```

so it remains in the SHARED-007 removal set.

## Corrected dependency order

```text
published Shared 0.10.0
        |
        +--> ARCH-010-BACKGROUND-020
        |
        +--> ARCH-010-SHOPIFY-024
                  |
                  v
         both Accepted Complete
                  |
                  v
         ARCH-010-SHARED-007 Attempt 2
                  |
                  v
         ARCH-010-SHARED-008 publish 0.11.0
                  |
                  v
         broader repository baseline-conformance + feature tasks
```

`BACKGROUND-020` and `SHOPIFY-024` deliberately run against Shared 0.10.0. Their
purpose is to make the breaking 0.11.0 release safe.

## Ownership boundaries

`BACKGROUND-020` removes only the existing pre-production consumers. It does not
implement provider-authoritative cancellation reconciliation (`BACKGROUND-012`) or
full capacity exhaustion/resume (`BACKGROUND-009`).

`SHOPIFY-024` removes only the obsolete Free-only message consumer and verifies there
are no other active retired-contract consumers. It does not implement the generic
capacity presentation (`SHOPIFY-008`) or broader clean-baseline conformance
(`SHOPIFY-023`).

`SHARED-007` remains the sole owner of actually deleting the public Shared symbols.
`SHARED-008` remains the sole owner of publishing version 0.11.0.
