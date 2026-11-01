# ARCH-049 WooCommerce tasks

Architecture: `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`
Assigned logical agent: `moda_woocommerce`
Owning repository: `moda-interact-woocommerce/`
Coordinator: `moda_architect`

| Task | Outcome | Status in uploaded task snapshot | Dependencies |
|---|---|---|---|
| `ARCH-049-WOOCOMMERCE-001` | Capture and publish WordPress Site Identity on initial connection; preserve explicit `requestSync()` and bounded retries | Complete (Attempt 2, architect-accepted; developer completion recorded) | None |
| `ARCH-049-WOOCOMMERCE-002` | Merchant Store branding panel, authorised manual sync and truthful last-accepted timestamp | Complete (Attempt 1; architect accepted, developer completion recorded) | `ARCH-049-WOOCOMMERCE-001` |

The individual task YAML is authoritative if this index becomes stale. Tasks 001 and 002 are accepted and explicitly complete. All declared dependencies of `ARCH-049-SYSTEM-TEST-001` are complete, so its task is dependency-ready; it remains unclaimed behind the terminal manual gate and requires explicit developer invocation before execution.

`WOOCOMMERCE-001` excludes automatic WordPress brand-change hooks and a Woo daily reconciliation; `WOOCOMMERCE-002` must not reintroduce them. Background's separate image-media recheck and Shopify source schedule remain in place.
