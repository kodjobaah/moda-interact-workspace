# Background initial recovery progress: U2 and C3

## Scope and conclusion

This is a static architectural investigation of the updated archive `moda-interact-workspace(20261103-212722).zip`. Background paths below are relative to its `moda-interact-background/` directory; Shared paths explicitly name that project. No application implementation, task status changes, live database or provider calls, or credentials were used. The tests discussed below were inspected, not executed by this investigation.

**U2 and C3 form one incomplete progress protocol.** The new neutral fallback reads the wrong identity namespace, but replacing that string alone will not restore progress. The real Shopify candidate worker normally stops at an existing `DETECTED` recovery; direct initiation prepares a fresh template and obtains current billing admission before inspecting an existing durable message; and fallback refuses attempts that have already acquired their final outbound link. A confirmed send can therefore be stranded after any of the billing, Support, attempt, recovery-status, or follow-up scheduling boundaries.

The smallest coherent correction is to let the existing candidate/initiation owner classify persisted initial-outreach progress before preparing a new send, using the existing recovery, sequence-one attempt, usage, message, reservation, and Support identities. Reuse the canonical admission lookup with a narrow projection extension. Resume a proven unadmitted message through the existing delivery service; hold a permit with an unknown provider outcome; reconcile a confirmed message through the existing billing/finalization owners. Never infer provider failure from an exception or from attempt status alone. No new generic queue, outbox, attempt sequence, or persistence table is justified by this evidence.

There is an explicit limit: existing data and billing helpers cannot prove one original paid reservation when several historical/current candidates exist, and a historical paid reservation that remains `RESERVED` or `AMBIGUOUS` cannot always be committed through the current policy. These cases remain visible reconciliation conflicts linked to BS-05. They are not permission to charge a newly selected source.

## 1. Durable identities and what they prove

| Identity or field | Writer and evidence | Meaning for replay |
|---|---|---|
| `(shopId, checkoutToken, generation)` | `database/prisma/schema.prisma:351`, unique declaration at 390; `recovery-initiation.service.ts:74` | Identifies the recovery generation. Ordinary incomplete-send retry must retain it. An expired-generation admission is a different lifecycle. |
| `(checkoutRecoveryId, sequence=1)` and attempt `id` | Schema 429/460; `recovery-outreach-attempt.service.ts:22` uses `upsert`, `update: {}` | Preserves one initial attempt and its original recipient/offer configuration. Replaying a send must not create sequence two or replace this ID. |
| `recovery-outreach:<attemptId>` | `recovery-initiation.service.ts:353`; `outbound-admission-reservation.service.ts:155` | The **hard-limit UsageEvent.idempotencyKey**, with `sourceId = message.id`. It is not a provider-dispatch key. |
| Shopify `arch040-auto-<sha256(messageId)>` | `recovery-conversation/outbound-send-fence.service.ts:232` | Atomic provider permission for one message. It proves admission, not successful provider delivery. It cannot be reconstructed from attempt ID alone. |
| Woo `arch046-woo-initial-<sha256(shopId + NUL + attemptId)>` | `woocommerce-recovery/woo-initial-send-fence.service.ts:248` | Attempt-scoped final permit. A lookup at 252 independently prevents a second permit even if a UsageEvent is missing. |
| `providerDispatchKey`, `providerDispatchAdmittedAt` | Message schema 693; final-fence updates | Either non-null is sufficient to stop an automatic resend when no confirmed outcome exists. A crash after permit commit but before HTTP is observationally indistinguishable from a crash after HTTP without its receipt. |
| `providerMessageId`, `status`, `sentAt` | `outbound-message-delivery.service.ts:488` (`markSent`); provider-status service | Durable `SENT`/`DELIVERED`/`READ`, non-null `sentAt`, and validated ownership are the current finalization evidence. A provider ID enables webhook correlation; a permit key does not. |
| Attempt `outboundMessageId`, `sentAt`, `followUpDueAt`, `status` | Support finalizer atomically links the confirmed initial send; synchronous 131026 evidence also links a failed message | These fields are valuable secondary lineage, but status alone is insufficient. Shopify currently sets `FAILED` on ambiguous provider errors. A missing link before finalization is normal. |
| Recovery-credit `UsageReservation.sourceKey` | `recovery-billing.service.ts:99`; Shared `src/billing.ts:308`; paid reservation service 195 | Logical source uses `createRecoveryIdempotencyKey(shopId, 'recovery-outreach:<attemptId>')`. Paid included source additionally embeds its period. Reservation owner FKs and status must identify the exact debit/commit/release. |
| `recovery-initial-outreach:v1:<attemptId>` | `recovery-initial-outreach-support-notice.service.ts:51` | Unique Support notification for the original successful attempt. Preserve the atomic attempt transition plus optional notice insertion. |
| Follow-up job ID from recovery/sequence/due date | `domain/recovery-outreach-follow-up.ts`; `recovery-outreach-follow-up.service.ts:13` | The persisted due date permits idempotent publication after a queue failure. It does not prove that publication happened. |

