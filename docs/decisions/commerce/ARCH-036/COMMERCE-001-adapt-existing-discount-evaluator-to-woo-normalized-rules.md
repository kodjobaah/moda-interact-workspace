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
status: in_progress
priority: 50
executor: developer
claimed_at: 2026-11-02T14:41:55Z
attempt: 1
depends_on: ["ARCH-036-BACKGROUND-001"]
enables: []
created: 2026-10-12
updated: 2026-11-02
---

# ARCH-036-COMMERCE-001 — Adapt existing Commerce discount evaluator for Woo normalized rules

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Canonical parent task definition is published on `task/ARCH-036-COMMERCE-001`. Implementation remains unclaimed; prepare it through `/moda_developer_create` before editing application code.

## Objective

Extend the retained Commerce deterministic discount reader/evaluator and local preview operations to consume existing Woo catalogue facts. Reuse one evaluator and preserve existing Shopify behavior. This is cached, advisory evaluation, not proof that Woo will redeem a coupon.

## Context


Commerce already contains deterministic discount reader/evaluator machinery for Shopify. Background sync writes normalized Woo coupon facts to the existing `providerSnapshot` JSONB. Adapt only the existing CommerceAgent discount reader/evaluator for its actual tool/runtime use to read supported Woo facts without conflating merchant selection with provider eligibility. No Shared publication or new evaluator framework is required.

## Scope

Implement a Commerce-owned, tenant-scoped Woo cached-rule adapter and wire it into the existing `discounts.getOptions` / `discounts.evaluate` local operation path in `src/commerce/preview/local-policy-providers.ts`, using the existing reader/evaluator contracts. Inspect the current dispatch and trusted basket/product-fact adapters before editing; route by the authoritative Shop platform, never by an untrusted offer identifier. Support only demonstrably representable `percent` and `fixed_cart` facts. No background conversation worker or ARCH-052 initial-outreach change is required.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

- Read the current same-Shop catalogue and discount rows, including provider identity, lifecycle, freshness, expiry, merchant selection and bounded `providerSnapshot` facts. `isAvailable` is merchant selection on both platforms, not provider validity. Reject foreign-Shop and wrong-provider IDs before evaluating them.
- For Woo merchant NONE return no options; FIXED uses valid checked candidates; AI_BEST_APPLICABLE uses valid supported candidates regardless of checked state. Honor an existing effective Admin single-FK override independently of merchant checked flags. Do not change Shopify policy semantics or store additional policy state.
- Inspect the actual snapshot producer `src/providers/woo-coupon-normalization.ts` in Background. Optional or absent attributes do not prove absence of restrictions. `providerStatus=ACTIVE` and `fixedSelectable` establish catalogue/code usability, not checkout eligibility. Never fabricate trusted currency, tax basis, rounding/allocation, usage, email, category, sale-item or customer facts to obtain ELIGIBLE.
- Woo percentage amounts use percentage units (for example 10 means 10%); the existing Shopify reader accepts fractions (0.10 means 10%). Use a provider-specific conversion into the common rule model with decimal-safe handling; retain Shopify boundary regressions. Fixed-cart rules require trusted matching currency and supported amount/allocation semantics.
- Incomplete, malformed, stale or unsupported facts produce existing UNKNOWN/UNSUPPORTED/error outcomes; evaluate known failed conditions as ineligible. Preserve cancellation, deadlines, bounded pagination and existing evidence provenance/fingerprinting. Do not present cached evidence as a provider redemption guarantee.
- Wire the adapter through the actual existing Commerce local-operation registrations, not only a standalone helper. Woo evaluation must not require Shopify `read_discounts`, a Shopify session/domain or a fabricated Shopify product identity. Use existing trusted basket/product-fact inputs; when a required Woo input is unavailable, return UNKNOWN/unavailable rather than fetch live Woo data or silently fall back to Shopify. Any genuinely missing cross-service contract is an architect blocker.
- Preserve published operation inputs/results and evidence contracts. No new Shared release, schema, direct Woo provider fetch, coupon mutation, redemption, outbound send or second evaluator. ARCH-052 owns current initial-outreach runtime and source validation; retired ARCH-036-BACKGROUND-003 is not a dependency or proof consumer.

