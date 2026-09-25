---
id: ARCH-021-COMMERCE-023
architecture_id: ARCH-021
title: Implement External HTTP authoring validation and request preview
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
  - ARCH-021-COMMERCE-019
  - ARCH-020-COMMERCE-030
enables:
  - ARCH-021-COMMERCE-021
created: 2026-09-24
updated: 2026-09-25
---

# Implement External HTTP authoring validation and request preview

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Implement the authoritative zero-provider-I/O validator and request-construction preview for canonical Phase 3 `EXTERNAL_HTTP` Tool definitions without depending on Shopify Admin compiler work.

## Context

COMMERCE-016 owns the canonical Commerce Tool definition, COMMERCE-017 owns bounded `buildRequest({args})`, and COMMERCE-019 owns the common validation result/auth/publication gate. This task composes only the External HTTP authoring semantics needed by COMMERCE-021.

## Scope

Primary files:

```text
src/commerce/tool-authoring/external-validation.ts
src/studio/tools/external-validation-server-actions.ts
src/commerce/external-publication/index.ts       # only existing structural helpers needed for visual/response validation
tests/external-tool-authoring-validation.test.ts
package.json
```

## Out of Scope

- Shopify Admin GraphQL validation.
- Real external HTTP requests.
- Credential display/decryption.
- Live-test receipts.
- Tool editor UI.

## Requirements

### R1 — full EXTERNAL_HTTP validation

For a candidate full definition:

1. parse through COMMERCE-016 `CommerceToolDefinitionSchema`;
2. require `execution.kind === 'EXTERNAL_HTTP'`;
3. confirm the exact immutable connection revision exists and its owning connection is enabled;
4. for `DECLARATIVE`, validate request mappings/static safe headers with no network call;
5. for `JAVASCRIPT`, compile through COMMERCE-017;
6. validate response mode:
   - DIRECT: JSON + resultPath/resultSchema structural contract;
   - OBJECT/LIST: accepted visual publication-shape compatibility;
   - JAVASCRIPT: compile the accepted response processor;
7. validate responseTemplate against the resulting resultSchema;
8. return deterministic issues using COMMERCE-019 `ToolAuthoringValidation`.

No DNS, HTTP, provider or credential operation is permitted.

### R2 — request-construction preview

Expose the named Server Action `src/studio/tools/external-validation-server-actions.ts` and require exactly `requireStudioPlatformRole('ADMIN')` before any database-backed validation/preview work. Do not create a function-valued production port or duplicate role matrix. The action accepts exactly:

```ts
{
  source?: string;
  request: unknown;
  arguments: unknown;
  inputSchema: unknown;
}
```

The exact DTO may be expressed as a strict discriminated union for declarative vs JavaScript request mode, but it MUST contain no connection credential value, provider response or absolute origin override.

Before request construction:

1. validate `arguments` through `compileSubset(inputSchema, 'input')`;
2. execute declarative mapping or COMMERCE-017 `buildRequest({args})`;
3. parse the result through COMMERCE-016 `ExternalRequestDescriptorSchema`;
4. return only `ToolAuthoringActionResult<ExternalRequestDescriptor>` using the COMMERCE-019 explicit error contract;
5. map database connectivity failures to `DATABASE_UNAVAILABLE`; never return `unknown`/`UNCONFIRMED` from this non-mutating action.

Preview performs no connection transport call.

### R3 — explicit errors and deterministic issue paths

Validation/preview are non-mutating. `FORBIDDEN`, `INVALID_INPUT`, `NOT_FOUND`, `DATABASE_UNAVAILABLE` and `INTERNAL_ERROR` must remain explicit COMMERCE-019 action results. A rejected validation/preview call MUST NOT be reconciled as a Tool mutation and MUST NOT create `UNCONFIRMED`. Unexpected errors are logged server-side through the approved shared structured logger.

External validation issues use stable paths under `/execution/...`, `/inputSchema` or `/responseTemplate` as appropriate. Maximum issue count and message-safety rules come from COMMERCE-019.

### R4 — publication relationship

This task proves structural validity only. It MUST NOT create a live-test receipt. After successful validation, publication remains blocked by COMMERCE-019 `LIVE_TEST_REQUIRED`.

### R5 — focused validation

Add `test:arch021-external-tool-authoring-validation` proving:

- valid declarative draft passes with zero network calls;
- missing/disabled connection fails;
- request JS syntax/entrypoint/descriptor errors surface;
- request preview validates CommerceAgent arguments before construction;
- DIRECT/Visual/response-JS branches validate deterministically;
- responseTemplate compatibility is enforced;
- provider transport is never called;
- common issue/auth contract comes from COMMERCE-019.

## Work Items

- [ ] Add External HTTP full-definition validator.
- [ ] Add named, hierarchy-authorized request-construction preview.
- [ ] Compose request/response JS and visual/DIRECT structural validation.
- [ ] Use COMMERCE-019 explicit action-result and COMMERCE-027 platform-role authorization contracts.
- [ ] Add focused zero-provider-I/O tests.

## Interfaces / Contracts

Consumes COMMERCE-016 Tool contracts, COMMERCE-017 request processor and COMMERCE-019 common validation/auth contract.

Produces the authoritative External HTTP validation/preview boundary consumed by COMMERCE-021.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-017
- ARCH-021-COMMERCE-019
- ARCH-020-COMMERCE-030

## Enables

- ARCH-021-COMMERCE-021

## Acceptance Criteria

- [ ] External HTTP authoring validation is server authoritative and zero-provider-I/O.
- [ ] Request preview receives only schema-validated Tool arguments and returns only a safe descriptor.
- [ ] Connection/request/response/template failures use the common bounded diagnostics contract.
- [ ] PLATFORM_ADMIN and PLATFORM_SUPER_ADMIN are admitted through hierarchy; merchant roles are denied.
- [ ] Validation/preview errors remain explicit and never become mutation UNCONFIRMED state.
- [ ] Validation creates no evidence that can satisfy the Phase 3 publication gate.

## Validation

- [ ] `npm run test:arch021-external-tool-authoring-validation`
- [ ] `npm run test:arch020-external-publication`
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not build Tool UI or execute a live HTTP request.

## Implementation Notes

Keep historical fixture utilities available for automated regressions only; they are not publication evidence.

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
