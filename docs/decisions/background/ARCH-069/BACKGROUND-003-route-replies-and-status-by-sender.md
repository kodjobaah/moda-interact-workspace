---
id: ARCH-069-BACKGROUND-003
architecture_id: ARCH-069
title: Route inbound messages, STOP and delivery status using the actual Moda sender
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-069-BACKGROUND-002]
enables: [ARCH-069-BACKGROUND-004]
created: 2026-11-13
updated: 2026-11-14
---

# Route inbound messages, STOP and delivery status using the actual Moda sender

## Architecture

[ARCH-069 WhatsApp sender pool and checkout reply routing](../../../architecture/ARCH-069-whatsapp-sender-pool-and-checkout-reply-routing.md). Owner: `moda_background` in `moda-interact-background`. Architect: `moda_architect`. R10 portable handoff.

## Objective

Deliver a customer reply to one proven checkout, or pass the original event and its verified possible owners to BACKGROUND-004. Apply an explicit STOP to the correct merchant scope. Apply a provider receipt and its downstream billing or reachability effects only to the proven original outbound. Two shops may contact the same customer on one Moda number. One shop may have several contacted baskets. The merchant's permitted checkout model applies to both Shopify and WooCommerce.

## Context

[DATABASE-001 R07](../../database/ARCH-069/DATABASE-001-create-sender-pool-and-active-assignments.md) supplies the thread, shop route, per-conversation membership, routing turn and non-pooled sender columns. [BACKGROUND-001 R08](BACKGROUND-001-allocate-and-release-recovery-senders.md) assigns and releases numbers and owns the effective-lifetime and locking rules. [BACKGROUND-002 R09](BACKGROUND-002-pin-senders-through-provider-dispatch.md) puts the permitted number on the wire. BG003 consumes that evidence. Receiving a message cannot select or reallocate an outbound number.

The snapshot's live router checks one configured number and queries by recipient with `LIMIT 2`. The inbound handler can downgrade a just-closed route to history, record recovery activity before the message is committed and repair engagement on duplicate input. Its provider-status service runs post-commit effects for several outcomes currently exposed as `ignored`. Those are the actual entry points to change.

## Scope

Paths below are relative to the Background repository. Preserve the existing callers, normalized event payloads and job names. Create one local entry module `src/services/recovery-sender-route.ts` for the verified route, evidence and transaction helpers. Put its set-oriented SQL and result mapping in `src/services/recovery-sender-route-store.ts`. Existing service-specific behaviour stays in the following files.

| Paths under `src/` | Responsibility |
| --- | --- |
| `workers/whatsapp.worker.ts`, `services/recovery-routing.service.ts`, `services/whatsapp-inbound-processing.service.ts`, `services/recovery-recipient-ownership.ts` | Parse and dispatch the existing jobs, classify the actual pair, prove candidate ownership, and pass the decision to the correct writer. The live method is `RecoveryRoutingService.resolveInboundMessage`. The similarly named `whatsapp-conversation-routing.service.ts` is not the live repair point. |
| `services/conversation.service.ts`, `services/conversation-ai-delay/pending-turn-repository.ts`, `services/recovery-outreach-attempt.service.ts`, `services/recipient-reachability-positive.service.ts` | Transaction-local message persistence, idempotency, activity, engagement and legitimate same-owner duplicate repair. Consume the existing pending-turn writer. |
| `services/recovery-conversation/recovery-conversation.sql.ts`, `services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts` | Read the verified inbound occurrence when checking a customer-service window, ordering follow-up evidence or recording engagement. |
| `services/inbound-whatsapp-audio.service.ts`, `services/whatsapp-media.service.ts`, `services/speech-transcription.service.ts`, `services/conversation-turn-processor.service.ts` | Revalidate the original owner before media, completion, agent reads and dispatch. Retain source-level errors. |
| `services/whatsapp-contact-opt-out.service.ts`, `services/whatsapp-contact-opt-out/{phone,quoted-outbound,stop-writer}.ts`, `services/routing-guidance.service.ts` | Authenticate the inbound pair, verify a quoted merchant when present, keep the registered-shop STOP writer and send approved generic guidance on the receiving number. |
| `services/whatsapp-provider-status.service.ts`, `services/whatsapp-provider-status-lifecycle.ts` | Validate both exact output-ID namespaces before applying status and deciding which post-commit repair is authorized. Reuse the existing lifecycle and usage helpers. |

Read the Shared v1 inbound and v2/v3 status definitions and Messaging's `app/lib/whatsapp/{inbound-message-normalizer,provider-status-normalizer,normalization-utils,whatsapp-job-publisher.server}.ts` as evidence. Admission starts after authenticated ingress and queue normalization. Signature verification and webhook publication remain in their existing services.

## Out of Scope

Database or Shared changes, provider registration/discovery, stock allocation, new checkout statuses, public wire contracts, tenant API changes, deployment, routing-model prompts, customer question selection, and changes to merchant basket or credit policies. BG004 owns pending questions and merchant/basket clarification. This task provides their verified input and common write guard.

## Requirements

### 1. Identify the original sender and customer

1. For ordinary inbound, STOP and guidance classify the receiving phone by its exact inventory primary key, irrespective of allocationEnabled. An inventory match requires the original event WABA. A drained number still serves active and historical conversations. A row on another WABA is a mismatch. On genuine absence only, verify the encrypted server-configured non-pooled pair. Never substitute a current singleton for missing proof of an old send. Canonicalize the customer's phone with `canonicalWhatsAppSender`; keep it distinct from Meta's phone-number ID.
2. For an exact quoted message, stored replay or callback, read the original immutable owner. For a pooled outbound verify conversation → assignment → route → thread → inventory, the repeat recipient and sender columns, original shop and trusted WABA. For non-pooled outbound the complete BG002 `dispatchProviderAccountId` / `dispatchProviderPhoneNumberId` pair is authoritative. Check independent proofs for conflict. Reject half pins. Where both pins are null and there is no assignment, the sole legacy fallback is the prior per-message delivered usage evidence specified under status below. An eligible historical reference may survive enrollment/reuse. Independently pinned historical receipts remain verifiable after the dedicated singleton changes. A current credential or a callback cannot supply yesterday's proof.
3. The unquoted legacy lookup is only for a currently proven dedicated, non-enrolled pair. Consider only unassigned recoveries with confirmed original contact to this customer on exactly that pair. Apply the exactly-one rule after this filtering. Enrolled pairs use the thread branch exclusively. Keep a genuine general/standalone conversation in its existing scope. A missing or conflicting assignment cannot turn a recovery into a general conversation. Unknown pairs have no merchant, STOP, guidance, audio or status authority. A storage/credential failure has a distinct retry outcome.

