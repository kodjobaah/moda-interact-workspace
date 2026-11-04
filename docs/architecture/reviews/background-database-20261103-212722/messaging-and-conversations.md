# Updated snapshot — messaging and conversation database review

Updated source: `moda-interact-workspace(20261103-212722).zip`.
Comparison source: `moda-interact-workspace(20261102-112817).zip`.
Prior references: MSG-01 through MSG-10 and TEMPLATE-01/TEMPLATE-02 from the initial assessment.

This is a read-only source review, including changed callers and schema contracts. Application source, tests, migrations and decisions are unchanged by this review; the patch adds review/evidence files. No dependency install, PostgreSQL/Redis/provider operation, Vitest execution, load test or EXPLAIN was performed. The updated Background checkout and its workspace ancestors have no `node_modules`; the focused tests therefore were inspected, not run. No applicable root or nested Background AGENTS.md was present. Historical pass reports in decision documents are not fresh verification by this review.

Unless a path is explicitly workspace-relative, paths and line numbers below are relative to the **updated** `moda-interact-background/` directory. Counts mean explicit ORM/raw database invocations in the stated boundary, excluding transaction-control statements, relation expansion, stored-function internals, configuration-reader internals and provider/Redis operations. They are not measured SQL counts or latency.

## Executive disposition

The update materially improves pending-turn state and handover fencing. **MSG-01 is resolved statically for newly persisted text ingress**: pending initialization now comes from a locked Conversation row inside the same transaction as message persistence and version advancement. The new repair service provides an independent queue-recovery path for valid durable recovery-AI pending turns. These improvements do **not** resolve the automated outbound moderation retry collapse (MSG-02), the reserved-message crash gap (MSG-03), or the unmatched early provider-status gap (MSG-04).

| Prior ID | Disposition | Updated assessment |
| --- | --- | --- |
| MSG-01 | **Resolved statically** | Fresh text ingress uses current row state under `FOR UPDATE`; the old stale pre-transaction pending-state decision is gone. Integration race coverage is present, but this review did not execute it. |
| MSG-02 | **Still applies** | Retryable outbound moderation still becomes a Boolean false, prepared failure and terminal turn completion. New repair excludes the completed/cleared turn. Inbound moderation retry handling remains separate and better supported. |
| MSG-03 | **Still applies** | `reserve` still suppresses every existing usage identity, including an unfinished reservation, and the processor completes the turn for that result. Repair can cause replay but does not distinguish reservation recovery states. |
| MSG-04 | **Still applies** | Provider ID is saved after provider response; a prior status lookup miss returns normally. The new pending-turn repair does not retain unmatched provider statuses. |
| MSG-05 | **Still applies** | No-context routing still normalizes `Customer.phone` in SQL; canonical phone indexes elsewhere do not change this query. Requires plans/data, not an assumed slow-query conclusion. |
| MSG-06 | **Still applies** | Full automated-message ID materialization and usage aggregation remain inside SERIALIZABLE admission. Delay and final version fencing do not bound that history query. |
| MSG-07 | **Changed scope** | Unbounded pending/history reads remain. The configurable delay of up to 30 minutes can widen the pending interval, which can extend further while processing is delayed. Early classification can revisit accumulated pending messages before the AGENT deadline. |
| MSG-08 | **Still applies** | The standalone STOP null-canonical fallback still loads and filters candidates twice. Preserve STOP locking and post-lock revalidation. |
| MSG-09 | **Changed scope / refined** | Small redundant-read opportunities remain, but some human-command rereads are after policy/moderation awaits and should remain fresh checks. New pending persistence adds an explicit locked read and separates three Conversation writes. |
| MSG-10 | **Changed scope** | Existing Shop/Conversation locks and human scans remain; a bounded per-process pending-turn poller adds documented, measurable work. Lack of a global lease and scanning future deadlines are intentional design choices, not defects. |

## 1. Durable pending state, deadline and completion

### MSG-01: what is fixed

`src/services/conversation.service.ts:133-156` still reads language/recovery context before the transaction, but it no longer decides pending initialization from that snapshot. The transaction creates the inbound message at `162-174`, then calls `recordProcessableInbound` at `176-180` before its language and monotonic clock writes (`181-195`).

