---
id: ARCH-021-COMMERCE-066
architecture_id: ARCH-021
title: Build schema-backed Result Template authoring UI
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
  - ARCH-021-COMMERCE-063
enables:
  - ARCH-021-COMMERCE-068
created: 2026-09-27
updated: 2026-09-27
---

# Build schema-backed Result Template authoring UI

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Build a reusable `ResultTemplateTab` presentation/controller that authors the existing canonical `responseTemplate` from COMMERCE-063's derived `ToolResultContract`, exposes schema-backed fields/tokens instead of requiring raw path guessing, and validates locally/server-authoritatively without yet changing Tool tab registration or Agent Contract/Review composition.

## Context

The runtime already supports two persisted response-template forms:

```text
kind: text
kind: items
```

The current UI exposes `responseTemplate` as raw JSON in Agent Contract. COMMERCE-063 provides the source-neutral field/collection catalogue and validator. This task builds the dedicated UI component in isolation so it can be reviewed independently from broader editor integration.

## Scope

Expected implementation areas include:

```text
src/studio/tools/authoring/result-template-tab.tsx
focused result-template hooks/helpers if useful
app/styles.css                         # bounded UI additions only

tests/result-template-tab.test.tsx or equivalent
```

## Out of Scope

- Registering the new tab in NewToolEditor/ToolEditor; COMMERCE-068 owns integration.
- Removing response template from Agent Contract.
- Review-tab changes.
- Request/Response UI changes.
- New response-template syntax.
- Tiptap/Novel or another rich-text dependency as an architectural requirement.
- Provider execution/persistence.

## Requirements

### R1 — consume `ToolResultContract`, not provider-specific schemas

The component receives the derived contract/binding catalogue from COMMERCE-063 and must not know whether it originated from Shopify Admin or External HTTP.

### R2 — text-template authoring

For `kind: text`, provide structured controls for:

```text
text
unavailable fallback
```

Expose clickable/insertable scalar bindings generated from the contract. Display friendly labels while preserving the exact canonical token, for example:

```text
[Price › Amount]
-> {{result.values.price.amount}}
```

Do not invent paths from display labels.

### R3 — items-template authoring

For `kind: items`, provide structured controls for:

```text
collection/itemsPath
item template
empty fallback
unavailable fallback
```

The collection chooser is limited to collection bindings COMMERCE-063 marks compatible with the current item-template grammar.

Item field tokens use exact `{{item.*}}` paths supplied by the contract.

### R4 — communicate optionality

Where a field is optional in the output contract, show that fact to the author. Do not present an optional field as guaranteed.

Using an optional field remains governed by the existing `unavailable` fallback/runtime semantics unless the canonical validator rejects it.

### R5 — retain invalid local text

Temporarily malformed/incomplete template text must remain visible so the author can fix it. Do not snap back to the last canonical template on validation failure.

Only a valid parseable `responseTemplate` is promoted to canonical local Tool state by the parent integration.

### R6 — validate through COMMERCE-063

Provide one clear action equivalent to:

```text
Validate result template
```

Display deterministic field-local issues returned by the canonical Result Template validator.

Validation success becomes stale when template text/type/collection or the supplied result contract changes.

### R7 — no raw JSON as the primary UX

The primary surface is structured template authoring. A secondary read-only canonical JSON disclosure is allowed for technical visibility, but the author should not have to type the response-template JSON object manually.

### R8 — bounded editor behavior

Retain existing template size/syntax bounds. Inserted tokens must be plain text tokens and must not introduce HTML execution/content-editable trust assumptions.

## Work Items

- [x] Add reusable `ResultTemplateTab` component.
- [x] Add text-template structured controls and binding insertion.
- [x] Add items-template collection/item controls.
- [x] Present required/optional field metadata.
- [x] Preserve invalid local authoring values.
- [x] Wire non-mutating validation/staleness behavior to COMMERCE-063.
- [x] Assess read-only canonical disclosure; it is not needed for this structured primary surface.
- [x] Add focused component tests independent of parent Tool tabs.

