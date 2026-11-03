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
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 3
depends_on:
- ARCH-052-BACKGROUND-009
enables:
- ARCH-052-SYSTEM-TEST-001
created: '2026-10-29'
updated: 2026-10-31
---

# ARCH-052-SHOPIFY-001: Make Shopify merchant discount selection match WooCommerce checkboxes

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This task was materialised and executed through the canonical launcher-resolved parent and implementation task worktrees; Attempt 3 evidence is recorded below.

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
- [x] Add UI and service tests, including a real PostgreSQL integration test definition and override-independent view. Attempt 1 could not execute the disposable PostgreSQL test because no working container runtime was available; Attempts 2 and 3 ran it successfully with Colima.

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

- [x] Shopify settings route/service unit tests and real PostgreSQL transaction tests, including sync race.
- [x] Shopify declared typecheck/build/lint and `git diff --check`.

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

Ready for Architect Review — Attempt 2. Both Changes Requested items from Attempt 1 have been addressed: the complete request body is bounded before form parsing, and the PostgreSQL transaction/race integration test passed against a disposable database.

### Files Changed

- Attempt 2 changed `app/routes/app/settings-save/route.ts` and `tests/unit/settings-save-recovery-route.test.ts` to enforce and verify the total request-body byte limit.
- `app/routes/app/recovery-settings/RecoverySettingsView.tsx` and `RecoverySettingsRoute.css` — accessible multi-select checkboxes, selected count/limit behavior, provider availability separated from merchant selection.
- `app/routes/app/settings-save/route.ts` — strict `selectedDiscountIds` recovery form parsing and bounded validation.
- `app/services/recovery-policy/recovery-policy.server.ts` — locked transactional revision/tenant validation and selected-flag replacement.
- `app/i18n/locales/*.json` — translated multi-select labels and validation messages in the existing supported locales.
- `tests/unit/recovery-settings-discounts.test.tsx`, recovery policy/settings route tests, and `tests/integration/shopify-recovery-discounts.postgres.integration.test.ts` — UI, service, route and PostgreSQL regression coverage.
- `tests/integration/merchant-feature-preferences.test.ts` and `tests/unit/recovery-settings-i18n.test.ts` — updated integration fixture and locale coverage.

### Work Completed

Replaced the single FIXED discount radio selection with a shop-scoped checkbox list backed by `ShopifyDiscount.isAvailable`. The UI shows the selected count, refuses additional selections after 50 instead of trimming, preserves NONE/FIXED/AI mode controls and translations, and renders provider catalogue availability independently from the merchant-selected flag. The loader exposes the selected set and effective source while preserving the Admin override as an independent policy.

The recovery save route accepts one strict JSON `selectedDiscountIds` value, enforces request-size, duplicate, malformed and count bounds, and no longer trusts `fixedShopifyDiscountId` as the submitted selection authority. The service uses the existing shop lock and a single transaction, compares the settings revision before writes, verifies every ID belongs to the exact shop, replaces selected flags atomically, and updates the deterministic FIXED anchor without changing provider availability fields.

For Attempt 2, the route now counts bytes from the request body stream and rejects a body larger than 8,192 bytes before calling `request.formData()`. The limit applies when `Content-Length` is absent or inaccurate. Regression coverage confirms an otherwise valid recovery form receives HTTP 400 when the complete encoded body exceeds the limit.

### Validation Results

- Focused route and recovery-policy unit tests — passed (33 tests across four files); strengthened settings-save route test rerun — passed (18 tests).
- `tests/integration/shopify-recovery-discounts.postgres.integration.test.ts` — passed (3 tests): shop isolation; atomic replacement/idempotence including dormant and new discounts; stale concurrent revision rejected without partial writes. Testcontainers used the available Colima Docker endpoint with Ryuk disabled; the test stopped its database container after completion.
- Declared TypeScript typecheck — passed.
- Declared lint — passed.
- Declared build — passed.
- `git diff --check` — passed.

