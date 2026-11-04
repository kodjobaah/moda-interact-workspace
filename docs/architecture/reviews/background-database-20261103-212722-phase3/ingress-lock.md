# U3: inbound message foreign-key lock upgrade

## Decision and evidence status

**Recommend acquiring the existing Conversation lock before inserting the inbound ConversationMessage.** The smallest implementation is to move the existing call to `recordProcessableInbound(tx, conversationId, receivedAt)` above `tx.conversationMessage.create` within the same interactive transaction. Its version/pending mutation stays in that transaction. This adds no call site, leaves the successful distinct-message call count unchanged, needs no migration, preserves the lock mode already used by the helper, and preserves the current pending-turn calculation. A failed INSERT can now follow helper work that the current ordering would not have performed; that work must roll back.

This is a source-supported concurrency defect and a proposed correction, **not an executed application regression or implemented fix**. The updated source snapshot is `moda-interact-workspace(20261103-212722).zip`. No PostgreSQL server/client, Docker, Podman, or PostgreSQL Python driver is available in this review environment. No existing database was contacted, credentials were not read, and no dependency was installed. The accompanying PostgreSQL 17 protocol is deliberately unexecuted.

Paths below are workspace relative. `BG` means `moda-interact-background`, `DB` means `moda-interact-database`.

## 1. Actual transaction boundary

The processable text path currently follows this order:

| Phase | Operation | Evidence |
| --- | --- | --- |
| Before receive | STOP/abuse/routing checks; active recovery external-activity update | `BG/src/services/whatsapp-inbound-processing.service.ts` |
| Before transaction | Sample receipt time; read message by unique provider ID, including Conversation projection | `BG/src/services/conversation.service.ts:96-116` |
| Duplicate shortcut | Check Conversation ownership, mark outreach engaged, return current Conversation version with duplicate=true | Same file, 118-130 |
| Before transaction | Read Conversation language/recovery context; resolve initial language | Same file, 133-156 |
| Transaction, step 1 | Insert INBOUND/CUSTOMER/DELIVERED child message | Same file, 162-174 |
| Transaction, step 2 | Read joined Conversation/recovery context with `FOR UPDATE OF c` | `BG/src/services/conversation-ai-delay/pending-turn-repository.ts:30-39` |
| Transaction, step 3 | If opening a recovery AI turn, read current delay setting; update version/pending fields; HUMAN mode clears AI work and advances processed version | Same helper, 54-108 |
| Transaction, step 4 | Write language from the pre-transaction resolution | `conversation.service.ts:181-188` |
| Transaction, step 5 | Update both Conversation clocks with GREATEST; commit | Same file, 190-197 |
| After commit | Mark outreach engaged | Same file, 199-202 |
| Outside receive | Reachability, current-route check, current turn-state check, and enqueue | `whatsapp-inbound-processing.service.ts:262-304` |

No outer transaction in the inspected ingress caller retains the earlier activity/route writes across `receiveMessage`. Network/Redis enqueue occurs outside the message transaction. Unsupported active inbound content also calls this receive method, so the lock-order issue is not exclusive to text. Historical text and audio reservation use separate child inserts without the later parent upgrade in that transaction.

The pre-read does not serialize writers. Worker configuration is concurrency-bound, not a per-Conversation receive mutex: `whatsapp.worker.ts:95-98,125` delegates inbound jobs and binds configured concurrency; `DB/prisma/schema.prisma:3319` defaults that configuration to 20. The normal producer's job identity is based on providerMessageId, so two different messages for one Conversation remain different jobs.

## 2. Why the FK matters

The baseline creates `ConversationMessage_conversationId_fkey` against Conversation(id), with ON DELETE/UPDATE CASCADE and no DEFERRABLE clause (`DB/prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql:1258`). Its providerMessageId uniqueness is at line 924. The migration chain inspected for this review does not replace that FK with a deferred one.

