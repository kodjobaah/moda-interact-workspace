---
id: ARCH-052-SHOPIFY-001
architecture_id: ARCH-052
title: Make Shopify merchant discount selection match WooCommerce checkboxes
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-052-BACKGROUND-009
enables:
- ARCH-052-SYSTEM-TEST-001
created: '2026-10-29'
updated: 2026-10-30
---

# ARCH-052-SHOPIFY-001: Make Shopify merchant discount selection match WooCommerce checkboxes

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Replace the Shopify one-radio FIXED discount UI with 0..50 merchant-selected discounts persisted as `ShopifyDiscount.isAvailable` under one locked transaction.

## Context

Shopify `RecoverySettingsView.tsx` has one `fixedShopifyDiscountId` radio control; `recovery-policy.server.ts` previously used that anchor as full authority. Woo has an established atomic multi-select save using the same discount table. BG009 first stops Shopify sync changing the selection flag.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- In `app/routes/app/recovery-settings/RecoverySettingsView.tsx` replace single radio with accessible checkbox list; show selected state from `ShopifyDiscount.isAvailable` for the same shop, independent of provider status. Keep NONE/FIXED/AI mode chooser, notify checkbox and existing language/translation. Permit at most 50 choices, show selected count and prevent silent trimming.
- Change `app/routes/app/settings-save/route.ts` to accept exactly one JSON string field `selectedDiscountIds` when intent=`recovery`, parsed as array with an app-owned strict array validator: 0..50 unique, nonempty string IDs, deterministic ASCII sort; reject malformed/duplicate/oversized input; remove acceptance of `fixedShopifyDiscountId` as merchant-submitted authority. Reject unknown fields/duplicate form entries, malformed JSON and payload >8192 bytes (400); >50 selections (422); FIXED with empty set (422).
- In `app/services/recovery-policy/recovery-policy.server.ts`, use one `client.$transaction` and existing `lockSettingsShop(tx, shopId)`; check `settings.updatedAt` against submitted revision **before writes**; if mismatch return 409, not partial save. Validate every selected ID references an existing discount row for that exact Shopify `shopId`, regardless of provider catalogue CURRENT/ERROR status or current checkout eligibility. Allow retaining previously selected but currently unavailable discounts as dormant selections; Background excludes them from sendable offers until independently re-verified.
- Inside the same transaction: `shopifyDiscount.updateMany({where:{shopId,isAvailable:true},data:{isAvailable:false}})` then `shopifyDiscount.updateMany({where:{shopId,id:{in:sortedIds}},data:{isAvailable:true}})` and assert affected count equals requested IDs; update ShopSettings `recoveryOfferMode`, existing timing/notification prefs, and `fixedShopifyDiscountId` to `sortedIds[0]` iff FIXED, otherwise null. Never write availability/providerStatus/unavailableAt.
- Return selected IDs and effective source in settings loader, maintain Admin override as independent effective policy (never merge merchant options), and use provider status/time/generation rather than isAvailable to display catalogue availability.
- Write tests proving two shops cannot change one another, re-saves are idempotent, concurrent stale revision 409, NEW sync items remain unchecked, NONE/AI preserve dormant flags, and unavailable formerly selected discount can be deselected.

## Out of Scope

- No DB model/table/column changes, no provider coupon mutations, no template/Background send code, no legacy single-radio compatibility.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Do not trust browser discount IDs; read and verify ownership/valid catalogue identity inside the transaction.
- No partial persistence after a stale revision or expired/out-of-scope merchant session.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

### Work Items

- [x] Implement checkbox form and strictly validated selected-ID request.
- [x] Implement atomic selected-flag replacement under Shop lock and revision compare.
- [x] Add UI and service tests, including a real PostgreSQL integration test definition and override-independent view. The disposable PostgreSQL test itself could not execute because no working container runtime was available.

## Interfaces / Contracts

- Form `intent=recovery`, `selectedDiscountIds` JSON array, `recoveryOfferMode`, existing other settings and revision; exactly one selection authority `ShopifyDiscount.isAvailable`.
- Existing `fixedShopifyDiscountId` remains deterministic first-sorted anchor solely to satisfy existing effective-policy schema; never treat as full selected set.

## Dependencies

