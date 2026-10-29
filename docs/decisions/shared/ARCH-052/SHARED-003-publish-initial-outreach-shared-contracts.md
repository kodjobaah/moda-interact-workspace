---
id: ARCH-052-SHARED-003
architecture_id: ARCH-052
title: Publish accepted initial-outreach Shared contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-001
- ARCH-052-SHARED-002
- ARCH-052-SHARED-004
- ARCH-052-SHARED-005
enables:
- ARCH-052-SHOPIFY-001
- ARCH-052-API-001
- ARCH-052-BACKGROUND-001
- ARCH-052-WOOCOMMERCE-001
- ARCH-052-BACKGROUND-005
- ARCH-052-ADMIN-001
- ARCH-052-BACKGROUND-007
- ARCH-052-ADMIN-002
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
- ARCH-052-API-002
- ARCH-052-GATEWAY-001
- ARCH-052-COMMERCE-003
- ARCH-052-API-003
- ARCH-052-API-004
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-003: Publish accepted initial-outreach Shared contracts

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Publish and verify the exact accepted @modainteract/moda-interact-shared version consumed by the initial-outreach integration tasks.

## Context

Shared contracts must be accepted before publication, and consumers use the published package rather than unpublished sibling sources.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Publish exactly the four architect-accepted Shared capabilities as one version: `/recovery-policy`, `/recovery-template-bindings`, `/node/recovery-private-read-auth`, and `/recovery-offer-proof`.
- Only release/version/package metadata permitted, and registry visibility checks. Do NOT rerun already-accepted tests, builds, lint or typecheck.

## Out of Scope

- No feature source edits, test reruns, typecheck, lint, builds or consumer changes in this publication-only task.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Publish only accepted implementation content. A publication blocker requiring code modification returns to architect.
- Do not install or publish from a previous task worktree; use the launcher-prepared release worktree and real release credentials.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Check Shared-001/002/004/005 accepted Complete.
- [ ] Publish the accepted package version and verify all four subpath exports.

## Interfaces / Contracts

- One verified published `@modainteract/moda-interact-shared` version exposing four ARCH-052 subpaths.

## Dependencies

- `ARCH-052-SHARED-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-004` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-005` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-SHOPIFY-001`
- `ARCH-052-API-001`
- `ARCH-052-BACKGROUND-001`
- `ARCH-052-WOOCOMMERCE-001`
- `ARCH-052-BACKGROUND-005`
- `ARCH-052-ADMIN-001`
- `ARCH-052-BACKGROUND-007`
- `ARCH-052-ADMIN-002`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`
- `ARCH-052-API-002`
- `ARCH-052-GATEWAY-001`
- `ARCH-052-COMMERCE-003`
- `ARCH-052-API-003`
- `ARCH-052-API-004`

## Acceptance Criteria

- [ ] Exactly four required subpaths resolve from the published package, without unreconciled source edits.

## Validation

- [ ] Release-only checks (prerequisites, version, registry visibility, diff).

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json (only when release tooling changes it)`

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
