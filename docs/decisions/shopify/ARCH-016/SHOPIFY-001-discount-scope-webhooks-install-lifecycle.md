---
id: ARCH-016-SHOPIFY-001
architecture_id: ARCH-016
title: Add Shopify discount scope, webhook ingress and installation lifecycle sync triggers
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: null
claimed_at: null
attempt: 4
depends_on:
- ARCH-016-DATABASE-001
- ARCH-016-SHARED-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16T18:45:00Z
---

# ARCH-016-SHOPIFY-001

## Objective

Wire Shopify discount discovery into the existing app install/subscription/webhook lifecycle without doing catalogue reconciliation inside the HTTP lifecycle.

## Published Shared dependency

Before editing, read ARCH-016-SHARED-001 Completion Report and install/pin the exact published package version in:

```text
package.json
package-lock.json
```

Do not copy the queue payload locally.

## Authorized implementation surface

```text
shopify.app.moda-interact.toml
app/routes/webhooks/root/route.jsx
app/routes/webhooks/app/scopes-update/route.jsx
app/routes/webhooks/app/uninstalled/route.jsx
app/services/webhooks/shopify-webhook-ingress.service.ts
app/services/webhooks/shopify-webhook-metadata.ts
app/services/webhooks/shopify-webhook-queue.server.ts
app/services/shop/shop.service.ts
app/services/billing/billing.service.ts
app/routes/app/billing/callback/route.tsx
new app/services/discounts/* queue/lifecycle helpers as required
focused tests for those files
package.json
package-lock.json
```

Do not implement Shopify Admin `discountNodes` reconciliation here. That belongs to BACKGROUND-001.

## Shopify app configuration

Modify only canonical:

```text
shopify.app.moda-interact.toml
```

Add `read_discounts` to required scopes. Preserve all existing scopes.

Add the five app-specific topics to the existing `/webhooks` subscription:

```text
discounts/create
discounts/update
discounts/delete
discounts/redeemcode_added
discounts/redeemcode_removed
```

Do not add a second shop-specific webhook registration mechanism.

## Webhook ingress rule

Existing checkout/order ingress remains unchanged.

For the five discount topics:

1. authenticate using existing root `authenticate.webhook` path;
2. resolve durable shop identity using existing ingress conventions;
3. create canonical Shared discount-sync payload with reason `DISCOUNT_WEBHOOK`;
4. publish to `shopify-discount-sync` queue using Shared contract/helper;
5. use Shopify delivery ID for duplicate-safe job identity;
6. acknowledge only after durable BullMQ acceptance, matching existing webhook reliability behavior;
7. do not parse/store the discount payload as catalogue truth;
8. do not call Shopify Admin API synchronously.

Unknown/non-supported topics retain existing behavior.

## Initial subscription bootstrap

Do NOT sync discounts on bare app installation / `NO_CONTRACT`.

After an initial Free/Paid activation has been durably verified as:

```text
Shop.status = ACTIVE
ShopSettings.onboardingCompleted = true
Subscription.status = ACTIVE | TRIALING
```

publish one best-effort `SUBSCRIPTION_ACTIVATED` discount-sync job.

App-side hook points in current snapshot:

```text
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts::completeFreeActivation
paid activation/sync path already used by billing callback
```

Do not publish before the activation transaction commits.

A queue publication failure MUST NOT roll back a valid subscription activation. Log the failure and leave the durable catalogue `SYNC_REQUIRED` so Background reconciliation/next lifecycle trigger can repair it.

When publishing the job, atomically/boundedly ensure `ShopifyDiscountCatalogue` exists and is `SYNC_REQUIRED` unless shop is unavailable. This state write must happen after subscription success; do not make a Shopify API call.

## Scope-update bootstrap

Current file:

```text
app/routes/webhooks/app/scopes-update/route.jsx
```

continues to persist the Session scope string.

After persistence, when the updated durable session includes `read_discounts` AND the shop currently satisfies eligible subscription/install state, request a FULL sync with reason `SCOPES_UPDATED`.

If the scope is absent, mark catalogue `UNAVAILABLE` and do not publish a sync.

Repeated scope-update webhooks are idempotent; duplicate FULL sync requests are safe.

## Uninstall

Current uninstall ordering is:

```text
authenticate
shopService.markUninstalled
session delete
```

Preserve that ordering.

Extend the same durable uninstall transaction/service boundary so BEFORE session deletion:

```text
Shop.status = UNINSTALLED                 existing behavior
ShopifyDiscountCatalogue.status = UNAVAILABLE
activeSyncToken = null
unavailableAt = uninstall event time
all ShopifyDiscount rows for shop:
  isAvailable = false
  unavailableAt = uninstall event time when not already set
```

Do NOT delete ShopifyDiscount rows. Do NOT delete RecoveryOutreachAttempt/Conversation history.

Do not enqueue a sync from uninstall.

## Reinstall boundary

Do not add app-side logic that marks the catalogue CURRENT on reinstall. Existing background billing reconciliation is provider authority for restored Free/Paid subscription state; BACKGROUND-001 owns the `REINSTALL_RECONCILED` sync trigger.

## Catalogue eligibility helper

Create one repository-local helper used by activation/scope paths. It must require:

```text
Shop ACTIVE
onboardingCompleted true
Subscription ACTIVE | TRIALING
current durable Session scope includes read_discounts
```

Do not duplicate slightly different eligibility predicates in each route.

## Required tests

