---
id: ARCH-028-BACKGROUND-013
architecture_id: ARCH-028
title: Commit attempted uncertain WhatsApp sends and compensate confirmed recovery delivery failures
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-004
  - ARCH-028-BACKGROUND-009
enables: []
created: 2026-10-22
updated: 2026-10-22
---

# Commit attempted uncertain WhatsApp sends and compensate confirmed recovery delivery failures

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

**Architect review prerequisite:** This task records a newly clarified merchant-credit policy. The existing ARCH-028 scope limits terminal-recipient compensation to Meta code `131026`. The architect must explicitly approve expanding compensation to authoritative post-acceptance `FAILED` outcomes and confirm the required DATABASE-owned migration before implementation. Do not mark this task ready or edit architecture `_index.md` files as part of this proposal.

## Objective

Ensure that exactly **one** recovery credit is committed when an outbound WhatsApp provider dispatch has been attempted, even if Meta's HTTP response is missing or the Background worker crashes, and that a subsequently confirmed delivery failure returns/corrects the exact committed credit once. A missing provider response is *presumed success for credit accounting*, not evidence of actual delivery and not grounds for an automatic resend.

## Confirmed merchant billing policy (2026-10-22)

1. A confirmed Meta API acceptance commits the recovery credit (existing behaviour).
2. Once dispatch **has actually been attempted**, an HTTP timeout, broken connection, missing response or uncertain provider result **commits the credit immediately**; no reconciliation grace period and no indefinite `AMBIGUOUS` holding state.
3. If Background crashes after the durable dispatch-attempt boundary, recovery commits that same credit once after restart. Reconciliation must be resumable and must not call Meta again.
4. A **definitive rejection before acceptance** releases the still-reserved credit; pre-provider validation/configuration/moderation/eligibility failure also releases it. No attempted dispatch means no credit consumption.
5. A later *authoritative*, correlated `FAILED` delivery report compensates the original committed credit once, provided no stronger `DELIVERED`/`READ` evidence has already won under the accepted provider-status transition policy.
6. If no authoritative failure arrives, the credit **remains committed**. A missing provider ID cannot be invented, and an unknown callback cannot be correlated by phone number, timestamp or guessed Shop.
7. Billing presumption must never manufacture `ConversationMessage.DELIVERED`, `deliveredAt`, a provider message ID, `DELIVERED_WHATSAPP_MESSAGE` usage, or a false merchant delivery receipt.

## Verified gaps in current Background `main`

- `src/services/recovery-billing/recovery-reservation-lifecycle.service.ts` classifies non-definitive provider errors as `ambiguous` and calls `markAmbiguous`, not `commit`. This diverges from point 2.
- `src/services/recovery-reservation/reservation-lifecycle.ts` currently only applies a normal `commit` from `RESERVED`; an `AMBIGUOUS` reservation replays rather than settling to `COMMITTED`. Any needed reconciliation transition must be explicit and idempotent.
- A forced mid-dispatch crash leaves the recovery credit `RESERVED`. The existing worker/BullMQ replay suppresses a second send but has no demonstrated durable, owner-safe credit-commit repair. This diverges from point 3.
- `src/services/whatsapp-provider-status.service.ts` persists provider `FAILED` and delivered-message usage but does not itself invoke a recovery-credit compensation owner. Existing ARCH-028-BACKGROUND-004/-009 define compensation for terminal-recipient code `131026`; expanding the eligible failure policy requires architect review, not duplicate compensation logic.
- `billing.UsageReservationCompensationReason` currently exposes `WHATSAPP_RECIPIENT_UNDELIVERABLE` only. A general, authoritative delivery-failure correction likely requires a DATABASE-owned enum/provenance contract amendment.

Existing passing system tests document **current behaviour**, not this new policy: `RECOVERY-PROVIDER-AMBIGUOUS-001` observed a held `AMBIGUOUS` credit; `RECOVERY-PROVIDER-CRASH-001` observed an orphaned `RESERVED` credit after safe BullMQ recovery; `RECOVERY-PROVIDER-UNKNOWN-ID-001` observed that unmatched callbacks cannot resolve that credit. `MESSAGING-STATUS-001` covers correlated delivery states but does not establish committed-credit compensation on all authorised `FAILED` events.

## Scope

### A. Durable attempted-dispatch authority and immediate settlement

