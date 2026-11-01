---
id: ARCH-043-SHOPIFY-001
architecture_id: ARCH-043
title: Create Shopify server-side platform configuration service
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-043-DATABASE-001
  - ARCH-043-ADMIN-002
enables:
  - ARCH-043-SHOPIFY-002
created: 2026-10-17
updated: 2026-10-18
---

# Create Shopify server-side platform configuration service

## Developer Ownership Amendment

On 2026-10-18, `/moda_developer_create ARCH-043-SHOPIFY-001` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_app`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The task remains at Attempt 0 until canonical preparation claims Attempt 1.

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Canonical configuration/envelope specification: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_app`; repository: `moda-interact`.
- Definition provenance: originally handed off as a portable task definition; now materialized on parent branch `task/ARCH-043-SHOPIFY-001`. No implementation worktree or attempt claim existed before this developer preparation.

## Objective

Provide one reusable, testable **server-only** Shopify configuration service that resolves and validates authorised `PlatformConfiguration` records afresh for each operation for subsequent consumers, without changing any current Shopify business call sites.

## Context

The 17 October snapshot contains `app/db.server.js` (Prisma), a synchronous `shopifyApp({...})` construction in `app/shopify.server.js`, and `app/services/merchant-knowledge/r2-config.server.ts` reading R2 settings from `process.env`. ARCH-043 already owns the new `PlatformConfiguration` schema through DATABASE-001. This task creates a reusable resolution boundary; SHOPIFY-002 performs all runtime integration.

## Scope

- Implement a small, modular server-only configuration service under `app/services/platform-configuration/` using the existing Prisma client and existing published ARCH-039 credential cryptography.
- Provide **three narrowly typed server-only readers**: `requireMerchantKnowledgeR2Configuration()` for sealed `merchant.knowledge.r2` (six fields), `requireShopifyOAuthCredentials()` for sealed `shopify.oauth`, and `requireShopifyPartnerCredentials()` for sealed `shopify.partner` (Partner billing identity).
- Implement shared internal record lookup, trusted-environment resolution, strict payload validation, no caching or invalidation infrastructure and bounded safe diagnostics. Keep secret and non-secret decode paths separate.
- Make the OAuth reader usable by a future load-before-serve/bootstrap mechanism; **do not** change `app/shopify.server.js`, route handlers, R2 consumers or startup scripts in this task.
- Add focused unit tests with injected Prisma, keyring/decrypt and environment values; no network access in tests.

## Out of Scope

- Do not wire `shopifyApp`, session storage, webhook ingress, upload intents/finalisation or UI to the service. Those changes belong to SHOPIFY-002.
- No database migration, Admin editor, generic remote configuration API, new Shared package, encryption implementation, or browser exposure.
- Do not use or extend legacy `merchantKnowledge.upload` for R2 credentials, and do not change Background's OAuth refresh reader.

## Requirements

