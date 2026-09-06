---
id: ARCH-006
title: Merchant communications, support inbox and system notifications
status: in_progress
coordinator: moda_architect
created: 2026-09-05
updated: 2026-09-06
---

# ARCH-006: Merchant communications, support inbox and system notifications

## Status

In Progress.

The architecture was refined on 2026-09-06 before `ARCH-006-DATABASE-001` was claimed. The revised design uses OpenAI Batch for translation cost, minute-scale polling rather than provider webhooks, and PostgreSQL-driven reconciliation that can reconstruct BullMQ execution after Redis loss.

`ARCH-006-DATABASE-001`, `ARCH-006-DATABASE-002`, `ARCH-006-SHARED-001/002/003/004` and `ARCH-006-BACKGROUND-001` are architect-accepted Complete. `0.7.0` remains historical; corrected `@modainteract/moda-interact-shared@0.7.1` is published and clean-consumer verified. `ARCH-006-BACKGROUND-004` and `ARCH-006-ADMIN-001` are Ready for their bounded Attempt 2 corrections, and `ARCH-006-SHOPIFY-001` is Ready for its first implementation attempt. Repository agents execute one architecture task per invocation and must return that task to Review and STOP; only `moda_architect` promotes downstream work.

Detailed translation concurrency, provider-failure and recovery mechanics are defined in [`ARCH-006-translation-batching-reliability.md`](ARCH-006-translation-batching-reliability.md). This canonical document owns the cross-domain decision; the companion owns the step-by-step reliability process.

## Problem

Moda Interact needs a durable internal support channel between each merchant Shop and Moda PlatformAdmins. It must support multilingual merchant/admin/system messages, exclusive durable Admin ownership, read/pending semantics and automated system notifications.

Translation is asynchronous and cost-sensitive. Redis/BullMQ, workers and provider calls can fail independently. A valid DB-accepted message must never remain permanently untranslated merely because enqueue/delayed work was lost. Provider Batch submission must not be duplicated merely because a queue job is delivered twice or the worker crashes around the provider create call.

## Goals

- one support thread per Shop shared by authorised Shopify staff;
- all active PlatformAdmins may read; one durable owner has exclusive administrative send authority;
- immutable source messages and separate translations;
- 1..500 user-perceived Unicode graphemes for merchant/admin authored source messages;
- `en-GB` platform support language with no wasteful English-to-English translation;
- OpenAI Batch translation for the chosen cost model;
- no OpenAI webhook/callback endpoint;
- minute-scale provider polling;
- one durable logical provider Batch submission, safe under duplicate delivery/horizontal workers;
- PostgreSQL as the durable ledger of required translation work;
- BullMQ deterministic jobs as reconstructible execution state;
- automatic startup/periodic recovery after Redis/worker loss;
- Admin-triggered durable failed-translation reconciliation through the same recovery engine;
- independently scalable merchant-communications background worker;
- tenant-safe Admin and Shopify inboxes;
- authoritative, idempotent `SUBSCRIPTION_ENDED` SYSTEM notification.

## Non-Goals

- WhatsApp transport or reuse of shopper WhatsApp conversations;
- provider completion webhooks;
- synchronous translation in user HTTP requests;
- per-message source-language LLM detection in v1; routing uses trusted language snapshots;
- attachments/rich trusted HTML;
- per-staff read receipts;
- automatic message retention/deletion policy;
- arbitrary future SYSTEM notification codes;
- translating through a tool-capable CommerceAgent.

## Current Architecture

Before this revision, ARCH-006 tasks treated translation as one broad background task with `translate-message`/`reconcile-message-translations`, 1..10,000-character UI compose and no durable provider Batch/submission/poll state. Admin/Shopify UI tasks also owned too much message/translation orchestration. Those task definitions are superseded/re-scoped before execution.

The existing platform already provides:
- Prisma/PostgreSQL repositories and `Shop`, `ShopSettings`, `PlatformAdmin`;
- ARCH-005 canonical BCP-47 merchant/admin language settings;
- BullMQ/Redis worker conventions and independently deployed background worker entrypoints;
- shared collision-safe colon-free BullMQ job-ID conventions;
- framework/shared queue-performance telemetry;
- protected Admin and Shopify authentication boundaries.