- Identify the exact durable boundary between *pre-provider* work and *provider dispatch attempted*. Persist an immutable, Shop/attempt/message-scoped dispatch intent **before** provider I/O. Review whether existing `ConversationMessage.providerDispatchAdmittedAt` and `providerDispatchKey` can be reused safely for automated recovery sends; do not confuse mere message reservation with actual provider attempt.
- For a caught uncertain provider outcome, commit the existing recovery source once and record a bounded `provider-outcome-unconfirmed` billing reason/state using the accepted source owner; leave provider acceptance/delivery evidence unknown.
- For a definite Meta rejection, release while still `RESERVED`. Preserve the current suppression/failure state, without contradicting the committed-credit correction rules below.
- Keep idempotency keys, immutable recipient, moderation-before-provider fence and existing outbound hard-limit accounting. Do not make Meta send retries part of financial settlement.

### B. Crash repair without resend

- Reconcile eligible attempted-but-unsettled recovery reservations after worker termination, using existing durable dispatch evidence and an existing Background worker/repair lifecycle where possible. Reconcile promptly after restart; no arbitrary grace period that changes this policy.
- Exactly one worker may settle a source. Repair must work for `RESERVED` and previously `AMBIGUOUS` attempted sources, be tenant-scoped, and survive worker crashes midway through correction.
- Preserve the original checkout/attempt idempotency fence. Neither direct replay nor BullMQ stalled-job replay may produce a second Meta request, second UsageEvent or second credit commitment.
- If provenance is insufficient to prove that provider dispatch was attempted, **fail closed and surface structured diagnostic evidence**; do not blindly charge a merchant for a merely reserved but unsent message.

### C. Compensate confirmed post-acceptance delivery failure

- Extend/reuse the accepted ARCH-028-BACKGROUND-004 compensation coordinator and BACKGROUND-009 purchased-credit strategy, rather than introducing a competing adjustment pipeline.
- On a real, correlated authoritative `FAILED` event eligible under the agreed provider-status precedence, correct the exact committed recovery source once; this must work when the recovery attempt has already advanced to `NO_RESPONSE`, when the provider-status callback is replayed, and when the process crashes between status convergence and financial correction.
- Preserve original `shopId`, billing `provider` (Shopify/Woo), source, billing period, idempotent correction lineage and original correction disposition. Negative UsageEvents must remain non-reportable to Shopify.
- For purchased credits, respect the existing ARCH-027 purchase/refund holds and ARCH-028-BACKGROUND-009 `RESTORED_SPENDABLE`, `HELD_FOR_REFUND` and `HISTORICAL_ONLY` rules. Do **not** trigger a new provider monetary refund or invent a make-good credit.
- Reuse existing hard-limit-usage correction and merchant support notification owners after durable financial correction; no false "credit restored" message for non-spendable dispositions.
- Do not compensate a later stale `FAILED` callback once authoritative `DELIVERED`/`READ` has already won. Preserve ARCH-028 accepted race and late-positive-evidence semantics for compensation already completed.

## Explicitly out of scope

- Claiming a missing HTTP response proves actual Meta delivery, fabricating a provider message ID or `DELIVERED` receipt.
- Automatic resending, provider-side message lookup by phone/time, or cross-merchant customer correlation.
- Monetary refunds, generic plan/pricing redesign, new merchant accounts or roles.
- Relaxing the existing `131026` reachability-suppression rule for other failure codes. Credit correction eligibility and recipient-suppression eligibility are separate decisions.
- Application-side edits in this task to other repositories. Any schema or consumer migration needed must be delegated to its owning task/repository by the architect.

## Work items

- [ ] Architect approves policy extension to ARCH-028 and assigns any DATABASE-owned provenance/enum migration (the present compensation-reason enum is insufficient for generic failed delivery).
- [ ] Implement durable provider-attempt authority, distinguishing pre-dispatch failures from attempted sends.
- [ ] Add exactly-once uncertain-outcome commitment, including explicit `AMBIGUOUS -> COMMITTED` handling where necessary, for lifetime-Free, paid-included, promotional and purchased recovery sources.
- [ ] Add crash-repair owner that commits attempted-but-unsettled sources without resending or bypassing existing source/tenant fences.
- [ ] Integrate confirmed `FAILED` compensation with existing ARCH-028 generic and purchased strategies, provider-status job retry, and source lineage.
- [ ] Keep provider delivery receipts independent from accounting presumption; add structured, bounded logging without customer/Meta secrets.
- [ ] Add focused unit, integration, fault-injection and duplicate/out-of-order callback tests; update impacted system-test scenarios.
- [ ] Keep production responsibilities split into source owners, dispatch evidence, reconciliation and compensation modules; new source files target <=200 lines and MUST remain <=300 lines.

## Acceptance criteria

