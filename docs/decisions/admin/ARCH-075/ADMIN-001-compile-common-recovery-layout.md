---
id: ARCH-075-ADMIN-001
architecture_id: ARCH-075
title: Compile immutable common recovery layout into replacement templates
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: codex
claimed_at: 2026-11-13T02:25:49Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-004
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Compile immutable common recovery layout into replacement templates

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Compile immutable common recovery layout into replacement templates.

## Context

The user explicitly requires all Meta templates, AI replies and HUMAN messages to share one shop header and checkout footer, with product images separate. Existing Admin-owned SHARED wrapper definition/slot is the common immutable content authority; family-specific body/offer/opt-out content stays intact. No duplicate hardcoded frame builders.

## Scope

Admin-owned immutable common layout selection/reference, new replacement Meta clone compilation, translation reconstruction and visible cross-family preview only; existing authoring/localeAst JSON, compiler and SHARED wrapper definition/slot. Adopt published Shared website/common-reference contract. Do not activate live pointers or submit registrations in this task.

## Out of Scope

Other repositories, new database tables/settings, provider permissions, live registrations/activation, source merges, unapproved publication, changing billing/cap semantics, arbitrary source refactors, automatic mutation of approved templates. Background engine001 remains on published5.13.8 and producer-disabled.

## Requirements

Select exact saved immutable SHARED wrapper definition+locale and freeze canonical Shared commonRef in NEW Meta authoring.commonLayout JSON; include it in immutable source hashing. Re-read saved definition/locale, verify sourceHash/contentHash/locale/family/audience/status and use public Shared reference parser with existing injected digest. Client-provided projection alone is not authority. No new database table/setting. Common layout is body-only slot with authoritative editable header and checkout conditional/footer; no duplicated hardcoded common frame.

The ONE existing compiler projects saved common header tokens into Meta BODY prefix, preserves authored family-specific body and original opt-out footer text, then appends common checkout conditional as actual final BODY suffix; native Meta FOOTER is empty for new clones. Logo uses genuine verified LOGO/SQUARE IMAGE HEADER; text shop identity is BODY content, not simultaneous native text header. Preserve original authoring body/footer bytes and existing INITIAL contextual Reply validation; compiler validates final projected1024 length, variable count, header/button limits and complete semantic bindings after insertion. Do not truncate, drop opt-out, regex-delete arbitrary inline checkout or fabricate a registration. Existing duplicates require explicit review and clear preview. Impossible/provider-ineligible shape fails with actionable bounded error.

Immutable approved snapshots remain readable/unchanged. Clone revisions rather than mutate published definitions; reconstructed target locales preserve matching localized commonRef and variable bindings. Body translations remain family-specific, common header/footer translations are authored/reviewed once in common revision. Preview should say Common shop header and Common checkout footer, not implementation jargon, and demonstrate custom common text changes across Meta/AI/HUMAN without copy-paste. Default name/site/divider/check-out content is not a second hardcoded builder. Return actual provider/API/schema/activation gaps; no unreviewed template-part transport or outside-window freeform send.

### Reviewed baseline drafts and progress truth

Root reviewed six body-only CHECKOUT baseline drafts in `/tmp/moda-six-recovery-scenarios.md` and `.json` as reviewable inputs, not approved registrations. Validate them through the repository native test runner before any seeding; preserve verified offer.description/offer.code, no fixed percentage/deadline, initial contextual Reply tail and opt-out. Source inventory translation-run/item results may be complete despite legacy definition status TRANSLATION_QUEUED: show actual run/item review/approval/assignment counts, do not rewrite historical status merely to make badges agree. External registration still requires root review of concrete final compiled copy/limits and required20 locales.

### Scenario catalogue coverage

