---
id: ARCH-026-API-007
architecture_id: ARCH-026
title: Acquire and manage merchant-approved WooCommerce read grants
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 31
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-026-DATABASE-003
  - ARCH-026-API-002
enables:
  - ARCH-026-API-008
  - ARCH-026-WOOCOMMERCE-015
created: 2026-10-10
updated: 2026-10-13
---

# Acquire and manage merchant-approved WooCommerce read grants

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Complete WooCommerce's native, merchant-approved `scope=read` application-authorisation flow and retain a verified, encrypted Woo REST credential for exactly the authenticated installation's Shop.

## Context

`WooInstallationConnectionService`, `WooInstallationAuthenticator` and their existing OpenAPI contract establish a credential for **Woo plugin -> Moda API** calls. They do not grant **Moda -> WooCommerce wc/v3** access. WooCommerce officially supports an application authorisation URL at `/wc-auth/v1/authorize`, with `app_name`, `scope`, `user_id`, `return_url` and `callback_url`. After merchant approval it posts a JSON consumer key/secret to the HTTPS callback and separately redirects the browser with a `success` indicator. Those two notifications may arrive in either order; the browser return is not proof of a usable grant.

## Scope

`moda-interact-api` only:

- Add an installation-principal-authenticated authorisation-start command and a read-only grant-status projection, plus a separate revoke-local-credential command.
- Construct a WooCommerce `scope=read` authorization URL bound to the verified installation and canonical site; handle a public HTTPS JSON callback using a single-use short-lived attempt.
- Validate a callback's exact pending attempt, declared `key_permissions=read` and credential possession against the same verified Woo store before writing an encrypted grant.
- Reuse the API's existing bounded site-identity/SSRF protection and canonical shared structured logger; add a versioned API-owned OpenAPI contract and focused tests.

## Out of Scope

- Any WooCommerce `write` or `read_write` consent; modifying orders, discounts, products or provider API keys.
- Running outgoing CommerceAgent/MCP Woo REST tools; handled separately from granting credentials.
- Altering the existing Connect HMAC verification, Free activation, subscription, entitlement credits or Shopify install flow.
- React/PHP plugin UI, changing WordPress user capabilities, a generic OAuth server, or giving raw credentials to clients.
- Auto-revoking the provider's key using `DELETE /wc/v3/...`: a read-only key cannot be assumed able to delete itself.

## Requirements

1. **Start:** Authenticate via the existing `WooInstallationAuthenticator` and resolve `shopId`, installation ID/version and canonical site from the server-side principal; reject inactive, revoked or inconsistent Woo tenants. Create a short-lived unpredictable opaque attempt, store only its digest, bind it to the installation generation, and return a browser-usable Woo auth URL with `scope=read` only. Generate `user_id` as a bounded opaque Moda attempt reference, **never** a merchant-supplied Shop ID. Use fixed API-owned HTTPS callback and approved return destinations; no caller-chosen redirects, callback hosts or scopes.
2. **Callback:** Handle WooCommerce's server-to-server JSON POST to the HTTPS `callback_url` using an unpredictable, expiring, one-use attempt token bound to the request path. Treat the callback as **unauthenticated until its attempt and provider credentials are verified**: its `user_id`, key ID and claimed permission are not independent proof of Shop identity. Recheck installation/Shop identity, attempt expiry and version immediately before commit. Require declared `key_permissions` exactly `read`, not `read_write`, and verify credential possession with a bounded, no-write `wc/v3` request to the exact canonical store before activating the grant. A callback alone never authorises a write operation.
3. **Transport safety:** Perform the provider verification over public HTTPS under the existing API-002 pinned-address/peer/TLS/no-redirect/size/deadline controls. Only the explicitly enabled non-production local-development mode may use a local Woo origin, and it must preserve every other check. A non-routable LocalWP environment must use an approved reachable test topology or report a blocked real-provider validation; never silently relax production SSRF/TLS rules.
4. **Encryption and races:** Use audited authenticated encryption (e.g. AES-256-GCM), server-only environment keyring with key identifiers and authenticated context binding to the installation, with no plaintext database field. Reject missing keys/keyring and fail closed on decrypt failure. Atomic consumption and compare-and-swap must prevent duplicate callbacks or old reconnect attempts from replacing a newer grant. Support explicit re-authorisation/rotation without changing Moda's installation credential.
5. **Return/status:** The browser `return_url` `success` parameter is advisory only. `GET` grant status reflects the **committed, verified** server-side state; callback-before-return and return-before-callback must converge. Denial, expiration and callback/provider failures leave Moda Connect and automatic Free billing intact. Status responses return no consumer key, consumer secret, nonce, ciphertext or untrusted callback data.
6. **Revocation:** An authenticated installation may revoke Moda's stored outgoing grant. All subsequent reads must fail closed. Document and signal that the Woo key may still exist at `WooCommerce > Settings > Advanced > REST API` and must be revoked there by an authorised store administrator; no unapproved provider write/delete API use.
7. **API contract and observability:** Define strict request/response bodies, size limits, no-store responses and bounded errors in `openapi/woocommerce-read-authorization-v1.yaml` (or equivalent versioned API-owned contract). Reuse Shared structured logging for semantically named start/approve/deny/revoke/failure events, bounded IDs/reasons only. Never log callback URLs with bearer tokens, HTTP Authorization headers, Woo keys/secrets or provider response bodies. Ensure the existing gateway API host route can deliver the HTTPS callback; do not add a Gateway task unless evidence shows it is needed.