`src/services/conversation-ai-delay/pending-turn-repository.ts:30-39` reads Conversation plus recovery-owned shop identity under `FOR UPDATE OF c`. Its decision uses this locked row: HUMAN handling at `54-69`, `opensPendingTurn = state.pendingTurnStartedAt === null` at `72`, optional settings capture at `74-96`, and version/pending update at `99-107`. Thus, if the previous turn completes before this lock is acquired, the new ingress sees null pending state and initializes it. If ingress acquires the lock first, the completion CAS cannot silently clear the newer inbound version. This closes the original interleaving.

The same helper is used by audio completion after an existing Conversation lock (`src/services/inbound-whatsapp-audio.service.ts:168-181`); its flag skips a second lock but still performs the joined state read. Text uses receipt time (`conversation.service.ts:96,179`); audio uses successful transcription completion time (`inbound-whatsapp-audio.service.ts:169,179`) while preserving provider event time for the conversation clocks (`182-188`).

The helper validates recovery linkage (`pending-turn-repository.ts:43-51`), reads `ShopSettings` only when opening a recovery AI pending turn, accepts missing settings as zero, and rejects malformed/out-of-range values (`74-87`). Later fragments do not rewrite the captured deadline, delay or revision (`72-105`). Merchant changes therefore affect the next pending turn, not an existing one. This is also asserted by the new source tests described below.

### Matching revision and version are now carried further

`ConversationService.claimTurn` requires observed inbound version, pending state and, when provided, AI mode/current revision/frozen revision (`conversation.service.ts:237-251`). `completeTurn` now conditionally requires the same original revision and clears all three deadline fields together with pending/processing state (`261-286`). The processor captures the frozen revision from pending state rather than rereading a new current ownership revision (`conversation-turn-processor.service.ts:289-298`). This prevents a HUMAN→AI cycle from reauthorizing old work.

The processor checks a new inbound version before AGENT reservation (`413-420`), carries `expectedInboundVersion` to delivery (`329-341`), and handles failed completion by releasing the obsolete claim and enqueueing a newer pending version (`300-320`). The final recovery send fence checks that version under its existing Shop/Conversation locks (`src/services/recovery-conversation/outbound-send-fence.service.ts:66-80,228-230`); general send does likewise (`src/services/outbound-whatsapp-admission/general-outbound-send-fence.service.ts:27-37`). Delivery forwards it to both fences (`outbound-message-delivery.service.ts:108-113,392-395,436-439`). These are correctness protections, not expendable duplicate reads.

API handover clearing was also traced: workspace-relative `moda-interact-api/src/merchant/conversations/control/service.ts:95-103` increments control revision, clears pending/deadline/processing state and advances the processed watermark together. Inbound while HUMAN also advances both inbound/processed versions and clears pending state in the shared helper. The new caller guards skip scheduling after HUMAN or no-pending results (`whatsapp-inbound-processing.service.ts:145-153,289-298`).

### Deadline placement is intentional

The pure rule is `max(frozen merchant deadline, min(last inbound + quiet window, pending start + maximum settle window))` (`conversation-ai-delay/eligibility.ts:14-17`). The processor's initial queue/claim gate still uses only quiet/max-settle (`conversation-turn-processor.service.ts:186-192,218-231,799-817`), then performs moderation, context and abuse classification. Only the AGENT path applies the merchant deadline, immediately before reserve/model work (`475-488`). AUTOMATION clarification at `438-472` deliberately bypasses the extra merchant delay.

This matches workspace-relative `docs/decisions/background/ARCH-054/BACKGROUND-002-enforce-pending-ai-deadline-and-control-fencing.md:62-65`, including its explicit permission to classify guidance before extra delay. It should not be reported as an AI-delay bypass. It does mean each early classification performs database work before being rescheduled; this belongs in MSG-07/MSG-10 measurement.

### Legacy pending turns: explicit deployment requirement, not a new MSG-01 defect

An already-pending recovery row with all `pendingAi*` fields null is not backfilled by the helper, because capture only occurs on a null `pendingTurnStartedAt`. The new processor suppresses a recovery turn with no frozen revision (`conversation-turn-processor.service.ts:389-392`); repair selects only non-null deadlines (`pending-turn-repair.ts:186`). Therefore the update is not an automatic migration/revival mechanism for old pending turns.

This is explicitly covered by the architecture rollout contract: workspace-relative `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md:144` requires old pending turns and queued jobs to be explicitly reconciled at deployment, and safe drain/invalidation before downgrade. `docs/decisions/database/ARCH-054/DATABASE-001-persist-shop-ai-delay-and-pending-deadline.md:115` calls for an explicit pending-turn drain before nonzero delay is enabled. Record deployment drain as **not verified from the source snapshot**, not as a missing implicit backfill requirement. It does not undo the fresh-ingress MSG-01 resolution.

