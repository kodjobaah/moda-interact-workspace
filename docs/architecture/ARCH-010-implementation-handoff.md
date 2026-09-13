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

The current coordinated ARCH-010 state after SHOPIFY-018 Attempt 3 acceptance is:

```text
all ARCH-010 task files: 81
complete:                 38
ready:                     3
pending:                  33
superseded:                7
```

There is no active `in_progress` or `review` ARCH-010 task in this snapshot.

### Ready frontier

```text
ARCH-010-ADMIN-010
ARCH-010-BACKGROUND-008
ARCH-010-BACKGROUND-009
<<<<<<< HEAD
=======
ARCH-010-SHOPIFY-018
>>>>>>> main
```

These tasks are independently executable according to their own dependencies. Do not serialize them merely because they share ARCH-010.

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

`BACKGROUND-002` is architect-accepted Complete at Attempt 3 (`97bf5f0`) and owns the concurrency-safe current-period Paid included-credit reservation primitive. `BACKGROUND-014` is architect-accepted Complete at Attempt 2 (`2104959`) and makes purchased reservations FIFO lot-aware. `BACKGROUND-019` is architect-accepted Complete at Attempt 6 (`08c288f`, final parent evidence `7fd5e1e`) and owns the final promotion-first routing plus exact promotional-grant reservation. Its completion releases `BACKGROUND-008` and `BACKGROUND-009` to Ready.

For Shopify, `SHOPIFY-023` is architect-accepted Complete at Attempt 1 (`01f0605`) after developer-run validation against the materialized DATABASE-013 submodule. `SHOPIFY-018` is architect-accepted Complete at Attempt 3 (`9ce3dfa`; production lifecycle implementation introduced at `1605a3c`; final parent report HEAD `e13673a`). Its enabled downstream tasks remain gated by other incomplete dependencies. SHOPIFY-003 and SHOPIFY-009 also remain gated by their other incomplete dependencies.

`BACKGROUND-015` is architect-accepted Complete at Attempt 4 (`29c791c`). The Partner reconciliation snapshot now uses one request for live subscription plus the latest validated lifecycle event. `BACKGROUND-012` remains Pending because BACKGROUND-007, BACKGROUND-009 and BACKGROUND-010 are still incomplete.

`BACKGROUND-019` Attempt 4 is Ready with an explicit upstream dependency-release step: the `moda-interact-background/database` gitlink must advance to the architect-accepted DATABASE-013 revision `014408e0402221f08a3961880b34e828a8bdc736`. This is a consumer gitlink release only; database source must remain unchanged. Shared `0.11.0` is already consumed and BACKGROUND-002/011/014 are same-repository accepted prerequisites, so they require no additional release action.

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
`ARCH-010-SHOPIFY-018` Attempt 2 is Changes Requested (narrow proof/workflow correction). Production `1605a3c` and test commit `dbfb9fc` remain the current candidates. Attempt 3 must add only the missing query-shape/parser/no-write assertions and exact VCS synchronization/report metadata unless a new test exposes a production defect. No downstream Shopify task is released until SHOPIFY-018 is architect-accepted Complete.

`ARCH-010-BACKGROUND-019` is architect-accepted Complete at Attempt 6. Accepted implementation branch HEAD: `08c288f`; final parent publication evidence reconciled from the developer handoff: `7fd5e1e`. The accepted DATABASE-013 checkout remains validation-only and the Background database gitlink is unchanged. `ARCH-010-BACKGROUND-008` and `ARCH-010-BACKGROUND-009` are now Ready because all of their dependencies are Complete. `ARCH-010-BACKGROUND-007` remains Pending until BG8 and BG9 are Complete; ARCH-010 system tests remain terminal/manual-gated.
