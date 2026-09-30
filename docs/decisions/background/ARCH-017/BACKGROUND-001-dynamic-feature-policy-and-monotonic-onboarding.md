---
id: ARCH-017-BACKGROUND-001
architecture_id: ARCH-017
title: Resolve dynamic feature policy, platform billing limits and monotonic onboarding
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 4
depends_on:
- ARCH-017-DATABASE-001
enables:
- ARCH-017-BACKGROUND-002
created: 2026-09-18
updated: 2026-09-18
---

# ARCH-017-BACKGROUND-001

> Frontmatter correction before materialisation: remove the accidental leading space before `task_kind` if your YAML parser treats it as invalid. The canonical value is `task_kind: implementation`.

## Objective

Update `moda-interact-background` to consume the ARCH-017 database model without any fixed feature enum, resolve outbound safety policy from PlatformBillingPolicy + ShopBillingPolicyOverride, enforce checkout-recovery capability at admission, and stop resetting historical onboarding completion during reinstall/no-contract reconciliation.

Do not implement BillingPlan materialisation here. Shopify owns callback/reconciliation materialisation. Do not implement Admin catalogue management here.

ARCH-011 remains out of scope.

## Dependency gate

Do not start until `ARCH-017-DATABASE-001` is architect-accepted and the repository's `database` submodule resolves to that accepted database commit.

After dependency materialisation, run:

```text
npm run prisma:generate
```

before TypeScript validation.

## Read before editing

```text
src/services/effective-billing-policy.service.ts
src/services/entitlement.service.ts
src/services/recovery-billing.service.ts
src/services/outbound-whatsapp-admission.service.ts
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
tests/unit/services/effective-billing-policy.service.test.ts
tests/unit/services/recovery-billing.service.test.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/services/outbound-whatsapp-admission.service.test.ts
package.json
database/prisma/schema.prisma
docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md
```

Search the repository for all remaining imports/usages of:

```text
BillingPlanFeatureIdentifier
defaultOutboundSoftLimit
defaultOutboundHardLimit
terminalMessageReservedSlots
```

Every production reference must either be intentionally replaced or documented as unrelated generated/history content.

## Authorized implementation surface

```text
src/services/effective-billing-policy.service.ts
src/services/entitlement.service.ts
src/services/recovery-billing.service.ts
src/services/outbound-whatsapp-admission.service.ts
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
focused unit/integration tests for the above, including:
- tests/unit/services/billing-subscription-reconciliation.service.test.ts
- tests/unit/services/billing-reconciliation.service.test.ts
package.json only if a focused test command is added
package-lock.json only if package.json changes
```

Do not edit the database submodule in this task.

## 1. Keep feature identity fully data-driven

Do NOT create `src/domain/billing-feature-keys.ts`, a feature-key registry, a TypeScript enum, a string-literal union, or any other central list of known Feature keys.

Background must treat `Feature.key` as database-owned dynamic data. Adding a Feature row in Admin must not require a Background code change merely so the resolver, entitlement service, or effective-policy model can recognize that feature.

Generic feature APIs MUST accept arbitrary non-empty feature-key strings obtained from persisted Feature rows.

A service that implements one concrete capability may reference that capability's stable key locally at the exact implementation boundary. For example, `RecoveryBillingService` may define a repository-local/private constant immediately in that service:

```ts
const CHECKOUT_RECOVERY_FEATURE_KEY = "checkout_recovery";
```

That local constant identifies the capability implemented by that service. It MUST NOT be exported as a catalogue registry and MUST NOT enumerate unrelated features.

Do not add constants for `ai_conversations`, `product_search`, `order_support`, or any future Feature merely because those rows exist in the catalogue. A future capability-owning implementation references its own key only if/when code is actually needed to implement that capability.

## 2. Change EffectiveBillingPolicy feature type

In `effective-billing-policy.service.ts`:

- remove the Prisma `BillingPlanFeatureIdentifier` import;
- remove `Object.values(BillingPlanFeatureIdentifier)`;
- remove `Record<BillingPlanFeatureIdentifier, boolean>`;
- expose effective features as a set of dynamic keys.

Target type:

```ts
export type EffectiveBillingPolicy = {
  // preserve all existing non-feature fields
  features: ReadonlySet<string>;
  // preserve outboundSoftLimit/outboundHardLimit/terminalMessageReservedSlots
};
```

If the repository's existing type is an interface, keep the existing form and change only the member type.

## 3. Load plan capability + shop preference

When resolving the current subscription plan, include Feature rows:

```ts
plan: {
  include: {
    features: {
      include: {
        feature: true,
      },
    },
  },
},
```

Also load `ShopFeaturePreference` for the same `shopId` including its Feature row. This may be a second query in the resolver transaction/read batch; do not introduce cross-service calls.

Only an unexpired `ShopBillingPolicyOverride` is effective, using the repository's existing expiry semantics.

Construct effective features exactly as follows:

```ts
const optedInFeatureKeys = new Set(
  shopFeaturePreferences
    .filter((preference) => preference.enabled)
    .map((preference) => preference.feature.key),
);

const effectiveFeatureKeys = new Set<string>();

for (const mapping of plan.features) {
  if (!mapping.enabled) continue;
  if (!mapping.feature.active) continue;

  if (mapping.feature.activationMode === "ALWAYS_ENABLED") {
    effectiveFeatureKeys.add(mapping.feature.key);
    continue;
  }

  if (
    mapping.feature.activationMode === "MERCHANT_OPT_IN" &&
    optedInFeatureKeys.has(mapping.feature.key)
  ) {
    effectiveFeatureKeys.add(mapping.feature.key);
  }
}
```

Do not delete or modify ShopFeaturePreference rows in Background.

Do not treat a preference as entitlement if the current BillingPlan does not map that feature.

## 4. Resolve outbound limits from PlatformBillingPolicy

Remove every read of these deleted BillingPlan fields:

```text
plan.defaultOutboundSoftLimit
plan.defaultOutboundHardLimit
plan.terminalMessageReservedSlots
```

Use:

```ts
const requestedHardLimit =
  activeOverride?.outboundHardLimit ?? platformPolicy.defaultOutboundHardLimit;

const outboundHardLimit = Math.min(
  requestedHardLimit,
  platformPolicy.absoluteOutboundHardLimit,
);

const requestedSoftLimit =
  activeOverride?.outboundSoftLimit ?? platformPolicy.defaultOutboundSoftLimit;

const outboundSoftLimit = Math.min(requestedSoftLimit, outboundHardLimit);

const terminalMessageReservedSlots =
  activeOverride?.terminalMessageReservedSlots ??
  platformPolicy.terminalMessageReservedSlots;
```

Then reuse/adjust the existing validation helpers so the final effective values satisfy:

```text
outboundHardLimit >= 2
outboundSoftLimit >= 1
outboundSoftLimit <= outboundHardLimit
terminalMessageReservedSlots >= 1
terminalMessageReservedSlots < outboundHardLimit
```

Do not silently clamp terminal-message slots to an invalid value. If persisted policy is structurally invalid, retain existing fail-closed/error behavior and make the reason explicit.

## 5. Refactor EntitlementService

Remove the current closed `featureMap` and enum-backed lookup.

The public methods should accept a dynamic key:

```ts
async hasFeature(shopId: string, featureKey: string): Promise<boolean> {
  const policy = await this.effectiveBillingPolicy.resolve(shopId);
  return policy.features.has(featureKey);
}

async assertFeature(shopId: string, featureKey: string): Promise<void> {
  const hasFeature = await this.hasFeature(shopId, featureKey);
  if (!hasFeature) {
    // preserve current EntitlementError type/error conventions
    throw ...;
  }
}
```

Do not introduce a central feature-key registry, enum, union, or exhaustive switch. Generic code must work with arbitrary persisted Feature keys. Concrete capability-owning code may use one local key constant for the capability it implements.

## 6. Enforce checkout_recovery in RecoveryBillingService

Current `RecoveryBillingService.admit()` resolves effective policy but does not make checkout recovery authoritative.

At the top of `recovery-billing.service.ts`, define only this capability-local constant (unless the file already has an equivalent local constant):

```ts
const CHECKOUT_RECOVERY_FEATURE_KEY = "checkout_recovery";
```

Do not export it and do not add any unrelated feature keys.

Before creating/reserving recovery capacity, require:

```ts
policy.features.has(CHECKOUT_RECOVERY_FEATURE_KEY)
```

If false, return/throw using the service's existing admission-denial pattern. Add a distinct reason such as `feature-unavailable` only if the current result union requires a reason string. Do not overload capacity exhaustion, pause, or billing-error reasons.

This check must occur before creating any reservation/usage mutation.

## 7. Preserve ShopFeaturePreference through plan changes

Search subscription reconciliation for plan-change code. Do not create, update or delete `ShopFeaturePreference` during:

```text
RENEWED_SAME_PLAN
PLAN_CHANGED
CONTRACT_ENDED
NO_CONTRACT
UNMAPPED
SYNC_ERROR
FROZEN
```

The resolver naturally makes a preference dormant when the current plan no longer maps the feature.

## 8. Fix reinstall onboarding reset

In `billing-subscription-reconciliation.service.ts`, current `completeReinstallWithoutContract` contains:

```ts
await transaction.shopSettings.update({
  where: { shopId },
  data: { onboardingCompleted: false },
});
```

Delete this write completely.

Do NOT replace it with another write to `onboardingCompleted`.

`completeReinstallWithoutContract` must update Subscription and Shop reinstall lifecycle only. Existing ShopSettings onboarding history remains unchanged.

Invariant:

```text
false stays false when the merchant has never successfully activated
true stays true forever after a prior successful verified activation
```

## Required tests

### Effective billing policy

Update `tests/unit/services/effective-billing-policy.service.test.ts` to prove:

1. an active `ALWAYS_ENABLED` mapped feature is effective without ShopFeaturePreference;
2. `MERCHANT_OPT_IN` mapped feature is false/absent without enabled preference;
3. same mapped optional feature becomes effective with enabled preference;
4. preference for feature not mapped by current BillingPlan remains ineffective;
5. inactive Feature is ineffective even if mapped and preferred;
6. `BillingPlanFeature.enabled=false` is ineffective;
7. resolver tolerates an unknown dynamic Feature key without code changes and returns it when activation rules permit;
8. PlatformBillingPolicy supplies default soft/hard/terminal values;
9. active ShopBillingPolicyOverride overrides soft/hard/terminal values;
10. absolute hard ceiling is still enforced;
11. expired override is ignored;
12. terminal reserve >= effective hard limit fails closed.

Do not assert `policy.features.CHECKOUT_RECOVERY`. Assert:

```ts
expect(policy.features.has("checkout_recovery")).toBe(true);
```

### Recovery admission

Add/update RecoveryBillingService tests:

- checkout_recovery effective -> existing admissible path unchanged;
- checkout_recovery absent -> no reservation/usage write and admission denied;
- optional features do not affect checkout admission.

### Onboarding

Update/add reconciliation tests:

- reinstall + no provider contract + `onboardingCompleted=false` -> remains false;
- reinstall + no provider contract + `onboardingCompleted=true` -> remains true;
- cancellation/no-contract does not reset true;
- successful activation paths that already set true remain unchanged.

### Preference persistence

Add a focused test proving a plan transition does not mutate `shopFeaturePreference` calls/rows and the resolver changes effective features based only on the new plan mapping.

## Validation

Inspect `package.json` first. Run the scripts that actually exist. Expected current commands include:

```text
npm run prisma:generate
npm run prisma:validate
npm run test:unit
npm test
npm run build
git diff --check
```

If `typecheck`/`lint` scripts exist at execution time, run them. Do not invent missing scripts; record absent scripts exactly per repository baseline policy.

## Stop conditions

STOP and return to moda_architect if:

- accepted DATABASE-001 does not contain Feature/ShopFeaturePreference/Platform policy fields described above;
- implementation would require adding a Shared contract solely for database feature keys;
- a plan transition appears to require copying ShopFeaturePreference rows;
- code would reintroduce a fixed complete feature enum/list;
- ARCH-011 behavior is needed to satisfy a test.

## Non-goals

- BillingPlan materialisation;
- Admin feature catalogue editing;
- merchant feature preference UI/action;
- provider subscription callback behavior;
- proration.

## Acceptance criteria

- no production import of `BillingPlanFeatureIdentifier` remains;
- EffectiveBillingPolicy uses dynamic feature keys and shop opt-in state;
- outbound limits no longer read BillingPlan fields;
- checkout recovery capability is actually enforced before recovery admission;
- no plan-change lifecycle mutates ShopFeaturePreference;
- reinstall/no-contract never resets onboarding history;
- required tests and repository validation pass or only documented unrelated baseline failures remain.

## Completion protocol

Set status to `review`, not `complete`. Completion Report must include exact implementation/parent commits, validation output, physical task worktree evidence and accepted DATABASE-001 revision.

## Completion Report

### Status

Ready for architect review. ARCH-017 Background changes are implemented and validated on attempt 4.

### Implementation

- Attempt 4 changed only `src/services/billing-reconciliation.service.ts` and `tests/unit/services/billing-reconciliation.service.test.ts`.
- `BillingReconciliationService.applySubscription(...)` no longer reads `ShopSettings.onboardingCompleted`; both initial-pending branches now use durable Subscription state and preserve their existing mismatch protection, canonical Paid activation, and unconditional early return.
- The accepted Attempt-2 dynamic feature/policy/admission/preference/reinstall changes and Attempt-3 queued reconciliation correction remain unchanged.

### Dependency Evidence

- Accepted DATABASE-001 implementation revision: `3c7179825c3e12af1d6db805b8a2a73c61c2097c` (`fix(database): tighten ARCH-017 billing schema validation`).
- Materialized implementation database gitlink: `22d56f41dafd2fd6784058ef0691b1269019b4b2`, which contains the accepted revision as an ancestor and provides Feature, ShopFeaturePreference, FeatureActivationMode, and platform policy models.
- No database submodule files or gitlinks were edited by this task.

### Validation

- `npm run prisma:generate`: passed.
- `npm run prisma:validate`: passed.
- Focused billing-reconciliation Vitest run (`tests/unit/services/billing-reconciliation.service.test.ts`): 44 passed.
- `npm run test:unit`: 1,035 passed across 68 files.
- `npm test`: 1,039 passed, 20 skipped across 69 passed and 11 skipped files.
- `npm run build` (Prisma generate + `tsc`): passed.
- `git diff --check`: passed.
- Attempt 4 search: `onboardingCompleted` has no matches in `src/services/billing-reconciliation.service.ts`; the service-wide obsolete predicate search returned no matches.
- No separate `typecheck` or `lint` scripts exist in `package.json`; build TypeScript compilation was used.

### Worktree / Git Evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-017-BACKGROUND-001`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-017-BACKGROUND-001`.
- Implementation commit: `fd267c8` (`fix(background): remove periodic onboarding gate`), pushed to `origin/task/ARCH-017-BACKGROUND-001`.
- Prior accepted implementation commits remain `33c2645` and `cdb6e4d`.
- Parent report commit submitted for architect review: `cc7fca2f`, pushed to `origin/task/ARCH-017-BACKGROUND-001`.
- No main branch was modified and no Architect Review section was edited.

