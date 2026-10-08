---
id: ARCH-027-API-001
architecture_id: ARCH-027
title: Automatically activate WooCommerce installs on the Moda Free plan
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-10-08T15:33:14Z
attempt: 1
depends_on:
  - ARCH-026-API-002
  - ARCH-027-DATABASE-001
enables:
  - ARCH-027-API-002
created: 2026-10-03
updated: 2026-10-08
---

# Automatically activate WooCommerce installs on the Moda Free plan

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Extend the accepted ARCH-026 WooCommerce installation connection flow so that a
**successfully connected WooCommerce Shop enters Moda already subscribed to the
Free plan**, without creating any Woo recurring billing contract or zero-value Woo
billing operation.

The first successful Woo connection must establish all of the following as one
durable Moda activation outcome:

```text
commerce.Shop
    platform = WOOCOMMERCE
    onboardingCompleted = true

woocommerce.WooCommerceInstallation
    existing ARCH-026 installation/authentication identity

billing.Subscription
    exactly one row for Shop
    plan = operational Free BillingPlan
    status = ACTIVE
    providerSubscriptionId = NULL
    billingPeriodId = NULL

billing.ShopEntitlementCounter
    counter = LIFETIME_FREE_RECOVERY_CREDITS
    granted exactly once for the lifetime of this Shop
```

The task must also make uninstall/reinstall and disconnect/reconnect safe:

```text
first connection
    -> grant lifetime Free credits at most once

reconnect/reinstall of the same durable Shop
    -> preserve the same Subscription/business state
    -> preserve every lifetime Free counter quantity exactly
    -> never grant Free credits again
```

This task is **not** a Woo provider-billing task. Free activation is local Moda
state. It MUST NOT call Woo `/subscriptions`, create a
`BillingOperation`, fabricate a provider contract ID, or create a
provider billing period.

## Context

ARCH-026 establishes the secure Woo installation boundary:

```text
POST /v1/woocommerce/installations/connect
    -> prove live control of canonical WordPress/Woo site
    -> first connection creates Shop + WooCommerceInstallation
    -> reconnect recovers the same Shop/installation and rotates credentials
    -> authenticated requests resolve authoritative shopId server-side
```

ARCH-026 deliberately stopped before onboarding/billing. Its accepted reconnect
contract preserves `Shop.id`, `WooCommerceInstallation.id` and all merchant/business
state and does not reset onboarding, subscription, billing or entitlement state.
ARCH-027 now intentionally extends the **post-proof connection transaction** with
the initial local Free activation required by the Woo product experience.

The current Shopify implementation already contains the business mechanics this task
must preserve conceptually:

- an operational `BillingPlan` is materialised from `MerchantPricingPlan` rather
  than creating a second product catalogue;
- `Subscription.shopId` is unique, so one Shop has at most one Moda Subscription;
- `ShopEntitlementCounter` has a unique `(shopId, counter)` key;
- the first lifetime Free allocation comes from
  `PlatformBillingPolicy.default.lifetimeFreeRecoveryAllowance`;
- an existing lifetime Free counter is never reset merely because activation is
  replayed.

Woo differs only in provider mechanics: a Free Woo merchant has no recurring Woo
contract at all.

ARCH-027-DATABASE-001 adds Woo billing persistence for later paid and one-time-charge
flows. This task consumes that accepted database baseline but does not create or
mutate Woo billing-operation/receipt rows.

### Product invariant

The advertised Woo application is Free to install. Therefore a merchant must not
need to choose a plan before entering the application for the first time.

The merchant experience is:

```text
install plugin
    -> complete secure Moda connection
    -> Free Moda subscription is already ACTIVE
    -> enter Moda Interact
    -> optionally buy top-ups or change to a paid plan later
```

### Anti-abuse invariant

Lifetime Free credits belong to the durable Moda `Shop`, **not** to a plugin
installation instance, WordPress credential generation, Woo contract or reconnect
attempt.

The task must specifically prevent this abuse:

```text
install
    -> receive Free allocation
uninstall
reinstall
    -> receive second Free allocation     FORBIDDEN
```

The durable anti-replay identities are:

```text
commerce.Shop.id
billing.ShopEntitlementCounter(shopId, LIFETIME_FREE_RECOVERY_CREDITS)
commerce.Shop.onboardingCompleted
```

The following MUST NOT be treated as Free-credit grant identity:

```text
WooCommerceInstallation.id
WooCommerceInstallation.credentialVersion
plugin activation timestamp
connection attemptId
Woo provider contract ID
```

## Scope

Modify only `moda-interact-api` implementation/tests/OpenAPI documentation required
to extend the accepted ARCH-026 connection flow with this automatic local Free
activation, plus the repository's nested `database/` gitlink required to consume the
architect-accepted ARCH-027 database baseline.

Expected implementation areas are conceptually:

```text
src/
  woocommerce/
    installation/
      ... accepted ARCH-026 API-002 connection service ...
    billing/
      initial-free-activation.service.ts
      free-plan-resolution.service.ts
      types.ts

openapi/
  woocommerce-installation-v1.yaml

tests/
  ... focused unit/integration tests ...
```

Exact filenames may differ when the accepted API-002 repository structure provides
clearer existing owners. Do not create parallel connection/authentication
implementations.

### Canonical database dependency

Before implementing this task, update the API repository's nested:

```text
database/
```

gitlink to the architect-accepted `moda-interact-database` `main` commit containing
`ARCH-027-DATABASE-001` and all of its prerequisites.

Generate Prisma from that pinned schema.

Do not copy/redeclare Prisma models in API-local types and do not edit database
schema/migrations in this task.

### Connection-transaction integration

Reuse the accepted `ARCH-026-API-002` connection proof, canonical-site identity,
credential generation, reconnect CAS and authentication implementation.

This task begins **after successful site-control proof**.

For a first connection, the same PostgreSQL transaction that would otherwise commit:

```text
commerce.Shop
woocommerce.WooCommerceInstallation
installation credential digest/version
```

must also complete the initial Free activation before commit.

The first connection transaction therefore becomes conceptually:

```text
site proof succeeded
    -> begin transaction
    -> create/resolve Woo Shop
    -> create WooCommerceInstallation
    -> persist installation credential digest
    -> ensure initial Woo Free activation
         -> resolve/materialise operational Free BillingPlan
         -> establish single ACTIVE Free Subscription
         -> ensure one lifetime Free counter
         -> set Shop.onboardingCompleted = true
    -> commit
    -> return raw installation credential once
```

No network call to Woo or another external service may occur inside this transaction.

If initial Free activation fails, the first connection transaction MUST roll back:

```text
no durable new Shop
no durable WooCommerceInstallation
no Subscription
no new lifetime Free counter
no onboarding completion
no newly issued credential digest
no raw installation credential returned
```

For a reconnect of an existing Shop, run the activation guard inside the same
transaction as API-002's reconnect/credential-rotation CAS. If a never-onboarded
legacy/development Shop requires initial Free activation and that activation fails,
credential rotation/reactivation must roll back so the previously valid durable
connection state is not partially changed.

### Activation lock order

Within the connection transaction, acquire/update durable business state in this
order:

```text
1. commerce.Shop
2. billing.Subscription (when a row exists)
3. billing.ShopEntitlementCounter / billing plan state as required
```

The implementation may use the accepted repository lock helpers or bounded
`SELECT ... FOR UPDATE` statements. It MUST NOT acquire these rows in the reverse
order in another branch of the same activation path.

Global concurrent BillingPlan materialisation for two different Shops must use the
bounded unique-conflict recovery described below rather than globally serialising all
Woo installations.

### Automatic activation eligibility

Read `commerce.Shop.onboardingCompleted` while the Shop row is locked.

#### Already onboarded

If:

```text
Shop.onboardingCompleted = true
```

then automatic Free activation is a strict no-op.

Do not:

- query/require the current Free catalogue to be healthy merely to reconnect;
- change `Subscription.planId` or status;
- clear or create provider subscription state;
- create or modify the lifetime Free counter;
- reset committed/reserved/refunding quantities;
- create billing periods;
- create Woo billing operations.

This rule is what protects paid merchants and previously activated Free merchants
from being forced back onto Free during reinstall/reconnect.

#### Never onboarded

If:

```text
Shop.onboardingCompleted = false
```

then initial Free activation is allowed only when the current Subscription is either:

```text
A. absent
```

or an **empty initial shell** exactly equivalent to:

```text
status = NO_CONTRACT
planId = NULL
providerSubscriptionId = NULL
billingPeriodId = NULL
pendingPlanId = NULL
pendingShopifyPlanHandle = NULL
pendingEffectiveAt = NULL
```

An existing Subscription with any established/pending plan/provider state MUST NOT
be overwritten with Free. Treat that as `INITIAL_FREE_ACTIVATION_CONFLICT`, preserve
all billing state and roll back the connection mutation being attempted.

### Free catalogue resolution

Do not accept a plan identifier from WordPress/browser input for automatic Free
activation.

Server-side, load the Moda pricing catalogue and require exactly one `FREE` plan
record. That plan must satisfy all of the following:

```text
planKind = FREE
isActive = true
allowancePeriod = LIFETIME
recurringAmountMinor = 0
shopifyRecoveryUsageEventHandle = NULL
includedRecoveryCredits is a safe non-negative integer
```

The Admin catalogue currently enforces one Free tier at the application layer; this
API path must nevertheless fail closed rather than selecting arbitrarily if the
durable database contains zero or multiple `FREE` rows.

The Free plan's `includedRecoveryCredits` is catalogue/product metadata. The actual
shop-lifetime Free entitlement grant for this task comes from:

```text
PlatformBillingPolicy.default.lifetimeFreeRecoveryAllowance
```

Do not substitute one field for the other.

### Free operational BillingPlan resolution/materialisation

The source product identity is the resolved `MerchantPricingPlan` row. Woo does not
select or authenticate a Shopify handle.

The current schema does not yet contain a direct
`MerchantPricingPlan -> BillingPlan` foreign key, so materialisation must reuse the
same operational-plan semantics as the existing Shopify
`BillingPlanResolutionService` while keeping the Shopify handle an internal current-
schema bridge only.

For the resolved Free catalogue plan:

1. lookup an existing `BillingPlan` by the catalogue row's current
   `shopifyPlanHandle`;
2. when an existing row is found, require:

```text
active = true
kind = FREE
```

3. when no row exists, validate the same Free catalogue invariants currently used by
   the Shopify resolver, including:
   - the system-required `checkout_recovery` feature mapping exists;
   - no feature mapping resolves to a missing feature;
   - Free has no Shopify recovery usage meter;
   - `includedRecoveryCredits` is a safe non-negative integer;
   - when `merchant_knowledge` is present, there is exactly one mapping, its
     configuration passes `MerchantKnowledgeFeatureConfigurationSchema`, and every
     configured purpose/data-format pair is currently active/compatible;
4. create the operational Free `BillingPlan` with the same current projection shape:

```text
shopifyPlanHandle = catalogue.shopifyPlanHandle   # current schema identity only
name = catalogue.displayName
kind = FREE
active = true
shopifyUsageEventHandle = NULL
includedRecoveryConversationAllowance = NULL
recoveryCreditPackEnabled = false
recoveryCreditsPerPack = NULL
shopifyRecoveryCreditPackEventHandle = NULL
features = copy all catalogue feature mappings as enabled with the same configuration
```

5. when `MerchantPricingPlan.materializedAt` is null, set it once after successful
   resolution/materialisation;
6. if two Shops concurrently race to create the same global operational Free plan,
   recover from the unique constraint by re-reading the winner and validating it;
   do not create duplicate BillingPlans and do not globally serialise all Shops.

