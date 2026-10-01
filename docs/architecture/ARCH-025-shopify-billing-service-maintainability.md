---
id: ARCH-025
title: Shopify BillingService maintainability refactor
status: in_progress
coordinator: moda_architect
created: 2026-10-01
updated: 2026-10-01
---

# ARCH-025: Shopify BillingService maintainability refactor

## Status

In Progress.

ARCH-025 is intentionally scoped to the Shopify application repository only:

```text
moda-interact/
```

It refactors the current `app/services/billing/billing.service.ts` monolith behind its existing public façade. It does **not** refactor Background billing reconciliation, CheckoutRecovery, Admin pricing-plan authoring, Commerce Studio, Gateway, Shared, Database or System Test.

ARCH-025 is materialised in the canonical development workspace. `ARCH-025-SHOPIFY-001` and `ARCH-025-SHOPIFY-002` are architect-accepted Complete, and the sequential execution frontier is `ARCH-025-SHOPIFY-003`. Later tasks remain dependency-gated and are materialised/claimed only through the normal `/moda-task <TASK_ID>` path.

## Problem

`moda-interact/app/services/billing/billing.service.ts` is approximately 2,677 lines and currently combines multiple independently meaningful workflows behind one public class:

- BillingPlan resolution/materialisation from `MerchantPricingPlan`;
- initial Free and Paid activation intent handling;
- hosted plan-change verification fencing;
- local Subscription and Shopify commercial/lifecycle reads;
- merchant recovery-capacity calculation;
- merchant billing-page read composition;
- recovery-credit purchase initiation/provider evidence fencing;
- current BillingPeriod projection/repair;
- provider-to-local Subscription synchronization;
- subscription-ended support notification/translation scheduling.

The objective is maintainability, not behavioural redesign. The current public façade is widely consumed by Shopify routes and tests, so callers must remain unchanged while internal workflow owners are extracted incrementally.

## Goals

- Keep `BillingService` and `billingService` as the stable Shopify application entry point.
- Preserve the current `BillingService` constructor signature and every public method signature.
- Preserve every public export currently exposed from `billing.service.ts`, including compatibility re-exports when implementation moves.
- Extract one coherent billing responsibility per task into bounded modules/services.
- Preserve all provider/network versus Prisma transaction boundaries and current lock order.
- Preserve all current billing lifecycle, CAS/fencing, retry, error-code, provider-evidence and entitlement semantics.
- Add focused tests for each extracted owner while preserving the existing façade regression suite byte-for-byte.
- Make `syncSubscription()` the final coordinator extraction after its subordinate responsibilities have stable owners.

## Non-Goals

ARCH-025 does not authorise:

- changes outside `moda-interact/` implementation code;
- changes to `moda-interact-background/`, Admin, Commerce, Messaging, Shared, Database, Gateway or System Test;
- Prisma schema or migration changes;
- queue/event contract changes;
- Shopify provider protocol changes;
- billing economics, plan rules, credits, retries or error-code changes;
- authorization/authentication changes;
- route API changes;
- introducing a command bus, plugin framework, DI container or generic billing framework;
- replacing the existing billing provider abstraction;
- changing existing test expectations to accommodate the refactor;
- deleting, skipping or weakening existing tests;
- refactoring `recovery-credit-purchase-management.service.ts` except where a later separate architecture explicitly authorises it.

If an implementation task discovers that its required extraction cannot be completed without one of these changes, it must stop and return the dependency/conflict to `moda_architect`.

## Current Architecture

The public façade is:

```text
app/services/billing/billing.service.ts
  BillingService
  billingService
```

Current public methods are grouped as follows:

```text
Activation
  prepareFreeActivation
  preparePaidActivation
  scheduleInitialFreeReconciliationIfCurrent
  completeFreeActivation

Subscription / provider reads
  getSubscription
  getSubscriptionProjection
  getMerchantShopifySubscriptionState
  getMerchantShopifyLifecycleState

Hosted plan-change callback fencing
  getHostedPlanVerificationFence
  recordHostedPlanChangeReturn
  recordHostedPlanVerificationFailure

Merchant billing/capacity reads
  getMerchantRecoveryCapacityState
  getMerchantBillingState

Commands / synchronization
  requestRecoveryCreditPack
  syncSubscription
```

