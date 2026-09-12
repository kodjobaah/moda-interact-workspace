---
id: ARCH-010-BACKGROUND-013
architecture_id: ARCH-010
title: Stop shop business execution after the Shopify contract ends
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
- ARCH-010-BACKGROUND-017
- ARCH-010-SHOPIFY-016
- ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-BACKGROUND-013: Stop shop business execution after the Shopify contract ends

## Objective

Extend the existing ARCH-010 shop-execution gates so an installed shop with `Subscription.status=NO_CONTRACT` cannot perform new Moda business execution after effective Shopify cancellation.

This is stronger than recovery-capacity exhaustion. Capacity exhaustion blocks only new recovery initiation; contract absence blocks all new business execution for the shop.

## Product invariants

1. `Shop.status=ACTIVE` means the app is installed; it does not prove a valid Shopify billing contract.
2. Business execution requires both:

```text
Shop.status = ACTIVE
AND
Subscription.status is an accepted executable current-contract state
```

3. A `NO_CONTRACT` merchant retains read/history/support/billing UI access in moda-interact but Background does not perform new merchant business actions.
4. Existing purchased/lifetime balances remain durable but non-spendable until a new Shopify contract is verified.
5. Historical/provider bookkeeping that completes already-committed pre-cancellation work may continue when it has no new customer-facing side effect.
6. No inbound/customer message after effective cancellation may create a new CommerceAgent response.
7. No queued Shopify event after effective cancellation may create a new recovery candidate/recovery/conversation/send.
8. Do not purge whole Redis queues.

## Inspect before editing

At minimum inspect:

```text
src/workers/whatsapp.worker.ts
src/services/conversation-turn-processor.service.ts
src/services/recovery-routing.service.ts
src/services/checkout-recovery.service.ts
src/services/pending-recovery-candidate.service.ts
src/services/effective-billing-policy.service.ts
src/services/recovery-billing.service.ts
ARCH-010 shop-status gate implementation from BACKGROUND-004/BACKGROUND-005
relevant Shopify-event worker entrypoints
provider-status / usage-publisher bookkeeping paths
```

Reuse/extend the accepted ARCH-010 execution-gate abstraction if BACKGROUND-004/BACKGROUND-005 introduced one. Do not create a second competing generic gate.

## Executable contract states

Use final project enum values. At minimum:

```text
ACTIVE   -> eligible subject to plan/capacity policy
TRIALING -> only if ARCH-010 already permits that exact plan state
NO_CONTRACT -> business execution denied
UNMAPPED    -> business execution denied
SYNC_ERROR  -> business execution denied where existing policy fails closed
```

Do not weaken existing fail-closed policy.

## WhatsApp inbound gate

After existing routing has resolved a durable `shopId`, but BEFORE mutating conversation business state:

```text
resolve ownership
  -> load current Shop + Subscription execution eligibility
  -> not executable: terminal no-op
  -> executable: continue existing receive/enqueue behavior
```

For NO_CONTRACT specifically, do not:

- append inbound customer message to the business conversation;
- create standalone/product conversation state;
- enqueue `process-conversation-turn`;
- invoke CommerceAgent;
- reserve recovery capacity;
- send outbound WhatsApp.

Also re-check eligibility immediately before processing an already-queued `process-conversation-turn`, because the contract can end after the inbound message was accepted but before the turn executes.

## Shopify/recovery queued-work gate

For queued Shopify/background business work whose durable shop can be identified, stop before creating new business state when the current subscription is NO_CONTRACT.

At minimum prevent post-cancellation creation/initiation of:

- pending recovery candidates;
- newly materialized CheckoutRecovery rows;
- recovery conversations;
- outbound recovery messages;
- CommerceAgent work;
- new billing reservations/usage.

A job that becomes ineligible solely because the contract ended should complete as a terminal no-op, not retry forever.

## Historical bookkeeping exception

Allow only bounded bookkeeping for work whose irreversible business action occurred before effective cancellation, for example:

- Meta delivery/read/failure status for an already-sent message;
- publication/reconciliation of an App Event that was durably committed while the provider contract/cycle was valid, subject to existing billing-cycle rules;
- terminal order/completion bookkeeping for an already-existing recovery when it creates no new outbound side effect.

Do not use this exception to create a new recovery, new conversation turn or new send.

## Capacity-blocked recovery interaction

A recovery with `admissionBlockReason=RECOVERY_CAPACITY_EXHAUSTED` must not be resumed merely because capacity later exists if the shop is now NO_CONTRACT.

BACKGROUND-009 resume processing must re-check contract execution eligibility before normal re-admission.

Do not relabel contract absence as capacity exhaustion.

## Required tests

At minimum prove:

1. Shop ACTIVE + Subscription ACTIVE continues normal execution;
2. Shop ACTIVE + Subscription NO_CONTRACT blocks new pending recovery scheduling;
3. NO_CONTRACT blocks matured candidate materialization before new recovery creation;
4. NO_CONTRACT blocks inbound WhatsApp before conversation message append;
5. NO_CONTRACT blocks standalone/product conversation creation;
6. NO_CONTRACT blocks already-queued conversation-turn processing on re-check;
7. NO_CONTRACT never invokes CommerceAgent;
8. NO_CONTRACT never sends new WhatsApp;
9. NO_CONTRACT never reserves/commits a recovery credit;
10. NO_CONTRACT does not create a capacity-exhaustion SYSTEM message;
11. provider-status bookkeeping for pre-cancellation outbound messages still works;
12. safe terminal bookkeeping for existing recoveries remains possible without outbound side effects;
13. capacity-resume worker skips NO_CONTRACT shops;
14. stale queued jobs become successful terminal no-ops, not retry storms;
15. UNINSTALLED shop behavior from BACKGROUND-004/005 remains unchanged;
16. active-contract credit exhaustion behavior from BACKGROUND-009 remains unchanged.

## Non-goals

Do not implement merchant UI, Shopify cancellation detection, resubscription, refunds, shop identification redesign or queue-wide purge.

## Stop conditions

Stop and return to `moda_architect` if safe contract eligibility cannot be checked after shop ownership is known without moving tenant identification into WhatsApp ingress or Shopify HTTP ingress.


## FROZEN-state coexistence

This task remains owner of NO_CONTRACT execution blocking. FROZEN is a separate provider lifecycle reason owned by BACKGROUND-017. Shared gate helpers may be refactored for reuse, but do not collapse FROZEN into NO_CONTRACT because restoration/cancellation semantics differ.


## Final promotional balance rule under NO_CONTRACT

Preserved campaign-linked `PromotionalCreditGrant` capacity does not authorise business work while Subscription is `NO_CONTRACT`. Preserve campaign/grant/selection history without consuming it until a verified executable contract exists again.

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