## Proposed Architecture

### Support domain

```text
Shop 1 -> 1 MerchantSupportThread -> many MerchantSupportMessage
                                      -> many MerchantMessageTranslation
```

Message kinds:

```text
ADMINISTRATIVE
SYSTEM
MERCHANT
```

Message states:

```text
PROCESSING
AVAILABLE
FAILED
```

Source content is immutable `originalBody`. Translation never replaces it.

### Base language and deterministic routing

Platform support language:

```text
en-GB
```

V1 source/target language is derived from trusted snapshots, not inferred from browser input or a pre-translation LLM:

```text
MERCHANT source        = ShopSettings.defaultLanguageTag snapshot
ADMINISTRATIVE source  = en-GB
SYSTEM source          = en-GB
display target         = ShopSettings.defaultLanguageTag snapshot when message created
```

Primary English language (`en-*`) is treated as not requiring translation to/from the platform English operational language:

```text
en-US merchant -> Admin   original only, no translation row/job
en-GB merchant -> Admin   original only, no translation row/job
fr-FR merchant -> Admin   MERCHANT_TO_ADMIN fr-FR -> en-GB

Admin -> en-CA merchant   original English AVAILABLE, no translation
Admin -> fr-FR merchant   ADMIN_TO_MERCHANT en-GB -> fr-FR, message PROCESSING until result
System -> ja-JP merchant  SYSTEM_TO_MERCHANT en-GB -> ja-JP, message PROCESSING until result
```

### Content length

Merchant/admin authored source message:

```text
1..500 user-perceived Unicode grapheme clusters
```

Both client and server validate using the shared grapheme contract. Server is authoritative. Over-length input is rejected, never truncated. Translated output may exceed 500 because language expansion is legitimate.

### OpenAI Batch choice

OpenAI is the initial provider, behind a narrow translation Batch adapter. Runtime provider/model are configuration (`TRANSLATION_PROVIDER`, `TRANSLATION_MODEL`); the coding agent model is unrelated.

Batch requests are tool-free and use `/v1/responses`. Each input line carries a `custom_id` that maps directly to the durable translation ID. Batch metadata carries the durable Moda `TranslationBatch.id` so ambiguous submission can be recovered without blind re-create.

No provider webhook is used. Moda polls provider Batch state from background jobs.

### Durable translation state

Direction is persisted before provider work:

```text
MERCHANT_TO_ADMIN
ADMIN_TO_MERCHANT
SYSTEM_TO_MERCHANT
```

Translation lifecycle:

```text
PENDING -> AVAILABLE
        -> FAILED (with explicit retry/reconciliation path)
```

Logical Batch lifecycle:

```text
READY
  -> SUBMITTING
       -> SUBMITTED
       -> SUBMISSION_UNKNOWN
  -> SUBMITTED
       -> PROVIDER_COMPLETED
       -> FAILED / EXPIRED / CANCELLED
  -> PROVIDER_COMPLETED
       -> COMPLETED after every result is durably terminal/applied
```

`SUBMISSION_UNKNOWN` means provider create may have succeeded but the worker did not safely persist the returned provider ID. It is never automatically changed back to READY for blind resubmission.

### BullMQ worker topology for the shared queue

`merchant-communications` is one BullMQ queue carrying multiple job names. Individual Background tasks own processors/handlers for their job names; they **do not** create competing per-job-name BullMQ `Worker` instances on that same queue. BullMQ workers consume from a queue rather than reserving only one job name, so separate dispatch/submit/poll/results workers on the same queue could steal and fail each other's jobs.

`ARCH-006-BACKGROUND-007` owns the process-level `merchant-communications` Worker/router. It routes by `job.name` to the accepted handlers. Horizontal scale is achieved by running multiple identical router-worker processes, each capable of handling every registered merchant-communications job name.

### Queue contracts

Dedicated queue:

```text
merchant-communications
```

Jobs:

```text
translation-dispatch
translation-batch-submit
translation-batch-poll
translation-batch-results
translation-reconcile
```

