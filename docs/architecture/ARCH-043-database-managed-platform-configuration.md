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

## 17 October 2026 — Source-backed environment-variable reconciliation (controlling addendum)

**Source boundary:** `moda-interact-workspace(20261017-165350).zip`, excluding the runtime/source trees in `moda-interact-system-test` and `moda-interact-documentation`; the later parent `moda-interact-workspace-ARCH-043-ADMIN-002(2).zip` supplies task metadata. The automated filtered inventory contains 130 distinct names, of which **23 are candidates for this decision**, not 23 new persisted keys. The live deployment has not been inspected; task status remains governed by individual YAML files. Previously superseded task drafts (`BACKGROUND-007`, `API-003-woo-billing...`, etc.) are *not* reactivated.

### Decision matrix (23 candidate environment names)

| Domain / count | Evidence (actual readers) | Disposition | Canonical DB owner / follow-up |
|---|---|---|---|
| Woo billing (3) | `moda-interact-api/src/woocommerce/billing/woo-billing-config.ts` | **2 secrets migrate:** `WOO_BILLING_API_KEY`, `WOO_BILLING_API_SECRET`; `WOO_BILLING_ENVIRONMENT` **stays deployment-owned** (`sandbox`/`production`) | `woocommerce.billing`; API-004 |
| Shopify Partner (5) | `moda-interact-admin/src/lib/admin/shopify-subscription-contract.ts`, `moda-interact-background/src/providers/shopify-partner-billing.provider.ts`, `moda-interact/app/services/billing/providers/shopify-billing.provider.ts` | Merge the token and org-ID *aliases* into one typed tuple; API version remains an optional field within that tuple | `shopify.partner`; ADMIN-004, BACKGROUND-009, SHOPIFY-003 |
| Shopify App Events (2) | `moda-interact-background/src/providers/shopify-app-events.provider.ts` | Dedicated identity/secret, not a surrogate for Shopify OAuth or Partner credentials | `shopify.appEvents`; BACKGROUND-009 |
| WhatsApp outbound sender (3) | `moda-interact-background/src/services/whatsapp.service.ts` and `whatsapp-media.service.ts` | Migrate outbound token + phone-number ID + business-account ID together; **not** Meta webhook verification | `messaging.sender`; BACKGROUND-009 |
| Speech provider API credentials (2) | `moda-interact-background/src/services/speech-transcription.service.ts` | Migrate the Groq and OpenAI **speech** keys to `ai.providers`; existing `CommerceTranslationProviderCredential` and enabled automatic translation model remain authoritative for support-message translation | `ai.providers`; BACKGROUND-008/009 and BACKGROUND-001 |
| Commerce cursor signing (1) | `moda-interact-commerce/src/commerce/preview/local-policy-providers.ts`, `moda-interact-mcp/src/runtime/prisma.ts` | **Defer**: cross-service same-key revision, signed cursor expiry/rotation and failure/cursor compatibility must be agreed before moving the signing root. No new task yet | `COMMERCE_CURSOR_SECRET` stays external |
| Existing embedding configuration (5) | `moda-interact-admin/src/lib/admin/shopify-taxonomy-embedding.ts`; `moda-interact-database/prisma/schema.prisma` (`CommerceEmbeddingConfiguration`); Background merchant-knowledge resolver | **Do not copy into PlatformConfiguration**. `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_INDEX_VERSION`, `EMBEDDING_API_KEY`, `SHOPIFY_TAXONOMY_EMBEDDING_DIMENSIONS` need a bounded legacy-taxonomy reader reconciliation with existing `REFERENCE_TAXONOMY` purpose, outside this secret-catalogue wave | Existing `CommerceEmbeddingConfiguration` remains authoritative; no new generic secret key |
| Shopify application ID (1) | Background Partner provider and Admin/Shopify billing provider | Include `SHOPIFY_APP_ID` as the app identity field in the same `shopify.partner` record; do not create `shopify.appId` | `shopify.partner` |

