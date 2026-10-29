---
id: ARCH-052-SHARED-008
architecture_id: ARCH-052
title: Define platform-neutral product search and exact-product MCP contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-008: Define platform-neutral product search and exact-product MCP contracts

## Architecture

Architecture ID: `ARCH-052`. Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised**; no Git branch or worktree created.

## Objective

Define the shared, platform-neutral product search and exact-product data contract used by the published MCP product tools, reusing `CommerceProductSchema`. Do not publish the InitialOutreachOfferAgent choice/result type.

## Context

`CommerceToolInputs.commerce_search_products` and `CommerceProductSchema` already exist. Shopify MCP supports bounded search via `shopify.searchProducts`; Woo MCP has only `products.list`/`products.retrieve` ports and no production reader. Product facts are NOT replicated to PostgreSQL.

## Scope

- Reuse and extend the existing `CommerceProductSchema`/`CommerceToolInputs.commerce_search_products` and corresponding outputs rather than creating a second commerce-product model. Require bounded same-shop ID, title, verified storefront URL, price, currency, availability, product type/vendor, timestamp; add bounded `categories:string[]` (up to 12), optional HTTPS `imageUrl` and nullable verified `saleEvidence` only when the platform supplies them.
- Add exact `commerce_get_product` input `{productId,variantId:null|string}` and result `{product:CommerceProductSchema|null}`. An exact lookup must not silently fall back to fuzzy search. Keep tool definitions browser-safe and publish via the ordinary accepted Commerce tool release (COMMERCE-006/007).
- Provider-specific readers, credentials, shop auth and tool registrations belong to MCP-003, not Shared; product rows are not copied into PostgreSQL.
- **Do not** define `OutreachPromotionChoiceSchema`, `VerifiedAlternativeProductPromotionSchema`, AI ranking rules, or template promotion targets here. BACKGROUND-010 owns the private agent decision and its evidence map. SHARED-005 owns shared provider discount evidence; SHARED-002 owns message binding/CTA semantics.
- Test Shopify/Woo normalized results, missing image/category, bad storefront host/URL, provider unavailable, overflow, exact variant mismatch and a product belonging to another shop.

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

`@modainteract/moda-interact-shared/commerce`: existing `CommerceProductSchema`, search input/output, and new `commerce_get_product` input/output. All MCP tools return the **existing** `CommerceToolResultSchema` envelope with feature data inside it.

## Dependencies

None.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] One shared product contract supports both commerce providers through generic MCP results.
- [ ] Exact lookup uses exact IDs and no new product storage.
- [ ] No AI-only or Background-only result schemas are published.

## Validation

- [ ] Shared commerce schema unit/negative tests including `src/commerce/contracts.test.ts`.
- [ ] Repository typecheck, lint/build as declared.

Use the scripts actually declared by the repository's package/tooling. Record unrun checks as unverified; include `git diff --check`.

## Stop Condition

Once Work Items, acceptance criteria and validation are met, set task status to `review`, complete its report, return to `moda_architect` and **STOP**. Do not mark it Complete, publish another task, merge branches or push `main`.

## Implementation Notes

Expected workspace-relative owned source paths (confirm paths exist in checked-out worktree before editing):

- `moda-interact-shared/src/commerce/schemas.ts`
- `moda-interact-shared/src/commerce/definitions.ts`
- `moda-interact-shared/src/commerce/contracts.test.ts`
- `moda-interact-shared/src/commerce/index.ts`

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