### Attempt-4 Correction Mapping

- **Periodic onboarding authority:** implemented in `src/services/billing-reconciliation.service.ts` by deleting the `ShopSettings` read and removing onboarding predicates from the mismatch and matching initial-pending branches; focused suite and zero-match search pass.
- **Initial Free:** `tests/unit/services/billing-reconciliation.service.test.ts` now runs the existing unresolved-initial-activation scenario for `onboardingCompleted=false` and `true`, proving no generic `subscription.upsert`, `billingPeriod.upsert`, or periodic settings read.
- **Initial Paid:** the existing canonical activation scenario now runs for both milestone values, preserving canonical BillingPeriod and included-recovery entitlement assertions while proving no periodic settings read.
- **Provider/pending-plan mismatch:** the existing drift scenario now runs for both milestone values, preserving no generic projection, no pending-state mutation, and no BillingPeriod creation.
- **Accepted prior corrections:** Attempt-3 queued reconciliation remains unchanged; reinstall/no-contract still performs no `onboardingCompleted=false` write.


## Architect Review — Attempt 2

### Review Status

**Changes Requested — make pending initial activation independent of the monotonic onboarding milestone**

### Accepted Attempt-2 functionality to preserve

The following production changes are functionally aligned with ARCH-017 and are not being reopened:

```text
dynamic Feature keys resolved from persisted Feature rows
MERCHANT_OPT_IN gated by ShopFeaturePreference + current plan mapping
ALWAYS_ENABLED resolved without a shop preference
PlatformBillingPolicy + active ShopBillingPolicyOverride own outbound limits
checkout_recovery checked before recovery reservation/admission
ShopFeaturePreference is not mutated by Background plan transitions
reinstall + no provider contract no longer writes onboardingCompleted=false
```

The reported focused/unit/full validation is sufficient supporting evidence for those areas. Do not broaden Attempt 3 into exhaustive test expansion.

### Functional finding — initial activation still requires `onboardingCompleted=false`

ARCH-017 changes `ShopSettings.onboardingCompleted` into a monotonic Shopify managed-pricing milestone. `ARCH-017-SHOPIFY-001` is required to persist:

```text
onboardingCompleted=true
```

before BillingPlan resolution/materialisation or later Subscription/BillingPeriod projection can fail.

The current Background reconciliation path still assumes the pre-ARCH-017 meaning of the flag.

In `BillingSubscriptionReconciliationService.reconcileJob(...)`, initial activation is currently classified only when:

```ts
row.settings?.onboardingCompleted === false
&& row.subscription.status === SubscriptionProjectionStatus.NO_CONTRACT
&& row.subscription.planId === null
&& row.subscription.pendingPlanId !== null
&& row.subscription.pendingShopifyPlanHandle !== null
&& row.subscription.nextReconcileAt !== null
```

The same obsolete condition is rechecked inside all three initial-activation completion/projection paths:

```text
completeVerifiedFree(...)
completeVerifiedPaid(...)
applyOtherCurrentPlan(...)
```

through:

```ts
settings?.onboardingCompleted !== false
```

as a reason to reject the transition.

This becomes incorrect once SHOPIFY-001 implements the agreed ARCH-017 milestone ordering:

```text
authenticated Shopify managed-pricing selection observed
  -> onboardingCompleted=true   (durable, separately committed)
  -> local BillingPlan/projection work
  -> if asynchronous reconciliation is still required,
     Subscription may remain NO_CONTRACT + pending plan + nextReconcileAt
```

A valid queued Background reconciliation for that state currently fails `isInitialActivation` and returns without consulting Shopify. Even if entry were reached, the completion transaction would reject because onboarding is already true.

That breaks the existing asynchronous recovery path precisely when the new monotonic milestone has already been persisted. The onboarding flag must no longer be used as the authority bit for pending initial billing reconciliation.

### Required Attempt-3 correction

Keep the correction narrowly scoped to `billing-subscription-reconciliation.service.ts` and its focused tests. Preserve all accepted Attempt-2 feature-policy/admission changes.

#### 1. Classify pending initial activation from Subscription state, not onboarding state

In `reconcileJob(...)`, remove `row.settings?.onboardingCompleted === false` from the `isInitialActivation` predicate.

The durable authority shape remains:

```text
Shop.status = ACTIVE
Subscription.status = NO_CONTRACT
Subscription.planId = null
Subscription.pendingPlanId != null
Subscription.pendingShopifyPlanHandle != null
Subscription.nextReconcileAt != null
job.subscriptionId matches
job.expectedNextReconcileAt matches the durable schedule
```

Keep the existing pending-plan identity and stale-job checks. Do not weaken them merely to remove the onboarding dependency.

Both values of `onboardingCompleted` must be valid for this pending activation shape:

```text
false  -> pre-callback / older pending flow may still reconcile
true   -> ARCH-017 callback milestone has already been persisted and reconciliation must still proceed
```

#### 2. Remove onboarding=false as a completion CAS prerequisite

In:

```text
completeVerifiedFree(...)
completeVerifiedPaid(...)
applyOtherCurrentPlan(...)
```