Confirmed supported core matrix: INITIAL/FOLLOW_UP × NO_OFFER/CODE_OFFER/AUTOMATIC_OFFER = six scenarios. CHECKOUT/ALTERNATIVE_PRODUCT are an additional target axis inside existing offered classes, never new discount promises. Inventory actual target eligibility from existing code and definitions. HUMAN outside-window uses existing approved RECOVERY_FOLLOW_UP_TEMPLATE catalogue; in-window HUMAN_TEXT uses the dynamic common frame. AI responses, terminal limits and service outcomes are dynamic content, not invented Meta purposes/HANDOFF enums. Two NO_OFFER published definitions cover two scenarios; duplicate queued NO_OFFER versions add no scenario coverage. Present clear scenario labels distinguishing approved business-initiated initial/follow-up recovery templates (including any supported outside-window HUMAN path) from dynamic AI product answers and HUMAN freeform messages. Prepare reviewable replacement/default seed drafts only for supported scenarios, with the one common layout and family-specific copy. Preserve existing offer eligibility/promises; no invented discount, policy, template family or transport. Missing supported scenario coverage must be explicit, not masked by duplicate queued versions. Preserve historical/queued definitions as immutable/cloneable records; no automatic deletion, retirement, registration or activation. Root reviews concrete copy/coverage before external registration. Golden previews and tests verify labels/coverage and common frame parity.

### Common revision lifecycle phases

Preapproval compile/save/registration may reference a fully reviewed immutable SAVED or PUBLISHED SHARED definition, with all20 reviewed locales and exact source/content hashes re-read. This does not activate its pointer or authorize runtime sends. Requiring PUBLISHED before compile would be circular because existing audited activation marks publication alongside pointer swap only after approvals. Runtime and final coordinated activation still require PUBLISHED and the current active SHARED slot/source/locale identity. No new stage-only publication action is needed. Test/describe both phases explicitly; no runtime eligibility relaxation.

## Work Items

- [x] Complete assigned bounded capability only.
- [x] Prove compatibility and meaningful negative/failure behavior.
- [x] Submit mirrored branch/report and stop.

## Interfaces / Contracts

Common content authority: selected immutable Admin SHARED wrapper revision and locale projection. Shared owns canonical semantic key/wrapper validation; Admin owns authoring/compiler/reference/activation; Background owns tenant-derived values, frozen rendering, sending and current fences. Existing template registration hashes remain authority for provider components.

## Dependencies

ARCH-075-SHARED-004

## Enables

Only explicitly promoted dependent tasks after acceptance.

## Acceptance Criteria

- [x] One common content source is used without duplicated formatting or unauthorized semantic widening.
- [x] Old stored projections/registrations remain readable and immutable; new fields do not grant tenant/provider authority.
- [x] Assigned validation and isolated mirrored synchronization evidence are complete.

## Validation

- [x] Golden custom-header/footer projections and Meta/dynamic parity with real public parser/renderer; legacy records unaffected.
- [x] Clone/translation/source-hash/tamper/stale-ref/locale mismatch and final composed-limit/opt-out preservation regressions.
- [x] Existing declared relevant tests/types/lint/build plus real PostgreSQL immutable-source fixture where applicable; exact-head CI and privacy checks.

## Stop Condition

After required work and validation, submit review and STOP. No enabled-task execution, merge, live mutation or unapproved public release.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet is startup/isolation authority. Report actual cross-owner gaps rather than inventing a setting/schema or weakening strict validation.

## Completion Report

### Status

Ready for architect review. Implementation committed and pushed. No GitHub Actions workflow is configured; root verified exact-head Vercel and preview-comment checks passed as supplementary validation. No live registration, assignment, activation or deployment was performed by this task.

### Files Changed

- `package.json`, `package-lock.json`: exact published Shared 5.13.9; exact @noble/hashes 2.0.1 provides browser-safe SHA256 to the canonical Shared parser.
- Authoring `common-layout.ts`, `common-layout-repository.ts`, `common-layout-reads.ts`, `types.ts`, `validation.ts`, `compiler.ts`, `repository.ts`, `registry.ts`: additive frozen reference, real saved-source authority, website variable and one compiler projection with final limits.
- Authoring `preview.ts`, compilation `reconstruction.ts`, `service.ts`, `reads.ts`, `meta-compiler.ts`, Meta `repository.ts`, `snapshot.ts`: reviewed target-locale reference, shared-renderer preview parity, registration-intent authority and bounded preview failure.
- Authoring `scenarios.ts`, `coverage.ts`, `reads.ts`; catalogue/page, common-layout selector, scenario coverage, existing workspace/draft/review preview and shared wrapper editor: six distinct scenarios, honest version/translation/approval/assignment counts, actual audience pointers and cross-family common layout preview.
- `tests/fixtures/arch075-common-layout.ts`, `tests/unit/arch075-common-layout.test.ts`, `tests/integration/arch075-common-layout.postgres.test.ts`, native ESM launcher/task PostgreSQL script: public parser/renderer, digest parity, immutable clone, stale-reference rejection, rollback, localization and compatibility evidence.
- Two baseline test fixtures only: existing recovery execution policy allowlist/count and existing platform-policy tab/dependency harness, preserving and extending role-boundary assertions. No production policy behavior changed.

