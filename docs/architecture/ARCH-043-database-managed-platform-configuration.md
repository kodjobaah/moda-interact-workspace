---
id: ARCH-043
title: Database-managed platform configuration (simplified)
status: agreed
coordinator: moda_architect
created: 2026-10-17
updated: 2026-10-17
---

# ARCH-043: Database-managed platform configuration (simplified)

## Status

**Agreed in principle by developer, 17 October 2026; portable task definitions, not materialised.** This supersedes the earlier nine-model/multi-policy/credential proposal. No application implementation or Git branch is included. `ARCH-042` is reserved for possible WooCommerce promotions work. No `docs/decisions/**/_index.md` or `docs/architecture/_index.md` edits during this architecture session.

## Problem

Several non-secret application policies are read from deployment environment variables, requiring redeployments to change business tuning. Other domain configuration already resides in PostgreSQL (BackgroundRuntimeConfig, billing policies, shop preferences, Commerce provider/model settings); duplicating those would add complexity. We want one modest, controlled store for remaining policies and **encrypted application secrets**.

## Goals

- Add one generic JSON configuration table and one append-only audit table, versioned and environment-scoped.
- Restrict editable keys and JSON payloads through published Shared validators; allow sealed secret envelopes only for designated secret purposes and never plaintext or recoverable audit values.
- Provide one secure Moda Admin editor and expose a typed validated snapshot to relevant service owners.
- Migrate approved nonsecret env readers independently by service; support cache refresh without hot-path database lookups.
- Preserve existing domain credential models/ciphertext; import selected root, OAuth, session and Meta secrets as encrypted rows without changing the Commerce credential ciphertext format. Retire old env declarations only after validated cutover.

## Non-Goals

- No new credential/policy tables, broad provider token migration, Woo coupon columns or existing domain configuration schema refactor.
- Do not move DB/Redis URLs, the independent configuration-unseal root/KMS identity, `OTEL_*`, service binding/routing, or WordPress merchant-local connection settings into PostgreSQL. Selected session/OAuth/webhook secrets are in scope **only as encrypted records**.
- Do not change existing BackgroundRuntimeConfig, PlatformBillingPolicy, ShopFeaturePreference, ShopSettings, Commerce embeddings/translation or provider-credential models.
- Do not have Shopify or WooCommerce browsers query central configuration directly, or expose Shopify decryption or unseal material to browsers or merchant-controlled plugin code; the trusted Shopify server may use purpose-bound unlock material.

## Existing source and new schema

Based on the 17 October 2026 workspace snapshot and the environment audit. `moda-interact-database/prisma/schema.prisma` already contains typed durable business settings and an audited Background singleton. The only new Prisma models are:

1. `PlatformConfiguration`: `id`, `environment`, `key`, `value Json`, `version`, `updatedBy`, `createdAt`, `updatedAt`, unique `(environment,key)`.
2. `PlatformConfigurationAudit`: `id`, `environment`, `key`, `expectedVersion`, `resultingVersion`, `beforeValue Json?`, `afterValue Json`, `actorId`, `reason`, `createdAt`; unique `(environment,key,resultingVersion)`.

The exact proposed Prisma declarations, payload schemas and field bounds are in `docs/architecture/ARCH-043-configuration-schema-review.md`.

## Runtime configuration groups

| Key | Owner/consumer | Editable data | Keep external |
|---|---|---|---|
| `woo.couponSync` | Background | ten bounded coupon-worker numeric controls | Redis, DB, worker infrastructure |
| `merchantKnowledge.upload` | API and Shopify server | file limits, R2 non-secret endpoint/bucket | R2 access/secret keys, signing secrets |
| `speech.transcription` | Background | provider choice and model IDs | Groq/OpenAI API keys |
| `support.translation` | Background | support-message translator provider/model only | API key; other Commerce translation configuration |
| `commerce.preview` | Commerce | deadlineMs and outputTokens | private service URLs, credentials, safety hard caps |
| `admin.grafana` | Admin | dashboard/navigation URLs | OTLP/LOKI transport and exporter credentials |

Existing database-backed domains are not copied into this table. All unlisted provider secrets remain with existing domain ownership, to avoid a bulk migration.

## Encrypted application secrets

The developer requested moving existing `COMMERCE_CONNECTION_KEYS_JSON` + active key ID, `AUTH_SECRET`, Shopify OAuth credentials, `META_APP_SECRET` and `WHATSAPP_VERIFY_TOKEN` to PostgreSQL. `PlatformConfiguration.value` holds a purpose-specific sealed envelope (AES-256-GCM), not a plaintext secret or an arbitrary string. The allowlisted purposes are `commerce.connectionKeys`, `auth.admin`, `auth.commerce`, `shopify.oauth`, `messaging.meta`. Existing Google OAuth client secrets may be included in their service-specific auth bundle; the Commerce command HMAC key may be bundled with its existing keyring where needed.

`PlatformConfigurationAudit` records secret update/revocation **metadata only**; no plaintext or replayable ciphertext. Approved reader paths use an independent deployment/KMS unwrap root; that root cannot be stored solely in the database it protects. The legacy Commerce keyring's authenticated-data and encrypted credential bytes must remain exactly compatible after moving the keyring itself to sealed configuration storage.