## 2. Existing correctness findings that remain

### MSG-02: outbound moderation retry remains terminal

`src/services/conversation-moderation/moderation-assessment.service.ts:171-188,230-246` retains typed `retry` results for lease/backoff/provider retry conditions. `outbound-message-delivery.service.ts:352-358` still reduces that result to `outcome.kind === "allow" && requireCurrentAllowance(...)`. A retry becomes false, leading to `failPrepared` and `suppressed` at `104-106`. The processor still completes after the send call (`628-638`), without inspecting whether the result represented a temporary moderation condition.

Additionally, `moderation-assessment.service.ts:123-138` catches canonical/assessment/configuration recheck exceptions and returns false. That is the specific swallowed-error path; do not claim that every moderation exception is swallowed, because delivery's outer catch rethrows exceptions (`outbound-message-delivery.service.ts:359-368`).

The new repair selector requires `inboundVersion > lastProcessedVersion` and non-null pending fields (`pending-turn-repair.ts:186-190`), so it cannot recover this completed turn. Inbound moderation, by contrast, preserves `retry`, releases the turn and reschedules (`conversation-turn-processor.service.ts:344-356`). The new `DelayedError` bypass at `640` avoids treating intentional active-job rescheduling as an ordinary processing error. That improves inbound/delay orchestration but does not change outbound Boolean collapse.

Required validation remains: transient outbound moderation → no provider send, preserve retryable durable intent, retry then send once; allowance-recheck database/config failure → original error observable and no terminal business suppression. Repair alone is not this fix.

### MSG-03: pending reservation remains an indistinguishable duplicate

`src/services/outbound-whatsapp-admission/outbound-admission-reservation.service.ts:82-86` suppresses whenever the usage idempotency key exists. It creates a PENDING outbound message and UsageEvent atomically (`145-166`) but its duplicate decision does not inspect message disposition. `conversation-turn-processor.service.ts:490-503` still invokes completion for any non-admitted reservation. A crash after the reservation commits and before provider dispatch thus remains a valid unfinished-outbound scenario that replay can acknowledge as complete.

The new repair service can resurrect the versioned job after queue loss/failed job/expired lease; it does not resume the pending admission. On replay the duplicate branch above remains decisive. `findExistingAdmission` (`outbound-admission-reservation.service.ts:53-65`) is not used by this processor branch to distinguish pending, provider-admitted/unknown, sent and failed outcomes.

Also unchanged: `outbound-provider-failure.service.ts:14-18` updates FAILED and removes usage in separate operations, leaving a crash interval between them. Preserve already-admitted/unknown provider protections; do not solve replay by blindly sending an existing reservation again.

The new retained-failed-job integration test uses a miniature worker that directly claims/completes Conversation, not the actual admission+model+provider processor (`tests/integration/arch054-pending-turn-repair.integration.test.ts:151-181`). Its queue retry/deduplication assertions do not cover this reservation crash boundary.

### MSG-04: early provider status remains unretained

`outbound-message-delivery.service.ts:116-125` performs provider I/O before `markSent`; only `markSent` stores the returned providerMessageId (`477-489`). `src/services/whatsapp-provider-status.service.ts:80-106` searches by that ID and returns `unknown-message` on a miss. The worker awaits status handling then returns successfully (`src/workers/whatsapp.worker.ts:107-109`). Compensation/positive reachability explicitly skip unknown-message outcomes (`whatsapp-provider-status.service.ts:249-267`).

The new repair domain contains only Conversation/version/deadline job recovery. No unmatched-status inbox/replay was introduced in the inspected call graph. Later provider redelivery could repair the event, but no such guarantee is established by this snapshot. Preserve the conclusion as a local event-order/reconciliation gap, not proof that production necessarily loses every early status.

The upstream Messaging producer does configure `attempts: 3` with exponential backoff starting at 1,000 ms for status jobs (workspace-relative `moda-interact-messaging/app/lib/whatsapp/whatsapp-job-publisher.server.ts:54-69`). That policy applies when processing fails; an `unknown-message` normal return does not trigger it. Thus queue retries do not by themselves close the unmatched-status gap.

## 3. Query shape and repeated-work findings

