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
attempt: 1
depends_on: []
enables:
  - ARCH-025-BACKGROUND-009
created: 2026-10-02
updated: 2026-10-03
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
- Any extracted collaborator/finaliser that performs recovery billing MUST receive and reuse the exact `RecoveryBillingService` instance supplied to the `CheckoutRecoveryService` constructor. Do not silently fall back to the module singleton when a caller supplied a custom/test billing service.
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

### R1 — canonical initial outreach owner and façade-observable operations

Move the implementation of `handleCheckoutCreated(...)`, persistence/idempotency helpers and confirmed-send finalisation behind bounded collaborators while keeping every currently public low-level method as a thin compatibility delegate on `CheckoutRecoveryService`.

The frozen `checkout-refresh.test.ts` replaces `service.upsertRecovery` and then invokes `service.handleCheckoutCreated(...)`. Preserve that observable relationship: initial outreach must call the **current replaceable façade `upsertRecovery(...)` operation** rather than bypassing it with a collaborator-private call. Use a narrow dynamic port/callback such as `(...args) => this.upsertRecovery(...args)` that resolves the façade method at invocation time; do not eagerly bind/capture the original method in the constructor, and do not reverse-import `checkout-recovery.service.ts` from the collaborator. Preserve the same current façade-call relationship for `resolveRecipient(...)` and `markRecoveryCapacityBlocked(...)`.

`attachCustomer(...)` and `markRecoveryMessageSent(...)` are public compatibility operations but are **not** the operations currently used by `handleCheckoutCreated(...)`. Do not consolidate semantics during extraction: customer attachment in initial outreach remains the direct `checkoutRecovery.update(...)` performed only when the resolved customer differs, while confirmed-send recovery transition remains the finaliser's `updateMany(...)` using the provider-confirmed `message.sentAt`. `markRecoveryMessageSent(...)` continues using its own `new Date()` compatibility semantics and must not replace confirmed-send finalisation.

### R2 — exact initiation order and asymmetric suppression semantics

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

Preserve these current initial-outreach distinctions exactly:

- `template-unavailable` / `market-unavailable` (or any selection other than `selected` / `provider-check-required`) returns the current recovery without provider/billing/conversation work and **does not** newly mark the sequence-1 attempt failed/cancelled;
- an initial billing admission blocked for exact reason `capacity-exhausted` calls the durable `markRecoveryCapacityBlocked(...)` operation and marks the attempt `CAPACITY_BLOCKED` without inventing a new failure code; other initial admission-block reasons return the recovery without introducing a new durable recovery block or attempt transition;
- a revalidation block marks the attempt `CAPACITY_BLOCKED` with the revalidation reason but does **not** newly call `markRecoveryCapacityBlocked(...)`; preserve the caller's current release/no-release behaviour rather than adding cleanup that is not present today;
- `resolveRecipient(...)` continues preferring `event.customer.phone`, then `TEST_WHATSAPP_RECIPIENT`, and throws when neither is available. Follow-up processing does not reuse this fallback.

### R3 — duplicate and confirmation semantics

Preserve `recovery-outreach:<attemptId>` exactly. Duplicate suppression may converge only from a durable message in `SENT`, `DELIVERED` or `READ` with matching conversation and non-null `sentAt`. A duplicate with `PENDING` still throws "send is still pending"; a duplicate with no durable admission still throws "has no durable message"; a confirmed-status message with wrong conversation/missing `sentAt` still fails `requireConfirmedMessage(...)`. Other non-confirmed durable statuses continue through the ordinary suppressed path: release the admission, mark the attempt `FAILED` with the suppression reason (including `duplicate`) and return the suppressed result. Do not normalise these branches.

### R4 — finalisation reuse and idempotent convergence

Put confirmed-send finalisation behind one collaborator that BACKGROUND-009 can reuse. Do not duplicate billing commit, attempt transition or confirmed-message validation between initial and follow-up paths. Preserve the current order: billing `commitSuccessfulInitiation(...)` first, then `markWaitingAfterConfirmedSend(...)`. If that transition returns `count === 0`, reread the attempt and converge only when it still exists, has the same `outboundMessageId`, and is not `FAILED`/`CANCELLED`; otherwise throw the existing finalisation-conflict error.

