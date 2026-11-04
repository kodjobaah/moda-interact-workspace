---
id: ARCH-056-BACKGROUND-004
architecture_id: ARCH-056
title: Continue candidate and initial-recovery finalization from durable progress
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-056-BACKGROUND-002
- ARCH-056-BACKGROUND-003
- ARCH-028-BACKGROUND-012
- ARCH-050-BACKGROUND-002
- ARCH-050-BACKGROUND-003
- ARCH-052-BACKGROUND-018
- ARCH-053-BACKGROUND-005
enables:
- ARCH-056-SYSTEM-TEST-001
created: '2026-11-03'
updated: '2026-11-04'
---

# ARCH-056-BACKGROUND-004: Continue candidate and initial-recovery finalization from durable progress

## Architecture

Parent architecture: `ARCH-056`. Task touchpoint: the existing Background candidate/materialization, initial-outreach orchestration and confirmed-finalization entry points. This task consumes the accepted billing and outbound boundary contracts; it does not own those implementation files.

## Objective

Make the real pending-candidate execution continue the same initial recovery generation after an interrupted preparation or finalization. Classify durable progress before new template/billing admission; resume only a proven unpermitted message; hold provider uncertainty; and replay confirmed bookkeeping through the exact billing and atomic Support owners. A successful job must not mean that a required-state exception was swallowed by an existing `DETECTED`/`MESSAGE_SENT` short circuit.

## Context

Optional prior evidence, if present, is `docs/architecture/reviews/background-database-20261103-212722-phase3/recovery-progress.md` and its U2/C3 matrix. It is not an execution prerequisite; the source boundaries and complete failure matrix are specified below. Read the actual worker and materializer rather than relying on direct-initiation mock tests. The current materializer returns `no-op-existing` for ordinary `DETECTED`/`MESSAGE_SENT`/`ENGAGED` recovery rows; the neutral fallback queries the usage identity as a provider-dispatch key; current initiation asks for a fresh template/credit before canonical receipt lookup; finalization has distinct billing, Support, status, and queue boundaries. The accepted ARCH-055-BACKGROUND-001 persisted sequence-two/follow-up interface is a preservation constraint; this task does not change that interface or add a new dependency edge to it.

## Scope

Modify only these production files, relative to `moda-interact-background/`:

- `src/services/checkout-recovery.service.ts` — composition and additive continuation entry only.
- `src/services/checkout-recovery/recovery-materialization.service.ts`
- `src/services/checkout-recovery/recovery-initiation.service.ts`
- `src/services/checkout-recovery/recovery-outreach-finalization.service.ts`
- `src/services/checkout-recovery/recovery-initial-outreach-support-notice.service.ts`
- `src/services/checkout-recovery/recovery-initial-outreach-support-notice.contracts.ts`
- `src/workers/pending-recovery-candidate.worker.ts`
- `src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `src/services/recovery-template-integration/initial-no-offer-fallback.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts` — actual initial finalizer and its billing port only; preserve no Woo follow-up scheduling.

No new production module, recovery attempt service, background scanner, queue, table, endpoint, billing policy, package script, or alternate Support writer is required. BACKGROUND-003 owns outbound admission/delivery/fences and the Woo sender adapter. BACKGROUND-002 owns credit source resolution and credit mutations. This task owns the focused unit/integration tests for its service and actual-worker paths, including the existing ARCH-052 Shopify neutral-template integration test.

This task owns the following existing test files for contract/mock updates and focused assertions:

- `tests/unit/workers/pending-recovery-candidate.worker.test.ts`
- `tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts`
- `tests/unit/services/checkout-recovery/recovery-initial-outreach-support-notice.service.test.ts`
- `tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts`
- `tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts`
- `tests/integration/arch052-shopify-initial-no-offer-dispatch.integration.test.ts`
- `tests/integration/recovery-initial-outreach-support-notice.integration.test.ts`

Create exactly these focused test modules and fixture file:

- `tests/unit/services/checkout-recovery/initial-outreach-progress.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-confirmed-initial-settlement.test.ts`
- `tests/integration/initial-outreach-progress.integration.test.ts`
- `tests/integration/initial-outreach-progress-worker.integration.test.ts`
- `tests/integration/fixtures/initial-outreach-progress.fixture.ts`

Read-only production/test dependencies (not edit permission):

- `src/services/recovery-billing.service.ts`
- `src/services/recovery-billing/recovery-billing.types.ts`
- `src/services/outbound-whatsapp-admission.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-whatsapp-admission.types.ts`
- `src/services/recovery-outreach-attempt.service.ts`
- `src/services/recovery-outreach-follow-up.service.ts`
- `src/services/pending-recovery-candidate.service.ts`
- `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`
- `src/services/woocommerce-recovery/woo-guarded-initial-sender.service.ts`
- `src/services/woocommerce-recovery/woo-resumed-outreach-settlement.adapter.ts`
- `src/services/woocommerce-recovery/woo-recovery-composition.ts`
- `database/prisma/schema.prisma`
- `tests/unit/services/woocommerce-recovery/woo-recovery-composition.test.ts`
- `tests/integration/arch055-follow-up-identity.integration.test.ts`

## Out of Scope

Covers U2 and C3 together at their real candidate/initiation/finalization touchpoint, using BG003 admission support and BG002 exact credit settlement. It includes the required-state versus optional-enrichment error distinction and narrow consumer wiring for Woo. It does not establish eventual automatic repair after job loss/exhaustion, general AI consumer completion, arbitrary legacy FAILED reset, unknown-provider recovery, new non-131026 compensation, general paid historical settlement, automatic policy/settings reactivation, or O7 read optimization.

## Requirements

### Real candidate and initiation routing

Within the existing checkout lock, perform persisted identity/progress classification before the existing new-send eligibility/order/supersession/template gates. Validate tenant and Shopify source first. Reconciliation of a confirmed receipt may run when the current shop is paused, a new-send plan gate denies, STOP exists, an order has completed, or the recovery became terminal; it performs no provider work and must not downgrade current terminal/engaged state.

For `needs-preparation`, enforce all existing current execution, processed-order, supersession, checkout lifetime, recipient, stored consent, STOP/reachability, suppression, capacity and offer-token conditions before provider admission. Preserve current first-insert consent behavior and the existing special suppression wake-up/retry owner. Continue the same recovery generation and same sequence-one attempt. An ordinary interrupted `DETECTED` row cannot be converted to `no-op-existing`. A true later expired-generation lifecycle remains with its existing owner; this repair must not synthesize a new generation to escape failed initial progress.

Perform the same early durable classification in direct initiation. In particular, a linked `WAITING_FOR_RESPONSE` attempt after a Support commit bypasses fallback/template preparation and new billing admission. A confirmed message with incomplete credit/Support/status work re-enters finalization; a `MESSAGE_SENT`/`ENGAGED` recovery with existing due follow-up re-enters the existing scheduling function.

For a proven unpermitted pending message, obtain `revalidateExistingInitialOutreach` for that exact message and reservation, prepare through existing current checks, and call BACKGROUND-003's `resumeInitialTemplate`. For a reserved credit before message creation, call the same billing port with explicit null and reuse its admission. Only a proven absent source goes through `billing.admit`. New initial sends carry the initial scope and exact returned credit key to BACKGROUND-003's fence. A duplicate return is followed by another canonical read; it is never treated as success or always-uncertain merely because the row exists.

After any sender exception, classify durable progress before accounting/attempt mutation. A technical exception before a permit does not prove provider failure; retain resumable evidence and rethrow the original error. A permit with no confirmed outcome holds and is never resubmitted. Preserve 131026's authoritative path. Only proven pre-permit refusal or authoritative provider rejection may mark the attempt failed/release under the existing exact owner. Remove the unconditional `FAILED/PROVIDER_FAILURE` transition for every non-131026 exception. A local receipt-persistence error after provider success remains uncertainty with its original error.

### Neutral fallback and required-state semantics

Replace the fallback's query using `providerDispatchKey = recovery-outreach:<attemptId>` with the shared scoped canonical admission lookup. Use the real Shopify/Woo key formats in tests. Do not reimplement usage/attempt/message joins in fallback, and do not call fallback at all for confirmed progress.

Keep optional offer/AI/MCP enrichment unavailable as the existing approved neutral-template opportunity. Distinguish a genuine business/configuration absence from a required-state technical failure. A lifetime policy reader outage, SQL failure, or moderation technical retry propagates a retry signal with the original error/cause; the automated facade's outer lifetime-unavailable branch must not return ordinary `CHECKOUT_UNAVAILABLE` for a dependency outage. Missing/invalid required runtime configuration is an explicit technical retry with a bounded reason when no original exception exists. Preserve actual eligibility denial/lifetime elapsed as refusal, not an artificial technical retry.

Business/configuration blocks may complete the current candidate processing only with their real recorded/logged disposition; they are not a confirmed send. This task does not add an automatic settings-change reactivation scanner. A released/failed/ambiguous legacy credit remains held unless its accepted existing owner supplies a sanctioned transition. Do not optimize the broader O7 repeated preparation reads as additional scope.

Keep the fallback port's existing union for semantic outcomes with no originating exception. Unexpected database/SDK failures and actual lifetime missing/invalid exceptions must instead reach the caller as the original exception after their declared local diagnostic. The facade must not populate a new required-state retry's cause from an unrelated optional offer originatingError; that optional failure has its own degradation/source event. A safe originating diagnostic is emitted even when neutral preparation succeeds. This does not add a generic error envelope or persist source bodies.

### Confirmed settlement and partial-finalization replay

Execute the existing boundaries in this order: exact confirmed billing settlement; atomic initial attempt plus optional Support notice; conditional recovery status update; eligible deterministic follow-up publication. No encompassing transaction spans provider/queue I/O.

The atomic Support finalizer must first read the exact Shop/recovery/attempt routing pointer without mutation, acquire that Shop FOR KEY SHARE, then take its existing initial-attempt FOR UPDATE and reread/validate unchanged ownership. Preserve all input/receipt/tenant predicates. Do not lock a different Shop after the attempt if the pointer changed; reject the conflict. This order is required because first-thread and notice insertion acquire immediate Shop/CheckoutRecovery FK locks: a final fence must not hold Shop FOR UPDATE (and Woo's Recovery lock) while waiting for the attempt held by this writer. Pre-acquiring Shop KEY SHARE excludes that fence before it can hold descendants. It adds no new policy, schema, independent Support writer or cross-boundary transaction.

1. Use only the settled billing result and its actual message/sentAt identity. A held result returns held without any Support notice, success status, or follow-up publication. A commit that affected zero/non-COMMITTED credit state is not success.
2. Preserve the atomic Support writer, unique `recovery-initial-outreach:v1:<attemptId>` source key, disabled-notification behavior, no replay backfill, and exact receipt identity checks. Do not write Support independently or reset the attempt in an earlier transaction.
3. Allow one narrow historical false-failure repair inside that same Support transaction: sequence-one `INITIAL` AUTOMATION attempt, `status = FAILED`, `failureCode = PROVIDER_FAILURE`, no closedAt, sentAt, outbound link or due date, exact canonical owned UsageEvent pointing to this confirmed message, and no conflicting attempt link. The caller must already have a settled exact credit. Read and CAS these predicates while holding the existing attempt lock; atomically transition to `WAITING_FOR_RESPONSE`, set the confirmed message/time/due, clear that stale failureCode, and insert the optional notice. Do not allow genuine rejection, 131026, CANCELLED, HUMAN, sequence-two, or ambiguous-credit reset. If these exact guards fail, hold visibly rather than generalizing the reset.
4. An already finalized attempt retains its **persisted followUpDueAt, including null**. Never use `storedDue ?? newlyDerivedDue` to turn a deliberate null into a new job after a policy toggle. Derive due time only at the first supported atomic finalization. Replays validate the exact existing message/time/due.
5. Update recovery only with `id`, shop ownership and `status = DETECTED` predicates; write actual receipt sentAt. Never overwrite COMPLETED, CANCELLED, EXPIRED or ENGAGED to MESSAGE_SENT. A zero-row status update triggers a current-state read/interpretation, not an assumed successful transition.
6. Reuse `ensureScheduledInitialFollowUp` and its persisted state guards/job identity. Retry queue publication after SQL finalization failure boundaries using the same due date and deterministic job. Existing current eligibility, responded-at, terminal, follow-up/sequence-two guards still apply. No new policy or second sequence-one attempt is introduced.

### Progress diagnostic ownership

Apply the parent architecture's mandatory revision-2 logging acceptance contract. Keep the actual thrown exception/cause intact; log safe source wording with real supplied Prisma code/clientVersion and the permitted metadata, never an entire meta/query/payload. The inspected Shared Error serializer omits causes and aggregate children, so explicit component messages are mandatory below. Tests import the actual locked installed Shared logger and record its version/resolution.

Use per-invocation stage and identity state, not mutable fields shared by concurrent calls. Include only available shop/recovery/attempt/message/job identity. Retain source-provided request IDs where available; do not add a tracing protocol or copy raw provider responses downstream. The Meta adapter and protected moderation source remain the owners of their detailed source diagnostics.

| Selected boundary | Stable event and owner | Required emitted evidence |
|---|---|---|
| Received optional failure followed by neutral fallback | Facade, new `recovery_template.initial_fallback.degraded` | Warn before PREPARED/BLOCKED/RETRY conversion with trigger, stage, known IDs and received safe source diagnostic when one exists. A typed failure without an exception retains its reason and creates no providerError. |
| Actual required-state fallback exception | Existing `recovery_template.initial_fallback.failed`, with existing facade error context | Log the actual safe required-state error and rethrow that same exception. Do not substitute an optional-enrichment cause or hide it in a reason-only retry. |
| Continuation failure before the established finalization stages | Initiation, new `recovery.initial_outreach.progress.failed` | Stage `classification`, `preparation`, `credit_revalidation` or `dispatch`, safe actual diagnostic and known IDs, including direct service entry. Original exception remains the thrown value. |
| Typed progress hold or business block | Continuation, new `recovery.initial_outreach.progress.held` and `.blocked` | Warn with actual reason, optional creditReason and known IDs. No invented originating exception, provider response or successful completion. Held work remains visible under the existing bounded retry contract. |
| Billing/Support/recovery-status/follow-up error | Existing Shopify/Woo finalization and atomic Support failure events | Retain safe original message and exact existing stage. Keep validated IDs, original throw identity and best-effort sink behavior; do not duplicate source response bodies. |
| Woo outreach contextual failure | Existing `woocommerce.recovery.outreach.failed` | Replace generic-only failed() diagnostics with safe actual source wording plus existing stage/IDs. Keep privacy and unchanged exception propagation; do not modify resumed-settlement policy. |
| Woo preflight/release or send/compensation double failure | Existing aggregation catch, using `woocommerce.recovery.outreach.failed` | Before throwing the aggregate, emit explicit preflightError/releaseError or sendError/compensationError fields, each retaining an independently bounded safe original message/code. Aggregate-only output is insufficient. |
| Candidate materialization and cleanup both fail | Worker, new `recovery.pending_candidate.processing_cleanup_failed` | Emit explicit materializationError and cleanupError with available queue/job/attempt/shop context before constructing/throwing the composite. Both messages must remain independently visible after Shared serialization. |
| Failed candidate/job or worker error | Existing `recovery.pending_candidate.job_failed`, `.worker_error`, and Woo job failure events | Safe actual boundary diagnostic and available queue/job/attempt/shop context. Retain real listeners in tests and invoke them. Their outer record does not replace source or component diagnostics. |

At every selected aggregation catch, emit the named original components while they are still independently available, then preserve both objects in application propagation. Keep the candidate's existing primary failure/retry-marker behavior; do not rely on a concatenated outer string to expose a cleanup failure. Replace Woo's test that requires total omission of the original diagnostic with a safe-message assertion that retains the harmless wording and excludes sensitive portions. The actual error object remains unchanged for the caller.

Preserve established finalization stage events and sink isolation. Never log a final applied/settled/sent success before its transaction commits, or after a required failure or typed hold. Expected no-error refusals record the actual reason without a manufactured exception. This task does not edit `whatsapp.worker.ts` or its tests; BACKGROUND-001 owns those diagnostic-only changes. No generic logging utility, recursive error-graph serializer, raw stack dump, source parser or Shared version change is authorized.

### Woo boundary and existing architecture preservation

Update the narrow Woo outreach billing/sender ports to consume these accepted methods. Its existing confirmed-message-first handling must use exact confirmed settlement before any new-send gate. The real `finalize.confirmed` adapter is in `woo-recovery-outreach.adapters.ts`; remove its fresh admission input and replace its old commit call with the exact settled/held contract. Return and consume `{kind:"finalized",outboundMessageId,sentAt}` or `{kind:"held",reason}` at that port. Preserve its own atomic Support/status sequence and `followUpDueAt === null` rule; do not route it into a Shopify helper that schedules a Woo follow-up. Prepared-message continuation remains behind its existing `NODE_ENV === test` plus injected test-outbound enablement; production composition remains disabled. Do not add a production enable callback, relax source routing, or fall back to generic `sendTemplate`. Preserve cancellation/resumed-attempt and sequence-two rules; do not take ownership of the separate resumed settlement adapter.

Keep ARCH-028-BACKGROUND-012's options-object API and missing-recipient checkout update semantics. Keep ARCH-028-BACKGROUND-013 blocked uncertainty policy intact. Retain ARCH-050 atomic Support semantics, ARCH-052 approved no-offer content/template contract, and current ARCH-055 sequence-two/follow-up identity behavior.

## Work Items

- [ ] Add the typed durable continuation entry to the existing initiation owner and wire it into the actual candidate path without changing the options-object API.
- [ ] Route confirmed/linked/pending/absent/failed/uncertain evidence before new-send preparation; keep identity checks mandatory and keep new-send guards intact.
- [ ] Consume BG002's exact-source retained-credit and confirmed-settlement results, and BG003's scoped same-message resume; never choose a fresh source on replay.
- [ ] Correct fallback identity lookup and the outer required-state lifetime failure semantics while preserving optional-enrichment neutral fallback.
- [ ] Remove exception-only provider-failure terminalization; preserve original technical errors and distinguish visible holds/business blocks.
- [ ] Replay atomic Support, guarded legacy false-failure repair, recovery status and deterministic follow-up scheduling, preserving finalized null due dates.
- [ ] Migrate the Woo outreach service and its real finalizer adapter without changing the production gate or introducing Woo follow-up.
- [ ] Add actual-worker fault-boundary and service regression tests, run every command, and report the explicit bounded-retry/repair limit.

- [ ] Emit optional degradation before fallback conversion and preserve/log actual required-state exceptions through facade and worker reentry.
- [ ] Replace Woo's generic-only failure diagnostic and emit both fixed-role errors at release/compensation aggregation.
- [ ] Emit materializationError and cleanupError at their candidate aggregation site while retaining existing failure-reason/retry-marker behavior.
- [ ] Add actual installed Shared sink assertions for progress, source-message retention, compound errors, finalization stages and real worker listeners; retain redaction and sink-failure semantics.

## Interfaces / Contracts

Export the following types from the existing initiation module and re-export them through the existing checkout recovery facade:

```ts
type InitialOutreachProgress =
  | { kind: "needs-preparation"; recoveryId: string;
      outreachAttemptId: string | null; outboundMessageId: string | null }
  | { kind: "reconciled"; recoveryId: string;
      outreachAttemptId: string; outboundMessageId: string }
  | { kind: "blocked"; recoveryId: string;
      reason: "pre-permit-refused" | "provider-rejected" | "recipient-unreachable" }
  | { kind: "held"; recoveryId: string;
      reason: "provider-outcome-unknown" | "lineage-conflict" | "credit-held";
      creditReason?: Extract<ConfirmedInitialOutreachSettlement |
        ExistingInitialOutreachCredit, { kind: "held" }>["reason"] };

