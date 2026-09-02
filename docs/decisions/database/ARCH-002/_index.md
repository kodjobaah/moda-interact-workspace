# ARCH-002 Database Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Amendment:

`docs/architecture/ARCH-002-admin-security-amendment.md`

Assigned Agent:

`moda_database`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| DATABASE-001 | Add platform-admin identity registry | Ready | - |

`DATABASE-001` provides the durable authorisation identity consumed by
`ADMIN-003`. It stores no administrator password or OAuth credential.
