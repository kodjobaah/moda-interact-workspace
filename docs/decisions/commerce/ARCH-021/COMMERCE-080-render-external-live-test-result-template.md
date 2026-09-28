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
status: in_progress
priority: 73
executor: copilot
claimed_at: 2026-09-28T06:23:53Z
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

- [ ] Replace split live-Test input with a complete External Tool definition + arguments + shop context.
- [ ] Validate full definition/provider kind server-side.
- [ ] Enforce canonical Result Template compatibility before provider I/O.
- [ ] Preserve existing Request/connection/provider/Response/result validation stages.
- [ ] Add `resultRendering` stage.
- [ ] Construct the production External `data.values` envelope.
- [ ] Reuse `renderDefinitionResult` for agent-facing text.
- [ ] Return bounded `renderedText` plus existing safe diagnostics.
- [ ] Preserve zero-write semantics and existing credential/body redaction.
- [ ] Add success/failure/no-provider-on-invalid-template tests.

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

- [ ] Live Test accepts one complete valid External Tool definition rather than independently supplied definition fragments.
- [ ] Invalid/incompatible Result Template fails before provider I/O.
- [ ] Existing five stages remain and `resultRendering` is added.
- [ ] Successful Test uses production `ExternalHttpResultDataSchema` semantics with validated values under `data.values`.
- [ ] `renderDefinitionResult` is the only template renderer used.
- [ ] Successful result includes the exact bounded `renderedText` the agent would receive.
- [ ] Existing request/provider/processed-result diagnostics remain bounded and credential-safe.
- [ ] Test performs zero persistence/publication-proof write.
- [ ] Existing non-template failure mappings remain backwards-equivalent where the stage is unchanged.

## Validation

- [ ] `npx vitest run tests/external-http-live-test.test.ts tests/external-http-live-test-action.test.ts`
- [ ] focused assertion that invalid template causes zero `observe`/provider calls
- [ ] focused assertion that rendered template reads `result.values.*`
- [ ] focused assertion that Test writes no publication receipt/audit/Tool state
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Keep authoring diagnostics separate from production authorization/grant semantics. Reuse production **data shape + renderer**, not production MCP grant resolution. The Test is staff-authorized Studio execution of an unsaved candidate.

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
