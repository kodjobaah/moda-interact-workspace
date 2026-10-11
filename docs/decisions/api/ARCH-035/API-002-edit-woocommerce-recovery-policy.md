---
id: ARCH-035-API-002
architecture_id: ARCH-035
title: Expose safe Woo recovery policy reads and updates
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 92
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-002
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-API-002: Expose safe Woo recovery policy reads and updates

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-175935).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Allow Woo merchants to edit recovery start delay and follow-up policy using the existing Shop-owned recovery settings and effective policy precedence.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate provider-neutral Moda domain state. The current capability is not established by this task definition.

## Scope

- Read current merchant-configured and effective values, platform-admin override indicators and allowed update ranges; never misrepresent effective settings as editable overrides.
- Add authenticated bounded mutation with compare-and-swap/revision protection for delay and follow-up enabled/delay only, retaining default/category/override precedence and audit.
- Provider-specific recovery-offer controls remain NONE/unavailable until ARCH-035-API-011 and runtime work prove Woo coupon safety.
- Do not copy Shopify-only fixedShopifyDiscountId or assign ShopifyDiscount rows to Woo shops.

## Out of Scope

- Coupon ingestion or provider discount application, direct platform-admin override edits, new merchant Settings table unless a precise schema blocker is found.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Requirements

**R1.** Read current merchant-configured and effective values, platform-admin override indicators and allowed update ranges; never misrepresent effective settings as editable overrides.

**R2.** Add authenticated bounded mutation with compare-and-swap/revision protection for delay and follow-up enabled/delay only, retaining default/category/override precedence and audit.

**R3.** Provider-specific recovery-offer controls remain NONE/unavailable until ARCH-035-API-011 and runtime work prove Woo coupon safety.

**R4.** Do not copy Shopify-only fixedShopifyDiscountId or assign ShopifyDiscount rows to Woo shops.


## Work Items

- [ ] Read current merchant-configured and effective values, platform-admin override indicators and allowed update ranges; never misrepresent effective settings as editable overrides.
- [ ] Add authenticated bounded mutation with compare-and-swap/revision protection for delay and follow-up enabled/delay only, retaining default/category/override precedence and audit.
- [ ] Provider-specific recovery-offer controls remain NONE/unavailable until ARCH-035-API-011 and runtime work prove Woo coupon safety.
- [ ] Do not copy Shopify-only fixedShopifyDiscountId or assign ShopifyDiscount rows to Woo shops.
- [ ] Add focused contract, invalid-input, tenant-security and integration tests within this repository's ownership boundary.
- [ ] Supply exact changed-file list, baseline SHA, validation evidence, Completion Report and worktree/branch synchronization evidence.

## Interfaces / Contracts

- Owning repository: `moda-interact-api`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

No blocking task dependency beyond the accepted ARCH-026/027 foundations in the stated snapshot. Confirm current compatible package/DB pins before claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-002`

## Acceptance Criteria

- [ ] Boundary, stale-revision and override precedence tests.
- [ ] Woo shop scope, non-Woo denial and no Shopify discount linkage tests.
- [ ] Read-after-write and Shopify recovery-policy regression tests.
- [ ] Scope stays within `moda-interact-api` and preserves approved cross-provider and 20-locale contracts.
- [ ] Baseline, task launcher isolation, implementation commit, parent task report and regression evidence are recorded without false claims for unavailable provider services.
- [ ] `git diff --check` and repository-required build/test/lint commands pass or precise blockers are reported.

## Validation

- [ ] Run repository-declared focused test suites plus full typecheck/lint/build where applicable.
- [ ] Run real integration/black-box provider or disposable database evidence when this task's scope includes that dependency; do not substitute a mocked success.
- [ ] Check tenant isolation, disconnected/revoked credential handling, idempotency and requested negative cases.
- [ ] For Woo UI tasks, run `npm run test:i18n`, `npm run i18n:verify:20`, PHP/JS tests, admin-locale test, `npm run plugin-zip` and manual LocalWP workflow.
- [ ] Verify `git diff --check` and submit the canonical Completion Report; leave all `_index.md` files untouched until explicit reconciliation.

## Stop Condition

When requirements/acceptance and required validation are fulfilled, set the task to `review`, populate the Completion Report and return to `moda_architect`. Do not begin dependent tasks or change other repositories on this task branch.

## Implementation Notes

Keep production responsibilities in small testable modules; prefer provider-neutral existing ownership to Shopify/Woo service duplication. Return unexpected cross-repository schema or provider-contract gaps to the architect before widening scope.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Dependencies will be rechecked at task claim time; no generated task document itself creates a branch, provider credential, tested artifact or release.

### Unresolved Issues

None identified beyond documented dependencies/provider gating.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Return to architect on implementation submission.
