---
id: ARCH-036-API-004
architecture_id: ARCH-036
title: Read Woo offer settings independently and list provider-identifiable coupons
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 25
executor: developer
claimed_at: 2026-10-15T22:43:12Z
attempt: 2
depends_on: ["ARCH-036-API-002"]
enables: ["ARCH-036-WOOCOMMERCE-004"]
created: 2026-10-15
updated: 2026-10-15
---

# ARCH-036-API-004 — Decouple settings GET and remove Moda-only coupon eligibility filters

## Architecture

- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Bounded follow-up to complete `ARCH-036-API-002`; no new coupon ownership or Save/CAS design.
- Owner: `moda_api`, repository `moda-interact-api`; coordinator: `moda_architect`.
- Materialised on parent task branch `task/ARCH-036-API-004`. Attempt 1 was returned Changes Requested; the developer resolved the worktree cleanliness blocker and claimed Attempt 2. Preserve the prior review and its corrections below.

## Observed defect

API logs repeatedly show `merchant.discount_offers.access.denied` with `reason=catalogue_not_current`. `GET /v1/merchant/discount-offers` currently calls `currentCatalogue()` and fails when Background has marked the catalogue `SYNC_REQUIRED`, `SYNCING`, `ERROR` or `UNAVAILABLE`. This blocks merchants from **reading the already saved offer mode**, even when it is `NONE` and no coupon browsing is needed. Recovery summary/policy GET still succeeds, so the misleading WooCommerce screen is caused by the discount-offer read gate, not a general connection failure.

## Objective

Return persisted merchant recovery-offer mode and selected Woo coupon IDs **regardless of catalogue readiness**. For the separately paginated catalogue, list provider-observed, identifiable/code-usable Woo coupons from a completed `CURRENT` scan **without Moda-imposed commercial validity rules**. WooCommerce—not API-004—decides whether a coupon is redeemable.

## Scope and invariants

- `GET /v1/merchant/discount-offers` must use the existing shop/installation authentication and provider ownership checks; read `ShopSettings`, the existing merchant `ShopifyDiscount.isAvailable` flags, effective Admin override and optional catalogue metadata without invoking `currentCatalogue()`.
- Missing `ShopifyDiscountCatalogue` is valid for configuration reads and must not be misrepresented as a successful empty coupon catalogue. Keep the existing stable response shape and revision semantics (revision is informational, **not a PUT precondition**).
- `GET /v1/merchant/discount-catalogue` **must still** require `CURRENT` plus a successful complete scan, with shop, Woo identity, current observed generation, true provider presence and safely deliverable coupon code. **Remove** API eligibility gates based on `providerStatus=ACTIVE`, `fixedSelectable` as a *commercial* decision, `startsAt`/`endsAt`, usage, amount and a hardcoded provider discount-type allowlist. A real `REMOVED` coupon must not be presented as currently existing. Preserve pagination/search filters and tenant safety. Coordinate with BACKGROUND-005's storage-safe Woo provider marker; do not assume arbitrary discount types fit `providerType VARCHAR(128)`.
- Preserve `PUT /v1/merchant/discount-offers` as agreed: Shop-row-locked, atomic full-set replacement, no catalogue-generation CAS, no provider-eligibility validation; merchant owns Woo `isAvailable`, mode and FIXED FK anchor. NONE and AI modes must be writable even if the provider catalogue is down, subject to existing request/tenant constraints.
- Do not change recovery-delay/follow-up policy or Admin override effective semantics; do not alter Shopify API behaviour. Woo catalogue responses must not imply redemption is guaranteed: Woo validates coupon acceptance at checkout. A coupon with missing/unusable code needs an explicit non-sendable representation, never a fabricated code or a silently shortened one.
- No new database model/migration, Background edits, new Woo REST provider calls, Shared package changes or `_index.md` changes.

## Required scenarios

