# ARCH-013 Shopify Tasks

Architecture:

`docs/architecture/ARCH-013-merchant-application-routing-navigation.md`

Assigned Agent:

`moda_app`

Coordinator:

`moda_architect`

> ARCH-013 routing cleanup is intentionally completed before billing v1.1 implementation work. Individual task YAML is authoritative.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| `SHOPIFY-001` | Make merchant routing, navigation and breadcrumbs lifecycle-coherent; remove redundant/stale routes | **Ready** | ARCH-010-SHOPIFY-012, ARCH-010-SHOPIFY-016, ARCH-010-SHOPIFY-021, ARCH-010-SHOPIFY-026 |

## Execution note

Run only `ARCH-013-SHOPIFY-001`. Do not start billing v1.1 implementation in the same task/attempt.

Architect review state: **Attempt 1 Changes Requested**. `SHOPIFY-001` remains **Ready** for the same task to be reclaimed as Attempt 2. The only authorised production correction is `/app` home-loader gating of pending-recovery business data for states that deny `PENDING_RECOVERIES`.
