---
id: ARCH-028-BACKGROUND-013
architecture_id: ARCH-028
title: Settle uncertain recovery dispatches from durable admission without resending
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-004
  - ARCH-028-BACKGROUND-009
  - ARCH-040-BACKGROUND-008
enables: []
created: 2026-10-22
updated: 2026-10-22
---

# Settle uncertain recovery dispatches from durable admission without resending

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

**Blocked design gate:** The proposed merchant policy charges an admitted provider attempt even if Meta returns no response; the architect has not yet resolved whether *durable final dispatch admission* (which is before HTTP) is an acceptable billable uncertainty boundary. This task must not be claimed or implemented while blocked. It must not be used to expand provider-FAILED compensation beyond `131026` without an approved separate architecture/Database amendment.

## Objective

Converge recovery-credit reservations exactly once after an *admitted but uncertain* WhatsApp dispatch or worker crash, using existing source owners and a durable, Shop-checked send-to-reservation association, **without resending to Meta or fabricating delivery evidence**.

## Context

The 22 October Background snapshot has both automated recovery sends and ARCH-040 merchant recovery follow-ups. `OutboundSendFenceService.admitFinalSend` persists `providerDispatchAdmittedAt` **before** provider HTTP; automated `RecoveryOutreachAttempt.outboundMessageId` is ordinarily linked only after confirmed send, whereas the HUMAN follow-up command links its attempt at admission. The lifecycle currently marks uncertain recovery usage `AMBIGUOUS`, and `HumanCommandDispatcherService.reconcileExpiredPermits` marks expired commands `UNKNOWN` without committing the associated recovery credit. The original system-test scenarios recorded safe *containment*, not exact settled billing.

Requested policy is immediate commitment after actual attempted dispatch and eventual commitment after a crash, with definitive rejection/release. Those two guarantees cannot be proven simultaneously from a pre-HTTP admission timestamp. **Proposed resolution, awaiting explicit merchant/architect agreement:** treat the durable final dispatch-admission transaction as the accounting boundary for unknown provider outcomes; acknowledge the rare crash-before-HTTP charge possibility. This boundary is not proof of provider contact or delivery. If that trade-off is rejected, uncertain crashes require a separate evidenced/authorised resolution mechanism rather than unconditional commitment.

Confirmed post-acceptance `FAILED` compensation remains owned by ARCH-028-BACKGROUND-004 (generic) and BACKGROUND-009 (purchased), currently only for code `131026`. Recipient suppression remains specific to `131026` under BACKGROUND-011. Any wider authoritative `FAILED` predicate first needs a reviewed architectural rule, truthful Database compensation reason and corresponding changes to those owners.

## Scope

- Reuse final durable provider admission and immutable recipient/dispatch key as the candidate accounting fence; distinguish not-admitted, admitted-uncertain, confirmed Meta acceptance and definitive rejection using persisted evidence.
- Establish exactly one durable recovery attempt -> outbound message/merchant send command -> `UsageReservation` source association **before** provider I/O. Use existing fields/constraints when sufficient; return any required schema constraint/index or compensation reason to `moda_database` for a separate task, never modify Prisma schema in Background.
- Handle automated initial and scheduled recovery-template follow-up sends plus merchant-initiated `RECOVERY_FOLLOW_UP_TEMPLATE` when an exact recovery-credit source was reserved; exclude ordinary `HUMAN_TEXT` and non-recovery conversations.
- Under the *approved* billing boundary, commit the same lifetime-Free, paid-included, promotional or purchased source once for a caught uncertain response; handle both `RESERVED` and already-`AMBIGUOUS` reservations using source-specific, race-safe transitions and one original positive UsageEvent.
- Repair eligible admitted-but-unsettled sources on restart using existing Background worker/dispatch reconciliation where possible, including human `DISPATCH_ADMITTED -> UNKNOWN` and automated stalled-job paths. Source/Shop locks/CAS prevent simultaneous normal finalisation and repair from double-committing.
- Release a source only for a proven pre-provider denial or definitive rejection according to the accepted boundary; if a late definitive failure conflicts with an already-committed repair, use the existing exact correction authority rather than invalidly releasing COMMITTED usage. Do not alter reachability classification.
- Use existing Shared structured logging for bounded branch/lineage/correction results; preserve the immutable no-repeat Meta send fence and leave provider status (including a missing provider message ID) unconfirmed when no acceptance evidence exists.