The file also owns substantial private/module logic including `ensureMappedCurrentBillingPeriodProjection`, `resolveOrMaterializeBillingPlan`, `readRecoveryCreditTopUpConfiguration`, `readMerchantPricingPlan`, `mapMerchantShopifySubscription`, activation locks/tokens, recovery-credit provider-evidence helpers and subscription-ended notification persistence.

## Proposed Architecture

The final Shopify billing boundary remains:

```text
routes / application services
        |
        v
BillingService                     compatibility façade
        |
        +--> BillingPeriodProjection
        +--> BillingPlanResolutionService
        +--> SubscriptionReadService
        +--> MerchantRecoveryCapacityReadService
        +--> MerchantBillingReadService
        +--> SubscriptionActivationService
        +--> subscription-locks.ts / billing-retry-policy.ts   shared internal mechanics
        +--> HostedPlanChangeService
        +--> RecoveryCreditPurchaseRequestService
        +--> SubscriptionEndedNotificationService
        +--> SubscriptionSyncService
```

`BillingService` must create/wire these collaborators from the same constructor dependencies already supplied today. No global service locator or new DI framework is permitted.
All collaborator constructors are inert wiring only: they must not perform provider/database I/O, environment discovery or eager Prisma-model access. This is required because the existing regression suite constructs `BillingService` with partial provider/database test doubles tailored to individual methods.

Extracted modules must not import `billing.service.ts`. Dependency direction is one-way from the façade/coordinator into collaborators. Public symbols moved out of the façade file must be re-exported from `billing.service.ts` so existing imports remain valid.

Two tiny repository-internal support modules are deliberate rather than generic frameworks: `subscription-locks.ts` owns the lock SQL shared by activation/hosted/sync, and `billing-retry-policy.ts` owns the existing `INITIAL_BILLING_RETRY_DELAY_MS` constant. They preserve one implementation of mechanics already shared by multiple workflows.

### Compatibility façade invariant

Throughout all eleven tasks, this remains valid without caller migration:

```ts
new BillingService(provider, database, dispatchTranslation)
```

and the singleton remains:

```ts
billingService
```

The following current exports remain available from `app/services/billing/billing.service.ts` with compatible meanings:

```text
BillingService
billingService
deriveBillingPeriodPhase
INITIAL_BILLING_RETRY_DELAY_MS
InitialFreeActivationToken
InitialPaidActivationToken
FreeActivationResult
CompletedFreeActivation
HostedPlanChangeReturnResult
HostedPlanVerificationFence
renderSubscriptionEndedMessage
```

In addition, the frozen regression suite currently invokes the runtime-private method name `resolveOrMaterializeBillingPlan(...)` through a TypeScript cast. ARCH-025 therefore preserves that private method name as a **thin compatibility delegate** to `BillingPlanResolutionService`; it is not a public API, but removing it during this initiative would violate the byte-identical regression contract.

## Regression Baseline

The supplied 1 October 2026 snapshot contains:

```text
tests/unit/services/billing.service.test.ts
```

with:

```text
213 tests
SHA-256: bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4
Known pre-task failure baseline: ARCH025-TEST-001
```

This file is a frozen ARCH-025 regression asset. Attempt 2 of `ARCH-025-SHOPIFY-001` proved that, at exact pre-task commit `b6d1fd6d362f2a6a302a735e0a54abd8ee677782`, the byte-identical file executes 213 tests with 18 date-sensitive failures, and that the submitted extraction commit has the identical 18 failing identifiers. The same differential also proved an identical 24-failure full-suite set. Those facts are recorded durably as `ARCH025-TEST-001` in `docs/development-baseline.md`.

Every ARCH-025 implementation task MUST satisfy all of the following:

1. do not modify `tests/unit/services/billing.service.test.ts`;
2. verify its SHA-256 remains exactly `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`;
3. run the complete frozen façade suite and require that it introduces no failing test identifier outside `ARCH025-TEST-001`; if an upstream change resolves a baseline failure, do not reintroduce it;
4. add a separate focused test file for the newly extracted capability;
5. run the full existing `npm test` suite and introduce no new failure relative to the current pre-task state; when the observed failure set still matches `ARCH025-TEST-001`, reference that baseline instead of rediscovering it;
6. do not add `.skip`, `.only`, `test.todo` or equivalent bypasses to make the task pass;
7. do not weaken production assertions/error handling solely to satisfy extraction tests.

