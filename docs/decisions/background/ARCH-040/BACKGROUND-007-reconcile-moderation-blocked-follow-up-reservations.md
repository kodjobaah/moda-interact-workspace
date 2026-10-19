---
id: ARCH-040-BACKGROUND-007
architecture_id: ARCH-040
title: Reconcile and release terminal pre-provider HUMAN follow-up reservations
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
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

# ARCH-040-BACKGROUND-007 — Reconcile moderation-blocked follow-up reservations

## Architecture

- Initiative: `ARCH-040`.
- Parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.
- Repository owner: `moda_background`, `moda-interact-background`.
- Coordination: `moda_architect`.
- **Defined, not materialised.** Pending until accepted DATABASE-006; no branch, worktree, implementation or validation is claimed.

## Objective

Ensure a HUMAN sequence-two template command **terminally rejected before provider admission** (including moderation `BLOCK`/`REVIEW_REQUIRED`) relinquishes its unused follow-up reservation safely and idempotently, making the *same* recovery/sequence-two allowance eligible for a subsequent independent claim, without sending to Meta or charging a recovery credit.

## Context

The 2026-10-18 21:47 snapshot contains completed BACKGROUND-002 and BACKGROUND-006. The production path is:

`src/services/recovery-conversation/human-command-dispatcher.service.ts` → `HumanCommandEvaluationService` / `ModerationAssessmentService` → `MerchantSendCommandService.rejectCommand`.

`HumanCommandDispatcherService.processClaim()` moderates the persisted HUMAN command **before its own provider admission**, but Shopify's ARCH-040-SHOPIFY-001 candidate has already reserved sequence-two in the earlier merchant-command acceptance transaction (the Woo/API producer contract is intended to be equivalent). On terminal moderation rejection, the dispatcher currently calls `rejectCommand(...)`, which changes the command to `CANCELLED` but does not reconcile `RecoveryOutreachAttempt.initiationKey`. The attempt remains `PENDING` and claimed, so `RecoveryFollowUpPolicyService.claimSequenceTwo()` returns `already-claimed`. A retryable moderation outage returns FAILED/nextAttemptAt and **must not** release the reservation.

**The database constraint blocker is real:** DATABASE-001 freezes an already claimed attempt and enforces a unique immutable command-to-attempt FK. DATABASE-006 must be accepted before implementing this Background task. Do not bypass these guards using raw SQL, deleting commands, new sequence rows or another credit source.

## Scope

- Bounded changes in `src/services/recovery-conversation/`, particularly `merchant-send-command.service.ts`, `human-command-dispatcher.service.ts` and, if needed, a small dedicated `follow-up-reservation-reconciliation.service.ts`.
- Use the accepted DATABASE-006 claim-release contract inside the **same short PostgreSQL transaction** as a lease-fenced terminal command cancellation where practical; maintain Shop → Conversation → command/sequence-two attempt lock order.
- Reconcile historical orphaned HUMAN reservations already associated with safely terminal `CANCELLED` commands, in bounded batches on the existing dispatcher polling/recovery path; do not add a new queue or deployment. Include explicit ownership predicates and a no-op result for stale claims.
- Apply the same safe terminal-cancel/release operation to all relevant **pre-provider** paths: control/recovery state conflicts, merchant suspension, deterministic HUMAN policy denial, moderation BLOCK/REVIEW_REQUIRED, invalid recipient, lost permission and failed final fence (provided no provider permit exists).
- Preserve retry state/ownership for transient moderation infrastructure failure, policy dependency errors and retryable credit-capacity outcomes. A temporary FAILED command with `nextAttemptAt` is not terminal and should not release the claim.
- Coordinate any held provisional billing admission with existing `RecoveryFollowUpBillingService.releaseBeforePermit`, and prove no settled credit/provider-side effects for a blocked command. Keep `recovery-outreach:<attemptId>` as the only credit source.
- Focused deterministic unit tests, disposable PostgreSQL integration tests, crash/restart and two-replica races with fake moderation/Meta transports.

## Out of Scope

- Do not change Prisma schema/migrations in this task; DATABASE-006 owns those. Do not implement Shopify/Woo/API acceptance/UI or 20-locale translations.
- No separate customer conversation, resend queue, new scheduler, provider transport, billing model, duplicate attempt, second follow-up, or credit per HUMAN message.
- Never release when `providerDispatchKey`/`outboundMessageId`/provider message exists, or state is `DISPATCH_ADMITTED`, `UNKNOWN` or `SENT`, even if a later provider result is a definite failure; post-permit compensation is a separate existing workflow.
- Do not mask a moderation failure as ALLOW, automatically resend terminally rejected content, or turn moderation review into an automatic suspension.
- Do not update `docs/decisions/**/_index.md` pending the end-of-session agreement.

