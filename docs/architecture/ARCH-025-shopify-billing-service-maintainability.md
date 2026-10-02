---
id: ARCH-025
title: Billing service maintainability refactor
status: in_progress
coordinator: moda_architect
created: 2026-10-01
updated: 2026-10-02
---

# ARCH-025: Billing service maintainability refactor

## Status

In Progress.

ARCH-025 now contains two **independent, repository-owned maintainability tranches** under the same billing architecture initiative:

```text
moda-interact/             Shopify BillingService façade
moda-interact-background/  billing subscription reconciliation coordinator
```

The historical architecture filename is retained so the already-materialised Shopify task files keep a stable durable reference. The architecture ID and this document remain authoritative for both tranches.

The Shopify tranche refactors `app/services/billing/billing.service.ts` behind its existing public façade. `ARCH-025-SHOPIFY-001` through `ARCH-025-SHOPIFY-011` are architect-accepted Complete; the Shopify tranche is complete.

The Background tranche refactors `src/services/billing-subscription-reconciliation.service.ts` behind its existing worker/service façade. `ARCH-025-BACKGROUND-001` is Ready; BACKGROUND-002 through BACKGROUND-007 remain dependency-gated.

The two tranches have **no ARCH-025 dependency on one another** and may proceed independently because they modify different repositories and introduce no cross-repository contract change. Within each repository, tasks remain sequential because they progressively extract from one high-churn compatibility façade/coordinator.

## Problem

### Shopify application

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

### Background billing reconciliation

`moda-interact-background/src/services/billing-subscription-reconciliation.service.ts` is approximately 1,900 lines. Its four-method public surface (`activateInitialPaid`, `enqueue`, `reconstruct`, `reconcileJob`) currently contains or directly owns:

- queued-job parsing, durable schedule fencing, state classification and skip logging;
- deterministic queue publication and startup reconstruction;
- one-snapshot provider reconciliation orchestration;
- initial Free/Paid activation and alternate-current-plan convergence;
- reinstall reconciliation;
- Free cycle discovery, pre-close usage flushing and same-plan rollover;
- established plan-change convergence;
- FROZEN/lifecycle replay coordination;
- lifecycle-specific retry/CAS behaviour;
- discount-sync and recovery-capacity-resume side effects;
- shared row-lock helpers.

Several canonical lower-level Background services already exist (`SamePlanBillingPeriodRolloverService`, `ShopifyPlanChangeTransitionService`, `ShopifySubscriptionLifecycleReconciliationService`, `ensureCurrentBillingPeriodProjection`, `shopifyUsageEventPublisherService`). ARCH-025 must increase delegation to those owners rather than create parallel implementations.

The objective in both repositories is maintainability, not behavioural redesign. Existing callers, routes, worker entrypoints, queue contracts and durable billing semantics remain stable while internal owners are extracted incrementally.

## Goals

- Keep `BillingService` and `billingService` as the stable Shopify application entry point.
- Preserve the current `BillingService` constructor signature, every public method signature and every compatibility export already required by the frozen Shopify suite.
- Reduce `BillingSubscriptionReconciliationService` to a queue-facing coordinator while preserving its exact seven-position constructor, four public methods, singleton and helper exports.
- Extract one coherent billing responsibility per task into bounded modules/services.
- Preserve all provider/network versus Prisma transaction boundaries and current lock/CAS behaviour in both repositories.
- Preserve all current billing lifecycle, retry, error-code, provider-evidence and entitlement semantics.
- Preserve the Background invariant that every **successfully parsed** queued job captures exactly one immutable `BackgroundRuntimeConfigSnapshot` immediately after parsing and before durable context loading; malformed input still fails during parsing before runtime-config/database/provider work.
- Preserve normal queued reconciliation as one `getSubscriptionReconciliationSnapshot(...)` call per accepted job and preserve reinstall's distinct `getActiveSubscription(...)` path.
- Reuse existing Background rollover, plan-change, lifecycle, projection, usage-publishing, discount and capacity-resume owners instead of duplicating their behaviour.
- Add focused tests for each extracted owner while preserving both large regression suites byte-for-byte.
- Make Shopify `syncSubscription()` and Background `reconcileJob()` the final coordinator extractions in their respective tranches.

## Non-Goals

ARCH-025 does not authorise:

- implementation changes outside `moda-interact/` and `moda-interact-background/`;
- CheckoutRecovery, Admin pricing-plan authoring, Commerce Studio, Messaging, Shared, Database, Gateway or System Test feature work;
- Prisma schema or migration changes;
- Shared queue/event contract changes;
- Shopify provider protocol changes;
- billing economics, plan rules, credits, retry intervals, error codes or durable lifecycle semantics;
- authentication/authorization changes;
- Shopify route or Background worker-entrypoint API changes;
- changing worker deployment topology, environment variables or Render configuration;
- introducing a command bus, plugin framework, DI container or generic billing/retry framework;
- replacing existing provider abstractions or canonical lifecycle/rollover/plan-change services;
- changing existing test expectations to accommodate refactoring;
- deleting, skipping or weakening existing tests;
- opportunistically fixing questionable legacy behaviour discovered during extraction;
- refactoring `recovery-credit-purchase-management.service.ts` except where a later separate architecture explicitly authorises it.

If an implementation task discovers that a safe extraction requires one of these changes, it must stop and return the dependency/conflict to `moda_architect`.

## Current Architecture

### Shopify application

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

### Background billing reconciliation

The worker/service façade is:

```text
src/services/billing-subscription-reconciliation.service.ts
  BillingSubscriptionReconciliationService
  billingSubscriptionReconciliationService
```

Current public methods/exports that must remain compatible are:

```text
BillingSubscriptionReconciliationService
billingSubscriptionReconciliationService
activateInitialPaid(...)
enqueue(...)
reconstruct()
reconcileJob(...)
InitialActivationPlan
FREE_CYCLE_DISCOVERY_RETRY_MS
ROLLOVER_RETRY_MS
nextSubscriptionReconcileAt(...)
createSubscriptionReconcilePayload(...)
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS  (compatibility re-export)
```

The current constructor is positional and is asserted by `tests/unit/runtime/entrypoint-isolation.test.ts`:

```text
(database, partner, queue, logger, now, runtimeConfig, discountQueue)
```

`src/entrypoints/billing.ts` and `src/services/billing-reconciliation.service.ts` are callers. The latter constructs this service solely to invoke `activateInitialPaid(...)`, which validates initial activation as a first-class extraction seam.

## Proposed Architecture

### Shopify application target

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

### Background target

```text
billing worker / BillingReconciliationService
        |
        v
BillingSubscriptionReconciliationService       compatibility coordinator
        |
        +--> classification.ts                  pure job/state classification
        +--> reconciliation-queue.service.ts    deterministic enqueue/reconstruction
        +--> initial-activation-reconciliation.service.ts
        |       +--> reconciliation-timing.ts
        |       +--> locking.ts
        |       +--> discount-sync-publisher.service.ts
        +--> reinstall-reconciliation.service.ts
        +--> billing-cycle-reconciliation.service.ts
        |       +--> SamePlanBillingPeriodRolloverService (existing)
        |       +--> shopifyUsageEventPublisherService (existing)
        +--> established-plan-change-reconciliation.service.ts
        |       +--> ShopifyPlanChangeTransitionService (existing)
        +--> reconciliation-context.ts          bounded durable snapshot/current-plan loading
        +--> ShopifySubscriptionLifecycleReconciliationService (existing)
```

The final `reconcileJob()` flow is:

```text
parse job
  -> capture exactly one BackgroundRuntimeConfigSnapshot
  -> load current durable shop/subscription context
  -> pure classify / reject stale or ineligible work
  -> load current local plan when required
  -> request exactly one provider reconciliation snapshot when required
  -> run existing lifecycle reconciliation with the captured runtime config
  -> delegate using the same source ordering to the applicable extracted owner(s)
  -> preserve the legacy final provider-plan dispatch/fallthrough (including FROZEN `continue`)
  -> publish only the committed durable next schedule
```

Reinstall intentionally remains separate from the normal snapshot path and continues to call `partner.getActiveSubscription(...)` once. Lifecycle retry decisions stay with the owning handler; the queue collaborator only publishes a requested durable schedule and does not become a generic retry-policy engine.

The final provider-plan lookup/branch dispatch remains bounded coordinator orchestration rather than being hidden inside an initial-activation-only entry point. This preserves the current source ordering shared by initial activation, established plan change and the legacy FROZEN lifecycle `continue` fallthrough. In particular, ARCH-025 does not add a new `kind === initial-activation` guard around the existing final Free/Paid/mismatch/`applyOtherCurrentPlan` predicates.

All collaborator constructors in both repositories are inert wiring only: no provider/database I/O, environment discovery or eager Prisma-model access.

## Regression Baseline

### Shopify frozen façade asset

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

