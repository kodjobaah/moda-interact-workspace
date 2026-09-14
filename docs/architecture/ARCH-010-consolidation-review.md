# ARCH-010 Final Consolidation / Architect Review

Date: 2026-09-12
Coordinator: `moda_architect`

## Overall decision

**ARCH-010 remains Agreed / In Progress.** It is the first-production billing/lifecycle baseline and is not yet Implemented.

```text
no production billing data
  -> PRE-PRODUCTION / BREAKING ROLLOUT
  -> one clean database + Shared/runtime model
  -> future architectures migrate forward from that baseline
```

The binding schema/runtime baseline is [`ARCH-010-first-production-baseline.md`](ARCH-010-first-production-baseline.md).

## Current workspace audit

The attached 2026-09-12 workspace contains 81 ARCH-010 task files. After restoring the durable architect-accepted histories for BACKGROUND-001 Attempt 6 and SHOPIFY-002 Attempt 8, and applying the safe pending-task consolidation described below:

```text
complete:    30
ready:        5
pending:     39
superseded:   7
```

Graph validation must remain based on individual task `depends_on` metadata. Superseded tasks are history only and are not execution prerequisites.

## Completed-history rule

Already-completed task implementation/review history is not reopened merely to merge task definitions. The five consolidation merges below affect only tasks that were still unimplemented in the supplied workspace.

Accepted-history reconciliation is not a task merge. BACKGROUND-001 remains Complete at architect-accepted Attempt 6 and SHOPIFY-002 remains Complete at architect-accepted Attempt 8. Neither task is reopened or replaced by a synthetic earlier completion record. Clean first-production compatibility corrections are assigned only to still-Pending/Ready tasks.

## Luna-oriented merge decision

Safe merges:

| Superseded task | Active owner | Reason |
|---|---|---|
| `BACKGROUND-016` | `BACKGROUND-012` | same reconciliation service, same provider snapshot, same dependencies, mutually exclusive lifecycle classification |
| `BACKGROUND-017` | `BACKGROUND-013` | same execution-policy boundary/paths; retain distinct NO_CONTRACT vs FROZEN reasons |
| `SHOPIFY-010` | `SHOPIFY-014` | component is pure presentation of the top-up adapter contract; same feature boundary |
| `SHOPIFY-011` | `SHOPIFY-015` | component is pure presentation of the Shopify-hosted plan-management flow |
| `SHOPIFY-019` | `SHOPIFY-016` | same merchant surfaces/action guards; one explicit lifecycle-restriction state matrix is safer |

The surviving tasks were rewritten rather than told to "do both old tasks". Each contains exact inspect paths, ordered state transitions, forbidden behaviour, numbered tests, validation requirements and STOP conditions suitable for GPT-5.6 Luna.

Review reconciliation preserves two absorbed edge requirements explicitly:

- `BACKGROUND-012` retains the post-commit BACKGROUND-009 capacity-resume hint after verified unfreeze;
- `SHOPIFY-016` consumes SHOPIFY-009's distinct `CONTRACT_FROZEN`/canonical local capacity projection rather than inventing another frozen-capacity state.

## Deliberate non-merges

The following remain separate because combining them would cross a real failure/performance/concurrency boundary:

- provider lifecycle snapshot (`BACKGROUND-015`) vs reconciliation (`BACKGROUND-012`);
- general lifecycle execution gate (`BACKGROUND-013`) vs the 22k/min queued Shopify hot-path gate (`BACKGROUND-018`);
- individual capacity-source reservation/accounting tasks;
- paid-period read presentation (`SHOPIFY-004`) vs App-Event cycle guard (`SHOPIFY-007`);
- promotion selection mutation (`SHOPIFY-021`) vs capacity presentation (`SHOPIFY-020`);
- all terminal system-test tasks.

## First-production removals

No runtime compatibility is retained for:

```text
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment / FREE_ALLOWANCE_ADJUSTED
FREE_RECOVERY_LIFETIME
ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)
MIGRATION_RECONCILED
SubscriptionCancellationRequest / local appSubscriptionCancel state machine
arbitrary merchant/Admin-selected purchased-credit refund quantity
negative/fractional App Event refund correction
campaign-less PromotionalCreditGrant
BILLING_FREE_ALLOWANCE_EXHAUSTED
BILLING_PLAN_CHANGE_ACTION_REQUIRED
```

Canonical lifetime entitlement is `LIFETIME_FREE_RECOVERY_CREDITS`.