1. **No catalogue yet:** saved `NONE` and zero selected IDs returned by settings GET; coupon listing returns `catalogue_not_current` rather than `items: []` success.
2. **Catalogue not ready:** GET saved mode/IDs under `SYNC_REQUIRED`, `SYNCING`, `ERROR` and `UNAVAILABLE`, including FIXED selections that are now ineligible.
3. **Current catalogue:** settings and list responses retain their existing successful contracts; list provider-observed Woo codes **even when unknown type, zero amount, expired, usage-exhausted or unusual restriction**; selected flags reflect persisted `isAvailable` values. The Admin override is reported accurately. Preserve an untruncated >255-character code.
4. **Independent Save:** switching to `NONE` or `AI_BEST_APPLICABLE` succeeds even when catalogue is unavailable; don't reintroduce the superseded CAS/eligibility checks from the API-002 Attempt 1 review.
5. **Security:** unauthorized, cross-shop, revoked installation and Shopify-principal calls stay rejected without disclosing coupon IDs or shop settings.
6. **No broadening:** settings reads don't fetch remote Woo coupons and don't silently change `ShopifyDiscountCatalogue.status` or any merchant state. Catalogue filtering still excludes cross-tenant, not-observed, confirmed-removed and technically non-sendable identities, **not** coupons disliked by Moda business-rule checks.

## ASCII interaction

```text
Woo merchant UI
      |
      +-- GET /v1/merchant/discount-offers
      |           |
      |           +-- authenticated Shop + saved ShopSettings
      |           +-- selected Woo isAvailable IDs / Admin override
      |           '-- 200 even if coupon catalogue ERROR/missing
      |
      '-- GET /v1/merchant/discount-catalogue
                  |
                  +-- CURRENT + complete last scan? -- yes --> observed Woo codes
                  '-- not CURRENT -------------------------> 503
```

## Acceptance criteria

- [ ] `GET /discount-offers` returns valid persisted NONE/FIXED/AI config independently of catalogue presence and status.
- [ ] `GET /discount-catalogue` continues to fail closed when not CURRENT; **all observed code-usable Woo coupons** (including unselected, expired, zero amount, unknown type and exhausted) remain listed when CURRENT. Confirmed removed/no-code items are not misleadingly presented as sendable.
- [ ] Existing authentication, isolation, override projection, full-set PUT and Woo merchant-owned `isAvailable` semantics remain unchanged; long coupon codes are not truncated and unknown type is not a failure.
- [ ] No new client-facing `expectedRevision` requirement or unnecessary user Refresh for a saved NONE configuration.

## Required validation

- [ ] Unit/route/contract tests for `GET` under missing/SYNC_REQUIRED/SYNCING/ERROR/UNAVAILABLE/CURRENT; expected response shape unchanged.
- [ ] Disposable PostgreSQL tests with persisted FIXED selection/anchor and Admin override, including concurrent Background status changes and failed read-grant cases; catalogue fixtures with unknown Woo types, zero amount, expired/exhausted, >255-character codes, confirmed removal, and Shopify lookalikes must prove Woo-only inclusive results and isolation.
- [ ] Negative tenant/authentication and Shopify-isolation regression tests; existing PUT concurrency tests remain passing.
- [ ] Typecheck, lint, full unit suite, build, PostgreSQL integration and `git diff --check`. List results and known baseline issues exactly.

## Stop condition

Return Completion Report in `review` status to `moda_architect` after implementation/validation. Do not start WOOCOMMERCE-004 automatically; do not modify `_index.md`.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at `2026-10-15T22:43:12Z`, following the Changes Requested review of Attempt 1. Attempt 2 has not yet submitted implementation or validation evidence. See the durable Attempt 2 claim and synchronization record below; Attempt 1 review history remains unchanged.

### Files Changed

No new application source changes have been made in Attempt 2. The API implementation baseline at `2e6e736ae8a2575733dc76344c6758413dc15d30` is present on `main`, `origin/main`, and the API task branch; the commit includes the offer service/tests, two API-004 tests, a database gitlink change, and a `start-dev.sh` change. This baseline was not authored or changed during the Attempt 2 claim. The shared API checkout is clean at claim time.

### Work Completed

Attempt 2 is claimed and both canonical task worktrees were verified and synchronized. Implementation and validation work remain to be done; the code baseline has not been reviewed in this attempt.

### Validation Results

No Attempt 2 implementation validation has been run yet. The implementation task branch is synchronized at `2e6e736ae8a2575733dc76344c6758413dc15d30`, equal to current `origin/main`; this is a synchronization baseline, not validation evidence.

### Deviations

None recorded.

### Unresolved Issues

Attempt 1's review findings remain to be resolved and evidenced in Attempt 2: establish task ownership/provenance for the API baseline, verify its scope (including the database gitlink and `start-dev.sh` changes), and run the required validations. The baseline is now committed and present on `main` as well as the task branch; this history is not rewritten or treated as a separate task delta.

