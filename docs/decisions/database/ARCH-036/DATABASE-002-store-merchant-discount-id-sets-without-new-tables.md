---
id: ARCH-036-DATABASE-002
architecture_id: ARCH-036
title: "Superseded — merchant selections use existing discount flag and policy FK"
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-DATABASE-002 — Superseded — no discount selection migration

## Architecture

- Architecture: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; owner: `moda_database` / `moda-interact-database`.
- **Defined but not materialised.** This task is **Ready**: catalogue schema changes were superseded and no prerequisite implementation is needed. It has no developer worktree or claimed attempt yet.

## Objective

Superseded. Woo multi-checkbox selections will be stored in existing `ShopifyDiscount.isAvailable` flags. No JSONB selected-ID array, `selectedForRecovery` column, or database constraint change is authorised.

## Context

Existing `ShopSettings.recoveryOfferMode` determines NONE, FIXED and AI_BEST_APPLICABLE. Current ARCH-016 SQL CHECK constraints require `fixedShopifyDiscountId` to be a **valid non-null foreign key** for `FIXED` on both ShopSettings and ShopRecoveryPolicyOverride. For Woo FIXED, API-002 will atomically set that FK to one genuinely selected, same-Shop `ShopifyDiscount.id` row, as a compatibility anchor. The full selection is every coupon row where `isAvailable=true`. When NONE or AI, the existing policy FK is null. `fixedShopifyDiscountId` cannot hold an arbitrary `woo:coupon:<id>` string: its foreign key references `ShopifyDiscount.id`. `shopifyDiscountNodeId` may safely hold that namespaced provider ID.

## Scope

Retain this task only as a history of the rejected database migration plan. No modifications to `moda-interact-database` are required by ARCH-036.

## Out of Scope

- No new selection, coupon, snapshot, join, provider-proof or audit tables.
- No new provider API, outgoing message format, background candidate ranking, Shopify merchant settings change or admin UI implementation.
- No creation of an immutable evidence/proof ledger; existing outreach `offerSnapshot` remains authoritative for a particular attempt.
- No history rewrite, data reset, deletion of missing/expired selected discount IDs, or `_index.md` update.
- No work on tasks listed under Enables.

## Requirements

Existing policy, override and `RecoveryOutreachAttempt` FIXED constraints remain untouched. API must enforce same-Shop FK ownership and update selected flags plus the compatibility anchor in one transaction with Shop locking/revision. For a FIXED save with no checked rows, reject rather than violate the database check. Unchecking the last coupon requires switching the mode away from FIXED. Admin override remains its own single existing FK; never store fake IDs.

## Work Items

- [x] Reject the proposed selectedDiscountIds JSONB and constraint migration.
- [x] Document application-owned consistency in API-002 and Background tasks.
- [x] Remove this task from active dependencies.

## Interfaces / Contracts

No new database interfaces. Reuse `ShopifyDiscount.isAvailable`, `ShopSettings.recoveryOfferMode`, and `ShopSettings.fixedShopifyDiscountId` with existing referential integrity.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

- [x] No new tables, columns, indexes, constraints, enums or migrations planned.
- [x] Existing Shopify selection FK and outreach constraints remain valid.
- [x] No executable task depends on DATABASE-002.

## Validation

Documentation-only dependency and schema inspection. No Prisma or SQL change is expected from this task.

## Stop Condition

Superseded. Do not claim, materialise or execute this task. The architect will retain it only for historical traceability.

## Implementation Notes

Do not claim, materialise or execute. API-002, BACKGROUND-002 and SHOPIFY-001 own the relevant behavioural changes.

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

No unreviewed assumption may relax the array bound, legacy Shopify FK path or app-owned tenant membership validation.

### Unresolved Issues

None recorded; return any migration/Prisma incompatibility or missing same-shop enforcement contract to the architect.

### Architectural Concerns

Any proposed new table, changed outreach semantics, shared contract adjustment or consumer-breaking schema rename requires a separate Architect decision.

## Architect Review

### Review Status

Superseded (planning only).

### Review Notes

No schema or migration work is authorised; no repository implementation has been submitted.

### Reviewed Files

Existing Prisma schema and ARCH-016 FK/CHECK constraints were inspected for this task decision.

### Validation Reviewed

Task definition/dependency validation only.

### Architecture Conformance

Consistent with the revised no-DDL ARCH-036 direction.

### Follow-up

Use the API/Background/Shopify application-owned tasks; do not implement the original database task.
