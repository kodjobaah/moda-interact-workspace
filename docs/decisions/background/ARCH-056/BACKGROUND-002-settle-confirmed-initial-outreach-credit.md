---
id: ARCH-056-BACKGROUND-002
architecture_id: ARCH-056
title: Reuse and settle the exact initial recovery credit
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: copilot
claimed_at: 2026-11-04T04:33:03Z
attempt: 4
depends_on:
- ARCH-028-BACKGROUND-004
- ARCH-028-BACKGROUND-009
enables:
- ARCH-056-BACKGROUND-004
- ARCH-056-SYSTEM-TEST-001
created: '2026-11-03'
updated: 2026-11-04
---

# ARCH-056-BACKGROUND-002: Reuse and settle the exact initial recovery credit

## Architecture

Architecture: `ARCH-056`. Parent: `docs/architecture/ARCH-056-background-persistence-and-recovery-progress.md`. Coordinator: `moda_architect`.

Definition revision: 4. Materialised in the canonical task worktrees. Attempt 2 implementation `79b8d5b` and report `650778eb2` are published. The 2026-11-04 architect review returns Changes Requested for strict orphan-message classification and incomplete preservation validation. The five-file fixture-only amendment below resolves the execution allowlist blocker. Attempt 2 is preserved and its claim is cleared; the next launcher claim starts Attempt 3.

## Objective

Give initial recovery orchestration one billing-owned contract for reusing an existing pre-permit reservation and one contract for settling an already confirmed message. Both must identify the exact original credit owner. Only a verified committed credit authorizes the consumer to continue confirmed-send finalization.

## Context

The phase-3 assessment identifies two related billing touchpoints. `RecoveryReservationLifecycleService.commit` discards the source owner's outcome, although a commit requested against `AMBIGUOUS` or `RELEASED` replays that status without committing. Separately, a restarted initial attempt cannot reconstruct its source safely by calling current `admit`: paid keys include the billing period, so a later admission can select a different source. Existing exact-source compensation lookup correctly rejects multiple candidates, including released history; its safety boundary must remain intact.

BS-04 is a smaller edit in the same paid owner: its successful Shopify commit reads and validates the plan meter handle, then reads it again inside the same transaction. Reuse that validated value. BS-05 is bounded here by explicit holds; this task does not establish a new rule for choosing between historical source candidates.

`ARCH-028-BACKGROUND-013` remains Blocked. A pre-HTTP permit, timeout or missing response is not newly authorized billing evidence. This task accepts only durable positive message confirmation for settlement and never converts an uncertain `AMBIGUOUS` source into a charge.

## Scope

One repository: `moda-interact-background`. Paths below are relative to that repository. The matching JSON manifest is the machine-readable allowlist; it contains no additional implementation scope.

| Production path | Operation | Purpose |
|---|---|---|
| `src/services/recovery-billing.service.ts` | Modify | Add the two public ports and re-export their types; preserve existing call signatures |
| `src/services/recovery-billing/recovery-billing.types.ts` | Modify | Define the exact public input/result unions below |
| `src/services/recovery-billing/recovery-reservation-lifecycle.service.ts` | Modify | Require a positive committed outcome and own final legacy-commit diagnostics |
| `src/services/recovery-billing/initial-outreach-credit.service.ts` | Create | Own transaction, evidence classification, exact-owner dispatch, retry and emitted diagnostics for the two ports |
| `src/services/recovery-billing/initial-outreach-credit-evidence.ts` | Create | Read and validate tenant, initial-attempt, message, usage and credit-owner evidence |
| `src/services/recovery-delivery-compensation/lineage.ts` | Modify narrowly | Extract the existing exact source lookup for reuse; preserve compensation's missing-source rejection |
| `src/services/recovery-delivery-compensation/reconcile.service.ts` | Modify narrowly | Lock the owned Shop before the message for the correction event's implicit FK; own final/retry compensation diagnostics |
| `src/services/whatsapp-provider-status.service.ts` | Modify narrowly | Order Shop before status/usage writes; own truthful status and after-commit diagnostics while preserving status policy |
| `src/services/free-recovery-reservation.service.ts` | Modify narrowly | Add a same-transaction commit wrapper around the existing ledger owner |
| `src/services/purchased-recovery-reservation.service.ts` | Modify narrowly | Add the same wrapper; preserve purchase-lot/refund behavior |
| `src/services/promotional-recovery-reservation.service.ts` | Modify narrowly | Add the same wrapper and a read-only retained-source eligibility wrapper |
| `src/services/paid-included-recovery-reservation.service.ts` | Modify narrowly | Add the same wrapper, a typed existing-period rejection, and remove BS-04's duplicate read |

Own the unit and integration paths listed under Validation. Existing finalization, Shopify initiation, Woo orchestration and outbound fence files belong to `ARCH-056-BACKGROUND-004` and `ARCH-056-BACKGROUND-003`, respectively; they are read-only dependencies here. No file has two implementation owners.

### Attempt 2 architect amendment — fixture-only scope (2026-11-04)

This amendment supersedes the previous read-only restriction for **only** these five existing required regression modules:

- `tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
- `tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts`
- `tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts`
- `tests/integration/paid-included-recovery-reservation.concurrency.integration.test.ts`
- `tests/integration/same-plan-billing-period-rollover.concurrency.integration.test.ts`

Authorize fixture/schema-alignment edits within these files: remove the retired BillingPlan soft/hard-limit and terminal-slot fields, seed their replacement policy/feature data through existing canonical schema where the tested behavior requires it, and retain the original reservation, accounting, concurrency, replay and rollover assertions. Run every original case; do not skip tests, weaken assertions, add schema fields, alter production policy, or fabricate passed evidence. These are tests_modify paths owned by BG002 in the matching execution map. Any needed shared fixture or production change outside this explicit list still requires separate disposition.

`tests/integration/recovery-human-provider-status.integration.test.ts` stays read-only and remains in the full required command. It passed the independent Attempt 2 rerun; preserve the implementer's earlier null-message failure as historical evidence. If it recurs, capture the failed command/dispatch stage and compare baseline/candidate prerequisites before proposing a narrowly scoped fix. A passing rerun does not establish the cause of the earlier failure, and no waiver of its assertions is granted.

## Out of Scope

No schema/migration, Shared publication, dependency or package-script change; no new queue, provider call, timeout billing policy, source substitution, reservation reactivation, counter/ledger implementation, historical-period settlement rule, broader failed-message compensation, provider-status policy change, Recovery/Support mutation or new schema-backed source binding. No changes to accepted tasks, the Blocked ARCH-028 task, or any `_index.md`.

This task deliberately holds nonunique and historical unresolved lineage. Do not claim that BS-05, the whole billing assessment, or uncertain-send settlement has been resolved.

## Requirements

### 1. Prove identity before selecting credit

Validate the supplied Shop, recovery and sequence-one `INITIAL` attempt through stored relations. A supplied message must be `OUTBOUND`, `AUTOMATION`, associated with that recovery's conversation, with no merchant command at all and no sequence-two claim. Any merchant command attached to the automated message/initial attempt is a conflict, including a same-Shop command. Verify any nonnull conversation Shop and all source-owner Shops. A linked attempt must link this message; an unlinked attempt requires the exact existing automated-message usage identity `recovery-outreach:<attemptId>` and the message as its source ID. Reject duplicate, missing or cross-Shop usage and conflicting reverse links. Preserve existing recipient evidence; do not reconstruct the intended recipient from a currently edited customer phone or locate a message by phone/time. The schema has no independent message recipient snapshot; do not claim one has been proved by this task.

Extract `findExactRecoveryReservationSource(tx, shopId, outreachAttemptId): Promise<RecoverySource | null>` from the existing lineage module. Search the same complete logical candidate set: Shared's `createRecoveryIdempotencyKey(shopId, "recovery-outreach:<attemptId>")`, plus correctly formed `paid-included:<billingPeriodId>:<logicalSource>` candidates. Zero returns null for the new pre-message path; more than one throws the existing lineage error. Existing `resolveExactRecoverySource` must continue to reject zero when its previous contract required one. Never filter away a historical `RELEASED` row, pick the newest candidate, or limit by current billing period to manufacture uniqueness.

Validate quantity one, source-key format, mutually consistent owner FKs, the exact counter kind and Shop, purchased lot ownership, and promotional grant ownership. Paid counter/period/key must agree. Reuse existing `readExactAutomatedUsage`, `resolveExactRecoverySource` and `readCommittedRecoveryUsage` where their contracts apply; do not copy the compensation ledger or weaken its predicate.

### 2. Classify and settle confirmed initial messages

Inside one Serializable transaction, read a routing-only message/Conversation/Shop pointer, validate it against the input, lock the exact owned `commerce.Shop` `FOR KEY SHARE`, then lock `whatsapp.ConversationMessage` by exact ID `FOR UPDATE`. Reread the message and its ownership; require the same message/provider/Conversation/Shop identity and then validate all attempt/source evidence. Never trust the preliminary status, lock a newly discovered different Shop after the message, or mutate a source if the ownership changed. The Shop lock orders the UsageEvent insert's immediate FK lock before the message and does not impose a new billing eligibility gate.

Confirmation means durable status `SENT`, `DELIVERED` or `READ`, nonnull actual `sentAt`, and no contradictory failure evidence. A missing/PENDING/FAILED message yields `message-not-confirmed`; inconsistent ownership yields `lineage-conflict`. A permit timestamp or provider ID alone is insufficient. Settlement does not require the attempt to still have a particular scheduler status, because confirmed replay may follow progress already recorded by its consumer.

| Exact reservation state/evidence | Result and mutation boundary |
|---|---|
| `RESERVED`, positive message, coherent owner | Commit through that owner's same-transaction wrapper; verify resulting reservation and original positive UsageEvent before returning `settled/committed` |
| `COMMITTED`, exact valid positive event, no correction/compensation | Return `settled/already-committed`; preserve the original event/provider/period, even after a plan or period change |
| `AMBIGUOUS` | `held/reservation-ambiguous`; no state change |
| `RELEASED` | `held/reservation-released`; no reactivation, fresh reserve or charge |
| Any compensation field or exact correction evidence | `held/reservation-compensated`; never overwrite or recharge |
| Paid `RESERVED` with original period no longer current/open | `held/paid-period-not-current`; do not choose a new period or credit kind |
| Missing/nonunique/wrong-owner/wrong-event lineage | `held/lineage-conflict`; no guessed source |
| Owner does not positively return the expected committed state | `held/settlement-not-committed`; no successful finalization permission |

Validate the committed event using the existing positive-usage helper: exact reservation event ID, Shop, recovery metric, positive quantity, source type, source ID/key, idempotency key, allowed original provider, and absence of correction. Additionally verify paid event billing-period identity against the original counter, and provider against the durable Shop platform. A `COMMITTED` label or nonnull event ID alone is insufficient. An invalid original event must not be replaced.

For paid `RESERVED`, retain the existing current/open-period rule. Add an optional structured `reason: "PERIOD_NOT_CURRENT_OPEN"` to `PaidIncludedRecoveryReservationError` at the existing commit guard, preserving its message/class and compatibility with other call sites. Map only that exact reason to the period hold. Do not parse error messages or map every billing error to a harmless hold. Meter/configuration/database errors preserve their original exception.

Every held result leaves all ledger/counter/lot/grant/refund rows unchanged. If classification fails after an owner mutation or positive-event insert, throw a narrow internal hold signal to abort the transaction and translate it only outside `$transaction`; returning a held object from a callback after writes is forbidden. A failed final verification must roll back the credit and event together.

### 3. Revalidate retained credit before any new provider permit

This method is read-only and transaction-consistent. With a message ID, lock/reread that message and require `PENDING`, null `providerDispatchKey`, null `providerDispatchAdmittedAt`, null `providerDispatchControlRevision`, no provider ID, no send/delivery/read/failure timestamp, no conflicting attempt link and the exact usage identity. A control revision alone is partial permit evidence and must hold. Restriction-revision metadata belongs to MerchantConversationSendCommand, not ConversationMessage; every merchant command is already forbidden for this automated identity. Reject any post-permit or receipt-bearing state as `message-not-pre-permit`. The initial attempt must be unsent and must not contradict the canonical pre-permit identity; no attempt-status reset is performed here.

Explicit null means the caller found no message, and the service must independently verify no stored attempt link, no sent evidence and no canonical automated-message usage/source message. An orphan, competing usage or discoverable existing message is `lineage-conflict`. Only a verified unsent initial identity with no message, no usage/link/permit evidence and zero matching reservation candidates yields `absent`. A PENDING message with no credit source never yields `absent`.

An existing source is reusable only if it is the single exact original source, `RESERVED`, unexpired (`expiresAt === null || expiresAt > now`), with no committed-event, release or compensation contradiction. Otherwise return the explicit state/expiry/lineage hold. The method never reserves, reactivates, releases, rebinds, consumes or changes quota.

Resolve current eligibility through transaction-bound existing `EffectiveBillingPolicyResolver` and, on its exact `NO_CONTRACT` branch, `PostContractRecoveryPolicyResolver`. Keep existing feature/new-recoveries-pause and subscription eligibility gates. Map recognized domain denials to the declared held reasons; other resolver/infrastructure errors propagate unchanged. Preserve the existing Woo frozen/post-coverage durable-credit exception; it does not authorize paid-included reuse. Final outbound policy/consent/pause checks remain with the final fence.

| Stored source | Reconstructed admission and eligibility |
|---|---|
| Lifetime-free counter | `kind: "lifetime-free"`, same key and reservation, current accepted effective or verified post-contract durable policy; no second allowance check for an already reserved unit |
| Purchased counter and exact lot | `kind: "purchased"`, same key/lot/reservation, current accepted effective or verified post-contract durable policy; preserve owner-supported ACTIVE/WITHDRAWN retained-reservation accounting and require its reserved unit still exists |
| Promotional grant | `kind: "promotional"`, same selected grant/key/reservation, current effective policy and the owner's read-only current selection/campaign/scope/date eligibility; mismatch holds |
| Paid period counter | `kind: "paid"`, same period/key/reservation, current paid plan with nonfrozen subscription, current policy phase `ACTIVE` (`policy.billingPeriod.phase`) and persisted period status `OPEN` (`BillingPeriod.status`), plus valid provider coverage under existing policy; old/draining/expired period holds |

Physical source ownership is authoritative. Mapping the lifetime-free counter to the existing `lifetime-free` admission label does not change its source. Post-contract free/purchased reuse requires the existing verified-ended-subscription rule; no new entitlement is inferred. Do not call `admit`, `reserve` or `revalidateBeforeProvider` to implement retained-source reuse: the latter can release and switch sources.

This result is not a provider permit. `BACKGROUND-003`'s final fence freshly proves the exact reservation under a lock before granting a permit; a pause/release/ambiguity between read-only revalidation and the fence cannot be ignored.

### 4. Preserve lock order and error semantics

The confirmed transaction acquires **Shop FOR KEY SHARE -> message FOR UPDATE -> existing owner lot/grant/counter/reservation operations**. Read Conversation/attempt evidence without requesting their row locks. Do not add a reservation `FOR UPDATE` before its owner counter; existing owners mutate their counter before the reservation. Never request a different Shop or Conversation/attempt row lock after the message lock. The retained-source method is read-only and does not insert an FK-bearing UsageEvent.

The coordinated final fence order in `BACKGROUND-003` is **Shop FOR UPDATE -> Conversation -> initial attempt -> message FOR UPDATE -> exact UsageReservation FOR SHARE -> permit CAS**. It locks no billing counter and requests no parent lock afterward. Existing Woo's credit-before-message order is corrected by that owner. BG002 and BG003 are independently executable; the shared agreement uses existing fields, not an unimplemented cross-task service.

The positive and negative UsageEvent inserts both acquire implicit Shop `KEY SHARE` through the immediate FK. Existing compensation currently starts with a message lock, and provider-status convergence can update a message before inserting delivered usage. Either could otherwise oppose a Shop-first fence. Make two bounded locking-only corrections in this task:

1. In `RecoveryDeliveryCompensationService.reconcileLocked`, read an exact provider-message/message-ID ownership pointer, lock that Shop `FOR KEY SHARE`, lock the message `FOR UPDATE`, reread and require unchanged ownership. Preserve the existing FAILED/131026 predicate, source resolution, release/correction mutations, outcome values and retry. Unknown/nonterminal messages keep their existing outcome; contradictory ownership fails closed. Never acquire a replacement Shop lock after the message.
2. At the provider-status transaction entry, resolve the exact provider-message/Shop pointer without mutation, lock its Shop `FOR KEY SHARE`, then reread and validate the same message/provider/Conversation/Shop identity before the existing status CAS, command/attempt convergence and delivered UsageEvent upsert. Preserve unknown/unowned handling, all existing status/131026/usage policy, original errors and bounded retries. A pointer mismatch is an explicit lineage rejection or existing retryable conflict, with no mutation and no late different-Shop acquisition. Do not rewrite attempt locking or introduce new status states. Compensation/reachability/notification remain after the status transaction commits.

This also covers a reachable initial crash window: the message is already SENT while its attempt remains PENDING, so a stale final-fence caller can reach that message while a DELIVERED status transaction inserts its first usage event. Tests must include the actual FK wait, not only inspect explicit SQL locks. Selected lock-graph claims cover these fence/receipt/settlement/status/compensation interactions; no claim about every period, cancellation or other application writer is authorized.

If failure/status convergence wins, settlement must reread and hold; if settlement wins, a later eligible 131026 correction remains owned by the existing compensation service. Never settle from an unlocked stale success read after a correlated failure has won.

Use the existing bounded reservation-conflict retry policy (three attempts; recognized concurrency/P2002/P2034 conflicts), with no provider operation inside a retry. Unexpected errors and the final exhausted error must rethrow the identical original exception object, preserving its application `message`, `stack`, `cause` and any code/meta already present. A typed hold produced from a caught domain/lineage exception must retain that originating exception for the local diagnostic before returning the hold. Do not substitute the hold's reason code for its original message. Expected absence, pause and state classifications that did not originate from an exception must not acquire a fabricated Error or provider diagnostic.

Apply requirement 6 below to emitted diagnostics. Passing `{error}` to a mock or preserving an object in memory is not proof that its original message and selected diagnostic fields appear in the actual Shared output. No local generic logger, generic serializer, cause-graph walker or alternative transport is authorized.

### 5. Remove the paid owner's duplicate meter read

Within `PaidIncludedRecoveryReservationService.commitInTransaction`, retain the existing transaction-bound paid-plan/meter validation and use that selected `shopifyUsageEventHandle` in the new UsageEvent. Remove `readPaidUsageEventHandle` once its duplicate call is gone. Preserve provider, source key, occurredAt, idempotency, reporting state and transaction isolation. The narrow target is one fewer explicit subscription read for successful Shopify RESERVED commitment; Woo has no extra meter lookup to remove. Do not claim the entire new settlement flow makes fewer queries.

### 6. Prove emitted diagnostics at the selected operation boundaries

Use the installed `@modainteract/moda-interact-shared/logging` `createLogger` and the parent architecture's common original-message and redaction contract. Add optional injected Shared logger dependencies only at the existing/new service owners below, preserving their existing constructor callers. Logging remains best-effort; a sink failure cannot change a return value, transaction result, retry decision or the original thrown exception.

The following ownership is fixed. A material source failure has one detailed service-owned diagnostic. Downstream records may add job/stage correlation, but must not blindly repeat full source diagnostics at every layer. Existing generic worker failure records are context, not a substitute for these selected direct-service guarantees.

| Owner and operation | Stable event | Required behavior |
|---|---|---|
| `InitialOutreachCreditService.settleConfirmedInitialOutreach` / `revalidateExistingInitialOutreach` | `recovery.initial_outreach_credit.failed` | Emit `error` once for an unexpected final failure or exhausted transaction retry, after its transaction has rolled back; rethrow the same object |
| The same two operations, semantic result | `recovery.initial_outreach_credit.held` | Emit `warn` with the exact held reason and stage; when a caught policy/lineage/period error produced the hold, include its original safe name/message and known cause rather than just the reason. With no originating exception, omit exception/provider fields |
| The same operations, recognized conflict followed by another attempt | `recovery.initial_outreach_credit.retry` | Emit `warn` with actual attempt, configured limit, stage and recognized conflict reason/code; preserve an actually supplied original message. The exhausted attempt belongs to `.failed`, not another retry event |
| Legacy `RecoveryReservationLifecycleService.commit` | `recovery.credit_commit.failed` | Own final errors of the compatibility successful-commit path, including `RecoveryCreditNotCommittedError`; log expected source identity and observed outcome/status when known, then rethrow the same object. This path is separate from the new coordinator's direct same-transaction owner calls |
| `RecoveryDeliveryCompensationService.withRetry`, used by both `reconcile` and `reconcileMessage` | `recovery.delivery_compensation.failed` / `recovery.delivery_compensation.retry` | Own original final/retried compensation errors for asynchronous and synchronous callers. Log after rollback, with the exact input identity and last attempted stage; keep existing outcome and retry semantics |
| Provider-status SQL transaction and its existing bounded retry | `whatsapp.provider_status.failed` / `whatsapp.provider_status.retry` | Own original status-transaction failures with `stage: "status_transaction"`; exhaustion is a final error, not successful application. Keep the actual provider-message ID and incoming normalized status |
| Provider-status continuation after a committed status transaction | `whatsapp.provider_status.downstream_failed` | Record `statusTransactionCommitted: true` and exact stage. For `compensation`, reference `sourceDiagnosticEvent: "recovery.delivery_compensation.failed"` and the same provider-message ID; the compensation owner already emits the original error, so this is context only. For failure/positive reachability or merchant notification, this existing status caller owns the original error diagnostic because those selected calls have no lower service failure-log owner. Rethrow unchanged in every case |

Use fixed stage values local to the operation. For initial credit: `identity`, `policy`, `source_lookup`, `source_commit`, `committed_usage_verification`. For compensation: `identity`, `source_lookup`, `source_release`, `source_correction`, `outbound_usage_cleanup`. For post-status work: `compensation`, `failure_reachability`, `positive_reachability`, `merchant_notification`. Keep stage and correlation state local to the current invocation/attempt, never in shared mutable fields on a singleton service or logger. Update the diagnostic stage immediately before the operation it describes. A transaction commit failure remains attached to its enclosing operation/last attempted stage; do not claim a later stage executed. Reset per-attempt diagnostic context before retrying so an earlier failed attempt cannot misattribute a later failure to stale Shop/source evidence.

Record available bounded correlation fields: `operation`, `stage`, `shopId`, `recoveryId`, `outreachAttemptId`, `outboundMessageId`, `providerMessageId`, `reservationId`, `sourceKey`, `sourceKind`, `attempt`, `maxAttempts`, `retryExhausted`, and the exact declared held `reason` or internal `reasonCode`. Include only facts actually known at that boundary. Do not guess missing IDs, label a provider code as a Prisma code, or print the entire admission/policy/message/Prisma argument object. A lower source commit whose internal retry count is not exposed must not claim a guessed attempt count.

Keep the original direct error message in emitted `data.error.message`, apart from the common documented redaction/truncation. The existing Shared Error serializer carries direct name/message only. If a known caught/constructed cause is relevant, pass its safe name/message explicitly as an ordinary bounded `cause` field; do not assume nesting an Error carries its own causes. Preserve the full original exception/cause object in application propagation. This task does not introduce automatic stack logging or promise that arbitrary cause graphs are emitted. The existing Meta adapter remains the original provider-response/SDK diagnostic owner; billing must not manufacture a Meta response from an internal error or replicate full provider payloads.

For database failures, separately copy only actually supplied, allowlisted diagnostics into the ordinary structured `databaseError` field (`code`, `clientVersion`, and the permitted `meta` keys below). Permit a genuine Prisma `code`, `clientVersion`, and `meta.modelName`, `meta.target`, `meta.constraint`, `meta.field_name` when they are bounded schema identifiers or arrays of such identifiers; permit an actually supplied five-character SQLSTATE such as `meta.code`. Preserve their value semantics. Omit unsupported values and absent fields. Never spread `error.meta`, a Prisma invocation, SQL text/parameters, driver response, connection URL, headers, or arbitrary nested SDK objects. No metadata field replaces the original safe message. Internal concurrency errors with an empty message must still expose operation, stage, an internal concurrency reason and actual retry counts; the empty original message is not permission to invent an upstream explanation.

Move the existing `whatsapp.provider_status.applied` emission to after the status transaction and its retry wrapper have successfully returned. Keep its event name/outcome semantics, but do not emit it for a transaction that rolls back or whose commit fails. A later compensation/reachability/notification failure may follow this committed-status event and must clearly carry `statusTransactionCommitted: true`; it cannot relabel committed status persistence as rolled back or acknowledge the whole provider job as successful.

Every exception-to-hold translation, the legacy nonpositive commit guard, exhausted retry, and selected after-commit failure must be covered by an emitted-record test below. Do not suppress a material original diagnostic because the caller will receive `held` or because SQL status persistence already committed.


The purchased reserve P2002-to-empty-conflict conversion and existing empty internal conflict classes are recorded baseline limitations, not authorized reserve/retry-helper changes. Preserve an actually supplied original message; when it is empty, report explicit internal reason, stage and real retry state without inventing provider wording. The four source services remain ledger owners and do not each gain an identical catch-and-log wrapper. No new production/test path, Shared release, generic sanitizer, logger, cause-graph walker or transport is authorized. The selected WhatsApp worker diagnostic boundary belongs to BG001; this task does not edit that worker.

## Work Items

- [x] Add exact input/result contracts and a thin facade collaborator, preserving existing constructor/caller compatibility and test injection.
- [x] Extract the existing unique source lookup without changing compensation's refusal behavior.
- [x] Add same-transaction owner wrappers, promotional retained-source eligibility and the typed paid-period guard.
- [x] Implement durable confirmed settlement with verified positive results, rollback-on-hold and Shop-key-share-before-message locking.
- [x] Apply the same early owned-Shop lock to existing provider-status/compensation transaction entries, retaining all their existing policy and after-commit behavior.
- [x] Finish read-only retained-source revalidation: the null-message path holds discoverable orphan automated messages and attempt-linked merchant commands rather than returning absent. Exact-source and reserved-before-outbound cases remain covered.
- [x] Make the existing successful-commit facade reject noncommitted owner outcomes.
- [x] Reuse the paid plan's already validated meter handle.
- [x] Implement the fixed selected failure/hold/retry diagnostic owners, stages and correlation fields, preserving original exception identity and existing accounting/status behavior.
- [x] Emit provider-status `applied` only after successful SQL commit; distinguish later committed-status continuation failures.
- [x] Add actual installed Shared-sink assertions for original direct messages, known causes, allowlisted database metadata, typed holds, exhausted retries, missing upstream fields, redaction and logging-sink failure isolation; do not certify this with logger-call mocks.
- [x] Add and execute the bounded unit/PostgreSQL matrix below; report contracts to BG004 and preserve BG003's lock-order agreement.

## Interfaces / Contracts

Define and export these types from `recovery-billing.types.ts`, and re-export them from `recovery-billing.service.ts`:

```ts
export type InitialOutreachCreditIdentity = {
  shopId: string;
  recoveryId: string;
  outreachAttemptId: string;
};

