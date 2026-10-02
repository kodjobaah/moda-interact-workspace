---
id: ARCH-025-BACKGROUND-012
architecture_id: ARCH-025
title: Extract checkout and cart event orchestration
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-BACKGROUND-011
enables:
  - ARCH-025-BACKGROUND-013
created: 2026-10-02
updated: 2026-10-02
---

# Extract checkout and cart event orchestration

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract checkout-create scheduling, checkout-update refresh/restart, cart activity and external-activity recording into a bounded Shopify event orchestrator without changing candidate precedence, lookup or durable refresh semantics.

## Context

The checkout/cart public methods are event orchestration, distinct from candidate materialisation and outreach. Checkout update first refreshes a pending candidate, then only if no candidate exists consults durable recovery state; active recovery refresh uses current Shopify data, terminal state never reopens, and EXPIRED schedules a new pending generation. WhatsApp also calls `recordExternalActivity(...)`, so that compatibility method must remain on the façade.

## Scope

Authorised implementation surface:

```text
src/services/checkout-recovery.service.ts
src/services/checkout-recovery/checkout-event-orchestrator.service.ts
tests/unit/services/checkout-recovery/checkout-event-orchestrator.service.test.ts
```

A directly adjacent repository-internal types file is permitted only where required to keep the extracted capability coherent.

## Out of Scope

pending-candidate service internals; materialisation; order handling; outreach; capacity resume; agent context.

## Requirements

### Common ARCH-025 CheckoutRecovery invariants

- This is a **move-only structural refactor**. Do not change recovery eligibility, outreach policy, billing/capacity economics, candidate/order correlation, queue identity, provider protocol, retry behaviour, authorization, durable lifecycle semantics or CommerceAgent context meaning.
- Preserve the exact compatibility surface from `src/services/checkout-recovery.service.ts`: `CheckoutRecoveryService`, `checkoutRecoveryService`, `MaturedCandidateMaterializationResult`, `CheckoutRefreshResult`, and every current public method: `handleCheckoutCreatedContract`, `materializeMaturedCandidate`, `recordExternalActivity`, `handleCheckoutUpdatedContract`, `handleCartActivityContract`, `handleOrderCompletedContract`, `upsertRecovery`, `attachCustomer`, `resolveRecipient`, `markRecoveryMessageSent`, `handleOrderCompleted`, `handleCheckoutCreated`, `processRecoveryOutreachFollowUp`, `markRecoveryCapacityBlocked`, `resumeCapacityBlockedRecovery`, `getAgentContext`, `getAgentContextForStandaloneConversation`.
- Preserve the constructor `(billingService: RecoveryBillingService = recoveryBillingService)`. Existing workers and Commerce callers continue using the `checkoutRecoveryService` singleton; do not migrate worker entrypoints/callers as part of extraction.
- Extracted modules MUST NOT import `checkout-recovery.service.ts`; dependency direction is façade -> collaborator. Symbols moved out of the façade that are currently exported must be compatibility re-exported from it.
- Collaborator constructors are inert wiring only. Do not perform Prisma/provider/Redis/queue/environment I/O or eager model access during construction.
- Any extracted collaborator that performs recovery billing MUST receive and reuse the exact `RecoveryBillingService` instance supplied to the `CheckoutRecoveryService` constructor. Do not silently fall back to the module singleton when a caller supplied a test/custom billing service.
- Continue reusing canonical owners: `RecoveryBillingService`, `RecoveryOutreachAttemptService`, `recoveryOutreachFollowUpService`, `RecoveryPolicyService`, `PendingRecoveryCandidateService`, `ShopExecutionEligibilityService`, `AbandonedCheckoutLookupService`, `RecoveryCapacityResumeService`, `OutboundWhatsAppAdmissionService`, `ConversationService`, `ConversationMessageService`, and `WhatsAppTemplateSelectorService`. Do not duplicate their logic.
- There remains exactly one outbound WhatsApp provider path through `OutboundWhatsAppAdmissionService`; do not create a direct Meta/provider send workflow. Deterministic outreach idempotency remains `recovery-outreach:<attemptId>`.
- Preserve all provider/network versus Prisma transaction boundaries, checkout-scoped lock boundaries, order-processed tombstone timing, status-guarded `updateMany` predicates, generation ordering and post-commit queue/provider ordering exactly. Do not move external calls into a Prisma transaction.
- Preserve stale/duplicate replay behaviour and terminal-state non-reopening. Do not convert durable capacity blocking into in-memory state.
- Preserve current data-source trust: webhook candidate/update basket/customer fields must not become durable recovery snapshot data where current Shopify lookup is authoritative.
- Preserve the integrated ARCH-024 `RecoveryAgentContext` contract: canonical `shopId`, shop domain, conversation ownership checks, language metadata and bounded history/current-message semantics.
- Do not introduce a new generic logger. If diagnostics are added, use the canonical Shared structured logger and bounded identifiers only; do not log whole checkout/customer/provider/message payloads.
- These post-ARCH-024 regression assets are frozen and MUST remain byte-for-byte unchanged:
  - `tests/unit/services/matured-candidate.materialization.test.ts` — SHA-256 `28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb`
  - `tests/unit/services/checkout-refresh.test.ts` — SHA-256 `3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f`
  - `tests/unit/services/order-recovery-correlation.test.ts` — SHA-256 `7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf`
  - `tests/unit/services/checkout-recovery.capacity-resume.test.ts` — SHA-256 `8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1`