PostgreSQL's immediate FK check uses a referenced-row KEY SHARE lock. KEY SHARE permits another KEY SHARE but conflicts with FOR UPDATE; FOR NO KEY UPDATE permits KEY SHARE and conflicts with another FOR NO KEY UPDATE. Locks survive until transaction end. PostgreSQL detects a circular wait by aborting a participant; the victim identity is not a stable test expectation. These statements follow the [PostgreSQL 17 lock documentation](https://www.postgresql.org/docs/17/explicit-locking.html#LOCKING-ROWS), [PostgreSQL 17 constraint timing defaults](https://www.postgresql.org/docs/17/sql-createtable.html), and [the PostgreSQL referential-integrity implementation](https://doxygen.postgresql.org/ri__triggers_8c_source.html). The source-browser page is explicitly git master, not a pinned PostgreSQL 17 source checkout; the supplied executable protocol targets PostgreSQL 17.

For distinct provider IDs, the supported schedule is:

| Step | Receive A | Receive B |
| --- | --- | --- |
| 1 | INSERT child A finishes; retains parent KEY SHARE | |
| 2 | | INSERT child B finishes; retains parent KEY SHARE |
| 3 | Requests parent FOR UPDATE; waits for B | |
| 4 | | Requests parent FOR UPDATE; waits for A |
| 5 | One transaction is aborted; the other can proceed | Victim is intentionally unspecified |

This is an inference from the source order and PostgreSQL rules. It is not evidence that production has experienced this schedule. A deadlock victim loses the whole transaction, including its inserted message. The successful transaction does not commit the victim's version or pending fields.

### Trigger audit

No inspected current application trigger acquires the intended strong Conversation lock before the inbound INSERT:

- `20261022215000_arch045_general_conversation_dispatch_admission/migration.sql:11-33` replaces the message-dispatch guard. New inbound rows have no providerDispatchKey; its admission branch is inactive. Even its outbound check uses a plain EXISTS, not FOR UPDATE.
- `20261017120000_arch040_recovery_human_handover/migration.sql:183-207` guards ownership/control updates. Normal version, pending, language and clock updates do not change ownership/control and do not take a Shop row lock.
- The deferred Conversation transition trigger in that migration, lines 250-253, is conditional on a control-mode change. It does not fire for these ordinary ingress updates. Its deferred event consistency reads are also not an earlier parent lock.
- `20260920182429_arch020_commerce_capability_releases/migration.sql:577` scopes the Conversation owner trigger to checkoutRecoveryId/shopId updates; the ingress writes do not update those columns.

The standalone fixture omits these triggers because they do not remove this interleaving on the inspected branch. That omission prevents the fixture from being presented as a full-schema/application test.

## 3. Relevant writer order

“Before” below means within one transaction unless the row explicitly says otherwise. Plain joined reads are distinguished from row locks.

