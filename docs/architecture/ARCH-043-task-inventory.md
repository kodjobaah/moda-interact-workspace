# ARCH-043 — Canonical task inventory (18 October 2026)

The **16 active task IDs** below implement the accepted two-table Platform Configuration design. Background has **exactly two** tasks: one generic typed service, then consumer integration. The previously authored one-purpose Background drafts (`BACKGROUND-001` through `BACKGROUND-009`, including `BACKGROUND-008/009`) are retired from task discovery and remain in Git history. Individual task YAML is authoritative for status; this file is a planning projection from the attached snapshot, not a claim of new branches, worktrees or completion.

The Admin registry (`moda-interact-admin/src/lib/admin/platform-configuration/{contracts,secrets-contracts}.ts`) and `docs/architecture/ARCH-043-configuration-environment-variable-mapping.md` define the **17 authoritative PostgreSQL keys**. Background service contracts support the nine keys used by Background; other keys are explicitly denied rather than exposing Admin/Commerce/Messaging secrets to Background. `merchant.knowledge.r2` is canonical; `merchantKnowledge.upload` and `support.translation` are not active. There are **no ARCH-043 Shared tasks**, configuration caches, Messaging runtime integration or new Prisma tables.

| Task | Owner | Snapshot status | Depends on |
|---|---|---|---|
| `ARCH-043-DATABASE-001` | moda_database | Complete | — |
| `ARCH-043-GATEWAY-001` | moda_gateway | Pending | `ARCH-043-ADMIN-001`, `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-001`, `ARCH-043-BACKGROUND-002`, `ARCH-043-API-001`, `ARCH-043-API-002`, `ARCH-043-COMMERCE-001`, `ARCH-043-COMMERCE-002`, `ARCH-043-SHOPIFY-001`, `ARCH-043-SHOPIFY-002`, `ARCH-043-MCP-001` |
| `ARCH-043-MCP-001` | moda_mcp | Pending | `ARCH-043-DATABASE-001` |
| `ARCH-043-SHOPIFY-001` | moda_app | Ready | `ARCH-043-DATABASE-001` |
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
No `_index.md` edits. Background-010..012 are not canonical new tasks; archived/superseded draft numbers are not reactivated. The developer reports `DATABASE-001` completed since this baseline; its canonical task YAML/architect review must be reconciled before dependent tasks are promoted from Pending to Ready. The ADMIN-002 task is already materialised and actively claimed by the developer; do not reset its execution metadata when applying this architectural amendment. Other task materialisation and status must be determined from their individual canonical task files.

## 18 October 2026 — Five pending additions (Background split into services and consumers)

The table above is historical source-snapshot state; the task frontmatter and developer's current branch determine live state. The five tasks below are defined but not materialised. No task can start while a dependency is still in progress/review. `ADMIN-002` stays developer-owned and in progress; the additional five sealed purposes belong to that existing task, with no new Admin authentication-bootstrap task.

| Task | Repository owner | Depends on |
|---|---|---|
| `ARCH-043-ADMIN-004` | `moda-interact-admin` | `ARCH-043-ADMIN-002` |
| `ARCH-043-API-004` | `moda-interact-api` | `ARCH-043-ADMIN-002`, `ARCH-043-DATABASE-001` |
| `ARCH-043-BACKGROUND-008` | `moda-interact-background` | `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-002` — create typed resolver services; no provider changes |
| `ARCH-043-BACKGROUND-009` | `moda-interact-background` | `ARCH-043-ADMIN-002`, `ARCH-043-BACKGROUND-008`, `ARCH-043-BACKGROUND-001` — integrate accepted resolver into providers |
| `ARCH-043-SHOPIFY-002` | `moda-interact` | `ARCH-043-SHOPIFY-001`, `ARCH-043-ADMIN-002` |

Current `GATEWAY-001` and terminal `SYSTEM-TEST-001` must remain pending until all five new tasks and their prerequisite set are accepted. `COMMERCE_CURSOR_SECRET` is deferred; embedding settings stay with `CommerceEmbeddingConfiguration`; `WOO_BILLING_ENVIRONMENT` stays deployment-owned. No `_index.md` edits. Background-010..012 are not canonical new tasks; archived/superseded draft numbers are not reactivated.

### Canonical new task file paths

- `docs/decisions/admin/ARCH-043/ADMIN-004-partner-api-credential-reader.md`
- `docs/decisions/api/ARCH-043/API-004-woo-billing-credential-reader.md`
- `docs/decisions/background/ARCH-043/BACKGROUND-008-platform-credential-resolver-services.md`
- `docs/decisions/background/ARCH-043/BACKGROUND-009-integrate-provider-credential-consumers.md`


## 18 October 2026 — Final Shopify two-task consolidation

`SHOPIFY-001` is the sole Shopify server-side configuration service task, covering **three** keys: `merchant.knowledge.r2`, `shopify.oauth` and `shopify.partner`. `SHOPIFY-002` wires all three into Merchant Knowledge R2 upload/finalisation, Shopify authentication bootstrap and the two Shopify Partner billing GraphQL calls. The former separate Shopify Partner consumer task and the legacy duplicate SHOPIFY-001 file are deleted from task discovery. Gateway and System Test depend only on SHOPIFY-002 for the Shopify cutover. Admin's Shopify Partner writer remains ADMIN-002; ADMIN-004 is a separate Admin consumer and is **not** folded into Shopify.

The snapshot has DATABASE-001 and ADMIN-002 Complete; SHOPIFY-001 is therefore marked Ready in the revised definition. SHOPIFY-002 remains Pending until its own task dependencies are Complete. No runtime implementation or `_index.md` changes are included.
