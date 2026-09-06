# ARCH-006 Translation Batching, Polling and Recovery

> Reliability companion to the canonical ARCH-006 decision:
> [`ARCH-006-merchant-communications-support-inbox.md`](ARCH-006-merchant-communications-support-inbox.md)
>
> Product-oriented summary:
> [`ARCH-006-merchant-communications-overview.md`](ARCH-006-merchant-communications-overview.md)
>
> The canonical support-inbox architecture remains authoritative for the overall
> initiative. This companion is authoritative for the detailed translation
> batching, concurrency, provider-failure, polling and reconciliation process.

## Purpose

ARCH-006 translation is deliberately asynchronous and cost-sensitive.
OpenAI Batch is the initial provider mechanism, while PostgreSQL remains the
source of truth for every translation that is still required.

The design must remain correct when any of the following happens:

- Redis is unavailable after a support message has committed;
- BullMQ delivery is lost, duplicated, delayed or failed;
- many background workers assemble translations concurrently;
- a worker crashes while assembling a logical Batch;
- OpenAI input preparation/upload fails;
- OpenAI Batch creation definitely fails;
- OpenAI may have accepted Batch creation but Moda loses the response;
- polling fails transiently;
- OpenAI finishes while Moda workers are offline;
- result processing crashes after applying only part of a Batch;
- a translation reaches a durable failed state and an administrator requests a retry.

The objective is not exactly-once execution at every network boundary. The
objective is **durable, idempotent business behaviour** with no lost required
translation and no blind duplicate provider Batch creation.

## Core reliability invariants

```text
PostgreSQL = durable ledger of required work and provider lifecycle
BullMQ     = reconstructible execution/scheduling mechanism
OpenAI     = external asynchronous provider
```

The following invariants apply:

1. A BullMQ job is never the sole evidence that a translation is required.
2. Message/translation state commits before best-effort Redis enqueue.
3. Exact BullMQ job-ID string construction is owned by
   `@modainteract/moda-interact-shared`; IDs are deterministic, collision-safe
   and colon-free.
4. Healthy existing deterministic jobs are reused.
5. Failed/stale BullMQ jobs are removed and recreated with the same logical
   shared job identity when PostgreSQL still requires the work.
6. Failed historical PostgreSQL TranslationBatch rows are retained.
7. Multiple workers may assemble work concurrently, but one translation may
   have only one current Batch assignment.
8. No Redis or OpenAI network call occurs while translation-claim row locks are
   held.
9. One logical `TranslationBatch` may have at most one accepted provider Batch.
10. An ambiguous provider-create outcome is never treated as a normal retry.
11. Provider polling is minute-scale and reconstructible from PostgreSQL.
12. Result application is idempotent per translation, not merely per Batch.
13. Durable provider-result failure is retried automatically only according to
    bounded policy; after exhaustion/non-retryable failure it requires durable
    Admin reconciliation intent.
14. Automatic recovery and Admin-triggered recovery use the same canonical
    background processors rather than separate repair implementations.
15. `merchant-communications` uses one process-level BullMQ Worker/router per worker process. Dispatch/submit/poll/results/reconcile tasks provide handlers; they do not create competing per-job-name Workers on the same queue. Every horizontal replica runs the same complete router.

## Shared-queue worker routing

The queue contract intentionally uses one queue name with multiple deterministic job names. BullMQ Workers compete for jobs at the queue level, so creating one Worker for `translation-dispatch` and another Worker for `translation-batch-submit` on the same queue would be unsafe: either Worker could receive the other's job.

Therefore:

```text
BACKGROUND-004/005/006/007 services -> processor/handler functions
BACKGROUND-007 runtime              -> one Worker(queue=merchant-communications)
                                       switch/router on job.name
horizontal replica N                -> same complete Worker/router
```

Unknown job names are rejected only by the central router after checking the complete accepted registry, not by a partial per-job Worker.

## Language decision before batching

Platform support/base language is:

```text
en-GB
```

The primary-language rule prevents wasteful English-to-English provider work:

```text
en-* merchant -> Admin        no translation row/provider work
non-English merchant -> Admin MERCHANT_TO_ADMIN -> en-GB

Admin/System -> en-* merchant no translation row/provider work
Admin -> non-English merchant ADMIN_TO_MERCHANT -> merchant snapshot
System -> non-English merchant SYSTEM_TO_MERCHANT -> merchant snapshot
```

