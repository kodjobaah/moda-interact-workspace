---
id: ARCH-043
title: Database-managed platform runtime configuration and protected provider credentials
status: agreed
coordinator: moda_architect
created: 2026-10-17
updated: 2026-10-17
---

# ARCH-043: Database-managed platform runtime configuration and protected provider credentials

## Status

**Agreed — portable task definitions only.** The architecture extends the 17 October 2026 environment audit. `ARCH-042` is intentionally left unallocated in this snapshot because the developer has discussed that identifier for WooCommerce promotions. This proposal does **not** reserve or create Git task branches on the developer's workstation. Task definitions in this patch are **defined but not materialised** and their `ready` metadata represents logical dependency eligibility after the definitions are materialised and regated.

**Documentation-session rule:** do not create or modify `docs/decisions/**/_index.md` or `docs/architecture/_index.md` until the developer explicitly confirms the architectural session is complete.

## Problem

Moda Interact configures many operational policies through `process.env` in API, Shopify, Background, Commerce and Admin, requiring deployment edits for business policy changes. Some configuration already resides in typed/versioned PostgreSQL models, particularly `BackgroundRuntimeConfig`, `CommerceEmbeddingConfiguration`, `CommerceTranslationModelConfiguration`, `PlatformBillingPolicy`, `ShopFeaturePreference` and provider credential records. Uncoordinated migration would duplicate authority, expose secrets, couple service bootstrap to the database, or regress high-throughput event handling.

The audit found **236 candidate environment-variable names**, including 97 development/test names, 63 bootstrap/deployment names, 23 likely typed DB policy candidates, 16 existing DB/reconcile candidates, 12 possible encrypted provider credentials, four environment-specific location candidates and 21 review/retain candidates. This is a **static inventory**, not a count of production variables.

## Goals

1. Move appropriate editable application policies and provider/model choices to typed versioned PostgreSQL configuration with Admin authorisation, compare-and-swap and durable audit history.
2. Reuse ARCH-014 Background config machinery and ARCH-039 Shared Node credential encryption, keyring and immutable AAD conventions; avoid generic catch-all JSON configuration and duplicate parsers.
3. Move eligible API, Background and internal provider credentials into encrypted environment-scoped DB records with explicit purpose, rotation and fail-closed readers.
4. Keep application runtime fast: non-overlapping snapshot refresh, bounded caches, per-operation consistency, last-known-good on transient refresh failure **only after a valid snapshot**.
5. Remove obsolete Render environment declarations only after all relevant consumers have switched and accepted independent test evidence.
6. Validate test/production isolation and provider/tenant authorisation with integrated system tests.

## Non-Goals

- Moving bootstrap `DATABASE_URL`, Redis URLs, `PORT`, host/upstream routing, `NODE_ENV`, deployment identity, OAuth/session/webhook signature secrets, Shopify application secrets, Meta webhook verify token, OpenTelemetry exporter transport or ARCH-039 keyring/HMAC roots into PostgreSQL.
- Moving test runners, local WordPress/LocalWP/CLI variables, disposable database setup, development paths and demo tooling into persistent app configuration.
- Making merchant-controlled WordPress plugin connect directly to Moda PostgreSQL or receive provider keys.
- Making Shopify browser/merchant app an ARCH-039 keyring decryptor. Shopify R2 write credentials remain externally managed until a separately approved hosted signing path exists. Do not grant keyring rights to Shopify merely to eliminate two env keys.
- Replacing existing merchant/feature-plan/billing state with global policies or changing unrelated runtime algorithms.

## Current Architecture — inspected sources