## Work Items

- [x] Define the authenticated start, status and revoke routes plus public callback route and versioned OpenAPI document.
- [x] Implement attempt token creation/digest, site-bound authorisation URL and bounded expiry/consumption rules.
- [x] Implement strict callback parser, grant verification through pinned/no-redirect GET, authenticated encryption and transaction-safe activation.
- [x] Implement safe re-authorisation, stale attempt rejection and local credential revocation/status projections.
- [x] Add API unit/route/OpenAPI/PostgreSQL tests for callback order, replay, denial, key-permission mismatch, shop mismatch, reconnect and encryption failures.
- [x] Confirm existing Connect/reconnect/Free-plan behaviour is unchanged.

## Interfaces / Contracts

- **HTTP owner:** `moda_api`. API-owned versioned OpenAPI contract for `POST /v1/woocommerce/read-authorizations`, `GET /v1/woocommerce/read-authorization`, `DELETE /v1/woocommerce/read-authorization`, and server-only `POST /v1/woocommerce/read-authorizations/callback/{opaqueAttemptToken}` (final names recorded in OpenAPI and used consistently by Woo PHP).
- **Authenticated producer:** `ARCH-026-WOOCOMMERCE-015` calls start/status/revoke with the existing installation credential via PHP. The public callback comes from WooCommerce, not the browser or PHP facade.
- **Persistence:** `ARCH-026-DATABASE-003` owns grant/attempt schema; API-007 alone handles key material.
- **Provider:** WooCommerce's documented `/wc-auth/v1/authorize` contract with `scope=read`; see https://developer.woocommerce.com/docs/apis/rest-api/authentication.

## Dependencies

- `ARCH-026-DATABASE-003` — grant and one-use pending-attempt schema.
- `ARCH-026-API-002` — accepted installation principal, canonical Woo URL and SSRF-safe site verifier.

## Enables

- `ARCH-026-API-008`.
- `ARCH-026-WOOCOMMERCE-015`.

## Acceptance Criteria

- [x] Only the authenticated, active Woo installation can initiate/grant/revoke access to its own Shop; the callback cannot attach credentials to a different Shop.
- [x] Generated Woo consent URLs request exactly `scope=read`; callback permission claims other than `read` fail closed.
- [x] A usable credential is verified against the exact canonical Woo store before an encrypted grant is committed; raw keys are absent from browser, logs and database plaintext.
- [x] Either callback/return arrival order, retry, double click, expiry, denial or reconnect race produces one consistent grant state and no cross-shop credential replacement.
- [x] Revoke/invalid-key handling prevents later reads and shows merchant-controlled provider-side key revocation requirements.
- [x] Connection, Free subscription, credits and existing installation credential/version are unchanged by grant success or failure.

## Validation

- [x] `npm run typecheck`.
- [x] `npm run lint`.
- [x] `npm test` with focused route/credential/parser cases.
- [x] `npm run test:integration` with disposable PostgreSQL for duplicate callback, stale generation, tenant and encryption lifecycle.
- [x] Record blocked evidence for the real Woo callback/return smoke: no approved non-production Woo store and publicly reachable HTTPS callback fixture was supplied for this run; production transport protections were not relaxed.
- [x] `git diff --check` and task-worktree/synchronization evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation pass, set task to `review`, return the Completion Report to `moda_architect` and STOP. Do not implement Woo PHP/React, the outbound read transport, or Commerce/MCP tool execution.

## Implementation Notes

