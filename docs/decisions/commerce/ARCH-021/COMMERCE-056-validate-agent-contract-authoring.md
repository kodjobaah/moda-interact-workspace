---
id: ARCH-021-COMMERCE-056
architecture_id: ARCH-021
title: Validate and clarify Agent contract authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 71
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-039
  - ARCH-021-COMMERCE-043
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Validate and clarify Agent contract authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make the existing Agent contract tab a self-contained, non-mutating validation checkpoint for the Tool fields exposed to the CommerceAgent: definition version, agent description, agent input schema and agent response template. Validation must reuse the canonical Tool-definition/publication rules, retain temporarily invalid authoring text locally with field-specific diagnostics, and perform no Tool persistence or provider I/O.

## Context

Manual validation of the completed local-only Tool authoring flow found that the Agent contract tab already has the correct structural boundary:

```text
src/studio/tools/authoring/agent-contract-tab.tsx
```

It is already composed by the new-Tool and persisted-DRAFT editors, so this task does **not** extract another component or redesign the tab structure.

The tab currently exposes:

```text
Definition SemVer
Description
Input JSON Schema
Response template
```

but its local feedback is largely limited to JSON parse failure. The canonical Commerce contracts already define stronger rules for semantic versioning, description bounds, the supported bounded input-schema subset, forbidden authority/credential inputs, response-template syntax/tokens and response-template compatibility with the processed result contract. Authors should discover those problems in the Agent contract tab rather than only at Review/Create/Publish.

The authoring lifecycle established by COMMERCE-039 remains authoritative:

```text
raw local form state
    -> may temporarily be incomplete/invalid

canonical local Tool candidate
    -> schema-valid authoring state

final Create / later persisted-DRAFT Save
    -> only durable boundary
```

Validation itself is never a persistence operation.

## Scope

Primary files are expected to include:

```text
src/commerce/tool-authoring/                       # named Agent-contract validation boundary/helper
src/commerce/tool-definition/contracts.ts          # consume/extract existing canonical helpers only when needed
src/commerce/tool-definition/publication.ts        # reuse/extract template-compatibility logic only when needed

src/studio/tools/authoring/agent-contract-tab.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/*server-actions*.ts               # bounded non-mutating validation action if required

app/styles.css                                     # only small validation/help presentation if needed

tests/tool-authoring-screen.test.tsx
tests/external-tools-ui.test.tsx                   # where the shared Agent tab is exercised
tests/shopify-admin-tools-ui.test.tsx              # parity where the shared Agent tab is used
tests/*agent-contract*                             # focused tests may be added
```

Use the repository's existing authoring action/result conventions. Exact filenames may follow current ownership and module conventions.

## Out of Scope

- Extracting the Agent contract form into another React component; `AgentContractTab` already owns that boundary.
- Request-tab, Response-tab, Test-tab or Review-tab redesign.
- COMMERCE-053 Automatic response generation.
- COMMERCE-054/055 live Test execution or Test UI.
- Provider DNS/network calls, credential resolution/decryption or live execution.
- Persisting a new Tool, ToolRevision, audit event, validation receipt or publication proof.
- Saving a persisted DRAFT merely because validation succeeded.
- Phase 2 tab gating, locked tabs or mandatory Next/Previous progression.
- Changing the Tool descriptor or another cross-service contract.
- Database/Prisma schema changes.
- Weakening final Create/Save/Publish server validation.

## Requirements

### R1 — preserve the existing component boundary

`AgentContractTab` remains the bounded presentation component for this authoring surface.

Do not duplicate its fields back into `NewToolEditor` or `ToolEditor`, and do not create another architecture task/component merely to split the four-field form further.

Parent editors may own orchestration/state and pass validation callbacks/results into the existing tab.

### R2 — add a named Agent-contract validation boundary

Add/reuse one non-mutating, server-authoritative validation boundary for the current Agent contract. It must validate the Agent-facing contract without requiring the complete Request/Test/Review flow to be valid.

