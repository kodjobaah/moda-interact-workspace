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
depends_on: ["ARCH-036-BACKGROUND-001"]
enables: ["ARCH-036-SYSTEM-TEST-002"]
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


Commerce already contains deterministic discount reader/evaluator machinery for Shopify. Background sync writes normalized Woo coupon facts to the existing `providerSnapshot` JSONB. Adapt only the existing CommerceAgent discount reader/evaluator for its actual tool/runtime use to read supported Woo facts without conflating merchant selection with provider eligibility. No Shared publication or new evaluator framework is required.

## Scope

Add provider-neutral cached-rule reader/adapter for Woo `percent` and `fixed_cart` coupon snapshots, relying on the existing evidence evaluator and trusted basket facts. Do not implement storefront writes or an independent Commerce coupon database.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements


- Normalize supported Woo `percent` and `fixed_cart` rules from existing `providerSnapshot`, current `providerStatus`, `fixedSelectable`, timestamps and trusted basket facts. For FIXED use selected-only candidates; for AI include all supported ACTIVE candidates. Do not conflate merchant checkbox selection with provider/current/checkout eligibility.
- Preserve existing Shopify single-FK reader/evaluator inputs and regression fixtures. The adapter does not authenticate to WooCommerce or fetch Woo coupons; only Background owns direct live proof.
- Verify the existing CommerceAgent operation uses the adapted evaluator. Background-003 independently owns send-time coupon proof and must not depend on this task; Commerce evaluation alone never certifies outbound proof or warrants a new cross-service schema.
- Fail closed for unsupported rules, unknown facts or missing provenance; no new Shared contract, DB model or additional outbound side effects.

## Work Items

- [ ] Map supported Woo snapshot rules into existing evaluator inputs.
- [ ] Reuse/extend existing deterministic evidence adapters, not duplicate logic.
- [ ] Add provider-separated Shopify/Woo evaluation, tie/unknown/invalid-rule tests.
- [ ] Document proof consumer inputs required by Background runtime.

## Interfaces / Contracts


Existing ARCH-020 Commerce discount reader/evaluator interfaces and current shared package exports where already in use, **not** new ARCH-036 Shared exports. Existing `providerSnapshot` data produced by BACKGROUND-001. Background-003 owns selection/reverification/outbound.

## Dependencies


- `ARCH-036-BACKGROUND-001` — normalized Woo coupon snapshot fields established and accepted.

## Enables


- `ARCH-036-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Woo FIXED evaluator considers selected alternatives, AI considers all supported ACTIVE coupons.
- [ ] One eligible offer result maximum, no stacking/false claim.
- [ ] Missing provenance and unsupported restrictions are denied or UNKNOWN.
- [ ] Existing Shopify evaluator regression fixtures pass.

## Validation

- [ ] Commerce focused evaluator/reader integration and property-style fixtures
- [ ] Declared Commerce typecheck/lint/test/build and `git diff --check`

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

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
