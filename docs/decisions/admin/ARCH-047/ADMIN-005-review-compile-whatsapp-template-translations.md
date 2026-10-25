---
id: ARCH-047-ADMIN-005
architecture_id: ARCH-047
title: Reconstruct, review and compile translated templates in Admin
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-047-DATABASE-001
enables: []
created: 2026-10-24
updated: 2026-10-25
---

# Reconstruct, review and compile translated templates in Admin

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`. Coordinator: `moda_architect`. This is a **defined but not materialised** task until the developer's launcher creates the canonical task branch/worktree.

## Objective

Reconstruct complete immutable locale templates from Background **keyed translated segments**, provide full-language review, and persist Meta-ready or wrapper-ready projections produced solely by Admin.

## Context

The adopted ARCH-047 design is **Moda Admin-only authoring**. A saved English source definition and its corresponding language content are immutable: corrections create a different definition using **Clone as New**. There are six Meta recovery purposes (`INITIAL`/`FOLLOW_UP` × `NO_OFFER`/`CODE_OFFER`/`AUTOMATIC_OFFER`) and one internally published `MODA_CONVERSATION_WRAPPER` family with `SHARED`, `AI` and `HUMAN` audiences. No template authored externally in Meta may be adopted.

`ARCH-047-DATABASE-001` defines the eleven-table persistence boundary, including `WhatsAppTemplateDefinition`, `WhatsAppTemplateLocale`, translation Run/Item/Batch/BatchItem, `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateMetaEvent`, publication Operation/Target and `WhatsAppConversationWrapperActiveSlot`, plus the nullable link to existing shop `WhatsAppTemplateVariant` and existing `CommerceAuditEvent` actions. Database stores technical relations/JSONB but does **not** enforce template lifecycle/business rules. Admin must enforce those rules transactionally. This Admin task never modifies Prisma schema or the existing database migration.

The six Admin tasks have **only `ARCH-047-DATABASE-001` as a formal dependency**. They own separate route/action/service/component modules, use stable documented persistence payloads, and must prove their capability with fixtures or injected dependencies when a sibling Admin/Background implementation is not yet complete. The end-to-end system test, not an artificial task chain, verifies their integration.


## Scope

- Own the `compilation/` module and `/system-controls/whatsapp-templates/[definitionId]/review/` interface. Read saved English locale structure and `TranslationItem.translatedAst` keyed segment results, not an AST returned by Background.
- For each of the 19 target languages: verify all required segment keys exactly once; compare each protected marker's exact multiplicity and semantic identity with the original `sourceSnapshot`, allowing reordered text but rejecting mutated/duplicated/dropped tokens, invented variables, unexpected keys and stale source hashes. Restore semantic AST variable nodes using Admin's authoring registry and reconstruct complete language components while preserving nontranslatable structure/URLs/button actions. Reject invalid/unsafe output and display a per-locale reason.
- Display all **20 complete language previews** (English + 19 generated) with text header/body/footer/ordered buttons or wrapper header/response slot/conditional footer. Provide source-vs-translation comparison, variable map and review status, not just a translated-count indicator. Admin may approve/reject results; **no in-place editing of a saved source or accepted locale**. A content correction uses Clone as New and a separate translation/review lifecycle.
- Round-trip the canonical `shopBrand.*` identifiers from ADMIN-003 through protected-marker reconstruction; never resolve actual merchant brand values or embed fictional preview substitutions in saved locale content. Accept all eight defined keys only where the author's purpose/component registry permits them. A Meta text header supports at most the allowed single variable, a Meta footer stays static, and wrapper header/footer/conditional text retain their typed brand bindings.
- Server-side revalidate reconstructed content, language/provider code compatibility and Meta-supported component limits. For Meta family, reuse the **existing ADMIN-003 pure authoring compiler and variable registry** (do not fork a second compiler) to compile each approved locale into **final provider `components`** and frozen positional `parameterBindingsSnapshot` (header/body/button indices, canonical semantic keys including `shopBrand.*`, compile/schema version and content digest). Do not let a translated rearrangement silently swap runtime variable meanings.
- For wrapper family, compile a **prepared runtime projection** (literal header/footer segments, required response slot, optional checkout-URL conditional and typed runtime bindings) that Background can render without parsing Admin's authoring AST. The saved English locale already contains its prepared projection from ADMIN-003; do not rewrite it. Insert a prepared projection once for each newly reconstructed language.
- Persist completed locale `localeAst`/`contentHash` exactly once with review evidence (`reviewedByAdminId`, `reviewedAt`, `status`); **do not alter an existing finalised locale's content** or source English AST. Store the prepared projection in the same locale JSONB envelope, e.g. `{schemaVersion, authoring, prepared}`: English is generated at its original save; translated locales are generated on first insertion. No subsequent in-place content or projection update is allowed. For Meta, later ADMIN-006 copies the approved compiled objects verbatim into frozen `MetaRegistration` snapshots after explicit confirmation.
- Persist only bounded review metadata/audit. Read existing model/runtime capabilities before enabling component types, and ensure full-language completeness checks remain application-owned.


### Required React component decomposition

Use a thin protected Server Component route and **separate** focused client components under `src/components/admin/whatsapp-templates/compilation/`:

- `TranslationReviewWorkspace` — layout/orchestration shell only.
- `ReviewLanguageSelector` — 20-locale selection and approval/failure indicators.
- `SourceTranslationComparison` — complete English/target comparison; reuse ADMIN-003's read-only display primitive when available.
- `ComponentAndVariableDiff` — header/body/footer/buttons, protected markers, bindings and diagnostics.
- `MetaTemplateReviewPreview` and `ConversationWrapperReviewPreview` — distinct family-specific views; do not cram both template formats into one giant conditional component.
- `TranslationReviewActions` — confirm/reject, pending/error states and no in-place editing controls.

Use a dedicated `useTemplateTranslationReview` controller for client selection/action state. Split keyed-segment verification, placeholder restoration, locale reconstruction, Meta compilation adapter, wrapper projection compilation and database finalisation into **separate pure/service files** under `src/lib/admin/whatsapp-templates/compilation/`. Reuse the pure compiler **owned by ADMIN-003** rather than copying or redefining it; define the required compile port/typed inputs explicitly for fixtures in a separately prepared worktree. Route/action files must not host reconstruction logic, SQL or large JSX trees. Preserve the same exact preview DTO used by authoring wherever applicable.

## Out of Scope

- No translation provider calls or Batch polling, Meta submission/status mutation, merchant assignment, wrapper activation, new Shared AST package or database migration.
- No automatic Meta template editing or partial publication; no human-authored customer response replaces a wrapper slot.


## Requirements

- [x] Reconstruct only when persisted source hash matches its translation run; late provider results and stale clones cannot overwrite accepted content.
- [x] Protected token multisets and component-key sets must match exactly; translation may reorder variables, compiler must derive correct per-language positional binding snapshots.
- [x] Meta header/body and wrapper header/footer/conditional `shopBrand.*` references survive reconstruction as typed identifiers, with no merchant data captured during translation or compilation; invalid component/key combinations fail validation.
- [x] English and all 19 translations are previewable; if rejected/malformed, locale stays unapproved with actionable diagnostics and does not silently become publishable.
- [x] Review writes are idempotent, guarded and audited. Template text changes always require a new definition; metadata/progress may update independently.


All server reads/mutations of template management require the existing authenticated platform-admin boundary; mutations and privileged cross-shop reads require **`SUPER_ADMIN`**, verified server-side (`requirePlatformAdminPage` / `requirePlatformAdminMutation` or repository-equivalent). Reject client-supplied actor identity, WABA ownership, approval and shop eligibility assertions. Persist bounded/redacted audit records using the existing `commerce.CommerceAuditEvent` and ARCH-047 audit enum; do not log tokens, credentials or unnecessary customer/checkout data. Reuse the platform's shared structured logger only for needed semantic logs.


## Work Items

- [x] Implement typed, Admin-local reconstruction/validation and consume ADMIN-003's deterministic provider/wrapper compiler and variable registry via a focused adapter/fixtures; do not add a competing compiler.
- [x] Implement review screen with English/current-language side-by-side previews, variable/button comparison and approve/reject actions.
- [x] Add transactional locale finalisation and audit with stale/duplicate/concurrent review tests.


## Interfaces / Contracts

**Inputs:** `TranslationRun.sourceSnapshot` with keyed protected source segments; `TranslationItem.translatedAst` with keyed translated segments; English `TemplateLocale.localeAst`. **Writes:** 19 finished `WhatsAppTemplateLocale` rows, each `localeAst` containing its complete authoring structure **plus prepared runtime/provider projection**; `contentHash`, review metadata and bounded audit. **Prepared Meta envelope example (illustrative; emit the canonical ADMIN-003 compiler shape):** `{schemaVersion:1, category:'MARKETING', components:[...], parameterBindings:{header:[{position:1,variable:'shopBrand.brandName'}],body:[{position:1,variable:'customer.firstName'}],buttons:[...]}, contentHash:'...'}`. Header bindings are present only for a variable-bearing header; brand values themselves are never frozen.  For conversation wrappers use `{schemaVersion:1, header:[...], responseSlot:'response.body', footer:[...], conditionals:[...], variableBindings:[...]}`. These JSON payload formats are Admin-owned persistence contracts, not a separate Shared implementation. This task **does not create MetaRegistration**; ADMIN-006 freezes copies only on confirmed submission.


**Module ownership.** Keep this task modular: put its domain services under `src/lib/admin/whatsapp-templates/compilation/`, components under `src/components/admin/whatsapp-templates/compilation/`, and its server actions in a task-specific `src/app/actions/whatsapp-template-compilation.ts`. Avoid a global `whatsapp-templates.ts` catch-all or unrelated edits to sibling modules. Prefer small repository/domain, validation, orchestrator and view components. Only the English authoring task owns the shared navigation/catalogue shell; other tasks provide focused subroutes/panels, not a second editor or shell.


## Dependencies

- `ARCH-047-DATABASE-001` — **the only formal task dependency**. No `ARCH-047-ADMIN-00N`, Background, Messaging or new Shared publication dependency is permitted. Use seeded DB fixtures and injected ports to test independently when upstream/downstream implementations are absent. Status remains Pending until DB001 is confirmed Complete in the canonical task record; do not infer completion from tests alone.

## Enables

None at task-definition time. Completion of this task does not grant permission to start another task or skip an independently required system-test gate.

## Acceptance Criteria

- [x] React views are composed from separately named, independently testable components; route pages, controller hooks, pure domain helpers, server actions and database services are in separate files with no monolithic screen/action implementation.

- [x] Each language's complete preview and durable metadata reflect the same validated source; exactly 20 reviewed locales are required by application policy before the definition is eligible for the relevant publication path.
- [x] Header/body/footer/buttons and wrapper conditional segments map correctly; missing/duplicate/prohibited variable markers block reconstruction; reordered variables bind to the intended semantic values.
- [x] Translated Meta headers retain their header position and `shopBrand.*` semantic key (where allowed); wrapper brand keys remain available in permitted header/footer/conditional slots, while Meta footers contain no variable bindings.
- [x] Approved locales contain Meta-ready or wrapper-ready projection with no dependency on a Background AST compiler. No content mutation of saved/approved templates occurs.
- [x] Rejection leaves prior live template assignments/active wrapper pointers unchanged; only newly authored content may replace them later.


## Validation

- [x] Token protection/reordering and variable-binding compiler unit tests for English/French/German and scripts with changed placeholder order; include Meta text-header `shopBrand.brandName`, body references, repeated brand variables, wrapper footer brand values, forbidden Meta footer tokens, button/URL protections and malformed translator responses.
- [x] Admin UI full-preview/a11y tests; PostgreSQL idempotent locale finalisation/auth/audit tests using fixture translation items; lint/typecheck/`git diff --check`.


## Stop Condition

After task-scoped work, acceptance criteria, validation and Completion Report are complete, set `status: review`, return control to `moda_architect` and **STOP**. Do not mark this task Complete yourself, start sibling/Admin/Background tasks, modify `_index.md`, merge branches or push main.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md`, `docs/developer-task-workflow.md`, the revised parent ARCH-047 architecture and current Admin repository instructions. Use launcher-prepared dedicated parent/implementation task worktrees and mirrored `task/<TASK_ID>` branches. In the Completion Report record prepared physical worktree isolation, start sync, recursive submodule materialisation, exact test commands/outcomes, changed paths and commits. The implementing agent must not modify `docs/decisions/**/_index.md`, another task, the parent architecture, another repository, or follow-on work. Reuse existing Admin Store Category AST authoring and Merchant Pricing translation UX patterns without copying their domain services or creating a competing generic runtime. Inspect the actual worktree state before implementation; the attached snapshot is not a live Git-branch guarantee.


