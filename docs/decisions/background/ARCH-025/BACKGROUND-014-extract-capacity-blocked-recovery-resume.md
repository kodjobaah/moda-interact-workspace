---
id: ARCH-025-BACKGROUND-014
architecture_id: ARCH-025
title: Extract capacity-blocked recovery resume
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-BACKGROUND-013
enables:
  - ARCH-025-BACKGROUND-015
created: 2026-10-02
updated: 2026-10-02
---

# Extract capacity-blocked recovery resume

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract per-recovery durable capacity-blocked resume/terminalisation while retaining `RecoveryCapacityResumeService` as the queue/repair scheduler and reusing canonical snapshot/initiation owners.

## Context

`resumeCapacityBlockedRecovery(...)` is a separate retry lifecycle: it validates durable block state and shop status, checks execution eligibility outside and inside the checkout lock, refreshes current Shopify checkout state, terminalises unrecoverable blocked recoveries atomically, or re-enters the canonical recovery initiation path. Queue/repair scheduling already belongs to `RecoveryCapacityResumeService` and must remain there.

## Scope

Authorised implementation surface:

```text
src/services/checkout-recovery.service.ts
src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts
tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts
```

A directly adjacent repository-internal types file is permitted only where required to keep the extracted capability coherent.

## Out of Scope

RecoveryCapacityResumeService queue/repair implementation; billing admission implementation; snapshot mapping; initial outreach; schema.

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

### R1 — durable admission-block authority

Only a durable `DETECTED` recovery with `admissionBlockReason = RECOVERY_CAPACITY_EXHAUSTED` is eligible. Preserve inactive-shop and execution-eligibility short-circuits before provider work. Preserve the checkout lock and durable reread after lock; an already transitioned/cleared recovery remains a no-op.

### R2 — provider lookup outcomes

Lookup uses the durable recovery's shop/checkout/cart/url/detectedAt. `provider-error`, `ambiguous` and `bounded-limit-exceeded` retain current thrown/retryable behaviour. `not-found` or a completed checkout terminalises the blocked recovery. Preserve the current externally returned terminal reason quirk: not-found returns `{ kind: "terminal", reason: "not-found" }`, while a found-but-completed checkout returns `{ kind: "terminal", reason: "found" }`; do not normalise the latter to `completed`.

### R3 — terminalisation transaction

Move `terminalizeUnrecoverableBlockedRecovery(...)` with this processor. Preserve one Prisma transaction with status/block CAS, `CANCELLED`, `expiredAt = new Date()`, clearing block fields and status-history creation only when update count is one. Keep source `recovery-capacity-resume` and current reason strings.

### R4 — canonical re-entry with frozen façade-call compatibility

For a still-abandoned checkout, reuse BACKGROUND-010 snapshot mapping and BACKGROUND-008 initiation using the current generation. The frozen capacity-resume suite replaces `service.handleCheckoutCreated` and expects `resumeCapacityBlockedRecovery(...)` to invoke that **current replaceable façade method**. Preserve that observable relationship with a narrow dynamic callback/port that resolves `this.handleCheckoutCreated` at invocation time; do not eagerly bind the original method in the constructor and do not reverse-import the façade from the processor.

Preserve call arity exactly: generation 1 calls `handleCheckoutCreated(seed)` with one argument; only later generations call `handleCheckoutCreated(seed, generation)`. After initiation, preserve the durable reread that distinguishes `capacity-exhausted` from `initiated`. If the reread is missing, current behaviour still returns `initiated` with fallback status `DETECTED`; do not turn that into an error. Do not duplicate the initial send path.

### R5 — first-block timestamp semantics

`markRecoveryCapacityBlocked(...)` remains the BACKGROUND-008 compatibility operation that only marks an unblocked `DETECTED` recovery, preserving the original block timestamp on repeats. `markRecoveryMessageSent(...)` continues clearing capacity-block fields.

## Work Items

- [ ] Extract per-recovery capacity resume/terminalisation and façade delegate.
- [ ] Keep RecoveryCapacityResumeService unchanged as scheduling/repair owner.
- [ ] Reuse snapshot builder and initiation service for re-entry.
- [ ] Add focused tests for eligibility/lock reread/provider outcomes/terminalisation/re-entry and duplicate replay.
- [ ] Run capacity-resume worker tests and frozen capacity suite.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

- `ARCH-025-BACKGROUND-013`

## Enables

- `ARCH-025-BACKGROUND-015`

## Acceptance Criteria

- [ ] Capacity-blocked recovery state remains durable and race-safe.
- [ ] Provider failure/unrecoverable outcomes preserve current retry/terminal behaviour.
- [ ] Re-entry uses the one canonical initiation workflow through the replaceable façade compatibility port, including current generation-1 call arity.
- [ ] Queue/repair scheduling is not duplicated or moved.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/services/matured-candidate.materialization.test.ts':'28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb','tests/unit/services/checkout-refresh.test.ts':'3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f','tests/unit/services/order-recovery-correlation.test.ts':'7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf','tests/unit/services/checkout-recovery.capacity-resume.test.ts':'8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values
- [ ] `git diff -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` is empty
- [ ] `npm test -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` passes
- [ ] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes
- [ ] `npm test` introduces no regression
- [ ] `npm run build` succeeds
- [ ] `git diff --check` passes
- [ ] `npm test -- tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts tests/unit/workers/recovery-capacity-resume.worker.test.ts` passes

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