| Writer | Lock/write order and boundary | Implication for U3 |
| --- | --- | --- |
| Current processable text / unsupported active ingress | New message INSERT → parent FK KEY SHARE → Conversation FOR UPDATE → non-key Conversation writes | Two receivers can perform the conflicting upgrade |
| Proposed processable ingress | Conversation FOR UPDATE and pending/version write → new message INSERT → remaining Conversation writes | Serializes before child FK acquisition; keeps current helper semantics |
| Audio reservation | Standalone child INSERT commits; later download/transcription is outside the completion transaction | Its FK lock is not retained across the later parent lock |
| Audio completion | Conversation FOR UPDATE → stale-order read → audio-message conditional UPDATE → existing helper with conversationAlreadyLocked → clocks | Already parent-first; do not remove its earlier lock |
| Historical text | Duplicate lookup → standalone child INSERT with outside-insert duplicate handling | No parent upgrade in the same transaction |
| Turn claim/completion/release and detected-language persistence | Conditional Conversation UPDATE | Serializes on the same parent; guards must remain intact |
| API control transition | Shop FOR UPDATE → installation FOR SHARE → joined Conversation FOR UPDATE / recovery FOR SHARE → Conversation mutation → control-event INSERT | Parent before event child; ownership/revision validation remains protected |
| Shopify recovery control | Owned-recovery read → Shop FOR UPDATE → Conversation FOR UPDATE → Conversation mutation → control-event INSERT; SERIALIZABLE | Parent before event child; isolation-level serialization retries remain separate |
| Recovery final-send fence | Plain initial context read → Shop FOR UPDATE → Conversation FOR UPDATE → refreshed context → command/attempt lock where applicable → message INSERT/UPDATE | Existing explicit order; provider HTTP starts after commit |
| General final-send fence | Shop FOR UPDATE → Conversation FOR UPDATE → prepared message FOR UPDATE → admission UPDATE | Strong parent lock precedes existing message work |
| Woo initial-send fence | Shop FOR UPDATE → Conversation FOR UPDATE → recovery → attempt → message | Same parent-first subset; consent/STOP evidence is rechecked under its own fence |
| STOP writer | Recipient advisory lock → sorted Shop FOR UPDATE locks → re-read phones → phone mutations; support notices after commit | Does not require ingress to acquire Shop; ingress has no subsequent Shop lock |
| Outbound markSent | Message UPDATE → message identity read → Conversation clock UPDATE | A separate remaining inversion against a concurrent parent-first fence on the same existing message; outside the U3 correction |

Writer evidence: `BG/src/services/inbound-whatsapp-audio.service.ts:23-36,165-199`; `BG/src/services/whatsapp-inbound-processing.service.ts:307-341`; `BG/src/services/conversation.service.ts:237-336,451-528`; `moda-interact-api/src/merchant/conversations/control/service.ts:37-118`; `moda-interact/app/services/recoveries/recovery-human-commands.server.ts:40-132`; `BG/src/services/recovery-conversation/recovery-conversation.sql.ts:45-59`; `BG/src/services/recovery-conversation/outbound-send-fence.service.ts:66-304`; `BG/src/services/outbound-whatsapp-admission/general-outbound-send-fence.service.ts:23-76`; `BG/src/services/woocommerce-recovery/woo-initial-send-fence.service.ts:102-180`; `BG/src/services/whatsapp-contact-opt-out/stop-writer.ts:32-78`; `BG/src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts:477-499`.

Ingress need not copy every earlier Shop lock used by outbound policy. It never requests Shop after taking Conversation. Adding a Shop lock to solve U3 would increase contention across unrelated Conversations without fixing an identified ingress ordering dependency.

The markSent inversion is an adjacent audit lead, not a reproduced new finding: a concurrent general-fence transaction can hold Conversation while requesting the existing outbound message, whereas markSent can hold that message while requesting Conversation. The earlier preparation/admission checks reduce overlap but are separate transactions; overlapping callers can have passed them before admission. This merits its own focused barrier test. Moving ingress's new-child INSERT does not make a claim that all database writers are deadlock-free.

## 4. Correction choice

| Choice | Benefit | Cost / correctness obligation | Recommendation |
| --- | --- | --- | --- |
| Move existing helper before child INSERT | Removes this upgrade order; reuses current strong lock and locked-state decision; successful distinct-message count unchanged | Version/pending write now precedes INSERT; duplicate losers can do more work, and all later failures must abort the entire transaction | Preferred narrow correction |
| Add a new explicit parent lock before INSERT, leave helper unchanged | Also removes this upgrade order | Adds a redundant call; helper may lock/read twice | Unnecessary for this text path |
| Change helper to FOR NO KEY UPDATE but retain child-first order | Allows both prior FK KEY SHARE holders; still serializes non-key parent changes | Changes the lock contract for every default helper caller; permits FK-only insertions during locked work; requires auditing all stronger later locks and writer assumptions | Viable alternative to test, not the smallest-risk first choice |
| Defer/remove FK, serialize whole queue, or add a Conversation mutex | May alter contention | Wider schema/runtime contract, extra failure modes, or unnecessary cross-job serialization | No evidence justifying it here |

