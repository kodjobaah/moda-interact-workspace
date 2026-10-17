# ARCH-043 — Simplified configuration and encrypted-secret task inventory

**Nineteen bounded task definitions** in ten domains, with **one consolidated database task and exactly two new Prisma models**. Encrypted application secrets share the generic configuration table; the independent unseal key/KMS identity stays external. All definitions are portable, not materialised; status must be re-gated before launch.

| Task | Owner | Initial status | Depends on |
|---|---|---|---|
| `ARCH-043-ADMIN-001` | moda_admin | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-ADMIN-002` | moda_admin | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-API-001` | moda_api | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-API-002` | moda_api | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-API-003` | moda_api | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-BACKGROUND-001` | moda_background | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-BACKGROUND-002` | moda_background | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-COMMERCE-001` | moda_commerce | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-COMMERCE-002` | moda_commerce | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-DATABASE-001` | moda_database | Ready | — |
| `ARCH-043-GATEWAY-001` | moda_gateway | Pending | `ARCH-043-ADMIN-001`, `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-001`, `ARCH-043-BACKGROUND-002`, `ARCH-043-API-001`, `ARCH-043-API-002`, `ARCH-043-API-003`, `ARCH-043-COMMERCE-001`, `ARCH-043-COMMERCE-002`, `ARCH-043-SHOPIFY-001`, `ARCH-043-SHOPIFY-002`, `ARCH-043-MCP-001`, `ARCH-043-MESSAGING-001` |
| `ARCH-043-MCP-001` | moda_mcp | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-MESSAGING-001` | moda_messaging | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002`, `ARCH-043-API-003` |
| `ARCH-043-SHARED-001` | moda_shared | Ready | — |
| `ARCH-043-SHARED-002` | moda_shared | Pending | `ARCH-043-SHARED-001`, `ARCH-043-SHARED-003` |
| `ARCH-043-SHARED-003` | moda_shared | Ready | — |
| `ARCH-043-SHOPIFY-001` | moda_app | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-SHOPIFY-002` | moda_app | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-SYSTEM-TEST-001` | moda_system_test | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002`, `ARCH-043-ADMIN-001`, `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-001`, `ARCH-043-BACKGROUND-002`, `ARCH-043-API-001`, `ARCH-043-API-002`, `ARCH-043-API-003`, `ARCH-043-COMMERCE-001`, `ARCH-043-COMMERCE-002`, `ARCH-043-SHOPIFY-001`, `ARCH-043-SHOPIFY-002`, `ARCH-043-MCP-001`, `ARCH-043-MESSAGING-001`, `ARCH-043-GATEWAY-001` |

## Files

- `docs/decisions/admin/ARCH-043/ADMIN-001-platform-configuration-editor.md`
- `docs/decisions/admin/ARCH-043/ADMIN-002-write-only-secrets-editor-and-auth-bootstrap.md`
- `docs/decisions/api/ARCH-043/API-001-merchant-knowledge-database-configuration.md`
- `docs/decisions/api/ARCH-043/API-002-sealed-commerce-keyring-consumer.md`
- `docs/decisions/api/ARCH-043/API-003-private-meta-webhook-secret-resolver.md`
- `docs/decisions/background/ARCH-043/BACKGROUND-001-consume-platform-runtime-configuration.md`
- `docs/decisions/background/ARCH-043/BACKGROUND-002-sealed-commerce-keyring-and-shopify-oauth.md`
- `docs/decisions/commerce/ARCH-043/COMMERCE-001-preview-database-configuration.md`
- `docs/decisions/commerce/ARCH-043/COMMERCE-002-sealed-studio-auth-and-connection-keyring.md`
- `docs/decisions/database/ARCH-043/DATABASE-001-platform-configuration-schema.md`
- `docs/decisions/gateway/ARCH-043/GATEWAY-001-retire-policy-environment-variables.md`
- `docs/decisions/mcp/ARCH-043/MCP-001-sealed-embedding-credential-keyring.md`
- `docs/decisions/messaging/ARCH-043/MESSAGING-001-database-backed-meta-verification-secrets.md`
- `docs/decisions/shared/ARCH-043/SHARED-001-define-platform-configuration-contracts.md`
- `docs/decisions/shared/ARCH-043/SHARED-002-publish-platform-configuration-contracts.md`
- `docs/decisions/shared/ARCH-043/SHARED-003-sealed-secret-envelope-contract.md`
- `docs/decisions/shopify/ARCH-043/SHOPIFY-001-merchant-knowledge-platform-policy.md`
- `docs/decisions/shopify/ARCH-043/SHOPIFY-002-sealed-shopify-oauth-bootstrap.md`
- `docs/decisions/system-test/ARCH-043/SYSTEM-TEST-001-certify-platform-runtime-configuration.md`

No `_index.md` files are edited. The first implementation gates are DATABASE-001, SHARED-001 and SHARED-003 (three independent tasks).
