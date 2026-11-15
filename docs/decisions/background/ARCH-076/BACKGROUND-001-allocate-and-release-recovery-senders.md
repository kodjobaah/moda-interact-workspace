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
updated: 2026-11-15
---

# Share WhatsApp senders by shop and release them after the last checkout

## Objective

Choose and persist the sending number for each eligible checkout before credit is reserved. Release that checkout independently when it ends. Provide the recovery worker with a bounded way to resume interrupted pre-credit work. Emit one traceable, server-side diagnostic for each actual failure.

## Architecture and delivery boundary

This is the binding Background contract for ARCH-076. The R07 DATABASE-001 contract owns the tables and indexes. BG001 owns allocation, transactional release, read-only sender verification inside a caller's transaction, repair discovery, and the corresponding diagnostics. BG002 activates initial sender selection, issues final permits and wires the repair job. BG003/BG004 own inbound routing, clarification and transcript handling. The existing recovery-per-checkout and merchant consent and billing rules continue to govern each individual basket. An assigned sender alone does not admit an outbound or make an unsent basket eligible for normal replies.

The platform must have at least one verified, enabled number for its active WhatsApp Business Account (WABA) once pooled sending is active. Admin owns activation, rejecting a change that disables the final enabled sender, and safe account changes. The migration can create an empty inventory before activation. The Admin owner must enforce that rule across concurrent configuration writes before pooled sending goes live. Reconcile the earlier ADMIN-001 enable/drain rules and BG002's `sender-pool-exhausted` result with this contract in their own handoffs. This task supplies the defensive Background behaviour for configuration drift. For a clean uncharged initial attempt, store the technical fault marker on that original attempt so repair can discover it. Billing-capacity re-entry keeps its existing retry owner. `CheckoutRecovery` gains no state. An occupied enabled sender always provides capacity for a new shop route.

## Repository touchpoints

All code paths below are relative to `moda-interact-background`. Use domain terminology for new production symbols and event names. Preserve existing status-history source values. Keep architecture IDs in task records and tests.

| Action and path | Responsibility |
| --- | --- |
| Create `src/services/whatsapp-sender-pool/assignment.ts` | Export the three allocator, verification and discard functions and their typed results from the contract below. |
| Create `src/services/whatsapp-sender-pool/assignment-store.ts` | Own bound allocation SQL, route ranking, ownership rechecks and exact conditional writes. Use `rows`, `first`, `changed`, and the `SqlTransaction` port from `src/services/recovery-conversation/recovery-conversation.sql.ts` for raw SQL. The read-only final-fence contract accepts the existing narrow port. |
| Create `src/services/whatsapp-sender-pool/expiry.ts` | Share the cutoff, live expiry transition and exact release operations. The five terminal-writer edits and existing scheduler error hook are listed below. |
| Create `src/services/whatsapp-sender-pool/waiters.ts` | Discover pending technical repair or a provisional assignment and run the injected enqueue function outside database transactions. |
| Create `src/services/whatsapp-sender-pool/diagnostics.ts` | Shared structured logger, redacted original failure details, and the existing operational incident surface. |
| Edit `src/services/outbound-whatsapp-admission/outbound-admission-reservation.service.ts` | Extract the complete existing `OutboundAdmissionReservationService.inspectInitialOutreachAdmission` classification into exported `inspectInitialOutreachAdmissionInTransaction(tx, scope)`. Preserve the class method, its signature and results as the public wrapper; keep current validation and a single transaction for existing callers. The allocator/discard paths use the transaction-local function. Do not call the wrapper from inside an open transaction. |
| Consume `src/services/recovery-billing/initial-outreach-credit-evidence.ts`, `src/services/recovery-delivery-compensation/lineage.ts`, `src/services/whatsapp-contact-opt-out/phone.ts`, `src/services/recovery-lifetime/checkout-recovery-lifetime.ts` | Reuse the current attempt/message lineage, `findExactRecoveryReservationSource`, `canonicalWhatsAppSender` / `matchesRegisteredPhone`, and `parseCheckoutRecoveryLifetimeDays`. No copied credit-key builder, international phone parser or policy defaults. |
| Consume the integrated `database` gitlink | Use the Database implementation commit accepted for DATABASE-001 via the repository's normal gitlink process. Generate the Prisma client from `database/prisma/schema.prisma`. Do not edit vendored schema/migrations or bump Shared libraries. |
| Existing `src/entrypoints/recovery.ts` | In the existing expiry scheduler's error hook use the safe diagnostic projection. Preserve its failure signal and the owning service identity. BG002 separately wires the repair callback. |
| Tests | Create the focused unit and integration files listed under Validation. Update the existing terminal, expiry and admission-classifier tests affected by the named code edits. No new worker, scheduler lease, API, feature flag or production deployment in this task. |

Read the parent [ARCH-076 architecture](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md) and [DATABASE-001](../../database/ARCH-076/DATABASE-001-create-sender-pool-and-active-assignments.md) when materialised. This portable handoff includes the decisions needed to implement BG001 even when the earlier parent architecture patch has not been applied.

## Local contracts

Use TypeScript discriminated unions. The following names and fields bind BG002 and make unit tests independent of provider I/O. Scalars below are immutable for one invocation.

```ts
type Sender = Readonly<{ providerAccountId: string; providerPhoneNumberId: string }>;
type Scope = Readonly<{
  shopId: string; recoveryId: string; conversationId: string;
  recipient: string; providerAccountId: string;
}>;
type PreparationScope = Scope & Readonly<{
  attemptId: string; mode: "initial" | "capacity-resume";
}>;
type Assigned = Readonly<{
  kind: "assigned"; routeId: string; assignedAt: Date; sender: Sender;
}>;
type DenialReason = "invalid-recipient" | "owner-mismatch" | "not-current" |
  "inactive" | "expired" | "attempt-ineligible" | "released" |
  "waba-mismatch" | "missing-assignment" | "credit-reconciliation" | "lineage-conflict";
type Ineligible = Readonly<{ kind: "ineligible"; reason: DenialReason }>;
type ConfigurationFault = Readonly<{
  kind: "sender-configuration-fault"; reason: "no-enabled-sender";
}>;
type Preparation = Assigned | Ineligible | ConfigurationFault |
  Readonly<{ kind: "already-admitted" }>;
type DiscardScope = Scope & Readonly<{
  attemptId: string; routeId: string; providerPhoneNumberId: string; assignedAt: Date;
}>;
```

