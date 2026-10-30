---
id: ARCH-052-COMMERCE-003
architecture_id: ARCH-052
title: Serve authenticated private Shopify checkout and alternative-product discount proof
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
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
updated: '2026-10-30'
---

# ARCH-052-COMMERCE-003: Serve authenticated private Shopify checkout and alternative-product discount proof

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** No private Commerce discount-proof route; MCP reads the existing shop discount catalogue directly.

The pre-existing description and completion-report placeholders elsewhere in this file remain historical only. No repository code or validation is authorised by this task.

## Context

Commerce-001 and Commerce-008 own Shopify provider-specific discount proof. MCP-003 obtains product images directly using its Shopify GraphQL connection. Background never calls Commerce image endpoint.

## Scope

None. This task is withdrawn; do not start the original implementation, create new provider verification services or publish obsolete proof contracts.

## Out of Scope

- No public gateway rewrite, Node HMAC implementation, provider eligibility rule engine rewrite, extra image table or secret in Git.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Private Render networking is defense in depth, not replacement for signature, replay and exact tenant/line checks.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

None — superseded; retain this historical definition only for audit.

## Interfaces / Contracts

`POST /internal/v1/recovery/discount-proof` Shared-005 proof through private-only transport and strict same-shop authorisation. No product-image route and no WooCommerce API proxy.

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

Owning repository paths:
- `moda-interact-commerce/app/internal/v1/recovery/discount-proof/route.ts` (new)
- `moda-interact-commerce/src/commerce/discounts/` (existing evaluators from COMMERCE-001/008)
- `moda-interact-commerce/tests/` (new route/provider integration tests)

Do not add `app/internal/v1/recovery/product-image/route.ts`. The MCP service owns product read/search directly. Scope is Commerce repository plus this task report only.

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

**Architectural supersession (2026-10-30):** No private Commerce discount-proof route; MCP reads the existing shop discount catalogue directly.

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