**Counts:** 16 environment names moved into **five sealed configuration records** (2 Woo billing + 5 Partner aliases/version + 2 App Events + 3 WhatsApp sender + 3 AI keys + 1 Shopify App ID), 1 retained external (`WOO_BILLING_ENVIRONMENT`), 1 deferred (`COMMERCE_CURSOR_SECRET`), 5 delegated to existing embedding configuration. No new Prisma table or ARCH-043 Shared publication is approved.

### Contract and security decisions

- Five *new* sealed purposes: `woocommerce.billing`, `shopify.partner`, `shopify.appEvents`, `messaging.sender`, `ai.providers`, in addition to the eight existing expanded ARCH-043 purposes. Each row contains only the approved v1 sealed envelope or disabled tombstone; the decrypted JSON is typed/allowlisted by Admin and independently validated by its consumer. R2/merchant Woo shop connection credentials remain separate. Canonical encryption/AAD from ARCH-039/ARCH-043 are unchanged. No extra SQL key-list migrations: the developer reports a forward migration dropping the former closed secret-name constraint, **not yet verified from this source snapshot**; writing any of these keys must be gated on verifying the current migration and remaining constraints.
- `shopify.partner` plaintext schema for the encrypted bundle: `{ accessToken, organizationId, appId, apiVersion? }`; Admin's `SHOPIFY_PARTNER_API_TOKEN`/`SHOPIFY_PARTNER_ORGANIZATION_ID` are aliases of Background/Shopify names, not extra stored credentials. Verify optional API version handling in each consumer. Rotation should replace the *entire* partner identity snapshot atomically.
- `woocommerce.billing`: `{ apiKey, apiSecret }`, with the environment mode selected **only** from deployment `WOO_BILLING_ENVIRONMENT`. Do not permit a sandbox identity to sign production billing requests. `shopify.appEvents`: `{ clientId, clientSecret }`. `messaging.sender`: `{ accessToken, phoneNumberId, businessAccountId }`. `ai.providers`: `{ groqSpeechApiKey?, openAiSpeechApiKey? }` for speech alone, requiring the selected speech credential (no blank-string default). Support translation uses existing `CommerceTranslationProviderCredential`. All credentials stay server-side.
- The Admin secret editor is **authorised reveal/edit** (not permanently write-only): decrypt on explicit request, hide/discard client value afterward, preserve unchanged fields on CAS update, and redact audit/structured logs. First setup reason is automatic; rotate/revoke ask only their relevant reason. Development bypass may manage development secrets but never production secrets. Existing revisioned `PlatformConfigurationAudit` cannot record pure read events without incrementing a revision; reveal events use security-structured logging, **not** a fabricated audit row.
- Admin/Commerce authentication loads `auth.admin` / `auth.commerce` **only for authentication operations**, not at application boot. When *no database record exists*, use a complete corresponding environment credential bundle. If the row exists but is disabled, malformed or undecryptable, or a DB read fails, fail authentication rather than downgrade. `AUTH_URL` and the three corresponding authentication environment variables must remain present as intentional fallback; Gateway-001 must not remove them. Auth.js compatibility and session rotation remain consumer-owned proof obligations.
- Runtime readers must not use stale cached keys after rotation. One validated revision per provider action/job; no DB query in hot per-event/byte paths and no provider network call inside a configuration transaction. During rollout, environment-based consumer behaviour is retained until DB records/reader tests prove cutover; after **explicit** cutover, a configured but invalid row fails closed. Do not silently mix values from DB and environment in one credential tuple. Existing webhook ingress (`META_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN`) remains environment-based; provider base URLs/callback origins such as `MODA_WOO_REST_READ_PUBLIC_ORIGIN` remain deployment-owned.

### Execution graph and rollout constraints

