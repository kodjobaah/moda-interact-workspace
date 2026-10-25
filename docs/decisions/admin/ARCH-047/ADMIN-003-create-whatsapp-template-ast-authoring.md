---
id: ARCH-047-ADMIN-003
architecture_id: ARCH-047
title: Create immutable WhatsApp templates with an Admin-owned AST editor
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

# Create immutable WhatsApp templates with an Admin-owned AST editor

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`. Coordinator: `moda_architect`. This task definition is materialised on parent branch `task/ARCH-047-ADMIN-003`; the canonical developer launcher will prepare the implementation worktree and claim execution.

## Objective

Implement the protected **English template authoring** capability, covering both Meta recovery purposes and internal AI/human conversation wrappers, using an Admin-owned AST and type-specific variables; save each finished English definition exactly once.

## Context

The adopted ARCH-047 design is **Moda Admin-only authoring**. A saved English source definition and its corresponding language content are immutable: corrections create a different definition using **Clone as New**. There are six Meta recovery purposes (`INITIAL`/`FOLLOW_UP` × `NO_OFFER`/`CODE_OFFER`/`AUTOMATIC_OFFER`) and one internally published `MODA_CONVERSATION_WRAPPER` family with `SHARED`, `AI` and `HUMAN` audiences. No template authored externally in Meta may be adopted.

`ARCH-047-DATABASE-001` defines the eleven-table persistence boundary, including `WhatsAppTemplateDefinition`, `WhatsAppTemplateLocale`, translation Run/Item/Batch/BatchItem, `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateMetaEvent`, publication Operation/Target and `WhatsAppConversationWrapperActiveSlot`, plus the nullable link to existing shop `WhatsAppTemplateVariant` and existing `CommerceAuditEvent` actions. Database stores technical relations/JSONB but does **not** enforce template lifecycle/business rules. Admin must enforce those rules transactionally. This Admin task never modifies Prisma schema or the existing database migration.

The six Admin tasks have **only `ARCH-047-DATABASE-001` as a formal dependency**. They own separate route/action/service/component modules, use stable documented persistence payloads, and must prove their capability with fixtures or injected dependencies when a sibling Admin/Background implementation is not yet complete. The end-to-end system test, not an artificial task chain, verifies their integration.


## Scope

- Own the protected catalogue and English authoring route under `src/app/(protected)/system-controls/whatsapp-templates/`, the System Controls sidebar entry/breadcrumbs, and the `authoring/` component/service module. Reuse existing Platform Admin authorisation and i18n patterns, not a new admin role.
- First select **Meta Recovery** (`INITIAL`/`FOLLOW_UP` × `NO_OFFER`/`CODE_OFFER`/`AUTOMATIC_OFFER`) or **Conversation Wrapper** (SHARED/AI/HUMAN). The selected business purpose must determine exactly which typed variables can be inserted. Use existing product locale registry for supported languages; English source language must be explicitly selected/mapped, not guessed from browser language.
- Build a type-checked visual AST authoring editor with text, semantic variable nodes, supported header/body/footer/button components and (for wrappers) one required `response.body` slot and optional checkout-aware conditional sections. Supply contextual example values and a live preview; never use real customer/checkout data in preview fixtures.
- Define one **Admin-local** versioned AST/value registry, pure compiler/projection builder, and validation contract. The pure compiler is owned once inside the Admin authoring module and is reused by ADMIN-005 for translated locales; never create a second implementation. Insert semantic identifiers such as `customer.firstName`, `shop.name`, `checkout.url`, `offer.code`, `offer.description`, not customer values or raw Meta positional variables. The six purposes expose only suitable offer variables; wrappers have optional checkout URL and required response slot. Restrict components to what existing Meta sending can bind; return incompatible new capabilities to architect rather than silently allowing them.
- Transactionally create one `WhatsAppTemplateDefinition` plus its English `WhatsAppTemplateLocale` (`localeAst` JSONB, `contentHash`, `sourceHash`, schema version and creator). Validate all authoring business rules **server-side** immediately before the save. The saved English `localeAst` must contain **both immutable authoring content and its deterministic prepared projection at creation** (e.g. `{schemaVersion,authoring,prepared}`). This includes Meta-ready English components/bindings or a wrapper-ready English projection, so a later review never needs to edit the saved English locale. Unsaved editor state may change; **saved English content may not**.
- Implement **Clone as New** by creating a fresh identity, new Meta provider template name/version when relevant, and provenance `clonedFromDefinitionId`; never update/delete in-place source/locale content or invoke Meta's edit-template endpoint. Saving must be duplicate-submit safe; a second click must not create a duplicate definition.
- Expose a stable module read interface for future subroutes: `getDefinitionDetail(id)` and an immutable, versioned authoring-record contract. Read existing definitions by ID and browse with bounded pagination; show family, purpose, source language and lifecycle honestly.


## Out of Scope

- Translation requests/jobs, result reconstruction, Meta create/list/update API calls, provider status reconciliation, bulk shop assignment, wrapper activation, recovery sends and customer checkout mutations.
- No Shared AST package or new database business constraints. Do not author translation prompts or use Background to validate the English AST.


## Requirements

- [x] Server-side and editor AST rules agree on allowed component kinds, maximum bounded text/JSON size, variable names, Meta-placeholder limits, at most supported dynamic URL buttons, and wrapper `response.body` presence; reject malformed/unknown variables with precise errors.
- [x] Save is an atomic definition + English locale write and a bounded one-time audit; fail cleanly without half-saved source. No additional language, Meta registration or merchant assignment is created on save.
- [x] A saved template's `localeAst`, `sourceHash`, business purpose and provider name are read-only by application policy; cloning yields an independent, newly named definition. No edit control appears on saved definitions.
- [x] No external Meta import/registration, no editor-built promises of discounts without approved typed offer bindings, no customer data exposed.


All server reads/mutations of template management require the existing authenticated platform-admin boundary; mutations and privileged cross-shop reads require **`SUPER_ADMIN`**, verified server-side (`requirePlatformAdminPage` / `requirePlatformAdminMutation` or repository-equivalent). Reject client-supplied actor identity, WABA ownership, approval and shop eligibility assertions. Persist bounded/redacted audit records using the existing `commerce.CommerceAuditEvent` and ARCH-047 audit enum; do not log tokens, credentials or unnecessary customer/checkout data. Reuse the platform's shared structured logger only for needed semantic logs.


## Work Items

- [x] Implement AST node definitions, semantic variable registry and renderer/validator in `authoring/` with small independently testable files.
- [x] Implement guarded pages, shared catalogue navigation, English editor and preview (responsive, keyboard-usable, clear validation and duplicate-save disable).
- [x] Implement transactional save/clone server actions and audit with focused auth, immutability and concurrency tests.


## Interfaces / Contracts

**Writes:** `WhatsAppTemplateDefinition` and source `WhatsAppTemplateLocale`; optional `clonedFromDefinitionId` and `CommerceAuditEvent`. **Reads:** own definitions/locales and existing 20-language identity utility. The Admin-local AST JSON envelope is versioned (`schemaVersion`, template family/purpose, components or wrapper slots, semantic variables); its immutable `authoring` and `prepared` fields are stored in the English locale's `localeAst`. ADMIN-005 must reuse the same pure compiler for other languages, not duplicate it. `sourceHash` is computed over a canonical immutable source projection, never based on volatile JSON key ordering. Other Admin tasks consume this persisted definition/AST format, not a new Shared package. **No** `TranslationRun`, `MetaRegistration`, publication or active-slot writes in this task.


**Module ownership.** Keep this task modular: put its domain services under `src/lib/admin/whatsapp-templates/authoring/`, components under `src/components/admin/whatsapp-templates/authoring/`, and its server actions in a task-specific `src/app/actions/whatsapp-template-authoring.ts`. Avoid a global `whatsapp-templates.ts` catch-all or unrelated edits to sibling modules. Prefer small repository/domain, validation, orchestrator and view components. Only the English authoring task owns the shared navigation/catalogue shell; other tasks provide focused subroutes/panels, not a second editor or shell.


## Dependencies

- `ARCH-047-DATABASE-001` — **the only formal task dependency**. No `ARCH-047-ADMIN-00N`, Background, Messaging or new Shared publication dependency is permitted. Use seeded DB fixtures and injected ports to test independently when upstream/downstream implementations are absent. Status remains Pending until DB001 is confirmed Complete in the canonical task record; do not infer completion from tests alone.

## Enables

None at task-definition time. Completion of this task does not grant permission to start another task or skip an independently required system-test gate.

## Acceptance Criteria

- [x] Six recovery purposes and three wrapper audiences are selectable, have the correct variables and usable previews; both families save atomically and appear in the catalogue.
- [x] Unknown AST node, unbound variable, missing response slot or unsupported dynamic Meta component fails before save on the server. Duplicate submit makes at most one definition.
- [x] Existing content cannot be edited after saving; Clone as New creates a distinct identity and does not mutate its source. No external-import action is present.
- [x] Denied/unauthenticated caller cannot read or save across the platform; audited writes carry the actual SUPER_ADMIN actor.


## Validation

- [x] Admin-local AST schema/variable/preview unit tests; server-auth/transaction/idempotency tests including forced rollback, and component accessibility/mobile rendering.
- [x] Focused PostgreSQL test against the consolidated schema for definition + source locale + audit and clone; typecheck, scoped lint/tests and `git diff --check` using package scripts that actually exist.


## Stop Condition

After task-scoped work, acceptance criteria, validation and Completion Report are complete, set `status: review`, return control to `moda_architect` and **STOP**. Do not mark this task Complete yourself, start sibling/Admin/Background tasks, modify `_index.md`, merge branches or push main.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md`, `docs/developer-task-workflow.md`, the revised parent ARCH-047 architecture and current Admin repository instructions. Use launcher-prepared dedicated parent/implementation task worktrees and mirrored `task/<TASK_ID>` branches. In the Completion Report record prepared physical worktree isolation, start sync, recursive submodule materialisation, exact test commands/outcomes, changed paths and commits. The implementing agent must not modify `docs/decisions/**/_index.md`, another task, the parent architecture, another repository, or follow-on work. Reuse existing Admin Store Category AST authoring and Merchant Pricing translation UX patterns without copying their domain services or creating a competing generic runtime. Inspect the actual worktree state before implementation; the attached snapshot is not a live Git-branch guarantee.


