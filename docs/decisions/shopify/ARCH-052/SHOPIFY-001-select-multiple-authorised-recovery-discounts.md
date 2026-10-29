---
id: ARCH-052-SHOPIFY-001
architecture_id: ARCH-052
title: Make Shopify merchant discount selection match WooCommerce checkboxes
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-BACKGROUND-009
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-001
- ARCH-052-SYSTEM-TEST-001
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHOPIFY-001: Make Shopify merchant discount selection match WooCommerce checkboxes

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Replace the Shopify one-radio FIXED discount UI with 0..50 merchant-selected discounts persisted as `ShopifyDiscount.isAvailable` under one locked transaction.

## Context

Shopify `RecoverySettingsView.tsx` has one `fixedShopifyDiscountId` radio control; `recovery-policy.server.ts` previously used that anchor as full authority. Woo has an established atomic multi-select save using the same discount table. BG009 first stops Shopify sync changing the selection flag.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- In `app/routes/app/recovery-settings/RecoverySettingsView.tsx` replace single radio with accessible checkbox list; show selected state from `ShopifyDiscount.isAvailable` for the same shop, independent of provider status. Keep NONE/FIXED/AI mode chooser, notify checkbox and existing language/translation. Permit at most 50 choices, show selected count and prevent silent trimming.
- Change `app/routes/app/settings-save/route.ts` to accept exactly one JSON string field `selectedDiscountIds` when intent=`recovery`, parsed as array using published `RecoverySelectedDiscountIdsSchema`; remove acceptance of `fixedShopifyDiscountId` as merchant-submitted authority. Reject unknown fields/duplicate form entries, malformed JSON and payload >8192 bytes (400); >50 selections (422); FIXED with empty set (422).
- In `app/services/recovery-policy/recovery-policy.server.ts`, use one `client.$transaction` and existing `lockSettingsShop(tx, shopId)`; check `settings.updatedAt` against submitted revision **before writes**; if mismatch return 409, not partial save. Validate every selected ID references an existing discount row for that exact Shopify `shopId`, regardless of provider catalogue CURRENT/ERROR status or current checkout eligibility. Allow retaining previously selected but currently unavailable discounts as dormant selections; Background excludes them from sendable offers until independently re-verified.
- Inside the same transaction: `shopifyDiscount.updateMany({where:{shopId,isAvailable:true},data:{isAvailable:false}})` then `shopifyDiscount.updateMany({where:{shopId,id:{in:sortedIds}},data:{isAvailable:true}})` and assert affected count equals requested IDs; update ShopSettings `recoveryOfferMode`, existing timing/notification prefs, and `fixedShopifyDiscountId` to `sortedIds[0]` iff FIXED, otherwise null. Never write availability/providerStatus/unavailableAt.
- Return selected IDs and effective source in settings loader, maintain Admin override as independent effective policy (never merge merchant options), and use provider status/time/generation rather than isAvailable to display catalogue availability.
- Write tests proving two shops cannot change one another, re-saves are idempotent, concurrent stale revision 409, NEW sync items remain unchecked, NONE/AI preserve dormant flags, and unavailable formerly selected discount can be deselected.

## Out of Scope

- No DB model/table/column changes, no provider coupon mutations, no template/Background send code, no legacy single-radio compatibility.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Do not trust browser discount IDs; read and verify ownership/valid catalogue identity inside the transaction.
- No partial persistence after a stale revision or expired/out-of-scope merchant session.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement checkbox form and strictly validated selected-ID request.
- [ ] Implement atomic selected-flag replacement under Shop lock and revision compare.
- [ ] Add real database races and UI tests, preserving override independent view.

## Interfaces / Contracts

- Form `intent=recovery`, `selectedDiscountIds` JSON array, `recoveryOfferMode`, existing other settings and revision; exactly one selection authority `ShopifyDiscount.isAvailable`.
- Existing `fixedShopifyDiscountId` remains deterministic first-sorted anchor solely to satisfy existing effective-policy schema; never treat as full selected set.

## Dependencies

- `ARCH-052-BACKGROUND-009` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-001`
- `ARCH-052-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Shopify and Woo both persist multiple selection flags using same existing model; new Shopify discounts never automatically become selected.
- [ ] Modes NONE/AI leave selected flags intact; switching back to FIXED reuses the saved set without using unavailable discounts as offers.
- [ ] No cross-tenant/partial updates or unverified provider eligibility claims.

## Validation

- [ ] Shopify settings route/service unit tests and real PostgreSQL transaction tests, including sync race.
- [ ] Shopify declared typecheck/build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact/app/routes/app/recovery-settings/RecoverySettingsView.tsx`
- `moda-interact/app/routes/app/settings-save/route.ts`
- `moda-interact/app/services/recovery-policy/recovery-policy.server.ts`
- `moda-interact/tests/`

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
