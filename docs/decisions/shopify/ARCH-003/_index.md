# ARCH-003 — Shopify Decisions

| Task | Title | Status | Depends On |
|---|---|---|---|
| ARCH-003-SHOPIFY-001 | Correct dashboard conversation relation | Complete | — |
| ARCH-003-SHOPIFY-002 | Show active pending recoveries on merchant Usage overview | Complete | SHOPIFY-001, BACKGROUND-002 |
| ARCH-003-SHOPIFY-003 | Make pending-recovery resource an explicit JSON response | Complete | ARCH-003-SHOPIFY-002 |

## Immediate executable task

```text
ARCH-003-SHOPIFY-003
```

Agent:

```text
moda_app
```

Repository:

```text
moda-interact
```

Reason:

The live SYSTEM-TEST-002 collector successfully reached the authenticated
embedded app but ordinary `fetch().json()` received React Router's framework
stream representation from the resource route.

The route must expose an explicit JSON HTTP contract.


## Architect acceptance — SHOPIFY-003

`ARCH-003-SHOPIFY-003` is Complete.

The pending-recovery resource now exposes an explicit JSON HTTP contract for
ordinary authenticated browser fetches.

Next integration step:

```text
deploy moda-interact
    -> rerun existing SYSTEM-TEST-002 CDP collector
```
