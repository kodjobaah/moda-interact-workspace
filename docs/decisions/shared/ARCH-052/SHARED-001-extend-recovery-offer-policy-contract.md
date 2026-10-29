---
id: ARCH-052-SHARED-001
architecture_id: ARCH-052
title: Extend canonical recovery policy with selected discount identities
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-001: Extend canonical recovery policy with selected discount identities

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Publish a versioned, validated merchant-selected discount-set projection without creating a second policy schema in Shopify, API or Background.

## Context

Shared already exports `@modainteract/moda-interact-shared/recovery-policy`. The existing `EffectiveRecoveryPolicySchema` accepts one fixedShopifyDiscountId and has a FIXED single-FK invariant.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Extend `moda-interact-shared/src/recovery-policy.ts` with a sorted, unique, bounded (50) `authorisedDiscountIds` semantic projection and an explicit versioned recovery-selection snapshot parser/serializer.
- Keep `NONE`, `FIXED`, `AI_BEST_APPLICABLE` unchanged. In FIXED, allow a nonempty authorised set; retain `fixedShopifyDiscountId` as an optional compatibility anchor, never as proof of every eligible candidate.
- Represent Admin override source with one override-authorised discount ID only; do not merge it with dormant merchant selections. NONE and AI do not interpret saved checked flags as a send authorization.
- Include versioned fixtures, invalid/duplicate/oversized/wrong-source negative cases and deterministic sort across Shopify, Woo API and Background.

## Out of Scope

- No database migration, merchant UI, discount eligibility, provider call, Meta template changes or release publication within this implementation task.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- No new local divergent policy DTOs in consumer repositories. Maintain legacy parser behaviour where currently invoked while introducing a deliberate migration to the versioned contract.
- Do not change provider discount/coupon IDs into codes; contracts carry internal catalogue IDs only.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Extend and export strict schemas/types.
- [ ] Add fixtures and backwards-compatible parser/regression tests.
- [ ] Document migration and consumer-facing types.

## Interfaces / Contracts

- Canonical export: `@modainteract/moda-interact-shared/recovery-policy` with `RecoverySelectedDiscountIdsSchema` and `RecoveryOfferSelectionSnapshotSchema` (names illustrative; retain one published spelling after implementation).
- Projection: `{version:1, source:"MERCHANT"|"ADMIN_OVERRIDE", mode, authorisedDiscountIds:[...sorted internal ids]}`.

## Dependencies

None.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] FIXED multi-ID set validates; empty/duplicate/cross-source ambiguity fails; no offer is granted merely because a coupon is selected.
- [ ] AI and NONE remain representable, Shopify/Woo consumers import the same exported validator.

## Validation

- [ ] Shared unit and schema regression tests, package build/typecheck as declared.
- [ ] Snapshot fixture parity tests and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-shared/src/recovery-policy.ts`
- `moda-interact-shared/src/recovery-policy.test.ts`
- `moda-interact-shared/package.json (only if exports change)`

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
