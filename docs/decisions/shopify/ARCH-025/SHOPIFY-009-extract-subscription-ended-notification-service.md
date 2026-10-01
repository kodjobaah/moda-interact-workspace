---
id: ARCH-025-SHOPIFY-009
architecture_id: ARCH-025
title: Extract subscription-ended notification workflow
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-008
enables:
  - ARCH-025-SHOPIFY-010
created: 2026-10-01
updated: 2026-10-01
---

# Extract subscription-ended notification workflow

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract subscription-ended support-message persistence, lifecycle identity derivation and translation scheduling into a dedicated service while preserving post-commit/best-effort isolation from billing state.

## Context

`syncSubscription()` currently invokes a substantial notification side effect for the no-active-subscription path. Moving that side effect before the final sync extraction reduces coordinator scope and establishes an explicit failure-isolation boundary.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/subscription-ended-notification.service.ts              # new
tests/unit/services/billing/subscription-ended-notification.service.test.ts  # new
```

Merchant-support service code is not modified.

## Out of Scope

- changing support message schema/codes/actions.
- changing translation infrastructure.
- changing when a subscription is classified ended.
- sync coordinator extraction itself.
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

### R1 — move exact notification capability

Move logic equivalent to:

```text
SubscriptionLifecycle
SubscriptionIdentityFacts
deriveLifecycleIdentity
persistSubscriptionEndedNotification
renderSubscriptionEndedMessage
```

into the notification service/module.

### R2 — preserve public helper export

`renderSubscriptionEndedMessage` remains exportable from `billing.service.ts` for compatibility.

### R3 — preserve support-message identity/idempotency

Keep the same lifecycle identity derivation, source-key format/version, system message code, language selection, upsert/duplicate behaviour and translation request creation rules.

### R4 — preserve failure isolation

Do not move notification/translation work into the transaction that commits billing Subscription state. Notification or translation dispatch failure must not roll back an already committed billing projection.

### R5 — preserve dispatch injection

The existing `BillingService` third constructor dependency (`dispatchTranslation`) remains supported and is passed to the extracted notification owner.

## Work Items

- [ ] Create `SubscriptionEndedNotificationService` and move lifecycle identity/render/persistence/translation logic.
- [ ] Preserve compatibility re-export of `renderSubscriptionEndedMessage`.
- [ ] Wire façade/sync path to the collaborator without changing side-effect timing.
- [ ] Add focused tests for lifecycle identity, source-key replay/idempotency, language/translation decisions and dispatch failure isolation.
- [ ] Prove frozen façade regression suite remains byte-identical and green.

## Interfaces / Contracts

Consumes existing merchant-support functions and Shared merchant-communication constants. No new event/queue/shared contract.

## Dependencies

- `ARCH-025-SHOPIFY-008`

## Enables

- `ARCH-025-SHOPIFY-010`

## Acceptance Criteria

- [ ] Subscription-ended support side effect has one owner.
- [ ] Message identity/code/language and translation semantics are unchanged.
- [ ] Already committed billing state remains isolated from notification/dispatch failure.
- [ ] `renderSubscriptionEndedMessage` compatibility export remains.
- [ ] Frozen 127-test façade suite passes unchanged.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `sha256sum tests/unit/services/billing.service.test.ts` returns exactly `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` passes all 127 tests
- [ ] `npm test -- tests/unit/services/billing/subscription-ended-notification.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/subscription-ended-notification.service.ts tests/unit/services/billing/subscription-ended-notification.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Implementation Notes

The service may own its internal database transaction for support-message persistence exactly as today. Do not combine it with generic merchant-support ownership.

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
