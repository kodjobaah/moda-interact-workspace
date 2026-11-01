---
id: ARCH-052-SHARED-004
architecture_id: ARCH-052
title: Define signed private recovery product-read request authentication
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-004: Define signed private recovery product-read request authentication

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** The bespoke Shared HMAC signer/nonce/replay contract for private service calls is not required by the agreed private-network trust model. Replacement: Private-only Commerce routing with strict tenant/recovery checks.

## Context

COMMERCE-003 implements one private Shopify provider eligibility route. Woo checkout URL generation is not an ARCH-052 capability: API-004 and WOOCOMMERCE-002 are superseded. The standalone MCP runtime performs Woo product search and Woo native coupon proof directly against the shop's Woo REST API using encrypted existing grants, so no product-image or Woo coupon-proof route is needed inside Moda API.

## Scope

None. This task is withdrawn; no files may be edited under this task.

## Out of Scope

- No service credentials in shared package; no API route, no gateway ingress, no exposure to browser-safe entrypoints, no merchant/provider data.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

No execution, claim, code changes, package publication or test work. Historical task retained for traceability.

## Work Items

None — superseded.

## Interfaces / Contracts

No new interface. Private-only Commerce routing with strict tenant/recovery checks.

## Dependencies

None — superseded.

## Enables

None — superseded.

## Acceptance Criteria

None — superseded.

## Validation

None — superseded; do not run task-specific tests.

## Stop Condition

Do not claim or execute this task. The developer must use the active replacement tasks.

## Implementation Notes

Task intentionally withdrawn during ARCH-052 Attempt 6 review. The bespoke Shared HMAC signer/nonce/replay contract for private service calls is not required by the agreed private-network trust model.

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