- [ ] Meta 2xx acceptance: one committed credit, zero reserved, one provider send and one positive recovery UsageEvent.
- [ ] HTTP timeout/lost response **after verified dispatch attempt**: original credit becomes `COMMITTED` exactly once; zero additional Meta requests; outbound status remains unconfirmed rather than falsely `DELIVERED`.
- [ ] Worker kill after dispatch attempt but before acknowledgement: on restart, original `RESERVED`/`AMBIGUOUS` source becomes `COMMITTED` once without duplicate send or duplicate UsageEvent.
- [ ] Provider/configuration/moderation failure before attempted dispatch: zero committed and zero reserved credits for that attempt after terminal handling; no send.
- [ ] Definitive Meta rejection: still-reserved source is released exactly once; zero committed credit for the rejected send.
- [ ] Correlated asynchronous provider `FAILED` after commitment: exact compensated credit restored/held historically as appropriate, once; original committed positive event remains auditable, exact negative event is never externally reported.
- [ ] Duplicate or out-of-order `FAILED`, `DELIVERED`, `READ` and job replays preserve final provider status and cannot double commit, double compensate or cross-tenant adjust.
- [ ] Unknown provider ID callbacks have no settlement authority by themselves; unmatched messages remain uncorrelated and cause no fictitious provider receipt.
- [ ] Usage counters are consistent across all supported credit sources, billing periods and Shopify/Woo providers, including purchased-refund holds and historical-only dispositions.
- [ ] Merchant-visible usage reflects the credit committed under this policy and any later legitimate compensation without claiming confirmed delivery where none exists.
- [ ] Failure injection between any two durable steps converges correctly after retry/restart; no manual Redis lock deletion or direct ledger mutation is needed.
- [ ] Repository tests, PostgreSQL integration, TypeScript build, `git diff --check`, and system-test release checks pass.

## Required system-test updates (owned by `moda-interact-system-test`)

After this production change is architect-approved and deployed to the appropriate test source:

- `RECOVERY-PROVIDER-AMBIGUOUS-001`: replace the expected held `AMBIGUOUS` credit with one newly committed credit after attempted dispatch.
- `RECOVERY-PROVIDER-CRASH-001`: retain kill/replay assertions; require eventual exactly-once commitment after restart instead of indefinite `RESERVED`.
- `RECOVERY-PROVIDER-UNKNOWN-ID-001`: continue rejecting unknown-ID callbacks, but expect credit committed by policy and no fabricated delivery receipt.
- `RECOVERY-PROVIDER-FAILURE-001`: retain release of definite rejected provider sends.
- `MESSAGING-STATUS-001`: add confirmed-failure credit compensation, replay, precedence and merchant-visible correction checks.
- `RECOVERY-PROVIDER-SETTLEMENT-001`: make the presently planned release-blocking scenario executable, covering commit/no-response, crash repair and confirmed failure correction.

Do not change system-test PASS/coverage records to claim this policy works before production implementation and black-box evidence exist.

## Interfaces / dependencies

- Reuses `ARCH-028-BACKGROUND-004` (generic compensation), `ARCH-028-BACKGROUND-009` (purchased compensation), `ARCH-027-BACKGROUND-005` (purchased refund authority) and existing `UsageReservation`/`UsageEvent` lineage.
- Requires architect coordination with `moda-interact-database` for an additive compensation reason/dispatch-evidence migration if existing fields cannot enforce the accepted policy.
- Coordinates with Messaging normalized provider-status ingestion, but does not infer Shop ownership or delivery from unknown IDs.
- Supersedes **only** the prior *credit-held indefinitely* expectation in affected system tests; preserves provider state and idempotency constraints.

## Validation

Background unit and PostgreSQL integration: all four recovery source types, multi-period and purchased refund-state edges, pre-/post-provider error classification, replay/crash interleavings, concurrency, status replay/late positive delivery, and negative UsageEvent provider attribution. Production-parity disposable local end-to-end: Shopify checkout -> Meta accept/lost response -> credit commit, crash -> commit on repair, authenticated merchant credit view, and correlated Meta FAILED -> exactly-once compensation; also Woo billing parity where source-specific.

## Stop condition

Complete implementation and evidence report -> `review` -> return to `moda_architect` -> STOP. Do not mark task complete or update `docs/decisions/**/_index.md` until architect acceptance and the session boundary permit it.

## Completion report

### Status

Not Started — pending architect review and schema-ownership decision.

### Files changed

None (implementation pending).

### Validation results

Not Run.

## Architect review

### Review status

Pending.

### Review notes

Confirm policy extension, database transition/evidence contract, ordering against existing ARCH-028 compensation tasks, and exact production/test ownership.
