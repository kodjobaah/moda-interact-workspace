---
id: ARCH-035-BACKGROUND-003
architecture_id: ARCH-035
title: Resolve Woo recovery offers from verified provider context
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-BACKGROUND-002
  - ARCH-035-API-012
  - ARCH-035-DATABASE-002
enables:
  - ARCH-035-SYSTEM-TEST-003
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-BACKGROUND-003: Resolve Woo recovery offers from verified provider context

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Enable runtime fixed/AI eligible Woo coupon decisions only with approved shop-scoped provider evidence and safe immutable snapshots.

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

**Files:** `src/services/woocommerce-recovery-offers/{offer-decision.service,provider-evidence.service}.ts`, focused
tests; thin call from existing `src/services/checkout-recovery/recovery-outreach-*` before dispatch. Use API-011's
accepted Woo read-grant provider proof (via service-only API client, never merchant browser), DATABASE-002 selection
row, and existing `RecoveryOutreachAttempt.offerSnapshot`. No new queue or merchant-side balance mutations.

**Exact algorithm:** for `Shop.platform=WOOCOMMERCE`, read authoritative desired mode from `ShopSettings`/effective
admin override. If NONE or unsupported AI strategy, snapshot `decision=NONE`. FIXED requires a non-null
`WooCommerceRecoveryCouponSelection` for **this shop**, matching verified providerCouponId/code, revision/evidence,
unexpired proof and current exact checkout cart. Re-fetch/validate coupon for product/category/customer eligibility
at send time; on any partial evidence/revocation/timeouts return NONE, never select 'best' optimistically. Build
`woo.offer.v1` normalized `offerSnapshot` with keys frozen by DATABASE-002, CAS it once on the attempt, then pass
only verified customer-usable coupon code into the existing outbound composer. Do not use `fixedShopifyDiscountId` on
Woo attempts or call Shopify discount sync; for Shopify branch preserve existing behaviour exactly.

**Tests:** selected coupon valid, merchant switches after attempt, deleted/expired/usage-exhausted, provider read
permission revoked, Woo item restrictions, two shops same code, exact immutable snapshot replay, concurrent workers,
referral/no-number no send, no double discount, and Shopify FIXED/AI regression. If provider proof fails, emitting an
outreach with an unsupported discount claim is forbidden even if conversation language/model asks for it.

## High-level scope (non-authoritative summary)

- Keep offer NONE as safe fallback when Woo coupon evidence cannot prove applicability, expiry, limits or provider state.
- Use shop/platform-safe contract and persisted offer identity from API-011/DATABASE-002; do not call Shopify discount sync/publish paths for Woo.
- Preserve timing/recovery send decisions and idempotent offer snapshot once selected; no unverified discount promises to WhatsApp customers.
- Bound provider lookups, retries and telemetry; do not ask merchant UI to supply a raw coupon at dispatch time.

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

- Owning repository: `moda-interact-background`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-BACKGROUND-002` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-API-012` must be architect-accepted Complete before this task is claimed (API-011 is an upstream read dependency).
- `ARCH-035-DATABASE-002` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-SYSTEM-TEST-003`

## Acceptance Criteria

- [ ] Eligible/expired/usage-limit/product-restriction/fixed-vs-AI and unavailable provider tests.
- [ ] Duplicate/out-of-order outreach and no-coupon fallback.
- [ ] Shopify discount policy and WhatsApp delivery regressions.
- [ ] Scope stays within `moda-interact-background` and preserves approved cross-provider and 20-locale contracts.
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
