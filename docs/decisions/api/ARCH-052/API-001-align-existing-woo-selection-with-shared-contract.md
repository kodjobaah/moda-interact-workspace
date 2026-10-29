---
id: ARCH-052-API-001
architecture_id: ARCH-052
title: Align existing Woo multi-select API with canonical Shared validator
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
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-API-001: Align existing Woo multi-select API with canonical Shared validator

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Retain WooCommerce multi-selection in existing ShopifyDiscount.isAvailable records; use the same published selected-ID contract as Shopify without any storage migration.

## Context

Woo `merchant/discount-offers/service.ts` already writes `isAvailable` transactionally, with 50 selected IDs and a deterministic FIXED anchor; there is no reason to move these rows to a join table.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- In `src/merchant/discount-offers/contract.ts`, replace its duplicated ID/array validation with published `RecoverySelectedDiscountIdsSchema`, retaining existing error mappings (`invalid_request`, `selection_limit_exceeded`, `selection_required`) and the exact Woo `GET/PUT /v1/merchant/discount-offers` payload `{recoveryOfferMode,selectedDiscountIds}`.
- In `src/merchant/discount-offers/service.ts` keep the authenticated principal, Shop lock, same-shop `wooRows` filters, zero/50 limit, single transaction updateMany(false)+updateMany(true), and mode/anchor update. Do **not** add/modify any Prisma model, relationship, schema migration or compatibility API.
- Ensure `isAvailable` means saved merchant checkbox regardless of provider status, expiry, current generation. Verify Woo coupon reconciliation creates unchecked rows, does not overwrite existing selections and preserves flags through ERROR/UNAVAILABLE.
- Keep active Admin override independent of merchant choices; set FIXED anchor to first ascending selected ID, null outside FIXED; preserve selected flags in NONE and AI.
- Add real PostgreSQL integration tests for two shops, stale grant rejection, simultaneous saves, Woo sync race and invalid/duplicate/oversized selected lists.

## Out of Scope

- No new selection table or data backfill, new endpoint, plugin UI change or Woo native coupon evaluator.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- This is a small alignment task, not a wholesale rewrite of already-correct Woo selection behaviour.
- Selection is never positive checkout coupon eligibility.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Adopt published Shared validator while preserving response/wire semantics.
- [ ] Prove selection flags and checkout provider status remain independent in DB tests.

## Interfaces / Contracts

- Existing Woo `GET/PUT /v1/merchant/discount-offers` schemaVersion 1, authenticated principal and Shared recovery-policy validator.

## Dependencies

- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Woo selected IDs remain in existing discount rows and behave exactly as canonical selection contract; no new schema.
- [ ] Admin override and provider unreadability do not mutate flags.

## Validation

- [ ] API contract/unit and real PostgreSQL transaction tests.
- [ ] API declared typecheck/lint/test and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-api/src/merchant/discount-offers/contract.ts`
- `moda-interact-api/src/merchant/discount-offers/service.ts`
- `moda-interact-api/tests/`

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