1. A narrow repository adapter queries `PlatformConfiguration` using **both** trusted `environment` and allowlisted `key`; never accept either from browser/request JSON. Reuse `app/db.server.js` rather than introducing a second Prisma client. No cross-environment fallback.
2. The three supported keys are exactly `merchant.knowledge.r2` (sealed six-field configuration), `shopify.oauth` (encrypted) and `shopify.partner` (encrypted). Unknown keys, malformed records, invalid versions and schema mismatches must fail with bounded non-secret errors.
3. Return a validated immutable R2 shape `{version, endpoint, bucket, accessKeyId, secretAccessKey, maxUploadBytes, maxXlsxUncompressedBytes}`; decrypt with the approved ARCH-039 Node crypto and AAD, validate safe bounds and HTTPS/host/bucket restrictions, and never expose credentials to the browser. No fabricated production endpoint, bucket or unsafe default.
4. Return a server-only Shopify OAuth credential shape `{ apiKey, apiSecret, version }`, never a raw envelope. Validate the database sealed-envelope schema and decrypt using **existing** `@modainteract/moda-interact-shared/security/credentials/node` functions; validate the decrypted `shopify.oauth` payload. The independent config-unseal material remains external. Do not reuse Merchant Knowledge/R2 credential material as an OAuth decryptor.
5. Provide `requireShopifyPartnerCredentials()` returning the **atomic** sealed `shopify.partner` tuple `{version, accessToken, organizationId, appId, apiVersion?}`. Require all non-optional fields, honour Admin registry field names (not environment variable names), validate `organizationId` and `appId` against the approved contract and use the caller's existing approved Partner API version when `apiVersion` is absent. All fields must come from the **same** validated configuration revision; do not combine database fields with the old `SHOPIFY_PARTNER_ACCESS_TOKEN`/`SHOPIFY_PARTNER_API_TOKEN`, `SHOPIFY_PARTNER_ORG_ID`/`SHOPIFY_PARTNER_ORGANIZATION_ID`, or `SHOPIFY_APP_ID` values. Keep Partner identity separate from Shopify app OAuth credentials.
6. Reconstruct the fixed UTF-8 AAD exactly as documented: `JSON.stringify(["moda-platform-config-v1", environment, key, version, 1])`; confirm compatibility with the Admin writer using known deterministic test vectors and reject environment/key/version or ciphertext tampering. Do not introduce a new Shared helper or cryptographic primitive.
7. Never cache configuration/secret values across operations. Read and validate the row for each relevant operation; do not query repeatedly within the same operation. A missing or invalid OAuth secret **must fail closed**, especially on cold start or after expiry/revocation. Never retain revoked credentials indefinitely. Policy read errors must not silently enable an R2 transfer.
8. Ensure the server-only module is not imported by browser bundles or serialised to client loaders. Emit safe key/revision/error-code diagnostics through the approved Shared logger; no plaintext secrets, ciphertext or complete confidential payloads.
9. Keep interfaces small; do not create a giant generic configuration framework. Implement no production fallback to `process.env.SHOPIFY_API_SECRET` inside this service.

### 18 October reader contract correction (controlling)

The service's canonical Merchant Knowledge read method is `requireMerchantKnowledgeR2Configuration(): Promise<{version:number; endpoint:string; bucket:string; accessKeyId:string; secretAccessKey:string; maxUploadBytes:number; maxXlsxUncompressedBytes:number}>`. It replaces the old `readMerchantKnowledgeUploadPolicy()` non-secret-only contract, not an additional method. The same service also exposes `requireShopifyOAuthCredentials()` and `requireShopifyPartnerCredentials()` independently. All three readers are **server-only** and validate environment, version, closed JSON shape, sealing/AAD and active status. R2 missing/revoked/invalid/unseal failures fail closed; no fallback to the legacy policy or R2 environment secrets after cutover. A test must verify that Shopify server code has approved Node-only unseal access without exposing credentials to a browser bundle. If that cannot be established, return the dependency to the architect rather than implement split configuration.

Keep existing asset relocation/in-flight constraints. Do not migrate historical `objectKey` data or invent a new publicly accessible signing endpoint as part of this task. Update the existing server-only unit tests to reflect this one full-field contract.


## Work Items

- [x] Create `app/services/platform-configuration/repository.server.ts` with environment/key-constrained Prisma lookup.
- [x] Create `app/services/platform-configuration/merchant-knowledge-r2.server.ts` to decrypt/validate the complete sealed R2 configuration tuple (or an equivalent small server-only module).
- [x] Create `app/services/platform-configuration/shopify-oauth-credentials.server.ts` to validate sealed envelope, create canonical AAD and decrypt/validate OAuth secrets.
- [x] Create `app/services/platform-configuration/shopify-partner-credentials.server.ts` (or equivalent focused module) to validate, unseal and return the **atomic** `shopify.partner` Partner API tuple. Do not wire billing call sites in this task.
- [x] Create `app/services/platform-configuration/service.server.ts` to expose typed readers that fetch and validate fresh values for each operation; keep collaborators injectable.
- [x] Add tests for correct policy/secret reads, invalid/missing rows, environment mismatch, tampering, fresh reads after edits and revocation, errors and ciphertext non-disclosure.
- [x] Record launcher-resolved worktree isolation/synchronisation, changed files and validation in the Completion Report; return to Review and STOP.

## Interfaces / Contracts

Proposed *internal* server-only API (the implementation may choose equivalent signatures while preserving observable semantics):