### Deviations

No scope deviations. The PostgreSQL test initially lacked a detected container runtime; it was subsequently run successfully using the available Colima Docker endpoint.

### Assumptions

The existing application-level test harness and declared build/typecheck/lint commands are authoritative; no database schema or migration change is needed for this task.

### Unresolved Issues

None for this task. Downstream system validation remains governed by its own task and dependency gates.

### Architectural Concerns

No cross-repository or schema ownership gap was identified. Both Attempt 1 review corrections are addressed; architect review should verify the body-stream limit and the recorded PostgreSQL evidence.

### Prepared Worktree Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHOPIFY-001`, branch `task/ARCH-052-SHOPIFY-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHOPIFY-001`, branch `task/ARCH-052-SHOPIFY-001`.
- Attempt 2 launcher claim commit: `8a9c71c782fd389e83dd0722ccfc1bccf176dda6`; dependency gate passed for `ARCH-052-BACKGROUND-009`.
- Attempt 2 reused the dedicated parent and implementation worktrees. Parent remote fast-forward: not needed; `origin/main` incorporated: yes. Implementation remote fast-forward: not needed; `origin/main` incorporated: already current.
- Recursive implementation submodule sync and update/init passed. The database submodule was initialized at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- Implementation task branch final commit: `b1c5ce3b892ed85385a82e7b7a89a66a04f28c2f`. Parent report is being submitted separately on the mirrored task branch.
- No shared checkout, another task worktree, parent submodule gitlink or `main` branch was modified.

### Attempt 3 Completion Report

#### Status

Ready for Architect Review — Attempt 3. The Attempt 2 Changes Requested item is addressed with deterministic PostgreSQL evidence that interleaves merchant selection writes and catalogue upserts.

#### Files Changed

- `tests/integration/shopify-recovery-discounts.postgres.integration.test.ts` — removed the pre-seeded new-discount assumption, added deterministic transaction interleaving with production-equivalent catalogue upsert payloads, and kept the stale-revision race independent of prior test state.

#### Work Completed

The assigned `moda-interact` repository contains the recovery selection save transaction but not the Shopify discount-row catalogue sync implementation. The actual row upsert is owned by `moda-interact-background/src/services/shopify-discount-catalogue.service.ts`; invoking that service here would cross the assigned repository boundary and require its separate worker runtime/database package. No cross-repository files, provider calls, or database/schema changes were made.

The PostgreSQL test therefore exercises the real `saveMerchantRecoveryPolicy` service and, deterministically after its second selection `updateMany` (while the same PostgreSQL transaction remains open), runs the production sync upsert's create/update data semantics against that transaction. The new discount does not exist before the test. The upsert creates it with `isAvailable: false`; for an existing selected discount it updates catalogue fields while omitting `isAvailable`. Assertions after transaction completion prove the selected row remains selected and the newly synchronized row is unchecked. This is an interleaved transaction arrangement, not a timing-based sleep.

A negative-control run temporarily added `isAvailable: false` to the upsert update payload. The new PostgreSQL case failed at the selected-row assertion (`expected true, received false`); the mutation was removed, and the same focused case passed. This demonstrates that the test detects the overwrite regression rather than merely observing preinserted state.

#### Validation Results

- PostgreSQL integration file using Testcontainers, Colima socket `$HOME/.colima/default/docker.sock`, and `TESTCONTAINERS_RYUK_DISABLED=true` — passed, 4/4 tests. The final full-file rerun passed after the negative-control mutation was removed.
- Negative control with catalogue update overwriting `isAvailable` — failed as expected on the selected-row assertion; production-equivalent update semantics restored and focused case passed, 1/1.
- Focused recovery-policy and discount-lifecycle unit tests — passed, 18/18.
- `npm run typecheck` — passed.
- Focused ESLint on the changed integration test — passed.
- `git diff --check` — passed.
- Full build and repository-wide lint were not rerun in Attempt 3 because this attempt changed only the PostgreSQL test; Attempt 2 recorded both as passing. No Attempt 3 result is claimed for those commands.

