---
id: ARCH-052-BACKGROUND-009
architecture_id: ARCH-052
title: Make Shopify catalogue and lifecycle writers preserve merchant selection
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-10-29T19:26:53Z
attempt: 1
depends_on: []
enables:
- ARCH-052-SHOPIFY-001
- ARCH-052-SYSTEM-TEST-001
created: '2026-10-29'
updated: 2026-10-29
---

# ARCH-052-BACKGROUND-009: Make Shopify catalogue and lifecycle writers preserve merchant selection

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Standardise `ShopifyDiscount.isAvailable` to mean merchant-selected, including Shopify discount refresh and subscription lifecycle transitions.

## Context

`shopify-discount-catalogue.service.ts` currently sets isAvailable=true on every upsert, false on disappearance/unavailable, and `billing-subscription-reconciliation/reinstall-reconciliation.service.ts` clears it when a contract is lost; Woo sync intentionally preserves this flag.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- In `src/services/shopify-discount-catalogue.service.ts`, set `isAvailable:false` ONLY in the `upsert.create` branch for brand-new provider discount rows. Remove `isAvailable` entirely from `upsert.update`. Never set `isAvailable` from providerStatus, syncGeneration, active scope, dates, or catalogue status.
- Delete the `shopifyDiscount.updateMany(...isAvailable:false)` calls from stale-generation reconciliation and `markCatalogueUnavailable`. Keep the existing `unavailableAt` and catalogue status changes untouched; a missing provider discount remains selected but is never eligible while unavailable.
- In `src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts`, remove only the `isAvailable:false` clearing operation in `completeReinstallWithoutContract`; retain subscription/Shop/catalogue invalidation and `unavailableAt` transitions unchanged.
- Audit every Background `shopifyDiscount` upsert/update/updateMany write in this snapshot for `isAvailable` modifications and prove that merchant selection is changed only by authenticated merchant settings APIs. Do not modify Woo coupon sync.
- Add PostgreSQL integration tests for new discount defaults false, sync does not select all, merchant choice survives full resync, disappearance, missing read scope, catalogue UNAVAILABLE and reinstall/no-contract; provider liveness still blocks positive eligibility.

## Out of Scope

- No DB migrations or schema changes, no merchant UI, no Woo API write or offer eligibility/AI implementation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- This is a prerequisite for Shopify multi-selection. Never infer a discount is authorised merely from the provider catalogue; availability fields remain separate.
- No historical backfill: development fixtures will explicitly reset only Shopify selections and fixed anchors before enabling the new feature.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Remove all Background-originated Shopify selection writes except false on first creation.
- [ ] Verify no-contract/reinstall path and provider metadata invalidation remain intact.
- [ ] Add real PostgreSQL lifecycle/concurrency regression tests.

## Interfaces / Contracts

- `ShopifyDiscount.isAvailable` means merchant selection; existing provider fields and catalogue generation retain their meanings.

## Dependencies

None.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-SHOPIFY-001`
- `ARCH-052-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] All newly synced discounts remain unchecked; selected ones survive re-sync and reinstall without becoming provider-eligible if unavailable.
- [ ] No Woo merchant checkbox state is changed by this task.

## Validation

- [ ] Shopify catalogue and reinstall service unit/integration tests; provider unavailable and sync race cases.
- [ ] Background test/build/lint according to package.json, `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/shopify-discount-catalogue.service.ts`
- `moda-interact-background/src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts`
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