export type ConfirmedInitialOutreachCreditInput = InitialOutreachCreditIdentity & {
  outboundMessageId: string;
};

export type ExistingInitialOutreachCreditInput = InitialOutreachCreditIdentity & {
  outboundMessageId: string | null;
};

export type ConfirmedInitialOutreachSettlement =
  | {
      kind: "settled";
      disposition: "committed" | "already-committed";
      sourceKind: "free" | "paid" | "purchased" | "promotional";
      sourceKey: string;
      reservationId: string;
      committedUsageEventId: string;
      outboundMessageId: string;
      sentAt: Date;
    }
  | {
      kind: "held";
      reason:
        | "message-not-confirmed"
        | "lineage-conflict"
        | "reservation-ambiguous"
        | "reservation-released"
        | "reservation-compensated"
        | "paid-period-not-current"
        | "settlement-not-committed";
      reservationId?: string;
      sourceKey?: string;
    };

export type ExistingInitialOutreachCredit =
  | {
      kind: "admitted";
      admission: RecoveryBillingAdmission;
      reservationId: string;
    }
  | { kind: "absent" }
  | {
      kind: "held";
      reason:
        | "message-not-pre-permit"
        | "lineage-conflict"
        | "reservation-not-reserved"
        | "reservation-expired"
        | "source-policy-mismatch"
        | "paused"
        | "feature-unavailable"
        | "contract-required"
        | "subscription-frozen"
        | "paid-period-not-current";
      reservationId?: string;
      sourceKey?: string;
    };
```

The `RecoveryBillingService` methods are:

```ts
settleConfirmedInitialOutreach(
  input: ConfirmedInitialOutreachCreditInput,
): Promise<ConfirmedInitialOutreachSettlement>;

