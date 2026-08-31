---
id: ARCH-002-BACKGROUND-008
architecture_id: ARCH-002
title: Integrate GenAI active spans in messaging worker
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 32
executor: codex
claimed_at: 2026-08-31 18:20:30+00:00
attempt: 2
depends_on:
- ARCH-002-BACKGROUND-006
- ARCH-002-SHARED-013
enables:
- ARCH-002-BACKGROUND-009
created: 2026-08-31
updated: '2026-08-31'
---

# Integrate GenAI active spans in messaging worker

## Objective

Use the shared GenAI active-span helpers around the existing CommerceAgent
workflow executed by `moda-messaging-worker`.

## Scope

Use `@modainteract/moda-interact-shared/observability/genai` for:

- one bounded conversation-turn span per inbound WhatsApp turn;
- agent invocation spans;
- tool invocation spans where the existing CommerceAgent/tool boundary exposes
  them cleanly;
- active-context nesting under the BullMQ Worker trace established by
  BACKGROUND-006;
- success/error span status and exception recording.

One inbound WhatsApp turn is one trace context chain. Do not model an entire
customer conversation as one trace.

## Out of Scope

- GenAI counters/histograms;
- BullMQ telemetry changes;
- provider/exporter setup;
- agent/tool business redesign;
- new CommerceAgent queue/service;
- prompt/message/tool payload recording.

## Acceptance Criteria

- [x] CommerceAgent work is nested under the inbound messaging Worker trace;
- [x] one inbound turn has bounded turn/agent/tool span structure;
- [x] application errors are rethrown unchanged after span error recording;
- [x] secrets, prompts, message content and tool payloads are not emitted;
- [x] arbitrary agent/tool names are not introduced as metric labels;
- [x] no GenAI metric work is implemented in this task.

## Validation

- [x] focused span nesting tests;
- [x] success/error tests;
- [x] sensitive-data tests/review;
- [x] affected repository tests;
- [x] typecheck;
- [x] production build.

## Stop Condition

After GenAI active-span integration is complete and validated, set this task to
`review`, complete the Completion Report, return to `moda_architect`, and STOP.

Do not begin BACKGROUND-009.

## Architect Resume Instruction — Shared Release Available

The shared-package blocker is resolved.

`ARCH-002-SHARED-012` and `ARCH-002-SHARED-013` are architect-accepted
Complete. The required capability is now available in the exact published
release:

```text
@modainteract/moda-interact-shared@0.5.0
```

Resume this same task.

Within BACKGROUND-008:

- update the background shared dependency/lockfile from exact `0.4.0` to exact
  `0.5.0`;
- use the shared GenAI helpers with metrics explicitly suppressed
  (`recordMetrics: false` or the architect-accepted equivalent);
- provide a bounded, non-sensitive `mapException` representation for the
  CommerceAgent/tool paths whose existing Errors may include external provider
  response detail;
- preserve and rethrow the original application error/value unchanged;
- preserve turn -> agent -> tool active-context nesting under the existing
  messaging BullMQ Worker trace.

Do not activate GenAI operational metrics in this task. That remains
BACKGROUND-009.

Do not create a local replacement for the shared GenAI helper.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/src/workers/whatsapp.worker.ts`
- `moda-interact-background/src/agents/commerce.agent.ts`
- `moda-interact-background/src/tools/search-product.ts`
- `moda-interact-background/tests/unit/observability/genai-observability.test.ts`
- `moda-interact-background/tests/unit/runtime/observability-startup.test.ts`
- `docs/decisions/background/ARCH-002/BACKGROUND-008-integrate-commerce-agent-genai-spans.md`

### Work Completed

- Upgraded the exact shared dependency and lockfile from `0.4.0` to the
  architect-approved `0.5.0` release.
- Wrapped each `message-received` WhatsApp job in one shared
  `observeConversationTurn("whatsapp", ...)` span inside the existing BullMQ
  Worker processor context.
- Wrapped the production CommerceAgent invocation and Shopify product-search
  tool execution with `observeAgentInvocation` and `observeAgentTool`.
- Passed `recordMetrics: false` at all three boundaries, without adding local
  GenAI instruments or metric helpers.
- Applied fixed, bounded, non-sensitive `mapException` representations at the
  turn, agent and tool boundaries. The shared helpers preserve and rethrow the
  original application error/value.
- Added focused in-memory trace evidence for Worker -> turn -> agent -> tool
  parentage, success/error status, semantic identities, unchanged error
  identity, sanitized exceptions, sensitive-data exclusion and metric
  suppression wiring.

### Validation Results

- `npm install @modainteract/moda-interact-shared@0.5.0 --save-exact`: passed;
  package and lockfile updated.
- `npm pkg get dependencies.@modainteract/moda-interact-shared && npm ls
  @modainteract/moda-interact-shared --depth=0`: passed; both report exact
  `0.5.0`.
- `npm test -- --run tests/unit/observability/genai-observability.test.ts`:
  passed, 1 file and 3 tests.
- `npm test -- --run tests/unit/agent/commerce.agent.pipeline.test.ts
  tests/unit/observability/genai-observability.test.ts`: passed, 2 files and 4
  tests.
- `npm test -- --run tests/unit/runtime/observability-startup.test.ts`: passed,
  1 file and 8 tests.
- `npm test`: 15 files passed, 1 failed and 2 skipped; 88 tests passed, 1
  failed and 4 skipped. The sole failure is the pre-existing unrelated
  `recovery-routing.service.test.ts` mock omission for
  `prisma.customerPhone.findMany`; all affected tests passed.
- `./node_modules/.bin/tsc --noEmit`: passed before and after focused changes.
- `npm run build`: passed, including Prisma Client generation and TypeScript
  production compilation.
- `"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick`: passed 7
  checks; retained the known unrelated `moda-interact/.npmrc`
  `shamefully-hoist` warning and reported the workspace baseline acceptable.