- `prepareInitialSender(input: PreparationScope): Promise<Preparation>` owns its short transactions. Normal Shopify, Woo and ordinary repair use `initial`. Only the verified Shopify billing-capacity re-entry uses `capacity-resume` after its existing gate succeeds. Always re-read the exact attempt and owner. Return `assignedAt` from the stored row on both insert and retry.
- `requireAssignedSender(tx: SqlTransaction, input: Scope & { phase: "initial" | "ongoing" }): Promise<Assigned | Ineligible>` is a read/lock operation on the caller's transaction. The caller holds the established Shop/Conversation locks. Resolve and lock the recovery and sequence-one attempt, then verify the original generation, live policy, recipient, WABA, thread, route and membership. Initial requires DETECTED/initial scope. Ongoing requires MESSAGE_SENT or ENGAGED and a confirmed initial outreach to the same recipient with that membership. Allow a drained sender on the live original route. A missing assignment is ineligible. No allocation lock, reassignment, new permit, usage write, credit mutation or provider request. Neutral thread prompts use their own later permit.
- `discardUnusedPreparation(input: DiscardScope): Promise<"discarded" | "retained" | "absent">` revalidates the exact stamped member under the same owner/parent locks. Return absent for no member, retained for a surviving or inconclusive claim and discarded only on a successful exact conditional deletion. An exception propagates; it cannot become a business result. A live provisional claim with no credit yet is itself a recovery point. Use the durable evidence below to prove the disposition. Concurrent workers can see the same assignedAt before either reserves credit. For an ordinary otherwise-eligible attempt retain the member when a concurrent pre-credit coordinator could still proceed. Delete only when locked durable state proves the attempted handoff is definitively denied/ended, no current rival can legally continue it, there is no admitted/uncertain send, and reservation lineage is absent or definitively released. For this operation a durable definitive denial is the exact initial attempt in FAILED or CANCELLED with a confirmed pre-permit-only disposition, on its original checkout. A billing-capacity hold alone is insufficient. For a CAPACITY_BLOCKED attempt retain the row whenever an authorised capacity-resume handoff could already be in progress. The stamped input does not convey a lease or exclude a rival; under this contract return retained for that case and let scope-checked replay or terminal expiry handle it. On any still-eligible PENDING attempt retain its existing member. For terminal recoveries invoke the terminal release operation so admitted history is preserved. An orphaned or inconsistent existing membership produces `retained` and a scoped owner diagnostic. A timeout cannot establish no-send. After any durable permit preserve the membership for history and release it only via the terminal path.
- `expireRecoveryIfDue(tx: Prisma.TransactionClient, recoveryId: string): Promise<boolean>` returns true only for a winning active-to-EXPIRED transition. `releaseRecoverySender(tx: Prisma.TransactionClient, recoveryId: string): Promise<{threadId:string;routeId:string;conversationId:string;routeClosed:boolean;threadClosed:boolean} | null>` clears the exact technical marker, releases the original owner and closes its emptied parents. Return a record on a winning member release, otherwise null. The existing public terminal-writer signatures stay intact. `dispatchWaitingRecoveries` has the signature and repair rules below. Use the owning process's logger through injection, with the existing worker logger as the default.

## Allocation and database transaction