- canonical TOML retains existing scopes + `read_discounts`;
- canonical TOML includes exactly the five required discount topics at `/webhooks`;
- authenticated `discounts/create` enqueues canonical FULL sync trigger;
- all five topics route identically except topic field;
- duplicate delivery ID dedupes;
- discount webhook never calls Admin API synchronously;
- initial NO_CONTRACT install does not enqueue;
- verified Free activation enqueues after commit;
- verified Paid activation enqueues after commit;
- failed activation does not enqueue;
- missing `read_discounts` scope does not enqueue;
- scope-added event for eligible shop enqueues;
- scope removal marks catalogue unavailable;
- uninstall marks catalogue/discount rows unavailable before sessions are removed;
- uninstall retains discount/history rows;
- queue publication failure does not invalidate a successfully committed subscription activation.

## Validation

Inspect `package.json` and run declared equivalents of:

```text
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

Also parse/inspect `shopify.app.moda-interact.toml` using existing config validation if present.

## Stop conditions

STOP if:

- implementation requires `write_discounts` (ARCH-016 is read-only discovery);
- implementation starts using webhook payload as the persistent discount definition;
- implementation needs to call Shopify during uninstall after session/token cleanup;
- a second webhook subscription mechanism would be introduced instead of canonical TOML app-specific subscriptions;
- implementation attempts to define AI/CommerceAgent discount selection.

## Completion protocol

## Completion Report

### Status

Ready for Review

### Work Completed

- Pinned `@modainteract/moda-interact-shared` to the exact published `0.12.1` release in `package.json` and `package-lock.json`.
- Added `read_discounts` to the existing required Shopify scope list.
- Added exactly the five required discount topics to the existing `/webhooks` subscription.
- Routed authenticated discount webhooks through the Shared `DISCOUNT_WEBHOOK` payload and `shopify-discount-sync` queue, using Shopify delivery IDs for deterministic duplicate handling and no synchronous Admin API call.
- Added one repository-local eligibility helper requiring ACTIVE shop, completed onboarding, ACTIVE/TRIALING subscription, and durable `read_discounts` session scope.
- Added post-commit best-effort `SUBSCRIPTION_ACTIVATED` publication for verified Free and Paid activation paths. Catalogue state is marked `SYNC_REQUIRED` before publication; queue failures are logged without invalidating the committed activation.
- Added scope-update state transitions and `SCOPES_UPDATED` publication for eligible shops; removed scope marks the catalogue and discount rows unavailable without deleting rows.
- Extended the existing uninstall transaction to mark catalogue and discount rows unavailable before session cleanup; no discount or recovery history is deleted.
- No catalogue reconciliation, Shopify Admin API discovery, reinstall `CURRENT` transition, write scope, or CommerceAgent selection contract was added.

### Files Changed

- `shopify.app.moda-interact.toml`
- `package.json`, `package-lock.json`
- `app/services/discounts/shopify-discount-lifecycle.service.ts`
- `app/services/webhooks/shopify-webhook-ingress.service.ts`
- `app/services/webhooks/shopify-webhook-queue.server.ts`
- `app/routes/webhooks/app/scopes-update/route.jsx`
- `app/routes/app/billing/callback/route.tsx`
- `app/services/shop/shop.service.ts`
- Focused webhook, billing callback, ShopService, and discount lifecycle tests

### Validation

- focused lifecycle suites: `66 passed`;
- discount lifecycle helper suite: `8 passed`;
- Shopify app config validation: passed for `shopify.app.moda-interact.toml`;
- `npm run lint`: passed;
- `npm run build`: passed;
- `npm run typecheck`: completed with no diagnostics from the changed implementation; repository baseline test/type diagnostics remain outside this task surface;
- `git diff --check`: passed;
- `npm test`: `610 passed`, `10 failed`, `3 skipped` out of `623`. The failures are existing merchant-i18n catalogue expectations exposed by the mandated Shared `0.12.1` pin, whose stricter ICU catalogue requires keys absent from those pre-existing fixtures. No discount lifecycle test failed.

### Physical Worktree Isolation

- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`;
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-016-SHOPIFY-001`;
- parent branch: `task/ARCH-016-SHOPIFY-001`;
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-016-SHOPIFY-001`;
- implementation branch: `task/ARCH-016-SHOPIFY-001`;
- shared workspace checkout switched or mutated for task work: no;
- shared implementation checkout switched or mutated for task work: no;
- another task worktree reused: no;
- implementation submodule `database`: `c59f2eb6953642f1c850d38b09ed03096d672547`;
- recursive submodule sync: passed;
- recursive submodule update/init: passed.

### Synchronization Evidence

- parent remote task branch fast-forwarded: not-needed;
- parent origin/main incorporated: already-current;
- implementation remote task branch fast-forwarded: not-needed;
- implementation origin/main incorporated: already-current.

### Git / Handoff

- implementation commit: `9aa4c57` (`feat(shopify): wire discount sync lifecycle triggers`);
- implementation branch pushed: `origin/task/ARCH-016-SHOPIFY-001`;
- task status set to `review`;
- executor and claimed timestamp cleared;
- returned to `moda_architect` for review; no merge to `main` performed.

## Completion protocol

The implementation and report are complete. The task is returned to `moda_architect` at `status: review`; stop here pending architect review.


## Architect Review — Attempt 1

### Status

**Changes Requested — durable offline-session fencing and idempotent catalogue invalidation**

This review is functionality-first. The Shopify configuration, authenticated discount
webhook ingress, canonical Shared `0.12.1` queue payload/job identity, post-commit
activation hook points and uninstall-before-session-delete ordering are otherwise
accepted. Attempt 2 must be a narrow correction; do not redesign the accepted webhook
or billing flows.

