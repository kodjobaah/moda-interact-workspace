---
id: ARCH-036-API-002
architecture_id: ARCH-036
title: Read and persist Woo merchant coupon selections
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-DATABASE-002", "ARCH-036-SHARED-003", "ARCH-036-API-001"]
enables: ["ARCH-036-WOOCOMMERCE-003", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-API-002 — Read and persist Woo merchant coupon selections

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Expose a tenant-authorised paginated shared-catalogue read and revision-guarded multi-coupon offer-selection write without changing delay/follow-up policy semantics.

## Context

The existing ARCH-035 API-002 only saves recovery delay/follow-up and explicitly forbids Woo coupon selection. This separate endpoint owns provider-specific selected IDs and modes.

## Scope

Expose versioned read of shop-scoped current catalogue and persisted selection, plus PUT to save offer mode and bounded selected discount IDs on existing policy row with the same CAS mechanism as ARCH-035 API-002. Return merchant configuration separately from effective override.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

No user-supplied shopId accepted. NONE => empty selection; Woo FIXED => 1..50 unique selected current Woo coupon IDs; AI => empty merchant-curated list, considers entire supported current catalogue. Selected discounts are one-per-recovery allowed set, not multiple stacked codes. Reject foreign/malformed/deleted/expired/zero-value/unsupported IDs with explicit 400/409; stale catalog returns retryable unavailable. Mutations preserve recoveryDelay/followUp fields and admin overrides, reject outdated revision; list pagination must not download entire catalogue into React.

## Work Items

- [ ] Build strict shop-authorised catalogue and selection reads with bounded pagination.
- [ ] Implement CAS mode/selected IDs update under shop row lock.
- [ ] Validate same-shop selectable coupons, override and stale generation.
- [ ] Add policy conflict/negative/feature-gating tests.

## Interfaces / Contracts

GET `/v1/merchant/discount-offers` and paginated GET `/v1/merchant/discount-catalogue`; PUT `/v1/merchant/discount-offers` (proposed fixed versioned paths), Shared offer v1 and existing `ShopSettings`/override.

## Dependencies

- `ARCH-036-DATABASE-002`
- `ARCH-036-SHARED-003`
- `ARCH-036-API-001`

## Enables

- `ARCH-036-WOOCOMMERCE-003`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] No Woo selector can update Shopify rows or foreign-Shop coupon IDs.
- [ ] Repeated identical PUT is idempotent, conflicting update is explicit 409 with unchanged stored state.
- [ ] Selected IDs persist across reload, filtering and refresh; revocations surface as unavailable.
- [ ] Existing recovery delay/follow-up GET/PUT behaviour unaffected.

## Validation

- [ ] API unit/integration auth/pagination/conflict/tenant tests
- [ ] Disposable PostgreSQL CAS, overridden policy and foreign-ID cases
- [ ] API typecheck/lint/test/build and `git diff --check`

## Implementation Notes

Provider discount eligibility at message-send time is a separate capability; saving an ID does not assert it is redeemable.

For developer execution, use the canonical `/moda_developer_create ARCH-036-API-002` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-API-002`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

The implementation executor will verify local checkout, dependencies and available toolchain at claim time.

### Unresolved Issues

None recorded by an implementation executor.

### Architectural Concerns

Report schema, cross-service or provider-proof deviations to `moda_architect` instead of silently expanding scope.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only, not implementation acceptance.

### Reviewed Files

Current 12 October 2026 source snapshot used to define ownership; implementation not yet reviewed.

### Validation Reviewed

None from this task.

### Architecture Conformance

To be determined after implementation inspection.

### Follow-up

Await canonical materialisation, execution and review.
