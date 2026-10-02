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
status: in_progress
priority: 90
executor: copilot
claimed_at: 2026-10-02T00:32:35Z
attempt: 1
depends_on:
  - ARCH-025-SHOPIFY-008
enables:
  - ARCH-025-SHOPIFY-010
created: 2026-10-01
updated: 2026-10-02
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
- Extracted collaborator constructors must be side-effect-free: store/wire dependencies only. Do not perform provider/database I/O, environment discovery or eager Prisma-model access during `new BillingService(...)`; the frozen suite constructs the façade with many partial test doubles.
- This is move-only refactoring: do not remove, coalesce, reorder or otherwise optimise away an existing provider/database read, write, lock or transaction as an incidental cleanup. Any intentional I/O change is outside this task.
- Do not introduce a new logger, DI container, command bus, plugin framework or generic billing framework.
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`. The proven pre-task failure set is `ARCH025-TEST-001`; the task must introduce no additional failing identifier.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — move exact notification capability without moving sync classification

Move logic equivalent to:

```text
TranslationDispatch
SubscriptionLifecycle
SubscriptionIdentityFacts
deriveLifecycleIdentity
persistSubscriptionEndedNotification
renderSubscriptionEndedMessage
```

into the notification service/module. The sync transaction must continue deciding whether the **previous** Subscription was ACTIVE/TRIALING and constructing the immutable lifecycle facts; this task does not move no-contract classification or the billing Subscription update into the notification service.

### R2 — preserve public helper export

`renderSubscriptionEndedMessage` remains exportable from `billing.service.ts` for compatibility.

### R3 — preserve support-message identity/idempotency

Keep the same lifecycle identity derivation, source-key format/version, system message code, language selection, upsert/duplicate behaviour and translation request creation rules.

### R4 — preserve failure isolation and exact error propagation

Do not move notification/translation work into the transaction that commits billing Subscription state. Notification or translation dispatch failure must not roll back an already committed billing projection.

After the billing transaction commits, preserve the current error rule exactly: failure with message `Unable to derive a durable subscription lifecycle identity.` is rethrown; all other notification-persistence or translation-dispatch failures are best-effort and do not fail `syncSubscription()`. Keep the missing-identity constant as a repository-internal export if needed so the caller does not duplicate/change the string.

### R5 — preserve dispatch injection and timing

The existing `BillingService` third constructor dependency (`dispatchTranslation`) remains supported and is passed to the extracted notification owner. Move/define the repository-internal `TranslationDispatch = (translationId: string) => Promise<void>` type with this owner and import the type into the façade rather than making the notification module depend on `billing.service.ts`. The owner may persist then dispatch using that injected function, but dispatch must occur only after the notification persistence transaction has committed and only when a translation ID was newly returned, exactly as today.

## Work Items

- [ ] Create `SubscriptionEndedNotificationService` and move lifecycle identity/render/persistence/translation logic while leaving ended-state classification in sync.
- [ ] Preserve compatibility re-export of `renderSubscriptionEndedMessage`.
- [ ] Wire façade/sync path to the collaborator without changing side-effect timing.
- [ ] Add focused tests for provider-ID/cycle fallback lifecycle identity, missing-identity rethrow, source-key replay/idempotency, language/translation decisions, post-commit dispatch and best-effort non-identity failure isolation.
- [ ] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Consumes existing merchant-support functions and Shared merchant-communication constants. Repository-internal lifecycle identity derivation may be imported by the still-unextracted sync path. No new event/queue/shared contract.

## Dependencies

- `ARCH-025-SHOPIFY-008`

## Enables

- `ARCH-025-SHOPIFY-010`

## Acceptance Criteria

- [ ] Subscription-ended support side effect has one owner.
- [ ] Message identity/code/language and translation semantics are unchanged.
- [ ] Already committed billing state remains isolated from notification/dispatch failure; missing durable lifecycle identity still propagates while all other notification/dispatch failures remain best-effort.
- [ ] `renderSubscriptionEndedMessage` compatibility export remains.
- [ ] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)"` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` introduces no failing identifier outside `ARCH025-TEST-001`
- [ ] `npm test -- tests/unit/services/billing/subscription-ended-notification.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/subscription-ended-notification.service.ts tests/unit/services/billing/subscription-ended-notification.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

The service may own its internal database transaction for support-message persistence exactly as today. Do not combine it with generic merchant-support ownership.


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
