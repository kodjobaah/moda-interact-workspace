---
id: ARCH-052-SYSTEM-TEST-002
architecture_id: ARCH-052
title: Certify Woo initial outreach, native coupon proof and secure cart return
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-BACKGROUND-008
- ARCH-052-API-001
- ARCH-052-WOOCOMMERCE-001
- ARCH-052-WOOCOMMERCE-002
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
- ARCH-052-DATABASE-001
- ARCH-052-DATABASE-002
enables: []
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SYSTEM-TEST-002: Certify Woo initial outreach, native coupon proof and secure cart return

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Independently certify WooCommerce initial outreach across selection modes and customer-tapped checkout restore.

## Context

Woo native coupon validation and signed restoration link are distinct WordPress boundaries that must be validated in the integrated runtime.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Run real Woo fixture (Classic and Blocks) with two installations, customer-specific checkout/consent state, selected versus unselected coupons and approved Meta templates.
- Exercise NONE, FIXED selected eligible/ineligible candidates, AI all-current-catalogue shortlist, provider usage/exclusion/expiry changes and no-offer fallback.
- Tap the actual WhatsApp CTA in test browser and verify installation-scoped cart restore, expiry, replay, removed/changed products, no automatic coupon application and no open redirect.
- Exercise stale grants/private DNS, incorrect shop, provider failure, product IMAGE media absence, category/translation fallback, STOP, moderation, final send fence and credit/Support notice idempotency.
- Prove Shopify availability flags and existing ARCH-036 Woo selection behaviour have not regressed.

## Out of Scope

- No provider implementation work, deployment configuration invention or early system-test gating of other tasks.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Never claim live end-to-end approval based only on mocked Meta or development-local Woo HTTPS; list manual provider verification separately.
- No customer data leakage in fixture logs or screenshots.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Add Woo initial-outreach integrated scenarios.
- [ ] Exercise customer-click restore, expiry, rule failure and credit/STOP matrix.
- [ ] Record reproducible certification and residual external verification.

## Interfaces / Contracts

- ARCH-052 accepted Woo native endpoints, Background resolver, immutable Meta bindings and existing Woo system-test integration.

## Dependencies

- `ARCH-052-BACKGROUND-008` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-API-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-WOOCOMMERCE-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-WOOCOMMERCE-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-ADMIN-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-ADMIN-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-DATABASE-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-DATABASE-002` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

None.

## Acceptance Criteria

- [ ] A valid Woo return link really restores customer checkout; invalid links cannot cross shops.
- [ ] All three modes have correct safe messages and no false discounts or duplicate credits.

## Validation

- [ ] System-test harness with WordPress/WooCommerce, Postgres/Redis and Meta simulator.
- [ ] Woo Classic/Blocks/browser integration plus `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-system-test/ (new ARCH-052 Woo scenarios/fixtures)`

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