A task with any task-introduced regression in the frozen BillingService suite is not eligible for review. A known `ARCH025-TEST-001` failure is not itself a task regression, but any changed, additional or worsened failure must be investigated.

## Data Model

No schema or migration changes are authorised.

Existing PostgreSQL tables, relationships, uniqueness constraints, BillingPeriod/Subscription lifecycle semantics and entitlement counters remain unchanged.

## Contracts

ARCH-025 introduces no new cross-repository runtime contract.

The principal compatibility contract is the existing in-process `BillingService` façade. Existing Shopify routes and services continue importing from:

```text
app/services/billing/billing.service.ts
```

Extracted collaborator APIs are repository-internal implementation contracts only.

## Consistency and Transactions

Structural extraction must preserve the exact transaction model currently expressed by `BillingService`:

- this is move-only: do not remove, coalesce, reorder or otherwise optimise existing provider/database reads, writes, locks or transactions as incidental cleanup;
- caller-owned transaction helpers stay caller-owned;
- provider/network calls that currently occur before a transaction remain before it;
- provider/network calls must not be moved into Prisma transactions;
- `SELECT ... FOR UPDATE` lock targets and ordering must not change; the shared subscription lock remains `ShopSettings -> Subscription`, and initial Paid finalisation retains the full `ShopSettings -> Subscription -> Shop` order;
- callback/provider fencing compares the same durable facts;
- BillingPeriod projection remains conflict-preserving rather than destructive, including the existing compatible-row update (which currently advances `BillingPeriod.updatedAt`);
- duplicate/replay behaviour remains idempotent;
- initial Paid finalisation remains a participant in the caller-owned `syncSubscription` transaction rather than opening a nested/second transaction;
- normal mapped BillingPeriods use the mapped projection helper, while the existing raw `billingPeriod.upsert` path for UNMAPPED/SYNC_ERROR cycles remains separate;
- notification/translation side effects remain isolated from already committed billing state where they are isolated today; missing durable lifecycle identity still propagates while other notification/dispatch failures remain best-effort.

## Ordering

The eleven tasks execute sequentially because each extraction edits the same compatibility façade and later tasks intentionally consume owners created by earlier tasks.

Do not parallelise sibling ARCH-025 Shopify tasks.

## Failure Handling

Existing error strings/codes and bounded failure results remain stable unless an individual task explicitly identifies a purely internal type move that does not change caller-visible behaviour.

In particular preserve current meanings of:

```text
SubscriptionProjectionStatus
lastSyncErrorCode
PARTNER_API_ERROR
BILLING_PERIOD_PLAN_CONFLICT
INVALID_PAID_PLAN_CONFIGURATION
```

and all current recovery-credit purchase error/admission semantics.

## Scalability

This is a structural refactor only. It must not add provider calls, Prisma round trips, transaction duration, queue work or per-request durable writes relative to the current equivalent path. Existing deliberate rereads/fences (for example the recovery-credit purchase provider and catalogue revalidation reads) must not be coalesced away.

A task that accidentally multiplies Shopify Partner API reads or database work is a behavioural regression.

## Security

No authentication, authorization, tenant isolation or secret-handling boundary changes are authorised.

Extracted services receive server-side dependencies only. No provider credential, Shopify token, whole customer object or billing payload may be newly exposed to browser code or logs.

## Observability

No new observability mechanism is required. Existing log/telemetry semantics remain unchanged. Do not introduce a new generic logger during extraction.

## Infrastructure Assessment

No infrastructure implementation is required. ARCH-025 does not change Render services, public/private routing, worker topology, environment variables, Redis, PostgreSQL infrastructure or deployment configuration.

Therefore no `moda_gateway` task is required.

## Rollout / Migration

Classification: **PRODUCTION / COMPATIBLE ROLLOUT** for behavioural purposes.

No database migration, data backfill, queue drain or cross-service deployment ordering is required. Each accepted task is independently deployable because the public Shopify application façade remains compatible.

