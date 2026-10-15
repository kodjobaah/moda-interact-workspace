---
id: ARCH-036-BACKGROUND-005
architecture_id: ARCH-036
title: Mirror identifiable Woo coupons without imposing Moda business eligibility
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-036-BACKGROUND-001"]
enables: []
created: 2026-10-15
updated: 2026-10-15
---

# ARCH-036-BACKGROUND-005 — Mirror identifiable Woo coupons; defer validity to WooCommerce

## Architecture

- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- This is a bounded follow-up to completed `ARCH-036-BACKGROUND-001`. It covers Woo catalogue mapping and the Woo branch of the existing recovery-policy offer snapshot, without reopening accepted dispatcher, lease, queue, credential or pagination designs.
- Owner: `moda_background`, repository `moda-interact-background`; coordinator: `moda_architect`.
- Materialised developer task. Attempt 1 was claimed on 2026-10-15 and returned to `ready` after developer self-review; attempt 1 is preserved.

## Observed defect

A Render Background scan for WooCommerce shop `cmv9kgh2b0000poammusu116y` completed successfully at `2026-10-15 13:21:18.624`, then a later run set `ShopifyDiscountCatalogue.status=ERROR` and `lastErrorCode=invalid_coupon` although previously valid coupons remained. `normalizeWooCoupons()` currently maps all items with throwing `normalizeWooCoupon()`; **one malformed individual item fails the entire otherwise complete catalogue**. API-002 consequently rejects catalogue GET with `catalogue_not_current`, hiding valid coupons.

## Objective

**WooCommerce determines coupon rules and redemption validity; Moda Interact synchronises coupon identities/codes and honours merchant configuration.** A coupon does not become `UNSUPPORTED`, hidden, deselected or un-sendable merely because Moda does not recognise its `discount_type`, its amount is zero or nonstandard, or its expiry/usage/product restrictions appear to make it ineligible. The merchant decides whether to select it; WooCommerce makes the final decision at redemption. A single malformed optional provider field must not move the complete catalogue to `ERROR`.

## Scope and invariants

- Own Woo-only mapping in `src/providers/woo-coupon-normalization.ts`, Woo catalogue reconciliation, and the Woo-specific branch of `src/services/recovery-policy.service.ts` (or focused extracted helper), plus their tests. Keep provider/business eligibility logic for **Shopify unchanged**; distinguish the provider using trusted shop/platform identity, not a guessed coupon title.
- Keep HTTPS/DNS-pinning, Woo REST grant checks, complete/bounded pagination, positive unique stable numeric provider IDs, claim/generation fencing, atomic writes and the two **verified complete absences** removal rule. Missing/invalid/duplicate IDs or incomplete scans fail the entire scan; ordinary per-coupon data oddities do not.
- Do not write `ShopifyDiscount.isAvailable` in any Woo provider sync path. It is the merchant's explicit selected/not-selected flag, not a provider eligibility field. Preserve FK/history and fixed selections.
- Do not store Woo customer PII, arbitrary metadata, email restrictions, `used_by` or full raw provider bodies. Preserve necessary provider fields in a safe, bounded snapshot while keeping the original `discount_type` for display/debugging.
- No database migration is expected: Prisma `singleRedeemCode` and `title` are `String`/TEXT. `providerType` is `VARCHAR(128)`: map arbitrarily long/unknown types to a stable **internal** storage-safe Woo marker (retaining the true type in the safe snapshot) rather than rejecting the coupon. Do not introduce an artificial 255-character coupon-code limit; examine and test real downstream serialization/transport bounds.
- No Shopify behaviour changes, new remote calls, scheduler/dispatcher modifications, CommerceAgent features or `docs/decisions/**/_index.md` changes.

## Required behaviour

