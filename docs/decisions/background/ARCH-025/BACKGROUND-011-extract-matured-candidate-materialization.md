---
id: ARCH-025-BACKGROUND-011
architecture_id: ARCH-025
title: Extract matured candidate materialisation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-010
enables:
  - ARCH-025-BACKGROUND-012
created: 2026-10-02
updated: 2026-10-03
---

# Extract matured candidate materialisation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the matured pending-candidate -> durable CheckoutRecovery lifecycle behind `materializeMaturedCandidate(...)`, preserving checkout/order race guards, provider outcome semantics, generation selection and canonical initiation.

## Context

Matured-candidate materialisation is a complete lifecycle: execution eligibility is checked before and after acquiring the checkout lock, an order tombstone suppresses recovery, latest generation state determines no-op/terminal/new generation, current Shopify data is fetched, non-recoverable outcomes are discarded, then the canonical snapshot is initiated. It should be independently testable without owning outreach or Shopify lookup implementations.

## Scope

Authorised implementation surface:

```text
src/services/checkout-recovery.service.ts
src/services/checkout-recovery/recovery-materialization.service.ts
tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts
```

A directly adjacent repository-internal types file is permitted only where required to keep the extracted capability coherent.

## Out of Scope

pending-candidate queue/index implementation; initial outreach implementation; snapshot mapping; checkout updates; order correlation; capacity resume.

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

### R1 — exact race/authority order

Preserve: execution eligibility -> resolve shop domain -> checkout lock -> recheck eligibility -> order-processed tombstone -> latest recovery generation -> provider lookup -> snapshot build -> canonical initiation. Do not fetch Shopify before the locked eligibility/tombstone checks.

### R2 — exact generation/status semantics

Latest generation ordering comes from BACKGROUND-008. `DETECTED`, `MESSAGE_SENT`, `ENGAGED` remain `no-op-existing`; `COMPLETED`/`CANCELLED` remain `discarded-terminal`; other prior generations advance `generation + 1`. Do not reopen terminal recoveries.

### R3 — provider outcomes

`provider-error` remains thrown/retryable. `not-found`, `ambiguous`, `bounded-limit-exceeded`, completed checkout and order-processed tombstone remain non-creating discard outcomes with the current result strings.

### R4 — trusted source invariant

Only current Shopify lookup data and BACKGROUND-010 mapping populate durable basket/customer recovery fields. Candidate-embedded stale/hostile basket/customer fields remain ignored.

### R5 — result/type and worker compatibility

`MaturedCandidateMaterializationResult` belongs to this materialisation capability if moved, but MUST remain compatibility-exported from `checkout-recovery.service.ts`. `recovery-created` continues to mean that a durable recoverable snapshot reached canonical initiation; it does **not** guarantee that WhatsApp was sent (bounded template selection or billing/revalidation suppression can still leave the materialisation result as `recovery-created`).

Preserve the current initiation invocation shape: generation 1 calls initiation with the seed only; later generations pass the explicit generation. `pending-recovery-candidate.worker.ts` continues invoking `checkoutRecoveryService.materializeMaturedCandidate(...)`; do not migrate the worker.

## Work Items

- [x] Extract the materialisation service and façade delegate.
- [x] Reuse BACKGROUND-008 latest query/initiation and BACKGROUND-010 snapshot builder.
- [x] Add focused tests for every current result kind, generation transition, double eligibility check and order race guard.
- [x] Run pending-candidate worker coverage.
- [x] Prove frozen assets remain byte-identical; the frozen aggregate retains its one documented baseline failure.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

- `ARCH-025-BACKGROUND-010`

## Enables

- `ARCH-025-BACKGROUND-012`

## Acceptance Criteria

- [x] Materialisation has one lifecycle owner and no duplicate outreach/mapping/provider implementation.
- [x] Checkout lock/order tombstone and provider outcome semantics are unchanged.
- [x] Candidate basket/customer data still cannot become recovery state; current Shopify data and BACKGROUND-010 builder remain authoritative.
- [x] Worker-facing public method remains compatible.

## Validation

- [x] `npm run prisma:generate` (passed via `npm run build`)
- [x] All four required frozen SHA-256 values match; frozen-file diff is empty.
- [x] Four frozen suites: 77 passed; the one matured-candidate language assertion matches the documented `ARCH025-BACKGROUND-TEST-001` identity.
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts`: 10/10 passed.
- [x] `npm test` completed; results and the unrelated observability timeout are detailed below.
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.
- [x] Focused materialization and worker suites pass: 15/15 and 1/1.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Complete

### Files Changed

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/recovery-materialization.service.ts`
- `tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts`

### Work Completed