1. Canonicalise the recipient supplied by the confirmed checkout owner. Validate it against the current exact recovery, sequence-one attempt, linked customer and registered recipient under the existing rules for that shop (including verified-country legacy phone handling). Different merchants may register the same customer number. Compare `Conversation.checkoutRecoveryId` and the recovery's `shopId`; a nullable legacy `Conversation.shopId` is valid when its recovery establishes the shop. Verify the latest generation for the same shop/checkout token. A different real checkout token is a separate basket.
2. Use short READ COMMITTED transactions and fixed SQL with bound data. On the positive claim path first acquire `pg_advisory_xact_lock(hashtextextended('whatsapp-pool-allocation:' || $1,0))` on the canonical recipient. Then lock the owning Shop → Conversation → CheckoutRecovery → RecoveryOutreachAttempt in the existing order. Lock/read the current lifetime before the inventory and sender locks. Recheck current facts after lock waits. Only DETECTED, within-lifetime recoveries can receive a fresh initial claim. Perform cleanup/release for an expired owner independently of preserving a historical permit. Inspect exact pre-existing admission before creating any member or marker. An exact prior classified confirmed or provider-uncertain/admitted dispatch takes precedence over an initial-only status guard and goes to existing continuation (`already-admitted`). Failed terminal dispositions stay with existing failure handling. A lineage conflict returns its own denial. Check `UsageEvent.idempotencyKey = 'recovery-outreach:' + attemptId` even when `outboundMessageId` is null. Verify the just-read reservation using `findExactRecoveryReservationSource(tx, shopId, attemptId)`. A retained credit/prepared message may continue on its existing matching assignment. Existing credit or prepared/admitted evidence without matching ownership cannot create an explanatory assignment or a new fault marker. Preserve its original reconciliation path. No reservation or send in the allocator.
3. For an existing membership, discover the original parent IDs without taking a child lock. Lock thread → route → assignment and re-read all IDs, ownership and open/released stamps. Retry returns that same persisted sender, route ID and assignedAt. Never re-home a released member. For a new checkout at the same shop, lock and reuse its open route for this customer, even when the number is disabled for new shops. Attach only the new conversation. A successful claim clears only its exact technical repair marker in this same transaction. Ineligible, stale or wrong-WABA evidence cannot authorize selection of a replacement.
4. Before reusing a sibling route or ranking, resolve effectively expired/terminal members and empty routes/threads for this recipient. Discover using the R07 open-row indexes. If found under the claim locks, exit without side effects, release the locks, run single-owner expiry/cleanup transactions and retry the claim on current data. Never expire another shop inside the allocating shop's transaction. For cascade-created empty parents close by original ID under the same parent locks as release. Do not attach to an empty generation. A new X/S1 after the last shop closed gets a new thread ID, without a cooldown.
5. For a new shop, start with enabled rows in `whatsapp."WhatsAppPoolSender"` for the trusted WABA. LEFT JOIN each phone's open `RecoverySenderThread` for the canonical recipient, then its open `RecoverySenderRoute` rows. Rank by `count(route.id) ASC, priority ASC, providerPhoneNumberId COLLATE "C" ASC`. Count live shop routes for this recipient/number, including valid provisional routes. Multiple checkouts at a shop count once. An idle number wins. When every number is occupied choose the first ranked enabled number and create a separate merchant route on its existing thread. Eligibility and charging remain per checkout. No prior assignment moves.
6. Lock the chosen inventory row FOR SHARE in a separate query, recheck account and enabled state, then lock/recheck the live thread FOR UPDATE. Repeat the ranking read using a fresh statement snapshot before writing. If that winner or live generation changed, restart the claim with fresh facts. A simultaneous close on an independent thread may linearise after the last ranking read. Atomically create the thread if necessary, the route and its member. Use the exact R07 open-thread key, open-customer/shop key and conversation PK. An expected unique collision rolls back the failed transaction before an exact re-read. No overlapping business locks from different shops. Transient PostgreSQL serialization/deadlock failures get up to three retries after the first attempt (four attempts total); handle documented Prisma P2034 and raw SQLSTATE 40001/40P01 without inventing a SQLSTATE if absent. Retry a 23505/P2002 only for `RecoverySenderThread_open_recipient_sender_key`, `RecoverySenderRoute_open_recipient_shop_key` or `RecoverySenderAssignment_pkey` confirmed by the constraint/metadata and verified owner on reread. Use the same three-retry ceiling for recoverable constraint contention. On exhaustion preserve and rethrow the last real exception. Re-throw unknown conflicts and all other dependency failures with their original diagnostic. Report each real retry individually. Exhaustion of a transaction retry budget is a database failure.
7. Before deleting a never-admitted provisional member, double-check its exact store, WABA, route, sender, conversation, assignedAt, authoritative provider and billing evidence. Preserve a sibling, a possible rival, a retained reservation, and ambiguous or confirmed provider evidence. A definitive deletion closes only emptied original parents. For closed/admitted memberships retain route and thread history needed for old receipts. Ignore allocationEnabled on existing eligible routes. The database pin owns integrity constraints, indexes and field defaults. No schema changes belong here.


**Denial mapping.** Return `invalid-recipient` when canonicalisation fails, `owner-mismatch` for a conflicting shop/customer/attempt/conversation or a changed verified recipient, `not-current` for a superseded generation, `expired` for an elapsed lifetime or EXPIRED state, and `inactive` for COMPLETED/CANCELLED or a status incompatible with the requested operation. Use `attempt-ineligible` for a wrong sequence/status/block reason or an unproven capacity-resume path, `released` for a released member or closed original parent, `waba-mismatch` for a proven account mismatch, and `missing-assignment` when the verify-only caller has no member. `credit-reconciliation` and `lineage-conflict` follow the evidence rules below. Compare the current account only with trusted configuration and persisted inventory. An adapter exception is never converted to a denial code.

**Existing admission-classifier mapping.** Keep the normal method's outcomes for its existing callers. In preparation, `confirmed` and `held/provider-outcome-unknown` transfer to prior-admission reconciliation. `held/lineage-conflict` is `ineligible/lineage-conflict`. `failed` in any disposition keeps the existing failure/finalisation owner and returns `ineligible/attempt-ineligible`. An `absent` result permits a fresh claim only with clean credit and ownership. A `prepared` or retained pre-permit credit may use its matching, active member. Missing original ownership on either returns `ineligible/credit-reconciliation`. A failed lookup throws its real error. Discard uses the explicit pre-permit-refused disposition as one piece of evidence and rechecks the full durable criteria.

## Shared expiry and terminal release

Use `src/services/whatsapp-sender-pool/expiry.ts` for the transaction-local `expireRecoveryIfDue(tx, recoveryId)` and `releaseRecoverySender(tx, recoveryId)`. The scheduled sweep and the allocator's cleanup call the former. All five terminal writers call the latter after a successful terminal change and before committing. When a historical recovery has neither the technical marker nor an assignment, release is a successful no-op. Neither helper opens a nested transaction.

| Existing Background file and symbol | Exact edit |
| --- | --- |
| `src/services/checkout-recovery-expiry.service.ts` · `CheckoutRecoveryExpiryService.expireInactive` | Retain its public arguments, count and 100-row / 1,000-page bounds. Move the existing BigInt `expiryCutoff` into `whatsapp-sender-pool/expiry.ts`. Use a strict keyset cursor on the **observed** `(lastExternalActivityAt,id)` for the ascending candidate scan, advancing past skipped rows as well as changed rows. The scheduler's runtime snapshot and optional clock argument apply to discovery only. In each candidate's existing transaction call `expireRecoveryIfDue`. Count only successful changes. |
| `src/services/checkout-recovery/order-recovery-correlation.service.ts` · `OrderRecoveryCorrelationService.handleOrderCompleted` | Keep checkout-token coordination, latest generation selection and history. After the successful completion update and history insertion, release that recovery in the same transaction before returning `completed`. The candidate-only and failed-CAS returns do not release a sender. |
| `src/services/checkout-recovery/recovery-capacity-resume-terminalization.ts` · `terminalizeUnrecoverableBlockedRecovery` | In the existing `updated.count === 1` branch, after cancellation history, release this recovery before commit. Preserve block-reason predicates and suppression wakeup rules. |
| `src/services/woocommerce-recovery/woo-checkout-activity.adapters.ts` · `WooExistingRecoveryRepository.closeForResumption` | After the exact shop/token/generation/activity CAS succeeds and writes `CHECKOUT_RESUMED` history, release only the old recovery before returning true. Ordinary `recordExternalActivity` continues to advance activity without releasing anything. |
| `src/services/woocommerce-recovery/woo-order-reconciliation.service.ts` · `WooOrderReconciliationService.transitionRecovery` | After the current CAS, history insert and unsent-attempt cancellation, release before returning `changed`. Keep the existing paid → COMPLETED and placed/cancelled → CANCELLED mappings, event time, retry on lost CAS, and Redis coordination. |

