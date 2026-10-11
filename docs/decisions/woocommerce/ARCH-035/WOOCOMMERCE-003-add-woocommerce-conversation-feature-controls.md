---
id: ARCH-035-WOOCOMMERCE-003
architecture_id: ARCH-035
title: Add Conversation Features controls to Woo Recovery Settings
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-003
enables:
  - ARCH-035-SYSTEM-TEST-001
  - ARCH-035-WOOCOMMERCE-004
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-WOOCOMMERCE-003: Add Conversation Features controls to Woo Recovery Settings

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Render and save allowed AI Conversations/Checkout Recovery and other merchant-feature preferences inside Recovery Settings.

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

**Files:** `includes/Rest/FeaturePreferencesController.php` plus `ModaApiClient` methods/class-map,
`src/recovery-settings/{feature-preferences-client,feature-preferences-controller,feature-preferences-panel,feature-preference-card}.js`,
focused tests and scoped styling. Compose under existing Recovery Settings rather than new `Features` submenu; no
300+ line UI/controller.

**UI/transport:** GET `/wp-json/moda-interact/v1/feature-preferences` and PUT same endpoint mapping API-003, with
strict WP nonce+`manage_woocommerce` and server-stored bearer. Show one card per API feature: title/description,
`enabled`, `effective`, `required`, `editable`, `planEligible`; system-required/always-enabled/plan-blocked states
visibly locked and never clickable. Save exactly `{expectedRevision,changes:[{featureId,enabled}]}`; no all-features
overwrite when one toggle changes. A conflicting revision prompts reload, no silent last-write-wins; loading, error
and successful save are accessible live-region text.

**Tests:** optional toggle, mandatory toggle denied even if manually POSTed, plan upgrade eligibility refresh, rapid
double click, 409 conflict, revoked connection cancels render, long translated feature labels, 20 PO/POT/MO/JS,
proper ZIP/PHP coverage; unchanged Shop language/store category.

## High-level scope (non-authoritative summary)

- Present effective, compulsory, disabled-by-plan and merchant-configurable states from the server without inferring entitlements in React.
- Separate small feature cards, save controller, error view and secured PHP REST proxy; keep current Store Category/recovery policy behaviour.
- Block double-click updates, clear state on disconnect, handle concurrent administrative changes and preserve accessible feedback.
- Translate all new messages for 20 supported WordPress admin locales.

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

- `ARCH-035-API-003` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-SYSTEM-TEST-001`
- `ARCH-035-WOOCOMMERCE-004`

## Acceptance Criteria

- [ ] Disabled/required/plan-unavailable state tests.
- [ ] Authenticated save, stale response, locale and packaging tests.
- [ ] LocalWP screenshot comparison with Shopify Recovery Settings.
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
