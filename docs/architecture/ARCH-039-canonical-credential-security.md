---
id: ARCH-039
title: Canonical hosted credential security and Render secret configuration
status: agreed
coordinator: moda_architect
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-039: Canonical hosted credential security and Render secret configuration

## Status

Agreed for task definition; task files have been prepared from the 2026-10-14 workspace snapshot. No implementation has been accepted or started by this definition. The developer explicitly plans to clear non-production encrypted data before cutover. This architecture is not authorised to delete any durable data itself.

## Problem

Multiple hosted Node.js services independently parse `COMMERCE_CONNECTION_KEYS_JSON` with incompatible key-ID bounds and different treatment of missing keyrings. Admin, Background, Commerce, MCP and API also duplicate AES-256-GCM and/or credential-envelope handling. The Woo REST-read API additionally consumes `MODA_WOO_REST_READ_KEYRING` and `MODA_WOO_REST_READ_ACTIVE_KEY_ID` (base64url) even though Background must decrypt the corresponding grants through the Commerce keyring (canonical base64). Operators therefore manage separate encodings of the same key bytes, and code can drift on cryptographic validation and failure behaviour.

The uploaded Gateway Blueprints already expose `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` through separate secret groups and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` as a Commerce-only secret. The task is to complete and enforce this existing architecture, **not** invent another secret-store mechanism.

## Goals

1. One published, Node-only implementation of credential keyring parsing, active-key selection, bounded authenticated AES-256-GCM encrypt/decrypt, and safe envelope validation in `@modainteract/moda-interact-shared`.
2. Exactly one canonical hosted encryption-key configuration contract: `COMMERCE_CONNECTION_KEYS_JSON` (JSON map of **standard-base64** 32-byte keys) and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` (writer selector). Key IDs are restricted to `[A-Za-z0-9_-]{1,64}`; keyring has 1–16 distinct entries; each encoded value is canonical padded standard Base64 for exactly 32 bytes. No URL-safe encoding or alternate keyring configuration.
3. One separate Commerce connection-command HMAC configuration: `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`, canonical padded standard Base64 encoding of 32 independent bytes, decoded/validated explicitly; never repurpose encryption bytes as an HMAC key or expose it to non-owners.
4. Shared, domain-bound authenticated-data builders where the same persisted credential is written/read by different services (including the embedding credential and Woo REST-read grant). Preserve existing cross-service OpenRouter and translation AAD contracts in Shared.
5. No independent local crypto primitives or locally maintained clones for the in-scope hosted credential paths; callers own authorisation, data access, provenance, provider constraints, and safe domain error mapping.
6. Gateway governs Render secret distribution for actual writers/readers, with environment isolation and automated least-privilege checks.
7. Prove cross-service compatibility and failure isolation via integrated black-box tests.

## Non-Goals

- Migrating, decrypting, rotating, re-encrypting or retaining historical development ciphertext; the developer will clear affected non-production data **before** cutover.
- Replacing unrelated secrets such as Shopify OAuth, Meta access tokens, installation credentials, TLS keys, auth cookies, HMACs for unrelated protocols, or OpenTelemetry exporter secrets.
- Introducing a general-purpose KMS, new storage, database schema, network API, or new key distribution service.
- Injecting hosted encryption keys or the Commerce command-HMAC secret into merchant-controlled WooCommerce PHP/JavaScript, a browser, Shopify merchant UI, Gateway request proxy or messaging ingress that does not decrypt the credentials.
- Moving domain-specific authorisation, tenant checks, database access, source-specific secret validation or command business semantics into Shared.

## Current Architecture (2026-10-14 snapshot)

