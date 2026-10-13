---
id: ARCH-036-BACKGROUND-003
architecture_id: ARCH-036
title: "Resolve and verify one Woo coupon before recovery outreach"
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: 2026-10-13
---

# ARCH-036-BACKGROUND-003 — Require live Woo coupon proof before outbound recovery offers

> **Superseded — do not execute or claim.** Superseded in Attempt 7: outbound recovery coupon selection, live proof and attempt-writing are outside this catalogue/display/configuration-only session. No implementation is authorised.
> The following original description is retained only as historical context; its Work Items, Dependencies and Acceptance Criteria are not operative.

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective


Resolve an eligible coupon candidate under NONE/FIXED/AI policy and **verify the chosen Woo coupon directly from Background** before any outbound discount promise, using only existing catalogue, policy, read-grant and attempt records.

## Context


The former BACKGROUND-002 candidate-filtering task is superseded because candidates must be selected as part of the same send-time flow that verifies provider eligibility. There is no API-003 coupon-proof route or ARCH-036 Shared proof schema. `isAvailable` marks merchant selection, not provider validity; an unchanged FIXED SQL check requires one actual internal discount FK.

## Scope


In `moda-interact-background`, adapt the existing recovery policy resolution and outreach path to resolve bounded candidates, fetch provider coupon detail directly with the secure read-grant client established by BACKGROUND-001, evaluate trusted checkout restrictions and persist one proven existing attempt. Preserve existing Shopify path, Admin override priority, immutable recipient/offer snapshot, outbox, charging and ordering semantics. No other repository changes.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements


1. **Policy/candidates:** NONE => never offer. Woo merchant FIXED => only same-Shop merchant-checked (`isAvailable=true`) ACTIVE, fixedSelectable, in-date coupons from CURRENT catalogue; Woo AI => all supported ACTIVE current coupons whether checked or not. Admin FIXED override retains its one real internal FK independent of merchant checkbox state. Shopify keeps its existing single chosen FK. Bound candidate count, sort deterministically, do not stack offers.
2. **Direct live proof:** for a Woo candidate re-resolve the current ACTIVE shop/installation/read grant and exact `woo:coupon:<id>` identity; use the secure Background Woo client to GET `/wp-json/wc/v3/coupons/{id}` with pinned/TLS/SSRF/no-redirect/size/time rules. Confirm code, provider state, expiry, usage limits and checkout applicability with authoritative basket/customer/product facts. A `wc/v3` coupon object alone does not prove customer-specific rules that lack those facts.
3. **Concurrency/failure:** recheck Shop, grant/credential generation, catalogue freshness, checked FIXED state and provider eligibility before committing/send. If a coupon changes, disappears, is exhausted, unverified or unprovable, fail closed; never create a fake FIXED NULL-FK attempt or claim/promote an offer. Unknown restrictions, timeout, private origin, revoked grant and missing checkout facts are not successful proof. No unsupported coupon-free fallback may silently override FIXED.
4. **Outreach:** persist at most one actual `ShopifyDiscount.id` in `RecoveryOutreachAttempt.fixedShopifyDiscountId` and the immutable provider-verified `offerSnapshot`, preserving recipient snapshot, historical rows, idempotent retry, message ordering, credit usage and no duplicate charges. No database schema or Shared contract changes.
5. **Commerce boundary:** Background owns coupon candidate filtering, authoritative customer/checkout applicability and outbound proof directly. `COMMERCE-001` independently adapts the existing CommerceAgent discount evaluator for its own use; it is not a prerequisite or stand-in for Background proof. Do not introduce a new cross-service contract or LLM eligibility shortcut. Keep Shopify regression tests green.

## Work Items


- [ ] Integrate deterministic NONE/FIXED/AI current-catalogue candidate filtering into existing Background recovery policy resolution (former BACKGROUND-002 scope).
- [ ] Reuse BACKGROUND-001 secure Woo grant/transport to read one exact coupon at send time, verify rules against trusted checkout facts and recheck current selection/grant.
- [ ] Persist one real internal coupon FK and immutable offer evidence only after valid proof; fail closed without invalid FIXED insert on unknown/no candidate.
- [ ] Add selection-race, expiry/deletion/usage exhaustion, revoked/missing keyring, unsupported-customer-rule, duplicate/retry, Admin override and Shopify regression tests.

## Interfaces / Contracts


Existing `ShopifyDiscountCatalogue`, `ShopifyDiscount`, `ShopSettings`, `ShopRecoveryPolicyOverride`, `RecoveryOutreachAttempt`, approved Woo grant and direct `wc/v3/coupons/{id}` GET. Existing Commerce evaluator where its actual call boundary is demonstrated. No API-003 route and no new Shared proof schema.

## Dependencies


- `ARCH-036-BACKGROUND-001` — secure provider client and current catalogue.
- `ARCH-036-API-002` — persisted checkbox/offer-mode semantics.
- `ARCH-036-SHOPIFY-001` — accepted Shopify compatibility with selection semantics.

## Enables


- `ARCH-036-SYSTEM-TEST-002`

## Acceptance Criteria


- [ ] NONE never offers a coupon; FIXED uses only selected valid alternatives; AI ignores selected flags but never offers invalid coupons; Admin and Shopify single-FK rules still work.
- [ ] Background directly obtains provider detail with verified grant, exact site/coupon identity and checkout facts; no API proof proxy/Shared contract.
- [ ] At most one verified coupon and one real internal FK/snapshot appear in an outbound attempt; no invalid FIXED attempt or fabricated discount.
- [ ] Stale/unavailable/expired/removed/exhausted/revoked/unsupported or racing coupons fail closed with no false promise/duplicate charge.
- [ ] Existing database schema and recovery/outbound ordering, retry and billing safety maintained.

## Validation


- [ ] Focused policy/candidate evaluator tests for NONE/FIXED/AI, selected/unselected, admin override and Shopify single FK.
- [ ] Direct Woo live-proof transport and checkout eligibility matrix with hostile/expired/revoked/restricted providers and concurrent selection/grant changes.
- [ ] Disposable PostgreSQL existing CHECK/FK, immutable offerSnapshot and Background outbound idempotency/billing/ordering regression tests.
- [ ] Repository-declared Background typecheck/lint/unit/build and `git diff --check`.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes


Candidate resolution and send-time proof now form one bounded Background task. The previous BACKGROUND-002 is superseded, not an additional dependency. Use the approved provider credential resolver/transport from BACKGROUND-001, and perform required send-time checks within Background. CommerceAgent evaluation is separate and cannot substitute for proof; when a genuine cross-repository gap is found, stop and refer it to the architect. No new contract, schema or coupon source of truth.

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
