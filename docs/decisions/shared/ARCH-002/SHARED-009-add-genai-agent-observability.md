---
id: ARCH-002-SHARED-009
architecture_id: ARCH-002
title: Add GenAI active-span helpers
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 20
executor: codex
claimed_at: 2026-08-31T13:56:38Z
attempt: 1
depends_on:
  - ARCH-002-SHARED-007
enables:
  - ARCH-002-SHARED-011
created: 2026-08-31
updated: 2026-08-31
---

# Add GenAI active-span helpers

## Architecture

Architecture ID:

`ARCH-002`

Coordinator:

`moda_architect`

## Objective

Provide reusable active-span helpers for one GenAI conversation-turn execution
path.

## Context

SHARED-007 owns the generic Node OpenTelemetry runtime.

This task adds only generic GenAI span mechanics on top of the global tracer
provider. It deliberately does not add operational metrics; metric work is
owned by `ARCH-002-SHARED-011`.

## Scope

- add an active span helper for one conversation turn;
- add an active span helper for an agent invocation;
- add an active span helper for a tool invocation;
- preserve parent/child nesting through the active OpenTelemetry context;
- set success/error span status correctly;
- record bounded, non-sensitive span attributes where architecture-approved;
- rely on the global OpenTelemetry tracer provider;
- remain a lightweight no-op when no provider is installed.

## Out of Scope

Do NOT:

- add duration, count or error metrics;
- create metric instruments;
- add arbitrary metric dimensions;
- capture prompt, completion, message or tool payload bodies;
- add Prisma or BullMQ functionality;
- add service-specific CommerceAgent/recovery semantics;
- change service repositories;
- publish the package;
- start SHARED-011 or SHARED-010.

## Trace Model

```text
conversation turn
  -> invoke_agent
       -> execute_tool
            -> HTTP/Prisma/etc auto spans
```

A conversation is not one long-lived trace. Each inbound turn is independently
traceable.

## Requirements

Helpers must perform no network I/O themselves.

Do not create a tracer provider, exporter or SDK. Use the global provider
installed by the shared Node runtime.

Agent/tool names may appear only as bounded safe span attributes where useful.
Do not capture customer identifiers, prompt/completion bodies, message bodies,
credentials or provider secrets by default.

## Work Items

- [x] Add conversation-turn active-span helper.
- [x] Add agent-invocation active-span helper.
- [x] Add tool-invocation active-span helper.
- [x] Preserve active-context nesting.
- [x] Handle success/error status.
- [x] Add focused span tests.
- [x] Document the span-helper boundary.

## Acceptance Criteria

- [x] turn -> agent -> tool spans nest correctly;
- [x] success span status is correct;
- [x] thrown/rejected operations mark the owning span as error and rethrow;
- [x] nested auto-instrumented spans can inherit the active helper span;
- [x] prompt/completion/message/tool payload bodies are absent by default;
- [x] no provider/exporter/SDK is created by the helpers;
- [x] no metrics are introduced by this task;
- [x] focused tests/typecheck/build required by this implementation task pass.

## Validation

- [x] focused span nesting test;
- [x] success/error test;
- [x] sensitive-data review;
- [x] repository-required typecheck/build/tests relevant to changed code.

## Stop Condition

When the span-helper capability and required validation are complete:

1. record the Completion Report;
2. set this task to `review`;
3. return control to `moda_architect`;
4. STOP.

Do not begin SHARED-011, SHARED-010 or any other follow-up task.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/src/observability/genai.ts`
- `moda-interact-shared/src/observability/genai.test.ts`
- `moda-interact-shared/package.json`
- `moda-interact-shared/tsup.config.ts`
- `moda-interact-shared/README.md`
- `docs/decisions/shared/ARCH-002/SHARED-009-add-genai-agent-observability.md`

### Work Completed

- Added conversation-turn, agent-invocation, and tool-invocation active-span
  helpers on the existing global-provider `withObservedSpan` abstraction.
- Preserved turn -> agent -> tool -> automatically instrumented child context,
  success/error status, exception recording, and original error rethrow.
- Bounded safe agent, provider, model, and tool span values to 80 characters;
  the closed conversation channel vocabulary remains `whatsapp | other`.
- Added the Node/runtime `./observability/genai` package and build entry points.
- Documented no-op behavior and the no-payload, no-metrics, no-SDK, and
  no-network-I/O boundary.

### Validation Results

- `npx tsx --test src/observability/genai.test.ts` — pass, 2/2; verified no-op
  behavior, exact parent span IDs, one shared trace, inherited synthetic
  auto-instrumented span context, bounded attributes, success/error status,
  exception events, and original error rethrow.
- `npm test` — pass, 61 active tests; one existing Redis-gated BullMQ test
  skipped because `TEST_REDIS_URL` was not configured.
- `npm run typecheck` — pass.
- `npm run build` — pass; GenAI JavaScript and declaration entries emitted.
- `npm pack --dry-run` — pass, 37-file package artifact including the GenAI
  entry point.
- Consumer-style import of `./observability/genai` — pass; all three public
  helpers resolved as functions.
- Source/build scope scan — pass; no metrics, SDK/provider, exporter, network,
  Prisma, or BullMQ constructs in the GenAI helper.
- Sensitive-data source/build and exported-span review — pass; no prompt,
  completion, message body, tool body, payload, authorization, credential, or
  secret capture.
- Editor diagnostics for the helper, test, and build config — no errors.
- `scripts/workspace-doctor.sh --quick` — 6 checks pass; existing warning for
  `moda-interact/.npmrc` `shamefully-hoist` configuration and informational
  background local-development shared link.

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

The implementation conforms to the granular SHARED-009 scope:

- conversation-turn, agent-invocation and tool-invocation active-span helpers
  are provided through the shared observability package;
- turn -> agent -> tool active-context nesting is preserved;
- success/error span status and exception recording use the accepted shared
  `withObservedSpan` boundary;
- agent/provider/model/tool span values are bounded and no prompt, completion,
  message or tool payload bodies are captured;
- the helpers create no SDK, provider, exporter or network dependency;
- no Prisma or BullMQ functionality was introduced;
- no GenAI metric instruments or metric dimensions were introduced, preserving
  SHARED-011 as a separate independently reviewable capability;
- the `./observability/genai` package export and build entry are present.

The submitted completion report records focused tests, repository tests,
typecheck, build, package dry-run, consumer import and sensitive-data/scope
validation as passing. The compressed review archive does not contain
`node_modules`, so those commands were not redundantly re-run during architect
review; source, task boundary and validation evidence were inspected directly.

`ARCH-002-SHARED-011` is now unblocked and may move to `ready`.
`ARCH-002-SHARED-010` remains blocked until SHARED-011 is Complete.