| Workload | Current evidence | Durable owner/reuse decision |
|---|---|---|
| Background controls | `moda-interact-database/prisma/schema.prisma` BackgroundRuntimeConfig + audit; `moda-interact-background/src/runtime/background-runtime-config.ts` | Extend existing singleton for coupon controls; do not duplicate |
| Woo coupon sync | `moda-interact-background/src/services/woo-coupon-sync-config.ts`, `src/workers/woo-coupon-sync.worker.ts` | DB-backed ten bounded knobs; keep ARCH-036 dispatcher lease |
| Merchant Knowledge storage | `moda-interact-background/src/services/merchant-knowledge-r2-config.ts`; Shopify `app/services/merchant-knowledge/r2-config.server.ts`; API `src/merchant/merchant-knowledge/upload-r2.ts` | One versioned policy/location contract across consumers; credential purposes separate |
| Speech | `moda-interact-background/src/services/speech-transcription.service.ts` | Typed selection, independently encrypted provider credentials |
| Support translation | Background `src/services/translation-batch-assembly.service.ts` and `src/providers/translation.provider.ts` | Do not conflate support message translation with Commerce's existing translation model configurations |
| Preview | `moda-interact-commerce/src/commerce/preview/run-budgets.ts` | Typed budget policy with code hard ceiling |
| Grafana links | `moda-interact-admin/src/lib/observability/grafana.ts` | Navigation URL policy only; NOT OpenTelemetry transport |
| Woo billing | `moda-interact-api/src/woocommerce/billing/woo-billing-config.ts` | DB encrypted pair, deployment WOO_BILLING_ENVIRONMENT remains external |
| Credential security | `docs/architecture/ARCH-039-canonical-credential-security.md` | Reuse only three canonical root env variables and published Node-only crypto; no new root aliases |
| Render deployment | `moda-interact-gateway/render.test.yaml`, `render.production.yaml` | Stage removals, separately inspect test vs production |

## Proposed Architecture

```text
                   Platform Admin (privileged CAS + audit)
                                 |
                                 v
              PostgreSQL environment-scoped typed policies
                 |                   |                   |
     BackgroundRuntimeConfig  Knowledge/AI policies   Encrypted provider
         (existing)              (new typed)          credential records
                 |                   |                   |
                 +----------+--------+-------------------+
                            |
                validated versioned snapshots
                            |
         +------------------+------------------+
         |                  |                  |
  Background workers   Merchant API     Commerce/Shopify Node server
         |                  |                  |
  bounded local read   authorised read   policy-only Shopify read
         |                  |                  |
         +----------- no per-event database lookup -----------+

        External bootstrap / Render secret manager (retained)
        DB URL, Redis, auth, Meta ingress, deployment identity,
        COMMERCE_CONNECTION_KEYS_JSON, writer active key and
        Commerce command HMAC; OTEL transport and Shopify R2 write keys
```

### Configuration ownership and classification

- **Policy:** typed table or existing domain table, immutable revisioned snapshot, CAS updates and independent deployment-environment identity. No arbitrary user-managed key names or mutable config JSON blob.
- **Provider credentials:** ciphertext envelope with environment/purpose/provider, active revision, bounded read cache, writer-side external ARCH-039 active-key selection and reader-side envelope key-ID lookup. Never return plaintext from admin read routes or logs.
- **Bootstrap:** external deployment config for DB, Redis, encryption roots, startup identity, ingress/auth, network and observability transport.
- **Merchant-side local:** WordPress API origin, CA bundle and connection mode remain on the merchant installation. Merchant product/plan preferences remain their existing DB records, not these global policies.

### Scope, environment and failure invariants

1. No database lookup in Shopify webhook acceptance, Meta webhook acknowledgement, each BullMQ event, each spreadsheet byte or model token; observe version changes with bounded refresh. Reuse ARCH-014 patterns wherever the Background process already has them.
2. Config edits require platform admin identity, expected monotonic version, reason and atomic audit. Distinct environments never fall back to each other's rows or credentials. Runtime readers ignore older revisions.
3. On cold start with missing/invalid required policy, the protected capability fails closed. After a valid startup snapshot, transient refresh error retains last-known-good under bounded monitoring; revoked credentials may not be used indefinitely under cache refresh failure and must use explicit credential-expiry/revocation policy.
4. Maintain immutable per-operation policy and credential snapshot for every R2 finalisation, outbound send, transcription job, coupon scan and preview run. Existing durable identifiers, charging and retry semantics do not change.
5. Keep hard safety maximums in code even where operator-selectable limits are DB-managed. Dynamic policy cannot disable SSRF/network validation or tenant checks.
6. Credential encryption uses only ARCH-039 Shared Node-only crypto and the external keys `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` (writers), `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` (Commerce command signer only). New domain AAD is encoded in Shared and published before readers and writers adopt it.
7. No second independent fallback authority after cutover. A bounded migration window may read old environment settings **only if separately documented, time-limited and explicitly opted in at deployment**, never as an unlogged silent fallback. Do not delete live credentials or durable state as part of a Blueprint cleanup.

