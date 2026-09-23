---
id: ARCH-021-COMMERCE-015
architecture_id: ARCH-021
title: Expose prompt-template revision history read contract
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 41
executor:
claimed_at:
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-008
enables:
  - ARCH-021-COMMERCE-013
created: 2026-09-23
updated: 2026-09-23
---

# Expose prompt-template revision history read contract

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

moda_architect

## Objective

Expose one bounded read-only prompt-template revision-history contract so Studio can resume an existing DRAFT and inspect immutable published history without changing accepted COMMERCE-008 mutation semantics.

## Context

COMMERCE-013 review showed that the accepted COMMERCE-008 port can resolve one exact revision or the latest published revision, but cannot enumerate a template's durable revisions. The template-library UI therefore cannot rediscover an existing DRAFT after refresh/reopen and cannot implement its required revision-history surface without bypassing the canonical service.

This task closes only that read-contract gap. COMMERCE-008 mutation, replay, CAS, audit, selectability and copy-on-use semantics remain authoritative and unchanged.

## Scope

- Extend the accepted prompt-template Studio/service contract with a read-only revision-list operation.
- Implement the operation in `PromptTemplateService` against `CommercePromptTemplateRevision`.
- Expose the operation through the authenticated template server-action boundary.
- Return both `DRAFT` and `PUBLISHED` revisions for one durable template id, including historical revisions of disabled templates/categories.
- Preserve exact revision identity, revision number, status, edit version, prompt text, content hash, creation time and publication time already defined by `PromptTemplateRevision`.
- Add focused service/server-action regressions.

### Deterministic contract

Add exactly this read shape to `TemplatePort`:

```ts
listRevisions(input: { templateId: string }): Promise<PromptTemplateRevision[]>;
```

Expose the corresponding server action:

```ts
listPromptTemplateRevisions(input: { templateId: string }): Promise<PromptTemplateRevision[]>;
```

The returned array MUST be ordered deterministically by:

```text
revisionNumber DESC
id ASC
```

The operation is an authenticated read available to `ADMIN` and `SUPER_ADMIN`; it MUST NOT require SUPER_ADMIN, create an audit event, or mutate state. An unknown/nonexistent template id returns an empty array. Disabled category/template state MUST NOT hide historical revisions from this read.

### Deterministic file boundary

Primary files:

```text
src/studio/agent-configuration/template-contracts.ts
src/commerce/agent-configuration/prompt-template-service.ts
src/studio/agent-configuration/template-server-actions.ts
tests/agent-configuration-templates.test.ts
```

A small additional focused test file is allowed if the existing service test becomes materially less readable.

## Out of Scope

- Any category/template/draft/publish mutation change.
- Changing `getTemplate(...)` default/selectable semantics.
- UI implementation; owned by COMMERCE-013.
- Platform/shop active prompt lifecycle; owned by COMMERCE-009/012/014.
- New persistence models or migrations.
- Provider/model/tool execution.

## Requirements

- Reuse the existing `PromptTemplateRevision` DTO exactly; do not create a second history DTO.
- Keep `getTemplate(...)` behaviour backwards compatible for COMMERCE-009 and other consumers.
- Do not filter out DRAFT revisions or revisions belonging to disabled template/category identities.
- Do not expose provider credentials, session tokens or unrelated customer/shop data.
- The query must be bounded to one `templateId` and deterministically ordered.

## Work Items

- [x] Add `TemplatePort.listRevisions({ templateId })`.
- [x] Implement deterministic read-only revision enumeration in `PromptTemplateService`.
- [x] Add ADMIN-authenticated `listPromptTemplateRevisions` server action.
- [x] Add focused revision-history/auth regressions.

## Interfaces / Contracts

Consumes:

- accepted COMMERCE-008 `PromptTemplateRevision` DTO and persistence;
- existing Studio ADMIN authentication.

Produces:

- read-only durable revision-history input for COMMERCE-013.

No mutation contract changes are produced.

## Dependencies

- ARCH-021-COMMERCE-008

## Enables

- ARCH-021-COMMERCE-013