revalidateExistingInitialOutreach(
  input: ExistingInitialOutreachCreditInput,
): Promise<ExistingInitialOutreachCredit>;
```

Inputs contain durable identities, not a caller-supplied admission, current source choice, billable timestamp or asserted success. `sentAt` in a successful result comes from the locked durable message. Neither method calls a provider.

Preserve `commitSuccessfulInitiation`'s existing input and `Promise<void>` signature for the remaining callers, including sequence two. Strengthen its lifecycle implementation: resolve only when the owner returns `committed` or `already-committed`, with `status=COMMITTED`, matching Shop/source/quantity and a nonnull committed-event ID. Throw an exported `RecoveryCreditNotCommittedError` for a nonpositive or internally inconsistent outcome; its fields must retain the attempted source identity and actual outcome, without marking accounting complete. This compatibility guard is not a substitute for the stronger new durable-message proof. Do not change provider-failure disposition or the shared reservation transition table.

### Source owner wrappers

Each of the four reservation services adds `commitInExistingTransaction(transaction: Prisma.TransactionClient, input)`, returning its existing owner outcome union. It validates quantity and delegates to the existing private `commitInTransaction`; it does not create a transaction, add another retry loop, or duplicate ledger mutations. Free and purchased use their current commit input types. Paid uses its current required Shop/source, optional quantity and `occurredAt` commit input.

Promotional's same-transaction commit input is `Omit<PromotionalRecoveryReservationInput, "planId"> & { planId?: string }`; narrow the private commit parameter accordingly. The current commit body uses the stored grant and needs no fabricated/current plan ID. Keep public `commit` compatible.

Promotional also adds the read-only `isReservedSourceEligibleInExistingTransaction(transaction, input: { shopId: string; reservationId: string; sourceKey: string; now: Date }): Promise<boolean>`. Reuse its existing `findUsableGrant` policy/selection/campaign predicates, narrowing that private helper's input to the Shop/time fields it actually uses. Require the same reserved reservation/grant and at least its reserved quantity. Do not require an additional unreserved credit, reserve another unit, change the merchant selection, or consume a grant. This avoids a second promotional eligibility policy in the new coordinator.

## Dependencies

- `ARCH-028-BACKGROUND-004` — Complete exact generic source/usage/131026 compensation contract.
- `ARCH-028-BACKGROUND-009` — Complete purchased source/refund compensation contract.

`ARCH-028-BACKGROUND-013` is an explicit preserved policy boundary, not a prerequisite that this task silently unblocks. No Database task is justified for these proved-or-held outcomes; schema expansion would require a separately reviewed requirement and owner.

## Enables

- `ARCH-056-BACKGROUND-004` consumes both ports and migrates initial Shopify/Woo callers. It must call settlement before Support/status/follow-up finalization; it calls retained-source revalidation before new outbound reservation or resume, and calls fresh `admit` only after `absent`.
- `ARCH-056-SYSTEM-TEST-001` proves integrated worker behavior after all its prerequisites are Complete.

BG002 does not migrate orchestration files. BG004 must not duplicate billing source queries. Legacy sequence-two callers retain their API and gain the positive-result guard; their recovery/unknown-outcome policy is not redesigned.

## Acceptance Criteria

- [x] Four source owners settle a positively confirmed initial message at most once through their existing accounting transactions.
- [x] Exact COMMITTED replay validates the original positive event and remains safe after period/policy change; stale RESERVED paid periods remain held.
- [x] AMBIGUOUS, RELEASED, compensated, missing or nonunique source evidence never becomes a new charge or a successful finalization result.
- [x] Pre-permit restart returns the same reservation/source admission without accounting mutation; null-message interruption, orphan automated-message evidence, and attempt-linked command evidence are covered; only verified source absence authorizes fresh admission.
- [x] Every held/error outcome preserves ledger state or rolls back all changes; failures retain their original diagnostics.
- [x] Confirmed settlement, provider failure/131026 compensation, final permit and shared-counter races obey the documented lock order and positive accounting invariants. BG002 PostgreSQL coverage now exercises the real settlement service against the accepted final fence in both permit-first/PENDING-hold and confirmed-settlement-first/refused-repeat-permit orders, using independent clients and asserting accounting and provider-call state.
- [x] BS-04's duplicate Shopify meter read is removed without report/provider changes; BS-05 and Blocked BG013 remain accurately bounded.
- [x] No edits escape the declared ownership allowlist or change schema, provider, queue, Support or recovery-status behavior directly.

- [x] Every selected material technical failure and exception-derived hold has its original safe direct message in an actual emitted Shared record at the declared service owner, with precise stage and available original identities.
- [x] Final retry failure rethrows the same exception, logs the actual retry state, and cannot emit false successful status application; after-commit failures identify which state already committed.
- [x] Known cause and allowlisted Prisma/SQLSTATE diagnostics are emitted explicitly when present; missing data produces no invented provider/database facts. Stack/cause-graph completeness is not claimed from Shared's direct Error serializer.
- [x] Captured emitted records pass the common sensitive-data/redaction/truncation assertions. Logging sink failure leaves accounting, holds, retries and original thrown exceptions unchanged.
- [x] Source-owned detailed diagnostics and downstream stage context follow the owner table; tests do not rely on an unrelated worker callback to compensate for a missing direct-service diagnostic.

## Validation

Modify these existing unit files only as required by the new contracts and owner wrappers:

- `tests/unit/services/recovery-billing.service.test.ts`
- `tests/unit/services/recovery-billing/recovery-reservation-lifecycle.service.test.ts`
- `tests/unit/services/recovery-billing/recovery-billing.test-support.ts`
- `tests/unit/services/free-recovery-reservation.service.test.ts`
- `tests/unit/services/purchased-recovery-reservation.service.test.ts`
- `tests/unit/services/promotional-recovery-reservation.service.test.ts`
- `tests/unit/services/paid-included-recovery-reservation.service.test.ts`
- `tests/unit/services/whatsapp-provider-status.service.test.ts`
- `tests/integration/arch028-recovery-delivery-compensation.integration.test.ts`

Create:

- `tests/unit/services/recovery-billing/initial-outreach-credit.service.test.ts`
- `tests/unit/services/recovery-billing/initial-outreach-credit-evidence.test.ts`
- `tests/unit/services/recovery-billing/initial-outreach-credit.test-support.ts`
- `tests/integration/arch056-initial-outreach-credit.integration.test.ts`
- `tests/integration/arch056-initial-outreach-credit-races.integration.test.ts`
- `tests/integration/arch056-initial-outreach-parent-fk.integration.test.ts`
- `tests/integration/fixtures/arch056-initial-outreach-credit.fixture.ts`

Required proof matrix:

1. Each source: new confirmed commitment, exact committed replay, two concurrent callers and changed current policy. Assert one original positive UsageEvent and exact original owner deltas/provider/reporting identity, not only the returned result.
2. AMBIGUOUS/RELEASED and every compensation/correction contradiction: hold with unchanged reservation, counter/lot/grant/refund, UsageEvent count and outbound usage. Wrong Shop/sequence/message/source/quantity and multiple candidates, including RELEASED history, fail closed.
3. Paid current RESERVED commits; historical RESERVED holds; historical COMMITTED with exact original event replays. Missing/wrong positive event or paid period/provider mismatch holds. Assert no current-period substitute reservation/event.
4. Null-message no-source returns absent; null-message exact retained RESERVED and PENDING-message exact retained RESERVED return the same source; PENDING-message no-source, orphan usage, competing link, expired/nonreserved source, any permit or receipt evidence hold. Snapshot durable rows before/after each read-only case.
5. Current pause/feature/contract/frozen cases, verified post-contract free/purchased cases, Woo durable-credit exceptions and promotional current-selection/date/scope mismatch use declared outcomes. Already reserved quantity must not require another available credit. Retained withdrawn purchase behavior must follow the existing owner/refund rules.
6. Legacy successful commit rejects all owner outcomes other than valid committed/already-committed, including undefined mocks, wrong Shop/source/status and missing committed event. Use realistic reservation outcome fixtures; no default fake success.
7. Inject failure after an owner counter/lot/grant update, after positive-event insert and at final positive verification. Assert full rollback; a genuine injected exception is the same object received by the caller. A recognized bounded race retries and never duplicates accounting. Alongside rollback and `rejectedError === injectedError`, assert the actual Shared-sink record, its original safe message and relevant stage. A `toHaveBeenCalledWith({error})` assertion on a mocked logger alone does not meet this gate.
8. Use two independent PostgreSQL clients and explicit test barriers for settlement versus actual provider-status/131026 compensation and two distinct confirmed messages sharing a counter. Assert both legal winner orders. The FK-sensitive test must exercise real positive/correction/delivered UsageEvent inserts with the canonical immediate Shop FK: hold the existing fence's Shop UPDATE before its message request, and show the accounting/status path waits for Shop KEY SHARE before taking the message; reverse the winner order as well. Include SENT message/PENDING attempt with a DELIVERED event, exact initial 131026 convergence, human-status regression and changed/vanished pointer cases. For final-permit ordering, use honest state predicates: PENDING permit winner makes settlement hold; confirmed-settlement winner makes a fence refuse another provider request. Do not fabricate simultaneous successful eligibility for incompatible message states. Full actual-fence integration is also checked in BG003/terminal tests.
9. Shopify paid commit performs one plan/meter read, preserving its handle/PENDING report event; Woo keeps NOT_APPLICABLE/null Shopify fields and adds no meter read. Wrapper tests prove no nested `$transaction` or wrapper-local retry.

10. **Emitted logging contract.** Import the actual installed Shared `createLogger`, inject a logger with a capturing `sink`, and serialize/parse and inspect the emitted sanitized records; do not mock the serializer or replace the shared package with a locally reimplemented test logger. Use distinct benign sentinels for an original database error, an exception-derived lineage/period hold, a known nested cause, final retry failure, and each after-commit failure. Require the exact safe original message in `data.error.message` at the declared detailed owner, correct event/level/service/environment/stage/correlation, and unchanged exception identity or specified held result. Use a Prisma-shaped real error supported by the installed client for `code`/allowlisted `meta`, and assert that arbitrary metadata/query arguments are absent. Test a pure predicate-based hold separately: it must contain no fabricated exception/provider fields. Test an internal empty-message conflict separately: explicit internal reason, stage and actual exhaustion counts remain visible without inventing a provider message. Capture both the real compensation owner's failure and the status caller's context-only after-commit record, correlated by exact message identity. A compensation stub alone cannot prove the lower owner emitted. For status SQL failure—including commit-time failure—assert no `whatsapp.provider_status.applied` event; for later compensation/reachability/notification failure assert committed status remains and `statusTransactionCommitted` is true. Run the common secret/PII/redaction/truncation fixtures against the actual emitted record, and use a throwing Shared sink to prove unchanged return/throw behavior.

Place these assertions only in already owned files:

- `tests/unit/services/recovery-billing/initial-outreach-credit.service.test.ts` and its already declared test-support file: credit failed/held/retry records, policy/lineage mapping, real Shared sink, known cause and metadata, redaction and sink failure.
- `tests/unit/services/recovery-billing/recovery-reservation-lifecycle.service.test.ts`: legacy nonpositive guard and final owner-error event, same-error identity, no duplicate event from the new coordinator path.
- `tests/unit/services/whatsapp-provider-status.service.test.ts`: transaction versus after-commit stages, actual Shared output, committed-state flag, no rolled-back `applied`, unchanged final exceptions, and no fabricated upstream diagnostics.
- `tests/integration/arch028-recovery-delivery-compensation.integration.test.ts`: actual compensation failure/retry ownership and original source/rollback proof.
- `tests/integration/arch056-initial-outreach-credit-races.integration.test.ts`: correlate the real compensation failure record with the real status caller's context-only record after status commit. Use test-only fault injection in these integration files; do not add production failpoints.
- The existing four source-owner unit files: retain/extend same-transaction wrapper exception-identity assertions; no duplicate log-owner wrapper is required in every source service.

The BG002 unit/integration/build/lint commands below execute these files. No additional runner or dependency is needed. Record the actual installed Shared version/package resolution with the test result; source inspection of a sibling Shared checkout is supporting evidence, not proof of the runtime package used by Background.

Run from the launcher-resolved implementation worktree after existing locked dependencies are available:

```bash
npm run build
npm run test -- tests/unit/services/recovery-billing.service.test.ts tests/unit/services/recovery-billing tests/unit/services/free-recovery-reservation.service.test.ts tests/unit/services/purchased-recovery-reservation.service.test.ts tests/unit/services/promotional-recovery-reservation.service.test.ts tests/unit/services/paid-included-recovery-reservation.service.test.ts tests/unit/services/whatsapp-provider-status.service.test.ts tests/unit/services/recovery-reservation/reservation-lifecycle.test.ts
npm run test:integration -- tests/integration/arch056-initial-outreach-credit.integration.test.ts tests/integration/arch056-initial-outreach-credit-races.integration.test.ts tests/integration/arch056-initial-outreach-parent-fk.integration.test.ts tests/integration/arch028-recovery-delivery-compensation.integration.test.ts tests/integration/recovery-human-provider-status.integration.test.ts tests/integration/free-recovery-reservation.concurrency.integration.test.ts tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts tests/integration/paid-included-recovery-reservation.concurrency.integration.test.ts tests/integration/same-plan-billing-period-rollover.concurrency.integration.test.ts
npx --no-install eslint src/services/recovery-billing.service.ts src/services/recovery-billing/recovery-billing.types.ts src/services/recovery-billing/recovery-reservation-lifecycle.service.ts src/services/recovery-billing/initial-outreach-credit.service.ts src/services/recovery-billing/initial-outreach-credit-evidence.ts src/services/recovery-delivery-compensation/lineage.ts src/services/recovery-delivery-compensation/reconcile.service.ts src/services/whatsapp-provider-status.service.ts src/services/free-recovery-reservation.service.ts src/services/purchased-recovery-reservation.service.ts src/services/promotional-recovery-reservation.service.ts src/services/paid-included-recovery-reservation.service.ts tests/unit/services/recovery-billing.service.test.ts tests/unit/services/recovery-billing/recovery-reservation-lifecycle.service.test.ts tests/unit/services/recovery-billing/recovery-billing.test-support.ts tests/unit/services/recovery-billing/initial-outreach-credit.service.test.ts tests/unit/services/recovery-billing/initial-outreach-credit-evidence.test.ts tests/unit/services/recovery-billing/initial-outreach-credit.test-support.ts tests/unit/services/free-recovery-reservation.service.test.ts tests/unit/services/purchased-recovery-reservation.service.test.ts tests/unit/services/promotional-recovery-reservation.service.test.ts tests/unit/services/paid-included-recovery-reservation.service.test.ts tests/unit/services/whatsapp-provider-status.service.test.ts tests/integration/arch028-recovery-delivery-compensation.integration.test.ts tests/integration/arch056-initial-outreach-credit.integration.test.ts tests/integration/arch056-initial-outreach-credit-races.integration.test.ts tests/integration/arch056-initial-outreach-parent-fk.integration.test.ts tests/integration/fixtures/arch056-initial-outreach-credit.fixture.ts tests/integration/free-recovery-reservation.concurrency.integration.test.ts tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts tests/integration/paid-included-recovery-reservation.concurrency.integration.test.ts tests/integration/same-plan-billing-period-rollover.concurrency.integration.test.ts
git diff --check
```

The existing `scripts/test-integration.mjs` provisions disposable PostgreSQL/Redis through Shared and deploys migrations; no new runner, `db push`, live database or external provider is required. Inspect no-test/skipped output and preserve cleanup failures alongside the original test error. Do not copy existing fixture cleanup that silently catches every exception. Record migration source, real source revisions, commands, before/after database assertions and actual results. These are future implementation obligations, not tests already executed by the architect.

## Implementation Notes

Use the parent architecture's common execution, error/logging, worktree and completion-evidence requirements. Keep the facade thin, put evidence reads and transaction orchestration in the two focused modules, and retain existing accounting in its four owners. New production modules target at most 200 physical lines and must not exceed 300; existing larger owner files receive only the specified wrapper/guard/read-reuse edits. If a further split is necessary to meet that rule, return the precise additional path for architectural review rather than silently creating unowned production modules.

### Stop Condition

Stop and report a scoped architecture question if an exact source cannot be represented without a schema change, a required claim would depend on post-permit uncertainty or new historical settlement policy, or the implementation requires editing another task's production files. Do not widen the eligibility predicate to make a test pass. On passing the scoped acceptance/validation gates, report evidence, publish the normal task mirrors, set `status: review`, return to `moda_architect` and stop; do not execute the enabled tasks.

## Completion Report

This section belongs to the implementing repository agent. No implementation is recorded by this definition.

### Status

Attempt 4's scoped implementation and validation are complete under the launcher claim. The orphan-message fix, attempt-linked command evidence check, five authorized fixture corrections, architect-approved ARCH-028 fixture isolation, and required final-permit/settlement interaction tests are present on the implementation branch. The exact required PostgreSQL matrix passes all 69 tests in its declared order. The architect accepted Attempt 4 and the task is complete; no enabled task was executed or claimed in this run.

### Attempt 1 Files Changed

Implementation repository: `moda-interact-background`; task branch `task/ARCH-056-BACKGROUND-002`; commit `00cfac4` (`Implement exact initial outreach credit settlement`), pushed to origin.

- `src/services/free-recovery-reservation.service.ts`
- `src/services/paid-included-recovery-reservation.service.ts`
- `src/services/promotional-recovery-reservation.service.ts`
- `src/services/purchased-recovery-reservation.service.ts`
- `src/services/recovery-billing.service.ts`
- `src/services/recovery-billing/recovery-billing.types.ts`
- `src/services/recovery-billing/recovery-reservation-lifecycle.service.ts`
- `src/services/recovery-billing/initial-outreach-credit.service.ts`
- `src/services/recovery-billing/initial-outreach-credit-evidence.ts`
- `src/services/recovery-delivery-compensation/lineage.ts`
- `src/services/recovery-delivery-compensation/reconcile.service.ts`
- `src/services/whatsapp-provider-status.service.ts`
- `tests/integration/arch028-recovery-delivery-compensation.integration.test.ts`
- `tests/integration/arch056-initial-outreach-credit.integration.test.ts`
- `tests/integration/arch056-initial-outreach-credit-races.integration.test.ts`
- `tests/integration/arch056-initial-outreach-parent-fk.integration.test.ts`
- `tests/integration/fixtures/arch056-initial-outreach-credit.fixture.ts`
- `tests/unit/services/free-recovery-reservation.service.test.ts`
- `tests/unit/services/paid-included-recovery-reservation.service.test.ts`
- `tests/unit/services/promotional-recovery-reservation.service.test.ts`
- `tests/unit/services/purchased-recovery-reservation.service.test.ts`
- `tests/unit/services/recovery-billing/initial-outreach-credit-evidence.test.ts`
- `tests/unit/services/recovery-billing/initial-outreach-credit.service.test.ts`
- `tests/unit/services/recovery-billing/initial-outreach-credit.test-support.ts`
- `tests/unit/services/recovery-billing/recovery-billing.test-support.ts`
- `tests/unit/services/recovery-billing/recovery-reservation-lifecycle.service.test.ts`
- `tests/unit/services/whatsapp-provider-status.service.test.ts`

### Files Changed

Attempt 2 changes these implementation-owned files:

- `src/services/recovery-billing/initial-outreach-credit-evidence.ts`
- `tests/integration/arch056-initial-outreach-credit.integration.test.ts`
- `tests/unit/services/recovery-billing/initial-outreach-credit-evidence.test.ts`
- `tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
- `tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts`
- `tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts`
- `tests/integration/paid-included-recovery-reservation.concurrency.integration.test.ts`
- `tests/integration/same-plan-billing-period-rollover.concurrency.integration.test.ts`

