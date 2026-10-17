---
id: ARCH-043-SHOPIFY-001
architecture_id: ARCH-043
title: Create Shopify server-side platform configuration service
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-043-DATABASE-001
  - ARCH-043-ADMIN-002
enables:
  - ARCH-043-SHOPIFY-002
created: 2026-10-17
updated: 2026-10-17
---

# Create Shopify server-side platform configuration service

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Canonical configuration/envelope specification: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_app`; repository: `moda-interact`.
- Portable definition: **defined but not materialised**; no developer worktree/branch/commit is claimed.

## Objective

Provide one reusable, testable **server-only** Shopify configuration service that resolves and validates authorised `PlatformConfiguration` records afresh for each operation for subsequent consumers, without changing any current Shopify business call sites.

## Context

The 17 October snapshot contains `app/db.server.js` (Prisma), a synchronous `shopifyApp({...})` construction in `app/shopify.server.js`, and `app/services/merchant-knowledge/r2-config.server.ts` reading R2 settings from `process.env`. ARCH-043 already owns the new `PlatformConfiguration` schema through DATABASE-001. This task creates a reusable resolution boundary; SHOPIFY-002 performs all runtime integration.

## Scope

- Implement a small, modular server-only configuration service under `app/services/platform-configuration/` using the existing Prisma client and existing published ARCH-039 credential cryptography.
- Provide **two narrowly typed readers**: `readMerchantKnowledgeUploadPolicy()` for non-secret `merchantKnowledge.upload`, and `requireShopifyOAuthCredentials()` for sealed `shopify.oauth`.
- Implement shared internal record lookup, trusted-environment resolution, strict payload validation, no caching or invalidation infrastructure and bounded safe diagnostics. Keep secret and non-secret decode paths separate.
- Make the OAuth reader usable by a future load-before-serve/bootstrap mechanism; **do not** change `app/shopify.server.js`, route handlers, R2 consumers or startup scripts in this task.
- Add focused unit tests with injected Prisma, keyring/decrypt and environment values; no network access in tests.

## Out of Scope

- Do not wire `shopifyApp`, session storage, webhook ingress, upload intents/finalisation or UI to the service. Those changes belong to SHOPIFY-002.
- No database migration, Admin editor, generic remote configuration API, new Shared package, encryption implementation, or browser exposure.
- Do not move R2 signing/access keys into `merchantKnowledge.upload`, and do not change Background's OAuth refresh reader.

## Requirements

1. A narrow repository adapter queries `PlatformConfiguration` using **both** trusted `environment` and allowlisted `key`; never accept either from browser/request JSON. Reuse `app/db.server.js` rather than introducing a second Prisma client. No cross-environment fallback.
2. The two supported keys are exactly `merchantKnowledge.upload` (non-secret) and `shopify.oauth` (encrypted). Unknown keys, malformed records, invalid versions and schema mismatches must fail with bounded non-secret errors.
3. Return a validated immutable policy shape `{ maxUploadBytes, maxXlsxUncompressedBytes, r2Endpoint, r2Bucket }` with `version`; validate integers, HTTPS endpoint, forbidden URL credentials and bucket against the canonical ARCH-043 contract and existing service security restrictions. No fabricated production endpoint, bucket or unsafe default.
4. Return a server-only Shopify OAuth credential shape `{ apiKey, apiSecret, version }`, never a raw envelope. Validate the database sealed-envelope schema and decrypt using **existing** `@modainteract/moda-interact-shared/security/credentials/node` functions; validate the decrypted `shopify.oauth` payload. The independent config-unseal material remains external. Do not reuse Merchant Knowledge/R2 credential material as an OAuth decryptor.
5. Reconstruct the fixed UTF-8 AAD exactly as documented: `JSON.stringify(["moda-platform-config-v1", environment, key, version, 1])`; confirm compatibility with the Admin writer using known deterministic test vectors and reject environment/key/version or ciphertext tampering. Do not introduce a new Shared helper or cryptographic primitive.
6. Never cache configuration/secret values across operations. Read and validate the row for each relevant operation; do not query repeatedly within the same operation. A missing or invalid OAuth secret **must fail closed**, especially on cold start or after expiry/revocation. Never retain revoked credentials indefinitely. Policy read errors must not silently enable an R2 transfer.
7. Ensure the server-only module is not imported by browser bundles or serialised to client loaders. Emit safe key/revision/error-code diagnostics through the approved Shared logger; no plaintext secrets, ciphertext or complete confidential payloads.
8. Keep interfaces small; do not create a giant generic configuration framework. Implement no production fallback to `process.env.SHOPIFY_API_SECRET` inside this service.

## Work Items

- [ ] Create `app/services/platform-configuration/repository.server.ts` with environment/key-constrained Prisma lookup.
- [ ] Create `app/services/platform-configuration/merchant-knowledge-policy.server.ts` to decode/validate typed non-secret policy.
- [ ] Create `app/services/platform-configuration/shopify-oauth-credentials.server.ts` to validate sealed envelope, create canonical AAD and decrypt/validate OAuth secrets.
- [ ] Create `app/services/platform-configuration/service.server.ts` to expose typed readers that fetch and validate fresh values for each operation; keep collaborators injectable.
- [ ] Add tests for correct policy/secret reads, invalid/missing rows, environment mismatch, tampering, fresh reads after edits and revocation, errors and ciphertext non-disclosure.
- [ ] Record launcher-resolved worktree isolation/synchronisation, changed files and validation in the Completion Report; return to Review and STOP.

## Interfaces / Contracts

Proposed *internal* server-only API (the implementation may choose equivalent signatures while preserving observable semantics):

```ts
interface ShopifyPlatformConfigurationService {
  readMerchantKnowledgeUploadPolicy(): Promise<{
    version: number;
    maxUploadBytes: number;
    maxXlsxUncompressedBytes: number;
    r2Endpoint: string;
    r2Bucket: string;
  }>;
  requireShopifyOAuthCredentials(): Promise<{
    version: number;
    apiKey: string;
    apiSecret: string;
  }>;
  invalidate(key: "merchantKnowledge.upload" | "shopify.oauth"): void;
}
```

- Data ownership: `ARCH-043-DATABASE-001` (`PlatformConfiguration`; validated `environment`, `key`, `version`, `value`).
- Envelope and AAD bytes: frozen ARCH-043 schema review; existing Shared/ARCH-039 encryption functions, **no ARCH-043 Shared publication**.
- Policy contract uses the four documented fields, subject to existing hard safety caps. Credential contract is server-only and purpose-specific.
- No public route, GraphQL schema, queue event or new cross-repository wire contract.

## Dependencies

- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-SHOPIFY-002`

