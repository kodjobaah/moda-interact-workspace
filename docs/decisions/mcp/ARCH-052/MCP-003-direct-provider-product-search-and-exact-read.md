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
status: in_progress
priority: 40
executor: codex
claimed_at: 2026-10-31T01:40:08Z
attempt: 1
depends_on:
- ARCH-052-SHARED-010
- ARCH-052-COMMERCE-006
- ARCH-052-MCP-005
enables:
- ARCH-052-BACKGROUND-007
- ARCH-052-COMMERCE-007
- ARCH-052-GATEWAY-001
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-10-31
---

# ARCH-052-MCP-003: Execute Shopify and WooCommerce product search directly inside MCP

## Architecture

Architecture ID: `ARCH-052`. Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised**; no Git branch or worktree created.

## Objective

Integrate **generic published** `commerce_search_products` and `commerce_get_product` execution into MCP across Shopify and WooCommerce, consuming the accepted direct Woo reader from **MCP-005** instead of implementing a duplicate transport or calling the hosted API.

## Context

`src/connections/ports.ts` already declares `products.list`/`products.retrieve`; `runtime/ports.ts` only registers Woo when an injected `ApprovedWooProductReader` exists. `WooProductReadService` in the hosted API is the security/behaviour reference, NOT a service proxy. Shopify MCP already executes bounded GraphQL product search and has an offline session reader.

## Scope

- Implement the published policy-operation dispatcher for `products.search` and `products.get` as defined by COMMERCE-006; use the published SHARED-010 product input/output schemas and the existing generic MCP response wrapper.
- Shopify: reuse existing `src/execution/policy/shopify-core.ts` GraphQL product search and exact product lookup, extending projection to include genuine `categoryIds`/`collectionIds` if provider-returned and `variantId` from the actual variant; do not substitute product type/name for an ID.
- WooCommerce: use **only the already accepted MCP-005** `ApprovedWooProductReader` and the existing `products.list`/`products.retrieve` connection ports. Map provider IDs to strings, simple products to `variantId:null`, variations to their real IDs, product/category IDs and storefront/image/price fields. No API proxy or new credential/keyring code in this task.
- Preserve existing page cursors, request budgets, shop/feature permissions, actual provider product URLs, bounded results, and shared logger. A missing provider category/collection ID remains absent; a non-variant Woo product is not an error.
- Keep result metadata compatible with product-search drafts published by COMMERCE-007; tool registration and publication are distinct tasks.
- For the returned `CommerceProduct.url`, use only the direct authenticated provider response for the **same current shop**. Validate canonical storefront-host ownership at the provider adapter/projection boundary against an independently authenticated shop origin: WooCommerce's verified installation site origin or Shopify's authenticated storefront/primary-domain metadata (including legitimate custom storefront domains). Do **not** derive an allowed-host list from the candidate URL, discount description, AI output or untrusted query. If host ownership cannot be established, return `url:null` as permitted by the existing product schema; do not provide a customer-facing URL to BACKGROUND-010. No new Shared schema or hosted API route is required for this internal validation.

## Out of Scope

No additional database table/column/migration, migration backfill, alternate provider proxy, customer-facing product database/cache, secret-bearing logs, unrelated architecture or other repository implementation.

## Requirements

- The MCP host uses published Shared-010 package schemas; `CommerceProductSchema.variantId` is nullable and `categoryIds`/`collectionIds` contain only provider IDs, not inferred labels.
- Shop identity, connection grant and `product_search` feature permission are mandatory. No MCP-to-API product requests or new product database.
- Secure direct Woo credential/transport belongs solely to MCP-005. MCP-003 consumes the port and tests projection/execution rather than reproducing encryption or SSRF logic.
- Preserve source product identity and missing fields; no fabricated prices, sale evidence, variant IDs, categories, or links.

## Work Items

- [ ] Wire published `commerce_search_products` and `commerce_get_product` handlers to existing shop connections and accepted MCP-005 Woo reader.
- [ ] Extend Shopify and Woo product output mapping for `variantId:null`, provider category/collection IDs, optional image and sale evidence using the exact Shared contract.
- [ ] Test entitlement, shop scope, partial/missing product fields, Woo simple/variation products, Shopify variant collections and direct provider access.
- [ ] Test that product URLs are direct current-shop provider results with independently authenticated storefront-host ownership; valid Shopify custom domains and verified Woo origins remain usable, while spoofed/external hosts, cross-shop records and unknown-origin URLs return `url:null` without granting an arbitrary host.
- [ ] Validate generic result schema, tool descriptor names, cancellation, structured errors and declared MCP scripts.

## Interfaces / Contracts

Consumer of `@modainteract/moda-interact-shared/commerce` published by SHARED-010: `CommerceToolInputs.commerce_search_products`, `.commerce_get_product`, their `CommerceToolOutputs` and `CommerceProductSchema` with nullable `variantId`, optional `categoryIds`/`collectionIds`. Internal Woo port: `ApprovedWooProductReader.read` and `WooCommerceProductReadRequest` already defined in MCP; MCP-005 owns its direct adapter. COMMERCE-006 owns code-defined `products.search`/`products.get` draft registrations; COMMERCE-007 publishes after MCP-003 is accepted.

## Dependencies

- `ARCH-052-SHARED-010` — published full product identity contract.
- `ARCH-052-COMMERCE-006` — canonical product-tool descriptors/operation registry.
- `ARCH-052-MCP-005` — secure direct Woo read adapter accepted in MCP.

## Enables

- ARCH-052-BACKGROUND-007
- ARCH-052-COMMERCE-007
- ARCH-052-GATEWAY-001
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Search and exact-product tools work for both store types with published result schemas and no internal API proxy.
- [ ] Woo simple products return `variantId:null`; genuine variants retain their source ID.
- [ ] Provider categories/collections are source IDs, not inferred category-label aliases; missing fields remain unknown/absent.
- [ ] Shop/entitlement/credential access remains enforced and errors logged safely.
- [ ] The tool never yields a customer-facing product URL whose storefront-host ownership cannot be established for its authenticated shop; absence is represented as `url:null` under the existing contract, not a fabricated product or a permissive new host allowlist.

## Validation

- [ ] MCP published-tool invocation tests, direct Shopify GraphQL and mocked Woo reader integration; tenant isolation, revoked tool/grant, schema validation and cursor behaviour.
- [ ] Declared MCP typecheck/build and `git diff --check`.

## Stop Condition

Once Work Items, acceptance criteria and validation are met, set task status to `review`, complete its report, return to `moda_architect` and **STOP**. Do not mark it Complete, publish another task, merge branches or push `main`.

## Implementation Notes

Expected MCP owning code: `src/execution/policy/`, `src/connections/resolver.ts`, `src/runtime/ports.ts` composition, and tests. **Do not implement** `src/connections/woocommerce/direct-product-reader.ts` here: MCP-005 owns it. No hosted API product route, no extra Prisma tables, no Shared edits. Publisher runs only in COMMERCE-007.

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