- Add separate focused tests for each extracted owner. Do not move assertions out of frozen files, skip tests, weaken assertions or change expected behaviour to make an extraction pass.
- Full `npm test` must introduce no regression. If a synchronized baseline failure exists, follow the durable baseline protocol; do not silently redefine expected failures inside the task.

### R1 — checkout-created contract

Move the existing `lifecycleReason(...)` mapping with this event-orchestration owner so checkout/cart denial reasons remain exactly `contract-required`, `subscription-frozen` or `shop-unavailable`.

`handleCheckoutCreatedContract(...)` remains a thin scheduling adaptation over `PendingRecoveryCandidateService.scheduleFromCheckoutCreated(...)`, preserving `discarded-shop-unavailable`, `discarded-subscription-frozen`, scheduled outcome fields and source `v2`.

### R2 — update decision precedence

Preserve resolved-shop lookup/eligibility before candidate refresh. A matching pending candidate is refreshed/rescheduled and returns before any durable recovery/Shopify lookup. No recovery means discard with no provider lookup. Terminal `COMPLETED/CANCELLED` means ignore with no provider lookup/write. `EXPIRED` schedules from checkout-updated and does not refresh the old recovery.

### R3 — active recovery refresh

Build lookup input only from durable recovery correlation/URL/detectedAt plus shop/event identity; do not use webhook basket data. `recordExternalActivity(...)` still moves forward only for active states and only when the incoming timestamp is newer, and currently occurs before the provider lookup. Provider error remains thrown. Non-found/ambiguous/bounded lookup outcomes remain discards after activity recording.

The basket refresh remains a status-guarded Prisma transaction that changes only currency, totalPrice, checkoutUrl and BACKGROUND-010 lineItems. `refreshed.count === 0` remains `already-transitioned`.

### R4 — cart activity

Cart activity continues to resolve/evaluate shop and only refresh pending candidate activity; it does not trigger Shopify lookup or create a recovery.

### R5 — WhatsApp compatibility

Keep `CheckoutRecoveryService.recordExternalActivity(...)` as a delegate because `whatsapp.worker.ts` calls it directly.

## Work Items

- [ ] Extract checkout/cart orchestrator and compatibility delegates.
- [ ] Reuse BACKGROUND-008 latest query and BACKGROUND-010 line-item mapping.
- [ ] Add focused tests for created scheduling, pending-first precedence, no-recovery/terminal/expired/active refresh, provider outcomes, monotonic activity and cart activity.
- [ ] Run WhatsApp worker regression coverage.
- [ ] Prove frozen assets remain byte-identical and pass.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

- `ARCH-025-BACKGROUND-011`

## Enables

- `ARCH-025-BACKGROUND-013`

## Acceptance Criteria

- [ ] Checkout/create/update/cart orchestration has one owner and retains exact decision order.
- [ ] Webhook basket data is never used for active recovery refresh.
- [ ] External activity remains monotonic and callable by WhatsApp worker.
- [ ] No worker/candidate/provider API contract changes.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/services/matured-candidate.materialization.test.ts':'28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb','tests/unit/services/checkout-refresh.test.ts':'3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f','tests/unit/services/order-recovery-correlation.test.ts':'7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf','tests/unit/services/checkout-recovery.capacity-resume.test.ts':'8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values
- [ ] `git diff -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` is empty
- [ ] `npm test -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` passes
- [ ] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes
- [ ] `npm test` introduces no regression
- [ ] `npm run build` succeeds
- [ ] `git diff --check` passes
- [ ] `npm test -- tests/unit/services/checkout-recovery/checkout-event-orchestrator.service.test.ts tests/unit/workers/whatsapp.worker.test.ts` passes

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