**Background two-task boundary (controlling):** `BACKGROUND-008` produces a repository-local typed async `BackgroundPlatformCredentialResolver` with `resolveWhatsAppSender`, `resolveShopifyAppEvents`, `resolveShopifyPartner`, `resolveSpeechProvider("groq"|"openai")` and `resolveSupportTranslation`. Each returns `{ version, credentials }` with one validated decrypted immutable operation snapshot or a bounded redacted typed error. The environment is derived server-side, and resolution is DB-only; no per-provider runtime integration is included. `BACKGROUND-009` must **only consume that accepted contract** across the concrete source call sites and tests documented in its task definition: `whatsapp.service.ts`, `whatsapp-media.service.ts`, `shopify-app-events.provider.ts`, `shopify-usage-event-publisher.service.ts`, `shopify-partner-billing.provider.ts`, `speech-transcription.service.ts` and the correctly scoped `translation.provider.ts` invocation. App Events auth token caches must be version-aware. Background Merchant Pricing/Store Category translation credentials must not be redirected to the support-message key. Both tasks remain separate and individually reviewable. The older proposed `BACKGROUND-010..012` files are not part of this canonical wave; no replacements are created for them.

`ADMIN-002` owns registration/validation and protected authoring of the five additional encrypted keys as an **amendment of its existing developer-owned in-progress task**, not as a separate auth task. The five newly defined tasks (API-004, BACKGROUND-008 resolver services, BACKGROUND-009 consumers, SHOPIFY-003, ADMIN-004) are pending until their existing dependencies are Complete. Gateway-001 may retire **only consumer-specific** old variables after each owning consumer has verified DB operation; it must retain foundational/fallback environment configuration and must not remove webhook verifier secrets. SYSTEM-TEST-001 is terminal and now depends on all five additions (including resolver and consumers) and Gateway-001. No source edits in either excluded repository, no index edits, no branch/claim/commit assertions from the snapshot.

**Not yet authorised:** migration of `COMMERCE_CURSOR_SECRET` to database; rewriting existing `CommerceEmbeddingConfiguration`; new root/keyring schemes; replacing per-shop WooCommerce REST OAuth grants; an API-to-Messaging secret endpoint; moving callback/service origins or the deployment-selected Woo billing environment into PostgreSQL.

## Existing source and new schema

Based on the 17 October 2026 workspace snapshot and the environment audit. `moda-interact-database/prisma/schema.prisma` already contains typed durable business settings and an audited Background singleton. The only new Prisma models are:

1. `PlatformConfiguration`: `id`, `environment`, `key`, `value Json`, `version`, `updatedBy`, `createdAt`, `updatedAt`, unique `(environment,key)`.
2. `PlatformConfigurationAudit`: `id`, `environment`, `key`, `expectedVersion`, `resultingVersion`, `beforeValue Json?`, `afterValue Json`, `actorId`, `reason`, `createdAt`; unique `(environment,key,resultingVersion)`.

The exact proposed Prisma declarations, payload schemas and field bounds are in `docs/architecture/ARCH-043-configuration-schema-review.md`.

## Runtime configuration groups

| Key | Owner/consumer | Editable data | Keep external |
|---|---|---|---|
| `woo.couponSync` | Background | ten bounded coupon-worker numeric controls | Redis, DB, worker infrastructure |
| `speech.transcription` | Background | provider choice and model IDs | Groq/OpenAI API keys |
| `commerce.preview` | Commerce | deadlineMs and outputTokens | private service URLs, credentials, safety hard caps |
| `admin.grafana` | Admin | dashboard/navigation URLs | OTLP/LOKI transport and exporter credentials |

Existing database-backed domains are not copied into this table. All unlisted provider secrets remain with existing domain ownership, to avoid a bulk migration.

## Encrypted application secrets

The developer requested moving existing `COMMERCE_CONNECTION_KEYS_JSON` + active key ID, `AUTH_SECRET`, Shopify OAuth credentials, `META_APP_SECRET` and `WHATSAPP_VERIFY_TOKEN` to PostgreSQL. `PlatformConfiguration.value` holds a purpose-specific sealed envelope (AES-256-GCM), not a plaintext secret or an arbitrary string. The allowlisted purposes are `commerce.connectionKeys`, `auth.admin`, `auth.commerce`, `shopify.oauth`, `messaging.meta`. Existing Google OAuth client secrets may be included in their service-specific auth bundle; the Commerce command HMAC key may be bundled with its existing keyring where needed.

