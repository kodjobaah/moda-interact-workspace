---
id: ARCH-035-API-018
architecture_id: ARCH-035
title: Certify and adapt accepted Woo knowledge presigned upload for browser-direct PUT
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 46
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-035-API-017]
enables: [ARCH-035-WOOCOMMERCE-014, ARCH-035-GATEWAY-001]
created: 2026-10-17
updated: 2026-10-17
---

# ARCH-035-API-018 — Browser-direct R2 signing compatibility and secure metadata handoff

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, 17 October browser-direct upload amendment.
- Owner: `moda_api`, `moda-interact-api`. **Defined but not materialised**: this uploaded snapshot cannot create the canonical task branches or worktrees.

## Objective

Prove and, only where necessary, minimally adapt the existing accepted API-017 presigned upload-intent contract for direct browser-to-R2 `PUT` without reimplementing upload persistence or finalisation.

## Context

`ARCH-035-API-017` is already **Complete (Attempt 1)**. Current `src/merchant/merchant-knowledge/upload.service.ts` returns `schemaVersion`, `assetId`, short-lived `uploadUrl`, `expiresAt`, `maxUploadBytes`, and `requiredHeaders` (`Content-Type`, `If-None-Match: *`, `x-amz-meta-sha256`). `upload-r2.ts` signs a bounded `PutObject` to the approved HTTPS R2 S3 endpoint and `finalize` verifies actual object bytes and metadata. Prior task text says PHP sends the bytes; that historical task is **not** to be modified or reopened. The browser transport needs explicit compatibility proofs, strict response/privacy guarantees and a consumer-ready contract.

## Scope

- Inspect API-017 signer/intent/finalise and `openapi/merchant-knowledge-v1.yaml` as implemented, including hosted response cache headers, URL/host restrictions and precise signed-header case/value preservation.
- Confirm a standard browser `fetch`/XHR `PUT` with a `Blob` can send exactly the signed headers and bytes to the R2 S3 API endpoint without API, WordPress or cookie credentials. Provide deterministic browser-like HTTP fixture tests, including `OPTIONS` preflight assumptions for Gateway, not a fabricated browser preflight pass.
- Preserve R2 `Content-Type`, `If-None-Match: *`, `x-amz-meta-sha256` signatures, TTL ≤ the durable upload-intent expiry, immutable object identity, idempotent duplicate finalize and verified SHA-256/length before activation.
- Ensure only the authenticated Woo principal receives the complete signed URL and required headers from the upload intent, with no-store responses and no logging/reflection of signed query parameters, file contents, keys or installation credentials; adjust API HTTP/OpenAPI output only if an evidenced gap exists.
- Document exact browser upload contract, safe error semantics (signature expired, redirect, bad header, R2 412, CORS unavailable, cancelled upload and finalize failure), environment-scope and rollout ordering for WOO-014/015 and Gateway; use shared Node logging conventions for any added diagnostics.
- Add focused test evidence. If the accepted API-017 implementation already satisfies a requirement, document the proof instead of gratuitous code changes; do not mutate its completed task definition/history.

## Out of Scope

- Re-creating API-017 intent/finalise/source lifecycle, changing Shopify code/storage paths, adding a second R2 signing implementation, new DB models, direct BullMQ publish, WordPress PHP or React uploads, or editing Gateway infrastructure.
- A permissive CORS policy or origin registration based solely on an untrusted browser `Origin` header.

## Requirements

- Retain canonical Woo authentication, `Shop.platform` check, tenant-scoped authorization and current revocation/rotation protections; browser sees a short-lived **object-scoped bearer URL**, never long-lived R2 or Moda credentials.
- Maintain existing `src/merchant/merchant-knowledge/` modules, `src/composition/merchant.ts` assembly, `src/auth/woo-installation/` principal and existing HTTP helpers. Any new cross-repository DTO/contract change requires an explicit compatibility decision, not an unreviewed competing implementation.
- No external network calls inside PostgreSQL transactions; missing R2 configuration fails only upload operations closed. Separate browser CORS transport from actual server authorization.
- Add no generic duplicate HTTP telemetry; use `@modainteract/moda-interact-shared/logging` only within Node, with bounded redaction.