| Consumer / owner | Source evidence and current behaviour |
|---|---|
| Admin | `src/lib/admin/openrouter-credential-keyring.ts` has a local parser, maximum key ID 64, and active-key loading. OpenRouter, translation and embedding credentials use local crypto helpers. |
| Background | `src/commerce/credential-keyring.ts` parses locally, maximum key ID 128. `src/security/aes-gcm-credential.ts` implements local bounded decryption; `src/services/woo-coupon-grant.service.ts` decrypts Woo API grants. |
| Commerce | `lib/server/credential-keyring.ts` returns an empty keyring on missing input; external connections, Preview/OpenRouter and embedding runtime each contain crypto. `src/commerce/connections/command-kernel.ts` HMACs canonical commands with a string key. |
| MCP | `src/execution/merchant-knowledge/credential-keyring.ts` largely duplicates Commerce; embedding runtime decrypts with local GCM. |
| API | `src/woocommerce/rest-read/config.ts` takes `MODA_WOO_REST_READ_KEYRING` with base64url material, plus a separate active ID; `envelope.ts` implements Woo grant AES-GCM. |
| Shared | Existing `commerce/model` OpenRouter and translation credential AAD helpers, but no exported common credential keyring/envelope primitive. |
| Gateway | Both `render.test.yaml` and `render.production.yaml` already define Commerce keyring/writer groups and Commerce-only HMAC. `tests/validate-render-blueprints.sh` currently limits keyring/writer attachments; the API is not yet a permitted writer. |

`ARCH-024-GATEWAY-001` is separately Ready in the snapshot; it preserves the keyring distribution needed by database-backed OpenRouter. ARCH-039 Gateway work must incorporate its accepted result rather than overwrite or duplicate it.

## Proposed Architecture

```text
            Render environment-specific external secrets
       COMMERCE_CONNECTION_KEYS_JSON (canonical base64 keyring)
       COMMERCE_CONNECTION_ACTIVE_KEY_ID (writer-only)
       COMMERCE_CONNECTION_COMMAND_HMAC_KEY (Commerce-only)
                               |
                  least-privilege deployment wiring
                               |
      +-------------+----------+-----------+------------+
      |             |          |           |            |
    Admin       Commerce    Background     MCP          API
  (writer)    (writer)      (reader)     (reader)     (writer)
      |             |          |           |            |
      +-------------+----------+-----------+------------+
                               |
       @modainteract/moda-interact-shared/security/credentials/node
            validated keyring + AEAD + shared AAD contracts
                               |
      caller-owned DB/tenant/policy checks and error mapping
```

- Shared receives explicit keyring bytes/inputs. **No `process.env` reads, Prisma, Redis or network operations inside generic crypto**; each hosted runtime reads its allocated environment variables and calls Shared.
- Reader-only services do not require an active-key selector. A missing/invalid keyring must fail closed when the encrypted capability is enabled or invoked. Optional feature disabling must be an explicit, independently validated host decision; silent empty-keyring substitution after malformed input is prohibited.
- Writers select only an active key that exists in the validated ring; readers select only the stored key ID. Existing key IDs can coexist for normal future rotation, although this initiative has no historical-ciphertext migration requirement.
- The generic AEAD primitive accepts authenticated data as explicit UTF-8/bytes; cross-service AAD builders live in Shared, while single-owner AAD is kept with its owning domain.
- For `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`, Shared provides strict encoding validation and raw key bytes, but Commerce retains its command digest/audit contract. Because non-production audit data will be cleared, the Commerce implementation may switch from treating the base64 *text* as an HMAC key to using decoded key bytes, with tests covering the new deterministic digest; this is **not** a ciphertext encryption key.

## Request / Event Flow

```text
Admin encrypts OpenRouter / translation / embedding credential
   -> Shared keyring + active key -> Shared authenticated seal
   -> owning domain persists envelope and domain metadata
   -> authorised Commerce / Background / MCP reader
   -> Shared keyring -> domain AAD -> Shared authenticated open

API authorises Woo REST-read credentials
   -> same Shared keyring + active key -> Shared authenticated seal
   -> Woo grant persists as before
   -> Background validates current installation, shop and grant
   -> same Shared keyring + Woo grant AAD -> Shared authenticated open

Commerce command mutation
   -> decode separate COMMERCE_CONNECTION_COMMAND_HMAC_KEY
   -> HMAC request digest for existing idempotency/audit semantics
```

## Repository Responsibilities

