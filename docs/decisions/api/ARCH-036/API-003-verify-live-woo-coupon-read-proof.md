---
id: ARCH-036-API-003
architecture_id: ARCH-036
title: Verify supported Woo coupon rules through the approved read grant
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-API-001", "ARCH-036-SHARED-003"]
enables: ["ARCH-036-BACKGROUND-003", "ARCH-036-SYSTEM-TEST-002"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-API-003 — Verify supported Woo coupon rules through the approved read grant

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Provide a narrowly scoped authoritative Woo coupon read/verification port for send-time discount proof.

## Context

Cached `providerStatus='ACTIVE'`, `fixedSelectable=true` and `isAvailable=true` are necessary for FIXED merchant selection, not sufficient proof of customer-specific coupon eligibility. AI mode may consider unchecked ACTIVE supported coupons.

## Scope

Extend the API-001 approved coupon GET allowlist with detail GET `/wc/v3/coupons/{id}` and relevant bounded coupon metadata. Expose an authenticated, shop/recovery-bound internal verification operation for authorised Background consumers, not a generic HTTP proxy.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

- Use the approved encrypted Woo read grant for bounded, pinned `GET /wp-json/wc/v3/coupons/{providerId}` only. No credentials exposed to Background, merchant browser or logs.
- Recheck exact Shop, original `woo:coupon:<id>` identity, current provider status, expiry, usage exhaustion, rules and authoritative checkout facts. For FIXED, verify the candidate remains selected (`isAvailable=true`) at proof time. For AI, ignore selection flags but require ACTIVE, supported and applicable rules.
- Return Shared proof outcome `QUALIFIES`/`DENIED`/`UNKNOWN` with bounded validity; never prove customer-specific restrictions solely from an inventory listing. Network, missing grant, unsupported rule or stale basket means no coupon promise.
- Existing records, offerSnapshot and provider credentials remain unchanged.

## Work Items

- [ ] Inspect and extend approved Woo provider GET allowlist for coupon detail only.
- [ ] Implement bounded verified coupon read against trusted shop and basket inputs.
- [ ] Provide narrow internal authenticated proof contract with structured failure codes.
- [ ] Test HTTP credential safety, inaccessible LocalWP, revoked grant and invalid restrictions.

## Interfaces / Contracts

API-001 / `ARCH-026-API-008` provider-read port; Shared proof v1; trusted internal caller and persisted recovery identity; no new provider credentials.

## Dependencies

- `ARCH-036-API-001` (already depends on approved `ARCH-026-API-008`)
- `ARCH-036-SHARED-003`

## Enables

- `ARCH-036-BACKGROUND-003`
- `ARCH-036-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] No credential/URL disclosure and no arbitrary provider reads; the Background worker never receives provider credentials.
- [ ] Supported eligible coupon passes with current provider facts; changed/expired/deleted fails.
- [ ] Absent/invalid read grant or untrusted basket always fails closed.
- [ ] No made-up provider eligibility or coupon-code claims.

## Validation

- [ ] API unit and provider HTTP fixture tests, authorization and SSRF tests
- [ ] Disposable PostgreSQL read-grant identity/cross-shop tests
- [ ] API declared typecheck/lint/test/build and `git diff --check`

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

This task is explicitly gated by pending `ARCH-026-API-008`. Do not infer readiness from code presence; if the grant cannot support coupon proof, report to architect.

For developer execution, use the canonical `/moda_developer_create ARCH-036-API-003` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-API-003`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