## Out of Scope

- A new compensation ledger, source owner or purchased refund procedure; broader confirmed `FAILED` correction belongs to BACKGROUND-004/009 only after separate approval.
- Any non-`131026` reachability suppression or phone-based provider-callback association.
- New queue contract, provider resend, provider lookup by phone/time, fabricated provider ID or `DELIVERED` receipt.
- Generic HUMAN_TEXT credit charging, new merchant users/roles, or unrelated moderation/follow-up eligibility changes owned by ARCH-040.
- Schema/migration changes in this Background task, and edits to System-Test scenario PASS records.

## Requirements

- [ ] A precise approved billable uncertainty boundary is documented in ARCH-028 before implementation. If durable pre-HTTP admission is selected, explicitly record its crash-before-HTTP exposure; do not equate admission with proof that HTTP started.
- [ ] No `UsageReservation` moves from mere reservation to committed accounting without a durable exact Shop/recovery/attempt/recipient/message/source association and the selected boundary evidence.
- [ ] Direct timeout, lost response, ambiguous send and crash repair converge to one committed source and one positive UsageEvent; not a second provider call. Missing evidence fails closed with a bounded diagnostic.
- [ ] Pre-admission denial and definitive rejection do not leave an uncorrected charged credit; no provider call or second send occurs on replay.
- [ ] Original source/period/provider (`SHOPIFY` or `WOOCOMMERCE`) and purchased refund holds are preserved; no new financial make-good or monetary refund.
- [ ] A credit committed due to uncertainty does not imply provider `SENT`, `DELIVERED`, `READ`, delivered-message usage or a fabricated provider ID.
- [ ] Human free-text cannot be charged against recovery capacity and all Shop/recipient identity boundaries remain enforced.
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines, MUST NOT exceed 300; existing >300-line modules receive only thin integration edits; independent policy/accounting/repair responsibilities remain separate.

## Work Items

- [ ] Obtain and record the accounting-boundary decision; confirm existing schema can express durable pre-I/O attempt/message/source lineage or define a Database-owned prerequisite before re-promoting.
- [ ] Integrate automated initial/follow-up and HUMAN recovery-template dispatch into exact pre-I/O source lineage; retain current final provider fence and no-repeat policy.
- [ ] Implement source-specific idempotent transition from RESERVED/AMBIGUOUS to COMMITTED using original UsageEvent and counters, without creating a duplicate or changing the reservation's credit source.
- [ ] Implement restart/lease-expiry repair for both automated and human template admitted-unknown sends, with safe pre-admission/definitive-failure handling and no Meta resend.
- [ ] Add deterministic fault injection at pre-fence, post-fence/pre-HTTP, HTTP timeout, response persistence and normal-credit-finalisation boundaries.
- [ ] Verify concurrency, provider-status precedence, purchased refund holds, multi-Shop isolation, Shopify/Woo provider attribution, and ordinary HUMAN_TEXT exclusion.
- [ ] Run the task-specific Background validation and record durable before/after evidence; return System-Test scenario expectations to the owning test task, without mutating its historical results.

## Interfaces / Contracts

