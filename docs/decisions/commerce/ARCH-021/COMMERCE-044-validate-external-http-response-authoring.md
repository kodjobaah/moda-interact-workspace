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
status: complete
priority: 61
executor: null
claimed_at: null
attempt: 1
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

- [x] Add/reuse a named Response-only validation service/Server Action.
- [x] Implement Direct mode-specific validation.
- [x] Implement Visual OBJECT/LIST mode-specific validation consuming COMMERCE-043 derivation.
- [x] Implement JavaScript source compile validation without executing a provider response.
- [x] Return deterministic Response-local issue paths.
- [x] Prove zero DNS/transport/credential reads.
- [x] Add explicit raw-local versus canonical-local versus durable-state contract coverage.
- [x] Add focused mode validation regressions.

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

- [x] A named Response-only validation boundary exists and does not require unrelated tabs to be complete.
- [x] Validation performs zero DNS/provider/credential operations.
- [x] Direct validation enforces JSON, Source-path and explicit result-schema rules.
- [x] Visual validation enforces JSON, paths, projection/filter/sort/limit bounds and COMMERCE-043 derived result-schema consistency.
- [x] JavaScript validation enforces empty Source path, supported runtime, bounded source and successful compilation.
- [x] JavaScript compile success is not misrepresented as runtime/result-schema success.
- [x] Errors use deterministic Response-local issue paths.
- [x] The contract permits temporarily invalid browser-local form values without durable persistence.
- [x] New-Tool Response validation creates/updates no Tool/ToolRevision rows.
- [x] Validation failures do not gate navigation to other authoring tabs.

## Validation

- [x] focused Response-only validation unit tests for Direct/Visual/JavaScript
- [x] focused Server Action authorization/error-envelope tests
- [x] explicit zero DNS/transport/credential-read proof
- [x] existing External HTTP validation regression packet
- [x] targeted TypeScript diagnostics or repository typecheck with baseline reconciliation
- [x] targeted ESLint for changed files
- [x] `git diff --check`

## Stop Condition

After the Response-only validation boundary, mode-specific checks, deterministic issue paths and required regressions are complete, set this task to `review`, complete the Completion Report and STOP. Do not redesign the Response-tab UI, implement live/sample response execution or start COMMERCE-045.

## Implementation Notes

Prefer extracting/reusing the response-specific pieces of `validateExternalHttpDefinition(...)` rather than maintaining two diverging validation implementations.

The authoritative boundary validates the current authoring definition; browser validation may improve immediacy but must not replace server validation.

## Completion Report

### Status
Ready for Review

### Files Changed
- `src/commerce/tool-authoring/external-validation.ts`
- `src/commerce/integration/external/index.ts`
- `src/studio/tools/external-validation-server-actions.ts`
- `tests/external-tool-authoring-validation.test.ts`
- `tests/external-tool-authoring-server-actions.test.ts`

### Work Completed
- Added a strict Response-only validation input and named validator for Direct, Visual OBJECT/LIST, and JavaScript modes. It does not require Request, Tool description, response template, connection metadata, or Review state.
- Direct and Visual modes enforce JSON format; all modes validate a safe or empty Source path and bounded result schema. Visual validation reuses COMMERCE-043 reconstruction/derivation, checks projection and filter/sort/limit constraints, and accepts persisted LIST schemas whose `items.maxItems` is greater than or equal to the current limit.
- JavaScript validation uses the bounded response compiler only, reports compiler diagnostics at the Response source path, and does not execute a transform or claim runtime/result-schema compatibility.
- Exposed the validator through the Commerce integration port and an ADMIN-authorized Server Action. Added coverage for raw invalid JSON, deterministic local paths, authorization/error envelopes, zero DNS/transport/credential reads, and no Tool/ToolRevision writes.
- Physical worktree isolation:
  - canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  - parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-044`
  - parent branch: `task/ARCH-021-COMMERCE-044`
  - implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-044`
  - implementation branch: `task/ARCH-021-COMMERCE-044`
  - shared workspace checkout switched/mutated for task work: no
  - shared implementation checkout switched/mutated for task work: no
  - another task worktree reused: no
- Start-of-attempt synchronization:
  - parent remote task branch fast-forwarded: not-needed
  - parent `origin/main` incorporated: already-current
  - implementation remote task branch fast-forwarded: not-needed
  - implementation `origin/main` incorporated: already-current
