# ARCH-005 — Shopify Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ARCH-005-SHOPIFY-001 | Initialise Shopify merchant international defaults | Complete | SHARED-002, DATABASE-001 |
| ARCH-005-SHOPIFY-002 | Introduce merchant UI locale and standards-aware formatting | Complete | SHARED-006, DATABASE-001 |
| ARCH-005-SHOPIFY-003 | Emit canonical buyer international context on Shopify recovery events | Complete | SHARED-004, BACKGROUND-001 |


Current executable Shopify task:

```text
None for ARCH-005
```

All three Shopify ARCH-005 implementation tasks are Complete.

`ARCH-005-SHARED-006` is Complete and published as:

```text
@modainteract/moda-interact-shared@0.6.3
```

`SHOPIFY-002` now consumes the Shared ICU runtime through the public
`@modainteract/moda-interact-shared/internationalization` subpath and owns its
merchant UI translations as 20 independent JSON catalogues under
`moda-interact/app/i18n/locales/`.

Country, language, currency and timezone remain independent. Integrated ARCH-005
system validation may advance when the authoritative system-test task/index is
reconciled against its complete dependency set.