The Completion Report contains the required launcher-resolved parent/implementation
worktree isolation and synchronization evidence. There is no workflow-conformance
correction required for Attempt 2.

The reported ten merchant-i18n fixture failures do not drive this review decision. The
Attempt-2 decision is based on the runtime lifecycle defects below.

### Finding 1 — activation bootstrap does not prove the durable offline session and is not atomically fenced

ARCH-016 requires discount catalogue eligibility to use the durable **offline** Shopify
session:

```text
Shop ACTIVE
ShopSettings.onboardingCompleted = true
Subscription ACTIVE | TRIALING
read_discounts present in the durable offline Session
```

The current `getDiscountSyncEligibility()` implementation uses:

```ts
db.session.findFirst({
  where: { shop: shop.domain },
  orderBy: { expires: "desc" },
})
```

This does not constrain `isOnline = false`. An online session is therefore allowed to
satisfy the discount-scope gate even though Background reconciliation requires durable
offline Shopify authority.

There is a second correctness problem in the same activation path: shop/subscription/
scope eligibility is read **before** the transaction that writes
`ShopifyDiscountCatalogue.status = SYNC_REQUIRED`. A concurrent uninstall or scope
removal can therefore occur between the eligibility read and the catalogue write, after
which the stale activation path can change an unavailable catalogue back to
`SYNC_REQUIRED` and publish a job.

#### Required Attempt-2 correction

In:

```text
app/services/discounts/shopify-discount-lifecycle.service.ts
```

refactor the subscription-activation bootstrap so eligibility and the
`SYNC_REQUIRED` state transition occur in **one bounded Prisma transaction**.

The transaction must:

1. load the shop by `shopId` with:
   - `domain`;
   - `status`;
   - `ShopSettings.onboardingCompleted`;
   - `Subscription.status`;
2. load the durable session using an explicit offline predicate:

```ts
where: {
  shop: shop.domain,
  isOnline: false,
}
```

If multiple offline rows are possible in the existing session-storage implementation,
select deterministically using the existing session expiry convention. Do not hardcode a
Shopify session ID string unless the existing repository already establishes that as its
canonical lookup contract.

3. evaluate the existing `isDiscountSyncEligible(...)` predicate using **that offline
   session scope**;
4. if not eligible, return `null` without changing the catalogue to `SYNC_REQUIRED` and
   without publishing;
5. if eligible, call `markDiscountCatalogueSyncRequired(...)` inside the same
   transaction and return only the immutable publish data needed after commit:

```text
shopId
shopDomain
requestedAt
```

6. commit the transaction;
7. only after commit, publish the canonical `SUBSCRIPTION_ACTIVATED` job;
8. keep queue publication best-effort. A publication failure must still leave the
   already-committed catalogue `SYNC_REQUIRED` and must not invalidate the successful
   billing/subscription activation.

Do **not** publish from inside the database transaction.

`getDiscountSyncEligibility()` may be removed if no caller remains, or may be refactored
to accept/use the transaction client, but there must be no separate pre-transaction
eligibility read followed by a later catalogue-state transaction.

Required concurrency behavior:

```text
activation transaction sees ACTIVE + eligible offline scope
  -> mark SYNC_REQUIRED
  -> commit
  -> publish

activation transaction sees UNINSTALLED
  -> no SYNC_REQUIRED write
  -> no publish

activation transaction sees offline scope without read_discounts
  -> no SYNC_REQUIRED write
  -> no publish

online session has read_discounts but offline session does not
  -> not eligible
  -> no publish
```

### Finding 2 — scope-update bootstrap trusts payload scope even when no durable offline scope proves it

`app/routes/webhooks/app/scopes-update/route.jsx` currently persists the authenticated
`session` when one exists, but then evaluates eligibility directly from:

```ts
payload.current.toString()
```

If no durable session is present, or if the authenticated session is not the durable
offline session, the route can still mark the catalogue `SYNC_REQUIRED` and enqueue a
`SCOPES_UPDATED` job from webhook payload state alone.

That violates the ARCH-016 fail-closed rule: the payload is a lifecycle signal, while
provider access authority is the persisted offline Session.

#### Required Attempt-2 correction

In:

```text
app/routes/webhooks/app/scopes-update/route.jsx
```

keep the existing authenticated webhook and Session-scope persistence, then in the **same
transaction** read the durable offline Session for the shop using:

```ts
isOnline: false
```

Use the persisted offline Session's `scope` for the eligibility predicate. Do not use
`payload.current` as the final authority for the sync decision after persistence.

Required behavior after the Session write:

```text
offline Session exists + has read_discounts + shop/subscription eligible
  -> mark catalogue SYNC_REQUIRED
  -> commit
  -> publish SCOPES_UPDATED

offline Session absent
  -> fail closed as unavailable
  -> no publish

offline Session present but read_discounts absent
  -> mark catalogue UNAVAILABLE
  -> no publish

payload says read_discounts but durable offline Session does not
  -> no publish
```

The queue publication stays after transaction commit. Do not call Shopify Admin API from
this route.

### Finding 3 — invalidation overwrites historical discount `unavailableAt`

The task's uninstall contract explicitly requires every retained `ShopifyDiscount` row
to become unavailable while setting:

```text
unavailableAt = uninstall event time when not already set
```

The current helper instead performs:

```ts
transaction.shopifyDiscount.updateMany({
  where: { shopId },
  data: { isAvailable: false, unavailableAt },
})
```

