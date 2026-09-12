---
id: ARCH-010-SYSTEM-TEST-005
architecture_id: ARCH-010
title: Validate Admin upgrade economics guardrail end to end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 995
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-ADMIN-009
enables:
- ARCH-010-SYSTEM-TEST-004
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-SYSTEM-TEST-005: Validate Admin upgrade economics guardrail end to end

## Manual gate

This task is **terminal/manual-gated**. Do not auto-run it merely because dependencies become Complete. No implementation task may depend on this task.

## Objective

Validate in an integrated test environment that Admin cannot activate an economically unsafe or unverifiable lower-plan + top-up configuration and that PASS configurations remain editable without affecting merchant runtime billing authority.

## Required scenarios

Re-use the fixtures and codes in:

```text
docs/contracts/ARCH-010-upgrade-economics-guardrail-test-matrix.md
```

At minimum prove end-to-end:

1. SUPER_ADMIN configures an explicit Free→Starter edge and verified economics snapshots;
2. Free production economics use monthly included `0`, not the lifetime-Free grant;
3. PASS permits guarded catalog mutation;
4. supplied Growth→Scale-like <20% premium blocks mutation;
5. missing snapshot yields UNVERIFIED and blocks mutation;
6. recurring/usage currency mismatch blocks mutation;
7. changing pack size causes immediate re-evaluation;
8. changing lower or higher monthly included capacity re-evaluates all affected adjacent edges;
9. top plan with no successor does not invent one;
10. top-ups disabled produces `NO_TOPUPS_AVAILABLE` for that edge;
11. guarded mutation writes calculation/snapshot audit evidence;
12. blocked mutation leaves database catalog state unchanged;
13. promotional/lifetime-Free/purchased merchant balances do not alter the result;
14. no Shopify merchant charge, App Event or subscription mutation is emitted by the guardrail test;
15. Admin explanation matches the persisted/evaluated integer-minor calculation.

## Evidence

Capture:

- seeded edge/snapshot IDs;
- pre/post BillingPlan state;
- PASS/FAIL/UNVERIFIED result/code/details;
- BillingAuditEvent evidence;
- proof blocked mutations are atomic no-ops;
- proof no merchant billing action was emitted.

## Non-goals

Do not test profitability/margin policy or change live Shopify Partner Dashboard prices.

## Completion Report

### Status
Manual-gated / not run.

### Evidence
Populate only when explicitly invoked.

### Architect Review
Pending.
