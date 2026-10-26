---
id: ARCH-046-BACKGROUND-004
architecture_id: ARCH-046
title: Enforce final Woo initial-recovery WhatsApp send consent and STOP fence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 38
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-046-BACKGROUND-001
  - ARCH-046-BACKGROUND-002
  - ARCH-045-BACKGROUND-005
  - ARCH-048-BACKGROUND-004
enables:
  - ARCH-048-BACKGROUND-005
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-26
---

# Enforce final Woo initial-recovery WhatsApp send consent and STOP fence

## Architecture

Architecture ID: `ARCH-046`.

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`.

Coordinator: `moda_architect`.

**Execution frontier (26 October 2026): Architect review accepted; developer explicitly completed Attempt 3.** All four dependencies were verified Complete by the canonical launcher. Attempt 3 was claimed at `2026-10-26T03:59:19Z`; the implementation worktree was synchronized with current Background `origin/main` in merge `e88d9345015202e915a9198d4c6803f41e9adfdb`. Focused unit, PostgreSQL/Redis, HUMAN/AI/general STOP, lint, typecheck, build and diff checks passed after that synchronization. Architect acceptance and the developer completion decision are recorded below. Scope remains limited to initial send and sequence-one retries; Woo follow-ups remain out of scope.

## Execution Ownership Amendment

On 25 October 2026, the developer explicitly took over this ready agent-owned task through `/moda_developer_create`. Execution and completion authority are now developer-controlled; `assigned_agent: moda_background`, task scope, dependencies and acceptance criteria are unchanged. Attempt 1 was claimed at `2026-10-25T16:39:00Z` after all explicit dependencies were verified Complete and both canonical task worktrees were prepared. This amendment records execution ownership only; no feature implementation has started.

## Objective

Implement a **Woo-specific, consent- and STOP-guarded final provider-admission sender** for the initial abandoned-checkout recovery template, including retries/reentries of the same initial attempt, by satisfying the existing `WooGuardedInitialSender` contract used by accepted `ARCH-048-BACKGROUND-004`. Preserve existing billing, attempt and provider idempotency semantics. Do not enable Woo scheduled or merchant post-window follow-ups.

## Context

`src/services/woocommerce-recovery/woo-recovery-outreach.service.ts` already defines `WooGuardedInitialSender.sendInitial()` and `findExistingAdmission()`. `woo-recovery-outreach.adapters.ts` explicitly requires a reviewed guarded sender and states that the generic `OutboundWhatsAppAdmissionService.sendTemplate` is **not** an acceptable Woo final sender without a Woo-specific final SQL consent fence. The business service already performs earlier recipient, observed-order, consent, Marketing-template and billing rechecks; these **do not replace** the last durable provider-permit guard.

The STOP writer/final permit must honour the existing Shop-first transaction lock order. A provider request must happen **only after** an admission transaction has successfully committed. Current Woo order observations are event-derived; they cannot prove a payment event that never reached Moda. This limitation remains explicit.

## Scope

- Implement **one** bounded Woo initial-send guard/adapter in `moda-interact-background` (for example `src/services/woocommerce-recovery/woo-guarded-initial-sender.service.ts`) matching the already published Background-local `WooGuardedInitialSender` TypeScript interface from BG004. This is an implementation task for the final-send boundary, **not** a second Woo outreach/orchestrator business service.
- Reuse existing outbound/provider-admission, `ConversationMessage` provider dispatch key, moderation, conversation and billing services. Add only the Woo-specific admission validation needed at the final durable permit, reusing shared STOP helpers and approved locked-row ordering. If the existing infrastructure cannot satisfy the contract without a new cross-repository interface/schema, stop and return that dependency gap to the architect; **do not** imitate atomicity with a preflight-only check.
- Validate current shop installation ACTIVE/not revoked, matching Woo Shop and `CheckoutRecovery`, exact current `CustomerPhone` and recipient, `whatsappConsentDecision = GRANTED` with applicable local STOP and merchant suppression clear, and appropriate latest successfully observed order/recovery terminal evidence. Do not infer opt-in from a collected number or let a delayed native grant clear a STOP. Confirm selected template is provider-verified **Marketing**, not merely Moda catalogue-approved.
- For the final **SQL transaction**, acquire relevant locks in the established order (Shop before recipient/attempt/message rows, consistent with STOP and recovery send paths); compare current recipient/consent and no-contact revision to the caller's expected snapshot and reject stale/mismatched state. Evaluate durable recovery/attempt and already-admitted provider idempotency in the same permit decision. Check event-derived order terminal status via accepted BG002 services at the checkout-locked orchestration boundary and enforce durable terminal suppression in the permit where persisted state is available. **No external provider/Redis/network I/O inside SQL locks.** Do not claim a Redis-only observation is transactionally locked in SQL.
- On known pre-permit denial: no provider call, no permanent initial-attempt consumption and release/refund a reversible credit reservation through the existing BG004/RecoveryBillingService flow. For DB/unavailable evidence/unknown provider outcome: throw or return an explicitly retryable/reconciliation state according to the existing sender contract; do not convert it into successful `suppressed` or send a second message.
- Enforce at-most-once durable provider admission with `findExistingAdmission(idempotencyKey)` and preserve the existing `PENDING`/`SENT`/`FAILED` reconciliation behaviour of BG004. Provider-confirmed sends retain earned charges even if a later terminal event arrives. No second initial message or second credit on replay.
- Reuse approved shared structured logging; unexpected DB, recipient, provider-permit and compensation failures must be awaited, logged safely and propagated. No sensitive customer contents or tokens in logs.

## Out of Scope

- **No** scheduled sequence-two Woo follow-up, merchant-authored proactive post-window recovery template, WhatsApp recipient consent queue, new follow-up scheduler or new billing scheme. Woo `followUpDueAt` remains null; no follow-up is enabled by this task. Those capabilities require separate approval/task definitions before any activation.
- No changes to the completed first-row admission policy or its shared merchant notification service; no duplicate STOP notification. `ARCH-046-BACKGROUND-002` owns initial row-denial Support notices.
- No reimplementation of existing general-service-message guard or weakening of its STOP requirement for human/AI in-window replies. No new WordPress REST checkout reader, session access, Shopify HTTP preflight or database schema by assumption.

## Requirements

### R1 — Existing Woo sender contract (do not redefine)

```ts
interface WooGuardedInitialSender {
  sendInitial(input: {
    recovery: WooOutreachRecovery;
    attemptId: string;
    conversationId: string;
    recipient: string;
    consent: WooRecoveryConsentSnapshot;
    template: WooMarketingTemplate;
    idempotencyKey: string;
    recoveryCreditSourceKey: string;
  }): Promise<{ kind: "admitted" } | { kind: "suppressed"; reason: string }>;
  findExistingAdmission(idempotencyKey: string): Promise<PersistedMessage | null>;
}
```

The canonical declaration and `PersistedMessage` type live in `woo-recovery-outreach.service.ts`. Implement against that declaration. The caller `WooRecoveryOutreachService.processInitial()` owns attempt creation, reservation, finalization and compensation; do not duplicate its business flow.

### R2 — Final decision matrix

| Current evidence at final permit | Required behaviour |
|---|---|
| Exact recipient GRANTED; no STOP/suppression; active installation; no known terminal state; verified Marketing template; no prior provider permit | Admit **once**, then use approved provider-delivery path after SQL commit |
| Customer STOP or merchant suppression; consent withdrawn/unknown/recipient changed; shop/installation inactive | Suppress before provider permit; no Meta call; reversible credit reservation released |
| Paid/cancelled/terminal order **already observed by Moda** or terminal recovery status | Suppress without Meta send even when candidate BullMQ job is absent |
| Missing/Utility/Authentication/unverified template category | Suppress without Meta call, no credit consumed |
| Database/guard dependency unavailable or unexpected failure | Fail closed and propagate; do not claim customer refusal or mark job completed |
| Existing `PENDING` provider admission with uncertain outcome | Reconcile; **never** blindly send twice or release a potentially earned charge |
| Existing provider-confirmed `SENT`/`DELIVERED`/`READ` | Return existing admission for BG004's idempotent finalization, no new Meta call |
| Existing confirmed `FAILED` admission | Follow existing compensation/reconciliation; no second first-send attempt |

An initial-send reentry is still sequence **1** and follows the same final fence. A different checkout or shop may not reuse this attempt's provider idempotency key.

### R3 — Race boundaries, logging and rollout

- A STOP committed **before** the final permit obtains its Shop lock blocks that permit; a STOP committed **after** a completed permit may be too late to stop an already admitted provider call. Document and test this ordering honestly.
- The event-only design cannot detect a Woo payment/update event never delivered to Moda. Do not claim live Woo verification. Preserve default-off Woo send gating until developer approval after integrated system testing.
- All technical exceptions propagate to the correct worker retry/reconciliation boundary using the existing shared structured logger. No new local generic logger, swallowed exceptions, PII-rich logs, unbounded retries or Redis/provider I/O within a DB transaction.

## Work Items

- [x] Inspect accepted BG004 service and adapters, BG002 observed-order/coordination services, exact-recipient consent reader, STOP lock writer, existing outbound SQL permit and provider idempotency/billing capabilities.
- [x] Implement and inject one concrete `WooGuardedInitialSender`, using existing admission/attempt/credit primitives without copying the entire outbound sender.
- [x] Enforce the R2 matrix with correct durable permit, Meta request outside SQL and explicit compensation/uncertain-outcome handling.
- [x] Add focused injected service tests, PostgreSQL/Redis concurrency/fault-injection tests and STOP/terminal/Marketing-category regression cases; validate read-after-commit existing admissions.
- [x] Record evidence for lock ordering, credential/tenant scope, absence of DB transaction I/O and shared logger/exception propagation.

## Interfaces / Contracts

Consumes `WooGuardedInitialSender`, `WooRecoveryOutreachService` and `createWooRecoveryOutreachService()` from accepted ARCH-048-BG004; `WooRecoveryConsentReader` from ARCH-046-BG001; observed-order/checkout guard contracts from ARCH-048-BG002; CustomerPhone STOP/no-contact from ARCH-045-BG005; existing transactional outbound provider admission and billing contracts. The **final sender** is produced here for injection into ARCH-048-BG005's composition; no worker modifications in this task.

If a provider-admission schema/contract gap prevents atomic final consent/STOP checks, treat this task as blocked by a newly discovered dependency and return it to `moda_architect` rather than introducing a second unsafe sender.

## Dependencies

- `ARCH-046-BACKGROUND-001`
- `ARCH-046-BACKGROUND-002`
- `ARCH-045-BACKGROUND-005`
- `ARCH-048-BACKGROUND-004`

## Enables

- `ARCH-048-BACKGROUND-005`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] A concrete, testable Woo `WooGuardedInitialSender` exists; the existing BG004 outreach service consumes it without a bare generic sender bypass.
- [x] Final permit correctly enforces all R2 cases, STOP lock ordering, exact recipient consent, observed terminal outcomes and verified Marketing template. Meta and Redis calls are **outside** the permit transaction.
- [x] No duplicate first send or credit on concurrent workers, retries or uncertain provider states; denial releases reversible reservations without permanently consuming sequence 1.
- [x] SHOPIFY/general in-window replies continue to use their existing guards; no Woo sequence-two follow-up is scheduled or authorised.
- [x] Shared structured logs are bounded, DB/Redis/provider faults propagate or reconcile and are never silently swallowed.
- [x] Default-off Woo send state is preserved until BG005 and terminal system-test acceptance; no assumption that an undelivered Woo event can be detected.

## Validation

- [x] Focused typecheck/unit + PostgreSQL permit/lock tests for current consent revisions, STOP/merchant suppression, installation/recipient change, template category and terminal recovery.
- [x] Two-client concurrent initial-attempt/send, STOP-versus-permit, paid/cancelled-order-versus-send, provider-confirmed/uncertain/failed-retry, billing source attribution and compensation tests.
- [x] Existing Shopify/outbound general guard and human/AI in-window STOP regressions; verify no new Woo follow-up path or Redis/HTTP under SQL lock.
- [x] Repository-declared relevant build/lint/test scripts, `git diff --check` and Completion Report with actual worktree/branch isolation evidence.

## Stop Condition

After the scope, criteria and validation are complete, set `status: review`, fill the Completion Report, return to `moda_architect` and **STOP**. Do not wire new workers, activate Woo sends or begin BG005. Required launcher-resolved worktree/synchronization evidence must be recorded.

## Implementation Notes

The earlier BG004 definition required a Woo follow-up engine that ARCH-048 deliberately does not provide. This revision removes that *implementation prerequisite* and narrows the task to the real initial-send safety gap. It does **not** assert that the guard is already implemented. Do not alter the completed ARCH-048-BG004 service merely to make an unguarded `sendTemplate()` typecheck. If a safe adapter cannot be built using current provider-admission capabilities, return a concrete missing primitive to the architect rather than silently weakening the final fence. Do not update domain `_index.md` files.

## Completion Report

### Status

Complete — Attempt 3 developer review passed and the developer explicitly completed the task after architect acceptance. Attempt 2 review history is preserved below.

### Files Changed

**Implementation repository:** `moda-interact-background`, branch `task/ARCH-046-BACKGROUND-004`, commit `0c92e12` (`feat(ARCH-046-BACKGROUND-004): enforce Woo final consent and STOP send fence`), pushed to `origin` on 25 October 2026. The commit contains **10 files, 1,131 insertions and 23 deletions**:

- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-provider-failure.service.ts`
- `src/services/woocommerce-recovery/woo-guarded-initial-sender.service.ts` (new)
- `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts` (new)
- `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`
- `tests/integration/woo-initial-send-fence.integration.test.ts` (new)
- `tests/unit/services/woocommerce-recovery/woo-guarded-initial-sender.service.test.ts` (new)
- `tests/unit/services/woocommerce-recovery/woo-initial-delivery.service.test.ts` (new)
- `tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts` (new)
- `tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts`