#### Deviations and Unresolved Issues

The production catalogue sync function cannot be directly invoked from the assigned repository because it is owned by `moda-interact-background`. The test uses equivalent PostgreSQL Prisma upsert semantics with the production create/update field behavior, and the negative control proves the requested regression sensitivity. This ownership boundary and test design are provided for Architect Review. No other deviations or unresolved implementation issues.

#### Attempt 3 VCS Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHOPIFY-001`, branch `task/ARCH-052-SHOPIFY-001`; claim commit `7213f4f53400a8838779ab43c39e86610810a73c`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHOPIFY-001`, branch `task/ARCH-052-SHOPIFY-001`.
- Implementation commit: `270e5dda914d9e4ec42c55812bf1c4485f138cee` (`test(shopify): cover catalogue sync interleaved with selection`), pushed to `origin/task/ARCH-052-SHOPIFY-001`.
- Recursive database submodule remained at `af77c594ecbfc78c26d01c0021a090830884bbff`; no parent submodule gitlink was staged.
- Only the task-owned implementation test and this task report were changed. No other task branch or `main` was changed.


## Architect Review

### Review Status

Accepted — Attempt 3.

### Review History

- **Attempt 1 — Changes Requested:** the complete 8,192-byte request-body limit was not enforced, and the PostgreSQL transaction/race test had not run. Attempt 2 addresses the full-body limit before form parsing (including missing or inaccurate `Content-Length`) and reports a successful three-test PostgreSQL run.
- **Attempt 2 — Changes Requested:** the PostgreSQL test pre-seeded the new discount and did not exercise catalogue upsert behavior during the selection transaction. Attempt 3 adds deterministic interleaving and evidence for the production upsert semantics.
- **Attempt 3 — Accepted:** the real PostgreSQL integration test passes with a new row created unchecked and an existing selected row preserved through catalogue upserts in the same transaction. The canonical worktree and commit histories support the reported isolated execution.

### Attempt 2 Review Notes

The required catalogue-sync race case remains unverified. In `tests/integration/shopify-recovery-discounts.postgres.integration.test.ts`, `discountNew` is inserted as unchecked in `createShop()` before the save, then the save test asserts it remains unchecked. This does not execute a catalogue synchronization or exercise synchronization interleaved with the merchant selection transaction. The task's Validation explicitly requires real PostgreSQL transaction tests “including sync race,” and its Work Items require proving new sync items remain unchecked.

For Attempt 3, add a PostgreSQL integration case that exercises the catalogue upsert behavior against the selection save in a deterministic concurrent/interleaved scenario. Assert that an already selected discount remains selected and a newly synchronized discount is unchecked after both operations complete. Keep source changes within this task's assigned repository; if the actual sync operation cannot be exercised from this repository, document the boundary and provide equivalent integration evidence that validates the production upsert semantics. Run the new test and record the actual result.

### Attempt 2 Reviewed Files

- `moda-interact/app/routes/app/settings-save/route.ts`
- `moda-interact/app/services/recovery-policy/recovery-policy.server.ts`
- `moda-interact/app/routes/app/recovery-settings/RecoverySettingsView.tsx`
- `moda-interact/tests/integration/shopify-recovery-discounts.postgres.integration.test.ts`
- `moda-interact/tests/unit/settings-save-recovery-route.test.ts`
- This task's Attempt 2 Completion Report and VCS evidence.

### Attempt 2 Validation Reviewed

Attempt 2 reports 33 focused unit tests across four files, a separate 18-test route rerun, three PostgreSQL integration tests, typecheck, lint, build, and `git diff --check` passing. Source inspection confirms the full request stream is capped at 8,192 bytes before `formData()` parsing, and the route tests cover absent and inaccurate `Content-Length`. The PostgreSQL suite covers tenant isolation, atomic replacement/idempotence, dormant selections, and stale concurrent revisions, but does not run catalogue sync. These implementation validations were not rerun during architect review; `git diff --check` passed for this review-record edit.

