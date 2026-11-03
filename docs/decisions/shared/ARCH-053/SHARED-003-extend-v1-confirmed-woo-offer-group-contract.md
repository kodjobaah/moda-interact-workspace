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
status: complete
priority: 18
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-052-SHARED-011
enables:
- ARCH-052-SHARED-012
- ARCH-053-API-003
created: 2026-10-30
updated: 2026-10-31
---

# ARCH-053-SHARED-003 — Extend Woo restore v1 with confirmed checkout offer groups

## Architecture

Architecture: `ARCH-053`. Parent: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Implementation is materialised on its dedicated task branch and submitted for Architect review.

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

- [x] Implement exact new union branch and regenerate inferred types.
- [x] Test singleton compatibility, multiple codes, mixed code/automatic sets, malformed/empty/overbound groups and v2 rejection.
- [x] Run Shared tests, typecheck and build. No package release was published.

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

- [x] The existing v1 resolver can return an ordered group (2..3) without a new route, version or recovery snapshot field.
- [x] Original customer coupons are unmodified and distinct from the recommended list.
- [x] Invalid group shapes fail validation; duplicate identity/pairing decisions remain with API/Woo.

## Validation

- [x] Woo Shared contract tests and inference/export checks passed.
- [x] Shared typecheck and build passed; `git diff --check` passed.

## Stop Condition

After the specified work, validation and acceptance criteria pass, update this task's Work Items and Completion Report, set status to `review`, hand back the implementation branch and evidence, and STOP. Do not self-accept, implement enabled tasks, modify other task/index files or push main.

## Implementation Notes

Use the launcher-resolved dedicated mirrored parent/implementation worktrees and shared structured logger. All unexpected errors must be logged with bounded identifiers and propagated to the owning failure/retry boundary. Never log coupon codes, customer information, bearer tokens or raw checkout URLs. Use relative workspace edit paths; do not touch `_index.md`.

## Completion Report

### Status

Architect accepted. Attempt 1 is complete.

### Files Changed

- `src/woocommerce/contracts.ts`
- `src/woocommerce/contracts.test.ts`
- `src/woocommerce/__fixtures__/woo-restore-v1.json`

### Work Completed

- Added the strict `CHECKOUT_OFFERS` branch to the existing `woo.restore.resolve.v1` outreach union. The ordered group contains 2–3 strict CODE or AUTOMATIC items with the exact bounded fields from the architecture contract.
- Kept singleton NONE, CHECKOUT_CODE, CHECKOUT_AUTOMATIC and ALTERNATIVE_PRODUCT branches unchanged. The existing `woocommerce` barrel already exports the schema and inferred union type; tests now import through that public entrypoint.
- Added complete v1 response golden JSON with an ordered group and the separate original `snapshot.appliedCouponCodes` list, plus a mixed CODE/AUTOMATIC example.
- Added coverage for 2- and 3-item groups, required/strict fields, empty and overbound arrays, malformed members, exact ordered round trips, inferred union typing and v2 rejection. Duplicate identity remains structural and is delegated to API/Woo as required.
- No endpoint, snapshot, route, package version or release changes were made.

### Validation Results

- `npm test`: 394 passed, 1 skipped; the Redis telemetry test requires `TEST_REDIS_URL`.
- `npm run typecheck`: passed.
- `npm run build`: passed, including `dist/woocommerce/index.d.ts`.
- Clean-process import of `dist/woocommerce/index.js`: passed; the public export parsed a mixed checkout-offer group.
- `git diff --check`: passed.

### Deviations

None.

### Assumptions

The Shared schema remains structural; offer identity uniqueness and compatibility are validated by API/Woo consumers.

### Unresolved Issues

None identified.

### Architectural Concerns

None identified during implementation.

### Synchronization and Version Control

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; shared workspace checkout unchanged.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-SHARED-003`, branch `task/ARCH-053-SHARED-003`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-SHARED-003`, branch `task/ARCH-053-SHARED-003`; shared implementation checkout unchanged.
- Another task worktree reused: no.
- Start synchronization: parent and implementation remote task branch fast-forwards were `not-needed`; `origin/main` was `already-current` in both worktrees.
- Recursive implementation submodules: sync passed; update/init passed; ready, no entries.
- Parent claim commit: `d8bf5857ce819613549aa22de528584370542571`, pushed by launcher.
- Implementation commit `fec2be64b148e48b328816632fa7b3ba3ae1565c` is present on both the local task branch and `origin/task/ARCH-053-SHARED-003`.
- Parent completion-record commit `121285c7c59e6c42986f1dca51beba30a4ee00ae` is included in the published parent task branch; current local and remote parent heads both resolve to `8ed51d5eef725f5bfc1f6ed6c9f03634e36a11d6` before this review update.
- No package release or main-branch update was made.

## Architect Review

### Review Status

Accepted — 2026-10-31. Attempt 1 complete.

### Review Notes

The implementation matches the bounded structural contract: `CHECKOUT_OFFERS` accepts 2–3 ordered strict CODE/AUTOMATIC entries in the existing `woo.restore.resolve.v1` response. Existing singleton variants, the separate original `snapshot.appliedCouponCodes`, and v2 rejection are preserved. Duplicate identity is deliberately left to API/Woo business validation as required. No out-of-scope route, snapshot, release, or consumer changes were found.

### Reviewed Files

- `src/woocommerce/contracts.ts`
- `src/woocommerce/contracts.test.ts`
- `src/woocommerce/__fixtures__/woo-restore-v1.json`

### Validation Reviewed

Reviewed the submitted evidence: 394 tests passed, 1 skipped because `TEST_REDIS_URL` was unavailable; typecheck, build, clean-process public-export import, and `git diff --check` passed. These checks were reported by the implementation agent and were not rerun during architect review. The implementation SHA `fec2be64b148e48b328816632fa7b3ba3ae1565c` matches `origin/task/ARCH-053-SHARED-003`.

### Architecture Conformance

Accepted. The v1-only wire shape and responsibility boundary conform to the task and ARCH-053/ARCH-052 architecture.

### Follow-up

ARCH-052-SHARED-012 is dependency-ready for the joint publication. No other task is promoted by this acceptance.