## Work Items

- [ ] Audit API-017 signer/intent/finalize and versioned OpenAPI for browser compatibility and document existing guarantees.
- [ ] Add deterministic browser-like signed PUT/header/redirect/expiry, idempotency and response privacy/security tests; correct only evidenced gaps in API-owned code.
- [ ] Clarify exact `requiredHeaders`, expiry, safe error and no-store metadata contract for Woo/Gateway consumers.
- [ ] Verify focused tests, typecheck, lint, production build and `git diff --check`; record evidence and Completion Report.

## Interfaces / Contracts

- Existing POST `/v1/merchant/merchant-knowledge/upload-intents` returns `schemaVersion: 1`, `assetId`, `uploadUrl`, `expiresAt`, `maxUploadBytes`, `requiredHeaders`. `uploadUrl` is an opaque signed capability, never stored beyond the active upload or sent to telemetry. `requiredHeaders` must be forwarded **exactly** in browser PUT (including required conditional and metadata headers).
- Browser PUT: `PUT <returned presigned R2 HTTPS S3 API URL>` with signed headers, file bytes, no Moda auth/WordPress cookie/CSRF header. Redirects are errors; WOO-014/015 must treat unsuccessful PUT or network/CORS failure as not finalised.
- Existing POST `/v1/merchant/merchant-knowledge/upload-finalize` remains authenticated through WordPress and authoritative on object verification. R2 CORS configuration belongs to GATEWAY-001, not this task.

## Dependencies

- `ARCH-035-API-017` — Complete in the inspected snapshot; reconfirm canonical task status before claim.

## Enables

- `ARCH-035-WOOCOMMERCE-014`
- `ARCH-035-GATEWAY-001`

## Acceptance Criteria

- [ ] Existing signed URL/headers are consumable via a browser-compatible PUT without transferring bytes through Moda API or WordPress PHP.
- [ ] Wrong headers, tampered URL, expired signature, overwrite replay and wrong bytes fail safely; finalisation verifies content, not a client success claim.
- [ ] Authenticated, tenant-bound intent is no-store and signed capability values do not reach logs/error responses or another tenant.
- [ ] Documented contract enables WOO-014/015 and Gateway origin/header configuration; no completed API-017 task or unrelated repository modified.
- [ ] No `docs/decisions/**/_index.md` files changed.

## Validation

- [ ] Focused API signer/route/openapi security tests and browser-like HTTP mock integration; mark actual cross-origin provider checks as Gateway/system-test evidence rather than claiming browser CORS proof here.
- [ ] Repository-prescribed typecheck, lint, relevant unit/integration tests, build if required by task, `git diff --check`.
- [ ] Completion Report with exact checks, paths, assertions, any unchanged-code proof and canonical dual-worktree/commit evidence.

## Stop Condition

Set task to `review`, return Completion Report to `moda_architect` and STOP when scoped Work Items, Acceptance Criteria and validation are complete. Do not execute Gateway or Woo tasks.

## Implementation Notes

- Use the accepted `src/merchant/merchant-knowledge/upload-{contract,r2,service,routes}.ts` as the starting point. Do not create a second upload service or duplicate signing code.
- A real browser CORS preflight is controlled by R2 bucket origin/header policy in GATEWAY-001, not by the API; record that as an explicit deployment dependency.
- Preserve previous accepted API-017 source and test baseline; if the current implementation passes all browser compatibility proofs, this task can be documentation/tests only.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the inspected baseline.

### Unresolved Issues

None known; browser R2 policy requires separate Gateway acceptance.

### Architectural Concerns

Escalate any Shared/Background/Gateway dependency gap rather than changing cross-repository code.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None.