The validation input should contain only the current Agent-contract values plus the minimum current result-contract context required to validate response-template paths, conceptually:

```text
definitionVersion
description
inputSchema
responseTemplate
current processed-result/output contract context
```

Do not make Agent-contract validation perform Request construction, connection lookup, provider observation, live execution or Tool persistence.

Reuse/extract canonical validation logic from the existing Commerce Tool-definition/publication contracts rather than maintaining a second set of SemVer, input-schema or response-template rules.

### R3 — validate the complete Agent-facing contract

At minimum validate and report deterministic issues for:

```text
Definition version
- valid semantic version syntax/bounds required by the canonical Tool contract

Agent description
- required/non-empty
- canonical maximum length

Agent input schema
- valid JSON object
- accepted bounded InputSchema subset
- supported nested/array/scalar forms only
- canonical property/count/size bounds
- authority/credential inputs remain forbidden

Agent response template
- valid JSON object
- canonical text/items template shape
- bounded fixed/text fields
- valid {{result.*}} / {{item.*}} tokens
- no unknown/non-scalar referenced result paths
- itemsPath resolves to a valid list/item result when using an items template
- compatibility with the current processed-result/output contract
```

Diagnostics must use deterministic paths suitable for field-local UI presentation, for example:

```text
/definitionVersion
/description
/inputSchema/...
/responseTemplate/...
```

Do not expose raw internal exceptions as the normal author-facing message.

### R4 — preserve raw local authoring state

The tab must distinguish authoring memory from durable persistence.

Temporarily invalid user input MUST remain visible in local form state so it can be corrected, including:

```text
malformed Input schema JSON
malformed Response template JSON
unsupported Input schema content
invalid response-template tokens/paths
invalid Definition version
```

Do not snap the field back to the last valid value merely because the canonical parser rejects the current text.

Only parseable/canonical values may be promoted into the canonical local Tool candidate as appropriate. Neither raw form state nor the canonical local candidate is durably persisted for a new Tool until the existing final Create boundary.

For an existing persisted DRAFT, running Agent-contract validation MUST NOT save the DRAFT.

### R5 — show validation in the Agent contract tab

Provide one clear action such as:

```text
Validate agent contract
```

and show its success/errors in this tab.

Where practical, display issues next to the affected control/JSON editor rather than only as one undifferentiated message at the bottom.

A successful validation state must become stale immediately when any of these change:

```text
definitionVersion
description
inputSchema
responseTemplate
processed-result/output contract used for template compatibility
```

Validation success from an older candidate must never remain visually current after those inputs change.

### R6 — clarify terminology and help text

Use user-facing labels that explain the agent-facing purpose rather than implementation terminology alone. Prefer wording equivalent to:

```text
Definition version
Agent description
Agent input schema
Agent response template
```

Add concise help text explaining:

- Definition version is the semantic version of this Tool definition (for example `1.0.0`).
- Agent description explains the Tool to the CommerceAgent/model.
- Agent input schema defines the arguments the agent is allowed to provide when invoking the Tool.
- Agent response template formats the processed Tool result into the agent-facing Tool response.

Keep technical JSON editors available; this task does not introduce a separate visual schema/template designer.

### R7 — new-Tool and persisted-DRAFT parity

Where the existing shared `AgentContractTab` is used, validation behaviour must be consistent for:

```text
new local Tool authoring
persisted DRAFT authoring
```

For new Tools, validation operates entirely on the non-durable local candidate.

For persisted DRAFTs, validation checks the current unsaved editor candidate and does not require saving first.

Validation does not itself satisfy any live-Test requirement or publication-proof requirement.

### R8 — preserve free tab navigation

Agent-contract errors are visible in Agent contract, but this task MUST NOT disable Request, Response, Test or Review solely because Agent-contract validation has failed or has not yet run.

Phase 2 gating remains outside this task.

## Work Items