- `ARCH-052-BACKGROUND-009` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-SYSTEM-TEST-001`

### Acceptance Criteria

- [x] Shopify and Woo both persist multiple selection flags using the same existing model; new Shopify discounts remain unchecked by default.
- [x] Modes NONE/AI preserve selected flags; the FIXED mode uses the saved set while provider availability is displayed separately.
- [x] Selection writes validate shop ownership and revision before mutation; no provider eligibility is inferred from merchant selection.

## Validation

- [ ] Shopify settings route/service unit tests and real PostgreSQL transaction tests, including sync race.
- [ ] Shopify declared typecheck/build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact/app/routes/app/recovery-settings/RecoverySettingsView.tsx`
- `moda-interact/app/routes/app/settings-save/route.ts`
- `moda-interact/app/services/recovery-policy/recovery-policy.server.ts`
- `moda-interact/tests/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Ready for Architect Review — Attempt 1. The implementation and parent report are being submitted on the mirrored `task/ARCH-052-SHOPIFY-001` branches. The disposable PostgreSQL integration remains unexecuted because Testcontainers could not find a working container runtime.

### Files Changed

- `app/routes/app/recovery-settings/RecoverySettingsView.tsx` and `RecoverySettingsRoute.css` — accessible multi-select checkboxes, selected count/limit behavior, provider availability separated from merchant selection.
- `app/routes/app/settings-save/route.ts` — strict `selectedDiscountIds` recovery form parsing and bounded validation.
- `app/services/recovery-policy/recovery-policy.server.ts` — locked transactional revision/tenant validation and selected-flag replacement.
- `app/i18n/locales/*.json` — translated multi-select labels and validation messages in the existing supported locales.
- `tests/unit/recovery-settings-discounts.test.tsx`, recovery policy/settings route tests, and `tests/integration/shopify-recovery-discounts.postgres.integration.test.ts` — UI, service, route and PostgreSQL regression coverage.
- `tests/integration/merchant-feature-preferences.test.ts` and `tests/unit/recovery-settings-i18n.test.ts` — updated integration fixture and locale coverage.

### Work Completed

Replaced the single FIXED discount radio selection with a shop-scoped checkbox list backed by `ShopifyDiscount.isAvailable`. The UI shows the selected count, refuses additional selections after 50 instead of trimming, preserves NONE/FIXED/AI mode controls and translations, and renders provider catalogue availability independently from the merchant-selected flag. The loader exposes the selected set and effective source while preserving the Admin override as an independent policy.

The recovery save route accepts one strict JSON `selectedDiscountIds` value, enforces request-size, duplicate, malformed and count bounds, and no longer trusts `fixedShopifyDiscountId` as the submitted selection authority. The service uses the existing shop lock and a single transaction, compares the settings revision before writes, verifies every ID belongs to the exact shop, replaces selected flags atomically, and updates the deterministic FIXED anchor without changing provider availability fields.

### Validation Results

- Focused Shopify recovery settings, route and policy tests — passed (35 tests reported by the implementation agent).
- Declared TypeScript typecheck — passed.
- Declared lint — passed.
- Declared build — passed.
- `git diff --check` — passed.
- `tests/integration/shopify-recovery-discounts.postgres.integration.test.ts` — not run: Testcontainers reported `Could not find a working container runtime strategy`. The real PostgreSQL transaction/race behavior therefore remains unverified in this attempt; no database test pass is claimed.

### Deviations

The disposable PostgreSQL integration could not run because the environment has no working container runtime. The integration test was added, but its assertions are not treated as executed evidence.

### Assumptions

The existing application-level test harness and declared build/typecheck/lint commands are authoritative; no database schema or migration change is needed for this task.

### Unresolved Issues

The isolated PostgreSQL transaction/race test must be run in an environment with a supported container runtime before integrated system certification.

### Architectural Concerns

No cross-repository or schema ownership gap was identified. Architect review should account for the unexecuted PostgreSQL integration test.

### Prepared Worktree Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHOPIFY-001`, branch `task/ARCH-052-SHOPIFY-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHOPIFY-001`, branch `task/ARCH-052-SHOPIFY-001`.
- Launcher claim commit: `4b139457157076f2c9f1d3db853a4b6815b4930f`; dependency gate passed for `ARCH-052-BACKGROUND-009`.
- Parent and implementation worktrees were newly created from current `origin/main`; recursive submodule sync/init passed. The database submodule was initialized at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- No shared checkout, other task worktree, parent submodule gitlink or `main` branch was modified.


## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

1. **Enforce the 8,192-byte limit on the complete request body.** The route calls `request.formData()` before applying a size check, then measures only the UTF-8 size of the `selectedDiscountIds` value. This does not meet the task requirement to reject payloads over 8,192 bytes: oversized values in other form fields or overall form encoding can pass that check, and the body is already parsed. Add a total-body byte limit that is enforced before unbounded form parsing, including when `Content-Length` is absent or inaccurate. Preserve the existing 400 response for an oversized request and add regression coverage for the full-body limit.

2. **Execute the PostgreSQL transaction/race integration test.** The required test was added but not run because Testcontainers could not find a working container runtime. The task specifically requires real PostgreSQL verification of tenant isolation, atomic replacement, idempotence, dormant selections, and stale concurrent revisions. Run the test in an environment with a supported PostgreSQL/container runtime and record the actual result; do not treat the added-but-skipped test as validation evidence.

### Reviewed Files

- `moda-interact/app/routes/app/settings-save/route.ts`
- `moda-interact/app/services/recovery-policy/recovery-policy.server.ts`
- `moda-interact/app/routes/app/recovery-settings/RecoverySettingsView.tsx`
- `moda-interact/tests/integration/shopify-recovery-discounts.postgres.integration.test.ts`
- This task's Completion Report and VCS evidence.

### Validation Reviewed

Reviewed the submitted report: 35 focused tests, typecheck, lint, build and `git diff --check` are reported as passing. The PostgreSQL integration test is explicitly reported as not run. These implementation validations were not rerun during architect review; `git diff --check` passed for this review-record edit.

### Architecture Conformance

Changes Requested. The multi-selection transaction, tenant-scoped ID verification, merchant selection semantics, and reported task-worktree isolation otherwise conform. The full request-size contract is not enforced, and the required database concurrency behavior remains unverified.

### Follow-up

Return the same task to `ready` for Attempt 2. Preserve Attempt 1 history. Once both corrections and required validation are complete, resubmit for architect review. Do not promote ARCH-052-SYSTEM-TEST-001 until this task is accepted and its dependencies are complete.
