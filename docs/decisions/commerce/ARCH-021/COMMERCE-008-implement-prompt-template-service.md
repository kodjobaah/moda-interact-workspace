---
id: ARCH-021-COMMERCE-008
architecture_id: ARCH-021
title: Implement category-organised prompt-template authoring service
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-DATABASE-001
  - ARCH-020-COMMERCE-002
enables:
  - ARCH-021-COMMERCE-009
  - ARCH-021-COMMERCE-013
  - ARCH-021-COMMERCE-014
created: 2026-09-23
updated: 2026-09-23
---

# Implement category-organised prompt-template authoring service

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Provide authenticated platform-admin lifecycle operations for data-driven prompt-template categories and reusable application-wide CommerceAgent prompt templates with immutable published revisions.

## Context

Templates are reusable authoring starting points. They are deliberately independent of model selection and they are never the active runtime prompt. Templates are organised by a platform-managed data-driven category/classification such as `Clothing & Fashion`; a category can contain multiple templates. A later prompt draft may be created from an exact published template revision by copying its text and recording provenance.

## Scope

- List/create/update/enable/disable platform prompt-template categories/classifications.
- List/search/filter/group enabled and historical prompt templates/revisions by category for internal Studio use.
- Require each template identity to belong to one category while allowing multiple templates under the same category.
- SUPER_ADMIN create template identities, create/update drafts, publish revisions and enable/disable templates.
- Enforce immutable published revision content.
- Produce stable content hashes/revision identity using the accepted repository conventions.
- Write durable audit events for privileged lifecycle changes.
- Expose typed server actions/port operations for later Studio UI and prompt creation.

## Out of Scope

- Shop-owned templates.
- Active platform/shop prompts.
- Model configuration.
- Model-specific automatic prompt switching.
- Provider calls or prompt execution.
- Runtime prompt rendering.

## Requirements

- Templates remain application-wide in Phase 2.
- ADMIN is read-only; mutations require SUPER_ADMIN outside development bypass.
- Categories are data-driven records, not an enum or hard-coded application list.
- Category slug/identity is stable; display metadata may be edited and audited.
- Disabling a category prevents normal new-authoring assignment/selection while preserving existing template/history visibility.
- A category may contain multiple templates; each template has exactly one category.
- `developmentBypass === true` uses the accepted canonical development actor semantics.
- DRAFT template revisions may persist empty prompt text; publication MUST reject blank/whitespace-only text.
- Published revisions cannot be edited; a new revision is required.
- Published `contentHash` is SHA-256 over the exact UTF-8 bytes of the persisted `promptText`; do not trim, normalise line endings or otherwise transform text for hashing.
- Historical/provenance exact-id reads may resolve disabled categories/templates and their published revisions so existing provenance remains inspectable.
- New-authoring selectable lookup requires both the category and template to be enabled and the requested revision to be published; callers must not bypass disablement merely by supplying an exact revision id.
- No operation may mutate prompts that were previously created from a template.
- Every privileged category/template mutation MUST reuse the existing immutable `CommerceAuditEvent` operation-receipt convention: `id = operationId`, `metadata.payloadHash` using the accepted publication `operationHash({ action, actorId, ...request })` canonical semantics, and replayable `metadata.result`; same request replays, conflicting reuse returns `CONFLICTING_REPLAY`, and unknown outcomes return the existing Studio `unknown` result for reconciliation. Do not create another operation table or invent different JSON canonicalisation.

### Deterministic persistence and file boundary

Consume these accepted Prisma models exactly:

```text
CommercePromptTemplateCategory
CommercePromptTemplate
CommercePromptTemplateRevision
CommerceAuditEvent
```

Primary implementation locations for this task are:

```text
src/commerce/agent-configuration/prompt-template-service.ts
src/studio/agent-configuration/template-contracts.ts
src/studio/agent-configuration/template-server-actions.ts
tests/agent-configuration-templates.test.ts
```

A template category is `CommercePromptTemplateCategory`; a template identity is `CommercePromptTemplate`; a version is `CommercePromptTemplateRevision`. Do not replace the category FK with free-text classification or an enum. Do not create shop-owned template persistence in Phase 2.

## Work Items

