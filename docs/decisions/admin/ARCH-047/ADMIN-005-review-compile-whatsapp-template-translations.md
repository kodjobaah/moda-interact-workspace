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
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-25T16:02:15Z
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

- [ ] Reconstruct only when persisted source hash matches its translation run; late provider results and stale clones cannot overwrite accepted content.
- [ ] Protected token multisets and component-key sets must match exactly; translation may reorder variables, compiler must derive correct per-language positional binding snapshots.
- [ ] Meta header/body and wrapper header/footer/conditional `shopBrand.*` references survive reconstruction as typed identifiers, with no merchant data captured during translation or compilation; invalid component/key combinations fail validation.
- [ ] English and all 19 translations are previewable; if rejected/malformed, locale stays unapproved with actionable diagnostics and does not silently become publishable.
- [ ] Review writes are idempotent, guarded and audited. Template text changes always require a new definition; metadata/progress may update independently.


All server reads/mutations of template management require the existing authenticated platform-admin boundary; mutations and privileged cross-shop reads require **`SUPER_ADMIN`**, verified server-side (`requirePlatformAdminPage` / `requirePlatformAdminMutation` or repository-equivalent). Reject client-supplied actor identity, WABA ownership, approval and shop eligibility assertions. Persist bounded/redacted audit records using the existing `commerce.CommerceAuditEvent` and ARCH-047 audit enum; do not log tokens, credentials or unnecessary customer/checkout data. Reuse the platform's shared structured logger only for needed semantic logs.


## Work Items

- [ ] Implement typed, Admin-local reconstruction/validation and consume ADMIN-003's deterministic provider/wrapper compiler and variable registry via a focused adapter/fixtures; do not add a competing compiler.
- [ ] Implement review screen with English/current-language side-by-side previews, variable/button comparison and approve/reject actions.
- [ ] Add transactional locale finalisation and audit with stale/duplicate/concurrent review tests.


## Interfaces / Contracts

**Inputs:** `TranslationRun.sourceSnapshot` with keyed protected source segments; `TranslationItem.translatedAst` with keyed translated segments; English `TemplateLocale.localeAst`. **Writes:** 19 finished `WhatsAppTemplateLocale` rows, each `localeAst` containing its complete authoring structure **plus prepared runtime/provider projection**; `contentHash`, review metadata and bounded audit. **Prepared Meta envelope example (illustrative; emit the canonical ADMIN-003 compiler shape):** `{schemaVersion:1, category:'MARKETING', components:[...], parameterBindings:{header:[{position:1,variable:'shopBrand.brandName'}],body:[{position:1,variable:'customer.firstName'}],buttons:[...]}, contentHash:'...'}`. Header bindings are present only for a variable-bearing header; brand values themselves are never frozen.  For conversation wrappers use `{schemaVersion:1, header:[...], responseSlot:'response.body', footer:[...], conditionals:[...], variableBindings:[...]}`. These JSON payload formats are Admin-owned persistence contracts, not a separate Shared implementation. This task **does not create MetaRegistration**; ADMIN-006 freezes copies only on confirmed submission.


**Module ownership.** Keep this task modular: put its domain services under `src/lib/admin/whatsapp-templates/compilation/`, components under `src/components/admin/whatsapp-templates/compilation/`, and its server actions in a task-specific `src/app/actions/whatsapp-template-compilation.ts`. Avoid a global `whatsapp-templates.ts` catch-all or unrelated edits to sibling modules. Prefer small repository/domain, validation, orchestrator and view components. Only the English authoring task owns the shared navigation/catalogue shell; other tasks provide focused subroutes/panels, not a second editor or shell.


## Dependencies

- `ARCH-047-DATABASE-001` — **the only formal task dependency**. No `ARCH-047-ADMIN-00N`, Background, Messaging or new Shared publication dependency is permitted. Use seeded DB fixtures and injected ports to test independently when upstream/downstream implementations are absent. Status remains Pending until DB001 is confirmed Complete in the canonical task record; do not infer completion from tests alone.

## Enables

None at task-definition time. Completion of this task does not grant permission to start another task or skip an independently required system-test gate.

## Acceptance Criteria

- [ ] React views are composed from separately named, independently testable components; route pages, controller hooks, pure domain helpers, server actions and database services are in separate files with no monolithic screen/action implementation.

- [ ] Each language's complete preview and durable metadata reflect the same validated source; exactly 20 reviewed locales are required by application policy before the definition is eligible for the relevant publication path.
- [ ] Header/body/footer/buttons and wrapper conditional segments map correctly; missing/duplicate/prohibited variable markers block reconstruction; reordered variables bind to the intended semantic values.
- [ ] Translated Meta headers retain their header position and `shopBrand.*` semantic key (where allowed); wrapper brand keys remain available in permitted header/footer/conditional slots, while Meta footers contain no variable bindings.
- [ ] Approved locales contain Meta-ready or wrapper-ready projection with no dependency on a Background AST compiler. No content mutation of saved/approved templates occurs.
- [ ] Rejection leaves prior live template assignments/active wrapper pointers unchanged; only newly authored content may replace them later.


## Validation

- [ ] Token protection/reordering and variable-binding compiler unit tests for English/French/German and scripts with changed placeholder order; include Meta text-header `shopBrand.brandName`, body references, repeated brand variables, wrapper footer brand values, forbidden Meta footer tokens, button/URL protections and malformed translator responses.
- [ ] Admin UI full-preview/a11y tests; PostgreSQL idempotent locale finalisation/auth/audit tests using fixture translation items; lint/typecheck/`git diff --check`.


## Stop Condition

After task-scoped work, acceptance criteria, validation and Completion Report are complete, set `status: review`, return control to `moda_architect` and **STOP**. Do not mark this task Complete yourself, start sibling/Admin/Background tasks, modify `_index.md`, merge branches or push main.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md`, `docs/developer-task-workflow.md`, the revised parent ARCH-047 architecture and current Admin repository instructions. Use launcher-prepared dedicated parent/implementation task worktrees and mirrored `task/<TASK_ID>` branches. In the Completion Report record prepared physical worktree isolation, start sync, recursive submodule materialisation, exact test commands/outcomes, changed paths and commits. The implementing agent must not modify `docs/decisions/**/_index.md`, another task, the parent architecture, another repository, or follow-on work. Reuse existing Admin Store Category AST authoring and Merchant Pricing translation UX patterns without copying their domain services or creating a competing generic runtime. Inspect the actual worktree state before implementation; the attached snapshot is not a live Git-branch guarantee.


## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-25T16:02:15Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The consolidated `ARCH-047-DATABASE-001` Attempt 7 model contract is the intended schema; inspect generated Prisma Client and actual accepted database implementation when this task becomes executable. Where the proposed JSONB envelopes are not yet implemented, fixture-based tests use the explicitly documented shape.

### Unresolved Issues

None at definition time. Return any missing persistence capability, provider-account configuration or cross-repository interface problem to `moda_architect` rather than silently changing DB/Background/Messaging ownership.

### Architectural Concerns

None at definition time.


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

## Execution Ownership Amendment

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_admin`, coordinator, repository, dependency, task scope, acceptance criteria and validation requirements.
- Claim state: This amendment does not claim an implementation attempt; the canonical launcher records the claim after dependency and worktree preparation.