```ts
interface ShopifyPlatformConfigurationService {
  requireMerchantKnowledgeR2Configuration(): Promise<{
    version: number;
    endpoint: string;
    bucket: string;
    accessKeyId: string;
    secretAccessKey: string;
    maxUploadBytes: number;
    maxXlsxUncompressedBytes: number;
  }>;
  requireShopifyOAuthCredentials(): Promise<{
    version: number;
    apiKey: string;
    apiSecret: string;
  }>;
  requireShopifyPartnerCredentials(): Promise<{
    version: number;
    accessToken: string;
    organizationId: string;
    appId: string;
    apiVersion?: string;
  }>;
}
```

- Data ownership: `ARCH-043-DATABASE-001` (`PlatformConfiguration`; validated `environment`, `key`, `version`, `value`).
- Envelope and AAD bytes: frozen ARCH-043 schema review; existing Shared/ARCH-039 encryption functions, **no ARCH-043 Shared publication**.
- R2 contract uses the six sealed documented fields, subject to existing hard safety caps. Credential contract is server-only and purpose-specific.
- No public route, GraphQL schema, queue event or new cross-repository wire contract.

## Dependencies

- `ARCH-043-DATABASE-001`
- `ARCH-043-ADMIN-002`

## Enables

- `ARCH-043-SHOPIFY-002`

## Acceptance Criteria

- [x] A single injectable server-only service retrieves all three supported keys using trusted deployment environment, with no cross-environment or unknown-key access.
- [x] Sealed R2 configuration rejects missing/revoked/unsafe endpoint, bucket, keys or limits and does not fabricate values.
- [x] OAuth and Partner secrets decrypt using existing Shared crypto and the exact Admin-compatible AAD; tampered row/key/version/envelope fails closed.
- [x] Partner reader returns an atomic, validated `{accessToken,organizationId,appId,apiVersion?}` tuple and rejects incomplete, disabled, revoked or cross-environment records; no mixed-source values.
- [x] The service returns typed values, never exposes ciphertext or plaintext to a browser response/log, and never retains values in a cross-operation cache.
- [x] Unit tests prove all **three** readers, including Partner revision/rotation, tampering, malformed identity, missing field, environment separation and no-cache behaviour, without changing the current OAuth, billing or Merchant Knowledge consumers.

## Validation

- [x] Focused typed-policy, crypto-compatibility and fresh-read unit tests
- [x] Typecheck, changed-file ESLint and repository build (existing declared commands)
- [x] Server-only import safety checks and `git diff --check`

## Stop Condition

After the scoped service and validation are complete, update the Completion Report and task status to Review, return to `moda_architect` and STOP. Do not begin SHOPIFY-002 or edit any `_index.md`.

## Implementation Notes

Suggested files are boundaries, not mandatory new framework layers. Use `app/db.server.js` and existing published ARCH-039 Node-only decryption, with clear test injection. The Shopify app currently constructs `shopifyApp` synchronously at import time: service construction must **not** opportunistically modify that behaviour. Runtime bootstrap choice and import/order verification belong to SHOPIFY-002. Shared structured logging is the only generic logger.

## Completion Report

### Status

Complete — Attempt 1 accepted and completed by explicit developer decision. Attempt 0 review history and the Attempt 1 claim are preserved. Implementation commit `9493811` is published on `origin/task/ARCH-043-SHOPIFY-001`.

### Files Changed

`moda-interact/app/services/platform-configuration/{composition,contracts,merchant-knowledge-r2,repository,seal,service,shopify-oauth-credentials,shopify-partner-credentials}.server.ts`; `moda-interact/tests/unit/platform-configuration/{server-only,service}.test.ts`; `moda-interact/package.json`; `moda-interact/package-lock.json`.

### Work Completed

Added a fresh-read, injectable server-only configuration service for sealed R2, Shopify OAuth, and Shopify Partner credentials. It constrains Prisma reads to the trusted deployment environment and exact supported key, validates closed payload/envelope shapes, reconstructs Admin-compatible AAD, uses the existing Shared Node credential crypto, returns frozen purpose-specific values, and emits bounded key/revision/error-code diagnostics. No runtime consumers or Shopify bootstrap call sites were changed. The R2 uncompressed XLSX hard cap was aligned to the Admin and Background contract (`2,147,483,647`).

### Validation Results