### 2. Apply precedence in the live worker

Run explicit typed STOP before raw abuse admission. For other input, run the existing raw abuse gate before lookup, persistence, clarification or media. Run the following order on recognized input.

| Priority | Input | Exact action |
| --- | --- | --- |
| 1 | Explicit typed STOP/UNSUBSCRIBE | Preserve `isExplicitWhatsAppStop`. A verified checkout outbound or confirmed shop-specific clarifying prompt can establish consent scope. Verify original recipient, shop, receiving WABA and number using the original immutable lineage. Released membership/closed route remains valid proof of the original merchant. A verified quote applies to that merchant only. At admission a confirmed clarification records its immutable promptScopeRouteId. A null stamp means neutral even when routeId was populated afterwards. A non-null stamp requires proving its original shop, thread generation, same recipient/account/sender and confirmed prompt receipt. A standalone STOP or missing, invalid, cross-scope, shop-selection or generic-guidance quote on a recognised sender applies `ALL_REGISTERED_SHOPS`. Propagate database read exceptions. A stop on an unknown sender has no effect. |
| 2 | Previously stored inbound provider ID | Read both `ConversationMessage.providerMessageId` and `RecoveryBasketRoutingTurn.inboundProviderMessageId`. Require matching canonical recipient, actual WABA/number, immutable thread generation, original scope if known, and direction where applicable. Replay only the original merchant or pending route turn, including a resolved turn and its matching checked-out conversation projection. Reject conflicting owners, wrong directions or changed sender and preserve original stored inputs. An exact duplicate may repair incomplete effects idempotently. |
| 3a | Quote of a checkout message | Look up the exact confirmed OUTBOUND provider ID and non-null sentAt. Verify original sender, recipient, shop, conversation/recovery, outreach or command recipient where present and existing eligibility, including `resolveRecoveryRecipient`. An active verified quote identifies that member. A closed one uses only the existing historical path. A verified shop-authored initial/follow-up, AI reply or merchant human reply with original OUTBOUND proof identifies the sending conversation; a fresh “What time do you close?” quoting that reply follows that conversation, even while another shop has a pending question. In a current thread with a pending question, forward exact confirmed outbound ownership and a verified original-basket reference as exact evidence for BACKGROUND-004 to distinguish an explicit answer from an unrelated quoted message. Never join unrelated questions merely because the same basket was quoted. |
| 3b | Quote of a clarifying prompt | Look up exact unique `RecoveryBasketRoutingTurn.promptProviderMessageId`, require confirmed sent receipt, original WABA/number/recipient and matching live thread generation. A neutral prompt uses its original thread and immutable null promptScopeRouteId. A shop prompt also requires its exact admitted shop route. On verified reply send the original turn/parent and proof to BACKGROUND-004, even if only one shop or basket now remains. A closed shop or thread may never be rebound to another route. A stale or closed-route quote is ineligible for active checkout work. A quote missing proof, cross-scope, or colliding across outbound types returns `INVALID_REFERENCE` without a fresh unquoted fallback. |
| 4 | Fresh unquoted inbound | Read the open `RecoverySenderThread` using the partial unique key `(canonicalRecipient, providerPhoneNumberId) WHERE closedAt IS NULL`, join the enrolled sender to verify WABA, and carry the immutable thread ID. Enumerate shop routes on that thread and their exact confirmed membership lineage. Group at the shop route. The former recipient/sender partial unique index on RecoverySenderRoute is absent. Different shops can simultaneously use this pair. No current positively authenticated ownership gives neutral handling. |

**Stored replay.** For pooled messages, the original conversation assignment, route and thread supply an immutable sender, shop and recipient. For an unassigned recovery conversation, use its stored inbound owner plus its original quoted outbound if present, otherwise its sequence-one proven original outbound/recipient. If the owner, pre-pool sender or addressing cannot be established exactly, skip merchant effects. Never infer legacy routing from an operator flag or query multiple shops for an exact message. General sends carrying a new non-pooled pin can receive their first verified status without any older delivered usage row.

For each shop route, require threadId, canonicalRecipient, sender/WABA and shop to agree throughout the join; recheck shop execution eligibility. Check every member using the predicates below. Before proving a shop, read only the metadata needed for ownership, contact eligibility, provider/clock checks, public merchant identity, and current-generation identity. Exclude all pricing, product names, checkout contents, customer profiles, conversation histories, previous agent responses, merchant settings and grants. One verified shop with one possible basket and no pending question can run the direct path; one verified shop with multiple possible baskets can run BACKGROUND-004's shop-only resolver. Several qualifying shops on the same thread yield the sender-thread branch. Check pending thread-scoped roots before either singleton shortcut. Roots scoped to a different shop never consume unrelated quoted input.

An eligible member must join to a RECOVERY conversation, matching shop/customer lineage, current recipient, its own recovery in MESSAGE_SENT or ENGAGED status, remaining effective lifetime and latest generation of that checkout under existing integration rules. Use the inclusive `lastExternalActivityAt` cutoff and the configured non-negative whole days, including zero and above 90. Fetch the sequence-one INITIAL attempt and its confirmed outbound. The attempt belongs to that recovery, matches the route's canonical recipient and has sentAt. Its outbound belongs to that conversation and has OUTBOUND direction, providerMessageId and sentAt. Exclude pending or unknown initial sends. One merchant's separate keys can produce any number of concurrent confirmed members.

For fresh unquoted events use the verified provider timestamp (whole seconds). Require the inbound second strictly after thread and shop-route openedAt and, for each candidate, strictly after the later of its membership assignment and its confirmed sequence-one outbound sentAt. A tie with route opening is unresolved. The Shared parser rejects a malformed timestamp before routing. A member whose initial outreach happened in a later second cannot be the subject of that earlier event. For a delayed event on a still-open shared thread compare membership/route history as of its provider second with the current live scope. A route/member that had already sent, was open at that event, and has since ended is a possible historical target. Do not silently shrink that event to the remaining live shop or basket. Preserve original candidate proof or use neutral quote guidance when the relevant time interval, lifecycle, or original effective eligibility cannot be proved. An opening/ending in the same provider second is indeterminate. A later confirmed outreach grants no permission on an earlier event. A tie with a current member’s admission/first send makes the ordering indeterminate; use neutral guidance asking the customer to quote the checkout, even if an older member would otherwise qualify. For a valid, representable but ineligible or indeterminate occurrence on a positively verified original thread or shop route, record a minimal IGNORED routing turn under that same provider ID and scope, with no basket selection or content. Redelivery after one sibling expires cannot turn that discarded event into a singleton reply. Neutral guidance retains its existing idempotent admission. Never replace event time with processing time. Explicit verified references and stored ownership have their own proof.

