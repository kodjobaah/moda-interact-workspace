---
id: ARCH-047-BACKGROUND-002
architecture_id: ARCH-047
title: Implement keyed template-segment translation module
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
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

# Implement keyed template-segment translation module

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This task was originally defined from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is now materialised and claimed for developer execution in canonical task worktrees after confirming the current DB001 prerequisite is complete and synchronizing the parent task branch with current workspace `origin/main`. No new ARCH-047 Shared package is assumed; inspect the current parent architecture and repository state before implementation.

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

- [x] Implement a cohesive `src/services/template-translation/` module with a small coordinator, Prisma repository, segment/token codec, Batch adapter and typed outcome port. Wire thin workers/queues using the existing ARCH-031 generic `translation-batch-runtime/` mechanisms.
- [x] Use `whatsapp.WhatsAppTemplateTranslationRun`, `Item`, `Batch` and `BatchItem`. One **run** refers to one immutable template definition/source hash; one **item** represents the complete segment set for one target language, normally 19 non-English items.
- [x] Consume `sourceSnapshot` prepared by Admin, and persist translated keyed segments in the **existing** `WhatsAppTemplateTranslationItem.translatedAst` JSONB column. Its historical column name does not make the contents a complete AST. Do not add/rename tables or columns.
- [x] Reuse the installed translation provider/model configuration and existing provider Batch submission, polling, result-membership correlation, retry and repair primitives. A provider-specific adapter may be needed; do not duplicate generic mechanisms.
- [x] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [x] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Consumes DB001** `WhatsAppTemplateDefinition`, `TranslationRun.sourceSnapshot`, `TranslationItem.translatedAst`, `Batch`, `BatchItem`, `CommerceTranslationModelConfiguration`. Admin owns the `sourceSnapshot` transport format and will consume `translatedAst` segment results. Include a stable segment `schemaVersion` and example fixtures in this task's tests; never define a second AST schema. No Shared-047 publication dependency.

**Public Background-local port:** `executeTemplateTranslation(runId): Promise<TranslationRunOutcome>` with separate narrow retry/poll/ingest methods as needed. Use idempotent run/item IDs and existing queue job identity. Provider data formatting is private to this module.

## Dependencies

- `ARCH-047-DATABASE-001`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [x] Unit fixtures for keyed `HEADER`/`BODY`/`FOOTER`/button text and mixed languages; preserve variable identity when translation reorders `{{1}}` and `{{2}}`.
- [x] Negative fixtures for missing, duplicated, invented, modified and misplaced tokens; duplicate/unknown segment keys, extra/missing components, malformed provider output and unsupported segment transport version.
- [x] Batch retry/correlation tests: duplicate jobs/results, partial results, stale run hash, late results from an old batch, provider timeout and recovery without re-translating successful items.
- [x] PostgreSQL integration with actual DB001 run/item/batch records, proving translated **segments** are persisted only in `translatedAst` and locale AST is untouched.
- [x] Run focused Vitest unit tests, required repository build/typecheck and `git diff --check`; inspect `package.json` rather than inventing test commands.
- [x] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [x] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

## Validation

- [x] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [x] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [x] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [x] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

The existing `src/services/translation-batch-runtime/` and `src/services/merchant-pricing-translation/` are useful implementation references, but Merchant Pricing's domain queries must not be reused for WhatsApp. Inject DB and provider ports. Keep provider adapters, protection/validation functions and orchestration independently testable. Hand Admin a stable result schema, not a provider response blob.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-002`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

Complete — developer execution Attempt 1 passed developer-as-architect review and was explicitly completed by the developer on 2026-10-26. The developer claim is cleared. `ARCH-047-DATABASE-001` is complete.

### Files Changed

Implementation commit `7e31d5885b77e20f1acbf48c1c77642d38267c67` changes 14 task-owned files in `moda-interact-background` (1,601 insertions, 6 deletions): three existing provider/worker/entrypoint files; the five-file `src/services/template-translation/` module; its thin worker; one integration fixture and integration test; and three focused unit test files. No migration, new Prisma schema or shared package was added. The implementation task branch is `task/ARCH-047-BACKGROUND-002`; local HEAD and `origin/task/ARCH-047-BACKGROUND-002` both resolve to the implementation commit above. The implementation worktree has one unrelated untracked path, `typescript`, which was left untouched; all task-owned paths are committed and clean. The canonical parent task worktree was clean at claim commit `e757239fe9e80c34ded4c9957da82b644cd66e1c` before this report update.

### Work Completed

- Added Admin-prepared source snapshot validation and keyed segment translation with deterministic protected-token sentinels, per-segment token identity/multiplicity checks, exact output-key membership, token restoration and content hashing.
- Added durable run/batch coordination, row-locked item assignment, provider submission/poll/result lifecycle, ambiguity correlation, deterministic BullMQ job repair, bounded retry/terminal handling and persistence of keyed JSON only in `translatedAst`.
- Registered thin submit/poll/results worker handlers and recurring reconciliation in the existing merchant communications worker. The existing provider supports `keyed-segments-v1` requests without changing default translation behavior.
- Added focused unit and PostgreSQL/BullMQ integration fixtures. Integration coverage proves concurrent allocation, successful keyed persistence without locale AST mutation, language-isolated retry, uncertain-create recovery, poll retry/stale sequence behavior and stale-source rejection.
- Reviewed against the current module-first ARCH-047 architecture. The earlier unresolved note about waiting for BACKGROUND-001/parent reconciliation is preparation-time text and is not a prerequisite: BACKGROUND-001 is a separate module and is not in this task's dependency list.

