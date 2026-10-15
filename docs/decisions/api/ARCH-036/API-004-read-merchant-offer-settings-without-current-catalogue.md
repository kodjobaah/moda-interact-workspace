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
status: review
priority: 25
executor: null
claimed_at: null
attempt: 2
depends_on: ["ARCH-036-API-002"]
enables: ["ARCH-036-WOOCOMMERCE-004"]
created: 2026-10-15
updated: 2026-10-16
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

- [x] `GET /discount-offers` returns valid persisted NONE/FIXED/AI config independently of catalogue presence and status.
- [x] `GET /discount-catalogue` continues to fail closed when not CURRENT; **all observed code-usable Woo coupons** (including unselected, expired, zero amount, unknown type and exhausted) remain listed when CURRENT. Confirmed removed/no-code items are not misleadingly presented as sendable.
- [x] Existing authentication, isolation, override projection, full-set PUT and Woo merchant-owned `isAvailable` semantics remain unchanged; long coupon codes are not truncated and unknown type is not a failure.
- [x] No new client-facing `expectedRevision` requirement or unnecessary user Refresh for a saved NONE configuration.

## Required validation

- [x] Unit/route/contract tests for `GET` under missing/SYNC_REQUIRED/SYNCING/ERROR/UNAVAILABLE/CURRENT; expected response shape unchanged.
- [x] Disposable PostgreSQL tests with persisted FIXED selection/anchor and Admin override, including concurrent Background status changes and failed read-grant cases; catalogue fixtures with unknown Woo types, zero amount, expired/exhausted, >255-character codes, confirmed removal, and Shopify lookalikes must prove Woo-only inclusive results and isolation.
- [x] Negative tenant/authentication and Shopify-isolation regression tests; existing PUT concurrency tests remain passing.
- [x] Typecheck, lint, full unit suite, build, PostgreSQL integration and `git diff --check`. List results and known baseline issues exactly.

## Stop condition

Return Completion Report in `review` status to `moda_architect` after implementation/validation. Do not start WOOCOMMERCE-004 automatically; do not modify `_index.md`.

## Completion Report

### Status

Developer Self-Review Passed — On 2026-10-16, the implementation at `2731e2eda7f2f954d5d6abd98e25eb0dedbfe0b4` passed all functional acceptance criteria and required validation. The earlier PostgreSQL fixture failures and missing cases were corrected and now pass. The unrelated `start-dev.sh` and database gitlink changes from baseline `2e6e736ae8a2575733dc76344c6758413dc15d30` remain documented as non-blocking scope observations; they do not affect the API-004 behavior under review. Because `completion_mode` is `developer`, explicit developer completion is pending. Attempt 1 and earlier Attempt 2 review history are preserved below.

### Files Changed

Attempt 2's current implementation branch is clean at `2731e2eda7f2f954d5d6abd98e25eb0dedbfe0b4`, published to `origin/task/ARCH-036-API-004`. This task-specific commit relocates tests into `tests/unit` and `tests/integration`, repairs the revocation and undeliverable-coupon fixtures, adds concurrent catalogue-status and failed read-grant PostgreSQL cases, and updates test discovery/configuration. The production service behavior remains in baseline commit `2e6e736ae8a2575733dc76344c6758413dc15d30`, which is also on `main` and predates the Attempt 2 claim. That baseline additionally changes `start-dev.sh` and advances the `database` gitlink to ARCH-032 database work; both remain without task-scope authorization.

### Work Completed

The reviewed service reads persisted offer preferences without requiring a current catalogue and retains readiness gating for coupon-list queries. Listing eligibility uses Woo identity, observed generation, not-removed status, and safe code delivery rather than commercial expiry, amount, usage, or type rules. Save remains merchant-owned and does not require catalogue-generation CAS. Attempt 2 now has disposable PostgreSQL coverage for concurrent Background status updates and failed Woo REST read authorization, in addition to the prior settings, catalogue, tenant, and Save cases.

### Validation Results