**Event-time and contention examples.** Treat the verified provider time as a UTC second `floor(epochMilliseconds / 1000)`. Compare each opening, assignment, confirmed first-contact and ending boundary at that precision. Same-second is unordered. Do not round up a receipt or use the worker clock to invent ordering. Preserve the actual normalized event time in the record. For an unquoted event received after number reuse, locate the exact thread generation covering its provider second before considering a fresh assignment. An older generation never acquires a replacement owner. With no provable ownership for that second, use the recognized-number neutral path. A pending question or quoted prompt cannot confer active rights on an expired generation.

| Evidence for a fresh reply | Outcome |
| --- | --- |
| Two distinct shops used different numbers for this customer | Look only on the number that received the event. When exactly one contacted, currently eligible basket remains on that number and no pending question applies, route directly. |
| Several shops shared the same number and were already contacted | Send BG004 the thread-level result with eligible identity stamps. BG003 performs no cross-merchant text classification and loads no merchant basket facts. |
| One proven shop has several distinct active checkout keys | Send BG004 the single-shop result containing all its confirmed eligible members. Distinct checkout keys at one shop do not supersede one another. |
| The worker receives a delayed event for two previously contacted shops, one of which has since expired | When the expired shop was a possible owner at the provider second, do not assign to the surviving shop. Use neutral quote guidance if the original ownership cannot be proved. An already-ended shop before that second adds no current candidate. |
| A later send for a new member is confirmed strictly after this event | The later member is excluded from that event. At an exact boundary with a relevant opening/first contact/closure, preserve the indeterminate disposition. |
| A valid quoted checkout message identifies a different basket from an outstanding question | Carry the exact quote and only applicable pending evidence. BG004 may bind it to an open question only under its explicit-answer rules. The independently quoted “What time do you close?” keeps its own checkout; the earlier delivery question stays pending. |

For unscoped reads use bound SQL and the open-thread index on `(canonicalRecipient, providerPhoneNumberId)`, then join `thread.id → route.threadId → assignment.routeId` and `assignment.conversationId → conversation.checkoutRecoveryId`. Include the history of that same recipient/sender generation needed to test the event interval. Identify the latest recovery by its own shop/checkout key. Do not limit candidates to two, impose a basket limit, issue a provider lookup, or read a full customer or stored cart per candidate. Reuse `ShopExecutionEligibilityService.evaluateResolvedShop` on its selected eligibility fields and the recipient verifier on a minimal projection that omits firstName. Require matching current customer/shop and confirmed sequence-one receipt in the active branch. A genuinely unknown prior contact cannot promote a provisional member. Keep a single consistent snapshot for candidate enumeration, including any pagination. Use a deterministic binary order (route ID, conversation ID) for complete candidate comparison and a short recheck at the point of mutation.

### 3. Persist and repair only the proved owner

1. For every direct or turn-ledger ownership write, acquire the bound provider-ID transaction advisory lock first, using the key specified in Interfaces / Contracts, then re-read both ownership tables. For a selected pooled target take Shop → Conversation → recovery/initial attempt/lifetime policy → thread → original route → original assignment in R08 order, without a global allocation lock. Consume R08 `requireAssignedSender(tx,{shopId,recoveryId,conversationId,recipient,providerAccountId,phase:"ongoing"})` to establish the selected live member and compare its returned route, sender and assignment stamp with the incoming proof. Evaluate effective expiry on fresh time after lock waits. While holding the thread lock, re-read the **complete** relevant candidate/pending set and its event-time history with narrow, nonlocking peer reads. Do not lock multiple shops. For an unscoped turn lock the thread and turn, acquire no shop locks afterward. For a fresh unquoted singleton, a competing contact provably eligible at the original provider second returns the appropriate unresolved handoff. A later contact adds no candidate. A verified quote or stored replay retains its original checkout subject to the historical/denied recheck. If a member closes before the write, a fresh unquoted event goes neutral, while a proved quote or stored replay keeps only its original history. Never rebind to the next generation.
2. Make `ConversationService.receiveMessageInternal` and `persistHistoricalInbound` transact with the recheck, parent first and child second. Extract the transaction-local processable write for BG004 reuse. For a fresh direct inbound combine its exact owner guard, provider-ID insert, actual TEXT/UNSUPPORTED contentType at insert, applicable `recordProcessableInbound(tx,...,{conversationAlreadyLocked:true})`, language and monotonic parent clocks in one transaction. Remove the unguarded pooled call to `checkoutRecoveryService.recordExternalActivity`: its implementation acquires a Redis checkout lock and uses global Prisma. Only a genuinely new, uniquely admitted live input can advance the exact current recovery's lastExternalActivityAt, and only if the verified event is later. Duplicates, unresolved or historical inputs cannot advance it. Roll back all side effects on message insert failure. Where language selection needs slow work, resolve only after a positive shop/checkout preflight, outside lifecycle locks, then repeat the guard inside the write transaction. Never invoke a tenant/model while choosing a shop. The specific provider-ID uniqueness race can recover after rollback in a fresh transaction under the same advisory lock by verifying BOTH stores, inbound direction and exact scoped owner. Any other P2002 is its original failure.
3. Keep provider occurrence separate from delivery/settlement time. Accepted ordinary text requires `createdAt=receivedAt` for the existing pending-batch partition. For a newly pooled, confirmed-owner CUSTOMER/INBOUND direct row, persist verified provider occurrence in existing `ConversationMessage.sentAt` at first insert; the outbound meaning remains unchanged. Audio retains its existing `createdAt=eventTime` and `transcriptionCompletedAt=completionTime`; historical insertion records eventTime. Use the stored first occurrence in duplicate repair and engagement, use receipt/completion for AI delay, keep the scheduler's lastInboundAt/lastMessageAt semantics, and derive the verified 24-hour window from the stored event via the qualified message evidence below. In `src/services/recovery-conversation/recovery-conversation.sql.ts#readRecoveryWindowEvidence` use the verified pooled inbound effective timestamp `COALESCE(msg."sentAt",msg."createdAt")` consistently in the predicate, selected maximum and ordering. Restrict this expression to confirmed CUSTOMER/INBOUND messages of a pooled conversation with an assignment. For older rows with a null stamp and existing non-pooled conversations use the established createdAt. Apply that same occurrence-time selection in `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts#process` when it filters/orders post-initial inbound messages and passes the time to engagement. Keep this query scoped to the original recovery. Do not backfill old timestamps. In `src/services/recipient-reachability-positive.service.ts#fromRoutedInbound` use the same verified stored event time for pooled rows (and the existing timestamp for non-pooled rows); delayed receipt processing must not override a newer reachability failure. Exercise an event replayed after 24 hours: routing proof never renews the customer-service window. Historical persisted evidence can repair only existing original-merchant reachability as previously permitted, and cannot advance active recovery/agent state.
4. Currently `ConversationService` calls `RecoveryOutreachAttemptService.markEngagedForConversation` after commit on fresh and duplicate rows, and audio invokes it before transcription. Preserve retryable post-commit repair, but fence the pooled repair in its own short same-owner transaction: re-read persisted INBOUND, original owner, verified timestamp and current eligibility; invoke the existing attempt selection/update semantics transaction-locally. Do not reacquire ownership in a different conversation. A closure after the primary commit skips engagement/AI scheduling. Ensure before-enqueue checks, positive-reachability calls, audio fallbacks and historical/unsupported paths consume only the verified committed result. Rejected/mismatched/unresolved rows produce none of these effects. A duplicate may repair the original missed enqueue/version once through the existing scheduling/dedup key.