### Background frozen reconciliation asset

The 2 October 2026 source snapshot contains:

```text
moda-interact-background/tests/unit/services/billing-subscription-reconciliation.service.test.ts
98 tests
SHA-256: 0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239
```

This file is a frozen ARCH-025 Background regression asset. Every Background task MUST:

1. leave it byte-for-byte unchanged;
2. verify that SHA-256 exactly;
3. run the complete 98-test file and require all 98 tests to pass;
4. add separate focused tests for the newly extracted owner;
5. run `tests/unit/runtime/entrypoint-isolation.test.ts` to protect the billing-worker constructor/entrypoint contract;
6. run the full existing `npm test` suite and introduce no regression;
7. add no `.skip`, `.only`, `test.todo` or equivalent bypass;
8. not weaken production assertions/error handling to satisfy extraction tests.

The supplied ZIP intentionally has no `moda-interact-background/node_modules`, so this architecture definition does **not** claim that the 98-test Background suite was executed while authoring these tasks. Runtime validation belongs to each prepared implementation worktree.

## Data Model

No schema or migration changes are authorised.

Existing PostgreSQL tables, relationships, uniqueness constraints, BillingPeriod/Subscription lifecycle semantics and entitlement counters remain unchanged.

## Contracts

ARCH-025 introduces no new cross-repository runtime contract.

The Shopify compatibility contract remains `BillingService` in `app/services/billing/billing.service.ts`.

The Background compatibility contract remains `BillingSubscriptionReconciliationService` in `src/services/billing-subscription-reconciliation.service.ts`, including its constructor, four public methods, singleton and public helper/type exports. Existing imports in `src/entrypoints/billing.ts` and `src/services/billing-reconciliation.service.ts` remain valid throughout the structural phase.

The Shared billing reconciliation queue contract remains owned by `@modainteract/moda-interact-shared/billing`; no ARCH-025 task may redefine or version it locally. Extracted collaborator APIs are repository-internal implementation contracts only.

## Consistency and Transactions

### Shopify

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

### Background

Structural extraction MUST preserve:

- exact `expectedNextReconcileAt` stale-job authority/CAS fencing;
- deterministic queue job identity derived from `subscriptionId` + `expectedNextReconcileAt`;
- current queue options and delayed scheduling;
- after `parseBillingSubscriptionReconcileJob(...)` succeeds, exactly one immutable runtime-config snapshot is captured before durable context loading; malformed input performs no runtime-config/database/provider work;
- normal reconciliation's single `getSubscriptionReconciliationSnapshot(...)` call and snapshot reuse;
- reinstall's distinct single `getActiveSubscription(...)` call;
- current provider/network versus transaction boundaries;
- current clock-read boundaries as well as database/provider boundaries: do not coalesce, hoist or reorder repeated `now()` reads where the source currently reads the clock separately, especially around drain-window, period-boundary, retry and queue-delay decisions;
- every current `SELECT ... FOR UPDATE` target/order per lifecycle rather than imposing one global lock order;
- existing `updateMany` CAS predicates and no-op behaviour on stale source state;
- existing structured-log event names, levels, bounded field sets and emission boundaries/order relative to the I/O they describe;
- post-commit/best-effort discount-sync and recovery-capacity-resume isolation where they are best-effort today;
- current pre-close usage-publish-before-period-boundary ordering;
- existing canonical `SamePlanBillingPeriodRolloverService`, `ShopifyPlanChangeTransitionService`, `ShopifySubscriptionLifecycleReconciliationService` and `ensureCurrentBillingPeriodProjection` transaction ownership.

This is move-only refactoring. Do not remove, coalesce, reorder or "optimise" existing provider/database calls, locks, transactions or durable rereads merely because code is moved.

## Ordering

The two repository tranches are independent and are not serialized against one another:

```text
Shopify:    SHOPIFY-001 -> ... -> SHOPIFY-011
Background: BACKGROUND-001 -> ... -> BACKGROUND-007
```

Within each repository the tasks execute sequentially because each extraction edits the same compatibility façade/coordinator and later tasks consume capabilities established by earlier tasks.

Do not parallelise sibling ARCH-025 tasks within the same repository.

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

For Background, preserve the current meaning and retry/fail-closed handling of at least:

```text
PARTNER_API_ERROR
PROVIDER_STATE_UNRESOLVED
MISSING_BILLING_CYCLE
MISSING_USAGE_METER
INVALID_INCLUDED_ALLOWANCE
PENDING_PLAN_HANDLE_MISMATCH
UNSUPPORTED_PAID_TRIAL
UNMAPPED_PLAN_HANDLE
UNEXPECTED_IMMEDIATE_PLAN_CHANGE
BILLING_PERIOD_PLAN_CONFLICT
PRE_CLOSE_USAGE_FLUSH_FAILED
PERIOD_ALIGNMENT_REQUIRED
PROVIDER_CYCLE_LAG
```

Lifecycle-specific retry decisions remain with their owning handlers; do not create a generic retry service that centralises business policy.

## Scalability

This is a structural refactor only. It must not add provider calls, Prisma round trips, transaction duration, queue work or per-request durable writes relative to the current equivalent path. Existing deliberate rereads/fences (for example the recovery-credit purchase provider and catalogue revalidation reads) must not be coalesced away.

A task that accidentally multiplies Shopify Partner API reads or database work is a behavioural regression.

For Background, the common hot path must not gain additional provider calls, database round trips, queue publications or transaction duration. In particular, normal accepted jobs continue to acquire at most one `getSubscriptionReconciliationSnapshot(...)` and reuse it; reinstall continues its separate single `getActiveSubscription(...)` read. Queue identity, delayed scheduling and startup reconstruction cardinality remain unchanged.

## Security

No authentication, authorization, tenant isolation or secret-handling boundary changes are authorised.

Extracted services receive server-side dependencies only. No provider credential, Shopify token, whole customer object or billing payload may be newly exposed to browser code or logs.

Background extraction must likewise keep provider credentials, Shopify tokens and whole provider/customer payloads out of new logs and preserve tenant/shop scoping on every durable lookup/mutation.

## Observability

No new observability mechanism is required. Existing log/telemetry semantics remain unchanged. Do not introduce a new generic logger during extraction.

Background already uses the canonical Shared structured logger. Preserve existing `billing.subscription_reconciliation.*` event meanings and bounded identifiers across extraction, including job start/finish, enqueue failure, provider failure, reinstall outcomes, pre-close publish failure, rollover retry and unsupported Paid trial. Do not introduce a competing logger or newly log provider/customer payloads.

## Infrastructure Assessment

No infrastructure implementation is required. ARCH-025 does not change Render services, public/private routing, worker topology, environment variables, Redis, PostgreSQL infrastructure or deployment configuration.

Therefore no `moda_gateway` task is required.

## Rollout / Migration

Classification: **PRODUCTION / COMPATIBLE ROLLOUT** for behavioural purposes.

No database migration, Shared publication, queue drain, infrastructure change or coordinated cross-repository deployment is required. Shopify and Background tasks are independently deployable because their existing public/worker façades remain compatible.

Rollback is ordinary code rollback of the affected repository commit; there is no schema rollback.

## Repository Responsibilities

Two implementation repositories participate, independently:

```text
repository: moda-interact
assigned_agent: moda_app
scope: Shopify BillingService tranche

repository: moda-interact-background
assigned_agent: moda_background
scope: billing subscription reconciliation tranche
```

The parent workspace owns architecture/task coordination files. Repository implementation remains confined to the assigned implementation repository plus the assigned parent task report file permitted by the task/VCS protocol. No ARCH-025 task grants either repository agent ownership of the other repository.

## Decisions / Tasks

### Shopify tranche

| Task | Outcome | Status | Depends On |
|---|---|---|---|
| ARCH-025-SHOPIFY-001 | Extract current billing-period projection/cycle invariants | Complete | - |
| ARCH-025-SHOPIFY-002 | Extract operational BillingPlan resolution/catalogue reads | Complete | SHOPIFY-001 |
| ARCH-025-SHOPIFY-003 | Extract Subscription/provider read service | Complete | SHOPIFY-002 |
| ARCH-025-SHOPIFY-004 | Extract merchant recovery-capacity read service | Complete | SHOPIFY-003 |
| ARCH-025-SHOPIFY-005 | Extract merchant billing-state read service | Complete | SHOPIFY-004 |
| ARCH-025-SHOPIFY-006 | Extract initial activation workflow | Complete | SHOPIFY-005 |
| ARCH-025-SHOPIFY-007 | Extract hosted plan-change verification workflow | Complete | SHOPIFY-006 |
| ARCH-025-SHOPIFY-008 | Extract recovery-credit purchase request workflow | Complete | SHOPIFY-007 |
| ARCH-025-SHOPIFY-009 | Extract subscription-ended notification workflow | Complete | SHOPIFY-008 |
| ARCH-025-SHOPIFY-010 | Extract initial Paid activation finalisation | Complete | SHOPIFY-009 |
| ARCH-025-SHOPIFY-011 | Extract remaining subscription synchronization coordinator | Complete | SHOPIFY-010 |

