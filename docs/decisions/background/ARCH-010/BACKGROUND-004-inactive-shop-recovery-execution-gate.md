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
status: ready
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-010-BACKGROUND-006
  - ARCH-010-BACKGROUND-013
  - ARCH-010-BACKGROUND-017
  - ARCH-010-BACKGROUND-018
  - ARCH-010-SHOPIFY-005
created: 2026-09-11
updated: 2026-09-11
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
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
