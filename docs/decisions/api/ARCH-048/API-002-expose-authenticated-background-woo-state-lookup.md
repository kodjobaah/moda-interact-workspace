---
id: ARCH-048-API-002
architecture_id: ARCH-048
title: Expose a shop-bound Woo current-state query to Background
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 34
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-048-API-001
enables:
  - ARCH-048-BACKGROUND-003
created: 2026-10-23
updated: 2026-10-23
---

# ARCH-048-API-002: Expose a shop-bound Woo current-state query to Background

## Architecture

- Architecture ID: `ARCH-048`.
- Canonical architecture: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.
- Coordinator: `moda_architect`.
- **Lifecycle:** portable review definition based on the 23 October 2026 workspace snapshot, **defined but not materialised**. No branch/worktree, commit, claim, implementation or acceptance is implied. Re-gate against the developer's canonical workspace before execution.

## Objective

Make the trusted Woo current-state read available to the Background recovery worker through a bounded authenticated, versioned, tenant-scoped service boundary.

## Context

The Woo activity ingress path already queues authenticated events, but Background cannot use API-held Woo REST read credentials. A state-query boundary should delegate to API-001 rather than introduce direct Woo provider calls in Background.

## Scope

- Define an internal-only, authenticated checkout-state query carrying the canonical shop ID resolved from trusted service identity and an opaque checkoutKey/linked order reference; never accept arbitrary merchant domain, customer phone, URL or Woo session ID as routing authority.
- Delegate to API-001 trusted provider-read port and return a strict versioned state/error projection, with bounded requests, concurrency, timeouts and response size.
- Reject external/unauthorised calls; protect replay/correlation secrets, ensure failures are typed and do not equate missing verification with eligibility.
- Document the actual API/Background contract, auth mechanism and local/deployment configuration, adding only the minimal approved wiring.

## Out of Scope

- WooCommerce REST credentials or plugin sessions returned to Background.
- Billing, recovery jobs or database changes.
- An anonymous/public checkout lookup or arbitrary Woo REST proxy.
- No `docs/decisions/**/_index.md` updates before the developer explicitly ends architecture reconciliation.

## Requirements

- Authenticate machine caller and enforce shop binding before resolving provider credentials; no browser cookie/admin auth substitute.
- If the existing service authentication or canonical Shared contract does not exist, return the ownership gap to architect for a separate bounded task before implementation proceeds; never invent a permissive shortcut or duplicate contracts.
- Existing API routing must support the boundary; a deployment/Gateway change, if genuinely necessary, requires a separately owned task.

## Work Items

- [ ] Implement trusted-only request handler/client contract and integration with API-001.
- [ ] Test positive and denial/unavailable cases, wrong shop, identity mismatch, replay and disabled/revoked installation.
- [ ] Document versioned consumer shape and validate existing API security/regressions.

## Interfaces / Contracts

- Required outcomes: verified `live_nonempty`, `empty`, `paid`, `cancelled`, `unpaid_order`, `not_found`, `expired`, `ambiguous`, `unavailable` with enough observation and correlation evidence to make accurate downstream decisions; normalise exact vocabulary once in the canonical contract.
- Producer: hosted API; consumer: `ARCH-048-BACKGROUND-003` and pre-send `ARCH-048-BACKGROUND-004`. Use an approved canonical runtime/validation mechanism, preferring published Shared exports when cross-repository types are required.

## Dependencies

- `ARCH-048-API-001`

## Enables

- `ARCH-048-BACKGROUND-003`

## Acceptance Criteria

- [ ] A Background caller can query only the authenticated shop and bounded checkout/order identity.
- [ ] No private credentials, raw session token, PII dump or unauthenticated route exposure.
- [ ] Transient provider errors do not become a recoverable result; response mapping stays consistent across retries.

## Validation

- [ ] API route auth/provider port and schema-version integration tests.
- [ ] Declared API lint/typecheck/build checks and `git diff --check`.

## Stop Condition

After the specified work, acceptance criteria and required validation are satisfied, record launcher-resolved **dedicated** parent/implementation task worktrees, start-of-attempt synchronization and recursive submodule evidence in the Completion Report. Change task state to `review`, return to `moda_architect` and **STOP**. Do not start an enabled task. The repo agent must not mark its own task Complete.

## Implementation Notes

This task owns transport/access, not eligibility. Record which existing service-to-service auth is used and provide test evidence; do not claim an unverified existing API-to-Background mechanism.

Respect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and `docs/developer-task-workflow.md`. Prepare through `/moda-task` or `/moda_developer_create` in the developer's actual workspace. Use service-owned existing runtime facilities; reuse `@modainteract/moda-interact-shared/logging` for new generic Node application logs, not an alternate logger. Follow the actual owning repository's declared checks; no unrelated refactors or cross-repository edits.

## Completion Report

### Status

Not Started — portable task definition; implementation execution not claimed.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run. Required validation is listed above for the future assigned executor.

### Deviations

None.

### Assumptions

The uploaded snapshot is not the current remote/branch authority. Dependencies and task paths must be rechecked on materialisation.

### Unresolved Issues

None recorded at task-definition stage beyond the review gates in the parent architecture.

### Architectural Concerns

Escalate missing cross-repository contracts, Woo guest-session read impossibility, authentication or deployment requirements to `moda_architect` before inventing a workaround.

## Architect Review

### Review Status

Pending — not yet reviewed as an implementation.

### Review Notes

Awaiting future repository implementation and evidence.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet assessed.

### Follow-up

None.