- [ ] Implement category/classification list/create/update/enable/disable service.
- [ ] Implement template list/detail/filter/group service by category.
- [ ] Implement draft create/update with CAS/idempotent mutation behaviour.
- [ ] Implement immutable publish operation.
- [ ] Implement enable/disable operation.
- [ ] Add durable audit writes.
- [ ] Expose typed server actions/Studio port.
- [ ] Add focused lifecycle/auth/replay tests.

## Interfaces / Contracts

Consumes:

- ARCH-021-DATABASE-001 prompt-template category/template/revision persistence.
- existing Studio authentication.

Produces:

- category/classification identities and category-grouped template discovery;
- exact published template revision identity/content plus new-authoring selectability semantics for COMMERCE-009 copy-on-use prompt creation;
- template authoring port for COMMERCE-013 template-library UI and COMMERCE-014 platform-prompt template selection.

## Dependencies

- ARCH-021-DATABASE-001
- ARCH-020-COMMERCE-002

## Enables

- ARCH-021-COMMERCE-009
- ARCH-021-COMMERCE-013
- ARCH-021-COMMERCE-014

## Acceptance Criteria

- [ ] Platform admins can create/manage data-driven template categories and place multiple templates in one category.
- [ ] Platform admins can create and version reusable prompt templates.
- [ ] Empty DRAFT template revisions may be saved; publishing blank/whitespace-only prompt text is rejected.
- [ ] Published template revisions are immutable and their `contentHash` is SHA-256 of the exact persisted UTF-8 prompt text bytes with no trimming/newline normalisation.
- [ ] Disabling a category or template prevents normal new selection/assignment, including direct exact-id selection, while preserving historical/provenance reads.
- [ ] Template edits never propagate into an existing prompt.
- [ ] Authorization, CAS, durable operation replay/conflict/unknown-outcome and audit semantics are tested.
- [ ] No runtime model/provider execution occurs.

## Validation

- [ ] focused prompt-template category + lifecycle tests
- [ ] focused auth/development-bypass tests
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

The service may expose a helper that returns exact published template revision text for copying, but it must not expose a mechanism that leaves prompt content dynamically linked to the template.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation commit `ddb03c1` on `task/ARCH-021-COMMERCE-008`.

- `src/commerce/agent-configuration/prompt-template-service.ts`
- `src/studio/agent-configuration/template-contracts.ts`
- `src/studio/agent-configuration/template-server-actions.ts`
- `tests/agent-configuration-templates.test.ts`

### Work Completed

Implemented category CRUD and enable/disable lifecycle using the accepted
`CommercePromptTemplateCategory` model, with stable slug identity, CAS checks,
and category-aware template assignment.

Implemented application-wide template identity CRUD, category filtering,
search, enabled/historical listing, exact detail reads, and disabled-category
or disabled-template selection rejection while preserving historical reads.

Implemented draft creation/update with empty draft support, CAS checks,
idempotent operation replay, conflicting operation-id detection, and copying
exact text from a published source revision without linking future edits.

Implemented immutable publication with blank-text rejection and exact UTF-8
SHA-256 content hashing. Added template/category/revision audit foreign keys,
`operationHash` payload receipts, replay results, and the existing unknown/
conflicting replay result shapes without an alternate operation table.

Added typed Studio read/mutation server actions with per-call admin or
SUPER_ADMIN authorization and the canonical development bypass semantics.
No provider, model, runtime, prompt execution, or alternate persistence calls
were introduced.

### Validation Results

Focused tests: PASS, `2` files and `9` tests (`tests/agent-configuration-templates.test.ts`, `tests/auth-permissions.test.ts`).

Targeted lint: PASS for all four changed files.

`git diff --check`: PASS.

Repository `npm run typecheck -- --pretty false`: exits `2` because of
pre-existing failures outside this task, including missing
`lib/preview/http`, `lib/preview/runtime`, and `src/commerce/preview/types`
imports; duplicate `productionCodePanel`; existing `studio-workspace.tsx`
union/property errors; stale generated Prisma `Sql`, `sql`, and
`InputJsonObject` API errors; and existing implicit-`any` diagnostics. No
diagnostics reference the four task files after the repair.

