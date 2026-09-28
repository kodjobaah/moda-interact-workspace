---
id: ARCH-021-COMMERCE-080
architecture_id: ARCH-021
title: Render the complete External HTTP candidate during non-durable Test
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 73
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-054
  - ARCH-021-COMMERCE-063
enables:
  - ARCH-021-COMMERCE-081
created: 2026-09-28
updated: 2026-09-28
---

# Render the complete External HTTP candidate during non-durable Test

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Extend the existing non-durable External HTTP live-Test backend so it accepts the complete current Tool definition, validates Result Template compatibility, executes Request/Response, renders the canonical production result through `renderDefinitionResult`, and returns the bounded text the agent would receive.

## Context

The current `external-live-test.ts` accepts Request/Response pieces separately and stops after processed-result contract validation. The Test UI therefore cannot show the populated Result Template. Production execution already defines the canonical External data envelope (`ExternalHttpResultDataSchema` with `values`) and canonical renderer (`renderDefinitionResult`).

This task changes only the backend Test contract. UI presentation is COMMERCE-081.

## Scope

Primary implementation:

```text
src/commerce/tool-authoring/external-live-test.ts
src/studio/tools/external-validation-server-actions.ts
src/commerce/tool-definition/publication.ts          # consume externalOutputSchema
src/commerce/execution/renderer.ts                   # consume only unless defect is proven
```

Tests:

```text
tests/external-http-live-test.test.ts
tests/external-http-live-test-action.test.ts
```


## Out of Scope

- Changing External Request/Response authoring semantics.
- Creating durable Test receipts/publication proof.
- Changing production renderer/template grammar.
- External Test React presentation; COMMERCE-081.
- Shopify live testing; COMMERCE-082.
- Persisting provider responses or customer data.

## Requirements

### R1 — one complete-candidate input contract

Replace the granular public live-Test input with this semantic shape (names may vary only mechanically):

```ts
type ExternalHttpLiveTestInput = {
  definition: CommerceToolDefinition; // execution.kind MUST be EXTERNAL_HTTP
  arguments: Record<string, unknown>;
  shopId: string | null;
};
```

The Server Action/backend must parse `definition` with `CommerceToolDefinitionSchema`, reject non-External definitions, and server-authorize the caller exactly as today. Do not trust a browser-supplied split between response format/media types/result schema/template.

### R2 — validate template compatibility before provider I/O

Before calling `observe`, validate:

```text
responseTemplate
against
externalOutputSchema(definition.execution.resultSchema)
```

using the COMMERCE-063 canonical Result Template validator. If incompatible, return a bounded deterministic Test failure and perform zero provider call.

### R3 — preserve existing five execution stages and add rendering

The result stages become exactly:

```text
requestConstruction
connectionResolution
providerRequest
responseProcessing
resultValidation
resultRendering
```

Existing stage meanings/error redaction remain unchanged.

### R4 — construct the same result envelope as production

After processed values pass `compileCommerceResultSchema(execution.resultSchema)`, construct canonical success data through `ExternalHttpResultDataSchema` with:

```text
source = EXTERNAL_HTTP
connectionRevisionId = definition.execution.connectionRevisionId
observedAt = current Test clock ISO timestamp
values = validated processed values
```

Then construct a valid `CommerceToolResult` success and call:

```ts
renderDefinitionResult(definition, result, {
  maxRecommendations: 20,
  maxSearchResults: 20,
})
```

Do not implement a second template renderer.

### R5 — return agent-facing rendered output without widening sensitive diagnostics

On successful rendering return:

```text
processedResult    existing bounded diagnostic value
renderedText       exact renderer output the agent would receive
```

`renderedText` is already bounded by the production renderer (4096 chars). Provider body/request diagnostics retain their existing bounds/redaction. Do not add secrets, credentials, full headers or unbounded payloads.

If the canonical renderer returns an ERROR because the template cannot render, mark `resultRendering` failed with a stable code and return only safe/bounded diagnostic text. A legitimate authored `unavailable` fallback produced by a valid template is the agent-facing result and is not itself a transport failure.

### R6 — Test remains strictly non-durable

A live Test must perform no Tool/ToolRevision/audit/operation receipt/publication-proof write. It must not change saved validation or publication state.

## Work Items