### 4. Voice and delayed AI turns

- **Audio reservation**— `src/services/whatsapp-inbound-processing.service.ts#processRoutedInboundMessage` passes the admitted, immutable owner to `src/services/inbound-whatsapp-audio.service.ts#reserve/process/processInternal/complete`. The snapshot does an unlocked find/create followed by global engagement. In the new pooled path take the provider-ID/owner locks in a short transaction and verify existing message direction, content type, original customer/conversation, receipt scope and media identity on a duplicate. Use the original persisted media reference, provider timestamp and quote; a differing replay cannot fetch another file. Reserve once, record newly eligible activity and repair eligible engagement under its original owner. Bind the existing attempt update through a transaction-scoped instance of the service from `src/services/recovery-outreach-attempt.service.ts#markEngagedFromInbound` with its original timestamp/sequence criteria. Historical audio only reserves its original metadata. Before shop or basket resolution BG003 returns the handoff without a checkout reservation or transcription. BG004 can use platform speech after it has durably admitted that event.
- **Audio completion and side effects** — Perform metadata/download/parsing/transcription outside DB locks. Keep the MIME/size/duration limit, retryability, stale-order check and final-attempt rules. After slow I/O, re-read the **same** proof and original reservation, including current lifecycle, under the ordered locks inside `complete` before the PENDING-to-COMPLETED update and `recordProcessableInbound`. If no longer eligible, leave the reservation historical without attaching a transcript, engaging, updating clocks/versions, enqueuing or sending fallback. For a proved current owner keep provider occurrence time for customer-window clocks and completion time for the pending AI delay. Return a disposition distinguishing loss of owner from successful persistence: the current caller runs `recipientReachabilityPositiveService.fromRoutedInbound` even on ignored audio. Call any repair only for a verified committed original inbound permitted for that effect. Revalidate immediately before enqueue or `voice-fallback:` dispatch; preserve BG002's final permit and frozen control revision. Provider body text, transcript and media URLs stay out of diagnostics. In `whatsapp-media.service.ts#downloadAudio` and `speech-transcription.service.ts#transcribe` retain source-specific network/config/read/parse causes and safe provider status/details prior to the existing typed conversion. Log storage or finalization failures separately from download or speech failures; preserve the first originating failure on propagation.
- **Delayed turn** — Keep the existing `process-conversation-turn` payload, stable conversation/version job IDs, delay, repair and worker concurrency. In `src/services/conversation-turn-processor.service.ts#ConversationTurnProcessor.process`, add a production-injected owner check before `moderation.moderatePending`, in the claimed-turn try/cleanup path. Call the same BG003 eligibility reader in `src/workers/whatsapp.worker.ts#loadConversationTurn` before rich customer/message selection and `checkoutRecoveryService.getAgentContext`. A terminal linked recovery currently falls into the general execution-scope test. Resolve using its own persisted conversation and sender history, never another current recipient owner or a general fallback. Scope-less older jobs still use the persisted owner. Keep genuine non-pooled callers under their existing eligibility rules; a missing assignment alone never authenticates an older recovery. In the processor repeat the original eligibility check after slow awaits, directly before agent invocation, and before any prepared send; keep the AI/HUMAN revision gates and BG002 final permit. Use existing `finishInactiveTurn` for stale pooled owners and `finishSuppressedTurn` for control changes; finish only the claimed version and dispose only its own unadmitted prepared outbound. The default production check must run even when pendingAiControlRevision is absent. A failing check throws its original error and releases the claim for retry. In both cleanup catches currently creating AggregateError, retain each distinct scoped primary/secondary record and propagate the first original failure. No model, moderation, provider or media call under a DB lock.

### 5. STOP and neutral guidance

