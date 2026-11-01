---
id: ARCH-026-API-008
architecture_id: ARCH-026
title: Establish a shop-scoped WooCommerce read-only provider connection
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-API-007
enables:
  - ARCH-026-SYSTEM-TEST-001
created: 2026-10-10
updated: 2026-10-16
---

# Establish a shop-scoped WooCommerce read-only provider connection

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Provide an API-owned, authenticated **outbound** WooCommerce read connection that resolves the correct merchant's verified REST grant without exposing or rebuilding credentials in tool/MCP code.

## Context

`ARCH-026-API-007` acquires and encrypts the merchant-approved Woo REST grant, while the existing API-002 installation credential authenticates PHP -> Moda calls. Commerce already contains an ARCH-030-labelled `WooCommerceReadOperation` authoring catalogue, but its Woo REST review and runtime connection wiring are placeholders; the provider credential and outbound transport must be ready **without** fabricating or copying that unfinished tool-execution contract. API-008 is a bounded provider client, not the implementation of all Commerce Woo tools.

## Scope

`moda-interact-api` only:

- Resolve a shop's active Woo installation, canonical site, current read grant and decrypted consumer key/secret in a private server-only connection service.
- Implement a hardened HTTPS `GET` transport against permitted `wc/v3` read resource paths, with a bounded first proof for product list/detail operations.
- Expose a narrow in-process typed provider-read port for later approved service integration and focused integration tests; do **not** introduce a public generic Woo HTTP proxy.
- Classify missing, revoked, invalid, forbidden and temporarily unavailable provider access without changing the Moda installation or Free-plan state.

## Out of Scope

- A general-purpose HTTP connection editor, arbitrary URLs/headers, non-GET methods or direct browser access to the provider read port.
- Broad operation coverage, customer/order PII retrieval, MCP authoring/preview/publishing or the ARCH-030 provider runtime connector.
- Credential acquisition/rotation or revocation commands (API-007), Prisma schema changes or Shopify connection refactoring.
- An unauthenticated/public internal-read endpoint. Network/service-to-service exposure requires a separate approved contract and security assessment when a consumer is scheduled.

## Requirements

1. **One authoritative connection:** Given an already authorised Woo Shop identity, resolve its active Woo installation and single current grant from DATABASE-003. Reject Shopify tenants, missing or revoked installation state, site/domain mismatch, absent/unverified/invalid grant and stale credential generations. Never accept a caller-provided arbitrary origin or secret.
2. **Secret boundary:** Decrypt credentials only inside the API-owned server-side port with the approved keyring/AAD; never return key material to PHP, React, merchant APIs, MCP tools, telemetry or error results. Keep secret lifetime short and never put consumer credentials into query strings or request logs.
3. **Read-only transport:** Support `GET` only, with an initial explicit allowlist of the existing Commerce `products.list` and `products.retrieve` operation semantics (`/wp-json/wc/v3/products`, `/products/{id}`). Validate path IDs and bounded query arguments; default to the least-privileged `view` context, cap result count and body size, reject provider-supplied new URLs/redirects. The allowlist is an API security policy; do not duplicate the entire ARCH-030 authoring catalogue or pretend every catalogued GET is already supported by this service.
4. **SSRF and network:** Resolve the canonical site through the same public HTTPS, DNS/socket pinning, peer/TLS verification, no-redirect and deadline controls already established by API-002. Do not pass custom hostnames from tool arguments. Only the previously approved explicit local-development mode can use local Woo origins. Never fall back to credentials in query parameters if an upstream server rejects the `Authorization` header.
5. **Failure policy:** Treat provider `401`/`403`, local grant revocation, timeout, non-2xx, malformed/oversized JSON and network failures as bounded outcomes. Persist an invalid-grant status only when evidence supports loss of access, without erasing encrypted credentials in logs or touching `WooCommerceInstallation.credentialDigest`. Retry only safe read operations under bounded deadlines.
6. **Observability/privacy:** Emit bounded shop/operation/outcome metadata using Shared logging. Do not log customer information, provider bodies, raw URLs containing secrets or key envelopes. Avoid exposing other store resources merely because the Woo key is broadly read-permitted.
7. **Consumer boundary:** The in-process port is the stable initial provider connection abstraction. A later Commerce/MCP/Background consumer must use a separately approved, authenticated service-to-service adapter; this task does not invent an unreviewed cross-service HTTP or Shared package contract. Existing ARCH-030 authoring work remains independently owned by `moda_commerce`.

