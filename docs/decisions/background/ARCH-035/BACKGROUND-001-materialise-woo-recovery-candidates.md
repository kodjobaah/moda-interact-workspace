---
id: ARCH-035-BACKGROUND-001
architecture_id: ARCH-035
title: Materialise and reschedule Woo abandoned checkout candidates
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-008
  - ARCH-035-WOOCOMMERCE-007
enables:
  - ARCH-035-BACKGROUND-002
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-BACKGROUND-001: Materialise and reschedule Woo abandoned checkout candidates

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Consume durable Woo cart/checkout events into the established recovery candidate and maturity pipeline with the same entitlement/outreach safety as Shopify.

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

**Files:** new
`src/services/woocommerce-activity/{receipt-claim.service,checkout-candidate.service,checkout-snapshot}.ts`
(exact three TypeScript modules), unit/Postgres tests; thin integration into existing
`src/workers/pending-recovery-candidate.worker.ts` and `src/services/pending-recovery-candidate/*` entrypoint. Use
DATABASE-001 receipt and lineage, accepted Shared v1 and existing `CheckoutRecovery`/candidate orchestration. No
second Woo-only WhatsApp worker or billing ledger.

**Deterministic handler:** claim a bounded ordered batch (max 100) of due PENDING/FAILED receipts with DB `SKIP
LOCKED`, CAS `PROCESSING/claimedUntil`, retry expired leases, and write APPLIED/IGNORED/FAILED plus safe failureCode. Prune only APPLIED/IGNORED receipts older than 30 days (bounded batches of 1000); retain PENDING/PROCESSING and failed/dead-letter events for manual recovery for >=90 days. Never delete `WooCommerceCheckoutLineage` terminal tombstones during ordinary receipt cleanup.
For `CHECKOUT_UPSERT`, lock lineage; if terminalState exists or `revision <= lineage.lastAppliedRevision`, mark IGNORED. `lineage.lastRevision` is the API-accepted high-water and must **not** itself suppress a first accepted receipt. On successful candidate materialisation, advance `lastAppliedRevision` with a CAS guarded by the same Shop/lineage lock.
Otherwise map only whitelisted `snapshot` fields to current recovery snapshot mapper; find/create the latest
`CheckoutRecovery` for `(Shop,checkoutKey,generation)` via lineage association, not a phone/email match. Save
`checkoutToken="woo:" + checkoutKey` only after ensuring no Shopify-generated token collision, `cartToken` from
server-owned cartKey, `lastExternalActivityAt` and stable generation; regenerate/reschedule pending maturity through
existing `pending-recovery-candidate` engine when checkout changes. The lineage links exactly one current
CheckoutRecovery; later lifecycle generations only via existing controlled generation rules.

**Reachability/entitlement:** if verified opt-in or E.164 phone is absent, recovery may remain DETECTED but **no
outbound/reservation/charge**, using ARCH-028 no-number policy. Preserve locale default/detection, suppression
interval, pricing eligibility and merchant recovery delay. Reuse existing `recovery-initiation`,
`recovery-materialization` and WhatsApp admission; do not enqueue messages directly from receipt processing.

**Tests:** duplicate receipt/parallel worker, Redis hint lost, order terminal before candidate, stale revision,
delayed activity handoff, recurrence/generation unique, invalid missing phone/consent, shop-local currency and URLs,
capacity and language regressions, Shopify checkout worker full subset. Record actual SQL commit and queue evidence;
no mock claimed as end-to-end.

## High-level scope (non-authoritative summary)

- Consume Shared v1 events only from authenticated persisted receipts, preserve ordering/replay and create/update a Shop-owned CheckoutRecovery with stable generation.
- Schedule maturity/rescheduling using effective recovery policy and existing queue controls without contacting Woo inside core transaction.
- Honor no-number/no-charge WhatsApp policy, store language and suppression, plan availability and customer consent; never manufacture a reachable recipient.
- Preserve Shopify event adapters, checkout recovery state transitions and existing ARCH-028 failures/reconciliation.

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

- `ARCH-035-API-008` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-007` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-BACKGROUND-002`

## Acceptance Criteria

- [ ] Disposable Postgres/Redis black-box activity->candidate->maturity tests.
- [ ] Duplicate/upsert/reorder and no-phone/no-entitlement behavior tests.
- [ ] Shopify regression, bounded log data and source module size checks.
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

**Superseded by ARCH-035 UI-only scope revision (11 October 2026).** This definition is historical and MUST NOT be claimed or executed under ARCH-035. Backend/data/event/coupon capabilities require a separately agreed architecture if ever authorised. No implementation was reviewed or accepted.

Return to architect on implementation submission.
