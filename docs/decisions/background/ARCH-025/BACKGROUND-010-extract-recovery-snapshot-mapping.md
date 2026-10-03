---
id: ARCH-025-BACKGROUND-010
architecture_id: ARCH-025
title: Extract canonical recovery snapshot mapping
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: copilot
claimed_at: 2026-10-03T02:05:18Z
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-009
enables:
  - ARCH-025-BACKGROUND-011
created: 2026-10-02
updated: 2026-10-03
---

# Extract canonical recovery snapshot mapping

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the canonical current-Shopify-to-RecoveryCheckoutSeed mapping and international-context resolution so materialisation, refresh and capacity resume reuse one exact snapshot shape without changing source precedence.

## Context

`toRecoverySeed(...)`, `resolveInternationalContext(...)`, `serializeLineItems(...)` and `safelyNormalize(...)` encode the durable recovery snapshot shape used by candidate materialisation and capacity resume, while checkout refresh reuses the line-item mapping. This is a stable prerequisite for moving those lifecycle handlers without duplicating mapping rules.

## Scope

Authorised implementation surface:

```text
src/services/checkout-recovery.service.ts
src/services/checkout-recovery/recovery-snapshot-builder.service.ts
src/services/checkout-recovery/recovery-mappers.ts
tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts
```

A directly adjacent repository-internal types file is permitted only where required to keep the extracted capability coherent.

## Out of Scope

candidate lifecycle decisions; provider lookup; initiation; checkout refresh lifecycle; capacity resume lifecycle; changes to Shopify normalized checkout contracts.

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

### R1 — exact durable seed shape

Preserve current seed fields and source ownership. Candidate contributes correlation/timing context only; current `NormalizedAbandonedCheckout` owns customer, basket, price, currency and recovery URL. Line-item JSON fields remain exactly `productId`, `variantId`, `title`, `variantTitle`, `sku`, `quantity`, `price`.

### R2 — preserve timestamp precedence

`detectedAt` remains `checkout.createdAt || candidate.checkoutCreatedAt || new Date().toISOString()`. `lastExternalActivityAt` is included only when candidate activity exists. Do not normalize these clock semantics as part of extraction.

### R3 — preserve international-context precedence exactly

Preserve the current, non-obvious behaviour rather than "fixing" it:

- `languageTag` comes only from normalized merchant `defaultLanguageTag`; current/event language tags are not selected here;
- `languageSource` is `merchant-default` iff that normalized merchant language exists, otherwise null;
- country: current Shopify -> event -> normalized merchant default;
- currency: current Shopify -> event -> null;
- time zone: current Shopify -> event -> normalized merchant default;
- invalid merchant defaults normalize to null rather than throw.

The one merchant settings read remains outside provider calls/transactions.

### R4 — reusable pure mapper

Keep line-item and seed-shaping code domain-specific. Do not create a generic mapping/plugin framework.

## Work Items

- [x] Extract snapshot builder and pure recovery mappers.
- [x] Replace existing callers with the same mapping boundary without changing lifecycle decisions.
- [x] Add focused precedence/invalid-default/line-item/timestamp tests.
- [x] Prove hostile or stale candidate basket/customer fields still cannot populate durable recovery state.
- [x] Prove frozen assets remain byte-identical; test outcomes match the documented baseline condition described below.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

- `ARCH-025-BACKGROUND-009`

## Enables

- `ARCH-025-BACKGROUND-011`

## Acceptance Criteria

- [x] One canonical mapping owner produces the same durable RecoveryCheckoutSeed shape.
- [x] Internationalization/source precedence is unchanged exactly.
- [x] No provider/database lifecycle semantics move into the mapping module.
- [x] Later materialisation/capacity/refresh tasks can consume the mapping without importing the façade.

## Validation