## Work Items

- [ ] Trace the current options/evaluation registration, effective policy and trusted basket inputs; record the concrete integration seam.
- [ ] Implement tenant/provider-scoped cached Woo rule reads and explicit unit/unknown-condition mapping into the retained evaluator.
- [ ] Integrate existing options/evaluation operations with provider dispatch and preserve Shopify authorization and behavior.
- [ ] Add focused operation-level tests for Woo policies/override, invalid/foreign IDs, stale/partial data, deadlines and Shopify regression.
- [ ] Document exactly which cached facts can be evaluated and which remain UNKNOWN; do not claim outbound or provider redemption certification.

## Interfaces / Contracts

Existing ARCH-020 Commerce reader/evaluator, `DiscountRuleSnapshot`, local operation and published evidence contracts; existing Shop policy and Woo `providerSnapshot` rows from accepted ARCH-036-BACKGROUND-001. Internal Commerce adapters may change within this task. Published cross-service contracts and ARCH-052 initial-outreach code remain unchanged.

## Dependencies


- `ARCH-036-BACKGROUND-001` — normalized Woo coupon snapshot fields established and accepted.

## Enables

None. The retired ARCH-036-SYSTEM-TEST-002 is not reactivated. ARCH-052 initial-outreach certification does not depend on this cached-evaluator work.

## Acceptance Criteria

- [ ] Real local options/evaluation registrations reach the Woo adapter for an authenticated Woo Shop; Shopify operations retain their existing provider path.
- [ ] NONE/FIXED/AI and effective Admin override obey the rules above, with same-Shop/provider isolation and no forced Shopify credentials for Woo.
- [ ] A complete supported fixture with trusted basket facts yields the correct deterministic evidence; incomplete or unsupported real snapshots cannot produce fabricated eligibility.
- [ ] Woo 10% and Shopify 0.10 normalization agree, without unit mixing; fixed-cart currency/rounding uncertainty fails closed.
- [ ] One offer is evaluated per evaluation operation; no new stacking, coupon application or one-offer limit is imposed on ARCH-052 initial outreach.
- [ ] Existing Shopify reader/evaluator/preview regression fixtures pass; no new schema, published contract or outbound behavior is introduced.

## Validation

- [ ] Focused reader/evaluator tests plus registered local-operation integration covering Woo success, UNKNOWN/unsupported, merchant modes, override precedence, tenant/provider rejection, stale catalogue and cancellation/deadline.
- [ ] Existing Shopify reader/evaluator/preview tests, including percentage normalization and fixed-policy behavior.
- [ ] Run repository-declared typecheck, changed-file lint, build and `git diff --check`; report any existing unrelated failure accurately. Use disposable PostgreSQL for database-backed integration when required by the actual test path; never test against persistent merchant data.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

No LLM prompt change is required merely to reuse deterministic evaluation; report any missing runtime connector to architect.

For developer execution, use the canonical `/moda_developer_create ARCH-036-COMMERCE-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-COMMERCE-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-11-02T14:41:55Z. Attempt 0 review history is preserved below.

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

## Definition reconciliation — 2026-11-02

The earlier four-task-session deferral is lifted by the developer’s explicit request on 2 November 2026 to correct this definition so implementation can begin. This bounded Commerce evaluator/preview work is now Ready; ARCH-036-BACKGROUND-001 is Complete. The old Background-003 proof ownership, retired SYSTEM-TEST-002 dependency and initial-outreach one-offer assumption are removed. Implementation remains unclaimed at Attempt 0, with developer-controlled completion: architect acceptance followed by an explicit developer completion decision.
