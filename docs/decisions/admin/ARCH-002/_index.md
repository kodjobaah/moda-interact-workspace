# ARCH-002 Admin Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Assigned Agent:

`moda_admin`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| ADMIN-001 | Add admin service health and readiness | Ready | GATEWAY-001 |
| ADMIN-002 | Add OpenTelemetry to admin runtime | Ready | GATEWAY-001 |

The admin service remains an internal/private HTTP service.

Its operational `/health` and `/ready` contract is separate from the unresolved
production admin application base-path/host-routing decision.

The same logical admin service identity is used in test and production.

The individual task file is authoritative for task state.
