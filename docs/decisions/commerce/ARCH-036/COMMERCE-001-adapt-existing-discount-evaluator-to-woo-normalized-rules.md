---
id: ARCH-036-COMMERCE-001
architecture_id: ARCH-036
title: Adapt existing Commerce discount evaluator for Woo normalized rules
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-DATABASE-001", "ARCH-036-SHARED-003"]
enables: ["ARCH-036-BACKGROUND-003", "ARCH-036-SYSTEM-TEST-002"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-COMMERCE-001 — Adapt existing Commerce discount evaluator for Woo normalized rules

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Reuse ARCH-020 deterministic discount rule/evidence machinery for normalized Woo coupons without introducing a second evaluator.

## Context

`moda-interact-commerce/src/commerce/discounts/evaluator/` already evaluates normalized eligibility and produces evidence. `read-operation-catalogue.ts` includes Woo coupons.list/retrieve authoring operations, but these are not evidence that a live Woo read grant or outbound proof is working.

## Scope

Add provider-neutral cached-rule reader/adapter for Woo `percent` and `fixed_cart` coupon snapshots, relying on the existing evidence evaluator and trusted basket facts. Do not implement storefront writes or an independent Commerce coupon database.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Preserve existing Shopify rule support, proposal budgeting, evidence TTL/digest and unknown/denied semantics. For Woo, compute only provable monetary discounts using exact decimal/currency rules; unsupported restrictions, absent facts, zero amounts or expired snapshots do not qualify. AI candidate ranking can prefer greatest provable discount with deterministic tie-breaking, but never authorize customer-facing claims without API-003 live proof at send time.

## Work Items

- [ ] Map supported Woo snapshot rules into existing evaluator inputs.
- [ ] Reuse/extend existing deterministic evidence adapters, not duplicate logic.
- [ ] Add provider-separated Shopify/Woo evaluation, tie/unknown/invalid-rule tests.
- [ ] Document proof consumer inputs required by Background runtime.

## Interfaces / Contracts

Existing ARCH-020 discount reader/evaluator ports and Shared v1 provider-neutral normalized rule/evidence contracts; existing mapped Discount data.

## Dependencies

- `ARCH-036-DATABASE-001`
- `ARCH-036-SHARED-003`

## Enables

- `ARCH-036-BACKGROUND-003`
- `ARCH-036-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Supported Woo fixed-cart/percent arithmetic matches exact currency tests.
- [ ] Unknown restrictions, stale snapshots and zero-valued coupons do not qualify.
- [ ] Shopify evaluator regressions pass; AI cannot invent a new coupon.
- [ ] No user-facing discount offer without provider verification.

## Validation

- [ ] Commerce focused evaluator/reader integration and property-style fixtures
- [ ] Declared Commerce typecheck/lint/test/build and `git diff --check`

## Implementation Notes

No LLM prompt change is required merely to reuse deterministic evaluation; report any missing runtime connector to architect.

For developer execution, use the canonical `/moda_developer_create ARCH-036-COMMERCE-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-COMMERCE-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
