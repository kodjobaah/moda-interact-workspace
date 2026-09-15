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
| `SHOPIFY-001` | Make merchant routing, navigation and breadcrumbs lifecycle-coherent; remove redundant/stale routes | Complete | ARCH-010-SHOPIFY-012, ARCH-010-SHOPIFY-016, ARCH-010-SHOPIFY-021, ARCH-010-SHOPIFY-026 |

## Execution note

Run only `ARCH-013-SHOPIFY-001`. Do not start billing v1.1 implementation in the same task/attempt.

Architect review state: **Attempt 2 Accepted**. `SHOPIFY-001` is Complete and ARCH-013 has no remaining Ready implementation task. Billing-v1.1/ARCH-011 work is not implicitly started; future task definitions must use the canonical ARCH-013 route graph.
