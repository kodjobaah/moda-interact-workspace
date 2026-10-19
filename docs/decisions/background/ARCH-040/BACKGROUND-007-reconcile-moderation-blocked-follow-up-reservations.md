---
id: ARCH-040-BACKGROUND-007
architecture_id: ARCH-040
title: Application-owned terminal cancellation and follow-up claim release
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-DATABASE-006
  - ARCH-040-BACKGROUND-002
  - ARCH-040-BACKGROUND-006
enables:
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-SYSTEM-TEST-002
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-19
updated: 2026-10-19
---

# ARCH-040-BACKGROUND-007 — Application-owned pre-provider follow-up release

## Architecture

- Initiative: `ARCH-040`, canonical parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.
- Owner: `moda_background` in `moda-interact-background`; pending until accepted DATABASE-006 is available in the Background database submodule.
- **This task is the sole owner of the complete follow-up claim/release state machine** for terminal pre-provider HUMAN sends. PostgreSQL only preserves existing row uniqueness, FK/identity, and narrow irreversible-provider safeguards.

## Objective

Ensure the single sequence-two recovery follow-up is not permanently consumed when its current HUMAN template command is terminally refused **before** Meta provider admission (including moderation BLOCK/REVIEW_REQUIRED). Under one application-owned PostgreSQL locking protocol, cancel the exact current command, release its unused attempt claim when safe, and preserve immutable command history and the original billing identity. Recover cancelled-but-still-claimed rows after crashes, without Shopify/Woo-specific processing, new queues or an additional follow-up attempt.

## Context — verified code to extend

- `src/services/recovery-conversation/merchant-send-command.service.ts`: `MerchantSendCommandService.rejectCommand` currently cancels the command only; it does **not** release the associated attempt.
- `src/services/recovery-conversation/human-command-dispatcher.service.ts`: `HumanCommandDispatcherService.processClaim` has terminal calls to `rejectCommand`; `claimMerchantFollowUp` is already available, and this dispatcher polls active/retryable commands only. Historical `CANCELLED` commands therefore require a **separate bounded repair scan**.
- `src/services/recovery-conversation/recovery-follow-up-policy.service.ts`: `RecoveryFollowUpPolicyService.claimSequenceTwo` already locks Shop/Conversation and the sequence-two attempt, implements existing HUMAN/AUTOMATION eligibility and uses the existing `recovery-outreach:<attemptId>` billing source.
- `src/services/recovery-conversation/outbound-send-fence.service.ts`: `OutboundSendFenceService.admitFinalSend` serializes the irreversible provider permit under Shop/Conversation/command/attempt row locks. A commit of this permit forbids release even if Meta later fails.
- `src/services/recovery-conversation/recovery-follow-up-billing.service.ts`: `RecoveryFollowUpBillingService.releaseBeforePermit` bridges the existing reservation lifecycle; it is **not** a second credit ledger.
- The merchant-side Shopify and Woo/API producers may already reserve sequence two when accepting a HUMAN template command. Background moderation happens later; checking moderation before the Background *second claim* is insufficient.

## Scope and exact change surface

1. Add one small application service under `src/services/recovery-conversation/`, e.g. `follow-up-reservation-reconciliation.service.ts`. It owns the transition, eligibility checks, billing coordination and reconciliation, using the accepted DATABASE-006 schema. No new generic framework or service deployment.
2. Change `merchant-send-command.service.ts` so terminal follow-up rejections use one lease-protected cancellation-and-release application operation rather than `rejectCommand` alone. Preserve `rejectCommand` for non-follow-up commands.
3. Change `human-command-dispatcher.service.ts` at **every terminal pre-provider** rejection branch; retain `deferCommand` for retryable outcomes, and never rerun a provider-admitted send.
4. Use the existing dispatcher poll lifecycle for a bounded cancelled-command repair scan. This scan is separate from `claimDueHumanCommands` and never sends anything to Meta.
5. Keep `RecoveryFollowUpPolicyService.claimSequenceTwo` as the **single** post-release claim operation for subsequent HUMAN/AUTOMATION requests; update only as necessary for transactional ownership compatibility, not to invent another scheduler.
6. Use only existing billing/admission, send-fence and provider-status services; never bypass provider/credit invariants.
7. Add isolated tests and PostgreSQL integration proofs for cancellations, concurrency, replay, crash recovery and billing non-effects.

## Normative algorithm — no alternatives

### A. Current owner and immutable identity

Use the existing attempt row uniquely selected by `(checkoutRecoveryId, sequence=2)`. A HUMAN owner is current **only if all** of:

```text
cmd.recoveryOutreachAttemptId == attempt.id
cmd.shopId == CheckoutRecovery.shopId == Conversation's effective shop
cmd.conversationId == recovery-linked Conversation.id
cmd.kind == RECOVERY_FOLLOW_UP_TEMPLATE
attempt.initiatedBy == HUMAN
attempt.initiationKey == cmd.idempotencyKey
attempt.status == PENDING
attempt.outboundMessageId == NULL
attempt.sentAt == NULL
cmd.providerDispatchKey == NULL
cmd.providerDispatchAdmittedAt == NULL
cmd.outboundMessageId == NULL
```

For normal dispatcher cancellation also require `cmd.state=CLAIMED`, the **current** `cmd.leaseToken`, and unexpired `cmd.leaseExpiresAt` as evaluated with the database clock. A historical-repair candidate instead requires immutable `cmd.state=CANCELLED` and a linked attempt **still** matching its `idempotencyKey`; no worker lease is fabricated for a terminal command. Also check that no related command has irreversible provider evidence or an incompatible live owner. Treat `UNKNOWN`, `DISPATCH_ADMITTED`, `SENT`, a linked provider message or an unresolved provider result as **never releasable**. The old command's `idempotencyKey`, `payloadSha256`, attempt FK and recipient remain unchanged.

### B. Locking and claim serialization

Use **one short PostgreSQL transaction** for the command cancellation and attempt claim reset. The lock order is mandatory and matches accepted send admission:

```text
1. commerce.Shop FOR UPDATE
2. whatsapp.Conversation FOR UPDATE
3. whatsapp.MerchantConversationSendCommand (current owner) FOR UPDATE
4. commerce.RecoveryOutreachAttempt (checkoutRecoveryId, sequence=2) FOR UPDATE
```

Start by resolving canonical recovery/shop/conversation identities using `readRecoveryContext`, then re-read/revalidate after `lockRecoveryContext(tx, conversationId)` obtains Shop/Conversation locks. Do not accept a browser-supplied shop or initiation key as authority. Lock the command and attempt in that order and use a bounded conditional UPDATE to prevent stale/ABA reset. The scheduled automated follow-up uses the same Shop/Conversation/attempt locks via `claimSequenceTwo`; do not bypass it with a separate INSERT or a second attempt.

### C. Billing is a prerequisite for releasing the claim

A reserved follow-up's credit identity is **always** `recovery-outreach:<attemptId>` and must never change across release/reclaim. Moderation `BLOCK`/`REVIEW_REQUIRED` is **not** a credit or provider event.

Before performing the final attempt reset, inspect the existing billing/reservation record for this credit identity using the existing `RecoveryFollowUpBillingService` / `RecoveryBillingService` interfaces. If a provisional admission is present, use `releaseBeforePermit` **outside** the claim-reset transaction, then verify that the durable reservation is released/cleared and no settled usage remains. If the credit state cannot be established or release fails, **do not release the attempt**; retain it as reserved for the same command and retry safe reconciliation. Do not invent a refund, new credit, source key or ledger. If a billing port does not expose a durable read needed to verify the state, report the exact gap to `moda_architect`; do not assume no reservation exists. Never call Meta, Redis or external services inside the transaction.

If a moderation/policy denial is terminal while credit release remains uncertain, preserve a fail-closed retryable cancellation-repair intent on the original command (using its existing FAILED/failureCode/nextAttemptAt fields if not provider-admitted), and prioritise that repair intent **before** reevaluating send eligibility on a later poll. Such a command must never transition back to an outbound send while repair is pending. Do not introduce a new queue or unbounded retries.

### D. Atomic cancel-and-release for the current claimed command

After preconditions A/B/C succeed, execute, in **the same** short transaction:

```text
1. Lease/CAS: CLAIMED + current token + unexpired lease + NULL provider permit
   -> CANCELLED with the existing bounded failureCode,
      completedAt=database time, lease cleared, payload/FK unchanged.
2. CAS on the *same* attempt id:
   WHERE sequence=2 AND status=PENDING
     AND initiatedBy=HUMAN AND initiationKey=:originalIdempotencyKey
     AND outboundMessageId IS NULL AND sentAt IS NULL
   SET initiatedBy=NULL, initiationKey=NULL, claimedAt=NULL,
       updatedAt=database time.
3. Require exactly one affected row at each transition or roll back both.
```

Do not reset `trigger`, recipient, offer snapshot, due time, credit rows or historical links. The new claimant's later `claimSequenceTwo` operation sets its own `initiatedBy`, `initiationKey`, `claimedAt`, and `trigger` under the same Shop/Conversation/attempt lock discipline. If either CAS affects zero rows, classify stale owner, lost lease, already released or irreversible state; do not fall back to unguarded SQL or erase a newer owner.

### E. Historical cancelled-command repair

During the existing dispatcher cycle, run one **read-only** due-discovery query (no pre-locking commands out of canonical order) for at most 25 historical candidates per cycle:

```text
CANCELLED HUMAN RECOVERY_FOLLOW_UP_TEMPLATE commands
  with recoveryOutreachAttemptId not null
  joined to PENDING sequence-two attempt
  where attempt.initiatedBy=HUMAN
    and attempt.initiationKey=cmd.idempotencyKey
    and attempt.outboundMessageId IS NULL AND attempt.sentAt IS NULL
    and cmd.providerDispatchKey IS NULL AND cmd.outboundMessageId IS NULL
ORDER BY cmd.createdAt, cmd.id
LIMIT 25
```

For each candidate, perform the same canonical lock/re-read and billing prerequisite, then reset **only** the still-current attempt claim; the command remains CANCELLED. A stale row, newly claimed attempt or provider-admitted row is a safe no-op. The query must be bounded/index-supported by existing due and FK indexes; add an application query index only if justified by an actual measured plan and route any schema request to `moda_architect`, not a new worker/queue. On crash after credit release but before attempt reset, the next scan retries idempotently. On crash before terminal cancellation, the original command lease recovery must re-enter the same terminal workflow, not send denied content.

### F. Outcome matrix (authoritative)

| Condition | Command outcome | Sequence-two attempt | Provider/billing |
|---|---|---|---|
| Moderation BLOCK or REVIEW_REQUIRED, pre-permit | CANCELLED by atomic operation | Reset same row to unclaimed after credit-safe check | No provider send or recovery credit |
| Terminal suspended shop, stale revision, terminal recovery, invalid recipient, policy denial, pre-permit | CANCELLED by same operation | Reset same row only if current HUMAN owner, safe | No provider send/new credit |
| Retryable moderation/transport dependency, transient policy error, capacity retry | FAILED with bounded retry | Claim remains owned | No provider permit; do not free slot |
| Credit release uncertain | Repair-priority FAILED (no provider permit) | Claim remains owned | Never send while repair pending |
| Stale or expired lease/current-owner mismatch | Refused/no-op | Unchanged | No provider send or credit |
| Already CANCELLED with matching old claim | Historical reconciliation, idempotent | Reset only if all safe predicates still hold | No extra credit |
| Already released or claimed by another | No-op/conflict | Keep new claimant unchanged | No extra credit |
| DISPATCH_ADMITTED / UNKNOWN / SENT, provider ID/message linked | Do not cancel/release | Permanent reservation for that attempt | Existing provider/credit reconciliation only |
| Subsequent eligible HUMAN or scheduled AUTOMATION | New independent claim via existing `claimSequenceTwo` | Same original attempt, one winner | Existing admission and source key only |

A terminal denial of a **non-follow-up** HUMAN_TEXT command continues using the existing `rejectCommand` and does not touch outreach.

## Out of Scope

- No schema/migration changes (DATABASE-006 owns them), no new partial active-owner index or trigger-driven policy, no new follow-up scheduler/BullMQ queue or deployment.
- No platform discriminator, Shopify/Woo/API acceptance/UI change, no merchant account/role model, no new outbound transport/billing ledger, no additional `Conversation` or sequence-two row.
- No release after provider admission or of a live retryable claim; no resetting command identity, claim recipient, payload or previous credit history.
- No `_index.md` updates, unrelated refactor or reopening completed BACKGROUND-002/BACKGROUND-006 tasks.

## Requirements

- **Application authority:** BG007 alone decides whether release is appropriate. DATABASE-006 permits only a narrow structural reset, never determines eligibility/moderation/billing/owner.
- **Transaction correctness:** One atomic cancellation + attempt reset under canonical locks; deterministic CAS outcomes and multi-replica safety; no provider/network call in transaction.
- **Historical safety:** Preserve cancelled command identity and audit links, no re-send on original idempotency replay, no ABA loss of new owner.
- **Credit/permit safety:** Fail closed if provider or credit disposition cannot be proven; no successful send/credit created by moderation outcomes.
- **Platform neutrality:** One dispatcher handles all recovery-linked HUMAN commands from Shopify and Woo API; scheduled follow-up remains in existing BullMQ pipeline.

## Work Items

