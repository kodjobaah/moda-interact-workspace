---
id: ARCH-035-WOOCOMMERCE-010
architecture_id: ARCH-035
title: Extend Woo Overview with recovery performance
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 47
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-010
  - ARCH-035-WOOCOMMERCE-009
  - ARCH-035-WOOCOMMERCE-006
enables:
  - ARCH-035-SYSTEM-TEST-002
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-WOOCOMMERCE-010: Extend Woo Overview with recovery performance

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Add Shopify-aligned recovery metrics, date filters, recent and pending recoveries and capacity indicators to current Woo Overview.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted
ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate
provider-neutral Moda domain state. The current capability is not established by this task definition.

## Deterministic implementation specification — mandatory

**Architect contract.** The exact model/column names, paths, API shapes, authentication boundary, state machine and
negative cases below are the implementation target. This section supersedes less-specific high-level text elsewhere
in this task. Agents may split production code into smaller modules, but must not change a public contract, migration
field, ownership rule, or dependency without returning to the architect. If a named existing dependency is absent or
incompatible, **STOP** and report the precise finding; do not silently invent a substitute.

**Files:** extend `src/overview-screen.js` by thin composition into
`src/overview/{analytics-client,analytics-controller,analytics-panels,pending-recoveries,recovery-stats}.js` and
`_overview.scss`; PHP `includes/Rest/OverviewAnalyticsController.php` plus API client/class-map, tests and
20-language assets. Keep all existing connection/onboarding/store-language/category items intact.

**UI:** GET API-010 `/v1/merchant/overview?range=7D|30D|90D` via privileged WordPress REST. Present counts by
DETECTED/MESSAGE_SENT/ENGAGED/COMPLETED/EXPIRED/CANCELLED, pending cards limited to 10, current capacity and
provider-proven recovered value or a **not yet verifiable** explanation when value=null. Range control selection
requests fresh data, without auto-refresh while merchant is interacting; manual Refresh and loading/empty/error
states. Verified Shop-owned links into WOOCOMMERCE-009 Recoveries and WOOCOMMERCE-006 Usage. Never display
null/unproved revenue as `$0 recovered` or reinterpret Woo billing month as 30-day entitlement.

**Tests:** connected/disconnected, independent AJAX errors do not hide connection, stale range switch, cross-Shop
link rejected, revenue null/currency formatting, admin locale, WordPress nonce and all 20 compiled translation packs;
dashboard layout responsive and no huge monolithic overview file.

## High-level scope (non-authoritative summary)

- Keep accepted connection/onboarding/store-category overview sections and add modular recovery analytics/pending widgets.
- Link to Woo Recoveries and Usage screens via native navigation and use API authoritative read values/refresh status.
- Apply administrator locale and complete 20 language packs; implement responsive/keyboard accessibility.
- Show honest unavailable/empty state rather than zero revenue when source evidence is absent.

## Out of Scope

- Unrelated Shopify or Woo Billing feature changes; changing another repository in this task.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Implementation work items — mandatory

- [ ] Implement **exactly** the named files, routes/models and public DTO fields in the Deterministic implementation specification; do not widen cross-repository ownership.
- [ ] Enforce every declared shop/platform binding, validation boundary, state transition, CAS/idempotency invariant, denial path and privacy restriction.
- [ ] Implement the **specific negative and concurrency test matrix** named in the specification; record actual commands and real results.
- [ ] Prove that affected Shopify behaviour and current ARCH-026/027 Woo onboarding/billing contracts are preserved.
- [ ] Provide a bounded diff, changed-file list, applied migration/Shared package version where applicable, task Completion Report, and clean synchronised implementation/task worktree evidence.

## Cross-repository boundary (common requirements)

- Owning repository: `moda-interact-woocommerce`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-API-010` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-009` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-006` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] LocalWP Shopify/Woo screenshot parity review with representative fixture data.
- [ ] Date-filter, pending pagination, navigation and stale/disconnect tests.
- [ ] 20-locale, WordPress REST and ZIP/regression validation.
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

When requirements/acceptance and required validation are fulfilled, set the task to `review`, populate the Completion
Report and return to `moda_architect`. Do not begin dependent tasks or change other repositories on this task branch.

## Implementation Notes

Keep production responsibilities in small testable modules; prefer provider-neutral existing ownership to Shopify/Woo
service duplication. Return unexpected cross-repository schema or provider-contract gaps to the architect before
widening scope.

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