continueInitialOutreach(input: {
  shopId: string;
  recoveryId: string;
}): Promise<InitialOutreachProgress>;
```

The method verifies the persisted shop/platform/recovery and same sequence-one attempt, delegates canonical message classification to BACKGROUND-003, and completes confirmed bookkeeping where possible. `needs-preparation` is an explicit handoff to the existing current-send preparation path, not completion. It does not create a new generation or fabricate a checkout/customer seed. Missing customer/recipient preparation still uses the accepted current checkout lookup and consent owner.

Export `InitialOutreachHeldError` from the initiation module, with bounded `recoveryId`, reason and optional creditReason. Materializer/direct initial callers convert `held` into this error so the worker cannot acknowledge a held state as complete. A genuine dependency error is rethrown unchanged, rather than wrapped as a semantic hold. Add these materialization result variants:

```ts
{ outcome: "recovery-reconciled"; checkoutToken: string; recoveryId: string }
{ outcome: "deferred-initial-outreach"; checkoutToken: string;
  recoveryId: string; reason: "pre-permit-refused" | "provider-rejected" |
    "recipient-unreachable" }
```

Keep the existing `materializeMaturedCandidate(candidate, options)` options object, `jobId`, `retrySuppressionAdmission`, source routing, missing-recipient update behavior, and ordinary existing result variants compatible. Existing `recovery-created` describes creation of a recovery row; it must never be presented as proof of a successful send. Preserve the public `handleCheckoutCreated` return shape for existing event/suppression/capacity callers while moving shared classification/preparation logic into local helpers as necessary.

Add `finalizeConfirmedInitialOutreach` to the existing finalization service. Its input is the validated recovery, sequence-one attempt state (including status, persisted link/sentAt and nullable due date), confirmed message, and optional follow-up policy; it has **no fresh admission input**. Its result is `{kind:"finalized",outboundMessageId,sentAt}` or `{kind:"held",reason: ConfirmedInitialOutreachSettlement held reason}`. Existing `finalizeConfirmedOutreach` retains its sequence-two behavior; route every selected initial caller through the new method and consume its outcome. A compatibility initial call must not turn a held result into a successful void return.

### Exact billing ports

Consume BACKGROUND-002's exact accepted exports:

```ts
revalidateExistingInitialOutreach(
  input: ExistingInitialOutreachCreditInput,
): Promise<ExistingInitialOutreachCredit>;