## Requirements

### R1. Terminal cancellation and release are one logical operation

A dispatcher that owns an unexpired `CLAIMED` command lease, and has not admitted an irreversible provider permit, must atomically:

1. Resolve the command's trusted shop/recovery/conversation/attempt identities from PostgreSQL, not from the UI.
2. Acquire the documented Shop → Conversation → command/attempt locks and verify that the command is the **current** HUMAN claimant of this recovery's sequence-two row.
3. CAS the command to terminal `CANCELLED` with the existing bounded safe failure code and immutable payload/idempotency unchanged.
4. Release only that claimant's still-pending, unsubmitted attempt through the accepted DATABASE-006 guarded transition. Do not touch any unrelated or newly claimed row.
5. Commit both mutations together, or make neither visible; return a structured already-processed/stale/fenced result for racing workers.

If an underlying provisionally reserved billing admission exists, use the existing no-charge release/compensation contract safely, without a provider call inside a database transaction. Document the atomicity/repair boundary if the billing port cannot share the database transaction.

### R2. Moderation decisions and retry semantics

- `BLOCK`/`REVIEW_REQUIRED` for the *persisted* HUMAN template content: terminal cancellation, no Meta, no credit, release reservation.
- Dependency outage, timeout, retryable moderation or `moderation_content_stale`: defer/retry the **same command and claim**; keep ownership until a terminal outcome or provider permit.
- A stale/different moderation digest must not be reused as ALLOW. The command is never auto-modified to evade moderation.
- Repeated moderation callbacks and worker claims must produce no duplicate releases or reissued provider permits.

### R3. Reconciliation after crashes and cross-platform consistency

- A cancelled-but-claimed pre-provider HUMAN command left by legacy behavior is eligible for idempotent bounded repair; use durable identities and explicit predicates.
- A lease timeout before cancellation must not permit two workers to cancel/release different active claims. A crash between logical steps converges without losing/overwriting a later owner.
- After release, `claimSequenceTwo` must permit only the next **eligible** HUMAN or scheduled AUTOMATION claimant; the ordinary mode/revision, customer-window, initial outreach, terminal recovery and recipient checks still apply. An old command's replay returns its original terminal command; it cannot seize the new claimant's slot.
- Existing sequence-two UNIQUE index, send fence, provider-ambiguous `UNKNOWN` reconciliation, and usage-source semantics remain unchanged.
- Shopify and Woo producers share this Background behavior, with no platform discriminator/branch in the worker.

### R4. Audit, logging and safety

- Use the existing published `@modainteract/moda-interact-shared/logging`, not a service-local JSON logger. Emit bounded events with `shopId`, `conversationId`, `commandId`, `attemptId`, `outcome` and safe reason codes for release success, stale owner/no-op, blocked release and recovery repair.
- Never log message text, template parameters, recipient phone, provider tokens, database URLs, raw database exceptions or moderation input. Expected idempotent replay should not be treated as an unhandled exception.
- The merchant command remains visibly terminal/not sent; never present a cancelled or moderated command as provider `SENT` merely because the follow-up slot is available again.

## Work Items

- [ ] Read accepted DATABASE-006 migration/release contract and ensure the Background database submodule contains its accepted commit.
- [ ] Trace all `rejectCommand` / `deferCommand` / final fence branches in `human-command-dispatcher.service.ts` and both existing send reconciliation paths.
- [ ] Implement the lease-protected atomic terminal cancellation + attempt release and a small reusable reconciliation service/port.
- [ ] Integrate only terminal pre-provider failure paths; preserve transient retry and provider-permit uncertainty fencing.
- [ ] Reconcile historical cancelled-but-claimed rows in bounded, idempotent batches (no new queue, timer or provider send).
- [ ] Cover duplicated dispatchers, lease expiry, crash injection, human-vs-automation race, stale ownership and original-idempotency replay.
- [ ] Prove no Meta send and no recovery credit is consumed for moderation BLOCK/REVIEW_REQUIRED, with actual ledger/admission assertions.
- [ ] Verify structured logging redaction and report the migration dependency/gitlink in Completion Report.

