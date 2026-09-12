---
id: ARCH-010-BACKGROUND-013
architecture_id: ARCH-010
title: Enforce NO_CONTRACT and FROZEN business-execution gates
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 59
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-BACKGROUND-004
  - ARCH-010-BACKGROUND-005
  - ARCH-010-BACKGROUND-012
enables:
  - ARCH-010-SHOPIFY-016
  - ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: 2026-09-12
---

# ARCH-010-BACKGROUND-013: Enforce NO_CONTRACT and FROZEN business-execution gates

## Consolidation

This task is the active owner of the work previously split between `ARCH-010-BACKGROUND-013` and `ARCH-010-BACKGROUND-017`.

`ARCH-010-BACKGROUND-017` is superseded and MUST NOT be implemented separately.

The merge is intentional because both states must be enforced by the same shop/subscription execution-policy boundary across the same recovery, WhatsApp, CommerceAgent and billing paths. They remain **distinct reasons** with different restoration semantics; they are combined only so one implementation cannot accidentally gate one path for NO_CONTRACT but forget the same path for FROZEN.

## Objective

Extend the accepted shop-execution gate from BACKGROUND-004/005 so all new Moda business execution requires:

```text
Shop.status = ACTIVE
AND Subscription.status is executable
```

For ARCH-010 first production:

```text
ACTIVE   -> executable subject to plan/capacity policy
TRIALING -> executable only where existing policy already permits
NO_CONTRACT -> deny with CONTRACT_REQUIRED / canonical equivalent
FROZEN      -> deny with SUBSCRIPTION_FROZEN
UNMAPPED/SYNC_ERROR -> preserve existing fail-closed behaviour
UNINSTALLED/inactive Shop -> preserve BACKGROUND-004/005 behaviour
```

`NO_CONTRACT`, `FROZEN`, capacity exhaustion and uninstall MUST remain distinguishable.

## Inspect before editing

Inspect and reuse the existing accepted gate rather than creating a second generic mechanism:

```text
src/services/effective-billing-policy.service.ts
src/services/checkout-recovery.service.ts
src/services/recovery-routing.service.ts
src/services/pending-recovery-candidate.service.ts
src/services/recovery-billing.service.ts
src/services/conversation-turn-processor.service.ts
src/services/conversation.service.ts
src/services/conversation.message.service.ts
src/services/inbound-whatsapp-abuse-admission.service.ts
src/services/outbound-whatsapp-admission.service.ts
src/services/shopify-usage-event-publisher.service.ts
src/workers/whatsapp.worker.ts
src/workers/pending-recovery-candidate.worker.ts
src/workers/checkout.worker.ts
src/workers/orders.worker.ts
```

Inspect focused tests for those paths, especially existing BACKGROUND-004/005 gate tests and:

```text
tests/unit/services/effective-billing-policy.service.test.ts
tests/unit/services/checkout-recovery.service.test.ts
tests/unit/services/recovery-routing.service.test.ts
tests/unit/services/pending-recovery-candidate.service.test.ts
tests/unit/services/conversation-turn-processor.service.test.ts
tests/unit/services/outbound-whatsapp-admission.service.test.ts
tests/unit/services/shopify-usage-event-publisher.service.test.ts
tests/unit/workers/pending-recovery-candidate.worker.test.ts
tests/unit/workers/whatsapp.worker.test.ts
```

## Single execution-policy rule

After a worker/service has resolved durable `shopId`, but before it performs an irreversible new business action, evaluate current Shop + Subscription execution state through the canonical reusable gate.

Do not query Shopify Partner API from this gate.

Do not move this gate into Shopify or Meta HTTP ingress merely to reject traffic early.

## Behaviour matrix

| Durable state | New recovery/candidate | Inbound business mutation | CommerceAgent | New outbound WhatsApp | New credit reservation | New UsageEvent/top-up | Historical bookkeeping |
|---|---|---|---|---|---|---|---|
| ACTIVE/TRIALING executable | normal policy | allowed | allowed | allowed | normal policy | normal policy | allowed |
| NO_CONTRACT | DENY terminal no-op | DENY | DENY | DENY | DENY | DENY | bounded pre-contract-end finalisation only |
| FROZEN | DENY terminal no-op | DENY | DENY | DENY | DENY | DENY | bounded pre-freeze finalisation only |
| UNMAPPED/SYNC_ERROR | preserve existing fail-closed policy | preserve | preserve | preserve | preserve | preserve | safe bookkeeping only |
| Shop UNINSTALLED/inactive | preserve BACKGROUND-004/005 | preserve | preserve | preserve | preserve | preserve | existing rules |

A denied queued job caused only by NO_CONTRACT/FROZEN must complete as a successful terminal no-op where the queue contract permits. Do not create retry storms and do not purge entire Redis queues.

## WhatsApp/conversation boundary

After ownership resolves to shopId and before mutating business conversation state:

```text
resolve shop
  -> evaluate execution state
  -> denied: terminal no-op, no message append/turn enqueue
  -> allowed: continue existing flow
```

Re-check the gate immediately before processing an already queued `process-conversation-turn`, because lifecycle state can change after inbound acceptance.

