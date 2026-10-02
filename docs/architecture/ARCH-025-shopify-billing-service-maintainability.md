---
id: ARCH-025
title: Runtime and Admin maintainability refactor
status: in_progress
coordinator: moda_architect
created: 2026-10-01
updated: 2026-10-02
---

# ARCH-025: Runtime and Admin maintainability refactor

## Status

In Progress.

ARCH-025 now contains four **independent maintainability sub-tranches** across three repository owners:

```text
moda-interact/             Shopify BillingService façade
moda-interact-background/  billing subscription reconciliation coordinator
moda-interact-background/  CheckoutRecoveryService lifecycle façade
moda-interact-admin/       MerchantPricingPlanBuilder wizard
```

The historical architecture filename is retained so already-materialised task files keep a stable durable reference. The architecture ID and this document remain authoritative for all ARCH-025 tranches.

The Shopify tranche refactors `app/services/billing/billing.service.ts` behind its existing public façade. `ARCH-025-SHOPIFY-001` through `ARCH-025-SHOPIFY-011` are architect-accepted Complete; the Shopify tranche is complete.

The first Background tranche refactors `src/services/billing-subscription-reconciliation.service.ts` behind its existing worker/service façade. `ARCH-025-BACKGROUND-001` is architect-accepted Complete; `ARCH-025-BACKGROUND-002` is Ready and BACKGROUND-003 through BACKGROUND-007 remain dependency-gated. Full-suite no-regression evidence is governed by `ARCH025-BACKGROUND-TEST-001`.

The second Background tranche refactors `src/services/checkout-recovery.service.ts` behind its existing worker/service façade. `ARCH-025-BACKGROUND-008` is Ready; BACKGROUND-009 through BACKGROUND-015 remain dependency-gated.

The Admin tranche refactors `src/components/admin/merchant/merchant-pricing-plan-builder.tsx` behind its unchanged exported React component/form boundary. All ARCH-024 Admin model-assignment work is integrated in the reviewed baseline. `ARCH-025-ADMIN-001` is Ready; ADMIN-002 through ADMIN-008 remain dependency-gated.

There is deliberately **no dependency edge between the four sub-tranches**. They modify different high-churn files across three repositories and may proceed independently; each chain remains sequential internally so accepted extraction interfaces are stable before the next extraction builds on them.

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

### Background checkout recovery

`moda-interact-background/src/services/checkout-recovery.service.ts` is approximately 1,579 lines and exposes a worker-facing compatibility surface spanning several independently meaningful recovery lifecycles:

- checkout-created/update/cart contract handling and activity correlation;
- matured pending-candidate materialisation from current Shopify data;
- durable CheckoutRecovery creation/generation and customer association;
- initial proactive recovery outreach, billing admission/revalidation and confirmed-send finalisation;
- no-response follow-up execution;
- order completion correlation, pending-candidate cancellation and checkout-scoped order tombstones;
- durable recovery-capacity blocking/resume/terminalisation;
- CommerceAgent recovery/conversation read-model assembly.

ARCH-024 Background work is integrated in the reviewed baseline: `RecoveryAgentContext` includes canonical `shopId`, both agent-context readers return the durable Shop identity, and the production Commerce model runtime changes are already present. CheckoutRecovery extraction therefore proceeds against the post-ARCH-024 source shape.

Canonical adjacent owners already exist and remain authoritative: `RecoveryBillingService`, `RecoveryOutreachAttemptService`, `recoveryOutreachFollowUpService`, `RecoveryPolicyService`, `PendingRecoveryCandidateService`, `ShopExecutionEligibilityService`, `AbandonedCheckoutLookupService`, `RecoveryCapacityResumeService`, `OutboundWhatsAppAdmissionService`, `ConversationService`, `ConversationMessageService` and `WhatsAppTemplateSelectorService`. ARCH-025 must increase delegation to these owners rather than create a second billing, queue, candidate-correlation, conversation or WhatsApp-send stack.

### Admin merchant pricing-plan builder

`moda-interact-admin/src/components/admin/merchant/merchant-pricing-plan-builder.tsx` is approximately 1,553 lines and combines seven wizard screens with a large cross-step draft, local transition rules and several derived read models:

- plan identity/status, Commerce-model assignment and supported-feature/Merchant Knowledge configuration;
- create/edit catalogue placement semantics;
- Shopify recurring pricing and recovery-meter configuration;
- usage-event/tier editing;
- English merchant content/highlight editing;
- portfolio economics presentation and SUPER_ADMIN override request state;
- translation workbook retention/validation and final review/submission;
- navigation gating, hidden form payload composition and final submit eligibility.

ARCH-024 Admin model-assignment work is integrated in the reviewed baseline: the draft contains `commerceModelId`, `Use Platform default` is supported, and a saved model that is no longer selectable remains visible as a repairable current value. Existing policy/validation modules under `src/lib/admin/merchant/` remain canonical and must not be duplicated inside the UI controller.

