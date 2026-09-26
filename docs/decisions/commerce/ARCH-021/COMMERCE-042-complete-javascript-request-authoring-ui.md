---
id: ARCH-021-COMMERCE-042
architecture_id: ARCH-021
title: Complete JavaScript request bindings and editor UX
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 62
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-041
enables: []
created: 2026-09-26
updated: 2026-09-26
---

# Complete JavaScript request bindings and editor UX

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make JavaScript request authoring understandable and resilient in the External HTTP Request tab by exposing COMMERCE-040 bindings through explicit Agent-input/Literal controls, providing a usable resizable JavaScript editor with actionable validation diagnostics, and preserving each request mode's unsaved local work when authors switch between Declarative and JavaScript.

## Context

The Request tab currently gives declarative authors an explicit mapping table:

```text
Query key | Source | Agent input / Literal | Omit if missing
```

but JavaScript mode exposes only a very shallow CodeMirror instance and the statement that request code receives Tool arguments. The source/value relationship is therefore hidden, and partial JavaScript edits can be rejected by whole-execution schema parsing before the author can see a useful diagnostic.

The current mode switch also replaces the active request with a fresh default:

```text
Declarative -> JavaScript
    destroys current declarative request state

JavaScript -> Declarative
    destroys current JavaScript request state
```

COMMERCE-040 establishes the canonical JavaScript `bindings` contract and COMMERCE-041 establishes Request-local validation/preview form state. This task completes the JavaScript-specific authoring UI on top of those accepted boundaries.

## Scope

Primary files:

```text
src/studio/external-http/request-tab.tsx
src/studio/external-http/editor.tsx
src/studio/code-response/code-editor.tsx              # only generic capability needed by Request editor
src/studio/tools/new-tool-editor.tsx                   # only if Request-mode local state must be composed here
src/studio/tools/tool-editor.tsx                       # persisted DRAFT parity where the same Request component is used
app/styles.css

tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

Additional directly affected Request-authoring UI tests may change when required by this capability.

## Out of Scope

- Changing the COMMERCE-040 canonical binding semantics.
- Live provider execution/testing.
- Response, Agent contract or Review tab redesign.
- Connection management/navigation.
- Phase 2 tab gating or mandatory progression.
- Database schema changes.
- Persisting inactive request-mode drafts.
- Changing response JavaScript editor behaviour unless a generic CodeEditor capability can be added without altering its existing semantics.

## Requirements

### R1 — explicit JavaScript Request values

When Request mode is `JavaScript`, show an explicit `Request values` authoring table backed by `request.bindings`.

For each binding, the author controls:

```text
Value name
Source: Agent input | Literal
Agent input name OR literal value
Omit if missing (Agent input only)
Remove
```

The semantics shown in the UI must be literal and unambiguous:

```text
Agent input
    Value is supplied from the named CommerceAgent Tool input at invocation time.

Literal
    The authored value is fixed in the Tool definition.
