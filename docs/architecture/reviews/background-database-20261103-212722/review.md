---
review_id: BGDB-20261103-02
title: Background database calls - updated snapshot reassessment
status: updated-static-review
coordinator: moda_architect
created: 2026-11-03
snapshot: moda-interact-workspace(20261103-212722).zip
baseline_snapshot: moda-interact-workspace(20261102-112817).zip
---

# Background database calls: updated snapshot reassessment

## Assessment

The updated snapshot materially improves delayed conversation processing and neutral initial outreach. The earlier text pending-turn race, MSG-01, is addressed in the current source. The initial-outreach retry finding, C3, is only partially mitigated: optional enrichment can now fall back to an approved neutral template, but a required-state failure after recovery creation still has no general worker re-entry path. The other earlier correctness and performance findings remain applicable at their stated confidence levels.

Three additional issues need attention before treating this as an integrated, reproducible snapshot. API source consumes the new ARCH-055 fields while its bundled Database schema and migrations remain behind. The new neutral fallback's prior-dispatch lookup also confuses a usage idempotency key with the provider dispatch key actually persisted by the send fences. The new text-ingress statement order permits a foreign-key lock-upgrade deadlock between concurrent messages. These are source/schema, identity and concurrency findings; no deployed build failure, live deadlock or duplicate message is claimed.

The ARCH-055 persisted human follow-up claim identity is otherwise consistently propagated through the reviewed producer, claim, replay, final admission and cancellation boundaries. New fixed AI deadlines, ownership/version checks and bounded queue repair should be retained. They are correctness work, so the additional calls they require should not be removed solely to lower a query count.

This report updates the previous assessment against the exact new archive. It is a static architectural review, not acceptance of an implementation attempt or a measured performance result.

## Source boundary and comparison

| Item | Evidence |
| --- | --- |
| Previous snapshot | `moda-interact-workspace(20261102-112817).zip` |
| Previous SHA-256 | `ee42bb83ee441ba9018779e760967a5bf87edcbc429eecc58699f1419863861b` |
| Updated snapshot | `moda-interact-workspace(20261103-212722).zip` |
| Updated SHA-256 | `f8194947c3564a8f9ea8942d9462ec83716aecc17fc1626d7d846af68c044024` |
| Architect role | Supplied `moda_architect(20261102-112835).toml` |
| Archive regular-file delta | 146 added, 315 changed, four removed |
| Background source delta | Seven added and 22 changed TypeScript files; no removals |
| Principal changed areas | ARCH-054 AI delay/repair, ARCH-052 neutral outreach, ARCH-055 claim/upload/lifecycle identity |

The source comparison uses original archive entries, excluding review files written after the earlier extraction. The updated archive does not include the previous review directory. This patch therefore adds a standalone review directory and has no dependency on applying the earlier review patch. Historical task acceptance reports are evidence of what those reports say; their builds and tests were not reproduced here.

There is no parent, Background or Database Git metadata in the supplied snapshot. Actual branch HEADs, submodule gitlinks, deployment state and remote publication cannot be established from these files. No application build, Prisma generation, integration suite, database/Redis connection, provider request, benchmark or query plan was executed during this reassessment. The delivery adds review/evidence documents only.

## What changes in the previous conclusions

### MSG-01: withdraw the old text pending-state race for the current source

Previously, text ingress used an unlocked earlier Conversation read to decide whether to create a pending turn. Completion could clear that state between the read and the write, leaving a new inbound version without a pending timestamp.

`moda-interact-background/src/services/conversation.service.ts` now calls `recordProcessableInbound` within the message transaction. The helper in `services/conversation-ai-delay/pending-turn-repository.ts` reads the current Conversation with `FOR UPDATE OF c` and decides whether to open the pending turn from that locked state. For a new recovery AI turn, it captures the merchant delay, fixed deadline and current control revision. Later fragments retain that snapshot. HUMAN ingress advances the processed watermark and creates no AI deadline. Audio completion uses the same helper after obtaining its existing Conversation lock.

The processor now carries the captured revision through claim/completion and final send admission. The final fence also compares the expected inbound version using its existing locked projection. These changes address stale ownership and changed inbound state after asynchronous preparation. Existing test source exercises the intended cases; runtime verification remains outstanding in this review.

This conclusion is specifically about the former MSG-01 interleaving. It does not close moderation retry loss, incomplete outbound reservation replay, early provider-status handling or every possible messaging race. The new locking order also creates the distinct U3 contention/retry issue below; keep that separate from the race that was fixed.

