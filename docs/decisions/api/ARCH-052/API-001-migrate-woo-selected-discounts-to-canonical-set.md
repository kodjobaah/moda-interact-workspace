---
id: ARCH-052-API-001
architecture_id: ARCH-052
title: Move Woo offer Save/GET to canonical selected-discount storage
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
- ARCH-052-DATABASE-001
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-API-001: Move Woo offer Save/GET to canonical selected-discount storage

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Make the existing authenticated Woo offer-settings API read/write the canonical merchant selected set while preserving its checkbox UI contract.

## Context

`moda-interact-api/src/merchant/discount-offers/service.ts` currently uses Woo ShopifyDiscount.isAvailable flags as merchant checkbox state and a single compatibility anchor. Woo merchant UI already supports up to 50 selected IDs.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Update existing hosted `merchant/discount-offers/service.ts` and `contract.ts` to return/persist merchant selectedDiscountIds from `ShopRecoverySelectedDiscount`, not the provider-sync flag.
- Keep the existing authenticated installation/shop scope, GET/PUT API envelope, revision handling, Woo UI contract, shop lock, transaction boundary and 409 conflict semantics.
- Atomically replace the selected set and update `ShopSettings` mode and legacy FIXED anchor; verify distinct, bounded, same-shop provider IDs even if coupon statuses have changed.
- Preserve active Admin override presentation and dormant selection, and add integration tests that Woo sync and merchant Save do not race into lost choices.

## Out of Scope

- No new coupon discovery, provider eligibility call, WordPress settings UI or other merchant API endpoint.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Cross-shop IDs rejected transactionally. Never use merchant `selected` to assert provider CURRENT/ACTIVE/checkout eligibility.
- Preserve API contract version unless a deliberate versioned change is necessary; no unreviewed Woo UI break.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Switch read/write adapters to canonical set and preserve API response.
- [ ] Test two Woo shops, concurrent Save/sync, merchant/override source.
- [ ] Run real PostgreSQL transaction tests and consumer compatibility fixtures.

## Interfaces / Contracts

- `GET/PUT` existing merchant discount offers contract; canonical Shared selection validator; DB001 join table.

## Dependencies

- `ARCH-052-DATABASE-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Woo checkboxes remain functional; selected IDs persist without abusing isAvailable.
- [ ] Shopify rows and other merchants remain unmodified; 409 conflict produces no partial save.

## Validation

- [ ] API unit and PostgreSQL integration/concurrency tests.
- [ ] API build/typecheck/lint as declared and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-api/src/merchant/discount-offers/service.ts`
- `moda-interact-api/src/merchant/discount-offers/contract.ts`
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