That overwrites an existing `unavailableAt` timestamp for discounts that were already
unavailable because of a prior full reconciliation, scope loss or earlier lifecycle
invalidation. The same helper is also used by scope removal, so repeated invalidation
mutates historical state instead of being idempotent.

The helper also uses `ShopifyDiscountCatalogue.updateMany()`. When the catalogue row does
not yet exist, "mark catalogue UNAVAILABLE" becomes a no-op even though ARCH-016 defines
one durable catalogue state record and the lifecycle event is authoritative enough to
establish the `UNAVAILABLE` state.

#### Required Attempt-2 correction

In:

```text
app/services/discounts/shopify-discount-lifecycle.service.ts
```

change `markDiscountCatalogueUnavailable(...)` so it satisfies all of the following:

1. ensure a catalogue state row exists for the shop (use the existing unique `shopId`
   boundary; an `upsert` is appropriate);
2. set catalogue status to `UNAVAILABLE`;
3. clear `activeSyncToken` and `syncStartedAt`;
4. set the catalogue `unavailableAt` to the lifecycle event time required by the caller;
5. set **all** shop discounts `isAvailable = false`;
6. set a discount row's `unavailableAt` only when that row currently has
   `unavailableAt = null`;
7. never delete catalogue or discount rows.

Because Prisma `updateMany` cannot express SQL `COALESCE` in a normal data object, use
bounded separate writes if necessary, for example one write that marks every row
unavailable and a second write restricted to `unavailableAt: null` that stamps the
lifecycle time. Do not use raw SQL solely for this correction.

For uninstall, preserve the existing ordering:

```text
authenticate
  -> ShopService.markUninstalled transaction
       -> Shop UNINSTALLED
       -> catalogue/discount invalidation
  -> delete Session rows
```

If `ShopService.markUninstalled()` needs to reuse an already-persisted `Shop.uninstalledAt`
on a duplicate uninstall delivery so the effective lifecycle time remains stable, do so
inside the existing service boundary. Do not move Session deletion into the transaction
and do not enqueue a discount sync from uninstall.

### Accepted behavior that MUST remain unchanged

Attempt 2 must preserve the already-correct implementation:

```text
@modainteract/moda-interact-shared pinned exactly to 0.12.1
read_discounts added to canonical shopify.app.moda-interact.toml
exact five discount webhook topics on the existing /webhooks subscription
root authenticate.webhook remains the authentication boundary
all five discount webhook topics publish canonical DISCOUNT_WEBHOOK jobs
Shopify delivery ID remains the deterministic webhook job identity input
webhook payload is never persisted as catalogue truth
no synchronous Shopify Admin API call from webhook ingress
Free/Paid verified activation publishes only after subscription transaction completion
queue failure does not roll back a committed activation
scope-update queue publication remains after its DB transaction commits
uninstall invalidates durable state before Session deletion
no discount/history deletion
no reinstall CURRENT mutation in moda-interact
no write_discounts scope
no CommerceAgent/AI discount-selection implementation
```

Do not redesign `shopify-webhook-ingress.service.ts`, the canonical Shared job schema,
BullMQ queue names/job names, billing-provider verification, or reinstall authority for
these findings.

### Attempt-2 authorised implementation surface

Modify only what is required for the corrections:

```text
app/services/discounts/shopify-discount-lifecycle.service.ts
app/routes/webhooks/app/scopes-update/route.jsx
app/services/shop/shop.service.ts                         # only if needed for stable duplicate-uninstall event time
focused tests for the three corrected lifecycle boundaries
this task Completion Report / review metadata
```

The following are already conformant and must not be changed merely to create a new
attempt:

```text
shopify.app.moda-interact.toml
app/routes/webhooks/root/route.jsx
app/services/webhooks/shopify-webhook-ingress.service.ts
app/services/webhooks/shopify-webhook-queue.server.ts
app/routes/app/billing/callback/route.tsx
package.json
package-lock.json
```

The exact Shared dependency remains `0.12.1`; do not publish or consume another Shared
version for these corrections.

### Required focused regression cases

Add/adjust only focused tests needed to prove the corrected functionality:

1. subscription activation with an online Session containing `read_discounts` but no
   eligible offline Session does not mark `SYNC_REQUIRED` and does not publish;
2. subscription activation performs eligibility and `SYNC_REQUIRED` mutation through one
   transaction-owned state read/write path, and publication occurs after that transaction
   resolves;
3. activation observed as `UNINSTALLED` (or with offline scope removed) at the
   transaction fence does not publish;
4. scope-update payload containing `read_discounts` does not publish when the durable
   offline Session does not contain it / is absent;
5. eligible persisted offline scope publishes `SCOPES_UPDATED` only after the
   transaction completes;
6. an already-non-null `ShopifyDiscount.unavailableAt` is preserved by scope/uninstall
   invalidation while `isAvailable` becomes/remains false;
7. a discount with `unavailableAt = null` receives the lifecycle timestamp;
8. invalidation creates/establishes the catalogue `UNAVAILABLE` state when the catalogue
   record is absent;
9. uninstall still invalidates catalogue/discount state before Session deletion and does
   not enqueue a sync.

These are regression guards for concrete functional defects. Do not expand Attempt 2
into exhaustive unrelated test work.

### Attempt-2 validation

Inspect the current `package.json` scripts and rerun the same declared validation used in
Attempt 1, including at minimum:

```text
focused ARCH-016 lifecycle tests
npm run typecheck
npm run lint
npm run build
Shopify TOML/config validation used in Attempt 1
git diff --check
```

Run `npm test` as required by the task. If the same ten merchant-i18n fixture failures
remain unchanged and none is caused by the Attempt-2 files, record them with the same
baseline evidence; do not modify merchant-i18n fixtures merely to turn the full-suite
count green.

