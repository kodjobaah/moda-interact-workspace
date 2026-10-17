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
- Restrict editable keys and JSON payloads through the Admin-owned allowlisted contracts and service-owned runtime validation; allow sealed secret envelopes only for designated secret purposes and never plaintext or recoverable audit values.
- Provide one contract-driven, reusable Moda Admin editor for policies and write-only secrets, backed by one generic CAS/audit persistence service; service owners validate their own snapshots.
- Migrate approved nonsecret env readers independently by service; perform a fresh PostgreSQL configuration read for each relevant operation, with no cross-operation configuration cache.
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

Bootstrap is explicit: one-time authenticated import before DB-only cutover; no browser or public webhook access to raw secret envelopes. Admin, Commerce and Shopify currently build authentication/Shopify clients from environment configuration, so their tasks must prove secure load-before-serve behaviour without an open authentication bypass. Messaging lacks a Prisma/PostgreSQL client in the 17 October snapshot. **ARCH-043 does not modify or integrate `moda-interact-messaging`**: it continues to use its existing `META_APP_SECRET` and `WHATSAPP_VERIFY_TOKEN` deployment configuration. The encrypted `messaging.meta` row, Admin secret form/import and purpose-scoped API-003 capability remain in scope, but none of them changes the Messaging runtime or authorises removal of its environment variables. Authentication/session rotation must follow concrete library/provider constraints, not invented grace behaviour.

## Shopify service and consumption task boundary

Two existing Shopify task IDs are reorganised by capability rather than by configuration key (no additional Shopify tasks):

1. `ARCH-043-SHOPIFY-001`: implement a server-only, typed `PlatformConfiguration` reader with trusted-environment key lookup, fresh per-operation reads, Merchant Knowledge policy validation and sealed `shopify.oauth` decryption using existing ARCH-039 Shared functions and the frozen AAD format. **No existing route, OAuth module or R2 call site is changed here.**
2. `ARCH-043-SHOPIFY-002`: consume the accepted service in the existing Merchant Knowledge R2 upload/finalise flow and in Shopify OAuth startup. Depends on `SHOPIFY-001` and `ADMIN-002` (authenticated secret import/cutover). Keep R2 access keys external. Prove authenticated **load-before-serve** for Shopify's current synchronous `shopifyApp` construction and preserve session/webhook/HMAC semantics.

Actual 17 October source: `moda-interact/app/shopify.server.js` calls `shopifyApp({...})` synchronously from `process.env.SHOPIFY_API_KEY`/`SHOPIFY_API_SECRET`; `app/services/merchant-knowledge/r2-config.server.ts` reads non-secret R2 endpoint/bucket/size and R2 keys from environment; `upload.server.ts` resolves that config in upload paths. The service task must not change these call sites. The consumption task must prove real startup-order compatibility rather than replacing synchronous credentials with an unresolved Promise or silent fallback. The existing upload asset stores `objectKey`, not bucket. `r2Endpoint` and `r2Bucket` **remain editable**; separate storage-relocation tasks own preservation of existing assets and in-flight uploads. ARCH-043 must not lock those fields or implement a competing relocation workflow.

The updated sequencing is `DATABASE-001 -> SHOPIFY-001 -> SHOPIFY-002`, with `ADMIN-002 -> SHOPIFY-002` as a secure import precondition. `GATEWAY-001`/`SYSTEM-TEST-001` still depend on SHOPIFY-002. There is no ARCH-043 Shared implementation task or new database model.

## Commerce service and consumption task boundary

The Commerce workstream contains exactly two domain tasks, organised by capability instead of by configuration key:

1. `ARCH-043-COMMERCE-001` **creates a reusable, read-only Commerce configuration service**, with three typed operations for `commerce.preview`, `auth.commerce` and `commerce.connectionKeys`. It reads the current environment-scoped PostgreSQL row per call, strictly validates policy/secret payloads, uses already published ARCH-039 decryption and the frozen AAD bytes, and does **not** alter existing Commerce consumers. No cross-operation configuration cache or fallback.
2. `ARCH-043-COMMERCE-002` **integrates the service into Commerce consumers**, including Studio preview admission, NextAuth/Google OAuth/session configuration, external connection keyring/HMAC, runtime/embedding and proof-verification paths. It depends on `COMMERCE-001` and `ADMIN-002` (credential import) and must address the existing synchronous `NextAuth(...)` construction and memoised backend configuration safely. Any framework limitation preventing no-cache consumption is a returned architecture issue, not permission for insecure startup or stale environment fallback.

Both tasks remain `moda_commerce`-owned. No additional Commerce, Database or Shared task is introduced. `DATABASE-001` was reported completed by the developer after the inspected snapshot; canonical YAML and architect acceptance must be reconciled before an executable `COMMERCE-001` claim. Gateway env cleanup and terminal System Test retain their existing dependency direction.

## Consistency, transactions and security