## Developer Self-Review - Changes Requested

### Reviewed Attempt

Attempt 1, developer execution. Review date: 2026-10-15.

### Review Findings

- `MODA_WORKTREE_ISOLATION_ERROR`: the canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004` is on `task/ARCH-036-API-004` but is clean at `2e6e736ae8a2575733dc76344c6758413dc15d30`, identical to `origin/main`; it has no API-004 implementation commits. The candidate source/test edits are in the shared `main` checkout, which is not an authorized substitute for the task worktree.
- Required corrections: preserve the shared-checkout edits and unrelated work; deliberately reconcile only the intended API-004 changes into the canonical implementation task worktree on `task/ARCH-036-API-004`; keep unrelated `start-dev.sh` changes and any unjustified database gitlink change out of the task branch; commit and publish the task-owned implementation changes. Do not use broad staging or overwrite/reset the shared checkout.
- After reconciliation, run the task's required route/unit/security and PostgreSQL validations, typecheck, lint, full unit suite, build and `git diff --check`. Use only a verified disposable PostgreSQL target and record exact commands/results plus known baseline failures. Update Work Items, Acceptance Criteria, deviations and unresolved issues from the resulting evidence.
- The current task branch contains no accepted review or implementation evidence. This is a failed review for Attempt 1, not a completion decision; no files were changed in the implementation repository during this review.

### State Transition

`status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. The next `/moda_developer_create ARCH-036-API-004` claim increments to Attempt 2 exactly once after the developer resolves the isolation issue.

### Physical Worktree Evidence

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-036-API-004`, branch `task/ARCH-036-API-004`, clean at local `HEAD` `250fac140392aec6a0d1680bffa69f9a06a9cf33`, synchronized by an origin/main merge; task branch is 45 commits ahead of `origin/task/ARCH-036-API-004` and remains a fast-forward descendant.
- Implementation task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004`, branch `task/ARCH-036-API-004`, clean at `2e6e736ae8a2575733dc76344c6758413dc15d30`, equal to `origin/main`; no implementation delta.
- Shared API source checkout: branch `main`, dirty with the candidate changes enumerated in the Completion Report. It was not used as the implementation worktree and was left untouched.

### Validation Reviewed

No implementation validation evidence was available in the canonical task worktree. No tests, typecheck, lint, build or database tests were run for this review.

## 2026-10-15 — Post-review implementation branch state

After the Changes Requested review was committed, the API repository state changed externally. The shared checkout is now clean at `2e6e736ae8a2575733dc76344c6758413dc15d30`, and that same `feat(api)` commit is present on `main`, `origin/main`, and `task/ARCH-036-API-004`/`origin/task/ARCH-036-API-004`. The commit changes the discount-offer service and tests, adds two API-004 tests, and also changes the database gitlink and `start-dev.sh`. The canonical API-004 implementation worktree is clean at that same commit; it has zero commits beyond `origin/main`, so no task-specific implementation delta remains. This confirms the code is committed, but does not establish a separate task-branch implementation review, task-attempt ownership, or validation evidence. The earlier statements describing the shared checkout as dirty reflect the state at review time; this entry records the subsequent observed state. No source changes, merges, or pushes to the API repository were performed by this review. The task remains `ready`, Attempt 1; no completion or acceptance decision is made. The prior Changes Requested findings concerning isolation/provenance and unverified required validation remain unresolved.

## Developer Claim — Attempt 2

- Claimed by developer at `2026-10-15T22:43:12Z`; `status: in_progress`, `executor: developer`, `attempt: 2`.
- Dependency `ARCH-036-API-002` was verified Complete through its canonical launcher route before the claim.
- Parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-036-API-004`, branch `task/ARCH-036-API-004`, was clean at `b6687b8cdc94268468ac71c098ab233881bb37fc`, equal to `origin/task/ARCH-036-API-004`. Current `origin/main` was already an ancestor; no parent merge was needed.
- Implementation task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004`, branch `task/ARCH-036-API-004`, was clean at `2e6e736ae8a2575733dc76344c6758413dc15d30`, equal to `origin/main` and `origin/task/ARCH-036-API-004`. No mainline merge or task-branch fast-forward was needed.
- No application source edits were made as part of claim preparation. The developer now owns implementation in the canonical API-004 worktree. Required validations remain those listed above; only use a verified disposable PostgreSQL target.

## Architect Review

### Review Status

Pending implementation evidence.
