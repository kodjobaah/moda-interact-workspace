---
id: ARCH-002-BACKGROUND-009
architecture_id: ARCH-002
title: Integrate bounded GenAI operational metrics in messaging worker
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 33
executor: codex
claimed_at: 2026-08-31 18:32:23+00:00
attempt: 1
depends_on:
- ARCH-002-BACKGROUND-008
enables:
- ARCH-002-GATEWAY-006
- ARCH-002-SYSTEM-TEST-002
created: 2026-08-31
updated: '2026-08-31'
---

# Integrate bounded GenAI operational metrics in messaging worker

## Objective

Use the shared GenAI operational metric helpers for the existing CommerceAgent
workflow without increasing metric cardinality.

## Scope

Integrate the published shared GenAI duration/outcome metric behaviour for:

- inbound conversation turns;
- agent invocations;
- tool invocations.

Preserve the span semantics accepted in BACKGROUND-008.

Metric attributes must remain restricted to the bounded vocabularies provided
by the shared helper. Arbitrary agent/tool/model/provider/customer/conversation
identifiers must not become metric dimensions.

## Out of Scope

- tracing redesign;
- BullMQ telemetry changes;
- token/cost billing architecture;
- prompt/message/tool payload telemetry;
- provider/exporter setup;
- Grafana dashboards.

## Acceptance Criteria

- [x] GenAI turn/agent/tool duration and outcome metrics are emitted;
- [x] metric dimensions remain bounded under varied agent/tool names;
- [x] metric instruments are not created per invocation;
- [x] sensitive content/identifiers are absent;
- [x] metric recording failure cannot replace the application result/error;
- [x] BACKGROUND-008 span behaviour remains unchanged.

## Validation

- [x] focused GenAI metric tests;
- [x] cardinality fuzz test;
- [x] sensitive-data test/review;
- [x] failure-isolation test;
- [x] affected repository tests;
- [x] typecheck;
- [x] production build.

## Stop Condition

After GenAI operational metrics are complete and validated, set this task to
`review`, complete the Completion Report, return to `moda_architect`, and STOP.

Do not begin gateway or system-test work.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/src/workers/whatsapp.worker.ts`
- `moda-interact-background/src/agents/commerce.agent.ts`
- `moda-interact-background/src/tools/search-product.ts`
- `moda-interact-background/tests/fixtures/genai-metrics.ts`
- `moda-interact-background/tests/unit/observability/genai-metrics.test.ts`
- `moda-interact-background/tests/unit/observability/genai-observability.test.ts`
- `docs/decisions/background/ARCH-002/BACKGROUND-009-integrate-commerce-agent-genai-metrics.md`

### Work Completed

- Removed the explicit `recordMetrics: false` suppression from the accepted
	conversation-turn, CommerceAgent invocation and product-search tool helper
	boundaries, activating the shared default-on operational metrics.
- Preserved all three bounded `mapException` callbacks and the accepted Worker
	-> turn -> agent -> tool active-context span structure.
- Added isolated in-memory OpenTelemetry metric evidence for all six exact
	shared metric names, duration aggregation, success/error counts and exact
	bounded attribute sets.
- Fuzzed 40 distinct agent/provider/model/tool names and proved they produce no
	additional metric series or sensitive metric attributes.
- Proved the six shared instruments are constructed once per module load and
	are not recreated across invocations.
- Proved synchronous duration-histogram and operation-counter failures cannot
	replace successful application results or original application errors.

### Validation Results

- Initial `npm test -- --run
	tests/unit/observability/genai-observability.test.ts`: expected discriminating
	result, 2 existing span tests passed and only the obsolete metric-suppression
	assertion failed before it was updated.
- `npm test -- --run tests/unit/observability/genai-observability.test.ts
	tests/unit/observability/genai-metrics.test.ts`: passed, 2 files and 4 tests.
- `npm test -- --run tests/unit/agent/commerce.agent.pipeline.test.ts
	tests/unit/observability/genai-observability.test.ts
	tests/unit/observability/genai-metrics.test.ts
	tests/unit/runtime/observability-startup.test.ts`: passed, 4 files and 13
	tests, including the final post-edit run.
- `npm test -- --run tests/unit/observability/genai-metrics.test.ts`: passed, 1
	file and 1 test after strengthening duration histogram assertions.
- `./node_modules/.bin/tsc --noEmit`: passed.
- `npm test`: 16 files passed, 1 failed and 2 skipped; 89 tests passed, 1 failed
	and 4 skipped. The sole failure is the unchanged, unrelated
	`recovery-routing.service.test.ts` mock omission for
	`prisma.customerPhone.findMany` recorded by BACKGROUND-008.
- `npm run build`: passed, including Prisma Client generation and TypeScript
	production compilation.
- `"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick`: passed 7 checks;
	retained the existing `moda-interact/.npmrc` `shamefully-hoist` warning and
	reported the workspace development baseline acceptable.
