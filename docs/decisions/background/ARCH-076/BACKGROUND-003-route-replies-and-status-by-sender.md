---
id: ARCH-076-BACKGROUND-003
architecture_id: ARCH-076
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
depends_on: [ARCH-076-BACKGROUND-002]
enables: [ARCH-076-BACKGROUND-004]
created: 2026-11-13
updated: 2026-11-13
---

# Route inbound messages, STOP and delivery status using the actual Moda sender

## Architecture

[ARCH-076 architecture](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md). Coordinator: `moda_architect`.

## Objective

Implement in the Background worker. For fresh unquoted replies, establish the customer’s shop from the actual receiving number. Pass every eligible same-shop basket to BACKGROUND-004 when basket attribution needs interpretation. Directly deliver an unambiguous singleton or proven checkout quote. After reuse, explicit message references, replays and delivery statuses retain their original ownership. An expired checkout confers no active processing rights and occupies no slot.

## Context

Preserved from original local commit `59705bb589342f31054e6c1fd011dacf9d495ae6` under root-authorized ARCH-076 collision correction. Defined portable design only; Pending/unclaimed until current-main compatibility review and explicit architect promotion. No runtime implementation or launch is authorized by preservation.

The snapshot accepts a single configured sender and searches for up to two conversations by recipient phone. BACKGROUND-002 adds durable shop routes, per-recovery memberships and explicit sender selection before transport. This worker must read that evidence to distinguish shops sharing a customer phone.

## Scope

Paths in this section are relative to `moda-interact-background/`. Modify the following existing services at their stated entry points. Extract the new pooled route read/validation to `src/services/recovery-sender-route.ts` to keep the live router small. Reuse the sender resolver and assignment lifecycle from BACKGROUND-001/002 and the existing shop, phone, conversation, consent, admission, control and historical handling.

| Path in repository | Required edit |
| --- | --- |
| `src/services/recovery-routing.service.ts` | Change `RecoveryRoutingService.resolveInboundMessage` and `isCurrentActiveRoute`. This is the router used by `whatsapp-inbound-processing.service.ts`. Do not implement the feature only in the similarly named `whatsapp-conversation-routing.service.ts`. |
| `src/services/whatsapp-inbound-processing.service.ts`, `src/services/conversation.service.ts`, `src/services/inbound-whatsapp-audio.service.ts` | Carry the verified owner and evidence into text/unsupported receive, audio reservation/completion, active rechecks and historical persistence. Expose a shop-route branch before checkout persistence, audio reservation or engagement for BACKGROUND-004. Remove the ungated standalone active-activity write from pooled handling. Preserve unpooled callers. |
| `src/services/recovery-recipient-ownership.ts`, `src/services/whatsapp-contact-opt-out/{phone,quoted-outbound}.ts`, `src/services/whatsapp-contact-opt-out.service.ts` | Reuse canonicalization/recipient checks. Verify the receiving sender and original recipient on a quoted checkout or a confirmed shop-specific clarifying prompt. Reuse the existing registered-merchant writer and idempotent notice publisher. |
| `src/services/routing-guidance.service.ts` | Authorise the incoming pair and send approved neutral guidance on that same number through the explicit identity in BACKGROUND-002. Preserve the Redis clarification key and expiry, recipient STOP fence and ten-second provider budget. |
| `src/services/whatsapp-provider-status.service.ts` | Protect the serializable lifecycle transaction and post-commit money/reachability/support paths with original outbound sender ownership. Keep duplicate status repair. |
| `src/workers/whatsapp.worker.ts`, `src/services/conversation-turn-processor.service.ts` | Gate a delayed pooled recovery turn on its still-open, eligible owner before loading basket context/invoking the agent. Consume a closed/superseded turn through the existing inactive/suppressed completion path. Preserve verified independent standalone behaviour. |