## Acceptance Criteria

- [x] One template with multiple DRAFT/PUBLISHED revisions returns every revision in `revisionNumber DESC, id ASC` order.
- [x] Disabled category/template state does not hide historical revisions.
- [x] Unknown template ids return an empty array.
- [x] ADMIN can read revision history; no SUPER_ADMIN mutation privilege is required.
- [x] The read creates no `CommerceAuditEvent` and mutates no durable state.
- [x] Existing `getTemplate(...)`, create/update draft, publish, replay, CAS and selectability semantics are unchanged.

## Validation

- [x] focused prompt-template revision-history service tests
- [x] focused server-action/auth test
- [x] targeted lint/typecheck for changed files
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to review, return the Completion Report to moda_architect and STOP. Do not begin COMMERCE-013 automatically.

## Implementation Notes

This is a read-contract completion task, not a reopening of COMMERCE-008 lifecycle semantics. Prefer one direct Prisma `findMany` scoped by `templateId` with the deterministic ordering above.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

- `moda-interact-commerce/src/studio/agent-configuration/template-contracts.ts`
- `moda-interact-commerce/src/commerce/agent-configuration/prompt-template-service.ts`
- `moda-interact-commerce/src/studio/agent-configuration/template-server-actions.ts`
- `moda-interact-commerce/tests/agent-configuration-templates.test.ts`
- `moda-interact-commerce/tests/agent-configuration-template-server-actions.test.ts`

### Work Completed

- Added exactly `TemplatePort.listRevisions({ templateId }): Promise<PromptTemplateRevision[]>`.
- Implemented one-template Prisma `findMany` revision enumeration ordered by `revisionNumber DESC, id ASC`; the direct revision query includes DRAFT/PUBLISHED rows, does not inspect enabled state, and naturally returns `[]` for unknown IDs.
- Exposed `listPromptTemplateRevisions` behind `requireStudioAdmin`, with no mutation, audit, or SUPER_ADMIN requirement.
- Added service coverage for deterministic ordering, disabled-template history, unknown IDs, and no audit surface; added server-action coverage for ADMIN access and auth rejection.
- Existing `getTemplate`, mutation, replay, CAS, publication, and selectability paths were not changed.

### Validation Results

- `npm exec vitest run tests/agent-configuration-templates.test.ts tests/agent-configuration-template-server-actions.test.ts`: passed, 2 files and 9 tests.
- `npm exec eslint src/studio/agent-configuration/template-contracts.ts src/commerce/agent-configuration/prompt-template-service.ts src/studio/agent-configuration/template-server-actions.ts tests/agent-configuration-templates.test.ts tests/agent-configuration-template-server-actions.test.ts`: passed.
- `git diff --check`: passed.
- Task-owned TypeScript filter: no diagnostics in the new revision-list contract, server action, or focused tests. The existing `prompt-template-service.ts` `createDraft` baseline diagnostics remain at line 81 (`TS2347`, `TS2339`).

### Prepared Execution Evidence

Physical worktree isolation:

- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-015`
- parent branch: `task/ARCH-021-COMMERCE-015`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-015`
- implementation branch: `task/ARCH-021-COMMERCE-015`
- shared workspace checkout switched/mutated for task work: no
- another task worktree reused: no

Start-of-attempt synchronization:

- parent remote task branch fast-forwarded: `not-needed`
- parent `origin/main` incorporated: `already-current`
- implementation remote task branch fast-forwarded: `not-needed`
- implementation `origin/main` incorporated: `yes`
- parent claim: Attempt 2, committed and pushed as `3564d819aa5b6e3d237096c80f3b0d96481f4b2f`

Recursive implementation submodules:

- `git submodule sync --recursive`: passed
- `git submodule update --init --recursive`: passed
- recorded submodule commit: `database` at `98fdf715e54fe6df92ac6951facd104e410068f2`

### Deviations

- Full repository typecheck remains non-green due to the documented pre-existing baseline; no task-local typecheck regression was identified.

### Assumptions

