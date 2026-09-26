---
id: ARCH-021-COMMERCE-044
architecture_id: ARCH-021
title: Add Response-specific validation for External HTTP authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 61
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-043
  - ARCH-021-COMMERCE-019
  - ARCH-021-COMMERCE-023
enables:
  - ARCH-021-COMMERCE-045
created: 2026-09-26
updated: 2026-09-26
---

# Add Response-specific validation for External HTTP authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Provide a non-mutating, server-authoritative External HTTP Response validation boundary that validates only the current Response-tab configuration according to the selected Direct, Visual or JavaScript mode and returns structured Response-local diagnostics without requiring Request, Test, Agent-contract or Review completion.

## Context

The accepted full-definition validation from COMMERCE-023 already understands important response rules, including JavaScript compilation and Visual/result-schema compatibility. Manual review nevertheless found that the Response tab has no dedicated validation checkpoint and often relies on whole-`ExternalHttpExecutionSchema` parsing while an administrator is editing individual fields.

That causes two problems:

1. temporarily invalid authoring values can be rejected before the UI has a chance to show what the author typed; and
2. administrators discover response-specific errors only through broader validation rather than in the tab where the error was created.

The desired authoring model distinguishes three layers:

```text
Raw local Response form state
  may be incomplete/temporarily invalid
        ↓
Canonical local Tool draft
  schema-valid but still browser-local for a new Tool
        ↓
Durable Tool state
  PostgreSQL only after final Create from Review
```

This task establishes the authoritative Response-only validation boundary and diagnostic contract. COMMERCE-045 owns the final UI composition and raw local state presentation.

## Scope

Primary files:

```text
src/commerce/tool-authoring/external-validation.ts
src/studio/tools/external-validation-server-actions.ts
src/studio/server-services.ts                           # only named service boundary where required
src/studio/external-http/ports.ts                       # bounded Response validation DTO/result where appropriate

tests/external-tool-authoring-validation.test.ts
tests/external-tool-authoring-server-actions.test.ts
```

Additional focused validation tests may change when required by repository conventions.

## Out of Scope

- Request-tab validation/preview; COMMERCE-040..042 own that independent follow-up.
- Final Response-tab layout and local form controls; COMMERCE-045 owns those changes.
- Live DNS, external HTTP/provider calls or credential reads/decryption.
- Running JavaScript response transforms against a real/sample provider response.
- Deriving Direct/JavaScript schemas from observed samples.
- Response-template validation from Agent contract.
- Phase 2 tab gating or mandatory Next/Back progression.
- Persisting intermediate new-Tool state.
- Database schema changes.

## Requirements

### R1 — named Response-only validation boundary

Add/reuse one named, non-mutating, hierarchy-authorized Server Action/service boundary for validating the current External HTTP Response configuration only.

The bounded input should contain only what Response validation needs, such as:

```text
responseFormat
resultPath / Source path
responseProcessing
resultSchema
```

and any COMMERCE-043 Visual authoring contract data required to derive/reconcile Visual `resultSchema`.

Do not require a valid Request definition, Tool description, response template or final Review state merely to validate Response authoring.

### R2 — zero provider I/O

Response validation is authoring validation, not Tool execution.

It MUST perform zero:

```text
DNS lookup
external HTTP/provider request
credential read/decryption
shop/session token resolution
```

JavaScript validation may invoke the accepted compiler/runtime compile boundary only to validate source/runtime compatibility; it must not execute the transform against a provider response in this task.

### R3 — Direct-mode validation

When processing mode is `DIRECT`, validate at least:

- response format is JSON;
- Source path is empty or a valid safe dot path;
- no Visual/JavaScript-only configuration is treated as active;
- explicit Direct `resultSchema` is a valid bounded details schema.

Direct validation does not claim that the provider will actually return a value matching the schema; observed-output validation belongs to Test.

### R4 — Visual-mode validation

When processing mode is Visual `OBJECT` or `LIST`, validate at least:

- response format is JSON;
- Source path is empty or a valid safe dot path;
- projected output names are safe and bounded;
- projection source paths are valid;
- COMMERCE-043 result types are supported;
- `omitIfMissing`/required semantics are coherent;
- LIST limit/filter/sort structures satisfy accepted runtime bounds;
- filter operators/typed values satisfy existing canonical rules;
- the canonical Visual `resultSchema` equals/is consistent with COMMERCE-043 deterministic derivation.

Do not require the user to separately author a raw Visual result schema.

### R5 — JavaScript-mode validation

When processing mode is `JAVASCRIPT`, validate at least:

- Source path/resultPath is empty;
- runtime version is supported;
- source is present and within accepted UTF-8 bounds;
- `transform(response)` source compiles through the accepted response-code compiler;
- response format/media types satisfy the canonical JSON/TEXT rules;
- explicit JavaScript `resultSchema` is a valid bounded details schema.

Compilation success is not evidence that the transform returns data matching the schema. That execution/sample check belongs to Test.

### R6 — deterministic Response-local issue paths

Return structured authoring issues using the existing `ToolAuthoringValidation` issue contract/path conventions.

Issues must be attributable to Response fields, including paths equivalent to:

```text
/execution/responseFormat
/execution/responseFormat/mediaTypes
/execution/resultPath
/execution/responseProcessing
/execution/responseProcessing/source
/execution/responseProcessing/fields/<name>/path
/execution/responseProcessing/filters/<index>
/execution/resultSchema
```

Use more specific existing paths where available rather than collapsing everything into `/execution/responseProcessing`.

### R7 — raw local state is allowed; durable persistence is not

The validation contract must support the UI distinction between:

```text
raw local Response form state
canonical local Tool draft
```

where practical by returning deterministic parse/validation issues instead of assuming every intermediate string is already canonical.

Do NOT interpret “invalid state must not persist” as permission to erase what the administrator typed.

For new-Tool authoring:

- temporarily invalid values MAY remain in browser-local Response form state;
- only schema-valid values may be promoted into the canonical local Tool draft;
- neither layer is durably persisted during Response authoring;
- Tool/ToolRevision persistence still occurs only on final Create from Review.

### R8 — validation state is advisory, not navigation gating

A Response validation failure must be visible and actionable but MUST NOT disable the other authoring tabs in this phase.

Changing relevant Response authoring after a successful validation must make that success stale; COMMERCE-045 owns the UI wiring for that staleness.

## Work Items

- [ ] Add/reuse a named Response-only validation service/Server Action.
- [ ] Implement Direct mode-specific validation.
- [ ] Implement Visual OBJECT/LIST mode-specific validation consuming COMMERCE-043 derivation.
- [ ] Implement JavaScript source compile validation without executing a provider response.
- [ ] Return deterministic Response-local issue paths.
- [ ] Prove zero DNS/transport/credential reads.
- [ ] Add explicit raw-local versus canonical-local versus durable-state contract coverage.
- [ ] Add focused mode validation regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-019
common authoring validation/auth/error envelope

ARCH-021-COMMERCE-023
External HTTP authoring validation and accepted response compiler conventions

ARCH-021-COMMERCE-043
Visual result-schema derivation
```

Produces the Response-only validation boundary consumed by COMMERCE-045.

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-043
- ARCH-021-COMMERCE-019
- ARCH-021-COMMERCE-023

## Enables

- ARCH-021-COMMERCE-045

## Acceptance Criteria

- [ ] A named Response-only validation boundary exists and does not require unrelated tabs to be complete.
- [ ] Validation performs zero DNS/provider/credential operations.
- [ ] Direct validation enforces JSON, Source-path and explicit result-schema rules.
- [ ] Visual validation enforces JSON, paths, projection/filter/sort/limit bounds and COMMERCE-043 derived result-schema consistency.
- [ ] JavaScript validation enforces empty Source path, supported runtime, bounded source and successful compilation.
- [ ] JavaScript compile success is not misrepresented as runtime/result-schema success.
- [ ] Errors use deterministic Response-local issue paths.
- [ ] The contract permits temporarily invalid browser-local form values without durable persistence.
- [ ] New-Tool Response validation creates/updates no Tool/ToolRevision rows.
- [ ] Validation failures do not gate navigation to other authoring tabs.

## Validation

- [ ] focused Response-only validation unit tests for Direct/Visual/JavaScript
- [ ] focused Server Action authorization/error-envelope tests
- [ ] explicit zero DNS/transport/credential-read proof
- [ ] existing External HTTP validation regression packet
- [ ] targeted TypeScript diagnostics or repository typecheck with baseline reconciliation
- [ ] targeted ESLint for changed files
- [ ] `git diff --check`

## Stop Condition

After the Response-only validation boundary, mode-specific checks, deterministic issue paths and required regressions are complete, set this task to `review`, complete the Completion Report and STOP. Do not redesign the Response-tab UI, implement live/sample response execution or start COMMERCE-045.

## Implementation Notes

Prefer extracting/reusing the response-specific pieces of `validateExternalHttpDefinition(...)` rather than maintaining two diverging validation implementations.

The authoritative boundary validates the current authoring definition; browser validation may improve immediacy but must not replace server validation.

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