- [x] Replace split live-Test input with a complete External Tool definition + arguments + shop context.
- [x] Validate full definition/provider kind server-side.
- [x] Enforce canonical Result Template compatibility before provider I/O.
- [x] Preserve existing Request/connection/provider/Response/result validation stages.
- [x] Add `resultRendering` stage.
- [x] Construct the production External `data.values` envelope.
- [x] Reuse `renderDefinitionResult` for agent-facing text.
- [x] Return bounded `renderedText` plus existing safe diagnostics.
- [x] Preserve zero-write semantics and existing credential/body redaction.
- [x] Add success/failure/no-provider-on-invalid-template tests.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-054                    existing External non-durable live-Test mechanism
ARCH-021-COMMERCE-063                    canonical template compatibility
CommerceToolDefinitionSchema             complete definition parsing
externalOutputSchema                     production template contract
ExternalHttpResultDataSchema              production External data envelope
renderDefinitionResult                    production renderer
```

No new Shared contract; this is Studio-internal Commerce authoring API.

## Dependencies

- ARCH-021-COMMERCE-054
- ARCH-021-COMMERCE-063

## Enables

- ARCH-021-COMMERCE-081

## Acceptance Criteria

- [x] Live Test accepts one complete valid External Tool definition rather than independently supplied definition fragments.
- [x] Invalid/incompatible Result Template fails before provider I/O.
- [x] Existing five stages remain and `resultRendering` is added.
- [x] Successful Test uses production `ExternalHttpResultDataSchema` semantics with validated values under `data.values`.
- [x] `renderDefinitionResult` is the only template renderer used.
- [x] Successful result includes the exact bounded `renderedText` the agent would receive.
- [x] Existing request/provider/processed-result diagnostics remain bounded and credential-safe.
- [x] Test performs zero persistence/publication-proof write.
- [x] Existing non-template failure mappings remain backwards-equivalent where the stage is unchanged.

## Validation

- [x] `./node_modules/.bin/vitest run tests/external-http-live-test.test.ts tests/external-http-live-test-action.test.ts tests/external-wiring.test.ts` (24 tests passed)
- [x] Focused assertion that invalid template causes zero `observe`/provider calls (covered by live-Test unit tests)
- [x] Focused assertion that rendered template reads `result.values.*` (integration assertion returns `missing`)
- [x] Focused assertion that Test writes no publication receipt/audit/Tool state (action and wiring suites passed)
- [x] Targeted ESLint for changed files (passed)
- [x] Changed-file TypeScript diagnostics and repository typecheck baseline reconciliation (see Completion Report)
- [x] `git diff --check` (passed)

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Keep authoring diagnostics separate from production authorization/grant semantics. Reuse production **data shape + renderer**, not production MCP grant resolution. The Test is staff-authorized Studio execution of an unsaved candidate.

## Completion Report

### Status

Review

### Files Changed

`src/commerce/tool-authoring/external-live-test.ts`; `src/studio/external-http/editor.tsx`; `src/studio/external-http/test-tab.tsx`; `src/studio/tools/new-tool-editor.tsx`; `src/studio/tools/tool-editor.tsx`; `tests/external-http-live-test-action.test.ts`; `tests/external-http-live-test.test.ts`; `tests/external-tools-ui.test.tsx`; `tests/external-wiring.test.ts`.

### Work Completed

The live-Test API now accepts a complete `CommerceToolDefinition` candidate with arguments and shop context, validates its Result Template compatibility before provider observation, and rejects non-External definitions. Successful response processing is validated and wrapped in the canonical External result data (`values`, connection revision and Test clock timestamp), then rendered by `renderDefinitionResult`; the returned result includes the bounded agent-facing `renderedText` and a `resultRendering` stage. Existing diagnostics, credential redaction, and no-durable-write behavior are preserved.

The existing authoring editors now pass Tool identity and Result Template state through the Test tab, which builds and schema-parses the full candidate. Candidate identity changes invalidate stale results. This is payload wiring only; Test result presentation remains for COMMERCE-081.

### Validation Results

Passed: `./node_modules/.bin/vitest run tests/external-http-live-test.test.ts tests/external-http-live-test-action.test.ts tests/external-wiring.test.ts` (3 files, 24 tests); `./node_modules/.bin/vitest run tests/external-tools-ui.test.tsx` (81 tests); targeted Test-tab UI selection (8 tests); targeted ESLint across all changed source/test files; `git diff --check`.

TypeScript: `./node_modules/.bin/tsc --noEmit` exits 2 with 29 diagnostics across the repository. The complete-definition Test-tab payload and live-Test backend/action/integration tests have no diagnostics. Four diagnostics remain in touched files: existing `ResponseTemplate` typing errors at untouched props in `src/studio/tools/new-tool-editor.tsx` and `src/studio/tools/tool-editor.tsx`, plus an unrelated mock-call assertion in `tests/external-tools-ui.test.tsx`. The repository-wide check is not clean; no unrelated type fixes were made.

Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-080`, branch `task/ARCH-021-COMMERCE-080`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-080`, same task branch. Parent claim commit `a6d55f78a241562f1821848c57f6fef993dbc071`; definition materialization commit `0927af241c89a77c715931b0d6dbe0713ab4b6a9`; implementation commit `ee87616`. Dependency gate passed for COMMERCE-054 and COMMERCE-063; task branch synchronization was not needed; `origin/main` was current. Recursive submodule sync/update passed; database submodule recorded at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`. The shared workspace and shared implementation checkout were not used for implementation; no other task worktree was reused. The implementation commit was pushed explicitly to `origin/task/ARCH-021-COMMERCE-080`.