- The existing Prisma-generated `commercePromptTemplateRevision.findMany` model surface is authoritative and returns all revision fields required by the existing `PromptTemplateRevision` mapper.
- Read authentication is enforced at the server-action boundary, consistent with neighboring template reads; the service port remains reusable for already-authenticated callers.

### Unresolved Issues

- None within task scope. Attempt 2 changed no implementation source or tests; it adds the launcher-provided canonical execution evidence requested by architect review.

### Architectural Concerns

None

### Requirements Mapping

- Revision-list port and exact DTO: `template-contracts.ts` and service implementation.
- Deterministic one-template ordering and disabled/unknown behavior: service regression in `agent-configuration-templates.test.ts`.
- ADMIN-authenticated read boundary with no SUPER_ADMIN privilege: `template-server-actions.ts` and `agent-configuration-template-server-actions.test.ts`.
- No audit or durable mutation: direct non-transactional read plus regression assertion that the test database has no audit surface.
- COMMERCE-008 semantics: no changes outside the new read method/action and focused regressions.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 supplies the exact prepared-execution evidence requested after Attempt 1. The recorded launcher state shows canonical sibling parent and implementation worktrees, matching `task/ARCH-021-COMMERCE-015` branches, start-of-attempt synchronization, an Attempt 2 claim committed and pushed in the parent branch, and recursive implementation-submodule materialisation with `database` recorded at `98fdf715e54fe6df92ac6951facd104e410068f2`.

The implementation remains substantively identical to the already-conformant Attempt 1 submission: the five task-owned implementation/test files are byte-identical between the Attempt 1 and Attempt 2 review archives. No source or test churn was introduced merely to satisfy the workflow correction.

The accepted capability remains exactly the bounded COMMERCE-015 contract: `TemplatePort.listRevisions({ templateId })`, deterministic one-template revision enumeration ordered by `revisionNumber DESC, id ASC`, and one ADMIN-authenticated read action. It reuses `PromptTemplateRevision`, exposes DRAFT/PUBLISHED history regardless of enabled state, returns `[]` for an unknown template id, creates no audit receipt, and does not modify COMMERCE-008 mutation/replay/CAS/publish/selectability semantics.

### Reviewed Files

- `moda-interact-commerce/src/studio/agent-configuration/template-contracts.ts`
- `moda-interact-commerce/src/commerce/agent-configuration/prompt-template-service.ts`
- `moda-interact-commerce/src/studio/agent-configuration/template-server-actions.ts`
- `moda-interact-commerce/tests/agent-configuration-templates.test.ts`
- `moda-interact-commerce/tests/agent-configuration-template-server-actions.test.ts`
- `docs/decisions/commerce/ARCH-021/COMMERCE-015-expose-prompt-template-revision-history.md`

### Validation Reviewed

- Attempt 2 reported focused Vitest: 2 files / 9 tests passed.
- Attempt 2 reported targeted ESLint: passed.
- Attempt 2 reported `git diff --check`: passed.
- Task-owned TypeScript filtering reports no new revision-history diagnostics; only the documented existing `prompt-template-service.ts` baseline diagnostics remain.
- Prepared execution evidence reviewed: canonical parent/implementation worktrees, matching task branches, start-of-attempt synchronization, Attempt 2 claim commit `3564d819aa5b6e3d237096c80f3b0d96481f4b2f`, recursive submodule sync/update, and database submodule commit `98fdf715e54fe6df92ac6951facd104e410068f2`.
- The supplied archive does not include `node_modules`, so the architect did not independently rerun Vitest/ESLint.

### Architecture Conformance

Conformant. The implementation and execution evidence now satisfy the task contract and the architect worktree-isolation protocol. No mutation semantics, schema, UI, provider execution or unrelated repository ownership were changed.

### Follow-up

COMMERCE-015 is Complete. Its dependency gate on ARCH-021-COMMERCE-013 is satisfied. Return COMMERCE-013 to `ready` with `attempt: 1` retained; its next claim becomes Attempt 2 and must execute the bounded UI correction contract already recorded in that task's Architect Review. Do not start COMMERCE-013 automatically from this acceptance.