| Touchpoint | Required decision |
| --- | --- |
| `src/services/whatsapp-inbound-processing.service.ts#processRoutedInboundMessage`, `whatsapp-contact-opt-out.service.ts#WhatsAppContactOptOutService.handleInbound`, `whatsapp-contact-opt-out/phone.ts` (last two under `src/services/`) | Keep explicit typed STOP first, **before raw abuse admission**, routing, moderation, audio or agent work. Preserve `isExplicitWhatsAppStop` exactly (trimmed case-insensitive STOP/UNSUBSCRIBE, optional single period/exclamation). Verify the event's receiving account/phone and canonical customer. Unknown sender or unparseable recipient is consumed without any mutation, guidance or ordinary routing. |
| `src/services/whatsapp-contact-opt-out/quoted-outbound.ts#resolveQuotedStopShop` | Resolve the quoted ID against both outbound `ConversationMessage.providerMessageId` and `RecoveryBasketRoutingTurn.promptProviderMessageId`. Require a single verified source. For a merchant message require confirmed OUTBOUND with sentAt, matching original sender, original recipient and merchant. For pooled use immutable conversation → assignment → route → thread → inventory, including closed history. Verify all available command/attempt recipient and owning shop/recovery links. For merchant/AI replies verify the conversation's original contacted recipient using its confirmed initial outreach and original thread. A mutable Customer.phone alone cannot prove who received an old message. Preserve evidenced non-pooled merchant outbound. A verified expired message may still identify the merchant for STOP without activating its recovery. |
| Same quote resolver, clarification-prompt branch | Require exact prompt ID, non-null promptAdmittedAt and promptSentAt and correct immutable thread generation, recipient, phone and WABA. Only a non-null original `promptScopeRouteId` with its own matching historical route, thread and shop can establish `QUOTED_SHOP`. A neutral prompt with a later populated `routeId` remains neutral even after terminal content scrubbing. Missing/deleted route, colliding IDs, unverified/cross-sender quote, generic guidance and unquoted STOP on a recognised sender all use `ALL_REGISTERED_SHOPS`. A database exception propagates and makes no consent decision. |
| `src/services/whatsapp-contact-opt-out/stop-writer.ts#writeLocalStop` and `publishStopNotices` | Reuse the existing local suppression writer, canonical-recipient lock, stable shop lock order, exact active CustomerPhone matching, revision CAS and post-commit source-key-deduplicated support notices. The registered shops can include shops with no active basket. Do not update upstream provider-consent fields. Preserve the original no-contact timestamp on replay. Log each failing per-shop notice separately with its source diagnostic and internal shop ID, complete the independent notices then rethrow the first original error so existing BullMQ repair can retry safely. |
| `src/services/routing-guidance.service.ts#sendRoutingGuidance` | Use the positively recognised pair again before send. Keep approved static shop-neutral copy, unsupported suppression, canonical phone check, existing environment-specific Redis key (SHA-256 over inbound provider ID), `SET EX 86400 NX`, existing SQL recipient STOP fence and 10-second deadline. For a free-form guidance reply use the authentic event time and a fresh post-lock clock at the SQL permit; authorize only within the existing strict 24-hour customer service window and reject future events. Suppress out-of-window guidance with an explicit local reason, including for a late job. Keep STOP processing independent of this outbound condition. Call BG002's `sendWhatsAppText({to,text},sender,signal)` outside the transaction. Preserve the NX guard on an uncertain send; no automatic second POST, commerce grant, checkout attachment or charge. Keep the distinct cache, DB admission, sender-resolution and provider failure stages and current public guidance outcomes. A routing/ownership read failure upstream propagates to BullMQ. A strictly best-effort guidance transport failure retains its existing typed outcome and NX guard. BG004 owns option-bearing store/basket prompts. |

### 6. Provider status and downstream effects

The `message-status` branch in `src/workers/whatsapp.worker.ts` calls `WhatsAppProviderStatusService.process` in `src/services/whatsapp-provider-status.service.ts`. Keep Shared v2/v3 validation, `withRetry`, Serializable isolation, existing CAS checks and public `"invalid" | "unknown-message" | "ignored" | "applied"` contract. Return one internal committed result per transaction attempt with public outcome, reason, message ID (if verified), and `postCommit: "none" | "failed" | "positive"`. Return diagnostic data from the winning transaction. A rolled-back/retried transaction cannot enable post-commit work.

1. Query both exact provider-ID namespaces within that transaction. No match is unknown-message. A collision is rejected. Look up the inventoried phone by ID to reject a conflicting WABA, including disabled rows. A non-pooled historical pair authenticated by its original message or prior usage can still be valid after the dedicated configuration rotates. For a conversation message, preserve existing Shop and message lock order, then re-read and verify OUTBOUND, stable provider ID, same conversation/recovery/shop and immutable physical sender before any lifecycle, command, attempt or usage write. Status envelopes contain no recipient phone. A closed or superseded original route is valid historic sender evidence. Never look up the presently active recipient owner. For a non-pooled message use the two dispatch fields together. With neither field and no assignment, accept only a pre-existing same-shop `billing.UsageEvent` at `deliveredUsageKey(message.id)` (`src/services/whatsapp-provider-status-lifecycle.ts`), metric DELIVERED_WHATSAPP_MESSAGE, sourceType WHATSAPP_PROVIDER_STATUS, sourceId exact internal message ID and parseable `providerResponseSummary` JSON with DELIVERED/READ and both IDs. Refuse incomplete/conflicting evidence, invalid/truncated JSON or wrong pair. Read the old record before any upsert. Never manufacture historical proof from this callback. A new properly pinned standalone message can receive its first status without an older usage record.
2. A confirmed prompt uses its original prompt receipt, thread, account/phone and frozen scope (if merchant-specific, prove the original route). Handle correct prompt as acknowledgement only: public ignored, internal verified-prompt, no checkout/turn lifecycle mutation, usage, billing, reachability, support or notification. R07 has no delivery-status column on routing turns. BG004 freezes the prompt permit and saves a positive send receipt, including after terminal content scrubbing. BG003 cannot use an unmatched status to fill an unknown prompt receipt, change IGNORED to AWAITING_REPLY or resend. Valid-looking incoming metadata alone is insufficient.
3. On a proven owned message preserve `canApplyProviderStatus`, `statusForProviderEvent`, existing `lifecycleUpdate`, first-delivered usage upsert, HUMAN command CAS and exact v3 131026 attribution. Replays may enrich null failure evidence or repair failed post-commit effects. For FAILED set `postCommit:"failed"` only on a permitted transition or exact FAILED duplicate. For DELIVERED/READ use `positive` on a permitted transition, repeat or compatible lower DELIVERED event on an already READ message (preserves deliveredAt backfill and delivery repair). SENT, stale negative events after positive delivery, invalid owner/sender, collision, unknown or inbound-only pointer all set `none`. Perform corrections only against the original outbound. An old receipt never reopens an expired checkout, moves a thread or attributes a different shop's charge.
4. Replace **both** post-commit tests currently based on `outcome !== "unknown-message"`. Failed repair still runs `compensation.reconcile` → `failureReachability.afterCorrection` → `notification.notify` in dependency order, through their existing `runAfterCommit` stages. Positive repair calls only `positiveReachability.fromProviderDelivery`. A dependency failure propagates its original error so retry re-verifies the same owner and repairs the committed row. Independent valid duplicate repairs remain possible even when public result is ignored. A forged/wrong-sender FAILED or DELIVERED with a real provider ID triggers none of the four operations.

### 7. Per-stage diagnostics, retry and privacy

Use the existing Shared structured logger, following parent `docs/observability/shared-logging.md`. Reuse the safe diagnostic projection introduced with BG001/BG002 and the local provider-status database metadata allowlist. Existing compatible domain event names can stay. At the failure source record one event per operation per affected message, occurrence and attempt, with deployment/service, operation, stage, reason, original exception class and original safely redacted message. Retain Prisma code and separate SQLSTATE, constraint, safe provider HTTP status/code/subcode/trace and Redis/BullMQ code when supplied. Preserve relevant bounded causes. Correlate by the existing opaque provider-message digest and verified internal IDs. Do not log raw inbound/quoted IDs as free text, job payload, customer phone or its hash, message or transcript, merchant aliases, item details, URLs, headers, credentials or raw response/SQL. A malformed upstream response is not permission to log a body echoed in a parser error.

