---
id: ARCH-021-COMMERCE-079
architecture_id: ARCH-021
title: Align persisted DRAFT authoring with the Tool creation ownership model
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 76
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-078
enables:
  - ARCH-021-SYSTEM-TEST-002
created: 2026-09-28
updated: 2026-09-28
---

# Align persisted DRAFT authoring with the Tool creation ownership model

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Apply the same Tool Definition/Request/Response/Result Template/Test/Review ownership model to persisted External HTTP and Shopify Admin DRAFTs while preserving explicit CAS Save/Validate/Publish semantics.

## Context

COMMERCE-078 changes the new Tool creation flow. The current `ToolEditor` independently retains the regressed Agent Contract/template composition and has provider-specific layout divergence. Leaving that state would mean a Tool changes ownership models immediately after first Save.

This task is separate because persisted DRAFTs have different failure/persistence semantics: immutable Tool identity already exists, Save uses revision `editVersion` CAS, validation/publication operate on a saved revision, and Cancel must revert local edits rather than deleting a not-yet-created Tool.

## Scope

Primary implementation:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/tool-authoring-tabs.tsx           # consume shared registry/composition
src/studio/tools/authoring/tool-definition-tab.tsx           # consume persisted mode
src/studio/tools/authoring/result-template-tab.tsx           # consume
src/studio/tools/authoring/review-tab.tsx
```

Focused tests:

```text
tests/external-tools-ui.test.tsx
tests/shopify-admin-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```


## Out of Scope

- Changing revision lifecycle, CAS rules or publication proof.
- Making immutable MCP name or provider kind mutable after Tool creation.
- Updating Tool-level display name/metadata through a draft save unless an already-existing explicit metadata action is intentionally invoked outside this task.
- External/Shopify new live-Test backend behaviour (C080/C082).
- Database changes.
- Non-External/non-Shopify legacy Tool editor cleanup unrelated to the supported authoring flow.

## Requirements

### R1 — persisted supported DRAFTs use the same six-step sequence

For `EXTERNAL_HTTP` and `SHOPIFY_ADMIN_GRAPHQL` DRAFTs, expose exactly:

```text
Tool Definition
Request
Response
Result Template
Test
Review
```

No Agent Contract tab is exposed.

### R2 — persisted Tool Definition has explicit mutability

Show in Tool Definition:

```text
MCP name          read-only
Display name      read-only summary of Tool metadata
Tool type         read-only
Description       editable definition.description
Definition version editable definition.definitionVersion
```

Do not introduce a provider-kind migration. Do not mutate Tool-level display name from draft Save.

### R3 — Request and Result Template ownership matches new Tools

External and Shopify input schema is edited only in Request. `responseTemplate` is edited only in Result Template. Result Template bindings use the same production-envelope result contract rules as C078.

### R4 — persisted Review derives Agent Contract and preserves revision operations

Review shows the same separate read-only cards as C078, including derived Agent Contract (`definitionVersion`, `description`, `inputSchema`) and Result Template.

Persisted Review retains the existing supported actions/authorization:

```text
Cancel unsaved changes
Save draft
Validate (where currently supported)
Publish controls for SUPER_ADMIN where currently supported
```

`Cancel unsaved changes` must restore the current selected revision's last saved definition and editor buffers, clear transient validation/Test state, set dirty false, and stay on the same revision route. It must not create another revision and must not call a mutation Server Action.

### R5 — Save remains one CAS update

`Save draft` must assemble the complete current candidate and call the existing `updateToolDraft` exactly once with the selected revision id and current `expectedEditVersion`. Successful Save replaces local buffers with the canonical returned revision and current editVersion. A CAS conflict remains visible and must not silently overwrite.

### R6 — Explore Shopify remains exact-session safe

For persisted Shopify DRAFTs, Request -> Explore -> Use in tool -> Request must preserve `toolId`, `toolRevisionId`, tab/editor buffers and the existing sessionStorage identity checks. Returning from Explore must not auto-save.

## Work Items

- [ ] Apply the six-step shared flow to persisted External HTTP DRAFTs.
- [ ] Apply the six-step shared flow to persisted Shopify Admin DRAFTs.
- [ ] Add persisted Tool Definition read-only/editable field split.
- [ ] Move External persisted input schema to Request.
- [ ] Integrate persisted ResultTemplateTab with production-envelope contracts.
- [ ] Remove persisted Agent Contract authoring tab/use.
- [ ] Derive read-only Agent Contract in Review.
- [ ] Add `Cancel unsaved changes` reset semantics.
- [ ] Preserve one-CAS Save and canonical refresh/editVersion update.
- [ ] Preserve persisted Shopify Explore handoff without auto-save.
- [ ] Add persisted-provider regression coverage.

## Interfaces / Contracts

Consumes C078's shared UI ownership model and existing persisted lifecycle actions:

```text
updateToolDraft
publishToolRevision
validateExternalToolDefinitionAction
ToolAuthoringSession(mode="existing")
```

No new database or cross-repository contract.

## Dependencies

- ARCH-021-COMMERCE-078

## Enables

- ARCH-021-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Persisted External and Shopify DRAFTs expose the same six-step sequence as new Tools.
- [ ] MCP name/provider kind are visibly read-only in Tool Definition.
- [ ] Input schema is owned by Request; Result Template owns `responseTemplate`.
- [ ] Agent Contract is review-only and contains no Result Template content.
- [ ] Cancel restores the exact saved revision locally with zero mutation call.
- [ ] Save performs exactly one `updateToolDraft` CAS write using current editVersion.
- [ ] CAS conflicts remain visible and do not overwrite newer state.
- [ ] Save/Publish authorization and current publication gates are unchanged.
- [ ] Persisted Shopify Explore return remains session-isolated and non-durable until Save.

## Validation

- [ ] `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx`
- [ ] focused CAS Save and Cancel-zero-write regressions
- [ ] focused persisted Explore round-trip regression
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Do not merge Tool-level metadata updates into revision Save. The task is about authoring ownership parity, not redefining the Tool/ToolRevision data model.

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
