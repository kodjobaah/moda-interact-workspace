# ARCH-049 WooCommerce tasks

Architecture: `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`
Assigned logical agent: `moda_woocommerce`
Owning repository: `moda-interact-woocommerce/`
Coordinator: `moda_architect`

| Task | Outcome | Status in uploaded task snapshot | Dependencies |
|---|---|---|---|
| `ARCH-049-WOOCOMMERCE-001` | Capture and publish WordPress Site Identity on initial connection; preserve explicit `requestSync()` and bounded retries | In progress (Attempt 1, developer; includes planned Attempt 2 correction) | None |
| `ARCH-049-WOOCOMMERCE-002` | Merchant Store branding panel, authorised manual sync and truthful last-accepted timestamp | Pending — defined but not materialised | `ARCH-049-WOOCOMMERCE-001` |

The individual task YAML is authoritative if this index becomes stale. Implementation of task 002 starts only when task 001 has been architect-accepted and explicitly completed. `ARCH-049-SYSTEM-TEST-001` is terminal and depends on both WooCommerce tasks plus the other ARCH-049 implementation prerequisites.

`WOOCOMMERCE-001` excludes automatic WordPress brand-change hooks and a Woo daily reconciliation; `WOOCOMMERCE-002` must not reintroduce them. Background's separate image-media recheck and Shopify source schedule remain in place.
