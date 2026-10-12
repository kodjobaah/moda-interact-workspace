---
id: ARCH-036-SYSTEM-TEST-001
architecture_id: ARCH-036
title: Certify shared catalogue sync and merchant selection
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-DATABASE-001", "ARCH-036-DATABASE-002", "ARCH-036-SHARED-003", "ARCH-036-BACKGROUND-001", "ARCH-036-SHOPIFY-001", "ARCH-036-API-001", "ARCH-036-WOOCOMMERCE-001", "ARCH-036-WOOCOMMERCE-002", "ARCH-036-API-002", "ARCH-036-WOOCOMMERCE-003", "ARCH-036-ADMIN-001"]
enables: ["ARCH-036-SYSTEM-TEST-002"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-SYSTEM-TEST-001 — Certify shared catalogue sync and merchant selection

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Independently verify Woo coupon preloading/updates and merchant checkbox persistence without regressing Shopify.

## Context

This is a terminal architecture-level test after its implementation dependencies are accepted; developer manual LocalWP testing may happen before invoking it.

## Scope

Black-box Woo plugin + hosted API + database tests for initial sync, page retries, stale generation, deletes, identity, selection CAS, 20-language UI and Shopify compatibility. Keep independent test fixtures and reproducible evidence.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Use disposable test Shop and coupon fixtures; establish observable outcomes via public plugin/admin/API boundaries, not unverified internal service mocks. Test at least 2 shops, >10 coupons, >1 snapshot page, updates/deletes, zero value and expiry, offline plugin/no WP-Cron. No new physical discount tables allowed. Do not treat the browser preview as proof of recovery send.

## Work Items

- [ ] Create isolated cross-provider fixtures and pagination scenario.
- [ ] Exercise initial sync, repeated pages, missed deletion and recovery after interrupted generation.
- [ ] Save multiple coupon IDs, verify mode switching and Shopify isolation.
- [ ] Record database state and screenshots or API evidence.

## Interfaces / Contracts

Test harness: LocalWP/Woo fixture, authenticated API, Prisma read-only proof, Shopify fixture; no privileged tenant bypass.

## Dependencies

- `ARCH-036-DATABASE-001`
- `ARCH-036-DATABASE-002`
- `ARCH-036-SHARED-003`
- `ARCH-036-BACKGROUND-001`
- `ARCH-036-SHOPIFY-001`
- `ARCH-036-API-001`
- `ARCH-036-WOOCOMMERCE-001`
- `ARCH-036-WOOCOMMERCE-002`
- `ARCH-036-API-002`
- `ARCH-036-WOOCOMMERCE-003`
- `ARCH-036-ADMIN-001`

## Enables

- `ARCH-036-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Current generation only after full upload, with missing coupons unavailable.
- [ ] Repeated pagination has no missing/duplicate identities, foreign tenant leak or fake discounts.
- [ ] Merchant settings persist and Shopify single-choice workflow still works.
- [ ] All required tests have reproducible per-scenario evidence.

## Validation

- [ ] Black-box and integration harness with disposable Postgres and LocalWP fixtures
- [ ] 20-language UI and shop/auth boundary evidence, `git diff --check`

## Implementation Notes

Terminal test only: no implementation task depends on SYSTEM-TEST-001.

For developer execution, use the canonical `/moda_developer_create ARCH-036-SYSTEM-TEST-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-SYSTEM-TEST-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