- Recursive implementation submodules:
  - `git submodule sync --recursive`: passed
  - `git submodule update --init --recursive`: passed
  - recorded submodule commit: `database` at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`

### Validation Results
- `npm run test:arch021-external-tool-authoring-validation`: passed, 52 tests across the authoring validation and Server Action suites.
- Targeted ESLint for all five changed source/test files: passed.
- `npx tsc --noEmit --pretty false`: repository-wide diagnostics remain in unrelated files due to missing generated Prisma client types and existing unresolved preview-module imports; filtering the run for all five changed files returned no diagnostics.
- `git diff --check`: passed.
- `npm run code-runtime:package`: passed; generated runtime hash remained `d4c9375f2b1ca4dc95f72c8aa2982a7a9951ac8011490d79c6582df732b4bbd9`.
- Implementation commit `11b8ae6` was pushed to `origin/task/ARCH-021-COMMERCE-044`.

### Deviations
None. Response-tab UI composition and navigation behavior remain owned by COMMERCE-045; this server-only boundary adds no navigation gating.

### Assumptions
Persisted Visual LIST schemas remain compatible when their bounded `items.maxItems` is greater than or equal to the current Visual projection limit, as accepted by COMMERCE-043.

### Unresolved Issues
The repository-wide TypeScript check remains blocked by the unrelated diagnostics recorded above; no diagnostics were reported in changed files.

### Architectural Concerns
None. JavaScript compilation is treated only as source/runtime validation, not as evidence of transform output compatibility.

## Architect Review

### Review Status
Accepted — Attempt 1

### Review Notes
Reviewed implementation `11b8ae6` and parent handoff `b00b3823`. Accepted.

The submitted implementation provides one strict Response-only validation boundary and
keeps the boundary independent of Request, Tool description, Agent-contract and Review
state. Direct, Visual OBJECT/LIST and JavaScript modes are validated against their
mode-specific contracts. Visual validation consumes the COMMERCE-043 reconstruction /
derivation rule rather than creating a second result-contract algorithm, including the
accepted persisted LIST compatibility where the durable `items.maxItems` bound is at
least the active Visual limit.

JavaScript Response validation calls only the accepted compile boundary; it does not run
`transform(response)` against a provider/sample payload. The integration proof shows the
Response-only path does not resolve connection metadata, credentials, DNS or transport
and creates/updates no Tool or ToolRevision rows. The named Server Action requires the
Studio `ADMIN` hierarchy role and returns through the existing bounded authoring action
envelope.

Response-local parse/schema/processing/source diagnostics use deterministic execution
paths. Temporarily invalid raw JSON is returned as bounded validation issues instead of
being persisted or silently normalised. This task adds no navigation gating or Response
UI redesign; those remain COMMERCE-045 scope.

The repository-wide TypeScript command remains non-zero for the submitted unrelated
baseline. The report records no diagnostics in task-owned files. The review archive does
not contain installed dependencies, so dependency-backed commands were not falsely
claimed as independently rerun by the architect.

### Reviewed Files
- `src/commerce/tool-authoring/external-validation.ts`
- `src/commerce/integration/external/index.ts`
- `src/studio/tools/external-validation-server-actions.ts`
- `tests/external-tool-authoring-validation.test.ts`
- `tests/external-tool-authoring-server-actions.test.ts`
- this task Completion Report
- ARCH-021 Response follow-up contract and COMMERCE-043 dependency contract

### Validation Reviewed
Submitted evidence accepted:

- `npm run test:arch021-external-tool-authoring-validation` -> PASS, 52 tests.
- targeted ESLint for the five changed source/test files -> PASS.
- `git diff --check` -> PASS.
- `npm run code-runtime:package` -> PASS; reported runtime artifact SHA-256
  `d4c9375f2b1ca4dc95f72c8aa2982a7a9951ac8011490d79c6582df732b4bbd9`.
- repository `npx tsc --noEmit --pretty false` remains blocked by unrelated baseline
  Prisma/generated-type and preview-module diagnostics; no changed-file diagnostic was
  reported.
- implementation `11b8ae6` and report `b00b3823` were reported pushed with clean
  worktrees and synchronized task branches.

### Architecture Conformance
Conforms. The Response validation boundary is non-mutating, zero-provider-I/O,
mode-specific and advisory. It preserves the raw-local / canonical-local / durable-state
separation and does not broaden the runtime or persistence authority of Response
authoring.

### Follow-up
`ARCH-021-COMMERCE-045` is promoted to `ready` for final Response-tab composition,
local raw-state presentation, validation-state staleness and per-mode draft retention.
