---
id: ARCH-043-SHOPIFY-002
architecture_id: ARCH-043
title: Wire all Shopify platform configuration consumers
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-18T18:35:03Z
attempt: 1
depends_on:
  - ARCH-043-SHOPIFY-001
  - ARCH-043-ADMIN-002
enables:
  - ARCH-043-GATEWAY-001
  - ARCH-043-SYSTEM-TEST-001
created: 2026-10-17
updated: 2026-10-18
---

# Wire all Shopify platform configuration consumers

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Source reader: `ARCH-043-SHOPIFY-001`.
- Admin secure secret import/rotation: `ARCH-043-ADMIN-002`.
- Owner: `moda_app` / `moda-interact`; **defined but not materialised**.

## Objective

Replace Shopify's applicable environment-backed configuration consumption with the accepted `SHOPIFY-001` service in **Merchant Knowledge uploads, Shopify OAuth/bootstrap, and Shopify Partner billing**, without introducing another configuration reader.

## Context

In the 17 October snapshot:
- `app/services/merchant-knowledge/r2-config.server.ts` reads `MERCHANT_KNOWLEDGE_R2_ENDPOINT`, `MERCHANT_KNOWLEDGE_R2_BUCKET` and `MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES` alongside external R2 credentials. `upload.server.ts` uses that synchronous configuration for both intent signing and finalisation.
- `app/shopify.server.js` builds `shopifyApp({...})` **synchronously at module evaluation**, using `SHOPIFY_API_KEY` and `SHOPIFY_API_SECRET`, then exports bound `authenticate`, `login`, `registerWebhooks`, session storage and other helpers.
SHOPIFY-001 provides three typed service readers; this task adapts call sites and proves that OAuth secrets are available **before** this synchronous client is constructed.

## Scope

1. Integrate `requireMerchantKnowledgeR2Configuration()` into the existing server-side R2/upload configuration flow as one six-field sealed operation snapshot; preserve existing upload security, tenant scoping, plan entitlements and R2 signing operations.
2. Integrate `requireShopifyOAuthCredentials()` with a verified load-before-serve bootstrap path for `shopifyApp` construction. Adapt startup/module import sequencing only as required for the deployed React Router runtime; preserve existing Shopify session, webhook and OAuth behaviour.
3. Replace Partner API identity/token reads in `app/services/billing/providers/shopify-billing.provider.ts`, covering **both** `getActiveSubscription()` and the other Partner GraphQL operation in that provider. Obtain the complete `{accessToken,organizationId,appId,apiVersion?}` tuple from `requireShopifyPartnerCredentials()` for each Partner operation. Keep existing billing correlation, subscription lifecycle, duplicate/idempotency protections, error handling and provider response shapes unchanged. Do not conflate Partner credentials with Shopify OAuth or merchant session credentials.
4. Review `app/services/billing/hosted-plan-change.service.ts` and `app/services/billing/subscription-activation.service.ts` for any indirect calls into the provider, and preserve their existing workflows without introducing duplicate credential parsing, new provider clients or network calls inside database transactions.
5. Update relevant existing server-side callers and tests; ensure all affected readers use SHOPIFY-001 rather than a new local `process.env` parser, extra Prisma query or duplicated decryptor.
6. Implement documented safe activation, rollback and key-rotation failure behaviours; remove corresponding **application runtime** env reads only after proving database cutover.

## Out of Scope

- No new `PlatformConfiguration` tables, migrations, Shared package, Admin editor or new decryptor.
- R2 credentials move only through the accepted server-side sealed `merchant.knowledge.r2` reader; Shopify scopes/app URL, CLI tooling configuration and the external unseal root remain deployment-owned.
- Do not change unrelated Shopify webhook filtering/recovery workflows or Background's separate OAuth/token-refresh integration.
- No new merchant UI or tenant-access API for platform secrets.

## Requirements

### Merchant Knowledge integration

- Extend or adapt `app/services/merchant-knowledge/r2-config.server.ts` and `upload.server.ts` to obtain the complete sealed `endpoint`, `bucket`, `accessKeyId`, `secretAccessKey`, `maxUploadBytes` and `maxXlsxUncompressedBytes` snapshot from SHOPIFY-001 on the server; **do not combine it with external R2 credentials after cutover**. Keep existing R2 client, HTTPS/host checks, upload format limits, size caps and signed request expiry.
- The existing upload-intent/finalisation endpoints continue to authenticate and resolve shop identity through `settingsAccess()`, enforce plan entitlement and verify object metadata. No browser receives R2 key material or config envelope. Do not create new remote signing endpoints without a separate architecture decision.
- A missing, invalid or unsafe policy fails without issuing a signed upload. Allow R2 endpoint and bucket edits; their data-migration and in-flight-asset handling are owned by separately agreed tasks, not ARCH-043. Keep a single fetched policy within one operation; document and test in-flight object/bucket continuity. Do not silently corrupt existing assets if storage settings change (the current `MerchantKnowledgeUploadedAsset` has `objectKey`, not a bucket snapshot).
- Fetch and validate the current policy via SHOPIFY-001 for each upload operation, without cross-operation caching. Preserve environment isolation and explicit operational configuration (no invented production bucket).