The current security suite intentionally reads the builder source and asserts product/security UI invariants. ADMIN-001 therefore makes those assertions extraction-safe by scanning the bounded builder module set without deleting or weakening them before JSX begins moving into child modules.

The objective across all participating repositories is maintainability, not behavioural redesign. Existing callers, routes, worker entrypoints, form/action contracts, queue contracts, durable billing/recovery semantics and Admin product policy remain stable while internal owners are extracted incrementally.

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
- Add focused tests for each extracted owner while preserving the frozen regression assets byte-for-byte.
- Keep `CheckoutRecoveryService`, `checkoutRecoveryService`, its one-argument `RecoveryBillingService` constructor dependency, every current public method and the current exported result types compatible throughout the structural phase.
- Preserve checkout-scoped serialization, order-processed tombstones, recovery generation ordering, durable capacity-block state and deterministic outreach idempotency keys.
- Preserve the post-ARCH-024 `RecoveryAgentContext` shape, including canonical `shopId`, shop domain and bounded conversation-history semantics.
- Reuse the existing recovery billing, outreach-attempt, follow-up scheduling, policy, candidate-correlation, eligibility, checkout lookup, capacity-resume, outbound admission, conversation and template-selection owners.
- Keep `MerchantPricingPlanBuilder` at its existing module path with the same props, form action, hidden-field contract, seven step labels/order and final submit semantics throughout the Admin structural phase.
- Move local Admin draft/state transitions into one typed reducer/controller without moving server/domain validation into React state.
- Preserve create-versus-edit plan-kind/placement behaviour, exact navigation gates, economics-override invalidation semantics, Merchant Knowledge product-policy inclusion, unavailable-current-Commerce-model repair, translation-retention rules and the always-mounted translation workbook.
- Keep existing pure/domain owners (`pricing-plan-builder.ts`, `pricing-builder-payload.ts`, `pricing-economics*`, `pricing-translations.ts`, `pricing-plan-feature-controls.ts`) authoritative.
- Make Shopify `syncSubscription()`, Background `reconcileJob()`, the final `CheckoutRecoveryService` façade reduction and the final `MerchantPricingPlanBuilder` wizard-shell reduction the terminal extraction steps in their respective sub-tranches.

## Non-Goals

ARCH-025 does not authorise:

- implementation changes outside `moda-interact/`, `moda-interact-background/` and `moda-interact-admin/`;
- Admin merchant-pricing-plan server-action transaction refactoring, QueueMonitor refactoring, other Admin UI refactors, Commerce Studio, Messaging, Shared, Database, Gateway or System Test feature work;
- redesigning CheckoutRecovery product behaviour, outreach policy, recovery capacity economics, candidate/order correlation semantics or CommerceAgent context contracts;
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
- refactoring `recovery-credit-purchase-management.service.ts` except where a later separate architecture explicitly authorises it;
- refactoring the canonical adjacent recovery services themselves except for import/wiring changes explicitly required by an ARCH-025 CheckoutRecovery task;
- introducing a second WhatsApp send path, billing reservation implementation, pending-candidate store, recovery queue framework or generic repository/service framework.
- changing `mutateMerchantPricingPlanAction`, server-side pricing/economics/translation policy or SUPER_ADMIN authorization as part of the builder extraction;
- introducing a new React form framework, client-side domain validation engine, global state store or UI component framework solely for this refactor;
- conditionally unmounting `MerchantPricingTranslationWorkbook` during normal wizard navigation or otherwise discarding its local workbook/upload state;

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

### Background checkout recovery

The worker/service façade is:

```text
src/services/checkout-recovery.service.ts
  CheckoutRecoveryService
  checkoutRecoveryService
```

The current public compatibility surface that must remain callable throughout the structural phase is:

```text
handleCheckoutCreatedContract(...)
materializeMaturedCandidate(...)
recordExternalActivity(...)
handleCheckoutUpdatedContract(...)
handleCartActivityContract(...)
handleOrderCompletedContract(...)
upsertRecovery(...)
attachCustomer(...)
resolveRecipient(...)
markRecoveryMessageSent(...)
handleOrderCompleted(...)
handleCheckoutCreated(...)
processRecoveryOutreachFollowUp(...)
markRecoveryCapacityBlocked(...)
resumeCapacityBlockedRecovery(...)
getAgentContext(...)
getAgentContextForStandaloneConversation(...)
MaturedCandidateMaterializationResult
CheckoutRefreshResult
```

The constructor remains:

```text
(billingService: RecoveryBillingService = recoveryBillingService)
```

Direct worker callers currently include checkout, order, pending-candidate, recovery-follow-up, capacity-resume and WhatsApp flows. Existing worker entrypoints must continue calling the `checkoutRecoveryService` singleton during the structural phase.

### Admin merchant pricing-plan builder

The public Admin UI boundary remains:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
  MerchantPricingPlanBuilder
