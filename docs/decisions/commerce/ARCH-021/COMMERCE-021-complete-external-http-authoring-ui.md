---
id: ARCH-021-COMMERCE-021
architecture_id: ARCH-021
title: Complete External HTTP request and response authoring UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-017
  - ARCH-021-COMMERCE-019
  - ARCH-021-COMMERCE-020
  - ARCH-021-COMMERCE-005
  - ARCH-021-COMMERCE-006
enables: []
created: 2026-09-23
updated: 2026-09-23
---

# Complete External HTTP request and response authoring UI

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Allow admins to author the complete canonical EXTERNAL_HTTP draft—exact connection revision, declarative or JavaScript request construction, and DIRECT/Visual/JavaScript response processing—while previewing request construction without making a provider call.

## Context

Phase 1 connected the Tool editor to real immutable connection revisions and installed response JavaScript composition. Phase 3 adds request construction and DIRECT response handling. Real provider execution remains Phase 4.

## Scope

Primary files:

```text
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/tool-editor.tsx
src/studio/external-http/editor.tsx
src/studio/code-response/code-editor.tsx       # reuse only; behavior changes only if required for generic label/props
src/studio/tools/validation-server-actions.ts
tests/external-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

## Out of Scope

- Live external HTTP calls.
- Credential display/decryption.
- POST/write methods.
- Shopify Admin UI (COMMERCE-022).
- Feature association/publishing after live test.

## Requirements

### R1 — execution choice

The Tool editor's external execution kind persists exactly:

```text
kind: EXTERNAL_HTTP
method: GET
connectionRevisionId: exact immutable selected revision
```

The user selects a real persisted connection revision; origin/auth are displayed only as safe metadata already exposed by the accepted port. Secrets never enter browser state.

### R2 — request authoring

Provide exactly two request modes:

```text
Declarative
JavaScript
```

Declarative fields:

```text
path
query mappings
static safe headers
```

JavaScript uses the existing CodeMirror JavaScript editor with starter source:

```js
function buildRequest({ args }) {
  return {
    path: '/',
    query: {},
    headers: { accept: 'application/json' }
  };
}
```

Do not show method/origin/credential/body controls inside JavaScript.

### R3 — request preview

Provide a bounded manual "Tool arguments" JSON editor/input for authoring preview only. On `Preview request`:

1. parse JSON;
2. server-validate against the current tool `inputSchema`;
3. execute declarative mapping or COMMERCE-017 request processor;
4. show only the resulting safe descriptor:

```text
GET <connection origin redacted-safe display + relative path/query>
authored safe headers
credential header: configured/redacted, never value
```

No DNS/network/provider call occurs. The UI must visibly label this as request construction preview, not a live Tool test.

### R4 — response authoring

Provide exactly three response modes:

```text
Direct
Visual
JavaScript
```

Direct:

```text
responseFormat must be JSON
resultPath
resultSchema
no projection/filter/code fields
```

Visual preserves existing OBJECT/LIST/filter/sort/limit editor.

JavaScript preserves existing raw-response/code editor and `transform(response)` contract.

Switching modes must not silently copy stale incompatible configuration into the newly selected mode. A dirty-editor confirmation is required before destructive mode resets.

### R5 — draft validation and save

Before Save/Publish handoff, use COMMERCE-019 authoritative validation. Browser-only validation is advisory.

Save persists the exact COMMERCE-016 Commerce-owned definition. No compatibility conversion is allowed.

Publication action may remain visible but COMMERCE-019 `LIVE_TEST_REQUIRED` must be shown clearly rather than treated as generic failure.

### R6 — no fixture-led human test

The production Tool editor must no longer present synthetic external response fixtures as the *normal* "test this tool" workflow. Fixture UI may remain in explicit developer/test-only paths used by automated suites. Real live Tool Test arrives in Phase 4.

## Work Items

- [ ] Add request mode UI and safe descriptor preview.
- [ ] Add DIRECT response mode.
- [ ] Preserve Visual/response JS modes.
- [ ] Wire authoritative validation/save and LIVE_TEST_REQUIRED presentation.
- [ ] Remove fixture-first human test affordance from production flow.
- [ ] Add focused UI regressions.

## Interfaces / Contracts

Consumes the COMMERCE-016 Commerce-owned Tool contract, COMMERCE-017 request processor preview and COMMERCE-019 validator.

## Dependencies

- ARCH-021-COMMERCE-017
- ARCH-021-COMMERCE-019
- ARCH-021-COMMERCE-020
- ARCH-021-COMMERCE-005
- ARCH-021-COMMERCE-006

## Enables

None in Phase 3. Phase 4 live-test tasks will depend on this completed authoring surface.

## Acceptance Criteria

- [ ] Admin can author every canonical EXTERNAL_HTTP request/response mode.
- [ ] Request JS sees only tool arguments and produces only a safe descriptor.
- [ ] Request preview performs zero provider I/O.
- [ ] Direct/Visual/JavaScript response modes persist losslessly.
- [ ] Production UI communicates that live testing is required before publication.

## Validation

- [ ] `npm run test:arch020-external-tools-ui`
- [ ] focused Phase 3 external authoring UI tests
- [ ] request-preview test proving zero transport calls
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not implement live HTTP execution/testing.

## Implementation Notes

The model/CommerceAgent supplies runtime arguments; this UI only authors `inputSchema`, mappings/code and optional manual preview arguments.

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
