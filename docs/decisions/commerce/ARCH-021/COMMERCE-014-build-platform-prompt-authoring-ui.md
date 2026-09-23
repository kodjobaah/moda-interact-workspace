---
id: ARCH-021-COMMERCE-014
architecture_id: ARCH-021
title: Build platform CommerceAgent prompt authoring UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 74
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-008
  - ARCH-021-COMMERCE-009
  - ARCH-021-COMMERCE-011
  - ARCH-021-COMMERCE-015
enables: []
created: 2026-09-23
updated: 2026-09-23
---

# Build platform CommerceAgent prompt authoring UI

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add application-wide CommerceAgent prompt lineage, draft, immutable revision history and active-pointer authoring to the Agent Configuration Studio surface.

## Context

The configurable platform behavioural prompt has a distinct lifecycle from reusable prompt templates. COMMERCE-009 owns the platform/shop prompt service and COMMERCE-008 supplies selectable published template revisions for copy-on-use. COMMERCE-011 establishes the Agent Configuration shell. This task implements only the platform prompt authoring UI; selected-shop prompt authoring remains COMMERCE-012.

## Scope

- Extend Agent Configuration with the application-wide/platform prompt section.
- Show the singleton platform prompt lineage, revision history and current environment active revision.
- Create a DRAFT revision from:
  - empty content;
  - current lineage content;
  - one exact currently-selectable published template revision.
- Edit/save DRAFT content with CAS and accepted replay/conflict/unknown-outcome handling.
- Publish non-blank DRAFT content into an immutable published revision.
- Activate a published platform revision using the environment-scoped pointer operation.
- Show `sourceTemplateRevisionId` provenance when a draft/revision originated from a template, without implying live linkage.
- Display immutable revision id/hash/status/published metadata needed for later preview validation.
- Apply dirty/navigation guards to unsaved prompt edits.
- ADMIN remains read-only; SUPER_ADMIN gets mutation controls outside development bypass.

## Out of Scope

- Prompt-template category/template management UI; owned by ARCH-021-COMMERCE-013.
- Shop prompt/model override UI; owned by ARCH-021-COMMERCE-012.
- Model catalogue/default UI; owned by ARCH-021-COMMERCE-011.
- Feature prompt removal.
- Live provider/model/tool execution.
- Grant/manifest/Background changes.
- Merchant access.

## Requirements

- Production composition must use COMMERCE-009 prompt operations and COMMERCE-008 selectable-template reads, never fixture ports.
- Platform prompt state/editor/mutation orchestration remains under `src/studio/agent-configuration/`, not `StudioWorkspace`.
- Empty DRAFT prompt content is valid. Publish must preserve the user's exact persisted text and surface the service validation error when it is blank/whitespace-only.
- `Use template` copies the exact selected published template revision into a prompt DRAFT; it is not a dynamic link.
- Published revisions are presented as immutable; editing requires a new DRAFT.
- Model selection must not be changed by any prompt operation.
- Mutation UI must preserve accepted durable replay/conflict/unknown-outcome semantics.

### Deterministic file boundary

Primary locations:

```text
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/platform-prompt-configuration.tsx
app/agent-configuration/page.tsx
tests/agent-configuration-platform-prompt-ui.test.tsx
```

Small helper components may be added only under `src/studio/agent-configuration/`. `StudioWorkspace` requires no new prompt editor state.

## Work Items

- [x] Add platform lineage/history/active-pointer presentation.
- [x] Add create-empty/create-from-current/create-from-template DRAFT actions.
- [x] Add DRAFT editing/saving with dirty/CAS handling.
- [x] Add immutable publish action and validation presentation.
- [x] Add platform active-pointer mutation UI.
- [x] Add provenance and stable revision/hash presentation.
- [x] Add focused lifecycle/auth/replay UI tests.
- [x] Consume exact published template revision history with category context and revalidation.
- [x] Guard every refresh-causing mutation against unsaved editor text.
- [x] Prove singleton platform-lineage rediscovery, platform-only scope and ADMIN read authentication.
- [x] Prove production handoff of the real prompt lifecycle and template actions.