### Completion / stop condition

Attempt 2 is ready for architect re-review only when:

```text
activation eligibility is fenced inside the same transaction as SYNC_REQUIRED
activation/scope eligibility uses only the durable offline Session scope
scope payload alone cannot authorize a sync
catalogue invalidation establishes UNAVAILABLE even when the row was absent
existing discount unavailableAt timestamps are preserved
newly unavailable discount rows receive the lifecycle timestamp
uninstall ordering/history retention remain unchanged
Shared stays pinned exactly to 0.12.1
all focused lifecycle validation passes
Completion Report records the actual Attempt-2 implementation/report commits and launcher evidence
```

Then push both mirrored task branches, set this same task back to `status: review`, clear
`executor` / `claimed_at`, and return it to `moda_architect`.

No ARCH-016 dependency is promoted by this review. `attempt` remains `1` in this Changes
Requested patch; `/moda-task ARCH-016-SHOPIFY-001` owns the transition to Attempt 2 and
the attempt increment when the task is reclaimed.

## Attempt 2 Completion Report

### Status

Ready for Review

### Corrections Completed

- Subscription activation eligibility and `SYNC_REQUIRED` mutation now share one Prisma transaction.
- Activation eligibility now reads only the durable offline Shopify Session (`isOnline: false`), deterministically ordered by expiry; online scope alone cannot authorize a sync.
- Scope-update persistence remains in the transaction, but sync eligibility now uses the persisted offline Session scope. Missing offline scope fails closed and invalidates without publishing.
- Catalogue invalidation now establishes an `UNAVAILABLE` row with upsert, marks all discounts unavailable, and stamps only rows whose `unavailableAt` is still null.
- Queue publication remains strictly after transaction completion and best-effort.

### Focused Validation

- corrected lifecycle and uninstall suites: `27 passed`;
- all focused accepted-path and correction suites: `77 passed`;
- `npm run build`: passed;
- Shopify TOML validation from Attempt 1 remains passed;
- `git diff --check`: passed;
- `npm test`: `613 passed`, `10 failed`, `3 skipped`; the same merchant-i18n fixture failures remain and do not involve Attempt 2 files;
- typecheck/lint still report unrelated repository baseline diagnostics outside the correction files.

### Worktree / Git Evidence

- launcher canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`;
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-016-SHOPIFY-001`;
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-016-SHOPIFY-001`;
- implementation submodule `database`: `c59f2eb6953642f1c850d38b09ed03096d672547`;
- Attempt 2 parent claim commit: `f4f19b5`;
- Attempt 2 implementation commit: `454f882` (`fix(shopify): fence discount lifecycle by offline session`);
- implementation branch pushed: `origin/task/ARCH-016-SHOPIFY-001`;
- task branch synchronization and recursive submodule preparation: passed;
- executor and claimed timestamp cleared; no main branch modified.

Task status is `review`; return control to `moda_architect` for re-review.

## Attempt 3 Completion Report

### Corrections Completed

- Added one shared PostgreSQL `Shop` row `FOR UPDATE` lifecycle lock helper and applied it before authoritative eligibility/state reads in activation, scope-update, and uninstall transactions.
- Activation, scope removal, and uninstall now serialize on the same Shop-row boundary, preventing stale activation from resurrecting `SYNC_REQUIRED` after a disabling lifecycle event commits.
- Duplicate uninstall deliveries now reuse persisted `Shop.uninstalledAt` for catalogue invalidation timestamps while preserving per-discount non-null `unavailableAt` values.
- Added focused lock-order, activation fencing, and duplicate-uninstall regression coverage.

### Attempt 3 Validation

- focused lifecycle suites: `27 passed` for lock/timestamp tests and `77 passed` across accepted-path plus correction suites;
- `npm run build`: passed;
- typecheck: no diagnostics from the Attempt 3 correction files; unrelated repository baseline diagnostics remain;
- lint: unchanged unrelated baseline errors in existing test files;
- `git diff --check`: passed;
- full `npm test` baseline remains unchanged and is not required for these focused lifecycle corrections.

### Attempt 3 Git / Handoff

- launcher claim commit: `8863cb06`;
- implementation correction commit: `2ffbd20` (`fix(shopify): serialize discount lifecycle transitions`);
- implementation branch pushed: `origin/task/ARCH-016-SHOPIFY-001`;
- canonical worktree/submodule preparation remained ready;
- executor and claimed timestamp cleared; no main branch modified.

Task status is `review`; return control to `moda_architect` for re-review.

## Architect Review — Attempt 2

### Status

**Changes Requested — the offline-session reads are corrected, but the lifecycle transaction is not yet a concurrency fence**

Implementation commit reviewed: `454f882`.
Parent Completion Report commit reported: `153425cb`.

Attempt 2 correctly fixes the three literal data-shape/state issues requested after
Attempt 1:

```text
activation reads only isOnline = false Session scope
scope-update payload is no longer final eligibility authority
catalogue UNAVAILABLE is established with upsert
discount rows preserve existing non-null unavailableAt values
newly unavailable discount rows receive the lifecycle timestamp
publication remains after transaction completion
```

Those corrections are retained. Do not redesign the accepted webhook ingress, Shared
queue contract, billing-provider verification, or catalogue projection.

One concurrency defect from Attempt 1 remains, and duplicate uninstall currently makes
the uninstall lifecycle timestamp unstable.

### Finding 1 — a normal Prisma transaction does not serialize activation against uninstall/scope removal

`enqueueSubscriptionActivatedDiscountSyncBestEffort()` now reads the shop and durable
offline Session and writes `ShopifyDiscountCatalogue.status = SYNC_REQUIRED` inside one
interactive Prisma transaction. `app/scopes-update` similarly performs its persistence,
reads and catalogue mutation inside one transaction.

That is necessary, but under PostgreSQL's normal `READ COMMITTED` isolation it is not a
lifecycle fence. Plain `SELECT` statements do not prevent another transaction from
committing a lifecycle change between the eligibility read and catalogue write.

The remaining race is:

```text
T1 activation: read Shop ACTIVE + eligible offline scope
T2 uninstall:  set Shop UNINSTALLED + catalogue UNAVAILABLE; commit
T1 activation: upsert catalogue SYNC_REQUIRED; commit
T1 activation: publish SUBSCRIPTION_ACTIVATED
```

A corresponding race exists between activation and a concurrent scope-removal update.
The result violates the required precedence of uninstall/scope loss and can resurrect an
unavailable catalogue as `SYNC_REQUIRED` after the disabling lifecycle event already
committed.

#### Required Attempt-3 correction

Use one **shop-scoped database row lock** as the common lifecycle serialization boundary
for all three app-side paths that can change discount catalogue eligibility:

```text
subscription activation bootstrap
APP_SCOPES_UPDATE persistence/eligibility
APP_UNINSTALLED invalidation
```

Implement this in the smallest repository-local form in:

```text
app/services/discounts/shopify-discount-lifecycle.service.ts
```

Add a helper that, inside the caller's existing Prisma transaction, acquires a PostgreSQL
`FOR UPDATE` lock on the durable `Shop` row before eligibility state is read or changed.
Follow the repository's existing `Prisma.sql` / transaction `$queryRaw` row-lock pattern;
do not add advisory locks or a new locking service.

The physical model in the task's pinned database schema is `Shop` in schema `commerce`.
The lock must therefore target the current schema/model mapping from the checked-out
Prisma schema rather than copying an unrelated raw-SQL table path from another service.

Required ordering for every participating transaction:

```text
resolve shop identity if necessary
  -> acquire Shop row FOR UPDATE
  -> re-read authoritative shop/settings/subscription/offline-session state
  -> make catalogue mutation
  -> commit
  -> publish after commit when applicable