1. **Provider identity first:** a complete, authentic Woo response with unique, positive, trustworthy coupon IDs is authoritative for which coupons exist. The catalogue can be `CURRENT` even with unknown types, unusual amounts, expired/exhausted conditions or optional fields Moda cannot interpret.
2. **Minimum useful projection:** map every identified Woo coupon with a usable redeem code to a persistent row (`woo:coupon:<id>`, method `CODE`, full stored code, stable internal `WooCoupon:` provider type). Do **not** require a type allowlist, amount greater than zero, percentage at most 100, future expiry, positive remaining usage, particular product/category restrictions or a code length chosen by Moda. `fixedSelectable`/`providerStatus` for Woo must represent **identifiable/code-usable/present**, not Moda's opinion of commercial eligibility.
3. **Optional data is descriptive:** capture amount, type, dates, limits and restrictions only when safely parseable; missing, unusual or malformed optional values should neither discard the coupon nor turn the whole catalogue `ERROR`. Unknown `discount_type` remains provider-defined, not `UNSUPPORTED` by Moda. Expiry/usage may be displayed as provider facts, but must not become selection or execution vetoes.
4. **Missing/unsafe code:** a trustworthy coupon ID can still be counted as **observed** if its code is missing/unusable for our outbound delivery. Preserve an existing row, selection and FK, and expose a technical delivery limitation without fabricating a code or applying arbitrary business rules. Do not pretend such a record is redeemable; if a new row cannot safely satisfy existing required fields, exclude it from *sendable* rows but keep its ID in removal bookkeeping. Other coupons still reconcile to `CURRENT`. Treat genuine transport/injection/serialization constraints as technical errors, not Woo validity rules.
5. **Removal semantics:** a malformed-but-observed ID is not missing, even across repeated successful scans. Mark `REMOVED` only after two consecutive **successful complete** scans confirm actual absence; do not reset merchant selection. Failed scans never count as misses. A later corrected coupon can become sendable without resetting its selection.
6. **Recovery runtime for Woo:** when mode FIXED is configured, do not suppress the merchant's selected, code-usable, previously observed Woo coupon because of `providerStatus=EXPIRED/EXHAUSTED/UNSUPPORTED`, `fixedSelectable` computed from commercial rules, date checks, discount type, amount or a temporary catalogue `ERROR` after a successful snapshot. Woo's checkout remains the redemption authority. Prevent use when no safely deliverable code exists, the coupon has been **confirmed REMOVED**, or the merchant has not selected it. Existing Shopify gates and security/tenant scoping must remain intact. Do not claim redemption succeeded because a code was sent. Check any already-integrated AI selection path for the same Woo-only assumptions; do not implement a new AI selection feature here.
7. **Atomicity and visibility:** after a trustworthy complete scan, upsert observed sendable coupons, account for ID-only observations and commit catalogue `CURRENT` atomically. Previously selected flags remain. If there are zero coupons, an authentic empty scan is still a successful catalogue.
8. **Diagnostics:** emit bounded structured per-item technical issue reasons and aggregate counts without leaking coupon codes, PII or raw Woo payloads. Distinguish `provider_identity_invalid`, `code_not_deliverable`, `optional_field_ignored` and actual transport/pagination failures from assertions about provider coupon validity.

## ASCII workflow

```text
Woo complete REST coupon scan
    |---- transport/auth/pagination failure ----> scan ERROR (no partial writes)
    v
Verify stable positive unique coupon IDs
    |---- missing/duplicate/ambiguous IDs ------> scan ERROR
    v
For EACH provider ID (no business-rule filter)
    |---- code usable --> persist full code, arbitrary type, optional metadata
    '-- code unusable --> retain observed ID; no invented redeem code
    v
Atomic reconcile / two verified absent scans / preserve isAvailable
    v
Catalogue CURRENT --> API lists merchant-configurable coupons
                          |
Merchant saves selected IDs (not provider validation)
                          |
Background Woo recovery: safe selected code --> merchant message
                                                 |
                                                 v
                                      WooCommerce validates redemption
```

## Acceptance criteria