The outbound automated-message UsageEvent and the recovery-credit reservation/committed recovery UsageEvent serve different accounting purposes. Do not collapse them because both include the attempt identity somewhere in their key.

## 2. Actual Shopify execution and retry path

### Candidate to durable recovery

`workers/pending-recovery-candidate.worker.ts:149` invokes `materializeMaturedCandidate`, not direct initiation. It passes `retrySuppressionAdmission` only when a prior failed reason contains one of two recipient-suppression markers (`:237`). After both successful and failed materialization it removes matured candidate indexes (`:176`). It rethrows materialization/cleanup failure, preserving both when necessary. The queue is configured for three attempts, exponential backoff starting at one second, removal on completion, and retained failed jobs (`services/pending-recovery-candidate.service.ts:49`).

`recovery-materialization.service.ts:50` checks execution eligibility, resolves domain, enters the checkout lock, repeats eligibility, checks the Redis processed-order marker and candidate supersession, and reads the latest recovery. An existing `DETECTED`, `MESSAGE_SENT`, or `ENGAGED` row ordinarily returns `no-op-existing` at 103. Only the suppression retry flag permits a `DETECTED` reentry. Fresh materialization then reads current abandoned-checkout state, builds the saved snapshot, resolves the recipient, and initiates.

Consequently, a required-state failure after recovery insertion can fail the first BullMQ execution and still cause the second execution to complete successfully without revisiting the failed work. The retained SQL row survives, but the job is acknowledged and removed. Candidate index cleanup is not itself a durable continuation mechanism. Conversely, merely retaining indexes or increasing BullMQ attempts would not repair the SQL short circuit.

Current eligibility and order guards also precede the existing recovery lookup. If they now deny a new send, they can prevent settlement of an earlier confirmed send. A correction must separate settlement of an existing receipt from authorization to create another send, while preserving tenant/platform identity checks for both.

### Recovery to prepared initial attempt

`recovery-initiation.service.ts:146` reads shop/latest recovery, performs first/reentry consent and reachability checks, upserts the recovery, resolves/attaches customer, then returns early for non-`DETECTED` state. Only this direct non-`DETECTED` path calls `ensureScheduledInitialFollowUp` for already-sent/engaged recoveries (208).

For `DETECTED`, it resolves current policy, recipient, stored consent and suppression; applies an optional admission gate; upserts sequence one; and calls automated template preparation (250–265). An unavailable template returns the current recovery without a retry signal. A thrown fallback `RETRY` does reach BullMQ, but the ordinary materializer short circuit blocks its next attempt.

The automated template facade reads recovery and lifetime before entering the new fallback (`recovery-template-integration/automated-recovery-template.service.ts:307`). An outer lifetime policy-unavailable result becomes ordinary `CHECKOUT_UNAVAILABLE` (335–337), while the fallback's own lifetime-unavailable result becomes `RETRY`. Required-state error semantics are therefore not uniform even within the neutral branch.

### Billing, hard-limit reservation and provider send

After successful preparation, initiation obtains recovery-credit admission (267), resolves the conversation, rechecks consent, revalidates credit, and validates any offer-source token. It then calls `sendTemplate` with the existing attempt key and actual returned credit source key (350).

`outbound-whatsapp-admission.service.ts:110` always calls `reserve` first. Existing UsageEvent means `duplicate`, returned before delivery; a `PENDING` message without a provider permit is not currently resumed. New reservation creates message and hard-limit UsageEvent in one Serializable transaction. Delivery then validates execution, registration, exact prepared content, moderation and current final consent/ownership/template conditions; the final SQL fence commits the dispatch permit; HTTP occurs after commit.

The provider call **and local `markSent` transaction are in the same `try`** (`outbound-message-delivery.service.ts:278`). A local receipt-persistence exception after successful provider HTTP can leave `PENDING` plus durable permit. The generic failure handler retains that ambiguous message and hard-limit usage. Billing marks the source `AMBIGUOUS`. Shopify initiation nevertheless unconditionally marks the attempt `FAILED` after non-131026 errors (360–369). This status does not prove that the provider rejected the message and must not override the permit.

### Confirmed message to complete bookkeeping

Initiation looks up the canonical durable message only after a successful send result, or after duplicate reservation (372–415). For a confirmed message it delegates to `RecoveryOutreachFinalizationService`:

1. Commit the actual recovery-credit reservation.
2. Atomically finalize attempt and optional Support notice in `RecoveryInitialOutreachSupportNoticeService`.
3. Update recovery from `DETECTED` to `MESSAGE_SENT` with actual message `sentAt`.
4. Read current persisted attempt/recovery state and publish eligible follow-up.

