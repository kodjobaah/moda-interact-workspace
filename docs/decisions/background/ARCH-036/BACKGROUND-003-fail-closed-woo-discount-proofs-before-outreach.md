---
id: ARCH-036-BACKGROUND-003
architecture_id: ARCH-036
title: Require live Woo coupon proof before outbound recovery offers
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-BACKGROUND-002", "ARCH-036-COMMERCE-001", "ARCH-036-API-003", "ARCH-036-WOOCOMMERCE-003"]
enables: ["ARCH-036-SYSTEM-TEST-002"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-BACKGROUND-003 — Require live Woo coupon proof before outbound recovery offers

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Integrate deterministic candidate evaluation and authoritative Woo coupon proof into the existing RecoveryOutreachAttempt lifecycle before sending a coupon claim.

## Context

The existing recovery worker snapshots offer metadata per attempt and owns WhatsApp/credit timing. A cached coupon or merchant-selected checkbox is not enough evidence to promise a redeemable offer.

## Scope

Choose at most one proven eligible coupon per outreach from FIXED selected set or AI current catalogue. Call API-003 narrow proof, persist immutable provider-neutral evidence into existing `offerSnapshot` and use existing approved outbound template/message composition only where safe. Otherwise send a truthful no-coupon message or fail closed under the approved policy; never charge for a coupon promise that was not actually sent.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Support only provider-proofable positive-value `percent`/`fixed_cart` initially. Rank by provable customer savings using Commerce evaluator; deterministic tie-break, no LLM invented code and no stacking. Re-evaluate at send time and respect deadline, revocation, catalogue freshness and failed provider proof. Use existing WhatsApp send and billing idempotency/recipient snapshot rules from ARCH-028; preserve follow-up ordering and existing initial vs follow-up credit semantics. An already sent immutable attempt must not be overwritten after coupon changes. Do not invent Meta template variable positions or coupon redemption URLs.

## Work Items

- [ ] Wire bounded candidate/ranking/proof within existing outbound lifecycle.
- [ ] Persist one immutable offer evidence snapshot and guard retry/duplicate sends.
- [ ] Handle unavailable provider, stale proof, unsupported rules and invalidated coupon without false claims.
- [ ] Test Meta template compatibility, billing idempotency and message ordering under retries.

## Interfaces / Contracts

Background policy candidate resolver, Commerce evaluator from COMMERCE-001, internal API-003 proof, Shared v1 evidence and existing `RecoveryOutreachAttempt.offerSnapshot`.

## Dependencies

- `ARCH-036-BACKGROUND-002`
- `ARCH-036-COMMERCE-001`
- `ARCH-036-API-003`
- `ARCH-036-WOOCOMMERCE-003`

## Enables

- `ARCH-036-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] No proactive message contains coupon data without current trusted provider proof.
- [ ] One and only one coupon may be offered per attempt; selected IDs are not stacked.
- [ ] Stale, revoked, expired, invalid or unsupported coupon evidence results in safe absence of coupon or blocked send.
- [ ] Existing Shopify recovery outreach and credit consumption remain unchanged.
- [ ] Duplicate/out-of-order retries cannot swap coupon proof on an existing attempt.

## Validation

- [ ] Background outbound/idempotency unit + integration tests, provider-proof fixture matrix
- [ ] Disposable PostgreSQL attempt immutability and retry tests
- [ ] WhatsApp sending fixture and negative proof tests, declared build/typecheck and `git diff --check`

## Implementation Notes

No new outbound template or charge rule. A missing template variable contract must block the coupon claim and return to architect.

For developer execution, use the canonical `/moda_developer_create ARCH-036-BACKGROUND-003` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-BACKGROUND-003`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
