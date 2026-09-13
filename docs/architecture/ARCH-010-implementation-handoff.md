# ARCH-010 Implementation Handoff

Date: 2026-09-13
Coordinator: `moda_architect`

## Current architecture state

ARCH-010 is **Agreed / In Progress** and is the clean **first-production baseline** for Moda Interact billing, merchant lifecycle and recovery capacity.

Read in this order before implementing any ARCH-010 task:

1. [`ARCH-010-first-production-baseline.md`](ARCH-010-first-production-baseline.md)
2. [`ARCH-010-merchant-lifecycle-state-transitions.md`](ARCH-010-merchant-lifecycle-state-transitions.md)
3. [`ARCH-010-promotional-campaigns.md`](ARCH-010-promotional-campaigns.md)
4. [`ARCH-010-supersession-map.md`](ARCH-010-supersession-map.md)
5. the exact assigned `docs/decisions/<domain>/ARCH-010/<TASK>.md`

The exact task file is the implementation contract. Do not implement from this handoff alone.

## Rollout classification

```text
PRE-PRODUCTION / BREAKING ROLLOUT
```

There is no production billing state requiring compatibility with intermediate development schemas/contracts. DATABASE-013 is the canonical first-production database baseline; future architectures migrate forward from it normally.

## Current audited task state

The current coordinated ARCH-010 state after BACKGROUND-006 Attempt 1 Changes Requested, with dependency readiness recomputed from the authoritative task files in this review snapshot, is:

```text
all ARCH-010 task files: 86
complete:                 50
ready:                     4
pending:                  24
superseded:                8
```

There is no active `in_progress` or `review` ARCH-010 task in this snapshot after the architect review is applied.

### Ready frontier

```text
ARCH-010-BACKGROUND-006
ARCH-010-BACKGROUND-010
ARCH-010-SHOPIFY-003
ARCH-010-SHOPIFY-022
```

These tasks are independently executable according to their own dependencies. BACKGROUND-006 is Ready only for its architect-requested Attempt-2 corrections; its dependants remain gated until it is architect-accepted Complete.

## Accepted-history reconciliation

Two completed tasks must retain their actual durable architect review history:

```text
ARCH-010-BACKGROUND-001
  Accepted Complete — Attempt 6
  implementation: 3b00b0777b1820a99644f85226bfebb927f7630b
  final parent publication evidence: c56c222

ARCH-010-SHOPIFY-002
  Accepted Complete — Attempt 8
  implementation head: 679a829
  final parent publication evidence: 1849cbb
```

Do not reset either task to an earlier attempt or reopen it for first-production cleanup. The baseline rule is to preserve completed history and put compatibility correction into later Pending/Ready tasks.

For Background, `BACKGROUND-011` is now Complete at accepted Attempt 4 and owns the narrow DATABASE-013 lifetime-counter conformance required by the accepted BACKGROUND-001 activation producer; its BullMQ/retry/CAS/onboarding semantics remain immutable.

`BACKGROUND-002` is architect-accepted Complete at Attempt 3 (`97bf5f0`) and owns the concurrency-safe current-period Paid included-credit reservation primitive. `BACKGROUND-014` is architect-accepted Complete at Attempt 2 (`2104959`) and makes purchased reservations FIFO lot-aware. `BACKGROUND-019` is architect-accepted Complete at Attempt 6 (`08c288f`, final parent evidence `7fd5e1e`) and owns the final promotion-first routing plus exact promotional-grant reservation. `BACKGROUND-008` is architect-accepted Complete at Attempt 3 (`b4ef7c8`, parent report `a8852ad`). `BACKGROUND-009` remains independently executable/reviewable; `BACKGROUND-007` remains gated until BG9 is Complete.

For Shopify, `SHOPIFY-023` is architect-accepted Complete at Attempt 1 (`01f0605`) after developer-run validation against the materialized DATABASE-013 submodule. `SHOPIFY-018` is architect-accepted Complete at Attempt 3 (`9ce3dfa`; production lifecycle implementation introduced at `1605a3c`; final parent report HEAD `e13673a`). Its enabled downstream tasks remain gated by other incomplete dependencies. SHOPIFY-003 and SHOPIFY-009 also remain gated by their other incomplete dependencies.

`BACKGROUND-015` is architect-accepted Complete at Attempt 4 (`29c791c`). The Partner reconciliation snapshot now uses one request for live subscription plus the latest validated lifecycle event. `BACKGROUND-012` remains Pending because BACKGROUND-007, BACKGROUND-009 and BACKGROUND-010 are still incomplete.