## Data Model and Transactions

- Extend `BackgroundRuntimeConfig(id=default)` with ten Woo coupon operational fields using existing version/audit mutation contract; do not reimplement the lease or queue concurrency semantics.
- Typed environment-keyed records for Merchant Knowledge upload and nonsecret R2 location, speech provider selection, support-message translation selection (only if genuinely distinct), Commerce preview budgets and Grafana navigation links. Exact model naming is database-owner scope.
- Separate encrypted R2, speech provider, outbound WhatsApp and Woo billing credential records, environment/purpose/provider scoped, with current active revision and audit. Credential plaintext never stored or audited; ARCH-039 domain-bound AAD protects immutable identity/bytes.
- Admin CAS and audit commit atomically. No Redis/external provider operations inside a DB mutation transaction. Consumers apply accepted versions monotonically.
- Initial seed: preserve existing effective defaults for bounded nonsecret policy where safe. R2 location, credential values and provider account identity require explicit verified operator input; never seed fabricated secrets, URLs or test/production identities.

## Contracts and Cross-Repository Ownership

- `ARCH-043-SHARED-001` owns browser-safe Merchant Knowledge policy DTO/runtime validation and `SHARED-002` its publication. API, Background and Shopify import the published package (`@modainteract/moda-interact-shared`) at their own consumer tasks.
- `ARCH-043-SHARED-003` owns Node-only provider credential AAD byte contracts for new encrypted provider records; `SHARED-004` publishes it for Admin credential writers and API/Background credential readers. Generic AEAD itself is reused from accepted ARCH-039 without forks.
- Database/Prisma owns durable schema and migrations; Admin owns operator mutation/auth/audit UI; Background owns worker consumers; API owns hosted Woo-facing reads and signing; Shopify owns Shopify merchant-server use; Commerce owns previews; Gateway owns Render Blueprint wiring; System Test owns integrated certification.
- Shared DTO revision/version is producer-validated before use; a newly published contract requires explicit consumer dependency version and tests. Published Node-only encryption primitives must not become browser imports.

## Rollout / Migration

**Compatible staged rollout**, because provider keys, live credentials, existing Merchant Knowledge assets and deployment data may exist. Do not assume pre-production or destroy state.

1. Define/migrate policy models and audit. Prepare/admin-populate environment-specific rows using existing safe defaults and explicit R2/provider identity verification. Verify database availability and safe rollback.
2. Publish Shared Knowledge policy validator; enable Admin versioned edits; adopt on API/Background/Shopify/Commerce with independent code/tests. Keep old environment declarations until all consumers accepted; no two active authorities.
3. Switch Woo coupon, speech selection, support translation, preview and Grafana display consumers; then Gateway removes verified obsolete nonsecret env keys.
4. Separate phase: publish Shared provider AAD; add encrypted database credential tables and privileged Admin write-only mutation; enter valid per-environment credentials using audited rotation rather than silently reading secrets into a migration script.
5. Roll out API/Background decryptors, prove valid/wrong-revision/wrong-key/rotation/revocation and tenant/role boundaries; remove only their migrated provider secret env assignments. Shopify R2 write secrets remain external pending a distinct reviewed hosted signing architecture. Retain all required ARCH-039 root secrets and Meta webhook ingress secrets.
6. Developer manual validation checkpoint (not a task dependency), then terminal black-box system-test tasks and final architect signoff. Rollback never restores an environment override after its authority is removed without a deliberate audited operator recovery path.

## Infrastructure and Observability

New hosted service or queue not required. Render Gateway owns staged Blueprint reduction, environment-specific secret group validation and rollback. Admin editor and Background cache operations use existing Shared structured logging and OTel instrumentation; do not add generic HTTP telemetry duplicates. Emit bounded config version observation/refresh failures, credential rotation/revocation failure reason codes and provider-operation denial, without ciphertext/secret values. Telemetry transport and environment identity remain independent of application configuration and failure-isolated.

## Dependency graph