### Background tranche

| Task | Outcome | Status | Depends On |
|---|---|---|---|
| ARCH-025-BACKGROUND-001 | Extract pure reconciliation classification | Ready | - |
| ARCH-025-BACKGROUND-002 | Extract queue publication and startup reconstruction | Pending | BACKGROUND-001 |
| ARCH-025-BACKGROUND-003 | Extract initial activation reconciliation | Pending | BACKGROUND-002 |
| ARCH-025-BACKGROUND-004 | Extract reinstall reconciliation | Pending | BACKGROUND-003 |
| ARCH-025-BACKGROUND-005 | Extract billing-cycle/pre-close/rollover reconciliation | Pending | BACKGROUND-004 |
| ARCH-025-BACKGROUND-006 | Extract established plan-change reconciliation | Pending | BACKGROUND-005 |
| ARCH-025-BACKGROUND-007 | Reduce `reconcileJob()` to bounded context/coordinator flow | Pending | BACKGROUND-006 |

Execution graph:

```text
SHOPIFY-001 -> ... -> SHOPIFY-010 -> SHOPIFY-011

BACKGROUND-001 -> BACKGROUND-002 -> BACKGROUND-003 -> BACKGROUND-004
      -> BACKGROUND-005 -> BACKGROUND-006 -> BACKGROUND-007
```

There is deliberately no dependency edge between the two repository tranches.

## System Validation

A separate `moda_system_test` task is **not applicable** to this structural maintainability initiative because ARCH-025 introduces no new cross-service contract, infrastructure topology, schema, queue protocol or externally observable product behaviour.

Architecture completion instead requires both repository tranches to preserve their frozen regression assets and introduce no full-suite regression, while each extracted owner gains focused tests. For Shopify, the durable `ARCH025-TEST-001` baseline remains authoritative; for Background, all 98 frozen reconciliation tests are required to pass. This does not waive repository-level integration/runtime validation already exercised by `npm test` or the production build.

## Open Questions

None.

## Change History

