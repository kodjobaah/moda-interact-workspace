---
id: ARCH-023-BACKGROUND-004
architecture_id: ARCH-023
title: Reconcile Merchant Knowledge processing
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-BACKGROUND-003
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-GATEWAY-001
  - ARCH-023-SYSTEM-TEST-002
created: 2026-09-27
updated: 2026-09-27
---

# Reconcile Merchant Knowledge processing

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Add durable reconciliation for pending/stale Merchant Knowledge revisions so database persistence remains authoritative when queue publication or worker delivery is missed.

## Context

Shopify commits requested revisions before best-effort BullMQ publication. ARCH-023 explicitly reuses the existing Moda reconciliation approach instead of introducing a transactional outbox.

## Scope

- Scan/reconcile pending or stale latest source revisions using bounded paging/claim semantics.
- Re-enqueue deterministic process jobs when work is missing/stale.
- Do not re-enqueue terminal/non-latest revisions or duplicate active work unnecessarily.
- Integrate reconciliation into the Merchant Knowledge worker entrypoint/schedule/runtime controls consistent with existing Background patterns.

## Out of Scope

- Changing source content.
- Automatic periodic refetch of ACTIVE URLs.
- New outbox tables.

## Requirements

- Reconciliation repairs queue-loss without changing merchant-requested URL/version.
- Repeated reconciliation is idempotent.
- ACTIVE historical/current revisions are not treated as refresh requests.
- Bounded scans avoid unbounded database/Redis work.

## Work Items

- [ ] Implement reconcile query/claim/re-enqueue path.
- [ ] Add queue-loss/stale-claim/idempotency/bounded-page tests.
- [ ] Wire periodic reconcile cycle into worker entrypoint.

## Interfaces / Contracts

Consumes ARCH-023-SHARED-002 reconcile/process contracts and B3 worker service.

## Dependencies

- ARCH-023-BACKGROUND-003
- ARCH-023-SHARED-004

## Enables

- ARCH-023-GATEWAY-001
- ARCH-023-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Persisted pending latest revision eventually receives process work after simulated enqueue loss.
- [ ] Terminal/stale revisions are skipped deterministically.

## Validation

- [ ] Focused reconciliation/integration tests.
- [ ] Worker entrypoint regression tests.
- [ ] Build/typecheck/lint as declared.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

None

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

Pending.

### Follow-up

None
