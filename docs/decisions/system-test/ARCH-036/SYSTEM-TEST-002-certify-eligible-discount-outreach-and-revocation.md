---
id: ARCH-036-SYSTEM-TEST-002
architecture_id: ARCH-036
title: Certify eligible Woo discount outreach and failure handling
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-SYSTEM-TEST-001", "ARCH-036-API-003", "ARCH-036-COMMERCE-001", "ARCH-036-BACKGROUND-002", "ARCH-036-BACKGROUND-003"]
enables: []
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-SYSTEM-TEST-002 — Certify eligible Woo discount outreach and failure handling

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Independently prove FIXED and AI Woo recovery offers are safe, scoped and sent only with valid proof.

## Context

Catalogue/selection tests alone cannot verify a customer-facing offer. Provider grant and outbound attempt immutability must be exercised through the full service boundary.

## Scope

End-to-end authenticated Woo fixture, stored customer checkout, Commerce eligibility and Background/WhatsApp simulator. Validate NONE, FIXED selected set, AI supported candidate, stale/expired/usage-restricted/zero-valued cases and service outages.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

- Verify NONE never offers coupons, FIXED uses only selected ACTIVE supported same-Shop coupons, AI may use any ACTIVE supported coupon regardless of selection flag.
- Recheck live Woo provider coupon against selected cached row and immutable checkout facts at send time. A code rename, expiry, removal, usage exhaustion or stale/revoked grant fails closed.
- Prove one real internal `ShopifyDiscount.id` in any FIXED attempt FK and one verified `offerSnapshot`; no fake compatibility ID, no stacking, no double-charge or invalid FIXED NULL-FK attempt.
- Validate duplicate/retried background jobs, concurrent merchant deselection, a changed coupon between catalogue and send, admin overrides, and Shopify regression cases.
- No database schema changes; use disposable PostgreSQL and black-box service fixtures.

## Work Items

- [ ] Run supported percent/fixed-cart customer eligibility scenario.
- [ ] Run denial/failure matrix and observe no false coupon promises.
- [ ] Prove repeat/retry/billing idempotency and read grant revocation.
- [ ] Report release readiness and any explicitly unsupported coupon semantics.

## Interfaces / Contracts

API-003 verified provider read; Commerce evidence; Background outreach; WhatsApp simulator; existing ShopSettings/Discount/outreach DB tables.

## Dependencies

- `ARCH-036-SYSTEM-TEST-001`
- `ARCH-036-API-003`
- `ARCH-036-COMMERCE-001`
- `ARCH-036-BACKGROUND-002`
- `ARCH-036-BACKGROUND-003`

## Enables

None.

## Acceptance Criteria

- [ ] Only a proven eligible coupon is promised, at most one per recovery attempt.
- [ ] Failure/revocation/stale/invalid states are fail closed with bounded errors.
- [ ] Store and customer isolation, conversation ordering and billing unaffected.
- [ ] No new discount tables and Shopify recovery regressions green.

## Validation

- [ ] Full cross-service BLACK_BOX/integration matrix
- [ ] Provider HTTP/Meta simulator, disposable database evidence and `git diff --check`

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Only mark ARCH-036 Implemented after terminal system tests and integration review pass.

For developer execution, use the canonical `/moda_developer_create ARCH-036-SYSTEM-TEST-002` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-SYSTEM-TEST-002`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