## Capacity order

```text
Paid: selected usable promotion -> current-period included -> purchased FIFO -> lifetime Free -> block new admission
Free: selected usable promotion -> purchased FIFO -> lifetime Free -> block new admission
```

The exact selected campaign grant lot is promotion authority; there is no aggregate promotional entitlement counter.

## Cancellation/freeze model

`BACKGROUND-012` is now the sole lifecycle reconciliation owner for scheduled/effective cancellation and freeze/unfreeze classification. Shopify is lifecycle authority; Moda does not call `appSubscriptionCancel`.

`BACKGROUND-013` is the sole general business-execution gate for both `NO_CONTRACT` and `FROZEN`, with distinct denial reasons and restoration semantics.

`BACKGROUND-018` remains separate for the high-volume queued Shopify checkout/cart/order early gate.

## Merchant plan-management model

`SHOPIFY-015` owns the app/HTTP half of plan management: hosted selection, callback provider verification, current/pending classification and production panel presentation.

`BACKGROUND-010` owns effective provider-confirmed plan transition. The callback never mutates BillingPeriod entitlement or performs proration.

## Current Ready frontier

```text
ARCH-010-SHOPIFY-016
ARCH-010-SHOPIFY-025
```


## Purchase-lifecycle/refund forward correction — 2026-09-13

The first-production product definition now treats each `RecoveryCreditPurchase` as an independent lifecycle:

```text
REQUESTED / ACTIVE / COMPLETED / WITHDRAWN / REFUNDED
```

The merchant withdraws an entire purchase from new allocation and requests refund of **all credits that ultimately remain unused** after pre-existing reservations settle. There is no merchant/Admin quantity input.

Completed DATABASE-007/BACKGROUND-014 remain immutable history. Forward corrections are owned by DATABASE-014, BACKGROUND-021 and BACKGROUND-022. The old pending support-only SHOPIFY-017 is superseded by SHOPIFY-025 (server read/actions) + SHOPIFY-026 (dedicated purchase/refund UI).

This correction deliberately preserves the existing aggregate purchased counter for the hot path while removing per-lot refunding/refunded counters from the final baseline.

## System-test boundary

System tests remain terminal/manual-gated and are never prerequisites for unfinished implementation. They run only after implementation/integration is ready and the developer explicitly invokes them.

## Architect conclusion

The active task graph is now smaller without blurring real architecture boundaries. The consolidation removes artificial task handoffs while preserving the boundaries that matter for correctness, concurrency, provider authority and the 22,000-webhook/minute performance target.

## Post-cleanup review update — BACKGROUND-011 Attempt 2

Before this cleanup overlay was applied, `ARCH-010-BACKGROUND-011` returned to review
against DATABASE-013 revision `014408e`.

Architect review found the DATABASE-013 rename, plan-independent lifetime policy and
lifetime-counter concurrency work sound, but identified two capacity-routing defects:

```text
different purchased/lifetime source keys can reserve two buckets for one recovery
purchased spendability is incorrectly gated by recoveryCreditPack.enabled
```

The attempt also partially composes Paid included-capacity routing that belongs to
`ARCH-010-BACKGROUND-002`.

`BACKGROUND-011` is therefore:

```text
status: Ready — Changes Requested Attempt 2
attempt: 2
next valid claim: Attempt 3
```

The Ready frontier is unchanged, but this task is a correction attempt rather than a
fresh Attempt 1.

## Post-cleanup review update — BACKGROUND-011 Attempt 3

Attempt 3 correctly established one canonical reservation source key, purchased-credit
spendability independent of pack-purchase enablement, and restored the Paid routing
boundary to BACKGROUND-002.

Architect review identified one remaining replay-state defect:

```text
already-released reservations are admitted without re-reserving capacity
already-ambiguous reservations are admitted instead of blocking replay
```

The Background repository is also still pinned to Shared `0.10.0` even though
SHARED-008 published and completed `0.11.0`.

`BACKGROUND-011` therefore remains on the Ready frontier as:

```text
status: Ready — Changes Requested Attempt 3
attempt: 3
next valid claim: Attempt 4
```

## Post-cleanup review update — BACKGROUND-011 Attempt 4 accepted

`ARCH-010-BACKGROUND-011` Attempt 4 is architect-accepted Complete.

Accepted implementation:

```text
implementation: e5d6f0b
parent claim:   7e42c4f
parent report:  150a557
database:       014408e
Shared:         0.11.0
```