Direction, source language and target language are persisted before provider
work. A later worker never infers direction from OpenAI output.

## Durable state

The detailed schema is owned by `ARCH-006-DATABASE-002`. Conceptually the
reliability process uses:

```text
MerchantMessageTranslation
  id
  messageId
  direction
  sourceLanguageTag
  targetLanguageTag
  status
  retryCount
  nextAttemptAt
  currentBatchId

MerchantTranslationBatch
  id
  status
  provider
  model
  providerBatchId
  inputFileId
  outputFileId
  errorFileId
  submitAttemptCount
  nextSubmitAt
  pollSequence
  nextPollAt
  failureCode

MerchantTranslationBatchItem
  batchId
  translationId
  providerCustomId

MerchantTranslationReconciliationRequest
  scope
  translationId?
  requestedByPlatformAdminId
  status
```

Historical Batch membership is preserved even when a later retry assigns a
translation to a new logical Batch. `currentBatchId` points only to the current
attempt.

`providerCustomId` belongs to one historical Batch item/provider attempt and is unique per item. A translation retried in a later logical Batch receives a new provider custom ID; result processing resolves that ID through the Batch item to the durable translation. Do not reuse one translation-stable provider custom ID across retry Batches.

## Durable acceptance flow

For a message that requires translation:

```text
request
  |
  v
PostgreSQL transaction
  +-- MerchantSupportMessage
  +-- MerchantMessageTranslation status=PENDING
  +-- immutable originalBody already persisted on message
  |
  v
COMMIT  <--- durable acceptance point
  |
  +-- best-effort deterministic translation-dispatch enqueue
  |
  v
HTTP response
```

If Redis is unavailable after commit, the translation remains `PENDING` and is
recovered from PostgreSQL later. The HTTP transaction is not rolled back merely
because Redis enqueue failed.

For inbound merchant messages, the original can be `AVAILABLE` immediately.
For Admin/System messages that require merchant-language translation, the
message remains `PROCESSING` until the required translation is `AVAILABLE`.

## Concurrent Batch assembly

Many `translation-dispatch` jobs may be consumed simultaneously. A worker must
not read a candidate page without locking and then assign rows later.

The required semantics are a short PostgreSQL transaction equivalent to:

```sql
SELECT ...
FROM MerchantMessageTranslation
WHERE status = 'PENDING'
  AND currentBatchId IS NULL
  AND (nextAttemptAt IS NULL OR nextAttemptAt <= NOW())
ORDER BY createdAt, id
FOR UPDATE SKIP LOCKED
LIMIT :batchSize;
```

The repository may use parameterised Prisma raw SQL or another proven mechanism
with the same PostgreSQL semantics.

Within the **same transaction** the assembler:

```text
1. selects one bounded stable-order set using row locks;
2. creates one logical MerchantTranslationBatch in READY;
3. creates historical MerchantTranslationBatchItem rows;
4. sets every selected translation.currentBatchId to that Batch;
5. commits.
```

Only after commit may it request the deterministic Batch-submit BullMQ job.

### Twenty-worker example

```text
Worker A -> locks eligible rows 1..N
Worker B -> SKIP LOCKED -> claims next eligible rows
Worker C -> skips A+B rows -> claims another set
...
Worker T -> claims only currently unlocked eligible rows
```

The workers may create multiple logical Batches concurrently. That is valid.
Correctness requires disjoint current membership, not one globally serial
assembler.

### Crash before commit

```text
rows locked
  -> worker crashes
  -> transaction rolls back
  -> PostgreSQL releases locks
  -> rows remain PENDING/currentBatchId=null
  -> another worker may claim them
```

### Crash after commit, before Redis enqueue

```text
TranslationBatch READY exists durably
translations point to it
submit BullMQ job is missing
  -> reconciliation later computes expected submit work
  -> adds/reuses deterministic submit job
```

No translation is returned to the unassigned pool merely because enqueue failed.

## Logical Batch submission

Provider submission is intentionally separate from Batch assembly.

```text
READY (and due)
  |
  | atomic conditional update
  v
SUBMITTING
```

Only the worker that successfully changes `READY -> SUBMITTING` may cross the
provider-create boundary. A duplicate submit job or another worker that updates
zero rows exits without provider creation.

