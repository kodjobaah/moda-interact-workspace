---
id: ARCH-002-SHARED-011
architecture_id: ARCH-002
title: Add bounded GenAI operational metrics
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 21
executor: codex
claimed_at: 2026-08-31T14:06:14Z
attempt: 1
depends_on:
  - ARCH-002-SHARED-009
enables:
  - ARCH-002-SHARED-010
created: 2026-08-31
updated: 2026-08-31
---

# Add bounded GenAI operational metrics

## Architecture

Architecture ID:

`ARCH-002`

Coordinator:

`moda_architect`

## Objective

Add bounded reusable GenAI duration and error metrics to the accepted GenAI
observability helper boundary.

## Context

SHARED-009 owns active span mechanics.

This task adds only generic operational metrics. It must not redesign the span
helpers or introduce service-specific CommerceAgent semantics.

## Scope

- record duration for conversation-turn, agent and tool operations;
- record generic success/error outcomes where required;
- create metric instruments once per process/module rather than dynamically per
  agent/tool invocation;
- use only absent or architecture-controlled low-cardinality metric dimensions;
- use the global OpenTelemetry meter provider;
- remain lightweight when no meter provider is installed.

## Out of Scope

Do NOT:

- redesign SHARED-009 span helpers;
- add new tracing/exporter/provider infrastructure;
- use arbitrary agent names as metric dimensions;
- use arbitrary tool names as metric dimensions;
- use model IDs as metric dimensions unless a future architecture explicitly
  defines a bounded vocabulary;
- use conversation, customer, message, job, recovery, checkout or shop IDs as
  metric dimensions;
- capture prompt/completion/message/tool payload contents;
- change service repositories;
- publish the package;
- begin SHARED-010.

## Cardinality Rule

String truncation is not cardinality protection.

Metric dimensions must be absent or selected from a small
architecture-controlled vocabulary.

High-cardinality values may never become a metric label merely because their
string length is bounded.

## Work Items

- [x] Add duration instruments.
- [x] Add bounded success/error outcome recording where required.
- [x] Ensure instruments are process/module singletons.
- [x] Ensure arbitrary agent/tool names are absent from metric attributes.
- [x] Add metric attribute-set/cardinality tests.
- [x] Add sensitive-data assertions.

## Acceptance Criteria

- [x] operation durations are recorded;
- [x] required success/error outcomes are recorded;
- [x] metric instruments are not dynamically created per invocation;
- [x] arbitrary agent/tool names are absent from metric attributes;
- [x] high-cardinality Moda/business identifiers are absent from metric
      attributes;
- [x] repeated/fuzzed agent/tool names do not create new series dimensions;
- [x] prompt/completion/message/tool contents are absent;
- [x] focused tests/typecheck/build required by this implementation task pass.

## Validation

- [x] metric attribute-set assertions;
- [x] high-cardinality repetition/fuzz test;
- [x] success/error metric test;
- [x] sensitive-data review;
- [x] repository-required typecheck/build/tests relevant to changed code.

## Stop Condition

When the metric capability and required validation are complete:

1. record the Completion Report;
2. set this task to `review`;
3. return control to `moda_architect`;
4. STOP.

Do not begin SHARED-010 or any other follow-up task.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/src/observability/genai.ts`
- `moda-interact-shared/src/observability/genai.metrics.test.ts`
- `moda-interact-shared/src/observability/test-fixtures/genai-metrics-app.ts`
- `moda-interact-shared/README.md`
- `docs/decisions/shared/ARCH-002/SHARED-011-add-genai-operational-metrics.md`

### Work Completed

- Extended the accepted SHARED-009 helpers with module-singleton duration
  histograms and operation counters for conversation-turn, agent, and tool
  operations using the global OpenTelemetry meter provider.
- Recorded success/error outcomes with only the closed `success | error`
  vocabulary; turn metrics additionally use the closed `whatsapp | other`
  channel vocabulary.
- Kept arbitrary agent, provider, model, tool, and Moda business identifiers
  out of metric attributes while retaining accepted bounded span attributes.
- Failure-isolated metric recording so it cannot replace an application result
  or original application error.
- Added in-memory metric export coverage with 50 fuzzed agent/tool names and
  documented the final metric boundary.

### Validation Results

- `npx tsx --test src/observability/genai.metrics.test.ts` — pass, 1/1;
  verified six fixed metric names, duration samples, success/error counts,
  exact attribute sets, closed values, fuzz stability, and sensitive-data
  absence.
- `npm run typecheck` — pass.
- Focused `npx tsx --test src/observability/genai.test.ts
  src/observability/genai.metrics.test.ts` — pass, 3/3; accepted span behavior
  remains intact alongside metrics.
- `npm test` — pass, 62 active tests; one existing Redis-gated BullMQ test
  skipped because `TEST_REDIS_URL` was not configured.
- `npm run build` — pass; GenAI JavaScript and declarations emitted.
- `npm pack --dry-run` — pass, 37-file package artifact.
- Consumer-style import of `./observability/genai` — pass; the three accepted
  public helper functions remain available.
- Exact source scan — pass; exactly three histograms and three counters are
  constructed at module scope before exported helper functions.
- Metric dimension and sensitive-data source/build scan — pass; no arbitrary
  names, Moda/business IDs, prompt, completion, message/tool payload,
  authorization, credential, or secret values reach metric recording.
- Editor diagnostics for implementation and focused tests — no errors.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation conforms to the granular SHARED-011 scope:

- duration histograms and operation counters are created once at module scope for
  conversation-turn, agent-invocation and tool-invocation operations;
- metric dimensions are restricted to the closed `outcome=success|error`
  vocabulary, with conversation-turn metrics additionally using the closed
  `channel=whatsapp|other` vocabulary;
- arbitrary agent, provider, model and tool names are excluded from metric
  attributes;
- conversation, customer, message, job, recovery, checkout and shop identifiers
  are excluded from metric attributes;
- prompt, completion, message and tool payload contents are not recorded;
- metric recording is failure-isolated and does not replace application results
  or original application errors;
- the accepted SHARED-009 active-span behaviour remains intact;
- no provider/exporter runtime, Prisma, BullMQ, service-repository or publication
  work was introduced.

The submitted completion report records focused metric tests, cardinality fuzzing,
success/error coverage, sensitive-data checks, typecheck, repository tests, build,
package dry-run and consumer import as passing. The Redis-gated BullMQ integration
test was skipped because `TEST_REDIS_URL` was not configured; that test is outside
the SHARED-011 metric scope and does not block acceptance.

`ARCH-002-SHARED-010` is now unblocked and may move to `ready` as a publication-only
task.
