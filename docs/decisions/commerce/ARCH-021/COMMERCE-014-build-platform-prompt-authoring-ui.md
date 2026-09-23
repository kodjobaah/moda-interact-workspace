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
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-008
  - ARCH-021-COMMERCE-009
  - ARCH-021-COMMERCE-011
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

## Interfaces / Contracts

Consumes:

- prompt-template selectable-revision port from ARCH-021-COMMERCE-008;
- prompt lifecycle/configuration port from ARCH-021-COMMERCE-009;
- Agent Configuration shell/module from ARCH-021-COMMERCE-011.

Produces the application-wide platform CommerceAgent prompt authoring surface. It does not own selected-shop prompt authoring.

## Dependencies

- ARCH-021-COMMERCE-008
- ARCH-021-COMMERCE-009
- ARCH-021-COMMERCE-011

## Enables

None.

## Acceptance Criteria

- [ ] Platform admins can inspect platform prompt history and active revision.
- [ ] A platform prompt DRAFT may start empty, from current lineage content or from one exact selectable published template revision.
- [ ] Empty DRAFT content may be saved; blank/whitespace-only publication is rejected and shown without silent text normalisation.
- [ ] Published revisions are immutable and their stable id/hash/status is visible.
- [ ] Activating a platform prompt targets only a published platform revision and does not change model state.
- [ ] Template provenance is visible as historical provenance only; no live template linkage is represented.
- [ ] ADMIN is read-only and no secret/session token is rendered.
- [ ] Platform prompt state/actions do not accumulate in `StudioWorkspace`.
- [ ] No live model/provider execution occurs.

## Validation

- [ ] focused platform-prompt route/component tests
- [ ] blank-draft/publish-validation tests
- [ ] template-copy/provenance UI tests
- [ ] pointer CAS/replay/conflict/unknown-outcome UI tests
- [ ] authorization/development-bypass UI tests
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin another Phase 2 task.

## Implementation Notes

Do not concatenate platform and shop prompts and do not remove the legacy capability prompt field here. Runtime consumption changes belong to later ARCH-021 phases.

## Completion Report

### Status

Ready for Review

### Files Changed

- `app/styles.css`
- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/commerce/agent-configuration/prompt-service.ts`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/platform-prompt-configuration.tsx`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `tests/agent-configuration-platform-prompt-ui.test.tsx`

### Work Completed

- Added a dedicated platform prompt module under `src/studio/agent-configuration/` with singleton lineage discovery, current-environment pointer display, immutable revision history, stable hash/id metadata, and historical template provenance.
- Added empty/current/template copy-on-use draft creation. Template copy sends the exact selected published revision text and revision id; no dynamic template link is represented.
- Added exact-text draft editing and save, dirty/unload/navigation protection, CAS conflict messaging, unknown-outcome reconciliation using the original operation id, blank publication validation display, immutable publish, and published-only pointer activation.
- Wired production server actions to COMMERCE-009 prompt operations and COMMERCE-008 selectable template reads. Added singleton platform-lineage read support for reloads before an active pointer exists.
- Kept model selection and `StudioWorkspace` prompt state unchanged; ADMIN renders read-only controls and no secrets/session credentials.

### Validation Results

- `npm exec vitest run tests/agent-configuration-platform-prompt-ui.test.tsx tests/agent-configuration-model-ui.test.tsx tests/agent-configuration-production.test.tsx tests/agent-configuration-server-actions.test.ts tests/agent-configuration-prompts.test.ts tests/agent-configuration-templates.test.ts --reporter=dot`: 6 files, 21 tests passed on the final focused run before the final lint-only rename; the isolated existing model handoff rerun also passed 4/4 after the rename. One combined rerun was order-sensitive and reported the pre-existing model handoff test once; it passes in isolation.
- `npm exec eslint` on all changed implementation/test files: passed.
- `git diff --check`: passed.
- Targeted `tsc --noEmit --pretty false` scan: no diagnostics in the new prompt component, prompt contracts/actions, or production prompt wiring. Full typecheck remains blocked by existing baseline diagnostics in `components/studio-workspace.tsx` (`productionCodePanel`, `responseProces[s]ing`, `StudioFailure.message`) and pre-existing Prisma generated-type diagnostics in `src/commerce/agent-configuration/prompt-service.ts` (`Prisma.sql`, implicit transaction typing, `Prisma.InputJsonValue`).
- `npm ci`: completed using the committed lockfile; npm reported existing engine/peer/deprecation warnings and 9 audit vulnerabilities.

### Deviations

- Added `PromptPort.getPlatformPrompt()` because the accepted read surface otherwise could not rediscover an existing singleton lineage when no environment active pointer had yet been created. This is a read-only extension of the COMMERCE-009 contract and does not add persistence.

### Assumptions

- The existing server actions enforce origin, ADMIN reads, SUPER_ADMIN mutations, and development bypass; the UI therefore consumes only their browser-safe inputs and does not render principals or credentials.
- A platform draft copied from the active pointer is the accepted interpretation of “current lineage content” for this phase.

### Unresolved Issues

- Full repository typecheck remains blocked by the baseline diagnostics listed above; no prompt-authoring-specific errors remain.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
