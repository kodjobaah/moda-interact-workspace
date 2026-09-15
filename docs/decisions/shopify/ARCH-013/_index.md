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
| `SHOPIFY-002` | Close residual billing-options navigation and validation gaps without reopening accepted routing architecture | Complete | ARCH-013-SHOPIFY-001 |

## Execution note

`SHOPIFY-001` remains Complete / Attempt 2 Accepted. `SHOPIFY-002` is Complete / Attempt 1 Accepted. Do not reopen either accepted routing task.

Current Ready frontier: none. ARCH-013 is Implemented. The SHOPIFY-002 sequencing gate on later billing-v1.1 work is removed, but no later billing task is implicitly started or promoted.
