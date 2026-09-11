---
id: ARCH-010-BACKGROUND-004
architecture_id: ARCH-010
title: Stop queued recovery work for inactive shops
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
executor: copilot
claimed_at: 2026-09-11T19:12:00Z
priority: 45
attempt: 2
depends_on: []
enables:
  - ARCH-010-BACKGROUND-006
  - ARCH-010-BACKGROUND-013
  - ARCH-010-BACKGROUND-017
  - ARCH-010-BACKGROUND-018
  - ARCH-010-SHOPIFY-005
created: 2026-09-11
updated: 2026-09-11T19:18:00Z
---

# ARCH-010-BACKGROUND-004: Stop queued recovery work for inactive shops

## Objective

Make current `Shop.status` an early execution gate for queued Shopify/recovery work so jobs accepted before uninstall become terminal no-ops once the owning shop is `UNINSTALLED` or `SUSPENDED`.

This task must prevent new recovery/customer/business work. It must **not** delete historical merchant state or change subscription/credit state.

## Inspect before editing

Inspect the implemented repository, including at least:

```text
src/workers/checkout.worker.ts
src/workers/orders.worker.ts
src/workers/pending-recovery-candidate.worker.ts
src/services/checkout-recovery.service.ts
src/services/pending-recovery-candidate.service.ts
src/services/abandoned-checkout-lookup.service.ts
src/services/effective-billing-policy.service.ts
src/services/shopify-usage-event-publisher.service.ts
src/services/billing-reconciliation.service.ts
src/events/shopify-contract-adapter.ts
tests/unit/services/*checkout*
tests/unit/services/*pending-recovery*
tests/unit/services/effective-billing-policy.service.test.ts
tests/unit/services/shopify-usage-event-publisher.service.test.ts
package.json
```

Read actual package scripts before choosing validation commands.

If ARCH-010-BACKGROUND-001/002/003 have already been implemented when this task begins, inspect their integrated code too and apply the same inactive-shop rule to any new subscription/recovery entrypoint that can execute merchant business work.

## Current implementation facts from the architecture snapshot

The supplied snapshot already has a late gate in `EffectiveBillingPolicyResolver`:

```text
subscription.shop.status !== ACTIVE -> SHOP_UNAVAILABLE
```

That is necessary but insufficient. Before reaching billing admission, queued recovery jobs can currently:

- schedule/refresh delayed recovery candidates;
- resolve current Shopify abandoned-checkout state;
- materialize durable CheckoutRecovery state;
- update recovery state.

The task must move the inactive-shop decision earlier at the durable business-execution boundaries.

## Required implementation shape

Prefer one small reusable Background-owned helper/service for current shop execution eligibility rather than copying different ad-hoc status semantics into every worker.

Example responsibility only (exact naming is implementation-owned):

```ts
isShopExecutionActive(shopId): Promise<boolean>
resolveActiveShopByDomain(domain): Promise<{ id: string } | null>
```

Do not create a new cross-repository/shared contract for this local database policy.

The policy is exactly:

```text
ACTIVE       -> business execution may proceed
UNINSTALLED  -> terminal no-op
SUSPENDED    -> terminal no-op
missing shop -> preserve existing not-found semantics
```

Do not infer eligibility from Subscription status as a replacement for Shop.status.

## Required guarded paths

At minimum cover all supplied-code paths below.

### Checkout-created scheduling

Before `PendingRecoveryCandidateService.scheduleFromCheckoutCreated()` creates/updates a BullMQ delayed candidate or Redis candidate indexes:

1. resolve shop by canonical domain;
2. read `Shop.status` in the same lookup;
3. if not ACTIVE, return a typed discarded/no-op outcome;
4. do not create/update candidate job data or indexes.

Do not throw/retry because the shop is uninstalled.

### Checkout update / cart activity

When an event resolves to a known shop that is not ACTIVE:

- do not refresh/reschedule pending candidates;
- do not call Shopify abandoned-checkout lookup;
- do not update CheckoutRecovery business state;
- return a stable ignored/discarded outcome.

### Order completion

If a queued order job belongs to an inactive shop, do not initiate new recovery-domain work. Preserve only any minimal idempotent cleanup/correlation needed to make already-queued work terminal; do not send customer communication or create new usage.

### Matured pending candidate

`materializeMaturedCandidate(candidate)` must check current Shop.status **before**:

- `resolveShopDomain()` if that call would cause provider/business work;
- Shopify abandoned-checkout lookup;
- creation/update of CheckoutRecovery;
- customer/conversation creation;
- outbound recovery admission.

For an inactive shop, return a terminal result such as `discarded-shop-unavailable` and allow the worker's existing `finally` cleanup to remove pending-candidate indexes.

Do not retry an inactive candidate.

## Jobs racing with uninstall

No attempt to purge every BullMQ queue is required.

Correctness comes from checking durable Shop.status when each job executes. A job that was queued while ACTIVE but starts after the uninstall transaction commits must no-op.

If a job has already passed the execution gate before the uninstall transaction commits, preserve existing transactional/idempotent behaviour. Do not introduce a distributed lock across the uninstall webhook and all workers in this task.

## Accounting exception

Do not break `ShopifyUsageEventPublisherService`'s current uninstall-cutoff behaviour.

Usage that represents work committed **before** `Shop.uninstalledAt` may still be published after uninstall. Post-uninstall business work must not create new billable usage.

Do not blanket-filter all `UNINSTALLED` usage rows out of the publisher.

## Billing reconciliation

The supplied `BillingReconciliationService.selectRotatingShopPage()` already selects only `Shop.status = ACTIVE`.

Preserve that rule. If ARCH-010 delayed subscription reconciliation has been integrated, its ordinary scanner/job execution must also treat an uninstalled shop as a stale/no-op target unless the later reinstall architecture explicitly permits it.

Do not reactivate a shop from Background in this task.

## Observability

Use the shared structured logger if new logging is required. Emit at most bounded operational metadata such as reason/job type; do not emit customer payloads or secrets.

A shop-unavailable no-op is an expected lifecycle outcome, not an exception stack.

Do not create duplicate generic BullMQ/HTTP telemetry.

## Required tests

Add focused coverage proving at least:

1. ACTIVE checkout-created event still schedules a candidate;
2. UNINSTALLED checkout-created event creates no candidate/job/index;
3. SUSPENDED checkout-created event creates no candidate/job/index;
4. queued checkout-update for UNINSTALLED shop performs no Shopify lookup and no recovery mutation;
5. queued cart-activity for UNINSTALLED shop performs no candidate mutation;
6. queued order work for UNINSTALLED shop performs no new customer/recovery action;
7. matured candidate for UNINSTALLED shop performs no Shopify abandoned-checkout lookup;
8. matured candidate for UNINSTALLED shop creates no CheckoutRecovery/customer/conversation/outbound action;
9. matured inactive candidate returns a terminal outcome and pending-candidate cleanup still occurs;
10. an ACTIVE shop continues through the existing materialization path unchanged;
11. `EffectiveBillingPolicyResolver` still rejects non-ACTIVE shops;
12. billing reconciliation continues to scan ACTIVE shops only;
13. pre-uninstall committed usage publication behaviour remains unchanged;
14. post-uninstall work does not create a new normal recovery usage event through the guarded paths.

Where a provider dependency is mocked, assert it was **not called** for inactive shops.

## Non-goals

Do not:

- change `ShopService.markUninstalled()`; that belongs to `ARCH-010-SHOPIFY-005`;
- solve reinstall;
- purge every queue on uninstall;
- change normalized WhatsApp contracts;
- redesign shop identification;
- change subscription/credit/refund state;
- implement billing-period rollover;
- modify another repository.

## Validation

Run the repository's actual focused tests for changed services, then the repository's declared unit/build/typecheck validations required by its package scripts and task baseline. Also run:

```text
git diff --check
```

If the actual repository lacks a named script, report the gap; do not invent an unrelated validation contract.

## Stop conditions

Stop and return to `moda_architect` if:

- inactive-shop gating requires a new cross-repository event field/contract;
- a relevant queued path cannot identify the shop from durable state;
- making a job terminal would corrupt required pre-uninstall accounting;
- the implementation would require changing Shopify ingress or another repository;
- an ARCH-010 task integrated after this definition materially changes the worker ownership boundary.

## Completion Report

### Status
Ready for Architect Review

### Files Changed
- `moda-interact-background/src/services/shop-execution-eligibility.service.ts`
- `moda-interact-background/src/services/pending-recovery-candidate.service.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/tests/unit/services/checkout-refresh.test.ts`
- `moda-interact-background/tests/unit/services/order-recovery-correlation.test.ts`
- `moda-interact-background/tests/unit/services/matured-candidate.materialization.test.ts`
- `moda-interact-background/tests/unit/workers/pending-recovery-candidate.worker.test.ts`

