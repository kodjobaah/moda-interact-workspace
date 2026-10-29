---
id: ARCH-052-DATABASE-001
architecture_id: ARCH-052
title: Persist canonical tenant-scoped selected discount sets
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
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
- ARCH-052-SHOPIFY-001
- ARCH-052-API-001
- ARCH-052-BACKGROUND-001
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-DATABASE-001: Persist canonical tenant-scoped selected discount sets

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Persist one merchant-authorised set of up to 50 discount identities per shop without conflating selection with provider availability.

## Context

ShopSettings.fixedShopifyDiscountId is a single compatibility anchor. Woo currently stores checkbox choices in ShopifyDiscount.isAvailable; Shopify uses the same field for provider availability. The existing recovery attempt has offerSnapshot but no authoritative multi-selection snapshot.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Add `ShopRecoverySelectedDiscount` in `moda-interact-database/prisma/schema.prisma` with `shopId`, `discountId`, `selectedAt`; composite primary/unique `(shopId, discountId)`, same-shop composite FK to `ShopifyDiscount`, cascading shop/discount deletion, and supporting shop selection index.
- Add `@@unique([shopId,id])` or equivalent referenceable composite key on ShopifyDiscount, plus Shop relation where needed; do not change provider-synchronisation semantics of `isAvailable`.
- Add nullable `RecoveryOutreachAttempt.authorisedDiscountIdsSnapshot Json?` for an immutable, bounded selection snapshot. Preserve `offerSnapshot`, fixedShopifyDiscountId FKs and existing constraints.
- Provide an additive migration and explicit one-time backfill: Shopify from current merchant ShopSettings FIXED anchor; Woo from its currently selected `isAvailable` coupons. Do not backfill expired Admin override into merchant selections.
- Create actual PostgreSQL migration tests for same-shop FK, duplicates, cascading cleanup, backfill and independent Shopify/Woo flag semantics.

## Out of Scope

- No Shopify/Woo settings UI, coupon sync changes, Admin override migration, application logic or outbound send changes.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Enforce shop ownership in PostgreSQL, not just application code. Wrong-shop discount IDs must be impossible to persist.
- Keep the existing one-FK setting as a compatibility projection; it is not the authority for the merchant multi-set after consumer migration.
- Do not overwrite historical attempts or prior sent-message promises. Retain positive/negative migration and rollback evidence.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Define model/relations/keys and one additive SQL migration.
- [ ] Backfill legitimate merchant selections without crossing shop/provider boundaries.
- [ ] Run real PostgreSQL constraints, backfill and migration validation.

## Interfaces / Contracts

- `ShopRecoverySelectedDiscount(shopId,discountId,selectedAt)`; `RecoveryOutreachAttempt.authorisedDiscountIdsSnapshot` as a versioned JSON array validated by Background.
- Reader/writer must have a deterministic ordering (`discountId` ascending) and maximum 50.

## Dependencies

None.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-SHOPIFY-001`
- `ARCH-052-API-001`
- `ARCH-052-BACKGROUND-001`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Two shops cannot share a selected discount link and duplicate selection fails as a conflict.
- [ ] Woo selections migrate without changing Shopify `isAvailable` provider meaning.
- [ ] Existing FIXED FK and attempt records remain valid; migration is rerunnable on a fresh database.

## Validation

- [ ] Prisma format/validate and generated-client check using repository-declared commands.
- [ ] Real PostgreSQL migration/up/down compatibility fixture and tenant FK tests.
- [ ] `git diff --check` and focused schema/index inspection.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/<arch052_selection_migration>/migration.sql`
- `moda-interact-database/tests/ (existing migration/integration harness)`

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
