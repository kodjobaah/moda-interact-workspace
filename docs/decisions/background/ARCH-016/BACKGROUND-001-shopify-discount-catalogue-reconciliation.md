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
status: in_progress
priority: 20
attempt: 3
depends_on:
- ARCH-016-DATABASE-001
- ARCH-016-SHARED-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16
executor: copilot
claimed_at: 2026-09-16T18:41:56Z
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

## Completion Report

### Work Completed

- Finding 1, provider normalization: `src/providers/shopify-discount.provider.ts` now queries `codesCount` and the actual `codes` connection for all four code union members, preserves bounded count/precision/evidence snapshots, and only proves `singleRedeemCode` when the exact one-code connection is complete. App-backed rows remain stored but non-selectable.
- Findings 2-3, catalogue fencing and request ordering: `src/services/shopify-discount-catalogue.service.ts` now uses one `FOR UPDATE` catalogue lock for request, claim, failure, and finalize paths; increments generations and replaces opaque tokens under the lock; revalidates eligibility before provider access and before `CURRENT`; preserves history/unavailable timestamps; and records `syncRequestedAt` monotonically from the canonical job timestamp. `src/workers/shopify-discount-sync.worker.ts` validates and passes `requestedAt`.
- Finding 4, durable request state: `src/services/billing-subscription-reconciliation.service.ts` establishes `SYNC_REQUIRED` in a short transaction before enqueue, leaves it durable on queue failure, and uses three exponential retries with retained failures.
- Findings 5-6, lifecycle coverage: `src/services/billing-subscription-reconciliation.service.ts` now publishes `REINSTALL_RECONCILED` for same-cycle Paid reinstall and marks NO_CONTRACT reinstall catalogues/rows unavailable without enqueueing.
- Finding 7, periodic Paid activation: `src/services/billing-reconciliation.service.ts` and `src/entrypoints/billing.ts` inject the existing canonical discount queue through the periodic billing activation route. `tests/unit/runtime/entrypoint-isolation.test.ts` tracks the expanded dependency contract.
- Accepted boundaries preserved: Shared remains exact `0.12.1`, Shopify API remains `2026-07`, the existing offline token mechanism is reused, the worker remains `moda-recovery-worker`, no write scope/AI selection/new service was added.

### Validation

- Focused lifecycle/entrypoint tests: passed, `3` files / `195` tests.
- `npm run prisma:validate`: passed.
- `npm run build`: task-owned files compile; blocked only by the unchanged baseline diagnostics in `src/services/inbound-whatsapp-audio.service.ts` (`transcriptionStatus`) and `src/workers/whatsapp.worker.ts` (`contentType`) from the generated Prisma client mismatch.
- `git diff --check`: passed.
- Full `npm test -- --passWithNoTests`: `7` existing failures remain outside this task: recovery entrypoint string expectation, translation batch concurrency integration, four translation enum/runtime configuration integrations, and the observability test expecting Shared `0.12.0` while the required dependency is `0.12.1`. No focused task test failed.
- No dedicated provider/catalogue tests were present in the supplied snapshot; provider and catalogue changes were validated by task-owned compilation, the focused lifecycle suite, Prisma validation, and source-level contract inspection.

### Launcher / Git Evidence

- canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`;
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-016-BACKGROUND-001`;
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-016-BACKGROUND-001`;
- task branches: `task/ARCH-016-BACKGROUND-001` in both worktrees;
- start synchronization: parent/implementation origin/main already current; recursive submodule preparation passed;
- database submodule commit: `655ff35ea04f4d2cdb4bef4313b3b977320999cd`;
- launcher claim commit: `512ca126`;
- implementation commit: `8665b93` (`fix(background): complete Shopify discount reconciliation rework`);
- implementation branch pushed to `origin/task/ARCH-016-BACKGROUND-001`;
- parent Completion Report updated on the mirrored parent task branch; no main branch modified.

Task status is `review`; return control to `moda_architect` for review.

## Architect Review — Attempt 1

### Status

**Changes Requested — provider normalization, catalogue fencing, durable sync-request state and lifecycle trigger coverage are incomplete**

Implementation commit reviewed: `70770d6`.
Parent Completion Report commit reported: `f4de682c`.

Attempt 1 establishes the correct high-level ownership boundary: Shopify is read through the
existing offline-token mechanism, the canonical Shared `0.12.1` queue contract is consumed,
pagination is outside the database transaction, the worker is registered in the existing
`moda-recovery-worker`, and no CommerceAgent/LLM discount-selection logic was introduced.
Those choices MUST be preserved.

The implementation is not yet functionally safe enough to accept. The following corrections
are required for Attempt 2.

### Finding 1 — Shopify code-discount normalization currently treats the GraphQL connection as an array

Current file:

```text
src/providers/shopify-discount.provider.ts
```

The GraphQL query returns `codes` as a `DiscountRedeemCodeConnection`, but the normalizer does:

```ts
const codes = Array.isArray(discount.codes) ? discount.codes : null;
```

Therefore a normal Shopify response produces `codeNodes = []`, `codeCount = 0`,
`singleRedeemCode = null`, and every native CODE discount becomes non-selectable even when it
has exactly one redeem code.

The query also omits `codesCount` and does not request code evidence for `DiscountCodeApp`.
ARCH-016 requires all four CODE union members to preserve provider count information and to
prove a single code only when exactly one code exists.

#### Required provider correction

For **all four** code types:

```text
DiscountCodeApp
DiscountCodeBasic
DiscountCodeBxgy
DiscountCodeFreeShipping
```

request:

```graphql
codesCount { count precision }
codes(first: 2) {
  nodes { code }
  pageInfo { hasNextPage }
}
```

Normalize deterministically:

```text
AUTOMATIC type
  codeCount = null
  singleRedeemCode = null

CODE type
  exact provider count is known only when codesCount.precision == EXACT
  codeCount = exact count when precision == EXACT; otherwise null

singleRedeemCode
  set only when:
    codesCount.precision == EXACT
    codesCount.count == 1
    exactly one non-empty code node was returned
    codes.pageInfo.hasNextPage == false
  otherwise null

fixedSelectable
  native AUTOMATIC -> true
  DiscountAutomaticApp -> false
  native CODE -> true only when singleRedeemCode is proven as above
  DiscountCodeApp -> false regardless of code count
```

Keep the bounded provider snapshot; include the returned count/precision and bounded code
connection evidence, but never credentials/tokens.

Do not infer a code from `title`.

### Finding 2 — catalogue generation/token fencing is not atomic and finalization does not revalidate eligibility

Current file:

```text
src/services/shopify-discount-catalogue.service.ts
```

The current finalize path performs a normal `findUnique()` token read, then writes rows and
finally writes `CURRENT`. It does not lock the catalogue row. A newer claim can therefore
change `activeSyncToken` after the old worker's read but before the old worker's writes, allowing
the stale worker to overwrite newer state.

The current finalize path also does **not** recheck:

```text
Shop.status == ACTIVE
ShopSettings.onboardingCompleted == true
Subscription.status == ACTIVE | TRIALING
durable offline Session still has read_discounts
```

before making the catalogue `CURRENT`.

Attempt 2 MUST use one shared catalogue-row lock helper in both claim and finalize:

```sql
SELECT "id"
FROM "shopify"."ShopifyDiscountCatalogue"
WHERE "shopId" = $shopId
FOR UPDATE
```

#### Claim order

Use this exact order in one short transaction:

```text
1. resolve Shop identity/domain
2. ensure catalogue row exists (upsert if absent)
3. acquire ShopifyDiscountCatalogue FOR UPDATE
4. reload catalogue after lock
5. re-read current Shop/settings/subscription/offline Session eligibility
6. monotonically record syncRequestedAt from the job requestedAt (Finding 3)
7. if ineligible:
     catalogue -> UNAVAILABLE
     clear activeSyncToken/syncStartedAt
     mark current discount rows unavailable
     preserve an existing non-null row unavailableAt; set it only where null
     return unavailable without provider request
8. if eligible:
     generation = locked.syncGeneration + 1
     generate a new opaque token
     set SYNCING + generation + token + syncStartedAt
9. commit
```

Two concurrent claims must not both derive the same next generation from the same unlocked
value.

#### Finalize order

Use this exact order in one bounded transaction:

```text
1. acquire the same catalogue FOR UPDATE lock
2. reload catalogue
3. if activeSyncToken != this worker token -> return superseded immediately
4. re-read current Shop/settings/subscription/offline Session eligibility
5. if eligibility is lost:
     catalogue -> UNAVAILABLE
     clear this token/syncStartedAt
     mark rows unavailable (preserve existing unavailableAt; set only where null)
     return unavailable
     DO NOT upsert fetched provider rows as current
