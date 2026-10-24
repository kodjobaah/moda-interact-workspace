---
id: ARCH-048-WOOCOMMERCE-001
architecture_id: ARCH-048
title: Superseded — do not expose Woo checkout/order read endpoint
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-23'
updated: '2026-10-23'
---

# ARCH-048-WOOCOMMERCE-001 — Superseded — do not expose Woo checkout/order read endpoint

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **proposed** definition based on the uploaded 2026-10-23 18:50 snapshot; no branch, task worktree, implementation commit, accepted review or release is claimed. Check actual canonical task state before materialisation.

## Objective

Withdraw the proposed remotely callable WordPress endpoint for resolving guest sessions and checkout/order data.

## Context

The developer rejected expanding the attack surface of a merchant-controlled WordPress site. ARCH-048 now uses outbound Woo hooks and existing authenticated Moda event ingress. This proposal was never implemented.

## Scope

- Keep the historical decision and explicit supersession rationale.
- Use WOOCOMMERCE-002/003 for outgoing event corrections instead.

## Out of Scope

- No WordPress REST checkout/session-reading route, cart-token API, remote guest-session resolution or provider-read credential expansion.

## Requirements

- This task is superseded; it must not become Ready.

## Work Items

None — this definition is superseded and must not be executed.

## Interfaces / Contracts

- Existing authenticated outbound Woo activity route remains the approved ingress.

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

- Do not replace this with an equally broad alternative read route. Any optional locally verified outbound event requires a separate approved contract.

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
