---
id: ARCH-010-SYSTEM-TEST-001
architecture_id: ARCH-010
title: Validate core subscription, capacity, top-up and billing-period lifecycle
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: manual
status: pending
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-GATEWAY-001
- ARCH-010-BACKGROUND-007
- ARCH-010-BACKGROUND-009
- ARCH-010-BACKGROUND-010
- ARCH-010-BACKGROUND-019
- ARCH-010-SHOPIFY-012
- ARCH-010-SHOPIFY-020
enables:
- ARCH-010-SYSTEM-TEST-004
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SYSTEM-TEST-001: Validate core subscription, capacity, top-up and billing-period lifecycle

## Terminal/manual gate

Do **not** auto-start. This is an expensive terminal validation task. The developer explicitly invokes it only after the implementation graph above has been integrated and manually smoke-checked.

No implementation/publication/infrastructure task depends on this system-test task.

## Objective

Validate the canonical ARCH-010 merchant subscription and recovery-capacity lifecycle end to end using the real integrated application/runtime and, where required, a Shopify development/test merchant.

The final capacity order must be treated as one invariant:

```text
Paid: selected promotional -> monthly included -> purchased -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION
Free: promotional -> purchased -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION
```

No automatic paid overage exists.

## Preflight

Before changing or running test tooling:

1. read the canonical ARCH-010 architecture and implementation handoff;
2. verify every explicit dependency is `complete`;
3. inspect `moda-interact-system-test/package.json` and existing harnesses;
4. reuse existing ephemeral PostgreSQL/Redis and provider-emulator/live-evidence patterns where they fit;
5. do not invent provider responses that are supposed to be verified against Shopify App Pricing live state.

If live Shopify evidence is required, record only non-secret identifiers/timestamps/plan handles needed to prove the transition. Never persist access tokens or provider credentials in test evidence.

## Required scenarios

### A. Fresh installation and first activation

Validate both first-plan paths:

```text
new install -> NO_CONTRACT -> onboarding
new install -> first verified Free activation
new install -> first verified Paid activation
```

Prove:

- onboarding is shown before a verified plan;
- product execution is unavailable while `NO_CONTRACT`;
- the shop-lifetime Free grant is created exactly once on first verified activation whether the first plan is Free or Paid;
- replaying callbacks/reconciliation does not regrant the lifetime allowance;
- a Free activation creates/uses provider BillingPeriod scope for App Events without creating a monthly Free included-recovery counter;
- a Paid activation creates exactly one current paid BillingPeriod and included-recovery counter.

### B. Canonical capacity priority

Create deterministic balances and prove source selection in order.

Paid example:

```text
included = 2
promotional = 2
purchased = 2
lifetime Free = 2
```

Eight admitted new recoveries must consume exactly in that order; the ninth is blocked.

Free example:

```text
promotional = 2
purchased = 2
lifetime Free = 2
```

Six admitted new recoveries must consume exactly in that order; the seventh is blocked.

For every source verify reservation/commit/release idempotency and that provider billing is emitted only for the source that owns that App Event.

### C. Capacity exhaustion and recovery

Prove:

- only **new** recovery initiation is blocked by ordinary capacity exhaustion;
- already-admitted conversations continue while capacity is exhausted;
- the durable blocked-recovery reason is recorded;
- exhaustion notification is emitted once per exhaustion epoch;
- capacity restoration through a promotional grant, purchased top-up activation, remaining lifetime Free capacity, or new Paid monthly period causes eligible blocked recoveries to be reconsidered without duplicate recovery creation.

### D. Recovery top-up lifecycle on Free and Paid

For both a mapped Free subscription and mapped Paid subscription:

1. verify the exact provider/local current BillingPeriod and configured recovery-credit-pack meter;
2. request one merchant-semantic top-up;
3. prove the App Event is reported through the Shopify App Pricing meter path, not a Billing API one-time purchase;
4. prove HTTP/provider submission alone does not activate local credits;
5. reconcile provider meter quantity;
6. activate exactly one local purchase lot;
7. prove replay does not double-grant;
8. prove purchased balance survives plan/cycle transitions.

### E. Same-plan provider billing-cycle rollover

Validate both branches:

**Paid**

- pre-close drain starts at the canonical window;
- old included reservations are settled/released safely;
- unused old monthly allowance is forfeited;
- one successor BillingPeriod opens from exact provider current cycle;
- one fresh included allowance is granted exactly once;
- lifetime Free, promotional and purchased balances are preserved.

**Free**

- provider BillingPeriod rotates for App Event scope;
- no monthly Free recovery allowance is granted/reset;
- lifetime Free/promotional/purchased recovery can continue when otherwise executable;
- new top-up purchase is paused while the provider cycle is draining/unverified.

### F. Hosted plan changes

Validate at least:

```text
Free -> Paid
Paid -> Paid
Paid -> Free
```

Prove Shopify current/pending state is authoritative, HTTP callback never grants plan entitlement directly, effective transition happens once at the verified boundary, old paid remainder is forfeited, and all lifetime buckets survive.

If Shopify reports an unexpected current-plan change within the same still-open cycle, prove Moda fails closed and does not invent proration or overlapping BillingPeriods.

## Required evidence

Return one table with at least:

| Scenario | PASS/FAIL | Durable DB evidence | Queue/runtime evidence | Provider evidence | Merchant UI evidence |
|---|---|---|---|---|---|

Also record the exact integrated commits/versions exercised for every repository materially involved.

## Validation

Any harness code added in `moda-interact-system-test` must pass the repository-declared `npm test`, `typecheck`, `lint` and `git diff --check` commands that actually exist.

Live-provider/manual steps may supplement automated checks but may not replace deterministic local assertions for state transitions that are fully under Moda control.

## Non-goals

Do not validate uninstall/reinstall/freeze/cancellation here; SYSTEM-TEST-002 owns those. Do not validate partial refunds or campaign-grant Admin workflows here; SYSTEM-TEST-003 owns those.

Do not change production implementation to make the test pass. Implementation defects return to `moda_architect` as Changes Requested against the owning task.

## Stop conditions

STOP and report instead of guessing if:

- Shopify test-store/App Pricing state cannot represent the required scenario;
- provider plan/meter configuration differs from the architecture;
- an explicit implementation dependency is not complete;
- test execution would require exposing provider secrets;
- observed provider behaviour makes a documented ARCH-010 safety branch a normal provider path.

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
Populate canonical isolated worktree/branch/commit/push evidence if test harness code changes.

### Architect Review
Manual terminal gate; pending developer/architect acceptance.