### Attempt 1 Work Completed

Implemented the billing facade/types, exact message/attempt/source evidence, same-transaction source-owner wrappers, confirmed settlement, read-only retained-source revalidation, legacy commit outcome guard, paid-meter read reuse, and bounded retry/hold/failure diagnostics. Extracted the existing exact-source lookup and applied Shop `FOR KEY SHARE` before message `FOR UPDATE` in settlement, compensation, and provider-status paths. Provider-status `applied` is emitted after successful transaction completion; post-commit failures carry committed-state context.

Added owner unit coverage, initial Shared logger sink tests, and PostgreSQL cases for the source commits/replays, shared-counter race and Shop-parent FK wait.

### Work Completed

Corrected the retained pre-permit PostgreSQL fixture to clear both message and attempt `sentAt`. Added actual Shared-sink assertions for direct errors, one-level known cause, allowlisted Prisma metadata and SQLSTATE, pure holds without fabricated upstream fields, retry exhaustion, secret redaction, truncation, and sink failure. Added status transaction versus post-commit log assertions, including compensation, reachability and notification stages.

Added three disposable-PostgreSQL rollback scenarios: unique-event conflict after owner counter mutation, injected owner exception after positive-event insertion with identity preservation, and failed final positive verification. Added an integration flow through the real compensation owner and provider-status service; it proves source-owner rollback and correlates the detailed owner record with the status caller's context-only record by provider message ID.

Fixed null-message absence classification so any outbound automated message in the supplied recovery conversation, including an unlinked pending message, produces `held/lineage-conflict` rather than authorizing fresh admission. Added unit and real PostgreSQL regression coverage. Corrected the five amended billing integration fixtures by seeding outbound limits and terminal reserved slots on `PlatformBillingPolicy`, retaining their original test cases and assertions.

### Attempt 1 Validation Results

