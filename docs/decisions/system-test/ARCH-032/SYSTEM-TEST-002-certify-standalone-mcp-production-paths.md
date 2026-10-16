---
id: ARCH-032-SYSTEM-TEST-002
architecture_id: ARCH-032
title: Certify standalone MCP production and Studio Live Test boundaries
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-ADMIN-001
- ARCH-032-BACKGROUND-001
- ARCH-032-COMMERCE-006
- ARCH-032-GATEWAY-001
- ARCH-032-MCP-014
- ARCH-032-MCP-016
- ARCH-032-MCP-019
- ARCH-032-MCP-020
enables: []
created: '2026-10-15'
updated: '2026-10-15'
---

# ARCH-032-SYSTEM-TEST-002 — Certify standalone MCP production and Studio Live Test boundaries

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`. Coordinator: `moda_architect`.

## Objective

Independently verify real Messaging → Background → MCP and Commerce Live Test flows after the relevant implementation, platform policy and private infrastructure tasks are accepted.

## Context

The existing black-box system test exposed a real missing MCP manifest, not a fixture defect. SYSTEM-TEST-001 targets an abandoned frozen remote Studio preview model and is superseded. This task uses the accepted Local Preview / Live Test / Fixture boundaries.

## Scope

- Preserve real Messaging and Background queue path; verify `commerce://capabilities` discovery, tool listing/calling and structured result handling.
- Exercise Commerce published Live Test, zero capabilities, same-tool multi-capability mapping, grant/revision/tenant isolation, failure sanitisation and deterministic aimock use only after MCP.
- Validate mandatory execution-policy readiness and fail-closed incident behaviour and private service isolation; record reproducible evidence.

## Out of Scope

- No MCP/Background/Commerce product implementation or system-test fixture changes to mask defects.
- No production cutover or merchant credential use.

## Requirements

- System-test task is terminal; never a prerequisite for a non-test task.
- Use actual accepted task worktrees and disposable service dependencies.
- Developer manual validation may occur before invoking this Ready task.

## Work Items

- [ ] Identify accepted application, publication and infrastructure commits.
- [ ] Run real black-box scenarios with bounded local fixtures and healthy migrations.
- [ ] Preserve per-boundary evidence, failures and observable results.

## Interfaces / Contracts

- Shared Commerce published manifest and result contracts.
- MCP protocol resources/list/read and tools/list/call.
- Background grant and ordering; Commerce Live Test private MCP client.

## Dependencies

- `ARCH-032-ADMIN-001`
- `ARCH-032-BACKGROUND-001`
- `ARCH-032-COMMERCE-006`
- `ARCH-032-GATEWAY-001`
- `ARCH-032-MCP-014`
- `ARCH-032-MCP-016`
- `ARCH-032-MCP-019`
- `ARCH-032-MCP-020`

## Enables

Calculated from `depends_on` in the 2026-10-15 reconciliation metadata; dependent work is never automatically claimed.

## Acceptance Criteria

- [ ] End-to-end inbound path advances beyond manifest and invokes eligible tool path.
- [ ] No cross-shop or revoked release leakage.
- [ ] Policy failures produce expected fail-closed behaviour.
- [ ] No public MCP route or Live Test fallback.

## Validation

- [ ] Black-box system tests with disposable PostgreSQL/Redis/MCP/aimock
- [ ] Evidence for SDK initialize/resource/tool calls and denial states
- [ ] Isolation and cleanup verification

## Stop Condition

Finish the bounded task, record the evidence in the Completion Report, move to `review`, return to `moda_architect`, and STOP. Repository agents do not close their own tasks. For developer-completion tasks, explicit developer completion remains required after acceptance.

## Implementation Notes

Runs only after all listed implementation and infrastructure dependencies have status complete and architect acceptance. This task does not directly trigger Gateway cutover; attach accepted evidence to the separate developer-controlled operational approval.

## Completion Report

### Status

Not Started — portable task definition; not materialised in developer worktrees.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; do not infer passing tests or accepted implementation from this definition.

### Deviations

None.

### Assumptions

None beyond the inspected 2026-10-15 snapshot.

### Unresolved Issues

Dependent implementation tasks and canonical task-worktree evidence remain unverified.

### Architectural Concerns

No new cross-repository ownership is granted by this definition.

## Architect Review

### Review Status

Pending.

### Review Notes

No independent implementation review or acceptance recorded by this definition.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation and evidence review.

### Follow-up

Only through the canonical task lifecycle.

## 2026-10-15 — Architect dependency reconciliation

**Terminal validation:** no non-system-test task depends on or is unblocked by this task. It is invoked only after all listed implementation tasks are Complete and accepted.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-ADMIN-001`, `ARCH-032-BACKGROUND-001`, `ARCH-032-COMMERCE-006`, `ARCH-032-GATEWAY-001`, `ARCH-032-MCP-014`, `ARCH-032-MCP-016`, `ARCH-032-MCP-019`, `ARCH-032-MCP-020`. Active `enables`: None.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.
