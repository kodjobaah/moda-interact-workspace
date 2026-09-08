# ARCH-003 — Shopify Decisions

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SHOPIFY-001 | Correct Shopify dashboard CheckoutRecovery conversation relation | Complete | — |
| SHOPIFY-002 | Show active pending recoveries on merchant Usage overview | Complete | SHOPIFY-001, BACKGROUND-002 |
| SHOPIFY-003 | Make pending-recovery resource an explicit JSON response | Complete | SHOPIFY-002 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
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
