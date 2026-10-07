# ARCH-028 Admin Tasks

Architecture: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Assigned Agent: `moda_admin`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ADMIN-001 | Configure platform WhatsApp recipient suppression duration | Pending | DATABASE-001 |

## Current frontier

ADMIN-001 becomes Ready when DATABASE-001 is Complete. It is independent of Shared/Messaging/Background execution.

## Boundary

Admin owns only audited SUPER_ADMIN configuration of the platform suppression duration. Background owns reachability policy execution.
