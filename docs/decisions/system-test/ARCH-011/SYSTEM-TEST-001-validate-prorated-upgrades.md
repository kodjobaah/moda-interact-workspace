---
id: ARCH-011-SYSTEM-TEST-001
architecture_id: ARCH-011
title: Validate integrated ARCH-011 upgrades and deferred downgrades
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-DATABASE-002
- ARCH-011-SHARED-002
- ARCH-011-BACKGROUND-001
- ARCH-011-BACKGROUND-002
- ARCH-011-BACKGROUND-003
- ARCH-011-SHOPIFY-002
- ARCH-011-ADMIN-002
enables: []
created: 2026-09-14
updated: 2026-09-14
---
# ARCH-011-SYSTEM-TEST-001

## Manual execution gate
Do not auto-run. Developer must explicitly claim after all dependencies are integrated/deployed to the Render test environment and a native Shopify App Pricing development/test store is available.

## Authorized implementation surface
```text
src/arch011-prorated-upgrades.js                 # new
scripts/run-arch011-prorated-upgrades.js         # new
test/arch011-prorated-upgrades.test.js           # new
docs/arch011-prorated-upgrades-evidence.md       # generated/updated evidence
package.json                                     # only add validate:arch011-prorated-upgrades script
```

## Required scenarios — all must record PASS/FAIL with provider/local evidence
1. native App Pricing succeeds with null legacySubscriptionId;
2. canonical Free->Starter->Growth->Scale topology/direct skips;
3. Moda requested Scale, Shopify selected Growth => Growth applied, Scale preserved as intent;
4. callback withheld => scheduled reconciliation still applies upgrade;
5. provider-observed higher plan with no request reconciles;
6. half-cycle 100->300 => target200/delta100 independent of usage;
7. repeated upgrades use complete segment history;
8. event timestamp, not worker/callback time, is boundary;
9. event at cycle start => boundary/full-opening not proration;
10. null currentBillingCycle/trial => no proration;
11. Paid->Free remains current paid + pending Free until boundary;
12. higher-paid->lower-paid remains current higher + pending lower until boundary; **if Shopify instead makes lower current same-cycle, FAIL and block production acceptance**;
13. REQUESTED expiry => FAILED/REQUEST_NOT_CONFIRMED and later provider upgrade recoverable;
14. missing event => NEEDS_ATTENTION then exact event recovery;
15. unresolved old-cycle evidence => FAILED at rollover, no invented timestamp;
16. PROVIDER_CONFIRMED/NEEDS_ATTENTION blocks new paid-meter recovery and top-up; REQUESTED+provider-still-source does not;
17. duplicate event/reconciler and reservation races do not duplicate grant/stale UsageEvent;
18. ARCH-010 purchased/promotional/lifetime-Free/capacity-order regressions remain unchanged.

## Commands
```text
npm test
npm run typecheck
npm run lint
npm run validate:render:test
npm run validate:arch011-prorated-upgrades
```
No non-system-test task may depend on this task. On any provider-behaviour mismatch, record FAIL and return to architect; do not patch production code from system-test task.

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
