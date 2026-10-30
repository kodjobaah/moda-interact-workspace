---
id: ARCH-052-BACKGROUND-005
architecture_id: ARCH-052
title: Bind deterministic basket summary and merchant category for initial outreach
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 35
executor: codex
claimed_at: 2026-10-30T15:59:52Z
attempt: 1
depends_on:
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-008
created: '2026-10-29'
updated: 2026-10-30
---

# ARCH-052-BACKGROUND-005: Bind deterministic basket summary and merchant category for initial outreach

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Render safe customer-facing `checkout.itemsSummary`, verified shop display name and existing `shop.categoryName` from saved recovery facts.

## Context

CheckoutRecovery.lineItems contains titles and quantities for both providers. `automated-recovery-template.service.ts` currently passes `shop.domain` as shopName, and ARCH-047 resolver has no checkout-item summary semantic key.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Add a bounded, locale-aware but deterministic item-summary formatter for saved `CheckoutRecovery.lineItems` (titles, variant, quantity, a small number of items and “and N more” suffix). No AI needed.
- Extend the existing `recovery-template-preparation/` variable resolver to bind the Shared `checkout.itemsSummary` key with safe length, Unicode/control, Meta placeholder and output-sanitisation checks.
- Resolve shop.name from verified brand/display configuration where available, not blindly from domain; preserve safe branded-domain fallback.
- Reuse existing `shop.categoryName` scoped/translated category binding; on missing category/translation require a separate approved no-category template or typed fallback, never invent category text.
- Produce fixture evidence for Shopify/Woo line-item formats, absent/invalid product titles, multiple quantities, locale, truncation and tenant isolation.

## Out of Scope

- No new category taxonomy reader/translation task, product photo fetch, AI wording, Meta AST compilation or discount evaluation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Basket description and shop category come from persisted trusted state, not AI-generated marketing prose. Category uses existing `shop.categoryName`; actual product category facts for AI come from MCP `commerce_search_products` and `commerce_get_product` when available.
- Follow task launcher and dedicated worktrees, Shared logger, no PII/credentials in logs and no provider cart mutations.

## Work Items

- [ ] Create summary formatter with bounded fixtures.
- [ ] Connect new semantic key and approved merchant brand fallback in Background preparer.
- [ ] Unit and DB-backed cross-tenant tests.

## Interfaces / Contracts

- Shared `/recovery-template-bindings` `checkout.itemsSummary`; `RecoveryTemplatePreparationInput` extends with shop-scoped trusted checkout summary.

## Dependencies

- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-BACKGROUND-008`

## Acceptance Criteria

- [ ] A checkout with shoes and a water bottle renders a readable deterministic item summary.
- [ ] Missing or malformed items/category cannot make an unapproved placeholder/value; approved generic fallback works.

## Validation

- [ ] Formatter property/negative tests, frozen-binding compatibility and Background integration.
- [ ] Background build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-template-preparation/recovery-template-brand.ts`
- `moda-interact-background/src/services/recovery-template-preparation/recovery-template.types.ts`
- `moda-interact-background/src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `moda-interact-background/tests/`

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
