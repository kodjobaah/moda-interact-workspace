---
id: ARCH-025-SHOPIFY-007
architecture_id: ARCH-025
title: Extract hosted plan-change verification workflow
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-006
enables:
  - ARCH-025-SHOPIFY-008
created: 2026-10-01
updated: 2026-10-01
---

# Extract hosted plan-change verification workflow

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract hosted billing-return verification fencing and retry-state updates into `HostedPlanChangeService` while preserving the exact pre-provider/post-provider durable fence semantics.

## Context

The callback workflow has its own concurrency contract and regression coverage. It should be independently reviewable rather than remain mixed with subscription reads/sync.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/hosted-plan-change.service.ts              # new
tests/unit/services/billing/hosted-plan-change.service.test.ts  # new
```

No callback route edits are authorised.

## Out of Scope

- provider subscription read/mapping service.
- activation.
- plan-change business redesign.
- changing retry delay/error code.
- edits to frozen `billing.service.test.ts`.

## Requirements

### Common ARCH-025 invariants

- Preserve `BillingService` constructor compatibility: `new BillingService(provider, database, dispatchTranslation)`.
- Preserve every existing public `BillingService` method signature and the `billingService` singleton export.
- Preserve all current public exports from `app/services/billing/billing.service.ts`; moved symbols must be compatibility re-exported from that file.
- Do not change routes/callers as part of extraction.
- Extracted modules MUST NOT import `billing.service.ts`; dependency direction is façade/coordinator -> collaborator.
- Do not change billing rules, error codes/strings, transaction boundaries, lock order, provider call order, retry semantics, idempotency, CAS/fencing, entitlement arithmetic or durable lifecycle state.
- Do not add provider/API calls or database round trips to the equivalent path solely because code moved.
- Do not introduce a new logger, DI container, command bus, plugin framework or generic billing framework.
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4` and all 127 tests must pass.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — move exact hosted workflow

Move implementation ownership for:

```text
getHostedPlanVerificationFence
recordHostedPlanChangeReturn
recordHostedPlanVerificationFailure
sameHostedPlanVerificationFence / sameFenceDate
```

and the exact lock/reread required by these methods.

### R2 — preserve compatibility exports

`HostedPlanChangeReturnResult` and `HostedPlanVerificationFence` remain exported from `billing.service.ts` with compatible shapes.

### R3 — preserve fence semantics

The durable state captured before provider verification must be compared against the locked/reread state before commit. Any changed protected fact must fence the write even when wall-clock `updatedAt` is equal/older.

### R4 — preserve failure semantics

Provider verification failure updates only existing retry metadata under the same unchanged fence, uses the same `PARTNER_API_ERROR` semantics, and does not manufacture Subscription state when none exists.

### R5 — preserve lock order

Keep the current accepted settings/subscription locking order and transaction boundaries exactly.

## Work Items

- [ ] Create `HostedPlanChangeService` and move fence/result types/helpers/method bodies.
- [ ] Re-export public types through `billing.service.ts`.
- [ ] Leave façade public methods as delegates.
- [ ] Add focused tests for null fence, current/pending/mismatch/no-active, changed-fence no-op, identical-updatedAt changed-content fence, failure retry and lock order.
- [ ] Prove frozen façade regression suite remains byte-identical and green.

## Interfaces / Contracts

Repository-internal service. Existing callback route continues calling `billingService` only; no new route contract.

## Dependencies

- `ARCH-025-SHOPIFY-006`

## Enables

- `ARCH-025-SHOPIFY-008`

## Acceptance Criteria

- [ ] Hosted verification has one owner outside the façade.
- [ ] Fence comparison protects the same complete durable projection.
- [ ] Retry/error behaviour and lock order are unchanged.
- [ ] Callback route is untouched.
- [ ] Frozen 127-test façade suite passes unchanged.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `sha256sum tests/unit/services/billing.service.test.ts` returns exactly `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` passes all 127 tests
- [ ] `npm test -- tests/unit/services/billing/hosted-plan-change.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/hosted-plan-change.service.ts tests/unit/services/billing/hosted-plan-change.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Implementation Notes

This extraction is structural. Do not simplify the fence by comparing fewer fields or by replacing explicit durable-state fencing with timestamps alone.

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
