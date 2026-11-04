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
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-028-BACKGROUND-004
- ARCH-028-BACKGROUND-009
enables:
- ARCH-056-BACKGROUND-004
- ARCH-056-SYSTEM-TEST-001
created: '2026-11-03'
updated: '2026-11-04'
---

# ARCH-056-BACKGROUND-002: Reuse and settle the exact initial recovery credit

## Architecture

Architecture: `ARCH-056`. Parent: `docs/architecture/ARCH-056-background-persistence-and-recovery-progress.md`. Coordinator: `moda_architect`.

Definition revision: 3. **Defined but not materialised.** No task branch, claim, implementation, test execution, commit or push is asserted. The two explicit prerequisites are Complete in the supplied snapshot; recheck their canonical status before execution.

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

- [ ] Add exact input/result contracts and a thin facade collaborator, preserving existing constructor/caller compatibility and test injection.
- [ ] Extract the existing unique source lookup without changing compensation's refusal behavior.
- [ ] Add same-transaction owner wrappers, promotional retained-source eligibility and the typed paid-period guard.
- [ ] Implement durable confirmed settlement with verified positive results, rollback-on-hold and Shop-key-share-before-message locking.
- [ ] Apply the same early owned-Shop lock to existing provider-status/compensation transaction entries, retaining all their existing policy and after-commit behavior.
- [ ] Implement read-only retained-source revalidation, including null-message reserved-before-outbound interruption and strict absent semantics.
- [ ] Make the existing successful-commit facade reject noncommitted owner outcomes.
- [ ] Reuse the paid plan's already validated meter handle.
- [ ] Implement the fixed selected failure/hold/retry diagnostic owners, stages and correlation fields, preserving original exception identity and existing accounting/status behavior.
- [ ] Emit provider-status `applied` only after successful SQL commit; distinguish later committed-status continuation failures.
- [ ] Add actual installed Shared-sink assertions for original direct messages, known causes, allowlisted database metadata, typed holds, exhausted retries, missing upstream fields, redaction and logging-sink failure isolation; do not certify this with logger-call mocks.
- [ ] Add and execute the bounded unit/PostgreSQL matrix below; report contracts to BG004 and preserve BG003's lock-order agreement.

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

- [ ] Four source owners settle a positively confirmed initial message at most once through their existing accounting transactions.
- [ ] Exact COMMITTED replay validates the original positive event and remains safe after period/policy change; stale RESERVED paid periods remain held.
- [ ] AMBIGUOUS, RELEASED, compensated, missing or nonunique source evidence never becomes a new charge or a successful finalization result.
- [ ] Pre-permit restart returns the same reservation/source admission without accounting mutation; null-message interruption is covered and only verified source absence authorizes fresh admission.
- [ ] Every held/error outcome preserves ledger state or rolls back all changes; failures retain their original diagnostics.
- [ ] Confirmed settlement, provider failure/131026 compensation, final permit and shared-counter races obey the documented lock order and positive accounting invariants.
- [ ] BS-04's duplicate Shopify meter read is removed without report/provider changes; BS-05 and Blocked BG013 remain accurately bounded.
- [ ] No edits escape the declared ownership allowlist or change schema, provider, queue, Support or recovery-status behavior directly.

- [ ] Every selected material technical failure and exception-derived hold has its original safe direct message in an actual emitted Shared record at the declared service owner, with precise stage and available original identities.
- [ ] Final retry failure rethrows the same exception, logs the actual retry state, and cannot emit false successful status application; after-commit failures identify which state already committed.
- [ ] Known cause and allowlisted Prisma/SQLSTATE diagnostics are emitted explicitly when present; missing data produces no invented provider/database facts. Stack/cause-graph completeness is not claimed from Shared's direct Error serializer.
- [ ] Captured emitted records pass the common sensitive-data/redaction/truncation assertions. Logging sink failure leaves accounting, holds, retries and original thrown exceptions unchanged.
- [ ] Source-owned detailed diagnostics and downstream stage context follow the owner table; tests do not rely on an unrelated worker callback to compensate for a missing direct-service diagnostic.

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
- `tests/integration/initial-outreach-credit.integration.test.ts`
- `tests/integration/initial-outreach-credit-races.integration.test.ts`
- `tests/integration/initial-outreach-parent-fk.integration.test.ts`
- `tests/integration/fixtures/initial-outreach-credit.fixture.ts`

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
- `tests/integration/initial-outreach-credit-races.integration.test.ts`: correlate the real compensation failure record with the real status caller's context-only record after status commit. Use test-only fault injection in these integration files; do not add production failpoints.
- The existing four source-owner unit files: retain/extend same-transaction wrapper exception-identity assertions; no duplicate log-owner wrapper is required in every source service.