### Work Completed

One exact saved SHARED source is frozen as `authoring.commonLayout`, including definition/source/locale/content identities and canonical prepared projection. Browser data is never authority: save and registration paths re-read the real reviewed source; English save locks its definition against concurrent retirement. The real existing compiler inserts the saved common header before the original body and opt-out text, then the saved checkout conditional last. Native Meta FOOTER is omitted only for new common-layout sources. Original AST body/footer bytes and INITIAL contextual Reply semantics are unchanged. Composed 1024-character and 10-body-parameter limits fail explicitly; content is never truncated or stripped.

Translated body jobs exclude common header/footer copy. Approval resolves the same immutable common definition/source hash's exact reviewed target locale; English fallback and foreign locale identities are rejected. Six reviewed CHECKOUT body drafts are selectable unsaved suggestions, not automatic seeds, registrations or business promises. Existing records remain immutable and cloneable.

Lifecycle clarification A (architect approved): fully reviewed immutable SAVED or PUBLISHED SHARED sources are eligible for **preapproval authoring/compilation/registration intent**. This grants no runtime sending authority. Existing wrapper publication marks PUBLISHED atomically with pointer replacement; requiring publication before replacement compilation would create a circular rollout. Runtime and coordinated final activation still require PUBLISHED plus the current active SHARED pointer and exact source/locale identities. This task creates no new stage-only publication action and changes no active pointer. The PostgreSQL fixture proves source creation/cloning leaves registrations and active slots empty.

### Validation Results

- Native focused common-layout regressions: final 8/8 passed, including the additional bounded Meta-preview error regression.
- Six scenario drafts validated through actual Admin AST validator, INITIAL Reply-tail checks and final common composition.
- Real disposable PostgreSQL test: 1 passed; save/replay/clone, exact persisted reference, original source unchanged, spoofed locale/retired source rejection with rollback, localized reference and no registration/activation.
- TypeScript `npx tsc --noEmit --incremental false`: passed on final source.
- `npm run lint`: passed with zero errors and one existing nested `database/eslint.config.mjs` anonymous-default-export warning; final changed-file lint also passed.
- `npm run build`: passed before the final bounded Meta-preview error mapping; final type/changed-file lint and focused regression passed after it.
- Full `npm run test:unit`: 784/784 passed before the final additional regression; final focused suite 8/8 passed.
- `npm test` observability/security: 334/334 passed.
- Source PR: https://github.com/kodjobaah/moda-interact-admin/pull/89 (draft). No GitHub Actions workflow is configured. Root verified exact-head Vercel and preview-comment checks passed, with supplementary deployment completed. Root reports exact-head architect source review passed without findings. This is not a browser visual review.
- Visual fixture: actual components and built production CSS, fictional data only, at `/tmp/admin001-preview.html`. Browser visual verification unavailable: iab absent; Chrome create-tab attempts timed out twice and the exact URL tab was not found. No screenshot, live visual or browser-pass claim.
- `git diff --check`: passed.

All checks use sanitized process environments, localhost dummy URLs or a uniquely named disposable PostgreSQL container. A synthetic test-only AUTH_SECRET supplies the existing policy-signing harness; no live credentials or databases were used.

### Deviations

Existing full-suite fixtures lagged the already-landed recovery execution policy/tab UI. Updated their exact allowlist/count and explicit mocks, keeping authorization/pagination assertions and adding recovery-policy access assertions. The first broad run also exposed the new preview adapter's incorrect envelope argument; corrected it using the actual public `readPreparedWrapper` contract, without a local schema or cast.

This agent's runtime restricted sibling-worktree writes/localhost binding. Initial exact-path edits used the authorized tool override; after root's instruction, remaining authored `/tmp` patch helpers and validation/visual commands were mechanically executed by root in the canonical worktree. No alternative checkout or shared source tree was used. An active helper was inadvertently rewritten once, interrupting that run; root reran an immutable copy. Only completed rerun results count above.

### Assumptions

