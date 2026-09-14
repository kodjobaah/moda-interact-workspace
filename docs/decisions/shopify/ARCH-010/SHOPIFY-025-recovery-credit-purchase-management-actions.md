---
id: ARCH-010-SHOPIFY-025
architecture_id: ARCH-010
title: Add merchant recovery-credit purchase history read model and refund lifecycle actions
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 79
executor: null
claimed_at: null
attempt: 3
depends_on:
- ARCH-010-DATABASE-014
- ARCH-010-BACKGROUND-021
- ARCH-010-BACKGROUND-022
- ARCH-010-SHOPIFY-014
- ARCH-010-SHARED-008
enables:
- ARCH-010-SHOPIFY-026
- ARCH-010-ADMIN-002
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-13
updated: 2026-09-14
---

# ARCH-010-SHOPIFY-025: Add merchant recovery-credit purchase history read model and refund lifecycle actions

## Objective

Provide one server-side merchant capability for:

1. listing the shop's own `RecoveryCreditPurchase` history across all canonical states;
2. requesting refund withdrawal for **one or more ACTIVE purchases**;
3. cancelling/reactivating one WITHDRAWN purchase while provider refund action has not begun;
4. returning deterministic per-purchase results under races with Background conversation reservations.

This task owns server read/action behaviour only. `SHOPIFY-026` owns the dedicated merchant page/components.

There is **no merchant-selected credit quantity** and no automatic Shopify money movement.