Accepted result:

```text
one canonical purchased/lifetime recovery reservation identity
replay never changes the originally selected capacity bucket
AMBIGUOUS replay blocks
RELEASED replay re-reserves only the same original bucket
lifetime-Free capacity uses granted - committed - reserved only
invalid lifetime counters fail closed
Shared 0.11.0 clean contract consumed
Paid included-credit composition remains owned by BACKGROUND-002
```

New Background Ready frontier:

```text
ARCH-010-BACKGROUND-002
ARCH-010-BACKGROUND-014
ARCH-010-BACKGROUND-015
```

`BACKGROUND-019` is architect-accepted Complete at Attempt 6. Its accepted promo-first cross-bucket routing is immutable and must be preserved by later purchased-credit lifecycle corrections such as BACKGROUND-022.

## Post-cleanup review update — BACKGROUND-003 Attempt 5 accepted

`ARCH-010-BACKGROUND-003` Attempt 5 is architect-accepted Complete.

Accepted history:

```text
Attempt-5 claim:          b5f3f9d90e9598b8f4ff32463bdd2dc9ed43a256
Attempt-5 evidence:       0fe699ced684a1c2ffde09cc3510eea2d98524e1
Attempt-5 parent report:  445d1874
```

The final evidence proves that queued first-Paid reconciliation fails closed when a
local BillingPlan still has the same `plan-paid` identity but Shopify's current plan
handle has drifted from durable pending intent (`paid-old -> paid-new`). The guard
records `PENDING_PLAN_HANDLE_MISMATCH`, schedules the bounded retry, preserves the
pending target and returns before any transaction/activation path. Attempt 5 required
no production-source change.

Direct dependency promotion caused by this acceptance:

```text
ARCH-010-BACKGROUND-006 -> Ready
ARCH-010-BACKGROUND-010 -> Ready
ARCH-010-SHOPIFY-003    -> Ready
```

Only these direct dependants are promoted here. Their own dependants remain gated
until the corresponding newly Ready task is separately implemented and
architect-accepted Complete.
## Post-review update — SHOPIFY-021 Attempt 4 accepted

`ARCH-010-SHOPIFY-021` Attempt 4 is architect-accepted Complete.

Accepted implementation/evidence:

```text
implementation: af3a9c44
parent report:  b6253f1e
PostgreSQL:     self-provisioned postgres:17.6-alpine via Testcontainers
concurrency:    2 passed / 0 skipped
database:       5443afdd8f0c816dc16e1f3e93f9906c5ca31d94 unchanged
```

The accepted merchant promotion-selection boundary now has real PostgreSQL evidence
for both different-campaign single-winner serialization and same-campaign exact-grant
replay. The integration fixture provisions and migrates its own disposable database;
`TEST_DATABASE_URL` is no longer part of this task's test contract.

`ARCH-010-SHOPIFY-022` is newly Ready because both of its dependencies are Complete.
`SHOPIFY-020` and `SYSTEM-TEST-003` remain gated by their other incomplete dependencies.

Current Ready frontier from authoritative ARCH-010 task YAML after this acceptance:

```text
ARCH-010-ADMIN-006
ARCH-010-BACKGROUND-003
ARCH-010-SHOPIFY-022
```

## Post-review update — SHOPIFY-022 Attempt 3 accepted

`ARCH-010-SHOPIFY-022` Attempt 3 is architect-accepted Complete.

Accepted implementation/evidence:

```text
implementation: 666409d
parent report:  600e9ba
focused:        28/28 and 46/46 passed
full suite:     316 passed, 3 skipped
build:          passed
```

The merchant promotion-history boundary now has explicit regression evidence that
real `REOPENED` lifecycle state never overrides `EXHAUSTED`, `CLOSED`, `EXPIRED` or
`NO_LONGER_ELIGIBLE`, and that reopen lifecycle evidence/internal provenance remains
server-side only.

`ARCH-010-SYSTEM-TEST-003` remains Pending / manual-gated because its other
dependencies are still incomplete. No direct dependant becomes Ready solely from
this acceptance.

Current Ready frontier from authoritative ARCH-010 task YAML remains:

```text
ARCH-010-BACKGROUND-006
ARCH-010-BACKGROUND-010
ARCH-010-SHOPIFY-003
```

## Post-review update — BACKGROUND-010 Attempt 6 accepted

