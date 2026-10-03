---
id: ARCH-025-BACKGROUND-015
architecture_id: ARCH-025
title: Extract recovery agent context and finish CheckoutRecovery façade
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 80
executor: copilot
claimed_at: 2026-10-03T12:03:32Z
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-014
enables: []
created: 2026-10-02
updated: 2026-10-03
---

# Extract recovery agent context and finish CheckoutRecovery façade

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the two recovery CommerceAgent context read models and reduce `CheckoutRecoveryService` to a compatibility façade over the accepted lifecycle collaborators without changing post-ARCH-024 shop/model context semantics.

## Context

After BACKGROUND-008..014, the remaining substantive methods are the CommerceAgent read models. ARCH-024 is integrated in this baseline: `RecoveryAgentContext` contains canonical `shopId`, current recovery context verifies conversation ownership, standalone context uses `ConversationService.getAgentSnapshot`, and bounded Commerce history preserves current/prior fragments. Moving these reads last allows the public façade to become wiring/delegation only.

## Scope

Authorised implementation surface:

```text
src/services/checkout-recovery.service.ts
src/services/checkout-recovery/recovery-agent-context.service.ts
tests/unit/services/checkout-recovery/recovery-agent-context.service.test.ts
```

A directly adjacent repository-internal types file is permitted only where required to keep the extracted capability coherent.

## Out of Scope

Commerce model resolution/runtime; conversation service/history implementation; worker/Commerce caller migrations; changing RecoveryAgentContext shared/type contract.

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

### R1 — integrated ARCH-024 identity contract

Both read paths must return `shopId: recovery.shopId` and `shop: recovery.shop.domain`. Do not derive model scope from domain or remove canonical Shop identity. Preserve the exact recovery/customer fields and null conversion of totalPrice.

### R2 — current recovery conversation ownership

`getAgentContext(...)` must continue loading the requested conversation through the recovery relation and throw when the recovery is missing or the conversation does not belong to that recovery. Preserve conversation type/summary/inboundVersion/language fields and languageSource normalization.

### R3 — bounded history

Continue calling `loadCommerceHistory(conversationId, pendingTurnStartedAt ?? new Date())`; current messages, prior history and `oversized` remain separate. Equal timestamps retain `createdAt ASC, id ASC` ordering through the existing history owner. Do not reimplement history loading.

### R4 — standalone conversation context

`getAgentContextForStandaloneConversation(...)` continues loading the recovery/shop/customer then delegates to `ConversationService.getAgentSnapshot(conversationId, pendingTurnStartedAt)` and overlays the recovery shop domain. Unlike `getAgentContext(...)`, the standalone path does not load the conversation through the recovery relation; do not add a new ownership check as incidental hardening. Preserve current error semantics.

### R5 — final façade and compatibility wiring

After extraction, `CheckoutRecoveryService` should contain constructor/wiring, compatibility re-exports and thin delegates only. All 17 existing public methods and both exported result types remain available from `checkout-recovery.service.ts`. Do not migrate callers in this task.

The final thin façade MUST retain the dynamic compatibility ports established earlier in this chain: initial outreach can still observe a replaced/spied `upsertRecovery(...)`, and capacity resume can still observe a replaced/spied `handleCheckoutCreated(...)`. Do not simplify those callbacks into eagerly bound collaborator methods during final cleanup. This preserves the frozen post-ARCH-024 regression contract without moving lifecycle logic back into the façade.

### R6 — no hidden framework

Do not introduce a service locator, generic repository, command bus or new cross-service contract merely to wire the façade.

## Work Items

- [x] Extract current/standalone agent context read service and façade delegates.
- [x] Preserve canonical shopId/domain and existing bounded history/ownership semantics.
- [x] Reduce CheckoutRecoveryService to compatibility wiring/delegation across BACKGROUND-008..015 owners.
- [x] Add focused context tests including missing recovery, ownership failure, canonical shopId/domain, standalone snapshot and equal-timestamp bounded history.
- [x] Run WhatsApp/voice/context regressions and all frozen assets.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

- `ARCH-025-BACKGROUND-014`

## Enables

None

## Acceptance Criteria

