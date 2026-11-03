---
id: ARCH-052-WOOCOMMERCE-002
architecture_id: ARCH-052
title: Provide secure customer-initiated Woo checkout restoration link
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
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

# ARCH-052-WOOCOMMERCE-002: Provide secure customer-initiated Woo checkout restoration link

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** WooCommerce recovery URL creation and cart restoration are outside ARCH-052. ARCH-052 assumes `CheckoutRecovery.checkoutUrl` has already been populated by the upstream recovery system for WooCommerce, as it does for Shopify. No plugin restore-link endpoint, token, transient or customer-cart restoration is part of this initiative.

## Context

The ARCH-052 Attempt 7 architecture explicitly treats an existing customer-specific checkout URL as a **precondition**. Its creation, lifetime and customer-click restoration behaviour are out of scope. ARCH-052-BACKGROUND-008 consumes the existing URL through normal checkout recovery state.

## Scope

None. This task is withdrawn; do not edit source files or create an implementation worktree for this task.

## Out of Scope

All formerly proposed restore-link creation, proxying, token storage, new REST endpoints, link issuance and cart restoration behaviour.

## Requirements

No execution, claim, code changes, package publication or tests. Historical task ID is retained for traceability only.

## Work Items

None — superseded.

## Interfaces / Contracts

No new interface. Source of the checkout CTA is the existing `CheckoutRecovery.checkoutUrl`, consumed in BACKGROUND-008.

## Dependencies

None — superseded.

## Enables

None — superseded.

## Acceptance Criteria

None — superseded.

## Validation

None — superseded; do not run task-specific tests.

## Stop Condition

Do not claim or execute this task. Use the active ARCH-052 definitions instead.

## Implementation Notes

Superseded by ARCH-052 Attempt 7 due to the agreed existing-checkout-URL precondition. This does not claim that WooCommerce cart restoration is implemented; it is explicitly an upstream requirement outside this initiative.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

ARCH-052 receives an already-populated `CheckoutRecovery.checkoutUrl` for each supported checkout.

### Unresolved Issues

None within the retired task's scope.

### Architectural Concerns

If the upstream recovery URL prerequisite is not met, report it to `moda_architect` rather than reconstructing it under ARCH-052.

## Architect Review

### Review Status

Pending.

### Review Notes

Superseded by architectural planning; no implementation review or acceptance is claimed.

### Reviewed Files

Task definition only.

### Validation Reviewed

No implementation tests; planning supersession only.

### Architecture Conformance

Not applicable — task superseded.

### Follow-up

None — do not execute.