```

Do not make the pre-lock lookup authoritative. If a route needs an initial lookup only to
obtain the shop ID, it MUST re-read all eligibility facts after the row lock is held.

Apply the same lock helper/boundary in:

```text
app/services/discounts/shopify-discount-lifecycle.service.ts
  enqueueSubscriptionActivatedDiscountSyncBestEffort(...)

app/routes/webhooks/app/scopes-update/route.jsx
  transaction handling Session scope + catalogue state

app/services/shop/shop.service.ts
  markUninstalled(...)
```

All three paths must acquire the same Shop-row lock before mutating Session/catalogue
lifecycle state. Keep one consistent lock ordering; do not lock Session first in one path
and Shop first in another.

Required concurrency outcomes:

```text
activation obtains Shop lock first
  -> eligible state + SYNC_REQUIRED commit
  -> later uninstall/scope removal obtains lock
  -> disabling lifecycle event writes UNAVAILABLE last

uninstall/scope removal obtains Shop lock first
  -> disabling lifecycle event commits
  -> later activation obtains lock and re-reads state
  -> activation is ineligible
  -> no SYNC_REQUIRED rewrite
  -> no publish
```

Queue publication remains outside the transaction and only follows a committed eligible
state. Do not hold the row lock while publishing to BullMQ.

### Finding 2 — duplicate uninstall changes the effective uninstall timestamp used by catalogue invalidation

`ShopService.markUninstalled()` conditionally writes `Shop.uninstalledAt` only when that
column is null, which is correct. However it then always calls:

```text
markDiscountCatalogueUnavailable(transaction, shop.id, uninstalledAt)
```

using the timestamp from the current webhook delivery.

On a duplicate/retried uninstall webhook, `Shop.uninstalledAt` therefore remains the
original first-uninstall time while `ShopifyDiscountCatalogue.unavailableAt` is rewritten
to the later retry time. This makes two durable records describe different effective
uninstall boundaries and means a duplicate delivery is not state-idempotent.

#### Required Attempt-3 correction

While holding the Shop lifecycle row lock from Finding 1, read the existing
`Shop.uninstalledAt` and derive exactly one effective timestamp:

```text
effectiveUninstalledAt = persisted Shop.uninstalledAt ?? incoming event time
```

Then:

1. when persisted `Shop.uninstalledAt` is null, set Shop status/uninstalledAt using the
   incoming event time as today;
2. when it is already non-null, preserve the persisted value;
3. call `markDiscountCatalogueUnavailable(...)` with `effectiveUninstalledAt`;
4. keep Session deletion outside/after the existing uninstall service transaction;
5. do not enqueue a discount sync from uninstall.

The existing discount-row behavior remains correct: all rows become unavailable and an
already non-null per-discount `unavailableAt` is preserved.

### Accepted Attempt-2 behavior that MUST remain unchanged

```text
Shared pinned exactly to 0.12.1
canonical read_discounts scope and five webhook topics unchanged
discount webhook payload remains trigger-only, never catalogue truth
no synchronous Shopify Admin API call in webhook ingress
o write_discounts scope
activation uses durable offline Session only
scope payload cannot authorize sync independently
catalogue UNAVAILABLE row is created when absent
existing discount unavailableAt values are preserved
Free/Paid activation publication remains after DB commit and best-effort
scope-update publication remains after DB commit
uninstall invalidates before Session deletion
no catalogue/discount/history deletion
no reinstall CURRENT mutation in moda-interact
no CommerceAgent/AI discount-selection implementation
```

### Attempt-3 authorised implementation surface

Modify only what is required for the two remaining lifecycle corrections:

```text
app/services/discounts/shopify-discount-lifecycle.service.ts
app/routes/webhooks/app/scopes-update/route.jsx
app/services/shop/shop.service.ts
focused tests for lifecycle serialization and duplicate uninstall stability
this task Completion Report / review metadata
```

Do not modify already-conformant webhook ingress/configuration, billing callback,
Shared dependency files, queue names/job schema, or unrelated merchant i18n code.

### Required focused validation for Attempt 3

Add/adjust only focused regression cases that prove functional behavior:

```text
1. activation acquires the common Shop lifecycle lock before authoritative eligibility reads
2. scope update acquires the same Shop lifecycle lock before Session/catalogue lifecycle mutation
3. uninstall acquires the same Shop lifecycle lock before Shop/catalogue invalidation
4. all three paths use the same lock ordering
5. an uninstall-wins interleaving cannot be followed by activation SYNC_REQUIRED/publish
6. a scope-removal-wins interleaving cannot be followed by activation SYNC_REQUIRED/publish
7. activation-wins ordering is followed by later disabling lifecycle UNAVAILABLE state
8. duplicate uninstall reuses persisted Shop.uninstalledAt for catalogue invalidation
```

These may use focused transaction/lock-order mocks if the repository test harness does
not provide a live concurrency database. The purpose is to prove the row-lock boundary,
not to expand into exhaustive integration testing.

Rerun the same task validation. The unchanged merchant-i18n baseline failures do not
require correction here if they remain unrelated to these files.

### Reclaim state

`ARCH-016-SHOPIFY-001` returns to:

```text
status: ready
attempt: 2
executor: null
claimed_at: null
```

The deterministic launcher owns the increment to Attempt 3 when the task is reclaimed.
No dependent task is promoted by this review. `ARCH-016-SYSTEM-TEST-001` remains Pending
and MUST NOT start automatically.

## Architect Review — Attempt 3

### Status

**Changes Requested — scope-update must acquire the common Shop lifecycle lock before mutating Session state**

Implementation commit reviewed: `2ffbd20`.
Parent Completion Report commit reported: `0df88e46`.

Attempt 3 correctly implements the common PostgreSQL Shop-row lock helper and fixes the
remaining activation/uninstall race from Attempt 2. The following Attempt-3 behavior is
accepted and MUST be preserved:

```text
lockShopLifecycleRow(...) uses commerce.Shop FOR UPDATE
activation resolves identity, acquires the Shop lock, then re-reads authoritative eligibility
activation publishes only after its transaction commits
uninstall resolves identity, acquires the same Shop lock, then re-reads durable uninstall state
duplicate uninstall reuses persisted Shop.uninstalledAt for catalogue invalidation
existing per-discount non-null unavailableAt values remain preserved
Shared remains pinned exactly to 0.12.1
```

One lifecycle-lock ordering defect remains in `APP_SCOPES_UPDATE`.

### Finding — scope-update writes Session.scope before acquiring the common Shop lock

Current code in:

```text
app/routes/webhooks/app/scopes-update/route.jsx
```

executes the transaction in this order:

```text
transaction.session.update(... scope ...)
  -> resolve Shop id
  -> lockShopLifecycleRow(... FOR UPDATE ...)
  -> re-read Shop/offline Session
  -> mutate catalogue
