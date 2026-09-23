---
id: ARCH-021-COMMERCE-013
architecture_id: ARCH-021
title: Build platform prompt-template library UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 72
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-008
  - ARCH-021-COMMERCE-011
  - ARCH-021-COMMERCE-015
enables: []
created: 2026-09-23
updated: 2026-09-23
---

# Build platform prompt-template library UI

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add the platform-managed category-organised prompt-template library to the Agent Configuration Studio surface using the accepted COMMERCE-008 service.

## Context

Prompt templates are application-wide authoring starting points, not active runtime prompts. They have their own category/template/revision lifecycle and can be implemented/reviewed independently of model management and platform prompt activation. COMMERCE-011 establishes the Agent Configuration route/module shell; this task adds only the template-library capability.

## Scope

- Extend the Agent Configuration module with a platform prompt-template library section.
- List/filter/group templates and revisions by category/classification.
- Create categories with stable authored slug and mutable display metadata.
- Update category display metadata without presenting stable slug/identity as renameable.
- Enable/disable categories.
- Create multiple template identities within one category.
- Update template display metadata and enable/disable templates.
- Create/edit DRAFT template revisions, including an empty initial draft.
- Publish a non-blank template revision.
- Display immutable published revision identity/hash and historical disabled category/template state where returned by COMMERCE-008.
- Apply dirty/navigation guards to unsaved template edits.
- ADMIN remains read-only; SUPER_ADMIN gets mutation controls outside development bypass.

## Out of Scope

- Platform prompt lineage/draft/history/active pointer; owned by ARCH-021-COMMERCE-014.
- Shop prompt/model overrides; owned by ARCH-021-COMMERCE-012.
- Platform model catalogue/default controls; owned by ARCH-021-COMMERCE-011.
- Live provider/model/tool execution.
- Grant/manifest/Background changes.
- Merchant-owned template libraries.

## Requirements

- Production composition must use COMMERCE-008 server actions/ports, never fixture ports.
- Category/template editor state and mutation orchestration remain under `src/studio/agent-configuration/` and must not move into `StudioWorkspace`.
- Category slug is shown as stable identity after creation; UI edit operations change display metadata only.
- Empty DRAFT content is valid, but the publish action must surface the COMMERCE-008 validation error for blank/whitespace-only content rather than silently altering the text.
- Disabled category/template history remains inspectable while new-authoring selection is unavailable according to COMMERCE-008.
- Mutation UI must preserve accepted replay/conflict/unknown-outcome semantics.

### Deterministic file boundary

Primary locations:

```text
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/prompt-template-library.tsx
app/agent-configuration/page.tsx
tests/agent-configuration-template-ui.test.tsx
```

Small helper components may be added only under `src/studio/agent-configuration/`. `StudioWorkspace` requires no new domain state for this task.

## Work Items

- [ ] Add category list/create/display-metadata-update/enable/disable UI.
- [ ] Add category-grouped/filterable template discovery.
- [ ] Add template identity metadata/enablement controls.
- [ ] Add template DRAFT editor/history/publish flow.
- [ ] Add dirty/navigation and replay/conflict/unknown-outcome handling.
- [ ] Add focused read-only/admin/auth/lifecycle UI tests.

## Interfaces / Contracts

Consumes:

- prompt-template service from ARCH-021-COMMERCE-008;
- Agent Configuration shell/module from ARCH-021-COMMERCE-011.

Produces the platform prompt-template library UI used by administrators for reusable copy-on-use authoring assets. It does not own prompt copy/activation.

## Dependencies

- ARCH-021-COMMERCE-008
- ARCH-021-COMMERCE-011
- ARCH-021-COMMERCE-015

## Enables

None.

## Acceptance Criteria

- [ ] Platform admins can manage data-driven template categories without mutating stable category slug/identity.
- [ ] Multiple templates can be browsed/authored within one category.
- [ ] Empty DRAFT template content can be saved; blank/whitespace-only publication is rejected and shown to the user.
- [ ] Published revision identity/hash/history is displayed without implying published content is editable.
- [ ] Disabled category/template history remains visible while new selection is unavailable.
- [ ] ADMIN is read-only and no secret/session token is rendered.
- [ ] Template-library state/actions do not accumulate in `StudioWorkspace`.
- [ ] No active prompt mutation or live model/provider execution occurs.