These are intentionally separate boundaries; a single transaction across provider HTTP is neither present nor appropriate. Convergence requires replay from each durable intermediate state.

## 3. Failure and retry state matrix

“Current owner” identifies who currently receives a retry, not a guarantee that it makes progress. `A` denotes the same sequence-one attempt, `M` its canonical message, `U` hard-limit usage, and `R` the exact recovery-credit reservation.

| Failure or stopped boundary | Durable evidence after interruption | Current retry owner and behavior | Required disposition |
|---|---|---|---|
| Candidate lookup fails before recovery insert | Candidate job; no recovery/attempt | BullMQ retries current materialization and can progress | Retry the current bounded lookup; preserve original error. |
| Initial consent denied or recipient suppressed before insert | No initial recovery/credit/message | Current event is discarded/denied; suppression or new input owns any later work | No new send while denied; no synthetic technical retry. |
| Recovery inserted; customer attachment or required read throws | `DETECTED`, no A or partial customer link | BullMQ retries, then ordinary `no-op-existing` | Resume the same generation and finish required preparation, after current send guards. |
| Stored suppression discovered after insert | `DETECTED` with suppression block; wake-up/version lineage | Existing suppression deferral/wake-up owners; two specific worker retry markers | Keep these owners and exact recipient/version checks; generic progress repair must not bypass suppression. |
| A created; preparation dependency throws | A `PENDING`, no U/M | Generic retry reaches `DETECTED` no-op | Retry preparation for A; reuse saved recovery state and fresh required eligibility. |
| Outer lifetime policy read unavailable | A can exist; facade returns unavailable | Initiation returns recovery; job succeeds | Classify technical required-state unavailability as retryable, with original error/cause. |
| Optional offer/AI/MCP evidence unavailable before permit | A `PENDING`; no permit | New fallback can prepare approved neutral message | Continue through existing neutral template path; no need to force a promotion. |
| Neutral binding/items/template unavailable | A `PENDING`; possible configuration history entry | Returns unavailable; no general reactivation owner shown | Remain blocked for the actual reason. Distinguish a durable business/configuration block from a technical failure; define explicit same-attempt reentry after remedy. |
| Capacity admission exhausted | `DETECTED` plus capacity block, A `CAPACITY_BLOCKED`; no M | Capacity resume worker scans `RECOVERY_CAPACITY_EXHAUSTED` | Existing capacity owner retries under its gates; generic replay must not invent capacity. |
| Other billing admission denial | A exists, possibly no recovery-level block marker | Usually return success; capacity scanner does not cover all reasons | Honor the real denial; retain an explicit disposition, not false “sent” or new attempt. |
| Credit reserved; conversation/consent/token step fails before M | R `RESERVED`, or `RELEASED` if cleanup succeeds | Some paths release then throw; others rethrow revalidation failure; materializer no-ops | Resume exact reservation or its sanctioned reactivation only; failed cleanup remains visible. No provider permit exists. |
| Hard-limit reservation transaction rolls back | No U/M from that transaction, R may remain | Thrown sender error may be treated as ambiguous billing/provider failure and A `FAILED` | Separate known pre-permit persistence failure from post-permit uncertainty. Do not terminalize A merely because sender orchestration threw. |
| Reservation commits; process stops before preparation/permit | U→M, M `PENDING`, both permit fields null | `sendTemplate` sees U and returns duplicate; initiation throws “still pending”; materializer no-ops | Resume the **same M and U** through existing prepared delivery after current checks. No second message or hard-limit quantity. |
| Exact content/moderation/final guard fails before permit | M `FAILED`; U may be deleted by `failPrepared`; no permit | Shopify commonly releases/marks A failed; no ordinary retry progress | Prove pre-permit state before cleanup. Business refusal remains blocked; technical pre-permit failures may resume only under a defined same-attempt transition. |
| `failPrepared` message write commits; usage deletion fails | M `FAILED`, U remains, possibly R reserved | Exception propagates; duplicate later sees failed M | Finish the known pre-permit cleanup, without provider work. Message FAILED alone does not prove credit compensation. |
| Final permit commits; process stops before HTTP | M `PENDING` plus permit; U retained | Indistinguishable from uncertain provider send | Hold provider outcome; no automatic second HTTP and no credit release based only on timeout/age. |
| HTTP times out or reply is lost | M `PENDING` plus permit; R may be `AMBIGUOUS`; Shopify A may be `FAILED` | Job throws; generic candidate retry then no-ops | Preserve uncertainty; reconcile only using provider evidence correlated to the exact message. Attempt FAILED must not authorize a retry. |
| HTTP succeeds; `markSent` transaction fails | Same durable state as preceding row, often no provider ID stored | Same ambiguity; local DB error passes through provider-failure path | Preserve original DB error and permit. Webhook cannot automatically repair a missing provider-ID link. No resend. |
| Definitive provider rejection | M `FAILED` plus permit; generic Shopify handler removes U; R release and A failure are separate | Worker generic no-op; direct replay may lack canonical message linkage | Keep failed-provider disposition and finish exact compensation. Preserve immutable attempt→failed-message lineage before removing the sole U link. Do not infer “never attempted” from a null canonical result. |
| Synchronous 131026 rejection | Linked failed message with code131026; evidence/compensation owner records exact lineage | Synchronous-recipient handler and delivery compensation; historical lookup recognizes it | Reuse its terminal failure/idempotency and recipient-suppression owners. No second attempt or duplicate compensation. |
| M confirmed; credit commit not done | U→M `SENT`/`DELIVERED`/`READ`, actual sentAt, R pending or committed uncertain | Generic retry no-op; direct retry repeats preparation/current admission first | Skip preparation and HTTP. Resolve original credit source and replay settlement, subject to existing source/period constraints. |
| Credit commit succeeds; Support transaction fails/rolls back | R `COMMITTED`; A still initial-pending, no notice from failed tx | Direct-service mocked tests can replay; real worker no-ops | Replay exact committed credit without another debit, then atomic Support/attempt transition. |
| Support/attempt transaction commits; recovery update fails | A `WAITING_FOR_RESPONSE` with M/sentAt/due; optional notice exists; recovery `DETECTED` | Worker no-op; real neutral fallback returns INVALID_ATTEMPT before message lookup | Bypass fallback; verify same receipt, replay Support idempotently, finish recovery update without downgrading a terminal/engaged state. |
| Recovery update commits; follow-up enqueue fails | Recovery `MESSAGE_SENT`, A persisted due date; no proven queue publication | Direct initiation can repair scheduling; candidate materializer returns no-op | Route actual retry to existing `ensureScheduledInitialFollowUp` and same deterministic job identity. |
| Job finishes but future queue job is lost | SQL says sent and due; no queue job | No general SQL-driven follow-up repair scan found in inspected call sites | Do not claim eventual self-healing. Reuse existing reconciliation entry for an explicit repair; broader recurring scanner is separate scope. |
| New STOP/order/expiry after confirmed provider send | Confirmed M; current new-send policy denies | Shopify early guards may prevent bookkeeping; Woo reconciles before gate/order checks | Finalize the existing receipt and exact credit without sending; preserve current recovery terminal state. New-send authorization remains denied. |
| Conflicting/missing message, tenant, attempt or reservation lineage | E.g. U points to missing M; linked M differs; multiple paid sources | Current paths variously throw or return unavailable | Visible reconciliation conflict, never “no prior send.” Do not repair by selecting an arbitrary current row. |
| Technical retries exhausted | Failed BullMQ job retained if still failed; partial SQL survives | No automatic generic SQL progress scanner established | Retained failed-job operational replay may call the same progress owner. Do not claim bounded retries guarantee eventual completion. |