Provider input is built from authoritative immutable PostgreSQL state. Each
provider request uses a `custom_id` that maps directly to the durable translation
ID. Provider Batch metadata carries the durable Moda TranslationBatch ID.

Where provider flow separates input-file upload from Batch creation, persist a
successful `inputFileId` before the irreversible Batch-create request and reuse
that persisted input file on a later safe retry.

## Provider-create failure classification

Not every thrown provider exception means the same thing.

### A. Definite retryable non-creation

Moda can prove no provider Batch was created, for example a known preparation
failure or explicit retryable rejection before acceptance.

```text
SUBMITTING
  -> submitAttemptCount += 1
  -> lastSubmitAttemptAt = now
  -> READY
  -> nextSubmitAt = configured minute-based retry time
```

The same logical Moda Batch is retried later. Retry timing is durable; it does
not rely on BullMQ automatic retry state.

### B. Definite terminal non-creation

Moda can prove no provider Batch was created and the failure is terminal or the
bounded submission-attempt policy is exhausted.

```text
SUBMITTING -> FAILED
```

The logical Batch history is retained. Affected translations are handled by the
bounded failure/reconciliation policy; the failed Batch row is not deleted.

### C. Successful provider creation

```text
SUBMITTING
  -> persist providerBatchId
  -> submittedAt
  -> pollSequence initial value
  -> nextPollAt = now + configured MINUTES
  -> SUBMITTED
  -> best-effort delayed poll enqueue
```

### D. Ambiguous provider creation

Example:

```text
Moda                         Provider
POST create Batch -----------> provider accepts Batch
                      X <----- response/connection lost
```

Moda cannot prove whether the provider created the Batch.

```text
SUBMITTING -> SUBMISSION_UNKNOWN
```

**Do not call provider Batch create again.**

The reconciler performs bounded provider correlation using durable Moda Batch
metadata plus the persisted input-file identity. If exactly one provider Batch
matches, adopt its provider ID and continue the normal submitted lifecycle. If
none is yet found, keep the state unresolved and reconcile again later. If
multiple candidates match, fail safe and record an operational conflict rather
than choosing one.

Provider SDK automatic retries must be disabled at the irreversible Batch-create
boundary so the SDK itself cannot secretly make a second create attempt.

## Minute-scale polling

Polling is deliberately measured in minutes.

Configuration owns values such as:

```text
TRANSLATION_BATCH_INITIAL_POLL_MINUTES
TRANSLATION_BATCH_POLL_INTERVAL_MINUTES
```

No architecture rule requires second-scale polling.

A poll job carries the durable logical Batch ID and `pollSequence`. The exact
colon-free job ID is produced by the shared helper.

```text
SUBMITTED/processing Batch
  |
  v
poll provider
  |
  +-- transient read/poll failure
  |      -> keep provider work nonterminal
  |      -> persist later nextPollAt in minutes
  |      -> advance/schedule canonical next poll as defined by processor
  |
  +-- provider still nonterminal
  |      -> update lastPolledAt
  |      -> advance durable pollSequence
  |      -> persist nextPollAt
  |      -> best-effort delayed next-poll enqueue
  |
  +-- provider completed
  |      -> persist output/error file IDs
  |      -> PROVIDER_COMPLETED
  |      -> best-effort deterministic results job
  |
  +-- provider terminal failure/expiry
         -> preserve Batch terminal state
         -> classify affected translations for bounded retry or durable FAILED
```

A transient polling failure never causes provider creation to be repeated.

## Result processing

Provider completion and Moda completion are different states.

```text
PROVIDER_COMPLETED
  -> result processing
  -> translation rows applied idempotently
  -> Batch COMPLETED only after required result processing finishes
```

Each output item maps directly to a translation through its provider
`custom_id`.

Result application checks authoritative translation/Batch membership and target
identity before applying output. A translation already `AVAILABLE` is skipped
idempotently.

### Partial crash example

```text
Batch contains tr1 tr2 tr3 tr4 tr5

worker applies tr1 -> AVAILABLE
worker applies tr2 -> AVAILABLE
worker applies tr3 -> AVAILABLE
worker crashes

replay:
  tr1 AVAILABLE -> skip
  tr2 AVAILABLE -> skip
  tr3 AVAILABLE -> skip
  tr4 pending for this result -> apply
  tr5 pending for this result -> apply
```

No successful result is duplicated and unfinished work is not abandoned.

