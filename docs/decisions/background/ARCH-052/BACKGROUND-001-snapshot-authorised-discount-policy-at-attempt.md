---
id: ARCH-052-BACKGROUND-001
architecture_id: ARCH-052
title: Freeze effective selected-discount policy at initial attempt creation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-DATABASE-001
- ARCH-052-SHARED-003
- ARCH-052-SHOPIFY-001
- ARCH-052-API-001
enables:
- ARCH-052-BACKGROUND-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-001: Freeze effective selected-discount policy at initial attempt creation

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Resolve merchant versus Admin override selection and persist the immutable authorised set for each INITIAL outreach attempt.

## Context

`src/services/recovery-policy.service.ts` currently resolves one fixedShopifyDiscountId. `RecoveryOutreachAttempt` already snapshots mode/anchor/offer but not multiple authorised IDs.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Update `src/services/recovery-policy.service.ts` and initial-attempt creation in `src/services/recovery-outreach-attempt.service.ts` to read the correct merchant selected set and the independently scoped Admin override.
- Write `authorisedDiscountIdsSnapshot` with schema version, source and sorted IDs atomically with attempt creation; keep existing configuredOfferMode, fixed FK, offerSnapshot and credit lifecycle unchanged.
- On retry/recovery replay load the frozen attempt set, not mutable current selected checkboxes; do not retroactively change a sent or pending attempt.
- Emit bounded Shared logger diagnostics for invalid/missing policy snapshots and safely return NO_OFFER where authorisation is not proven.

## Out of Scope

- No candidate discount eligibility, AI invocation, Meta template selection or merchant preference mutation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Admin override FIXED authorises its one saved ID only; dormant merchant FIXED choices must not leak into override.
- Retries of the same attempt use the same selection source/identities even after settings changes.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement tenant-scoped effective policy source reader.
- [ ] Persist/replay immutable selection snapshot with attempt transaction.
- [ ] Add PostgreSQL integration fixtures for selection and overwrite races.

## Interfaces / Contracts

- DB001 `RecoveryOutreachAttempt.authorisedDiscountIdsSnapshot` validated by Shared001. `RecoveryOfferPolicy.authorisedDiscountIds` is read from the frozen snapshot.

## Dependencies

- `ARCH-052-DATABASE-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHOPIFY-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-API-001` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-002`

## Acceptance Criteria

- [ ] Repeated jobs and concurrent settings changes cannot broaden authorised IDs.
- [ ] No fake Woo anchor is treated as a selected discount.
- [ ] Existing follow-up promise and credit-admission behaviour is preserved.

## Validation

- [ ] Focused Background policy/attempt unit and PostgreSQL integration tests.
- [ ] Background build, relevant lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-policy.service.ts`
- `moda-interact-background/src/services/recovery-outreach-attempt.service.ts`
- `moda-interact-background/tests/integration/`

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
