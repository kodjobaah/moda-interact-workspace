# ARCH-006 Gateway Tasks

Architecture: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Assigned Agent: `moda_gateway`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| GATEWAY-001 | Deploy merchant-communications worker | Ready | BACKGROUND-007 |

The individual task file YAML metadata is authoritative. This index is a navigation/planning aid and must be corrected if it drifts.

Architect coordination on 2026-09-06: BACKGROUND-007 is independently architect-accepted Complete, so GATEWAY-001 is Ready. System-test tasks enabled by this deployment remain Pending/manual-gated until all of their implementation dependencies are Complete and the developer chooses to run them.

Architect coordination on 2026-09-06: GATEWAY-001 Attempt 1 returned to Ready for a bounded deployment-contract/Blueprint-validation correction. BACKGROUND-007 remains Complete. ARCH-006 system-test tasks remain Pending/manual-gated and must not be promoted by the Gateway agent.
