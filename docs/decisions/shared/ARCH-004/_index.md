# ARCH-004 — Shared Tasks

Architecture:

```text
docs/architecture/ARCH-004-cart-activity-recovery-rescheduling.md
```

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ARCH-004-SHARED-001 | Define canonical cart activity recovery event | Complete | — |
| ARCH-004-SHARED-002 | Publish cart activity shared contract release | Complete | SHARED-001 |

Shared release tasks are complete.


## Architect acceptance — SHARED-001

```text
ARCH-004-SHARED-001   Complete
ARCH-004-SHARED-002   Ready
```

The accepted cart activity contract can now be published before Shopify and
Background consumers adopt it.


## Architect acceptance — SHARED-002

```text
ARCH-004-SHARED-001   Complete
ARCH-004-SHARED-002   Complete
```

Published consumer version:

```text
@modainteract/moda-interact-shared@0.6.0
```

Shopify and Background consumer work may now proceed in parallel.