```

The current component owns these seven ordered steps:

```text
0 Plan
1 Catalogue placement
2 Shopify pricing
3 Usage events
4 Merchant content
5 Portfolio economics
6 Translations & review
```

Important current transition semantics that are part of the compatibility contract include:

- forward navigation is only one step at a time; backward navigation is always permitted;
- step 3 blocks forward navigation only for an unbounded zero-cost fixed usage event;
- step 4 blocks forward navigation only when merchant content is invalid;
- step 5 blocks forward navigation until economics passes or an allowed override has a valid reason;
- final submission is stricter than step navigation and additionally requires required fields, valid Merchant Knowledge configuration, a bounded admin reason and retained/validated translations;
- create-time FREE/PAID changes recompute catalogue placement, while edit-time plan-kind changes do not;
- FREE payload submission nulls the recovery usage-event handle without erasing the retained local draft value;
- economics override enablement resets only when the current economics configuration key changes (handle, credits, currency, recurring price, effective placement, minimum upgrade premium or serialized usage events);
- Merchant Knowledge is always submitted in `supportedFeatureKeys` by product policy while its configuration is independently validated;
- the current unavailable Commerce model stays visible/selectable until explicitly repaired;
- `MerchantPricingTranslationWorkbook` remains mounted and is hidden outside step 6 so its local uploaded-workbook state survives navigation.

The form continues to submit to `mutateMerchantPricingPlanAction` with hidden `payload`, `translationJson`, `economicsOverrideRequested` and `economicsOverrideReason` fields. Server-side action validation/transactions remain outside this tranche.

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

### Admin target

The final Admin boundary remains the existing exported component while internal draft/state and substantial step markup move behind it:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
  MerchantPricingPlanBuilder                     form shell + hidden fields + navigation

src/components/admin/merchant/merchant-pricing-plan-builder/
  merchant-pricing-plan-draft.ts                 typed draft, pure reducer/actions/selectors
  use-merchant-pricing-plan-draft.ts             thin React wiring around the pure draft controller
  plan-step.tsx                                  identity/status/model/features/knowledge
  catalogue-placement-step.tsx                   placement presentation
  shopify-pricing-step.tsx                       recovery meter/currency/recurring price
  usage-events-step.tsx                          usage events + tiers
  merchant-content-step.tsx                      description/highlights
  portfolio-economics-step.tsx                   economics presentation/override controls
  translations-review-step.tsx                   mounted workbook + final review/admin reason/submit UI
```

The pure draft/controller owns local UI transitions only. It may call existing canonical pure helpers but must not duplicate server-side payload validation, economics policy, translation validation or feature policy. Step components receive bounded props/actions and do not independently reconstruct the complete draft or hidden submission payload.

ADMIN-001 also changes the existing source-based security test harness so builder assertions read the bounded builder shell + `merchant-pricing-plan-builder/**` module set. Assertion names/patterns remain semantically equivalent; this is test-location adaptation, not a behavioural expectation change. After ADMIN-001 that security test becomes immutable for ADMIN-002..008.

A deep pre-execution coherence review further establishes ADMIN-001 as the complete controller-contract task: all state mutations and derived selectors required by ADMIN-002..008 must exist before ADMIN-001 is accepted, with later tasks consume-only. The pure draft module remains directly testable by the repository plain-Node TypeScript runner; event/highlight identity generation and economics-override clearing stay at their current hook/UI impurity boundaries. The extraction-safe security module set also participates in the existing ARCH-014 forbidden operational-dependency scan, so moving JSX cannot create a blind spot.

The Admin chain is independent of the Shopify and Background chains. Within ADMIN-001..008, tasks are sequential because each extraction relies on the accepted typed draft/controller and previously established child-module contracts.

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
146 tests
SHA-256: 0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239
```

This file is frozen for BACKGROUND-001..007. Every reconciliation-chain task MUST leave it byte-for-byte unchanged, verify the SHA-256, run the complete file, add separate focused tests for the extracted owner, run `tests/unit/runtime/entrypoint-isolation.test.ts`, run the full existing `npm test` suite without regression, and add no test bypasses or weakened production assertions.

BACKGROUND-001 Attempt 2 established durable development baseline `ARCH025-BACKGROUND-TEST-001` for the full `moda-interact-background` suite by comparing exact pre-task commit `670fbad4d52308c96ef41a6a4d29116f1ad42f1a` with submitted commit `b3c7a1264a22baf498b14916a341686a751de869` under the same dependency/environment state. Later ARCH-025 Background tasks may reference that baseline only when they introduce no new failing test or suite identity; if an upstream/environment repair resolves a baseline failure, tasks must not recreate it.

### Background frozen CheckoutRecovery assets

The integrated post-ARCH-024 source snapshot freezes these four existing CheckoutRecovery regression files for BACKGROUND-008..015:

```text
tests/unit/services/matured-candidate.materialization.test.ts
  SHA-256: 28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb
tests/unit/services/checkout-refresh.test.ts
  SHA-256: 3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f
tests/unit/services/order-recovery-correlation.test.ts
  SHA-256: 7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf
tests/unit/services/checkout-recovery.capacity-resume.test.ts
  SHA-256: 8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1
```

Every CheckoutRecovery-chain task MUST leave all four files byte-for-byte unchanged, verify all four hashes, run them, add separate focused tests for the extracted owner, run `tests/unit/runtime/entrypoint-isolation.test.ts`, run the full existing `npm test` suite without task-introduced regression, and add no test bypasses or weakened production assertions.

The supplied ZIP intentionally has no `moda-interact-background/node_modules`, so this architecture definition does **not** claim runtime execution of either Background frozen baseline while authoring the tasks. Runtime validation belongs to each prepared implementation worktree.

### Admin frozen policy assets

These existing pure/domain test assets are frozen byte-for-byte throughout ADMIN-001..008:

```text
tests/unit/merchant-pricing-builder-payload.test.ts
  SHA-256 a985f89cbc9f4d41901d2c1e400935faf8453a5bd866ac0834a58b0851feb243
tests/unit/merchant-pricing-plan-model.test.ts
  SHA-256 e953adaa54f7aceb31cc43af21f8088c800b32d69c2fc2561dff69fc27ce1086
tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts
  SHA-256 610a7b0d0860490575cdec508f52e438a4e7bee87970a101b6b39d4591d6630f
tests/unit/merchant-pricing-economics.test.ts
  SHA-256 eb7164c84a7c056edfc461fd5b9213ab87e3537511ccf426d32f6bc6804e05e8
tests/unit/merchant-pricing-economics-override.test.ts
  SHA-256 434ad7ca05dad91bfb4fb62ce3ad5cbcd1f27355cc51c879dc7bd9a9967c79f7
tests/unit/merchant-pricing-translations.test.ts
  SHA-256 90e0e5e37687d3037712afac1828175fe8e6623550525572fbcb9d2dc57d8c92
tests/unit/merchant-pricing-translation-workbook.test.ts
  SHA-256 385e79ffcd761b046fb119be18de5f313461cb8d81d6a4f0fb23d3b7837e3ce8
