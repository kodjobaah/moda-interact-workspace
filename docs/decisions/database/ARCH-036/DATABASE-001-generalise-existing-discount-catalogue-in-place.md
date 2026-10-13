---
id: ARCH-036-DATABASE-001
architecture_id: ARCH-036
title: "Superseded — existing catalogue requires no schema changes"
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: 2026-10-12
---
# ARCH-036-DATABASE-001 — Superseded — no discount catalogue schema migration

## Architecture

- Architecture: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; owner: `moda_database` / `moda-interact-database`.
- **Defined but not materialised.** No task branch, dedicated worktree, implementation commit or push has been created.

## Objective

Superseded. The existing `shopify.ShopifyDiscountCatalogue` and `shopify.ShopifyDiscount` models and physical tables will be reused for WooCommerce, without migrations or schema edits.

## Context

The current required `shopifyDiscountNodeId` column can hold a stable WooCommerce identity in the form `woo:coupon:<positive-integer-id>`. `providerSnapshot` is already JSONB; `providerStatus`, `isAvailable`, `fixedSelectable`, expiry and sync-generation fields already exist. Existing Shopify consumers retain their current Prisma model/column names. The meaning of `isAvailable` changes in application code, not DDL.

## Scope

Historical task record only; do not implement or materialise. Runtime mapping and sync live in BACKGROUND-001/004 and related API tasks.

## Out of Scope

All Prisma/schema/migration/index/table changes to the existing discount catalogue; changes to ShopifyDiscount/ShopifyDiscountCatalogue physical names and historical migrations.

## Requirements

No schema change, migration, table rename, new provider ID column, enum or PostgreSQL constraint replacement. Required fields must receive meaningful, valid Woo values; arbitrary strings cannot satisfy a foreign key. `shopifyDiscountNodeId` is a regular scoped unique string, not a foreign key.

## Work Items

- [x] Confirm existing fields are sufficient for provider-aware Woo coupon rows.
- [x] Supersede proposed catalogue DDL work.

## Interfaces / Contracts

Existing `ShopifyDiscountCatalogue` / `ShopifyDiscount` Prisma models, with no generated client changes.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

- [x] No catalogue migration is required.
- [x] Implementations depend on API/Background provider mapping rather than this task.

## Validation

Documentation-only status and dependency audit; no implementation testing required.

## Stop Condition

Superseded. Do not claim, materialise or execute this task. The architect will retain it only for historical traceability.

## Implementation Notes

Do not claim or execute this superseded task. Preserve historical record for traceability.

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

The executor will verify checkout, actual dependencies, task worktrees and available toolchain at claim time.

### Unresolved Issues

None recorded.

### Architectural Concerns

Stop and return cross-repository, credential, provider compatibility or schema deviations to `moda_architect`.

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
