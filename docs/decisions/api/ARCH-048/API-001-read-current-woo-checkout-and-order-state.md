---
id: ARCH-048-API-001
architecture_id: ARCH-048
title: Extend trusted Woo REST read to current checkout and order state
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-048-WOOCOMMERCE-001
enables:
  - ARCH-048-API-002
created: 2026-10-23
updated: 2026-10-23
---

# ARCH-048-API-001: Extend trusted Woo REST read to current checkout and order state

## Architecture

- Architecture ID: `ARCH-048`.
- Canonical architecture: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.
- Coordinator: `moda_architect`.
- **Lifecycle:** portable review definition based on the 23 October 2026 workspace snapshot, **defined but not materialised**. No branch/worktree, commit, claim, implementation or acceptance is implied. Re-gate against the developer's canonical workspace before execution.

## Objective

Implement a narrow trusted hosted read port for the Woo plugin’s versioned current checkout/order projection, reusing existing installation-scoped REST-read authorisation and hardened HTTP transport.

## Context

`src/woocommerce/rest-read/provider-connection.service.ts` currently supports product reads only, with shop/install binding, an ACTIVE `read` grant, credential-version recheck after provider I/O, and DNS/peer/redirect protections. We must extend this owned capability without turning it into a generic proxy.

## Scope

- Add a strict provider read operation for a bounded checkout key and optional correlated order ID, using the route and versioned projection delivered by WOOCOMMERCE-001.
- Reuse validated canonical site, transport protections, active shop/platform/installation and credential state, neutral verification of rejected credentials, and post-I/O grant revalidation.
- Return a discriminated typed result distinguishing verified basket/order state from `not_found`, `expired`, `ambiguous`, `reauthorization_required`, `provider_unavailable`, `invalid_response` and permission failure.
- Add API-focused tests for positive state, Woo terminal statuses, key/order mismatch, tenant isolation, rotation, revocation, 403 handling, timeout, SSRF and response bounds.

## Out of Scope

- Public merchant/browser fetch of arbitrary checkout state.
- Maturity/consent decisions, recovery INSERT or billable outreach.
- New Woo customer/session storage tables or direct Background provider credentials.
- No `docs/decisions/**/_index.md` updates before the developer explicitly ends architecture reconciliation.

## Requirements

- Provider `404` cannot automatically mean abandoned or unpaid; preserve explicit provider state/errors.
- Never infer a valid grant from product-scope access without proving the new endpoint accepts the intended credentials.
- Do not decrypt or emit secrets in logs/responses; no unsafe redirects, user-controlled hosts or generic REST path passthrough.

## Work Items

- [ ] Reuse trusted Woo connection resolver/transport for a narrow additional operation.
- [ ] Validate/projection-map Woo response with strict identity, lifecycle and bounded fields.
- [ ] Write mocked and integration/negative security tests and preserve product-read regressions.

## Interfaces / Contracts

- Producer: `ARCH-048-WOOCOMMERCE-001` plugin-only bounded current-state endpoint.
- Consumer: `ARCH-048-API-002` authenticated Background query route, not an unscoped browser API.
- Keep any wire schema canonical; do not independently clone another repository’s shared validator if a published Shared export exists.

## Dependencies

- `ARCH-048-WOOCOMMERCE-001`

## Enables

- `ARCH-048-API-002`

## Acceptance Criteria

- [ ] Correct shop/key/linked order state can be resolved without cross-tenant leakage.
- [ ] Rotated/revoked/absent grants, unreadable or expired sessions fail closed as explicit non-eligible outcomes.
- [ ] Product-only reads remain unaffected; existing security hardening reused.

## Validation

- [ ] Focused API unit/integration tests and existing Woo REST read security/regression tests.
- [ ] Repository declared typecheck/lint/build checks for changed paths and `git diff --check`.

## Stop Condition

After the specified work, acceptance criteria and required validation are satisfied, record launcher-resolved **dedicated** parent/implementation task worktrees, start-of-attempt synchronization and recursive submodule evidence in the Completion Report. Change task state to `review`, return to `moda_architect` and **STOP**. Do not start an enabled task. The repo agent must not mark its own task Complete.

## Implementation Notes

If the plugin cannot provide a safely authenticated current-session projection, mark this task blocked and return to architect; do not fall back to trusting queued snapshots.

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