### MSG-05 — same routing candidate

`src/services/recovery-routing.service.ts:126-153` still uses nested `regexp_replace(customer.phone, ...)`, joins recovery/conversation/shop and limits returned candidates to two. That result limit is not a bound on scanned rows. `CustomerPhone` canonical indexes still exist (`database/prisma/schema.prisma:307-309`), while the active query continues to use `Customer.phone`. No source evidence changes this optimisation candidate. Preserve multishop ambiguity and newest Woo generation rules when exploring an indexed canonical path. Obtain EXPLAIN with realistic distribution first.

### MSG-06 — same history-sensitive reservation

`outbound-admission-reservation.service.ts:114-132` retrieves every automated outbound message ID in the conversation, then aggregates matching usage with an IN list. It remains inside the Serializable transaction at `71-74`. Existing UsageEvent indexes at `database/prisma/schema.prisma:1632-1637` do not provide a sourceId-leading index for this query. Failed/prepared-message history may grow independently of successful usage limits. Assess join/aggregate plans, cardinality and serialization retry rate before introducing counters or indexes. Added final version fencing does not alter this materialization.

### MSG-07 — same unbounded reads, potentially wider accumulation window

Pending moderation fetches every matching inbound candidate (`conversation-moderation/moderation-turn-gate.ts:20-29`) and sequentially assesses them (`32-45`). Commerce's current-pending history query still has no `take` (`src/commerce/history.ts:69-86`), while its 32,000-character bound is applied after retrieval (`26-48`). The worker still loads all pending `inReplyToProviderId` values (`workers/whatsapp.worker.ts:221-231`) to compute `.some(...)` (`270-272`).

The new pending turn preserves its first start/deadline while subsequent fragments increase inboundVersion (`pending-turn-repository.ts:72-105`). With configured delay up to 30 minutes, these same queries can cover a much longer pending interval. Early classification before the deadline is explicitly allowed; each such classification may revisit cached moderation rows. For M eligible cached inbound items, the gate still has 2 direct outer queries plus 3 direct assessment operations per item, excluding configuration operations and stored-function internals; a fresh assessed item has 5. These are code-path counts, not network/SQL measurements.

This widens the measurement priority; it does not justify a claim of unrestricted ingress or an invented workload. Raw abuse controls still exist. Preserve all-pending moderation semantics and completion watermarks when considering pagination/work budgets; silent truncation followed by full version completion would be unsafe.

### MSG-08 — STOP fallback unchanged

`src/services/whatsapp-contact-opt-out/stop-writer.ts:36-52` still queries active canonical-match OR null-canonical candidates, with no shop predicate for standalone STOP, then filters in memory. It does this twice around stable Shop locking. No new canonical backfill/query bound was introduced. The recipient advisory lock, stable Shop order, post-lock reread, CAS updates and post-commit notices (`32-86`) are safeguards; do not remove them to save round trips. Measure null-canonical population and plans and improve the canonical path/fallback separately.

### MSG-09 — refine what can safely be carried

1. `outbound-message-delivery.service.ts:481-498` still writes Message, reads its conversationId and writes Conversation (3 calls). Returning conversationId from the first write can remove one read while retaining the transaction.
2. `recovery-outreach-attempt.service.ts:183-188` still rereads checkoutRecoveryId for engagement. If optimised, carry the identity established by the new locked helper; do not treat the old pre-transaction language read as an authoritative post-lock value.
3. Human dispatch now loads/validates immutable command ownership before evaluation (`human-command-dispatcher.service.ts:202-219`), and evaluation calls `loadClaimedCommand` again (`human-command-evaluation.service.ts:19-21`). Each successful load performs command+recovery-context queries (`merchant-send-command.service.ts:61-79`). This is an opportunity for a clearly scoped validated context, but the later context read at dispatcher `228` follows policy/moderation awaits and should not automatically be removed. Preserve the new durable follow-up claim identity validation before failure/cancellation side effects.
4. Human claim still costs 1 discovery SELECT plus N UPDATE/RETURNING calls (`merchant-send-command.service.ts:39-55`), despite the “one SQL statement” comment. Production available slots remain bounded at 4. No performance defect is implied by the misleading comment alone.
5. New text persistence separates version/pending update, language update and clock update while retaining the same Conversation lock. It is a later write-combination candidate, not a reason to drop the locked-state decision that fixes MSG-01.

