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
status: review
priority: 190
executor: null
claimed_at: null
attempt: 1
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

- [x] Operational views correlate service and worker effects and cannot mistake preview/test traffic for production.
- [x] Observability requirements are version-controlled and no undocumented manual backend configuration is necessary.
- [x] Alert thresholds distinguish assumed initial values from measured capacity evidence.

## Validation

- [x] Run local dashboard/query/config validation with fixture signal names and environment filters.
- [x] Provide developer-owned backend validation instructions; acceptance requires recorded evidence for required hosted signals/alerts.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Ready for Review. Attempt 1 implementation is complete and locally validated.

### Files Changed

- `dashboards/commerce-operational.json`
- `alerts/commerce-operational.yaml`
- `docs/commerce-operational-runbook.md`
- `tests/fixtures/commerce-operational-signals.json`
- `tests/validate-commerce-observability.sh`

### Work Completed

Added a version-controlled Grafana dashboard with service/environment selectors,
live MCP and eligibility views, worker oldest-waiting-age view, preview view and
Background-owned evidence-refresh view. Added four C11 alert rules with explicit
production/live filters, inclusive sample floors, strictly-greater thresholds,
consecutive-duration handling for queue lag, and `NoData` states. Added the
operational runbook for unavailable service, permission/provider failures, queue
lag, evidence failures, rollback, capability disablement and preview isolation.
The evidence-refresh rule and panel are intentionally marked as Background-002
owned; until that accepted terminal event exists they remain `No data` rather
than fabricating a business signal.

### Validation Results

| Requirement | Fixture / command | Expected side effect | Result |
| --- | --- | --- | --- |
| Emitted Commerce signal names and units | `tests/fixtures/commerce-operational-signals.json`; `tests/validate-commerce-observability.sh` | Dashboard/alerts reference discovery, MCP, eligibility, preview, queue-age and refresh names; queue age is milliseconds | PASS |
| Production vs preview/environment isolation | `dashboards/commerce-operational.json`; validator | Environment selector is test/production; production alert queries require `purpose=live`; preview sample is visible only in preview panel | PASS |
| MCP denominator and threshold | `alerts/commerce-operational.yaml`; validator | Operational failure rate is `F / A > 0.05` with inclusive `A >= 20`; expected DENIED is excluded | PASS |
| Queue lag threshold and duration | alert rule plus fixture sample `121000ms` | Converted age is strictly greater than 120 seconds and must remain true for 5 minutes | PASS |
| Evidence failure threshold and ownership | alert rule, runbook and pending-owner fixture | `F / A > 0.10`, `A >= 20`, live only; missing Background signal remains No data | PASS locally; hosted signal pending |
| Configuration syntax and hygiene | `bash -n tests/validate-commerce-observability.sh`; Ruby YAML parse; `git diff --check` | Valid shell/YAML and no whitespace errors | PASS |

Exact local results: `tests/validate-commerce-observability.sh` passed with
`commerce observability configuration validation passed`; `bash -n ...` passed;
Ruby parsed `alerts/commerce-operational.yaml`; `git diff --check` passed.

### Deviations

No scope deviation. The C11 evidence-refresh signal is not emitted by the
accepted Commerce inventory; the alert documents Background-002 ownership and
does not substitute Commerce eligibility outcomes.

### Assumptions

The deployed Grafana data sources and service/resource label mapping are supplied
by the developer's environment. Dashboard JSON is provisioned with Loki and
Prometheus datasource variables and does not commit backend credentials.

### Unresolved Issues

Developer-owned hosted validation remains: provision the dashboard/alerts in the
approved Grafana environment, verify test then production arrival, capture live
Commerce and preview events, confirm preview exclusion, exercise alert boundaries
and recovery, and verify Background's terminal evidence-refresh signal. No live
deployment, backend provisioning, provider call or hosted alert evaluation was
performed by this agent.

### Architectural Concerns

The evidence-refresh alert cannot become actionable until Background emits the
accepted terminal signal named in the fixture. This is an explicit cross-repo
handoff, not an implementation of Background behavior.

### Git / VCS

Expected execution branch: `task/ARCH-020-GATEWAY-002`. Attempt: 1. Implementation
and parent report commits/pushes will be recorded here before submission. No main
integration, parent service gitlink update, live deployment or enabled-task launch
is performed.

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
