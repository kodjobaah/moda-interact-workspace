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
status: complete
priority: 50
executor: null
claimed_at: null
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
- Canonical parent task definition is published on `task/ARCH-036-COMMERCE-001`. Attempt 1 is accepted and explicitly completed by the developer; both task branches are published.

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

- [x] Trace the current options/evaluation registration, effective policy and trusted basket inputs; record the concrete integration seam.
- [x] Implement tenant/provider-scoped cached Woo rule reads and explicit unit/unknown-condition mapping into the retained evaluator.
- [x] Integrate existing options/evaluation operations with provider dispatch and preserve Shopify authorization and behavior.
- [x] Add focused operation-level tests for Woo policies/override, invalid/foreign IDs, stale/partial data, deadlines and Shopify regression.
- [x] Document exactly which cached facts can be evaluated and which remain UNKNOWN; do not claim outbound or provider redemption certification.

## Interfaces / Contracts

Existing ARCH-020 Commerce reader/evaluator, `DiscountRuleSnapshot`, local operation and published evidence contracts; existing Shop policy and Woo `providerSnapshot` rows from accepted ARCH-036-BACKGROUND-001. Internal Commerce adapters may change within this task. Published cross-service contracts and ARCH-052 initial-outreach code remain unchanged.

## Dependencies


- `ARCH-036-BACKGROUND-001` — normalized Woo coupon snapshot fields established and accepted.

## Enables

None. The retired ARCH-036-SYSTEM-TEST-002 is not reactivated. ARCH-052 initial-outreach certification does not depend on this cached-evaluator work.

## Acceptance Criteria

- [x] Real local options/evaluation registrations reach the Woo adapter for an authenticated Woo Shop; Shopify operations retain their existing provider path.
- [x] NONE/FIXED/AI and effective Admin override obey the rules above, with same-Shop/provider isolation and no forced Shopify credentials for Woo.
- [x] A complete supported fixture with trusted basket facts yields the correct deterministic evidence; incomplete or unsupported real snapshots cannot produce fabricated eligibility.
- [x] Woo 10% and Shopify 0.10 normalization agree, without unit mixing; fixed-cart currency/rounding uncertainty fails closed.
- [x] One offer is evaluated per evaluation operation; no new stacking, coupon application or one-offer limit is imposed on ARCH-052 initial outreach.
- [x] Existing Shopify reader/evaluator/preview regression fixtures pass; no new schema, published contract or outbound behavior is introduced.

## Validation

- [x] Focused reader/evaluator tests plus registered local-operation integration covering Woo success, UNKNOWN/unsupported, merchant modes, override precedence, tenant/provider rejection, stale catalogue and cancellation/deadline.
- [x] Existing Shopify reader/evaluator/preview tests, including percentage normalization and fixed-policy behavior.
- [x] Run repository-declared typecheck, changed-file lint, build and `git diff --check`; report any existing unrelated failure accurately. Use disposable PostgreSQL for database-backed integration when required by the actual test path; never test against persistent merchant data.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

No LLM prompt change is required merely to reuse deterministic evaluation; report any missing runtime connector to architect.

