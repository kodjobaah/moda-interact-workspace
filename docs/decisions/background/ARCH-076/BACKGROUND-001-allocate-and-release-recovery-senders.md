---
id: ARCH-076-BACKGROUND-001
architecture_id: ARCH-076
title: Share WhatsApp senders by shop and release them after the last checkout
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-076-DATABASE-001]
enables: [ARCH-076-BACKGROUND-002]
created: 2026-11-13
updated: 2026-11-13
---

# Share WhatsApp senders by shop and release them after the last checkout

## Architecture

[ARCH-076 — WhatsApp sender pool and checkout reply routing](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinated by `moda_architect`.

## Objective

Give each customer/shop pair one sending number while any checkout has an open membership. Allow all separately eligible checkouts at that shop to share it. Release each checkout independently and make the sender available across shops immediately when its last member ends.

## Context

Preserved from original local commit `59705bb589342f31054e6c1fd011dacf9d495ae6` under root-authorized ARCH-076 collision correction. Defined portable design only; Pending/unclaimed until current-main compatibility review and explicit architect promotion. No runtime implementation or launch is authorized by preservation.

Implement Background-owned allocation, release and wait discovery in the repository named above. All paths below are relative to that repository. Read the [parent architecture](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md) and the accepted DATABASE-001 definition. Pin `database` to the integrated DB revision that contains that migration. This task supplies working database services, terminal transition wiring and integration tests. BACKGROUND-002 owns enabling pre-credit selection in the two outbound entry points, the repair-worker job handler and the provider-send bridge. Keep repair discovery exported and directly tested here. Wire the tick and worker together in BACKGROUND-002 so an intermediate checkout never publishes unrecognised jobs.

## Scope

Own the three new sender-pool service modules, shared expiry operation, existing recovery terminal writers and focused unit/PostgreSQL tests listed below. Paths are relative to `moda-interact-background`.

## Out of Scope

The final permit, HTTP transport, Admin UI, schema migration, webhook routing and activation are separate boundaries.

## Requirements

The shop supplies checkout identity through its platform and its existing checkout lifecycle. Repeated events for the same checkout use existing generation/attempt semantics. A separate eligible checkout at that shop remains a separate recovery, conversation, consent/admission evaluation and credit. Never deduplicate, cancel or supersede it solely because the customer phone or sender is shared. PostgreSQL enforces one open shop route for (canonicalRecipient, shopId) and a single shop owner for each (canonicalRecipient, providerPhoneNumberId). Each recovery conversation independently joins that route. Detect effective expiry immediately, including before a sweep. A temporary pre-credit membership occupies a route slot but becomes eligible for normal replies only after that recovery's eligible initial send is confirmed. Release after the last open member, including clean-up of never-admitted preparations. Retain exact sender history for admitted messages.

## Work Items

- [ ] Add `src/services/whatsapp-sender-pool/assignment.ts`, `expiry.ts` and `waiters.ts`. Use the existing Prisma client and bound values for SQL. The new directory owns one implementation shared by the Shopify and Woo paths. Keep runtime names domain-specific. Use `canonicalWhatsAppSender` from `src/services/whatsapp-contact-opt-out/phone.ts`, returning the digits-only canonical form or an invalid-owner result. Propagate actual database/configuration errors.
- [ ] Export `prepareInitialSender({shopId,recoveryId,conversationId,attemptId,recipient,providerAccountId})`. Success returns `{kind:'assigned',routeId,assignedAt,sender:{providerAccountId,providerPhoneNumberId}}`; the internal Date assignedAt and routeId identify this exact provisional membership. Resolve shop/recipient/checkout ownership from persisted rows, never from a model or client. Remaining outcomes are `{kind:'pool-exhausted'}`, `{kind:'ineligible'}` and `{kind:'already-admitted'}`. If there is no existing open same-shop route and no new eligible sender, return pool-exhausted. Require one current matching shop, RECOVERY conversation, current checkout generation, active canonical recipient and eligible sequence-one attempt before a new claim. Accept PENDING, and CAPACITY_BLOCKED **only** when the existing authorised billing-capacity re-entry calls this path and has proved its ordinary preconditions. Preserve every existing billing failure code/hold. A CAPACITY_BLOCKED attempt can occupy an available tentative sender for its ordinary re-entry; if the pool is full, retain billing capacity as its existing retry owner and never replace its status with PENDING or overwrite its reason. Check the exact attempt's dispatch and receipt proofs even when its outboundMessageId is still null (use the existing initial admission idempotency-key lookup). Admitted/sent/unknown evidence returns already-admitted to existing continuation. Never manufacture an assignment to explain an old permit. Only current DETECTED recoveries are eligible to claim. Legacy customer snapshots still follow existing ownership rules.
- [ ] In a short claim transaction take `pg_advisory_xact_lock(hashtextextended('whatsapp-pool-allocation:' || $1,0))` on the bound canonical recipient before any other row locks. Revalidate this attempt under the existing Shop -> Conversation -> CheckoutRecovery -> attempt lock order. Probe its immutable conversation membership first. Discover routeId without a member lock, lock its immutable route row first, then re-read/lock the exact member and compare the original route ID. Unreleased matching member and open route return their original sender/assignedAt idempotently. If released or wrong shop, recipient, WABA or generation, return ineligible, never re-home it. A previously admitted conversation lacking a historical membership follows its existing reconciliation.
- [ ] If this checkout has no member, look up the existing open `whatsapp."RecoverySenderRoute"` by its exact (canonicalRecipient, shopId), join the verified inventory WABA, and lock the route row. If it still exists and has at least one live/provisional sibling, insert **only this checkout's membership** under that route. Reuse it even when its inventory row is currently drained, another sender is idle, or every sender is occupied by open routes. Draining prevents new shop routes. It does not split an existing shop thread or prevent another eligible checkout at that shop joining it. A conflicting WABA/identity is a typed ineligible/configuration failure, with no reselection. Never merge conversations or select an existing checkout here. Re-read the owner if a wait on its route lock observes closure. A found route with no current member must first be closed under its row lock; this prevents attachment to an earlier, empty route generation.
- [ ] Otherwise start a new route. Select the first enabled inventory entry on the trusted WABA, ordered by `priority ASC, "providerPhoneNumberId" COLLATE "C" ASC`, with no open route for (canonicalRecipient, providerPhoneNumberId). Lock the inventory row FOR SHARE; recheck priority candidate eligibility and drain state. Insert the route with database time and its first member in the same transaction. `RecoverySenderAssignment.conversationId` PK and the two open-route partial unique indexes enforce ownership. Use conflict-safe inserts, re-read an atomically claimed same-shop route or retry another eligible sender. Under a competing claim a checkout can never have two memberships or two charged initial sends. No Redis lock or contact row serializes assignments across tenants.
- [ ] Expire stale members by exact recovery ID before declaring a route occupied. Discover only this recipient's relevant open routes and their members using the partial indexes in DATABASE-001. Perform conditional expiry on stale owners one recovery at a time in separate short transactions using the same operation as the scheduler; never hold a new shop's or recipient allocation lock while expiring a different shop. At claim time, if a prior open member was found newly due or terminal, exit the claim transaction without business effects, process that owner and reread. Use the actual database cutoff and status, latest platform generation, and ordinary expiry side effects. An already-terminal member with a stale open row is released on exact owner proof. Close an empty orphan route under its lock if a cascade removed all of its members. While a shop route retains **any** live or valid pre-credit member, another shop cannot use its number for this recipient. Three retries for SQLSTATE 40001/40P01, then log and let the existing job retry. A database failure never becomes pool exhaustion.
- [ ] Extract the exact expiry cutoff used by `src/services/checkout-recovery-expiry.service.ts` (retain BigInt arithmetic/range handling, zero and inclusive `lastExternalActivityAt <= now - lifetime`). Reuse `src/services/recovery-lifetime/checkout-recovery-lifetime.ts` for policy parsing. Read `checkoutRecoveryLifetimeDays` for the active environment from the same runtime config row as the Woo initial fence. Do not substitute an arbitrary maximum. Recheck time after lock acquisition in claim and permit. Compare actual DB status and the cutoff even before the scheduled sweep. On expiry/cancellation/completion close only the member for this checkout. After its existing recovery lock, read the member route ID without taking a member row lock, take the immutable route row FOR UPDATE, then lock/update the member. Require the same route ID, conversation ID and `releasedAt IS NULL`. Use database statement time. Under that same route lock run `UPDATE whatsapp."RecoverySenderRoute" r SET "closedAt"=statement_timestamp() WHERE r.id=$1 AND r."closedAt" IS NULL AND NOT EXISTS (SELECT 1 FROM whatsapp."RecoverySenderAssignment" m WHERE m."routeId"=r.id AND m."releasedAt" IS NULL)`. Use a fresh READ COMMITTED statement snapshot after acquiring the lock, or retry the whole operation on serialization conflict. Never lock all sibling recoveries/members merely to count them. Attach and every close/discard serialize on that route lock before modifying any membership. Final fences honor established Shop/Conversation/Recovery ordering, then route -> member. Close never takes the allocator advisory lock. Closing the route immediately invalidates every pending basket clarification on that route ID. BACKGROUND-004 owns revalidation and bounded content cleanup. Release does not wait for a cleanup job. An old route can never attach to its successor. Preserve history and existing attempt, usage, support and status-history effects.
- [ ] Wire this terminal-release operation inside the same transaction as the successful status CAS in `src/services/checkout-recovery-expiry.service.ts`, `src/services/checkout-recovery/order-recovery-correlation.service.ts`, `src/services/checkout-recovery/recovery-capacity-resume-terminalization.ts`, `src/services/woocommerce-recovery/woo-checkout-activity.adapters.ts` (closeForResumption) and `src/services/woocommerce-recovery/woo-order-reconciliation.service.ts`. Inspect repository writers of CheckoutRecovery terminal status for equivalent SQL transitions. Release the old member by exact conversation and route. Closing A1 with A2 still open preserves that shop route and sender. Independent checkout keys remain eligible, including for the same recipient. Closing the final member makes the sender immediately reusable. A stale close of A1 cannot close or discard A2 or a newer shop route. Keep the existing terminal writer lock discipline and transaction boundaries.
- [ ] Export `requireAssignedSender(tx,{shopId,recoveryId,conversationId,recipient,providerAccountId})` for BACKGROUND-002. Caller already holds the normal final-fence shop/conversation locks. Lock the recovery row before route and member; verify the exact recovery-conversation membership, unreleased member, unclosed route, route.shopId and canonicalRecipient, WABA, latest generation, status and effective lifetime. Shared ownership by a sibling gives no permission to send on the target recovery. Disabled inventory still permits use of an open shop route. Use current statement time, not a config-cache TTL, to decide expiry. Return the existing assignment or ineligible. Never create/transfer a row or acquire the allocation advisory lock from a final fence. Reuse this owner check in the inbound task where a current route needs revalidation.
- [ ] Export `discardUnusedPreparation({shopId,recoveryId,conversationId,attemptId,recipient,routeId,providerPhoneNumberId,assignedAt})` using the typed proof from the claim. Under the same owner locks, compare exact original preparation identity (return the persisted assignedAt to the coordinator as an internal receipt); use the checkout's existing coordination plus durable attempt/message/credit evidence before removing it. Under route -> member locks, delete only the exact never-admitted membership after proving no admitted/confirmed/unknown dispatch for this conversation, no in-progress rival pre-credit handoff, and an absent or definitively released credit reservation. If it was the final open member, close that same route with the locked empty-membership test. Siblings, their reservations and original sender evidence remain independent. Where durable state cannot prove exclusive ownership, retain it for replay or expiry. After any admitted permit keep the row as original sender history and only close via release time. Never reopen RELEASED billing reservations.
- [ ] An existing eligible same-shop route always takes precedence over declaring a waiter, even on a one-number full pool. Waiting is represented only by `commerce."RecoveryOutreachAttempt"` with sequence 1, PENDING and `failureCode='WHATSAPP_SENDER_POOL_EXHAUSTED'` (index from DATABASE-001). Set marker in the same transaction where a clean pre-credit claim confirms exhaustion. No Meta calls, UsageReservation, dispatch permit or extra attempt. Reconfirm no prior billing reservation/permit before first marking. A pre-existing reserved or uncertain credit without ownership follows the explicit cutover/reconciliation path, never the new waiter branch. Clear only this marker on the exact attempt in the same transaction as a successful initial claim. The stored tentative assignment is its durable replacement during the pre-credit handoff. An already claimed same-owner retry clears a stale identical marker idempotently. Existing initial-credit validation treats a non-null failureCode as a hold. Preserve all other failure codes.
- [ ] Export `dispatchWaitingRecoveries({limit,enqueue})`. Use the existing recoveryRepairShopBatchSize as the positive bound. Page oldest by attempt.updatedAt ASC, id ASC under the partial index. Select DETECTED active owners only, clearing stale markers on terminal/non-pending rows by conditional update. Enqueue only {recoveryId,attemptId} from persisted state. On durable queue acknowledgement conditionally advance that waiter's updatedAt using its observed timestamp and marker; keep the marker for crash recovery. Rotate still-busy rows (and log/rethrow queue failures after attempting the rest of the batch). Older rows must not permanently starve a later eligible recipient. A later repair tick can republish missing work after restart or Admin enables a sender. As a separate bounded repair query in this same pass, identify open provisional rows with a DETECTED unblocked recovery, sequence-one PENDING attempt, no competing terminal/settlement proof, and no provider permit. These cover a crash after successful claim/marker clear and before billing or dispatch. Use the open member index joined to its unclosed route and conversation->recovery and unique (recovery,sequence), order by attempt.updatedAt,id, limit per branch, advance selected attempt.updatedAt conditionally only after acknowledgement. Include legal retained pre-permit prepared message/credit so its original continuation can finish. Require policy eligibility again at dispatch. Release unused preparations proven terminal or definitively pre-permit denied; avoid waking billing-capacity/consent-blocked recoveries under this scheduler. No new lease, service, unbounded sweep, cross-shop customer table or outbound call in the scheduler.

## Interfaces / Contracts

`prepareInitialSender`, `requireAssignedSender`, `discardUnusedPreparation` and `dispatchWaitingRecoveries` are Background-local calls with the inputs and results frozen above. Successful preparation returns the trusted sender pair, `routeId` and `assignedAt` for tentative-cleanup CAS. `requireAssignedSender` returns only current pinned sender details and route identity for the caller’s exact member. Recovery-level outbound remains per checkout; shop-level clarification never uses this call as a surrogate recovery permit. The authenticated WABA is supplied from the encrypted server configuration. DATABASE-001 is the schema and index owner.

## Dependencies

ARCH-076-DATABASE-001, accepted and integrated.

## Enables

ARCH-076-BACKGROUND-002.

## Acceptance Criteria

- [ ] Concurrent A1/A2 for the same shop and recipient use exactly one route/sender and two recovery memberships. Replays return the original route/member. Concurrent A and B for the same recipient use distinct senders. Another recipient can independently use either. Business tests distinguish two real checkout identities from an update/duplicate of one.
- [ ] Each terminal transition releases only the exact member. A live sibling keeps the number for its shop. Expiry/release of the last member frees the pair immediately, including before the sweep. Empty routes left by cascade have no long-lived claim.
- [ ] Busy attempts incur no billing/permit, persist the exact wait marker and are discoverable fairly after a crash.
- [ ] Verification covers released historical rows, orphan tentative rows, drain, concurrent lifetime/activity changes and failed queue acknowledgements.

## Validation

Add `tests/unit/services/whatsapp-sender-pool/assignment.test.ts`, `waiters.test.ts` beside it and `tests/integration/whatsapp-sender-pool-lifecycle.integration.test.ts`. Run from the prepared repository worktree:

```bash
npm ci
npm run prisma:generate
npx vitest run tests/unit/services/whatsapp-sender-pool tests/unit/services/checkout-recovery-expiry.service.test.ts
node scripts/test-integration.mjs tests/integration/whatsapp-sender-pool-lifecycle.integration.test.ts
npm run build
git diff --check
```

Use disposable PostgreSQL 17 + pgvector and Redis under the integration harness. Use independent DB connections and deterministic barriers. Demonstrate (1) two real A checkouts with one phone share one route even when S2 is free, when only S1 exists, and when S1 is subsequently drained; two shops for X receive distinct numbers, repeats of one recovery use the same member, and other recipients can reuse S1; (2) one-number exhaustion has a pending waiter and zero charges; (3) immediate availability at the exact configured cutoff, before the sweep, after it, for zero days, and after completion/cancellation/Woo resumption; (4) activity CAS racing expiry, lazy reclaim racing sweep, concurrent opposite-shop expiries, inventory drain and stale close vs newer assignment; (5) tentative cleanup cannot erase a competing/admitted permit; (6) concurrent A1 release versus A2 attach, simultaneous closure of A1/A2, cascade-to-empty route, different-shop reclaim and stale A1 close after reuse; prove no double route, no prematurely closed live A2 route, and eventual waiter success after the final release; (7) queue publication failed before/after commit, paging fairness, replay of cursor timestamp CAS, preserved credit history and pre-cutover unassigned already-sent evidence. Verify row counts, actual sender IDs and history, not solely return kinds. Check the identity and lifecycle of each route, membership and provider permit separately. Recheck merchant-specific STOP/consent and per-recovery credit evidence independently for every member. Keep provider-ambiguous credit correction independent of release.

## Implementation Notes

Stop and return exact path/symbol and failing test/SQLSTATE if the accepted DB artifact lacks required names/indexes. Report newly observed supported paths to the architect when they contradict the binding. No provider enrolment, live send, deployment, historical migration edit or new billing algorithm. Record baseline defects separately.

Portable definition. /moda-task ARCH-076-BACKGROUND-001 after dependency integration. Report prepared parent/implementation worktrees, branch/SHA and database pin, changed paths, command/exit codes, all DB/Redis cleanup and concurrency proof in this task. Return for architect review. Execution status: not started.

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
