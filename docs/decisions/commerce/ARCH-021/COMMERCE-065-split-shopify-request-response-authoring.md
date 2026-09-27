---
id: ARCH-021-COMMERCE-065
architecture_id: ARCH-021
title: Split Shopify Admin Request and Response authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 75
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-062
  - ARCH-021-COMMERCE-064
enables:
  - ARCH-021-COMMERCE-068
created: 2026-09-27
updated: 2026-09-27
---

# Split Shopify Admin Request and Response authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make Shopify Admin Tool authoring follow the same conceptual Request/Response separation as External HTTP: Request owns the Admin GraphQL invocation, while Response owns `resultPath` and the compiler-derived read-only `resultSchema` supplied by COMMERCE-062.

## Context

The current Shopify Admin editor places GraphQL, operation name, variable mappings, `resultPath` and raw editable `resultSchema` together in Request, while Response is a placeholder saying that the schema is authored in Request.

That duplicates schema knowledge already available from the pinned Admin query and prevents the result contract from becoming a clean source for Result Template fields.

COMMERCE-064 has already established the Admin Explore round trip. This task changes only the Request/Response authoring responsibility; general traversal/gating remains deferred.

## Scope

Expected implementation areas include:

```text
src/studio/tools/shopify-admin-editor.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx              # persisted DRAFT parity where this authoring surface exists
src/studio/tools/authoring/                    # focused Shopify Response component if useful
src/studio/tools/*server-actions*.ts           # consume COMMERCE-062 derivation action
app/styles.css

tests/shopify-admin-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

## Out of Scope

- Explore Shopify schema/query-builder implementation; COMMERCE-064 owns it.
- Result Template tab; COMMERCE-066/068 own it.
- General tab gating/Next/Back coordination.
- Provider execution or live Test UI.
- Manual editing of Admin `resultSchema`.
- External HTTP Response behavior.
- Database schema changes.

## Requirements

### R1 — Request owns only invocation authoring

The Shopify Request tab contains the Admin invocation concerns:

```text
GraphQL document
operation name
variable mappings
Explore Shopify entry point
Admin query validation status/diagnostics
```

Remove editable `resultPath` and editable raw `resultSchema` from Request.

Manual GraphQL remains fully editable.

### R2 — Response owns result selection

The Shopify Response tab contains:

```text
resultPath
non-mutating derive/validate result contract action/status
derived result shape/fields
read-only derived resultSchema disclosure where useful
```

Do not duplicate Request controls here.

### R3 — resultSchema is compiler-produced

When the current Admin document/resultPath is derivable, update the canonical local Tool candidate's `execution.resultSchema` with the exact schema returned by COMMERCE-062.

The author does not type/edit the schema directly.

Temporarily invalid `resultPath` input remains visible locally with Response-local diagnostics; it must not silently revert.

### R4 — schema derivation becomes stale when Request changes

Any change to Admin query identity that can alter the selected result must invalidate the currently displayed derivation success, including:

```text
document
operationName
apiVersion/schemaHash where authoring can change them
resultPath
```

Variable mapping changes do not change the output shape but remain governed by Request validation.

Do not implement tab gating; only mark the Response derivation stale.

### R5 — show the actual derived fields

Present the derived result structure in an understandable read-only form sufficient for an author to see what `data.values` will contain.

Do not require users to understand raw JSON Schema to determine available fields.

A technical read-only schema disclosure may remain available as secondary detail.

### R6 — local-only lifecycle remains intact

For new Tools, Request/Response authoring stays in the existing local/session draft until final Create.

For persisted DRAFTs, deriving the result contract does not save the DRAFT automatically.

### R7 — do not change general navigation semantics

Request and Response remain freely navigable. No tab becomes locked because query/result validation has not been run.

## Work Items

- [ ] Remove Result path/schema controls from Shopify Request UI.
- [ ] Add Shopify Response authoring component/surface.
- [ ] Wire Response derivation to COMMERCE-062.
- [ ] Promote only valid derived schemas into canonical local Tool state.
- [ ] Retain invalid resultPath text and show actionable Response-local diagnostics.
- [ ] Invalidate stale derivation when query/resultPath changes.
- [ ] Show derived values structure/read-only schema.
- [ ] Cover new Tool and persisted DRAFT authoring parity where applicable.

## Interfaces / Contracts

Consumes COMMERCE-062's non-mutating Admin result-contract derivation.

Produces no new runtime/durable contract beyond the already-canonical persisted `execution.resultSchema`.

## Dependencies

- `ARCH-021-COMMERCE-062`
- `ARCH-021-COMMERCE-064`

## Enables

- `ARCH-021-COMMERCE-068`

## Acceptance Criteria

- [ ] Shopify Request contains document, operation and mappings but no editable result schema.
- [ ] Shopify Response owns resultPath.
- [ ] A valid resultPath derives and installs the canonical local `resultSchema`.
- [ ] Invalid resultPath text remains visible and actionable.
- [ ] Query changes invalidate prior derived-result success.
- [ ] Authors can inspect the resulting `data.values` shape without editing JSON Schema.
- [ ] New Tool derivation causes no durable write.
- [ ] Persisted-DRAFT derivation does not save automatically.
- [ ] Manual GraphQL remains supported.
- [ ] Tab navigation remains ungated.

## Validation

- [ ] Shopify Admin Request UI tests
- [ ] Shopify Admin Response UI tests
- [ ] stale-derivation regression tests
- [ ] new/persisted authoring lifecycle tests
- [ ] targeted lint
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-068 or COMMERCE-069.

## Implementation Notes

Keep output-schema derivation on the canonical COMMERCE-062 boundary. React must not reconstruct GraphQL response types independently.

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