| Owner | Responsibility |
|---|---|
| `moda_shared` | Canonical Node-only keyring, AEAD/envelope code, cross-service AAD helpers, HMAC-key decoding and publication |
| `moda_admin` | OpenRouter/translation/embedding credential writer migration |
| `moda_background` | Credential keyring consumers and Woo grant decryption migration |
| `moda_commerce` | External connection credential security, command-HMAC and Preview/embedding readers |
| `moda_mcp` | Merchant Knowledge keyring and embedding reader |
| `moda_api` | Woo REST-read configuration and grant encryption/decryption |
| `moda_gateway` | Render Blueprint groups/attachments, API writer wiring, secret-absence and least-privilege validation, operator docs |
| `moda_system_test` | Black-box interop, tamper, secret boundary and rollout verification |
| WordPress / Shopify merchant UI | No change; hosted secret values must never reach them |

## Data Model

No Prisma or SQL migration. Use existing encrypted credential columns (`keyId`/`encryptionKeyId`, nonce, auth tag, ciphertext, edit version/rotation version as defined by domain). Shared does not own database mappings. Non-production clearing is a developer-controlled prerequisite for breaking cutover, not a task to drop tables or truncate records.

## Contracts

Owner: `moda-interact-shared` published as `@modainteract/moda-interact-shared/security/credentials/node`, with a Node-only export-map entry, types and build/test coverage. Target public capabilities, with final signatures determined in SHARED-001/002/003:

- `parseCredentialKeyring(raw)` / `resolveActiveCredentialKey(keyring, activeKeyId)`; strict keyring contract stated above; no silent optional fallback.
- `sealCredential({keyring, activeKeyId, plaintext, aad})` and `openCredential({keyring, envelope, aad})`; AES-256-GCM, fresh 12-byte random nonce, 16-byte auth tag, bounded non-empty ciphertext, authenticated UTF-8/bytes; safe typed failures without secret leakage.
- `parseCommerceConnectionCommandHmacKey(raw)` for the independently configured Base64 HMAC key; no assumption that HMAC key is part of AES keyring.
- Shared AAD builders for `CommerceEmbeddingConfiguration` and the Woo REST-read grant. Existing OpenRouter and translation AAD builders continue to be reused. The Woo grant uses the exact trusted identifiers (`shopId`, installation ID, authorisation attempt, credential-version snapshot); no tenant-agnostic AAD.

Consumers pin and import **the published Shared version**, not source-relative imports or service-local copies. Publication is a separate accepted-task gate.

## Consistency and Transactions

No new transaction mechanism. Domain writers continue using their existing database transaction and audit/idempotency behaviour. AEAD failure must not cause credential acceptance or unsafe plaintext fallback. Woo grant current-status/tenant/version checks remain performed before/after provider reads as currently implemented. Commerce command digest changes may invalidate non-production idempotency evidence; the developer's wipe must account for this rather than trying to reconcile old audit digests.

## Ordering

Shared implementation and publication precede consumers. API and Background Woo tasks use the same Shared AAD, encryption and payload contracts and can independently implement against them. Gateway is final wiring **after** consumers can accept canonical configuration and after overlapping ARCH-024-GATEWAY-001 is Complete. System test comes last.

## Failure Handling

Reject JSON parse failures, duplicate/invalid key IDs, empty/oversized keyring, unknown key IDs, non-canonical standard-base64 and wrong key sizes. Authentication failure, wrong AAD, corrupt nonce/tag/ciphertext, invalid UTF-8 and bounded-payload violations must fail closed with secret-free errors. Consumers map errors to their existing domain-specific safe error categories; no raw plaintext, key bytes, environment variable contents or crypto stack internals in logs, traces, API responses or provider calls. Startup/feature configuration must not silently invent keys.

## Scalability

Crypto and keyring validation are local Node operations; no additional database, Redis, HTTP request or queue round trip is introduced. Cache parsed keyrings at host boundaries where safe, but do not cache credentials across owner-specific revocation/version decisions. Preserve existing worker throughput and event ingress behaviour.

## Security

Encryption and command HMAC are independent keys with different authorised audiences. Read-only Background/MCP do not need active-key selector; API gains access to AES keyring/selector but **not** command HMAC. Admin and Commerce remain AES writers. No hosted secret in WordPress plugin, browsers, public gateway/messaging ingress or client-side bundles. Use `server-only` adapters where frameworks require them. Test/production secrets must be distinct; never commit secret values or print fixtures that resemble real credentials. Key rotation of command HMAC remains a separate architecture decision for persistent audit data; no automatic silent HMAC rotation in this initiative.

