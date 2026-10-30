---
id: ARCH-052-GATEWAY-001
architecture_id: ARCH-052
title: Configure private Shopify proof and direct MCP WooCommerce REST access
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-MCP-003
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-008
- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-30'
---

# ARCH-052-GATEWAY-001: Configure private Shopify proof and direct MCP WooCommerce REST access

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Configure only the existing private MCP deployable connectivity necessary for **direct Shopify GraphQL and WooCommerce REST product reads**. Do not create or route a private Commerce discount-proof service.

## Context

**Snapshot fact:** Gateway has `render.test.yaml` and `render.production.yaml`; no `render.yaml` is present in this snapshot. Both already declare private Commerce/API services and the `moda-recovery-worker` worker. Modify the files that actually exist, not an invented blueprint.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Review and configure the existing per-environment MCP outbound provider connectivity and encrypted WooCommerce credential keyring wiring in the actual Render test/production Blueprint files.
- Keep MCP private and preserve existing shop and provider security boundaries.
- Avoid new public routes, Commerce proof routes, hosted API product proxies and bespoke SHARED-004 HMAC/nonce machinery.

## Out of Scope

Commerce discount-proof HTTP endpoints; Woo coupon-proof endpoints; hosted API product proxy; new checkout restoration/capture; new Shared HMAC auth framework; application feature implementation.

## Requirements

Only update environment infrastructure when the inspected MCP runtime requires it. Keep secret values outside repository code, retain private-only ingress, and route direct provider reads from MCP. Do not configure any removed proof endpoint.

## Work Items

- [ ] Inspect real MCP runtime and Render environment files.
- [ ] Configure required direct outbound provider access and secure Woo credential environment wiring without secrets in Git.
- [ ] Confirm no private Commerce discount-proof route is introduced.
- [ ] Record minimal infrastructure changes and checks.

## Interfaces / Contracts

Existing Render environment files and private-only Commerce proof route; MCP direct Woo REST uses Shared credential keyring encryption/identity and MCP-003 secure transport. Existing checkout URL is stored in `CheckoutRecovery` and requires no Gateway route.

## Dependencies

- ARCH-052-MCP-003
- ARCH-052-SHARED-003

## Enables

- ARCH-052-BACKGROUND-008
- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Direct provider product reads from private MCP are supported without a hosted API proxy.
- [ ] No obsolete Commerce/private coupon-proof routes are added.
- [ ] Credentials remain secret and MCP ingress stays private.

## Validation

- [ ] Render Blueprint lint/validation and private/public route smoke fixtures.
- [ ] Secrets scan and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/nginx/`
- `moda-interact-gateway/haproxy/`
- `moda-interact-gateway/docs/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

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
