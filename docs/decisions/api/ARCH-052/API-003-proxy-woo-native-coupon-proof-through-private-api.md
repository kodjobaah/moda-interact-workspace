---
id: ARCH-052-API-003
architecture_id: ARCH-052
title: Expose authenticated private Woo discount-proof proxy with existing Woo provider grant
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-API-003: Expose authenticated private Woo discount-proof proxy with existing Woo provider grant

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

**Superseded without implementation.** MCP-002/003 call the WooCommerce plugin coupon proof using the same MCP-owned secure, read-only Woo REST connection; no API broker.

## Context

WooCommerce-001 owns provider-local WC_Discounts rule evaluation. Background cannot use an unprotected plugin endpoint or provider credentials; hosted API owns Woo read grants and is the only service that can authenticate the merchant installation.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

No implementation. Do not claim, materialise, modify repository code or attempt publication under this task.

## Out of Scope

- No Woo coupon rule reimplementation in hosted API, no public reverse proxy, no persistence schema, no merchant coupon selection edits.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

The replacement tasks and parent architecture are authoritative. Historical wording in this superseded task is retained solely for audit; it must not govern an implementation.

## Work Items

- [x] Marked superseded in the architecture plan. No code executed.

## Interfaces / Contracts

None — see replacement tasks.

## Dependencies

None — task is superseded.

## Enables

None — task is superseded.

## Acceptance Criteria

- [x] Superseded without implementation. The replacement tasks are explicitly identified.

## Validation

Not applicable; no implementation permitted.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

No implementation. Replacement: MCP-002/003 call the WooCommerce plugin coupon proof using the same MCP-owned secure, read-only Woo REST connection; no API broker.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
