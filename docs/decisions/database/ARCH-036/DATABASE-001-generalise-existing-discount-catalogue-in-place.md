---
id: ARCH-036-DATABASE-001
architecture_id: ARCH-036
title: Generalise the existing discount catalogue in place
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-036-DATABASE-002", "ARCH-036-BACKGROUND-001", "ARCH-036-API-001", "ARCH-036-API-003", "ARCH-036-COMMERCE-001", "ARCH-036-ADMIN-001", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-DATABASE-001 — Generalise the existing discount catalogue in place

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Make existing `ShopifyDiscountCatalogue` and `ShopifyDiscount` records provider-neutral without creating or renaming physical discount tables.

## Context

The existing Prisma models live in PostgreSQL schema `shopify` and already contain shop-scoped sync generations, provider snapshots, discount availability and foreign-key relationships. Shopify must retain every existing discount identity and reference during this change.

## Scope

Add a provider discriminator and stable external discount identity to the existing rows. Prefer provider-neutral Prisma model/field names mapped to the existing physical tables/columns (`@@map`/`@map`) so historical migration history is untouched. Preserve IDs, relations, uniqueness, indexes and Shopify data; extend the existing catalogue row with bounded durable page-progress metadata needed for Woo snapshot uploads.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Existing Shopify records are classified as SHOPIFY without changing their primary keys or referenced IDs. Woo discount identities are stable per `(shopId, provider, externalId)` and cannot impersonate Shopify identifiers. Catalogue generation is per shop/provider; partial generations are not CURRENT. Additive migration only; no new discount, sync staging, or join tables, and no destructive physical rename. Use existing schema `shopify` unless an independently approved migration says otherwise. Address null/backfill/default handling in fresh and upgrade databases.

## Work Items

- [ ] Inspect all current Prisma discount relationships, indexes, and historical migrations.
- [ ] Write additive schema migration plus provider-ID mapping and bounded sync-progress fields on existing tables.
- [ ] Verify Shopify backfill/reference continuity and fresh/upgrade/repeat migration proof.
- [ ] Run schema and PostgreSQL integration tests for provider/shop identity and generation fencing.

## Interfaces / Contracts

Existing `Shop`, `ShopSettings`, `ShopRecoveryPolicyOverride`, `RecoveryOutreachAttempt` relations; provider-neutral Prisma views of physical `shopify.ShopifyDiscountCatalogue` and `shopify.ShopifyDiscount`; `Shop.platform` provider identity.

## Dependencies

None.

## Enables

- `ARCH-036-DATABASE-002`
- `ARCH-036-BACKGROUND-001`
- `ARCH-036-API-001`
- `ARCH-036-API-003`
- `ARCH-036-COMMERCE-001`
- `ARCH-036-ADMIN-001`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] No new physical discount or sync tables and no changes to historical migration files.
- [ ] Existing Shopify discount row IDs, relation references, and valid queries survive migration.
- [ ] Woo `(shop, provider, externalId)` identities cannot collide across shops/providers.
- [ ] Unfinished Woo upload generation is never represented as a usable CURRENT catalogue; stale sync token/page replay fails closed.
- [ ] Prisma validation, fresh/upgrade/re-run migrations and representative indexed queries pass.

## Validation

- [ ] Prisma validate and migration checksum/SQL fixture checks
- [ ] Disposable PostgreSQL fresh, upgrade and repeat migration rehearsals
- [ ] Existing Shopify catalogue FK/query and Woo identity/generation integration cases
- [ ] Repository typecheck/tests actually declared by package.json and `git diff --check`

## Implementation Notes

This task changes only the database repository. It must not update producers/consumers or invent a Woo delivery mechanism. Schema mapping compatibility is reviewed before data readers are migrated.

For developer execution, use the canonical `/moda_developer_create ARCH-036-DATABASE-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-DATABASE-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
