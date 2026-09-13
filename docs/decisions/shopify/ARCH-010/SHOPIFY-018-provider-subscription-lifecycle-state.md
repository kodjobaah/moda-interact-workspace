---
id: ARCH-010-SHOPIFY-018
architecture_id: ARCH-010
title: Expose Shopify-authoritative subscription lifecycle state including freeze
  and unfreeze
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 59
executor: copilot
claimed_at: '2026-09-13T09:44:10Z'
attempt: 3
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHOPIFY-013
- ARCH-010-SHOPIFY-023
enables:
- ARCH-010-SHOPIFY-012
- ARCH-010-SHOPIFY-014
- ARCH-010-SHOPIFY-015
- ARCH-010-SHOPIFY-016
- ARCH-010-SHOPIFY-021
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-SHOPIFY-018: Expose Shopify-authoritative subscription lifecycle state including freeze and unfreeze

## Objective

Extend the merchant-app Shopify billing provider/service read model so billing-management UI can distinguish ACTIVE, FROZEN, cancellation and unresolved provider states without treating local BillingPlan rows as commercial truth.

This task is read-only provider/service work. It does not mutate Subscription or activate/unfreeze anything.

## Inspect before editing

```text
app/services/billing/providers/shopify-billing.provider.ts
app/services/billing/billing.types.ts
app/services/billing/billing.service.ts
SHOPIFY-013 accepted/provider commercial read model
billing provider/service tests
```

## Provider snapshot

Add a read method equivalent to BACKGROUND-015's canonical semantics:

```text
activeSubscription(appId, shopId)
+
latest relevant root events SubscriptionStatus event
```

Prefer one Partner GraphQL HTTP request for the billing-management read.

Filter lifecycle events exactly to:

```text
SUBSCRIPTION_CREATED
SUBSCRIPTION_UPDATED
SUBSCRIPTION_CANCELLATION_SCHEDULED
SUBSCRIPTION_CANCELED
SUBSCRIPTION_FROZEN
SUBSCRIPTION_UNFROZEN
```

Scope by both Shopify app ID and shop ID. Bound history to at most 365 days.

Do not use Admin Billing API subscription status, legacy billing webhooks or local Subscription status as Shopify commercial truth.

## Merchant provider lifecycle read model

Expose a typed result equivalent to:

```ts
type MerchantShopifyLifecycleState =
  | { state: "ACTIVE"; subscription: MerchantShopifySubscriptionState; latestEvent: ... }
  | { state: "FROZEN"; subscription: MerchantShopifySubscriptionState | null; latestEvent: FrozenEvent }
  | { state: "CANCELED"; subscription: null; latestEvent: CanceledEvent }
  | { state: "UNRESOLVED"; subscription: MerchantShopifySubscriptionState | null; latestEvent: ... | null }
  | { state: "NO_ACTIVE_SUBSCRIPTION"; subscription: null; latestEvent: null };
```

Use actual repository types/naming. Preserve these semantics:

- latest effective FROZEN event => `FROZEN`;
- live active subscription + no effective freeze => `ACTIVE`;
- null live subscription + latest CANCELED => `CANCELED`;
- null live subscription + UNFROZEN/CREATED/UPDATED/CANCELLATION_SCHEDULED for an established merchant => `UNRESOLVED`, not canceled;
- truly new/no-contract merchant with no relevant lifecycle evidence may be `NO_ACTIVE_SUBSCRIPTION`;
- provider failure throws/returns verification failure; never substitute local plan data.

## Frozen commercial presentation data

If activeSubscription is null but the latest FROZEN historical event contains provider plan data, preserve the provider plan handle/billing period from that event for display/mapping purposes. Do not fabricate price data that the historical event did not provide.

A local `BillingPlan` lookup may map the Shopify handle to a Moda plan label/features, but mapping is not proof that the Shopify contract is active.

## Important distinction

Do not interpret App Events `ACCOUNT_FROZEN` as merchant subscription freeze. This task uses only Partner subscription lifecycle state `FROZEN`/`SUBSCRIPTION_FROZEN`.

## Required tests

At minimum prove:

1. active live subscription + no freeze returns ACTIVE;
2. latest FROZEN returns FROZEN even when activeSubscription is temporarily non-null;
3. null live subscription + FROZEN returns FROZEN;
4. null + CANCELED returns CANCELED;
5. null + UNFROZEN returns UNRESOLVED for an established merchant;
6. null + no provider history may return NO_ACTIVE_SUBSCRIPTION for fresh/no-contract context;
7. provider plan handle from frozen event is preserved without invented price;
8. mapped/unmapped local plan status remains separate from provider lifecycle state;
9. Partner failure never falls back to local commercial truth;
10. query is scoped to app+shop and bounded to 365 days;
11. existing SHOPIFY-013 active commercial fields remain unchanged for ACTIVE state;
12. no Prisma subscription mutation occurs.

## Non-goals

No dashboard/banner UI, no top-up action, no plan-change action, no Background reconciliation, no Admin and no lifecycle persistence.

## Stop conditions

STOP if root Historical Events subscription status is unavailable in the configured Partner API version. Report the exact provider gap to `moda_architect`; do not use legacy `APP_SUBSCRIPTIONS_UPDATE` or Admin Billing API as a substitute.

## Completion Report

### Status
In Progress.

### Implementation

- Added a Shopify Partner one-request lifecycle snapshot using `activeSubscription` plus root `SubscriptionStatus` events.
- Applied the canonical six lifecycle event filters, app/shop scoping, and a maximum 365-day history window.
- Added strict lifecycle event parsing and typed ACTIVE, FROZEN, CANCELED, UNRESOLVED, and NO_ACTIVE_SUBSCRIPTION service states.
- Preserved the existing SHOPIFY-013 active commercial fields and kept local `BillingPlan` mapping separate from provider lifecycle truth.
- Preserved frozen historical plan handle and billing period without fabricating price data.
- Kept the read path free of `Subscription` mutations.

### Files Changed

- `app/services/billing/providers/shopify-billing.provider.ts`
- `app/services/billing/billing.types.ts`
- `app/services/billing/billing.service.ts`
- `tests/unit/services/shopify-billing.provider.test.ts`
- `tests/unit/services/billing.service.test.ts`

### Validation

- Passed: `npm run prisma:validate`.
- Passed: `npm run prisma:generate`.
- Passed: `./node_modules/.bin/vitest run tests/unit/services/shopify-billing.provider.test.ts` (18 tests).
- Passed: `./node_modules/.bin/vitest run tests/unit/services/billing.service.test.ts -t "lifecycle|provider history|SHOPIFY-018"` (12 tests).
- Passed: lifecycle-focused provider/service run (24 tests, 67 skipped).
- Passed: `npm run build`.
- Passed: `git diff --check`.
- Full `npm test`: 278 passed, 1 skipped, 2 unrelated baseline failures: `billing.service.test.ts` `schedules the next pre-close reconciliation for a pack-enabled Free cycle` received `Date { NaN }`; `billing-reconciliation.service.test.ts` `uses the shared contract and deterministic delayed job identity` observed zero `queue.add` calls.
- `npm run typecheck`: pre-existing workspace diagnostics outside SHOPIFY-018, including JSX implicit-any/session errors and missing shared-package exports `APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS` in existing billing files/tests; no changed lifecycle test diagnostic was reported.
- `git diff --check` passed.

### Handoff Evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-018`
- Implementation branch: `task/ARCH-010-SHOPIFY-018`
- Implementation commit: `1605a3c` (production implementation preserved).
- Attempt 2 implementation test commit: `dbfb9fc`.
- Parent claim commit: `51d0ef0`
- Parent report branch: `task/ARCH-010-SHOPIFY-018`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-018`
- Attempt 2 report commit: `8a527ae` (this report commit).
- Both branches were synchronized with their remotes before validation; no origin/main merge was required.
- Database gitlink staged: no.
- Main branches modified: no.

Returned to `moda_architect` for review. This report does not claim architect acceptance.

## Architect Review

### Attempt 1 — Changes Requested

#### Review Status

Changes Requested.

The implementation direction is architecturally correct. The submitted production source matches the canonical ARCH-010 lifecycle design and BACKGROUND-015 provider semantics:

```text
- one Partner GraphQL request combines activeSubscription + root events;
- events uses edges[0].node;
- lifecycle history is filtered to exactly the six required subscription event types;
- history is scoped by app subject + shop and bounded by occurredAtMin/occurredAtMax;
- SubscriptionStatus/AppReference/shop identity are validated;
- exact lifecycle state/eventType pairing is enforced;
- active Shopify commercial data remains provider-authoritative;
- latest FROZEN takes precedence over a temporarily non-null activeSubscription;
- null + CANCELED maps to CANCELED;
- other lifecycle evidence without a live subscription maps fail-closed to UNRESOLVED;
- no provider failure is converted to local commercial truth;
- the merchant lifecycle read path performs no Subscription mutation.
```

No production-source change is currently requested. Preserve implementation commit:

```text
1605a3c
```

unless one of the missing tests below exposes a genuine defect.

Attempt 1 cannot be accepted because the task's **Required tests** section says "At minimum prove" twelve lifecycle behaviours, while the submitted focused coverage directly proves only a subset. The Completion Report also omits the mandatory four start-of-attempt synchronization outcomes and the task metadata remains `in_progress` despite the handoff claiming review.

This is therefore a **test / validation / Completion Report / task-metadata only** Attempt 2 unless a new test exposes a real implementation defect.

#### Finding 1 — Prove ACTIVE and FROZEN precedence through the service read model

Extend:

```text
tests/unit/services/billing.service.test.ts
```

Directly prove both cases:

```text
A. live activeSubscription + no effective FROZEN event
   -> state = ACTIVE
   -> subscription preserves the complete SHOPIFY-013 commercial projection:
      planHandle
      description
      price amount/currency
      billingPeriod
      currentPeriodStart/currentPeriodEnd
      trialEndsAt
      cancelAtEndOfCycle
      pendingUpdate
      usageItems
   -> mapped/unmapped local plan information remains mapping only