### C3: optional failures have a fallback, but general recovery continuation is still missing

`automated-recovery-template.service.ts` routes initial policy `NONE` and selected optional enrichment failures to `InitialNoOfferFallbackService`. The fallback validates saved checkout/recovery/attempt state and uses the existing independently approved neutral text template. It avoids optional model, discount and product-image work for the neutral branch. The absence of an offer-admission token is legitimate for that no-offer preparation; mandatory consent, STOP, billing, moderation and final template/provider guards remain.

However, recovery initiation still persists the DETECTED recovery and sequence-one attempt before required preparation can fail. The fallback can return REQUIRED_STATE_UNAVAILABLE, which becomes a thrown retry. The candidate worker still allows re-entry only for specific suppression markers; a generic retry sees the existing DETECTED recovery and returns `no-op-existing`. Queue repair of conversation turns does not repair this checkout-initiation state machine.

Keep C3 open, with a narrower description of the failures now avoided. The next proof must run the actual candidate worker and materializer through post-insert failures, rather than directly invoking initiation twice. Include a failure after attempt/support-notice finalization but before the separate recovery status update.

### ARCH-055: the persisted follow-up owner improves identity correctness

New API and Shopify command producers persist a command UUID as both command `followUpClaimKey` and attempt `initiationKey`; the public HTTP idempotency key remains separately scoped to the shop. Historical rows are backfilled from each command's own historical key, not an attempt's potentially newer owner. Background loads the stored value and uses it at replay, provider admission, cancellation and conditional attempt reset. Missing/blank keys fail closed without guessing which owner or credit to release.

This is a useful change with no additional database invocation merely to carry the field: existing projections contain it. It does not resolve the earlier BS-05 accounting-lineage risk, because claim ownership and the exact consumed credit reservation are different identities.

## New findings and changed measurement scope

### U1 — API's bundled database dependency is behind its source

Canonical Database, Background, Shopify and Admin schemas are identical at 191,864 bytes and 130 models. Their migration trees contain 71 SQL migrations plus `migration_lock.toml`, all byte-identical. API still contains the old 191,707-byte schema and lacks the three ARCH-055 migrations.

API's normal `build` and `typecheck` scripts run Prisma generation from `database/prisma/schema.prisma`. That schema lacks `followUpClaimKey` and `intentPurposeKey`, although API's command admission and upload service use them in typed Prisma operations. A client generated from these included bytes does not define those fields. This is a concrete archive integration mismatch; it is not a build result produced in this session.

Reconcile the intended Database dependency in API, regenerate through the normal build path and validate the migration/producer/consumer combination. Do not hand-edit a consumer schema to hide the mismatch. Existing Commerce/MCP schema divergence predates this update and is distinguished in the schema appendix.

Evidence: `moda-interact-api/package.json`; `src/merchant/conversations/messages/admission.service.ts`; `src/merchant/merchant-knowledge/upload.service.ts`; the compared schema and migration trees. Exact hashes and counts are in [source-and-inventory-delta.json](source-and-inventory-delta.json) and [billing/schema review](billing-and-scheduled-work.md).

### U2 — New fallback prior-dispatch check uses the wrong identity

`initial-no-offer-fallback.service.ts` queries `ConversationMessage.providerDispatchKey` using `recovery-outreach:<attemptId>`. The normal path uses that string as `UsageEvent.idempotencyKey`. Shopify's provider fence persists `arch040-auto-<hash(messageId)>`; Woo persists `arch046-woo-initial-<hash(shop,attempt)>`.

The new query therefore misses ordinary persisted dispatch permits. Its alternate linked-message lookup cannot run for a non-null attempt link because an earlier guard already rejects that state. Existing reservation and final-send guards still apply downstream, so this finding does not establish duplicate provider delivery. It establishes that the new early uncertainty check does not detect the canonical data it was designed to inspect.

The unit test mocks a row for the same incorrect query, while the new success-path integration fixture asserts the real Shopify key prefix. Add the missing interrupted-finalization case using actual persisted usage/message identities. Reuse the existing attempt-to-usage-to-message resolution and distinguish confirmed, uncertain and definitive failure outcomes before preparing again. No new index or parallel identity scheme is needed.