- `git diff --check`: passed for `moda-interact-background`.
- VS Code diagnostics: no errors in changed production or test files.
- Exact source scans: zero `recordMetrics: false` suppressions, three canonical
	shared GenAI helper boundaries, three safe exception mappers and no local
	GenAI metric instruments/helpers.

### Deviations

None.

### Assumptions

- The accepted BACKGROUND-006 BullMQ active-context guarantee remains the
	Worker parent boundary for the turn helper, as accepted in BACKGROUND-008.

### Unresolved Issues

- The existing recovery-routing unit-test mock still lacks
	`prisma.customerPhone.findMany`, leaving the unrelated full suite one test
	short of green.
- `npm install` continues to report three high-severity audit findings and five
	pending install-script approvals already observed in BACKGROUND-008. They did
	not block focused tests, typecheck, build or workspace validation and were not
	remediated within this bounded task.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation satisfies the final granular background GenAI-metrics
boundary:

- the three architect-accepted GenAI observation boundaries remain exactly the
  conversation-turn, CommerceAgent invocation and Shopify product-search tool
  boundaries established by BACKGROUND-008;
- the explicit `recordMetrics: false` suppression was removed from those
  boundaries, activating the shared default-on SHARED-011 metric behaviour from
  `@modainteract/moda-interact-shared@0.5.0`;
- the BACKGROUND-008 `mapException` callbacks remain in place and the existing
  Worker -> turn -> agent -> tool active-context tracing structure is preserved;
- no service-local GenAI meter, counter, histogram or replacement metric helper
  was introduced;
- production code does not create instruments per invocation;
- `@opentelemetry/sdk-metrics` was added only as a development dependency for
  isolated in-memory metric validation;
- the committed lockfile continues to resolve exact shared version `0.5.0` from
  the npm registry.

The focused metric fixture proves all six accepted shared metric instruments are
present:

```text
moda.agent.invocation.duration_ms
moda.agent.invocation.operations
moda.agent.tool.duration_ms
moda.agent.tool.operations
moda.conversation.turn.duration_ms
moda.conversation.turn.operations
```

The test also proves the bounded dimension contract:

- agent and tool metrics: `outcome` only;
- conversation-turn metrics: `channel` and `outcome` only;
- `outcome` is restricted to `success|error`;
- `channel` is restricted to `whatsapp|other`.

Forty varied agent/provider/model/tool names do not create additional metric
dimensions or series labels, and the sensitive sentinel value is absent from
the collected metric representation.

The fixture observes exactly three histograms and three counters after module
load, providing evidence that instruments are module-singleton rather than
created per invocation.

Metric failure isolation is also demonstrated for both duration-histogram and
operation-counter failures: successful application values are preserved and
original application errors are rethrown unchanged by identity.

### Validation Reviewed

Accepted evidence:

- GenAI observability + metric suite: 2 files, 4 tests passed;
- affected CommerceAgent/observability/runtime suite: 4 files, 13 tests passed;
- focused metric suite passed after strengthened histogram assertions;
- TypeScript `tsc --noEmit`: passed;
- production build: passed;
- workspace doctor quick: 7 checks passed;
- `git diff --check`: passed;
- direct production-source scan confirms:
  - zero `recordMetrics: false` suppressions;
  - exactly the three canonical shared GenAI helper boundaries;
  - all three safe exception mappers retained;
  - no local GenAI metric instruments/helpers.

The repository-wide suite still contains the previously known unrelated
`recovery-routing.service.test.ts` Prisma mock omission for
`customerPhone.findMany`. No BACKGROUND-009 affected test failed.

The existing npm audit/install-script warnings were not introduced by this
bounded task and were appropriately left outside scope.

### Architecture Conformance

Conforms.

BACKGROUND-009 activates only the bounded shared operational metrics assigned to
this task. It does not redesign tracing, change BullMQ telemetry, add
token/billing metrics, configure exporters/providers, or begin gateway/system
test implementation.

### Follow-up

`ARCH-002-BACKGROUND-009` is Complete.

The ARCH-002 background observability chain is now fully Complete:

```text
BACKGROUND-005   shared runtime                         Complete
BACKGROUND-006   BullMQ trace propagation               Complete
BACKGROUND-007   bounded worker operational metrics     Complete
BACKGROUND-008   GenAI active spans                     Complete
BACKGROUND-009   bounded GenAI operational metrics      Complete
```

The background dependency contribution to `ARCH-002-GATEWAY-006` and
`ARCH-002-SYSTEM-TEST-002` is now satisfied.

Do not transition either cross-domain task to Ready from this background-only
archive. `moda_architect` must evaluate their remaining dependencies against the
current full ARCH-002 coordination documents.