### Deviations

The Task-tab payload and editor boundary wiring were included so the new complete-definition backend contract is reachable from both existing editors. Test result presentation was not changed and remains out of scope for COMMERCE-080. Repository TypeScript validation is recorded as limited by the current 47-diagnostic baseline described above.

### Assumptions

The selected shop remains supplied by the existing Studio selection/authorization flow. The Result Template is parsed from the editor's current JSON text and is part of the same unsaved candidate as Request and Response state.

### Unresolved Issues

Repository-wide `tsc --noEmit` is not clean (29 diagnostics); see Validation Results for relevant pre-existing diagnostics and the changed-file reconciliation.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is accepted.

C080 satisfies the complete-candidate External HTTP live-Test contract. The backend parses one complete `CommerceToolDefinition`, rejects non-External definitions, validates Result Template compatibility against `externalOutputSchema(execution.resultSchema)` before provider observation, preserves the existing Request/connection/provider/Response/result-validation stages, and adds the required `resultRendering` stage.

After Response processing succeeds, the implementation validates processed values with the canonical Commerce result schema, constructs the same `ExternalHttpResultDataSchema` envelope used by production (`source`, `connectionRevisionId`, `observedAt`, `values`), constructs a valid `CommerceToolResult`, and delegates rendering to the production `renderDefinitionResult` boundary. No second template renderer is introduced.

The successful Test result returns the existing bounded processed-result diagnostics plus the exact bounded `renderedText` returned by the production renderer. Template incompatibility fails before provider I/O; renderer failure is mapped to a stable bounded rendering-stage failure. Existing request/provider diagnostics and zero-write semantics remain unchanged.

Both new and persisted External HTTP editors now pass the current unsaved Tool identity, Result Template text, execution/Request state, input schema, arguments and selected shop into the Test tab. The Test tab schema-parses the full local definition immediately before execution and invalidates stale results when candidate identity changes. This is candidate-payload wiring only; presentation of rendered Test output remains correctly deferred to COMMERCE-081.

The launcher/worktree evidence is complete: dedicated parent and implementation worktrees were used, dependency gating for COMMERCE-054 and COMMERCE-063 passed, task-branch synchronization was not needed, `origin/main` was current at preparation, recursive submodule synchronization passed, and the pinned `database` commit is recorded. Implementation commit `ee876163` and parent report commit `937c54df` are pushed and the worktrees are reported clean.

### Reviewed Files

- `src/commerce/tool-authoring/external-live-test.ts`
- `src/studio/tools/external-validation-server-actions.ts`
- `src/studio/external-http/test-tab.tsx`
- `src/studio/external-http/editor.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/commerce/tool-definition/publication.ts`
- `src/commerce/execution/renderer.ts`
- `tests/external-http-live-test.test.ts`
- `tests/external-http-live-test-action.test.ts`
- `tests/external-wiring.test.ts`
- `tests/external-tools-ui.test.tsx`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Backend/action/integration packet: 24/24 passed across three files.
- External Tools UI suite: 81/81 passed.
- Targeted Test-tab UI selection: 8 tests passed.
- Invalid-template/no-provider assertion: passed.
- Production `result.values.*` renderer integration assertion: passed.
- Zero-write Test-path assertions: passed.
- Targeted ESLint: passed.
- `git diff --check`: passed.
- Repository `tsc --noEmit`: 29 diagnostics remain. The new complete-definition Test payload and backend/action/integration paths have no diagnostics; four diagnostics in touched files are documented at pre-existing unchanged template-typing/mock-assertion sites.

### Architecture Conformance

Conforms.

C080 reuses the production External result envelope and renderer without widening provider authorization, persistence, shared contracts, template grammar or Test presentation scope. Live Test remains a staff-authorized, non-durable execution of the current unsaved candidate.

### Follow-up

None for C080. ARCH-021-COMMERCE-080 is Complete.

COMMERCE-081 is listed as enabled by C080 but is not materialized in this submitted parent snapshot, so no task-status promotion is performed here. When C081 is materialized, its dependency on C080 is satisfied.