## Completion Report

### Status

**Review — developer workflow Attempt 1 (claimed at `2026-10-25T16:02:15Z`).** Developer self-review passed on 25 October 2026. Implementation commit `8e2ddcc` is published to the Admin repository's `task/ARCH-047-ADMIN-005` branch. Because `completion_mode: developer`, explicit developer completion remains pending; this task is not Complete.

### Files Changed

Admin implementation commit `8e2ddcc` reports **30 changed files**:

- `moda-interact-admin/package.json`
- `moda-interact-admin/scripts/test-arch047-admin-compilation-postgres.mjs`
- `moda-interact-admin/src/app/(protected)/system-controls/whatsapp-templates/[definitionId]/review/page.tsx`
- `moda-interact-admin/src/app/actions/whatsapp-template-compilation.ts`
- `moda-interact-admin/src/components/admin/whatsapp-templates/authoring/template-read-only-preview.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/authoring/template-saved-detail.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/compilation/component-and-variable-diff.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/compilation/conversation-wrapper-review-preview.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/compilation/meta-template-review-preview.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/compilation/review-language-selector.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/compilation/source-translation-comparison.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/compilation/translation-review-actions.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/compilation/translation-review-workspace.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/compilation/use-template-translation-review.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/contracts.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/language-codes.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/locations.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/meta-compiler.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/reads.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/reconstruction.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/repository.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/restoration.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/segments.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/service.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/compilation/wrapper-compiler.ts`
- `moda-interact-admin/tests/fixtures/arch047-translation-fixture.ts`
- `moda-interact-admin/tests/integration/arch047-template-compilation.postgres.test.ts`
- `moda-interact-admin/tests/unit/arch047-template-compilation-components.test.tsx`
- `moda-interact-admin/tests/unit/arch047-template-compilation-service.test.ts`
- `moda-interact-admin/tests/unit/arch047-template-compilation.test.ts`