The BG002 unit/integration/build/lint commands below execute these files. No additional runner or dependency is needed. Record the actual installed Shared version/package resolution with the test result; source inspection of a sibling Shared checkout is supporting evidence, not proof of the runtime package used by Background.

Run from the launcher-resolved implementation worktree after existing locked dependencies are available:

```bash
npm run build
npm run test -- tests/unit/services/recovery-billing.service.test.ts tests/unit/services/recovery-billing tests/unit/services/free-recovery-reservation.service.test.ts tests/unit/services/purchased-recovery-reservation.service.test.ts tests/unit/services/promotional-recovery-reservation.service.test.ts tests/unit/services/paid-included-recovery-reservation.service.test.ts tests/unit/services/whatsapp-provider-status.service.test.ts tests/unit/services/recovery-reservation/reservation-lifecycle.test.ts
npm run test:integration -- tests/integration/initial-outreach-credit.integration.test.ts tests/integration/initial-outreach-credit-races.integration.test.ts tests/integration/initial-outreach-parent-fk.integration.test.ts tests/integration/arch028-recovery-delivery-compensation.integration.test.ts tests/integration/recovery-human-provider-status.integration.test.ts tests/integration/free-recovery-reservation.concurrency.integration.test.ts tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts tests/integration/paid-included-recovery-reservation.concurrency.integration.test.ts tests/integration/same-plan-billing-period-rollover.concurrency.integration.test.ts
npx --no-install eslint src/services/recovery-billing.service.ts src/services/recovery-billing/recovery-billing.types.ts src/services/recovery-billing/recovery-reservation-lifecycle.service.ts src/services/recovery-billing/initial-outreach-credit.service.ts src/services/recovery-billing/initial-outreach-credit-evidence.ts src/services/recovery-delivery-compensation/lineage.ts src/services/recovery-delivery-compensation/reconcile.service.ts src/services/whatsapp-provider-status.service.ts src/services/free-recovery-reservation.service.ts src/services/purchased-recovery-reservation.service.ts src/services/promotional-recovery-reservation.service.ts src/services/paid-included-recovery-reservation.service.ts tests/unit/services/recovery-billing.service.test.ts tests/unit/services/recovery-billing/recovery-reservation-lifecycle.service.test.ts tests/unit/services/recovery-billing/recovery-billing.test-support.ts tests/unit/services/recovery-billing/initial-outreach-credit.service.test.ts tests/unit/services/recovery-billing/initial-outreach-credit-evidence.test.ts tests/unit/services/recovery-billing/initial-outreach-credit.test-support.ts tests/unit/services/free-recovery-reservation.service.test.ts tests/unit/services/purchased-recovery-reservation.service.test.ts tests/unit/services/promotional-recovery-reservation.service.test.ts tests/unit/services/paid-included-recovery-reservation.service.test.ts tests/unit/services/whatsapp-provider-status.service.test.ts tests/integration/arch028-recovery-delivery-compensation.integration.test.ts tests/integration/initial-outreach-credit.integration.test.ts tests/integration/initial-outreach-credit-races.integration.test.ts tests/integration/initial-outreach-parent-fk.integration.test.ts tests/integration/fixtures/initial-outreach-credit.fixture.ts
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

Not Started

### Files Changed

Pending implementation.

### Work Completed

Pending implementation.

### Validation Results

Not run. Record exact commands, exit results, failures, warnings, source/build/schema provenance, scenario evidence and cleanup; do not copy planned checks as completed results.

### Deviations

None at definition time. Record actual deviations and their architect disposition before review.

### Assumptions

The reviewed snapshot and accepted prerequisite contracts are the definition baseline. Recheck the real current checkout and task state at launch.

### Unresolved Issues

Pending implementation evidence. Preserve the task's explicit held/deferred and blocked-policy boundaries.

### Architectural Concerns

Return changes to ownership, contracts, schema, transaction boundaries, durable-state semantics, queue behavior, security or another repository to moda_architect before expanding scope.

## Architect Review

This section belongs only to moda_architect. Definition authoring is not implementation acceptance.

### Review Status

Pending

### Review Notes

Awaiting an implementation submission and its evidence.

### Reviewed Files

No implementation submitted.

### Validation Reviewed

No implementation validation submitted.

### Architecture Conformance

Pending review against the parent architecture, task allowlist, interface contracts, repository boundaries and failure requirements.

### Follow-up

Pending implementation review; no enabled task may be started by this task's executor.