Attempt 2 re-validation (canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004`, HEAD `2731e2eda7f2f954d5d6abd98e25eb0dedbfe0b4`):

- Passed: `npm --prefix /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004 test` (344 total, 302 passed, 0 failed, 42 skipped; database-backed integration tests run separately).
- Passed: `npm --prefix /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004 run test:arch036-discount-offers:postgres` (7/7 passed using a disposable Docker PostgreSQL database; all 49 migrations applied). This includes the repaired fixtures, concurrent uncommitted Background status change, failed read-grant behavior, and existing Save/scan concurrency tests.
- Passed: `npm --prefix /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004 run typecheck`.
- Passed: `npm --prefix /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004 run lint` (`--max-warnings=0`).
- Passed: `npm --prefix /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004 run build`.
- Passed: `git diff --check origin/main...HEAD` in the implementation worktree.
- The earlier PostgreSQL failures at baseline `2e6e736` were fixed in `2731e2e`; the two previously missing PostgreSQL scenarios now pass. No validation failures remain for the current commit.

### Deviations

Baseline `2e6e736` changes `start-dev.sh` by replacing the public ngrok origin and removing `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` guards. It also advances the `database` gitlink from `42b1ee8` to `1397650`, whose tip is an ARCH-032 database change, unrelated to API-004. These changes are documented for visibility but are not blockers for this functionality-focused review: neither changes the API-004 service behavior, and the current required tests/build all pass. The task-specific `2731e2e` commit does not modify either path.

### Unresolved Issues

No unresolved functional issues were found in the reviewed behavior or required scenarios. The production service change is in baseline commit `2e6e736`, already on `main` and predating the Attempt 2 claim; the task-specific Attempt 2 commit contains validation/test corrections and coverage, not new production service behavior. The documented development-script and database-pointer changes remain contextual deviations and do not block the Passed functional review. Explicit developer completion remains pending.

## Developer Self-Review - Changes Requested (Attempt 2)

### Review Findings

- Fix the PostgreSQL test fixture for revocation by setting `revokedAt` when setting installation `status: REVOKED`, in accordance with `WooCommerceInstallation_status_revoked_at_check`; rerun the disposable PostgreSQL suite.
- Fix the `UNDELIVERABLE` coupon fixture so it satisfies `ck_arch016_discount_fixed_selectable` (for example, `fixedSelectable: false`); rerun the suite and confirm the test still verifies that unsafe/no-code rows are excluded from the merchant catalogue.
- Add a PostgreSQL test in which Background changes catalogue status while settings GET is being read, proving the persisted merchant mode/IDs and catalogue state remain stable and no writes occur. Add the required failed read-grant case; ensure the test uses disposable PostgreSQL.
- Resolve whether the database submodule gitlink and `start-dev.sh` changes belong to this task. Keep `start-dev.sh` out of the task scope unless explicitly authorized; document and justify any required schema gitlink dependency. Do not alter protected `main` history.
- Update checkboxes and the Completion Report from the passing rerun evidence. Then request another review; do not complete the task while required database coverage is failing or absent.

### State Transition

`status: ready`, `executor: null`, `claimed_at: null`, `attempt: 2`. The next developer claim increments to Attempt 3 exactly once.

### Review Scope

Attempt 2 reconciled and validated the existing commit `2e6e736ae8a2575733dc76344c6758413dc15d30`; no implementation files or API repository refs were changed in this review. That commit is already present on `main` and the matching task branch. The parent task record is the only artifact changed by this review.

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

Developer Self-Review Passed on 2026-10-16. Task is in `review` pending the developer's explicit completion decision.

## Developer Self-Review - Changes Requested (Attempt 2 Reconciliation, 2026-10-16)

### Review Findings

- The updated PostgreSQL fixtures and newly required concurrent-status and failed-read-grant tests pass. The unit suite, typecheck, lint, build and disposable PostgreSQL suite also pass; no current validation failure remains.
- Resolve the out-of-scope changes in baseline `2e6e736ae8a2575733dc76344c6758413dc15d30` before acceptance. `start-dev.sh` now pins a different public ngrok origin and removes the required `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` guards. The `database` gitlink advances from `42b1ee8` to `1397650`, whose commit is ARCH-032 database work unrelated to API-004. Obtain explicit architect/developer authorization for these changes or correct them on the task branch; do not rewrite protected `main` history.
- The production service change remains in baseline commit `2e6e736`, already on `main` before Attempt 2. The task-specific Attempt 2 commit is `2731e2eda7f2f954d5d6abd98e25eb0dedbfe0b4`; it repairs the fixtures, adds the missing database cases, and relocates tests/configuration. Keep this provenance clear in any later completion report.

### Validation Reviewed

- `npm --prefix /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004 test`: 344 tests, 302 passed, 0 failed, 42 skipped.
- `npm --prefix /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004 run test:arch036-discount-offers:postgres`: 7/7 passed; all 49 migrations applied to a disposable PostgreSQL database.
- `npm --prefix /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004 run typecheck`: passed.
- `npm --prefix /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004 run lint`: passed with zero warnings.
- `npm --prefix /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004 run build`: passed.
- `git diff --check origin/main...HEAD` in the implementation worktree: passed.

### Physical Worktree Evidence

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-036-API-004`, branch `task/ARCH-036-API-004`; clean before this report update and synchronized with `origin/task/ARCH-036-API-004` at the preceding parent review commit.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-004`, branch `task/ARCH-036-API-004`, clean at `2731e2eda7f2f954d5d6abd98e25eb0dedbfe0b4`, equal to `origin/task/ARCH-036-API-004`; one task-specific commit ahead of `origin/main`.
- No shared/default checkout was substituted or changed during this re-review. Neither task branch was merged to `main`.

### State Transition

`status: ready`, `executor: null`, `claimed_at: null`, `attempt: 2`. This re-review does not create Attempt 3; a later developer claim increments the attempt exactly once.

## Developer Self-Review Passed (Attempt 2, 2026-10-16)

### Review Outcome

This Passed functional review supersedes the earlier same-day Changes Requested outcome after the developer clarified that review should focus on behavior and passing verification. All functional acceptance criteria and required validation checks are supported by passing evidence recorded in the Completion Report. The earlier two PostgreSQL fixture failures were corrected, and the required Background-status concurrency and failed read-grant scenarios were added and passed against disposable PostgreSQL. No functional corrections remain.

The `start-dev.sh` and ARCH-032 database gitlink observations are retained as non-blocking deviations because they do not affect API-004 functionality. The production service baseline predates Attempt 2 and is already on `main`; the task-specific Attempt 2 commit contains the test fixes, added database coverage, and test-layout/configuration updates.

### State Transition

`status: review`, `executor: null`, `claimed_at: null`, `attempt: 2`. `completion_mode: developer`; explicit developer completion is pending. No task branch was merged to `main`.
