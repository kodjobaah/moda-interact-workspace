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
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-011
enables:
  - ARCH-025-BACKGROUND-013
created: 2026-10-02
updated: 2026-10-03
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
  - `tests/unit/services/checkout-refresh.test.ts` — SHA-256 `3330367841b6a35e5cdb15c6f8619b529b7436834da8c307d66c16e3202a36f`
  - `tests/unit/services/order-recovery-correlation.test.ts` — SHA-256 `7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf`
  - `tests/unit/services/checkout-recovery.capacity-resume.test.ts` — SHA-256 `8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1`
- Add separate focused tests for each extracted owner. Do not move assertions out of frozen files, skip tests, weaken assertions or change expected behaviour to make an extraction pass.
- Full `npm test` must introduce no regression. If a synchronized baseline failure exists, follow the durable baseline protocol; do not silently redefine expected failures inside the task.

### R1 — checkout-created contract

Move the existing `lifecycleReason(...)` mapping with this event-orchestration owner so checkout/cart denial reasons remain exactly `contract-required`, `subscription-frozen` or `shop-unavailable`.

`handleCheckoutCreatedContract(...)` remains a thin scheduling adaptation over `PendingRecoveryCandidateService.scheduleFromCheckoutCreated(...)`, preserving `discarded-shop-unavailable`, `discarded-subscription-frozen`, scheduled outcome fields and source `v2`.

### R2 — update decision precedence and exact resolved-shop read

Preserve the current direct Prisma shop lookup by **domain** selecting `id`, Shop `status` and `subscription.status`, followed by `ShopExecutionEligibilityService.evaluateResolvedShop(...)`, before candidate refresh. Do not replace this with another shop-resolution helper or add/remove a database read merely because the code moved; the frozen checkout-refresh suite observes this boundary.

A matching pending candidate is refreshed/rescheduled and returns before any durable recovery/Shopify lookup. No recovery means discard with no provider lookup. Terminal `COMPLETED/CANCELLED` means ignore with no provider lookup/write. `EXPIRED` schedules from checkout-updated and does not refresh the old recovery. Preserve the pending refresh arguments (`cartToken: null`, `isEmpty: null`, optional event international context) and the EXPIRED scheduling source fields from the durable recovery.

### R3 — active recovery refresh

Build lookup input only from durable recovery correlation/URL/detectedAt plus shop/event identity; do not use webhook basket data. `recordExternalActivity(...)` still moves forward only for active states and only when the incoming timestamp is newer, and currently occurs before the provider lookup. Provider error remains thrown. Non-found/ambiguous/bounded lookup outcomes remain discards after activity recording.

The basket refresh remains a status-guarded Prisma transaction that changes only currency, totalPrice, checkoutUrl and BACKGROUND-010 lineItems. `refreshed.count === 0` remains `already-transitioned`.

### R4 — cart activity

Cart activity continues to resolve/evaluate shop and only refresh pending candidate activity; it does not trigger Shopify lookup or create a recovery.

### R5 — result/type and WhatsApp compatibility

`CheckoutRefreshResult` belongs to this event-orchestration capability if moved, but MUST remain compatibility-exported from `checkout-recovery.service.ts`. Keep `CheckoutRecoveryService.recordExternalActivity(...)` as a delegate because `whatsapp.worker.ts` calls it directly. The monotonic update retains statuses `DETECTED`/`MESSAGE_SENT`/`ENGAGED` and `lastExternalActivityAt < activityAt`; active refresh still calls it before Shopify lookup, so provider failure/non-found outcomes do not roll back the activity timestamp.

## Work Items

- [x] Extract checkout/cart orchestrator and compatibility delegates.
- [x] Reuse BACKGROUND-008 latest query and BACKGROUND-010 line-item mapping.
- [x] Add focused tests for created scheduling, pending-first precedence, no-recovery/terminal/expired/active refresh, provider outcomes, monotonic activity and cart activity.
- [x] Run WhatsApp worker regression coverage.
- [x] Prove frozen assets remain byte-identical; the frozen aggregate retains its one documented baseline failure.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

- `ARCH-025-BACKGROUND-011`

## Enables

- `ARCH-025-BACKGROUND-013`

## Acceptance Criteria

- [x] Checkout/create/update/cart orchestration has one owner and retains exact decision order.
- [x] Webhook basket data is never used for active recovery refresh.
- [x] External activity remains monotonic and callable by WhatsApp worker.
- [x] No worker/candidate/provider API contract changes.

## Validation

- [x] `npm run prisma:generate` (passed via `npm run build`)
- [x] All four required frozen SHA-256 values match; frozen-file diff is empty.
- [x] Four frozen suites: 77 passed; the one matured-candidate language assertion matches the documented `ARCH025-BACKGROUND-TEST-001` identity.
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts`: 10/10 passed.
- [x] Full `npm test` completed; failures and the unrelated observability timeout are detailed below.
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.
- [x] Focused orchestrator and WhatsApp suites pass: 18/18 and 7/7 (25/25 combined).

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Complete

### Files Changed

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/checkout-event-orchestrator.service.ts`
- `tests/unit/services/checkout-recovery/checkout-event-orchestrator.service.test.ts`

### Work Completed