## Work Items

- [x] Implement explicit Shop/installation/grant resolution, AEAD decrypt and fail-closed state mapping.
- [x] Implement bounded, pinned `GET` transport for product list/detail read operations and safe response handling.
- [x] Add typed in-process provider-read interface and focused API unit/integration tests using test keys and stubbed Woo endpoints.
- [x] Verify the approved read-grant lifecycle and bounded read through the disposable Woo-compatible fixture, including the absence of credentials from results/logs. A live merchant-approved provider smoke was not available.

## Interfaces / Contracts

- **Input:** Trusted, pre-authorised `commerce.Shop.id` (not a browser-owned `shopId`) and API-approved read operation/arguments; API-008 resolves the provider origin and keys.
- **Output:** Bounded success/failure result with no authentication material. Later remote consumers require their own approved service authentication and transport contract; no HTTP endpoint is claimed here.
- **Persistence:** `ARCH-026-DATABASE-003` grant and `ARCH-026-DATABASE-001` installation.
- **Existing Commerce reference:** `moda-interact-commerce/src/commerce/woocommerce/read-operation-catalogue.ts` (`products.list`, `products.retrieve`) is authoring reference, not a newly published API contract.

## Dependencies

- `ARCH-026-API-007` — verified Woo read grants and credential encryption lifecycle.

## Enables

- `ARCH-026-SYSTEM-TEST-001` — real read-through proof following Woo authorisation.

## Acceptance Criteria

- [x] Two Woo shops with different credentials cannot read one another's data; missing/revoked/stale credentials fail closed.
- [x] Only provider-derived canonical origins and the initial two product GET operations are accepted. Arbitrary paths/headers, write verbs, redirects and unsafe DNS are rejected.
- [x] Provider credentials never enter WordPress, browser/React, MCP payloads, response metadata or logs.
- [x] Verified `read` credentials successfully fetch bounded product data from an approved Woo fixture; `401`, `403`, timeout and invalid JSON produce bounded failures.
- [x] Free subscription, entitlements, installation credential and onboarding status are unchanged by successful or failed provider reads.

## Validation

- [x] `npm run typecheck`.
- [x] `npm run lint`.
- [x] `npm test` with targeted GET allowlist, cryptography, SSRF, response and tenant-isolation cases.
- [x] `npm run test:integration` with disposable PostgreSQL grant fixtures and Woo-compatible HTTP server. Live provider proof was unavailable and is recorded as a limitation.
- [x] `git diff --check` and task-isolation/synchronization evidence.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set task to `review`, return its Completion Report to `moda_architect` and STOP. Do not implement Commerce/ARCH-030 read tools or expand to order/customer reads as opportunistic work.

## Implementation Notes

Do not make secrets available merely to avoid a later internal API decision. A read-only Woo key is not an authorization grant for arbitrary data exfiltration, and the provider's GET capability still requires Moda operation- and tenant-level enforcement. A future private broker, if needed by an extracted MCP server, must be separately designed with service-authenticated, shop-bound request attestation and approved network routing.

## Completion Report

### Status

API-008 implementation and local validation are present in the synchronized `origin/main` baseline and documented below. No API-008 execution attempt has been claimed; lifecycle remains `ready`, attempt 0. This report does not submit a review or complete the task.

### Files Changed

The implementation is inherited from `origin/main`; no API-008 source delta exists on `task/ARCH-026-API-008`. Relevant implementation and test files include:

- `src/woocommerce/rest-read/provider-connection.service.ts`
- `src/woocommerce/rest-read/product-operation.ts`
- `src/woocommerce/rest-read/provider-connection.test.ts`
- `src/woocommerce/rest-read/provider-connection.postgres.test.ts`
- `src/woocommerce/rest-read/provider-transport.test.ts`
- `src/woocommerce/rest-read/README.md`
- This task Completion Report.

### Work Completed

- Added a private in-process Woo product read port that resolves the installation and active `read` grant using the trusted Shop identity, rejects tenant/platform/site/generation mismatches, and decrypts the grant only inside the API service with the API-007 keyring and authenticated context.
- Added fixed `products.list` and `products.retrieve` operations with bounded arguments, `GET`-only pinned transport, response projection/size limits, no redirect handling, and bounded failure outcomes. The service rechecks the selected installation/grant after network I/O and withholds data if it was revoked or rotated during the request.
- Added tests for tenant credential separation, stale/revoked/missing grants, unsupported operations, secret/log isolation, cancellation and race/failure behavior, plus PostgreSQL integration from persisted grant through bounded Woo-compatible product GET and revocation.
- The implementation code and tests were already present on `origin/main` before the API-008 task worktree was created. The task branch currently contains no task-specific source change.