When denied, do not:

- append a new inbound business message that advances the conversation;
- create standalone/product conversation state;
- invoke CommerceAgent/tools;
- enqueue a new business turn;
- reserve recovery capacity;
- send new automated WhatsApp.

## Recovery/event boundary

Before queued Shopify/recovery work creates or advances new business state, deny NO_CONTRACT/FROZEN shops.

At minimum prevent:

- new pending recovery candidates;
- candidate refresh that schedules future business execution;
- new CheckoutRecovery materialisation/business mutation;
- recovery-conversation initiation;
- new outbound recovery sends;
- new recovery billing reservation/commit;
- new top-up purchase UsageEvent;
- new recovery UsageEvent created after denial state is known.

`BACKGROUND-018` remains separate and owns the **earlier high-volume checkout/cart/order event gate** for FROZEN shops. Do not duplicate its hot-path filtering here.

## Distinct denial semantics

### NO_CONTRACT

Use a canonical reason equivalent to `CONTRACT_REQUIRED`. Do not emit capacity-exhausted system state.

Purchased, lifetime-Free and campaign-linked promotion capacity remain durable but non-spendable until a verified contract exists again.

### FROZEN

Use a canonical reason equivalent to `SUBSCRIPTION_FROZEN`.

Do not classify FROZEN as `NO_CONTRACT`, `RECOVERY_CAPACITY_EXHAUSTED`, `UNMAPPED_PLAN` or shop unavailability.

A successful BACKGROUND-012 unfreeze that restores Subscription ACTIVE/TRIALING automatically restores normal execution; no separate Shop status mutation is required.

## Historical/accounting exceptions

Allow only bounded finalisation of business actions irreversibly committed before the denial state became effective, for example:

- Meta delivery/read/failure status for an already-sent message;
- provider confirmation/reconciliation for a previously committed billing event when provider evidence is unambiguous;
- reservation completion/release required to keep accounting balanced;
- terminal order/completion bookkeeping for an already-existing recovery with no new customer-facing side effect.

For FROZEN, do not publish a **new** provider billing event for a business occurrence after the locally known freeze event time. Preserve the original event timestamp; never retimestamp a pre-freeze event into a later cycle to make it billable.

The exceptions MUST NOT create a new recovery, conversation turn, customer message or credit spend.

## Capacity-resume interaction

BACKGROUND-009 resume processing must re-check this execution gate before re-admitting a capacity-blocked recovery.

```text
capacity becomes available
  -> Subscription NO_CONTRACT/FROZEN? stop
  -> otherwise run normal re-admission
```

Do not relabel lifecycle denial as capacity exhaustion.

## Required tests

Prove all of the following:

1. ACTIVE executable subscription preserves normal business execution;
2. NO_CONTRACT blocks new pending recovery scheduling;
3. NO_CONTRACT blocks candidate materialisation before new recovery creation;
4. NO_CONTRACT blocks inbound conversation mutation before append;
5. NO_CONTRACT blocks already-queued conversation-turn processing on re-check;
6. NO_CONTRACT never invokes CommerceAgent, sends WhatsApp or reserves/commits credit;
7. NO_CONTRACT does not create a capacity-exhaustion SYSTEM message;
8. FROZEN returns a distinct SUBSCRIPTION_FROZEN policy result;
9. FROZEN blocks recovery even when credits remain;
10. FROZEN blocks promotional, included, purchased and lifetime-Free reservation paths;
11. FROZEN blocks inbound mutation, CommerceAgent and new outbound WhatsApp;
12. FROZEN blocks new top-up/recovery UsageEvent creation;
13. queued pre-freeze business work reaches a terminal no-op after freeze unless it qualifies for bounded accounting finalisation;
14. pre-existing Meta delivery-status bookkeeping remains allowed in both lifecycle-denial states;
15. reservation finalisation already past the irreversible point remains accounting-safe;
16. capacity-resume skips both NO_CONTRACT and FROZEN;
17. denied stale jobs do not retry forever;
18. UNINSTALLED/inactive behaviour from BACKGROUND-004/005 is unchanged;
19. active-contract RECOVERY_CAPACITY_EXHAUSTED behaviour remains narrower and unchanged;
20. successful unfreeze to ACTIVE/TRIALING restores normal paths without another shop-status mutation;
21. no Partner API call was added to the execution gate;
22. no Shopify/Meta HTTP-ingress lifecycle lookup was added;
23. BACKGROUND-018 remains the only task-owned FROZEN raw checkout/cart/order early gate.

## Non-goals

Do not implement provider lifecycle reconciliation, merchant UI, raw-event hot-path filtering, queue-wide purge, refunds, new shop-identification architecture or new queue contracts.

## Validation

Run focused policy/recovery/WhatsApp/conversation/usage tests for every changed path, then repository-declared test/typecheck/build commands and `git diff --check`. Do not invent scripts.

## Stop conditions

STOP and return to `moda_architect` if any shop-owned business path cannot establish durable shop identity before irreversible action without changing HTTP-ingress architecture.

STOP if implementing one lifecycle reason would require bypassing the existing accepted BACKGROUND-004/005 generic execution gate rather than extending/reusing it.

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