The helper updates only non-key version, processing and pending fields on these branches. Thus FOR NO KEY UPDATE is not intrinsically invalid. Its two-receiver example should be included as a comparison in the mechanism protocol, without treating that example as a complete lock-graph proof. The preferred change keeps the existing strongest lock acquisition and alters only its position.

Do not split the helper outside the interactive transaction. Do not advance a version in a committed first transaction and insert the message in another. Keep createdAt/receivedAt, monotonic clocks, HUMAN clearing, frozen AI delay/revision, and message ownership checks unchanged.

The receive-level client-call estimates in the prior updated report remain 11 when opening a recovery AI turn with matching engagement and 10 when extending one with matching engagement. These estimates count Prisma/raw calls on successful distinct-message paths, not generated SQL statements or round trips. The proposed reorder changes neither successful estimate. It can increase work on a concurrent duplicate or other failed-INSERT path because the helper now runs before that failure; its writes still roll back. Combining the three Conversation writes or eliminating language/engagement rereads is a separate optimization.

## 5. Duplicate and retry requirements

The early message lookup is an optimization and duplicate shortcut, not a concurrency proof. Two callers can both miss the same providerMessageId.

With parent-first ordering, the winner locks and records the message. After that winner commits, the loser may acquire the parent, increment the version locally, and fail its child INSERT with the unique constraint. **The loser must leave the transaction rejected so every local parent mutation rolls back.** Returning success inside the transaction after catching the INSERT error would be incorrect. No extra duplicate lookup is mandatory for correctness; a post-lock lookup would be a separate call/behavior tradeoff.

The current receive wrapper logs the original error object with the Shared structured logger and rethrows it (`conversation.service.ts:78-85`). The ingress wrapper also propagates failure (`whatsapp-inbound-processing.service.ts:23-30`); the worker awaits it. No local transaction retry exists in this path. The normal Messaging producer configures **three total attempts**, exponential backoff with a 1,000 ms base (`moda-interact-messaging/app/lib/whatsapp/whatsapp-job-publisher.server.ts:22-38`). This is a queue retry opportunity, not guaranteed unlimited delivery.

On retry after a failed transaction, the whole receive path runs again. On retry after a transaction committed but engagement/enqueue failed, the existing-message branch returns the current Conversation version and the caller can repair enqueue. Preserve its ownership check. The new pending repair cannot resurrect an inbound message whose transaction never committed.

The U3 conclusion is therefore contention/retry consumption and possible eventual job failure if its budget is exhausted, not demonstrated data loss. Do not add exception-to-false handling or mark a failed receive as completed.

## 6. Language: an existing race that reordering does not fix

The pre-transaction language read deserves an explicit boundary. It is no longer used to decide pending initialization, but its resolved tag/source is unconditionally written after the helper lock.

A valid existing schedule is:

1. Receive for version n+1 reads language L0 while Conversation is still at n.
2. The processor owning version n passes `applyDetectedLanguage`'s version/lease predicate and commits L1.
3. Receive locks current Conversation, increments to n+1, then overwrites L1 with its earlier L0 resolution.

The detected-language predicate in `conversation.service.ts:517-528` cannot prevent this ordering because the new receive has not yet advanced the version at step 2. The language resolver preserves a current tag when there is no explicit standalone override (`conversation-language.service.ts:resolveInitialLanguage`). This is a pre-existing stale-language write, not a consequence of moving the helper.

