---
id: ARCH-041-SYSTEM-TEST-001
architecture_id: ARCH-041
title: Certify refactored hosted API parity end-to-end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-041-API-003
  - ARCH-041-API-005
  - ARCH-041-API-007
  - ARCH-041-API-013
  - ARCH-041-API-014
enables: []
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-SYSTEM-TEST-001 — Certify refactored hosted API parity end-to-end

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** portable canonical task definition; defined but **not materialised** (no task worktree, Git branch, commit or push in this session).
- **Task state:** `pending` according to explicit dependencies in this snapshot; readiness is re-gated by the launcher before an attempt.

## Objective

Independently certify that the accepted modular API preserves established HTTP, authorization, billing and provider behaviours against a running hosted API with controlled dependencies.

## Context

This task is a terminal `moda_system_test` certification after API routing and billing internals tasks are all architect-accepted complete. It must not gate implementation or use in-process implementation-specific assertions as a substitute for black-box evidence.

## Scope

- Create or adapt a bounded black-box `moda-interact-system-test` scenario for the hosted API, using supported local service startup, disposable PostgreSQL and deterministic Woo billing provider emulation.
- Exercise live/readiness, Woo connection/auth negative cases, merchant bootstrap/store context, billing read/catalogue, recurring create/switch/cancel, recovery-credit purchase and purchase-history request routing.
- Assert statuses, bounded errors, no-store/no credential leakage, wrong method/unknown route and `GET`/`POST` path collision parity.
- Prove durable replay/no double-charge, provider definite rejection/unknown outcome and tenant isolation using database/provider evidence; include callback authentication isolation as a security negative. Verify the newly auth-owned `WooInstallationAuthenticator` still accepts and denies the same installation credentials (public routes remain outside its scope).
- Capture reproducible command, fixture lifecycle and run evidence; return results for architect review.

## Out of Scope

- Modifying API production code, implementing a new API feature, touching Woo plugin/Shopify/Background runtime, changing OpenAPI or manufacturing an external provider receipt.

## Requirements

- Validate against the **accepted** API task implementation and its new unit/integration test evidence, not against unattached snapshot expectations. `moda-interact-system-test` retains its own fixture/executor/assertion layout; it must not import or relocate `moda-interact-api/tests/`.
- Explicitly probe public health, denied installation bearer (missing/duplicate/revoked/wrong shop as supported), signed webhook and REST-read callback boundaries, while preserving the established credential-rotation semantics rather than imposing a new one.
- Execute only after API-003, API-005, API-007, API-013 and API-014 have `status: complete` (all preceding API tasks thus transitively complete).
- System-test orchestration/executors/fixtures/assertions must remain separate modules; no 300+ line catch-all scenario files.
- Use invocation-owned disposable infra and clean teardown; never rely on an existing developer database or commit secrets.
- No new API implementation feature or Source-of-Truth schema changes; defect findings return to `moda_architect` for owning API correction.

## Work Items

- [ ] Register a focused ARCH-041 black-box scenario in existing system-test framework and validate its runner/catalogue contract.
- [ ] Add disposable API/Postgres/provider fixtures, negative security/HTTP assertions and independent durable-state/provider evidence.
- [ ] Run the scenario and collect concise PASS/FAIL/blocked output with evidence paths.
- [ ] Write completion report; return for Architect review and STOP.

## Interfaces / Contracts

Black-box `moda-interact-api` HTTP/OpenAPI v1 and existing PostgreSQL billing operation/purchase state. Data-plane harness owns infrastructure; provider stub has no privileged access to hidden in-process API methods.

## Dependencies

- `ARCH-041-API-003` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-041-API-005` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-041-API-007` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-041-API-013` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-041-API-014` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

None.

## Acceptance Criteria

- [ ] Original HTTP API behaviour is unchanged across sampled connection, merchant, billing and error-path scenarios.
- [ ] Tenant isolation, auth revocation/invalid credential, bounded error/log treatment and callback auth boundary have independent proof before and after API-014, with no accidental global middleware.
- [ ] Recurring and recovery-credit idempotency/provider state/transient failure scenarios do not create duplicate operations or double charges.
- [ ] PostgreSQL state and provider interactions support recorded outcomes and fixture cleanup succeeds.
- [ ] Integrated test is reproducible and no non-system-test dependency points at it.

## Validation

- [ ] Record evidence that the new `tests/unit/**` and `tests/integration/**` suites were validated by owning API tasks, but do not treat `npm test` as executing PostgreSQL integration tests.
- [ ] `npm run lint`, `npm run typecheck`, `npm run validate:catalogue` (from the installed system-test package).
- [ ] Focused `node --test` harness tests for new fixture/executor/assertion modules.
- [ ] Run ARCH-041 black-box scenario using the existing `scripts/run-system-tests.js` runner and capture the runner command, evidence directory and result counts.
- [ ] `git diff --check` and launcher task-worktree isolation evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

The new API test-layout convention belongs **only** to `moda-interact-api`. This task follows the existing system-test modular fixture/executor/assertion/orchestration conventions and remains a terminal, independent black-box validation of accepted implementation.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not include the entire WooCommerce UI or Shopify merchant screen; this initiative is an API-internal refactor. Check existing infrastructure bootstrap helpers before adding any. If PostgreSQL/Docker is not available, mark integration validation not run/blocked rather than reporting a pass.

## Completion Report

### Status

Not Started — portable definition; no implementation attempt.

### Files Changed

None. To be recorded by the executing agent.

### Work Completed

None.

### Validation Results

Not run; source snapshot inspection is not a test run. Record exact commands, actual pass/fail/skip counts and any environment-specific blockers.

### Deviations

None.

### Assumptions

The 2026-10-16 00:01:47 uploaded ZIP is a **snapshot only**. At execution the canonical Git mainline, active task state and accepted dependencies must be rechecked; do not assume this snapshot represents the live developer worktree.

### Unresolved Issues

None at definition time. Execution-dependent blockers and newly discovered constraints must be recorded.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed or accepted; task is defined but not materialised.

### Reviewed Files

None — review will inspect the exact source diff and task/report branches.

### Validation Reviewed

Not run.

### Architecture Conformance

To be assessed against `ARCH-041`, the canonical task and actual implementation.

### Follow-up

Architect records Accepted / Changes Requested / Blocked and adjusts eligible dependencies only after review.