| Failing stage | Required distinction and outcome |
| --- | --- |
| `classify_sender`, `load_thread`, `load_owners`, `verify_quote`, `compare_event_time`, `recheck_owner` | Log the exact read or verification exception and leave merchant state untouched. Unrecognized pair, invalid reference, stale generation and clock ties are expected decisions with their own precise reason, never synthetic exceptions. |
| `persist_inbound`, `reserve_audio`, `fetch_media`, `transcribe`, `complete_audio`, `repair_engagement`, `enqueue_turn`, `release_claim` | Separate committed state from proposed writes. Distinguish a provider error from failure persisting its outcome. A queued duplicate can repair only legitimate unfinished effects of its same committed owner. |
| `stop_scope`, `stop_write`, `publish_stop_notice`, guidance Redis admission, SQL admission and provider send | A failed evidence query cannot become broad STOP. An actually invalid quote on an authenticated explicit STOP does use the broad registered-shop scope. Log each failed independent shop notice, preserve committed suppression, then propagate the first original notice failure. Best-effort guidance retains its own typed result and the existing no-repeat behaviour for uncertain delivery. |
| `status_transaction`, `compensation`, `failure_reachability`, `merchant_notification`, `positive_reachability` | Track each transaction retry with original cause and attempt. Use a verified committed disposition to select the effect. If compensation fails, record it and stop before the dependent operations. If it succeeded but notification failed, record the true failing stage; the next valid replay repairs idempotently. |

When primary handling and independent cleanup both fail, emit two separately correlated records and propagate the first original thrown value, including when logging at an outer stage. No combined-only event, generic replacement or swallowed downstream exception. Keep stable public credential/transport error contracts and the existing handling of definitively rejected or unknown provider calls. Only source-safe projections enter logs. Inject a Shared sink in tests and assert serialized original messages, redaction, stages, IDs and thrown identity, including independent errors for two affected shops and primary/secondary errors on one turn.

## Work Items

- [ ] Implement the exact sender, legacy, replay, quoted-message and event-time ownership reads in the active production path. Provide both local handoffs and the shared, transaction-local recheck.
- [ ] Fence new text, unsupported and voice writes, history, deduplication, positive reachability and delayed work. Preserve first occurrence, independent retention/scheduling clocks and original checkout continuity through closure.
- [ ] Wire scoped STOP and same-number neutral guidance. Protect the serializable status writer and every post-commit repair owner. Emit separate safe stage diagnostics.
- [ ] Prove the decision matrix through the live worker/service entry points, using independent database connections, real Redis, and fake provider/model I/O. Fill in the Completion Report with reproducible evidence.

## Interfaces / Contracts

BG003 adds only Background-local types. Export the two handoffs and shared owner guard from `src/services/recovery-sender-route.ts`. The normalized event and provider types come from their existing modules. Physical-number identifiers, canonical recipient and original provider IDs are server-only. A serialized receipt stamp uses ISO UTC timestamps and separate internal/provider IDs.

```ts
type MemberStamp = Readonly<{
  routeId: string
  conversationId: string
  recoveryId: string
  generation: number
  assignedAt: string
  initialAttemptId: string
  initialMessageId: string
  initialProviderMessageId: string
  initialSentAt: string
}>

type ShopStamp = Readonly<{
  routeId: string
  routeOpenedAt: string
  shopId: string
  domain: string | null
  brandName: string | null
  members: readonly MemberStamp[]
}>

type VerifiedQuote =
  | { kind: "checkout"; providerMessageId: string; messageId: string;
      shopId: string; routeId: string; conversationId: string;
      initialOutreach: boolean }
  | { kind: "prompt"; providerMessageId: string; originalTurnId: string;
      promptScopeRouteId: string | null }

type ThreadEvidence = Readonly<{
  threadId: string
  openedAt: string
  canonicalRecipient: string
  sender: Readonly<{ providerAccountId: string; providerPhoneNumberId: string }>
  inboundProviderMessageId: string
  occurredAt: string
  pendingRootIds: readonly string[]
  quote: VerifiedQuote | null
}>

type UnresolvedInbound =
  | { kind: "sender-thread"; evidence: ThreadEvidence; shops: readonly ShopStamp[] }
  | { kind: "shop-route"; evidence: ThreadEvidence; shop: ShopStamp }

type AcceptUnresolvedInbound = (
  event: WhatsAppInboundEvent,
  handoff: UnresolvedInbound
) => Promise<void>
```

1. Use `kind:"sender-thread"` for multiple eligible shops, a previously unresolved neutral root or a verified neutral prompt response, even if the live set is now empty or singleton. Use `kind:"shop-route"` for a proven shop with several possible baskets or a verified applicable shop-specific pending root. A verified historical original quote only has its own historical path. An unsupported message never creates a BG004 text/audio clarification. On a genuinely unresolved unsupported event return without basket attachment or outgoing guidance. Keep `resolved`, `guidance` and `ignored` in the existing `RecoveryRoute` union. A pooled resolved result carries original thread, shop, selected member, sender and source discriminant (`stored-replay`, `checkout-quote` or `fresh-single-member`). A historical direct quote/replay on a non-pooled sender uses its independently proved original owner without fabricating a thread. On `shop-route`, pending roots are limited to this shop and attributable thread-level roots proved relevant to the supplied quote. Route-private labels, order contents and other merchants' grants are never sent to the single-checkout agent.
2. Add an optional final in-process `acceptUnresolvedInbound` dependency to `processRoutedInboundMessage`. For either verified branch call it **once per processing invocation** with the untouched normalized event and evidence and await it. An injected failure propagates on the existing job. Without a consumer return the typed unresolved result for inspection, without a basket write, customer-facing choice prompt or agent call. Do not silently enable this intermediate worker for live pool traffic. BG004 persists the original content and selection state with its existing strict size/digest rules before interpreting it. Delivery can repeat. The consumer must use the shared provider-ID lock for once-only effects.
3. For every ownership insert/replay lock all participating provider message IDs with parameterized `pg_advisory_xact_lock(hashtextextended('whatsapp-inbound-owner:' || $1::text, 0))` before business locks. De-duplicate and order multiple IDs by UTF-8 bytes. Read both `ConversationMessage.providerMessageId` and `RecoveryBasketRoutingTurn.inboundProviderMessageId` under that lock. Use separate lookups on `promptProviderMessageId` and outbound message ID when proving a quote. A row in both inbound stores must be BG004's matching terminal projection. A mismatching direction/owner/role or duplicate with changed identity cannot run new work. For a verified replay use the original stored content and references. For a newly ingested direct message on replay, compare the authenticated customer/sender, stored original occurrence and original context where present; for voice also compare the persisted media reference. If the normalized redelivery supplies conflicting identity, skip merchant effects, retain the stored owner and log the bounded mismatch. Never use a redelivered body to overwrite the original. A raced insert is recoverable only on the precise provider-ID unique constraint, followed by reloading and verifying the winner in a valid transaction. Other unique/DB errors propagate.
4. Make `revalidatePooledInboundInTransaction(tx, expected, event)` return the existing typed disposition with the newly checked proof before attaching an event. Use the production path's parent/child order and BG001's `requireAssignedSender(..., phase:"ongoing")` for the chosen active checkout. Check the exact returned route, `assignedAt` and sender, current cutoff and generation, using fresh database time after the locks. Verify all candidate and pending-root identities again under the thread lock. Do not lock a peer shop while holding the thread. Stronger proof from a fresh read can never move a previously stored event to a new owner. BG004 can call the same guard inside its projection transaction without opening a nested transaction or posting to Redis/Meta.
5. For a representable but indeterminate event on a positively established original thread, write one content-free R07 `IGNORED` row with its inbound ID, thread ID, known route ID or SQL NULL, and verified occurredAt. Input, candidates, moderation, parent, selected conversation, prompt text, scope, admission and receipt are SQL NULL. Database defaults own creation/update time. A replay has zero active effects. When no original thread can be established, return neutral without inserting under a successor. Shared rejects malformed envelopes before this logic, so never synthesize occurredAt. A valid unresolved question uses the handoff instead of this tombstone.
6. On an existing routing row preserve terminal scrub and prompt scope. A verified BG004 `RESOLVED` row with `{v:1,role:"selectionOnly"}` may be a neutral merchant selection without a ConversationMessage. Match its original thread, selected conversation if retained and valid control lineage; acknowledge the control without manufacturing merchant text. A missing expected objective projection or unverifiable/deleted owner grants no new right. An `IGNORED`/terminal row may still have a verified prompt receipt for historical recognition or STOP. R07 holds no independent delivered/read/failed columns for prompts.