```

`tests/security/admin-merchant-pricing-plan.test.mjs` starts from SHA-256 `89243548c486f68cc7b741e9cac6ded5090ba477f1049e512ae6f982ccd92856` with 13 tests. ADMIN-001 may modify only its builder source-loading mechanism so existing builder assertions scan the bounded extracted module set; existing test names and product/security assertions must not be removed or weakened. ADMIN-002..008 MUST NOT modify that accepted ADMIN-001 test file.

ADMIN-001 adds focused pure controller tests in `tests/unit/merchant-pricing-plan-builder-draft.test.ts`. Later step-extraction tasks reuse that controller suite plus the extraction-safe security suite rather than introducing a new React test framework solely for structural extraction.

## Data Model

No schema or migration changes are authorised.

Existing PostgreSQL tables, relationships, uniqueness constraints, BillingPeriod/Subscription lifecycle semantics, CheckoutRecovery/outreach/status-history semantics and entitlement counters remain unchanged. The Admin builder continues producing the same server-validated MerchantPricingPlan payload; ARCH-025 introduces no Admin schema/migration change.

## Contracts

ARCH-025 introduces no new cross-repository runtime contract.

The Shopify compatibility contract remains `BillingService` in `app/services/billing/billing.service.ts`.

The Background reconciliation compatibility contract remains `BillingSubscriptionReconciliationService` in `src/services/billing-subscription-reconciliation.service.ts`, including its constructor, four public methods, singleton and public helper/type exports. Existing imports in `src/entrypoints/billing.ts` and `src/services/billing-reconciliation.service.ts` remain valid throughout the structural phase.

The Background recovery compatibility contract remains `CheckoutRecoveryService` / `checkoutRecoveryService` in `src/services/checkout-recovery.service.ts`, including the existing constructor, all 17 current public methods and the exported `MaturedCandidateMaterializationResult` / `CheckoutRefreshResult` types. Existing checkout/order/pending-candidate/follow-up/capacity/WhatsApp/Commerce callers remain valid throughout the structural phase.

The Shared billing reconciliation queue contract remains owned by `@modainteract/moda-interact-shared/billing`; no ARCH-025 task may redefine or version it locally. CheckoutRecovery queue/provider/event contracts likewise remain unchanged. Extracted collaborator APIs are repository-internal implementation contracts only.

The Admin compatibility contract remains the `MerchantPricingPlanBuilder` props/export and its HTML form submission to `mutateMerchantPricingPlanAction`, including hidden `intent`, `payload`, `translationJson`, `economicsOverrideRequested` and `economicsOverrideReason` fields. Extracted draft/step APIs are repository-internal UI contracts only.

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

### Background reconciliation

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
- existing canonical `SamePlanBillingPeriodRolloverService`, `ShopifyPlanChangeTransitionService`, `ShopifySubscriptionLifecycleReconciliationService` and `ensureCurrentBillingPeriodProjection` transaction ownership;
- dependency identity as well as behaviour: dependencies currently supplied through `BillingSubscriptionReconciliationService` (`database`, Partner provider, subscription queue, structured logger and clock) remain the exact instances passed to extracted collaborators; dependencies currently reached as canonical module owners/singletons remain those canonical owners unless an individual task explicitly authorises a change.

This is move-only refactoring. Do not remove, coalesce, reorder or "optimise" existing provider/database calls, locks, transactions or durable rereads merely because code is moved. Preserve current permissive classification predicates even where their static non-null assertions are stronger than the runtime gate: initial activation does not currently require `pendingEffectiveAt`, and rollover does not currently require non-null `currentPeriodStart`/`currentPeriodEnd`. Treat those as pre-existing source quirks to characterise, not refactor opportunities.

### Background CheckoutRecovery

Structural extraction MUST preserve:

- checkout-scoped `PendingRecoveryCandidateService.withCheckoutLock(...)` boundaries and the current before/inside-lock execution-eligibility rereads;
- order-processed tombstone placement outside the Prisma completion transaction and before materialisation can initiate outreach;
- latest recovery generation ordering by `generation DESC, id DESC`;
- status-guarded `updateMany` predicates and terminal-state non-reopening;
- durable `RECOVERY_CAPACITY_EXHAUSTED` blocking and first-block timestamp semantics;
- provider/network calls outside Prisma transactions and the current billing admit/revalidate/commit/release/provider-failure order;
- deterministic outbound idempotency `recovery-outreach:<attemptId>` and durable-message confirmation before billing/outreach finalisation;
- current Shopify lookup as the authoritative basket/customer source for materialisation/refresh/resume;
- exact post-ARCH-024 `RecoveryAgentContext` Shop identity and bounded conversation-history semantics;
- test-visible façade call relationships frozen by the post-ARCH-024 regression assets: `handleCheckoutCreated(...)` must continue to invoke the replaceable public `upsertRecovery(...)` operation, and capacity resume must continue to invoke the replaceable public `handleCheckoutCreated(...)` operation. Extracted collaborators may satisfy this with narrow dynamic callback/port wiring, but MUST NOT reverse-import the façade or bind an original method eagerly in a way that bypasses a later façade replacement/spy;
- the exact `RecoveryBillingService` instance supplied to the `CheckoutRecoveryService` constructor for every extracted billing-aware collaborator/finaliser; do not silently substitute the module singleton;
- the current initial-outreach versus follow-up asymmetries: initial bounded template selection returns without marking the attempt failed, only initial admission reason `capacity-exhausted` durably blocks the recovery, follow-up capacity blocks remain attempt-level, and confirmed-send finalisation uses provider `sentAt` rather than the compatibility `markRecoveryMessageSent(...)` clock.

No CheckoutRecovery task may create a second billing, candidate/tombstone, WhatsApp-send, follow-up queue, capacity-resume queue or conversation implementation.

### Admin builder

No Prisma transaction moves into the client refactor. `mutateMerchantPricingPlanAction` remains the server-side authority for parsing, SUPER_ADMIN authorization, catalogue concurrency, economics override approval, translation validation, feature persistence, usage-event persistence and audit writes. The client draft/controller must not claim those responsibilities.

## Ordering

The three sub-tranches are independent and are not serialized against one another:

```text
Shopify:                  SHOPIFY-001 -> ... -> SHOPIFY-011
Background reconciliation: BACKGROUND-001 -> ... -> BACKGROUND-007
Background recovery:       BACKGROUND-008 -> ... -> BACKGROUND-015
```

Within each individual chain tasks execute sequentially because later tasks consume interfaces established by earlier tasks. The two Background chains intentionally may execute independently even though they share one repository because they modify different primary coordinator/façade files and have no runtime-contract dependency.

Do not parallelise tasks **within the same chain**. Do not invent a cross-chain dependency or priority when both Background frontiers are Ready.

For the Admin wizard, preserve the seven-step order, one-step forward navigation limit, unrestricted backward navigation and the exact step-specific forward gates described above. Moving a step into another component must not change when the translation workbook mounts or when final submission becomes available.

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

Lifecycle-specific reconciliation retry decisions remain with their owning handlers; do not create a generic retry service that centralises business policy. CheckoutRecovery extraction likewise preserves existing result/reason strings, provider-failure distinctions, template/admission suppression outcomes and recovery status transitions rather than normalising them.

Admin extraction must preserve the current non-destructive translation workbook behaviour, unavailable-Commerce-model repair warning, economics hard-fail/override distinctions and local draft state across normal step navigation. Structural extraction must not convert render/local-state errors into server mutations or alter server-returned validation/error semantics.

## Scalability

This is a structural refactor only. It must not add provider calls, Prisma round trips, transaction duration, queue work or per-request durable writes relative to the current equivalent path. Existing deliberate rereads/fences (for example the recovery-credit purchase provider and catalogue revalidation reads) must not be coalesced away.

A task that accidentally multiplies Shopify Partner API reads or database work is a behavioural regression.

For Background reconciliation, the common hot path must not gain additional provider calls, database round trips, queue publications or transaction duration. In particular, normal accepted jobs continue to acquire at most one `getSubscriptionReconciliationSnapshot(...)` and reuse it; reinstall continues its separate single `getActiveSubscription(...)` read. Queue identity, delayed scheduling and startup reconstruction cardinality remain unchanged.

For CheckoutRecovery, extraction must not add Shopify checkout lookups, billing admissions/revalidations, outbound provider sends, candidate/Redis operations or Prisma round trips to an equivalent lifecycle path. In particular no-recovery/terminal checkout updates still avoid Shopify lookup, candidate materialisation still checks the order tombstone before provider lookup, and capacity resume still rereads durable state under the checkout lock before Shopify/provider work.

## Security

No authentication, authorization, tenant isolation or secret-handling boundary changes are authorised.

Extracted services receive server-side dependencies only. No provider credential, Shopify token, whole customer object or billing payload may be newly exposed to browser code or logs.

Background extraction must likewise keep provider credentials, Shopify tokens and whole provider/customer payloads out of new logs and preserve tenant/shop scoping on every durable lookup/mutation. CheckoutRecovery mapping must continue ignoring untrusted/stale webhook basket/customer fields where current Shopify data is the authoritative recovery snapshot source.

Admin extraction does not move authorization client-side. `mutateMerchantPricingPlanAction` remains protected by the existing Platform SUPER_ADMIN mutation boundary and revalidates every submitted payload. The builder may present availability/repair state but must not treat client-side selectors as authorization or durable validation.

## Observability

No new observability mechanism is required. Existing log/telemetry semantics remain unchanged. Do not introduce a new generic logger during extraction.

Background reconciliation already uses the canonical Shared structured logger. Preserve existing `billing.subscription_reconciliation.*` event meanings and bounded identifiers across extraction, including job start/finish, enqueue failure, provider failure, reinstall outcomes, pre-close publish failure, rollover retry and unsupported Paid trial. CheckoutRecovery does not need a new generic logging layer for this structural refactor; any newly necessary diagnostics must use the canonical Shared logger and bounded IDs only. Do not introduce a competing logger or newly log provider/customer/message payloads.

## Infrastructure Assessment

No infrastructure implementation is required. ARCH-025 does not change Render services, public/private routing, worker topology, environment variables, Redis, PostgreSQL infrastructure or deployment configuration.

Therefore no `moda_gateway` task is required.

## Rollout / Migration

Classification: **PRODUCTION / COMPATIBLE ROLLOUT** for behavioural purposes.

No database migration, Shared publication, queue drain, infrastructure change or coordinated cross-repository deployment is required. Shopify and Background tasks are independently deployable because their existing public/worker façades remain compatible.

### Background CheckoutRecovery target

The final CheckoutRecovery boundary remains worker-facing and compatible:

```text
workers / Commerce host
        |
        v