- [ ] Add/reuse one named non-mutating Agent-contract validator using canonical Tool-definition/publication rules.
- [ ] Validate Definition version and Agent description with deterministic field paths.
- [ ] Validate Agent input schema including canonical bounds and authority/credential restrictions.
- [ ] Validate Agent response-template syntax/tokens and compatibility with the current processed-result/output contract.
- [ ] Add bounded Server Action/service wiring without provider I/O or persistence.
- [ ] Retain malformed/invalid local Agent-contract text while showing actionable field-local diagnostics.
- [ ] Add `Validate agent contract` UI/status and stale-success invalidation.
- [ ] Clarify Agent-contract labels/help text without redesigning the tab.
- [ ] Preserve new-Tool and persisted-DRAFT parity through the existing `AgentContractTab` component.
- [ ] Add focused regression tests for validation, local-state retention, staleness and zero-persistence behaviour.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-016
canonical Commerce Tool-definition, input-schema and response-template contracts

ARCH-021-COMMERCE-039
non-durable new-Tool authoring until final Create

ARCH-021-COMMERCE-043
current processed-result/result-schema contract used by Visual Response authoring
```

Reuse the canonical publication/template compatibility semantics in:

```text
src/commerce/tool-definition/publication.ts
```

where applicable. Do not duplicate template path interpretation in Studio UI code.

No new cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-039
- ARCH-021-COMMERCE-043

## Enables

None.

## Acceptance Criteria

- [ ] `AgentContractTab` remains the single bounded React component for the Agent-contract form.
- [ ] The tab offers a clear `Validate agent contract` action.
- [ ] Validation does not require Request/Test/Review completion and performs no provider/network/credential work.
- [ ] Definition version and description failures are shown at deterministic Agent-contract paths.
- [ ] Input-schema validation uses the canonical bounded input-schema contract and rejects forbidden authority/credential inputs.
- [ ] Response-template validation uses the canonical template contract and validates paths against the current processed-result/output contract.
- [ ] Malformed/temporarily invalid JSON/text remains visible locally for correction instead of silently reverting.
- [ ] New-Tool Agent-contract validation writes no Tool, ToolRevision, audit, receipt or publication-proof state.
- [ ] Persisted-DRAFT Agent-contract validation does not save the DRAFT.
- [ ] Validation success is invalidated by any relevant Agent-contract/result-contract edit.
- [ ] Labels/help text clearly explain Definition version, Agent description, Agent input schema and Agent response template.
- [ ] New local Tool and persisted-DRAFT flows use the same Agent-contract validation semantics where the shared tab is used.
- [ ] Other tabs remain freely navigable; no Phase 2 gating is introduced.
- [ ] Final Create/Save/Publish validation remains authoritative and is not weakened or bypassed.

## Validation

- [ ] focused Agent-contract domain/Server Action tests
- [ ] focused `AgentContractTab` / new-Tool authoring UI tests
- [ ] persisted-DRAFT Agent-contract UI regression tests
- [ ] input-schema authority/credential rejection tests
- [ ] response-template result-path compatibility tests
- [ ] explicit proof that validation performs no provider I/O and no durable Tool/ToolRevision/audit writes
- [ ] relevant common Tool-authoring regression packet declared by the repository
- [ ] targeted TypeScript diagnostics or repository typecheck with baseline reconciliation
- [ ] targeted ESLint for changed files
- [ ] `git diff --check`

## Stop Condition

After Agent-contract validation, local-state retention, terminology/help text and required regressions are complete, set this task to `review`, complete the Completion Report and STOP. Do not begin Review-tab redesign, Test implementation, publication-proof work or Phase 2 tab gating.

## Implementation Notes

The current form is already extracted into `src/studio/tools/authoring/agent-contract-tab.tsx`; preserve that component boundary.

Prefer extracting/reusing canonical Agent-contract validation helpers from Tool-definition/publication code over validating a complete Tool merely to obtain Agent-contract errors. The purpose of this task is to let the tab validate its own concerns independently.

For External HTTP, remember that agent response templates see the Commerce Tool output contract (including the existing `values` wrapper used by execution/publication semantics), not the raw provider response.

Do not treat successful Agent-contract validation as a live-Test receipt or publication authorization.

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