B. live activeSubscription + latest SUBSCRIPTION_FROZEN/FROZEN event
   -> state = FROZEN, not ACTIVE
   -> live subscription may still be returned for display
   -> frozen provider planHandle/billingPeriod come from the lifecycle event
```

The existing null-live-subscription FROZEN case may remain.

This directly proves Required Tests 1, 2 and 11.

#### Finding 2 — Complete the null-live-subscription lifecycle matrix

Keep the existing CANCELED/UNFROZEN coverage and add explicit cases for the remaining provider evidence:

```text
activeSubscription = null + latest CREATED
  -> UNRESOLVED

activeSubscription = null + latest UPDATED
  -> UNRESOLVED

activeSubscription = null + latest CANCELLATION_SCHEDULED
  -> UNRESOLVED
  -> cancelEffectiveOn preserved

activeSubscription = null + latest UNFROZEN
  -> UNRESOLVED

activeSubscription = null + latest CANCELED
  -> CANCELED

activeSubscription = null + latest FROZEN
  -> FROZEN

activeSubscription = null + no lifecycle event
  -> NO_ACTIVE_SUBSCRIPTION
```

Do not reinterpret any of these states from local `Subscription.status`.

#### Finding 3 — Prove frozen provider presentation data remains provider-owned

Add mapped and unmapped FROZEN service cases.

Mapped:

```text
latestEvent.planHandle = "growth"
BillingPlan(shopifyPlanHandle="growth") exists
-> providerPlanHandle = "growth"
-> billingPeriod comes from provider event
-> mappingStatus = MAPPED
-> modaMapping is local label/features only
```

Unmapped:

```text
latestEvent.planHandle = "provider-plan-not-in-moda"
no BillingPlan row
-> state = FROZEN
-> providerPlanHandle preserved exactly
-> billingPeriod preserved exactly
-> mappingStatus = UNMAPPED
-> modaMapping = null
```

Do not add/fabricate historical price data. The FROZEN read model must not invent a `price` field from local `BillingPlan` data.

This proves Required Tests 7 and 8.

#### Finding 4 — Prove lifecycle provider failure never falls back to local truth

Add a service test with durable/local commercial-looking state present, for example:

```text
local Subscription/plan exists
provider.getSubscriptionLifecycleSnapshot() rejects
```

Required outcome:

```text
getMerchantShopifyLifecycleState() rejects with the provider verification failure
no ACTIVE/FROZEN/CANCELED/NO_ACTIVE state is manufactured from local Subscription
no Subscription mutation occurs
```

Also add direct provider snapshot failure coverage in:

```text
tests/unit/services/shopify-billing.provider.test.ts
```

for:

```text
non-2xx Partner HTTP response -> reject
GraphQL errors -> reject
```

Do not reuse only the pre-existing `getActiveSubscription()` failure tests; the new lifecycle snapshot path must be proved directly.

This proves Required Test 9.

#### Finding 5 — Prove exact query scope and the 365-day bound

Strengthen the lifecycle provider request test so it asserts all of:

```text
one fetch call only
query contains activeSubscription(
query contains events(
query contains subjectId: $appId
query contains shopId: $shopId
query contains occurredAtMin: $occurredAtMin
query contains occurredAtMax: $occurredAtMax
orderBy: OCCURRED_AT_DESC
first: 1
```

Variables must prove:

```text
appId === configured SHOPIFY_APP_ID
shopId === requested shopifyShopId

eventTypes exactly equal:
  SUBSCRIPTION_CREATED
  SUBSCRIPTION_UPDATED
  SUBSCRIPTION_CANCELLATION_SCHEDULED
  SUBSCRIPTION_CANCELED
  SUBSCRIPTION_FROZEN
  SUBSCRIPTION_UNFROZEN
```

Parse `occurredAtMin` and `occurredAtMax` and assert:

```text
occurredAtMax - occurredAtMin
  == 365 * 24 * 60 * 60 * 1000
```

Do not weaken this to merely checking that the variable names exist.

This proves Required Test 10.

#### Finding 6 — Prove the new provider parser fails closed

`getSubscriptionLifecycleSnapshot()` introduces a new parser surface. Add focused provider tests proving:

```text
events.edges = []
  -> latestLifecycleEvent = null

wrong AppReference id
  -> reject

wrong shop id
  -> reject

invalid occurredAt
  -> reject

valid state + wrong eventType
  -> reject

malformed lifecycle root/edges
  -> reject
```

Also directly prove at least:

```text
CANCELLATION_SCHEDULED preserves cancelEffectiveOn
UNFROZEN parses as UNFROZEN
CANCELED parses as CANCELED
```

The production parser already appears to implement these rules. This finding is missing proof, not a request to redesign it.

#### Finding 7 — Prove read-only Prisma behaviour explicitly

For lifecycle service tests, assert the read path does not perform projection writes.

At minimum:

```text
database.subscription.upsert -> not called
database.billingPeriod.upsert -> not called
database.$transaction -> not called
```

If the test fixture exposes other Subscription mutation methods, assert those are also not called.

Local `Shop.findUnique` and `BillingPlan.findUnique` reads are allowed.

This proves Required Test 12.

#### Finding 8 — Preserve scope

Unless a new test fails because production behavior is genuinely wrong:

```text
DO NOT MODIFY:
app/services/billing/providers/shopify-billing.provider.ts
app/services/billing/billing.types.ts
app/services/billing/billing.service.ts
```

Expected Attempt 2 code changes are test/report-only:

```text
tests/unit/services/shopify-billing.provider.test.ts
tests/unit/services/billing.service.test.ts
docs/decisions/shopify/ARCH-010/SHOPIFY-018-provider-subscription-lifecycle-state.md
```

Do not implement:

```text
SHOPIFY-012 billing route/UI
SHOPIFY-014 top-up adapter
SHOPIFY-015 plan-management UI/flow
SHOPIFY-016 cancellation/FROZEN presentation
SHOPIFY-021 promotion selection
Background reconciliation/persistence
database schema changes
legacy billing webhooks/Admin Billing API fallback
```

#### Finding 9 — Validation

Materialize the task's accepted DATABASE-013 dependency as required by the repository, without changing/staging the database gitlink.

Run:

```bash
npm run prisma:validate
npm run prisma:generate

./node_modules/.bin/vitest run \
  tests/unit/services/shopify-billing.provider.test.ts

./node_modules/.bin/vitest run \
  tests/unit/services/billing.service.test.ts \
  -t "SHOPIFY-018|lifecycle|provider history"

npm run typecheck
npm run build
npm test
git diff --check
```

If the focused service test naming does not support the filter above, prefix/rename the SHOPIFY-018 lifecycle test descriptions so they can be selected deterministically; do not skip required lifecycle tests because the broader file contains an unrelated baseline failure.

Expected:

```text
SHOPIFY-018 focused provider/lifecycle tests: PASS
Prisma validate/generate: PASS
git diff --check: PASS
```

The currently reported unrelated baselines may remain only if unchanged:

```text
billing.service full-file/full-suite:
  pre-existing pack-enabled Free Date { NaN } scheduling failure

repository typecheck:
  pre-existing shared-package export diagnostic for
  APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
```

The Completion Report must give the exact command, failing test/diagnostic, and changed-file non-regression evidence. A generic "unrelated failures documented" statement is insufficient.

#### Finding 10 — Mandatory VCS/workflow evidence

Attempt 1 does not record the mandatory four start-of-attempt synchronization outcomes.

Attempt 2 Completion Report must explicitly record:

```text
parent remote task branch fast-forwarded: yes | not-needed
parent origin/main incorporated: yes | already-current
implementation remote task branch fast-forwarded: yes | not-needed
implementation origin/main incorporated: yes | already-current
```

Also record:

```text
parent physical worktree
implementation physical worktree
parent task branch
implementation task branch
implementation commit
final parent report commit
both branches pushed
both branches clean
database gitlink staged: no
main branches modified: no
```

The user handoff identifies the Attempt 1 commits as:

```text
implementation: 1605a3c
parent report: 53d7653
```

The embedded Completion Report currently records only the implementation commit and parent claim commit. Attempt 2 must record the actual final parent report HEAD after all report metadata is committed.

#### Finding 11 — Correct task metadata on return

The submitted archive still contains:

```text
status: in_progress
executor: copilot
claimed_at: 2026-09-12T23:41:20Z
attempt: 1
```

despite the handoff saying it was returned for review.

For this Changes Requested handoff, return the task to:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next authorized:

```text
/moda-task ARCH-010-SHOPIFY-018
```

claim becomes Attempt 2.

Attempt 2 must return with:

```text
status: review
attempt: 2
```

before architect review.

#### Architect Decision

**Changes Requested — Attempt 1.**

The production implementation remains the current accepted candidate pending completion of the required proof:

```text
1605a3c
```

No downstream task is released by this review.

`ARCH-010-SHOPIFY-012`, `ARCH-010-SHOPIFY-014`, `ARCH-010-SHOPIFY-015`, `ARCH-010-SHOPIFY-016`, and `ARCH-010-SHOPIFY-021` remain Pending because SHOPIFY-018 is not Complete and each also has other incomplete prerequisites.

The ARCH-010 Ready frontier remains:

```text
ARCH-010-ADMIN-010
ARCH-010-BACKGROUND-019
ARCH-010-SHOPIFY-018
```

### Attempt 2 — Changes Requested

#### Review Status

Changes Requested — narrow test/workflow correction only.

Attempt 2 materially satisfies the architecture and most of the Attempt 1 proof contract.

Architect review confirms:

```text
- production source is byte-for-byte unchanged from Attempt 1;
- ACTIVE preserves the complete SHOPIFY-013 commercial projection;
- live subscription + latest FROZEN resolves to FROZEN;
- null-live CREATED / UPDATED / CANCELLATION_SCHEDULED / UNFROZEN resolve fail-closed to UNRESOLVED;
- null-live CANCELED resolves to CANCELED;
- null-live FROZEN resolves to FROZEN;
- no provider history resolves to NO_ACTIVE_SUBSCRIPTION;
- mapped and unmapped FROZEN presentation remain separate from provider truth;
- lifecycle provider failures do not fall back to local commercial state;
- HTTP and GraphQL lifecycle-snapshot failures reject;
- wrong app, wrong shop, invalid timestamp, wrong state/event pairing and malformed event fail closed;
- query variables contain the exact six lifecycle event types;
- the bounded history interval is exactly 365 days;
- no local Subscription mutation is performed by the read path;
- Prisma validate/generate, focused lifecycle tests, build and diff check pass;
- the full-suite failures reported remain outside the SHOPIFY-018 lifecycle changes.
```

The production implementation remains accepted as the current candidate:

```text
1605a3c
```

and Attempt 2 test implementation:

```text
dbfb9fc
```

No production-source change is requested.

Attempt 2 is not yet accepted because a few **explicit** Attempt 1 review obligations remain absent from the committed proof, and the VCS/task metadata is still stale.

#### Finding 1 — Add the two missing GraphQL query-shape assertions

The provider request test already proves one HTTP request, scoping, event types, ordering, `first: 1`, and the exact 365-day interval.

Add the two explicit assertions required by Attempt 1:

```ts
expect(body.query).toContain("activeSubscription(");
expect(body.query).toContain("events(");
```

in:

```text
tests/unit/services/shopify-billing.provider.test.ts
```

Do not change the production query.

#### Finding 2 — Directly prove valid UNFROZEN and CANCELED parser success

The service tests prove downstream classification of UNFROZEN/CANCELED snapshots, but Attempt 1 explicitly required the **provider parser** itself to prove these valid event types parse successfully.

Add focused provider cases to:

```text
tests/unit/services/shopify-billing.provider.test.ts
```

for:

```text
SUBSCRIPTION_UNFROZEN / state UNFROZEN
  -> latestLifecycleEvent.state === "UNFROZEN"
  -> eventType === "SUBSCRIPTION_UNFROZEN"

SUBSCRIPTION_CANCELED / state CANCELED
  -> latestLifecycleEvent.state === "CANCELED"
  -> eventType === "SUBSCRIPTION_CANCELED"
```

The existing CANCELLATION_SCHEDULED parser success case remains valid.

Do not change parser production code unless these tests expose a genuine defect.

#### Finding 3 — Complete the explicit no-write proof

Attempt 1 required, at minimum:

```text
database.subscription.upsert -> not called
database.billingPeriod.upsert -> not called
database.$transaction -> not called
```

The lifecycle test currently asserts:

```text
subscription.upsert -> not called
subscription.update -> not called
$transaction -> not called
```

but omits the explicit `billingPeriod.upsert` assertion.

Add:

```ts
expect(database.billingPeriod.upsert).not.toHaveBeenCalled();
```

to the lifecycle read-only proof.

No production service change is requested.

#### Finding 4 — Correct task state on handoff

The submitted Attempt 2 archive still contains:

```text
status: in_progress
executor: copilot
claimed_at: '2026-09-13T09:26:58Z'
attempt: 2
```

despite the handoff stating that the task was returned to architect review.

For this Changes Requested handoff, return to:

```text
status: ready
attempt: 2
executor: null
claimed_at: null
```

The next authorized:

```text
/moda-task ARCH-010-SHOPIFY-018
```

claim becomes Attempt 3.

Attempt 3 must return with:

```text
status: review
attempt: 3
```

#### Finding 5 — Record the four synchronization outcomes exactly

The Completion Report currently says:

```text
Both branches were synchronized with their remotes before validation;
no origin/main merge was required.
```

That does not satisfy the mandatory workflow evidence contract.

Attempt 3 must explicitly record all four fields:

```text
parent remote task branch fast-forwarded: yes | not-needed
parent origin/main incorporated: yes | already-current
implementation remote task branch fast-forwarded: yes | not-needed
implementation origin/main incorporated: yes | already-current
```

Do not replace those four fields with prose.

Also retain:

```text
parent physical worktree
implementation physical worktree
parent task branch
implementation task branch
implementation commit
both branches pushed
both branches clean
database gitlink staged: no
main branches modified: no
```

#### Finding 6 — Record the actual final parent report HEAD

The submitted archive records:

```text
Attempt 2 report commit: 8a527ae
```

but the developer handoff identifies the final published parent report HEAD as:

```text
9592a9e
```

Attempt 3 must record the actual final parent task-branch HEAD after all Completion Report metadata is committed.

Do not leave an earlier intermediate report commit in the final handoff evidence.

#### Attempt 3 scope

Expected implementation changes only:

```text
tests/unit/services/shopify-billing.provider.test.ts
tests/unit/services/billing.service.test.ts
docs/decisions/shopify/ARCH-010/SHOPIFY-018-provider-subscription-lifecycle-state.md
```

Unless one of the added tests fails because production behavior is genuinely incorrect:

```text
DO NOT MODIFY:
app/services/billing/providers/shopify-billing.provider.ts
app/services/billing/billing.types.ts
app/services/billing/billing.service.ts
```

Do not implement downstream UI/adapter tasks.

#### Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate

./node_modules/.bin/vitest run \
  tests/unit/services/shopify-billing.provider.test.ts

./node_modules/.bin/vitest run \
  tests/unit/services/billing.service.test.ts \
  -t "lifecycle|provider history|SHOPIFY-018"

npm run build
git diff --check
```

Also rerun the broader validation required by the repository/task and document any unchanged baselines exactly.

Expected focused outcome:

```text
provider lifecycle suite: PASS
lifecycle service suite: PASS
Prisma validate/generate: PASS
build: PASS
git diff --check: PASS
```

#### Architect Decision

**Changes Requested — Attempt 2.**

This is a narrow proof/workflow correction. The production implementation remains the current accepted candidate.

No downstream task is released yet.

`ARCH-010-SHOPIFY-012`, `ARCH-010-SHOPIFY-014`, `ARCH-010-SHOPIFY-015`, `ARCH-010-SHOPIFY-016`, and `ARCH-010-SHOPIFY-021` remain Pending.

On successful SHOPIFY-018 acceptance, each enabled task must be re-evaluated against all of its other dependencies before any Pending -> Ready promotion.

