---
id: ARCH-021-COMMERCE-040
architecture_id: ARCH-021
title: Add explicit value bindings to JavaScript HTTP request construction
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 60
executor: copilot
claimed_at: 2026-09-26T10:50:01Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-017
  - ARCH-021-COMMERCE-023
  - ARCH-021-COMMERCE-039
enables:
  - ARCH-021-COMMERCE-041
created: 2026-09-26
updated: 2026-09-26
---

# Add explicit value bindings to JavaScript HTTP request construction

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Extend the canonical `EXTERNAL_HTTP` JavaScript request definition so `buildRequest({ args })` receives only an explicitly declared set of request values whose source is either a CommerceAgent input or an authored literal, giving JavaScript request construction the same visible source semantics as declarative mappings without exposing the complete Tool input object implicitly.

## Context

Developer manual review of the COMMERCE-039 local-only authoring flow identified an asymmetry in the Request tab.

Declarative request construction explicitly records, for each query value:

```text
Source = Agent input
    -> value comes from one named Tool input

Source = Literal
    -> authored value is used directly
```

JavaScript request construction currently stores only:

```ts
{
  kind: "JAVASCRIPT",
  runtimeVersion: "quickjs-sync.v1",
  source: "function buildRequest({ args }) { ... }"
}
```

and the request processor receives a validated copy of the Tool's complete argument object. This makes JavaScript authoring less explicit than declarative authoring and gives the request program access to inputs it did not deliberately bind.

ARCH-021 is still pre-production for this execution shape. This task therefore makes one canonical breaking contract correction rather than introducing a compatibility parser or a parallel `v2` shape.

This task establishes only the canonical definition/runtime semantics. COMMERCE-041 and COMMERCE-042 own the Request-tab validation/preview and UI authoring changes.

## Scope

Primary files:

```text
src/commerce/tool-definition/contracts.ts
src/commerce/tool-definition/mappings.ts
src/commerce/code-request/processor.ts                # only where required by the binding contract
src/commerce/tool-authoring/external-validation.ts

tests/arch021-commerce-tool-contract.test.ts
tests/code-request-processor.test.ts
tests/external-tool-authoring-validation.test.ts
tests/external-tool-authoring-server-actions.test.ts
```

Update repository fixtures/builders that construct canonical `JAVASCRIPT` external requests when required by the new definition shape. Do not change Studio presentation in this task.

## Out of Scope

- Request-tab layout, validation presentation or request preview placement; COMMERCE-041 owns those changes.
- JavaScript binding controls, CodeMirror sizing or mode-switch preservation; COMMERCE-042 owns those changes.
- Live external provider calls.
- Credential resolution/display.
- Response processing changes.
- Phase 2 tab gating or Next/Back progression.
- Database schema/migration changes.
- A compatibility parser for the superseded JavaScript request shape.
- Enabling production JavaScript External HTTP execution before its later runtime phase.

## Requirements

### R1 — one canonical JavaScript request shape

Change the canonical JavaScript request construction shape to include an explicit bounded binding map:

```ts
{
  kind: "JAVASCRIPT";
  runtimeVersion: "quickjs-sync.v1";
  bindings: {
    [requestValueName: string]:
      | { input: string; omitIfMissing?: true }
      | { literal: JsonValue };
  };
  source: string;
}
```

Use the existing bounded mapping semantics where appropriate rather than creating a second structurally different Agent-input/Literal contract.

Binding names remain safe bounded names and the existing mapping-count/storage bounds remain enforced.

Do not change the JavaScript entrypoint name/signature:

```js
function buildRequest({ args }) { ... }
```

The semantic change is what `args` contains, not the function name.

### R2 — resolve bindings before the sandbox

For JavaScript request construction:

1. validate the complete Tool invocation arguments against the Tool `inputSchema`;
2. resolve `request.bindings` deterministically;
3. for `{ input }`, copy only the named top-level Tool input value;
4. for `{ literal }`, preserve the exact bounded JSON literal;
5. honour existing `omitIfMissing` semantics;
6. fail missing required bindings with the existing invalid-input semantics;
7. pass only the resolved binding record to QuickJS as `buildRequest({ args })`.

The JavaScript request processor MUST NOT receive a copy of every validated Tool input merely because it exists in `inputSchema`.

Structured input values may be bound for JavaScript because JavaScript may intentionally transform them before returning the final descriptor. The final request descriptor remains restricted to the existing relative path + scalar query + safe-header contract.

### R3 — preserve authority/credential isolation

JavaScript request bindings MUST NOT provide an alternate route for authority/credential-like Tool inputs.