`ARCH-010-BACKGROUND-010` Attempt 6 is architect-accepted Complete.

Accepted implementation/evidence:

```text
implementation: 48f1b40bea8093b5e5a1b99ed9ca4d67ffbbac7d
focused:        198/198 passed
integration:    3/3 passed
Prisma:         validate/generate passed
diff:           passed
```

Attempt 6 was evidence-only: the actual Attempt-5 -> Attempt-6 implementation delta
is limited to the two scoped reconciliation test files. The accepted production
implementation from Attempt 4/5 therefore remains unchanged.

Newly dependency-eligible tasks:

```text
ARCH-010-BACKGROUND-012
ARCH-010-SHOPIFY-015
```

`ARCH-010-SYSTEM-TEST-001` remains Pending/manual-gated because its remaining
dependencies are incomplete.

Current Ready frontier from authoritative task YAML after this acceptance:

```text
ARCH-010-BACKGROUND-012
ARCH-010-SHOPIFY-003
ARCH-010-SHOPIFY-006
ARCH-010-SHOPIFY-015
```

## Post-review update — SHOPIFY-006 Attempt 4 accepted

`ARCH-010-SHOPIFY-006` Attempt 4 is architect-accepted Complete.

Accepted result:

```text
parent /app loader gates lifecycle before app-shell reads
pending reinstall ordinary product paths -> /app/reinstalling
suspended ordinary product paths -> /app/merchant-support
pending reinstall merchant support remains reachable
unmarked uninstall merchant support -> /auth/login
standalone reinstall route remains outside the normal app layout
```

Accepted evidence:

```text
implementation: 5aa1a1898ffbdd4191354a4f62d0cbc0f4ab7ddf
focused:        83 passed
full suite:     380 passed, 3 skipped
build:          passed
database:       5443afdd8f0c816dc16e1f3e93f9906c5ca31d94 unchanged
```

`ARCH-010-SYSTEM-TEST-002` remains Pending/manual-gated because its other lifecycle
dependencies are incomplete. No normal implementation task is promoted by this
acceptance.

Current Ready frontier from authoritative ARCH-010 task YAML:

```text
ARCH-010-BACKGROUND-012
ARCH-010-SHOPIFY-004
ARCH-010-SHOPIFY-015
```

## Post-review update — SHOPIFY-015 Attempt 5 accepted

`ARCH-010-SHOPIFY-015` Attempt 5 is architect-accepted Complete.

Accepted hosted-return concurrency model:

```text
durable pre-provider Subscription fence
  -> one Partner read
  -> ShopSettings/Subscription lock
  -> full durable projection equality check
  -> unchanged projection only may persist provider observation
```

Absence is now represented canonically:

```text
no durable Subscription before Partner read -> null
no durable Subscription after lock          -> null
```

so unchanged `NO_ACTIVE_SUBSCRIPTION` is classified `no_active` without inventing a
Subscription or retry state.

Accepted implementation:

```text
0fad89ce76d59d954a0bd8894d527eaadda478b1
```

Validation:

```text
focused: 196 passed
full:    438 passed, 3 skipped
Prisma:  passed
build:   passed
static:  passed
diff:    passed
```

`ARCH-010-SHOPIFY-012` remains Pending because `SHOPIFY-007`, `SHOPIFY-009` and
`SHOPIFY-014` remain incomplete.

Current Ready frontier from authoritative ARCH-010 task YAML:

```text
ARCH-010-BACKGROUND-012
ARCH-010-SHOPIFY-007
ARCH-010-SHOPIFY-009
```

## Post-review update — BACKGROUND-012 Attempt 8 accepted with manual validation follow-up

`ARCH-010-BACKGROUND-012` Attempt 8 is architect-accepted Complete.

The final production implementation is frozen. Attempt 8 changed tests only and left
three evidence rows (17, 24, 26) without complete executable proof. Architect review
classified those as non-blocking evidence/workspace gaps rather than demonstrated
production defects.

Manual/system lifecycle validation remains required before final ARCH-010 release
acceptance for:

```text
ambiguous provider-null established contract preservation
freeze/unfreeze recovery admission behaviour
fully materialized Shopify/Messaging ingress ownership scan
```

This acceptance promotes:

```text
ARCH-010-BACKGROUND-013
ARCH-010-BACKGROUND-018
```

to Ready.

`SHOPIFY-016` and `SYSTEM-TEST-002` remain gated by their remaining dependencies.

Current authoritative Ready frontier:

```text
ARCH-010-BACKGROUND-013
ARCH-010-BACKGROUND-018
```

## Post-review update — BACKGROUND-018 Attempt 1 accepted

`ARCH-010-BACKGROUND-018` is architect-accepted Complete on functional behaviour.

Accepted boundary:

```text
FROZEN checkout.created
  -> stop before BullMQ candidate/index work

FROZEN checkout.updated
  -> stop before candidate/recovery/provider work

FROZEN cart.activity
  -> one minimal durable lifecycle read
  -> stop before candidate/index work

FROZEN order.completed
  -> retain bounded terminal safety bookkeeping only
```

No synchronous Shopify/Partner lifecycle lookup was added to HTTP ingress, and no
new lifecycle cache or global serialization was introduced.

The approximately 22,000-events/minute architecture target remains a later
integrated/manual capacity-validation item.

Current Background Ready frontier:

```text
ARCH-010-BACKGROUND-013
```

`ARCH-010-SYSTEM-TEST-002` remains Pending/manual-gated until its remaining
implementation dependencies, including `BACKGROUND-013` and `SHOPIFY-016`, are
Complete.

## Post-review update — BACKGROUND-013 Attempt 3 accepted

`ARCH-010-BACKGROUND-013` Attempt 3 is architect-accepted Complete on functional
behaviour.

Accepted execution rule:

```text
ACTIVE/TRIALING
  -> existing plan/capacity policy

NO_CONTRACT
  -> CONTRACT_REQUIRED terminal business no-op

FROZEN
  -> SUBSCRIPTION_FROZEN terminal business no-op

UNMAPPED / SYNC_ERROR / inactive Shop
  -> existing fail-closed behaviour
```

The canonical gate is now enforced across the relevant recovery, candidate,
capacity-resume, conversation-turn, billing and outbound-provider boundaries, with
rechecks at owned asynchronous lock/send boundaries.

No new HTTP-ingress lifecycle lookup, Partner API gate, queue purge, lifecycle Redis
cache or global serialization was introduced.

`SHOPIFY-016` remains Pending because `SHOPIFY-012` is still incomplete.

Current implementation-ready frontier:

```text
ARCH-010-SHOPIFY-012
ARCH-010-BACKGROUND-021
```

## Post-review update — BACKGROUND-021 Attempt 1 accepted

`ARCH-010-BACKGROUND-021` is architect-accepted Complete on functional and commercial
correctness.

Accepted purchase activation authority:

```text
REQUESTED non-spendable purchase
  + exact immutable before snapshot
  + exact linked REPORTED one-pack UsageEvent
  + exact provider subscription / plan / cycle / pack meter
  + unique unresolved purchase
  + Q1 = Q0 + 1
  + positive C1 - C0
  + K1 = K0
  -> one Serializable REQUESTED -> ACTIVE activation
  -> immutable provider amount/currency
  -> currentAmount = creditsGranted
  -> aggregate purchased grant exactly once
```

Ambiguous or incomplete provider evidence remains non-spendable.

Capacity resume remains post-commit/best-effort.

This acceptance promotes:

```text
ARCH-010-BACKGROUND-022
```

to Ready.

`ARCH-010-SHOPIFY-025` remains Pending until `BACKGROUND-022` is Complete.

Current implementation-ready frontier:

```text
ARCH-010-SHOPIFY-012
ARCH-010-BACKGROUND-022
```

## Post-review update — BACKGROUND-022 Attempt 3 accepted

`ARCH-010-BACKGROUND-022` is architect-accepted Complete on functional behavior.

Accepted purchased-credit reservation model:

```text
fresh ACTIVE lot snapshot
  -> prove currentAmount - reservedAmount >= quantity
  -> exact id/version/status/currentAmount/reservedAmount CAS
  -> increment reservedAmount
  -> whole Serializable retry on CAS loss
```

This allows multiple live reservations from one multi-credit lot without weakening
refund/lifecycle concurrency.

The earlier final-withdrawn-credit correction remains accepted:

```text
last reserved credit committed from WITHDRAWN lot
  -> COMPLETED atomically
  -> live refund cancelled NO_CREDITS_REMAINING
  -> no provider-refund movement
```

This acceptance promotes:

```text
ARCH-010-SHOPIFY-025
```

to Ready.

Current implementation-ready frontier:

```text
ARCH-010-SHOPIFY-016
ARCH-010-SHOPIFY-025
```

