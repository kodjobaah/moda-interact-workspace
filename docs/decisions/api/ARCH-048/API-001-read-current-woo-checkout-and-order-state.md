---
id: ARCH-048-API-001
architecture_id: ARCH-048
title: Superseded — no hosted Woo checkout provider-reader extension
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-23'
updated: '2026-10-23'
---

# ARCH-048-API-001 — Superseded — no hosted Woo checkout provider-reader extension

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **proposed** definition based on the uploaded 2026-10-23 18:50 snapshot; no branch, task worktree, implementation commit, accepted review or release is claimed. Check actual canonical task state before materialisation.

## Objective

Withdraw the proposed hosted provider-read extension for Woo guest checkout/order verification.

## Context

This task depended on the now-superseded WordPress read endpoint. The approved event-driven architecture does not require Moda API to read checkout state from the merchant site.

## Scope

- Keep ordinary authenticated `/v1/woocommerce/activity` intake unchanged.

## Out of Scope

- No Moda API outbound Woo checkout/session lookup, no changes to existing product REST-read connection.

## Requirements

- No implementation authorised.

## Work Items

None — this definition is superseded and must not be executed.

## Interfaces / Contracts

- Existing Woo checkout/order capture event contracts.

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

- Do not repurpose this identifier for an unrelated new API capability.

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
