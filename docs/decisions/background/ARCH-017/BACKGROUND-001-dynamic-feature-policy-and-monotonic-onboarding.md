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
claimed_at: 2026-09-18T20:30:45Z
attempt: 2
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

Blocked pending correction of the prepared database submodule revision. No Background source or test files were changed, and no implementation commit was created.

### Blocking Evidence

- The authoritative ARCH-017-DATABASE-001 Completion Report identifies accepted database implementation commit `3c7179825c3e12af1d6db805b8a2a73c61c2097c` (`fix(database): tighten ARCH-017 billing schema validation`).
- The prepared Background implementation worktree records database gitlink commit `3f8bc8aae7f6d39de960d7b52e8791d5e346be31` (`feat(database): persist inbound media transcription state (#30)`).
- The prepared revision still contains `BillingPlanFeatureIdentifier`, `BillingPlan.defaultOutboundSoftLimit`, `BillingPlan.defaultOutboundHardLimit`, and `BillingPlan.terminalMessageReservedSlots`, and has no `Feature`, `ShopFeaturePreference`, or `FeatureActivationMode` models. It therefore does not satisfy the dependency contract required by this task.
- The accepted commit object is present in the database repository, but the Background gitlink is not advanced to it. Per the task stop conditions, implementing against the old contract would require editing the database submodule or fabricating incompatible local types, both out of scope.

### Validation

- `git -C database rev-parse HEAD`: `3f8bc8aae7f6d39de960d7b52e8791d5e346be31`.
- `git -C database show -s --format='%H %s' HEAD`: `3f8bc8aae7f6d39de960d7b52e8791d5e346be31 feat(database): persist inbound media transcription state (#30)`.
- Schema inspection confirmed the dependency mismatch described above.
- No Prisma generation, tests, build, typecheck, lint, or diff validation was run because the required database contract is absent and the task explicitly requires stopping in this condition.

### Worktree / Git Evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-017-BACKGROUND-001`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-017-BACKGROUND-001`.
- Both worktrees were clean before this report-only update.
- Implementation commit: none.
- Parent report commit: produced by the authorized report update.
- No database submodule files were edited; no main branch was modified.

### Required Resolution

Advance the Background branch's database gitlink to accepted DATABASE-001 commit `3c7179825c3e12af1d6db805b8a2a73c61c2097c` (or rerun the prepared launcher with a corrected dependency packet), then resume this same task attempt. No Architect Review section was edited.