### Attempt 2 Architecture Conformance

Changes Requested. Attempt 2 resolves both Attempt 1 findings, and the selection UI, tenant-scoped transactional save, request-size limit, and reported worktree evidence otherwise conform. The required sync-race validation is still absent.

### Attempt 2 Follow-up

Return the same task to `ready` for Attempt 3. Preserve the Attempt 1 and Attempt 2 history. Do not promote ARCH-052-SYSTEM-TEST-001 until this task is accepted and its other dependencies are complete.

### Attempt 3 Review

#### Review Notes

The requested sync-race evidence is present in the implementation, not only in the report. The integration case begins with no `discountNew` row, calls the real `saveMerchantRecoveryPolicy`, and interleaves the catalogue upserts after the service's second selection `updateMany` while the same PostgreSQL transaction remains open. After commit, it asserts the pre-existing selected row remains selected and the newly created catalogue row is unchecked.

The test's upsert create/update fields match the production behavior in `moda-interact-background/src/services/shopify-discount-catalogue.service.ts`: new rows set `isAvailable: false`; updates omit `isAvailable`, while refreshing provider/catalogue metadata. This is the equivalent integration evidence explicitly allowed by the Attempt 2 correction because the actual sync service is owned by Background. The reported negative control that adds `isAvailable: false` to the update payload fails on the selected-row assertion, demonstrating regression sensitivity. No cross-repository implementation changes were made.

Attempt 3 startup evidence is independently consistent with the canonical task histories: the parent claim commit `7213f4f53400a8838779ab43c39e86610810a73c` is on the dedicated parent worktree and follows the prior review state; the implementation commit `270e5dda914d9e4ec42c55812bf1c4485f138cee` follows the prior task tip `b1c5ce3b892ed85385a82e7b7a89a66a04f28c2f` and descends from implementation `origin/main`. The parent task worktree had incorporated its then-current mainline before the claim; the later `origin/main` update postdates the Attempt 3 submission. Both canonical worktree paths and matching task branches were verified. Recursive submodule status is clean and the database submodule is at the recorded gitlink `af77c594ecbfc78c26d01c0021a090830884bbff`.

#### Reviewed Files

- `tests/integration/shopify-recovery-discounts.postgres.integration.test.ts` at implementation commit `270e5dda914d9e4ec42c55812bf1c4485f138cee`.
- `app/services/recovery-policy/recovery-policy.server.ts`.
- Background production sync source `src/services/shopify-discount-catalogue.service.ts`.
- Attempt 3 Completion Report, claim and submission commits, and both canonical task worktrees.

#### Validation Reviewed

- Reran `MODA_DISPOSABLE_INTEGRATION=1 DOCKER_HOST=unix://$HOME/.colima/default/docker.sock TESTCONTAINERS_RYUK_DISABLED=true npm test -- tests/integration/shopify-recovery-discounts.postgres.integration.test.ts` from the implementation worktree: **4/4 tests passed**.
- Reviewed Attempt 3 report for focused unit tests (18/18), typecheck, focused ESLint and `git diff --check`; these passed as reported. Build and repository-wide lint were not rerun because Attempt 3 changed only the integration test; Attempt 2 records them passing.
- Verified the Attempt 3 implementation commit is pushed to `origin/task/ARCH-052-SHOPIFY-001`, the parent submission commit is present on the parent task branch, and the recursive database submodule matches its gitlink. No main branch was changed.

#### Architecture Conformance

Accepted. The implementation satisfies the Attempt 2 correction without crossing repository ownership, and remains within the task's scope and validation contract.

#### Follow-up

Mark `ARCH-052-SHOPIFY-001` Complete and reconcile its domain index and the ARCH-052 execution table. `ARCH-052-SYSTEM-TEST-001` remains Pending because its other implementation and publication dependencies are incomplete; do not promote it from this acceptance alone.
