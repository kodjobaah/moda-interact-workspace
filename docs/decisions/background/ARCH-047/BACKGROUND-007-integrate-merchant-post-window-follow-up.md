---
id: ARCH-047-BACKGROUND-007
architecture_id: ARCH-047
title: Integrate merchant post-window recovery follow-up templates
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-26T12:11:19Z
attempt: 1
depends_on:
  - ARCH-047-BACKGROUND-001
  - ARCH-047-BACKGROUND-004
  - ARCH-047-BACKGROUND-006
enables: []
created: 2026-10-24
updated: 2026-10-26
---

# Integrate merchant post-window recovery follow-up templates

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

**Architectural handoff clarified — 26 October 2026 (documentation only):** This task originated as a portable definition but was subsequently materialised and claimed as developer Attempt 1, as recorded in the unchanged YAML and Completion Report below. The ARCH-047 parent architecture and completed BACKGROUND-001 have a documentation-only reconciliation covering the final ownership boundary:

- **Admin** exclusively authors and validates the AST, reconstructs accepted translations, and persists compiled Meta components plus frozen positional parameter bindings.
- **BACKGROUND-001** consumes those compiled database snapshots, resolves trusted runtime values, and returns a `PreparedRecoveryTemplate` or typed unavailable result. It does not parse, reconstruct, authoring-validate or compile the Admin AST.
- **BG007** integrates that prepared result and the completed BG006 late admission/final-send adapter into the merchant post-window recovery path. It does not duplicate template compilation, selection, parameter binding or provider-status reconciliation.
- The completed ARCH-047 Shared package covers the **Meta template-status BullMQ v2 event** used by Messaging/BG003. There is **no Shared AST package**, no BG007 Shared-AST publication dependency and no requirement to introduce one.

**Before resuming this existing developer claim**, verify that the parent-architecture/BG001 documentation reconciliation has been applied in the canonical task baseline and that BG001, BG004 and BG006 remain `complete`. This documentation correction neither resets the claim nor constitutes BG007 feature implementation or validation.

## Objective

Reuse the approved follow-up template preparer and BG006 final fence in the merchant post-window sequence-two path, without changing ordinary human replies.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Update only the **post-24-hour** Meta template branch of `recovery-conversation/human-command-dispatcher.service.ts` and its narrow command-evaluation/selection adapters to use BG001 prepared follow-up and BG004 verified offer decision where required.
- Reuse BG006's late DB template-admission check and established human recovery claim, reserve/send/compensate pipeline. Keep merchant authentication/authorization in the existing API/Shopify/Woo boundaries; Background rechecks tenant/recipient/recovery claims.

## Out of Scope

- No free-text in-window AI/human wrapper work (BG008/009), no Meta authoring/editing/importing, no new merchant inbox/roles or parallel credit provider.
- Do not change the permitted one-follow-up-after-window policy, send timing semantics or existing human command retries just to accommodate templates.

## Requirements

**R1 — Correct branch.** If the rolling 24-hour customer-service window is open, preserve existing permitted ordinary human free-text handling (subsequently wrapped by BG009). If closed, only the existing eligible **sequence-two** recovery follow-up may use a Meta-approved Follow-up template; never send a free-text wrapper outside the window.

**R2 — Trusted preparation.** Resolve an approved Follow-up purpose/offer using BG004/BG001 with the **same shop/WABA/recipient/conversation checkout** and language as the stored merchant command. A merchant-selected template identifier must be re-resolved against current permitted assignments, not trusted as arbitrary Meta name or injected parameter list.

**R3 — Idempotency and audit.** One sequence-two claim per recovery, no duplicate sends from retries/double-clicks, do not consume another conversation/credit on refusal; persist provider and moderation evidence through existing mechanisms. Preserve authorised merchant identity, source and command audit.

**R3a — Prepared components in merchant follow-up.** Consume the same BG001-produced ordered text bindings, checkout CTA button parameter and optional separately typed READY image header as BG006. Preserve the already-compiled component shape; never fetch ShopBrand originals, process images, append a checkout URL a second time or permit unverified merchant-supplied image/header overrides. If a required brand/media/checkout binding is unavailable, return a normal typed human-command no-send result without consuming sequence two or a credit.

**R4 — Final gate. Use the **same BG006** late template recheck/final admission adapter; respect STOP, consent, moderation, entitlement, credit compensation and terminal recovery/order checks. Do not add another final fence or metadata GET.