Evidence and branch reasoning: [checkout/recovery review](checkout-and-recovery.md), including `initial-no-offer-fallback.service.ts`, `outbound-admission-reservation.service.ts` and both final fences.

### U3 — Text ingress can upgrade conflicting foreign-key locks

`conversation.service.ts:162` inserts the child ConversationMessage before `recordProcessableInbound` requests `FOR UPDATE OF c` on the parent Conversation. The declared message-to-conversation foreign key is nondeferrable. PostgreSQL's referenced-row check uses a key-share lock, which can coexist with another key-share lock but conflicts with the subsequent requested update lock. These mechanics are documented in the [PostgreSQL row-lock compatibility table](https://www.postgresql.org/docs/17/explicit-locking.html#LOCKING-ROWS), the [referential-integrity checker source](https://doxygen.postgresql.org/ri__triggers_8c_source.html) and [constraint timing defaults](https://www.postgresql.org/docs/17/sql-createtable.html).

The source and those locking rules support this possible interleaving: two transactions insert different provider messages for the same conversation, each obtains the compatible foreign-key lock, and each then waits for the other when it requests the stronger parent lock. No earlier per-conversation lock was found spanning this transaction. This is a static concurrency finding, not a reproduced database result.

The transaction rolls back atomically on failure; no partially committed message/version state is asserted. `receiveMessage` logs and rethrows without a local transaction retry. The normal Messaging publisher configures three total job attempts with exponential backoff starting at 1,000 ms, so a victim can repeat the ingress path and consume its retry budget. Successful eventual processing is not guaranteed after exhaustion, and the pending-turn repair service does not reconstruct a message whose insertion rolled back.

Acquire the required parent lock before the child insert within the same transaction, or separately justify a compatible weaker row lock against all existing writers. Preserve atomic message/version/pending-state updates. The targeted regression is two database sessions with distinct provider IDs, paused after the child inserts before their parent-lock requests. Test actual ingress and retry behaviour as well as the helper in isolation.

Source evidence: `services/conversation.service.ts`, `services/conversation-ai-delay/pending-turn-repository.ts`, canonical baseline migration's `ConversationMessage_conversationId_fkey`, and `moda-interact-messaging/app/lib/whatsapp/whatsapp-job-publisher.server.ts`. See [messaging review](messaging-and-conversations.md) for the surrounding execution path.

### O7 — New neutral path repeats two reads before preparation

The valid initial `NONE` branch performs six explicit client invocations before delegated sender/template preparation: two in the outer facade and four in fallback. Recovery and lifetime policy are each read twice. On this short neutral branch, that is a narrow consolidation candidate. After a long model/MCP operation, a fresh state read can be necessary and should not be removed by applying the same shortcut indiscriminately.

This six-call boundary excludes template/sender internals, billing, dispatch, implicit relation expansion and transaction control. The neutral path also avoids substantial optional enrichment work, so the duplicate reads do not establish a net performance regression.

### R2 / MSG-10: add the new periodic pending-turn repair to the workload model

Each messaging process now schedules one repair pass 30 seconds after the previous pass completes. A pass reads pages of 100, scans at most 1,000 candidates, retains its keyset cursor across passes and performs one to ten SELECT invocations. It uses cached runtime configuration and deterministic versioned queue IDs. Existing jobs are preserved; due failed jobs can be retried. The existing `(pendingAiNotBeforeAt, id)` index matches the ordering.

For M messaging processes and negligible pass duration, this adds approximately `2 × M` empty-poll SELECTs per minute, or up to `20 × M` SELECTs per minute at the page ceiling. Redis job checks/retries/adds are separate. Replicas deliberately may discover the same candidates; execution-time claim/final-send guards remain necessary. Bounded returned rows do not prove bounded examined rows, latency or fleet capacity.

The repair reconstructs missing jobs and retries due failed jobs for selected durable pending AI turns. Successful processing still depends on the claim predicates; the messaging appendix records a partial-lease-state validation gap for legacy/corrupt state. It cannot recover a version already marked processed by moderation suppression or reservation replay, because such a row no longer satisfies the pending selector. This is why MSG-02 and MSG-03 remain open.

## Complete disposition of earlier findings

The identifiers below are review references, not newly created implementation tasks. "Retained" preserves the earlier evidence classification; it does not promote a risk to a reproduced defect.

