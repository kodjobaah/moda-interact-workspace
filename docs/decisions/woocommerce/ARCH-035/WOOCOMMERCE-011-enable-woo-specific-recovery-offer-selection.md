---
id: ARCH-035-WOOCOMMERCE-011
architecture_id: ARCH-035
title: Add approved Woo recovery-offer selection UI
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 38
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-012
  - ARCH-035-DATABASE-002
  - ARCH-035-WOOCOMMERCE-002
enables:
  - ARCH-035-SYSTEM-TEST-003
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-WOOCOMMERCE-011: Add approved Woo recovery-offer selection UI

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Complete the recovery offer section of Woo Recovery Settings with real eligible Woo coupons and safe offer modes.

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

**Files:** `src/recovery-settings/woo-offers/{client,controller,mode-selector,coupon-list,coupon-status}.js`, scoped
styles/tests, PHP `includes/Rest/RecoveryOffersController.php` and `ModaApiClient` methods/class-map. Compose within
existing Recovery Settings policy form, never a duplicate discount menu. **Dependencies now include API-012** (coupon
selection transaction after DATABASE-002), API-011 proof read, DATABASE-002 and WOOCOMMERCE-002.

**UI:** GET `/v1/merchant/recovery-offers/coupons` through privileged WP GET proxy; PUT
`/v1/merchant/recovery-offers/selection` with `{actionId,expectedRevision,mode,providerCouponId}` through WordPress
nonce + manage_woocommerce. Show NONE always; FIXED only with API-verified selectable coupons from Shop-owned read
grant; AI_BEST_APPLICABLE remains visibly unsupported (disabled with clear reason) until backend capability is
proved, not a fake dropdown. Coupon identity/description/expiry displayed from API only; never send coupon
code/discount value/ShopifyDiscount ID as authority. On 409/expired/revoked provider proof, reset to authoritative
selection with explanatory message and no optimistic coupon promise. On choice NONE, clear provider coupon evidence
via API-012 and do not change recovery delay/follow-up inadvertently.

**Tests:** shortcode/nonce forgery, stale CAS, two shops identical coupon code, expired/restricted/unsupported
coupon, read grant revoked mid-selection, failed API reconnect, long 20-locale labels and CSS, keyboard, idempotent
repeat, full WordPress plugin ZIP and absence of Shopify GraphQL calls.

## High-level scope (non-authoritative summary)

- Present only read-authorised, eligible Woo coupon choices and available AI-applicable/None options from API; no Shopify discount handles.
- Ensure mutations use provider-scoped reviewed selection and revision validation, clearly distinguish unsupported/out-of-date/expired choices.
- Preserve existing delay/follow-up feature controls and 20-language WordPress admin formatting/labels.
- Do not let merchant UI assert a discount was applied until outbound runtime has provider-correct proof.

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

- `ARCH-035-API-012` must be architect-accepted Complete before this task is claimed (API-011 is an upstream read dependency).
- `ARCH-035-DATABASE-002` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-002` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-SYSTEM-TEST-003`

## Acceptance Criteria

- [ ] Coupon disabled and invalidated access states, stale save and duplicate submit tests.
- [ ] LocalWP real permitted coupon read and long-locale UI validation.
- [ ] Proof no Shopify discount or unchecked coupon IDs reach settings.
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

**Superseded by ARCH-035 UI-only scope revision (11 October 2026).** This definition is historical and MUST NOT be claimed or executed under ARCH-035. Backend/data/event/coupon capabilities require a separately agreed architecture if ever authorised. No implementation was reviewed or accepted.

Return to architect on implementation submission.
