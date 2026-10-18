# ARCH-043 — Canonical task inventory (18 October 2026)

The **17 active task IDs** below implement the accepted two-table Platform Configuration design. Background has **exactly two** tasks: one generic typed service, then consumer integration. The previously authored one-purpose Background drafts (`BACKGROUND-001` through `BACKGROUND-009`, including `BACKGROUND-008/009`) are retired from task discovery and remain in Git history. Individual task YAML is authoritative for status; this file is a planning projection from the attached snapshot, not a claim of new branches, worktrees or completion.

The Admin registry (`moda-interact-admin/src/lib/admin/platform-configuration/{contracts,secrets-contracts}.ts`) and `docs/architecture/ARCH-043-configuration-environment-variable-mapping.md` define the **17 authoritative PostgreSQL keys**. Background service contracts support the nine keys used by Background; other keys are explicitly denied rather than exposing Admin/Commerce/Messaging secrets to Background. `merchant.knowledge.r2` is canonical; `merchantKnowledge.upload` and `support.translation` are not active. There are **no ARCH-043 Shared tasks**, configuration caches, Messaging runtime integration or new Prisma tables.

| Task | Owner | Snapshot status | Depends on |
|---|---|---|---|
| `ARCH-043-DATABASE-001` | moda_database | Complete | — |
| `ARCH-043-ADMIN-001` | moda_admin | Complete | DATABASE-001 |
| `ARCH-043-ADMIN-002` | moda_admin | Complete | DATABASE-001, ADMIN-001 |
| `ARCH-043-ADMIN-004` | moda_admin | Pending | ADMIN-002 |
| `ARCH-043-API-001` | moda_api | Ready | DATABASE-001 |
| `ARCH-043-API-002` | moda_api | Pending | API-001, ADMIN-002 |
| `ARCH-043-API-004` | moda_api | Pending | DATABASE-001, ADMIN-002 |
| `ARCH-043-BACKGROUND-001` | moda_background | Ready | DATABASE-001, ADMIN-002 |
| `ARCH-043-BACKGROUND-002` | moda_background | Pending | BACKGROUND-001, ADMIN-002 |
| `ARCH-043-COMMERCE-001` | moda_commerce | Pending | DATABASE-001 |
| `ARCH-043-COMMERCE-002` | moda_commerce | Pending | COMMERCE-001, ADMIN-002 |
| `ARCH-043-SHOPIFY-001` | moda_app | Pending | DATABASE-001 |
| `ARCH-043-SHOPIFY-002` | moda_app | Pending | SHOPIFY-001, ADMIN-002 |
| `ARCH-043-SHOPIFY-003` | moda_app | Pending | SHOPIFY-001, ADMIN-002 |
| `ARCH-043-MCP-001` | moda_mcp | Pending | DATABASE-001 |
| `ARCH-043-GATEWAY-001` | moda_gateway | Pending | ADMIN-001/002/004, API-001/002/004, BACKGROUND-001/002, COMMERCE-001/002, SHOPIFY-001/002/003, MCP-001 |
| `ARCH-043-SYSTEM-TEST-001` | moda_system_test | Pending | All required implementation/Gateway tasks (terminal) |

## Canonical Background task definitions

- `docs/decisions/background/ARCH-043/BACKGROUND-001-platform-configuration-service.md` — one reusable typed server-only configuration reader; environment-scoped DB lookup, canonical AAD/decryption, validation, fresh operation snapshots and injectability. **No consumer changes.**
- `docs/decisions/background/ARCH-043/BACKGROUND-002-consume-platform-configuration.md` — consumer-by-consumer replacement of Background environment reads, including Woo coupon, R2, speech, Commerce keyring, Shopify OAuth/Partner/App Events and WhatsApp sender, plus existing DB-owned support-message translation. **No second resolver.**

## Dependencies and operation rules

`DATABASE-001` and `ADMIN-002` are marked Complete in this snapshot. `BACKGROUND-001` can be promoted Ready subject to rechecking the canonical parent task branch and launcher preparation; `BACKGROUND-002` stays Pending until architect acceptance of `BACKGROUND-001`. Gateway and System Test depend on both, never on superseded `BACKGROUND-008/009`. Other domains keep their separate approved ownership and task files.

All configuration readers do a fresh PostgreSQL read **per relevant operation**, with same-operation reuse only; no application/Redis configuration caches or stale fallback. R2 endpoint/bucket remain editable, with asset relocation handled by separate tasks. Existing `BackgroundRuntimeConfig` and Commerce translation provider/model configuration are separate authorities and are not replaced.

No `docs/decisions/**/_index.md` or `docs/architecture/_index.md` changes are authorised before the developer closes the architectural session.