| ID | Updated disposition | Current conclusion |
| --- | --- | --- |
| R1 | Retained | Heartbeat rejection and unpropagated lease loss still permit scheduler overlap; duplicate business effects are unproven. |
| R2 | Expanded measurement scope | Existing configuration/reconciliation polling remains; add pending-turn repair. |
| R3 | Retained | Original errors are still replaced at platform configuration/readiness and the identified Woo diagnostic event. New outreach logs improve other sites. |
| C1 | Retained | Shopify's ten-second unrenewed exclusion and GET/DEL release remain. |
| C2 | Retained | Basket refresh can overwrite newer data without an expected activity/version predicate. |
| C3 | Partially mitigated | Neutral fallback avoids selected optional failures; generic post-insert worker continuation remains missing. |
| C4 | Retained | Capacity repair can repeatedly select an obstructed first shop page. |
| C5 | Retained | Shopify order history can use a stale observed source status. |
| O1 | Retained | Scheduling-only policy reads still load broad settings/discount/catalogue context. |
| O2 | Retained | A single-statement interactive transaction remains; correct the write fence before simplifying it. |
| O3 | Retained | Latest-recovery control-flow reads still load all scalar columns. |
| O4 | Retained | Woo preflight reads overlap; final rechecks remain necessary and full initial-send reachability remains gated. |
| O5 | Retained | Both unique and nonunique generation indexes remain declared; actual deployed cost is unmeasured. |
| O6 | Retained | Successful expiry pages remain transaction-heavy. |
| MSG-01 | Addressed in current source | Pending initialization now uses current locked state in the message transaction. |
| MSG-02 | Retained | Outbound moderation retry/dependency outcomes can still become terminal suppression. |
| MSG-03 | Retained | Existing usage identity still suppresses an unfinished outbound reservation on replay. |
| MSG-04 | Retained | An early provider status with no persisted provider message ID still lacks durable unmatched-event repair. |
| MSG-05 | Retained | No-context phone lookup still normalizes text in the predicate instead of using canonical indexed identity. |
| MSG-06 | Retained | Admission still materializes automatic message IDs before aggregating usage. |
| MSG-07 | Expanded measurement scope | Unbounded history/moderation reads remain; the configurable delay of up to 30 minutes can widen the pending interval, which can extend further while processing is delayed. |
| MSG-08 | Retained | Canonical-null STOP fallback retains broad unresolved-phone scans. |
| MSG-09 | Refined | Small redundant lookups remain and ingress has separable writes; late human-command and final locked revalidation must remain fresh. |
| MSG-10 | Expanded measurement scope | Existing locking/human polling costs remain; new repair and current-turn guards add work to measure. |
| TEMPLATE-01 | Retained | Template assembly still uses 5 + 2N explicit transaction calls. |
| TEMPLATE-02 | Retained | Meta pollers can repeat provider GET discovery across replicas; CAS still protects writes. |
| BS-01 | Retained | Knowledge pending repair still lacks progress past retained ineligible prefixes. |
| BS-02 | Retained | Successful tombstone deletion still has no persisted external-deletion acknowledgement. |
| BS-03 | Retained | Eligibility still rereads shop-wide source/rank context per source. |
| BS-04 | Retained | Paid Shopify commit still repeats a meter-handle read in the same transaction. |
| BS-05 | Retained as conditional risk | Historical/current reservation ambiguity still requires a period-transition reproduction; no live accounting failure is claimed. |
| BS-06 | Retained | Billing queue reconstruction still selects/publishes an unbounded global set. |
| BS-07 | Retained | Translation/catalogue/chunk loops still perform serial per-item writes under publication locks. |

The earlier Woo production qualification also remains: normal composition does not inject the test-only enable callback. Full initial-send work is implemented behind a test-only enable path, with corresponding test source, but must not be counted as ordinary production workload from this snapshot. Confirmed-send reconciliation does run before that gate.

## Inventory and interpretation

| Metric | Previous | Updated | Delta |
| --- | ---: | ---: | ---: |
| Background TypeScript files | 481 | 488 | +7 |
| Source lines | 70,139 | 71,324 | +1,185 |
| Worker modules | 25 | 25 | 0 |
| Files with direct database client sites | 198 | 201 | +3 |
| ORM reads | 433 | 438 | +5 |
| ORM writes | 358 | 359 | +1 |
| Raw query/execute sites | 236 | 238 | +2 |
| Transaction boundaries | 162 | 162 | 0 |
| Total direct sites | 1,189 | 1,197 | +8 |
| Separately indexed SQL-wrapper calls | 59 | 59 | 0 |

