---
id: ARCH-010-SYSTEM-TEST-002
architecture_id: ARCH-010
title: Validate uninstall, reinstall, cancellation and freeze execution gates
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: manual
status: pending
priority: 101
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-BACKGROUND-006
- ARCH-010-BACKGROUND-012
- ARCH-010-BACKGROUND-013
- ARCH-010-BACKGROUND-016
- ARCH-010-BACKGROUND-017
- ARCH-010-BACKGROUND-018
- ARCH-010-SHOPIFY-006
- ARCH-010-SHOPIFY-016
- ARCH-010-SHOPIFY-019
enables:
- ARCH-010-SYSTEM-TEST-004
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SYSTEM-TEST-002: Validate uninstall, reinstall, cancellation and freeze execution gates

## Terminal/manual gate

Do **not** auto-start. The developer explicitly invokes this terminal system test after the relevant implementation has been integrated and manually smoke-checked.

No implementation task depends on this system-test task.

## Objective

Prove that lifecycle state controls **execution**, not ownership of historical balances, and that Shopify subscription lifecycle truth is never collapsed into the wrong Moda state.

## Required scenarios

### A. Uninstall execution gate

With an active merchant that owns monthly/lifetime/purchased/promotional state:

1. enqueue representative checkout/recovery and inbound WhatsApp work;
2. process Shopify uninstall;
3. prove `Shop.status=UNINSTALLED` while subscription/BillingPeriod/history/balances are preserved;
4. prove pre-existing queued business jobs terminate safely after resolving the inactive shop;
5. prove no new recovery, conversation turn, CommerceAgent call, outbound WhatsApp or new credit reservation is created after uninstall;
6. prove allowed historical/provider-status accounting can still finalize previously committed work.

### B. Safe reinstall

Prove reinstall does not immediately make the merchant executable.

Validate provider outcomes:

- no active Shopify contract -> activate shop into prior-onboarded `NO_CONTRACT` access without destroying lifetime balances;
- same Free plan/current provider cycle -> restore safely without regranting lifetime Free;
- same Paid plan/same exact period -> reuse period/counter without reset;
- same plan/later provider cycle -> delegate to canonical rollover and create only provider-current cycle;
- provider API unavailable for bounded retry window -> merchant remains fail-closed in restoration state and explicit retry/support remains available.

### C. Scheduled and effective full cancellation

Validate:

- `cancelAtEndOfCycle=true` with no pending plan change is presented as scheduled full cancellation;
- current service continues until provider-effective end, except new top-up purchase is disabled once full cancellation is scheduled;
- provider `CANCELED` evidence + no active contract closes the final provider BillingPeriod and transitions to `NO_CONTRACT`;
- Paid monthly unused remainder is forfeited;
- promotional, purchased and lifetime Free balances remain owned but non-spendable;
- onboarding history is not reset and the merchant remains on dashboard/history/support/billing surfaces;
- all new shop business execution stops under `NO_CONTRACT`.

Also prove Paid->Free with provider pending/current plan state is treated as a plan change, not full cancellation.

### D. Freeze and unfreeze

Validate provider lifecycle classification with live subscription snapshot + historical lifecycle evidence.

Prove:

- `SUBSCRIPTION_FROZEN` projects `Subscription.status=FROZEN`, not `NO_CONTRACT`;
- BillingPeriod and all balances remain unchanged;
- all new recovery/WhatsApp/CommerceAgent/billing mutation work is blocked;
- checkout/cart worker events terminate early while frozen;
- `order.completed` may perform only terminal safety bookkeeping for an already-existing recovery and cannot create new customer-facing work;
- delayed reconciliation remains reconstructable after Redis loss;
- `SUBSCRIPTION_UNFROZEN` alone does not restore execution without usable live `activeSubscription`;
- verified restoration reuses same cycle or safely catches up to exact current provider cycle without synthetic missed-month allowances.

### E. Null provider result classification

For an established merchant prove:

```text
activeSubscription = null + latest CANCELED -> cancellation path
activeSubscription = null + latest FROZEN  -> frozen path
activeSubscription = null + UNFROZEN/CREATED/UPDATED/CANCELLATION_SCHEDULED/no usable evidence -> unresolved fail-closed retry
provider transport failure -> sync failure, never invented NO_CONTRACT
```

## Required evidence

Return a scenario matrix with durable state before/after, queued-job disposition, merchant-visible behaviour and provider evidence.

Explicitly prove no lifecycle transition resets:

```text
campaign-linked PromotionalCreditGrant quantity/committed/reserved history
PURCHASED_RECOVERY_CREDITS
LIFETIME_FREE_RECOVERY_CREDITS
```

except ordinary consumption/refund rules unrelated to the lifecycle event. There is no aggregate promotional entitlement counter in the first-production baseline.

## Validation

Any system-test harness changes must pass repository-declared tests/type/lint and `git diff --check`.

Use real or captured authoritative Partner API evidence for lifecycle-event classification; do not simulate a cancellation/freeze distinction only in prose.

## Non-goals

Do not test partial purchased-credit refund settlement or promotional campaign Admin UX here. Do not redesign Shopify identity mapping. Do not introduce provider cancellation mutations.

## Stop conditions

STOP if provider historical-event access is unavailable in the configured Partner API and the freeze/cancel distinction cannot be evidenced safely. STOP if a lifecycle test would require production merchant data or secrets. Return implementation defects to the owning ARCH-010 task rather than changing runtime code from the system-test task.

## Completion Report

### Status
Not started.

### Scenarios Executed
Populate during execution.

### Evidence
Populate during execution.

### Validation Results
Populate during execution.

### Git / VCS
Populate if harness code changes.

### Architect Review
Manual terminal gate; pending developer/architect acceptance.