### Work Completed
- Added a Background-owned durable `Shop.status` eligibility service.
- Added terminal no-op gating for `UNINSTALLED` and `SUSPENDED` checkout-created scheduling before BullMQ or Redis writes.
- Added inactive-shop gates for matured candidates, checkout updates, cart activity, and order completion before Shopify or recovery-domain work.
- Preserved missing-shop semantics, ACTIVE scheduling/materialization behavior, billing reconciliation selection, and existing usage publisher cutoff behavior.
- Added explicit ACTIVE fixtures and regression coverage proving inactive checkout-created events create no job or index.
- Added inactive checkout-update, cart-activity, order-completion, and matured-candidate assertions, including the required order-shop status projection.
- Added worker-level coverage proving matured inactive candidates still run pending-candidate cleanup in `finally`.
- Implementation commit: `c03027b` (`fix(background): gate inactive recovery execution`).

### Validation
- Passed: complete focused B004 regression set, 83 tests across five suites.
- Passed: `git diff --check`.
- The adjacent EffectiveBillingPolicy, billing reconciliation, and usage publisher suites remain blocked during module loading because `@prisma/client` has not been generated in this checkout.
- `npx tsc --noEmit` remains blocked by the existing syntax error in `src/entrypoints/billing.ts:37`.
- `npm run build` and `npm run prisma:validate` remain blocked because their configured Prisma path `database/prisma/schema.prisma` does not exist in this checkout.
- `npm run typecheck` is not declared in `package.json`.
- Full `npm run test:unit` was not run after the focused validation because the repository-level Prisma and TypeScript blockers remain unresolved.

### Validation Results
- Focused B004 suites: 5 files, 83 tests passed.
- Implementation worktree branch published: `task/ARCH-010-BACKGROUND-004` at `c03027b`.
- Parent task branch synchronized from `main` before attempt-2 claim; implementation branch was published after the corrections.
- No architect acceptance decision has been made by this agent.

### Git / VCS
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-004`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-004`.
- Parent branch: `task/ARCH-010-BACKGROUND-004`.
- Implementation branch: `task/ARCH-010-BACKGROUND-004`.
- Parent claim commit: `abdf404`.
- Implementation commit: `c03027b`, pushed to `origin/task/ARCH-010-BACKGROUND-004`.
- Task metadata handoff is published on the parent branch; no merge or acceptance was performed.

### Architect Review

#### Review Status

Changes Requested

#### Attempt 1 — Changes Requested

The implementation direction is correct, but the submitted handoff contains two
concrete code defects plus incomplete acceptance coverage and workflow evidence.

##### Accepted design direction

Architect review accepts the following approach and does not request redesign:

- a Background-owned `ShopExecutionEligibilityService` is the right local reusable
  policy boundary;
- checkout-created scheduling resolves durable `Shop.status` before BullMQ/Redis
  candidate mutation;
- `ACTIVE` proceeds, while `UNINSTALLED` and `SUSPENDED` return a terminal
  `discarded-shop-unavailable` outcome;
- checkout-update checks current shop status before candidate refresh, Shopify
  abandoned-checkout lookup or recovery mutation;
- cart activity checks current shop execution eligibility before candidate mutation;
- matured-candidate materialization checks durable shop activity before Shopify
  provider lookup or recovery creation;
- order completion is intended to gate inactive shops before new recovery-domain
  work;
- missing-shop behaviour remains distinct from inactive-shop behaviour;
- the existing usage-publisher uninstall cutoff and ACTIVE-only billing-reconciliation
  selection were not blanket-rewritten.

Do not redesign those accepted boundaries in Attempt 2.

##### Correction 1 — fix the invalid order-shop projection

Current `handleOrderCompleted()` does:

```ts
const shop = await prisma.shop.findUnique({
  where: { domain: event.shop },
  select: { id: true },
});

...

if (shop.status !== "ACTIVE") {
```

`status` is not selected, so the returned Prisma object does not contain
`shop.status`.

Select the durable status in the same lookup:

```ts
select: { id: true, status: true }
```

and preserve the existing missing-shop / inactive-shop outcomes.

Add focused coverage that would fail if the status field is omitted.

