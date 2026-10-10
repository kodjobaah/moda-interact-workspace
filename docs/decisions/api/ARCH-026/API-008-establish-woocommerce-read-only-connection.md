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
status: pending
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-API-007
enables:
  - ARCH-026-SYSTEM-TEST-001
created: 2026-10-10
updated: 2026-10-10
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

- [ ] Implement explicit Shop/installation/grant resolution, AEAD decrypt and fail-closed state mapping.
- [ ] Implement bounded, pinned `GET` transport for product list/detail read operations and safe response handling.
- [ ] Add typed in-process provider-read interface and focused API unit/integration tests using test keys and stubbed Woo endpoints.
- [ ] Verify real read-only Woo API access with an approved grant and absence of credentials in outputs/logs.

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

- [ ] Two Woo shops with different credentials cannot read one another's data; missing/revoked/stale credentials fail closed.
- [ ] Only provider-derived canonical origins and the initial two product GET operations are accepted. Arbitrary paths/headers, write verbs, redirects and unsafe DNS are rejected.
- [ ] Provider credentials never enter WordPress, browser/React, MCP payloads, response metadata or logs.
- [ ] Verified `read` credentials successfully fetch bounded product data from an approved Woo fixture; `401`, `403`, timeout and invalid JSON produce bounded failures.
- [ ] Free subscription, entitlements, installation credential and onboarding status are unchanged by successful or failed provider reads.

## Validation

- [ ] `npm run typecheck`.
- [ ] `npm run lint`.
- [ ] `npm test` with targeted GET allowlist, cryptography, SSRF, response and tenant-isolation cases.
- [ ] `npm run test:integration` with disposable PostgreSQL grant fixtures, plus test Woo HTTP server / real provider proof where reachable.
- [ ] `git diff --check` and task-isolation/synchronization evidence.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set task to `review`, return its Completion Report to `moda_architect` and STOP. Do not implement Commerce/ARCH-030 read tools or expand to order/customer reads as opportunistic work.

## Implementation Notes

Do not make secrets available merely to avoid a later internal API decision. A read-only Woo key is not an authorization grant for arbitrary data exfiltration, and the provider's GET capability still requires Moda operation- and tenant-level enforcement. A future private broker, if needed by an extracted MCP server, must be separately designed with service-authenticated, shop-bound request attestation and approved network routing.

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

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

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

Await repository implementation and Completion Report.
