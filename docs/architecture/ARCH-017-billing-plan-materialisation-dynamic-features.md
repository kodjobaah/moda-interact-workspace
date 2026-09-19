---
id: ARCH-017
title: Billing-plan materialisation, dynamic features, and billing-policy ownership
status: In Progress
coordinator: moda_architect
created: 2026-09-18
updated: 2026-09-19
---

# ARCH-017: Billing-plan materialisation, dynamic features, and billing-policy ownership

## Status

In Progress.

This architecture is intentionally non-prorated. ARCH-011 is not part of this release and MUST NOT be used to introduce same-cycle plan segments, prorated allowance arithmetic or same-cycle downgrade/upgrade machinery.

## Problem

The current runtime assumes an operational `BillingPlan` already exists before the first Shopify subscription callback. `prepareFreeActivation`, `preparePaidActivation` and generic subscription projection lookup resolve only `BillingPlan.shopifyPlanHandle`. Therefore an active `MerchantPricingPlan` can be selectable and approved by Shopify while Moda still projects the resulting subscription as `UNMAPPED` simply because the runtime `BillingPlan` has not yet been materialised.

The current model also has four additional structural problems:

1. `BillingPlanFeatureIdentifier` is a Prisma enum. The feature catalogue is closed at deploy time and Admin cannot add feature definitions without a schema/code deployment.
2. `BillingPlanFeature` currently represents plan capability but there is no separate durable shop-level opt-in preference for optional capabilities.
3. `defaultOutboundSoftLimit`, `defaultOutboundHardLimit` and `terminalMessageReservedSlots` are stored on `BillingPlan` even though they are platform/shop operational policy rather than commercial-plan identity.
4. reinstall reconciliation can reset `ShopSettings.onboardingCompleted` to `false`, conflating historical onboarding completion with current subscription state.

## Goals

- lazily materialise an operational `BillingPlan` from a known active `MerchantPricingPlan` when Shopify callback/reconciliation first needs it;
- keep `MerchantPricingPlan` and `BillingPlan` physically independent, related only by the same unique `shopifyPlanHandle` at runtime;
- make `UNMAPPED` mean a genuinely unresolved Shopify plan identity, not merely an unmaterialised known catalogue plan;
- make feature definitions durable database catalogue rows instead of a fixed feature enum;
- let Admin define the feature set supported by each MerchantPricingPlan;
- preserve `BillingPlanFeature` as the runtime projection of a plan's supported capabilities;
- add shop-level optional feature preferences that survive plan changes;
- make checkout recovery a mandatory system feature for every MerchantPricingPlan;
- make MerchantPricingPlan durable after a BillingPlan has been materialised from the same handle;
- forbid deletion and Shopify-handle reuse for durable plans while retaining deactivate/reactivate and permitted edit operations;
- synchronize operationally relevant edits of a durable MerchantPricingPlan to its BillingPlan transactionally;
- move outbound soft/hard defaults and terminal-message reservation from BillingPlan to PlatformBillingPolicy, with optional per-shop overrides;
- make onboarding completion monotonic at the application lifecycle level.

## Non-goals

- ARCH-011 prorated subscriptions;
- same-cycle BillingPlan segmentation;
- automatic implementation of arbitrary newly-created Feature behaviour;
- changing Shopify managed-pricing configuration itself;
- replacing current purchased-credit/top-up pricing architecture;
- adding a new Shared package contract;
- creating the final system-test task in this initiative yet.

## Core identity rule

There is NO database relation between `MerchantPricingPlan` and `BillingPlan`.

```text
MerchantPricingPlan.shopifyPlanHandle   UNIQUE
BillingPlan.shopifyPlanHandle           UNIQUE
```

The handle is the runtime correlation key only.

`MerchantPricingPlan.shopifyPlanHandle` remains globally unique even when a plan is inactive. Deactivation does not free the handle for another row.

## MerchantPricingPlan durability

Add:

```text
MerchantPricingPlan.materializedAt DateTime?
```

Meaning:

```text
materializedAt == null     -> not yet durable
materializedAt != null     -> durable forever
```

The first successful creation/resolution of a corresponding BillingPlan from that MerchantPricingPlan sets `materializedAt` if it is null. It is never cleared.

Durable plan rules:

- cannot be deleted;
- `shopifyPlanHandle` remains immutable;
- `planKind` becomes immutable;
- may be deactivated/reactivated;
- may edit allowed commercial/presentation properties;
- may add/remove supported dynamic features;
- edits that affect BillingPlan runtime projection are reconciled to the BillingPlan in the same Admin transaction;
- `MerchantPricingPlan.isActive` MUST NOT be copied to `BillingPlan.active`.

`MerchantPricingPlan.isActive` answers: "may a merchant newly select this catalogue plan?"

`BillingPlan.active` answers: "may existing runtime billing execute this operational plan?"

These are intentionally different controls.

## Normal recovery usage-meter identity

`MerchantPricingUsageEvent[]` are ARCH-014 top-up/credit-pack offers. They MUST NOT be guessed/reused as the normal paid recovery meter during automatic BillingPlan materialisation.