Rollback is ordinary code rollback of the affected Shopify application commit; there is no schema rollback.

## Repository Responsibilities

Only one implementation repository participates:

```text
repository: moda-interact
assigned_agent: moda_app
```

The parent workspace contains the architecture/task coordination files. Repository task implementation remains confined to `moda-interact/` plus the assigned parent task report file permitted by the task/VCS protocol.

## Decisions / Tasks

| Task | Outcome | Status | Depends On |
|---|---|---|---|
| ARCH-025-SHOPIFY-001 | Extract current billing-period projection/cycle invariants | Complete | - |
| ARCH-025-SHOPIFY-002 | Extract operational BillingPlan resolution/catalogue reads | Complete | SHOPIFY-001 |
| ARCH-025-SHOPIFY-003 | Extract Subscription/provider read service | Ready | SHOPIFY-002 |
| ARCH-025-SHOPIFY-004 | Extract merchant recovery-capacity read service | Pending | SHOPIFY-003 |
| ARCH-025-SHOPIFY-005 | Extract merchant billing-state read service | Pending | SHOPIFY-004 |
| ARCH-025-SHOPIFY-006 | Extract initial activation workflow | Pending | SHOPIFY-005 |
| ARCH-025-SHOPIFY-007 | Extract hosted plan-change verification workflow | Pending | SHOPIFY-006 |
| ARCH-025-SHOPIFY-008 | Extract recovery-credit purchase request workflow | Pending | SHOPIFY-007 |
| ARCH-025-SHOPIFY-009 | Extract subscription-ended notification workflow | Pending | SHOPIFY-008 |
| ARCH-025-SHOPIFY-010 | Extract initial Paid activation finalisation | Pending | SHOPIFY-009 |
| ARCH-025-SHOPIFY-011 | Extract remaining subscription synchronization coordinator | Pending | SHOPIFY-010 |

Execution graph:

```text
SHOPIFY-001
   |
   v
SHOPIFY-002
   |
   v
SHOPIFY-003
   |
   v
SHOPIFY-004
   |
   v
SHOPIFY-005
   |
   v
SHOPIFY-006
   |
   v
SHOPIFY-007
   |
   v
SHOPIFY-008
   |
   v
SHOPIFY-009
   |
   v
SHOPIFY-010
   |
   v
SHOPIFY-011
```

## System Validation

A separate `moda_system_test` task is **not applicable** to this Shopify-only structural initiative because ARCH-025 introduces no new integrated cross-service behaviour, infrastructure topology, database contract or externally observable product feature.

Architecture completion instead requires every implementation task to preserve the byte-identical 213-test façade asset and introduce no task-only failures beyond the durable `ARCH025-TEST-001` baseline, while also introducing no full-suite regression. This decision does not waive repository-level integration tests already exercised by `npm test`.

## Open Questions

None.

## Change History

- 2026-10-01: Initial agreed Shopify-only BillingService maintainability architecture and eleven-task deterministic extraction sequence defined from the supplied current snapshot.
- 2026-10-01: Meticulous source/task reconciliation tightened hidden helper ownership, preserved the frozen-suite private resolution delegate, introduced single owners for shared lock/retry mechanics, corrected initial-Paid finalisation to remain inside the caller-owned sync transaction, fixed notification/no-contract semantics, preserved deliberate provider/catalogue rereads and raw UNMAPPED/SYNC_ERROR BillingPeriod projection, added explicit Stop Conditions, and made hash validation cross-platform.
- 2026-10-01: SHOPIFY-001 Attempt 2 proved the exact pre-task and submitted commits have identical frozen-suite and full-suite failure identifiers. Corrected the frozen asset count from 127 to 213, established durable baseline `ARCH025-TEST-001`, accepted SHOPIFY-001, and advanced SHOPIFY-002 to Ready.
- 2026-10-01: SHOPIFY-002 Attempt 1 accepted the move-only `BillingPlanResolutionService` extraction at implementation commit `804894cc598d394c7d1f61bc2828c61743d1145f`. The façade retains its frozen private resolver delegate, all observed failures remain within `ARCH025-TEST-001`, and SHOPIFY-003 advances to Ready.