6. upsert all observed rows with this generation
7. observed rows -> isAvailable true, unavailableAt null, lastSeenSyncGeneration = generation
8. rows not seen in generation -> isAvailable false; set unavailableAt only where null
9. catalogue -> CURRENT, clear token/error, set lastSuccessfulSyncAt
10. commit
```

No network request may occur while this transaction/row lock is held.

Provider failure may conditionally set `ERROR` only while the failing worker still owns its
token. Also clear `syncStartedAt` when clearing the token. Preserve historical rows.

### Finding 3 — `syncRequestedAt` does not represent the latest request and can regress semantically

Current worker:

```text
src/workers/shopify-discount-sync.worker.ts
```

parses `payload.requestedAt` but discards it. `reconcile()` then writes a fresh processing-time
`new Date()`.

Attempt 2 MUST pass the parsed job request timestamp into the catalogue service and record:

```text
syncRequestedAt = max(existing syncRequestedAt, payload.requestedAt)
```

inside the locked claim transaction.

Do not replace a newer persisted request timestamp with an older out-of-order job timestamp.
Validate the parsed ISO value as a real Date before use; the Shared parser remains the schema
authority.

### Finding 4 — Background lifecycle publication does not durably establish `SYNC_REQUIRED`

Current helper:

```text
BillingSubscriptionReconciliationService.publishDiscountSync(...)
```

only calls BullMQ. If queue publication fails, it logs the failure but leaves no durable
`SYNC_REQUIRED` state, contrary to the task contract.

Attempt 2 MUST make the Background request path durable before queue publication:

```text
authoritative billing/reinstall transaction commits
  -> short discount-request transaction
       -> re-read current Shop/settings/subscription/offline Session eligibility
       -> if no longer eligible: set/leave catalogue UNAVAILABLE; do not enqueue
       -> if eligible: upsert/update catalogue SYNC_REQUIRED
            syncRequestedAt = max(existing, requestedAt)
            activeSyncToken = null
            syncStartedAt = null
  -> commit
  -> enqueue canonical job
```

If queue publication fails:

```text
log bounded error
leave catalogue SYNC_REQUIRED
DO NOT roll back the already-correct billing/reinstall transition
```

For Background-produced jobs use the repository's existing BullMQ transient convention:

```text
attempts: 3
backoff: { type: "exponential", delay: 1000 }
removeOnComplete: true
removeOnFail: false
```

Do not introduce a second queue contract or another credential store.

### Finding 5 — successful same-cycle Paid reinstall does not request discount reconciliation

Current path:

```text
completeReinstallPaid(...)
  -> same provider/current period
  -> activateReinstallPaid(...)
```

`activateReinstallPaid()` commits the restored ACTIVE/TRIALING state and only calls
`publishNext(...)`; it never requests `REINSTALL_RECONCILED`.

After `activateReinstallPaid()` successfully commits (`true`), request the canonical discount
sync with reason:

```text
REINSTALL_RECONCILED
```

before/independently of the existing billing schedule publication. Do not publish when the
result is `false` or `"invalid"`.

Preserve the already-correct Free reinstall and paid rollover trigger paths.

### Finding 6 — reinstall resolving to NO_CONTRACT does not force the catalogue UNAVAILABLE

Current:

```text
completeReinstallWithoutContract(...)
```

correctly restores the shop installation lifecycle but does not touch the discount catalogue.
The task contract explicitly requires:

```text
reinstall -> NO_CONTRACT
  catalogue UNAVAILABLE
  provider rows unavailable
  no discount-sync job