- VS Code diagnostics were clean for all changed production and test files.
- Final source review confirmed exact `0.5.0`, three canonical GenAI helper
  boundaries, explicit metric suppression at each boundary, no local GenAI
  metric instruments and no captured prompt/message/tool payload fields.

### Deviations

The focused nesting test uses an in-memory active span representing the BullMQ
Worker parent. BACKGROUND-006 separately proves the native BullMQ consumer span
is active in the processor; no Redis-backed test was required by this task.

### Assumptions

- The accepted BACKGROUND-006 BullMQ active-context guarantee remains the
  parent boundary for the turn helper invoked inside the Worker processor.

### Unresolved Issues

- The existing recovery-routing unit-test mock still lacks
  `prisma.customerPhone.findMany`, leaving the unrelated full suite one test
  short of green.
- `npm install` reported three high-severity audit findings and pending
  install-script approvals. They did not block this task's tests, typecheck,
  build or workspace doctor and were not remediated within this bounded task.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The resumed implementation satisfies the granular BACKGROUND-008 contract:

- the production background dependency is upgraded from exact shared version
  `0.4.0` to exact architect-approved `0.5.0`, with the lockfile resolving the
  published npm registry artifact;
- the WhatsApp `message-received` Worker path creates one shared
  `observeConversationTurn("whatsapp", ...)` active span inside the existing
  BullMQ processor context;
- the production CommerceAgent invocation is wrapped by the shared
  `observeAgentInvocation` helper;
- the production Shopify product-search tool is wrapped by the shared
  `observeAgentTool` helper;
- the resulting active-context structure is Worker -> turn -> agent -> tool;
- all three GenAI observation boundaries explicitly use
  `recordMetrics: false`, so BACKGROUND-009 metric activation has not started;
- no local GenAI meter, counter, histogram, provider, exporter or replacement
  helper was introduced;
- all three boundaries supply bounded, non-sensitive `mapException`
  representations rather than sending provider/tool response details to
  telemetry;
- the focused error-path test proves the original provider `Error` is rethrown
  unchanged by identity while the recorded exception messages are the bounded
  architect-approved representations;
- prompt text, customer message content, conversation summary, shop/customer
  identifiers, phone number, checkout token and provider error content are
  absent from the captured telemetry test representation;
- the production CommerceAgent/tool behavior, BullMQ queue/job contracts,
  retries/concurrency and worker topology remain unchanged.

The task submission accidentally dropped `ARCH-002-SHARED-013` from its
frontmatter dependency list when the previously blocked task was resumed.
Because SHARED-013 is already architect-accepted Complete and the implementation
actually consumes its published `0.5.0` release, this is coordination-document
drift rather than an implementation defect. The architect acceptance overlay
restores that dependency.

### Validation Reviewed

Accepted evidence:

- focused GenAI observability suite: 3/3 passed;
- CommerceAgent pipeline + GenAI observability: 4/4 passed;
- observability-startup suite: 8/8 passed;
- TypeScript `tsc --noEmit`: passed;
- production build: passed;
- workspace doctor quick: 7 checks passed;
- exact dependency/package inspection: `0.5.0`;
- direct source review confirms the three canonical helper boundaries,
  metric suppression, safe exception mapping, and absence of local GenAI
  metric instruments.

The repository-wide suite reports the same known unrelated
`recovery-routing.service.test.ts` Prisma mock omission
(`customerPhone.findMany`) already observed in earlier accepted background
tasks. All BACKGROUND-008 affected tests pass.

The reported npm audit/install-script warnings were not introduced as part of
the GenAI tracing behavior and were not remediated inside this bounded task.

### Architecture Conformance

Conforms.

One inbound WhatsApp job/turn is not extended into a cross-message
conversation trace. The task adds only the active GenAI span semantics assigned
to BACKGROUND-008 and leaves operational GenAI metrics to BACKGROUND-009.

### Follow-up

`ARCH-002-BACKGROUND-008` is Complete.

`ARCH-002-BACKGROUND-009` is now unblocked and may move to `ready`.

Do not begin GATEWAY-006 or SYSTEM-TEST-002 solely from this transition; the
remaining BACKGROUND-009 and other cross-domain prerequisites still apply.