Read-only evidence includes Shared `src/whatsapp.ts` v1 and `src/billing.ts` statuses v2/v3, Messaging `app/lib/whatsapp/{inbound-message-normalizer,provider-status-normalizer,normalization-utils}.ts`, and `whatsapp-job-publisher.server.ts`. Inbound `occurredAt` is the verified provider occurrence time. Numeric webhook timestamps are Unix seconds normalized to ISO. Background `outbound-message-delivery.service.ts::markSent` sets `ConversationMessage.sentAt` at provider receipt persistence. Neither enqueue time nor the time an operator replays a job proves which checkout an inbound belongs to.

## Out of Scope

Sender allocation, sender administration, schema/migration, public API, Shared publication, Messaging ingress, credential/queue changes and runtime Meta HTTP discovery.

## Requirements

1. Canonicalize `event.customerPhone` using `canonicalWhatsAppSender`. Resolve the received `providerPhoneNumberId` under the event's `providerAccountId` in this environment. A matching inventory row is pooled even when `allocationEnabled=false`. Disabling allocation has no effect on validation of outstanding/historical messages or STOP. If the ID is enrolled for a different account, reject even when encrypted singleton credentials appear to match. Unknown account/number grants no merchant route, STOP write, status effect or guidance send.
2. Only a non-enrolled phone matching the configured dedicated singleton WABA/phone can use the former unquoted candidate lookup. Restrict its candidates to conversations without a `RecoverySenderAssignment` and require a genuinely confirmed original outbound to the same recipient with the exact stored non-pooled evidence below. Apply the existing exactly-one-candidate rule *after* this filter and enforce effective expiry/generation before any active effect. Unknown or ambiguous legacy context receives neutral handling. For enrolled phone IDs fresh unquoted lookup uses the open shop route and its confirmed members. Enrolling a formerly dedicated number cannot invalidate an explicitly referenced and proven pre-pool message, but it never enables a recipient-only fallback.
   - **Original outbound sender evidence.** Reuse BACKGROUND-002's non-pooled permit fields `ConversationMessage.dispatchProviderAccountId` and `dispatchProviderPhoneNumberId`. A complete pair must match the received WABA/phone. For pooled recovery messages without a non-pooled pin, take the immutable conversation assignment, its original shop route and joined inventory. If competing evidence disagrees or either half of a stored pair is missing, reject. If no assignment and no dispatch pair exist, allow *only* independently persisted, original-message evidence. In this snapshot load the existing `billing.UsageEvent` by `deliveredUsageKey(message.id)` (`whatsapp-delivered:<internal-message-id>`). Require the same owning shop, `DELIVERED_WHATSAPP_MESSAGE` metric, `WHATSAPP_PROVIDER_STATUS` source type, exact internal message ID in `sourceId` and valid previously saved `providerResponseSummary` JSON carrying `DELIVERED` or `READ` and both exact provider IDs. This read must precede all processing of the incoming event. Missing or truncated JSON, scope mismatch and absent proof are unresolved. A matching current credential or today's callback cannot establish yesterday's sender. If a previously unknown provider result for an expired checkout is later reconciled, it can update only its original message and recovery lineage. It cannot reopen the released assignment, change the next checkout's sequence-one receipt/time threshold or overwrite ownership of an inbound message already recorded for that next checkout. Existing provider and DB read errors retain their original diagnostics/queue retry.
   - **Stored inbound replay.** For pooled messages, the original conversation assignment and route supply an immutable sender, shop and recipient. For an unassigned recovery conversation, use its stored inbound owner plus its original quoted outbound if present, otherwise its sequence-one proven original outbound/recipient. If the owner, pre-pool sender or addressing cannot be established exactly, skip merchant effects. Never infer legacy routing from an operator flag or query multiple shops for an exact message. General sends carrying a new non-pooled pin can receive their first verified status without any older delivered usage row.
3. Process recognised inbound messages in the order below. Preserve raw abuse admission ahead of normal routing. Body text can resolve a basket only within an already authenticated shop route through BACKGROUND-004. Treat customer-supplied shop names, checkout IDs and guessed references as untrusted input.