Add a distinct MerchantPricingPlan field:

```text
shopifyRecoveryUsageEventHandle String?
```

Rules:

- FREE -> null;
- PAID_METERED -> required by Admin before the plan can be activated/saved as operationally complete;
- lazy materialisation copies it to `BillingPlan.shopifyUsageEventHandle`;
- current `MerchantPricingUsageEvent[]` remains top-up catalogue data and is unchanged.

## Lazy BillingPlan materialisation

```text
verified/requested Shopify plan handle
        |
        v
find BillingPlan(handle)
        |
        +-- usable active plan found ----------------------> use it
        |
        +-- existing BillingPlan found but inactive ------> fail closed / SYNC_ERROR
        |
        +-- no BillingPlan
                |
                v
        find active MerchantPricingPlan(handle)
                |
                +-- none -------------------------------> UNMAPPED
                |
                +-- found but invalid/incomplete -------> SYNC_ERROR
                |
                +-- valid
                        |
                        v
                create/upsert BillingPlan
                create BillingPlanFeature projection
                set materializedAt once
                        |
                        v
                continue normal activation/reconciliation
```

Materialisation MUST be idempotent under concurrent callbacks. Unique `BillingPlan.shopifyPlanHandle` is the database arbiter; duplicate-race recovery rereads the winner instead of producing an error to the merchant.

Materialised fields:

```text
MerchantPricingPlan.displayName
    -> BillingPlan.name

MerchantPricingPlan.planKind
    -> BillingPlan.kind

MerchantPricingPlan.shopifyRecoveryUsageEventHandle
    -> BillingPlan.shopifyUsageEventHandle

PAID_METERED MerchantPricingPlan.includedRecoveryCredits
    -> BillingPlan.includedRecoveryConversationAllowance

FREE
    -> BillingPlan.includedRecoveryConversationAllowance = null

new runtime plan
    -> recoveryCreditPackEnabled = false
    -> recoveryCreditsPerPack = null
    -> shopifyRecoveryCreditPackEventHandle = null

MerchantPricingPlanFeature[]
    -> BillingPlanFeature[]
```

The existing ARCH-014 MerchantPricing usage-event catalogue remains the top-up source; ARCH-017 does not reintroduce the legacy BillingPlan credit-pack definition as catalogue authority.

## Dynamic feature model

Replace fixed `BillingPlanFeatureIdentifier` with database catalogue state.

```text
Feature
  key                    immutable unique string
  displayName
  description?
  active
  activationMode         ALWAYS_ENABLED | MERCHANT_OPT_IN
  systemRequired

MerchantPricingPlanFeature
  merchantPricingPlanId
  featureId

BillingPlanFeature
  planId
  featureId
  enabled

ShopFeaturePreference
  shopId
  featureId
  enabled
```

Initial system feature rows:

```text
checkout_recovery   ALWAYS_ENABLED   systemRequired=true
ai_conversations    MERCHANT_OPT_IN  systemRequired=false
product_search      MERCHANT_OPT_IN  systemRequired=false
order_support       MERCHANT_OPT_IN  systemRequired=false
```

A dynamic database Feature definition is authoritative catalogue data. Generic runtime code MUST NOT maintain a central registry, enum, union, or exhaustive list of Feature keys. Adding a Feature through Admin must not require Background, Shopify, or Admin code merely so generic catalogue/entitlement processing can recognize it. A component that implements concrete behavior for one capability may reference that capability's stable `Feature.key` locally at the implementation boundary; that local reference is not a catalogue registry and must not enumerate unrelated features.

Deactivating a non-system Feature is a global availability switch. It does not delete MerchantPricingPlanFeature, BillingPlanFeature or ShopFeaturePreference rows. If later reactivated, the existing plan support and merchant preference relationships become effective again.

## Checkout-recovery invariant

`checkout_recovery` is the mandatory baseline feature.

- It is seeded and cannot be deleted/deactivated through Admin.
- Every MerchantPricingPlan MUST have a `MerchantPricingPlanFeature` mapping to it.
- Admin UI displays it as required/read-only.
- server actions independently enforce it.
- every materialised BillingPlan receives the corresponding BillingPlanFeature mapping.
- checkout recovery does not require a `ShopFeaturePreference` row.

## Optional merchant preferences

For a feature with `activationMode=MERCHANT_OPT_IN`:

```text
effective =
    Feature.active
    AND BillingPlanFeature.enabled
    AND current BillingPlan maps the Feature
    AND ShopFeaturePreference.enabled
```

For `ALWAYS_ENABLED`:

```text
effective =
    Feature.active
    AND BillingPlanFeature.enabled
    AND current BillingPlan maps the Feature
```

ShopFeaturePreference belongs to Shop and is NOT moved, deleted or recreated on plan changes.

If a merchant prefers a feature that a new plan does not support, the preference remains stored but dormant. If a later plan supports the feature again, the preference becomes effective again automatically.

## Durable-plan edit projection

Admin owns catalogue edits. When `materializedAt != null`, save is one transaction:

```text
update MerchantPricingPlan
replace MerchantPricingPlanFeature desired set
find BillingPlan by same shopifyPlanHandle
assert it exists
update allowed runtime projection fields
reconcile BillingPlanFeature to the exact desired feature set
write audit event
commit
```

Runtime projection fields synchronized by ARCH-017:

```text
BillingPlan.name
BillingPlan.shopifyUsageEventHandle
BillingPlan.includedRecoveryConversationAllowance
BillingPlanFeature[]
```

`BillingPlan.kind` does not need to change after durability because `MerchantPricingPlan.planKind` is immutable once durable.

Do NOT synchronize:

```text
MerchantPricingPlan.isActive -> BillingPlan.active
```

## Billing policy ownership

`PlatformBillingPolicy` and `ShopBillingPolicyOverride` are distinct policy layers. `PlatformBillingPolicy` is the platform-wide baseline and safety policy. `ShopBillingPolicyOverride` is an optional shop-owned record; each non-null eligible override field replaces the corresponding platform default for that shop only. Platform-wide pauses and absolute safety ceilings cannot be relaxed by a shop override.

Remove from BillingPlan:

```text
defaultOutboundSoftLimit
defaultOutboundHardLimit
terminalMessageReservedSlots
```

Add to PlatformBillingPolicy:

```text
defaultOutboundSoftLimit
defaultOutboundHardLimit
terminalMessageReservedSlots
```

Add optional per-shop override:

```text
ShopBillingPolicyOverride.terminalMessageReservedSlots Int?
```

Effective policy:

```text
effectiveHard = min(
  activeOverride.outboundHardLimit ?? platform.defaultOutboundHardLimit,
  platform.absoluteOutboundHardLimit
)

effectiveSoft = min(
  activeOverride.outboundSoftLimit ?? platform.defaultOutboundSoftLimit,
  effectiveHard
)

effectiveTerminalReserved =
  activeOverride.terminalMessageReservedSlots
  ?? platform.terminalMessageReservedSlots
```

Validation always requires terminal reserve >= 1 and < effective hard limit.

## Onboarding invariant

`ShopSettings.onboardingCompleted` means: the merchant has completed the Shopify managed-pricing selection step at least once. It is a Shopify-side commercial milestone, not evidence that Moda successfully mapped, materialised or reconciled the selected plan.

```text
fresh install / no authenticated Shopify billing callback yet -> false
authenticated callback for an ACTIVE shop is entered          -> true
any later Moda billing lifecycle outcome                       -> remains true
```

The authenticated Shopify billing callback owns this one-way transition. After Shopify admin authentication, authenticated-shop resolution and the ACTIVE-shop guard succeed, the callback MUST persist `onboardingCompleted=true` before validating Moda callback parameters and before any provider verification, BillingPlan resolution/materialisation, Subscription/BillingPeriod projection or retry scheduling. Missing callback metadata or any later Moda/provider failure does not undo or suppress this milestone.

`BillingService` MUST NOT use `onboardingCompleted` to decide initial activation, token freshness, pending-intent preservation, reconciliation or billing projection. Those decisions derive from durable `Subscription` state and provider truth. UNKNOWN/UNMAPPED, invalid catalogue state, inactive operational plan, SYNC_ERROR, provider/API failure, cancellation, NO_CONTRACT, reinstall and plan change MUST NOT reset true to false.

## Billing periods

ARCH-010 non-prorated BillingPeriod semantics remain unchanged:

- one effective BillingPlan per BillingPeriod;
- same-plan renewal closes old verified period and opens successor;
- plan change is represented at supported period boundary, not by intra-period segments;
- paid included allowance is period-scoped;
- lifetime Free and purchased credits remain independent of BillingPeriod.

## Rollout classification

PRE-PRODUCTION / BREAKING ROLLOUT.

There are no production customers or production billing lifecycle state to preserve. No production compatibility adapter is required for the removed BillingPlan limit fields or enum feature type. The migration performs only mechanical schema conversion required to keep the development database valid (for example BillingPlanFeature enum -> Feature FK) plus canonical bootstrap/invariant data. It MUST NOT infer ARCH-017 business lifecycle state from existing development rows: no MerchantPricingPlan durability inference, no optional MerchantPricingPlanFeature inference, no recovery-meter inference, and no ShopFeaturePreference inference.

## Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-017-DATABASE-001 | moda_database | Ready | - |
| ARCH-017-BACKGROUND-001 | moda_background | Pending | ARCH-017-DATABASE-001 |
| ARCH-017-SHOPIFY-001 | moda_app | Complete | ARCH-017-DATABASE-001 |
| ARCH-017-SHOPIFY-002 | moda_app | Complete | ARCH-017-SHOPIFY-001 |
| ARCH-017-ADMIN-001 | moda_admin | complete | ARCH-017-DATABASE-001 |

BACKGROUND-001, SHOPIFY-001 and ADMIN-001 intentionally have no dependencies on one another and may execute in parallel after DATABASE-001 is accepted.

SHOPIFY-002 is a follow-on lifecycle correction after SHOPIFY-001. It does not reopen SHOPIFY-001 and has no dependency on BACKGROUND-001 or ADMIN-001.