`PlatformConfigurationAudit` records secret update/revocation **metadata only**; no plaintext or replayable ciphertext. Approved reader paths use an independent deployment/KMS unwrap root; that root cannot be stored solely in the database it protects. The legacy Commerce keyring's authenticated-data and encrypted credential bytes must remain exactly compatible after moving the keyring itself to sealed configuration storage.

Bootstrap is explicit: one-time authenticated import before DB-only cutover; no browser or public webhook access to raw secret envelopes. Admin, Commerce and Shopify currently build authentication/Shopify clients from environment configuration, so their tasks must prove secure load-before-serve behaviour without an open authentication bypass. Messaging lacks a Prisma/PostgreSQL client in the 17 October snapshot. **ARCH-043 does not modify or integrate `moda-interact-messaging`**: it continues to use its existing `META_APP_SECRET` and `WHATSAPP_VERIFY_TOKEN` deployment configuration. The encrypted `messaging.meta` row, Admin secret form/import and purpose-scoped API-002 Meta resolver capability remain in scope, but none of them changes the Messaging runtime or authorises removal of its environment variables. Authentication/session rotation must follow concrete library/provider constraints, not invented grace behaviour.

## 18 October consolidation decision — one R2 owner and one translation owner (controlling)

This section supersedes older `merchantKnowledge.upload`, `support.translation`, `openAiTranslationApiKey` and `resolveSupportTranslation()` design statements elsewhere in ARCH-043. No new Prisma model, Shared publication or Background task is authorised. The accepted ADMIN-001 implementation and its task history remain intact; ADMIN-002 and existing consumer tasks own the *forward* retirement work.

### Merchant Knowledge R2 (single effective source)

- **Canonical:** sealed `PlatformConfiguration` key `merchant.knowledge.r2`, environment-scoped, six fields `{endpoint, bucket, accessKeyId, secretAccessKey, maxUploadBytes, maxXlsxUncompressedBytes}`. All fields are validated and versioned atomically. Admin exposes only the `merchant.knowledge.r2` editor; no legacy R2 policy, reconciliation, or retirement switch is created.
- **Migration precondition:** per environment, inspect the existing `merchantKnowledge.upload` revision and the existing `merchant.knowledge.r2` status. Copy its endpoint/bucket/limits only after validating them against current hard caps, obtain or verify the matching R2 credentials through authorised secret entry, and save one complete sealed record. Do not invent endpoint, bucket, size or secret defaults. If both records already contain divergent values, STOP for operator reconciliation rather than silently overwriting either. The `merchant.knowledge.r2` revision and audit entry must reflect the actual set/rotate; preserve old audit rows.
- **Consumer implementation:** API-001 reads one sealed R2 snapshot per upload intent/finalisation; Shopify-001 offers a server-only typed full R2 reader and SHOPIFY-002 uses it for upload operations; Background-002 handles any existing Background Knowledge use of R2. All three owners validate before using, preserve existing SSRF/HTTPS/bucket, upload-size, XLSX decompression, integrity and tenant checks; browser clients never receive R2 credentials. No split reads (`merchantKnowledge.upload` plus secret env), no silent fallback to the old record at runtime. Shopify must prove Node-only server access to the approved unseal material; if unavailable, return a bounded architectural dependency instead of shipping partial secrets.
- **Relocation:** a changed endpoint/bucket can make existing `objectKey`-only uploads unreachable. The separately owned relocation/in-flight-object policy remains a prerequisite for *changing* locations; configuration cutover must preserve existing objects and not assume old/new buckets are interchangeable.

### Translation (single existing credential/profile owner)