| Priority | Input | Exact action |
| --- | --- | --- |
| 1 | Explicit typed STOP/UNSUBSCRIBE | Preserve `isExplicitWhatsAppStop`. A verified checkout outbound or confirmed shop-specific clarifying prompt can establish consent scope. Verify original recipient, shop, receiving WABA and number using the original immutable lineage. Released membership/closed route remains valid proof of the original merchant. A verified quote applies to that merchant only. A standalone STOP or missing, invalid, cross-scope or generic-guidance quote on a recognised sender applies `ALL_REGISTERED_SHOPS`. Propagate database read exceptions. A stop on an unknown sender has no effect. |
| 2 | Previously stored inbound provider ID | Read both `ConversationMessage.providerMessageId` and `RecoveryBasketRoutingTurn.inboundProviderMessageId`. Require matching canonical recipient, actual WABA/number, route generation and direction where applicable. Replay only the original merchant or pending route turn, including a resolved turn and its matching checked-out conversation projection. Reject conflicting owners, wrong directions or changed sender and preserve original stored inputs. An exact duplicate may repair incomplete effects idempotently. |
| 3a | Quote of a checkout message | Look up the exact confirmed OUTBOUND provider ID and non-null sentAt. Verify original sender, recipient, shop, conversation/recovery, outreach or command recipient where present and existing eligibility, including `resolveRecoveryRecipient`. An active verified quote identifies that member. A closed one uses only the existing historical path. In a current route with a pending question, forward a verified original-basket reference as exact evidence for BACKGROUND-004 to distinguish an explicit answer from an unrelated quoted message. Never join unrelated questions merely because the same basket was quoted. |
| 3b | Quote of a clarifying prompt | Look up exact unique `RecoveryBasketRoutingTurn.promptProviderMessageId`, require confirmed sent receipt, original WABA/number/recipient and matching route generation. A current prompt goes to BACKGROUND-004 with its exact original turn, even if only one basket now remains. A stale or closed-route quote is ineligible for active checkout work. A quote missing proof, cross-scope, or colliding across outbound types returns `INVALID_REFERENCE` without a fresh unquoted fallback. |
| 4 | Fresh unquoted inbound | Read the one open `RecoverySenderRoute` via its partial unique `(canonicalRecipient, providerPhoneNumberId) WHERE closedAt IS NULL` and verify the joined inventory's WABA. Enforce current `isShopExecutionActive` and recipient ownership. Load all unreleased `RecoverySenderAssignment` members for this route; never use the legacy two-candidate query here. Compute confirmed, eligible candidates below. No current scope gives the existing neutral no-recovery/shop-unavailable outcome. |

An eligible member must join to a RECOVERY conversation, matching shop/customer lineage, current recipient, its own recovery in MESSAGE_SENT or ENGAGED status, remaining effective lifetime and latest generation of that checkout under existing integration rules. Use the inclusive `lastExternalActivityAt` cutoff and the configured non-negative whole days, including zero and above 90. Fetch the sequence-one INITIAL attempt and its confirmed outbound. The attempt belongs to that recovery, matches the route's canonical recipient and has sentAt. Its outbound belongs to that conversation and has OUTBOUND direction, providerMessageId and sentAt. Exclude pending or unknown initial sends. One merchant's separate keys can produce any number of concurrent confirmed members.

For fresh unquoted events use the verified provider timestamp (whole seconds). Require the inbound second strictly after the route opened and, for each candidate, strictly after the later of its membership assignment and its confirmed sequence-one outbound sentAt. An invalid timestamp or tie with route opening is unresolved. A member whose initial outreach happened in a later second cannot be the subject of that earlier event. A tie with a current member’s admission/first send makes the ordering indeterminate; use neutral guidance asking the customer to quote the checkout, even if an older member would otherwise qualify. For an ineligible or indeterminate timestamp on a positively verified shop route, record a minimal IGNORED routing turn under that same provider ID and scope, with no basket selection or content. Redelivery after one sibling expires cannot turn that discarded event into a singleton reply. Neutral guidance retains its existing idempotent admission. Never replace event time with processing time. Explicit verified references and stored ownership have their own proof.