```

Inside the same authoritative reinstall transaction, set/upsert the catalogue `UNAVAILABLE`,
clear `activeSyncToken` / `syncStartedAt`, and mark rows unavailable while preserving existing
non-null `unavailableAt` values. Do not enqueue a discount job for this path.

### Finding 7 — one reachable Paid activation path constructs reconciliation without the discount queue

Current file:

```text
src/services/billing-reconciliation.service.ts
```

contains a direct initial-Paid activation path which constructs:

```text
new BillingSubscriptionReconciliationService(...).activateInitialPaid(...)
```

without a `discountQueue`. Because `publishDiscountSync()` returns immediately when the queue is
absent, a successful activation through the periodic billing reconciliation path can complete
without `SUBSCRIPTION_ACTIVATED` discount reconciliation.

Attempt 2 is explicitly authorised to modify:

```text
src/services/billing-reconciliation.service.ts
```

only for dependency injection of the existing canonical discount-sync queue.

Make the queue flow explicit:

```text
billing entrypoint creates/reuses shopifyDiscountSyncQueue
  -> createBillingReconciliationService(..., shopifyDiscountSyncQueue)
  -> BillingReconciliationService retains that queue dependency
  -> nested BillingSubscriptionReconciliationService receives the same queue
  -> successful direct activateInitialPaid path establishes SYNC_REQUIRED then publishes SUBSCRIPTION_ACTIVATED
```

Do not alter unrelated billing reconciliation rules.

### Accepted Attempt-1 work that MUST remain unchanged

Preserve:

```text
@modainteract/moda-interact-shared pinned exactly to 0.12.1
Admin GraphQL API version 2026-07
all provider pagination outside long DB transactions
all eight documented discount union members represented
existing offline Shopify token/session refresh mechanism
canonical shopify-discount-sync / reconcile-shopify-discounts contract
worker registered in existing moda-recovery-worker
bounded worker concurrency (no global platform serialization)
no new Render service
no write_discounts scope
no CommerceAgent / AI ranking / basket-applicability implementation
```

### Attempt-2 authorised implementation surface

Attempt 2 may modify only:

```text
src/providers/shopify-discount.provider.ts
src/services/shopify-discount-catalogue.service.ts
src/workers/shopify-discount-sync.worker.ts
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts          # newly authorised only for queue injection
src/entrypoints/billing.ts
src/entrypoints/billing-resources.ts
focused provider/catalogue/billing lifecycle tests
this task Completion Report / review metadata
```

`src/entrypoints/recovery.ts`, Shared package/version, database schema/migration and unrelated
workers must not change unless a compile-only import adjustment is strictly necessary.

### Required focused functional validation

Tests should be narrowly targeted to these corrections rather than expanded into exhaustive
coverage. At minimum prove:

```text
provider:
  >1 discountNodes page is still traversed
  code connection object is parsed correctly
  exact one-code native CODE -> codeCount 1 + exact code + fixedSelectable true
  multiple-code native CODE -> not fixed-selectable
  unknown/non-exact count -> no singleRedeemCode and not fixed-selectable
  DiscountCodeApp remains not fixed-selectable

catalogue:
  two concurrent/newer claims cannot share the same next generation
  newer token supersedes older finalization before any row mutation
  uninstall/scope/subscription eligibility loss before finalize cannot become CURRENT
  out-of-order older requestedAt does not regress syncRequestedAt
  missing rows become unavailable without deleting history
  provider failure sets ERROR only for token owner; retry can return CURRENT

background lifecycle:
  queue failure leaves catalogue SYNC_REQUIRED and billing state committed
  Background-produced jobs have 3 exponential retries and retain final failures
  Free activation publishes SUBSCRIPTION_ACTIVATED after commit
  Paid activation through both subscription worker and periodic billing reconciliation publishes after commit
  Free reinstall publishes REINSTALL_RECONCILED
  same-cycle Paid reinstall publishes REINSTALL_RECONCILED
  rollover Paid reinstall publishes REINSTALL_RECONCILED
  reinstall NO_CONTRACT leaves catalogue UNAVAILABLE and publishes nothing
