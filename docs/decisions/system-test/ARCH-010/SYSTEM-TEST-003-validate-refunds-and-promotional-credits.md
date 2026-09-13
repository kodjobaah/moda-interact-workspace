---
id: ARCH-010-SYSTEM-TEST-003
architecture_id: ARCH-010
title: Validate purchased-credit refund lifecycle and opt-in promotional campaigns
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: manual
status: pending
priority: 102
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-014
- ARCH-010-BACKGROUND-021
- ARCH-010-BACKGROUND-022
- ARCH-010-BACKGROUND-019
- ARCH-010-SHOPIFY-025
- ARCH-010-SHOPIFY-026
- ARCH-010-ADMIN-003
- ARCH-010-ADMIN-005
- ARCH-010-ADMIN-006
- ARCH-010-SHOPIFY-020
- ARCH-010-SHOPIFY-021
- ARCH-010-SHOPIFY-022
enables:
- ARCH-010-SYSTEM-TEST-004
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-SYSTEM-TEST-003: Validate purchased-credit refund lifecycle and opt-in promotional campaigns

## Terminal/manual gate

Do **not** auto-start. The developer explicitly invokes this terminal/manual validation only after all dependencies are integrated and manually smoke-checked. No implementation task depends on this task.

## Objective

Validate end to end:

1. canonical `RecoveryCreditPurchase` lifecycle and immutable purchase monetary provenance;
2. FIFO allocation across multiple independent purchase lots;
3. self-service merchant refund **requests** for one or more ACTIVE purchase lots without self-service provider money movement;
4. reservation-vs-refund and reactivation-vs-Admin concurrency;
5. whole-remaining human/provider settlement;
6. dedicated merchant purchase/refund history UI;
7. optional GLOBAL/PLAN/SHOP promotional campaigns and promo-first consumption.

## Purchased-credit lifecycle scenarios

At minimum validate:

1. top-up starts as `REQUESTED`, `currentAmount=0`, `reservedAmount=0` and is non-spendable;
2. exact provider after quantity/cost/currency activates purchase exactly once and freezes immutable original amount/currency/provenance;
3. current/later plan or top-up-price change does not modify historical purchase value;
4. ACTIVE purchase begins with `currentAmount=creditsGranted`;
5. successful reservation commit decrements `currentAmount` and `reservedAmount` by one;
6. failed/released reservation decrements only `reservedAmount`;
7. final successful consumption transitions ACTIVE -> COMPLETED with zero current/reserved;
8. COMPLETED cannot be refunded/reactivated;
9. REFUNDED cannot be spent/refunded/reactivated.

## Multiple purchase lots / FIFO

Create at least four purchases with deterministic age and mixed states.

Prove:

1. new reservations consume only ACTIVE lots in original FIFO order;
2. WITHDRAWN/REQUESTED/COMPLETED/REFUNDED lots are skipped;
3. withdrawing one lot does not freeze another ACTIVE lot;
4. reactivating an old lot restores it to its original FIFO position, not newest position;
5. exact UsageReservation always remains bound to the purchase that funded it;
6. aggregate purchased counter remains conserved across all lots.

## Merchant refund request scenarios

Use the dedicated purchase-management UI/API.

Prove:

1. merchant can view Active, Refund pending, Completed, Refunded and All/history;
2. REQUESTED purchase is visible but non-selectable;
3. ACTIVE purchase with `availableAmount > 0` is selectable;
4. ACTIVE purchase with `availableAmount = 0` is disabled/non-selectable;
5. no quantity/percentage/refund-money input exists;
6. selecting one ACTIVE purchase creates one refund request and transitions only that purchase to WITHDRAWN;
7. selecting multiple ACTIVE purchases processes each independently;
8. one failed lot in a multi-select batch does not roll back another successful lot;
9. cross-shop purchase IDs cannot be viewed/mutated;
10. request-time snapshots record the fresh winning current/reserved/available values;
11. request immediately removes only that purchase from new FIFO allocation;
12. request creates no provider refund/API action.

## Reservation-vs-refund races

Use real PostgreSQL concurrency/two independent clients or an equivalent integrated harness. Do not fake the core race using only mocks.

### One available credit

Start:

```text
current=1 reserved=0 ACTIVE
```

Run reservation and refund concurrently.

Prove both legal outcomes:

**reservation wins**

```text
reserved=1
refund retry -> available=0 -> REFUND_NOT_AVAILABLE
purchase remains ACTIVE
```

**refund wins**

```text
purchase -> WITHDRAWN
reservation retry cannot use that lot and may move to next ACTIVE FIFO lot
```

No double-spend/negative balance.

### Two available credits

Start:

```text
current=2 reserved=0 ACTIVE
```

