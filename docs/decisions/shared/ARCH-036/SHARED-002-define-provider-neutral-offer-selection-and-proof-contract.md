---
id: ARCH-036-SHARED-002
architecture_id: ARCH-036
title: "Define minimal cross-service coupon proof contract without policy schema changes"
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

# ARCH-036-SHARED-002 — Define provider-neutral selected-offer and proof contracts

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Define a minimal versioned, shop-bound coupon **send-time proof envelope** shared between the API-owned Woo verification port and Background/Commerce consumers. Do not change the existing recovery-policy schema.

## Context

No new selected-ID JSON storage exists. Woo merchant selections are `ShopifyDiscount.isAvailable=true`, and the existing `fixedShopifyDiscountId` FK is populated with one real selected row when mode FIXED. Therefore published `EffectiveRecoveryPolicySchema` can remain unchanged. The genuinely shared new boundary is provider verification: one selected coupon and a bounded proof or denial that Background must parse.

## Scope

Add a narrow versioned coupon-proof contract (one internal `ShopifyDiscount.id`, Shop ID, provider source/identity, verified rule snapshot/digest, optional checkout provenance, verified and expiry timestamps, and `QUALIFIES`/`DENIED`/`UNKNOWN`). Provider-specific live Woo rule evaluation remains API-owned; Background uses the proof for one attempt and freezes only safe evidence in existing `offerSnapshot`.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

No `selectedDiscountIds` arrays, new policy enums, new policy field or fake compatibility ID. The existing Shared `recovery-policy` export remains unchanged and old Shopify policy fixtures must continue parsing. Fail closed on stale, invalid, foreign-shop, unproven, expired or unsupported evidence. The selection flag is **not** a claim of checkout applicability. Only one coupon may be promised per attempt.

## Work Items

- [ ] Define minimal versioned shop/coupon proof and denial schemas.
- [ ] Test wrong-Shop, expired, missing checkout facts and unsupported-rule outcomes.
- [ ] Prove unchanged compatibility of existing Shopify FIXED policy and outreach snapshots.
- [ ] Document API producer, Background/Commerce consumers and publication version.

## Interfaces / Contracts

`@modainteract/moda-interact-shared/discounts` (only required proof envelope); existing `/recovery-policy` remains unchanged. API-003 produces proof; BACKGROUND-003 and COMMERCE-001 consume it.

## Dependencies

None.

## Enables

- `ARCH-036-SHARED-003`

## Acceptance Criteria

- [ ] Existing Shared policy validator unchanged and Shopify fixtures pass.
- [ ] Proof envelope is safe, bounded and provider/shop bound.
- [ ] No selected-ID list or database schema changes.

## Validation

- [ ] Contract unit/negative/golden fixtures and Shopify backwards compatibility.
- [ ] Declared Shared typecheck/lint/build and `git diff --check`.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Do not publish or integrate this task; SHARED-003 is the release gate.

For developer execution, use the canonical `/moda_developer_create ARCH-036-SHARED-002` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-SHARED-002`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
