---
id: ARCH-020-GATEWAY-002
architecture_id: ARCH-020
title: Add Commerce operational dashboards and alerts
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 190
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-010
  - ARCH-020-BACKGROUND-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-22
---

# Add Commerce operational dashboards and alerts

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Expose actionable Commerce/MCP health using existing observability infrastructure.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Gateway-owned dashboard/alert/OTLP configuration and operational runbook.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [ ] Use accepted signal inventory to add MCP error/latency, eligibility outcomes, provider throttling and conversation-lag views.
- [ ] Enforce explicit environment and production-versus-preview filters; avoid duplicating framework metrics.
- [ ] Configure actionable alerts for service unavailability, queue lag and systematic evidence/permission failures with documented thresholds.
- [ ] Document triage for release rollback, capability disable, provider failure and preview cost without secret/customer exposure.

## Interfaces / Contracts

COMMERCE-010/Background semantic signals plus existing HTTP/client/runtime instrumentation.

### Implementation guidance

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C11**. These are required acceptance inputs, not optional examples.

Deliver version-controlled dashboards/alerts using the accepted actual signal inventory and C11 initial numeric thresholds/sample floors. Include no-data state and production/preview/environment filters. Add runbook steps for unavailable service, permission denials, unknown routing sends and evidence failures.

### Deterministic review clarification

Use the accepted COMMERCE-010 inventory and exact C11 outcome denominators.
Evaluate rolling windows once per minute, separately by service/environment and
purpose=live. Threshold comparisons are strictly greater than the stated value;
minimum sample counts are inclusive. Readiness requires consecutive failures for
2 minutes; oldest pending age must exceed120 seconds continuously for5 minutes.
No samples render No data and do not trigger a failure-rate alert. Test boundary
values, low samples, recovery, preview exclusion and missing telemetry separately;
missing telemetry is observable, not fabricated success or a business failure.

### Required evidence

Static fixtures validate each query references emitted names/units and each alert excludes preview with correct sample floor/duration. Required deployed arrival/alert evidence is recorded by the developer; do not claim config syntax proves live arrival.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-010
- ARCH-020-BACKGROUND-002

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Operational views correlate service and worker effects and cannot mistake preview/test traffic for production.
- [ ] Observability requirements are version-controlled and no undocumented manual backend configuration is necessary.
- [ ] Alert thresholds distinguish assumed initial values from measured capacity evidence.

## Validation

- [ ] Run local dashboard/query/config validation with fixture signal names and environment filters.
- [ ] Provide developer-owned backend validation instructions; acceptance requires recorded evidence for required hosted signals/alerts.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Not Started.

### Files Changed

None; implementation has not started.

### Work Completed

None; task definition only.

### Validation Results

Not run. At execution, distinguish agent checks from exact developer validation required.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

See parent architecture review assumptions; no implementation evidence asserted.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-GATEWAY-002. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