This matrix deliberately separates an unsent message with no permit, a known pre-permit refusal, a definitive provider failure, a provider-admitted unknown outcome, a confirmed receipt, and partially finalized bookkeeping. A boolean “has message” or the `DETECTED`/`FAILED` enum cannot represent these distinctions.

## 4. U2: precise defect and canonical lookup boundaries

`recovery-template-integration/initial-no-offer-fallback.service.ts:144` queries `ConversationMessage.providerDispatchKey = 'recovery-outreach:' + attempt.id`. Neither current Shopify nor Woo writes that key. The linked-message branch at 145 is unreachable because the attempt guard at 138 already rejects a non-null `outboundMessageId`.

The test named “reconciles an existing durable provider dispatch” (`tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts:115`) mocks this wrong lookup and asserts `RETRY`. It neither uses a real dispatch key nor performs reconciliation. The new integration test asserts a real `arch040-auto-` key on the happy path but does not interrupt and replay the lifecycle (`tests/integration/arch052-shopify-initial-no-offer-dispatch.integration.test.ts:139`).

The correct existing lookup is `OutboundWhatsAppAdmissionService.findExistingAdmission`, backed by `OutboundAdmissionReservationService.findExistingAdmission` (53). It makes one UsageEvent lookup followed by one message lookup, or a failed-recipient historical lookup if usage is absent. Its current message projection lacks provider permit fields, direction, sender and owning recovery; its usage projection lacks shop/metric/source type. **Narrowly extend this existing projection and validate those identities**, rather than adding a new lookup service at every layer.

Three limitations must be handled explicitly:

- A `PENDING` result needs both permit fields to distinguish safely resumable preparation from unknown provider outcome. Extending the selected columns does not add a source-level read.
- A null result with a persisted usage source ID, an existing attempt message link, or a finalized attempt is an integrity conflict. The current fallback recognizes only linked `FAILED`/131026 messages after usage deletion (`outbound-whatsapp-admission/failed-outreach-admission.ts`). It is not a general “no prior provider operation” proof.
- Generic Shopify definitive failures can remove the usage link without persisting attempt→message. Reuse the existing attempt outbound link and failure-evidence/compensation owner pattern to retain terminal failed-message identity before deleting hard-limit usage. Do not expose a new retry branch that interprets this historical information loss as an unsent attempt. Data that has already lost all immutable linkage must remain a visible conflict; no speculative search by content or latest message is acceptable.