CheckoutRecoveryService                         compatibility façade
        |
        +--> RecoveryInitiationService
        |      +--> RecoveryOutreachFinalizationService
        |      +--> latest-recovery query primitive
        +--> RecoveryOutreachFollowUpProcessorService
        +--> RecoverySnapshotBuilder / recovery-mappers
        +--> RecoveryMaterializationService
        +--> CheckoutEventOrchestratorService
        +--> OrderRecoveryCorrelationService
        +--> RecoveryCapacityResumeProcessorService
        +--> RecoveryAgentContextService
```

The extracted owners continue to delegate canonical work to the existing recovery billing, outreach-attempt, follow-up scheduling, policy, candidate correlation, execution-eligibility, Shopify checkout lookup, capacity-resume scheduling, outbound WhatsApp admission, conversation and template-selection services.

The checkout-recovery chain is independent of BACKGROUND-001..007 and the Shopify chain. Within BACKGROUND-008..015, tasks are sequential because each extraction establishes interfaces reused by later CheckoutRecovery lifecycle owners.

Rollback is ordinary code rollback of the affected repository commit; there is no schema rollback.

### Admin builder rollout

ADMIN-001..008 are a pre-production-compatible structural UI extraction with no form/action/schema migration. Each task is independently reviewable, retains the public component module, and can be rolled back by reverting that task's repository commit. The Admin chain may run independently of both Background chains because it modifies a different repository and no shared runtime contract.

## Repository Responsibilities

Three implementation repositories participate, independently:

```text
repository: moda-interact
assigned_agent: moda_app
scope: Shopify BillingService tranche

repository: moda-interact-background
assigned_agent: moda_background
scope: billing subscription reconciliation and CheckoutRecovery maintainability tranches