##### Correction 2 — make the matured-candidate result type match runtime behaviour

`materializeMaturedCandidate()` now returns:

```ts
{
  outcome: "discarded-shop-unavailable",
  checkoutToken: candidate.checkoutToken,
}
```

but `MaturedCandidateMaterializationResult` does not declare that variant.

Add the terminal result variant to the union. Do not weaken the return type to a
generic string.

##### Correction 3 — add the required inactive-path regression coverage

The archive contains focused `UNINSTALLED` / `SUSPENDED` assertions for
`PendingRecoveryCandidateService.scheduleFromCheckoutCreated()`, which covers the
checkout-created scheduling requirement.

However, the submitted tests do not contain focused assertions for the other
required inactive paths. In particular, Architect review could not find
`shop-unavailable` / `discarded-shop-unavailable` coverage for:

- checkout-update;
- cart activity;
- order completion;
- matured-candidate materialization.

Attempt 2 must add focused tests proving at least:

1. inactive checkout-update does not call
   `pendingRecoveryCandidateService.refreshCandidateActivity`;
2. inactive checkout-update does not call Shopify abandoned-checkout lookup and
   does not mutate `CheckoutRecovery`;
3. inactive cart activity does not mutate/refresh a pending candidate;
4. inactive order completion performs no candidate resolution/cancellation,
   order tombstone creation, recovery transaction/update or new customer/recovery
   work;
5. inactive matured candidate does not call `resolveShopDomain()` or Shopify
   abandoned-checkout lookup;
6. inactive matured candidate creates/updates no CheckoutRecovery, customer,
   conversation or outbound action;
7. the inactive matured-candidate result is terminal
   `discarded-shop-unavailable`;
8. the worker's existing `finally` cleanup still executes for that terminal result;
9. ACTIVE checkout-update/cart/order/matured paths continue through their existing
   behaviour;
10. the existing `EffectiveBillingPolicyResolver` non-ACTIVE rejection,
    ACTIVE-only billing reconciliation, and pre-uninstall committed-usage
    publication tests remain passing or are explicitly rerun.

Where provider/recovery dependencies are mocked, assert they were not called.

The task contract requires these behaviours; passing only the 36
pending-candidate tests is not sufficient acceptance evidence.

##### Correction 4 — repair the test fixture/module-load blocker if it is local to the tests

The Completion Report states that checkout/order focused suites cannot load because
an existing test mock leaves `SubscriptionProjectionStatus.ACTIVE` undefined.

If that blocker is in a test mock owned by the Background repository and can be
corrected without changing production semantics, update the mock so the focused
ARCH-010-BACKGROUND-004 tests can actually execute.

Do not use the pre-existing mock defect as a reason to omit the task's required
focused assertions.

If correcting that mock would cross a task/repository boundary or materially alter
another accepted contract, stop and report the exact blocker to Architect instead.

##### Correction 5 — record mandatory worktree/synchronisation evidence

The submitted Completion Report still says:

```text
### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.
```

That does not satisfy the mandatory task-worktree isolation policy.

On Attempt 2 record:

```text
Parent worktree:
Implementation worktree:

Negative isolation assertions:
  parent is not the primary/shared workspace: yes
  implementation is not the shared repository checkout: yes

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Implementation commit:
Parent report commit:
Branches pushed:
Worktrees clean:
```

Use the resolver-selected canonical worktrees.

##### Repository-wide validation blockers

The reported failures in:

- `src/entrypoints/billing.ts:37`;
- the existing Prisma build path;
- undeclared `npm run typecheck`;
- unrelated baseline unit/mock failures;

may remain documented if they are truly pre-existing and unchanged by this task.

They do **not**, however, waive the requirement that the changed inactive-shop
paths themselves are type-correct and have executable focused coverage.

After fixing the two direct code defects and test fixtures, run the maximum focused
validation available for every changed guarded path and record exact commands and
results.

Also rerun:

```text
git diff --check
```

If a repository-wide command remains blocked by a baseline defect, document the
exact unchanged blocker separately from the focused task validation.

##### Scope guard

Do not:

- change Shopify uninstall ingress;
- purge BullMQ globally;
- reactivate shops;
- redesign Subscription status;
- change credits/refunds/billing-period rollover;
- blanket-disable legitimate pre-uninstall usage publication;
- modify another repository.

Return the same task to `review` after the corrections.