Payloads contain durable IDs/schema version only. Never message body, shop ID, admin identity or provider secrets.

Deterministic BullMQ job IDs are collision-safe and **must not contain `:`**. Poll job identity includes durable `pollSequence`; each successive provider poll therefore has a distinct deterministic identity while duplicate scheduling of the same sequence collapses.

### Redis/BullMQ invariant

```text
A BullMQ job is never the sole evidence that translation work exists.
```

PostgreSQL answers “what work is required?” BullMQ causes that work to execute.

After any DB commit, enqueue is best-effort. Failure to enqueue must not roll back or delete accepted message/translation/provider state.

### Deterministic queue reconciliation

When durable DB state says a job should exist, the reconciler computes the expected deterministic job ID and inspects BullMQ:

```text
missing                         -> add
waiting/delayed/active healthy  -> reuse
failed                          -> remove queue job + recreate same ID
completed but DB still requires -> remove stale completed job + recreate same ID
```

“Delete and retry” applies to the failed/stale BullMQ execution job, **not** to durable translation/Batch history.

### Startup and periodic self-healing

The merchant-communications worker runs reconciliation on startup and periodically using a configurable interval in **minutes**. It is a process/runtime loop, not solely another BullMQ scheduled job, so Redis loss cannot erase the only recovery trigger.

Bounded/indexed reconciliation covers:

```text
PENDING translation + no current batch       -> dispatch
READY logical batch                           -> submit
SUBMISSION_UNKNOWN                            -> provider metadata lookup; never create blindly
SUBMITTED/nonterminal + nextPollAt due        -> current-sequence poll
PROVIDER_COMPLETED                            -> result processing
PENDING due translation                       -> dispatch/recovery
PENDING admin reconciliation request          -> targeted/bounded recovery of durable FAILED translations
```

### Provider submission idempotency

Batch assembly and provider submission use two distinct concurrency controls. Batch assembly selects a bounded stable-order page of eligible translations inside a short PostgreSQL transaction using `FOR UPDATE SKIP LOCKED` (or proven equivalent), then creates Batch membership/current pointers in that same transaction. Concurrent assemblers therefore claim disjoint rows; they never hold DB row locks across Redis or provider network calls.

Submission worker then atomically claims one durable logical Batch:

```text
READY (due) -> SUBMITTING
```

Only the worker that wins the conditional update may cross the provider Batch-create boundary. Duplicate/concurrent submit jobs observe non-READY and return.

The provider Batch-create call disables SDK/BullMQ automatic retries. The provider input-file ID is persisted before the irreversible create boundary where supported. A failure proven to occur before Batch creation, or an explicit provider rejection that proves no Batch was created, may return the same logical Batch to `READY` with durable minute-based `nextSubmitAt` and bounded `submitAttemptCount`. If create outcome is ambiguous, durable state becomes `SUBMISSION_UNKNOWN`. Reconciliation scans bounded/paginated recent OpenAI Batch listings and matches both logical Batch metadata and persisted `input_file_id`; if exactly one match is found it adopts provider identity and resumes polling. If none is found it remains unknown and is revisited; multiple matches fail safe for investigation. It never blindly submits another Batch.

### Minute-scale polling

Polling cadence is environment-configurable in minutes, e.g. categories:

```text
TRANSLATION_BATCH_INITIAL_POLL_MINUTES
TRANSLATION_BATCH_POLL_INTERVAL_MINUTES
TRANSLATION_RECONCILIATION_INTERVAL_MINUTES
```

Exact operational defaults are deployment configuration, not architecture constants. No seconds-scale polling requirement exists.

A nonterminal poll transactionally advances `pollSequence` + `nextPollAt`, then best-effort enqueues the next delayed poll. If Redis loses that job, reconciliation sees overdue DB state and restores it.

### Result application

Provider completion is persisted as `PROVIDER_COMPLETED` before result processing. The result processor reads provider output, maps `custom_id` to expected Batch items, and applies each translation idempotently.

