# ARCH-026 API Tasks

Architecture: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Assigned agent: `moda_api`.

Coordinator: `moda_architect`.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| API-001 | Establish the hosted Moda merchant API foundation | Ready | None |
| API-002 | Establish WooCommerce installation connection and authentication | Pending | API-001, DATABASE-001 |
| API-003 | Expose the authenticated Woo merchant bootstrap read model | Pending | API-002, DATABASE-002 |

API-001 repository provisioning is satisfied and its Attempt 1 implementation is architecture-conformant, but the task is Ready for a bounded launcher/worktree/VCS evidence correction before acceptance. API-002 remains Pending until both API-001 and DATABASE-001 are architect-accepted Complete. API-003 remains Pending until both API-002 and DATABASE-002 are architect-accepted Complete, then exposes the first authenticated DB-backed merchant bootstrap read model including shared international context. The individual task file is authoritative for task state.
