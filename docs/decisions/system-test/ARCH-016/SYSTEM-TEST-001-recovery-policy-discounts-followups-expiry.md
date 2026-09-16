---
id: ARCH-016-SYSTEM-TEST-001
architecture_id: ARCH-016
title: Validate recovery policy, discount lifecycle, outreach charging and recovery expiry end to end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-016-DATABASE-001
- ARCH-016-SHARED-001
- ARCH-016-SHOPIFY-001
- ARCH-016-BACKGROUND-001
- ARCH-016-SHOPIFY-002
- ARCH-016-ADMIN-001
- ARCH-016-ADMIN-002
- ARCH-016-BACKGROUND-002
- ARCH-016-BACKGROUND-003
enables: []
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-016-SYSTEM-TEST-001

## Objective

Validate the integrated ARCH-016 behavior only after every implementation dependency is architect-accepted and the developer has had the opportunity to perform manual testing.

## Execution timing

This task is intentionally defined now but MUST NOT execute while any dependency is incomplete.

When dependencies become Complete, `moda_architect` may mark it Ready. The developer may perform manual environment testing before invoking it.

No implementation task depends on this system-test task.

## Authorized implementation surface

```text
architecture-specific fixtures/seeds under existing system-test conventions
ARCH-016 test specifications
Shopify test fixture helpers
Render/test-environment orchestration already owned by moda_system_test
no application implementation changes
```

## Required scenarios

### A. Subscription + discount catalogue lifecycle

1. installed shop with NO_CONTRACT -> no discount provider sync;
2. activate Free -> FULL sync -> CURRENT local catalogue;
3. activate Paid -> FULL sync -> CURRENT local catalogue;
4. Shopify discounts/create webhook -> full reconciliation;
5. update -> changed projection;
6. delete -> row retained but unavailable;
7. redeemcode add/remove -> reconciliation;
8. duplicate webhook delivery -> no duplicate/corrupt state;
9. uninstall -> shop/catalogue unavailable, rows retained;
10. reinstall + eligible subscription reconciliation -> full sync before CURRENT;
11. reinstall NO_CONTRACT -> unavailable;
12. scope missing/removal -> unavailable.

Use Shopify test/dev provider fixtures or documented stubs consistent with system-test repository; do not run destructive calls against production merchants.

### B. Merchant policy

- Free merchant can configure recovery start/follow-up/offer mode;
- Paid merchant same capability;
- NONE;
- valid FIXED;
- active but non-fixed-selectable discount visible/not selectable;
- AI_BEST_APPLICABLE persists with no AI execution;
- admin override changes effective policy without changing merchant row;
- override expiry restores merchant policy.

### C. Outreach credits + Conversation

Seed enough entitlement for controlled assertions.

Scenario 1:

```text
attempt #1 sent -> credit -1
customer replies -> conversation continues
agent reply -> credit unchanged
follow-up wake-up -> suppressed
```

Scenario 2:

```text
attempt #1 sent -> credit -1
no reply
follow-up after configured delay (<24h) -> attempt #2 -> credit -1 again
same Conversation ID
```

Scenario 3:

```text
follow-up >=24h -> still new proactive credit
same Conversation ID
```

Scenario 4:

```text
no capacity at follow-up due -> no provider send; no negative capacity; attempt CAPACITY_BLOCKED
```

Prove retry/idempotency for both attempt IDs.

### D. Recovery expiry/generation

With platform lifetime configured short enough for test fixture:

```text
recovery generation 1 active
external activity advances clock
outbound automation does not advance clock
expiry after inactivity -> EXPIRED
history remains
later checkout update -> PendingRecoveryCandidate
further update resets pending timer
maturity -> generation 2
new Conversation for generation 2
old Conversation still historical
```

Also prove COMPLETED and CANCELLED do not restart.

### E. Concurrency/race

- two matured restart jobs -> one generation N+1;
- checkout activity races expiry -> active recovery survives when activity wins;
- two discount sync workers -> older token cannot finalize over newer generation.

## AI non-goal assertion

Search/test runtime to prove ARCH-016 paths do not invoke CommerceAgent/LLM merely because `AI_BEST_APPLICABLE` is configured.

## Required validation

Inspect repository scripts, then run declared equivalents of:

```text
npm test
npm run typecheck
npm run lint
git diff --check
```

Run environment-backed tests only against the configured test environment. Record exact environment, seed IDs and cleanup evidence.

## Stop conditions

STOP if:

- an implementation defect is found; return it to `moda_architect` rather than patching another repository from system-test;
- test environment would target production merchants/provider state;
- CommerceAgent AI semantics are required to complete these ARCH-016 tests.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
