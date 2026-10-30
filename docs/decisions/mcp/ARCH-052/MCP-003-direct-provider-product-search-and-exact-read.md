---
id: ARCH-052-MCP-003
architecture_id: ARCH-052
title: Execute Shopify and WooCommerce product search directly inside MCP
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-003
- ARCH-052-COMMERCE-006
enables:
- ARCH-052-BACKGROUND-007
- ARCH-052-COMMERCE-007
- ARCH-052-GATEWAY-001
- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-30'
---

# ARCH-052-MCP-003: Execute Shopify and WooCommerce product search directly inside MCP

## Architecture

Architecture ID: `ARCH-052`. Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised**; no Git branch or worktree created.

## Objective

Implement platform-neutral product search and exact product/variant reads in MCP, making provider calls directly rather than calling the hosted Moda API.

## Context

`src/connections/ports.ts` already declares `products.list`/`products.retrieve`; `runtime/ports.ts` only registers Woo when an injected `ApprovedWooProductReader` exists. `WooProductReadService` in the hosted API is the security/behaviour reference, NOT a service proxy. Shopify MCP already executes bounded GraphQL product search and has an offline session reader.

## Scope

- Replace the unbound API-broker-only reader in `src/connections/woocommerce/provider.ts` and `src/runtime/ports.ts` with a production-owned `createDirectWooRestProductReader` in `src/connections/woocommerce/direct-product-reader.ts`. Use `src/runtime/prisma.ts` and existing `WooCommerceInstallation`/`WooCommerceRestReadGrant` Prisma delegates. On each invocation load exact authenticated shop installation/grant, status ACTIVE/read scope, credentialVersion, rotation/authorizationAttempt IDs and canonical site origin; use `@modainteract/moda-interact-shared/security/credentials/node` `parseCredentialKeyring`, `decryptCredential`, `createWooRestReadGrantAad`. Read `COMMERCE_CONNECTION_KEYS_JSON` plus approved active-key config at startup; fail closed if unset/malformed. Do not expose or cache plaintext credentials across requests. Recheck grant and installation *after* provider response before returning data. No API calls.
- Implement MCP-owned Woo **GET-only** hardened REST transport in `src/connections/woocommerce/secure-read-transport.ts`, using the existing API Woo verifier as *behavioural reference* only (no API import): canonical site validation, HTTPS except explicit local-test mode, no redirect, DNS resolution and pinned public routable IP, peer-address check, TLS hostname verification, bounded timeouts, header/body size, content type and pagination. Reject private/loopback/metadata/IPv6 unsafe origins in production, DNS rebinding and credentials in URL; support local OAuth only with explicit local test policy. Reuse Shared security primitives, not duplicated generic cryptography.
- Implement exact Woo REST `products.list` and `products.retrieve` projection in `src/connections/woocommerce/product-read-operation.ts` using `/wp-json/wc/v3/products` and product variations when `variantId` is supplied. Request `_fields` for ids/name/prices/regular_price/sale_price/stock_status/permalink/images/categories/variations; resolve variation image before product image; return only Shared-008 allowed fields. Never return raw HTML/secret meta. Bound result size (max 20), page/search/keyword and verify permalink/image HTTPS storefront host and product ownership; missing => nullable result, never synthetic fallback. Search may find related products by query/taxonomy with bounded pages; no persistent product cache.
- Add `src/execution/policy/product-search-executor.ts` implementing **published** `products.search@1.0.0` and `products.get@1.0.0` definitions from COMMERCE-006 through `createPublishedExecutionRegistry` in `src/runtime/service-ports.ts`; dispatch by trusted `StoreConnection.platform`. For Shopify reuse existing `createShopifyCoreAdapters.searchProducts` and implement exact ID/variant GraphQL read; for Woo use new direct reader. Map to the identical Shared-008 product schemas. Do not make an API-process HTTP call, duplicate SDK publisher, or turn this into a product database.
- Implement direct WooCommerce REST product list/retrieve through the approved MCP connection, with no coupon-proof endpoint, generic HTTP proxy or hosted Moda API hop.
- Tests: encrypted grant/key rotation/tampered AAD, revoked/wrong-shop grant before and during I/O, DNS rebinding, redirect/loopback/TLS mismatch, HTTP 401/429/404, oversized body, variant fallback, deleted product, taxonomies, sale-price evidence, Shopify/Woo result parity, no MCP-to-API traffic, `tools/list` published descriptor gating and no credential leaks.