Emit the Background-local `kind: 'shop-route'` branch when an eligible shop route has multiple candidates, an existing pending exchange that might receive an answer, or a verified quote requiring clarification handling. A verified original-basket quote carries the exact member as evidence. Return the verified routeId, shopId, canonical recipient, WABA and phone-number ID, inbound provider ID and event occurrence time, matching root/quote evidence when present and all eligible member identifiers with membership and confirmed-send timestamps. Treat a zero-candidate route as ineligible for new commerce work; let BACKGROUND-004 report stale choices without basket disclosure when an already-verified clarification is awaiting an answer. A singleton with no pertinent pending exchange can proceed through the direct branch. Resolve text and voice through the same contract. Unsupported messages preserve existing neutral/non-processable handling. The intermediate BACKGROUND-003 implementation must type this handoff and prevent checkout writes for unresolved inputs. BACKGROUND-004 implements and wires the final classification, customer response and resumption before the coordinated rollout.

### Mutations, delayed work and diagnostics

- Carry resolution origin (stored replay, explicit quote, fresh single member or verified shop route) with the resolved route as a Background-local discriminant. Recheck the same assignment and same conversation at the write boundary. Use a short PostgreSQL transaction with the owning lifecycle lock order from BACKGROUND-001/002; acquire conversation parent before message child. Verify active status, assignment ownership, effective expiry and generation under the lock that serialises with release. Recheck the decision inputs and candidate membership under the route lock. If a formerly unique choice has become ambiguous, return the scoped handoff, without writing a basket message. Only after a basket is uniquely resolved may the worker advance its external activity using a monotonic update and persist/process the inbound. Do not call the global Prisma/Redis-backed `checkoutRecoveryService.recordExternalActivity` inside a transaction. Do not extend lifetime on a replay or a late/ambiguous event. If release wins, a new unquoted route returns neutral/unresolved. Only a stored replay or explicit verified quote can take the historical path. Never re-resolve an in-flight event into the subsequent owner.
- Serialize the two inbound ownership stores. For all direct and route-level inbound owner writes, take the same transaction-scoped PostgreSQL advisory lock via `pg_advisory_xact_lock(hashtextextended('whatsapp-inbound-owner:' || $1, 0))` on the bound provider ID before owner locks (binary ascending provider IDs when resolving a chain). Re-read both stores. The only permitted cross-table occurrence of an inbound ID is the exact resolved route-turn projection into its selected conversation, committed atomically by BACKGROUND-004. A retry verifies both sides. Preserve unique provider-message deduplication. If an insert races another worker, recover only on the exact unique conflict, reload the winner, verify direction and owner and apply existing duplicate repair to the same conversation. No extra version bump or duplicate processable message. Preserve historical text/unsupported persistence and historical audio reservation without active engagement, refreshed recovery activity, new AI work, media download/transcription or billing.
- For new directly attributed active audio, perform the durable route check at reservation before fetching media. Recheck inside the existing completion transaction before `recordProcessableInbound` and before enqueuing or sending voice fallback. Ambiguous audio reaches the shop-route handoff before any media fetch or basket attachment. BACKGROUND-004 then owns its route-scoped handling. Only complete the original, eligible conversation. Preserve redelivery repair, control mode, stale-transcript/revision checks and the existing final-attempt policy. Provider/network calls remain outside lock transactions. After a valid active text receipt recheck the same owner before enqueuing. The delayed-turn load and existing final send permit must independently gate an intervening closure. Do not load another shop's context or contact a newly assigned shop as a fallback.
- In `WhatsAppProviderStatusService.apply`, find by `providerMessageId` and verify original OUTBOUND, original conversation/shop and its original sender evidence: immutable membership and its original route (including closed or released rows) for pooled checkout sends, dispatch pair or qualifying prior persisted per-message proof for non-pooled sends. Recheck inside the locked transaction before status changes to message, command, outreach attempt, usage, recovery or credits. Status envelopes contain no customer phone. Use the stored outbound owner, never a new owner lookup by recipient, and never sender evidence derived from the event being validated. Return a distinct internal sender-rejected outcome on mismatch/missing proof. Carry an explicit boolean qualifying the committed result for downstream repair: set true only for a verified owned outbound with a valid lifecycle event or idempotent duplicate eligible for the existing repair. Guard both existing post-commit blocks (FAILED compensation/reachability/notice and DELIVERED/READ positive reachability). Merely returning the existing `ignored` result would still invoke them. Preserve exported status behaviour for existing callers as needed by mapping this internal rejection to `ignored` after skipping all effects.
- A confirmed clarification prompt is outbound proof at shop scope only. A status for its provider ID must match its original route and WABA/number, irrespective of subsequent reuse. Bypass every checkout status, command, billing, reachability, notification and post-commit repair path. A collision between a clarification provider ID and an unrelated conversation message is a rejected mismatch. Generic guidance cannot prove a merchant.
- Keep neutral guidance free of shop, checkout, thumbnail and basket information. Unsupported types already suppress guidance. Preserve same-message deduplication, all-shop no-contact check and existing handling for uncertain guidance sends. A failure reading pool/assignment storage must not be interpreted as absence of a sender or absence of consent. At the owning boundary log the original error message and safe provider/SQL fields through the existing Shared structured logger plus stage, bounded reason and opaque message correlation. Redact phones, tokens, URL credentials and message content. Route unknowns are expected no-merchant outcomes, not thrown fake provider errors. Preserve Messaging's existing v1 inbound/v2-v3 status retry contracts; do not publish a second job or re-enqueue on a deterministic mismatch.

