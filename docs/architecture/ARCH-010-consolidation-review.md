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
RecoveryCreditPurchaseStatus.REFUNDED
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
ARCH-010-ADMIN-007
ARCH-010-ADMIN-010
ARCH-010-BACKGROUND-002
ARCH-010-BACKGROUND-014
ARCH-010-BACKGROUND-015
ARCH-010-SHOPIFY-023
```

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

`BACKGROUND-019` remains Pending until both BACKGROUND-002 and BACKGROUND-014 complete.