```

That does not satisfy the Attempt-3 contract. Attempt 3 explicitly required every
participating lifecycle transaction to acquire the **same Shop row lock before any
Session/catalogue lifecycle mutation**, with one consistent lock order across activation,
scope update and uninstall.

Although the Session write is not externally visible until transaction commit, it already
acquires/mutates the Session row before the common lifecycle serialization boundary. This
creates a mixed lock order (`Session -> Shop`) while the canonical lifecycle order is
`Shop -> Session/catalogue`. The purpose of the shared fence is not merely that the Shop
row is locked at some point in the transaction; it is to establish one deterministic
shop-scoped ordering boundary before lifecycle state is mutated.

### Required Attempt-4 correction

Make one narrow correction in:

```text
app/routes/webhooks/app/scopes-update/route.jsx
```

Inside the existing `db.$transaction(...)`, use this exact order:

```text
1. resolve Shop identity by authenticated shop domain (ID lookup only)
2. if no Shop row exists, return null without catalogue mutation/publish
3. acquire lockShopLifecycleRow(transaction, shopId)
4. only after the Shop lock is held, persist session.scope = payload.current when session exists
5. re-read authoritative Shop status/settings/subscription after the lock
6. re-read the durable offline Session (`shop = domain`, `isOnline = false`) after the Session persistence
7. evaluate eligibility from the persisted offline Session scope only
8. missing/no-read_discounts offline scope -> mark catalogue UNAVAILABLE; no publish
9. eligible state -> mark catalogue SYNC_REQUIRED
10. commit transaction
11. publish SCOPES_UPDATED only after commit
```

The pre-lock Shop lookup is identity resolution only. Do not use any pre-lock Shop,
Subscription, ShopSettings or Session values as authoritative eligibility state.

Do **not** move BullMQ publication inside the transaction.

Do **not** add another lock. The existing `lockShopLifecycleRow(...)` helper is the one
canonical lifecycle lock for this task.

### Required lock-order invariant after correction

All three participating lifecycle paths must now be:

```text
subscription activation:
  resolve Shop id -> Shop FOR UPDATE -> authoritative reads -> catalogue mutation -> commit -> publish