For developer execution, use the canonical `/moda_developer_create ARCH-036-COMMERCE-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-COMMERCE-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

## Completion Report

### Status

Complete — Attempt 1. Architect Review Accepted and explicit Developer Completion Decision recorded on 2026-11-02. Execution and completion modes remain developer-owned; claim cleared without incrementing the attempt.

### Files Changed and Work Completed

- `src/commerce/preview/local-policy-providers.ts`: authoritative Shop-platform dispatch, same-Shop/current-generation Woo catalogue reads, merchant NONE/FIXED/AI policy, independent Admin override, and conservative trusted-input handling through registered local operations.
- `src/commerce/discounts/reader/reader.ts` and `types.ts`: Woo percentage-unit conversion, normalized cached-rule mapping, exact FIXED authorization independent of bounded options, and truncation propagation. Dates are filtered before limits; options remain bounded to 50.
- `tests/arch036-commerce-discount-reader.test.ts` and `tests/arch036-commerce-local-discounts.test.ts`: focused mapping/arithmetic and operation coverage including 51 selections, expired leading rows, foreign-Shop rejection, override, stale/deadline handling and Shopify FIXED scope regression.
- `docs/discount-support-matrix.md`: supported cached facts, bounded selection behavior, and unavailable/unsupported cases.

Material assistance: developer-requested `moda_commerce` implementation assistance; independent architect review identified the selection-pagination P2, then verified its correction. Execution ownership stayed with the developer.

### Validation Results

- Independently verified submitted suites: 8/8 tests; additional cursor-aware review diagnostic: 1/1. Combined 3 files / 9 tests passed under Node 24.19.0. Diagnostic source/output is retained in `evidence/COMMERCE-001-attempt-1-selection-recheck.md`; temporary implementation test removed.
- Changed-file lint and production build passed as reported by the executor; existing Nunjucks warning remains. These were not independently rerun during publication.
- Repository typecheck was run and reports the existing unrelated NODE_ENV error at `tests/system-commerce-tool-sync.test.ts:305`; not recorded as passing.
- `git diff --check` passed again before publication. Reviewed six-file SHA-256 fingerprint matches the published content: `cd237a1aae9ef4226f4a0905a56c4052899166c9dc934eab4ddfe45e19ff74b6`.
- Registered-operation tests use isolated Prisma fixtures; no persistent merchant database was used.

### Deviations, Assumptions and Remaining Limits

No new schema, published contracts, live Woo reads, checkout mutation or ARCH-052 outreach changes. Synthetic complete fixtures establish deterministic arithmetic, not provider redemption proof. The actual Woo adapter lacks trusted product facts/calculation semantics and deliberately returns UNAVAILABLE/unsupported; the 51st selected coupon is authorized but cannot fabricate eligibility. The known unrelated typecheck failure is accepted as a documented validation limitation. No task-blocking issue remains.

### Git / VCS and Physical Isolation

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-036-COMMERCE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-COMMERCE-001`.
- Both branches: `task/ARCH-036-COMMERCE-001`; route revalidated with the canonical launcher.
- Parent start-of-attempt mainline incorporation is recorded by `a63797f45`; claim is `4233ad771`. Implementation started at mainline `d0ade086b60b42a4145cc7e50836c2b2c8258de5`. No new attempt or new mainline merge was performed during completion.
- Implementation commit: `67107a79567cf91df7fdb25dbbefe63abae07233`, pushed to `origin/task/ARCH-036-COMMERCE-001`.
- Prior durable passing correction review: parent `25efb16a6fc65ef74905baa8085dfdf5818b82b0`. This completion report is published in the subsequent parent completion commit (its containing Git commit identifies the report revision).
- Shared checkouts were not switched or used for task changes; no other task worktree reused; no parent submodule gitlink staged. Neither branch merged into main.

## Architect Review

### Review Status

**Accepted — Attempt 1**, 2026-11-02. The previously reviewed local correction is now published unchanged as `67107a79567cf91df7fdb25dbbefe63abae07233`. The prior P2 is resolved and no blocking findings remain. Historical pre-submission reviews below are preserved, superseded by this acceptance.

### Developer Self-Review Accepted and Completion Decision

The explicit `/moda_developer_update ARCH-036-COMMERCE-001 complete Architect Review Accepted` request authorizes completion after reconciliation/publication. The six-file implementation matches the independently reviewed fingerprint; Work Items and Acceptance Criteria are satisfied within the documented cached/advisory scope. Record the developer's explicit completion decision: **Complete**, Attempt 1 unchanged, executor and claimed_at cleared.

### Dependency Frontier

