---
id: ARCH-010-BACKGROUND-017
architecture_id: ARCH-010
title: Gate all shop business execution while the Shopify subscription is frozen
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-BACKGROUND-004
  - ARCH-010-BACKGROUND-005
  - ARCH-010-BACKGROUND-013
  - ARCH-010-BACKGROUND-016
enables:
  - ARCH-010-SHOPIFY-019
  - ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-BACKGROUND-017: Gate all shop business execution while the Shopify subscription is frozen

## Objective

Make `Subscription.status=FROZEN` an explicit Background execution gate across recovery, WhatsApp/conversation and billable business paths while preserving read/history/accounting finalization.

Do not model freeze as ordinary capacity exhaustion or as `Shop.status` inactivity.

## Inspect before editing

```text
src/services/effective-billing-policy.service.ts
src/services/checkout-recovery.service.ts
recovery scheduling/processing services
outbound WhatsApp admission/sending services
inbound WhatsApp/conversation/CommerceAgent processing services
billing usage/top-up publisher/reconciliation services
tests covering BACKGROUND-004, BACKGROUND-005 and BACKGROUND-013 gates
```

## Effective billing policy

Add an explicit failure reason equivalent to:

```text
SUBSCRIPTION_FROZEN
```

When the shop is ACTIVE but Subscription.status is FROZEN, this reason must be returned/thrown before plan features/counters can authorize business work.

Do not misclassify FROZEN as:

```text
NO_CONTRACT
UNMAPPED_PLAN
SHOP_UNAVAILABLE
RECOVERY_CAPACITY_EXHAUSTED
```

## Business execution that MUST stop

After a worker resolves ownership to a FROZEN shop, it must not create/start:

- new CheckoutRecovery business processing;
- delayed recovery execution;
- recovery-conversation initiation;
- inbound customer-message mutation that would advance CommerceAgent/business state;
- CommerceAgent invocation/tool execution;
- outbound automated WhatsApp/customer messages;
- new Free/Paid/purchased credit reservations;
- new top-up purchase App Events;
- new recovery usage App Events or other billable work created after freeze is known.

Queued work that reaches this gate after the freeze should end as a successful terminal no-op where the existing queue contract permits it. Do not retry forever and do not purge Redis as correctness.

## Historical/accounting exceptions

Freeze must not corrupt already-committed history.

Allowed bounded operations include:

- Meta delivery/read/failure status updates for a message sent before freeze;
- local completion/release of a reservation whose business action had already crossed its irreversible point before freeze, according to existing idempotent accounting rules;
- reconciliation/storage of provider lifecycle evidence;
- provider confirmation of previously submitted events where provider evidence is unambiguous.

These exceptions must never send a new customer-facing message or create a new recovery.

## Usage publication guard

Do not publish a new provider billing event for business work whose committed occurrence is after the locally known freeze event time.

For a pre-freeze committed UsageEvent, follow BACKGROUND-016's same-cycle/period-closed rules. Never mutate its occurrence timestamp to make Shopify accept it.

## Shopify raw-event boundary

`ARCH-010-BACKGROUND-018` owns the earlier high-volume Shopify checkout/cart event gate. Do not duplicate its worker-level event filtering here. This task remains authoritative for downstream recovery, WhatsApp, CommerceAgent, reservation and billable-business execution after ownership/business context is resolved.

The order-completion safety bookkeeping permitted by BACKGROUND-018 is not permission to send or initiate customer work while frozen.

## Required tests

At minimum prove:

1. EffectiveBillingPolicyResolver returns SUBSCRIPTION_FROZEN distinctly;
2. FROZEN blocks new recovery admission even when credits remain;
3. FROZEN blocks purchased-credit reservation;
4. FROZEN blocks lifetime Free reservation;
5. FROZEN blocks paid included reservation;
6. FROZEN blocks new outbound WhatsApp;
7. FROZEN blocks CommerceAgent processing;
8. FROZEN blocks inbound business-state mutation after ownership resolution;
9. queued pre-freeze recovery work becomes a terminal no-op after freeze;
10. Meta delivery-status bookkeeping for pre-freeze outbound remains allowed;
11. no new billable UsageEvent is created after freeze is known;
12. NO_CONTRACT and UNINSTALLED existing gates remain unchanged;
13. capacity exhaustion behaviour remains narrower than freeze;
14. unfreeze automatically permits normal paths again once Subscription is ACTIVE/TRIALING without requiring a separate shop-status mutation.

## Non-goals

No provider API query, no UI, no queue schema, no cancellation transition, no credit reset/refund and no shop-identification redesign.

## Validation

Run focused billing policy/recovery/WhatsApp tests plus repository-declared build/typecheck/full tests and `git diff --check`.

## Stop conditions

STOP if a shop-owned business path cannot establish shop identity before irreversible customer/provider business action. Report that path to `moda_architect`; do not weaken the frozen gate or invent ARCH-010 shop-identification changes.

## Completion Report

### Status
Not started.