### Shopify Partner API / billing integration

- Use `requireShopifyPartnerCredentials()` from SHOPIFY-001 for each actual Partner GraphQL operation, **not** an independently invented reader or environment lookup. `accessToken`, `organizationId`, `appId` and optional `apiVersion` must be from the same DB record/revision.
- Remove `SHOPIFY_PARTNER_ACCESS_TOKEN`, `SHOPIFY_PARTNER_API_TOKEN`, `SHOPIFY_PARTNER_ORG_ID`, `SHOPIFY_PARTNER_ORGANIZATION_ID`, `SHOPIFY_APP_ID` and `SHOPIFY_PARTNER_API_VERSION` as runtime credential reads **where present in the Shopify repository**, only after tested cutover. An approved default Partner API version is permitted when optional `apiVersion` is absent; it must never silently select another credential source.
- Preserve both existing `ShopifyBillingProvider` Partner API operations, including session-independent Partner billing calls, errors, provider data contracts and idempotency. Test revoked/rotated/unavailable configuration and ensure no token reaches browser data, logs or error responses.

### Shopify OAuth bootstrap integration

- Use the SHOPIFY-001 sealed `shopify.oauth` reader to provide **both** `apiKey` and `apiSecret` before constructing the existing `shopifyApp({...})` object. Preserve synchronous exported auth helpers (`authenticate`, `login`, `registerWebhooks`, `sessionStorage`) and existing session/route imports; do not export half-initialised clients or use placeholder secrets.
- Prove a concrete startup mechanism compatible with the actual package scripts / React Router server module load (e.g., a same-process preinitialisation mechanism verified by tests). Do not assume an asynchronous database lookup is safe inside the current synchronous module expression; never start serving protected routes before bootstrap is completed.
- On absent, revoked, malformed, undecryptable or wrong-environment secret, **fail closed** at bootstrap/readiness (no blank key, hidden env fallback or unauthenticated bypass). On database/unseal outage, retain only explicitly approved bounded rollback semantics; no indefinite stale credential acceptance.
- Confirm the Shopify client and webhook HMAC verifier continue using the same versioned secrets; confirm applicable Shopify OAuth/auth session flows, scoped dedupe `apiKey` exports, token refresh interactions and webhook signature validation remain correct. Verify permitted rotation overlap with the real Shopify library; do not invent multi-key support.
- Require that `ARCH-043-ADMIN-002` has securely imported active `shopify.oauth` values before a DB-only release. Safe local development/bootstrap must be documented without placing OAuth secrets into browser output or source control.

### 18 October upload consumer correction (controlling)

`app/services/merchant-knowledge/r2-config.server.ts` and `upload.server.ts` must consume `SHOPIFY-001.requireMerchantKnowledgeR2Configuration()` as **one immutable six-field operation snapshot**, without merging legacy `merchantKnowledge.upload` or R2 credential environment values. Validate upload intent/finalisation, signed headers, shop authentication, tenant caps, existing assets and safe bucket-location changes. Browser response must never include `accessKeyId`, `secretAccessKey` or sealed envelope. Legacy config and environment fallbacks cannot silently override the selected row. The Shopify OAuth/startup requirements of this task are unchanged.


## Work Items

- [ ] Identify upload call sites and adapt `r2-config.server.ts` / `upload.server.ts` to consume the Shopify configuration service; preserve validated R2 signing and tenant checks while moving credentials to the single sealed record.
- [ ] Test upload-intent and finalisation with valid/invalid/missing policies, fresh revisions after editable R2 location changes, pending uploads handled by the separately owned relocation flow and environmental mismatch.
- [ ] Inspect the actual `shopifyApp` module evaluation and React Router runtime startup path; implement and test a safe load-before-serve credential bootstrap using SHOPIFY-001 without new crypto.
- [ ] Adapt `app/shopify.server.js` and any necessary startup composition only after bootstrap can be proved. Maintain existing exports and Shopify auth semantics.
- [ ] Replace both Partner operations in `app/services/billing/providers/shopify-billing.provider.ts` with the accepted `requireShopifyPartnerCredentials()` reader; add Partner query/version, billing regression, rotation, revocation and no-mixed-source tests.
- [ ] Review indirect billing callers for unchanged provider semantics and ensure no stale Partner environment reads remain in the Shopify runtime.
- [ ] Test bootstrap failure, successful OAuth login/session handling, webhook HMAC, rotation and rollback; verify no secret appears in client or logs.
- [ ] Record startup/deployment ordering and credential-import precondition; document required environment-variable retirement for GATEWAY-001.
- [ ] Record launcher-resolved isolation/synchronisation and actual validation in Completion Report; stop at Review.

