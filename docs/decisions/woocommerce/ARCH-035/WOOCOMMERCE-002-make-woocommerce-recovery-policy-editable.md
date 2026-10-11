---
id: ARCH-035-WOOCOMMERCE-002
architecture_id: ARCH-035
title: Add editable Woo recovery policy controls
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 92
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-002
enables:
  - ARCH-035-SYSTEM-TEST-001
  - ARCH-035-WOOCOMMERCE-011
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-WOOCOMMERCE-002: Add editable Woo recovery policy controls

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-175935).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Extend the existing Store Category and read-only effective recovery summary into a safe merchant-editable Recovery Settings view.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate provider-neutral Moda domain state. The current capability is not established by this task definition.

## Scope

- Keep accepted Store Category selector and effective summary; add recovery start delay, follow-up on/off and delay inputs, save/verify/conflict feedback and reset where contract permits.
- Make provider offer options explicitly unavailable unless the approved Woo coupon backend is ready; do not show nonfunctional Shopify discount choices.
- Separate React components, controller/session revision, PHP REST proxy and view; prevent duplicate writes and stale confirmation on reconnect.
- Preserve WordPress administrator locale, 20 complete language packs and keyboard-responsive UI.

## Out of Scope

- Editing platform-owned overrides, unverified coupon discounts, monolithic page expansion.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Requirements

**R1.** Keep accepted Store Category selector and effective summary; add recovery start delay, follow-up on/off and delay inputs, save/verify/conflict feedback and reset where contract permits.

**R2.** Make provider offer options explicitly unavailable unless the approved Woo coupon backend is ready; do not show nonfunctional Shopify discount choices.

**R3.** Separate React components, controller/session revision, PHP REST proxy and view; prevent duplicate writes and stale confirmation on reconnect.

**R4.** Preserve WordPress administrator locale, 20 complete language packs and keyboard-responsive UI.


## Work Items

- [ ] Keep accepted Store Category selector and effective summary; add recovery start delay, follow-up on/off and delay inputs, save/verify/conflict feedback and reset where contract permits.
- [ ] Make provider offer options explicitly unavailable unless the approved Woo coupon backend is ready; do not show nonfunctional Shopify discount choices.
- [ ] Separate React components, controller/session revision, PHP REST proxy and view; prevent duplicate writes and stale confirmation on reconnect.
- [ ] Preserve WordPress administrator locale, 20 complete language packs and keyboard-responsive UI.
- [ ] Add focused contract, invalid-input, tenant-security and integration tests within this repository's ownership boundary.
- [ ] Supply exact changed-file list, baseline SHA, validation evidence, Completion Report and worktree/branch synchronization evidence.

## Interfaces / Contracts

- Owning repository: `moda-interact-woocommerce`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-API-002` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-SYSTEM-TEST-001`
- `ARCH-035-WOOCOMMERCE-011`

## Acceptance Criteria

- [ ] Manual LocalWP edit/reload, override indicator and conflict review.
- [ ] PHP authenticated mutation checks, JS controls/stale/duplicate-submit tests.
- [ ] 20 locale asset and package validation.
- [ ] Scope stays within `moda-interact-woocommerce` and preserves approved cross-provider and 20-locale contracts.
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