## Dependencies

`ARCH-069-BACKGROUND-002` accepted and integrated, including the R07 database pin and R08 BG001 exports. Applying an architectural handoff does not fulfil this execution dependency.

## Enables

[BACKGROUND-004](BACKGROUND-004-resolve-same-shop-baskets-and-clarify-replies.md) consumes **both** the multi-shop sender-thread result and the single-shop basket result. It implements selection, independent question retention, clarification and resumption of the authentic customer request in one checkout conversation.

## Acceptance Criteria

- [ ] Implement and cover the inventory classifier, pooled indexed lookup, explicit proof and exact UTC timestamp boundary. An unquoted reply can route even with eligible recoveries at two different shops. A pair with no active/confirmed owner never attaches by proximity.
- [ ] Demonstrate expiration at and before the inclusive cutoff, including before the sweep, followed by reuse for the same recipient at a different shop. A new post-confirmation free-text and voice reply enter only the new conversation, and a pre-send/boundary-second webhook, old quote and replay do not. A separate recipient on the same Moda phone remains independent.
- [ ] With one enabled number, positively identify two simultaneously contacted merchants on the same thread. Verify both store candidates reach only the neutral handoff, no foreign checkout facts are projected, HUMAN/AI original outbound quotes retain their exact owners, and a pre-/post-close delayed webhook cannot inherit the surviving shop. Test that a neutral prompt remains neutral for quoted STOP/status after binding and after terminal scrub.
- [ ] With three confirmed distinct same-shop checkouts, return all three to the resolver on the same sender. Keep a second shop on another sender and exclude its similarly named products. A quote of any eligible member takes its exact path. A wrong sender, unconfirmed outbound or ineligible member grants no evidence.
- [ ] Check replay during/after clarification including simultaneous duplicate deliveries, matched and stale prompt quotes, unrelated quoted basket messages, customer answers when only one displayed candidate remains, and the strict same-second boundary on one of multiple members. Verify no provisional checkout action or delayed cross-tenant effect, and that statuses for a prompt cannot touch billing, reachability or notices.
- [ ] Regression: first recovery A's dispatch result is initially unknown. Expire A, reuse its number for B, confirm B's first send, process an eligible fresh reply for B, then reconcile A's late receipt/status and redeliver the inbound event. B retains the assignment, inbound row and original version. A's receipt/status is historical, its release timestamp stays set, and a subsequent valid unquoted reply still goes to B. A new quoted A message can use only the ordinary historical path.
- [ ] Exercise changed owner during text persistence and between audio reservation and finalization with concurrent real PostgreSQL transactions and deterministic barriers. Assert durable conversation IDs, inboundVersion, activity time, attempt engagement and mocked enqueue/AI/media/guidance side effects. Test delayed turn after closure. Preserve genuine duplicate repair and all existing human/AI, moderation and 24-hour gates.
- [ ] Test quoted/standalone/invalid-quote STOP after reuse and on an allocation-disabled sender, unknown WABA, wrong phone, changed recipient, positive status on the old send, poisoned cross-sender FAILED and repeated valid FAILED/DELIVERED. Assert exact suppression scopes and absence of every incorrect write and post-commit call, with proper repair for the valid duplicates.
- [ ] Exercise a non-enrolled verified singleton and ambiguous legacy input per the cutover contract. A non-pooled first callback with a stored dispatch pair is valid. An unpinned historical send with exact prior stored delivery evidence is valid; corrupt/missing prior evidence stays unresolved even for unchanged current credentials. Drained pooled identities cannot take the singleton fallback. Existing general messages cannot be reclassified as a checkout.

## Validation

Run through the existing Background worker/service entry points with disposable PostgreSQL 17 + pgvector and Redis. Use a loopback/fake WhatsApp transport, media service, speech provider, model and merchant-notification publisher. No live provider/model calls. Add `tests/integration/pooled-inbound-routing.integration.test.ts`, `tests/integration/pooled-status-routing.integration.test.ts` and focused fixtures/assertions under `tests/integration/helpers/`. Reuse `arch056-inbound-barriers.ts` and `arch056-inbound-fixtures.ts`. Keep tests modular. Upgrade old positive fixtures that contain only a provider ID and mutable customer phone with a real pin or immutable member and original recipient. Keep the old weak fixtures as negative tests.

