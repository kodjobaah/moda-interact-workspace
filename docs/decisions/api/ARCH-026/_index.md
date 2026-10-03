# ARCH-026 API Tasks

Architecture: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Assigned agent: `moda_api`.

Coordinator: `moda_architect`.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| API-001 | Establish the hosted Moda merchant API foundation | Complete | None |
| API-002 | Establish WooCommerce installation connection and authentication | Complete | API-001, DATABASE-001 |
| API-003 | Expose the authenticated Woo merchant bootstrap read model | Ready | API-002, DATABASE-002 |

API-001 Attempt 2 and API-002 Attempt 2 are Accepted and Complete. API-002 implementation `ba2650b36b599d7965ca5fe12ac0131179a2bcfa` is the accepted Woo installation connection/authentication contract: public/global targets retain strict HTTPS/default-port policy even under local-development mode, live site-control proof precedes state-dependent reconnect conflict, the authenticated probe distinguishes expected `401 unauthorized` from unexpected `500 internal_error`, and OpenAPI v1 carries exact status/error mappings. DATABASE-002 is also architect-accepted Complete, so API-003 now has all dependencies satisfied and is Ready. WOO-003 is independently promoted Ready from API-002 acceptance. The individual task file is authoritative for task state.
