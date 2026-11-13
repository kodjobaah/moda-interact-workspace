---
id: ARCH-076-BACKGROUND-002
architecture_id: ARCH-076
title: Pin the selected sender through initial, automated and merchant WhatsApp dispatch
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-076-BACKGROUND-001]
enables: [ARCH-076-BACKGROUND-003]
created: 2026-11-13
updated: 2026-11-13
---

# Pin senders through the provider dispatch

## Architecture

[ARCH-076 — WhatsApp sender pool and checkout reply routing](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinated by `moda_architect`.

## Objective

Send each recovery message through its membership of the customer/shop route, and return parked attempts to the existing provider flow. Two eligible baskets at one shop use one physical WhatsApp sender; both retain their own admission, credit, conversation and provider-message history.

## Context

Preserved from original local commit `59705bb589342f31054e6c1fd011dacf9d495ae6` under root-authorized ARCH-076 collision correction. Defined portable design only; Pending/unclaimed until current-main compatibility review and explicit architect promotion. No runtime implementation or launch is authorized by preservation.

Integrate the accepted BACKGROUND-001 allocator into the **existing** initial-outreach, final-permit and transport paths. The first credit reservation precedes the existing final SQL permit. Source keys are stable and a RELEASED reservation cannot be reopened. Join the existing same-shop route, or obtain a new route plus this recovery’s provisional membership, before reserving its credit. Confirm that exact member at the final permit. A provisional member alone cannot receive an inbound reply. Never infer a provider confirmation from a pool row. All paths below are relative to `moda-interact-background`. Read the [binding architecture](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md).

## Scope

Change the two initial outreach coordinators, existing final permits, HTTP transport, human dispatcher and pool retry integration listed below, plus their tests. All repository paths are relative to `moda-interact-background`.

## Out of Scope

Do not enable test-only Woo production outreach, introduce an alternative billing or standalone routing policy, change provider registrations, or deploy. BACKGROUND-003 owns inbound identity, STOP, guidance and provider status. The checkout selection/clarification task owns route-level dialogue and its provider permits.

## Requirements

All distinct recoveries accepted by the merchant/platform checkout flow run their own pre-credit preparation; a shop with multiple checkouts for this recipient shares its open sender route. No latest-basket or one-basket-per-shop selection or cancellation belongs in outbound. Keep all send eligibility, moderation, approved template, service-window, credit and idempotency checks. Only a committed permit can supply the sender for the HTTP call. General outbound uses a server-resolved configured singleton only while it is outside the inventory.

## Work Items

- [ ] **Shopify first send.** In `src/services/checkout-recovery/recovery-initiation.service.ts` preserve lookup of sequence one, its conversation, existing provider admission and credit evidence. An earlier confirmed or uncertain permit continues through its original finalisation/hold first. On a fresh or proven pre-permit PENDING attempt run BG001 `prepareInitialSender` after eligibility/consent and approved template selection and immediately before the first `billingService.admit`. Existing credit can continue only with the same durable sender preparation for this recovery. If that preparation is missing on pre-cutover reserved credit, hold for its existing reconciliation and do not submit a provider request. Expose `sender-pool-exhausted` as a typed deferred outcome through `checkout-recovery/recovery-materialization.service.ts`, `checkout-recovery.service.ts` and worker handling. For PENDING, a normal exhausted result acknowledges work only after the wait marker commits. A billing-capacity re-entry of an existing CAPACITY_BLOCKED attempt keeps its existing capacity-repair owner if no sender is available; it never becomes a fresh sender waiter or loses its billing status. Never mark the attempt FAILED, emit a billing-capacity notice, consume a dispatch ID, or mark outreach sent. Before revalidating retained credit, recognise the exact PENDING wait-marker case and run pre-credit claim/clear. Do not treat an existing independently eligible checkout in this shop as a duplicate or cancel its conversation. Preserve all other failure/hold decisions at `src/services/recovery-billing/initial-outreach-credit.service.ts`.
- [ ] **Woo first send.** In `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts` call the same service after `resolve-conversation` and before `reserve-recovery-credit` in `processInitial`. Carry attemptId/conversationId, canonical recipient and configured WABA through the existing `woo-recovery-composition.ts` injection. Preserve `woo-guarded-initial-sender.service.ts`, Redis observed-order check, actual Woo consent snapshot and `WooInitialSendFenceService` final SQL permission. Treat pool exhaustion as parked work in `woo-recovery-orchestrator.service.ts`, before the generic deferred-to-BullMQ-error conversion. Preserve `NODE_ENV==='test'` and existing Woo outbound/test admission switches. A production or development Woo sender must not be activated by this task.
- [ ] **Pre-credit outcomes.** On no credit available or other definitive refusal before a provider permit use the existing reason, billing cleanup and the guarded BG001 discard operation. A capacity wait cannot enter a release-and-re-reserve cycle. Transient failure before the permit may resume the same assignment, attempt, retained credit and prepared message following the established progress classifier. On a definite no-send, prove the original reservation belongs to that attempt before release. On possibly admitted or genuinely provider-uncertain outcomes keep the assignment and existing credit/UNKNOWN lineage for reconciliation; never re-post, retry as text or change phone. Expiry releases this member; the slot becomes free when the shop route loses its last open member. Any old acknowledgement after reassignment finalises only its old message/attempt. Remove only this failed tentative membership when permitted. Do not free a shop route while a sibling remains open.
- [ ] **Repair wiring.** Add `src/services/whatsapp-sender-pool/retry-job.ts`. Keep the existing `PENDING_RECOVERY_CANDIDATE_QUEUE`. Job name `recovery-sender-pool-retry-v1`, exact data `{recoveryId:string,attemptId:string}`, existing bounded ID grammar, deterministic BullMQ job ID `sender-pool-` plus lowercase SHA-256 of UTF-8 recoveryId, NUL, attemptId. Mirror the add/getJob/validate/retry-failed semantics and removeOnComplete/failed retention of `woocommerce-recovery/woo-initial-dispatch.queue.ts`; share the stable queue helper where this preserves both existing job identities. Add the job to the established worker's allowed job names and discriminant in `src/workers/pending-recovery-candidate.worker.ts`. The repair callback in `src/entrypoints/recovery.ts` must call BG001 waiter discovery on the existing `RECOVERY_CAPACITY_REPAIR` leased tick with `recoveryRepairShopBatchSize`. Run original billing repair and pool discovery independently, collect/log failures, and propagate errors so neither silently disables the other. Add shutdown of the producer handle. Use the DB marker/open preparation as recovery source after a crash, not the finite BullMQ retry count.
- [ ] **Exact repair continuation.** The worker reloads attempt, recovery, shop/platform, generation, recipient, latest external activity and original dispatch progress by its payload IDs. An unrelated, terminal, changed, superseded or no-longer-waiting/non-provisional owner is a no-op; confirmed/admitted work only enters its established receipt/hold continuation. Resolve the platform from this join. On Woo call `onInitialDispatch(recoveryId,attemptId)`, preserving its checkout lock. On Shopify use `RecoveryMaterializationService.materialize` via `checkoutRecoveryService.materializeMaturedCandidate` with an optional internal expected `{recoveryId,attemptId,generation}` for this retry only. Build the existing PendingRecoveryCandidate from trusted shop.id/domain, checkoutToken, cartToken, checkoutUrl, detectedAt/lastExternalActivityAt. Inside its existing checkout lock verify expected owner, latest generation, DETECTED, active lifetime, current policy recovery delay and no newer candidate/order both before provider preparation and at the existing admission gate. A waiting job may never manufacture a next generation when it finds an expired original. Use the normal authoritative checkout lookup, consent, recipient, discount/template and billing path. On a newer event or a still-future maturity, leave the durable eligible state for normal maturity/next repair. Do not call the checkout-event ingress as a new event or fabricate a recent activity time. Retained unknown/prepared progress uses ordinary idempotency; do not issue an extra API call to Meta.
- [ ] **Final permits.** In `src/services/recovery-conversation/outbound-send-fence.service.ts` extend successful `DispatchPermit` with required `sender: ModaWhatsAppSender`. Apply to all HUMAN/AGENT/AUTOMATION kinds and both free-form and proactive sends. In `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts` extend the successful `WooInitialFinalPermit` identically. Under the normal Shop -> Conversation -> CheckoutRecovery ordering, lock the target recovery, its open shop route and then its unreleased membership, and call BG001's `requireAssignedSender`; ensure the permit checks effective lifetime even when the expiry sweep is late. Perform the check before mutating usage/claims/product context/permit evidence and commit the decision with the dispatch key. For initial sends require DETECTED and sequence-one scope, for later sends require eligible MESSAGE_SENT/ENGAGED and confirmed initial send to the same canonical recipient. Ignore allocationEnabled for a still-open route, including an eligible newly joined sibling. Match the target conversation, shop and canonical recipient to the immutable membership/route proof. Sharing a transport number never authorises one checkout to spend or send against another. Validate the approved template registration WABA against the permitted WABA, including Woo and merchant post-window templates. Reject released/stale owner, changed generation, missing credentials, wrong WABA or recipient with a typed pre-permit denial. Keep moderation, controls, final offer/image checks, local STOP, consent and customer service window in their original gates.
- [ ] **Transport.** Reuse `ModaWhatsAppSender` from `src/services/whatsapp.service.ts` (move its type-only definition into `src/integration/whatsapp/types.ts` and re-export if needed). Require a trusted sender argument on all three final HTTP methods, `sendWhatsAppTemplate(input,sender,signal?)`, `sendWhatsAppText(input,sender,signal?)`, `sendWhatsAppImage(input,sender,signal?)`. This separate parameter keeps preparers/templates/media inputs free of sender authority. In those methods use up-to-date token and verify token configuration's businessAccountId matches sender.providerAccountId. Build the Graph endpoint only from `sender.providerPhoneNumberId`. Never reread singleton phoneNumberId as the source for a pooled send; no provider-side discovery per checkout, fallback phone, retry on another number, request-body 'from', or sender in AI/merchant input. In `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts` replace the private null-for-success fence result with a discriminated admitted sender or normal suppression; carry it through prepared text, frozen image, template, terminal text and Woo-specific send without dropping it. In `src/services/recovery-conversation/human-command-dispatcher.service.ts` keep the exact message/delivery plan from the committed permit, pass its sender to direct text/image/follow-up sends, and preserve its UNKNOWN recording on uncertain results. Adapt `outbound-whatsapp-admission.service.ts`, `outbound-whatsapp-admission/outbound-whatsapp-admission.types.ts`, provider ports, immediate callers and focused fakes to compile. Adapt `src/services/routing-guidance.service.ts` to pass the sender identity already validated against its inbound event. BACKGROUND-003 upgrades that singleton validation for recognition of pooled numbers. Expose the same sender-explicit text transport to the route-level clarification owner. For its approved routing question, accept only `{to,text}` and the verified `{providerAccountId,providerPhoneNumberId}` supplied by the clarification owner’s committed route-scoped prompt permit. A model never chooses the number, recipient, shop or provider endpoint. The clarification is a service-window response on the incoming number; it must not call an initial/follow-up recovery sender or bill one of the candidate baskets. This task supplies the transport interface and fake-provider contract test; the clarification task implements prompt authentication, moderation, dedupe, provider evidence and revalidation.
- [ ] **Standalone and legacy.** A genuine standalone outbound still uses the existing encrypted singleton when it is outside the pool. In `outbound-whatsapp-admission/general-outbound-send-fence.service.ts`, require proven standalone ownership, trusted sender resolved from server configuration, and a protected negative inventory lookup. Within the final transaction take the membership lock used by Admin, `pg_advisory_xact_lock(hashtextextended('whatsapp-pool-membership:' || phone_id,0))` with bound ID before reading inventory. Presence of the phone row in any state including disabled returns typed `sender-reserved-for-recoveries` before dispatch. No second choice. At successful general permit, write DATABASE-001's message fields `dispatchProviderAccountId` and `dispatchProviderPhoneNumberId` together, with the dispatch key, return those IDs in the permit and use them on the wire. These fields remain null for newly pooled messages, whose exact conversation membership -> immutable route -> inventory provides sender evidence even after its member is released and its route is closed. A recovery never enters the general fence because its sender is missing. Leave pre-cutover unassigned retained recovery messages on historical quote/status handling using positive evidence only; if a legacy outbound is to continue, require immutable sender proof matching original and configured singleton, outside the inventory under the same membership lock, then persist sender on that message as for general sends. If proof is unavailable, refuse the new legacy dispatch. An old unassigned already-admitted recovery is never recreated as fresh pooled outreach. Preserve existing authenticated guidance exemption for neutral non-merchant replies.
- [ ] **Coverage, operational visibility and rollout.** Use the existing shared logger. Emit bounded exhaustion, claim, release, denied owner, WABA mismatch and ambiguous dispatch outcomes with recovery/attempt/message internal IDs. Preserve redacted original error message, safe provider error code/status and relevant response details. No raw recipient/token/body or new middleware/metrics. Deploy only as coordinated pre-production cutover after inbound/STOP/status handling and Admin are integrated. A one-number pool is supported. Do not add a feature toggle, extra credential, provider call to probe configuration on every send or live activation.

## Interfaces / Contracts

Consume BACKGROUND-001's four local services and DATABASE-001's schema. The required final HTTP sender argument is `ModaWhatsAppSender = {providerAccountId:string, providerPhoneNumberId:string}`. The success result from each provider permit carries exactly that sender. The internal retry queue protocol and job name are defined above. Do not add cross-service wire contracts.

## Dependencies

ARCH-076-BACKGROUND-001, accepted and integrated.

## Enables

ARCH-076-BACKGROUND-003.

## Acceptance Criteria

- [ ] The normal Shopify and Woo paths join a shared same-shop sender route for independently accepted baskets. Each basket retains one recoverable initial attempt, an independent credit and its own initial provider message ID. No second sender or charge is created for a retry.
- [ ] A captured fake Meta server sees the same selected phone-number ID for two simultaneous baskets of the same shop and recipient. A second shop uses another number if the first shop still has an open member. No extra call occurs for a new shop when all senders are occupied. The route-level clarification text transport sends on the supplied verified route number.
- [ ] Concurrent expiry, drift, terminal state or unknown dispatch never authorise a second HTTP submit. General/legacy sends cannot leak into a pool sender.
- [ ] Crash injection across tentative claim, marker clearing, credit reservation, final permit and provider response is reconciled by the defined owner.

## Validation

Create `tests/integration/whatsapp-sender-pool-dispatch.integration.test.ts` and `tests/unit/services/whatsapp-sender-pool/retry-job.test.ts`. Extend the existing focused unit suites for the changed fences/HTTP callers and worker. Use disposable PostgreSQL 17 with pgvector + Redis and a loopback fake Graph service. Commands from the prepared implementation worktree:

```bash
npm ci
npm run prisma:generate
npx vitest run tests/unit/services/whatsapp-sender-pool tests/unit/services/whatsapp.service.test.ts tests/unit/services/routing-guidance.service.test.ts tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts tests/unit/workers/pending-recovery-candidate.worker.test.ts
node scripts/test-integration.mjs tests/integration/whatsapp-sender-pool-dispatch.integration.test.ts tests/integration/arch056-initial-outreach-credit-races.integration.test.ts tests/integration/woo-initial-send-fence-races.integration.test.ts tests/integration/recovery-human-dispatch.integration.test.ts tests/integration/general-outbound-stop-fence.integration.test.ts tests/integration/arch068-conversation-image.integration.test.ts
npm run build
git diff --check
```

Prove exact Graph path and request `to` for Shopify and permitted Woo initial, follow-up, merchant and AI text/image, prepared template/terminal-text paths, and legacy general success/denial. Exercise one available number, an existing Shopify CAPACITY_BLOCKED attempt re-entering once funded with both a busy and a free pool, two non-superseded baskets for one shop/recipient sharing a sender with independent debit/receipt/follow-up lineage, sibling expiry and one remaining basket, different shops on distinct numbers, no credit on wait, automatic recovery after expiry/addition, same attempt/source key, pool drain during preparation, membership race against standalone send, changed token/WABA, changed recipient, effective expiry at final permit, worker restart after each stage, no duplicate submit after timeout, correct receipt from an older admitted message after reuse. Use real transactions and captured request counts. Force a failure on a waiter's queue publication and repair it; simulate loss of a queue job after provisional-claim commit but before billing and after reserve but before permit. Verify no current waiter is charged or looped solely because every sender is occupied. Keep legacy confirmation/repair idempotent. Confirm the Woo normal-entrypoint deployment restriction stays in force.

## Implementation Notes

Stop and refer exact evidence to the architect if a prerequisite contract is absent or conflicting. Keep all billing source selection rules intact.

Portable definition. Execute with /moda-task ARCH-076-BACKGROUND-002 following architect acceptance/integration of BACKGROUND-001. Record prepared isolated worktrees, mirrored branches/commits, database pin, changed files, exact validation results and container cleanup. Report remaining baseline failures separately. Execution status: not started.

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