Passed: `npm test -- --run tests/unit/platform-configuration` (2 files, 8 tests); `npm run typecheck`; `npx eslint app/services/platform-configuration tests/unit/platform-configuration` (no findings; existing TypeScript 5.9 / typescript-estree compatibility notice); `npm run build` (client and SSR builds passed; existing dependency/large-chunk warnings); client artifact scan found no configuration-service, unseal-key, or AAD markers; `git diff --check` passed. A deterministic independently pinned AES-GCM test vector verified Admin-compatible AAD/decryption. No full repository test suite or full repository lint was required or run.

### Deviations

The installed baseline declared Shared 1.3.0, which does not expose the already-published `security/credentials/node` and logging entrypoints required by this task. The dependency was updated to 2.4.1. An unrelated pre-existing database submodule pointer advance to `69c0c8b` (ARCH-040 database work) was deliberately left unstaged and excluded from implementation commit `9493811`.

### Assumptions

No current Shopify consumer was wired, consistent with SHOPIFY-002 scope. `apiVersion` remains optional in the Partner tuple as specified by Admin; consumers must supply their approved default when absent.

### Unresolved Issues

The implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-SHOPIFY-001` is physically separate from the parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-SHOPIFY-001`. Both use `task/ARCH-043-SHOPIFY-001`. Implementation commit `9493811` was pushed to `origin/task/ARCH-043-SHOPIFY-001`; parent task record update is being committed on the matching parent task branch. The unrelated database submodule pointer is not included. The generic push helper initially refused due to inherited `origin/main` upstream; the task branch was explicitly pushed by matching branch name, without pushing to `main`.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Developer Self-Review Accepted. Focused tests, typecheck, changed-file lint, production build, client-bundle scan, and whitespace check passed. The reviewer verified the exact Admin AAD vector, three independent typed readers, fresh reads, environment/key constraints, fail-closed behavior, and the shared Admin/Background R2 bounds. Implementation is scoped to SHOPIFY-001; no runtime consumers were changed. Review performed against implementation commit `9493811`.

### Reviewed Files

Implementation commit `9493811`; Shopify platform configuration service and focused unit tests.

### Validation Reviewed

None

### Architecture Conformance

Conforms to the task boundary and ARCH-043 sealed configuration contract. R2 bound mismatch found during review was corrected before acceptance. The only excluded worktree delta is the unrelated database submodule pointer advance; it remains uncommitted.

### Follow-up

Developer review passed. Per `completion_mode: developer`, the explicit `/moda_developer_update ARCH-043-SHOPIFY-001 complete` decision was applied after recording this accepted review. No downstream task was started; SHOPIFY-002 remains enabled by this task.

### Developer Self-Review

- Decision: Accepted
- Attempt: 1
- Implementation revision: `9493811` (`origin/task/ARCH-043-SHOPIFY-001`)
- Evidence: Required focused tests, typecheck, changed-file lint, production build, client artifact scan, and `git diff --check` passed.
- Findings: The R2 uncompressed-size cap was aligned with the Admin/Background contract before acceptance. No blocking findings remain for this task's scope.

### Developer Completion Decision

- Decision: Complete
- Authority: Explicit developer request `/moda_developer_update ARCH-043-SHOPIFY-001 complete`
- Accepted attempt: 1 (unchanged)
- Downstream: Recalculate dependency frontier; do not start SHOPIFY-002 in this task.

## 17 October 2026 ARCH-043 extension (architect-owned amendment)

The Shopify server-only reader may expose strict `merchant.knowledge.r2` (six-field sealed JSON) to server code only; never to browser, and never grant client-side access to unwrap root. Verify the developer-provided forward migration before enabling the three added purposes.

## 18 October 2026 — Shopify consolidation amendment

This task is the only ARCH-043 Shopify **service** implementation task. The earlier `ARCH-043-SHOPIFY-003` Partner-reader work is folded into this task as a third typed reader. Only `SHOPIFY-002` changes runtime call sites. The `shopify.partner` configuration contract is the approved Admin sealed registry tuple, separate from `shopify.oauth`; no new Shared module or database model. DATABASE-001 and ADMIN-002 are Complete in the inspected snapshot, so this unclaimed task is eligible for Ready status; the task launcher must recheck status/dependencies at claim time.
