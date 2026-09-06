# ARCH-005 — Shopify Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ARCH-005-SHOPIFY-001 | Initialise Shopify merchant international defaults | Ready — Attempt 2 scope correction | SHARED-002, DATABASE-001 |
| ARCH-005-SHOPIFY-002 | Introduce merchant UI locale and standards-aware formatting | Ready | SHARED-002, DATABASE-001 |
| ARCH-005-SHOPIFY-003 | Emit canonical buyer international context on Shopify recovery events | Complete | SHARED-004, BACKGROUND-001 |

Immediate executable Shopify tasks:

```text
ARCH-005-SHOPIFY-001
ARCH-005-SHOPIFY-002
```

`SHOPIFY-001` now owns only merchant-default initialisation at authenticated
shop resolution, including `read_locales` and `read_markets` pre-production
scope configuration. It no longer owns the cross-service event contract.

`SHOPIFY-003` is Complete. Its consumer-first rollout was satisfied and the producer now emits the accepted optional buyer-specific context:

```text
SHARED-004 published
    -> BACKGROUND-001 accepts the optional context
    -> SHOPIFY-003 emits it  [complete]
```

Currency, language and country remain independent. `presentment_currency` must
never be used to infer `customer_locale`, and country must never be used to
choose language.

Architect acceptance note:

- `SHOPIFY-003` passed producer-contract review and is Complete.
- Its completion does not independently make system testing Ready; Shopify 001/002 and remaining Messaging implementation must still complete.
