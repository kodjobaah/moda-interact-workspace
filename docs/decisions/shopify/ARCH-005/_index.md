# ARCH-005 — Shopify Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SHOPIFY-001 | Initialise Shopify merchant international defaults | Complete | SHARED-002, DATABASE-001 |
| SHOPIFY-002 | Introduce merchant UI locale and standards-aware formatting | Complete | SHARED-006, DATABASE-001 |
| SHOPIFY-003 | Emit canonical buyer international context on Shopify recovery events | Complete | SHARED-004, BACKGROUND-001 |
| SHOPIFY-004 | Complete authenticated Shopify merchant UI internationalisation coverage | **Ready** | SHOPIFY-002, ARCH-006-SHOPIFY-003, ARCH-007-SHOPIFY-002 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
Current executable Shopify task:

```text
ARCH-005-SHOPIFY-004 — Ready, next claim Attempt 1
```

`ARCH-005-SHOPIFY-004` is now Ready. `ARCH-005-SHOPIFY-002`, `ARCH-006-SHOPIFY-003`, and `ARCH-007-SHOPIFY-002` are all architect-accepted Complete. Claim it as Attempt 1 and follow the standalone 32-key i18n manifest exactly.

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