The callback contains secrets, so its request logging, error handling and HTTPS termination are security-sensitive. WooCommerce's `user_id` fields in callback/return messages are **not** a substitute for the server-generated attempt bearer and verified principal binding. The callback token in a URL is itself sensitive: avoid emitting full callback URLs to logs/traces. AES-GCM keys must never be committed. No staff-admin Commerce connection record should be invented to satisfy the merchant credential write.

## Completion Report

### Status

Complete after explicit developer acceptance of attempt 1.

### Files Changed

No API source changes were made in this attempt. The authorization service, routes, OpenAPI contract and focused tests were already present in the synchronized `origin/main` implementation baseline before this task claim. This task report is the only task-owned parent change in this reconciliation.

### Work Completed

- Reconciled the existing API-007 implementation in `src/woocommerce/rest-read/` and `openapi/woocommerce-read-authorization-v1.yaml`: authenticated start/status/revoke, one-use digest-backed callback attempts, exact `read` scope validation, same-shop provider credential verification, AES-GCM envelope storage, transaction-safe activation/rotation, bounded no-redirect provider transport, and advisory browser return.
- Verified focused authorization, route, OpenAPI and PostgreSQL tests are present. The source implementation is inherited from `origin/main`; the implementation task branch has no task-exclusive source diff.
- Recorded the developer-supplied architectural assessment that the implementation meets requirements based on validation, while leaving formal completion to the Architect Review.

### Validation Results

Passed `npm run typecheck` (including Prisma Client generation) and `npm run lint` in the canonical implementation task worktree.

Passed `npm test`: 276 tests total, 235 passed, 0 failed, 41 database-fixture-dependent tests skipped in this unit-suite invocation. The separate integration command ran its declared PostgreSQL suites, including API-007 authorization/provider coverage.

Passed `npm run test:integration`: the disposable PostgreSQL suites completed with no failures. The Woo authorization/provider-specific cases passed 4/4, covering callback persistence/ciphertext/replay/revocation, rotation ordering, stale installation generation, and bounded provider read/revocation behavior. The harness applied the ordered Prisma migrations and removed its disposable fixtures.

Passed `git diff --check` for both canonical task worktrees. The implementation worktree was clean and based on `origin/main`; no source changes were made. The parent task branch contains the durable claim and this review report.

Blocked/not run: a real merchant-approved Woo authorization callback/return smoke test requires a non-production Woo store and publicly reachable HTTPS callback fixture. Neither was supplied for this run; no production SSRF/TLS protections were weakened.

### Deviations

The implementation already existed in the synchronized API `origin/main` baseline before attempt 1 began. No duplicate source changes were introduced on the task branch. The real-provider smoke test remains blocked on external non-production HTTPS test infrastructure.

### Assumptions

The architectural assessment supplied with this reconciliation is based on validation evidence outside the task record; the local checks above were rerun and recorded independently.

### Unresolved Issues

The real-provider callback/return smoke remains unrun because an approved non-production Woo store and publicly reachable HTTPS callback were unavailable. The required validation permits explicit blocked evidence for this prerequisite; no production transport protections were relaxed.

### Architectural Concerns

No task-specific source delta exists because the implementation is inherited from `origin/main`. The live callback/return path has not been exercised against a real merchant-approved Woo store in this run.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Do not implement Woo PHP/React or other downstream work under API-007. Downstream tasks may proceed according to their own explicit dependencies.

## Developer Completion Decision

### Decision

Accepted attempt 1 and explicitly completed the task via `/moda_developer_update ARCH-026-API-007 complete`.

### Review Basis

The developer-supplied architectural assessment states that API-007 meets its requirements based on reported validation. The task report records all Work Items and Acceptance Criteria complete, and independent validation passed for typecheck, lint, unit tests (235 passed, 0 failed; 41 fixture-dependent skips), and PostgreSQL integration (4/4 authorization/provider tests passed). The live Woo callback smoke limitation is explicitly recorded and matches the task's blocked-evidence alternative.

### Publication

The parent completion decision is committed on `task/ARCH-026-API-007`. The implementation task branch is committed/pushed at the validated source baseline; no task-specific source diff was required because the implementation was already present in `origin/main`. No task branch was merged to `main`.

### Dependency Frontier

Reconciled after completion: `ARCH-026-API-008` and `ARCH-026-WOOCOMMERCE-015` are eligible because all of their explicit dependencies are complete. Their parent task records are advanced from `pending` to `ready`. `ARCH-026-SYSTEM-TEST-001` remains `pending`; API-008 and WOOCOMMERCE-015 are not yet complete.