- [x] Agent-context reads have one owner and retain the integrated ARCH-024 contract exactly.
- [x] CheckoutRecoveryService is a thin compatibility façade with no full lifecycle implementation remaining and retains the accepted dynamic compatibility ports required by frozen façade-spy tests.
- [x] All existing worker/Commerce callers continue using the same public singleton/methods.
- [ ] Frozen regression assets remain byte-identical and all required tests/build pass. The assets are byte-identical, but the frozen aggregate retains its documented `ARCH025-BACKGROUND-TEST-001` language-metadata failure; see Validation Results.

## Validation

- [x] `npm run prisma:generate` passes.
- [x] The four frozen SHA-256 values match exactly.
- [x] `git diff -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` is empty.
- [x] The four frozen suites ran: 77 passed, 1 failed. The sole failure is the unchanged matured-candidate language assertion in durable baseline `ARCH025-BACKGROUND-TEST-001`.
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts`: 10/10 passed.
- [x] `npm test` completed: 1,579 passed, 38 skipped, 10 failed across 5 failed files, plus 1 suite-loading failure (113 passed, 15 skipped). Eight test failures and the missing ARCH-020 fixture match `ARCH025-BACKGROUND-TEST-001`; the other two failures are observability-startup timeouts in the separately triaged preload/runtime class. No changed context test or required caller regression failed.
- [x] `npm run build` succeeds; Prisma generation and TypeScript compilation pass.
- [x] `git diff --check` passes.
- [x] `npm test -- tests/unit/services/checkout-recovery/recovery-agent-context.service.test.ts tests/unit/workers/whatsapp.worker.test.ts tests/integration/commerce/voice-workflow.test.ts`: 3 files, 19/19 passed. The dedicated context suite passes 6/6; frozen checkout-refresh passes 24/24.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Review

### Files Changed

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/recovery-agent-context.service.ts`
- `tests/unit/services/checkout-recovery/recovery-agent-context.service.test.ts`

### Work Completed

- Extracted both context read paths into `RecoveryAgentContextService`; the public façade retains constructor/singleton compatibility and delegates both methods.
- Preserved recovery shopId/domain, attached conversation ownership checks, field/null mapping, language normalization, bounded history delegation, standalone snapshot delegation and its existing error semantics.
- Preserved the previously established dynamic façade callbacks for outreach and capacity resume; no caller migration or lifecycle-policy change was made.
- Added six focused tests covering context mapping, equal-timestamp loader-order preservation, fallback boundary, missing recovery, foreign conversation, standalone snapshot, canonical shop overlay and propagated snapshot errors.
- Implementation commit `9c94d2f` (`refactor(background): extract recovery agent context`) is pushed to `origin/task/ARCH-025-BACKGROUND-015`.
- Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-BACKGROUND-015`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-BACKGROUND-015`; both task branches are `task/ARCH-025-BACKGROUND-015`. Shared workspace/source checkouts were not switched or mutated, and no other task worktree was reused. Parent and implementation task refs required no fast-forward; both already incorporated origin/main. Recursive submodule sync/update passed; database submodule recorded at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

### Validation Results

- `npm run prisma:generate`: passed.
- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- Dedicated context service tests: 6/6 passed.
- Frozen checkout-refresh façade regression: 24/24 passed.
- Context + WhatsApp worker + voice workflow regressions: 3 files, 19/19 passed.
- Entrypoint isolation: 10/10 passed.
- Frozen aggregate: 77/78 passed. The one failure is the durable `ARCH025-BACKGROUND-TEST-001` matured-candidate Shopify language-metadata assertion. All four frozen files match their specified SHA-256 values and their diff is empty.
- Full `npm test`: 1,579 passed, 38 skipped, 10 failed, plus one suite-loading failure. The 8 durable failures and missing ARCH-020 fixture match `ARCH025-BACKGROUND-TEST-001`; two observability-startup timeouts are the separately triaged preload/runtime issue, outside the changed files.
- `git diff --check`: passed.

### Deviations

No implementation-scope deviation. The frozen aggregate and full suite retain the documented baseline failures above; no baseline, frozen test or unrelated source was changed.

### Assumptions

None

### Unresolved Issues

The durable `ARCH025-BACKGROUND-TEST-001` failures and separately triaged observability-startup timeout class remain for Architect Review; all required changed-slice tests and build checks pass.

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
