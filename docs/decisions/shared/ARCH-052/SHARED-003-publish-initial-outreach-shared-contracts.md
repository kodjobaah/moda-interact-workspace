---
id: ARCH-052-SHARED-003
architecture_id: ARCH-052
title: Publish the accepted initial-outreach contracts (including product search)
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
- ARCH-052-SHARED-002
- ARCH-052-SHARED-005
- ARCH-052-SHARED-006
- ARCH-052-SHARED-008
enables:
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
- ARCH-052-BACKGROUND-005
- ARCH-052-BACKGROUND-007
- ARCH-052-BACKGROUND-010
- ARCH-052-COMMERCE-003
- ARCH-052-COMMERCE-006
- ARCH-052-COMMERCE-008
- ARCH-052-GATEWAY-001
- ARCH-052-MCP-001
- ARCH-052-MCP-002
- ARCH-052-MCP-003
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
- ARCH-052-WOOCOMMERCE-001
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-003: Publish the accepted initial-outreach contracts (including product search)

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Publish the four architect-accepted Shared contract changes (template bindings, on-demand provider evidence, minimal outreach MCP identity, product search). This is a **publication-only gate**, with no new policy snapshot, bespoke HMAC authentication, or AI decision schema.

## Context

Shared contracts must be accepted before publication, and consumers use the published package rather than unpublished sibling sources.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Once SHARED-002, SHARED-005, SHARED-006 and SHARED-008 are architect-accepted Complete, select and publish their approved Shared package version using the repository release procedure. Make only release-specific metadata/lockfile changes permitted by existing tooling.
- Verify the exact published registry version exposes `/commerce`, `/recovery-offer-proof`, `/recovery-template-bindings` and retains existing unaffected exports; record version and registry evidence. No /node/recovery-private-read-auth export.
- Do not rerun tests, lint, builds or typechecking inside a publication-only task. Return code problems to the implementing task owner.

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

- [ ] Confirm SHARED-002/005/006/008 are all Complete with accepted Architect Reviews.
- [ ] Publish the approved version with release-metadata-only edits.
- [ ] Verify exact registry version and exports; record release evidence and absence of source changes.

## Interfaces / Contracts

Shared package `/commerce` (existing generic result, outreach context and product schemas), `/recovery-offer-proof` (targeted provider evidence), `/recovery-template-bindings` (approved template bindings). No frozen selection, agent choice or private HMAC exports.

## Dependencies

- `ARCH-052-SHARED-002` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-SHARED-005` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-SHARED-006` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-SHARED-008` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-ADMIN-001`
- `ARCH-052-ADMIN-002`
- `ARCH-052-BACKGROUND-005`
- `ARCH-052-BACKGROUND-007`
- `ARCH-052-BACKGROUND-010`
- `ARCH-052-COMMERCE-003`
- `ARCH-052-COMMERCE-006`
- `ARCH-052-COMMERCE-008`
- `ARCH-052-GATEWAY-001`
- `ARCH-052-MCP-001`
- `ARCH-052-MCP-002`
- `ARCH-052-MCP-003`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`
- `ARCH-052-WOOCOMMERCE-001`

## Acceptance Criteria

- [ ] Exactly four prerequisite implementation tasks are Complete and architect-accepted before publication.
- [ ] The approved version is available and the required exports resolve.
- [ ] Publication did not modify application behaviour or rerun accepted implementation validation.

## Validation

- [ ] Inspect accepted implementation review evidence, run the authorised release command, confirm registry visibility and diff only release metadata. No source tests/typecheck/build/lint in a publication task.

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
