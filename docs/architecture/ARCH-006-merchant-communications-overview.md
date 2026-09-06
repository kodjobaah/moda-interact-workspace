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
    |
    v
DATABASE-002  COMPLETE
    |
    v
SHARED-001    COMPLETE
    |
    v
SHARED-002    COMPLETE / published 0.7.0
    |
    +--> SHARED-003 READY   (correct broken Node export)
            |
            v
         SHARED-004 PENDING (publish + clean-consumer verify 0.7.1)
            |
            +--> BACKGROUND-004 BLOCKED
            +--> ADMIN-001      BLOCKED
            +--> SHOPIFY-001    BLOCKED
```

`SHARED-002`/`0.7.0` remain historical. SHARED-003 corrected the Node export and SHARED-004 published `@modainteract/moda-interact-shared@0.7.1`, then proved the exact registry artifact from a clean consumer. The three affected consumer tasks are now released by `moda_architect`; downstream children remain dependency-gated. `BACKGROUND-001` remains Complete. System tests remain terminal/manual-gated and do not block implementation.

## Luna-sized task decomposition

The previous broad translation/UI tasks are replaced by stable capability boundaries:

```text
DATABASE-001 core support schema
DATABASE-002 translation/Batch/recovery schema
SHARED-001 validation + queue contracts
SHARED-002 publish 0.7.0
SHARED-003 correct Node export
SHARED-004 publish/consumer-verify 0.7.1

BACKGROUND-001 provider adapter
BACKGROUND-004 batch assembly
BACKGROUND-005 one-time provider submission
BACKGROUND-006 polling + result application
BACKGROUND-007 reconciliation + deployable worker runtime
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