This task may implement a bounded API-local Free-plan resolver/materialiser because
the API must perform the local activation transaction. It MUST NOT modify the Shopify
repository or silently change existing Shopify materialisation behaviour.

### Lifetime Free-credit grant

Within the locked activation transaction, read:

```text
ShopEntitlementCounter
where (shopId, counter = LIFETIME_FREE_RECOVERY_CREDITS)
```

If the row already exists:

```text
DO NOT update grantedQuantity
DO NOT update committedQuantity
DO NOT update reservedQuantity
DO NOT update refundingQuantity
DO NOT reset version
```

Reuse it exactly as found.

If the row does not exist, load:

```text
PlatformBillingPolicy.id = "default"
```

and require `lifetimeFreeRecoveryAllowance` to be a safe non-negative integer.
Then create exactly one counter:

```text
shopId = current Shop
counter = LIFETIME_FREE_RECOVERY_CREDITS
grantedQuantity = PlatformBillingPolicy.default.lifetimeFreeRecoveryAllowance
committedQuantity = 0
reservedQuantity = 0
refundingQuantity = 0
```

The existing unique `(shopId, counter)` database key is part of the idempotency
boundary. Handle a same-Shop concurrent conflict by re-reading the existing counter;
never convert a uniqueness conflict into a second grant or reset.

If:

```text
Shop.onboardingCompleted = true
```

but the lifetime counter is missing, reconnect MUST NOT recreate Free credits. That
is an inconsistent durable state requiring separate operational repair, not a reason
to grant credits during reinstall.

### Subscription projection

For an eligible never-onboarded Shop, establish the single local Free subscription
without provider evidence.

The resulting projection is exactly:

```text
shopId = current Shop
planId = resolved/materialised Free BillingPlan.id
status = ACTIVE
observedShopifyPlanHandle = NULL
billingPeriodId = NULL
currentPeriodStart = NULL
currentPeriodEnd = NULL
trialEndsAt = NULL
cancelAtPeriodEnd = false
providerSubscriptionId = NULL
pendingShopifyPlanHandle = NULL
pendingPlanId = NULL
pendingEffectiveAt = NULL
nextReconcileAt = NULL
lastProviderLifecycleState = NULL
lastProviderLifecycleEventId = NULL
lastProviderLifecycleEventAt = NULL
```

Do not fabricate Shopify provider observation state merely because the operational
BillingPlan currently contains Shopify compatibility fields.

Do not create a `BillingPeriod` or `BillingPeriodEntitlementCounter` for this local
Free activation. The Free recovery capacity is shop-lifetime state represented by
`ShopEntitlementCounter`.

Do not create a `BillingOperation`, `WooCommerceBillingWebhookReceipt`,
`RecoveryCreditPurchase` or `UsageEvent`.

After the Subscription and lifetime Free counter are valid in the same transaction,
set:

```text
commerce.Shop.onboardingCompleted = true
```

Normal runtime code must never set it back to false.

### Reinstall/reconnect preservation

The accepted API-002 reconnect path identifies an existing installation by canonical
site identity and preserves the same durable `Shop.id`.

For any Shop whose `onboardingCompleted` is already true, reconnect/reinstall MUST
preserve exactly:

```text
Subscription row/id
Subscription plan/status/provider fields
all BillingPeriods
lifetime Free counter id
lifetime Free grantedQuantity
lifetime Free committedQuantity
lifetime Free reservedQuantity
lifetime Free refundingQuantity
purchased credits
refund state
```

Credential rotation and installation lifecycle changes are allowed only as already
defined by API-002.

A merchant uninstalling and reinstalling the plugin on the same canonical Woo site
must therefore never increase the lifetime Free grant or recreate consumed Free
credits.

## Out of Scope