The replay decision belongs before new template and billing preparation in initiation. The fallback remains responsible for approved neutral content and required input validation. Pass a narrow validated progress/snapshot context through that call, or delegate to the same canonical decision once; do not repeat recovery→attempt→usage→message resolution in the worker, initiation, facade and fallback. A snapshot is an optimization of preparation, not authority to skip the fresh final SQL provider fence.

## 5. Woo: useful existing design, bounded applicability

`woocommerce-recovery/woo-recovery-outreach.service.ts` supplies an existing pattern:

- `enqueueInitial` (269) and `processInitial` (331) look up sequence one and its canonical persisted message **before** the outbound gate at 306/376.
- Confirmed but incompletely finalized sends are queued/finalized even if new outbound is disabled or an order arrived later. A sent attempt with recovery still `DETECTED` is explicitly repaired.
- Still-pending attempts are republished under the same attempt identity when a queue publication failed or an old job disappeared (319).
- `compensateProviderError` (580) first checks whether persistence already says confirmed and never refunds that send. It marks an attempt failed only when the message is durably failed. This is the important contrast with Shopify's unconditional failed status.
- `woo-resumed-outreach-settlement.adapter.ts:113` already distinguishes permit-recorded unknown, confirmed, definitive failure and pre-permit cancellation, validates tenant/recovery/attempt/message lineage and releases the specific reservation owner. Reuse its invariants, not an unrelated new framework.

Do not copy Woo's limitations: it treats every `PENDING` message as uncertain because its projection lacks permit fields; ordinary failed-compensation replay throws an unresolved marker rather than completing all compensation; `finalizeExisting` (548) calls current `billing.admit`, which is not proof of original source ownership across policy or period changes. A confirmed message with FAILED/CANCELLED attempt currently throws, so correcting Shopify's ambiguous-error terminalization also requires a carefully guarded legacy reconciliation path rather than blindly resetting every failed attempt.

The source remains production-disabled for new Woo initial outbound: `enabled()` requires `NODE_ENV === 'test'` and explicit injected `enableTestOutbound()` true (499). Composition supplies no callback. Removing an offer-token requirement only lets approved neutral content use an enabled test sender; it does not activate production delivery. Existing receipt reconciliation remains before that gate and must stay there.

## 6. Database work: necessary versus redundant

These are source-level database operation sites in bounded branches, not measured SQL round trips. Relation expansion, trigger work, BEGIN/COMMIT, helper internals and retry multiplication are excluded unless explicitly stated.

| Bounded path | Current source-level calls | Assessment |
|---|---:|---|
| Fallback rejects invalid recovery/attempt | 2 reads in parallel | Necessary identity/state data; should reuse the caller's verified projection where freshness permits. |
| Fallback valid attempt, wrong dispatch probe hits mocked row | 3 reads total | Third read uses wrong namespace; linked-message read is unreachable. Remove/replace at the single progress owner. |
| Fallback through saved-items/lifetime check before delegated template preparer | 4 reads total | Recovery + attempt + wrong dispatch probe + lifetime. Sender/template helpers are additional. |
| Initial NONE facade through those fallback checks | 6 reads total | Adds outer recovery and lifetime. Same short branch can reuse both; after a long external selection phase, freshness may require a reread. |
| Template unapproved history branch | Above + 1 write | Required evidence by current design, but repeat invocations may repeat history; not a recovery-progress marker. |
| Canonical admission lookup with intact usage | 2 reads | Usage key→message identity is necessary. Add permit and ownership columns to these reads, not another message read. |
| Canonical absence for a recovery-attempt key | Usually 2 reads | Usage miss then linked-attempt historical check. Missing usage and missing lineage are not universally equivalent to unsent. |
| Duplicate reservation in `reserve` | 1 read inside Serializable transaction | Early duplicate check is useful, but must return enough verified existing state for a controlled same-message resume; cannot always be terminal duplicate. |
| Fresh hard-limit reservation | 6 direct operations, plus optional groupBy, plus policy helper work | Existing-usage read, historical-attempt read, conversation read, automated-message list, message create, usage create. Atomic message+usage insertion and uniqueness are necessary. |
| Prepared message before external send | Message reads/CAS, moderation reads/writes, final SQL fence | Keep final freshness and content/registration/consent checks. Do not remove them merely because initiation already checked. Repeated snapshot discovery can be consolidated, final authority cannot. |
| Local `markSent` | 3 operations in one transaction | Update message receipt; reread its conversation ID; update conversation timestamp. Since delivery already has verified conversation ID, that reread is a possible local optimization, not the U2/C3 correctness fix. |
| Support finalizer successful enabled first transition | 9 operations in one transaction | Attempt row lock; attempt/lineage read; message read; guarded attempt update; setting read; thread create; thread read; notice create; thread timestamp update. Atomicity is required. |
| Support disabled first transition | 5 operations in one transaction | Same until setting read. Persists attempt completion without notice; later opt-in must not backfill. |
| Support finalizer replay | 3 operations in one transaction | Lock, attempt/lineage read, message read. Returns replayed only for exact message/sentAt/due values. Do not replace with an unlocked existence probe. |
| After Support finalization | Recovery update if DETECTED + recovery/attempt read | Needed separate convergence steps. The final read determines follow-up eligibility; queue publication is not SQL. |

