---
id: ARCH-036-BACKGROUND-001
architecture_id: ARCH-036
title: Preserve Shopify discount sync on shared tables
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-DATABASE-001"]
enables: ["ARCH-036-SHOPIFY-001", "ARCH-036-BACKGROUND-002", "ARCH-036-ADMIN-001", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-BACKGROUND-001 — Preserve Shopify discount sync on shared tables

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Adapt the existing Shopify discount synchronisation worker to the provider-neutral Prisma models without changing established Shopify behaviour.

## Context

`src/services/shopify-discount-catalogue.service.ts` currently uses `shopifyDiscountCatalogue`, `shopifyDiscount` and a raw SQL lock on `shopify.ShopifyDiscountCatalogue`. Shopify webhook and subscription-driven sync must remain operational.

## Scope

Update Shopify Background service and focused worker tests for provider-neutral Prisma names/identity. Keep the existing GraphQL provider, queue, activation criteria, statuses, lock semantics and generation invalidation; no WooCommerce sync consumer is added here.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Shopify ACTIVE/TRIALING, onboarding and offline-session `read_discounts` eligibility preserved. Shop+provider token prevents a Woo sync from changing Shopify catalogue. Existing raw SQL lock must point to the still-unchanged physical table. Reconciliation invalidates only that shop/provider rows. Queue contract and logs retain current semantics.

## Work Items

- [ ] Switch Shopify catalogue DB reads/writes to mapped provider-neutral models.
- [ ] Retain transaction lock and request/reconcile error paths.
- [ ] Run subscription, webhook, duplicate, stale generation and uninstall regressions.
- [ ] Verify no Woo records or alternate-provider sessions are touched.

## Interfaces / Contracts

Existing `shopifyDiscountProvider`, `SHOPIFY_DISCOUNT_SYNC` Shared contracts, provider-neutral DB Prisma mapping from DATABASE-001.

## Dependencies

- `ARCH-036-DATABASE-001`

## Enables

- `ARCH-036-SHOPIFY-001`
- `ARCH-036-BACKGROUND-002`
- `ARCH-036-ADMIN-001`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Existing Shopify sync and webhook tests remain green, including generation and stale token cases.
- [ ] No change to Shopify GraphQL data requests/acknowledgement or queue payload.
- [ ] Cross-provider and cross-shop writes are impossible.
- [ ] No new background queue introduced.

## Validation

- [ ] Background focused discount sync worker unit tests
- [ ] Disposable PostgreSQL provider/generation concurrency tests
- [ ] Declared Background typecheck/build and `git diff --check`

## Implementation Notes

Consumer-side product offer policy changes are in BACKGROUND-002/003, not this task.

For developer execution, use the canonical `/moda_developer_create ARCH-036-BACKGROUND-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-BACKGROUND-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