**R5 — Failure.** No matching Follow-up template, stale consent, unavailable offer, revoked Meta registration or closed policy is a typed no-send/error communicated through existing human-command result, never fallback to unauthorised Meta template or free text.

**R6 — Merchant admission contracts remain owned by their service.** The current Shopify server action (`moda-interact/app/services/recoveries/recovery-human-commands.server.ts`) and Woo hosted API admission (`moda-interact-api/src/merchant/conversations/messages/admission.service.ts`) still permit the legacy `purpose: "checkout-recovery"`. Their merchant-facing eligibility, selectable Follow-up catalogue and request validation must be corrected by their owning Shopify/API/Woo tasks. BG007 receives a durable authenticated merchant command; it MUST independently re-resolve the chosen name/language or variant identity against the current shop/WABA, appropriate `FOLLOW_UP_*` purpose, verified offer decision and approved Moda-authored assignment before any provider admission. Never trust caller-supplied `templateParameters` as verified discounts, brand text, checkout URL or image-header values. If the merchant's requested variant conflicts with the BG001-prepared eligible variant, return a typed `template_not_allowed`/`follow_up_unavailable` and cancel/release the unconsumed sequence-two claim safely. BG007 is not authorised to modify Shopify, API or Woo plugin code.

**R7 — Remove obsolete human-path Meta verification.** Replace the existing `recovery-conversation/human-command-dispatcher.service.ts` live Meta `templateCategories.verify()` preflight and legacy body-parameters-only assembly with BG001's complete provider-ready components and the BG006 late database status fence. After both automated and human production callers have migrated, remove `whatsapp-template-selector.service.ts` and `whatsapp-template-category.service.ts` and related service registrations **only if** an import/reference audit proves no other live consumers remain. Do not remove the independent consent, authoritative STOP, moderation, final-send admission or credit safeguards. Replace old category-specific tests with fail-closed registration/late-admission tests.

## Work Items

- [x] Update only the **post-24-hour** Meta template branch of `recovery-conversation/human-command-dispatcher.service.ts` and its narrow command-evaluation/selection adapters to use BG001 prepared follow-up and BG004 verified offer decision where required.
- [x] Reuse BG006's late DB template-admission check and established human recovery claim, reserve/send/compensate pipeline. Keep merchant authentication/authorization in the existing API/Shopify/Woo boundaries; Background rechecks tenant/recipient/recovery claims.
- [ ] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

- [x] Remove the human-dispatcher's obsolete Meta category verifier/preflight and caller-provided parameter trust; pass BG001-prepared complete body/header/button components through the BG006 final admission adapter.
- [x] Audit references to both legacy template-selector/category services in all Background production code and tests after BG006; delete unused modules and stale tests/mocks once no real caller remains, or record the exact unretired consumer as a blocking architectural gap.
- [ ] Verify separate Shopify and Woo merchant admission changes against their owning tasks and fixtures; do not implement them from Background.

## Interfaces / Contracts

**Consumes** BG001 preparation, BG004 offer decision, BG006 template fence adapter and existing `HumanCommandDispatcherService`/`MerchantSendCommandService`. No new cross-repo template transport and no changes to the command payload unless specifically required by an independently accepted merchant API task.

## Dependencies

- `ARCH-047-BACKGROUND-001`
- `ARCH-047-BACKGROUND-004`
- `ARCH-047-BACKGROUND-006`


**Dependency and resume gate (26 October 2026):** BG001, BG004 and BG006 are `complete` in the inspected snapshot, and BG007 is **already claimed by the developer in Attempt 1**; do not re-claim, increment `attempt`, reset `executor` or promote its task status as part of this amendment. Re-check the canonical task metadata and the applied ARCH-047/BG001 documentation reconciliation before resuming. DB001 is not an additional direct dependency of BG007, and the Shared Meta-status v2 package is not a BG007 authoring/AST prerequisite. Any newly discovered cross-repository blocker must be reported to the architect rather than implemented from Background.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [x] The eligible post-window path forwards BG001 ShopBrand/body/header/button bindings unchanged; unavailable READY R2 media or a missing CTA checkout link refuses the send, and the in-window free-text path is unaffected.

- [x] In-window typed human text remains unchanged by this task; post-window uses only one eligible Follow-up Meta template with correct language/offer bindings.
- [x] Wrong-shop/WABA/wrong-variant, merchant template override, stale published slot and revoked Meta registration are refused.
- [ ] Rapid duplicate commands, provider timeout, STOP after preparation, credits consumed/refunded and retry safety.
- [x] Existing ARCH-040 human command, follow-up claim and final admission tests pass, plus focused integration/build/`git diff --check`.
- [x] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [x] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