## Acceptance Criteria

- [ ] A single injectable server-only service retrieves both supported keys using trusted deployment environment, with no cross-environment or unknown-key access.
- [ ] Non-secret policy rejects unsafe endpoint/bucket/limits and does not supply fabricated values.
- [ ] OAuth secret decrypts with the existing Shared crypto and exact Admin-compatible AAD; tampered row/key/version/envelope fails closed.
- [ ] The service returns typed values, never exposes ciphertext or plaintext to a browser response/log, and never retains values in a cross-operation cache.
- [ ] All service tests pass without changing the current OAuth startup or Merchant Knowledge upload behaviour.

## Validation

- [ ] Focused typed-policy, crypto-compatibility and fresh-read unit tests
- [ ] Typecheck, changed-file ESLint and repository build (existing declared commands)
- [ ] Server-only import safety checks and `git diff --check`

## Stop Condition

After the scoped service and validation are complete, update the Completion Report and task status to Review, return to `moda_architect` and STOP. Do not begin SHOPIFY-002 or edit any `_index.md`.

## Implementation Notes

Suggested files are boundaries, not mandatory new framework layers. Use `app/db.server.js` and existing published ARCH-039 Node-only decryption, with clear test injection. The Shopify app currently constructs `shopifyApp` synchronously at import time: service construction must **not** opportunistically modify that behaviour. Runtime bootstrap choice and import/order verification belong to SHOPIFY-002. Shared structured logging is the only generic logger.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation and validation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not yet assessed.

### Follow-up

None

## 17 October 2026 ARCH-043 extension (architect-owned amendment)

The Shopify server-only reader may expose strict `merchant.knowledge.r2` (six-field sealed JSON) to server code only; never to browser, and never grant client-side access to unwrap root. Verify the developer-provided forward migration before enabling the three added purposes.
