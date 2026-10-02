---
id: ARCH-025-BACKGROUND-009
architecture_id: ARCH-025
title: Extract recovery outreach follow-up processor
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
depends_on:
  - ARCH-025-BACKGROUND-008
enables:
  - ARCH-025-BACKGROUND-010
created: 2026-10-02
updated: 2026-10-02
---

# Extract recovery outreach follow-up processor

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract execution of a due no-response recovery follow-up into a bounded processor that reuses the existing follow-up scheduler and BACKGROUND-008 confirmed-send finalisation without changing admission, engagement or duplicate-send semantics.

## Context

`processRecoveryOutreachFollowUp(...)` is a distinct lifecycle from initial outreach: it runs under a checkout lock, determines due/terminal/engaged state, CAS-claims the initial attempt as no-response, creates sequence 2, re-checks shop execution eligibility and then repeats billing/template/provider admission for the follow-up. The existing `recoveryOutreachFollowUpService` remains the queue scheduling owner.

## Scope

Authorised implementation surface:

```text
src/services/checkout-recovery.service.ts
src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts
tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts
```

A directly adjacent repository-internal types file is permitted only where required to keep the extracted capability coherent.

## Out of Scope

follow-up queue scheduling service; initial outreach; snapshot mapping; materialisation; checkout/order/capacity/agent-context flows.

## Requirements

### Common ARCH-025 CheckoutRecovery invariants

- This is a **move-only structural refactor**. Do not change recovery eligibility, outreach policy, billing/capacity economics, candidate/order correlation, queue identity, provider protocol, retry behaviour, authorization, durable lifecycle semantics or CommerceAgent context meaning.
- Preserve the exact compatibility surface from `src/services/checkout-recovery.service.ts`: `CheckoutRecoveryService`, `checkoutRecoveryService`, `MaturedCandidateMaterializationResult`, `CheckoutRefreshResult`, and every current public method: `handleCheckoutCreatedContract`, `materializeMaturedCandidate`, `recordExternalActivity`, `handleCheckoutUpdatedContract`, `handleCartActivityContract`, `handleOrderCompletedContract`, `upsertRecovery`, `attachCustomer`, `resolveRecipient`, `markRecoveryMessageSent`, `handleOrderCompleted`, `handleCheckoutCreated`, `processRecoveryOutreachFollowUp`, `markRecoveryCapacityBlocked`, `resumeCapacityBlockedRecovery`, `getAgentContext`, `getAgentContextForStandaloneConversation`.
- Preserve the constructor `(billingService: RecoveryBillingService = recoveryBillingService)`. Existing workers and Commerce callers continue using the `checkoutRecoveryService` singleton; do not migrate worker entrypoints/callers as part of extraction.
- Extracted modules MUST NOT import `checkout-recovery.service.ts`; dependency direction is façade -> collaborator. Symbols moved out of the façade that are currently exported must be compatibility re-exported from it.
- Collaborator constructors are inert wiring only. Do not perform Prisma/provider/Redis/queue/environment I/O or eager model access during construction.
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

### R1 — preserve checkout-scoped execution

Load only the durable lock target first and retain `PendingRecoveryCandidateService.withCheckoutLock(shopId, checkoutToken, ...)` around the due-state reread and all follow-up decisions. Missing recovery remains `suppressed/missing-recovery`.

### R2 — preserve due/engagement decision order

Within the lock preserve: recovery + ordered attempts + conversation/customer load; `not-due`; terminal suppression; already-sent sequence-2 suppression; inbound-message lookup from `initial.sentAt`; engaged marking; `markNoResponseIfWaiting(...)` CAS; lost-CAS reread via `getOrCreate(...)`; then sequence-2 creation. Do not move customer-response detection after the no-response claim.

### R3 — preserve admission/provider flow

Execution eligibility is rechecked before template/billing/provider work. Template-unavailable marks the follow-up attempt failed. Billing admission and revalidation retain their current attempt-level `CAPACITY_BLOCKED` outcomes; this follow-up path does **not** newly call `markRecoveryCapacityBlocked(...)` on the durable recovery. Provider send uses the same deterministic idempotency key and BACKGROUND-008 finalisation. Preserve the current `providerSendCompleted` distinction so errors after a completed provider call are not sent to `handleProviderFailure(...)`.

### R4 — add missing characterization coverage

Add focused coverage for at least: missing/not-due, terminal, already-sent, engaged-before-due, lost no-response CAS, shop ineligible, template unavailable, admission block, revalidation block, provider failure, duplicate confirmed send, duplicate pending/missing durable message and successful sequence-2 send.

## Work Items

- [ ] Extract the follow-up processor and leave `processRecoveryOutreachFollowUp` as façade delegate.
- [ ] Reuse BACKGROUND-008 confirmed-send finalisation.
- [ ] Keep `recoveryOutreachFollowUpService` as scheduling-only canonical owner.
- [ ] Add focused state/race/provider characterization tests.
- [ ] Prove frozen assets remain byte-identical and pass.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

- `ARCH-025-BACKGROUND-008`

## Enables

- `ARCH-025-BACKGROUND-010`

## Acceptance Criteria

- [ ] Follow-up execution is isolated from initial outreach and queue scheduling.
- [ ] Checkout lock and no-response CAS/engagement race semantics are unchanged.
- [ ] No second billing, scheduling or provider-send implementation is introduced.
- [ ] Existing worker call through `checkoutRecoveryService.processRecoveryOutreachFollowUp` remains compatible.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/services/matured-candidate.materialization.test.ts':'28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb','tests/unit/services/checkout-refresh.test.ts':'3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f','tests/unit/services/order-recovery-correlation.test.ts':'7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf','tests/unit/services/checkout-recovery.capacity-resume.test.ts':'8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values
- [ ] `git diff -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` is empty
- [ ] `npm test -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` passes
- [ ] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes
- [ ] `npm test` introduces no regression
- [ ] `npm run build` succeeds
- [ ] `git diff --check` passes
- [ ] `npm test -- tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts` passes

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
