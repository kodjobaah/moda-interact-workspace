---
id: ARCH-053-SHARED-003
architecture_id: ARCH-053
title: Extend Woo restore v1 with confirmed checkout offer groups
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 18
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-011
enables:
- ARCH-052-SHARED-012
- ARCH-053-API-003
created: 2026-10-30
updated: 2026-10-30
---

# ARCH-053-SHARED-003 — Extend Woo restore v1 with confirmed checkout offer groups

## Architecture

Architecture: `ARCH-053`. Parent: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Architect coordination task; **portable definition, not materialised**. No branch or runtime implementation has been created by this artifact.

## Objective

Extend the **existing** `woo.restore.resolve.v1` successful response with one additional bounded `CHECKOUT_OFFERS` variant for the confirmed initial message, keeping original shopper coupons separate.

## Context

ARCH-053-SHARED-001 and its publication are already Complete. The first real group-aware API-003 and Woo-007 implementations are still Pending; pre-production architecture explicitly allows extending the existing v1 before release without a v2 resolver or legacy adapter. ARCH-052 owns selecting/sending offers, ARCH-053 owns customer-initiated Woo native application.

## Scope

- Modify `moda-interact-shared/src/woocommerce/contracts.ts`, existing Woo schema tests and exports only as necessary; preserve `WooCartRestoreSupportedSnapshotV1Schema` and `snapshot.appliedCouponCodes` unchanged.
- Add `CHECKOUT_OFFERS` to `WooRestoreOutreachOfferV1Schema` discriminated union while retaining existing NONE/CHECKOUT_CODE/CHECKOUT_AUTOMATIC/ALTERNATIVE_PRODUCT variants for actual single-offer flows.
- Test exact v1 JSON, strict rejection of malformed/empty/duplicate-array/overbound group shape (business duplicate detection belongs to API/Woo), and `woo.restore.resolve.v2` rejection.

## Out of Scope

- No new endpoint, query parameter, cart URL issuance, WordPress mutation, snapshot backfill, v2 wire, duplicate outgoing offer table, or re-implementation of Shared coupon/ID validators.

## Requirements

- This implementation must follow SHARED-011 so the two Shared worktrees do not independently modify the same package baseline. One publication task SHARED-012 later publishes BOTH accepted implementations; no second npm release solely for ARCH-053.
- The resolver response describes what was confirmed sent; it is not an instruction to bypass WooCommerce native coupon validation.
- Preserve the exact order of offered codes and the original `snapshot.appliedCouponCodes` separately; non-checkout alternative offers never convey coupon codes to restore.

## Work Items

- [ ] Implement exact new union branch and regenerate inferred types.
- [ ] Test single offer, multiple codes, mixed code/automatic set, rejection of overbound/malformed v1 and no v2.
- [ ] Run Shared implementation tests/typecheck/build; do not publish.

## Interfaces / Contracts

Append this branch to `WooRestoreOutreachOfferV1Schema` using the existing `WooNoControlTextSchema` helper:

```typescript
z.strictObject({
  kind: z.literal("CHECKOUT_OFFERS"),
  offers: z.array(z.discriminatedUnion("method", [
    z.strictObject({
      method: z.literal("CODE"),
      code: WooNoControlTextSchema(128),
      providerDiscountId: WooNoControlTextSchema(191),
    }),
    z.strictObject({
      method: z.literal("AUTOMATIC"),
      providerDiscountId: WooNoControlTextSchema(191),
    }),
  ])).min(2).max(3),
}),
```

Example eligible v1 response addition: `"outreachOffer":{"kind":"CHECKOUT_OFFERS","offers":[{"method":"CODE","code":"SAVE10","providerDiscountId":"woo:coupon:10"},{"method":"CODE","code":"SHIPFREE","providerDiscountId":"woo:coupon:20"}]}`. The full response retains `schemaVersion:"woo.restore.resolve.v1"`, `snapshot` and current shop authorization, with **no change to checkout links**. Structural schema parsing does not prove coupon uniqueness or validity: API and Woo enforce that.

## Dependencies

- ARCH-052-SHARED-011

## Enables

- ARCH-052-SHARED-012
- ARCH-053-API-003

## Acceptance Criteria

- [ ] The existing v1 resolver can return an ordered group (2..3) without a new route, version or recovery snapshot field.
- [ ] Original customer coupons are unmodified and distinct from the recommended list.
- [ ] Invalid group shape fails validation; no partial group is silently represented as a valid group.

## Validation

- [ ] Woo Shared contract tests and inference/export checks.
- [ ] Shared typecheck/build, `git diff --check`.

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