## Interfaces / Contracts

Consumes:

```text
ToolResultContract/binding catalogue
current responseTemplate
COMMERCE-063 validation action/result
```

Emits local authoring callbacks only. It does not persist Tool state.

## Dependencies

- `ARCH-021-COMMERCE-063`

## Enables

- `ARCH-021-COMMERCE-068`

## Acceptance Criteria

- [x] Text mode shows schema-derived scalar fields and inserts exact canonical tokens.
- [x] Items mode only offers supported collection paths.
- [x] Item token paths are derived from the selected item schema.
- [x] Optional fields are visibly distinguishable from guaranteed fields.
- [x] Invalid local text is retained after failed validation.
- [x] Validation errors appear in the Result Template surface.
- [x] Validation is stale after template or result-contract changes.
- [x] The component contains no Shopify/External-specific path derivation.
- [x] No Tool/database write occurs.
- [x] No new rich-text dependency is required.

## Validation

- [ ] focused ResultTemplateTab tests
- [ ] token insertion/path tests
- [ ] text/items mode tests
- [ ] invalid-local-state/staleness tests
- [ ] targeted lint
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-068.

## Implementation Notes

Keep component responsibilities bounded. A simple textarea plus schema-backed insertion controls is sufficient; do not introduce a rich editor solely to render visual pills.

## Completion Report

### Status

Ready for Review (Attempt 1).

### Files Changed

Changed in `moda-interact-commerce`:

- `src/studio/tools/authoring/result-template-tab.tsx`
- `tests/result-template-tab.test.tsx`

### Work Completed

Added a standalone, provider-neutral `ResultTemplateTab` that consumes COMMERCE-063's derived `ToolResultContract` and an injected canonical validation function. Text and items modes expose bounded plain-text fields, exact schema-derived tokens, supported collection choices, and required/optional metadata. Incomplete local drafts remain visible; only `ResponseTemplateSchema`-parseable values are emitted to the parent. Validation issues are rendered by canonical field path, and a validation result becomes stale when the draft or supplied binding contract changes. No Tool registration, persistence, database write, or rich-text dependency was added.

Implementation commit `0c1f5de` is pushed to `task/ARCH-021-COMMERCE-066`.

### Validation Results

Passed:

- `./node_modules/.bin/vitest run tests/result-template-tab.test.tsx` — 1 file, 4 tests.
- Targeted ESLint on the component and component test.
- Changed-file editor TypeScript diagnostics — no errors in either changed file.
- `git diff --check`.

The task worktree had no dependency directory, so focused validation temporarily linked the already-installed Commerce `node_modules` from the canonical source checkout; that symlink was removed after validation and is not part of the task changes.

### Deviations

None. The component remains standalone; tab registration and parent Tool-editor composition remain with COMMERCE-068.

### Assumptions

The parent integration supplies the COMMERCE-063 validator through `onValidate`; this keeps authorization/server-action composition outside the isolated presentation component while allowing local or server-authoritative validation.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Launcher Evidence

Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-066` on `task/ARCH-021-COMMERCE-066`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-066` on the same task branch. Shared workspace checkout switched/mutated for task work: no. Shared implementation checkout switched/mutated for task work: no. Another task worktree reused: no.

Start-of-attempt synchronization: parent remote task branch fast-forwarded `not-needed`; parent `origin/main` incorporated `already-current`; implementation remote task branch fast-forwarded `not-needed`; implementation `origin/main` incorporated `already-current`. Parent start HEAD: `43d061bbc99e4eaa6e5e2c8af9a04e1adbdcfad4`. Implementation start HEAD: `0816bda450586bb0bc45069499fbc028a0b691cd`.

Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database` initialized at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`. Launcher claim commit: `7b1ee98e31598a15ba99793dca9a82c7a12b4087`.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