- Extracted checkout-created scheduling, external-activity recording, checkout-update refresh/restart, cart activity and lifecycle denial-reason mapping into `CheckoutEventOrchestratorService`.
- Kept `CheckoutRecoveryService`'s constructor, public methods, singleton call path and `CheckoutRefreshResult` compatibility export. The façade delegates all extracted event operations; order, materialization, outreach, capacity and context methods remain on the façade.
- Preserved the direct shop-domain query and selected fields before eligibility and candidate refresh; pending candidates still take precedence over durable lookup.
- Preserved durable recovery-derived Shopify lookup inputs, monotonic activity write before provider lookup, provider-error propagation, and the status-guarded transaction that refreshes only basket snapshot fields.
- Added 18 focused tests covering scheduling/result mapping, shop/eligibility order, pending precedence, missing/terminal/expired/active recovery, lookup outcomes, provider failure, guarded refresh races, external activity and cart activity.
- Left all frozen regression files unchanged, as confirmed by their exact hashes and empty frozen-file diff.

### Validation Results

- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- New orchestrator suite: 18/18 passed.
- Frozen `checkout-refresh` suite: 24/24 passed.
- Orchestrator plus WhatsApp worker regression: 25/25 passed.
- Entrypoint isolation: 10/10 passed.
- Four frozen suites: 77 passed / 1 failed. The failure is the exact documented `ARCH025-BACKGROUND-TEST-001` language-metadata assertion; all four frozen SHA-256 values match and the frozen-file diff is empty.
- Full `npm test`: 1,529 passed, 38 skipped, 9 failed, plus one suite-loading failure. Eight test failures and the missing ARCH-020 fixture match the durable `ARCH025-BACKGROUND-TEST-001` baseline. The additional `observability-startup` timeout occurred for `moda-recovery-worker`; it is outside the B012 change set and is the previously triaged observability preload/runtime issue recorded in B011's accepted review.
- `git diff --check`: passed.

### Deviations

The full suite reproduced the known observability-startup timeout in addition to the durable baseline failures. It is reported for Architect Review; no baseline, observability code or unrelated tests were changed.

### Assumptions

None

### Unresolved Issues

The known `ARCH025-BACKGROUND-TEST-001` failures remain. The unrelated observability-startup timeout also occurred in the full run, consistent with the separate issue already documented in B011's accepted review.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

Accepted. `CheckoutEventOrchestratorService` is a move-only extraction of checkout-created scheduling, checkout-update refresh/restart, cart activity and external-activity recording. `CheckoutRecoveryService` retains its constructor, singleton and public compatibility methods; `CheckoutRefreshResult` remains compatibility re-exported from the façade, and the WhatsApp worker continues calling `checkoutRecoveryService.recordExternalActivity(...)`.

The exact update authority/order is preserved: direct Shop lookup by domain selecting `id` / Shop `status` / `subscription.status` -> `evaluateResolvedShop(...)` -> pending-candidate refresh -> latest durable recovery -> terminal/EXPIRED decision -> monotonic external-activity write -> current Shopify lookup -> status-guarded basket refresh transaction. Pending candidates still return before durable recovery/provider reads; no recovery and terminal recovery still stop before Shopify lookup; EXPIRED still schedules a new pending generation from durable recovery fields; provider errors remain thrown after activity recording; non-found/ambiguous/bounded lookup outcomes remain discards; and active refresh still mutates only currency, total price, checkout URL and BACKGROUND-010 line items. Cart activity still resolves/evaluates Shop and only refreshes pending candidate activity.

Implementation `b0cc1c0d41a86085fdd5bafc6ba9e505a9c4182c` changes only the three authorised files against task base `9bd1afe7de220975b5c90fcc51069ad3cc623686`; parent report `d88c9f5dfbd9a86f4a2cb51b427692328ee735ff` records clean remote-aligned worktrees. Focused orchestrator tests pass 18/18, orchestrator plus WhatsApp coverage passes 25/25, entrypoint isolation passes 10/10, build/Prisma generation and `git diff --check` pass, and all four frozen hashes remain exact. The frozen aggregate remains 77/78 only for the durable `ARCH025-BACKGROUND-TEST-001` matured-candidate language assertion.

Full `npm test` has the eight durable baseline failures plus the known ARCH-020 fixture-load failure and one `observability-startup` timeout for `moda-recovery-worker`. That observability test spawns only the profile preload/shared observability runtime and reads entrypoint source; it does not execute CheckoutRecovery/B012 code, and B012 changes no observability preload, entrypoint, package or runtime file. This is the same separate preload/runtime issue already triaged in BACKGROUND-011 and is not added to `ARCH025-BACKGROUND-TEST-001`.

### Reviewed Files

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/checkout-event-orchestrator.service.ts`
- `tests/unit/services/checkout-recovery/checkout-event-orchestrator.service.test.ts`

### Validation Reviewed

- Focused orchestrator: 18/18 passed.
- Orchestrator + WhatsApp worker coverage: 25/25 passed.
- Entrypoint isolation: 10/10 passed.
- Four frozen hashes: exact; frozen-file diff empty.
- Frozen aggregate: 77 passed / 1 documented baseline failure.
- Full suite: eight durable baseline failures + known fixture-load failure + previously triaged unrelated observability preload timeout.
- `npm run build` / Prisma generation: passed.
- `git diff --check`: passed.

### Architecture Conformance

Accepted. Checkout/cart event orchestration now has one bounded owner while preserving direct Shop/eligibility reads, candidate precedence, current-Shopify trust, external-activity monotonicity, transaction boundaries, lifecycle non-reopening, façade/worker compatibility and canonical BACKGROUND-010 mapping. No candidate, materialisation, order, outreach, capacity or agent-context ownership was duplicated or moved.

### Follow-up

Track the existing `observability-startup` preload/runtime timeout separately from ARCH-025-BACKGROUND-012. Do not add it to `ARCH025-BACKGROUND-TEST-001` without same-environment baseline proof.