- Trusted deployment identity determines `environment`; no client-controlled environment, prod/test fallback or cross-tenant leakage.
- `PlatformConfiguration.value` is a closed non-secret policy object OR a strict encrypted secret envelope for a designated key. Reject plaintext secrets everywhere. No freeform JSON editor. Admin-owned typed policy contracts declare the field kind, validation, ranges, units and permission; the reusable editor renders those controls. Admin-002 adds five write-only secret contract variants to the same renderer, with a separate server-only secret write branch.
- Create with expected revision zero, update with matching revision, atomically increment version and append audit event with verified admin actor. Clearing/resetting is an update, never deletion or revision reset. Concurrent writes and stale replay fail.
- Runtime readers perform a fresh validated database read **for each relevant operation**. Do not add process-local/Redis configuration caches, TTL refresh loops, last-known-good snapshots or stale-value fallback. A single operation may reuse its own read; a subsequent operation must fetch again. Missing/invalid/unavailable required configuration fails closed. Authentication frameworks that capture secrets during bootstrap require an explicitly verified framework-supported loading/rotation strategy; do not claim they support live updates without proving it.
- Existing unrelated provider keys remain in their current approved stores; no plaintext credentials in `value` or credentials/ciphertext in audit logs. Service hard limits remain in code. SSRF restrictions stay service-owned.
- Avoid unrelated source/migration changes; roll out DATABASE-001, ADMIN-001 generic editor, ADMIN-002 secret import/bootstrap, independent consumers, Gateway cleanup, terminal System Test. Existing ARCH-039 Shared encryption is reused without change.

## Infrastructure and observability

API-003 remains a narrowly scoped private Meta secret-reader capability, with service identity enforced and no public access. **There is no Messaging consumer or private API-to-Messaging connection in ARCH-043.** Gateway must not remove Messaging webhook verification environment credentials as part of this initiative. Gateway edits only the existing Render Blueprint declarations after consumers complete. Shared structured logging emits key/revision and correlation without values containing credentials; existing framework and OpenTelemetry request telemetry should be reused rather than duplicated.

## Deployment classification and rollback

Treat existing service deployments and configuration state as requiring compatible rollout, not disposable. Database migration is additive. Admin/readers are deployed before env removal, and safe defaults/cutover tests are recorded. Securely import old secrets before cutover; preserve a restricted rollback path until every consumer verifies DB-backed bootstrap and credential rotation without exposing secrets. Roll back consumers without dropping historical configuration/audit tables; secret rollback/recovery requires the prior unseal key and encrypted record revisions as specified in the schema review.

## Execution graph

```text
  DATABASE-001
       |
       +------> ADMIN-001 ------> ADMIN-002 (secure secret import)
       |                             |
       +------> SHOPIFY-001 ---------+------> SHOPIFY-002
       |         server-only                 OAuth + Knowledge integration
       |         config service                      |
       |                                             v
       +------> other independent consumers     GATEWAY-001
       |                                             |
       +------> API-003 (private capability only)    v
       |                                          SYSTEM-TEST-001
       +------> other required work ---------------> (terminal)
```

There are **no new ARCH-043 Shared tasks**. All crypto operations use the already published ARCH-039 Node-only functions. The frozen configuration AAD bytes are `JSON.stringify(["moda-platform-config-v1", environment, key, resultingVersion, 1])` after strict identifier and revision validation, with no new package export. Writer/reader byte vectors are acceptance tests in the owning service tasks. `ADMIN-002` depends on the reusable editor from `ADMIN-001` but most consumer implementations can be built independently after the database task; **SHOPIFY-002 explicitly depends on SHOPIFY-001 and ADMIN-002** so its authenticated startup integration has the accepted reader and secure-import capability available. Activating any DB-only secret reader requires imported values and proven auth/secret bootstrap. Terminal System Test depends on all implementations, never the reverse.

## Task inventory

See `docs/architecture/ARCH-043-task-inventory.md` for authoritative portable task definitions and the dependency table. Task YAML is authoritative for task status. Status *ready* means eligible if definitions are materialised and dependencies re-gated; it does not assert a worktree or task branch was created.

## Open questions

- Confirm rollout environment and secure out-of-band injection of the independent config-unseal root or KMS identity; it cannot come solely from the protected database.
- Verify Shopify's module-initialisation contract supports an authenticated load-before-serve DB secret bootstrap. Do not remove OAuth environment inputs if this cannot be proven.
- API-003 is a purpose-scoped private capability only; no Messaging integration, service-to-service invocation from Messaging, or removal of Messaging webhook secrets is authorised under ARCH-043. Any later consumer requires separate architectural approval.
- Determine exact Auth.js/Shopify/Meta rotation compatibility and safe rollback. Never silently allow a keyless or unauthenticated mode.

- Confirm approved per-environment defaults/activation for R2 storage, since endpoint/bucket must not be fabricated. Endpoint and bucket are editable; storage relocation and in-flight asset protection belong to already separate tasks.
- Confirm whether worker concurrency can be adjusted live or requires a worker restart; preserve existing BullMQ correctness.
- Confirm if support-message translation already has equivalent database authority before creating a second policy key.

## Change history

- 17 October 2026: Removed only the Messaging runtime integration task. `messaging.meta` encrypted storage, Admin controls and API-003 definition remain. Messaging environment verification credentials are retained. Per-operation database reads replace configuration caching, and R2 endpoint/bucket remain editable with relocation owned elsewhere.


- 17 October 2026: developer explicitly adds Commerce keyring/active ID, Admin/Commerce AUTH_SECRET, Shopify OAuth and Meta verification secrets to encrypted database management. No additional Prisma model; one independent external unseal root or KMS identity required. Expanded repository consumer tasks.


- 17 October 2026: removed ARCH-043 Shared implementation/publication tasks as redundant; defined one contract-driven Admin editor (ADMIN-001), one write-only secret/bootstrap extension (ADMIN-002), frozen the AAD bytes in architecture, and rewired downstream dependencies to DATABASE-001.
