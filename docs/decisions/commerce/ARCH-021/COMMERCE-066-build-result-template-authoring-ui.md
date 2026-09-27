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
status: in_progress
priority: 74
executor: copilot
claimed_at: 2026-09-27T15:44:07Z
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

- [ ] Add reusable `ResultTemplateTab` component.
- [ ] Add text-template structured controls and binding insertion.
- [ ] Add items-template collection/item controls.
- [ ] Present required/optional field metadata.
- [ ] Preserve invalid local authoring values.
- [ ] Wire non-mutating validation/staleness behavior to COMMERCE-063.
- [ ] Add read-only canonical disclosure if useful.
- [ ] Add focused component tests independent of parent Tool tabs.

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

- [ ] Text mode shows schema-derived scalar fields and inserts exact canonical tokens.
- [ ] Items mode only offers supported collection paths.
- [ ] Item token paths are derived from the selected item schema.
- [ ] Optional fields are visibly distinguishable from guaranteed fields.
- [ ] Invalid local text is retained after failed validation.
- [ ] Validation errors appear in the Result Template surface.
- [ ] Validation is stale after template or result-contract changes.
- [ ] The component contains no Shopify/External-specific path derivation.
- [ ] No Tool/database write occurs.
- [ ] No new rich-text dependency is required.

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

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

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