- 2026-10-02: SHOPIFY-011 Attempt 2 accepted the report-only reconciliation for the final Shopify sync-coordinator extraction at reviewed implementation commit `3e96f68decc0051aefa9dfbb53101a3661895a9b` and published parent report tip `ac475108c5ec5326d14cbc151d2825786b4b008b`. `BillingService.syncSubscription()` is a thin delegate, the provider-to-local coordinator preserves the accepted provider/transaction/locking/projection semantics, and the full Shopify tranche is now Complete. ARCH-025 remains In Progress because the independent Background tranche is still active.
- 2026-10-02: Deep Background task-coherence review tightened parse-before-runtime-config semantics, clock/log preservation, reconstruction count semantics, cycle error-clearing distinctions, exact current-plan eligibility gates, reinstall pre-transaction rereads and the legacy FROZEN `continue` provider-plan fallthrough. Kept the final provider-plan lookup/branch dispatch as bounded coordinator orchestration so accepted lifecycle-service interfaces remain sufficient through BACKGROUND-007.
- 2026-10-02: Extended ARCH-025 with an independent Background billing-subscription reconciliation maintainability tranche. Added seven sequential `moda_background` tasks, froze the 98-test reconciliation regression asset, preserved worker constructor/entrypoint and provider-call invariants, and kept lifecycle-specific retries with their owning handlers rather than creating a generic retry service.
- 2026-10-01: Initial agreed Shopify-only BillingService maintainability architecture and eleven-task deterministic extraction sequence defined from the supplied current snapshot.
- 2026-10-01: Meticulous source/task reconciliation tightened hidden helper ownership, preserved the frozen-suite private resolution delegate, introduced single owners for shared lock/retry mechanics, corrected initial-Paid finalisation to remain inside the caller-owned sync transaction, fixed notification/no-contract semantics, preserved deliberate provider/catalogue rereads and raw UNMAPPED/SYNC_ERROR BillingPeriod projection, added explicit Stop Conditions, and made hash validation cross-platform.
- 2026-10-01: SHOPIFY-001 Attempt 2 proved the exact pre-task and submitted commits have identical frozen-suite and full-suite failure identifiers. Corrected the frozen asset count from 127 to 213, established durable baseline `ARCH025-TEST-001`, accepted SHOPIFY-001, and advanced SHOPIFY-002 to Ready.
- 2026-10-01: SHOPIFY-002 Attempt 1 accepted the move-only `BillingPlanResolutionService` extraction at implementation commit `804894cc598d394c7d1f61bc2828c61743d1145f`. The façade retains its frozen private resolver delegate, all observed failures remain within `ARCH025-TEST-001`, and SHOPIFY-003 advances to Ready.
- 2026-10-01: SHOPIFY-003 Attempt 2 accepted the isolated `SubscriptionReadService` extraction at implementation commit `ba0380e7688930277e9e075610ac915a256eec1d`; task-local dependency installation reproduced only `ARCH025-TEST-001`, and SHOPIFY-004 advanced to Ready.
- 2026-10-01: SHOPIFY-004 Attempt 1 accepted the move-only `MerchantRecoveryCapacityReadService` extraction at implementation commit `350dedbf61290a01bf3edba642de64cc8482c811`. Capacity precedence, blocker semantics, paid-period integrity and SHOPIFY-002 top-up catalogue reuse are unchanged; all observed failures remain within `ARCH025-TEST-001`, and SHOPIFY-005 advances to Ready.
- 2026-10-01: SHOPIFY-005 Attempt 1 accepted the move-only `MerchantBillingReadService` extraction at implementation commit `28b7cc065035d8bc0fe81a30208c33d770930b08`. Supplied commercial-state reuse, the single provider-read fallback, exact-cycle/phase eligibility, billing-page composition and SHOPIFY-002 catalogue reuse are unchanged; all observed failures remain within `ARCH025-TEST-001`, and SHOPIFY-006 advances to Ready.
- 2026-10-02: SHOPIFY-006 Attempt 1 accepted the move-only `SubscriptionActivationService` extraction at implementation commit `e0b5ec0644239d74b44b0f492270440de0dae5f0`. Free/Paid activation intent, guarded Free reconciliation/completion, token fencing, shared lock order and retry timing are unchanged; initial Paid durable finalisation remains in `syncSubscription()`, all observed failures remain within `ARCH025-TEST-001`, and SHOPIFY-007 advances to Ready.
- 2026-10-02: SHOPIFY-007 Attempt 1 accepted the move-only `HostedPlanChangeService` extraction at implementation commit `a72bd153f3cafd0e8301d64172421cfe066b801b`. Complete durable-fence comparison, shared lock order, pending/current/mismatch/no-active outcomes and `PARTNER_API_ERROR` retry semantics are unchanged; the callback route and SHOPIFY-006 shared lock/retry modules remain untouched, all observed failures remain within `ARCH025-TEST-001`, and SHOPIFY-008 advances to Ready.
- 2026-10-02: SHOPIFY-008 Attempt 1 accepted the move-only `RecoveryCreditPurchaseRequestService` extraction at implementation commit `96f7db9e437b9732ba0f2b4186fa9306e72dec97`. The exact two provider lifecycle snapshots, two catalogue reads, provider-before-transaction boundary, Serializable Subscription locking/revalidation, idempotency/single-flight behavior and ignored extra runtime pricing payload semantics are unchanged; all observed failures remain within `ARCH025-TEST-001`, and SHOPIFY-009 advances to Ready.
- 2026-10-02: SHOPIFY-009 Attempt 2 accepted the report-only reconciliation for the move-only `SubscriptionEndedNotificationService` extraction at reviewed implementation task commit `209a36138dd438815c3ee360298a97db6d2d6f85`. Lifecycle/source-key identity, support persistence, translation dispatch timing and missing-identity propagation remain unchanged; Attempt 2 introduced no source/test delta, the implementation main merge contains the reviewed task commit without additional file changes, and SHOPIFY-010 advances to Ready.
- 2026-10-02: SHOPIFY-010 Attempt 1 accepted the initial Paid activation finalisation extraction at final implementation commit `b3f0733388f5b2d83d259a61a4319eb15448af45` (production extraction introduced by `9c039a87f98ff3b8c0f51bb9fd9b4552855fda44`; final commit adds focused failure-identity coverage only). The caller-owned `syncSubscription()` transaction, stale-token fence, `ShopSettings -> Subscription -> Shop` lock order, branch-specific error precedence, exact BillingPeriod/counter/lifetime predicates and atomic success projection are preserved; no provider call or nested transaction was introduced, all observed failures remain within `ARCH025-TEST-001`, and SHOPIFY-011 advances to Ready.
