---
id: ARCH-035-BACKGROUND-002
architecture_id: ARCH-035
title: Reconcile authoritative Woo order outcomes
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 59
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-BACKGROUND-001
  - ARCH-035-WOOCOMMERCE-008
enables:
  - ARCH-035-API-009
  - ARCH-035-API-010
  - ARCH-035-BACKGROUND-003
  - ARCH-035-SYSTEM-TEST-002
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-BACKGROUND-002: Reconcile authoritative Woo order outcomes

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Make paid/placed Woo order evidence deterministically suppress, cancel or complete matching recovery attempts without sending a late recovery message.

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

**Files:** new `src/services/woocommerce-activity/{order-outcome.service,order-correlation.service}.ts`,
unit/Postgres tests; thin existing `src/workers/orders.worker.ts`/candidate integration. No schema changes
(DATABASE-001 lineage contains terminal state and correlation). Background consumes durable authenticated receipt,
not raw provider HTTP/WordPress request.

**State machine:** on ORDER_PLACED mark checkout/lineage terminal for abandonment scheduling, cancel pending
candidate/outbound where still cancelable; on ORDER_PAID mark lineage PAID irreversibly, move the exact Shop-owned
CheckoutRecovery to COMPLETED using existing status history and any verified attribution; on ORDER_CANCELLED keep
that lineage fenced, close/cancel pending outreach, and do not reopen existing recovery; a **new** checkoutKey
permits new recovery only. Resolve correlation strictly via `(shopId,checkoutKey)` and linked `(shopId,orderId)`;
never buyer phone/email. When an order arrives before first checkout event, create/retain the terminal lineage
tombstone so the late checkout receipt is IGNORED. ORDER_PAID outranks stale PLACED/CANCELLED; never allow later
checkout/order cancellation to undo completed PAID.

**Side effects:** cancel only uncommitted scheduling/reservations through existing services and preserve committed
usage (do not compensate paid messages merely because a later order arrives). Do not mutate `ShopEntitlementCounter`
from raw order data. Every transition uses receipt/lineage/high-water checks under Shop+lineage lock and is
idempotent on duplicate provider events. Recovery attribution is null/unknown unless exact source lineage and
verified paid order meet policy; no guessed revenue.

**Tests:** order-first, checkout-first, duplicate paid, cancelled->paid, paid->late checkout, two checkouts sharing
phone, cross-Shop identical order IDs, in-flight WhatsApp race, already committed usage, after-cancellation new
checkoutKey, Shopify order-worker regressions, reconciliation under delayed Redis.

## High-level scope (non-authoritative summary)

- Correlate persisted Woo order evidence to exact Shop-owned cart/checkout lineage and never by ambiguous contact PII.
- Handle order-before-checkout, checkout-after-order and duplicate/out-of-order arrivals with monotonic terminal guards.
- Preserve reservation release/commit correctness, merchant metrics and purchased/Free allowance state; no double completion or charging.
- Continue using existing recovery/WhatsApp orchestration, never a second Woo-only outreach worker.

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

- `ARCH-035-BACKGROUND-001` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-008` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-API-009`
- `ARCH-035-API-010`
- `ARCH-035-BACKGROUND-003`
- `ARCH-035-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Order-first/check-out-first/duplicate delivery tests with queued outreach race.
- [ ] Idempotent completion/cancel and correct credit release, no late WhatsApp proof.
- [ ] Shopify recovery conversion and messaging regressions.
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
