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
status: review
priority: 41
executor: null
claimed_at: null
attempt: 1
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

- [ ] Add `TemplatePort.listRevisions({ templateId })`.
- [ ] Implement deterministic read-only revision enumeration in `PromptTemplateService`.
- [ ] Add ADMIN-authenticated `listPromptTemplateRevisions` server action.
- [ ] Add focused revision-history/auth regressions.

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

- [ ] One template with multiple DRAFT/PUBLISHED revisions returns every revision in `revisionNumber DESC, id ASC` order.
- [ ] Disabled category/template state does not hide historical revisions.
- [ ] Unknown template ids return an empty array.
- [ ] ADMIN can read revision history; no SUPER_ADMIN mutation privilege is required.
- [ ] The read creates no `CommerceAuditEvent` and mutates no durable state.
- [ ] Existing `getTemplate(...)`, create/update draft, publish, replay, CAS and selectability semantics are unchanged.

## Validation

- [ ] focused prompt-template revision-history service tests
- [ ] focused server-action/auth test
- [ ] targeted lint/typecheck for changed files
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to review, return the Completion Report to moda_architect and STOP. Do not begin COMMERCE-013 automatically.

## Implementation Notes

This is a read-contract completion task, not a reopening of COMMERCE-008 lifecycle semantics. Prefer one direct Prisma `findMany` scoped by `templateId` with the deterministic ordering above.

## Completion Report

### Status

Ready for Review

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
- `git diff --check`: passed; staged diff check also passed before commit.
- `npm run typecheck`: failed on the repository baseline with 237 errors across 16 files. The only touched-file entry is the pre-existing `createDraft` diagnostics at service line 81; no diagnostic points to the new revision-list method, server action, or focused tests.

### Deviations

- Full repository typecheck remains non-green due to the documented pre-existing baseline; no task-local typecheck regression was identified.

### Assumptions

- The existing Prisma-generated `commercePromptTemplateRevision.findMany` model surface is authoritative and returns all revision fields required by the existing `PromptTemplateRevision` mapper.
- Read authentication is enforced at the server-action boundary, consistent with neighboring template reads; the service port remains reusable for already-authenticated callers.

### Unresolved Issues

 - None within task scope.

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
