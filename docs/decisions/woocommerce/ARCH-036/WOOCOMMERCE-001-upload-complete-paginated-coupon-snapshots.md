---
id: ARCH-036-WOOCOMMERCE-001
architecture_id: ARCH-036
title: Upload complete Woo coupon snapshots asynchronously
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-API-001", "ARCH-036-SHARED-003"]
enables: ["ARCH-036-WOOCOMMERCE-002", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-WOOCOMMERCE-001 — Upload complete Woo coupon snapshots asynchronously

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Add a bounded Woo plugin producer that enumerates the local coupon catalogue and pushes a complete versioned generation to Moda.

## Context

`RecoveryCouponCatalogueController` already reads a paginated local preview. Snapshot publication must be separate from browser reads and from normal coupon-save requests.

## Scope

Add a PHP Action Scheduler job to enumerate coupon IDs using keyset/cursor pagination, produce validated v1 snapshots and call API begin/page/complete with server-side installation credentials. Use Woo `WC_Coupon` public getters; no new WordPress custom tables or consumer keys sent to browsers.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Trigger an initial full preload after a verified connected installation and approved merchant state; do not block admin navigation or coupon saves. Stable page boundaries despite coupon edits; retries must replay identical accepted page payloads or restart a full generation when contents change. Cap page sizes and memory/network work; a failed page leaves the catalogue non-current, never partially current. Explicitly cover Woo read-only/LocalWP outbound transport and offline failure. Shared contract golden fixtures must match PHP output.

## Work Items

- [ ] Implement initial-load job and cursor-based coupon enumeration.
- [ ] Normalize supported coupon data and restriction metadata into Shared fixture-compatible v1 pages.
- [ ] Push start/page/complete with idempotent retries and bounded failures.
- [ ] Add WordPress integration tests for empty/large/changing catalogues and disconnected sites.

## Interfaces / Contracts

Producer: Woo PHP plugin; consumer: API-001 versioned coupon snapshot ingest; existing installation secret stored server-side; Action Scheduler where available.

## Dependencies

- `ARCH-036-API-001`
- `ARCH-036-SHARED-003`

## Enables

- `ARCH-036-WOOCOMMERCE-002`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Initial plugin connection eventually yields a completed current catalogue for authenticated shop.
- [ ] No full-catalogue read or provider network call in the WordPress coupon edit request.
- [ ] Retrials do not duplicate rows, leak keys or falsely finish truncated scans.
- [ ] Fixtures include expiry, usage limits, zero-value and unsupported coupon types.

## Validation

- [ ] Woo PHPUnit/PHP syntax plus Action Scheduler fixture tests
- [ ] Shared golden fixture cross-validation and forced network outage tests
- [ ] Woo JS/i18n regressions, plugin packaging and `git diff --check`

## Implementation Notes

This task implements initial/full sync only. Change hooks and recurring reconciliation belong to WOOCOMMERCE-002.

For developer execution, use the canonical `/moda_developer_create ARCH-036-WOOCOMMERCE-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-WOOCOMMERCE-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
