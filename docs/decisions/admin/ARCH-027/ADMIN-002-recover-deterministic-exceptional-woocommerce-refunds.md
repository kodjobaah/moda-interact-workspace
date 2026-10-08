---
id: ARCH-027-ADMIN-002
architecture_id: ARCH-027
title: Recover deterministic exceptional WooCommerce refunds
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-04
updated: 2026-10-04
---

# Recover deterministic exceptional WooCommerce refunds

## Objective

**Superseded before implementation.**

The original task inferred allowance recovery from provider monetary relationships (`expected amount`, under-refund, over-refund). The reconciled rule is:

```text
provider owns monetary refund
Moda owns allowance
```

Moda never derives credit quantity from provider money.

## Replacement architecture

Normal Woo refund freezes local unused allowance, waits for provider monetary outcome, and removes exactly the frozen `finalCreditQuantity` on trusted refund completion.

An unmatched external provider refund remains ADMIN-001 attention-only because no trusted local allowance quantity can be inferred from money.

Provider rejection/cancellation may release a local hold only after SYSTEM-TEST-002 proves a trusted evidence contract and a later explicit task defines that mutation.

## Requirements

- Keep status `superseded`, attempt 0 and no claim/executor.
- Do not implement amount-based over/under-refund recovery.
- Do not create a local refund/credit mutation from unmatched provider money.

## Work Items

- [x] Supersede amount-based exceptional recovery.
- [x] Remove from system-test dependency/enable chains.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

- [x] No ADMIN-002 implementation branch/worktree is created.
- [x] ARCH-027 has no monetary-to-credit inference path for Woo refunds.
- [x] Unmatched provider refund remains non-mutating attention.

## Stop Condition

STOP. Do not execute this task.

## Architect Review

### Review Status

Superseded

### Follow-up

`ARCH-027-ADMIN-001` and `ARCH-027-SYSTEM-TEST-002`.