A read-count reduction is not the primary success criterion. Reconciliation should avoid policy/offer/MCP/template work for a confirmed receipt, and should not recreate a message or reservation for a known existing send. Preserve the final locked checks even if they cost additional queries.

### Minimum persisted decisions by replay state

This is a decision budget, not an invented universal query total. Tenant/recovery/attempt resolution and the single canonical usage/message lookup can share their selected context. An authoritative mutation must still recheck its own predicates under the existing lock/transaction.

| Classified state | Minimum further database decision | Work that should not run |
|---|---|---|
| No attempt or message, same incomplete recovery | Validate current send eligibility; upsert the existing sequence identity; reserve credit only after valid preparation | New generation creation merely to escape a stuck attempt |
| U→PENDING M, both permit fields null | Verify usage ownership/source kind and current reservation/guards; compare-and-set content; existing final permit CAS | Second message insert, second hard-limit usage, unrelated credit source |
| Permit recorded, no confirmed/definitive receipt | Retain exact ownership and unresolved status; evidence-based reconciliation only | Template/offer recomputation, new permit, automatic release or provider HTTP |
| Definitive failed M | Read exact compensation/lineage state; finish only the corresponding release/correction and terminal evidence | New send or a second debit/refund |
| Confirmed M, exact R already COMMITTED | Verify same committed source/outcome; atomic attempt/Support replay; missing recovery update; follow-up eligibility read | Current billing admission or current template selection |
| Confirmed M, exact R RESERVED | Attempt source-owned commit only under its existing contract, and verify successful committed outcome | Substitution with a new period/current-source reserve |
| Confirmed M, R AMBIGUOUS/RELEASED or nonunique | Explicit billing reconciliation/conflict; do not advance completion on a no-op return | Treating a resolved commit Promise as proof of charge |
| Attempt/Support already finalized, recovery stale | Verify exact M/sentAt/persisted due; conditional recovery update; existing follow-up eligibility read | Recreating notice, re-deciding a finalized null due date, sender preparation |
| Recovery sent, queue publication failed | Existing `ensureScheduledInitialFollowUp` read and deterministic queue add | All initial admission/delivery work |

Finite ownership remains explicit: the existing candidate queue owns up to three executions; suppression/capacity retain their dedicated wake-up owners; unknown provider results require evidence; failed jobs can be operationally replayed through the same owner after exhaustion. There is no demonstrated generic periodic sweep that guarantees indefinite completion.

## 7. Smallest coherent correction specification

### A. One reachable progress decision

Extend the existing materialization/initiation flow so ordinary retry of an existing generation enters a **persisted initial-outreach decision**, instead of returning solely because recovery is `DETECTED`. Reuse the latest recovery already read and the unique sequence-one attempt. Route `MESSAGE_SENT`/`ENGAGED` retry to existing scheduling reconciliation where needed. A known confirmed receipt must be allowed to settle before new-send execution/order/consent gates; tenant, platform and receipt ownership remain mandatory.

This should be a narrow evolution of `RecoveryInitiationService` and its materialization port, not a new generic orchestration service. The method's result must distinguish completed, business-blocked, technical-retry, provider-uncertain and lineage-conflict. Mapping a technical required-state outage to “unavailable, return recovery” is not completion. Existing capacity and suppression resume owners remain the owners of their specific blocks.

### B. Existing canonical read and controlled same-message continuation

Extend canonical usage/message projection with permit and ownership fields. Classify the same persisted state once. Use existing message ID, hard-limit UsageEvent and source type when a message is provably unadmitted. `sendTemplate` currently cannot do this because it returns duplicate before delivery; add a narrow existing-reservation continuation inside its current reservation/delivery owner, or expose its existing prepared-template delivery through a verified resume operation. A caller must not fabricate `AdmittedOutbound` from an arbitrary message ID.

Resume must validate tenant, recovery, sequence, recipient, usage metric/source kind and any attempt link, derive terminal/general/recovery semantics from persisted usage plus current policy, and use the existing content CAS/final SQL permit. Concurrent replay must permit at most one HTTP. Fresh preparation may be repeated only before the permit and only under the current approved-template/offer/consent rules. After a permit, neither new content nor a second message is an authorized retry.

