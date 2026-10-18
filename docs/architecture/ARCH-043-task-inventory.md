# ARCH-043 — Task inventory (contract-driven Admin, no new Shared work)

**20 canonical task definitions after 18 October Background consolidation** (15 original plus 5 new tasks); one Database task and no ARCH-043 Shared publication task. Old superseded draft task files remain excluded. The earlier files are superseded. Shopify and Commerce each retain two task IDs, divided into a reusable server-only configuration service (`*-001`) and consuming runtime integration (`*-002`). The task frontmatter is authoritative for state.

**18 October deduplication reconciliation (controlling):** no task IDs or states change. ADMIN-002 prepares retirement of duplicate active authoring (`merchantKnowledge.upload`, `support.translation`, and `ai.providers.openAiTranslationApiKey`) **without waiting for downstream consumers**; Gateway-001 activates the two legacy policy editor restrictions after cutover. The extra translation API key is removed from the new speech-only writer contract. API-001 + SHOPIFY-001/002 (+ Background-002 where relevant) adopt one sealed `merchant.knowledge.r2`; BACKGROUND-001/009 adopt existing `CommerceTranslationProviderCredential` and `CommerceTranslationModelConfiguration` for support translations. BACKGROUND-008 remains a resolver **only** for WhatsApp, Shopify and speech. Gateway and terminal system test verify that retired keys cannot override authoritative configuration. No new Database/Shared/System Test task.
**14 portable task definitions**; one Database task, two Admin tasks, no ARCH-043 Shared tasks. The earlier files are superseded. Shopify, Commerce and API each retain two task IDs, divided into a reusable server-only configuration service (`*-001`) and consuming runtime integration (`*-002`). The task frontmatter is authoritative for state.

| Task | Agent | Status | Dependencies |
|---|---|---|---|
| `ARCH-043-ADMIN-001` | moda_admin | Complete | `ARCH-043-DATABASE-001` |
| `ARCH-043-ADMIN-002` | moda_admin | Complete | `ARCH-043-DATABASE-001`, `ARCH-043-ADMIN-001` |
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

No `_index.md` edits. Background-010..012 are not canonical new tasks; archived/superseded draft numbers are not reactivated. The developer reports `DATABASE-001` completed since this baseline; its canonical task YAML/architect review must be reconciled before dependent tasks are promoted from Pending to Ready. The ADMIN-002 task is already materialised and actively claimed by the developer; do not reset its execution metadata when applying this architectural amendment. Other task materialisation and status must be determined from their individual canonical task files.

## 18 October 2026 — Five pending additions (Background split into services and consumers)

The table above is historical source-snapshot state; the task frontmatter and developer's current branch determine live state. The five tasks below are defined but not materialised. No task can start while a dependency is still in progress/review. `ADMIN-002` stays developer-owned and in progress; the additional five sealed purposes belong to that existing task, with no new Admin authentication-bootstrap task.

| Task | Repository owner | Depends on |
|---|---|---|
| `ARCH-043-ADMIN-004` | `moda-interact-admin` | `ARCH-043-ADMIN-002` |
| `ARCH-043-API-004` | `moda-interact-api` | `ARCH-043-ADMIN-002`, `ARCH-043-DATABASE-001` |
| `ARCH-043-BACKGROUND-008` | `moda-interact-background` | `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-002` — create typed resolver services; no provider changes |
| `ARCH-043-BACKGROUND-009` | `moda-interact-background` | `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-008`, `ARCH-043-BACKGROUND-001` — integrate accepted resolver into providers |
| `ARCH-043-SHOPIFY-003` | `moda-interact` | `ARCH-043-ADMIN-002`, `ARCH-043-SHOPIFY-001` |

Current `GATEWAY-001` and terminal `SYSTEM-TEST-001` must remain pending until all five new tasks and their prerequisite set are accepted. `COMMERCE_CURSOR_SECRET` is deferred; embedding settings stay with `CommerceEmbeddingConfiguration`; `WOO_BILLING_ENVIRONMENT` stays deployment-owned. No `_index.md` edits. Background-010..012 are not canonical new tasks; archived/superseded draft numbers are not reactivated.

### Canonical new task file paths

- `docs/decisions/admin/ARCH-043/ADMIN-004-partner-api-credential-reader.md`
- `docs/decisions/api/ARCH-043/API-004-woo-billing-credential-reader.md`
- `docs/decisions/background/ARCH-043/BACKGROUND-008-platform-credential-resolver-services.md`
- `docs/decisions/background/ARCH-043/BACKGROUND-009-integrate-provider-credential-consumers.md`
- `docs/decisions/shopify/ARCH-043/SHOPIFY-003-partner-billing-credential-reader.md`
