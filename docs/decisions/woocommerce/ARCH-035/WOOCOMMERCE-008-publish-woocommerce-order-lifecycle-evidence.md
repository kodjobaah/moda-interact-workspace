---
id: ARCH-035-WOOCOMMERCE-008
architecture_id: ARCH-035
title: Capture authoritative Woo order lifecycle evidence
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 63
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-008
enables:
  - ARCH-035-BACKGROUND-002
  - ARCH-035-SYSTEM-TEST-002
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-WOOCOMMERCE-008: Capture authoritative Woo order lifecycle evidence

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Publish signed/authenticated order outcome events so abandoned checkout recoveries stop or complete when a matching Woo order is placed/paid/cancelled.

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

**Files:** `includes/Activity/{OrderEvents,OrderCorrelation}.php` and PHPUnit/WordPress integration tests; thin hooks
in `includes/Runtime.php`, reusing WOO-007 `ActivityOutbox`/publisher. No SQL on `wp_posts`/`wp_postmeta`; Woo CRUD
only for HPOS.

**Hooks and event mapping:** subscribe to `woocommerce_checkout_order_processed` (Classic),
`woocommerce_store_api_checkout_order_processed` (Blocks) and `woocommerce_order_status_changed` for authoritative
durable order transitions; guard duplicate firings. Read order `_moda_checkout_key` persisted by WOO-007, never guess
by billing email/phone/IP. Produce `ORDER_PLACED` on durable order creation, `ORDER_PAID` only when
`WC_Order::is_paid()`/paid status is provider-confirmed, and `ORDER_CANCELLED` on cancelled/failed terminal
transitions. Do not treat thank-you page or payment intent as proof. One WordPress action result produces stable
`eventId` and revision in durable Action Scheduler outbox; retry bytes unchanged. Do not publish a missing
checkoutKey event under a made-up identity; emit safe diagnostic/attention and skip.

**Ordering/replay:** the API/DB tombstone is authoritative, not provider webhook arrival order; race of payment and
cart updates must never reopen paid recovery. Real Woo order status changes may be emitted repeatedly but same
order/kind/revision must not double complete business state. Tests: classic+Blocks+HPOS, offsite delayed payment,
paid order before checkout snapshot, cancelled/failed, refund status not misrepresented as a fresh paid order,
duplicate hooks, same order replay, disconnected credential, two shops identical order number.

## High-level scope (non-authoritative summary)

- Use HPOS-compatible Woo order hooks and explicit paid/placed/cancelled/refunded state mapping, not assumption based on browser thank-you navigation.
- Correlate canonical order identity to captured cart/checkout context, refuse ambiguous matches and preserve provider timing for out-of-order delivery.
- Retry bounded server-side delivery without duplicate business consequences and never block normal order processing when Moda is unavailable.
- Keep event adapter/test fixtures separate from cart-capture and UI components.

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

- `ARCH-035-API-008` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-BACKGROUND-002`
- `ARCH-035-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Classic/Blocks + HPOS order transition matrix; idempotent repeated status updates.
- [ ] Late paid event, missing checkout relation, credential rotation and no-cross-Shop tests.
- [ ] No double webhook publication or unintended refund/entitlement mutation.
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