- Extracted matured-candidate eligibility, checkout lock, order tombstone, latest-generation decisions, Shopify lookup outcome handling, snapshot building, and canonical initiation into `RecoveryMaterializationService`.
- Kept the façade method, singleton, constructor, worker call path, and initiation ownership intact. Re-exported `MaturedCandidateMaterializationResult` from the façade for type compatibility.
- Preserved order: eligibility, shop-domain resolution, checkout lock, locked eligibility, order tombstone, latest generation, provider lookup, snapshot builder, initiation. Generation 1 still calls initiation without an explicit generation; later generations pass `generation + 1`.
- Kept billing and outreach in the existing façade initiation path, which was constructed with the exact caller-supplied `RecoveryBillingService`; the extracted materializer does not implement billing or provider transport.
- Added 15 focused tests covering guard order, both eligibility checks, order suppression, active and terminal generations, lookup discard outcomes, retryable provider errors, completed checkout, and generation invocation shape.
- Left the four frozen tests, B010 task report, and all observability files unchanged.

### Validation Results

- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- Focused materialization suite: 15/15 passed.
- Pending-recovery-candidate worker suite: 1/1 passed.
- Entrypoint isolation: 10/10 passed.
- Four frozen suites: 77 passed / 1 failed. The failing language-metadata assertion is the exact documented `ARCH025-BACKGROUND-TEST-001` identity; all four file hashes match their required values and the frozen diff is empty.
- Full `npm test`: 1,498 passed, 38 skipped, 9 failed, plus one suite-loading failure. The eight established failures and missing ARCH-020 fixture match `ARCH025-BACKGROUND-TEST-001`. One `observability-startup` case timed out for `moda-recovery-worker` during the full run; an isolated run also timed out for `moda-shopify-event-worker`, and a single-profile rerun timed out for that same profile. The observability test and runtime files are outside the task change set.
- `git diff --check`: passed.

### Deviations

The full suite includes a reproducible observability-startup timeout not listed in the durable baseline and outside B011's changed files. It is reported for Architect Review; the baseline and unrelated observability code were not modified.

### Assumptions

None

### Unresolved Issues

The known `ARCH025-BACKGROUND-TEST-001` failures remain. Additionally, one observability preload probe timeout reproduced in isolation for the Shopify-event worker profile; this is outside B011 scope and needs separate baseline/owner triage.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

Accepted. `RecoveryMaterializationService` is a move-only extraction of the matured-candidate lifecycle. The façade retains `materializeMaturedCandidate(...)`, singleton/constructor compatibility and the `MaturedCandidateMaterializationResult` re-export. The exact authority order remains eligibility -> shop-domain resolution -> checkout lock -> locked eligibility -> order tombstone -> latest generation -> Shopify lookup -> BACKGROUND-010 snapshot build -> canonical initiation. Active generations remain no-op, terminal generations remain closed, provider errors remain retryable, and generation 1 still invokes initiation without an explicit generation while later generations pass the incremented generation.

Implementation `4ae8c61c1e24d82a94158a58f4f6bf339e0f9960` changes only the three authorised files. Focused materialisation tests pass 15/15, pending-candidate worker coverage passes 1/1, entrypoint isolation passes 10/10, build/Prisma generation and `git diff --check` pass, and all four frozen hashes remain exact. The frozen aggregate's one matured-candidate language assertion is the existing `ARCH025-BACKGROUND-TEST-001` identity.

The additional `observability-startup` timeout is not added to the durable baseline. It reproduces in an isolated observability probe, but that probe imports only the shared observability preload/runtime and does not import `checkout-recovery.service.ts`, `RecoveryMaterializationService`, or any B011 file. B011 leaves the observability test/preload/runtime/package inputs unchanged, so the timeout is an unrelated runtime/observability issue for separate owner triage rather than a materialisation regression.

### Reviewed Files

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/recovery-materialization.service.ts`
- `tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts`

### Validation Reviewed

- Focused materialisation: 15/15 passed.
- Pending-candidate worker coverage: 1/1 passed.
- Entrypoint isolation: 10/10 passed.
- Four frozen hashes: exact; frozen-file diff empty.
- Frozen aggregate: 77 passed / 1 documented baseline failure.
- Full suite: eight durable baseline failures + known fixture-load failure, plus one unrelated reproducible observability preload timeout.
- `npm run build` / Prisma generation: passed.
- `git diff --check`: passed.

### Architecture Conformance

Accepted. The extracted capability has one lifecycle owner, preserves the trusted-current-Shopify snapshot boundary and all checkout/order race guards, and does not duplicate outreach, mapping, billing or provider implementations.

### Follow-up

Track the reproducible `observability-startup` preload timeout separately from ARCH-025-BACKGROUND-011. Do not add it to `ARCH025-BACKGROUND-TEST-001` without same-environment baseline proof.
