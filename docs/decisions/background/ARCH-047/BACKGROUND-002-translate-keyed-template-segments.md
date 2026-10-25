---
id: ARCH-047-BACKGROUND-002
architecture_id: ARCH-047
title: Implement keyed template-segment translation module
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
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

# Implement keyed template-segment translation module

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This is a **portable task definition** prepared from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is not a repository implementation, task claim or evidence of a created worktree/branch. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

## Objective

Execute persisted, Admin-prepared translation segments with protected variables and ARCH-031 Batch runtime; return keyed results, not reconstructed ASTs.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Implement a cohesive `src/services/template-translation/` module with a small coordinator, Prisma repository, segment/token codec, Batch adapter and typed outcome port. Wire thin workers/queues using the existing ARCH-031 generic `translation-batch-runtime/` mechanisms.
- Use `whatsapp.WhatsAppTemplateTranslationRun`, `Item`, `Batch` and `BatchItem`. One **run** refers to one immutable template definition/source hash; one **item** represents the complete segment set for one target language, normally 19 non-English items.
- Consume `sourceSnapshot` prepared by Admin, and persist translated keyed segments in the **existing** `WhatsAppTemplateTranslationItem.translatedAst` JSONB column. Its historical column name does not make the contents a complete AST. Do not add/rename tables or columns.
- Reuse the installed translation provider/model configuration and existing provider Batch submission, polling, result-membership correlation, retry and repair primitives. A provider-specific adapter may be needed; do not duplicate generic mechanisms.

## Out of Scope

- Parsing, compiling, validating or reconstructing the Admin **authoring AST** or Meta `components` JSON; populating `WhatsAppTemplateLocale.localeAst` from raw translations; Admin approval/activation, Meta submission, webhook handling, offer resolution and message sending.
- New Shared template package, new translation tables, new queue infrastructure without demonstrated necessity, rewriting ARCH-031 translation services, or touching `docs/decisions/**/_index.md`.

## Requirements

**R1 — Input contract.** `run.sourceSnapshot` is Admin-created, versioned JSONB holding `schemaVersion`, `sourceLanguageTag`, `sourceHash` and `segments[]`. Each segment has an immutable unique **key** (for example `header.text`, `body.text`, `buttons.0.text`), `text` and an optional list of protected token identities. Include any non-sensitive semantic token hints supplied by Admin. Background does not infer component positions from text or parse the authoring AST. Reject malformed/unknown segment-transport versions at the **job boundary**, not by revalidating saved authoring rules.

**R2 — Protected tokens.** Before translation, replace each protected token occurrence with a stable, unambiguous sentinel (or an equivalent lossless protected-token mechanism). Protect `{{1}}`/`{{2}}`, non-translatable identifiers, dynamic URL portions and provider metadata. At result admission, compare the expected and returned **multiset of token identities per segment**: missing, changed, extra or duplicated tokens fail that language item. Translators may reorder intact tokens naturally. Preserve a deterministic token-restore map; never assume the model obeyed prompt instructions alone.

**R3 — Output contract.** `item.translatedAst` stores `{schemaVersion:1,segments:[{key,text}]}` or a precisely documented, equivalent keyed-segment projection. Every source key appears exactly once, with no added/removed segments, after token restoration. Persist item-level success/error/retry, output hash and result correlation separately. **Admin**, not Background, later reconstructs a full translated locale and compiles Meta/runtime payloads.

**R4 — Durable execution.** Claim/retry items with CAS or row locks, prevent duplicate Batch membership, correlate custom IDs and late results to the original run/item and source hash. Failed languages may retry without redoing successful languages; partial completion is visible. Provider failures, malformed results and stale/orphaned runs have bounded, observable terminal or retry states.

**R5 — Privacy and resilience.** Only customer-independent template text and placeholder hints enter translation requests; no customer checkout values or credentials. Do not call OpenAI/Batch/Redis inside a DB transaction. Reuse existing OTel/structured logging, and leave baseline translation workloads unaffected.

## Work Items

