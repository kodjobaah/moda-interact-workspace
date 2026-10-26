---
id: ARCH-047-SHOPIFY-001
architecture_id: ARCH-047
title: Restrict Shopify merchant follow-up choices and admission to Moda-authored templates
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 35
executor: developer
claimed_at: 2026-10-26T12:16:42Z
attempt: 1
depends_on:
  - ARCH-047-DATABASE-001
enables:
  - ARCH-047-SYSTEM-TEST-001
created: 2026-10-26
updated: 2026-10-26
---

# Restrict Shopify merchant follow-up choices and admission to Moda-authored templates

## Architecture

Architecture: `ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. Defined against the 26 October 2026, 06:28 workspace snapshot. The task definition was published on `origin/main` in `5c329bbc`; this developer takeover is being materialised on its canonical parent task branch. No implementation is claimed before the canonical launcher claim.

## Objective

Replace the Shopify recovery human follow-up's legacy template list/admission allowlist with a tenant-scoped catalogue of eligible **Moda-authored, explicitly published** Follow-up template choices, leaving Background BG007 authoritative for verified offer resolution and final sending.

## Context

`moda-interact/app/services/recoveries/recovery-human-commands.server.ts` still filters `purpose: "checkout-recovery"` in `readApprovedRecoveryTemplates` and in `RECOVERY_FOLLOW_UP_TEMPLATE` admission. The new six-purpose catalogue instead uses `FOLLOW_UP_NO_OFFER`, `FOLLOW_UP_CODE_OFFER` and `FOLLOW_UP_AUTOMATIC_OFFER` with a non-null Meta registration; eligibility cannot be inferred solely from an `APPROVED` variant. Merchant intent remains subject to Background BG007's final read-only checkout/offer and provider-safety recheck.

## Scope

- Own only `moda-interact/` Shopify authenticated recovery-list/detail/server-action/UI files and focused tests; start from the actual existing `readApprovedRecoveryTemplates`, merchant command submission and reply-composer paths.
- Use the current conversation/recovery/shop identity and validated sender WABA to list **only** live, enabled, non-retired, locally published, Meta-approved and current provider-approved `FOLLOW_UP_*` variants linked to a Moda-authored registration. Reject ambiguous shop/WABA/name/language records.
- Preserve existing `templateVariantId` merchant intent for an exact candidate and derive provider template name/language from DB; do not let the browser supply Meta names, prices, checkout URLs, discount codes or template parameters as trusted values.
- Extend Shopify preview/selection UI only as required to display the appropriate source language and purpose and report a safe unavailable state without inventing an offer.

## Out of Scope

- No changes to `moda-interact-background`, hosted Woo API, WordPress plugin or DB schema; no creation/editing of Meta templates; no offer-eligibility evaluation or billing admission in Shopify; no cart/checkout mutations.

## Requirements

**R1 — Authoritative selection.** For merchant-initiated sequence-two only, query `WhatsAppTemplateVariant` joined to `WhatsAppTemplateMetaRegistration` and definition/locale, using the current authenticated shop, configured sender and exact target language. Accept only `purpose` in `FOLLOW_UP_NO_OFFER`, `FOLLOW_UP_CODE_OFFER`, `FOLLOW_UP_AUTOMATIC_OFFER`; reject null registration, expired/stale status, retired/unpublished definition, disabled variant and wrong WABA. Do not return templates merely because a legacy row says `APPROVED`.

**R2 — Checkout/offer semantics.** Only offer a choice when the existing human-control, due-time, rolling-window and sequence-two restrictions allow it. If there is no verified checkout-specific positive-offer evidence, the UI must not promise eligibility for CODE/AUTOMATIC. It may show safe No Offer candidates while Background BG007 still re-evaluates the exact chosen variant. No Shopify GraphQL/Meta metadata GET in the merchant command transaction.

**R3 — Admission and replay.** Validate `templateVariantId` in the server action against the same current catalogue; reject stale/forged variants. Persist the existing idempotent sequence-two claim and provider name/language snapshot only after the existing successful admission conditions; the Background process will re-resolve all parameters and perform the final fence. Do not add staff roles or a second outbound queue.

**R4 — Retire obsolete behaviour.** Remove all `purpose: "checkout-recovery"` filters and obsolete imported-template choices in this Shopify interface; remove dead helpers/tests only after checking real imports, while preserving human text, tenant scope, STOP/consent, late response and billing behaviour.

## Work Items

- [x] Replace both legacy selectors in `recovery-human-commands.server.ts` with the DB-backed current `FOLLOW_UP_*` catalogue and exact variant validation.
- [x] Update dedicated merchant template selector/preview React components and state hook as necessary without bundling the whole Recovery Detail UI into one file.
- [x] Replace legacy mocks and add post-window, selection, replay, stale/foreign WABA and no-offer tests.
- [x] Document actual task worktree/commit/test evidence and source-level obsolete-code cleanup.

## Interfaces / Contracts

Consumes `Shop`, `WhatsAppTemplateVariant`, `WhatsAppTemplateMetaRegistration`, the published template definition and existing `MerchantConversationSendCommand` (name/language command snapshot). Browser sends only the stable `templateVariantId` already supported by Shopify. BG007 owns offer verification, fresh template resolution, parameter binding and provider final admission; this task does not change that ownership.

## Dependencies

- `ARCH-047-DATABASE-001` (Complete in the supplied snapshot).

## Enables

- `ARCH-047-SYSTEM-TEST-001` after acceptance and integration.

## Acceptance Criteria

- [x] Shopify only exposes Moda-authored, published, provider-eligible `FOLLOW_UP_*` assignments for the correct shop/WABA/language, and denies legacy/null-registration/stale/ambiguous variants.
- [x] Positive-discount candidates are not presented as verified customer-specific savings without read-only provider evidence; this Shopify interface exposes only safe No Offer choices. BG007 independent final admission is a separate Background and system-test gate, not an outcome claimed by this task.
- [x] Existing human-control, service-window, one-follow-up, idempotency, consent, STOP and billing semantics remain unchanged.
- [x] No production `purpose: "checkout-recovery"` filter or obsolete imported-template action remains in this Shopify merchant command/list path; no duplicate template picker or monolithic component is introduced.

## Validation

- [x] Focused Shopify server-action and UI tests, lint/typecheck per actual package scripts; test stale consent/offer/assignment and denied-user boundaries.
- [x] `git diff --check` and source-reference check for legacy `checkout-recovery` purpose in touched Shopify paths; preserve unrelated code.

## Stop Condition

Complete only this Shopify task, update Completion Report and set task to `review`, then STOP. Do not change system-test, parent architecture, other repositories or `_index.md` files.

## Implementation Notes

Use launcher-prepared dedicated mirrored `task/ARCH-047-SHOPIFY-001` worktrees and the current task branch as required by the repository policies. The source snapshot is not proof of current main; reconcile exact installed dependency versions at implementation start. Do not weaken Background's final admission by relying on early UI eligibility.

## Completion Report

### Status

Ready for Review — developer-executed Attempt 1, claimed at `2026-10-26T12:16:42Z`. The incremental implementation correction labelled `attempt2.patch` was applied within the same task claim and does not increment the task's `attempt: 1`. Implementation changes were committed as `d863b9d` (`feat(arch-047-shopify-001)`) and pushed to `origin/task/ARCH-047-SHOPIFY-001`. Formal architect review and the developer's explicit completion decision remain outstanding.

### Files Changed

Implementation repository: `moda-interact`, 15 source/test files in commit `d863b9d`:

- `app/routes/app/recovery-detail/human-conversation-panel.tsx`
- `app/routes/app/recovery-detail/loader.server.ts`
- `app/routes/app/recovery-detail/merchant-reply-composer.tsx`
- `app/routes/app/recovery-detail/state.ts`
- `app/services/platform-configuration/contracts.server.ts`
- `app/services/recoveries/recovery-detail.server.ts`
- `app/services/recoveries/recovery-follow-up-catalogue.server.ts` (new)
- `app/services/recoveries/recovery-follow-up-sender.server.ts` (new)
- `app/services/recoveries/recovery-human-commands.server.ts`
- `tests/fixtures/arch047-shopify-follow-up.ts` (new)
- `tests/unit/arch040-shopify-command.test.ts`
- `tests/unit/arch040-shopify-layout.test.tsx`
- `tests/unit/arch047-shopify-follow-up-catalogue.test.ts` (new)
- `tests/unit/arch047-shopify-follow-up-sender.test.ts` (new)
- `tests/unit/arch047-shopify-follow-up-ui.test.tsx` (new)

The separate review-submission patch updates only this parent-workspace task definition. No domain `_index.md`, parent architecture, database schema or Background implementation is changed.

### Work Completed

- Replaced the legacy `checkout-recovery` purpose selectors and list counts in the Shopify recovery human-send and recovery-detail paths with a shared, database-backed `FOLLOW_UP_*` catalogue.
- Resolves the authenticated active Shopify shop and configured, trusted Meta sender WABA; enforces shop/WABA scoping, purpose, immutable Moda definition/locale provenance, publication success, reviewed/source locale policy, provider approval, provider identity consistency, non-retirement and drift checks. Ambiguous candidate slots fail closed.
- Serves only safe `FOLLOW_UP_NO_OFFER` choices while checkout-specific positive-offer eligibility is not independently verified. No customer discount, checkout URL, Meta template identity or template parameter is trusted from browser input.
- Revalidates the selected `templateVariantId` under the existing serializable merchant-command transaction and writes the chosen server-resolved provider template name/language snapshot. Preserves human-control, due-time, service-window, recipient/reachability, sequence-two claim and idempotent replay behaviour without a second queue or provider calls in admission.
- Updates the recovery detail loader, selector and UI eligibility/selection behaviour; clears stale selections and removes legacy template presentation. Keeps existing human text and platform control paths.
- Adds tests covering wrong/foreign shop or WABA, publication and Meta drift, source/translation status, ambiguity, missing sender configuration, language fallback, unverified offers, stale selection and repeat/replay admission, together with existing ARCH-040 command and UI regressions.

### Validation Results

From developer-provided `typescript(20261026-125437)` terminal log, after applying the incremental Attempt 2 correction:

- **Prisma:** `npm run prisma:generate` succeeded; Prisma Client **6.19.3** generated from `database/prisma/schema.prisma`.
- **Focused tests:** `npx vitest run tests/unit/arch047-shopify-follow-up-catalogue.test.ts tests/unit/arch047-shopify-follow-up-sender.test.ts tests/unit/arch047-shopify-follow-up-ui.test.tsx tests/unit/arch040-shopify-command.test.ts tests/unit/arch040-shopify-layout.test.tsx tests/unit/recovery-detail-readers.test.ts` — **6/6 test files; 138/138 tests passed**.
- **Lint:** `npm run lint` completed without reported errors.
- **Typecheck:** `npm run typecheck` (`react-router typegen && tsc --noEmit`) completed without reported errors, including a subsequent explicit repeat.
- **Production build:** `npm run build` succeeded for the client and SSR server bundles. Non-blocking warnings concerned Rollup's handling of upstream Zod comments, the Prisma browser external, empty chunks and large client chunks; no build failure occurred.
- **Git whitespace:** `git diff --check` is shown without reported errors after patch application and validation.
- **Source reference verification:** inspection of the supplied snapshot found no `purpose: "checkout-recovery"` selector and no `readApprovedRecoveryTemplates` reference in the touched Shopify command/detail/loader/selector files.
- **Scope:** a targeted six-file test run, not a complete application test suite. No Shopify-to-Background/Meta end-to-end test was run under this task.

### Deviations

None from the Shopify task's bounded implementation scope. Positive CODE/AUTOMATIC offer options are deliberately not offered without checkout-specific verified provider evidence; the task explicitly permits the safe No Offer selection. The two implementation patch deliveries were applied during the same developer task attempt.

### Assumptions

- Existing `Shop` tenant identity, ARCH-043 sealed platform sender configuration (with its documented missing-record-only environment fallback), Prisma schema and existing recovery command/credit machinery remain authoritative; no new database schema or merchant role is required.
- Provider/template final admission, verified checkout-specific offers, and Meta delivery remain Background-owned and must be independently rechecked at dispatch by the relevant Background implementation.

### Unresolved Issues

- `ARCH-047-BACKGROUND-007` remains **Ready**, not Complete, in this snapshot. Its independent pre-send revalidation, parameter resolution and provider rejection cannot be claimed as integrated or verified by these Shopify tests. Integration belongs to its own task and terminal system validation.
- Positive CODE/AUTOMATIC options remain unavailable until the separate checkout-specific provider eligibility path can substantiate them. This is intentional fail-closed behaviour, not a Shopify implementation failure.

### Architectural Concerns

- Cross-repository integrated validation must confirm consistency between Shopify accepting the Admin-authored English `SOURCE_SAVED` locale and Background's final eligibility/registration checks. Do not weaken Background final admission to match early UI choices; reconcile any disagreement through the owning task/architect.
- No new cross-service contract, schema, provider mutation or billing mechanism was introduced in this Shopify task.

### Git / VCS

- **Task branch (both repositories):** `task/ARCH-047-SHOPIFY-001`.
- **Parent task worktree:** `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-SHOPIFY-001`; canonical task file above, with `status: in_progress` in the supplied snapshot before this review-submission patch.
- **Implementation task worktree:** `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-SHOPIFY-001`; the terminal log and developer's worktree archive show execution from the dedicated task worktree on the matching task branch.
- **Primary workspace root:** not separately printed by the supplied launcher evidence. Dedicated parent and implementation paths, not shared/default checkout paths, are recorded.
- **Start-of-attempt synchronization (from existing task claim report):** parent `origin/main` already incorporated; implementation task worktree based on `origin/main` commit `1ef61c8c4d9b405b42bd24f3d81b19f170f16cdf`. The claim reports recursive submodule sync/init success and nested database commit `3f1f50b91c9e93ff9647a3d1d7f6fd46b9b888b9`. Full launcher packet / task-branch fast-forward evidence is not in the latest terminal log.
- **Implementation repository:** `moda-interact`; commit `d863b9d`, message `feat(arch-047-shopify-001)`; explicitly pushed to `origin/task/ARCH-047-SHOPIFY-001` after an initial plain `git push` failed because the upstream branch was `origin/main`. The subsequent `git push -u origin task/ARCH-047-SHOPIFY-001` succeeded and set the correct upstream.
- **Parent workspace:** this submission changes the canonical task file only; parent commit SHA / successful push remain pending developer application of this patch. No implementation submodule gitlink is included in this patch.
- **Integration:** implementation branch not merged to implementation `main`; parent branch not merged to workspace `main` by this submission.
- **Isolation evidence limitation:** the snapshot and terminal log support dedicated worktree use, but do not independently reproduce the complete launch preparation packet or prove that no other checkout was touched. Architect may request that evidence before acceptance.

## Architect Review

### Review Status
Pending.

### Review Notes
No implementation reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Not assessed.

### Follow-up
Review the final integration with BG007; do not use system testing as an implementation dependency.

## Developer Ownership Amendment

- Date: 2026-10-26.
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-SHOPIFY-001` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_app`, coordinator, repository, task scope, acceptance criteria, validation requirements, dependency gate, Ready eligibility, and attempt 0. The explicit dependency `ARCH-047-DATABASE-001` was verified complete. This amendment does not itself claim an implementation attempt.
