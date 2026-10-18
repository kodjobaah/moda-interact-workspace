# ARCH-043 — Task inventory (contract-driven Admin, no new Shared work)

**14 portable task definitions**; one Database task, two Admin tasks, no ARCH-043 Shared tasks. The earlier files are superseded. Shopify, Commerce and API each retain two task IDs, divided into a reusable server-only configuration service (`*-001`) and consuming runtime integration (`*-002`). The task frontmatter is authoritative for state.

| Task | Agent | Status | Dependencies |
|---|---|---|---|
| `ARCH-043-ADMIN-001` | moda_admin | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-ADMIN-002` | moda_admin | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-ADMIN-001` |
| `ARCH-043-API-001` | moda_api | Ready | `ARCH-043-DATABASE-001` |
| `ARCH-043-API-002` | moda_api | Pending | `ARCH-043-API-001`, `ARCH-043-ADMIN-002` |
| `ARCH-043-BACKGROUND-001` | moda_background | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-BACKGROUND-002` | moda_background | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-COMMERCE-001` | moda_commerce | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-COMMERCE-002` | moda_commerce | Pending | `ARCH-043-COMMERCE-001`, `ARCH-043-ADMIN-002` |
| `ARCH-043-DATABASE-001` | moda_database | Complete | — |
| `ARCH-043-GATEWAY-001` | moda_gateway | Pending | `ARCH-043-ADMIN-001`, `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-001`, `ARCH-043-BACKGROUND-002`, `ARCH-043-API-001`, `ARCH-043-API-002`, `ARCH-043-COMMERCE-001`, `ARCH-043-COMMERCE-002`, `ARCH-043-SHOPIFY-001`, `ARCH-043-SHOPIFY-002`, `ARCH-043-MCP-001` |
| `ARCH-043-MCP-001` | moda_mcp | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-SHOPIFY-001` | moda_app | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-SHOPIFY-002` | moda_app | Pending | `ARCH-043-SHOPIFY-001`, `ARCH-043-ADMIN-002` |
| `ARCH-043-SYSTEM-TEST-001` | moda_system_test | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-ADMIN-001`, `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-001`, `ARCH-043-BACKGROUND-002`, `ARCH-043-API-001`, `ARCH-043-API-002`, `ARCH-043-COMMERCE-001`, `ARCH-043-COMMERCE-002`, `ARCH-043-SHOPIFY-001`, `ARCH-043-SHOPIFY-002`, `ARCH-043-MCP-001`, `ARCH-043-GATEWAY-001` |

## Canonical task files

- `docs/decisions/admin/ARCH-043/ADMIN-001-platform-configuration-editor.md`
- `docs/decisions/admin/ARCH-043/ADMIN-002-write-only-secrets-editor-and-auth-bootstrap.md`
- `docs/decisions/api/ARCH-043/API-001-platform-configuration-service.md`
- `docs/decisions/api/ARCH-043/API-002-consume-platform-configuration.md`
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

No `_index.md` edits. `DATABASE-001` is `complete` in the inspected 21:06 snapshot. API-001 is defined Ready on this basis; the task launcher must still revalidate current canonical state before materialising or claiming. All tasks are defined but not materialised in a developer Git worktree.

## API consolidation decision (17 October 2026)

- `API-001`: server-only service for Knowledge policy and sealed Commerce/Meta credentials.
- `API-002`: apply service to existing Knowledge and REST-read consumers and implement the approved private Meta capability. No Messaging consumer.
- Prior `API-003` functionality is retained within API-002; stale duplicate API-001/API-002/API-003 task files are removed so discovery sees one definition per remaining ID.
- API-002 depends on both API-001 and ADMIN-002. Gateway and terminal System Test depend on API-002, not removed API-003. No `_index.md` changes.