remove the `settings?.onboardingCompleted !== false` rejection condition.

Use the existing locked Subscription pending-state identity as the concurrency/staleness authority:

```text
status
planId
pendingPlanId
pendingShopifyPlanHandle
pendingEffectiveAt
nextReconcileAt
```

Do not replace the removed condition with `onboardingCompleted===true`; the reconciliation must remain valid for both pre-milestone and post-milestone pending jobs.

It is acceptable for successful verified activation paths to retain their existing idempotent `onboardingCompleted=true` write. No path may write `false`.

`applyOtherCurrentPlan(...)` must not introduce a false write. Under ARCH-017, if Shopify already persisted the milestone it remains true; if Background is processing an older/pre-callback pending state, this task does not need to redefine unrelated callback semantics.

#### 3. Preserve reinstall monotonicity

Do not change the accepted Attempt-2 correction in `completeReinstallWithoutContract(...)`:

```text
no write to ShopSettings.onboardingCompleted
```

The correction requested here is only removal of onboarding as an initial-activation gating/CAS condition.

### Required focused regression coverage

Add only enough tests to prove the functional interaction:

1. `NO_CONTRACT + pending plan + onboardingCompleted=true` is recognized as initial activation and reaches provider reconciliation rather than no-op;
2. the same state with provider `null` preserves pending intent and schedules the next retry;
3. the same state with verified Free provider truth completes Free activation;
4. the same state with verified Paid provider truth completes Paid activation;
5. `onboardingCompleted=false` pending activation still works, preserving the pre-callback recovery path;
6. stale `subscriptionId` / `expectedNextReconcileAt` guards remain authoritative;
7. reinstall + no contract still performs no onboarding write.

Do not add an exhaustive lifecycle matrix for this correction.

### Non-blocking observation

`src/domain/types.ts` still contains the unused historical four-value `EntitlementFeature` union. Current production feature resolution and `EntitlementService` no longer consume it, so it does not block this functionality-first review. Do not broaden Attempt 3 solely to remove that dead type unless the implementation naturally touches that surface.

### Architecture Conformance

Not yet accepted. The dynamic feature policy, platform billing-limit ownership, checkout-recovery admission gate, preference preservation, and reinstall monotonicity are functionally sound. Acceptance is blocked only on making pending initial subscription reconciliation compatible with ARCH-017's new monotonic onboarding timing.

## Architect Review — Attempt 3

### Review Status

**Changes Requested — remove the remaining onboarding gate from periodic initial-subscription reconciliation**

### Scope of this review

This is a functionality-first review. Attempt 3 is not being reopened for exhaustive testing, lint coverage, code style, or unrelated cleanup.

Attempt 3 correctly fixed the queued `BillingSubscriptionReconciliationService` path requested by the Attempt-2 review. Preserve all of the following exactly unless a change is mechanically required by the correction below:

```text
initial activation classification in BillingSubscriptionReconciliationService no longer requires onboardingCompleted=false
completeVerifiedFree no longer uses onboarding as a CAS prerequisite
completeVerifiedPaid no longer uses onboarding as a CAS prerequisite
applyOtherCurrentPlan no longer uses onboarding as a CAS prerequisite
completeReinstallWithoutContract performs no onboardingCompleted write
dynamic persisted Feature keys remain in use
MERCHANT_OPT_IN remains gated by ShopFeaturePreference + current plan capability
ALWAYS_ENABLED remains independent of shop preference
PlatformBillingPolicy + active ShopBillingPolicyOverride remain the outbound-limit authority
checkout_recovery remains enforced before recovery admission/reservation
Background plan transitions do not mutate ShopFeaturePreference
```

Do not redesign any of those areas in Attempt 4.

### Functional defect

`src/services/billing-reconciliation.service.ts` still treats `ShopSettings.onboardingCompleted=false` as authority for an initial pending Subscription.

The current `applySubscription(...)` implementation contains this read:

```ts
const settings = await this.database.shopSettings.findUnique({
  where: { shopId },
  select: { onboardingCompleted: true },
});
```

and then two initial-pending branches whose first predicate is:

```ts
settings?.onboardingCompleted === false
```

This is incompatible with ARCH-017. `onboardingCompleted=true` is a historical Shopify managed-pricing milestone. It may already be true while durable Subscription state is still:

```text
status = NO_CONTRACT
planId = null
pendingPlanId != null
pendingShopifyPlanHandle != null
```

The periodic billing reconciler runs before queued subscription reconstruction in the billing worker. Therefore it can observe this legitimate post-callback state before `BillingSubscriptionReconciliationService` completes the initial transition.

With `onboardingCompleted=true`, the two special initial-pending branches are currently skipped. The method can then fall through to generic provider projection and consume the pending initial state without the canonical initial-activation transition.

That is a functional billing-state race and blocks acceptance.

---

## Attempt 4 deterministic correction contract

### Objective

Make the periodic `BillingReconciliationService` produce the same initial-pending result for identical Subscription/provider state regardless of whether:

```text
ShopSettings.onboardingCompleted = false
```

or:

```text
ShopSettings.onboardingCompleted = true
```