- `OutboundSendFenceService`/`ConversationMessage.providerDispatchKey` and `providerDispatchAdmittedAt`; HUMAN `MerchantConversationSendCommand` permit/attempt association; automated `RecoveryOutreachAttempt` and original billing reservation/source key.
- Existing Free/paid/promotional/purchased reservation services and negative-correction owners BACKGROUND-004/009. No competing Shared schema or local generic logger.
- ARCH-040-BACKGROUND-008 final permit/verified-window integration is a prerequisite because it changes the same dispatch boundary. ARCH-040-BACKGROUND-007 is transitive via 008.
- Provider `FAILED/131026` status/compensation remains an independent confirmed-outcome path; no unknown-ID callback can establish Shop or attempt lineage alone.

## Dependencies

- `ARCH-028-BACKGROUND-004`
- `ARCH-028-BACKGROUND-009`
- `ARCH-040-BACKGROUND-008`

An additional Database-owned dependency must be defined and accepted if the inspected existing columns cannot enforce the exact admitted-message/attempt/source association; no placeholder task ID is treated as accepted. This task remains Blocked pending the accounting-policy decision even after the listed prerequisites become Complete.

## Enables

None currently. After the policy/schema gate is resolved, `moda_architect` should define a *separate terminal settlement system-test task* requiring BACKGROUND-013 and its accepted prerequisites, without making any implementation task depend on system tests. Keep ARCH-028-SYSTEM-TEST-001 scoped to the original `131026` policy.

## Acceptance Criteria

- [ ] A no-response outcome with accepted admission evidence commits exactly one original recovery source without a second Meta call; the message remains unconfirmed when no provider response exists.
- [ ] Crash at each tested boundary is restart-safe, including the acknowledged pre-HTTP admission edge under the explicitly approved merchant policy.
- [ ] RESERVED/AMBIGUOUS/COMMITTED and competing worker interleavings never double-charge, double-release or leave a settled source reserved indefinitely.
- [ ] Definitive rejection or pre-admission denial does not leave a net charged credit; committed repair corrections, where required, remain exact/idempotent.
- [ ] Automated initial, scheduled sequence-2 and human sequence-2 template paths settle correctly; ordinary HUMAN_TEXT never consumes recovery capacity.
- [ ] Purchased refund holds, historical-only rules, original Shop/provider, reporting exclusion and outbound-hard-limit semantics remain correct.
- [ ] Duplicate/out-of-order FAILED/DELIVERED/READ or unknown provider-ID callbacks cannot override status precedence, fabricate a receipt or infer ownership from phone numbers.
- [ ] No new ARCH-028 production source exceeds 300 lines; focused validation, appropriate Background tests/build and `git diff --check` pass.

## Validation

- Focused unit/PostgreSQL integration for all four credit sources and both platform providers; include idempotency/multi-worker races, exact lineage and purchased refund-state variants.
- Deterministic worker-kill/restart, lease expiry, lost provider response and replay tests across automated and HUMAN follow-up. Verify no Meta resend and no fake provider success.
- Actual repository-declared relevant tests/build/lint and `git diff --check`. Record any environment limitations. Integrated black-box release evidence belongs to a separate System-Test task.

## Stop Condition

After defined work, acceptance and validation are complete, set status `review`, fill the Completion Report, return to `moda_architect` and STOP. No implementation code, status acceptance or `docs/decisions/**/_index.md` update is authorised while the task is Blocked.

## Implementation Notes

Prefer one thin settlement coordinator consuming exact existing source owners, with focused admission-lineage and restart-repair collaborators. Reuse the existing background scheduler/poller where justified; do not add a queue solely to perform a process-local repair. Do not call Meta, Redis or any other external endpoint inside the database transaction. The `providerDispatchAdmittedAt` evidence must be interpreted consistently across automated and HUMAN follow-up paths, even though their creation/linkage timing differs in the supplied snapshot.

## Completion Report

### Status

Not Started — blocked on accounting-boundary approval and any proven Database precondition.

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

Approval of the billable durable-admission boundary versus evidence-based resolution; durable pre-provider automated attempt/message/source association; any necessary Database constraint/migration.