**Expiry decision.** Lock the exact recovery row first. Read `public."BackgroundRuntimeConfig"` with `id='default' FOR SHARE` using the same transaction, then obtain `statement_timestamp()` in a fresh statement after the locks are acquired. Bind the existing policy parser in `src/services/recovery-lifetime/checkout-recovery-lifetime.ts` to that locked read, following the policy access pattern in `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts`. The unlocked reader and a timestamp captured when the transaction began cannot decide a release. Recheck persisted active status (DETECTED, MESSAGE_SENT or ENGAGED) and latest external activity against the inclusive cutoff. Preserve zero days, millisecond precision, BigInt arithmetic and the representable PostgreSQL/JavaScript date bounds. An unrepresentable past cutoff means no recovery is due. A missing policy row throws the existing missing-policy error. For an invalid value emit the policy event and rethrow the original parser exception. Both paths roll the transaction back. Keep the existing history reason/source and unsent-attempt filters. Only a winning conditional update writes EXPIRED, the existing history, and the existing attempt cancellations. Use the same checked database time on those three writes and release within that transaction. A refreshed cutoff after an Admin change can defer a discovered candidate. The keyset cursor ensures it does not monopolise subsequent pages.

**Release and locks.** Centralise terminal marker cleanup inside `releaseRecoverySender`, after the caller's existing business writes and before the no-assignment early return or any sender lock. Clear only `failureCode='WHATSAPP_SENDER_POOL_EXHAUSTED'` on the exact recovery's sequence-one INITIAL attempt, including when the terminal writer already changed its status. Preserve every other failure code and disposition. Then use the recovery's unique conversation to read its original assignment and route/thread IDs without locking new business rows. Lock the original thread, then route, then assignment. Recheck ownership and the captured IDs after waiting. Set `releasedAt` once on the exact conversation/route where it is still NULL. Close the original route only under `NOT EXISTS` an unreleased member and the original thread only under `NOT EXISTS` an open route. Perform these tests in fresh READ COMMITTED statements under their parent locks. Use database statement time for sender timestamps. Concurrent repeat close touches no successor. A missing assignment on a never-admitted recovery still permits the ordinary status, history and attempt changes to commit. Propagate actual DB failures to roll back all terminal effects together. Claims and final permits acquire their own Shop → Conversation → Recovery → Attempt locks and the current policy lock before taking sender locks. Terminal and lazy-expiry transactions operate on one checkout at a time; once they hold sender locks they do not subsequently acquire any shop/conversation/recovery/attempt or policy lock. Complete cross-shop expiry in a separate transaction before restarting allocation; never expire a sibling while holding the recipient allocation lock. Never take the allocation advisory lock during closure.

**Expiry evidence.** Extend the existing expiry unit suite and the BG001 lifecycle integration suite. With independent connections pause a one-day sweep after discovery of a two-day-old checkout, commit Admin's change to 21 days, then continue. Verify current recovery, membership, route and thread remain open, history count stays constant and the sweep advances. Repeat with customer activity committed after discovery and with the exact configured cutoff, including zero days. Show sweep versus allocator expiry creates exactly one history row and one release. Exercise the five writers through their normal entry points, idempotent legacy no-membership returns, the Woo lost-CAS case, rollback on release error, and simultaneous membership attachment versus final release. Check no other basket, merchant, permit or billing history is changed. Regression suites include `tests/unit/services/checkout-recovery-expiry.service.test.ts`, `tests/unit/services/checkout-recovery/order-recovery-correlation.service.test.ts`, `tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts`, `tests/unit/services/woocommerce-recovery/woo-checkout-activity.adapters.test.ts` and `tests/unit/services/woocommerce-recovery/woo-order-reconciliation.service.test.ts`; update their owned transaction mocks wherever affected.

## Pre-credit configuration fault and repair

