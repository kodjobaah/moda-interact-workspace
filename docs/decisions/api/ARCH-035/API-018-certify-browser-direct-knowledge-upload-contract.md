---
id: ARCH-035-API-018
architecture_id: ARCH-035
title: Certify and adapt accepted Woo knowledge presigned upload for browser-direct PUT
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 46
executor: null
claimed_at: null
attempt: 1
depends_on: [ARCH-035-API-017, ARCH-043-API-002]
enables: [ARCH-035-WOOCOMMERCE-014, ARCH-035-GATEWAY-001]
created: 2026-10-17
updated: 2026-10-18
---

# ARCH-035-API-018 — Browser-direct R2 signing compatibility and secure metadata handoff

## Developer Ownership Amendment

On 2026-10-18, `/moda_developer_create ARCH-035-API-018` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_api`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The task remains at Attempt 0 until canonical preparation claims Attempt 1.

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, 17 October browser-direct upload amendment.
- Owner: `moda_api`, `moda-interact-api`. This definition was initially handed off portably and is now materialized on parent branch `task/ARCH-035-API-018`; no implementation worktree or attempt claim existed before this developer preparation.

## Objective

Prove and, only where necessary, minimally adapt the existing accepted API-017 presigned upload-intent contract for direct browser-to-R2 `PUT` without reimplementing upload persistence or finalisation.

## Context

`ARCH-035-API-017` is already **Complete (Attempt 1)**. Current `src/merchant/merchant-knowledge/upload.service.ts` returns `schemaVersion`, `assetId`, short-lived `uploadUrl`, `expiresAt`, `maxUploadBytes`, and `requiredHeaders` (`Content-Type`, `If-None-Match: *`, `x-amz-meta-sha256`). `upload-r2.ts` signs a bounded `PutObject` to the approved HTTPS R2 S3 endpoint and `finalize` verifies actual object bytes and metadata. Prior task text says PHP sends the bytes; that historical task is **not** to be modified or reopened. The browser transport needs explicit compatibility proofs, strict response/privacy guarantees and a consumer-ready contract.

**18 October configuration reconciliation:** Accepted `ARCH-043-API-001/002` introduced `src/platform-configuration/{repository,contracts,service,composition}.ts` and wired `src/index.ts` -> `src/composition/merchant.ts` -> `MerchantKnowledgeUploadService.dependencies()` to read the sealed, exact-environment PostgreSQL key `merchant.knowledge.r2` on each protected operation. The six-field configuration contains `endpoint`, `bucket`, `accessKeyId`, `secretAccessKey`, `maxUploadBytes`, `maxXlsxUncompressedBytes`. `MODA_CONFIG_UNSEAL_KEY` and `MODA_CONFIG_UNSEAL_ACTIVE_KEY_ID` remain deployment environment inputs for the root unseal key; old `MERCHANT_KNOWLEDGE_*` environment variables are not a production fallback. Keep those accepted implementations and tasks unchanged. The unused production-path `loadUploadR2Configuration()` remains a legacy test fixture parser, not a second configuration source.

## Scope

- Inspect API-017 signer/intent/finalise and `openapi/merchant-knowledge-v1.yaml` as implemented, including hosted response cache headers, URL/host restrictions and precise signed-header case/value preservation. Correct the outdated PHP-server-only PUT description for the approved browser-direct flow; update any similarly stale PHP-proxy comment in API-owned signer code without changing signed bytes.
- Reuse the accepted ARCH-043 purpose-specific `ApiPlatformConfigurationReader` injection. Prove lazy, per-operation resolution of `merchant.knowledge.r2` with exact environment, sealed R2 credentials/policy, secure root-key environment reads, fail-closed absent/disabled/malformed/unsealable configuration, and absence of legacy credential fallback. Do not implement a new generic configuration loader or environment parser.
- Confirm a standard browser `fetch`/XHR `PUT` with a `Blob` can send exactly the signed headers and bytes to the R2 S3 API endpoint without API, WordPress or cookie credentials. Provide deterministic browser-like HTTP fixture tests, including `OPTIONS` preflight assumptions for Gateway, not a fabricated browser preflight pass.
- Preserve R2 `Content-Type`, `If-None-Match: *`, `x-amz-meta-sha256` signatures, TTL ≤ the durable upload-intent expiry, immutable object identity, idempotent duplicate finalize and verified SHA-256/length before activation.
- Ensure only the authenticated Woo principal receives the complete signed URL and required headers from the upload intent, with no-store responses and no logging/reflection of signed query parameters, file contents, keys or installation credentials; adjust API HTTP/OpenAPI output only if an evidenced gap exists.
- Document exact browser upload contract, safe error semantics (signature expired, redirect, bad header, R2 412, CORS unavailable, cancelled upload and finalise failure), environment-scope and rollout ordering for WOO-014/015 and Gateway; use shared Node logging conventions for any added diagnostics.
- Test configuration change *between* intent, signed browser PUT and finalisation (credential rotation, bucket/endpoint/policy change or disabled configuration). Never verify or finalise against a different object silently; require deterministic fail-closed handling and documented retry with a new valid intent where necessary. Do not demand uninterrupted in-flight uploads after a deliberate R2 storage change.
- Add focused test evidence. If the accepted API-017 implementation already satisfies a requirement, document the proof instead of gratuitous code changes; do not mutate its completed task definition/history.

## Out of Scope

- Re-creating API-017 intent/finalise/source lifecycle, changing Shopify code/storage paths, adding a second R2 signing implementation, new DB models, direct BullMQ publish, WordPress PHP or React uploads, or editing Gateway infrastructure.
- Reimplementing or changing the accepted ARCH-043 configuration reader, restoring legacy `MERCHANT_KNOWLEDGE_*` environment fallback, exposing root/unsealed secrets in browser responses, or modifying completed ARCH-043 task history.
- A permissive CORS policy or origin registration based solely on an untrusted browser `Origin` header.

## Requirements

- Retain canonical Woo authentication, `Shop.platform` check, tenant-scoped authorization and current revocation/rotation protections; browser sees a short-lived **object-scoped bearer URL**, never long-lived R2 or Moda credentials.
- Maintain existing `src/merchant/merchant-knowledge/` modules, `src/composition/merchant.ts` assembly, `src/auth/woo-installation/` principal and existing HTTP helpers. Any new cross-repository DTO/contract change requires an explicit compatibility decision, not an unreviewed competing implementation.
- No external network calls inside PostgreSQL transactions. Missing/invalid sealed R2 configuration fails the affected protected operation closed without aborting unrelated API startup; the existing knowledge-catalogue read also requires the upload-limit policy, so do not claim that only upload endpoints can be affected. Separate browser CORS transport from actual server authorisation.
- Add no generic duplicate HTTP telemetry; use `@modainteract/moda-interact-shared/logging` only within Node, with bounded redaction.

## Work Items

- [x] Audit API-017 signer/intent/finalise and versioned OpenAPI for browser compatibility and document existing guarantees, including replacement of obsolete PHP-only PUT guidance.
- [x] Verify accepted ARCH-043 configuration composition and per-operation `merchant.knowledge.r2` failure/redaction boundaries without introducing a second loader or fallback; add only missing focused consumer tests.
- [x] Exercise credential/bucket/policy change between intent and finalisation and document secure in-flight retry/failure behaviour.
- [x] Add deterministic browser-like signed PUT/header/redirect/expiry, idempotency and response privacy/security tests; correct only evidenced gaps in API-owned code.
- [x] Clarify exact `requiredHeaders`, expiry, safe error and no-store metadata contract for Woo/Gateway consumers.
- [x] Verify focused tests, typecheck, lint, production build and `git diff --check`; record evidence and Completion Report.

## Interfaces / Contracts

- Existing POST `/v1/merchant/merchant-knowledge/upload-intents` returns `schemaVersion: 1`, `assetId`, `uploadUrl`, `expiresAt`, `maxUploadBytes`, `requiredHeaders`. `uploadUrl` is an opaque signed capability, never stored beyond the active upload or sent to telemetry. `requiredHeaders` must be forwarded **exactly** in browser PUT (including required conditional and metadata headers).
- Browser PUT: `PUT <returned presigned R2 HTTPS S3 API URL>` with signed headers, file bytes, no Moda auth/WordPress cookie/CSRF header. Redirects are errors; WOO-014/015 must treat unsuccessful PUT or network/CORS failure as not finalised.
- R2 configuration owner: accepted `ARCH-043-API-002`; exact key `merchant.knowledge.r2` is read via `ApiPlatformConfigurationReader` per operation and unsealed with deployment-held root material. API-018 owns only browser contract compatibility/hardening and evidence, not the configuration service.
- Existing POST `/v1/merchant/merchant-knowledge/upload-finalize` remains authenticated through WordPress and authoritative on object verification. R2 CORS configuration belongs to GATEWAY-001, not this task.

## Dependencies

- `ARCH-035-API-017` — Complete in the inspected snapshot; reconfirm canonical task status before claim.
- `ARCH-043-API-002` — Complete in the inspected snapshot; owns accepted database-managed R2 configuration consumer wiring and must not be duplicated.

## Enables

- `ARCH-035-WOOCOMMERCE-014`
- `ARCH-035-GATEWAY-001`

## Acceptance Criteria

- [x] Existing signed URL/headers are consumable via a browser-compatible PUT without transferring bytes through Moda API or WordPress PHP.
- [x] Wrong headers, tampered URL, expired signature, overwrite replay and wrong bytes fail safely; finalisation verifies content, not a client success claim.
- [x] Authenticated, tenant-bound intent is no-store and signed capability values do not reach logs/error responses or another tenant.
- [x] Documented contract enables WOO-014/015 and Gateway origin/header configuration; no completed API-017 or ARCH-043 task/repository modified.
- [x] PostgreSQL-backed sealed `merchant.knowledge.r2` remains the sole production R2 credential/policy source; absence, tampering and unseal failure do not fall back to old environment fields or leak credentials.
- [x] A configuration change between signed intent and finalisation has deterministic, secure behaviour with no false successful activation or verification of the wrong object.
- [x] No `docs/decisions/**/_index.md` files changed.

## Validation

- [x] Focused API signer/route/OpenAPI security tests, ARCH-043 consumer/configuration failure tests and browser-like HTTP mock integration (including mid-upload configuration change); mark actual cross-origin provider checks as Gateway/system-test evidence rather than claiming browser CORS proof here.
- [x] Repository-prescribed typecheck, lint, relevant unit/integration tests, build if required by task, `git diff --check`.
- [x] Completion Report with exact checks, paths, assertions, any unchanged-code proof and canonical dual-worktree/commit evidence.

## Stop Condition

Set task to `review`, return Completion Report to `moda_architect` and STOP when scoped Work Items, Acceptance Criteria and validation are complete. Do not execute Gateway or Woo tasks.

## Implementation Notes

- Use the accepted `src/merchant/merchant-knowledge/upload-{contract,r2,service,routes}.ts` as the starting point, together with `src/platform-configuration/` and its composition wiring. Do not create a second upload/configuration service or duplicate signing code.
- A real browser CORS preflight is controlled by R2 bucket origin/header policy in GATEWAY-001, not by the API; record that as an explicit deployment dependency.
- Preserve previous accepted API-017 source and test baseline; if the current implementation passes all browser compatibility proofs, this task can be documentation/tests only.

## Completion Report

### Status

Review — Attempt 1 submitted by developer after accepted self-review. Implementation commits `939fdb3` and `4de3f18` are published on `origin/task/ARCH-035-API-018`. Explicit developer completion decision is pending.

### Files Changed

`moda-interact-api/docs/arch035-browser-direct-knowledge-upload.md`; `docs/arch035-knowledge-upload.md`; `openapi/merchant-knowledge-v1.yaml`; `src/merchant/merchant-knowledge/upload-r2.ts`; `src/merchant/merchant-knowledge/upload.service.ts`; `tests/fixtures/merchant-knowledge/verify-presigned-put.ts`; `tests/unit/merchant/merchant-knowledge/upload-browser-{openapi,routes,transport}.test.ts`; `tests/unit/platform-configuration/api-consumers.test.ts`.

### Work Completed

Certified the existing API-017 signed intent/finalise lifecycle for browser-direct Blob PUT without adding a second upload path. Updated API-owned signer guidance and versioned OpenAPI, and documented exact required headers, TTL/expiry, no-store/privacy, safe failure/retry semantics, R2 CORS ownership, rollout order and the limitation that local HTTP fixtures do not prove browser CORS. Added an independent SigV4 verifier and deterministic browser-like HTTP transport coverage. Added a consumer regression creating an intent under valid sealed R2 configuration, then revoking configuration before finalization; the fresh read returns bounded 503 before R2 verification or asset activation. Existing API-017 source lifecycle remains unchanged.

### Validation Results

Passed: focused browser/configuration tests (15/15); `npm test` (479/479); `npm run test:arch035-knowledge-upload:postgres` (1/1 migration-backed lifecycle test including replay/retry, replacement, reprocess, entitlement-off and expiry); `npm run typecheck`; `npm run lint` (`eslint . --max-warnings=0`); `npm run build`; `git diff --check`. No real Cloudflare bucket/browser CORS test was claimed; that evidence belongs to GATEWAY-001/system certification.

### Deviations

No API-017 or ARCH-043 implementation was changed. The only implementation addition after initial task commit `939fdb3` is the focused revocation regression in commit `4de3f18`. R2 CORS/provider behavior remains explicitly outside API-018 and is deferred to Gateway/system validation.

### Assumptions

API-017's accepted migration-backed lifecycle test remains a suitable verification of unchanged idempotent-finalize/replay semantics; it was rerun successfully against this implementation branch. Local Node HTTP fixtures verify request composition and modeled OPTIONS responses only; they do not emulate browser enforcement or Cloudflare R2 policy.

### Unresolved Issues

No API-018 implementation blocker remains. The real approved-origin R2 CORS/preflight and provider PUT remains for GATEWAY-001/system validation. Dependency-frontier check found WOOCOMMERCE-014 already in progress and left untouched. GATEWAY-001 is pending and depends only on this task; its canonical parent task worktree is not registered/present, so its task record was not mutated from a noncanonical checkout.

### Architectural Concerns

No cross-repository contract or R2 identity mismatch remains. Do not claim a live browser CORS pass based on the local fixture.

## Architect Review

### Review Status

Developer Self-Review Accepted for Attempt 1; explicit developer completion decision pending.

### Review Notes

Accepted. The API-017 signer and route contract remain object-scoped, tenant-authenticated and no-store. The browser fixture verifies exact signed headers, Blob bytes, credentials omission, redirect rejection, signature expiry/tampering, overwrite precondition and wrong-byte rejection. The new consumer regression proves a revoked sealed configuration is freshly read and stops finalization before object verification or activation. Full unit, typecheck, lint, build and migration-backed upload lifecycle validations passed. Live R2 CORS remains Gateway-owned.

### Reviewed Files

Implementation commits `939fdb3` and `4de3f18`; API-018 browser contract docs/OpenAPI, signer compatibility adjustment, browser transport/route/OpenAPI tests and configuration-revocation regression.

### Validation Reviewed

Focused browser/configuration tests 15/15; full API unit suite 479/479; disposable PostgreSQL upload lifecycle 1/1; typecheck, lint, build and diff check passed.

### Architecture Conformance

Conforms to API-018 scope. Existing API-017 state/persistence is reused; no PHP or Gateway code, completed task definition, ARCH-043 implementation, or `_index.md` file was changed. Live R2 CORS/provider validation is clearly deferred to its owner.

### Follow-up

Developer Self-Review Accepted. Per `completion_mode: developer`, the explicit completion command is pending. After that transition, reconcile downstream eligibility without starting either enabled task.

### Developer Self-Review

- Decision: Accepted
- Attempt: 1
- Implementation revisions: `939fdb3`, `4de3f18` (`origin/task/ARCH-035-API-018`)
- Evidence: Focused browser/configuration suite 15/15; full API unit suite 479/479; migration-backed PostgreSQL upload lifecycle 1/1; typecheck, lint, production build and `git diff --check` passed.
- Findings: Mid-flow R2 configuration revocation is covered and fails closed before verification/activation. Real R2 CORS is not an API-owned validation and remains Gateway/system evidence.

### Developer Completion Decision

Pending explicit developer completion command. Attempt 1 remains unchanged.