## Completion Report

### Status

Ready for Architect Review — developer Attempt 1 passed self-review on 2026-10-25. Required focused tests, disposable PostgreSQL integration, TypeScript, production lint and diff checks passed. The implementation branch is pushed; the unrelated untracked `typescript` log was left untouched and is not part of the task changes. Completion mode remains developer, so this review does not complete the task.

### Files Changed

`moda-interact-admin/` implementation branch (cumulative Attempts 1–4):

- `package.json` and `scripts/test-arch047-admin-authoring-postgres.mjs` — focused validation scripts.
- `src/app/(protected)/system-controls/whatsapp-templates/page.tsx` and `src/app/actions/whatsapp-template-authoring.ts` — guarded catalogue, authoring route and server action.
- `src/components/admin/admin-shell.tsx` and `src/components/admin/sidebar.tsx` — catalogue navigation.
- `src/components/admin/whatsapp-templates/authoring/` — all 18 task-owned editor, step navigation, preview, palette, catalogue and read-only detail modules.
- `src/lib/admin/whatsapp-templates/authoring/` — AST/types, registry, compiler, validation, preview, canonical hashing, repository, service and reads modules.
- `tests/unit/arch047-template-authoring-{ast,components,service}.test.ts[x]` — focused authoring/component/transaction service tests; Attempt 4 changes only the AST fixture.
- `tests/integration/arch047-template-authoring.postgres.test.ts` — disposable PostgreSQL create/clone/replay/audit/rollback scenarios.
- `src/components/admin/whatsapp-templates/authoring/use-template-authoring-draft.ts` — Attempt 1 final correction adds the current draft to preview memo dependencies so invalid-draft previews refresh correctly.