`ADMIN-006` is architect-accepted Complete at Attempt 2 (`b0332e5`; parent Completion Report `bbe6647`). Campaign reporting now exposes exact grant-lot merchant history with bounded/filterable pagination and read-only SUPER_ADMIN presentation. This acceptance does not release `SYSTEM-TEST-003`, which remains manual-gated behind its other incomplete dependencies.

## Luna-oriented task consolidation

The current repository/task audit found five safe merges. Only still-unimplemented tasks are merged.

```text
BACKGROUND-016 -> BACKGROUND-012
  freeze/unfreeze reconciliation is absorbed into the same canonical
  subscription reconciliation state machine as cancellation.

BACKGROUND-017 -> BACKGROUND-013
  FROZEN execution gating is absorbed into the same reusable execution-policy
  boundary as NO_CONTRACT while preserving distinct denial reasons.

SHOPIFY-010 -> SHOPIFY-014
  top-up server adapter + TopUpPurchasePanel become one merchant top-up capability.

SHOPIFY-011 -> SHOPIFY-015
  hosted plan-change select/return + SubscriptionChangePanel become one app-owned
  merchant plan-management capability.

SHOPIFY-019 -> SHOPIFY-016
  scheduled cancellation, effective NO_CONTRACT and FROZEN merchant restriction
  presentation/action guards become one explicit state matrix.
```

The absorbed task files remain in the repository with `status: superseded` and a `superseded_by` pointer. They MUST NOT be claimed.

### Tasks deliberately NOT merged

Do not merge these boundaries:

- `BACKGROUND-015` provider snapshot vs `BACKGROUND-012` lifecycle state machine;
- `BACKGROUND-018` high-volume FROZEN Shopify-event early gate vs `BACKGROUND-013` general business-execution gate;
- `BACKGROUND-002/011/014/019` capacity sources, because their locking/accounting invariants differ;
- `SHOPIFY-004` paid-period presentation vs `SHOPIFY-007` cycle-phase/App-Event mutation guard;
- `SHOPIFY-020` promotion capacity presentation vs `SHOPIFY-021` campaign catalogue/selection;
- system tests vs any implementation task.

This keeps each surviving task bounded enough for GPT-5.6 Luna while avoiding artificial component/server or lifecycle-state fragmentation.

## High-volume Shopify boundary

The platform target remains approximately **22,000 Shopify webhook events/minute**. ARCH-010 must not move business/lifecycle filtering into the Shopify HTTP webhook path.

```text
Shopify HTTP ingress
  authenticate
  validate/minimally normalise
  deterministic identity
  durable enqueue
  ACK

Background
  dequeue
  minimal early state checks
  discard/no-op common irrelevant path
  perform expensive action path only when required
```

`BACKGROUND-018` remains intentionally separate because it modifies this high-volume queued-event hot path. It must not add Partner API calls or unnecessary database/Redis work per event.

## Database and Shared baseline

Already Complete:

```text
DATABASE-013   one clean first-production Prisma schema + empty-db baseline migration
BACKGROUND-020 remove live Background consumers of deleted Shared compatibility names
SHOPIFY-024    remove live Shopify consumers of deleted Shared compatibility names
SHARED-007     remove obsolete pre-production Shared contracts
SHARED-008     publish clean first-production Shared contract
```

Do not recreate removed compatibility concepts locally.

Canonical lifetime entitlement:

```text
LIFETIME_FREE_RECOVERY_CREDITS
```

Removed from first production include:

```text
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment
FREE_RECOVERY_LIFETIME
ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)
MIGRATION_RECONCILED
SubscriptionCancellationRequest / local cancellation executor
RecoveryCreditPurchaseStatus.REFUNDED
negative-App-Event refund correction
campaign-less promotional grants
BILLING_FREE_ALLOWANCE_EXHAUSTED
BILLING_PLAN_CHANGE_ACTION_REQUIRED
```

## Canonical capacity order

```text
FREE
  selected usable campaign PromotionalCreditGrant
  -> PURCHASED_RECOVERY_CREDITS
  -> LIFETIME_FREE_RECOVERY_CREDITS
  -> BLOCK NEW RECOVERY ADMISSION

PAID
  selected usable campaign PromotionalCreditGrant
  -> current BillingPeriod INCLUDED_RECOVERY_CREDITS
  -> PURCHASED_RECOVERY_CREDITS
  -> LIFETIME_FREE_RECOVERY_CREDITS
  -> BLOCK NEW RECOVERY ADMISSION
```

