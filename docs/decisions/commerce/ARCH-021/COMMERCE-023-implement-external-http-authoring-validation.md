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
status: review
priority: 40
executor: null
claimed_at: null
attempt: 1
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

- [x] Add External HTTP full-definition validator.
- [x] Add named, hierarchy-authorized request-construction preview.
- [x] Compose request/response JS and visual/DIRECT structural validation.
- [x] Use COMMERCE-019 explicit action-result and COMMERCE-027 platform-role authorization contracts.
- [x] Add focused zero-provider-I/O tests.

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

- [x] External HTTP authoring validation is server authoritative and zero-provider-I/O.
- [x] Request preview receives only schema-validated Tool arguments and returns only a safe descriptor.
- [x] Connection/request/response/template failures use the common bounded diagnostics contract.
- [x] PLATFORM_ADMIN and PLATFORM_SUPER_ADMIN are admitted through hierarchy; merchant roles are denied.
- [x] Validation/preview errors remain explicit and never become mutation UNCONFIRMED state.
- [x] Validation creates no evidence that can satisfy the Phase 3 publication gate.

## Validation

- [x] `npm run test:arch021-external-tool-authoring-validation` (equivalent local Vitest binary: 6 passed; pnpm wrapper was blocked by ignored build scripts)
- [x] `npm run test:arch020-external-publication` (included in the 95-test Commerce-016/017/019 suite)
- [x] targeted lint/typecheck (lint passed; task-owned files have zero type diagnostics; repository-wide typecheck has unrelated baseline errors)
- [x] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not build Tool UI or execute a live HTTP request.

## Implementation Notes

Keep historical fixture utilities available for automated regressions only; they are not publication evidence.

## Completion Report

### Status
Ready for Review

### Files Changed
- `package.json`
- `src/commerce/integration/external/index.ts`
- `src/commerce/tool-authoring/external-validation.ts`
- `src/studio/tools/external-validation-server-actions.ts`
- `tests/external-tool-authoring-validation.test.ts`

### Work Completed
- Added authoritative, zero-provider-I/O EXTERNAL_HTTP definition validation with canonical schema parsing, immutable connection-revision metadata checks, request/response processor compilation, visual/DIRECT structural validation, and bounded common authoring issues.
- Added the platform-role-authorized request-construction Server Action. It validates CommerceAgent arguments before declarative or JavaScript construction, returns only the safe external request descriptor, and maps explicit action errors without creating mutation evidence.
- Exposed the validator through the existing external integration facade without adding a transport, credential, or publication receipt path.
- Focused repair mapping: `src/commerce/tool-authoring/external-validation.ts` validates arguments before request parsing and keeps compiler error codes on stable source paths; `tests/external-tool-authoring-validation.test.ts` covers that ordering and response-template rejection. No Architect Review correction was present; the Architect Review section below is unchanged.

### Validation Results
- Launcher evidence: prepared execution was resumed in parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-023`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-023`, branch `task/ARCH-021-COMMERCE-023`, Attempt 1, `execution_mode: agent`; existing handoff changes were preserved.
- `node_modules/.bin/vitest run tests/external-tool-authoring-validation.test.ts`: PASS, 1 file and 6 tests.
- Commerce-016/017/019 contract, authorization, publication, and integration command covering 9 files: PASS, 9 files and 95 tests.
- `node_modules/.bin/eslint src/commerce/tool-authoring/external-validation.ts src/commerce/integration/external/index.ts src/studio/tools/external-validation-server-actions.ts tests/external-tool-authoring-validation.test.ts`: PASS.
- `git diff --check`: PASS.
- Source audit for provider transport, network, credential, and provider calls in the new authoring/preview boundary: PASS; no forbidden calls found.
- `npm run typecheck`: non-zero with 15 existing diagnostics in 7 untouched route/test files; zero diagnostics in task-owned files. See Unresolved Issues for the unrelated baseline condition.
- Commerce integration command `tests/backend-integration.test.ts tests/commerce-lifecycle.test.ts tests/definition-execution.test.ts tests/mcp-service.test.ts tests/external-wiring.test.ts`: 67 passed, 2 failed in existing Commerce-013 backend bootstrap expectations in `tests/backend-integration.test.ts`; no task-owned file is involved.
- Initial `pnpm run test:arch021-external-tool-authoring-validation` was blocked before execution by the environment's `ERR_PNPM_IGNORED_BUILDS`; the equivalent local Vitest binary ran successfully after the prepared dependencies were available.

### Deviations
- None from the bounded Commerce-023 scope. No Shopify Admin validation, live HTTP request, credential display/decryption, live-test receipt, or Tool UI was added.

### Assumptions
- The existing `requireStudioPlatformRole('ADMIN')` hierarchy helper is the authoritative admission contract for platform administrators and super administrators and denial for merchant roles.
- The implementation branch commit is `fb5ed5ba1ad9269a00ecb5ef74275b980f9d453c`.

### Unresolved Issues
- Repository-wide typecheck remains non-zero because of 15 unrelated existing diagnostics in untouched files: the code-response preview route imports, agent-configuration tests, C20 fixture test, external wiring test, local MCP diagnostic test, and selected-shop-context tests.
- Two existing Commerce-013 backend integration expectations fail because `getCommerceBackend()` does not throw after reset; this is outside the task-owned diff and requires the owning integration task/architect decision.

### Architectural Concerns
None.

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