Parent task file: this Completion Report and checklists only. No `_index.md`, sibling Admin task or Background implementation changes are part of this handoff.

### Work Completed

- Implemented an Admin-only, versioned English AST with purpose-specific semantic variables and one reusable pure compiler for future translated locales.
- Implemented six Meta recovery purposes and three wrapper audiences, including response slot/checkout conditional rules, immutable prepared English projections and server validation.
- Delivered protected full-width catalogue and three-step Setup / Compose / Review & Save editor, keyboard-usable insertion controls, contextual ShopBrand variables, nonblocking example preview and Clone as New.
- Implemented transactional definition/source-locale/audit creation, duplicate-submit protection, immutable read-only saved view and deterministic provider template naming.
- Corrected the Attempt 3 AST test's union-typed `body` fixture without changing production code; Meta test bodies now contain only `ContentNode`s while wrapper tests retain the required `response.body` slot.
- Corrected the preview hook's missing `draft` dependency after scoped lint identified a stale-preview risk; the focused authoring suite passed again after the correction.

### Validation Results

- `npm run test:arch047-admin-authoring:unit`: **28 passed, 0 failed**, rerun after the preview-hook correction.
- `npm run test:arch047-admin-authoring:postgres`: **2 passed, 0 failed** against the disposable Docker PostgreSQL fixture; the harness refused external-database mode and removed its container after create/clone/replay/audit/rollback coverage.
- `npx tsc --noEmit -p tsconfig.json`: passed after the fixture and preview-hook corrections.
- Scoped `npx eslint` on task production files: passed with no warnings after the preview-hook correction. The broader initial lint invocation also named ignored test files; those ignore notices were avoided by rerunning on production files only.
- `git diff --check`: passed after the final implementation correction.
- Implementation commit `3844f22e3ce6b911d430b8dca6326e0d263b5f17` is pushed to `origin/task/ARCH-047-ADMIN-003`. The implementation worktree is on that branch with no tracked changes; an untracked `typescript` log remains and was not inspected, staged, or modified.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-ADMIN-003`, branch `task/ARCH-047-ADMIN-003`, current head `7d1b01a21a8bd23a9e38e01c24dfb0753742a8c7`, synchronized with its origin task branch at inspection.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-ADMIN-003`, branch `task/ARCH-047-ADMIN-003`, current head `3844f22e3ce6b911d430b8dca6326e0d263b5f17`; recursive submodule status is clean at `database` commit `3f1f50b91c9e93ff9647a3d1d7f6fd46b9b888b9`. Both branches include their respective `origin/main` histories; neither task branch was merged to main.
- Launcher-start synchronization details were not present in the task record available during this reconciliation; the above branch heads and current synchronization were checked directly.