`ARCH-036-BACKGROUND-001` is the accepted prerequisite. No active task explicitly depends on COMMERCE-001, and `enables` is empty. The historical SYSTEM-TEST-002 reference is inside a superseded task whose operative `depends_on` is empty; it remains superseded. No downstream task is promoted and no manual system-test gate is changed.

## Definition reconciliation — 2026-11-02

The earlier four-task-session deferral is lifted by the developer’s explicit request on 2 November 2026 to correct this definition so implementation can begin. This bounded Commerce evaluator/preview work is now Ready; ARCH-036-BACKGROUND-001 is Complete. The old Background-003 proof ownership, retired SYSTEM-TEST-002 dependency and initial-outreach one-offer assumption are removed. Implementation remains unclaimed at Attempt 0, with developer-controlled completion: architect acceptance followed by an explicit developer completion decision.


## Architect local implementation review — Attempt 1, 2 November 2026

### Decision and lifecycle

**Changes requested on the local working-tree implementation; no architect acceptance.** This is the requested pre-submission review, not completion. Preserve `status: in_progress`, `executor: developer`, the original claim timestamp, Attempt 1 and developer-controlled completion. No downstream task is promoted or executed. The developer still owns reconciliation and publication of the implementation through `/moda_developer_update ARCH-036-COMMERCE-001`.

Reviewed six changed/untracked files in the canonical implementation worktree, based on HEAD `d0ade086b60b42a4145cc7e50836c2b2c8258de5`. The implementation remains uncommitted and unpublished. Only this parent review/evidence is published by the architect.

### Finding

**P2 — the first selected page is incorrectly used as the complete authorization set.** In `src/commerce/preview/local-policy-providers.ts:318–323`, Woo FIXED policy reads at most 50 checked rows, filters dates after that limit, and puts only those IDs in `fixedOfferIds`. `reader.ts:183–195` then treats this bounded subset as the complete selected set: an exact request for a valid 51st selected coupon is rejected with DENIED. `getDiscountOptions` queries only those first 50 IDs, so its provider cannot see the additional selected rows and returns `truncated: false`. Expired/not-started rows occupying that first page can further hide valid later rows. This breaks the required selected-candidate semantics and accurate bounded pagination.

Preserve bounded reads; do not solve this with an unbounded selected-set load. Separate exact same-Shop selected-ID authorization from the bounded options scan, or use an equivalent bounded design that can authorize an exact selected coupon beyond page one. Apply relevant validity predicates before page limits and accurately signal when the offered set is truncated. Preserve the independent effective Admin override and reject truly unselected/foreign/provider-mismatched IDs.

### Validation and inspected behavior

- Independent run with Node 24.19.0: the **two submitted test files passed, 6/6 tests**.
- Two temporary review diagnostics used the actual registered local operations with a Prisma fixture honoring the `take`, ID-filter and cursor arguments for 51 selected coupons. Both failed: options returned `truncated: false` instead of true; exact evaluation of `woo:coupon:151` returned DENIED. This establishes the bounded-set defect without claiming a live database run. [Reproduction and output](evidence/COMMERCE-001-attempt-1-pagination-review.md).
- Temporary diagnostic file was removed after execution; no implementation source/test changes retained by the architect. `git diff --check` passed before review publication.
- Inspected the current Background snapshot producer: `WooCoupon:code`, `woo:coupon:<id>`, explicit percentage units, bounded optional restriction facts and code identity agree with the adapter. Same-Shop/platform dispatch, Woo scope separation, fixed override precedence, unknown restrictions, currency/rounding limitations, cancellation/deadline gates and conservative absence of provider-redemption claims are the appropriate direction.
- Current Woo calculation semantics and trusted product facts remain intentionally unavailable; the support matrix documents this. The synthetic arithmetic fixture is not provider proof. This review does not request inventing facts or widening ARCH-052 outreach behavior.
- Actual Shopify local-operation routing is not exercised by the six submitted tests: the fraction comparison injects Shopify-shaped data under a Woo policy. Include a real Shopify-policy/local-registration regression with valid/missing scopes and preserved FIXED behavior when addressing the defect, as required by the task. Also cover expired leading rows, a selected ID beyond the first page, accurate truncation, and continued denial of unselected/foreign IDs.
- Lint, build and the existing `tests/system-commerce-tool-sync.test.ts:305` NODE_ENV typecheck failure are recorded as executor-reported results; architect did not rerun those commands.