## 4. Repair coverage, limits and operational checks

The production messaging entrypoint starts exactly one repair service per messaging process and includes its close handler (`src/entrypoints/messaging.ts:16-23,34-38`). The poller waits 30 seconds before its first pass and after each completed/failed pass, avoids local overlap and awaits in-flight shutdown (`conversation-ai-delay/start-pending-turn-repair.ts:9,33-69`). It intentionally has no cross-process lease. Deterministic job IDs and the processor claim CAS provide duplicate-execution protection; absence of a lease alone is not a bug.

`pending-turn-repair.ts:181-199` selects AI rows with durable deadline/start/inbound clock, unprocessed version and matching frozen/current control revision. It excludes a live ordinary processing lease. **It includes future deadlines**, then computes and publishes the remaining delay (`83-90,142-154`). This matches the task's intended repair of all durable pending scheduling, not only already-overdue rows. Existing waiting/delayed/active jobs are skipped; retained failed jobs are retried only when eligible (`147-176`).

The cursor persists across passes (`49,125`), resets only at end/empty page (`76-78,128-130`), and each pass scans at most 1,000 rows in pages of 100 (`15-16,73-75`). The index is an ordinary B-tree on `(pendingAiNotBeforeAt,id)`, **not a partial index** (`database/prisma/migrations/20261031170000_arch054_merchant_ai_response_delay/migration.sql:12-13`; schema `556`). Keyset ordering can use it, while other eligibility predicates still require filtering. A bounded return count is not proof of bounded scanned tuples; actual plans remain unmeasured.

### Cursor/error fairness and repeated retry: measurement/design limits

- On a queue operation error, the pass rethrows the original error before advancing past that candidate (`109-125`). The next pass resumes after the last successful candidate. This preserves failed work; a persistent item-specific fault would also prevent progress to later keys until it clears. The existing error test exercises one transient failure, not permanent poison-item isolation. A global Redis outage is not evidence that skipping that item would help.
- The cursor prevents permanent restart-at-first-page behavior under an older-row flood, and its unit test explicitly exercises that. Rows inserted or becoming eligible behind the current cursor wait for a wrap. Future pending rows contribute to the traversal, so repair delay depends on retained population, per-candidate Redis latency and candidate churn. Do not claim indefinite starvation from the code alone; measure wrap time and global oldest eligible pending age separately from the pass-local `oldestDueLagMs`.
- Due failed jobs reset both attempts counters (`165`). That intentionally recovers exhausted transient jobs, but there is no lifetime retry limit in this repair service. A permanently failing processor can be attempted across repeated repair cycles. Record failure-class metrics/escalation expectations and confirm policy for permanent failures; this is not proof of duplicate customer sends because downstream admission fences still apply.
- `oldestDueLagMs` is computed only over scanned candidates (`102-106`), so it is not a global oldest-due database metric.

### Narrow validation gap: null processing timestamp with a populated processing version

The repair selector accepts `processingInboundVersion IS NOT NULL AND processingStartedAt IS NULL` (`pending-turn-repair.ts:191`). The actual `claimTurn` permits a null processing version or an old processing timestamp, **but not a null timestamp paired with a populated version** (`conversation.service.ts:248-251`). With that persisted combination, a current due job can fail its claim and be delayed 250 ms repeatedly (`conversation-turn-processor.service.ts:242-280`), without becoming claimable merely through passage of time.

This combination is allowed by the nullable schema (`database/prisma/schema.prisma:534-535`) and explicitly seeded in the repair integration fixture (`tests/integration/arch054-pending-turn-repair.integration.test.ts:59-60`, index 4; asserted enqueued at `115`). That test checks enqueue, not successful processing by the real processor. However, all inspected normal Conversation writers set or clear the lease pair atomically: claim `conversation.service.ts:253-256`; completion/release `279-284,326-333`; HUMAN inbound `pending-turn-repository.ts:64-65`; API control `95-103`. No ordinary production writer creating the partial pair was found. Classify this as a **legacy/corrupt-state repair contract and end-to-end validation gap**, not a proven incident or a normal-path failure. A focused test should pass this fixture through the real claim/process boundary and settle the intended handling.

### U3 — new text-ingress lock-upgrade deadlock interleaving

