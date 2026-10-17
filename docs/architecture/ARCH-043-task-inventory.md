# ARCH-043 — Task inventory (contract-driven Admin, no new Shared work)

**15 portable task definitions**; one Database task, two Admin tasks, no ARCH-043 Shared tasks. The earlier files are superseded. Shopify and Commerce each retain two task IDs, divided into a reusable server-only configuration service (`*-001`) and consuming runtime integration (`*-002`). The task frontmatter is authoritative for state.

| Task | Agent | Status | Dependencies |
|---|---|---|---|
| `ARCH-043-ADMIN-001` | moda_admin | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-ADMIN-002` | moda_admin | In Progress (developer) | `ARCH-043-DATABASE-001`, `ARCH-043-ADMIN-001` |
| `ARCH-043-API-001` | moda_api | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-API-002` | moda_api | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-API-003` | moda_api | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-BACKGROUND-001` | moda_background | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-BACKGROUND-002` | moda_background | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-COMMERCE-001` | moda_commerce | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-COMMERCE-002` | moda_commerce | Pending | `ARCH-043-COMMERCE-001`, `ARCH-043-ADMIN-002` |
| `ARCH-043-DATABASE-001` | moda_database | Ready | — |
| `ARCH-043-GATEWAY-001` | moda_gateway | Pending | `ARCH-043-ADMIN-001`, `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-001`, `ARCH-043-BACKGROUND-002`, `ARCH-043-API-001`, `ARCH-043-API-002`, `ARCH-043-API-003`, `ARCH-043-COMMERCE-001`, `ARCH-043-COMMERCE-002`, `ARCH-043-SHOPIFY-001`, `ARCH-043-SHOPIFY-002`, `ARCH-043-MCP-001` |
| `ARCH-043-MCP-001` | moda_mcp | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-SHOPIFY-001` | moda_app | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-SHOPIFY-002` | moda_app | Pending | `ARCH-043-SHOPIFY-001`, `ARCH-043-ADMIN-002` |
| `ARCH-043-SYSTEM-TEST-001` | moda_system_test | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-ADMIN-001`, `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-001`, `ARCH-043-BACKGROUND-002`, `ARCH-043-API-001`, `ARCH-043-API-002`, `ARCH-043-API-003`, `ARCH-043-COMMERCE-001`, `ARCH-043-COMMERCE-002`, `ARCH-043-SHOPIFY-001`, `ARCH-043-SHOPIFY-002`, `ARCH-043-MCP-001`, `ARCH-043-GATEWAY-001` |

## Canonical task files

- `docs/decisions/admin/ARCH-043/ADMIN-001-platform-configuration-editor.md`
- `docs/decisions/admin/ARCH-043/ADMIN-002-write-only-secrets-editor-and-auth-bootstrap.md`
- `docs/decisions/api/ARCH-043/API-001-merchant-knowledge-database-configuration.md`
- `docs/decisions/api/ARCH-043/API-002-sealed-commerce-keyring-consumer.md`
- `docs/decisions/api/ARCH-043/API-003-private-meta-webhook-secret-resolver.md`
- `docs/decisions/background/ARCH-043/BACKGROUND-001-consume-platform-runtime-configuration.md`
- `docs/decisions/background/ARCH-043/BACKGROUND-002-sealed-commerce-keyring-and-shopify-oauth.md`
- `docs/decisions/commerce/ARCH-043/COMMERCE-001-platform-configuration-service.md`
- `docs/decisions/commerce/ARCH-043/COMMERCE-002-consume-platform-configuration.md`
- `docs/decisions/database/ARCH-043/DATABASE-001-platform-configuration-schema.md`
- `docs/decisions/gateway/ARCH-043/GATEWAY-001-retire-policy-environment-variables.md`
- `docs/decisions/mcp/ARCH-043/MCP-001-sealed-embedding-credential-keyring.md`
- `docs/decisions/shopify/ARCH-043/SHOPIFY-001-platform-configuration-service.md`
- `docs/decisions/shopify/ARCH-043/SHOPIFY-002-consume-platform-configuration.md`
- `docs/decisions/system-test/ARCH-043/SYSTEM-TEST-001-certify-platform-runtime-configuration.md`

No `_index.md` edits. The developer reports `DATABASE-001` completed since this baseline; its canonical task YAML/architect review must be reconciled before dependent tasks are promoted from Pending to Ready. The ADMIN-002 task is already materialised and actively claimed by the developer; do not reset its execution metadata when applying this architectural amendment. Other task materialisation and status must be determined from their individual canonical task files.
