---
id: ARCH-048-API-002
architecture_id: ARCH-048
title: Superseded — no Background-to-Moda-API state-query endpoint
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 34
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-23'
updated: '2026-10-23'
---

# ARCH-048-API-002 — Superseded — no Background-to-Moda-API state-query endpoint

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **proposed** definition based on the uploaded 2026-10-23 18:50 snapshot; no branch, task worktree, implementation commit, accepted review or release is claimed. Check actual canonical task state before materialisation.

## Objective

Withdraw the proposed internal HTTP current-state query from Background to Moda API.

## Context

Background already consumes authenticated events and can query the existing PostgreSQL recovery state itself. The user does not want additional WordPress checkout-reading endpoints or extra internal proxy hops.

## Scope

- Preserve existing API event acceptance and queue publication.

## Out of Scope

- No internal Background-to-API checkout state endpoint or credential passthrough.

## Requirements

- No implementation authorised.

## Work Items

None — this definition is superseded and must not be executed.

## Interfaces / Contracts

- Existing Woo `/v1/woocommerce/activity` ingress only.

## Dependencies

None

## Enables

None

## Acceptance Criteria

None — superseded. No implementation is authorised by this task.

## Validation

None — superseded. No tests, claim or feature work should be performed against this task.

## Stop Condition

After only this task's work, criteria and required validation, complete the Completion Report with the launcher-resolved dedicated parent and implementation worktree paths, isolation, start-of-attempt synchronisation and repository revision evidence. Change to `review`, return to `moda_architect` and **STOP**. Do not start dependent work. Superseded tasks must not be claimed.

## Implementation Notes

- There is no replacement ARCH-048-BACKGROUND-005 provider HTTP reader.

- Use `/moda-task` preparation with the real developer workspace before code execution. Do not treat the snapshot as a Git branch; do not edit any `docs/decisions/**/_index.md` during this architecture session. Validate actual repository scripts rather than guessing commands. Respect assigned repository and task-document ownership.

## Completion Report

### Status

Not Started — proposed portable definition only.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run by repository implementer; no task worktree or Git remote is accessible in this review package.

### Deviations

None.

### Assumptions

The latest uploaded workspace ZIP is a source snapshot, not necessarily the developer's latest task branches. The developer reports `ARCH-046-BACKGROUND-004` complete after the ZIP; verify its accepted implementation for consumer integration, without reopening it.

### Unresolved Issues

Original task design intentionally withdrawn. Refer to the parent ARCH-048 architecture.

### Architectural Concerns

No remotely callable WordPress checkout/session read route is authorised.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
