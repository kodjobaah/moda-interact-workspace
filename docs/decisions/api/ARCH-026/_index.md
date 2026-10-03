# ARCH-026 API Tasks

Architecture: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Assigned agent: `moda_api`.

Coordinator: `moda_architect`.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| API-001 | Establish the hosted Moda merchant API foundation | Complete | None |
| API-002 | Establish WooCommerce installation connection and authentication | Complete | API-001, DATABASE-001 |
| API-003 | Expose the authenticated Woo merchant bootstrap read model | Ready | API-002, DATABASE-002 |

API-001 Attempt 2 and API-002 Attempt 2 are Accepted and Complete. API-002 implementation `ba2650b36b599d7965ca5fe12ac0131179a2bcfa` remains the accepted Woo installation connection/authentication contract. API-003 Attempt 1 is Ready / Changes Requested: its authenticated tenant-scoped read model is accepted in substance, but the merchant-bootstrap OpenAPI contract must add the runtime validator's non-empty lower bound for nullable international-context strings and strengthen the OpenAPI consistency regression. WOO-003 remains independently Ready from API-002 acceptance. WOO-005 is not promoted; it still requires accepted WOO-004 and API-003. The individual task file is authoritative for task state.