## Interfaces / Contracts

- Consume only `ARCH-043-SHOPIFY-001` server-only typed readers (R2, OAuth and Partner); do not duplicate query, AAD or decryption code or introduce a config cache.
- `ARCH-043-ADMIN-002` owns secure writer/import; current `shopify.oauth` envelope and frozen AAD contract stay unchanged.
- Keep existing `shopifyApp` exported session/auth/webhook helpers and existing Merchant Knowledge upload route/error contracts.
- Do not change `MerchantKnowledgeUploadedAsset` schema, `Shop`/session schema or existing encrypted Commerce credential formats.

## Dependencies

- `ARCH-043-SHOPIFY-001`
- `ARCH-043-ADMIN-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Shopify Merchant Knowledge upload/finalise and R2 signing use validated database policy, with the sealed R2 credentials and original security checks preserved.
- [ ] Each new upload request reads the current editable R2 endpoint/bucket values; in-flight upload migration and historical asset location remain with the separate storage-relocation tasks.
- [ ] Shopify OAuth key/secret are loaded and decrypted **before** any `shopifyApp` construction or authenticated ingress; no unsafe env fallback.
- [ ] Both Shopify Partner billing operations consume a fresh, atomic `shopify.partner` tuple through SHOPIFY-001, preserve existing billing behaviour, and fail closed on missing/revoked/invalid secrets without mixing database and environment fields.
- [ ] OAuth/login, sessions, webhook HMAC, tenant isolation and existing Shopify functionality pass regression tests; missing/tampered/revoked secrets cause closed failures.
- [ ] Rotation/restart/readiness and deployment cutover are documented and verified under the actual Shopify runtime; CLI infrastructure variables are not removed indiscriminately.

## Validation

- [ ] Merchant Knowledge upload-intent/finalisation tests and R2 security tests
- [ ] Shopify auth/bootstrap/webhook HMAC/session tests including cold-start failure and rotation cases
- [ ] Shopify Partner billing provider and indirect subscription lifecycle regression tests for both Partner queries, version default, rotation and revoked credentials
- [ ] Typecheck, lint, production build and relevant integration tests using repository-defined scripts
- [ ] `git diff --check`, worktree/branch evidence and recorded env-read removal diff

## Stop Condition

Complete defined integrations and validation, update task/Completion Report to Review, return to `moda_architect`, and STOP. Do not perform Gateway cleanup, system testing or `_index.md` edits.

## Implementation Notes

This task absorbs the previous `ARCH-043-SHOPIFY-003` Partner credential consumer. The old task is removed from active discovery, and downstream Gateway/System Test depend on SHOPIFY-002 for **all three** Shopify configuration cutovers. Keep runtime implementation exclusively in `moda-interact`; Admin manages credential import, Background owns its separate Partner provider, and Gateway owns environment-variable removal.


Prefer modular adapters over an oversized `shopify.server.js` or a generic config framework. Inspect the real Shopify SDK and React Router startup contract first. If authenticated load-before-serve cannot be achieved without a new entrypoint/service lifecycle decision, **report the architectural blocker** rather than writing a partially initialised or insecure fallback. Reuse approved Shared logging and ARCH-039 cryptography. Treat R2 endpoint/bucket changes as an explicit in-flight upload safety concern, not an invisible generic config refresh.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-18T18:35:03Z. Attempt 0 review history is preserved below.

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

Replace R2 endpoint, bucket, credentials and size reads with one sealed `merchant.knowledge.r2` record; no duplicate `merchantKnowledge.upload` policy after cutover. Validate endpoint/SSRF and relocation safety. Requires ADMIN-002 and verification of the developer forward migration before cutover.

## Developer execution takeover amendment

This ready task was explicitly invoked through `/moda_developer_create`, transferring execution ownership to the developer. `assigned_agent: moda_app` remains unchanged for domain ownership. Completion is developer-controlled; the task will stop at Review for developer reconciliation and architect review.
