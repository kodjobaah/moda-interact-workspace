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
| `SHOPIFY-002` | Close residual billing-options navigation and validation gaps without reopening accepted routing architecture | Ready | ARCH-013-SHOPIFY-001 |

## Execution note

`SHOPIFY-001` remains Complete / Attempt 2 Accepted. Run `ARCH-013-SHOPIFY-002` as the current Ready correction task. Do not reopen SHOPIFY-001 and do not start billing v1.1 implementation in the same task.

Current Ready frontier: `ARCH-013-SHOPIFY-002`. Billing-v1.1 implementation remains sequenced after SHOPIFY-002 architect acceptance.