## Observability

Reuse `@modainteract/moda-interact-shared/logging` for existing semantic structured events; do not add a second generic logger or new generic HTTP metrics. Emit only bounded reason codes such as `configuration_invalid`, `credential_unavailable`, or `authentication_failed`, without secrets, key bytes, ciphertext, plaintext, AAD containing tenant identifiers beyond existing policy or stack traces containing secrets. No new Gateway observability transport task is required.

## Infrastructure / Rollout

**PRE-PRODUCTION / BREAKING ROLLOUT** explicitly approved on the basis of the user's plan to clear development data. The developer must confirm a cutover checkpoint that clears **all affected non-production encrypted rows, corresponding job payloads and command audit/idempotency evidence where required**, and ensures no old producer or consumer remains live. This permission does not apply to production durable state without separate approval. No backward-compatibility adapter or dual keyring is authorised for this effort.

Order: SHARED-001/002/003 acceptance -> SHARED-004 publication -> repository consumer implementations/acceptance -> overlapping ARCH-024 Gateway completion -> GATEWAY-001 configuration/test+production manifest updates -> developer-controlled non-production clear-and-cutover -> SYSTEM-TEST-001 -> architect verification. The Gateway task must not itself perform an environment deployment, generate values or clear a database. Validated Render `sync:false` secret *names* and least-privilege attachments are committed; values remain out of source control.

## Decisions / Tasks

| Task | Owner | Initial status | Depends on |
|---|---|---|---|
| ARCH-039-SHARED-001 | moda_shared | Ready | — |
| ARCH-039-SHARED-002 | moda_shared | Pending | SHARED-001 |
| ARCH-039-SHARED-003 | moda_shared | Pending | SHARED-001 |
| ARCH-039-SHARED-004 | moda_shared | Pending | SHARED-001, SHARED-002, SHARED-003 |
| ARCH-039-ADMIN-001 | moda_admin | Pending | SHARED-004 |
| ARCH-039-ADMIN-002 | moda_admin | Pending | SHARED-004 |
| ARCH-039-BACKGROUND-001 | moda_background | Pending | SHARED-004 |
| ARCH-039-BACKGROUND-002 | moda_background | Pending | SHARED-004, BACKGROUND-001 |
| ARCH-039-COMMERCE-001 | moda_commerce | Pending | SHARED-004 |
| ARCH-039-COMMERCE-002 | moda_commerce | Pending | SHARED-004, COMMERCE-001 |
| ARCH-039-MCP-001 | moda_mcp | Pending | SHARED-004 |
| ARCH-039-API-001 | moda_api | Pending | SHARED-004 |
| ARCH-039-API-002 | moda_api | Pending | SHARED-004, API-001 |
| ARCH-039-GATEWAY-001 | moda_gateway | Pending | ARCH-024-GATEWAY-001, ADMIN-001/002, BACKGROUND-001/002, COMMERCE-001/002, MCP-001, API-002 |
| ARCH-039-SYSTEM-TEST-001 | moda_system_test | Pending | SHARED-004 and all ARCH-039 consumer + GATEWAY-001 tasks |

See each fully-qualified YAML `depends_on` list for the authoritative graph. Tasks may run in parallel when dependencies and distinct task worktrees permit it; do not work in shared/default checkouts. All non-system-test tasks use `execution_mode: developer`, `completion_mode: developer` for the requested patch-apply/verify workflow. Architect review alone does not make a developer-mode task Complete; developer explicitly completes it. The system-test task uses the normal agent execution/review path.

## Open Questions

No blocking design questions at definition time. The keyring bounds, Base64 encoding, encryption/HMAC separation, fail-closed behaviour, and lack of historical compatibility are the intended agreed design. Confirm the actual environment cutover and non-production wipe independently before integration testing.

## Change History

- 2026-10-14: Agreed ARCH-039 with 15 bounded tasks, canonical three-variable deployment contract and developer-approved pre-production breaking rollout. Domain `_index.md`, global architecture `_index.md`, workspace state and implementation files deliberately untouched pending architecture-session confirmation.