A crash halfway through a Batch is replay-safe: already AVAILABLE translations are skipped and remaining items are applied. Logical Batch becomes COMPLETED only after expected items are terminal.

Outbound ADMINISTRATIVE/SYSTEM message becomes AVAILABLE only when its required display translation is AVAILABLE. Merchant original is AVAILABLE immediately even if its admin translation fails.

### Pending Admin response boundary

Merchant message transaction:

```text
merchantMessageVersion += 1
needsAdminResponse = true
lastMerchantMessageAt = message.createdAt
```

Administrative reply snapshots:

```text
respondsThroughMerchantVersion = current merchantMessageVersion
```

When that reply becomes AVAILABLE:

```text
current version == snapshot -> needsAdminResponse=false
newer merchant version      -> remain true
```

SYSTEM never clears pending support. `readAt` never clears pending support.

### Durable Admin reconciliation request

Admin “retry translation” does not manipulate BullMQ or OpenAI. It persists a `MerchantTranslationReconciliationRequest` and may best-effort enqueue a reconcile hint. Any active PlatformAdmin may request a targeted failed-translation retry; platform-wide failed-translation reconciliation is SUPER_ADMIN-only. The background reconciler processes both through the same recovery algorithm.

A durable provider/result `FAILED` translation is not automatically re-submitted forever by the periodic scanner. Explicit reconciliation intent resets an eligible terminal failed translation to a new PENDING attempt while retaining historical Batch membership. Therefore an Admin retry request remains valid even when Redis is unavailable at click time.

## Request / Event Flow

### Non-English merchant -> Admin

```text
Merchant POST
  -> authenticate + derive Shop
  -> validate <=500 graphemes
  -> DB transaction:
       MERCHANT message AVAILABLE
       sourceLanguageTag=shop snapshot
       PENDING translation MERCHANT_TO_ADMIN -> en-GB
       merchantMessageVersion++ / pending=true
  -> commit
  -> best-effort translation-dispatch
  -> background assembles READY logical Batch
  -> deterministic submit
  -> OpenAI Batch
  -> minute delayed poll(s)
  -> PROVIDER_COMPLETED
  -> result processor -> translation AVAILABLE
```

If merchant source is English, translation row/queue/provider steps are omitted.

### Non-English merchant target <- Admin

```text
Admin POST
  -> authenticate active Admin + recheck durable owner
  -> validate <=500 graphemes
  -> DB transaction:
       ADMINISTRATIVE PROCESSING
       source=en-GB / display=<shop snapshot>
       respondsThroughMerchantVersion=<snapshot>
       PENDING ADMIN_TO_MERCHANT translation
  -> commit + best-effort dispatch
  -> Batch/poll/results
  -> message AVAILABLE
  -> clear pending only if no newer merchant version
```

If merchant target is English, message is AVAILABLE in the creation transaction and no translation is created.

### Redis loss / worker restart

```text
PostgreSQL durable states remain
   -> merchant-communications worker starts
   -> startup reconciliation scans bounded due work
   -> expected deterministic BullMQ jobs inspected
   -> healthy existing reused / missing added / failed-stale removed+recreated
   -> normal canonical processors continue
```

### Admin-triggered recovery

```text
Admin clicks Retry/Reconcile
  -> protected Admin server persists reconciliation request
  -> optional best-effort reconcile job
  -> return success even if Redis is down once DB request committed
  -> background startup/periodic reconciler claims request
  -> restores canonical deterministic work
  -> records request outcome
```

## Repository Responsibilities

| Repository | Responsibility |
|---|---|
| moda-interact-database | support/message schema; translation/Batch/reconciliation durable lifecycle + indexes |
| moda-interact-shared | canonical language/body/queue schemas and deterministic BullMQ IDs |
| moda-interact-background | OpenAI Batch adapter; batch assembly; single submission; polling/results; self-healing runtime |
| moda-interact-gateway | deploy independently scalable background worker + env/secret wiring; no webhook route |
| moda-interact-admin | protected support server capabilities, ownership/pending commands, UI, durable manual reconciliation request, queue monitor |
| moda-interact | tenant-safe merchant support server/UI; authoritative subscription-ended SYSTEM producer |
| moda-interact-system-test | integrated inbox/system/resilience validation |

