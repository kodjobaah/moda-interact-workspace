---
id: ARCH-020-COMMERCE-010
architecture_id: ARCH-020
title: Instrument capability operations and preview isolation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 140
executor:
claimed_at:
attempt: 3
depends_on:
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-009
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-002
created: 2026-09-20
updated: 2026-09-21
---

# Instrument capability operations and preview isolation

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Make Commerce capability behaviour observable through the approved shared telemetry stack.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Commerce startup instrumentation, semantic event adapters and telemetry fixtures.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [x] Include developer-resource unavailable/timeout/validation outcomes and schema/compiler availability in the existing technical signal inventory; never log document/query/input content or tool definitions. Keep discovery distinct from live MCP and preview.

- [x] Observe definition resolution/executor operation/render outcomes separately using bounded semantic events. Put version/IDs only in allowed redacted logs/traces, never metric labels or raw templates.

- [x] Inspect and reuse framework/shared HTTP, client and runtime telemetry before adding any semantic signals.
- [x] Use shared logging and the accepted Commerce service identity with explicit environment and preview purpose. No OpenTelemetry export exists in the consumed shared package, so no competing exporter was added.
- [x] Propagate Background W3C `traceparent` context and emit bounded semantic outcomes for resolution, publishing, evaluation and preview.
- [x] Redact secrets/customer data/provider payloads and keep high-cardinality identifiers out of metric labels.
- [x] Document available signal names/units/outcomes for Gateway dashboards and telemetry-failure isolation.

## Interfaces / Contracts

docs/observability/shared-logging.md and approved @modainteract/moda-interact-shared/observability exports.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C11**. These are required acceptance inputs, not optional examples.

Deliver the accepted signal inventory with actual framework/shared names, units, environment/purpose and sample fixture output. Only add missing semantic outcomes. Preview audit is redacted logging, not an unsupported CommerceAuditAction enum extension.

### Deterministic review clarification

The C11 inventory must identify counter numerator/denominator and one terminal
outcome per logical MCP request, not per span/retry. Failure-rate numerator is
transport timeout/unavailability or internal/provider operational failure; expected
DENIED/revoked/INVALID_INPUT outcomes remain requests but are not operational
errors. Evidence refresh uses one terminal outcome per refresh decision and counts
changed/missing/expired evidence or operational failure as refresh failure. Record
request-level call counts separately from provider attempts. Export local fixture
samples for success, expected denial, operational failure and refresh failure.

### Required evidence

Use local exporters and a sensitive-marker fixture; assert trace continuity, preview isolation and absent secrets/transcripts/phones. Demonstrate sink failures leave tool/publication results unchanged. Provide exact hosted arrival checks for developer evidence.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-009

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-002

## Acceptance Criteria



## Validation



Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

## Completion Report

### Status

Ready for Review.

### Files Changed

Implemented shared-logger-backed semantic telemetry, traceparent propagation, discovery/compiler/schema outcomes, definition resolution/execution/render outcomes, publication and eligibility outcomes, preview terminal outcomes, local redaction/sink-isolation fixtures, and the accepted signal inventory.

Correction checklist applied for this rework attempt:

- [x] Discovery unavailable/timeout/validation and schema/compiler availability are separate from live MCP and preview.
- [x] One terminal outcome is recorded per logical request; request counts and provider attempts are distinct fields.
- [x] Expected denial/revocation/invalid input remain non-operational outcomes; operational unavailable/error outcomes are distinguishable.
- [x] Eligibility records the four C11 outcomes and preview records completed/cancelled/denied/unknown.
- [x] Traceparent is validated and propagated into execution events; IDs are hashed or correlation-only and never metric labels.
- [x] Sensitive-marker fixture proves no prompt/provider/run content leakage; logger failures do not alter results.
- [x] A2-R1: batch, SDK protocol, invalid-input, denial, and operational terminal outcomes are classified before the single request event; refused provider reservations are excluded from `providerAttempts`.
- [x] A2-R2: fallback rendering is reported as render success while renderer overflow is reported as render error.
- [x] A2-R3: evaluator telemetry retains trusted preview/live purpose, environment, and trace/span correlation; MCP terminal events retain incoming trace correlation.
- [x] A2-R4: real MCP/publication throwing-sink fixtures prove unchanged results/commit state; evaluator eligibility is distinct from Background-002-owned C18 refresh decisions.


### Work Completed

Added `src/commerce/observability.ts`, integrated semantic events into discovery, MCP trace propagation, definition execution, publication, discount evaluation, and preview, and added `docs/observability-commerce.md` plus `tests/observability.test.ts`. Attempt 3 changed MCP terminal classification/attempt accounting, render-stage classification, policy/evaluator context propagation, and the local regression fixtures.

### Validation Results

Agent-executed:

- Focused MCP/executor/evaluator/publication/observability suites: PASS, 70/70; publication and observability sink-isolation fixtures: PASS, 30/30.
- `npm run typecheck`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS; Prisma client generated from accepted database gitlink `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.
- `git diff --check`: PASS.
- Full `npm test`: 345/347 passed. Unrelated baseline failures: `tests/discount-reader.test.ts` deadline timing expectation and `tests/discovery-limits.test.ts` Redis-backed rolling-window timeout after 30s with `REDIS_URL` configured.

Requirement-to-fixture matrix:

| Requirement | Fixture/check | Expected side effect | Result |
| --- | --- | --- | --- |
| MCP request denominator and terminal outcome | `tests/mcp-service.test.ts` real manifest/tool requests | one request event with logical call and provider-attempt counts; denial and unavailable remain distinct | PASS |
| Stage cardinality and classification | `tests/definition-execution.test.ts`, `tests/discovery.test.ts`, `tests/commerce-lifecycle.test.ts` | one terminal stage event; invalid input/denial are not operational failure; fallback render is not renderer failure | PASS |
| Trace and purpose continuity | `tests/query-execution.test.ts`, `tests/preview-service.test.ts` | incoming trace reaches provider boundary; preview retains `purpose=preview` and environment | PASS |
| Sink isolation and redaction | real MCP tool and publication lifecycle with throwing logger plus sensitive-marker fixture | business result/commit behavior unchanged and sensitive content absent | PASS locally; hosted arrival pending |
| Evidence refresh | `docs/observability-commerce.md` ownership handoff | evaluator `UNKNOWN` is not claimed as C18 refresh numerator/denominator; Background-002 owns exact-call refresh | Handoff recorded; external signal pending |

Developer-owned hosted evidence required: confirm one live trace/log correlation and one preview event arrive in the configured hosted sink, with no sensitive marker; preview must be excluded from production alerts. No live/shared environment was contacted by this agent.

### Deviations

No scope deviation. The consumed shared package exposes structured logging but no OpenTelemetry exporter API, so the implementation uses the approved shared logger and does not invent a competing exporter. Framework HTTP/client telemetry remains reused rather than duplicated.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Hosted arrival verification and the Background-002 refresh signal remain developer/integration-owned. The two full-suite failures listed above are unrelated to changed files and were not modified.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: `task/ARCH-020-COMMERCE-010`.

- Implementation commit: `a51eb69` (`fix(commerce): complete telemetry rework corrections`), pushed to `origin/task/ARCH-020-COMMERCE-010`.
- Recursive database submodule: accepted SHA `5abfd87f57038bae515aaa09ec7c8db62adcfb98`; no database files or gitlink were changed.
- No main branch integration, merge, parent service gitlink update, or hosted validation was performed.


## Architect Review

### Attempt 2 — Changes Requested (2026-09-21)

Reviewer: moda_architect. Reviewed implementation `3343c954a186bd276fe9bb577c482ab57c9fb6a6` and report `ad8e2de2ab4ef9cb21ab752c0db21d22319fe81e`; both remote heads verified, both submitted worktrees clean. **Changes Requested; Ready, Attempt 2; executor/claim null.** Preserve the implemented improvements: request-boundary telemetry now exists, duplicate execution emission is removed, discovery validates before success, early publication authorization is classified as denial, and query transport can carry trace IDs. No acceptance or downstream promotion.

#### A2-R1 — Finish MCP terminal classification and attempt accounting (A1-R1)

`src/commerce/mcp/service.ts:handle` initializes SUCCEEDED and returns the batch protocol error without changing it. A real `[]` request returned JSON-RPC -32600 but emitted SUCCEEDED in the architect reproduction. SDK-generated protocol errors likewise bypass `recordError`/`onToolResult`; a tool call defaults to DENIED even when rejected by SDK argument validation. The new finally event is therefore not consistently the actual terminal outcome. The reservation counter also increments before rejecting request 13, so it can report 13 provider attempts although the bounded provider dispatch limit is 12.

Classify every protocol/transport return before the single terminal emission, including malformed batches, invalid arguments/envelopes and SDK-generated errors. Preserve INVALID_INPUT versus DENIED/REVOKED versus operational failure; do not use HTTP 200 or the initial default as proof of success. Count successful provider reservations separately from refused reservations so the reported attempts match dispatched work. Keep the existing one-event finally behavior. Verify batch rejection and one SDK rejection at the service boundary, plus the budget-exhaustion count; this is bounded functional coverage, not an exhaustive protocol test matrix.

#### A2-R2 — Measure render-stage success independently of business status (A1-R2)

In `src/commerce/execution/executor.ts`, `definitionFailure()` still reports render ERROR whenever the returned business status is ERROR, even though it successfully attached the configured fallback. The architect reproduction supplies invalid mapped input and gets the correct INVALID_INPUT/fallback business result, but an incorrect render ERROR. Conversely, the normal path now always emits render SUCCEEDED, even when `renderDefinitionResult()` creates an INVALID_INPUT result because generated text exceeds the renderer limit.

Use a single render-outcome determination that distinguishes successful fallback rendering from an actual renderer-generated failure. Preserve the public business result and bounded fallback. Apply it to both early definitionFailure and normal execution paths; emit exactly one render record for an executed render stage. Verify early invalid-input fallback success and an actual over-limit render failure. Do not change the result status simply to make telemetry pass.

#### A2-R3 — Complete evaluator purpose/environment/correlation propagation (A1-R3)

`src/commerce/discounts/evaluator/adapter.ts` still builds `{environment: dependencies.environment ?? 'development', purpose: 'live', requestId: context.grantId}` and drops trace IDs. The changed executor/preview/query types do not fix this downstream boundary. The reproduction invokes a TEST preview evaluation with trace context; its reader-failure eligibility record is emitted as live/development with traceId undefined. This contaminates live eligibility/operational views. The terminal MCP request record also omits the incoming trace fields even though the tool executor receives them.

Carry trusted purpose and correlation through the common policy/evaluator context and derive environment from the trusted request context (with an explicit, consistent deployment fallback only where needed). Preserve the context through recommendation-to-evaluator calls and every success/failure emission. Add incoming trace correlation to the terminal MCP record. Demonstrate a preview evaluator event retains preview/TEST/correlation and a live MCP-to-executor-to-provider path retains its incoming correlation; directly injecting IDs into a standalone query port alone is not evidence of the complete chain. Reuse accepted tracing/logging; no new exporter or live endpoint is required.

#### A2-R4 — Correct refresh ownership and evidence claims (A1-R4)

The report says evidence refresh is pending another owner, while `docs/observability-commerce.md` now says discount evaluation owns refresh and claims UNKNOWN represents missing/expired/changed evidence. These are different decisions: the evaluator has no original evidence/provenance input with which to compare a refresh. C18's exact-call refresh is owned by Background's turn-local replay/provenance boundary and can replay a recommendation producer. An ordinary evaluator UNKNOWN must not be advertised as the terminal refresh-decision numerator/denominator.

Keep eligibility outcomes distinct from the final refresh decision. Document Background-002's ownership and the actual available signal/export, or explicitly record an architecture integration gap if absent; do not modify another repository or invent a replacement refresh metric in the evaluator. Clarification of A1-R4: this task must not be required to implement the external owner's signal. A truthful concrete handoff is acceptable for that external gap, while Commerce-owned fixes remain required.

Remove contradictory/duplicate inventory rows. The new publication test checks authorization denial and the MCP test uses a recording logger; neither supplies a throwing sink. Therefore the new “integrated MCP/publication fixtures” sink-isolation PASS is unsupported. Supply the previously requested small real tool/publication fixture with a throwing sink and sensitive markers, assert unchanged results/commit state and absent sensitive output, then record its actual command/result. Keep framework signal availability honest rather than asserting unnamed framework signals have been verified. Hosted arrival remains developer-owned; do not promote pending checks to PASS.

#### Architect verification

Reran the submitted six focused service files: **106/106 passed**. Temporary harness `/tmp/c010-a2-review/review.test.ts`, importing actual submitted services, ran three targeted assertions: **3 failed**, confirming batch success misclassification, lost preview/environment/trace context, and fallback render misclassification. The failures above are the basis of this decision; the reported known Redis timeout and unrun hosted arrival are not blockers for this review. Typecheck/lint/build results were reviewed from submission without redundant reruns. No implementation files or main branch changed. No dependent is promoted; preserve the developer-owned final manual system-test gate.

### Attempt 1 — Changes Requested (2026-09-21)

Reviewer: moda_architect. Reviewed implementation `7a88d721d2b9c9a912b0886e2dc4544466205e38` and parent report `41d662e20815d4629d4824027de46746e3fda6aa` (including the local completion-checkbox follow-up to pushed report `baae4d96`). Decision: **Changes Requested; Ready, Attempt 1; executor and claim null**. No acceptance, implementation change, or main integration. Corrections concern observable functionality, not exhaustive test coverage.

#### A1-R1 — Emit the actual MCP request signal

`src/commerce/observability.ts` defines `request()`, but production source never calls it. `src/commerce/mcp/service.ts` only parses trace context; neither successful manifest/tool calls nor denied/revoked/unavailable requests emit the documented terminal request event. Consequently the documented request denominator, operational-failure numerator and provider-attempt counts do not exist at the service boundary.

Add a telemetry dependency at the MCP service boundary and emit exactly one bounded terminal record for each logical request, including early rejection and error paths. Capture the final semantic outcome rather than assuming HTTP 200 means success. Preserve expected DENIED, REVOKED and INVALID_INPUT as non-operational outcomes. Populate logical-call and provider-attempt counts from their real owners; do not infer attempts from spans or emit a second generic HTTP metric. Make the dependency usable by the backend composition owner without requiring this task to complete COMMERCE-013. Verify actual manifest/tool success, expected denial and operational failure using a local sink; assert cardinality and counts, rather than invoking `telemetry.request()` directly.

#### A1-R2 — Correct stage cardinality and failure classification

In `src/commerce/execution/executor.ts`, a thrown provider error emits an execution outcome in the catch and again after it. Render outcome is inferred from the returned business result's ERROR status, so successfully rendering an unavailable fallback is reported as a renderer failure. In `lib/discovery/service.ts`, search emits SUCCEEDED before validating returned titles/URLs; rejected provider output then emits UNAVAILABLE as well. Invalid search/document input is also classified as upstream unavailability. In `src/commerce/publication/lifecycle.ts`, command validation and first authorization run outside the telemetry catch, while an authorization failure inside the transaction is mapped to ERROR.

Move terminal emission after validation/final classification and emit once per performed stage/operation. Distinguish successful fallback rendering from actual rendering failure. Keep invalid input and expected authorization failures out of operational failures, including early publication rejection. Preserve original return values, thrown domain errors and transaction behavior. Add focused service-level regressions for a thrown executor provider failure, invalid discovery output/input, and early publication denial; no broad coverage expansion is requested.

#### A1-R3 — Carry correlation and purpose through real boundaries

MCP passes parsed trace IDs into the executor, but `src/commerce/query/index.ts` constructs the provider request with only content-type and no propagated trace context; there is no local Background-to-MCP-to-provider continuity fixture. The eligibility adapter drops trace fields and defaults environment to development, while executor/evaluator hard-code purpose live. `PreviewService.log()` only emits COMPLETED/CANCELLED/UNKNOWN, leaving the promised DENIED preview signal without an emission path.

Carry a trusted execution telemetry context (environment, purpose, correlation) through query and policy adapters and their transport boundary, reusing existing framework/shared tracing when available. Preserve preview purpose through reused execution/evaluation paths; do not label preview work live. Emit a bounded preview denial at its actual decision boundary without double-counting a run terminal. Demonstrate an incoming traceparent reaching a synthetic provider boundary and a preview execution retaining preview purpose/environment in its domain records. This requires local fixtures, not hosted credentials or a new exporter.

#### A1-R4 — Make the evidence and inventory match implementation

`tests/observability.test.ts` exercises emitter methods directly; its throwing-logger test does not execute a tool or publication. The inventory nevertheless marks service-level sink isolation and other integrated requirements PASS. Correct the report/checklists and `docs/observability-commerce.md` to distinguish emitted service signals from helper-only samples and pending composition/deployment evidence. List actual available framework/shared signals (or explicitly state what was inspected and absent), and identify the concrete evidence-refresh owner/signal and its success/failure/count semantics instead of “when available.” Supply the required local refresh-failure sample from the owning boundary without modifying another repository.

Use a small local fixture that passes sensitive markers through real tool/publication inputs and a throwing sink, confirming unchanged business results/commit behavior and absence of sensitive data in captured records. This is bounded evidence for the task's explicit isolation contract, not a request for exhaustive tests. Hosted arrival remains developer-owned.

#### Validation and scope

Architect reran `npm test -- tests/mcp-service.test.ts tests/definition-execution.test.ts tests/observability.test.ts`: **23/23 passed**. Source inspection confirms the missing request caller, missing provider trace propagation, hard-coded purpose and incorrect outcome paths. Temporary harness `/tmp/c010-a1-review/review.test.ts` (using the repository server-only alias) ran two service-level assertions: **both failed**, confirming two execution records for one thrown provider error and `[SUCCEEDED, UNAVAILABLE]` for rejected discovery output. The harness imports the submitted services; no implementation files were edited. Existing reported repository-wide typecheck/full-suite baseline failures are not reasons for this decision. No dependent is promoted until COMMERCE-010 is accepted. Preserve developer-owned live validation and the final manual system-test gate.

### Original pending review placeholder (historical)

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.


## Architect readiness reconciliation — COMMERCE-007 acceptance — 2026-09-21

Promoted **Ready**, Attempt 0 retained, executor/claimed_at null. COMMERCE-004/007/009 are architect-accepted Complete, including COMMERCE-007 Attempt 7 at `e08b896`. All explicit prerequisites are satisfied. Normal preparation owns synchronization and claim and must consume actual accepted source. No automatic launch, implementation change, main integration or gitlink update.