- In the allocation transaction, try a valid existing checkout membership, then the existing live shop route, before ranking registered, enabled inventory for the authenticated WABA. Only a successful inventory query returning zero eligible rows for a **new** route returns `{kind:'sender-configuration-fault',reason:'no-enabled-sender'}`. One eligible number always wins, even when every shop for the recipient already uses it. Database errors, missing credentials, wrong-account evidence and billing holds cannot take this branch. The active-pool invariant belongs to Admin at enablement, disable-last-number and WABA change. Background handles an observed breach defensively.
- Keep `CheckoutRecovery.status`, `admissionBlockReason` and the original attempt status. For the ordinary unblocked, pre-credit, sequence-1 `INITIAL/PENDING` attempt, CAS only its NULL `failureCode` to the **existing DATABASE-001 value** `WHATSAPP_SENDER_POOL_EXHAUSTED`. This is a durable repair lookup key for an operator fault. First prove exact attempt/recovery/shop/recipient, no original credit or uncertain provider evidence and no other hold. Lookup includes the initial message/idempotency key even when `outboundMessageId` is NULL. Reuse an identical marker without renewing its position on each allocation call. If an unrelated failure code or ambiguous billing/dispatch evidence exists, preserve the original owner and disposition. Commit before emitting the operator-visible configuration error or acknowledging deferred work. No additional attempt, recovery status, credit reservation, provider permit or HTTP call. A successfully claimed or already-owned eligible membership clears only this exact attempt's identical marker in the claim transaction. The provisional membership is now the durable recovery point before billing. For an authorised `CAPACITY_BLOCKED` re-entry return the same configuration fault on zero inventory, leave the existing block/attempt untouched and leave retry ownership to capacity repair.
- In `src/services/whatsapp-sender-pool/waiters.ts` export `dispatchWaitingRecoveries({limit,enqueue}): Promise<void>`. `limit` is the positive configured `recoveryRepairShopBatchSize`. The injected `enqueue({recoveryId,attemptId}): Promise<void>` returns after durable add/verification. Read two separate limited pages ordered by `RecoveryOutreachAttempt.updatedAt ASC, id ASC`. The first uses R07's partial index for sequence-1 PENDING attempts with the exact configuration marker. The second joins unreleased members, open routes and threads, their current RECOVERY conversation and the DETECTED, unblocked recovery's own sequence-1 PENDING attempt. Require no competing failure code, terminal outcome, claimed provider permit or confirmed/unknown dispatch. Include valid pre-permit preparation/retained credit for the original idempotent continuation; avoid redispatch of already-admitted work. Check exact lineage again at worker processing; discovery has no authority to spend. The shared terminal release helper above clears this exact marker even on a recovery with no assignment. For superseded generations, exclude stale owners before LIMIT. Recheck the same facts under the owner locks on execution. Closed or superseded rows cannot displace eligible rows on an eligible page.
- Rotate each selected attempt after **both** durable queue acknowledgement and per-row enqueue failure, never treating failure as success. Use an exact attempt ID and recovery ID, observed `updatedAt`, status, expected marker (or exact still-open provisional membership) CAS. Set `updatedAt = GREATEST(statement_timestamp(), "updatedAt" + interval '1 millisecond')` to advance at the table's millisecond precision; keep the fault marker/provisional state until claim/terminal processing. A zero-row CAS means another writer advanced or closed it. On enqueue failure log the original exception with this row's IDs and attempt the rotation in a separate short transaction. On rotation failure log that exception separately with the same IDs. Proceed with the remaining rows and independent branch, propagating the first original exception after both passes. Never perform Redis I/O under a DB transaction. An unavailable DB for discovery/rotation remains a DB error. Continue the other independent query when possible. Crashes before publication/rotation rediscover the durable candidate, and duplicate acknowledgements converge through the stable job ID.


Stage the result locally and execute the post-commit fault diagnostic/report outside the allocation transaction. For a clean already-marked attempt with zero inventory, preserve the existing marker and still record this detection. A failed marker write or commit emits its actual database error and cannot return a successful parked outcome. For a capacity re-entry with no technical marker, emit the same configuration incident only after eligibility and zero rows are confirmed. A marked attempt is eligible for repair only while current, unblocked, unexpired and owned by the original shop/recipient. Preparing or claiming an already-expired member cannot keep an empty route occupied.

## Server-side diagnostics and error propagation

Own `src/services/whatsapp-sender-pool/diagnostics.ts` and `tests/unit/services/whatsapp-sender-pool/diagnostics.test.ts`. Inject the existing Shared `StructuredLogger`. Use `createLogger` from `@modainteract/moda-interact-shared/logging` and the deployment identity returned by `src/runtime/deployment-environment.ts#resolveDeploymentEnvironmentName` for the default logger. In the recovery process use `serviceName: "moda-recovery-worker"`. Accept the owning process's logger for calls from another worker. Use the existing Shared console/OTel/Loki pipeline. Resolve the service name from the calling process when injected. The helper owns the domain event names and safe fields. Use the existing log sink and incident persistence. Keep this projection local to the sender-pool operations.

Each failure record carries its operation, the failing stage, and the available internal `shopId`, `recoveryId`, `conversationId`, `attemptId`, `threadId` and `routeId`. Preserve the existing job or correlation ID when available and safe. Retry records also carry the transaction-attempt number and retry decision. Use identifiers from the validated internal rows. A phone number, its derived value, checkout URL, checkout token, credentials, raw query/bindings, message body and serialized job payload are outside this field set.

Use the exact prefix `recovery.sender_pool.`. Append the following event name at the boundary that knows why the operation failed.

| Boundary | Event suffix and diagnostic distinction |
| --- | --- |
| Sender preparation, validation of an existing assignment, provisional discard | `assignment.failed`, `assignment.verify_failed`, `preparation.discard_failed` respectively. Record the failed stage (`owner_read`, `inventory_read`, `lock`, `rank`, `membership_write`, `evidence_read`, `transaction_commit` or `discard`). |
| Empty result after a **successful** enabled-inventory read for a new shop route | `configuration.no_enabled_sender` at ERROR with the actual configuration fact and the affected attempt ID. Keep distinct from an inventory query error, credential read error, and an eligible shared assignment. No fabricated upstream exception. |
| Transaction contention | `transaction.retry` at WARN for each actual retry due to a dependency exception, with the original error and the failed operation/stage. The final failure has the operation-specific ERROR event and `retryExhausted=true` only if the budget was exhausted. Expected owner/CAS misses do not generate exception logs. |
| Expiry policy, expiry transition, and membership/route/thread closure | `expiry.policy_failed`, `expiry.transition_failed` and `release.failed`. For release, record the exact stage as `release_member`, `close_route` or `close_thread` and the originating terminal path. Use stage `transaction_commit` when the transaction callback succeeded but its enclosing transaction rejected. If both a statement and a rollback error are observable, log each distinct cause/stage as supplied by the driver. |
| Repair discovery, enqueue and scheduling timestamp write | `repair.scan_failed`, `repair.enqueue_failed` and `repair.rotation_failed`. Carry the branch from which the row was discovered, plus the recovery/attempt when already known. Each distinct row or failing stage gets its own record even when two exception messages are identical. |
| Operator notification, when its delivery/persistence fails | `configuration.alert_failed`. Preserve that failure separately from the original zero-enabled-senders event. The alert failure must never erase the configuration fault or the retryable outreach attempt. |

Set the stage immediately before the fallible operation. Emit the single diagnostic for that failure at the closest owning boundary that has its scope. For an owned transaction emit it after rejection. For an operation called inside the caller's transaction, attribute an observed statement error to the source and let the caller handle a distinct commit failure. A worker or scheduler boundary may record the fact that a job or tick failed. Existing expiry `onError` in `src/entrypoints/recovery.ts` must use a safe projection for that record; do not re-emit unsanitized `error.message` there. Only this existing expiry error hook is in scope here. BG002 owns activation of the repair callback and the new queue job.

