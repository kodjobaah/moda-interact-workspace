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
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-09-18T21:15:27Z
attempt: 3
depends_on:
- ARCH-017-DATABASE-001
enables: []
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
tests/unit/services/effective-billing-policy.service.test.ts
tests/unit/services/recovery-billing.service.test.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
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
focused unit/integration tests for the above
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

Ready for architect review. ARCH-017 Background changes are implemented and validated on attempt 2.

### Implementation

- `src/services/effective-billing-policy.service.ts`: removed the Prisma feature enum and plan-owned outbound fields; resolves dynamic Feature keys, active plan mappings, ShopFeaturePreference opt-ins, platform defaults, active shop overrides, and fail-closed outbound validation.
- `src/services/entitlement.service.ts`: accepts arbitrary persisted feature-key strings and checks the effective feature set.
- `src/services/recovery-billing.service.ts`: requires the local `checkout_recovery` capability before reservation or usage mutation.
- `src/services/billing-subscription-reconciliation.service.ts`: no-contract reinstall reconciliation no longer resets onboarding history.
- Focused tests cover dynamic feature activation, policy limits/overrides, recovery admission, and onboarding preservation.

### Dependency Evidence

- Accepted DATABASE-001 implementation revision: `3c7179825c3e12af1d6db805b8a2a73c61c2097c` (`fix(database): tighten ARCH-017 billing schema validation`).
- Materialized implementation database gitlink: `22d56f41dafd2fd6784058ef0691b1269019b4b2`, which contains the accepted revision as an ancestor and provides Feature, ShopFeaturePreference, FeatureActivationMode, and platform policy models.
- No database submodule files or gitlinks were edited by this task.

### Validation

- `npm run prisma:generate`: passed.
- `npm run prisma:validate`: passed.
- Focused four-service Vitest run: 248 passed.
- `npm run test:unit`: 1,032 passed.
- `npm test`: 1,036 passed, 20 skipped; 11 test files skipped by repository configuration.
- `npm run build` (Prisma generate + `tsc`): passed.
- `git diff --check`: passed.
- No separate `typecheck` or `lint` scripts exist in `package.json`; build TypeScript compilation was used.
- Legacy production search found no `BillingPlanFeatureIdentifier` or BillingPlan outbound-limit references; `terminalMessageReservedSlots` remains only as the effective policy field, platform/override input, validation, and outbound calculation.

### Worktree / Git Evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-017-BACKGROUND-001`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-017-BACKGROUND-001`.
- Implementation commit: `cdb6e4d` (`feat(background): resolve dynamic billing feature policy`), pushed to `origin/task/ARCH-017-BACKGROUND-001`.
- Parent report commit: `ce710095` (`chore(task): return BACKGROUND-001 for review`), pushed to `origin/task/ARCH-017-BACKGROUND-001`.
- No main branch was modified and no Architect Review section was edited.

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