repository: moda-interact-admin
assigned_agent: moda_admin
scope: MerchantPricingPlanBuilder draft/controller and step extraction
```

The parent workspace owns architecture/task coordination files. Repository implementation remains confined to the assigned implementation repository plus the assigned parent task report file permitted by the task/VCS protocol. No ARCH-025 task grants one repository agent ownership of another participating repository.

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
| ARCH-025-BACKGROUND-001 | Extract pure reconciliation classification | Complete | - |
| ARCH-025-BACKGROUND-002 | Extract queue publication and startup reconstruction | Ready | BACKGROUND-001 |
| ARCH-025-BACKGROUND-003 | Extract initial activation reconciliation | Pending | BACKGROUND-002 |
| ARCH-025-BACKGROUND-004 | Extract reinstall reconciliation | Pending | BACKGROUND-003 |
| ARCH-025-BACKGROUND-005 | Extract billing-cycle/pre-close/rollover reconciliation | Pending | BACKGROUND-004 |
| ARCH-025-BACKGROUND-006 | Extract established plan-change reconciliation | Pending | BACKGROUND-005 |
| ARCH-025-BACKGROUND-007 | Reduce `reconcileJob()` to bounded context/coordinator flow | Pending | BACKGROUND-006 |
| ARCH-025-BACKGROUND-008 | Extract initial recovery outreach and confirmed-send finalisation | Ready | - |
| ARCH-025-BACKGROUND-009 | Extract no-response recovery outreach follow-up processor | Pending | BACKGROUND-008 |
| ARCH-025-BACKGROUND-010 | Extract canonical recovery snapshot mapping | Pending | BACKGROUND-009 |
| ARCH-025-BACKGROUND-011 | Extract matured-candidate materialisation | Pending | BACKGROUND-010 |
| ARCH-025-BACKGROUND-012 | Extract checkout/cart event orchestration | Pending | BACKGROUND-011 |
| ARCH-025-BACKGROUND-013 | Extract order completion correlation | Pending | BACKGROUND-012 |
| ARCH-025-BACKGROUND-014 | Extract capacity-blocked recovery resume | Pending | BACKGROUND-013 |
| ARCH-025-BACKGROUND-015 | Extract recovery agent-context reads and finish the façade | Pending | BACKGROUND-014 |

### Admin tranche

| Task | Outcome | Status | Depends On |
|---|---|---|---|
| ARCH-025-ADMIN-001 | Extract typed draft/controller and make security assertions extraction-safe | Ready | - |
| ARCH-025-ADMIN-002 | Extract Plan step | Pending | ADMIN-001 |
| ARCH-025-ADMIN-003 | Extract Catalogue placement step | Pending | ADMIN-002 |
| ARCH-025-ADMIN-004 | Extract Shopify pricing step | Pending | ADMIN-003 |
| ARCH-025-ADMIN-005 | Extract Usage events step | Pending | ADMIN-004 |
| ARCH-025-ADMIN-006 | Extract Merchant content step | Pending | ADMIN-005 |
| ARCH-025-ADMIN-007 | Extract Portfolio economics step | Pending | ADMIN-006 |
| ARCH-025-ADMIN-008 | Extract Translations/review and reduce final builder shell | Pending | ADMIN-007 |

Execution graph:

```text
SHOPIFY-001 -> ... -> SHOPIFY-010 -> SHOPIFY-011

BACKGROUND-001 -> BACKGROUND-002 -> BACKGROUND-003 -> BACKGROUND-004
      -> BACKGROUND-005 -> BACKGROUND-006 -> BACKGROUND-007

BACKGROUND-008 -> BACKGROUND-009 -> BACKGROUND-010 -> BACKGROUND-011
      -> BACKGROUND-012 -> BACKGROUND-013 -> BACKGROUND-014 -> BACKGROUND-015

ADMIN-001 -> ADMIN-002 -> ADMIN-003 -> ADMIN-004
      -> ADMIN-005 -> ADMIN-006 -> ADMIN-007 -> ADMIN-008
```

There is deliberately no dependency edge between the Shopify tranche, either Background chain and the Admin builder chain.

## System Validation

A separate `moda_system_test` task is **not applicable** to this structural maintainability initiative because ARCH-025 introduces no new cross-service contract, infrastructure topology, schema, queue protocol or externally observable product behaviour.

Architecture completion instead requires all four sub-tranches to preserve their frozen regression assets and introduce no full-suite regression, while each extracted owner gains focused tests. For Shopify, the durable `ARCH025-TEST-001` baseline remains authoritative; for Background reconciliation, all 98 frozen reconciliation tests are required to pass. CheckoutRecovery extraction additionally freezes these integrated post-ARCH-024 regression assets byte-for-byte:

```text
tests/unit/services/matured-candidate.materialization.test.ts
  SHA-256 28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb
tests/unit/services/checkout-refresh.test.ts
  SHA-256 3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f