## Inspect before editing

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/repositories/**
app/routes/app/billing/**
server Prisma/database access conventions
authenticated Shopify user/shop resolution
merchant i18n/error/action conventions
tests/unit/services/**
```

Read implemented `DATABASE-014`, `BACKGROUND-021`, `BACKGROUND-022`, and `SHOPIFY-014` first.

Prefer a focused server service such as:

```text
app/services/billing/recovery-credit-purchase-management.service.ts
```

Use repository naming conventions if an equivalent service already exists. Do not put concurrency/business logic in React components.

## Merchant purchase-history read model

Expose a shop-scoped paginated read model. Query by `shopId` in the database; never fetch cross-shop rows then filter in memory.

Default page size 20, hard max 50 unless the repository already uses a stricter standard.

At minimum return for each purchase:

```text
id
status: REQUESTED | ACTIVE | COMPLETED | WITHDRAWN | REFUNDED
createdAt
activatedAt
creditsGranted
currentAmount
reservedAmount
availableAmount = max(currentAmount - reservedAmount, 0)
planName/planHandle snapshot safe for merchant display
original provider purchase amount/currency when confirmed
latest/live refund summary if any
completed refund summary if any
```

The server may return `availableAmount` as a computed read-model field; it is never persisted.

For merchant semantics:

```text
ACTIVE     -> availableAmount can be selected for withdrawal only if > 0
WITHDRAWN  -> zero spendable capacity; show current/reserved and refund workflow
COMPLETED  -> all credits consumed
REFUNDED   -> remaining unused credits were refunded
REQUESTED  -> purchase still awaiting provider confirmation; non-spendable/non-refundable
```

Do not expose internal provider credentials, raw GraphQL responses, Admin IDs or secrets.

## Request refund for one purchase — canonical transaction

A refund request means:

> Withdraw this entire purchase from new allocation and refund every credit that ultimately remains unused after existing reservations settle.

The merchant does **not** supply quantity, price, currency, provider charge ID or provider action kind.

Use one Serializable transaction with bounded retry/CAS for each selected purchase.

### Transaction steps

Freshly read:

```text
RecoveryCreditPurchase
ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS)
any non-terminal RecoveryCreditRefund for this purchase
```

Require:

```text
purchase.shopId = authenticated shop
purchase.status = ACTIVE
no non-terminal refund already exists
```

Compute from the winning database state:

```text
availableAmount = purchase.currentAmount - purchase.reservedAmount
```

If:

```text
availableAmount < 1
```

return per-item result:

```text
REFUND_NOT_AVAILABLE
```

with no mutation. The purchase stays ACTIVE.

Otherwise create one `RecoveryCreditRefund` with:

```text
source = MERCHANT_UI
purchase/shop identity
authenticated Shopify user identity when available
immutable commercial snapshots from purchase
currentAmountAtRequestSnapshot = purchase.currentAmount
reservedAmountAtRequestSnapshot = purchase.reservedAmount
availableAmountAtRequestSnapshot = availableAmount
status = REQUESTED
bounded deterministic requestKey/idempotency identity
```

Then atomically CAS both purchase and aggregate counter in the same transaction:

```text
purchase:
  WHERE id + status=ACTIVE + version=expected
  SET status=WITHDRAWN, version += 1

aggregate purchased counter:
  refundingQuantity += availableAmount
  version += 1 via expected-version CAS
```

`availableAmount` is the unreserved part of this purchase that becomes held immediately. Existing reservations remain represented in aggregate `reservedQuantity` and are not double-counted in `refundingQuantity`.

If either CAS fails, roll back the **whole transaction** and retry from fresh state. Do not reuse a stale browser quantity.

## Reservation/refund race — required observable results

The browser-displayed value is advisory only. Server state at the winning CAS decides.

### Displayed 1, conversation wins it

If the merchant saw:

```text
available = 1
```

but a conversation reserves that credit first, refund retry sees:

```text
available = 0
```

Return:

```text
REFUND_NOT_AVAILABLE
```

Do not set WITHDRAWN.

### Displayed 2, conversation reserves 1 first

Fresh retry sees:

```text
currentAmount = 2
reservedAmount = 1
availableAmount = 1
```

Request succeeds:

```text
ACTIVE -> WITHDRAWN
availableAmountAtRequestSnapshot = 1
```

Return enough state for UI copy equivalent to:

```text
Refund requested. 1 credit is currently refundable and 1 credit is still in progress.
The final refund will cover every credit that remains after in-flight conversations settle.
```

Do not promise that the final refund quantity is permanently 1. If the in-flight conversation later releases, BACKGROUND-022 moves that credit into the withdrawal hold and the final refund can become 2.

### Refund wins first

If ACTIVE -> WITHDRAWN wins first, a competing Background reservation must lose/retry and skip this lot. SHOPIFY-025 must not create a shop-global lock.

## Batch refund request: one or more purchases

Accept a bounded unique list of purchase IDs, recommended max 20 per action.

Security:

```text
all IDs are resolved under authenticated shopId
unknown/cross-shop IDs return a bounded per-item denial/not-found result
client cannot submit quantities or money
```

**Do not wrap the whole batch in one database transaction.**

Process each selected purchase independently through the canonical single-purchase transaction above. This is deliberate because different lots may race independently with conversations.

Return ordered per-purchase outcomes such as:

```text
REQUESTED
REFUND_NOT_AVAILABLE
NOT_ACTIVE
ALREADY_WITHDRAWN
ALREADY_REFUNDED
COMPLETED
NOT_FOUND
```

A failure on Purchase B must not roll back a successful withdrawal of Purchase A.

Use one client request identity for transport replay plus purchase ID in each per-lot request key, or another deterministic equivalent that permits:

- safe HTTP retry of the same batch;
- later new refund request after a prior refund request was withdrawn/reactivated;
- no duplicate live refund row for one purchase.

## Reactivate/cancel refund request

A merchant may change their mind only while the purchase is WITHDRAWN and the exact live refund is still strictly pre-provider-action:

```text
purchase.status = WITHDRAWN
refund.status = REQUESTED
no provider action/reference/confirmation exists
```

Use one Serializable transaction and CAS both refund and purchase/aggregate state.

Freshly compute:

```text
heldAvailable = purchase.currentAmount - purchase.reservedAmount
```

### If currentAmount > 0

Atomically:

```text
aggregate.refundingQuantity -= heldAvailable
purchase.status = ACTIVE
purchase.version += 1
refund.status = CANCELLED
refund.reason = MERCHANT_REACTIVATED (bounded canonical equivalent)
refund.version += 1
```

Do not change `currentAmount` or `reservedAmount`.

Existing reservations continue. The reactivated purchase returns to its original FIFO position because `activatedAt/createdAt/id` are unchanged.

### If currentAmount = 0

Do not reactivate. Atomically ensure:

```text
purchase.status = COMPLETED
refund.status = CANCELLED
reason = NO_CREDITS_REMAINING
```

and return a completed/no-credits result.

### Race with Admin provider-action lock

ADMIN-003 moves refund `REQUESTED -> PROVIDER_ACTION_REQUIRED` using refund version/CAS.

Merchant reactivation and Admin provider-action lock therefore compete on the same refund version. Exactly one wins.

If Admin wins first, merchant retry sees `PROVIDER_ACTION_REQUIRED` and must return:

```text
REACTIVATION_NOT_AVAILABLE
```

Never restore credits after provider settlement may have started.

## Aggregate-counter correctness

Request/re-activate paths must maintain the same aggregate conventions BACKGROUND-022 uses:

```text
request withdrawal:
  refundingQuantity += currentAmount - reservedAmount

reactivate:
  refundingQuantity -= currentAmount - reservedAmount
```

All counter updates require versioned CAS in the same transaction as purchase/refund lifecycle mutation.

Do not derive a shop-global purchase state from the aggregate counter.

## Merchant system messages

Use existing published Shared codes where product messaging already expects them:

```text
BILLING_REFUND_REQUEST_RECEIVED
BILLING_REFUND_COMPLETED
BILLING_REFUND_REJECTED
```

The request-received message may be created exactly once on successful per-purchase request using refund ID as identity.

Do not create new Shared codes merely for immediate UI confirmation/reactivation unless implementation proves the existing merchant history cannot communicate the state. If a new cross-service code is genuinely required, STOP and return to `moda_architect` rather than inventing one in this repo.

## Capacity resume after reactivation

Reactivation can restore spendable purchased capacity. Do not add a cross-repository Redis/BullMQ dependency to the Shopify app solely for this action.

BACKGROUND-009's durable periodic capacity-repair scan remains sufficient first-production recovery if no existing safe post-commit hook is available. If an accepted local integration already exposes a best-effort resume hint without coupling the app to Background internals, it may be used post-commit only.

## Required tests

At minimum prove:

1. list query is shop-scoped and paginated;
2. all five purchase states map correctly;
3. ACTIVE available is `currentAmount-reservedAmount`;
4. quantity/money supplied by client is ignored/rejected;
5. request with available 0 performs no mutation;
6. request with available >0 creates one refund + ACTIVE->WITHDRAWN + aggregate hold atomically;
7. same request replay is idempotent;
8. one-live-refund DB conflict is handled deterministically;
9. displayed-1 / reservation-wins returns REFUND_NOT_AVAILABLE;
10. displayed-2 / one reservation wins can withdraw fresh available 1;
11. refund-wins causes stale reservation CAS to lose (service contract/integration fixture);
12. batch processes lots independently and reports partial success;
13. cross-shop purchase ID cannot be read/mutated;
14. reactivation REQUESTED refund restores ACTIVE and aggregate hold exactly;
15. reactivation does not alter current/reserved values;
16. provider-action-required refund cannot be reactivated;
17. reactivation/Admin-lock race has exactly one winner;
18. currentAmount 0 cannot reactivate and yields COMPLETED;
19. no provider refund API/negative App Event is called;
20. focused service tests, repository typecheck/build/full relevant tests and `git diff --check` pass.

## Non-goals

Do not implement React/page UI, provider settlement, Admin approval, Background reservation code or database schema.

## Stop conditions

STOP if DATABASE-014/BACKGROUND-022 are not integrated, if authenticated shop scoping cannot be proven, or if the only implementation would require a shop-global lock or client-trusted quantity.

## Completion Report

### Status
Ready for Review.

### Attempt-3 Completion Report

#### Initially Missing
- `requestRefundWithRetry` handled `P2002` only by reloading the exact deterministic request key. A concurrent request for the same purchase with a different request ID could therefore rethrow the partial one-live-refund uniqueness conflict as a server error.

#### Applied Fixes
- Added a shop-scoped `RecoveryCreditPurchase.findFirst` fallback after the exact request-key lookup. The fallback reloads only live refund statuses and returns the persisted purchase/refund outcome, preserving `REQUESTED` versus `ALREADY_WITHDRAWN` semantics and winning current/reserved/available values.
- Added the required regression test for request B losing to a different-request live refund from request A. It proves no second refund is created and no Prisma error escapes.
- No route, schema, Shared, Background, Admin, provider, page-UI, quantity, money, or transaction-boundary changes were made.

#### Final Checklist Audit
- Authenticated shop resolution, shop-scoped paginated history, all five purchase states, safe refund summaries, computed availability, bounded unique batch input, ordered independent outcomes, client-quantity/money rejection by omission, Serializable per-purchase transactions, bounded retry, purchase/refund/aggregate CAS, exact hold/release accounting, reactivation/provider-action protection, zero-credit completion, and no provider/App Event call remain intact from the prior implementation.
- Same-request request-key replay remains deterministic.
- Different-request one-live-refund `P2002` now resolves from authenticated persisted `id + shopId` purchase state; cross-shop fallback state is not queried or exposed.
- Prisma schema conventions were rechecked: `RecoveryCreditRefund.requestKey` is unique, the partial live-refund uniqueness is authoritative, and `ShopEntitlementCounter` identity is `(shopId, counter)` with versioned fields. No schema change is required.
- All task non-goals remain satisfied. No unresolved functional requirement was found in the second explicit pass.

#### Validation
- Focused service test: passed, 12/12.
- Related billing tests: passed, 2 files and 196 tests.
- Full test suite: passed, 42 files and 516 tests; 2 files and 3 tests skipped.
- `npm run prisma:generate`: passed.
- `npm run prisma:validate`: passed.
- `npm run build`: passed.
- Direct ESLint for the changed service, route, and test: passed; only the repository TypeScript-version support warning was emitted.
- Changed-file diagnostics: no errors.
- `git diff --check`: passed.
- Repository `npm run lint`: remains non-zero on 16 pre-existing errors outside changed files. Repository `npm run typecheck`: remains non-zero on the known baseline JSX implicit-any/Polaris, missing `d3` declarations, nullable billing plan, Redis overload, and incomplete billing test mock diagnostics; no diagnostic references the changed files.

#### Git / Worktree / Claim Evidence
- Launcher claim commit: `ec9e45437bbc889fa04c5e6c0bc947afe350c395`; attempt 3 was already claimed by the launcher and was not re-prepared or reclaimed.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-025`, branch `task/ARCH-010-SHOPIFY-025`, clean after publication.
- Implementation commit: `957990b0b36b63eb4ff9f5871abead8d4d6ce68e`, pushed to `origin/task/ARCH-010-SHOPIFY-025`.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-025`, branch `task/ARCH-010-SHOPIFY-025`.

#### Unresolved Baseline Issues
- Repository-wide lint and typecheck baseline failures remain outside this task and do not reference the final changed files.

### Initial Audit Findings and Corrections
- The existing service had no authenticated server resource boundary for the future merchant page. Added `app/routes/app/billing/recovery-credits/route.ts` with shop resolution, capability checks, paginated loader, bounded batch action, and reactivation action; no page UI or provider call was added.
- A `P2002` request-key conflict was reported as `REQUESTED` without reading the authoritative row. The service now reloads the refund by its deterministic request key and returns the persisted purchase/refund lifecycle outcome.
- The original pagination test fixture ignored its `shopId` filter and falsely expected a cross-shop row. The fixture now applies the filter and the assertion proves the other shop is excluded.
- The Prisma schema was inspected and validated: `requestKey` is unique, aggregate identity is `(shopId, counter)`, and all fields/enums used by the service match the existing schema. No schema change is required.

### Requirement Checklist
- Shop-scoped history, default page size 20, hard maximum 50, all five statuses, safe summaries, and computed availability: implemented and tested.
- Fresh Serializable refund transactions, bounded retry, purchase/refund/aggregate CAS, exact hold/release accounting, and no shop-global lock: implemented.
- Client quantity/money is ignored; the resource action accepts only authenticated shop context, purchase IDs, and request identity.
- Batch input is unique and bounded to 20, each lot is independent, replay is deterministic, and unknown/cross-shop IDs do not disclose data.
- Reactivation requires `WITHDRAWN` plus a strictly pre-provider-action `REQUESTED` refund, preserves current/reserved values, releases only the held aggregate amount, and completes zero-current purchases.
- No provider refund API, negative App Event, new Shared code, schema, Background, Admin, or page-UI change was introduced.

### Required Test Items
1. Shop-scoped paginated list: covered by the list test and corrected fixture filter.
2. All five purchase states: covered by the status mapping test.
3. ACTIVE availability: covered by computed availability assertions.
4. Client quantity/money cannot control the operation: covered by the withdrawal test with conflicting client values.
5. Zero availability is a no-op: covered by the zero-availability test.
6. Successful refund creates one refund, withdraws the purchase, and holds aggregate capacity: covered.
7. Same-request replay is idempotent: covered.
8. Request-key uniqueness conflict is deterministic: covered by the added persisted-state conflict test.
9. Displayed 1 but reservation wins: covered by fresh zero availability.
10. Displayed 2 but one reservation wins: covered by fresh partial availability and request snapshot behavior.
11. Refund wins against stale reservation CAS: covered by the Serializable/CAS retry contract and conflict retry test.
12. Batch partial success and independent outcomes: covered.
13. Cross-shop purchase cannot be read or mutated: covered.
14. Reactivation restores ACTIVE and releases the aggregate hold: covered.
15. Reactivation preserves current/reserved values: covered by returned state assertions and CAS predicates.
16. Provider-action-required refund cannot reactivate: covered.
17. Reactivation/Admin-lock race has one CAS winner: covered by provider-action lock rejection and shared refund-version CAS boundary.
18. Zero-current purchase completes instead of reactivating: covered.
19. No provider refund API or negative App Event is called: the service has no provider/event dependency; the focused path is database-only and the build/test suite passes.
20. Focused tests, relevant suite, full suite, Prisma validation/generation, build, touched lint, typecheck review, and `git diff --check`: recorded below.

### Files Changed
- `moda-interact/app/services/billing/recovery-credit-purchase-management.service.ts`
- `moda-interact/app/routes/app/billing/recovery-credits/route.ts`
- `moda-interact/tests/unit/services/recovery-credit-purchase-management.service.test.ts`

### Validation Results
- Focused management service: passed, 11/11.
- Relevant billing suites: passed, 3 files and 198 tests.
- Full suite: passed, 42 files and 515 tests; 2 files and 3 tests skipped.
- `npm run prisma:generate`: passed.
- `npm run prisma:validate`: passed.
- `npm run build`: passed.
- Direct ESLint on all three changed files: passed; only the repository TypeScript-version support warning was emitted.
- Repository lint script: reports 16 pre-existing errors outside the changed files because its script ignores positional file arguments; no changed-file lint error.
- `git diff --check`: passed.
- `npm run typecheck`: remains non-zero on the known repository baseline (existing JSX implicit-any/Polaris diagnostics, missing `d3` declarations, existing nullable billing plan, Redis overload, and incomplete billing test mocks); no diagnostic remains in the changed service, route, or focused test.

### Git / VCS Evidence
- Claim commit: `08d85bb9ac97e30ca1c2d8e4b2af3879e376ea09` on parent and implementation task branches.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-025`.
- Implementation branch: `task/ARCH-010-SHOPIFY-025`.
- Implementation commit: `1db0a03` (`fix(shopify): harden recovery credit management actions`), pushed to `origin/task/ARCH-010-SHOPIFY-025`.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-025`.
- No schema, Shared, Background, Admin, provider, or page-UI files were changed.

### Unresolved Issues
- The repository-wide typecheck and lint baselines remain unresolved outside this task; they do not reference the final changed files.

### Architect Review
Pending.

## Architect Review — Attempt 2

### Status

**Changes Requested — one functional conflict-recovery correction only**

This review intentionally prioritises merchant/runtime functionality over exhaustive
test coverage.

The second-pass implementation is broadly accepted:

```text
authenticated merchant resource route
shop-scoped purchase-history query
bounded pagination
all five purchase lifecycle states
server-computed availableAmount
fresh-state refund quantity
one Serializable transaction per selected purchase
independent batch-lot outcomes
ACTIVE -> WITHDRAWN + aggregate refund hold
pre-provider WITHDRAWN -> ACTIVE reactivation
zero-current WITHDRAWN -> COMPLETED
provider-action lock blocks reactivation
exact purchase/refund/aggregate CAS
no client-trusted quantity/money
no provider refund API or negative App Event
no schema / Background / Admin / Shared / page-UI change
```

The corrected cross-shop test fixture and deterministic same-request `requestKey`
replay are also accepted.

One explicit database race is still not handled functionally.

---

### Finding — `P2002` from the one-live-refund-per-purchase index can escape as a 500

The database has two independent uniqueness constraints relevant to refund creation:

```text
1. RecoveryCreditRefund.requestKey UNIQUE

2. RecoveryCreditRefund_one_non_terminal_per_purchase_key
   UNIQUE (purchaseId)
   WHERE status IN (
     REQUESTED,
     PROVIDER_ACTION_REQUIRED,
     NEEDS_ATTENTION
   )
```

The current `requestRefundWithRetry(...)` catches any `P2002`, but recovery then looks
up only:

```ts
RecoveryCreditRefund.findUnique({
  where: {
    requestKey: requestKey(
      input.shopId,
      input.requestId,
      input.purchaseId,
    ),
  },
})
```

That correctly resolves a replay/race where the conflicting unique constraint is the
same deterministic `requestKey`.

It does **not** resolve this normal merchant race:

```text
Request A:
  requestId = A
  purchase  = P

Request B:
  requestId = B
  purchase  = P

both read P as ACTIVE with no live refund
both attempt RecoveryCreditRefund.create(...)

A wins:
  creates requestKey(..., A, P)
  withdraws P

B loses:
  PostgreSQL raises P2002 from the partial
  one-non-terminal-refund-per-purchase unique index
```

B then searches for:

```text
requestKey(..., B, P)
```

but the authoritative winning row is:

```text
requestKey(..., A, P)
```

so the lookup returns null and the Prisma error is rethrown.

The merchant therefore receives a server failure for a concurrency condition that the
task explicitly requires to be deterministic.

This violates:

```text
one-live-refund DB conflict is handled deterministically
safe HTTP/batch concurrency
bounded per-purchase outcome under races
```

This is a production functionality defect, not a request for additional coverage
breadth.

---

### Required correction

Modify only:

```text
app/services/billing/recovery-credit-purchase-management.service.ts
```

Keep the current same-request `requestKey` reload first.

When a `P2002` occurs:

```text
1. reload by the exact deterministic requestKey;
2. if found and shop ownership matches, return the persisted authoritative outcome;
3. if not found, resolve the purchase under authenticated shopId and reload its
   current non-terminal refund;
4. if a live refund now exists for that purchase, return the deterministic current
   purchase/refund outcome;
5. only rethrow if neither the exact request nor an authoritative live-refund state
   can explain the uniqueness conflict.
```

The purchase fallback must be shop-scoped at the database query boundary, e.g. an
equivalent of:

```ts
recoveryCreditPurchase.findFirst({
  where: {
    id: input.purchaseId,
    shopId: input.shopId,
  },
  include: {
    refunds: {
      where: {
        status: {
          in: [...LIVE_REFUND_STATUSES],
        },
      },
      orderBy: {
        createdAt: "desc",
      },
      take: 1,
    },
  },
})
```

Do not fetch a cross-shop purchase and then expose its refund state.

For an authoritative live refund, preserve the existing outcome semantics:

```text
REQUESTED                -> REQUESTED
PROVIDER_ACTION_REQUIRED -> ALREADY_WITHDRAWN
NEEDS_ATTENTION          -> ALREADY_WITHDRAWN
```

and include current/reserved/available amounts from the winning purchase state.

Do not create another refund row.

Do not retry with a new request key.

Do not wrap the whole batch in one transaction.

Do not weaken the database partial unique index.

Do not inspect Prisma error-message text or index names as business authority; the
persisted purchase/refund state is authoritative.

---

### Functional regression evidence required

No broad test expansion is required.

Update only:

```text
tests/unit/services/recovery-credit-purchase-management.service.test.ts
```

Add one permanent functional regression:

```text
resolves a different-request P2002 live-refund race from the persisted purchase state
```

Exact scenario:

```text
purchase P initially ACTIVE

winning persisted state after concurrent request A:
  purchase P = WITHDRAWN
  live refund = REQUESTED
  requestKey = key for request A

current call:
  requestId = B

transaction throws P2002
exact key-B lookup returns null
shop-scoped purchase fallback returns P + winning live refund
```

Require:

```text
service resolves normally
code = REQUESTED
purchaseId = P
no second refund is created
no Prisma error escapes
```

Also preserve the existing same-request request-key conflict test.

One additional row using `PROVIDER_ACTION_REQUIRED` is optional, not required for this
functionality-first review, because it uses the same persisted-state mapping.

No new integration/race suite is required solely for this deterministic post-conflict
read.

---

### Accepted work — do not churn

Do not redesign:

```text
app/routes/app/billing/recovery-credits/route.ts
history pagination/read model
batch independence
refund request transaction/CAS
aggregate refundingQuantity accounting
reactivation transaction/CAS
zero-current completion
provider-action protection
requestKey format
purchase/refund schema
```

Do not add:

```text
provider refund calls
negative Shopify App Events
Background dependencies
Admin behavior
React/page UI
Shared codes
schema migrations
shop-global locks
```

unless the narrow conflict-resolution correction proves one of those is genuinely
required, in which case STOP and return the limitation to `moda_architect`.

---

### Attempt-3 allowed scope

Production:

```text
app/services/billing/recovery-credit-purchase-management.service.ts
```

Tests:

```text
tests/unit/services/recovery-credit-purchase-management.service.test.ts
```

plus this task/Completion Report.

---

### Attempt-3 validation

Prioritise the functional slice:

```bash
npm exec vitest run \
  tests/unit/services/recovery-credit-purchase-management.service.test.ts

npm run build
npm run prisma:validate
git diff --check
```

Run the relevant/full repository suite only for regression awareness.

The known unrelated repository typecheck/lint baseline remains non-blocking if the
changed service/test have no new diagnostics.

Do not spend Attempt 3 fixing unrelated baseline diagnostics.

---

### Workflow / Completion Report

Preserve immutable Attempt-2 publication history:

```text
Claim:
08d85bb9ac97e30ca1c2d8e4b2af3879e376ea09

Attempt-2 implementation:
1db0a03

Attempt-2 parent report:
78bd50f
```

Record full SHAs from repository history where available.

Return this SAME task through `/moda-task`.

Preserve:

```text
attempt: 2
```

The next authorised claim must increment to **Attempt 3 exactly once**.

Attempt 3 may return to `review` when:

```text
1. same-request requestKey P2002 remains deterministic;
2. different-request one-live-refund P2002 resolves from authenticated persisted
   purchase/refund state;
3. no duplicate refund is created;
4. no Prisma error escapes for that normal concurrency race;
5. focused functional validation passes;
6. no changed-file regression is introduced;
7. status = review, executor = null, claimed_at = null;
8. both worktrees are clean and pushed.
```

Then STOP and return to `moda_architect`.

`ARCH-010-SHOPIFY-026`, `ARCH-010-ADMIN-002`, and
`ARCH-010-SYSTEM-TEST-003` remain gated until `SHOPIFY-025` is
architect-accepted Complete.

## Architect Review — Attempt 3

### Status

**Accepted**

This review intentionally prioritises production functionality, merchant isolation,
refund-state correctness, and concurrency behaviour over exhaustive test coverage.

Attempt 3 closes the remaining different-request `P2002` race without regressing the
previously accepted purchase-history, refund, reactivation, or accounting behavior.

### Accepted uniqueness-conflict recovery

The refund service now distinguishes the two authoritative database conflict paths
without relying on Prisma error-message text or index names.

On `P2002`:

```text
1. reload the exact deterministic requestKey;
2. if that exact request exists for the authenticated shop, return persisted state;
3. otherwise reload purchase by exact:
     purchase.id
     + authenticated shopId
4. inspect only current non-terminal/live refunds;
5. if an authoritative live refund exists, return that persisted outcome;
6. otherwise rethrow the unexplained uniqueness error.
```

This correctly handles both:

```text
same-request transport replay
```

and:

```text
different-request race for the same ACTIVE purchase
```

where the second transaction loses the database's one-live-refund-per-purchase unique
constraint.

The losing merchant request therefore no longer receives an avoidable server error
when another request has already established the authoritative refund state.

### Accepted shop isolation

The different-request fallback is scoped at the database query boundary:

```text
purchase.id = requested purchase
AND
purchase.shopId = authenticated shop
```

The implementation does not fetch a cross-shop purchase and filter it in memory.

Therefore a uniqueness conflict cannot be used to discover another shop's purchase or
refund lifecycle.

Unknown/cross-shop purchase IDs continue to resolve through the bounded merchant
not-found behavior.

### Accepted refund outcome mapping

A persisted live refund is mapped from durable state:

```text
REQUESTED
  -> REQUESTED

PROVIDER_ACTION_REQUIRED
  -> ALREADY_WITHDRAWN

NEEDS_ATTENTION
  -> ALREADY_WITHDRAWN
```

and current/reserved/available amounts are returned from the authoritative winning
purchase state.

The conflict path does not:

```text
create a second refund
generate another request key
repeat the provider action
trust client quantity
trust client money
wrap the whole batch in one transaction
weaken the partial unique index
```

### Accepted reactivation / later-new-request semantics

The fallback loads only live statuses:

```text
REQUESTED
PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
```

A refund cancelled by successful merchant reactivation is therefore historical rather
than an active conflict owner.

A later genuine refund request with a new request identity can proceed against the
reactivated ACTIVE purchase, subject to the ordinary fresh-state availability and CAS
rules.

This preserves the task requirement that transport replay remains bounded while a
later new refund request after reactivation is still possible.

### Previously accepted functionality preserved

Architect inspection confirms the following remain intact:

```text
authenticated merchant resource route
shop-scoped purchase-history query
default/max pagination bounds
all canonical purchase states
server-computed availableAmount
no client-trusted refund quantity or money
bounded unique batch input
per-purchase batch independence
Serializable per-purchase transaction
bounded whole-transaction retry
fresh-state refund availability
purchase ACTIVE -> WITHDRAWN CAS
aggregate refundingQuantity hold
one live refund per purchase
same-request deterministic requestKey replay
pre-provider REQUESTED refund reactivation
WITHDRAWN -> ACTIVE reactivation
zero-current WITHDRAWN -> COMPLETED
provider-action/reference/confirmation reactivation lockout
purchase/refund/aggregate versioned CAS
no provider refund API call
no negative Shopify App Event
no schema / Shared / Background / Admin / page-UI change
```

No additional architectural correction is required.

### Validation accepted

```text
Focused service tests:
  12 passed

Full application suite:
  516 passed
  3 skipped

Prisma generate:
  passed

Prisma validate:
  passed

Production build:
  passed

Changed-file lint:
  passed

git diff --check:
  passed

Repository-wide lint/typecheck:
  known unrelated baseline failures remain
  no changed-file diagnostic introduced
```

Acceptance is based on the runtime behavior above, not on satisfying a particular
test-count target.

### Accepted implementation evidence

Developer handoff:

```text
Attempt-3 implementation:
957990b0b36b63eb4ff9f5871abead8d4d6ce68e

Attempt-3 parent report:
57eaa82
```

Preserve the full parent-report SHA from repository history when publishing the
architect acceptance.

Both worktrees were reported clean and pushed.

### Dependency reconciliation

`ARCH-010-SHOPIFY-025` is Complete.

All declared prerequisites of:

```text
ARCH-010-SHOPIFY-026
```

are now Complete:

```text
ARCH-010-SHOPIFY-025
ARCH-010-SHOPIFY-012
```

Therefore `SHOPIFY-026` is promoted to `ready`.

All declared prerequisites of:

```text
ARCH-010-ADMIN-002
```

are also now Complete:

```text
ARCH-010-DATABASE-014
ARCH-010-BACKGROUND-022
ARCH-010-SHOPIFY-025
ARCH-010-SHARED-008
ARCH-010-ADMIN-010
```

Therefore `ADMIN-002` is promoted to `ready`.

`ARCH-010-SYSTEM-TEST-003` remains Pending/manual-gated because it still depends on
`SHOPIFY-026`, `ADMIN-003`, and its other declared implementation prerequisites.

The current automatic implementation-ready frontier is:

```text
ARCH-010-SHOPIFY-026
ARCH-010-ADMIN-002
```

No Attempt 4 is required for `ARCH-010-SHOPIFY-025`.