- [ ] A complete scan containing standard coupons plus **unknown provider types, zero amounts, expired, exhausted and nonstandard limits** results in `CURRENT`; coupons with safe ID/code remain merchant-configurable without `UNSUPPORTED` eligibility vetoes.
- [ ] A Woo code **longer than 255 characters** round-trips storage and the API projection without truncation, unless an independently verified transport limitation exists; any genuine limitation has explicit error treatment and evidence.
- [ ] A complete scan with five normal coupons and one coupon with a trustworthy ID but malformed *optional* fields yields `CURRENT`, retains all safely sendable coupons, and never marks the observed malformed ID `REMOVED`.
- [ ] A no-code/unsafe-code item never causes the whole scan to fail and never produces an invented outbound code; any previously saved selection/FK survives, with a clear technical-delivery state.
- [ ] Missing/duplicate/ambiguous IDs, inconsistent pages, revoked grants and other untrustworthy scans still fail without partial writes or false-removal transitions.
- [ ] Two verified complete misses mark truly absent coupons REMOVED; transient failures, odd optional fields and malformed-but-observed rows do not.
- [ ] **Woo FIXED recovery snapshot** honours a merchant-selected, safely deliverable code even with unknown type, zero amount, expired/exhausted provider metadata or catalogue ERROR after an earlier complete successful scan; confirmed REMOVED/no code are handled safely. Existing **Shopify** runtime behaviour remains unchanged.
- [ ] No Background provider write to Woo `isAvailable` during success, retries, recovery from ERROR or failed scans.

## Required validation

- [ ] Normaliser unit tests for custom/unknown type (including long type), zero and nonstandard amount, expired/usage-exhausted, absent/malformed optional fields, >255-character code, no-code and duplicate/missing IDs.
- [ ] Disposable PostgreSQL integration for complete mixed scans, preserving selection, no false removal of identified coupons, two-miss confirmation, claim fencing, atomic rollback and `ERROR -> CURRENT` recovery.
- [ ] Woo-specific FIXED recovery-policy tests for selected-coupon snapshots with unusual provider attributes, missing code, known REMOVED and catalogue ERROR; **Shopify parity tests** explicitly prove unchanged filtering.
- [ ] Run existing ARCH-036 catalogue/dispatch PostgreSQL-Redis suites, unit tests, typecheck/build and `git diff --check`. Report exact commands/results and environmental blocks; do not claim live Render verification unless run.

## Stop condition

Submit a bounded Completion Report in `review` to `moda_architect`; do not trigger another task or modify `_index.md`.

## Completion Report

### Status

Changes Requested — Attempt 1 review found an unrelated database gitlink advance, a failing unsafe-code test case, incomplete required validation, and no verified downstream transport limit for long coupon codes. Attempt 1 is preserved; no new attempt has been claimed.

### Files Changed

The pushed implementation commit `9cda979c57275ee5211562094a63d74f7df2ae13` changes `src/providers/woo-coupon-normalization.ts`, `src/providers/woo-coupon-transport.ts`, `src/services/recovery-policy.service.ts`, `src/services/woo-coupon-catalogue.service.ts`, and four Woo unit/integration test files. It also advances the `database` submodule from the prepared commit `40674aea91527d5645aa922c9627af673b487223` to `12c3bee13cabeb3c8b9cb0ac602d836700702413`, outside this task's scope. No implementation changes were made during this review.

### Work Completed

The implementation changes Woo coupon normalization to retain identified coupons despite malformed optional attributes, adds bounded per-item diagnostics, tracks code-unavailable identities, preserves merchant selection during catalogue upsert, applies two-successful-miss removal, and relaxes the FIXED recovery snapshot for trusted Woo shops while retaining Shopify checks. The self-review did not accept the implementation; required corrections remain below.

### Validation Results