## Validation

- [ ] focused template-library route/component tests
- [ ] category/template lifecycle UI tests
- [ ] empty-draft/publish-validation UI regression
- [ ] authorization/development-bypass UI tests
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin another Phase 2 task.

## Implementation Notes

A template remains an authoring asset. Do not add UI wording or state that suggests an active platform/shop prompt stays dynamically linked to the template.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-commerce/app/styles.css`
- `moda-interact-commerce/components/production-studio-page.tsx`
- `moda-interact-commerce/components/studio-workspace.tsx`
- `moda-interact-commerce/src/studio/agent-configuration/agent-configuration-screen.tsx`
- `moda-interact-commerce/src/studio/agent-configuration/prompt-template-library.tsx`
- `moda-interact-commerce/tests/agent-configuration-template-ui.test.tsx`

### Work Completed

- Added the category-organised, filterable platform prompt-template library to Agent Configuration, including category metadata and enablement controls, multiple templates per category, template metadata and enablement controls, draft editing, publication validation, immutable published revision/hash display, historical disabled-state inspection, and dirty navigation protection.
- Kept category/template state and mutation orchestration under `src/studio/agent-configuration/`; `StudioWorkspace` only receives the existing module composition and no template domain state.
- Preserved mutation replay, conflict, and unknown-outcome handling through the COMMERCE-008 action port. ADMIN remains read-only; SUPER_ADMIN receives mutation controls outside development bypass.
- Repaired focused test result mocks with typed `TemplateResult<T>` helpers and made the loader dependency explicit with a memoized loader callback.

Requirements mapping:
- Production composition uses the COMMERCE-008 server action/port wiring in `agent-configuration-screen.tsx` and `production-studio-page.tsx`; no fixture port is used.
- Stable category slugs are displayed as identity while metadata update controls omit slug mutation.
- Empty drafts can be saved and blank publication errors are surfaced from the service result.
- Published revision number, immutable revision id, and SHA-256 content hash are displayed; published text is not presented as editable content.
- Disabled category/template history remains inspectable while new-authoring controls use enabled categories only.
- ADMIN controls are read-only and the UI renders no secret or session token.
- Template state/actions remain in `src/studio/agent-configuration/`; no new template domain state was added to `StudioWorkspace`.
- The implementation contains no active prompt mutation or live model/provider execution.

### Validation Results

- PASS: `npm exec vitest run tests/agent-configuration-template-ui.test.tsx tests/agent-configuration-templates.test.ts tests/auth-action-button.test.tsx tests/auth-permissions.test.ts tests/auth-entrypoints.test.ts tests/auth-origin.test.ts tests/auth-security-policy.test.ts tests/auth-platform-admin.test.ts tests/auth-environment.test.ts tests/auth-development-identity.test.ts` from the implementation worktree: the new template UI test, template service test, and six auth files passed (47 tests passed).
- BASELINE: the same focused run retained 4 unrelated failures: `tests/auth-development-identity.test.ts` reports `Prisma.sql is not a function` in the existing development identity fixture, and `tests/auth-entrypoints.test.ts` expects the existing route source to contain `createMcpService`. These failures are outside the six changed files and were not altered.
- PASS: `npm exec eslint src/studio/agent-configuration/prompt-template-library.tsx tests/agent-configuration-template-ui.test.tsx`.
- BASELINE: `npm run typecheck` exits 1 on existing commerce/database typing diagnostics in files such as `src/commerce/integration/backend.ts`, `src/commerce/integration/backend/publication-storage.ts`, `src/commerce/integration/studio/services.ts`, and `tests/c20-integration-fixture.test.ts`; no diagnostic names either repaired file.
- PASS: `git diff --check`.

### Deviations

The repository-wide typecheck and the full focused auth matrix are not green because of the documented unrelated baseline diagnostics above. No unrelated source was changed to mask or repair those failures.

### Assumptions

The existing COMMERCE-008 server-action wiring and current auth baseline are the accepted contracts for this task. The prior Attempt 1 implementation edits and user edits in the six listed files are all intentional and preserved.

### Unresolved Issues

The four unrelated focused auth failures and the existing repository-wide typecheck failures remain for their owning tasks/baseline tracking.

### Architectural Concerns

None

## Architect Review

### Review Status

Blocked

### Review Notes

Attempt 1 establishes the correct production ownership boundary and most of the platform template-library UI, but it cannot satisfy the durable DRAFT/history contract against the currently accepted COMMERCE-008 read port. The accepted `TemplatePort.getTemplate(...)` returns at most one revision and, without an explicit `revisionId`, resolves the latest `PUBLISHED` revision only. It exposes no revision enumeration operation. Consequently a pre-existing DRAFT becomes undiscoverable after refresh/reopen and the UI cannot render the required revision history without bypassing the accepted service boundary.

The review also found two local UI correctness defects that remain in COMMERCE-013 after the dependency is supplied:

1. `TemplateEditor` initialises `displayName` and `description` from the first selected template but is not keyed/synchronised when `selected.template.id` changes. Selecting another template therefore retains the previous template's editable metadata and can write those stale values into the newly selected template.
2. Dirty-state protection covers only draft prompt text and only Studio route navigation. Clicking another template calls `open(...)` directly and then clears dirty state, silently discarding an unsaved draft. Template metadata edits are not registered as dirty either. Internal template switching must use an explicit discard/stay guard and selected-template metadata edits must participate in the same dirty contract.

The production wiring itself is otherwise appropriately bounded: Agent Configuration receives the COMMERCE-008 server actions, ADMIN mutation controls are absent, no provider/tool execution is introduced, and replay/conflict/unknown results reuse the accepted operation-result model.

### Reviewed Files

- `moda-interact-commerce/src/studio/agent-configuration/prompt-template-library.tsx`
- `moda-interact-commerce/src/studio/agent-configuration/agent-configuration-screen.tsx`
- `moda-interact-commerce/src/studio/agent-configuration/template-contracts.ts`
- `moda-interact-commerce/src/studio/agent-configuration/template-server-actions.ts`
- `moda-interact-commerce/src/commerce/agent-configuration/prompt-template-service.ts`
- `moda-interact-commerce/components/production-studio-page.tsx`
- `moda-interact-commerce/components/studio-workspace.tsx`
- `moda-interact-commerce/tests/agent-configuration-template-ui.test.tsx`
- `moda-interact-commerce/tests/agent-configuration-production.test.tsx`

### Validation Reviewed

- Submitted focused template UI/service/auth validation: reported 47 passes with four documented unrelated auth baseline failures.
- Targeted ESLint: reported PASS.
- `git diff --check`: reported PASS.
- Repository-wide typecheck: reported existing unrelated diagnostics.
- Static review confirmed the revision-history read gap and selected-template/dirty-state defects above.

### Architecture Conformance

Blocked on `ARCH-021-COMMERCE-015`. COMMERCE-013 must continue to consume the canonical prompt-template service rather than querying Prisma directly or redefining revision lifecycle semantics in the UI.

### Follow-up

After `ARCH-021-COMMERCE-015` is architect-accepted Complete, return this same task to Ready for Attempt 2. Attempt 2 must:

1. consume the new read-only revision-history action/port and render durable DRAFT/PUBLISHED revision history for the selected template;
2. make an existing DRAFT discoverable and resumable after refresh/reopen, while keeping published revisions immutable;
3. reset/synchronise template metadata editor state when the selected template identity changes (for example by keying the editor by durable template id) and add a regression that switches between two templates before saving;
4. include selected-template metadata changes as dirty state and prevent template-to-template switching from silently discarding dirty draft/metadata state; cancellation must keep the current template/editor unchanged;
5. extend focused production composition coverage so `ProductionStudioPage` is proven to hand the real template server actions into Agent Configuration;
6. add focused regressions for durable draft resume/history and the dirty template-switch guard;
7. reconcile Work Items, Acceptance Criteria, Validation and Completion Report/worktree evidence before returning to review.

Do not add direct database reads to the UI, do not change template mutation semantics in COMMERCE-013, and do not begin COMMERCE-014.