```text
           DATABASE-001 (Knowledge) ---> SHARED-001 ---> SHARED-002 (publish)
                      |                                  |
                      +-------------------------------+--+----> ADMIN-001
                      |                               +-------> API-001
                      |                               +-------> BACKGROUND-002
                      |                               +-------> SHOPIFY-001

 DATABASE-002 (Woo coupon) ------> ADMIN-002, BACKGROUND-001
 DATABASE-003 (Speech choice) ---> ADMIN-003, BACKGROUND-003
 DATABASE-004 (Preview budget) --> ADMIN-004, COMMERCE-001
 DATABASE-005 (Grafana) --------> ADMIN-005
 DATABASE-006 (Support translation) -> ADMIN-006, BACKGROUND-004

 SHARED-003 (credential AAD) ---> SHARED-004 (publish)
       |                              |
 DATABASE-007/008/009/010 -----------+----> ADMIN-007..010
       |                              +----> API-002, API-003
       |                              +----> BACKGROUND-005..007

 nonsecret consumer/admin acceptance -------> GATEWAY-001
                                                |
                                                v
                                           SYSTEM-TEST-001

 secret consumer/admin acceptance ----------> GATEWAY-002
                                                |
                                                v
                                           SYSTEM-TEST-002
```

**Hard invariant:** no database, Shared, Admin, Background, API, Shopify, Commerce, Gateway or publication task depends on any SYSTEM-TEST task. Shopify and Woo/API branches have no artificial cross-dependency: each consumes Shared/Database as appropriate. The credential phase is independently gated by Shared publication, per-domain schema and existing nonsecret consumer readiness where necessary.

## Decisions / Tasks