## Out of Scope

No additional database table/column/migration, migration backfill, alternate provider proxy, customer-facing product database/cache, secret-bearing logs, unrelated architecture or other repository implementation.

## Requirements

- Only assigned repository code and this task report may be changed. Do not implement Enabled tasks.
- Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the exact launcher packet and dedicated mirrored parent/implementation worktrees. Re-read the authoritative task before claiming.
- Use `@modainteract/moda-interact-shared/logging` for new Node structured logs; record unexpected exceptions with bounded reason codes and propagate to the owning error/retry boundary. Never log credentials, complete URLs, coupon codes, raw provider payloads or customer personal data.
- Authenticate every shop/grant/call with its trusted identity, enforce provider deadlines, bounded pagination, strict response projection, customer/tenant separation and read-only provider behavior.
- This is a **pre-production breaking design**. Do not add legacy adapters/backfills or change conversation CommerceAgent lifecycle.

## Work Items

- [ ] Implement exactly the scoped files and runtime behavior.
- [ ] Add deterministic unit and negative/security tests.
- [ ] Run the required validation; record all commands and evidence in Completion Report.

## Interfaces / Contracts

MCP published product tools `commerce_search_products` and `commerce_get_product`, operations `products.search` and `products.get` `1.0.0`; Shared-008 result contracts. Built-in discount handlers are separate MCP-002. Direct Woo connection reads only existing Postgres encrypted connection records and live Woo REST; no stored product rows.

## Dependencies

- ARCH-052-SHARED-003
- ARCH-052-COMMERCE-006

## Enables

- ARCH-052-BACKGROUND-007
- ARCH-052-COMMERCE-007
- ARCH-052-GATEWAY-001
- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Product search for both platforms works entirely within MCP; **zero calls to Moda API** on this path.
- [ ] Direct Woo provider preserves credential encryption, grant recheck, anti-SSRF/TLS and read-only semantics.
- [ ] `commerce_get_product` returns exact variant image and shop-safe permalink or explicit not-found; missing data never fabricated.
- [ ] Published product tools use one canonical Shared contract and fail closed when unavailable.

## Validation

- [ ] MCP unit/security tests for Woo direct provider + Shopify dispatcher.
- [ ] MCP integration harness with two Woo installations, fake DNS/HTTPS and Shopify GraphQL.
- [ ] MCP declared typecheck, lint, build and `git diff --check`.

Use the scripts actually declared by the repository's package/tooling. Record unrun checks as unverified; include `git diff --check`.

## Stop Condition

Once Work Items, acceptance criteria and validation are met, set task status to `review`, complete its report, return to `moda_architect` and **STOP**. Do not mark it Complete, publish another task, merge branches or push `main`.

## Implementation Notes

Expected workspace-relative owned source paths (confirm paths exist in checked-out worktree before editing):

- `moda-interact-mcp/src/connections/woocommerce/direct-product-reader.ts` (new)
- `moda-interact-mcp/src/connections/woocommerce/secure-read-transport.ts` (new)
- `moda-interact-mcp/src/connections/woocommerce/product-read-operation.ts` (new)
- `moda-interact-mcp/src/connections/woocommerce/provider.ts`
- `moda-interact-mcp/src/connections/ports.ts`
- `moda-interact-mcp/src/runtime/ports.ts`
- `moda-interact-mcp/src/runtime/prisma.ts`
- `moda-interact-mcp/src/runtime/service-ports.ts`
- `moda-interact-mcp/src/execution/policy/product-search-executor.ts` (new)
- `moda-interact-mcp/tests/unit/connections/woocommerce/` and `tests/integration/`

## Completion Report

### Status

Not Started — portable definition; no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Confirm execution baseline in dedicated task worktree.

### Unresolved Issues

None established.

### Architectural Concerns

Return material contract/security/proof gaps to `moda_architect` without inventing a workaround.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation accepted.

### Reviewed Files

Task definition and uploaded 29 October 2026 snapshot only.

### Validation Reviewed

No implementation tests yet.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through canonical task launcher only after dependencies are Complete.