- **Canonical:** existing `CommerceTranslationProviderCredential` encrypted OpenAI secret plus `CommerceTranslationModelConfiguration` enabled profiles/automatic default, managed by **System Controls → Translations**. Keep both the existing UI and their persistence/audit models. Do not create a second OpenAI translation credential in `ai.providers` or independently editable provider/model in `support.translation`; exclude those two Platform Configuration keys from the clean registry.
- The `ai.providers` sealed bundle is **speech-only**, with optional `groqSpeechApiKey` and `openAiSpeechApiKey`; require at least one when creating that bundle and the specific key required by the selected speech provider. `speech.transcription` remains the separately managed speech provider/model policy.
- For a **new support-message translation job**, resolve an enabled **automatic default** translation profile in the correct Commerce environment and acquire the existing OpenAI credential via the already implemented Background resolver (`src/commerce/translation-provider-credential.ts`, ARCH-039 crypto). Validate the actual `CommerceEnvironment` mapping from deployment identity, provider, model and enabled state. Preserve the chosen model identity for existing queued/claimed batches; do not rewrite historical translation jobs on later default changes. If no valid default or credential exists, fail the support translation operation with bounded diagnostics, not a guessed model or `OPENAI_API_KEY` fallback.
- Do not change Merchant Pricing, Store Category or other translation workflow ownership merely because they share `translation.provider.ts`. BACKGROUND-001 owns the support-message policy/default integration; BACKGROUND-009 integrates approved callers and uses existing translation credential services, **not** the BACKGROUND-008 generic resolver for translation. Prove call-site isolation and add focused regression tests.
- **Fresh-database rule:** no `support.translation` record or compatibility reader exists. New support work uses the existing automatic translation model directly.

### Clean implementation and review sequence

1. ADMIN-002 exposes the final registry directly (four canonical policy groups, thirteen sealed purposes); no migration UI, legacy record handling, retirement flag or deferred tab removal.
2. API-001, Shopify-001/002 and any Background R2 consumer read the single `merchant.knowledge.r2` record with normal strict validation and fail-closed behaviour.
3. Background-001/009 use the existing Commerce translation credential and enabled automatic default. Do not introduce a second support translation policy or OpenAI translation key.
4. Gateway and terminal System Test validate only the canonical sources. This is a fresh pre-production database rollout, not a compatibility or historical-data conversion project.

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

## Hosted API two-stage implementation (API-001 / API-002)

1. `ARCH-043-API-001` builds a single **read-only, reusable hosted API configuration service** for `merchantKnowledge.upload`, `commerce.connectionKeys`, and `messaging.meta`; it owns trusted environment-scoped reads, strict validation and existing ARCH-039 decryption. It changes **no consumers or HTTP routing**, and introduces no cache.
2. `ARCH-043-API-002` applies that service to Merchant Knowledge reads/upload, Woo REST-read keyring start/callback/proofs and the previously agreed fixed-purpose private Meta resolver. It depends on accepted `API-001` **and `ADMIN-002`** (secure secret import), and includes no Messaging runtime integration or Messaging environment-secret removal. The private capability requires approved Gateway identity and fails closed when that identity is unavailable.

R2 endpoint and bucket remain editable; other tasks own migration/asset continuity. Existing R2 access credentials remain in their current protected store. The old `API-003` definition is consolidated into API-002, and obsolete task files with duplicated API IDs are retired from discovery. The 15-task set becomes **14 canonical tasks**.

## Consistency, transactions and security

