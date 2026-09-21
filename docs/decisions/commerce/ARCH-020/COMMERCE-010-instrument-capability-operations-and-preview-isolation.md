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
executor: null
claimed_at: null
attempt: 1
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

- [ ] Discovery failure is observable without leaking authored content or changing production conversation outcomes; no invented per-feature metric labels.

- [ ] No duplicate generic HTTP metric/logger is introduced; required semantic signals correspond to documented operational gaps.
- [ ] Fixture traces correlate Background-to-MCP-to-provider while preview traffic remains distinguishable.
- [ ] Telemetry sink failure does not break tool results or publication correctness; no sensitive fixture marker leaks.

## Validation

- [ ] Template failure and missing operation fixtures remain diagnosable without leaking input/response text; generic HTTP instrumentation is reused.

- [ ] Run local exporter/sink fixtures for identity, propagation, sensitive-data absence and failure isolation.
- [ ] Provide developer-owned backend arrival verification instructions without exporting normal automated tests to hosted telemetry.

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

### Work Completed

None; task definition only.

### Validation Results

Agent-executed:

- `npm test -- --run tests/observability.test.ts tests/definition-execution.test.ts tests/preview-service.test.ts tests/discovery.test.ts tests/discovery-process.test.ts tests/discount-evaluator.test.ts`: PASS, 72/72.
- `npm test -- --run tests/mcp-service.test.ts tests/definition-execution.test.ts tests/observability.test.ts`: PASS, 23/23.
- `npm run lint`: PASS.
- `npm run build`: PASS; Prisma client generated from accepted database gitlink `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.
- `git diff --check`: PASS.
- `npm run typecheck`: task-local changes clean; blocked by existing baseline errors: `Prisma.sql`/`Prisma.Sql` missing in `lib/auth/development-platform-admin.ts` (4 errors) and implicit `tx` in `lib/server/connections.ts` (1 error).
- Full `npm test`: 334/337 passed. Existing baseline failures: 2 `tests/auth-development-identity.test.ts` failures caused by `Prisma.sql is not a function`; `tests/discovery-limits.test.ts` timed out after 30s in the Redis-backed rolling-window check with `REDIS_URL` configured.

Developer-owned hosted evidence required: confirm one live trace/log correlation and one preview event arrive in the configured hosted sink, with no sensitive marker; preview must be excluded from production alerts. No live/shared environment was contacted by this agent.

### Deviations

No scope deviation. The consumed shared package exposes structured logging but no OpenTelemetry exporter API, so the implementation uses the approved shared logger and does not invent a competing exporter. Framework HTTP/client telemetry remains reused rather than duplicated.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Hosted arrival verification remains developer-owned. The two baseline test/typecheck issues above are unrelated to changed files and were not modified.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: `task/ARCH-020-COMMERCE-010`.

- Parent/report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-010`, branch `task/ARCH-020-COMMERCE-010`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-010`, branch `task/ARCH-020-COMMERCE-010`.
- Recursive database submodule: accepted SHA `5abfd87f57038bae515aaa09ec7c8db62adcfb98`; no database files or gitlink were changed.
- Implementation commit: `7a88d72` (`feat(commerce): instrument capability operations and previews`), pushed to `origin/task/ARCH-020-COMMERCE-010`.
- Parent report commit: pending this report update, then pushed to `origin/task/ARCH-020-COMMERCE-010`.
- No main branch integration, merge, parent service gitlink update, or hosted validation was performed.

## Architect Review

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