### Validation Results

- Focused translation regression suite: all seven `tests/unit/services/translation-batch-runtime/` files, `tests/unit/services/template-translation/`, and five existing merchant-pricing translation regression files; 14 files passed, 63 tests passed.
- `npm run build`: passed; Prisma Client generated and TypeScript compilation completed.
- `npm run test:integration -- tests/integration/whatsapp-template-translation.integration.test.ts`: passed; 1 integration file, 5 tests passed against the configured disposable PostgreSQL/BullMQ harness. Direct invocation of the Node script initially failed because `prisma` was not on PATH; the declared npm script supplies the required PATH and the harness then passed.
- `npm exec eslint -- src/services/template-translation src/workers/template-translation.worker.ts tests/unit/services/template-translation tests/integration/whatsapp-template-translation.integration.test.ts`: passed with no diagnostics.
- `git diff --check origin/main...HEAD`: passed. Implementation branch equals its published remote task branch. Scoped status confirms task-owned files are committed; unrelated untracked `typescript` was preserved.

### Deviations

No scope or architecture deviations. The integration harness was run through `npm run test:integration` after direct script invocation exposed a PATH issue; all five integration tests passed. No other-task files or downstream readiness records were changed.

### Assumptions

The DB001 Attempt 7 model names and fields are authoritative design inputs, not proof of an accepted/applied production migration. Reinspect current implementation on claim.

### Unresolved Issues

None identified within this task. The architecture document describes the module-first boundary: Admin owns AST compilation, Background consumes keyed prepared segments, and no new Shared template package is presumed. Remaining architecture-wide status reconciliation is outside this task and does not block this module's review.

### Architectural Concerns

No additional cross-repository issues identified at definition time; return any new gap to the architect.

## Developer Self-Review - Passed/Accepted

### Review Status

Passed/Accepted — developer-as-architect review of Attempt 1. Required Work Items, Acceptance Criteria and Validation are complete; implementation and task report are committed and pushed on their mirrored task branches.

### Review Notes

No blocking review findings. The implementation consumes versioned Admin-prepared keyed segments, validates protected-token identity and output membership, persists only the keyed result projection, and reuses existing Batch lifecycle primitives. It does not reconstruct the authoring AST, mutate Meta templates, write locale AST, or introduce an outbound send path. PostgreSQL/BullMQ integration evidence and all required focused validation passed.

### Reviewed Files

`src/services/template-translation/`; `src/workers/template-translation.worker.ts`; `src/providers/translation.provider.ts`; `src/workers/merchant-communications.worker.ts`; `src/entrypoints/merchant-communications.ts`; the new template translation unit and integration tests.

### Validation Reviewed

Focused translation regression suite (14 files / 63 tests), repository build, PostgreSQL/BullMQ integration suite (5 tests), scoped ESLint, and `git diff --check` all passed. See Completion Report for exact commands and branch evidence.

### Architecture Conformance

Accepted as conformant to the keyed-segment module boundary in ARCH-047: Admin owns authoring AST compilation; Background consumes prepared snapshots, protects/restores tokens, persists keyed projections only, reuses ARCH-031 runtime primitives, and leaves Meta management, publication and final-send admission outside this module.

### Follow-up

No task-local follow-up is required. No downstream task explicitly depends on BACKGROUND-002; no dependency frontier changes were identified. No adjacent task was started and `_index.md` was not changed.

## Developer Completion Decision

- Date: 2026-10-26.
- Action: The developer explicitly invoked `/moda_developer_update ARCH-047-BACKGROUND-002 complete` after the durable Passed/Accepted review above.
- Decision: All required Work Items and Acceptance Criteria are complete; implementation commit `7e31d5885b77e20f1acbf48c1c77642d38267c67` and the parent task report are committed and published on their canonical mirrored task branches. No merge to `main` is required or performed.
- State: `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1` (unchanged).
- Dependency frontier: No other ARCH-047 task declares BACKGROUND-002 in `depends_on`; no downstream task promotion or regression was needed.

## Execution Ownership Amendment

- Date: 2026-10-25.
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, dependency, task scope, acceptance criteria and validation requirements.
- Dependency check: `ARCH-047-DATABASE-001` is `complete` in its canonical task record.
- Claim: Attempt 1 is claimed by `developer` at `2026-10-25T19:09:28Z` after canonical worktree preparation and synchronization.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-BACKGROUND-002`, branch `task/ARCH-047-BACKGROUND-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-BACKGROUND-002`, branch `task/ARCH-047-BACKGROUND-002`, created from current Background `origin/main` because no BACKGROUND-002 task branch existed locally or remotely.
- The parent task branch was merged with current workspace `origin/main` during claim preparation and published at claim commit `e757239fe9e80c34ded4c9957da82b644cd66e1c`. Implementation was committed and pushed on the mirrored task branch. The Accepted review/report was committed and pushed as `fac0de03a7bfb9e2036b73ab551392eb5b7219d2`; this explicit completion decision is recorded on the same parent task branch. No branch was merged into `main`.