`ShopSettings.onboardingCompleted` MUST NOT decide whether an initial Subscription is eligible for periodic reconciliation.

### Files allowed to change

Implementation changes are limited to:

```text
src/services/billing-reconciliation.service.ts
tests/unit/services/billing-reconciliation.service.test.ts
```

The parent task Completion Report may also be updated through the normal task workflow.

Do not change another production file.

If the correction cannot be implemented using the existing public `BillingSubscriptionReconciliationService.activateInitialPaid(...)` method and the existing `Subscription` fields, stop and return the concrete blocker to `moda_architect` rather than expanding scope.

### Step 1 — remove the periodic ShopSettings onboarding read

Open:

```text
src/services/billing-reconciliation.service.ts
```

Inside `applySubscription(...)`, find the exact block immediately after the existing Subscription/lifecycle reconciliation logic:

```ts
const settings = await this.database.shopSettings.findUnique({
  where: { shopId },
  select: { onboardingCompleted: true },
});
```

Delete that block completely.

After Attempt 4, `applySubscription(...)` must not query `ShopSettings` solely to determine initial activation eligibility.

Do not replace the deleted read with another ShopSettings read.

### Step 2 — remove onboarding from the mismatch-protection branch

Immediately after the deleted settings read, the first special branch currently begins with:

```ts
if (
  settings?.onboardingCompleted === false
  && existing?.status === SubscriptionProjectionStatus.NO_CONTRACT
```

Change this branch so that it begins with:

```ts
if (
  existing?.status === SubscriptionProjectionStatus.NO_CONTRACT
```

Preserve every other predicate in that branch unchanged unless TypeScript formatting requires a mechanical edit.

In particular preserve:

```text
existing.planId === null
existing.pendingPlanId !== null
plan?.active
plan.kind === BillingPlanKind.PAID_METERED
plan.id === existing.pendingPlanId
provider.planHandle / plan.shopifyPlanHandle mismatch checks against existing.pendingShopifyPlanHandle
```

Preserve the existing result:

```ts
return { billingPeriodId: null, packMeterHandle: null };
```

This branch must continue to prevent a mismatched provider handle from falling into generic projection.

### Step 3 — remove onboarding from the matching initial-pending branch

The next special branch currently begins with:

```ts
if (
  settings?.onboardingCompleted === false
  && existing?.status === SubscriptionProjectionStatus.NO_CONTRACT
```

Change it so that it begins with:

```ts
if (
  existing?.status === SubscriptionProjectionStatus.NO_CONTRACT
```

Preserve the remaining durable-state predicates:

```text
existing.planId === null
existing.pendingPlanId !== null
existing.pendingShopifyPlanHandle === provider.planHandle
```

Do not add an `onboardingCompleted===true` requirement.

Do not add any replacement ShopSettings condition.

### Step 4 — preserve canonical Paid initial activation

Inside the matching initial-pending branch, preserve the existing Paid guard:

```ts
if (plan?.active && plan.id === existing.pendingPlanId && plan.kind === BillingPlanKind.PAID_METERED) {
```

and preserve the existing call to:

```ts
new BillingSubscriptionReconciliationService(...).activateInitialPaid(...)
```

Do not copy or reimplement `activateInitialPaid` transaction logic in `billing-reconciliation.service.ts`.

Do not replace this with direct `subscription.upsert`, `billingPeriod.upsert`, or manual entitlement-counter mutations.

The canonical method remains responsible for initial Paid BillingPeriod integrity, included recovery-credit entitlement creation, lifetime-Free state, and pending-state concurrency checks.

After the optional Paid activation call, preserve the branch's unconditional:

```ts
return { billingPeriodId: null, packMeterHandle: null };
```

That return is required for both Free and Paid pending initial selections so generic projection cannot consume the state.

### Step 5 — required behaviour for initial Free

For this durable state:

```text
Subscription.status = NO_CONTRACT
Subscription.planId = null
Subscription.pendingPlanId = <Free plan id>
Subscription.pendingShopifyPlanHandle = provider.planHandle
provider resolves to that Free BillingPlan
```

the matching initial-pending branch must return before generic projection.

It must NOT call `activateInitialPaid(...)` because the plan is Free.

It must NOT call the generic `subscription.upsert` projection path.

This behaviour must be identical whether onboarding is false or true.

### Step 6 — required behaviour for matching initial Paid

For this durable state:

```text
Subscription.status = NO_CONTRACT
Subscription.planId = null
Subscription.pendingPlanId = <Paid plan id>
Subscription.pendingShopifyPlanHandle = provider.planHandle
provider resolves to the same active PAID_METERED BillingPlan
```

periodic reconciliation MUST call the existing canonical `activateInitialPaid(...)` path and then return before generic projection.

This behaviour must be identical whether onboarding is false or true.

### Step 7 — required behaviour for provider/pending-plan mismatch

For an initial pending Paid Subscription where the local pending identity does not match provider truth, preserve the state rather than projecting the provider plan generically.

For both onboarding values, the periodic reconciler must:

```text
not call generic subscription.upsert for the provider plan
not clear pendingPlanId
not clear pendingShopifyPlanHandle
not manufacture successful initial activation
not create a generic BillingPeriod for the mismatched provider plan
return from the existing mismatch-protection branch
```

Do not change the existing mismatch identity rules in Attempt 4. Only remove onboarding as a prerequisite for applying them.

### Step 8 — provider-null retry path is not reopened

The `if (!provider)` branch already preserves existing pending intent and advances `nextReconcileAt` without reading onboarding.

Do not redesign it in Attempt 4.

Do not add onboarding logic to it.

### Step 9 — established Subscription behaviour is not reopened

Do not change logic for:

```text
established ACTIVE/TRIALING subscriptions
scheduled plan changes
same-plan rollover
FROZEN reconciliation
provider cancellation/lifecycle reconciliation
usage reconciliation
recovery-credit purchase reconciliation
ARCH-011/proration behaviour
```

Do not change generic projection except as a consequence of the two initial-pending branches returning correctly for both onboarding values.

### Step 10 — exact focused test changes

Open:

```text
tests/unit/services/billing-reconciliation.service.test.ts
```

Use the existing tests around the current initial-pending rotation behaviour. Do not create a separate broad lifecycle suite.

#### Test A — Free pending initial selection

Current test:

```text
does not consume an unresolved initial activation when rotation sees it current
```

Convert this test to execute the same scenario for both:

```ts
[false, true]
```

values of `onboardingCompleted`.

`it.each([false, true])(...)` is preferred.

For both values, assert at minimum:

```ts
expect(test.database.subscription.upsert).not.toHaveBeenCalled();
```

Also assert that generic BillingPeriod projection was not used if the harness exposes that mock:

```ts
expect(test.database.billingPeriod.upsert).not.toHaveBeenCalled();
```

Because `applySubscription(...)` no longer reads ShopSettings for this decision, it is valid and preferred to additionally assert:

```ts
expect(test.database.shopSettings.findUnique).not.toHaveBeenCalled();
```

provided no unrelated code in that scenario legitimately calls it.

#### Test B — matching Paid pending initial selection

Current test:

```text
uses canonical paid activation for a pending initial target during rotation
```

Convert this scenario to run for both onboarding values.

For both values preserve the existing proof that canonical activation occurred, including the existing assertions that:

```text
generic billingPeriod.upsert was not used
the canonical transaction created the paid BillingPeriod
the included-recovery entitlement counter was created/upserted
```

Do not weaken those assertions.

The canonical activation transaction may still write:

```ts
onboardingCompleted: true
```

idempotently. That write is allowed. Attempt 4 removes onboarding as an eligibility predicate; it does not prohibit successful activation from persisting the true milestone.

#### Test C — provider/pending-plan mismatch

Current test:

```text
leaves a same-local-plan handle drift pending during rotation
```

Convert this scenario to run for both onboarding values.

For both values preserve/assert:

```ts
expect(test.database.billingPeriod.upsert).not.toHaveBeenCalled();
expect(test.database.subscription.upsert).not.toHaveBeenCalled();
expect(test.database.subscription.updateMany).not.toHaveBeenCalled();
```

Do not change the scenario into a successful activation case.

#### Test D — existing trial/retry coverage

Do not rewrite the existing:

```text
re-observes an unsupported paid trial with a null schedule and later activates its exact cycle
```

flow unless a minimal fixture adjustment is mechanically required after removal of the periodic ShopSettings read.

Its billing semantics are not reopened.

### Step 11 — repository search after editing

From the `moda-interact-background` task worktree run:

```bash
grep -n "onboardingCompleted" src/services/billing-reconciliation.service.ts
```

Expected Attempt-4 result:

```text
no matches
```

If a remaining match exists in `billing-reconciliation.service.ts`, inspect it. Do not submit Attempt 4 while that service still uses onboarding as an initial-activation predicate.

Also run:

```bash
grep -RInE \
  "onboardingCompleted[[:space:]]*===[[:space:]]*false|onboardingCompleted[[:space:]]*!==[[:space:]]*true" \
  src/services
```

Do not blindly change every result. Inspect results only for billing initial-activation/reconciliation authority. Existing unrelated lifecycle/reporting uses are outside scope.

### Step 12 — validation commands

Use the scripts that currently exist in `moda-interact-background/package.json`.

Run, in this order:

```bash
npm run prisma:generate
npm run prisma:validate
npx vitest run tests/unit/services/billing-reconciliation.service.test.ts
npm run test:unit
npm test
npm run build
git diff --check
```

There is no separate `lint` script and no separate `typecheck` script in the submitted repository. Do not invent either command. `npm run build` is the required TypeScript compilation check.

If an existing documented baseline failure appears unchanged, reference the relevant baseline ID in the Completion Report. Any failure caused by either Attempt-4 changed file is blocking.

### Step 13 — Completion Report requirements

Return the task to `review`, not `complete`.

The Attempt-4 Completion Report must record the exact:

```text
implementation commit
parent report commit
accepted DATABASE-001 revision/materialized database gitlink
focused billing-reconciliation test count/result
unit test count/result
full-suite count/result
Prisma generate result
Prisma validate result
build result
git diff --check result
physical implementation worktree path
physical parent task worktree path
push evidence for both task branches
```

