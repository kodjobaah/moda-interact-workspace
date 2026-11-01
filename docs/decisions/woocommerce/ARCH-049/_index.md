# ARCH-049 WooCommerce tasks

Architecture: `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`
Assigned logical agent: `moda_woocommerce`
Owning repository: `moda-interact-woocommerce/`
Coordinator: `moda_architect`

| Task | Outcome | Status in uploaded task snapshot | Dependencies |
|---|---|---|---|
| `ARCH-049-WOOCOMMERCE-001` | Capture and publish WordPress Site Identity on initial connection; preserve explicit `requestSync()` and bounded retries | Complete (Attempt 2, architect-accepted; developer completion recorded) | None |
| `ARCH-049-WOOCOMMERCE-002` | Merchant Store branding panel, authorised manual sync and truthful last-accepted timestamp | Architect accepted (Attempt 1; remains in review pending explicit developer completion) | `ARCH-049-WOOCOMMERCE-001` |

The individual task YAML is authoritative if this index becomes stale. Task 001 is accepted and explicitly complete. Task 002 is architect-accepted, but its `completion_mode: developer` keeps it in `review` until the developer records explicit completion. `ARCH-049-SYSTEM-TEST-001` remains pending and terminal because task 002 and other declared prerequisites remain incomplete; acceptance does not waive its manual gate.

`WOOCOMMERCE-001` excludes automatic WordPress brand-change hooks and a Woo daily reconciliation; `WOOCOMMERCE-002` must not reintroduce them. Background's separate image-media recheck and Shopify source schedule remain in place.