No database schema, Background, Messaging, Shared implementation, or `docs/decisions/**/_index.md` files were changed by this submission.

### Work Completed

- Added Admin-owned keyed-segment parsing, source/run hash checking, protected-marker and key-multiplicity validation, typed semantic-variable restoration, and language/provider validation. Reordered variables compile with semantic bindings in the correct target-language position; altered/duplicated/dropped variables and forbidden component placements fail closed.
- Reused the ADMIN-003 pure `compileTemplateAst` authoring compiler for Meta template components and prepared conversation-wrapper projections. New locale JSONB contains the immutable authoring representation and prepared projection, with a content digest; original English content is not modified.
- Added the 20-language review workspace, the language selector, full source/target comparisons, section/variable diff, dedicated Meta and wrapper previews, review actions and controller hook. Incomplete or rejected translations remain non-publishable; `readyForPublication` requires all 20 language entries to be English source or approved.
- Added `SUPER_ADMIN`-guarded server reads and approve/reject mutation; serializable transactional finalisation with a definition row lock, content immutability, retry/idempotency behaviour, review actor/time metadata and bounded `CommerceAuditEvent` records. Rejected locale content is not saved; existing live template/wrapper selection is not mutated.
- Added translation fixtures, focused unit and React component tests, and disposable PostgreSQL tests for concurrent finalisation, audit rollback and rejection.

