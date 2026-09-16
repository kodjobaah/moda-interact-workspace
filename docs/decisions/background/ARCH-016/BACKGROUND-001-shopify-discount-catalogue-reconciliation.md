---
id: ARCH-016-BACKGROUND-001
architecture_id: ARCH-016
title: Reconcile the merchant Shopify discount catalogue
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-016-DATABASE-001
- ARCH-016-SHARED-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-016-BACKGROUND-001

## Objective

Own all provider-side full reconciliation of the local Shopify discount catalogue and the Background lifecycle triggers that occur after deferred initial subscription/reinstall reconciliation.

## Published Shared dependency

Install/pin the exact ARCH-016-SHARED-001 published version in `package.json` + lockfile. Import canonical queue contract/schema; do not duplicate it locally.

## Authorized implementation surface

```text
src/providers/shopify-discount.provider.ts                  # new
src/services/shopify-discount-catalogue.service.ts          # new
src/workers/shopify-discount-sync.worker.ts                 # new
src/entrypoints/recovery.ts                                 # register worker only
src/entrypoints/resources.ts or queue resources             # as needed
src/services/billing-subscription-reconciliation.service.ts # activation/reinstall sync triggers only
src/runtime/queue-concurrency-controller.ts                 # only if required to register the new queue safely
focused unit/integration tests
package.json
package-lock.json
```

Do not modify CommerceAgent/LLM selection logic.

## Queue/worker

Consume canonical queue:

```text
queueName = shopify-discount-sync
jobName   = reconcile-shopify-discounts
```

Register it in the existing `moda-recovery-worker` entrypoint. Do not create a new Render service.

Use bounded worker concurrency following existing repository conventions. The catalogue token/generation fence is the correctness mechanism across worker replicas; do not globally serialize the entire platform.

## Shopify access token

Reuse the repository's existing offline Shopify access-token/session refresh mechanism used by background Shopify reads.

Do not create a second credential store.

Before any GraphQL request, require:

```text
Shop ACTIVE
ShopSettings.onboardingCompleted = true
Subscription ACTIVE | TRIALING
read_discounts scope available
```

If not eligible:

```text
mark catalogue UNAVAILABLE (or leave UNAVAILABLE)
mark current ShopifyDiscount rows unavailable
complete job without provider request
```

## Provider API

Use Admin GraphQL API version `2026-07` consistent with app configuration.

Query `discountNodes(first: ..., after: ...)` and page until `pageInfo.hasNextPage = false`.

Request all eight current `Discount` union types explicitly:

```text
DiscountAutomaticApp
DiscountAutomaticBasic
DiscountAutomaticBxgy
DiscountAutomaticFreeShipping
DiscountCodeApp
DiscountCodeBasic
DiscountCodeBxgy
DiscountCodeFreeShipping
```

For every type retrieve at least:

```text
node id
__typename
title
summary when available
status
startsAt
endsAt
method/code information required below
```

For code types, retrieve redeem-code count and enough code data to prove `singleRedeemCode` only when exactly one code exists. Never assume the title is the code.

Preserve a bounded JSON `providerSnapshot` containing provider facts needed by a future CommerceAgent architecture. Do not persist secrets/tokens.

## Normalization

For each returned node derive:

```text
method = AUTOMATIC for DiscountAutomatic*
method = CODE      for DiscountCode*

providerType = exact __typename
providerStatus = exact Shopify status string
title/summary/startsAt/endsAt from provider
codeCount = provider count when available
singleRedeemCode = exact code only when codeCount == 1 and fetched/proven
```

`fixedSelectable` rule:

```text
AUTOMATIC native provider type
  -> true

CODE native provider type with exactly one proven redeem code
  -> true

CODE with 0/multiple/unknown redeem codes
  -> false

DiscountAutomaticApp / DiscountCodeApp
  -> false in ARCH-016 v1
```

All records are still stored/displayable regardless of `fixedSelectable`.

Do NOT implement basket eligibility or "best" selection.

## Full sync generation fence

Implement exactly this lifecycle:

### Claim

In a short DB transaction:

1. load shop + catalogue;
2. revalidate install/subscription/scope eligibility;
3. create catalogue if absent;
4. increment `syncGeneration` by 1;
5. generate opaque random `activeSyncToken`;
6. set `status = SYNCING`, `syncStartedAt = now`, clear last error;
7. commit.

### Fetch

Fetch all GraphQL pages outside a long-running DB transaction.

### Finalize

In one bounded transaction:

1. lock/reload catalogue;
2. require `activeSyncToken` still equals this worker token;
3. revalidate shop still ACTIVE, subscribed and scope-eligible;
4. upsert every observed `ShopifyDiscount` by `(shopId, shopifyDiscountNodeId)`;
5. set each observed row `isAvailable = true`, `lastSeenSyncGeneration = generation`, `lastSyncedAt = now`, `unavailableAt = null`;
6. mark all rows for shop whose `lastSeenSyncGeneration != generation` as `isAvailable = false`, `unavailableAt = now`;
7. set catalogue `CURRENT`, `lastSuccessfulSyncAt = now`, clear token/error/unavailableAt.

If token no longer matches, return `superseded` without changing rows/catalogue status.

If eligibility is lost before final commit, set/leave `UNAVAILABLE`, do not publish stale rows as current.

### Failure

Provider/parse failure:

- if this worker still owns token, set `ERROR`, clear token, set bounded error code/time;
- keep last successfully synchronized rows for history but UI MUST treat them unavailable because catalogue is not CURRENT;
- throw/retry according to existing BullMQ transient-provider convention;
- retries remain idempotent.

## Sync-request state

When consuming a valid job, ensure `syncRequestedAt` records the latest request time monotonically.

A new request arriving while another sync is running may supersede it by causing a later generation. Older worker finalization must fail its token check.

## Background subscription/reinstall lifecycle triggers

Current deferred subscription authority is in:

```text
src/services/billing-subscription-reconciliation.service.ts
```

After a transaction successfully transitions an initial activation or reinstall to:

```text
Shop ACTIVE
onboardingCompleted true
Subscription ACTIVE | TRIALING
```

publish canonical discount sync reason:

```text
SUBSCRIPTION_ACTIVATED      initial deferred activation
REINSTALL_RECONCILED        reinstall Free/Paid restored
```

Publish only after the authoritative transaction commits.

For reinstall resolving to NO_CONTRACT:

```text
catalogue UNAVAILABLE
no sync job
```

Publishing failure is best-effort relative to the billing transition: log it and persist `SYNC_REQUIRED`; do not roll back correct billing state.

Do not duplicate app-side activation logic; this task handles only Background-owned completion paths.

## Required tests

Provider:

- paginates through >1 page;
- parses all eight union types;
- code count 1 captures exact code;
- code count >1 never invents a code;
- app/function-backed rows stored but not fixed-selectable;
- provider status/dates preserved;
- token/session missing => no provider call.

Catalogue:

- first sync CURRENT;
- missing row on later full sync marked unavailable, not deleted;
- duplicate job idempotent;
- newer sync token supersedes older finalization;
- uninstall/eligibility loss prevents stale finalization;
- provider failure sets ERROR without deleting history;
- successful retry returns CURRENT;
- no long DB transaction wraps network pagination.

Lifecycle:

- deferred Free activation publishes after commit;
- deferred Paid activation publishes after commit;
- reinstall Free publishes REINSTALL_RECONCILED;
- reinstall Paid publishes REINSTALL_RECONCILED;
- reinstall NO_CONTRACT does not publish and leaves catalogue unavailable;
- queue publish failure does not roll back billing state.

## Validation

Inspect package scripts, then run declared equivalents of:

```text
npm test
npm run build
npm run prisma:validate
git diff --check
```

Run focused provider/catalogue/worker tests separately and record counts.

## Stop conditions

STOP if:

- implementation needs `write_discounts`;
- background cannot obtain the existing offline token without inventing another credential mechanism;
- GraphQL schema differs materially from the eight documented 2026-07 union types and would require architectural interpretation;
- implementation begins evaluating basket applicability or AI ranking;
- implementing the new queue would require a new Render service.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
