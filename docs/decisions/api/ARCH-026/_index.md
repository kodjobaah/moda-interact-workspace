# ARCH-026 API Tasks

Architecture: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Assigned agent: `moda_api`.

Coordinator: `moda_architect`.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| API-001 | Establish the hosted Moda merchant API foundation | Complete | None |
| API-002 | Establish WooCommerce installation connection and authentication | Ready | API-001, DATABASE-001 |
| API-003 | Expose the authenticated Woo merchant bootstrap read model | Pending | API-002, DATABASE-002 |

API-001 Attempt 2 is Accepted and Complete after the evidence-only launcher/worktree/VCS correction; implementation remains at `6635491`. API-002 Attempt 1 is returned Ready / Changes Requested: the overall connection/authentication design is retained, but public/global targets in local-development must keep the public default-port policy, the authenticated probe must distinguish expected 401 rejection from unexpected 500/internal failure, state-dependent reconnect conflict must follow site-control proof, and the full prepared launcher/worktree/submodule packet must be recorded. DATABASE-002 is architect-accepted Complete, so API-003 has its database dependency satisfied but remains Pending until API-002 is architect-accepted Complete. WOO-003 likewise remains Pending on API-002. Neither downstream task is promoted. The individual task file is authoritative for task state.