settleConfirmedInitialOutreach(
  input: ConfirmedInitialOutreachCreditInput,
): Promise<ConfirmedInitialOutreachSettlement>;
```

`InitialOutreachCreditIdentity` is `{shopId,recoveryId,outreachAttemptId}`; `ExistingInitialOutreachCreditInput` adds `outboundMessageId: string | null`, and `ConfirmedInitialOutreachCreditInput` adds `outboundMessageId: string`. Import these accepted aliases; do not redeclare competing source policy.

`ExistingInitialOutreachCredit` returns `admitted` with the original `RecoveryBillingAdmission` and reservation ID; `absent`; or `held` with the fixed reasons `message-not-pre-permit`, `lineage-conflict`, `reservation-not-reserved`, `reservation-expired`, `source-policy-mismatch`, `paused`, `feature-unavailable`, `contract-required`, `subscription-frozen`, or `paid-period-not-current`. It does not reserve, release, reactivate, or rebind credit. Explicit `outboundMessageId: null` is supplied only after canonical classification proves there is no message. Only `absent` permits the existing fresh `billing.admit`; an exact existing reserved credit is reused. A pending message with missing credit is not absence.

`ConfirmedInitialOutreachSettlement` returns `settled` with disposition `committed`/`already-committed`, exact source kind/key, reservation ID, committed usage ID, message ID and actual sentAt; or `held` with `message-not-confirmed`, `lineage-conflict`, `reservation-ambiguous`, `reservation-released`, `reservation-compensated`, `paid-period-not-current`, or `settlement-not-committed`. Only settled permits Support/attempt/status progress. No `billing.admit`, current source substitution, offer preparation, provider call, or pre-provider release runs on a confirmed replay. Both billing methods preserve unexpected original exceptions.

Do not automatically commit `AMBIGUOUS` from a permit or age. Do not retry a released reservation through a new source or implement new credit reactivation policy. Those states remain visible holds. A historical paid credit that cannot be committed by its real period owner remains held rather than charging the current period.

## Dependencies

- `ARCH-056-BACKGROUND-002` — Requires Complete. Supplies the exact retained-source and confirmed-settlement contracts, positive-commit guard and selected compatible status/compensation lock ordering.
- `ARCH-056-BACKGROUND-003` — Requires Complete. Supplies scoped durable lookup, same-message initial resume and exact final source/permit/receipt behavior.
- `ARCH-028-BACKGROUND-012` — Complete. Preserve candidate options-object routing and token-identified missing-recipient update behavior.
- `ARCH-050-BACKGROUND-002` — Complete. Preserve Shopify confirmation wiring to the common atomic initial-attempt/Support writer.
- `ARCH-050-BACKGROUND-003` — Complete. Preserve the actual Woo confirmed-initial Support finalizer adapter, its initial-only/no-follow-up behavior and production outbound gate.
- `ARCH-052-BACKGROUND-018` — Complete. Correct the existing approved no-offer fallback without changing its accepted neutral content contract.
- `ARCH-053-BACKGROUND-005` — Complete. Preserve the current recovery-lifetime eligibility owner while correcting required-state failure propagation in the initial facade/fallback.

Start from the accepted BG002/BG003 commits. Do not duplicate their billing resolver, use an unsafe temporary sender, or silently bypass a missing prerequisite. ARCH-028-BACKGROUND-013 remains an explicit blocked policy boundary; this task does not unblock it.

## Enables

- `ARCH-056-SYSTEM-TEST-001` proves the integrated actual-worker interruption matrix using the accepted Background SHA and all accepted upstream task commits.

## Acceptance Criteria

- [ ] The real candidate handler continues interrupted DETECTED progress in the same generation/attempt and never acknowledges a required-state exception through an ordinary no-op.
- [ ] A pre-message retained credit is reused, a pre-permit message is resumed in place, and only proven source absence permits fresh admission.
- [ ] Provider uncertainty and credit holds remain visible failed/held work with no retry HTTP, speculative refund, new debit, Support notice or success status.
- [ ] Confirmed replay bypasses template/new-admission gates and uses only exact settled billing evidence before atomic Support/status/follow-up work.
- [ ] Each selected billing/Support/status/queue interruption converges idempotently on explicit retry; finalized null/non-null due dates and actual message sentAt remain unchanged.
- [ ] The historical FAILED/PROVIDER_FAILURE repair is confined to the exact specified confirmed and settled lineage; genuine failure, 131026, cancellation and sequence two are not reset.
- [ ] Optional enrichment still allows approved neutral outreach while required-state outages fail with original error/cause.
- [ ] Woo confirmed replay works before the production outbound gate; new/resumed provider work stays test-only and never schedules a Woo sequence two.
- [ ] Bounded retry exhaustion retains visible failed work, and the documented explicit replay entry reaches the same handler; no generic scanner is claimed.
- [ ] All listed worker/service, PostgreSQL/Redis, regression, build, lint and whitespace commands pass with real prerequisites; no skipped environment is reported as passed.

- [ ] A safe optional-source marker remains observable when neutral fallback succeeds; a required fallback error is logged and reaches the caller as the same actual exception, without an unrelated cause.
- [ ] Woo unexpected-failure output retains safe original wording and stage/IDs, while sensitive text is excluded; wholesale useful-diagnostic omission is not accepted.
- [ ] Materialization/cleanup and preflight/release or send/compensation pairs expose both source messages independently through actual Shared serialization and retain both original objects for propagation.
- [ ] Progress holds/blocks and finalization failures emit truthful reasons/stages/messages and known correlation; no failed/held state is logged as sent or completed, and no upstream fields are fabricated.
- [ ] Actual worker listeners and a throwing real Shared sink are tested; diagnostic delivery cannot change success, retry, original thrown identity, SQL outcome or compensation behavior.

## Validation

Drive the actual candidate handler/materializer with real SQL and bounded Redis job execution where applicable, not only a direct service mock:

| Stopped boundary | Required next execution |
|---|---|
| Recovery inserted; required customer/read fails | Same generation; original error fails first job; retry reaches preparation rather than `no-op-existing`. |
| Attempt exists; required lifetime/preparation read fails | Same attempt; technical retry survives facade/fallback; optional offer outage still allows approved neutral preparation. |
| Exact credit RESERVED, no message | Revalidate/reuse that source; no second reservation/current-period replacement. |
| Message and usage committed, no permit | Same message/usage through BG003; no second quantity or HTTP permission. |
| Permit committed, no outcome, including HTTP success then receipt DB failure | Visible held/failed job with original evidence; zero retry HTTP, zero speculative release/commit. |
| Confirmed receipt, credit not committed | Exact BG002 settlement; no template/admit/provider work. A held source prevents all later completion. |
| Credit committed, Support rolls back | Replay already committed credit and one atomic attempt/notice transition. |
| Support/attempt commits, recovery status update fails | Bypass fallback and its INVALID_ATTEMPT guard; one notice; finish conditional status update. |
| Recovery status commits, follow-up enqueue fails | Same stored due date and job identity, no second message/credit/notice. |
| Finalized due null or non-null, policy then changes | Preserve the exact stored value; no null-to-date conversion on replay. |
| Confirmed receipt followed by STOP/order/pause/terminal state | Reconcile observed receipt/credit without new provider work or terminal-state downgrade; current follow-up guards remain. |
| Failed candidate exhausts bounded retries | Job remains failed/visible; no false acknowledgement or claim of autonomous SQL scanning. Explicit retry enters the same real handler. |

Also test conflicting tenants/keys, missing lineage, all billing held reasons at the consumption boundary, the narrow legacy false-failure guard, current suppression wake-up behavior, neutral no-offer actual dispatch, genuine 131026/cancellation preservation, Woo production disabled plus confirmed-before-gate, and sequence-two compatibility. In the task-owned Support integration suite, force both finalizer/final-fence winner orders using a Shop with no existing Support thread. Execute actual first-thread and recovery-linked notice inserts and their immediate FK checks; observe Shop KEY SHARE before attempt ownership, unchanged-pointer validation, one atomic notice/attempt result and no fence/attempt/parent cycle. A pre-created thread or mocked notice insert alone does not exercise this boundary.

The existing queue remains three attempts with its accepted backoff/removal policy. The explicit recovery route after exhaustion is retry of the retained failed candidate with its original job data through `materializeMaturedCandidate(candidate, {jobId, ...existingOptions})`, using the real worker handler. For an already confirmed known recovery, `continueInitialOutreach({shopId,recoveryId})` is also a stable service entry. Neither route authorizes a new send from uncertain evidence. Do not create an unauthenticated repair endpoint or imply a recurring scanner exists.

### Emitted-record logging matrix

Use the actual installed Shared createLogger with a capture sink (or a test-only factory interception that delegates to it), record version/resolution and serialize/parse captured records. Assert the selected safe original/component message field, event, level, service/environment, exact stage and known identity. Mocked logger argument checks and rejection-only tests remain useful but do not establish emission. Verify absence of injected secrets/PII, explicit redaction/truncation, no fabricated providerError, original thrown-object identity or approved typed result, and unchanged business behavior with a throwing sink.

| Owned test module | Required logging proof |
|---|---|
| `tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts` | Replace the unexpected-DB-error reason-only RETRY expectation with emitted safe source marker plus rejection by that same exception. Test actual missing/invalid lifetime exceptions separately from business lifetime denial. |
| `tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts` | Optional failure followed by PREPARED neutral fallback still emits its safe source/degradation marker. Required fallback error retains its actual identity/cause instead of unrelated optional cause; no-error typed outcomes have no invented providerError. |
| `tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts` | Replace generic-only failure-output expectation with safe source wording/stage/IDs and exclusion of sensitive portions. Verify independent emitted markers plus retained aggregate objects for preflight/release and send/compensation pairs. |
| `tests/unit/workers/pending-recovery-candidate.worker.test.ts` | Retain and invoke failed/error callbacks in the harness. Distinct materialization and cleanup errors appear under their own named fields through actual Shared serialization, with queue/job/attempt/shop context and preserved composite/retry-marker behavior. |
| `tests/unit/services/checkout-recovery/initial-outreach-progress.test.ts` | Direct and queued continuation failure emits actual stage/message and rethrows unchanged; held/blocked results retain exact reasons and never claim completed work or invented source diagnostics. |
| `tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts` | Supplement the existing four-stage original-object tests with emitted original-safe name/message and correlation; a throwing sink cannot replace the failure or continue status/follow-up work. |
| `tests/unit/services/checkout-recovery/recovery-initial-outreach-support-notice.service.test.ts` | Actual emitted persistence message/category and only validated IDs. No notice/customer content; logging failure cannot undo a committed transaction or mask its failure. |
| `tests/unit/services/woocommerce-recovery/woo-confirmed-initial-settlement.test.ts` | Actual adapter finalization-stage/message output, truthful held diagnostics, and no logging-induced sent/notice/sequence-two behavior. |

Extend the already declared actual-worker integration scenario with one captured materialization/cleanup compound-failure record and one confirmed-receipt/finalization error record. Inspect actual emitted records separately from SQL/provider state assertions; a report that merely copies an injected string is not log-delivery evidence. Keep existing source adapter detail ownership and moderation privacy; no provider parser or generic log-serialization implementation is added.

Run from the task checkout of `moda-interact-background/`, after its declared PostgreSQL/Redis prerequisites are ready. Commands are standalone and do not depend on this drafting manifest:

```sh
npx --no-install vitest run tests/unit/workers/pending-recovery-candidate.worker.test.ts tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts tests/unit/services/checkout-recovery/recovery-initial-outreach-support-notice.service.test.ts tests/unit/services/checkout-recovery/initial-outreach-progress.test.ts tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts tests/unit/services/woocommerce-recovery/woo-confirmed-initial-settlement.test.ts tests/unit/services/woocommerce-recovery/woo-recovery-composition.test.ts
```

```sh
npm run test:integration -- tests/integration/initial-outreach-progress.integration.test.ts tests/integration/initial-outreach-progress-worker.integration.test.ts tests/integration/arch052-shopify-initial-no-offer-dispatch.integration.test.ts tests/integration/recovery-initial-outreach-support-notice.integration.test.ts tests/integration/arch055-follow-up-identity.integration.test.ts
```

```sh
npm run build
```

```sh
npx --no-install eslint src/services/checkout-recovery.service.ts src/services/checkout-recovery/recovery-materialization.service.ts src/services/checkout-recovery/recovery-initiation.service.ts src/services/checkout-recovery/recovery-outreach-finalization.service.ts src/services/checkout-recovery/recovery-initial-outreach-support-notice.service.ts src/services/checkout-recovery/recovery-initial-outreach-support-notice.contracts.ts src/workers/pending-recovery-candidate.worker.ts src/services/recovery-template-integration/automated-recovery-template.service.ts src/services/recovery-template-integration/initial-no-offer-fallback.service.ts src/services/woocommerce-recovery/woo-recovery-outreach.service.ts src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts tests/unit/workers/pending-recovery-candidate.worker.test.ts tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts tests/unit/services/checkout-recovery/recovery-initial-outreach-support-notice.service.test.ts tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts tests/integration/arch052-shopify-initial-no-offer-dispatch.integration.test.ts tests/integration/recovery-initial-outreach-support-notice.integration.test.ts tests/unit/services/checkout-recovery/initial-outreach-progress.test.ts tests/unit/services/woocommerce-recovery/woo-confirmed-initial-settlement.test.ts tests/integration/initial-outreach-progress.integration.test.ts tests/integration/initial-outreach-progress-worker.integration.test.ts tests/integration/fixtures/initial-outreach-progress.fixture.ts
```

```sh
git diff --check
```

## Implementation Notes

Use the parent architecture's common worktree, ownership, error/logging and completion-evidence rules. Keep facade wiring thin, decision logic in the existing initiation/materialization owners, exact accounting in BG002, provider permission in BG003, and atomic Support writes in their existing service. Add no production module or speculative reactivation/scanner infrastructure. Newly created test modules target at most 200 physical lines and must not exceed 300; keep fixtures separate in the declared fixture file.

The terminal system proof must pin and execute this accepted Background SHA; it must not implicitly build remote main. Completion needs actual worker/queue/database/provider evidence, not direct-initiation mocks alone.

Stop on an unresolved identity/credit policy, a needed unowned production edit, unsafe reactivation, or a missing accepted prerequisite. Preserve visible held state and original errors. A fallback-key-only change is incomplete. On passing the scoped gates, publish normal task mirrors and evidence, set status to review, return to the architect and stop; do not execute enabled tasks.

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


## Architect Dependency Reconciliation (2026-11-04)

Ready for normal launcher preparation: all declared prerequisites are complete (ARCH-056-BACKGROUND-002/003, ARCH-028-BACKGROUND-012, ARCH-050-BACKGROUND-002/003, ARCH-052-BACKGROUND-018 and ARCH-053-BACKGROUND-005). This promotion does not claim or execute the task; Attempt 0 and the empty executor claim remain unchanged. SYSTEM-TEST-001 still requires this task's completion.