## Data Model

Core:

```text
MerchantSupportThread
MerchantSupportMessage
```

Translation/recovery:

```text
MerchantMessageTranslation
MerchantTranslationBatch
MerchantTranslationBatchItem
MerchantTranslationReconciliationRequest
```

Key uniqueness/invariants:

```text
one thread per Shop
one translation per message + targetLanguageTag
one non-null SYSTEM sourceKey
one provider+providerBatchId identity
historical BatchItem membership retained
one currentBatchId pointer per translation
```

## Contracts

Owner: `moda-interact-shared`, package `@modainteract/moda-interact-shared`.

Producer/consumers:
- Admin/Shopify produce translation-dispatch/reconcile hints;
- background produces/consumes dispatch/submit/poll/results/reconcile execution;
- all validate shared schemas at runtime.

Schema version v1. Payloads are strict/minimal and body-free.

## Consistency and Transactions

- DB transaction is the durable acceptance point for support/translation state.
- Redis enqueue occurs after commit and is not correctness-critical.
- batch assembly current-claim is atomic using a bounded short PostgreSQL `FOR UPDATE SKIP LOCKED` transaction (or proven equivalent); Batch membership and `currentBatchId` commit together.
- multiple assemblers therefore claim disjoint translations without a global worker lock, and no Redis/OpenAI call occurs while row locks are held.
- provider submit starts only after atomic READY->SUBMITTING claim.
- provider create ambiguity becomes SUBMISSION_UNKNOWN.
- results are idempotent per translation.
- response-boundary pending clear is conditional on current merchant version.

## Ordering

Global translation ordering is unnecessary. Work is keyed by durable translation/Batch IDs. Message history uses stable `createdAt + id` ordering. Only response-boundary state transitions for one thread require conditional transactional coordination.

## Failure Handling

- DB unavailable: message creation fails and no queue work is emitted.
- Redis unavailable after DB commit: accepted work remains durable and reconciles later.
- provider Batch-create definite retryable non-creation: same logical Batch returns to READY with durable minute-based `nextSubmitAt` and bounded attempts.
- provider Batch-create ambiguous outcome: `SUBMISSION_UNKNOWN`, bounded metadata+input-file correlation, no blind create.
- provider poll/read transient failure: retry minute-scale; do not falsely fail translations.
- known provider Batch/per-request retryable terminal failure: affected translations retry in a new logical Batch only up to bounded automatic retry count; exhausted/non-retryable failures become durable `FAILED` and remain Admin-reconcilable.
- lost delayed poll: nextPollAt/pollSequence restore it.
- provider completes while Moda offline: overdue poll discovers completion on recovery.
- failed/stale BullMQ job: remove/recreate same deterministic identity.
- failed durable Batch/history: retained; translations may later be reassigned to a new logical Batch according to retry policy.
- partial result crash: replay per translation.

The complete failure matrix, including pre/post-commit assembler crashes, definite versus ambiguous provider-create failures, Redis-loss reconstruction and queue-state repair, is maintained in [`ARCH-006-translation-batching-reliability.md`](ARCH-006-translation-batching-reliability.md).

## Scalability

Translation is separated from raw Shopify event scaling. The new merchant-communications worker scales independently according to translation backlog/provider limits.

Batch assembly is bounded/configurable. Reconciliation uses indexed due-state queries and bounded pages; it never scans all historical AVAILABLE/COMPLETED rows. Polling is minute-scale. Deterministic job identities make multiple worker instances safe; DB CAS/unique constraints provide correctness under concurrency.

## Security

- Admin identity/role is server-derived; owner send checked in write transaction.
- Merchant Shop identity is server-derived from Shopify auth.
- SYSTEM cannot be composed from browser paths.
- message bodies are plain text and untrusted.
- translation provider has no tools/actions.
- queue payloads/log/metrics contain no body/secrets.
- OpenAI credential is deployment secret, never committed.
- raw provider prompt/response is not persisted.

## Observability

Reuse approved framework/shared queue-performance telemetry for `merchant-communications`; do not create duplicate generic metrics.