For sequence 1, preserve follow-up due-at calculation exactly: an existing attempt `followUpDueAt` wins; otherwise compute from provider `message.sentAt` only when policy follow-up is enabled and has a truthy delay. The recovery changes from `DETECTED` to `MESSAGE_SENT` using `message.sentAt` and clears capacity-block fields. Initial follow-up scheduling still requires recovery `MESSAGE_SENT`/`ENGAGED`, sequence-1 attempt `WAITING_FOR_RESPONSE`, non-null `sentAt` and `followUpDueAt`, no `customerRespondedAt`, and no sequence-2 attempt currently `WAITING_FOR_RESPONSE`/`ENGAGED`. Other sequence-2 statuses do not satisfy that suppression guard.

### R5 — latest generation query

Move the current latest-recovery read into a small CheckoutRecovery-specific primitive preserving `orderBy: [{ generation: "desc" }, { id: "desc" }]`. Do not introduce a generic repository framework.

## Work Items

- [x] Extract initiation + finalisation collaborators and wire façade delegates.
- [x] Preserve public low-level compatibility delegates used by existing tests/callers.
- [x] Extract the latest-generation query primitive with identical ordering.
- [x] Add focused tests for blocked admission, conversation failure/release, revalidation block, provider failure, duplicate confirmed send, pending/missing duplicate, successful confirmed send and replay/follow-up repair.
- [ ] Prove all frozen assets remain byte-identical and pass. Hash/diff integrity is proven; the combined command retains the single `ARCH025-BACKGROUND-TEST-001` matured-candidate baseline failure, so this literal pass claim remains open.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

None

## Enables

- `ARCH-025-BACKGROUND-009`

## Acceptance Criteria

- [x] Initial recovery outreach is owned outside the façade and follows the same I/O/transition order.
- [x] Billing admission/commit/release/provider-failure semantics are unchanged.
- [x] Provider send still has one deterministic admission/idempotency path.
- [x] Confirmed-send finalisation is reusable by the follow-up task without importing the façade.
- [ ] Existing public methods/constructor remain compatible and the frozen `upsertRecovery` façade-spy relationship remains observable. The literal final clause “frozen assets pass” remains baseline-red only because `matured-candidate.materialization.test.ts` retains its documented `ARCH025-BACKGROUND-TEST-001` failure.

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/services/matured-candidate.materialization.test.ts':'28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb','tests/unit/services/checkout-refresh.test.ts':'3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f','tests/unit/services/order-recovery-correlation.test.ts':'7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf','tests/unit/services/checkout-recovery.capacity-resume.test.ts':'8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values
- [x] `git diff -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` is empty
- [ ] `npm test -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` passes — not claimed: the unchanged matured-candidate suite retains its documented `ARCH025-BACKGROUND-TEST-001` failure; the checkout-refresh suite passes 24/24 after the extraction-introduced typo was corrected before submission.
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes
- [x] `npm test` introduces no regression
- [x] `npm run build` succeeds
- [ ] `git diff --check` passes
- [x] `npm test -- tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts` passes

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Review

### Files Changed

- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/src/services/checkout-recovery/recovery-initiation.service.ts`
- `moda-interact-background/src/services/checkout-recovery/recovery-outreach-finalization.service.ts`
- `moda-interact-background/src/services/checkout-recovery/latest-recovery.ts`
- `moda-interact-background/tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`

### Work Completed

- Extracted canonical initial recovery outreach into `RecoveryInitiationService` while preserving `CheckoutRecoveryService.handleCheckoutCreated(...)` as the public compatibility surface.
- Wired narrow invocation-time façade ports for `upsertRecovery(...)`, `resolveRecipient(...)` and `markRecoveryCapacityBlocked(...)`, preserving the frozen replaceable-method/spying relationship rather than eagerly binding the original methods.
- Extracted confirmed durable-message validation, successful billing commit, outreach-attempt transition, `DETECTED -> MESSAGE_SENT` projection and initial follow-up scheduling into `RecoveryOutreachFinalizationService`. The finaliser receives the same `RecoveryBillingService` instance supplied to `CheckoutRecoveryService`.
- Reused that finalisation owner from the existing follow-up path without moving follow-up orchestration itself into this task.
- Extracted the CheckoutRecovery-specific latest-generation lookup into `latest-recovery.ts` with unchanged `generation desc, id desc` ordering.
- Preserved initial-outreach ordering and asymmetric suppression/error handling: template non-selection returns without billing/provider work; exact initial `capacity-exhausted` persists the recovery block; revalidation blocking does not newly persist that block; conversation creation failure releases admission; provider-send failure uses `handleProviderFailure`; post-send confirmation/finalisation errors are not reclassified as provider failures.
- Corrected the checkout-refresh typo introduced during the extraction before submission; the frozen `checkout-refresh.test.ts` file remained byte-identical and its suite passes 24/24.
- Added 10 focused `RecoveryInitiationService` tests covering the extracted initiation/finalisation contract.

Published implementation evidence:

```text
implementation branch: task/ARCH-025-BACKGROUND-008
implementation commit: 39dad5532d75a2df3b13fcd485b6cfab90e71e57
parent task branch before this report patch: 476e81b9c75d8530c7d7875be7ae271e0804eeb1
```

The implementation commit changes only the five authorised implementation/test files. This report-completion patch changes only this task document.

### Validation Results

- `npm run prisma:generate`: passed.
- Focused `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`: 10/10 passed.
- All four frozen SHA-256 checks match the required values; the frozen files are byte-identical.
- Frozen checkout-refresh suite: 24/24 passed after correcting the extraction-introduced checkout-refresh typo.
- Combined frozen regression command is **not** recorded as passing: `tests/unit/services/matured-candidate.materialization.test.ts` retains the documented `ARCH025-BACKGROUND-TEST-001` baseline failure. No new frozen failing test or suite identity appeared.
- `tests/unit/runtime/entrypoint-isolation.test.ts`: 10/10 passed.
- Full `npm test`: remains non-green only on the documented `ARCH025-BACKGROUND-TEST-001` failure/suite identities; no new test or suite identity appeared, so no task regression was introduced.
- Production build: passed.
- `git diff --check`: not independently rerun as part of this documentary report-completion patch; leave the literal Validation checkbox open rather than inventing evidence.

### Deviations

- The task contract literally says the combined frozen regression command must “pass”. It does not: the unchanged matured-candidate test retains one documented `ARCH025-BACKGROUND-TEST-001` baseline failure. The corresponding Work Item, Acceptance Criterion clause and Validation checkbox remain open deliberately. Hash integrity and no-regression evidence are proven.
- The full suite is also not globally green, but its failure/suite identity set matches the durable Background baseline exactly, which satisfies the no-regression requirement without redefining the baseline.

### Assumptions

- `ARCH025-BACKGROUND-TEST-001` remains the authoritative no-regression baseline for the known Background full-suite failure identities. Improvements to those baseline failures must be kept; this task does not require recreating them.
- The parent task branch will receive a new report commit when this patch is applied and published; no future report SHA is invented here.

### Unresolved Issues

- The repository-wide Background baseline remains non-green for the pre-existing failures documented by `ARCH025-BACKGROUND-TEST-001`.
- The literal combined-frozen-suite “passes” gate remains open solely because of the baseline-red matured-candidate identity.
- `git diff --check` remains unclaimed in this report because that execution result was not part of the supplied final evidence.

### Architectural Concerns

None identified. The implementation review found no source-level correction required before Architect disposition.

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

## Developer Override - Reopen (2026-10-03)

- Previous accepted attempt: none. Attempt 1 was submitted for architect review and remains unaccepted.
- Reopen reason: the developer explicitly requested reopening this task. The Attempt 1 Completion Report leaves the literal frozen-suite pass criterion open because the unchanged matured-candidate suite has its documented `ARCH025-BACKGROUND-TEST-001` failure, and it leaves `git diff --check` unclaimed. Reopening permits another agent execution cycle to address the remaining task gates while preserving all Attempt 1 implementation and validation evidence.
- Reopen transition: `review` -> `ready`; `executor` and `claimed_at` remain null; `attempt` remains `1`.
- This reopen is not a claim. The next `/moda-task` preparation may claim Attempt 2 once its normal synchronization and dependency gates pass.