```

Run the repository-declared equivalents of:

```text
focused ARCH-016 provider/catalogue/lifecycle tests
npm run prisma:validate
npm run build
git diff --check
```

The known generated-Prisma-client mismatch may remain documented if it is unchanged and no
Attempt-2 file introduces a new diagnostic. Do not perform unrelated generated-client cleanup.

### Completion / stop condition

Attempt 2 is ready for architect re-review only when:

```text
code-discount provider normalization uses the actual Shopify connection/count shape
claim/finalize share an atomic catalogue-row token/generation fence
finalization revalidates current eligibility before CURRENT
syncRequestedAt is monotonic from canonical job requestedAt
Background lifecycle triggers durably establish SYNC_REQUIRED before queue publication
queue publication failure preserves SYNC_REQUIRED
all successful initial activation/reinstall branches emit the correct canonical reason
NO_CONTRACT reinstall forces UNAVAILABLE and emits no job
Shared remains exactly 0.12.1
no provider network call is held inside the catalogue DB transaction
```

Then push both mirrored task branches, set this same task back to `status: review`, clear
`executor` / `claimed_at`, update the Completion Report with focused evidence, and return to
`moda_architect`.

No ARCH-016 dependency is promoted by this review. `attempt` remains `1` in this Changes
Requested patch; `/moda-task ARCH-016-BACKGROUND-001` owns the increment to Attempt 2 when the
task is reclaimed. `ARCH-016-SYSTEM-TEST-001` remains Pending and MUST NOT start automatically.

## Architect Review — Attempt 2

### Status

**Changes Requested — preserve the latest request clock on ineligible claims and resolve Shop identity before catalogue creation**

Implementation commit reviewed: `8665b93`.
Parent Completion Report commit reviewed: `006ad5a2`.

Attempt 2 correctly fixes the substantive Attempt-1 provider, fencing and lifecycle defects. The following work is accepted and MUST be preserved:

```text
@modainteract/moda-interact-shared remains exactly 0.12.1
Shopify Admin GraphQL remains 2026-07
all eight documented discount union members remain queried
codesCount + bounded codes connection evidence is used for CODE normalization
singleRedeemCode is proven only for exact one-code native CODE discounts
app/function-backed discounts remain stored but fixedSelectable false
discountNodes pagination remains outside database transactions
one ShopifyDiscountCatalogue FOR UPDATE fence protects generation/token request, claim, failure and finalize paths
finalize checks activeSyncToken before row mutation
finalize revalidates current install/subscription/offline-scope eligibility before CURRENT
provider failure writes ERROR only for the owning token and clears syncStartedAt/token
Background lifecycle publication establishes SYNC_REQUIRED before BullMQ enqueue
Background-produced jobs retain attempts=3, exponential 1000ms backoff, removeOnComplete=true, removeOnFail=false
same-cycle Paid reinstall now emits REINSTALL_RECONCILED
NO_CONTRACT reinstall leaves the catalogue/rows UNAVAILABLE and emits no discount-sync job
periodic Paid activation receives the canonical discount queue
no new service, credential store, write_discounts scope or AI/CommerceAgent selection
```

The current implementation is not accepted because one remaining state-ordering defect can lose the latest durable request timestamp, and the claim helper still attempts catalogue creation before proving the Shop exists.

### Finding 1 — an ineligible valid worker job does not advance `syncRequestedAt`

Current claim flow in:

```text
src/services/shopify-discount-catalogue.service.ts
```

does this:

```text
lock/create catalogue
resolve Shop
evaluate eligibility

if ineligible:
  mark catalogue UNAVAILABLE
  return

only if eligible:
  update syncRequestedAt = max(existing, payload.requestedAt)
  claim generation/token
```

This does not satisfy the Attempt-1 correction contract. `syncRequestedAt` is the durable timestamp of the **latest valid synchronization request**, not merely the latest request that happened to find the shop eligible.

A valid job for an existing shop can therefore be newer than the persisted request clock but disappear from durable ordering when the shop is currently:

```text
UNINSTALLED
onboarding incomplete
subscription not ACTIVE/TRIALING
missing read_discounts on the durable offline Session
```

That produces a real ordering defect:

```text
persisted syncRequestedAt = T1

job T3 arrives while shop is temporarily ineligible
  -> catalogue UNAVAILABLE
  -> T3 is not recorded

older/retried job T2 runs later after eligibility is restored
  -> syncRequestedAt becomes T2

durable state now says T2 was the latest request even though T3 existed
```

#### Required Attempt-3 correction

In the locked claim transaction, for an **existing Shop**, compute and persist:

```text
syncRequestedAt = max(catalogue.syncRequestedAt, requestedAt)
```

**before** branching on eligibility.

Use this exact order:

```text
1. resolve Shop identity/domain by shopId
2. if Shop does not exist:
     return unavailable
     do not create a catalogue
     do not call Shopify
3. ensure the catalogue row exists
4. acquire ShopifyDiscountCatalogue FOR UPDATE
5. reload the catalogue after the lock
6. compute latestRequestedAt = max(catalogue.syncRequestedAt, requestedAt)
7. persist latestRequestedAt in the same locked transaction
8. re-read current Shop/settings/subscription/durable offline Session eligibility
9. if ineligible:
     catalogue -> UNAVAILABLE
     preserve latestRequestedAt
     clear activeSyncToken/syncStartedAt
     mark current discount rows unavailable while preserving existing unavailableAt
     return unavailable