Domain outcomes may record bounded status counts/errors without message/shop/admin identifiers or free-form language labels. Stable OTel service name for deployable worker: `moda-merchant-communications-worker`; environment isolation follows existing architecture.

## Rollout / Migration

1. DATABASE-001 core support schema.
2. DATABASE-002 translation/Batch/recovery state.
3. SHARED-001 contracts -> architect acceptance -> SHARED-002 publication.
4. Background provider/assembly/submission/poll/reconciliation chain.
5. Admin and Shopify server capabilities may proceed after DB/shared publication in parallel with background chain.
6. Gateway deploys accepted background runtime.
7. Admin/Shopify UI tasks start only after their server capability and background recovery runtime are accepted; ARCH-005 UI dependencies must also be complete.
8. SYSTEM message producer integrates authoritative billing transition.
9. System-test tasks are terminal/manual-gated validation. No implementation, publication, infrastructure or other non-system-test task may depend on a system-test task. After implementation/deployment dependencies are accepted, system tests are invoked only when the developer explicitly authorises them after manual verification.

Stateless development workers may be recreated from infrastructure-as-code; PostgreSQL/Redis durable data is not implicitly disposable.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-006-DATABASE-001 | moda_database | Complete | - |
| ARCH-006-DATABASE-002 | moda_database | Complete | DATABASE-001 |
| ARCH-006-SHARED-001 | moda_shared | Complete | ARCH-005-SHARED-001, DATABASE-002 |
| ARCH-006-SHARED-002 | moda_shared | Complete | SHARED-001 |
| ARCH-006-SHARED-003 | moda_shared | Complete | SHARED-002 |
| ARCH-006-SHARED-004 | moda_shared | Complete | SHARED-003 |
| ARCH-006-BACKGROUND-001 | moda_background | Complete | DATABASE-002, SHARED-002 |
| ARCH-006-BACKGROUND-004 | moda_background | Ready — Attempt 2 correction | BACKGROUND-001, SHARED-004 |
| ARCH-006-BACKGROUND-005 | moda_background | Pending | BACKGROUND-004 |
| ARCH-006-BACKGROUND-006 | moda_background | Pending | BACKGROUND-005 |
| ARCH-006-BACKGROUND-007 | moda_background | Pending | BACKGROUND-006 |
| ARCH-006-GATEWAY-001 | moda_gateway | Pending | BACKGROUND-007 |
| ARCH-006-ADMIN-001 | moda_admin | Ready — Attempt 2 correction | DATABASE-002, SHARED-002, SHARED-004, ARCH-005-ADMIN-001 |
| ARCH-006-ADMIN-003 | moda_admin | Pending | ADMIN-001 |
| ARCH-006-ADMIN-004 | moda_admin | Pending | ADMIN-003, BACKGROUND-007 |
| ARCH-006-ADMIN-002 | moda_admin | Pending | BACKGROUND-007 |
| ARCH-006-SHOPIFY-001 | moda_app | Ready | DATABASE-002, SHARED-002, SHARED-004, ARCH-005-DATABASE-001 |
| ARCH-006-SHOPIFY-002 | moda_app | Pending | SHOPIFY-001 |
| ARCH-006-SHOPIFY-003 | moda_app | Pending | SHOPIFY-001, BACKGROUND-007, ARCH-005-SHOPIFY-002 |
| ARCH-006-SYSTEM-TEST-001 | moda_system_test | Pending | ADMIN-004, SHOPIFY-003, GATEWAY-001 |
| ARCH-006-SYSTEM-TEST-002 | moda_system_test | Pending | SHOPIFY-002, SHOPIFY-003, GATEWAY-001 |
| ARCH-006-SYSTEM-TEST-003 | moda_system_test | Pending | BACKGROUND-007, GATEWAY-001, ADMIN-001, SHOPIFY-001 |
| ARCH-006-BACKGROUND-002 | moda_background | Superseded | - |
| ARCH-006-BACKGROUND-003 | moda_background | Superseded | - |

### Execution graph