### Validation Results

Evidence: developer terminal transcripts `typescript(20261025-163303)` and `typescript(20261025-164645)`, supplied with the task snapshot.

| Command | Observed result |
| --- | --- |
| `npm run test:arch047-admin-compilation:unit` | **PASS — 13/13 tests**: token protection, key/source validation, language codes, positional bindings, template limits, idempotent/rejected reviews and `SUPER_ADMIN` checks. |
| `npm run test:arch047-admin-compilation:components` | **PASS — 3/3 tests**: 20-language selector, full Meta/wrapper views, immutable-content review controls. |
| `npm run test:arch047-admin-compilation:postgres` | **PASS — 3/3 disposable PostgreSQL tests**: unique/frozen concurrent finalisation, rejected review without content or live-pointer changes, and audit-failure transaction rollback. |
| `npm run build` | **PASS during this review**: Prisma Client generated, Next.js compilation, TypeScript checking and completed production build. Build emitted BullMQ optional `@valkey/valkey-glide`/dynamic-import warnings in queue-monitor and merchant-support imports; no build failure. |
| `npm run lint` | **PASS during this review (0 errors, 1 warning)**. Warning: `database/eslint.config.mjs` (`import/no-anonymous-default-export`), outside the changed implementation files. |
| `git diff --check` | **PASS during this review** on both implementation diff and parent review-record diff. |
| Implementation Git commit and push | **PASS**: `8e2ddcc` on `task/ARCH-047-ADMIN-005`, pushed to `origin/task/ARCH-047-ADMIN-005`. |

The implementer did not provide a separate focused accessibility automation report beyond the three React component checks. Those tests include accessibility-oriented selector attributes (`aria-pressed`/labels), but no independent end-to-end a11y scan is evidenced.