### Validation Results

Passed `npm run typecheck` (including Prisma Client generation) and `npm run lint` in the canonical API-008 implementation worktree.

Passed `npm test`: 276 tests total, 235 passed, 0 failed, 41 database-fixture-dependent tests skipped in this unit-suite invocation.

Passed `npm run test:integration`: all 40 tests across the declared disposable PostgreSQL integration suites passed, with 0 failures or skips. API-008 provider-specific PostgreSQL coverage passed 1/1 for approved read grant -> bounded product GET -> revocation/stale-generation fail-closed behavior. Fixture containers are removed by the harness.

Passed `git diff --check`. Canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-API-008` is clean on `task/ARCH-026-API-008`, based on and tracking its published mainline baseline; recursive `database` submodule is initialized at `42b1ee84d4190c9c4c812049e07de5004a22c1b9`. Canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-API-008` is clean before this report update and tracks its task branch.

Not run: live provider proof against a merchant-approved non-production WooCommerce store. The disposable Woo-compatible endpoint exercises the actual bounded transport and persistence flow; no live store/callback fixture was supplied.

### Deviations

API-008 source and tests are inherited from `origin/main`; they were not authored on this newly created task branch. Local PostgreSQL integration uses a Woo-compatible HTTP fixture rather than a live merchant store. No production data or transport-policy relaxation was used.

### Assumptions

The task's provider-read proof is satisfied for this reconciliation by the disposable Woo-compatible integration fixture; a live provider smoke remains useful external evidence but was unavailable.

### Unresolved Issues

The live merchant-approved Woo read smoke has not been run. No API-008 task attempt has been claimed, so this report does not transition the task to review or complete.

### Architectural Concerns

No source diff is owned by the API-008 task branch because the API implementation is already in the mainline baseline. Keep the provider port in-process and preserve the task's prohibition on an unapproved cross-service broker or broader Woo read surface.

## Architect Review

### Review Status

Accepted — retrospective implementation-evidence reconciliation, 2026-10-16.

### Review Notes

The shop-scoped, server-only WooCommerce provider read port and bounded product operations exist; credential resolution enforces installation/grant consistency, canonical site and grant freshness, with fail-closed failures and no public credential route.

This is an explicit architecture-level retrospective closure based on the 2026-10-16 supplied code snapshot, **not** a reconstruction of an original task execution or CI run. The attached archive has no Git worktrees/commits or historical launcher packet, so mirrored-branch isolation, claim provenance, original attempts, historical test results and actual WordPress/HTTPS/provider execution cannot be independently certified here. Original `attempt: 0` and executor-owned Completion Report are preserved without manufacturing evidence. These provenance limitations do not establish process compliance. Terminal integrated Woo provider certification remains `ARCH-026-SYSTEM-TEST-001`.

### Reviewed Files

- `moda-interact-api/src/woocommerce/rest-read/provider-connection.service.ts`
- `moda-interact-api/src/woocommerce/rest-read/product-operation.ts`
- `moda-interact-api/src/woocommerce/rest-read/credential-verifier.ts`
- `moda-interact-api/src/woocommerce/rest-read/README.md`

### Validation Reviewed

- `moda-interact-api/src/woocommerce/rest-read/provider-connection.test.ts` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-api/src/woocommerce/rest-read/provider-connection.postgres.test.ts` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-api/src/woocommerce/rest-read/provider-transport.test.ts` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-api/src/woocommerce/rest-read/product-operation.test.ts` (test present and inspected; not independently executed in this read-only archive)
- Static cross-file wiring and source inspection: completed for this task's bounded implementation.
- No new API TypeScript, PHP unit, WordPress integration, PostgreSQL or live provider tests were executed as part of this reconciliation unless explicitly listed as PASS above.

### Architecture Conformance

Accepted for bounded code-level implementation reconciliation. Live/integrated runtime acceptance is reserved for terminal system-test evidence. No source-code change is authorised by this review.

### Follow-up

`ARCH-026-SYSTEM-TEST-001` — certify the integrated HTTPS callback, real Woo consent/read and credential/tenant/billing isolation. Recover missing Git/provenance records separately if full historical workflow certification is required; do not invent them.