It must explicitly state all of the following functional outcomes:

```text
1. BillingReconciliationService no longer reads ShopSettings.onboardingCompleted to classify initial pending activation.

2. Pending initial Free is protected from generic projection for both historical onboarding values.

3. Matching pending initial Paid uses BillingSubscriptionReconciliationService.activateInitialPaid(...) for both historical onboarding values.

4. Provider/pending-plan mismatch remains pending and cannot fall through to generic projection for either historical onboarding value.

5. The accepted Attempt-3 queued reconciliation correction and reinstall monotonicity remain unchanged.
```

The prior Completion Report text currently records parent report commit `515f5fda4f69d9588bfc7a8e52e577ad84d41b4a`, while the Attempt-3 submission message identified `cdd05ff8`.

Attempt 4 must replace stale report metadata with the actual pushed Attempt-4 parent report commit. Do not preserve contradictory current-attempt commit identifiers in the final Completion Report.

### Stop conditions

Stop and return the task to `moda_architect` without speculative changes if any of the following occurs:

```text
1. Removing the two onboarding predicates causes the initial-pending branches to become ambiguous for established Subscription state.

2. The existing activateInitialPaid(...) method cannot be reused without changing its public contract.

3. Correctness requires a schema/database change.

4. Correctness requires changing ARCH-011/proration semantics.

5. Correctness requires changing dynamic Feature policy, ShopFeaturePreference, checkout-recovery admission, or outbound policy resolution.

6. Correctness requires changing another production service rather than the two authorised files.
```

Do not resolve a stop condition by inventing a new architecture or silently expanding the task.

### Acceptance invariant

Attempt 4 is functionally complete only when this statement is true:

```text
Holding Subscription state and provider truth constant, changing only
ShopSettings.onboardingCompleted from false to true does not change the
periodic reconciler's treatment of an initial pending Free or Paid selection.
```

### Architecture Conformance

Not yet accepted. Attempt 3 correctly fixed queued reconciliation. Attempt 4 is limited to removing the same obsolete onboarding authority from the periodic billing reconciler while preserving all already-correct ARCH-017 Background behaviour.

## Architect Review — Attempt 4 — Accepted

### Review Status

**Accepted — Complete.**

Architect re-review accepts Attempt 4. The functional blocker from Attempt 3 is corrected at the periodic billing-reconciliation boundary without reopening the already-correct ARCH-017 Background implementation.

The reviewed production state now satisfies the required onboarding invariant:

```text
Holding Subscription state and provider truth constant, changing only
ShopSettings.onboardingCompleted from false to true does not change the
periodic reconciler's treatment of an initial pending Free or Paid selection.
```

Specifically:

```text
BillingReconciliationService.applySubscription(...)
  - no longer reads ShopSettings.onboardingCompleted to classify an initial pending Subscription;
  - protects matching initial Free from generic subscription/BillingPeriod projection for both historical onboarding values;
  - delegates matching active PAID_METERED initial activation to
    BillingSubscriptionReconciliationService.activateInitialPaid(...) for both historical onboarding values;
  - preserves the provider/pending-handle mismatch guard for both historical onboarding values; and
  - returns from both initial-pending branches before generic provider projection can consume pending state.
```

The accepted queued reconciliation correction remains intact: `BillingSubscriptionReconciliationService.reconcileJob(...)` classifies initial activation from durable Subscription state rather than requiring `onboardingCompleted=false`, and its initial completion paths use pending Subscription identity as their concurrency/staleness authority.

The earlier ARCH-017 Background functionality also remains conformant:

```text
- effective features are dynamic persisted Feature keys rather than a fixed Prisma enum/list;
- ALWAYS_ENABLED and MERCHANT_OPT_IN semantics are resolved from current plan mappings, Feature.active and ShopFeaturePreference;
- Background does not create, update or delete ShopFeaturePreference during plan transitions;
- outbound soft/hard/terminal limits resolve from PlatformBillingPolicy plus an active ShopBillingPolicyOverride;
- checkout_recovery is checked before recovery reservation/admission mutations;
- reinstall/no-contract reconciliation never writes onboardingCompleted=false.
```

Validation submitted for Attempt 4 and accepted as supporting evidence:

```text
focused billing-reconciliation tests: PASS (44)
unit tests:                          PASS (1,035)
full suite:                          PASS (1,039; 20 skipped)
Prisma generation:                   PASS
Prisma validation:                   PASS
build / TypeScript compilation:      PASS
git diff --check:                    PASS
```

The submitted implementation commit is `fd267c8`; the submitted parent report commit is `cc7fca2f`. The materialized database revision is `22d56f41`, containing the architect-accepted DATABASE-001 revision as an ancestor.

The historical unused four-value `EntitlementFeature` union in `src/domain/types.ts` remains a non-blocking observation because the reviewed production entitlement/effective-policy paths do not consume it. No further implementation attempt is required solely to remove that dead type.

`ARCH-017-BACKGROUND-001` is therefore Complete at Attempt 4. This acceptance does not create, authorize or start a terminal ARCH-017 system-test task; the existing manual-testing checkpoint remains in force.