## Work Items

- [ ] Implement inventory membership and positive original-message sender verification in the live inbound, guidance, STOP and status paths.
- [ ] Implement the indexed shop-route lookup, all-member eligibility and receipt-time checks, safe singleton/quote attribution, both-store deduplication and the typed BACKGROUND-004 handoff. Exercise races, delayed work and duplicates.
- [ ] Protect transactional and post-commit status effects. Implement the unit and disposable integration cases below.

## Interfaces / Contracts

Consume Shared `NormalizedWhatsAppInboundMessageSchema` v1 and normalized status v2/v3, and the existing Background-local send identity from BACKGROUND-002. `WhatsAppPoolSender.providerPhoneNumberId` identifies the immutable inventory record in this environment. `RecoverySenderAssignment.conversationId` identifies the original recovery even after release. `RecoverySenderAssignment.routeId` points to immutable `RecoverySenderRoute`, which retains the shop, canonical phone and inventory identity. A route with several active members is valid. `RecoveryBasketRoutingTurn.routeId` retains the original scope for a route-level inbound or prompt. `canonicalRecipient` contains the digits-only international number. For unassigned non-pooled dispatch, the stored pair comprises `dispatchProviderAccountId` and `dispatchProviderPhoneNumberId`. See Requirements for their complete precedence, eligibility and failure behaviour.

## Dependencies

`ARCH-076-BACKGROUND-002` must be accepted and integrated in the prepared task worktree.

## Enables

`ARCH-076-BACKGROUND-004` implements the same-shop basket resolver on the typed handoff.

## Acceptance Criteria