Use the existing `initialOutreachDiagnostic` in `src/services/outbound-whatsapp-admission/outbound-provider-failure.service.ts` for the actual exception name, source message, redaction/truncation flags and immediate cause. Project the source `message` explicitly when a driver throws a plain object with a string message. Use the database metadata allowlist in `src/services/whatsapp-provider-status.service.ts#databaseErrorContext` as the reference for Prisma `code`, `clientVersion`, `modelName`, `constraint`, `target` and `field_name`. Preserve PostgreSQL SQLSTATE (five alphanumeric characters) separately from Prisma's P-code when present in driver `code`, Prisma `meta.code` or a nested cause. Preserve a real failure code from BullMQ/Redis where supplied. If Prisma wraps the database error, include the actual diagnostic part of `meta.message` or cause separately with the same text protections; do not reduce a deadlock, failed FK or lost database connection to a generic label. When a driver message includes SQL or a Prisma call dump, expose the database diagnostic clause and safe constraint identifiers. Exclude statement text, bind values, affected-row contents, URL/DSN, secrets and customer text. Apply redaction to every emitted string, including causes. Strip a Prisma call dump or SQL excerpt before projecting the actual driver error clause. For PostgreSQL detail that contains “Key (…)=(…)” or a failing row, retain the named key/constraint and diagnostic wording, omit the offending values. Allowlist stable metadata fields rather than logging a serialized response. Expose useful safe messages in local/test and production. Mark truncation explicitly, propagate the full original exception to its caller. Never serialize raw `meta`, arbitrary nested response bodies or stack objects. In the log projection retain nested Error.cause diagnostics up to four levels, detecting cycles and flagging further depth as truncated. For an AggregateError record each independent member as its own event with the same correlation and its ordinal. Keep the complete original thrown value, including stack and causes, on propagation. The scope here has no WhatsApp HTTP response. Provider transport diagnostics belong to BACKGROUND-002.

**Operator alert after the zero-inventory transaction commits.** In the same diagnostics module use `createOperationalIncidentReporter`, `parseOperationalIncidentOccurrenceV1` and `createPrismaOperationalIncidentPersistence` from `@modainteract/moda-interact-shared/incidents`. Model the wiring on `src/services/recovery-conversation/human-send-operational-incident.service.ts#createHumanSendIncidentSink`. Use a pool-specific producer, not the human-send sink. Write an internal platform incident via the existing persistence and set `notifySupport:false`. Its fixed envelope is `contractVersion='operational-incident.v1'`, `sourceService='background'`, the resolved deployment environment, `category='WHATSAPP_SENDER_POOL'`, `reasonCode='NO_ENABLED_SENDER'`, `resourceKey='messaging.sender.' + occurrenceId`, `shopId=null`, `severity='HIGH'`, `correlationId=attemptId`, and current UTC ISO `occurredAt`. Its truthful local error message is `No enabled WhatsApp sender is configured for the active WhatsApp Business Account.` Use the attempt's internally generated ID. Set `occurrenceId` to the deterministic UUID representation used by `commandOccurrenceId` in the reference: SHA-256 over UTF-8 `whatsapp-sender-pool-no-enabled-v1`, environment, providerAccountId and attemptId separated by single NUL bytes (no terminal NUL); format the first 32 hex characters with nibble 12 forced to `4` and nibble 16 forced to `8`, standard UUID hyphens. Each affected attempt gets a distinct occurrence visible through its correlation ID. Repeated reports from that attempt in the same environment/account deduplicate the dashboard occurrence. Each detection retains its own checkout-scoped diagnostic log. The attempt-scoped resource key gives different attempts separate operator incidents, even for the same WABA. Repeated delivery of the exact same incident keeps one dashboard entry for that occurrence and logs each detection. Database, queue and credential failures have their own events.

The Shared reporter catches its own validation/persistence failures and returns null. Validate the locally constructed envelope before calling it. If validation throws, emit `configuration.alert_failed` with `stage=validate` and the safe original failure. Decorate only the incident persistence port's `transactionForKey`: on a failed durable write emit `configuration.alert_failed` with `stage=persist`, the actual thrown message/cause and the affected attempt; rethrow that same object inside the decorator so the existing reporter can handle it. Do not fabricate another exception when the reporter returns null. The original configuration-fault response and retry evidence survive a failed alert. On a repeated zero-inventory observation call the idempotent reporter again, so an earlier reporting outage can heal. Tests must show one incident occurrence after two detections on one attempt, two separate incident keys and occurrences for two attempts, and that an incident write rejection retains its own log/message alongside the original allocation fault. No new infrastructure, merchant notification or admin surface.

A batch processes its remaining candidates after an individual publication fails. Log each publication failure once with the affected identities; record a secondary rotation/cleanup failure separately with its own original message. After the bounded pass, reject with the first original failure (`throw firstError`), including when it is an arbitrary JS thrown value. Track whether a failure occurred separately from its truthiness. Keep remaining originals attributable via their separate records. Never replace the first failure with the last or a generic batch error. The explicitly best-effort operator incident is separate: log its own original write error and retain the committed typed configuration-fault outcome. For an ordinary method with one failing dependency, rethrow the original caught object. A normal ineligible/expired/already-admitted result is a typed business outcome. Propagate dependency exceptions. Use `assignment.created`, `assignment.reused`, `release.completed` and `preparation.discarded` at DEBUG after commit, with only available internal IDs and disposition. For releases performed within an existing outer writer carry the result through the transaction and log only after that writer’s transaction resolves (use the release result defined above). Emit `assignment.denied` with its precise typed reason for an expected rejected owner, without manufacturing an error. Use `assignment.waba_mismatch` at ERROR for a demonstrated account mismatch and include the affected internal IDs. Neither condition is an empty-inventory incident. For thrown SQL errors, use `stage=read_policy` for policy read, `classify_provider_evidence` for the classifier, and `classify_credit_evidence` for credit. Distinguish `repair.scan_failed` branches as `marked_attempt` and `provisional_member`. A positive result returned by an inner sender helper is never logged as committed until the caller’s outer transaction resolves.