Let one conversation reserve first. Refund retry must see fresh:

```text
current=2 reserved=1 available=1
```

and may transition to WITHDRAWN. UI must report fresh 1 currently refundable + 1 in progress rather than stale 2.

## Existing reservation settlement after withdrawal

Prove:

1. new reservations cannot use WITHDRAWN lot;
2. pre-existing exact reservation can commit while lot is WITHDRAWN;
3. commit decrements lot current+reserved and aggregate reserved/increments committed;
4. pre-existing exact reservation can release while lot is WITHDRAWN;
5. release decrements lot/aggregate reserved and increments aggregate refunding for the returned held credit;
6. ambiguous reservation prevents provider settlement while still reserved;
7. if every pre-existing reservation commits and current reaches 0, purchase becomes COMPLETED and refund closes with no provider action;
8. if releases leave credits and reserved reaches 0, final refund quantity equals then-current `currentAmount`, which may exceed request-time available snapshot.

## Merchant reactivation

While purchase is WITHDRAWN and refund status is REQUESTED:

1. merchant sees Reactivate;
2. reactivation atomically releases exactly `currentAmount-reservedAmount` from aggregate refunding;
3. purchase returns ACTIVE without changing current/reserved/purchase age;
4. refund becomes terminal CANCELLED history;
5. a later new refund request can be created after further consumption;
6. provider-action-required/needs-attention state disables reactivation.

## Reactivation vs Admin provider lock race

Run merchant reactivation and SUPER_ADMIN provider-action lock concurrently against the same refund.

Exactly one may win:

- merchant wins -> purchase ACTIVE, refund terminal CANCELLED, Admin cannot start provider action;
- Admin wins -> refund PROVIDER_ACTION_REQUIRED, purchase remains WITHDRAWN, merchant cannot reactivate.

No state may expose both spendable credits and a potentially-started provider refund.

## Provider settlement

With WITHDRAWN purchase and `reservedAmount=0,currentAmount>0`:

1. Admin final credit quantity is system-derived exactly from currentAmount;
2. Admin has no arbitrary quantity input;
3. expected provider amount is derived from immutable original purchase amount/currency, never current plan/top-up price;
4. changing current plan/rate after purchase does not change expected refund;
5. provider amount/currency mismatch cannot complete;
6. ambiguous provider action keeps purchase WITHDRAWN/held and blocks merchant reactivation;
7. successful completion sets purchase REFUNDED/current=0;
8. aggregate refunding and granted quantities decrease exactly by final refunded credits;
9. completed refund stores provider evidence and merchant completion message exactly once;
10. replay cannot double-refund/double-remove credits;
11. only one completed refund can exist for one purchase.

Include at least one non-divisible proportional money case to prove the deterministic currency-safe rounding policy without floating-point drift.

## Merchant UI history

Capture evidence that:

- Active rows show current/reserved/available;
- Refund pending rows show in-flight reservations and reactivation availability;
- Completed rows explain all credits used;
- Refunded rows show final refunded credits and actual persisted provider amount/currency;
- historical original purchase amount comes from immutable purchase provenance;
- no current-price cash estimate is fabricated;
- mixed multi-select results are presented per purchase.

## Promotion scenarios

Retain the promotional campaign scenarios from the existing ARCH-010 plan, including:

1. GLOBAL/PLAN/SHOP visibility and targeting;
2. explicit merchant selection before grant;
3. one still-usable selected promotion at a time;
4. promo consumed before all other capacity sources;
5. expiry/close/reopen semantics;
6. plan-target loss after plan change;
7. same merchant cannot claim same campaign twice;
8. concurrent promotion selection has one winner;
9. merchant/Admin history and reporting remain campaign-linked;
10. promotional usage creates no Shopify recovery/top-up App Event;
11. promotional/lifetime Free credits are never refundable;
12. FROZEN/NO_CONTRACT/inactive shop cannot spend promo;
13. no automatic paid overage exists.

## Evidence

Capture deterministic DB rows for:

```text
RecoveryCreditPurchase
RecoveryCreditRefund
UsageReservation
ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS)
relevant UsageEvents
promotion grant/campaign rows
```

Capture merchant/Admin UI evidence, provider-call evidence/absence and concurrency outcomes. Never expose secrets.

## Non-goals

Do not implement missing behaviour from this task. Defects return to `moda_architect` for routing to the owning implementation task.

## Stop conditions

STOP if any implementation dependency is not Complete, if live provider evidence cannot safely prove the requested scenario, or if system testing would require changing production code rather than filing a defect.

## Completion Report

### Status
Not started/manual-gated.

### Validation Results
Populate when explicitly invoked.

### Architect Review
Pending.