- [x] `npm run prisma:generate` (passed via `npm run build`)
- [x] Frozen asset SHA-256 values match all four required hashes.
- [x] The frozen regression-file diff is empty.
- [x] Frozen test command completed: 77 passed; the one failure in `matured-candidate.materialization.test.ts` is the documented `ARCH025-BACKGROUND-TEST-001` baseline identity.
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts`: 10/10 passed.
- [x] `npm test`: final run had 8 failures, 1,476 passed, 38 skipped, plus one suite-loading failure; every failure identity matches `ARCH025-BACKGROUND-TEST-001`, with no additional identity.
- [x] `npm run build` succeeded.
- [x] `git diff --check` passed.
- [x] `npm test -- tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts`: 7/7 passed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Ready for architect review

### Files Changed

Implementation worktree:

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/recovery-snapshot-builder.service.ts`
- `src/services/checkout-recovery/recovery-mappers.ts`
- `tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts`

Parent task worktree:

- `docs/decisions/background/ARCH-025/BACKGROUND-010-extract-recovery-snapshot-mapping.md`

### Work Completed

Extracted international-context resolution, exact RecoveryCheckoutSeed shaping, safe default normalization and line-item serialization into pure domain-specific recovery mappers. Added `RecoverySnapshotBuilderService` as the canonical boundary; it performs the existing single merchant-settings read and delegates to those pure mappers.

Materialization and capacity resume now build the same seed through the builder; checkout refresh uses its shared line-item serializer. The façade retains its public class, singleton, constructor and lifecycle decisions. Candidate fields remain limited to correlation/timing inputs, while Shopify lookup data supplies durable checkout, customer, price, currency and basket fields. No provider call, transaction, queue or lifecycle behavior was moved into the mapper module.

Added seven focused tests for current/event/merchant international precedence, merchant-only language, invalid defaults, exact line-item shape, Shopify-authoritative seed fields, hostile candidate basket/customer values, merchant settings read count and timestamp/activity fallbacks.

Launcher evidence: prepared execution was true; dependency gate passed for `ARCH-025-BACKGROUND-009`; Attempt 1 was claimed by Copilot. Claim commit: `c4d0aa403643981b42d67f37e00c48048867297b`. Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-BACKGROUND-010`, `task/ARCH-025-BACKGROUND-010`. Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-BACKGROUND-010`, `task/ARCH-025-BACKGROUND-010`. Both worktrees were newly created; task-branch fast-forward was not needed and `origin/main` was already current in both. Shared workspace/source checkouts were not switched or mutated, and no other task worktree was reused. Recursive submodule sync and init/update passed; `database` is at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

Implementation commit: `be488df` (`Extract canonical recovery snapshot builder`).

### Validation Results

Passed: focused snapshot builder tests (7/7); entrypoint isolation (10/10); Prisma generation and TypeScript compilation via `npm run build`; `git diff --check`; all four frozen asset hashes; and an empty diff for the frozen files.

The four frozen suites reported 77 passing tests and one known failure in `matured-candidate.materialization.test.ts`. That exact test identity and its language-metadata expected/actual difference are listed in `ARCH025-BACKGROUND-TEST-001`; the other three frozen suites passed. The final full suite reported 8 failed, 1,476 passed and 38 skipped across 123 files, plus the missing ARCH-020 fixture suite-load error. All failures match that durable baseline; no new failure identity appeared. An additional observability-startup timeout appeared on the first full run but the isolated suite passed 10/10 and the timeout did not recur on the final full run.

### Deviations

The task's frozen regression suite cannot be fully green without changing a frozen test or violating R3's explicit merchant-only language precedence. The exact failing assertion is a proven pre-task baseline condition, so it was left unchanged and recorded for architect review.

### Assumptions

The launcher-prepared worktrees and passed dependency gate are the authorized task execution route. `ARCH025-BACKGROUND-TEST-001` remains the applicable baseline for full-suite and frozen-suite failure identity comparison.

### Unresolved Issues

The documented `ARCH025-BACKGROUND-TEST-001` baseline remains, including the frozen matured-candidate language assertion and missing ARCH-020 fixture. No task-specific regression was observed.

### Architectural Concerns

The frozen matured-candidate test expects event language when merchant settings are absent, while this task's explicit R3 contract requires language only from normalized merchant defaults. Existing baseline evidence records that assertion as pre-task failing; architect review should resolve the test/contract mismatch in an authorized later change. The Architect Review section remains pending and untouched.

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