## Interfaces / Contracts

Consumes:

- prompt-template selectable-template/exact-revision reads from ARCH-021-COMMERCE-008;
- prompt-template revision-history read contract from ARCH-021-COMMERCE-015;
- prompt lifecycle/configuration port from ARCH-021-COMMERCE-009;
- Agent Configuration shell/module from ARCH-021-COMMERCE-011.

Produces the application-wide platform CommerceAgent prompt authoring surface. It does not own selected-shop prompt authoring.

## Dependencies

- ARCH-021-COMMERCE-008
- ARCH-021-COMMERCE-009
- ARCH-021-COMMERCE-011
- ARCH-021-COMMERCE-015

## Enables

None.

## Acceptance Criteria

- [x] Platform admins can inspect platform prompt history and active revision.
- [x] A platform prompt DRAFT may start empty, from current lineage content or from one exact selectable published template revision.
- [x] Empty DRAFT content may be saved; blank/whitespace-only publication is rejected and shown without silent text normalisation.
- [x] Published revisions are immutable and their stable id/hash/status is visible.
- [x] Activating a platform prompt targets only a published platform revision and does not change model state.
- [x] Template provenance is visible as historical provenance only; no live template linkage is represented.
- [x] ADMIN is read-only and no secret/session token is rendered.
- [x] Platform prompt state/actions do not accumulate in `StudioWorkspace`.
- [x] No live model/provider execution occurs.

## Validation

- [x] focused platform-prompt route/component tests
- [x] blank-draft/publish-validation tests
- [x] template-copy/provenance UI tests
- [x] pointer CAS/replay/conflict/unknown-outcome UI tests
- [x] authorization/development-bypass UI tests
- [x] targeted lint/typecheck
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin another Phase 2 task.

## Implementation Notes

Do not concatenate platform and shop prompts and do not remove the legacy capability prompt field here. Runtime consumption changes belong to later ARCH-021 phases.

## Completion Report

### Status

Ready for Review

### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-014`
- Parent branch: `task/ARCH-021-COMMERCE-014`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-014`
- Implementation branch: `task/ARCH-021-COMMERCE-014`
- Shared workspace and shared implementation checkouts switched or mutated for task work: no
- Another task worktree reused: no

### Start-of-Attempt Synchronization

- Parent task branch and implementation branch were prepared by the deterministic launcher with `origin/main` incorporated.
- Recursive implementation submodule synchronization and initialization passed; recorded `database` commit: `98fdf715e54fe6df92ac6951facd104e410068f2`.
- Parent claim commit: `d0898444`.
- Implementation correction commit: `1612226`.

### Files Changed

- `app/styles.css`
- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/commerce/agent-configuration/prompt-service.ts`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/platform-prompt-configuration.tsx`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `src/studio/agent-configuration/template-server-actions.ts`
- `tests/agent-configuration-platform-prompt-ui.test.tsx`
- `tests/agent-configuration-production.test.tsx`
- `tests/agent-configuration-prompts.test.ts`
- `tests/agent-configuration-server-actions.test.ts`

### Work Completed

- Added a dedicated platform prompt module under `src/studio/agent-configuration/` with singleton lineage discovery, current-environment pointer display, immutable revision history, stable hash/id metadata, and historical template provenance.
- Added empty/current/template copy-on-use draft creation. Template copy presents category context, lets the administrator choose one exact published revision, revalidates that revision immediately before copying, and sends the same revision id to draft creation; no dynamic template link is represented.
- Added exact-text draft editing and save, dirty/unload/navigation protection, CAS conflict messaging, unknown-outcome reconciliation using the original operation id, blank publication validation display, immutable publish, and published-only pointer activation.
- Blocked publish, new-draft, active-copy, template-copy and activation actions while editor text is dirty, preventing silent discard or stale publication.
- Wired production server actions to COMMERCE-009 prompt operations and COMMERCE-008/015 canonical template reads. Added singleton platform-lineage read support for reloads before an active pointer exists and removed the duplicate local template reader contract.
- Kept model selection and `StudioWorkspace` prompt state unchanged; ADMIN renders read-only controls and no secrets/session credentials.

### Validation Results

- `npm exec vitest run tests/agent-configuration-platform-prompt-ui.test.tsx tests/agent-configuration-production.test.tsx tests/agent-configuration-prompts.test.ts tests/agent-configuration-server-actions.test.ts tests/agent-configuration-model-ui.test.tsx`: 5 files, 19 tests passed.
- The UI suite includes dirty-action blocking and exact revision/category selection; service/server-action suites cover platform-only lineage rediscovery and ADMIN authentication.
- `npm exec eslint` on all changed implementation/test files: passed.
- `git diff --check`: passed.
- Changed-file diagnostics: no errors in production composition, prompt component/contracts, and focused tests.
- PostgreSQL concurrency validation was not runnable in this worktree because `@prisma/client` is not generated (`Please run "prisma generate"`); six non-PostgreSQL focused suites passed with 19 tests and 6 PostgreSQL tests skipped by setup failure.

### Deviations

- Added `PromptPort.getPlatformPrompt()` because the accepted read surface otherwise could not rediscover an existing singleton lineage when no environment active pointer had yet been created. Focused service and authenticated server-action regressions cover platform-only scope and this read-only extension does not add persistence.

### Assumptions

- The existing server actions enforce origin, ADMIN reads, SUPER_ADMIN mutations, and development bypass; the UI therefore consumes only their browser-safe inputs and does not render principals or credentials.
- A platform draft copied from the active pointer is the accepted interpretation of “current lineage content” for this phase.

### Unresolved Issues

- PostgreSQL concurrency tests remain environment-blocked until the generated Prisma client is available; no prompt-authoring-specific diagnostics remain in the changed-file check.

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 establishes the correct high-level platform-prompt authoring boundary: the editor lives under `src/studio/agent-configuration/`, production composition uses the accepted prompt/template services, ADMIN is read-only, published revision identity/hash/provenance are visible, pointer mutation is environment-scoped, and no provider/model/tool execution is introduced.

The following task-scoped corrections are required before acceptance:

1. **Unsaved DRAFT text can currently be discarded or stale content can be published.** `PlatformPromptConfiguration.run()` reloads the lineage after every successful mutation. While `draftText !== savedText`, `Publish revision`, `New empty draft`, `Copy active revision`, `Use template`, and published-revision `Activate` remain enabled. A successful action therefore calls `load()` and replaces the local editor text. Most seriously, `Publish revision` publishes the persisted pre-edit draft while the browser may visibly contain different unsaved text, then reloads and loses those edits. Attempt 2 must prevent every lineage-refreshing mutation from silently discarding dirty editor state. `Publish revision` MUST NOT execute while the editor is dirty; it may run only after the current text has been saved. Other refresh-causing prompt actions must either be disabled while dirty or use an explicit discard/stay guard before invoking any server action.

2. **`Use template` does not let the administrator choose the exact published template revision required by the task.** The current selector stores only `templateId` and `handleUseTemplate()` calls `getPromptTemplate({ templateId, selectable: true })`, which silently resolves whichever published revision is latest at click time. Attempt 2 must consume the accepted `ARCH-021-COMMERCE-015` revision-history read contract, present the selectable template/category plus an explicit published revision identity, and revalidate the exact choice with `getPromptTemplate({ templateId, revisionId, selectable: true })` immediately before copying. `createDraft` must receive that same exact `sourceTemplateRevisionId`. The chooser must expose category context/grouping consistent with the parent architecture rather than presenting an unclassified flat list.

3. **Do not duplicate the canonical template read contract inside prompt contracts.** The added `PromptTemplateReader` in `prompt-contracts.ts` is unused and structurally duplicates the COMMERCE-008/015 template contract. Remove it and consume the canonical template contracts/actions.

4. **The new singleton-platform read extension needs focused proof.** `getPlatformPrompt()` is consistent with COMMERCE-009's original scope to read the singleton platform lineage and is acceptable as a bounded read-only completion of that contract, but Attempt 1 adds it without a focused service/server-action regression. Add proof that an existing platform lineage can be rediscovered when no environment pointer exists, that the read cannot return a SHOP lineage, and that the production server action retains ADMIN authentication. Do not change prompt mutation/CAS/replay semantics.

5. **Production composition coverage must prove the prompt handoff.** Extend the existing Agent Configuration production-composition regression to assert that the real prompt lifecycle actions and canonical template read actions are supplied through `agentConfigurationPromptActions`; do not rely only on the existing model-action assertion.

The submitted Completion Report also omits the launcher-prepared worktree/synchronization/submodule evidence required by the repository-task protocol. Attempt 2 must record the exact prepared parent and implementation worktrees, matching task branches, start-of-attempt synchronization and recursive submodule evidence rather than reconstructing or guessing values.

### Reviewed Files

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/commerce/agent-configuration/prompt-service.ts`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/platform-prompt-configuration.tsx`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `src/studio/agent-configuration/template-server-actions.ts`
- `tests/agent-configuration-platform-prompt-ui.test.tsx`
- `tests/agent-configuration-production.test.tsx`

### Validation Reviewed

- Reviewed the reported focused validation: 6 files / 21 tests passing on the final focused run, plus the isolated model-handoff rerun.
- Reviewed the reported targeted ESLint and `git diff --check` passes.
- Confirmed the supplied archive contains no `node_modules`, so Vitest was not independently rerun in architect review.
- Existing repository-wide TypeScript baseline diagnostics are not treated as task regressions where they remain outside the changed behavior.
- Additional regressions are mandatory for the dirty-mutation guard, exact template-revision selection, singleton-platform read/auth path and production prompt-action composition described above.

### Architecture Conformance

Partial. The platform prompt surface is on the correct Agent Configuration boundary and reuses the accepted prompt lifecycle, but Attempt 1 does not yet preserve dirty-editor correctness or the exact copy-on-use template revision contract. The unused duplicate `PromptTemplateReader` also conflicts with canonical template-contract ownership.

### Follow-up

Return the same task for Attempt 2. No separate correction task is required. `ARCH-021-COMMERCE-015` is now an explicit prerequisite because its accepted revision-history read is required for deterministic exact-revision selection. It is already Complete, so the task remains executable.

Attempt 2 correction contract:

- [ ] Consume `listPromptTemplateRevisions({ templateId })` from the accepted COMMERCE-015 server action/contract.
- [ ] Render an exact published revision choice with category context; retain only revisions that are `PUBLISHED` for selection.
- [ ] Before copying, call `getPromptTemplate({ templateId, revisionId, selectable: true })` and pass the same exact revision id to `createDraft`.
- [ ] Remove the unused local `PromptTemplateReader` duplicate from `prompt-contracts.ts`.
- [ ] Prevent `Publish revision` from executing while `draftText !== savedText`.
- [ ] Prevent `New empty draft`, `Copy active revision`, `Use template`, and `Activate` from silently discarding dirty prompt text; require save/revert or explicit discard/stay semantics before the server action runs.
- [ ] Add focused UI regressions proving dirty actions perform no write until the dirty state is resolved and exact revision/category selection copies the chosen revision, not merely the latest revision.
- [ ] Add focused `getPlatformPrompt()` service/server-action coverage for no-pointer lineage rediscovery, PLATFORM-only scope and ADMIN authentication.
- [ ] Extend production composition coverage to assert the real `agentConfigurationPromptActions` handoff.
- [ ] Re-run the focused prompt/model/production suites, targeted ESLint/type diagnostics and `git diff --check`.
- [ ] Reconcile Work Items, Acceptance Criteria, Validation and the Completion Report, including exact launcher worktree/synchronization/submodule evidence.
