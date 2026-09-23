---
id: ARCH-021-COMMERCE-019
architecture_id: ARCH-021
title: Implement Phase 3 server-side tool-authoring validation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-017
  - ARCH-021-COMMERCE-018
  - ARCH-020-COMMERCE-030
enables:
  - ARCH-021-COMMERCE-021
  - ARCH-021-COMMERCE-022
created: 2026-09-23
updated: 2026-09-23
---

# Implement Phase 3 server-side tool-authoring validation

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Create one authenticated server-side authoring validator for new EXTERNAL_HTTP and SHOPIFY_ADMIN_GRAPHQL drafts, compile all authored JavaScript/GraphQL locally, and explicitly prevent Phase 3 definitions from being published until Phase 4 supplies a real live-test receipt.

## Context

The existing ARCH-020 external publication validator uses synthetic response samples/receipts. ARCH-021's product contract requires a real selected-shop/provider test before a newly authored tool is publishable. Phase 3 therefore validates authoring completely but does not pretend fixture validation is deployment evidence.

## Scope

Primary files:

```text
src/commerce/tool-authoring/validation.ts
src/commerce/tool-authoring/contracts.ts
src/studio/tools/validation-server-actions.ts
src/commerce/external-publication/index.ts
src/commerce/external-publication/contracts.ts
src/commerce/publication/validation.ts        # only if central dispatch needs exact new kind handling
tests/tool-authoring-validation.test.ts
package.json
```

## Out of Scope

- Real Shopify/external requests.
- Live-test receipt implementation (Phase 4).
- Tool editor UI.
- Provider credentials in browser/client contracts.
- Replacing old ARCH-020 historical publication evidence for already-published development revisions.

## Requirements

### R1 — exact authoring validator result

Expose one server-side port returning:

```ts
type ToolAuthoringValidation =
  | { valid: true; schemaHash: string | null; issues: [] }
  | { valid: false; schemaHash: string | null; issues: Array<{ path: string; code: string; message: string; line?: number | null; column?: number | null }> };
```

Maximum 32 issues; messages must not contain raw credentials/provider response payloads.

### R2 — EXTERNAL_HTTP draft validation

For every External draft:

1. parse full `CommerceToolDefinitionSchema`;
2. confirm exact connection revision exists and connection is enabled;
3. for DECLARATIVE request, validate mappings/static headers only; perform no network request;
4. for JAVASCRIPT request, compile through COMMERCE-017; optional manual argument preview may execute the sandbox only, never transport;
5. validate response mode:
   - DIRECT: JSON + resultPath/resultSchema structural contract;
   - OBJECT/LIST: existing visual publication-shape compatibility;
   - JAVASCRIPT: compile existing response processor;
6. validate responseTemplate against resulting resultSchema;
7. return deterministic issue paths under `/execution/...`.

### R3 — SHOPIFY_ADMIN_GRAPHQL draft validation

For Admin drafts:

1. parse full tool definition;
2. invoke COMMERCE-018 local compiler with exact `inputSchema`;
3. require compiler's pinned `schemaHash` to equal definition.schemaHash;
4. validate responseTemplate against declared resultSchema;
5. perform no Dev MCP/network/session request in the normal server action.

### R4 — request JavaScript preview contract

Expose an authenticated ADMIN/SUPER_ADMIN action that accepts:

```ts
{ source: string; arguments: unknown; inputSchema: unknown }
```

It MUST validate arguments through `compileSubset(inputSchema, 'input')` before calling `buildRequest`. Return only a COMMERCE-016-valid request descriptor or bounded diagnostics. This preview performs no connection lookup/HTTP call.

### R5 — Phase 3 publication gate

For a DRAFT using either canonical Phase 3 kind:

```text
EXTERNAL_HTTP             (new request-based contract)
SHOPIFY_ADMIN_GRAPHQL
```

`validateForPublication` MUST return a stable non-success result:

```text
code: LIVE_TEST_REQUIRED
path: /liveTest
message: Run a successful live tool test for the current saved revision before publishing.
```

Synthetic fixture/sample validation MUST NOT create a receipt that satisfies this gate.

Already-published historical revisions are read-only history; this task does not retroactively unpublish them.

Phase 4 will replace this fail-closed gate with exact live-test receipt validation.

### R6 — development bypass

Use the already accepted auth rule: `developmentBypass === true` is sufficient for the trusted development path. Do not reintroduce ID/role cross-validation under bypass.

### R7 — exact focused validation

Add `test:arch021-tool-authoring-validation` proving:

- external declarative draft valid without network;
- request JS syntax/entrypoint/descriptor errors surfaced;
- DIRECT/visual/response JS validation branches;
- missing/disabled connection rejected;
- valid Admin query accepted locally;
- Admin mutation/wrong hash rejected;
- request preview validates CommerceAgent arguments before JS;
- provider transport is never called;
- Phase 3 publication returns LIVE_TEST_REQUIRED;
- development bypass path does not consult PlatformAdmin authorization.

## Work Items

- [ ] Add one server authoring-validation port/action.
- [ ] Integrate request/response JS and visual/DIRECT structural validation.
- [ ] Integrate Admin compiler.
- [ ] Add request-descriptor preview action.
- [ ] Install fail-closed live-test publication gate.
- [ ] Add focused tests.

## Interfaces / Contracts

Consumes COMMERCE-016 baseline, COMMERCE-017 request processor and COMMERCE-018 Admin compiler.

Produces the validation API consumed by both Phase 3 Tool editors and the publication lifecycle.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-017
- ARCH-021-COMMERCE-018
- ARCH-020-COMMERCE-030

## Enables

- ARCH-021-COMMERCE-021
- ARCH-021-COMMERCE-022

## Acceptance Criteria

- [ ] Full draft validation is server authoritative and zero-provider-I/O.
- [ ] New definitions cannot publish from synthetic evidence.
- [ ] Request JavaScript preview receives only schema-validated arguments.
- [ ] Admin validation uses only pinned local schema in normal Studio requests.

## Validation

- [ ] `npm run test:arch021-tool-authoring-validation`
- [ ] `npm run test:arch020-external-publication`
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not build Tool UI or live tests.

## Implementation Notes

Keep historical ARCH-020 fixture utilities for automated tests; they cease to be proof for publishing new Phase 3 definitions.

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