Apply the existing External HTTP forbidden-input policy to JavaScript `{ input }` bindings as well as declarative mappings. In particular, credential/authority names that are forbidden for external request mappings must remain unavailable through JavaScript bindings.

Connection origin, authentication material, provider credentials, environment/process state and network APIs remain unavailable to request JavaScript.

### R4 — one binding resolver across preview and execution mapping

Use one canonical binding-resolution rule for:

```text
request preview
Tool argument mapping / future execution
request processor input
```

Do not independently reimplement Agent-input/Literal resolution in the browser and server.

`previewExternalRequest(...)` MUST resolve the same bindings before invoking the request processor that the runtime mapping boundary would resolve for the same definition/arguments.

### R5 — authoring validation understands bindings

Server-authoritative External HTTP authoring validation must reject at least:

- malformed binding names;
- unknown `{ input }` references;
- forbidden external input names;
- missing required mapped input during request preview;
- invalid literal values/bounds;
- malformed JavaScript request source;
- request processor output that is not a valid safe descriptor.

Diagnostics must use deterministic request/binding paths suitable for COMMERCE-041/042 UI presentation.

### R6 — pre-production breaking contract

This is a canonical pre-production contract correction.

Do not add:

```text
JAVASCRIPT_V2
legacy JavaScript parser
implicit "all Tool inputs" fallback
```

Update repository fixtures/tests/builders to the new canonical shape. No Prisma migration is required because Tool definitions remain JSON-owned Commerce state.

## Work Items

- [ ] Add bounded `bindings` to the canonical JavaScript request contract.
- [ ] Remove implicit copy-all-inputs semantics for JavaScript request construction.
- [ ] Reuse one deterministic binding resolver for JavaScript preview/runtime mapping.
- [ ] Apply External HTTP forbidden-input policy to JavaScript bindings.
- [ ] Preserve bounded QuickJS input/output and safe descriptor validation.
- [ ] Update authoritative External HTTP validation for binding diagnostics.
- [ ] Update canonical fixtures/builders/tests to the single new shape.
- [ ] Add regression coverage proving unbound Tool inputs are absent from JavaScript `args`.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-016
Commerce Tool-definition contract and mapping bounds

ARCH-021-COMMERCE-017
bounded buildRequest({ args }) QuickJS runtime

ARCH-021-COMMERCE-023
External HTTP authoring validation/request preview boundary
```

Produces the revised canonical JavaScript request contract consumed by COMMERCE-041/042.

No cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-017
- ARCH-021-COMMERCE-023
- ARCH-021-COMMERCE-039

## Enables

- ARCH-021-COMMERCE-041

## Acceptance Criteria

- [ ] Canonical JavaScript request definitions contain an explicit bounded `bindings` map.
- [ ] `buildRequest({ args })` receives the resolved bindings only, not all validated Tool inputs.
- [ ] Agent-input and Literal bindings use deterministic semantics equivalent to the platform mapping model.
- [ ] Structured JavaScript-bound values remain possible while final descriptor query values remain scalar/bounded.
- [ ] Unknown/forbidden input bindings fail authoritative validation deterministically.
- [ ] Request preview and runtime argument mapping use the same binding-resolution rule.
- [ ] Unbound Tool inputs are proven absent from request JavaScript input.
- [ ] Existing QuickJS security/runtime bounds remain intact.
- [ ] No compatibility parser, new execution kind/version or Prisma migration is introduced.
- [ ] No Studio UI, live provider call or tab gating is implemented by this task.

## Validation

- [ ] focused Commerce Tool-contract tests
- [ ] focused request-processor tests
- [ ] focused External HTTP authoring validation/preview tests
- [ ] existing common Tool-authoring packet required by repository scripts
- [ ] targeted TypeScript diagnostics for changed files or repository typecheck with baseline reconciliation
- [ ] targeted ESLint for changed files
- [ ] `git diff --check`

## Stop Condition

After the canonical JavaScript binding contract, resolver, authoritative validation and required regressions are complete, set the task to `review`, complete the Completion Report and STOP. Do not modify Request-tab presentation, move preview UI, resize CodeMirror or implement live provider testing.

## Implementation Notes

Prefer extending/reusing the existing mapping helpers rather than teaching the sandbox about Tool schemas or connection state. QuickJS should continue to receive one already-resolved JSON-safe `args` object and return one safe request descriptor.

The user-facing terminology in later UI is:

```text
Agent input -> supplied by the CommerceAgent invocation
Literal     -> authored fixed value
```

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