The single common source is a reviewed SHARED wrapper with one response slot, name and website exactly once in the header, empty static footer, and checkout URL last in its single conditional, as required by the published parser. Runtime tenant values and media authorization remain Background-owned.

### Unresolved Issues

Provider approval remains external: local compiler success is not Meta approval. In particular the required final dynamic checkout parameter must survive actual Meta registration eligibility; no successful registration is claimed and no copy was silently altered. Existing inline checkout/button duplication remains visible for explicit review. Admin002 owns coordinated common-pointer/per-shop replacement activation after all required locales are approved.

Catalogue aggregation SQL was schema-reviewed; its pure scenario projection has tests. The real PostgreSQL fixture specifically covers immutable-source authority rather than the catalogue aggregation query. No production inventory mutation or provider permission change was attempted.

### Architectural Concerns

No new settings/table or duplicated common frame renderer. The existing Shared renderer supplies dynamic examples; the existing Admin compiler owns provider projection. Website/reference validation is consumed from published Shared 5.13.9. Existing approved Meta snapshots remain unchanged. Root/architect owns final source merges and all live rollout.

### Physical Worktree Isolation

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-ADMIN-001`, branch `task/ARCH-075-ADMIN-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-ADMIN-001`, branch `task/ARCH-075-ADMIN-001`.
- Shared workspace/source checkout switched or mutated: no. Another task worktree reused: no.
- Prepared packet: claim attempt 1, executor codex; parent synchronization not-needed/already-current at `ce95d092677af62a18fb753b029e8df7e20d9955`; implementation synchronization not-needed/already-current at `447d651f775411a500937cc0d66e3ca8fd11a9fc`.
- Launcher recursive submodule sync/update passed; database recorded `5329d5390d346042895219663f3a040ea54ae168`. No startup preparation repeated.

### Source Checkpoint

- Implementation: `dab45425891dcc47f3679dcefcc91b59faee09fe`.
- Separate baseline fixture repair: `bd9c12e5cfc7d2f209c3a8a0eb0fee727648f390`.
- Source branch: `task/ARCH-075-ADMIN-001`, pushed; worktree clean after checkpoint.
- Draft source PR: https://github.com/kodjobaah/moda-interact-admin/pull/89.
- Root executed the exact owned-path checkpoint script; no main merge or force-push.

## Architect Review

### Review Status

Accepted

### Review Notes

Actual exact implementation `dab45425891dcc47f3679dcefcc91b59faee09fe` reviewed against baseline `bd9c12e5cfc7d2f209c3a8a0eb0fee727648f390`. Canonical public common-reference parser/browser digest, saved-source authority, locale reconstruction, existing compiler projection/limits, preserved body/opt-out and scenario/progress views conform. Final bounded Meta error mapping reviewed. Report-only correction eac2d5e2a resolves stale CI wording/checklists. No source findings remain.

### Reviewed Files

Common-layout parser adapter/source repository/choices; authoring compiler/validation/repository/preview/types; translation reconstruction/review; Meta snapshot/repository; six-scenario draft/coverage/UI; PostgreSQL and public renderer parity/negative tests; package dependency metadata.

### Validation Reviewed

784 full units before final bounded error mapping; final8 focused regressions,334 observability/security checks, real immutable-source PostgreSQL fixture, final types/lint passed. Production build passed before that mapping; changed-file checks and regression passed afterward. Exact-head Vercel checks passed as supplementary build/deploy evidence; no Actions workflow exists. Browser visual verification unavailable and not claimed. Canonical prepared synchronization/recursive isolation and root-assisted exact-worktree execution transparently recorded; no alternate checkout/live mutation.

### Architecture Conformance

One saved immutable SHARED revision drives compilation, not duplicated hardcoded frame. Reviewed SAVED eligible only preapproval; runtime active/PUBLISHED remains required. Existing approved snapshots and authored initial Reply/opt-out content remain immutable. No new schema/permission/provider operation. Provider acceptance of checkout-final template shape remains explicit external gate, not a local success claim.

### Follow-up

Root merges exact source. BG002 becomes eligible only after BG001 also Complete and compatible-reader rollout proof; Admin002 stays gated on BG002. Root reviews concrete scenario copy/cohort and actual Meta approvals before live activation. No automatic seeding/registration/activation or provider-template multipart expansion.