Test with an injected Shared `createLogger({ ..., sink })` in addition to any spy. Assert the serialized record and the thrown object independently. Cover (1) a raw Prisma failure with `P2010`, underlying SQLSTATE and a distinct message in `meta.message`, (2) two transient transactions with different messages followed by terminal failure or success, (3) separate context for two failing rows with identical messages, (4) failure A during enqueue and failure B during rotating A, with two records in order, original A propagated and another candidate still processed, (5) live-policy read failure vs a legitimately extended lifetime, (6) successful inventory query with zero enabled rows vs a thrown inventory read, (7) nested causes, text/URL/credential/recipient redaction and truncation markers in the final sink under test and production, (8) successful fallback sharing an occupied sender emits no pool-fault event. No test should accept a reason code alone when the failing dependency supplied a message.

## Downstream activation contract

BG001 exercises the injected publisher in tests. The running worker starts publishing only when BG002 registers the consumer. BG002 imports these local exports, registers the consumer and enables both sides together. The bindings below are fixed for BG002 and must be reflected in its task before execution.

| Existing or planned Background touchpoint | Binding for BG002 |
| --- | --- |
| `src/services/checkout-recovery/recovery-initiation.service.ts` → `RecoveryInitiationService.continueInitialOutreach` and `handleCheckoutCreated`; `src/services/checkout-recovery/recovery-materialization.service.ts` → `RecoveryMaterializationService.materialize`; `src/services/checkout-recovery.service.ts` → `CheckoutRecoveryService.materializeMaturedCandidate` | On an existing attempt reconcile provider admission first. When the exact clean configuration marker is present, continue normal eligibility and template preparation and run the sender claim before the ordinary retained-credit checks which reject a non-null failure code. Use the same requirement at both retained-credit checkpoints. The full allocation succeeds and clears the marker before existing billing validation/admission resumes. Do not clear a marker to bypass a real credit/permission failure. In the ordinary unmarked path select after approved template preparation and before `billingService.admit`. Preserve the existing materialisation outcome contracts for all other callers; expose the typed configuration-fault outcome through the Background wrappers. |
| `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts` → `RecoveryCapacityResumeProcessorService.resume`; `src/services/checkout-recovery/recovery-capacity-resume-admission-gate.ts` → `createRecoveryCapacityResumeAdmissionGate(...).check` | Ordinary Shopify, Woo and sender-repair calls pass `mode:'initial'`. Only the capacity resume path, after a successful existing gate, may pass `mode:'capacity-resume'` for an actually billing-capacity-blocked attempt. A suppression wakeup alone does not confer this permission. Revalidate exact IDs, DETECTED generation, block reason `RECOVERY_CAPACITY_EXHAUSTED` and attempt status under the allocation locks. |
| `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts` → `WooRecoveryOutreachService.processInitial`; `woo-recovery-composition.ts` → `createWooRecoveryRuntime`; `woo-recovery-orchestrator.service.ts` → `WooRecoveryOrchestratorService.onInitialDispatch` (same directory) | For a permitted Woo initial, resolve the sender between the existing `resolve-conversation` and `reserve-recovery-credit` stages under the existing checkout coordination. Recognise a committed configuration fault before generic deferred-to-BullMQ-error conversion. Preserve Woo outbound's existing test-mode guard. |
| `src/entrypoints/recovery.ts` → existing `RECOVERY_CAPACITY_REPAIR` callback; `src/services/whatsapp-sender-pool/retry-job.ts` (new in BG002); `src/workers/pending-recovery-candidate.worker.ts` → `createPendingRecoveryCandidateWorker` | Keep the existing capacity repair and also invoke the above bounded discovery, logging each failure distinctly. Use existing `PENDING_RECOVERY_CANDIDATE_QUEUE`, job `recovery-sender-pool-retry-v1`, only persisted `{recoveryId,attemptId}`, ID `sender-pool-` plus lowercase SHA-256 of UTF-8 recoveryId, one NUL byte, attemptId. Mirror `WooInitialDispatchQueue.initial` in `src/services/woocommerce-recovery/woo-initial-dispatch.queue.ts` for stable add, validation and retry of retained failed jobs, and close the producer on shutdown. Re-check original recovery/attempt/generation, lifecycle, current recipient and original permit/credit proofs. Dispatch Woo through `onInitialDispatch`; dispatch Shopify through materialisation fenced to the original recovery, attempt and generation. A stale retry cannot open a replacement checkout. BG001 tests inject the queue callback only. |
| `src/services/recovery-conversation/outbound-send-fence.service.ts` → `OutboundSendFenceService.admitFinalSend`; `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts` → `WooInitialSendFenceService.admitFinalSend` | BG002 passes phase `initial` for initial outreach or `ongoing` for later recovery messages, uses the returned sender pair on the final permit, and preserves the original account/number on callbacks. Do not wire these callers in BG001. |

## Work Items

- [ ] Implement the exact allocation/verification/repair contracts and scoped evidence-classifier extraction.
- [ ] Wire the five terminal writers, live expiry checks, technical marker cleanup and scoped diagnostic boundaries.
- [ ] Add the specified tests, complete validation and publish both mirrored task branches for review.

## Acceptance Criteria