```text
DATABASE-001
    -> DATABASE-002
        -> SHARED-001 -> SHARED-002 -> SHARED-003 -> SHARED-004

SHARED-002 + DATABASE-002
    -> BACKGROUND-001

SHARED-004 + BACKGROUND-001
    -> BACKGROUND-004 -> BACKGROUND-005 -> BACKGROUND-006 -> BACKGROUND-007 -> GATEWAY-001

SHARED-004 + DATABASE-002 + ARCH-005-ADMIN-001
    -> ADMIN-001 -> ADMIN-003 -> ADMIN-004 (also waits BACKGROUND-007)

SHARED-004 + DATABASE-002 + ARCH-005-DATABASE-001
    -> SHOPIFY-001 -> SHOPIFY-002
                 -> SHOPIFY-003 (also waits BACKGROUND-007 + ARCH-005-SHOPIFY-002)

BACKGROUND-007 -> ADMIN-002

ADMIN-004 + SHOPIFY-003 + GATEWAY-001 -> SYSTEM-TEST-001
SHOPIFY-002 + SHOPIFY-003 + GATEWAY-001 -> SYSTEM-TEST-002
BACKGROUND-007 + GATEWAY-001 + ADMIN-001 + SHOPIFY-001 -> SYSTEM-TEST-003
```

## Open Questions

None blocking task creation. Operational values for Batch size and minute polling/reconciliation intervals remain environment configuration and should be selected/tested during deployment rather than embedded as architecture constants.

## Change History

- 2026-09-06: architect accepted SHARED-004 after `0.7.1` publication, registry metadata/integrity evidence and isolated clean-consumer Node-subpath execution. Returned BACKGROUND-004 and ADMIN-001 to Ready for bounded Attempt 2 corrections and SHOPIFY-001 to Ready for its first attempt. No downstream child or system-test task was promoted.
- 2026-09-06: architect review of `ARCH-006-BACKGROUND-004` exposed a broken `0.7.0` `merchant-communications/node` export, a mock test-contract defect, missing real PostgreSQL `SKIP LOCKED` concurrency evidence, and an unsafe per-job Worker pattern on the shared queue. Added SHARED-003/004 remediation, blocked affected consumers, and made BACKGROUND-007 the sole process-level `merchant-communications` Worker/router owner.

- 2026-09-06: architect independently accepted `ARCH-006-BACKGROUND-001`; advanced only `ARCH-006-BACKGROUND-004` to Ready. Added workspace-wide repository-agent hard-stop policy: one task per invocation, return to Review, no self-acceptance or downstream promotion.

- 2026-09-05: initial ARCH-006 support inbox/translation architecture and task graph.
- 2026-09-06: reduced authored source limit to 500 Unicode graphemes; established `en-GB` English-base no-translation rules; adopted OpenAI Batch for cost; removed provider webhook; added durable Batch/submission/poll state, minute polling, deterministic queue reconciliation, Admin-triggered durable recovery and independently deployable translation worker; split UI from server/back-end work and superseded cross-repository system-notification/duplicate telemetry tasks.
- 2026-09-06: architect accepted `ARCH-006-DATABASE-001`; advanced `ARCH-006-DATABASE-002` to Ready.
- 2026-09-06: architect accepted `ARCH-006-DATABASE-002`; advanced `ARCH-006-SHARED-001` to Ready because its ARCH-005 shared prerequisite is already Complete. Background/Admin/Shopify work remains gated by `ARCH-006-SHARED-002`. System tests remain terminal and require explicit developer invocation after manual verification.
- 2026-09-06: documented concurrent `FOR UPDATE SKIP LOCKED` Batch assembly, definite/ambiguous provider-create retry semantics, minute polling, partial-result replay and Redis/Admin reconciliation in the dedicated translation reliability companion.
- 2026-09-06: architect accepted `ARCH-006-SHARED-002` after publication of `@modainteract/moda-interact-shared@0.7.0`; advanced `ARCH-006-BACKGROUND-001`, `ARCH-006-ADMIN-001` and `ARCH-006-SHOPIFY-001` to Ready. System tests remain terminal/manual-gated and do not block implementation.