- [ ] Implement a cohesive `src/services/template-translation/` module with a small coordinator, Prisma repository, segment/token codec, Batch adapter and typed outcome port. Wire thin workers/queues using the existing ARCH-031 generic `translation-batch-runtime/` mechanisms.
- [ ] Use `whatsapp.WhatsAppTemplateTranslationRun`, `Item`, `Batch` and `BatchItem`. One **run** refers to one immutable template definition/source hash; one **item** represents the complete segment set for one target language, normally 19 non-English items.
- [ ] Consume `sourceSnapshot` prepared by Admin, and persist translated keyed segments in the **existing** `WhatsAppTemplateTranslationItem.translatedAst` JSONB column. Its historical column name does not make the contents a complete AST. Do not add/rename tables or columns.
- [ ] Reuse the installed translation provider/model configuration and existing provider Batch submission, polling, result-membership correlation, retry and repair primitives. A provider-specific adapter may be needed; do not duplicate generic mechanisms.
- [ ] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Consumes DB001** `WhatsAppTemplateDefinition`, `TranslationRun.sourceSnapshot`, `TranslationItem.translatedAst`, `Batch`, `BatchItem`, `CommerceTranslationModelConfiguration`. Admin owns the `sourceSnapshot` transport format and will consume `translatedAst` segment results. Include a stable segment `schemaVersion` and example fixtures in this task's tests; never define a second AST schema. No Shared-047 publication dependency.

**Public Background-local port:** `executeTemplateTranslation(runId): Promise<TranslationRunOutcome>` with separate narrow retry/poll/ingest methods as needed. Use idempotent run/item IDs and existing queue job identity. Provider data formatting is private to this module.

## Dependencies

- `ARCH-047-DATABASE-001`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [ ] Unit fixtures for keyed `HEADER`/`BODY`/`FOOTER`/button text and mixed languages; preserve variable identity when translation reorders `{{1}}` and `{{2}}`.
- [ ] Negative fixtures for missing, duplicated, invented, modified and misplaced tokens; duplicate/unknown segment keys, extra/missing components, malformed provider output and unsupported segment transport version.
- [ ] Batch retry/correlation tests: duplicate jobs/results, partial results, stale run hash, late results from an old batch, provider timeout and recovery without re-translating successful items.
- [ ] PostgreSQL integration with actual DB001 run/item/batch records, proving translated **segments** are persisted only in `translatedAst` and locale AST is untouched.
- [ ] Run focused Vitest unit tests, required repository build/typecheck and `git diff --check`; inspect `package.json` rather than inventing test commands.
- [ ] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [ ] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

## Validation

- [ ] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [ ] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [ ] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [ ] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

The existing `src/services/translation-batch-runtime/` and `src/services/merchant-pricing-translation/` are useful implementation references, but Merchant Pricing's domain queries must not be reused for WhatsApp. Inject DB and provider ports. Keep provider adapters, protection/validation functions and orchestration independently testable. Hand Admin a stable result schema, not a provider response blob.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-002`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

Not Started — task definition only; no implementation was executed or validated in this artifact.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run; implementation validation remains outstanding.

### Deviations

None recorded.

### Assumptions

The DB001 Attempt 7 model names and fields are authoritative design inputs, not proof of an accepted/applied production migration. Reinspect current implementation on claim.

### Unresolved Issues

The parent ARCH-047 architecture and `BACKGROUND-001` still require final reconciliation with the Admin-owned AST/compilation and no-new-Shared-template-package decision before work begins.

### Architectural Concerns

No additional cross-repository issues identified at definition time; return any new gap to the architect.

## Architect Review

### Review Status

Pending — implementation not submitted.

### Review Notes

Not reviewed.

### Reviewed Files

None yet.

### Validation Reviewed

None yet.

### Architecture Conformance

To be assessed against the reconciled ARCH-047 parent architecture and current repository code.

### Follow-up

Architect to reconcile the parent task graph and obsolete Admin/Shared references before promoting these tasks to Ready.