- [x] Post-window human commands reject unsupported legacy purpose, externally originated/unlinked variants, wrong WABA/language, ambiguous assignments, unverified offers and client-supplied parameter overrides; no sequence-two or credit is consumed on refusal.
- [x] The production human template branch no longer calls the Meta category API or assembles body-only placeholder arrays from untrusted merchant command data. It uses the same BG006 late database fence and prepared components (including trusted checkout button and optional READY image header).
- [x] Obsolete Background template selector/category implementation is deleted after verified last-caller removal; all legacy tests/fixtures are rewritten or removed appropriately. If a production caller outside task ownership still requires the old module, record the exact blocker and do **not** claim complete removal.

## Validation

- [x] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [x] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [ ] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [x] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Keep changes local to the existing merchant command path and integration points. Any Shopify/Woo merchant UI filtering of available Follow-up templates belongs to its owning frontend task, not Background.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-007`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

In Progress — Developer Attempt 1 remains active. The canonical route confirms `execution_mode: developer`, `completion_mode: developer`, `executor: developer`, and the existing claim; no task lifecycle metadata was changed during this reconciliation. The parent architecture handoff reconciliation is present. BG001, BG004 and BG006 each have `status: complete` in the current parent task snapshot.

### Files Changed

The published implementation branch `task/ARCH-047-BACKGROUND-007` is at `942e68b2a43f66bec35dfeaaaa1d70e82ca9703a`, equal to `origin/task/ARCH-047-BACKGROUND-007`. Relative to `origin/main`, the branch changes 21 paths (884 insertions, 596 deletions):

- `scripts/integration-prisma-path.mjs`, `scripts/integration-prisma-path.test.mjs`, `scripts/test-integration.mjs`
- `src/services/recovery-conversation/follow-up-claim-cancellation.service.ts`, `human-command-dispatcher.service.ts`, `human-send-policy.service.ts`, `merchant-follow-up-template.service.ts`, `outbound-send-fence.service.ts`
- Deletes `src/services/whatsapp-template-category.service.ts` and `src/services/whatsapp-template-selector.service.ts`
- Adds `tests/integration/arch047-merchant-follow-up-final-permit.integration.test.ts`; updates `tests/integration/arch048-woo-initial-outreach.integration.test.ts`, `tests/integration/fixtures/recovery-human-dispatch.fixture.ts`, and `tests/integration/woo-initial-send-redis-fault.integration.test.ts`
- Updates `tests/unit/services/checkout-recovery.capacity-resume.test.ts`, `checkout-refresh.test.ts`, `matured-candidate.materialization.test.ts`, and `tests/unit/services/recovery-conversation/human-synchronous-rejection.test.ts`; adds `tests/unit/services/recovery-conversation/merchant-follow-up-template.service.test.ts`; deletes the two legacy selector/category unit test files

### Work Completed

The implementation integrates the human post-window branch with the BG001 prepared-template result and BG006 final database fence, rejects untrusted merchant template parameters and mismatched tenant/recovery/template identity, and preserves prepared body/header/button data. The legacy Background selector/category modules and their tests are removed after the implementation/test reference audit found no remaining references under `src/` or `tests/`. No source change was made during this reconciliation.

### Validation Results

Passed during this reconciliation from the canonical implementation worktree:

- `npx vitest run tests/unit/services/recovery-conversation/merchant-follow-up-template.service.test.ts tests/unit/services/recovery-conversation/start-human-command-dispatcher.test.ts` — 2 files, 31 tests passed.
- `npm run test:integration -- tests/integration/arch047-merchant-follow-up-final-permit.integration.test.ts` — 1 PostgreSQL integration file, 4 tests passed.
- `npm run test:arch040-recovery-conversation` — 10 files, 108 tests passed.
- `npm run test:arch040-background-runtime:postgres` — 2 PostgreSQL integration files, 9 tests passed.
- `npm run build` — Prisma Client v6.19.3 generation and TypeScript compilation passed.
- Targeted `npx eslint` over changed human follow-up production files and their focused tests — passed without diagnostics.
- `git diff --check origin/main...HEAD` — passed.
- Final standalone developer validation, 26 October 2026: `npm run lint` completed with no ESLint diagnostics; `git diff --check` completed without errors; `git status --short` printed no entries, confirming a clean implementation worktree at that point.
- Production and test reference audit for `whatsappTemplateSelectorService`, `metaWhatsAppTemplateCategoryService`, `templateCategories.verify`, and imports of the deleted modules returned no matches. One `purpose: "checkout-recovery"` literal remains in the unrelated `tests/unit/services/matured-candidate.materialization.test.ts`; it is not a human template caller and was not changed as an unrelated fixture.

Current branch evidence: the earlier reconciliation observed a pre-existing untracked top-level `typescript` text log, which it inspected and did not modify. The developer's later final standalone `git status --short` output was empty; that newer observation is recorded without inferring how the earlier log ceased appearing. Implementation HEAD was verified at `origin/task/ARCH-047-BACKGROUND-007`, with `origin/main` an ancestor. The dedicated parent worktree was on `task/ARCH-047-BACKGROUND-007`, clean before the earlier report edit, with HEAD `a9539e5baea15d28a940bcf6d0d8b1e51f07d4fe` equal to its origin task ref and `origin/main` an ancestor. No commit or push was made as part of this documentation update. Current-state evidence does not independently prove the original attempt-start synchronization or recursive-submodule preparation packet.

### Deviations

No implementation source change or unrelated artifact cleanup was made during the evidence reconciliation. The implementation commit includes integration-harness path scripts in addition to the human follow-up feature tests; build, lint and focused integration validation passed with these files present.

### Assumptions

The recorded current parent task states and existing implementation branch are the snapshot being reconciled. Current worktree cleanliness and ancestry are observations from this update, not retroactive proof of launcher preparation at attempt start.

### Unresolved Issues

**Acceptance remains incomplete; task deliberately stays `in_progress`.** The focused tests establish tenant/recovery scoping, forged parameter rejection, prepared component pass-through, idempotent repeat processing, revoked-registration refusal without provider dispatch/usage, and missing identity refusal. The current evidence does not fully demonstrate all listed STOP-after-preparation, provider-timeout, credit compensation/refund and retry interleavings; the corresponding Acceptance Criteria remain unchecked.

**External merchant admission verification remains outside this Background checkout.** The parent snapshot contains Shopify `ARCH-047-SHOPIFY-001` and API `ARCH-047-API-001` implementation records describing the new `FOLLOW_UP_*` admission/catalogue and empty client-parameter contract. Woo `ARCH-047-WOOCOMMERCE-001` records that its UI remains unavailable until the hosted API catalogue is available. This reconciliation did not run those repositories' tests or independently inspect their implementation worktrees, so the R6 cross-service verification criterion remains unchecked.

**Workflow evidence gap.** The launcher route and current mirrored worktree branches are verified, but the original attempt-start synchronization/recursive submodule preparation packet is not present in this update's evidence. Do not infer it from current branch ancestry. The implementation worktree's untracked `typescript` text log is pre-existing developer data and remains untouched.

### Architectural Concerns

No new cross-repository code was added. Preserve the separately owned Shopify/API/Woo admission and UI boundaries; any gap found by their owners should be coordinated by `moda_architect`.

## Architect Review

### Review Status

Pending — implementation not submitted.

### Review Notes

**26 October 2026 — architectural documentation handoff only:** The parent ARCH-047/BG001 AST and Shared-package contradiction has been resolved in the architect's documentation reconciliation. BG007 must consume BG001's trusted prepared-template output and BG006's late send fence; it must not compile the Admin AST or depend on a Shared AST package. This is **not** an architectural acceptance of BG007 implementation: there is no completed implementation review or new test evidence, and the developer Attempt 1 claim and task status remain unchanged.

### Reviewed Files

None yet.

### Validation Reviewed

None yet.

### Architecture Conformance

To be assessed against the reconciled ARCH-047 parent architecture and current repository code.

### Follow-up

Verify that the ARCH-047 parent and accepted BG001 reconciliation patch is present in the canonical development baseline. Once verified, the developer may **resume the existing claimed Attempt 1**, not start a second attempt: implement the post-window integration under R1–R7, preserve the current admission/moderation/consent/STOP/credit safeguards, run the task's declared tests, and complete the developer-owned Completion Report. If actual moderation or final-send contracts cannot safely cover prepared runtime parameters, return the specific issue to `moda_architect` rather than weakening the fence. Only the normal authorised review/completion workflow can close BG007.

## Execution Ownership Amendment

- Date: 2026-10-26
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, dependencies, task scope, acceptance criteria, and validation requirements.
- Claim state: Developer Attempt 1 was claimed after confirming all dependencies complete and preparing the canonical worktrees.
