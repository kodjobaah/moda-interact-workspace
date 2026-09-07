# ARCH-006 Merchant Communications — Revised Execution Overview

> Companion to the canonical architecture: [`ARCH-006-merchant-communications-support-inbox.md`](ARCH-006-merchant-communications-support-inbox.md).
> Detailed batching/concurrency/failure/recovery process: [`ARCH-006-translation-batching-reliability.md`](ARCH-006-translation-batching-reliability.md).
> The canonical architecture and individual task YAML state are authoritative.

## Core product rules

- one support thread belongs to one Shop and is shared by its authorised Shopify staff;
- all active PlatformAdmins may read; one durable PlatformAdmin owner has exclusive administrative-send authority;
- source messages are immutable and translations are separate;
- merchant/admin authored source messages are plain text, **1..500 user-perceived Unicode graphemes**;
- platform support/base language is `en-GB`;
- English (`en-*`) to/from platform English does not create translation work;
- non-English translation uses OpenAI Batch asynchronously for the chosen cost model;
- provider completion is polled in **minutes**; there is no OpenAI webhook;
- PostgreSQL owns required translation state; BullMQ jobs are reconstructible execution hints;
- deterministic queue IDs are reused while healthy and failed/stale queue jobs are removed/recreated with the same logical ID;
- failed durable DB Batch/translation history is retained;
- worker startup + periodic reconciliation rebuilds work after Redis loss;
- Admin “Retry translation” creates durable reconciliation intent and uses the same background recovery engine; SUPER_ADMIN can request bounded platform-wide failed-translation reconciliation.

## Translation flow

```text
merchant/admin/system server transaction
        |
        +-- original message
        +-- required PENDING translation (only if language differs by architecture rule)
        |
        v commit
best-effort translation-dispatch
        v
background batch assembly -> READY
        v
atomic READY -> SUBMITTING
        v
OpenAI Batch create exactly once
        v
SUBMITTED + nextPollAt (minutes)
        v
BullMQ delayed poll
        +-- non-terminal -> advance durable pollSequence/nextPollAt -> next delayed poll
        +-- completed -> PROVIDER_COMPLETED -> result processor
        v
translation AVAILABLE -> outbound message AVAILABLE when required
```

## Recovery flow

```text
worker starts / periodic minute interval / durable Admin reconciliation request
        v
query bounded due PostgreSQL state
        v
compute expected deterministic BullMQ job
        |
        +-- missing -> add
        +-- waiting/delayed/active -> reuse
        +-- failed -> remove + recreate same ID
        +-- completed but DB still requires work -> remove + recreate same ID
```

`SUBMISSION_UNKNOWN` is special: search provider metadata for the existing logical Batch and adopt it. Do **not** blindly create another provider Batch.

The detailed companion defines the PostgreSQL `FOR UPDATE SKIP LOCKED` batch-claim transaction, provider failure classes, deterministic queue repair table, partial-result replay and Admin-triggered recovery.

## Current execution state

```text
DATABASE-001  COMPLETE
DATABASE-002  COMPLETE
SHARED-001    COMPLETE
SHARED-002    COMPLETE / published 0.7.0 (historical)
SHARED-003    COMPLETE
SHARED-004    COMPLETE / published + clean-consumer verified 0.7.1
BACKGROUND-001 COMPLETE
BACKGROUND-004 COMPLETE / real PostgreSQL concurrency validated
BACKGROUND-005 READY

parallel quality-infrastructure chain:
SHARED-005 READY -> SHARED-006 PENDING -> BACKGROUND-008 PENDING

ADMIN-001   READY / Attempt 3 bounded correction (non-English response boundary)

Attempt 2 Admin review found early pending-response clearing for PROCESSING non-English replies; BACKGROUND-006 remains the owner of the eventual AVAILABLE transition and response-boundary clear.
SHOPIFY-001 READY / first attempt
```

The disposable integration-test chain is intentionally parallel and non-gating. It standardises repeatable PostgreSQL/Redis integration testing but does not prevent BACKGROUND-005, Admin, Shopify or other implementation work from proceeding. System tests remain terminal/manual-gated.

### Shared disposable integration-test substrate

Reusable disposable PostgreSQL/Redis lifecycle belongs in the Node-only testing boundary of `@modainteract/moda-interact-shared`, not in the manual-gated `moda-interact-system-test` repository and not in the database repository. The database repository remains sole owner of Prisma schema/migrations. Consumers pass the authoritative schema path (normally their `database/prisma/schema.prisma` submodule path) to the shared harness, which starts fresh containers, runs `prisma migrate deploy`, exposes test URLs, executes consumer integration work, and always cleans up.

The existing `moda-interact-system-test/src/ephemeral-postgres.js` and `ephemeral-redis.js` are useful prior art, but application repositories must not acquire a dependency on the system-test repository. SHARED-005 promotes the reusable mechanism into a normal Node-only package surface; SHARED-006 publishes it; BACKGROUND-008 adopts it.

## Luna-sized task decomposition

The previous broad translation/UI tasks are replaced by stable capability boundaries:

```text
DATABASE-001 core support schema
DATABASE-002 translation/Batch/recovery schema
SHARED-001 validation + queue contracts
SHARED-002 publish 0.7.0
SHARED-003 correct Node export
SHARED-004 publish/consumer-verify 0.7.1
SHARED-005 disposable PostgreSQL/Redis + migration test harness
SHARED-006 publish reusable testing subpath

BACKGROUND-001 provider adapter
BACKGROUND-004 batch assembly
BACKGROUND-005 one-time provider submission
BACKGROUND-006 polling + result application
BACKGROUND-007 reconciliation + deployable worker runtime
BACKGROUND-008 adopt disposable integration-test harness (parallel/non-gating)
GATEWAY-001 Render worker/env wiring

ADMIN-001 server support capability
ADMIN-003 ownership/pending server capability
ADMIN-004 support UI
ADMIN-002 queue-monitor extension

SHOPIFY-001 server support capability
SHOPIFY-002 subscription-ended producer
SHOPIFY-003 merchant Messages UI

SYSTEM-TEST-001 inbox/security/language
SYSTEM-TEST-002 system notification
SYSTEM-TEST-003 Batch/recovery resilience
```

This is intentionally finer than the original plan, but not file-level/microscopic: each implementation task has one independently reviewable runtime or product outcome and a clear stop condition.