| Case | Evidence required from the implementation |
| --- | --- |
| Free sender versus shared sender | Same customer in two shops on different numbers routes directly to the correct single contacted checkout. On one occupied number for both shops, the unresolved consumer sees both permitted shop stamps and original event. No basket writes, agent, media, language detection or debit. Same shop with three valid baskets yields all three. Include at least one different customer on the same number and another shop with similar labels. |
| Quote, pending questions and replay | Test active, historical and invalid original quotes, neutral and shop-specific prompt quotes, and unrelated quoted HUMAN/AI answers. In seeded BG004-compatible fixtures, a neutral question becomes shop-bound without changing its original prompt scope. Preserve two independent roots, original text/audio reference, exact reply-to ID and candidate stamps. When only one displayed choice survives, deliver the answer to the pending owner, never directly to that survivor. Verify no duplicate projection or artificial text for a resolved merchant-selection-only control. |
| Timing and expiry | Cover one second before, equal to and after first confirmed contact; opening, closure and reuse boundaries; fresh unquoted event with an ended possible owner; inclusive lifetime cutoff including zero days before sweep. Prove strict original provider time across replay and historic claims. A delayed accepted text arriving more than 24h after it was written cannot authorize a new in-window response. A job with an invalid normalized timestamp writes nothing. An indeterminate but valid one under proven thread scope writes only its content-free tombstone. |
| Concurrency and restart | Force contention in separate PostgreSQL sessions at provider-ID insertion, membership release, candidate-set change, message write, voice completion and pending-turn processing. Exercise both commit orders using barriers. Check the exact-owner UNIQUE conflict and an unrelated error. A crash after commit or enqueue failure repairs the original version once; an old or conflicting owner cannot be rebound. Test the closure gate before moderation/context load and after external I/O. |
| Text/audio and clocks | Verify correct insertion type, ordinary receipt time for batching, provider occurrence for customer-window/engagement, transcript-completion time for AI scheduling, HUMAN versus AI behaviour and bounded audio retries. No context/credits/transcription on unresolved input in BG003. Assert the exact permitted post-commit reachability call or absence for each owner. |
| STOP, guidance, status | Test quoted, unquoted, forged/missing and neutral-prompt STOP, drained numbers, one shop active while another registered shop has no basket, unknown account and failed DB read. Verify exact no-contact rows, original timestamps/revision, separate notice failures and successful notice repair. Capture guidance phone, recipient, request count, Redis duplicate suppression, post-STOP refusal and 10-second budget. |
| Receipts and failures | Exercise v2/v3, first callback to a pinned standalone, valid pre-existing legacy usage, malformed/partial/conflicting history, unknown response, prompt/checkout ID collision, late receipt after reuse, v3 131026 and contradictory/out-of-order statuses. For `FAILED` and `DELIVERED/READ` verify actual row changes and exact post-commit call counts. An owned compatible duplicate repairs; a mismatching duplicate produces zero effects. Test older DELIVERED after READ and failed post-commit notification on retry. |
| Diagnostic isolation | Show three separate safe source messages for a DB/queue/provider failure and a case with a secondary failure against the same original event. Two independent per-shop failures remain distinguishable. Add secrets, phone, message/media text and provider-echoed private values to fixtures and assert their absence in serialized records. |

Run from the launcher-prepared Background repository. The integration script sets up the disposable database/Redis fixtures. Record case outcomes, runtime versions and cleanup.

```bash
npm ci &&
npm run prisma:generate &&
npx --no-install vitest run \
  tests/unit/services/recovery-routing.service.test.ts \
  tests/unit/services/whatsapp-inbound-processing.service.test.ts \
  tests/unit/services/conversation.service.test.ts \
  tests/unit/services/conversation-turn-processor.service.test.ts \
  tests/unit/services/inbound-whatsapp-audio.service.test.ts \
  tests/unit/services/whatsapp-media.service.test.ts \
  tests/unit/services/speech-transcription.service.test.ts \
  tests/unit/services/recipient-reachability-positive.service.test.ts \
  tests/unit/services/whatsapp-contact-opt-out.service.test.ts \
  tests/unit/services/routing-guidance.service.test.ts \
  tests/unit/services/whatsapp-provider-status.service.test.ts \
  tests/unit/domain/whatsapp-provider-status-transition.test.ts \
  tests/unit/workers/whatsapp.worker.test.ts &&
node scripts/test-integration.mjs \
  tests/integration/pooled-inbound-routing.integration.test.ts \
  tests/integration/pooled-status-routing.integration.test.ts \
  tests/integration/recovery-recipient-routing.integration.test.ts \
  tests/integration/woo-recovery-inbound-routing.integration.test.ts \
  tests/integration/whatsapp-contact-opt-out.integration.test.ts \
  tests/integration/routing-guidance-stop-fence.integration.test.ts \
  tests/integration/recovery-human-provider-status.integration.test.ts \
  tests/integration/arch056-inbound-lock-order.integration.test.ts \
  tests/integration/arch056-inbound-rollback.integration.test.ts \
  tests/integration/arch054-pending-turn-repair.integration.test.ts \
  tests/integration/recovery-follow-up-claim-races.integration.test.ts &&
npm run build &&
npm run lint &&
git diff --check &&
git diff --cached --check
```

Confirm production coverage with the following inventories. Record each actual write, provider call or post-commit repair owner and its verified gate. Keep template-status jobs and ordinary non-recovery behaviour covered by existing tests. No silent skips.

```bash
rg -n 'resolveInboundMessage|isCurrentActiveRoute|persistHistoricalInbound|receiveMessage|markEngagedFromInbound|recordExternalActivity' src/services
rg -n 'processRoutedInboundMessage|loadConversationTurn|moderatePending|getAgentContext|readRecoveryWindowEvidence|fromRoutedInbound' src
rg -n 'resolveQuotedStopShop|writeLocalStop|publishStopNotices|sendRoutingGuidance|runAfterCommit|fromProviderDelivery|afterCorrection' src/services
```

## Implementation Notes

Use `/moda-task ARCH-069-BACKGROUND-003` when BG002 is accepted and integrated. Record launcher-prepared parent and implementation worktree paths, branch names and starting/ending SHAs, recursive database gitlink and command output. Check off Work Items and Acceptance Criteria and submit the Completion Report for architect review. Keep new production identifiers descriptive of the domain and retain existing durable keys.

The intermediate build must stay out of live pooled traffic until BG004 consumes the unresolved handoff and the coordinated Admin/Background release is ready. The intermediate handoff is observable to integration tests in-process. No second BullMQ routing job is needed. Report missing accepted symbols/columns, irreconcilable proof or an actual baseline/build failure by path, command, original error and violated invariant. Distinguish an incompatible prerequisite from a missing test dependency. A legitimate unknown sender, bad quote or expired checkout is an expected runtime result, never an architectural blocker.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Awaiting execution.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Awaiting implementation.

### Follow-up

None.