| Task | Owner | Status at definition | Depends On |
|---|---|---|---|
| `ARCH-043-DATABASE-001` | `moda_database` | Ready | — |
| `ARCH-043-DATABASE-002` | `moda_database` | Ready | — |
| `ARCH-043-DATABASE-003` | `moda_database` | Ready | — |
| `ARCH-043-DATABASE-004` | `moda_database` | Ready | — |
| `ARCH-043-DATABASE-005` | `moda_database` | Ready | — |
| `ARCH-043-DATABASE-006` | `moda_database` | Ready | — |
| `ARCH-043-DATABASE-007` | `moda_database` | Ready | — |
| `ARCH-043-DATABASE-008` | `moda_database` | Ready | — |
| `ARCH-043-DATABASE-009` | `moda_database` | Ready | — |
| `ARCH-043-DATABASE-010` | `moda_database` | Ready | — |
| `ARCH-043-SHARED-001` | `moda_shared` | Ready | — |
| `ARCH-043-SHARED-002` | `moda_shared` | Pending | `ARCH-043-SHARED-001` |
| `ARCH-043-SHARED-003` | `moda_shared` | Ready | — |
| `ARCH-043-SHARED-004` | `moda_shared` | Pending | `ARCH-043-SHARED-003` |
| `ARCH-043-ADMIN-001` | `moda_admin` | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-ADMIN-002` | `moda_admin` | Pending | `ARCH-043-DATABASE-002` |
| `ARCH-043-ADMIN-003` | `moda_admin` | Pending | `ARCH-043-DATABASE-003` |
| `ARCH-043-ADMIN-004` | `moda_admin` | Pending | `ARCH-043-DATABASE-004` |
| `ARCH-043-ADMIN-005` | `moda_admin` | Pending | `ARCH-043-DATABASE-005` |
| `ARCH-043-ADMIN-006` | `moda_admin` | Pending | `ARCH-043-DATABASE-006` |
| `ARCH-043-ADMIN-007` | `moda_admin` | Pending | `ARCH-043-DATABASE-007`, `ARCH-043-SHARED-004` |
| `ARCH-043-ADMIN-008` | `moda_admin` | Pending | `ARCH-043-DATABASE-008`, `ARCH-043-SHARED-004` |
| `ARCH-043-ADMIN-009` | `moda_admin` | Pending | `ARCH-043-DATABASE-009`, `ARCH-043-SHARED-004` |
| `ARCH-043-ADMIN-010` | `moda_admin` | Pending | `ARCH-043-DATABASE-010`, `ARCH-043-SHARED-004` |
| `ARCH-043-BACKGROUND-001` | `moda_background` | Pending | `ARCH-043-DATABASE-002` |
| `ARCH-043-BACKGROUND-002` | `moda_background` | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-BACKGROUND-003` | `moda_background` | Pending | `ARCH-043-DATABASE-003` |
| `ARCH-043-BACKGROUND-004` | `moda_background` | Pending | `ARCH-043-DATABASE-006` |
| `ARCH-043-BACKGROUND-005` | `moda_background` | Pending | `ARCH-043-DATABASE-007`, `ARCH-043-SHARED-004`, `ARCH-043-BACKGROUND-002` |
| `ARCH-043-BACKGROUND-006` | `moda_background` | Pending | `ARCH-043-DATABASE-008`, `ARCH-043-SHARED-004`, `ARCH-043-BACKGROUND-003` |
| `ARCH-043-BACKGROUND-007` | `moda_background` | Pending | `ARCH-043-DATABASE-009`, `ARCH-043-SHARED-004` |
| `ARCH-043-API-001` | `moda_api` | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-API-002` | `moda_api` | Pending | `ARCH-043-DATABASE-007`, `ARCH-043-SHARED-004`, `ARCH-043-API-001` |
| `ARCH-043-API-003` | `moda_api` | Pending | `ARCH-043-DATABASE-010`, `ARCH-043-SHARED-004` |
| `ARCH-043-SHOPIFY-001` | `moda_app` | Pending | `ARCH-043-DATABASE-001`, `ARCH-043-SHARED-002` |
| `ARCH-043-COMMERCE-001` | `moda_commerce` | Pending | `ARCH-043-DATABASE-004` |
| `ARCH-043-GATEWAY-001` | `moda_gateway` | Pending | `ARCH-043-ADMIN-001`, `ARCH-043-ADMIN-002`, `ARCH-043-ADMIN-003`, `ARCH-043-ADMIN-004`, `ARCH-043-ADMIN-005`, `ARCH-043-ADMIN-006`, `ARCH-043-BACKGROUND-001`, `ARCH-043-BACKGROUND-002`, `ARCH-043-BACKGROUND-003`, `ARCH-043-BACKGROUND-004`, `ARCH-043-API-001`, `ARCH-043-SHOPIFY-001`, `ARCH-043-COMMERCE-001` |
| `ARCH-043-GATEWAY-002` | `moda_gateway` | Pending | `ARCH-043-ADMIN-007`, `ARCH-043-ADMIN-008`, `ARCH-043-ADMIN-009`, `ARCH-043-ADMIN-010`, `ARCH-043-BACKGROUND-005`, `ARCH-043-BACKGROUND-006`, `ARCH-043-BACKGROUND-007`, `ARCH-043-API-002`, `ARCH-043-API-003` |
| `ARCH-043-SYSTEM-TEST-001` | `moda_system_test` | Pending | `ARCH-043-GATEWAY-001` |
| `ARCH-043-SYSTEM-TEST-002` | `moda_system_test` | Pending | `ARCH-043-GATEWAY-002` |

## Open Questions / Explicit gates

- Confirm target environment, initial R2 endpoints/buckets, policy values and provider identities when tasks materialise; these are not present in a static snapshot and must not be invented.
- Shopify R2 write-key migration is **not authorised** in this architecture: ARCH-039 forbids keyring distribution to the merchant app. If removing those remaining keys becomes mandatory, agree a separate hosted-upload-signing architecture and task set with tenant-authenticated hosted API boundary before touching it.
- ARCH-039 system-test certification is still pending in this snapshot; its accepted Shared/consumer code may be reused, but new credential system certification must include any consequences of outstanding ARCH-039 integration findings.
- Embedded/provider workflow coverage must be checked before deprecating any `EMBEDDING_*` names. Existing `CommerceEmbeddingConfiguration` is already database owned; do not create duplicate work based on static references alone.
- Confirm whether support-message translation can safely reuse an existing DB model in DATABASE-006; if equivalent authority exists, do not create a second row, record evidence and narrow tasks accordingly.
- Determine deployment compatibility for any legacy in-flight R2 finalisation and WhatsApp message before live cutover.

## Change History

- **2026-10-17:** Defined typed DB runtime policy + encrypted provider credential migration, 236-variable audit classification, task graph and staged deployment; no `_index.md` edits, worktrees or Git remote operations.
