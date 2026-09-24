---
id: ARCH-021-COMMERCE-026
architecture_id: ARCH-021
title: Simplify prompt-template authoring to current template content
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-DATABASE-002
  - ARCH-021-COMMERCE-008
  - ARCH-021-COMMERCE-013
  - ARCH-021-COMMERCE-015
enables:
  - ARCH-021-COMMERCE-028
created: 2026-09-24
updated: 2026-09-24
---

# Simplify prompt-template authoring to current template content

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`


## Objective

Remove prompt-template draft/publish/revision machinery while keeping first-class template categories, current template content, platform-admin authoring, audit, CAS, and copy-on-use into immutable Agent Prompt revisions.

## Context

Prompt templates are an authoring convenience. Runtime behavior requires an effective immutable Agent Prompt revision, not a template revision history. DATABASE-002 moves current template text onto `CommercePromptTemplate.promptText` and removes `CommercePromptTemplateRevision`.

## Scope

Primary files:

```text
src/commerce/agent-configuration/prompt-template-service.ts
src/studio/agent-configuration/template-contracts.ts
src/studio/agent-configuration/template-server-actions.ts
src/studio/agent-configuration/prompt-template-library.tsx
tests/agent-configuration-template.test.ts
```

## Out of Scope

- Removing `CommercePromptTemplateCategory`.
- Merchant editing of platform templates.
- Agent Prompt publish lifecycle.
- Agent Configuration model/prompt service changes owned by COMMERCE-025.
- Generic Studio composition changes.

## Requirements

### R1. Exact service surface

The template service must expose only:

```text
listCategories
createCategory
updateCategory
setCategoryEnabled
listTemplates
getTemplate
createTemplate
updateTemplate
setTemplateEnabled
```

Remove template methods equivalent to `listRevisions`, `createDraft`, `updateDraft`, `publishRevision`.

### R2. Exact template DTO

Template DTO includes:

```text
id
key
categoryId
displayName
description
promptText
enabled
editVersion
createdAt
updatedAt
```

No template revision DTO is returned.

### R3. Template CAS

`updateTemplate` updates metadata and/or `promptText` using `expectedEditVersion` and increments `editVersion` exactly once.

Category CAS remains `expectedEditVersion` on the category row.

### R4. Explicit errors and lightweight reconciliation

Use the same result/error rules as COMMERCE-025:

```text
no kind:'unknown'
no payloadHash
no stored result replay
DATABASE_UNAVAILABLE remains explicit
operationId is audit/reconciliation correlation only
```

Template mutations write `CommerceAuditEvent.operationId` atomically.

### R5. Copy-on-use behavior

Remove all UI/service references to `sourceTemplateRevisionId`.

The Agent Prompt service in COMMERCE-025 owns copying `CommercePromptTemplate.promptText` into a new prompt DRAFT and storing `sourceTemplateId`.

Changing template text after copying must never mutate existing Agent Prompt revisions.

### R6. UI exact behavior

`PromptTemplateLibrary` must show categories and current templates grouped by category.

For a selected template, show/edit:

```text
display name
description
current prompt text
enabled state
editVersion-backed save
```

Remove:

```text
revision history
Save draft
Update draft
Publish revision
published revision hash/status copy
```

Keep category create/update/enable/disable and multiple templates per category.

## Work Items

- [ ] Replace revision service API with R1 surface.
- [ ] Replace template contracts/DTOs with R2.
- [ ] Implement direct CAS update of promptText.
- [ ] Remove template revision UI/history.
- [ ] Update audit/reconciliation behavior.
- [ ] Update focused tests.

## Interfaces / Contracts

Consumes `CommercePromptTemplateCategory`, `CommercePromptTemplate.promptText`, and `CommerceAuditEvent.operationId`.

## Dependencies

- ARCH-021-DATABASE-002
- ARCH-021-COMMERCE-008
- ARCH-021-COMMERCE-013
- ARCH-021-COMMERCE-015

## Enables

- ARCH-021-COMMERCE-028

## Acceptance Criteria

- [ ] Categories remain first-class and data-driven.
- [ ] Multiple templates may exist in one category.
- [ ] Template content is edited directly with CAS.
- [ ] No template revision persistence/service/UI remains.
- [ ] Existing Agent Prompt revisions remain unaffected by later template edits.
- [ ] Errors are explicit and reconcilable; none are swallowed into `unknown`.

## Validation

- [ ] focused template service tests
- [ ] focused template UI tests
- [ ] stale CAS test
- [ ] DB-unavailable error test
- [ ] operation reconciliation test
- [ ] targeted ESLint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

Do not remove categories and do not move templates into a JSON blob. The simplification removes template revision lifecycle only.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

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