### Follow-up

Correct the bounded-selection/authorization behavior and supply the focused regressions above. Reconcile the Completion Report and publish implementation evidence through the developer workflow before final architect acceptance. Completion still requires the explicit developer completion decision after acceptance; no claim or lifecycle transition was made by this review.

Reviewed working-tree fingerprint (SHA-256 of the ordered six relative paths and file bytes, NUL-separated): `fc4caffd64a3892180a29f6f0f85be3b3f7163679a843392638b7516cf779a38`.


## Architect local correction review — Attempt 1, 2 November 2026

### Outcome

**Previous P2 resolved; no new blocking implementation findings in the inspected local changes.** This supersedes the earlier local Changes Requested finding, while preserving its evidence as history. This is a working-tree correction review, not acceptance of a published submission or a task-completion decision. Preserve `in_progress`, `executor: developer`, the original claim and Attempt 1. No downstream transition is required (`enables` is empty).

### Correction verified

The policy resolver now distinguishes an exact requested offer from options enumeration. Exact Woo FIXED authorization uses a same-Shop, selected, current-generation, valid-provider and in-date `findFirst` query; it does not depend on the first options page. Options select 51 valid rows to detect overflow, expose at most 50 IDs and propagate truncation through the reader. Date predicates occur before query limits in selection and provider reads. Effective Admin overrides retain their independent single-ID path; Shopify retains its FIXED/provider-scope path. The support matrix documents the bound and exact authorization behavior.

### Independent validation

- Submitted focused suites: **2 files / 8 tests passed**. These cover percentage units, selection/override behavior, stale catalogue/deadline rejection, 51 selections/expired rows, foreign-Shop rejection and registered Shopify FIXED routing with present/missing `read_discounts` scope.
- Added one temporary review-only diagnostic with a cursor-aware Prisma fixture: **passed**. It asserts the exact 50 distinct expected IDs after excluding an expired row, `truncated: true`, `woo:coupon:151` reaching evaluation as UNAVAILABLE rather than DENIED, and unselected `woo:coupon:999` remaining DENIED. Combined run: **3 files / 9 tests passed**, Node 24.19.0. [Diagnostic and output](evidence/COMMERCE-001-attempt-1-selection-recheck.md).
- The temporary test was removed after execution; implementation edits remain solely developer-owned. `git diff --check` passed.
- Executor-reported changed-file lint and production build passes remain recorded as supplied evidence; the Nunjucks warning and pre-existing NODE_ENV typecheck error at `tests/system-commerce-tool-sync.test.ts:305` are not claimed resolved. Those commands were not independently repeated by the architect.
- Woo trusted product facts/calculation semantics remain unavailable in the actual local adapter, so UNAVAILABLE/unsupported behavior is deliberate. No fabricated eligibility, provider redemption guarantee, new public contract or ARCH-052 behavior is approved by this review.

### Publication and completion boundary

Implementation remains uncommitted on the canonical task worktree based on `d0ade086b60b42a4145cc7e50836c2b2c8258de5`. Reconcile the Completion Report and publish the implementation through `/moda_developer_update ARCH-036-COMMERCE-001` before final acceptance of the submitted revision. Developer-controlled completion still requires an explicit developer completion decision. This review publishes only parent documentation/evidence and does not change task lifecycle or implementation Git state.

Reviewed working-tree fingerprint (SHA-256 of the ordered six relative paths and file bytes, NUL-separated): `cd237a1aae9ef4226f4a0905a56c4052899166c9dc934eab4ddfe45e19ff74b6`.
