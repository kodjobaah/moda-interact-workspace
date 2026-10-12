---
id: ARCH-036-DATABASE-002
architecture_id: ARCH-036
title: Persist selected discount sets on existing policy rows
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-DATABASE-001"]
enables: ["ARCH-036-SHOPIFY-001", "ARCH-036-API-002", "ARCH-036-BACKGROUND-002", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-DATABASE-002 — Persist selected discount sets on existing policy rows

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Represent a bounded merchant-selected set of permitted discount IDs in existing policy rows with no new selection table.

## Context

`ShopSettings.fixedShopifyDiscountId` and the corresponding override column are single Shopify discount references. Woo merchants require checkboxes for multiple permitted coupons, but a later outreach still chooses at most one proven eligible coupon. `RecoveryOutreachAttempt.offerSnapshot` already persists immutable per-attempt evidence.

## Scope

Add a bounded JSON array field (e.g. `selectedDiscountIds`) to existing `ShopSettings` and `ShopRecoveryPolicyOverride`, retaining `fixedShopifyDiscountId` and its FKs for legacy Shopify reads/writes. Constrain shape, size, uniqueness, status and policy mode in application/DB checks where feasible; reuse existing attempt `offerSnapshot` and do not add an outreach table.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

`NONE` and `AI_BEST_APPLICABLE` have an empty explicit selected set; Woo `FIXED` requires at least one valid current same-Shop Woo coupon, with no duplicate ID and a firm cap (propose 50). Shopify legacy FIXED remains the existing single FK until migrated separately. A saved selection may later become unavailable; retain selection for editing but never use unavailable coupons for messaging. Admin override source takes precedence without silently replacing merchant preferences. Revision conflicts must use existing CAS/updatedAt policy semantics. Protect against foreign-Shop JSON IDs transactionally, because JSON lacks relational FKs.

## Work Items

- [ ] Add bounded selected IDs JSON fields to existing policy/override rows and migrate defaults.
- [ ] Record invariants for same-Shop IDs and policy mode; choose schema shape and check constraints.
- [ ] Test concurrent edits, invalid/foreign references, stale selection and legacy Shopify settings.
- [ ] Document absence of JSON element foreign keys and corresponding transaction-level enforcement.

## Interfaces / Contracts

`ShopSettings`, `ShopRecoveryPolicyOverride`, `RecoveryOutreachAttempt.offerSnapshot` (unchanged physical field), existing shared `RecoveryOfferMode`, API-002 and future selection contract.

## Dependencies

- `ARCH-036-DATABASE-001`

## Enables

- `ARCH-036-SHOPIFY-001`
- `ARCH-036-API-002`
- `ARCH-036-BACKGROUND-002`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] No new tables; merchant and admin override rows can store distinct bounded selections.
- [ ] Foreign-Shop, malformed, duplicate, oversized or invalid-mode sets are refused without partial writes.
- [ ] Existing Shopify `fixedShopifyDiscountId` references and saved data remain valid.
- [ ] Revoked/expired coupons do not become usable merely because IDs remain in JSON.
- [ ] No previously committed outreach snapshot is rewritten.

## Validation

- [ ] Prisma schema validation and disposable PostgreSQL migration tests
- [ ] JSON constraints, same-Shop application contract fixtures and CAS race cases
- [ ] Shopify existing settings/override regressions and `git diff --check`

## Implementation Notes

Do not implement selection API or change default offer modes in this task.

For developer execution, use the canonical `/moda_developer_create ARCH-036-DATABASE-002` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-DATABASE-002`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
