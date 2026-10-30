---
id: ARCH-052-BACKGROUND-013
architecture_id: ARCH-052
title: Capture Shopify discount classes and own combination tags
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-BACKGROUND-011
enables:
- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001
created: 2026-10-30
updated: 2026-10-30
---

# ARCH-052-BACKGROUND-013 — Capture Shopify discount classes and own combination tags

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Architect coordination task; **portable definition, not materialised**. No branch or runtime implementation has been created by this artifact.

## Objective

Complete Shopify Basic discount combination snapshots by persisting each discount's own tags and provider discount classes, separately from already-captured `combinesWith` allowances.

## Context

BACKGROUND-011 Attempt 2 is awaiting architect review. It persists Basic `combinesWith` booleans and **allowed** same-line tags, but does not query the discount's own `tags` or `discountClasses`. Shopify Plus same-line stacking requires two-way tag matches and a trusted Plus entitlement; unobserved tags cannot be interpreted as a valid pair. Do not reopen or edit BACKGROUND-011 during review.

## Scope

- In `moda-interact-background/src/providers/shopify-discount.provider.ts`, extend BOTH existing `DiscountAutomaticBasic` and `DiscountCodeBasic` GraphQL selections with `tags` and `discountClasses`; obtain authenticated `shop.plan.shopifyPlus` once per provider sync (not once per coupon or send) and preserve the existing bounded snapshot format and operation/error handling.
- Normalize own `tags`, provider `discountClasses` and an observed shop-level `shopifyPlus` in the snapshot without overwriting `combinesWith.productDiscountsWithTagsOnSameCartLine` (allowed tags). Preserve strict boundedness, source provenance and truncation status.
- Add focused GraphQL fixture tests for mutual/nonmutual tags, empty vs unknown, truncation, mixed discount classes, unsupported discount types and provider failures.

## Out of Scope

- No changes to currently claimed `ARCH-052-SHOPIFY-001` merchant UI, `ARCH-052-MCP-005` Woo reader, `ARCH-049-BACKGROUND-003` brand sync, accepted SHARED-009/010, Woo coupon plugin or new database schema.

## Requirements

- Treat absent/malformed/overflow provider tags/classes as unknown/incomplete. Do not truncate then label `COMPLETE`.
- Source `tags` are the discount's own tags; allowed same-line tags remain inside `combinesWith`. Shopify Plus plan entitlement is obtained from the separately authenticated shop plan source; if unavailable it must be `null`, never inferred from title or tags.
- Keep the existing providerSnapshot same-table strategy. No external network operations in a DB transaction or extra provider calls per checkout.

## Work Items

- [ ] Add fields to both bounded Basic GraphQL selections and normalize independently.
- [ ] Ensure no regression to previously persisted `combinesWith` policy.
- [ ] Test valid, malformed and ambiguous provider facts; record validation evidence.

## Interfaces / Contracts

Shopify Admin GraphQL 2026-07: `shop { plan { shopifyPlus } }` (one bounded shop-level observation per sync), `DiscountAutomaticBasic.tags`, `DiscountAutomaticBasic.discountClasses`, `DiscountCodeBasic.tags`, `DiscountCodeBasic.discountClasses` and `DiscountCombinesWith.productDiscountsWithTagsOnSameCartLine`. The resulting snapshot stores `tags: string[]|null`, `discountClasses: Array<"ORDER"|"PRODUCT"|"SHIPPING">|null`, `shopifyPlus: boolean|null`, and the existing typed `combinesWith` object. MCP-002 subsequently projects these into Shared facts. It is not an eligibility verdict.

## Dependencies

- ARCH-052-BACKGROUND-011

## Enables

- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Own vs allowed tags are not confused, and an unknown or oversized array remains non-authoritative.
- [ ] Both Basic selectors preserve existing discount data, seller selections and source-backed conditions without modifying provider availability/merchant flags.
- [ ] No checkout mutation or additional provider lookup on the hot path.

## Validation

- [ ] Focused Shopify provider query/normalization tests.
- [ ] Background declared lint/build and `git diff --check`.

## Stop Condition

After the specified work, validation and acceptance criteria pass, update this task's Work Items and Completion Report, set status to `review`, hand back the implementation branch and evidence, and STOP. Do not self-accept, implement enabled tasks, modify other task/index files or push main.

## Implementation Notes

Use the launcher-resolved dedicated mirrored parent/implementation worktrees and shared structured logger. All unexpected errors must be logged with bounded identifiers and propagated to the owning failure/retry boundary. Never log coupon codes, customer information, bearer tokens or raw checkout URLs. Use relative workspace edit paths; do not touch `_index.md`.

## Completion Report

### Status

Not started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

No production compatibility is required; all required source provenance remains available for implementing agents to verify.

### Unresolved Issues

None at definition time.

### Architectural Concerns

Any source contract/deployment gap must be escalated rather than patched locally.

## Architect Review

### Review Status

Pending.

### Review Notes

New multi-discount feature task; no implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

No implementation validation yet.

### Architecture Conformance

Pending implementation and review.

### Follow-up

None.
