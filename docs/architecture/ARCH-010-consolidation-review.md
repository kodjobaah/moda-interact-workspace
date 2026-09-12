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

The attached 2026-09-12 workspace contains 81 ARCH-010 task files. After synchronizing the developer-confirmed completion of SHOPIFY-002 and applying the safe pending-task consolidation described below:

```text
complete:    29
ready:        6
pending:     39
superseded:   7
```

Graph validation must remain based on individual task `depends_on` metadata. Superseded tasks are history only and are not execution prerequisites.

## Completed-history rule

Already-completed task implementation/review history is not reopened merely to merge task definitions. The five consolidation merges below affect only tasks that were still unimplemented in the supplied workspace.

SHOPIFY-002 is a special status synchronization: the developer confirmed it is already complete but its parent task document was stale. The task state is corrected for planning; this consolidation does not invent missing task-branch evidence not present in the ZIP.

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
ARCH-010-BACKGROUND-001
ARCH-010-BACKGROUND-011
ARCH-010-BACKGROUND-015
ARCH-010-SHOPIFY-023
```

## System-test boundary

System tests remain terminal/manual-gated and are never prerequisites for unfinished implementation. They run only after implementation/integration is ready and the developer explicitly invokes them.

## Architect conclusion

The active task graph is now smaller without blurring real architecture boundaries. The consolidation removes artificial task handoffs while preserving the boundaries that matter for correctness, concurrency, provider authority and the 22,000-webhook/minute performance target.