## Interfaces / Contracts

- Canonical DB claim/release: `ARCH-040-DATABASE-006` (newly permitted pre-provider relinquishment only).
- Existing services: `MerchantSendCommandService`, `HumanCommandDispatcherService`, `RecoveryFollowUpPolicyService.claimSequenceTwo`, `RecoveryFollowUpBillingService`, `OutboundSendFenceService`, `HumanSendReconciliationService`, `ModerationAssessmentService`.
- Existing persisted objects: `whatsapp.MerchantConversationSendCommand`, `commerce.RecoveryOutreachAttempt`, `whatsapp.ConversationModerationAssessment`, `whatsapp.ConversationMessage`.
- No new platform-specific queue/API/shared payload: Shopify and Woo/API remain command producers and readers; Background remains sole worker/provider-dispatch owner.

## Dependencies

- `ARCH-040-DATABASE-006` — new schema/release gate, currently Ready but not yet Complete.
- `ARCH-040-BACKGROUND-002` — current production worker wiring, Complete.
- `ARCH-040-BACKGROUND-006` — moderation gating and assessment service, Complete.

## Enables

- `ARCH-040-SYSTEM-TEST-001` — one shared follow-up and credit safety.
- `ARCH-040-SYSTEM-TEST-002` — Shopify moderated HUMAN follow-up end to end.
- `ARCH-040-SYSTEM-TEST-003` — Woo/API moderated HUMAN follow-up end to end.

## Acceptance Criteria

- [ ] BLOCK/REVIEW_REQUIRED of an already reserved HUMAN template: original command becomes terminal `CANCELLED`, single sequence-two claim is released, no provider request/permit/outbound message or settled recovery credit exists.
- [ ] Retryable moderation failure retains the same command and attempt, performs no Meta request, and does not release early; eventual ALLOW follows normal send/credit path once.
- [ ] Separate eligible new HUMAN command or scheduled AUTOMATION can claim the same sequence-two row after release; two simultaneous claims yield one winner and no double send/credit.
- [ ] Original cancelled command replay remains cancelled; duplicate cancellation/reconciliation yields idempotent no-op; no mutation of new claimant under ABA or stale leases.
- [ ] Provider `DISPATCH_ADMITTED`, `UNKNOWN`, `SENT`, message-linked, or credibly submitted attempts are never made available by this repair, irrespective of later outcomes.
- [ ] Moderation denial, suspended shop, stale control/recovery, final-fence refusal and crash recovery all use the safe shared release policy where pre-provider, without broadening existing send admission.
- [ ] Recovery and claim state remains correctly tenant scoped and source-independent (Shopify and Woo).
- [ ] Shared structured logs contain safe bounded identifiers/reasons and exclude sensitive content or raw exceptions.

## Validation

- [ ] `npm run test:arch040-recovery-conversation`
- [ ] `npm run test:arch040-background-wiring`
- [ ] `npm run test:arch040-moderation`
- [ ] `npm run test:arch040-background-runtime:postgres`
- [ ] `npm run test:arch040-moderation:postgres`
- [ ] Add focused `tests/unit/services/recovery-conversation/*` tests for release, recovery and races.
- [ ] Add disposable PostgreSQL tests to `tests/integration/recovery-human-dispatch.integration.test.ts` (or a dedicated companion file) for real triggers, claim reuse and credit/provider non-effects.
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `git diff --check` and canonical launcher task-worktree/synchronisation evidence.

## Stop Condition

Once the defined Work Items, Acceptance Criteria and required Validation pass, record exact results in the Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not begin the system-test tasks or unrelated platform work.

## Implementation Notes

The current dispatcher evaluates moderation before its *own* attempt claim, but **not before the producer's acceptance-time claim**; avoid falsely concluding that reservation cleanup is unnecessary. The accepted provider-permit fence is one-way and must remain so. Do not mark this task ready until DATABASE-006 is accepted and its generated Prisma version is available in Background.

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

The 2026-10-18 supplied codebase/accepted task statuses are the definition baseline. Live Git preparation must verify canonical worktrees and dependencies.

### Unresolved Issues

DATABASE-006 must be architect-accepted before execution.

### Architectural Concerns

Do not weaken one-way provider fences or accepted-command immutability to clear a claim. Any missing DB primitive goes back to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation, receipt/billing invariant proofs and PostgreSQL contention evidence.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

After acceptance, independent ARCH-040 system tests validate runtime behavior with real ingress and provider fakes.
