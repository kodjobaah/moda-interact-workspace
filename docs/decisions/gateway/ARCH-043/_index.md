# ARCH-043 Gateway Tasks

Architecture: [ARCH-043-configuration-environment-variable-mapping](../../../architecture/ARCH-043-configuration-environment-variable-mapping.md); [ARCH-043-database-managed-platform-configuration](../../../architecture/ARCH-043-database-managed-platform-configuration.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-043-GATEWAY-001](GATEWAY-001-retire-policy-environment-variables.md) | Remove retired application-policy environment variables | ready | `ARCH-043-ADMIN-001`, `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-001`, `ARCH-043-BACKGROUND-002`, `ARCH-043-API-001`, `ARCH-043-API-002`, `ARCH-043-COMMERCE-001`, `ARCH-043-COMMERCE-002`, `ARCH-043-SHOPIFY-001`, `ARCH-043-SHOPIFY-002`, `ARCH-043-MCP-001`, `ARCH-043-ADMIN-004`, `ARCH-043-API-004`, `ARCH-043-MESSAGING-001` |
| [ARCH-043-GATEWAY-002](GATEWAY-002-retire-migrated-provider-secrets.md) | Retire superseded provider secret wiring after database cutover | superseded | — |