Same-message continuation also requires the existing MSG-03 cleanup contract to be closed. `outbound-provider-failure.service.ts:14` currently writes FAILED unconditionally and then deletes hard-limit usage in a separate operation. A resumed/concurrent caller must not use this cleanup to overwrite a message another caller has admitted or confirmed, or erase its durable accounting/identity. Pre-permit cleanup must conditionally claim a still-PENDING message with both permit fields null and couple usage removal to that successful claim; a zero-row claim must reclassify the persisted state. Definitive post-permit provider failure remains a separate evidence-based disposition. This is a required invariant for the proposed correction and an existing MSG-03 coupling, not a claim that this investigation executed or proved a production race.

### C. Preserve failure evidence and separate local errors from provider outcomes

Keep the original error/cause, but classify by the persisted send boundary. An exception before any permit may be retryable preparation failure; a permit with unknown receipt stays uncertain; a definitive provider rejection uses exact compensation; a confirmed receipt cannot be refunded because later persistence/logging failed. Adopt the existing Woo confirmed-first error discipline and guarded attempt updates.

Do not use unconditional `markStatus(FAILED)` for all sender exceptions. Do not reset a previously failed attempt solely because it has no outbound link. Legacy attempts that were incorrectly marked FAILED while the message is confirmed need a narrowly evidenced reconciliation transition, preserving audit information and never overriding genuine definitive failures, cancellations, another message link, or later engagement.

Preserve immutable failed-message linkage when deleting hard-limit usage. The existing 131026 path is an example of using current fields and the failure/compensation owner, not a reason to broaden 131026-specific policy to all errors.

### D. Confirmed finalization replays actual decisions

Reuse `RecoveryOutreachFinalizationService` and `RecoveryInitialOutreachSupportNoticeService`. Retain atomic attempt-plus-notice and their exact-identity replay checks; independently retry recovery status and follow-up publication. Finalization must not require a new offer/template or current consent to account for a send that already happened.

For an already-finalized attempt, preserve stored `followUpDueAt`, **including null**. Current `attempt.followUpDueAt ?? deriveFromCurrentPolicy` can turn a previously persisted null into a date after policy changes, conflicting with Support replay's exact due-date equality. Distinguish “not yet finalized” from “finalized with no follow-up”; do not use nullish coalescing as that distinction. Before the first attempt transition, the existing policy decision still needs an explicit contract; the current attempt stores offer configuration but no dedicated initial follow-up-policy snapshot. Do not invent proof of a previous null decision when it was never persisted.

### E. Exact original credit or visible conflict

Reuse existing exact-source lineage logic in `recovery-delivery-compensation/lineage.ts:23` for the evidence model, with billing retaining ownership of successful settlement. That helper derives the logical source from immutable usage/attempt/message data; searches base and paid-prefixed candidates with a bound of two; requires exactly one; and validates source ownership. It is not permission to invoke failure compensation for a success.

`recoveryCreditSourceKey` passed to the sender is not stored as a dedicated message/attempt reservation FK. The hard-limit UsageEvent's billingPeriodId identifies its policy period, not the selected credit kind or immutable recovery reservation. When multiple historical/base/current reservations match, the snapshot does not establish a unique correct debit through that helper. Keep this conflict visible; do not choose newest, current, or first non-released source.

For an exact **already-COMMITTED** reservation, existing idempotent commit can replay. For an exact still-RESERVED paid reservation, `paid-included-recovery-reservation.service.ts:279` checks the current open period, current subscription linkage and present time before a new commit. A rollover can therefore prevent settlement even with a confirmed old receipt.

AMBIGUOUS is a different boundary: `recovery-reservation/reservation-lifecycle.ts:80` permits a commit mutation only from RESERVED; AMBIGUOUS or RELEASED instead returns an unchanged replay outcome. `RecoveryReservationLifecycleService.commit` currently discards the underlying outcome. Therefore a resolved `commitSuccessfulInitiation` call alone is not proof that a source became COMMITTED. Confirmed replay must positively establish a successful/previously committed settlement before claiming completion; ambiguous sources need a defined, evidence-based transition through their current owner. This nuance also applies beyond paid credits.

These are billing policy/lineage boundaries, not solved by better queue replay. Fresh `billing.admit` can select a new period or credit source and must not be used as the shortcut. No schema migration or historical source migration is proposed without separately establishing the missing evidence and the approved settlement rule.

## 8. Deterministic validation specification

Extend the existing tests with controlled fault injection and durable-state assertions. Use an isolated SQL/Redis test fixture where SQL atomicity/concurrency matters and fake provider responses throughout. Do not use live merchant/providers for verification.

