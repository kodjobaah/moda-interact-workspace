---
id: ARCH-003-QUEUE-OVERVIEW-READINESS-AMENDMENT
title: Tenant Directory queue overview readiness and unavailable-state amendment
architecture_id: ARCH-003
status: agreed
coordinator: moda_architect
created: 2026-09-04
updated: 2026-09-04
---

# ARCH-003 queue overview readiness and unavailable-state amendment

## Decision

A separate bounded Admin correction task is introduced for the Tenant Directory
queue overview cards:

`ARCH-003-ADMIN-008`

The currently executing `ARCH-003-ADMIN-002` task is not modified or expanded.

The revised local execution sequence is:

```text
ARCH-003-ADMIN-002
        |
        v
ARCH-003-ADMIN-008
        |
        v
ARCH-003-ADMIN-003
```

`ARCH-003-ADMIN-003` is therefore amended to depend on `ARCH-003-ADMIN-008`.

## Observed issue

The four queue KPI cards on `Tenant Directory` render `Unavailable` even though
Admin has already demonstrated working Redis/BullMQ connectivity through the
existing detailed queue monitor.

Inspection of the accepted ADMIN-001 implementation shows that the overview
creates BullMQ `Queue` readers with bounded fail-fast settings including:

```text
lazyConnect: true
enableOfflineQueue: false
maxRetriesPerRequest: 1
skipWaitingForReady: true
```

and immediately calls:

```text
getJobCounts('active')
```

A cold queue connection can therefore be asked to execute before its Redis
connection is ready. With offline queuing deliberately disabled, that initial
read can fail and the overview correctly-but-unhelpfully maps the failure to
`Unavailable`. The observed server error `Stream isn't writeable and
enableOfflineQueue option is false` is consistent with this path.

The unavailable fallback also has a confirmed presentation defect: the word
`Unavailable` is rendered with oversized KPI value styling and can flow outside
of its card into neighbouring layout space.

The architecture does not authorise reverting to indefinite/offline queued
Admin HTTP behavior.

## Required correction direction

The overview reader should establish BullMQ queue readiness before issuing its
active-count command, while preserving the existing bounded/fail-fast Admin
connection policy.

The readiness wait itself must remain bounded by the existing queue-operation
timeout contract.

When Redis is genuinely unavailable, the UI must continue to show an honest
`Unavailable` state, but that non-numeric status must use a compact responsive
style that remains inside the card. Healthy numeric active counts retain their
existing KPI emphasis.

Do not:

- set `maxRetriesPerRequest: null`;
- enable indefinite reconnect/request waiting;
- re-enable an overview-only raw ioredis reader;
- modify worker connection policy;
- hide a genuinely unavailable Redis service by returning fabricated zeroes.

## Scope boundary

This amendment is confined to `moda-interact-admin` and the Tenant Directory
queue overview read path.
