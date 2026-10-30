---
id: ARCH-052-BACKGROUND-011
architecture_id: ARCH-052
title: Enrich Shopify discount catalogue with source-backed targeting facts
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-BACKGROUND-009
- ARCH-052-SHARED-010
enables:
- ARCH-052-MCP-002
created: '2026-10-30'
updated: '2026-10-30'
---

# ARCH-052-BACKGROUND-011: Enrich existing Shopify discount catalogue with targeting facts

## Architecture

ARCH-052. Parent `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. New repository-owned implementation task, not materialised.

## Objective

Extend the **existing** Shopify discount sync projection so `ShopifyDiscount.providerSnapshot` contains genuine discount kind/value, product/variant/collection targets, purchase thresholds and known restrictions needed by MCP-002. Do not create a separate provider-proof API or business eligibility engine.

## Context

`src/providers/shopify-discount.provider.ts` currently queries only discount title, summary, status, dates and codes. `ShopifyDiscountCatalogueService.reconcile()` already upserts `providerSnapshot`; BACKGROUND-009 separates provider status from merchant selection and must be accepted before this task changes the same path. WooCommerce's `woo-coupon-normalization.ts` already captures coupon restriction fields and does not require a new sync implementation in this task.

## Scope

- Extend `src/providers/shopify-discount.provider.ts` GraphQL selection and `normalizeDiscount()` to retain **bounded, typed, safe** provider discount facts for supported Shopify Basic code/automatic discounts, including discount percentage/amount and currency, customerGets product/variant/collection selections, exclusions when available, minimum subtotal/quantity and customer scope when available. Use Shopify's actual typed GraphQL fragments; do not invent unsupported fields or call the checkout provider.
- Store the fetched facts inside the **existing** `ShopifyDiscount.providerSnapshot` in the existing catalogue upsert. Keep `providerStatus`, `startsAt`, `endsAt`, `lastSyncedAt`, `unavailableAt` and merchant-owned `isAvailable` behaviour unchanged. No Prisma migrations.
- Project **completeness** and `unrepresentedConditions` evidence: app discounts, BxGy, unsupported targeting, incomplete nested pagination and unknown values remain `PARTIAL` or `UNKNOWN`, never falsely `COMPLETE`. Deep provider target enumeration must have bounded pagination/request size; incomplete target enumeration is not represented as an empty unrestricted set.
- Preserve the existing Shopify discount GraphQL page iteration, sync generation transaction and failure handling. Reuse Shared structured logging; no secrets, full raw payloads or customer data in diagnostics.

## Out of Scope

Woo coupon sync, MCP tool implementation, product API search, Commerce private proof routes, AI/LLM ranking, merchant selection UI, schema/migrations, provider cart mutation, ARCH-053 checkout URLs.

## Requirements

- Provider native targets are captured in raw Shopify IDs; `productType` labels are not equivalent to collection IDs. Do not infer conditions from discount title or `summary` text.
- A response whose provider targeting has more nodes than the bounded fetch is marked incomplete. Never mark unsupported/custom provider apps as fully representable.
- Do not make `isAvailable` track Shopify status; BACKGROUND-009 owns that separation.

## Work Items

- [ ] Extend the Shopify discount GraphQL fragments and provider normalisation for observed conditions, with explicit supported/partial/unknown outcomes.
- [ ] Persist condition facts in the existing `providerSnapshot`, not another table or service.
- [ ] Test Basic automatic/code product targets, collection targets, percentage/fixed amounts, purchase minimum, BxGy/app incomplete, nested target truncation, sync retries and preserved merchant selection.
- [ ] Run targeted Background test/typecheck/build scripts, record worktree and validation evidence.

## Interfaces / Contracts

Producer: `ShopifyDiscountProvider.listDiscounts` -> `ShopifyDiscountRecord.providerSnapshot` -> existing catalogue upsert. Consumer: MCP-002 reads `providerSnapshot` and maps to `CommerceDiscountConditionFactsSchema` from published SHARED-010. **No new external wire contract**: the snapshot remains database-internal JSON; its provider-observed values map to the exact Shared-009 fields. Missing or incomplete provider targeting must be represented through `completeness`/`unrepresentedConditions` in MCP output.

## Dependencies

- ARCH-052-BACKGROUND-009
- ARCH-052-SHARED-010

## Enables

- ARCH-052-MCP-002

## Acceptance Criteria

- [ ] Targeting/value facts are truly source-backed for supported Shopify types and remain bounded.
- [ ] Provider pagination/truncation cannot be confused with unrestricted discounts.
- [ ] Original catalogue sync and merchant `isAvailable` invariants pass regression tests.

## Validation

- [ ] Background Shopify provider and catalogue sync tests with real-world shaped GraphQL fixtures.
- [ ] Declared Background typecheck/build and `git diff --check`; record command outcomes.

## Stop Condition

Set `status:review`, return Completion Report to architect and STOP. Do not start MCP-002.

## Implementation Notes

Source files: `moda-interact-background/src/providers/shopify-discount.provider.ts`, `src/services/shopify-discount-catalogue.service.ts` (only if necessary to retain provider facts), corresponding tests. Existing Woo source unchanged. This task deliberately does not make live provider reads during outreach; only the pre-existing catalogue synchroniser reads Shopify.

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

Uses accepted BACKGROUND-009.

### Unresolved Issues

None yet.

### Architectural Concerns

Escalate provider fields that cannot be retrieved or bounded; do not silently infer conditions.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