The broader auth-development-identity test file remains unavailable because
the same baseline generated Prisma client lacks `Prisma.sql`; the focused
prompt-template and auth-permission tests pass.

### Deviations

No implementation deviation from the task contract. The repository-wide typecheck
and broader auth-development-identity failures are documented baseline gaps and
were not modified.

### Assumptions

The accepted Prisma client currently generated in this worktree does not expose
the raw SQL helpers expected by existing authentication code. Re-generating or
changing the database dependency is outside this task’s ownership and was not
performed.

### Unresolved Issues

The implementation assumes the accepted database schema and generated client
are available at deployment time; no migration or schema changes were made.

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 establishes the intended Phase 2 prompt-template service boundary in substance: categories and template identities are data-driven, category/template/draft CAS updates use atomic `updateMany` predicates, publication is limited to the current DRAFT revision/version, published content hashing uses the exact persisted UTF-8 prompt bytes, disabled category/template state is excluded from new-authoring selection while historical reads remain available, SUPER_ADMIN/development-bypass authorization is preserved, and no model/provider/runtime execution is introduced.

Two functional concurrency requirements remain incomplete:

1. The immutable `CommerceAuditEvent` operation receipt is only checked before the mutation. Two concurrent requests with the same `operationId` can both observe no receipt, perform the mutation in separate transactions, and race on `CommerceAuditEvent.id`. The losing transaction is currently translated to a generic error instead of reconciling the durable winner. The same gap means unexpected/commit-ambiguous database failures never use the declared Studio `unknown` outcome. Attempt 2 must reconcile after the transaction fails: when a durable receipt exists and actor/action/payload hash match, return its stored result; when the receipt exists with different input, return `CONFLICTING_REPLAY`; when the durable outcome genuinely cannot be established, return the existing `unknown` result. Known domain validation/CAS errors must remain known errors rather than being converted to unknown.

2. `createDraft` allocates `revisionNumber` using `count({ templateId }) + 1` without serialising creation for that template. Two distinct concurrent draft creates can therefore choose the same revision number and one fails the accepted `[templateId, revisionNumber]` uniqueness constraint. Attempt 2 must serialise or otherwise retry/allocate revision creation so independent concurrent creates can obtain distinct valid revision numbers without weakening the unique constraint. Prefer the narrowest per-template mechanism; do not globally serialise template authoring.

These are bounded corrections to the existing service. Do not redesign the category/template data model, publication hash semantics, authorization boundary, selection semantics, or Phase 2 ownership.

### Reviewed Files

- `src/commerce/agent-configuration/prompt-template-service.ts`
- `src/studio/agent-configuration/template-contracts.ts`
- `src/studio/agent-configuration/template-server-actions.ts`
- `tests/agent-configuration-templates.test.ts`
- `database/prisma/schema.prisma` (accepted persistence/uniqueness contract)
- `src/commerce/connections/command-kernel.ts` (accepted durable concurrent-replay reference pattern)

### Validation Reviewed

- Submitted focused tests: 9 passed.
- Submitted targeted lint: passed.
- Submitted `git diff --check`: passed.
- Task-owned files are clean under the submitted TypeScript check; documented repository-wide baseline diagnostics remain non-blocking.
- Existing in-memory tests prove sequential replay and stale CAS behavior but cannot prove the two PostgreSQL concurrency cases above. Attempt 2 needs only focused disposable-PostgreSQL evidence for concurrent same-`operationId` reconciliation and concurrent same-template draft creation; exhaustive lifecycle testing is not required.

### Architecture Conformance

Partial. The lifecycle, authorization, hashing, immutable-publication and selection boundaries conform, but the Phase 2 durable operation-receipt contract requires same-request replay/conflicting-reuse/unknown-outcome semantics under concurrent execution, and reusable template revision creation must remain correct under concurrent authors.

### Follow-up

Return the same task to Attempt 2. Preserve the accepted implementation and correct only:

- durable receipt reconciliation for concurrent/ambiguous outcomes;
- per-template concurrent revision-number allocation;
- focused PostgreSQL concurrency regressions proving those behaviors.

COMMERCE-009, COMMERCE-013 and COMMERCE-014 remain dependency-gated until COMMERCE-008 is architect-accepted Complete.
