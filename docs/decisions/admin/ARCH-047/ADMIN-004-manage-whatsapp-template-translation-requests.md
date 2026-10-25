---
id: ARCH-047-ADMIN-004
architecture_id: ARCH-047
title: Prepare keyed translation runs and display durable progress
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-DATABASE-001
enables: []
created: 2026-10-24
updated: 2026-10-25
---

# Prepare keyed translation runs and display durable progress

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`. Coordinator: `moda_architect`. This is a **defined but not materialised** task until the developer's launcher creates the canonical task branch/worktree.

## Objective

Implement Admin-owned **translation request preparation and progress UI** for saved English templates, without translating or interpreting the English AST in Background.

## Context

The adopted ARCH-047 design is **Moda Admin-only authoring**. A saved English source definition and its corresponding language content are immutable: corrections create a different definition using **Clone as New**. There are six Meta recovery purposes (`INITIAL`/`FOLLOW_UP` × `NO_OFFER`/`CODE_OFFER`/`AUTOMATIC_OFFER`) and one internally published `MODA_CONVERSATION_WRAPPER` family with `SHARED`, `AI` and `HUMAN` audiences. No template authored externally in Meta may be adopted.

`ARCH-047-DATABASE-001` defines the eleven-table persistence boundary, including `WhatsAppTemplateDefinition`, `WhatsAppTemplateLocale`, translation Run/Item/Batch/BatchItem, `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateMetaEvent`, publication Operation/Target and `WhatsAppConversationWrapperActiveSlot`, plus the nullable link to existing shop `WhatsAppTemplateVariant` and existing `CommerceAuditEvent` actions. Database stores technical relations/JSONB but does **not** enforce template lifecycle/business rules. Admin must enforce those rules transactionally. This Admin task never modifies Prisma schema or the existing database migration.

The six Admin tasks have **only `ARCH-047-DATABASE-001` as a formal dependency**. They own separate route/action/service/component modules, use stable documented persistence payloads, and must prove their capability with fixtures or injected dependencies when a sibling Admin/Background implementation is not yet complete. The end-to-end system test, not an artificial task chain, verifies their integration.


## Scope

- Own translation request creation, status reads and retry-action UI under `src/lib/admin/whatsapp-templates/translations/`, `src/components/admin/whatsapp-templates/translations/` and `src/app/(protected)/system-controls/whatsapp-templates/[definitionId]/translations/`.
- Read a saved English definition/locale and extract **stable keyed text segments** from supported translatable locations: text header, body, footer and button labels for Meta; wrapper header/footer/conditional display text for wrappers. Do not translate template names, category, Meta language codes, semantic variable identifiers, button URLs or runtime response body.
- Treat the eight `ShopBrand` text-use semantic keys authored by ADMIN-003 as protected variables: `shopBrand.brandName`, `shopBrand.logoUrl`, `shopBrand.logoAltText`, `shopBrand.logoWidth`, `shopBrand.logoHeight`, `shopBrand.squareLogoUrl`, `shopBrand.squareLogoAltText` and `shopBrand.coverImageUrl`. These are **variable identifiers**, not live merchant values or translatable prose. Protect every occurrence, including a Meta text-header variable (where supported), body variables and wrapper header/footer/conditional text variables. Meta footer content remains static text; `response.body` is a structural insertion slot and must never become a translation segment. Preserve ADMIN-003's component-specific allowlists and header restrictions rather than granting every key every placement.
- Produce a bounded, versioned `sourceSnapshot` JSONB with `definitionId`, `sourceHash`, `sourceLanguageTag`, `schemaVersion` and `segments:[{key,text,protectedTokens}]`. Each key is a deterministic path or AST node ID; placeholder occurrences use unique **opaque protected markers**, with an explicit map from each marker to its semantic variable, so translated words can reorder variables without changing meaning.
- Transactionally create one `WhatsAppTemplateTranslationRun` and **19** `WhatsAppTemplateTranslationItem` rows using the model configuration chosen by the established Admin translation configuration; ensure durable source hash/model identity, per-language technical identity and no translation before the immutable English locale has committed. Duplicate requests do not generate a second active run for the same source/configuration; use application serialisation/idempotency.
- The request is picked up asynchronously by `BACKGROUND-002` using the existing Batch worker mechanisms. **Do not call Background synchronously, translate inside an Admin action or invent a new cross-service queue schema.** If operational wake-up is required, use an existing approved handoff, with the database remaining durable truth.
- UI shows `SAVED`, `TRANSLATION_QUEUED`, `TRANSLATING`, `PARTIALLY_FAILED`, `READY_FOR_REVIEW` from persisted run/item status. Show 1 English source + 19 language results distinctly, counts, per-language failure and bounded refresh (auto-poll only while active and stop on selection/unmount). The retry action requests only failed/pending work using the persisted fields; Background owns retry execution and provider Batch correlation.


### Required React component decomposition

Use a thin protected Server Component route and **separate** client components under `src/components/admin/whatsapp-templates/translations/`:

- `TemplateTranslationWorkspace` — composes the view without executing translation operations.
- `TranslationRequestControls` — explicit Generate/Retry actions and duplicate-request disable.
- `TranslationProgressSummary` — English source + 19 target counts/states.
- `TranslationLocaleStatusList` — paginated/scroll-safe per-locale progress and failure reasons.
- `TranslationRunErrorNotice` — actionable failures and configuration guidance.

Place polling, request/retry state, stale-response cancellation and selection-aware refresh in a dedicated `useTemplateTranslationRun` hook/controller. Automatic polling is enabled only for an active run, stops on unmount or while the administrator is inspecting a selected result, and must not create duplicate starts. Segment extraction, protected-marker assignment, source-hash calculation and transaction handling stay in separate **pure helpers and server-side service/repository files** under `src/lib/admin/whatsapp-templates/translations/`. The task-specific action is a thin authenticated adapter. JSX components must not contain provider Batch logic, Prisma queries or segment-extraction algorithms.

## Out of Scope

- No AST redesign, new translation engine, provider Batch submit/poll, translated content reconstruction, Meta submission or wrapper/shop publication.
- Do not create a per-segment database table or rename existing `TranslationItem.translatedAst`; it stores the keyed translated segments until Admin reconstructs them.


## Requirements

- [ ] The source snapshot contains exactly one stable entry per translatable component and protected token occurrences without leaking actual customer values or secrets; duplicate/missing segment keys are rejected on request creation.
- [ ] Repeated `shopBrand.*` tokens remain independently protected, with stable semantic identifiers and unique per-occurrence opaque markers; translations cannot replace them with a preview value, a merchant's real branding, or a translated identifier.
- [ ] A verified source hash and immutable source locale are captured; a later clone cannot receive an older run's outputs. Per-language progress comes from persisted items, not simulated UI state.
- [ ] Translation request write and model identity assignment are atomic; repeated start/retry is idempotent and does not discard completed languages.


All server reads/mutations of template management require the existing authenticated platform-admin boundary; mutations and privileged cross-shop reads require **`SUPER_ADMIN`**, verified server-side (`requirePlatformAdminPage` / `requirePlatformAdminMutation` or repository-equivalent). Reject client-supplied actor identity, WABA ownership, approval and shop eligibility assertions. Persist bounded/redacted audit records using the existing `commerce.CommerceAuditEvent` and ARCH-047 audit enum; do not log tokens, credentials or unnecessary customer/checkout data. Reuse the platform's shared structured logger only for needed semantic logs.


## Work Items

- [ ] Implement pure extraction/token-marker helpers with deterministic fixtures for header/body/footer/buttons and wrapper conditionals.
- [ ] Exercise the ADMIN-003 variable registry for allowed `shopBrand.*` placements; protect Meta text-header/body and wrapper header/footer/conditional tokens while leaving Meta footers, URLs and the wrapper response slot unmodified.
- [ ] Implement transactional run/item creation, deduplicated request action, progress/list/retry endpoints and bounded polling UI.
- [ ] Add tests for duplicate starts, 19 target items, exact source-hash binding and meaningful failed/queued states.


## Interfaces / Contracts

**Reads:** immutable English `WhatsAppTemplateLocale.localeAst`, definition, configured translation-model record. **Writes:** `WhatsAppTemplateTranslationRun.sourceSnapshot` and `WhatsAppTemplateTranslationItem` rows; status/progress UI reads Run/Item/Batch/BatchItem. Background's agreed contract is `{schemaVersion:1,segments:[{key:string,text:string,protectedTokens:[{marker:string,variable:string}]}]}` for source and `{schemaVersion:1,segments:[{key:string,text:string}]}` in `TranslationItem.translatedAst`. Protected marker strings are opaque and unique **per occurrence**, including two occurrences of the same `shopBrand.*` key. The `variable` field retains the canonical `shopBrand.*` identifier, never a `ShopBrand` value. The compiler/reconstructor module (ADMIN-005) owns reinsertion of results by `key`. The database schema stays unchanged.


**Module ownership.** Keep this task modular: put its domain services under `src/lib/admin/whatsapp-templates/translations/`, components under `src/components/admin/whatsapp-templates/translations/`, and its server actions in a task-specific `src/app/actions/whatsapp-template-translations.ts`. Avoid a global `whatsapp-templates.ts` catch-all or unrelated edits to sibling modules. Prefer small repository/domain, validation, orchestrator and view components. Only the English authoring task owns the shared navigation/catalogue shell; other tasks provide focused subroutes/panels, not a second editor or shell.


## Dependencies

- `ARCH-047-DATABASE-001` — **the only formal task dependency**. No `ARCH-047-ADMIN-00N`, Background, Messaging or new Shared publication dependency is permitted. Use seeded DB fixtures and injected ports to test independently when upstream/downstream implementations are absent. Status remains Pending until DB001 is confirmed Complete in the canonical task record; do not infer completion from tests alone.

## Enables

None at task-definition time. Completion of this task does not grant permission to start another task or skip an independently required system-test gate.

## Acceptance Criteria

- [ ] React views are composed from separately named, independently testable components; route pages, controller hooks, pure domain helpers, server actions and database services are in separate files with no monolithic screen/action implementation.

- [ ] Saving an English template does not implicitly translate; explicit Generate persists one run and exactly 19 target-language items for supported target locales.
- [ ] Source snapshots use stable component keys; source text markers survive opaque variable contract; untranslatable URLs, metadata and response slot never become translation work.
- [ ] Header/body and wrapper translatable segments protect all supported `shopBrand.*` identifiers without leaking merchant-specific values; unsupported Meta footer variables are rejected by the source authoring contract, not silently included as translation work.
- [ ] Progress, partial failures and retry controls reflect PostgreSQL; reloading/navigation does not lose progress or cause an extra run.
- [ ] Repeated concurrent requests do not produce duplicate active work, and are audited and SUPER_ADMIN-only.


## Validation

- [ ] Pure keyed-segment extraction/marker tests (including repeated brand name, brand alt text, header/body placement and wrapper footer/conditional text); 20-locale mapping fixtures; Admin route/action auth/duplicate-submit tests.
- [ ] Database integration tests for run/items creation and idempotent retry requests using stubbed Background statuses; relevant lint/typecheck/build and `git diff --check`.


## Stop Condition

After task-scoped work, acceptance criteria, validation and Completion Report are complete, set `status: review`, return control to `moda_architect` and **STOP**. Do not mark this task Complete yourself, start sibling/Admin/Background tasks, modify `_index.md`, merge branches or push main.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md`, `docs/developer-task-workflow.md`, the revised parent ARCH-047 architecture and current Admin repository instructions. Use launcher-prepared dedicated parent/implementation task worktrees and mirrored `task/<TASK_ID>` branches. In the Completion Report record prepared physical worktree isolation, start sync, recursive submodule materialisation, exact test commands/outcomes, changed paths and commits. The implementing agent must not modify `docs/decisions/**/_index.md`, another task, the parent architecture, another repository, or follow-on work. Reuse existing Admin Store Category AST authoring and Merchant Pricing translation UX patterns without copying their domain services or creating a competing generic runtime. Inspect the actual worktree state before implementation; the attached snapshot is not a live Git-branch guarantee.


## Completion Report

### Status

Not Started — portable task definition, not materialised/claimed.

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