## Provider-result retry

A known provider Batch/per-request retryable failure may return the affected
translation to a new logical attempt only within bounded automatic retry policy:

```text
failed historical Batch retained
  -> affected translation.retryCount += 1
  -> currentBatchId cleared after definite terminal classification
  -> PENDING
  -> nextAttemptAt = configured minute-based retry time
  -> later assembler claims it into a NEW logical Batch
```

A failed logical Batch is never changed back into a new provider attempt once it
has reached its historical terminal state.

When automatic retry is exhausted, or the provider failure is non-retryable:

```text
translation -> FAILED
```

Automatic periodic reconciliation does not silently reset that durable failure.
An explicit durable Admin reconciliation request is required.

## Deterministic BullMQ reconciliation

For every due unit of work PostgreSQL says should exist, reconciliation computes
the expected shared deterministic job identity and inspects BullMQ:

| Queue state | Reconciliation action |
|---|---|
| job missing | add canonical job |
| waiting | reuse existing job |
| delayed | reuse existing job |
| active | reuse existing job |
| failed | remove queue job, then recreate same logical shared job ID |
| completed and PostgreSQL says work is complete | do nothing |
| completed but PostgreSQL still requires work | remove stale queue job, recreate same logical shared job ID |

Removing a failed/stale **BullMQ job** is allowed. Removing failed historical
PostgreSQL Batch/translation audit state merely to make retry easier is not.

Poll work is versioned by durable `pollSequence`, so successive legitimate polls
have different deterministic identities while duplicate scheduling of the same
poll sequence remains idempotent.

## Startup and periodic reconciliation

Reconciliation is not itself dependent solely on a BullMQ repeat/delayed job.
The merchant-communications worker runtime performs:

```text
worker process starts
  -> initialise DB/provider/Redis dependencies
  -> run bounded startup reconciliation
  -> run normal BullMQ consumers
  -> periodically run bounded reconciliation at configured MINUTE interval
```

The exact startup ordering may follow repository runtime conventions, but Redis
must not be the only mechanism capable of scheduling reconciliation.

Reconciliation uses bounded, index-supported due queries. It does not scan all
historical completed translations/Batches.

Conceptually it repairs:

| Durable state | Required recovery |
|---|---|
| `PENDING` translation, no current Batch, due | restore translation-dispatch work |
| `READY` Batch, due | restore Batch-submit work |
| `SUBMISSION_UNKNOWN` | correlate provider state; never blind resubmit |
| `SUBMITTED`/provider-processing Batch with overdue `nextPollAt` | restore current poll work |
| `PROVIDER_COMPLETED` | restore results work |
| durable manual reconciliation request `PENDING` | process request through canonical recovery |

## Redis-loss scenario

Example:

```text
tr100 PENDING/currentBatchId=null
tr101 PENDING/currentBatchId=null
batch20 READY
batch21 SUBMITTED nextPollAt overdue
batch22 PROVIDER_COMPLETED
```

Redis loses all waiting/delayed/failed job state and the worker is restarted.
PostgreSQL still contains every required business transition.

Startup reconciliation restores:

```text
tr100 -> dispatch
tr101 -> dispatch
batch20 -> submit
batch21 -> poll
batch22 -> results
```

The outage delays translation but does not permanently lose it.

## Provider completes while Moda is offline

```text
10:00 provider Batch submitted
10:05 Moda background unavailable
10:12 provider completes Batch
10:35 Moda returns
```

PostgreSQL still has the submitted Batch with an overdue `nextPollAt`.
Startup reconciliation restores the poll job, the provider reports completion,
and normal result processing continues. No webhook is required.

## Admin-triggered reconciliation

The Admin application does not manipulate OpenAI or BullMQ directly.

A protected Admin server action creates durable intent:

```text
MerchantTranslationReconciliationRequest
  scope = TRANSLATION
  translationId = <failed translation>
  requestedByPlatformAdminId = authenticated admin
  status = PENDING
```

A SUPER_ADMIN may request bounded platform-wide failed-translation reconciliation
using the approved `FAILED_TRANSLATIONS` scope.

After the DB request commits, Admin may best-effort enqueue a reconcile hint, but
successful Redis delivery is not required for accepting the request.

```text
Admin request committed
  +-- Redis available   -> hint may accelerate processing
  +-- Redis unavailable -> request remains PENDING
                            startup/periodic reconciler later processes it
```

