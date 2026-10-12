---
id: ARCH-036-SHARED-001
architecture_id: ARCH-036
title: Define versioned Woo coupon snapshot contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-036-SHARED-003"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-SHARED-001 — Define versioned Woo coupon snapshot contract

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Define the canonical bounded runtime contract for plugin-to-API WooCommerce coupon snapshot synchronisation.

## Context

The Woo PHP plugin cannot import a TypeScript runtime schema. The canonical wire contract must still be versioned and have parity fixtures consumed by both PHP and the hosted API.

## Scope

Publishable shared schema/type definitions for start/page/complete snapshots, coupon identity, provider type, normalized rules, generation token and idempotency evidence. Include frozen JSON golden fixtures with PHP-compatible validation expectations. No implementation, database writes or npm publication in this task.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Snapshot is bound to authenticated installation/shop, never a browser-supplied shop ID. Use `woo.discounts.sync.v1`, bounded page size/field lengths and a deterministic page digest; completed generation alone may make coupons selectable. Preserve coupon code, type (`percent`/`fixed_cart` and classified unsupported types), amount as decimal string, currency, expiry, usage and relevant restriction flags, with unsupported rules distinguished from eligible evidence. No entire customer/cart payloads, credentials or arbitrary provider URLs.

## Work Items

- [ ] Define v1 wire schemas, IDs, bounded sizes and error semantics.
- [ ] Define begin/page/complete lifecycle and replay/partial-failure fixture vectors.
- [ ] Export portable fixtures and runtime TypeScript validator.
- [ ] Test malformed, duplicate, out-of-order and adversarial payload rejection.

## Interfaces / Contracts

Shared package `@modainteract/moda-interact-shared` versioned exports; producers `moda-interact-woocommerce` PHP and hosted API; consumer hosted API; canonical JSON fixtures checked on both sides.

## Dependencies

None.

## Enables

- `ARCH-036-SHARED-003`

## Acceptance Criteria

- [ ] Consumers have one authoritative v1 schema and golden payload fixtures.
- [ ] PHP fixtures and Shared schema agree, including bad/expired/restricted examples.
- [ ] No shop credentials/customer PII and no silent promotion of partial snapshots.
- [ ] Contract changes do not alter existing Shopify event schemas.

## Validation

- [ ] Focused Shared schema tests and fixture corpus
- [ ] Build/typecheck/lint per Shared package scripts; `git diff --check`

## Implementation Notes

Runtime Shared package publication belongs only to SHARED-003.

For developer execution, use the canonical `/moda_developer_create ARCH-036-SHARED-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-SHARED-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