- Woo paid subscription creation.
- Woo `/subscriptions` calls.
- Woo plan switching or cancellation.
- Woo one-time `/charges` top-up creation.
- Woo webhook ingress or HMAC verification.
- `BillingOperation` creation for Free activation.
- `WooCommerceBillingWebhookReceipt` processing.
- A zero-value recurring Woo contract for Free.
- Billing-plan selection UI.
- Billing/read-model endpoints for the Woo Admin application.
- Top-up UI or purchase history/refund UI.
- Background Woo lifecycle reconciliation.
- Changes to `moda-interact`, `moda-interact-background`, `moda-interact-admin`,
  `moda-interact-woocommerce`, `moda-interact-shared` or `moda-interact-gateway`.
- Database schema/migration changes.
- Removal/renaming of Shopify compatibility fields on `BillingPlan` or
  `Subscription`.
- Cross-domain abuse prevention for a merchant intentionally creating unrelated
  stores/sites with different durable Moda Shop identities. This task prevents
  uninstall/reinstall replay for the **same durable Shop/site identity**.

## Requirements

### R1 — Successful first Woo connection activates Free atomically

A successfully proven first Woo connection does not return a usable installation
credential until Shop creation, installation persistence and initial Free activation
have committed together.

### R2 — Free is local Moda subscription state

The resulting Subscription is ACTIVE Free with `providerSubscriptionId = NULL` and
no Woo recurring contract or Woo billing operation.

### R3 — One Subscription per Shop is preserved

Use the existing unique `Subscription.shopId` projection. This task never creates a
second Subscription for a Shop.

### R4 — Lifetime Free credits are granted at most once

The first eligible activation may create the unique lifetime Free counter. Reconnect,
reinstall, credential rotation and repeated connect attempts must never increase or
reset that grant.

### R5 — Consumed/reserved Free state survives reinstall

If lifetime Free credits have already been committed/reserved/refunding, reconnect
must preserve those quantities exactly rather than reconstructing a fresh balance.

### R6 — Existing paid/established merchant state is never downgraded

An already-onboarded Shop is a strict activation no-op. A never-onboarded Shop with
non-empty subscription state fails closed rather than being overwritten with Free.

### R7 — Exactly one active Free catalogue plan is required

Automatic activation does not accept a plan ID from the plugin. Zero/multiple Free
catalogue rows, inactive Free plan or invalid Free-plan configuration fail closed.

### R8 — Operational BillingPlan is reused/materialised, not duplicated

Woo Free activation converges on the same current operational BillingPlan semantics
used by Shopify. Concurrent materialisation must resolve to one BillingPlan row.

### R9 — Free activation has no BillingPeriod

No provider financial cycle is fabricated for a local Woo Free subscription.

### R10 — Existing lifetime counter is authoritative

When a lifetime Free counter already exists on a never-onboarded Shop, activation may
reuse it but must not change any quantity. `PlatformBillingPolicy` is consulted only
when the counter is absent and a first grant is genuinely required.

### R11 — Reconnect remains connection-safe

When reconnect requires a never-onboarded Free activation and that activation fails,
credential rotation/reactivation is rolled back. Existing durable credentials/state
are not partially replaced.

### R12 — No secret exposure or new browser authority

The task preserves API-002's credential and tenant-authorisation boundary. Browser/
plugin input cannot select `shopId`, Free-plan ID, grant quantity or operational
BillingPlan ID. Logs never contain bootstrap/install credentials or credential
digests.

### R13 — No provider call inside activation transaction

Automatic Free activation performs PostgreSQL/local validation only. No Woo, Shopify,
HTTP or other external network operation occurs inside the transaction.

### R14 — First-install failure is bounded and documented

Use API-002's existing error envelope and add stable connection failure codes where
needed:

```text
FREE_PLAN_CONFIGURATION_UNAVAILABLE
    HTTP 503
    no connection/billing state committed

INITIAL_FREE_ACTIVATION_CONFLICT
    HTTP 409
    existing never-onboarded Shop contains non-empty subscription state;
    no billing/credential mutation committed
```

The accepted OpenAPI document and runtime/tests must agree. Do not expose internal
Prisma/database details in the public error response.

## Work Items

