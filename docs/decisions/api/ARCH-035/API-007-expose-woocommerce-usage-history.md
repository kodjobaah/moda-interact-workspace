---
id: ARCH-035-API-007
architecture_id: ARCH-035
title: Expose Woo provider-correct usage and entitlement history
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 72
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-006
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-API-007: Expose Woo provider-correct usage and entitlement history

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Provide a Woo-authenticated merchant usage-history read using existing UsageEvent and entitlement-period data, not Shopify billing provider views.

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

**Files:** `src/merchant/usage/{contract,history.service,routes}.ts`, tests and
`openapi/woocommerce-merchant-usage-v1.yaml`. Use existing `billing.UsageEvent`, `BillingPeriod`, `UsageReservation`,
`CheckoutRecovery`, `RecoveryCreditPurchase`; no new schema or copy of Shopify `app/routes/app/usage/route.jsx`
loaders.

**GET `/v1/merchant/usage?scope=CURRENT|HISTORY&metric=ALL|RECOVERY_CONVERSATION&page=1&pageSize=20`:**
`{schemaVersion:1,scope,page,pageSize,total,totalPages,period:{id?,startAt,endAt,kind:"FREE_LIFETIME"|"ENTITLEMENT_30_DAYS"}|null,capacity:{...authoritative
billing
capacity},items:[{id,occurredAt,metric,quantity,provider,sourceLabel,recoveryId|null,billingPeriodIdPresent:boolean}]}`.
Use stable `(occurredAt DESC,id DESC)` order, pageSizes 10|20|50, maximum page 1000; `id` opaque internal event
identity; no raw provider charge/Shopify event handle, no customer PII, no other-Shop recovery references. CURRENT
means active Moda entitlement period for paid, or shop-lifetime Free; HISTORY is all prior Shop-owned events.
Financial Woo monthly renewal is not the 30-day entitlement window.

**Rules:** validate `UsageEvent.shopId` plus linked CheckoutRecovery ownership; Woo records must have provider
`WOOCOMMERCE` or provider-neutral historical context; Shopify reporting-state fields are not merchant display
statuses. Present spent purchased/promotional/Free recovery credits without deriving refund or payment charges; no
invented billing period for Free. Authenticated reads only, bounded Prisma selects. Tests: empty Free, current 30-day
boundary, provider split, history paging/timestamp ties, cross-Shop linked recovery, refuted/double credited usage,
no PSP fields, cancelled subscription history preserved.

## High-level scope (non-authoritative summary)

- Filter events by authenticated shop, bounded period/current-past selector, metric, cursor and stable ordering with linked recovery only when same tenant.
- Distinguish Woo financial billing month from Moda 30-day entitlement windows and Free lifetime/purchased/promotional consumption.
- Expose merchant-safe reason/timestamp/quantity/source status, no raw provider IDs or Shopify reporting-only statuses.
- Handle missing billing period and zero-usage Free states explicitly and safely.

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

- Owning repository: `moda-interact-api`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

No blocking task dependency beyond the accepted ARCH-026/027 foundations in the stated snapshot. Confirm current compatible package/DB pins before claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-006`

## Acceptance Criteria

- [ ] Cursor bounds/foreign-period and platform filtering tests.
- [ ] Free/Paid/FROZEN, purchased/promo and compensation history tests.
- [ ] Shopify usage-history parity/regression and schema validation.
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