Bootstrap is explicit: one-time authenticated import before DB-only cutover; no browser or public webhook access to raw secret envelopes. Admin, Commerce and Shopify currently build authentication/Shopify clients from environment configuration, so their tasks must prove secure load-before-serve behaviour without an open authentication bypass. Messaging lacks a PostgreSQL dependency in the 17 October snapshot; it should consume a narrowly scoped authenticated private API secret snapshot, cache locally, and fail closed on initial load failure. Session and webhook rotation must follow concrete library/provider constraints, not invented grace behaviour.

## Consistency, transactions and security

- Trusted deployment identity determines `environment`; no client-controlled environment, prod/test fallback or cross-tenant leakage.
- `PlatformConfiguration.value` is a closed non-secret policy object OR a strict encrypted secret envelope for a designated key. Reject plaintext secrets everywhere. No freeform JSON editor.
- Create with expected revision zero, update with matching revision, atomically increment version and append audit event with verified admin actor. Clearing/resetting is an update, never deletion or revision reset. Concurrent writes and stale replay fail.
- Normal runtime uses validated cached snapshots; no database query for every webhook, checkout, message or AI turn. On transient refresh failure, use the last validated snapshot when safe; on cold start follow explicit safe defaults or fail closed for configuration requiring explicit setup.
- Existing unrelated provider keys remain in their current approved stores; no plaintext credentials in `value` or credentials/ciphertext in audit logs. Service hard limits remain in code. SSRF restrictions stay service-owned.
- Avoid unrelated changes to source/migrations; roll out DB, accepted Shared publication, readers/Admin, Gateway cleanup, terminal System Test.

## Infrastructure and observability

The Messaging secret distribution requires an authenticated private API route and verified service-to-service access; Gateway must assess private connectivity and service identity. No direct Messaging PostgreSQL client is proposed. Gateway edits only the existing Render Blueprint declarations after consumers complete. Shared structured logging emits key/revision and correlation without values containing credentials; existing framework and OpenTelemetry request telemetry should be reused rather than duplicated.

## Deployment classification and rollback

Treat existing service deployments and configuration state as requiring compatible rollout, not disposable. Database migration is additive. Admin/readers are deployed before env removal, and safe defaults/cutover tests are recorded. Securely import old secrets before cutover; preserve a restricted rollback path until every consumer verifies DB-backed bootstrap and credential rotation without exposing secrets. Roll back consumers without dropping historical configuration/audit tables; secret rollback/recovery requires the prior unseal key and encrypted record revisions as specified in the schema review.

## Execution graph

```text
  DATABASE-001 ──────────────┐
  SHARED-001 ───┐            |
  SHARED-003 ───┴── SHARED-002 (publish)
                  |          |
                  +----------+
                             |
      +----------------------+----------------------+
      |                      |                      |
  Policy readers         Secret writers       Secret consumers
  Admin/Background/      ADMIN-002           COMMERCE-002
  API/Commerce/                             SHOPIFY-002
  Shopify                                  BACKGROUND-002
                                           API-002 / MCP-001
                                                |
                                             API-003
                                                |
                                           MESSAGING-001
      |                      |                      |
      +----------------------+----------------------+
                             |
                         GATEWAY-001
                             |
                        SYSTEM-TEST-001
```

The two Shared implementation tasks may proceed alongside DATABASE-001. SHARED-002 publishes both validators and the Node-only sealed-secret codec before secret consumers start. Every task is repository-owned; no system-test task gates implementation. Secrets must be imported into encrypted records **before** a consuming service removes its bootstrap environment inputs.

## Task inventory

See `docs/architecture/ARCH-043-task-inventory.md` for authoritative portable task definitions and the dependency table. Task YAML is authoritative for task status. Status *ready* means eligible if definitions are materialised and dependencies re-gated; it does not assert a worktree or task branch was created.

## Open questions

- Confirm rollout environment and secure out-of-band injection of the independent config-unseal root or KMS identity; it cannot come solely from the protected database.
- Verify Shopify's module-initialisation contract supports an authenticated load-before-serve DB secret bootstrap. Do not remove OAuth environment inputs if this cannot be proven.
- Confirm existing service-to-service authentication and private routing for API-to-Messaging secret snapshots; missing capability is an explicit API/Gateway gate, not permission for an unauthenticated endpoint.
- Determine exact Auth.js/Shopify/Meta rotation compatibility and safe rollback. Never silently allow a keyless or unauthenticated mode.

- Confirm approved per-environment defaults/activation for R2 storage, since endpoint/bucket must not be fabricated.
- Confirm whether worker concurrency can be adjusted live or requires a worker restart; preserve existing BullMQ correctness.
- Confirm if support-message translation already has equivalent database authority before creating a second policy key.

## Change history

- 17 October 2026: developer explicitly adds Commerce keyring/active ID, Admin/Commerce AUTH_SECRET, Shopify OAuth and Meta verification secrets to encrypted database management. No additional Prisma model; one independent external unseal root or KMS identity required. Expanded repository consumer tasks.

- 17 October 2026: rejected complex nine-model/multi-credential architecture in favour of two generic models and a bounded two-table approach; this amendment adds sealed application secrets without new tables. Prior 40/31/10-task drafts are superseded by 19 bounded task definitions, still using only two new Prisma models and one Shared publication gate.