- [ ] Update the API repository's `database/` gitlink to the architect-accepted ARCH-027 database baseline.
- [ ] Extend the accepted API-002 post-proof first-connection transaction with initial Free activation.
- [ ] Extend reconnect transaction handling with the `onboardingCompleted` activation guard without changing API-002 site proof/authentication semantics.
- [ ] Add one bounded initial Woo Free activation service.
- [ ] Resolve exactly one active FREE `MerchantPricingPlan` server-side; accept no client-selected Free plan ID.
- [ ] Validate the deterministic Free catalogue invariants defined by this task.
- [ ] Reuse/materialise the operational Free `BillingPlan` with current Shopify-equivalent materialisation semantics.
- [ ] Handle concurrent global Free BillingPlan materialisation without duplicate rows.
- [ ] Establish the Shop's unique ACTIVE Free Subscription with no provider subscription/billing-period evidence.
- [ ] Reuse an existing lifetime Free counter without changing any quantity.
- [ ] Create the lifetime Free counter from `PlatformBillingPolicy.default` only when it does not already exist on a genuinely first activation.
- [ ] Set shared `Shop.onboardingCompleted=true` only in the same committed activation transaction.
- [ ] Make already-onboarded reconnect/reinstall a strict billing/entitlement no-op.
- [ ] Fail closed rather than overwriting non-empty subscription state on a never-onboarded Shop.
- [ ] Preserve API-002 reconnect credential CAS/rollback behaviour if initial activation fails.
- [ ] Update the accepted installation OpenAPI error contract without changing the successful connection response shape.
- [ ] Add focused unit tests for eligibility, plan validation, operation-plan materialisation mapping and anti-reset behaviour.
- [ ] Add disposable PostgreSQL integration coverage for first activation, replay, uninstall/reinstall, concurrency and rollback.
- [ ] Add structured domain logging through the API's accepted shared logger only where useful; include bounded identifiers/outcome and no secrets.

## Interfaces / Contracts

### Consumed installation principal / connection contract

Owner:

`ARCH-026-API-002`

This task extends the successful connection transaction but does not replace API-002
site proof or authentication.

The authoritative tenant remains server-resolved:

```text
canonical verified site / Woo installation
    -> commerce.Shop.id
```

No browser-supplied Shop identity is accepted.

### Consumed database contracts

```text
commerce.Shop
    platform
    onboardingCompleted

woocommerce.WooCommerceInstallation

billing.MerchantPricingPlan
billing.BillingPlan
billing.Subscription
billing.PlatformBillingPolicy
billing.ShopEntitlementCounter
billing.Feature / BillingPlanFeature / MerchantPricingPlanFeature
merchant-knowledge compatibility tables used by current materialisation validation
```

Schema owner:

`moda_database`

### Produced runtime state

For the first successful Woo activation:

```text
Shop.onboardingCompleted = true

Subscription
    shopId = Shop.id
    planId = Free BillingPlan.id
    status = ACTIVE
    providerSubscriptionId = NULL
    billingPeriodId = NULL

ShopEntitlementCounter
    unique(shopId, LIFETIME_FREE_RECOVERY_CREDITS)
```

No cross-service queue/event contract is introduced by this task.

### Public HTTP contract

Existing owner:

`moda-interact-api`

Document:

```text
openapi/woocommerce-installation-v1.yaml
```

Successful connect/reconnect response shape remains the accepted API-002 shape.
Only bounded failure codes required by automatic activation are added.

## Dependencies

- `ARCH-026-API-002`
- `ARCH-027-DATABASE-001`

`ARCH-026-API-002` must be Complete so this task extends one accepted connection/
authentication implementation rather than inventing another.

`ARCH-027-DATABASE-001` must be Complete so the API pins one accepted ARCH-027
billing schema frontier before later billing API work begins.

## Enables

- `ARCH-027-API-002`

API-002 may build the Shopify-parity Woo billing presentation/read model assuming a
connected Woo merchant already has a deterministic local Free subscription unless
that merchant has subsequently moved to another plan through an accepted billing
lifecycle.

## Acceptance Criteria