Text persists its child ConversationMessage before acquiring `FOR UPDATE OF c` (`conversation.service.ts:163-180`; helper `30-39`). The baseline immediate, non-deferrable FK `ConversationMessage_conversationId_fkey` is present (`database/prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql:1258`). Two concurrent inserts with distinct providerMessageIds can each hold a compatible referenced-row KEY SHARE lock before each attempts the conflicting FOR UPDATE upgrade. Each transaction can then wait for the other. This interpretation is supported by [PostgreSQL 17 row-lock rules](https://www.postgresql.org/docs/17/explicit-locking.html#LOCKING-ROWS), [constraint timing defaults](https://www.postgresql.org/docs/17/sql-createtable.html) and the [referential-integrity implementation](https://doxygen.postgresql.org/ri__triggers_8c_source.html). This is a statically supported possible deadlock introduced by the new lock order. A deterministic PostgreSQL barrier test should reproduce the interleaving and verify that queue retry preserves both messages. Existing Promise.all coverage has no barrier forcing both inserts before both lock upgrades. This was not reproduced here and is not being promoted to a confirmed operational regression.

There is an existing retry boundary: `ConversationService.receiveMessage` logs and rethrows the original exception (`conversation.service.ts:75-89`), and the upstream Messaging producer submits inbound jobs with `attempts: 3` and exponential backoff with 1,000 ms base (workspace-relative `moda-interact-messaging/app/lib/whatsapp/whatsapp-job-publisher.server.ts:22-38`). No local transaction retry wrapper is shown, but an aborted transaction can therefore be retried by the queue. This materially limits the conclusion: the supported interleaving establishes a contention/retry defect, not evidence of a lost message or a reopened MSG-01. The future implementation should establish the intended Conversation lock before the child insert, or justify a lock mode/order that preserves current-state serialization without this upgrade cycle; that design choice needs the focused transaction test. A useful forced-barrier test would assert the expected exception/retry behavior and eventual persistence of both messages, rather than assuming no retry exists. The test needs a real PostgreSQL transaction/FK boundary; the existing concurrent test alone does not establish the interleaving.

## 5. Updated branch budgets

| Boundary/branch | Old explicit DB calls | Updated explicit DB calls | Interpretation |
| --- | ---: | ---: | --- |
| Fresh recovery text; opens pending AI turn; matching outreach engagement | 9 | **11** | Two outside reads; Message create; locked joined read; settings read; pending/version write; language write; clock write; engagement recovery read + attempt read + attempt update. |
| Fresh recovery text; joins existing pending AI turn; matching outreach engagement | 8 | **10** | Same as above without settings read. Previous helper-free code also skipped its pending initialization operation. |
| Duplicate text; matching outreach engagement | 4 | **4** | Existing message+conversation read, then three engagement operations. No automatic legacy pending backfill. |
| New helper alone: recovery AI opening | n/a | **3** | Locked joined raw read + settings read + Conversation update. |
| New helper alone: existing pending, HUMAN, or standalone opening | n/a | **2** | Joined raw read + Conversation update. HUMAN clears/acknowledges rather than schedules. |
| Audio completion transaction: successful non-stale recovery AI opening | 6 | **7** | Existing lock, stale-message check, message update, helper 3, clocks. |
| Audio completion transaction: successful non-stale joining pending | 6 | **6** | Helper 2 replaces prior version update + pending-null update. |
| Inbound caller after accepted text, before enqueue | 0 extra state read | **1 extra state read** | New AI/pending guard; enqueue's own state read remains. Audio already read state; its new guard adds no query there. |
| Successful due recovery AGENT processor, identical inner services and no races | baseline | **net +3** | Removes one fresh ownership capture; adds three ownership checks and one hasChanged read. New final-version fence compares an already selected row, adding no separate read. |
| Failed claim; same version/revision still pending | 2 before reschedule | **3 before reschedule** | State read + claim update + new current-state read. This is a race disambiguation improvement. |
| Complete-owned success | 1 | **1** | Stronger conditional UPDATE, same count. |
| Complete-owned misses because a newer pending version exists; recovery revision provided | 1 unchecked completion | **5** | Completion CAS, stale suppression CAS, release, latest-state read, enqueue's state read. A race-recovery path, not the ordinary-success budget. |
| Empty pending-repair pass | n/a | **1** | One bounded discovery SELECT. |
| Any pending-repair pass | n/a | **1–10** | 100-row pages, maximum 1,000 rows; an exact short full page can cause an empty-page query, but 1,000 cap prevents an eleventh query. No per-candidate DB mutation. |
| Human claim of N rows | 1+N | **1+N** | Still bounded by production available slots; no consolidation occurred. |
| markSent successful transaction | 3 | **3** | Message update, message read, conversation update. |

Repair also performs up to 1,000 sequential Redis `getJob` calls per pass, plus state/retry or add operations. Count those separately from PostgreSQL. With P messaging processes, a simplistic near-zero-runtime envelope is about 2P–20P repair SELECT invocations per minute; real cadence is lower when passes take time. That is a code-derived envelope, not observed load. Read/lock durations, returned/scanned rows, payload bytes and retry counts remain to be measured.

## 6. Test coverage and what it does not establish

New/changed test source inspected:

- `tests/unit/services/conversation-ai-delay/pending-turn-repository.test.ts:31-138`: recovery shop ownership/delay capture, missing settings zero, corrupt delay rejection, fragment snapshot retention, HUMAN state, standalone behavior. Database calls are mocked.
- `tests/integration/conversation-turn-scheduling.integration.test.ts:124-188`: Promise.all first text messages, one durable frozen snapshot, changed merchant setting does not rewrite pending fields. `190-227`: atomic rollback of message and snapshot. Integration tests were not run in this review.
- `tests/unit/services/conversation.service.test.ts:409-470`: frozen revision claim/completion and obsolete-revision suppression guards. `472-528` models concurrent receipts. These are not a forced real-database recreation of the old complete-between-read-and-write MSG-01 interleaving.
- `tests/unit/services/conversation-turn-processor/facade-scheduling.cases.ts:35-75`: AGENT pre-deadline release/reschedule without reserve/model, and intended immediate AUTOMATION clarification.
- `tests/unit/services/conversation-turn-processor/facade-agent-races.cases.ts:7-70`: newer-version cleanup and original version forwarding across a late ownership await; the latter asserts forwarding to a mocked admission service, not a live database/provider fence race.
- `tests/unit/services/conversation-ai-delay/pending-turn-repair.test.ts:50-90`: cross-pass cursor progress under additional older rows; `92-109`: transient enqueue failure then retry; `112-136`: retained failed job due-vs-future behavior; `139-153`: competing retry state change. No permanent per-item failure test or append-ahead saturation bound is established.
- `tests/integration/arch054-pending-turn-repair.integration.test.ts:103-136`: 10,000-row fixture/page cap, exclusion of stale ownership and active leases, deterministic queue deduplication/restart. `138-259`: retained failed job concurrent repair through a miniature worker. `261-324`: enqueue error preservation and future deadline delay. None exercises the real outbound reservation crash boundary.
- `tests/unit/services/conversation-ai-delay/start-pending-turn-repair.test.ts:10-48`: timer, error logging, local non-overlap and graceful close.

Priority next validation remains concrete fault injection for MSG-02, MSG-03 and MSG-04; a deterministic old-turn-completion/new-ingress transaction barrier for the resolved MSG-01 mechanism; real-processor consumption of the repair partial-lease fixture; and measured query plans/cardinality for MSG-05–08 plus the new repair scan. No performance threshold, actual deployment drain, provider redelivery guarantee or total workload capacity is demonstrated by this snapshot inspection.

## 7. TEMPLATE-01 and TEMPLATE-02 remain applicable

The template-translation repository and Meta template due-poller/repository/service are unchanged between the archives, and the updated messaging entrypoint still starts the existing Meta poller (`src/entrypoints/messaging.ts:23`). Their relevant caller wiring and database paths remain present.

**TEMPLATE-01:** `src/services/template-translation/repository.ts:73` still performs five fixed raw calls followed by two per claimed item during nonempty successful assembly. A full 100-item batch therefore uses 205 explicit calls in one transaction. This is bounded work and an optimisation candidate; transaction duration and lock wait have not been measured. Retain atomic claims, deterministic item identities and complete publication if combining inserts/assignments.

**TEMPLATE-02:** `src/services/meta-template-management/due-poller.ts:38` still processes 25 due registrations per cycle and schedules 60 seconds after completion. `repository.ts:23` bounds discovery; `service.ts:155` reads a registration and performs provider GET verification before recording its conditional reconciliation. There is no durable pre-GET claim on that branch. Replicas may repeat read/provider discovery; write CAS and provider-submission claims remain, so this does not establish duplicate POSTs or duplicate sends. Measure replicated work before changing scheduling, and keep provider HTTP outside database transactions.