```

The binding table must edit the exact COMMERCE-040 canonical binding map; it must not create a browser-only parallel mapping representation.

### R2 — bounded literal authoring

JavaScript binding literals may be any JSON value permitted by the canonical bounded mapping contract, not only strings.

The UI must preserve the authored JSON type (`string`, number, boolean, null, object or array where contract-allowed) and show a deterministic validation error for malformed/out-of-bounds literal text rather than coercing it silently.

### R3 — truthful JavaScript contract guidance

The JavaScript section must explain the exact contract:

```js
function buildRequest({ args }) {
  // args contains only the resolved Request values declared above.
  // return { path, query, headers };
}
```

Do not describe `args` as the entire Tool input object after COMMERCE-040.

The current Request preview from COMMERCE-041 must execute the current bindings + source and display the resulting descriptor.

### R4 — usable resizable CodeMirror editor

The JavaScript request editor must no longer render as an effectively one-line code strip.

Provide a useful initial editing area with, at minimum:

```text
visible multi-line height suitable for the starter function
vertical scrolling
vertical resizing by the author
line numbers retained
```

A request-specific wrapper/class is preferred if changing generic `CodeEditor` styling would unintentionally resize unrelated response JavaScript editors.

Resizing is presentation state only and must not mutate the Tool definition.

### R5 — retain invalid/partial JavaScript while editing

Authors must be able to type temporarily invalid JavaScript, including an incomplete function, without the editor snapping back to the last schema-valid source.

Keep the raw source in Request-local form state and surface COMMERCE-041 validation/compile diagnostics against that current source.

Only canonical valid request state is emitted to durable Tool-definition state.

### R6 — preserve both mode drafts during the authoring session

Switching Request mode must not destroy the other mode's unsaved local configuration.

Within the current editor session maintain distinct local drafts for:

```text
Declarative request
JavaScript request
```

Example:

```text
author creates declarative mappings
-> switches to JavaScript and edits bindings/source
-> switches back
-> original declarative mappings are restored
-> switches again to JavaScript
-> JavaScript bindings/source are restored
```

Only the currently selected mode belongs to the canonical Tool definition and is persisted by final Create/Save. The inactive local mode draft is authoring convenience only and must not be written into the definition.

### R7 — validation/preview staleness

Changing JavaScript source or any binding must immediately invalidate the Request validation/preview result established by COMMERCE-041.

The UI must show binding/source diagnostics in the Request tab and must not require visiting Test or Review to discover JavaScript request errors.

### R8 — no gating

All authoring tabs remain freely navigable. JavaScript errors are visible Request-tab state only in this phase and do not introduce locked tabs or mandatory Next/Back progression.

## Work Items

- [ ] Render COMMERCE-040 JavaScript bindings as Request values.
- [ ] Add Agent input/Literal source switching with typed literal preservation.
- [ ] Update JavaScript contract help text to describe resolved bindings accurately.
- [ ] Give Request JavaScript CodeMirror a useful resizable multi-line presentation.
- [ ] Retain invalid/partial JavaScript source locally with actionable diagnostics.
- [ ] Preserve independent Declarative and JavaScript local drafts across mode switches.
- [ ] Invalidate Request validation/preview state on source/binding edits.
- [ ] Add focused regressions for mapping parity, literal typing, editor state and mode switching.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-040
canonical JavaScript Request bindings

ARCH-021-COMMERCE-041
Request-local validation and exact request preview
```

No new cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-041

## Enables

None.

## Acceptance Criteria

- [ ] JavaScript mode visibly exposes Request values with Agent input/Literal sources.
- [ ] The binding controls edit the canonical COMMERCE-040 `bindings` map.
- [ ] JSON literal types are preserved and malformed literals receive visible errors.
- [ ] JavaScript guidance states that `args` contains only resolved Request values.
- [ ] The request CodeMirror editor opens at a useful multi-line height, scrolls and can be resized vertically.
- [ ] Partial/invalid JavaScript remains visible while being edited and receives validation diagnostics.
- [ ] Declarative authoring state survives Declarative -> JavaScript -> Declarative switching within the session.
- [ ] JavaScript bindings/source survive JavaScript -> Declarative -> JavaScript switching within the session.
- [ ] Only the active request mode is part of the canonical definition/persistence payload.
- [ ] Request validation/preview is invalidated when source/bindings change.
- [ ] New-Tool authoring remains non-durable until final Create.
- [ ] No live provider I/O or Phase 2 gating is introduced.

## Validation

- [ ] focused External HTTP Request JavaScript UI tests
- [ ] focused mode-switch retention tests for new and persisted-DRAFT authoring where applicable
- [ ] focused Request validation/preview regression with JavaScript bindings
- [ ] existing External UI/common Tool-authoring regression packet required by repository scripts
- [ ] targeted TypeScript diagnostics or repository typecheck with baseline reconciliation
- [ ] targeted ESLint for changed files
- [ ] `git diff --check`

## Stop Condition

After JavaScript binding controls, resizable editor, partial-source diagnostics, mode-draft preservation and required regressions are complete, set the task to `review`, complete the Completion Report and STOP. Do not begin Response-tab, Test-tab, Agent-contract or Review-tab redesign and do not implement Phase 2 gating.

## Implementation Notes

The current mode switch creates a brand-new default request object for the selected mode. Replace that destructive behaviour with explicit Request-local per-mode drafts.

Do not persist both modes into the canonical Tool definition. This is local editor state analogous to retaining text while the author compares alternatives.

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
