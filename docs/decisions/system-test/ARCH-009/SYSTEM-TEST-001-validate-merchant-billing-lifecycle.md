---
id: ARCH-009-SYSTEM-TEST-001
architecture_id: ARCH-009
title: Validate merchant billing lifecycle, cancellation and refund scenarios
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
  - ARCH-009-SHOPIFY-001
  - ARCH-009-BACKGROUND-001
  - ARCH-009-BACKGROUND-002
  - ARCH-009-ADMIN-001
  - ARCH-009-ADMIN-002
  - ARCH-009-ADMIN-003
enables: []
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-009-SYSTEM-TEST-001

## Terminal/manual gate

Do not auto-start.

Developer explicitly invokes after manual verification.

## Scenario A — Free -> paid -> Free

```text
Free=5
consume3
remaining2
upgrade paid via hosted pricing
Free remains durable2 but unused
schedule paid->Free
paid remains current until effective
Free becomes current
remaining2
```

Also full cancellation -> NO_CONTRACT, not Free.

## Scenario B — purchased credits across renewal

```text
exhaust paid included
activate pack
partly consume
new billing period
fresh included capacity used first
purchased unchanged
after included exhaust, purchased resumes
```

## Scenario C — cancellation

Merchant request -> REQUESTED END_OF_CYCLE/no provider call.

SUPER_ADMIN approval.

Background exact Partner booleans, one call, PROVIDER_ACCEPTED.

Provider cancelAtPeriodEnd -> COMPLETED.

Immediate mode -> provider null -> NO_CONTRACT.

Old request + replacement subscription -> no cancellation against replacement,
NEEDS_ATTENTION.

## Scenario D — full-pack refund

Insufficient available -> approval denied.

Correction mode:

```text
hold
purchase ACTIVE
one -1
REPORTED not completion
human confirmation
finalization
granted -= pack
refunding -= pack
purchase REFUNDED
```

Replay no double decrement.

Dashboard mode:

```text
hold
no -1
human provider confirmation
exactly-once finalization
```

## Scenario E — upgrade/downgrade/support

Change plan/Switch to Free -> Shopify hosted pricing.

Merchant support asks upgrade -> Admin sends /app/billing Change plan CTA, no
Subscription mutation.

## Generic guard

Generic pack correction rejected/no event.

## Security

ADMIN triage only.

SUPER_ADMIN approve/confirm.

Cross-shop rejected.

No provider credentials in browser/log evidence.

## Final matrix

| Scenario | Result | Evidence |
|---|---|---|
| Free -> paid -> Free | PASS/FAIL | ... |
| Purchased credits across renewal | PASS/FAIL | ... |
| Cancellation | PASS/FAIL | ... |
| Refund | PASS/FAIL | ... |
| Upgrade/downgrade + support | PASS/FAIL | ... |
| Generic correction guard | PASS/FAIL | ... |

All PASS required.

## Stop

Return evidence and STOP.
