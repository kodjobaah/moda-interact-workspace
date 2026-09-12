---
id: ARCH-010-SYSTEM-TEST-004
architecture_id: ARCH-010
title: Final ARCH-010 merchant lifecycle acceptance matrix
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: manual
status: pending
priority: 103
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SYSTEM-TEST-001
- ARCH-010-SYSTEM-TEST-002
- ARCH-010-SYSTEM-TEST-003
- ARCH-010-SYSTEM-TEST-005
enables: []
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SYSTEM-TEST-004: Final ARCH-010 merchant lifecycle acceptance matrix

## Terminal/manual gate

Do **not** auto-start. The developer explicitly invokes this final acceptance task only after SYSTEM-TEST-001/002/003 are manually accepted.

This task is terminal. It enables no implementation task.

## Objective

Produce the final cross-scenario acceptance record proving that the independently tested ARCH-010 behaviours compose without contradictory state or merchant access.

Prefer reusing evidence from SYSTEM-TEST-001/002/003 plus a small number of targeted cross-scenario journeys rather than rerunning every expensive provider test unnecessarily.

## Cross-scenario journeys

At minimum validate these composed journeys:

### Journey 1 — Free -> Paid -> exhausted -> top-up -> rollover -> Free

Prove one lifetime Free grant only, exact source consumption order, purchased balance survival, no monthly Free reset and no duplicate provider-period allowance.

### Journey 2 — Paid -> promotional campaign -> purchase -> partial refund -> plan change

Prove promotional is consumed before purchased, unused purchased capacity remains refundable, refund hold cannot be spent, and plan change preserves every lifetime bucket and refund history.

### Journey 3 — Paid -> freeze -> natural order completion -> unfreeze -> later cancellation

Prove frozen checkout/cart work is suppressed, terminal order bookkeeping prevents stale recovery, unfreeze restores only after verified provider truth, and later effective cancellation produces `NO_CONTRACT` rather than `FROZEN` while preserving lifetime balances.

### Journey 4 — Active -> uninstall with queued work -> reinstall after provider cycle advanced

Prove queued work does not execute while inactive, no lifetime balance is destroyed/regranted, and reinstall catches up directly to the exact provider-current cycle without synthetic missed periods.

## Final state matrix

Produce a single matrix covering at least:

```text
fresh NO_CONTRACT/onboarding
Free active
Paid active
capacity exhausted
provider period draining
plan change pending
cancellation scheduled
NO_CONTRACT after cancellation
UNINSTALLED
reinstall pending
FROZEN
refund pending/held/completed
promotional capacity available
```

For each state record:

- merchant surfaces available;
- new recovery allowed?;
- existing conversation work allowed?;
- checkout/cart worker processing allowed?;
- top-up purchase allowed?;
- plan change allowed?;
- balances spendable vs preserved-only;
- canonical exit transition.

## Architectural invariants that must all pass

1. Shopify App Pricing remains commercial subscription authority.
2. PostgreSQL remains durable local lifecycle/capacity truth; Redis is reconstructable delivery/scheduling infrastructure.
3. Merchants never access `moda-interact-admin`.
4. No automatic paid overage exists.
5. Lifetime Free is granted exactly once per shop at first verified activation.
6. Promotional and purchased credits survive plan/lifecycle changes; promotional is non-refundable, purchased unused capacity can be partially refunded.
7. Capacity order is exact and uniform across runtime/read models.
8. Free provider BillingPeriod never becomes a monthly Free recovery grant.
9. `activeSubscription=null` alone never proves cancellation for an established merchant.
10. System-test/manual evidence contains no secrets.

## Outcome

All required rows/scenarios must be PASS before ARCH-010 can be considered implementation-accepted.

If any scenario fails, identify the exact owning implementation task(s), return those tasks to `moda_architect` for Changes Requested, and do not weaken the test or architecture to match the defect.

## Validation

If no harness code changes are required, this task may be evidence-only. If code changes are made, run repository-declared tests/type/lint and `git diff --check`.

## Non-goals

Do not add new product behaviour, change plan economics, add promotional expiry, automate provider refunds, or redesign mid-cycle plan entitlement segmentation.

## Stop conditions

STOP if prerequisite system tests are not architect/developer accepted, if the integrated environment does not correspond to the commits those tests exercised, or if provider credentials/data cannot be handled safely.

## Completion Report

### Status
Not started.

### Evidence Reused
Populate during execution.

### Cross-Scenario Journeys
Populate during execution.

### Final State Matrix
Populate during execution.

### Outcome
Pending.

### Architect Review
Manual terminal gate; pending final acceptance.