The background reconciler does not implement a second translation algorithm. It
restores canonical dispatch/submit/poll/results work according to durable state.

For one failed translation, reconciliation first determines whether an existing
nonterminal/current Batch lifecycle still owns it. If so, that lifecycle is
repaired instead of creating a second attempt. Only a definitively failed and
eligible translation is reset to the bounded retry path/new logical Batch.

## Failure matrix

| Failure point | Durable state | Recovery |
|---|---|---|
| DB message/translation transaction fails | nothing accepted | request fails; enqueue nothing |
| DB commit succeeds, initial Redis enqueue fails | translation `PENDING` | startup/periodic reconciliation restores dispatch |
| assembler crashes before commit | no Batch/current assignment committed | row locks release; another assembler claims later |
| assembler commits, submit enqueue fails | Batch `READY` | reconciliation restores submit job |
| duplicate submit jobs/workers | only one `READY -> SUBMITTING` claim succeeds | losers return without provider create |
| provider preparation/known retryable non-create failure | `READY` + durable nextSubmitAt/attempt count | minute-scale safe retry |
| provider create response is ambiguous | `SUBMISSION_UNKNOWN` | correlate/adopt existing provider Batch; never blind create |
| provider create succeeds, delayed poll enqueue fails | `SUBMITTED` + nextPollAt | reconciliation restores poll |
| provider poll call transiently fails | provider lifecycle remains nonterminal | durable minute-scale next poll |
| provider completes while workers offline | overdue submitted/provider-processing Batch | startup reconciliation polls and discovers completion |
| provider completion persisted, results enqueue fails | `PROVIDER_COMPLETED` | reconciliation restores results job |
| result worker crashes halfway | some translations AVAILABLE, others not applied | replay idempotently per translation |
| retryable provider-result failure | failed Batch retained; affected translation PENDING/due if retries remain | new logical Batch later |
| automatic translation retries exhausted | translation `FAILED` | explicit durable Admin reconciliation required |
| failed BullMQ execution job | DB still says work required | remove failed queue job and recreate same shared deterministic identity |

## Scaling and contention

The design intentionally permits horizontal worker scaling:

- assemblers use `FOR UPDATE SKIP LOCKED` and bounded pages rather than a global lock;
- provider calls happen outside DB row-lock transactions;
- submit ownership uses an atomic state transition per logical Batch;
- polling is keyed per Batch/poll sequence;
- result application is idempotent per translation;
- reconciliation is bounded/indexed and every repaired operation remains
  independently idempotent, so correctness does not depend on a singleton
  reconciler.

A lease may be added later only as an optimisation if redundant reconciliation
scans become expensive. It must not become the correctness mechanism.

## Runtime configuration

Architecture owns the units and semantics; deployment owns actual values.
Configuration includes concepts such as:

```text
TRANSLATION_PROVIDER
TRANSLATION_MODEL
TRANSLATION_BATCH_MAX_REQUESTS
TRANSLATION_BATCH_SUBMIT_RETRY_MINUTES
TRANSLATION_BATCH_SUBMIT_MAX_ATTEMPTS
TRANSLATION_BATCH_INITIAL_POLL_MINUTES
TRANSLATION_BATCH_POLL_INTERVAL_MINUTES
TRANSLATION_RECONCILIATION_INTERVAL_MINUTES
TRANSLATION_MAX_AUTO_RETRIES
```

Poll/retry/reconciliation cadence is minute-based. Task implementations must not
quietly replace these with second-scale loops.

## Task ownership

The detailed flow is intentionally decomposed so a Luna implementation agent
handles one bounded failure model at a time:

```text
DATABASE-002   durable translation/Batch/reconciliation state
SHARED-001     schemas + deterministic colon-free queue identities
BACKGROUND-001 provider Batch adapter and failure classification boundary
BACKGROUND-004 concurrent atomic Batch assembly
BACKGROUND-005 one-time provider submission
BACKGROUND-006 minute polling + idempotent result application + bounded provider-result retry
BACKGROUND-007 startup/periodic/manual reconciliation + worker runtime
GATEWAY-001    independently deployable worker/environment wiring
ADMIN-001      protected durable manual reconciliation command
SYSTEM-TEST-003 integrated concurrency/provider/Redis/recovery validation
```

The canonical task files remain authoritative for executable scope and current
status.