**Worktree evidence verified during review:** canonical launcher routes to parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-ADMIN-005` and implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-ADMIN-005`. Both are registered on `task/ARCH-047-ADMIN-005`, clean, and contain current `origin/main`; implementation HEAD `8e2ddcc7bc251597639f4138dde30a077a663707` equals `origin/task/ARCH-047-ADMIN-005`. Recursive database submodule is materialised at gitlink `3f1f50b91c9e93ff9647a3d1d7f6fd46b9b888b9`. Thus the earlier archive omission is closed by live repository/worktree verification; the launcher packet itself is not retained as a separate artifact.

### Deviations

- Attempt 2 implementation corrections resolved three TypeScript errors, an unavailable Shared import, and a PostgreSQL test-runner module condition issue. They were applied in the same **workflow Attempt 1**; no new claim was made.
- The submitted implementation commit's subject references `arch-007-admin-005`; its **actual branch, files and task identification are ARCH-047-ADMIN-005**, and the remote push succeeded. This is a commit-message typo, not a task-scope change.
- Required provider/Background integration is exercised with documented keyed-segment fixtures pending independently owned tasks, rather than claiming end-to-end cross-repository verification here.

### Assumptions

- The locally available generated Prisma Client and disposable PostgreSQL schema reflect the accepted `ARCH-047-DATABASE-001` persistence boundary.
- Translation run/source snapshots and keyed translation items are validly produced by their owning task; this task validates them at the Admin boundary. Independent Background/provider integration remains the architecture-wide system-test responsibility.
- This is a developer-executed task (`execution_mode: developer`, `completion_mode: developer`); **no acceptance or completion decision is implied** by this submission.

### Unresolved Issues

- **Review evidence to verify:** the launcher's physical-isolation/start synchronisation/recursive submodule materialisation packet and the parent task branch publication; these are not established by the provided terminal transcripts/archive alone.
- No remaining task-scoped test or build failures were shown in the supplied validation logs. The build/lint warnings above remain visible for reviewer assessment.

### Architectural Concerns

No new cross-repository schema/contract changes were introduced. The requirement to consume only keyed translation items and preserve Admin-only immutable authoring/compilation is covered by the implementation and fixture tests; final system-level interaction with the Background translator and publication tasks remains outside this task's scope.


## Architect Review

### Review Status

Developer Self-Review Passed — Attempt 1. Explicit developer completion is pending.

### Review Notes

Task scope and acceptance evidence were reconciled against the published implementation diff and task record. Route/action authorization, source/run identity checks, keyed-marker validation, compiler reuse, immutable locale finalisation, audit rollback behavior and full-language review presentation were inspected. No task-scoped acceptance gap was found. Missing standalone accessibility automation remains a minor evidence limitation; component coverage and semantic labels/pressed state are present. Existing build/lint warnings are recorded above and do not fail validation.

### Reviewed Files

All 30 implementation files in commit `8e2ddcc`, including the review route/action, compilation services, components, focused tests and disposable PostgreSQL harness. No unrelated repository or task files are changed.

### Validation Reviewed

Re-ran `npm run test:arch047-admin-compilation:unit` (13/13 pass), `npm run test:arch047-admin-compilation:components` (3/3 pass), `npm run test:arch047-admin-compilation:postgres` (3/3 pass), `npm run lint` (0 errors, 1 pre-existing warning), `npm run build` (pass with recorded BullMQ warnings), and `git diff --check` (pass).

### Architecture Conformance

Conforms to the Admin-only immutable translation review/compilation boundary. No schema, Background, Messaging, Shared, caller integration, live assignment, wrapper activation or `_index.md` changes were found. Completion remains separate from review.

### Follow-up

Developer may explicitly complete with `/moda_developer_update ARCH-047-ADMIN-005 complete`. No sibling or downstream task was started.

## Developer Self-Review - Passed

- Attempt: 1; reviewed 25 October 2026.
- Result: Passing; no known required Work Item or Acceptance Criterion remains incomplete.
- Implementation branch: `task/ARCH-047-ADMIN-005`, commit `8e2ddcc7bc251597639f4138dde30a077a663707`, pushed and clean.
- Parent task branch: `task/ARCH-047-ADMIN-005`; this review record will be committed and pushed separately.
- Completion decision: pending explicit developer action because `completion_mode: developer`; status remains `review`, attempt remains 1, executor and claim timestamp are null.

## Execution Ownership Amendment

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_admin`, coordinator, repository, dependency, task scope, acceptance criteria and validation requirements.
- Claim state: This amendment does not claim an implementation attempt; the canonical launcher records the claim after dependency and worktree preparation.
