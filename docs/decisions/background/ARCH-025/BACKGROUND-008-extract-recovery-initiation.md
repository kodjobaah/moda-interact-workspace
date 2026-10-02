---
id: ARCH-025-BACKGROUND-008
architecture_id: ARCH-025
title: Extract recovery initiation and confirmed-send finalisation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-025-BACKGROUND-009
created: 2026-10-02
updated: 2026-10-02
---

# Extract recovery initiation and confirmed-send finalisation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the canonical DETECTED -> initial proactive outreach workflow, confirmed-send finalisation and the one small latest-recovery query primitive behind the unchanged `CheckoutRecoveryService` façade without changing billing, provider-send or follow-up semantics.

## Context

`handleCheckoutCreated(...)` currently combines durable recovery creation/generation, customer association, template selection, billing admission/revalidation, conversation creation, provider send/idempotency, durable-message confirmation, billing commit, outreach-attempt state and follow-up scheduling. Later materialisation and capacity-resume tasks both need this canonical initiation owner. The current `findLatestRecovery(...)` generation-order query is also reused by creation/materialisation/refresh, so this task establishes one small CheckoutRecovery-specific query primitive rather than duplicating that rule.

## Scope

Authorised implementation surface:

```text
src/services/checkout-recovery.service.ts
src/services/checkout-recovery/recovery-initiation.service.ts
src/services/checkout-recovery/recovery-outreach-finalization.service.ts
src/services/checkout-recovery/latest-recovery.ts
tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts
```

A directly adjacent repository-internal types file is permitted only where required to keep the extracted capability coherent.

## Out of Scope

matured candidate orchestration; checkout/update/cart handlers; follow-up execution; order correlation; capacity-resume processor; agent-context reads; edits to canonical billing/outreach/WhatsApp/conversation services.

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

### R1 — canonical initial outreach owner

Move the implementation of `handleCheckoutCreated(...)` and its directly owned helpers (`upsertRecovery`, `attachCustomer`, `resolveRecipient`, `markRecoveryMessageSent`, `markRecoveryCapacityBlocked`, `requireConfirmedMessage`, `finalizeConfirmedOutreach`, `ensureScheduledInitialFollowUp`, `isUniqueConflict`) behind bounded collaborators. Keep all currently public methods as thin compatibility delegates on `CheckoutRecoveryService`.

### R2 — exact initiation order

Preserve the current order and failure isolation:

```text
upsert/reuse durable recovery generation
 -> resolve/attach customer
 -> if already MESSAGE_SENT/ENGAGED: repair initial follow-up scheduling and stop
 -> resolve policy + get/create sequence-1 attempt
 -> resolve recipient
 -> select approved/provider-check-required template
 -> billing admit
 -> if capacity-exhausted: durably mark recovery blocked + attempt CAPACITY_BLOCKED
 -> create/reuse recovery Conversation
 -> billing revalidate
 -> provider send through OutboundWhatsAppAdmissionService
 -> resolve duplicate admission / require confirmed durable message
 -> commit successful billing initiation
 -> mark attempt WAITING_FOR_RESPONSE
 -> move DETECTED recovery to MESSAGE_SENT using confirmed sentAt
 -> schedule initial follow-up when due
```

Conversation creation failure must still release the admission before any provider call. Provider-call failure must still route through `RecoveryBillingService.handleProviderFailure(...)` and mark the attempt `FAILED/PROVIDER_FAILURE`. A post-send durable-confirmation/finalisation error must not be reclassified as a pre-provider failure.

### R3 — duplicate and confirmation semantics

Preserve `recovery-outreach:<attemptId>` exactly. Duplicate suppression may converge only from a durable message in `SENT`, `DELIVERED` or `READ` with matching conversation and non-null `sentAt`; `PENDING`, missing or mismatched durable messages retain the current error behaviour.

### R4 — finalisation reuse

Put confirmed-send finalisation behind one collaborator that BACKGROUND-009 can reuse. Do not duplicate billing commit, attempt transition or confirmed-message validation between initial and follow-up paths.

### R5 — latest generation query

Move the current latest-recovery read into a small CheckoutRecovery-specific primitive preserving `orderBy: [{ generation: "desc" }, { id: "desc" }]`. Do not introduce a generic repository framework.

## Work Items

- [ ] Extract initiation + finalisation collaborators and wire façade delegates.
- [ ] Preserve public low-level compatibility delegates used by existing tests/callers.
- [ ] Extract the latest-generation query primitive with identical ordering.
- [ ] Add focused tests for blocked admission, conversation failure/release, revalidation block, provider failure, duplicate confirmed send, pending/missing duplicate, successful confirmed send and replay/follow-up repair.
- [ ] Prove all frozen assets remain byte-identical and pass.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

None

## Enables

- `ARCH-025-BACKGROUND-009`

## Acceptance Criteria

- [ ] Initial recovery outreach is owned outside the façade and follows the same I/O/transition order.
- [ ] Billing admission/commit/release/provider-failure semantics are unchanged.
- [ ] Provider send still has one deterministic admission/idempotency path.
- [ ] Confirmed-send finalisation is reusable by the follow-up task without importing the façade.
- [ ] Existing public methods/constructor remain compatible and frozen assets pass.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/services/matured-candidate.materialization.test.ts':'28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb','tests/unit/services/checkout-refresh.test.ts':'3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f','tests/unit/services/order-recovery-correlation.test.ts':'7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf','tests/unit/services/checkout-recovery.capacity-resume.test.ts':'8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values
- [ ] `git diff -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` is empty
- [ ] `npm test -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` passes
- [ ] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes
- [ ] `npm test` introduces no regression
- [ ] `npm run build` succeeds
- [ ] `git diff --check` passes
- [ ] `npm test -- tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts` passes

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
