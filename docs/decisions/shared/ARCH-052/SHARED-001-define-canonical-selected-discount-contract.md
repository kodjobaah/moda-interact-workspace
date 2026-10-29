---
id: ARCH-052-SHARED-001
architecture_id: ARCH-052
title: Define one shared merchant-selection and immutable-attempt snapshot contract
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

# ARCH-052-SHARED-001: Define one shared merchant-selection and immutable-attempt snapshot contract

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Define the exact 0..50 merchant discount selection semantics and a version-one frozen outreach policy snapshot, without any Prisma changes.

## Context

Both providers store discount rows in shopify.ShopifyDiscount. Woo already writes isAvailable as the merchant checkbox. Shopify writes isAvailable as provider health; ARCH-052-BACKGROUND-009 corrects that. Existing Shared EffectiveRecoveryPolicySchema still requires one fixedShopifyDiscountId when mode=FIXED, so the first sorted selected ID remains a non-authoritative single-ID projection.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Modify `moda-interact-shared/src/recovery-policy.ts` and tests; export strict `RecoverySelectedDiscountIdsSchema` for an array of 0..50 unique IDs trimmed and sorted ASCII ascending; IDs `[A-Za-z0-9_-]{1,128}`; reject duplicate IDs, control chars, >50 and unknown object keys.
- Export `RecoveryOfferSelectionSnapshotSchema` and `parseRecoveryOfferSelectionSnapshot`. Exact existing-column JSON: `{ contract:"moda.recovery.offer-selection.v1", source:"MERCHANT"|"ADMIN_OVERRIDE", recoveryOfferMode:"NONE"|"FIXED"|"AI_BEST_APPLICABLE", authorisedDiscountIds:string[], sentOffer:null|{kind:"NO_OFFER"}|{kind:"CODE_OFFER"|"AUTOMATIC_OFFER",providerDiscountId:string,code:string|null} }`. All keys required; initial attempt always has `sentOffer:null` until confirmed provider send. Reject unknown fields. FIXED merchant 1..50; NONE/AI `[]`; ADMIN_OVERRIDE+FIXED exactly one ID.
- Permission fields in `offerSnapshot` MUST be immutable after initial INSERT. Only a single compare-and-set from `sentOffer:null` to a verified sent result is permitted after provider send confirmation. `NO_OFFER` is the exact sent no-offer template; CODE/AUTOMATIC values come only from provider-verified resolved offer used in the actual Meta request. Never treat selected discount as already promised.
- Keep existing `EffectiveRecoveryPolicySchema` unchanged for callers requiring `fixedShopifyDiscountId` in FIXED mode: project first ascending authorised ID as non-authoritative anchor. `ShopifyDiscount.isAvailable` is now merchant checkbox ONLY for both providers.
- Export parser and typed contract through published `/recovery-policy`; tests for canonical sort, duplicate IDs, all mode/source combinations, correct sentOffer variants, immutable permission diff detection and unknown/old JSON rejection.

## Out of Scope

- No new database tables, columns, Prisma migrations, backfill or legacy snapshot parser. No merchant settings, provider API, template or send implementation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- No new DB table, column, Prisma migration, historical snapshot parser, backfill or old behaviour adapter.
- Offer-selection authorisation and the actually sent offer have distinct required fields inside the existing snapshot JSON.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement four named Shared exports and strict invariants.
- [ ] Add valid/invalid cross-platform vectors, Admin-override and canonical sort tests.

## Interfaces / Contracts

- Published `RecoverySelectedDiscountIdsSchema`, `RecoveryOfferSelectionSnapshotSchema`, parser and type. JSON contract above is authoritative for Background/Shared tests.

## Dependencies

None.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] Both platforms agree on existing-row checkbox semantics and strict frozen snapshot; no single-ID fallback grants permission.
- [ ] Actual sent-offer value cannot be inferred merely from the choice list.

## Validation

- [ ] Run Shared declared unit tests including new recovery selection fixtures.
- [ ] Shared package build/typecheck and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-shared/src/recovery-policy.ts`
- `moda-interact-shared/src/recovery-policy.test.ts`

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