- Trusted deployment identity determines `environment`; no client-controlled environment, prod/test fallback or cross-tenant leakage.
- `PlatformConfiguration.value` is a closed non-secret policy object OR a strict encrypted secret envelope for a designated key. Reject plaintext secrets everywhere. No freeform JSON editor. Admin-owned typed policy contracts declare the field kind, validation, ranges, units and permission; the reusable editor renders those controls. Admin-002 adds five write-only secret contract variants to the same renderer, with a separate server-only secret write branch.
- Create with expected revision zero, update with matching revision, atomically increment version and append audit event with verified admin actor. Clearing/resetting is an update, never deletion or revision reset. Concurrent writes and stale replay fail.
- Runtime readers perform a fresh validated database read **for each relevant operation**. Do not add process-local/Redis configuration caches, TTL refresh loops, last-known-good snapshots or stale-value fallback. A single operation may reuse its own read; a subsequent operation must fetch again. Missing/invalid/unavailable required configuration fails closed. Authentication frameworks that capture secrets during bootstrap require an explicitly verified framework-supported loading/rotation strategy; do not claim they support live updates without proving it.
- Existing unrelated provider keys remain in their current approved stores; no plaintext credentials in `value` or credentials/ciphertext in audit logs. Service hard limits remain in code. SSRF restrictions stay service-owned.
- Avoid unrelated source changes; implement DATABASE-001 schema, ADMIN-001 generic editor, ADMIN-002 final secret writer/request-time Auth.js reader, independent consumers, Gateway configuration, then terminal System Test. Existing ARCH-039 Shared encryption is reused without change.

## Infrastructure and observability

API-002 includes a narrowly scoped private Meta secret-reader capability, with service identity enforced and no public access. **There is no Messaging consumer or private API-to-Messaging connection in ARCH-043.** Gateway must not remove Messaging webhook verification environment credentials as part of this initiative. Gateway edits only the existing Render Blueprint declarations after consumers complete. Shared structured logging emits key/revision and correlation without values containing credentials; existing framework and OpenTelemetry request telemetry should be reused rather than duplicated.

## Deployment classification and rollback

This is a **fresh pre-production configuration** implementation. No configuration-data migration or legacy-key rollout is required. Keep ordinary Prisma schema migrations and schema constraints, but use only canonical Platform Configuration keys from the first deployment. Admin registers the final keys directly; consumers adopt them without reading historical configuration rows. Preserve independent deployment secrets, including absent-row Auth.js environment fallback, and validate consumer wiring before Gateway removes superseded environment values.

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
       +------> API-002 (private Meta capability only)    v
       |                                          SYSTEM-TEST-001
       +------> other required work ---------------> (terminal)