No automatic Paid overage exists.

## Subscription plan-change boundary

Merchant upgrade/downgrade is Shopify-hosted and Shopify-authoritative:

```text
SHOPIFY-015
  merchant interaction + hosted selection + synchronous provider verification
  -> persist/schedule safe current/pending projection only

BACKGROUND-010
  effective provider-confirmed plan transition
  -> close/open BillingPeriod and grant/forfeit period entitlement exactly once
```

The app callback never grants plan capacity or performs local subscription creation.

## Lifecycle boundary after consolidation

```text
BACKGROUND-015
  live subscription + latest lifecycle snapshot
        ↓
BACKGROUND-012
  one deterministic lifecycle reconciliation state machine:
  pending plan / scheduled cancellation / CANCELED / FROZEN / UNFROZEN / ambiguity
        ↓
BACKGROUND-013
  reusable business-execution gate:
  NO_CONTRACT vs FROZEN distinct reasons
        ↓
BACKGROUND-018
  separate 22k/min-sensitive early checkout/cart/order FROZEN gate
```

## System-test rule

All ARCH-010 system-test tasks remain terminal/manual-gated. No implementation/publication/infrastructure task depends on them.

Do not auto-start system tests when dependencies become Complete. The developer may manually inspect the integrated product first and explicitly invoke system tests afterwards.

## Agent execution rule

For every Ready task, the repository agent must:

1. re-read the exact task file;
2. claim the same task through the normal workflow;
3. edit only the stated repository/scope;
4. implement every numbered invariant/test rather than approximating the objective;
5. use actual `package.json` scripts rather than inventing validation commands;
6. stop on any task STOP condition and return the exact mismatch to `moda_architect`;
7. return to review and STOP after the task's validation/completion report.

If a clean-baseline symbol is missing, do not recreate a legacy alias locally. Return the contract gap to the architect.




`ARCH-010-SHOPIFY-018` is architect-accepted Complete at Attempt 3. Accepted task branch HEAD: `9ce3dfa`; production lifecycle implementation introduced at `1605a3c`; final parent report HEAD reconciled from the developer handoff: `e13673a`. No enabled downstream Shopify task becomes Ready yet because each still has other incomplete dependencies.
`ARCH-010-BACKGROUND-019` is architect-accepted Complete at Attempt 6. Accepted implementation branch HEAD: `08c288f`; final parent publication evidence reconciled from the developer handoff: `7fd5e1e`. The accepted DATABASE-013 checkout remains validation-only and the Background database gitlink is unchanged. `ARCH-010-BACKGROUND-008` is now architect-accepted Complete at Attempt 3 (`b4ef7c8`; parent report `a8852ad`). `ARCH-010-BACKGROUND-009` remains the remaining Background frontier dependency for `ARCH-010-BACKGROUND-007`, so BG7 stays Pending; ARCH-010 system tests remain terminal/manual-gated.

## Recovery-credit purchase lifecycle/refund correction — 2026-09-13

Current first-production rule:

```text
RecoveryCreditPurchase.status = REQUESTED | ACTIVE | COMPLETED | WITHDRAWN | REFUNDED
ACTIVE availableAmount = currentAmount - reservedAmount
```

Each purchase is independent. Merchant refund request uses versioned CAS to transition only an eligible ACTIVE purchase to WITHDRAWN; no quantity is supplied by the browser. Existing reservations continue to settle, and provider action waits for `reservedAmount=0`. Merchant reactivation is allowed only while the exact refund remains pre-provider-action.

Forward tasks:

```text
DATABASE-014   canonical purchase lifecycle/balances + immutable commercial provenance
BACKGROUND-021 provider-confirmed purchase valuation and REQUESTED -> ACTIVE
BACKGROUND-022 final purchased-lot reservation/refund concurrency; must preserve accepted BACKGROUND-019 promo-first routing
SHOPIFY-025    purchase history + per-purchase/batch refund/reactivation server actions
SHOPIFY-026    dedicated purchase/refund-management UI
ADMIN-002/003  human triage + provider settlement against exact purchase evidence
SYSTEM-TEST-003 terminal integrated refund/multi-purchase validation
```

`SHOPIFY-017` is superseded. DATABASE-007, BACKGROUND-014, BACKGROUND-019 and SHOPIFY-018 remain immutable accepted history and are not edited by this correction.
