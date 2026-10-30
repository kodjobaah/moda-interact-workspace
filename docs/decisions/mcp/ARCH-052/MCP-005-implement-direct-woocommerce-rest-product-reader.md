---
id: ARCH-052-MCP-005
architecture_id: ARCH-052
title: Implement secure direct WooCommerce product REST reader in MCP
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-MCP-003
created: '2026-10-30'
updated: '2026-10-30'
---

# ARCH-052-MCP-005: Implement the secure direct WooCommerce read adapter

## Architecture

ARCH-052. Parent `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Portable task definition.

## Objective

Provide MCP's existing `ApprovedWooProductReader` port with a **direct, read-only WooCommerce REST adapter** using MCP's existing installation/grant records. Do not call the hosted Moda API or implement published tool registration here.

## Context

`src/connections/woocommerce/provider.ts` already takes an `ApprovedWooProductReader`, `runtime/prisma.ts` exposes database access, and the current API repository's `src/woocommerce/rest-read/` is a **security reference**, not an internal HTTP proxy. MCP already has grant eligibility and shop-connection abstractions.

## Scope

- Implement `src/connections/woocommerce/direct-product-reader.ts` exporting `createDirectWooRestProductReader` satisfying the existing `ApprovedWooProductReader` interface; integrate it through the existing `src/runtime/ports.ts` composition without creating another port type.
- Resolve tenant-scoped active installation and read grant for each call; reuse the published Shared `@modainteract/moda-interact-shared/security/credentials/node` keyring, decrypt and AAD primitives; fail closed when keyring/grant missing or invalid.
- Implement bounded GET-only Woo REST product list/retrieve, safe canonical site origin, DNS resolution/pinning, TLS, redirect controls, timeouts, max response bytes, provider status/error mapping and after-read grant recheck. No user-supplied absolute URLs, no public inbound API route, no token/header leakage.
- Match existing `WooCommerceProductReadRequest` operations `products.list`/`products.retrieve`; do not create a product catalogue in PostgreSQL.
- Use Shared logger and existing MCP error mechanism; log bounded event codes, never plaintext credentials, product/customer data or provider response bodies.

## Out of Scope

No Shopify GraphQL changes, discount evaluation, MCP published tool mapping, Commerce Studio publication, API calls, customer cart writes, checkout URL generation, database schema changes or new generic security/crypto implementation.

## Requirements

The same underlying WooCommerce REST API must be contacted **directly by MCP**. Reuse Shared security primitives and current database grant records rather than copying another repository's secret-handling functions. Do not make a private link synonymous with granting arbitrary shop access; keep grants scoped to authenticated shops.

## Work Items

- [ ] Implement the production direct reader and wire MCP composition through existing grant/connection interfaces.
- [ ] Add fixture-based tests for active/revoked/wrong-shop grants, key rotation, wrong AAD, DNS rebinding/SSRF, redirects, GET-only constraints, timeout/large response, provider 4xx/5xx and race on credential change.
- [ ] Validate actual MCP declared scripts, build and module boundaries; return Completion Report.

## Interfaces / Contracts

Use `ApprovedWooProductReader.read({shopId,request,signal,deadlineAt}): Promise<unknown>` from existing `src/connections/woocommerce/provider.ts`. `request` remains the existing `WooCommerceProductReadRequest` union in `src/connections/ports.ts`. **No new Shared schema** is required for this internal reader. MCP-003 consumes this adapter and maps provider data into the canonical Shared product output, including nullable variant IDs and category IDs after SHARED-010 publication.

## Dependencies

None. It can be implemented using existing MCP grants and published Shared credentials without waiting for new discount schemas or Commerce publication.

## Enables

- ARCH-052-MCP-003

## Acceptance Criteria

- [ ] Direct authenticated Woo GET requests work without calls to Moda hosted API.
- [ ] Tenant/grant/rotation/security checks fail closed with bounded errors.
- [ ] Tests cover negative/adversarial origin and credential cases; no unrelated MCP tools or schema files changed.

## Validation

- [ ] MCP unit/integration tests for direct reader and selected routes; typecheck/build and `git diff --check`.

## Stop Condition

Set status `review`, return Completion Report and STOP; do not start MCP-003.

## Implementation Notes

This is a bounded provider-connection task. MCP-003 retains end-to-end generic tool execution, provider response projection and final product result validation.

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

Current encrypted credentials and grants are valid at execution time.

### Unresolved Issues

None yet.

### Architectural Concerns

Escalate gaps in published security primitives rather than implement another crypto system.

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

None.