Launcher evidence:

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-056-BACKGROUND-002
parent branch: task/ARCH-056-BACKGROUND-002
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-056-BACKGROUND-002
implementation branch: task/ARCH-056-BACKGROUND-002
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: already-current
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current
git submodule sync --recursive: passed
git submodule update --init --recursive: passed
recorded implementation base: afac7c3766d92fb14beff669232c1b01c2ed0be0
recorded database submodule: 5907b4572ea9efc2a24c07e4c3bd3e107db4260b
implementation commit: 00cfac4
```

Agent-executed checks:

- `npm run build` — passed; Prisma Client 6.19.3 generated and TypeScript build completed.
- `npx --no-install tsc --noEmit` — passed after final integration fixture/test additions.
- Task-scoped unit command from this task's Validation section — passed, 16 files and 266 tests.
- Exact task-scoped `npx --no-install eslint ...` command from Validation — passed.
- `git diff --check` — passed.
- `npm ls @modainteract/moda-interact-shared --depth=0` — installed package `@modainteract/moda-interact-shared@3.0.0`.

Broader unit check:

- `npm run test:unit` — 3,692 passed, 7 failed (337 passed test files, 4 failed test files). Failures were three `whatsapp.worker.test.ts` enqueue assertions, one `whatsapp-inbound-processing.service.test.ts` enqueue assertion, one ARCH-049 frozen-image reason assertion, and two observability-startup timeouts. These are outside this task's changed paths; no applicable baseline ID was identified during this attempt.

PostgreSQL checks already executed:

- The initial ARCH-056 settlement/race/parent-FK command passed 3 files and 7 tests. It ran before the latest retained-source and state-hold cases were added; those new cases remain unexecuted.
- `tests/integration/arch028-recovery-delivery-compensation.integration.test.ts` passed 28 tests.
- `tests/integration/recovery-human-provider-status.integration.test.ts` passed 1 test.
- The four existing reservation-owner concurrency files reported 11 failures across 4 files. Each failed during fixture creation because stale tests pass removed `BillingPlan.defaultOutboundSoftLimit` and `defaultOutboundHardLimit` fields to Prisma. The provider-status suite included in that command passed 1 test. No production/schema/test-fixture repair was made because those legacy owner fixtures are outside this task's authorized paths.
- No cleanup failure was shown in the captured summaries. The full required matrix, including same-plan rollover and the latest added integration cases, has not been run by the agent.

Developer validation required (the full disposable PostgreSQL/Redis integration command, per `docs/agent-validation-execution-policy.md`):

```bash
npm run test:integration -- tests/integration/arch056-initial-outreach-credit.integration.test.ts tests/integration/arch056-initial-outreach-credit-races.integration.test.ts tests/integration/arch056-initial-outreach-parent-fk.integration.test.ts tests/integration/arch028-recovery-delivery-compensation.integration.test.ts tests/integration/recovery-human-provider-status.integration.test.ts tests/integration/free-recovery-reservation.concurrency.integration.test.ts tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts tests/integration/paid-included-recovery-reservation.concurrency.integration.test.ts tests/integration/same-plan-billing-period-rollover.concurrency.integration.test.ts
```

Expected success condition: all task-owned ARCH-056 and affected lock-order tests pass; the pre-existing owner fixture/schema drift must be resolved or dispositioned before claiming the full matrix passed. The new four-source revalidation, eight ambiguity/release holds, and stale paid-period integration cases require execution against the disposable database.

### Attempt 1 Deviations

The new coordinator is 235 physical lines: above the 200-line target but below the hard 300-line ceiling. No unowned production module was introduced to split it. The exact full PostgreSQL matrix is deferred to developer validation; the legacy owner concurrency fixtures currently fail before exercising production behavior. The full unit suite also has seven unrelated failures listed above. Emitted-record coverage is not yet complete for all specified cause/redaction, mutation-then-rollback, and selected after-commit failure scenarios.

### Attempt 1 Assumptions

The prepared launcher packet is the source for physical worktree, synchronization, claim and recursive-submodule evidence. The installed Shared package version was confirmed from the implementation worktree, not a sibling checkout.

### Attempt 1 Unresolved Issues

Developer execution of the full integration command remains required. Resolve/disposition the four stale owner concurrency fixture failures. Add or complete actual Shared-sink assertions for known causes, redaction/truncation, typed period/policy holds, rollback after owner mutation/event insertion, selected after-commit failures, and compensation/status diagnostic correlation. The latest added retained-source and state-hold PostgreSQL cases are typechecked but unexecuted. Do not claim BG-013, BS-05, historical source selection, or uncertain-send settlement is resolved.

### Architectural Concerns

No schema, package/dependency, Shared publication, cross-repository, provider, queue, Support or recovery-status policy change was made. The remaining items are evidence/validation gaps; no enabled task was started.

### Validation Results

- `npm run build` — passed; Prisma Client 6.19.3 generated and TypeScript build completed.
- Required BG002 unit matrix — passed, 16 files and 271 tests.
- Focused null-message evidence unit regression — passed, 1 file and 5 tests.
- ESLint on all eight Attempt 2 changed TypeScript files and `git diff --check` — passed.
- `git diff --check` — passed.
- Shared runtime resolution — `npm ls @modainteract/moda-interact-shared --depth=0` reports `@modainteract/moda-interact-shared@3.0.0`.
- `tests/integration/arch056-initial-outreach-credit.integration.test.ts` — passed, 1 file and 22 tests, including the orphan-message PostgreSQL regression.
- The five explicitly authorized reservation/rollover fixture suites — passed, 5 files and all 12 original tests.
- Full matrix command: `node scripts/test-integration.mjs` with the ten integration paths listed in this task's Validation section.
- Full required PostgreSQL matrix — 10 files, 65 passed and 1 failed. The only failure is the read-only `recovery-human-provider-status.integration.test.ts`: `outboundMessageId` is null when the test loads the command's message at line 43, before its provider-status assertions; the emulator reported zero messages. The same test passed when rerun alone (1 file, 1 test). This establishes a combined-run-dependent failure, not its root cause. No cleanup failure was reported.
- Broader `npm run test:unit` — 341 files, 3,710 passed and 2 failed (3,712 tests). The unrelated failures are an inbound-processing enqueue expectation and an ARCH-049 frozen-image reason expectation; neither is in the changed files.

The five fixture files above were modified only under the explicit Attempt 2 amendment. `recovery-human-provider-status.integration.test.ts` remains read-only and unchanged. Do not weaken its assertions or infer a cause from the isolated pass; retain the combined-run failure for architect disposition.

### Deviations

All edits remain within the implementation-owned paths and the five-file amendment. The complete validation gate is not satisfied because the required PostgreSQL command still fails in the read-only HUMAN-status test, and the broader unit suite has two unrelated failures. Acceptance checklist items remain unchecked; targeted passes do not replace the required full matrix.

### Assumptions

Attempt 2 uses the launcher-resolved implementation worktree; task metadata is `ready` with no active claim. Runtime logging assertions use the installed Shared package version 3.0.0. Changes remain uncommitted and unpushed.

### Unresolved Issues

The combined required integration run still fails at the read-only HUMAN-status test despite its isolated pass; the cause is undetermined and no change is authorized there. The broad unit suite also has two unrelated failures. Do not mark this task complete or unblock `ARCH-056-BACKGROUND-004` or `ARCH-056-SYSTEM-TEST-001` on this evidence. Preserve the existing BS-05, ARCH-028-BACKGROUND-013 and uncertain-send policy boundaries.

### Attempt 2 Architectural Concerns

No schema, package/dependency, Shared publication, cross-repository, provider, queue, Support or recovery-status policy changes were made. The only production edit adds explicit one-level cause context to the BG002-owned settlement/revalidation diagnostics.

### Attempt 3 Validation and Disposition

Launcher claim: Attempt 3, task `in_progress`, executor `copilot`, claimed at `2026-11-04T03:04:51Z`. Dependency checks passed for ARCH-028-BACKGROUND-004 and ARCH-028-BACKGROUND-009. The parent claim commit is `d07754e63876fb2220b16f41480f4f6139700c16`; parent and implementation branches are `task/ARCH-056-BACKGROUND-002`. Recursive database submodule initialization passed at `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`.

Attempt 3 worktree and synchronization evidence:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-056-BACKGROUND-002`, branch `task/ARCH-056-BACKGROUND-002`, HEAD and `origin/task/ARCH-056-BACKGROUND-002` at `d07754e63876fb2220b16f41480f4f6139700c16`. The launcher incorporated the already-current `origin/main`; the Attempt 3 claim was committed and pushed. The only parent-worktree modification is this completion report, not yet committed or pushed.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-056-BACKGROUND-002`, branch `task/ARCH-056-BACKGROUND-002`, HEAD `a5953b9def12b91b79b02b5874b686fcec5cbeaf`; implementation origin task ref at `79b8d5bc5cf5ad4090ee0dc0b06246e10489ca78`. At final validation the implementation branch is six commits ahead of its origin task ref and has nine unstaged, uncommitted implementation-file modifications. No implementation commit or push was made in Attempt 3. Shared workspace and implementation checkouts were not switched or mutated by launcher preparation.
- Recursive Database submodule: initialized and synchronized at `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`.
- Final scope is the nine changed implementation files listed in the implementation worktree status and this one report file in the parent worktree. No temporary diagnostic test/import remains.

Validation on the implementation worktree:

- `npm run build` — passed; Prisma Client 6.19.3 generated and TypeScript build completed.
- Required BG002 unit matrix — 16 files, 271 tests passed.
- Full declared task-scoped ESLint command, including the five authorized fixture files — passed.
- `git diff --check` — passed.
- `tests/integration/arch056-initial-outreach-credit.integration.test.ts` — 22/22 passed after removal of the temporary diagnostic test.
- Initial Attempt 3 required ten-file PostgreSQL/Redis run — 10 files, 65 passed and 1 failed at the unchanged read-only `recovery-human-provider-status.integration.test.ts:43`; both outbound message IDs were null and the emulator recorded zero sends.
- Following the first authorized teardown cleanup, a default-parallel run passed the HUMAN test but exposed one foreign command from the new BG002 regression itself (66 passed, 1 failed). That regression now inserts accepted intent and transitions it to `CANCELLED` with its attempt link in the same transaction, before it can enter the global claim queue.
- Final exact required ten-file command in declared order with default Vitest scheduling — 10 files, 67/67 passed.
- The exact required ten-file command with `--no-file-parallelism` in declared order — 10 files, 66/66 passed before the command regression was added. The earlier HUMAN-first serial 66/66 run was diagnostic only.
- `arch028-recovery-delivery-compensation.integration.test.ts` followed by the unchanged HUMAN-status test with `--no-file-parallelism` — 2 files, 29/29 passed after cleanup.
- Required BG002 unit matrix — 16 files, 272/272 passed after the command-evidence change.
- Focused evidence unit tests — 6/6 passed; focused BG002 PostgreSQL integration file — 23/23 passed, including orphan-message and attempt-linked command holds.
- `npm run build` and scoped ESLint over all nine changed implementation TypeScript files — passed after cleanup.
- `git diff --check` — passed in both implementation and parent report worktrees.

Safe diagnostic evidence was collected with temporary tests in the BG002-owned integration module; all probes and their imports were removed before final validation. In isolation, a fixture analogue claimed its two own command IDs and both commands reached `SENT` with one dispatch attempt, provider dispatch keys, outbound message IDs, and two provider requests. After earlier matrix suites, the claim call returned two different command IDs; its own commands remained `ACCEPTED`, `failureCode` null, dispatch-attempt count zero, with no dispatch key, outbound ID, or provider request. A safe candidate snapshot identified the two earliest foreign candidates as `ACCEPTED` rows with `arch028-` Shop IDs, created by the HUMAN branches of `arch028-recovery-delivery-compensation.integration.test.ts`. That fixture previously left accepted commands claimable after teardown. The architect approved making these synthetic lineage commands terminal within the same setup transaction that inserts and links them, while retaining conditional cleanup. A subsequent 66/67 default-parallel run exposed a second contaminant: the new BG002 command-evidence regression had itself created an accepted command. Its fixture now inserts, links and cancels that synthetic command in one transaction. This preserves realistic accepted-intent creation and command lineage without exposing test-only accepted rows to another file's global claim. `processClaim` returning normally was not treated as proof of a send.

The initial matrix failure was caused by stale accepted HUMAN commands left by the ARCH-028 integration fixture. Following explicit architect approval, `arch028-recovery-delivery-compensation.integration.test.ts` creates each synthetic command as accepted intent and transitions it to `CANCELLED` with its outbound link inside one transaction, so it is non-claimable as soon as it becomes visible. Teardown also cancels only tracked rows that still belong to that fixture's Shop, remain `ACCEPTED`, have no provider dispatch key, and have no lease token or expiry. The BG002 command-evidence regression likewise makes its synthetic linked command terminal atomically. These changes preserve lineage and existing assertions while preventing test-only rows from being consumed by the global due-command query. No edits were made to HUMAN production code, `recovery-human-provider-status.integration.test.ts`, its shared fixture, or the integration runner. Temporary diagnostics are absent from the final implementation diff.

**Architect disposition:** the architect approved the ARCH-028 fixture-only isolation correction. Its final guidance was to insert synthetic commands as accepted intent and cancel/link them atomically before commit, retaining conditional teardown cleanup. The implementation also added the architect-requested null-message attempt-command check and unit/PostgreSQL regressions; the command regression's own fixture is made terminal atomically to avoid polluting the global claim queue. The final required matrix, build, 272-test unit matrix, scoped lint, and diff checks pass. Task acceptance is pending architect re-review; keep ARCH-056-BACKGROUND-004 and ARCH-056-SYSTEM-TEST-001 gated until explicit acceptance. Implementation changes remain uncommitted and unpushed.

### Attempt 4 Validation and Disposition

Launcher claim: Attempt 4, task `in_progress`, executor `copilot`, claimed at `2026-11-04T04:33:03Z`. Dependency checks passed for ARCH-028-BACKGROUND-004 and ARCH-028-BACKGROUND-009. The parent claim commit is `60b9427632a1bc4f08472362b274acb2c5eb1a32`; recursive database submodule synchronization/initialization passed at `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`.

Attempt 4 worktree evidence:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-056-BACKGROUND-002`, branch `task/ARCH-056-BACKGROUND-002`, launcher claim at `60b9427632a1bc4f08472362b274acb2c5eb1a32`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-056-BACKGROUND-002`, branch `task/ARCH-056-BACKGROUND-002`, base `a5953b9def12b91b79b02b5874b686fcec5cbeaf`.
- Database submodule: initialized and synchronized at `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`.
- No production code or BG003-owned files changed in Attempt 4. The BG002-owned race integration module now contains the two requested final-permit/settlement winner cases.

The permit-first case admits through the real Shopify `OutboundSendFenceService`, then invokes the real `InitialOutreachCreditService` while the message truthfully remains PENDING. Settlement returns `held/message-not-confirmed`; reservation, counter, and recovery-usage rows remain unchanged, and the provider mock is untouched. The confirmed-settlement-first case sends through the existing Shopify resume path, verifies durable SENT/provider identity, settles through the real BG002 service on an independent client, then confirms a later real fence call is suppressed and resume cannot produce a second provider call. The reservation/counter and positive recovery UsageEvent assertions verify exact settlement. These are ordered winner cases, not a claim of simultaneous overlap; no barrier-based concurrency is claimed by these two tests.

Attempt 4 validation on the implementation worktree:

- Focused `tests/integration/arch056-initial-outreach-credit-races.integration.test.ts` — 4/4 passed after correcting the test helper to receive its Prisma client explicitly.
- `npm run build` — passed; Prisma Client 6.19.3 generated and TypeScript compilation completed.
- Required BG002 unit command — 16 files, 272/272 passed.
- Exact required ten-file disposable PostgreSQL/Redis command in the Validation section — 10 files, 69/69 passed, no skips.
- Scoped ESLint over all ten changed TypeScript files — passed.
- `npm ls @modainteract/moda-interact-shared --depth=0` — installed runtime package `@modainteract/moda-interact-shared@3.0.0`.
- Implementation `git diff --check` — passed.

Scheduling and parallel diagnostic: `vitest.config.ts` sets `fileParallelism: false` when `MODA_DISPOSABLE_INTEGRATION=1`; the passing declared integration command is therefore serial across files. The architect's separate explicit `--fileParallelism=true` diagnostic from Attempt 3 produced 62 passed and 5 failed tests in three files, with P2034 conflicts/deadlocks; its root cause was not established. That override is not the declared validation command, and no parallel-pass or broader retry-policy claim is made.

The implementation and parent report are published on their task branches. The architect accepted Attempt 4 in the review record below. No enabled task was executed or claimed in this run.

## Architect Review

This section belongs only to moda_architect. Definition authoring is not implementation acceptance.

### Review Status

Changes Requested — Attempt 1 (2026-11-04). Return the task to `ready`; clear the executor claim. Do not mark complete or promote downstream tasks.

### Review Notes

- The implementation is substantial, but its own Completion Report says required acceptance evidence is incomplete. In particular, the latest retained-source and state-hold PostgreSQL cases were added after the passing 7-test run and have not been executed; the full required integration matrix has not passed.
- The report records 11 failures across four existing reservation-owner concurrency suites because their fixtures pass removed Prisma fields. The task's Validation section explicitly requires those failures to be resolved or dispositioned before claiming the matrix passed. Keep the limitation visible and obtain an architect disposition or update the approved scope/evidence before resubmission; do not claim those cases passed.
- Required actual installed-Shared-sink coverage remains incomplete for causes, typed holds, missing upstream fields, redaction/truncation, sink failure, rollback after owner/event mutation, and selected after-commit failure/correlation. The report also identifies these gaps; complete the owned assertions in the required test files.
- Complete the required mutation-and-rollback evidence, including same-error identity and the emitted owner record, then run the full task validation matrix including the newly added integration cases. Record actual Shared package resolution and precise pass/fail/skip results.
- Update the implementation-owned acceptance checklist from verified evidence on resubmission. The acceptance criteria currently remain unchecked, which is consistent with the outstanding validation.
- The initial task metadata said the definition was unmaterialised even though the canonical task branch and attempt claim exist. This review corrects that report discrepancy; future attempt provenance should match the launcher evidence.

### Reviewed Files

- `src/services/recovery-billing/initial-outreach-credit.service.ts`
- `src/services/recovery-billing/initial-outreach-credit-evidence.ts`
- `src/services/recovery-billing/recovery-billing.types.ts`
- `src/services/recovery-billing/recovery-reservation-lifecycle.service.ts`
- `src/services/recovery-delivery-compensation/lineage.ts`
- `src/services/recovery-delivery-compensation/reconcile.service.ts`
- `src/services/whatsapp-provider-status.service.ts`
- The implementation report's 27 listed production and test paths

### Validation Reviewed

Reviewed the reported build, focused unit suite (266 tests), targeted lint, and initial three-file PostgreSQL run (7 tests), plus the 28-test compensation and 1-test provider-status runs. These were reported by the implementer and not rerun during review. The latest added PostgreSQL cases are unexecuted; the complete required integration matrix is not passing, and emitted-record/rollback evidence remains incomplete as detailed above.

### Architecture Conformance

The inspected implementation generally follows the selected exact-source and Shop-before-message lock design. Acceptance is blocked by the required evidence and validation gaps above; no conclusion is recorded for the unexecuted cases. No architecture-wide or schema change is approved by this review.

### Follow-up

Continue on the same mirrored task branches at Attempt 2. Do not start `ARCH-056-BACKGROUND-004` or `ARCH-056-SYSTEM-TEST-001` from this task; both remain gated on accepted prerequisites.

## Architect Review — Changes Requested (Attempt 2, 2026-11-04)

### P2 — Null-message revalidation overlooks unlinked automated messages

`assertNoInitialMessageEvidence` in `src/services/recovery-billing/initial-outreach-credit-evidence.ts:189–200` queries only a message already linked to the attempt and the canonical UsageEvent. It never checks for a discoverable unlinked outbound AUTOMATION message in the owned recovery conversation. With a valid unsent INITIAL attempt, no reservation/usage/attempt link, and an existing PENDING automated message in that conversation, `revalidateExistingInitialOutreach({outboundMessageId: null})` returns `{kind: "absent"}`. The contract explicitly requires `held/lineage-conflict` for orphan evidence; consumers are authorized to make a fresh admission only after absent, so this result incorrectly authorizes fresh credit/admission on an inconsistent existing-message state.

Independently reproduced using the task's real PostgreSQL fixture and canonical migrations. A new pending orphan message was inserted without bypassing constraints; expected `held/lineage-conflict`, observed `absent`. Add a scoped same-recovery conversation orphan check without resolving identity by phone/time or accepting a guessed message; preserve exact tenant/initial ownership. Add durable regression cases in the already-owned evidence and PostgreSQL modules for the orphan hold, read-only state preservation, and genuine absence.

The temporary reviewer test was removed from the implementation worktree. Its local reproducer remains at `/tmp/arch056-review-orphan-credit.integration.test.ts`; assertion output is at `/tmp/arch056-bg002-review-orphan.log`.

### Required validation and scope disposition

The required preservation gate still fails before exercising twelve owner-concurrency/rollover cases. The five-file amendment above and matching machine-readable allowlist authorize the minimal fixture corrections. Complete those corrections and rerun the complete required command; passing focused settlement tests do not replace the unexecuted preservation assertions. HUMAN status is not added to the modification allowlist because it passed this independent run. No runtime, schema, provider or historical billing policy expansion is authorized.

### Independently verified evidence

- Implementation `79b8d5bc5cf5ad4090ee0dc0b06246e10489ca78` and parent `650778eb2d206424a367c581c4a2702b2d877c60` match their remote task branches. Both canonical task worktrees were clean at review start. Prepared Database pin is `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`.
- Exact required unit matrix: 270/270 passed, 16 files.
- Exact required PostgreSQL/Redis matrix: **53 passed, 12 failed**, 65 tests in 10 files; nonzero exit. All twelve failures are Prisma fixture errors for removed BillingPlan fields across the five named suites. The human-provider-status test passed in this run, so the implementer's 52/13 result remains historical rather than the current rerun result. No root cause is established for that earlier human-status failure.
- The additional orphan-message regression reached the database-backed assertion and failed as described above. It is separate from the 65-test required matrix.
- Production build, declared task-scoped ESLint and whitespace checks passed using Node 24.19.0. The new fixture allowlist adds those five files to required lint for the next attempt; their edits are not implemented by this review.
- Reviewed the added cause/Prisma/SQLSTATE, provider-status correlation and rollback evidence. The current owned cases passed, but acceptance is withheld for the concrete absence defect and incomplete preservation gate.

### Lifecycle and handoff

Changes Requested. Set `status: ready`, clear executor/claimed_at, preserve Attempt 2. The next normal launcher claim creates Attempt 3. BG004 and SYSTEM-TEST-001 remain gated. Preserve historical reports and do not claim BS-05 or ARCH-028-BACKGROUND-013 is resolved. No implementation source was changed, and no branch was merged. This parent review/scope overlay is local and uncommitted/unpushed pending publication.


## Architect Re-review — Changes Requested (Attempt 2 follow-up, 2026-11-04)

### Resolved findings

Reviewed the eight uncommitted implementation files on top of `79b8d5bc5cf5ad4090ee0dc0b06246e10489ca78`. The orphan-message correction now checks OUTBOUND AUTOMATION messages through the exact recovery conversation after initial-attempt/recovery/Shop validation. It fails closed with lineage-conflict and does not guess a message identity or mutate accounting. The existing genuine-absence case and new PostgreSQL orphan regression both pass. The five authorized fixture edits remove the retired BillingPlan fields and seed canonical PlatformBillingPolicy values where required; the original twelve concurrency/refund/rollover tests and assertions are preserved and now pass. The prior P2 implementation finding and twelve fixture failures are resolved in this working-tree state.

### Remaining validation blocker

The independently executed, exact ten-file required PostgreSQL/Redis command still exits nonzero: **65 passed, 1 failed, 66 total**. `tests/integration/recovery-human-provider-status.integration.test.ts:43–44` attempts to load a message with a null command outboundMessageId; the emulator reports zero sends. This occurs before provider-receipt assertions. It reproduces the implementer's combined-run failure, but neither a production cause nor a fixture/isolation cause is established. The historical isolated pass does not satisfy the required combined preservation gate. Do not waive the failure or describe the full matrix as passing.

Continue diagnosis using the existing fixture read-only and BG002-owned regression modules if additional diagnostics are needed: capture safe command state/failure code, claimed command count and the dispatcher outcome before the null lookup. Establish whether admission/preparation or test-state contamination prevented dispatch; do not infer the cause from the null ID alone. No expansion to HUMAN production code, the read-only HUMAN-status regression, or shared fixtures is granted by this review. If the demonstrated correction needs one of those paths, return the precise evidence and proposed scope for architect disposition. Preserve all original assertions and run the complete required matrix after correction.

### Independently verified validation

- Exact required units: **271/271 passed**, 16 files.
- Exact required PostgreSQL/Redis matrix: **65 passed, 1 failed**, 10 files; includes the new orphan regression and all twelve repaired legacy cases.
- Production build and the full declared task-scoped ESLint command, including the five authorized fixtures: passed.
- Implementation whitespace check: passed.
- Logs: `/tmp/arch056-bg002-rereview-integration.log`, `/tmp/arch056-bg002-rereview-unit.log`, `/tmp/arch056-bg002-rereview-build.log`, `/tmp/arch056-bg002-rereview-lint.log`.
- The broader unit suite was not rerun; retain the implementer's separately reported two failures without conflating them with this passing required unit matrix.

### Disposition and publication

Changes Requested for the remaining required validation failure; no additional production defect was identified in this correction. Keep `status: ready`, Attempt 2, executor/claimed_at null. No downstream task is promoted: BG004 and SYSTEM-TEST-001 remain gated. The implementation correction is still uncommitted/unpushed, so this review does not identify it as published or complete. Reconcile implementation-owned checklist/report text and publish the corrected implementation before resubmission. This architect addendum is local; no implementation files were changed, no commits or pushes were performed, and nothing was merged.


## Architect Review — Changes Requested (Attempt 3, 2026-11-04)

### Resolved implementation and fixture findings

Reviewed the nine local implementation-file changes on `a5953b9def12b91b79b02b5874b686fcec5cbeaf`. Null-message revalidation now holds both orphan automated-message evidence and a merchant command linked to the validated INITIAL attempt. The additional command check is read-only and does not select a replacement identity. The ARCH-028 fixture creates accepted intent and cancels/links it atomically, so another worker cannot observe its synthetic commands as due work. Conditional cleanup is scoped to tracked IDs, Shop, accepted state and absence of dispatch/lease evidence. The new command-evidence fixture likewise becomes terminal atomically. Existing compensation assertions are retained. These corrections resolve the previously reproduced code and global-command-queue contamination findings.

### P2 — Complete the required final-permit/settlement evidence

The open acceptance item is still an explicit BG002 validation obligation. Validation case 8 requires honest winner predicates: a PENDING permit winner makes settlement hold, and a confirmed-settlement winner makes the fence refuse another provider request. The task says full actual-fence integration is *also* checked in BG003; it does not transfer all BG002 proof to that task.

BG003 is accepted and its code is incorporated in this worktree. Its `initial-outreach-admission-races.integration.test.ts` uses a synthetic owner transaction that directly mutates counters/reservations and inserts a fixture ledger event; it does not invoke `InitialOutreachCreditService.settleConfirmedInitialOutreach`. BG002's parent-FK test proves one Shop-lock-before-message ordering, but does not exercise the two specified final-permit/settlement outcomes. The passing unit message-not-confirmed case does not replace the required PostgreSQL interaction evidence.

Add the missing cases in BG002-owned integration modules, using independent clients and explicit barriers where overlap is asserted. Exercise the real BG002 settlement port against the accepted fence or its documented boundary; assert held/no accounting mutation for the pending permit winner and no new permit/provider request after valid confirmed settlement, with exact reservation/counter/positive-event state. Keep eligibility states truthful; do not fabricate a successful settlement of a PENDING message. This requires no BG003 production change or edits to its owned tests. No new scope expansion is granted. Reconcile the checklist from that evidence and rerun the affected and required suites before resubmission.

### Independently verified validation and scheduling correction

- Exact declared ten-file PostgreSQL/Redis command: **67/67 passed**, 10 files, no skips.
- Required units: **272/272 passed**, 16 files.
- Build, full declared scoped ESLint and implementation/parent whitespace checks: passed.
- The effective `vitest.config.ts` sets `fileParallelism: false` when disposable integration is enabled. Therefore the passing default command is serial across files; the report's description of it as default-parallel is incorrect.
- Additional diagnostic run of the same ten files with explicit `--fileParallelism=true`: **62 passed, 5 failed**, across 3 failed files. Failures report Prisma P2034 write conflicts/deadlocks in the source settlement cases, shared-counter race and parent-FK test. The HUMAN-status case passed. The root cause of these parallel-run failures was not established by this review. This override is not the declared validation command and does not negate its 67/67 pass; do not claim parallel validation passed or expand production retry policy from this diagnostic result.
- Logs: `/tmp/arch056-bg002-attempt3-review-integration.log`, `/tmp/arch056-bg002-attempt3-review-unit.log`, `/tmp/arch056-bg002-attempt3-review-build.log`, `/tmp/arch056-bg002-attempt3-review-lint.log`, `/tmp/arch056-bg002-attempt3-review-parallel.log`.

### Disposition and handoff

Changes Requested for the outstanding required interaction evidence, not for a newly demonstrated production defect. Correct the scheduling description in the completion report and retain the diagnostic result. Return to `ready`, clear executor/claimed_at, preserve Attempt 3; the next normal claim creates Attempt 4. Implementation corrections remain uncommitted/unpushed; publication is still required before durable completion. BG004 and SYSTEM-TEST-001 remain gated. This review changes only the parent task record, is local and uncommitted, and neither publishes implementation nor merges any branch.

## Architect Re-review — Accepted (Attempt 4, 2026-11-04)

### Review Status

Accepted — Attempt 4. `completion_mode: automatic`; task status is `complete`.

### Review Notes

- The requested final-permit/settlement evidence is now covered in the BG002-owned PostgreSQL race suite using the real outbound fence and `InitialOutreachCreditService` on independent clients. Permit-first leaves the message PENDING, settlement returns `held/message-not-confirmed`, accounting remains unchanged, and no provider call occurs. Confirmed-settlement-first records the durable send and exact credit once; a later fence/resume does not make another provider call.
- The tests represent ordered winner cases and make no claim of barrier-proven simultaneous overlap. No blocking findings remain; scope and ownership are respected, with no production or BG003-owned changes in Attempt 4.

### Reviewed Files

- `tests/integration/arch056-initial-outreach-credit-races.integration.test.ts`
- Attempt 4 Completion Report and the task's declared acceptance/validation contract

### Validation Reviewed

- Focused BG002 race integration suite independently rerun: **4/4 passed**.
- The Attempt 4 report records the full required PostgreSQL/Redis matrix at **69/69 passed with no skips**, required units at **272/272**, plus build, scoped ESLint and `git diff --check` passing. Those broader checks were reviewed from the report, not rerun during this review-only re-review.

### Architecture Conformance

The outstanding Attempt 3 interaction-evidence request is satisfied. The implementation and evidence remain within BG002's approved scope; the ordered outcome assertions preserve the documented settlement and permit boundaries. No new architecture or policy claim is introduced.

### Follow-up

No correction is requested. This task is accepted and complete. BG004 and SYSTEM-TEST-001 were not executed, claimed, or edited. This architect disposition changes no implementation code and does not commit, push, merge, or otherwise publish the parent task branch; publication remains the developer's responsibility.