- [ ] Integrate the accepted DATABASE-001 pin, regenerate the client, and implement only the BG001 write touchpoints above. Preserve the established class entry points and provider/consumer ownership. Build the tests through the allocator, existing terminal services and repair callback, with no network-provider dependency.
- [ ] With recipients X and Y and senders S1/S2/S3, reproduce these persisted states. X/A1 and X/A2 share one merchant route even with S2 idle. X/B1 uses an idle S2 when available. With only S1 enabled X/A and X/B both use S1 in separate routes. Y can use S1 independently. An unused S3 beats an occupied sender. With no free number rank one shop with three baskets ahead of two shops with one basket each, then prove priority and C collation tie-breaks. Retain the sender on exact replay. No attempt has a technical fault marker in any positive scenario.
- [ ] Drain S1 and prove the existing X/A route still admits an independently eligible A2. Inject zero enabled senders for a new X/B, confirm DETECTED, the original attempt/marker, the operator diagnostic, zero debit and zero provider calls. Restore S1 and resume that same attempt on the next eligible repair pass, clear the marker atomically, and prove no new attempt/credit in BG001. A missing credential, wrong WABA, inventory query exception, conflict and confirmed provider outcome each have their own observable disposition. An already capacity-blocked attempt retains its original billing gate and reason.
- [ ] Exercise concurrent A1/A2 creation, separate-shop claims, drain versus claim, attach versus release and two simultaneous final-member releases with independent PostgreSQL connections and deterministic barriers. Inspect rows, original IDs and counts. Released members/closed routes cannot attach to a successor; new admission after last-shop closure gets a new thread ID immediately. Deleting one merchant can leave an empty parent or a surviving peer. Prove cleanup repairs only the former. Preserve all prior receipts and credit ownership.
- [ ] Cover valid zero days, exact cutoff equality, a live activity extension, a policy extension between discovery and expiry, concurrently scheduled/lazy expiry, every terminal writer, and a release write failure that rolls back the transition. A future external-activity timestamp is not evidence of eligible outreach. With an otherwise active recovery, use the existing lifetime predicate to refuse assignment without expiring it solely for having a future timestamp.
- [ ] Capture pauses after provisional claim, marker clear and retained credit before a permit. A retained provisional member is rediscovered after restart. Discard cannot delete an active rival's claim, committed credit or provider history. Without sufficient exclusive proof return retained. Confirm preserved continuation when a provider permit exists even for a null attempt.outboundMessageId. S1 cannot authorise checkout B solely because A uses it.
- [ ] With batch size one, fail publication for oldest A on repeated attempts while B remains eligible. B is offered on the next pass after a successful rotation and A stays retryable. Exercise each discovery branch, failed/ambiguous publication, stale rotation CAS, crash before/after enqueue and a distinct error from the second branch. After restoration revalidate the original recovery and attempt; stale work has no effect on a successor. Verify all independent errors are visible and the first original rejection is propagated.
- [ ] Satisfy the serialized-log and operator-incident tests above. Include two separate errors in one repair pass with differing original causes and two rows failing with identical text. Assert per-row IDs and separate events, redaction of sensitive literals, original source message where safe, actual underlying error code, and exact thrown-object identity. Assert separate dashboard incidents and occurrences for two different zero-inventory attempts and idempotent dashboard reporting of a retry of the same occurrence.

## Validation

From the launcher-resolved Background worktree run the following commands using the parent Node version and existing lockfile. The target new files are `tests/unit/services/whatsapp-sender-pool/assignment.test.ts`, `tests/unit/services/whatsapp-sender-pool/waiters.test.ts`, `tests/unit/services/whatsapp-sender-pool/diagnostics.test.ts` and `tests/integration/whatsapp-sender-pool-lifecycle.integration.test.ts`. Use the existing checkout, attempt, credit and public test fixtures, plus deterministic transaction barriers; keep the integration scenarios modular. Integration fixture data and external connection targets must be disposable.

```bash
npm ci
npm run prisma:generate
npx --no-install vitest run \
  tests/unit/services/whatsapp-sender-pool \
  tests/unit/services/checkout-recovery-expiry.service.test.ts \
  tests/unit/services/checkout-recovery/order-recovery-correlation.service.test.ts \
  tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts \
  tests/unit/services/woocommerce-recovery/woo-checkout-activity.adapters.test.ts \
  tests/unit/services/woocommerce-recovery/woo-order-reconciliation.service.test.ts \
  tests/unit/services/outbound-whatsapp-admission/initial-outreach-admission.test.ts \
  tests/unit/services/outbound-whatsapp-admission/outbound-admission-reservation.service.test.ts
npm run build
npm run lint
git diff --check
git diff --cached --check
```

The architect explicitly authorises this integration command for BG001 in the claimed worktree under `docs/agent-validation-execution-policy.md`. Use the existing Node runner and the PG17/pgvector + Redis harness which owns startup and teardown. Run the following once per implementation attempt and record the individual results. No Meta traffic, live data, merchant notification or hosted deployment.

```bash
node scripts/test-integration.mjs \
  tests/integration/whatsapp-sender-pool-lifecycle.integration.test.ts \
  tests/integration/initial-outreach-admission-resume.integration.test.ts \
  tests/integration/initial-outreach-admission-races.integration.test.ts \
  tests/integration/woo-order-reconciliation.integration.test.ts \
  tests/integration/woo-checkout-activity.integration.test.ts \
  tests/integration/woo-recovery-composed-services.integration.test.ts
```

## Dependencies and Implementation Notes

Defined but not materialised. The execution dependency is accepted and integrated ARCH-076-DATABASE-001. Applying the Markdown handoff does not satisfy that dependency. Once available, use `/moda-task ARCH-076-BACKGROUND-001`. If the accepted pin is missing, required model/index names differ, or an incompatible active writer cannot be covered by the specified transaction, return the actual path/symbol, SQLSTATE or command failure and conflicting invariant to the architect. Keep genuine environment/tool failures distinct from a code failure. Do not implement another task to bypass a dependency.

In the Completion Report record both launcher-resolved worktree paths, mirrored branches and start/final SHAs, submodule SHA, edited files, test commands and exit codes, captured per-stage failure evidence using synthetic IDs, database concurrency proofs, fixture image and teardown. If the integration command could not run, mark it pending and record the exact blocker. Return the implementation and parent report for architect review; integration into main is developer-owned. BG002 is the next execution dependency. Use the downstream activation contract in this handoff when revising BG002, before that task is claimed.

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

## Reconciliation provenance — 15 November 2026

Reconciled from the later local sender-pool revision formerly labelled ARCH-069. The completed chronological-input architecture and its ARCH-069 task identities are unchanged. ARCH-076 was already reserved for the earlier sender-pool proposal; this revision updates that proposal in place, retaining its Git history. These are definition changes, not implementation or deployment evidence. All execution remains Pending until compatibility review and dependency promotion.
