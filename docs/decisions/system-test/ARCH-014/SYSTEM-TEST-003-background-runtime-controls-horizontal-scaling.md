---
id: ARCH-014-SYSTEM-TEST-003
architecture_id: ARCH-014
title: Validate runtime controls and horizontal-scaling convergence end to end
task_kind: validation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: manual
status: ready
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-DATABASE-004
- ARCH-014-BACKGROUND-001
- ARCH-014-BACKGROUND-002
- ARCH-014-BACKGROUND-003
- ARCH-014-BACKGROUND-004
- ARCH-014-BACKGROUND-005
- ARCH-014-ADMIN-009
enables: []
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-SYSTEM-TEST-003

## Objective

Prove that Admin runtime-control changes are durable, audited and safe under horizontally scaled Background/Admin execution.

This is a terminal developer-gated test. Do not run automatically from an implementation agent.

## Environment

Use one PostgreSQL database and one Redis instance shared by all test processes.

Run at least two independently constructed Background process/service instances for concurrency scenarios. Prefer separate Node processes where the existing system-test harness supports it; separate service instances are acceptable only for deterministic lease unit/integration portions.

Do not fake horizontal scaling by invoking the same singleton twice in one call stack for the terminal queue-global-concurrency scenario.

## Scenario A — optimistic Admin mutation

Start with config version `N`.

Issue two concurrent mutations carrying:

```text
expectedVersion = N
```

from independent request contexts.

Required:

```text
exactly one succeeds
resulting version = N + 1
exactly one BackgroundRuntimeConfigAuditEvent is created
loser returns the exact concurrency conflict
winner values remain authoritative
```

Repeat using two different tabs to prove there is still no silent field merge.

## Scenario B — global billing scheduler

Run at least two billing scheduler instances against the same lease table.

Required:

```text
only one BILLING_RECONCILIATION lease winner performs a cycle
other replica skips
heartbeat keeps ownership during a cycle > initial heartbeat period
```

Kill/stop the lease owner without release; after expiry another instance must acquire with higher generation.

A stale old handle must fail heartbeat/release.

## Scenario C — live interval change

Start billing interval at 60s, then Admin-save 15s.

Required:

- no worker redeploy;
- config version propagates;
- waiting scheduler reschedules;
- no overlapping global cycle;
- cycle begun on old version completes without mid-cycle mutation;
- next cycle uses new version.

Repeat conceptually for recovery repair and translation reconciliation with shorter test-friendly injected clocks/timers rather than waiting production durations.

## Scenario D — batch/throughput controls

Change and prove:

```text
billing shops per cycle
Shopify usage publish batch
recovery shops per repair
recoveries per resume job
translation reconciliation page size
translations per provider batch
```

The exact configured bound must reach the service query/processing boundary.

## Scenario E — translation retry separation

Set:

```text
translationPollIntervalSeconds = 120
translationResultRetrySeconds = 30
```

Prove provider polling uses 120 and failed result application uses 30.

No migrated translation tuning environment variable may override DB state.

## Scenario F — messaging settle controls

With two messaging replicas:

1. set quiet window 3000 / max settle 10000;
2. save quiet window 1000;
3. wait for runtime-config convergence (maximum normal refresh window plus test tolerance);
4. send subsequent turn.

Prove later turns use 1000 without restart.

Existing in-flight/finished turn is not retroactively changed.

## Scenario G — abuse protection

Lower one sender limit using Admin.

After config convergence, prove requests through more than one messaging replica share Redis counters and enforce the committed limit.

Redis outage remains fail-closed.

Prove fixed one-minute/ten-minute windows did not become editable/change.

## Scenario H — fleet-wide BullMQ concurrency

For a controlled queue, run at least two Worker instances sharing Redis.

Configure global concurrency `4`.

Queue enough blocking jobs to exceed four.

Required:

```text
aggregate active jobs across both workers <= 4
```

Admin-save `2`.

Allow already active jobs to finish; prove subsequent aggregate active work converges to <=2 without worker restart.

Admin-save `6`; prove aggregate may rise to <=6.

A stale config replica must not revert Redis to an older cap after the newer DB version exists.

## Scenario I — runtime-config read outage

After successful initialization, make config refresh reads fail temporarily.

Required:

- workers continue with last-known-good;
- no default reset;
- no version regression;
- after DB recovery, latest higher version is adopted.

Initial startup with no readable/missing singleton must fail readiness.

## Scenario J — UI usability

Verify Admin Controls contains:

```text
Operational
Advanced
Abuse Protection
```

and grouped Setting / Value / Purpose-Guidance tables.

Verify:

- fleet-wide wording is present for queue concurrency;
- every row shows default/range;
- system-managed settings are not editable;
- merchant recovery delay is not duplicated as a global control;
- raw technical env names are not primary labels;
- stale save displays exact concurrency message.

## Evidence required

Completion report must include:

```text
database migration/config version evidence
audit-event evidence
lease generation/owner evidence
multi-process or multi-worker evidence
BullMQ global concurrency evidence
Admin screenshots or DOM assertions for each tab
commands/tests executed
any environment limitations
```

## Pass condition

All scenarios A-J pass.

Any lost update, duplicate global reconciliation run while a valid lease is held, stale global-concurrency reversion, or Admin-editable system-managed invariant is a task failure.