### Architectural Concerns

No new compensation reason is silently assumed. Generic non-`131026` confirmed delivery failure remains outside the approved ARCH-028 correction policy.

## Architect Review

### Review Status

Blocked — architectural clarification and prerequisite ownership; this is **not** an
implementation review or an accepted task attempt. Attempt remains `0` and no
implementation claim or completion is authorised.

### Review Notes

Architect review of the supplied 2026-10-22 workspace snapshot and the
`RECOVERY-PROVIDER-SETTLEMENT-ACCEPTANCE.md` black-box handoff identifies the
following required corrections before this task can become Ready:

1. **Make the billable dispatch boundary coherent.**
   `OutboundSendFenceService.admitFinalSend` persists
   `ConversationMessage.providerDispatchAdmittedAt` before the Meta HTTP call.
   A process may die between those two operations. The durable marker proves
   dispatch *admission*, not that an HTTP request was actually attempted.
   Automatic crash settlement cannot simultaneously guarantee both (a) never
   charge for a request not actually attempted and (b) commit every crashed
   admitted operation without later provider evidence. Record an explicit
   merchant-policy decision: either durable dispatch admission is the billable
   uncertainty boundary (including the small crash-before-HTTP window), or
   insufficiently evidenced cases require a separate authorised resolution
   path. Do not present a pre-HTTP marker as proof of provider contact.
2. **Persist exact recovery lineage before provider I/O.** For automated initial
   and follow-up sends, the current `RecoveryOutreachAttempt.outboundMessageId`
   association is normally finalised after confirmed Meta acceptance. The
   already-persisted outbound UsageEvent/idempotency key alone is not an
   explicit attempt foreign key. Require a durable, tenant-checked one-to-one
   message/attempt/reservation-source association at the approved dispatch
   boundary, before HTTP, so crash repair can identify the original Free,
   paid-included, promotional or purchased source without a guessed source key,
   current billing-policy reclassification or provider-ID fabrication. Assess
   whether existing columns suffice before proposing new ones.
3. **Do not conflate failures before and after the dispatch fence.** The current
   recovery send catch can observe database, revalidation and provider errors;
   `RecoveryReservationLifecycleService.handleProviderFailure` calls
   `markAmbiguous` for any non-definitive error. Distinguish pre-permit failures
   (release/no charge), definitive HTTP rejection (no net charge) and admitted
   uncertain outcomes (the selected billing policy). On retry/restart, protect
   in-flight dispatches and use the existing immutable dispatch fence so that
   no second Meta call can be authorised.
4. **Assign the Database-owned amendment first.**
   `billing.UsageReservationCompensationReason` currently has only
   `WHATSAPP_RECIPIENT_UNDELIVERABLE`; do not record a general authoritative
   `FAILED` delivery correction under that inaccurate reason. Define a bounded,
   additive reason/provenance migration and any proven repair index or required
   attempt-link constraint in a separate `moda_database` task; validate fresh
   migration, all source types and exact Shop/UsageEvent lineage. No schema
   changes are authorised inside BACKGROUND-013.
5. **Reuse and amend the unfinished compensation owners.** BACKGROUND-004 and
   BACKGROUND-009 currently compensate `FAILED/131026`, with purchased-credit
   correction isolated to BACKGROUND-009. If broader correlated authoritative
   `FAILED` compensation is approved, extend those pending/Ready task contracts
   before implementation, or explicitly justify a separate small owner. Do not
   put a second generic/purchased compensation engine in BACKGROUND-013.
   Keep suppression classification/writes limited to `131026` in
   BACKGROUND-011/006, while separately defining when generic failed delivery
   reverses outbound hard-limit usage and sends a merchant notice. A late
   `DELIVERED`/`READ` must retain the accepted status-precedence semantics.