```

There are **no new ARCH-043 Shared tasks**. All crypto operations use the already published ARCH-039 Node-only functions. The frozen configuration AAD bytes are `JSON.stringify(["moda-platform-config-v1", environment, key, resultingVersion, 1])` after strict identifier and revision validation, with no new package export. Writer/reader byte vectors are acceptance tests in the owning service tasks. `ADMIN-002` depends on the reusable editor from `ADMIN-001` but most consumer implementations can be built independently after the database task; **SHOPIFY-002 explicitly depends on SHOPIFY-001 and ADMIN-002** so its authenticated startup integration has the accepted reader and secure-import capability available. Activating any DB-only secret reader requires imported values and proven auth/secret bootstrap. Terminal System Test depends on all implementations, never the reverse.

## Task inventory

See `docs/architecture/ARCH-043-task-inventory.md` for authoritative portable task definitions and the dependency table. Task YAML is authoritative for task status. Status *ready* means eligible if definitions are materialised and dependencies re-gated; it does not assert a worktree or task branch was created.

## Open questions

- Confirm rollout environment and secure out-of-band injection of the independent config-unseal root or KMS identity; it cannot come solely from the protected database.
- Verify Shopify's module-initialisation contract supports an authenticated load-before-serve DB secret bootstrap. Do not remove OAuth environment inputs if this cannot be proven.
- API-002 includes a purpose-scoped private capability only; no Messaging integration, service-to-service invocation from Messaging, or removal of Messaging webhook secrets is authorised under ARCH-043. Any later consumer requires separate architectural approval.
- Determine exact Auth.js/Shopify/Meta rotation compatibility and safe rollback. Never silently allow a keyless or unauthenticated mode.

- Confirm approved per-environment defaults/activation for R2 storage, since endpoint/bucket must not be fabricated. Endpoint and bucket are editable; storage relocation and in-flight asset protection belong to already separate tasks.
- Confirm whether worker concurrency can be adjusted live or requires a worker restart; preserve existing BullMQ correctness.
- Confirm if support-message translation already has equivalent database authority before creating a second policy key.

## Change history

- 17 October 2026: Removed only the Messaging runtime integration task. `messaging.meta` encrypted storage, Admin controls and API-002 private resolver scope remain. Messaging environment verification credentials are retained. Per-operation database reads replace configuration caching, and R2 endpoint/bucket remain editable with relocation owned elsewhere.


- 17 October 2026: developer explicitly adds Commerce keyring/active ID, Admin/Commerce AUTH_SECRET, Shopify OAuth and Meta verification secrets to encrypted database management. No additional Prisma model; one independent external unseal root or KMS identity required. Expanded repository consumer tasks.


- 17 October 2026: removed ARCH-043 Shared implementation/publication tasks as redundant; defined one contract-driven Admin editor (ADMIN-001), one write-only secret/bootstrap extension (ADMIN-002), frozen the AAD bytes in architecture, and rewired downstream dependencies to DATABASE-001.

## 17 October 2026 extension: bootstrap identity, R2 and platform WooCommerce secrets

The developer confirmed Auth.js credentials may be database-backed when PostgreSQL is available before authenticated startup. Preserve `auth.admin` and `auth.commerce` as sealed purposes (environment OAuth values only during transitional import), not as permanent environment exclusions. `AUTH_URL`, database connection, service identity and `MODA_CONFIG_UNSEAL_*` remain external. A controlled, authenticated import must precede switching Auth.js to DB-only, and cold-start failure/rotation must fail closed. An existing environment-authenticated SUPER_ADMIN can perform initial import while the old deployment is still live; do not claim a browser-login-independent recovery route unless it is independently authenticated.

Add `commerce.bootstrap` as an independently sealed `{adminEmail}` selector mapped from `COMMERCE_BOOTSTRAP_ADMIN_EMAIL`. Commerce verifies the configured email matches exactly one active SUPER_ADMIN; it is not a replacement for authentication or authorisation. Never hardcode a real operator address as a source default.

Add `merchant.knowledge.r2` as ONE encrypted JSON object containing `{endpoint,bucket,accessKeyId,secretAccessKey,maxUploadBytes,maxXlsxUncompressedBytes}` (the limits are JSON integers). All six values are atomically versioned. The older `merchantKnowledge.upload` policy is not part of the canonical registry; adapt API-001, BACKGROUND-002 and SHOPIFY-001/002 to the single sealed source and existing hard caps/SSRF protection. API and Background must use the published ARCH-039 Node crypto, not Shopify client/browser code. Existing object relocation remains separately owned.

Add `woocommerce.auth` as a sealed platform-owned `{consumerKey,consumerSecret}` pair. The inspected WooCommerce read-auth implementation uses shop-specific credentials already persisted under each merchant's grants. Do not replace those, create global cross-tenant credentials, or migrate unrelated grant envelopes. No Woo runtime consumer or Gateway environment removal is approved until a concrete platform-owned consumer is identified.

DATABASE-001 originally introduced two key-specific secret CHECK allowlists. The developer reports having authored a forward migration to remove those restrictions; this migration must be verified and applied before enabling writes to the three additional purposes. No `ARCH-043-DATABASE-002` task will be created. Database generic integrity, uniqueness and append-only audit remain required. Secret purpose allowlisting, sealed-value validation and redacted audit enforcement are now owned by authorised server-side writers/readers; prohibit untrusted direct SQL writes and document the reduced database-level defence in depth. `ARCH-043-ADMIN-002` owns the Admin secret writer **and** its Auth.js DB-backed cutover; Commerce's equivalent is within COMMERCE-001/002. Complete system tests only after the consumers' actual source changes, validation and approved rollout. No `_index.md` change in this decision patch.

Admin Auth.js bootstrap and DB-only cutover remain inside `ARCH-043-ADMIN-002`; no additional Admin authentication cutover task is created.