APP_SCOPES_UPDATE:
  resolve Shop id -> Shop FOR UPDATE -> Session scope persistence -> authoritative reads -> catalogue mutation -> commit -> publish if eligible

APP_UNINSTALLED:
  resolve Shop id -> Shop FOR UPDATE -> authoritative uninstall read/write -> catalogue invalidation -> commit -> Session deletion
```

There must be no `Session` write before the Shop lock in `APP_SCOPES_UPDATE`.

### Attempt-4 authorised implementation surface

Modify only:

```text
app/routes/webhooks/app/scopes-update/route.jsx
focused scope-update lifecycle test(s)
this task Completion Report / review metadata
```

Do not change:

```text
app/services/discounts/shopify-discount-lifecycle.service.ts
app/services/shop/shop.service.ts
shopify.app.moda-interact.toml
webhook ingress/queue implementation
billing callback/provider verification
package.json or package-lock.json
Shared queue contract/version
```

unless a compile-only import adjustment is strictly required by the route correction.

### Required focused regression validation

Add a focused route-level regression test under the existing `tests/unit/routes/`
boundary that proves call order, not only that the lock helper is eventually invoked.
The test must fail against Attempt 3 and pass after the correction.

At minimum prove:

```text
1. Shop identity lookup occurs before the lifecycle lock only as ID resolution
2. lockShopLifecycleRow / transaction.$queryRaw occurs before transaction.session.update
3. transaction.session.update occurs before the post-lock offline Session eligibility read
4. catalogue mutation occurs after the Shop lock
5. SCOPES_UPDATED publication occurs after the transaction resolves
6. scope removal still marks UNAVAILABLE and does not publish
7. payload read_discounts without persisted offline read_discounts still cannot publish
```

Do not broaden Attempt 4 into unrelated test cleanup. Rerun the focused ARCH-016
lifecycle tests, build, relevant type/lint validation and `git diff --check`. Existing
unrelated repository baseline diagnostics do not require correction in this task.

### Completion / stop condition

Attempt 4 is ready for architect re-review only when:

```text
APP_SCOPES_UPDATE acquires the Shop FOR UPDATE lock before Session.scope mutation
all authoritative scope eligibility is still based on the post-lock persisted offline Session
activation and uninstall retain the accepted Attempt-3 locking behavior
duplicate uninstall retains the persisted first Shop.uninstalledAt
publication remains after transaction commit
Shared remains pinned exactly to 0.12.1
focused lock-order regression validation passes
```

Then push both mirrored task branches, set this same task back to `status: review`, clear
`executor` / `claimed_at`, and return it to `moda_architect`.

No ARCH-016 dependency is promoted by this review. `attempt` remains `3` in this Changes
Requested patch; `/moda-task ARCH-016-SHOPIFY-001` owns the increment to Attempt 4 when
the task is reclaimed. `ARCH-016-SYSTEM-TEST-001` remains Pending and MUST NOT start
automatically.

## Attempt 4 Completion Report

### Status

Ready for Review

### Correction Mapping

- Moved the authenticated Shop identity lookup ahead of every lifecycle mutation in `APP_SCOPES_UPDATE`.
- The existing `lockShopLifecycleRow(transaction, shopId)` call now precedes `transaction.session.update`, establishing the common `Shop FOR UPDATE -> Session/catalogue` order required by activation, scope update, and uninstall.
- Retained the post-lock authoritative Shop and durable offline Session reads; `payload.current` is persisted but cannot independently authorize a sync.
- Retained catalogue mutation inside the transaction and `SCOPES_UPDATED` publication after transaction commit.
- Added a focused route-level regression suite proving lock-before-Session order, post-Session offline eligibility read, post-commit publication, scope-removal invalidation, and payload-only fail-closed behavior.

### Files Changed

- `app/routes/webhooks/app/scopes-update/route.jsx`
- `tests/unit/routes/scopes-update.test.jsx`

### Validation

- focused route and lifecycle suites: `14 passed`;
- focused ESLint for both changed files: passed;
- `npm run build`: passed;
- Shopify config validation for `shopify.app.moda-interact.toml`: passed;
- `git diff --check`: passed;
- `npm test`: `617 passed`, `10 failed`, `3 skipped` across `630`; the same merchant-i18n catalogue baseline failures remain unrelated to Attempt 4 files;
- `npm run typecheck`: repository baseline diagnostics remain, including pre-existing JSX implicit-`any` diagnostics in the lifecycle route/service and unrelated application diagnostics;
- `npm run lint`: repository baseline errors remain in unrelated dashboard, billing, privacy, and existing test files; changed files pass focused ESLint.

### Worktree / Git Evidence

- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`;
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-016-SHOPIFY-001`;
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-016-SHOPIFY-001`;
- parent and implementation branches: `task/ARCH-016-SHOPIFY-001`;
- no shared checkout or `main` branch modified;
- implementation submodule and previously accepted Shared `0.12.1` dependency unchanged.

### Git / Handoff

- implementation correction commit: recorded below after publication;
- parent task/report commit: recorded below after publication;
- both mirrored task branches are pushed to their corresponding `origin/task/ARCH-016-SHOPIFY-001` refs;
- executor and claimed timestamp cleared; attempt remains `4`;
- no merge to `main` performed.

Task status is `review`; return control to `moda_architect` for re-review. No architect acceptance decision has been made by this agent.
