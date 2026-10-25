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

- [ ] Server-side and editor AST rules agree on allowed component kinds, maximum bounded text/JSON size, variable names, Meta-placeholder limits, at most supported dynamic URL buttons, and wrapper `response.body` presence; reject malformed/unknown variables with precise errors.
- [ ] Save is an atomic definition + English locale write and a bounded one-time audit; fail cleanly without half-saved source. No additional language, Meta registration or merchant assignment is created on save.
- [ ] A saved template's `localeAst`, `sourceHash`, business purpose and provider name are read-only by application policy; cloning yields an independent, newly named definition. No edit control appears on saved definitions.
- [ ] No external Meta import/registration, no editor-built promises of discounts without approved typed offer bindings, no customer data exposed.


All server reads/mutations of template management require the existing authenticated platform-admin boundary; mutations and privileged cross-shop reads require **`SUPER_ADMIN`**, verified server-side (`requirePlatformAdminPage` / `requirePlatformAdminMutation` or repository-equivalent). Reject client-supplied actor identity, WABA ownership, approval and shop eligibility assertions. Persist bounded/redacted audit records using the existing `commerce.CommerceAuditEvent` and ARCH-047 audit enum; do not log tokens, credentials or unnecessary customer/checkout data. Reuse the platform's shared structured logger only for needed semantic logs.


## Work Items

- [ ] Implement AST node definitions, semantic variable registry and renderer/validator in `authoring/` with small independently testable files.
- [ ] Implement guarded pages, shared catalogue navigation, English editor and preview (responsive, keyboard-usable, clear validation and duplicate-save disable).
- [ ] Implement transactional save/clone server actions and audit with focused auth, immutability and concurrency tests.


## Interfaces / Contracts

**Writes:** `WhatsAppTemplateDefinition` and source `WhatsAppTemplateLocale`; optional `clonedFromDefinitionId` and `CommerceAuditEvent`. **Reads:** own definitions/locales and existing 20-language identity utility. The Admin-local AST JSON envelope is versioned (`schemaVersion`, template family/purpose, components or wrapper slots, semantic variables); its immutable `authoring` and `prepared` fields are stored in the English locale's `localeAst`. ADMIN-005 must reuse the same pure compiler for other languages, not duplicate it. `sourceHash` is computed over a canonical immutable source projection, never based on volatile JSON key ordering. Other Admin tasks consume this persisted definition/AST format, not a new Shared package. **No** `TranslationRun`, `MetaRegistration`, publication or active-slot writes in this task.


**Module ownership.** Keep this task modular: put its domain services under `src/lib/admin/whatsapp-templates/authoring/`, components under `src/components/admin/whatsapp-templates/authoring/`, and its server actions in a task-specific `src/app/actions/whatsapp-template-authoring.ts`. Avoid a global `whatsapp-templates.ts` catch-all or unrelated edits to sibling modules. Prefer small repository/domain, validation, orchestrator and view components. Only the English authoring task owns the shared navigation/catalogue shell; other tasks provide focused subroutes/panels, not a second editor or shell.


## Dependencies

- `ARCH-047-DATABASE-001` — **the only formal task dependency**. No `ARCH-047-ADMIN-00N`, Background, Messaging or new Shared publication dependency is permitted. Use seeded DB fixtures and injected ports to test independently when upstream/downstream implementations are absent. Status remains Pending until DB001 is confirmed Complete in the canonical task record; do not infer completion from tests alone.

## Enables

None at task-definition time. Completion of this task does not grant permission to start another task or skip an independently required system-test gate.

## Acceptance Criteria

- [ ] Six recovery purposes and three wrapper audiences are selectable, have the correct variables and usable previews; both families save atomically and appear in the catalogue.
- [ ] Unknown AST node, unbound variable, missing response slot or unsupported dynamic Meta component fails before save on the server. Duplicate submit makes at most one definition.
- [ ] Existing content cannot be edited after saving; Clone as New creates a distinct identity and does not mutate its source. No external-import action is present.
- [ ] Denied/unauthenticated caller cannot read or save across the platform; audited writes carry the actual SUPER_ADMIN actor.


## Validation

- [ ] Admin-local AST schema/variable/preview unit tests; server-auth/transaction/idempotency tests including forced rollback, and component accessibility/mobile rendering.
- [ ] Focused PostgreSQL test against the consolidated schema for definition + source locale + audit and clone; typecheck, scoped lint/tests and `git diff --check` using package scripts that actually exist.


## Stop Condition

After task-scoped work, acceptance criteria, validation and Completion Report are complete, set `status: review`, return control to `moda_architect` and **STOP**. Do not mark this task Complete yourself, start sibling/Admin/Background tasks, modify `_index.md`, merge branches or push main.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md`, `docs/developer-task-workflow.md`, the revised parent ARCH-047 architecture and current Admin repository instructions. Use launcher-prepared dedicated parent/implementation task worktrees and mirrored `task/<TASK_ID>` branches. In the Completion Report record prepared physical worktree isolation, start sync, recursive submodule materialisation, exact test commands/outcomes, changed paths and commits. The implementing agent must not modify `docs/decisions/**/_index.md`, another task, the parent architecture, another repository, or follow-on work. Reuse existing Admin Store Category AST authoring and Merchant Pricing translation UX patterns without copying their domain services or creating a competing generic runtime. Inspect the actual worktree state before implementation; the attached snapshot is not a live Git-branch guarantee.


## Completion Report

### Status

Not Started — materialised task definition; developer takeover recorded, awaiting canonical launcher preparation and claim.

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

## Developer Takeover

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-ADMIN-003` while this task was ready and agent-owned. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_admin`, coordinator, repository, dependency, scope, acceptance criteria and validation requirements.
- Claim state: This amendment does not claim an implementation attempt. The canonical launcher records the claim after worktree preparation, synchronization and dependency verification.
