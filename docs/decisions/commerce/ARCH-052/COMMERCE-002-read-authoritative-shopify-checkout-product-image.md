---
id: ARCH-052-COMMERCE-002
architecture_id: ARCH-052
title: Read first checkout-product image from Shopify product facts
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-COMMERCE-002: Read first checkout-product image from Shopify product facts

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

**Superseded without implementation.** MCP-003 performs exact Shopify product/variant media lookup directly through existing MCP Shopify connection.

## Context

Commerce product search and variant-facts readers exist, but their selected GraphQL products currently omit image metadata. CheckoutRecovery.lineItems stores product/variant IDs without image URLs.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

No implementation. Do not claim, materialise, modify repository code or attempt publication under this task.

## Out of Scope

- No R2 upload, media DB write, Woo image sourcing, template header change or storefront cart mutation.

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

No implementation. Replacement: MCP-003 performs exact Shopify product/variant media lookup directly through existing MCP Shopify connection.

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
