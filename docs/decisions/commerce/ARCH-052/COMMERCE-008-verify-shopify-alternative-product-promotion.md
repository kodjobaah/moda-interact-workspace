---
id: ARCH-052-COMMERCE-008
architecture_id: ARCH-052
title: Verify Shopify discounts for a specific recommended product without checkout mutation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
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
created: '2026-10-29'
updated: '2026-10-30'
---

# ARCH-052-COMMERCE-008: Verify Shopify discounts for a specific recommended product without checkout mutation

## Architecture

Architecture ID: `ARCH-052`. Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised**; no Git branch or worktree created.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** Alternative product relevance is assessed by the dedicated agent using the MCP product-search and discount-catalogue tools, without a separate Shopify proof engine.

The pre-existing description and completion-report placeholders elsewhere in this file remain historical only. No repository code or validation is authorised by this task.

## Context

COMMERCE-001 proves discounts against the original checkout. If none applies, the InitialOutreachOfferAgent may promote another product, but only when a provider-backed rule proves the offer applies to that alternative purchase; matching a category name is not proof.

## Scope

None. This task is withdrawn; do not start the original implementation, create new provider verification services or publish obsolete proof contracts.

## Out of Scope

No additional database table/column/migration, migration backfill, alternate provider proxy, customer-facing product database/cache, secret-bearing logs, unrelated architecture or other repository implementation.

## Requirements

- Only assigned repository code and this task report may be changed. Do not implement Enabled tasks.
- Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the exact launcher packet and dedicated mirrored parent/implementation worktrees. Re-read the authoritative task before claiming.
- Use `@modainteract/moda-interact-shared/logging` for new Node structured logs; record unexpected exceptions with bounded reason codes and propagate to the owning error/retry boundary. Never log credentials, complete URLs, coupon codes, raw provider payloads or customer personal data.
- Authenticate every shop/grant/call with its trusted identity, enforce provider deadlines, bounded pagination, strict response projection, customer/tenant separation and read-only provider behavior.
- This is a **pre-production breaking design**. Do not add legacy adapters/backfills or change conversation CommerceAgent lifecycle.

## Work Items

None — superseded; retain this historical definition only for audit.

## Interfaces / Contracts

Shared-005 `RecoveryDiscountProofRequestSchema.target.kind=ALTERNATIVE_PRODUCT`; existing COMMERCE-001 evaluator and COMMERCE-003 private proof endpoint. `MCP-004` is consumer; no Commerce Studio authoring.

## Dependencies

None — superseded.

## Enables

None — superseded.

## Acceptance Criteria

None — superseded; no code is to be accepted under this task.

## Validation

Not applicable; the superseded implementation must not run.

## Stop Condition

This task is superseded. Do not claim, implement, run tests, publish, merge or unblock dependants from it.

## Implementation Notes

Expected workspace-relative owned source paths (confirm paths exist in checked-out worktree before editing):

- `moda-interact-commerce/src/commerce/discounts/`
- `moda-interact-commerce/src/commerce/products/index.ts` (read existing functions only unless required to expose eligibility facts)
- `moda-interact-commerce/tests/`

## Completion Report

### Status

Not Started — portable definition; no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Confirm execution baseline in dedicated task worktree.

### Unresolved Issues

None established.

### Architectural Concerns

Return material contract/security/proof gaps to `moda_architect` without inventing a workaround.

## Architect Review

### Review Status

Pending.

### Review Notes

**Architectural supersession (2026-10-30):** Alternative product relevance is assessed by the dedicated agent using the MCP product-search and discount-catalogue tools, without a separate Shopify proof engine.

Definition only; no implementation accepted.

### Reviewed Files

Task definition and uploaded 29 October 2026 snapshot only.

### Validation Reviewed

No implementation tests yet.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through canonical task launcher only after dependencies are Complete.