6. **Rework scope and dependencies.** BACKGROUND-013 currently combines durable
   dispatch authority, uncertain-credit settlement, crash-repair operation and
   general purchased/generic failure compensation, and depends on
   BACKGROUND-004 and BACKGROUND-009 without the necessary Database gate.
   Narrow it to one reviewable dispatch/uncertainty-settlement capability
   (including its directly necessary repair path), or split further if the
   actual implementations require distinct failure ownership. Recompute
   dependencies without cycles, promote tasks only when all dependencies are
   architect-accepted Complete, and preserve the no-system-test-dependency
   invariant.
7. **Reconcile black-box acceptance under System-Test ownership.**
   `RECOVERY-PROVIDER-SETTLEMENT-ACCEPTANCE.md` currently expects held
   `AMBIGUOUS`/`RESERVED` decisions, escalation and evidence-based review.
   `RECOVERY-PROVIDER-AMBIGUOUS-001`, `RECOVERY-PROVIDER-CRASH-001`,
   `RECOVERY-PROVIDER-UNKNOWN-ID-001` and `MESSAGING-STATUS-001` passed against
   old behaviour. Their acceptance criteria and the planned
   `RECOVERY-PROVIDER-SETTLEMENT-001` executor must be separately reconciled by
   `moda_system_test` *after* the production design is accepted; preserve
   historical PASS evidence and do not manufacture fresh PASS results. Ensure
   the ARCH-028 system-test dependency frontier includes the final settlement
   implementation and that the authenticated merchant view distinguishes an
   accounting commitment from a verified delivery receipt.
8. **Normalise the task file before execution.** Restore the canonical task
   headings (`Context`, `Out of Scope`, `Requirements`, `Interfaces / Contracts`,
   `Dependencies`, `Enables`, `Implementation Notes`, `Completion Report`, etc.)
   with a bounded objective, focussed acceptance criteria and source-owned
   validation. The current proposal's informal headings do not meet the
   task-file format policy. Preserve the original problem/evidence, with this
   review as the latest rework contract.

### Reviewed Files

- `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`
- `docs/decisions/background/ARCH-028/BACKGROUND-004-*.md`, `BACKGROUND-009-*.md`
- `moda-interact-background/src/services/recovery-billing/recovery-reservation-lifecycle.service.ts`
- `moda-interact-background/src/services/recovery-conversation/outbound-send-fence.service.ts`
- `moda-interact-background/src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `moda-interact-background/src/services/checkout-recovery/recovery-outreach-finalization.service.ts`
- `moda-interact-background/src/services/whatsapp-provider-status.service.ts`
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-system-test/docs/RECOVERY-PROVIDER-SETTLEMENT-ACCEPTANCE.md`

### Validation Reviewed

Source/task inspection and existing recorded black-box results only. No new
implementation, tests, Git branches, worktrees, commits or pushes were executed
in the developer workspace. This portable review patch is documentation-only.

### Architecture Conformance

Not yet conformant: the proposed compensation eligibility exceeds the agreed
`131026` scope, and the claimed actual-dispatch/crash billing invariant cannot
be established using the current pre-I/O admission timestamp alone.

### Follow-up

Keep BACKGROUND-013 Blocked until the billable linearisation point is explicitly
agreed and the parent architecture, Database amendment, existing compensation
owners and system-test handoff are reconciled. Then re-materialise/update the
canonical task, calculate the dependency graph and promote to Ready when valid.

### Task-definition reconciliation (2026-10-22, no implementation acceptance)

The task now has the canonical sections, a bounded uncertain-send/repair objective, and a new ARCH-040-BACKGROUND-008 final-dispatch dependency. General post-acceptance FAILED compensation is deliberately kept with BACKGROUND-004/009 and the existing `131026` scope. The original review concerns about the durable admission/accounting boundary and any necessary database-owned lineage remain **unresolved**. Status stays Blocked; Attempt 0 has not been claimed, tests have not run, and no implementation has been accepted. The original review notes above are retained as the historical correction contract.
