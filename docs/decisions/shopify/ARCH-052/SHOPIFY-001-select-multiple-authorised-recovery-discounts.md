---
id: ARCH-052-SHOPIFY-001
architecture_id: ARCH-052
title: Save and display Shopify merchant-selected discount sets
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
- ARCH-052-DATABASE-001
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-001
- ARCH-052-SYSTEM-TEST-001
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHOPIFY-001: Save and display Shopify merchant-selected discount sets

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Replace Shopify’s one-discount FIXED radio flow with merchant-authorised multi-selection without changing catalogue/provider availability semantics.

## Context

`moda-interact/app/routes/app/recovery-settings/RecoverySettingsView.tsx` has one `fixedShopifyDiscountId` radio choice; Shopify discount `isAvailable` means provider availability.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Update `app/routes/app/recovery-settings/RecoverySettingsView.tsx` to show up to 50 selected discounts with accessible checkbox controls, search/pagination where available, and provider status separate from selection.
- Change `app/routes/app/settings-save/route.ts` and `app/services/recovery-policy/recovery-policy.server.ts` to load/store the canonical `ShopRecoverySelectedDiscount` set within one shop-scoped transaction, with optimistic revision/conflict handling.
- Maintain one deterministic legacy `ShopSettings.fixedShopifyDiscountId` anchor for existing readers until Background switches; do not interpret it as the whole selection.
- Preserve NONE/AI dormant selections, Admin effective-override display, existing 20-language internationalisation and merchant visibility rules.

## Out of Scope

- No mutation of Shopify `isAvailable`, provider catalogue sync, discount creation, Meta templates or Background send rules.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Do not trust browser discount IDs; read and verify ownership/valid catalogue identity inside the transaction.
- No partial persistence after a stale revision or expired/out-of-scope merchant session.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement checkbox UI and merchant read projection.
- [ ] Implement atomic shop-scoped save and deterministic anchor.
- [ ] Add UI, tenant isolation, stale-revision and provider-state regression tests.

## Interfaces / Contracts

- Use the published Shared recovery-policy selected-ID contract and DB001 join table; existing Shopify recovery settings route remains the merchant ingress.

## Dependencies

- `ARCH-052-DATABASE-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-001`
- `ARCH-052-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Shopify merchant can select multiple valid discounts, and NONE/AI do not erase saved choices.
- [ ] Shopify provider availability flags are unchanged; Admin override remains independently authoritative when active.
- [ ] Other-shop and stale-revision submissions cannot modify a selection.

## Validation

- [ ] Relevant Shopify route/service unit and real database integration tests.
- [ ] Repository-declared typecheck/test/lint and `git diff --check`.

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
