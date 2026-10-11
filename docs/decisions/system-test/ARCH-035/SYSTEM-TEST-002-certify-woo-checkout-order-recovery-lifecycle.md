---
id: ARCH-035-SYSTEM-TEST-002
architecture_id: ARCH-035
title: Certify Woo checkout-to-recovery and order outcomes
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-WOOCOMMERCE-007
  - ARCH-035-WOOCOMMERCE-008
  - ARCH-035-BACKGROUND-002
  - ARCH-035-WOOCOMMERCE-009
  - ARCH-035-WOOCOMMERCE-010
enables:
  - ARCH-035-SYSTEM-TEST-003
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-SYSTEM-TEST-002: Certify Woo checkout-to-recovery and order outcomes

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Certify full Woo cart/checkout/order ingestion, abandonment scheduling, recovery status, overview counts and no-late-outreach behaviour.

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

**Files:** `src/arch035/woo-activity/{wp-fixtures,api-executor,background-executor,assertions}.js`,
`test/arch035/woo-activity.test.js`, selected scenario-catalogue registrations and evidence manifest; reuse existing
ephemeral PostgreSQL/Redis harness, WhatsApp emulator and checkout/order worker images. No source-code workaround or
hidden fixture after start.

**Proof matrix:** Classic authenticated checkout, Classic guest checkout, Checkout Blocks, HPOS order meta; unique
checkoutKey and stable eventId across 5xx retries; legitimate POST receives 202 then identical replay 200, conflict
409; lost Redis hint recovered by DB claim; same key cross-Shop collision isolated; order paid before checkout, order
placed before maturity, paid after send, duplicate order paid and cancelled->paid, late cart after terminal, missing
explicit WhatsApp consent and no-number no-charge, cap reservation idempotence; recovered-revenue nonzero only with
verified exact paid lineage; API-009 list/detail and API-010 counts match DB; Shopify original checkout/order
messaging scenario unchanged.

**Evidence:** `ARCH035-WOO-01..12` separate JSON artifacts with HTTP, receipt/lineage/CheckoutRecovery status and
event count, queue evidence, WhatsApp delivery emulator count, no leaked containers, source revision+timestamps and
redacted run IDs. A unit test with a fake WordPress hook is never sufficient for Classic/Blocks/HPOS certification;
report unsupported external provider tests as BLOCKED, not PASS.

## High-level scope (non-authoritative summary)

- Run reproducible Classic/Checkout Blocks and HPOS-compatible fixture paths against disposable API/DB/Redis/Background and WordPress plugin.
- Prove genuine authenticated ingress, replay/out-of-order/failed queue ordering, shop scoping, customer consent/no number and order-first suppression.
- Certify Recoveries list/detail, pending/overview metrics, Usage linkage and Shopify lifecycle regression in black-box evidence.
- Keep payment/refund provider certification under ARCH-027; do not silently equate mocked Woo order data with Woo SaaS billing evidence.

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

- Owning repository: `moda-interact-system-test`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-WOOCOMMERCE-007` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-008` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-BACKGROUND-002` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-009` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-010` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-SYSTEM-TEST-003`

## Acceptance Criteria

- [ ] End-to-end event->materialisation->outreach->order completion matrix.
- [ ] Security tenant/credential/logout, zero PII logs and idempotent repeated events.
- [ ] Fresh disposable checkout and failure cleanup evidence and Shopify regression.
- [ ] Scope stays within `moda-interact-system-test` and preserves approved cross-provider and 20-locale contracts.
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