**Post-self-review correction commit:** `984d568` (`feat(background)`), pushed to `origin/task/ARCH-046-BACKGROUND-004` on 25 October 2026. The terminal capture shows **8 files changed, 455 insertions and 124 deletions**:

- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts` (updated)
- `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts` (updated)
- `tests/integration/fixtures/woo-initial-send-fence.fixture.ts` (new)
- `tests/integration/woo-initial-send-fence-races.integration.test.ts` (new)
- `tests/integration/woo-initial-send-fence.integration.test.ts` (updated)
- `tests/integration/woo-initial-send-redis-fault.integration.test.ts` (new)
- `tests/unit/services/outbound-whatsapp-admission/outbound-provider-failure.service.test.ts` (updated)
- `tests/unit/services/woocommerce-recovery/woo-initial-delivery.service.test.ts` (updated)

**Additional implementation validation/refactor commit:** `5e7a6d0` (`feat(arch-046-background)`), pushed to `origin/task/ARCH-046-BACKGROUND-004` in the terminal capture ending 26 October 2026. Git reports **9 files changed, 806 insertions and 774 deletions**:

- `tests/integration/recovery-human-dispatch.integration.test.ts` (reduced to 202 lines)
- `tests/integration/recovery-human-ai-ownership.integration.test.ts` (new)
- `tests/integration/recovery-human-provider-recovery.integration.test.ts` (new)
- `tests/integration/recovery-human-provider-status.integration.test.ts` (new)
- `tests/integration/recovery-human-follow-up-billing.integration.test.ts` (new)
- `tests/integration/recovery-human-follow-up-claims.integration.test.ts` (new)
- `tests/integration/recovery-human-follow-up-cancellation-races.integration.test.ts` (new)
- `tests/integration/woo-initial-send-fence-races.integration.test.ts` (corrected test transaction `$queryRaw` forwarding)
- `vitest.config.ts` (sequential execution of disposable integration test files sharing PostgreSQL/Redis; concurrency within individual race tests remains)

The seven HUMAN suites retain the original 27 test definitions/28 executable cases; the **refactored suites were run** with the Woo race suite in the 32/32 passing integration capture. The latest `git status` after the newest commit shows only the untracked `typescript` terminal recording. No production sending or consent source file was changed by `5e7a6d0` or `ac5d455`.

**PostgreSQL startup/test-infrastructure correction commit:** `ac5d455` (commit message recorded as `feat(arch-047-background-004)` although the branch/task is ARCH-046-BACKGROUND-004), pushed to `origin/task/ARCH-046-BACKGROUND-004` on 26 October 2026 (`5e7a6d0..ac5d455`). Git reports **3 files changed, 205 insertions, 7 deletions**:

- `scripts/integration-startup-retry.mjs` (new): bounded retry for Shared's specific PostgreSQL readiness timeout; nonzero Vitest runs and unrelated errors are not retried; both failures retained if the retry also fails.
- `scripts/integration-startup-retry.test.mjs` (new): seven exception-preservation, retry and non-retry unit tests.
- `scripts/test-integration.mjs`: integrates the bounded startup retry without changing production message delivery.

These commits record the implementation and validation corrections and remain preserved on the implementation task branch. The canonical developer claim, review handoff and explicit completion are recorded on the parent task branch; no implementation history was rewritten.

**Parent task branch:** Attempt 3 was claimed, reconciled to `review`, and explicitly completed after architect acceptance. The task record is published on `task/ARCH-046-BACKGROUND-004`. No parent architecture, domain `_index.md`, unrelated implementation code or submodule gitlink was changed.

### Work Completed

- Implemented `WooGuardedInitialSenderService` against the existing `WooGuardedInitialSender` contract and `WooInitialSendFenceService` for final Woo sequence-one provider admission; existing outreach continues to own reservations, billing, compensation and attempt finalisation.
- Reused the established outbound moderation, persisted `ConversationMessage` admission and provider delivery machinery. Final SQL permit locks Shop first, checks recovery/conversation/attempt identity, exact registered recipient, consent revision, active Woo installation, local STOP/suppression and durable terminal order evidence, and commits the provider dispatch key before the external provider call.
- Preserved duplicate-admission protection, existing confirmed-send reconciliation and fail-closed behaviour for uncertain provider outcomes. Denied pre-permit sends release reversible credit reservations without permanently consuming sequence one.
- Reused `@modainteract/moda-interact-shared/logging` for structured, bounded error diagnostics. Technical failures are logged and rethrown; a compensation failure retains the original error rather than being swallowed.
- Added focused sender, permit, provider-delivery and outreach unit tests and real PostgreSQL tests for concurrent permit contenders, STOP ordering, terminal order evidence, consent/recipient/install changes and provider dispatch persistence.
- Preserved default-off Woo outbound gating and absence of Woo follow-up scheduling or BG005 worker composition.
- After developer Changes Requested, added race cases using separate PostgreSQL clients for STOP-before-permit and already-observed completed/cancelled order before a waiting permit, with durable dispatch-key assertions; a database rollback/logging/retry case; and a real Redis read-failure scenario using the existing test-only outreach sender. The latter is **not** proof of production worker composition.
- Added provider failure/uncertain-outcome and ordinary HUMAN/AI existing-fence regression assertions in unit tests, and refined fixtures and exception-chain handling to satisfy lint. A prior focused run passed **102/102** (`typescript(20261025-200807)`); the production implementation was not altered by the subsequent test-only changes.
- Split the former 975-line HUMAN dispatch integration test into seven independently focused suites (each at most 202 lines in the supplied snapshot), retaining 28 executable cases; restricted disposable integration **file-level** parallelism to avoid cross-suite interference through global due-command claims, while preserving within-test concurrency. This refactor and the corrected Woo race test are in `5e7a6d0`; all eight selected integration suites **passed 32/32** in `typescript(20261026-030803)`.
- Added an infrastructure-only integration startup retry (`ac5d455`) that retries *only* Shared's PostgreSQL-readiness timeout once, logs safe diagnostic metadata through the canonical shared logger, and preserves original/secondary failures. Seven targeted retry tests passed; the integration and production failure boundaries remain fail-closed.

### Validation Results

Earlier evidence below spans 25–26 October 2026 and is retained as historical context. The Attempt 3 results are separate reruns against the synchronized implementation branch and are identified explicitly.

| Validation | Verified result / source |
|---|---|
| Attempt 3 focused Woo/outbound unit regressions | **PASS: 78/78 tests across 5 files** using `npx vitest run` on `woo-guarded-initial-sender`, `woo-initial-delivery`, `woo-initial-send-fence`, `woo-recovery-outreach`, and `outbound-provider-failure` tests. |
| Attempt 3 disposable PostgreSQL/Redis regressions | **PASS: 54/54 tests across 13 files** using `npm exec -- node scripts/test-integration.mjs` for Woo final permit/races/Redis faults; HUMAN/AI ownership, dispatch, billing, cancellation, claims and provider recovery/status; conversation services; and general/routing STOP fences. |
| Attempt 3 bounded PostgreSQL startup-retry tests | **PASS: 7/7** via `node --test scripts/integration-startup-retry.test.mjs`. |
| Attempt 3 repository lint | **PASS:** `npm run lint` (`eslint .`) completed without errors. |
| Attempt 3 TypeScript and production build | **PASS:** `npx tsc --noEmit` completed without diagnostics; `npm run build` completed with Prisma Client v6.19.3 generation and TypeScript compilation. |
| Attempt 3 Git validation | **PASS:** `git diff --check` reported no errors; implementation worktree remained clean and synchronized after validation. |
| Earlier focused Woo/outbound unit regressions | **PASS: 102/102 tests** in `typescript(20261025-200807)` (earlier 89/89 suite also passed in `typescript(20261025-170947)`). Includes initial delivery, final fence and outbound provider failure assertions. |
| Base Woo final-permit PostgreSQL integration | **PASS: 5/5** in `typescript(20261025-172449)`; current consent/recipient and installation changes, STOP, terminal state and idempotent provider permit. |
| Concurrent Woo STOP/order/transaction rollback races | **PASS: 4/4** in `typescript(20261026-014840)` and again within the later 32/32 group; separate SQL-client lock ordering and rollback/retry. |
| Seven refactored HUMAN/AI and provider/billing suites plus Woo race suite | **PASS: 8/8 suites, 32/32 tests** in `typescript(20261026-030803)`, including HUMAN dispatch, AI ownership/handover, provider recovery/status, follow-up billing, follow-up claims, cancellation races and Woo concurrency. No regression remains from the earlier parallel-suite interference. |
| Remaining Woo PostgreSQL, real Redis fault, general STOP and conversation regressions | **PASS: 5/5 suites, 22/22 tests** in `typescript(20261026-033946)`: recovery-conversation 11; Woo SQL fence 5; Woo Redis failure 1; general outbound STOP 3; routing-guidance STOP 2. Intentional Redis fault emitted a structured error and propagated without provider send or committed recovery charge. |
| Bounded PostgreSQL startup-retry tests | **PASS: 7/7** via `node --test scripts/integration-startup-retry.test.mjs` in `typescript(20261026-033946)`. Failure-retry rules exclude test assertion failure, Redis faults and unrelated migration errors. |
| Repository lint | **PASS:** `npm run lint` (`eslint .`) completed without errors in `typescript(20261026-033946)`. |
| Repository TypeScript | **PASS:** `npx tsc --noEmit` completed without diagnostics in `typescript(20261026-033946)`. |
| Production build | **PASS:** `npm run build` (`npm run prisma:generate && tsc`) completed without diagnostics; Prisma Client v6.19.3 generation succeeded in `typescript(20261026-033946)`. |
| Implementation task branch | **PASS:** current tip `e88d9345015202e915a9198d4c6803f41e9adfdb` equals `origin/task/ARCH-046-BACKGROUND-004`; it includes the preserved implementation head `ac5d455` and the launcher synchronization merge. |
| Canonical developer Attempt 3 launch, synchronization and claim | **PASS:** parent claim commit `0e41dc305038de33e6685354e782f032d13534e1`; launcher verified four dependencies complete and prepared the implementation worktree. Review and completion preserve Attempt 3 and clear claim fields. |

The prior test-fixture violations (digits-only attempt recipient and funded `UsageReservation`) were corrected without loosening database constraints. The earlier PostgreSQL Docker readiness timeout was addressed with a narrowly bounded startup retry. Attempt 3 validation was rerun after the launcher synchronization and all selected checks passed. No task-level validation blocker remains; separately gated BG005/system-test work remains outstanding.

### Execution / Worktree Evidence

- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-046-BACKGROUND-004`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-BACKGROUND-004`.
- The canonical launcher claimed Attempt 3 in parent commit `0e41dc305038de33e6685354e782f032d13534e1`. It verified all four declared dependencies complete and synchronized the implementation worktree with current Background `origin/main`; synchronization merge `e88d9345015202e915a9198d4c6803f41e9adfdb` was pushed to `origin/task/ARCH-046-BACKGROUND-004`.
- Physical isolation was verified: parent worktree root uses common Git directory `/Users/kwadwoadomafriyie/project/moda-interact-workspace/.git`; implementation worktree root uses `/Users/kwadwoadomafriyie/project/moda-interact-workspace/.git/modules/moda-interact-background`. Both local task branches matched their respective `origin/task/ARCH-046-BACKGROUND-004` refs before the report edit.
- `git submodule status --recursive` in the implementation worktree reports initialized `database` at gitlink `3f1f50b91c9e93ff9647a3d1d7f6fd46b9b888b9`. Both worktrees were clean before this task-record edit; implementation validation left the implementation worktree clean.
- The parent task record was modified only after these checks. No implementation source changes were made during Attempt 3; the feature implementation and prior corrections remain in the published history through `ac5d455`, with `e88d934` as the current synchronized tip.

### Deviations

- No new database migration, cross-service contract, Woo follow-up engine, BG005 worker wiring, Woo activation or production sending logic was introduced after the earlier final-permit implementation.
- The test-only changes in `5e7a6d0` split the HUMAN integration suite and serialize disposable integration files; `ac5d455` changes only the integration test infrastructure with a bounded PostgreSQL readiness retry. Both are covered by the passing tests above.
- The newest commit subject inadvertently says `arch-047`; the actual repository/branch and implemented task remain **ARCH-046-BACKGROUND-004**. Preserve the published commit ID; no amend/force-push is necessary.
- No Attempt 3 implementation changes were needed; this review reran the required validation on the synchronized implementation tree and reconciled the parent task record through the canonical claim branch.

### Assumptions

- `ARCH-048-BACKGROUND-004` continues to own the checkout lease, earlier observed-order preflight, first-send credit reservation and compensation. BG005 will compose the guarded sender when separately authorised.
- Existing durable Woo order observations only reflect events received by Moda. A missing Woo event cannot be inferred by this sender, nor can a Redis-only observation be claimed to be SQL-locked.
- Woo outbound remains default-off until the separate composition, developer activation and integrated system-test gates are satisfied.

### Unresolved Issues

- **No current functional/test failure is evidenced.** The previously failing HUMAN races and Docker startup were addressed; the latest supplied logs show the selected unit, PostgreSQL/Redis, HUMAN/AI/general STOP regression, lint, typecheck and build checks passing.
- No unresolved developer validation blocker remains. Completion does not wire BG005, activate Woo outreach or authorize Woo sequence-two follow-ups.
- As before, this task does not integrate BG005 worker composition, activate Woo outreach or cover end-to-end production sending. Such work remains separately gated.

### Architectural Concerns

- STOP committed before the Shop-locked provider permit blocks admission; STOP committed after the permit cannot retroactively retract a provider request. Tests exercise both orderings.
- The permit uses durable PostgreSQL state for atomic decisions; the previously accepted Redis checkout/order observation remains an earlier guarded boundary, not a phantom SQL lock. Undelivered Woo events remain an explicit architectural limitation.
- Provider-uncertain admissions must be reconciled, not blindly retried with a new first send or automatically compensated as though no dispatch occurred.

## Architect Review

### Review Status

Accepted — “Architect Review Accepted” was explicitly supplied with the developer completion request on 26 October 2026.

### Review Notes

Accepted the implementation for the defined initial-send and sequence-one retry consent/STOP fence. The Attempt 3 review and Completion Report were accepted; this does not approve BG005 composition, enable Woo sending, or waive the separate system-test gate.

### Reviewed Files

Woo guarded sender and final permit services, outbound provider-admission/delivery services, Woo recovery outreach integration, task-owned unit and PostgreSQL/Redis regressions, and Attempt 3 validation results.

### Validation Reviewed

Attempt 3: 78 focused unit tests, 54 tests across 13 disposable PostgreSQL/Redis integration suites, 7 startup-retry tests, lint, TypeScript, production build and `git diff --check` passed after synchronization. The full repository test suite was not run.

### Architecture Conformance

Consistent with ARCH-048's initial-outreach-only boundary and default-off rollout.

### Follow-up

BG005 may become dependency-ready after this acceptance and satisfaction of its other dependencies. Woo follow-ups and live sending remain separately gated.

## Developer Self-Review - Changes Requested

### Review Decision

Attempt 1 is not accepted for developer completion. The implementation branch is committed and pushed, but the current Completion Report marks required Work Items, Acceptance Criteria and Validation incomplete and explicitly records evidence gaps.

### Required Corrections

- Complete and report the task-owned concurrency and fault cases: two-client initial-send admission, STOP-versus-permit ordering, observed paid/cancelled order versus send, provider-confirmed/uncertain/failed retry behavior, billing source attribution and compensation. Include read-after-commit validation for existing admissions.
- Complete and report the Shopify/general outbound and human/AI in-window STOP regressions. Add evidence that no Woo follow-up path was introduced and no Redis or HTTP operation occurs while SQL locks are held.
- Run the repository-declared relevant lint/build checks and any remaining focused/full checks required by the task; record exact commands and results. Do not report the broad checks as passing without evidence.
- Record canonical launcher preparation/synchronization evidence for the parent and implementation worktrees, including physical isolation and recursive submodule state, or attach the existing durable preparation packet that proves it.
- Update the Completion Report and task checkboxes only to reflect verified work. Keep Woo outbound default-off; do not wire BG005 or broaden task scope.

### State Transition

Returned to `ready`, with `executor: null`, `claimed_at: null`, and Attempt 1 unchanged. No new attempt is claimed by this review; the next `/moda_developer_create` invocation may claim Attempt 2.

## Developer Self-Review - Changes Requested (Attempt 2)

### Review Decision

Attempt 2 is not accepted for developer completion. The implementation worktree is clean at `984d568`, with no new task implementation commit after the Attempt 2 claim. The parent task branch contains the published claim; required validation gaps from Attempt 1 remain open, and no evidence of those tests running during Attempt 2 was found.

### Required Corrections

- Run the focused unit regressions changed by `984d568`, including the Woo initial-delivery and outbound provider-failure tests; record exact commands and results.
- Run `tests/integration/woo-initial-send-fence-races.integration.test.ts` and `tests/integration/woo-initial-send-redis-fault.integration.test.ts` against the required PostgreSQL/Redis test services. Include the STOP/order race, transaction rollback/retry, Redis failure, and no-duplicate-admission outcomes.
- Run existing general/Shopify outbound guard and HUMAN/AI in-window STOP regressions; report concrete results for provider reconciliation, billing attribution and compensation.
- Run relevant repository lint and build/typecheck commands after any corrections, plus `git diff --check`; preserve default-off Woo rollout and do not add BG005 wiring or follow-up scheduling.
- Update Work Items, Acceptance Criteria, Validation and Completion Report only to match verified results. Keep the task at Attempt 2 during corrections; a later `/moda_developer_update` can reconcile the completed cycle.

### State Transition

Returned to `ready`, with `executor: null`, `claimed_at: null`, and Attempt 2 unchanged. The next `/moda_developer_create` invocation may claim Attempt 3 after synchronizing the canonical worktrees and verifying dependencies.

## Developer Self-Review - Attempt 3

### Review Decision

Passed for developer review handoff. The canonical Attempt 3 claim, implementation synchronization, dependency state, worktree isolation and recursive submodule state were verified. Focused unit and disposable PostgreSQL/Redis integration regressions passed after synchronization, as did startup-retry tests, lint, TypeScript, production build and `git diff --check`. No new implementation change was required.

### State Transition

Set to `review`; `executor` and `claimed_at` are cleared, and Attempt 3 is preserved. No completion action was requested or applied. Architect review remains pending.

## Developer Completion Decision - Attempt 3

The developer explicitly invoked completion on 26 October 2026 after the accepted Architect Review. All required Work Items, Acceptance Criteria and Validation items are complete. The implementation task branch is committed, pushed and clean at `e88d9345015202e915a9198d4c6803f41e9adfdb`; the parent report is committed and pushed on `task/ARCH-046-BACKGROUND-004`. The task is `complete`; `executor` and `claimed_at` are null; Attempt 3 is unchanged. No task branch was merged to `main`.

### Dependency Frontier Update

- `ARCH-048-BACKGROUND-005` has all six declared dependencies Complete. Its canonical parent task record is Ready at Attempt 0, published as `d9affe0a`; no implementation attempt was claimed.
- `ARCH-046-SYSTEM-TEST-002` remains `blocked` because its other implementation prerequisites and manual LocalWP gate remain outstanding. It was not modified or claimed.
- `ARCH-048-SYSTEM-TEST-001` and other downstream tasks were not promoted without verifying all of their explicit dependencies and manual gates.
