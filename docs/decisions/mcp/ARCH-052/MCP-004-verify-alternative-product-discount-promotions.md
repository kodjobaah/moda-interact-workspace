---
id: ARCH-052-MCP-004
architecture_id: ARCH-052
title: Verify alternate product promotions using existing MCP provider proof
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-30'
---

# ARCH-052-MCP-004: Verify alternate product promotions using existing MCP provider proof

## Architecture

Architecture ID: `ARCH-052`. Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised**; no Git branch or worktree created.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** No separate alternative-product discount-proof adapter; the dedicated agent combines existing MCP discount-catalogue and product-search results.

The pre-existing description and completion-report placeholders elsewhere in this file remain historical only. No repository code or validation is authorised by this task.

## Context

After checkout discount matching fails, the InitialOutreachOfferAgent should search for other merchant promotions; a coupon code applying to a different product is not evidence that the abandoned checkout is discounted.

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

Built-in MCP `commerce_evaluate_discount` target `ALTERNATIVE_PRODUCT` (SHARED-005); Shared-005 alternative-product provider evidence (inside existing generic MCP result envelope); WooCommerce-001 native proof and COMMERCE-008 Shopify proof; no new published tool or Commerce Studio authoring.

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

- `moda-interact-mcp/src/execution/policy/discount-tool-executor.ts` (from MCP-002)
- `moda-interact-mcp/src/execution/policy/alternative-product-proof.ts` (new)
- `moda-interact-mcp/src/connections/woocommerce/provider.ts`
- `moda-interact-mcp/src/runtime/service-ports.ts`
- `moda-interact-mcp/tests/unit/execution/policy/`

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

**Architectural supersession (2026-10-30):** No separate alternative-product discount-proof adapter; the dedicated agent combines existing MCP discount-catalogue and product-search results.

Definition only; no implementation accepted.

### Reviewed Files

Task definition and uploaded 29 October 2026 snapshot only.

### Validation Reviewed

No implementation tests yet.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through canonical task launcher only after dependencies are Complete.