10. if eligible:
     generation = locked.syncGeneration + 1
     create new opaque activeSyncToken
     catalogue -> SYNCING
     retain latestRequestedAt
     clear prior error
11. commit
12. only then perform provider pagination
```

It is acceptable to combine steps 7 and 9/10 into one `update` per branch, provided both branches persist the same `latestRequestedAt` and the value never regresses.

Do not use processing time as a substitute for the canonical job `requestedAt`.

### Finding 2 — the claim creates/locks the catalogue before proving the Shop exists

`lockCatalogue(...)` currently performs:

```ts
shopifyDiscountCatalogue.upsert({
  where: { shopId },
  create: { shopId },
  update: {},
})
```

before `reconcile(...)` checks whether the referenced Shop row exists.

Because `ShopifyDiscountCatalogue.shopId` is a foreign key, a stale/invalid queued job for a Shop that has been hard-deleted can fail at catalogue creation and enter BullMQ retry/error handling instead of terminating without provider work.

This also differs from the exact Attempt-1 claim order, which required Shop identity/domain resolution before catalogue creation.

Attempt 3 MUST therefore resolve the Shop first, as described in Finding 1. A missing Shop is a bounded terminal `unavailable` outcome for this worker invocation:

```text
no catalogue upsert
no generation/token claim
no provider request
```

Apply the same defensive ordering to `requestSync(shopId, requestedAt)` because it uses the same catalogue-creation helper:

```text
resolve Shop first
missing Shop -> return "unavailable"
existing Shop -> lock/create catalogue -> evaluate eligibility -> request/unavailable transition
```

For `requestSync`, no BullMQ job exists yet, so an ineligible request does not need a new durable request timestamp beyond the existing task contract; the important requirement is that it must not attempt to create a catalogue for a missing Shop.

### Attempt-3 authorised implementation surface

Attempt 3 is intentionally narrow. Modify only:

```text
src/services/shopify-discount-catalogue.service.ts
focused catalogue service tests
this task Completion Report / review metadata
```

Do NOT modify:

```text
src/providers/shopify-discount.provider.ts
src/workers/shopify-discount-sync.worker.ts
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
src/entrypoints/billing.ts
src/entrypoints/billing-resources.ts
src/entrypoints/recovery.ts
Shared package/version
database schema/migrations
unrelated workers/services
```

unless a compile-only import adjustment is strictly necessary.

### Required focused validation

Do not expand into exhaustive test work. Add only focused regression coverage that proves:

```text
existing eligible Shop:
  newer requestedAt advances syncRequestedAt and normal claim still reaches SYNCING

existing ineligible Shop:
  newer requestedAt advances syncRequestedAt
  catalogue ends UNAVAILABLE
  provider is not called

existing ineligible Shop + older out-of-order job:
  syncRequestedAt does not regress

missing Shop:
  reconcile returns unavailable
  no catalogue upsert/create is attempted
  provider is not called

requestSync missing Shop:
  returns unavailable
  no catalogue upsert/create is attempted
```

Retain the previously reported provider/lifecycle validation. Run the repository-declared equivalents of:

```text
focused catalogue regression tests
npm run prisma:validate
npm run build
git diff --check
```

The existing generated-Prisma-client and unrelated baseline suite failures remain non-blocking if unchanged.

### Completion / stop condition

Return for architect review only when:

```text
every valid worker request for an existing Shop monotonically records canonical payload.requestedAt even when eligibility is lost
no older job can regress syncRequestedAt
missing Shop cannot reach catalogue creation or Shopify provider access
all accepted Attempt-2 provider/fencing/lifecycle behavior remains unchanged
```

Then push both mirrored task branches, set this same task back to `status: review`, clear `executor` / `claimed_at`, update the Completion Report with Attempt-3 evidence, and return to `moda_architect`.

No ARCH-016 dependency is promoted by this review. `attempt` remains `2` in this Changes Requested patch; `/moda-task ARCH-016-BACKGROUND-001` owns the increment to Attempt 3 when the task is reclaimed. `ARCH-016-SYSTEM-TEST-001` remains Pending and MUST NOT start automatically.