tests/unit/services/order-recovery-correlation.test.ts
  SHA-256 7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf
tests/unit/services/checkout-recovery.capacity-resume.test.ts
  SHA-256 8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1
```

The Admin tranche must preserve the seven frozen pure-policy test files listed above, retain all 13 existing `admin-merchant-pricing-plan.test.mjs` tests/assertions through its ADMIN-001 extraction-safe loader adjustment, then keep the accepted security file unchanged for ADMIN-002..008. Every Admin task must pass `npm run test:unit`, `npm test`, targeted lint, production build and `git diff --check`. This does not waive repository-level integration/runtime validation already exercised by those commands.

## Open Questions

None.

## Change History

- 2026-10-02: BACKGROUND-001 blocked-task disposition found no source-level defect in the pure classification extraction. Corrected the architect-authored frozen reconciliation suite count from 98 to the 146 tests actually executed by the byte-identical required-hash asset. Returned BACKGROUND-001 to Ready for an evidence-only Attempt 2 comparing exact pre-task commit `670fbad4d52308c96ef41a6a4d29116f1ad42f1a` with submitted commit `b3c7a1264a22baf498b14916a341686a751de869` under the same environment; no Background full-suite baseline is created until that differential proves the failure set is pre-existing.
- 2026-10-02: BACKGROUND-001 Attempt 2 was accepted after the same-environment differential proved the exact same eight failing tests plus the same commerce-evidence fixture-loading failure on the pre-task and submitted commits. Recorded durable no-regression baseline `ARCH025-BACKGROUND-TEST-001`, marked BACKGROUND-001 Complete and promoted BACKGROUND-002 to Ready.
- 2026-10-02: Deep ADMIN-001..008 source/task coherence review kept the eight-task graph unchanged, made ADMIN-001 the complete consume-only controller contract for all later steps, preserved pure-Node testability and UI-edge identity/effect semantics, closed the extracted-module security-scan blind spot, and characterized exact translation fallback, usage-event stale-field/tier behaviour, secondary economics rows and translation-workbook/final-step mount semantics.
- 2026-10-02: Added the independent Admin `MerchantPricingPlanBuilder` maintainability chain ADMIN-001..008 against the post-ARCH-024 model-assignment baseline. Preserved the seven-step form/action contract, exact navigation/economics/translation/product-policy semantics, established a typed draft/controller boundary before JSX extraction, froze seven pure-policy test assets, and made the existing source-based security assertions extraction-safe without weakening them.
- 2026-10-02: Added the independent CheckoutRecoveryService maintainability chain BACKGROUND-008..015 against the integrated post-ARCH-024 Background baseline. Preserved the worker-facing façade, canonical Shop `shopId` agent context, checkout-scoped race guards, recovery generation/idempotency, billing/provider boundaries and existing adjacent recovery owners; froze four post-ARCH-024 regression assets and kept the chain independent from BACKGROUND-001..007.
- 2026-10-02: Deep architectural coherence review of BACKGROUND-008..015 retained the eight-task graph but tightened test-visible façade compatibility ports, exact injected billing identity, initial/follow-up suppression asymmetries, finalisation CAS convergence, CheckoutRefresh direct shop lookup, materialisation result semantics and capacity-resume re-entry arity/result behaviour.
- 2026-10-02: SHOPIFY-011 Attempt 2 accepted the report-only reconciliation for the final Shopify sync-coordinator extraction at reviewed implementation commit `3e96f68decc0051aefa9dfbb53101a3661895a9b` and published parent report tip `ac475108c5ec5326d14cbc151d2825786b4b008b`. `BillingService.syncSubscription()` is a thin delegate, the provider-to-local coordinator preserves the accepted provider/transaction/locking/projection semantics, and the full Shopify tranche is now Complete. ARCH-025 remains In Progress because the independent Background tranche is still active.
- 2026-10-02: Second deep BACKGROUND-001..007 source-closure review preserved permissive null-shape classification quirks, exact dependency identity across extracted collaborators, canonical shared locking reuse, direct tests for timing/locking/discount primitives, and both FROZEN `continue` edge paths (provider present and provider null). No task split, reorder or new runtime behaviour was introduced.
- 2026-10-02: Deep Background task-coherence review tightened parse-before-runtime-config semantics, clock/log preservation, reconstruction count semantics, cycle error-clearing distinctions, exact current-plan eligibility gates, reinstall pre-transaction rereads and the legacy FROZEN `continue` provider-plan fallthrough. Kept the final provider-plan lookup/branch dispatch as bounded coordinator orchestration so accepted lifecycle-service interfaces remain sufficient through BACKGROUND-007.
- 2026-10-02: Extended ARCH-025 with an independent Background billing-subscription reconciliation maintainability tranche. Added seven sequential `moda_background` tasks, froze the reconciliation regression asset, preserved worker constructor/entrypoint and provider-call invariants, and kept lifecycle-specific retries with their owning handlers rather than creating a generic retry service.
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