- `npx vitest run tests/unit/providers/woo-coupon-normalization.test.ts tests/unit/services/woo-coupon-catalogue.service.test.ts tests/unit/services/woo-recovery-offer-policy.test.ts`, from the canonical Background implementation worktree: 29 passed, 1 failed. The failing `unsafe redeem code` fixture contains the literal characters backslash and `n` (`"a\\nb"`) rather than a newline/control character, so it does not exercise the intended rejection.
- An initial focused-test attempt, `npm run lint`, and `npm run build` were run from the unrelated MCP-020 worktree. Those results do not validate this task and are not counted.
- `git diff --check origin/main...HEAD` on the implementation branch and `git diff --check` on this parent task record passed.
- The PostgreSQL catalogue reconciliation and dispatch integration suites, full unit suite, Background lint/build/typecheck, and downstream code-length delivery-boundary validation were not run during this review.

### Deviations

The implementation branch contains an unrelated `database` gitlink advance from prepared commit `40674aea91527d5645aa922c9627af673b487223` to `12c3bee13cabeb3c8b9cb0ac602d836700702413`. The implementation commit is already pushed. Do not rewrite published history or modify the Database repository; correct the pointer in a new task-branch commit.

### Unresolved Issues

The field(s) behind the live `invalid_coupon` have not been independently identified; preserve this as a diagnostic gap, not a basis for rejecting whole catalogues. The real downstream serialization/transport limit for long coupon codes also remains unverified.

### Launcher Preparation Evidence

- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-036-BACKGROUND-005`, branch `task/ARCH-036-BACKGROUND-005`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-BACKGROUND-005`, branch `task/ARCH-036-BACKGROUND-005`.
- Attempt 1 was claimed by the launcher as `developer` at `2026-10-15T17:15:43Z`; parent claim commit `9ff04ffd665512d29fc638cf5bd7fa75c48c7ca5` was committed and pushed.
- Dependency gate passed: `ARCH-036-BACKGROUND-001` was complete. Both task worktrees were created and current with `origin/main`; no remote task-branch fast-forward was needed.
- Recursive submodule sync and initialization passed. The prepared `database` submodule commit was `40674aea91527d5645aa922c9627af673b487223`; the implementation branch now points to `12c3bee13cabeb3c8b9cb0ac602d836700702413` as disclosed above.
- Implementation task branch commit `9cda979c57275ee5211562094a63d74f7df2ae13` is pushed and in sync with its remote. Both implementation and parent worktrees were clean before this parent report update.

## Architect Review

### Review Status

Pending implementation evidence.

## Developer Self-Review - Changes Requested

### Review Outcome

Attempt 1 is not accepted. The implementation commit is pushed and the implementation worktree is clean, but the focused unit suite has one failing test, required repository/integration validation is incomplete, long-code delivery limits were not verified, and the implementation branch contains an out-of-scope Database gitlink advance.

### Required Corrections

- Correct `tests/unit/services/woo-recovery-offer-policy.test.ts` so the unsafe-code fixture contains an actual control character (for example, an actual newline), then rerun the same focused three-file unit command and confirm it passes.
- Restore the `database` gitlink on the Background implementation task branch to prepared baseline `40674aea91527d5645aa922c9627af673b487223` in a new commit. Do not edit the Database repository and do not rewrite the already-pushed `9cda979` commit.
- Trace the real recovery-message serialization and delivery path for codes longer than 255 characters, identify any concrete transport ceiling, and add a test at that boundary. The existing normalizer test proves only normalization/storage projection, not successful downstream delivery.
- Run from the canonical Background implementation worktree: `npm run test:arch036-woo-coupon-catalogue:postgres`, `npm run test:arch036-woo-coupon-dispatch:postgres`, `npm test`, `npm run lint`, `npm run build` (including Prisma generation/TypeScript compilation), and `git diff --check`. Record exact outcomes and environmental blocks; do not claim live Render verification.
- Preserve the corrected materialised/claimed lifecycle description in the task definition and update the remaining report sections as the attempt progresses.

### Attempt State

Returned to `ready`; `executor` and `claimed_at` are cleared. Attempt remains 1. The implementation branch and Database repository were not modified during this review.
