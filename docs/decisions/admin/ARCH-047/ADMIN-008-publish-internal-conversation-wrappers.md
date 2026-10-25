---
id: ARCH-047-ADMIN-008
architecture_id: ARCH-047
title: Approve and activate internal AI and human conversation wrappers
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

# Approve and activate internal AI and human conversation wrappers

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`. Coordinator: `moda_architect`. This is a **defined but not materialised** task until the developer's launcher creates the canonical task branch/worktree.

## Objective

Provide internal review and explicit activation of prepared, multilingual conversation wrappers for `SHARED`, `AI` and `HUMAN` response sources, without any Meta submission or merchant assignment.

## Context

The adopted ARCH-047 design is **Moda Admin-only authoring**. A saved English source definition and its corresponding language content are immutable: corrections create a different definition using **Clone as New**. There are six Meta recovery purposes (`INITIAL`/`FOLLOW_UP` × `NO_OFFER`/`CODE_OFFER`/`AUTOMATIC_OFFER`) and one internally published `MODA_CONVERSATION_WRAPPER` family with `SHARED`, `AI` and `HUMAN` audiences. No template authored externally in Meta may be adopted.

`ARCH-047-DATABASE-001` defines the eleven-table persistence boundary, including `WhatsAppTemplateDefinition`, `WhatsAppTemplateLocale`, translation Run/Item/Batch/BatchItem, `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateMetaEvent`, publication Operation/Target and `WhatsAppConversationWrapperActiveSlot`, plus the nullable link to existing shop `WhatsAppTemplateVariant` and existing `CommerceAuditEvent` actions. Database stores technical relations/JSONB but does **not** enforce template lifecycle/business rules. Admin must enforce those rules transactionally. This Admin task never modifies Prisma schema or the existing database migration.

The six Admin tasks have **only `ARCH-047-DATABASE-001` as a formal dependency**. They own separate route/action/service/component modules, use stable documented persistence payloads, and must prove their capability with fixtures or injected dependencies when a sibling Admin/Background implementation is not yet complete. The end-to-end system test, not an artificial task chain, verifies their integration.


## Scope

- Own `wrappers/` module and `/system-controls/whatsapp-templates/wrappers/` route/panel. Consume existing definition/locale records and the **Admin-compiled prepared runtime wrapper projection** in `TemplateLocale.localeAst`; never implement a second editor, translation extraction or AST compiler.
- A wrapper has a required `response.body` insertion slot, optional header/footer, typed shop/customer/**`ShopBrand`** variables and checkout-aware conditional URL sections. Consume the canonical eight `shopBrand.*` keys from ADMIN-003's versioned prepared bindings, including permitted header/footer/conditional text placements; do not introduce an alternate wrapper AST/compiler or inline branding into the saved projection. `response.body` is a runtime insertion slot, not a translatable or stored brand value. Provide a full example preview using an illustrative AI/human response and clearly labelled **example** brand values; where a merchant-scoped preview is offered, use that shop's `ShopBrand` only and flag missing nullable fields rather than inventing or crossing tenant values. Omit disabled/stale checkout-link sections. The inserted response is authored by AI/human at runtime, **never** stored in the template.
- Enforce application-only publication checks: centrally created template, correct wrapper kind/audience, immutable source/review hashes, all expected 20 reviewed locales and presence of a validated prepared runtime projection. No Meta registration or marketing template approval is required.
- Explicit SUPER_ADMIN action selects activation audience(s): `SHARED` default, optional `AI` and `HUMAN` override. For each audience update `WhatsAppConversationWrapperActiveSlot.definitionId` with an optimistic compare-and-swap `editVersion` and transactional audit; no database business CHECK or second pointer table. Do not overwrite a concurrent newer activation without re-review.
- Show existing versus proposed full wrapper (header, response slot, footer and conditional checkout link) in the selected language with audience, first-published time and rollback/replace impact. A new version is created with Clone as New; changing an active template's content in place is forbidden. An older already-reviewed definition can be reactivated through an explicit audited action without modifying its content.
- Publishing is a platform-level pointer change, **not** copying 20 wrappers into every Shop. Background owns SHARED/AI/HUMAN fallback precedence and final rendering/send eligibility. Admin must not create out-of-window Meta sends or modify the customer checkout.


## Out of Scope

- No Meta template submission/status, per-shop recovery assignments, Background AST rendering, AI generation, human message authorship, moderation or checkout mutations.


## Requirements

- [ ] Exactly one row per activated audience is maintained via technical `audience` PK and versioned CAS; semantic audience-kind/approval checks live in Admin.
- [ ] No `response.body` insertion slot, invalid projection, unmatched 20 languages or incorrect family prevents activation; existing pointer remains unchanged on failure.
- [ ] Validated wrapper projections keep `shopBrand.*` bindings typed in allowed header/footer/conditional sections for all 20 locales, with no merchant value frozen into the central definition or active pointer. Validation rejects unknown keys and disallowed placements; missing optional merchant branding is not silently invented.
- [ ] The global `SHARED` pointer is fallback; optional AI/HUMAN overrides are explicitly selected and the UI shows which audience resolves to which definition.


All server reads/mutations of template management require the existing authenticated platform-admin boundary; mutations and privileged cross-shop reads require **`SUPER_ADMIN`**, verified server-side (`requirePlatformAdminPage` / `requirePlatformAdminMutation` or repository-equivalent). Reject client-supplied actor identity, WABA ownership, approval and shop eligibility assertions. Persist bounded/redacted audit records using the existing `commerce.CommerceAuditEvent` and ARCH-047 audit enum; do not log tokens, credentials or unnecessary customer/checkout data. Reuse the platform's shared structured logger only for needed semantic logs.


## Work Items

- [ ] Implement activation eligibility/compare-and-swap and audit service for current pointers in `wrappers/`.
- [ ] Create review/activation preview (including brand-variable labels/example substitutions and missing-value disclosure) and concurrency/conflict UI without duplicating `authoring/` or `compilation/`.
- [ ] Add audited activation/replacement/reactivation and unsafe/invalid projection tests using stubbed compiled locale records.


## Interfaces / Contracts

**Reads:** `WhatsAppTemplateDefinition`/20 reviewed `WhatsAppTemplateLocale` prepared `localeAst` projections and existing `WhatsAppConversationWrapperActiveSlot`. Prepared projections carry canonical `shopBrand.*` references for the eligible wrapper sections; any optional merchant-context preview reads `ShopBrand` only under the requested shop scope and never persists its values into centrally activated content. **Writes:** slot `definitionId`, `editVersion`, `updatedByAdminId`, `updatedAt`, optionally definition `publishedAt` for first successful activation, and bounded `CommerceAuditEvent`. No `MetaRegistration`, `PublicationTarget` or `WhatsAppTemplateVariant` writes. Consumer `BACKGROUND-005` reads the prepared projection only; no Background authoring AST parser is required.


**Module ownership.** Keep this task modular: put its domain services under `src/lib/admin/whatsapp-templates/wrappers/`, components under `src/components/admin/whatsapp-templates/wrappers/`, and its server actions in a task-specific `src/app/actions/whatsapp-template-wrapper-publication.ts`. Avoid a global `whatsapp-templates.ts` catch-all or unrelated edits to sibling modules. Prefer small repository/domain, validation, orchestrator and view components. Only the English authoring task owns the shared navigation/catalogue shell; other tasks provide focused subroutes/panels, not a second editor or shell.


## Dependencies

- `ARCH-047-DATABASE-001` — **the only formal task dependency**. No `ARCH-047-ADMIN-00N`, Background, Messaging or new Shared publication dependency is permitted. Use seeded DB fixtures and injected ports to test independently when upstream/downstream implementations are absent. Status remains Pending until DB001 is confirmed Complete in the canonical task record; do not infer completion from tests alone.

## Enables

None at task-definition time. Completion of this task does not grant permission to start another task or skip an independently required system-test gate.

## Acceptance Criteria

- [ ] Platform admin can activate SHARED/AI/HUMAN slots independently, preview fully translated wrapper content including header/footer/conditional brand variable references and see the effective override/fallback selection.
- [ ] All eight supported brand identifiers survive the prepared projection in permitted sections without content mutation; example values are clearly distinguished from real per-shop values and missing optional values are not concealed.
- [ ] Stale CAS, wrong kind/audience or incomplete translations cannot silently replace a current wrapper; no Meta call is made.
- [ ] Activating new or previous immutable definition changes pointers/audit only; already sent AI/human response contents and checkout records are untouched.


## Validation

- [ ] Schema-backed CAS race/replay tests, semantic eligibility and complete-locale fixture tests, exact preview/conditional section UI tests including `ShopBrand` header/footer/conditional bindings, unknown-key rejection, missing nullable values and clearly fictional previews.
- [ ] Auth/audit/rollback and no-provider-network tests; declared lint/typecheck and `git diff --check`.


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