- [ ] Implement and cover the inventory classifier, pooled indexed lookup, explicit proof and exact UTC timestamp boundary. An unquoted reply can route even with eligible recoveries at two different shops. A pair with no active/confirmed owner never attaches by proximity.
- [ ] Demonstrate expiration at and before the inclusive cutoff, including before the sweep, followed by reuse for the same recipient at a different shop. A new post-confirmation free-text and voice reply enter only the new conversation, and a pre-send/boundary-second webhook, old quote and replay do not. A separate recipient on the same Moda phone remains independent.
- [ ] With three confirmed distinct same-shop checkouts, return all three to the resolver on the same sender. Keep a second shop on another sender and exclude its similarly named products. A quote of any eligible member takes its exact path. A wrong sender, unconfirmed outbound or ineligible member grants no evidence.
- [ ] Check replay during/after clarification including simultaneous duplicate deliveries, matched and stale prompt quotes, unrelated quoted basket messages, customer answers when only one displayed candidate remains, and the strict same-second boundary on one of multiple members. Verify no provisional checkout action or delayed cross-tenant effect, and that statuses for a prompt cannot touch billing, reachability or notices.
- [ ] Regression: first recovery A's dispatch result is initially unknown. Expire A, reuse its number for B, confirm B's first send, process an eligible fresh reply for B, then reconcile A's late receipt/status and redeliver the inbound event. B retains the assignment, inbound row and original version. A's receipt/status is historical, its release timestamp stays set, and a subsequent valid unquoted reply still goes to B. A new quoted A message can use only the ordinary historical path.
- [ ] Exercise changed owner during text persistence and between audio reservation and finalization with concurrent real PostgreSQL transactions and deterministic barriers. Assert durable conversation IDs, inboundVersion, activity time, attempt engagement and mocked enqueue/AI/media/guidance side effects. Test delayed turn after closure. Preserve genuine duplicate repair and all existing human/AI, moderation and 24-hour gates.
- [ ] Test quoted/standalone/invalid-quote STOP after reuse and on an allocation-disabled sender, unknown WABA, wrong phone, changed recipient, positive status on the old send, poisoned cross-sender FAILED and repeated valid FAILED/DELIVERED. Assert exact suppression scopes and absence of every incorrect write and post-commit call, with proper repair for the valid duplicates.
- [ ] Exercise a non-enrolled verified singleton and ambiguous legacy input per the cutover contract. A non-pooled first callback with a stored dispatch pair is valid. An unpinned historical send with exact prior stored delivery evidence is valid; corrupt/missing prior evidence stays unresolved even for unchanged current credentials. Drained pooled identities cannot take the singleton fallback. Existing general messages cannot be reclassified as a checkout.

## Validation

Run in the launcher-resolved Background task worktree against the accepted database submodule. Use the repository lockfile and generated Prisma client. Put new tests under `tests/integration/pooled-inbound-routing.integration.test.ts`, `tests/integration/pooled-status-routing.integration.test.ts` and existing focused unit owners. Reuse the existing fixture/barrier helpers, add small local scenario modules as needed. No live Meta, deployed data or billable model calls.

```bash
npm ci
npm run prisma:generate
npm exec -- vitest run tests/unit/services/recovery-routing.service.test.ts tests/unit/services/whatsapp-inbound-processing.service.test.ts tests/unit/services/inbound-whatsapp-audio.service.test.ts tests/unit/services/whatsapp-contact-opt-out.service.test.ts tests/unit/services/routing-guidance.service.test.ts tests/unit/services/whatsapp-provider-status.service.test.ts tests/unit/workers/whatsapp.worker.test.ts
node scripts/test-integration.mjs tests/integration/pooled-inbound-routing.integration.test.ts tests/integration/pooled-status-routing.integration.test.ts tests/integration/recovery-recipient-routing.integration.test.ts tests/integration/woo-recovery-inbound-routing.integration.test.ts tests/integration/whatsapp-contact-opt-out.integration.test.ts tests/integration/routing-guidance-stop-fence.integration.test.ts tests/integration/recovery-human-provider-status.integration.test.ts tests/integration/arch056-inbound-lock-order.integration.test.ts tests/integration/arch056-inbound-rollback.integration.test.ts
npm run build
npm run lint
git diff --check
```

- [ ] Unit/real disposable pg17+pgvector and Redis checks ran (including guarded tests, with no silent skips), production build, lint and whitespace checked. Record individual results and container cleanup. Source/permissions/provider-fixture mismatches go in the Completion Report with exact diagnostics.

## Implementation Notes

Portable definition, defined but not materialised. Start through `/moda-task ARCH-076-BACKGROUND-003`. Record launcher packet, physical parent/implementation paths and branches, starting SHAs, database pin, end SHAs, changed paths, commands and results. With the task complete set the parent task YAML to review, submit the Completion Report to moda_architect and stop. Do not change shared indices, merge, deploy or begin system-test execution.

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
