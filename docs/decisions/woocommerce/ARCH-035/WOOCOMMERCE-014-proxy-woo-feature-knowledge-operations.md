---
id: ARCH-035-WOOCOMMERCE-014
architecture_id: ARCH-035
title: Proxy feature preferences and Merchant Knowledge through WordPress
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-035-API-014, ARCH-035-API-015, ARCH-035-API-016, ARCH-035-API-017, ARCH-035-API-018]
enables: [ARCH-035-WOOCOMMERCE-015]
created: 2026-10-16
updated: 2026-10-17
---

# ARCH-035-WOOCOMMERCE-014 — Proxy feature preferences and Merchant Knowledge through WordPress

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_woocommerce`, repository `moda-interact-woocommerce`; coordinator: `moda_architect`.
- **Re-gated on 2026-10-17:** earlier materialised parent task definition was Ready, but the new browser-direct transport requires architect-accepted API-018 before implementation can start. Status is now `pending`, with no active executor/claim in the supplied snapshot. The real launcher verifies parent and implementation worktrees before execution.

## Objective

Implement privileged server-mediated WordPress REST proxies for approved Woo feature-preference, knowledge-source and file operations.

## Context

W003/W004 currently have production unavailable adapters. The hosted API tasks own authoritative state and validation; WordPress remains a security boundary and Woo site identity/credential guard.

## Scope

- Add bounded WordPress PHP REST routes and API client methods mapping the exact accepted API-014..017 contracts; enforce `manage_woocommerce`, nonce, connected Shop credential, site identity, revocation and safe error remapping on every request.
- WordPress PHP remains the only browser-to-hosted-Moda API caller, with timeouts, bounded **metadata JSON** bodies/responses, strict schema and nonce/session/installation guards. PHP must not receive or forward CSV/XLSX file bytes.
- For uploads: PHP proxies authenticated **metadata-only** intent/finalise requests; on intent, validate and forward only the bounded API-018-approved presigned `uploadUrl`, expiry, `assetId`, limits and exact required headers to the authorised WordPress browser with no-store response. On finalise, recheck connection/session/nonce and send metadata to API-017. PHP never accepts, buffers, streams, proxies, persists or logs the file contents.
- Do not expose installation secrets in browser/logs; re-read installation guard before writes, reject stale credentials/changes, and preserve existing two-stage menus.
- Add PHP tests for authenticated/denied/revoked/cross-installation metadata operations, response no-store/cache safety, unknown signed host/URL/header rejection, safe error mapping and rejection of binary/multipart upload attempts.

## Out of Scope

- Implementing business/entitlement decisions, hosted API endpoints, database schemas or browser React presentation.
- Issuing/uploading R2 object bytes in PHP, adding permissive R2 CORS or WordPress persistent file storage. R2 CORS belongs to GATEWAY-001 and browser transfer to WOO-015.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. WooCommerce must not import `@modainteract/moda-interact-shared/logging` into PHP or browser code. Where diagnostic logging is genuinely needed in the WordPress plugin, use existing WordPress/WooCommerce facilities with bounded, redacted metadata; the hosted Node.js API owns shared-logger integration.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [ ] Add bounded WordPress PHP REST routes and API client methods mapping the exact accepted API-014..017 contracts; enforce `manage_woocommerce`, nonce, connected Shop credential, site identity, revocation and safe error remapping on every request.
- [ ] Implement bounded metadata JSON requests/responses; reject multipart/file-body upload requests; preserve strict nonce/session and credential handling.
- [ ] Expose the signed R2 PUT URL and **exact** signed headers to an authorised browser from a no-store WordPress response; broker finalisation metadata after connection revalidation. No PHP binary transport or local temporary file.
- [ ] Do not expose installation secrets in browser/logs; re-read installation guard before writes, reject stale credentials/changes, and preserve existing two-stage menus.
- [ ] Add PHP tests for authenticated/denied/revoked/cross-installation intent/finalise, non-cacheable signed-capability response, binary rejection, error mapping and bounded metadata validation.
- [ ] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- WordPress `moda-interact/v1` privileged REST operations, using existing facade conventions and accepted API-014..017 endpoint paths plus the API-018 browser upload capability contract. No direct browser-to-hosted Moda API.
- Proxy canonical server responses and HTTP conflict/errors without fabricating success.

## Dependencies

- `ARCH-035-API-014` (must be Complete and architect accepted)
- `ARCH-035-API-015` (must be Complete and architect accepted)
- `ARCH-035-API-016` (must be Complete and architect accepted)
- `ARCH-035-API-017` (Complete; historical upload lifecycle unchanged)
- `ARCH-035-API-018` (must be Complete and architect accepted)

## Enables

- `ARCH-035-WOOCOMMERCE-015`

## Acceptance Criteria

- [ ] Every request enforces nonce, capability, connected-state, canonical-site identity and installation credential; no browser-to-hosted API direct path.
- [ ] Browser receives signed R2 URL and required headers **only** through a privileged no-store intent response; WordPress does not receive file bytes, and server-side finalisation remains authoritative. Unauthorised callers, unsafe URL destinations, redirect/replay and malformed headers fail closed; signed URL is not logged or exposed through errors.
- [ ] No changes to existing Billing/recovery-policy/site categories routes; one failed R2 step does not claim uploaded/active state.
- [ ] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [ ] Focused PHPUnit proxy auth/nonce/capability, signed-intent/finalise metadata, no-store, binary rejection, unsafe URL, malformed response and upstream failure mapping tests.
- [ ] PHP lint, repository declared JS/PHP/build/ZIP checks as changed, `git diff --check`.
- [ ] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled WooCommerce-structure handoff (2026-10-16 22:56 snapshot)

- Extend the existing PHP plugin boundaries: register privileged route controllers through `includes/Runtime.php`, place domain controllers in `includes/Rest/`, add hosted API methods in `includes/Api/ModaApiClient.php` (or a narrow delegated client), and add strict response validation under `includes/Api/`. Do not wire PHP requests into a React view or create a parallel installation-credential resolver.
- Match existing `StoreCategoryController.php`, `RecoveryPolicyController.php` and `StoreContextController.php` patterns for the `moda-interact/v1` namespace, `manage_woocommerce`, WordPress REST nonce/session enforcement, canonical site-URL guard, connection record, `ModaApiClientException` and status mapping. Test both denied and stale-site/rotated-credential cases.
- WordPress handles metadata-only intent and finalise. From authenticated API-018 contract, validate that the returned signed destination is HTTPS and exactly the approved R2 S3 endpoint with bounded expiry/headers; return that short-lived capability **only to the authorised administrator in a no-store response**. Never log the query string, store it in WordPress options, add installation credentials to R2 requests or accept binary in PHP. Browser sends bytes directly to R2; the API verifies finalisation. Recheck the current Woo site identity/credential before finalise and never infer success from the intent response.
- Keep browser-to-WordPress requests and PHP-to-Moda requests separately bounded. Add PHP controller/API client/response-contract tests within the existing `tests/` suite, plus negative tests for host validation, timeouts, malformed JSON and failure mapping. This task's implementation does **not** modify the native screen, which remains WOO-015's responsibility. No LocalWP startup, connection or interactive manual validation is assigned to the WOO-014 repository agent; use PHPUnit/HTTP fixtures for PHP boundary proofs. Any live LocalWP check is developer-owned and outside this task's agent Validation gate.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

Logging/runtime boundary: this is a WordPress/PHP proxy, not a Node.js service. Do not add `@modainteract/moda-interact-shared/logging`, another generic logger or a Node-only package to the plugin. Preserve existing error handling and fail-closed security checks. Optional PHP diagnostics must use bounded, redacted WordPress/WooCommerce facilities and must not expose installation credentials, authorisation headers, signed R2 URLs, uploaded file contents or customer data. The hosted `moda-interact-api` owns its own shared structured logging.

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

The uploaded ZIP represents a portable design baseline, not the developer's current on-disk branches. Confirm source, task status and dependency state with the launcher before execution.

### Unresolved Issues

None evidenced beyond the explicit implementation and test dependencies above.

### Architectural Concerns

Report any cross-repository contract, R2 identity, reconciliation or security mismatch to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation and validation evidence.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None until implementation submission.

## Dependency Frontier Reconciliation (2026-10-17)

API-017 was explicitly completed on its developer-owned task branch after an accepted review. Canonical task routes report all four declared prerequisites complete: API-014, API-015, API-016 and API-017. This unclaimed task is therefore promoted from `pending` to `ready`; `executor` and `claimed_at` remain null and `attempt` remains 0. The canonical parent task worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-014` on `task/ARCH-035-WOOCOMMERCE-014`, created from refreshed `origin/main` at `66b545426e1ced9dfbd05a79dde340db4cfc27f0`. No implementation worktree was created, no attempt was claimed, and no task or main branch was merged.