The same corrected lexical method was applied to both inputs. It counts source locations, not SQL executions or performance. The new helper has mutually exclusive branches; a fallback read site is unreachable after an earlier guard; another site can execute once per repair page. These distinctions are why the eight-site increase cannot be translated into an eight-query increase per event.

### Changed named branch budgets

| Named boundary | Previous | Updated |
| --- | ---: | ---: |
| Fresh recovery text opens pending AI turn, including matching outreach engagement | 9 | 11 |
| Fresh recovery text joins pending AI turn, including matching outreach engagement | 8 | 10 |
| Duplicate text with matching outreach engagement | 4 | 4 |
| Successful non-stale audio completion transaction opens pending AI turn | 6 | 7 |
| Same audio transaction joins pending turn | 6 | 6 |
| Successful due recovery AGENT processor, otherwise identical inner services and no races | Baseline | Net +3 |
| Initial NONE preparation through pre-preparer fallback checks | No equivalent old neutral shortcut | 6 |
| New pending-turn repair pass | Absent | 1–10 SELECTs |

These are explicit client-invocation budgets with narrow boundaries, not SQL counts or complete event totals. Text's caller also adds one state read before enqueue, outside the receive-method figures; enqueue has its own existing read. The processor delta removes one ownership capture and adds three ownership checks plus one changed-version read. The final inbound-version comparison uses an already selected locked row. Detailed exclusions and race-path counts are in the domain appendices.

The architect's 20,000 Shopify ingress events/minute remains a reference assumption, not measured traffic or recovery/send volume. Keep hot filtering, actionable recovery, conversation turns, schedulers and retries separate. Query reduction should retain tenant scope, consent/STOP, control revision, exact billing lineage, durable provider ambiguity and atomic publication.

## Revised next steps

1. Reconcile API's Database dependency and normal client-generation/build path. Verify coordinated ARCH-055 producer/consumer migration order.
2. Correct fallback's existing-dispatch lookup and prove canonical interrupted-send/finalization cases. Resolve general C3 continuation through the actual candidate worker, retaining the same recovery/attempt/usage identities.
3. Correct and validate U3's parent/child lock order. Validate the new pending-turn capture and fixed-deadline/version fences under concurrent inbound/completion/takeover and failed queue publication. Keep MSG-01 removed from the open defect list unless contradictory execution evidence emerges.
4. Continue the earlier correctness work: moderation typed retries, pending reservation replay, early provider statuses, Shopify lease/activity/history races, and capacity/knowledge repair fairness.
5. Measure the new branch costs and repair scan alongside the retained hot-path and batch opportunities. Prefer narrow projection/read reuse and bulk persistence only where existing integrity boundaries remain intact.

ARCH-054 explicitly requires draining/reconciling old pending turns and queued jobs during rollout (`docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`, rollout sections). Legacy recovery rows with no captured pending-AI triple are not automatically backfilled. This is an existing deployment prerequisite, not a newly inferred migration defect. The ARCH-055 migration likewise requires coordinated producer/consumer quiescence; nullable keys are not a guarantee of compatibility with legacy writers.

## Review files and validation

- [Runtime and inventory](runtime-and-inventory.md): exact method, new repair cadence, retained lease/configuration findings and prerequisites.
- [Checkout and recovery](checkout-and-recovery.md): every C/O disposition, fallback identity defect, worker continuation and named call budgets.
- [Messaging and conversations](messaging-and-conversations.md): MSG/TEMPLATE dispositions, fixed deadline/ownership behaviour and changed branch budgets.
- [Billing and scheduled work](billing-and-scheduled-work.md): schema/migration parity, human claim identity, every BS disposition and producer/consumer boundaries.
- [Database call inventory](database-call-inventory.json): refreshed source-location index.
- [Snapshot delta](snapshot-delta.json): exact added/changed/removed regular-file paths.
- [Source and inventory comparison](source-and-inventory-delta.json): hashes, migration parity and per-file count changes.

Delivery validation uses a fresh extraction of the exact updated ZIP to check strict whitespace/applicability, review-only changed paths, authored-versus-applied content equality, unchanged original file bytes and byte equality of the standalone patch with the ZIP member. The separate validation record contains the actual results and patch hash. These checks establish artifact integrity, not runtime acceptance. No task status, architecture status, index, application source or migration is changed by this delivery.