- [ ] A first successfully proven Woo connection atomically creates/connects the Shop and leaves it on an ACTIVE Free Moda Subscription before returning the raw installation credential.
- [ ] The first Woo Free Subscription has `providerSubscriptionId = NULL`.
- [ ] The first Woo Free Subscription has no `BillingPeriod` and no current billing-period entitlement counter.
- [ ] No `BillingOperation` is created for automatic Free activation.
- [ ] No Woo `/subscriptions` or other external provider call occurs for Free activation.
- [ ] Automatic activation accepts no client/plugin-supplied plan ID, BillingPlan ID, grant quantity or Shop ID.
- [ ] Exactly one FREE MerchantPricingPlan is required and it must be active, lifetime, zero recurring price and otherwise valid under the specified catalogue rules.
- [ ] Existing operational Free BillingPlan is reused when present and valid.
- [ ] Missing operational Free BillingPlan is materialised with the same current Free projection/feature semantics as Shopify.
- [ ] Concurrent materialisation of the global Free plan results in one operational BillingPlan and successful bounded winner recovery.
- [ ] `MerchantPricingPlan.materializedAt` is set once when appropriate.
- [ ] First activation creates the unique lifetime Free counter from `PlatformBillingPolicy.default.lifetimeFreeRecoveryAllowance` only when that counter is absent.
- [ ] An existing lifetime Free counter is reused without changing granted, committed, reserved, refunding or version values.
- [ ] `Shop.onboardingCompleted` becomes true only in the same successful transaction as Free Subscription/counter establishment.
- [ ] A connection failure caused by invalid/missing Free catalogue or platform policy leaves no newly committed Shop/installation/subscription/counter/credential state.
- [ ] A never-onboarded Shop with non-empty Subscription state is not overwritten with Free and returns the bounded activation-conflict outcome.
- [ ] Reconnect of an already-onboarded Free Shop does not require revalidating the current Free catalogue and changes no billing/entitlement state.
- [ ] Reconnect of an already-onboarded paid Shop preserves the paid Subscription and does not force Free.
- [ ] Uninstall/reinstall of the same canonical Shop does not create a second lifetime Free counter or increase/reset its grant.
- [ ] Uninstall/reinstall after some lifetime Free credits have been consumed preserves committed/reserved/refunding state exactly.
- [ ] Credential rotation/reconnect state rolls back if required first-time Free activation fails.
- [ ] Successful connection response remains API-002-compatible.
- [ ] OpenAPI/runtime/tests agree on `FREE_PLAN_CONFIGURATION_UNAVAILABLE` and `INITIAL_FREE_ACTIVATION_CONFLICT` without leaking internal details.
- [ ] No credential/bootstrap secret/digest appears in logs, traces, errors or snapshots.
- [ ] Existing API-002 connection/authentication tests remain green apart from intentionally updated Free-activation expectations.

## Validation

Inspect the accepted `moda-interact-api/package.json` before execution and run the
repository-declared commands rather than assuming scripts.

Required validation includes:

- [ ] clean dependency installation from the API lockfile;
- [ ] Prisma generation from the pinned ARCH-027 database submodule succeeds;
- [ ] focused unit tests for Free activation eligibility/state machine;
- [ ] focused unit tests for Free catalogue validation and operational BillingPlan mapping/materialisation;
- [ ] focused unit test proving an existing lifetime counter is never reset;
- [ ] focused API-002 connection tests proving first-connect success now yields atomic Free activation;
- [ ] focused reconnect tests proving already-onboarded Free and paid Shops are billing no-ops;
- [ ] disposable PostgreSQL integration: first Woo connection -> exactly one Shop, installation, ACTIVE Free Subscription and lifetime counter;
- [ ] disposable PostgreSQL integration: repeated successful connect/reconnect -> same Shop/subscription/counter IDs and unchanged entitlement quantities;
- [ ] disposable PostgreSQL integration: simulate uninstall/revocation then reconnect -> no second Free grant and no consumed-credit restoration;
- [ ] disposable PostgreSQL integration: two concurrent eligible activation attempts -> one Subscription, one lifetime counter, one grant;
- [ ] disposable PostgreSQL integration: two different Shops concurrently materialising Free -> one global operational Free BillingPlan reused by both;
- [ ] disposable PostgreSQL integration: invalid/missing Free catalogue configuration -> transaction rollback and documented 503 outcome;
- [ ] disposable PostgreSQL integration: missing/invalid PlatformBillingPolicy when first counter is required -> transaction rollback;
- [ ] disposable PostgreSQL integration: existing onboarding=true with missing counter -> reconnect does not manufacture new credits;
- [ ] disposable PostgreSQL integration: never-onboarded non-empty Subscription -> 409 conflict and no billing/credential mutation;
- [ ] OpenAPI validation for the updated connection failure codes;
- [ ] `npm run typecheck`;
- [ ] `npm run lint`;
- [ ] `npm test`;
- [ ] `npm run build`;
- [ ] `git diff --check`;
- [ ] changed-file/worktree checks required by `moda_api`.

PostgreSQL validation must use disposable databases only. Do not point task tests at
shared development, staging or production durable data.

If required PostgreSQL/runtime prerequisites are unavailable, record the exact
blocker in the Completion Report rather than silently weakening the acceptance
contract.

## Stop Condition

After all defined Work Items, Acceptance Criteria and required Validation are
complete:

```text
finish Completion Report
    -> set task status to review
    -> clear active execution claim as required by the normal task protocol
    -> return to moda_architect
    -> STOP
```

Do not begin `ARCH-027-API-002`, paid Woo billing commands, top-up commands,
webhook work, Background reconciliation or Woo UI work.

## Implementation Notes

This task intentionally makes the Woo installation experience differ from Shopify's
initial plan-selection flow while keeping the post-activation product experience
aligned: Woo Marketplace merchants enter Moda on Free automatically and may later
use the same conceptual Billing/plan/top-up experience.

The Free plan's current `BillingPlan.shopifyPlanHandle` value is tolerated only as a
legacy/current-schema operational identity bridge. Do not expose it in Woo API
responses and do not treat it as Woo provider evidence.

Do not use `WooCommerceInstallation.status` as merchant billing state. ACTIVE/REVOKED
continues to describe installation authentication eligibility only.

Do not "repair" an already-onboarded Shop by recreating a missing lifetime Free
counter during reconnect. The anti-abuse rule is intentionally fail-safe: reinstall
must never become a credit minting mechanism.

Do not reset a counter merely because the current platform policy allowance changed.
The grant captured on first activation remains the Shop's lifetime grant evidence.

When logging activation outcomes, prefer bounded semantic outcomes such as:

```text
ACTIVATED_FREE
ALREADY_ONBOARDED
REUSED_EXISTING_LIFETIME_COUNTER
CONFIGURATION_UNAVAILABLE
ACTIVATION_CONFLICT
```

Use the accepted shared logger; do not create an API-local generic logger.

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

- ARCH-026 API-002's accepted connection route and reconnect CAS remain the
  authoritative installation identity/authentication implementation.
- One durable `Shop.id` continues to represent the same canonical Woo site across
  uninstall/reinstall and reconnect.
- The Admin catalogue continues to intend exactly one Free plan; this API path still
  verifies that invariant at runtime rather than trusting it blindly.
- `PlatformBillingPolicy.default.lifetimeFreeRecoveryAllowance` remains the
  authoritative first lifetime Free grant quantity.

### Unresolved Issues

None within this task's bounded automatic-Free activation scope.

### Architectural Concerns

Any implementation fact that requires:

- changing the one-Subscription-per-Shop invariant;
- storing billing state on `WooCommerceInstallation`;
- creating a Woo provider contract for Free;
- issuing Free credits from a new Woo-specific entitlement model;
- weakening API-002 site-control/authentication semantics;
- modifying another repository to complete initial Free activation;

must be returned to `moda_architect` rather than worked around locally.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
