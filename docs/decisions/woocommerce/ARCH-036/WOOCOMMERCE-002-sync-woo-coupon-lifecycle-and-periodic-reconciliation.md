---
id: ARCH-036-WOOCOMMERCE-002
architecture_id: ARCH-036
title: Sync Woo coupon changes and periodic reconciliation
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-WOOCOMMERCE-001"]
enables: ["ARCH-036-WOOCOMMERCE-003", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-WOOCOMMERCE-002 — Sync Woo coupon changes and periodic reconciliation

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Keep the shared coupon catalogue current following Woo coupon mutations, deletions and missed events.

## Context

Coupons may be created, edited, disabled, deleted, redeemed or expire after initial sync. Push-based reconciliation must not trust that all WordPress hooks fire or that WP-Cron runs continuously.

## Scope

Register Woo-supported coupon create/update/delete/status/usage hooks to coalesce full sync requests. Add periodic Action Scheduler reconciliation and reconnect/resume triggers using the existing full-sync producer. Preserve the WordPress Admin local coupon preview.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

No network calls inside Woo coupon save transaction. Coalesce repeated hooks per shop, use a bounded retry policy and an explicit high-water sync request time. Reconciliation handles missed deletes and revocations via completed-generation tombstones. Treat low-traffic WP-Cron delays as freshness risk; catalog freshness guard is enforced in API and Background. On disconnected/revoked installation stop publications; reconcile after reconnect.

## Work Items

- [ ] Wire only officially supported coupon lifecycle events and status transitions.
- [ ] Coalesce and schedule full snapshot work plus periodic reconciliation.
- [ ] Test deletes, missed hooks, failed network and reconnect.
- [ ] Document Action Scheduler/WP-Cron reliability and staleness behaviour.

## Interfaces / Contracts

Woo coupon lifecycle hooks/Action Scheduler; producer from WOOCOMMERCE-001; API-001 server ingest.

## Dependencies

- `ARCH-036-WOOCOMMERCE-001`

## Enables

- `ARCH-036-WOOCOMMERCE-003`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Changes eventually appear through a completed provider generation; missing coupons become unavailable.
- [ ] Retries, duplicate hooks and Woo crashes do not create parallel unbounded jobs.
- [ ] No shopper/cart payload is sent; no direct WordPress-to-Moda database access.
- [ ] A stale catalogue is never treated as proof of a valid recovery coupon.

## Validation

- [ ] WordPress/Woo hook tests and Action Scheduler retry cases
- [ ] Integration against disposable Moda API snapshot fixture and `git diff --check`
- [ ] Woo lint/tests/build/plugin package per declared scripts

## Implementation Notes

Do not invent a second queue framework or WordPress sync storage table.

For developer execution, use the canonical `/moda_developer_create ARCH-036-WOOCOMMERCE-002` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-WOOCOMMERCE-002`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
