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
status: review
priority: 40
executor: null
claimed_at: null
attempt: 2
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
  status: review
  executor: null
  claimed_at: null
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

- [x] Implement category/classification list/create/update/enable/disable service.
- [x] Implement template list/detail/filter/group service by category.
- [x] Implement draft create/update with CAS/idempotent mutation behaviour.
- [x] Implement immutable publish operation.
- [x] Implement enable/disable operation.
- [x] Add durable audit writes.
- [x] Expose typed server actions/Studio port.
- [x] Add focused lifecycle/auth/replay tests.

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

- [x] Platform admins can create/manage data-driven template categories and place multiple templates in one category.
- [x] Platform admins can create and version reusable prompt templates.
- [x] Empty DRAFT template revisions may be saved; publishing blank/whitespace-only prompt text is rejected.
- [x] Published template revisions are immutable and their `contentHash` is SHA-256 of the exact persisted UTF-8 prompt text bytes with no trimming/newline normalisation.
- [x] Disabling a category or template prevents normal new selection/assignment, including direct exact-id selection, while preserving historical/provenance reads.
- [x] Template edits never propagate into an existing prompt.
- [x] Authorization, CAS, durable operation replay/conflict/unknown-outcome and audit semantics are tested.
- [x] No runtime model/provider execution occurs.

## Validation

- focused prompt-template category + lifecycle tests
- focused auth/development-bypass tests
- targeted lint/typecheck
- `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

The service may expose a helper that returns exact published template revision text for copying, but it must not expose a mechanism that leaves prompt content dynamically linked to the template.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation commit `7a90a03` on `task/ARCH-021-COMMERCE-008`.

- `src/commerce/agent-configuration/prompt-template-service.ts`
- `tests/agent-configuration-templates-postgres.test.ts`

The accepted Attempt 1 implementation remains in the four previously reviewed files: `src/studio/agent-configuration/template-contracts.ts`, `src/studio/agent-configuration/template-server-actions.ts`, and `tests/agent-configuration-templates.test.ts`, in addition to the service above.

### Work Completed

Implemented the two requested Attempt 2 corrections without changing the accepted category/template model or ownership boundary.

- Failed or commit-ambiguous transactions now reconcile the durable `CommerceAuditEvent` by actor, action, and exact `operationHash` payload. A matching receipt replays its result, a mismatched receipt returns `CONFLICTING_REPLAY`, and an unestablished outcome returns the existing `unknown` result. Known CAS, validation, not-found, forbidden, and replay errors remain known outcomes.
- Draft creation locks the owning `CommercePromptTemplate` row with `FOR UPDATE` before counting and allocating `revisionNumber`, serializing only concurrent drafts for the same template while preserving the accepted unique constraint.
- Added an explicit-opt-in disposable-PostgreSQL regression suite for concurrent same-operation receipt reconciliation and concurrent draft numbering. It does not delete immutable audit/template fixture rows.

### Validation Results

- `npm test -- --run tests/agent-configuration-templates.test.ts tests/agent-configuration-templates-postgres.test.ts tests/auth-permissions.test.ts`: PASS, 2 files and 9 tests; 2 PostgreSQL tests skipped without explicit opt-in.
- `npx eslint src/commerce/agent-configuration/prompt-template-service.ts src/studio/agent-configuration/template-contracts.ts src/studio/agent-configuration/template-server-actions.ts tests/agent-configuration-templates.test.ts tests/agent-configuration-templates-postgres.test.ts`: PASS.
- `npm run prisma:generate`: PASS; accepted Prisma client generated successfully.
- `git diff --check`: PASS.
- `npm run typecheck -- --pretty false`: exits `2` on existing repository-wide failures outside task-owned files, including missing preview modules, duplicate `productionCodePanel`, existing Studio union/property errors, and unrelated implicit-`any`/generated-client diagnostics. No final diagnostics reference the task-owned files.
- `COMMERCE_PROMPT_TEMPLATE_POSTGRES=1 npm test -- --run tests/agent-configuration-templates-postgres.test.ts`: BLOCKED, not passed. The configured database returned `unknown` during category fixture setup, and cleanup confirmed the target enforces the immutable `CommerceAuditEvent` trigger (`ARCH020 immutable CommerceAuditEvent`). No concurrency assertion was accepted as PostgreSQL evidence.

### Deviations

The required PostgreSQL concurrency evidence remains pending because the configured database target was not a usable disposable ARCH-021 fixture. The regression file is present and opt-in, but the attempt is recorded as blocked rather than passed. No migration, schema, alternate operation table, or provider/runtime call was added.

### Assumptions

The implementation consumes the accepted generated Prisma client and migration state. The PostgreSQL regression requires a disposable target with the ARCH-021 persistence migration applied and `COMMERCE_PROMPT_TEMPLATE_POSTGRES=1`.

### Unresolved Issues

Developer/architect must provide or validate a disposable PostgreSQL target before accepting the two live concurrency regressions.

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