| Case | Existing test home to extend | Required evidence |
|---|---|---|
| Generic first-send required read fails after recovery insert | `tests/unit/workers/pending-recovery-candidate.worker.test.ts`; `tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts` | Invoke the actual worker twice; same generation/attempt resumes. Include non-suppression error, not only the existing two marker cases. |
| Real neutral fallback receives a valid existing permit | `tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts`; integration `arch052-shopify-initial-no-offer-dispatch.integration.test.ts` | Persist real Shopify and Woo keys plus UsageEvent link; no mocked wrong namespace. Required classification and zero template/provider work after permit. |
| Initial NONE lifetime/config outage | Template integration tests + actual worker case | Technical read failure throws/preserves original error and retry resumes A; configuration/business denial stays blocked without false send. |
| Unadmitted message resumption | Outbound admission/delivery tests; actual worker integration | U→M PENDING with both permit fields null; replay uses same M/U, one total provider call and no second usage quantity. Two concurrent replayers still one permit/call. |
| Cleanup overlaps a winning resume/final permit | Outbound delivery/failure tests with deterministic barriers | Cleanup CAS loses after permit/confirmation, preserves M and U, and reclassifies without overwriting SENT or removing admitted usage. Pre-permit cleanup success removes only its own usage transactionally. |
| Crash immediately after permit before HTTP | Same integration fixture | PENDING permit must never automatically resend, even if test knows HTTP was never reached. Shows the protocol's observable limit. |
| Provider timeout / provider success plus markSent DB failure | `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`; outbound delivery tests | Hold permit and R, do not label known failed solely from exception. Original local/provider error retained. No second provider call. |
| Persisted confirmed message plus thrown sender exception | Initiation tests, analogous Woo test at 357 | No refund, no new credit admission, no failed attempt overwrite; converge via finalizer. |
| Failure compensation crashes after message failure before credit/usage work | Delivery compensation and initiation integration tests | Immutable failed-message lineage survives; replay finishes same source cleanup once and never reclassifies as unsent. Preserve 131026 semantics separately. |
| Billing commit fails once after send | Initial no-offer integration + finalization tests | Exact same confirmed M and original R; next worker replay commits once and sends zero further HTTP. |
| Support insertion fails once | `tests/integration/recovery-initial-outreach-support-notice.integration.test.ts:255`, plus real worker replay | Existing transaction rollback assertions plus actual queue reentry. Exactly one eventual notice and one credit. |
| Recovery status write fails after Support transaction | `tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts`; no-offer integration | A remains linked WAITING, notice exists, recovery DETECTED; retry reaches finalization without real fallback rejecting A; one notice, no new send. |
| Follow-up queue add fails after MESSAGE_SENT | Initiation/finalization tests + worker | Replay reaches `ensureScheduledInitialFollowUp`; persisted due unchanged; same deterministic job ID; no initial resend. |
| Follow-up setting changes between finalization/replay | Finalization notice tests | Persisted null remains null; persisted date remains that date; no Support conflict or silent new follow-up decision. |
| STOP, paid order, shop pause after confirmation | Shopify integration; analogous Woo test at 291 | Existing receipt bookkeeping completes with no new send; terminal recovery status not downgraded. An unsent counterpart remains denied. |
| Paid source historical/current ambiguity | Billing/compensation lineage tests | Multiple candidates yield visible conflict, no new reservation/debit. Distinguish exact COMMITTED replay from historical RESERVED/AMBIGUOUS policy failure. |
| Commit returns already-ambiguous/already-released | Reservation lifecycle and initial finalization tests | No false completed settlement, no Support/recovery completion claimed merely because the Promise resolved; exact source remains visible for reconciliation. |
| Missing/cross-tenant message/usage/attempt | Admission/finalizer integration | Never convert broken linkage into unsent, bypass tenant checks, or finalize another recovery. |
| Woo disabled runtime and reconciliation | `tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts` | New outbound remains disabled outside explicit test; confirmed partial finalization still executes before gate. |
| Exhausted retries | Worker test with three technical failures | Job remains failed/inspectable; no false success after DETECTED, no claimed automatic periodic repair. |

The existing initiation test at 558 mocks preparation and sender duplicate behavior, directly invokes the service twice, and does not run through the ordinary materializer. It demonstrates a helper replay path, not full worker convergence. The current provider-error test at 524 explicitly expects unconditional attempt FAILED for a generic Error; that expectation must change if the design is implemented. Existing Support transaction tests remain useful and should be preserved rather than replaced with mocks of their atomic behavior.

## Outcome of this investigation

U2 is confirmed as a wrong-identity lookup. C3 remains open after the updated fallback because normal worker replay and several partial-finalization states are still unreachable. The correction boundary is now explicit: one durable progress decision in existing initiation/materialization, canonical message lookup with permit/ownership fields, same-message pre-permit continuation, receipt-first error handling, replayable existing finalizers, and exact-source billing conflict handling. Changes to any one of these in isolation must not be described as complete recovery retry convergence.