### Deviations

User-approved within-task authoring refinements: catalogue separated from editor, Setup/Compose/Review navigation, live preview with inline semantic token insertion, and nullable `ShopBrand` text-variable bindings. Runtime per-shop resolution, translations and Meta publication remain outside this task.

### Assumptions

The accepted `ARCH-047-DATABASE-001` schema remains canonical. Preview values are fictional, and nullable ShopBrand field availability must be checked by the eventual delivery runtime. No Meta provider calls or merchant assignment occur during Admin source save.

### Unresolved Issues

No known task-scoped implementation or validation issue remains. The untracked `typescript` log is outside the committed task diff and was preserved. Architect review remains pending.

### Architectural Concerns

The English prepared AST now exposes ShopBrand semantic bindings. Their shop-scoped runtime resolution is a separate ARCH-047 Background contract and must not be claimed as implemented by ADMIN-003; no Background task is modified here.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Developer Self-Review Passed (Attempt 1)

### Review Outcome

Attempt 1 passes developer self-review. The implementation satisfies the task scope and checked acceptance criteria. The focused authoring tests, disposable PostgreSQL integration, TypeScript check, scoped production lint and `git diff --check` all pass after the final correction. The implementation task branch is pushed. Because `completion_mode: developer`, this passing review returns the task to `review`; explicit developer completion remains pending.

### Corrections and Validation

- Fixed the Attempt 3 union-typed AST fixture in Attempt 4; the current full focused unit suite passes 28/28.
- Added `draft` to the preview memo dependency after lint identified that invalid-draft preview state could otherwise become stale; focused tests pass after the change.
- The disposable PostgreSQL suite passes 2/2, TypeScript passes, scoped production lint passes without warnings, and `git diff --check` passes.

### Git and Worktree Evidence

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-ADMIN-003`, branch `task/ARCH-047-ADMIN-003`.
- Implementation task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-ADMIN-003`, branch `task/ARCH-047-ADMIN-003`.
- Implementation head `3844f22e3ce6b911d430b8dca6326e0d263b5f17` is pushed. This parent task record is committed and pushed with the review transition. The implementation worktree retains an unrelated untracked `typescript` log, which was not staged or altered.

### State

`status: review`, `executor: null`, `claimed_at: null`, `attempt: 1`. No explicit developer completion decision was made. No task branch was merged to `main`.

## Developer Takeover

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-ADMIN-003` while this task was ready and agent-owned. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_admin`, coordinator, repository, dependency, scope, acceptance criteria and validation requirements.
- Claim state: This amendment does not claim an implementation attempt. The canonical launcher records the claim after worktree preparation, synchronization and dependency verification.