There is **no additional language algorithm change required to remove U3**. However, a description saying “all ingress decisions now use locked current state” would be false. If the later implementation also consolidates reads/writes, carry languageTag/languageSource and recovery identity from a locked Conversation projection, resolve language after acquiring that lock, then persist the result. Do not reuse the pre-lock snapshot as authoritative. Simply checking the resolver's `changed` flag is incomplete: it compares the tag, while an explicit same-tag selection may still change the source to customer-explicit.

Treat these as separate acceptance scopes: the narrow U3 reorder must preserve existing language behavior; a language freshness correction needs its own forced old-read/new-detection ordering test and explicit same-tag/source-override coverage.

## 7. Validation that would establish the fix

The present integration test uses Promise.all for concurrent receives (`BG/tests/integration/conversation-turn-scheduling.integration.test.ts:125-188`). It does not force both child inserts to finish before either upgrade. Its current success, if observed, would not exclude U3. The rollback test at 190-229 reconstructs the child-first sequence manually; future regression coverage should exercise the corrected receive path as well.

| Test | Deterministic boundary | Required result |
| --- | --- | --- |
| Current mechanism, distinct provider IDs | Finish both FK-checked INSERTs, then request both parent upgrades | One 40P01 victim; one survivor; transaction atomicity; replay victim yields exactly two messages and version 2 |
| Parent-first mechanism | A holds parent; B blocks acquiring parent before any B INSERT; A commits; B proceeds | No deadlock in this schedule; both messages once; version 2 |
| Real receive, fresh recovery AI turn | Hold A immediately after its parent lock and start B on same Conversation | B waits before child insertion; frozen pending start/deadline/revision from first successful recorder; versions 1 and 2 |
| Old completion versus new receive | Complete old turn after the new receive's pre-read but before its lock | New locked helper reopens pending state correctly; no return of the old MSG-01 stale-pending defect |
| Duplicate same provider ID | Both early duplicate reads miss; overlap inside transaction | One message/version increment; loser fully rolls back; retry returns duplicate and preserves ownership |
| Error after parent mutation, before/during child INSERT | Force a unique/validation failure through the real receive path | Message and every pending/version/clock mutation roll back; original error reaches logger/caller |
| HUMAN transition in both orders | Control writer wins parent first, then receive; reverse in separate test | HUMAN mode consumes inbound without AI work; no stale AI permit after revision change |
| Audio completion versus text | Parent-lock boundary, committed audio reservation already exists | Event-order checks remain current; one completion per audio row; coherent versions/pending snapshot |
| Final-send fence versus new inbound | Hold each side at its parent lock in separate cases | Existing expected-version/control predicates make the decision from the serialized current state |
| Language freshness, if included | Pause after old language pre-read; commit valid detection; resume receive | Current detected language retained unless an authorized explicit preference overrides; same-tag source upgrade preserved |

For the application tests, use test-level transaction/client interception or real independent sessions to establish barriers. Do not add production sleeps or synchronization abstractions. A barrier requiring both INSERTs after parent-first locking is invalid: the second INSERT is supposed to be unreachable until the first transaction releases the parent.

Existing repository runner, after dependencies and disposable infrastructure are available:

```sh
cd moda-interact-background
npm run test:integration -- tests/integration/conversation-turn-scheduling.integration.test.ts
```

The runner provisions `pgvector/pgvector:pg17`, applies the local Prisma schema through Shared disposable infrastructure, and selects supplied tests (`scripts/test-integration.mjs:14-19,80-94`). It has not been run during this review, and the current test file does not yet contain the proposed forced-interleaving tests.

## 8. Supplied mechanism experiment

- `u3-postgres17-setup.sql`: minimal source-faithful PK/FK/unique/version fixture.
- `u3-postgres17-reproduction.md`: exact disposable-container commands and two-session schedules for current order, parent-first order, weaker-lock comparison, rollback and duplicate behavior.

Record actual image ID, server version, SQLSTATE, wait graph, and post-transaction rows if executed later. Keep that evidence separate from application tests and from the static snapshot assessment. No result from that future execution is asserted here.