- [ ] Inspect accepted DATABASE-006 changes and sync generated Prisma/client before implementation.
- [ ] Implement exact lock/CAS cancellation-and-release operation under the existing SQL port; require database clock lease check.
- [ ] Update `human-command-dispatcher.service.ts` terminal rejection branches to use the operation for follow-up commands; preserve non-follow-up handling and retryable deferrals.
- [ ] Add fail-closed billing precondition/release verification; route missing durable inspection primitive for architect decision instead of guessing.
- [ ] Add bounded, read-only discovery + per-candidate canonical-lock historical CANCELLED repair in the existing polling cycle.
- [ ] Inspect both Shopify and Woo API HUMAN template-command acceptance transactions and the scheduled AUTOMATION `claimSequenceTwo()` path to confirm they serialize on the same Shop/Conversation/attempt locks. If a producer can bypass the lock/claim protocol, report an architectural blocker to `moda_architect`; do not edit another repository or claim integration safety.
- [ ] Ensure subsequent `claimSequenceTwo()` of HUMAN/AUTOMATION uses same row and unaffected eligibility/credit rules.
- [ ] Add unit and disposable PostgreSQL tests for moderation refusal, billing failure, lease expiry, failed two-step transaction, crash recovery, two workers, HUMAN-vs-AUTOMATION races, stale releases and idempotency replays.
- [ ] Use shared structured logging for bounded reason codes/identities only, not content or secrets; record exact changes and deviations.

## Interfaces / Contracts

- `RecoveryFollowUpPolicyService.claimSequenceTwo`: one shared claimant of `(checkoutRecoveryId, 2)`.
- `MerchantSendCommandService`, `HumanCommandDispatcherService`, `OutboundSendFenceService`, `RecoveryFollowUpBillingService`, `HumanSendReconciliationService`, `ModerationAssessmentService`.
- Persistence: `commerce.RecoveryOutreachAttempt`, `whatsapp.MerchantConversationSendCommand` and existing credit/recipient/receipt records.
- Database schema gate: `ARCH-040-DATABASE-006`; no new Shared package or platform-specific queue.

## Dependencies

- `ARCH-040-DATABASE-006` (must be accepted Complete).
- `ARCH-040-BACKGROUND-002` (Complete in October 19 snapshot).
- `ARCH-040-BACKGROUND-006` (Complete in October 19 snapshot).

## Enables

- `ARCH-040-SYSTEM-TEST-001`.
- `ARCH-040-SYSTEM-TEST-002`.
- `ARCH-040-SYSTEM-TEST-003`.

## Acceptance Criteria

- [ ] Terminal pre-provider follow-up refusals cancel the original current command, make the **same** unique sequence-two attempt eligible for a new claim, and preserve historical links/idempotency.
- [ ] Moderation ALLOW/BLOCK alone neither sends a message nor consumes credit; a blocked/review-required pre-permit command never reaches Meta or settled recovery usage.
- [ ] Retried moderation/credit dependencies retain the original slot; failed billing release cannot make the attempt available or later dispatch an originally denied command.
- [ ] Concurrency between cancellation, original-lease expiry, new HUMAN command, scheduled AUTOMATION and final provider admission yields one valid claimant and no stale-owner overwrite.
- [ ] Historical CANCELLED command repair succeeds within bounded dispatcher polls; a stale, already-released or post-provider row is a no-op.
- [ ] No release of a DISPATCH_ADMITTED, UNKNOWN, SENT or provider-message-linked attempt regardless of provider's later definitive result; duplicate command replay remains terminal.
- [ ] Shopify and WooCommerce use exactly the same Background implementation; existing worker scheduling and follow-up billing identity remain unchanged.

## Validation

Recommended implementation evidence (subsequent developer integration/certification remains separate from feature acceptance):

- [ ] Existing repository-declared ARCH-040 service, wiring and moderation suites after verifying `package.json`.
- [ ] Disposable PostgreSQL integration for real row locks, triggers, new relation and provider/credit non-effects.
- [ ] Injected crash/restart, lease-expiration and multi-replica contention tests with fake provider.
- [ ] `npm run lint`, `npm run build`, `git diff --check` if declared; task worktree and gitlink evidence.

## Stop Condition

When the defined feature is implemented with its Completion Report, transition to review and STOP; do not start dependent system tests.

## Implementation Notes

Any missing billing-read primitive or release contract is an architecture gap. Do not invent a competing ledger, clear a claim after UNKNOWN/provider permit, mutate accepted DATABASE-001 migrations or add database policy triggers in BG007. Changes required in Shopify/Woo producers must be returned to `moda_architect`, not implemented across repository boundaries.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

October 19, 2026 snapshot; canonical launcher/worktree state must be verified when executing.

### Unresolved Issues

None recorded.

### Architectural Concerns

If an existing producer can bypass the same lock/claim protocol, report the exact source path to `moda_architect` before integration acceptance; no platform-specific bypass is permitted.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting code review and persisted state/credit tests.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

After acceptance, the three independent system-test tasks verify complete platform execution.

## Developer Takeover

On 2026-10-19, the developer explicitly took ownership of Attempt 1 for implementation. The logical repository owner remains `moda_background`; this amendment changes only execution and completion authority to developer mode. The task scope, dependencies, acceptance criteria and architectural ownership are unchanged.
